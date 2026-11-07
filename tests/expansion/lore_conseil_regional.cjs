'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Council=require('../../src/v050/10c_conseil_regional.js');

function registry(overrides={}){
 const networks=Object.fromEntries(Council.NETWORKS.map(item=>[item.id,{
  id:item.id,label:item.label,access:65,legitimacy:68,coercion:35,resilience:62,
  controller:'Service public territorial',reasons:[]
 }]));
 return{
  networks,
  scores:{charte_vivants:20,republique_services:18,continuite:5,federation:12,travailleurs:9,levant:3,technocratie:4,fragmentation:1},
  projection:{winner:'charte_vivants',label:'Charte des Vivants',alternate:'republique_services',alternateLabel:'République des Services',confidence:96,margin:2,state:'contestée',reasons:['Accès et recours convergent.']},
  identity:{status:'recognized',evidence:{body:true,deathNotice:true,terminalTrace:true,a03Journal:true,odetteTestimony:true,relayRecognition:true,regionalSignatures:true,publicWitnesses:true,hydraulicRegisters:true,visualArchives:true}},
  ...overrides
 };
}
function campaign(done=true,madame=registry()){
 return{quest:{main:done?59:48,aubagneComplete:done,aubagneOutcome:done?'federation':null},playTime:7200,v059Madame:madame};
}
function deliberate(camp=campaign(),madame=camp.v059Madame,choices={preuve:'pluralite',minimum:'universel',controle:'audit',force:'sans_armee'}){
 let ledger=Council.synchronize(Council.fresh(),camp,madame);
 ledger=Council.reduce(ledger,{type:'convene'},camp,madame).ledger;
 for(const [motion,choice] of Object.entries(choices))ledger=Council.reduce(ledger,{type:'motion',motion,choice},camp,madame).ledger;
 return ledger;
}

test('catalogue: quatre motions, huit voies, treize délégations et sept réseaux',()=>{
 assert.equal(Object.keys(Council.MOTIONS).length,4);
 assert.equal(Council.PATHS.length,8);
 assert.equal(Council.DELEGATIONS.length,13);
 assert.equal(Council.NETWORKS.length,7);
 assert.equal(new Set(Council.PATHS.map(item=>item.id)).size,8);
});

test('déverrouillage: le conseil reste fermé avant la fin du chapitre VI',()=>{
 const before=campaign(false);
 assert.equal(Council.synchronize(Council.fresh(),before,before.v059Madame).status,'locked');
 const after=campaign(true);
 assert.equal(Council.synchronize(Council.fresh(),after,after.v059Madame).status,'available');
});

test('migration: une ancienne sauvegarde partielle est assainie sans muter l’entrée',()=>{
 const raw={schema:0,status:'convened',clauses:{preuve:'pluralite',minimum:'inconnue'},failedVotes:[{path:'levant',for:'4',against:7,abstain:2,at:12}],journal:[{type:'convene',at:1},{type:'hack'}]};
 const snapshot=structuredClone(raw),camp=campaign();
 const migrated=Council.synchronize(raw,camp,camp.v059Madame);
 assert.deepEqual(raw,snapshot);
 assert.equal(migrated.schema,1);
 assert.equal(migrated.status,'convened');
 assert.equal(migrated.clauses.preuve,'pluralite');
 assert.equal(migrated.clauses.minimum,null);
 assert.equal(migrated.failedVotes.length,1);
 assert.equal(migrated.journal.length,1);
});

test('convocation: impossible avant la fin, unique après le déverrouillage',()=>{
 const locked=campaign(false);
 let plan=Council.reduce(Council.fresh(),{type:'convene'},locked,locked.v059Madame);
 assert.equal(plan.ok,false);
 const camp=campaign();
 plan=Council.reduce(Council.fresh(),{type:'convene',at:10},camp,camp.v059Madame);
 assert.equal(plan.ok,true);
 assert.equal(plan.ledger.status,'convened');
 assert.equal(plan.ledger.convenedAt,10);
 const again=Council.reduce(plan.ledger,{type:'convene'},camp,camp.v059Madame);
 assert.equal(again.ok,false);
});

test('motions: les clauses sont amendables avant ratification et déterminent la délibération',()=>{
 const camp=campaign();let ledger=Council.reduce(Council.synchronize(Council.fresh(),camp,camp.v059Madame),{type:'convene'},camp,camp.v059Madame).ledger;
 ledger=Council.reduce(ledger,{type:'motion',motion:'preuve',choice:'registre'},camp,camp.v059Madame).ledger;
 assert.equal(ledger.clauses.preuve,'registre');
 ledger=Council.reduce(ledger,{type:'motion',motion:'preuve',choice:'pluralite'},camp,camp.v059Madame).ledger;
 assert.equal(ledger.clauses.preuve,'pluralite');
 for(const [motion,choice] of [['minimum','universel'],['controle','audit'],['force','sans_armee']])ledger=Council.reduce(ledger,{type:'motion',motion,choice},camp,camp.v059Madame).ledger;
 assert.equal(ledger.status,'deliberating');
 assert.equal(ledger.journal.filter(item=>item.type==='motion').length,5);
});

test('candidatures: projection, alternative et fragmentation restent toujours recevables après les motions',()=>{
 const camp=campaign(),ledger=deliberate(camp),list=Council.candidates(ledger,camp,camp.v059Madame);
 const byId=Object.fromEntries(list.map(item=>[item.id,item]));
 assert.equal(byId.charte_vivants.eligible,true);
 assert.equal(byId.republique_services.eligible,true);
 assert.equal(byId.fragmentation.eligible,true);
 assert.equal(list[0].id,'charte_vivants');
});

