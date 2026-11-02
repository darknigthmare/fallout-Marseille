#!/usr/bin/env node
'use strict';
// The water polygons below are explicitly synthetic. Support tests use the
// production bridge resolver and the production walking integrator unchanged.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'src/v050/04ab_city_water_physics.js'),'utf8');
const M=require('../../src/v050/04ab_city_water_physics.js'),GIS=require('../../src/v046/00_integrity.js');
const bridgeSource=fs.readFileSync(path.join(root,'src/v050/04b_surfaces.js'),'utf8'),core=fs.readFileSync(path.join(root,'src/core-v017.js'),'utf8');
const water=()=>({rings:[[[-10,-10],[10,-10],[10,10],[-10,10],[-10,-10]]],geoProperties:{v051Water:true}});
let passed=0;function test(name,run){run();passed++;console.log('OK '+name);}
test('A source water polygon is blocked independently of its elevation',()=>assert.equal(M.blocked({exterior:true,water:true}),true));
test('Dry land is never classified from elevation zero or missing terrain',()=>{assert.equal(M.blocked({exterior:true,water:false}),false);assert.equal(M.blocked({exterior:true}),false);});
test('Only real measured supports bypass the water boundary',()=>{for(const deck of [true,0,{height:2},{height:2,measured:false},{height:NaN,measured:true}])assert.equal(M.blocked({exterior:true,water:true,deck}),true);assert.equal(M.blocked({exterior:true,water:true,deck:{height:2,measured:true}}),false);});
test('Measured roof support is admitted using the same strict contract',()=>assert.equal(M.blocked({exterior:true,water:true,roof:{height:7,measured:true}}),false));
test('Historical interiors, laboratories and actual vehicle scenes are exempt',()=>{for(const flags of [{exterior:false},{exterior:true,lab:true},{exterior:true,vehicle:true}])assert.equal(M.blocked({water:true,...flags}),false);});
test('Polygon classification preserves a dry courtyard hole',()=>{const d=water();d.rings.push([[-2,-2],[-2,2],[2,2],[2,-2],[-2,-2]]);const records=new Map([['source',{water:[d]}]]);assert.equal(M.waterAt({x:0,z:0,records,inside:GIS.inside}),false);assert.equal(M.waterAt({x:5,z:0,records,inside:GIS.inside}),true);});
test('Unflagged existing source water is affected only inside the municipal extent',()=>{const d=water();d.geoProperties={};const records=new Map([['source',{water:[d]}]]);assert.equal(M.waterAt({x:0,z:0,records,inside:GIS.inside,inExtent:()=>false}),false);assert.equal(M.waterAt({x:0,z:0,records,inside:GIS.inside,inExtent:()=>true}),true);});
test('An explicitly acquired water polygon keeps its full verified border outside the commune',()=>assert.equal(M.waterAt({x:0,z:0,records:new Map([['source',{water:[water()]}]]),inside:GIS.inside,inExtent:()=>false}),true));
test('The spatial index excludes land records before polygon classification',()=>{let calls=0;const records=new Map();records.v047Index={surface:{at:()=>[{type:'land',draw:water()},{type:'water',draw:water()}]}};assert.equal(M.waterAt({x:0,z:0,records,inside:(...args)=>{calls++;return GIS.inside(...args);}}),true);assert.equal(calls,1);});
test('Missing source geometry or invalid coordinates do not fabricate water',()=>{assert.equal(M.waterAt({x:0,z:0,records:new Map(),inside:GIS.inside}),false);assert.equal(M.waterAt({x:NaN,z:0,records:new Map([['source',{water:[water()]}]]),inside:GIS.inside}),false);});

