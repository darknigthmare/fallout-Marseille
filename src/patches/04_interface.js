/* v0.18 — Visible provenance, family-specific first person models and test hooks. */
const V018_RELEASE={name:'Les Fondations vérifiables',officialTilesBundled:0,officialTerrainBundled:0,coveragePlan:5884};
let v018StatusReturn='MENU';
function v018CoverageReport(){const a=world?.geoMacro?v017RecountAudit(world):V017_RUNTIME.audit;return{...V018_RELEASE,macroRegions:Object.keys(V015_GEO_MACROS).length,historicInstances:ALL_ZONE_IDS.length,actualRegionLoadedTiles:V017_RUNTIME.fixtureMode?0:(world?.geoTiles?.size||0),synthetic:!!V017_RUNTIME.fixtureMode,projection:'EPSG:2154 / 1 unité = 1 m',verticalDatum:world?.geoTerrain?.source||'Aucun MNT chargé',render:{...V018.render},audit:{...a}};}
function v018OpenStatus(){
  const r=v018CoverageReport();v018StatusReturn=mode;mode='STATUS';document.exitPointerLock?.();const screen=$('v018StatusScreen');screen.classList.remove('hidden');screen.innerHTML=`<div class="v018-status-box"><header><p class="eyebrow">ÉTAT RÉEL DE LA LIVRAISON · v0.18</p><h2>LE TERRITOIRE N’EST PAS ENCORE ACQUIS</h2><p>Le code géographique est corrigé. Le téléchargement des données réelles n’a pas abouti dans l’atelier de fabrication. Aucun faux village ne le remplace.</p></header><div class="v018-status-metrics"><article><b>0 / 5 884</b><span>Tuiles officielles incorporées</span></article><article><b>0 / 8</b><span>Modèles de terrain incorporés</span></article><article><b>${r.historicInstances}</b><span>Anciennes instances conservées</span></article></div><section><h3>Ne pas confondre</h3><p><strong>Plan de couverture :</strong> les huit régions prévues. Ce n’est pas un certificat de données téléchargées.</p><p><strong>Campagne :</strong> les quartiers scénarisés historiques restent jouables. Leur géométrie stylisée n’est pas la reproduction cadastrale.</p><p><strong>Extérieurs géographiques :</strong> polygones vectoriels et terrain importables. Les hauteurs manquantes utilisent une estimation explicitement comptée ; les points d’accès aux abris sont fictifs.</p><p><strong>Session courante :</strong> ${r.actualRegionLoadedTiles} tuile(s) locale(s), cache ou réseau, réellement chargée(s) ; ${r.synthetic?'jeu de test synthétique actif':'aucune fixture active'}.</p><p>Rendu : ${escapeHtml(r.render.backend)} · ${r.render.customMeshes||0} maillages géographiques actuellement affichés.</p></section><footer><button id="v018StatusClose" class="primary">Retour</button><button id="v018RestoreFromStatus">Restaurer la dernière copie de campagne</button></footer></div>`;$('v018StatusClose').onclick=()=>{screen.classList.add('hidden');mode=v018StatusReturn;};$('v018RestoreFromStatus').onclick=()=>{if(v018RestoreBackup())screen.classList.add('hidden');};
}
const v018Schedule=v017ScheduleAroundPlayer;
v017ScheduleAroundPlayer=function(w){if(V017_RUNTIME.fixtureMode||V018.testingNoNetwork)return;v018Schedule(w);};
const v018GeoHUD=v015UpdateGeoHud;
v015UpdateGeoHud=function(){v018GeoHUD();if(!world?.geoMacro)return;const a=V017_RUNTIME.audit;const modeLabel=V017_RUNTIME.fixtureMode?'TEST SYNTHÉTIQUE — PAS MARSEILLE':'EXTÉRIEUR · DONNÉES VÉRIFIABLES';$('geoMode').textContent=modeLabel;$('geoStream').textContent=`${world.geoTiles.size} TUILES CHARGÉES · ${a.assumedHeights||0} HAUTEURS ESTIMÉES · 1 UNITÉ = 1 M`;$('v018FixtureMark')?.classList.toggle('hidden',!V017_RUNTIME.fixtureMode);};
const v018UpdateHud=updateHUD;
let v018WeaponLast='';
function v018WeaponFamily(w){const t=(w.name||'').toLowerCase();if(w.melee||w.ammoType==='melee'||/couteau|marteau|masse|hache|tronçon|machette|gantelet|poing|glaive|scie|éventreur|batte/.test(t))return'melee';if(/rivete|harpon|cérami|lance-brique|soude|chalumeau|clou/.test(t))return'industrial';if(/laser|plasma|tesla|gauss|gamma|énergie|émetteur/.test(t))return'energy';if(/minigun|gatling|fat man|mortier|missile|canon|mitrailleuse|lance-grenades|incinér/.test(t))return'heavy';if(/pompe|chevrotine|double canon|fusil de quai|shotgun|caravane/.test(t))return'shotgun';if(/pistolet|revolver|derringer|délivreur/.test(t))return'pistol';return'rifle';}
function v018WeaponSVG(kind){const pieces={
  pistol:'<path d="M145 91L233 58 298 96 207 139Z" fill="url(#steel)"/><path d="M211 74L226 70 272 97 256 102Z" fill="#1b2323"/><path d="M155 108L188 97 217 163 184 184 165 154Z" fill="#454837"/><path d="M145 91L151 77 237 45 299 85 298 96 233 58Z" fill="#838a7b"/><path d="M274 72L290 65 301 73 298 85Z" fill="#151f20"/>',
  rifle:'<path d="M30 164L196 71 267 73 295 94 166 166 95 204Z" fill="url(#steel)"/><path d="M196 71L262 31 276 43 229 83Z" fill="#59685e"/><path d="M245 36L255 12 270 18 268 35Z" fill="#1b2321"/><path d="M163 119L193 103 220 175 190 188Z" fill="#303d39"/><path d="M77 160L145 122 157 144 83 192Z" fill="#806644"/><path d="M175 79L198 66 220 78 195 93Z" fill="#151e1d"/>',
  shotgun:'<path d="M25 192L175 90 242 92 268 111 113 224Z" fill="#67513b"/><path d="M174 89L264 30 279 42 210 103Z" fill="url(#steel)"/><path d="M203 94L284 43 294 59 232 109Z" fill="#59675f"/><path d="M96 170L179 120 198 139 113 192Z" fill="#998052"/><path d="M103 169L179 126M110 179L186 134" stroke="#463929" stroke-width="5"/>',
  energy:'<path d="M61 164L184 63 269 58 311 106 182 203Z" fill="#767f51"/><path d="M154 83L243 34 277 53 193 109Z" fill="url(#steel)"/><path d="M220 39L237 11 273 27 266 56Z" fill="#4b5f54"/><path d="M118 156L203 101 244 127 163 181Z" fill="#303d31"/><path d="M138 154L207 113M150 163L218 121" stroke="#bde477" stroke-width="7"/><circle cx="275" cy="88" r="16" fill="#c69342"/><path d="M68 152L104 126 137 158 111 184Z" fill="#484c3a"/>',
  heavy:'<path d="M10 162L139 55 240 60 322 125 191 242Z" fill="url(#steel)"/><ellipse cx="202" cy="77" rx="71" ry="41" transform="rotate(-25 202 77)" fill="#788276"/><path d="M133 65L230 3 297 40 203 105Z" fill="#343f3c"/><path d="M141 68L238 10M156 77L255 21M172 88L275 34" stroke="#9a9d87" stroke-width="10"/><circle cx="93" cy="172" r="43" fill="#616c58"/><circle cx="93" cy="172" r="27" fill="#2d3a32"/>',
  industrial:'<path d="M65 168L160 73 262 68 304 112 188 219Z" fill="#b7974d"/><path d="M172 66L243 16 283 37 211 98Z" fill="#4e5b55"/><path d="M123 139L197 90 233 115 154 177Z" fill="#343e34"/><path d="M131 141L197 99M147 153L213 113" stroke="#e2c96a" stroke-width="8"/><path d="M82 153L126 118M199 176L264 128" stroke="#303e32" stroke-width="12"/><circle cx="267" cy="91" r="19" fill="#d4ceab"/><path d="M267 91L275 81" stroke="#743c28" stroke-width="3"/>',
  melee:'<path d="M169 211L201 185 113 92 91 112Z" fill="#6d563c"/><path d="M92 112L125 89 130 61 76 9 35 25 29 61 61 97Z" fill="url(#steel)"/><path d="M42 37L79 25 113 62 102 80 66 65Z" fill="#91968a"/><path d="M130 156L159 134M139 169L169 146M154 187L184 165" stroke="#b9a179" stroke-width="7"/>'};
  return `<svg viewBox="0 0 360 260" aria-hidden="true"><defs><linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#a0a590"/><stop offset=".4" stop-color="#505c50"/><stop offset=".75" stop-color="#253633"/><stop offset="1" stop-color="#172622"/></linearGradient></defs><path d="M130 260L103 190 123 165 162 180 194 260Z" fill="#456058"/><path d="M109 192L119 163 157 158 181 185 164 218 129 219Z" fill="#837456"/>${pieces[kind]||pieces.rifle}<path d="M252 260L205 213 221 168 251 167 278 197 296 260Z" fill="#394d46"/><path d="M216 195L217 174 237 155 257 163 266 190 251 216 231 216Z" fill="#9d8861"/></svg>`;}
