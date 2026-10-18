/* v0.18 — Geometry corrections. Original implementation; no external runtime dependency.
   Tests exercise polygons with holes, clipping at the near plane, true metric scale,
   ground interpolation, GPU meshes, and collision/ray consistency. */
const V018_EPS = 1e-8;
const V018 = {geoEpoch:0, controllers:new Set(), lastWorld:null, render:{backend:'pending',customMeshes:0,triangles:0}, fieldReturn:null};

function v018Ring(raw){
  const ring=[];
  for(const p of raw||[]){
    if(!Array.isArray(p)||!Number.isFinite(p[0])||!Number.isFinite(p[1]))throw new Error('Coordonnée polygonale invalide');
    if(!ring.length||Math.hypot(p[0]-ring.at(-1)[0],p[1]-ring.at(-1)[1])>V018_EPS)ring.push([p[0],p[1]]);
  }
  if(ring.length>1&&Math.hypot(ring[0][0]-ring.at(-1)[0],ring[0][1]-ring.at(-1)[1])<V018_EPS)ring.pop();
  if(ring.length<3||Math.abs(v017SignedArea(ring))<V018_EPS)return null;
  ring.push([...ring[0]]);return ring;
}
function v018PolygonGroups(raw){
  const rings=raw.map(v018Ring).filter(Boolean);if(!rings.length)return [];
  const orientation=Math.sign(v017SignedArea(rings[0])),groups=[];
  for(const ring of rings){
    if(Math.sign(v017SignedArea(ring))===orientation){groups.push([ring]);continue;}
    let parent=groups.at(-1);
    if(!parent||!v017PointInPoly(ring[0][0],ring[0][1],parent[0])){
      parent=groups.find(g=>v017PointInPoly(ring[0][0],ring[0][1],g[0]));
    }
    if(parent)parent.push(ring);else groups.push([ring]);
  }
  return groups;
}
function v018Contains(rings,x,z){let inside=false;for(const ring of rings||[])if(v017PointInPoly(x,z,ring))inside=!inside;return inside;}
/* Scan-band tessellation: triangulates concave footprints and holes exactly by
   pairing boundary intersections inside each band. No bounding-box substitution. */
