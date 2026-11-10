/* An authored exhibition courtyard uses the existing renderer, inputs and saves.
 * The surveying layer is untouched; only the existing port anchors its entrance. */
if(typeof baseState==='function'&&typeof MistralBoules!=='undefined'){
 const M=MistralBoules,copy=x=>JSON.parse(JSON.stringify(x));
 const P={nelly:[-5,0,4],cercle:[0,0,1],sortie:[0,0,7]};
 const rt={busy:false,paused:false,error:null,delay:0,owner:null,world:null};
 const anchor=v042Site(M.RELAY);
 if(anchor&&!v042Site(M.SITE)){const s={...copy(anchor),id:M.SITE,name:'Cour des Cent Trêves',description:'Boulodrome d’exposition fictionnel : une mène, trois boules chacun, aucune mise.',kind:'interior',interior:'boules',safe:true,visitable:true,unique:true,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],enemyRadius:0,rewardCaps:0,rewardXP:0,respawnHours:0,provenance:{kind:'authored-fiction',anchorId:M.RELAY}};V042_CATALOG.push(s);V042_SITE_BY_ID[s.id]=s;V042_SITES_BY_MACRO[s.macro].push(s);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[s.macro]++;}
 const base=baseState;baseState=function(...a){const s=base(...a);s.v073Boules=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(...arguments);s.v073Boules=M.migrate(raw?.v073Boules);return s;};state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const local=()=>!!world?.v073Boules&&state.v042?.activeInterior===M.SITE;
 const notice=t=>{V027.message=t;toast(t,'bad');return false;};
 function blocked(){return !gameStarted||!['PLAYING','DIALOGUE','PIP','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Pas de progression dans le banc géographique.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':!onGround?'Les pieds doivent rester au sol.':null;}
 function near(id){const p=P[id],v=state.player.pos;return local()&&p&&Math.hypot(v[0]-p[0],v[2]-p[2])<=(id==='cercle'?.65:3.2)&&Math.abs(v[1]-1.65)<.65&&lineOfSight(v,[p[0],1.25,p[2]+.7]);}
 function sync(){if(rt.owner!==state||rt.world!==world){rt.owner=state;rt.world=world;rt.delay=0;rt.paused=false;rt.error=null;}}
 function restore(owner,before){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}
 function commit(next){if(rt.busy)return false;const owner=state,w=world,before=copy(owner),old=owner.v073Boules;rt.busy=true;
  try{const n=M.migrate(next),delta=n.played-old.played,win=n.wins-old.wins;if(delta<0||delta>1||win<0||win>delta)throw Error('Mesure périmée.');
   if(delta){const p=v046LoreState().petanque;for(const k of ['played','wins'])if(!Number.isSafeInteger(p[k])||p[k]<0||p[k]>999998)throw Error('Historique COCHONNET invalide.');p.played+=delta;p.wins+=win;}
   owner.v073Boules=n;if(state!==owner||world!==w||saveGame(false)===false)throw Error('La feuille de mène n’a pas pu être sauvegardée.');
  }catch(e){restore(owner,before);rt.error=e.message;return notice(e.message+' Le coup est annulé.');}finally{rt.busy=false;}
  rt.error=null;rt.delay=0;updateQuestUI();updateHUD();return true;
 }
 function act(type,value){sync();if(blocked()||!local()||rt.busy)return false;try{
  const l=state.v073Boules,r=l.round;
  if(type==='start'){if(!near('nelly'))return notice('Nelly garde la feuille de mène.');return commit(M.start(l));}
  if(type==='retry'){if(!near('nelly'))return false;if(saveGame(false)===false)throw Error('Écriture toujours refusée.');rt.paused=false;rt.error=null;return true;}
  if(type==='configure'){if(!near('cercle')||rt.paused)return false;return commit(M.configure(l,value?.style,value?.power));}
  if(type==='throw'){if(!near('cercle')||rt.paused||!r)return notice('Rejoignez le cercle et attendez votre tour.');const yaw=Math.atan2(Math.sin(state.player.yaw),Math.cos(state.player.yaw));return commit(M.launch(l,'player',yaw,r.power,r.style));}
  return false;
 }catch(e){return notice(e.message);}}
 function guard(fn){const owner=state,w=world,rev=state.v073Boules.revision;return()=>owner===state&&w===world&&rev===state.v073Boules.revision?fn():notice('La feuille a changé. Rouvrez la conversation.');}
 const back=()=>({text:'Revenir.',onChoose:closeDialogue});
 function dialogue(id){sync();if(blocked()||!near(id))return false;const l=state.v073Boules,r=l.round,ch=[];
  let text=id==='nelly'?'« Le lanceur a survécu à trois guerres de voisinage. Le mètre aussi. Les deux sont sous ma garde : ici, personne ne gagne parce qu’il parle plus fort. Pas de mise, pas de grenade, et on attend que tout s’arrête avant de mesurer. »\n\nNelly Ferrand ouvre une mène d’exposition : trois boules chacun. Le but est posé par l’arbitre ; s’il sort, la mène est annulée. Le camp qui n’a pas le point rejoue. Une égalité au millimètre fait alterner les lancers.':'Le cercle délimite votre départ. Réglez la force, choisissez pointer (cloche) ou tirer (rasant), puis visez dans le terrain. La commande de tir habituelle lance une boule ; Recharger change le geste. Aucun appui maintenu ni réflexe chronométré n’est nécessaire.';
  if(id==='nelly'&&(!r||r.phase==='result'))ch.push({text:r?'Commencer une autre mène, sans mise.':'Ouvrir la mène d’exposition.',onChoose:guard(()=>{if(act('start'))closeDialogue();})});
  if(id==='nelly'&&rt.paused)ch.push({text:'Retenter la sauvegarde et reprendre.',onChoose:guard(()=>{act('retry');dialogue(id);})});
  if(id==='cercle'&&r?.phase==='aim'&&r.turn==='player'&&!rt.paused){
   for(const [style,label]of [['pointer','Pointer · lancer en cloche'],['tirer','Tirer · lancer rasant']])ch.push({text:label+(style===r.style?' [choisi]':''),onChoose:guard(()=>{act('configure',{style,power:r.power});dialogue(id);})});
   for(const n of [-5,-1,1,5])ch.push({text:'Force '+(n>0?'+':'')+n+' · '+Math.max(0,Math.min(100,r.power+n))+' %',onChoose:guard(()=>{act('configure',{style:r.style,power:Math.max(0,Math.min(100,r.power+n))});dialogue(id);})});
   ch.push({text:'Lancer dans la direction visée.',onChoose:guard(()=>{if(act('throw'))closeDialogue();})});
  }
  ch.push({text:'Consulter les distances au but.',onChoose:guard(()=>{closeDialogue();v027Open('data','boules');})},back());
  openDialogue(speaker(id==='nelly'?'Nelly Ferrand':'Cercle de lancer','COCHONNET · LES CENT TRÊVES','C3'),text+'\n\n'+M.briefing(l)+(r?.phase==='aim'?'\nGeste : '+r.style+' · Force : '+r.power+' %.':''),ch);return true;
 }
 function build(){sync();const w=createWorld(V042_INSTANCE_ZONE,'La cour des Cent Trêves','COCHONNET-3 · MÈNE D’EXPOSITION',{skyTop:[90,115,128],skyBottom:[180,168,129],fog:[.45,.48,.42],daylight:.85,wind:.04,indoor:false});w.v073Boules=true;w.bounds=[-8,8,-15,8];w.spawn=[0,1.65,5.5];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE;
  const stone=[.48,.44,.35],steel=[.25,.32,.32],box=(p,s,c=stone,solid=true)=>{const d=addBox(w,p,s,c);if(solid)addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});return d;};
  box([0,-.17,-3.5],[16,.3,23],stone,false);addFloorZone(w,0,-3.5,16,23,0);box([0,-.035,-5],[5,.07,14],[.66,.55,.37],false);
  for(const [x,z,sx,sz]of [[-7.8,-3.5,.35,23],[7.8,-3.5,.35,23],[0,-14.8,16,.35]])box([x,1.4,z],[sx,2.8,sz]);
  for(const x of [-2.5,2.5])box([x,.009,-5],[.035,.018,14],[.88,.83,.62],false);
  for(const z of [-12,2])box([0,.009,z],[5,.018,.035],[.88,.83,.62],false);
  // The visible rails are outside the dead-ball lines, never invisible bouncers.
  for(const x of [-3,3])box([x,.14,-5],[.16,.28,14.8],[.34,.28,.19]);
  for(let i=0;i<40;i++){const a=i*Math.PI*2/40;box([Math.cos(a)*.65,.016,1+Math.sin(a)*.65],[.085,.025,.085],[.8,.79,.67],false);}
  for(const x of [-6,6])for(const z of [-9,-3]){box([x,.48,z],[1,.16,3.3],[.35,.29,.20]);for(const dz of [-1.1,1.1])box([x,.23,z+dz],[.7,.46,.18],steel);box([x+(x<0?-.35:.35),.95,z],[.14,.85,3.3],[.38,.32,.21]);}
  box([-5,1,2],[2,.15,1.2],steel);box([-5,.45,2],[1.6,.9,.6]);box([-5,1.13,2],[.8,.1,.5],[.81,.77,.58],false);
  // The mechanical arm reaches the common release point, not a ghost opponent.
  box([-1.35,.48,.5],[.65,.96,.8],steel);box([-.62,.85,.5],[1.45,.16,.22],[.62,.47,.24],false);box([-1.35,1.15,.5],[.8,.3,.6],steel);addPart(w,'sphere',[-1.35,1.17,.84],[.18,.18,.12],[.74,.58,.27],0,{emissive:.2});
  addHumanNPC(w,'r73:nelly','Nelly Ferrand','Arbitre des Cent Trêves',P.nelly,[.30,.39,.34],{yaw:Math.PI});
  addInteract(w,'r73:cercle',[0,.15,.6],'Régler le lancer · COCHONNET',()=>dialogue('cercle'),{radius:2,kind:'quest',priority:8,condition:()=>near('cercle')&&!blocked()});
  addInteract(w,'r73:sortie',[0,1.25,7.7],'Retourner au Vieux-Port',()=>!blocked()&&near('sortie')&&v042ExitInstance(),{radius:3.2,kind:'door',priority:5});
  if(typeof v021Sign==='function'){v021Sign(w,0,2.25,-14.55,'CENT TREVES / PAS DE MISE',.075);v021Sign(w,-5,2.3,1.3,'NELLY / ARBITRE',.055);v021Sign(w,0,2.7,7.8,'RETOUR / VIEUX-PORT',.065);}
  w.levelRoutes=[{id:'r73-court',points:[[0,0,5.5],[0,0,1],[4,0,1],[4,0,-10]]}];return w;
 }
 const buildBase=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE?build():buildBase(...arguments);};
 const talk=talkToNPC;talkToNPC=function(id){return id==='r73:nelly'?dialogue('nelly'):talk(...arguments);};
 const claim=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE?false:claim(...arguments);};
 const fire=fireWeapon;fireWeapon=function(...a){return local()?mode==='PLAYING'&&act('throw'):fire(...a);};
 const reloading=reload;reload=function(...a){if(!local())return reloading(...a);const r=state.v073Boules.round;if(mode==='PLAYING'&&r?.phase==='aim'&&r.turn==='player')return act('configure',{style:r.style==='pointer'?'tirer':'pointer',power:r.power});return false;};
 const combat=v020TickCombat;v020TickCombat=function(...a){return local()?undefined:combat(...a);};
 const vats=toggleVATS;toggleVATS=function(...a){return local()?false:vats(...a);};
 const enemies=updateEnemies;updateEnemies=function(dt){if(!local())return enemies(...arguments);sync();if(!gameStarted||mode!=='PLAYING'||zoneTransitioning||V046.busy||V047.pending||V046.lab||!(state.player.hp>0)||rt.busy||rt.paused||!Number.isFinite(dt)||dt<=0)return;inCombat=false;dt=Math.min(dt,.2);const r=state.v073Boules.round;if(!r)return;
  try{if(r.phase==='moving'){const next=M.advance(state.v073Boules,dt);if(next.round.phase!==r.phase){if(!commit(next))rt.paused=true;}else state.v073Boules=next;}
   else if(r.phase==='aim'&&r.turn==='house'){rt.delay+=dt;if(rt.delay>=1){const shot=M.house(state.v073Boules);if(!commit(M.launch(state.v073Boules,shot.team,shot.yaw,shot.power,shot.style)))rt.paused=true;}}
  }catch(e){rt.paused=true;rt.error=e.message;notice(e.message+' Adressez-vous à Nelly.');}
 };
 const draws=collectDraws;collectDraws=function(t){const out=draws(...arguments);if(!local())return out;const r=state.v073Boules.round;if(!r)return out;
  for(const b of [r.jack,...r.balls]){if(b.out)continue;const d=2*M.radius(b),color=b.id==='jack'?[.85,.72,.29]:b.team==='player'?[.78,.80,.75]:[.34,.47,.57];part(out,'sphere',b.p.slice(),[d,d,d],color,0,{emissive:b.id==='jack'?.12:0});if(b.id!=='jack')part(out,'cube',[b.p[0],b.p[1]+M.radius(b)*.83,b.p[2]],[d*.55,.025,.045],b.team==='player'?[.19,.27,.22]:[.85,.66,.35]);}
  // A neutral sight line shows the launch axis, not a guaranteed landing result.
  if(r.phase==='aim'&&r.turn==='player'&&near('cercle'))for(let i=1;i<=8;i++){const y=state.player.yaw;part(out,'cube',[Math.sin(y)*i*.45,.018,.5-Math.cos(y)*i*.45],[.045,.015,.11],[.72,.72,.51],-y);}
  return out;
 };
 const hud=updateHUD;updateHUD=function(...a){const r=hud(...a),isLocal=local();document.body.classList.toggle('v073-court',isLocal);const el=document.getElementById('v073CourtHud');if(el){el.hidden=!isLocal||mode!=='PLAYING';if(isLocal){const l=state.v073Boules.round;el.textContent=rt.paused?'MÈNE SUSPENDUE · Nelly peut retenter l’écriture':l?.phase==='aim'&&l.turn==='player'?`${near('cercle')?'DANS LE CERCLE':'REJOIGNEZ LE CERCLE'} · ${l.style.toUpperCase()} · FORCE ${l.power} % · Tir : lancer · Recharger : changer de geste · Interagir : réglages`:M.briefing(state.v073Boules);}}return r;};
 const ui=updateQuestUI;updateQuestUI=function(...a){if(!local())return ui(...a);$('questTitle').textContent='COCHONNET · LA MÈNE DES CENT TRÊVES';$('questObjective').textContent=M.briefing(state.v073Boules);};
 const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return marker(...arguments);const r=state.v073Boules.round,id=!r||r.phase==='result'||rt.paused?'nelly':'cercle',p=P[id];return{zone:world.id,pos:[p[0],1.25,p[2]],label:id==='nelly'?'Nelly · feuille de mène':'Cercle de lancer'};};
 function relayNear(){const site=v042Site(M.RELAY),p=state.player.pos;return !!site&&world?.v046&&world.geoMacro&&!state.v042?.activeInterior&&!world.v050CityInterior&&settings.geoFalloutLayer&&v042SiteDiscovered(site)&&!v050TravelNearbyThreat(world,p)&&world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===M.RELAY&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 function enter(){if(blocked()||!relayNear())return false;if(state.v055Ordnance?.armed)return notice('Terminez d’abord le lancer de grenade.');const owner=state,w=world,before=copy(owner),maps={active:new Map(V042_RUNTIME.active),npc:new Map(V042_RUNTIME.npcData),nearest:V042_RUNTIME.nearest,instance:V042_RUNTIME.instanceSite,retained:V048.retained},save=saveGame;let wrote=false;saveGame=function(...a){const r=save(...a);if(r===false)throw Error('Départ non sauvegardé.');wrote=true;return r;};try{if(!v042EnterSite(M.SITE))throw Error('Départ interrompu.');return true;}catch(e){restore(owner,before);world=w;V042_RUNTIME.active=maps.active;V042_RUNTIME.npcData=maps.npc;V042_RUNTIME.nearest=maps.nearest;V042_RUNTIME.instanceSite=maps.instance;V048.retained=maps.retained;v049Own(w);if(wrote){try{save(false);}catch{}}return notice(e.message);}finally{saveGame=save;}}
 const relayTalk=v042TalkNPC;v042TalkNPC=function(id){if(blocked()||V042_RUNTIME.npcData.get(id)?.siteId!==M.RELAY||!relayNear())return relayTalk(...arguments);const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text:'COCHONNET · La cour des Cent Trêves',onChoose:guard(()=>openDialogue(speaker('Relais du Vieux-Port','UNE TRÊVE, TROIS BOULES','C3'),'« Nelly a remis le lanceur en service. Il confond toujours une poignée de mains et une remise à zéro, mais ses boules roulent droit. Enfin… presque. »\n\nLa cour est un lieu fictionnel relié par chargement. L’exposition n’exige aucune autre quête et ne demande aucune mise.',[{text:'Rejoindre le boulodrome d’exposition.',onChoose:guard(enter)},back()]))},...(ch||[]).slice(-1)],...rest);};try{return relayTalk(...arguments);}finally{openDialogue=old;}};
 function track(){if(blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=M.RELAY;try{if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Repère non sauvegardé.');}updateQuestUI();return true;}
 V027_SUBS.data.boules='COCHONNET · LE TERRAIN';const data=v027Data;v027Data=function(c){if(V027.sub!=='boules')return data(...arguments);const l=state.v073Boules,r=l.round,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">LIGUE DES CENT TRÊVES</p><h2>Une mène, pas un tirage au sort</h2><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre le relais du Vieux-Port','r73:track')+'<p>Mènes physiques terminées : '+l.played+' · Victoires : '+l.wins+'. Les anciens résultats restent conservés séparément.</p><h3>Mesures entre centres</h3>'+(r&&!r.jack.out?M.distances(r).map(b=>'<p>'+esc((b.team==='player'?'Vous ':'Machine ')+b.id.replace(/\D/g,'')+' : '+(b.metres*100).toFixed(1)+' cm'+(r.phase==='moving'?' · provisoire':''))+'</p>').join(''):'<p>Aucune mesure en cours.</p>')+(r?'<p>Boules sorties : '+r.balls.filter(b=>b.out).length+'.</p>':'')+'<h3>Le règlement de Nelly</h3><p>Trois boules chacun. Celui qui n’a pas le point rejoue ; à égalité au millimètre, les lancers alternent. But sorti : mène annulée. Aucun gain de capsules, de butin ou d’expérience. Une victoire compte pour les anciens dossiers COCHONNET, sans les terminer à distance.</p><p>Depuis le cercle : commande Tir pour lancer, Recharger pour changer de geste, Interagir pour régler la force. Le Pip-Boy mesure mais ne lance pas. Vous pouvez quitter et reprendre la cour : positions, vitesses et tours sont conservés.</p></div>';};
 const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='r73:track'?v027CanAct()&&track():dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v073Boules;return rows(...arguments).concat(l.round?[{id:'r73:mene',name:'LA MÈNE DES CENT TRÊVES',stage:l.round.phase==='result'?'done':'active',active:local()&&l.round.phase!=='result',text:M.briefing(l),zone:null,steps:[['Mène ouverte',true],['Boules stabilisées',l.round.phase==='result'],['Résultat mesuré',l.round.phase==='result']],source:'COCHONNET',badge:l.round.phase==='result'?'✓':'',hint:'Nelly · cour du Vieux-Port'}]:[]);};
 const previousTrack=v027Track;v027Track=function(id){return id==='r73:mene'?track():previousTrack(...arguments);};
 V027_STATIONS.boules={name:'COCHONNET — Les Cent Trêves',freq:'73.3',hint:'Le mètre a le dernier mot',available:()=>!!state.v073Boules.round,text:()=>M.briefing(state.v073Boules)};
 // Replace only the old random-roll controls; never re-create the other dossier nodes.
 const oldPanel=v046LorePanel;v046LorePanel=function(c){const result=oldPanel(...arguments),buttons=c.querySelectorAll('[data-v46-boule]');if(buttons.length){const first=buttons[0],link=document.createElement('button');link.textContent='COCHONNET · Rejoindre le terrain';link.onclick=()=>v027Open('data','boules');first.before(link);for(const b of buttons)b.remove();for(const text of c.querySelectorAll('p'))if(text.textContent.includes('Résolution probabiliste'))text.textContent='Les anciens résultats sont conservés. Les nouvelles mènes se jouent dans la cour des Cent Trêves, auprès du relais du Vieux-Port.';}return result;};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();const style=document.createElement('style');style.textContent='body.v073-court #weaponModel,body.v073-court #weaponHud{display:none!important}#v073CourtHud{position:fixed;left:50%;transform:translateX(-50%);bottom:15%;max-width:calc(100% - 30px);width:600px;box-sizing:border-box;padding:9px 13px;background:#101b18eb;border:1px solid #9b9f75;color:#eee9cc;font:14px/1.4 monospace;text-align:center;pointer-events:none;z-index:18}#v073CourtHud[hidden]{display:none}@media(max-width:600px){#v073CourtHud{font-size:12px;bottom:26%}}';document.head.appendChild(style);const el=document.createElement('div');el.id='v073CourtHud';el.hidden=true;document.body.appendChild(el);Object.assign(window.__MISTRAL_DEBUG,{v073BoulesInfo:()=>({ledger:copy(state.v073Boules),points:copy(P),local:local(),paused:rt.paused,error:rt.error,nearCircle:near('cercle')}),v073BoulesOpen:()=>v027Open('data','boules'),v073BoulesAction:act});};
}
