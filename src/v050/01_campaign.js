/* The airlock commits its campaign progress only after a measured, walkable
   exterior has been published. Authored workshops remain an explicit narrative
   scene, connected by a physical gateway and a persistent geographic return. */
const V050_CAMPAIGN_POINT=[43.2966,5.5708];
const V050_CAMPAIGN={serial:0,active:null,last:null,completed:0,cancelled:0,failed:0};
const V050_CAMPAIGN_GATE='v050-campaign-workshops';
const V050_CAMPAIGN_RETURN='v050-campaign-territory';
function v050CampaignFresh(){return{schema:1,route:null,gateway:null,returnPoint:null,workshopVisits:0};}
function v050CampaignPosition(p){return Array.isArray(p)&&p.length===3&&p.every(Number.isFinite);}
function v050CampaignReturnPoint(r){
  if(!r||!V015_GEO_MACROS[r.macro]||!v050CampaignPosition(r.pos)||!v046Region(...v015GeoUnproject(r.macro,r.pos[0],r.pos[2])))return null;
  return{macro:r.macro,pos:r.pos.slice(),yaw:Number.isFinite(r.yaw)?r.yaw:0,pitch:Number.isFinite(r.pitch)?clamp(r.pitch,-1.3,1.3):0};
}
const v050CampaignBaseState=baseState;
baseState=function(){const s=v050CampaignBaseState();s.v050Campaign=v050CampaignFresh();return s;};
const v050CampaignMigrateBase=migrateState;
migrateState=function(input={}){
  const s=v050CampaignMigrateBase(input),old=input.v050Campaign||{},fresh=v050CampaignFresh();
  const raw=v015GeoProject('geo_huveaune',...V050_CAMPAIGN_POINT),p=old.gateway;
  s.v050Campaign={...fresh,route:['geographic','story'].includes(old.route)?old.route:null,
    gateway:v050CampaignPosition(p)&&Math.hypot(p[0]-raw[0],p[2]-raw[2])<=125?p.slice():null,
    returnPoint:v050CampaignReturnPoint(old.returnPoint),workshopVisits:Math.max(0,Math.floor(Number(old.workshopVisits)||0))};
  return s;
};
state=migrateState(state);if(world)v049Own(world);

function v050CampaignCurrent(ctx){return!!ctx&&V050_CAMPAIGN.active===ctx&&ctx.state===state&&!ctx.cancelled&&!ctx.applied;}
function v050CampaignGuard(ctx){
  if(!v050CampaignCurrent(ctx)||world!==ctx.departure||state.player.zone!==ctx.zone)
    throw Error('Passage abandonné : la session ou le lieu de départ a changé.');
  if(state.player.pos.some((n,i)=>Math.abs(n-ctx.pos[i])>.02)||state.worldTime!==ctx.time||
    state.v035.prologue.stage!==ctx.prologueStage||state.v035.prologue.complete!==ctx.prologueComplete||state.quest.main!==ctx.main)
    throw Error('Passage abandonné : la situation de départ a changé.');
}
function v050CampaignInvalidate(reason='annulation'){
  const ctx=V050_CAMPAIGN.active;
  if(ctx&&!ctx.applied){ctx.cancelled=true;ctx.status='cancelled';V050_CAMPAIGN.cancelled++;V050_CAMPAIGN.last={id:ctx.id,kind:ctx.kind,status:'cancelled',reason};}
  V050_CAMPAIGN.active=null;return ctx;
}
function v050CampaignBegin(kind){
  const ctx={id:++V050_CAMPAIGN.serial,kind,state,departure:world,zone:state.player.zone,pos:state.player.pos.slice(),time:state.worldTime,
    prologueStage:state.v035.prologue.stage,prologueComplete:state.v035.prologue.complete,main:state.quest.main,
    snapshot:deepClone(state),status:'loading',applied:false,cancelled:false,published:false,arrival:null,
    bank:V046.terrain,readyAnchor:V046.readyAnchor,active:new Map(V042_RUNTIME.active),npcData:new Map(V042_RUNTIME.npcData),
    worldId:V042_RUNTIME.worldId,nearest:V042_RUNTIME.nearest,loaded:new Map(V017_RUNTIME.loaded)};
  V050_CAMPAIGN.active=ctx;return ctx;
}
function v050CampaignRollback(ctx){
  // A failed publication may only restore the transaction's own scene/state.
  // It must never copy the old campaign over a subsequently loaded save.
  if(!v050CampaignCurrent(ctx)||!ctx.published||world!==ctx.target)return false;
  const restored=deepClone(ctx.snapshot);for(const k of Object.keys(state))delete state[k];Object.assign(state,restored);
  world=ctx.departure;V046.terrain=ctx.bank;V046.readyAnchor=ctx.readyAnchor;V046.prepared=null;
  V042_RUNTIME.active=new Map(ctx.active);V042_RUNTIME.npcData=new Map(ctx.npcData);V042_RUNTIME.worldId=ctx.worldId;V042_RUNTIME.nearest=ctx.nearest;
  V017_RUNTIME.loaded=new Map(ctx.loaded);V049.lastBind=null;v049Own(world);
  ctx.published=false;ctx.arrival=null;updateLocation();updateQuestUI(false);updateHUD();return true;
}
function v050CampaignFailed(ctx,message){
  if(!v050CampaignCurrent(ctx))return false;
  v050CampaignRollback(ctx);ctx.status='failed';V050_CAMPAIGN.failed++;
  V050_CAMPAIGN.last={id:ctx.id,kind:ctx.kind,status:'failed',reason:String(message||'Le passage n’est pas prêt.')};return false;
}
/* The legacy scene loader autosaves during its final synchronous publication.
   Hold that save until the route and campaign progress form one complete state. */
