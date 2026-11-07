'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Lore=require('../../src/v050/10a_lore_services.js');

const CONTACTS=[
 {id:'v042-marseille-caravan-01',name:'Halte caravanière · Vieux-Port',safe:true},
 {id:'v042-marseille-caravan-02',name:'Relais marchand · Saint-Charles',safe:true},
 {id:'v042-huveaune-caravan-01',name:'Halte caravanière · Vallée de l’Huveaune',safe:true},
 {id:'v042-laciotat-caravan-01',name:'Halte caravanière · La Ciotat',safe:true}
];
const richInventory={water:99,food:99,cloth:99,antibiotics:99,circuitry:99,scrap:99};

function openThenResolve(questId,choiceId){
 const bindings=Lore.bind(CONTACTS);
 let ledger=Lore.fresh();
 let plan=Lore.reduce(ledger,bindings,{type:'accept',quest:questId},{atGiver:true,inventory:richInventory,playTime:10});
 assert.equal(plan.ok,true);ledger=plan.ledger;
 plan=Lore.reduce(ledger,bindings,{type:'resolve',quest:questId,choice:choiceId},{atGiver:true,inventory:richInventory,playTime:20});
 return{bindings,plan};
}

test('catalogue: quatre dossiers, quatre factions et sept réseaux distincts',()=>{
 assert.equal(Lore.catalog().length,4);
 assert.deepEqual(Lore.IDS,['carte_verte','terminus_humain','dose_collective','pavillon_secours']);
 assert.deepEqual(Lore.FACTIONS,['sociale','aiguilleurs','commissariat','amiraute']);
 assert.equal(Lore.NETWORKS.length,7);
 assert.equal(new Set(Lore.NETWORKS.map(item=>item.id)).size,7);
});

test('liaisons: chaque dossier pointe vers un relais réel et sûr du catalogue v0.42',()=>{
 const bindings=Lore.bind(CONTACTS);
 assert.equal(bindings.every(quest=>quest.available),true);
 assert.deepEqual(bindings.map(quest=>quest.contactSite),CONTACTS.map(site=>site.id));
 const unsafe=Lore.bind(CONTACTS.map((site,index)=>index===2?{...site,safe:false}:site));
 assert.equal(unsafe.find(quest=>quest.id==='dose_collective').available,false);
});

test('migration: une sauvegarde partielle est complétée sans accepter une issue inconnue',()=>{
 const bindings=Lore.bind(CONTACTS);
 const migrated=Lore.migrate({schema:0,quests:{carte_verte:{accepted:true,outcome:'urgence_universelle'},terminus_humain:{accepted:true,outcome:'inconnue'}},journal:[{type:'accepted',quest:'carte_verte',at:1},{type:'hack',quest:'carte_verte'}]},bindings);
 assert.equal(migrated.schema,1);
 assert.deepEqual(migrated.quests.carte_verte,{accepted:true,outcome:'urgence_universelle'});
 assert.deepEqual(migrated.quests.terminus_humain,{accepted:true,outcome:null});
 assert.equal(migrated.quests.dose_collective.accepted,false);
 assert.equal(migrated.journal.length,1);
});

test('ouverture: le contact physique est requis et l’entrée ne peut pas être répétée',()=>{
 const bindings=Lore.bind(CONTACTS),before=Lore.fresh();
 const denied=Lore.reduce(before,bindings,{type:'accept',quest:'carte_verte'},{atGiver:false,inventory:richInventory});
 assert.equal(denied.ok,false);
 assert.deepEqual(before,Lore.fresh());
 const opened=Lore.reduce(before,bindings,{type:'accept',quest:'carte_verte'},{atGiver:true,inventory:richInventory});
 assert.equal(opened.ok,true);
 assert.equal(opened.ledger.quests.carte_verte.accepted,true);
 const repeated=Lore.reduce(opened.ledger,bindings,{type:'accept',quest:'carte_verte'},{atGiver:true,inventory:richInventory});
 assert.equal(repeated.ok,false);
});

test('résolution: chaque dossier consomme une quantité finie et conserve une issue exclusive',()=>{
 for(const quest of Lore.catalog()){
  const {plan}=openThenResolve(quest.id,quest.choices[0].id);
  assert.equal(plan.ok,true,quest.id);
  assert.deepEqual(plan.cost,quest.choices[0].cost,quest.id);
  assert.equal(plan.ledger.quests[quest.id].outcome,quest.choices[0].id,quest.id);
  const bindings=Lore.bind(CONTACTS);
  const second=Lore.reduce(plan.ledger,bindings,{type:'resolve',quest:quest.id,choice:quest.choices[1].id},{atGiver:true,inventory:richInventory});
  assert.equal(second.ok,false,quest.id);
 }
});

test('économie: des fournitures insuffisantes refusent la décision sans muter l’entrée',()=>{
 const bindings=Lore.bind(CONTACTS);
 const opened=Lore.reduce(Lore.fresh(),bindings,{type:'accept',quest:'pavillon_secours'},{atGiver:true,inventory:{}}).ledger;
 const snapshot=structuredClone(opened);
 const denied=Lore.reduce(opened,bindings,{type:'resolve',quest:'pavillon_secours',choice:'corridor_civil'},{atGiver:true,inventory:{water:2,food:3}});
 assert.equal(denied.ok,false);
 assert.deepEqual(opened,snapshot);
 assert.equal(denied.ledger.quests.pavillon_secours.outcome,null);
});

test('conséquences: les textes n’affirment ni train, flotte, clinique ou décontamination simulés',()=>{
 const text=Lore.catalog().flatMap(quest=>quest.choices.map(choice=>choice.text)).join('\n').toLowerCase();
 assert.match(text,/aucun train/);
 assert.match(text,/aucun bâtiment/);
 assert.match(text,/ni hôpital ouvert/);
 assert.match(text,/aucune décontamination/);
});

test('bulletins: l’état ouvert puis résolu est reflété sans modifier le registre',()=>{
 const bindings=Lore.bind(CONTACTS),fresh=Lore.fresh();
 const original=structuredClone(fresh);
 assert.match(Lore.bulletin('sociale',fresh,bindings),/La Sociale/);
 assert.deepEqual(fresh,original);
 const opened=Lore.reduce(fresh,bindings,{type:'accept',quest:'carte_verte'},{atGiver:true,inventory:richInventory}).ledger;
 assert.match(Lore.bulletin('sociale',opened,bindings),/dossier est ouvert/i);
 const resolved=Lore.reduce(opened,bindings,{type:'resolve',quest:'carte_verte',choice:'urgence_universelle'},{atGiver:true,inventory:richInventory}).ledger;
 assert.match(Lore.bulletin('sociale',resolved,bindings),/trousse d’urgence/i);
});

test('intégration statique: état versionné, migration, actions Pip-Boy et hook de debug sont câblés',()=>{
 const source=fs.readFileSync(path.join(__dirname,'../../src/v050/10a_lore_services.js'),'utf8');
 for(const token of ['v054Services','migrateState=function','SERVICES ET SOUVERAINETÉS','l54:accept','l54:resolve','l54:track','serviceLore'])assert.match(source,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
});
