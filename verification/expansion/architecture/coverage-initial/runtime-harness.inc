function runtime(){
 const core=fs.readFileSync(path.join(root,'src/core-v017.js'),'utf8'),patch=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8'),c=vm.createContext({console,URL,MistralFacades:F});
 let harness=`const deepClone=o=>JSON.parse(JSON.stringify(o)),cMix=(a,b,t)=>a.map((v,i)=>v+(b[i]-v)*t),COLORS={limestone:[.5,.5,.4],black:[0,0,0],roof:[.4,.2,.1],rust:[.4,.3,.2],darkMetal:[.2,.2,.2]};
 const test={failSave:false,throwSave:false,saves:0,saved:null,sight:true,threat:false,ground:()=>0,blocked:()=>false,ensureFail:false,defer:false,resolve:null,autoResults:[],notes:[],dialogue:null,badBuild:false};
 const V015_GEO_MACROS={geo_marseille:{bbox:[43.22,5.285,43.34,5.51]},geo_huveaune:{bbox:[43.245,5.43,43.335,5.64]}},ALL_ZONE_IDS=['geo_marseille'],V046={busy:false,terrain:{},readyAnchor:[0,0,0]},V047={pending:null},V017_RUNTIME={loaded:new Map()},V042_RUNTIME={active:new Map(),npcData:new Map(),worldId:'geo_marseille'};
 let mode='PLAYING',zoneTransitioning=false,jumpVelocity=0,onGround=true;
 function baseState(){return{player:{zone:'geo_marseille',pos:[10,1.65,-1.15],yaw:.7,pitch:.2,hp:100,crouched:false},inventory:{scrap:7},flags:{looted:{}},v026:{containers:{}}};}
 function migrateState(s={}){return deepClone(s.player?s:baseState());}
 let state=baseState();
 function v015GeoUnproject(id,x,z){return[43.3-z/110000,5.4+x/80000];}function v046Region(lat,lon){return Number.isFinite(lat)&&Number.isFinite(lon)?'geo_marseille':null;}
 function saveGame(){test.saves++;if(test.throwSave)throw Error('disk full');if(test.failSave)return false;test.saved=JSON.stringify(state);return true;}
 function v049Own(){}function toast(){}function updateLocation(){}function updateHUD(){}function startNewGame(){}
 function lineOfSight(){return test.sight;}function v050TravelNearbyThreat(){return test.threat;}function v047Bank(){return{};}function v047Height(bank,x,z){return{height:test.ground(x,z)};}
 function v018ZoneName(id){return id;}function worldRegionLabel(id){return id;}function isZoneUnlocked(){return true;}
 function collidesAt(x,z){return test.blocked(x,z);}function tryPlayerMove(dx,dz){state.player.pos[0]+=dx;state.player.pos[2]+=dz;return true;}
 function updatePlayer(){}function v046Publish(){}function v046Cancel(){V046.busy=false;zoneTransitioning=false;mode='PLAYING';}
 function closeDialogue(){mode='PLAYING';test.dialogue=null;}function speaker(name,role){return{name,role};}function openDialogue(person,text,choices){mode='DIALOGUE';test.dialogue={person,text,choices};}function openNote(id,title,text){test.notes.push({id,title,text});}
 function v026NewContainer(w,id,title,pos,items){const key=w.id+'|'+id;state.v026.containers[key]??={id,title,pos:pos.slice(),items:deepClone(items)};return[key,state.v026.containers[key]];}function v026Attach(w,key,c){addInteract(w,'stash:'+key,[c.pos[0],c.pos[1]+1.05,c.pos[2]],'Stash',()=>{},{});}
 globalThis.window=globalThis;window.__MISTRAL_DEBUG={};
 `;
 harness+=core.slice(core.indexOf('function createWorld('),core.indexOf('function addBuilding('));
 for(const name of['v017SignedArea','v017PolyBounds','v017AddPrism','v017AddPolyCollider','v017PointInPoly','v017PointSegDist'])harness+='\n'+core.split('\n').find(l=>l.startsWith('function '+name+'('));
 harness+='\nconst V017_PRISM_BASE=v017AddPrism;\n'+patch.slice(patch.indexOf('const V018_EPS'),patch.indexOf('function v018MeshData('));
 harness+=`
 function exterior(){const w=createWorld('geo_marseille','Exterior','Marseille');w.v046=true;w.geoMacro=true;w.v046Records=new Map();w.staticDraws.push({mesh:'prism',rings:${JSON.stringify(square)},baseY:0,height:12,geoLayer:'building',geoFeatureId:'runtime-source',geoProperties:{nombre_d_etages:3,usage_1:'Résidentiel'},v046GeometryId:'source-geometry'});return w;}
 let world=exterior();
 function buildWorld(id){if(test.badBuild)throw Error('broken builder');return exterior();}
 async function v046Ensure(lat,lon,w,initial,opts){if(test.defer)await new Promise(r=>test.resolve=r);if(test.ensureFail){mode='LOADING';return false;}world=w;v046Publish(w);state.player.zone=w.id;state.player.pos=opts.spawn.slice();state.player.yaw=opts.yaw;state.player.pitch=0;test.autoResults.push(saveGame(false));mode='PLAYING';return true;}
 function loadZone(id,opts={}){if(V015_GEO_MACROS[id])return v046Ensure(43.3,5.4,exterior(),true,opts);world=buildWorld(id);state.player.zone=id;state.player.pos=(opts.spawn||world.spawn).slice();state.player.yaw=opts.yaw??world.spawnYaw;state.player.pitch=0;test.autoResults.push(saveGame(false));mode='PLAYING';return true;}
 `;
 vm.runInContext(harness,c);vm.runInContext(source,c,{filename:'08_city_interiors.js'});vm.runInContext('v050CityInteriorAfterInit();globalThis.d=window.__MISTRAL_DEBUG;const portal=d.v050CityInteriorInfo().doors[0].pos;state.player.pos=[portal[0],1.65,portal[2]]',c);
 return{run:s=>vm.runInContext(s,c),json:s=>JSON.parse(JSON.stringify(vm.runInContext(s,c)))};
}