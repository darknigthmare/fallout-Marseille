const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),M=require(path.join(root,'src/v046/00_integrity.js')),Stream=require(path.join(root,'src/v047/00_stream_primitives.js'));
const BOX=[43.1696313,5.22875102,43.39105653,5.53254336],Q=[43.29,5.35,43.30,5.36],REGION='geo_marseille_commune';
const PROOF={source:'Explicit synthetic city survey fixture',resource:'ign-bdtopo',license:'CC0 fixture',attribution:'Synthetic test only',acquiredAt:'2026-10-23',verticalDatum:'NGF-IGN69',inputSha256:'a'.repeat(64)};
function descriptor(raw,prefix,bbox){const data=JSON.stringify(raw),sha256=crypto.createHash('sha256').update(data).digest('hex');return{descriptor:{path:'data/map_pack/city/'+prefix+'-'+sha256.slice(0,16)+'.json',bytes:Buffer.byteLength(data),sha256,bbox},data};}
function files(options={}){
 const coverage={bbox:Q,crs:'EPSG:4326',complete:true,layer:'BDTOPO_V3:batiment',returned:1};
 const building={type:'Feature',id:'fixture-building',properties:{kind:'building',sourceId:'fixture-building',height:10,provenance:{...PROOF,coverage}},geometry:{type:'Polygon',coordinates:[[[5.352,43.292],[5.358,43.292],[5.358,43.298],[5.352,43.298],[5.352,43.292]]]}};
 const raw={schemaVersion:1,region:REGION,queryBbox:Q,features:options.empty?[]:[building],source:PROOF,coverages:[{...coverage,returned:options.empty?0:1},{...coverage,returned:0,layer:'BDTOPO_V3:troncon_de_route'}]},chunk=descriptor(raw,'m13055-r00-c00',Q);
 Object.assign(chunk.descriptor,{id:'m13055-r00-c00',region:REGION,queryBbox:Q,coverages:raw.coverages,counts:{buildings:options.empty?0:1,roads:0}});
 const base=descriptor({macro:REGION,width:2,height:2,bbox:BOX,values:[10,10,10,10],rowOrder:'north-to-south',sourceResource:'ign_rge_alti_wld',provenance:PROOF,verticalDatum:'NGF-IGN69'},'terrain',BOX);
 const data={'data/map_pack/city/index.json':JSON.stringify({schemaVersion:1,crs:'EPSG:4326',region:REGION,municipality:{code:'13055',name:'Marseille',bbox:BOX},coverage:{complete:true,uniqueBuildings:options.empty?0:1,uniqueRoads:0},tiles:[chunk.descriptor]}),'data/map_pack/city/terrain-index.json':JSON.stringify({schemaVersion:1,region:REGION,bbox:BOX,base:base.descriptor,tiles:[]}),[chunk.descriptor.path]:chunk.data,[base.descriptor.path]:base.data};
 return{data,chunk,base};
}
function sandbox(data={}){
 const integrity={...M,TerrainBank:class extends M.TerrainBank{}},context=vm.createContext({console,Map,Set,AbortController,setTimeout,clearTimeout,TextDecoder,Uint8Array,crypto:crypto.webcrypto,
  MistralIntegrity:integrity,MistralStream:Stream,V015_GEO_MACROS:{geo_huveaune:{bbox:[43.245,5.43,43.335,5.64]}},V046_BOUNDS:{geo_huveaune:[43.245,5.43,43.335,5.64]},V046:{lab:false,busy:false,terrain:new integrity.TerrainBank({}),gate:{cache:new Map()}},V047:{pending:null,records:new Map(),meshes:new Map()},
  v046Resource:async()=>({source:'cadastre',z:16,x:0,y:0,layers:{},origin:'synthetic original'}),v047BankStamp:()=>'',window:{__MISTRAL_DEBUG:{}},
  v015GeoProject:(_id,lat,lon)=>[lon*1000,0,-lat*1000],v017TileBounds:()=>({south:Q[0],west:Q[1],north:Q[2],east:Q[3]}),v017LonLatToTile:()=>({x:0,y:0}),v046TileKey:(s,z,x,y)=>[s,z,x,y].join(':'),v037TileAllowed:()=>false,
  v046Plan:()=>({box:Q,keys:[],dem:[],p:[5355,0,-43295],lat:43.295,lon:5.355}),v017ClassRoad:()=>({width:2,color:[.3,.3,.3],kind:'road'}),v046Ensure:async()=>true,v046Cancel:()=>true,v046Loading:()=>{},world:{},state:{},mode:'PLAYING',zoneTransitioning:false,
  v017PolyBounds:rings=>{let minX=Infinity,minZ=Infinity,maxX=-Infinity,maxZ=-Infinity;for(const ring of rings)for(const p of ring){minX=Math.min(minX,p[0]);maxX=Math.max(maxX,p[0]);minZ=Math.min(minZ,p[1]);maxZ=Math.max(maxZ,p[1]);}return{minX,maxX,minZ,maxZ,cx:(minX+maxX)/2,cz:(minZ+maxZ)/2};},
  v017FeatureWorldPaths:(_layer,f)=>f.paths,v018PolygonGroups:paths=>[paths],fetch:async url=>{const raw=data[url];return{status:raw?200:404,ok:!!raw,arrayBuffer:async()=>new TextEncoder().encode(raw).buffer};}
 });
 vm.runInContext('globalThis.ensureCalls=0;v046Ensure=async function(){ensureCalls++;return true;};v046StartLab=async function(){V046.lab=true;return true;};v047LeaveLab=function(){V046.lab=false;return true;};',context);
 vm.runInContext(fs.readFileSync(path.join(root,'src/v050/04_source_geometry.js'),'utf8'),context);
 vm.runInContext(fs.readFileSync(path.join(root,'src/v050/04a_city_sources.js'),'utf8'),context);return context;
}
const run=(c,code)=>vm.runInContext(code,c),plain=value=>JSON.parse(JSON.stringify(value));
test('Missing optional city atlas leaves the base map and old bounds unchanged',async()=>{
 const c=sandbox();assert.equal(await run(c,'v051CityReady()'),null);assert.equal(await run(c,'v046Ensure(43.295,5.355)'),true);assert.equal(run(c,'V046_BOUNDS.geo_marseille_commune'),undefined);assert.deepEqual(plain(run(c,'v046Plan().dem')),[]);
});
test('A complete city registers its extent without mutating the active terrain bank',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');assert.deepEqual(plain(run(c,'V046_BOUNDS.geo_marseille_commune')),BOX);assert.deepEqual(Object.keys(c.V046.terrain.bounds),[]);const info=plain(run(c,'v051CityInfo()'));assert.equal(info.sourceBuildings,1);assert.equal(info.registered,true);assert.equal(info.terrainIndexPresent,true);
});
test('A partial atlas never registers a city extent or starts a source-only scene',async()=>{
 const f=files();const index=JSON.parse(f.data['data/map_pack/city/index.json']);index.coverage.complete=false;f.data['data/map_pack/city/index.json']=JSON.stringify(index);const c=sandbox(f.data);await assert.rejects(run(c,'v051CityReady()'),/incomplet/);assert.equal(run(c,'V046_BOUNDS.geo_marseille_commune'),undefined);assert.equal(await run(c,'v046Ensure(43.295,5.355)'),false);assert.equal(c.mode,'LOADING');assert.match(c.V046.error[0].message,/incomplet/);
});
test('City resources outside the old tile pack come only from verified source partitions',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');const plan=plain(run(c,'v046Plan(43.295,5.355)'));assert.ok(plan.dem.includes('dem:'+REGION));assert.deepEqual(plan.keys,['base:14:0:0','cadastre:16:0:0']);const r=await run(c,"v046Resource('cadastre:16:0:0')");assert.equal(r.v051CityOnly,true);assert.equal(r.empty,false);assert.equal(r.layers.building.features.length,1);assert.equal(r.layers.building.features[0].sourceId,'fixture-building');assert.equal(run(c,'V046.terrain.grids.size'),0);
});
test('Corrupt partition bytes reject before any feature is published or cached',async()=>{
 const f=files();f.data[f.chunk.descriptor.path]=f.chunk.data.replace('height":10','height":11');const c=sandbox(f.data);await run(c,'v051CityReady()');await assert.rejects(run(c,"v046Resource('cadastre:16:0:0')"),/SHA-256/);assert.equal(run(c,'V051_CITY.cache.size'),0);assert.equal(run(c,'V051_CITY.loads.size'),0);
});
test('An explicit empty road query removes old road strokes only within its receipt',async()=>{
 const f=files({empty:true}),c=sandbox(f.data);await run(c,'v051CityReady()');c.resource={source:'base',z:14,x:0,y:0,layers:{transportation:{features:[{id:'old',type:2,props:{},paths:[[[5340,-43295],[5370,-43295]]]}]}}};const result=await run(c,'v051CityEnrich(resource)');assert.equal(result.layers.transportation.features.length,1);assert.equal(result.layers.transportation.features[0].v050Paths.length,2);assert.ok(result.layers.transportation.features.every(f=>f.v050Paths.every(p=>p.every(q=>q[0]<=5350||q[0]>=5360))));assert.equal(c.resource.layers.transportation.features[0].paths.length,1);
});
test('Concurrent map workers share one immutable chunk request and release settled promises',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');let chunkReads=0;const fetch=c.fetch;c.fetch=async url=>{if(url===f.chunk.descriptor.path){chunkReads++;await new Promise(r=>setTimeout(r,10));}return fetch(url);};const [a,b]=await Promise.all([run(c,'v051CityChunk(V051_CITY.index.tiles[0])'),run(c,'v051CityChunk(V051_CITY.index.tiles[0])')]);assert.equal(a,b);assert.equal(chunkReads,1);assert.equal(run(c,'V051_CITY.loads.size'),0);assert.equal(run(c,'V051_CITY.cache.size'),1);
});
test('An aborted waiter cannot publish while another map worker can reuse the completed chunk',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');let release;const fetch=c.fetch;c.fetch=url=>url===f.chunk.descriptor.path?new Promise(resolve=>{release=()=>fetch(url).then(resolve);}):fetch(url);c.controller=new AbortController();const aborted=run(c,'v051CityChunk(V051_CITY.index.tiles[0],controller.signal)');const shared=run(c,'v051CityChunk(V051_CITY.index.tiles[0])');c.controller.abort();await assert.rejects(aborted,/annulé/);assert.equal(run(c,'V046.terrain.grids.size'),0);release();assert.equal((await shared).projected.length,1);assert.equal(run(c,'V051_CITY.loads.size'),0);
});
test('Byte budget eviction releases cached partitions and does not retain hidden resolved promises',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');run(c,'V051_CITY.cache.maxBytes=1');const result=await run(c,'v051CityChunk(V051_CITY.index.tiles[0])');assert.equal(result.projected.length,1);assert.equal(run(c,'V051_CITY.cache.size'),0);assert.equal(run(c,'V051_CITY.cache.bytes'),0);assert.equal(run(c,'V051_CITY.loads.size'),0);
});
test('Refreshing while a chunk is in flight refuses its late response',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');let release;const fetch=c.fetch;c.fetch=url=>url===f.chunk.descriptor.path?new Promise(resolve=>{release=()=>fetch(url).then(resolve);}):fetch(url);const old=run(c,'v051CityChunk(V051_CITY.index.tiles[0])');assert.equal(run(c,'v051CityRefresh()'),true);release();await assert.rejects(old,/périmée/);assert.equal(run(c,'V051_CITY.cache.size'),0);
});
test('Synthetic laboratory ignores city resources and restores the exact prior real extent',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');await run(c,'v046StartLab()');assert.equal(run(c,'V046_BOUNDS.geo_marseille_commune'),undefined);assert.deepEqual(plain(run(c,'v046Plan().dem')),[]);assert.equal(run(c,'v047LeaveLab()'),true);assert.deepEqual(plain(run(c,'V046_BOUNDS.geo_marseille_commune')),BOX);
});
test('The verified coarse city DEM stages with its own datum and never mutates the live bank',async()=>{
 const f=files(),c=sandbox(f.data);await run(c,'v051CityReady()');const source=await run(c,"v046Resource('dem:geo_marseille_commune')");c.source=source;const h=run(c,'(()=>{const stage=new MistralIntegrity.TerrainBank(V046_BOUNDS);stage.add(source.raw,source.id);return stage.read(43.295,5.355);})()');assert.equal(h.height,10);assert.equal(h.verticalDatum,'NGF-IGN69');assert.equal(run(c,'V046.terrain.grids.size'),0);
});
test('A city base DEM requires explicit provenance and a compatible normal-height datum',()=>{
 const raw={macro:REGION,width:2,height:2,bbox:BOX,values:[1,2,3,4],sourceResource:'ign_rge_alti_wld'};assert.throws(()=>M.terrain(raw,REGION),/Provenance/);assert.throws(()=>M.terrain({...raw,provenance:{...PROOF,verticalDatum:'WGS84 ellipsoidal'}},REGION),/Référentiel/);assert.equal(M.terrain({...raw,provenance:PROOF},REGION).sourceResource,'ign_rge_alti_wld');
});
test('A vector-only city installation leaves old source enrichment usable until terrain is present',async()=>{
 const f=files();delete f.data['data/map_pack/city/terrain-index.json'];const c=sandbox(f.data);await run(c,'v051CityReady()');assert.equal(run(c,'V051_CITY.registered'),false);c.resource={source:'cadastre',z:16,x:0,y:0,layers:{}};assert.equal(await run(c,'v051CityEnrich(resource)'),c.resource);
});
test('A cancelled navigation never starts later when its optional index finishes loading',async()=>{
 const f=files(),c=sandbox(f.data);let release;const fetch=c.fetch;c.fetch=url=>url==='data/map_pack/city/index.json'?new Promise(resolve=>{release=()=>fetch(url).then(resolve);}):fetch(url);const pending=run(c,'v046Ensure(43.295,5.355)');run(c,'v046Cancel()');release();assert.equal(await pending,false);assert.equal(run(c,'ensureCalls'),0);
});
test('Refreshing during index readiness invalidates the earlier navigation without overwriting its successful replacement',async()=>{
 const f=files(),c=sandbox(f.data),read=c.fetch;let release,first=true;
 c.fetch=url=>url==='data/map_pack/city/index.json'&&first?(first=false,new Promise(resolve=>{release=()=>read(url).then(resolve);})):read(url);
 const old=run(c,'v046Ensure(43.295,5.355)');assert.equal(run(c,'v051CityRefresh()'),true);
 assert.equal(await run(c,'v046Ensure(43.295,5.355)'),true);assert.equal(run(c,'ensureCalls'),1);release();
 assert.equal(await old,false);assert.equal(c.mode,'PLAYING');assert.equal(c.V046.busy,false);assert.deepEqual(plain(run(c,'V051_CITY.errors')),[]);
 assert.equal(run(c,'V051_CITY.registered'),true);assert.equal(run(c,'V051_CITY.index.tiles.length'),1);
});
test('A background boot index superseded by refresh cannot append a stale error to the healthy replacement',async()=>{
 const f=files(),c=sandbox(f.data),read=c.fetch;let release,first=true;
 c.fetch=url=>url==='data/map_pack/city/index.json'&&first?(first=false,new Promise(resolve=>{release=()=>read(url).then(resolve);})):read(url);
 run(c,'v051CityAfterInit()');const old=run(c,'V051_CITY.indexPromise').catch(error=>error);assert.equal(run(c,'v051CityRefresh()'),true);
 await run(c,'v051CityReady()');release();assert.match((await old).message,/périmé/);await new Promise(resolve=>setImmediate(resolve));
 assert.equal(run(c,'V051_CITY.registered'),true);assert.deepEqual(plain(run(c,'V051_CITY.errors')),[]);
});
test('Rendered partition bounds exclude distant whole-road tails while keeping the raw descriptor intact',async()=>{
 const f=files(),index=JSON.parse(f.data['data/map_pack/city/index.json']);index.tiles[0].bbox=[43.2,5.2,43.4,5.6];index.tiles[0].renderBbox=Q;f.data['data/map_pack/city/index.json']=JSON.stringify(index);const c=sandbox(f.data);await run(c,'v051CityReady()');assert.equal(run(c,'v051CityDescriptors([43.21,5.21,43.22,5.22]).length'),0);assert.equal(run(c,'v051CityDescriptors([43.293,5.353,43.294,5.354]).length'),1);assert.deepEqual(plain(run(c,'V051_CITY.index.tiles[0].bbox')),[43.2,5.2,43.4,5.6]);assert.equal(run(c,'V051_CITY.requests'),0);
});
test('Twenty streamed city terrain windows never accumulate in a staged bank or alter the published bank before commit',()=>{
 const c=sandbox(),baseId='geo_huveaune',aubagne='enrichment:geo_huveaune:aaaaaaaaaaaaaaaa';
 const grid=(id,height)=>({macro:id,width:2,height:2,bbox:BOX,values:[height,height,height,height],sourceResource:'ign_rge_alti_wld',provenance:PROOF,verticalDatum:'NGF-IGN69'});
 c.active=new c.MistralIntegrity.TerrainBank({[baseId]:BOX});c.active.add(grid(baseId,10),baseId);c.active.add(grid(aubagne,20),aubagne);
 for(let i=0;i<20;i++){
  const old=c.active,oldKeys=[...old.grids.keys()],newId='enrichment:'+REGION+':'+i.toString(16).padStart(16,'0');
  c.stage=run(c,'v051CityStageBank({geo_huveaune:active.bounds.geo_huveaune},active)');c.stage.add(grid(newId,30+i),newId);
  assert.equal(c.stage.grids.size,3);assert.ok(c.stage.grids.has(baseId)&&c.stage.grids.has(aubagne));assert.deepEqual([...old.grids.keys()],oldKeys);assert.equal(old.grids.has(newId),false);
  c.active=c.stage;
 }
 const outside=run(c,'v051CityStageBank({geo_huveaune:active.bounds.geo_huveaune},active)');assert.equal(outside.grids.size,2);assert.equal(c.active.grids.size,3);
});
