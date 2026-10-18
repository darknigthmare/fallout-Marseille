/* v0.42 — deterministic Fallout content layer over the real geographic territory. */
const V042_SITE_BY_ID=Object.fromEntries(V042_CATALOG.map(s=>[s.id,s]));
const V042_SITES_BY_MACRO=Object.fromEntries(Object.keys(V042_MACRO_PROFILES).map(id=>[id,V042_CATALOG.filter(s=>s.macro===id)]));
const V042_KIND_LABELS={shelter:'ABRI',settlement:'COLONIE',outpost:'AVANT-POSTE',interior:'LIEU VISITABLE',nest:'NID HOSTILE',elite:'MENACE ÉLITE',boss:'BOSS RÉGIONAL',landmark:'POINT REMARQUABLE',caravan:'HALTE CARAVANIÈRE'};
const V042_KIND_COLORS={shelter:[.71,.64,.24],settlement:[.35,.69,.39],outpost:[.47,.62,.34],interior:[.36,.56,.58],nest:[.62,.25,.17],elite:[.76,.42,.12],boss:[.78,.14,.12],landmark:[.57,.55,.36],caravan:[.65,.49,.24]};
const V042_INSTANCE_ZONE='v042_expedition';
if(!ALL_ZONE_IDS.includes(V042_INSTANCE_ZONE))ALL_ZONE_IDS.push(V042_INSTANCE_ZONE);
function v042Fresh(){return{schema:1,discovered:{},cleared:{},visited:{},tracked:null,activeContract:null,contracts:{},siteKills:{},eliteKills:{},bossKills:{},regional:{},activeInterior:null,returnPoint:null,discoveries:0,clears:0,filter:'all',lastSite:null,lastUpdate:null};}
const v042BaseState=baseState;baseState=function(){const s=v042BaseState();s.v042=v042Fresh();s.geo??={};s.geo.return??=null;s.geo.pendingTarget??=null;s.geo.lastMacro??='geo_huveaune';s.geo.visitedMacros??={};s.geo.surfaceVisited??={};s.geo.surfaceActions??={};s.geo.lastSurface??=null;s.geo.discoveryCount??=Object.keys(s.geo.surfaceVisited).length;return s;};
const v042MigrateBase=migrateState;migrateState=function(input={}){const s=v042MigrateBase(input),f=v042Fresh(),p=input.v042||{};s.v042={...f,...p,discovered:{...f.discovered,...(p.discovered||{})},cleared:{...f.cleared,...(p.cleared||{})},visited:{...f.visited,...(p.visited||{})},contracts:{...f.contracts,...(p.contracts||{})},siteKills:{...f.siteKills,...(p.siteKills||{})},eliteKills:{...f.eliteKills,...(p.eliteKills||{})},bossKills:{...f.bossKills,...(p.bossKills||{})},regional:{...f.regional,...(p.regional||{})}};if(s.v042.tracked&&!V042_SITE_BY_ID[s.v042.tracked])s.v042.tracked=null;if(s.v042.activeInterior&&!V042_SITE_BY_ID[s.v042.activeInterior])s.v042.activeInterior=null;return s;};
state=migrateState(state);
settings.geoFalloutLayer=settings.geoFalloutLayer!==false;
settings.geoContentBudget=clamp(Number(settings.geoContentBudget)||7,3,12);
settings.geoShowUnknownMajor=settings.geoShowUnknownMajor!==false;
const V042_RUNTIME={worldId:null,active:new Map(),clock:0,nearest:null,discoveredNow:[],spawnedEnemies:0,spawnedNpcs:0,lastCounts:{},npcData:new Map(),instanceSite:null};
function v042Site(id){return V042_SITE_BY_ID[id]||null;}
function v042Sites(macro=world?.id){return V042_SITES_BY_MACRO[macro]||[];}
function v042IsHostileSite(s){return!!s&&['nest','elite','boss'].includes(s.kind);}
function v042IsMajorSite(s){return!!s&&['shelter','settlement','boss','interior'].includes(s.kind);}
function v042SiteCleared(s){return!!state.v042.cleared[s.id];}
function v042SiteDiscovered(s){return!!state.v042.discovered[s.id];}
function v042Regional(macro){const r=state.v042.regional[macro]||{discovered:0,cleared:0,boss:false};state.v042.regional[macro]=r;return r;}
function v042SiteLabel(s){return`${V042_KIND_LABELS[s.kind]||s.kind} · ${s.name}`;}
function v042TierLabel(n){return['','I','II','III','IV','V'][clamp(n,1,5)]||String(n);}
