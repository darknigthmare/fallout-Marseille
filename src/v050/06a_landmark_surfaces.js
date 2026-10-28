/* Native IGN MNS surfaces refine two landmark silhouettes. A MNS is the upper
   observed surface, not a facade survey or a semantic/structural roof model.
   Source building identities, XY contours and interior envelopes stay intact. */
const MistralLandmarkSurfaces=(()=>{
 const MAX_BYTES=16*1024*1024,MAX_RECORDS=24,MAX_FACES=60000,MAX_VERTICES=40000,EPS=1e-7;
 const finite=n=>typeof n==='number'&&Number.isFinite(n),copy=v=>JSON.parse(JSON.stringify(v));
 function fail(s){throw Error('Surfaces MNS : '+s);}
 function key(g){if(!g||!['Polygon','MultiPolygon'].includes(g.type)||!Array.isArray(g.coordinates))fail('empreinte absente');return JSON.stringify([g.type,g.coordinates]);}
 function validate(raw){
  if(!raw||raw.schemaVersion!==1||raw.kind!=='ign-native-mns-landmark-surfaces'||raw.frame!=='EPSG:2154-NGF-IGN69'||!Array.isArray(raw.records)||raw.records.length>MAX_RECORDS)fail('atlas incompatible');
  const s=raw.source;if(s?.provider!=='IGN'||s.product!=='MNS LiDAR HD'||s.nativeSpacingMeters!==.5||s.license!=='Licence Ouverte 2.0'||typeof s.attribution!=='string'||!s.attribution||!Array.isArray(s.tiles)||!s.tiles.length||s.tiles.length>4)fail('provenance incompatible');
  const tiles=new Set();for(const t of s.tiles){let u;try{u=new URL(t.feature?.properties?.url_mns);}catch{fail('URL officielle absente');}if(u.protocol!=='https:'||u.hostname!=='data.geopf.fr'||u.username||u.password||u.pathname!=='/wms-r'||!u.searchParams.get('LAYERS')?.startsWith('IGNF_LIDAR-HD_MNS_')||!/^[a-f0-9]{64}$/.test(t.sha256)||tiles.has(t.sha256)||t.header?.resolutionMeters?.some(n=>n!==.5)||t.header?.nodata!==-9999||t.feature.properties.systeme_altimetrique!=='IGN69'||t.feature.properties.systeme_planimetrique!=='LAMB93')fail('dalle non attribuée');tiles.add(t.sha256);}
  const records=[],seen=new Set();let count=0;
  for(const r of raw.records){
   if(typeof r.cleabs!=='string'||!r.cleabs||r.cleabs.length>128||seen.has(r.cleabs)||!Array.isArray(r.vertices)||r.vertices.length<3||r.vertices.length>MAX_VERTICES||!Array.isArray(r.faces)||!r.faces.length||r.faces.length>MAX_FACES||!Array.isArray(r.boundary)||!r.boundary.length||!r.sourceProperties||!Array.isArray(r.sourceTileSha256)||!r.sourceTileSha256.length||r.sourceTileSha256.some(h=>!tiles.has(h)))fail('volume hors contrat');
   seen.add(r.cleabs);count+=r.faces.length;if(count>220000)fail('budget global dépassé');
   for(const p of r.vertices)if(!Array.isArray(p)||p.length!==3||!p.every(finite)||p[0]<0||p[0]>1300000||p[1]<6000000||p[1]>7200000||p[2]<-100||p[2]>1000)fail('sommet invalide');
   for(const f of r.faces){if(!Array.isArray(f)||f.length!==3||new Set(f).size!==3||f.some(i=>!Number.isInteger(i)||i<0||i>=r.vertices.length))fail('triangle invalide');for(let i=0;i<3;i++){const a=r.vertices[f[i]],b=r.vertices[f[(i+1)%3]];if(Math.hypot(a[0]-b[0],a[1]-b[1])>Math.SQRT1_2+EPS)fail('triangle hors cellule native');}}
   for(const edge of r.boundary)if(!Array.isArray(edge)||edge.length!==2||edge[0]===edge[1]||edge.some(i=>!Number.isInteger(i)||i<0||i>=r.vertices.length))fail('bord invalide');
   const m=r.measurements;if(!m||![m.minimumElevation,m.maximumElevation,m.footprintAreaSquareMetres,m.roofProjectedAreaSquareMetres,m.boundaryLengthMetres,m.sourceBoundaryLengthMetres].every(finite)||m.minimumElevation>m.maximumElevation||Math.abs(m.footprintAreaSquareMetres-m.roofProjectedAreaSquareMetres)>Math.max(.0001,m.footprintAreaSquareMetres*1e-7)||Math.abs(m.boundaryLengthMetres-m.sourceBoundaryLengthMetres)>.002)fail('couverture métrique incomplète');
   if(Math.abs(Math.min(...r.vertices.map(p=>p[2]))-m.minimumElevation)>EPS||Math.abs(Math.max(...r.vertices.map(p=>p[2]))-m.maximumElevation)>EPS)fail('bornes verticales incohérentes');
   records.push({...copy(r),geometryKey:key(r.rawGeometry)});
  }
  return{source:copy(s),records};
 }
 function matches(record,draw){return draw?.mesh==='prism'&&draw.geoLayer==='building'&&draw.geoProperties?.cleabs===record.cleabs&&draw.sourceGeometry&&key(draw.sourceGeometry)===record.geometryKey&&Object.entries(record.sourceProperties).every(([k,v])=>(draw.geoProperties[k]??null)===v);}
 function projected(r,origin){return r.vertices.map(p=>[p[0]-origin[0],p[2],origin[1]-p[1]]);}
 function build(record,draw,origin){
  if(!matches(record,draw)||!Array.isArray(origin)||origin.length!==2||!origin.every(finite)||!finite(draw.baseY)||record.measurements.minimumElevation<draw.baseY-.01)fail('liaison ou base incompatible');
  const vertices=projected(record,origin),faces=record.faces.map(f=>{const a=vertices[f[0]],b=vertices[f[1]],c=vertices[f[2]];return(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])>=0?f.slice():[f[0],f[2],f[1]];}),wallVertices=[],wallFaces=[];
  for(const[ai,bi]of record.boundary){const a=vertices[ai],b=vertices[bi],i=wallVertices.length;wallVertices.push([a[0],draw.baseY,a[2]],[b[0],draw.baseY,b[2]],b.slice(),a.slice());wallFaces.push([i,i+1,i+2],[i,i+2,i+3]);}
  return{roof:{mesh:'geoSurface',vertices,faces},walls:{mesh:'geoSurface',vertices:wallVertices,faces:wallFaces},minimumElevation:record.measurements.minimumElevation,maximumElevation:record.measurements.maximumElevation};
 }
 // A small metric index prevents every facade vertex/support probe from
 // scanning the thousands of measured triangles of the entire monument.
 class SurfaceIndex{
  constructor(vertices,faces,size=2){if(!finite(size)||size<.5||size>64)fail('index métrique hors budget');this.vertices=vertices;this.faces=faces;this.size=size;this.cells=new Map();for(let i=0;i<faces.length;i++){const ps=faces[i].map(n=>vertices[n]),a=Math.floor(Math.min(...ps.map(p=>p[0]))/size),b=Math.floor(Math.max(...ps.map(p=>p[0]))/size),c=Math.floor(Math.min(...ps.map(p=>p[2]))/size),d=Math.floor(Math.max(...ps.map(p=>p[2]))/size);if(![a,b,c,d].every(Number.isSafeInteger)||(b-a+1)*(d-c+1)>64)fail('triangle hors index borné');for(let x=a;x<=b;x++)for(let z=c;z<=d;z++){const k=x+':'+z;if(!this.cells.has(k))this.cells.set(k,[]);this.cells.get(k).push(i);}}}
  candidates(x,z,r=0){if(![x,z,r].every(finite)||Math.abs(x)>2e7||Math.abs(z)>2e7||r<0||r>8)return[];const ids=new Set();for(let a=Math.floor((x-r)/this.size);a<=Math.floor((x+r)/this.size);a++)for(let b=Math.floor((z-r)/this.size);b<=Math.floor((z+r)/this.size);b++)for(const i of this.cells.get(a+':'+b)||[])ids.add(i);return[...ids];}
  heightAt(x,z,padding=0){let height=null,best=Infinity;for(const i of this.candidates(x,z,padding)){const ps=this.faces[i].map(n=>this.vertices[n]),t=MistralRoofSolids.projected(ps);if(!t)continue;const y=MistralRoofSolids.plane(t,x,z);if(y!==null){if(best>EPS){height=y;best=0;}else height=Math.max(height,y);continue;}if(!padding||best===0)continue;for(let j=0;j<3;j++){const a=ps[j],b=ps[(j+1)%3],dx=b[0]-a[0],dz=b[2]-a[2],den=dx*dx+dz*dz;if(den<EPS)continue;const u=Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[2])*dz)/den)),d=Math.hypot(x-a[0]-u*dx,z-a[2]-u*dz);if(d<=padding+EPS&&d<best){best=d;height=a[1]+u*(b[1]-a[1]);}}}return height;}
 }
 return{MAX_BYTES,MAX_RECORDS,MAX_FACES,MAX_VERTICES,EPS,key,validate,matches,projected,build,SurfaceIndex};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralLandmarkSurfaces;

