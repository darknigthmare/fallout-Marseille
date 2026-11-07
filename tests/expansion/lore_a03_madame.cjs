'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Madame=require('../../src/v050/10b_a03_madame.js');

function campaign(overrides={}){
 return{
  playTime:120,
  flags:{rationDenied:false,archiveMemo:false,relayPowered:false,marseilleArchiveRead:false,cinemaResolved:false,notes:{},...(overrides.flags||{})},
  quest:{main:0,relayOutcome:null,finalOutcome:null,mainComplete:false,routesOutcome:null,routesComplete:false,waterOutcome:null,waterComplete:false,industryOutcome:null,industryComplete:false,marseilleOutcome:null,marseilleComplete:false,aubagneOutcome:null,aubagneComplete:false,...(overrides.quest||{})},
  rep:{},
  v053Lore:{quests:{...(overrides.v053Lore?.quests||{})}},
  v054Services:{quests:{...(overrides.v054Services?.quests||{})}}
 };
}

function winnerFor(finalOutcome){
 const c=campaign({flags:{rationDenied:true,archiveMemo:true,relayPowered:true,notes:{'journal-a03':true,'marseille-proof':true}},quest:{main:11,relayOutcome:'negotiate',finalOutcome,mainComplete:true}});
 return Madame.synchronize(Madame.fresh(),c).projection.winner;
}

test('fresh: le registre contient sept réseaux et huit projections politiques',()=>{
 const state=Madame.fresh();
 assert.equal(state.schema,1);
 assert.deepEqual(Object.keys(state.networks),['identite','eau','sante','transport','energie','communication','approvisionnement']);
 assert.equal(Madame.ENDINGS.length,8);
 assert.equal(Object.keys(state.scores).length,8);
});

test('migration: les preuves historiques sont déduites sans muter la campagne',()=>{
 const source=campaign({flags:{rationDenied:true,archiveMemo:true,relayPowered:true,marseilleArchiveRead:true,notes:{'journal-a03':true,'marseille-proof':true}},quest:{main:11,relayOutcome:'negotiate',finalOutcome:'federation',mainComplete:true,treilleOutcome:'testimony',waterOutcome:'right',waterComplete:true,cinemaOutcome:'communes'}});
 const snapshot=structuredClone(source);
 const result=Madame.synchronize(null,source);
 assert.deepEqual(source,snapshot);
 assert.equal(result.identity.status,'recognized');
 assert.equal(result.identity.relayMethod,'negotiate');
 for(const key of ['body','deathNotice','terminalTrace','a03Journal','relayRecognition','regionalSignatures','publicWitnesses','hydraulicRegisters','visualArchives'])assert.equal(result.identity.evidence[key],true,key);
 assert.equal(result.projection.winner,'charte_vivants');
});

test('requête M.A.D.A.M.E.: un choix est exclusif et la source reste intacte',()=>{
 const raw=Madame.fresh(),snapshot=structuredClone(raw),c=campaign({flags:{rationDenied:true,notes:{'journal-a03':true}}});
 const first=Madame.reduce(raw,{type:'petition',choice:'plurality'},c);
 assert.equal(first.ok,true);
 assert.deepEqual(raw,snapshot);
 assert.equal(first.ledger.identity.terminalPetition,'plurality');
 assert.equal(first.ledger.identity.evidence.a03Journal,true);
 const second=Madame.reduce(first.ledger,{type:'petition',choice:'trace'},c);
 assert.equal(second.ok,false);
 assert.equal(second.ledger.identity.terminalPetition,'plurality');
});

test('témoignage d’Odette: la forme est persistante et non remplaçable',()=>{
 const c=campaign({flags:{rationDenied:true,notes:{'journal-a03':true}}});
 const first=Madame.reduce(Madame.fresh(),{type:'odette',choice:'protect'},c);
 assert.equal(first.ok,true);
 assert.equal(first.ledger.identity.odetteChoice,'protect');
 assert.equal(first.ledger.identity.evidence.odetteTestimony,true);
 const second=Madame.reduce(first.ledger,{type:'odette',choice:'attestation'},c);
 assert.equal(second.ok,false);
});