function v018Triangulate(rings){
  const edges=[],levels=new Set();
  for(const raw of rings){const ring=v018Ring(raw);if(!ring)continue;
    for(let i=0;i<ring.length-1;i++){const a=ring[i],b=ring[i+1];levels.add(a[1]);
      if(Math.abs(a[1]-b[1])>V018_EPS)edges.push({a,b,lo:Math.min(a[1],b[1]),hi:Math.max(a[1],b[1])});}}
  const zs=[...levels].sort((a,b)=>a-b),triangles=[];
  const at=(e,z)=>e.a[0]+(e.b[0]-e.a[0])*(z-e.a[1])/(e.b[1]-e.a[1]);
  const add=(a,b,c)=>{if(Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))>V018_EPS)triangles.push([a,b,c]);};
  for(let i=0;i<zs.length-1;i++){
    const lo=zs[i],hi=zs[i+1],mid=(lo+hi)/2;if(hi-lo<V018_EPS)continue;
    const active=edges.filter(e=>e.lo<mid&&e.hi>mid).sort((a,b)=>at(a,mid)-at(b,mid));
    if(active.length%2)throw new Error('Polygone non fermé ou auto-intersecté');
    for(let k=0;k<active.length;k+=2){const l=active[k],r=active[k+1],a=[at(l,lo),lo],b=[at(r,lo),lo],c=[at(r,hi),hi],d=[at(l,hi),hi];add(a,b,c);add(a,c,d);}
  }
  return triangles;
}
function v018MeshData(d){
  const tris=[],push=(a,b,c)=>tris.push(...a,...b,...c);
  if(d.mesh==='terrain'||d.mesh==='geoSurface'){
    for(const f of d.faces||[]){const a=d.vertices[f[0]],b=d.vertices[f[1]],c=d.vertices[f[2]];if(a&&b&&c)push(a,b,c);}
  }else{
    const y=d.mesh==='prism'?(d.baseY||0)+d.height:d.pos[1];
    for(const t of v018Triangulate(d.rings||[])){
      const a=[t[0][0],y,t[0][1]],b=[t[1][0],y,t[1][1]],c=[t[2][0],y,t[2][1]];
      if(vCross(vSub(b,a),vSub(c,a))[1]<0)push(a,c,b);else push(a,b,c);
    }
    if(d.mesh==='prism')for(const ring of d.rings){for(let i=0;i<ring.length-1;i++){
      const p=ring[i],q=ring[i+1],a=[p[0],d.baseY||0,p[1]],b=[q[0],d.baseY||0,q[1]],c=[q[0],y,q[1]],e=[p[0],y,p[1]];push(a,b,c);push(a,c,e);
    }}
  }
  const chunks=[];for(let i=0;i<tris.length;i+=9*18000)chunks.push(flatMesh(tris.slice(i,i+9*18000)));return chunks;
}
function v018MeshRevision(d){return`${d.revision||0}/${d.baseY}/${d.height}/${d.pos?.[1]}`;}
function v018DeleteGLMesh(gl,m){gl.deleteBuffer(m.p);gl.deleteBuffer(m.n);gl.deleteBuffer(m.i);}
const v018OriginalGLRender=GLRenderer.prototype.render;
GLRenderer.prototype.render=function(draws,camera,env){
  const gl=this.gl;this.resize();this.geoMeshes??=new Map();
  const active=new Set(draws.filter(d=>['prism','flatpoly','terrain','geoSurface'].includes(d.mesh)));
  for(const[d,entry]of this.geoMeshes)if(!active.has(d)){for(const m of entry.meshes)v018DeleteGLMesh(gl,m);this.geoMeshes.delete(d);}
  gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);
  const far=world?.geoMacro?8000:400,proj=m4Perspective(rad(camera.fov||67),this.canvas.width/this.canvas.height,.08,far),vp=m4Multiply(proj,m4LookAt(camera.pos,vAdd(camera.pos,camera.dir)));
  gl.uniformMatrix4fv(this.loc.viewProj,false,vp);gl.uniform3fv(this.loc.sun,env.sunDir||[.4,.8,.2]);gl.uniform3fv(this.loc.fog,env.fog||[.45,.58,.58]);gl.uniform3fv(this.loc.cam,camera.pos);
  const nearFog=gl.getUniformLocation(this.program,'uFogNear'),farFog=gl.getUniformLocation(this.program,'uFogFar');
  if(nearFog)gl.uniform1f(nearFog,world?.geoMacro?1200:65);if(farFog)gl.uniform1f(farFog,world?.geoMacro?6500:280);
  let count=0,triangles=0;
  for(const d of draws){
    if(d.hidden)continue;let meshes,model;
    if(active.has(d)){
      let e=this.geoMeshes.get(d);const revision=v018MeshRevision(d);
      if(!e||e.revision!==revision){if(e)for(const m of e.meshes)v018DeleteGLMesh(gl,m);e={revision,meshes:v018MeshData(d).map(x=>this.createMesh(x))};this.geoMeshes.set(d,e);}
      meshes=e.meshes;model=m4Identity();gl.disable(gl.CULL_FACE);count++;
    }else{const m=this.meshes[d.mesh||'cube'];if(!m)continue;meshes=[m];model=m4TRS(d.pos,d.rotY||0,d.scale||[1,1,1]);gl.enable(gl.CULL_FACE);}
    if(typeof v028SetGLPiece==='function')v028SetGLPiece(this,d);gl.uniformMatrix4fv(this.loc.model,false,model);gl.uniform3fv(this.loc.color,d.color||COLORS.white);gl.uniform1f(this.loc.emissive,d.emissive||0);const alpha=d.alpha??1;gl.uniform1f(this.loc.alpha,alpha);
    if(alpha<1){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);}else{gl.disable(gl.BLEND);gl.depthMask(true);}
    for(const m of meshes){gl.bindBuffer(gl.ARRAY_BUFFER,m.p);gl.enableVertexAttribArray(this.loc.pos);gl.vertexAttribPointer(this.loc.pos,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,m.n);gl.enableVertexAttribArray(this.loc.nor);gl.vertexAttribPointer(this.loc.nor,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,m.i);gl.drawElements(gl.TRIANGLES,m.count,gl.UNSIGNED_SHORT,0);triangles+=m.count/3;}
  }
  gl.depthMask(true);gl.enable(gl.CULL_FACE);gl.disable(gl.BLEND);V018.render={backend:'WebGL',customMeshes:count,triangles,bufferGroups:this.geoMeshes.size};
};
/* The software fallback uses the same triangles, clipped against the near plane.
   It no longer drops an entire building when one corner is behind the camera. */
