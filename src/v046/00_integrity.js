/* Pure, independently testable continuity primitives. No global game mutation. */
const MistralIntegrity = (()=>{
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  function hash(value){let h=2166136261;const s=typeof value==='string'?value:JSON.stringify(value);for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619);return(h>>>0).toString(16).padStart(8,'0');}
  function ringKey(r){let a=r.map(p=>p.map(v=>Math.round(v*1000)/1000));if(a.length>1&&JSON.stringify(a[0])===JSON.stringify(a.at(-1)))a.pop();if(!a.length)return'';const candidates=[];for(const b of[a,a.slice().reverse()]){let m=0;for(let i=1;i<b.length;i++)if(JSON.stringify(b[i])<JSON.stringify(b[m]))m=i;candidates.push(JSON.stringify(b.slice(m).concat(b.slice(0,m))));}return candidates.sort()[0];}
  function footprintKey(source,rings,props={}){return source+':'+hash([rings.map(ringKey).sort(),props.height??props.render_height??null,props.levels??props['building:levels']??null]);}
  function inside(rings,x,z){function ring(r){let hit=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const a=r[i],b=r[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;}return !!rings.length&&ring(rings[0])&&!rings.slice(1).some(ring);}
  function intersects(a,b){return a[0]<b[2]&&a[2]>b[0]&&a[1]<b[3]&&a[3]>b[1];}
  function contains(b,lat,lon){return lat>=b[0]&&lat<=b[2]&&lon>=b[1]&&lon<=b[3];}
  function terrain(raw,id,expected){
    const {width:w,height:h,bbox:b,values:v}=raw||{};
    if(raw?.macro!==id||!Number.isInteger(w)||!Number.isInteger(h)||w<2||h<2||w*h>1048576||!Array.isArray(v)||v.length!==w*h)throw new Error('Grille incomplète : '+id);
    if(!Array.isArray(b)||b.length!==4||!b.every(Number.isFinite)||b[0]>=b[2]||b[1]>=b[3]||expected&&b.some((x,i)=>Math.abs(x-expected[i])>1e-7))throw new Error('Emprise incompatible : '+id);
    if((raw.sourceResource||raw.source_resource||raw.resource)!=='ign_rge_alti_wld'&&!raw.qaFixture)throw new Error('Provenance altimétrique absente : '+id);
    if(raw.rowOrder&&raw.rowOrder!=='north-to-south')throw new Error('Ordre des lignes non pris en charge');
    const data=Float64Array.from(v,x=>x!==null&&typeof x==='number'&&Number.isFinite(x)&&x>-100&&x<9000?x:NaN);
    if(!data.some(Number.isFinite))throw new Error('Aucune altitude valide : '+id);
    return{id,width:w,height:h,bbox:b.slice(),data,qa:!!raw.qaFixture};
  }
  function sample(t,lat,lon){if(!contains(t.bbox,lat,lon))return null;const b=t.bbox,x=(lon-b[1])/(b[3]-b[1])*(t.width-1),y=(b[2]-lat)/(b[2]-b[0])*(t.height-1),a=Math.floor(x),c=Math.floor(y),d=Math.min(t.width-1,a+1),e=Math.min(t.height-1,c+1),u=x-a,v=y-c;let sum=0,n=0;for(const[xx,yy,weight]of[[a,c,(1-u)*(1-v)],[d,c,u*(1-v)],[a,e,(1-u)*v],[d,e,u*v]]){const z=t.data[yy*t.width+xx];if(Number.isFinite(z)&&weight>0){sum+=z*weight;n+=weight;}}return n>0?sum/n:null;}
  class TerrainBank{
    constructor(bounds){this.bounds=bounds;this.grids=new Map();}
    add(raw,id){const t=terrain(raw,id,this.bounds[id]);this.grids.set(id,t);return t;}
    required(b){return Object.keys(this.bounds).filter(id=>intersects(this.bounds[id],b)).sort();}
    read(lat,lon){let sum=0,w=0;const sources=[];for(const id of Object.keys(this.bounds).sort()){const b=this.bounds[id];if(!contains(b,lat,lon))continue;if(!this.grids.has(id))return{height:null,missing:id,sources};const t=this.grids.get(id),z=sample(t,lat,lon);if(z===null)continue;const edge=Math.min((lat-b[0])/(b[2]-b[0]),(b[2]-lat)/(b[2]-b[0]),(lon-b[1])/(b[3]-b[1]),(b[3]-lon)/(b[3]-b[1]));const weight=Math.max(.0001,Math.min(1,edge*12));sum+=z*weight;w+=weight;sources.push(id);}return{height:w?sum/w:null,missing:null,sources};}
  }
  class Gate{
    constructor(maxParallel=4){this.maxParallel=maxParallel;this.serial=0;this.current=null;this.cache=new Map();this.status={phase:'idle',done:0,total:0,errors:[]};}
    cancel(){this.serial++;if(this.current)this.current.abort();this.current=null;this.status={...this.status,phase:'cancelled'};}
    async run(keys,fetcher,prepare,publish,onProgress=()=>{}){
      this.cancel();const ticket=this.serial,controller=new AbortController();this.current=controller;const unique=[...new Set(keys)];this.status={phase:'loading',done:0,total:unique.length,errors:[]};onProgress(this.status);
      let index=0;const result=new Map(),errors=[];
      const worker=async()=>{while(index<unique.length&&!controller.signal.aborted){const key=unique[index++];try{const value=this.cache.has(key)?this.cache.get(key):await fetcher(key,controller.signal);if(controller.signal.aborted||ticket!==this.serial)return;this.cache.set(key,value);result.set(key,value);}catch(e){if(!controller.signal.aborted)errors.push({key,message:String(e.message||e)});}if(ticket===this.serial){this.status.done++;onProgress(this.status);}}};
      await Promise.all(Array.from({length:Math.min(this.maxParallel,unique.length)},worker));
      if(ticket!==this.serial||controller.signal.aborted)return{ok:false,cancelled:true};
      if(errors.length){this.status={...this.status,phase:'failed',errors};onProgress(this.status);return{ok:false,errors};}
      try{this.status.phase='preparing';onProgress(this.status);const stage=await prepare(result,controller.signal);if(ticket!==this.serial||controller.signal.aborted)return{ok:false,cancelled:true};publish(stage);this.status={...this.status,phase:'ready',errors:[]};onProgress(this.status);this.current=null;return{ok:true};}catch(e){if(ticket!==this.serial)return{ok:false,cancelled:true};errors.push({key:'geometry',message:String(e.message||e)});this.status={...this.status,phase:'failed',errors};onProgress(this.status);return{ok:false,errors};}
    }
  }
  return{hash,ringKey,footprintKey,inside,intersects,contains,terrain,sample,TerrainBank,Gate};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralIntegrity;
