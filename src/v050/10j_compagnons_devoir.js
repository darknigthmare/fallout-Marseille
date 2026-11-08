/* Compagnons du Devoir — original Mistral fiction, not an official Fallout faction.
 * Two existing geographic relays, a bounded workshop and a real shared consumable lot.
 * Quest parts never enter saleable inventory. Earlier political records are read-only. */
const MistralDevoir = (() => {
 'use strict';
 const Parent=typeof MistralVoisins!=='undefined'?MistralVoisins:require('./10i_fete_voisins.js');
 const own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k),copy=o=>JSON.parse(JSON.stringify(o));
 const integer=n=>Number.isSafeInteger(n)&&n>=0&&n<=999999;
 const SITES={aubagne:'v042-huveaune-caravan-02',ciotat:'v042-laciotat-caravan-01'};
 const LESSONS={
  aubagne:{name:'Le calibre d’argile',speaker:'Samira Valette',role:'Céramiste · correspondante des Compagnons',part:'Cartouche témoin',text:'« Une pièce jolie n’est pas une pièce juste. Le calibre témoin doit laisser passer la tige bleue, sans jeu au repère blanc. La rouge est fendue, la verte trop large ; la bleue porte les deux marques. Ce contrôle ne certifie ni une eau potable ni une protection contre les radiations. »',answer:'bleue',choices:{rouge:'Cartouche rouge · fissure au col',verte:'Cartouche verte · jeu au repère',bleue:'Cartouche bleue · marques concordantes'},exchange:{clay:2,cloth:1},technical:{scrap:1}},
  ciotat:{name:'Le clapet des cales',speaker:'Anton Riva',role:'Ajusteur · liaison des chantiers',part:'Clapet de retour',text:'« Nous gardons un petit lot pour apprendre, pas un chantier qui fabrique tout gratuitement. Le clapet du banc doit laisser passer le témoin vers RETOUR et le retenir dans l’autre sens. A est bloqué ; B passe dans les deux sens ; C répond aux deux contrôles. La pression du banc reste limitée. »',answer:'C',choices:{A:'Clapet A · aucun passage',B:'Clapet B · passage dans les deux sens',C:'Clapet C · retour contrôlé'},exchange:{scrap:3,cloth:1},technical:{scrap:1}}
 };
 const PLANS={partage:{name:'Plans partagés',text:'Lucie laisse une copie commentée aux deux relais. Le petit lot commun de trois doses peut être travaillé ici, à Aubagne ou à La Ciotat. Changer de comptoir ne le renouvelle pas.',uses:3},atelier:{name:'Réserve d’atelier',text:'Les Compagnons confient cinq doses à Lucie, qui supervise chaque mélange dans la Cité. Les relais connaissent le résultat, mais ne peuvent pas utiliser cette réserve. La meilleure dotation conserve la dépendance à l’atelier.',uses:5}};
 const STEP_IDS=['bati','cartouche','clapet'];
 function basis(s){const b=Parent.basis(s),v=Parent.migrate(s?.v066Voisins);if(!b||!v.finished||!v.basis||Object.keys(b).some(k=>b[k]!==v.basis[k]))return null;return {...b,repas:v.outcome};}
 function validBasis(b){return !!b&&['lots','occupants'].includes(b.representation)&&['solidarite','usage','avance'].includes(b.charges)&&['audit','syndic'].includes(b.controle)&&['forfait','avenant','entraide'].includes(b.assurance)&&['repertoire','usage','depot'].includes(b.acte)&&['table_ouverte','paliers','treve'].includes(b.repas);}
 function fresh(){return {schema:1,revision:0,opened:false,basis:null,lessons:{aubagne:{read:false,method:null},ciotat:{read:false,method:null}},assembly:[],notice:false,controls:{entree:'fermee',retour:'ouvert'},pressure:0,readback:false,tested:false,testMethod:null,plan:null,remaining:0,produced:0,finished:false,journal:[]};}
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Carnet de métier plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.revision=integer(raw.revision)?raw.revision:0;l.opened=raw.opened===true&&validBasis(raw.basis);
  if(l.opened){
   l.basis=Object.fromEntries(['representation','charges','controle','assurance','acte','repas'].map(k=>[k,raw.basis[k]]));
   for(const id of Object.keys(SITES)){const r=raw.lessons?.[id];l.lessons[id]={read:r?.read===true,method:r?.read===true&&['apprentissage','echange','technique'].includes(r?.method)?r.method:null};}
   if(Array.isArray(raw.assembly)&&raw.assembly.includes('bati'))l.assembly=['bati',...['cartouche','clapet'].filter(id=>raw.assembly.includes(id)&&l.lessons[id==='cartouche'?'aubagne':'ciotat'].method)];
   l.notice=raw.notice===true;
   if(l.assembly.length===3&&l.notice){
    if(['ouverte','fermee'].includes(raw.controls?.entree))l.controls.entree=raw.controls.entree;
    if(['ouvert','ferme'].includes(raw.controls?.retour))l.controls.retour=raw.controls.retour;
    l.pressure=[1,2].includes(raw.pressure)&&l.controls.entree==='ouverte'?raw.pressure:0;
    if(l.pressure===2&&l.controls.retour!=='ferme')l.pressure=0;
    l.readback=l.pressure===2&&raw.readback===true;
    if(raw.tested===true&&['manuel','technique'].includes(raw.testMethod)){l.tested=true;l.testMethod=raw.testMethod;l.pressure=0;l.readback=false;l.controls={entree:'fermee',retour:'ouvert'};}
   }
   if(l.tested&&raw.finished===true&&own(PLANS,raw.plan)){l.finished=true;l.plan=raw.plan;const max=PLANS[l.plan].uses;
    // Preserve scarcity on malformed saves: unknown counters never replenish a used batch.
    l.remaining=integer(raw.remaining)?Math.min(max,raw.remaining):0;
    l.produced=integer(raw.produced)?Math.min(max,raw.produced):max-l.remaining;
    l.remaining=Math.min(l.remaining,max-l.produced);
   }
  }
  const kinds=['open','read','part','assemble','notice','switch','prime','test','readback','finish','produce'];
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&kinds.includes(e.type)).slice(-48).map(e=>({type:e.type,id:typeof e.id==='string'?e.id.slice(0,30):null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];return l;
 }
 function context(raw){const l=migrate(raw),b=l.basis;if(!b)return 'Un ouvrage de métier après le repas, sans réécrire les droits.';return (b.repas==='treve'?'Le repas a laissé une objection ouverte.':'Le repas a permis un échange, pas une unanimité.')+' '+(b.representation==='lots'?'Le toit reste exclu du scrutin historique.':'Le toit avait une voix au scrutin.')+' Les actes et l’assurance restent distincts.';}
 function briefing(raw){const l=migrate(raw);if(!l.opened)return 'Après la fête, parlez à Lucie à l’atelier de la Cité.';if(l.finished)return PLANS[l.plan].text+` Doses restantes : ${l.remaining}.`;if(!l.lessons.aubagne.method||!l.lessons.ciotat.method)return 'Rencontrez les correspondants d’Aubagne Haute et de La Ciotat, dans l’ordre choisi. Chaque pièce se gagne par un essai, un échange ou une expertise.';if(l.assembly.length<3)return `Revenez au banc de Lucie : ${l.assembly.length}/3 éléments montés.`;if(!l.tested)return 'Lisez la notice. Amorcez avec le retour ouvert, fermez le retour, éprouvez et lisez le cadran ; ouvrez enfin le retour pour décharger.';return 'Le banc a passé son épreuve. Choisissez avec Lucie comment transmettre le plan et conserver les doses.';}
 function point(type,id){return ['open','finish'].includes(type)?'lucie':['read','part'].includes(type)?id:type==='assemble'?'montage':type==='switch'?id:type==='produce'?id:'cadran';}
 function apply(snapshot,a={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));const where=point(a.type,a.id);
  if(!ctx.near||ctx.point!==where)throw Error('Rejoignez le bon équipement ou représentant.');
  const relay=['aubagne','ciotat'].includes(where);
  if(relay){if(ctx.site!==SITES[where]||!ctx.contact)throw Error('Le correspondant du relais doit être présent et visible.');}
  else if(!ctx.local)throw Error('Rejoignez l’atelier de la Cité Radieuse.');
  const b=basis(snapshot);if(!b)throw Error('Terminez la fête avant de commencer ce tour de main.');
  if(!Number.isFinite(snapshot.player?.hp)||snapshot.player.hp<=0||!integer(snapshot.player.caps))throw Error('État du personnage invalide.');
  const l=migrate(snapshot.v067Devoir);if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Cette proposition est périmée.');
  if(l.revision===999999)throw Error('Carnet plein.');
  if(l.opened&&Object.keys(b).some(k=>b[k]!==l.basis[k]))throw Error('Le contexte source a changé ; le carnet conservé ne sera pas réécrit.');
  const spend=cost=>{for(const[id,n]of Object.entries(cost)){const v=own(snapshot.inventory,id)?snapshot.inventory[id]:0;if(!integer(v)||v<n)throw Error('Fournitures insuffisantes ou quantité invalide.');}};
  let cost={},reward=0,produce=false;
  if(a.type==='open'){if(l.opened)throw Error('Tour de main déjà ouvert.');l.opened=true;l.basis=b;}
  else{
   if(!l.opened)throw Error('Parlez d’abord à Lucie.');
   if(l.finished&&a.type!=='produce')throw Error('L’ouvrage a déjà été réceptionné.');
   if(a.type==='read'){if(!own(LESSONS,a.id)||l.lessons[a.id].read)throw Error('Leçon inconnue ou déjà lue.');l.lessons[a.id].read=true;}
   else if(a.type==='part'){
    if(!own(LESSONS,a.id)||!l.lessons[a.id].read||l.lessons[a.id].method)throw Error('Lisez la leçon ; la pièce est remise une seule fois.');const q=LESSONS[a.id];
    if(a.value==='apprentissage'){if(a.answer!==q.answer)throw Error('Le témoin ne correspond pas. Relisez les marques ; aucune ressource n’a été consommée.');}
    else if(a.value==='echange')cost=q.exchange;
    else if(a.value==='technique'){if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');cost=q.technical;}
    else throw Error('Méthode inconnue.');spend(cost);l.lessons[a.id].method=a.value;
   }else if(a.type==='assemble'){
    if(!STEP_IDS.includes(a.id)||l.assembly.includes(a.id)||a.id!=='bati'&&!l.assembly.includes('bati'))throw Error('Posez le bâti en premier ; chaque pièce se monte une fois.');
    if(a.id!=='bati'&&!l.lessons[a.id==='cartouche'?'aubagne':'ciotat'].method)throw Error('Rapportez la pièce de son relais.');l.assembly.push(a.id);
   }else if(a.type==='notice'){if(l.notice)throw Error('Notice déjà lue.');l.notice=true;}
   else if(['switch','prime','test','readback'].includes(a.type)){
    if(l.assembly.length!==3||!l.notice||l.tested)throw Error('Montez les trois éléments, lisez la notice ; une épreuve validée reste figée.');
    if(a.type==='switch'){
     if(a.id==='entree'&&['ouverte','fermee'].includes(a.value)){l.controls.entree=a.value;if(a.value==='fermee'){l.pressure=0;l.readback=false;}}
     else if(a.id==='retour'&&['ouvert','ferme'].includes(a.value)){l.controls.retour=a.value;if(a.value==='ouvert'&&l.pressure===2){if(l.readback){l.tested=true;l.testMethod='manuel';l.controls.entree='fermee';}l.pressure=0;l.readback=false;}}
     else throw Error('Réglage inconnu.');
    }else if(a.type==='prime'){if(l.controls.entree!=='ouverte'||l.controls.retour!=='ouvert'||l.pressure!==0)throw Error('Amorçage : entrée ouverte, retour ouvert, cadran au repos.');l.pressure=1;}
    else if(a.type==='test'){
     if(a.value==='technique'){if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');cost={circuitry:1};spend(cost);l.tested=true;l.testMethod='technique';l.pressure=0;l.readback=false;l.controls={entree:'fermee',retour:'ouvert'};}
     else if(a.value==='manuel'){if(l.pressure!==1||l.controls.entree!=='ouverte'||l.controls.retour!=='ferme')throw Error('L’épreuve exige un amorçage, puis le retour fermé.');l.pressure=2;}
     else throw Error('Méthode inconnue.');
    }else{if(l.pressure!==2||l.readback)throw Error('Lisez le cadran pendant l’épreuve, une seule fois.');l.readback=true;}
   }else if(a.type==='finish'){
    if(!l.tested||!own(PLANS,a.id)||snapshot.player.caps>999954)throw Error('Épreuve manquante, transmission inconnue ou compte plein.');l.plan=a.id;l.remaining=PLANS[a.id].uses;l.produced=0;l.finished=true;reward=45;
   }else if(a.type==='produce'){
    if(!l.finished||l.remaining<1||!['lucie','aubagne','ciotat'].includes(a.id))throw Error('Aucune dose disponible.');
    if(l.plan==='atelier'&&a.id!=='lucie')throw Error('Cette réserve reste à l’atelier de Lucie.');
    const held=own(snapshot.inventory,'sealant')?snapshot.inventory.sealant:0;if(!integer(held)||held===999999)throw Error('Stock de mastic invalide ou plein.');
    cost={chemicals:1,cloth:1};spend(cost);l.remaining--;l.produced++;produce=true;
   }else throw Error('Action de métier inconnue.');
  }
  const out=copy(snapshot);out.inventory??={};for(const[id,n]of Object.entries(cost))out.inventory[id]=snapshot.inventory[id]-n;
  out.player.caps+=reward;if(produce)out.inventory.sealant=(snapshot.inventory?.sealant||0)+1;
  l.revision++;l.journal.push({type:a.type,id:typeof a.id==='string'?a.id:null,at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});l.journal=l.journal.slice(-48);out.v067Devoir=l;return out;
 }
 return {SITES:copy(SITES),LESSONS:copy(LESSONS),PLANS:copy(PLANS),STEPS:STEP_IDS.slice(),fresh,migrate,basis,point,context,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralDevoir;

if(typeof baseState==='function'&&typeof MistralVoisins!=='undefined'){
 const M=MistralDevoir,copy=o=>JSON.parse(JSON.stringify(o)),P={lucie:[-15,0,0],montage:[-18,0,3.5],entree:[-20,0,3.5],retour:[-16,0,3.5],cadran:[-18,0,3.5]};
 const rt={busy:false,error:null};
 const base=baseState;baseState=function(...args){const s=base(...args);s.v067Devoir=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(raw);s.v067Devoir=M.migrate(raw?.v067Devoir);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v063Radieuse&&state.v042?.activeInterior===MistralRadieuse.SITE.id;
 const ready=()=>!!M.basis(state);
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc géographique sans écriture de campagne.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':inCombat?'Terminez le combat.':null;}
 function near(id){const p=P[id];if(!local()||!p)return false;if(id==='lucie'&&!world.npcs.some(n=>n.id==='r63:lucie'&&n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7]);}
 function contact(id){const site=M.SITES[id],def=site&&v042Site(site),p=state.player.pos;if(!def?.safe||!v042SiteDiscovered(def)||!world?.v046||!world.geoMacro||state.v042.activeInterior||world.v050CityInterior||!settings.geoFalloutLayer)return false;if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,p))return false;return world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===site&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 function notice(text){V027.message=text;toast(text,'bad');return false;}
 function act(type,id,value,answer,revision){
  if(rt.busy)return false;const owner=state,scene=world,before=copy(owner),where=M.point(type,id),isRelay=Object.prototype.hasOwnProperty.call(M.SITES,where),at=isRelay?contact(where):near(where);let next;
  try{next=M.apply(owner,{type,id,value,answer},{local:local(),near:at,point:where,site:isRelay?M.SITES[where]:null,contact:isRelay&&at,blocked:blocked(),revision});}catch(e){return notice(e.message);}
  rt.busy=true;try{owner.v067Devoir=next.v067Devoir;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde du métier refusée.');}
  catch(e){if(state===owner){for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}return notice(e.message+' Échange annulé.');}finally{rt.busy=false;}
  try{bind(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='finish'?'Ouvrage reçu · 45 capsules.':type==='produce'?'Une dose de mastic préparée.':'Carnet de métier sauvegardé.','good');}catch(e){rt.error=e.message;}return true;
 }
 function guard(fn){const owner=state,scene=world,revision=state.v067Devoir.revision;return()=>state===owner&&world===scene&&revision===state.v067Devoir.revision?fn(revision):notice('Cette conversation est périmée.');}
 const back=()=>({text:'Revenir.',onChoose:closeDialogue}),costs=o=>Object.entries(o).map(([id,n])=>n+' '+itemLabel(id)).join(' + ');
 function production(id){return {text:'Préparer un mastic · 1 produit chimique + 1 tissu · '+state.v067Devoir.remaining+' doses restantes',onChoose:guard(rev=>{act('produce',id,null,null,rev);id==='lucie'?lucie():relay(id);})};}
 function confirm(plan){if(!ready()||blocked()||!near('lucie'))return false;openDialogue(speaker('Lucie Armand','COMPAGNONS DU DEVOIR','LA'),M.PLANS[plan].name+'\n\n'+M.PLANS[plan].text+'\n\nChaque dose transforme 1 produit chimique et 1 tissu en 1 mastic d’étanchéité. Le stock est commun aux comptoirs autorisés, limité et sauvegardé. 45 capsules à réception, une fois. Aucun traitement de l’eau, radiation ou infection.\n\n'+M.context(state.v067Devoir),[{text:'Confirmer la transmission.',onChoose:guard(rev=>{act('finish',plan,null,null,rev);lucie();})},{text:'Revenir aux choix.',onChoose:guard(lucie)}]);return true;}
 function lucie(){
  if(!ready()||blocked()||!near('lucie'))return false;const l=state.v067Devoir,ch=[];
  if(!l.opened)ch.push({text:'Commencer « L’ouvrage et la transmission ».',onChoose:guard(rev=>{act('open',null,null,null,rev);lucie();})});
  if(l.tested&&!l.finished)for(const[id,p]of Object.entries(M.PLANS))ch.push({text:'Examiner : '+p.name,onChoose:guard(()=>confirm(id))});
  if(l.finished&&l.remaining)ch.push(production('lucie'));ch.push(back());
  openDialogue(speaker('Lucie Armand','ATELIER · COMPAGNONS DU DEVOIR','LA'),(!l.opened?'« Après le repas, il reste un métier à transmettre. Aubagne garde les calibres d’argile ; La Ciotat connaît les clapets. Je fournis un bâti de démonstration. Rapporte les deux pièces, monte-les et fais l’épreuve. Ce n’est ni une pompe miraculeuse ni une admission automatique chez les Compagnons. »\n\n':'')+M.briefing(l)+'\n\n'+M.context(l),ch);return true;
 }
 function relay(id){
  if(!ready()||blocked()||!contact(id)||!state.v067Devoir.opened)return false;const l=state.v067Devoir,q=M.LESSONS[id],r=l.lessons[id],ch=[];
  if(!r.read)ch.push({text:'Écouter la leçon et lire les marques.',onChoose:guard(rev=>{act('read',id,null,null,rev);relay(id);})});
  else if(!r.method){for(const[value,label]of Object.entries(q.choices))ch.push({text:'Essai : '+label,onChoose:guard(rev=>{act('part',id,'apprentissage',value,rev);relay(id);})});ch.push({text:'Échanger les fournitures · '+costs(q.exchange),onChoose:guard(rev=>{act('part',id,'echange',null,rev);relay(id);})},{text:'Expertise technique · INT 5 · '+costs(q.technical),onChoose:guard(rev=>{act('part',id,'technique',null,rev);relay(id);})});}
  if(l.finished&&l.plan==='partage'&&l.remaining)ch.push(production(id));ch.push(back());
  const status=r.method?'Pièce protégée dans le carnet, non vendable. Méthode : '+r.method+'.':'Une seule pièce pédagogique est réservée. L’essai ne consomme rien.';
  openDialogue(speaker(q.speaker,q.role.toUpperCase(),'CD'),(r.read?q.text:'« Un voyage compte si tu emportes un geste, pas seulement une caisse. Lis les marques ; ce lot ne se renouvellera pas. »')+'\n\n'+status+(l.finished?'\n\n'+M.PLANS[l.plan].text:''),ch);return true;
 }
 function equipment(id){
  if(!ready()||blocked()||!near(id)||!state.v067Devoir.opened)return false;const l=state.v067Devoir,ch=[];
  if(id==='montage')for(const step of M.STEPS)if(!l.assembly.includes(step))ch.push({text:'Monter : '+({bati:'bâti prêté par Lucie',cartouche:'cartouche témoin d’Aubagne',clapet:'clapet de La Ciotat'}[step]),onChoose:guard(rev=>{act('assemble',step,null,null,rev);equipment(id);})});
  if(id==='entree'||id==='retour'){if(!l.tested)for(const value of id==='entree'?['ouverte','fermee']:['ouvert','ferme'])ch.push({text:(l.controls[id]===value?'✓ ':'')+id+' : '+value,onChoose:guard(rev=>{act('switch',id,value,null,rev);equipment(id);})});}
  else if(id==='cadran'){
   if(!l.notice)ch.push({text:'Lire la notice du banc.',onChoose:guard(rev=>{act('notice',null,null,null,rev);equipment(id);})});
   if(l.notice&&!l.tested)ch.push({text:'Amorcer le circuit de démonstration.',onChoose:guard(rev=>{act('prime',null,null,null,rev);equipment(id);})},{text:'Éprouver à charge limitée.',onChoose:guard(rev=>{act('test',null,'manuel',null,rev);equipment(id);})},{text:'Relever la graduation témoin.',onChoose:guard(rev=>{act('readback',null,null,null,rev);equipment(id);})},{text:'Contrôle technique · INT 5 + 1 circuit.',onChoose:guard(rev=>{act('test',null,'technique',null,rev);equipment(id);})});
  }
  ch.push(back());openDialogue(speaker({montage:'Banc des trois métiers',entree:'Alimentation du banc',retour:'Soupape de retour',cadran:'Cadran d’épreuve'}[id],'OUVRAGE LIMITÉ · AUCUNE EAU PRODUITE','CD'),`Montage : ${l.assembly.length}/3 · cadran : ${l.pressure}/2 · ${l.tested?'épreuve validée':l.readback?'lecture conservée, ouvrez le retour':'épreuve à réaliser'}.\n\n`+(l.notice?'Notice : entrée ouverte et retour ouvert, amorcer. Fermer le retour, éprouver, relever le cadran. Ouvrir le retour : la sécurité ferme l’alimentation. Aucun essai raté n’explose ou ne consomme de stock.':'La notice reste au cadran.')+'\n\n'+M.briefing(l),ch);return true;
 }
 function bind(w){
  if(!w?.v063Radieuse)return;
  if(w.v067Owner!==state){for(const k of ['staticDraws','colliders','interactables'])w[k]=w[k].filter(o=>!o.v067Devoir);w.v067Owner=state;w.v067Installed=false;w.v067Key=null;}
  if(!ready()){if(w.v067Installed){for(const k of ['staticDraws','colliders','interactables'])w[k]=w[k].filter(o=>!o.v067Devoir);w.v067Installed=false;w.v067Key=null;}return;}
  if(!w.v067Installed){w.v067Installed=true;
   const box=(p,s,c,role,solid=false)=>{const d=addBox(w,p,s,c);d.v067Devoir=true;d.v067Role=role;if(solid){const col=addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});col.v067Devoir=true;}return d;};
   box([-18,.76,3.5],[4.7,.18,1.1],[.42,.32,.21],'table',true);for(const x of [-20,-16])for(const z of [3.1,3.9])box([x,.36,z],[.14,.72,.14],[.27,.30,.28],'table',true);
   box([-18,1.01,3.45],[2.8,.28,.70],[.34,.39,.36],'bati');
   box([-18.6,1.40,3.45],[.48,.62,.48],[.70,.58,.41],'cartouche');
   box([-17.3,1.30,3.45],[.65,.40,.48],[.42,.53,.50],'clapet');
   box([-18,1.28,3.45],[.9,.12,.13],[.47,.39,.24],'tube');
   for(const [id,x]of [['entree',-20],['retour',-16]]){box([x,1.04,3.5],[.55,.45,.5],[.27,.34,.32],'control');box([x,1.30,3.5],[.65,.10,.12],[.67,.30,.20],id);}
   box([-18,1.68,3.45],[.6,.50,.16],[.75,.72,.55],'gauge');box([-18,1.68,3.56],[.08,.35,.035],[.20,.25,.23],'needle');
   box([-18,.89,3.95],[.75,.03,.19],[.58,.41,.23],'notice');
   for(const [i,id]of ['aubagne','ciotat'].entries())box([-19+i*2,.91,3.9],[.35,.07,.18],[.71,.67,.50],'plan:'+id);
   const start=w.staticDraws.length;if(typeof v021Sign==='function')v021Sign(w,-18,2.10,3.5,'DEVOIR',.05);for(const d of w.staticDraws.slice(start))d.v067Devoir=true;
   for(const id of ['montage','entree','retour','cadran']){const p=P[id];const it=addInteract(w,'d67:'+id,[p[0],p[1]+(id==='cadran'?1.75:1.1),p[2]+(id==='montage'?1.05:.7)],{montage:'Assembler le banc des trois métiers',entree:'Régler l’alimentation',retour:'Régler le retour',cadran:'Consulter le cadran et sa notice'}[id],()=>w===world&&w.v067Owner===state&&equipment(id),{radius:3,kind:'quest',priority:id==='montage'?5:6,condition:()=>ready()&&!blocked()&&near(id)&&state.v067Devoir.opened&&(id!=='montage'||state.v067Devoir.assembly.length<3)&&(id!=='cadran'||state.v067Devoir.assembly.length===3)});it.v067Devoir=true;}
  }
  const l=state.v067Devoir,key=[l.revision,l.opened].join(':');if(w.v067Key===key)return;w.v067Key=key;
  for(const d of w.staticDraws){const r=d.v067Role;if(M.STEPS.includes(r))d.hidden=!l.assembly.includes(r);if(r==='tube')d.hidden=l.assembly.length!==3;if(r==='entree'||r==='retour')d.color=l.controls[r]===(r==='entree'?'ouverte':'ouvert')?[.27,.60,.40]:[.67,.30,.20];if(r==='needle')d.pos[0]=-18+[-.18,0,.18][l.pressure];if(r==='gauge')d.color=l.tested?[.45,.72,.52]:[.75,.72,.55];if(r?.startsWith('plan:'))d.hidden=!l.finished||l.plan!=='partage';}
 }
 const build=v042BuildInstance;v042BuildInstance=function(...args){const w=build(...args);bind(w);return w;};
 const draw=collectDraws;collectDraws=function(...args){bind(world);return draw(...args);};
 function topic(call,text,fn){const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text,onChoose:guard(fn)},...(ch||[]).slice(-1)],...rest);};try{return call();}finally{openDialogue=old;}}
 const talk=talkToNPC;talkToNPC=function(id){return id==='r63:lucie'&&ready()&&!blocked()&&near('lucie')?topic(()=>talk(...arguments),'Compagnons du Devoir · le tour de main',lucie):talk(...arguments);};
 const relayTalk=v042TalkNPC;v042TalkNPC=function(id){const site=V042_RUNTIME.npcData.get(id)?.siteId,who=Object.keys(M.SITES).find(k=>M.SITES[k]===site);return who&&ready()&&state.v067Devoir.opened&&!blocked()&&contact(who)?topic(()=>relayTalk(...arguments),'Compagnons du Devoir · '+M.LESSONS[who].name,()=>relay(who)):relayTalk(...arguments);};
 function track(id){const site=Object.prototype.hasOwnProperty.call(M.SITES,id)?M.SITES[id]:id==='cite'?MistralRadieuse.SITE.id:null;if(!site||!ready()||blocked()||!v042Site(site))return false;const owner=state,scene=world,before=copy(owner);owner.v042.tracked=site;try{if(state!==owner||world!==scene||saveGame(false)===false)throw Error();}catch{if(state===owner){for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}return notice('Repère non sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
 V027_SUBS.data.devoir='COMPAGNONS DU DEVOIR';const data=v027Data;v027Data=function(c){if(V027.sub!=='devoir')return data(...arguments);const l=state.v067Devoir,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">L’OUVRAGE ET LA TRANSMISSION</p><h2>Compagnons du Devoir</h2><p>'+esc(M.briefing(l))+'</p><p>'+esc(M.context(l))+'</p>'+Object.entries(M.LESSONS).map(([id,q])=>'<section class="v046-notice"><h3>'+esc(q.name)+'</h3><p>'+esc(v042Site(M.SITES[id])?.name||M.SITES[id])+'</p><p>'+esc(l.lessons[id].method?'Pièce obtenue · '+l.lessons[id].method:l.lessons[id].read?'Leçon lue · choisir la pièce':'À rencontrer')+'</p>'+v027Button('Suivre ce relais','d67:track',id,!l.opened)+'</section>').join('')+v027Button('Retourner à la Cité','d67:track','cite',!ready())+'<h3>Banc</h3><p>'+l.assembly.length+'/3 éléments · '+esc(l.tested?'Épreuve validée':l.pressure+'/2 au cadran')+'</p><h3>Transmission</h3><p>'+esc(l.plan?M.PLANS[l.plan].text:'À décider avec Lucie après l’épreuve.')+'</p><p>Doses communes restantes : '+l.remaining+'. Une préparation coûte 1 produit chimique + 1 tissu pour 1 mastic. Aucun traitement médical ou de l’eau.</p></div>';};
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='d67:track'?v027CanAct()&&track(arg):dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v067Devoir;return rows(...arguments).concat(l.opened?[{id:'d67:quest',name:'L’OUVRAGE ET LA TRANSMISSION',stage:l.finished?'done':'active',active:!l.finished,text:M.briefing(l),zone:null,steps:[['Calibre d’Aubagne',!!l.lessons.aubagne.method],['Clapet de La Ciotat',!!l.lessons.ciotat.method],['Banc monté',l.assembly.length===3],['Épreuve déchargée',l.tested],['Transmission décidée',l.finished]],source:'Compagnons du Devoir',badge:l.finished?'✓':'',hint:'Lucie · Aubagne Haute · La Ciotat'}]:[]);};
 const oldTrack=v027Track;v027Track=function(id){if(id!=='d67:quest')return oldTrack(...arguments);const l=state.v067Devoir;return track(!l.lessons.aubagne.method?'aubagne':!l.lessons.ciotat.method?'ciotat':'cite');};
 const oldMarker=getObjectiveMarker;getObjectiveMarker=function(){const l=state.v067Devoir;if(!ready()||!local()||l.finished)return oldMarker(...arguments);let id=!l.opened?'lucie':l.assembly.length<3?'montage':!l.tested?'cadran':'lucie';if(l.opened&&(!l.lessons.aubagne.method||!l.lessons.ciotat.method))return {zone:world.id,pos:[0,1.25,28],label:'Sortir vers '+(!l.lessons.aubagne.method?'Aubagne Haute':'La Ciotat')};const p=P[id];return {zone:world.id,pos:[p[0],p[1]+1.25,p[2]+.7],label:'Compagnons · '+id};};
 const ui=updateQuestUI;updateQuestUI=function(flash=false){const l=state.v067Devoir;if(!ready()||!local()||l.finished)return ui(...arguments);$('questTitle').textContent='L’OUVRAGE ET LA TRANSMISSION';$('questObjective').textContent=M.briefing(l);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='L’OUVRAGE ET LA TRANSMISSION';f.querySelector('p').textContent=M.briefing(l);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.devoir={name:'Compagnons — un geste qui se transmet',freq:'97.6',hint:'Une signature ne remplace pas un essai',available:()=>state.v067Devoir.opened,text:()=>M.briefing(state.v067Devoir)};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v067DevoirInfo:()=>{bind(world);return {ledger:copy(state.v067Devoir),points:copy(P),ready:ready(),local:local(),contacts:Object.fromEntries(Object.keys(M.SITES).map(id=>[id,contact(id)])),error:rt.error};},v067DevoirOpen:()=>v027Open('data','devoir'),v067DevoirAction:act});};
}
