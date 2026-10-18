/* v0.18 — Campaign safeguards, local quest journal and subtitle cassette player. */
let v018SessionKind='campaign';
const V018_SANDBOX_KEY='fallout_mistral_sandbox_v018';
const v018BaseState=baseState;
baseState=function(){const s=v018BaseState();s.v018={coordinates:'EPSG:2154-local',travelMode:'story',trackedQuest:null,tapeBookmarks:{},tapeSpeed:1};return s;};
const v018Migrate=migrateState;
migrateState=function(input){
  const s=v018Migrate(input);s.v018={coordinates:'EPSG:2154-local',travelMode:'story',trackedQuest:null,tapeBookmarks:{},tapeSpeed:1,...(input.v018||{})};
  if(input.v018?.coordinates!=='EPSG:2154-local'){
    const convert=(macro,p)=>{const d=V018_OLD_SCALES[macro];if(!d||!Array.isArray(p))return p;const lat=d.center[0]-p[2]/(110540*d.scale),lon=d.center[1]+p[0]/(111320*Math.cos(rad(d.center[0]))*d.scale),q=v015GeoProject(macro,lat,lon);return[q[0],1.65,q[2]];};
    if(V018_OLD_SCALES[s.player.zone])s.player.pos=convert(s.player.zone,s.player.pos);
    if(s.geo?.return){s.geo.return.pos=convert(s.geo.return.macro,s.geo.return.pos);s.geo.return.coordinates='EPSG:2154-local';}
  }
  s.v018.coordinates='EPSG:2154-local';s.v018.tapeSpeed=[.75,1,1.5].includes(s.v018.tapeSpeed)?s.v018.tapeSpeed:1;return s;
};
state=migrateState(state);
function v018ValidateSave(input){
  if(!input||typeof input!=='object'||Array.isArray(input)||!input.player||!input.character||!input.quest)throw new Error('Ce fichier n’est pas une sauvegarde Mistral.');
  let count=0;function visit(value,depth=0){if(++count>250000||depth>32)throw new Error('Sauvegarde trop complexe.');if(typeof value==='number'&&!Number.isFinite(value))throw new Error('Nombre invalide.');if(value&&typeof value==='object')for(const[k,v]of Object.entries(value)){if(['__proto__','prototype','constructor'].includes(k))throw new Error('Clé interdite.');visit(v,depth+1);}}
  visit(input);const p=input.player;if(!Array.isArray(p.pos)||p.pos.length!==3||p.pos.some(x=>!Number.isFinite(x)||Math.abs(x)>1e7))throw new Error('Position invalide.');
  if(typeof p.zone!=='string'||(!ALL_ZONE_IDS.includes(p.zone)&&!V015_GEO_MACROS[p.zone]))throw new Error('Secteur de sauvegarde inconnu.');
  if(typeof input.character.name!=='string'||input.character.name.length>80)throw new Error('Identité invalide.');
  for(const[k,v]of Object.entries(input.inventory||{}))if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>1e9)throw new Error('Inventaire invalide : '+k);
  return true;
}
function v018SaveKey(){return v018SessionKind==='sandbox'?V018_SANDBOX_KEY:SAVE_KEY;}
function v018WriteSave(raw,key=v018SaveKey(),backup=false){
  // Do not report a durable save when only the in-memory fallback succeeded.
  if(backup){const prev=localStorage.getItem(key);if(prev){const arr=JSON.parse(localStorage.getItem(key+'_backups')||'[]');if(!arr.length||arr[0].raw!==prev){arr.unshift({date:new Date().toISOString(),raw:prev});localStorage.setItem(key+'_backups',JSON.stringify(arr.slice(0,3)));}}}
  localStorage.setItem(key,raw);if(localStorage.getItem(key)!==raw)throw new Error('Écriture non confirmée');return true;
}
saveGame=function(manual=false){if(!gameStarted)return false;persistAmmoCache();state.version=VERSION;state.lastSave=new Date().toISOString();try{v018ValidateSave(state);v018WriteSave(JSON.stringify(state),v018SaveKey(),manual);updateContinueButton();if(manual)toast(v018SessionKind==='sandbox'?'Bac à sable sauvegardé séparément.':'Campagne sauvegardée.','good');return true;}catch(e){V018.saveError=String(e.message);if(manual)toast('Sauvegarde non conservée. Exportez le fichier JSON.','bad');return false;}};
const v018OldStart=v014StartNewGameForV015;
startNewGame=function(free=false){V018.transitionEpoch=(V018.transitionEpoch||0)+1;zoneTransitioning=false;v018SessionKind=free?'sandbox':'campaign';if(!free){try{const raw=localStorage.getItem(SAVE_KEY);if(raw)v018WriteSave(raw,SAVE_KEY,true);}catch{}}
  v018OldStart(free);state.v018??=baseState().v018;state.v018.travelMode='story';saveGame(false);
};
loadGame=function(){try{let raw=localStorage.getItem(SAVE_KEY);if(!raw){const key=LEGACY_SAVE_KEYS.find(k=>localStorage.getItem(k));if(key)raw=localStorage.getItem(key);}if(!raw)return false;const data=JSON.parse(raw);v018ValidateSave(data);const next=migrateState(data);state=next;v018SessionKind='campaign';syncEquipment();gameStarted=true;loadZone(state.player.zone,{spawn:state.player.pos,yaw:state.player.yaw,silent:true,force:true,instance:!V015_GEO_MACROS[state.player.zone]});saveGame(false);toast('Campagne chargée.','good');return true;}catch(e){toast('Sauvegarde refusée : '+e.message,'bad');return false;}};
function v018ImportRaw(raw){if(typeof raw!=='string'||raw.length>8*1024*1024)throw new Error('Fichier trop volumineux.');const parsed=JSON.parse(raw);v018ValidateSave(parsed);const next=migrateState(parsed);v018WriteSave(JSON.stringify(next),SAVE_KEY,true);state=next;v018SessionKind='campaign';syncEquipment();return true;}
importSave=function(){const inp=document.createElement('input');inp.type='file';inp.accept='.json,application/json';inp.onchange=async()=>{const f=inp.files?.[0];if(!f)return;try{if(f.size>8*1024*1024)throw new Error('Fichier trop volumineux');v018ImportRaw(await f.text());closePipboy();gameStarted=true;loadZone(state.player.zone,{spawn:state.player.pos,yaw:state.player.yaw,instance:!V015_GEO_MACROS[state.player.zone]});toast('Import vérifié ; ancienne campagne conservée en secours.','good');}catch(e){toast('Import refusé : '+e.message,'bad');}};inp.click();};
function v018RestoreBackup(){try{const backups=JSON.parse(localStorage.getItem(SAVE_KEY+'_backups')||'[]');if(!backups.length){toast('Aucune copie de secours disponible.');return false;}v018ImportRaw(backups[0].raw);return loadGame();}catch(e){toast(e.message,'bad');return false;}}

