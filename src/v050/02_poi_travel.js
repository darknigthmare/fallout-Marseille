/* Territorial travel uses the same validated publication gate as walking.
   Quotes and transaction tokens are session state: no save-schema migration,
   map unlock, reward or elapsed time is written before a successful arrival. */
const V050_TRAVEL={serial:0,active:null,confirmation:null,last:null,completed:0,cancelled:0,failed:0};
function v050TravelPoint(site){
  const p=state.v046?.placements?.[site.id];
  return Array.isArray(p)&&p.length===3&&p.every(Number.isFinite)?p.slice():v015GeoProject(site.macro,site.lat,site.lon);
}
function v050TravelQuote(site){
  const p=v050TravelPoint(site),distance=Math.hypot(p[0]-state.player.pos[0],p[2]-state.player.pos[2]);
  return {distance,minutes:Math.max(5,Math.ceil(distance/4000*60))};
}
function v050TravelDuration(minutes){return minutes<60?`${minutes} min`:`${Math.floor(minutes/60)} h ${String(minutes%60).padStart(2,'0')}`;}
function v050TravelNearbyThreat(w=world,pos=state.player.pos){
  return !!inCombat||v020Danger()||(w?.enemies||[]).some(e=>e.alive&&Math.hypot(e.pos[0]-pos[0],e.pos[2]-pos[2])<40);
}
function v050TravelBlock(site,loading=false){
  if(!site||!v042SiteDiscovered(site))return 'Approchez-vous de ce lieu pour le découvrir avant de voyager.';
  if(!world?.v046||!world.geoMacro||state.v042.activeInterior)return 'Rejoignez le territoire extérieur pour voyager.';
  if(!(state.player.hp>0))return 'Le voyage est indisponible à zéro point de vie.';
  const ground=v047Height(v047Bank(world),state.player.pos[0],state.player.pos[2]).height;
  if(!onGround||ground===null||!Number.isFinite(ground)||v046SurfaceAt(state.player.pos,world.v046Records).water||collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]))
    return 'Rejoignez un sol stable et dégagé avant de voyager.';
  if(v050TravelNearbyThreat())return 'Voyage impossible : des ennemis vous menacent à proximité.';
  if(typeof V040!=='undefined'&&V040.active)return 'Quittez la traversée guidée avant de voyager.';
  if(state.v026?.carry&&v026MassTotal()>v026Capacity())return 'Allégez votre inventaire avant de voyager.';
  if(!loading&&(V046.busy||V047.pending||zoneTransitioning||V050_TRAVEL.active))return 'Un chargement est en cours. Attendez sa fin.';
  if(!loading&&(!v027CanAct()||V027.tab!=='map'))return 'Ouvrez la fiche du lieu sur la carte pour préparer le voyage.';
  if(v050TravelQuote(site).distance<90)return 'Vous êtes déjà à proximité de ce lieu.';
  return null;
}
function v050TravelCurrent(ctx){return !!ctx&&V050_TRAVEL.active===ctx&&ctx.state===state&&ctx.world===world&&!ctx.cancelled&&!ctx.applied;}
function v050TravelInvalidate(reason='annulation'){
  const ctx=V050_TRAVEL.active;V050_TRAVEL.confirmation=null;
  if(ctx&&!ctx.applied){ctx.cancelled=true;ctx.status='cancelled';V050_TRAVEL.cancelled++;V050_TRAVEL.last={id:ctx.id,site:ctx.site.id,status:'cancelled',reason};}
  V050_TRAVEL.active=null;return ctx;
}
function v050TravelGuard(ctx){
  if(!v050TravelCurrent(ctx))throw Error('Voyage abandonné : la session ou le lieu de départ a changé.');
  if(state.player.zone!==ctx.zone||state.player.pos.some((n,i)=>Math.abs(n-ctx.pos[i])>.02)||state.worldTime!==ctx.time)
    throw Error('Voyage abandonné : le point de départ a changé.');
  const blocked=v050TravelBlock(ctx.site,true);if(blocked)throw Error(blocked);
}
/* A usable arrival needs measured ground at its feet and in a walking margin.
   A road is walkable; a building, water polygon or missing tile is not. */