const v050CampaignSaveBase=saveGame;
saveGame=function(...args){const c=V050_CAMPAIGN.active;if(v050CampaignCurrent(c))return false;return v050CampaignSaveBase(...args);};

function v050CampaignArrival(stage,w,ctx,plan){
  if(ctx.returnPoint){
    const r=ctx.returnPoint,[x,,z]=r.pos,y=v050TravelGround(stage,w,x,z,.6);
    if(y===null)throw Error('Le point de retour enregistré n’est plus praticable. Les ateliers restent accessibles.');
    for(const[dx,dz]of [[.8,0],[-.8,0],[0,.8],[0,-.8]]){
      const h=v050TravelGround(stage,w,x+dx,z+dz,.4);
      if(h===null||Math.abs(h-y)>.65)throw Error('La sortie des ateliers ne dispose pas d’une marge de marche sûre.');
    }
    return{pos:[x,y,z],anchor:state.v050Campaign.gateway?.slice()||null,yaw:r.yaw,pitch:r.pitch};
  }
  const site={id:V050_CAMPAIGN_GATE,macro:w.id,lat:V050_CAMPAIGN_POINT[0],lon:V050_CAMPAIGN_POINT[1]};
  const arrival=v050TravelArrival(stage,w,site,plan);arrival.pitch=0;return arrival;
}
const v050CampaignPrepareBase=v046Prepare;
v046Prepare=async function(plan,resources,w,signal){
  const task=V047.pending,ctx=task?.opts?.v050CampaignId?V050_CAMPAIGN.active:null;
  if(ctx&&task.opts.v050CampaignId===ctx.id)v050CampaignGuard(ctx);
  const stage=await v050CampaignPrepareBase(plan,resources,w,signal);
  if(!ctx||task?.opts?.v050CampaignId!==ctx.id)return stage;
  MistralWork.check(signal);v050CampaignGuard(ctx);
  ctx.arrival=v050CampaignArrival(stage,w,ctx,plan);MistralWork.check(signal);v050CampaignGuard(ctx);
  task.opts.yaw=ctx.arrival.yaw;stage.height=ctx.arrival.pos[1];stage.v050Campaign=ctx;return stage;
};
const v050CampaignPublishBase=v046Publish;
v046Publish=function(w,stage,plan){
  const ctx=stage.v050Campaign;if(ctx)v050CampaignGuard(ctx);
  const result=v050CampaignPublishBase(w,stage,plan);
  if(ctx){ctx.loadedAnchor=plan.p.slice();plan.p=ctx.arrival.pos.slice();ctx.published=true;}
  return result;
};
function v050CampaignCompletePrologue(route){
  state.v035.prologue.complete=true;state.v035.prologue.stage=9;state.quest.main=Math.max(2,state.quest.main);
  state.player.discovered=[...new Set(state.player.discovered.filter(id=>id!=='vault_prologue').concat(['vault']))];
  state.v050Campaign.route=route;
}
function v050CampaignFinishMap(ctx){
  if(!v050CampaignCurrent(ctx)||!ctx.published||world!==ctx.target||!ctx.arrival)return false;
  const p=ctx.arrival.pos,expected=[p[0],p[1]+playerEyeHeight(),p[2]];
  if(state.player.pos.some((n,i)=>Math.abs(n-expected[i])>.02))return v050CampaignFailed(ctx,'La position publiée diffère de l’arrivée contrôlée.');
  if(ctx.kind==='exit')v050CampaignCompletePrologue('geographic');
  state.v018.travelMode='geographic';state.player.pitch=ctx.arrival.pitch||0;jumpVelocity=0;onGround=true;
  state.geo.lastMacro=world.id;state.geo.visitedMacros[world.id]=true;
  state.v046.lastLocation=v015GeoUnproject(world.id,p[0],p[2]);
  if(ctx.arrival.anchor)state.v050Campaign.gateway=ctx.arrival.anchor.slice();
  state.v050Campaign.returnPoint={macro:world.id,pos:state.player.pos.slice(),yaw:state.player.yaw,pitch:state.player.pitch};
  v050CampaignAttachGateway(world);ctx.applied=true;ctx.status='complete';V050_CAMPAIGN.completed++;
  V050_CAMPAIGN.last={id:ctx.id,kind:ctx.kind,status:'complete',arrival:state.player.pos.slice(),loadedAnchor:ctx.loadedAnchor.slice(),real:!V046.lab};V050_CAMPAIGN.active=null;
  updateLocation();updateQuestUI(true);updateHUD();saveGame(false);
  toast(ctx.kind==='exit'?'AUBAGNE · Rejoignez la balise des ateliers pour retrouver Mireille.':'Retour au territoire · position géographique retrouvée.','good');return true;
}
const v050CampaignEnsureBase=v046Ensure;
v046Ensure=async function(lat,lon,w=world,initial=false,opts={}){
  const id=opts.v050CampaignId,ctx=id?V050_CAMPAIGN.active:null;
  if(id&&(!ctx||ctx.id!==id||!v050CampaignCurrent(ctx)))return false;
  if(!id&&V050_CAMPAIGN.active)v050CampaignInvalidate('autre chargement');
  if(ctx){ctx.status='loading';ctx.arrival=null;ctx.published=false;}
  const ok=await v050CampaignEnsureBase(lat,lon,w,initial,opts);
  if(!ctx)return ok;
  if(ok)return v050CampaignFinishMap(ctx);
  if(v050CampaignCurrent(ctx))v050CampaignFailed(ctx,V046.error?.[0]?.message);
  else if(V050_CAMPAIGN.active===ctx)v050CampaignInvalidate('session modifiée');
  return false;
};
const v050CampaignCancelBase=v046Cancel;
v046Cancel=function(){v050CampaignInvalidate();return v050CampaignCancelBase();};
const v050CampaignLoadBase=loadZone;
loadZone=function(id,opts={}){
  const ctx=V050_CAMPAIGN.active;if(ctx&&opts.v050CampaignId!==ctx.id)v050CampaignInvalidate('changement de lieu');
  return v050CampaignLoadBase(id,opts);
};
const v050CampaignNewBase=startNewGame;
startNewGame=function(...args){v050CampaignInvalidate('nouvelle partie');return v050CampaignNewBase(...args);};