/* One-off rewards require a collected proof. Repeated / out-of-order calls do nothing. */
const v018OldResolveLocal=v013ResolveLocalQuest;
v013ResolveLocalQuest=function(zone,outcome){if(!V013_LOCAL_QUESTS[zone]||state.lore?.localQuests?.[zone]!==2||!['community','payment','archive'].includes(outcome))return false;v018OldResolveLocal(zone,outcome);if(state.v018.trackedQuest===zone)state.v018.trackedQuest=null;return true;};

/* Physical instance traversal remembers a full exterior return, including pitch. */
v015EnterInstance=function(id){const a=v015AnchorForZone(id);if(!a)return false;state.geo.return={macro:world?.id||a.macro,pos:[...state.player.pos],yaw:state.player.yaw,pitch:state.player.pitch,anchor:id,coordinates:'EPSG:2154-local'};state.geo.pendingTarget=null;state.v018.travelMode='geographic';loadZone(id,{instance:true,force:true,silent:true,noTravel:true});return true;};
v015ExitInstance=function(id){const a=v015AnchorForZone(id);if(!a)return false;const r=state.geo.return?.macro===a.macro?deepClone(state.geo.return):null;state.v018.travelMode='geographic';const p=r?.pos||v015TargetSpawn(id);loadZone(a.macro,{geoDirect:true,force:true,silent:true,noTravel:true,spawn:p,yaw:r?.yaw||0});if(r){state.player.pos=[...r.pos];state.player.pitch=r.pitch||0;}saveGame(false);return true;};

