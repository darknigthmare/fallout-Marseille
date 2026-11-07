/* Poste Restante — authored post-ratification overlay. No surveyed feature,
   historical ending, old quest or unlimited regional resource is overwritten. */
const MistralPoste=(()=>{
 'use strict';
 const copy=v=>JSON.parse(JSON.stringify(v)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const PATHS=['charte_vivants','republique_services','continuite','federation','travailleurs','levant','technocratie','fragmentation'];
 const HOME='v042-huveaune-caravan-02';
 const LETTERS=[
  {id:'identite',name:'Le nom sous la rature',site:HOME,clause:'preuve',evidence:'Une habitante figure sur le reçu de naissance, mais pas sur la copie du registre. Elle demande que son nom ne passe pas à la radio.',a:'Faire reconnaître la présence devant témoins',b:'Déposer les deux versions sous scellés',costA:{cloth:1},costB:{circuitry:1},giftA:{water:2},giftB:{scrap:2},textA:'Les témoins signent une présence provisoire. Le bulletin ne publie aucun nom personnel.',textB:'Les versions sont conservées séparément. Le relais ouvre un recours, sans effacer la première preuve.'},
  {id:'eau',name:'La fontaine ne lit pas',site:'v042-marseille-settlement-02',clause:'minimum',evidence:'La table de Longchamp attend trois voyageurs. Son eau est comptée, mais le guichet exige encore une carte délivrée dans le quartier.',a:'Avancer une réserve aux voyageurs',b:'Conserver une réserve commune sous double reçu',costA:{water:3},costB:{scrap:2,cloth:1},giftA:{food:2},giftB:{water:2},textA:'Trois eaux sont remises sans attendre les cartes. Il ne s’agit pas d’une remise en marche de la fontaine.',textB:'Les récipients passent sous deux signatures. La réserve demeure finie et son partage reste contestable.'},
  {id:'sante',name:'La dette ne se transmet pas',site:'v042-marseille-caravan-01',clause:'minimum',evidence:'Une trousse est retenue à cause d’une dette attachée à une famille, et non au blessé. La soignante demande une décision traçable.',a:'Fournir la trousse immédiatement',b:'Financer la garde et inscrire le recours',costA:{antibiotics:1,cloth:2},costB:{food:2,water:2},giftA:{stimpak:1},giftB:{antibiotics:1},textA:'La trousse est remise avant le contrôle du dossier. Le reçu refuse la transmission de la dette.',textB:'La garde reçoit les fournitures. Le recours est conservé séparément du dossier médical du blessé.'},
  {id:'transport',name:'Un billet pour les absents',site:'v042-marseille-caravan-02',clause:'controle',evidence:'L’Horloge compte toujours un voyageur absent. Le relais demande si la copie de l’horaire doit valoir davantage que les personnes présentes.',a:'Équiper la halte des voyageurs',b:'Conserver un horaire contradictoire',costA:{food:2,water:1},costB:{circuitry:1,scrap:2},giftA:{cloth:2},giftB:{weaponParts:1},textA:'La halte reçoit sa réserve. Aucun train ni trajet supplémentaire n’est annoncé.',textB:'Un horaire annoté reste au relais. Le courrier prouve une contestation, pas la réparation d’une ligne.'},
  {id:'energie',name:'Le compteur et la colline',site:'v042-huveaune-caravan-01',clause:'controle',evidence:'Deux relevés donnent des seuils différents pour la même colline. Le Commissariat exige une contre-mesure avant tout nouvel ordre.',a:'Confier les instruments aux habitants',b:'Équiper le retrait volontaire des équipes',costA:{circuitry:2,scrap:1},costB:{water:2,cloth:2},giftA:{scrap:3},giftB:{antibiotics:1},textA:'Le relais reçoit des composants pour comparer les relevés. La dose réelle de la carte ne change pas.',textB:'L’eau et les tissus sont affectés au retrait des équipes. Aucune évacuation régionale n’est simulée.'},
  {id:'communication',name:'Un silence de sept secondes',site:'v042-garlaban-caravan-01',clause:'preuve',evidence:'Canal 13 a reçu une alerte sans origine vérifiable. Une famille redoute que son adresse soit diffusée avec le démenti.',a:'Diffuser un démenti sans noms',b:'Conserver le signal et son contre-témoignage',costA:{circuitry:1},costB:{cloth:1,scrap:1},giftA:{food:2},giftB:{water:2},textA:'Le bulletin signale l’incertitude et retire les adresses privées. La radio ne désigne aucun suspect.',textB:'Le relais garde les deux messages sous des références distinctes. Le doute n’est pas présenté comme une preuve.'},
  {id:'approvisionnement',name:'Le quai sans propriétaire',site:'v042-laciotat-caravan-01',clause:'force',evidence:'Un équipage de secours reçoit un ordre de saisie avant même le débarquement. Les dockers réclament un reçu partagé avec les naufragés.',a:'Avancer les vivres avant la saisie',b:'Garantir un manifeste à double garde',costA:{food:3,water:2},costB:{scrap:2,circuitry:1},giftA:{stimpak:1},giftB:{weaponParts:1},textA:'Les vivres sont remis au relais de secours avant l’examen du pavillon. Aucun navire n’est créé.',textB:'L’équipage et les dockers conservent chacun le manifeste. Le reçu ne transfère pas le port à l’Amirauté.'}
 ];
 const IDS=LETTERS.map(q=>q.id),TYPES=['accept','inspect','deliver','claim','finish'];
 function fresh(){return{schema:1,charter:null,accepted:false,finished:false,letters:Object.fromEntries(IDS.map(id=>[id,{read:false,choice:null,claimed:false}])),journal:[]};}
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Version du registre postal plus récente que ce programme.');
  const out=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return out;
  out.charter=PATHS.includes(raw.charter)?raw.charter:null;out.accepted=raw.accepted===true&&!!out.charter;
  for(const id of IDS){const r=own(raw.letters,id)?raw.letters[id]:null;if(!r||!out.accepted)continue;const choice=['a','b'].includes(r.choice)?r.choice:null;out.letters[id]={read:r.read===true||!!choice,choice,claimed:!!choice&&r.claimed===true};}
  out.finished=out.accepted&&raw.finished===true&&IDS.every(id=>out.letters[id].choice);
  out.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&TYPES.includes(e.type)&&(!e.id||IDS.includes(e.id))).slice(-32).map(e=>({type:e.type,id:IDS.includes(e.id)?e.id:null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];
  return out;
 }
 function unlocked(c){return c?.status==='ratified'&&PATHS.includes(c.charter);}
 function policy(q,c){const x=c?.clauses||{};return q.clause==='preuve'?(x.preuve==='pluralite'?'La présence doit pouvoir être attestée par plusieurs preuves.':x.preuve==='local'?'Le relais territorial conserve son droit de témoignage.':'Le registre régional doit conserver un recours.'):q.clause==='minimum'?(x.minimum==='universel'?'Le minimum vital précède le dossier.':x.minimum==='territorial'?'Le quota local doit être publié et contestable.':'La contribution doit être connue ; la dette familiale reste contestée.'):q.clause==='controle'?(x.controle==='veto'?'Les équipes peuvent suspendre un ordre dangereux.':x.controle==='audit'?'La décision doit rester vérifiable et contestable.':'L’ordre critique doit être limité et consigné.'):x.force==='sans_armee'?'Le service ne dispose pas de sa propre armée.':x.force==='gardes_locales'?'Les gardes locales doivent se prêter assistance.':'La force régionale doit rendre compte de ses saisies.';}
 function apply(snapshot,action={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));
  if(!unlocked(snapshot?.v060Council))throw Error('Une ratification régionale est nécessaire.');
  const out=copy(snapshot),ledger=migrate(out.v061Poste),c=out.v060Council,p=out.player;
  if(!p||!Number.isFinite(p.hp)||p.hp<=0)throw Error('La tournée exige une partie active.');
  if(ledger.charter&&ledger.charter!==c.charter)throw Error('Le reçu postal appartient à une autre ratification.');
  const q=LETTERS.find(q=>q.id===action.id),r=q&&ledger.letters[q.id];out.inventory??={};
  const transfer=(items,sign)=>{for(const[id,n]of Object.entries(items)){const old=out.inventory[id]??0;if(!Number.isInteger(old)||old<0||old>999999||old+sign*n<0||old+sign*n>999999)throw Error('Fournitures insuffisantes ou inventaire invalide.');}for(const[id,n]of Object.entries(items))out.inventory[id]=(out.inventory[id]??0)+sign*n;};
  if(action.type==='accept'){
   if(!ctx.contact||!LETTERS.some(q=>q.site===ctx.site))throw Error('Rencontrez un relais de Poste Restante.');
   if(ledger.accepted)throw Error('La tournée est déjà ouverte.');ledger.accepted=true;ledger.charter=c.charter;
  }else{
   if(!ledger.accepted)throw Error('Acceptez la tournée auprès d’un relais.');
   if(action.type==='finish'){
    if(!ctx.contact||ctx.site!==HOME)throw Error('Rapportez les sept reçus au relais d’Aubagne Haute.');
    if(ledger.finished||!IDS.every(id=>ledger.letters[id].choice))throw Error('La tournée est incomplète ou déjà soldée.');
    if(!Number.isInteger(p.caps)||p.caps<0||p.caps>9999904)throw Error('Compte de capsules invalide.');p.caps+=95;ledger.finished=true;
   }else{
    if(!q||ctx.site!==q.site)throw Error('Ce courrier appartient à un autre relais.');
    if(action.type==='inspect'){
     if(!ctx.physical&&!(ctx.counter&&ctx.contact))throw Error('Examinez le pupitre sur place.');if(r.read)throw Error('Réclamation déjà examinée.');r.read=true;
    }else if(action.type==='deliver'){
     if(!ctx.contact)throw Error('Le représentant doit être présent.');if(!r.read||r.choice)throw Error('Examinez la réclamation, ou conservez la décision déjà prise.');
     if(!['a','b'].includes(action.choice))throw Error('Décision inconnue.');transfer(action.choice==='a'?q.costA:q.costB,-1);r.choice=action.choice;
    }else if(action.type==='claim'){
     if((!ctx.physical&&!(ctx.counter&&ctx.contact))||!r.choice||r.claimed)throw Error('Contre-don absent, éloigné ou déjà pris.');transfer(r.choice==='a'?q.giftA:q.giftB,1);r.claimed=true;
    }else throw Error('Action postale inconnue.');
   }
  }
  ledger.journal.push({type:action.type,id:q?.id||null,at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});ledger.journal=ledger.journal.slice(-32);out.v061Poste=ledger;return out;
 }
 function bulletin(raw){const l=migrate(raw);if(!l.accepted)return'Poste Restante — les exemplaires attendent leurs porteurs. Une charte signée ne remplace pas une lettre livrée.';const n=IDS.filter(id=>l.letters[id].choice).length;return l.finished?'Poste Restante — sept reçus rapportés. Les réclamations restent consultables ; aucune archive personnelle n’a été diffusée.':`Poste Restante — ${n}/7 copies remises. `+LETTERS.filter(q=>l.letters[q.id].choice).map(q=>q.name+' : '+(l.letters[q.id].choice==='a'?q.textA:q.textB)).join(' ');}
 return{HOME,IDS:IDS.slice(),PATHS:PATHS.slice(),catalog:()=>copy(LETTERS),fresh,migrate,unlocked,policy,apply,bulletin};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralPoste;

if(typeof baseState==='function'&&typeof MistralCouncil!=='undefined'){
 const M=MistralPoste,copy=v=>JSON.parse(JSON.stringify(v)),letters=M.catalog();
 const base=baseState;baseState=function(...args){const s=base(...args);s.v061Poste=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(raw);s.v061Poste=M.migrate(raw?.v061Poste);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const rt={owner:null,signature:'',draws:[],entries:[],busy:false,error:null};
 const unlocked=()=>M.unlocked(state.v060Council);
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Le banc synthétique ne modifie pas la tournée.':zoneTransitioning||V046.busy||V047.pending?'Le territoire est en cours de chargement.':!world?.v046||state.v042?.activeInterior||world.v050CityInterior?'Rejoignez un relais du territoire extérieur.':!settings.geoFalloutLayer?'La couche de rencontres territoriales est désactivée.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,state.player.pos)?'Éloignez le danger avant cet échange.':null;}
 function contact(site){const p=state.player.pos,definition=v042Site(site);if(!definition||!v042SiteDiscovered(definition))return false;return (world?.npcs||[]).some(n=>n.alive!==false&&(n.v042Site===site||V042_RUNTIME.npcData.get(n.id)?.siteId===site)&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 function physical(id){const e=rt.entries.find(e=>e.q.id===id),p=state.player.pos;return !!(e&&rt.owner===world&&e.state===state&&Math.hypot(e.pos[0]-p[0],e.pos[2]-p[2])<=3&&Math.abs(e.pos[1]+1-p[1])<2.2&&lineOfSight(p,[e.pos[0],e.pos[1]+1,e.pos[2]+.55]));}
 function notice(text){V027.message=text;toast(text,'bad');return false;}
 function transact(type,id,choice,site){
  if(rt.busy)return false;const owner=state,before=copy(owner);let next;
  try{next=M.apply(owner,{type,id,choice},{blocked:blocked(),site,contact:contact(site),physical:physical(id),counter:!rt.entries.some(e=>e.q.id===id)});}catch(e){return notice(e.message);}
  rt.busy=true;
  try{owner.v061Poste=next.v061Poste;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||saveGame(false)===false)throw Error('Sauvegarde postale refusée.');}
  catch(e){if(state===owner){for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}return notice(e.message+' Échange annulé.');}
  finally{rt.busy=false;}
  rt.signature='';try{bind();updateQuestUI(true);if(mode==='PIP')renderPipboy();toast(type==='finish'?'Tournée soldée · 95 capsules.':type==='claim'?'Contre-don récupéré une seule fois.':'Reçu postal sauvegardé.','good');}catch(e){rt.error='Présentation après sauvegarde : '+e.message;}
  return true;
 }
 function costs(v){return Object.entries(v).map(([id,n])=>n+' '+itemLabel(id)).join(' + ');}
 function dialogue(q){
  if(blocked()||!contact(q.site))return notice(blocked()||'Le relais est trop éloigné.');
  bind();const owner=state,w=world,l=state.v061Poste,r=l.letters[q.id],safe=fn=>()=>{if(state!==owner||world!==w)return false;return fn();},choices=[];
  if(!l.accepted)choices.push({text:'Accepter la tournée des sept réseaux.',onChoose:safe(()=>{transact('accept',q.id,null,q.site);dialogue(q);})});
  else if(!r.read)choices.push(rt.entries.some(e=>e.q.id===q.id)?{text:'Où lire la réclamation ?',onChoose:safe(()=>{toast('Examinez le pupitre postal jaune près de ce relais.');closeDialogue();})}:{text:'Lire la réclamation conservée au comptoir.',onChoose:safe(()=>{transact('inspect',q.id,null,q.site);dialogue(q);})});
  else if(!r.choice)for(const k of ['a','b'])choices.push({text:(k==='a'?q.a:q.b)+' · '+costs(k==='a'?q.costA:q.costB),onChoose:safe(()=>{transact('deliver',q.id,k,q.site);dialogue(q);})});
  if(r.choice&&!r.claimed&&!rt.entries.some(e=>e.q.id===q.id))choices.push({text:'Recevoir le contre-don au comptoir.',onChoose:safe(()=>{transact('claim',q.id,null,q.site);dialogue(q);})});
  if(l.accepted&&!l.finished&&q.site===M.HOME&&M.IDS.every(id=>l.letters[id].choice))choices.push({text:'Rapporter les sept reçus · 95 capsules.',onChoose:safe(()=>{transact('finish',null,null,q.site);dialogue(q);})});
  choices.push({text:'Revenir.',onChoose:closeDialogue});
  openDialogue(speaker('Poste Restante','RELAIS DES SEPT RÉSEAUX','PR'),q.name+' — '+M.policy(q,state.v060Council)+'\n\n'+(!l.accepted?'Camille Diop a confié sept plis au réseau des facteurs. Chaque relais garde un exemplaire et rend un reçu.':r.choice?(r.choice==='a'?q.textA:q.textB):q.evidence),choices);return true;
 }
 // Preserve all ordinary NPC choices; only add a postal topic while that relay speaks.
 const oldTalk=v042TalkNPC;v042TalkNPC=function(id){const site=V042_RUNTIME.npcData.get(id)?.siteId,q=letters.find(q=>q.site===site);if(!q||!unlocked()||blocked()||!contact(site))return oldTalk(...arguments);const previous=openDialogue,owner=state,w=world;openDialogue=function(s,text,choices,...rest){const extra={text:'Poste Restante · '+q.name,onChoose:()=>state===owner&&world===w&&dialogue(q)};return previous(s,text,[...(choices||[]).slice(0,-1),extra,...(choices||[]).slice(-1)],...rest);};try{return oldTalk(...arguments);}finally{openDialogue=previous;}};
 function ground(x,z){if(typeof v050TravelGround!=='function')return null;return v050TravelGround({records:world.v046Records,bank:world.v047TerrainBank||V046.terrain,geoColliders:(world.colliders||[]).filter(c=>c.v046Tile),v050GameplayColliders:(world.colliders||[]).filter(c=>!c.v046Tile&&!c.v061Poste)},world,x,z,.5);}
 function position(anchor,existing=null){const candidates=existing?[[existing[0],existing[2],true]]:[];for(const radius of[4.5,6.5,9])for(let i=0;i<12;i++)candidates.push([anchor[0]+Math.cos(i*Math.PI/6)*radius,anchor[2]+Math.sin(i*Math.PI/6)*radius,false]);for(const[x,z,retained]of candidates){const y=ground(x,z);if(!Number.isFinite(y))continue;const samples=[[.5,.5],[-.5,.5],[.5,-.5],[-.5,-.5]].map(([dx,dz])=>ground(x+dx,z+dz));if(samples.some(h=>!Number.isFinite(h)||Math.abs(h-y)>.12))continue;if((world.colliders||[]).some(c=>!c.disabled&&!c.v061Poste&&y+1.5>=(c.minY??-Infinity)&&y<=(c.maxY??Infinity)&&v017ColliderHit(c,x,z,.75)))continue;if((world.npcs||[]).some(n=>Math.hypot(n.pos[0]-x,n.pos[2]-z)<1.6)||(world.interactables||[]).some(n=>!n.v061Poste&&Math.hypot(n.pos[0]-x,n.pos[2]-z)<1.7)||!retained&&Math.hypot(state.player.pos[0]-x,state.player.pos[2]-z)<1.3)continue;if(!lineOfSight([anchor[0],anchor[1]+1.6,anchor[2]],[x,y+1,z]))continue;return[x,y,z];}return null;}
 function inspect(q){if(!state.v061Poste.letters[q.id].read&&!transact('inspect',q.id,null,q.site))return false;if(blocked()||!physical(q.id))return false;openNote('post61:'+q.id,q.name.toUpperCase(),M.policy(q,state.v060Council)+'\n\n'+q.evidence+(state.v061Poste.letters[q.id].choice?'\n\nREÇU : '+(state.v061Poste.letters[q.id].choice==='a'?q.textA:q.textB):'')+'\n\nRapportez votre décision au représentant. Aucun nom privé ne sera transmis à la radio.');return true;}
 function bind(){
  const sites=world?.v046?[...V042_RUNTIME.active.keys()].sort().join('|'):'',signature=[unlocked(),settings.geoFalloutLayer,V046.lab,world?.v050CityInterior,sites,JSON.stringify(state.v061Poste)].join(':');
  if(rt.owner===world&&rt.state===state&&rt.records===world?.v046Records&&rt.signature===signature)return;
  const previous=rt.owner===world&&rt.state===state?new Map(rt.entries.map(e=>[e.q.id,e.pos])):new Map();
  if(rt.owner)for(const k of['interactables','colliders'])rt.owner[k]=rt.owner[k].filter(o=>!o.v061Poste);
  rt.owner=world;rt.state=state;rt.records=world?.v046Records;rt.signature=signature;rt.entries=[];rt.draws=[];
  if(!world?.v046||!unlocked()||!settings.geoFalloutLayer||V046.lab||world.v050CityInterior)return;
  for(const q of letters){const rec=V042_RUNTIME.active.get(q.site);if(!rec?.site.safe||!rec.pos?.every(Number.isFinite))continue;const pos=position(rec.pos,previous.get(q.id));if(!pos)continue;
   const r=state.v061Poste.letters[q.id],col=r.claimed?[.25,.29,.25]:r.choice?[.25,.60,.35]:r.read?[.3,.48,.67]:[.83,.63,.16],temp={staticDraws:[]},box=(offset,size,color)=>addBox(temp,pos.map((n,i)=>n+offset[i]),size,color);
   box([0,.1,0],[.85,.2,.65],[.22,.24,.22]);box([0,.65,0],[.12,1.1,.12],[.33,.36,.34]);box([0,1.2,0],[.85,.5,.10],col);box([0,1.2,.06],[.59,.27,.02],[.88,.85,.70]);
   if(r.choice&&!r.claimed){box([0,.39,.22],[.66,.35,.45],[.51,.35,.17]);box([0,.58,.22],[.70,.05,.47],col);}
   for(const d of temp.staticDraws){d.v061Poste=q.id;d.v042Site=q.site;}rt.draws.push(...temp.staticDraws);
   const e={q,pos,state},it=addInteract(world,'post61:'+q.id,[pos[0],pos[1]+1,pos[2]+.55],r.choice?(r.claimed?'Relire le reçu · ':'Récupérer le contre-don · ')+q.name:'Examiner le courrier · '+q.name,()=>{if(e.state!==state||rt.owner!==world)return false;return r.choice&&!r.claimed?transact('claim',q.id,null,q.site):inspect(q);},{radius:3,kind:'note',priority:4,condition:()=>!blocked()&&physical(q.id)});it.v061Poste=q.id;it.v042Site=q.site;
   const collider=addCollider(world,pos[0],pos[2],.85,.65,{id:'post61:'+q.id,minY:pos[1],maxY:pos[1]+1.45});collider.v061Poste=q.id;collider.v042Site=q.site;rt.entries.push(e);
  }
 }
 const draw=collectDraws;collectDraws=function(...args){bind();return draw(...args).concat(rt.draws);};
 function track(id){const q=letters.find(q=>q.id===id);if(!q||!unlocked()||blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=q.site;try{if(saveGame(false)===false)throw Error();}catch{for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);return notice('Suivi non sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
 V027_SUBS.data.poste='POSTE RESTANTE';
 function panel(c){const esc=v027Escape,l=state.v061Poste;c.innerHTML='<div class="p27-long"><p class="p27-kicker">APRÈS LES ÉTATS GÉNÉRAUX</p><h2>Les premières lettres de la Charte</h2><p>'+esc(!unlocked()?'La tournée s’ouvre après la ratification régionale.':M.bulletin(l))+'</p>'+letters.map(q=>{const r=l.letters[q.id],site=v042Site(q.site);return'<section class="v046-notice"><h3>'+esc(q.name)+'</h3><p>'+esc(site?.name||q.site)+'</p><p>'+esc(r.choice?(r.choice==='a'?q.textA:q.textB):r.read?q.evidence:'Examinez le pupitre, remettez le courrier au représentant, puis récupérez le contre-don.')+'</p><p>'+esc(r.claimed?'Contre-don déjà retiré.':r.choice?'Contre-don disponible sur le pupitre.':'Réclamation à résoudre sur place.')+'</p>'+v027Button('Suivre le relais','post61:track',q.id,!unlocked())+'</section>';}).join('')+'<p>Les sept reçus se rapportent au relais marchand d’Aubagne Haute. La tournée ne remplace ni les dossiers précédents ni la charte ratifiée.</p></div>';}
 const data=v027Data;v027Data=function(c){if(V027.sub==='poste')return panel(c);const r=data(...arguments);if(V027.sub==='council'&&unlocked())c.insertAdjacentHTML('beforeend','<section class="v046-notice"><h2>La charte doit aussi voyager</h2><p>Poste Restante attend des porteurs pour les sept réseaux.</p>'+v027Button('Consulter la tournée','jump','data:poste')+'</section>');return r;};
 const dispatch=v027Dispatch;v027Dispatch=function(action,arg){if(action==='post61:track')return v027CanAct()&&track(arg);return dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v061Poste;if(!l.accepted)return rows(...arguments);return rows(...arguments).concat([{id:'post61:tour',name:'LES PREMIÈRES LETTRES DE LA CHARTE',stage:l.finished?'done':'active',active:!l.finished,text:M.bulletin(l),zone:null,steps:letters.map(q=>[q.name,!!l.letters[q.id].choice]).concat([['Sept reçus rapportés à Aubagne Haute',l.finished]]),source:'Poste Restante',badge:l.finished?'✓':'',hint:'Sept courriers et des réserves finies'}]);};
 const prevTrack=v027Track;v027Track=function(id){if(id==='post61:tour'){const q=letters.find(q=>!state.v061Poste.letters[q.id].choice)||letters[0];return track(q.id);}return prevTrack(...arguments);};
 V027_STATIONS.poste={name:'Poste Restante — la tournée continue',freq:'61.3',hint:'Reçus et réclamations des relais',available:unlocked,text:()=>M.bulletin(state.v061Poste)};
 const previousAfter=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){previousAfter?.();Object.assign(window.__MISTRAL_DEBUG,{v061PosteInfo:()=>{bind();return{ledger:copy(state.v061Poste),physical:rt.entries.map(e=>({id:e.q.id,site:e.q.site,pos:e.pos.slice()})),draws:rt.draws.length,error:rt.error,unlocked:unlocked()};},v061PosteOpen:()=>v027Open('data','poste'),v061PosteAction:(type,id,choice,site)=>transact(type,id,choice,site)});};
}
