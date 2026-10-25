/* Continuity of the French factions already preserved in v0.46. These four
   new dossiers extend that canon; they are not recovered v0.44 conversations. */
const MistralLoreContinuity=(()=>{
 const copy=v=>JSON.parse(JSON.stringify(v)),own=(v,k)=>Object.prototype.hasOwnProperty.call(v||{},k);
 const SPECS=[
  {id:'cendres',name:'Le droit d’être compté',faction:'convention',factionName:'Convention des Cendres',macro:'geo_marseille',kind:'testimony',required:2,contactIndex:0,
   description:'Deux relais doivent attester l’existence de familles que les registres des Baumettes refusent. La Convention ne s’accorde pas sur ce qu’il faut garder de leurs noms.',
   pending:'Recueillir deux témoignages auprès de relais marseillais distincts, puis revenir au contact.',
   choices:[
    {id:'anonymes',label:'Garantir une identité protégée sans publier les noms',cost:{},caps:45,xp:80,loreRep:3,rep:{ligue:2},text:'Les attestations restent sous la garde des familles. L’assemblée reconnaît leur droit d’exister sans afficher leurs noms.'},
    {id:'registre',label:'Confier une copie contradictoire aux assemblées',cost:{},caps:55,xp:80,loreRep:2,rep:{ligue:1,continuite:1},text:'Une copie du registre est déposée dans les relais. Les familles gardent un droit de réponse et peuvent contester chaque ligne.'}
   ]},
  {id:'formulaire',name:'Le formulaire impossible',faction:'concorde',factionName:'Direction de la Continuité — CONCORDE',macro:'geo_marseille',kind:'audit',required:2,contactIndex:1,
   description:'Une copie CERFA-77 déclare la même réserve vide et déjà saisie. Le contact accepte un diagnostic matériel ou deux déclarations contradictoires.',
   pending:'Analyser la copie au relais avec Intelligence 5 et un circuit, ou réunir les témoignages de deux relais distincts.',
   choices:[
    {id:'rectifier',label:'Faire rectifier le dossier et rendre le reçu aux habitants',cost:{},caps:50,xp:90,loreRep:3,rep:{continuite:2,ligue:1},text:'Le refus CERFA-77 est remplacé par un reçu contradictoire. La réserve n’est plus déclarée saisie et les habitants gardent leur exemplaire.'},
    {id:'publier',label:'Publier les contradictions avant toute nouvelle saisie',cost:{},caps:40,xp:90,loreRep:1,rep:{continuite:-1,ligue:3},text:'Les deux versions du formulaire circulent dans les relais. CONCORDE perd le monopole de l’explication et les saisies contestées sont dénoncées.'}
   ]},
  {id:'signaux',name:'Les signaux des crêtes',faction:'vigies',factionName:'Vigies des Crêtes',macro:'geo_garlaban',kind:'observation',required:3,contactIndex:0,
   description:'Trois balises des crêtes donnent des avis contradictoires sur les fumées. Les Vigies demandent de lire chaque repère sur place avant de choisir le bulletin.',
   pending:'Examiner les trois repères indiqués sur les crêtes, puis rapporter les observations au relais.',
   choices:[
    {id:'alerte',label:'Diffuser une alerte publique avec les limites des observations',cost:{},caps:45,xp:100,loreRep:3,rep:{secours:3},text:'Les fumées observées et les secteurs non vérifiés sont nommés séparément. Canal 13 transmet une alerte prudente, sans inventer une attaque.'},
    {id:'relais',label:'Transmettre d’abord aux relais chargés de prévenir les habitants',cost:{},caps:55,xp:100,loreRep:2,rep:{secours:2,veilleurs:1},text:'Les relais reçoivent les observations avant l’annonce générale. Chaque équipe est chargée de prévenir son secteur et de conserver les incertitudes.'}
   ]},
  {id:'lazaret',name:'L’autre rive',faction:'insulaires',factionName:'Insulaires du Lazaret',macro:'geo_frioul',kind:'delivery',required:0,contactIndex:0,
   description:'Au Lazaret, la même embarcation doit porter une réserve de soin ou des vivres pour un passage accompagné. Les Insulaires demandent une décision et des fournitures réelles.',
   pending:'Rapporter au contact deux eaux et un antibiotique pour le soin, ou deux eaux et deux vivres pour le passage accompagné.',
   choices:[
    {id:'soins',label:'Constituer la réserve de soin · 2 eaux + 1 antibiotique',cost:{water:2,antibiotics:1},caps:35,xp:80,loreRep:3,rep:{francs:2,secours:1},text:'La réserve de soin est remise au Lazaret. Les personnes accueillies disposent d’eau et d’antibiotiques avant une nouvelle traversée.'},
    {id:'passage',label:'Approvisionner le passage accompagné · 2 eaux + 2 vivres',cost:{water:2,food:2},caps:35,xp:80,loreRep:2,rep:{francs:2,ligue:1},text:'Le passage accompagné reçoit ses vivres et son eau. Le choix est inscrit au registre du Lazaret ; aucune réserve renouvelable n’a été créée.'}
   ]}
 ];
 const IDS=SPECS.map(q=>q.id),FACTIONS=['convention','gilets','syndicat','concorde','communes','sansdossier','cochonnet','vigies','insulaires'];
 const safe=s=>s&&s.safe===true&&['settlement','outpost','caravan'].includes(s.kind)&&s.npcSlots>0;
 function bind(catalog){
  if(!Array.isArray(catalog)||catalog.length>4096)throw Error('Catalogue de relais incompatible');
  return SPECS.map(spec=>{const contacts=catalog.filter(s=>s.macro===spec.macro&&safe(s)).sort((a,b)=>a.id.localeCompare(b.id)),landmarks=catalog.filter(s=>s.macro===spec.macro&&s.kind==='landmark').sort((a,b)=>a.id.localeCompare(b.id)),contact=contacts[spec.contactIndex%Math.max(1,contacts.length)];return{...copy(spec),contactSite:contact?.id||null,witnessSites:contacts.map(s=>s.id),observationSites:landmarks.slice(0,spec.required).map(s=>s.id),available:!!contact&&(spec.kind!=='observation'||landmarks.length>=spec.required)};});
 }
 function fresh(){return{schema:1,quests:Object.fromEntries(IDS.map(id=>[id,{accepted:false,witnesses:[],observations:[],audit:false,outcome:null}])),journal:[]};}
 function migrate(raw,bindings){
  const out=fresh(),old=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{},proofs=(values,allowed,max)=>Array.isArray(values)?[...new Set(values.filter(x=>typeof x==='string'&&allowed.includes(x)))].slice(0,max):[];
  for(const q of bindings){const s=old.quests?.[q.id];if(!s||typeof s!=='object'||Array.isArray(s))continue;const r=out.quests[q.id],choice=q.choices.find(c=>c.id===s.outcome);r.accepted=s.accepted===true||!!choice;if(r.accepted){r.witnesses=proofs(s.witnesses,q.witnessSites,q.required);r.observations=proofs(s.observations,q.observationSites,q.required);r.audit=q.kind==='audit'&&s.audit===true;r.outcome=choice?.id||null;}}
  if(Array.isArray(old.journal))for(const row of old.journal.slice(-16)){const q=bindings.find(q=>q.id===row?.quest);if(q&&out.quests[q.id].outcome===row.choice&&!out.journal.some(r=>r.quest===q.id))out.journal.push({quest:q.id,choice:row.choice,playTime:typeof row.playTime==='number'&&Number.isFinite(row.playTime)?Math.max(0,Math.min(1e9,row.playTime)):0});}
  return out;
 }
 function progress(q,s){if(!s?.accepted)return{ready:false,text:'Rencontrer le contact pour ouvrir le dossier.'};if(s.outcome)return{ready:false,text:q.choices.find(c=>c.id===s.outcome)?.text||'Décision conservée.'};if(q.kind==='delivery')return{ready:true,text:q.pending};if(q.kind==='audit'&&s.audit)return{ready:true,text:'La copie du registre a été analysée.'};const count=q.kind==='observation'?s.observations.length:s.witnesses.length;return{ready:count>=q.required,text:(q.kind==='observation'?'Repères examinés : ':'Témoignages distincts : ')+count+' / '+q.required+'.'};}
 function enough(inventory,cost){return Object.entries(cost).every(([id,n])=>typeof inventory?.[id]==='number'&&Number.isFinite(inventory[id])&&inventory[id]>=n);}
 function reduce(raw,bindings,action,context={}){
  const q=bindings.find(q=>q.id===action?.quest),ledger=migrate(raw,bindings),none=reason=>({ok:false,reason});if(!q?.available)return none('Ce dossier ne possède pas de relais compatible.');if(context.blocked)return none(context.blocked);
  const s=ledger.quests[q.id];if(s.outcome)return none('Une décision et une seule récompense sont déjà conservées.');
  let cost={},reward=null;
  if(action.type==='accept'){if(!context.atGiver)return none('Rencontrez le contact du dossier.');if(s.accepted)return none('Ce dossier est déjà ouvert.');s.accepted=true;}
  else{if(!s.accepted)return none('Ouvrez ce dossier auprès de son contact.');
   if(action.type==='witness'){if(!['testimony','audit'].includes(q.kind)||!context.contact||!q.witnessSites.includes(context.siteId))return none('Le témoignage demande un habitant présent dans un relais du secteur.');if(s.witnesses.includes(context.siteId))return none('Le témoignage de ce relais est déjà conservé.');if(s.witnesses.length>=q.required)return none('Les témoignages nécessaires sont déjà réunis.');s.witnesses.push(context.siteId);}
   else if(action.type==='audit'){if(q.kind!=='audit'||!context.atGiver)return none('L’analyse doit être menée auprès du contact.');if(s.audit)return none('Cette copie a déjà été analysée.');if(!(context.intelligence>=5))return none('Intelligence 5 requise pour analyser la copie.');cost={circuitry:1};if(!enough(context.inventory,cost))return none('Un circuit est nécessaire ; aucun paiement partiel.');s.audit=true;}
   else if(action.type==='observe'){if(q.kind!=='observation'||!context.physicalObservation||!q.observationSites.includes(context.siteId))return none('Examinez le vrai repère à portée et avec une ligne de vue libre.');if(s.observations.includes(context.siteId))return none('Ce repère est déjà consigné.');s.observations.push(context.siteId);}
   else if(action.type==='resolve'){if(!context.atGiver)return none('Retournez voir le contact pour prendre la décision.');const choice=q.choices.find(c=>c.id===action.choice);if(!choice)return none('Décision inconnue.');if(!progress(q,s).ready)return none('Les preuves du dossier sont encore incomplètes.');cost=choice.cost;if(!enough(context.inventory,cost))return none('Il manque des fournitures ; aucun paiement partiel.');s.outcome=choice.id;reward={caps:choice.caps,xp:choice.xp,faction:q.faction,loreRep:choice.loreRep,rep:copy(choice.rep),text:choice.text};ledger.journal.push({quest:q.id,choice:choice.id,playTime:Math.max(0,Math.min(1e9,Number(context.playTime)||0))});ledger.journal=ledger.journal.slice(-16);}
   else return none('Action de dossier inconnue.');
  }
  return{ok:true,ledger,cost:copy(cost),reward,quest:q.id};
 }
 function nextSite(q,s){if(!s?.accepted||s.outcome)return q.contactSite;if(q.kind==='observation')return q.observationSites.find(id=>!s.observations.includes(id))||q.contactSite;if(['testimony','audit'].includes(q.kind)&&!progress(q,s).ready)return q.witnessSites.find(id=>!s.witnesses.includes(id))||q.contactSite;return q.contactSite;}
 function bulletin(channel,ledger,bindings,legacy={}){
  const completed=id=>{const q=bindings.find(q=>q.id===id),s=ledger.quests[id];return s?.outcome?q?.choices.find(c=>c.id===s.outcome)?.text:null;};
  if(channel==='centtreves'){const p=legacy.petanque||{};return`COCHONNET-3 tient le registre : ${Math.max(0,Number(p.played)||0)} mènes, ${Math.max(0,Number(p.wins)||0)} victoires. `+(legacy.done?.encore||legacy.done?.pointe?'Les abords homologués restent sous la trêve. Une victoire ne décide pas qui a le droit de manger.':'La trêve tient jusqu’à la fin de la mène. Les dossiers « On joue encore » et « Tu tires ou tu pointes ? » restent à conclure.');}
  if(channel==='lazaret')return completed('lazaret')||'Lazaret à l’écoute. Une place à bord n’est pas une promesse d’accueil. Le contact des Insulaires attend de l’eau et une décision pour la réserve de soin ou le passage accompagné.';
  const lines=['Canal 13 — les Ronds-Points Libres transmettent les faits, pas les listes de suspects.'];for(const id of['cendres','formulaire','signaux'])if(completed(id))lines.push(completed(id));if(lines.length===1)lines.push('Des habitants demandent des attestations, une copie CERFA-77 se contredit et les Vigies attendent les observations des crêtes.');return lines.join(' ');
 }
 return{catalog:()=>copy(SPECS),IDS:IDS.slice(),FACTIONS:FACTIONS.slice(),bind,fresh,migrate,progress,enough,reduce,nextSite,bulletin};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralLoreContinuity;

if(typeof baseState==='function'&&typeof V042_CATALOG!=='undefined'){
 const bindings=MistralLoreContinuity.bind(V042_CATALOG),copy=v=>JSON.parse(JSON.stringify(v));
 const oldBase=baseState;baseState=function(){const s=oldBase();s.v053Lore=MistralLoreContinuity.fresh();return s;};
 if(typeof V027_SUBS!=='undefined')V027_SUBS.data.continuity='RELAIS ET DOSSIERS';
 const oldMigrate=migrateState;migrateState=function(input={}){const s=oldMigrate(input);s.v053Lore=MistralLoreContinuity.migrate(input.v053Lore,bindings);return s;};state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 function blocked(){
  if(!gameStarted||!['PLAYING','PIP','DIALOGUE'].includes(mode)||!(state.player.hp>0))return'Reprenez une partie active avant cette opération.';
  if(V046.lab)return'Le banc synthétique ne modifie pas les dossiers de votre campagne.';
  if(!world?.v046||!world.geoMacro||state.v042?.activeInterior)return'Rejoignez les relais du territoire extérieur.';
  if(V046.busy||V047.pending||zoneTransitioning)return'Attendez la fin du chargement du secteur.';
  if(typeof onGround==='boolean'&&!onGround)return'Rejoignez un sol stable avant cet échange.';
  if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,state.player.pos))return'Éloignez-vous du combat avant cet échange.';
  return null;
 }
 function contact(siteId){
  const site=v042Site(siteId),p=state.player.pos;if(!site||!v042SiteDiscovered(site)||!world?.v046)return null;
  const candidates=(world.npcs||[]).filter(n=>n.alive!==false&&(n.v042Site===siteId||V042_RUNTIME.npcData.get(n.id)?.siteId===siteId)&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs((n.pos[1]||0)+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],(n.pos[1]||0)+1.4,n.pos[2]]));
  return candidates.sort((a,b)=>dist2(a.pos,p)-dist2(b.pos,p)||String(a.id).localeCompare(String(b.id)))[0]||null;
 }
 function notify(message){if(typeof V027!=='undefined')V027.message=message;if(typeof toast==='function')toast(message,'bad');return false;}
 function transact(plan,message){
  if(!plan.ok)return notify(plan.reason);const owner=state,keys=['v053Lore','v046','inventory','player','rep','achievements','lastSave','version','equipment','ammo','flags'],snapshot=Object.fromEntries(keys.map(k=>[k,owner[k]===undefined?undefined:copy(owner[k])]));
  try{for(const[id,n]of Object.entries(plan.cost)){if(!(owner.inventory[id]>=n))throw Error('Fournitures devenues insuffisantes.');owner.inventory[id]-=n;}owner.v053Lore=plan.ledger;
   if(plan.reward){const r=plan.reward;owner.player.caps+=r.caps;owner.v046.lore.reputation??={};owner.v046.lore.reputation[r.faction]=Math.max(-100,Math.min(100,(owner.v046.lore.reputation[r.faction]||0)+r.loreRep));for(const[id,n]of Object.entries(r.rep))owner.rep[id]=Math.max(-100,Math.min(100,(owner.rep[id]||0)+n));gainXP(r.xp,bindings.find(q=>q.id===plan.quest).name);}
   if(state!==owner||saveGame(false)===false)throw Error('La décision ne peut pas être sauvegardée.');
  }catch(error){if(state===owner)for(const key of keys){if(snapshot[key]===undefined)delete owner[key];else owner[key]=snapshot[key];}return notify((error?.message||'Écriture refusée.')+' Opération annulée sans paiement ni récompense conservés.');}
  if(typeof V027!=='undefined')V027.message=message;if(mode==='PIP')renderPipboy();return true;
 }
 function act(type,id,choice,siteId){
  const q=bindings.find(q=>q.id===id);if(!q)return false;const atGiver=!!contact(q.contactSite),context={blocked:blocked(),atGiver,contact:!!contact(siteId),siteId,inventory:state.inventory,intelligence:Number(state.character.special.I||state.character.special.intelligence)||0,playTime:state.playTime};
  const plan=MistralLoreContinuity.reduce(state.v053Lore,bindings,{type,quest:id,choice},context);return transact(plan,plan.reward?.text||(type==='accept'?'Dossier ouvert auprès du contact.':type==='audit'?'La copie CERFA-77 et le circuit utilisé sont consignés.':'Le témoignage de ce relais est conservé.'));
 }
 function track(id){const q=bindings.find(q=>q.id===id);if(!q||!state.v053Lore.quests[id].accepted||blocked())return false;const site=MistralLoreContinuity.nextSite(q,state.v053Lore.quests[id]);if(!v042Site(site))return false;const previous=state.v042.tracked,lastSave=state.lastSave,version=state.version;state.v042.tracked=site;try{if(saveGame(false)===false)throw Error();}catch{state.v042.tracked=previous;state.lastSave=lastSave;state.version=version;return notify('Le suivi ne peut pas être sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
 function observed(id,worldOwner,stateOwner){
  if(world!==worldOwner||state!==stateOwner)return false;const plan=MistralLoreContinuity.reduce(state.v053Lore,bindings,{type:'observe',quest:'signaux'},{siteId:id,physicalObservation:true,inventory:state.inventory,playTime:state.playTime});return plan.ok?transact(plan,'Le repère des crêtes a été observé sur place.'):false;
 }
 const oldRead=v042ReadSite;v042ReadSite=function(id){const it=world?.interactables?.find(i=>i.id==='v042-lore-'+id),p=state.player.pos,physical=!blocked()&&it&&dist2(p,it.pos)<=3.6&&Math.abs(p[1]-it.pos[1])<2.8&&lineOfSight(p,it.pos),owner=world,stateOwner=state,result=oldRead(...arguments);if(physical)observed(id,owner,stateOwner);return result;};
 function info(){return{schema:1,quests:bindings.map(q=>{const s=state.v053Lore.quests[q.id];return{id:q.id,name:q.name,faction:q.faction,contactSite:q.contactSite,observationSites:q.observationSites.slice(),witnessSites:q.witnessSites.slice(),available:q.available,accepted:s.accepted,outcome:s.outcome,witnesses:s.witnesses.slice(),observations:s.observations.slice(),audit:s.audit,progress:MistralLoreContinuity.progress(q,s),contact:!!contact(q.contactSite),nextSite:MistralLoreContinuity.nextSite(q,s)};}),journal:copy(state.v053Lore.journal),stations:['canal13','centtreves','lazaret'],origin:'New extensions of the established repository canon; original v0.44 conversation/source not recovered'};}
 function panel(c){const esc=v027Escape,deny=blocked();c.innerHTML='<div class="p27-long"><p class="p27-kicker">LES VOIX DES RELAIS</p><h2>Dossiers et engagements</h2><p>Les habitants peuvent attester une présence, contester un registre ou demander des fournitures. Chaque décision conserve ses preuves, ses coûts et ses conséquences.</p>'+(deny?'<p>'+esc(deny)+'</p>':'')+bindings.map(q=>{const s=state.v053Lore.quests[q.id],progress=MistralLoreContinuity.progress(q,s),giver=v042Site(q.contactSite),present=!!contact(q.contactSite),witness=q.witnessSites.find(id=>!!contact(id)),outcome=q.choices.find(x=>x.id===s.outcome);return'<section class="v046-notice"><h3>'+esc(q.name)+'</h3><p>'+esc(q.factionName)+' · '+esc(giver?.name||'Relais indisponible')+'</p><p>'+esc(q.description)+'</p><p>'+esc(outcome?.text||q.pending)+'</p><p>'+esc(progress.text)+'</p>'+(!q.available?'':!s.accepted?v027Button('Ouvrir le dossier au relais','l53:accept',q.id,!!deny||!present):s.outcome?'<p>Décision et récompense conservées. Ce dossier ne se renouvelle pas.</p>':v027Button('Suivre le prochain repère','l53:track',q.id,!!deny)+(['testimony','audit'].includes(q.kind)?v027Button('Recueillir le témoignage du relais présent','l53:witness',q.id+'|'+(witness||''),!!deny||!witness||s.witnesses.includes(witness)||s.witnesses.length>=q.required):'')+(q.kind==='audit'?v027Button('Analyser la copie · INT 5, 1 circuit','l53:audit',q.id,!!deny||!present||s.audit||Number(state.character.special.I||0)<5||!MistralLoreContinuity.enough(state.inventory,{circuitry:1})):'' )+q.choices.map(ch=>'<p>'+esc(ch.label)+' · '+ch.caps+' capsules, '+ch.xp+' XP.</p>'+v027Button('Conclure : '+ch.label,'l53:resolve',q.id+'|'+ch.id,!!deny||!present||!progress.ready||!MistralLoreContinuity.enough(state.inventory,ch.cost))).join(''))+'</section>';}).join('')+'<h3>Bulletins des relais</h3><p>Canal 13, la Ligue des Cent Trêves et le Lazaret rendent compte des engagements conservés. Les fréquences se consultent dans RADIO.</p>'+v027Button('Ouvrir les stations','jump','radio:stations')+'</div>';}
 const oldData=v027Data;v027Data=function(c){if(V027.sub==='continuity')return panel(c);const result=oldData(...arguments);if(V027.sub==='france')c.insertAdjacentHTML('beforeend','<section class="v046-notice"><h2>Les voix des relais</h2><p>La Convention, CONCORDE, les Vigies et les Insulaires ont de nouveaux engagements à proposer sur le territoire.</p>'+v027Button('Consulter les dossiers des relais','jump','data:continuity')+'</section>');return result;};
 const oldDispatch=v027Dispatch;v027Dispatch=function(action,arg=''){if(typeof action!=='string'||!action.startsWith('l53:'))return oldDispatch(...arguments);if(!v027CanAct())return false;const[a,b]=String(arg).split('|');if(action==='l53:track')return track(a);if(action==='l53:accept')return act('accept',a);if(action==='l53:audit')return act('audit',a);if(action==='l53:witness')return act('witness',a,null,b);if(action==='l53:resolve')return act('resolve',a,b);return false;};
 function conversation(id){
  const d=V042_RUNTIME.npcData.get(id),site=d&&v042Site(d.siteId);if(!d||!site||!contact(site.id))return false;const relevant=bindings.filter(q=>q.contactSite===site.id||q.witnessSites.includes(site.id)&&['testimony','audit'].includes(q.kind)&&state.v053Lore.quests[q.id].accepted),choices=[],lines=[];
  for(const q of relevant){const s=state.v053Lore.quests[q.id];if(s.outcome){lines.push(q.factionName+' : '+q.choices.find(c=>c.id===s.outcome).text);continue;}if(!s.accepted&&q.contactSite===site.id)choices.push({text:'Ouvrir « '+q.name+' ».',onChoose:()=>{act('accept',q.id);conversation(id);}});if(s.accepted){lines.push(q.name+' — '+MistralLoreContinuity.progress(q,s).text);if(['testimony','audit'].includes(q.kind)&&q.witnessSites.includes(site.id)&&!s.witnesses.includes(site.id)&&s.witnesses.length<q.required)choices.push({text:'Consigner le témoignage pour « '+q.name+' ».',onChoose:()=>{act('witness',q.id,null,site.id);conversation(id);}});if(q.contactSite===site.id){if(q.kind==='audit'&&!s.audit)choices.push({text:'Analyser la copie CERFA-77 · INT 5 et 1 circuit.',condition:()=>Number(state.character.special.I||0)>=5&&MistralLoreContinuity.enough(state.inventory,{circuitry:1}),onChoose:()=>{act('audit',q.id);conversation(id);}});if(MistralLoreContinuity.progress(q,s).ready)for(const ch of q.choices)choices.push({text:q.name+' · '+ch.label,condition:()=>MistralLoreContinuity.enough(state.inventory,ch.cost),onChoose:()=>{act('resolve',q.id,ch.id);conversation(id);}});}}}
  choices.push({text:'Parler du secteur et commercer.',onChoose:()=>oldTalk(id)},{text:'Consulter tous les dossiers des relais.',onChoose:()=>{closeDialogue();v027Open('data','continuity');}},{text:'Prendre congé.',onChoose:closeDialogue});openDialogue(speaker(d.name,d.role.toUpperCase(),'FR'),lines.join('\n\n')||'Les relais recueillent des engagements qui doivent pouvoir être tenus sur place. Les noms des factions ne remplacent pas une preuve ni les fournitures promises.',choices);return true;
 }
 const oldTalk=v042TalkNPC;v042TalkNPC=function(id){const d=V042_RUNTIME.npcData.get(id),site=d&&v042Site(d.siteId),relevant=site&&bindings.some(q=>q.contactSite===site.id||q.witnessSites.includes(site.id)&&['testimony','audit'].includes(q.kind)&&state.v053Lore.quests[q.id].accepted);return relevant&&conversation(id)||oldTalk(...arguments);};
 const channels={canal13:{name:'Canal 13 — Ronds-Points Libres',freq:'107.3',hint:'Témoignages et avertissements'},centtreves:{name:'Ligue des Cent Trêves',freq:'101.3',hint:'COCHONNET et engagements tenus'},lazaret:{name:'Lazaret — l’autre rive',freq:'90.8',hint:'Accueil et traversées'}};
 for(const[id,channel]of Object.entries(channels))V027_STATIONS[id]={...channel,available:()=>id==='centtreves'?!!(state.v046.lore.petanque?.played||state.v046.lore.accepted?.encore||state.v046.lore.accepted?.pointe):id==='lazaret'?state.v053Lore.quests.lazaret.accepted||!!(v042Site(bindings.find(q=>q.id==='lazaret').contactSite)&&v042SiteDiscovered(v042Site(bindings.find(q=>q.id==='lazaret').contactSite))):bindings.some(q=>q.id!=='lazaret'&&state.v053Lore.quests[q.id].accepted),text:()=>MistralLoreContinuity.bulletin(id,state.v053Lore,bindings,state.v046.lore)};
 const oldRows=v027QuestRows;v027QuestRows=function(){return oldRows(...arguments).concat(bindings.filter(q=>state.v053Lore.quests[q.id].accepted).map(q=>{const s=state.v053Lore.quests[q.id],target=MistralLoreContinuity.nextSite(q,s);return{id:'l53:'+q.id,name:q.name,stage:s.outcome?'done':'active',active:!s.outcome&&state.v042.tracked===target,text:MistralLoreContinuity.progress(q,s).text,zone:null,steps:[['Engagement pris au relais',true],[q.pending,!!s.outcome||MistralLoreContinuity.progress(q,s).ready],['Décision rapportée au contact',!!s.outcome]],source:q.factionName,badge:s.outcome?'✓':'',hint:q.factionName};}));};
 const oldTrack=v027Track;v027Track=function(id){return typeof id==='string'&&id.startsWith('l53:')?track(id.slice(4)):oldTrack(...arguments);};
 globalThis.v053LoreAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v053LoreInfo:info,v053LoreAccept:id=>act('accept',id),v053LoreWitness:(id,siteId)=>act('witness',id,null,siteId),v053LoreAudit:id=>act('audit',id),v053LoreResolve:(id,choice)=>act('resolve',id,choice),v053LoreTrack:track,v053LoreOpen:()=>v027Open('data','continuity')});};
}
