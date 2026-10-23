/* Optional measured-source layers. A validated local import enriches the base
   pack; the engine never manufactures a survey or downloads one implicitly. */
const V050_GEOGRAPHY={index:null,indexPromise:null,bundles:new Map(),loads:new Map(),errors:[],loaded:false,epoch:0};
async function v050LocalSourceJSON(path,descriptor=null,optional=false){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
 try{
  const response=await fetch(path,{signal:controller.signal,cache:'no-store'});
  if(optional&&response.status===404)return null;
  if(!response.ok)throw Error('Source locale indisponible : HTTP '+response.status);
  const limit=descriptor?.bytes??(optional?1024*1024:64*1024*1024),declared=Number(response.headers?.get?.('content-length'));
  if(Number.isFinite(declared)&&declared>limit)throw Error('Source locale hors budget');
  let bytes;
  if(response.body?.getReader){
   const reader=response.body.getReader(),chunks=[];let total=0;
   try{while(true){const part=await reader.read();if(part.done)break;total+=part.value.byteLength;if(total>limit){await reader.cancel();throw Error('Source locale hors budget');}chunks.push(part.value);}const joined=new Uint8Array(total);let offset=0;for(const chunk of chunks){joined.set(chunk,offset);offset+=chunk.byteLength;}bytes=joined.buffer;}finally{reader.releaseLock?.();}
  }else bytes=await response.arrayBuffer();
  if(!bytes.byteLength||bytes.byteLength>limit)throw Error('Source locale hors budget');
  if(descriptor){
   if(bytes.byteLength!==descriptor.bytes)throw Error('Taille de source incohérente');
   if(!crypto.subtle)throw Error('Vérification SHA-256 indisponible');
   const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
   if(digest!==descriptor.sha256)throw Error('Empreinte SHA-256 de source incorrecte');
  }
  return JSON.parse(new TextDecoder().decode(bytes));
 }finally{clearTimeout(timer);}
}
function v050SourceBox(value){return Array.isArray(value)&&value.length===4&&value.every(Number.isFinite)&&value[0]<value[2]&&value[1]<value[3]&&value[0]>=-90&&value[2]<=90&&value[1]>=-180&&value[3]<=180;}
function v050SourceCoverage(properties,region){
 const proof=properties.provenance,coverage=proof?.coverage;if(!coverage)return null;
 const expected=properties.kind==='road'?'BDTOPO_V3:troncon_de_route':'BDTOPO_V3:batiment',bbox=coverage.bbox,bounds=V046_BOUNDS[region];
 if(proof.resource!=='ign-bdtopo'||coverage.complete!==true||coverage.crs!=='EPSG:4326'||coverage.layer!==expected||!Number.isInteger(coverage.returned)||coverage.returned<0||!v050SourceBox(bbox)||bbox[0]<bounds[0]||bbox[1]<bounds[1]||bbox[2]>bounds[2]||bbox[3]>bounds[3])throw Error('Preuve de couverture géographique incomplète');
 const polygon=[[bbox[0],bbox[1]],[bbox[0],bbox[3]],[bbox[2],bbox[3]],[bbox[2],bbox[1]]].map(p=>{const q=v015GeoProject(region,...p);return[q[0],q[2]];});
 return{proof:coverage,polygon};
}
/* Clip existing straight metric segments against the projected query boundary.
   Parameters are reused for Z, so no terrain height or guessed road connection
   is invented at the edge of an authoritative extract. Source files stay whole. */
