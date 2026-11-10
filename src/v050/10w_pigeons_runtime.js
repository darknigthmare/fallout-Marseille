/* Authored Post courtyard: two inhabited lofts, original stylised pigeons,
 * sealed dispatches and a walkable two-level fallback. No IGN geometry changes. */
if(typeof baseState==='function'&&typeof MistralPigeons!=='undefined'){
 const M=MistralPigeons,copy=x=>JSON.parse(JSON.stringify(x));
 const P={mirette:[0,0,22],sortie:[0,0,27],soins:[-21,0,-11],pompes:[21,3.2,-11],
  'source:soins':[-7,0,14],'source:pompes':[7,0,14],'loft:soins':[-17,0,-16],'loft:pompes':[17,3.2,-16]};
 const rt={busy:false,paused:false,error:null};
 const anchor=v042Site(M.RELAY);
 if(anchor&&!v042Site(M.SITE)){
  const s={...copy(anchor),id:M.SITE,name:'Cour des colombiers · Poste Restante',kind:'interior',interior:'pigeons',description:'Cour de correspondance fictionnelle : deux colombiers habités, un passage à pied et deux plis.',safe:true,visitable:true,unique:true,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],enemyRadius:0,rewardCaps:0,rewardXP:0,respawnHours:0,provenance:{kind:'authored-fiction',anchorId:M.RELAY}};
  V042_CATALOG.push(s);V042_SITE_BY_ID[s.id]=s;V042_SITES_BY_MACRO[s.macro].push(s);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[s.macro]++;
 }
 const base=baseState;baseState=function(...args){const s=base(...args);s.v074Pigeons=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(...arguments);s.v074Pigeons=M.migrate(raw?.v074Pigeons);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v074Pigeons&&state.v042?.activeInterior===M.SITE;
 const notice=t=>{V027.message=t;toast(t,'bad');return false;};
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc géographique sans progression.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':!onGround?'Rejoignez le sol.':null;}
 function near(id){const p=P[id];return local()&&p&&Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.2&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.8]);}
 function restore(owner,snapshot){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,snapshot);}
 function commit(next,caption){
  if(rt.busy)return false;const owner=state,w=world,before=copy(owner);rt.busy=true;
  try{owner.v074Pigeons=next.v074Pigeons;owner.player.caps=next.player.caps;if(state!==owner||w!==world||saveGame(false)===false)throw Error('Courrier non sauvegardé.');}
  catch(e){restore(owner,before);return notice(e.message+' Opération annulée.');}
  finally{rt.busy=false;if(world===w&&state===owner)visuals(w);}
  updateQuestUI(true);updateHUD();if(caption)toast(caption,'good');return true;
 }
 function act(type,id,bird,revision){let next;const p=M.point(type,id);try{next=M.act(state,{type,id,bird},{local:local(),near:near(p),point:p,blocked:blocked(),revision});}catch(e){return notice(e.message);}return commit(next,type==='finish'?'Deux réponses remises · 50 capsules, une fois.':'Courrier sauvegardé.');}
 function guard(fn){const s=state,w=world,r=state.v074Pigeons.revision;return()=>state===s&&world===w&&r===state.v074Pigeons.revision?fn(r):notice('Cette conversation est périmée.');}
 const back=()=>({text:'Revenir.',onChoose:closeDialogue});
 function confirm(id){if(blocked()||!near('mirette')||!Object.hasOwn(M.POLICIES,id))return false;
  openDialogue(speaker('Mirette Valon','POSTE RESTANTE','MV'),M.POLICIES[id].text+'\n\nLes deux reçus resteront dans le carnet. Cette décision ne change ni la charte régionale ni les anciennes tournées. 50 capsules à la clôture, une fois.',[{text:'Confirmer le traitement des réponses.',onChoose:guard(r=>{act('finish',id,null,r);dialogue('mirette');})},{text:'Revenir aux réponses.',onChoose:guard(()=>dialogue('mirette'))}]);return true;
 }
 function dialogue(id){
  if(blocked()||!near(id))return false;const l=state.v074Pigeons,ch=[];let title,text;
  const add=(label,type,key,bird,close=false)=>ch.push({text:label,onChoose:guard(r=>{const ok=act(type,key,bird,r);if(ok&&close)closeDialogue();else dialogue(id);})});
  if(id==='mirette'){
   title='Mirette Valon';text='« Le terminal veut encore un numéro de rue. Aïcha habite de l’autre côté de cette cour depuis vingt ans, et sa rue n’existe pas dans la machine. Les pigeons connaissent leur maison, pas nos formulaires. Ils sont revenus au guichet dans ces cages, avec un porteur. Maintenant ils peuvent rapporter un pli chez eux. Vous pouvez aussi prendre la passerelle. »';
   if(!l.opened)add('Accepter « La bonne adresse ».','open');
   if(!l.finished&&M.IDS.every(k=>l.mail[k].phase==='received'))for(const [key,o]of Object.entries(M.POLICIES))ch.push({text:o.name,onChoose:guard(()=>confirm(key))});
   if(rt.paused)ch.push({text:'Retenter la sauvegarde du vol.',onChoose:guard(()=>{try{if(saveGame(false)===false)throw Error();rt.paused=false;}catch{notice('Écriture toujours refusée.');}dialogue(id);})});
  }else if(id.startsWith('source:')){
   const key=id.split(':')[1],o=M.MAIL[key],m=l.mail[key];title=o.name;
   text='Au dos du pli : « '+o.body+' »\n\nBague '+o.ring+' : '+o.home+'. Le pigeon '+o.bird+' est attaché à ce colombier. Changer le texte ne lui apprend pas une autre destination.';
   if(!l.notes.includes(key))add('Relever la bague et son colombier.','read',key);
   if(m.phase==='source'){
    for(const b of M.BIRDS)add('Fixer le pli au tube de '+b+'.','load',key,b);
    add('Prendre le pli dans la sacoche · à pied.','take',key);
   }
   if(m.phase==='loaded'){add('Ouvrir la cage de départ.','release',key,null,true);add('Retirer le pli avant départ.','unload',key);}
   text+='\n\nUn pli chargé n’est pas encore parti. Le retour du pigeon ne remplace pas le reçu signé par l’habitant.';
  }else if(id.startsWith('loft:')){
   const key=id.split(':')[1];title=M.MAIL[key].home;text='La trappe d’arrivée est distincte de la cage du guichet. Le courrier n’est lâché qu’après ouverture du bon colombier. L’ouverture ne libère ni vivres ni objets du joueur.';
   if(!l.hatches[key])add('Ouvrir la trappe d’arrivée.','hatch',key);
  }else if(M.IDS.includes(id)){
   const o=M.MAIL[id],m=l.mail[id];title=o.recipient;
   text=id==='soins'?'« Le numéro du dispensaire est resté sur une porte détruite. Moi, je suis encore ici. Ce qui m’importe, c’est de savoir qui attend et ce que je peux réellement lui offrir. »':'« Mon adresse ? La conduite qui fuit, puis l’escalier. Ça n’entre jamais dans leurs cases. Je ne commande pas un réseau entier : une poignée suffira pour cette réparation. »';
   if(['arrived','carried'].includes(m.phase))ch.push({text:'Remettre le pli et demander une réponse.',onChoose:guard(r=>{if(act('receive',id,null,r))openDialogue(speaker(o.recipient,'RÉPONSE AU PORTEUR','PR'),o.reply,[{text:'Conserver le reçu signé.',onChoose:closeDialogue}]);})});
   if(m.phase==='received')text+='\n\n'+o.reply;
  }else return false;
  ch.push(back());openDialogue(speaker(title,'POSTE RESTANTE · COLOMBIERS','PR'),text+'\n\n'+M.briefing(l),ch);return true;
 }
 function visuals(w){if(!w?.v074Pigeons)return;const l=state.v074Pigeons;
  for(const d of w.staticDraws){if(d.p74CageRoof){const m=l.mail[d.p74CageRoof],p=P['source:'+d.p74CageRoof],departed=m.method==='oiseau'&&['flying','arrived','received'].includes(m.phase);d.pos=[p[0]-(departed?1:0),departed?3.32:2.35,p[2]];d.scale=departed?[.04,2,1.5]:[2,.04,1.5];}if(d.p74Hatch)d.hidden=l.hatches[d.p74Hatch];if(d.p74Envelope)d.hidden=!['source','loaded'].includes(l.mail[d.p74Envelope].phase);if(d.p74Receipt)d.hidden=l.mail[d.p74Receipt].phase!=='received';if(d.p74Panel)d.hidden=l.policy!=='annonce';}
  for(const c of w.colliders)if(c.p74Hatch)c.disabled=l.hatches[c.p74Hatch];
 }
 function build(){
  rt.paused=false;rt.error=null;const w=createWorld(V042_INSTANCE_ZONE,'La cour des colombiers','POSTE RESTANTE · LA BONNE ADRESSE',{skyTop:[75,112,139],skyBottom:[184,170,129],fog:[.46,.50,.43],daylight:.85,wind:.1,indoor:false});
  w.v074Pigeons=true;w.bounds=[-26,26,-24,30];w.spawn=[0,1.65,25];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE;
  const stone=[.57,.54,.43],wood=[.43,.31,.20],metal=[.27,.34,.33];
  const box=(p,s,c=stone,solid=true)=>{const d=addBox(w,p,s,c);if(solid)addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});return d;};
  box([0,-.15,3],[52,.3,54],stone,false);addFloorZone(w,0,3,52,54,0);
  for(const [x,z,sx,sz]of [[-25.5,3,.4,54],[25.5,3,.4,54],[0,-23.5,51,.4]])box([x,1.1,z],[sx,2.2,sz]);
  // Upper terrace belongs to this fictional courtyard, not to an IGN building.
  box([17,3.02,-14],[16,.36,20],stone,false);addFloorZone(w,17,-14,16,20,3.2,{priority:1});addCollider(w,17,-14,16,20,{minY:2.84,maxY:3.1});
  v021Stairs(w,20,4,16,3.8,3.2);
  for(const [x,z,sx,sz]of [[12,-4,6,.2],[24,-14,.2,18],[9,-14,.2,20]])box([x,3.85,z],[sx,1.3,sz],metal);
  for(const x of [10,24])box([x,1.4,-14],[.45,2.8,.45],metal);
  box([0,.6,20],[8,1.2,1.1],wood);box([0,3.3,22],[10,.15,6],metal,false);
  for(const x of [-4.8,4.8])box([x,1.65,24],[.15,3.3,.15],metal);
  // Houses identify recipients; doors are background, the accessible path stays outside.
  box([-20,1.7,-21],[10,3.4,2.4],[.58,.64,.55]);box([18,4.8,-21],[12,3.2,2.4],[.64,.49,.36]);
  for(const id of M.IDS){
   const o=M.MAIL[id],p=P['source:'+id],home=P['loft:'+id];
   box([p[0],.6,p[2]],[2,1.2,1.5],wood);box([p[0],1.24,p[2]],[2.1,.08,1.6],[.65,.57,.38],false);
   // Cage framework with no false collision around the scheduled take-off path.
   for(const dx of [-.9,.9])for(const dz of [-.65,.65])box([p[0]+dx,1.8,p[2]+dz],[.04,1.1,.04],metal,false);
   const lid=box([p[0],2.35,p[2]],[2,.04,1.5],metal,false);lid.p74CageRoof=id;
   const env=box([p[0]+.55,1.32,p[2]+.25],[.42,.035,.27],[.86,.79,.56],false);env.p74Envelope=id;
   // Each loft is a wall-mounted open landing, with its own movable front shutter.
   box([home[0],home[1]+.58,home[2]],[2,1.16,1.1],wood);box([home[0],home[1]+1.25,home[2]],[2.3,.16,1.6],[.45,.48,.40],false);
   for(const dx of [-1,1])box([home[0]+dx,home[1]+1.85,home[2]-.35],[.12,1.15,.7],wood);
   box([home[0],home[1]+2.5,home[2]-.35],[2.2,.16,.85],wood);
   const shutter=box([home[0],home[1]+1.85,home[2]+.36],[1.9,1.15,.10],metal,false);shutter.p74Hatch=id;
   const col=addCollider(w,home[0],home[2]+.36,1.9,.10,{minY:home[1]+1.3,maxY:home[1]+2.43});col.p74Hatch=id;
   for(const [point,label]of [['source:'+id,'Préparer le pli · '+o.name],['loft:'+id,'Examiner la trappe · '+o.home]]){const q=P[point];addInteract(w,'p74:'+point,[q[0],q[1]+1.25,q[2]+.8],label,()=>dialogue(point),{kind:'quest',priority:5,radius:3.2,condition:()=>!blocked()&&near(point)});}
   const receiver=P[id];box([receiver[0]+1,receiver[1]+.6,receiver[2]],[.9,1.2,.7],wood);
   const receipt=box([receiver[0]+1,receiver[1]+1.23,receiver[2]],[.65,.03,.40],[.87,.81,.62],false);receipt.p74Receipt=id;
   addHumanNPC(w,'p74:'+id,o.recipient,id==='soins'?'Relais de soins':'Atelier des pompes',receiver,id==='soins'?[.55,.57,.43]:[.32,.40,.48],{yaw:Math.PI});
  }
  addHumanNPC(w,'p74:mirette','Mirette Valon','Poste Restante',P.mirette,[.62,.49,.25],{yaw:Math.PI});
  box([-4,1.3,18],[.15,2.6,.15],metal);const board=box([-4,2.2,18],[2,.9,.12],[.74,.70,.51],false);board.p74Panel=true;
  if(typeof v021Sign==='function'){const first=w.staticDraws.length;v021Sign(w,-4,2.22,18.10,'2 PLIS RECUS',.032);for(const d of w.staticDraws.slice(first))d.p74Panel=true;}
  // Ordinary lived-in objects; none claims to be a surveyed architectural feature.
  for(const x of [-22,-18]){box([x,.28,3],[2.5,.56,.9],wood);box([x,1.0,3.35],[2.5,.25,.14],wood);}
  for(const [x,y,z]of [[-23,0,-18],[-12,0,-20],[11,3.2,-21],[23,3.2,-21]]){box([x,y+.25,z],[.9,.5,.8],[.56,.38,.25]);box([x,y+.70,z],[.65,.6,.60],[.35,.45,.26],false);}
  for(let i=0;i<3;i++){box([-3+i*1.1,.73,20.62],[.65,.4,.4],[[.35,.45,.52],[.60,.43,.26],[.42,.49,.32]][i],false);box([-3+i*1.1,.77,20.84],[.38,.035,.02],[.13,.17,.16],false);}

  if(typeof v021Sign==='function'){v021Sign(w,0,2.7,19.4,'POSTE RESTANTE',.07);v021Sign(w,-20,2.6,-19.7,'SOINS / A-17',.055);v021Sign(w,18,5.8,-19.7,'POMPES / B-04',.055);v021Sign(w,20,1.3,12,'PASSERELLE',.045);}
  addInteract(w,'p74:sortie',[0,1.25,27.8],'Retourner au relais',()=>!blocked()&&near('sortie')&&v042ExitInstance(),{kind:'door',priority:5,radius:3.2});
  visuals(w);return w;
 }
 const buildBase=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE?build():buildBase(...arguments);};
 const ground=groundHeightAt;groundHeightAt=function(x,z,feet=0){if(!local())return ground(...arguments);const a=world.floorZones.filter(f=>x>=f.minX&&x<=f.maxX&&z>=f.minZ&&z<=f.maxZ).map(f=>floorZoneHeight(f,x,z)).filter(h=>h<=feet+.60);return a.length?Math.max(...a):0;};
 const talk=talkToNPC;talkToNPC=function(id){return typeof id==='string'&&id.startsWith('p74:')?dialogue(id.slice(4)):talk(...arguments);};
 const claim=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE?false:claim(...arguments);};
 // The postal pigeons are neutral transport actors, not enemies or loot sources.
 // Their bespoke low-poly bodies and two wing poses are rendered here.
 function birdDraw(id,t){
  const l=state.v074Pigeons,m=l.mail[id],p=m.pos.map(n=>n/1000),fly=m.phase==='flying';
  const out=[],target=fly?M.ROUTES[id][m.waypoint]:[m.pos[0],m.pos[1],m.pos[2]-1000],yaw=Math.atan2(target[0]-m.pos[0],-(target[2]-m.pos[2])),c=Math.cos(yaw),s=Math.sin(yaw);
  const part=(mesh,off,size,color,emissive=0)=>out.push({mesh,pos:[p[0]+off[0]*c+off[2]*s,p[1]+off[1],p[2]-off[0]*s+off[2]*c],scale:size,color,rotY:yaw,emissive});
  const grey=id==='soins'?[.42,.46,.50]:[.51,.48,.44],ring=id==='soins'?[.20,.55,.70]:[.70,.33,.20];
  part('sphere',[0,.26,0],[.58,.55,.78],grey);part('sphere',[0,.59,-.28],[.33,.38,.35],[.34,.39,.41]);
  part('sphere',[0,.43,-.20],[.37,.38,.34],[.29,.46,.37]);part('cube',[0,.58,-.51],[.14,.10,.18],[.68,.63,.49]);
  for(const side of [-1,1]){part('sphere',[side*.15,.65,-.34],[.065,.065,.065],[.85,.46,.17]);part('sphere',[side*.175,.65,-.35],[.035,.035,.035],[.06,.07,.05]);
   const flap=fly&&!settings.reduceMotion?Math.sin(t*10)*.13:0;part('cube',[side*(fly?.52:.29),.25+flap,.02],[fly?.67:.13,.08,.56],grey);part('cube',[side*(fly?.52:.32),.28+flap,.12],[fly?.60:.12,.025,.075],[.18,.21,.23]);
   part('cube',[side*.15,-.015,.02],[.06,.16,.06],[.51,.30,.25]);part('cube',[side*.15,-.08,-.08],[.09,.04,.22],[.51,.30,.25]);}
  part('cube',[0,.15,.46],[.37,.07,.42],[.28,.30,.32]);part('cube',[-.15,-.01,.02],[.09,.06,.10],ring);
  if(m.method==='oiseau'&&!['source','received'].includes(m.phase))part('cylinder',[.16,.03,.10],[.11,.28,.11],[.73,.66,.48]);
  return out;
 }
 const draws=collectDraws;collectDraws=function(t){const out=draws(...arguments);if(local())for(const id of M.IDS)out.push(...birdDraw(id,Number.isFinite(t)?t:0));return out;};
 function airClear(id,from,to){const n=Math.max(1,Math.ceil(Math.hypot(...to.map((v,i)=>v-from[i]))/150));for(let i=1;i<=n;i++){const p=to.map((v,j)=>(from[j]+(v-from[j])*i/n)/1000);if(world.colliders.some(c=>!c.disabled&&p[1]+.75>(c.minY??0)&&p[1]-.12<(c.maxY??Infinity)&&v017ColliderHit(c,p[0],p[2],.32)))return false;}return true;}
 const update=updateEnemies;updateEnemies=function(dt){
  if(!local())return update(...arguments);
  if(!gameStarted||mode!=='PLAYING'||zoneTransitioning||V046.busy||V047.pending||V046.lab||!(state.player.hp>0)||rt.busy||rt.paused||!Number.isFinite(dt)||dt<=0)return;
  const owner=state,w=world;let step;
  try{step=M.advance(owner.v074Pigeons,Math.max(1,Math.round(Math.min(.2,dt)*1000)),{canMove:airClear});}catch(e){rt.paused=true;rt.error=e.message;return notice(e.message);}
  if(step.events.length){const before=copy(owner);try{owner.v074Pigeons=step.ledger;if(state!==owner||world!==w||saveGame(false)===false)throw Error('Étape du vol non sauvegardée.');}catch(e){restore(owner,before);rt.paused=true;return notice(e.message+' Le vol est en pause ; contactez Mirette.');}updateQuestUI(false);}
  else owner.v074Pigeons=step.ledger;
  visuals(w);inCombat=false;
 };
 function relayNear(){const def=v042Site(M.RELAY),p=state.player.pos;return !!def&&world?.v046&&world.geoMacro&&!state.v042?.activeInterior&&!world.v050CityInterior&&settings.geoFalloutLayer&&v042SiteDiscovered(def)&&!v050TravelNearbyThreat(world,p)&&world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===M.RELAY&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 function enter(){if(blocked()||!relayNear())return false;const owner=state,w=world,before=copy(owner),maps={active:new Map(V042_RUNTIME.active),npc:new Map(V042_RUNTIME.npcData),nearest:V042_RUNTIME.nearest,instance:V042_RUNTIME.instanceSite,retained:V048.retained},save=saveGame;let wrote=false;saveGame=function(...a){const r=save(...a);if(r===false)throw Error('Départ non sauvegardé.');wrote=true;return r;};try{if(!v042EnterSite(M.SITE))throw Error('Départ interrompu.');return true;}catch(e){restore(owner,before);world=w;V042_RUNTIME.active=maps.active;V042_RUNTIME.npcData=maps.npc;V042_RUNTIME.nearest=maps.nearest;V042_RUNTIME.instanceSite=maps.instance;V048.retained=maps.retained;v049Own(w);if(wrote){try{save(false);}catch{}}return notice(e.message);}finally{saveGame=save;}}
 const relayTalk=v042TalkNPC;v042TalkNPC=function(id){if(blocked()||V042_RUNTIME.npcData.get(id)?.siteId!==M.RELAY||!relayNear())return relayTalk(...arguments);const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text:'Poste Restante · La bonne adresse',onChoose:guard(()=>openDialogue(speaker('Relais de Saint-Charles','DEUX PLIS, DEUX COLOMBIERS','PR'),'Mirette attend un porteur pour sa cour de correspondance. Les colombiers reçoivent les plis des habitants voisins ; le passage à pied reste ouvert.',[{text:'Rejoindre la cour des colombiers.',onChoose:guard(enter)},back()]))},...(ch||[]).slice(-1)],...rest);};try{return relayTalk(...arguments);}finally{openDialogue=old;}};
 function track(){if(blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=M.RELAY;try{if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Repère non sauvegardé.');}updateQuestUI(true);return true;}
 V027_SUBS.data.pigeons='PIGEONS · POSTE RESTANTE';const data=v027Data;v027Data=function(c){if(V027.sub!=='pigeons')return data(...arguments);const l=state.v074Pigeons,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">LA BONNE ADRESSE</p><h2>Pigeons de Poste Restante</h2><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre Saint-Charles','p74:track')+M.IDS.map(id=>'<section class="v046-notice"><h3>'+esc(M.MAIL[id].name)+'</h3><p>'+esc(M.MAIL[id].recipient+' · '+M.MAIL[id].home+' · bague '+M.MAIL[id].ring)+'</p><p>'+esc({source:'Au guichet',loaded:'Chargé, pas envoyé',flying:'En vol',arrived:'Au colombier, reçu à demander',carried:'Dans la sacoche',received:'Réponse signée'}[l.mail[id].phase])+'</p>'+(l.mail[id].phase==='received'?'<p>'+esc(M.MAIL[id].reply)+'</p>':'')+'</section>').join('')+'<p>La passerelle est libre. Les deux oiseaux reviennent à leur propre colombier ; ils ne lisent pas les adresses et ne pilotent pas une poste régionale autonome.</p></div>';};
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='p74:track'?v027CanAct()&&track():dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v074Pigeons;return rows(...arguments).concat(l.opened?[{id:'p74:quest',name:'LA BONNE ADRESSE',stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:M.IDS.map(id=>[M.MAIL[id].name,l.mail[id].phase==='received']).concat([['Réponses remises à Mirette',l.finished]]),source:'Poste Restante',badge:l.finished?'✓':'',hint:'Mirette · Saint-Charles'}]:[]);};
 const oldTrack=v027Track;v027Track=function(id){return id==='p74:quest'?track():oldTrack(...arguments);};
 function next(){const l=state.v074Pigeons;if(!l.opened||M.IDS.every(id=>l.mail[id].phase==='received'))return'mirette';const id=M.IDS.find(id=>l.mail[id].phase!=='received'),p=l.mail[id].phase;if(['arrived','carried'].includes(p))return id;if(p==='loaded'&&!l.hatches[id])return'loft:'+id;return'source:'+id;}
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return marker(...arguments);const id=next(),p=P[id];return{zone:world.id,pos:[p[0],p[1]+1.25,p[2]+.8],label:'La bonne adresse · '+(id==='mirette'?'Mirette':(M.MAIL[id]?.recipient||(id.startsWith('loft')?'Colombier':'Guichet')))};};
 const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local())return ui(...arguments);$('questTitle').textContent='LA BONNE ADRESSE';$('questObjective').textContent=M.briefing(state.v074Pigeons);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='LA BONNE ADRESSE';f.querySelector('p').textContent=M.briefing(state.v074Pigeons);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.pigeons={name:'Poste Restante — la bonne adresse',freq:'74.2',hint:'Un départ ne vaut pas réception',available:()=>state.v074Pigeons.opened,text:()=>state.v074Pigeons.finished?(state.v074Pigeons.policy==='annonce'?'Deux plis reçus. Aucun nom ni adresse ne figure au bulletin.':'Tournée close. Les réponses sont conservées sous pli.'):M.briefing(state.v074Pigeons)};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v074PigeonsInfo:()=>({ledger:copy(state.v074Pigeons),local:local(),points:copy(P),paused:rt.paused,error:rt.error,birdDraws:local()?M.IDS.map(id=>({id,count:birdDraw(id,0).length})):[]}),v074PigeonsOpen:()=>v027Open('data','pigeons'),v074PigeonsAction:act});};
}
