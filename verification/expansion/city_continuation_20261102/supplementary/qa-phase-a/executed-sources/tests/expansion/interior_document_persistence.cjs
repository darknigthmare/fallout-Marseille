'use strict';
/* Execute the shipped interior transactions and native polygon builders with
   the same controlled scene/storage seams as city_interiors.cjs. Every plan
   here is an attributed synthetic regression fixture, not a measured survey. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),test=require('node:test');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'src/v050/08_city_interiors.js'),'utf8'),F=require('../../src/v050/07_facades.js');
const square=[[[0,0],[20,0],[20,20],[0,20],[0,0]]];
// Reuse only the controlled harness function, never execute the other suite.
// The new-game seam models the production reset through wrapped baseState().
const shared=fs.readFileSync(path.join(__dirname,'city_interiors.cjs'),'utf8'),start=shared.indexOf('function runtime(){'),end=shared.indexOf("\n// End reusable interior runtime harness.",start);
assert.ok(start>=0&&end>start,'The shared production runtime harness must be present');
const runtimeSource=shared.slice(start,end).replace('function startNewGame(){}','function startNewGame(){state=baseState();world=exterior();mode="PLAYING";}');
assert.notEqual(runtimeSource,shared.slice(start,end),'The new-game test seam must reset state');
const runtime=Function('fs','path','vm','root','source','F','square',runtimeSource+';return runtime;')(fs,path,vm,root,source,F,square);
const clone=o=>JSON.parse(JSON.stringify(o));
function plan(f,title='Synthetic coted plan'){
 return{schemaVersion:1,frame:'building-local-metre',buildingId:f.run('d.v050CityInteriorInfo().active?.id||d.v050CityInteriorInfo().doors[0].building'),source:{url:'https://example.org/declared-plan-fixture',license:'CC0 fixture',attribution:'Controlled persistence fixture',title,accessedAt:'2026-10-24'},levels:[{level:0,elevation:0,height:4,entry:[-8,-8],walls:[{a:[-2,-10],b:[-2,-1],thickness:.2},{a:[-2,1],b:[-2,10],thickness:.2}],rooms:[{id:'west',use:'fixture',ring:[[-10,-10],[-2,-10],[-2,10],[-10,10],[-10,-10]]}]}]};
}
function put(f,p=plan(f)){f.run('globalThis.planFixture='+JSON.stringify(p));return f.json('d.v050CityRegisterDocument(planFixture)');}
function enter(f){f.run('{const portalNext=d.v050CityInteriorInfo().doors[0].pos;state.player.pos=[portalNext[0],1.65,portalNext[2]];}');assert.equal(f.run('d.v050CityInteriorEnter(d.v050CityInteriorInfo().doors[0].id)'),true);}
async function exit(f){assert.equal(f.run('d.v050CityInteriorExit()'),true);await f.run('Promise.resolve().then(()=>Promise.resolve())');assert.equal(f.run('world.id'),'geo_marseille');assert.equal(f.run('state.v050City.active'),null);}
function cold(saved){const f=runtime();f.run('state=migrateState(JSON.parse('+JSON.stringify(saved)+'));loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true});d.v050CityInteriorBind()');return f;}
function declared(f){assert.equal(f.run('world.v050CityInterior.provenance'),'documented');assert.equal(f.run('d.v050CityInteriorInfo().active.currentLevelSource.attribution'),'Controlled persistence fixture');}

test('Registration is saved immediately with a bounded attributed metric record',()=>{
 const f=runtime(),p=plan(f),result=put(f,p),info=f.json('d.v050CityInteriorInfo()');
 assert.equal(result.persisted,true);assert.equal(result.activeSnapshotPreserved,false);assert.deepEqual(result.documentedLevels,[0]);assert.equal(info.doors[0].documentOrigin,'registered');assert.deepEqual(info.doors[0].documentSource,p.source);assert.equal(info.documentRegistry.entries,1);assert.equal(info.documentRegistry.maxBuildings,32);assert.equal(info.documentRegistry.maxBytes,512*1024);assert.ok(info.documentRegistry.bytes>0&&info.documentRegistry.bytes<=info.documentRegistry.maxBytes);
 const saved=JSON.parse(f.run('test.saved'));assert.deepEqual(saved.v050City.documents[0].document.source,p.source);assert.equal(saved.v050City.documents[0].building.id,p.buildingId);assert.equal(f.run('test.saves'),1);
 f.run('planFixture.source.title="changed by caller";planFixture.levels[0].walls[0].a[0]=999');assert.equal(f.run('state.v050City.documents[0].document.source.title'),p.source.title);assert.equal(f.run('state.v050City.documents[0].document.levels[0].walls[0].a[0]'),-2);
});

test('Documented walls, floors and attribution survive cold interior load, exit and reentry',async()=>{
 const first=runtime(),p=plan(first);assert.equal(first.run('d.v052CityInteriorLayout()'),null);put(first,p);enter(first);declared(first);const original=first.json('world.v050CityInterior'),saved=first.run('test.saved'),f=cold(saved);assert.deepEqual(first.json('d.v052CityInteriorLayout()'),original);first.run('globalThis.qaLayout=d.v052CityInteriorLayout();qaLayout.walls[0].a[0]=999');assert.equal(first.run('world.v050CityInterior.walls[0].a[0]'),-2);const furniture=first.json('d.v050CityInteriorInfo().active.furnishing');assert.equal(furniture.colliderFurniture,furniture.objects);assert.ok(furniture.renderFurniture>furniture.objects);
 declared(f);assert.deepEqual(f.json('world.v050CityInterior.walls'),original.walls);assert.equal(f.run('world.v050CityInterior.signature'),original.signature);assert.equal(f.run('state.v050City.documents.length'),1);await exit(f);assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'documented or mixed');enter(f);declared(f);assert.equal(f.run('world.v050CityInterior.signature'),original.signature);assert.deepEqual(f.json('world.v050CityInterior.walls'),original.walls);assert.deepEqual(f.json('state.v050City.active.document.source'),p.source);assert.equal(f.run('world.v050CityInterior.elevation'),0);assert.equal(f.run('world.v050CityInterior.height'),4);
});

test('An exterior save restores its registered plan in a completely new runtime',()=>{
 const first=runtime();put(first);const f=cold(first.run('test.saved'));assert.equal(f.run('d.v050CityInteriorInfo().doors[0].documentOrigin'),'registered');enter(f);declared(f);
});

test('Old active-only documentary saves recover a durable registry before leaving',async()=>{
 const first=runtime();put(first);enter(first);const saved=JSON.parse(first.run('test.saved'));delete saved.v050City.documents;delete saved.v050City.active.documentOrigin;saved.v050City.schema=1;
 const f=cold(JSON.stringify(saved));assert.equal(f.run('state.v050City.documents.length'),1);assert.equal(f.run('state.v050City.active.documentOrigin'),'legacy');declared(f);await exit(f);enter(f);declared(f);assert.equal(f.run('state.v050City.active.documentOrigin'),'registered');
});

test('Registering a revision indoors preserves the active snapshot across cold load',async()=>{
 const first=runtime();put(first,plan(first,'Old synthetic plan'));enter(first);const original=first.json('world.v050CityInterior'),revision=plan(first,'Revised synthetic plan');revision.levels[0].walls[0].a[0]=-3;revision.levels[0].walls[0].b[0]=-3;revision.levels[0].walls[1].a[0]=-3;revision.levels[0].walls[1].b[0]=-3;
 const result=put(first,revision);assert.equal(result.activeSnapshotPreserved,true);assert.equal(result.appliesOnNextEntry,true);assert.equal(first.run('state.v050City.active.document.source.title'),'Old synthetic plan');assert.equal(first.run('world.v050CityInterior.signature'),original.signature);assert.deepEqual(first.json('world.v050CityInterior.walls'),original.walls);
 const f=cold(first.run('test.saved'));assert.equal(f.run('state.v050City.active.document.source.title'),'Old synthetic plan');assert.equal(f.run('state.v050City.documents[0].document.source.title'),'Revised synthetic plan');assert.equal(f.run('world.v050CityInterior.signature'),original.signature);await exit(f);enter(f);assert.equal(f.run('world.v050CityInterior.source.title'),'Revised synthetic plan');assert.equal(f.run('world.v050CityInterior.walls[0].a[0]'),-3);assert.notEqual(f.run('world.v050CityInterior.signature'),original.signature);
});

test('Installed attributed properties are read without mutation or registry copying',async()=>{
 const f=runtime(),p=plan(f,'Installed synthetic plan');f.run('globalThis.installedFixture='+JSON.stringify(p)+';globalThis.installedProperties={...world.staticDraws[0].geoProperties,interiorDocument:installedFixture};globalThis.originalProperties=JSON.stringify(installedProperties);function freezeFixture(o){if(o&&typeof o==="object"){Object.freeze(o);for(const v of Object.values(o))freezeFixture(v);}}freezeFixture(installedProperties);const exteriorBase=exterior;exterior=function(){const w=exteriorBase();w.staticDraws[0].geoProperties=installedProperties;return w;};world.staticDraws[0].geoProperties=installedProperties;d.v050CityInteriorBind()');
 assert.equal(f.run('d.v050CityInteriorInfo().doors[0].documentOrigin'),'installed');assert.equal(f.run('state.v050City.documents.length'),0);enter(f);declared(f);assert.equal(f.run('state.v050City.active.documentOrigin'),'installed');assert.equal(f.run('JSON.stringify(installedProperties)===originalProperties'),true);
 f.run('state=migrateState(JSON.parse(test.saved));loadZone(state.player.zone,{spawn:state.player.pos,force:true,silent:true})');assert.equal(f.run('state.v050City.documents.length'),0);declared(f);await exit(f);enter(f);declared(f);assert.equal(f.run('state.v050City.documents.length'),0);assert.equal(f.run('JSON.stringify(installedProperties)===originalProperties'),true);
});

test('Installed plans with missing attribution are rejected with visible diagnostics',()=>{
 const f=runtime(),p=plan(f);delete p.source.attribution;f.run('world.staticDraws[0].geoProperties.interiorDocument='+JSON.stringify(p)+';d.v050CityInteriorBind()');const info=f.json('d.v050CityInteriorInfo()');assert.equal(info.doors[0].provenance,'invented');assert.equal(info.documentRegistry.entries,0);assert.ok(info.documentRegistry.rejections.some(r=>/installé refusé/.test(r.reason)));enter(f);assert.equal(f.run('world.v050CityInterior.provenance'),'invented');
});

for(const mode of['false','exception'])test('Failed '+mode+' storage during registration restores the prior plan and save',()=>{
 const f=runtime();put(f,plan(f,'Previously persisted fixture'));const before=f.json('state'),saved=f.run('test.saved');f.run(mode==='false'?'test.failSave=true':'test.throwSave=true');assert.throws(()=>put(f,plan(f,'Unsaved fixture')),mode==='false'?/annulé/:/disk full/);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),saved);assert.equal(f.run('d.v050CityInteriorInfo().doors[0].documentSource.title'),'Previously persisted fixture');assert.ok(f.run('d.v050CityInteriorInfo().documentRegistry.rejections.length')>0);
});

test('Invalid explicit documents leave save, registry and active geometry unchanged',()=>{
 const f=runtime();put(f);enter(f);const before=f.json('state'),signature=f.run('world.v050CityInterior.signature'),saved=f.run('test.saved'),bad=plan(f);bad.source.url='https://user:password@example.org/plan';assert.throws(()=>put(f,bad),/sans identifiants/);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),saved);assert.equal(f.run('world.v050CityInterior.signature'),signature);
});

test('A quota failure indoors preserves the exact scene, active plan and loot ledger',()=>{
 const f=runtime();put(f);enter(f);f.run('globalThis.sceneBeforeRegistration=world;test.failSave=true');const before=f.json('state'),saved=f.run('test.saved'),signature=f.run('world.v050CityInterior.signature');assert.throws(()=>put(f,plan(f,'Rejected indoor revision')),/annulé/);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),saved);assert.equal(f.run('world===sceneBeforeRegistration'),true);assert.equal(f.run('world.v050CityInterior.signature'),signature);assert.equal(f.run('d.v050CityInteriorInfo().active.documentSource.title'),'Synthetic coted plan');
});

test('A loaded save cannot inherit another save’s registered plan or diagnostics',()=>{
 const f=runtime();put(f);f.run('state=migrateState(baseState());updatePlayer(.6)');assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'invented');assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.entries'),0);assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.rejections.length'),0);enter(f);assert.equal(f.run('world.v050CityInterior.provenance'),'invented');
});

test('New game resets documentary data even in the same JavaScript runtime',()=>{
 const f=runtime();put(f);f.run('startNewGame();d.v050CityInteriorBind()');assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.entries'),0);assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'invented');enter(f);assert.equal(f.run('world.v050CityInterior.provenance'),'invented');
});

for(const [name,change]of[['height','world.staticDraws[0].height=13'],['levels','world.staticDraws[0].geoProperties.nombre_d_etages=4'],['absolute elevation','world.staticDraws[0].baseY=1;test.ground=()=>1']])test('A changed source '+name+' never receives a registered plan for the former volume',()=>{
 const f=runtime();put(f);f.run(change+';d.v050CityInteriorBind()');const info=f.json('d.v050CityInteriorInfo()');assert.equal(info.doors[0].provenance,'invented');assert.ok(info.documentRegistry.rejections.some(r=>/volume source a changé/.test(r.reason)));assert.equal(f.run('state.v050City.documents.length'),1);
});

test('A forged saved local footprint cannot retarget the registered plan',()=>{
 const first=runtime();put(first);const saved=JSON.parse(first.run('test.saved'));saved.v050City.documents[0].building.rings[0]=saved.v050City.documents[0].building.rings[0].map(p=>p.map(v=>v*1.1));const f=cold(JSON.stringify(saved));assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'invented');assert.ok(f.json('d.v050CityInteriorInfo().documentRegistry.rejections').some(r=>/volume source a changé/.test(r.reason)));
});

test('Cyclic vertex order and reversed winding preserve the same metric plan identity',()=>{
 const f=runtime();put(f);f.run('const reorderedRing=world.staticDraws[0].rings[0].slice(0,-1).reverse();reorderedRing.push(reorderedRing[0].slice());world.staticDraws[0].rings=[reorderedRing];d.v050CityInteriorBind()');assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'documented or mixed');assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.rejections.length'),0);
});

test('A source name or use update does not move or discard a metric documentary plan',()=>{
 const f=runtime();put(f);f.run('world.staticDraws[0].geoProperties.name="Updated source label";world.staticDraws[0].geoProperties.usage_1="Commercial";d.v050CityInteriorBind()');assert.equal(f.run('d.v050CityInteriorInfo().doors[0].provenance'),'documented or mixed');enter(f);declared(f);assert.equal(f.run('world.v050CityInterior.walls[0].a[0]'),-2);
});

test('A registration over the byte budget is rejected before persistence with explicit diagnostics',()=>{
 const f=runtime(),p=plan(f);p.extra='x'.repeat(262144);const before=f.json('state');assert.throws(()=>put(f,p),/budget/);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saves'),0);assert.ok(f.json('d.v050CityInteriorInfo().documentRegistry.rejections').some(r=>/512 Kio/.test(r.reason)));
});

test('Migration caps registry size and reports omitted, duplicate and invalid records',()=>{
 const first=runtime();put(first);const saved=JSON.parse(first.run('test.saved')),base=clone(saved.v050City.documents[0]);saved.v050City.documents=Array.from({length:35},(_,i)=>{const r=clone(base);r.building.id='bounded-fixture-'+i;r.document.buildingId=r.building.id;return r;});saved.v050City.documents[1]=clone(saved.v050City.documents[0]);delete saved.v050City.documents[2].document.source.license;
 const f=cold(JSON.stringify(saved)),info=f.json('d.v050CityInteriorInfo().documentRegistry');assert.equal(info.entries,30);assert.equal(info.omissions,5);assert.ok(info.warnings.some(s=>/dupliqué/.test(s)));assert.ok(info.warnings.some(s=>/provenance/.test(s)));assert.ok(info.warnings.some(s=>/budget/.test(s)));assert.ok(info.bytes<=info.maxBytes);
});

test('Migration rejects oversized records and a malformed registry without hiding omissions',()=>{
 const first=runtime();put(first);const saved=JSON.parse(first.run('test.saved'));saved.v050City.documents[0].document.extra='x'.repeat(262144);let f=cold(JSON.stringify(saved));assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.entries'),0);assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.omissions'),1);saved.v050City.documents={invalid:true};f=cold(JSON.stringify(saved));assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.entries'),0);assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.omissions'),1);
});

test('The building-count budget rejects an additional registration atomically',()=>{
 const first=runtime();put(first);const saved=JSON.parse(first.run('test.saved')),base=clone(saved.v050City.documents[0]);saved.v050City.documents=Array.from({length:32},(_,i)=>{const r=clone(base);r.building.id='occupied-fixture-'+i;r.document.buildingId=r.building.id;return r;});const f=cold(JSON.stringify(saved)),before=f.json('state'),stored=f.run('test.saved');assert.throws(()=>put(f),/32 bâtiments/);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),stored);assert.equal(f.run('d.v050CityInteriorInfo().documentRegistry.entries'),32);
});
