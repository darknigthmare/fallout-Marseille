/* v0.18 — validated imports and streaming lifecycle. A source plan is NOT a downloaded map. */
V017PbfReader.prototype.skip=function(wire){
  if(wire===0){this.varint();return;}
  let len;if(wire===1)len=8;else if(wire===2)len=this.varint();else if(wire===5)len=4;else throw new Error('Type protobuf non pris en charge');
  if(!Number.isSafeInteger(len)||len<0||this.pos+len>this.end)throw new Error('Champ protobuf tronqué');this.pos+=len;
};
V017PbfReader.prototype.varId=function(){let n=0n,s=0n;for(let i=0;i<10;i++){if(this.pos>=this.end)throw new Error('Identifiant tronqué');const b=this.buf[this.pos++];n|=BigInt(b&127)<<s;if(!(b&128))return n<=BigInt(Number.MAX_SAFE_INTEGER)?Number(n):n.toString();s+=7n;}throw new Error('Identifiant trop long');};
v017ParseFeature=function(bytes){const r=new V017PbfReader(bytes),f={id:0,tags:[],type:0,geometry:[]};while(r.pos<r.end){const tag=r.varint(),n=tag>>3,w=tag&7;if(n===1&&w===0)f.id=r.varId();else if(n===2&&w===2)f.tags=v017PackedVarints(r.bytes());else if(n===3&&w===0)f.type=r.varint();else if(n===4&&w===2)f.geometry=v017PackedVarints(r.bytes());else r.skip(w);}return f;};
const v018OldDecode=v017DecodeMVT;
v017DecodeMVT=function(input){
  const data=input instanceof Uint8Array?input:new Uint8Array(input);if(data.length>32*1024*1024)throw new Error('Tuile anormalement volumineuse');
  if(!data.length)return{}; // A zero-feature ocean tile is valid.
  const prefix=new TextDecoder().decode(data.slice(0,120)).trim().toLowerCase();if(prefix.startsWith('<')||prefix.startsWith('{'))throw new Error('Réponse HTML/JSON reçue au lieu de MVT');
  const layers=v018OldDecode(data);
  for(const l of Object.values(layers)){if(!(l.extent>0&&l.extent<=65536))throw new Error('Étendue MVT invalide');for(const f of l.features){if(![1,2,3].includes(f.type))throw new Error('Type de géométrie MVT invalide');if(f.tags.length%2)throw new Error('Attributs MVT incomplets');}}
  return layers;
};
v017DecodeGeometry=function(f){
  let x=0,y=0,i=0,path=[],out=[];const g=f.geometry||[],zz=n=>n%2?-(Math.floor(n/2)+1):Math.floor(n/2);
  while(i<g.length){const command=g[i++],cmd=command&7,count=Math.floor(command/8);if(!count||count>1000000)throw new Error('Commande MVT invalide');
    if(cmd===1||cmd===2){if(i+count*2>g.length)throw new Error('Coordonnées MVT tronquées');if(cmd===2&&!path.length)throw new Error('LineTo sans MoveTo');
      for(let k=0;k<count;k++){x+=zz(g[i++]);y+=zz(g[i++]);if(!Number.isFinite(x)||!Number.isFinite(y))throw new Error('Coordonnée MVT invalide');
        if(cmd===1){if(path.length)out.push(path);path=[];}if(f.type===1)out.push([[x,y]]);else path.push([x,y]);}}
    else if(cmd===7){if(count!==1||!path.length)throw new Error('ClosePath invalide');if(path[0][0]!==path.at(-1)[0]||path[0][1]!==path.at(-1)[1])path.push([...path[0]]);out.push(path);path=[];}
    else throw new Error('Commande géométrique MVT inconnue');
  }
  if(path.length)out.push(path);return out;
};
function v018Stats(source){return{source,sourceRoads:0,renderedRoads:0,sourcePolygons:0,renderedPolygons:0,sourceBuildings:0,renderedBuildings:0,danglingRoadEnds:0,duplicates:0,assumedHeights:0};}
function v018Fingerprint(source,layer,f,rings){
  // Cyclic ring order is normalised; clipped fragments remain distinct.
  const shape=rings.map(r=>{let a=r.slice(0,-1).map(p=>`${p[0].toFixed(2)},${p[1].toFixed(2)}`),min=0;for(let i=1;i<a.length;i++)if(a[i]<a[min])min=i;return a.slice(min).concat(a.slice(0,min)).join(';');}).join('|');
  return`${source}:${layer}:${f.id||''}:${shape}`;
}
function v018Register(w,key,fingerprint,create){
  w.v018Entities??=new Map();const old=w.v018Entities.get(fingerprint);if(old){old.owners.add(key);return false;}
  const drawStart=w.staticDraws.length,colliderStart=w.colliders.length;create();
  const owners=new Set([key]),entry={owners,draws:w.staticDraws.slice(drawStart),colliders:w.colliders.slice(colliderStart)};
  for(const d of[...entry.draws,...entry.colliders]){d.geoOwners=owners;d.sourceFingerprint=fingerprint;}
  w.v018Entities.set(fingerprint,entry);return true;
}
function v018FinishTile(w,key,stats,z,x,y){
  w.geoTiles.add(key);w.geoTileStats[key]=stats;w.v018TileCoords??={};w.v018TileCoords[key]={z,x,y};V017_RUNTIME.loaded.set(key,stats);V017_RUNTIME.errors.delete(key);
  const source=stats.source;V017_RUNTIME.source=source;V017_RUNTIME.status=source==='fixture'?'TEST SYNTHÉTIQUE — PAS LA CARTE RÉELLE':source==='pack'?'DONNÉES DU PACK LOCAL':source==='cache'?'DONNÉES DU CACHE LOCAL':'DONNÉES VECTORIELLES DISTANTES';v017RecountAudit(w);return true;
}
function v018Ground(w,x,z){return w.geoTerrain?v017TerrainHeight(w,x,z):0;}
function v018AddRoad(w,path,props,color,key,layerName){
  if(path.length<2)return null;
  const cls=v017ClassRoad(props),explicit=parseFloat(props.width),lanes=parseFloat(props.lanes),isWater=layerName==='waterway';
  let width=Number.isFinite(explicit)&&explicit>0?explicit:Number.isFinite(lanes)&&lanes>0?lanes*3.1:cls.kind==='trail'?1.6:cls.kind==='rail'?1.435:cls.kind==='arterial'?10:5.5;
  if(isWater)width=Number.isFinite(explicit)?explicit:3;
  width=clamp(width,.4,70);const points=[];
  for(let i=0;i<path.length-1;i++){const a=path[i],b=path[i+1],len=Math.hypot(b[0]-a[0],b[1]-a[1]),steps=Math.max(1,Math.ceil(len/12));for(let k=0;k<steps;k++)points.push([lerp(a[0],b[0],k/steps),lerp(a[1],b[1],k/steps)]);}points.push(path.at(-1));
  const verts=[],faces=[],deckLayer=Number(props.layer)||0,bridge=String(props.brunnel||'').includes('bridge')||props.bridge==='yes',offset=bridge?Math.max(4,deckLayer*4):String(props.brunnel||'').includes('tunnel')?-Math.max(4,Math.abs(deckLayer)*4):0;
  for(let i=0;i<points.length;i++){
    const a=points[Math.max(0,i-1)],p=points[i],b=points[Math.min(points.length-1,i+1)];let dx=b[0]-a[0],dz=b[1]-a[1],l=Math.hypot(dx,dz)||1,nx=-dz/l,nz=dx/l;
    for(const s of[-1,1]){const x=p[0]+nx*width*.5*s,z=p[1]+nz*width*.5*s;verts.push([x,v018Ground(w,x,z)+(isWater?.025:.085)+offset,z]);}
    if(i){const j=i*2;faces.push([j-2,j-1,j],[j-1,j+1,j]);}
  }
  const b=v017PolyBounds([points]);const d={mesh:'geoSurface',pos:[b.cx,0,b.cz],vertices:verts,faces,color:isWater?COLORS.water:color,scale:[1,1,1],geoTile:key,alpha:1,roadPath:path.map(p=>[...p]),roadProperties:{...props},widthAssumed:!Number.isFinite(explicit),elevationAssumed:bridge||offset!==0,geoLayer:layerName,revision:0};w.staticDraws.push(d);return d;
}
/* Retain every imported footprint inside an active tile. Distance is a render
   decision, not a destructive import filter. Courtyards are grouped as holes. */
