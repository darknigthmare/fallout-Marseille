/* v0.20 — persistent field state and isolated transient simulation.
 * Source lineage: recovered v0.18; v0.19 sources were NOT available.
 * Old unknown fields are deliberately retained by migrateState.
 */
const V020={clock:0,cooldown:0,reload:null,execution:null,scene:0,heldFire:false,
  combatLog:[],panel:'interventions',query:'',filter:'all',map:null,mapPath:[],mapPin:null,
  actors:new Map(),navCache:new WeakMap(),lastWorld:null,qa:false,shots:0,renderFrames:0};
function v020Fresh(){return {schema:1,operations:{},visits:{},returnPoint:null,
  companionOrders:{},favorites:['pistol10',null,null,null],stash:{},craftCount:{},
  discoveredStations:{},restHours:0,notes:{},looted:{},openedDoors:{},
  accessibility:{localPlan:true},lastVersion:'0.20.0'};}
const v020BaseState=baseState;
baseState=function(){const s=v020BaseState();s.v020=v020Fresh();return s;};
const v020Migrate=migrateState;
migrateState=function(input={}){
  const s=v020Migrate(input),f=v020Fresh(),old=input.v020||{};
  s.v020={...f,...old};
  for(const k of ['operations','visits','companionOrders','stash','craftCount','discoveredStations','notes','looted','openedDoors'])s.v020[k]={...f[k],...(old[k]||{})};
  s.v020.favorites=Array.from({length:4},(_,i)=>{const id=(old.favorites||f.favorites)[i];return WEAPONS[id]&&s.equipment.ownedWeapons.includes(id)?id:null;});
  s.v020.schema=1;s.v020.lastVersion='0.20.0';return s;
};
state=migrateState(state);
function v020Log(kind,text){V020.combatLog.push({at:+V020.clock.toFixed(2),kind,text});if(V020.combatLog.length>24)V020.combatLog.shift();}
function v020ResetTransient(){V020.scene++;V020.cooldown=0;V020.reload=null;V020.execution=null;V020.heldFire=false;reloadTimer=0;vatsState=null;selectedInteractable=null;$('interactPrompt')?.classList.add('hidden');V020.actors.clear();V020.map=null;V020.mapPath=[];V020.mapPin=null;keys.clear();$('vats')?.classList.add('hidden');$('weaponModel')?.classList.remove('reload');}
const v020LoadZone=loadZone;
loadZone=function(id,opts={}){
  v020ResetTransient();$('v020Panel')?.classList.add('hidden');
  if(typeof V020_OPERATIONS!=='undefined'&&V020_OPERATIONS[id]){opts={...opts,instance:true,noTravel:true};state.v020.tracked=id;}
  return v020LoadZone(id,opts);
};
const v020Start=startNewGame;
startNewGame=function(free=false){v020ResetTransient();return v020Start(free);};
const v020Compute=computeDerived;
computeDerived=function(){const dead=state?.player?.hp<=0;v020Compute();if(dead)state.player.hp=0;};
const v020Save=saveGame;
saveGame=function(manual=false){
  if(state.player.hp<=0||mode==='DEAD'){if(manual)toast('La sauvegarde vivante précédente est conservée.');return false;}
  return v020Save(manual);
};
function v020Mode(next){keys.clear();touchMove={x:0,y:0};V020.heldFire=false;mode=next;if(next!=='PLAYING')document.exitPointerLock?.();}
function v020Physical(id,max=3.6){const it=world?.interactables.find(i=>i.id===id);return !!(it&&dist2(state.player.pos,it.pos)<=max&&lineOfSight(state.player.pos,[it.pos[0],it.pos[1]||1,it.pos[2]]));}
function v020Notify(text,bad=false){toast(text,bad?'bad':'good');return false;}
function v020Spend(cost){
  if(!cost||Object.entries(cost).some(([k,n])=>!Number.isInteger(n)||n<0))return false;
  if(!hasCost(cost))return false;return payCost(cost);
}
function v020Label(id){if(id==='caps')return 'Capsules';return AMMO_INFO[id]?.name||WEAPONS[id]?.name||ARMORS[id]?.name||itemLabel(id);}
const v020RegionName=worldRegionLabel;
worldRegionLabel=function(id){return typeof V020_OPERATIONS!=='undefined'&&V020_OPERATIONS[id]?V020_OPERATIONS[id].place:v020RegionName(id);};
