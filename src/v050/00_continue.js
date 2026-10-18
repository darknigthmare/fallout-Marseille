/* Continue resumes the newest valid campaign, regardless of its storage shape.
   Reading/ranking never rewrites an autosave, manual slot or legacy source. */
function v050ContinueTimestamp(value){
  if(typeof value==='number')return Number.isFinite(value)&&value>0&&value<=8640000000000000?value:0;
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}T/.test(value))return 0;
  const n=Date.parse(value);return Number.isFinite(n)&&n>0?n:0;
}
function v050ContinueCandidates(){
  const rows=[],seen=new Set(),sources=[{key:SAVE_KEY,kind:'current',rank:0},
    ...[1,2,3].map(slot=>({key:v035SlotKey(slot),kind:'slot',slot,rank:1})),
    {key:V035_AUTOSAVE_KEY,kind:'auto',rank:2},
    ...LEGACY_SAVE_KEYS.map((key,index)=>({key,kind:'legacy',rank:3,index}))];
  for(const source of sources){
    if(seen.has(source.key))continue;seen.add(source.key);
    try{
      const raw=storage.getItem(source.key);if(!raw||raw.length>8*1024*1024)continue;
      const parsed=JSON.parse(raw),envelope=source.kind==='slot'||source.kind==='auto',snapshot=envelope?parsed?.snapshot:parsed;
      v018ValidateSave(snapshot);
      const savedAt=(envelope?v050ContinueTimestamp(parsed.savedAt):0)||v050ContinueTimestamp(snapshot.lastSave);
      rows.push({...source,savedAt,snapshot});
    }catch{ /* An unreadable candidate does not hide another valid save. */ }
  }
  // Current wins exact ties; manual slots keep deterministic slot order, then
  // autosave and legacy keys in their declared (newest-version-first) order.
  return rows.sort((a,b)=>b.savedAt-a.savedAt||a.rank-b.rank||(a.slot||0)-(b.slot||0)||(a.index||0)-(b.index||0));
}
function v050ContinueInfo(){return v050ContinueCandidates().map(c=>({kind:c.kind,key:c.key,slot:c.slot||0,savedAt:c.savedAt,zone:c.snapshot.player.zone,version:c.snapshot.version||null}));}
v035RefreshContinue=function(){
  const b=$('btnContinue');if(!b)return;
  const best=v050ContinueCandidates()[0];b.disabled=!best;
  if(!best){b.textContent='Continuer';b.title='';return;}
  const chapter=v035ChapterForStage(Number(best.snapshot.quest?.main)||0).name;
  b.textContent='Continuer · '+chapter;
  const date=best.savedAt?new Date(best.savedAt).toLocaleString('fr-FR'):'date inconnue';
  b.title=`${best.snapshot.character.name||'Survivant'} · ${v018ZoneName(best.snapshot.player.zone)} · ${date}`;
};
v035ContinueLatest=async function(){
  const best=v050ContinueCandidates()[0];if(!best){v035RefreshContinue();toast('Aucune sauvegarde de campagne lisible.','bad');return false;}
  try{
    // Validate migration before replacing the live session or any stored data.
    const next=migrateState(best.snapshot);v018ValidateSave(next);
    if(V046.busy||V047.pending)v046Cancel();
    state=next;v018SessionKind='campaign';if(best.kind==='slot')state.v035.activeSlot=best.slot;
    syncEquipment();gameStarted=true;v035CloseScreen();hideAllScreens();
    v035BeginSession(best.kind==='slot'?'slot-'+best.slot:'continuer-'+best.kind);
    const loaded=loadZone(state.player.zone,{spawn:state.player.pos.slice(),yaw:state.player.yaw,silent:true,force:true,noTravel:true,instance:!V015_GEO_MACROS[state.player.zone]});
    // Geographic preparation is asynchronous. Let its normal loading gate own
    // retry/cancel and only report a successful Continue once it has committed.
    if(loaded&&typeof loaded.then==='function'&&await loaded===false)return false;
    if(state!==next)return false;
    saveGame(false);v035RefreshContinue();toast('Campagne chargée.','good');return true;
  }catch(e){toast('Sauvegarde refusée : '+String(e.message||e),'bad');v035RefreshContinue();return false;}
};
updateContinueButton=function(){v035RefreshContinue();};
const v050ContinueAfterBase=v035AfterInit;
v035AfterInit=function(){v050ContinueAfterBase();$('btnContinue').onclick=v035ContinueLatest;
  Object.assign(window.__MISTRAL_DEBUG,{v035ContinueLatest,v050ContinueInfo});v035RefreshContinue();};
