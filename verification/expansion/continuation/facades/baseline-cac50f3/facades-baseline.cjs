/* Metric facade detail on the original building edges. Source footprints and
   collision solids are never replaced by boxes. Unless an attributed facade
   document supplies the opening, the architectural detail is authored fiction. */
const MistralFacades=(()=>{
 const EPS=1e-7,limit=(v,a,b)=>Math.max(a,Math.min(b,v));
 const finite=v=>typeof v==='number'&&Number.isFinite(v);
 function hash(value){let h=2166136261;for(const c of String(value))h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0;}
 function text(v){return typeof v==='string'?v.trim():'';}
 function inside(rings,x,z){let hit=false;for(const ring of rings){let part=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])part=!part;}if(part)hit=!hit;}return hit;}
 function normalized(raw){
  if(!Array.isArray(raw)||!raw.length||raw.length>256)return null;
  const rings=[];let vertices=0;
  for(const source of raw){if(!Array.isArray(source)||source.length<3)return null;const ring=[];
   for(const p of source){if(!Array.isArray(p)||!finite(p[0])||!finite(p[1]))return null;if(!ring.length||Math.hypot(p[0]-ring.at(-1)[0],p[1]-ring.at(-1)[1])>EPS)ring.push([p[0],p[1]]);}
   if(ring.length>1&&Math.hypot(ring[0][0]-ring.at(-1)[0],ring[0][1]-ring.at(-1)[1])<EPS)ring.pop();
   if(ring.length<3||ring.length>8192||(vertices+=ring.length)>16384)return null;
   let area=0;for(let i=0;i<ring.length;i++){const a=ring[i],b=ring[(i+1)%ring.length];area+=a[0]*b[1]-b[0]*a[1];}if(Math.abs(area)<EPS)return null;
   ring.push(ring[0].slice());rings.push(ring);
  }return rings;
 }
 function ringIdentity(ring){const a=ring.slice(0,-1),orders=[];for(const points of[a,a.slice().reverse()]){let at=0;for(let i=1;i<points.length;i++)if(points[i][0]<points[at][0]||points[i][0]===points[at][0]&&points[i][1]<points[at][1])at=i;orders.push(JSON.stringify(points.slice(at).concat(points.slice(0,at))));}return orders.sort()[0];}
 function geometryIdentity(rings){const value=JSON.stringify([ringIdentity(rings[0]),rings.slice(1).map(ringIdentity).sort()]);return hash(value).toString(16).padStart(8,'0')+hash('geometry:'+value).toString(16).padStart(8,'0');}
 const PALETTES={
  residential:{wall:[.73,.65,.52],trim:[.81,.76,.64],shutter:[.26,.37,.31],glass:[.14,.23,.23],iron:[.17,.20,.18]},
  industrial:{wall:[.53,.55,.51],trim:[.66,.67,.60],shutter:[.29,.35,.36],glass:[.19,.26,.27],iron:[.21,.24,.23]},
  commercial:{wall:[.68,.61,.48],trim:[.80,.73,.59],shutter:[.29,.38,.33],glass:[.13,.24,.25],iron:[.18,.21,.18]},
  civic:{wall:[.72,.70,.62],trim:[.84,.81,.70],shutter:[.31,.38,.35],glass:[.15,.22,.23],iron:[.20,.22,.20]},
  religious:{wall:[.75,.73,.65],trim:[.85,.82,.71],shutter:[.34,.35,.29],glass:[.20,.25,.28],iron:[.20,.20,.18]}
 };
 function style(properties={}){
  const type=['nature','usage_1','usage_2','building','amenity','shop'].map(k=>String(properties[k]||'')).join(' ').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  if(/religieu|eglise|chapelle|cathedral|church|mosque|synagogue/.test(type))return'religious';
  if(/industri|agricol|entrepot|warehouse|hangar|serre|greenhouse/.test(type))return'industrial';
  if(/commercial|commerce|magasin|shop|retail|restaurant/.test(type))return'commercial';
  if(/public|mairie|administr|ecole|school|hopital|hospital|musee|museum|gare|station/.test(type))return'civic';
  return'residential';
 }
 function document(raw){
  if(!raw||typeof raw!=='object'||raw.schemaVersion!==1||!['source','license','attribution','acquiredAt'].every(k=>text(raw[k])))return null;
  if(!Array.isArray(raw.openings)||raw.openings.length>2048)return null;
  const openings=[];
  for(const o of raw.openings){
   if(!o||!['door','window','shopfront'].includes(o.type)||!Number.isInteger(o.ringIndex??0)||!Number.isInteger(o.edgeIndex)||o.edgeIndex<0||!['offset','bottom','width','height'].every(k=>finite(o[k]))||o.offset<0||o.bottom<0||o.width<=0||o.height<=0)return null;
   openings.push({type:o.type,ringIndex:o.ringIndex??0,edgeIndex:o.edgeIndex,offset:o.offset,bottom:o.bottom,width:o.width,height:o.height});
  }
  const completeEdges=raw.completeEdges??[];if(!Array.isArray(completeEdges)||completeEdges.length>16384||completeEdges.some(e=>!e||!Number.isInteger(e.ringIndex)||e.ringIndex<0||!Number.isInteger(e.edgeIndex)||e.edgeIndex<0))return null;
  return{source:text(raw.source),license:text(raw.license),attribution:text(raw.attribution),acquiredAt:text(raw.acquiredAt),openings,completeEdges:completeEdges.map(e=>({ringIndex:e.ringIndex,edgeIndex:e.edgeIndex}))};
 }
 function describe(draw){
  if(!draw||draw.mesh!=='prism'||!finite(draw.baseY)||!finite(draw.height)||draw.height<=0||draw.height>1000)return null;
  const rings=normalized(draw.rings);if(!rings)return null;
  const properties=draw.geoProperties||{},sourceId=String(properties.sourceId||draw.geoFeatureId||draw.id||draw.v046GeometryId||'building'),declaredKey=text(properties.cleabs),stableSourceId=declaredKey&&declaredKey.length<=512?declaredKey:sourceId,id=stableSourceId+':'+geometryIdentity(rings);
  const levelsRaw=['building:levels','levels','nombre_d_etages'].map(k=>Number(properties[k])).find(n=>Number.isInteger(n)&&n>=1&&n<=200);
  // The original metric height is never stretched to fit a guessed floor count.
  const levels=levelsRaw||Math.max(1,Math.round(draw.height/(style(properties)==='industrial'?4.2:3.05)));
  const declared=!!levelsRaw,facadeDocument=document(properties.facadeDocument);
  const bounds={minX:Infinity,minZ:Infinity,maxX:-Infinity,maxZ:-Infinity};
  for(const r of rings)for(const p of r){bounds.minX=Math.min(bounds.minX,p[0]);bounds.maxX=Math.max(bounds.maxX,p[0]);bounds.minZ=Math.min(bounds.minZ,p[1]);bounds.maxZ=Math.max(bounds.maxZ,p[1]);}
  return{id,sourceId,stableSourceId,rings,baseY:draw.baseY,height:draw.height,levels,levelHeight:draw.height/levels,levelsBasis:declared?'source-declared':'invented',style:style(properties),properties,bounds,facadeDocument,provenance:facadeDocument?'mixed':'invented',heightBasis:draw.heightBasis||draw.sourceProfile?.basis||'existing-building-envelope'};
 }
 function edges(description){const out=[];for(let r=0;r<description.rings.length;r++){const ring=description.rings[r];let signed=0;for(let i=1;i<ring.length;i++)signed+=ring[i-1][0]*ring[i][1]-ring[i][0]*ring[i-1][1];const direction=(signed>0?1:-1)*(r===0?1:-1);for(let i=0;i<ring.length-1;i++){
  const a=ring[i],b=ring[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]);if(length<.08)continue;const tangent=[(b[0]-a[0])/length,(b[1]-a[1])/length],normal=[tangent[1]*direction,-tangent[0]*direction];
  out.push({ringIndex:r,edgeIndex:i,a:a.slice(),b:b.slice(),length,tangent,normal});
 }}return out;}
 function supportedOpening(o,e,d){return e&&o.offset+o.width<=e.length+EPS&&o.bottom+o.height<=d.height+EPS;}
 function entrances(draw){
  const d=draw?.rings&&draw.baseY!==undefined&&draw.height!==undefined&&draw.levelHeight?draw:describe(draw);if(!d||d.height<1.95)return[];
  const all=edges(d),edgeMap=new Map(all.map(e=>[e.ringIndex+':'+e.edgeIndex,e])),documented=[];
  for(const o of d.facadeDocument?.openings||[]){if(o.type!=='door'||o.ringIndex!==0)continue;const e=edgeMap.get(o.ringIndex+':'+o.edgeIndex);if(supportedOpening(o,e,d)&&o.bottom<=.35)documented.push({o,e});}
  const complete=new Set((d.facadeDocument?.completeEdges||[]).map(e=>e.ringIndex+':'+e.edgeIndex));
  const candidates=documented.length?documented:all.filter(e=>e.ringIndex===0&&e.length>=1.6&&!complete.has(e.ringIndex+':'+e.edgeIndex)).sort((a,b)=>b.length-a.length||Math.min(a.a[0],a.b[0])-Math.min(b.a[0],b.b[0])||Math.min(a.a[1],a.b[1])-Math.min(b.a[1],b.b[1])||Math.max(a.a[0],a.b[0])-Math.max(b.a[0],b.b[0])||Math.max(a.a[1],a.b[1])-Math.max(b.a[1],b.b[1])).map(e=>({e,o:null}));
  const result=[];
  for(const {e,o}of candidates.slice(0,64)){const width=o?.width??Math.min(d.style==='industrial'?2.4:1.15,e.length*.6),height=o?.height??Math.min(2.35,d.levelHeight-.08,d.height-.08),fractions=o?[(o.offset+o.width/2)/e.length]:[.5,.34,.66];
   if(height<1.85||width<.78)continue;
   for(const t of fractions){if(!o&&(d.facadeDocument?.openings||[]).some(known=>known.ringIndex===e.ringIndex&&known.edgeIndex===e.edgeIndex&&known.offset<t*e.length+width/2&&known.offset+known.width>t*e.length-width/2&&known.bottom<height))continue;const p=[e.a[0]+(e.b[0]-e.a[0])*t,e.a[1]+(e.b[1]-e.a[1])*t];let candidate=null;
    for(const inset of[.95,.7,.5]){const ip=[p[0]-e.normal[0]*inset,p[1]-e.normal[1]*inset],op=[p[0]+e.normal[0]*1.15,p[1]+e.normal[1]*1.15];
     if(!inside(d.rings,...ip)||inside(d.rings,...op))continue;
     // A player-width clearance must exist; a sliver is not an accessible room.
     if([-1,1].some(s=>!inside(d.rings,ip[0]+e.tangent[0]*.4*s,ip[1]+e.tangent[1]*.4*s)))continue;
     candidate={id:d.id+':entrance:'+e.ringIndex+':'+e.edgeIndex+':'+Math.round(t*10000),buildingId:d.id,center:[p[0],d.baseY+(o?.bottom||0),p[1]],outside:[op[0],d.baseY+(o?.bottom||0),op[1]],inside:[ip[0],d.baseY+(o?.bottom||0),ip[1]],tangent:e.tangent.slice(),normal:e.normal.slice(),ringIndex:0,edgeIndex:e.edgeIndex,width,height,offset:t*e.length-width/2,provenance:o?'documented':'invented',source:o?d.facadeDocument.source:null};break;
    }if(candidate){result.push(candidate);break;}
   }
  }return result;
 }
 function floorSchedule(d,selection){
  const levels=selection?.levelElevations;
  if(Array.isArray(levels)&&levels.length===d.levels&&levels.every(finite)&&Math.abs(levels[0])<EPS&&levels.every((y,i)=>y>=0&&y<d.height&&(i===0||y-levels[i-1]>=1.95-EPS))&&d.height-levels.at(-1)>=1.95-EPS)return levels.slice();
  return Array.from({length:d.levels},(_,i)=>i*d.levelHeight);
 }
 function selectedEntrance(door,selection,d,levelElevations){
  if(door.provenance==='documented')return door;
  const elevationOffset=selection?.elevationOffset??0;let height=selection?.height??door.height;
  if(!finite(elevationOffset)||elevationOffset<0||!finite(height)||height<1.85||height>door.height+EPS)return null;
  const floor=levelElevations.findIndex(y=>Math.abs(y-elevationOffset)<EPS);
  if(floor>=0)height=Math.min(height,(levelElevations[floor+1]??d.height)-elevationOffset-.08);
  if(height<1.85||elevationOffset+height>d.height+EPS)return null;
  const at=p=>[p[0],d.baseY+elevationOffset,p[2]];
  return{...door,height,elevationOffset,center:at(door.center),inside:at(door.inside),outside:at(door.outside)};
 }
 function facadePlan(draw,options={}){
  const d=describe(draw);if(!d)return null;const all=edges(d),candidates=entrances(d),selection=draw.v050EntranceSelection,levelElevations=floorSchedule(d,selection),doors=(selection===null?[]:selection?candidates.filter(door=>door.id===selection.id).slice(0,1):candidates.slice(0,1)).map(door=>selectedEntrance(door,selection,d,levelElevations)).filter(Boolean),openings=[],maxOpenings=limit(Math.floor(options.maxOpenings??512),1,4096),byEdge=new Map(all.map(e=>[e.ringIndex+':'+e.edgeIndex,e]));
  const occupied=new Map(),occupy=o=>{const key=o.ringIndex+':'+o.edgeIndex;if(!occupied.has(key))occupied.set(key,[]);occupied.get(key).push(o);};
  const documented=(d.facadeDocument?.openings||[]).slice().sort((a,b)=>(a.type==='door'?-1:0)-(b.type==='door'?-1:0));
  for(const door of doors)if(door.provenance==='invented'){const o={type:'door',ringIndex:0,edgeIndex:door.edgeIndex,offset:door.offset,bottom:door.elevationOffset,width:door.width,height:door.height,provenance:'invented',source:null};if(openings.length<maxOpenings)openings.push(o);occupy(o);}
  for(const o of documented){const e=byEdge.get(o.ringIndex+':'+o.edgeIndex);if(!supportedOpening(o,e,d))continue;const item={...o,provenance:'documented',source:d.facadeDocument.source};if(openings.length<maxOpenings)openings.push(item);occupy(item);}
  // Documented openings define only what is actually documented. Missing faces
  // and floors can be completed coherently, always with invented provenance.
  const seed=hash(d.id),bay=d.style==='industrial'?4.8:d.style==='religious'?4.2:2.8+(seed%50)/100,rows=[];let potentialOpenings=0;
  const complete=new Set((d.facadeDocument?.completeEdges||[]).map(e=>e.ringIndex+':'+e.edgeIndex));
  for(const e of all){if(e.length<1.45||complete.has(e.ringIndex+':'+e.edgeIndex))continue;const count=Math.min(160,Math.floor(e.length/bay));if(!count)continue;rows.push({edge:e,count,start:potentialOpenings,end:potentialOpenings+count*d.levels});potentialOpenings+=count*d.levels;}
  // Sample candidate indices directly. A complex 200-storey polygon never
  // materialises millions of window objects before the renderer's LOD budget.
  const remaining=maxOpenings-openings.length,sampleCount=Math.min(potentialOpenings,Math.max(0,remaining)),attempts=Math.min(potentialOpenings,Math.max(0,remaining*4)),visited=new Set();let rowIndex=0,attempted=0;
  for(let n=0;n<attempts&&openings.length<maxOpenings;n++){const slot=n%sampleCount,phase=Math.floor(n/sampleCount),index=Math.min(potentialOpenings-1,Math.floor(slot*potentialOpenings/sampleCount)+phase);if(slot===0)rowIndex=0;if(visited.has(index))continue;visited.add(index);while(rowIndex<rows.length&&index>=rows[rowIndex].end)rowIndex++;const row=rows[rowIndex];if(!row)break;attempted++;const e=row.edge,local=index-row.start,floor=Math.floor(local/row.count),column=local%row.count,step=e.length/row.count,levelHeight=(levelElevations[floor+1]??d.height)-levelElevations[floor],bottom=levelElevations[floor]+Math.min(.95,levelHeight*.29),height=Math.min(d.style==='religious'?2.25:1.55,levelHeight*.53),width=Math.min(d.style==='industrial'?2.2:1.12,step*.53),offset=step*(column+.5)-width/2;
   if(height<.5||bottom+height>d.height-.15||offset<.12||offset+width>e.length-.12)continue;
   const o={type:floor===0&&d.style==='commercial'?'shopfront':'window',ringIndex:e.ringIndex,edgeIndex:e.edgeIndex,offset,bottom,width,height,provenance:'invented',source:null};
   if((occupied.get(e.ringIndex+':'+e.edgeIndex)||[]).some(a=>a.offset<o.offset+o.width+.15&&a.offset+a.width+.15>o.offset&&a.bottom<o.bottom+o.height+.12&&a.bottom+a.height+.12>o.bottom))continue;
   openings.push(o);
  }
  return{...d,levelElevations,edges:all,doors,openings,seed,detailCoverage:{budgeted:attempted<potentialOpenings||documented.length>maxOpenings,potentialOpenings,attempted,maxOpenings,retainedOpenings:openings.length}};
 }
 function geometry(draw,options={}){
  const maxQuads=limit(Math.floor(options.maxQuads??512),8,4096),detail=options.detail!=='low',plan=facadePlan(draw,{maxOpenings:Math.min(2048,Math.max(1,Math.floor(maxQuads/(detail?6:1))))});if(!plan)return{draws:[],quads:0,openings:0,bytes:0};
  const groups=new Map(),palette=PALETTES[plan.style],shade=((plan.seed%21)-10)/550;
  const material=name=>name==='wall'?palette.wall.map(v=>limit(v+shade,0,1)):palette[name]||palette.trim;
  let quads=0,openingCount=0;const renderedOpenings=[];
  function quad(e,x0,y0,x1,y1,name,offset=.018){if(quads>=maxQuads||x1<=x0||y1<=y0)return false;let g=groups.get(name);if(!g){g={vertices:[],faces:[]};groups.set(name,g);}const at=(x,y)=>[e.a[0]+e.tangent[0]*x+e.normal[0]*offset,plan.baseY+y,e.a[1]+e.tangent[1]*x+e.normal[1]*offset],k=g.vertices.length;g.vertices.push(at(x0,y0),at(x1,y0),at(x1,y1),at(x0,y1));g.faces.push([k,k+1,k+2],[k,k+2,k+3]);quads++;return true;}
  // Every panel follows an actual outer or courtyard edge. The tiny offset is
  // a rendering separation only and never changes the measured footprint.
  const openingReserve=plan.openings.length?Math.min(maxQuads,Math.max(8,Math.min(Math.floor(maxQuads*.7),Math.min(plan.openings.length,16)*(detail?8:1)))):0,panelBudget=maxQuads-openingReserve;
  for(const e of plan.edges){if(quads>=panelBudget)break;quad(e,0,0,e.length,plan.height,'wall',.008);if(detail&&plan.height>3&&quads<panelBudget)quad(e,0,Math.max(.1,plan.height-.20),e.length,plan.height-.05,'trim',.024);}
  for(const o of plan.openings){const e=plan.edges.find(e=>e.ringIndex===o.ringIndex&&e.edgeIndex===o.edgeIndex);if(!e||quads+(detail?8:1)>maxQuads)continue;
   const x=o.offset,y=o.bottom,w=o.width,h=o.height;quad(e,x,y,x+w,y+h,o.type==='door'?'iron':'glass',.027);openingCount++;renderedOpenings.push({...o});
   if(!detail)continue;const trim=Math.min(.09,w*.075,h*.06),lo=Math.max(0,x-trim),hi=Math.min(e.length,x+w+trim),bottom=Math.max(0,y-trim),top=Math.min(plan.height,y+h+trim);
   quad(e,lo,bottom,x,top,'trim',.042);quad(e,x+w,bottom,hi,top,'trim',.042);quad(e,x,y+h,x+w,top,'trim',.042);if(y>0)quad(e,x,bottom,x+w,y,'trim',.042);
   if(o.type==='window'&&plan.style==='residential'&&o.provenance!=='documented'){const sw=Math.min(.30,w*.28);if(x-sw>.08)quad(e,x-sw,y,x-.03,y+h,'shutter',.038);if(x+w+sw<e.length-.08)quad(e,x+w+.03,y,x+w+sw,y+h,'shutter',.038);}
   if(o.type==='window'&&y>.4)quad(e,lo,Math.max(0,y-.13),hi,y-.06,'trim',.075);
  }
  const tile=draw.v046Tile||draw.geoTile||'facade:'+plan.id,center=[(plan.bounds.minX+plan.bounds.maxX)/2,plan.baseY+plan.height/2,(plan.bounds.minZ+plan.bounds.maxZ)/2];
  const draws=[...groups].map(([name,g])=>({mesh:'geoSurface',vertices:g.vertices,faces:g.faces,pos:center.slice(),scale:[1,1,1],color:material(name),alpha:1,revision:0,v046Tile:tile,v046GeometryId:'facade:'+plan.id+':'+name,id:'facade:'+plan.id+':'+name,v050Facade:true,geoLayer:'facade',facadeBuildingId:plan.id,facadeProvenance:plan.provenance,sourceProvenance:plan.facadeDocument?{source:plan.facadeDocument.source,license:plan.facadeDocument.license,attribution:plan.facadeDocument.attribution,acquiredAt:plan.facadeDocument.acquiredAt}:null,renderOffsetMeters:.075}));
  const bytes=draws.reduce((n,g)=>n+g.vertices.length*96+g.faces.length*96,0);
  return{draws,quads,openings:openingCount,renderedOpenings,bytes:bytes+renderedOpenings.length*256,description:{id:plan.id,sourceId:plan.sourceId,stableSourceId:plan.stableSourceId,style:plan.style,baseY:plan.baseY,height:plan.height,levels:plan.levels,levelHeight:plan.levelHeight,levelElevations:plan.levelElevations.slice(),provenance:plan.provenance,detailCoverage:plan.detailCoverage}};
 }
 function distance(bounds,x,z){return Math.hypot(Math.max(bounds.minX-x,0,x-bounds.maxX),Math.max(bounds.minZ-z,0,z-bounds.maxZ));}
 class Index{
  constructor(draws=[],size=96){this.size=size;this.cells=new Map();this.large=[];this.count=0;this.rebuild(draws);}
  rebuild(draws){this.cells.clear();this.large=[];this.count=0;const seen=new Set();for(const draw of draws){if(draw?.mesh!=='prism'||draw.geoLayer!=='building')continue;const d=describe(draw);if(!d||seen.has(d.id))continue;seen.add(d.id);this.count++;const item={draw,description:d},a=Math.floor(d.bounds.minX/this.size),b=Math.floor(d.bounds.maxX/this.size),c=Math.floor(d.bounds.minZ/this.size),e=Math.floor(d.bounds.maxZ/this.size);if((b-a+1)*(e-c+1)>128){this.large.push(item);continue;}for(let x=a;x<=b;x++)for(let z=c;z<=e;z++){const key=x+':'+z;if(!this.cells.has(key))this.cells.set(key,[]);this.cells.get(key).push(item);}}
  }
  around(x,z,radius=120,maxBuildings=48){const set=new Set(this.large);for(let a=Math.floor((x-radius)/this.size);a<=Math.floor((x+radius)/this.size);a++)for(let b=Math.floor((z-radius)/this.size);b<=Math.floor((z+radius)/this.size);b++)for(const item of this.cells.get(a+':'+b)||[])set.add(item);return[...set].map(item=>({...item,distance:distance(item.description.bounds,x,z)})).filter(item=>item.distance<=radius).sort((a,b)=>a.distance-b.distance||a.description.id.localeCompare(b.description.id)).slice(0,maxBuildings);}
 }
 class Cache{
  constructor(maxBytes=8*1024*1024,maxEntries=64){this.maxBytes=Math.max(1,maxBytes);this.maxEntries=Math.max(1,maxEntries);this.entries=new Map();this.bytes=0;this.hits=0;this.builds=0;this.evictions=0;}
  key(draw,options){return JSON.stringify([draw.geoProperties?.sourceId||draw.geoFeatureId||draw.v046GeometryId||draw.id,draw.baseY,draw.height,draw.rings,draw.geoProperties,draw.v050EntranceSelection??null,draw.v050EntranceSelection===undefined,options]);}
  get(draw,options={}){const key=this.key(draw,options);if(this.entries.has(key)){const value=this.entries.get(key);this.entries.delete(key);this.entries.set(key,value);this.hits++;return value;}const value=geometry(draw,options);value.bytes+=key.length*2+512;this.builds++;if(value.bytes>this.maxBytes)return value;while(this.entries.size>=this.maxEntries||this.bytes+value.bytes>this.maxBytes){const [first,old]=this.entries.entries().next().value;this.entries.delete(first);this.bytes-=old.bytes;this.evictions++;}this.entries.set(key,value);this.bytes+=value.bytes;return value;}
  clear(){this.entries.clear();this.bytes=0;}
 }
 return{hash,inside,normalized,geometryIdentity,style,document,describe,edges,entrances,floorSchedule,facadePlan,geometry,distance,Index,Cache};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralFacades;