function v050CampaignReady(){return!V050_CAMPAIGN.active&&!V046.busy&&!V047.pending&&!zoneTransitioning&&state.player.hp>0&&['PLAYING','DIALOGUE'].includes(mode);}
function v050CampaignLoadMap(kind){
  if(!v050CampaignReady())return false;
  if(kind==='exit'&&(world?.id!=='vault_prologue'||state.v035.prologue.stage<8||state.v035.prologue.complete))return false;
  if(kind==='return'&&world?.id!=='aubagne')return false;
  closeDialogue();const ctx=v050CampaignBegin(kind);
  ctx.returnPoint=kind==='return'?v050CampaignReturnPoint(state.v050Campaign.returnPoint):null;
  const ll=ctx.returnPoint?v015GeoUnproject(ctx.returnPoint.macro,ctx.returnPoint.pos[0],ctx.returnPoint.pos[2]):V050_CAMPAIGN_POINT;
  ctx.target=v046World(v046Region(...ll));
  return v046Ensure(...ll,ctx.target,true,{v046Reposition:true,v050CampaignId:ctx.id,noTravel:true,force:true,silent:true,geoDirect:true});
}
function v050CampaignLoadStory(kind){
  if(!v050CampaignReady())return false;
  if(kind==='story-exit'&&(world?.id!=='vault_prologue'||state.v035.prologue.stage<8||state.v035.prologue.complete))return false;
  if(kind==='workshops'&&!v050CampaignNear(V050_CAMPAIGN_GATE))return false;
  closeDialogue();const ctx=v050CampaignBegin(kind),point=world?.v046?{macro:world.id,pos:state.player.pos.slice(),yaw:state.player.yaw,pitch:state.player.pitch}:null;
  try{
    loadZone('aubagne',{instance:true,force:true,silent:true,noTravel:true,v050CampaignId:ctx.id});ctx.target=world;ctx.published=world?.id==='aubagne';
    if(!v050CampaignCurrent(ctx)||!ctx.published||world===ctx.departure)throw Error('Les ateliers n’ont pas été chargés.');
    if(kind==='story-exit')v050CampaignCompletePrologue('story');
    if(point)state.v050Campaign.returnPoint=point;
    state.v018.travelMode='story';state.v050Campaign.workshopVisits++;v050CampaignAttachNarrativeReturn(world);
    ctx.applied=true;ctx.status='complete';V050_CAMPAIGN.completed++;V050_CAMPAIGN.last={id:ctx.id,kind,status:'complete',zone:'aubagne',real:false};V050_CAMPAIGN.active=null;
    updateLocation();updateQuestUI(true);updateHUD();saveGame(false);return true;
  }catch(e){v050CampaignFailed(ctx,e.message);v050CampaignInvalidate('entrée interrompue');toast('Passage interrompu : '+String(e.message||e),'bad');return false;}
}
v35pExit=function(){
  if(world?.id!=='vault_prologue'||state.v035.prologue.stage<8||state.v035.prologue.complete||!v050CampaignReady())return false;
  openDialogue(speaker('SAS 2','SURFACE · AUBAGNE','A3'),
    'Pression stable. La sortie ouvre le territoire d’Aubagne. Une balise des ateliers vous permettra de rejoindre Mireille et la suite de la campagne dans une scène narrative.',[
      {text:'Sortir vers Aubagne',onChoose:()=>v050CampaignLoadMap('exit')},
      {text:'Rejoindre directement les ateliers — scène narrative',onChoose:()=>v050CampaignLoadStory('story-exit')},
      {text:'Rester dans l’abri',onChoose:closeDialogue}]);return true;
};
function v050CampaignNear(id){const it=world?.interactables.find(i=>i.id===id);return!!it&&Math.hypot(it.pos[0]-state.player.pos[0],it.pos[2]-state.player.pos[2])<=it.radius+.25;}
function v050CampaignOpenWorkshops(){
  if(!world?.v046||!v050CampaignNear(V050_CAMPAIGN_GATE)||!v050CampaignReady())return false;
  if(v050TravelNearbyThreat()){toast('Mettez-vous à l’abri du danger avant de rejoindre les ateliers.','bad');return false;}
  openDialogue(speaker('ATELIERS D’AUBAGNE','PASSAGE VERS LA CAMPAGNE','AB'),
    'Mireille Barral vous attend dans les ateliers. Cette entrée mène à la scène narrative de la campagne. Votre point sur la carte est conservé pour le retour.',[
      {text:'Entrer dans les ateliers — scène narrative',onChoose:()=>v050CampaignLoadStory('workshops')},
      {text:'Continuer l’exploration',onChoose:closeDialogue}]);return true;
}
function v050CampaignOpenReturn(){
  if(world?.id!=='aubagne'||!v050CampaignNear(V050_CAMPAIGN_RETURN)||!v050CampaignReady())return false;
  if(v050TravelNearbyThreat()){toast('Éloignez le danger avant de regagner le territoire.','bad');return false;}
  openDialogue(speaker('SORTIE DES ATELIERS','TERRITOIRE D’AUBAGNE','AB'),
    state.v050Campaign.returnPoint?'Reprendre l’exploration au point géographique conservé ? Votre progression dans les ateliers et votre inventaire restent acquis.':'Rejoindre le territoire d’Aubagne ? La sortie sera préparée sur un sol mesuré et dégagé.',[
      {text:'Retourner au territoire d’Aubagne',onChoose:()=>v050CampaignLoadMap('return')},
      {text:'Rester dans les ateliers',onChoose:closeDialogue}]);return true;
}
function v050CampaignAttachGateway(w){
  const p=state.v050Campaign.gateway;if(!w?.v046||!p||w.interactables.some(i=>i.id===V050_CAMPAIGN_GATE))return;
  const h=v047Height(v047Bank(w),p[0],p[2]).height;if(h===null)return;
  const[x,,z]=p,y=Math.max(0,h);
  addBox(w,[x,y+1.35,z],[.22,2.7,.22],COLORS.darkMetal);
  addBox(w,[x,y+2.25,z],[2.3,.75,.14],COLORS.amber,0,{emissive:.16});
  v021Sign(w,x,y+2.27,z+.1,'ATELIERS',.062);
  addInteract(w,V050_CAMPAIGN_GATE,[x,y+1.2,z],'Ateliers d’Aubagne — poursuivre la campagne',v050CampaignOpenWorkshops,{kind:'door',radius:4.5,priority:8,marker:true});
  w.subzones.push({id:V050_CAMPAIGN_GATE,name:'Accès aux ateliers · campagne',pos:[x,y,z]});
}
function v050CampaignAttachNarrativeReturn(w){
  if(w?.id!=='aubagne'||w.interactables.some(i=>i.id===V050_CAMPAIGN_RETURN))return;
  w.name='Ateliers d’Aubagne · scène narrative';
  const p=ldFindFree(w,w.spawn[0]+5,w.spawn[2]-4),[x,y,z]=p;
  addBox(w,[x,y+1.1,z],[.22,2.2,.22],COLORS.darkMetal);v021Sign(w,x,y+1.8,z,'TERRITOIRE',.065);
  addInteract(w,V050_CAMPAIGN_RETURN,[x,y+1.1,z],'Retourner au territoire d’Aubagne',v050CampaignOpenReturn,{kind:'door',radius:4,priority:8,marker:true});
}
const v050CampaignBuildBase=buildWorld;
buildWorld=function(id){const w=v050CampaignBuildBase(id);v050CampaignAttachGateway(w);if(id==='aubagne')v050CampaignAttachNarrativeReturn(w);return w;};
const v050CampaignRegionBase=worldRegionLabel;
worldRegionLabel=function(id){return id==='aubagne'?'PAYS D’AUBAGNE · SCÈNE NARRATIVE':v050CampaignRegionBase(id);};
function v050CampaignGuidance(){return!!world?.v046&&!!state.v050Campaign.gateway&&state.mode!=='free'&&!state.v042.activeContract&&!state.v042.tracked&&!state.v046.lore.side;}
const v050CampaignMarkerBase=getObjectiveMarker;
getObjectiveMarker=function(){if(v050CampaignGuidance()){const p=state.v050Campaign.gateway;return{zone:world.id,pos:[p[0],p[1]+2.8,p[2]],label:'Ateliers d’Aubagne — campagne'};}return v050CampaignMarkerBase();};
const v050CampaignQuestBase=updateQuestUI;
updateQuestUI=function(flash=false){const result=v050CampaignQuestBase(flash);if(v050CampaignGuidance()){
  $('questTitle').textContent='LA CAMPAGNE · ATELIERS D’AUBAGNE';$('questObjective').textContent='Rejoignez la balise des ateliers pour poursuivre avec Mireille (scène narrative).';
}return result;};
function v050CampaignInfo(){
  const c=V050_CAMPAIGN.active,it=world?.interactables.find(i=>i.id===(world.v046?V050_CAMPAIGN_GATE:V050_CAMPAIGN_RETURN));
  return{saved:deepClone(state.v050Campaign),prologue:deepClone(state.v035.prologue),main:state.quest.main,zone:world?.id,
    pending:c?{id:c.id,kind:c.kind,status:c.status}:null,last:V050_CAMPAIGN.last,completed:V050_CAMPAIGN.completed,cancelled:V050_CAMPAIGN.cancelled,failed:V050_CAMPAIGN.failed,
    gateway:it?{id:it.id,label:it.label,pos:it.pos.slice(),radius:it.radius}:null};
}
function v050CampaignAfterInit(){Object.assign(window.__MISTRAL_DEBUG,{v35pExit,v050CampaignInfo,v050CampaignOpenWorkshops,v050CampaignOpenReturn,
  v050CampaignRetry:()=>{const c=V050_CAMPAIGN.active,p=V046.last;return c?.status==='failed'&&p?.opts?.v050CampaignId===c.id?v046Ensure(p.lat,p.lon,p.w,p.initial,p.opts):false;}});}
