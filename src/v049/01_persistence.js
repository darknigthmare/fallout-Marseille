/* Living actors remember wounds/poses across streaming and instance rebuilds.
   Identity includes the site and inside/outside, never the current macro label. */
const V049={version:'0.49.0',identities:new Map(),owners:new WeakMap(),clock:0,lastBind:null,
 stats:{snapshots:0,restored:0,unloads:0,cycles:0,bodiesBound:0,duplicatesMerged:0},last:null};
for(const site of V042_CATALOG){
 for(let i=0;i<site.enemySlots;i++)for(const inside of [false,true]){
  if(inside&&!site.visitable)continue;const id=v042EnemyId(site,i,inside);
  V049.identities.set(id,{id,site:site.id,scope:inside?'inside':'outside',kind:'enemy'});
 }
 for(let i=0;i<site.npcSlots;i++){const id=`v042-npc:${site.id}:${i}`;V049.identities.set(id,{id,site:site.id,scope:'outside',kind:'npc'});}
}
function v049Fresh(){return {schema:1,actors:{}};}
const v049Base=baseState;baseState=function(){const s=v049Base();s.v049=v049Fresh();return s;};
function v049Identify(id){return V049.identities.get(id)||null;}
function v049Scope(w,meta){return !!(w&&meta&&(meta.scope==='outside'?w.geoMacro:w.id===V042_INSTANCE_ZONE&&(w.v049Site||state.v042?.activeInterior)===meta.site));}
function v049Own(w){if(w){V049.owners.set(w,state);if(w.id===V042_INSTANCE_ZONE)w.v049Site=state.v042?.activeInterior;}return w;}
function v049Allowed(w){return !!(w&&V049.owners.get(w)===state);}
function v049LimbMap(e){return {...(state.v025?.limbs?.[world?.id]?.[e.id]||{}),...(e.v025LimbLoss||{})};}
function v049CaptureActor(e,w=world){const meta=v049Identify(e?.id);if(!v049Allowed(w)||!v049Scope(w,meta))return null;
 const old=state.v049.actors[e.id],raw={...e,at:state.playTime||0,limbs:meta.kind==='enemy'?v049LimbMap(e):undefined};
 const snapshot=MistralEncounters.clean(raw,meta);if(!snapshot)return null;
 if(old?.alive===false||state.flags.enemyDead[e.id]){snapshot.alive=false;if(meta.kind==='enemy')snapshot.health=0;}
 state.v049.actors[e.id]=snapshot;V049.stats.snapshots++;return snapshot;
}
function v049Checkpoint(w=world,site=null){if(!v049Allowed(w))return 0;let n=0;for(const a of [...(w.enemies||[]),...(w.npcs||[])])if(!site||a.v042Site===site)n+=!!v049CaptureActor(a,w);return n;}
function v049Apply(a,w){const meta=v049Identify(a?.id);if(!meta)return a;let snap=state.v049.actors[a.id];
 if(!snap&&meta.kind==='enemy'){
  const olds=Object.entries(state.v022?.encounters||{}).filter(([k,v])=>k.endsWith('|'+a.id)&&v.type===a.type).map(([,v])=>v);
  if(olds.length){snap=MistralEncounters.clean({...a,health:Math.min(a.health,...olds.map(v=>v.health)),legDamage:Math.max(a.legDamage||0,...olds.map(v=>v.leg||0)),armDamage:Math.max(a.armDamage||0,...olds.map(v=>v.arm||0)),limbs:v049LimbMap(a),at:state.playTime},meta);if(snap)state.v049.actors[a.id]=snap;}
 }

 if(snap&&v049Scope(w,meta)){
  a.alive=snap.alive;
  for(const k of ['pos','home','yaw','phase','health','maxHealth','armDamage','legDamage','morale','maxMorale','alerted','state','lastKnown','searchTimer','attackCooldown','suppressed','speed','damage','armor','anim','routeIndex','routePause','activity'])if(Object.hasOwn(snap,k))a[k]=Array.isArray(snap[k])?snap[k].slice():snap[k];
  if(meta.kind==='enemy'){a.status={...snap.status};a.v025LimbLoss={...snap.limbs};a.v021Windup=null;}
  if(meta.kind==='enemy'&&state.v022)state.v022.encounters[w.id+'|'+a.id]={zone:w.id,type:a.type,health:a.health,leg:a.legDamage,arm:a.armDamage};
  V049.stats.restored++;V049.last={event:'restored',site:meta.site,id:a.id};
 }else if(!snap){const rng=detailRng('v049-actor:'+a.id);a.yaw=rng()*TAU;if(meta.kind==='enemy')a.phase=rng()*TAU;else{a.anim=rng()*TAU;a.routePause=rng()*2;}}
 return a;
}
const v049SpawnEnemies=v042SpawnEnemies;
v042SpawnEnemies=function(w,p,site,inside=false){
 v049Own(w);v042ResetRespawn(site);
 for(let i=0;i<site.enemySlots;i++){const id=v042EnemyId(site,i,inside);if(state.v049.actors[id]?.alive===false)state.flags.enemyDead[id]=true;}
 const result=v049SpawnEnemies(w,p,site,inside);for(const a of result)v049Apply(a,w);return result;
};
const v049SpawnNpcs=v042SpawnNpcs;
v042SpawnNpcs=function(w,p,site){v049Own(w);const ns=v049SpawnNpcs(w,p,site);for(const a of ns)v049Apply(a,w);return ns;};
/* Scope Math.random only to the synchronous site builder: decorative fragments
   cannot be re-rolled by entering the same sector from another direction. */
