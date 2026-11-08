'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const L=require('../../src/v050/10k_cour_lys.js'),M=require('../../src/v050/10l_parts_absents.js');
const cp=o=>JSON.parse(JSON.stringify(o));
function lys(policy='serment',route='service'){
 let s={player:{hp:100,caps:0},inventory:{circuitry:4,food:2},character:{special:{I:5}},playTime:40,v068Lys:L.fresh(),v060Council:{charter:'test-history',sealed:true},v067Devoir:{remaining:0}};
 const a=(type,id,answer)=>{s=L.apply(s,{type,id,answer},{local:true,near:true,point:L.point(type,id)});};
 a('open');for(const id of L.VOICES)a('hear',id);a('read','vivres');a('read','accueil');a('gate',route,'hote');a('read','programme');a('decide',policy);for(const id of L.VOICES)a('notify',id);a('finish');return s;
}
function act(s,type,id,extra={}){return M.apply(s,{type,id},{local:true,near:true,point:M.point(type,id),...extra});}
function open(s=lys()){return act(s,'open');}
function prepare(policy='serment',gate='manuel',s=lys(policy)){
 s=open(s);for(const id of M.VOICES)s=act(s,'hear',id);s=act(s,'read');
 if(gate==='manuel'){s=act(s,'moor','babord');s=act(s,'moor','tribord');}
 return act(s,'gate',gate);
}
function planned(plan='secours',policy='serment',gate='manuel'){return act(prepare(policy,gate),'plan',plan);}
function deliverAll(s,order=M.CRATES){
 for(const id of order){s=act(s,'take',id);const t=M.tally(s.v069Parts),dest=M.DESTS.find(d=>t[d]<M.PLANS[s.v069Parts.plan].quota[d]);s=act(s,'deliver',dest);}return s;
}
const history=s=>JSON.stringify([s.v068Lys,s.v060Council,s.v067Devoir]);

