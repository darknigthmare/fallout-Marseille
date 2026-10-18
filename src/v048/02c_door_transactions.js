/* Do not erase the active interior before its exterior has been validated.
   A failed return keeps a valid, saveable interior; Retry finalises the same
   transaction, Cancel leaves its site and return point intact. */
function v048FinishExit(ctx) {
  if(!ctx||ctx.state!==state||!world?.v046)return false;
  state.v042.activeInterior=null;state.v042.lastSite=ctx.site;V042_RUNTIME.instanceSite=null;
  V048.exitPending=null;saveGame(false);return true;
}
v042ExitInstance=function() {
  if(world?.id!==V042_INSTANCE_ZONE||V048.exitPending)return false;
  const r=state.v042.returnPoint;
  const ctx={interior:world,state,site:state.v042.activeInterior,target:r?.macro||'geo_huveaune'};
  V048.exitPending=ctx;
  try {
    const result=loadZone(ctx.target,{geoDirect:true,force:true,noTravel:true,...(r?.pos?{spawn:r.pos,yaw:r.yaw}:{} )});
    // Retained-world path is synchronous; streamed path finalises in Ensure.
    if(world?.v046)v048FinishExit(ctx);
    if(result&&typeof result.catch==='function')result.catch(()=>{});
    return true;
  } catch(e) {
    if(world===ctx.interior){state.v042.activeInterior=ctx.site;V042_RUNTIME.instanceSite=ctx.site;}
    V048.exitPending=null;toast('Retour interrompu : '+String(e.message||e),'bad');return false;
  }
};
const v048EnsureBeforeDoors=v046Ensure;
v046Ensure=async function(...args){const ctx=V048.exitPending,ok=await v048EnsureBeforeDoors(...args);
  if(ok&&ctx&&V048.exitPending===ctx)v048FinishExit(ctx);return ok;};
const v048CancelBeforeDoors=v046Cancel;
v046Cancel=function(){const ctx=V048.exitPending;v048CancelBeforeDoors();
  if(ctx){if(world===ctx.interior&&ctx.state===state){state.v042.activeInterior=ctx.site;V042_RUNTIME.instanceSite=ctx.site;}V048.exitPending=null;}};
const v048LoadBeforeDoors=loadZone;
loadZone=function(id,opts={}){if(V048.exitPending&&id!==V048.exitPending.target)V048.exitPending=null;return v048LoadBeforeDoors(id,opts);};
const v048NewBeforeDoors=startNewGame;
startNewGame=function(...args){V048.exitPending=null;return v048NewBeforeDoors(...args);};
