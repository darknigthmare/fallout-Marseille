/* Consigne portuaire: authored overlay; flight corridors and moving baskets.
 * Existing regional gabian rig and native combat. No changes to IGN geometry. */
if(typeof baseState==='function'&&typeof MistralGabians!=='undefined'){
 const M=MistralGabians,copy=x=>JSON.parse(JSON.stringify(x));
 const P={nora:[-8,0,23],registre:[8,0,23],sortie:[0,0,27],'lure:filets':[-24,0,-19],'lure:tole':[24,0,-19],'lower:filets':[-20,0,3],'lower:tole':[20,0,3],'basket:filets':[-10,0,-13],'basket:tole':[10,0,-13]};
 const rt={busy:false,paused:false,error:null,blockedBaskets:[]};
 const anchor=v042Site(M.RELAY);
 if(anchor&&!v042Site(M.SITE)){const s={...copy(anchor),id:M.SITE,name:'La consigne des gabians',kind:'interior',interior:'gabians',description:'Cour de consigne fictionnelle : objets personnels emportés dans les paniers, gabians et palans.',safe:true,visitable:true,unique:true,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],enemyRadius:0,rewardCaps:0,rewardXP:0,respawnHours:0,provenance:{kind:'authored-fiction',anchorId:M.RELAY}};V042_CATALOG.push(s);V042_SITE_BY_ID[s.id]=s;V042_SITES_BY_MACRO[s.macro].push(s);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[s.macro]++;}
 const base=baseState;baseState=function(...args){const s=base(...args);s.v073Gabians=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(...arguments);s.v073Gabians=M.migrate(raw?.v073Gabians);return s;};state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v073Gabians&&state.v042?.activeInterior===M.SITE,managed=e=>local()&&e?.g73Id&&world.enemies.includes(e);
 const notice=t=>{V027.message=t;toast(t,'bad');return false;};
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc géographique sans progression.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':!onGround?'Rejoignez le sol.':null;}
 function near(id){const p=P[id];return local()&&p&&Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.2&&Math.abs(state.player.pos[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],1.25,p[2]+1.4]);}
 function restore(owner,before){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}
 function commit(next,caption){if(rt.busy)return false;const owner=state,w=world,before=copy(owner);rt.busy=true;try{owner.v073Gabians=next.v073Gabians;owner.player.caps=next.player.caps;owner.inventory=next.inventory;if(state!==owner||world!==w||saveGame(false)===false)throw Error('Consigne non sauvegardée.');}catch(err){restore(owner,before);return notice(err.message+' Modification annulée.');}finally{rt.busy=false;if(state===owner&&world===w)visuals(w);}updateQuestUI(true);updateHUD();if(caption)toast(caption,'good');return true;}
 function act(type,id,method,revision){const point=M.actionPoint(type,id);let next;try{next=M.act(state,{type,id,method},{blocked:blocked(),local:local(),near:near(point),point,revision});}catch(err){return notice(err.message);}return commit(next,type==='finish'?'Trois objets rendus · 45 capsules, une fois.':type==='return'?'Objet confié à Nora.':'Progression de la consigne sauvegardée.');}
 function guard(fn){const owner=state,w=world,rev=state.v073Gabians.revision;return()=>state===owner&&world===w&&rev===state.v073Gabians.revision?fn(rev):notice('Conversation périmée.');}
 const back=()=>({text:'Revenir.',onChoose:closeDialogue});
 function dialogue(id){
  if(blocked()||!near(id))return false;const l=state.v073Gabians,ch=[];let title,text;
  const add=(label,type,key,method,close=false)=>ch.push({text:label,onChoose:guard(rev=>{const ok=act(type,key,method,rev);if(ok&&close)closeDialogue();else dialogue(id);})});
  if(id==='nora'){
   title='Nora Ferrand';text='« Objets trouvés, objets perdus… Il manque une colonne : objets qui s’envolent. J’ai laissé les plateaux ouverts dix minutes. Les gabians ont pris ce qui brillait, et moi je dois expliquer à Mina où est sa bague. Les paniers suspendus étaient à nous avant leurs nids. On peut les descendre doucement. Les restes de poisson sont au fond, pas dans votre casse-croûte. »';
   if(!l.opened)add('Aider Nora à retrouver les objets.','open');
   for(const [key,o]of Object.entries(M.OBJECTS))if(l.objects[key]==='bag')ch.push({text:'Rendre : '+o.name+'.',onChoose:guard(rev=>{if(act('return',key,null,rev))openDialogue(speaker('Nora Ferrand','LA CONSIGNE','NF'),'« '+o.text+' Merci. Je le range ici pour '+o.owner+'. »',[{text:'Les autres objets.',onChoose:guard(()=>dialogue('nora'))},back()]);})});
   if(l.opened&&!l.finished&&Object.values(l.objects).every(v=>v==='returned'))add('Faire le point avec Nora · 45 capsules.','finish');
   if(rt.paused)ch.push({text:'Retenter la sauvegarde de la consigne.',onChoose:guard(()=>{try{if(saveGame(false)===false)throw Error();rt.paused=false;}catch{notice('Écriture toujours refusée.');}dialogue(id);})});
  }else if(id==='registre'){
   title='Le registre aux coins cornés';text=Object.values(M.OBJECTS).map(o=>o.name+' — '+o.owner+'\n'+o.text).join('\n\n')+'\n\nAu crayon : « Fermer les plateaux. Les oiseaux ne lisent pas les tickets. — Nora »';if(!l.manifest)add('Noter à qui appartiennent les objets.','manifest');
  }else if(id.startsWith('lure:')){
   const key=id.split(':')[1];title='Restes de poisson · '+(key==='filets'?'filets':'tôle');text='Un petit lot de déchets de poisson, réservé par Nora. Ce point est à l’écart des objets et du passage. Le gabian doit réellement y parvenir avant que vous touchiez au palan.';if(!l.lures[key]&&l.birds[key].hp>0)add('Déposer les restes à l’écart.','lure',key,null,true);
  }else if(id.startsWith('lower:')){
   const key=id.split(':')[1],p=l.platforms[key];title='Palan du panier · '+(key==='filets'?'filets':'tôle');text='Le frein retient le panier. Une descente lente laisse le nid entier. Restez hors du dessous du panier : le mouvement s’arrête si quelqu’un passe dans son volume.';if(!p.method){add('Descendre à la manivelle · gratuit.','lower',key,'manuel',true);add('Régler le réducteur · INT 5 + 1 ferraille.','lower',key,'technique',true);}else text+='\n\nDescente : '+Math.round(p.drop/M.DROP*100)+' %.';
  }else if(id.startsWith('basket:')){
   const key=id.split(':')[1];title='Panier récupéré · '+(key==='filets'?'filets':'tôle');text=l.platforms[key].drop===M.DROP?'Les objets sont pris entre les liens du panier. Vous pouvez les retirer un par un sans arracher le nid.':'Le panier reste trop haut. Utilisez son palan après avoir éloigné le gabian.';for(const [oid,o]of Object.entries(M.OBJECTS))if(o.nest===key&&l.objects[oid]==='nest')add('Prendre : '+o.name+'.','take',oid);
  }else return false;ch.push(back());openDialogue(speaker(title,id==='nora'?'CONSIGNE DU VIEUX-PORT':'LES OBJETS TROUVÉS','NF'),text+'\n\n'+M.briefing(l),ch);return true;
 }
 function rig(e,t=0){const a=state.v073Gabians.birds[e.g73Id];return MistralRegionalBestiary.rig(e,'gabianBombardier',t,{reduceMotion:settings.reduceMotion,moving:a.phase==='guard'||a.phase==='lure',windup:a.wind?a.wind.elapsed/1100:0});}
 function visuals(w){if(!w?.v073Gabians)return;const l=state.v073Gabians;
  for(const e of w.enemies){if(!e.g73Id)continue;const a=l.birds[e.g73Id],old=e.pos;e.pos=a.pos.map(n=>n/1000);if(old&&Math.hypot(e.pos[0]-old[0],e.pos[2]-old[2])>.001)e.yaw=Math.atan2(e.pos[0]-old[0],-(e.pos[2]-old[2]));e.home=e.pos.slice();e.health=a.hp/100;e.maxHealth=M.HP/100;e.armDamage=a.wings/100;e.legDamage=a.legs/100;e.alive=a.hp>0;e.alerted=!!a.wind;e.state=a.phase==='guard'?'patrol':a.phase==='lure'?'retreat':'idle';e.status={...(e.status||{}),burning:a.burn/1000,slow:a.slow/1000};}
  for(const d of w.staticDraws){if(d.g73Basket)d.pos[1]=d.g73Y-l.platforms[d.g73Basket].drop/1000;if(d.g73Object)d.hidden=l.objects[d.g73Object]!=='nest';if(d.g73Returned)d.hidden=l.objects[d.g73Returned]!=='returned';if(d.g73Food)d.hidden=!l.lures[d.g73Food];if(d.g73Rope){const y=4.2-l.platforms[d.g73Rope].drop/1000;d.pos[1]=(6+y)/2;d.scale[1]=6-y;}}
  for(const c of w.colliders)if(c.g73Basket){const y=4.2-l.platforms[c.g73Basket].drop/1000;c.minY=y-.16;c.maxY=y+.42;}
 }
 function build(){
  rt.paused=false;rt.error=null;rt.blockedBaskets=[];
  const w=createWorld(V042_INSTANCE_ZONE,'La consigne des gabians','LES OBJETS TROUVÉS',{skyTop:[69,104,115],skyBottom:[166,156,119],fog:[.41,.47,.43],daylight:.8,wind:.18,indoor:false});w.v073Gabians=true;w.bounds=[-28,28,-26,30];w.spawn=[0,1.65,25];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE;
  const stone=[.45,.44,.35],wood=[.43,.31,.18],steel=[.22,.29,.29];
  function box(pos,size,color=stone,solid=true){const d=addBox(w,pos,size,color);if(solid)addCollider(w,pos[0],pos[2],size[0],size[2],{minY:pos[1]-size[1]/2,maxY:pos[1]+size[1]/2});return d;}
  box([0,-.15,2],[56,.3,56],stone,false);addFloorZone(w,0,2,56,56,0);
  box([0,-.3,-42],[120,.15,34],[.19,.33,.35],false); // Scenic water, outside the authored court, not a surveyed coast.
  for(const [x,z,sx,sz]of [[-27.6,2,.6,56],[27.6,2,.6,56],[0,-25.5,56,.6]])box([x,.85,z],[sx,1.7,sz]);
  for(const z of [-22,0,19])box([0,.015,z],[53,.025,.12],[.68,.61,.35],false);
  box([-8,3.4,23],[12,.18,8],steel);for(const x of [-13.5,-2.5])box([x,1.7,25],[.16,3.4,.16],steel);
  box([-8,.6,21],[10,1.2,1.1],wood);box([-8,1.23,21],[10.2,.08,1.2],[.63,.52,.31],false);
  for(const [x,z,sx,sz]of [[0,4,6,2],[0,-7,3,3]])box([x,1,z],[sx,2,sz],wood);
  for(const id of M.IDS){const side=M.BIRDS[id].side,x=side*10,z=-13;
   for(const dx of [-2.4,2.4])box([x+dx,3,z],[.25,6,.25],steel);box([x,6,z],[5.2,.25,.35],steel);
   for(const dx of [-1.3,1.3]){const d=box([x+dx,5.1,z],[.035,1.8,.035],[.54,.49,.36],false);d.g73Rope=id;}
   const basket=box([x,4.2,z],[3.4,.3,2.6],wood,false);basket.g73Basket=id;basket.g73Y=4.2;
   const col=addCollider(w,x,z,3.4,2.6,{minY:4.04,maxY:4.62});col.g73Basket=id;
   for(const dz of [-1.15,1.15]){const d=box([x,4.48,z+dz],[3.4,.3,.15],wood,false);d.g73Basket=id;d.g73Y=4.48;}
   for(let n=0;n<7;n++){const d=box([x+(n-3)*.26,4.4,z+(n%2?-.3:.3)],[.1,.08,1.45],[.37,.33,.21],false);d.g73Basket=id;d.g73Y=4.4;}
   const food=box([side*22,.22,-20],[.65,.12,.65],[.51,.41,.29],false);food.g73Food=id;
   const a=state.v073Gabians.birds[id],e=addEnemy(w,'g73:'+id,'bloatfly',M.BIRDS[id].name,a.pos.map(n=>n/1000),{health:M.HP/100,damage:8,range:10,speed:3,armor:.05,loot:{}});if(e){e.g73Id=id;e.yaw=0;}
  }
  // Distinct salvage silhouettes instead of three interchangeable gold blocks.
  function objectShape(id,x,y,z,returned=false){
   const gold=[.78,.63,.28],silver=[.68,.69,.61];
   function part(pos,size,color=gold){const d=box(pos,size,color,false);if(returned)d.g73Returned=id;else{d.g73Object=id;d.g73Basket=M.OBJECTS[id].nest;d.g73Y=pos[1];}return d;}
   function ring(cx,cz,radius,color){for(let n=0;n<12;n++){const a=n*Math.PI/6;part([cx+Math.cos(a)*radius,y,cz+Math.sin(a)*radius],[.07,.07,.07],color);}}
   if(id==='clef'){ring(x,z-.19,.13,gold);part([x,y,z+.14],[.07,.07,.44]);for(const dz of [.24,.34])part([x+.065,y,z+dz],[.14,.07,.065]);}
   else if(id==='bague')ring(x,z,.18,silver);
   else{part([x,y,z],[.22,.17,.24],silver);part([x,y,z+.2],[.11,.09,.22],silver);part([x,y+.091,z-.02],[.12,.012,.085],[.18,.23,.22]);ring(x,z-.24,.09,silver);}
  }
  let objIndex=0;for(const [id,o]of Object.entries(M.OBJECTS)){
   const x=M.BIRDS[o.nest].side*10+(id==='clef'?-.5:id==='bague'?.5:0);objectShape(id,x,4.64,-12.7);objectShape(id,-11+objIndex*2,1.38,21,true);objIndex++;
  }
  for(const [id,p]of Object.entries(P)){if(['nora','sortie'].includes(id))continue;
   if(!id.startsWith('basket:')){box([p[0],.5,p[2]],[1.2,1,.7],steel);box([p[0],1.06,p[2]],[1.25,.12,.75],[.63,.52,.31],false);}
   const label=id==='registre'?'Lire le registre':id.startsWith('lure:')?'Restes de poisson réservés':id.startsWith('lower:')?'Actionner le palan':'Examiner le panier';
   addInteract(w,'g73:'+id,[p[0],1.25,p[2]+1.4],label,()=>dialogue(id),{radius:3.2,kind:'quest',priority:5,condition:()=>!blocked()&&near(id)});
  }
  addHumanNPC(w,'g73:nora','Nora Ferrand','Gardienne de la consigne',P.nora,[.33,.43,.40],{yaw:Math.PI});
  addInteract(w,'g73:sortie',[0,1.25,28.4],'Retourner au Vieux-Port',()=>!blocked()&&near('sortie')&&v042ExitInstance(),{radius:3.2,kind:'door',priority:5});
  if(typeof v021Sign==='function'){v021Sign(w,-8,2.8,21.7,'OBJETS TROUVES',.075);v021Sign(w,0,2.5,29,'RETOUR / VIEUX-PORT',.065);for(const id of M.IDS)v021Sign(w,M.BIRDS[id].side*20,2.3,2.8,'PALAN / HORS CHARGE',.045);}
  w.levelRoutes=[{id:'g73-side',points:[[0,0,25],[25.5,0,25],[25.5,0,-21]]}];visuals(w);return w;
 }
 const buildBase=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE?build():buildBase(...arguments);};
 const talk=talkToNPC;talkToNPC=function(id){return id==='g73:nora'?dialogue('nora'):talk(...arguments);};
 const claim=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE?false:claim(...arguments);};
 const oldRig=v025Rig;v025Rig=function(e,t=gameClock){return managed(e)?rig(e,V025.active?V025.poseTime:t):oldRig(...arguments);};
 const oldDamage=damageEnemy;damageEnemy=function(e,amount,part='body',crit=false,pierce=0){if(!managed(e))return oldDamage(...arguments);if(!e.alive||rt.busy||!gameStarted||V046.lab||zoneTransitioning||!(state.player.hp>0))return;try{return commit({...state,v073Gabians:M.hit(state.v073Gabians,e.g73Id,amount,part,pierce)});}catch(err){return notice(err.message);}};
 const oldKill=killEnemy;killEnemy=function(e){return managed(e)?damageEnemy(e,M.HP,'body',false,1):oldKill(...arguments);};
 const statusBase=applyEnemyStatus;applyEnemyStatus=function(e,type,seconds){if(!managed(e)||!['burning','slow'].includes(type))return statusBase(...arguments);try{return commit({...state,v073Gabians:M.effect(state.v073Gabians,e.g73Id,type,seconds)});}catch(err){return notice(err.message);}};
 const companion=updateCompanion;updateCompanion=function(...args){if(!local())return companion(...args);const w=world,all=w.enemies;w.enemies=all.filter(e=>!e.g73Id||!state.v073Gabians.lures[e.g73Id]);try{return companion(...args);}finally{w.enemies=all;}};
 function airClear(id,from,to){const steps=Math.max(1,Math.ceil(Math.hypot(...to.map((n,i)=>n-from[i]))/200));for(let i=1;i<=steps;i++){const p=to.map((n,j)=>(from[j]+(n-from[j])*i/steps)/1000);if(world.colliders.some(c=>!c.disabled&&p[1]+1.35>(Number.isFinite(c.minY)?c.minY:0)&&p[1]+.1<(Number.isFinite(c.maxY)?c.maxY:Infinity)&&v017ColliderHit(c,p[0],p[2],.96)))return false;}return true;}
 function platformClear(id,oldDrop,newDrop){const p=P['basket:'+id],min=4.2-newDrop/1000-.16,max=4.2-oldDrop/1000+.42;
  const people=[{pos:[state.player.pos[0],state.player.pos[1]-1.65,state.player.pos[2]],height:1.85},...world.npcs.filter(n=>n.alive!==false).map(n=>({pos:n.pos,height:1.8}))];
  const clear=!people.some(n=>Math.abs(n.pos[0]-p[0])<2.1&&Math.abs(n.pos[2]-p[2])<1.7&&n.pos[1]<max&&n.pos[1]+n.height>min);if(!clear)rt.blockedBaskets.push(id);return clear;
 }
 function hitPlayer(event){const p=state.player.pos,feet=p[1]-1.65,t=event.target;if(Math.hypot(p[0]-t[0],p[2]-t[2])<=.95&&feet<t[1]+1.55&&p[1]>t[1]-.2&&lineOfSight([t[0],t[1]+.12,t[2]],[p[0],feet+.7,p[2]]))hurtPlayer(event.damage,'Gabian · lâcher corrosif');}
 const enemiesBase=updateEnemies;updateEnemies=function(dt){
  if(!local())return enemiesBase(...arguments);
  if(!gameStarted||mode!=='PLAYING'||zoneTransitioning||V046.busy||V047.pending||V046.lab||!(state.player.hp>0)||rt.busy||rt.paused||!Number.isFinite(dt)||dt<=0)return;
  const owner=state,w=world,previous=owner.v073Gabians,targets={},p=owner.player.pos;
  for(const e of w.enemies)if(e.g73Id&&e.alive&&lineOfSight([e.pos[0],e.pos[1]+.5,e.pos[2]],p))targets[e.g73Id]=[Math.round(p[0]*1000),Math.max(0,Math.round((p[1]-1.65)*1000)),Math.round(p[2]*1000)];
  rt.blockedBaskets=[];let step;try{step=M.advance(previous,Math.max(1,Math.round(Math.min(.2,dt)*1000)),{targets,canMove:airClear,platformClear,projectileClear:(from,to)=>lineOfSight(from,to)});}catch(err){rt.paused=true;rt.error=err.message;notice(err.message);return;}
  if(step.events.length){const before=copy(owner),oldMode=mode,hadDeath=!!$('deathModal');
   try{owner.v073Gabians=step.ledger;for(const e of step.events)if(e.type==='impact')hitPlayer(e);if(state!==owner||world!==w||saveGame(false)===false)throw Error('Mouvement non sauvegardé.');}
   catch(err){restore(owner,before);mode=oldMode;if(!hadDeath)$('deathModal')?.remove();rt.paused=true;visuals(w);updateHUD();return notice(err.message+' Retentez auprès de Nora.');}
   for(const e of step.events)if(e.type==='warning')subtitle(M.BIRDS[e.id].name,'LÂCHER CORROSIF — quittez la zone visée.',1300);updateQuestUI(false);
  }else owner.v073Gabians=step.ledger;
  visuals(w);inCombat=M.IDS.some(id=>!!owner.v073Gabians.birds[id].wind||!!owner.v073Gabians.birds[id].shot);
 };
 const draws=collectDraws;collectDraws=function(t){const out=draws(...arguments);if(!local())return out;
  for(const e of world.enemies){if(!e.g73Id)continue;const a=state.v073Gabians.birds[e.g73Id];
   if(a.hp===0)for(const d of rig(e,0).draws)out.push({...d,pos:[d.pos[0],e.pos[1]+(d.pos[1]-e.pos[1])*.28,d.pos[2]],scale:[d.scale[0],d.scale[1]*.28,d.scale[2]],color:d.color.map(v=>v*.55)});
   if(a.shot)out.push({mesh:'sphere',pos:M.projectilePosition(a.shot),scale:[.18,.18,.18],color:[.48,.62,.24],yaw:0,emissive:.25});
   if(a.wind)out.push({mesh:'cylinder',pos:[a.wind.target[0]/1000,a.wind.target[1]/1000+.03,a.wind.target[2]/1000],scale:[1.9,.035,1.9],color:[.72,.47,.18],yaw:0,emissive:.2});
  }return out;
 };
 function relayNear(){const site=v042Site(M.RELAY),p=state.player.pos;return !!site&&world?.v046&&world.geoMacro&&!state.v042?.activeInterior&&!world.v050CityInterior&&settings.geoFalloutLayer&&v042SiteDiscovered(site)&&!v050TravelNearbyThreat(world,p)&&world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===M.RELAY&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 function enter(){if(blocked()||!relayNear())return false;const owner=state,w=world,before=copy(owner),maps={active:new Map(V042_RUNTIME.active),npc:new Map(V042_RUNTIME.npcData),nearest:V042_RUNTIME.nearest,instance:V042_RUNTIME.instanceSite,retained:V048.retained},save=saveGame;let wrote=false;saveGame=function(...a){const r=save(...a);if(r===false)throw Error('Départ non sauvegardé.');wrote=true;return r;};try{if(!v042EnterSite(M.SITE))throw Error('Départ interrompu.');return true;}catch(err){restore(owner,before);world=w;V042_RUNTIME.active=maps.active;V042_RUNTIME.npcData=maps.npc;V042_RUNTIME.nearest=maps.nearest;V042_RUNTIME.instanceSite=maps.instance;V048.retained=maps.retained;v049Own(w);if(wrote){try{save(false);}catch{}}return notice(err.message);}finally{saveGame=save;}}
 const relayTalk=v042TalkNPC;v042TalkNPC=function(id){if(blocked()||V042_RUNTIME.npcData.get(id)?.siteId!==M.RELAY||!relayNear())return relayTalk(...arguments);const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text:'Consigne · Les objets trouvés',onChoose:guard(()=>openDialogue(speaker('Relais du Vieux-Port','OBJETS TROUVÉS','AR'),'Nora garde les affaires des gens qui embarquent. Deux gabians ont emporté trois objets dans les paniers de sa cour. Elle cherche une aide pour les récupérer.',[{text:'Rejoindre la consigne.',onChoose:guard(enter)},back()]))},...(ch||[]).slice(-1)],...rest);};try{return relayTalk(...arguments);}finally{openDialogue=old;}};
 function track(){if(blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=M.RELAY;try{if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Repère non sauvegardé.');}updateQuestUI(true);return true;}
 V027_SUBS.data.gabians='GABIANS · OBJETS TROUVÉS';const data=v027Data;v027Data=function(c){if(V027.sub!=='gabians')return data(...arguments);const l=state.v073Gabians,esc=v027Escape;
  c.innerHTML='<div class="p27-long"><p class="p27-kicker">CONSIGNE DU VIEUX-PORT</p><h2>Les objets trouvés</h2><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre le Vieux-Port','g73:track')+'<h3>Objets confiés</h3>'+Object.entries(M.OBJECTS).map(([id,o])=>'<p><b>'+esc(o.name)+'</b> · '+esc({nest:'dans un panier',bag:'transporté',returned:'rendu à Nora'}[l.objects[id]])+(l.manifest?' · '+esc(o.owner)+'<br>'+esc(o.text):'')+'</p>').join('')+'<h3>Paniers</h3>'+M.IDS.map(id=>'<p>'+esc(M.BIRDS[id].name)+' · descente '+Math.round(l.platforms[id].drop/M.DROP*100)+' % · '+esc({guard:'en garde',lure:'en déplacement',fed:'à l’écart',falling:'chute',dead:'abattu'}[l.birds[id].phase])+'</p>').join('')+'<p>Les objets restent dans le sac de mission. Le registre de Nora permet de connaître leurs propriétaires.</p></div>';
 };
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='g73:track'?v027CanAct()&&track():dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v073Gabians;return rows(...arguments).concat(l.opened?[{id:'g73:quest',name:'LES OBJETS TROUVÉS',stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:[['Deux paniers descendus',M.IDS.every(id=>l.platforms[id].drop===M.DROP)],['Trois objets récupérés',Object.values(l.objects).every(v=>v!=='nest')],['Trois objets rendus',Object.values(l.objects).every(v=>v==='returned')],['Retour auprès de Nora',l.finished]],source:'Consigne',badge:l.finished?'✓':'',hint:'Nora · Vieux-Port'}]:[]);};
 const oldTrack=v027Track;v027Track=function(id){return id==='g73:quest'?track():oldTrack(...arguments);};
 function next(){const l=state.v073Gabians;if(!l.opened||Object.values(l.objects).includes('bag')||Object.values(l.objects).every(v=>v==='returned'))return 'nora';const id=M.IDS.find(id=>Object.entries(M.OBJECTS).some(([o,d])=>d.nest===id&&l.objects[o]==='nest'));if(!id)return 'nora';if(!l.lures[id]&&l.birds[id].hp>0)return 'lure:'+id;if(l.platforms[id].drop!==M.DROP)return 'lower:'+id;return 'basket:'+id;}
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return marker(...arguments);const id=next(),p=P[id];return {zone:world.id,pos:[p[0],1.25,p[2]+1.4],label:'Les objets trouvés · '+(id==='nora'?'Nora':id.startsWith('lure:')?'Restes de poisson':id.startsWith('lower:')?'Palan':'Panier')};};
 const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local())return ui(...arguments);$('questTitle').textContent='LES OBJETS TROUVÉS';$('questObjective').textContent=rt.blockedBaskets.length?'Écartez-vous du dessous du panier pour laisser la descente reprendre.':M.briefing(state.v073Gabians);if(flash){const f=$('questFlash');f.querySelector('strong').textContent='LES OBJETS TROUVÉS';f.querySelector('p').textContent=M.briefing(state.v073Gabians);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 V027_STATIONS.gabians={name:'La consigne — objets trouvés',freq:'73.2',hint:'Les oiseaux ne lisent pas les tickets',available:()=>state.v073Gabians.opened,text:()=>M.briefing(state.v073Gabians)};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v073GabiansInfo:()=>({ledger:copy(state.v073Gabians),points:copy(P),local:local(),error:rt.error,paused:rt.paused,blockedBaskets:rt.blockedBaskets.slice(),enemies:(world?.enemies||[]).filter(e=>e.g73Id).map(e=>({id:e.g73Id,pos:e.pos.slice(),health:e.health,alive:e.alive,state:e.state}))}),v073GabiansOpen:()=>v027Open('data','gabians'),v073GabiansAction:act});};
}
