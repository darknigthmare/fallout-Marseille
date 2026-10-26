const test=require('node:test'),assert=require('node:assert/strict');
const M=require('../../src/v046/00_integrity.js');
const proof={resource:'ign-bdtopo',source:'IGN BD TOPO',license:'Licence Ouverte 2.0',attribution:'IGN — Géoplateforme',acquiredAt:'2026-10-23',verticalDatum:'NGF-IGN69'};
const ign=nature=>({nature,largeur_de_chaussee:null,nombre_de_voies:null,position_par_rapport_au_sol:'0',provenance:proof});
test('IGN Sentier and Escalier are narrow estimated paths with their source classification retained',()=>{
 for(const nature of ['Sentier','Escalier']){const p=M.roadProfile(ign(nature));assert.equal(p.width,1.6);assert.equal(p.widthAssumed,true);assert.match(p.widthBasis,/nature IGN.*estimation/);assert.equal(p.sourceNature,nature);assert.equal(p.maritime,false);}
});
test('IGN measured width and supplied lanes retain precedence over nature-derived estimates',()=>{
 const p=M.roadProfile({...ign('Sentier'),largeur_de_chaussee:7.25});assert.equal(p.width,7.25);assert.equal(p.widthAssumed,false);assert.equal(p.widthBasis,'largeur_de_chaussee');
 const lanes=M.roadProfile({...ign('Chemin'),nombre_de_voies:2});assert.equal(lanes.width,6.2);assert.match(lanes.widthBasis,/voies.*estimation/);
});
test('The other observed IGN natures use explicit, conservative classes without changing known widths',()=>{
 for(const nature of ['Chemin','Route empierrée']){const p=M.roadProfile(ign(nature));assert.equal(p.roadClass,'track');assert.equal(p.width,3);assert.equal(p.widthAssumed,true);}
 for(const nature of ['Route à 1 chaussée','Route à 2 chaussées','Rond-point','Bretelle'])assert.equal(M.roadProfile(ign(nature)).roadClass,'road');
 const motorway=M.roadProfile({...ign('Type autoroutier'),largeur_de_chaussee:9});assert.equal(motorway.roadClass,'motorway');assert.equal(motorway.width,9);assert.equal(motorway.widthAssumed,false);
});
test('Explicit existing classifications and non-IGN nature fields preserve their prior interpretation',()=>{
 assert.equal(M.roadProfile({...ign('Route à 1 chaussée'),class:'footway'}).width,1.6);
 assert.equal(M.roadProfile({class:'track'}).width,1.6);
 assert.equal(M.roadProfile({nature:'Sentier'}).width,5.5);
 assert.equal(M.roadProfile({...ign('Nature inconnue')}).width,5.5);
});
test('A documented ferry itinerary creates no asphalt deck, while its source XYZ and attributes remain unchanged',()=>{
 const props=ign('Bac ou liaison maritime'),path=[[0,0,0],[100,0,0]],before=JSON.stringify({props,path}),mesh=M.roadMesh(path,props,()=>0);
 assert.equal(mesh.maritime,true);assert.deepEqual(mesh.faces,[]);assert.deepEqual(mesh.vertices,[]);assert.match(mesh.surfaceOmitted,/maritime/);assert.equal(JSON.stringify({props,path}),before);
});
function upRay(vertices,faces,p){let nearest=Infinity;
 for(const f of faces){const[a,b,c]=f.map(i=>vertices[i]),den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);if(Math.abs(den)<1e-12)continue;const u=((b[2]-c[2])*(p[0]-c[0])+(c[0]-b[0])*(p[2]-c[2]))/den,v=((c[2]-a[2])*(p[0]-c[0])+(a[0]-c[0])*(p[2]-c[2]))/den,w=1-u-v;if(u<0||v<0||w<0)continue;const h=u*a[1]+v*b[1]+w*c[1];if(h>=p[1])nearest=Math.min(nearest,h-p[1]);}return nearest;
}
test('The real Vieux-Port sentier no longer forms a phantom ceiling over the measured clear street camera',()=>{
 // Actual acquired TRONROUT0000000040960607, in the engine's unchanged
 // Lambert-93 frame. The ground callback is the actual diagnostic sample.
 const path=[[-11436.344327306258,-957.9047132395208,3.1],[-11418.744158137357,-963.3053934387863,3],[-11412.844418070046,-962.9053058279678,3.7],[-11394.944465419976,-922.9048272529617,3.4]],props={...ign('Sentier'),cleabs:'TRONROUT0000000040960607',sourceId:'troncon_de_route.6003809',precision_altimetrique:1.5,precision_planimetrique:2.5},p=[-11398.888126658509,3.0129979244143144,-926.6633799411356],before=JSON.stringify({path,props}),old=M.roadMesh(path,{...props,nature:undefined},()=>1.3629979244143142),fixed=M.roadMesh(path,props,()=>1.3629979244143142);
 assert.equal(old.width,5.5);assert.ok(Math.abs(upRay(old.vertices,old.faces,p)-.5065151815586476)<1e-8);
 assert.equal(fixed.width,1.6);assert.equal(upRay(fixed.vertices,fixed.faces,p),Infinity);assert.equal(fixed.heightBasis,'coordonnées Z source');assert.equal(fixed.elevationAssumed,false);
 assert.deepEqual(fixed.vertices.map(v=>v[1]),old.vertices.map(v=>v[1]));assert.equal(JSON.stringify({path,props}),before);
});