/* Cassette subtitles: line duration follows its reading length, not a fixed 3.6 s. */
const v018TapeRender=renderHolotape;
function v018TapeDuration(line,speed=state.v018.tapeSpeed){return clamp(1300+String(line).trim().split(/\s+/).length*330,3000,18000)/speed;}
function v018TapeBookmark(){if(holotapeState){state.v018.tapeBookmarks[holotapeState.zoneId]={index:holotapeState.index,elapsed:holotapeState.elapsed||0};}}
openHolotape=function(zoneId){const d=V013_LORE_CATALOG[zoneId];if(!d)return false;clearInterval(holotapeTimer);state.lore.holotapes[zoneId]=true;state.lore.holotapePlays[zoneId]=(state.lore.holotapePlays[zoneId]||0)+1;const b=state.v018.tapeBookmarks[zoneId]||{};holotapeState={zoneId,index:clamp(b.index||0,0,d.lines.length-1),elapsed:Math.max(0,b.elapsed||0),playing:false,returnMode:mode==='PIP'?'PIP':'PLAYING'};document.exitPointerLock?.();mode='HOLOTAPE';$('holotapeScreen').classList.remove('hidden');renderHolotape();v013HolotapePlay(true);return true;};
function v018TapeTick(dt){if(!holotapeState?.playing||document.hidden)return;const d=V013_LORE_CATALOG[holotapeState.zoneId];holotapeState.elapsed+=dt;const duration=v018TapeDuration(d.lines[holotapeState.index]);if(holotapeState.elapsed>=duration){if(holotapeState.index<d.lines.length-1){holotapeState.index++;holotapeState.elapsed=0;}else{holotapeState.elapsed=duration;holotapeState.playing=false;clearInterval(holotapeTimer);}v018TapeBookmark();renderHolotape();}else v018TapeProgress();}
function v018TapeProgress(){if(!holotapeState)return;const d=V013_LORE_CATALOG[holotapeState.zoneId],durations=d.lines.map(l=>v018TapeDuration(l)),total=durations.reduce((a,b)=>a+b,0),elapsed=durations.slice(0,holotapeState.index).reduce((a,b)=>a+b,0)+Math.min(holotapeState.elapsed,durations[holotapeState.index]);$('holotapeProgress').style.width=`${elapsed/total*100}%`;if($('v018TapeTime'))$('v018TapeTime').textContent=`${Math.floor(elapsed/1000)} / ${Math.ceil(total/1000)} s`;}
v013HolotapePlay=function(on){if(!holotapeState)return;clearInterval(holotapeTimer);holotapeState.playing=!!on;if(on){let last=performance.now();holotapeTimer=setInterval(()=>{const current=performance.now();v018TapeTick(Math.min(1000,current-last));last=current;},100);}v018TapeBookmark();renderHolotape();};
v013HolotapeStep=function(d){if(!holotapeState)return;holotapeState.index=clamp(holotapeState.index+d,0,V013_LORE_CATALOG[holotapeState.zoneId].lines.length-1);holotapeState.elapsed=0;v018TapeBookmark();renderHolotape();};
renderHolotape=function(){v018TapeRender();if(!holotapeState)return;const root=$('holotapeText').parentElement;let panel=$('v018TapePanel');if(!panel){panel=document.createElement('div');panel.id='v018TapePanel';root.appendChild(panel);}const data=V013_LORE_CATALOG[holotapeState.zoneId];panel.innerHTML=`<div class="v018-tape-tools"><span id="v018TapeTime"></span><label>Vitesse <select id="v018TapeSpeed"><option value="0.75">0,75×</option><option value="1">1×</option><option value="1.5">1,5×</option></select></label><span>SOUS-TITRES · VOIX NON ENREGISTRÉE</span></div><details><summary>Transcription complète</summary><ol>${data.lines.map(l=>`<li>${escapeHtml(l)}</li>`).join('')}</ol></details>`;$('v018TapeSpeed').value=String(state.v018.tapeSpeed);$('v018TapeSpeed').onchange=e=>{state.v018.tapeSpeed=Number(e.target.value);v018TapeBookmark();renderHolotape();};v018TapeProgress();};
closeHolotape=function(){if(!holotapeState)return;clearInterval(holotapeTimer);holotapeTimer=null;v018TapeBookmark();const next=holotapeState.returnMode;holotapeState=null;$('holotapeScreen').classList.add('hidden');mode=next;saveGame(false);};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&holotapeState?.playing){v013HolotapePlay(false);v018TapeBookmark();}});

