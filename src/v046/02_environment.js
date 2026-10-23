/* One decoration identity per global metre cell, admitted only by source land
   coverage. Roads/buildings never come from random population in real mode. */
function v046Blocked(w,x,z){for(const c of w.colliders)if(!c.v042Site&&!c.disabled&&v017ColliderHit(c,x,z,2))return true;for(const r of w.v046Records?.values()||[])for(const road of r.roads)if(road.geoLayer==='transportation'){const p=road.roadPath;for(let i=1;i<p.length;i++)if(v017PointSegDist(x,z,p[i-1],p[i])<(road.widthAssumed?7:5))return true;}return false;}
function v046Nature(w,plan){w.staticDraws=w.staticDraws.filter(d=>!d.v046Nature);const size=64,n=6,gx=Math.floor((plan.p[0]+V046_ORIGIN[0])/size),gy=Math.floor((V046_ORIGIN[1]-plan.p[2])/size),out=[],ids=[];for(let dx=-n;dx<=n;dx++)for(let dy=-n;dy<=n;dy++){const xcell=gx+dx,ycell=gy+dy,key=`nature:${xcell}:${ycell}`,rng=detailRng(key),x=(xcell+.18+rng()*.64)*size-V046_ORIGIN[0],z=V046_ORIGIN[1]-(ycell+.18+rng()*.64)*size,scale=.65+rng()*.7;const s=v046SurfaceAt([x,0,z],w.v046Records),h=v046HeightAt(x,z);if(s.water||h.height===null||v046Blocked(w,x,z))continue;
 const tmp={staticDraws:[],colliders:[],ambient:[]};if(s.forest)addTree(tmp,x,z,scale,'pine');else if(s.urban){addTrashPileProp(tmp,x,0,z,rng()*TAU,scale,rng);}else continue;
 for(const d of tmp.staticDraws){d.pos[1]+=Math.max(0,h.height);d.v046Nature=key;d.v046GeometryId=key+':'+out.length;out.push(d);}ids.push(key);}
 w.staticDraws.push(...out);w.v046NatureIds=ids;
}
/* Site visibility does not depend on the macro label. Placements are resolved
   against validated source geometry once, recorded, and reused on return. */
const v046WorldPointOld=v042WorldPoint;
v042WorldPoint=function(w,site){if(!w?.v046)return v046WorldPointOld(w,site);const old=state.v046.placements[site.id];if(old)return old.slice();const p=v015GeoProject(w.id,site.lat,site.lon);const candidates=[[0,0]];for(let r=14;r<=98;r+=14)for(let i=0;i<12;i++)candidates.push([Math.cos(i/12*TAU)*r,Math.sin(i/12*TAU)*r]);for(const[dx,dz]of candidates){const x=p[0]+dx,z=p[2]+dz,h=v046HeightAt(x,z);if(h.height===null||v046SurfaceAt([x,0,z],w.v046Records).water||v046Blocked(w,x,z))continue;const pos=[x,Math.max(0,h.height),z];state.v046.placements[site.id]=pos;return pos.slice();}return null;};
const v046SpawnOld=v042SpawnSite;v042SpawnSite=function(w,site){if(!w?.v046)return v046SpawnOld(w,site);if(!v042WorldPoint(w,site))return null;return v046SpawnOld(w,site);};
const v046LayerOld=v042UpdateLayer;v042UpdateLayer=function(dt){if(!world?.v046)return v046LayerOld(dt);if(V046.busy||!settings.geoFalloutLayer)return;V042_RUNTIME.clock+=dt;if(V042_RUNTIME.clock<.7)return;V042_RUNTIME.clock=0;V042_RUNTIME.worldId=world.id;
 const rows=V042_CATALOG.map(site=>{const p=v015GeoProject(world.id,site.lat,site.lon);return{site,p,d:Math.hypot(p[0]-state.player.pos[0],p[2]-state.player.pos[2])};}).sort((a,b)=>a.d-b.d||a.site.id.localeCompare(b.site.id));V042_RUNTIME.nearest=rows[0];const allowed=rows.filter(r=>r.d<Math.min(480,r.site.activationRadius));const keep=new Set(allowed.slice(0,settings.geoContentBudget).map(r=>r.site.id));for(const[id,rec]of V042_RUNTIME.active){if(rec.enemies.some(e=>e.alive&&e.alerted))keep.add(id);}
 for(const id of[...V042_RUNTIME.active.keys()])if(!keep.has(id))v042UnloadSite(id);for(const r of allowed){if(r.d<r.site.discoverRadius&&!V046.lab)v042Discover(r.site);if(keep.has(r.site.id)&&!V042_RUNTIME.active.has(r.site.id))v042SpawnSite(world,r.site);}for(const rec of V042_RUNTIME.active.values())v042CheckSite(rec);
};
/* Source coverage is always retained beyond the visible distance. Cull custom
   geometry by its extents, never just the centre of a large road/forest. */
/* Native-resolution terrain can contain more vertices than JavaScript permits
   function arguments. Visit coordinates directly; never spread a mesh into
   Math.min/max or allocate a second full array just to calculate its bounds. */
function v046DrawBounds(draw){
 let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
 function point(p,zIndex){
  const x=p?.[0],z=p?.[zIndex];if(!Number.isFinite(x)||!Number.isFinite(z))return;
  if(x<minX)minX=x;if(x>maxX)maxX=x;if(z<minZ)minZ=z;if(z>maxZ)maxZ=z;
 }
 if(draw.vertices){for(const p of draw.vertices)point(p,2);}
 else if(draw.rings){for(const ring of draw.rings)for(const p of ring)point(p,1);}
 else if(draw.roadPath){for(const p of draw.roadPath)point(p,1);}
 if(minX!==Infinity)return{minX,maxX,minZ,maxZ};
 const x=Number.isFinite(draw.pos?.[0])?draw.pos[0]:0,z=Number.isFinite(draw.pos?.[2])?draw.pos[2]:0;
 return{minX:x-10,maxX:x+10,minZ:z-10,maxZ:z+10};
}
const v046CollectOld=collectDraws;collectDraws=function(t){const ds=v046CollectOld(t);if(!world?.v046)return ds;const[x,,z]=state.player.pos;return ds.filter(d=>{if(!d.v046Tile&&!d.v046Nature&&!d.v046Terrain)return true;const b=d.v046Bounds||(d.v046Bounds=v046DrawBounds(d));return Math.hypot(x-Math.max(b.minX,Math.min(b.maxX,x)),z-Math.max(b.minZ,Math.min(b.maxZ,z)))<720;});};
