'use strict';
const {test}=require('node:test');
const a=require('node:assert/strict');
const M=require('../../src/v050/10y_consigne_vie.js');
const hands={clef:'direct',bague:'consigne',sifflet:'direct'};
const ctx=l=>({local:true,near:true,revision:l.revision});
const start=id=>M.action(M.fresh(),hands,id,'go',ctx(M.fresh()));
test('missing old ledger is migrated without inventing any invitation',()=>a.deepEqual(M.migrate(null,hands),M.fresh()));
test('fresh ledgers do not share arrays or person objects',()=>{const x=M.fresh();x.people.clef.started=true;a.equal(M.fresh().people.clef.started,false);});
test('unknown schema is refused, not silently erased',()=>a.throws(()=>M.migrate({...M.fresh(),schema:2},hands)));
for(const value of [-1,1.2,NaN,Infinity,1000000])test('invalid revision '+value,()=>a.throws(()=>M.migrate({...M.fresh(),revision:value},hands)));
for(const id of M.IDS){
 test(id+': endpoints and distances',()=>{a.deepEqual(M.position(id,0),M.ROUTES[id].path[0]);a.deepEqual(M.position(id,M.total(id)),M.ROUTES[id].path.at(-1));a.ok(M.total(id)>0);});
 test(id+': validated roundtrip',()=>{const l=start(id);a.deepEqual(M.migrate(JSON.parse(JSON.stringify(l)),hands),l);});
 test(id+': cannot walk before saved receipt',()=>a.throws(()=>M.action(M.fresh(),{},id,'go',ctx(M.fresh()))));
 test(id+': duplicate invitation rejected',()=>{const l=start(id);a.throws(()=>M.action(l,hands,id,'go',ctx(l)));});
 test(id+': stale dialogue rejected',()=>{const l=start(id);a.throws(()=>M.action(l,hands,id,'wait',{...ctx(l),revision:0}));});
 test(id+': pause and resume do not change progress',()=>{let l=start(id);l=M.action(l,hands,id,'wait',ctx(l));const p=M.advance(l,hands,id,250);a.equal(p.moved,false);a.deepEqual(p.ledger,l);l=M.action(l,hands,id,'resume',ctx(l));a.equal(M.advance(l,hands,id,250).ledger.people[id].progress,250);});
 test(id+': solid blocker refuses entire sample step without mutation',()=>{const l=start(id),before=JSON.stringify(l);let calls=0;const step=M.advance(l,hands,id,250,()=>++calls<3);a.equal(step.blocked,true);a.equal(step.moved,false);a.equal(JSON.stringify(l),before);a.deepEqual(step.ledger,l);});
 test(id+': reaches destination without crossing segment corners or overshooting',()=>{let l=start(id),prev=M.position(id,0),checkpoints=0;for(let i=0;i<300;i++){const s=M.advance(l,hands,id,250,(from,to)=>{a.ok(Math.hypot(...to.map((v,j)=>v-from[j]))<=.0500001);return true;});l=s.ledger;if(s.checkpoint)checkpoints++;const p=M.position(id,l.people[id].progress);a.ok(Math.hypot(...p.map((v,j)=>v-prev[j]))<=.2500001);prev=p;}a.equal(l.people[id].progress,M.total(id));a.deepEqual(prev,M.ROUTES[id].path.at(-1));a.ok(checkpoints>=4);a.equal(l.revision,2);});
 test(id+': memory only at actual arrival and is recorded once',()=>{let l=start(id);a.throws(()=>M.action(l,hands,id,'listen',ctx(l)));while(l.people[id].progress<M.total(id))l=M.advance(l,hands,id,250).ledger;l=M.action(l,hands,id,'listen',ctx(l));a.equal(l.people[id].heard,true);a.throws(()=>M.action(l,hands,id,'listen',ctx(l)));a.throws(()=>M.action(l,hands,id,'wait',ctx(l)));});
 test(id+': progress before invitation rejected',()=>{const l=M.fresh();l.people[id].progress=20;a.throws(()=>M.migrate(l,hands));});
 test(id+': arrived pause contradictory',()=>{const l=start(id);l.people[id].progress=M.total(id);l.people[id].paused=true;a.throws(()=>M.migrate(l,hands));});
 test(id+': missing receipt invalidates persisted routine, never fabricates one',()=>a.throws(()=>M.migrate(start(id),{})));
 test(id+': midway roundtrip preserves precise millimetres',()=>{const l=M.advance(start(id),hands,id,137).ledger;a.equal(M.migrate(JSON.parse(JSON.stringify(l)),hands).people[id].progress,137);});
 test(id+': zero step is an exact no-op',()=>{const l=start(id);a.deepEqual(M.advance(l,hands,id,0).ledger,l);});
 test(id+': memory boolean and route bounds are strict',()=>{for(const change of [{heard:'yes'},{progress:-1},{progress:M.total(id)+1},{progress:NaN}]){const l=start(id);Object.assign(l.people[id],change);a.throws(()=>M.migrate(l,hands));}});
 test(id+': no writes to another owner or caller ledger',()=>{const l=start(id),before=JSON.stringify(l),r=M.advance(l,hands,id,200);a.equal(JSON.stringify(l),before);for(const other of M.IDS.filter(x=>x!==id))a.deepEqual(r.ledger.people[other],l.people[other]);a.deepEqual(Object.keys(r.ledger).sort(),['people','revision','schema']);});
}
for(const bad of [0,'nora',null,'__proto__'])test('unknown owner refused '+String(bad),()=>a.throws(()=>M.position(bad,0)));
for(const step of [-1,.2,251,Infinity,NaN])test('invalid movement step '+step,()=>a.throws(()=>M.advance(start('clef'),hands,'clef',step)));
for(const c of [{near:false},{local:false},{blocked:true}])test('invalid interaction context '+JSON.stringify(c),()=>a.throws(()=>M.action(M.fresh(),hands,'clef','go',{...ctx(M.fresh()),...c})));
test('all three owners advance independently with different route lengths',()=>{let l=M.fresh();for(const id of M.IDS)l=M.action(l,hands,id,'go',ctx(l));for(let i=0;i<80;i++)for(const id of M.IDS)l=M.advance(l,hands,id,250).ledger;for(const id of M.IDS)a.equal(l.people[id].progress,M.total(id));a.equal(l.revision,6);});

for(const id of M.IDS)test(id+': heading reconstructed at every saved distance and destination',()=>{
 for(let p=0;p<=M.total(id);p+=137)a.ok(Number.isFinite(M.heading(id,p)));
 a.equal(M.heading(id,M.total(id)),M.ROUTES[id].yaw);
});

for(const id of M.IDS)test(id+': native rig faces forward along its route, never backwards',()=>{
 for(let p=0;p<M.total(id);p+=173){const q=M.position(id,p),r=M.position(id,p+1),y=M.heading(id,p);
  const dot=-Math.sin(y)*(r[0]-q[0])-Math.cos(y)*(r[2]-q[2]);a.ok(dot>0);
 }
});
