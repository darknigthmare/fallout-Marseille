/* Measured bridge decks are physical support surfaces, never a new terrain
   sample. The original DEM and missing-data state remain unchanged below them.
   Only the published road triangles participate; no inferred deck/railing or
   underground passage is manufactured from a bridge label. */
const MistralSurfaces=(()=>{
 const STEP=.72,EPS=1e-7,CELL=32,MAX_SLOPE=1;
 function measuredBridge(d){
  const p=d?.sourceProfile,props=d?.roadProperties||d?.geoProperties||{},width=d?.roadWidth??p?.width;
  if(d?.mesh!=='geoSurface'||d.geoLayer!=='transportation'||d.hidden||!p?.bridge||p.tunnel||p.elevationAssumed!==false||!Number.isFinite(width)||width<=0||width>300)return false;
  if(/rail|tram|ferry|aerial|construction|proposed|abandoned/.test(String(props.class||props.subclass||props.highway||props.railway||'')))return false;
  const xyz=p.heightBasis==='coordonnées Z source'&&Array.isArray(d.roadPath)&&d.roadPath.length>=2&&d.roadPath.every(q=>Array.isArray(q)&&q.length>=3&&q.slice(0,3).every(Number.isFinite));
  const absolute=Number.isFinite(p.absoluteHeight),clearance=['bridge:height','min_height'].includes(p.heightBasis)&&Number.isFinite(p.offset)&&p.offset>=0;
  return xyz||absolute||clearance;
 }
 function triangle(vertices,face,id){
  if(!Array.isArray(face)||face.length!==3||face.some(i=>!Number.isInteger(i)||i<0||i>=vertices.length))return null;
  const points=face.map(i=>vertices[i]);if(points.some(p=>!Array.isArray(p)||p.length<3||!p.slice(0,3).every(Number.isFinite)))return null;
  const[a,b,c]=points,den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);if(Math.abs(den)<1e-10)return null;
  const gx=((b[1]-a[1])*(c[2]-a[2])-(c[1]-a[1])*(b[2]-a[2]))/den,gz=((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/den;
  if(Math.hypot(gx,gz)>MAX_SLOPE+EPS)return null;
  return{a:a.slice(0,3),b:b.slice(0,3),c:c.slice(0,3),den,id,minX:Math.min(a[0],b[0],c[0]),maxX:Math.max(a[0],b[0],c[0]),minZ:Math.min(a[2],b[2],c[2]),maxZ:Math.max(a[2],b[2],c[2])};
 }
 function height(t,x,z){
  if(!Number.isFinite(x)||!Number.isFinite(z)||x<t.minX-EPS||x>t.maxX+EPS||z<t.minZ-EPS||z>t.maxZ+EPS)return null;
  const u=((t.b[2]-t.c[2])*(x-t.c[0])+(t.c[0]-t.b[0])*(z-t.c[2]))/t.den,v=((t.c[2]-t.a[2])*(x-t.c[0])+(t.a[0]-t.c[0])*(z-t.c[2]))/t.den,w=1-u-v;
  return u>=-EPS&&v>=-EPS&&w>=-EPS?u*t.a[1]+v*t.b[1]+w*t.c[1]:null;
 }
 class DeckIndex{
  constructor(draws=[]){
   this.cells=new Map();this.broad=[];this.decks=0;this.triangles=0;const seen=new Set();
   for(const d of draws){
    if(!measuredBridge(d)||!Array.isArray(d.vertices)||!Array.isArray(d.faces))continue;
    const id=d.v046GeometryId||d.id||d;if(seen.has(id))continue;seen.add(id);let admitted=false;
    for(const face of d.faces){const t=triangle(d.vertices,face,typeof id==='string'?id:'measured-bridge');if(!t)continue;admitted=true;this.triangles++;
     const x0=Math.floor(t.minX/CELL),x1=Math.floor(t.maxX/CELL),z0=Math.floor(t.minZ/CELL),z1=Math.floor(t.maxZ/CELL);
     if((x1-x0+1)*(z1-z0+1)>4096)this.broad.push(t);
     else for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){const key=x+':'+z;if(!this.cells.has(key))this.cells.set(key,[]);this.cells.get(key).push(t);}
    }
    if(admitted)this.decks++;
   }
  }
  at(x,z){return Number.isFinite(x)&&Number.isFinite(z)?[...(this.cells.get(Math.floor(x/CELL)+':'+Math.floor(z/CELL))||[]),...this.broad]:[];}
  support(x,z,feet,allowStep=true){
   if(!Number.isFinite(feet))return null;
   const ceiling=feet+(allowStep?STEP:EPS);let result=null;
   for(const t of this.at(x,z)){const y=height(t,x,z);if(y!==null&&y<=ceiling&&(!result||y>result.height+EPS||Math.abs(y-result.height)<=EPS&&t.id<result.id))result={height:y,id:t.id,measured:true};}
   return result;
  }
  ceiling(x,z,previousHead,nextHead){
   if(![previousHead,nextHead].every(Number.isFinite)||nextHead<=previousHead)return null;
   let result=null;for(const t of this.at(x,z)){const y=height(t,x,z);if(y!==null&&y>=previousHead-EPS&&y<=nextHead+EPS&&(!result||y<result.height))result={height:y,id:t.id};}return result;
  }
 }
 return{STEP,triangle,height,measuredBridge,DeckIndex};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralSurfaces;

const V050_SURFACES={cache:new WeakMap(),contact:null};
function v050DeckIndex(w=world){
 if(!w?.v046)return null;
 const owner=w.v046Records||w.staticDraws;let cached=V050_SURFACES.cache.get(w);
 if(!cached||cached.owner!==owner){
  const draws=w.v046Records?[...w.v046Records.values()].flatMap(r=>r.roads||[]):w.staticDraws||[];
  cached={owner,index:new MistralSurfaces.DeckIndex(draws)};V050_SURFACES.cache.set(w,cached);
 }
 return cached.index;
}
function v050DeckSupport(x,z,referenceFeet,allowStep=true){return v050DeckIndex()?.support(x,z,referenceFeet,allowStep)||null;}
const v050SurfaceGroundBase=groundHeightAt;
groundHeightAt=function(x,z,referenceFeet=0){
 const ground=v050SurfaceGroundBase(x,z,referenceFeet);if(!world?.v046)return ground;
 const atPlayer=state?.player?.pos&&Math.abs(x-state.player.pos[0])<1e-7&&Math.abs(z-state.player.pos[2])<1e-7;
 // A rising or falling body cannot step up onto a surface above its feet.
 // The core integrator will land on the measured plane when descending through it.
 const deck=v050DeckSupport(x,z,referenceFeet,!(atPlayer&&!onGround));if(!deck)return ground;
 const terrain=v047Height(v047Bank(world),x,z).height;
 return terrain===null?deck.height:Math.max(ground,deck.height);
};
const v050SurfaceUpdateBase=updatePlayer;
updatePlayer=function(dt){
 const active=world?.v046&&gameStarted&&mode==='PLAYING'&&!zoneTransitioning&&!V018.qaFreeze&&Number.isFinite(dt)&&dt>0;
 const w=world,s=state,p=state.player,eye=playerEyeHeight(),feet=p.pos[1]-eye,head=p.pos[1]+.18,wasRising=active&&!onGround&&jumpVelocity>0,previous=V050_SURFACES.contact;
 if(active&&onGround&&previous?.world===w&&previous.state===s&&Math.hypot(previous.x-p.pos[0],previous.z-p.pos[2])<2){
  const deck=v050DeckSupport(p.pos[0],p.pos[2],feet,false),ground=v050SurfaceGroundBase(p.pos[0],p.pos[2],feet);
  if(!deck&&feet-ground>.95){onGround=false;jumpVelocity=0;}
 }
 const result=v050SurfaceUpdateBase(dt);
 if(active&&world===w&&state===s){
  // Deck data supplies a top plane, not an invented thickness. Stop an upward
  // head crossing at that same measured plane; never snap the player above it.
  if(wasRising&&!onGround){const ceiling=v050DeckIndex(w).ceiling(p.pos[0],p.pos[2],head,p.pos[1]+.18);if(ceiling){p.pos[1]=ceiling.height-.181;jumpVelocity=0;}}
  const support=onGround?v050DeckSupport(p.pos[0],p.pos[2],p.pos[1]-playerEyeHeight(),false):null;
  V050_SURFACES.contact=support&&Math.abs(support.height-(p.pos[1]-playerEyeHeight()))<.05?{world:w,state:s,x:p.pos[0],z:p.pos[2],...support}:null;
 }else if(world!==w||state!==s||!world?.v046)V050_SURFACES.contact=null;
 return result;
};
function v050SurfacesAfterInit(){
 Object.assign(window.__MISTRAL_DEBUG,{v050DeckSupport,v050SurfaceInfo:()=>{const index=v050DeckIndex();return{decks:index?.decks||0,triangles:index?.triangles||0,contact:V050_SURFACES.contact?{id:V050_SURFACES.contact.id,height:V050_SURFACES.contact.height}:null};}});
}
