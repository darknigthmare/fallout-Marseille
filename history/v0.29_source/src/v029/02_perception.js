/* Perception is based on sight, facing and distance. Sound gives a place to
 * investigate, not magical sight through the obstacle. No enemy is teleported. */
function v029Sense(e){if(!e.v029Sense)e.v029Sense={awareness:0,heard:null,time:0};return e.v029Sense;}
function v029Observe(e,dt,d,sight,detect){const s=v029Sense(e);if(e.v029Standby)return false;if(e.alerted){s.awareness=1;return d<detect&&sight;}
 const dir=cameraDir(e.yaw||0,0),v=vNorm([state.player.pos[0]-e.pos[0],0,state.player.pos[2]-e.pos[2]]),forward=vDot(dir,v)>.34;
 const sees=sight&&d<detect&&(forward||d<2.4);
 if(sees){const pace=.38+clamp(1-d/Math.max(1,detect),0,1)*1.35;s.awareness=clamp(s.awareness+dt*pace,0,1);if(s.awareness>=1){s.heard=null;s.time=0;return true;}}
 else s.awareness=Math.max(0,s.awareness-dt*.23);
 return false;}
function v029Noise(pos,radius,kind='bruit'){if(!world||!Array.isArray(pos)||pos.length!==3||!pos.every(Number.isFinite)||!Number.isFinite(radius)||radius<=0)return 0;let n=0;
 for(const e of world.enemies){if(!e.alive||e.v029Standby||e.alerted||e.damage<=0)continue;const eye=[e.pos[0],e.pos[1]+1.15,e.pos[2]],source=[pos[0],pos[1]+.7,pos[2]],direct=lineOfSight(eye,source),range=radius*(direct?1:.45);if(vLen(vSub(e.pos,pos))>range)continue;const s=v029Sense(e);s.heard=[...pos];s.time=7;s.awareness=Math.max(s.awareness,.35);e.state='investigate';n++;}
 if(n)state.v029.noiseCount++;V029.lastNoise={kind,pos:[...pos],heard:n};return n;}
const v029EnemyUpdate=updateEnemies;updateEnemies=function(dt){if(mode!=='PLAYING'||!world||zoneTransitioning)return;const all=world.enemies,active=all.filter(e=>!e.v029Standby),before=new Map(active.map(e=>[e.id,[...e.pos]]));world.enemies=active;
 try{v029EnemyUpdate(dt);}finally{world.enemies=all;}
 for(const e of all){if(!e.alive)continue;if(e.v029Standby){e.alerted=false;e.state='standby';e.v021Windup=null;continue;}const s=v029Sense(e);
 if(!e.alerted&&s.heard&&s.time>0){s.time=Math.max(0,s.time-dt);if(before.has(e.id))e.pos=before.get(e.id);e.state='investigate';const d=dist2(e.pos,s.heard);if(d>.6){const dx=s.heard[0]-e.pos[0],dz=s.heard[2]-e.pos[2];e.yaw=Math.atan2(dx,-dz);tryEnemyMove(e,dx/d*Math.max(.5,e.speed*.65)*dt,dz/d*Math.max(.5,e.speed*.65)*dt);}if(s.time===0){s.heard=null;e.state='idle';}}
 if(!e.alerted&&!s.heard&&s.awareness>.05)e.state='suspicious';}
 v029RefreshStealth();};
function v029RefreshStealth(){let level=0,seen=false,search=false;for(const e of world?.enemies||[]){if(!e.alive||e.v029Standby||e.damage<=0)continue;const s=v029Sense(e);level=Math.max(level,s.awareness);if(e.alerted){search=true;if(lineOfSight([e.pos[0],e.pos[1]+1.1,e.pos[2]],state.player.pos))seen=true;}if(s.heard)search=true;}
 V029.stealth={label:seen?'DANGER':search?'PRUDENCE':level>.04?'SOUPÇON':'CACHÉ',level:seen?100:Math.round(level*100)};return V029.stealth;}
const v029UpdatePlayer=updatePlayer;updatePlayer=function(dt){const active=gameStarted&&mode==='PLAYING'&&!zoneTransitioning&&!V018.qaFreeze&&Number.isFinite(dt)&&dt>0,before=[...state.player.pos];const r=v029UpdatePlayer(dt);if(active){state.v029.elapsed=Math.min(1e9,state.v029.elapsed+dt);V029.footClock-=dt;
 for(const id of Object.keys(state.v029.terminals))v029Expire(id);
 if(!world?.vehicleMode&&state.player.hp>0&&dist2(before,state.player.pos)>.025&&V029.footClock<=0){const running=keys.has('ShiftLeft')||keys.has('ShiftRight');if(!state.player.crouched){v029Noise([state.player.pos[0],state.player.pos[1]-playerEyeHeight(),state.player.pos[2]],running?14:4.5,'pas');V029.footClock=running?.36:.65;}}v029RefreshStealth();}return r;};
// No in-place floating indicator while the actor is behind cover.
const v029Collect=collectDraws;collectDraws=function(t){const draws=v029Collect(t);for(const e of world?.enemies||[]){if(!e.alive||!e.v029Standby)continue;part(draws,'sphere',[e.pos[0],e.pos[1]+1.9,e.pos[2]],[.13,.13,.13],[.24,.75,.55],0,{emissive:.5});}return draws;};
