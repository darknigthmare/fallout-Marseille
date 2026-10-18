/* Reproducible synthetic boundary laboratory. Deliberately NOT called Marseille
   imagery, official DEM, or acquired map data. Isolated from campaign saving. */
const V046_LAB_LL=[43.29,5.43];
const V046_LAB={delay:0,fail:null,sequence:0};
function v046LabEncode(rings){let x=0,y=0,out=[];const zz=v=>(v<<1)^(v>>31);for(let raw of rings){const r=raw.slice();if(r.length>2&&r[0][0]===r.at(-1)[0]&&r[0][1]===r.at(-1)[1])r.pop();if(!r.length)continue;out.push(9,zz(r[0][0]-x),zz(r[0][1]-y));x=r[0][0];y=r[0][1];if(r.length>1){out.push(((r.length-1)<<3)|2);for(const p of r.slice(1)){out.push(zz(p[0]-x),zz(p[1]-y));x=p[0];y=p[1];}}if(r.length>2)out.push(15);}return out;}
function v046LabRecord(key){if(key.startsWith('dem:')){const id=key.slice(4),b=V046_BOUNDS[id],width=41,height=41,values=[];for(let y=0;y<height;y++)for(let x=0;x<width;x++){const lat=b[2]+(b[0]-b[2])*y/(height-1),lon=b[1]+(b[3]-b[1])*x/(width-1);values.push(48+(lat-V046_LAB_LL[0])*320+(lon-V046_LAB_LL[1])*80);}return{id,raw:{macro:id,bbox:b.slice(),width,height,values,qaFixture:true,sourceResource:'ign_rge_alti_wld',rowOrder:'north-to-south'},source:'BANC QA SYNTHÉTIQUE'};}
 const[src,sz,sx,sy]=key.split(':'),z=+sz,x=+sx,y=+sy,extent=65536,origin=v015GeoProject('geo_huveaune',...V046_LAB_LL),layers={};
 function point(p){const[lat,lon]=v015GeoUnproject('geo_huveaune',origin[0]+p[0],origin[2]+p[1]),t=v017LonLatToTile(lat,lon,z);return[Math.round((t.x-x)*extent),Math.round((t.y-y)*extent)];}
 function add(lname,id,rings,props,type=3,center=[0,0]){const ll=v015GeoUnproject('geo_huveaune',origin[0]+center[0],origin[2]+center[1]),t=v017LonLatToTile(...ll,z);if(Math.floor(t.x)!==x||Math.floor(t.y)!==y)return;layers[lname]??={name:lname,extent,features:[]};let geometry=v046LabEncode(rings.map(r=>r.map(point)));if(type===2&&geometry.at(-1)===15)geometry.pop();layers[lname].features.push({id,type,props,geometry});}
 function box(x,z,w,h){return[[x,z],[x+w,z],[x+w,z+h],[x,z+h],[x,z]];}
 if(src==='cadastre'){
  add('batiments',1001,[box(-60,-110,40,38)],{height:11,nature:'dur'},3,[-40,-91]);
  add('batiments',1002,[box(22,-95,58,52),box(35,-81,30,26).reverse()],{height:12,nature:'dur'},3,[51,-69]);
  add('batiments',1003,[box(-122,-80,28,25)],{height:7,nature:'dur'},3,[-108,-67]);
  add('batiments',1004,[box(98,-76,30,34)],{height:8,nature:'dur'},3,[113,-59]);
  add('batiments',1005,[[[-12,-145],[35,-145],[35,-131],[2,-131],[2,-111],[-12,-111],[-12,-145]]],{height:9,nature:'dur'},3,[5,-131]);
 }else{
  add('transportation',2001,[[[-1100,0],[1100,0]]],{class:'secondary',width:9},2,[0,0]);
  add('transportation',2002,[[[-86,150],[-86,-185],[110,-185]]],{class:'residential',width:5.5},2,[-86,-50]);
  add('landuse',3001,[box(-200,-205,400,190)],{class:'residential'},3,[0,-100]);
  add('landcover',3002,[box(-530,60,1060,600)],{class:'wood'},3,[0,290]);
  add('landcover',3003,[box(-460,-600,920,340)],{class:'wood'},3,[0,-410]);
 }
 return{source:src,z,x,y,layers,empty:!Object.keys(layers).length,origin:'BANC QA SYNTHÉTIQUE',buffer:new ArrayBuffer(0)};
}
async function v046LabProvider(key,signal){if(V046_LAB.delay)await new Promise((resolve,reject)=>{const t=setTimeout(resolve,V046_LAB.delay);signal.addEventListener('abort',()=>{clearTimeout(t);reject(new Error('Annulé'));},{once:true});});if(key===V046_LAB.fail||V046_LAB.fail==='all')throw new Error('Échec réseau injecté — '+key);return v046LabRecord(key);}
const v046SaveOld=saveGame;saveGame=function(...args){if(V046.lab)return false;return v046SaveOld(...args);};
async function v046StartLab(){if(!V046.labBackup){V046.labBackup=deepClone(state);V046.labSettings=deepClone(settings);}V046.gate.cancel();V046.gate.cache.clear();V046.terrain=new MistralIntegrity.TerrainBank(V046_BOUNDS);V046.lab=true;V046.labProvider=v046LabProvider;V046.busy=false;state=migrateState(baseState());state.v018.travelMode='story';settings.geoFalloutLayer=false;state.worldTime=13;state.playTime=0;gameStarted=true;mode='PLAYING';$('menuScreen').classList.remove('active');$('bootScreen').classList.remove('active');const w=v046World('geo_marseille'),p=v015GeoProject(w.id,...V046_LAB_LL),ll=v015GeoUnproject(w.id,p[0]-40,p[2]+38);const ok=await v046Ensure(ll[0],ll[1],w,true,{yaw:0});if(ok){state.player.pos=[p[0]-40,v017TerrainHeight(world,p[0]-40,p[2]+38)+1.65,p[2]+38];state.player.yaw=0;state.player.pitch=.025;}return ok;}
function v046Signature(){if(!world?.v046)return null;const[x,,z]=state.player.pos;return{scene:world.v046SceneId||(world.v046SceneId=++V046.serial),region:world.id,buildings:[...world.v046Records.values()].flatMap(r=>r.buildings).map(d=>({id:d.v046GeometryId,rings:d.rings,baseY:d.baseY,height:d.height})).sort((a,b)=>a.id.localeCompare(b.id)),roads:[...world.v046Records.values()].flatMap(r=>r.roads).map(d=>({id:d.v046GeometryId,vertices:d.vertices})).sort((a,b)=>a.id.localeCompare(b.id)),nature:world.staticDraws.filter(d=>d.v046Nature&&Math.hypot(d.pos[0]-x,d.pos[2]-z)<230).map(d=>({cell:d.v046Nature,mesh:d.mesh,pos:d.pos,scale:d.scale})).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)))};}
