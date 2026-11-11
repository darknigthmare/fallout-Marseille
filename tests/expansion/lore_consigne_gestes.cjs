'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../../src/v050/10x_consigne_gestes.js'),'utf8');
const G=require('../../src/v050/10x_consigne_gestes.js');
for(const id of G.ids){
 test(id+': four phases end in a kept object, not a second inventory item',()=>{
  assert.deepEqual([0,600,1800,2500,2900].map(t=>G.pose(id,t).phase),['receive','recognise','keep','release','done']);
  assert.equal(G.pose(id,2900).done,true);assert.deepEqual(G.pose(id,2900),G.pose(id,1e8));
 });
 test(id+': entire trajectory is continuous, finite and reachable',()=>{
  let previous=G.pose(id,0);
  for(let ms=1;ms<=2900;ms++){
   const p=G.pose(id,ms),joint=G.elbow(p.hand);
   assert.ok([...p.hand,...p.item,...joint].every(Number.isFinite));
   assert.ok(Math.hypot(...p.hand.map((v,i)=>v-previous.hand[i]))<.003);
   assert.ok(Math.hypot(...p.item.map((v,i)=>v-previous.item[i]))<.003);
   assert.ok(Math.abs(Math.hypot(...joint.map((v,i)=>v-[.32,1.34,0][i]))-.36)<1e-8);
   assert.ok(Math.abs(Math.hypot(...joint.map((v,i)=>v-p.hand[i]))-.36)<1e-8);
   previous=p;
  }
 });
 test(id+': returned poses do not expose mutable definitions',()=>{const p=G.pose(id,800);p.hand[0]=999;p.item[0]=999;assert.ok(G.pose(id,800).hand[0]<1);});
}
test('invalid clocks and unknown/prototype identifiers rejected',()=>{
 for(const id of ['__proto__','constructor','other',null])assert.throws(()=>G.pose(id,0));
 for(const t of [-1,NaN,Infinity,'200']){assert.throws(()=>G.pose('clef',t));assert.throws(()=>G.elapsed(0,t));}
});
test('pause, bounded tab-resume delta and completion cap',()=>{
 assert.equal(G.elapsed(500,100,false),500);assert.equal(G.elapsed(500,60000),600);assert.equal(G.elapsed(2890,100),2900);
 assert.equal(G.elapsed(500,0),500);
});
test('pose coordinates follow native rig yaw and scale',()=>{
 assert.deepEqual(G.point([10,2,20],0,[1,3,-2],2),[12,8,16]);
 const p=G.point([0,0,0],Math.PI/2,[1,0,0]);assert.ok(Math.abs(p[0])<1e-10);assert.equal(p[2],-1);
});
function fixture(){
 const ctx=vm.createContext({console,Math,Map,Number,Object,JSON,Error});
 vm.runInContext(`
 let state={v042:{activeInterior:'consigne'},v073Gabians:{finished:false,handoffs:{clef:null,bague:null,sifflet:null}},player:{hp:100,caps:45},inventory:{scrap:2}};
 let world={id:'interior',v073Gabians:true},mode='DIALOGUE',gameStarted=true,gameClock=0,zoneTransitioning=false;
 const settings={reduceMotion:false},V046={busy:false,lab:false},V047={pending:false};
 const COLORS={skin:[.8,.6,.4],clothBlue:[.3,.4,.5]};
 const MistralGabians={SITE:'consigne',OBJECTS:{clef:{owner:'Éloi'},bague:{owner:'Mina'},sifflet:{owner:'Rachid'}}};
 const elements={questTitle:{},questObjective:{}};const $=id=>elements[id];
 const window={__MISTRAL_DEBUG:{}};let displayed;
 function openDialogue(s,t,c){displayed={s,t,choices:c};return true;}
 function humanParts(out,n){out.push({mesh:'cube',pos:[0,0,0],native:'body'});for(const p of [[.32,1.16,0],[.33,.89,.025],[.33,.73,.02]])out.push({mesh:'sphere',pos:[n.pos[0]+p[0],n.pos[1]+p[1],n.pos[2]+p[2]],native:'arm'});}
 const npcs=['clef','bague','sifflet'].map((id,i)=>({id:'g73:owner:'+id,pos:[i*3,0,18],yaw:0,color:COLORS.clothBlue,skin:COLORS.skin}));
 function collectDraws(t){const out=[];for(const n of npcs)humanParts(out,n,t);return out;}
 function getObjectiveMarker(){return {label:'Nora'};}
 function updateQuestUI(){elements.questTitle.textContent='base';}
 globalThis.start=(key,success=true)=>{openDialogue({name:MistralGabians.OBJECTS[key].owner},'',[{text:'Remettre en main propre : objet.',onChoose:()=>{if(success)state.v073Gabians.handoffs[key]='direct';return success;}}]);return displayed.choices[0].onChoose();};
 globalThis.info=()=>window.__MISTRAL_DEBUG.v075GesturesInfo();
 globalThis.snapshot=()=>JSON.stringify(state);
 globalThis.draw=t=>collectDraws(t);
 `+source+`;v053LoreAfterInit();`,ctx);
 return {ctx,ev:s=>vm.runInContext(s,ctx)};
}
test('real successful native callback alone starts presentation; failed transaction does not',()=>{
 const f=fixture();f.ev(`start('clef',false)`);assert.equal(f.ev('info().active.length'),0);
 f.ev(`start('clef')`);assert.equal(f.ev('info().active[0].id'),'clef');assert.equal(f.ev('state.player.caps'),45);
});
test('repeated callbacks cannot restart a completed handoff',()=>{
 const f=fixture();f.ev(`start('clef');draw(.1)`);const ms=f.ev('info().active[0].ms');f.ev(`start('clef')`);assert.equal(f.ev('info().active[0].ms'),ms);
});
test('rendering never writes the campaign; exactly three native right-arm parts replaced',()=>{
 const f=fixture();f.ev(`start('clef')`);const snap=f.ev('snapshot()'),d=f.ev('draw(.1)');
 assert.equal(d.filter(d=>d.v075Hand).length,1);assert.equal(d.filter(d=>d.native==='arm').length,6);
 assert.equal(d.filter(d=>d.native==='body').length,3);assert.equal(f.ev('snapshot()'),snap);
});
test('same timestamp does not advance; pause and dialogue have distinct semantics',()=>{
 const f=fixture();f.ev(`start('clef');draw(.1);draw(.1)`);assert.equal(f.ev('info().active[0].ms'),100);
 f.ev(`mode='PIP';draw(.2);draw(10)`);assert.equal(f.ev('info().active[0].ms'),100);
 f.ev(`mode='DIALOGUE';draw(10.1)`);assert.ok(Math.abs(f.ev('info().active[0].ms')-200)<1e-7);
});
test('load or world replacement clears transient animation but retains the visible object',()=>{
 const f=fixture();f.ev(`start('bague');state=JSON.parse(JSON.stringify(state))`);
 assert.equal(f.ev('info().active.length'),0);assert.ok(f.ev('draw(.1).some(d=>d.v075Object===\'bague\')'));
 f.ev(`start('clef');world={...world}`);assert.equal(f.ev('info().active.length'),0);
});
test('reduce-motion uses final objects immediately and cancels an active gesture',()=>{
 const f=fixture();f.ev(`settings.reduceMotion=true;start('bague')`);assert.equal(f.ev('info().active.length'),0);
 assert.ok(f.ev('draw(.1).some(d=>d.v075Object===\'bague\')'));
 f.ev(`settings.reduceMotion=false;start('clef');settings.reduceMotion=true;draw(.2)`);assert.equal(f.ev('info().active.length'),0);
});
test('all three independent gestures finish without reward, duplicate hand or lost object',()=>{
 const f=fixture();f.ev(`for(const k of ['clef','bague','sifflet'])start(k)`);const snap=f.ev('snapshot()');
 for(let i=1;i<=31;i++)f.ev('draw('+i/10+')');assert.equal(f.ev('info().active.length'),0);
 const draws=f.ev('draw(4)');assert.equal(new Set(draws.filter(d=>d.v075Object).map(d=>d.v075Object)).size,3);
 assert.equal(draws.filter(d=>d.v075Hand).length,0);assert.equal(f.ev('snapshot()'),snap);
});
test('no animation is started by old schema-compatible received objects',()=>{
 const f=fixture();f.ev(`state.v073Gabians.handoffs={clef:'consigne',bague:'direct',sifflet:'consigne'}`);
 assert.equal(f.ev('info().active.length'),0);assert.equal(f.ev('draw(1).filter(d=>d.v075Hand).length'),0);
});
test('completed optional epilogue points to exit, not an already-paid reward',()=>{
 const f=fixture();assert.equal(f.ev('getObjectiveMarker().label'),'Nora');
 f.ev(`for(const k of ['clef','bague','sifflet'])start(k);state.v073Gabians.finished=true;updateQuestUI()`);
 assert.match(f.ev('getObjectiveMarker().label'),/Retour au Vieux-Port/);assert.match(f.ev('elements.questTitle.textContent'),/TERMINÉ/);
});
test('unfinished optional epilogue remains optional in the HUD',()=>{
 const f=fixture();f.ev(`state.v073Gabians.finished=true;updateQuestUI()`);
 assert.match(f.ev('elements.questObjective.textContent'),/Facultatif/);
});

