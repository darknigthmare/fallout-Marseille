'use strict';
/* Execute the shipped field-life module, including its production guards and
   transactions. Geometry/provider seams are controlled here; native map tests
   separately exercise the real PBFs, terrain bank and browser storage. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../../src/v050/05_wasteland.js'), 'utf8');
let passed = 0;
function fixture() {
 const context = vm.createContext({console});
 vm.runInContext(`
 const TAU=Math.PI*2,clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 const deepClone=o=>JSON.parse(JSON.stringify(o)),dist2=(a,b)=>Math.hypot(a[0]-b[0],a[2]-b[2]);
 const test={ground:()=>10,blocked:()=>false,failSave:false,throwSave:false,sight:true,saves:0,saved:null};
 const V042_CATALOG=[{id:'safe-relay',safe:true,kind:'settlement',name:'Relais test',macro:'geo_huveaune',faction:'ateliers',factionLabel:'Ateliers'},
 {id:'hostile-site',safe:false,kind:'outpost',name:'Hostile',faction:'concorde'},
 {id:'second-relay',safe:true,kind:'caravan',name:'Caravane',macro:'geo_huveaune',faction:'ligue'}];
 const V015_GEO_MACROS={geo_huveaune:{name:'Aubagne'}};
 function baseState(){return{player:{pos:[0,11.65,0],zone:'geo_huveaune',yaw:0,hp:40,maxHp:100,ap:5,maxAp:90,rad:25,caps:0},
  inventory:{scrap:10,cloth:10,food:10,water:10,ration:5,stimpak:2,chemicals:4,ceramicFilter:2},rep:{},needs:{hunger:70,thirst:70,fatigue:80},
  worldTime:23,v020:{restHours:0},status:{infection:0,bleeding:0,burning:0},v042:{discovered:{'safe-relay':true,'second-relay':true}},lastSave:null};}
 function migrateState(s={}){return deepClone(s.player?s:baseState());}
 let state=baseState(),mode='PIP',gameStarted=true,zoneTransitioning=false,onGround=true;
 let world={id:'geo_huveaune',v046:true,geoMacro:true,v046Records:new Map(),v047TerrainBank:{},colliders:[],interactables:[],
  enemies:[],npcs:[{alive:true,v042Site:'safe-relay',pos:[0,10,1]}]};
 const V046={lab:false,busy:false,terrain:{}},V047={pending:null},V027={ready:true,message:'',sub:'camp'};
 const V027_SUBS={status:{},data:{}},COLORS={clothTan:[.4,.4,.2],darkMetal:[.2,.2,.2]};
 const V020_RECIPES=[{id:'ration',name:'Deux rations',cost:{food:4,water:1},item:'ration',count:2},
 {id:'purify',name:'Filtrer eau',cost:{chemicals:1,ceramicFilter:1},item:'water',count:4},
 {id:'bandage',name:'Pansement',cost:{cloth:3,chemicals:1},item:'stimpak',count:1},
 {id:'10mm',name:'Munitions',cost:{scrap:3,chemicals:2},item:'ammo10',count:10}];
 const window={__MISTRAL_DEBUG:{}};
 function v046Region(lat,lon){return lat>=43.245&&lat<=43.335&&lon>=5.43&&lon<=5.64?'geo_huveaune':null;}
 function v015GeoUnproject(id,x,z){return[43.2966-z/110540,5.5708+x/81000];}
 function v015GeoProject(id,lat,lon){return[(lon-5.5708)*81000,0,(43.2966-lat)*110540];}
 function v046HeightAt(x,z){return{height:test.ground(x,z)};}
 function v050TravelGround(stage,w,x,z){return test.ground(x,z);}
 function v046Blocked(w,x,z){return test.blocked(x,z);}
 function v050TravelNearbyThreat(){return world.enemies.some(e=>e.alive&&dist2(e.pos,state.player.pos)<40);}
 function playerEyeHeight(){return 1.65;}
 function v027CanAct(){return mode==='PIP'&&gameStarted&&!zoneTransitioning&&state.player.hp>0;}
 function hasCost(cost){return Object.entries(cost).every(([id,n])=>(id==='caps'?state.player.caps:state.inventory[id]||0)>=n);}
 function v020Spend(cost){if(!hasCost(cost))return false;for(const[id,n]of Object.entries(cost)){if(id==='caps')state.player.caps-=n;else state.inventory[id]-=n;}return true;}
 function saveGame(){test.saves++;if(test.throwSave)throw Error('disk full');if(test.failSave)return false;test.saved=JSON.stringify(state);return true;}
 function v027Notify(message){V027.message=message;return false;}
 function v042Site(id){return V042_CATALOG.find(s=>s.id===id)||null;}
 function v042SiteDiscovered(s){return!!state.v042.discovered[s.id];}
 function lineOfSight(){return test.sight;}
 function v049Own(){}function toast(){}function renderPipboy(){}function v027Open(){}
 function addInteract(w,id,pos,label,onInteract,options){w.interactables.push({id,pos,label,onInteract,...options});}
 function addBox(w,pos,scale,color,rotY){w.staticDraws.push({mesh:'cube',pos,scale,color,rotY});}
 function addPart(w,mesh,pos,scale,color){w.staticDraws.push({mesh,pos,scale,color});}
 function v046Publish(){}function updatePlayer(){}function collectDraws(){return[];}
 function v027Status(c){c.innerHTML='previous status';}function v027Data(c){c.innerHTML='previous data';}
 function v027Dispatch(){return 'legacy dispatch';}
 function escapeHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
 function v027Button(label,action,arg,disabled){return '<button data-p27="'+action+'" data-arg="'+arg+'"'+(disabled?' disabled':'')+'>'+label+'</button>';}
 function v020HtmlCost(cost){return Object.entries(cost).map(([k,v])=>k+' '+v).join(', ');}
 function v020Label(id){return id;}
 `, context);
 vm.runInContext(source, context, {filename:'05_wasteland.js'});
 return {run: code => vm.runInContext(code, context), json: code => JSON.parse(JSON.stringify(vm.runInContext(code, context)))};
}
function check(name, body) { body();passed++;console.log('OK '+name); }
check('Old saves receive no free kit or materials',()=>{const f=fixture();assert.equal(f.run('state.v050Wasteland.kitOwned'),false);assert.equal(f.run('state.v050Wasteland.camp'),null);assert.equal(f.run('state.inventory.scrap'),10);});
check('Kit spends its complete construction cost once',()=>{const f=fixture();assert.equal(f.run('v050CampPlace()'),true);assert.equal(f.run('state.inventory.scrap'),7);assert.equal(f.run('state.inventory.cloth'),9);assert.equal(f.run('state.v050Wasteland.kitOwned'),true);assert.equal(f.run('state.v050Wasteland.camp.macro'),'geo_huveaune');assert.equal(f.run('test.saves'),1);});
check('Visible camp and physical interaction are created',()=>{const f=fixture();f.run('v050CampPlace()');assert.equal(f.run('collectDraws(0).length'),3);assert.equal(f.run("world.interactables.filter(i=>i.id==='v050-camp').length"),1);f.run('v050CampBind();v050CampBind()');assert.equal(f.run("world.interactables.filter(i=>i.id==='v050-camp').length"),1);});
check('Already deployed kit cannot be duplicated',()=>{const f=fixture();f.run('v050CampPlace()');const before=f.json('state');assert.equal(f.run('v050CampPlace()'),false);assert.deepEqual(f.json('state'),before);});
check('Packing retains exactly one reusable kit and removes its scene props',()=>{const f=fixture();f.run('v050CampPlace()');assert.equal(f.run('v050CampPack()'),true);assert.equal(f.run('state.v050Wasteland.camp'),null);assert.equal(f.run('state.v050Wasteland.kitOwned'),true);assert.equal(f.run('collectDraws(0).length'),0);assert.equal(f.run('world.interactables.length'),0);assert.equal(f.run('v050CampPlace()'),true);assert.equal(f.run('state.inventory.scrap'),7);assert.equal(f.run('state.inventory.cloth'),9);});
check('Distant kit cannot be recalled or used for free rest',()=>{const f=fixture();f.run('v050CampPlace();state.player.pos[0]=100');const before=f.json('state');assert.equal(f.run('v050CampPack()'),false);assert.equal(f.run('v050CampRest(4)'),false);assert.deepEqual(f.json('state'),before);});
for(const [name,setup] of [
 ['no measured altitude','test.ground=()=>null'],['steep footprint','test.ground=(x,z)=>Math.abs(x)*10'],['road or solid footprint','test.blocked=()=>true'],
 ['insufficient complete kit resources','state.inventory.cloth=0'],['combat','world.enemies=[{alive:true,pos:[0,10,10]}]'],
 ['nearby unalerted enemy','world.enemies=[{alive:true,pos:[0,10,50]}]'],['loading','V047.pending={}'],['narrative interior','world.v046=false'],
 ['lab isolation','V046.lab=true'],['closed Pip-Boy','mode="PLAYING"'],['dead player','state.player.hp=0']
 ,['airborne player','onGround=false'],['player over an unmeasured hole','test.ground=()=>null'],['floating camera','state.player.pos[1]+=5']
])check('Placement refuses '+name+' without payment',()=>{const f=fixture();f.run(setup);const before=f.json('state');assert.equal(f.run('v050CampPlace()'),false);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saves'),0);});
check('Failed persistent write rolls construction back',()=>{const f=fixture();f.run('test.failSave=true');const before=f.json('state');assert.equal(f.run('v050CampPlace()'),false);assert.deepEqual(f.json('state'),before);assert.equal(f.run('world.interactables.length'),0);});
check('Storage exception also rolls construction back',()=>{const f=fixture();f.run('test.throwSave=true');const before=f.json('state');assert.equal(f.run('v050CampPlace()'),false);assert.deepEqual(f.json('state'),before);});
check('Camp migration validates source coordinate bounds and kit ownership',()=>{const f=fixture();assert.equal(f.run('v050WastelandMigrate({kitOwned:false,camp:{lat:43.3,lon:5.5}}).camp'),null);assert.equal(f.run('v050WastelandMigrate({kitOwned:true,camp:{lat:91,lon:5}}).camp'),null);assert.equal(f.run('v050WastelandMigrate({kitOwned:true,camp:{lat:43.3,lon:5.5,yaw:Infinity}}).camp.yaw'),0);});
check('Camp, exact resources and ledger survive JSON save migration',()=>{const f=fixture();f.run("v050CampPlace();v050AidDeliver('safe-relay','water');state=migrateState(JSON.parse(test.saved));v049Own(world)");assert.equal(f.run('state.v050Wasteland.kitOwned'),true);assert.equal(f.run('state.v050Wasteland.aid["safe-relay"].water'),true);assert.equal(f.run('state.inventory.scrap'),7);assert.equal(f.run('state.inventory.water'),8);assert.equal(f.run('v050CampNear()'),true);});
check('Rest uses finite supplies, advances time once, preserves rads and wounds',()=>{const f=fixture();f.run('v050CampPlace()');assert.equal(f.run('v050CampRest(4)'),true);assert.equal(f.run('state.inventory.water'),9);assert.equal(f.run('state.inventory.ration'),4);assert.equal(f.run('state.worldTime'),3);assert.equal(f.run('state.player.hp'),88);assert.equal(f.run('state.player.ap'),90);assert.equal(f.run('state.player.rad'),25);assert.equal(f.run('state.needs.fatigue'),0);assert.equal(f.run('state.v050Wasteland.restHours'),4);});
check('Invalid rest durations cannot alter time or supplies',()=>{const f=fixture();f.run('v050CampPlace()');const before=f.json('state');for(const arg of [0,-1,2,24,NaN,Infinity])assert.equal(f.run(`v050CampRest(${arg})`),false);assert.deepEqual(f.json('state'),before);});
check('Active infection prevents outdoor sleeping',()=>{const f=fixture();f.run('v050CampPlace();state.status.infection=10');const before=f.json('state');assert.equal(f.run('v050CampRest(1)'),false);assert.deepEqual(f.json('state'),before);});
check('Incomplete rest supplies cause no partial cost',()=>{const f=fixture();f.run('v050CampPlace();state.inventory.ration=0');const before=f.json('state');assert.equal(f.run('v050CampRest(4)'),false);assert.deepEqual(f.json('state'),before);});
check('Failed save rolls elapsed time, health, fatigue and ingredients back',()=>{const f=fixture();f.run('v050CampPlace();test.failSave=true');const before=f.json('state');assert.equal(f.run('v050CampRest(4)'),false);assert.deepEqual(f.json('state'),before);});
check('Field cooking uses actual recipe costs and quantities',()=>{const f=fixture();f.run('v050CampPlace()');assert.equal(f.run('v050CampCraft("ration")'),true);assert.equal(f.run('state.inventory.food'),6);assert.equal(f.run('state.inventory.water'),9);assert.equal(f.run('state.inventory.ration'),7);assert.equal(f.run('state.v050Wasteland.crafts'),1);});
check('Portable camp cannot manufacture workshop ammunition',()=>{const f=fixture();f.run('v050CampPlace()');const before=f.json('state');assert.equal(f.run('v050CampCraft("10mm")'),false);assert.deepEqual(f.json('state'),before);});
check('Camp services recheck road/solid conflicts after terrain publication',()=>{const f=fixture();f.run('v050CampPlace();test.blocked=()=>true');const before=f.json('state');assert.equal(f.run('v050CampRest(1)'),false);assert.equal(f.run('v050CampCraft("ration")'),false);assert.deepEqual(f.json('state'),before);});
check('Camp services require an unobstructed physical access',()=>{const f=fixture();f.run('v050CampPlace();test.sight=false');const before=f.json('state');assert.equal(f.run('v050CampRest(1)'),false);assert.equal(f.run('v050CampCraft("ration")'),false);assert.deepEqual(f.json('state'),before);});
check('Purification failure cannot consume only its first ingredient',()=>{const f=fixture();f.run('v050CampPlace();state.inventory.ceramicFilter=0');const before=f.json('state');assert.equal(f.run('v050CampCraft("purify")'),false);assert.deepEqual(f.json('state'),before);});
check('Aid requires an alive, discovered and visible recipient nearby',()=>{for(const setup of ['world.npcs=[]','world.npcs[0].alive=false','world.npcs[0].pos[0]=20','state.v042.discovered={}','test.sight=false']){const f=fixture();f.run(setup);const before=f.json('state');assert.equal(f.run("v050AidDeliver('safe-relay','water')"),false);assert.deepEqual(f.json('state'),before);}});
check('Aid consumes finite supplies and rewards the associated faction',()=>{const f=fixture();assert.equal(f.run("v050AidDeliver('safe-relay','water')"),true);assert.equal(f.run('state.inventory.water'),8);assert.equal(f.run('state.player.caps'),10);assert.equal(f.run('state.rep.artisans'),1);assert.equal(f.run('state.v050Wasteland.aid["safe-relay"].water'),true);});
check('An aid delivery cannot be rewarded twice, including after reload',()=>{const f=fixture();f.run("v050AidDeliver('safe-relay','water');state=migrateState(JSON.parse(test.saved))");const before=f.json('state');assert.equal(f.run("v050AidDeliver('safe-relay','water')"),false);assert.deepEqual(f.json('state'),before);});
check('Aid categories are distinct finite needs, never an infinite contract',()=>{const f=fixture();for(const id of ['water','food','medicine'])assert.equal(f.run(`v050AidDeliver('safe-relay','${id}')`),true);assert.equal(f.run('state.player.caps'),36);assert.equal(f.run('state.rep.artisans'),4);assert.equal(f.run('Object.keys(state.v050Wasteland.aid["safe-relay"]).length'),3);});
check('Hostile and fabricated relay IDs cannot grant aid rewards',()=>{for(const id of ['hostile-site','unknown','__proto__']){const f=fixture();const before=f.json('state');assert.equal(f.run(`v050AidDeliver('${id}','water')`),false);assert.deepEqual(f.json('state'),before);}});
check('Unknown aid types cannot spend arbitrary inventory',()=>{const f=fixture();const before=f.json('state');for(const type of ['unknown','constructor','__proto__'])assert.equal(f.run(`v050AidDeliver('safe-relay','${type}')`),false);assert.deepEqual(f.json('state'),before);});
check('Insufficient medicine causes neither partial payment nor faction gains',()=>{const f=fixture();f.run('state.inventory.cloth=0');const before=f.json('state');assert.equal(f.run("v050AidDeliver('safe-relay','medicine')"),false);assert.deepEqual(f.json('state'),before);});
check('Aid persistence failure rolls ledger, resources, caps and reputation back',()=>{const f=fixture();f.run('test.failSave=true');const before=f.json('state');assert.equal(f.run("v050AidDeliver('safe-relay','water')"),false);assert.deepEqual(f.json('state'),before);});
check('Migration keeps only known safe sites and exact boolean receipts',()=>{const f=fixture();assert.deepEqual(f.json(`v050WastelandMigrate({kitOwned:'yes',restHours:-7,crafts:Infinity,aid:{'safe-relay':{water:true,food:1,medicine:false,extra:true},'hostile-site':{water:true},unknown:{food:true}}})`),{schema:1,kitOwned:false,camp:null,restHours:0,crafts:0,aid:{'safe-relay':{water:true}}});});
check('Pip-Boy pages expose production actions and existing tabs are preserved',()=>{const f=fixture();f.run('v050WastelandAfterInit();var panel={innerHTML:""};v027Status(panel)');assert.match(f.run('panel.innerHTML'),/w50:pitch/);assert.equal(f.run('V027_SUBS.status.camp'),'BIVOUAC');assert.equal(f.run('V027_SUBS.data.aid'),'ENTRAIDE');assert.equal(f.run('v027Dispatch("legacy")'),'legacy dispatch');f.run('V027.sub="aid";v027Data(panel)');assert.match(f.run('panel.innerHTML'),/safe-relay\|water/);});
check('Panel dispatch uses the same guarded functions as physical gameplay',()=>{const f=fixture();assert.equal(f.run('v027Dispatch("w50:pitch")'),true);f.run('mode="MENU"');const before=f.json('state');assert.equal(f.run('v027Dispatch("w50:rest","4")'),false);assert.deepEqual(f.json('state'),before);});
console.log(JSON.stringify({passed,failed:0,total:passed,scope:'Production field-life module with controlled geometry, session and persistence seams'}));