test('three plans each allocate exactly six crates, at least three kitchens and one for each other group',()=>{for(const p of Object.values(M.PLANS)){assert.equal(Object.values(p.quota).reduce((a,b)=>a+b),6);assert.ok(p.quota.cuisines>=3&&p.quota.accueil>=1&&p.quota.equipage>=1);}});
test('absent registry starts with six distinct racked crates and no acceptance',()=>{assert.deepEqual(M.migrate(null),M.fresh());assert.equal(M.held(M.fresh()),null);assert.deepEqual(M.tally(M.fresh()),{cuisines:0,accueil:0,equipage:0});});
test('actual Lys completion required, not a forged policy and finish flag',()=>{for(const v of [undefined,L.fresh(),{policy:'commune',finished:true}]){const s=lys();s.v068Lys=v;assert.equal(M.basis(s),null);assert.throws(()=>open(s),/audience/);}});
test('last notification without Lys closure does not unlock cargo',()=>{const s=lys();s.v068Lys.finished=false;assert.throws(()=>open(s),/audience/);});
test('opening freezes only immutable prior policy and archive route',()=>{const s=lys('regence','etiquette'),n=open(s);assert.deepEqual(n.v069Parts.basis,{policy:'regence',route:'etiquette'});assert.equal(s.v069Parts,undefined);assert.equal(history(n),history(s));});
test('opening is free and exclusive',()=>{const s=lys(),n=open(s);assert.deepEqual(n.inventory,s.inventory);assert.equal(n.player.caps,s.player.caps);assert.throws(()=>open(n),/déjà/);});
for(const context of [{local:false},{near:false},{point:'eloi'},{blocked:'combat'},{blocked:'loading'},{blocked:'lab'}])test('invalid physical context refuses without mutation '+JSON.stringify(context),()=>{const s=lys(),before=cp(s);assert.throws(()=>act(s,'open',null,context));assert.deepEqual(s,before);});
for(const n of [NaN,Infinity,'10',-1,1.5])test('invalid caps rejected before cloning: '+String(n),()=>{const s=lys();s.player.caps=n;assert.throws(()=>open(s),/capsules/);assert.ok(Object.is(s.player.caps,n));});
test('dead and malformed health refuse',()=>{for(const n of [0,-1,NaN,Infinity,'100']){const s=lys();s.player.hp=n;assert.throws(()=>open(s));}});
test('unknown and prototype keys never become actions or plans',()=>{const s=prepare();for(const id of ['__proto__','constructor','toString','bad']){assert.throws(()=>act(s,'plan',id));assert.throws(()=>act(s,'hear',id));assert.throws(()=>act(s,'take',id));}assert.throws(()=>act(s,'unknown','maelle'));});
test('no inspection, hearing or handling before opening',()=>{for(const[type,id]of [['read'],['hear','eloi'],['moor','babord'],['gate','manuel'],['take','A']])assert.throws(()=>act(lys(),type,id),/abord/);});
test('both local testimonies distinct and single-use',()=>{let s=open();s=act(s,'hear','nora');assert.throws(()=>act(s,'hear','nora'));s=act(s,'hear','eloi');assert.equal(s.v069Parts.heard.length,2);assert.throws(()=>act(s,'hear','maelle'));});
test('notice mandatory before any mechanical action',()=>{const s=open();for(const[type,id]of [['moor','babord'],['gate','manuel'],['gate','technique']])assert.throws(()=>act(s,type,id),/Consigne/);});
test('one mooring cannot open gate; failure spends nothing',()=>{let s=act(open(),'read');s=act(s,'moor','tribord');const before=cp(s);assert.throws(()=>act(s,'gate','manuel'),/deux amarres/);assert.deepEqual(s,before);});
test('two independent moorings in either order enable free manual entry',()=>{for(const order of [['babord','tribord'],['tribord','babord']]){let s=act(open(),'read');for(const id of order)s=act(s,'moor',id);const inv=cp(s.inventory);s=act(s,'gate','manuel');assert.deepEqual(s.inventory,inv);assert.equal(s.v069Parts.gate,'manuel');}});
test('mechanical controls and notice cannot be replayed after completion',()=>{const s=prepare();assert.throws(()=>act(s,'read'));assert.throws(()=>act(s,'moor','babord'));assert.throws(()=>act(s,'gate','manuel'));assert.throws(()=>act(s,'gate','technique'));});
test('INT and circuit mandatory for shortcut, no partial costs on failure',()=>{for(const n of [1,4,NaN,'5',undefined]){const s=act(open(),'read');s.character.special.I=n;assert.throws(()=>act(s,'gate','technique'),/Intelligence/);assert.equal(s.inventory.circuitry,4);}for(const n of [undefined,0,NaN,Infinity,'1',1.5,-2]){const s=act(open(),'read');s.inventory.circuitry=n;assert.throws(()=>act(s,'gate','technique'),/circuit/);assert.equal(s.v069Parts.gate,null);}});
test('technical route secures both locks and consumes exactly one circuit',()=>{const s=act(open(),'read'),n=act(s,'gate','technique');assert.equal(n.inventory.circuitry,s.inventory.circuitry-1);assert.deepEqual(n.v069Parts.moored,['babord','tribord']);});
test('plans require both voices and actual safe access, then are exclusive',()=>{let s=open();assert.throws(()=>act(s,'plan','secours'));s=act(prepare(),'plan','secours');assert.throws(()=>act(s,'plan','rotation'));assert.throws(()=>act(s,'plan','secours'));});
test('a crate cannot be taken before a plan or twice; only one crate can be carried',()=>{assert.throws(()=>act(prepare(),'take','A'));const s=act(planned(),'take','A');assert.equal(M.held(s.v069Parts),'A');assert.throws(()=>act(s,'take','A'));assert.throws(()=>act(s,'take','B'));});
test('empty hands cannot deliver and wrong rack cannot receive another crate',()=>{assert.throws(()=>act(planned(),'deliver','cuisines'));let s=act(planned(),'take','F');assert.throws(()=>act(s,'return','A'));s=act(s,'return','F');assert.equal(M.held(s.v069Parts),null);assert.equal(s.v069Parts.crates.F,'rack');assert.throws(()=>act(s,'return','F'));});
test('each full destination rejects further crates without dropping the held crate',()=>{let s=planned();s=act(act(s,'take','A'),'deliver','equipage');s=act(s,'take','B');assert.throws(()=>act(s,'deliver','equipage'),/complet/);assert.equal(M.held(s.v069Parts),'B');});
test('picking all cargo never counts as delivered; closure requires all six at their destinations',()=>{let s=planned();for(const id of M.CRATES.slice(0,5)){s=act(s,'take',id);const t=M.tally(s.v069Parts),d=M.DESTS.find(d=>t[d]<M.PLANS.secours.quota[d]);s=act(s,'deliver',d);}s=act(s,'take','F');assert.throws(()=>act(s,'finish'),/déposées/);});
for(const policy of ['serment','commune','regence'])for(const gate of ['manuel','technique'])for(const plan of Object.keys(M.PLANS))test(policy+'/'+gate+'/'+plan+': full physical deliveries preserve original history and ordinary inventory',()=>{
 let s=planned(plan,policy,gate);const old=history(s),inv=cp(s.inventory),caps=s.player.caps;s=deliverAll(s,['F','B','D','A','E','C']);assert.equal(s.v069Parts.finished,false);s=act(s,'finish');assert.equal(s.player.caps,caps+40);assert.deepEqual(s.inventory,inv);assert.equal(history(s),old);assert.deepEqual(M.tally(s.v069Parts),M.PLANS[plan].quota);assert.throws(()=>act(s,'finish'));assert.throws(()=>act(s,'take','A'));assert.deepEqual(M.migrate(cp(s.v069Parts)),s.v069Parts);
});
test('free complete route with INT1, empty inventory and zero starting capsules',()=>{const s=lys();s.player.caps=0;s.inventory={};s.character.special.I=1;let n=act(prepare('serment','manuel',s),'plan','secours');n=act(deliverAll(n),'finish');assert.deepEqual(n.inventory,{});assert.equal(n.player.caps,40);});
test('claiming the original welcome parcel after opening never invalidates the frozen source',()=>{let s=open();s=L.apply(s,{type:'claim'},{local:true,near:true,point:'colis'});assert.equal(act(s,'read').v069Parts.notice,true);});
test('a different valid earlier policy cannot silently rewrite the cargo source',()=>{const s=open();s.v068Lys=lys('commune').v068Lys;assert.throws(()=>act(s,'read'),/source a changé/);assert.equal(s.v069Parts.basis.policy,'serment');});
test('stale confirmations and revision saturation refuse without mutation',()=>{const s=prepare();assert.throws(()=>act(s,'plan','secours',{revision:s.v069Parts.revision-1}),/périmée/);s.v069Parts.revision=999999;assert.throws(()=>act(s,'plan','secours'),/plein/);});
test('caps overflow does not consume completion reward',()=>{const s=deliverAll(planned());s.player.caps=999980;assert.throws(()=>act(s,'finish'),/plein/);assert.equal(s.v069Parts.finished,false);});
test('JSON reload preserves a carried crate and every delivery, never refilling the rack',()=>{let s=planned();for(const id of M.CRATES){s=act(s,'take',id);s=cp(s);s.v069Parts=M.migrate(s.v069Parts);assert.equal(M.held(s.v069Parts),id);const d=M.DESTS.find(d=>M.tally(s.v069Parts)[d]<M.PLANS.secours.quota[d]);s=act(s,'deliver',d);const old=cp(s.v069Parts);s=cp(s);s.v069Parts=M.migrate(s.v069Parts);assert.deepEqual(s.v069Parts,old);}});
test('future or malformed registry fails closed instead of resetting finite stock',()=>{for(const raw of [[],3,{schema:2},{}])assert.throws(()=>M.migrate(raw));for(const mutate of [l=>delete l.crates.A,l=>l.crates.A='constructor',l=>{l.crates.A='held';l.crates.B='held';},l=>l.finished=true,l=>l.gate=null,l=>l.heard=['eloi'],l=>l.opened=false]){const l=cp(act(planned(),'take','A').v069Parts);mutate(l);assert.throws(()=>M.migrate(l));}});
test('mutating exported presentation catalogue cannot alter authoritative quotas',()=>{const old=M.PLANS.secours.quota.cuisines;M.PLANS.secours.quota.cuisines=999;try{const s=planned();let n=s;for(const id of ['A','B','C'])n=act(act(n,'take',id),'deliver','cuisines');n=act(n,'take','D');assert.throws(()=>act(n,'deliver','cuisines'),/complet/);}finally{M.PLANS.secours.quota.cuisines=old;}});
test('new games start empty of old cargo decisions; inspection never fabricates a political outcome',()=>{const done=act(deliverAll(planned('rotation')),'finish');assert.equal(M.fresh().plan,null);assert.equal(M.fresh().finished,false);const n=act(open(),'read');assert.equal(n.v069Parts.plan,null);assert.equal(done.v069Parts.plan,'rotation');});
module.exports={lys,act,prepare,planned,deliverAll};
