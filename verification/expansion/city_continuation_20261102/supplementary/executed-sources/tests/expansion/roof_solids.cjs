#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm');
const context=vm.createContext({console,window:{__MISTRAL_DEBUG:{}}});vm.runInContext(require('./roof_harness.cjs').script(),context);
let passed=0;function test(name,fn){fn();passed++;console.log('OK '+name);}const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
const f=context.roofFixture(),s=f.solid;
test('Explicit source roof receives a precise closed solid',()=>assert.ok(s&&s.faces.length>0));
test('Source ridge and eaves are retained exactly',()=>{near(s.heightAt(10,10),12);near(s.heightAt(0,10),9);near(s.heightAt(1,10),9.3);});
test('The source exterior remains solid below its pitched surface',()=>assert.equal(s.contains([1,5,10]),true));
test('Empty air inside the old ridge-height box is outside the source solid',()=>assert.equal(s.contains([1,11,10]),false));
test('A vertical ray hits the pitched source face before the old flat envelope',()=>near(s.ray([1,20,10],[0,-1,0],100),10.7));
test('A horizontal ray above the local roof pitch remains unobstructed',()=>assert.equal(s.ray([1,11,-5],[0,0,1],100),Infinity));
test('A ray into a source gable hits its measured face',()=>near(s.ray([10,11,-5],[0,0,1],100),5));
test('Solid walls below the eaves remain obstructing',()=>near(s.ray([1,5,-5],[0,0,1],100),5));
test('A ray starting in the solid returns zero',()=>assert.equal(s.ray([1,5,10],[1,0,0],100),0));
test('A ray starting above the local pitch is not treated as inside',()=>assert.ok(s.ray([1,11,10],[1,0,0],100)>0));
test('Source faces are two-sided for exit and downward rays',()=>{near(s.ray([1,20,10],[0,-1,0],100),10.7);assert.ok(Number.isFinite(s.ray([1,11,10],[1,0,0],100)));});
test('A ray limit is respected by exact faces',()=>assert.equal(s.ray([1,20,10],[0,-1,0],10),Infinity));
test('An unbounded ray still intersects the exact source exterior',()=>near(s.ray([1,20,10],[0,-1,0],Infinity),10.7));
test('Invalid ray inputs cannot create a hit',()=>{assert.equal(s.ray([NaN,0,0],[1,0,0]),Infinity);assert.equal(s.ray([1,20,10],[0,-1,0],-1),Infinity);});
test('The footprint-disc maximum is analytic on the source slope',()=>near(s.maxDisk(1,10,.38),9.414));
test('A foot-disc grazing an outer wall still detects its real roof edge',()=>near(s.maxDisk(-.2,10,.3),9.03));
test('A separated foot-disc cannot collide with a building',()=>assert.equal(s.maxDisk(-1,10,.38),null));
test('A cylinder in empty roof-box air no longer collides',()=>assert.equal(s.cylinder(1,10,.1,10,11.83),false));
test('A cylinder intersecting the actual roof volume collides',()=>assert.equal(s.cylinder(1,10,.1,9.2,11.03),true));
test('A cylinder resting on its supporting roof disc is not embedded',()=>assert.equal(s.cylinder(1,10,.38,9.414,11.244),false));
test('A source courtyard remains open to rays and bodies',()=>{
 const h=context.roofFixture({rings:[[[0,0],[20,0],[20,20],[0,20],[0,0]],[[5,5],[5,15],[15,15],[15,5],[5,5]]]}).solid;
 assert.equal(h.ray([10,20,10],[0,-1,0],100),Infinity);assert.equal(h.cylinder(10,10,.38,0,1.83),false);assert.equal(h.support(10,10,20,.38,false),null);
 near(h.ray([10,8,10],[1,0,0],100),5);
});
test('An elevated source building preserves its open underpass and bottom cap',()=>{
 const e=context.roofFixture({props:{min_height:4}}).solid;
 assert.equal(e.cylinder(1,10,.38,0,1.83),false);assert.equal(e.ray([1,1,-5],[0,0,1],100),Infinity);near(e.ray([1,1,10],[0,1,0],100),3);
});
test('Negative absolute elevations retain their physical datum',()=>{
 const n=context.roofFixture({props:{ground_elevation:-20}}).solid;near(n.heightAt(10,10),-8);near(n.ray([10,0,10],[0,-1,0],100),8);
});
test('A skillion source roof retains its single measured slope',()=>{
 const k=context.roofFixture({props:{'roof:shape':'skillion'}}).solid;near(k.heightAt(0,10),12);near(k.heightAt(20,10),9);
});
test('Unknown source roof shape retains the conservative envelope',()=>assert.equal(context.roofFixture({omit:['roof:shape']}).solid,undefined));
test('Missing source roof direction retains the conservative envelope',()=>assert.equal(context.roofFixture({omit:['roof:direction']}).solid,undefined));
test('An estimated building height does not become a certified source roof',()=>assert.equal(context.roofFixture({omit:['height'],props:{'building:levels':4}}).solid,undefined));
test('Reachable support never steps more than the existing .72m limit',()=>{assert.ok(s.support(1,10,9,.38,true));assert.equal(s.support(1,10,0,.38,true),null);});
test('An airborne actor cannot step upward to a roof surface',()=>{assert.equal(s.support(1,10,9.3,.38,false),null);assert.ok(s.support(1,10,10,.38,false));});
test('Steep source roofs remain solid but are not walking platforms',()=>{
 const r=context.roofFixture({props:{height:40,'roof:height':30}}).solid;assert.ok(r);assert.equal(r.support(1,10,100,.38,false),null);assert.equal(r.cylinder(1,10,.38,11,13),true);
});
for(const[name,ok]of Object.entries(context.runRoofProof()))test('Production integration: '+name,()=>assert.equal(ok,true));
test('The body-height narrow-phase context is restored after each query',()=>{context.roofScene(f);context.collidesAt(1,10,.1,11.65);assert.equal(context.roofRun('V050_ROOFS.body'),null);});
test('Crouched walking uses the actual player eye height on a pitched roof',()=>{
 const h=s.support(1,10,14,.32,false).height;context.roofScene(f,h,1,10);context.roofRun('state.player.crouched=true;state.player.pos[1]-=.47');context.tryPlayerMove(.1,0);
 near(context.roofRun('state.player.pos[0]'),1.1);near(context.roofRun('state.player.pos[1]-playerEyeHeight()'),s.support(1.1,10,14,.32,false).height);
});
test('Stepping off a source roof starts a fall without snapping to the terrain',()=>{
 const h=s.support(.1,10,14,.38,false).height;context.roofScene(f,h,.1,10);context.tryPlayerMove(-.6,0);
 assert.equal(context.roofRun('onGround'),false);near(context.roofRun('state.player.pos[1]-playerEyeHeight()'),h);
});
test('Other boxes preserve their original collision behavior',()=>{
 context.roofScene();context.roofRun("world.colliders=[{minX:30,maxX:40,minY:0,maxY:12,minZ:0,maxZ:20}]");assert.equal(context.collidesAt(35,10,.38,6.65),true);
});
test('Streaming removal invalidates roof support',()=>{
 context.roofScene(f);assert.ok(context.roofRun('v050RoofSupport(1,10,14,false)'));
 context.roofRun('world.colliders=[];world.v046Records=new Map()');assert.equal(context.roofRun('v050RoofSupport(1,10,14,false)'),null);
});
console.log(JSON.stringify({suite:'roof_solids',passed,failed:0}));
