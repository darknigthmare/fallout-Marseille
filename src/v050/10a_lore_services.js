/* Fallout: Mistral v0.54 — Services publics et souverainetés.
   Extension additive du registre v0.53 : quatre dossiers jouables reliés à
   des relais v0.42 réels. Les conséquences restent finies et déclaratives :
   aucune ligne de train, flotte, clinique ou décontamination n'est simulée ici. */
const MistralServiceLore=(()=>{
 'use strict';
 const SCHEMA=1;
 const copy=value=>JSON.parse(JSON.stringify(value));
 const NETWORKS=[
  {id:'identite',name:'Identité',question:'Qui peut attester qu’une personne existe ?'},
  {id:'eau',name:'Eau',question:'Qui reçoit la ressource avant que la réserve soit vide ?'},
  {id:'sante',name:'Santé',question:'Le soin est-il un droit, une dette ou une cotisation ?'},
  {id:'transport',name:'Transport',question:'Une voie appartient-elle à ceux qui la gardent, l’entretiennent ou l’empruntent ?'},
  {id:'energie',name:'Énergie',question:'Qui accepte la dose, la panne et le risque nécessaires aux autres ?'},
  {id:'communication',name:'Communication',question:'Qui peut transformer un signal en vérité publique ?'},
  {id:'approvisionnement',name:'Approvisionnement',question:'Qui décide ce qui circule, attend ou reste au quai ?'}
 ];
 const SPECS=[
  {
   id:'carte_verte',name:'La carte verte',faction:'sociale',factionName:'La Sociale',network:'sante',
   contactId:'v042-marseille-caravan-01',contactLabel:'Halte caravanière · Vieux-Port',
   description:'Une régulatrice de La Sociale demande comment accueillir des Sans-Dossier sans transformer le soin en dette héréditaire. Le relais ne peut constituer qu’une réserve limitée.',
   pending:'Rejoindre le relais du Vieux-Port avec les fournitures d’une décision. Aucune clinique permanente ni réserve renouvelable ne sera créée par ce dossier.',
   choices:[
    {id:'urgence_universelle',label:'Garantir une trousse d’urgence sans condition · 2 eaux + 1 antibiotique + 2 tissus',cost:{water:2,antibiotics:1,cloth:2},caps:45,xp:105,loreRep:3,rep:{secours:3,ligue:1},text:'Le relais reçoit une trousse d’urgence finie, accessible avant toute vérification d’identité. Le reçu interdit d’en faire une dette familiale ; il ne promet ni hôpital ouvert ni stock renouvelable.'},
    {id:'cotisation_locale',label:'Confier la réserve à une caisse locale contrôlée · 2 vivres + 1 antibiotique + 1 circuit',cost:{food:2,antibiotics:1,circuitry:1},caps:55,xp:105,loreRep:2,rep:{secours:2,ligue:2},text:'Une caisse locale reçoit les fournitures et publie ses entrées et sorties. La Sociale conserve un droit d’audit, pas un droit sur les descendants. Aucun soin illimité n’est annoncé.'}
   ]
  },
  {
   id:'terminus_humain',name:'Tout le monde descend',faction:'aiguilleurs',factionName:'Les Aiguilleurs du Réseau',network:'transport',
   contactId:'v042-marseille-caravan-02',contactLabel:'Relais marchand · Saint-Charles',
   description:'À Saint-Charles, l’Horloge continue de classer des absents comme voyageurs en retard. Les Aiguilleurs demandent un protocole humain avant toute reprise future du trafic.',
   pending:'Rejoindre le relais de Saint-Charles avec les fournitures d’une décision. Le dossier règle un protocole d’accueil, pas le déplacement physique d’un train.',
   choices:[
    {id:'quai_humain',label:'Équiper un quai d’accueil hors contrôle automatique · 2 eaux + 2 vivres + 1 tissu',cost:{water:2,food:2,cloth:1},caps:45,xp:110,loreRep:3,rep:{ligue:2,secours:2},text:'Le relais réserve un espace d’accueil aux voyageurs que l’Horloge ne reconnaît pas. Les quantités livrées sont consignées ; aucun train n’est annoncé comme réparé ou mis en circulation.'},
    {id:'horaire_manuel',label:'Créer un registre manuel contradictoire · 3 ferrailles + 1 circuit + 1 tissu',cost:{scrap:3,circuitry:1,cloth:1},caps:55,xp:110,loreRep:3,rep:{ligue:1,veilleurs:3},text:'Les équipes assemblent un registre manuel et un arrêt de sécurité local. L’Horloge ne peut plus être la seule preuve d’un passage, mais aucune signalisation animée ni ligne active n’est créée.'}
   ]
  },
  {
   id:'dose_collective',name:'La dose collective',faction:'commissariat',factionName:'Commissariat des Atomes',network:'energie',
   contactId:'v042-huveaune-caravan-01',contactLabel:'Halte caravanière · Vallée de l’Huveaune',
   description:'Une liaison du Commissariat demande aux relais de choisir entre partager les mesures de radiation ou protéger d’abord les civils exposés. Les deux options limitent le monopole des experts.',
   pending:'Rejoindre la halte de la vallée avec les fournitures d’une décision. Cette liaison ne purge pas une zone et ne remet aucun réacteur en service.',
   choices:[
    {id:'dosimetres_partages',label:'Rendre les mesures vérifiables par les habitants · 2 circuits + 2 ferrailles',cost:{circuitry:2,scrap:2},caps:60,xp:120,loreRep:3,rep:{veilleurs:3,ligue:1},text:'Les composants servent à des instruments de comparaison confiés au relais. Les habitants peuvent contester une mesure officielle ; aucune décontamination régionale ni production énergétique n’est annoncée.'},
    {id:'cordon_civil',label:'Constituer une réserve pour les personnes exposées · 2 tissus + 2 eaux + 1 antibiotique',cost:{cloth:2,water:2,antibiotics:1},caps:45,xp:120,loreRep:3,rep:{secours:3,veilleurs:1},text:'Le relais reçoit une réserve finie pour les personnes exposées et consigne les seuils de retrait. Le Commissariat garde ses relevés, mais ne peut transformer la halte en zone d’essai sans témoin.'}
   ]
  },
  {
   id:'pavillon_secours',name:'Le pavillon de secours',faction:'amiraute',factionName:'Amirauté du Levant',network:'approvisionnement',
   contactId:'v042-laciotat-caravan-01',contactLabel:'Halte caravanière · La Ciotat',
   description:'Une délégation du Levant veut enregistrer les secours maritimes. Les gens de La Ciotat acceptent un protocole seulement s’il protège les naufragés avant les droits de saisie.',
   pending:'Rejoindre la halte de La Ciotat avec les fournitures d’une décision. Le dossier n’ajoute ni navire, ni flotte, ni corridor maritime visible.',
   choices:[
    {id:'corridor_civil',label:'Approvisionner un accueil sans immatriculation préalable · 3 eaux + 3 vivres',cost:{water:3,food:3},caps:50,xp:115,loreRep:3,rep:{francs:3,ciotat:1},text:'La halte conserve une réserve finie pour les naufragés avant toute vérification de pavillon. L’Amirauté reçoit une copie du protocole, sans droit de saisie automatique et sans convoi simulé.'},
    {id:'convoi_enregistre',label:'Partager un manifeste contradictoire avec les équipages · 3 ferrailles + 1 circuit + 2 tissus',cost:{scrap:3,circuitry:1,cloth:2},caps:60,xp:115,loreRep:2,rep:{francs:2,ciotat:2},text:'Un manifeste local est conservé par la halte et les équipages, pas seulement par l’Amirauté. Il décrit les personnes attendues et les secours dus ; aucun bâtiment n’est physiquement déployé.'}
   ]
  }
 ];
 const IDS=SPECS.map(spec=>spec.id);
 const FACTIONS=SPECS.map(spec=>spec.faction);
 const own=(value,key)=>Object.prototype.hasOwnProperty.call(value||{},key);
 function bind(catalog=[]){
  const byId=new Map((Array.isArray(catalog)?catalog:[]).map(site=>[site.id,site]));
  return SPECS.map(spec=>{
   const site=byId.get(spec.contactId);
   return {...copy(spec),contactSite:spec.contactId,contactName:site?.name||spec.contactLabel,available:!!site&&site.safe===true};
  });
 }
 function fresh(){
  return{schema:SCHEMA,quests:Object.fromEntries(IDS.map(id=>[id,{accepted:false,outcome:null}])),journal:[]};
 }
 function migrate(raw,bindings=bind([])){
  const next=fresh(),input=raw&&typeof raw==='object'?raw:{};
  for(const quest of bindings){
   const source=input.quests?.[quest.id];
   if(!source||typeof source!=='object')continue;
   const valid=quest.choices.some(choice=>choice.id===source.outcome);
   next.quests[quest.id]={accepted:source.accepted===true||valid,outcome:valid?source.outcome:null};
  }
  if(Array.isArray(input.journal))next.journal=input.journal.filter(entry=>entry&&typeof entry==='object'&&IDS.includes(entry.quest)&&['accepted','resolved'].includes(entry.type)).slice(-64).map(copy);
  return next;
 }
 function enough(inventory={},cost={}){
  return Object.entries(cost).every(([id,count])=>Number.isFinite(inventory?.[id])&&inventory[id]>=count);
 }
 function progress(quest,state){
  if(!quest?.available)return{ready:false,text:'Relais indisponible dans le catalogue actuel.'};
  if(state?.outcome){const choice=quest.choices.find(item=>item.id===state.outcome);return{ready:false,text:choice?.text||'Décision déjà conservée.'};}
  if(!state?.accepted)return{ready:false,text:'Le dossier doit être ouvert auprès du relais.'};
  return{ready:true,text:'Le dossier est ouvert. Rapportez les fournitures d’une seule décision au relais.'};
 }
 function reduce(raw,bindings,action={},context={}){
  const ledger=migrate(raw,bindings),quest=bindings.find(item=>item.id===action.quest),failure=reason=>({ok:false,reason,ledger,cost:{}});
  if(!quest)return failure('Dossier inconnu.');
  const state=ledger.quests[quest.id];
  if(context.blocked)return failure(context.blocked);
  if(!quest.available)return failure('Le relais lié à ce dossier est indisponible.');
  if(action.type==='accept'){
   if(!context.atGiver)return failure('Parlez au contact du relais pour ouvrir ce dossier.');
   if(state.outcome)return failure('Ce dossier a déjà une conclusion.');
   if(state.accepted)return failure('Ce dossier est déjà ouvert.');
   state.accepted=true;ledger.journal.push({type:'accepted',quest:quest.id,at:Number(context.playTime)||0});
   return{ok:true,ledger,cost:{},notice:'Dossier ouvert : '+quest.name+'.'};
  }
  if(action.type==='resolve'){
   const choice=quest.choices.find(item=>item.id===action.choice);
   if(!choice)return failure('Décision inconnue.');
   if(!context.atGiver)return failure('Revenez au contact du relais pour conclure.');
   if(!state.accepted)return failure('Ouvrez d’abord le dossier auprès du relais.');
   if(state.outcome)return failure('Une décision exclusive a déjà été sauvegardée.');
   if(!enough(context.inventory,choice.cost))return failure('Fournitures insuffisantes pour cette décision.');
   state.outcome=choice.id;ledger.journal.push({type:'resolved',quest:quest.id,choice:choice.id,at:Number(context.playTime)||0});
   return{ok:true,ledger,cost:copy(choice.cost),reward:{quest:quest.id,faction:quest.faction,caps:choice.caps,xp:choice.xp,loreRep:choice.loreRep,rep:copy(choice.rep),text:choice.text},notice:choice.text};
  }
  return failure('Action de dossier inconnue.');
 }
 function bulletin(faction,raw,bindings){
  const ledger=migrate(raw,bindings),quests=bindings.filter(item=>item.faction===faction);
  if(!quests.length)return'Aucun bulletin disponible.';
  const quest=quests[0],state=ledger.quests[quest.id],choice=quest.choices.find(item=>item.id===state.outcome);
  if(choice)return quest.factionName+' : '+choice.text;
  if(state.accepted)return quest.factionName+' : '+progress(quest,state).text;
  return quest.factionName+' : '+quest.description;
 }
 return{SCHEMA,NETWORKS:copy(NETWORKS),IDS:IDS.slice(),FACTIONS:FACTIONS.slice(),catalog:()=>copy(SPECS),bind,fresh,migrate,enough,progress,reduce,bulletin};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralServiceLore;

if(typeof baseState==='function'&&typeof V042_CATALOG!=='undefined'){
 const bindings=MistralServiceLore.bind(V042_CATALOG),clone=value=>JSON.parse(JSON.stringify(value));
 const oldBase=baseState;baseState=function(){const stateValue=oldBase();stateValue.v054Services=MistralServiceLore.fresh();return stateValue;};
 const oldMigrate=migrateState;migrateState=function(input={}){const stateValue=oldMigrate(input);stateValue.v054Services=MistralServiceLore.migrate(input.v054Services,bindings);return stateValue;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 if(typeof V027_SUBS!=='undefined'&&V027_SUBS.data)V027_SUBS.data.services='SERVICES ET SOUVERAINETÉS';
 function blocked(){
  if(!gameStarted||!['PLAYING','PIP','DIALOGUE'].includes(mode)||!(state.player.hp>0))return'Reprenez une partie active avant cette opération.';
  if(typeof V046!=='undefined'&&V046.lab)return'Le banc synthétique ne modifie pas les décisions de la campagne.';
  if(!world?.v046||!world.geoMacro||state.v042?.activeInterior)return'Rejoignez les relais du territoire extérieur.';
  if((typeof V046!=='undefined'&&V046.busy)||(typeof V047!=='undefined'&&V047.pending)||zoneTransitioning)return'Attendez la fin du chargement du secteur.';
  if(typeof onGround==='boolean'&&!onGround)return'Rejoignez un sol stable avant cet échange.';
  if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,state.player.pos))return'Éloignez-vous du combat avant cet échange.';
  return null;
 }
 function siteContact(siteId){
  const site=v042Site(siteId),player=state.player.pos;if(!site||!v042SiteDiscovered(site)||!world?.v046)return null;
  const runtime=typeof V042_RUNTIME!=='undefined'?V042_RUNTIME:null;
  const candidates=(world.npcs||[]).filter(npc=>npc.alive!==false&&(npc.v042Site===siteId||runtime?.npcData?.get?.(npc.id)?.siteId===siteId)&&Math.hypot(npc.pos[0]-player[0],npc.pos[2]-player[2])<=8&&Math.abs((npc.pos[1]||0)+1.4-player[1])<2.8&&lineOfSight(player,[npc.pos[0],(npc.pos[1]||0)+1.4,npc.pos[2]]));
  return candidates.sort((a,b)=>dist2(a.pos,player)-dist2(b.pos,player)||String(a.id).localeCompare(String(b.id)))[0]||null;
 }
 function notify(message){if(typeof V027!=='undefined')V027.message=message;if(typeof toast==='function')toast(message,'bad');return false;}
 function restore(owner,snapshot){if(state!==owner)return;for(const key of Object.keys(owner))if(!Object.prototype.hasOwnProperty.call(snapshot,key))delete owner[key];Object.assign(owner,snapshot);}
 function transact(plan){
  if(!plan.ok)return notify(plan.reason);const owner=state,snapshot=clone(owner);
  try{
   for(const[id,count]of Object.entries(plan.cost||{})){if(!(owner.inventory[id]>=count))throw Error('Fournitures devenues insuffisantes.');owner.inventory[id]-=count;}
   owner.v054Services=plan.ledger;
   if(plan.reward){const reward=plan.reward;owner.player.caps+=reward.caps;owner.v046??={};owner.v046.lore??={};owner.v046.lore.reputation??={};owner.v046.lore.reputation[reward.faction]=Math.max(-100,Math.min(100,(owner.v046.lore.reputation[reward.faction]||0)+reward.loreRep));owner.rep??={};for(const[id,count]of Object.entries(reward.rep||{}))owner.rep[id]=Math.max(-100,Math.min(100,(owner.rep[id]||0)+count));if(typeof gainXP==='function')gainXP(reward.xp,bindings.find(item=>item.id===reward.quest)?.name||'Dossier des services');}
   if(state!==owner||saveGame(false)===false)throw Error('La décision ne peut pas être sauvegardée.');
  }catch(error){restore(owner,snapshot);return notify((error?.message||'Écriture refusée.')+' Opération annulée sans paiement ni récompense conservés.');}
  if(typeof V027!=='undefined')V027.message=plan.notice||plan.reward?.text||'Décision conservée.';if(typeof updateQuestUI==='function')updateQuestUI(true);if(mode==='PIP'&&typeof renderPipboy==='function')renderPipboy();return true;
 }
 function act(type,id,choice){
  const quest=bindings.find(item=>item.id===id);if(!quest)return false;
  const plan=MistralServiceLore.reduce(state.v054Services,bindings,{type,quest:id,choice},{blocked:blocked(),atGiver:!!siteContact(quest.contactSite),inventory:state.inventory,playTime:state.playTime});
  return transact(plan);
 }
 function track(id){
  const quest=bindings.find(item=>item.id===id);if(!quest||!quest.available||blocked())return false;
  const owner=state,snapshot=clone(owner);owner.v042.tracked=quest.contactSite;
  try{if(state!==owner||saveGame(false)===false)throw Error();}catch{restore(owner,snapshot);return notify('Le suivi du relais ne peut pas être sauvegardé.');}
  if(typeof updateQuestUI==='function')updateQuestUI(true);if(mode==='PIP'&&typeof renderPipboy==='function')renderPipboy();return true;
 }
 function panel(container){
  const esc=v027Escape,deny=blocked();
  const networks=MistralServiceLore.NETWORKS.map(network=>'<li><strong>'+esc(network.name)+'</strong> — '+esc(network.question)+'</li>').join('');
  const dossiers=bindings.map(quest=>{
   const questState=state.v054Services.quests[quest.id],status=MistralServiceLore.progress(quest,questState),contact=v042Site(quest.contactSite),present=!!siteContact(quest.contactSite),choice=quest.choices.find(item=>item.id===questState.outcome);
   let actions='';
   if(!quest.available)actions='<p>Le relais requis est absent ou non sûr dans le catalogue chargé.</p>';
   else if(!questState.accepted)actions=v027Button('Suivre le relais','l54:track',quest.id,!!deny)+v027Button('Ouvrir le dossier au relais','l54:accept',quest.id,!!deny||!present);
   else if(!questState.outcome)actions=v027Button('Suivre le relais','l54:track',quest.id,!!deny)+quest.choices.map(item=>'<p>'+esc(item.label)+' · '+item.caps+' capsules, '+item.xp+' XP.</p>'+v027Button('Conclure : '+item.label,'l54:resolve',quest.id+'|'+item.id,!!deny||!present||!MistralServiceLore.enough(state.inventory,item.cost))).join('');
   else actions='<p>Décision exclusive sauvegardée. Ce dossier ne se renouvelle pas.</p>';
   return'<section class="v046-notice"><h3>'+esc(quest.name)+'</h3><p>'+esc(quest.factionName)+' · '+esc(contact?.name||quest.contactName)+'</p><p>'+esc(quest.description)+'</p><p>'+esc(choice?.text||status.text)+'</p>'+actions+'</section>';
  }).join('');
  const bulletins=bindings.map(quest=>'<p>'+esc(MistralServiceLore.bulletin(quest.faction,state.v054Services,bindings))+'</p>').join('');
  container.innerHTML='<div class="p27-long"><p class="p27-kicker">RÉPUBLIQUE DES SERVICES</p><h2>Services et souverainetés</h2><p>Quatre puissances disputent la santé, le rail, la mesure atomique et le secours maritime. Les décisions ci-dessous coûtent des fournitures réelles, sont sauvegardées et restent uniques.</p>'+(deny?'<p>'+esc(deny)+'</p>':'')+'<h3>Les sept réseaux</h3><ul>'+networks+'</ul>'+dossiers+'<h3>Bulletins conservés</h3>'+bulletins+'</div>';
 }
 const oldData=v027Data;v027Data=function(container){
  if(V027.sub==='services')return panel(container);
  const result=oldData(...arguments);
  if(['france','continuity'].includes(V027.sub))container.insertAdjacentHTML('beforeend','<section class="v046-notice"><h2>La République des services</h2><p>La Sociale, les Aiguilleurs, le Commissariat des Atomes et l’Amirauté du Levant proposent désormais quatre dossiers aux relais existants.</p>'+v027Button('Consulter les services et souverainetés','jump','data:services')+'</section>');
  return result;
 };
 const oldDispatch=v027Dispatch;v027Dispatch=function(action,arg=''){
  if(typeof action!=='string'||!action.startsWith('l54:'))return oldDispatch(...arguments);
  if(!v027CanAct())return false;const[id,choice]=String(arg).split('|');
  if(action==='l54:track')return track(id);
  if(action==='l54:accept')return act('accept',id);
  if(action==='l54:resolve')return act('resolve',id,choice);
  return false;
 };
 const previousAfter=globalThis.v053LoreAfterInit;
 globalThis.v053LoreAfterInit=function(){
  if(typeof previousAfter==='function')previousAfter();
  globalThis.__MISTRAL_DEBUG??={};
  globalThis.__MISTRAL_DEBUG.serviceLore=()=>({schema:MistralServiceLore.SCHEMA,networks:clone(MistralServiceLore.NETWORKS),quests:bindings.map(quest=>({id:quest.id,name:quest.name,faction:quest.faction,network:quest.network,contactSite:quest.contactSite,available:quest.available,state:clone(state.v054Services.quests[quest.id])})),journal:clone(state.v054Services.journal)});
 };
}
