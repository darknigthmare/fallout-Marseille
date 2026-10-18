/* One view into the current game world. Framing rotates/zooms at the player's
   eye, never translates the player or introduces an off-camera shot origin. */
const v025BaseCamera=getCamera;
function v025Viewport(){const r=$('gameCanvas').getBoundingClientRect();return {width:r.width||innerWidth,height:r.height||innerHeight,left:r.left,top:r.top};}
function v025Focus(e,instant=false){if(!e?.alive)return;const r=v025Rig(e),origin=[...state.player.pos],size=r.bounds.max.map((v,i)=>v-r.bounds.min[i]),middle=r.bounds.min.map((v,i)=>(v+r.bounds.max[i])/2),target=v025ToWorld(e,middle),distance=Math.max(.5,vLen(vSub(target,origin))),v=v025Viewport(),portrait=v.width<650;
 const availableHeight=Math.max(160,v.height-(portrait?320:270)),fraction=clamp(availableHeight/v.height*.76,.23,.58),aspect=v.width/v.height;
 const vf=2*Math.atan(Math.max(size[1]/(2*distance*fraction),(Math.hypot(size[0],size[2])*.63)/(distance*aspect*(portrait?.64:.68)*2)));
 const fov=clamp(vf*180/Math.PI,10,85),desiredY=(70+availableHeight/2)/v.height;
 // Move the point we look at, not the camera: the actor fits above the command bar.
 target[1]-=distance*Math.tan(rad(fov)/2)*(1-2*desiredY);
 const dir=vNorm(vSub(target,origin)),yaw=Math.atan2(dir[0],-dir[2]),pitch=Math.asin(clamp(dir[1],-.98,.98));
 const previous=V025.focus?v025CurrentCamera():{pos:origin,dir:cameraDir(state.player.yaw,state.player.pitch),fov:67};
 const startYaw=Math.atan2(previous.dir[0],-previous.dir[2]),delta=((yaw-startYaw+Math.PI*3)%TAU)-Math.PI;
 V025.pan={at:performance.now(),duration:instant||settings.reduceMotion?0:190,yaw:startYaw,toYaw:startYaw+delta,pitch:Math.asin(clamp(previous.dir[1],-.98,.98)),toPitch:pitch,fov:previous.fov,toFov:fov};
 V025.focus={enemy:e,origin,target};
}
function v025CurrentCamera(){if(!V025.focus)return v025BaseCamera(gameClock);const p=V025.pan,elapsed=p.duration?clamp((performance.now()-p.at)/p.duration,0,1):1,a=1-Math.pow(1-elapsed,3);
 return{pos:[...state.player.pos],dir:cameraDir(lerp(p.yaw,p.toYaw,a),lerp(p.pitch,p.toPitch,a)),fov:lerp(p.fov,p.toFov,a)};
}
getCamera=function(t){return V025.active&&['VATS','VATS_EXEC'].includes(mode)&&V025.focus?v025CurrentCamera():v025BaseCamera(t);};
function v025Project(p,camera=getCamera(gameClock)){const v=v025Viewport(),f=vNorm(camera.dir),right=vNorm(vCross(f,[0,1,0])),up=vNorm(vCross(right,f)),rel=vSub(p,camera.pos),z=vDot(rel,f);if(z<=.08)return null;const focal=v.height/(2*Math.tan(rad(camera.fov||67)/2));return{x:v.width*.5+vDot(rel,right)*focal/z,y:v.height*.5-vDot(rel,up)*focal/z,z};}
function v025Hull(points){const a=points.filter(Boolean).map(p=>[p.x,p.y]).sort((p,q)=>p[0]-q[0]||p[1]-q[1]);if(a.length<3)return a;const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]),lower=[],upper=[];for(const p of a){while(lower.length>1&&cross(lower.at(-2),lower.at(-1),p)<=0)lower.pop();lower.push(p);}for(const p of [...a].reverse()){while(upper.length>1&&cross(upper.at(-2),upper.at(-1),p)<=0)upper.pop();upper.push(p);}return [...lower.slice(0,-1),...upper.slice(0,-1)];}
function v025Current(){if(!vatsState||mode!=='VATS')return null;const e=vatsState.targets[vatsState.targetIndex],parts=e&&enemyHitParts(e);return e?.alive&&parts?.length?{enemy:e,parts,part:parts[clamp(vatsState.partIndex,0,parts.length-1)]}:null;}
function v025Stop(){V025.active=false;V025.focus=null;V025.pan=null;V025.selected=null;V025.screen=[];V025.lastShot=null;V025.epoch++;document.body.classList.remove('v025-targeting','v025-executing');$('v025Exec')?.setAttribute('hidden','');}
function v025Paint(){if(V025.paintBusy||!renderer||!world)return;V025.paintBusy=true;try{sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(V025.active?V025.poseTime:gameClock),getCamera(gameClock),currentEnv());v025Position();}finally{V025.paintBusy=false;}}
const v025OpenOld=toggleVATS;
toggleVATS=function(){if(mode==='VATS'){closeVATS();return false;}const result=v025OpenOld();if(mode==='VATS'){V020.heldFire=false;keys.clear();}return result;};
closeVATS=function(){if(mode!=='VATS')return false;v025Stop();$('vats').classList.add('hidden');vatsState=null;v020Mode('PLAYING');$('gameCanvas')?.focus();return true;};
const v025CancelOld=v020CancelVats;v020CancelVats=function(){v025Stop();return v025CancelOld();};
const v025ResetOld=v020ResetTransient;v020ResetTransient=function(){v025Stop();return v025ResetOld();};
const v025LoadOld=loadZone;loadZone=function(...args){v025Stop();return v025LoadOld(...args);};
const v025ExecuteOld=executeVATS;executeVATS=function(){const queued=vatsState?.queue?.[0];if(!queued)return false;const result=v025ExecuteOld();if(result){V025.active=true;V025.selected={enemy:queued.enemy,part:queued.part.id};v025Focus(queued.enemy);document.body.classList.remove('v025-targeting');document.body.classList.add('v025-executing');$('v025Exec').hidden=false;}return result;};
const v025EmitOld=v020Emit;v020Emit=function(forced=null){if(forced&&mode==='VATS_EXEC'&&V025.active){V025.selected={enemy:forced.enemy,part:forced.part.id};if(forced.enemy.alive)v025Focus(forced.enemy,true);}
 const health=forced?.enemy?.health;const result=v025EmitOld(forced);if(forced&&V025.active){V025.lastShot={enemy:forced.enemy,part:forced.part.label,critical:!!forced.critical,hit:result&&forced.enemy.health<health,emitted:result,at:performance.now()};v025ExecHud();}return result;};
