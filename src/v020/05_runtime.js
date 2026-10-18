/* Integration: no auxiliary setInterval simulation; one existing frame loop. */
const v020FrameBase=frame;
frame=function(ts){const dt=Math.min(.05,(ts-lastFrame)/1000||.016);if(!V018.qaFreeze)v020TickCombat(dt);v020FrameBase(ts);};
const v020KeyBase=handleKeyDown;
handleKeyDown=function(e){if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName)){if(e.code==='Escape'&&mode==='FIELD'){e.preventDefault();v020CloseField();}return;}
 if(mode==='FIELD'){if(['Escape','KeyT','Tab'].includes(e.code)){e.preventDefault();v020CloseField();}return;}
 if(mode==='VATS_EXEC'){if(['Escape','KeyV'].includes(e.code)){e.preventDefault();v020CancelVats();}return;}
 if(mode==='PLAYING'){
  if(['KeyT','KeyM'].includes(e.code)||e.key?.toLowerCase()==='m'){e.preventDefault();if(!e.repeat)v020OpenField((e.code==='KeyM'||e.key?.toLowerCase()==='m')?'plan':'interventions');return;}
  if(/^Digit[1-4]$/.test(e.code)){e.preventDefault();if(!e.repeat)v020UseFavorite(+e.code.slice(-1)-1);return;}
 }return v020KeyBase(e);
};
const v020Hide=hideAllScreens;hideAllScreens=function(){v020Hide();$('v020Panel')?.classList.add('hidden');};
const v020HudBase=updateHUD;let v020HudStamp=0;let v046QuickStamp="";
updateHUD=function(){v020HudBase();const bar=$('v020Quickbar'),hint=$('v020QuestHint');if(!bar)return;const visible=gameStarted&&mode==='PLAYING';bar.hidden=!visible;hint.hidden=!visible;const quest=$('questCard');if(quest)quest.style.opacity=world?.v020Interior&&state.v020.tracked?'0':'1';
 const now=performance.now();if(now-v020HudStamp<220)return;v020HudStamp=now;
 if(visible){const stamp=JSON.stringify([state.v020.favorites,state.player.weaponId]);if(stamp!==v046QuickStamp||!bar.querySelector('[data-slot]')){v046QuickStamp=stamp;const bag=bar.querySelector('[data-v26-quick]');bar.innerHTML=`<button data-open="interventions">T · Relais</button><button data-open="plan">M · Plan</button>`+state.v020.favorites.map((id,i)=>`<button class="quick-slot ${id===state.player.weaponId?'active':''}" data-slot="${i}" title="${id?escapeHtml(WEAPONS[id]?.name||'Arme'):'Vide'}">${i+1} · ${id?escapeHtml(WEAPONS[id]?.name||'Arme'):'Vide'}</button>`).join('');if(bag)bar.prepend(bag);}
 const id=state.v020.tracked,d=V020_OPERATIONS[id],s=d&&v020OpState(id),o=activeCompanion()?v020Command():null;
 if(d&&!s.resolution){hint.innerHTML=`<b>${escapeHtml(d.title)}</b>${!s.accepted?'Rencontrer '+escapeHtml(d.name):!s.diagnosed?'Lire le diagnostic':!s.component?'Récupérer '+escapeHtml(d.component):!s.isolated?escapeHtml(d.action):'Décider de la remise en service'}${o?`<br><small>Compagnon · ${o.move==='hold'?'tient sa position':'suit'} · ${o.fire==='quiet'?'feu retenu':'riposte'}</small>`:''}`;}else hint.hidden=true;
 }
};
function v020AfterInit(){
 if(sky){const oldSky=sky.draw.bind(sky);sky.draw=function(env,t){if(!world?.v020Interior)return oldSky(env,t);const canvas=$('skyCanvas'),ctx=canvas.getContext('2d');const g=ctx.createLinearGradient(0,0,0,canvas.height);g.addColorStop(0,'#101916');g.addColorStop(1,'#38463b');ctx.fillStyle=g;ctx.fillRect(0,0,canvas.width,canvas.height);};}
 document.title='Fallout : Mistral · v0.20 · Les relais du quotidien';
 const field=document.createElement('section');field.id='v020Panel';field.className='hidden';field.setAttribute('role','dialog');field.setAttribute('aria-modal','true');field.setAttribute('aria-label','Services et interventions de terrain');field.innerHTML=`<header><div><div class="v20-eyebrow">PIP-BOY · SERVICES DE PROXIMITÉ · 0.20</div><h2 id="v020Title">Relais du quotidien</h2><div id="v020Place"></div></div><button id="v020Close" data-v20="close">Fermer</button></header><nav id="v020Nav" aria-label="Rubriques de terrain"></nav><label id="v020SearchWrap"><input id="v020Search" type="search" placeholder="Rechercher un équipement ou une recette…" aria-label="Rechercher"></label><div id="v020Body"></div>`;
 document.body.appendChild(field);field.addEventListener('click',e=>{const btn=e.target.closest('[data-v20]');if(btn&&!btn.disabled)v020Dispatch(btn.dataset.v20);});$('v020Search').addEventListener('input',e=>{V020.query=e.target.value.slice(0,100);V020.gearPage=0;v020RenderField();});
 $('gameCanvas').addEventListener('mousedown',e=>{if(e.button===0&&mode==='PLAYING')V020.heldFire=true;});document.addEventListener('mouseup',()=>V020.heldFire=false);window.addEventListener('blur',()=>{V020.heldFire=false;keys.clear();});document.addEventListener('visibilitychange',()=>{if(document.hidden){V020.heldFire=false;keys.clear();}});
 const bar=document.createElement('div');bar.id='v020Quickbar';bar.hidden=true;bar.setAttribute('aria-label','Raccourcis de terrain');document.body.appendChild(bar);bar.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;b.dataset.open?v020OpenField(b.dataset.open):b.dataset.slot!==undefined?v020UseFavorite(+b.dataset.slot):null;});
 const hint=document.createElement('div');hint.id='v020QuestHint';hint.hidden=true;document.body.appendChild(hint);
 const badge=document.createElement('p');badge.id='v020Version';badge.textContent='v0.20 · 3 intérieurs de relève · T : services · M : plan local. Base récupérée v0.18 ; captures v0.19 archivées.';($('menuScreen').querySelector('.menu-content')||$('menuScreen').querySelector('nav')||$('menuScreen')).appendChild(badge);
 const intro=$('btnChapter');if(intro){intro.textContent='Exploration libre · contenu historique';}
 const savedCoverage=v018CoverageReport;v018CoverageReport=function(){return {...savedCoverage(),historicInstances:86,newRelays:3,name:'Les relais du quotidien'};};const savedStatus=v018OpenStatus;v018OpenStatus=function(){savedStatus();$('v018StatusScreen').querySelector('.eyebrow').textContent='ÉTAT RÉEL DE LA LIVRAISON · v0.20';};$('v018MenuStatus').onclick=v018OpenStatus;
 const newBtn=$('btnNew');if(newBtn)newBtn.textContent='Nouvelle campagne · lieux scénarisés';
 Object.assign(window.__MISTRAL_DEBUG,{
  v020RandomFire:(roll=.5)=>{const fn=Math.random;Math.random=()=>roll;try{return fireWeapon();}finally{Math.random=fn;}},
  v020QueueBody:()=>{if(!vatsState)return false;vatsState.partIndex=enemyHitParts(vatsState.targets[vatsState.targetIndex]).findIndex(p=>p.id==='body');return vatsAddCurrent();},
  v020RandomTick:(dt,roll=.5)=>{const fn=Math.random;Math.random=()=>roll;try{v020TickCombat(dt);return {mode,ammo:state.player.ammoClip,ap:state.player.ap,hp:world.enemies[0]?.health};}finally{Math.random=fn;}},
  v020Favorite, v020CloseDoor:(id)=>{state.v020.openedDoors[id]=false;},
  v020AutomaticIds:()=>Object.keys(WEAPONS).filter(id=>v020Profile(WEAPONS[id]).automatic),
  v020Hold:(held)=>V020.heldFire=!!held,
  v020Reset:()=>{v020ResetTransient();state=baseState();syncEquipment();state.v018.travelMode='story';return deepClone(state);},
  v020Inventory:()=>deepClone(state.inventory),
  v020Items:()=>Object.keys(ITEM_VALUES),
  v020OpDefs:()=>deepClone(V020_OPERATIONS),
  v020MapState:()=>({pin:V020.mapPin,path:V020.mapPath}),
  v020Recipes:()=>deepClone(V020_RECIPES),
  v020WalkQA:(target)=>{const route=v020Route(state.player.pos,target);if(!route)return {ok:false,reason:'no route'};let steps=0;const prev=V018.qaFreeze;V018.qaFreeze=false;keys.clear();for(const p of route){let local=0;while(dist2(state.player.pos,p)>.48&&local++<45){state.player.yaw=Math.atan2(p[0]-state.player.pos[0],-(p[2]-state.player.pos[2]));keys.add('KeyW');updatePlayer(.05);steps++;}if(local>=45){keys.clear();V018.qaFreeze=prev;return {ok:false,pos:state.player.pos,blocked:p,steps};}}keys.clear();V018.qaFreeze=prev;return {ok:dist2(state.player.pos,target)<2.6,pos:state.player.pos,steps};},
  v020Version:()=>({version:'0.20.0',source:'0.18',v019Sources:false,operations:Object.keys(V020_OPERATIONS),recipes:V020_RECIPES.length,actualMapTiles:0}),
  v020Open:v020OpenField,v020Close:v020CloseField,v020Craft,v020Rest,v020Repair,v020Stash,v020Order:v020SetOrder,v020Equip:equipWeapon,
  v020State:()=>deepClone(state),v020Load:(id)=>{gameStarted=true;V018.networkDisabled=true;hideAllScreens();loadZone(id,{instance:true,force:true,silent:true,noTravel:true});mode='PLAYING';$('hud').classList.remove('hidden');return {id:world.id,spawn:world.spawn};},
  v020Stats:()=>({id:world.id,draws:world.staticDraws.length,colliders:world.colliders.length,doors:world.interactables.filter(i=>i.kind==='door').length,rooms:world.v020Rooms,interactables:world.interactables.map(i=>({id:i.id,pos:i.pos,label:i.label})),enemy:world.enemies.map(e=>({id:e.id,hp:e.health,alive:e.alive,pos:e.pos,alerted:e.alerted})),player:[...state.player.pos],mode,station:world.v020Station}),
  v020Seed:(resources={})=>{for(const [id,n] of Object.entries(resources))if(id==='caps')state.player.caps=n;else if(AMMO_INFO[id])state.ammo[id]=n;else state.inventory[id]=n;syncEquipment();return deepClone(state.inventory);},
  v020GrantWeapon:(id)=>{if(!WEAPONS[id])return false;if(!state.equipment.ownedWeapons.includes(id))state.equipment.ownedWeapons.push(id);state.equipment.weaponCondition[id]=100;state.equipment.loadedAmmo[id]=WEAPONS[id].clip||0;return true;},
  v020SetPlayer:(patch)=>{Object.assign(state.player,deepClone(patch));return deepClone(state.player);},
  v020SetOp:(id,patch)=>{Object.assign(v020OpState(id),patch);return deepClone(v020OpState(id));},
  v020SetFlags:(p)=>Object.assign(state.flags,p),
  v020Approach:(id)=>{const it=world.interactables.find(i=>i.id===id);if(!it)return null;let p=null;for(const a of [0,Math.PI,Math.PI/2,-Math.PI/2,.75,-.75]){const q=[it.pos[0]+Math.sin(a)*1.6,(it.pos[1]>3?it.pos[1]+.65:1.65),it.pos[2]+Math.cos(a)*1.6];if(q[0]>world.bounds[0]+.6&&q[0]<world.bounds[1]-.6&&q[2]>world.bounds[2]+.6&&q[2]<world.bounds[3]-.6&&!collidesAt(q[0],q[2],.36,q[1])&&lineOfSight(q,it.pos)){p=q;break;}}if(!p)return null;state.player.pos=p;state.player.yaw=Math.atan2(it.pos[0]-p[0],-(it.pos[2]-p[2]));state.player.pitch=0;return {pos:p,physical:v020Physical(id)};},
  v020Interact:(id)=>{const it=world.interactables.find(i=>i.id===id);if(!it||!v020Physical(id,4))return false;return it.onInteract();},
  v020OpAction,v020Exit:v020ExitInterior,v020Enter:v020EnterInterior,
  v020Route:(target)=>v020Route(state.player.pos,target),v020Collides:(p)=>collidesAt(p[0],p[2],.36,p[1]||1.65),
  v020LOS:(a,b)=>lineOfSight(a,b),v020Door:(id)=>{const it=world.interactables.find(i=>i.id===id);return it?.onInteract();},
  v020Tick:(dt,sim=false)=>{v020TickCombat(dt);if(sim){const old=V018.qaFreeze;V018.qaFreeze=false;updatePlayer(dt);V018.qaFreeze=old;}updateHUD();return {mode,cooldown:V020.cooldown,reload:reloadTimer,shots:V020.shots,execution:V020.execution?.queue.length??null};},
  v020Combat:()=>({mode,cooldown:V020.cooldown,reload:reloadTimer,reloadWeapon:V020.reload?.weapon,shots:V020.shots,queue:vatsState?.queue.length,execution:V020.execution?.queue.length,ammo:state.player.ammoClip,ap:state.player.ap,log:V020.combatLog}),
  v020Vats:()=>{toggleVATS();return mode;},v020VatsAdd:()=>vatsAddCurrent(),v020VatsExecute:()=>executeVATS(),v020VatsCancel:v020CancelVats,
  v020Damage:(weapon,type='raider',part='body')=>v020Damage(WEAPONS[weapon],{type}, {id:part,mult:part==='head'?1.65:1},false),
  v020Fixture:(wall=false,type='raider',distance=10)=>{v020ResetTransient();world=createWorld('v020_qa_fixture','ARÈNE SYNTHÉTIQUE QA — PAS UN LIEU RÉEL','QA');world.bounds=[-20,20,-20,20];addFloorZone(world,0,0,40,40,0);addBox(world,[0,-.1,0],[40,.2,40],[.38,.4,.31]);world.spawn=[0,1.65,8];state.player.zone=world.id;state.player.pos=[0,1.65,8];state.player.yaw=0;state.player.pitch=0;state.player.hp=state.player.maxHp;state.player.ap=state.player.maxAp;gameStarted=true;mode='PLAYING';hideAllScreens();$('hud').classList.remove('hidden');const id='v020-qa-enemy';delete state.flags.enemyDead[id];addEnemy(world,id,type,'Cible synthétique',[0,0,8-distance],{health:2000,detect:0,range:0,damage:0,speed:0,loot:{}});if(wall)v020Wall(world,0,8-distance/2,30,.5,[.4,.4,.3]);return world.id;},
  v020AddWall:()=>v020Wall(world,0,3,30,.5,[.4,.4,.3]),
  v020EnemyPatch:(patch)=>{Object.assign(world.enemies[0],patch);return deepClone(world.enemies[0]);},
  v020Companion:(id,pos,dt=0)=>{if(!COMPANIONS[id])return null;state.flags[COMPANIONS[id].flag]=true;state.player.activeCompanion=id;const a=v020CompanionActor();if(a&&pos)a.pos=[...pos];if(dt)updateCompanion(dt);return a?{pos:[...a.pos],order:v020Command(),cooldown:a.attackCooldown}:null;},
  v020NpcStep:(dt)=>{updateNPCSchedules(dt);return world.npcs.map(n=>({id:n.id,pos:n.pos,moving:n.moving}));},
  v020ModalDismiss:()=>{debugDismissDialogue();v020CloseField();},
  v020Renderer:()=>({class:renderer?.constructor?.name,webgl:!!renderer?.gl}),
 });
 const captureBase=window.__MISTRAL_DEBUG.v018CaptureAt;window.__MISTRAL_DEBUG.v018CaptureAt=function(...args){const out=captureBase(...args);updateSelectedInteractable();updateHUD();return out;};
 updateHUD();
}