function v050ClipSourcePaths(paths,polygon,inside=true){
 const area=polygon.reduce((sum,a,i)=>{const b=polygon[(i+1)%polygon.length];return sum+a[0]*b[1]-b[0]*a[1];},0),orientation=Math.sign(area);if(!orientation)throw Error('Emprise de couverture dégénérée');
 const fragments=[];let current=[];
 const same=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1])<1e-7&&(Number.isFinite(a[2])===Number.isFinite(b[2]))&&(!Number.isFinite(a[2])||Math.abs(a[2]-b[2])<1e-7),flush=()=>{if(current.length>1)fragments.push(current);current=[];};
 const at=(a,b,t)=>{if(t<=1e-12)return a.slice();if(t>=1-1e-12)return b.slice();const p=[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];if(Number.isFinite(a[2])&&Number.isFinite(b[2]))p[2]=a[2]+(b[2]-a[2])*t;return p;};
 for(const path of paths){
  flush();
  for(let i=1;i<path.length;i++){
   const a=path[i-1],b=path[i],dx=b[0]-a[0],dz=b[1]-a[1];let entry=0,exit=1,intersects=true;
   for(let j=0;j<polygon.length;j++){
    const p=polygon[j],q=polygon[(j+1)%polygon.length],ex=q[0]-p[0],ez=q[1]-p[1],offset=orientation*(ex*(a[1]-p[1])-ez*(a[0]-p[0])),direction=orientation*(ex*dz-ez*dx);
    if(Math.abs(direction)<1e-12){if(offset< -1e-7){intersects=false;break;}continue;}
    const t=-offset/direction;if(direction>0)entry=Math.max(entry,t);else exit=Math.min(exit,t);if(entry>exit+1e-12){intersects=false;break;}
   }
   let intervals;if(!intersects)intervals=inside?[]:[[0,1]];else if(inside)intervals=exit-entry>1e-12?[[Math.max(0,entry),Math.min(1,exit)]]:[];else intervals=[[0,Math.max(0,entry)],[Math.min(1,exit),1]].filter(([lo,hi])=>hi-lo>1e-12);
   if(!intervals.length){flush();continue;}
   for(const[lo,hi]of intervals){const first=at(a,b,lo),last=at(a,b,hi);if(Math.hypot(last[0]-first[0],last[1]-first[1])<1e-8)continue;if(current.length&&same(current.at(-1),first))current.push(last);else{flush();current=[first,last];}}
  }
  flush();
 }
 return fragments;
}
async function v050SourceIndex(){
 if(typeof location!=='undefined'&&!['http:','https:'].includes(location.protocol))return null;
 const epoch=V050_GEOGRAPHY.epoch;
 if(!V050_GEOGRAPHY.indexPromise)V050_GEOGRAPHY.indexPromise=(async()=>{
  const index=await v050LocalSourceJSON('data/map_pack/enrichment/index.json',null,true);
  if(index&&(index.schemaVersion!==1||index.crs!=='EPSG:4326'||!index.regions||typeof index.regions!=='object'||Array.isArray(index.regions)))throw Error('Index des sources incompatible');
  for(const[id,d]of Object.entries(index?.regions||{})){
   if(!V046_BOUNDS[id]||!/^data\/map_pack\/enrichment\/[a-zA-Z0-9_.-]+\.json$/.test(d.path)||!Number.isInteger(d.bytes)||d.bytes<1||d.bytes>64*1024*1024||!/^[0-9a-f]{64}$/.test(d.sha256)||!v050SourceBox(d.bbox))throw Error('Descripteur de source invalide : '+id);
  }
  if(epoch!==V050_GEOGRAPHY.epoch)throw Error('Index de sources périmé');
  V050_GEOGRAPHY.index=index;V050_GEOGRAPHY.loaded=true;return index;
 })().catch(error=>{if(epoch===V050_GEOGRAPHY.epoch)V050_GEOGRAPHY.indexPromise=null;throw error;});
 return V050_GEOGRAPHY.indexPromise;
}
function v050SourceFeature(feature,region){
 const p=feature?.properties,g=feature?.geometry;
 if(feature?.type!=='Feature'||!p||!['building','road'].includes(p.kind)||typeof p.sourceId!=='string'||!p.sourceId||!p.provenance||!['source','license','attribution','acquiredAt'].every(k=>typeof p.provenance[k]==='string'&&p.provenance[k].trim()))throw Error('Objet sans identité ou provenance de source');
 const expected=p.kind==='building'?['Polygon','MultiPolygon']:['LineString','MultiLineString'];if(!g||!expected.includes(g.type))throw Error('Type géographique incompatible avec '+p.kind);
 const absolute=['altitude_minimale_sol','altitude_maximale_sol','altitude_minimale_toit','altitude_maximale_toit','z_min_sol','z_max_sol','z_min_toit','z_max_toit','ground_elevation','roof_elevation','ele','deck_height','bridge:ele'].some(key=>MistralIntegrity.metres(p[key])!==null);
 if(absolute&&!MistralIntegrity.compatibleDatum(p.provenance.verticalDatum))throw Error('Référentiel vertical incompatible : conversion explicite vers NGF-IGN69 requise pour '+p.sourceId);
 let count=0;
 const project=coordinate=>{if(!Array.isArray(coordinate)||coordinate.length<2||coordinate.length>3||!coordinate.every(Number.isFinite)||coordinate[0]<-180||coordinate[0]>180||coordinate[1]<-90||coordinate[1]>90||++count>250000)throw Error('Coordonnée de source invalide');if(coordinate.length===3&&!MistralIntegrity.compatibleDatum(p.provenance.verticalDatum))throw Error('Référentiel vertical incompatible : conversion explicite vers NGF-IGN69 requise pour '+p.sourceId);const q=v015GeoProject(region,coordinate[1],coordinate[0]),out=[q[0],q[2]];if(coordinate.length===3)out[2]=coordinate[2];return out;};
 const ring=coordinates=>{if(!Array.isArray(coordinates)||coordinates.length<4||coordinates.length>2048)throw Error('Anneau source invalide');const points=coordinates.map(project),first=points[0],last=points.at(-1);if(first[0]!==last[0]||first[1]!==last[1])throw Error('Anneau source ouvert');return points.map(q=>q.slice(0,2));};
 const polygon=coordinates=>{if(!Array.isArray(coordinates)||!coordinates.length)throw Error('Polygone source vide');return coordinates.map(ring);};
 let groups=null,paths;
 if(g.type==='Polygon'){groups=[polygon(g.coordinates)];paths=groups.flat();}
 else if(g.type==='MultiPolygon'){groups=g.coordinates.map(polygon);paths=groups.flat();}
 else {const line=coordinates=>{if(!Array.isArray(coordinates)||coordinates.length<2)throw Error('Route source vide');return coordinates.map(project);};paths=g.type==='LineString'?[line(g.coordinates)]:g.coordinates.map(line);}
 const bounds=v017PolyBounds(paths),identity='source:'+region+':'+p.kind+':'+p.sourceId,coverage=v050SourceCoverage(p,region);
 if(p.kind==='road'&&coverage)paths=v050ClipSourcePaths(paths,coverage.polygon,true);
 return{id:identity,sourceId:p.sourceId,type:p.kind==='building'?3:2,props:{...p},v050Paths:paths,v050Groups:groups,v050Source:true,v050Geometry:g,v050Coverage:coverage,v050Bounds:bounds};
}
async function v050SourceBundle(region,descriptor){
 if(V050_GEOGRAPHY.bundles.has(region))return V050_GEOGRAPHY.bundles.get(region);
 const epoch=V050_GEOGRAPHY.epoch;
 if(!V050_GEOGRAPHY.loads.has(region))V050_GEOGRAPHY.loads.set(region,(async()=>{
  const raw=await v050LocalSourceJSON(descriptor.path,descriptor);
  if(raw?.schemaVersion!==1||raw.region!==region||!Array.isArray(raw.features)||raw.features.length>20000)throw Error('Fichier régional de sources invalide');
  const features=raw.features.map(feature=>v050SourceFeature(feature,region));
  if(raw.terrainTiles!==undefined&&(!Array.isArray(raw.terrainTiles)||raw.terrainTiles.length>16))throw Error('Atlas de terrain hors budget');
  const terrainGrids=[...(raw.terrain?[raw.terrain]:[]),...(raw.terrainTiles||[])],identities=new Set();let cells=0;
  if(terrainGrids.length>16)throw Error('Atlas de terrain hors budget');
  for(const grid of terrainGrids){
   const prefix='enrichment:'+region;
   if(typeof grid?.macro!=='string'||!grid.macro.startsWith(prefix)||grid.macro!==prefix&&!/^:[0-9a-f]{16}$/.test(grid.macro.slice(prefix.length))||identities.has(grid.macro))throw Error('Terrain source associé à une autre région ou identifiant dupliqué');
   identities.add(grid.macro);cells+=grid.width*grid.height;if(cells>4194304)throw Error('Atlas de terrain hors budget');
   MistralIntegrity.terrain(grid,grid.macro);
  }
  if(epoch!==V050_GEOGRAPHY.epoch)throw Error('Sources régionales périmées');
  const bundle={...raw,projected:features,terrainGrids};V050_GEOGRAPHY.bundles.set(region,bundle);return bundle;
 })().catch(error=>{if(epoch===V050_GEOGRAPHY.epoch)V050_GEOGRAPHY.loads.delete(region);throw error;}));
 return V050_GEOGRAPHY.loads.get(region);
}
function v050BoxesTouch(a,b){return a.minX<=b.maxX&&a.maxX>=b.minX&&a.minZ<=b.maxZ&&a.maxZ>=b.minZ;}
function v050FootprintsOverlap(a,b){
 if(MistralIntegrity.ringKey(a[0])===MistralIntegrity.ringKey(b[0]))return true;
 const orientation=(a,b,p)=>(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]);
 const boundary=(rings,p)=>rings.some(r=>r.some((a,i)=>{const q=r[(i+1)%r.length];return Math.abs(orientation(a,q,p))<1e-7&&p[0]>=Math.min(a[0],q[0])-1e-7&&p[0]<=Math.max(a[0],q[0])+1e-7&&p[1]>=Math.min(a[1],q[1])-1e-7&&p[1]<=Math.max(a[1],q[1])+1e-7;}));
 if(a[0].some(p=>!boundary(b,p)&&MistralIntegrity.inside(b,p[0],p[1]))||b[0].some(p=>!boundary(a,p)&&MistralIntegrity.inside(a,p[0],p[1])))return true;
 for(const ar of a)for(let i=1;i<ar.length;i++)for(const br of b)for(let j=1;j<br.length;j++)if(orientation(ar[i-1],ar[i],br[j-1])*orientation(ar[i-1],ar[i],br[j])< -1e-8&&orientation(br[j-1],br[j],ar[i-1])*orientation(br[j-1],br[j],ar[i])< -1e-8)return true;
 return false;
}
function v050SourceReplaces(feature,paths,overlays){
 const props=feature.props||{},id=String(props.sourceId??feature.id),bounds=v017PolyBounds(paths);
 for(const replacement of overlays){
  const replaces=replacement.props.replaces;
  if(id===replacement.sourceId||typeof replaces==='string'&&replaces===id||Array.isArray(replaces)&&replaces.includes(id))return true;
  if(feature.type===2){const lineKey=path=>{const points=path.map(p=>[Math.round(p[0]*1000),Math.round(p[1]*1000)]);return[JSON.stringify(points),JSON.stringify(points.slice().reverse())].sort()[0];};if(paths.every(original=>replacement.v050Paths.some(path=>lineKey(path)===lineKey(original))))return true;continue;}
  if(feature.type!==3||replacement.type!==3||!v050BoxesTouch(bounds,replacement.v050Bounds))continue;
  /* Positive footprint overlap, including an old solid roof over a newly
     surveyed courtyard. Touching adjacent walls alone never remove a neighbour. */
  const originalGroups=v018PolygonGroups(paths);
  if(replacement.v050Groups.some(rings=>originalGroups.some(original=>v050FootprintsOverlap(original,rings))))return true;
 }
 return false;
}
async function v050EnrichResource(resource,key,signal){
 const index=await v050SourceIndex();if(!index)return resource;
 if(signal?.aborted)throw Error('Import des sources annulé');
 if(key.startsWith('dem:')){
  const region=key.slice(4),descriptor=index.regions[region];if(descriptor)await v050SourceBundle(region,descriptor);return resource;
 }
 const tile=v017TileBounds(resource.z,resource.x,resource.y),box=[tile.south,tile.west,tile.north,tile.east],corners=[[tile.south,tile.west],[tile.south,tile.east],[tile.north,tile.west],[tile.north,tile.east]];
 const features=[];
 for(const[region,descriptor]of Object.entries(index.regions))if(MistralIntegrity.intersects(box,descriptor.bbox)){const bundle=await v050SourceBundle(region,descriptor);features.push(...bundle.projected);}
 if(signal?.aborted)throw Error('Import des sources annulé');
 return v050ApplySourceOverlays(resource,features);
}
/* Shared by optional regional imports and the partitioned city atlas. Empty
   authoritative road queries still remove old roads inside their exact query
   rectangle; no feature is manufactured to carry that proof. */