test('prévision: le vote est déterministe et attribue exactement treize suffrages',()=>{
 const camp=campaign(),ledger=deliberate(camp),a=Council.candidates(ledger,camp,camp.v059Madame).find(item=>item.id==='charte_vivants').forecast,b=Council.forecastVotes('charte_vivants',ledger.clauses,camp.v059Madame);
 assert.deepEqual(a,b);
 assert.equal(a.for+a.against+a.abstain,13);
 assert.equal(a.details.length,13);
});

test('ratification: une Charte des Vivants cohérente est adoptée et produit neuf diapositives',()=>{
 const camp=campaign(),ledger=deliberate(camp),plan=Council.reduce(ledger,{type:'ratify',path:'charte_vivants',at:8000},camp,camp.v059Madame);
 assert.equal(plan.ok,true);
 assert.equal(plan.passed,true);
 assert.equal(plan.ledger.status,'ratified');
 assert.equal(plan.ledger.charter,'charte_vivants');
 assert.ok(plan.ledger.tally.for>=7);
 assert.equal(plan.ledger.slides.length,9);
 assert.deepEqual(plan.ledger.slides.slice(2).map(item=>item.id),Council.NETWORKS.map(item=>item.id));
 assert.ok(plan.ledger.legitimacy>=0&&plan.ledger.legitimacy<=100);
});

test('rejet: une fragmentation sans majorité reste amendable et conserve le vote',()=>{
 const camp=campaign(),ledger=deliberate(camp),plan=Council.reduce(ledger,{type:'ratify',path:'fragmentation',at:8100},camp,camp.v059Madame);
 assert.equal(plan.ok,true);
 assert.equal(plan.passed,false);
 assert.equal(plan.ledger.status,'deliberating');
 assert.equal(plan.ledger.charter,null);
 assert.equal(plan.ledger.failedVotes.length,1);
 const amended=Council.reduce(plan.ledger,{type:'motion',motion:'force',choice:'gardes_locales'},camp,camp.v059Madame);
 assert.equal(amended.ok,true);
 assert.equal(amended.ledger.clauses.force,'gardes_locales');
});

test('exclusivité: une charte ratifiée ne peut plus être remplacée ni amendée',()=>{
 const camp=campaign(),ratified=Council.reduce(deliberate(camp),{type:'ratify',path:'charte_vivants'},camp,camp.v059Madame).ledger;
 assert.equal(Council.reduce(ratified,{type:'ratify',path:'republique_services'},camp,camp.v059Madame).ok,false);
 assert.equal(Council.reduce(ratified,{type:'motion',motion:'preuve',choice:'registre'},camp,camp.v059Madame).ok,false);
 assert.equal(ratified.charter,'charte_vivants');
});

test('réseaux: les épilogues restent textuels, bornés et mentionnent les valeurs avant/après',()=>{
 const camp=campaign(),ratified=Council.reduce(deliberate(camp),{type:'ratify',path:'republique_services'},camp,camp.v059Madame).ledger;
 for(const slide of ratified.slides.slice(2)){
  assert.match(slide.text,/Projection du registre/);
  assert.doesNotMatch(slide.text,/NaN|undefined/);
  const numbers=[...slide.text.matchAll(/(?:accès|légitimité|coercion|résilience) (\d+)→(\d+)/g)].flatMap(match=>[Number(match[1]),Number(match[2])]);
  assert.equal(numbers.length,8);
  assert.equal(numbers.every(value=>value>=0&&value<=100),true);
 }
});

test('bulletins: les cinq états du conseil donnent une information cohérente',()=>{
 const locked=campaign(false),camp=campaign();
 assert.match(Council.bulletin(Council.fresh(),locked,locked.v059Madame),/six chartes/i);
 let ledger=Council.synchronize(Council.fresh(),camp,camp.v059Madame);
 assert.match(Council.bulletin(ledger,camp,camp.v059Madame),/convocation/i);
 ledger=Council.reduce(ledger,{type:'convene'},camp,camp.v059Madame).ledger;
 assert.match(Council.bulletin(ledger,camp,camp.v059Madame),/0\/4/);
 ledger=deliberate(camp);
 assert.match(Council.bulletin(ledger,camp,camp.v059Madame),/ratification/i);
 ledger=Council.reduce(ledger,{type:'ratify',path:'charte_vivants'},camp,camp.v059Madame).ledger;
 assert.match(Council.bulletin(ledger,camp,camp.v059Madame),/ratifiée/i);
});

test('robustesse: les actions inconnues sont refusées sans mutation de l’état fourni',()=>{
 const camp=campaign(),ledger=deliberate(camp),snapshot=structuredClone(ledger);
 assert.equal(Council.reduce(ledger,{type:'motion',motion:'preuve',choice:'inconnue'},camp,camp.v059Madame).ok,false);
 assert.equal(Council.reduce(ledger,{type:'ratify',path:'inconnue'},camp,camp.v059Madame).ok,false);
 assert.deepEqual(ledger,snapshot);
});

test('intégration statique: sauvegarde, Mireille, Pip-Boy, radio, journal et écran régional sont câblés',()=>{
 const source=fs.readFileSync(path.join(__dirname,'../../src/v050/10c_conseil_regional.js'),'utf8');
 for(const token of ['v060Council','migrateState=function','saveGame=function','talkMireille=function','continueExplore=function','showEnding=function','CONSEIL RÉGIONAL','c60:motion','c60:ratify','V027_STATIONS.council','ÉTATS GÉNÉRAUX DU MISTRAL','v060CouncilInfo'])assert.match(source,new RegExp(token.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')));
});
