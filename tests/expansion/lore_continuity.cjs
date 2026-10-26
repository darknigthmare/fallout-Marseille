'use strict';
/* New narrative transactions use the actual immutable v0.42 site catalogue.
   NPC positions, storage and scene state below are explicit controlled seams,
   not a native city playthrough or a recovered ChatGPT conversation. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),test=require('node:test');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'src/v050/10_lore_continuity.js'),'utf8'),oldLore=fs.readFileSync(path.join(root,'src/v046/04_lore.js'),'utf8'),catalogSource=fs.readFileSync(path.join(root,'src/v042/00_catalog.js'),'utf8'),G=require('../../src/v050/10_lore_continuity.js'),clone=v=>JSON.parse(JSON.stringify(v));
const catalogContext=vm.createContext({});vm.runInContext(catalogSource+';globalThis.exportCatalog=V042_CATALOG;',catalogContext);const catalog=clone(catalogContext.exportCatalog),bindings=G.bind(catalog);
const quest=id=>bindings.find(q=>q.id===id),giver=(id,extra={})=>({atGiver:true,contact:true,inventory:{water:5,food:5,antibiotics:2,circuitry:2,scrap:5,cloth:3},intelligence:6,playTime:90,...extra}),step=(s,type,id,ctx={},choice)=>G.reduce(s,bindings,{type,quest:id,choice},ctx);
function opened(id){return step(G.fresh(),'accept',id,giver(id)).ledger;}
function witnesses(s,id){for(const siteId of quest(id).witnessSites.slice(0,2))s=step(s,'witness',id,giver(id,{siteId})).ledger;return s;}

test('Six faction dossiers bind only existing sites without moving the catalogue',()=>{
 const before=clone(catalog),out=G.bind(catalog);assert.deepEqual(catalog,before);assert.deepEqual(out.map(q=>q.faction),['convention','concorde','vigies','insulaires','syndicat','sansdossier']);assert.equal(new Set(out.map(q=>q.id)).size,6);assert.ok(out.every(q=>q.available));
 for(const q of out){const site=catalog.find(s=>s.id===q.contactSite);assert.ok(site.safe&&site.npcSlots>0&&site.macro===q.macro);for(const id of q.observationSites)assert.equal(catalog.find(s=>s.id===id).kind,'landmark');assert.ok(q.choices.length===2);}
 assert.equal(quest('signaux').observationSites.length,3);
});

test('An absent compatible host remains unavailable instead of inventing a new placement',()=>{
 const out=G.bind([]);assert.ok(out.every(q=>!q.available&&q.contactSite===null));assert.equal(G.reduce(G.fresh(),out,{type:'accept',quest:'cendres'},giver('cendres')).ok,false);
});

test('Catalogues and outcomes returned to callers cannot edit private narrative definitions',()=>{
 const first=G.catalog();first[0].choices[0].rep.ligue=100;first[0].name='changed';assert.equal(G.catalog()[0].name,'Le droit d’être compté');assert.equal(G.catalog()[0].choices[0].rep.ligue,2);bindings[0].description=bindings[0].description;assert.equal(G.IDS.length,6);
});

test('Remote acceptance and a blocked contact cannot create an accepted dossier',()=>{
 const s=G.fresh();assert.equal(step(s,'accept','cendres',giver('cendres',{atGiver:false})).ok,false);assert.equal(step(s,'accept','cendres',giver('cendres',{blocked:'combat'})).ok,false);assert.deepEqual(s,G.fresh());
});

test('Testimonies require two different eligible physical relays and reward only once',()=>{
 let s=opened('cendres'),first=quest('cendres').witnessSites[0];assert.equal(step(s,'witness','cendres',giver('cendres',{siteId:'unknown'})).ok,false);assert.equal(step(s,'resolve','cendres',giver('cendres'),'anonymes').ok,false);s=step(s,'witness','cendres',giver('cendres',{siteId:first})).ledger;assert.equal(step(s,'witness','cendres',giver('cendres',{siteId:first})).ok,false);s=step(s,'witness','cendres',giver('cendres',{siteId:quest('cendres').witnessSites[1]})).ledger;const out=step(s,'resolve','cendres',giver('cendres'),'anonymes');assert.equal(out.ok,true);assert.equal(out.reward.rep.ligue,2);assert.equal(out.reward.faction,'convention');assert.equal(out.ledger.journal.length,1);assert.equal(step(out.ledger,'resolve','cendres',giver('cendres'),'registre').ok,false);assert.equal(s.quests.cendres.outcome,null);
});

test('A technical audit pays one circuit after an Intelligence check; testimonies are an alternative',()=>{
 const s=opened('formulaire');assert.equal(step(s,'audit','formulaire',giver('formulaire',{intelligence:4})).ok,false);assert.equal(step(s,'audit','formulaire',giver('formulaire',{inventory:{}})).ok,false);const technical=step(s,'audit','formulaire',giver('formulaire'));assert.equal(technical.ok,true);assert.deepEqual(technical.cost,{circuitry:1});assert.equal(step(technical.ledger,'audit','formulaire',giver('formulaire')).ok,false);assert.ok(G.progress(quest('formulaire'),technical.ledger.quests.formulaire).ready);const social=witnesses(s,'formulaire');assert.equal(social.quests.formulaire.audit,false);assert.ok(G.progress(quest('formulaire'),social.quests.formulaire).ready);
});

test('Three unique source landmarks must be physically examined before the Vigies decision',()=>{
 let s=opened('signaux');for(const siteId of quest('signaux').observationSites){assert.equal(step(s,'observe','signaux',{siteId,physicalObservation:false}).ok,false);s=step(s,'observe','signaux',{siteId,physicalObservation:true}).ledger;assert.equal(step(s,'observe','signaux',{siteId,physicalObservation:true}).ok,false);}assert.equal(s.quests.signaux.observations.length,3);assert.equal(step(s,'resolve','signaux',giver('signaux',{atGiver:false}),'alerte').ok,false);const done=step(s,'resolve','signaux',giver('signaux'),'alerte');assert.equal(done.ok,true);assert.equal(done.reward.rep.secours,3);
});

test('Lazaret decisions have distinct real supplies and no partial payment',()=>{
 const s=opened('lazaret'),before=clone(s);assert.equal(step(s,'resolve','lazaret',giver('lazaret',{inventory:{water:2,food:1}}),'passage').ok,false);assert.deepEqual(s,before);const supplies=step(s,'resolve','lazaret',giver('lazaret'),'passage'),care=step(s,'resolve','lazaret',giver('lazaret'),'soins');assert.deepEqual(supplies.cost,{water:2,food:2});assert.deepEqual(care.cost,{water:2,antibiotics:1});assert.notDeepEqual(supplies.reward.rep,care.reward.rep);assert.notEqual(supplies.reward.text,care.reward.text);
});

test('Migration bounds and revalidates proofs, unknown quests and duplicated decisions',()=>{
 const old={quests:{cendres:{accepted:true,witnesses:['unknown',...quest('cendres').witnessSites,...quest('cendres').witnessSites],observations:['bad'],outcome:'not-a-choice'},lazaret:{accepted:false,outcome:'soins'},unknown:{accepted:true}},journal:Array.from({length:500},()=>({quest:'lazaret',choice:'soins',playTime:Infinity}))},m=G.migrate(old,bindings);assert.equal(m.quests.cendres.witnesses.length,2);assert.equal(m.quests.cendres.outcome,null);assert.equal(m.quests.lazaret.accepted,true);assert.equal(m.journal.length,1);assert.equal(m.journal[0].playTime,0);assert.equal(m.quests.unknown,undefined);assert.deepEqual(G.migrate(null,bindings),G.fresh());assert.equal(G.migrate({quests:{cendres:{accepted:false,witnesses:quest('cendres').witnessSites}}},bindings).quests.cendres.witnesses.length,0);
});

test('Bulletins reflect only conserved outcomes and preserve legacy COCHONNET victories',()=>{
 const fresh=G.fresh(),pending=G.bulletin('canal13',fresh,bindings),done=step(witnesses(opened('cendres'),'cendres'),'resolve','cendres',giver('cendres'),'anonymes').ledger;assert.ok(!pending.includes('Les attestations restent'));assert.ok(G.bulletin('canal13',done,bindings).includes('Les attestations restent'));assert.match(G.bulletin('centtreves',fresh,bindings,{petanque:{played:3,wins:1},done:{encore:true}}),/3 mènes, 1 victoires/);assert.match(G.bulletin('lazaret',fresh,bindings),/attend de l’eau/);
});

function runtime(){
 const c=vm.createContext({console});vm.runInContext(catalogSource,c);
 vm.runInContext(`
 const test={saves:0,saved:null,fail:false,throwSave:false,sight:true,threat:false,baseReads:0,legacyTrades:0,dialogue:null,notes:[],readHook:null};
 function deepClone(v){return JSON.parse(JSON.stringify(v));}function clamp(n,a,b){return Math.max(a,Math.min(b,n));}
 let gameStarted=true,mode='PIP',zoneTransitioning=false,onGround=true;
 const V046={busy:false,lab:false},V047={pending:null},V042_RUNTIME={npcData:new Map()},V027_SUBS={data:{france:'FRANCE EN CENDRES'}},V027={sub:'france',tab:'data',message:''},V027_STATIONS={legacy:{name:'Unchanged station'}},WEAPONS={};
 function baseState(){return{player:{zone:'geo_marseille',pos:[0,1.65,0],hp:100,caps:100,xp:0,level:1},inventory:{water:5,food:5,antibiotics:2,circuitry:2,scrap:5,cloth:3},character:{special:{I:6}},rep:{ligue:0,continuite:0,francs:0,secours:0,veilleurs:0},achievements:[],flags:{},v046:{lore:{done:{},accepted:{},reputation:{},petanque:{played:0,wins:0}}},v042:{discovered:{},visited:{},cleared:{},tracked:null},lastSave:'before'};}
 function migrateState(s={}){return deepClone(s.player?s:baseState());}let state=baseState(),world={id:'geo_marseille',v046:true,geoMacro:true,npcs:[],enemies:[],interactables:[]};
 function v049Own(){}function saveGame(){test.saves++;state.lastSave='attempted-save';if(test.throwSave)throw Error('disk full');if(test.fail)return false;test.saved=JSON.stringify(state);return true;}
 function gainXP(n){state.player.xp+=n;}function toast(){}function renderPipboy(){}function updateQuestUI(){}function addItem(id,n){state.inventory[id]=(state.inventory[id]||0)+n;}
 function v042Site(id){return V042_CATALOG.find(s=>s.id===id)||null;}function v042SiteDiscovered(s){return !!state.v042.discovered[s.id];}function v042Discover(s){state.v042.discovered[s.id]=true;}
 function dist2(a,b){return Math.hypot(a[0]-b[0],a[2]-b[2]);}function lineOfSight(){return test.sight;}function v050TravelNearbyThreat(){return test.threat;}
 function v042ReadSite(id){test.baseReads++;state.v042.visited[id]=true;mode='NOTE';if(test.readHook)test.readHook();return 'read-base';}
 function v042TalkNPC(){test.legacyTrades++;return 'legacy-talk';}function speaker(name,role){return{name,role};}function openDialogue(person,text,choices){test.dialogue={person,text,choices};mode='DIALOGUE';}function closeDialogue(){mode='PLAYING';}
 function v027Open(tab,sub){V027.tab=tab;V027.sub=sub;mode='PIP';return true;}function v027Data(c){c.innerHTML='legacy-data';}function v027Dispatch(){return 'legacy-dispatch';}function v027CanAct(){return mode==='PIP'&&!zoneTransitioning&&state.player.hp>0;}
 function v027QuestRows(){return[{id:'legacy-quest',name:'Legacy quest',stage:'active'}];}function v027Track(){return 'legacy-track';}
 function v027Escape(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}function v027Button(t,a,arg='',disabled=false){return '<button data-p27="'+a+'" data-arg="'+arg+'"'+(disabled?' disabled':'')+'>'+t+'</button>';}
 function detailHash(s){return Array.from(s).reduce((h,c)=>((h*31)^c.charCodeAt(0))>>>0,0);}function detailRng(){return()=>.1;}
 globalThis.window=globalThis;window.__MISTRAL_DEBUG={};
 `,c);vm.runInContext(oldLore,c);vm.runInContext(source,c,{filename:'10_lore_continuity.js'});vm.runInContext(`v053LoreAfterInit();globalThis.d=window.__MISTRAL_DEBUG;
 function placeSite(siteId){const site=v042Site(siteId),id='npc:'+siteId;world.id=site.macro;world.npcs=[{id,alive:true,v042Site:siteId,pos:[1,0,1]}];V042_RUNTIME.npcData.clear();V042_RUNTIME.npcData.set(id,{siteId,name:'Explicit fixture NPC',role:'contact'});state.v042.discovered[siteId]=true;state.player.pos=[1,1.65,2];return id;}
 function placeGiver(id){return placeSite(d.v053LoreInfo().quests.find(q=>q.id===id).contactSite);}
 function observeSite(id){world.interactables=[{id:'v042-lore-'+id,pos:[0,1,0]}];state.player.pos=[0,1.65,1];mode='PLAYING';return v042ReadSite(id);}
 `,c);
 return{run:s=>vm.runInContext(s,c),json:s=>clone(vm.runInContext(s,c)),set:(name,value)=>{c[name]=value;}};
}

test('Runtime adds a separate ledger and leaves all eight historical dossiers, nine factions and 25 testimony names intact',()=>{
 const f=runtime();assert.equal(f.run('V046_LORE.quests.length'),8);assert.equal(f.run('V046_LORE.factions.length'),9);assert.equal(f.run('V046_LORE.bestiary.length'),25);assert.equal(f.run('d.v053LoreInfo().quests.length'),6);assert.equal(f.run('V027_SUBS.data.continuity'),'RELAIS ET DOSSIERS');assert.equal(f.run('V027_STATIONS.legacy.name'),'Unchanged station');assert.equal(f.run('v027Dispatch("other","x")'),'legacy-dispatch');assert.equal(f.run('v027Track("legacy-quest")'),'legacy-track');
});

for(const failure of['distance','line of sight','dead NPC','undiscovered','loading','combat','airborne','lab','dead player','scene'])test('A '+failure+' contact cannot open or pay a new dossier',()=>{
 const f=runtime();f.run('placeGiver("lazaret")');const patches={distance:'state.player.pos=[30,1.65,30]','line of sight':'test.sight=false','dead NPC':'world.npcs[0].alive=false',undiscovered:'state.v042.discovered={}',loading:'V046.busy=true',combat:'test.threat=true',airborne:'onGround=false',lab:'V046.lab=true','dead player':'state.player.hp=0',scene:'world.v046=false'};f.run(patches[failure]);const before=f.json('state');assert.equal(f.run('d.v053LoreAccept("lazaret")'),false);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saves'),0);
});

test('A delivery is paid and rewarded exactly once, survives migration and affects existing reputation keys',()=>{
 const f=runtime();f.run('placeGiver("lazaret")');assert.equal(f.run('d.v053LoreAccept("lazaret")'),true);const before=f.json('state');assert.equal(f.run('d.v053LoreResolve("lazaret","soins")'),true);const after=f.json('state');assert.equal(after.inventory.water,before.inventory.water-2);assert.equal(after.inventory.antibiotics,before.inventory.antibiotics-1);assert.equal(after.player.caps,before.player.caps+35);assert.equal(after.player.xp,before.player.xp+80);assert.equal(after.rep.francs,2);assert.equal(after.rep.secours,1);assert.equal(after.v046.lore.reputation.insulaires,3);f.run('state=migrateState(JSON.parse(test.saved));placeGiver("lazaret")');const saved=f.json('state');assert.equal(f.run('d.v053LoreResolve("lazaret","passage")'),false);assert.deepEqual(f.json('state'),saved);assert.equal(f.run('V027_STATIONS.lazaret.text().includes("antibiotiques")'),true);
});

for(const throwing of[false,true])test('A '+(throwing?'throwing':'false-returning')+' persistence failure restores supplies, XP, both reputation ledgers and the prior decision',()=>{
 const f=runtime();f.run('placeGiver("lazaret");d.v053LoreAccept("lazaret")');const before=f.json('state'),saved=f.run('test.saved');f.run(throwing?'test.throwSave=true':'test.fail=true');assert.equal(f.run('d.v053LoreResolve("lazaret","soins")'),false);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),saved);assert.equal(f.run('V027_STATIONS.lazaret.text().includes("La réserve de soin est remise")'),false);
});

test('The dialogue callback rechecks position at the time of payment and keeps legacy conversation reachable',()=>{
 const f=runtime();const id=f.run('placeGiver("lazaret")');assert.equal(f.run('v042TalkNPC('+JSON.stringify(id)+')'),true);assert.ok(f.run('test.dialogue.choices.some(c=>c.text.includes("Ouvrir"))'));f.run('state.player.pos=[100,1.65,100];test.dialogue.choices.find(c=>c.text.includes("Ouvrir")).onChoose()');assert.equal(f.run('state.v053Lore.quests.lazaret.accepted'),false);f.run('placeGiver("lazaret");v042TalkNPC('+JSON.stringify(id)+');test.dialogue.choices.find(c=>c.text==="Parler du secteur et commercer.").onChoose()');assert.ok(f.run('test.dialogue.choices.some(c=>c.text==="Parler du secteur et commercer.")'));f.run('test.dialogue.choices.find(c=>c.text==="Parler du secteur et commercer.").onChoose()');assert.equal(f.run('test.legacyTrades'),1);
});

test('Testimony records distinct active source relays and the dossier appears in the actual quest journal',()=>{
 const f=runtime();f.run('placeGiver("cendres");d.v053LoreAccept("cendres")');const first=quest('cendres').witnessSites[0],second=quest('cendres').witnessSites[1];for(const id of[first,second]){f.run('placeSite('+JSON.stringify(id)+')');assert.equal(f.run('d.v053LoreWitness("cendres",'+JSON.stringify(id)+')'),true);}f.run('placeGiver("cendres")');assert.equal(f.run('d.v053LoreResolve("cendres","registre")'),true);const rows=f.json('v027QuestRows()');assert.equal(rows[0].id,'legacy-quest');assert.equal(rows.find(r=>r.id==='l53:cendres').stage,'done');assert.match(f.run('V027_STATIONS.canal13.text()'),/copie du registre/);
});

test('A remote note read cannot fabricate an observation, while three real proximity/LOS inspections persist',()=>{
 const f=runtime();f.run('placeGiver("signaux");d.v053LoreAccept("signaux");mode="PLAYING"');const ids=quest('signaux').observationSites;f.run('v042ReadSite('+JSON.stringify(ids[0])+')');assert.equal(f.run('state.v053Lore.quests.signaux.observations.length'),0);for(const id of ids){f.run('mode="PLAYING";observeSite('+JSON.stringify(id)+')');}assert.equal(f.run('state.v053Lore.quests.signaux.observations.length'),3);assert.equal(f.run('test.baseReads'),4);f.run('state=migrateState(JSON.parse(test.saved));mode="PIP";placeGiver("signaux")');assert.equal(f.run('d.v053LoreResolve("signaux","alerte")'),true);assert.equal(f.run('state.rep.secours'),3);
});

test('Observation after a base reader changes scene or save owner is not applied to the replacement',()=>{
 for(const patch of['world={...world,id:"other"}','state=migrateState(baseState())']){const f=runtime(),id=quest('signaux').observationSites[0];f.run('placeGiver("signaux");d.v053LoreAccept("signaux");test.readHook=()=>{'+patch+'};observeSite('+JSON.stringify(id)+')');assert.equal(f.run('state.v053Lore.quests.signaux.observations.length'),0);}
});

test('Tracking chooses the next unrecorded site without validating a proof or granting a reward',()=>{
 const f=runtime();f.run('placeGiver("signaux");d.v053LoreAccept("signaux")');const before=f.json('state.v053Lore');assert.equal(f.run('d.v053LoreTrack("signaux")'),true);assert.equal(f.run('state.v042.tracked'),quest('signaux').observationSites[0]);assert.deepEqual(f.json('state.v053Lore'),before);assert.equal(f.run('state.player.caps'),100);f.run('test.fail=true');const target=f.run('state.v042.tracked'),last=f.run('state.lastSave');assert.equal(f.run('d.v053LoreTrack("signaux")'),false);assert.equal(f.run('state.v042.tracked'),target);assert.equal(f.run('state.lastSave'),last);
});

test('New game and another save do not inherit proofs, decisions or faction broadcasts',()=>{
 const f=runtime();f.run('placeGiver("lazaret");d.v053LoreAccept("lazaret");d.v053LoreResolve("lazaret","passage");state=migrateState(baseState())');assert.equal(f.run('state.v053Lore.quests.lazaret.accepted'),false);assert.equal(f.run('state.v053Lore.journal.length'),0);assert.equal(f.run('V027_STATIONS.lazaret.text().includes("Le passage accompagné reçoit")'),false);
});

test('The Pip-Boy continuity panel reports evidence and disables remote payment while preserving legacy France content',()=>{
 const f=runtime();f.run('globalThis.container={innerHTML:"",querySelectorAll:()=>[],insertAdjacentHTML(where,extra){this.innerHTML+=extra;}};V027.sub="continuity";v027Data(container)');assert.match(f.run('container.innerHTML'),/Le droit d’être compté/);assert.match(f.run('container.innerHTML'),/data-p27="l53:accept"[^>]*disabled/);f.run('V027.sub="france";v027Data(container)');assert.match(f.run('container.innerHTML'),/Dossiers régionaux/);assert.match(f.run('container.innerHTML'),/Consulter les dossiers des relais/);f.run('V027.sub="other";v027Data(container)');assert.equal(f.run('container.innerHTML'),'legacy-data');
});

test('Appending the new France link preserves historical quest and COCHONNET button listeners',()=>{
 const f=runtime();f.run(`globalThis.boundButtons=[];globalThis.domFixture={_html:'',get innerHTML(){return this._html;},set innerHTML(value){this._html=value;boundButtons=[];for(const m of value.matchAll(/data-v46-quest="([^"]+)"/g))boundButtons.push({dataset:{v46Quest:m[1]}});for(const m of value.matchAll(/data-v46-boule="([^"]+)"/g))boundButtons.push({dataset:{v46Boule:m[1]}});},querySelectorAll(selector){return boundButtons.filter(b=>selector.includes('quest')?b.dataset.v46Quest:b.dataset.v46Boule);},insertAdjacentHTML(where,extra){this._html+=extra;}};V027.sub='france';v027Data(domFixture)`);
 assert.equal(f.run('boundButtons.length'),10);assert.equal(f.run('boundButtons.every(b=>typeof b.onclick==="function")'),true);f.run('boundButtons.find(b=>b.dataset.v46Boule==="pointer").onclick()');assert.equal(f.run('state.v046.lore.petanque.played'),1);assert.equal(f.run('state.v046.lore.petanque.wins'),1);
});


test('Syndicat binds the existing memorial and wreck, not a replacement when a named observation is absent',()=>{
 const q=quest('cadences');assert.equal(q.contactSite,'v042-laciotat-caravan-01');assert.deepEqual(q.observationSites,['v042-laciotat-landmark-01','v042-laciotat-landmark-03']);assert.equal(G.bind(catalog.filter(s=>s.id!=='v042-laciotat-landmark-03')).find(q=>q.id==='cadences').available,false);assert.equal(q.kind,'observation');
});

test('Syndicat requires both on-site observations before either exclusive allocation',()=>{
 let s=opened('cadences');for(const siteId of quest('cadences').observationSites){assert.equal(step(s,'resolve','cadences',giver('cadences'),'atelier').ok,false);assert.equal(step(s,'observe','cadences',{siteId,physicalObservation:false}).ok,false);s=step(s,'observe','cadences',{siteId,physicalObservation:true}).ledger;assert.equal(step(s,'observe','cadences',{siteId,physicalObservation:true}).ok,false);}assert.equal(step(s,'observe','cadences',{siteId:quest('signaux').observationSites[0],physicalObservation:true}).ok,false);assert.equal(step(s,'resolve','cadences',giver('cadences',{inventory:{scrap:2,circuitry:1}}),'atelier').ok,false);const atelier=step(s,'resolve','cadences',giver('cadences'),'atelier'),repos=step(s,'resolve','cadences',giver('cadences'),'repos');assert.deepEqual(atelier.cost,{scrap:3,circuitry:1});assert.deepEqual(repos.cost,{cloth:2,water:2});assert.equal(atelier.reward.faction,'syndicat');assert.notDeepEqual(atelier.reward.rep,repos.reward.rep);assert.equal(step(atelier.ledger,'resolve','cadences',giver('cadences'),'repos').ok,false);assert.equal(s.quests.cadences.outcome,null);
});

test('Sans-Dossier waits for distinct relay commitments, preserves privacy, and pays an actual optional welcome',()=>{
 let s=opened('attente');const ids=quest('attente').witnessSites.slice(0,2);assert.equal(quest('attente').contactSite,'v042-marseille-caravan-02');s=step(s,'witness','attente',giver('attente',{siteId:ids[0]})).ledger;assert.equal(step(s,'witness','attente',giver('attente',{siteId:ids[0]})).ok,false);assert.equal(step(s,'resolve','attente',giver('attente'),'discrets').ok,false);s=step(s,'witness','attente',giver('attente',{siteId:ids[1]})).ledger;const privacy=step(s,'resolve','attente',giver('attente'),'discrets'),welcome=step(s,'resolve','attente',giver('attente'),'accueil');assert.deepEqual(privacy.cost,{});assert.deepEqual(welcome.cost,{food:2,water:2});assert.equal(welcome.reward.faction,'sansdossier');assert.match(privacy.reward.text,/sans noms/);assert.match(welcome.reward.text,/sans annoncer un trajet/);assert.equal(step(welcome.ledger,'resolve','attente',giver('attente'),'discrets').ok,false);assert.equal(step(s,'resolve','attente',giver('attente',{inventory:{food:2,water:1}}),'accueil').ok,false);
});

test('Migration extends a stored four-dossier campaign without changing any existing evidence, decision or journal',()=>{
 let old=step(witnesses(opened('cendres'),'cendres'),'resolve','cendres',giver('cendres'),'registre').ledger;for(const id of['cadences','attente'])delete old.quests[id];const before=clone(old),migrated=G.migrate(old,bindings);for(const id of['cendres','formulaire','signaux','lazaret'])assert.deepEqual(migrated.quests[id],before.quests[id]);assert.deepEqual(migrated.journal,before.journal);for(const id of['cadences','attente'])assert.deepEqual(migrated.quests[id],G.fresh().quests[id]);assert.deepEqual(old,before);assert.equal(G.progress(quest('cadences'),migrated.quests.cadences).ready,false);
});

test('The physical reader routes new Syndicat evidence without filling the Vigies dossier',()=>{
 const f=runtime();f.run('placeGiver("cadences");d.v053LoreAccept("cadences");placeGiver("signaux");d.v053LoreAccept("signaux")');for(const id of quest('cadences').observationSites){f.run('mode="PLAYING";observeSite('+JSON.stringify(id)+')');}assert.equal(f.run('state.v053Lore.quests.cadences.observations.length'),2);assert.equal(f.run('state.v053Lore.quests.signaux.observations.length'),0);f.run('mode="PIP";placeGiver("cadences")');const before=f.json('state');assert.equal(f.run('d.v053LoreResolve("cadences","atelier")'),true);const after=f.json('state');assert.equal(after.inventory.scrap,before.inventory.scrap-3);assert.equal(after.inventory.circuitry,before.inventory.circuitry-1);assert.equal(after.player.caps,before.player.caps+50);assert.equal(after.v046.lore.reputation.syndicat,3);assert.match(f.run('V027_STATIONS.canal13.text()'),/arrêt manuel/);f.run('state=migrateState(JSON.parse(test.saved));placeGiver("cadences")');assert.equal(f.run('d.v053LoreResolve("cadences","repos")'),false);
});

for(const throwing of[false,true])test('The new material allocation rolls back on '+(throwing?'throwing':'false')+' persistence failure',()=>{
 const f=runtime();f.run('placeGiver("cadences");d.v053LoreAccept("cadences")');for(const id of quest('cadences').observationSites)f.run('mode="PLAYING";observeSite('+JSON.stringify(id)+')');f.run('mode="PIP";placeGiver("cadences")');const before=f.json('state'),saved=f.run('test.saved');f.run(throwing?'test.throwSave=true':'test.fail=true');assert.equal(f.run('d.v053LoreResolve("cadences","atelier")'),false);assert.deepEqual(f.json('state'),before);assert.equal(f.run('test.saved'),saved);assert.doesNotMatch(f.run('V027_STATIONS.canal13.text()'),/arrêt manuel/);
});

test('Sans-Dossier payment, native journal and returned contact dialogue preserve a single shared reward',()=>{
 const f=runtime();f.run('placeGiver("attente");d.v053LoreAccept("attente")');for(const id of quest('attente').witnessSites.slice(0,2)){f.run('placeSite('+JSON.stringify(id)+')');assert.equal(f.run('d.v053LoreWitness("attente",'+JSON.stringify(id)+')'),true);}f.run('placeGiver("attente")');const before=f.json('state');assert.equal(f.run('d.v053LoreResolve("attente","accueil")'),true);const after=f.json('state');assert.equal(after.inventory.water,before.inventory.water-2);assert.equal(after.inventory.food,before.inventory.food-2);assert.equal(after.player.caps,before.player.caps+55);assert.equal(after.player.xp,before.player.xp+85);assert.equal(after.v046.lore.reputation.sansdossier,3);assert.match(f.run('V027_STATIONS.canal13.text()'),/deux lieux d’attente/);assert.equal(f.json('v027QuestRows()').find(q=>q.id==='l53:attente').stage,'done');f.run('v042TalkNPC(placeGiver("attente"))');assert.match(f.run('test.dialogue.text'),/sans annoncer un trajet/);f.run('state=migrateState(JSON.parse(test.saved));placeGiver("attente")');const replay=f.json('state');assert.equal(f.run('d.v053LoreResolve("attente","discrets")'),false);assert.deepEqual(f.json('state'),replay);
});

test('New dossiers do not inherit another campaign or allow a stale physical observation to write replacement state',()=>{
 const f=runtime();f.run('placeGiver("cadences");d.v053LoreAccept("cadences");test.readHook=()=>{state=migrateState(baseState());}');f.run('observeSite('+JSON.stringify(quest('cadences').observationSites[0])+')');assert.equal(f.run('state.v053Lore.quests.cadences.observations.length'),0);assert.equal(f.run('state.v053Lore.quests.cadences.accepted'),false);assert.equal(f.run('state.v053Lore.quests.attente.accepted'),false);assert.equal(f.run('state.v053Lore.journal.length'),0);
});


test('Syndicat explicit host never falls back to another relay when the proved existing host is absent',()=>{
 const out=G.bind(catalog.filter(s=>s.id!=='v042-laciotat-caravan-01')),q=out.find(q=>q.id==='cadences');assert.equal(q.contactSite,null);assert.equal(q.available,false);assert.equal(G.reduce(G.fresh(),out,{type:'accept',quest:'cadences'},giver('cadences')).ok,false);for(const id of['cendres','formulaire','signaux','lazaret','attente'])assert.deepEqual(out.find(q=>q.id===id),quest(id));
});

test('All four original complete definitions and actual bindings remain byte-identical to shipped 3d94e4c',()=>{
 const digest=require('node:crypto').createHash('sha256').update(JSON.stringify(bindings.slice(0,4))).digest('hex');assert.equal(digest,'733229adf7d470758e673d10e3cff1ed854c609375889d8d0cab51b25eb8a7f9');
});