v017ApplyCadastreTile=function(w,key,layers,z,x,y,source='live'){
  if(!w?.geoMacro||w.geoTiles?.has(key))return false;w.geoTiles??=new Set();w.geoTileStats??={};const stats=v018Stats(source),layer=layers.batiments||layers.building||Object.values(layers).find(l=>/bat/i.test(l.name));
  if(layer)for(const f of layer.features){if(f.type!==3)continue;const groups=v018PolygonGroups(v017FeatureWorldPaths(layer,f,z,x,y,w.id));
    for(const rings of groups){stats.sourceBuildings++;const b=v017PolyBounds(rings),h=v017HeightFromFeature(f,rings[0],w.geo.kind),p=f.props||{},assumed=v018HeightInfo(f).estimated,base=v018Ground(w,b.cx,b.cz),hash=detailHash(String(f.id));
      const added=v018Register(w,key,v018Fingerprint('cadastre',layer.name,f,rings),()=>{
        const d=V017_PRISM_BASE(w,rings,base,h,cMix(COLORS.plaster,COLORS.limestone,(hash%100)/140),{geoTile:key,lod:'footprint',id:`cad-${f.id}`,roofColor:COLORS.roof});
        d.geoFeatureId=String(f.id);d.heightAssumed=assumed;d.geoLayer='building';d.geoSource='cadastre';d.geoProperties={...p};
        v017AddPolyCollider(w,rings[0],base,base+h,{rings,geoTile:key,id:`cad-${f.id}`});
      });
      if(added){stats.renderedBuildings++;if(assumed)stats.assumedHeights++;}else stats.duplicates++;
    }
  }
  v018FinishTile(w,key,stats,z,x,y);v018RefreshBaseBuildings(w);return true;
};
v017ApplyFranceTile=function(w,key,layers,z,x,y,source='live'){
  if(!w?.geoMacro||w.geoTiles?.has(key))return false;w.geoTiles??=new Set();w.geoTileStats??={};const stats=v018Stats(source);
  for(const lname of['landcover','landuse','park','water','waterway','transportation','building']){const layer=layers[lname];if(!layer)continue;
    for(const f of layer.features){const paths=v017FeatureWorldPaths(layer,f,z,x,y,w.id);if(!paths.length)continue;
      if((lname==='transportation'||lname==='waterway')&&f.type===2){for(const path of paths){if(path.length<2)continue;stats.sourceRoads++;const cls=v017ClassRoad(f.props||{});const d=v018AddRoad(w,path,f.props||{},cls.color,key,lname);if(d)stats.renderedRoads+=path.length-1;}continue;}
      if(f.type!==3)continue;
      for(const rings of v018PolygonGroups(paths)){
        if(lname==='building'){
          stats.sourceBuildings++;const b=v017PolyBounds(rings),h=v017HeightFromFeature(f,rings[0],w.geo.kind),p=f.props||{},added=v018Register(w,key,v018Fingerprint('base','building',f,rings),()=>{
            const d=V017_PRISM_BASE(w,rings,v018Ground(w,b.cx,b.cz),h,cMix(COLORS.plaster,COLORS.concrete,.2),{geoTile:key,id:`base-${f.id}`});d.geoSource='base';d.geoLayer='building';d.geoFeatureId=String(f.id);d.heightAssumed=v018HeightInfo(f).estimated;
            v017AddPolyCollider(w,rings[0],d.baseY,d.baseY+h,{rings,geoTile:key,id:`base-${f.id}`});
          });if(added)stats.renderedBuildings++;else stats.duplicates++;
        }else{
          stats.sourcePolygons++;const added=v018Register(w,key,v018Fingerprint('base',lname,f,rings),()=>{
            const d=V017_FLATPOLY_BASE(w,rings,lname==='water'?.025:.012,v017PolygonColor(lname,f.props||{}),{geoTile:key,alpha:1,id:`${lname}-${f.id}`});d.geoLayer=lname;d.geoProperties={...(f.props||{})};
            if(w.geoTerrain&&lname!=='water')v018DrapePolygon(w,d);
          });if(added)stats.renderedPolygons++;else stats.duplicates++;
        }
      }
    }
  }
  v018FinishTile(w,key,stats,z,x,y);v018RefreshBaseBuildings(w);return true;
};
function v018RefreshBaseBuildings(w){
  const cadastral=(w.staticDraws||[]).filter(d=>d.geoSource==='cadastre'&&d.rings);
  // A base-map building is suppressed only by an overlapping cadastral building,
  // never merely by the presence of a cadastre tile (which may be empty).
  for(const e of w.v018Entities?.values()||[])for(const d of e.draws)if(d.geoSource==='base'&&d.geoLayer==='building'){
    const hit=cadastral.some(c=>v018Contains(c.rings,d.pos[0],d.pos[2])||v018Contains(d.rings,c.pos[0],c.pos[2]));d.hidden=hit;for(const col of e.colliders)col.disabled=hit;
  }
}
function v018DrapePolygon(w,d){
  const triangles=v018Triangulate(d.rings),vertices=[],faces=[];for(const tri of triangles){const base=vertices.length;for(const p of tri)vertices.push([p[0],v018Ground(w,p[0],p[1])+.035,p[1]]);faces.push([base,base+2,base+1]);}
  d.originalRings=d.rings;d.mesh='geoSurface';d.vertices=vertices;d.faces=faces;d.revision=(d.revision||0)+1;
}
v017RecountAudit=function(w){
  const a={sourceBuildings:0,renderedBuildings:0,sourceRoads:0,renderedRoads:0,sourcePolygons:0,renderedPolygons:0,danglingRoadEnds:0,tilesBase:0,tilesCadastre:0,tilesFailed:V017_RUNTIME.errors.size,proceduralRoads:0,proceduralBuildings:0,duplicates:0,assumedHeights:0};
  for(const[k,s]of Object.entries(w.geoTileStats||{})){for(const p of['sourceBuildings','sourceRoads','renderedRoads','sourcePolygons','renderedPolygons','duplicates'])a[p]+=s[p]||0;if(k.startsWith('base:'))a.tilesBase++;else if(k.startsWith('cadastre:'))a.tilesCadastre++;}
  a.renderedBuildings=w.staticDraws.filter(d=>d.mesh==='prism'&&d.geoLayer==='building'&&!d.hidden).length;a.assumedHeights=w.staticDraws.filter(d=>d.heightAssumed&&!d.hidden).length;
  a.loadedFootprintFragments=w.staticDraws.filter(d=>d.geoLayer==='building').length;a.courtyardHoles=w.staticDraws.filter(d=>d.geoLayer==='building'&&!d.hidden).reduce((s,d)=>s+Math.max(0,(d.rings?.length||1)-1),0);
  V017_RUNTIME.audit=a;return a;
};
v017PruneTiles=function(w){
  const caps={base:18,cadastre:50},[lat,lon]=v015GeoUnproject(w.id,...[state.player.pos[0],state.player.pos[2]]);
  for(const source of['base','cadastre']){const keys=[...(w.geoTiles||[])].filter(k=>k.startsWith(source+':'));if(keys.length<=caps[source])continue;
    const t=v017LonLatToTile(lat,lon,V017_TILE_SOURCES[source].zoom),sorted=keys.map(k=>{const c=w.v018TileCoords?.[k];return{k,d:c?Math.hypot(c.x+.5-t.x,c.y+.5-t.y):Infinity};}).sort((a,b)=>b.d-a.d);
    for(const{k}of sorted.slice(0,keys.length-caps[source])){
      for(const[f,e]of w.v018Entities||[]){e.owners.delete(k);if(!e.owners.size){w.staticDraws=w.staticDraws.filter(d=>!e.draws.includes(d));w.colliders=w.colliders.filter(c=>!e.colliders.includes(c));w.v018Entities.delete(f);}}
      w.staticDraws=w.staticDraws.filter(d=>d.geoOwners?d.geoOwners.size>0:d.geoTile!==k);w.colliders=w.colliders.filter(c=>c.geoOwners?c.geoOwners.size>0:c.geoTile!==k);w.geoTiles.delete(k);delete w.geoTileStats[k];delete w.v018TileCoords?.[k];V017_RUNTIME.loaded.delete(k);
    }
  }
  v018RefreshBaseBuildings(w);v017RecountAudit(w);
};

