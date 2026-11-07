/* Mutuelle Phocéenne — a finite fictional claim, not an insurance simulator.
 * Reads the completed Radieuse record; never rewrites its vote or the regional charter.
 * Pure model first, then the adapter for the existing browser engine. */
const MistralMutuelle = (() => {
 'use strict';
 const own = (o, k) => Object.prototype.hasOwnProperty.call(o || {}, k);
 const copy = value => JSON.parse(JSON.stringify(value));
 const EVIDENCE = {
  contrat: {name:'L’avenant de sauvegarde',point:'registre',text:'L’avenant local de 2286 couvre une stabilisation urgente avant expertise. Il distingue la cause d’un dommage du classement radioactif du territoire. Il ne couvre pas automatiquement chaque habitation.'},
  piece: {name:'Le manchon conservé',point:'pompe',text:'Lucie a gardé le manchon retiré et le reçu des pièces. Ils étayent une rupture mécanique locale, sans prouver une absence de radiation ni donner un droit général à indemnisation.'},
  habitants: {name:'L’annexe du toit',point:'toit',text:'Le plan annexe et les témoignages attestent une présence. Être habitant, être propriétaire et être assuré restent trois choses différentes. Le dossier conserve la décision de l’assemblée, même si elle a exclu le toit.'},
  refus: {name:'Le code de refus automatique',point:'syndic',text:'Le bordereau a classé le dommage « conséquence indirecte de guerre » à partir du secteur, avant lecture du constat. C’est une contradiction vérifiable, pas la preuve que l’experte a provoqué la fuite.'}
 };
 const METHODS = {
  copies:{label:'Déposer une contre-expertise contradictoire',cost:{cloth:2},attribute:null,minimum:0,text:'Deux copies protégées restent à des gardes distinctes. Aucune version n’est effacée.'},
  technique:{label:'Expliquer la rupture mécanique · INT 5',cost:{scrap:1},attribute:'I',minimum:5,text:'L’examen de la pièce limite le litige à la rupture documentée. Il ne certifie pas toute l’installation.'},
  mediation:{label:'Faire reconnaître l’avenant · CHA 5',cost:{},attribute:'C',minimum:5,text:'L’experte reconnaît la contradiction du bordereau sans promettre davantage que sa réserve disponible.'}
 };
 const OUTCOMES = {
  forfait:{name:'Quittance des lots inscrits',caps:45,cost:{},gift:{scrap:3},text:'Le forfait clôt cette réclamation pour les lots assurés. Les habitants du toit restent hors du périmètre d’assurance, même s’ils ont obtenu une voix. Les 45 capsules et trois ferrailles sont confiées au porteur mandaté.'},
  avenant:{name:'Avenant de présence',caps:25,cost:{cloth:2,scrap:2},gift:{cloth:2,circuitry:1},text:'Une couverture locale reconnaît tous les occupants de ce dossier, toit compris. Elle exige une contribution matérielle et conserve un contrôle des quantités. Elle ne rétablit aucune voix exclue du scrutin historique.'},
  entraide:{name:'Entraide sans quittance',caps:0,cost:{food:2,water:2},gift:{stimpak:1,scrap:2},text:'La copropriété refuse de solder ses droits et organise une réserve d’entraide. L’indemnité de la Mutuelle n’est pas versée. Le contre-don provient d’un stock fini des habitants, pas d’un procès futur automatiquement gagné.'}
 };
 const IDS = Object.keys(EVIDENCE);
 const CLAUSES = {charges:['solidarite','usage','avance'],representation:['occupants','lots'],controle:['audit','syndic']};
 const safeCount = n => Number.isInteger(n) && n >= 0 && n <= 999999;
 function basis(r) {
  if(!r || r.finished !== true || r.vote?.passed !== true || r.accepted !== true) return null;
  if(!['pompe','reseau','toit'].every(k=>r.works?.includes(k)) || !['registre','pompe','reseau','toit'].every(k=>r.evidence?.includes(k))) return null;
  if(!Object.keys(CLAUSES).every(k=>CLAUSES[k].includes(r.clauses?.[k]))) return null;
  const clauses=Object.fromEntries(Object.keys(CLAUSES).map(k=>[k,r.clauses[k]]));
  return {clauses,roofHeard:Array.isArray(r.heard)&&r.heard.includes('salome')};
 }
 function validBasis(b) {return !!b && Object.keys(CLAUSES).every(k=>CLAUSES[k].includes(b.clauses?.[k])) && typeof b.roofHeard==='boolean';}
 function fresh(){return {schema:1,revision:0,opened:false,basis:null,evidence:[],method:null,outcome:null,claimed:false,reported:false,journal:[]};}
 function migrate(raw) {
  if(raw && Number.isInteger(raw.schema) && raw.schema>1) throw Error('Dossier de Mutuelle plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.opened=raw.opened===true&&validBasis(raw.basis);
  if(l.opened)l.basis={clauses:Object.fromEntries(Object.keys(CLAUSES).map(k=>[k,raw.basis.clauses[k]])),roofHeard:raw.basis.roofHeard};
  l.evidence=l.opened&&Array.isArray(raw.evidence)?IDS.filter(id=>raw.evidence.includes(id)):[];
  l.method=l.evidence.length===IDS.length&&own(METHODS,raw.method)?raw.method:null;
  l.outcome=l.method&&own(OUTCOMES,raw.outcome)?raw.outcome:null;
  l.claimed=!!l.outcome&&raw.claimed===true;l.reported=!!l.outcome&&raw.reported===true;
  l.revision=safeCount(raw.revision)?raw.revision:0;
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&['open','evidence','argue','settle','claim','report'].includes(e.type)).slice(-24).map(e=>({type:e.type,id:typeof e.id==='string'?e.id.slice(0,32):null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];
  return l;
 }
 function roof(l) {
  if(!l.basis)return 'Le dossier se fonde sur les travaux réceptionnés.';
  return l.basis.clauses.representation==='lots'?'Le toit a été exclu du vote. Aucun accord d’assurance ne peut réécrire ce procès-verbal.':'Les habitants du toit ont été admis au vote. Cela ne les rend pas automatiquement titulaires de l’ancien contrat.';
 }
 function briefing(raw) {
  const l=migrate(raw);
  if(!l.opened)return 'Après réception des travaux, rencontrez Édith Vernet au hall de la Cité Radieuse.';
  if(!l.method)return `${l.evidence.length}/4 pièces confrontées. Présentez ensuite une contre-expertise à Édith.`;
  if(!l.outcome)return 'Le refus automatique est contesté. Trois accords, avec leurs coûts et exclusions, sont proposés par Édith.';
  return OUTCOMES[l.outcome].name+' — '+(l.reported?'Reçu remis à Josiane.':'Rapportez le reçu à Josiane.')+' '+(l.claimed?'Colis retiré.':'Un colis unique attend dans la réserve de la rue intérieure.');
 }
 function apply(snapshot,a={},ctx={}) {
  if(ctx.blocked)throw Error(String(ctx.blocked));
  if(!ctx.local||!ctx.near)throw Error('Rejoignez le bon interlocuteur ou le document dans la Cité Radieuse.');
  const b=basis(snapshot?.v063Radieuse);if(!b)throw Error('Faites d’abord réceptionner les trois travaux par Josiane.');
  if(!Number.isFinite(snapshot.player?.hp)||snapshot.player.hp<=0)throw Error('Une partie active est nécessaire.');
  if(!safeCount(snapshot.player.caps))throw Error('Compte de capsules invalide.');
  const current=migrate(snapshot.v064Mutuelle);
  if(ctx.revision!==undefined&&ctx.revision!==current.revision)throw Error('Cette proposition est périmée. Rouvrez le dialogue.');
  if(current.opened&&JSON.stringify(current.basis)!==JSON.stringify(b))throw Error('Le procès-verbal source diffère du dossier conservé.');
  const out=copy(snapshot),l=migrate(out.v064Mutuelle);out.inventory??={};
  const at=point=>{if(ctx.point!==point)throw Error('Cet acte doit être effectué auprès du bon contact.');};
  // Validate the original values before JSON can turn NaN/Infinity into null.
  const transfer=(items,sign)=>{for(const[id,n]of Object.entries(items)){const value=own(snapshot.inventory,id)?snapshot.inventory[id]:0;if(!safeCount(value)||value+sign*n<0||value+sign*n>999999)throw Error('Fournitures insuffisantes ou quantité invalide.');}for(const[id,n]of Object.entries(items))out.inventory[id]=(out.inventory[id]||0)+sign*n;};
  if(a.type==='open') {
   at('expert');if(l.opened)throw Error('La réclamation est déjà ouverte.');l.opened=true;l.basis=b;
  } else {
   if(!l.opened)throw Error('Ouvrez d’abord la réclamation auprès d’Édith.');
   if(a.type==='evidence') {
    if(!own(EVIDENCE,a.id))throw Error('Pièce inconnue.');at(EVIDENCE[a.id].point);
    if(l.evidence.includes(a.id)||l.outcome)throw Error('Pièce déjà conservée ou dossier clos.');l.evidence.push(a.id);
   } else if(a.type==='argue') {
    at('expert');if(l.evidence.length!==IDS.length||l.method||l.outcome)throw Error('Quatre pièces sont nécessaires ; la contre-expertise ne se paie qu’une fois.');
    if(!own(METHODS,a.id))throw Error('Méthode inconnue.');const method=METHODS[a.id],value=snapshot.character?.special?.[method.attribute];
    if(method.attribute&&(!Number.isFinite(value)||value<method.minimum))throw Error('Caractéristique insuffisante pour cette méthode.');
    transfer(method.cost,-1);l.method=a.id;
   } else if(a.type==='settle') {
    at('expert');if(!l.method||l.outcome)throw Error('Contre-expertise nécessaire ou conclusion déjà enregistrée.');
    if(!own(OUTCOMES,a.id))throw Error('Accord inconnu.');const o=OUTCOMES[a.id];
    if(out.player.caps+o.caps>999999)throw Error('Compte de capsules plein.');
    transfer(o.cost,-1);out.player.caps+=o.caps;l.outcome=a.id;
   } else if(a.type==='claim') {
    at('colis');if(!l.outcome||l.claimed)throw Error('Aucun colis à retirer, ou colis déjà retiré.');transfer(OUTCOMES[l.outcome].gift,1);l.claimed=true;
   } else if(a.type==='report') {
    at('josiane');if(!l.outcome||l.reported)throw Error('Aucun accord à remettre, ou reçu déjà remis.');l.reported=true;
   } else throw Error('Action de Mutuelle inconnue.');
  }
  l.revision=Math.min(999999,l.revision+1);l.journal.push({type:a.type,id:a.id||null,at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});l.journal=l.journal.slice(-24);out.v064Mutuelle=l;return out;
 }
 return {EVIDENCE:copy(EVIDENCE),METHODS:copy(METHODS),OUTCOMES:copy(OUTCOMES),IDS:IDS.slice(),fresh,migrate,basis,roof,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralMutuelle;

if(typeof baseState==='function'&&typeof MistralRadieuse!=='undefined') {
 const M=MistralMutuelle,copy=v=>JSON.parse(JSON.stringify(v));
 const POINTS={expert:[4,0,23],dossier:[5,0,19.5],colis:[9.5,3.2,-11],josiane:[-7,0,22],registre:[-16,0,22],pompe:[-18,0,-8],toit:[-8,6.4,-28],syndic:[17,0,8]};
 const NPC_ID='m64:expert',rt={busy:false,error:null};
 const base=baseState;baseState=function(...args){const s=base(...args);s.v064Mutuelle=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(raw);s.v064Mutuelle=M.migrate(raw?.v064Mutuelle);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v063Radieuse&&state.v042?.activeInterior===MistralRadieuse.SITE.id;
 const ready=()=>!!M.basis(state.v063Radieuse);
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Le banc géographique ne modifie pas la campagne.':zoneTransitioning||V046.busy||V047.pending?'Attendez la fin du chargement.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':inCombat?'Terminez le combat.':null;}
 function near(id){
  const p=POINTS[id];if(!local()||!p)return false;
  if(['expert','josiane'].includes(id)){const n=world.npcs.find(n=>n.id===(id==='expert'?NPC_ID:'r63:josiane'));if(!n||!n.alive)return false;}
  return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.3&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.65]);
 }
 function notice(t){V027.message=t;toast(t,'bad');return false;}
 function pointFor(type,id){return type==='claim'?'colis':type==='report'?'josiane':type==='evidence'?M.EVIDENCE[id]?.point:'expert';}
 function restore(owner,before){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}
 function act(type,id,revision){
  if(rt.busy)return false;const owner=state,scene=world,before=copy(owner),point=pointFor(type,id);let next;
  try{next=M.apply(owner,{type,id},{blocked:blocked(),local:local(),near:near(point),point,revision});}catch(e){return notice(e.message);}
  rt.busy=true;
  try{owner.v064Mutuelle=next.v064Mutuelle;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde du dossier refusée.');}
  catch(e){restore(owner,before);return notice(e.message+' Échange annulé.');}finally{rt.busy=false;}
  try{bind(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='claim'?'Colis retiré une seule fois.':'Pièce ou décision conservée.','good');}catch(e){rt.error=e.message;}
  return true;
 }
 function guarded(fn){const owner=state,scene=world,revision=state.v064Mutuelle.revision;return()=>{if(state!==owner||world!==scene||revision!==state.v064Mutuelle.revision)return notice('Cette conversation est périmée.');return fn(revision);};}
 const amount=o=>Object.keys(o).length?Object.entries(o).map(([id,n])=>n+' '+itemLabel(id)).join(' + '):'aucune fourniture';
 function outcomeText(id){const o=M.OUTCOMES[id];return o.text+'\n\nCoût : '+amount(o.cost)+'. Capsules reçues : '+o.caps+'. Colis unique : '+amount(o.gift)+'.\n\n'+M.roof(state.v064Mutuelle);}
 function confirm(id){
  if(blocked()||!near('expert'))return notice(blocked()||'Rejoignez Édith.');
  openDialogue(speaker('Édith Vernet','EXPERTE · MUTUELLE PHOCÉENNE','EV'),'ACCORD EXCLUSIF — '+M.OUTCOMES[id].name+'\n\n'+outcomeText(id)+'\n\nCe choix clôt les négociations de ce dossier. Ni nouvelles primes automatiques, ni assurance mondiale ne seront créées.',[
   {text:'Confirmer cet accord.',onChoose:guarded(rev=>{act('settle',id,rev);expert();})},
   {text:'Revenir aux propositions.',onChoose:guarded(()=>expert())}
  ]);return true;
 }
 function expert(){
  if(blocked()||!ready()||!near('expert'))return notice(blocked()||'Édith attend dans le hall après réception des travaux.');
  const l=state.v064Mutuelle,choices=[];
  if(!l.opened)choices.push({text:'Ouvrir « Sinistre non couvert ».',onChoose:guarded(rev=>{act('open',null,rev);expert();})});
  else if(!l.method&&l.evidence.length===4)for(const[id,m]of Object.entries(M.METHODS))choices.push({text:m.label+' · '+amount(m.cost),onChoose:guarded(rev=>{act('argue',id,rev);expert();})});
  else if(l.method&&!l.outcome)for(const[id,o]of Object.entries(M.OUTCOMES))choices.push({text:'Examiner : '+o.name,onChoose:guarded(()=>confirm(id))});
  choices.push({text:'Revenir.',onChoose:closeDialogue});
  const text=!l.opened?'« Je couvre un sinistre, pas la fin du monde. Le classement du secteur a rejeté votre fuite avant même que je voie le manchon. Ramenez l’avenant, la pièce, l’annexe des habitants et le bordereau : nous confronterons les quatre. Ma caisse a un fond ; votre droit au recours ne devrait pas en avoir. »':l.outcome?outcomeText(l.outcome):M.briefing(l)+'\n\n'+M.roof(l)+(l.method?'\n\n'+M.METHODS[l.method].text:'');
  openDialogue(speaker('Édith Vernet','EXPERTE · MUTUELLE PHOCÉENNE','EV'),text,choices);return true;
 }
 function evidence(id){
  const e=M.EVIDENCE[id];if(!e||blocked()||!near(e.point)||!state.v064Mutuelle.opened)return false;
  const done=state.v064Mutuelle.evidence.includes(id),choices=[];
  if(!done)choices.push({text:'Verser cette pièce au dossier.',onChoose:guarded(rev=>{act('evidence',id,rev);evidence(id);})});
  choices.push({text:'Revenir.',onChoose:closeDialogue});
  openDialogue(speaker(e.name,'CONTRE-EXPERTISE LOCALE','MP'),e.text+'\n\n'+(id==='habitants'?M.roof(state.v064Mutuelle)+'\n\n':'')+(done?'Copie conservée. La pièce originale et le procès-verbal restent intacts.':'La copie du document sera ajoutée, sans modifier le constat initial.'),choices);return true;
 }
 function receipt(){
  if(blocked()||!near('dossier'))return false;const l=state.v064Mutuelle;
  openNote('m64:receipt','MUTUELLE PHOCÉENNE — DOSSIER LOCAL',M.briefing(l)+'\n\n'+M.roof(l)+(l.outcome?'\n\n'+outcomeText(l.outcome):'\n\nUne caisse finie, des archives contradictoires. Aucun contrat nouveau ne remplace le droit d’exister.'));return true;
 }
 // Interpose a topic only during the existing synchronous dialogue opening.
 // Reopening the base equipment retains its original repair/withdraw choices.
 function withTopic(call,label,callback){const previous=openDialogue;openDialogue=function(s,text,choices,...rest){return previous(s,text,[...(choices||[]).slice(0,-1),{text:label,onChoose:guarded(callback)},...(choices||[]).slice(-1)],...rest);};try{return call();}finally{openDialogue=previous;}}
 function bind(w){
  if(!w?.v063Radieuse)return;
  const active=ready(),l=state.v064Mutuelle;
  if(w.v064Owner!==state){for(const k of['staticDraws','colliders','interactables','npcs'])w[k]=w[k].filter(x=>!x.v064Mutuelle);w.v064Owner=state;w.v064Installed=false;w.v064VisualKey=null;}
  if(!active)return;
  if(!w.v064Installed){
   w.v064Installed=true;
   const box=(p,size,color,solid=false)=>{const d=addBox(w,p,size,color);d.v064Mutuelle=true;if(solid){const c=addCollider(w,p[0],p[2],size[0],size[2],{minY:p[1]-size[1]/2,maxY:p[1]+size[1]/2});c.v064Mutuelle=true;}return d;};
   const npc=addHumanNPC(w,NPC_ID,'Édith Vernet','Experte de la Mutuelle',POINTS.expert,[.36,.32,.27],{dialogue:NPC_ID,yaw:Math.PI});npc.v064Mutuelle=true;
   box([5,.45,19.5],[2.1,.9,.95],[.38,.28,.16],true);
   box([5,.97,19.5],[1.25,.12,.65],[.78,.74,.58]);
   box([5.7,1.25,19.35],[.36,.5,.28],[.21,.30,.24]);
   const plaque=box([4.2,1.04,19.6],[.35,.04,.4],[.67,.34,.18]);plaque.v064Status=true;
   const newIt=(id,p,label,fn)=>{const it=addInteract(w,'m64:'+id,[p[0],p[1]+1.25,p[2]+.65],label,()=>w===world&&w.v064Owner===state&&fn(),{radius:3.3,priority:5,kind:'quest',condition:()=>!blocked()&&near(id)});it.v064Mutuelle=true;return it;};
   newIt('dossier',POINTS.dossier,'Lire le dossier de la Mutuelle',receipt);
   const it=newIt('colis',POINTS.colis,'Retirer le colis du règlement',()=>act('claim',null));it.condition=()=>!blocked()&&near('colis')&&!!state.v064Mutuelle.outcome&&!state.v064Mutuelle.claimed;
   const p=POINTS.colis;
   const crate=box([p[0],p[1]+.35,p[2]],[1,.7,.8],[.47,.32,.17]);crate.v064Gift=true;
   const lid=box([p[0],p[1]+.73,p[2]],[1.06,.08,.86],[.58,.48,.25]);lid.v064Gift=true;
   const c=addCollider(w,p[0],p[2],1,.8,{id:'m64:colis',minY:p[1],maxY:p[1]+.8});c.v064Mutuelle=true;c.v064Gift=true;
  }
  // Wrappers are installed once per original interactable, not once per frame.
  for(const[id,e]of Object.entries(M.EVIDENCE)){
   const it=w.interactables.find(it=>it.id==='r63:'+e.point);if(!it||it.v064Wrapped)continue;it.v064Wrapped=true;const previous=it.onInteract;
   it.onInteract=function(...args){if(world!==w||!ready()||!state.v064Mutuelle.opened||blocked()||!near(e.point))return previous(...args);return withTopic(()=>previous(...args),'Mutuelle · '+e.name,()=>evidence(id));};
  }
  const key=[l.outcome,l.claimed,l.reported].join(':');if(w.v064VisualKey===key)return;w.v064VisualKey=key;
  const show=!!l.outcome&&!l.claimed;
  for(const d of w.staticDraws){if(d.v064Gift)d.hidden=!show;if(d.v064Status)d.color=l.reported?[.25,.55,.34]:l.outcome?[.32,.46,.65]:[.67,.34,.18];}
  for(const c of w.colliders)if(c.v064Gift)c.disabled=!show;
 }
 const build=v042BuildInstance;v042BuildInstance=function(...args){const w=build(...args);bind(w);return w;};
 const draw=collectDraws;collectDraws=function(...args){bind(world);return draw(...args);};
 const talk=talkToNPC;talkToNPC=function(id){
  if(id===NPC_ID){bind(world);return expert();}
  if(id==='r63:josiane'&&local()&&ready()&&!blocked()&&near('josiane')){
   const l=state.v064Mutuelle;return withTopic(()=>talk(...arguments),l.outcome&&!l.reported?'Mutuelle · remettre le reçu':'Mutuelle · le litige des parties communes',rev=>{
    if(l.outcome&&!l.reported)act('report',null,rev);
    openDialogue(speaker('Josiane Roux','PRÉSIDENTE DE SÉANCE','JR'),M.briefing(state.v064Mutuelle)+'\n\n'+M.roof(state.v064Mutuelle),[{text:'Revenir.',onChoose:closeDialogue}]);
   });
  }
  return talk(...arguments);
 };
 V027_SUBS.data.mutuelle='MUTUELLE PHOCÉENNE';
 const data=v027Data;v027Data=function(c){
  if(V027.sub!=='mutuelle'){const result=data(...arguments);if(V027.sub==='radieuse'&&ready())c.insertAdjacentHTML('beforeend','<section class="v046-notice"><h3>Après les travaux : le sinistre</h3><p>Édith Vernet reçoit les recours dans le hall.</p>'+v027Button('Consulter le dossier','jump','data:mutuelle')+'</section>');return result;}
  const l=state.v064Mutuelle,esc=v027Escape;
  c.innerHTML='<div class="p27-long"><p class="p27-kicker">MUTUELLE PHOCÉENNE DE RECONSTRUCTION</p><h2>Sinistre non couvert</h2><p>'+esc(!ready()?'Faites réceptionner les travaux de la Cité Radieuse pour ouvrir ce dossier.':M.briefing(l))+'</p><p>'+esc(M.roof(l))+'</p>'+v027Button('Suivre la Cité Radieuse','m64:track')+'<h3>Pièces conservées</h3>'+M.IDS.map(id=>'<p>'+(l.evidence.includes(id)?'✓ ':'— ')+esc(M.EVIDENCE[id].name)+'</p>').join('')+'<h3>Accords possibles</h3>'+Object.entries(M.OUTCOMES).map(([id,o])=>'<section class="v046-notice"><h3>'+esc((l.outcome===id?'✓ ':'')+o.name)+'</h3><p>'+esc(o.text)+'</p><p>'+esc('Coût : '+amount(o.cost)+' · '+o.caps+' capsules · Colis : '+amount(o.gift))+'</p></section>').join('')+'<p>Les décisions se prennent sur place. Ni vote réécrit, ni primes automatiques, ni réserve renouvelable.</p></div>';
 };
 function track(){if(blocked())return notice(blocked());const owner=state,before=copy(owner);owner.v042.tracked=MistralRadieuse.SITE.id;try{if(state!==owner||saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Suivi non sauvegardé.');}updateQuestUI(true);return true;}
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='m64:track'?v027CanAct()&&track():dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v064Mutuelle;return rows(...arguments).concat(l.opened?[{id:'m64:quest',name:'SINISTRE NON COUVERT',stage:l.reported?'done':'active',active:local()&&!l.reported,text:M.briefing(l),zone:null,steps:[['Quatre pièces confrontées',l.evidence.length===4],['Refus contesté',!!l.method],['Accord choisi',!!l.outcome],['Reçu remis',l.reported],['Colis retiré',l.claimed]],source:'Mutuelle Phocéenne',badge:l.reported?'✓':'',hint:'Édith Vernet · hall de la Cité Radieuse'}]:[]);};
 const oldTrack=v027Track;v027Track=function(id){return id==='m64:quest'?track():oldTrack(...arguments);};
 function next(){const l=state.v064Mutuelle;if(!l.opened)return'expert';const missing=M.IDS.find(id=>!l.evidence.includes(id));if(missing)return M.EVIDENCE[missing].point;if(!l.outcome)return'expert';if(!l.claimed)return'colis';return !l.reported?'josiane':'dossier';}
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local()||!ready())return marker(...arguments);const id=next(),p=POINTS[id];return {zone:world.id,pos:[p[0],p[1]+1.25,p[2]],label:id==='expert'?'Édith Vernet':id==='colis'?'Colis unique':id==='josiane'?'Remettre le reçu':'Dossier de la Mutuelle'};};
 const questUI=updateQuestUI;updateQuestUI=function(flash=false){if(!local()||!ready())return questUI(...arguments);$('questTitle').textContent='SINISTRE NON COUVERT';$('questObjective').textContent=M.briefing(state.v064Mutuelle);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='SINISTRE NON COUVERT';f.querySelector('p').textContent=M.briefing(state.v064Mutuelle);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.mutuelle={name:'Mutuelle Phocéenne — recours et reçus',freq:'94.6',hint:'Une réserve finie ; des preuves qui restent',available:()=>state.v064Mutuelle.opened,text:()=>M.briefing(state.v064Mutuelle)+(state.v064Mutuelle.outcome?' '+M.OUTCOMES[state.v064Mutuelle.outcome].text:'')};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v064MutuelleInfo:()=>{bind(world);return{ledger:copy(state.v064Mutuelle),ready:ready(),local:local(),points:copy(POINTS),error:rt.error};},v064MutuelleOpen:()=>v027Open('data','mutuelle'),v064MutuelleAction:act});};
}
