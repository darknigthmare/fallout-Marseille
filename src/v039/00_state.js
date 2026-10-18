/* v0.39 — official RGE ALTI sampled terrain for all eight real macro-regions. */
const V039_TERRAIN_RELAY='https://hykklcvvwjwhcvukbzts.supabase.co/functions/v1/fallout-mistral-terrain-v039';
const V039_TERRAIN_PLAN={version:'0.39.0',regions:8,width:161,height:161,samplesPerRegion:25921,totalSamples:207368,valid:174944,missing:32424,bytes:1260176,resource:'ign_rge_alti_wld',source:'RGE ALTI IGN',sourceTitle:'Pyramide RGE Alti France Entière (Métropole, DOM et COM couvertes)',license:'Licence Ouverte 2.0',verticalDatum:'NGF-IGN69 — altitude normale, France continentale',noDataThreshold:-100};
const V039_TERRAIN_SNAPSHOT={complete:true,count:8,totalBytes:1260176,totalValid:174944,totalMissing:32424,regions:{
 geo_calanques:{valid:21063,missing:4858,min:-8.52,max:638.19,mean:131.902,bytes:137635},geo_etoile:{valid:25921,missing:0,min:64.99,max:768.45,mean:317.122,bytes:178722},geo_frioul:{valid:6198,missing:19723,min:-67.51,max:81.92,mean:2.89132,bytes:121364},geo_garlaban:{valid:25921,missing:0,min:60,max:1031.19,mean:304.142,bytes:178206},geo_huveaune:{valid:25921,missing:0,min:24.82,max:708.45,mean:210.666,bytes:176122},geo_laciotat:{valid:21717,missing:4204,min:-8.94,max:560.11,mean:150.016,bytes:144586},geo_marseille:{valid:22282,missing:3639,min:-17.9,max:643.91,mean:109.791,bytes:144478},geo_saintebaume:{valid:25921,missing:0,min:74.49,max:1029.36,mean:367.892,bytes:179063}
}};
const V039={cloud:{state:'snapshot',...deepClone(V039_TERRAIN_SNAPSHOT),error:null,checkedAt:null},loaded:new Map(),last:null,requests:0,cacheHits:0,packHits:0,cloudHits:0,errors:0};
function v039Fresh(){return{schema:1,terrainCloudConfirmed:false,lastTerrainCheck:null,terrainLoads:0,terrainPackHits:0,terrainCacheHits:0,terrainCloudHits:0,terrainErrors:0,lastTerrainMacro:null,lastTerrainSource:null}}
const v039BaseState=baseState;baseState=function(){const s=v039BaseState();s.v039=v039Fresh();return s};
const v039Migrate=migrateState;migrateState=function(input={}){const s=v039Migrate(input),f=v039Fresh(),p=input.v039||{};s.v039={...f,...p};return s};state=migrateState(state);
settings.geoTerrain=settings.geoTerrain!==false;settings.geoTerrainCache=settings.geoTerrainCache!==false;
V027_SUBS.map.terrain='RELIEF IGN';
function v039TerrainName(id){return V015_GEO_MACROS[id]?.region?.replace('MACRO-RÉGION · ','')||id}