function v050TravelGround(stage,w,x,z,radius=.8){
  if(!Number.isFinite(x)||!Number.isFinite(z))return null;
  const [lat,lon]=v015GeoUnproject(w.id,x,z);if(!v046Region(lat,lon))return null;
  const b=w.bounds;if(b&&(x-radius<b[0]||x+radius>b[1]||z-radius<b[2]||z+radius>b[3]))return null;
  for(const[source,zoom]of [['base',14],['cadastre',16]]){
    const t=v017LonLatToTile(lat,lon,zoom),key=v046TileKey(source,zoom,Math.floor(t.x),Math.floor(t.y));
    if(!stage.records.has(key))return null;
  }
  const h=v047Height(stage.bank,x,z).height;if(h===null||!Number.isFinite(h)||v046SurfaceAt([x,0,z],stage.records).water)return null;
  const y=Math.max(0,h),head=y+1.83;
  const nearby=stage.records.v047Index?.solids.at(x,z)||stage.geoColliders;
  const gameplay=stage.v050GameplayColliders||(stage.v050GameplayColliders=w.colliders.filter(c=>!c.v046Tile));
  for(const c of [...nearby,...gameplay]){
    if(c.disabled||head<(c.minY??-Infinity)||y>(c.maxY??Infinity))continue;
    if(v017ColliderHit(c,x,z,radius))return null;
  }
  return y;
}
function v050TravelAnchor(stage,w,site){
  const raw=v015GeoProject(w.id,site.lat,site.lon),saved=state.v046?.placements?.[site.id];
  if(Array.isArray(saved)&&saved.length===3&&saved.every(Number.isFinite)){
    if(Math.hypot(saved[0]-raw[0],saved[2]-raw[2])>125)throw Error('Le point enregistré de ce lieu est invalide.');
    const y=v050TravelGround(stage,w,saved[0],saved[2],.4);
    if(y===null)throw Error('L’accès enregistré de ce lieu n’est pas praticable avec les données chargées.');
    return [saved[0],y,saved[2]];
  }
  const temp={...w,v046Records:stage.records,v047TerrainBank:stage.bank,colliders:stage.geoColliders};
  const candidates=[[0,0]];for(let r=14;r<=98;r+=14)for(let n=0;n<12;n++)candidates.push([Math.cos(n/12*TAU)*r,Math.sin(n/12*TAU)*r]);
  for(const[dx,dz]of candidates){const x=raw[0]+dx,z=raw[2]+dz,y=v050TravelGround(stage,w,x,z,2);
    if(y!==null&&!v046Blocked(temp,x,z))return[x,y,z];
  }
  throw Error('Aucun accès praticable au lieu dans les données chargées.');
}
function v050TravelArrival(stage,w,site,plan){
  const anchor=v050TravelAnchor(stage,w,site),actors=[...(w.enemies||[]),...(w.npcs||[]),...Object.values(state.v049?.actors||{}).filter(a=>a.scope==='outside')];
  for(const r of [22,28,36,48,64,80])for(let n=0;n<16;n++){
    const angle=n/16*TAU,x=anchor[0]+Math.sin(angle)*r,z=anchor[2]+Math.cos(angle)*r;
    // Keep the player inside the original, validated movement margin. The
    // loaded anchor stays at plan.p even when the final landing is offset.
    if(Math.hypot(x-plan.p[0],z-plan.p[2])>145)continue;
    const y=v050TravelGround(stage,w,x,z);if(y===null)continue;
    const margin=[[1,0],[-1,0],[0,1],[0,-1],[2.5,0],[-2.5,0],[0,2.5],[0,-2.5]];
    if(margin.some(([dx,dz])=>{const h=v050TravelGround(stage,w,x+dx,z+dz,.55);return h===null||Math.abs(h-y)>.65;}))continue;
    if(actors.some(a=>a.alive!==false&&Array.isArray(a.pos)&&Math.hypot(a.pos[0]-x,a.pos[2]-z)<(a.kind==='npc'||String(a.id).startsWith('v042-npc:')?3:18)))continue;
    if(Object.entries(state.v046?.placements||{}).some(([id,p])=>id!==site.id&&Array.isArray(p)&&Math.hypot(p[0]-x,p[2]-z)<18))continue;
    return {pos:[x,y,z],anchor,yaw:Math.atan2(anchor[0]-x,z-anchor[2])};
  }
  throw Error('Aucune arrivée dégagée et praticable près de ce lieu. Votre position est conservée.');
}
const v050TravelPrepareBase=v046Prepare;
v046Prepare=async function(plan,resources,w,signal){
  const task=V047.pending,ctx=task?.opts?.v050TravelId?V050_TRAVEL.active:null;
  if(ctx&&task.opts.v050TravelId===ctx.id)v050TravelGuard(ctx);
  const stage=await v050TravelPrepareBase(plan,resources,w,signal);
  if(!ctx||task?.opts?.v050TravelId!==ctx.id)return stage;
  MistralWork.check(signal);v050TravelGuard(ctx);
  const arrival=v050TravelArrival(stage,w,ctx.site,plan);
  MistralWork.check(signal);v050TravelGuard(ctx);
  ctx.arrival=arrival;task.opts.yaw=arrival.yaw;
  stage.v050Travel=ctx;stage.height=arrival.pos[1];return stage;
};
const v050TravelPublishBase=v046Publish;
v046Publish=function(w,stage,plan){
  const ctx=stage.v050Travel;if(ctx)v050TravelGuard(ctx);
  const result=v050TravelPublishBase(w,stage,plan);
  if(ctx){
    // Publish first with the ORIGINAL anchor, then let the existing Ensure
    // reposition to the verified landing. No frame can observe half a move.
    ctx.loadedAnchor=plan.p.slice();plan.p=ctx.arrival.pos.slice();ctx.published=true;
  }
  return result;
};
function v050TravelFinish(ctx){
  if(!v050TravelCurrent(ctx)||!ctx.published||!ctx.arrival)return false;
  const expected=[ctx.arrival.pos[0],ctx.arrival.pos[1]+playerEyeHeight(),ctx.arrival.pos[2]];
  if(state.player.pos.some((n,i)=>Math.abs(n-expected[i])>.02))return false;
  ctx.applied=true;ctx.status='complete';
  state.worldTime=((ctx.time+ctx.quote.minutes/60)%24+24)%24;
  state.player.pitch=0;jumpVelocity=0;onGround=true;state.v046.placements[ctx.site.id]=ctx.arrival.anchor.slice();
  state.v046.lastLocation=v015GeoUnproject(world.id,state.player.pos[0],state.player.pos[2]);
  state.geo.lastMacro=world.id;state.geo.visitedMacros[world.id]=true;state.v018.travelMode='geographic';
  V050_TRAVEL.completed++;V050_TRAVEL.last={id:ctx.id,site:ctx.site.id,status:'complete',minutes:ctx.quote.minutes,distance:Math.round(ctx.quote.distance),arrival:state.player.pos.slice(),loadedAnchor:ctx.loadedAnchor.slice()};
  V050_TRAVEL.active=null;V050_TRAVEL.confirmation=null;
  closePipboy();updateLocation();updateQuestUI(false);updateHUD();
  toast(`ARRIVÉE · ${ctx.site.name} · ${v050TravelDuration(ctx.quote.minutes)} écoulées`,'good');return true;
}
const v050TravelEnsureBase=v046Ensure;
v046Ensure=async function(lat,lon,w=world,initial=false,opts={}){
  const id=opts.v050TravelId,ctx=id?V050_TRAVEL.active:null;
  if(id&&(!ctx||ctx.id!==id||!v050TravelCurrent(ctx)))return false;
  if(!id&&V050_TRAVEL.active)v050TravelInvalidate('autre chargement');
  if(ctx){ctx.status='loading';ctx.published=false;ctx.arrival=null;}
  const ok=await v050TravelEnsureBase(lat,lon,w,initial,opts);
  if(!ctx)return ok;
  if(ok)return v050TravelFinish(ctx);
  if(v050TravelCurrent(ctx)){ctx.status='failed';V050_TRAVEL.failed++;V050_TRAVEL.last={id:ctx.id,site:ctx.site.id,status:'failed',reason:V046.error?.[0]?.message||'Données ou arrivée indisponibles'};}
  else if(V050_TRAVEL.active===ctx)v050TravelInvalidate('session modifiée');
  return false;
};
const v050TravelCancelBase=v046Cancel;
v046Cancel=function(){v050TravelInvalidate();const out=v050TravelCancelBase();if(mode==='PIP'&&V027.tab==='map')renderPipboy();return out;};
const v050TravelLoadBase=loadZone;
loadZone=function(...args){if(V050_TRAVEL.active)v050TravelInvalidate('changement de lieu');V050_TRAVEL.confirmation=null;return v050TravelLoadBase(...args);};
const v050TravelNewBase=startNewGame;
startNewGame=function(...args){v050TravelInvalidate('nouvelle partie');return v050TravelNewBase(...args);};
function v050TravelRequest(id,confirmed=false){
  const site=v042Site(id),blocked=v050TravelBlock(site);
  if(blocked){toast(blocked,'bad');return false;}
  if(!confirmed){V050_TRAVEL.confirmation={site:id,state,world};renderPipboy();return true;}
  const confirmation=V050_TRAVEL.confirmation;
  if(!confirmation||confirmation.site!==id||confirmation.state!==state||confirmation.world!==world)return false;
  const quote=v050TravelQuote(site),ctx={id:++V050_TRAVEL.serial,site,state,world,zone:state.player.zone,pos:state.player.pos.slice(),time:state.worldTime,quote,status:'loading',cancelled:false,applied:false,published:false};
  V050_TRAVEL.active=ctx;V050_TRAVEL.confirmation=null;
  return v046Ensure(site.lat,site.lon,world,false,{v046Reposition:true,v050TravelId:ctx.id,noTravel:true});
}
function v050TravelCardHTML(site){
  const blocked=v050TravelBlock(site),quote=world?.v046?v050TravelQuote(site):null;
  const confirmation=V050_TRAVEL.confirmation?.site===site.id&&V050_TRAVEL.confirmation?.state===state;
  return `<section class="v050-travel"><h3>VOYAGE RAPIDE</h3>${quote?`<p>${(quote.distance/1000).toFixed(2)} km à vol d’oiseau · durée estimée : <strong>${v050TravelDuration(quote.minutes)}</strong>.</p>`:''}<p>${blocked?v027Escape(blocked):'Arrivée à proximité du repère. Le temps avance uniquement lorsque le voyage aboutit.'}</p>${confirmation&&!blocked?`<div class="p27-confirm" role="group" aria-label="Confirmer le voyage vers ${v027Escape(site.name)}"><h3>Rejoindre ${v027Escape(site.name)} ?</h3><p>${v050TravelDuration(quote.minutes)} seront ajoutées à l’heure du monde. Aucun coût en capsules.</p>${v027Button('Confirmer le voyage','v050-travel-confirm',site.id)}${v027Button('Rester ici','v050-travel-cancel')}</div>`:v027Button('Préparer le voyage','v050-travel',site.id,!!blocked)}</section>`;
}
const v050TravelLayerPanelBase=v042LayerPanel;
v042LayerPanel=function(c){
  const result=v050TravelLayerPanelBase(c),site=v042Site(state.v042.tracked),card=c.querySelector('.v42-tracked');
  if(site&&v042SiteDiscovered(site)&&card)card.insertAdjacentHTML('beforeend',v050TravelCardHTML(site));
  return result;
};
const v050TravelDispatchBase=v027Dispatch;
v027Dispatch=function(action,arg=''){
  if(action==='v050-travel')return v050TravelRequest(arg);
  if(action==='v050-travel-confirm')return v050TravelRequest(arg,true);
  if(action==='v050-travel-cancel'){if(!v027CanAct())return false;V050_TRAVEL.confirmation=null;renderPipboy();return true;}
  if(['v042-track','v042-untrack','tab','sub','close'].includes(action))V050_TRAVEL.confirmation=null;
  return v050TravelDispatchBase(action,arg);
};
/* A macro label is no longer a scene boundary. Both the nearby list and the
   tracked marker must continue to work across that label, including clears. */