function v050ApplySourceOverlays(resource,features,explicitCoverages=[]){
 const tile=v017TileBounds(resource.z,resource.x,resource.y),box=[tile.south,tile.west,tile.north,tile.east],corners=[[tile.south,tile.west],[tile.south,tile.east],[tile.north,tile.west],[tile.north,tile.east]];
 const worldCorners=corners.map(p=>v015GeoProject('geo_huveaune',p[0],p[1])),tileBounds=v017PolyBounds([worldCorners.map(p=>[p[0],p[2]])]),kind=resource.source==='cadastre'?'building':'road',overlays=features.filter(f=>f.props.kind===kind&&f.v050Paths.length&&v050BoxesTouch(tileBounds,f.v050Bounds)),coverages=[],coverageKeys=new Set();
 if(kind==='road')for(const coverage of explicitCoverages)if(coverage.proof.layer==='BDTOPO_V3:troncon_de_route'&&MistralIntegrity.intersects(box,coverage.proof.bbox)){const key=JSON.stringify(coverage.proof);if(!coverageKeys.has(key)){coverageKeys.add(key);coverages.push(coverage);}}
 if(kind==='road')for(const feature of features)if(feature.props.kind==='road'&&feature.v050Coverage&&MistralIntegrity.intersects(box,feature.v050Coverage.proof.bbox)){const key=JSON.stringify(feature.v050Coverage.proof);if(!coverageKeys.has(key)){coverageKeys.add(key);coverages.push(feature.v050Coverage);}}
 if(!overlays.length&&!coverages.length)return resource;
 const layers={...resource.layers},names=kind==='building'?['batiments','building']:['transportation'];
 for(const name of names){const layer=layers[name];if(!layer)continue;const retained=[];
  for(const f of layer.features){let paths=v017FeatureWorldPaths(layer,f,resource.z,resource.x,resource.y,'geo_huveaune');
   if(kind==='road'&&f.type===2&&coverages.length){for(const coverage of coverages)paths=v050ClipSourcePaths(paths,coverage.polygon,false);if(!paths.length)continue;const unscoped=overlays.filter(overlay=>!overlay.v050Coverage);if(!v050SourceReplaces(f,paths,unscoped))retained.push({...f,v050Paths:paths});}
   else if(!v050SourceReplaces(f,paths,overlays))retained.push(f);
  }
  layers[name]={...layer,features:retained};
 }
 const target=kind==='building'?'building':'transportation',original=layers[target];layers[target]={...(original||{name:target,extent:4096}),features:[...(original?.features||[]),...overlays]};
 return{...resource,layers};
}
const v050SourceResourceBase=v046Resource;
v046Resource=async function(key,signal){const resource=await v050SourceResourceBase(key,signal);if(V046.lab)return resource;try{return await v050EnrichResource(resource,key,signal);}catch(error){if(!signal?.aborted){V050_GEOGRAPHY.errors.push(String(error.message||error));V050_GEOGRAPHY.errors=V050_GEOGRAPHY.errors.slice(-10);}throw error;}};
const v050SourceTerrainBase=MistralIntegrity.TerrainBank.prototype.add;
MistralIntegrity.TerrainBank.prototype.add=function(raw,id){
 const grid=v050SourceTerrainBase.call(this,raw,id);
 if(V046_BOUNDS[id]){
  const bundle=V046.lab?null:V050_GEOGRAPHY.bundles.get(id),overlays=bundle?.terrainGrids||(bundle?.terrain?[bundle.terrain]:[]),retained=new Set(overlays.map(overlay=>overlay.macro));
  for(const key of this.grids.keys())if((key==='enrichment:'+id||key.startsWith('enrichment:'+id+':'))&&!retained.has(key)){this.grids.delete(key);delete this.bounds[key];}
  for(const overlay of overlays)v050SourceTerrainBase.call(this,overlay,overlay.macro);
 }
 return grid;
};
function v050RefreshGeography(){
 if(V046.busy&&V046.gate?.status.phase!=='failed')return false;
 V050_GEOGRAPHY.epoch++;V050_GEOGRAPHY.index=null;V050_GEOGRAPHY.indexPromise=null;V050_GEOGRAPHY.loaded=false;V050_GEOGRAPHY.bundles.clear();V050_GEOGRAPHY.loads.clear();V050_GEOGRAPHY.errors=[];
 V046.gate?.cache.clear();V047.records?.clear();V047.meshes?.clear();V050_GEOGRAPHY.terrainMeshes?.clear();return true;
}
/* Cache identities cover georeferencing and dimensions as well as elevations. */
v047BankStamp=function(bank){return MistralIntegrity.hash([...bank.grids].sort(([a],[b])=>a.localeCompare(b)).map(([id,g])=>[id,g.width,g.height,g.bbox,g.sourceResource,g.verticalDatum,g.v047Digest||(g.v047Digest=MistralIntegrity.hash(Array.from(g.data)))]));};
/* Fine patches exceed the 12 MiB cache used by coarse terrain. Retain at most
   two in their own LRU; BudgetCache counts shared arrays once per patch with
   MistralStream.bytes rather than mistaking a mesh count for a memory bound. */