function v050FacadesAfterInit(){
 if(typeof window==='undefined'||window.__mistralFacadesInstalled)return;window.__mistralFacadesInstalled=true;
 const runtime={world:null,source:null,index:null,cache:new MistralFacades.Cache(),draws:[],selection:[],live:new Map(),last:null,lastTime:0,stats:{buildings:0,visibleBuildings:0,quads:0,openings:0,fictionalBuildings:0,documentedBuildings:0}};
 const quality=()=>settings?.quality==='high'?{radius:145,buildings:64,quads:8192,perBuilding:512}:settings?.quality==='low'?{radius:65,buildings:24,quads:2048,perBuilding:256}:{radius:105,buildings:40,quads:4096,perBuilding:384};
 function reset(w){runtime.world=w;runtime.source=null;runtime.index=null;runtime.draws=[];runtime.selection=[];runtime.live=new Map();runtime.last=null;runtime.lastTime=0;runtime.cache.clear();runtime.stats={buildings:0,visibleBuildings:0,quads:0,openings:0,fictionalBuildings:0,documentedBuildings:0};}
 function refresh(force=false){
  if(!world?.v046||!world.geoMacro){if(runtime.world)reset(null);return[];}
  if(runtime.world!==world)reset(world);
  if(runtime.source!==world.staticDraws){runtime.source=world.staticDraws;runtime.index=new MistralFacades.Index(world.staticDraws);runtime.last=null;}
  const p=state.player.pos,o=quality(),now=Date.now();
  if(!force&&runtime.last&&runtime.last.quality===settings.quality&&Math.hypot(p[0]-runtime.last.x,p[2]-runtime.last.z)<3&&now-runtime.lastTime<1000)return runtime.draws;
  const selected=runtime.index.around(p[0],p[2],o.radius,o.buildings),draws=[],live=new Map();let quads=0,openings=0,visible=0,documented=0;
  for(const item of selected){const remaining=o.quads-quads;if(remaining<8)break;const result=runtime.cache.get(item.draw,{detail:item.distance>70?'low':'high',maxQuads:Math.min(o.perBuilding,remaining)});if(!result.draws.length)continue;draws.push(...result.draws);live.set(item.description.id,result);quads+=result.quads;openings+=result.openings;visible++;if(item.description.facadeDocument)documented++;}
  runtime.draws=draws;runtime.selection=selected;runtime.live=live;runtime.last={x:p[0],z:p[2],quality:settings.quality};runtime.lastTime=now;
  runtime.stats={buildings:runtime.index.count,visibleBuildings:visible,quads,openings,fictionalBuildings:visible-documented,documentedBuildings:documented};return draws;
 }
 const previousPublish=v046Publish;v046Publish=function(...args){const result=previousPublish(...args);if(args[0]===world)reset(world);return result;};
 const previousCollect=collectDraws;collectDraws=function(t){const draws=previousCollect(t);return draws.concat(refresh());};
 if(window.__MISTRAL_DEBUG)Object.assign(window.__MISTRAL_DEBUG,{
  v050FacadeInfo:()=>({...runtime.stats,cache:{bytes:runtime.cache.bytes,entries:runtime.cache.entries.size,hits:runtime.cache.hits,builds:runtime.cache.builds,evictions:runtime.cache.evictions},radius:quality().radius,selection:runtime.selection.slice(0,10).map(item=>({id:item.description.id,distance:item.distance,style:item.description.style,provenance:item.description.provenance})),limit:'Les détails inventés sont cohérents avec l’emprise et la hauteur disponibles ; ils ne constituent pas un relevé de façade.'}),
  v050FacadeRefresh:()=>{refresh(true);return runtime.stats;},
  v050FacadeDoors:()=>runtime.selection.flatMap(item=>MistralFacades.entrances(item.description)),
  v050FacadeBuilding:(id)=>{const item=runtime.selection.find(item=>item.description.id===id||item.description.sourceId===id||item.description.stableSourceId===id);if(!item)return null;const d=item.description,result=runtime.live.get(d.id);return{id:d.id,sourceId:d.sourceId,stableSourceId:d.stableSourceId,baseY:d.baseY,height:d.height,levels:d.levels,levelHeight:d.levelHeight,levelsBasis:d.levelsBasis,style:d.style,provenance:d.provenance,rings:d.rings.slice(0,32).map(r=>r.slice(0,2048).map(p=>p.slice())),ringsTruncated:d.rings.length>32||d.rings.some(r=>r.length>2048),rendered:!!result,openings:result?.renderedOpenings.slice(0,128)||[],openingsTruncated:(result?.renderedOpenings.length||0)>128,detailCoverage:result?.description.detailCoverage||null};}
 });
}
