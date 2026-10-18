function v027Dispatch(a,arg=''){if(!v027CanAct())return false;
 if(a==='close')return closePipboy();
 if(a==='tab')return v027Set(arg);
 if(a==='sub')return v027Set(V027.tab,arg);
 if(a==='jump'){const[t,s]=arg.split(':');return v027Set(t,s);}
 if(a==='next'){const keys=Object.keys(V027_TABS);return v027Set(keys[(keys.indexOf(V027.tab)+1)%keys.length]);}
 if(a==='settings')return v027Set('data','system');
 if(a==='select'){V027.selected=arg;V027.confirm=null;$('pipContent').scrollTop=0;renderPipboy();return true;}
 if(a==='page'){V027.page=Math.max(0,V027.page+Number(arg));V027.selected=null;renderPipboy();return true;}
 if(['equip','use','recycle','mod','tag'].includes(a))return v027ItemAction(a,arg);
 if(a==='favorite'){const[id,n]=arg.split('|');const ok=v020Favorite(id,Number(n));renderPipboy();return ok;}
 if(a==='perk'){if(!Object.hasOwn(PERK_INFO,arg)||(state.player.perkPoints||0)<1||(state.perks[arg]||0)>=PERK_INFO[arg].max)return false;buyPerk(arg);renderPipboy();return true;}
 if(a==='theme'){if(!['green','amber','white'].includes(arg))return false;state.v027.theme=arg;saveGame(false);renderPipboy();return true;}
 if(a==='scan'){state.v027.scanlines=!state.v027.scanlines;saveGame(false);renderPipboy();return true;}
 if(a==='background'){state.v027.backgroundTape=!state.v027.backgroundTape;saveGame(false);renderPipboy();return true;}
 if(a==='clear-tags'){state.v027.tagged=[];saveGame(false);renderPipboy();return true;}
 if(a==='read'){if(!v027Notes().some(r=>r.id===arg))return false;state.v027.read[arg]=true;saveGame(false);renderPipboy();return true;}
 if(a==='track')return v027Track(arg);
 if(a==='quest-map'){const r=v027QuestRows().find(r=>r.id===arg);if(!r?.zone)return false;if(r.stage!=='done')v027Track(arg);v027Set('map',r.zone===world.id?'local':'places');V027.selected=r.zone;renderPipboy();return true;}
 if(a==='floor'){const h=Number(arg);if(![0,3.2].includes(h)||h&& !v021IsScene())return false;V021.mapFloor=h;renderPipboy();return true;}
 if(a==='zoom'){V027.zoom=clamp(V027.zoom+Number(arg),1,2);renderPipboy();return true;}
 if(a==='clear-pin'){V020.mapPin=null;V020.mapPath=[];state.v027.pin=null;saveGame(false);renderPipboy();return true;}
 if(a==='travel')return v027Travel(arg);
 if(a==='travel-confirm')return v027Travel(arg,true);
 if(a==='cancel-confirm'){V027.confirm=null;renderPipboy();return true;}
 if(a==='terminal'){if(!state.lore.terminals[arg]||!V013_LORE_CATALOG[arg]?.action||state.lore.terminalActions[arg]||world.id!==arg||!v021Near('v013-terminal-'+arg,3.5))return v027Notify('Commande locale inaccessible : archive seule.');executeTerminalAction(arg);renderPipboy();return true;}
 if(a==='field'){closePipboy();v020OpenField(arg);return true;}
 if(a==='save'){const ok=saveGame(true);V027.message=ok?'Progression écrite dans ce navigateur.':'Écriture refusée. Exportez un fichier JSON pour conserver la progression.';renderPipboy();if($('p27SaveState'))$('p27SaveState').textContent=V027.message;return ok;}
 if(a==='export'){v027Bookmark();exportSave();return true;}
 if(a==='import'){if(!confirm('Importer un fichier remplacera la campagne après validation et copie de secours. L’exploration actuelle reste dans sa clé séparée. Continuer ?'))return false;v027Bookmark();if(V027.tape)V027.tape.playing=false;importSave();return true;}
 if(a==='station'){const d=V027_STATIONS[arg];if(!d||!d.available())return false;v027Bookmark();if(V027.tape)V027.tape.playing=false;V027.activeStation=V027.activeStation===arg?null:arg;radioOn=!!V027.activeStation;renderPipboy();return true;}
 if(a==='tape-start')return v027TapeStart(arg);
 if(a.startsWith('tape-'))return v027TapeControl(a.slice(5),arg);
 return false;
}
const v027Keys=handleKeyDown;handleKeyDown=function(e){if(mode==='PIP'){
 if(e.code==='Escape'||e.code==='Tab'){e.preventDefault();closePipboy();return;}
 if(['INPUT','TEXTAREA','SELECT'].includes(e.target?.tagName))return;
 const key=e.key.toLowerCase();const tabs=Object.keys(V027_TABS),subs=Object.keys(V027_SUBS[V027.tab]);
 if(['q','e'].includes(key)){e.preventDefault();v027Set(tabs[(tabs.indexOf(V027.tab)+(key==='e'?1:-1)+tabs.length)%tabs.length]);return;}
 if(['a','d','arrowleft','arrowright'].includes(key)){e.preventDefault();const next=['d','arrowright'].includes(key)?1:-1;v027Set(V027.tab,subs[(subs.indexOf(V027.sub)+next+subs.length)%subs.length]);return;}
 if(['arrowup','arrowdown'].includes(key)){e.preventDefault();const rows=[...$('pipContent').querySelectorAll('.p27-row')],i=rows.findIndex(r=>r.classList.contains('selected'));if(rows.length){const target=rows[(i+(key==='arrowdown'?1:-1)+rows.length)%rows.length];V027.selected=target.dataset.arg;renderPipboy();const el=[...$('pipContent').querySelectorAll('.p27-row')].find(r=>r.dataset.arg===V027.selected);el?.focus({preventScroll:true});el?.scrollIntoView({block:'nearest'});}return;}
 return;}
 if(mode==='PLAYING'&&e.code==='KeyI'&&!e.repeat&&!['INPUT','TEXTAREA','SELECT'].includes(e.target?.tagName)){e.preventDefault();v027Open('inventory','weapon');return;}
 return v027Keys(e);
};
const v027OpenField=v020OpenField;v020OpenField=function(...a){document.body.classList.remove('p27-open');return v027OpenField(...a);};
const v027ModalDismiss=v020CancelVats;v020CancelVats=function(...a){return v027ModalDismiss(...a);};
function v027ResumeSandbox(){try{const keys=[V018_SANDBOX_KEY,'fallout_mistral_sandbox_v026','fallout_mistral_sandbox_v025','fallout_mistral_sandbox_v024','fallout_mistral_sandbox_v023','fallout_mistral_sandbox_v022','fallout_mistral_sandbox_v021','fallout_mistral_sandbox_v020','fallout_mistral_sandbox_v018'];const key=keys.find(k=>localStorage.getItem(k));if(!key)return v027Notify('Aucune exploration sauvegardée.');const raw=JSON.parse(localStorage.getItem(key));v018ValidateSave(raw);state=migrateState(raw);v018SessionKind='sandbox';syncEquipment();gameStarted=true;hideAllScreens();loadZone(state.player.zone,{instance:!V015_GEO_MACROS[state.player.zone],force:true,silent:true,noTravel:true,spawn:state.player.pos,yaw:state.player.yaw});saveGame(false);return true;}catch(e){toast('Exploration non chargée : '+e.message,'bad');return false;}}
function v027Start(){if(!confirm('Commencer une exploration séparée pour essayer le Pip-Boy ? La campagne et les anciennes versions sont conservées. Seule l’exploration v0.27 précédente sera remplacée.'))return false;startNewGame(true);state.v018.travelMode='story';state.v027=v027Fresh();state.v027.documents={};V027.activeStation=null;state.equipment.ownedWeapons=['pistol10','pipeCarbine'];state.equipment.ownedArmors=['vaultSuit','workshopJacket'];state.player.weaponId='pistol10';state.player.armorId='vaultSuit';state.v020.favorites=['pistol10',null,null,null];addItem('radioTube',2);addItem('enamelCup',1);syncEquipment();state.v021.returnPoints=[{zone:'aubagne'}];loadZone('transit_depot',{instance:true,force:true,silent:true,noTravel:true,spawn:[0,1.65,44],yaw:0});saveGame(false);return v027Open('status','health');}
/* Legacy closeTrade/closeHack timers may request a lock after a new panel opens.
   Guard the shared canvas entry point and also release a late native grant. */
