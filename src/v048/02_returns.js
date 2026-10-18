/* Keep one previously validated exterior while visiting a territorial interior.
   This is session memory, not a second campaign save. Inventory/quests are never
   rolled back on return. On mismatch, use the ordinary validated loading gate. */
function v048DiscardReturn(reason='remplacé') {
  if(V048.retained){V048.returns.discarded++;V048.returns.last={event:'discard',reason};}
  V048.retained=null;
}
function v048Retain(site) {
  if(!world?.v046 || !site?.visitable)return null;
  const bytes=MistralStream.bytes({draws:world.staticDraws,colliders:world.colliders,records:world.v046Records,bank:V046.terrain,
    raw:new Map(V046.gate.cache)});
  if(bytes>V048.returnLimit){v048DiscardReturn('budget de session');V048.returns.missed++;return null;}
  const snapshot={world,bank:V046.terrain,readyAnchor:V046.readyAnchor?.slice(),raw:new Map(V046.gate.cache),
    active:new Map(V042_RUNTIME.active),npcData:new Map(V042_RUNTIME.npcData),worldId:V042_RUNTIME.worldId,
    nearest:V042_RUNTIME.nearest,state,site:site.id,lab:V046.lab,pos:state.player.pos.slice(),
    yaw:state.player.yaw,pitch:state.player.pitch,bytes,createdAt:Date.now()};
  V048.retained=snapshot;V048.returns.kept++;V048.returns.last={event:'keep',site:site.id,bytes};return snapshot;
}
const v048EnterBase=v042EnterSite;
v042EnterSite=function(id) {
  const site=v042Site(id);if(!site?.visitable||!world?.geoMacro)return v048EnterBase(id);
  if(V047.pending||V046.busy)v046Cancel();
  v048Retain(site);
  try {const ok=v048EnterBase(id);if(!ok)v048DiscardReturn('entrée refusée');return ok;}
  catch(e){v048DiscardReturn('échec entrée');throw e;}
};
function v048CanRestore(id, opts) {
  const r=V048.retained;
  return !!(r && world?.id===V042_INSTANCE_ZONE && r.state===state && r.lab===V046.lab &&
    r.world?.v046 && id===r.world.id && state.v042?.returnPoint?.site===r.site &&
    MistralWork.sameReturn(r.pos,opts?.spawn) && r.world.v046Anchor &&
    Math.hypot(r.pos[0]-r.world.v046Anchor[0],r.pos[2]-r.world.v046Anchor[2])<=170);
}
function v048RestoreExterior(id, opts) {
  const r=V048.retained;if(!r)return false;
  const rollback={world,bank:V046.terrain,readyAnchor:V046.readyAnchor,active:new Map(V042_RUNTIME.active),
    npcData:new Map(V042_RUNTIME.npcData),worldId:V042_RUNTIME.worldId,pos:state.player.pos.slice(),zone:state.player.zone,yaw:state.player.yaw,pitch:state.player.pitch,mode};
  try {
    v046Cancel();V046.terrain=r.bank;V046.readyAnchor=r.readyAnchor;V046.prepared=r.world;
    v046LegacyLoad(id,{...opts,force:true,geoDirect:true,noTravel:true,silent:true,spawn:r.pos.slice(),yaw:r.yaw});
    if(world!==r.world)throw Error('Scène de retour non publiée');
    V042_RUNTIME.active=new Map(r.active);V042_RUNTIME.npcData=new Map(r.npcData);V042_RUNTIME.worldId=world.id;
    V042_RUNTIME.nearest=r.nearest;V042_RUNTIME.instanceSite=null;
    state.player.pos=r.pos.slice();state.player.pitch=r.pitch;state.player.yaw=r.yaw;state.player.zone=world.id;
    V047.lastPoint=[r.pos[0],r.pos[2]];V047.nextWarmAt=performance.now()+500;
    V046.gate.cache.pin(v047CurrentResources());for(const[k,v]of r.raw)V046.gate.cache.set(k,v);
    mode='PLAYING';zoneTransitioning=false;V046.busy=false;V046.error=null;
    const validated=v047CurrentResources().length;
    V046.gate.status={phase:'ready',done:validated,total:validated,errors:[],origin:'retained-scene'};
    v046Loading({phase:'ready'});$('hud').classList.add('active');updateLocation();updateHUD();updateQuestUI(false);
    V048.returns.reused++;V048.returns.last={event:'return',site:r.site,bytes:r.bytes,scenePreserved:true};
    V048.retained=null;return true;
  } catch(e) {
    V046.prepared=null;world=rollback.world;V046.terrain=rollback.bank;V046.readyAnchor=rollback.readyAnchor;
    V042_RUNTIME.active=rollback.active;V042_RUNTIME.npcData=rollback.npcData;V042_RUNTIME.worldId=rollback.worldId;
    state.player.pos=rollback.pos;state.player.zone=rollback.zone;state.player.yaw=rollback.yaw;state.player.pitch=rollback.pitch;
    mode=rollback.mode;zoneTransitioning=false;V046.busy=false;v048DiscardReturn(String(e.message));return false;
  }
}
const v048LoadBase=loadZone;
loadZone=function(id,opts={}) {
  if(V015_GEO_MACROS[id]&&v048CanRestore(id,opts)&&v048RestoreExterior(id,opts))return true;
  if(V048.retained && id!==V042_INSTANCE_ZONE) {V048.returns.missed++;v048DiscardReturn('autre destination ou contexte différent');}
  return v048LoadBase(id,opts);
};
const v048NewGameBase=startNewGame;
startNewGame=function(...args){v048DiscardReturn('nouvelle partie');return v048NewGameBase(...args);};
/* The lab has its own retained exterior slot, isolated from a real campaign visit. */
const v048StartLabBase=v046StartLab;
v046StartLab=async function(){if(!V046.lab){V048.campaignReturn=V048.retained;V048.retained=null;}return v048StartLabBase();};
function v048LeaveLab(){const active=V046.lab,ok=v047LeaveLab();if(active&&ok){V048.retained=V048.campaignReturn||null;V048.campaignReturn=null;
  if(V048.retained)V048.retained.state=state;}return ok;}
