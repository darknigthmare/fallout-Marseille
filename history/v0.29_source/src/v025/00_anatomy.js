/* v0.25 — target the rendered actor, not a disconnected anatomical diagram.
   The original rig builds both the visible parts and the target volumes. All
   meshes remain depth-tested by the existing renderer. No imported game assets. */
const V025={rigs:new WeakMap(),active:false,epoch:0,poseTime:0,focus:null,pan:null,selected:null,
  screen:[],lastCamera:null,queueOpen:false,paintBusy:false,lastPaint:0,lastShot:null,cacheClock:0};
function v025Group(id){return ({arm_l:'arms',arm_r:'arms',claw_l:'arms',claw_r:'arms',leg_l:'legs',leg_r:'legs',fore_l:'legs',fore_r:'legs',back_l:'legs',back_r:'legs',thruster_l:'legs',thruster_r:'legs',tail:'body'})[id]||id;}
function v025Fresh(){return {schema:1,limbs:{}};}
const v025BaseState=baseState;baseState=function(){const s=v025BaseState();s.v025=v025Fresh();return s;};
const v025Migrate=migrateState;migrateState=function(input={}){const s=v025Migrate(input);s.v025=v025Fresh();
  // Bounded plain dictionaries; refuse inherited keys and non-finite damage.
  const allowed=/^(head|body|arms|legs|arm_[lr]|leg_[lr]|fore_[lr]|back_[lr]|thruster_[lr]|claw_[lr]|tail)$/;
  for(const [zone,actors] of Object.entries(input.v025?.limbs||{}).slice(0,120)){
    if(!/^[a-zA-Z0-9_:.-]{1,100}$/.test(zone)||['__proto__','constructor','prototype'].includes(zone)||!actors||typeof actors!=='object')continue;
    const dst={};for(const [id,parts]of Object.entries(actors).slice(0,250)){
      if(!/^[a-zA-Z0-9_:.-]{1,150}$/.test(id)||['__proto__','constructor','prototype'].includes(id)||!parts||typeof parts!=='object')continue;
      const a={};for(const[k,v]of Object.entries(parts)){if(allowed.test(k)&&Number.isFinite(v))a[k]=clamp(v,0,1);}if(Object.keys(a).length)dst[id]=a;
    }if(Object.keys(dst).length)s.v025.limbs[zone]=dst;
  }return s;
};state=migrateState(state);
const v025OriginalEnemyParts=enemyParts;
const v025OriginalHitParts=enemyHitParts;
function v025Local(e,p){const a=-(e.yaw||0),c=Math.cos(a),s=Math.sin(a),d=vSub(p,e.pos);return[c*d[0]+s*d[2],d[1],-s*d[0]+c*d[2]];}
function v025ToWorld(e,p){const c=Math.cos(e.yaw||0),s=Math.sin(e.yaw||0);return[e.pos[0]+c*p[0]+s*p[2],e.pos[1]+p[1],e.pos[2]-s*p[0]+c*p[2]];}
function v025Side(x,left,right){return x<0?left:right;}
function v025Classify(f,e,d){const sc=f==='robot'&&e.boss?1.2:f==='boar'?1.15:f==='dog'?.72:['tarente','scorpion','crab'].includes(f)&&e.boss?1.5:f==='drone'&&e.boss?1.4:1;
  const [x,y,z]=v025Local(e,d.pos).map(v=>v/sc);
  if(['raider','ghoul','robot'].includes(f)){
    if(y>1.39&&Math.abs(x)<.31)return 'head';
    if(Math.abs(x)>(f==='robot'?.36:.26)&&y>=.65)return v025Side(x,'arm_l','arm_r');
    if(y<.72)return v025Side(x,'leg_l','leg_r');return 'body';
  }
  if(f==='drone'){if(Math.abs(x)>.45)return v025Side(x,'thruster_l','thruster_r');if(z<-.3||y>1.7)return 'head';return 'body';}
  if(f==='crane'){if(y>2.18||z<-1.3)return 'arms';if(Math.abs(x)>.86)return v025Side(x,'leg_l','leg_r');if(z<-.8&&y>1.5)return 'head';return 'body';}
  if(['boar','dog'].includes(f)){if(y<.57&&Math.abs(x)>.2)return z<.1?v025Side(x,'fore_l','fore_r'):v025Side(x,'back_l','back_r');if(z<-.55)return 'head';return 'body';}
  if(['tarente','scorpion','crab'].includes(f)){
    if(f!=='crab'&&z>.65)return 'tail';
    if(Math.abs(x)>.5&&z<-.6)return v025Side(x,'claw_l','claw_r');
    if(Math.abs(x)>.5&&y<.5)return v025Side(x,'leg_l','leg_r');
    if(z<-.5)return 'head';return 'body';
  }
  // Older models keep broad groups, based on their real vertical/lateral
  // geometry. Never divide distance by a huge arm radius: that used to assign
  // every polygon of the deathclaw to its arms.
  if(/deathclaw/i.test(e.type)){const k=e.boss?1.4:1;if(y/k>2.1)return 'head';if(Math.abs(x)/k>.60)return 'arms';if(z/k>.7)return 'tail';return 'body';}
  const old=v025OriginalHitParts(e),head=old.find(p=>p.id==='head'),body=old.find(p=>p.id==='body'),legs=old.find(p=>p.id==='legs'),arms=old.find(p=>p.id==='arms');
  if(head&&y>head.center[1]-e.pos[1]-head.radius*.35)return 'head';
  if(arms&&Math.abs(x)>Math.max(.26,(body?.radius||.6)*.64))return 'arms';
  if(legs&&y<legs.center[1]-e.pos[1]+legs.radius*.24)return 'legs';
  return 'body';
}
const V025_LABELS={head:'TÊTE',body:'TORSE',arm_l:'BRAS GAUCHE',arm_r:'BRAS DROIT',leg_l:'JAMBE GAUCHE',leg_r:'JAMBE DROITE',fore_l:'PATTE AV. GAUCHE',fore_r:'PATTE AV. DROITE',back_l:'PATTE AR. GAUCHE',back_r:'PATTE AR. DROITE',claw_l:'PINCE GAUCHE',claw_r:'PINCE DROITE',thruster_l:'PROPULSEUR GAUCHE',thruster_r:'PROPULSEUR DROIT',tail:'QUEUE',arms:'OUTIL',legs:'PATTES'};
function v025Label(id,f,e){if(f==='legacy')return v025OriginalHitParts(e).find(p=>p.id===id)?.label||V025_LABELS[id]||id;
 if(id==='head')return ['robot','drone','crane'].includes(f)?'CAPTEURS':f==='boar'?'HURE':f==='crab'?'YEUX':'TÊTE';
 if(id==='body')return ['robot','drone','crane'].includes(f)?'CHÂSSIS':f==='crab'?'CARAPACE':['boar','dog'].includes(f)?'FLANC':f==='tarente'||f==='scorpion'?'CORPS':'TORSE';
 if(id.startsWith('arm_')&&f==='robot')return id==='arm_l'?'OUTIL GAUCHE':'OUTIL DROIT';
 if(id.startsWith('leg_')&&!['raider','ghoul'].includes(f))return ['robot','crane'].includes(f)?'MOTEUR '+(id==='leg_l'?'GAUCHE':'DROIT'):'PATTES '+(id==='leg_l'?'GAUCHES':'DROITES');
 return V025_LABELS[id]||id;
}
function v025Rig(e,t=gameClock){const time=V025.active?V025.poseTime:t,key=[time,...e.pos,e.yaw||0,e.state,e.v021Windup?.elapsed,e.boss,settings.reduceMotion].join('|'),prev=V025.rigs.get(e);if(prev?.key===key)return prev;
 const ds=[];v025OriginalEnemyParts(ds,e,time);const family=v021EnemyFamily(e),groups=new Map();
 for(const d of ds){const id=v025Classify(family,e,d);d.v025Part=id;d.v025Enemy=e.id;
   // The radio antenna is decoration, not the optical sensor hitbox.
   if(family==='robot'&&v025Local(e,d.pos)[1]>(e.boss?1.2:1)*1.8){d.v025Part='antenna';continue;}
   if(family==='drone'&&v025Local(e,d.pos)[1]>(e.boss?1.4:1)*1.7){d.v025Part='antenna';continue;}
   let b=groups.get(id);if(!b){b={id,min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity],draws:[]};groups.set(id,b);}b.draws.push(d);
   const p=v025Local(e,d.pos),s=d.scale||[1,1,1];for(let a=0;a<3;a++){b.min[a]=Math.min(b.min[a],p[a]-s[a]/2);b.max[a]=Math.max(b.max[a],p[a]+s[a]/2);}
 }
 const order=['head','body','arm_l','arm_r','arms','claw_l','claw_r','leg_l','leg_r','fore_l','fore_r','back_l','back_r','thruster_l','thruster_r','legs','tail'];
 const parts=[...groups.values()].sort((a,b)=>order.indexOf(a.id)-order.indexOf(b.id)).map(b=>{const centerLocal=b.min.map((v,i)=>(v+b.max[i])/2),size=b.min.map((v,i)=>b.max[i]-v),g=v025Group(b.id),old=v025OriginalHitParts(e).find(p=>p.id===g);
   const corners=[];for(let x=0;x<2;x++)for(let y=0;y<2;y++)for(let z=0;z<2;z++)corners.push(v025ToWorld(e,[x?b.max[0]:b.min[0],y?b.max[1]:b.min[1],z?b.max[2]:b.min[2]]));
   return {id:b.id,group:g,label:v025Label(b.id,family,e),center:v025ToWorld(e,centerLocal),radius:Math.max(.10,Math.min(.72,Math.max(size[0],size[1],size[2])*.43)),mult:old?.mult??(g==='head'?1.65:g==='arms'?.72:g==='legs'?.78:1),cost:old?.cost??(g==='head'?35:g==='arms'||g==='legs'?22:25),bounds:b,corners};});
 const bounds={min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};for(const p of parts)for(let i=0;i<3;i++){bounds.min[i]=Math.min(bounds.min[i],p.bounds.min[i]);bounds.max[i]=Math.max(bounds.max[i],p.bounds.max[i]);}
 const rig={key,parts,draws:ds,family,bounds};V025.rigs.set(e,rig);return rig;
}
enemyHitParts=function(e){return v025Rig(e).parts;};
function v025LimbLoss(e,id){const saved=state.v025?.limbs?.[world?.id]?.[e.id];if(saved&&Object.hasOwn(saved,id))return saved[id];const group=v025Group(id);return group==='arms'?(e.armDamage||0):group==='legs'?(e.legDamage||0):0;}
const v025DamageEnemy=damageEnemy;damageEnemy=function(e,amount,id='body',crit=false,pierce=0){if(!e||!e.alive)return;const before=e.health,g=v025Group(id),oldLoss=v025LimbLoss(e,id);
 let persistent=null;
 if(world&&!world.id.includes('fixture')){const zones=state.v025.limbs,actors=zones[world.id]||(zones[world.id]={});
   // Seed both limbs from inherited shared damage, then update only the side hit.
   persistent=actors[e.id]||(actors[e.id]=Object.fromEntries(enemyHitParts(e).map(p=>[p.id,v025LimbLoss(e,p.id)])));}
 const result=v025DamageEnemy(e,amount,g,crit,pierce);const dealt=Math.max(0,before-e.health);
 if(dealt>0&&persistent){persistent[id]=clamp(oldLoss+dealt/Math.max(25,e.maxHealth*(g==='head'?.65:g==='body'?1:.48)),0,1);}
 // Ephemeral fixtures use actor-local values, never contaminate a campaign save.
 else if(dealt>0){e.v025LimbLoss=e.v025LimbLoss||Object.fromEntries(enemyHitParts(e).map(p=>[p.id,0]));e.v025LimbLoss[id]=clamp((e.v025LimbLoss[id]||0)+dealt/Math.max(25,e.maxHealth*.48),0,1);}return result;
};
const v025ReadLoss=v025LimbLoss;v025LimbLoss=function(e,id){return e.v025LimbLoss?.[id]??v025ReadLoss(e,id);};
// Exact body frame rotation and pose are used for both labels and targets.
// Action origin remains the player's eye, never a zoomed/framing camera location.
v020TargetChance=function(e,p){if(!e?.alive||!p||!world)return 0;const w=currentWeapon(),origin=state.player.pos,d=vLen(vSub(origin,p.center));if(d>Math.min(65,(w.range||100)+(w.melee?.5:0))||!lineOfSight(origin,p.center))return 0;
 const g=p.group||v025Group(p.id),sp=state.character.special;const chance=Math.round(clamp(94-d*(w.melee?2:1.2)+sp.P*2+sp.L*.3-(g==='head'?24:g==='arms'?11:g==='legs'?8:0)-(e.boss?8:0),5,95));return V023.criticalShot?100:Math.min(95,chance+(v023Tagged('sneak')&&state.player.crouched?5:0));
};vatsChance=v020TargetChance;
// Free aim uses an oriented bounding volume for the same visible part, not a
// sphere so large that an arm behind a torso intercepts a head shot.
const v025Acquire=acquireShotTarget;acquireShotTarget=function(origin,dir){if(!world)return null;let distance=firstObstacle(origin,dir,150),hit=null;
 for(const e of world.enemies){if(!e.alive)continue;const local=v025Local(e,origin),c=Math.cos(e.yaw||0),s=Math.sin(e.yaw||0),direction=[c*dir[0]-s*dir[2],dir[1],s*dir[0]+c*dir[2]];
  for(const p of enemyHitParts(e)){const b=p.bounds,box={minX:b.min[0],maxX:b.max[0],minY:b.min[1],maxY:b.max[1],minZ:b.min[2],maxZ:b.max[2]};const t=rayAABB(local,direction,box,distance);if(t>=0&&t<distance){distance=t;hit={enemy:e,part:p,t};}}
 }return hit;
};
// Highlight the real mesh. Tint is applied to copies in this frame only and is
// naturally occluded by world geometry in both rendering backends.
enemyParts=function(draws,e,t){const rig=v025Rig(e,t),selected=V025.selected,active=V025.active&&selected?.enemy===e;
 for(const d of rig.draws){if(active&&d.v025Part===selected.part&&v020TargetChance(e,rig.parts.find(p=>p.id===selected.part))>0){draws.push({...d,color:cMix(d.color,[.58,1,.36],.66),emissive:Math.max(d.emissive||0,.25)});}else draws.push(d);}
};
