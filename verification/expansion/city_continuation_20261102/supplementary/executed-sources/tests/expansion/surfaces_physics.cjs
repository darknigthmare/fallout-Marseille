#!/usr/bin/env node
'use strict';
// Runs the production bridge resolver and the original movement/jump integrator.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'src/v050/04b_surfaces.js'),'utf8'),core=fs.readFileSync(path.join(root,'src/core-v017.js'),'utf8');
const GIS=require(path.join(root,'src/v046/00_integrity.js'));
const pure=vm.createContext({});vm.runInContext(source.slice(0,source.indexOf('const V050_SURFACES'))+'\nglobalThis.M=MistralSurfaces;',pure);const M=pure.M;
let passed=0;function test(name,fn){fn();passed++;console.log('OK '+name);}
function bridge({id='deck',height=4,width=6,path:line=null,props={}}={}){
 const roadPath=line||[[-10,0,height],[10,0,height]],properties={bridge:'yes',width,...props},mesh=GIS.roadMesh(roadPath,properties,()=>0);
 const{vertices,faces,...profile}=mesh;
 return{mesh:'geoSurface',geoLayer:'transportation',sourceProfile:profile,roadWidth:mesh.width,roadProperties:properties,roadPath,vertices,faces,id,v046GeometryId:id};
}
const floor=4.085;
test('A measured XYZ bridge is admitted',()=>assert.equal(M.measuredBridge(bridge()),true));
test('An absolute source deck altitude is admitted without route Z',()=>assert.equal(M.measuredBridge(bridge({path:[[-10,0],[10,0]],props:{ele:4}})),true));
test('An explicitly measured bridge clearance is admitted',()=>assert.equal(M.measuredBridge(bridge({path:[[-10,0],[10,0]],props:{'bridge:height':4}})),true));
test('A guessed bridge layer never becomes a walking platform',()=>assert.equal(M.measuredBridge(bridge({path:[[-10,0],[10,0]],props:{layer:2}})),false));
test('An ordinary draped road does not change ground physics',()=>assert.equal(M.measuredBridge(bridge({props:{bridge:'no'}})),false));
test('Tunnel geometry is excluded',()=>assert.equal(M.measuredBridge(bridge({props:{tunnel:'yes'}})),false));
test('Rail and non-built routes are excluded',()=>{for(const cls of ['rail','tram','ferry','construction','proposed','abandoned'])assert.equal(M.measuredBridge(bridge({props:{class:cls}})),false);});
test('Invalid widths are excluded',()=>{for(const width of [0,-1,NaN,Infinity,301]){const d=bridge();d.roadWidth=width;assert.equal(M.measuredBridge(d),false);}});
test('A partially measured XYZ route cannot promote guessed segments',()=>assert.equal(M.measuredBridge(bridge({path:[[-10,0,4],[10,0]]})),false));
test('Invalid source Z cannot become measured elevation',()=>assert.equal(M.measuredBridge(bridge({path:[[-10,0,4],[10,0,NaN]]})),false));
test('Barycentric support follows the actual sloped source triangles',()=>{
 const i=new M.DeckIndex([bridge({path:[[0,0,0],[24,0,12]]})]);
 assert.ok(Math.abs(i.support(6,0,4,false).height-3.085)<1e-10);
});
test('The exact mesh edge supports a foot; outside the stroke does not',()=>{
 const i=new M.DeckIndex([bridge()]);assert.ok(i.support(0,3,5));assert.equal(i.support(0,3.001,5),null);
});
test('Shared triangle seams have stable support height',()=>{
 const i=new M.DeckIndex([bridge()]);for(const x of [-10,-5,0,5,10])assert.ok(Math.abs(i.support(x,0,5).height-floor)<1e-10);
});
test('Degenerate and invalid faces cannot introduce a platform',()=>{
 const d=bridge();d.faces=[[0,0,0],[0,1,999],[0,1,NaN]];const i=new M.DeckIndex([d]);assert.equal(i.triangles,0);assert.equal(i.support(0,0,5),null);
});
test('Non-finite vertices cannot introduce a platform',()=>{
 const d=bridge();d.vertices=d.vertices.map(v=>[v[0],Infinity,v[2]]);assert.equal(new M.DeckIndex([d]).triangles,0);
});
test('Source slopes beyond the walking limit are excluded',()=>assert.equal(new M.DeckIndex([bridge({path:[[0,0,0],[10,0,20]]})]).triangles,0));
test('Negative source elevations remain negative',()=>assert.ok(new M.DeckIndex([bridge({height:-5})]).support(0,0,-4,false).height<0));
test('Source geometry and NoData samples remain untouched',()=>{
 const d=bridge(),before=JSON.stringify(d);new M.DeckIndex([d]).support(0,0,6);assert.equal(JSON.stringify(d),before);
 const mesh=GIS.roadMesh([[-10,0,4],[10,0,4]],{bridge:'yes',width:6},()=>null);assert.ok(mesh.faces.length);
});
test('Stacked decks select the highest reachable floor, not an overhead deck',()=>{
 const i=new M.DeckIndex([bridge({id:'lower'}),bridge({id:'upper',height:14})]);assert.ok(Math.abs(i.support(0,0,4.1).height-floor)<1e-10);assert.equal(i.support(0,0,0),null);
});
test('Grounded reach is limited to the existing .72m step',()=>{
 const i=new M.DeckIndex([bridge()]);assert.ok(i.support(0,0,floor-.7,true));assert.equal(i.support(0,0,floor-.8,true),null);
});
test('An airborne reference cannot step onto a floor above its feet',()=>{
 const i=new M.DeckIndex([bridge()]);assert.equal(i.support(0,0,floor-.1,false),null);assert.ok(i.support(0,0,floor+.1,false));
});
test('Invalid references have no support',()=>{const i=new M.DeckIndex([bridge()]);for(const n of [null,undefined,NaN,Infinity])assert.equal(i.support(0,0,n),null);});
test('Duplicate tile representations do not duplicate physical decks',()=>assert.equal(new M.DeckIndex([bridge(),bridge()]).decks,1));
test('The upward head crossing query returns only the first measured plane',()=>{
 const i=new M.DeckIndex([bridge({id:'lower'}),bridge({height:6,id:'upper'})]);assert.equal(i.ceiling(0,0,3,7).height,floor);assert.equal(i.ceiling(0,0,5,3),null);
});

