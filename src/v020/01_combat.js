/* Combat uses one weapon calculation in free aim and V.A.T.S.; no delayed timer
 * can shoot into another scene. All resource consumption occurs at emission. */
function v020Profile(w=currentWeapon()){
  const text=(w.name||'').toLowerCase();
  const delay=w.melee?(/scie|tronçon|éventreur/.test(text)?.22:.58):w.heavy?.55:(w.burst||0)>1?.24:w.pellets?.72:/revolver|gauss|précision|harpon|chasse/.test(text)?.65:/mitrailleur|minigun|automatique|gatling/.test(text)?.13:.30;
  return {delay,automatic:!w.melee&&(/mitrailleur|minigun|gatling|automatique|bozar|p90|g11/i.test(w.name)||(w.burst||0)>1),rounds:w.melee?0:w.pellets?1:Math.max(1,w.burst||1),projectiles:w.pellets||Math.max(1,w.burst||1),range:w.range||100};
}
function v020Damage(w,e,part={id:'body',mult:1},crit=false){
  const sp=state.character.special,condition=equipmentCondition('weapon',state.player.weaponId)/100;
  let n=(w.damage+(w.melee?sp.S*2.4:sp.P*.6))*(.55+.45*condition)*(part.mult||1)*difficultyInfo().outgoing*(1+(state.perks.gunslinger||0)*(w.melee?.04:.12))*(crit?1.75:1);
  const cat=enemyCategory(e.type);
  if(cat==='robot'||robotType(e.type))n*=1+(state.perks.technician||0)*.1+(w.robotBonus||0);
  else if(creatureType(e.type)||e.attackType==='melee')n*=1+(w.creatureBonus||0);
  return n;
}
function v020Wear(w,rounds=1){setEquipmentCondition('weapon',state.player.weaponId,equipmentCondition('weapon',state.player.weaponId)-(w.conditionLoss??.3)*(1+(rounds-1)*.16)*(1-(state.perks.armorer||0)*.08));}
function v020CanEmit(){return !!world&&['PLAYING','VATS_EXEC'].includes(mode)&&!zoneTransitioning&&!V020.reload&&reloadTimer<=0&&V020.cooldown<=0&&state.player.hp>0;}
function v020Impact(e,amount,part,crit,w){damageEnemy(e,amount,part,crit,w.armorPierce||0);if(w.status&&e.alive)applyEnemyStatus(e,w.status,5);}
splashDamage=function(center,base,source,pierce=0,radius=0){
  if(!radius)return;const origin=[center[0],(center[1]||0)+.85,center[2]];
  for(const e of world?.enemies||[]){if(!e.alive||e===source)continue;const target=[e.pos[0],(e.pos[1]||0)+.8,e.pos[2]],d=vLen(vSub(target,origin));if(d<=radius&&lineOfSight(origin,target))damageEnemy(e,base*clamp(1-d/radius,.18,.82),'body',false,pierce*.65);}
};
meleeTarget=function(w){const cam=getCamera(gameClock);let best=null,bestD=Infinity;for(const e of world?.enemies||[]){if(!e.alive)continue;const parts=enemyHitParts(e),p=parts.find(p=>p.id==='body')||parts[0],d=vLen(vSub(p.center,cam.pos));if(d>(w.range||3)+.5||d>=bestD||vDot(cam.dir,vNorm(vSub(p.center,cam.pos)))<.4||!lineOfSight(cam.pos,p.center))continue;best=e;bestD=d;}return best;};
function v020Emit(forced=null){
  if(!v020CanEmit())return false;const w=currentWeapon(),p=v020Profile(w),clip=state.player.ammoClip;
  if(equipmentCondition('weapon',state.player.weaponId)<=0)return v020Notify('Arme hors service : réparation nécessaire.',true);
  if(!w.melee&&clip<=0){audio.empty();return false;}
  if(forced&&(!forced.enemy.alive||forced.weapon!==state.player.weaponId))return false;
  if(forced){const part=enemyHitParts(forced.enemy).find(x=>x.id===forced.part.id);if(!part||v020TargetChance(forced.enemy,part)<=0)return false;forced.part=part;}
  const rounds=w.melee?0:Math.min(p.rounds,clip,forced?forced.rounds:Infinity);if(forced&&(!Number.isFinite(rounds)||(!w.melee&&rounds<=0)||state.player.ap<forced.cost))return false;
  if(forced)state.player.ap-=forced.cost;
  if(!w.melee)state.player.ammoClip-=rounds;
  V020.cooldown=p.delay;V020.shots++;weaponKick=1;audio.ensure();w.melee?audio.tone(145,.08,'sawtooth',.045,-35):audio.shot();
  $('weaponModel')?.classList.add('fire');const epoch=V020.scene;setTimeout(()=>{if(epoch===V020.scene)$('weaponModel')?.classList.remove('fire');},90);
  const hits=new Map(),cam=getCamera(gameClock),count=w.melee?1:w.pellets||rounds;
  for(let i=0;i<count;i++){
    let e,part;
    if(forced){if(Math.random()*100>=v020TargetChance(forced.enemy,forced.part))continue;e=forced.enemy;part=forced.part;}
    else if(w.melee){e=meleeTarget(w);part=e&&(enemyHitParts(e).find(x=>x.id==='body')||enemyHitParts(e)[0]);}
    else{const h=acquireShotTarget(cam.pos,spreadDirection(cam.dir,(w.spread||0)*(w.pellets?1.35:1)));if(h&&h.t<=p.range){e=h.enemy;part=h.part;}}
    if(!e||!part)continue;const crit=Math.random()<.03+state.character.special.L*.012;
    const old=hits.get(e)||{n:0,part:part.id,crit:false};old.n+=v020Damage(w,e,part,crit);old.crit||=crit;hits.set(e,old);
  }
  for(const [e,h] of hits){v020Impact(e,h.n,h.part,h.crit,w);if(w.splash)splashDamage(e.pos,h.n*.72,e,w.armorPierce||0,w.splash);}
  if(hits.size)hitMarker();else if(forced)toast('V.A.T.S. · tir manqué.');
  v020Wear(w,Math.max(1,rounds));persistAmmoCache();
  for(const e of world.enemies)if(e.alive&&dist2(state.player.pos,e.pos)<(w.silenced?14:38)){e.alerted=true;e.lastKnown=[...state.player.pos];e.searchTimer=8;}
  v020Log('tir',`${w.name} · ${rounds} munition(s) · ${hits.size} cible(s)`);updateHUD();return true;
}
fireWeapon=function(){if(mode!=='PLAYING')return false;return v020Emit();};
reload=function(){
  const w=currentWeapon();if(mode!=='PLAYING'||V020.reload||reloadTimer>0||w.melee||state.player.ammoClip>=w.clip||state.player.ammoReserve<=0)return false;
  V020.reload={weapon:state.player.weaponId,scene:V020.scene};reloadTimer=Math.max(.52,(w.reload||1.4)-state.character.special.A*.035)*(equipmentCondition('weapon',state.player.weaponId)<20?1.3:1);
  audio.reload();$('weaponModel')?.classList.add('reload');return true;
};
finishReload=function(){
  const r=V020.reload;V020.reload=null;reloadTimer=0;$('weaponModel')?.classList.remove('reload');
  if(!r||r.weapon!==state.player.weaponId||r.scene!==V020.scene)return false;
  const w=currentWeapon(),take=Math.max(0,Math.min(w.clip-state.player.ammoClip,state.player.ammoReserve));state.player.ammoClip+=take;state.player.ammoReserve-=take;persistAmmoCache();updateHUD();return true;
};
const v020Equip=equipWeapon;
equipWeapon=function(id){if(mode==='VATS_EXEC')return false;if(!WEAPONS[id]||!state.equipment.ownedWeapons.includes(id))return false;V020.reload=null;reloadTimer=0;V020.cooldown=Math.max(V020.cooldown,.22);$('weaponModel')?.classList.remove('reload');v020Equip(id);return true;};
function v020TargetChance(e,part){
  const cam=getCamera(gameClock),w=currentWeapon(),d=vLen(vSub(cam.pos,part.center));
  if(!e.alive||d>Math.min(65,(w.range||100)+(w.melee?.5:0))||!lineOfSight(cam.pos,part.center))return 0;
  const sp=state.character.special;return Math.round(clamp(94-d*(w.melee?2:1.2)+sp.P*2+sp.L*.3-(part.id==='head'?24:part.id==='arms'?11:part.id==='legs'?8:0)-(e.boss?8:0),5,95));
}
vatsChance=v020TargetChance;
vatsTargets=function(){return (world?.enemies||[]).filter(e=>e.alive&&enemyHitParts(e).some(p=>v020TargetChance(e,p)>0)).sort((a,b)=>dist2(state.player.pos,a.pos)-dist2(state.player.pos,b.pos));};
const v020ToggleVats=toggleVATS;
toggleVATS=function(){if(mode==='PLAYING'&&(V020.reload||equipmentCondition('weapon',state.player.weaponId)<=0)){toast('Terminez le rechargement ou réparez cette arme.');return false;}v020ToggleVats();return mode==='VATS';};
vatsAddCurrent=function(){
  if(!vatsState)return false;const e=vatsState.targets[vatsState.targetIndex],part=enemyHitParts(e)[vatsState.partIndex],spent=vatsState.queue.reduce((s,q)=>s+q.cost,0),p=v020Profile();
  if(v020TargetChance(e,part)<=0)return v020Notify('Membre masqué ou hors portée.',true);
  if(spent+part.cost>state.player.ap)return v020Notify('Points d’action insuffisants.',true);
  const reserved=vatsState.queue.reduce((s,q)=>s+q.rounds,0),rounds=currentWeapon().melee?0:Math.min(p.rounds,state.player.ammoClip-reserved);
  if(!currentWeapon().melee&&rounds<=0)return v020Notify('Chargeur entièrement réservé.',true);
  vatsState.queue.push({enemy:e,part:{...part},cost:part.cost,rounds,weapon:state.player.weaponId});renderVATS();return true;
};
executeVATS=function(){if(!vatsState?.queue.length)return false;V020.execution={queue:[...vatsState.queue],scene:V020.scene,world:world.id,wait:0};vatsState=null;$('vats').classList.add('hidden');v020Mode('VATS_EXEC');return true;};
function v020CancelVats(){V020.execution=null;vatsState=null;$('vats')?.classList.add('hidden');if(['VATS','VATS_EXEC'].includes(mode))v020Mode('PLAYING');}
function v020TickCombat(dt){
  if(!['PLAYING','VATS_EXEC'].includes(mode)||zoneTransitioning)return;V020.clock+=dt;V020.cooldown=Math.max(0,V020.cooldown-dt);
  if(mode==='PLAYING'&&V020.heldFire&&v020Profile().automatic&&V020.cooldown<=0&&state.player.ammoClip>0&&!V020.reload)v020Emit();
  if(isBoatZone()&&V020.reload&&reloadTimer>0){reloadTimer-=dt;if(reloadTimer<=0)finishReload();}
  const ex=V020.execution;if(!ex)return;
  if(ex.scene!==V020.scene||ex.world!==world?.id||state.player.hp<=0){v020CancelVats();return;}
  ex.wait-=dt;if(ex.wait>0||V020.cooldown>0)return;
  const q=ex.queue.shift();if(!q){v020CancelVats();persistAmmoCache();updateHUD();return;}
  const success=v020Emit(q);if(!success)v020Log('annulé','Cible masquée, neutralisée ou arme indisponible : aucun PA consommé.');ex.wait=success?Math.max(.32,v020Profile().delay):.08;
}