const v018OldSoftwareDraw=SoftwareRenderer.prototype.drawItem;
SoftwareRenderer.prototype.drawItem=function(d,z,camera,basis,focal,env){
  if(!['prism','flatpoly','terrain','geoSurface'].includes(d.mesh))return v018OldSoftwareDraw.call(this,d,z,camera,basis,focal,env);
  if(!d._v018Triangles||d._v018Revision!==v018MeshRevision(d)){d._v018Triangles=v018MeshData(d).flatMap(c=>{const out=[];for(let i=0;i<c.positions.length;i+=9)out.push([c.positions.slice(i,i+3),c.positions.slice(i+3,i+6),c.positions.slice(i+6,i+9)]);return out;});d._v018Revision=v018MeshRevision(d);}
  const ctx=this.ctx,faces=[],near=.08;
  for(const tri of d._v018Triangles){
    const p=tri.map(a=>{const r=vSub(a,camera.pos);return{x:vDot(r,basis.right),y:vDot(r,basis.up),z:vDot(r,basis.forward)};}),clipped=[];
    for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length],ai=a.z>=near,bi=b.z>=near;if(ai)clipped.push(a);if(ai!==bi){const t=(near-a.z)/(b.z-a.z);clipped.push({x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t),z:near});}}
    if(clipped.length<3)continue;const pts=clipped.map(a=>({x:this.canvas.width/2+a.x/a.z*focal,y:this.canvas.height/2-a.y/a.z*focal,z:a.z}));
    const normal=vNorm(vCross(vSub(tri[1],tri[0]),vSub(tri[2],tri[0]))),shade=.65+.25*Math.abs(normal[1]);faces.push({pts,depth:pts.reduce((n,a)=>n+a.z,0)/pts.length,shade});
  }
  faces.sort((a,b)=>b.depth-a.depth);
  for(const f of faces){ctx.fillStyle=this.color(d.color,f.depth,env,f.shade+(d.emissive||0),d.alpha??1);ctx.beginPath();f.pts.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fill();}
  V018.render.backend='Canvas logiciel';
};

/* Lambert-93 (EPSG:2154), GRS80. Every exterior unit is now one metre.
   Historic instances keep their own local coordinate system. */