/* Absolute datum and geodetic bounds: no per-region subtraction of the minimum.
   Unavailable DEM cells remain missing instead of becoming an invented sea level. */
function v018SetTerrain(w,j){
  if(!w?.geoMacro||!Number.isInteger(j.width)||!Number.isInteger(j.height)||j.width<2||j.height<2||j.width*j.height>4000000||!Array.isArray(j.values)||j.values.length!==j.width*j.height)throw new Error('Dimensions MNT invalides');
  if(!Array.isArray(j.bbox)||j.bbox.length!==4||!j.bbox.every(Number.isFinite)||j.bbox[0]>=j.bbox[2]||j.bbox[1]>=j.bbox[3]||Math.abs(j.bbox[0])>90||Math.abs(j.bbox[2])>90||Math.abs(j.bbox[1])>180||Math.abs(j.bbox[3])>180)throw new Error('Emprise MNT absente');
  const invalid=j.values.filter(v=>v===null||!Number.isFinite(v)).length;if(invalid)throw new Error(`MNT incomplet : ${invalid} cellules absentes`);
  if(j.values.some(v=>v< -12000||v>9000))throw new Error('Altitude aberrante ou valeur NoData');
  w.geoTerrain={width:j.width,height:j.height,heights:[...j.values],bbox:[...j.bbox],min:Math.min(...j.values.slice(0,50000)),max:Math.max(...j.values.slice(0,50000)),absoluteMin:0,source:j.source||'MNT importé — provenance non fournie'};
  w.geoTerrain.min=j.values.reduce((a,b)=>Math.min(a,b),Infinity);w.geoTerrain.max=j.values.reduce((a,b)=>Math.max(a,b),-Infinity);
  w.staticDraws=w.staticDraws.filter(d=>d.id!==`geo-ground-${w.id}`&&d.id!==`terrain-${w.id}`);v017AddTerrainMesh(w,w.geoTerrain);
  for(const d of w.staticDraws){if(d.mesh==='prism'&&d.geoTile){d.baseY=v018Ground(w,d.pos[0],d.pos[2]);d.pos[1]=d.baseY+d.height/2;d.revision=(d.revision||0)+1;}else if(d.roadPath){const props=d.roadProperties,ix=w.staticDraws.indexOf(d);const replacement=v018AddRoad(w,d.roadPath,props,d.color,d.geoTile,d.geoLayer);w.staticDraws.pop();w.staticDraws[ix]=replacement;}else if(d.mesh==='flatpoly'&&d.geoLayer&&d.geoLayer!=='water')v018DrapePolygon(w,d);}
  for(const c of w.colliders)if(c.poly&&c.geoTile){const h=c.maxY-c.minY,b=v017PolyBounds(c.rings||[c.poly]);c.minY=v018Ground(w,b.cx,b.cz);c.maxY=c.minY+h;}
  v017GroundExistingContent(w);w.geoTerrainStatus=`MNT · ${Math.round(w.geoTerrain.min)}–${Math.round(w.geoTerrain.max)} m · ${w.geoTerrain.source}`;return true;
}
v017TerrainHeight=function(w,x,z){
  const t=w?.geoTerrain;if(!t)return 0;let u,v;
  if(t.bbox){const[lat,lon]=v015GeoUnproject(w.id,x,z),[s,west,n,e]=t.bbox;u=clamp((lon-west)/(e-west),0,1);v=clamp((n-lat)/(n-s),0,1);}else{const[a,b,c,d]=w.bounds;u=clamp((x-a)/(b-a),0,1);v=clamp((z-c)/(d-c),0,1);}
  const gx=u*(t.width-1),gy=v*(t.height-1),ix=Math.floor(gx),iy=Math.floor(gy),jx=Math.min(ix+1,t.width-1),jy=Math.min(iy+1,t.height-1),at=(i,j)=>t.heights[j*t.width+i];
  return lerp(lerp(at(ix,iy),at(jx,iy),gx-ix),lerp(at(ix,jy),at(jx,jy),gx-ix),gy-iy);
};
v017LoadTerrain=async function(w){
  if(!w?.geoMacro)return false;const epoch=V018.geoEpoch;
  if(location.protocol==='file:'){w.geoTerrainStatus='MNT absent du monofichier';return false;}
  try{const r=await fetch(`data/map_pack/terrain/${w.id}.json`);if(!r.ok)throw new Error(`HTTP ${r.status}`);const j=await r.json();if(epoch!==V018.geoEpoch||w!==world)return false;return v018SetTerrain(w,j);}catch(e){if(w===world)w.geoTerrainStatus=`MNT non chargé · ${String(e.message).slice(0,100)}`;return false;}
};

