'use strict';
/* Production geometry/save/door/service/storage modules. Source, loader and
   localStorage seams are explicit controlled fixtures; no native play claim. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),test=require('node:test');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'src/v050/08_city_interiors.js'),'utf8'),G=require('../../src/v050/08_city_interiors.js'),F=require('../../src/v050/07_facades.js');
const square=[[[0,0],[20,0],[20,20],[0,20]]],shared=fs.readFileSync(path.join(__dirname,'city_interiors.cjs'),'utf8');
const start=shared.indexOf('function runtime(){'),end=shared.indexOf('\n// End reusable interior runtime harness.',start);
assert.ok(start>=0&&end>start);
const runtime=Function('fs','path','vm','root','source','F','square',shared.slice(start,end)+';return runtime;')(fs,path,vm,root,source,F,square);
const navStart=shared.indexOf('function reachable('),navEnd=shared.indexOf('\nfor(const[name,rings]',navStart);
assert.ok(navStart>=0&&navEnd>navStart);
const reachable=Function('G','assert',shared.slice(navStart,navEnd)+';return reachable;')(G,assert);
const clone=v=>JSON.parse(JSON.stringify(v)),sha=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/interior_layouts_before_domestic.json'),'utf8'));
const capture=l=>({layout:l,doors:G.roomDoorPlan(l),services:G.servicePlan(l),storage:G.storagePlan(l),models:l.furniture.map(f=>({id:f.id,parts:G.furnitureModel(f)}))});
function building(rings=square,id='synthetic-domestic',properties={usage_1:'Résidentiel'}){return G.building({id,sourceId:'declared-synthetic-regression',rings,baseY:12,height:12,levels:3,properties});}
function enter(f){return f.run('d.v050CityInteriorEnter(d.v050CityInteriorInfo().doors[0].id)');}
async function leave(f){f.run('state.player.pos=[world.v050CityInterior.entry[0],world.v050CityInterior.elevation+1.65,world.v050CityInterior.entry[1]]');assert.equal(f.run('d.v050CityInteriorExit()'),true);await f.run('Promise.resolve().then(()=>Promise.resolve())');assert.equal(f.run('world.id'),'geo_marseille');}
for(const row of baseline.cases)test('Frozen full layout/doors/services/deposits/models '+row.version+' '+row.name,()=>{
 const b=clone(row.building),before=clone(b),l=G.layout(b,row.level,row.entry,row.document);assert.equal(sha(capture(l)),row.sha256);assert.deepEqual(b,before);
});
test('Source descriptors retain five; only admitted new invented dwellings select six',()=>{
 const b=building(),before=clone(b);assert.equal(b.layoutVersion,5);assert.equal(G.visitBuilding(b).layoutVersion,6);assert.deepEqual(b,before);
 for(const use of['Industriel','Commercial','Bureau','École','Hôpital','Garage','Gymnase','Église'])assert.equal(G.visitBuilding(building(square,'use-'+use,{usage_1:use})).layoutVersion,5);
 assert.equal(G.visitBuilding(b,{},true).layoutVersion,5);
});
for(const version of[1,2,3,4,5,6])test('Recorded visit version '+version+' cannot upgrade or downgrade on another entrance',()=>{
 const b=building(),k=G.hash(b.id);assert.equal(G.visitBuilding(b,{visitLayouts:{[k]:version},visits:{[k]:8}}).layoutVersion,version);
});
test('Historical inactive visits without a snapshot or explicit version remain five',()=>{
 const b=building(),k=G.hash(b.id);assert.equal(G.visitBuilding(b,{visits:{[k]:9}}).layoutVersion,5);
});
test('Version registry rejects prototype/invalid values and has a hard non-evicting bound',()=>{
 const input=Object.fromEntries(Array.from({length:G.VISIT_LAYOUT_LIMIT+5},(_,i)=>[i.toString(16).padStart(16,'0'),6])),before=clone(input),out=G.migrateVisitLayouts(input);
 assert.equal(Object.keys(out).length,G.VISIT_LAYOUT_LIMIT);assert.deepEqual(input,before);assert.equal(out['0000000000000800'],undefined);
 assert.deepEqual(G.migrateVisitLayouts(JSON.parse('{"__proto__":6,"constructor":6,"0000000000000001":0,"0000000000000002":7,"0000000000000003":"6"}')),{});
 assert.equal(G.visitBuilding(building(),{visitLayouts:out}).layoutVersion,5);
 const k=Object.keys(out)[0];assert.equal(G.visitBuilding({...building(),id:'known'}, {visitLayouts:{...out,[G.hash('known')]:6},visitHistoryLimited:true}).layoutVersion,6);assert.equal(out[k],6);
});
test('A full bathroom is private, sleeping is separate and fridge follows a closed kitchen',()=>{
 const b=G.visitBuilding(building()),l=G.layout(b,0,[-8,-8]),bath=l.rooms.find(r=>r.type==='bathroom'),bed=l.rooms.find(r=>r.type==='bedroom'),kitchen=l.rooms.find(r=>r.type==='kitchen');
 assert.ok(bath&&bed&&kitchen);for(const kind of['sanitary','washbasin','shower'])assert.ok(l.furniture.some(f=>f.kind===kind&&f.roomId===bath.id));
 assert.ok(l.furniture.some(f=>f.kind==='bed'&&f.roomId===bed.id));assert.ok(l.furniture.some(f=>f.kind==='fridge'&&f.roomId===kitchen.id));assert.ok(l.furniture.some(f=>f.kind==='sanitary'&&f.variant==='compact'));
 assert.ok(G.roomDoorPlan(l).doors.some(d=>d.roomId===bath.id));assert.equal(l.programCoverage.completeInventedProgram,true);assert.equal(l.programCoverage.domesticProgramme.provenance,'invented');
 assert.deepEqual(l.programCoverage.domesticProgramme.equipmentNotOperational,['shower','fridge']);assert.equal(l.source,null);
});
test('New physical models fit their metric footprint and do not provide water, food or a new service',()=>{
 for(const kind of['shower','fridge']){const def=G.FURNITURE[kind],parts=G.furnitureModel({kind});assert.ok(parts.length>1&&parts.length<=10);for(const p of parts){assert.ok(Math.abs(p.pos[0])+p.size[0]/2<=def.size[0]/2+1e-7);assert.ok(Math.abs(p.pos[2])+p.size[2]/2<=def.size[1]/2+1e-7);assert.ok(p.pos[1]-p.size[1]/2>=-1e-7);assert.ok(p.pos[1]+p.size[1]/2<=def.height+1e-7);}assert.equal(G.SERVICE_KINDS[kind],undefined);assert.equal(G.STORAGE_KINDS[kind],undefined);}
});
test('A tiny home reports missing private wet room instead of putting its WC in the living space',()=>{
 const b=G.visitBuilding(building([[[0,0],[3,0],[3,6],[0,6]]])),l=G.layout(b,0,[-.8,-2]);assert.equal(l.rooms.some(r=>r.type==='bathroom'),false);
 for(const kind of['sanitary','washbasin','shower']){assert.ok(!l.furniture.some(f=>f.kind===kind));assert.ok(l.programCoverage.furnishingOmissions.some(o=>o.kind===kind&&o.reason==='requires-private-wet-room'));}
 assert.equal(l.programCoverage.completeInventedProgram,false);
});
const shapes=[['compact home',[[[0,0],[6,0],[6,8],[0,8]]]],['apartment',[[[0,0],[10,0],[10,12],[0,12]]]],['courtyard',[[[0,0],[24,0],[24,20],[0,20]],[[9,7],[15,7],[15,13],[9,13]]]],['concave wing',[[[0,0],[20,0],[20,6],[6,6],[6,20],[0,20]]]],['linked wings',[[[0,0],[30,0],[30,12],[20,12],[20,24],[30,24],[30,36],[0,36],[0,24],[10,24],[10,12],[0,12]]]]];
for(const[name,rings]of shapes)test('Independent actor flood fill and actual furniture bodies stay connected: '+name,()=>{
 const b=G.visitBuilding(building(rings,'nav-'+name)),bb=G.bounds(b.rings),l=G.layout(b,0,[bb.minX+1,bb.minZ+1]),nav=reachable(l,.2);
 assert.equal(nav.reached,nav.all,JSON.stringify(nav.unreached.slice(0,5)));assert.deepEqual(l.rings,b.rings);assert.equal(l.programCoverage.navigation.newUnreachableCells,0);
 assert.ok(l.furniture.length<=32&&l.rooms.length<=10&&l.programCoverage.navigation.sampledCells<=4096&&l.programCoverage.navigationChecks<=180);
 for(const f of l.furniture){assert.ok(G.walkable(l,...f.approach,.38));assert.ok(!l.furniture.some(o=>G.furnitureBlocked(o,...f.approach,.38)));assert.ok(f.ring.every(p=>G.clearance(l.rings,...p)>=.1));assert.equal(f.provenance,'invented');}
});
test('A rotated source and upper floor retain their rings, metric heights and deterministic plan',()=>{
 const a=.37,rings=[square[0].map(([x,z])=>[Math.cos(a)*x-Math.sin(a)*z,Math.sin(a)*x+Math.cos(a)*z])],b=G.visitBuilding(building(rings,'rotated')),saved=clone(b),first=G.layout(b,2),next=G.layout(G.validateBuilding(saved),2);
 assert.deepEqual(next,first);assert.deepEqual(first.rings,b.rings);assert.equal(first.elevation,8);assert.equal(first.height,4);assert.equal(first.programCoverage.navigation.newUnreachableCells,0);
});
test('Documentary visits keep the entire version-five plan and models even if given a six descriptor',()=>{
 const row=baseline.cases.find(r=>r.version===5&&r.document),b={...clone(row.building),layoutVersion:6};assert.equal(sha(capture(G.layout(b,row.level,row.entry,row.document))),row.sha256);
});
test('Actual attributed IGN dwelling retains original XYZ, projected footprint and source height with invented rooms only',()=>{
 const record=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/interior_domestic_source.json'),'utf8')).cases[0],before=clone(record),patch=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8'),ctx=vm.createContext({rad:n=>n*Math.PI/180});
 vm.runInContext(patch.slice(patch.indexOf('function v018Lambert93'),patch.indexOf('const V018_OLD_SCALES')),ctx);const origin=ctx.v018Lambert93(...record.projection.originLatLon),polygon=record.rawFeature.geometry.type==='MultiPolygon'?record.rawFeature.geometry.coordinates[0]:record.rawFeature.geometry.coordinates,rings=polygon.map(r=>r.map(p=>{const q=ctx.v018Lambert93(p[1],p[0]);return[q[0]-origin[0],origin[1]-q[1]];}));
 assert.equal(crypto.createHash('sha256').update(JSON.stringify(record.rawFeature)).digest('hex'),record.sourceFeatureSha256);assert.deepEqual(rings,record.metric.rings);
 const profile=require('../../src/v046/00_integrity.js').buildingProfile(record.rawFeature.properties);assert.equal(record.metric.baseY,profile.groundElevation??0);assert.equal(record.metric.height,profile.height);
 const b=G.visitBuilding(G.building(F.describe({mesh:'prism',geoLayer:'building',...record.metric,geoProperties:record.rawFeature.properties,sourceGeometry:record.rawFeature.geometry}))),l=G.layout(b,0,record.expected.localEntry);
 assert.equal(b.id,record.expected.buildingId);assert.equal(b.layoutVersion,6);assert.equal(b.programmeUse.basis,'source-attribute');assert.equal(b.programmeUse.field,'usage_1');assert.equal(b.programmeUse.value,'Résidentiel');assert.deepEqual(l.rings,b.rings);assert.equal(l.source,null);assert.equal(l.provenance,'invented');assert.ok(l.furniture.some(f=>f.kind==='shower'));assert.ok(l.furniture.some(f=>f.kind==='fridge'));assert.deepEqual(record,before);
});
const restCases=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/interior_domestic_rest.json'),'utf8')).cases;
for(const c of restCases)test('Exact native84 home '+c.sourceId+' keeps its plan and obtains only a physically admitted bed service',()=>{
 const l=G.layout(c.building,c.floor,c.entry),before=JSON.stringify(l),plan=G.servicePlan(l),rest=plan.services.find(s=>s.kind==='rest');assert.equal(sha(l),c.expected.layoutSha256);assert.equal(l.signature,c.expected.signature);assert.equal(sha(G.storagePlan(l)),c.expected.storagePlanSha256);assert.equal(JSON.stringify(l),before);
 assert.equal(!!rest,c.expected.restAfterBoundedFallback);assert.equal(crypto.createHash('sha256').update(JSON.stringify(c.rawFeature)).digest('hex'),c.sourceFeatureSha256);
 const bed=l.furniture.find(f=>f.id===c.expected.bedId);assert.deepEqual(bed.approach,c.expected.originalApproach);assert.equal(G.SERVICE_APPROACH_PROBES,4);
 if(rest){assert.equal(rest.furnitureId,bed.id);assert.notDeepEqual(rest.approach,bed.approach);assert.equal(rest.approachBasis,'same-bed-navigation-proof');assert.ok(rest.approachProbe<=4);assert.ok(G.walkable(l,...rest.approach,.4));assert.ok(!l.furniture.some(f=>G.furnitureBlocked(f,...rest.approach,.4)));assert.ok(G.canTravel(l,rest.approach,[rest.target[0],rest.target[2]],.04));assert.ok(rest.meshPart.offsetMeters<=.16);assert.equal(rest.meshPart.material,'blanket');}
 else assert.ok(plan.omissions.some(o=>o.furnitureId===bed.id&&o.reason===c.expected.originalOmission.reason));
 const fivePlan=G.servicePlan({...l,layoutVersion:5});assert.ok(!fivePlan.services.some(s=>s.kind==='rest'));assert.ok(fivePlan.omissions.some(o=>o.furnitureId===bed.id&&o.reason===c.expected.originalOmission.reason));
});
test('The real six bed fallback does not mutate frozen geometry or furniture approaches',()=>{
 const c=restCases[0],l=G.layout(c.building,c.floor,c.entry),before=JSON.stringify(l);function freeze(o){if(o&&typeof o==='object'){Object.freeze(o);for(const v of Object.values(o))freeze(v);}}freeze(l);assert.ok(G.servicePlan(l).services.some(s=>s.kind==='rest'));assert.equal(JSON.stringify(l),before);
});
test('The alternate bed approach is independently reachable around actual final furniture bodies',()=>{
 const c=restCases[0],l=G.layout(c.building,c.floor,c.entry),result=reachable(l,.2);assert.equal(result.reached,result.all);assert.ok(G.servicePlan(l).services.some(s=>s.kind==='rest'));
});
test('An extra solid on the only eligible alternate bed approach preserves the original refusal',()=>{
 const c=restCases[0],l=G.layout(c.building,c.floor,c.entry),rest=G.servicePlan(l).services.find(s=>s.kind==='rest'),[x,z]=rest.approach;l.furniture.push({id:'declared-synthetic-blocker',kind:'crate',pos:[x,z],size:[.8,.8],height:1.4,ring:[[x-.4,z-.4],[x+.4,z-.4],[x+.4,z+.4],[x-.4,z+.4],[x-.4,z-.4]],provenance:'invented'});const before=JSON.stringify(l);assert.ok(!G.servicePlan(l).services.some(s=>s.kind==='rest'));assert.equal(JSON.stringify(l),before);
});
test('An alternate physically free point behind a synthetic partition never bypasses navigation proof',()=>{
 const c=restCases[0],l=G.layout(c.building,c.floor,c.entry),bed=l.furniture.find(f=>f.kind==='bed'),bb=G.bounds(l.rings),x=(l.entry[0]+bed.pos[0])/2;l.walls.push({a:[x,bb.minZ-1],b:[x,bb.maxZ+1],thickness:.2,provenance:'invented-synthetic-blocker'});const before=JSON.stringify(l);assert.ok(!G.servicePlan(l).services.some(s=>s.kind==='rest'));assert.equal(JSON.stringify(l),before);
});
function actualBedRuntime(){
 const c=restCases[0],f=runtime(),draw={mesh:'prism',geoLayer:'building',...c.metric,geoProperties:c.rawFeature.properties,sourceGeometry:c.rawFeature.geometry},door=F.entrances(draw,{preferredId:c.doorId}).find(d=>d.id===c.doorId);assert.ok(door);
 f.run('world.staticDraws=['+JSON.stringify(draw)+'];test.ground=()=>'+c.ground+';state.player.pos='+JSON.stringify([door.outside[0],c.ground+1.65,door.outside[2]])+';d.v050CityInteriorBind();function hasCost(c){return Object.entries(c).every(([k,n])=>(state.inventory[k]||0)>=n);}function v020Spend(c){if(!hasCost(c))return false;for(const[k,n]of Object.entries(c))state.inventory[k]-=n;return true;}state.inventory.water=3;state.status={};state.needs={fatigue:80,thirst:80,hunger:80};state.worldTime=12;state.v020={restHours:0};Object.assign(state.player,{hp:50,maxHp:100,ap:20,maxAp:100})');assert.equal(enter(f),true);f.run('globalThis.service=d.v050CityInteriorInfo().services.stations.find(s=>s.kind==="rest");state.player.pos=[service.approach[0],world.v050CityInterior.elevation+1.65,service.approach[1]]');assert.equal(f.run('service.approachBasis'),'same-bed-navigation-proof');return f;
}
test('The actual home fallback keeps runtime LOS refusal and exact ordinary paid rest',()=>{
 const f=actualBedRuntime();f.run('test.sight=false');const before=f.json('state');assert.equal(f.run('d.v056CityInteriorService(service.id,"rest:1")'),false);assert.deepEqual(f.json('state'),before);f.run('test.sight=true');assert.equal(f.run('d.v056CityInteriorService(service.id,"rest:1")'),true);assert.equal(f.run('state.inventory.water'),2);assert.equal(f.run('state.worldTime'),13);assert.equal(f.run('state.v050City.services.restHours'),1);
});
for(const failure of['false','exception'])test('The actual alternate home bed rolls back '+failure+' persistence failure without changing plan or supplies',()=>{
 const f=actualBedRuntime(),before=f.json('state'),l=f.json('world.v050CityInterior');f.run(failure==='false'?'test.failSave=true':'test.throwSave=true');assert.equal(f.run('d.v056CityInteriorService(service.id,"rest:1")'),false);assert.deepEqual(f.json('state'),before);assert.deepEqual(f.json('world.v050CityInterior'),l);
});
test('Production entry, cold Continue and reentry preserve six plus service and deposit identities',async()=>{
 const f=runtime();assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),6);const sig=f.run('world.v050CityInterior.signature'),ids=f.json('[d.v050CityInteriorInfo().services.stations.map(s=>s.id),d.v050CityInteriorInfo().storage.stores.map(s=>s.id)]');
 assert.ok(f.run('world.staticDraws.some(d=>d.v050CityFurnishing?.kind==="shower")'));assert.ok(f.run('world.colliders.some(d=>d.v050CityFurnishing?.kind==="shower")'));
 f.run('state=migrateState(JSON.parse(test.saved));loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');assert.equal(f.run('world.v050CityInterior.signature'),sig);await leave(f);assert.equal(enter(f),true);assert.equal(f.run('world.v050CityInterior.signature'),sig);assert.deepEqual(f.json('[d.v050CityInteriorInfo().services.stations.map(s=>s.id),d.v050CityInteriorInfo().storage.stores.map(s=>s.id)]'),ids);
});
for(const version of[1,2,3,4,5])test('Old active layout '+version+' migrates, exits and reenters with identical geometry and local IDs',async()=>{
 const f=runtime();assert.equal(enter(f),true);f.run('globalThis.old=JSON.parse(test.saved);old.v050City.active.building.layoutVersion='+version+';delete old.v050City.visitLayouts;delete old.v050City.visitHistoryLimited;state=migrateState(old);loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');
 assert.equal(f.run('state.v050City.active.building.layoutVersion'),version);const before=f.json('world.v050CityInterior'),ids=f.json('[d.v050CityInteriorInfo().services.stations,d.v050CityInteriorInfo().storage.stores]');await leave(f);assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),version);assert.deepEqual(f.json('world.v050CityInterior'),before);assert.deepEqual(f.json('[d.v050CityInteriorInfo().services.stations,d.v050CityInteriorInfo().storage.stores]'),ids);
});
test('An inactive historical five keeps its exact populated cupboard after migration and reentry',async()=>{
 const f=runtime();f.run('state.v050City.visits[MistralCityInteriors.hash(d.v050CityInteriorInfo().doors[0].building)]=3');assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),5);
 const store=f.run('d.v050CityInteriorInfo().storage.stores[0].id'),sig=f.run('world.v050CityInterior.signature');f.run('state.v050City.storage['+JSON.stringify(store)+']={scrap:4};saveGame(false)');await leave(f);
 f.run('globalThis.old=JSON.parse(test.saved);delete old.v050City.visitLayouts;delete old.v050City.visitHistoryLimited;state=migrateState(old);loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');assert.equal(enter(f),true);assert.equal(f.run('world.v050CityInterior.signature'),sig);assert.deepEqual(f.json('state.v050City.storage['+JSON.stringify(store)+']'),{scrap:4});assert.ok(f.json('d.v050CityInteriorInfo().storage.stores.map(s=>s.id)').includes(store));
});
test('A later documentary plan cannot replace a saved six or orphan its populated cupboard',async()=>{
 const f=runtime();assert.equal(enter(f),true);const sig=f.run('world.v050CityInterior.signature'),furniture=f.json('world.v050CityInterior.furniture'),id=f.run('state.v050City.active.building.id'),store=f.run('d.v050CityInteriorInfo().storage.stores[0].id'),doc=clone(baseline.cases.find(r=>r.document).document);doc.buildingId=id;
 f.run('state.v050City.storage['+JSON.stringify(store)+']={scrap:4};saveGame(false)');const before=f.json('state'),saved=f.run('test.saved');assert.throws(()=>f.run('d.v050CityRegisterDocument('+JSON.stringify(doc)+')'),/aménagement inventé sauvegardé/);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),saved);
 await leave(f);f.run('world.staticDraws[0].geoProperties.interiorDocument='+JSON.stringify(doc)+';d.v050CityInteriorBind()');assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'invented');assert.ok(f.json('d.v050CityInteriorInfo().documentRegistry.rejections').some(r=>/Plan tardif non appliqué/.test(r.reason)));
 assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),6);assert.equal(f.run('world.v050CityInterior.signature'),sig);assert.deepEqual(f.json('world.v050CityInterior.furniture'),furniture);assert.deepEqual(f.json('state.v050City.storage['+JSON.stringify(store)+']'),{scrap:4});
 f.run('state=migrateState(JSON.parse(test.saved));loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');assert.equal(f.run('world.v050CityInterior.signature'),sig);assert.deepEqual(f.json('state.v050City.storage['+JSON.stringify(store)+']'),{scrap:4});
 assert.equal(G.visitBuilding(building(square,id),{visitLayouts:{[G.hash(id)]:6}},true).layoutVersion,6);
});
test('Approaching a different facade keeps the original six entrance, full signature and populated cupboard',async()=>{
 const f=runtime();assert.equal(enter(f),true);const original=f.json('state.v050City.active'),layout=f.json('world.v050CityInterior'),store=f.run('d.v050CityInteriorInfo().storage.stores[0].id');f.run('state.v050City.storage['+JSON.stringify(store)+']={scrap:3};saveGame(false)');await leave(f);
 f.run('state.player.pos=[10,1.65,21.15];d.v050CityInteriorBind()');assert.equal(f.run('world.staticDraws[0].v050EntranceSelection.id'),original.entranceId);assert.equal(enter(f),false);f.run('state.player.pos=d.v050CityInteriorInfo().doors[0].pos.slice();state.player.pos[1]=1.65');assert.equal(enter(f),true);assert.deepEqual(f.json('world.v050CityInterior'),layout);assert.deepEqual(f.json('state.v050City.active.entry'),original.entry);assert.deepEqual(f.json('state.v050City.storage['+JSON.stringify(store)+']'),{scrap:3});
});
test('An unavailable saved source entrance refuses any alternative and preserves version, plan and supplies',async()=>{
 const f=runtime();assert.equal(enter(f),true);const entrance=f.run('state.v050City.active.entranceId');f.run('globalThis.savedEntrance='+JSON.stringify(entrance));await leave(f);const before=f.json('state');
 f.run('globalThis.originalFacades=MistralFacades;MistralFacades={...originalFacades,entrances:(...a)=>originalFacades.entrances(...a).filter(d=>d.id!==savedEntrance)};d.v050CityInteriorBind()');assert.equal(f.run('d.v050CityInteriorInfo().doors.length'),0);assert.equal(f.run('d.v050CityInteriorInfo().rejections.savedEntranceUnavailable'),1);assert.equal(f.run('world.staticDraws[0].v050EntranceSelection'),null);assert.deepEqual(f.json('state'),before);
 f.run('MistralFacades=originalFacades;d.v050CityInteriorBind()');assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.entranceId'),entrance);assert.equal(f.run('state.v050City.active.building.layoutVersion'),6);
});
test('A blocked original approach never moves an existing six to another free facade',async()=>{
 const f=runtime();assert.equal(enter(f),true);await leave(f);const before=f.json('state'),p=f.json('d.v050CityInteriorInfo().doors[0].pos');f.run('test.blocked=(x,z)=>Math.hypot(x-('+p[0]+'),z-('+p[2]+'))<1;d.v050CityInteriorBind()');assert.equal(f.run('d.v050CityInteriorInfo().doors.length'),0);assert.equal(f.run('d.v050CityInteriorInfo().rejections.savedEntranceUnavailable'),1);assert.deepEqual(f.json('state'),before);
});
test('Entrance identities are bounded, validated and recoverable from a cold active visit',()=>{
 const k=G.hash('home'),versions={[k]:6},id='source-building:entrance:outer:1';assert.deepEqual(G.migrateVisitEntrances({[k]:id},versions),{[k]:id});assert.deepEqual(G.migrateVisitEntrances({[k]:id},{[k]:5}),{});assert.deepEqual(G.migrateVisitEntrances({[k]:'x'.repeat(1025)},versions),{});
 const entries=Object.fromEntries(Array.from({length:512},(_,i)=>[i.toString(16).padStart(16,'0'),'x'.repeat(1024)]));assert.equal(G.entranceFits({visitEntrances:entries},k,id),false);
 const f=runtime();assert.equal(enter(f),true);const entrance=f.run('state.v050City.active.entranceId');f.run('globalThis.cold=JSON.parse(test.saved);delete cold.v050City.visitEntrances;state=migrateState(cold);loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');assert.equal(f.run('state.v050City.active.entranceId'),entrance);assert.equal(f.run('Object.values(state.v050City.visitEntrances)[0]'),entrance);
});
test('Truncated old visit history never promotes its omitted inactive home or clears the conservative marker',()=>{
 const f=runtime();f.run('globalThis.old=JSON.parse(JSON.stringify(state));old.v050City.visits=Object.fromEntries(Array.from({length:20000},(_,i)=>[i.toString(16).padStart(16,"0"),1]));old.v050City.visits[MistralCityInteriors.hash(d.v050CityInteriorInfo().doors[0].building)]=1;delete old.v050City.visitHistoryLimited;state=migrateState(old);d.v050CityInteriorBind()');
 assert.equal(f.run('state.v050City.visitHistoryLimited'),true);assert.equal(f.run('Object.keys(state.v050City.visits).length'),20000);assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),5);assert.equal(f.run('Object.keys(state.v050City.visits).length'),20000);
 f.run('state=migrateState(JSON.parse(test.saved));loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');assert.equal(f.run('state.v050City.visitHistoryLimited'),true);
});
test('A full version registry keeps every previous entry and admits a new home on five',()=>{
 const f=runtime();f.run('state.v050City.visitLayouts=Object.fromEntries(Array.from({length:2048},(_,i)=>[i.toString(16).padStart(16,"0"),6]))');const before=f.json('state.v050City.visitLayouts');assert.equal(enter(f),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),5);assert.deepEqual(f.json('state.v050City.visitLayouts'),before);
});
for(const failure of['false','exception'])test('Failed '+failure+' entry rolls back all version/history metadata and exact scene',()=>{
 const f=runtime(),before=f.json('state');f.run('globalThis.beforeScene=world;'+(failure==='false'?'test.failSave=true':'test.throwSave=true'));assert.equal(enter(f),false);assert.deepEqual(f.json('state'),before);assert.equal(f.run('world===beforeScene'),true);assert.equal(f.run('Object.keys(state.v050City.visitLayouts).length'),0);
});
test('Changing floors and returning preserves six, finite salvage and independent door identities',()=>{
 const f=runtime();assert.equal(enter(f),true);f.run('Object.values(state.v026.containers)[0].items={};saveGame(false)');const before=f.json('state.v026.containers'),sig=f.run('world.v050CityInterior.signature'),doors=f.json('d.v050CityInteriorInfo().roomDoors.doors.map(d=>d.id)');assert.equal(f.run('d.v050CityInteriorFloor(1)'),true);assert.equal(f.run('state.v050City.active.building.layoutVersion'),6);assert.ok(f.json('d.v050CityInteriorInfo().roomDoors.doors.map(d=>d.id)').every(id=>!doors.includes(id)));assert.equal(f.run('d.v050CityInteriorFloor(-1)'),true);assert.equal(f.run('world.v050CityInterior.signature'),sig);const after=f.json('state.v026.containers');for(const[k,v]of Object.entries(before))assert.deepEqual(after[k],v);assert.equal(Object.keys(after).length,Object.keys(before).length+1);assert.deepEqual(after[Object.keys(before)[0]].items,{});
});
