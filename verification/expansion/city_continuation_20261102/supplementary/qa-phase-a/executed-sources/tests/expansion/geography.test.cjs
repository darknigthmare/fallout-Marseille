const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const M = require(path.join(root, 'src/v046/00_integrity.js'));
const proof = {source:'Measured survey fixture',license:'CC0',attribution:'Test survey',acquiredAt:'2026-10-23',verticalDatum:'NGF-IGN69'};
const grid = (id, bbox, values, width=2, height=2) => ({macro:id,bbox,values,width,height,rowOrder:'north-to-south',sourceResource:'ign_rge_alti_wld'});

test('Metres reject prefix garbage and convert explicit centimetres / feet', () => {
  assert.equal(M.metres('6,5 m'), 6.5);
  assert.equal(M.metres('120cm'), 1.2);
  assert.ok(Math.abs(M.metres('12\' 6"')-3.81)<1e-12);
  assert.equal(M.metres('12 unknown'), null);
  assert.equal(M.metres('12;40'), null);
});
test('Building lower floor is subtracted from total height, never added above it', () => {
  const b=M.buildingProfile({height:'18 m',min_height:'6m','roof:height':'3 m','roof:shape':'gabled','roof:direction':90});
  assert.equal(b.height,12);assert.equal(b.eavesHeight,9);assert.equal(b.estimated,false);
  assert.equal(b.minHeight+b.height,18);
});
test('IGN absolute building elevations retain the measured ground datum', () => {
  const b=M.buildingProfile({z_min_sol:143.2,z_max_toit:160.7});
  assert.equal(b.groundElevation,143.2);assert.equal(b.totalHeight,17.5);assert.equal(b.estimated,false);
  assert.equal(b.groundElevation+b.totalHeight,160.7);
});
test('Live GeoPF building schema preserves roof/ground envelope separately from reported hauteur', () => {
  // Sanitised property values from the official extract, not a generated survey.
  const b=M.buildingProfile({hauteur:3.1,altitude_minimale_sol:104.6,altitude_maximale_sol:106,altitude_minimale_toit:107.7,altitude_maximale_toit:108.1,nombre_d_etages:1,precision_planimetrique:5,precision_altimetrique:1});
  assert.equal(b.groundElevation,104.6);assert.equal(b.groundMaximum,106);
  assert.equal(b.roofMinimum,107.7);assert.equal(b.roofElevation,108.1);
  assert.equal(b.groundElevation+b.totalHeight,108.1);assert.equal(b.reportedHeight,3.1);
  assert.equal(b.estimated,false);assert.equal(b.roofEstimated,true);
  assert.equal(b.planimetricAccuracy,5);assert.equal(b.altimetricAccuracy,1);
  assert.match(b.basis,/altitude_maximale_toit/);
});
test('Live Pas de Z building fields never turn unknown roof or precision into measurements', () => {
  const b=M.buildingProfile({hauteur:null,altitude_minimale_sol:107,altitude_maximale_toit:null,precision_altimetrique:9999,methode_d_acquisition_altimetrique:'Pas de Z'});
  assert.equal(b.groundElevation,107);assert.equal(b.reportedHeight,null);
  assert.equal(b.estimated,true);assert.equal(b.roofEstimated,true);assert.equal(b.altimetricAccuracy,null);
});
test('Level-derived building dimensions stay explicitly estimated', () => {
  const b=M.buildingProfile({'building:levels':4,'building:min_level':1});
  assert.equal(b.height,9);assert.equal(b.minHeight,3);assert.equal(b.estimated,true);
});
test('Road widths accept source units and IGN width attributes', () => {
  assert.equal(M.roadProfile({width:'7,25 m'}).width,7.25);
  assert.equal(M.roadProfile({largeur_de_chaussee:6}).width,6);
  assert.equal(M.roadProfile({largeur_chaussee:4.2}).widthAssumed,false);
  assert.equal(M.roadProfile({lanes:2}).widthAssumed,true);
});
test('A bridge with measured deck altitude does not acquire a made-up layer offset', () => {
  const mesh=M.roadMesh([[0,0],[20,0]],{width:6,bridge:'yes',layer:4,ele:52.5},()=>10);
  assert.equal(mesh.elevationAssumed,false);assert.equal(mesh.offset,0);
  assert.ok(mesh.vertices.every(v=>Math.abs(v[1]-52.585)<1e-10));
  assert.equal(Math.abs(mesh.vertices[0][2]-mesh.vertices[1][2]),6);
});
test('Source route Z values interpolate the actual deck independently of terrain', () => {
  const mesh=M.roadMesh([[0,0,30],[24,0,34]],{width:8,bridge:true},()=>1);
  assert.equal(mesh.heightBasis,'coordonnées Z source');assert.equal(mesh.elevationAssumed,false);
  assert.deepEqual(mesh.vertices.map(v=>v[1]),[30.085,30.085,32.085,32.085,34.085,34.085]);
});
test('Live GeoPF road schema retains measured width and absolute source Z at grade', () => {
  const mesh=M.roadMesh([[0,0,108.1],[20,0,107.9]],{largeur_de_chaussee:3,nombre_de_voies:1,position_par_rapport_au_sol:'0',precision_planimetrique:2.5,precision_altimetrique:1.5},()=>0);
  assert.equal(mesh.width,3);assert.equal(mesh.widthAssumed,false);assert.equal(mesh.bridge,false);
  assert.equal(mesh.heightBasis,'coordonnées Z source');assert.equal(mesh.sourcePosition,'0');
  assert.ok(Math.abs(mesh.vertices[0][1]-108.185)<1e-10);assert.ok(Math.abs(mesh.vertices.at(-1)[1]-107.985)<1e-10);
  assert.equal(mesh.planimetricAccuracy,2.5);assert.equal(mesh.altimetricAccuracy,1.5);
});
test('Partially missing route Z is explicitly mixed with terrain, never a fully measured deck', () => {
  const mesh=M.roadMesh([[0,0,108.1],[20,0]],{largeur_de_chaussee:3,bridge:'yes'},()=>105);
  assert.equal(mesh.elevationAssumed,true);assert.equal(mesh.heightBasis,'coordonnées Z partielles et terrain');
});
test('IGN ordinal position is not converted into metres and unknown elevated height stays absent', () => {
  const props={position_par_rapport_au_sol:'2',provenance:{resource:'ign-bdtopo'},largeur_de_chaussee:6};
  const unknown=M.roadMesh([[0,0],[20,0]],props,()=>100);
  assert.equal(unknown.bridge,true);assert.equal(unknown.ordinalPosition,2);assert.equal(unknown.offset,0);
  assert.equal(unknown.unavailableElevation,true);assert.equal(unknown.faces.length,0);
  const known=M.roadMesh([[0,0,113],[20,0,114]],props,()=>100);
  assert.equal(known.elevationAssumed,false);assert.equal(known.unavailableElevation,false);
  assert.equal(M.roadProfile({position_par_rapport_au_sol:'-1'}).tunnel,true);
});
test('A draped route does not construct a face across absent terrain', () => {
  const mesh=M.roadMesh([[0,0],[24,0]],{width:6},x=>x>=10&&x<=14?null:15);
  assert.equal(mesh.faces.length,0);
  assert.ok(mesh.vertices.every(v=>v.every(Number.isFinite)));
});
test('NoData with positive interpolation weight remains missing', () => {
  const t=M.terrain(grid('a',[0,0,1,1],[10,20,null,40]),'a');
  assert.equal(M.sample(t,.5,.5),null);
  assert.equal(M.sample(t,1,0),10);
  assert.equal(M.sample(t,0,1),40);
});
test('Incompatible or missing vertical references require explicit transformation before layering', () => {
  assert.equal(M.compatibleDatum('NGF-IGN69 — altitude normale, France continentale'),true);
  assert.equal(M.compatibleDatum('EPSG:5720'),true);assert.equal(M.compatibleDatum('NGF / IGN 1969'),true);
  assert.equal(M.compatibleDatum('EGM2008'),false);assert.equal(M.compatibleDatum('WGS84 ellipsoidal (not NGF-IGN69)'),false);
  assert.throws(()=>M.terrain({...grid('enrichment:a',[0,0,1,1],[1,2,3,4]),sourceResource:'survey',verticalDatum:'EGM2008',provenance:proof},'enrichment:a'),/conversion explicite/);
});
test('Highest-resolution covering source is used without blending away its measurements', () => {
  const b=new M.TerrainBank({a:[0,0,1,1],b:[0,0,1,1]});
  b.add(grid('a',[0,0,1,1],[10,10,10,10]),'a');
  b.add(grid('b',[0,0,1,1],Array(9).fill(25),3,3),'b');
  assert.equal(b.read(.5,.5).height,25);assert.deepEqual(b.read(.5,.5).sources,['b']);
});
test('Measured local terrain overlays keep their own extent and do not mutate macro bounds', () => {
  const bounds={a:[0,0,2,2]},bank=new M.TerrainBank(bounds);
  bank.add(grid('a',bounds.a,[10,10,10,10]),'a');
  bank.add({...grid('enrichment:a',[.5,.5,1.5,1.5],[31,32,33,34]),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'},'enrichment:a');
  assert.equal(bank.read(1,1).height,32.5);assert.ok(Math.abs(bank.read(.2,.2).height-10)<1e-10);
  assert.deepEqual(Object.keys(bounds),['a']);assert.equal(bank.read(1,1).verticalDatum,'NGF-IGN69');
  assert.deepEqual(bank.required([0,0,2,2]),['a']);
  assert.throws(()=>bank.add({...grid('enrichment:b',[0,0,1,1],[1,2,3,4]),sourceResource:'survey'},'enrichment:b'),/Provenance/);
});

function sandbox(files={}) {
  const localM={...M,TerrainBank:class extends M.TerrainBank{}};
  const context=vm.createContext({console,Map,Set,AbortController,setTimeout,clearTimeout,TextDecoder,Uint8Array,crypto:crypto.webcrypto,
    MistralIntegrity:localM,MistralStream:require(path.join(root,'src/v047/00_stream_primitives.js')),V046_BOUNDS:{geo_huveaune:[0,0,2,2]},V046:{lab:false,terrain:new localM.TerrainBank({})},
    v046Resource:async()=>({}),v047BankStamp:()=>'',window:{__MISTRAL_DEBUG:{}},
    v015GeoProject:(_id,lat,lon)=>[lon*1000,0,-lat*1000],
    v017TileBounds:()=>({south:.9,west:.9,north:1.1,east:1.1}),
    v017PolyBounds:rings=>{const p=rings.flat(),xs=p.map(v=>v[0]),zs=p.map(v=>v[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);return{minX,maxX,minZ,maxZ,cx:(minX+maxX)/2,cz:(minZ+maxZ)/2};},
    v017FeatureWorldPaths:(_layer,feature)=>feature.paths,v018PolygonGroups:paths=>[paths],
    fetch:async url=>{const raw=files[url];return{status:raw?200:404,ok:!!raw,arrayBuffer:async()=>new TextEncoder().encode(raw).buffer};}
  });
  vm.runInContext(fs.readFileSync(path.join(root,'src/v050/04_source_geometry.js'),'utf8'),context);
  return context;
}
const building = {type:'Feature',id:'measured-1',properties:{kind:'building',sourceId:'measured-1',height:12,provenance:proof},geometry:{type:'Polygon',coordinates:[[[.98,.98],[1.02,.98],[1.02,1.02],[.98,1.02],[.98,.98]],[[.995,.995],[.995,1.005],[1.005,1.005],[1.005,.995],[.995,.995]]]}};
function measuredFiles(feature=building) {
  const bundle=JSON.stringify({schemaVersion:1,region:'geo_huveaune',source:proof,features:[feature]});
  const digest=crypto.createHash('sha256').update(bundle).digest('hex'),file='data/map_pack/enrichment/geo_huveaune-source.json';
  return{'data/map_pack/enrichment/index.json':JSON.stringify({schemaVersion:1,crs:'EPSG:4326',regions:{geo_huveaune:{path:file,bytes:Buffer.byteLength(bundle),sha256:digest,bbox:[.98,.98,1.02,1.02]}}}),[file]:bundle};
}
test('Imported polygon rings and courtyard topology survive projected source conversion', () => {
  const c=sandbox();c.feature=building;
  const result=vm.runInContext("v050SourceFeature(feature,'geo_huveaune')",c);
  assert.equal(result.v050Groups.length,1);assert.equal(result.v050Groups[0].length,2);
  assert.equal(M.inside(result.v050Groups[0],1000,-1000),false);
  assert.equal(M.inside(result.v050Groups[0],981,-1000),true);
  assert.deepEqual(JSON.parse(JSON.stringify(result.props.provenance)),proof);
});
test('Optional index absence preserves the original map resource', async () => {
  const c=sandbox();c.resource={source:'cadastre',z:16,x:0,y:0,layers:{}};
  const result=await vm.runInContext("v050EnrichResource(resource,'cadastre:16:0:0',null)",c);
  assert.equal(result,c.resource);
});
test('Non-HTTP diagnostic documents do not resolve optional relative source URLs', async () => {
  const c=sandbox();c.location={protocol:'about:'};c.fetch=()=>{throw Error('Relative URL must not be fetched');};c.resource={source:'cadastre',z:16,x:0,y:0,layers:{}};
  assert.equal(await vm.runInContext("v050EnrichResource(resource,'cadastre:16:0:0',null)",c),c.resource);
});
test('Source content length is refused before allocating an oversized body', async () => {
  const c=sandbox();let read=false;c.fetch=async()=>({ok:true,status:200,headers:{get:()=>String(2*1024*1024)},arrayBuffer:async()=>{read=true;return new ArrayBuffer(1);}});
  await assert.rejects(vm.runInContext("v050LocalSourceJSON('fixture',null,true)",c),/hors budget/);assert.equal(read,false);
});
test('Streaming source reads stop at the expected byte budget', async () => {
  const c=sandbox();let calls=0,cancelled=false;
  c.fetch=async()=>({ok:true,status:200,headers:{get:()=>null},body:{getReader:()=>({read:async()=>{calls++;return{done:false,value:new Uint8Array(60)};},cancel:async()=>{cancelled=true;},releaseLock:()=>{}})}});
  await assert.rejects(vm.runInContext("v050LocalSourceJSON('fixture',{bytes:100,sha256:'0'.repeat(64)})",c),/hors budget/);
  assert.equal(calls,2);assert.equal(cancelled,true);
});
test('Verified enrichment is consumed by the runtime without mutating vector resources', async () => {
  const c=sandbox(measuredFiles());
  c.resource={source:'cadastre',z:16,x:0,y:0,layers:{batiments:{extent:4096,features:[{id:'legacy-1',type:3,paths:[[[979,-979],[990,-979],[990,-990],[979,-990],[979,-979]]],props:{}}]}}};
  const before=JSON.stringify(c.resource),result=await vm.runInContext("v050EnrichResource(resource,'cadastre:16:0:0',null)",c);
  assert.equal(JSON.stringify(c.resource),before);
  assert.equal(result.layers.building.features.length,1);
  assert.equal(result.layers.batiments.features.length,0);
  assert.equal(result.layers.building.features[0].props.height,12);
});
test('Coverage clipping interpolates source XY and Z on the original segments exactly', () => {
  const c=sandbox();c.paths=[[[-5,5,100],[5,5,110],[15,5,120]]];c.polygon=[[0,0],[10,0],[10,10],[0,10]];
  const inside=vm.runInContext('v050ClipSourcePaths(paths,polygon,true)',c),outside=vm.runInContext('v050ClipSourcePaths(paths,polygon,false)',c);
  assert.deepEqual(JSON.parse(JSON.stringify(inside)),[[[0,5,105],[5,5,110],[10,5,115]]]);
  assert.deepEqual(JSON.parse(JSON.stringify(outside)),[[[-5,5,100],[0,5,105]],[[10,5,115],[15,5,120]]]);
  c.polygon.reverse();assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('v050ClipSourcePaths(paths,polygon,true)',c))),JSON.parse(JSON.stringify(inside)));
});
test('Clipping keeps parallel outside paths and removes no unqueried source segment', () => {
  const c=sandbox();c.paths=[[[-5,-2,100],[15,-2,120]]];c.polygon=[[0,0],[10,0],[10,10],[0,10]];
  assert.deepEqual(JSON.parse(JSON.stringify(vm.runInContext('v050ClipSourcePaths(paths,polygon,false)',c))),c.paths);
  assert.equal(vm.runInContext('v050ClipSourcePaths(paths,polygon,true).length',c),0);
});
test('Complete WFS query replaces base road strokes only inside its certified query extent', async () => {
  const feature={type:'Feature',id:'official-road',properties:{kind:'road',sourceId:'official-road',width:6,provenance:{...proof,resource:'ign-bdtopo',coverage:{bbox:[.99,.99,1.01,1.01],crs:'EPSG:4326',complete:true,layer:'BDTOPO_V3:troncon_de_route',returned:1}}},geometry:{type:'LineString',coordinates:[[.98,1,100],[1.02,1,120]]}};
  const c=sandbox(measuredFiles(feature));c.resource={source:'base',z:14,x:0,y:0,layers:{transportation:{extent:4096,features:[{id:'old-road',type:2,props:{},paths:[[[980,-1000,90],[1020,-1000,130]]]}]}}};
  const before=JSON.stringify(c.resource),result=await vm.runInContext("v050EnrichResource(resource,'base:14:0:0',null)",c),rows=result.layers.transportation.features;
  assert.equal(JSON.stringify(c.resource),before);assert.equal(rows.length,2);
  const base=rows.find(f=>f.id==='old-road'),source=rows.find(f=>f.v050Source);
  assert.deepEqual(JSON.parse(JSON.stringify(base.v050Paths)),[[[980,-1000,90],[990,-1000,100]],[[1010,-1000,120],[1020,-1000,130]]]);
  assert.deepEqual(JSON.parse(JSON.stringify(source.v050Paths)),[[[990,-1000,105],[1010,-1000,115]]]);
  assert.deepEqual(JSON.parse(JSON.stringify(source.v050Geometry)),feature.geometry);
});
test('A complete-query corner with no source road geometry stays empty instead of retaining old roads', async () => {
  const feature={type:'Feature',id:'official-road',properties:{kind:'road',sourceId:'official-road',provenance:{...proof,resource:'ign-bdtopo',coverage:{bbox:[.99,.99,1.01,1.01],crs:'EPSG:4326',complete:true,layer:'BDTOPO_V3:troncon_de_route',returned:1}}},geometry:{type:'LineString',coordinates:[[.99,.99,100],[1.01,.99,100]]}};
  const c=sandbox(measuredFiles(feature));c.v017TileBounds=()=>({south:.995,west:.995,north:1.005,east:1.005});c.resource={source:'base',z:14,x:0,y:0,layers:{transportation:{extent:4096,features:[{id:'old-road',type:2,props:{},paths:[[[998,-1000],[1002,-1000]]]}]}}};
  const result=await vm.runInContext("v050EnrichResource(resource,'base:14:0:0',null)",c);
  assert.equal(result.layers.transportation.features.length,0);
});
test('An incomplete or unrelated query receipt never authorises coverage deletion', () => {
  const c=sandbox();c.feature={type:'Feature',id:'road',properties:{kind:'road',sourceId:'road',provenance:{...proof,resource:'ign-bdtopo',coverage:{bbox:[.99,.99,1.01,1.01],crs:'EPSG:4326',complete:false,layer:'BDTOPO_V3:troncon_de_route',returned:1}}},geometry:{type:'LineString',coordinates:[[.99,1],[1.01,1]]}};
  assert.throws(()=>vm.runInContext("v050SourceFeature(feature,'geo_huveaune')",c),/couverture/);
});
test('Absolute building attributes and route XYZ cannot silently mix ellipsoidal and NGF heights', () => {
  const c=sandbox();c.feature={type:'Feature',id:'road',properties:{kind:'road',sourceId:'road',provenance:{...proof,verticalDatum:'WGS84 ellipsoidal'}},geometry:{type:'LineString',coordinates:[[.99,1,10],[1.01,1,12]]}};
  assert.throws(()=>vm.runInContext("v050SourceFeature(feature,'geo_huveaune')",c),/conversion explicite/);
  c.feature={...building,properties:{...building.properties,altitude_minimale_sol:100,provenance:{...proof,verticalDatum:'EGM96'}}};
  assert.throws(()=>vm.runInContext("v050SourceFeature(feature,'geo_huveaune')",c),/conversion explicite/);
});
test('Corrupted local source checksum blocks enrichment instead of publishing altered geometry', async () => {
  const files=measuredFiles();files['data/map_pack/enrichment/geo_huveaune-source.json']=files['data/map_pack/enrichment/geo_huveaune-source.json'].replace('height":12','height":13');
  const c=sandbox(files);c.resource={source:'cadastre',z:16,x:0,y:0,layers:{}};
  await assert.rejects(vm.runInContext("v050EnrichResource(resource,'cadastre:16:0:0',null)",c),/SHA-256/);
});
test('Surveyed courtyard removes an old solid footprint while a touching neighbour survives', async () => {
  const c=sandbox(measuredFiles());
  c.resource={source:'cadastre',z:16,x:0,y:0,layers:{batiments:{extent:4096,features:[
    {id:'old-solid',type:3,paths:[[[980,-980],[1020,-980],[1020,-1020],[980,-1020],[980,-980]]],props:{}},
    {id:'neighbour',type:3,paths:[[[1020,-980],[1040,-980],[1040,-1020],[1020,-1020],[1020,-980]]],props:{}}
  ]}}};
  const result=await vm.runInContext("v050EnrichResource(resource,'cadastre:16:0:0',null)",c);
  assert.equal(result.layers.batiments.features.length,1);assert.equal(result.layers.batiments.features[0].id,'neighbour');
  assert.equal(result.layers.building.features[0].v050Groups[0].length,2);
});
test('Changing georeferencing invalidates the terrain geometry cache identity', () => {
  const c=sandbox();c.bank=new M.TerrainBank({a:[0,0,1,1]});c.bank.add(grid('a',[0,0,1,1],[1,2,3,4]),'a');
  const a=vm.runInContext('v047BankStamp(bank)',c);c.bank.grids.get('a').bbox=[0,0,2,2];
  assert.notEqual(vm.runInContext('v047BankStamp(bank)',c),a);
});
test('Different measured absolute building elevations never deduplicate', () => {
  const rings=[[[0,0],[2,0],[2,2],[0,2],[0,0]]];
  assert.notEqual(M.footprintKey('building',rings,{z_min_sol:10,z_max_toit:20}),M.footprintKey('building',rings,{z_min_sol:20,z_max_toit:30}));
});
test('Source gabled roof reaches its measured ridge and preserves a real courtyard', () => {
  const context=vm.createContext({v017SignedArea:ring=>ring.reduce((sum,p,i)=>{const q=ring[(i+1)%ring.length];return sum+p[0]*q[1]-q[0]*p[1];},0)/2});
  const source=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8');
  vm.runInContext(source.slice(0,source.indexOf('function v018MeshData')),context);
  const rings=[[[0,0],[20,0],[20,20],[0,20],[0,0]],[[5,5],[5,15],[15,15],[15,5],[5,5]]];
  const profile=M.buildingProfile({height:12,'roof:height':3,'roof:shape':'gabled','roof:direction':90});
  const mesh=M.roofMesh(rings,profile,100,context.v018Triangulate);
  assert.ok(mesh);assert.equal(Math.max(...mesh.vertices.map(p=>p[1])),112);
  let planArea=0;
  for(const face of mesh.faces){const[a,b,c]=face.map(i=>mesh.vertices[i]),area=Math.abs((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]))/2;planArea+=area;if(area>1e-8)assert.equal(M.inside([rings[1]],(a[0]+b[0]+c[0])/3,(a[2]+b[2]+c[2])/3),false);}
  assert.ok(Math.abs(planArea-300)<1e-7);
});
test('Roof projection bounds handle a large degenerate source without spread stack overflow', () => {
  const ring=Array.from({length:180000},(_,i)=>[0,i]);ring.push(ring[0]);
  const profile=M.buildingProfile({height:8,'roof:height':2,'roof:shape':'gabled','roof:direction':90});
  assert.equal(M.roofMesh([ring],profile,100,()=>{throw Error('A zero-width roof must not be triangulated');}),null);
});
test('Terrain source bundle attaches to the same staged bank as base elevations', () => {
  const c=sandbox();c.overlay={...grid('enrichment:geo_huveaune',[.9,.9,1.1,1.1],[40,40,40,40]),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'};
  vm.runInContext("V050_GEOGRAPHY.bundles.set('geo_huveaune',{terrain:overlay})",c);
  c.raw=grid('geo_huveaune',[0,0,2,2],[10,10,10,10]);
  const result=vm.runInContext("(()=>{const bank=new MistralIntegrity.TerrainBank(V046_BOUNDS);bank.add(raw,'geo_huveaune');return bank.read(1,1);})()",c);
  assert.equal(result.height,40);assert.equal(result.sourceResource,'survey');
});
test('Several source grids coexist and select the finest covering tile without fake DEM fetches', async () => {
  const files=measuredFiles(),file='data/map_pack/enrichment/geo_huveaune-source.json';
  const bundle=JSON.parse(files[file]);bundle.terrainTiles=[
    {...grid('enrichment:geo_huveaune:1111111111111111',[.5,.5,1.5,1.5],[20,20,20,20]),sourceResource:'broad-survey',provenance:proof,verticalDatum:'NGF-IGN69'},
    {...grid('enrichment:geo_huveaune:2222222222222222',[.95,.95,1.05,1.05],[44,44,44,44]),sourceResource:'fine-survey',provenance:proof,verticalDatum:'NGF-IGN69'}
  ];
  files[file]=JSON.stringify(bundle);const index=JSON.parse(files['data/map_pack/enrichment/index.json']);index.regions.geo_huveaune.bytes=Buffer.byteLength(files[file]);index.regions.geo_huveaune.sha256=crypto.createHash('sha256').update(files[file]).digest('hex');files['data/map_pack/enrichment/index.json']=JSON.stringify(index);
  const c=sandbox(files);c.resource={source:'cadastre',z:16,x:0,y:0,layers:{}};
  await vm.runInContext("v050EnrichResource(resource,'dem:geo_huveaune',null)",c);
  c.raw=grid('geo_huveaune',[0,0,2,2],[10,10,10,10]);
  const info=vm.runInContext("(()=>{const b=new MistralIntegrity.TerrainBank(V046_BOUNDS);b.add(raw,'geo_huveaune');return{fine:b.read(1,1),broad:b.read(.8,.8),base:b.read(.1,.1),required:b.required([0,0,2,2]),size:b.grids.size};})()",c);
  assert.equal(info.size,3);assert.equal(info.fine.height,44);assert.ok(Math.abs(info.broad.height-20)<1e-10);assert.equal(info.base.height,10);
  assert.deepEqual(JSON.parse(JSON.stringify(info.required)),['geo_huveaune']);
});
test('Source refresh removes stale overlay grids only in the new staged bank', () => {
  const c=sandbox();c.overlay={...grid('enrichment:geo_huveaune:1111111111111111',[.9,.9,1.1,1.1],[40,40,40,40]),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'};c.raw=grid('geo_huveaune',[0,0,2,2],[10,10,10,10]);
  vm.runInContext("V050_GEOGRAPHY.bundles.set('geo_huveaune',{terrainGrids:[overlay]});globalThis.active=new MistralIntegrity.TerrainBank(V046_BOUNDS);active.add(raw,'geo_huveaune');V050_GEOGRAPHY.bundles.clear();globalThis.staged=new MistralIntegrity.TerrainBank(V046_BOUNDS);for(const[id,g]of active.grids)staged.grids.set(id,g);staged.add(raw,'geo_huveaune');",c);
  assert.equal(vm.runInContext('active.read(1,1).height',c),40);assert.equal(vm.runInContext('staged.read(1,1).height',c),10);
});
test('Synthetic lab terrain does not inherit installed real source tiles', () => {
  const c=sandbox();c.overlay={...grid('enrichment:geo_huveaune',[.9,.9,1.1,1.1],[40,40,40,40]),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'};c.raw=grid('geo_huveaune',[0,0,2,2],[10,10,10,10]);
  vm.runInContext("V050_GEOGRAPHY.bundles.set('geo_huveaune',{terrain:overlay});V046.lab=true;globalThis.bank=new MistralIntegrity.TerrainBank(V046_BOUNDS);bank.add(raw,'geo_huveaune');",c);
  assert.equal(vm.runInContext('bank.read(1,1).height',c),10);assert.equal(vm.runInContext('bank.grids.size',c),1);
});
test('Refreshing a failed source snapshot rejects late responses without erasing the next index', async () => {
  const c=sandbox();c.V047={records:new Map(),meshes:new Map()};let release;
  c.fetch=()=>new Promise(resolve=>{release=resolve;});
  const old=vm.runInContext('v050SourceIndex()',c);
  assert.equal(vm.runInContext('v050RefreshGeography()',c),true);
  const current=JSON.stringify({schemaVersion:1,crs:'EPSG:4326',regions:{}});
  c.fetch=async()=>({ok:true,status:200,arrayBuffer:async()=>new TextEncoder().encode(current).buffer});
  const next=await vm.runInContext('v050SourceIndex()',c);
  release({ok:true,status:200,arrayBuffer:async()=>new TextEncoder().encode(current).buffer});
  await assert.rejects(old,/périmé/);
  assert.equal(await vm.runInContext('v050SourceIndex()',c),next);
});
test('Fine terrain renders actual imported nodes, cuts coarse overlaps, and joins both boundaries', async () => {
  const c=sandbox();c.V047={meshes:new Map()};c.job={work:{checkpoint:async()=>{}}};
  const geometry=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8');
  c.v017SignedArea=ring=>ring.reduce((sum,p,i)=>{const q=ring[(i+1)%ring.length];return sum+p[0]*q[1]-q[0]*p[1];},0)/2;
  vm.runInContext(geometry.slice(0,geometry.indexOf('function v018MeshData')),c);
  c.v015GeoUnproject=(_id,x,z)=>[-z/1000,x/1000];
  c.bank=new c.MistralIntegrity.TerrainBank({geo_huveaune:[0,0,2,2]});
  c.bank.add(grid('geo_huveaune',[0,0,2,2],[50,50,50,50]),'geo_huveaune');
  const values=Array.from({length:25},(_,i)=>100+i);values[12]=null;
  c.bank.add({...grid('enrichment:geo_huveaune',[.99998,.99998,1.00002,1.00002],values,5,5),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'},'enrichment:geo_huveaune');
  c.plan={lat:1,lon:1,p:[1000,0,-1000]};
  const vertices=[],faces=[];for(let j=0;j<=8;j++)for(let i=0;i<=8;i++)vertices.push([896+i*32,49.94,-1120+j*32]);
  for(let j=0;j<8;j++)for(let i=0;i<8;i++){const a=j*9+i,b=a+1,k=a+9,d=k+1;faces.push([a,k,b],[b,k,d]);}
  c.coarse=[{mesh:'terrain',vertices,faces,v047GeometryId:'coarse',v046Terrain:true}];
  const originalFaces=faces.length;
  const out=await vm.runInContext("v050RefineTerrainMeshes(coarse,plan,bank,'stamp',job)",c),fine=out.find(d=>d.v050FineTerrain),seam=out.find(d=>d.v050TerrainSeam),cut=out.find(d=>d.v047GeometryId.startsWith('coarse'));
  assert.ok(fine&&seam&&cut);assert.equal(fine.vertices.length,25);assert.ok(fine.faces.length<32);
  for(let i=0;i<values.length;i++)if(values[i]!==null)assert.equal(fine.vertices[i][1],values[i]-.06);
  assert.ok(!fine.faces.some(face=>face.includes(12)));
  assert.equal(c.coarse[0].faces.length,originalFaces);assert.ok(cut.faces.length<originalFaces);
  assert.ok(seam.faces.length>0);assert.ok(seam.vertices.every(v=>v.every(Number.isFinite)));
  const second=await vm.runInContext("v050RefineTerrainMeshes(coarse,plan,bank,'stamp',job)",c);
  assert.equal(second.find(d=>d.v050FineTerrain),fine);
});
function landSurfaceContext(){
  const c=sandbox();c.MistralStream=require(path.join(root,'src/v047/00_stream_primitives.js'));
  c.v017SignedArea=ring=>ring.reduce((sum,p,i)=>{const q=ring[(i+1)%ring.length];return sum+p[0]*q[1]-q[0]*p[1];},0)/2;
  const geometry=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8');vm.runInContext(geometry.slice(0,geometry.indexOf('function v018MeshData')),c);
  c.job={work:{checkpoint:async()=>{}}};return c;
}
const surfaceArea=triangles=>triangles.reduce((sum,t)=>sum+Math.abs((t[1][0]-t[0][0])*(t[2][2]-t[0][2])-(t[1][2]-t[0][2])*(t[2][0]-t[0][0]))/2,0);
test('A coarse land triangle spanning a real DEM bump and pit is cut only over actual fine faces',async()=>{
  const c=landSurfaceContext(),vertices=[],faces=[];for(let j=0;j<=4;j++)for(let i=0;i<=4;i++)vertices.push([i,i===1&&j===1?20:i===3&&j===3?-8:4,j]);
  for(let j=0;j<4;j++)for(let i=0;i<4;i++){const a=j*5+i;faces.push([a,a+5,a+1],[a+1,a+5,a+6]);}
  c.fine={mesh:'terrain',vertices,faces,color:[.3,.4,.2],v050FineTerrain:true,v046Terrain:true,v047GeometryId:'fine'};
  const triangle=[[-10,10,-10],[-10,10,20],[20,10,-10]],rings=[[[-10,-10],[-10,20],[20,-10],[-10,-10]]];
  c.land={mesh:'geoSurface',vertices:triangle,faces:[[0,1,2]],color:[.6,.5,.4],rings,geoLayer:'landuse',v046GeometryId:'land'};
  c.water={...c.land,geoLayer:'water',v046GeometryId:'water'};c.road={...c.land,geoLayer:'transportation',v046GeometryId:'road'};
  const result=await vm.runInContext('v050RefineLandSurfaces([fine],[land,water,road],job)',c),cut=result.draws.find(d=>d.geoLayer==='landuse');
  assert.ok(cut.v050LandCut);assert.equal(result.draws.find(d=>d.geoLayer==='water'),c.water);assert.equal(result.draws.find(d=>d.geoLayer==='transportation'),c.road);
  const cutTriangles=cut.faces.map(f=>f.map(i=>cut.vertices[i]));assert.ok(Math.abs(surfaceArea(cutTriangles)-(450-16))<1e-8);
  assert.ok(cut.vertices.every(p=>p[1]===10));assert.equal(c.land.faces.length,1);assert.equal(c.land.vertices,triangle);assert.equal(cut.rings,rings);
  for(const face of result.terrain.flatMap(d=>d.faces))for(const index of face)assert.equal(vertices[index][1],c.fine.vertices[index][1]);
  assert.ok(result.terrain.some(d=>d.vertices.some(p=>p[1]===20)));assert.ok(result.terrain.some(d=>d.vertices.some(p=>p[1]===-8)));
  assert.ok(result.terrain.every(d=>d.landColorSampling&&d.vertices===vertices));
});
test('Fine NoData holes remove old covering land planes while the outside coarse geometry stays unchanged',async()=>{
  const c=landSurfaceContext(),vertices=[],faces=[];for(let j=0;j<=4;j++)for(let i=0;i<=4;i++)vertices.push([i,i===2&&j===2?0:5,j]);
  for(let j=0;j<4;j++)for(let i=0;i<4;i++){const a=j*5+i;for(const f of[[a,a+5,a+1],[a+1,a+5,a+6]])if(!f.includes(12))faces.push(f);}
  c.fine={mesh:'terrain',vertices,faces,color:[.2,.3,.1],v050FineTerrain:true,v047GeometryId:'nodata'};
  c.land={mesh:'geoSurface',vertices:[[-10,3,-10],[-10,3,20],[20,3,-10]],faces:[[0,1,2]],color:[.5,.4,.3],rings:[[[-10,-10],[-10,20],[20,-10],[-10,-10]]],geoLayer:'landcover',v046GeometryId:'land'};
  const result=await vm.runInContext('v050RefineLandSurfaces([fine],[land],job)',c),cut=result.draws[0],triangles=cut.faces.map(f=>f.map(i=>cut.vertices[i]));
  assert.ok(Math.abs(surfaceArea(triangles)-(450-16))<1e-8);
  assert.ok(!result.terrain.flatMap(d=>d.faces).some(f=>f.includes(12)));assert.equal(result.terrain.flatMap(d=>d.faces).length,faces.length);
  const support=await vm.runInContext('v050TerrainSupport(fine,job.work)',c);assert.equal(vm.runInContext('v050SurfaceInside',c)(support,[2,2]),true);
  assert.ok(!triangles.some(t=>M.inside([t.map(p=>[p[0],p[2]])],2,2)));assert.ok(cut.vertices.every(p=>p[1]===3));
});
test('Exact support clipping preserves slope at boundary crossings and handles coincident edges',async()=>{
  const c=landSurfaceContext();c.fine={vertices:[[0,0,0],[0,0,2],[2,0,0],[2,0,2]],faces:[[0,1,2],[2,1,3]],v047GeometryId:'square'};
  const support=await vm.runInContext('v050TerrainSupport(fine,job.work)',c),clip=vm.runInContext('v050ClipLandTriangle',c);
  for(const triangle of[[[-2,0,-1],[-2,3,2],[4,6,-1]],[[0,0,0],[0,2,2],[2,4,0]],[[2,2,0],[2,4,2],[4,4,0]],[[1,1,1],[1,1.5,1.5],[1.5,1.5,1]]]){
    const out=clip(triangle,support);assert.ok(out.flat().every(p=>p.every(Number.isFinite)));
    for(const t of out){const p=t.reduce((a,b)=>[a[0]+b[0]/3,a[1]+b[2]/3],[0,0]);assert.equal(vm.runInContext('v050SurfaceInside',c)(support,p),false);}
  }
  const sloped=[[-2,-5,-1],[-2,4,2],[4,7,-1]],out=clip(sloped,support);assert.ok(out.flat().every(p=>Math.abs(p[1]-(2*p[0]+3*p[2]+2))<1e-8));
  assert.equal(clip([[0,0,0],[0,2,2],[2,4,0]],support).length,0);
});
test('Land colours use an indexed centroid sample with holes while preserving every DEM face and altitude',async()=>{
  const c=landSurfaceContext();const vertices=[],faces=[];for(let j=0;j<=8;j++)for(let i=0;i<=8;i++)vertices.push([i,i+j,j]);for(let j=0;j<8;j++)for(let i=0;i<8;i++){const a=j*9+i;faces.push([a,a+9,a+1],[a+1,a+9,a+10]);}
  c.fine={vertices,faces,color:[.1,.2,.3],v050FineTerrain:true,v047GeometryId:'colors'};
  const outer=[[0,0],[0,8],[8,8],[8,0],[0,0]],hole=[[2,2],[6,2],[6,6],[2,6],[2,2]],land={vertices:[[0,0,0],[0,0,8],[8,0,0]],faces:[[0,1,2]],rings:[outer,hole],geoLayer:'landuse',color:[.7,.5,.2],v046GeometryId:'ring'};
  c.land=[land,...Array.from({length:200},(_,i)=>({...land,rings:[outer.map(([x,z])=>[x+1000+i*10,z])],v046GeometryId:'far-'+i}))];
  const result=await vm.runInContext('v050RefineLandSurfaces([fine],land,job)',c);assert.equal(result.terrain.length,2);
  assert.equal(result.terrain.reduce((sum,d)=>sum+d.faces.length,0),faces.length);assert.ok(result.terrain.every(d=>d.vertices===vertices));
  for(const draw of result.terrain)for(const f of draw.faces){const p=f.reduce((a,i)=>[a[0]+vertices[i][0]/3,a[1]+vertices[i][2]/3],[0,0]),expected=M.inside([outer,hole],...p)?land.color:c.fine.color;assert.deepEqual(draw.color,expected);}
  assert.equal(result.terrain[0].landColorPolygons,1);assert.ok(result.terrain[0].landColorCandidateTests<=faces.length);
  assert.equal(c.land[1],result.draws.find(d=>d.v046GeometryId==='far-0'));
  const second=await vm.runInContext('v050RefineLandSurfaces([fine],land,job)',c);assert.equal(second.terrain[0],result.terrain[0]);assert.equal(second.draws[0],result.draws[0]);
});
test('A projected grid uses the exact outer stitch box while its curved DEM nodes remain unchanged',async()=>{
  const c=landSurfaceContext(),geometry=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8');c.rad=x=>x*Math.PI/180;
  vm.runInContext(geometry.slice(geometry.indexOf('function v018Lambert93'),geometry.indexOf('const V018_OLD_SCALES')),c);
  const project=vm.runInContext('v018Lambert93',c),origin=project(43.285,5.51),vertices=[],faces=[],n=21;
  for(let j=0;j<n;j++)for(let i=0;i<n;i++){const p=project(43.2976-j*.002/(n-1),5.5698+i*.002/(n-1));vertices.push([p[0]-origin[0],100,origin[1]-p[1]]);}
  for(let j=0;j<n-1;j++)for(let i=0;i<n-1;i++){const a=j*n+i;faces.push([a,a+n,a+1],[a+1,a+n,a+n+1]);}
  c.fine={vertices,faces,v047GeometryId:'curved'};const support=await vm.runInContext('v050TerrainSupport(fine,job.work)',c),b=support.bounds;
  const triangle=[[b.minX-1000,30,b.minZ-1000],[b.minX-1000,30,b.maxZ+2000],[b.maxX+2000,30,b.minZ-1000]],out=vm.runInContext('v050ClipLandTriangle',c)(triangle,support);
  const removed=surfaceArea([triangle])-surfaceArea(out);assert.ok(Math.abs(removed-(b.maxX-b.minX)*(b.maxZ-b.minZ))<1e-4);
  assert.ok(out.flat().every(p=>p[1]===30));assert.equal(c.fine.vertices,vertices);
});
test('The outer stitch mask removes land over boundary NoData and colours the unchanged seam faces too',async()=>{
  const c=landSurfaceContext(),box={minX:0,maxX:4,minZ:0,maxZ:4};
  c.fine={vertices:[[0,0,0],[0,0,4],[4,0,0],[4,0,4],[1,12,1],[1,14,2],[2,13,1]],faces:[[4,5,6]],color:[.1,.2,.3],v050FineTerrain:true,v050LandMask:box,v050LandMaskId:'window',v047GeometryId:'fine'};
  c.seam={vertices:[[0,4,0],[0,5,1],[1,5,0]],faces:[[0,1,2]],color:[.1,.2,.3],v050TerrainSeam:true,v050LandMask:box,v050LandMaskId:'window',v047GeometryId:'seam'};
  c.land={vertices:[[-10,3,-10],[-10,3,20],[20,3,-10]],faces:[[0,1,2]],color:[.6,.4,.3],rings:[[[-10,-10],[-10,20],[20,-10],[-10,-10]]],geoLayer:'landuse',v046GeometryId:'land'};
  const result=await vm.runInContext('v050RefineLandSurfaces([fine,seam],[land],job)',c),cut=result.draws[0];
  assert.ok(Math.abs(surfaceArea(cut.faces.map(f=>f.map(i=>cut.vertices[i])))-434)<1e-8);
  const fine=result.terrain.find(d=>d.v050FineTerrain),seam=result.terrain.find(d=>d.v050TerrainSeam);assert.equal(fine.vertices,c.fine.vertices);assert.equal(seam.vertices,c.seam.vertices);assert.deepEqual(seam.color,c.land.color);assert.equal(seam.faces[0],c.seam.faces[0]);assert.equal(fine.faces[0],c.fine.faces[0]);
  assert.ok(!cut.faces.some(f=>M.inside([f.map(i=>[cut.vertices[i][0],cut.vertices[i][2]])],.5,2)));
});
function sourceCacheContext(){
  const c=landSurfaceContext();c.V047={meshes:new c.MistralStream.BudgetCache(12*1024*1024,64),records:new Map()};
  c.v015GeoProject=(_id,lat,lon)=>[(lon-1)*111320,0,(1-lat)*111320];c.v015GeoUnproject=(_id,x,z)=>[1-z/111320,1+x/111320];
  c.bank=new c.MistralIntegrity.TerrainBank({geo_huveaune:[0,0,2,2]});c.bank.add(grid('geo_huveaune',[0,0,2,2],[10,10,10,10]),'geo_huveaune');c.plan={lat:1,lon:1,p:[0,0,0]};return c;
}
test('A native-size fine patch survives the separate bounded cache even when the 12 MiB coarse cache evicts it',async()=>{
  const c=sourceCacheContext(),width=326,height=446,values=Array(width*height).fill(23.5),missing=Math.floor(height/2)*width+Math.floor(width/2);values[missing]=null;
  c.bank.add({...grid('enrichment:geo_huveaune',[.999,.999,1.001,1.001],values,width,height),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'},'enrichment:geo_huveaune');
  const first=await vm.runInContext("v050RefineTerrainMeshes([],plan,bank,'native',job)",c),fine=first.find(d=>d.v050FineTerrain),cache=vm.runInContext('v050TerrainCache()',c),entry=[...cache.values()][0];
  assert.equal(fine.vertices.length,width*height);assert.ok(!fine.faces.some(f=>f.includes(missing)));assert.ok(cache.stats().bytes>12*1024*1024);assert.ok(cache.stats().bytes<=64*1024*1024);assert.equal(cache.stats().entries,1);
  c.V047.meshes.set('large-source-proof',entry);assert.equal(c.V047.meshes.size,0);assert.equal(cache.size,1);
  c.plan={lat:1.0008,lon:1.0008,p:c.v015GeoProject('',1.0008,1.0008)};
  const second=await vm.runInContext("v050RefineTerrainMeshes([],plan,bank,'native',job)",c);assert.equal(second.find(d=>d.v050FineTerrain),fine);assert.equal(second.find(d=>d.v050TerrainSeam),first.find(d=>d.v050TerrainSeam));assert.equal(cache.stats().hits,1);assert.ok(cache.stats().entries<=2);
  assert.equal(vm.runInContext('v050RefreshGeography()',c),true);assert.equal(cache.size,0);
});
test('Small source grids reuse the complete patch across anchors and invalidate by source stamp, datum and NoData',async()=>{
  const c=sourceCacheContext(),raw={...grid('enrichment:geo_huveaune',[.9999,.9999,1.0001,1.0001],Array(49).fill(14),7,7),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'};
  c.bank.add(raw,raw.macro);const stamp=()=>vm.runInContext('v047BankStamp(bank)',c),build=async()=>{c.stamp=stamp();return(await vm.runInContext('v050RefineTerrainMeshes([],plan,bank,stamp,job)',c)).find(d=>d.v050FineTerrain);};
  const first=await build();c.plan={lat:1.00009,lon:.99991,p:c.v015GeoProject('',1.00009,.99991)};assert.equal(await build(),first);
  c.bank.add({...raw,verticalDatum:'EPSG:5720'},raw.macro);const datum=await build();assert.notEqual(datum,first);assert.equal(datum.vertices.length,49);
  const values=raw.values.slice();values[24]=null;c.bank.add({...raw,values,verticalDatum:'EPSG:5720'},raw.macro);const changed=await build();assert.notEqual(changed,datum);assert.ok(!changed.faces.some(f=>f.includes(24)));
  const cache=vm.runInContext('v050TerrainCache()',c);assert.equal(cache.size,2);assert.ok(cache.stats().evictions>=1);assert.ok(cache.stats().bytes<=cache.maxBytes);
});
test('A physically wider source retains a bounded moving window instead of caching the complete grid',async()=>{
  const c=sourceCacheContext(),width=257,height=65,raw={...grid('enrichment:geo_huveaune',[.999,.996,1.001,1.004],Array(width*height).fill(14),width,height),sourceResource:'survey',provenance:proof,verticalDatum:'NGF-IGN69'};c.bank.add(raw,raw.macro);
  const first=(await vm.runInContext("v050RefineTerrainMeshes([],plan,bank,'wide',job)",c)).find(d=>d.v050FineTerrain);assert.ok(first.vertices.length<width*height);
  c.plan={lat:1,lon:1.0035,p:c.v015GeoProject('',1,1.0035)};const second=(await vm.runInContext("v050RefineTerrainMeshes([],plan,bank,'wide',job)",c)).find(d=>d.v050FineTerrain);assert.notEqual(second,first);assert.ok(second.vertices.length<=262144);assert.ok(second.vertices.length<width*height);
});
