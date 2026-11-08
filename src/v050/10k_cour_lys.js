/* Cour du Lys d'If — authored Fallout: Mistral fiction.
 * A distinct audience instance; old island dungeons and geographic features stay intact.
 * The crossing is a loading-screen journey, not a freely navigable simulated vessel. */
const MistralLys=(()=>{
 'use strict';
 const copy=o=>JSON.parse(JSON.stringify(o)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k),count=n=>Number.isSafeInteger(n)&&n>=0&&n<=999999;
 const SITE_ID='v068-cour-lys',ANCHOR='v042-frioul-interior-01';
 const PORTS=['v042-marseille-caravan-01','v042-frioul-caravan-01'];
 const PEOPLE={
  apolline:{name:'Apolline Veyran',role:'Chambellane du Lys',pos:[-8,0,18],text:'« Nous avons gardé des œuvres, des vivres et des portes ouvertes quand les autres brûlaient leurs archives. Puis la machine a décidé que protéger le royaume exigeait de classer ses habitants. Je veux préserver ce refuge, pas affamer les cuisines. »'},
  sana:{name:'Sana Borel',role:'Intendante des cuisines',pos:[-16,0,2],text:'« Le roi est une lumière. Il ne mange pas. Pourtant son protocole réserve des parts aux titres avant de compter les bouches. Je peux partager ce lot ; je ne peux pas nourrir toute la rade avec. »'},
  basile:{name:'Basile Orsini',role:'Gardien des collections',pos:[16,0,6],text:'« Louis a empêché la dispersion des collections. Vous pouvez retirer son pouvoir sans détruire ce qu’il sait. Je refuse qu’une nouvelle liberté commence par brûler les traces des anciens abus. »'},
  jeanne:{name:'Jeanne Ravel',role:'Porte-parole des Sans-Titre',pos:[8,0,18],text:'« On nous a recueillis sans nous demander d’où nous venions. Maintenant on nous refuse une ration parce que personne n’a transmis de titre à nos parents. Nous demandons une voix, pas un ancêtre inventé. »'}
 };
 const VOICES=['sana','basile','jeanne'];
 const EVIDENCE={
  vivres:{name:'Le stock et les assiettes',pos:[-18,0,-8],text:'Le stock d’accueil est distinct du lot des habitants. Les comptes montrent une priorité aux rangs, pas un manque total de nourriture. Les réserves restent limitées : ouvrir le garde-manger ne crée pas un ravitaillement permanent.'},
  accueil:{name:'La promesse du refuge',pos:[19,0,-4],text:'Une ancienne inscription d’accueil protège toute personne secourue comme HÔTE, avant tout serment. La cour a ajouté ses titres au fil des générations ; cette clause n’a jamais été abrogée. Elle ouvre un droit de visite, pas la propriété du fort.'},
  programme:{name:'Le roi de la salle de classe',pos:[16,0,-23],text:'LOUIS-27 était un médiateur pédagogique : « La monarchie et ses contradictions ». Les survivants lui ont confié les inventaires, puis l’autorité. Il a pris un rôle d’enseignement pour une succession légitime. Ses connaissances restent réelles ; son sang royal ne l’a jamais été.'}
 };
 const POLICIES={
  serment:{name:'La Cour sous serment',text:'LOUIS conserve un rôle cérémoniel. L’accueil et les rations ne dépendent plus d’un héritage ; les intendants rendent leurs décisions contestables. Les dignitaires conservent toutefois une influence que le serment ne supprime pas.',gift:{food:3,cloth:1}},
  commune:{name:'Le musée et la commune',text:'Les habitants reprennent l’administration locale. LOUIS reste guide des collections, sans commande de rationnement. La communauté gagne une voix, mais doit entretenir elle-même les services et arbitrer ses désaccords.',gift:{food:1,water:3}},
  regence:{name:'La régence de secours',text:'Les décrets automatiques sont suspendus. Apolline et les Sans-Titre gardent ensemble les décisions d’urgence ; les archives restent consultables. Cette solution protège le secours immédiat, mais reporte le conflit sur la durée de la régence.',gift:{food:2,scrap:2}}
 };
 function fresh(){return{schema:1,revision:0,opened:false,heard:[],evidence:[],route:null,policy:null,notified:[],claimed:false,finished:false,journal:[]};}
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Registre du Lys plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.revision=count(raw.revision)?raw.revision:0;l.opened=raw.opened===true;
  if(l.opened){l.heard=VOICES.filter(k=>Array.isArray(raw.heard)&&raw.heard.includes(k));l.route=['etiquette','technique','service'].includes(raw.route)?raw.route:null;
   l.evidence=Object.keys(EVIDENCE).filter(k=>Array.isArray(raw.evidence)&&raw.evidence.includes(k)&&(k!=='programme'||l.route));
   if(l.heard.length===3&&l.evidence.length===3&&own(POLICIES,raw.policy))l.policy=raw.policy;
   if(l.policy){l.notified=VOICES.filter(k=>Array.isArray(raw.notified)&&raw.notified.includes(k));l.claimed=raw.claimed===true;l.finished=l.notified.length===3&&raw.finished===true;}
  }
  const kinds=['open','hear','read','gate','decide','notify','claim','finish'];
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&kinds.includes(e.type)).slice(-32).map(e=>({type:e.type,id:typeof e.id==='string'?e.id.slice(0,30):null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];return l;
 }
 function point(type,id){return ['open','finish'].includes(type)?'apolline':['hear','notify','read'].includes(type)?id:type==='gate'?(id==='service'?'levier':'guichet'):type==='decide'?'louis':'colis';}
 function briefing(raw){const l=migrate(raw);return !l.opened?'La traversée mène à une audience, pas à un serment d’allégeance. Parlez à Apolline.':l.finished?'Le règlement local est remis. Il ne constitue ni une réunification de la France ni une nouvelle fin régionale.':l.policy?`${l.notified.length}/3 interlocuteurs informés. Revenez ensuite auprès d’Apolline.`:`${l.heard.length}/3 voix entendues · ${l.evidence.length}/3 preuves. Examinez les archives, puis confrontez LOUIS-27.`;}
 function apply(snapshot,a={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));if(!ctx.local||!ctx.near||ctx.point!==point(a.type,a.id))throw Error('Rejoignez le bon interlocuteur ou document de la Cour.');
  if(!Number.isFinite(snapshot.player?.hp)||snapshot.player.hp<=0||!count(snapshot.player.caps))throw Error('État du personnage invalide.');
  const l=migrate(snapshot.v068Lys);if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Cette proposition est périmée.');if(l.revision===999999)throw Error('Registre plein.');
  let cost={},gain={},caps=0;
  if(a.type==='open'){if(l.opened)throw Error('Audience déjà ouverte.');l.opened=true;}
  else{
   if(!l.opened)throw Error('Parlez d’abord à Apolline.');
   if(a.type==='hear'){if(!VOICES.includes(a.id)||l.heard.includes(a.id)||l.policy)throw Error('Voix inconnue, déjà entendue ou audience conclue.');l.heard.push(a.id);}
   else if(a.type==='read'){if(!own(EVIDENCE,a.id)||l.evidence.includes(a.id))throw Error('Document inconnu ou déjà copié.');if(a.id==='programme'&&!l.route)throw Error('Ouvrez un accès aux archives.');l.evidence.push(a.id);}
   else if(a.type==='gate'){
    if(l.route||!['etiquette','technique','service'].includes(a.id))throw Error('Accès inconnu ou déjà ouvert.');
    if(a.id==='etiquette'&&(!l.evidence.includes('accueil')||a.answer!=='hote'))throw Error('Relisez la clause d’accueil : quel statut protège une personne secourue ? Aucun droit n’a été perdu.');
    if(a.id==='technique'){if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');cost={circuitry:1};}
    l.route=a.id;
   }else if(a.type==='decide'){if(l.policy||l.heard.length!==3||l.evidence.length!==3||!own(POLICIES,a.id))throw Error('Trois voix et trois preuves sont nécessaires ; le règlement est exclusif.');l.policy=a.id;}
   else if(a.type==='notify'){if(!l.policy||!VOICES.includes(a.id)||l.notified.includes(a.id))throw Error('Règlement absent, interlocuteur inconnu ou déjà informé.');l.notified.push(a.id);}
   else if(a.type==='claim'){if(!l.policy||l.claimed)throw Error('Colis indisponible ou déjà retiré.');gain=POLICIES[l.policy].gift;l.claimed=true;}
   else if(a.type==='finish'){if(!l.policy||l.notified.length!==3||l.finished)throw Error('Audience incomplète ou déjà soldée.');caps=55;l.finished=true;}
   else throw Error('Action du Lys inconnue.');
  }
  for(const [id,n]of Object.entries(cost)){const v=own(snapshot.inventory,id)?snapshot.inventory[id]:0;if(!count(v)||v<n)throw Error('Fournitures insuffisantes ou quantité invalide.');}
  for(const [id,n]of Object.entries(gain)){const v=own(snapshot.inventory,id)?snapshot.inventory[id]:0;if(!count(v)||v+n>999999)throw Error('Inventaire invalide ou plein.');}
  if(snapshot.player.caps+caps>999999)throw Error('Compte de capsules plein.');
  const out=copy(snapshot);out.inventory??={};for(const[id,n]of Object.entries(cost))out.inventory[id]=snapshot.inventory[id]-n;for(const[id,n]of Object.entries(gain))out.inventory[id]=(snapshot.inventory?.[id]||0)+n;out.player.caps+=caps;
  l.revision++;l.journal.push({type:a.type,id:typeof a.id==='string'?a.id:null,at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});l.journal=l.journal.slice(-32);out.v068Lys=l;return out;
 }
 return{SITE_ID,ANCHOR,PORTS:PORTS.slice(),PEOPLE:copy(PEOPLE),VOICES:VOICES.slice(),EVIDENCE:copy(EVIDENCE),POLICIES:copy(POLICIES),fresh,migrate,point,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralLys;

if(typeof baseState==='function'&&typeof V042_CATALOG!=='undefined'){
 const M=MistralLys,copy=o=>JSON.parse(JSON.stringify(o));
 const anchor=v042Site(M.ANCHOR);
 if(anchor&&!v042Site(M.SITE_ID)){
  const site={...copy(anchor),id:M.SITE_ID,name:'Cour du Lys d’If · Le roi ne mange pas',description:'Audience dans une cour insulaire. Intérieur fictionnel distinct des anciens lieux d’If ; traversée narrative possible depuis les relais maritimes.',kind:'interior',interior:'lys',faction:'lys',factionLabel:'Cour du Lys d’If',tier:1,safe:true,unique:true,visitable:true,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],enemyRadius:0,rewardCaps:0,rewardXP:0,respawnHours:0,provenance:{kind:'authored-fiction',anchorId:M.ANCHOR,scope:'Reuses approximate existing catalogue anchor, not a surveyed entrance or historic floor plan.'}};
  V042_CATALOG.push(site);V042_SITE_BY_ID[site.id]=site;V042_SITES_BY_MACRO[site.macro].push(site);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[site.macro]++;
 }
 const P={...Object.fromEntries(Object.entries(M.PEOPLE).map(([k,p])=>[k,p.pos])),...Object.fromEntries(Object.entries(M.EVIDENCE).map(([k,p])=>[k,p.pos])),guichet:[16,0,-8],levier:[6,0,-23],louis:[-8,3.2,-25],colis:[-18,0,-2],sortie:[0,0,26]};
 const rt={busy:false,error:null};
 const base=baseState;baseState=function(...a){const s=base(...a);s.v068Lys=M.fresh();return s;};
 const migrate=migrateState;migrateState=function(raw={}){const s=migrate(raw);s.v068Lys=M.migrate(raw?.v068Lys);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v068Lys&&state.v042?.activeInterior===M.SITE_ID;
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc synthétique sans progression de campagne.':zoneTransitioning||V046.busy||V047.pending?'Attendez la fin du chargement.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':inCombat?'Éloignez le combat.':null;}
 function near(id){const p=P[id];if(!local()||!p)return false;if(M.PEOPLE[id]&&!world.npcs.some(n=>n.id==='lys68:'+id&&n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.3&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7]);}
 function portNear(site){if(!M.PORTS.includes(site)||!world?.geoMacro||!world.v046||state.v042?.activeInterior||world.v050CityInterior||!settings.geoFalloutLayer||!v042SiteDiscovered(v042Site(site)))return false;const p=state.player.pos;if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,p))return false;return world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===site&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 const notice=t=>{V027.message=t;toast(t,'bad');return false;};
 function restore(owner,before){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}
 function act(type,id,answer,revision){
  if(rt.busy)return false;const owner=state,scene=world,before=copy(owner);let next;
  try{next=M.apply(owner,{type,id,answer},{local:local(),near:near(M.point(type,id)),point:M.point(type,id),blocked:blocked(),revision});}catch(e){return notice(e.message);}
  rt.busy=true;try{owner.v068Lys=next.v068Lys;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde du Lys refusée.');}catch(e){restore(owner,before);return notice(e.message+' Opération annulée.');}finally{rt.busy=false;}
  try{visuals(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='finish'?'Audience close · 55 capsules.':'Décision locale sauvegardée.','good');}catch(e){rt.error=e.message;}return true;
 }
 function guard(fn){const owner=state,scene=world,rev=state.v068Lys.revision;return()=>state===owner&&world===scene&&rev===state.v068Lys.revision?fn(rev):notice('Cette conversation est périmée.');}
 const back=()=>({text:'Revenir.',onChoose:closeDialogue});
 function talk(id){
  if(blocked()||!near(id))return notice(blocked()||'Rejoignez cet habitant.');const p=M.PEOPLE[id],l=state.v068Lys,ch=[];if(!p)return false;
  if(id==='apolline'&&!l.opened)ch.push({text:'Ouvrir « Le roi ne mange pas ».',onChoose:guard(rev=>{act('open',null,null,rev);talk(id);})});
  if(l.opened&&M.VOICES.includes(id)&&!l.heard.includes(id))ch.push({text:'Écouter et conserver sa position.',onChoose:guard(rev=>{act('hear',id,null,rev);talk(id);})});
  if(l.policy&&M.VOICES.includes(id)&&!l.notified.includes(id))ch.push({text:'Présenter le règlement adopté.',onChoose:guard(rev=>{act('notify',id,null,rev);talk(id);})});
  if(id==='apolline'&&l.notified.length===3&&!l.finished)ch.push({text:'Clore l’audience · 55 capsules.',onChoose:guard(rev=>{act('finish',null,null,rev);talk(id);})});ch.push(back());
  openDialogue(speaker(p.name,p.role.toUpperCase(),'LY'),p.text+'\n\n'+M.briefing(l)+(l.policy?'\n\n'+M.POLICIES[l.policy].text:''),ch);return true;
 }
 function evidence(id){if(blocked()||!near(id))return false;const l=state.v068Lys,e=M.EVIDENCE[id],ch=[];if(!e)return false;if(l.opened&&!l.evidence.includes(id))ch.push({text:'Conserver cette preuve.',onChoose:guard(rev=>{act('read',id,null,rev);evidence(id);})});ch.push(back());openDialogue(speaker(e.name,'ARCHIVES DU LYS','AR'),e.text,ch);return true;}
 function gate(service=false){const point=service?'levier':'guichet';if(blocked()||!near(point))return false;const l=state.v068Lys,ch=[];
  if(l.opened&&!l.route){if(service)ch.push({text:'Ouvrir la porte de service depuis le couloir.',onChoose:guard(rev=>{act('gate','service',null,rev);gate(true);})});else{for(const [id,label]of [['hereditaire','Un sujet héréditaire'],['hote','Un hôte secouru'],['objet','Un objet de collection']])ch.push({text:label,onChoose:guard(rev=>{act('gate','etiquette',id,rev);gate();})});ch.push({text:'Dérivation technique · INT 5 + 1 circuit.',onChoose:guard(rev=>{act('gate','technique',null,rev);gate();})});}}ch.push(back());
  openDialogue(speaker(service?'Verrou de service':'Guichet des titres','ACCÈS AUX ARCHIVES','LY'),l.route?'Un accès aux archives est sauvegardé. Les autres passages ne sont pas requalifiés comme réparés.':service?'Le personnel a conservé un déverrouillage manuel. Il ouvre le passage latéral ; il ne détruit pas les archives et ne prétend pas accorder un titre.':'Le guichet demande quel statut protège une personne secourue. La promesse d’accueil est exposée avec les collections. Le couloir de service offre également un passage sans paiement.',ch);return true;
 }
 function king(){if(blocked()||!near('louis'))return false;const l=state.v068Lys,ch=[];if(l.opened&&!l.policy)for(const[id,p]of Object.entries(M.POLICIES))ch.push({text:'Examiner : '+p.name,onChoose:guard(()=>confirm(id))});ch.push(back());openDialogue(speaker('LOUIS-27','SA MAJESTÉ PÉDAGOGIQUE','XX'),l.policy?M.POLICIES[l.policy].text:'« Je suis le roi de ce que j’ai préservé. Mes titres garantissent la continuité ; vos preuves prétendent que ma couronne était une consigne de cours. Montrez-moi que protéger ces sujets n’exige pas de les classer par naissance. »\n\n'+M.briefing(l),ch);return true;}
 function confirm(id){if(blocked()||!near('louis')||!M.POLICIES[id])return false;const p=M.POLICIES[id];openDialogue(speaker('LOUIS-27','RÈGLEMENT LOCAL · CHOIX EXCLUSIF','XX'),p.name+'\n\n'+p.text+'\n\nLes collections seront conservées. Ni la charte régionale ni les anciens votes ne seront réécrits. Le stock d’accueil remet une fois : '+Object.entries(p.gift).map(([k,n])=>n+' '+itemLabel(k)).join(' + ')+'. Informez les trois représentants, puis revenez auprès d’Apolline : 55 capsules, une fois.',[{text:'Confirmer ce règlement.',onChoose:guard(rev=>{act('decide',id,null,rev);king();})},{text:'Revenir aux propositions.',onChoose:guard(king)}]);return true;}
 function supply(){if(blocked()||!near('colis'))return false;const l=state.v068Lys,ch=[];if(l.policy&&!l.claimed)ch.push({text:'Retirer le colis d’accueil.',onChoose:guard(rev=>{act('claim',null,null,rev);supply();})});ch.push(back());openDialogue(speaker('Réserve d’accueil','LOT FINI · DISTINCT DES RATIONS DES HABITANTS','LY'),!l.policy?'Le stock d’accueil reste fermé pendant l’audience.':l.claimed?'Le colis a déjà été remis. Aucun voyage ni changement d’heure ne le renouvelle.':Object.entries(M.POLICIES[l.policy].gift).map(([id,n])=>n+' '+itemLabel(id)).join(' + ')+'. Ce retrait ne prélève pas les réserves de la Cité ou des pharmacies.',ch);return true;}
 function visuals(w){if(!w?.v068Lys)return;const l=state.v068Lys;for(const d of w.staticDraws){if(d.lysGate)d.hidden=l.route&&(d.lysGate==='service'?l.route==='service':l.route!=='service');if(d.lysRoyal)d.hidden=l.policy==='commune';if(d.lysCrown||d.lysCrownBand)d.hidden=l.policy==='commune'||l.policy==='regence';if(d.lysGuide)d.hidden=l.policy!=='commune';if(d.lysBanner)d.color=l.policy==='commune'?[.31,.51,.41]:l.policy==='regence'?[.57,.45,.25]:[.22,.30,.53];if(d.lysBody){d.emissive=l.policy==='regence'?.25:.60;}if(d.lysGift)d.hidden=!l.policy||l.claimed;}
  for(const c of w.colliders){if(c.lysGate)c.disabled=!!l.route&&(c.lysGate==='service'?l.route==='service':l.route!=='service');if(c.lysGift)c.disabled=!l.policy||l.claimed;}
 }
 function build(){
  const w=createWorld(V042_INSTANCE_ZONE,'Cour du Lys d’If — Le roi ne mange pas','COUR INSULAIRE · SCÈNE FICTIONNELLE',{skyTop:[58,91,133],skyBottom:[173,159,118],fog:[.48,.49,.43],wind:.4,daylight:.65,indoor:false});w.v068Lys=true;w.bounds=[-24,24,-32,30];w.spawn=[0,1.65,24];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE_ID;
  const stone=[.58,.53,.43],dark=[.23,.28,.29],gold=[.81,.65,.28];
  const box=(p,s,c=stone,solid=false,tag=null)=>{const d=addBox(w,p,s,c);if(tag)d[tag]=true;if(solid){const co=addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});if(tag)co[tag]=true;}return d;};
  box([0,-.18,-1],[48,.36,62],stone);addFloorZone(w,0,-1,48,62,0,{priority:1});
  for(const x of [-23.6,23.6])box([x,3,-1],[.6,6,62],stone,true);box([0,3,-31.5],[48,6,.6],stone,true);
  for(const x of [-14,14])box([x,2.0,29.4],[20,4,.5],stone,true);
  for(const x of [-22,-14,-6,2,10,18])box([x,5.8,-31.4],[2.3,1.5,1],stone,true);
  // Deliberately wide court and independent loops; no mandatory jumping.
  box([-10,.05,13],[12,.10,21],[.34,.31,.29]);box([6,.05,13],[12,.10,21],[.34,.31,.29]);
  for(const x of [-21,21])for(const z of [16,0]){box([x,2.4,z],[.7,4.8,.7],dark,true);const b=box([x,3.2,z+.42],[1.8,2.5,.06],[.22,.30,.53]);b.lysBanner=true;box([x,3.2,z+.47],[.18,1.6,.04],gold);box([x,3.2,z+.48],[.9,.18,.04],gold);}
  // Museum to the east, kitchen to the west; both connect to the central court.
  box([-10,1.4,-2],[.3,2.8,10],stone,true);box([-10,1.4,-13],[.3,2.8,6],stone,true);
  box([-18,.55,6.2],[5,1.1,1.4],[.36,.28,.18],true);for(const x of[-20,-18,-16]){box([x,1.25,6.2],[.6,.3,.6],[.54,.45,.29]);}
  for(const z of [8,0]){box([21,.6,z],[1.8,1.2,2],dark,true);addPart(w,'sphere',[21,1.55,z],[.60,.68,.50],gold);}
  // Archive: front door and a distinct service entry remain physical alternatives.
  box([8,1.8,-15],[.35,3.6,10],stone,true);box([8,1.8,-28],[.35,3.6,6],stone,true);
  box([10,1.8,-10],[4,3.6,.35],stone,true);box([21,1.8,-10],[4,3.6,.35],stone,true);
  const front=box([15.5,1.65,-10],[7,3.3,.25],dark);front.lysGate='front';const fc=addCollider(w,15.5,-10,7,.25,{minY:0,maxY:3.3});fc.lysGate='front';
  const side=box([8,1.65,-22.5],[.25,3.3,5],dark);side.lysGate='service';const sc=addCollider(w,8,-22.5,.25,5,{minY:0,maxY:3.3});sc.lysGate='service';
  for(const z of [-16,-25]){box([21.5,1.1,z],[1,2.2,3],dark,true);for(let i=0;i<4;i++)box([21.0,.4+i*.45,z],[.1,.24,2.7],[.52,.41,.27]);}
  // Royal gallery and stairs, with solid undersides and a fall-back ground floor.
  box([-8,3.02,-25],[28,.36,14],stone);addFloorZone(w,-8,-25,28,14,3.2,{priority:1});addCollider(w,-8,-25,28,14,{minY:2.84,maxY:3.1});v021Stairs(w,-8,-12,12,4,3.2);
  for(const [x,width]of [[-17,10],[1,10]])box([x,3.9,-18],[width,1.3,.22],dark,true);
  box([-8,3.6,-26],[3,.8,2.5],dark,true);box([-8,4.1,-26],[2.6,.2,2.2],gold);
  const body=addPart(w,'cylinder',[-8,5.1,-26],[.65,1.6,.5],gold,0,{emissive:.6,alpha:.68});body.lysRoyal=true;body.lysBody=true;
  const head=addPart(w,'sphere',[-8,6.15,-26],[.65,.7,.65],gold,0,{emissive:.6,alpha:.72});head.lysRoyal=true;head.lysBody=true;
  // An original stylised ceremonial bust, rendered with the existing meshes.
  for(const [p,size]of [[[-8,5.65,-26],[1.6,.34,.75]],[[-8,4.62,-26.16],[1.50,.80,.56]],[[-8.78,5.08,-26],[.24,1.02,.27]],[[-7.22,5.08,-26],[.24,1.02,.27]],[[-8,5.15,-26.40],[1.72,1.35,.16]]]){const d=box(p,size,gold);d.lysRoyal=true;d.lysBody=true;d.emissive=.55;d.alpha=.68;}
  for(const x of [-8.18,-7.82]){const d=box([x,6.24,-25.65],[.12,.09,.035],[.28,.21,.08]);d.lysRoyal=true;}
  const mouth=box([-8,6.04,-25.64],[.27,.055,.03],[.38,.27,.08]);mouth.lysRoyal=true;
  const band=addPart(w,'cylinder',[-8,6.50,-26],[.75,.16,.75],gold,0,{emissive:.6});band.lysRoyal=true;band.lysCrownBand=true;
  for(const x of [-8.50,-8,-7.50]){const c=box([x,6.73,-26],[.16,.35,.18],gold);c.lysCrown=true;}
  for(const y of [4.5,4.9,5.3,5.7]){const d=box([-8,y,-25.59],[1.25,.035,.025],[.96,.88,.52]);d.lysRoyal=true;d.emissive=.5;}
  const guide=box([-8,5.4,-26],[1.3,1.7,.08],[.35,.65,.70]);guide.lysGuide=true;guide.emissive=.5;
  for(const [id,e]of Object.entries(M.EVIDENCE)){const [x,y,z]=e.pos;box([x,y+.5,z],[1.2,1,.75],dark,true);box([x,y+1.05,z],[1.3,.08,.85],[.77,.71,.55]);addInteract(w,'lys68:'+id,[x,y+1.25,z+.7],'Lire · '+e.name,()=>evidence(id),{radius:3.3,kind:'quest',priority:5,condition:()=>near(id)&&!blocked()});}
  box([6,.9,-23],[.6,1.8,.45],dark,true);box([6,1.6,-22.72],[.35,.16,.12],gold);
  for(const [id,label,fn]of [['guichet','Consulter le guichet des archives',()=>gate()],['levier','Déverrouiller la porte de service',()=>gate(true)],['louis','S’adresser à LOUIS-27',king],['colis','Examiner la réserve d’accueil',supply]]){const p=P[id];addInteract(w,'lys68:'+id,[p[0],p[1]+1.25,p[2]+.7],label,fn,{radius:3.3,kind:'quest',priority:5,condition:()=>near(id)&&!blocked()});}
  const crate=box([-18,.45,-2],[1.2,.9,.9],[.41,.32,.19],true,'lysGift');box([-18,.96,-2],[1.3,.1,1],[.61,.52,.29],false,'lysGift');
  for(const[id,p]of Object.entries(M.PEOPLE))addHumanNPC(w,'lys68:'+id,p.name,p.role,p.pos,id==='apolline'?[.27,.33,.56]:id==='sana'?[.47,.39,.28]:id==='basile'?[.32,.42,.36]:[.55,.36,.27],{dialogue:'lys68:'+id,yaw:Math.PI});
  const sign=(x,y,z,t)=>{if(typeof v021Sign==='function')v021Sign(w,x,y,z,t,.065);};sign(0,2.2,28,'RETOUR AU PASSEUR');sign(-17,2.6,6,'CUISINES');sign(17,3.3,-10,'ARCHIVES');sign(-8,6.8,-30,'LOUIS / XXVII');sign(0,3,10,'LA COUR DU LYS');
  addInteract(w,'lys68:sortie',[0,1.25,26.7],'Retourner au point de débarquement',()=>{if(blocked()||!near('sortie'))return false;return v042ExitInstance();},{radius:3.3,kind:'door',priority:5});
  w.subzones=[{id:'lys-entree',name:'Accueil des hôtes',pos:[0,0,22]},{id:'lys-cuisine',name:'Cuisines des titres',pos:[-16,0,0]},{id:'lys-musee',name:'Collections préservées',pos:[17,0,3]},{id:'lys-archives',name:'Archives pédagogiques',pos:[16,0,-23]},{id:'lys-couronne',name:'Galerie royale',pos:[-8,3.2,-25]}];w.levelRoutes=[{id:'lys-free',points:[[0,0,24],[-4,0,16],[-4,0,-6],[-8,0,-6],[-8,3.2,-18],[-8,3.2,-23]]}];visuals(w);return w;
 }
 const oldBuild=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE_ID?build():oldBuild(...arguments);};
 const ground=groundHeightAt;groundHeightAt=function(x,z,feet=0){if(!world?.v068Lys)return ground(...arguments);const hs=world.floorZones.filter(f=>x>=f.minX&&x<=f.maxX&&z>=f.minZ&&z<=f.maxZ).map(f=>floorZoneHeight(f,x,z)).filter(h=>h<=feet+.60);return hs.length?Math.max(...hs):0;};
 const oldTalk=talkToNPC;talkToNPC=function(id){return typeof id==='string'&&id.startsWith('lys68:')?talk(id.slice(6)):oldTalk(...arguments);};
 const oldClaim=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE_ID?false:oldClaim(...arguments);};
 function sail(site){
  if(blocked()||!portNear(site)||!v042Site(M.SITE_ID))return notice(blocked()||'Rejoignez le représentant du relais maritime.');
  const owner=state,scene=world,before=copy(owner),maps={active:new Map(V042_RUNTIME.active),npcData:new Map(V042_RUNTIME.npcData),nearest:V042_RUNTIME.nearest,instance:V042_RUNTIME.instanceSite,retained:V048.retained};
  const oldSave=saveGame;let wrote=false;saveGame=function(...a){const ok=oldSave(...a);if(ok===false)throw Error('Départ non sauvegardé.');wrote=true;return ok;};
  try{const ok=v042EnterSite(M.SITE_ID);if(!ok)throw Error('Traversée interrompue.');return true;}
  catch(e){restore(owner,before);world=scene;V042_RUNTIME.active=maps.active;V042_RUNTIME.npcData=maps.npcData;V042_RUNTIME.nearest=maps.nearest;V042_RUNTIME.instanceSite=maps.instance;V048.retained=maps.retained;if(typeof v049Own==='function')v049Own(world);if(wrote){try{oldSave(false);}catch{}}return notice(e.message);}
  finally{saveGame=oldSave;}
 }
 function crossing(site){if(blocked()||!portNear(site))return false;openDialogue(speaker('Maëlle Sarti','PASSEUSE · LIAISON AVEC LA COUR','MS'),'« La cour reçoit les hôtes avant de leur chercher des ancêtres. J’assure l’aller et le retour de cette audience ; je ne vous vends ni un navire ni une allégeance. »\n\nTraversée narrative par écran de chargement, sans navigation libre. Retour au même point de départ. Aucun paiement ni fin de campagne préalable. Les anciennes visites d’If restent distinctes.',[{text:'Embarquer pour l’audience du Lys.',onChoose:guard(()=>sail(site))},back()]);return true;}
 const relayTalk=v042TalkNPC;v042TalkNPC=function(id){const site=V042_RUNTIME.npcData.get(id)?.siteId;if(!M.PORTS.includes(site)||blocked()||!portNear(site))return relayTalk(...arguments);const prev=openDialogue;openDialogue=function(s,t,ch,...rest){return prev(s,t,[...(ch||[]).slice(0,-1),{text:'Passage maritime · Cour du Lys d’If',onChoose:guard(()=>crossing(site))},...(ch||[]).slice(-1)],...rest);};try{return relayTalk(...arguments);}finally{openDialogue=prev;}};
 function track(){if(blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=M.PORTS[0];try{if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Suivi non sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
 V027_SUBS.data.lys='COUR DU LYS D’IF';const data=v027Data;v027Data=function(c){if(V027.sub!=='lys')return data(...arguments);const l=state.v068Lys,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">LE ROI NE MANGE PAS</p><h2>La Cour du Lys d’If</h2><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre le départ du Vieux-Port','lys68:track')+'<p>Autre départ : halte de Ratonneau. Traversée narrative ; aucun bateau pilotable ajouté.</p><h3>Les voix</h3>'+M.VOICES.map(id=>'<p>'+(l.heard.includes(id)?'✓ ':'— ')+esc(M.PEOPLE[id].name)+'</p>').join('')+'<h3>Les preuves</h3>'+Object.entries(M.EVIDENCE).map(([id,e])=>'<p>'+(l.evidence.includes(id)?'✓ ':'— ')+esc(e.name)+'</p>').join('')+'<h3>Le règlement</h3><p>'+esc(l.policy?M.POLICIES[l.policy].text:'À confronter à LOUIS-27 sur place.')+'</p><p>'+esc(l.claimed?'Colis déjà retiré.':l.policy?'Colis d’accueil disponible dans les cuisines.':'Stock d’accueil fermé.')+'</p><p>Cour fictionnelle compacte, pas une restitution architecturale du château réel.</p></div>';};
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='lys68:track'?v027CanAct()&&track():dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v068Lys;return rows(...arguments).concat(l.opened?[{id:'lys68:quest',name:'LE ROI NE MANGE PAS',stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:[['Trois voix et trois preuves',l.heard.length===3&&l.evidence.length===3],['Règlement confronté à LOUIS',!!l.policy],['Trois représentants informés',l.notified.length===3],['Audience close',l.finished]],source:'Cour du Lys d’If',badge:l.finished?'✓':'',hint:'Apolline · cour insulaire'}]:[]);};
 const prevTrack=v027Track;v027Track=function(id){return id==='lys68:quest'?track():prevTrack(...arguments);};
 function next(){const l=state.v068Lys;if(!l.opened)return'apolline';const h=M.VOICES.find(k=>!l.heard.includes(k));if(h)return h;const e=Object.keys(M.EVIDENCE).find(k=>!l.evidence.includes(k));if(e)return e==='programme'&&!l.route?'guichet':e;if(!l.policy)return'louis';const n=M.VOICES.find(k=>!l.notified.includes(k));return n||(!l.finished?'apolline':!l.claimed?'colis':'sortie');}
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return marker(...arguments);const id=next(),p=P[id];return{zone:world.id,pos:[p[0],p[1]+1.25,p[2]+.7],label:M.PEOPLE[id]?.name||M.EVIDENCE[id]?.name||'Cour du Lys · '+id};};
 const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local())return ui(...arguments);$('questTitle').textContent='LE ROI NE MANGE PAS';$('questObjective').textContent=M.briefing(state.v068Lys);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='LE ROI NE MANGE PAS';f.querySelector('p').textContent=M.briefing(state.v068Lys);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.lys={name:'Le Lys — nouvelles de la cour',freq:'98.6',hint:'Un roi ne peut régner sur un inventaire vide',available:()=>state.v068Lys.opened,text:()=>M.briefing(state.v068Lys)+(state.v068Lys.policy?' '+M.POLICIES[state.v068Lys.policy].text:'')};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v068LysInfo:()=>({ledger:copy(state.v068Lys),local:local(),points:copy(P),site:M.SITE_ID,error:rt.error}),v068LysOpen:()=>v027Open('data','lys'),v068LysAction:act});};
}