updateHUD=function(){v018UpdateHud();const w=currentWeapon(),kind=v018WeaponFamily(w);if(kind!==v018WeaponLast){v018WeaponLast=kind;const m=$('weaponModel');m.classList.add('v018-viewmodel');m.dataset.family=kind;m.innerHTML=v018WeaponSVG(kind)+'<i id="muzzleFlash" class="muzzle-flash"></i>';}
  const el=$('v018ReloadProgress');if(el){el.classList.toggle('hidden',reloadTimer<=0);el.textContent=reloadTimer>0?`RECHARGEMENT · ${reloadTimer.toFixed(1)} s`:'';}
  if(!world?.geoMacro)$('v018FixtureMark')?.classList.add('hidden');
};
function v018Atlas(c){const regions=Object.entries(V015_GEO_MACROS);c.innerHTML=`<section class="v018-atlas"><p class="eyebrow">ATLAS DE COUVERTURE · PAS UN FOND CARTOGRAPHIQUE</p><h2>HUIT TERRITOIRES, DEUX NIVEAUX DE PREUVE</h2><p>Les coordonnées ci-dessous localisent le périmètre prévu. La livraison ne contient aucune tuile officielle ni aucun relief importé. Les instances historiques sont des créations de jeu, pas des reproductions exactes des lieux.</p><div class="v018-journal-tools"><button id="v018DataStatus">État des données</button><input id="v018AtlasSearch" placeholder="Rechercher une instance…" aria-label="Rechercher une destination"></div><div class="v018-regions">${regions.map(([id,d])=>`<article><h3>${escapeHtml(d.region.replace('MACRO-RÉGION · ',''))}</h3><small>${d.bbox.map(x=>x.toFixed(3)).join(' / ')}</small><p>Lambert-93 · échelle métrique<br>Relief : non inclus</p><button data-region="${id}">Ouvrir l’extérieur strict</button></article>`).join('')}</div><h3>INSTANCES HISTORIQUES CONSERVÉES</h3><div id="v018Destinations" class="v018-destinations"></div></section>`;
  const render=()=>{const q=$('v018AtlasSearch').value.toLowerCase();$('v018Destinations').innerHTML=ALL_ZONE_IDS.filter(id=>(id+' '+v018ZoneName(id)).toLowerCase().includes(q)).map(id=>`<button data-instance="${id}" ${!isZoneUnlocked(id)?'disabled':''}>${escapeHtml(v018ZoneName(id))}</button>`).join('');$('v018Destinations').querySelectorAll('[data-instance]').forEach(b=>b.onclick=()=>{if(inCombat){toast('Voyage indisponible pendant un combat.');return;}closePipboy();state.v018.travelMode='story';loadZone(b.dataset.instance,{instance:true});});};render();$('v018AtlasSearch').oninput=render;$('v018DataStatus').onclick=v018OpenStatus;c.querySelectorAll('[data-region]').forEach(b=>b.onclick=()=>{if(inCombat){toast('Voyage indisponible pendant un combat.');return;}closePipboy();state.v018.travelMode='geographic';loadZone(b.dataset.region,{geoDirect:true});});
}
renderPipMap=v018Atlas;
v017RenderGeoMap=v018Atlas;
function v018AfterInit(){
  const s=document.createElement('section');s.id='v018StatusScreen';s.className='v018-status-screen hidden';s.setAttribute('role','dialog');s.setAttribute('aria-label','État de la cartographie');document.body.appendChild(s);
  const badge=document.createElement('div');badge.id='v018FixtureMark';badge.className='v018-fixture-mark hidden';badge.textContent='GÉOMÉTRIE DE TEST SYNTHÉTIQUE — CE N’EST PAS UNE CARTE RÉELLE';$('hud').appendChild(badge);
  const reload=document.createElement('div');reload.id='v018ReloadProgress';reload.className='v018-reload hidden';$('weaponHud').appendChild(reload);
  const b=document.createElement('button');b.id='v018MenuStatus';b.textContent='État des données et de la build';$('menuScreen').querySelector('nav').appendChild(b);b.onclick=v018OpenStatus;
  $('btnChapter').textContent='Bac à sable · sauvegarde séparée';$('btnNew').textContent='Nouvelle campagne · instances historiques';
}
Object.assign(window.__MISTRAL_DEBUG,{
  v018Status:v018CoverageReport,v018OpenStatus,v018Projection:(lat,lon)=>({xy:v018Lambert93(lat,lon),inverse:v018InverseLambert(...v018Lambert93(lat,lon))}),
  v018Triangulate:(rings)=>v018Triangulate(rings),v018Groups:(rings)=>v018PolygonGroups(rings),v018Contains:(rings,x,z)=>v018Contains(rings,x,z),
  v018Ray:(rings,origin,dir,minY=0,maxY=10)=>{const b=v017PolyBounds(rings);return rayAABB(origin,dir,{poly:rings[0],rings,minX:b.minX,maxX:b.maxX,minZ:b.minZ,maxZ:b.maxZ,minY,maxY});},
  v018Collision:(rings,x,z)=>{const b=v017PolyBounds(rings);return v017ColliderHit({poly:rings[0],rings,minX:b.minX,maxX:b.maxX,minZ:b.minZ,maxZ:b.maxZ,minY:0,maxY:20},x,z,.2);},
  v018Terrain:(j)=>v018SetTerrain(world,j),v018TerrainSample:(lat,lon)=>{const p=v015GeoProject(world.id,lat,lon);return v017TerrainHeight(world,p[0],p[2]);},
  v018NoNetwork:(v=true)=>V018.testingNoNetwork=v,v018ReadLayers:(bytes)=>v017DecodeMVT(new Uint8Array(bytes)),
  v018Apply:(source,key,layers,z,x,y,provenance='fixture')=>(source==='cadastre'?v017ApplyCadastreTile:v017ApplyFranceTile)(world,key,layers,z,x,y,provenance),
  v018Prune:()=>v017PruneTiles(world),v018Geometry:()=>world.staticDraws.filter(d=>['prism','flatpoly','terrain','geoSurface'].includes(d.mesh)).map(d=>({mesh:d.mesh,rings:d.rings,baseY:d.baseY,height:d.height,id:d.id,hidden:d.hidden,pos:d.pos,layer:d.geoLayer,roadPath:d.roadPath,vertices:d.vertices,faces:d.faces})),
  v018LoadInstance:(id='vault')=>{V018.testingNoNetwork=true;gameStarted=true;state.v018.travelMode='story';hideAllScreens();loadZone(id,{instance:true,silent:true,force:true});mode='PLAYING';$('hud').classList.add('active');return id;},
  v018LoadMacro:(id='geo_marseille')=>{V018.testingNoNetwork=true;gameStarted=true;state.v018.travelMode='geographic';hideAllScreens();loadZone(id,{geoDirect:true,silent:true,force:true,spawn:[0,1.65,0]});mode='PLAYING';$('hud').classList.add('active');return id;},
  v018SetCamera:(pos,yaw=0,pitch=0)=>{state.player.pos=[...pos];state.player.yaw=yaw;state.player.pitch=pitch;return pos;},
  v018InspectSave:(data)=>v018ValidateSave(data),v018ImportRaw,v018RestoreBackup,v018Migrate:(s)=>migrateState(s),
  v018SaveKey:()=>v018SaveKey(),v018Keys:()=>({campaign:SAVE_KEY,sandbox:V018_SANDBOX_KEY}),v018StartFree:()=>startNewGame(true),v018StartStory:()=>startNewGame(false),
  v018Journal:()=>v018Journal(),v018Track:(id)=>state.v018.trackedQuest=id,v018Marker:()=>getObjectiveMarker(),v018QuestData:()=>deepClone(V013_LOCAL_QUESTS),
  v018QuestStage:(id,stage)=>state.lore.localQuests[id]=stage,v018ResolveLocal:(id,outcome)=>v013ResolveLocalQuest(id,outcome),
  v018TapeOpen:openHolotape,v018TapeState:()=>holotapeState?{...holotapeState}:null,v018TapeDuration,v018TapeTick,v018TapeStep:(n)=>v013HolotapeStep(n),v018TapePlay:(on)=>v013HolotapePlay(on),v018TapeClose:closeHolotape,
  v018WeaponFamily:(id)=>v018WeaponFamily(WEAPONS[id]||{}),v018World:()=>({id:world.id,bounds:world.bounds,spawn:world.spawn,subzones:deepClone(world.subzones),portals:deepClone(world.geoPortals||{}),colliders:deepClone(world.colliders)}),
  v018RenderInfo:()=>({...V018.render}),v018RetryInfo:()=>[...V018_RETRY],v018Queue:(source,z,x,y)=>v017QueueTile(world,source,z,x,y),
  v018Fixture:(name=true)=>{V017_RUNTIME.fixtureMode=!!name;V018.testingNoNetwork=true;$('v018FixtureMark').classList.toggle('hidden',!name);},
  v018IsolatedFixture:()=>{world.staticDraws=[];world.colliders=[];world.npcs=[];world.enemies=[];world.loot=[];world.interactables=[];world.ambient=[];world.hazards=[];world.subzones=[];state.player.activeCompanion=null;V017_RUNTIME.fixtureMode=true;V018.testingNoNetwork=true;}
});

