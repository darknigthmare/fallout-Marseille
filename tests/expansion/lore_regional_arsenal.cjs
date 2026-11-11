'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const A=require('../../src/v050/17a_regional_arsenal.js'),F=require('../../src/v050/17_first_person.js'),snapshot=require('../../tools/regional_catalog_snapshot.cjs');
const initial=snapshot(),weapons=structuredClone(initial.weapons),before=structuredClone(weapons);
A.install(F,weapons);
const has=(g,tag)=>g.faces.some(f=>f.tag===tag);
for(const id of initial.regional)test('stable regional identity '+id,()=>{
 const w=weapons[id],record=A.entry(id);assert.ok(record);assert.equal(w.mistralViewId,id);assert.equal(F.family(w),record.family);assert.equal(F.profile(w),record.profile);
 const {mistralViewId,...numeric}=w;assert.deepEqual(numeric,before[id]);
 const translated={...w,name:'Un nom traduit',damage:w.damage*1.13};assert.equal(F.family(translated),record.family);assert.equal(F.profile(translated),record.profile);
 const g=F.geometry(record.family,{profile:record.profile,reload:w.melee?0:.5});assert.ok(g.faces.every(f=>f.points.every(v=>v.every(Number.isFinite))));assert.ok(g.faces.length<950);
});
test('all 55 declared regional IDs covered, no foreign equipment reclassified',()=>{assert.deepEqual(Object.keys(A.RECORDS).sort(),initial.regional.sort());assert.equal(Object.keys(A.RECORDS).length,55);for(const id of Object.keys(weapons).filter(k=>!A.entry(k)))assert.deepEqual(weapons[id],before[id]);});
test('installation is idempotent',()=>{const family=F.family;assert.equal(A.install(F,weapons),false);assert.equal(F.family,family);});
test('no prototype property is an arsenal record',()=>{for(const k of ['__proto__','constructor','toString','unknown',null,9])assert.equal(A.entry(k),null);});
test('catalogue reads real ammunition and ownership without granting anything',()=>{const s={equipment:{ownedWeapons:['saltArc','pistol10']},player:{weaponId:'saltArc'}};const old=JSON.stringify(s);const rows=A.catalogue(weapons,initial.ammo,s);assert.equal(rows.length,55);assert.equal(rows.filter(r=>r.owned).length,1);assert.equal(rows.find(r=>r.id==='saltArc').ammoName,initial.ammo.protonCell.name);assert.equal(JSON.stringify(s),old);assert.equal(rows.find(r=>r.id==='ceramicSaw').clip,null);});
test('accent-insensitive search, bounded query, owned-only filter',()=>{const rows=A.catalogue(weapons,initial.ammo,{equipment:{ownedWeapons:['ceramicSaw']}});assert.equal(A.filter(rows,'ceramique',true)[0].id,'ceramicSaw');assert.equal(A.filter(rows,'aucun resultat xyz').length,0);assert.equal(A.filter(rows,'<script>').length,0);assert.equal(A.filter(rows,'').length,55);});
for(const [kind,profile,held,old]of [['industrial','needle','held-needle-tray','held-cassette'],['heavy','mortar40','held-40mm','held-rocket']]){
 test(profile+' feed exists only in reload window',()=>{for(const r of [0,.1,.18,.5,.86,.95,1]){const g=F.geometry(kind,{profile,reload:r});assert.equal(has(g,held),r>=.18&&r<=.86);assert.equal(has(g,old),false);if(profile==='needle')assert.equal(has(g,'needle-tray'),!(r>=.18&&r<=.86));}});
 test(profile+' sights and support anchors valid in portrait and desktop',()=>{for(const[w,h]of[[390,844],[1440,900]])for(const r of[0,.5]){const g=F.geometry(kind,{profile,reload:r,aim:r?0:1,aspect:w/h}),v=F.project(g.anchors.sight,w,h);if(!r)assert.ok(Math.abs(v[0]-w/2)<1e-8&&Math.abs(v[1]-h/2)<1e-8);else for(const k of['grip-1','reloadPart']){const a=F.project(g.anchors[k],w,h);assert.ok(a[0]>0&&a[0]<w&&a[1]>0&&a[1]<h);}}});
}
test('disc saw has its disc, guard and motor but no long machete blade',()=>{const g=F.geometry('blade',{profile:'ceramic-disc'});for(const t of['ceramic-disc','disc-hub','saw-motor','saw-guard','palm-1'])assert.ok(has(g,t));for(const t of['blade','blade-spine','hammer-head'])assert.equal(has(g,t),false);});
test('disc slots respond to emitted strike, but not a reduced-motion strike',()=>{const slots=g=>g.faces.filter(f=>f.tag==='disc-slot').map(f=>f.points);assert.notDeepEqual(slots(F.geometry('blade',{profile:'ceramic-disc',kick:.2})),slots(F.geometry('blade',{profile:'ceramic-disc',kick:.7})));assert.deepEqual(slots(F.geometry('blade',{profile:'ceramic-disc',kick:.2,reduceMotion:true})),slots(F.geometry('blade',{profile:'ceramic-disc',kick:.7,reduceMotion:true})));});
test('old family streams remain exactly unchanged without a new profile',()=>{delete require.cache[require.resolve('../../src/v050/17_first_person.js')];const original=require('../../src/v050/17_first_person.js');for(const kind of ['pistol','rifle','shotgun','heavy','energy','industrial','melee','blade','fist'])assert.deepEqual(F.geometry(kind,{reload:.5}),original.geometry(kind,{reload:.5}));});
test('missing catalogue item is not manufactured by the guide',()=>{const subset={saltArc:weapons.saltArc};assert.deepEqual(A.catalogue(subset,initial.ammo,{}).map(r=>r.id),['saltArc']);});