function v050TerrainCache(){return V050_GEOGRAPHY.terrainMeshes||(V050_GEOGRAPHY.terrainMeshes=new MistralStream.BudgetCache(64*1024*1024,2));}
/* Render native imported nodes near the player. The surrounding coarse cells
   are removed, then a sampled annulus joins the exact grid boundary to the
   global 32 m mesh. This is an explicit local LOD, not a claim that the entire
   territory is rendered at survey resolution. NoData never gets a triangle. */
async function v050RefineTerrainMeshes(coarse,plan,bank,stamp,job){
 const sources=[...bank.grids.values()].filter(g=>g.enrichment&&Math.max(...g.resolutionMeters)<32).map(g=>{
  const lat=Math.max(g.bbox[0],Math.min(g.bbox[2],plan.lat)),lon=Math.max(g.bbox[1],Math.min(g.bbox[3],plan.lon)),p=v015GeoProject('geo_huveaune',lat,lon);
  return{g,lat,lon,distance:Math.hypot(p[0]-plan.p[0],p[2]-plan.p[2])};
 }).filter(item=>item.distance<720&&![...bank.grids.values()].some(other=>!other.enrichment&&MistralIntegrity.contains(other.bbox,item.lat,item.lon)&&other.resolutionMeters[0]*other.resolutionMeters[1]<item.g.resolutionMeters[0]*item.g.resolutionMeters[1])).sort((a,b)=>a.distance-b.distance||a.g.resolutionMeters[0]*a.g.resolutionMeters[1]-b.g.resolutionMeters[0]*b.g.resolutionMeters[1]||a.g.id.localeCompare(b.g.id));
 if(!sources.length)return coarse;
 const {g,lat,lon}=sources[0],centerX=Math.round((lon-g.bbox[1])/(g.bbox[3]-g.bbox[1])*(g.width-1)),centerY=Math.round((g.bbox[2]-lat)/(g.bbox[2]-g.bbox[0])*(g.height-1)),halfX=Math.max(1,Math.min(255,Math.ceil(256/g.resolutionMeters[0]))),halfY=Math.max(1,Math.min(255,Math.ceil(256/g.resolutionMeters[1]))),whole=g.width*g.height<=262144&&(g.width-1)*g.resolutionMeters[0]<=512&&(g.height-1)*g.resolutionMeters[1]<=512;
 const x0=whole?0:Math.max(0,centerX-halfX),x1=whole?g.width-1:Math.min(g.width-1,centerX+halfX),y0=whole?0:Math.max(0,centerY-halfY),y1=whole?g.height-1:Math.min(g.height-1,centerY+halfY),width=x1-x0+1,height=y1-y0+1;
 if(width<2||height<2||width*height>262144)return coarse;
 const key='source-terrain:'+g.id+':'+[x0,x1,y0,y1].join(':')+':'+stamp;
 const cache=v050TerrainCache();let patch=cache.get(key);
 if(!patch){
  const vertices=[],faces=[],valid=[];let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
  for(let j=y0;j<=y1;j++){
   for(let i=x0;i<=x1;i++){
    const lat=g.bbox[2]-(g.bbox[2]-g.bbox[0])*j/(g.height-1),lon=g.bbox[1]+(g.bbox[3]-g.bbox[1])*i/(g.width-1),p=v015GeoProject('geo_huveaune',lat,lon),elevation=g.data[j*g.width+i];
    vertices.push([p[0],Number.isFinite(elevation)?elevation-.06:0,p[2]]);valid.push(Number.isFinite(elevation));minX=Math.min(minX,p[0]);maxX=Math.max(maxX,p[0]);minZ=Math.min(minZ,p[2]);maxZ=Math.max(maxZ,p[2]);
   }
   await job.work.checkpoint(width);
  }
  for(let j=0;j<height-1;j++){
   for(let i=0;i<width-1;i++){const a=j*width+i,b=a+1,c=a+width,d=c+1;if(valid[a]&&valid[b]&&valid[c])faces.push([a,c,b]);if(valid[b]&&valid[c]&&valid[d])faces.push([b,c,d]);}
   await job.work.checkpoint(width);
  }
  const border=[];
  for(let i=0;i<width;i++)border.push(vertices[i]);
  for(let j=1;j<height;j++)border.push(vertices[j*width+width-1]);
  for(let i=width-2;i>=0;i--)border.push(vertices[(height-1)*width+i]);
  for(let j=height-2;j>0;j--)border.push(vertices[j*width]);
  const inner=border.map(p=>[p[0],p[2]]);inner.push(inner[0].slice());
  const box={minX:Math.floor(minX/32)*32-32,maxX:Math.ceil(maxX/32)*32+32,minZ:Math.floor(minZ/32)*32-32,maxZ:Math.ceil(maxZ/32)*32+32},outer=[];
  for(let x=box.minX;x<box.maxX;x+=32)outer.push([x,box.minZ]);
  for(let z=box.minZ;z<box.maxZ;z+=32)outer.push([box.maxX,z]);
  for(let x=box.maxX;x>box.minX;x-=32)outer.push([x,box.maxZ]);
  for(let z=box.maxZ;z>box.minZ;z-=32)outer.push([box.minX,z]);outer.push(outer[0].slice());
  const seamVertices=[],seamFaces=[];
  for(const tri of v018Triangulate([outer,inner])){
   const points=tri.map(p=>{const ll=v015GeoUnproject('geo_huveaune',p[0],p[1]),h=bank.read(...ll).height;return h===null?null:[p[0],h-.06,p[1]];});
   if(points.every(Boolean)){const k=seamVertices.length;seamVertices.push(...points);seamFaces.push([k,k+2,k+1]);}
   if(seamFaces.length%128===0)await job.work.checkpoint(128);
  }
  const common={mesh:'terrain',pos:[(minX+maxX)/2,0,(minZ+maxZ)/2],scale:[1,1,1],color:[.30,.33,.25],v046Terrain:true,v046Bounds:box,revision:0,sourceResource:g.sourceResource,sourceSpacingMeters:g.resolutionMeters.slice(),sourceScope:'Nœuds de la grille importée dans un voisinage borné à 262144 sommets ; LOD de 32 m au-delà',v050LandMask:box,v050LandMaskId:key};
  patch={box,draws:[{...common,vertices,faces,v050FineTerrain:true,v047GeometryId:key},{...common,vertices:seamVertices,faces:seamFaces,v050TerrainSeam:true,v047GeometryId:key+':seam'}]};
  cache.set(key,patch);
 }
 const out=[];
 for(const draw of coarse){
  const faces=draw.faces.filter(face=>{const p=face.map(i=>draw.vertices[i]),x=(p[0][0]+p[1][0]+p[2][0])/3,z=(p[0][2]+p[1][2]+p[2][2])/3;return x<=patch.box.minX||x>=patch.box.maxX||z<=patch.box.minZ||z>=patch.box.maxZ;});
  if(faces.length===draw.faces.length)out.push(draw);else if(faces.length)out.push({...draw,faces,revision:(draw.revision||0)+1,v047GeometryId:draw.v047GeometryId+':cut:'+key});
  await job.work.checkpoint(draw.faces.length);
 }
 out.push(...patch.draws);return out;
}
/* Only render faces are replaced. Original land rings, records, surface indices
   and caches remain available for geography/gameplay. The sampled land colour
   follows the fine DEM triangles instead of bridging their measured relief. */