const v049SpawnSite=v042SpawnSite;
v042SpawnSite=function(w,site){const old=Math.random,rng=detailRng('v049-site:'+site.id);try{Math.random=rng;const rec=v049SpawnSite(w,site);v049BindBodies(w,true);return rec;}finally{Math.random=old;}};
const v049Unload=v042UnloadSite;
v042UnloadSite=function(id){v049Checkpoint(world,id);const out=v049Unload(id);if(out){V049.stats.unloads++;V049.last={event:'unloaded',site:id};V049.lastBind=null;}return out;};
const v049Damage=damageEnemy;
damageEnemy=function(e,...args){const r=v049Damage(e,...args);if(e&&v049Identify(e.id)){const changed=state.v025?.limbs?.[world?.id]?.[e.id];if(changed)e.v025LimbLoss={...(e.v025LimbLoss||{}),...changed};v049CaptureActor(e);}return r;};
const v049Loss=v025LimbLoss;
v025LimbLoss=function(e,id){return e?.v025LimbLoss?.[id]??(v049Identify(e?.id)?state.v049?.actors?.[e.id]?.limbs?.[id]:undefined)??v049Loss(e,id);};
/* A site can legitimately repopulate only after its declared game-time delay.
   Its entire previous encounter ledger, old limb maps and remains are retired. */
const v049Respawn=v042ResetRespawn;
v042ResetRespawn=function(site){if(site?.unique||site?.kind==='boss')return false;const changed=v049Respawn(site);if(!changed)return false;
 for(const[id,m]of V049.identities)if(m.site===site.id&&m.kind==='enemy'){delete state.v049.actors[id];for(const zone of Object.values(state.v025?.limbs||{}))delete zone[id];}
 for(const key of Object.keys(state.v022?.encounters||{}))if([...V049.identities.values()].some(m=>m.site===site.id&&key.endsWith('|'+m.id)))delete state.v022.encounters[key];
 for(const[key,c]of Object.entries(state.v026.containers))if(v049Identify(c.id?.slice(8))?.site===site.id&&c.kind==='remains')delete state.v026.containers[key];
 if(world){world.interactables=world.interactables.filter(i=>!(i.v049Body&&i.v042Site===site.id));}
 V049.lastBind=null;V049.stats.cycles++;return true;
};