function v018ZoneName(id){return V015_GEO_ANCHORS[id]?.label||V013_LORE_CATALOG[id]?.label||SHELTER_DEFS[id]?.title||id;}
let v018JournalFilter='active',v018JournalQuery='';
function v018Journal(root=$('pipContent')){
  const rows=Object.entries(V013_LOCAL_QUESTS).filter(([id,q])=>{const s=state.lore.localQuests[id]||0;return(v018JournalFilter==='all'||v018JournalFilter==='active'&&s>0&&s<3||v018JournalFilter==='done'&&s===3)&&(!v018JournalQuery||[q.title,q.giver,v018ZoneName(id)].join(' ').toLocaleLowerCase('fr').includes(v018JournalQuery.toLocaleLowerCase('fr')));});
  root.innerHTML=`<section class="v018-journal"><p class="eyebrow">DOSSIERS DE TERRAIN</p><h2>CARNET DE ROUTE</h2><p>Les enquêtes locales sont séparées de la campagne principale. Le repère suit la preuve puis la personne à retrouver.</p><div class="v018-journal-tools"><input id="v018QuestSearch" placeholder="Rechercher un lieu ou un nom…" aria-label="Rechercher une quête" value="${escapeHtml(v018JournalQuery)}"><select id="v018QuestFilter" aria-label="État des quêtes"><option value="active">En cours</option><option value="done">Terminées</option><option value="all">Toutes les enquêtes</option></select><button id="v018QuestUntrack">Suivre la campagne</button></div><div class="v018-quest-cards">${rows.map(([id,q])=>{const s=state.lore.localQuests[id]||0;return`<article><small>${escapeHtml(v018ZoneName(id))} · ${['À DÉCOUVRIR','PREUVE À RETROUVER','RETOUR AU CONTACT','RÉSOLUE'][s]}</small><h3>${escapeHtml(q.title||'Dossier local')}</h3><p>${escapeHtml(q.giver)} · ${escapeHtml(q.role)}</p><p>${s===1?escapeHtml(q.objective||'Cherchez la preuve dans une sous-zone du secteur.'):s===2?'La preuve est dans votre dossier. Revenez choisir son destin.':s===3?'Décision : '+escapeHtml(state.lore.localQuestOutcomes[id]||'enregistrée'):'Parlez à la personne référente sur place.'}</p>${s>0&&s<3?`<button data-track="${id}">${state.v018.trackedQuest===id?'REPÈRE ACTIF':'Suivre cette enquête'}</button>`:''}</article>`;}).join('')||'<p>Aucune enquête dans cette sélection. Les contacts se trouvent dans les quartiers habités.</p>'}</div></section>`;
  $('v018QuestFilter').value=v018JournalFilter;$('v018QuestFilter').onchange=e=>{v018JournalFilter=e.target.value;v018Journal(root);};$('v018QuestSearch').oninput=e=>{v018JournalQuery=e.target.value;const pos=e.target.selectionStart;v018Journal(root);$('v018QuestSearch').focus();$('v018QuestSearch').setSelectionRange(pos,pos);};$('v018QuestUntrack').onclick=()=>{state.v018.trackedQuest=null;v018Journal(root);};root.querySelectorAll('[data-track]').forEach(b=>b.onclick=()=>{state.v018.trackedQuest=b.dataset.track;v018Journal(root);saveGame(false);});
}
const v018RenderPipData=renderPipData;
renderPipData=function(c){v018RenderPipData(c);const bar=document.createElement('div');bar.className='v018-pip-actions';bar.innerHTML='<button id="v018OpenJournal">CARNET DE ROUTE</button><button id="v018RestoreBackup">COPIE DE SECOURS</button>';c.prepend(bar);$('v018OpenJournal').onclick=()=>v018Journal(c);$('v018RestoreBackup').onclick=v018RestoreBackup;};
const v018OldMarker=getObjectiveMarker;
getObjectiveMarker=function(){const id=state.v018?.trackedQuest,s=state.lore?.localQuests?.[id];if(!id||s<1||s>=3)return v018OldMarker();if(world?.id===id){const target=s===1?world.interactables.find(i=>i.id.includes('objective')&&i.id.includes(id)):world.npcs.find(n=>n.id===`v013-giver-${id}`);if(target)return{zone:id,pos:target.pos};}if(world?.geoMacro){const a=v015AnchorForZone(id);if(a?.macro===world.id)return{zone:world.id,pos:v015GeoProject(world.id,a.lat,a.lon)};}return{zone:id,pos:[0,0,0]};};
const v018OldTerminalAction=executeTerminalAction;
executeTerminalAction=function(zoneId){if(!V013_LORE_CATALOG[zoneId]||state.lore.terminalActions[zoneId])return false;if(world?.id!==zoneId){toast('Les archives se consultent à distance ; la commande exige le terminal sur place.');return false;}v018OldTerminalAction(zoneId);return true;};
const v018OldTerminalRender=renderLoreTerminal;
renderLoreTerminal=function(){v018OldTerminalRender();if(terminalLoreState&&world?.id!==terminalLoreState.zoneId){$('terminalLoreAction').disabled=true;$('terminalLoreAction').textContent='ARCHIVE EN LECTURE SEULE — REJOINDRE LE TERMINAL';}};
