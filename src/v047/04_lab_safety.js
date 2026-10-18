/* The synthetic laboratory is a separate session, never a substitute for the
   campaign exterior. Retain the real scene and resource bank before entering. */
const v047StartLabBase=v046StartLab;
v046StartLab=async function(){
 if(!V046.lab)V047.labWorldBackup={world,terrain:V046.terrain,readyAnchor:V046.readyAnchor?.slice(),active:new Map(V042_RUNTIME.active),worldId:V042_RUNTIME.worldId,gameStarted,raw:new Map(V046.gate.cache),auto:V047.auto};
 v046Cancel();V047.meshes.clear();V047.records.clear();V047.lastPoint=null;V047.nextWarmAt=0;
 return v047StartLabBase();
};
function v047LeaveLab(){
 if(!V046.lab)return false;
 const backup=V047.labWorldBackup;V046.gate.cancel();V047.pending=null;V046.busy=false;V046.error=null;V046.prepared=null;zoneTransitioning=false;
 state=migrateState(V046.labBackup||baseState());V046.labBackup=null;
 if(V046.labSettings){Object.assign(settings,V046.labSettings);V046.labSettings=null;}
 world=backup?.world||null;V046.terrain=backup?.terrain||new MistralIntegrity.TerrainBank(V046_BOUNDS);V046.readyAnchor=backup?.readyAnchor||null;
 V042_RUNTIME.active=backup?.active||new Map();V042_RUNTIME.worldId=backup?.worldId||null;gameStarted=backup?.gameStarted||false;
 V046.gate.cache.clear();V046.gate.cache.pin(v047CurrentResources());for(const[k,v]of backup?.raw||[])V046.gate.cache.set(k,v);
 V047.meshes.clear();V047.records.clear();V047.auto=backup?.auto!==false;V047.lastPoint=null;V047.nextWarmAt=0;V047.labWorldBackup=null;
 /* showMenu historically writes a save and builds a decorative Aubagne world.
    Keep saving disabled for that call, then restore the retained real scene. */
 gameStarted=false;V046.lab=true;v046Loading({phase:'idle'});showMenu();
 V046.lab=false;V046.labProvider=null;world=backup?.world||world;
 /* A late startup timer must not replace a retained campaign with the menu
    diorama. Restore the pre-lab session flag after showMenu clears it. */
 gameStarted=!!backup?.gameStarted;
 V042_RUNTIME.active=backup?.active||new Map();V042_RUNTIME.worldId=backup?.worldId||null;
 $('v046LabBadge').hidden=true;return true;
}
const v047AfterInitCore=v047AfterInit;v047AfterInit=function(){v047AfterInitCore();window.__MISTRAL_DEBUG.v046Campaign=v047LeaveLab;};
