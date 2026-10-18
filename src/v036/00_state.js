/* v0.36 — official vector territory streaming. No procedural substitute is added. */
const V036_RELAY='https://hykklcvvwjwhcvukbzts.supabase.co/functions/v1/fallout-mistral-map-v036';
const V036_PUBLIC_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYXNlIiwicmVmIjoiaHlra2xjdnZ3andocmN2dWtienRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4NTgwNjAsImV4cCI6MjA5NzQzNDA2MH0.630TpeNsO-W7CT2QTQ53_3Y36ioOjvHB6-Pst6AQY7g';
const V036_PLAN={version:'0.36.0',base:367,cadastre:5517,total:5884,terrainExpected:8,terrainBundled:0,bounds:{south:43.125,west:5.255,north:43.420,east:5.755}};
const V036={health:{state:'unchecked',checkedAt:null,checks:[],error:null},lastTransfer:0,transferCount:0,lastLatLon:null,manifestChecked:false,installed:null};
function v036Fresh(){return{schema:1,preferRelay:true,autoMacroTransfer:true,lastMacro:null,lastLatLon:null,onlineTilesLoaded:0,localTilesLoaded:0,cacheTilesLoaded:0};}
const v036BaseState=baseState;baseState=function(){const s=v036BaseState();s.v036=v036Fresh();return s;};
const v036Migrate=migrateState;migrateState=function(input={}){const s=v036Migrate(input),f=v036Fresh(),p=input.v036||{};s.v036={...f,...p};s.v036.preferRelay=p.preferRelay!==false;s.v036.autoMacroTransfer=p.autoMacroTransfer!==false;return s;};state=migrateState(state);
settings.geoStreaming=settings.geoStreaming!==false;settings.geoOfflineFirst=settings.geoOfflineFirst!==false;settings.geoCache=settings.geoCache!==false;
// Two planned macro-regions were absent from the historical runtime. They now stream the same official layers.
V015_GEO_MACROS.geo_etoile??={name:'Massif de l’Étoile · Territoire réel',region:'MACRO-RÉGION · ÉTOILE',center:[43.3600,5.5150],bbox:[43.3000,5.4350,43.4200,5.6000],scale:.070,kind:'hills',neighbors:['geo_marseille','geo_huveaune','geo_garlaban']};
V015_GEO_MACROS.geo_saintebaume??={name:'Sainte-Baume · Territoire réel',region:'MACRO-RÉGION · SAINTE-BAUME',center:[43.3125,5.6600],bbox:[43.2150,5.5650,43.4100,5.7550],scale:.066,kind:'hills',neighbors:['geo_garlaban','geo_calanques','geo_laciotat']};
V015_MACRO_BRIDGES.geo_etoile??=[['geo_marseille','accates','VERS MARSEILLE'],['geo_garlaban','latreille','VERS GARLABAN']];
V015_MACRO_BRIDGES.geo_saintebaume??=[['geo_garlaban','gemenos','VERS GÉMENOS'],['geo_calanques','roquefort','VERS CASSIS'],['geo_laciotat','ceyreste','VERS LA CIOTAT']];
for(const id of['geo_etoile','geo_saintebaume'])if(!ALL_ZONE_IDS.includes(id))ALL_ZONE_IDS.push(id);
