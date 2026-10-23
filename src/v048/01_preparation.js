/* v0.48 builds the same immutable geometry as v0.47, with cooperative checkpoints
   inside tile imports, spatial indexing, terrain rows and vegetation cells. */
const V048={version:'0.48.0',job:null,lastJob:null,jobs:[],serial:0,
  returns:{kept:0,reused:0,missed:0,discarded:0,last:null},retained:null,returnLimit:48*1024*1024,
  test:{pausePhase:null,pauseMs:0},legacyPrepare:v046Prepare};
function v048Phase(job, phase, done=0, total=1) {
  MistralWork.check(job.work.signal); job.work.phase=phase;job.done=done;job.total=Math.max(1,total);
  if(V048.job===job) v048RefreshWork?.();
}
async function v048Step(job, phase, total) {
  v048Phase(job,phase,0,total); await job.work.checkpoint(0,true);
  if(V048.test.pausePhase===phase&&V048.test.pauseMs>0) {
    const until=performance.now()+Math.min(2000,V048.test.pauseMs);
    while(performance.now()<until) await job.work.checkpoint(0,true);
  }
}
async function v048Import(w, resource, key, work) {
  const out={key,draws:[],colliders:[],land:[],water:[],buildings:[],roads:[],estimatedHeights:0,missingGroundBuildings:0,empty:resource.empty,source:resource.origin};
  const names=resource.source==='cadastre'?['batiments','building']:['water','landcover','landuse','park','waterway','transportation'];
  for(const name of names) {
    const layer=resource.layers[name];if(!layer)continue;
    for(let offset=0;offset<layer.features.length;offset+=8) {
      MistralWork.check(work.signal);
      const tmp=v046World(w.id);tmp.v047TerrainBank=w.v047TerrainBank;
      const batch={...resource,layers:{[name]:{...layer,features:layer.features.slice(offset,offset+8)}}};
      const r=v046Import(tmp,batch,key);
      for(const field of ['draws','colliders','land','water','buildings','roads'])out[field].push(...r[field]);
      out.estimatedHeights+=r.estimatedHeights;out.missingGroundBuildings+=r.missingGroundBuildings||0;await work.checkpoint(8);
    }
  }
  return out;
}
async function v048Index(records, colliders, work) {
  const surface=new MistralStream.SpatialGrid(96),solids=new MistralStream.SpatialGrid(48),roads=new MistralStream.SpatialGrid(48);
  for(const r of records.values()) {
    for(const [type,list] of [['water',r.water],['land',r.land]])for(const d of list){surface.add(v017PolyBounds(d.rings),{type,draw:d});await work.checkpoint();}
    for(const d of r.roads) {
      if(d.geoLayer!=='transportation')continue;const ps=d.roadPath||[];
      for(let i=1;i<ps.length;i++){roads.add({minX:Math.min(ps[i-1][0],ps[i][0])-8,maxX:Math.max(ps[i-1][0],ps[i][0])+8,minZ:Math.min(ps[i-1][1],ps[i][1])-8,maxZ:Math.max(ps[i-1][1],ps[i][1])+8},{a:ps[i-1],b:ps[i],width:d.widthAssumed?7:5});await work.checkpoint();}
    }
  }
  for(const c of colliders)if(!c.v042Site&&!c.disabled){solids.add({minX:c.minX-2,maxX:c.maxX+2,minZ:c.minZ-2,maxZ:c.maxZ+2},c);await work.checkpoint();}
  return {surface,solids,roads};
}
async function v048Meshes(plan, bank, stamp, job) {
  const size=512,step=32,grid=16,radius=940,out=[];
  const xmin=Math.floor((plan.p[0]-radius)/size),xmax=Math.floor((plan.p[0]+radius)/size),zmin=Math.floor((plan.p[2]-radius)/size),zmax=Math.floor((plan.p[2]+radius)/size);
  const total=(xmax-xmin+1)*(zmax-zmin+1);await v048Step(job,'relief',total);let done=0;
  for(let cx=xmin;cx<=xmax;cx++)for(let cz=zmin;cz<=zmax;cz++) {
    const key='terrain:'+cx+':'+cz+':'+stamp;let d=V047.meshes.get(key);
    if(d){V047.stats.reusedTerrain++;out.push(d);v048Phase(job,'relief',++done,total);await job.work.checkpoint();continue;}
    const vertices=[],faces=[],valid=[];
    for(let j=0;j<=grid;j++) {
      for(let i=0;i<=grid;i++){const x=cx*size+i*step,z=cz*size+j*step,h=v047Height(bank,x,z);vertices.push([x,h.height===null?0:h.height-.06,z]);valid.push(h.height!==null);}
      await job.work.checkpoint(grid+1);
    }
    for(let j=0;j<grid;j++) {
      for(let i=0;i<grid;i++){const a=j*(grid+1)+i,b=a+1,c=a+grid+1,e=c+1;if(valid[a]&&valid[b]&&valid[c])faces.push([a,c,b]);if(valid[b]&&valid[c]&&valid[e])faces.push([b,c,e]);}
      await job.work.checkpoint(grid);
    }
    d={mesh:'terrain',vertices,faces,pos:[(cx+.5)*size,0,(cz+.5)*size],scale:[1,1,1],color:[.30,.33,.25],v046Terrain:true,v047GeometryId:key};
    MistralWork.check(job.work.signal);V047.meshes.set(key,d);V047.stats.builtTerrain++;out.push(d);v048Phase(job,'relief',++done,total);
  }
  return typeof v050RefineTerrainMeshes==='function'?await v050RefineTerrainMeshes(out,plan,bank,stamp,job):out;
}
async function v048Nature(w, plan, bank, job) {
  const out=[],ids=[],size=64,n=13,gx=Math.floor((plan.p[0]+V046_ORIGIN[0])/size),gy=Math.floor((V046_ORIGIN[1]-plan.p[2])/size);
  let done=0;const total=(n*2+1)**2;await v048Step(job,'nature',total);
  for(let dx=-n;dx<=n;dx++)for(let dy=-n;dy<=n;dy++) {
    const key=`nature:${gx+dx}:${gy+dy}`,rng=detailRng(key),x=(gx+dx+.18+rng()*.64)*size-V046_ORIGIN[0],z=V046_ORIGIN[1]-(gy+dy+.18+rng()*.64)*size,scale=.65+rng()*.7,s=v046SurfaceAt([x,0,z],w.v046Records),h=v047Height(bank,x,z);
    if(!s.water&&h.height!==null&&!v046Blocked(w,x,z)) {
      const tmp={staticDraws:[],colliders:[],ambient:[]};
      if(s.forest)addTree(tmp,x,z,scale,'pine');else if(s.urban)addTrashPileProp(tmp,x,0,z,rng()*TAU,scale,rng);
      if(s.forest||s.urban){let piece=0;for(const d of tmp.staticDraws){d.pos[1]+=Math.max(0,h.height);d.v046Nature=key;d.v046GeometryId=key+':'+piece++;out.push(d);}ids.push(key);}
    }
    if(++done%16===0||done===total)v048Phase(job,'nature',done,total);
    await job.work.checkpoint(4);
  }
  return {draws:out,ids};
}
v046Prepare=async function(plan, resources, w, signal) {
  const job={id:++V048.serial,work:new MistralWork.Budget({signal}),done:0,total:1,status:'preparing'};V048.job=job;
  try {
    await v048Step(job,'validation',plan.dem.length);
    const bank=new MistralIntegrity.TerrainBank(V046_BOUNDS);
    for(const[id,g]of V046.terrain.grids)bank.grids.set(id,g);
    let done=0;
    for(const key of plan.dem){const r=resources.get(key);if(!r)throw Error('Terrain absent : '+key);bank.add(r.raw,r.id);v048Phase(job,'validation',++done,plan.dem.length);await job.work.checkpoint();}
    if(V047.test.delayPrepare)await new Promise(r=>setTimeout(r,V047.test.delayPrepare));
    MistralWork.check(signal);if(V047.test.failPrepare)throw Error('Échec de préparation injecté — banque active intacte');
    const stamp=v047BankStamp(bank),records=new Map();await v048Step(job,'batiments',plan.keys.length);done=0;
    for(const key of plan.keys) {
      MistralWork.check(signal);const resource=resources.get(key);if(!resource)throw Error('Tuile absente : '+key);
      const revision=v047TileStamp(resource,stamp),cacheKey=key+':'+revision;let record=w?.v046Records?.get(key);
      if(record?.v047Revision!==revision)record=V047.records.get(cacheKey);
      if(record){V047.stats.reusedTiles++;}else{
        const tmp=v046World(w.id);tmp.v047TerrainBank=bank;
        record=await v048Import(tmp,resource,key,job.work);record.v047Revision=revision;
        MistralWork.check(signal);V047.records.set(cacheKey,record);V047.stats.builtTiles++;
      }
      records.set(key,record);v048Phase(job,'batiments',++done,plan.keys.length);await job.work.checkpoint(8);
    }
    await v048Step(job,'collisions',records.size);const draws=[],colliders=[],seen=new Set(),collisionIds=new Set();done=0;
    for(const r of records.values()) {
      for(const d of r.draws){if(!seen.has(d.v046GeometryId)){seen.add(d.v046GeometryId);draws.push(d);}await job.work.checkpoint();}
      for(const c of r.colliders){const id=MistralIntegrity.footprintKey('collision',c.rings||[c.polygon||[]],{height:c.maxY});if(!c.rings||!collisionIds.has(id)){if(c.rings)collisionIds.add(id);colliders.push(c);}await job.work.checkpoint();}
      v048Phase(job,'collisions',++done,records.size);
    }
    records.v047Index=await v048Index(records,colliders,job.work);
    const h=v047Height(bank,plan.p[0],plan.p[2]),s=v046SurfaceAt(plan.p,records);if(h.height===null&&!s.water)throw Error('Aucune altitude valide sous le joueur');
    const ground=await v048Meshes(plan,bank,stamp,job),land=typeof v050RefineLandSurfaces==='function'?await v050RefineLandSurfaces(ground,draws,job):{terrain:ground,draws},temp=v046World(w.id);temp.v047TerrainBank=bank;temp.v046Records=records;temp.colliders=colliders;
    const nature=await v048Nature(temp,plan,bank,job);await v048Step(job,'publication',1);MistralWork.check(signal);job.status='prepared';
    return {records,terrain:land.terrain,height:h.height===null?0:Math.max(0,h.height),bank,geoDraws:land.draws,geoColliders:colliders,nature,bankStamp:stamp};
  } catch(e) {job.status=signal?.aborted?'cancelled':'failed';throw e;}
  finally {const report={id:job.id,status:job.status,...job.work.snapshot()};if(!V048.lastJob||report.id>=V048.lastJob.id)V048.lastJob=report;V048.jobs.push(report);if(V048.jobs.length>20)V048.jobs.shift();if(V048.job===job)V048.job=null;}
};