function v018Lambert93(lat,lon){
  const e=.0818191910428158,n=.725607765053267,c=11754255.426096,phi=rad(lat),s=Math.sin(phi),l=Math.log(Math.tan(Math.PI/4+phi/2)*Math.pow((1-e*s)/(1+e*s),e/2)),r=c*Math.exp(-n*l),g=n*(rad(lon)-rad(3));
  return[700000+r*Math.sin(g),12655612.049876-r*Math.cos(g)];
}
function v018InverseLambert(x,y){
  const e=.0818191910428158,n=.725607765053267,c=11754255.426096,dx=x-700000,dy=12655612.049876-y,r=Math.hypot(dx,dy),l=-Math.log(r/c)/n;
  let phi=2*Math.atan(Math.exp(l))-Math.PI/2;
  for(let i=0;i<12;i++)phi=2*Math.atan(Math.exp(l)*Math.pow((1+e*Math.sin(phi))/(1-e*Math.sin(phi)),e/2))-Math.PI/2;
  return[phi*180/Math.PI,3+Math.atan2(dx,dy)/n*180/Math.PI];
}
const V018_OLD_SCALES=Object.fromEntries(Object.entries(V015_GEO_MACROS).map(([id,d])=>[id,{scale:d.scale,center:[...d.center]}]));
for(const d of Object.values(V015_GEO_MACROS)){d.scale=1;d.metricOrigin=v018Lambert93(...d.center);d.name=d.name.replace('Territoire réel','Extérieur géographique');}
v015GeoProject=function(id,lat,lon){const d=V015_GEO_MACROS[id];if(!d)throw new Error('Région inconnue');const p=v018Lambert93(lat,lon),o=d.metricOrigin;return[p[0]-o[0],0,o[1]-p[1]];};
v015GeoUnproject=function(id,x,z){const d=V015_GEO_MACROS[id];return v018InverseLambert(x+d.metricOrigin[0],d.metricOrigin[1]-z);};
function v018HeightInfo(f){
  const p=f.props||{},parse=v=>{if(typeof v==='number')return v;if(typeof v==='string'){const m=v.match(/^\s*(\d+(?:[.,]\d+)?)\s*(m|metres|meters)?\s*$/i);if(m)return Number(m[1].replace(',','.'));}return NaN;};
  for(const key of['render_height','height','building:height']){const n=parse(p[key]);if(Number.isFinite(n)&&n>0&&n<500)return{height:n,estimated:false,basis:key};}
  const levels=parse(p['building:levels']??p.levels);if(Number.isFinite(levels)&&levels>0&&levels<100)return{height:levels*3,estimated:true,basis:'niveaux × 3 m — estimation'};
  return{height:6,estimated:true,basis:'6 m par défaut — estimation'};
}
v017HeightFromFeature=function(f){return v018HeightInfo(f).height;};

/* Solid volume collisions: courtyard holes remain open. Roofs/floors block rays,
   including a ray starting above the building and aimed downwards. */
