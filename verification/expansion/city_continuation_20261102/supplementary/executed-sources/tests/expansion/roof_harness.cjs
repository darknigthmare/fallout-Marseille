'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..');
function script(){
 const core=fs.readFileSync(path.join(root,'src/core-v017.js'),'utf8'),patch=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8'),geo=fs.readFileSync(path.join(root,'src/v046/01_world.js'),'utf8');
 let out=`
 const noop=()=>{},TAU=Math.PI*2,COLORS={white:[1,1,1],plaster:[.6,.6,.6],limestone:[.5,.5,.5],roof:[.4,.2,.2]},clamp=(n,a,b)=>Math.max(a,Math.min(b,n)),cMix=(a,b,t)=>a.map((v,i)=>v+(b[i]-v)*t),detailHash=()=>1;
 let world,state,mode='PLAYING',gameStarted=true,zoneTransitioning=false,onGround=true,jumpVelocity=0,bobPhase=0,reloadTimer=0,weaponKick=0,autosaveTimer=0,inCombat=false;
 const keys=new Set(),touchMove={x:0,y:0},audio={tone:noop};
 const isBoatZone=()=>false,pollGamepad=()=>({x:0,y:0,sprint:false});
 const playerEyeHeight=()=>state.player.crouched?1.18:1.65,v047Height=()=>({height:0}),v047Bank=()=>({}),v015GeoUnproject=()=>[0,0];
 const updateStatus=noop,updateNPCSchedules=noop,updateSelectedInteractable=noop,updateLootProximity=noop,updateCompanion=noop,updateEnemies=noop,updateRoux=noop,updateWeather=noop,saveGame=noop;
 function groundHeightAt(){return 0;}
 `;
 out+=core.slice(core.indexOf('function v3('),core.indexOf('function m4('));
 out+=core.slice(core.indexOf('function flatMesh('),core.indexOf('function cubeData('));
 for(const name of ['v017SignedArea','v017PolyBounds','v017AddPrism','v017PointInPoly','v017PointSegDist','v017ColliderHit','collidesAt','rayAABB','firstObstacle','lineOfSight']){
  const lines=core.split('\n').filter(line=>line.startsWith('function '+name+'('));
  out+='\n'+(name==='collidesAt'?lines.at(-1):lines[0]);
 }
 out+='\nconst V017_PRISM_BASE=v017AddPrism,V017_RAY_AABB_BASE=rayAABB;';
 out+=patch.slice(0,patch.indexOf('const v018OriginalGLRender'));
 out+=patch.slice(patch.indexOf('v017AddPolyCollider=function'),patch.indexOf('SoftwareRenderer.prototype.render=function'));
 out+=fs.readFileSync(path.join(root,'src/v046/00_integrity.js'),'utf8');
 out+='\nconst V046={terrain:{read:()=>({height:0})}};';
 out+=geo.slice(geo.indexOf('function v046SourceBuilding('),geo.indexOf('function v046Import('));
 out+=core.slice(core.indexOf('function tryPlayerMove('),core.indexOf('function tryEnemyMove('));
 out+=core.slice(core.indexOf('function updatePlayer(dt)'),core.indexOf('function toggleCrouch('));
 out+=fs.readFileSync(path.join(root,'src/v050/04b_surfaces.js'),'utf8');
 out+=fs.readFileSync(path.join(root,'src/v050/04c_roof_collisions.js'),'utf8');
 out+=`
 function roofFixture(options={}){
  const rings=options.rings||[[[0,0],[20,0],[20,20],[0,20],[0,0]]];
  const w={v046:true,id:'geo_huveaune',staticDraws:[],colliders:[],bounds:[-100,100,-100,100],hazards:[],v046Records:new Map()};
  const props={height:12,ground_elevation:0,'roof:height':3,'roof:shape':'gabled','roof:direction':90,provenance:{source:'Declared roof test fixture',license:'CC0',attribution:'Test',acquiredAt:'2026-10-23'},...options.props};
  for(const key of options.omit||[])delete props[key];
  const body=v046SourceBuilding(w,rings,{id:'survey-building',props,v050Source:true},'fixture-tile');
  w.v046Records=new Map([['fixture-tile',{roads:[],draws:w.staticDraws,colliders:w.colliders}]]);
  return{w,body,cap:w.staticDraws.find(d=>d.geoLayer==='roof'),collider:w.colliders[0],solid:w.colliders[0]?.v050RoofSolid};
 }
 function roofScene(fixture=roofFixture(),feet=0,x=-5,z=10){
  world=fixture.w;state={player:{pos:[x,feet+1.65,z],ap:100,maxAp:100,crouched:false,yaw:0},character:{trait:''},perks:{},weather:{type:'clear'},status:{},worldTime:12,playTime:0};
  mode='PLAYING';onGround=true;jumpVelocity=0;return fixture;
 }
 globalThis.roofFixture=roofFixture;globalThis.roofScene=roofScene;globalThis.roofSolidAPI=MistralRoofSolids;
 globalThis.roofRun=(expression)=>eval(expression);
 globalThis.runRoofProof=()=>{
  const checks={},near=(a,b)=>Math.abs(a-b)<1e-6,f=roofScene();
  checks.explicit_source_attached=!!f.solid;
  checks.empty_air_ray=rayAABB([1,11,-5],[0,0,1],f.collider,100)===Infinity;
  checks.actual_roof_ray=near(rayAABB([1,20,10],[0,-1,0],f.collider,100),10.7);
  checks.solid_wall_ray=near(rayAABB([1,5,-5],[0,0,1],f.collider,100),5);
  checks.projectile_path_clear=firstObstacle([1,11,-5],[0,0,1],40)===40;
  checks.los_above_pitch_clear=lineOfSight([1,11,-5],[1,11,25]);
  checks.empty_air_body=!collidesAt(1,10,.1,11.65);
  checks.wall_body=collidesAt(1,10,.1,6.65);
  const support=f.solid.support(1,10,14,.38,false).height;roofScene(f,support,1,10);tryPlayerMove(.1,0);
  checks.walk_source_roof=near(state.player.pos[0],1.1)&&near(state.player.pos[1]-1.65,f.solid.support(1.1,10,14,.38,false).height);
  roofScene(f,14,1,10);onGround=false;jumpVelocity=-3;updatePlayer(.8);checks.fall_lands_on_source_roof=onGround&&near(state.player.pos[1]-1.65,support);
  const elevated=roofScene(roofFixture({props:{min_height:4}}),1.8,1,10);onGround=false;jumpVelocity=5;updatePlayer(.2);
  checks.source_base_stops_upward_head=!onGround&&jumpVelocity===0&&near(state.player.pos[1]+.18,3.999);
  const hole=roofScene(roofFixture({rings:[[[0,0],[20,0],[20,20],[0,20],[0,0]],[[5,5],[5,15],[15,15],[15,5],[5,5]]]}),0,10,10);
  checks.courtyard_has_no_roof=rayAABB([10,20,10],[0,-1,0],hole.collider,100)===Infinity&&!collidesAt(10,10,.38,1.65);
  const unknown=roofScene(roofFixture({omit:['roof:shape']}));checks.unknown_shape_keeps_envelope=!unknown.solid&&rayAABB([1,11,-5],[0,0,1],unknown.collider,100)===5;
  roofScene(f,0,-5,10);tryPlayerMove(6,0);checks.ground_cannot_teleport_onto_roof=state.player.pos[0]===-5&&near(state.player.pos[1],1.65);
  return checks;
 };
 `;
 return out;
}
module.exports={script};
if(require.main===module&&process.argv.includes('--script'))process.stdout.write(script());