test('a backwards render timestamp cannot create extra elapsed time on catch-up',()=>{
 const f=fixture();f.ev(`start('clef');draw(.1);draw(.05);draw(.1)`);assert.equal(f.ev('info().active[0].ms'),100);
});
test('scene transition, laboratory and dead player pause presentation',()=>{
 const f=fixture();f.ev(`start('clef');zoneTransitioning=true;draw(.1);zoneTransitioning=false;V046.lab=true;draw(.2);V046.lab=false;state.player.hp=0;draw(.3)`);
 assert.equal(f.ev('info().active[0].ms'),0);
});
test('a callback owned by a replaced save cannot start a gesture',()=>{
 const f=fixture();f.ev(`openDialogue({name:'Éloi'},'',[{text:'Remettre en main propre : objet.',onChoose:()=>{state=JSON.parse(JSON.stringify(state));state.v073Gabians.handoffs.clef='direct';}}]);displayed.choices[0].onChoose();`);
 assert.equal(f.ev('info().active.length'),0);
});
test('unrelated dialogue choices and other scenes pass through unchanged',()=>{
 const f=fixture();f.ev(`let calls=0;const ordinary={text:'Parler du bateau',onChoose:()=>++calls};openDialogue({name:'Éloi'},'',[ordinary]);`);
 assert.equal(f.ev('displayed.choices[0]===ordinary'),true);f.ev('displayed.choices[0].onChoose()');assert.equal(f.ev('calls'),1);
 f.ev(`world={id:'elsewhere'};start('clef')`);assert.equal(f.ev('info().active.length'),0);
});

test('inverse rig coordinates preserve world attachment for every yaw and scale',()=>{
 for(const yaw of [0,.3,-Math.PI/2,Math.PI])for(const sc of [.5,1,2]){
  const origin=[-5,2,18],p=[.33,.75,.13],q=G.unpoint(origin,yaw,G.point(origin,yaw,p,sc),sc);
  assert.ok(q.every((v,i)=>Math.abs(v-p[i])<1e-12));
 }
});