v017AddPolyCollider=function(w,ring,minY,maxY,opts={}){
  const rings=opts.rings||[ring],b=v017PolyBounds(rings),c={minX:b.minX,maxX:b.maxX,minZ:b.minZ,maxZ:b.maxZ,minY,maxY,id:opts.id||null,disabled:!!opts.disabled,poly:rings[0],rings,geoTile:opts.geoTile||null};w.colliders.push(c);return c;
};
v017ColliderHit=function(c,x,z,r=0){
  if(x+r<c.minX||x-r>c.maxX||z+r<c.minZ||z-r>c.maxZ)return false;if(!c.poly)return true;
  const rings=c.rings||[c.poly];if(v018Contains(rings,x,z))return true;
  for(const ring of rings)for(let i=0;i<ring.length-1;i++)if(v017PointSegDist(x,z,ring[i],ring[i+1])<=r)return true;
  return false;
};
rayAABB=function(o,d,c,maxDist=200){
  if(!c.poly)return V017_RAY_AABB_BASE(o,d,c,maxDist);const rings=c.rings||[c.poly],lo=c.minY??-Infinity,hi=c.maxY??Infinity;
  if(o[1]>=lo&&o[1]<=hi&&v018Contains(rings,o[0],o[2]))return 0;
  let best=Infinity;
  for(const ring of rings)for(let i=0;i<ring.length-1;i++){
    const a=ring[i],b=ring[i+1],vx=b[0]-a[0],vz=b[1]-a[1],den=d[0]*vz-d[2]*vx;if(Math.abs(den)<V018_EPS)continue;
    const ox=a[0]-o[0],oz=a[1]-o[2],t=(ox*vz-oz*vx)/den,u=(ox*d[2]-oz*d[0])/den,yy=o[1]+d[1]*t;
    if(t>=0&&t<=maxDist&&u>=0&&u<=1&&yy>=lo&&yy<=hi)best=Math.min(best,t);
  }
  if(Math.abs(d[1])>V018_EPS)for(const yy of[lo,hi]){const t=(yy-o[1])/d[1];if(t>=0&&t<=maxDist&&v018Contains(rings,o[0]+d[0]*t,o[2]+d[2]*t))best=Math.min(best,t);}
  return best;
};
SoftwareRenderer.prototype.render=function(draws,camera,env){
  this.resize();this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);const forward=vNorm(camera.dir),right=vNorm(vCross(forward,[0,1,0])),up=vNorm(vCross(right,forward)),basis={forward,right,up},focal=this.canvas.height/(2*Math.tan(rad(camera.fov||67)/2)),far=world?.geoMacro?8000:400;
  const visible=[];for(const d of draws){if(d.hidden)continue;const z=vDot(vSub(d.pos,camera.pos),forward),custom=['prism','flatpoly','terrain','geoSurface'].includes(d.mesh);if(!custom&&(z<.08||z>far))continue;visible.push({d,z});}visible.sort((a,b)=>b.z-a.z);for(const a of visible)this.drawItem(a.d,a.z,camera,basis,focal,env);V018.render={backend:'Canvas logiciel',customMeshes:visible.filter(a=>['prism','flatpoly','terrain','geoSurface'].includes(a.d.mesh)).length,triangles:0};
};
SoftwareRenderer.prototype.color=function(col,dist,env,shade=1,alpha=1){const fog=world?.geoMacro?clamp((dist-1200)/5300,0,1):clamp((dist-55)/225,0,1),fc=env.fog||[.5,.6,.58];return `rgba(${[0,1,2].map(i=>Math.round(clamp(lerp(col[i]*shade,fc[i],fog),0,1)*255)).join(',')},${alpha})`;};
/* Software geographic fallback: a real per-pixel depth buffer avoids a large park
   polygon painting over nearer buildings. It is lower resolution than WebGL. */