const V018_RETRY=new Map();
v017FetchWithTimeout=async function(url,ms=12000){const ctrl=new AbortController();V018.controllers.add(ctrl);const timer=setTimeout(()=>ctrl.abort(),ms);try{const r=await fetch(url,{signal:ctrl.signal,mode:'cors',cache:'default'});if(!r.ok)throw new Error(`HTTP ${r.status}`);const b=await r.arrayBuffer();v017DecodeMVT(b);return b;}finally{clearTimeout(timer);V018.controllers.delete(ctrl);}};
v017GetTileBuffer=async function(source,z,x,y){
  const def=V017_TILE_SOURCES[source],key=v017TileKey(source,z,x,y);
  if(location.protocol!=='file:')try{return{buffer:await v017FetchWithTimeout(v017TileURL(def.local,z,x,y),3000),source:'pack'};}catch(e){if(e.name==='AbortError')throw e;}
  if(settings.geoCache!==false){const cached=await v017CacheGet(key);if(cached){try{v017DecodeMVT(cached);return{buffer:cached,source:'cache'};}catch{await v018CacheDelete(key);}}}
  if(settings.geoStreaming===false)throw new Error('Aucune donnée locale — réseau désactivé');
  return{buffer:await v017FetchWithTimeout(v017TileURL(def.url,z,x,y),12000),source:'live'};
};
async function v018CacheDelete(key){const db=await v017OpenDB();if(!db)return;return new Promise(resolve=>{const t=db.transaction('tiles','readwrite');t.objectStore('tiles').delete(key);t.oncomplete=t.onerror=t.onabort=()=>resolve();});}
v017CachePut=async function(key,buffer){try{const db=await v017OpenDB();if(!db)return false;return await new Promise(resolve=>{const tx=db.transaction('tiles','readwrite');tx.objectStore('tiles').put(buffer,key);tx.oncomplete=()=>resolve(true);tx.onabort=tx.onerror=()=>resolve(false);});}catch{return false;}};
v017QueueTile=function(w,source,z,x,y,priority=0){
  const key=v017TileKey(source,z,x,y),retry=V018_RETRY.get(key);if(retry&&performance.now()<retry.at)return;
  if(w.geoTiles?.has(key)||V017_RUNTIME.pending.has(key)||V017_RUNTIME.queue.some(j=>j.key===key))return;
  V017_RUNTIME.queue.push({w,source,z,x,y,key,priority,epoch:V018.geoEpoch});V017_RUNTIME.queue.sort((a,b)=>a.priority-b.priority);v017PumpQueue();
};
v017PumpQueue=function(){
  while(V017_RUNTIME.active<2&&V017_RUNTIME.queue.length){const j=V017_RUNTIME.queue.shift();if(j.w!==world||j.epoch!==V018.geoEpoch)continue;
    V017_RUNTIME.active++;const token={epoch:j.epoch};V017_RUNTIME.pending.set(j.key,token);
    (async()=>{try{const got=await v017GetTileBuffer(j.source,j.z,j.x,j.y),layers=v017DecodeMVT(got.buffer);if(j.epoch!==V018.geoEpoch||j.w!==world)return;
      (j.source==='base'?v017ApplyFranceTile:v017ApplyCadastreTile)(j.w,j.key,layers,j.z,j.x,j.y,got.source);V018_RETRY.delete(j.key);
      if(settings.geoCache!==false&&got.source!=='cache')await v017CachePut(j.key,got.buffer);
    }catch(e){if(j.epoch!==V018.geoEpoch)return;const failures=(V018_RETRY.get(j.key)?.failures||0)+1;V018_RETRY.set(j.key,{failures,at:performance.now()+Math.min(300000,5000*2**(failures-1))});V017_RUNTIME.errors.set(j.key,String(e));V017_RUNTIME.lastError=String(e);if(!V017_RUNTIME.fixtureMode)V017_RUNTIME.status='CARTOGRAPHIE NON DISPONIBLE — AUCUNE VILLE INVENTÉE';}
    finally{if(V017_RUNTIME.pending.get(j.key)===token)V017_RUNTIME.pending.delete(j.key);V017_RUNTIME.active=Math.max(0,V017_RUNTIME.active-1);v017PumpQueue();}})();
  }
};
const v018OldLoad=loadZone;
loadZone=function(id,opts={}){
  V018.geoEpoch++;for(const c of V018.controllers)c.abort();V018.controllers.clear();V017_RUNTIME.queue.length=0;V017_RUNTIME.loaded.clear();V017_RUNTIME.errors.clear();V017_RUNTIME.fixtureMode=false;
  if(state.v018?.travelMode==='story'&&ALL_ZONE_IDS.includes(id)&&!V015_GEO_MACROS[id])opts={...opts,legacyDirect:true,instance:true};
  return v018OldLoad(id,opts);
};
v015MacroBounds=function(id){const[s,w,n,e]=V015_GEO_MACROS[id].bbox,p=[[s,w],[s,e],[n,w],[n,e]].map(a=>v015GeoProject(id,...a));return[Math.min(...p.map(a=>a[0])),Math.max(...p.map(a=>a[0])),Math.min(...p.map(a=>a[2])),Math.max(...p.map(a=>a[2]))];};
/* Re-importing a terrain must not add its altitude a second time to inhabitants. */
v017GroundExistingContent=function(w){
  const place=p=>{if(!p?.pos)return;const previous=p.v018AppliedHeight||0,h=v017TerrainHeight(w,p.pos[0],p.pos[2]);p.pos[1]+=h-previous;p.v018AppliedHeight=h;};
  for(const d of w.staticDraws)if(d.mesh!=='terrain'&&d.id!==`geo-ground-${w.id}`&&!d.geoTile)place(d);
  for(const it of w.interactables)place(it);
  for(const n of w.npcs){place(n);if(n.home)n.home[1]=v017TerrainHeight(w,n.home[0],n.home[2]);if(n.route)for(const p of n.route)p[1]=v017TerrainHeight(w,p[0],p[2]);}
  for(const l of w.loot)place(l);for(const s of w.subzones)s.pos[1]=v017TerrainHeight(w,s.pos[0],s.pos[2]);
  if(w===world)state.player.pos[1]=v017TerrainHeight(w,state.player.pos[0],state.player.pos[2])+playerEyeHeight();
};