function sandbox({draws=[bridge()],dem=()=>0,feet=0,x=0,z=0}={}){
 const noop=()=>{},context=vm.createContext({console,Map,WeakMap,Set,world:{v046:true,id:'geo_huveaune',bounds:[-100,100,-100,100],hazards:[],v046Records:new Map([['tile',{roads:draws}]])},
  state:{player:{pos:[x,feet+1.65,z],ap:100,maxAp:100,crouched:false,yaw:0},character:{trait:''},perks:{},weather:{type:'clear'},status:{},worldTime:12,playTime:0},
  mode:'PLAYING',gameStarted:true,zoneTransitioning:false,V018:{qaFreeze:false},onGround:true,jumpVelocity:0,bobPhase:0,reloadTimer:0,weaponKick:0,autosaveTimer:0,inCombat:false,
  keys:new Set(),touchMove:{x:0,y:0},isBoatZone:()=>false,pollGamepad:()=>({x:0,y:0,sprint:false}),clamp:(n,a,b)=>Math.max(a,Math.min(b,n)),
  playerEyeHeight:()=>1.65,collidesAt:()=>false,groundHeightAt:(x,z)=>dem(x,z)??0,v047Height:(_bank,x,z)=>({height:dem(x,z)}),v047Bank:()=>({}),
  updateStatus:noop,updateNPCSchedules:noop,updateSelectedInteractable:noop,updateLootProximity:noop,updateCompanion:noop,updateEnemies:noop,updateRoux:noop,updateWeather:noop,saveGame:noop,
  audio:{tone:noop},window:{__MISTRAL_DEBUG:{}}
 });
 vm.runInContext(core.slice(core.indexOf('function tryPlayerMove('),core.indexOf('function tryEnemyMove(')),context);
 vm.runInContext(core.slice(core.indexOf('function updatePlayer(dt)'),core.indexOf('function toggleCrouch(')),context);
 vm.runInContext(source,context);return context;
}
test('Walking beneath an overhead bridge preserves the baseline ground',()=>{
 const c=sandbox();assert.equal(c.groundHeightAt(0,0,0),0);c.updatePlayer(.1);assert.equal(c.state.player.pos[1],1.65);assert.equal(c.onGround,true);
});
test('A reachable measured approach lifts the player by the true ramp height',()=>{
 const c=sandbox({draws:[bridge({path:[[0,0,0],[20,0,4]]})],x:-.5});c.tryPlayerMove(.6,0);
 assert.ok(Math.abs(c.state.player.pos[0]-.1)<1e-10);assert.ok(Math.abs(c.state.player.pos[1]-1.755)<1e-10);
});
test('Stepping along a source slope follows its barycentric deck',()=>{
 const c=sandbox({draws:[bridge({path:[[0,0,0],[20,0,4]]})],x:5,feet:1.085});c.tryPlayerMove(.5,0);
 assert.ok(Math.abs(c.state.player.pos[1]-1.65-1.185)<1e-10);assert.equal(c.onGround,true);
});
test('Leaving the deck edge initiates the original fall without vertical teleportation',()=>{
 const c=sandbox({feet:floor,x:9.9});c.tryPlayerMove(.2,0);
 assert.equal(c.onGround,false);assert.ok(Math.abs(c.state.player.pos[1]-1.65-floor)<1e-10);
});
test('The production integrator lands a falling body on the measured deck',()=>{
 const c=sandbox({feet:6});c.onGround=false;c.jumpVelocity=-3;c.updatePlayer(.4);
 assert.equal(c.onGround,true);assert.ok(Math.abs(c.state.player.pos[1]-1.65-floor)<1e-10);assert.equal(c.jumpVelocity,0);
});
test('Rising from below cannot snap a foot up to the overhead bridge',()=>{
 const c=sandbox({feet:floor-.2});c.onGround=false;c.jumpVelocity=1;c.updatePlayer(.01);
 assert.equal(c.onGround,false);assert.ok(c.state.player.pos[1]-1.65<floor);
});
test('A jump from beneath stops its head at the source plane and never arrives above it',()=>{
 const c=sandbox({feet:1.8});c.onGround=false;c.jumpVelocity=5;c.updatePlayer(.2);
 assert.equal(c.onGround,false);assert.equal(c.jumpVelocity,0);assert.ok(Math.abs(c.state.player.pos[1]+.18-(floor-.001))<1e-10);assert.ok(c.state.player.pos[1]-1.65<floor);
});
test('Jumping from an existing deck retains airborne motion until landing',()=>{
 const c=sandbox({feet:floor});c.jump();c.updatePlayer(.1);
 assert.equal(c.onGround,false);assert.ok(c.state.player.pos[1]-1.65>floor);assert.ok(c.jumpVelocity>0);
 for(let i=0;i<20;i++)c.updatePlayer(.1);
 assert.equal(c.onGround,true);assert.ok(Math.abs(c.state.player.pos[1]-1.65-floor)<1e-10);
});
test('A retired deck falls to the original lower terrain instead of snapping down',()=>{
 const c=sandbox({feet:floor});c.updatePlayer(.01);
 c.world.v046Records=new Map();c.updatePlayer(.1);
 assert.equal(c.onGround,false);assert.ok(c.state.player.pos[1]-1.65>0);assert.ok(c.state.player.pos[1]-1.65<floor);
});
test('Publishing a replacement deck invalidates the physical index',()=>{
 const c=sandbox({feet:floor});assert.ok(Math.abs(c.groundHeightAt(0,0,floor)-floor)<1e-10);
 c.world.v046Records=new Map([['new',{roads:[bridge({height:14})]}]]);assert.equal(c.groundHeightAt(0,0,floor),0);
});
test('Measured support over DEM NoData does not fill the underlying bank',()=>{
 let calls=0;const c=sandbox({feet:floor,dem:()=>{calls++;return null;}});
 assert.ok(Math.abs(c.groundHeightAt(0,0,floor)-floor)<1e-10);assert.equal(c.v047Height({},0,0).height,null);assert.ok(calls>0);
});
test('An unmeasured bridge preserves the exact ordinary-ground integrator',()=>{
 const d=bridge({path:[[-10,0],[10,0]],props:{layer:2}}),c=sandbox({draws:[d],dem:()=>2,feet:2});
 c.updatePlayer(.1);assert.equal(c.state.player.pos[1],3.65);assert.equal(c.onGround,true);
});
test('Non-geographic worlds preserve baseline ground physics',()=>{
 const c=sandbox({dem:()=>3,feet:3});c.world.v046=false;c.updatePlayer(.1);assert.equal(c.state.player.pos[1],4.65);
});
test('Paused simulation does not move a supported player',()=>{
 const c=sandbox({feet:floor});c.mode='PAUSE';const before=c.state.player.pos.slice();c.updatePlayer(.5);assert.deepEqual(c.state.player.pos,before);
});
console.log(JSON.stringify({suite:'surfaces_physics',passed,failed:0}));
