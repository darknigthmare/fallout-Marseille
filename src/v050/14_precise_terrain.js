/* Native LiDAR cell values stay in their published Lambert-93 lattice.
   This optional twelve-square-kilometre atlas neither replaces old archives
   nor labels a reprojection or a denser output grid as a new measurement. */
const MistralPreciseTerrain=(()=>{
 const finite=Number.isFinite,resource='ign_lidar_hd_mnt',maximum=1048576;
 function descriptor(d){
  if(!d||!/^enrichment:geo_marseille_commune:[0-9a-f]{16}$/.test(d.id)||!/^data\/map_pack\/precise\/native-r[0-9]{5}-c[0-9]{5}-[0-9a-f]{16}\.f32$/.test(d.path)||!/^[0-9a-f]{64}$/.test(d.sha256)||!d.path.endsWith('-'+d.sha256.slice(0,16)+'.f32')||!Number.isInteger(d.width)||!Number.isInteger(d.height)||d.width<2||d.height<2||d.width*d.height>maximum||d.bytes!==d.width*d.height*4||d.crs!=='EPSG:2154'||d.verticalDatum!=='NGF-IGN69'||d.dataType!=='Float32LE'||d.rowOrder!=='north-to-south'||d.nodata!==-9999)throw Error('Dalle LiDAR native incompatible');
  if(!Array.isArray(d.origin)||d.origin.length!==2||!d.origin.every(finite)||!Array.isArray(d.step)||d.step.length!==2||d.step[0]!==.5||d.step[1]!==-.5||!Array.isArray(d.bbox)||d.bbox.length!==4||!d.bbox.every(finite)||d.bbox[0]>=d.bbox[2]||d.bbox[1]>=d.bbox[3]||!Array.isArray(d.nativeBounds)||d.nativeBounds.length!==4||d.nativeBounds.some((v,i)=>!finite(v)||Math.abs(v-[d.origin[0],d.origin[1]-(d.height-1)*.5,d.origin[0]+(d.width-1)*.5,d.origin[1]][i])>1e-7)||!Number.isInteger(d.validPoints)||!Number.isInteger(d.noDataPoints)||d.validPoints<0||d.noDataPoints<0||d.validPoints+d.noDataPoints!==d.width*d.height)throw Error('Géoréférencement LiDAR natif incohérent');
  return d;
 }
 function index(value){
  if(!value||value.schemaVersion!==1||value.kind!=='native-lidar-f32'||value.crs!=='EPSG:2154'||value.verticalDatum!=='NGF-IGN69'||value.nativeSpacingMeters!==.5||value.sourceResource!==resource||value.sourceTiles!==12||value.coverageSquareMeters!==12000000||!Array.isArray(value.nativeExtent)||JSON.stringify(value.nativeExtent)!=='[892000,6245000,895000,6249000]'||!Array.isArray(value.tiles)||value.tiles.length!==48||!value.provenance||!['source','license','attribution','acquiredAt'].every(k=>typeof value.provenance[k]==='string'&&value.provenance[k].trim())||value.provenance.resampled!==false)throw Error('Atlas LiDAR natif incompatible');
  const ids=new Set(),paths=new Set(),windows=new Set();let bytes=0;
  for(const d of value.tiles){descriptor(d);const match=d.path.match(/native-r([0-9]{5})-c([0-9]{5})-/),row=+match[1],column=+match[2],window=row+':'+column;if(row%1000||column%1000||row>7000||column>5000||d.width!==Math.min(1001,6000-column)||d.height!==Math.min(1001,8000-row)||d.origin[0]!==892000+column*.5||d.origin[1]!==6249000-row*.5||!Array.isArray(d.sourceIds)||!d.sourceIds.length||d.sourceIds.length>4||d.sourceIds.some(id=>!/^metadata\.[0-9]+$/.test(id)))throw Error('Fenêtre native différente du treillis source');if(ids.has(d.id)||paths.has(d.path)||windows.has(window))throw Error('Dalle LiDAR dupliquée');ids.add(d.id);paths.add(d.path);windows.add(window);bytes+=d.bytes;}
  if(bytes>256*1024*1024||value.validPoints!==value.tiles.reduce((n,d)=>n+d.validPoints,0)||value.noDataPoints!==value.tiles.reduce((n,d)=>n+d.noDataPoints,0))throw Error('Atlas LiDAR hors budget');return value;
 }
 function decode(buffer,d,provenance){
  descriptor(d);if(!(buffer instanceof ArrayBuffer)||buffer.byteLength!==d.bytes)throw Error('Binaire LiDAR tronqué');
  const view=new DataView(buffer),data=new Float32Array(d.width*d.height);let valid=0,missing=0;
  for(let i=0;i<data.length;i++){const z=view.getFloat32(i*4,true);if(!finite(z)||z===d.nodata){data[i]=NaN;missing++;}else{if(z<=-100||z>=9000)throw Error('Altitude LiDAR invalide, non remplacée');data[i]=z;valid++;}}
  if(valid!==d.validPoints||missing!==d.noDataPoints)throw Error('Masque NoData LiDAR différent du reçu');
  return{id:d.id,width:d.width,height:d.height,bbox:d.bbox.slice(),data,v054Native:true,origin:d.origin.slice(),step:d.step.slice(),nativeBounds:d.nativeBounds.slice(),resolutionMeters:[.5,.5],enrichment:true,sourceResource:resource,verticalDatum:d.verticalDatum,provenance:{...provenance},v047Digest:d.sha256+':'+JSON.stringify([d.origin,d.step,d.width,d.height,d.nodata,d.crs]),noDataPoints:missing};
 }
 function sample(grid,easting,northing){
  let x=(easting-grid.origin[0])/.5,y=(grid.origin[1]-northing)/.5;
  if(!finite(x)||!finite(y)||x< -1e-6||y< -1e-6||x>grid.width-1+1e-6||y>grid.height-1+1e-6)return{inside:false,height:null};
  x=Math.max(0,Math.min(grid.width-1,x));y=Math.max(0,Math.min(grid.height-1,y));
  const a=Math.floor(x),b=Math.floor(y),c=Math.min(a+1,grid.width-1),d=Math.min(b+1,grid.height-1),u=x-a,v=y-b;let z=0,weight=0;
  for(const[ix,iy,w]of[[a,b,(1-u)*(1-v)],[c,b,u*(1-v)],[a,d,(1-u)*v],[c,d,u*v]]){if(w<=1e-12)continue;const h=grid.data[iy*grid.width+ix];if(!finite(h))return{inside:true,height:null};z+=h*w;weight+=w;}
  return{inside:true,height:weight?z/weight:null,pixel:[x,y]};
 }
 function read(bank,lat,lon,project,sampleLegacy){
  const candidates=[],sources=[],noData=[],nativeMissing=[];let projected=null;
  for(const id of Object.keys(bank.bounds).sort()){
   const b=bank.bounds[id];if(lat<b[0]||lat>b[2]||lon<b[1]||lon>b[3])continue;
   const g=bank.grids.get(id);if(!g)return{height:null,missing:id,sources};
   let height;
   if(g.v054Native){projected||=project(lat,lon);const out=sample(g,...projected);if(!out.inside)continue;height=out.height;if(height===null)nativeMissing.push(id);}
   else height=sampleLegacy(g,lat,lon);
   if(height===null){noData.push(id);continue;}candidates.push({id,g,height,resolution:g.resolutionMeters[0]*g.resolutionMeters[1]});
  }
  /* Fine NoData stays missing inside its true native support. It is never
     filled with a coarser sample and presented as a fine surveyed altitude. */
  if(nativeMissing.length&&!candidates.some(c=>c.g.v054Native))return{height:null,missing:null,sources:[],noData,resolutionMeters:[.5,.5],sourceResource:resource,interpolation:'LiDAR natif absent : aucun comblement',verticalDatum:'NGF-IGN69'};
  candidates.sort((a,b)=>a.resolution-b.resolution||Number(b.g.v054Native)-Number(a.g.v054Native)||Number(b.g.enrichment)-Number(a.g.enrichment)||a.id.localeCompare(b.id));
  const chosen=candidates[0];if(chosen)sources.push(chosen.id);
  return{height:chosen?.height??null,missing:null,sources,noData,resolutionMeters:chosen?.g.resolutionMeters.slice()||null,sourceResource:chosen?.g.sourceResource||null,interpolation:chosen?.g.v054Native?'bilinéaire sur centres natifs Lambert-93, voisins valides requis':'bilinéaire, quatre échantillons valides requis',verticalDatum:chosen?.g.verticalDatum||null};
 }
 function selected(atlas,p,origin,radius=384){
  const x=p[0]+origin[0],y=origin[1]-p[2];return(atlas?.tiles||[]).filter(d=>d.nativeBounds[0]<=x+radius&&d.nativeBounds[2]>=x-radius&&d.nativeBounds[1]<=y+radius&&d.nativeBounds[3]>=y-radius);
 }
 function meshCenter(p,origin,extent=[892000,6245000,895000,6249000]){
  const half=127.5,clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
  return[clamp(Math.round((p[0]+origin[0])*2)/2,extent[0]+half,extent[2]-.5-half)-origin[0],origin[1]-clamp(Math.round((origin[1]-p[2])*2)/2,extent[1]+.5+half,extent[3]-half)];
 }
 /* Refine the existing XY triangles, never the source road axis or width.
    Mid-edge and centroid probes catch ground relief hidden by a sparse stroke.
    These are bounded rendering probes, not a new survey or an error guarantee
    between probes. Coarse-only triangles keep their original representation. */
 function roadSurface(vertices,faces,read,options={}){
  const tolerance=options.tolerance??.04,minEdge=options.minEdge??1,maxEdge=options.maxEdge??8,maxSplits=options.maxSplits??2048,lift=.085;
  if(![tolerance,minEdge,maxEdge].every(n=>finite(n)&&n>0)||maxEdge<minEdge||!Number.isInteger(maxSplits)||maxSplits<0||maxSplits>8192)throw Error('Budget du ruban LiDAR invalide');
  const probes=new Map(),indices=new Map(),out=[],triangles=[],leaves=[],splitEdges=new Map(),sources=new Map(),stats={inputFaces:faces.length,outputFaces:0,splits:0,conformitySplits:0,samples:0,nativeSamples:0,noDataSamples:0,omittedNoDataFaces:0,budgetLimitedFaces:0,resolutionLimitedFaces:0,maxInputProbeErrorMeters:0,maxAdaptiveLeafProbeErrorMeters:0,toleranceMeters:tolerance,minimumEdgeMeters:minEdge,maximumEdgeMeters:maxEdge,maximumSplits:maxSplits,visualOffsetMeters:lift};
  function probe(x,z){const key=x+':'+z;if(probes.has(key))return probes.get(key);const r=read(x,z)||{},height=finite(r.height)?r.height:null,native=r.sourceResource===resource;
   const p={x,z,height,native};probes.set(key,p);stats.samples++;if(native)stats.nativeSamples++;if(height===null)stats.noDataSamples++;
   for(const id of r.sources||[])if(!sources.has(id))sources.set(id,{id,sourceResource:r.sourceResource||null,verticalDatum:r.verticalDatum||null,resolutionMeters:r.resolutionMeters?.slice()||null,interpolation:r.interpolation||null});return p;
  }
  function emit(points,original=false){const face=[];for(const p of points){const position=original?p:[p.x,p.height+lift,p.z],key=position.join(':');if(!indices.has(key)){indices.set(key,out.length);out.push(position.slice());}face.push(indices.get(key));}triangles.push(face);}
  const edgeKey=(a,b)=>{const first=a[0]+':'+a[2],second=b[0]+':'+b[2];return first<second?first+'|'+second:second+'|'+first;};
  function visit(raw,depth=0){
   const p=raw.map(v=>probe(v[0],v[2])),mid=p.map((a,i)=>{const b=p[(i+1)%3];return probe((a.x+b.x)/2,(a.z+b.z)/2);}),center=probe((p[0].x+p[1].x+p[2].x)/3,(p[0].z+p[1].z+p[2].z)/3),all=[...p,...mid,center];
   if(!all.some(v=>v.native)){leaves.push({raw,original:true});return;}
   const missing=all.some(v=>v.height===null),lengths=p.map((a,i)=>Math.hypot(a.x-p[(i+1)%3].x,a.z-p[(i+1)%3].z)),edge=lengths.indexOf(Math.max(...lengths)),longest=lengths[edge];
   const error=missing?Infinity:Math.max(...mid.map((m,i)=>Math.abs(m.height-(p[i].height+p[(i+1)%3].height)/2)),Math.abs(center.height-(p[0].height+p[1].height+p[2].height)/3)),needs=missing||longest>maxEdge||error>tolerance;
   if(depth===0&&finite(error))stats.maxInputProbeErrorMeters=Math.max(stats.maxInputProbeErrorMeters,error);
   if(needs&&longest>minEdge&&depth<24&&stats.splits<maxSplits){stats.splits++;const a=edge,b=(edge+1)%3,c=(edge+2)%3,m=[mid[edge].x,0,mid[edge].z];splitEdges.set(edgeKey(raw[a],raw[b]),m);visit([raw[a],m,raw[c]],depth+1);visit([m,raw[b],raw[c]],depth+1);return;}
   if(missing){stats.omittedNoDataFaces++;return;}
   if(needs){if(stats.splits>=maxSplits)stats.budgetLimitedFaces++;else stats.resolutionLimitedFaces++;}
   stats.maxAdaptiveLeafProbeErrorMeters=Math.max(stats.maxAdaptiveLeafProbeErrorMeters,error);leaves.push({raw,original:false});
  }
  for(const face of faces){if(!Array.isArray(face)||face.length!==3||face.some(i=>!Number.isInteger(i)||!Array.isArray(vertices[i])||vertices[i].length<3||!vertices[i].slice(0,3).every(finite)))throw Error('Triangle de chaussée invalide');visit(face.map(i=>vertices[i]));}
  /* Carry every existing edge split into its neighbouring leaf. Otherwise an
     independently refined triangle could leave a vertical crack at a T join.
     This only propagates the finite adaptive split tree; it cannot start an
     additional error-driven refinement or exceed its source-edge partitions. */
  function conform(raw,original){for(let a=0;a<3;a++){const b=(a+1)%3,c=(a+2)%3,m=splitEdges.get(edgeKey(raw[a],raw[b]));if(m){stats.conformitySplits++;conform([raw[a],m,raw[c]],false);conform([m,raw[b],raw[c]],false);return;}}
   const p=raw.map(v=>probe(v[0],v[2]));if(p.some(v=>v.height===null)){stats.omittedNoDataFaces++;return;}emit(original?raw:p,original);
  }
  for(const leaf of leaves)conform(leaf.raw,leaf.original);
  stats.outputFaces=triangles.length;return{vertices:out,faces:triangles,stats,sources:[...sources.values()]};
 }
 return{descriptor,index,decode,sample,read,selected,meshCenter,roadSurface,resource};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralPreciseTerrain;

if(typeof window!=='undefined'&&typeof v046Ensure==='function'){
 const M=MistralPreciseTerrain,R={index:null,promise:null,epoch:0,known:false,loads:new Map(),cache:new MistralStream.BudgetCache(48*1024*1024,12),meshes:new MistralStream.BudgetCache(48*1024*1024,1),errors:[],requests:0};
 const error=e=>{R.errors.push(String(e?.message||e));R.errors=R.errors.slice(-10);};
 const sourceRoad=typeof v046SourceRoad==='function'?v046SourceRoad:null;
 if(sourceRoad)v046SourceRoad=function(w,path,props,color,key,layerName){
  const d=sourceRoad(w,path,props,color,key,layerName),bank=w.v047TerrainBank||V046.terrain;
  if(!d?.sourceProfile?.surfaceDerived||![...bank.grids.values()].some(g=>g.v054Native))return d;
  const refined=M.roadSurface(d.vertices,d.faces,(x,z)=>bank.read(...v015GeoUnproject(w.id,x,z)));
  if(!refined.stats.nativeSamples)return d;
  d.vertices=refined.vertices;d.faces=refined.faces;d.revision=(d.revision||0)+1;d.sourceProfile.surfaceNativeRefinement={...refined.stats,scope:'Sondages natifs aux sommets, milieux et centres des triangles ; seuils et budgets de rendu, pas une nouvelle mesure ni une borne continue de précision'};
  d.sourceProfile.surfaceTerrainSources=refined.sources;
  if(!d.faces.length){const at=w.staticDraws.indexOf(d);if(at>=0)w.staticDraws.splice(at,1);return null;}return d;
 };
 async function ready(){
  if(V046.lab)return null;if(R.promise)return R.promise;const epoch=R.epoch;
  const promise=(async()=>{const raw=await v050LocalSourceJSON('data/map_pack/precise/index.json',null,true);if(epoch!==R.epoch)throw Error('Atlas LiDAR périmé');if(!raw){if(R.known)throw Error('Atlas LiDAR précédemment chargé absent');return null;}const atlas=M.index(raw);for(const d of atlas.tiles)for(const[e,n]of[[d.nativeBounds[0],d.nativeBounds[1]],[d.nativeBounds[2],d.nativeBounds[1]],[d.nativeBounds[0],d.nativeBounds[3]],[d.nativeBounds[2],d.nativeBounds[3]]]){const ll=v018InverseLambert(e,n);if(ll[0]<d.bbox[0]-1e-7||ll[0]>d.bbox[2]+1e-7||ll[1]<d.bbox[1]-1e-7||ll[1]>d.bbox[3]+1e-7||d.bbox[2]-d.bbox[0]>.006||d.bbox[3]-d.bbox[1]>.008)throw Error('Emprise WGS84 différente du repère natif');}R.index=atlas;R.known=true;return R.index;})();
  R.promise=promise;promise.catch(e=>{if(epoch===R.epoch&&R.promise===promise)R.promise=null;});return promise;
 }
 const add=MistralIntegrity.TerrainBank.prototype.add;
 MistralIntegrity.TerrainBank.prototype.add=function(raw,id){
  if(!raw?.v054Native)return add.call(this,raw,id);
  if(raw.id!==id||!(raw.data instanceof Float32Array)||raw.data.length!==raw.width*raw.height)throw Error('Ressource LiDAR native incohérente');
  this.bounds[id]=raw.bbox.slice();this.grids.set(id,raw);return raw;
 };
 const read=MistralIntegrity.TerrainBank.prototype.read;
 MistralIntegrity.TerrainBank.prototype.read=function(lat,lon){return[...this.grids.values()].some(g=>g.v054Native)?M.read(this,lat,lon,v018Lambert93,MistralIntegrity.sample):read.call(this,lat,lon);};
 const plan=v046Plan;v046Plan=function(lat,lon){const out=plan(lat,lon);if(!V046.lab&&R.index){const selected=M.selected(R.index,out.p,V046_ORIGIN);if(selected.length>9||selected.reduce((n,d)=>n+d.bytes,0)>37*1024*1024)throw Error('Secteur LiDAR hors budget');for(const d of selected)out.dem.push('precisedem:'+d.id.split(':').at(-1));}return out;};
 async function binary(d,signal){
  v051CityAbort(signal);const cached=R.cache.get(d.path);if(cached)return cached;const epoch=R.epoch;
  if(!R.loads.has(d.path)){
   const promise=(async()=>{
    R.requests++;const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
    try{const response=await fetch(d.path,{signal:controller.signal,cache:'no-store'});if(!response.ok)throw Error('Binaire LiDAR indisponible : HTTP '+response.status);
     const declared=response.headers.get('Content-Length');if(declared!==null&&Number(declared)!==d.bytes)throw Error('Taille LiDAR annoncée incorrecte');
     const buffer=await v047ReadBody(response,controller.signal,d.bytes);if(buffer.byteLength!==d.bytes||MistralStream.sha256(buffer)!==d.sha256)throw Error('Empreinte binaire LiDAR incorrecte');
     const grid=M.decode(buffer,d,R.index.provenance);if(epoch!==R.epoch)throw Error('Binaire LiDAR périmé');const result={raw:grid,id:grid.id,source:'IGN — MNT LiDAR HD natif 0,5 m',origin:'IGN — MNT LiDAR HD natif 0,5 m'};R.cache.set(d.path,result);return result;
    }finally{clearTimeout(timer);}
   })();R.loads.set(d.path,promise);promise.then(()=>{if(R.loads.get(d.path)===promise)R.loads.delete(d.path);},()=>{if(R.loads.get(d.path)===promise)R.loads.delete(d.path);});
  }
  return v051CityWait(R.loads.get(d.path),signal);
 }
 const resource=v046Resource;v046Resource=async function(key,signal){
  if(V046.lab||!key.startsWith('precisedem:'))return resource(key,signal);
  const d=R.index?.tiles.find(t=>t.id.endsWith(':'+key.slice(11)));if(!d)throw Error('Dalle LiDAR inconnue');return binary(d,signal);
 };
 const ensure=v046Ensure;v046Ensure=async function(...args){
  if(!V046.lab){const serial=V051_CITY.navigationSerial;try{await ready();}catch(e){if(serial!==V051_CITY.navigationSerial)return false;error(e);V046.last={lat:args[0],lon:args[1],w:args[2]||world,initial:!!args[3],opts:args[4]||{}};V046.error=[{key:'precise-index',message:String(e.message||e)}];if(!args[4]?.v047Warm){V046.busy=true;zoneTransitioning=true;mode='LOADING';v046Loading({phase:'failed',done:0,total:1,errors:V046.error});}return false;}if(serial!==V051_CITY.navigationSerial)return false;}
  return ensure(...args);
 };
 const refresh=v051CityRefresh;v051CityRefresh=function(){if(!refresh())return false;R.epoch++;R.index=null;R.promise=null;R.loads.clear();R.cache.clear();R.meshes.clear();R.errors=[];return true;};
 function nativeAt(grids,x,z){const e=x+V046_ORIGIN[0],n=V046_ORIGIN[1]-z;let inside=false;for(const g of grids){const r=M.sample(g,e,n);if(r.inside){inside=true;if(r.height!==null)return r.height;}}return null;}
 const refine=v050RefineTerrainMeshes;
 v050RefineTerrainMeshes=async function(coarse,plan,bank,stamp,job){
  const grids=[...bank.grids.values()].filter(g=>g.v054Native);
  const p=plan.p,center=grids.find(g=>M.sample(g,p[0]+V046_ORIGIN[0],V046_ORIGIN[1]-p[2]).inside);
  if(!center){if(!grids.length)return refine(coarse,plan,bank,stamp,job);const view=Object.create(bank);view.grids=new Map([...bank.grids].filter(([,g])=>!g.v054Native));view.bounds=Object.fromEntries(Object.entries(bank.bounds).filter(([id])=>view.grids.has(id)||!id.startsWith('enrichment:')));return refine(coarse,plan,view,stamp,job);}
  /* Recenter the mesh window at the atlas edges, never its source cells or
     the player. Cutting a square beyond native support would erase valid
     coarse terrain without supplying fine faces on that outside portion. */
  const[x,z]=M.meshCenter(p,V046_ORIGIN,R.index?.nativeExtent);
  const half=127.5,width=511,key='native-lidar:'+x+':'+z+':'+stamp;let patch=R.meshes.get(key);
  if(!patch){
   const vertices=[],valid=[],faces=[],x0=x-half,z0=z-half;
   for(let j=0;j<width;j++){for(let i=0;i<width;i++){const xx=x0+i*.5,zz=z0+j*.5,h=nativeAt(grids,xx,zz);vertices.push([xx,h===null?0:h-.06,zz]);valid.push(h!==null);}await job.work.checkpoint(width);}
   for(let j=0;j<width-1;j++){for(let i=0;i<width-1;i++){const a=j*width+i,b=a+1,c=a+width,d=c+1;if(valid[a]&&valid[b]&&valid[c])faces.push([a,c,b]);if(valid[b]&&valid[c]&&valid[d])faces.push([b,c,d]);}await job.work.checkpoint(width);}
   const border=[];for(let i=0;i<width;i++)border.push(vertices[i]);for(let j=1;j<width;j++)border.push(vertices[j*width+width-1]);for(let i=width-2;i>=0;i--)border.push(vertices[(width-1)*width+i]);for(let j=width-2;j>0;j--)border.push(vertices[j*width]);
   const inner=border.map(v=>[v[0],v[2]]);inner.push(inner[0].slice());
   const box={minX:Math.floor(x0/32)*32-32,maxX:Math.ceil((x0+255)/32)*32+32,minZ:Math.floor(z0/32)*32-32,maxZ:Math.ceil((z0+255)/32)*32+32},outer=[];
   for(let xx=box.minX;xx<box.maxX;xx+=32)outer.push([xx,box.minZ]);for(let zz=box.minZ;zz<box.maxZ;zz+=32)outer.push([box.maxX,zz]);for(let xx=box.maxX;xx>box.minX;xx-=32)outer.push([xx,box.maxZ]);for(let zz=box.maxZ;zz>box.minZ;zz-=32)outer.push([box.minX,zz]);outer.push(outer[0].slice());
   const seamVertices=[],seamFaces=[];
   for(const triangle of v018Triangulate([outer,inner])){const points=triangle.map(a=>{const h=v047Height(bank,a[0],a[1]).height;return h===null?null:[a[0],h-.06,a[1]];});if(points.every(Boolean)){const n=seamVertices.length;seamVertices.push(...points);seamFaces.push([n,n+2,n+1]);}if(seamFaces.length%128===0)await job.work.checkpoint(128);}
   const common={mesh:'terrain',pos:[x,0,z],scale:[1,1,1],color:[.30,.33,.25],v046Terrain:true,v046Bounds:box,revision:0,sourceResource:M.resource,sourceSpacingMeters:[.5,.5],sourceScope:'Vrais centres natifs LiDAR HD 0,5 m dans un carré local de 255 m ; LOD et raccord au-delà, sans triangles sur NoData',v050LandMask:box,v050LandMaskId:key,v054NativeTerrain:true};
   patch={box,draws:[{...common,vertices,faces,v050FineTerrain:true,v047GeometryId:key},{...common,vertices:seamVertices,faces:seamFaces,v050TerrainSeam:true,v047GeometryId:key+':seam'}]};R.meshes.set(key,patch);
  }
  const out=[];for(const draw of coarse){const faces=draw.faces.filter(f=>{const a=f.map(i=>draw.vertices[i]),xx=(a[0][0]+a[1][0]+a[2][0])/3,zz=(a[0][2]+a[1][2]+a[2][2])/3;return xx<=patch.box.minX||xx>=patch.box.maxX||zz<=patch.box.minZ||zz>=patch.box.maxZ;});if(faces.length===draw.faces.length)out.push(draw);else if(faces.length)out.push({...draw,faces,revision:(draw.revision||0)+1,v047GeometryId:draw.v047GeometryId+':cut:'+key});await job.work.checkpoint(draw.faces.length);}out.push(...patch.draws);return out;
 };
 function info(){const active=[...(V046.terrain?.grids?.values()||[])].filter(g=>g.v054Native),draws=(world?.staticDraws||[]).filter(d=>d.v054NativeTerrain);return{present:!!R.index,sourceTiles:R.index?.sourceTiles||0,availableChunks:R.index?.tiles.length||0,coverageSquareMeters:R.index?.coverageSquareMeters||0,nativeSpacingMeters:.5,resampled:false,activeChunks:active.map(g=>({id:g.id,origin:g.origin.slice(),width:g.width,height:g.height,bytes:g.data.byteLength,noDataPoints:g.noDataPoints})),activeBytes:active.reduce((n,g)=>n+g.data.byteLength,0),rendered:draws.map(d=>({id:d.v047GeometryId,vertices:d.vertices.length,faces:d.faces.length,native:!!d.v050FineTerrain,seam:!!d.v050TerrainSeam,spacing:d.sourceSpacingMeters})),cache:R.cache.stats(),meshCache:R.meshes.stats(),inflight:R.loads.size,requests:R.requests,errors:R.errors.slice(),scope:'Douze km² centraux, pas toute Marseille ; précision du levé distincte du pas natif et du LOD.'};}
 function meshSamples(){const draws=(world?.staticDraws||[]).filter(d=>d.v054NativeTerrain&&d.v050FineTerrain),g=draws[0];if(!g)return null;const v=g.vertices,w=511,indices=[0,1,w,w+1,Math.floor(v.length/2),v.length-2,v.length-1,v.length-w-1],unique=new Set(draws.map(d=>d.vertices));return{uniqueVertices:[...unique].reduce((n,v)=>n+v.length,0),faces:draws.reduce((n,d)=>n+d.faces.length,0),nativeSpacingMeters:.5,displayOffsetMeters:-.06,samples:indices.map(i=>({index:i,position:v[i].slice(),easting:v[i][0]+V046_ORIGIN[0],northing:V046_ORIGIN[1]-v[i][2]})),bounds:{minE:v[0][0]+V046_ORIGIN[0],maxE:v[w-1][0]+V046_ORIGIN[0],maxN:V046_ORIGIN[1]-v[0][2],minN:V046_ORIGIN[1]-v[v.length-1][2]}};}
 function roadInfo(id=null){
  const roads=(world?.staticDraws||[]).filter(d=>d.sourceProfile?.surfaceNativeRefinement),selected=id?roads.find(d=>d.geoFeatureId===id||d.id===id||d.geoFeatureId?.endsWith(':'+id)):null;
  const summary=d=>({id:d.geoFeatureId||d.id||null,geometry:d.v046GeometryId,vertices:d.vertices.length,faces:d.faces.length,revision:d.revision,refinement:{...d.sourceProfile.surfaceNativeRefinement}});
  const result={roads:roads.length,inputFaces:roads.reduce((n,d)=>n+d.sourceProfile.surfaceNativeRefinement.inputFaces,0),outputFaces:roads.reduce((n,d)=>n+d.faces.length,0),budgetLimitedFaces:roads.reduce((n,d)=>n+d.sourceProfile.surfaceNativeRefinement.budgetLimitedFaces,0),resolutionLimitedFaces:roads.reduce((n,d)=>n+d.sourceProfile.surfaceNativeRefinement.resolutionLimitedFaces,0),summaries:roads.slice(0,12).map(summary),selected:null};
  if(selected){const bank=world.v047TerrainBank||V046.terrain,read=(x,z)=>bank.read(...v015GeoUnproject(world.id,x,z)),old=MistralIntegrity.roadMesh(selected.roadPath.map(p=>p.slice(0,2)),selected.roadProperties,(x,z)=>read(x,z).height);
   const evaluate=mesh=>{let maximum=0,missing=0;for(const face of mesh.faces){const p=face.map(i=>mesh.vertices[i]),x=(p[0][0]+p[1][0]+p[2][0])/3,z=(p[0][2]+p[1][2]+p[2][2])/3,r=read(x,z);if(r.height===null){missing++;continue;}maximum=Math.max(maximum,Math.abs(r.height+.085-(p[0][1]+p[1][1]+p[2][1])/3));}return{faces:mesh.faces.length,maxCentroidErrorMeters:maximum,missingCentroids:missing};};
   result.selected={...summary(selected),roadPath:selected.roadPath.map(p=>p.slice()),sourceGeometry:selected.sourceGeometry,sourceProvenance:selected.sourceProvenance,sourceProfile:{...selected.sourceProfile},before:evaluate(old),after:evaluate(selected),samples:Array.from({length:Math.min(24,selected.vertices.length)},(_,i)=>{const index=Math.floor(i*(selected.vertices.length-1)/Math.max(1,Math.min(24,selected.vertices.length)-1)),position=selected.vertices[index].slice();return{index,position,terrain:read(position[0],position[2]),easting:position[0]+V046_ORIGIN[0],northing:V046_ORIGIN[1]-position[2]};})};
  }return result;
 }
 function renderedAt(easting,northing){const x=easting-V046_ORIGIN[0],z=V046_ORIGIN[1]-northing,out=[];for(const d of world?.staticDraws||[]){if(!d.v046Terrain||!d.vertices||!d.faces)continue;const b=d.v046Bounds;if(b&&(x<b.minX||x>b.maxX||z<b.minZ||z>b.maxZ))continue;for(const face of d.faces){const t=face.map(i=>d.vertices[i]);if(x<Math.min(...t.map(p=>p[0]))||x>Math.max(...t.map(p=>p[0]))||z<Math.min(...t.map(p=>p[2]))||z>Math.max(...t.map(p=>p[2])))continue;const cross=(a,b)=>(b[0]-a[0])*(z-a[2])-(b[2]-a[2])*(x-a[0]),signs=[cross(t[0],t[1]),cross(t[1],t[2]),cross(t[2],t[0])];if(signs.every(n=>n>=-1e-8)||signs.every(n=>n<=1e-8)){out.push({id:d.v047GeometryId,native:!!d.v054NativeTerrain,seam:!!d.v050TerrainSeam,triangle:t.map(p=>p.slice()),sourceResource:d.sourceResource||null});break;}}if(out.length>=8)break;}return out;}
 const panel=v047Panel;v047Panel=function(c){panel(c);const s=info(),section=document.createElement('section');section.className='v047-box';section.innerHTML='<h3>MNT LIDAR HD NATIF</h3><p>'+ (s.present?'12 km² centraux disponibles au pas natif de 0,5 m ; '+s.activeChunks.length+' morceaux réellement chargés.':'Atlas précis local absent ou en cours de vérification ; les autres reliefs restent distincts.')+'</p><p>Valeurs Float32 dans le repère Lambert-93 / IGN69, sans rééchantillonnage des altitudes. Le rendu emploie les vrais centres de pixels dans un carré local de 255 m, puis un raccord et un niveau de détail plus large. Une absence LiDAR ne devient pas une mesure inventée.</p><p>Cette couverture partielle ne certifie ni précision absolue de 50 cm, ni relief complet de la commune.</p>';c.querySelector('.v047-integrity')?.appendChild(section);};
 globalThis.v054PreciseTerrainAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v054PreciseTerrainInfo:info,v054PreciseTerrainReady:ready,v054PreciseTerrainSample:(lat,lon)=>V046.terrain.read(lat,lon),v054PreciseTerrainMeshSamples:meshSamples,v054PreciseTerrainRenderedAt:renderedAt,v055NativeRoadInfo:roadInfo});if(['http:','https:'].includes(location.protocol))ready().catch(error);};
}