test('les quatre conclusions du chapitre identitaire produisent quatre axes dominants distincts',()=>{
 assert.equal(winnerFor('continuity'),'continuite');
 assert.equal(winnerFor('federation'),'federation');
 assert.equal(winnerFor('workers'),'travailleurs');
 assert.equal(winnerFor('fragment'),'fragmentation');
});

test('les dossiers de services modifient réellement santé, transport, énergie et approvisionnement',()=>{
 const base=Madame.synchronize(Madame.fresh(),campaign());
 const c=campaign({v054Services:{quests:{
  carte_verte:{outcome:'urgence_universelle'},
  terminus_humain:{outcome:'quai_humain'},
  dose_collective:{outcome:'dosimetres_partages'},
  pavillon_secours:{outcome:'corridor_civil'}
 }}});
 const result=Madame.synchronize(Madame.fresh(),c);
 assert.ok(result.networks.sante.access>base.networks.sante.access);
 assert.ok(result.networks.transport.access>base.networks.transport.access);
 assert.ok(result.networks.energie.legitimacy>base.networks.energie.legitimacy);
 assert.ok(result.networks.approvisionnement.access>base.networks.approvisionnement.access);
});

test('une campagne de services publics cohérente projette une République des Services',()=>{
 const c=campaign({
  flags:{rationDenied:true,archiveMemo:true,relayPowered:true,marseilleArchiveRead:true,notes:{'journal-a03':true,'marseille-proof':true}},
  quest:{main:59,relayOutcome:'repair',finalOutcome:'federation',mainComplete:true,routesOutcome:'public',routesComplete:true,waterOutcome:'priority',waterComplete:true,industryOutcome:'public',industryComplete:true,marseilleOutcome:'public',marseilleComplete:true,aubagneOutcome:'public',aubagneComplete:true,signalOutcome:'public'},
  v054Services:{quests:{carte_verte:{outcome:'cotisation_locale'},terminus_humain:{outcome:'horaire_manuel'},dose_collective:{outcome:'cordon_civil'},pavillon_secours:{outcome:'convoi_enregistre'}}}
 });
 const result=Madame.synchronize(Madame.fresh(),c);
 assert.equal(result.projection.winner,'republique_services');
 assert.ok(result.projection.confidence>=80);
});

test('les métriques des réseaux restent bornées et la projection est déterministe',()=>{
 const c=campaign({flags:{rationDenied:true,archiveMemo:true,relayPowered:true,notes:{'journal-a03':true}},quest:{main:59,relayOutcome:'force',finalOutcome:'continuity',mainComplete:true,routesOutcome:'concessions',routesComplete:true,waterOutcome:'concessions',waterComplete:true,industryOutcome:'arsenal',industryComplete:true,marseilleOutcome:'concessions',marseilleComplete:true,aubagneOutcome:'concessions',aubagneComplete:true,signalOutcome:'subscription',firewatchOutcome:'command'}});
 const a=Madame.synchronize(Madame.fresh(),c),b=Madame.synchronize(Madame.fresh(),c);
 assert.deepEqual(a,b);
 for(const network of Object.values(a.networks))for(const metric of ['access','legitimacy','coercion','resilience'])assert.ok(network[metric]>=0&&network[metric]<=100,`${network.id}.${metric}`);
});

test('les actions inconnues sont refusées sans altérer le registre',()=>{
 const raw=Madame.fresh(),snapshot=structuredClone(raw);
 const result=Madame.reduce(raw,{type:'pirate',choice:'x'},campaign());
 assert.equal(result.ok,false);
 assert.deepEqual(raw,snapshot);
});

test('intégration statique: sauvegarde, borne, Odette, relais, Pip-Boy, radio et debug sont câblés',()=>{
 const source=fs.readFileSync(path.join(__dirname,'../../src/v050/10b_a03_madame.js'),'utf8');
 for(const token of ['v059Madame','interactRationTerminal=function','interactVaultExit=function','talkOdette=function','resolveRelay=function','completeChapter=wrapMilestone','M.A.D.A.M.E. ET SEPT RÉSEAUX','V027_STATIONS.madame','v059MadameInfo'])assert.match(source,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
});
