const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../..'),M=require(path.join(root,'src/v046/00_integrity.js')),fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/vieux_port_road_ground.json')));
function harness(sample,realCoordinates=false){
 const context=vm.createContext({MistralIntegrity:M,COLORS:{water:[.1,.3,.4]},V046:{terrain:null},v017PolyBounds:rings=>{const points=rings.flat(),xs=points.map(p=>p[0]),zs=points.map(p=>p[1]);return{cx:(Math.min(...xs)+Math.max(...xs))/2,cz:(Math.min(...zs)+Math.max(...zs))/2};},v015GeoUnproject:(_id,x,z)=>[z,x],rad:a=>a*Math.PI/180});
 if(realCoordinates){const patch=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8');vm.runInContext(patch.slice(patch.indexOf('function v018Lambert93'),patch.indexOf('const V018_OLD_SCALES')),context);vm.runInContext("const origin=v018Lambert93(43.285,5.51);v015GeoUnproject=(_id,x,z)=>v018InverseLambert(x+origin[0],origin[1]-z);globalThis.project=(lat,lon)=>{const q=v018Lambert93(lat,lon);return[q[0]-origin[0],origin[1]-q[1]];};",context);}
 const source=fs.readFileSync(path.join(root,'src/v046/01_world.js'),'utf8');vm.runInContext(source.slice(source.indexOf('function v046SourceRoad('),source.indexOf('function v046SourceBuilding(')),context);
 const bank={read:(lat,lon)=>({height:sample(lat,lon),sources:['fixture-mnt'],sourceResource:'ign_rge_alti_wld',verticalDatum:'NGF-IGN69',resolutionMeters:[10,10],interpolation:'bilinéaire, quatre échantillons valides requis'})},world={id:'geo_marseille_commune',staticDraws:[],v047TerrainBank:bank};
 return{context,world,build:(path,props,layer='transportation')=>context.v046SourceRoad(world,path,props,[.5,.4,.3],'fixture-tile',layer)};
}
const props=()=>({nature:'Sentier',position_par_rapport_au_sol:'0',largeur_de_chaussee:1.6,provenance:{resource:'ign-bdtopo'}}),sourcePath=[[0,0,8],[0,40,9]];
test('The real Vieux-Port road follows the real MNT subset while its source XYZ, width and receipts stay unchanged',()=>{
 const bank=new M.TerrainBank({});bank.add(fixture.terrain,fixture.terrain.macro);const h=harness((lat,lon)=>bank.read(lat,lon).height,true),raw=fixture.feature.geometry.coordinates,p=fixture.feature.properties,original=JSON.stringify({raw,p}),path=raw.map(c=>[...h.context.project(c[1],c[0]),c[2]]),draw=h.build(path,p);
 assert.ok(draw);assert.equal(draw.sourceProfile.surfaceDerived,true);assert.equal(draw.sourceProfile.sourceHeightBasis,'coordonnées Z source');assert.equal(draw.sourceProfile.sourceXYZPreserved,true);assert.match(draw.sourceProfile.heightBasis,/MNT.*dérivée/);assert.equal(draw.roadWidth,1.6);assert.equal(draw.widthAssumed,true);
 for(const vertex of draw.vertices){const ll=h.context.v015GeoUnproject(h.world.id,vertex[0],vertex[2]),height=bank.read(...ll).height;assert.ok(Number.isFinite(height));assert.ok(Math.abs(vertex[1]-height-.085)<1e-9);}
 assert.deepEqual(JSON.parse(JSON.stringify(draw.roadPath)),path);assert.equal(JSON.stringify({raw,p}),original);assert.equal(draw.sourceProfile.surfaceTerrainSources[0].verticalDatum,'NGF-IGN69');
 const eye=3.0129979244143144;assert.ok(draw.vertices.slice(-2).every(v=>v[1]<eye),'The original near-camera source endpoint was 3.4 m; its derived ground ribbon now stays below the standing camera.');
});
test('Ground contact never replaces absent MNT with a false zero-altitude face',()=>{
 const none=harness(()=>null),original=JSON.stringify(sourcePath);assert.equal(none.build(sourcePath,props()),null);assert.equal(none.world.staticDraws.length,0);assert.equal(JSON.stringify(sourcePath),original);
 const partial=harness((z)=>z<20?null:100+z*.01),draw=partial.build(sourcePath,props());assert.ok(draw);assert.ok(draw.sourceProfile.surfaceNoDataVertices>0);for(const face of draw.faces)assert.ok(face.every(i=>draw.vertices[i][1]>100));
});
test('Bridges, tunnels, absolute elevations and explicit clearances retain their exact source heights',()=>{
 for(const patch of [{position_par_rapport_au_sol:'1'},{position_par_rapport_au_sol:'-1'},{bridge:'yes'},{tunnel:'yes'},{ele:80},{deck_height:80},{'bridge:ele':80},{'bridge:height':0},{min_height:2}]){
  const p={...props(),...patch},h=harness(()=>1),draw=h.build(sourcePath,p);assert.ok(draw);assert.notEqual(draw.sourceProfile.surfaceDerived,true);assert.equal(draw.sourceProfile.heightBasis,'coordonnées Z source');assert.equal(draw.sourceProfile.elevationAssumed,false);assert.equal(draw.vertices[0][1],8.085);assert.equal(draw.vertices.at(-1)[1],9.085);assert.deepEqual(JSON.parse(JSON.stringify(draw.roadPath)),sourcePath);
 }
});
test('Unspecified ordinal levels, non-IGN surveys and waterways preserve their previous XYZ policy',()=>{
 for(const [p,layer,lift] of [[{...props(),position_par_rapport_au_sol:undefined},'transportation',.085],[{...props(),provenance:{resource:'local-survey'}},'transportation',.085],[props(),'waterway',.025]]){const draw=harness(()=>1).build(sourcePath,p,layer);assert.notEqual(draw.sourceProfile.surfaceDerived,true);assert.equal(draw.vertices[0][1],8+lift);assert.equal(draw.sourceProfile.heightBasis,'coordonnées Z source');}
});
test('A supplied carriageway width keeps measurement precedence in the derived ground representation',()=>{
 const p={...props(),largeur_de_chaussee:7.25},draw=harness(()=>2).build(sourcePath,p);assert.equal(draw.roadWidth,7.25);assert.equal(draw.widthAssumed,false);assert.equal(draw.sourceProfile.widthBasis,'largeur_de_chaussee');assert.equal(draw.sourceProfile.surfaceDerived,true);
});
test('The pure source-geometry mesh API still honors XYZ at grade unless the runtime explicitly derives ground contact',()=>{
 const mesh=M.roadMesh(sourcePath,props(),()=>1);assert.equal(mesh.vertices[0][1],8.085);assert.equal(mesh.heightBasis,'coordonnées Z source');assert.equal(mesh.elevationAssumed,false);assert.notEqual(mesh.surfaceDerived,true);
});