const v050TravelNearestBase=v042NearestDiscovered;
v042NearestDiscovered=function(limit=8){if(!world?.v046)return v050TravelNearestBase(limit);
  return V042_CATALOG.filter(v042SiteDiscovered).map(s=>({s,d:v042DistancePos(state.player.pos,v050TravelPoint(s))})).sort((a,b)=>a.d-b.d||a.s.id.localeCompare(b.s.id)).slice(0,limit);
};
const v050TravelMarkerBase=getObjectiveMarker;
getObjectiveMarker=function(){
  const s=v042Site(state.v042.activeContract||state.v042.tracked);
  if(world?.v046&&s&&v042SiteDiscovered(s)){const p=v050TravelPoint(s);return {zone:world.id,pos:[p[0],v042Ground(world,p[0],p[2])+1.4,p[2]],label:s.name};}
  return v050TravelMarkerBase();
};
const v050TravelQuestBase=updateQuestUI;
updateQuestUI=function(flash=false){const out=v050TravelQuestBase(flash),site=v042Site(state.v042.tracked);
  if(!state.v042.activeContract&&site&&v042SiteDiscovered(site)&&v042SiteCleared(site)){
    $('questTitle').textContent='REPÈRE TERRITORIAL';$('questObjective').textContent='Rejoindre : '+site.name;
  }
  return out;
};
const v050TravelHudBase=v042UpdateHud;
v042UpdateHud=function(){const out=v050TravelHudBase(),site=V042_RUNTIME.nearest?.site;
  if(site&&!v042SiteDiscovered(site)){const el=$('v042LayerHud');if(el&&!el.classList.contains('hidden')){el.querySelector('b').textContent='SIGNATURE INCONNUE';el.querySelector('span').textContent=`Approchez pour identifier ce lieu · ${Math.round(V042_RUNTIME.nearest.d)} m`;}}
  return out;
};
function v050TravelInfo(){const c=V050_TRAVEL.active;return {completed:V050_TRAVEL.completed,cancelled:V050_TRAVEL.cancelled,failed:V050_TRAVEL.failed,confirmation:V050_TRAVEL.confirmation?.site||null,pending:c?{id:c.id,site:c.site.id,status:c.status,minutes:c.quote.minutes}:null,last:V050_TRAVEL.last};}
function v050TravelAfterInit(){
  V027_SUBS.map.fallout='LIEUX ET VOYAGES';
  Object.assign(window.__MISTRAL_DEBUG,{v050TravelInfo,v050TravelRequest,v050TravelBlock:id=>v050TravelBlock(v042Site(id)),v050TravelQuote:id=>{const s=v042Site(id);return s?v050TravelQuote(s):null;},v050TravelNearby:()=>v042NearestDiscovered().map(r=>({id:r.s.id,distance:r.d})),v050TravelMarker:()=>getObjectiveMarker(),v050TravelRetry:()=>{const c=V050_TRAVEL.active,p=V046.last;return c?.status==='failed'&&p?.opts?.v050TravelId===c.id?v046Ensure(p.lat,p.lon,p.w,p.initial,p.opts):false;},v027Dispatch,v046Cancel});
}