function v056LandmarksAfterInit(){
 if(typeof window==='undefined'||window.__mistralLandmarkSurfaces)return;window.__mistralLandmarkSurfaces=true;
 const runtime={promise:null,loaded:false,missing:false,error:null,records:new Map(),source:null,applied:new Map(),rejected:new Map(),serial:0,byCap:new WeakMap(),facadeCache:new WeakMap(),facadeTrianglesOmitted:0};
 function info(){return{loaded:runtime.loaded,missing:runtime.missing,error:runtime.error,records:runtime.records.size,applied:[...runtime.applied].map(([id,a])=>({cleabs:id,siteContext:a.record.siteContext,vertices:a.roof.vertices.length,roofTriangles:a.roof.faces.length,wallTriangles:a.walls.faces.length,minimumElevation:a.minimumElevation,maximumElevation:a.maximumElevation})),rejected:[...runtime.rejected].map(([cleabs,reason])=>({cleabs,reason})),nativeSpacingMeters:.5,facadeTrianglesOmitted:runtime.facadeTrianglesOmitted,scope:'Surface supérieure observée MNS, découpée dans les emprises IGN inchangées ; aucun relevé de façade ou de pièce.'};}
 function apply(w,draws,colliders){let applied=0;for(const d of draws.slice()){const r=runtime.records.get(d.geoProperties?.cleabs);if(!r||d.v056MeasuredSurface)continue;try{
   if(!MistralLandmarkSurfaces.matches(r,d))throw Error('source-geometry-or-properties-changed');
   if(draws.some(cap=>cap!==d&&cap.geoLayer==='roof'&&cap.geoFeatureId===d.geoFeatureId))throw Error('explicit-roof-already-present');
   const collider=colliders.find(c=>c.id===d.id);if(!collider||collider.disabled)throw Error('source-collider-unavailable');
   const origin=typeof V046_ORIGIN!=='undefined'?V046_ORIGIN:null;if(!origin)throw Error('metric-origin-unavailable');
   const surface=MistralLandmarkSurfaces.build(r,d,origin),index=new MistralLandmarkSurfaces.SurfaceIndex(surface.roof.vertices,surface.roof.faces);
   const cap={...surface.roof,pos:d.pos.slice(),scale:[1,1,1],color:[.63,.61,.55],alpha:1,revision:1,geoLayer:'roof',geoFeatureId:d.geoFeatureId,v046Tile:d.v046Tile||d.geoTile,geoTile:d.geoTile,id:d.id+':mns',v046GeometryId:d.v046GeometryId+':mns-v1',v056MeasuredRoof:true,roofBasis:'MNS LiDAR HD, centres natifs et intersections interpolées',sourceProvenance:{source:'IGN — MNS LiDAR HD',license:runtime.source.license,attribution:runtime.source.attribution,acquiredAt:runtime.source.tiles.map(t=>t.feature.properties.date_fin_acquisition).join(', '),verticalDatum:'NGF-IGN69'}};
   // Construct the same narrow-phase class used by declared roof geometry.
   // The original broad XY and source descriptor remain intact.
   const bounds={...collider,maxY:surface.maximumElevation},solid=new MistralRoofSolids.Solid({...d,height:surface.maximumElevation-d.baseY},cap,bounds,()=>v018MeshData(surface.walls),MistralIntegrity.inside);
   solid.heightAt=(x,z)=>index.heightAt(x,z);
   for(const t of v018Triangulate(d.rings))solid.faces.push(t.map(p=>[p[0],d.baseY,p[1]]));
   const tops=index.faces.map(f=>MistralRoofSolids.projected(f.map(i=>index.vertices[i])));solid.maxDisk=function(x,z,r=0,walkableOnly=false){if(![x,z,r].every(Number.isFinite)||r<0||x+r<this.bounds.minX||x-r>this.bounds.maxX||z+r<this.bounds.minZ||z-r>this.bounds.maxZ)return null;let result=null;for(const i of index.candidates(x,z,r)){const t=tops[i];if(!t||walkableOnly&&!t.walkable)continue;const y=MistralRoofSolids.diskHeight(t,x,z,r);if(y!==null&&(result===null||y>result))result=y;}return result;};
   Object.assign(collider,{maxY:surface.maximumElevation,v050RoofSolid:solid});d.v056MeasuredSurface={...surface,index,record:r,roof:cap};d.revision=(d.revision||0)+1;draws.push(cap);runtime.byCap.set(cap,d.v056MeasuredSurface);runtime.applied.set(r.cleabs,d.v056MeasuredSurface);runtime.rejected.delete(r.cleabs);applied++;
  }catch(error){runtime.rejected.set(r.cleabs,String(error.message||error));}}if(applied&&typeof V050_ROOFS!=='undefined')V050_ROOFS.cache.delete(w);return applied;}
 async function ready(){if(!runtime.promise)runtime.promise=(async()=>{try{const descriptor=await v050LocalSourceJSON('data/map_pack/landmark_surfaces/index.json',null,true);if(!descriptor){runtime.missing=true;runtime.loaded=true;return info();}const d=descriptor.surface;if(descriptor.schemaVersion!==1||!d||!/^data\/map_pack\/landmark_surfaces\/marseille-mns-[a-f0-9]{16}\.json$/.test(d.path)||!Number.isInteger(d.bytes)||d.bytes<1||d.bytes>MistralLandmarkSurfaces.MAX_BYTES||!/^[a-f0-9]{64}$/.test(d.sha256)||!d.path.endsWith(d.sha256.slice(0,16)+'.json'))throw Error('Descripteur MNS invalide');const atlas=MistralLandmarkSurfaces.validate(await v050LocalSourceJSON(d.path,d));runtime.source=atlas.source;runtime.records=new Map(atlas.records.map(r=>[r.cleabs,r]));runtime.loaded=true;if(world?.v046&&!V046.lab){for(const record of world.v046Records?.values()||[])apply(world,record.draws,record.colliders);const caps=[];apply(world,world.staticDraws,world.colliders);for(const record of world.v046Records?.values()||[])for(const cap of record.draws)if(cap.v056MeasuredRoof&&!world.staticDraws.includes(cap))caps.push(cap);if(caps.length)world.staticDraws=world.staticDraws.concat(caps);window.__MISTRAL_DEBUG?.v050FacadeRefresh?.();}return info();}catch(error){runtime.error=String(error.message||error);return info();}})();return runtime.promise;}
 const importing=v046Import;v046Import=function(...args){const result=importing(...args);if(runtime.loaded&&!runtime.error&&!V046.lab)apply(args[0],result.draws,result.colliders);return result;};
 const ensure=v046Ensure;v046Ensure=async function(...args){const serial=++runtime.serial;if(!V046.lab)await ready();if(serial!==runtime.serial)return false;return ensure(...args);};
 const cancel=v046Cancel;v046Cancel=function(...args){runtime.serial++;return cancel(...args);};
 const mesh=v018MeshData;v018MeshData=function(draw){return mesh(draw.v056MeasuredSurface?.walls||draw);};
 // Only complete generated facade triangles below the actual upper surface
 // are kept. Invented bays never remain floating over a measured lower roof.
 function clipFacade(draw,activeSurfaces){const surface=activeSurfaces.get(draw.facadeBuildingId?.split(':')[0]);if(!surface||!draw.vertices||!draw.faces)return draw;const hit=runtime.facadeCache.get(draw);if(hit?.surface===surface)return hit.draw;const faces=draw.faces.filter(f=>f.every(i=>{const p=draw.vertices[i],y=surface.index.heightAt(p[0],p[2],.10);return y!==null&&p[1]<=y+.015;})),result={...draw,faces,v046GeometryId:draw.v046GeometryId+':mns-clip-v1',revision:(draw.revision||0)+1,v056MeasuredRoofClipped:true};runtime.facadeTrianglesOmitted+=draw.faces.length-faces.length;runtime.facadeCache.set(draw,{surface,draw:result});return result;}
 const collect=collectDraws;collectDraws=function(...args){const draws=collect(...args),activeSurfaces=new Map();for(const cap of draws)if(cap.v056MeasuredRoof){const surface=runtime.byCap.get(cap);if(surface)activeSurfaces.set(surface.record.cleabs,surface);}return draws.map(d=>d.geoLayer==='facade'?clipFacade(d,activeSurfaces):d);};
 Object.assign(window.__MISTRAL_DEBUG,{v056LandmarkInfo:info,v056LandmarkReady:ready,v056LandmarkSurface:(id,x,z)=>{const s=runtime.applied.get(id);if(!s)return null;return{cleabs:id,sourceTileSha256:s.record.sourceTileSha256.slice(),minimumElevation:s.minimumElevation,maximumElevation:s.maximumElevation,roofVertices:s.roof.vertices.length,roofTriangles:s.roof.faces.length,wallTriangles:s.walls.faces.length,height:Number.isFinite(x)&&Number.isFinite(z)?s.index.heightAt(x,z):null,sourceProperties:JSON.parse(JSON.stringify(s.record.sourceProperties)),rawGeometry:JSON.parse(JSON.stringify(s.record.rawGeometry)),sampleVertices:s.roof.vertices.slice(0,12).map(p=>p.slice()),measurements:JSON.parse(JSON.stringify(s.record.measurements))};}});
 ready();
}