const V050_LAND_SUPPORT=new WeakMap(),V050_LAND_STYLES=new WeakMap(),V050_LAND_CUTS=new WeakMap();
async function v050TerrainSupport(draw,work){
 if(V050_LAND_SUPPORT.has(draw))return V050_LAND_SUPPORT.get(draw);
 let bounds=draw.v050LandMask;
 if(!bounds){bounds={minX:Infinity,maxX:-Infinity,minZ:Infinity,maxZ:-Infinity};let done=0;for(const p of draw.vertices){bounds.minX=Math.min(bounds.minX,p[0]);bounds.maxX=Math.max(bounds.maxX,p[0]);bounds.minZ=Math.min(bounds.minZ,p[2]);bounds.maxZ=Math.max(bounds.maxZ,p[2]);if(++done%2048===0)await work.checkpoint(2048);}}
 if(!Object.values(bounds).every(Number.isFinite)||bounds.minX>=bounds.maxX||bounds.minZ>=bounds.maxZ)return null;
 const support={bounds,key:draw.v050LandMaskId||draw.v047GeometryId};V050_LAND_SUPPORT.set(draw,support);return support;
}
function v050SurfaceInside(support,p){const b=support.bounds;return p[0]>b.minX&&p[0]<b.maxX&&p[1]>b.minZ&&p[1]<b.maxZ;}
/* A triangle/rectangle difference is partitioned into at most four convex
   pieces. Every boundary point interpolates XYZ on its original triangle;
   the interior is discarded even where the DEM deliberately has NoData. */
