/* Exact narrow phase for a roof whose shape, direction and height were supplied.
   Unknown roof shapes retain their labelled bounding volume. A closed solid is
   a collision model of the rendered exterior, never an invented interior. */
const MistralRoofSolids=(()=>{
 const EPS=1e-7;
 const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((n,v,i)=>n+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 function face(a,b,c){
  if([a,b,c].some(p=>!Array.isArray(p)||p.length<3||!p.slice(0,3).every(Number.isFinite)))return null;
  const normal=cross(sub(b,a),sub(c,a));return Math.hypot(...normal)>1e-10?[a.slice(0,3),b.slice(0,3),c.slice(0,3)]:null;
 }
 function projected(points){
  const[a,b,c]=points,den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);if(Math.abs(den)<1e-10)return null;
  const gx=((b[1]-a[1])*(c[2]-a[2])-(c[1]-a[1])*(b[2]-a[2]))/den,gz=((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/den;
  return{a,b,c,den,gx,gz,walkable:Math.hypot(gx,gz)<=1+EPS};
 }
 function plane(t,x,z){
  const u=((t.b[2]-t.c[2])*(x-t.c[0])+(t.c[0]-t.b[0])*(z-t.c[2]))/t.den,v=((t.c[2]-t.a[2])*(x-t.c[0])+(t.a[0]-t.c[0])*(z-t.c[2]))/t.den,w=1-u-v;
  return u>=-EPS&&v>=-EPS&&w>=-EPS?u*t.a[1]+v*t.b[1]+w*t.c[1]:null;
 }
 function rayFace(origin,direction,points,maxDistance){
  const[a,b,c]=points,e1=sub(b,a),e2=sub(c,a),p=cross(direction,e2),det=dot(e1,p);if(Math.abs(det)<1e-10)return Infinity;
  const inv=1/det,s=sub(origin,a),u=dot(s,p)*inv;if(u< -EPS||u>1+EPS)return Infinity;
  const q=cross(s,e1),v=dot(direction,q)*inv;if(v< -EPS||u+v>1+EPS)return Infinity;
  const distance=dot(e2,q)*inv;return distance>=-EPS&&distance<=maxDistance+EPS?Math.max(0,distance):Infinity;
 }
 function rayBounds(o,d,b,limit){
  let lo=0,hi=limit;
  for(const[axis,min,max]of[[0,b.minX,b.maxX],[1,b.minY,b.maxY],[2,b.minZ,b.maxZ]]){
   if(Math.abs(d[axis])<1e-12){if(o[axis]<min-EPS||o[axis]>max+EPS)return false;}
   else{let a=(min-o[axis])/d[axis],c=(max-o[axis])/d[axis];if(a>c)[a,c]=[c,a];lo=Math.max(lo,a);hi=Math.min(hi,c);if(lo>hi+EPS)return false;}
  }
  return true;
 }
 /* A linear roof plane reaches its maximum over triangle∩foot-disc at a
    vertex, a circle/edge intersection, or the circle's uphill tangent. */
 function diskHeight(t,x,z,r){
  let result=plane(t,x,z),r2=r*r;
  const admit=(px,pz)=>{if((px-x)**2+(pz-z)**2>r2+EPS)return;const y=plane(t,px,pz);if(y!==null&&(result===null||y>result))result=y;};
  for(const p of[t.a,t.b,t.c])admit(p[0],p[2]);
  for(const[a,b]of[[t.a,t.b],[t.b,t.c],[t.c,t.a]]){
   const dx=b[0]-a[0],dz=b[2]-a[2],sx=a[0]-x,sz=a[2]-z,A=dx*dx+dz*dz;if(A<1e-12)continue;
   const B=2*(sx*dx+sz*dz),C=sx*sx+sz*sz-r2,discriminant=B*B-4*A*C;if(discriminant< -EPS)continue;
   const root=Math.sqrt(Math.max(0,discriminant));for(const u of[(-B-root)/(2*A),(-B+root)/(2*A)])if(u>=-EPS&&u<=1+EPS)admit(a[0]+u*dx,a[2]+u*dz);
  }
  const gradient=Math.hypot(t.gx,t.gz);if(gradient>1e-12)admit(x+r*t.gx/gradient,z+r*t.gz/gradient);
  return result;
 }
 class Solid{
  constructor(body,cap,collider,geometry,inside){
   this.id=collider.id;this.rings=body.rings;this.minY=collider.minY;this.maxY=collider.maxY;this.bounds={...collider};this.inside=inside;
   this.faces=[];this.tops=[];const eaves=body.baseY+body.height;
   for(const data of geometry(body))for(let i=0;i<data.indices.length;i+=3){
    const points=data.indices.slice(i,i+3).map(index=>data.positions.slice(index*3,index*3+3)),valid=face(...points);if(!valid)continue;
    if(points.every(p=>Math.abs(p[1]-eaves)<EPS)){
     const bottom=face(...points.map(p=>[p[0],this.minY,p[2]]).reverse());if(bottom)this.faces.push(bottom);
    }else this.faces.push(valid);
   }
   for(const indices of cap.faces||[]){
    if(!Array.isArray(indices)||indices.length!==3||indices.some(i=>!Number.isInteger(i)||i<0||i>=cap.vertices.length))throw Error('Face de toiture invalide');
    const valid=face(...indices.map(i=>cap.vertices[i]));if(!valid)continue;
    this.faces.push(valid);const top=projected(valid);if(top)this.tops.push(top);
   }
   if(!this.tops.length)throw Error('Toiture sans surface supérieure');
  }
  heightAt(x,z){let result=null;for(const t of this.tops){const y=plane(t,x,z);if(y!==null&&(result===null||y>result))result=y;}return result;}
  contains(p){const y=this.heightAt(p[0],p[2]);return y!==null&&this.inside(this.rings,p[0],p[2])&&p[1]>=this.minY-EPS&&p[1]<=y+EPS;}
  ray(origin,direction,maxDistance=200){
   if(!Array.isArray(origin)||!Array.isArray(direction)||origin.length<3||direction.length<3||!origin.slice(0,3).every(Number.isFinite)||!direction.slice(0,3).every(Number.isFinite)||!(Number.isFinite(maxDistance)||maxDistance===Infinity)||maxDistance<0)return Infinity;
   if(!rayBounds(origin,direction,this.bounds,maxDistance))return Infinity;if(this.contains(origin))return 0;
   let result=Infinity;for(const points of this.faces)result=Math.min(result,rayFace(origin,direction,points,maxDistance));return result;
  }
  maxDisk(x,z,r=0,walkableOnly=false){
   if(![x,z,r].every(Number.isFinite)||r<0||x+r<this.bounds.minX||x-r>this.bounds.maxX||z+r<this.bounds.minZ||z-r>this.bounds.maxZ)return null;
   let result=null;for(const t of this.tops){if(walkableOnly&&!t.walkable)continue;const y=diskHeight(t,x,z,r);if(y!==null&&(result===null||y>result))result=y;}return result;
  }
  cylinder(x,z,r,feet,head){
   if(![feet,head].every(Number.isFinite)||head<feet||head<this.minY-EPS||feet>this.maxY+EPS)return false;
   const top=this.maxDisk(x,z,r);return top!==null&&feet<top-EPS;
  }
  support(x,z,feet,r=0,allowStep=true){
   if(!Number.isFinite(feet))return null;const y=this.maxDisk(x,z,r,true);
   return y!==null&&y<=feet+(allowStep?.72:EPS)?{id:this.id,height:y,measured:true}:null;
  }
 }
 function explicit(body,cap){const p=body?.sourceProfile;return !!(p&&cap?.geoLayer==='roof'&&p.estimated===false&&p.roofEstimated===false&&p.roofHeight>0&&Number.isFinite(p.roofDirection)&&['gabled','skillion'].includes(p.roofShape));}
 return{EPS,face,plane,projected,rayFace,diskHeight,Solid,explicit};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralRoofSolids;

const V050_ROOFS={cache:new WeakMap(),body:null,actorEye:null,contact:null,attached:0};
const v050RoofBuildingBase=v046SourceBuilding;
v046SourceBuilding=function(w,rings,feature,key){
 const start=w.staticDraws.length,body=v050RoofBuildingBase(w,rings,feature,key);if(!body)return body;
 const cap=w.staticDraws.slice(start).find(d=>d.geoLayer==='roof'&&d.geoFeatureId===body.geoFeatureId),collider=w.colliders.findLast(c=>c.id===body.id);
 if(collider&&MistralRoofSolids.explicit(body,cap)){
  try{collider.v050RoofSolid=new MistralRoofSolids.Solid(body,cap,collider,v018MeshData,MistralIntegrity.inside);V050_ROOFS.attached++;}
  catch(error){collider.v050RoofError=String(error.message||error);}
 }
 return body;
};
const v050RoofRayBase=rayAABB;
rayAABB=function(origin,direction,collider,maxDistance=200){return collider.v050RoofSolid?collider.v050RoofSolid.ray(origin,direction,maxDistance):v050RoofRayBase(origin,direction,collider,maxDistance);};
const v050RoofFootprintBase=v017ColliderHit;
v017ColliderHit=function(c,x,z,r=0){
 if(!v050RoofFootprintBase(c,x,z,r))return false;
 return c.v050RoofSolid&&V050_ROOFS.body?c.v050RoofSolid.cylinder(x,z,r,V050_ROOFS.body.feet,V050_ROOFS.body.head):true;
};
const v050RoofCollisionBase=collidesAt;
collidesAt=function(x,z,r=.38,eyeY=null){
 const previous=V050_ROOFS.body,eye=eyeY??state.player?.pos?.[1]??1.65,atPlayer=Math.abs(x-state.player.pos[0])<1e-7&&Math.abs(z-state.player.pos[2])<1e-7&&Math.abs(eye-state.player.pos[1])<1e-7;
 V050_ROOFS.body={feet:eye-(V050_ROOFS.actorEye??(atPlayer?playerEyeHeight():1.65)),head:eye+.18};
 try{return v050RoofCollisionBase(x,z,r,eyeY);}finally{V050_ROOFS.body=previous;}
};
const v050RoofMoveBase=tryPlayerMove;
tryPlayerMove=function(...args){const previous=V050_ROOFS.actorEye;V050_ROOFS.actorEye=playerEyeHeight();try{return v050RoofMoveBase(...args);}finally{V050_ROOFS.actorEye=previous;}};
function v050RoofEntries(w=world){
 if(!w?.v046)return[];const owner=w.v046Records||w.colliders;let cache=V050_ROOFS.cache.get(w);
 if(!cache||cache.owner!==owner){cache={owner,entries:w.colliders.filter(c=>!c.disabled&&c.v050RoofSolid)};V050_ROOFS.cache.set(w,cache);}return cache.entries.filter(c=>!c.disabled);
}
function v050RoofSupport(x,z,feet,allowStep=true,radius=.38){
 let result=null;for(const c of v050RoofEntries()){const support=c.v050RoofSolid.support(x,z,feet,radius,allowStep);if(support&&(!result||support.height>result.height))result=support;}return result;
}
const v050RoofGroundBase=groundHeightAt;
groundHeightAt=function(x,z,referenceFeet=0){
 const ground=v050RoofGroundBase(x,z,referenceFeet);if(!world?.v046)return ground;
 const atPlayer=Math.abs(x-state.player.pos[0])<1e-7&&Math.abs(z-state.player.pos[2])<1e-7,support=v050RoofSupport(x,z,referenceFeet,!(atPlayer&&!onGround),state.player.crouched?.32:.38);
 if(!support)return ground;return v047Height(v047Bank(world),x,z).height===null?support.height:Math.max(ground,support.height);
};
const v050RoofUpdateBase=updatePlayer;
updatePlayer=function(dt){
 const active=world?.v046&&gameStarted&&mode==='PLAYING'&&!zoneTransitioning&&!V018.qaFreeze&&Number.isFinite(dt)&&dt>0,w=world,s=state,p=state.player,eye=playerEyeHeight(),feet=p.pos[1]-eye,head=p.pos[1]+.18,wasRising=active&&!onGround&&jumpVelocity>0,radius=p.crouched?.32:.38,previous=V050_ROOFS.contact;
 if(active&&onGround&&previous?.world===w&&previous.state===s&&Math.hypot(previous.x-p.pos[0],previous.z-p.pos[2])<2&&!v050RoofSupport(p.pos[0],p.pos[2],feet,false,radius)&&feet-v050RoofGroundBase(p.pos[0],p.pos[2],feet)>.95){onGround=false;jumpVelocity=0;}
 const result=v050RoofUpdateBase(dt);
 if(active&&world===w&&state===s){
  if(wasRising&&!onGround&&p.pos[1]+.18>head){let distance=p.pos[1]+.18-head;for(const c of v050RoofEntries(w))distance=Math.min(distance,c.v050RoofSolid.ray([p.pos[0],head,p.pos[2]],[0,1,0],distance));if(distance<p.pos[1]+.18-head){p.pos[1]=head+distance-.181;jumpVelocity=0;}}
  const support=onGround?v050RoofSupport(p.pos[0],p.pos[2],p.pos[1]-playerEyeHeight(),false,radius):null;
  V050_ROOFS.contact=support&&Math.abs(support.height-(p.pos[1]-playerEyeHeight()))<.05?{world:w,state:s,x:p.pos[0],z:p.pos[2],...support}:null;
 }else if(world!==w||state!==s||!world?.v046)V050_ROOFS.contact=null;
 return result;
};
function v050RoofAfterInit(){Object.assign(window.__MISTRAL_DEBUG,{v050RoofSupport,v050RoofInfo:()=>({precise:v050RoofEntries().length,triangles:v050RoofEntries().reduce((n,c)=>n+c.v050RoofSolid.faces.length,0),contact:V050_ROOFS.contact?{id:V050_ROOFS.contact.id,height:V050_ROOFS.contact.height}:null})});}
