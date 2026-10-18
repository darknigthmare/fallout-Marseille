/* v0.41 — authenticated 24-chunk local territory pack and benchmark state. */
const V041_PACK_RELAY='https://hykklcvvwjwhcvukbzts.supabase.co/functions/v1/fallout-mistral-local-pack-v041';
const V041_PACK_SNAPSHOT={version:'0.41.0',coordinates:5884,baseCoordinates:367,cadastreCoordinates:5517,pbfObjects:4557,officialEmpty:1327,chunkCount:24,baseChunks:5,cadastreChunks:19,totalBase64Bytes:119130028,format:'zip',jwtRequired:true};
const V041={remote:{state:'unchecked',...V041_PACK_SNAPSHOT,error:null,checkedAt:null},local:{state:'unchecked',complete:false,coordinates:0,objects:0,officialEmpty:0,missing:5884,invalid:0,bytes:0,terrain:0,error:null,checkedAt:null},benchmark:{state:'unchecked',sampledPbf:0,decodedBytes:0,seconds:0,throughputMiBps:0,tilesPerSecond:0,p95:0,peakRssKiB:0,terrain:0,completePack:false,error:null,checkedAt:null}};
function v041Fresh(){return{schema:1,lastPackCheck:null,localPackComplete:false,localCoordinates:0,localTerrain:0,lastBenchmark:null}}
const v041BaseState=baseState;baseState=function(){const s=v041BaseState();s.v041=v041Fresh();return s};
const v041MigrateBase=migrateState;migrateState=function(input={}){const s=v041MigrateBase(input),f=v041Fresh(),p=input.v041||{};s.v041={...f,...p};return s};state=migrateState(state);
settings.geoPreferLocalPack=settings.geoPreferLocalPack!==false;
