/* Notaires de l’Après — original Fallout: Mistral fiction.
 * Residence, ownership, insurance and voting are separate records.
 * Pure state machine, then a bounded overlay in the existing Radieuse instance. */
const MistralNotaires = (() => {
 'use strict';
 const own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const copy=v=>JSON.parse(JSON.stringify(v));
 const count=n=>Number.isSafeInteger(n)&&n>=0&&n<=999999;
 const READINGS={
  ordre:{name:'Le protocole des minutes',point:'desk',text:'Le coffre trie les deux derniers chiffres de trois dates : titre du lot (2076), convention d’entretien (2248), avenant d’assurance (2286). Il conserve cet ordre de dépôt, pas une hiérarchie des droits. Les rouleaux portent 00, 76, 48 et 86.'},
  lot:{name:'Un lot sans héritier établi',point:'registre',text:'La copie de 2076 décrit les parties communes, pas les abris construits sur le toit. Aucun héritier actuel n’est établi par cette seule feuille. Le cachet conserve un titre ancien ; il ne désigne pas automatiquement un propriétaire vivant.'},
  couverture:{name:'Le reçu n’est pas un acte',point:'assurance',text:'Le règlement de la Mutuelle porte sur la fuite documentée. Ni une indemnité ni un avenant d’assurance ne transfère la propriété des communs. Le règlement choisi reste conservé sans modification.'}
 };
 const DECISIONS={
  repertoire:{name:'Répertoire contradictoire',text:'Les titres anciens restent lisibles, avec les présences actuelles et leurs réserves inscrites en marge. Aucun héritier n’est inventé et aucun ordre d’expulsion n’est produit. Le litige de propriété demeure ouvert.'},
  usage:{name:'Convention d’usage des communs',text:'Josiane et Salomé déposent un accord local pour l’entretien et l’usage des communs, toit compris. Il ne transfère pas la propriété et ne répare pas rétroactivement une exclusion du scrutin. Les autres titres restent archivés.'},
  depot:{name:'Double garde, titre non tranché',text:'Deux copies contradictoires restent sous des gardes distinctes. Les résidents ne sont pas effacés ; la propriété n’est attribuée à personne dans ce dossier. La question reste ouverte, sans procès gagné par anticipation.'}
 };
 const METHODS={
  sequence:{name:'Respecter l’ordre de dépôt',cost:{},int:0},
  technique:{name:'Déverrouiller le mécanisme · INT 5',cost:{scrap:1},int:5},
  force:{name:'Forcer la fermeture · 2 ferrailles',cost:{scrap:2},int:0}
 };
 const CHOICES=['76','48','86','00'],READ_IDS=Object.keys(READINGS),WITNESSES=['josiane','salome'];
 const CLAUSES={charges:['solidarite','usage','avance'],representation:['occupants','lots'],controle:['audit','syndic']};
 function validSource(b){return !!b&&Object.keys(CLAUSES).every(k=>CLAUSES[k].includes(b.clauses?.[k]))&&typeof b.roofHeard==='boolean'&&['forfait','avenant','entraide'].includes(b.settlement);}
 function source(s){
  const r=s?.v063Radieuse,m=s?.v064Mutuelle;
  if(r?.accepted!==true||r.finished!==true||r.vote?.passed!==true||!Array.isArray(r.works)||!['pompe','reseau','toit'].every(k=>r.works.includes(k)))return null;
  if(!Array.isArray(r.evidence)||!['registre','pompe','reseau','toit'].every(k=>r.evidence.includes(k)))return null;
  if(m?.opened!==true||m.reported!==true||!['copies','technique','mediation'].includes(m.method)||!Array.isArray(m.evidence)||!['contrat','piece','habitants','refus'].every(k=>m.evidence.includes(k)))return null;
  const b={clauses:Object.fromEntries(Object.keys(CLAUSES).map(k=>[k,r.clauses?.[k]])),roofHeard:Array.isArray(r.heard)&&r.heard.includes('salome'),settlement:m.outcome};
  if(!validSource(b)||!m.basis||Object.keys(CLAUSES).some(k=>m.basis.clauses?.[k]!==b.clauses[k])||m.basis.roofHeard!==b.roofHeard)return null;
  return b;
 }
 function fresh(){return {schema:1,revision:0,opened:false,source:null,readings:[],witnesses:[],dials:['00','00','00'],vault:null,original:false,verified:false,decision:null,receipts:[],closed:false,journal:[]};}
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Registre notarial plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.opened=raw.opened===true&&validSource(raw.source);
  if(l.opened){l.source={clauses:Object.fromEntries(Object.keys(CLAUSES).map(k=>[k,raw.source.clauses[k]])),roofHeard:raw.source.roofHeard,settlement:raw.source.settlement};
   l.readings=READ_IDS.filter(k=>Array.isArray(raw.readings)&&raw.readings.includes(k));
   l.witnesses=WITNESSES.filter(k=>Array.isArray(raw.witnesses)&&raw.witnesses.includes(k));
   l.dials=l.dials.map((v,i)=>CHOICES.includes(raw.dials?.[i])?raw.dials[i]:v);
   l.vault=l.readings.length===3&&own(METHODS,raw.vault)?raw.vault:null;
   l.original=!!l.vault&&raw.original===true;
   l.verified=l.original&&(l.vault!=='force'||raw.verified===true);
   if(l.original&&l.witnesses.length===2&&own(DECISIONS,raw.decision)&&(l.verified||raw.decision==='depot'))l.decision=raw.decision;
   l.receipts=l.decision?WITNESSES.filter(k=>Array.isArray(raw.receipts)&&raw.receipts.includes(k)):[];
   l.closed=!!l.decision&&l.receipts.length===2&&raw.closed===true;
  }
  l.revision=count(raw.revision)?raw.revision:0;
  const actions=['open','read','witness','dial','unseal','collect','verify','decide','notify','close'];
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&actions.includes(e.type)).slice(-32).map(e=>({type:e.type,id:typeof e.id==='string'?e.id.slice(0,32):null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];
  return l;
 }
 function context(raw){const l=migrate(raw);if(!l.source)return 'Le dossier suivra le procès-verbal et le reçu, sans les remplacer.';
  return (l.source.clauses.representation==='lots'?'Le toit reste exclu du scrutin historique.':'Le toit avait une voix au scrutin.')+' '+({forfait:'La quittance de la Mutuelle couvre les seuls lots inscrits.',avenant:'L’avenant assure les occupants, sans leur attribuer un titre.',entraide:'L’entraide n’a pas soldé le litige d’assurance.'}[l.source.settlement]);}
 function briefing(raw){const l=migrate(raw);if(!l.opened)return 'Après remise du reçu de la Mutuelle, rencontrez Maître Élias Benhamou dans le hall.';
  if(l.closed)return 'Les deux destinataires ont leur copie. Le registre est clos, pas l’histoire de la propriété.';
  if(l.decision)return DECISIONS[l.decision].name+' · '+l.receipts.length+'/2 copies remises. Revenez ensuite au notaire.';
  if(!l.vault)return l.readings.length+'/3 documents, '+l.witnesses.length+'/2 mandats. Examinez ensuite le coffre de la rue intérieure.';
  if(!l.original)return 'Le coffre est ouvert. Prélevez la minute conservée à l’intérieur.';
  return (l.verified?'Minute comparée aux copies conservées.':'Fermeture forcée : le scellé ne prouve plus la chaîne de garde.')+' Confrontez les deux mandats puis choisissez un acte auprès d’Élias.';
 }
 function apply(snapshot,a={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));
  if(!ctx.local||!ctx.near)throw Error('Rejoignez le document ou l’interlocuteur dans la Cité Radieuse.');
  const b=source(snapshot);if(!b)throw Error('Faites réceptionner les travaux et remettez le reçu de la Mutuelle.');
  if(!Number.isFinite(snapshot.player?.hp)||snapshot.player.hp<=0||!count(snapshot.player.caps))throw Error('État du personnage invalide.');
  const l=migrate(snapshot.v065Notaires);
  if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Cette proposition est périmée.');
  if(l.opened&&JSON.stringify(l.source)!==JSON.stringify(b))throw Error('Le contexte source a changé. Le dossier conservé ne sera pas réécrit.');
  if(l.closed)throw Error('Ce registre est déjà clos.');
  if(l.revision===999999)throw Error('Registre plein. Aucune nouvelle écriture autorisée.');
  const out=copy(snapshot);out.inventory??={};
  const at=id=>{if(ctx.point!==id)throw Error('Ce document ou cet interlocuteur ne permet pas cet acte.');};
  const spend=cost=>{for(const[id,n]of Object.entries(cost)){const value=own(snapshot.inventory,id)?snapshot.inventory[id]:0;if(!count(value)||value<n)throw Error('Fournitures insuffisantes ou quantité invalide.');}for(const[id,n]of Object.entries(cost))out.inventory[id]=(snapshot.inventory[id]||0)-n;};
  if(a.type==='open'){at('notaire');if(l.opened)throw Error('Dossier déjà ouvert.');l.opened=true;l.source=b;}
  else{
   if(!l.opened)throw Error('Ouvrez d’abord le dossier auprès du notaire.');
   if(a.type==='read'){if(!own(READINGS,a.id))throw Error('Document inconnu.');at(READINGS[a.id].point);if(l.readings.includes(a.id))throw Error('Copie déjà conservée.');l.readings.push(a.id);}
   else if(a.type==='witness'){if(!WITNESSES.includes(a.id))throw Error('Mandataire inconnu.');at(a.id);if(l.witnesses.includes(a.id)||l.decision)throw Error('Mandat déjà conservé ou décision enregistrée.');l.witnesses.push(a.id);}
   else if(a.type==='dial'){at('vault');if(l.vault||!Number.isInteger(a.id)||a.id<0||a.id>2||!CHOICES.includes(a.value))throw Error('Rouleau invalide ou coffre déjà ouvert.');l.dials[a.id]=a.value;}
   else if(a.type==='unseal'){
    at('vault');if(l.vault||l.readings.length!==3||!own(METHODS,a.id))throw Error('Trois documents sont requis ; le coffre ne s’ouvre qu’une fois.');
    if(a.id==='sequence'&&l.dials.join('-')!=='76-48-86')throw Error('Ordre incorrect : titre, entretien, assurance. Aucun scellé n’a été détruit.');
    if(a.id==='technique'&&(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5))throw Error('Intelligence 5 nécessaire.');
    spend(METHODS[a.id].cost);l.vault=a.id;
   }else if(a.type==='collect'){at('vault');if(!l.vault||l.original)throw Error('Minute inaccessible ou déjà prélevée.');l.original=true;l.verified=l.vault!=='force';}
   else if(a.type==='verify'){at('notaire');if(!l.original||l.verified||l.decision)throw Error('Contre-vérification indisponible.');spend({cloth:2});l.verified=true;}
   else if(a.type==='decide'){
    at('notaire');if(!l.original||l.witnesses.length!==2||l.decision||!own(DECISIONS,a.id))throw Error('Minute et deux mandats nécessaires ; acte exclusif.');
    if(!l.verified&&a.id!=='depot')throw Error('Scellé rompu : contre-vérifiez les copies ou choisissez la double garde.');l.decision=a.id;
   }else if(a.type==='notify'){if(!WITNESSES.includes(a.id))throw Error('Destinataire inconnu.');at(a.id);if(!l.decision||l.receipts.includes(a.id))throw Error('Acte absent ou copie déjà remise.');l.receipts.push(a.id);}
   else if(a.type==='close'){at('notaire');if(!l.decision||l.receipts.length!==2)throw Error('Les deux copies doivent être remises.');if(out.player.caps>999964)throw Error('Compte de capsules plein.');out.player.caps+=35;l.closed=true;}
   else throw Error('Action notariale inconnue.');
  }
  l.revision++;l.journal.push({type:a.type,id:a.id==null?null:String(a.id),at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});l.journal=l.journal.slice(-32);out.v065Notaires=l;return out;
 }
 return {READINGS:copy(READINGS),DECISIONS:copy(DECISIONS),METHODS:copy(METHODS),CHOICES:CHOICES.slice(),fresh,migrate,source,context,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralNotaires;

if(typeof baseState==='function'&&typeof MistralMutuelle!=='undefined'){
 const M=MistralNotaires,copy=v=>JSON.parse(JSON.stringify(v));
 const P={notaire:[-4,0,18],desk:[-4,0,15.5],vault:[-5,3.2,-14],registre:[-16,0,22],assurance:[5,0,19.5],josiane:[-7,0,22],salome:[10,6.4,-28]};
 const NPC='n65:notaire',rt={busy:false,error:null};
 const base=baseState;baseState=function(...a){const s=base(...a);s.v065Notaires=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(raw);s.v065Notaires=M.migrate(raw?.v065Notaires);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v063Radieuse&&state.v042?.activeInterior===MistralRadieuse.SITE.id;
 const ready=()=>!!M.source(state);
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc géographique sans écriture de campagne.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':inCombat?'Terminez le combat.':null;}
 function near(id){const p=P[id];if(!local()||!p)return false;const npcId={notaire:NPC,josiane:'r63:josiane',salome:'r63:salome'}[id];if(npcId&&!world.npcs.some(n=>n.id===npcId&&n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.2&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7]);}
 function point(type,id){return type==='read'?M.READINGS[id]?.point:['witness','notify'].includes(type)?id:['dial','unseal','collect'].includes(type)?'vault':'notaire';}
 function notice(t){V027.message=t;toast(t,'bad');return false;}
 function act(type,id,value,revision){
  if(rt.busy)return false;const owner=state,scene=world,before=copy(owner),where=point(type,id);let next;
  try{next=M.apply(owner,{type,id,value},{local:local(),near:near(where),point:where,blocked:blocked(),revision});}catch(e){return notice(e.message);}
  rt.busy=true;
  try{owner.v065Notaires=next.v065Notaires;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde notariale refusée.');}
  catch(e){if(state===owner){for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}return notice(e.message+' Échange annulé.');}finally{rt.busy=false;}
  try{bind(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='close'?'Deux copies remises · 35 capsules, une fois.':'Registre notarial sauvegardé.','good');}catch(e){rt.error=e.message;}
  return true;
 }
 function guard(fn){const owner=state,scene=world,rev=state.v065Notaires.revision;return()=>state===owner&&world===scene&&rev===state.v065Notaires.revision?fn(rev):notice('Cette conversation est périmée.');}
 function accessible(id){return !blocked()&&ready()&&near(id);}
 function closeChoice(){return {text:'Revenir.',onChoose:closeDialogue};}
 function confirm(id){if(!accessible('notaire'))return false;openDialogue(speaker('Maître Élias Benhamou','NOTAIRES DE L’APRÈS','EB'),M.DECISIONS[id].name+'\n\n'+M.DECISIONS[id].text+'\n\n'+M.context(state.v065Notaires)+'\n\nACTE EXCLUSIF : aucune expulsion ni attribution automatique de propriété. Deux copies devront être remises. L’indemnité de tournée est de 35 capsules après les deux reçus.',[{text:'Confirmer cet acte.',onChoose:guard(rev=>{act('decide',id,null,rev);notary();})},{text:'Revenir aux actes.',onChoose:guard(notary)}]);return true;}
 function notary(){
  if(!accessible('notaire'))return notice(blocked()||'Élias attend après la remise du reçu de la Mutuelle.');const l=state.v065Notaires,choices=[];
  if(!l.opened)choices.push({text:'Ouvrir « Les clés ne font pas un titre ».',onChoose:guard(rev=>{act('open',null,null,rev);notary();})});
  if(l.original&&!l.verified&&!l.decision)choices.push({text:'Contre-vérifier les copies · 2 tissus.',onChoose:guard(rev=>{act('verify',null,null,rev);notary();})});
  if(l.original&&l.witnesses.length===2&&!l.decision)for(const [id,d]of Object.entries(M.DECISIONS))choices.push({text:'Examiner : '+d.name,onChoose:guard(()=>confirm(id))});
  if(l.decision&&l.receipts.length===2&&!l.closed)choices.push({text:'Clore le registre · 35 capsules.',onChoose:guard(rev=>{act('close',null,null,rev);notary();})});
  choices.push(closeChoice());
  openDialogue(speaker('Maître Élias Benhamou','GOULE CONSCIENTE · NOTAIRES DE L’APRÈS','EB'),(!l.opened?'« Ma peau a mieux survécu que certains actes. Ne prenez pas ma mémoire pour une preuve. Une clé ouvre une porte ; elle ne dit pas qui a le droit d’y vivre. Je conserve les titres, les présences et les désaccords, dans trois chemises distinctes. »\n\n':'')+M.briefing(l)+'\n\n'+M.context(l)+(l.decision?'\n\n'+M.DECISIONS[l.decision].text:''),choices);return true;
 }
 function read(id){const r=M.READINGS[id];if(!r||!accessible(r.point)||!state.v065Notaires.opened)return false;const done=state.v065Notaires.readings.includes(id),choices=[];if(!done)choices.push({text:'Conserver une copie de lecture.',onChoose:guard(rev=>{act('read',id,null,rev);read(id);})});choices.push(closeChoice());openDialogue(speaker(r.name,'MINUTES DISTINCTES','NA'),r.text+'\n\n'+(id==='couverture'?M.context(state.v065Notaires):'L’original reste intact.')+(done?'\nCopie conservée.':''),choices);return true;}
 function witness(id){if(!accessible(id)||!state.v065Notaires.opened)return false;const l=state.v065Notaires,choices=[];if(!l.witnesses.includes(id)&&!l.decision)choices.push({text:'Consigner ce mandat distinct.',onChoose:guard(rev=>{act('witness',id,null,rev);witness(id);})});if(l.decision&&!l.receipts.includes(id))choices.push({text:'Remettre sa copie de l’acte.',onChoose:guard(rev=>{act('notify',id,null,rev);witness(id);})});choices.push(closeChoice());openDialogue(speaker(id==='josiane'?'Josiane Roux':'Salomé Veyre','MANDAT NOTARIAL LOCAL','NA'),(id==='josiane'?'« Conservez les anciens comptes. Je signe pour l’entretien des communs, pas pour vendre la maison de quelqu’un d’autre. »':'« Ne me transformez ni en propriétaire imaginaire, ni en équipement du toit. Notez notre présence et ce que nous acceptons réellement. »')+'\n\n'+M.context(l)+(l.decision?'\n\n'+M.DECISIONS[l.decision].text:''),choices);return true;}
 function vault(){
  if(!accessible('vault')||!state.v065Notaires.opened)return false;const l=state.v065Notaires,choices=[];
  if(!l.vault){for(let i=0;i<3;i++)choices.push({text:'Tourner le rouleau '+(i+1)+' · '+l.dials[i],onChoose:guard(rev=>{const value=M.CHOICES[(M.CHOICES.indexOf(l.dials[i])+1)%M.CHOICES.length];act('dial',i,value,rev);vault();})});for(const[id,m]of Object.entries(M.METHODS))choices.push({text:m.name,onChoose:guard(rev=>{act('unseal',id,null,rev);vault();})});}
  else if(!l.original)choices.push({text:'Prélever la minute sous protection.',onChoose:guard(rev=>{act('collect',null,null,rev);vault();})});
  choices.push(closeChoice());
  openDialogue(speaker('Coffre des minutes','TITRE · ENTRETIEN · ASSURANCE','NA'),!l.vault?'Trois rouleaux : '+l.dials.join(' — ')+'. Le protocole du bureau explique l’ordre. Un essai incorrect ne détruit rien.\n\nForcer ouvre aussi la fermeture, mais rompt sa chaîne de garde : il faudra contre-vérifier les copies pour les actes autres que la double garde.':l.original?'La minute est protégée dans le dossier, pas vendable dans le sac. Le coffre ne crée pas de seconde copie au rechargement.':'La fermeture est ouverte. Le cahier de dépôt distingue les titres de 2076, les engagements d’entretien de 2248 et l’assurance de 2286. Aucun n’efface les autres.',choices);return true;
 }
 function topic(call,label,fn){const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text:label,onChoose:guard(fn)},...(ch||[]).slice(-1)],...rest);};try{return call();}finally{openDialogue=old;}}
 function bind(w){
  if(!w?.v063Radieuse)return;
  if(w.v065Owner!==state){for(const k of['staticDraws','colliders','interactables','npcs'])w[k]=w[k].filter(o=>!o.v065Notaires);w.v065Owner=state;w.v065Installed=false;w.v065Key=null;}
  if(!ready()){if(w.v065Installed){for(const k of['staticDraws','colliders','interactables','npcs'])w[k]=w[k].filter(o=>!o.v065Notaires);w.v065Installed=false;w.v065Key=null;}return;}
  if(!w.v065Installed){
   w.v065Installed=true;
   const box=(pos,size,color,solid=false)=>{const d=addBox(w,pos,size,color);d.v065Notaires=true;if(solid){const c=addCollider(w,pos[0],pos[2],size[0],size[2],{minY:pos[1]-size[1]/2,maxY:pos[1]+size[1]/2});c.v065Notaires=true;}return d;};
   const n=addHumanNPC(w,NPC,'Maître Élias Benhamou','Notaire de l’Après',P.notaire,[.27,.31,.36],{skin:[.47,.45,.34],dialogue:NPC,yaw:Math.PI});n.v065Notaires=true;
   box([-4,.45,15.5],[1.8,.9,.9],[.34,.26,.16],true);box([-4,.97,15.5],[1.4,.12,.65],[.72,.67,.51]);
   for(let i=0;i<3;i++)box([-4.5+i*.5,1.1,15.4],[.30,.18,.38],[[.32,.43,.61],[.52,.36,.22],[.39,.54,.33]][i]);
   const plaque=box([-4,1.04,15.8],[1.3,.035,.18],[.58,.38,.20]);plaque.v065Plaque=true;
   // Sealed cabinet is clear of the reserve, the stairs and the four earlier exhibits.
   const [x,y,z]=P.vault;
   box([x,y+.08,z],[2,.16,1.1],[.20,.25,.24],true);box([x-.92,y+1,z],[.16,2,1.1],[.24,.28,.27],true);box([x+.92,y+1,z],[.16,2,1.1],[.24,.28,.27],true);box([x,y+1,z-.48],[2,2,.14],[.24,.28,.27],true);box([x,y+2,z],[2,.15,1.1],[.24,.28,.27],true);
   const door=box([x,y+1,z+.49],[1.7,1.9,.12],[.38,.43,.37]);door.v065Door=true;
   const c=addCollider(w,x,z+.49,1.7,.12,{id:'n65:door',minY:y,maxY:y+2});c.v065Notaires=true;c.v065Door=true;
   const paper=box([x,y+.4,z+.08],[1.1,.13,.65],[.78,.73,.56]);paper.v065Paper=true;
   for(const id of['desk','vault']){const p=P[id],it=addInteract(w,'n65:'+id,[p[0],p[1]+1.25,p[2]+.7],id==='vault'?'Examiner le coffre des minutes':'Lire le protocole des minutes',()=>w===world&&w.v065Owner===state&&(id==='vault'?vault():read('ordre')),{kind:'quest',radius:3.2,priority:5,condition:()=>accessible(id)&&state.v065Notaires.opened});it.v065Notaires=true;}
   for(const id of['josiane','salome']){const p=P[id];for(const [off,size,col]of [[[1,.05,0],[.6,.1,.42],[.23,.27,.24]],[[1,.43,0],[.08,.78,.08],[.34,.35,.28]],[[1,.9,0],[.5,.7,.08],[.38,.55,.39]]]){const d=box(p.map((v,i)=>v+off[i]),size,col);d.v065Receipt=id;d.v065ReceiptLabel=off[1]===.9;}}
  }
  for(const[id,target]of [['lot','r63:registre'],['couverture','m64:dossier']]){const it=w.interactables.find(o=>o.id===target);if(!it||it.v065Wrapped)continue;it.v065Wrapped=true;const old=it.onInteract;it.onInteract=function(...a){return world===w&&ready()&&state.v065Notaires.opened&&accessible(M.READINGS[id].point)?topic(()=>old(...a),'Notaires · '+M.READINGS[id].name,()=>read(id)):old(...a);};}
  const l=state.v065Notaires,key=[l.vault,l.original,l.decision,l.receipts.join(','),l.closed].join(':');if(w.v065Key===key)return;w.v065Key=key;
  for(const d of w.staticDraws){if(d.v065Door)d.hidden=!!l.vault;if(d.v065Paper)d.hidden=!l.vault||l.original;if(d.v065Receipt)d.hidden=!l.receipts.includes(d.v065Receipt);if(d.v065Plaque)d.color=l.closed?[.28,.54,.35]:l.decision?[.30,.45,.65]:[.58,.38,.20];}
  for(const c of w.colliders)if(c.v065Door)c.disabled=!!l.vault;
 }
 const build=v042BuildInstance;v042BuildInstance=function(...a){const w=build(...a);bind(w);return w;};
 const draw=collectDraws;collectDraws=function(...a){bind(world);return draw(...a);};
 const talk=talkToNPC;talkToNPC=function(id){if(id===NPC){bind(world);return notary();}const who={'r63:josiane':'josiane','r63:salome':'salome'}[id];return who&&state.v065Notaires.opened&&accessible(who)?topic(()=>talk(...arguments),'Notaires · mandat et copie',()=>witness(who)):talk(...arguments);};
 V027_SUBS.data.notaires='NOTAIRES DE L’APRÈS';
 const data=v027Data;v027Data=function(c){if(V027.sub!=='notaires')return data(...arguments);const l=state.v065Notaires,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">MINUTES, PRÉSENCES ET CLÉS</p><h2>Les clés ne font pas un titre</h2><p>'+esc(M.briefing(l))+'</p><p>'+esc(M.context(l))+'</p>'+v027Button('Suivre la Cité Radieuse','n65:track')+'<h3>Documents</h3>'+Object.entries(M.READINGS).map(([id,r])=>'<p>'+(l.readings.includes(id)?'✓ ':'— ')+esc(r.name)+'</p>').join('')+'<h3>Coffre</h3><p>'+esc(l.vault?(l.original?'Minute prélevée.':'Minute à prélever.'):l.dials.join(' — '))+'</p><h3>Actes</h3>'+Object.entries(M.DECISIONS).map(([id,d])=>'<section class="v046-notice"><h3>'+esc((l.decision===id?'✓ ':'')+d.name)+'</h3><p>'+esc(d.text)+'</p></section>').join('')+'<p>Les actes se concluent sur place. Ni titres effacés, ni nouveau vote, ni propriété accordée par une assurance.</p></div>';};
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='n65:track'?dispatch('r63:track'):dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v065Notaires;return rows(...arguments).concat(l.opened?[{id:'n65:quest',name:'LES CLÉS NE FONT PAS UN TITRE',stage:l.closed?'done':'active',active:local()&&!l.closed,text:M.briefing(l),zone:null,steps:[['Documents et mandats',l.readings.length===3&&l.witnesses.length===2],['Minute protégée',l.original],['Acte déposé',!!l.decision],['Copies remises',l.receipts.length===2],['Registre clos',l.closed]],source:'Notaires de l’Après',badge:l.closed?'✓':'',hint:'Élias Benhamou · Cité Radieuse'}]:[]);};
 const track=v027Track;v027Track=function(id){return id==='n65:quest'?v027Dispatch('n65:track'):track(...arguments);};
 function next(){const l=state.v065Notaires;if(!l.opened)return'notaire';const r=Object.keys(M.READINGS).find(k=>!l.readings.includes(k));if(r)return M.READINGS[r].point;const h=['josiane','salome'].find(k=>!l.witnesses.includes(k));if(h)return h;if(!l.original)return'vault';if(!l.decision)return'notaire';return ['josiane','salome'].find(k=>!l.receipts.includes(k))||'notaire';}
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local()||!ready())return marker(...arguments);const id=next(),p=P[id];return {zone:world.id,pos:[p[0],p[1]+1.25,p[2]+.7],label:id==='vault'?'Coffre des minutes':id==='notaire'?'Maître Élias Benhamou':'Document ou mandat notarial'};};
 const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local()||!ready())return ui(...arguments);$('questTitle').textContent='LES CLÉS NE FONT PAS UN TITRE';$('questObjective').textContent=M.briefing(state.v065Notaires);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='LES CLÉS NE FONT PAS UN TITRE';f.querySelector('p').textContent=M.briefing(state.v065Notaires);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.notaires={name:'Notaires — les minutes restent',freq:'95.6',hint:'Une présence n’est pas une erreur de classement',available:()=>state.v065Notaires.opened,text:()=>M.briefing(state.v065Notaires)+(state.v065Notaires.decision?' '+M.DECISIONS[state.v065Notaires.decision].text:'')};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v065NotairesInfo:()=>{bind(world);return {ledger:copy(state.v065Notaires),ready:ready(),local:local(),points:copy(P),error:rt.error};},v065NotairesOpen:()=>v027Open('data','notaires'),v065NotairesAction:act});};
}
