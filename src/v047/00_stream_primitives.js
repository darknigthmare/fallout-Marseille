/* v0.47 portable streaming primitives. Byte counts are retained-resource estimates,
   not a measurement of the browser heap or of GPU memory. */
const MistralStream = (()=>{
 function bytes(value,seen=new Set()){
  if(value===null||value===undefined)return 0;
  if(typeof value==='string')return value.length*2;
  if(typeof value==='number')return 8;
  if(typeof value==='boolean')return 4;
  if(typeof value!=='object'||seen.has(value))return 0;
  seen.add(value);
  if(value instanceof ArrayBuffer)return value.byteLength;
  if(ArrayBuffer.isView(value))return bytes(value.buffer,seen);
  if(value instanceof Map)return [...value].reduce((n,[k,v])=>n+bytes(k,seen)+bytes(v,seen),32);
  if(Array.isArray(value))return value.reduce((n,v)=>n+bytes(v,seen),16);
  return Object.entries(value).reduce((n,[k,v])=>n+k.length*2+bytes(v,seen),32);
 }
 class BudgetCache {
  constructor(maxBytes=48*1024*1024,maxEntries=128){this.maxBytes=maxBytes;this.maxEntries=maxEntries;this.items=new Map();this.pins=new Set();this.bytes=0;this.hits=0;this.misses=0;this.evictions=0;}
  get size(){return this.items.size;}
  has(k){return this.items.has(k);}
  get(k){const e=this.items.get(k);if(!e){this.misses++;return undefined;}this.items.delete(k);this.items.set(k,e);this.hits++;return e.value;}
  peek(k){return this.items.get(k)?.value;}
  set(k,value){this.delete(k);const size=bytes(value);this.items.set(k,{value,size});this.bytes+=size;this.trim();return this;}
  delete(k){const e=this.items.get(k);if(!e)return false;this.bytes-=e.size;return this.items.delete(k);}
  pin(keys){this.pins=new Set(keys);this.trim();}
  trim(){for(const k of this.items.keys()){if(this.size<=this.maxEntries&&this.bytes<=this.maxBytes)break;if(!this.pins.has(k)){this.delete(k);this.evictions++;}}}
  clear(){this.items.clear();this.bytes=0;this.pins.clear();}
  keys(){return this.items.keys();}
  *values(){for(const e of this.items.values())yield e.value;}
  *entries(){for(const [k,e] of this.items)yield[k,e.value];}
  [Symbol.iterator](){return this.entries();}
  stats(){return{entries:this.size,bytes:this.bytes,budgetBytes:this.maxBytes,pinned:this.pins.size,overBudgetBytes:Math.max(0,this.bytes-this.maxBytes),hits:this.hits,misses:this.misses,evictions:this.evictions};}
 }
 class SpatialGrid {
  constructor(size=64){this.cellSize=size;this.cells=new Map();this.broad=[];this.count=0;}
  key(x,z){return Math.floor(x/this.cellSize)+':'+Math.floor(z/this.cellSize);}
  add(bounds,value){if(!bounds||!Object.values(bounds).every(Number.isFinite))throw Error('Invalid spatial bounds');const x0=Math.floor(bounds.minX/this.cellSize),x1=Math.floor(bounds.maxX/this.cellSize),z0=Math.floor(bounds.minZ/this.cellSize),z1=Math.floor(bounds.maxZ/this.cellSize);if((x1-x0+1)*(z1-z0+1)>4096)this.broad.push(value);else for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){const k=x+':'+z;if(!this.cells.has(k))this.cells.set(k,[]);this.cells.get(k).push(value);}this.count++;return this;}
  at(x,z){return [...new Set([...(this.cells.get(this.key(x,z))||[]),...this.broad])];}
  around(x,z,r=0){const values=new Set(this.broad);for(let a=Math.floor((x-r)/this.cellSize);a<=Math.floor((x+r)/this.cellSize);a++)for(let b=Math.floor((z-r)/this.cellSize);b<=Math.floor((z+r)/this.cellSize);b++)for(const v of this.cells.get(a+':'+b)||[])values.add(v);return[...values];}
 }
 function checkEmpty(proof,source,z,x,y){if(proof?.officialEmpty!==true)throw Error('Vide sans preuve explicite');for(const[k,v]of Object.entries({source,z,x,y}))if(k in proof&&proof[k]!==v)throw Error('Preuve vide associée à une autre coordonnée : '+k);if(proof.sha256&&proof.sha256!=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')throw Error('Empreinte du vide incorrecte');return true;}
 function sameFramePoint(a,b,epsilon=.01){return a.length===b.length&&a.every((v,i)=>Number.isFinite(v)&&Number.isFinite(b[i])&&Math.abs(v-b[i])<=epsilon);}
 function sha256(buffer){
  const data=buffer instanceof Uint8Array?buffer:new Uint8Array(buffer),n=data.length,len=Math.ceil((n+9)/64)*64,padded=new Uint8Array(len);padded.set(data);padded[n]=128;
  const view=new DataView(padded.buffer);view.setUint32(len-8,Math.floor(n/0x20000000));view.setUint32(len-4,(n*8)>>>0);
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2],H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],w=new Uint32Array(64),rr=(v,k)=>(v>>>k)|(v<<(32-k));
  for(let offset=0;offset<len;offset+=64){for(let i=0;i<16;i++)w[i]=view.getUint32(offset+4*i);for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(w[i-16]+(rr(a,7)^rr(a,18)^(a>>>3))+w[i-7]+(rr(b,17)^rr(b,19)^(b>>>10)))>>>0;}let[a,b,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const t1=(h+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^(~e&g))+K[i]+w[i])>>>0,t2=((rr(a,2)^rr(a,13)^rr(a,22))+((a&b)^(a&c)^(b&c)))>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}const v=[a,b,c,d,e,f,g,h];for(let i=0;i<8;i++)H[i]=(H[i]+v[i])>>>0;}
  return H.map(v=>v.toString(16).padStart(8,'0')).join('');
 }
 return{bytes,BudgetCache,SpatialGrid,checkEmpty,sameFramePoint,sha256};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralStream;