function v025ExecHud(){const box=$('v025Exec');if(!box||mode!=='VATS_EXEC')return;const hit=V025.lastShot,remaining=V020.execution?.queue.length||0,signature=[remaining,hit?.at,hit?.emitted].join(':');if(box.dataset.signature===signature)return;box.dataset.signature=signature;box.innerHTML=hit?`<small>V.A.T.S. · ${remaining} ACTION(S) RESTANTE(S)</small><strong>${escapeHtml(hit.enemy.name)} · ${escapeHtml(hit.part)}</strong><span>${!hit.emitted?'ACTION ANNULÉE · aucune ressource débitée':hit.hit?(hit.critical?'IMPACT CRITIQUE':'IMPACT CONFIRMÉ'):'TIR MANQUÉ'}</span><button id="v025StopExec">Interrompre [V / Échap]</button>`:'<strong>V.A.T.S. · exécution</strong><span>Échap / V pour interrompre les actions restantes.</span>';const b=$('v025StopExec');if(b)b.onclick=()=>v020CancelVats();}
// Overlay tracks the very same camera as the renderer. No separate timer, no
// synthetic canvas representing another copy of the opponent.
const v025FrameBase=frame;frame=function(ts){v025FrameBase(ts);if(V025.active&&mode==='VATS')v025Position();else if(V025.active&&mode==='VATS_EXEC')v025ExecHud();else if(V025.active)v025Stop();};