function v050ClipLandTriangle(triangle,support){
 const b=support.bounds;let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
 for(const p of triangle){minX=Math.min(minX,p[0]);maxX=Math.max(maxX,p[0]);minZ=Math.min(minZ,p[2]);maxZ=Math.max(maxZ,p[2]);}
 if(maxX<=b.minX||minX>=b.maxX||maxZ<=b.minZ||minZ>=b.maxZ)return[triangle];
 const planes=[[0,b.minX,1],[0,b.maxX,-1],[2,b.minZ,1],[2,b.maxZ,-1]],outside=[];let remaining=triangle;
 for(const[axis,edge,sign]of planes){if(remaining.length<3)break;const inside=[],piece=[];
  for(let i=0;i<remaining.length;i++){const a=remaining[i],q=remaining[(i+1)%remaining.length],da=(a[axis]-edge)*sign,dq=(q[axis]-edge)*sign;
   if(da>=0)inside.push(a);if(da<=0)piece.push(a);
   if(da>0&&dq<0||da<0&&dq>0){const t=da/(da-dq),p=a.map((value,k)=>value+(q[k]-value)*t);p[axis]=edge;inside.push(p);piece.push(p);}
  }
  for(let i=1;i<piece.length-1;i++){const a=piece[0],q=piece[i],c=piece[i+1];if(Math.abs((q[0]-a[0])*(c[2]-a[2])-(q[2]-a[2])*(c[0]-a[0]))>1e-10)outside.push([a,q,c]);}remaining=inside;
 }
 return outside;
}
async function v050RefineLandSurfaces(terrain,draws,job){
 const fine=terrain.filter(d=>d.v050FineTerrain||d.v050TerrainSeam);if(!fine.some(d=>d.v050FineTerrain))return{terrain,draws};
 const land=draws.filter(d=>!d.hidden&&['landcover','landuse','park'].includes(d.geoLayer)&&d.rings?.length&&d.vertices&&d.faces),landSet=new Set(land),supports=[];
 for(const draw of fine){const support=await v050TerrainSupport(draw,job.work);if(support&&!supports.some(s=>s.key===support.key))supports.push(support);}if(!supports.length)return{terrain,draws};
 const styled=new Map();
 for(const draw of fine){const support=V050_LAND_SUPPORT.get(draw);if(!support)continue;const relevant=land.filter(d=>v050BoxesTouch(v017PolyBounds(d.rings),support.bounds)),stamp=MistralIntegrity.hash(relevant.map(d=>[d.v046GeometryId,d.color])),cached=V050_LAND_STYLES.get(draw);if(cached?.stamp===stamp){styled.set(draw,cached.draws);continue;}
  const index=new MistralStream.SpatialGrid(32),priority={landcover:0,landuse:1,park:2};let ordinal=0;
  for(const d of relevant){const b=v017PolyBounds(d.rings);index.add({minX:Math.max(b.minX,support.bounds.minX),maxX:Math.min(b.maxX,support.bounds.maxX),minZ:Math.max(b.minZ,support.bounds.minZ),maxZ:Math.min(b.maxZ,support.bounds.maxZ)},{draw:d,rank:priority[d.geoLayer]*100000+ordinal++});await job.work.checkpoint();}
  const groups=new Map();let tests=0,done=0;
  for(const face of draw.faces){const p=face.map(i=>draw.vertices[i]),x=(p[0][0]+p[1][0]+p[2][0])/3,z=(p[0][2]+p[1][2]+p[2][2])/3;let chosen=null;
   for(const candidate of index.at(x,z)){tests++;if((!chosen||candidate.rank>chosen.rank)&&MistralIntegrity.inside(candidate.draw.rings,x,z))chosen=candidate;}
   const color=chosen?.draw.color||draw.color,key=color.join(',');if(!groups.has(key))groups.set(key,{color,faces:[]});groups.get(key).faces.push(face);if(++done%1024===0)await job.work.checkpoint(1024);
  }
  const pieces=[...groups].map(([key,group])=>({...draw,color:group.color,faces:group.faces,v050TerrainPatchId:draw.v047GeometryId,v047GeometryId:draw.v047GeometryId+':land:'+stamp+':'+key,landColorSampling:'Couleur au centre de chaque triangle ; anneaux et trous conservés, altitudes inchangées',landColorPolygons:relevant.length,landColorCandidateTests:tests,revision:(draw.revision||0)+1}));
  V050_LAND_STYLES.set(draw,{stamp,draws:pieces});styled.set(draw,pieces);
 }
 const output=[];let added=0;
 for(const draw of draws){if(!landSet.has(draw)){output.push(draw);continue;}const candidates=supports.filter(s=>v050BoxesTouch(v017PolyBounds(draw.rings),s.bounds));if(!candidates.length){output.push(draw);continue;}const key=candidates.map(s=>s.key).join('|');let cache=V050_LAND_CUTS.get(draw);if(!cache){cache=new Map();V050_LAND_CUTS.set(draw,cache);}if(cache.has(key)){const cached=cache.get(key);if(cached)output.push(cached);continue;}
  const vertices=[],faces=[];let done=0;
  for(const face of draw.faces){let triangles=[face.map(i=>draw.vertices[i])];for(const support of candidates)triangles=triangles.flatMap(tri=>v050ClipLandTriangle(tri,support));for(const tri of triangles){const k=vertices.length;vertices.push(...tri);const orientation=(tri[1][0]-tri[0][0])*(tri[2][2]-tri[0][2])-(tri[1][2]-tri[0][2])*(tri[2][0]-tri[0][0]);faces.push(orientation<0?[k,k+1,k+2]:[k,k+2,k+1]);}if((added+=triangles.length*3)>1048576)throw Error('Découpe des surfaces au-delà du budget géométrique');if(++done%32===0)await job.work.checkpoint(32);}
  const cut=faces.length?{...draw,vertices,faces,v050LandCut:true,v050LandCutSupports:candidates.map(s=>s.key),revision:(draw.revision||0)+1,v047GeometryId:(draw.v047GeometryId||draw.v046GeometryId)+':fine-cut:'+MistralIntegrity.hash(key)}:null;cache.set(key,cut);if(cache.size>4)cache.delete(cache.keys().next().value);if(cut)output.push(cut);await job.work.checkpoint();
 }
 return{terrain:terrain.flatMap(d=>styled.get(d)||[d]),draws:output};
}
function v050TerrainMeshInfo(){
 const patches=new Map();for(const d of world?.staticDraws||[]){if(!d.v050FineTerrain)continue;const key=d.v050TerrainPatchId||d.v047GeometryId;if(!patches.has(key))patches.set(key,{source:d.sourceResource,nodeSpacingMeters:d.sourceSpacingMeters,vertices:d.vertices.length,faces:0,scope:d.sourceScope,colorGroups:0,colorSampling:d.landColorSampling||null,colorPolygonCount:d.landColorPolygons||0,colorCandidateTests:d.landColorCandidateTests||0});const p=patches.get(key);p.faces+=d.faces.length;p.colorGroups++;}return[...patches.values()];
}
function v050LandSurfaceInfo(){
 const draws=world?.staticDraws||[],masks=new Map();for(const d of draws)if(d.v050LandMask)masks.set(d.v050LandMaskId,{bounds:d.v050LandMask,key:d.v050LandMaskId});
 let trianglesInside=0,clippedDraws=0,coloredFaces=0,seamColoredFaces=0;
 for(const d of draws){if(d.v050FineTerrain&&d.landColorSampling)coloredFaces+=d.faces.length;if(d.v050TerrainSeam&&d.landColorSampling)seamColoredFaces+=d.faces.length;if(d.v050LandCut)clippedDraws++;
  if(d.hidden||!['landcover','landuse','park'].includes(d.geoLayer)||!d.vertices||!d.faces)continue;
  for(const face of d.faces){const tri=face.map(i=>d.vertices[i]),area=t=>Math.abs((t[1][0]-t[0][0])*(t[2][2]-t[0][2])-(t[1][2]-t[0][2])*(t[2][0]-t[0][0]))/2;for(const support of masks.values())if(area(tri)-v050ClipLandTriangle(tri,support).reduce((sum,t)=>sum+area(t),0)>1e-6){trianglesInside++;break;}}
 }
 return{masks:[...masks.values()].map(s=>s.bounds),clippedDraws,coloredFaces,seamColoredFaces,oldLandTrianglesInside:trianglesInside,colorSampling:'Centre des triangles, index spatial de 32 m ; eau et routes inchangées'};
}
function v050SourceObjectInfo(sourceId){
 const draw=(world?.staticDraws||[]).find(d=>d.geoProperties?.sourceId===sourceId&&d.sourceProfile);return draw?v050SourceObjectSummary(draw):null;
}
function v050SourceObjectSummary(draw){return{id:draw.geoFeatureId||draw.id,sourceId:draw.geoProperties.sourceId,kind:draw.geoLayer,baseY:draw.baseY??null,height:draw.height??null,profile:{...draw.sourceProfile},footprintRings:draw.rings?.length||0,vertices:draw.vertices?.length||0,provenance:draw.geoProperties.provenance||null};}
function v050GeographyInfo(){
 const bundles=[...V050_GEOGRAPHY.bundles.values()],draws=(world?.staticDraws||[]).filter(d=>d.geoProperties?.sourceId&&d.sourceProfile),coverages=new Map();
 for(const bundle of bundles)for(const feature of bundle.projected){const proof=feature.props.provenance;if(proof?.coverage)coverages.set(JSON.stringify([proof.resource,proof.coverage]),{...proof.coverage,source:proof.source,resource:proof.resource,inputSha256:proof.inputSha256});}
 return{version:'0.50.0',indexPresent:!!V050_GEOGRAPHY.index,loadedRegions:[...V050_GEOGRAPHY.bundles.keys()].sort(),sourceBuildings:bundles.reduce((n,b)=>n+b.projected.filter(f=>f.props.kind==='building').length,0),sourceRoads:bundles.reduce((n,b)=>n+b.projected.filter(f=>f.props.kind==='road').length,0),coverages:[...coverages.values()],terrainSources:[...V046.terrain.grids.values()].map(g=>({id:g.id,resource:g.sourceResource,resolutionMeters:g.resolutionMeters.slice(),enrichment:g.enrichment,verticalDatum:g.verticalDatum,conversion:g.provenance?.conversion||null})),terrainCache:V050_GEOGRAPHY.terrainMeshes?.stats()||null,missingGroundBuildings:[...world?.v046Records?.values()||[]].reduce((n,r)=>n+(r.missingGroundBuildings||0),0),sourceObjectCount:draws.length,sourceObjectsTruncated:draws.length>100,sourceObjects:draws.slice(0,100).map(v050SourceObjectSummary),terrainMesh:v050TerrainMeshInfo(),errors:V050_GEOGRAPHY.errors.slice()};
}
function v050GeographyAfterInit(){Object.assign(window.__MISTRAL_DEBUG,{v050GeographyInfo,v050SourceObjectInfo,v050LandSurfaceInfo,v050RefreshGeography});$('v046Retry')?.addEventListener('click',()=>{if(V050_GEOGRAPHY.errors.length)v050RefreshGeography();},true);}