SoftwareRenderer.prototype.renderGeoDepth=function(draws,camera,basis,env){
  const W=Math.max(1,Math.round(this.canvas.width*.65)),H=Math.max(1,Math.round(this.canvas.height*.65));
  if(!this.geoRaster||this.geoRaster.width!==W||this.geoRaster.height!==H){this.geoRaster=document.createElement('canvas');this.geoRaster.width=W;this.geoRaster.height=H;this.geoCtx=this.geoRaster.getContext('2d');this.geoImage=this.geoCtx.createImageData(W,H);this.geoDepth=new Float32Array(W*H);}
  const rgba=this.geoImage.data,depth=this.geoDepth;rgba.fill(0);depth.fill(0);const focal=H/(2*Math.tan(rad(camera.fov||67)/2)),near=.08,sun=env.sunDir||[.4,.8,.2],fogc=env.fog||[.5,.6,.58];let trisDrawn=0,pixels=0;
  for(const d of draws){
    const revision=v018MeshRevision(d);if(!d._v018Triangles||d._v018Revision!==revision){d._v018Triangles=v018MeshData(d).flatMap(c=>{const out=[];for(let i=0;i<c.positions.length;i+=9)out.push([c.positions.slice(i,i+3),c.positions.slice(i+3,i+6),c.positions.slice(i+6,i+9)]);return out;});d._v018Revision=revision;}
    for(const tri of d._v018Triangles){const poly=tri.map(a=>{const r=vSub(a,camera.pos);return{x:vDot(r,basis.right),y:vDot(r,basis.up),z:vDot(r,basis.forward)};}),clip=[];
      for(let i=0;i<3;i++){const a=poly[i],b=poly[(i+1)%3],ai=a.z>=near,bi=b.z>=near;if(ai)clip.push(a);if(ai!==bi){const t=(near-a.z)/(b.z-a.z);clip.push({x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t),z:near});}}if(clip.length<3)continue;
      const pp=clip.map(a=>({x:W/2+a.x/a.z*focal,y:H/2-a.y/a.z*focal,iz:1/a.z})),normal=vNorm(vCross(vSub(tri[1],tri[0]),vSub(tri[2],tri[0]))),light=.5+.32*Math.abs(vDot(normal,sun))+.12*Math.abs(normal[1])+(d.emissive||0),col=d.color||[.7,.7,.6];
      for(let k=1;k<pp.length-1;k++){const a=pp[0],b=pp[k],c=pp[k+1],den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);if(Math.abs(den)<1e-7)continue;
        const left=Math.max(0,Math.floor(Math.min(a.x,b.x,c.x))),right=Math.min(W-1,Math.ceil(Math.max(a.x,b.x,c.x))),top=Math.max(0,Math.floor(Math.min(a.y,b.y,c.y))),bottom=Math.min(H-1,Math.ceil(Math.max(a.y,b.y,c.y)));if(left>right||top>bottom)continue;trisDrawn++;
        const dx0=(b.y-c.y)/den,dx1=(c.y-a.y)/den,dy0=(c.x-b.x)/den,dy1=(a.x-c.x)/den;let start0=dx0*(left+.5-c.x)+dy0*(top+.5-c.y),start1=dx1*(left+.5-c.x)+dy1*(top+.5-c.y);
        for(let y=top;y<=bottom;y++,start0+=dy0,start1+=dy1){let u=start0,v=start1;for(let x=left;x<=right;x++,u+=dx0,v+=dx1){const q=1-u-v;if(u<-.00001||v<-.00001||q<-.00001)continue;const iz=u*a.iz+v*b.iz+q*c.iz,index=y*W+x;if(iz<=depth[index]||iz<=0)continue;depth[index]=iz;const f=clamp((1/iz-1200)/5300,0,1),i=index*4;rgba[i]=clamp(lerp(col[0]*light,fogc[0],f),0,1)*255;rgba[i+1]=clamp(lerp(col[1]*light,fogc[1],f),0,1)*255;rgba[i+2]=clamp(lerp(col[2]*light,fogc[2],f),0,1)*255;rgba[i+3]=(d.alpha??1)*255;pixels++;}}
      }
    }
  }
  this.geoCtx.putImageData(this.geoImage,0,0);this.ctx.drawImage(this.geoRaster,0,0,this.canvas.width,this.canvas.height);return{triangles:trisDrawn,fragments:pixels};
};
SoftwareRenderer.prototype.render=function(draws,camera,env){
 this.resize();this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);const forward=vNorm(camera.dir),right=vNorm(vCross(forward,[0,1,0])),up=vNorm(vCross(right,forward)),basis={forward,right,up},focal=this.canvas.height/(2*Math.tan(rad(camera.fov||67)/2)),custom=draws.filter(d=>!d.hidden&&['prism','flatpoly','terrain','geoSurface'].includes(d.mesh));
 const rest=draws.filter(d=>!d.hidden&&!custom.includes(d)).map(d=>({d,z:vDot(vSub(d.pos,camera.pos),forward)})).filter(a=>a.z>.08&&a.z<(world?.geoMacro?8000:400)).sort((a,b)=>b.z-a.z);
 if(custom.length){for(const a of rest.filter(a=>a.d.id?.startsWith('geo-ground-')))this.drawItem(a.d,a.z,camera,basis,focal,env);const stats=this.renderGeoDepth(custom,camera,basis,env);for(const a of rest.filter(a=>!a.d.id?.startsWith('geo-ground-')))this.drawItem(a.d,a.z,camera,basis,focal,env);V018.render={backend:'Canvas logiciel · profondeur géographique',customMeshes:custom.length,...stats};}
 else{for(const a of rest)this.drawItem(a.d,a.z,camera,basis,focal,env);V018.render={backend:'Canvas logiciel',customMeshes:0,triangles:0};}
};