Object.assign(window.__MISTRAL_DEBUG,{
 v018GeometryContract:()=>{
   let draws=0,buffers=0,deleted=0,uploads=0;const g=new Proxy({createBuffer:()=>({n:++buffers}),deleteBuffer:()=>deleted++,bufferData:()=>uploads++,drawElements:()=>draws++,getUniformLocation:()=>1},{get:(o,k)=>k in o?o[k]:typeof k==='string'&&k===k.toUpperCase()?1:()=>{}});
   const r=Object.create(GLRenderer.prototype);r.gl=g;r.canvas={width:640,height:480};r.resize=()=>{};r.program={};r.loc={};r.meshes={};const ring=[[0,0],[10,0],[10,10],[0,10],[0,0]],hole=[[3,3],[3,7],[7,7],[7,3],[3,3]],d={mesh:'prism',pos:[5,3,5],rings:[ring,hole],baseY:0,height:6,color:[.7,.6,.5]};
   r.render([d],{pos:[20,18,22],dir:[-1,-.5,-1]},{});const retained=r.geoMeshes.size;r.render([],{pos:[20,18,22],dir:[-1,-.5,-1]},{});return{draws,buffers,deleted,uploads,retained,released:r.geoMeshes.size,kind:'API GL simulée — pas un pilote GPU'};
 },v018ShaderSources:()=>GLRenderer.toString().match(/const (?:vs|fs)=`[^`]+`/g),
 v018Terminal:(zone)=>openLoreTerminal(zone,true),v018TerminalAction:(zone)=>executeTerminalAction(zone),
 v018PersistentStatus:()=>({error:V018.saveError||null,session:v018SessionKind,key:v018SaveKey()}),
 v018SafeWorldInfo:()=>({id:world?.id,draws:world?.staticDraws.length,npcs:world?.npcs.length,enemies:world?.enemies.length,interactables:world?.interactables.length}),
 v018CloseStatus:()=>{$('v018StatusScreen').classList.add('hidden');mode=v018StatusReturn;}
});
const v018Toast=toast;
toast=function(text,type=''){v018Toast(text,type);const stack=$('toastStack');while(stack.children.length>4)stack.firstElementChild.remove();};
const v018PlayerUpdate=updatePlayer;
updatePlayer=function(dt){if(V018.qaFreeze)return;v018PlayerUpdate(dt);};
Object.assign(window.__MISTRAL_DEBUG,{
 v018CaptureAt:(pos,yaw=0,pitch=0)=>{debugRenderPaused=true;V018.qaFreeze=true;state.player.cameraMode='first';state.player.pos=[...pos];state.player.yaw=yaw;state.player.pitch=pitch;$('toastStack').innerHTML='';updateHUD();sky.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),getCamera(gameClock),currentEnv());return{camera:getCamera(gameClock),renderer:{...V018.render}};},
 v018ResumeSimulation:()=>{V018.qaFreeze=false;debugRenderPaused=false;},v018ToastTest:()=>{for(let i=0;i<20;i++)toast('Notification de test '+i);return $('toastStack').children.length;}
});

Object.assign(window.__MISTRAL_DEBUG,{v018WeaponCatalog:()=>Object.entries(WEAPONS).map(([id,w])=>({id,name:w.name,family:v018WeaponFamily(w)}))});

Object.assign(window.__MISTRAL_DEBUG,{
 v018HeightInfo:p=>v018HeightInfo({props:p}),
 v018PendingLoad:id=>loadZone(id,{instance:true,force:true}),
 v018ReloadState:()=>({timer:reloadTimer,weapon:currentWeapon().id,ammo:state.player.ammoInMag}),
 v018ManualTick:dt=>{updatePlayer(dt);updateHUD();},
 v018StreamSourceForQA:fn=>{v017GetTileBuffer=fn;},
 v018StreamEpoch:()=>V018.geoEpoch
});
