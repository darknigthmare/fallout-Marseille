/* v0.38 — complete persistent vector cache, including official empty tiles. */
const V038_RELAY='https://hykklcvvwjwhcvukbzts.supabase.co/functions/v1/fallout-mistral-map-v038';
const V038_PLAN={version:'0.38.0',base:367,cadastre:5517,total:5884,basePbf:367,cadastrePbf:4190,cadastreEmpty:1327,totalPbf:4557,totalEmpty:1327,cloudBytes:86973739,terrainExpected:8,terrainBundled:0,bounds:{south:43.125,west:5.255,north:43.420,east:5.755}};
const V038_SNAPSHOT={verifiedAt:'2026-09-19T01:53:47Z',base:{coordinates:367,pbf:367,empty:0,bytes:29456613,hits:31},cadastre:{coordinates:5517,pbf:4190,empty:1327,bytes:57517126,hits:1},total:5884,totalBytes:86973739,totalEmpty:1327,complete:true};
const V038={relay:V038_RELAY,lastCoverage:null,emptyTilesServed:0,dataTilesServed:0,proof:{filled:{source:'cadastre',z:16,x:33757,y:23976,bytes:3816,sha256:'07bdaf302341a82085ffda39ab10b35444e26313c6f3401f873ac2a2b294c6c7'},empty:{source:'cadastre',z:16,x:33730,y:23996,bytes:0,sha256:'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}}};
function v038Fresh(){return{schema:1,lastCoverage:null,fullVectorCacheConfirmed:false,emptyTilesLoaded:0,dataTilesLoaded:0,verifiedAt:null}}
const v038BaseState=baseState;baseState=function(){const s=v038BaseState();s.v038=v038Fresh();return s};
const v038Migrate=migrateState;migrateState=function(input={}){const s=v038Migrate(input),f=v038Fresh(),p=input.v038||{};s.v038={...f,...p};return s};state=migrateState(state);
