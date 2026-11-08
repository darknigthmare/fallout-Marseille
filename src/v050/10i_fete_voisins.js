/* La fête des voisins — authored local continuation, not a new regional ending.
 * A meal is neither a vote nor a transfer of title. Historical registries are read-only.
 * Pure model first; actors/props are reconstructed, never serialized into the save. */
const MistralVoisins = (() => {
 'use strict';
 const own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const copy=o=>JSON.parse(JSON.stringify(o));
 const integer=n=>Number.isSafeInteger(n)&&n>=0&&n<=999999;
 const GUESTS=['karim','lucie','nadia','salome'];
 const PANTRY=['rations','vaisselle'];
 const CONTROL={source:['archives','micro'],sortie:['alerte','local'],niveau:['fort','limite']};
 const LABELS={source:'Source',sortie:'Destination',niveau:'Niveau',archives:'Annonce de 2076',micro:'Micro du voisinage',alerte:'Ancienne ligne de sirène',local:'Haut-parleurs de proximité',fort:'Pleine puissance',limite:'Limiteur engagé'};
 const ACTS=['repertoire','usage','depot'];
 const ENDINGS={
  table_ouverte:{name:'Une table, pas une unanimité',text:'Les voisins ont mangé ensemble et répondu aux objections. Les réserves restent lisibles : ni le repas ni les excuses ne changent le scrutin, l’assurance ou les titres.'},
  paliers:{name:'Des voisins, plusieurs tables',text:'Les portions ont circulé entre les paliers. Les objections ont reçu une réponse sans imposer une réunion unique. Les accords antérieurs restent distincts.'},
  treve:{name:'Une trêve à hauteur d’assiette',text:'Chacun a reçu sa portion, mais au moins une objection reste sans réponse. Le repas n’a pas dégénéré ; il n’a pas réconcilié tout le monde non plus.'}
 };
 const REPLIES={karim:{comptes:'Rendre l’origine des portions publique',geste:'Avancer 5 capsules pour le prochain nettoyage',laisser:'Reconnaître que le désaccord reste ouvert'},salome:{reserves:'Dire publiquement ce qui reste contesté',excuses:'Présenter des excuses sans promettre de nouveaux droits · CHA 5',laisser:'Ne pas régler ce désaccord pendant le repas'}};
 function validBasis(b){return !!b&&['lots','occupants'].includes(b.representation)&&['forfait','avenant','entraide'].includes(b.assurance)&&ACTS.includes(b.acte)&&['solidarite','usage','avance'].includes(b.charges)&&['audit','syndic'].includes(b.controle);}
 function basis(s){
  const r=s?.v063Radieuse,m=s?.v064Mutuelle,n=s?.v065Notaires;
  if(r?.accepted!==true||r.finished!==true||r.vote?.passed!==true||!Array.isArray(r.works)||!['pompe','reseau','toit'].every(k=>r.works.includes(k)))return null;
  if(m?.opened!==true||m.reported!==true||!['forfait','avenant','entraide'].includes(m.outcome)||!m.basis)return null;
  if(n?.opened!==true||n.closed!==true||n.original!==true||!ACTS.includes(n.decision)||!['sequence','technique','force'].includes(n.vault)||(!n.verified&&n.decision!=='depot'))return null;
  if(!Array.isArray(n.readings)||!['ordre','lot','couverture'].every(k=>n.readings.includes(k))||!Array.isArray(n.witnesses)||!['salome','josiane'].every(k=>n.witnesses.includes(k))||!Array.isArray(n.receipts)||!['josiane','salome'].every(k=>n.receipts.includes(k)))return null;
  for(const k of ['charges','representation','controle'])if(r.clauses?.[k]!==m.basis.clauses?.[k]||r.clauses?.[k]!==n.source?.clauses?.[k])return null;
  const heard=Array.isArray(r.heard)&&r.heard.includes('salome');
  if(m.basis.roofHeard!==heard||n.source?.roofHeard!==heard||n.source?.settlement!==m.outcome)return null;
  const b={representation:r.clauses.representation,charges:r.clauses.charges,controle:r.clauses.controle,assurance:m.outcome,acte:n.decision};return validBasis(b)?b:null;
 }
 function fresh(){return {schema:1,revision:0,opened:false,basis:null,heard:[],meal:null,pantry:[],notice:false,controls:{source:'archives',sortie:'alerte',niveau:'fort'},sound:null,layout:null,started:false,served:[],answers:{karim:null,salome:null},finished:false,outcome:null,journal:[]};}
 function mealReady(l){return l.meal==='apport'||l.meal==='placard'&&PANTRY.every(k=>l.pantry.includes(k));}
 function soundReady(c){return c?.source==='micro'&&c?.sortie==='local'&&c?.niveau==='limite';}
 function result(l){return !l.answers.karim||!l.answers.salome||Object.values(l.answers).includes('laisser')?'treve':l.layout==='commune'?'table_ouverte':'paliers';}
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Carnet de fête plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.revision=integer(raw.revision)?raw.revision:0;
  l.opened=raw.opened===true&&validBasis(raw.basis);
  if(l.opened){
   l.basis=Object.fromEntries(Object.keys({representation:0,charges:0,controle:0,assurance:0,acte:0}).map(k=>[k,raw.basis[k]]));
   l.heard=GUESTS.filter(k=>Array.isArray(raw.heard)&&raw.heard.includes(k));
   l.meal=['apport','placard'].includes(raw.meal)?raw.meal:null;
   l.pantry=l.meal==='placard'?PANTRY.filter(k=>Array.isArray(raw.pantry)&&raw.pantry.includes(k)):[];
   l.notice=raw.notice===true;
   for(const[k,values]of Object.entries(CONTROL))if(values.includes(raw.controls?.[k]))l.controls[k]=raw.controls[k];
   l.sound=raw.sound==='silence'?'silence':raw.sound==='limitee'&&l.notice&&soundReady(l.controls)?'limitee':null;
   if(raw.started===true&&l.heard.length===4&&mealReady(l)&&l.sound&&['commune','paliers'].includes(raw.layout)){
    l.layout=raw.layout;l.started=true;l.served=GUESTS.filter(k=>Array.isArray(raw.served)&&raw.served.includes(k));
    for(const id of ['karim','salome'])if(l.served.includes(id)&&own(REPLIES[id],raw.answers?.[id]))l.answers[id]=raw.answers[id];
    l.finished=raw.finished===true&&l.served.length===4&&!!l.answers.karim&&!!l.answers.salome;
    l.outcome=l.finished?result(l):null;
   }
  }
  const kinds=['open','listen','meal','collect','notice','switch','sound','start','serve','answer','finish'];
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&kinds.includes(e.type)).slice(-48).map(e=>({type:e.type,id:typeof e.id==='string'?e.id.slice(0,32):null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];return l;
 }
 function context(raw){const l=migrate(raw),b=l.basis;if(!b)return 'Une soirée locale après les travaux, le sinistre et le dépôt des actes.';return (b.representation==='lots'?'Le toit reste exclu du vote historique.':'Le toit a participé au vote historique.')+' '+({usage:'La convention d’usage ne transfère pas la propriété.',repertoire:'Le répertoire conserve des titres et des présences contradictoires.',depot:'La double garde laisse le titre non tranché.'}[b.acte]);}
 function briefing(raw){const l=migrate(raw);if(!l.opened)return 'Après clôture du registre notarial, proposez une fête à Josiane.';if(l.finished)return ENDINGS[l.outcome].text;if(l.started)return `${l.served.length}/4 portions remises. `+(!l.answers.karim||!l.answers.salome?'Écoutez aussi Karim et Salomé avant de conclure.':'Revenez à Josiane pour terminer la soirée.');return `${l.heard.length}/4 voisins consultés · repas ${mealReady(l)?'prêt':'à préparer'} · sonorisation ${l.sound?'sécurisée':'à régler ou couper'}.`;}
 function apply(snapshot,a={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));
  if(!ctx.local||!ctx.near)throw Error('Rejoignez le voisin ou le matériel dans la Cité.');
  const b=basis(snapshot);if(!b)throw Error('Terminez le dossier des Notaires avant cette soirée.');
  if(!Number.isFinite(snapshot.player?.hp)||snapshot.player.hp<=0||!integer(snapshot.player.caps))throw Error('État du personnage invalide.');
  const l=migrate(snapshot.v066Voisins);
  if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Cette proposition est périmée.');
  if(l.opened&&Object.keys(b).some(k=>b[k]!==l.basis[k]))throw Error('Les décisions sources ont changé ; la soirée conservée ne sera pas réécrite.');
  if(l.finished)throw Error('La soirée est déjà terminée.');if(l.revision===999999)throw Error('Carnet plein.');
  const out=copy(snapshot);out.inventory??={};
  const at=id=>{if(ctx.point!==id)throw Error('Cette opération doit se faire au bon endroit.');};
  const before=()=>{if(l.started)throw Error('Le service a commencé : les préparatifs sont figés.');};
  const spend=cost=>{for(const[id,n]of Object.entries(cost)){const v=own(snapshot.inventory,id)?snapshot.inventory[id]:0;if(!integer(v)||v<n)throw Error('Fournitures insuffisantes ou quantité invalide.');}for(const[id,n]of Object.entries(cost))out.inventory[id]=snapshot.inventory[id]-n;};
  if(a.type==='open'){at('josiane');if(l.opened)throw Error('Soirée déjà ouverte.');l.opened=true;l.basis=b;}
  else{
   if(!l.opened)throw Error('Parlez d’abord à Josiane.');
   if(a.type==='listen'){before();at(a.id);if(!GUESTS.includes(a.id)||l.heard.includes(a.id))throw Error('Voisin inconnu ou déjà consulté.');l.heard.push(a.id);}
   else if(a.type==='meal'){before();at('buffet');if(l.meal||!['apport','placard'].includes(a.id))throw Error('Préparation inconnue ou déjà choisie.');if(a.id==='apport')spend({food:3,water:2});l.meal=a.id;}
   else if(a.type==='collect'){before();at(a.id);if(l.meal!=='placard'||!PANTRY.includes(a.id)||l.pantry.includes(a.id))throw Error('Réserve non affectée ou déjà retirée.');l.pantry.push(a.id);}
   else if(a.type==='notice'){before();at('console');if(l.notice)throw Error('Notice déjà lue.');l.notice=true;}
   else if(a.type==='switch'){before();at(a.id);if(!l.notice||l.sound||!own(CONTROL,a.id)||!CONTROL[a.id].includes(a.value))throw Error('Lisez la notice ; réglage inconnu ou déjà sécurisé.');l.controls[a.id]=a.value;}
   else if(a.type==='sound'){
    before();at('console');if(l.sound||!['test','silence','technique'].includes(a.id))throw Error('Méthode inconnue ou sonorisation déjà sécurisée.');
    if(a.id==='silence')l.sound='silence';
    else{if(!l.notice)throw Error('Lisez la notice avant de brancher.');if(a.id==='technique'){if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');spend({circuitry:1});l.controls={source:'micro',sortie:'local',niveau:'limite'};}
     if(!soundReady(l.controls))throw Error('Essai coupé : micro local et limiteur requis. La sirène ne sera pas activée.');l.sound='limitee';}
   }else if(a.type==='start'){
    before();at('josiane');if(l.heard.length!==4||!mealReady(l)||!l.sound||!['commune','paliers'].includes(a.id))throw Error('Quatre invitations, le repas et une sonorisation sûre sont nécessaires.');l.layout=a.id;l.started=true;
   }else if(a.type==='serve'){
    at(a.id);if(!l.started||!GUESTS.includes(a.id)||l.served.includes(a.id))throw Error('Portion absente, voisin inconnu ou déjà servi.');l.served.push(a.id);
   }else if(a.type==='answer'){
    at(a.id);if(!l.started||!own(REPLIES,a.id)||!l.served.includes(a.id)||l.answers[a.id]||!own(REPLIES[a.id],a.value))throw Error('Réponse inconnue, portion non servie ou objection déjà traitée.');
    if(a.id==='karim'&&a.value==='geste'){if(out.player.caps<5)throw Error('5 capsules nécessaires.');out.player.caps-=5;}
    if(a.id==='salome'&&a.value==='excuses'&&(!Number.isFinite(snapshot.character?.special?.C)||snapshot.character.special.C<5))throw Error('Charisme 5 nécessaire ; une reconnaissance factuelle reste possible.');l.answers[a.id]=a.value;
   }else if(a.type==='finish'){
    at('josiane');if(!l.started||l.served.length!==4||!l.answers.karim||!l.answers.salome)throw Error('Servez les quatre voisins et donnez une réponse à Karim et Salomé.');if(out.player.caps>999969)throw Error('Compte de capsules plein.');out.player.caps+=30;l.finished=true;l.outcome=result(l);
   }else throw Error('Action de voisinage inconnue.');
  }
  l.revision++;l.journal.push({type:a.type,id:typeof a.id==='string'?a.id:null,at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});l.journal=l.journal.slice(-48);out.v066Voisins=l;return out;
 }
 return {GUESTS:GUESTS.slice(),PANTRY:PANTRY.slice(),CONTROL:copy(CONTROL),LABELS:copy(LABELS),ENDINGS:copy(ENDINGS),REPLIES:copy(REPLIES),fresh,basis,migrate,mealReady,soundReady,context,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralVoisins;

if(typeof baseState==='function'&&typeof MistralNotaires!=='undefined'){
 const M=MistralVoisins,copy=v=>JSON.parse(JSON.stringify(v)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k),rt={busy:false,error:null};
 const HOME=Object.fromEntries(MistralRadieuse.PEOPLE.map(p=>[p.id,p.pos.slice()]));
 const P={...HOME,buffet:[-1,6.4,-26.3],rations:[-21,0,0],vaisselle:[20,3.2,-3],source:[-21,0,-4],sortie:[20,3.2,-13],niveau:[17,6.4,-30],console:[17,6.4,-25]};
 const SEATS={josiane:[-6.3,6.4,-26.2],karim:[-3.2,6.4,-24],lucie:[.5,6.4,-24],nadia:[4.6,6.4,-26.2],salome:[.5,6.4,-29]};
 const WORDS={karim:'« Quel placard avez-vous ouvert ? Les charges ont déjà été réparties ; je ne veux pas payer une fête cachée dans une facture de pompe. »',lucie:'« Je viens. Mais pas avec la sirène branchée sur la musique. L’étiquette de 2076 n’a pas appris à reconnaître une fête depuis. »',nadia:'« Une portion par voisin, pas une prime à celui qui parle le plus fort. Le repas ne doit pas vider la réserve de soin. »',salome:'« Je veux bien partager le repas. Pas servir de décor à une affiche qui prétendrait que tout a toujours été juste. »'};
 const base=baseState;baseState=function(...a){const s=base(...a);s.v066Voisins=M.fresh();return s;};
 const migrate=migrateState;migrateState=function(raw={}){const s=migrate(raw);s.v066Voisins=M.migrate(raw?.v066Voisins);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v063Radieuse&&state.v042?.activeInterior===MistralRadieuse.SITE.id;
 const ready=()=>!!M.basis(state);
 const during=()=>state.v066Voisins.started&&!state.v066Voisins.finished;
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc géographique sans écriture.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':inCombat?'Terminez le combat.':null;}
 function location(id){return own(HOME,id)?world?.npcs.find(n=>n.id==='r63:'+id)?.pos:P[id];}
 function near(id){const p=location(id);if(!local()||!p)return false;if(own(HOME,id)&&!world.npcs.some(n=>n.id==='r63:'+id&&n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.5&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.85]);}
 function where(type,id){return ['open','start','finish'].includes(type)?'josiane':type==='meal'?'buffet':['notice','sound'].includes(type)?'console':id;}
 function notice(t){V027.message=t;toast(t,'bad');return false;}
 function act(type,id,value,revision){
  if(rt.busy)return false;const owner=state,scene=world,before=copy(owner),point=where(type,id);let next;
  try{next=M.apply(owner,{type,id,value},{local:local(),near:near(point),point,blocked:blocked(),revision});if(type==='start'&&!M.GUESTS.concat('josiane').every(k=>world.npcs.some(n=>n.id==='r63:'+k&&n.alive)))throw Error('Un voisin manque à l’appel. Le service ne démarre pas.');}catch(e){return notice(e.message);}
  rt.busy=true;
  try{owner.v066Voisins=next.v066Voisins;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde de la soirée refusée.');}
  catch(e){if(state===owner){for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}return notice(e.message+' Échange annulé.');}finally{rt.busy=false;}
  try{bind(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();if(type==='sound'&&id!=='silence')audio.tone(440,.10,'sine',.025);toast(type==='finish'?'Soirée terminée · 30 capsules, une seule fois.':type==='start'?'Le service est mis en place. Aucune minuterie cachée.':'Préparation sauvegardée.','good');}catch(e){rt.error=e.message;}return true;
 }
 function guard(fn){const owner=state,scene=world,revision=state.v066Voisins.revision;return()=>state===owner&&world===scene&&revision===state.v066Voisins.revision?fn(revision):notice('Cette conversation est périmée.');}
 const accessible=id=>!blocked()&&ready()&&near(id);
 const back=()=>({text:'Revenir.',onChoose:closeDialogue});
 function responseText(id,l){if(id==='karim')return l.meal==='apport'?'Les trois vivres et deux eaux ont été apportés par le joueur. La réserve festive de l’immeuble reste scellée.':'Le lot festif réservé à cette soirée a été utilisé une fois. Ni l’eau de la pompe ni les réserves de pharmacie n’ont été prélevées.';return M.context(l)+' Une invitation ne transforme pas l’ancien scrutin en vote unanime.';}
 function person(id){
  if(!accessible(id))return notice(blocked()||'Rejoignez ce voisin.');const l=state.v066Voisins,choices=[],p=MistralRadieuse.PEOPLE.find(p=>p.id===id);
  if(id==='josiane'){
   if(!l.opened)choices.push({text:'Préparer « La fête des voisins ».',onChoose:guard(rev=>{act('open',null,null,rev);person(id);})});
   else if(!l.started)for(const [layout,label]of [['commune','Une table commune sur la terrasse'],['paliers','Un service de palier en palier']])choices.push({text:'Prévoir : '+label,onChoose:guard(()=>confirmStart(layout))});
   else if(!l.finished)choices.push({text:'Terminer la soirée · 30 capsules.',onChoose:guard(rev=>{if(act('finish',null,null,rev))closeDialogue();else person(id);})});
  }else if(M.GUESTS.includes(id)&&l.opened){
   if(!l.started&&!l.heard.includes(id))choices.push({text:'Écouter ses conditions et transmettre l’invitation.',onChoose:guard(rev=>{act('listen',id,null,rev);person(id);})});
   if(during()&&!l.served.includes(id))choices.push({text:'Servir sa portion réservée.',onChoose:guard(rev=>{act('serve',id,null,rev);person(id);})});
   if(during()&&l.served.includes(id)&&own(M.REPLIES,id)&&!l.answers[id])for(const [choice,label]of Object.entries(M.REPLIES[id]))choices.push({text:label,onChoose:guard(rev=>{act('answer',id,choice,rev);person(id);})});
  }
  choices.push(back());const answered=own(l.answers,id)&&l.answers[id];
  openDialogue(speaker(p?.name||'Voisin','LA FÊTE DES VOISINS','FV'),(id==='josiane'?'« Nous avons des actes. Voyons si nous savons encore partager une table. Le repas ne promet ni pardon ni unanimité. »':WORDS[id])+'\n\n'+(l.served.includes(id)?'Portion remise. '+(id==='karim'||id==='salome'?responseText(id,l):'Le voisin remercie les cuisiniers sans déclarer les litiges terminés.'):'')+(answered?'\nRéponse conservée : '+M.REPLIES[id][answered]+'.':'')+'\n\n'+M.briefing(l)+(during()?'\nPour les autres dossiers, retrouvons nos postes après le repas.':''),choices);return true;
 }
 function confirmStart(layout){if(!accessible('josiane'))return false;const l=state.v066Voisins;openDialogue(speaker('Josiane Roux','MISE EN PLACE DU SERVICE','FV'),(layout==='commune'?'Les cinq voisins seront disposés autour de la table sur la terrasse.':'Les voisins restent à leur palier ; portez les quatre portions à leurs postes habituels.')+'\nLes préparatifs terminés, chacun rejoint sa place. Vous pourrez vous absenter et reprendre les portions restantes.\n\n'+M.context(l)+'\n\nLes préparatifs deviennent définitifs au début du service.',[{text:'Confirmer la mise en place.',onChoose:guard(rev=>{if(act('start',layout,null,rev))closeDialogue();else person('josiane');})},{text:'Revenir aux préparatifs.',onChoose:guard(()=>person('josiane'))}]);return true;}
 function equipment(id){
  if(!accessible(id)||!state.v066Voisins.opened)return false;const l=state.v066Voisins,choices=[];let text='';
  if(id==='buffet'){
   text='Quatre portions et une table. Choisissez un apport personnel (3 vivres + 2 eaux) ou le petit lot festif de l’immeuble, à récupérer avec la vaisselle. Ce lot est distinct des réserves précédentes.';
   if(!l.meal)for(const [v,label]of [['apport','Fournir 3 vivres et 2 eaux'],['placard','Utiliser le lot festif réservé et la vaisselle']])choices.push({text:label,onChoose:guard(rev=>{act('meal',v,null,rev);equipment(id);})});
   text+='\n\n'+(l.meal?l.meal==='apport'?'Apport retiré de votre inventaire.':'Lot affecté : '+l.pantry.length+'/2 éléments récupérés.':'Aucune réserve choisie.');
  }else if(M.PANTRY.includes(id)){
   text=id==='rations'?'Des boîtes prévues pour cette fête, conservées à part des médicaments et de la réserve d’eau. Elles seront consommées par les quatre portions, pas ajoutées au sac.':'Une caisse de gobelets et de bols lavés. Emportez la caisse vers le buffet ; elle ne produit aucun matériau vendable.';
   if(l.meal==='placard'&&!l.pantry.includes(id)&&!l.started)choices.push({text:'Prendre ce lot pour la soirée.',onChoose:guard(rev=>{act('collect',id,null,rev);equipment(id);})});
  }else if(id==='console'){
   text='L’ancienne sonorisation relie une annonce de 2076 à une ligne de sirène. La notice impose MICRO, LOCAL et LIMITEUR. Les trois sélecteurs sont sur la platine de l’atelier, l’aiguillage de la galerie et le limiteur de terrasse. Un essai erroné est coupé avant l’alarme.';
   if(!l.notice&&!l.started)choices.push({text:'Lire la notice de raccordement.',onChoose:guard(rev=>{act('notice',null,null,rev);equipment(id);})});
   if(!l.sound&&!l.started)for(const [v,label]of [['test','Tester les trois réglages'],['technique','Régler avec Lucie · INT 5 et 1 circuit'],['silence','Débrancher : une fête sans amplification']])choices.push({text:label,onChoose:guard(rev=>{act('sound',v,null,rev);equipment(id);})});
   text+='\n\n'+Object.entries(l.controls).map(([k,v])=>M.LABELS[k]+' : '+M.LABELS[v]).join('\n')+'\n'+(l.sound==='limitee'?'Micro local testé. Aucun jingle d’archive ni alarme ne sera lancé.':l.sound==='silence'?'Amplificateur débranché. La fête reste possible.':'Circuit non validé.');
  }else if(own(M.CONTROL,id)){
   text=M.LABELS[id]+' : '+M.LABELS[l.controls[id]]+'. Le sélecteur garde sa position après sauvegarde.';
   if(l.notice&&!l.sound&&!l.started)for(const v of M.CONTROL[id])choices.push({text:(l.controls[id]===v?'✓ ':'')+'Choisir : '+M.LABELS[v],onChoose:guard(rev=>{act('switch',id,v,rev);equipment(id);})});
   if(!l.notice)text+='\nLisez la notice au pupitre de la terrasse.';
  }
  choices.push(back());openDialogue(speaker(id==='buffet'?'Le buffet des communs':id==='console'?'Sonorisation de 2076':M.LABELS[id]||'Réserve festive','RÉSERVE FINIE · SERVICE LOCAL','FV'),text,choices);return true;
 }
 function unstage(w){if(!w?.v066Homes)return;for(const n of w.npcs){const old=w.v066Homes[n.id];if(old){n.pos=old.pos.slice();n.home=old.home.slice();n.yaw=old.yaw;n.v020Static=old.static;n.activity=old.activity;delete n.v066Staged;}}w.v066Homes=null;}
 function stage(w,active){if(!active){unstage(w);return;}w.v066Homes??={};for(const [id,pos]of Object.entries(SEATS)){const n=w.npcs.find(n=>n.id==='r63:'+id);if(!n||!n.alive)continue;if(!w.v066Homes[n.id])w.v066Homes[n.id]={pos:n.pos.slice(),home:n.home.slice(),yaw:n.yaw,static:n.v020Static,activity:n.activity};n.pos=pos.slice();n.home=pos.slice();n.yaw=Math.atan2(P.buffet[0]-pos[0],pos[2]-P.buffet[2]);n.v020Static=true;n.activity='repas';n.v066Staged=true;}}
 function bind(w){
  if(!w?.v063Radieuse)return;
  if(w.v066Owner!==state){unstage(w);for(const k of ['staticDraws','colliders','interactables'])w[k]=w[k].filter(o=>!o.v066Voisins);w.v066Owner=state;w.v066Installed=false;w.v066Key=null;}
  if(!ready()){unstage(w);if(w.v066Installed){for(const k of ['staticDraws','colliders','interactables'])w[k]=w[k].filter(o=>!o.v066Voisins);w.v066Installed=false;w.v066Key=null;}return;}
  if(!w.v066Installed){
   w.v066Installed=true;
   const box=(p,s,c,solid=false,role=null)=>{const d=addBox(w,p,s,c);d.v066Voisins=true;if(role)d.v066Role=role;if(solid){const col=addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});col.v066Voisins=true;if(role)col.v066Role=role;}return d;};
   const part=(mesh,p,s,c,role)=>{const d=addPart(w,mesh,p,s,c);d.v066Voisins=true;d.v066Role=role;return d;};
   // Keep the two stairs and every prior evidence point free. The table exists only after opening.
   box([-1,7.22,-26.3],[8,.18,1.5],[.56,.37,.20],true,'table');
   for(const x of [-4.5,2.5])for(const z of [-26.8,-25.8])box([x,6.8,z],[.15,.8,.15],[.23,.26,.23],true,'table');
   box([-1,7.32,-26.3],[7.8,.03,1.35],[.80,.72,.49],false,'nappe');
   for(const [index,id]of M.GUESTS.entries()){const x=-3.9+index*1.85;part('cylinder',[x,7.37,-26.25],[.6,.04,.6],[.8,.79,.68],'plate:'+id);part('sphere',[x,7.50,-26.25],[.36,.22,.34],[.59,.38,.17],'food:'+id);part('cylinder',[x+.45,7.51,-26.55],[.18,.30,.18],[.48,.62,.61],'cup:'+id);}
   for(const id of ['rations','vaisselle']){const p=P[id];box([p[0],p[1]+.5,p[2]],[1.15,1,.75],[.34,.30,.22],true);const lid=box([p[0],p[1]+1.02,p[2]],[1.2,.09,.8],[.66,.54,.30],false,'lid:'+id);box([p[0],p[1]+.8,p[2]+.4],[.8,.28,.04],[.71,.69,.52]);}
   for(const id of ['source','sortie','niveau','console']){const p=P[id];box([p[0],p[1]+.6,p[2]],[1.1,1.2,.6],[.25,.31,.31],true);box([p[0],p[1]+1.28,p[2]],[1.2,.15,.8],[.50,.49,.39]);const indicator=box([p[0],p[1]+.95,p[2]+.32],[.40,.2,.04],[.67,.30,.18],false,'control:'+id);part('cylinder',[p[0]+.29,p[1]+1.40,p[2]],[.14,.12,.14],[.63,.62,.49],'knob');}
   // A small speaker and pennants are local authored objects, not architectural survey data.
   box([21,8.0,-31],[.8,2.7,.7],[.20,.25,.26],true);box([21,9.5,-31],[1.7,1.1,.7],[.44,.40,.28]);
   for(const x of [-9,8])box([x,8.0,-30.9],[.08,3.2,.08],[.28,.31,.29],true,'rigging');
   box([-.5,9.72,-30.9],[17.1,.035,.035],[.30,.29,.23],false,'rigging');
   for(let i=0;i<11;i++)box([-8+i*1.5,9.45,-30.9],[.7,.5,.03],[[.61,.31,.22],[.72,.65,.37],[.26,.47,.52]][i%3],false,'bunting');
   if(typeof v021Sign==='function')for(const [id,label]of Object.entries({source:'PLATINE',sortie:'AIGUILLAGE',niveau:'LIMITEUR',console:'PUPITRE',rations:'REPAS',vaisselle:'BOLS'})){const p=P[id],start=w.staticDraws.length;v021Sign(w,p[0],p[1]+1.62,p[2]+.1,label,.055);for(const d of w.staticDraws.slice(start))d.v066Voisins=true;}
   for(const id of [...M.PANTRY,'source','sortie','niveau','console','buffet']){const p=P[id];const it=addInteract(w,'v66:'+id,[p[0],p[1]+1.25,p[2]+.85],id==='buffet'?'Préparer le buffet':id==='console'?'Consulter la sonorisation':M.LABELS[id]?'Régler · '+M.LABELS[id]:'Examiner le lot · '+id,()=>w===world&&w.v066Owner===state&&equipment(id),{kind:'quest',radius:3.5,priority:5,condition:()=>accessible(id)&&state.v066Voisins.opened&&!state.v066Voisins.started});it.v066Voisins=true;}
  }
  const l=state.v066Voisins,key=[l.revision,l.opened,l.started,l.finished].join(':');if(w.v066Key===key)return;w.v066Key=key;
  stage(w,l.started&&!l.finished&&l.layout==='commune');
  for(const d of w.staticDraws){const role=d.v066Role;if(!role)continue;
   if(['table','nappe'].includes(role))d.hidden=!l.opened;
   else if(role==='bunting')d.hidden=!l.started;
   else if(role==='rigging')d.hidden=!l.opened;
   else if(role.startsWith('plate:')||role.startsWith('cup:'))d.hidden=!M.mealReady(l)||l.layout==='paliers';
   else if(role.startsWith('food:'))d.hidden=!M.mealReady(l)||l.layout==='paliers'||l.served.includes(role.split(':')[1]);
   else if(role.startsWith('lid:'))d.hidden=l.pantry.includes(role.split(':')[1]);
   else if(role.startsWith('control:')){const id=role.split(':')[1],okay=l.sound==='silence'||(id==='console'?l.sound==='limitee':l.controls[id]===M.CONTROL[id][1]);d.color=l.sound==='silence'?[.35,.38,.36]:okay?[.30,.61,.41]:[.67,.30,.18];d.emissive=l.sound==='limitee'?.15:0;}
  }
  for(const c of w.colliders)if(['table','rigging'].includes(c.v066Role))c.disabled=!l.opened;
 }
 const build=v042BuildInstance;v042BuildInstance=function(...a){const w=build(...a);bind(w);return w;};
 const draw=collectDraws;collectDraws=function(...a){bind(world);return draw(...a);};
 function topic(call,label,fn){const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text:label,onChoose:guard(fn)},...(ch||[]).slice(-1)],...rest);};try{return call();}finally{openDialogue=old;}}
 const talk=talkToNPC;talkToNPC=function(id){const who=typeof id==='string'&&id.startsWith('r63:')?id.slice(4):null;if(!who||!own(HOME,who)||!ready()||blocked()||!near(who))return talk(...arguments);if(during())return person(who);return topic(()=>talk(...arguments),'Fête des voisins · '+(state.v066Voisins.finished?'le lendemain':'préparer le repas'),()=>person(who));};
 const oldDispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='v66:track'?oldDispatch('r63:track'):oldDispatch(...arguments);};
 V027_SUBS.data.voisins='LA FÊTE DES VOISINS';
 const data=v027Data;v027Data=function(c){if(V027.sub!=='voisins')return data(...arguments);const l=state.v066Voisins,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">LES ASSIETTES NE VOTENT PAS</p><h2>La fête des voisins</h2><p>'+esc(M.briefing(l))+'</p><p>'+esc(M.context(l))+'</p>'+v027Button('Suivre la Cité Radieuse','v66:track')+'<h3>Voisins</h3>'+M.GUESTS.map(id=>'<p>'+esc(MistralRadieuse.PEOPLE.find(p=>p.id===id).name)+' · '+(l.served.includes(id)?'Portion remise':l.heard.includes(id)?'Invitation transmise':'À consulter')+'</p>').join('')+'<h3>Préparatifs</h3><p>Repas : '+esc(l.meal==='apport'?'Apport personnel':l.meal==='placard'?'Lot festif · '+l.pantry.length+'/2 éléments':'À choisir')+'</p><p>Son : '+esc(l.sound==='silence'?'Sans amplification':l.sound==='limitee'?'Micro local limité':'Non sécurisé')+'</p><p>Service : '+esc(l.layout==='commune'?'Table de terrasse':l.layout==='paliers'?'Palier en palier':'À décider')+'</p><h3>Objections</h3>'+['karim','salome'].map(id=>'<p>'+esc(id==='karim'?'Karim':'Salomé')+' : '+esc(l.answers[id]?M.REPLIES[id][l.answers[id]]:'À entendre pendant le repas')+'</p>').join('')+'<p>Aucune minuterie ni réécriture des droits. Les anciens dialogues reprennent à la fin du service.</p></div>';};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v066Voisins;return rows(...arguments).concat(l.opened?[{id:'v66:quest',name:'LA FÊTE DES VOISINS',stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:[['Invitations transmises',l.heard.length===4],['Repas préparé',M.mealReady(l)],['Son sécurisé',!!l.sound],['Quatre portions',l.served.length===4],['Soirée conclue',l.finished]],source:'Copropriété Radieuse',badge:l.finished?'✓':'',hint:'Josiane · Les assiettes ne votent pas'}]:[]);};
 const track=v027Track;v027Track=function(id){return id==='v66:quest'?v027Dispatch('v66:track'):track(...arguments);};
 function next(){const l=state.v066Voisins;if(!l.opened||l.finished)return'josiane';if(!l.started){const guest=M.GUESTS.find(k=>!l.heard.includes(k));if(guest)return guest;if(!l.meal)return'buffet';if(!M.mealReady(l))return M.PANTRY.find(k=>!l.pantry.includes(k));if(!l.sound){if(!l.notice)return'console';return Object.keys(M.CONTROL).find(k=>l.controls[k]!==M.CONTROL[k][1])||'console';}return'josiane';}return M.GUESTS.find(k=>!l.served.includes(k))||['karim','salome'].find(k=>!l.answers[k])||'josiane';}
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local()||!ready())return marker(...arguments);const id=next(),p=location(id);return p?{zone:world.id,pos:[p[0],p[1]+1.25,p[2]+.85],label:own(HOME,id)?MistralRadieuse.PEOPLE.find(p=>p.id===id).name:M.LABELS[id]||'Préparatifs de la fête'}:marker(...arguments);};
 const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local()||!ready())return ui(...arguments);$('questTitle').textContent='LA FÊTE DES VOISINS';$('questObjective').textContent=M.briefing(state.v066Voisins);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='LA FÊTE DES VOISINS';f.querySelector('p').textContent=M.briefing(state.v066Voisins);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.voisins={name:'La fête des voisins — sans unanimité forcée',freq:'96.6',hint:'Un repas ne remplace pas un acte',available:()=>state.v066Voisins.opened,text:()=>M.briefing(state.v066Voisins)};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v066VoisinsInfo:()=>{bind(world);return {ledger:copy(state.v066Voisins),ready:ready(),local:local(),points:copy(Object.fromEntries(Object.keys(P).map(id=>[id,location(id)||P[id]]))),error:rt.error};},v066VoisinsOpen:()=>v027Open('data','voisins'),v066VoisinsAction:act});};
}
