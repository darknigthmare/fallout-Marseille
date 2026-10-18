/* A corpse ledger belongs to an encounter, not to the region label shown by
   the HUD. Existing partial inventories remain authoritative and finite. */
function v049BodyIdentity(id){return typeof id==='string'&&id.startsWith('remains:')?v049Identify(id.slice(8)):null;}
function v049BodyKey(c){return 'territory|'+c.id;}
const v049Key=v026Key;v026Key=function(zone,id){return v049BodyIdentity(id)?v049BodyKey({id}):v049Key(zone,id);};
function v049NormalizeBodies(s){
 const normalized={};for(const[key,c]of Object.entries(s.v026?.containers||{})){
  const meta=v049BodyIdentity(c.id);if(!meta||c.kind!=='remains'){normalized[key]=c;continue;}
  const k=v049BodyKey(c),old=normalized[k];
  if(old){old.items=MistralEncounters.remainder(old.items,c.items);old.permission||=c.permission;old.visited||=c.visited;V049.stats.duplicatesMerged++;}
  else normalized[k]=c;
 }
 if(s.v026)s.v026.containers=normalized;
}
const v049Migrate=migrateState;
migrateState=function(input={}){const s=v049Migrate(input);s.v049=MistralEncounters.migrate(input.v049,v049Identify);v049NormalizeBodies(s);return s;};
state=migrateState(state);if(world)v049Own(world);
function v049TagBody(w,key,c){const meta=v049BodyIdentity(c.id);if(!meta)return;
 const it=w.interactables.find(i=>i.id==='v026:'+key);if(it){it.v042Site=meta.site;it.v049Body=true;}
}
const v049Container=v026NewContainer;
v026NewContainer=function(w,id,...args){const out=v049Container(w,id,...args),c=out[1];if(v049BodyIdentity(id)){c.zone=w.id;V049.lastBind=null;}return out;};
const v049Attach=v026Attach;
v026Attach=function(w,key,c){const r=v049Attach(w,key,c);v049TagBody(w,key,c);return r;};
function v049BindBodies(w=world,force=false){if(!w||!state.v026)return 0;
 const scope=w.geoMacro?'outside':w.id===V042_INSTANCE_ZONE?'inside:'+ (w.v049Site||state.v042.activeInterior):null;
 const token=w.id+':'+scope+':'+Object.keys(state.v026.containers).length+':'+V042_RUNTIME.active.size;
 if(!force&&V049.lastBind?.w===w&&V049.lastBind.token===token&&V049.lastBind.state===state)return 0;
 V049.lastBind={w,token,state};let n=0;
 for(const[key,c]of Object.entries(state.v026.containers)){
  const meta=v049BodyIdentity(c.id);if(!meta||c.kind!=='remains')continue;
  const current=v049Scope(w,meta);c.zone=current?w.id:'v049_inactive';
  if(!current)continue;
  // Recreate only the interaction, never its contents/reward. Distant bodies
  // remain lightweight save entries and will bind on the next streamed visit.
  const active=meta.scope==='inside'||V042_RUNTIME.active.has(meta.site);
  if(active){v026Attach(w,key,c);n++;}
 }
 V049.stats.bodiesBound+=n;return n;
}
const v049Kill=killEnemy;
killEnemy=function(e){const meta=v049Identify(e?.id);if(meta&&(state.flags.enemyDead[e.id]||e.alive===false))return;
 const r=v049Kill(e);if(meta){v049CaptureActor(e);V049.lastBind=null;v049BindBodies(world,true);}return r;
};
const v049Draws=collectDraws;
collectDraws=function(t){v049BindBodies();return v049Draws(t);};
/* Ownership guards prevent an old scene from being copied into a newly loaded
   snapshot. This matters for manual slots and restoration out of the test lab. */
const v049Build=buildWorld;
buildWorld=function(id){const w=v049Build(id);v049Own(w);v049BindBodies(w,true);return w;};
const v049Load=loadZone;
loadZone=function(...args){v049Checkpoint();return v049Load(...args);};
const v049Enter=v042EnterSite;
v042EnterSite=function(id){v049Checkpoint();return v049Enter(id);};
const v049Save=saveGame;
saveGame=function(...args){v049Checkpoint();return v049Save(...args);};
const v049Envelope=v035WriteEnvelope;
v035WriteEnvelope=function(...args){if(V046.lab)return null;v049Checkpoint();return v049Envelope(...args);};
const v049SafeSave=v035SafeToSave;v035SafeToSave=function(){return !V046.lab&&v049SafeSave();};
const v049Recap=v035CaptureRecap;
v035CaptureRecap=function(...args){if(V046.lab)return null;v049Checkpoint();return v049Recap(...args);};
const v049Player=updatePlayer;
updatePlayer=function(dt){const out=v049Player(dt);if(mode==='PLAYING'&&!V046.busy){V049.clock+=dt;if(V049.clock>=1){V049.clock=0;v049Checkpoint();}}return out;};
/* Banking the campaign happens before the lab creates a different state object.
   Returning binds that retained scene to the freshly restored campaign state. */
const v049Lab=v046StartLab;
v046StartLab=async function(){if(!V046.lab){v049Checkpoint();V049.labNpcBackup=new Map(V042_RUNTIME.npcData);}return v049Lab();};
const v049Leave=v048LeaveLab;
v048LeaveLab=function(){const was=V046.lab,ok=v049Leave();if(was&&ok){v049Own(world);V042_RUNTIME.npcData=V049.labNpcBackup||new Map();V049.labNpcBackup=null;V049.lastBind=null;v049BindBodies(world,true);}return ok;};