function v027GuardPointer(){const canvas=$('gameCanvas'),request=canvas.requestPointerLock?.bind(canvas);if(request){canvas.requestPointerLock=function(...args){if(mode!=='PLAYING'||zoneTransitioning||!gameStarted)return;try{const result=request(...args);return result?.catch?result.catch(()=>undefined):result;}catch{return;}};}document.addEventListener('pointerlockchange',()=>{if(document.pointerLockElement===canvas&&(mode!=='PLAYING'||zoneTransitioning))document.exitPointerLock?.();});}
function v027AfterInit(){v027Shell();v027GuardPointer();document.title='Fallout : Mistral · v0.27 · Le terminal au poignet';$('v020Version').textContent='v0.27 · Pip-Boy : STAT, INV, DATA, MAP, RADIO · recherche de composants · holodisques intégrés. Carte réelle non intégrée.';
 const b=document.createElement('button');b.id='btnV027';b.textContent='Pip-Boy · exploration séparée';b.onclick=v027Start;$('menuScreen').querySelector('nav').prepend(b);if($('btnV023Resume'))$('btnV023Resume').onclick=v027ResumeSandbox;
 const cap=document.createElement('div');cap.id='p27Captions';cap.hidden=true;cap.setAttribute('aria-live','polite');document.body.appendChild(cap);
 let last=performance.now();setInterval(()=>{const next=performance.now(),dt=Math.min(750,next-last);last=next;if(!V027.tapeManual)v027TapeTick(dt);},120);
 Object.assign(window.__MISTRAL_DEBUG,{openPip:(t)=>v027Open(t),closePip:closePipboy,setPipTab,debugOpenPip,v027Open,v027Set,v027Dispatch,v027Start,v027ResumeSandbox,v027Track,v027TapeStart,v027TapeTick,v027TapeControl,
 v027Info:()=>({version:VERSION,tabs:Object.keys(V027_TABS),subtabs:Object.fromEntries(Object.entries(V027_SUBS).map(([k,v])=>[k,Object.keys(v)])),officialTiles:0}),v027State:()=>deepClone(state.v027),v027UI:()=>({tab:V027.tab,sub:V027.sub,selected:V027.selected,mode,rows:[...$('pipContent').querySelectorAll('.p27-row')].map(b=>({id:b.dataset.arg,text:b.innerText})),tape:V027.tape?{...V027.tape}:null}),v027Select:id=>{V027.selected=id;renderPipboy();},v027QuestRows,v027Notes,v027Matches:v027ComponentMatches,v027ManualTape:b=>V027.tapeManual=b,
 v027ReadNote:(id,title,text)=>openNote(id,title,text),v027GiveTape:id=>{if(!V013_LORE_CATALOG[id]?.lines)return false;state.lore.holotapes[id]=true;return true;},v027MarkTerminal:id=>state.lore.terminals[id]=true,v027Pin:()=>({saved:state.v027.pin,runtime:V020.mapPin,path:V020.mapPath}),v027Subtitles:()=>({hidden:$('p27Captions').hidden,text:$('p27Captions').textContent}),v027DocumentSize:()=>Object.keys(state.v027.documents||{}).length});
}
