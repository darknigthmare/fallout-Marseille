/* v0.22 — finite persistent state; no official map is claimed by these local layouts. */
const V022={clock:0,world:null,boundState:null,alarmUntil:0,conversation:null,lastCheckpoint:0,events:[],frameMs:0};
function v022Fresh(){return {schema:1,actors:{},encounters:{},caches:{},task:{accepted:false,kit:false,beds:false,consent:null,relay:false,ending:null,rewarded:false,tracked:false},observed:{}};}
const v022Base=baseState;baseState=function(){const s=v022Base();s.v022=v022Fresh();return s;};
const v022Migrate=migrateState;migrateState=function(input={}){const s=v022Migrate(input),p=input.v022||{},f=v022Fresh();s.v022={...f,...p,schema:1,task:{...f.task,...(p.task||{})},actors:{},encounters:{},caches:{...(p.caches||{})},observed:{...(p.observed||{})}};
 for(const [k,a] of Object.entries(p.actors||{}).slice(0,80))if(a&&Array.isArray(a.pos)&&a.pos.length===3&&a.pos.every(Number.isFinite))s.v022.actors[k]={...a,pos:[...a.pos],yaw:Number.isFinite(a.yaw)?a.yaw:0};
 for(const [k,a] of Object.entries(p.encounters||{}).slice(-2048))if(a&&typeof a.zone==='string'&&Number.isFinite(a.health))s.v022.encounters[k]={zone:a.zone,type:String(a.type||''),health:Math.max(0,a.health),leg:clamp(Number(a.leg)||0,0,.65),arm:clamp(Number(a.arm)||0,0,.65)};
 if(!['anonymous','sealed',null].includes(s.v022.task.consent))s.v022.task.consent=null;
 if(!['home','road',null].includes(s.v022.task.ending))s.v022.task.ending=null;
 return s;};state=migrateState(state);
function v022RememberEnemy(e){if(!world||!ALL_ZONE_IDS.includes(world.id)||!world.enemies.includes(e)||!state.v022)return;state.v022.encounters[world.id+'|'+e.id]={zone:world.id,type:e.type,health:Math.max(0,e.health||0),leg:e.legDamage||0,arm:e.armDamage||0};}
function v022Checkpoint(){if(!world||V022.boundState!==state||V022.world!==world)return;for(const e of world.enemies||[])v022RememberEnemy(e);for(const n of world.npcs||[])if(n.v022Civil)state.v022.actors[n.id]={pos:[...n.pos],yaw:n.yaw,activity:n.activity,world:world.id};}
const v022SaveBase=saveGame;saveGame=function(manual=false){if(state.player.hp>0)v022Checkpoint();return v022SaveBase(manual);};
const v022Damage=damageEnemy;damageEnemy=function(e,...args){const r=v022Damage(e,...args);if(e)v022RememberEnemy(e);return r;};
const v022Load=loadZone;loadZone=function(id,opts={}){v022Checkpoint();V022.alarmUntil=0;V022.conversation=null;const r=v022Load(id,opts);v022Bind();return r;};
function v022Bind(){if(!world||V022.world===world&&V022.boundState===state)return;V022.world=world;V022.boundState=state;V022.alarmUntil=0;V022.conversation=null;for(const e of world.enemies||[]){const a=state.v022.encounters[world.id+'|'+e.id];if(a&&a.type===e.type&&e.alive){e.health=clamp(a.health,0,e.maxHealth);e.legDamage=a.leg;e.armDamage=a.arm;if(!e.health){e.alive=false;state.flags.enemyDead[e.id]=true;}}}}
function v022Near(id,r=3.2){const i=world?.interactables.find(x=>x.id===id);return !!(i&&dist2(state.player.pos,i.pos)<=r&&Math.abs(state.player.pos[1]-i.pos[1])<1.95&&lineOfSight(state.player.pos,i.pos));}
function v022Record(kind,detail){V022.events.push({kind,detail,time:+V022.clock.toFixed(2)});if(V022.events.length>60)V022.events.shift();}