function sandbox({draws=[],dem=()=>0,feet=0,x=-11,z=0,lab=false,exterior=true,vehicle=false,blocked=false}={}){
 const noop=()=>{},context=vm.createContext({console,Map,WeakMap,Set,world:{v046:exterior,id:'geo_marseille_commune',vehicleMode:vehicle?'boat':undefined,bounds:[-100,100,-100,100],hazards:[],v046Records:new Map([['tile',{roads:draws,water:[water()],land:[]}]])},
  state:{player:{pos:[x,feet+1.65,z],ap:100,maxAp:100,crouched:false,yaw:0},character:{trait:''},perks:{},weather:{type:'clear'},status:{},worldTime:12,playTime:0},
  mode:'PLAYING',gameStarted:true,zoneTransitioning:false,V018:{qaFreeze:false},V046:{lab},onGround:true,jumpVelocity:0,bobPhase:0,reloadTimer:0,weaponKick:0,autosaveTimer:0,inCombat:false,
  keys:new Set(),touchMove:{x:0,y:0},isBoatZone:()=>vehicle,pollGamepad:()=>({x:0,y:0,sprint:false}),clamp:(n,a,b)=>Math.max(a,Math.min(b,n)),
  playerEyeHeight:()=>1.65,collidesAt:()=>blocked,groundHeightAt:(x,z)=>dem(x,z)??0,v047Height:(_bank,x,z)=>({height:dem(x,z)}),v047Bank:()=>({}),MistralIntegrity:GIS,
  V051_CITY_BOUNDS:[43.1,5.2,43.4,5.6],v015GeoUnproject:()=>[43.3,5.3],
  updateStatus:noop,updateNPCSchedules:noop,updateSelectedInteractable:noop,updateLootProximity:noop,updateCompanion:noop,updateEnemies:noop,updateRoux:noop,updateWeather:noop,saveGame:noop,
  audio:{tone:noop},window:{__MISTRAL_DEBUG:{}}
 });
 vm.runInContext(core.slice(core.indexOf('function tryPlayerMove('),core.indexOf('function tryEnemyMove(')),context);
 vm.runInContext(core.slice(core.indexOf('function updatePlayer(dt)'),core.indexOf('function toggleCrouch(')),context);
 vm.runInContext(source,context);vm.runInContext(bridgeSource,context);return context;
}
function bridge({height=4,props={}}={}){const roadPath=[[-20,0,height],[20,0,height]],p={bridge:'yes',width:6,...props},mesh=GIS.roadMesh(roadPath,p,()=>0),{vertices,faces,...profile}=mesh;return{mesh:'geoSurface',geoLayer:'transportation',sourceProfile:profile,roadWidth:mesh.width,roadProperties:p,roadPath,vertices,faces,id:'measured-bridge',v046GeometryId:'measured-bridge'};}
test('The actual walking integrator cannot enter surveyed water over valid zero terrain',()=>{const c=sandbox();c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-11);assert.equal(c.state.player.pos[1],1.65);});
test('The same original integrator walks normally over dry zero terrain',()=>{const c=sandbox({x:-20});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-18);});
test('A measured bridge allows the original walking integrator across water',()=>{const d=bridge(),floor=4.085,c=sandbox({draws:[d],feet:floor,x:-11});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-9);assert.ok(Math.abs(c.state.player.pos[1]-1.65-floor)<1e-9);});
test('An overhead measured bridge cannot make the water below walkable',()=>{const c=sandbox({draws:[bridge()]});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-11);});
test('A guessed bridge layer cannot bypass the surveyed water boundary',()=>{const d=bridge({props:{ele:undefined}});d.sourceProfile.elevationAssumed=true;d.roadPath=d.roadPath.map(p=>p.slice(0,2));const c=sandbox({draws:[d]});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-11);});
test('Even an actual support cannot weaken an existing wall collision',()=>{const c=sandbox({draws:[bridge()],feet:4.085,blocked:true});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-11);});
test('The laboratory keeps its controlled historical movement behavior',()=>{const c=sandbox({lab:true});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-9);});
test('Historical indoor movement is unchanged by municipal water guards',()=>{const c=sandbox({exterior:false});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-9);});
test('The production boat API retains the existing vehicle movement behavior',()=>{const c=sandbox({vehicle:true});c.tryPlayerMove(2,0);assert.equal(c.state.player.pos[0],-9);});
test('A source water polygon never changes the measured height bank or rings',()=>{const c=sandbox(),before=JSON.stringify(c.world.v046Records.get('tile').water);c.collidesAt(0,0,.38,1.65);assert.equal(JSON.stringify(c.world.v046Records.get('tile').water),before);assert.equal(c.groundHeightAt(0,0),0);});
test('Measured roof support preserves the exterior collision resolver contract',()=>{const c=sandbox();c.v050RoofSupport=()=>({height:3,measured:true});assert.equal(c.collidesAt(0,0,.38,4.65),false);});
test('Unmeasured roof markers cannot make water solid',()=>{const c=sandbox();c.v050RoofSupport=()=>({height:3,measured:false});assert.equal(c.collidesAt(0,0,.38,4.65),true);});
test('The roof collision context provides the exact crouched actor feet',()=>{const c=sandbox({x:0});c.V050_ROOFS={actorEye:1,body:{feet:4}};let foot=null;c.v050DeckSupport=(_x,_z,feet)=>{foot=feet;return{height:4,measured:true};};assert.equal(c.collidesAt(0,0,.32,5),false);assert.equal(foot,4);});
test('Airborne actors cannot step up onto a higher platform through the water guard',()=>{const c=sandbox({x:0});c.V050_ROOFS={actorEye:1.65,body:{feet:4}};c.onGround=false;let step=null;c.v050DeckSupport=(_x,_z,_feet,allow)=>{step=allow;return null;};c.collidesAt(0,0,.38,5.65);assert.equal(step,false);});
console.log(JSON.stringify({passed,failed:0,scope:'Production municipal non-swimmable water boundary, original walking integrator and real bridge support model; explicitly synthetic water/terrain fixtures'}));
