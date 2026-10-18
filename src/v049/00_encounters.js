/* Portable whitelist serializer. Only resolved territorial identities enter the
   save. Never persist renderer references, closures or arbitrary actor fields. */
const MistralEncounters=(()=>{
 'use strict';
 const MAX_ACTORS=2048,MAX_BYTES=2*1024*1024;
 const finite=(v,lo,hi,fallback=lo)=>Number.isFinite(v)?Math.max(lo,Math.min(hi,v)):fallback;
 const vector=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<=1e6)?v.slice():null;
 const parts=/^(head|body|arms|legs|arm_[lr]|leg_[lr]|fore_[lr]|back_[lr]|thruster_[lr]|claw_[lr]|tail)$/;
 function numbers(obj,regex,max){const out={};if(!obj||typeof obj!=='object'||Array.isArray(obj))return out;for(const[k,v]of Object.entries(obj).slice(0,40))if(regex.test(k)&&Number.isFinite(v))out[k]=finite(v,0,max);return out;}
 function clean(raw,identity){
  if(!raw||typeof raw!=='object'||!identity)return null;
  const pos=vector(raw.pos),home=vector(raw.home);if(!pos||!home)return null;
  const out={id:identity.id,site:identity.site,scope:identity.scope,kind:identity.kind,pos,home,
   yaw:finite(raw.yaw,-1e6,1e6,0),phase:finite(raw.phase,0,1e9,0),alive:raw.alive!==false,at:finite(raw.at,0,1e12,0)};
  if(identity.kind==='enemy'){
   if(!Number.isFinite(raw.maxHealth)||raw.maxHealth<=0||!Number.isFinite(raw.health))return null;
   out.maxHealth=finite(raw.maxHealth,1,100000);out.health=out.alive?finite(raw.health,0,out.maxHealth):0;out.alive=out.alive&&out.health>0;
   out.armDamage=finite(raw.armDamage,0,1,0);out.legDamage=finite(raw.legDamage,0,1,0);
   out.limbs=numbers(raw.limbs,parts,1);out.status=numbers(raw.status,/^(slow|burning|bleeding|poison|poisoned|stunned|stun|irradiated)$/,600);
   out.morale=finite(raw.morale,0,1000,100);out.maxMorale=finite(raw.maxMorale,1,1000,100);
   out.alerted=!!raw.alerted;out.state=['idle','patrol','search','chase','attack','flee','cover'].includes(raw.state)?raw.state:'idle';
   out.lastKnown=vector(raw.lastKnown);out.searchTimer=finite(raw.searchTimer,0,600,0);out.attackCooldown=finite(raw.attackCooldown,0,120,0);out.suppressed=finite(raw.suppressed,0,120,0);
   // Spec stays stable even if the player levels up while away.
   out.speed=finite(raw.speed,0,100,2);out.damage=finite(raw.damage,0,10000,10);out.armor=finite(raw.armor,0,.95,0);
  }else{
   out.anim=finite(raw.anim,0,1e9,0);out.routeIndex=Math.floor(finite(raw.routeIndex,0,10000,0));out.routePause=finite(raw.routePause,0,600,0);
   out.activity=['idle','walk','work','rest','patrol','talk'].includes(raw.activity)?raw.activity:'idle';
  }
  return out;
 }
 function migrate(input,resolve){const actors={};let size=0,count=0;
  for(const[id,raw]of Object.entries(input?.actors||{})){
   if(count>=MAX_ACTORS)break;
   const meta=resolve(id),entry=clean(raw,meta);if(!entry)continue;
   const bytes=JSON.stringify(entry).length;if(size+bytes>MAX_BYTES)continue;size+=bytes;actors[id]=entry;count++;
  }
  return {schema:1,actors};
 }
 /* Merge old duplicate corpses conservatively: missing known inventory counts
    mean consumed, not missing metadata. Never manufacture a second reward. */
 function remainder(a,b){const out={};for(const k of new Set([...Object.keys(a||{}),...Object.keys(b||{})])){const n=Math.min(finite(a?.[k],0,1e6,0),finite(b?.[k],0,1e6,0));if(n>0)out[k]=Math.floor(n);}return out;}
 return {clean,migrate,vector,finite,remainder,MAX_ACTORS,MAX_BYTES};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralEncounters;
