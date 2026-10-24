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
 function words(value){return String(value||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
 function appearance(properties={}){
  // IGN's broad nature "Industriel, agricole ou commercial" is ambiguous.
  // A specific usage wins over that fallback instead of hiding shops/housing.
  for(const field of['usage_1','usage_2','architectureUse','building','amenity','shop','nature']){
   const value=words(properties[field]);if(!value.trim())continue;let name=null;
   if(/religieu|eglise|chapelle|cathedral|church|mosque|synagogue|culte/.test(value))name='religious';
   else if(/resident|habitat|appartement|apartments|house|residential|logement/.test(value))name='residential';
   else if(/public|mairie|administr|ecole|school|hopital|hospital|musee|museum|gare|station|sportif|tribune|gymnase/.test(value))name='civic';
   else if(field==='shop'&&!/^(no|none|vacant)$/.test(value)||/commerce|commercial|magasin|shop|retail|restaurant|bureau|service/.test(value)&&!/industri.*commercial/.test(value))name='commercial';
   else if(/industri|agricol|entrepot|warehouse|hangar|serre|greenhouse|silo/.test(value))name='industrial';
   if(name)return{style:name,basis:field};
  }return{style:'residential',basis:'invented-fallback'};
 }
 function style(properties={}){return appearance(properties).style;}
 function typology(properties={},category=style(properties)){
  const value=words([properties.nature,properties.building,properties.amenity,properties.usage_1,properties.usage_2,properties.architectureUse].join(' '));
  if(/serre|greenhouse/.test(value))return'greenhouse';
  if(/silo|chateau d.eau|reservoir|tour de refroidissement|cheminee/.test(value))return'technical-tower';
  if(/tribune|gradin|grandstand/.test(value))return'grandstand';
  if(category==='religious')return'nave';
  if(/hangar|entrepot|warehouse|hall industriel|halle|gymnase/.test(value))return'open-hall';
  if(/annexe|garage|carport/.test(value))return'annexe';
  return'stacked';
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
  const character=appearance(properties),volumeType=typology(properties,character.style),levelsRaw=['building:levels','levels','nombre_d_etages'].map(k=>Number(properties[k])).find(n=>Number.isInteger(n)&&n>=1&&n<=200);
  // The original metric height is never stretched to fit a guessed floor count.
  const levels=levelsRaw||(volumeType==='stacked'?Math.max(1,Math.round(draw.height/(character.style==='industrial'?4.2:3.05))):1);
  const declared=!!levelsRaw,facadeDocument=document(properties.facadeDocument);
  const bounds={minX:Infinity,minZ:Infinity,maxX:-Infinity,maxZ:-Infinity};
  for(const r of rings)for(const p of r){bounds.minX=Math.min(bounds.minX,p[0]);bounds.maxX=Math.max(bounds.maxX,p[0]);bounds.minZ=Math.min(bounds.minZ,p[1]);bounds.maxZ=Math.max(bounds.maxZ,p[1]);}
  return{id,sourceId,stableSourceId,rings,baseY:draw.baseY,height:draw.height,levels,levelHeight:draw.height/levels,levelsBasis:declared?'source-declared':'invented',levelInferenceBasis:declared?'source-declared':volumeType==='stacked'?'metric-height-estimate':'invented-functional-volume',typology:volumeType,style:character.style,styleBasis:character.basis,properties,bounds,facadeDocument,provenance:facadeDocument?'mixed':'invented',heightBasis:draw.heightBasis||draw.sourceProfile?.basis||'existing-building-envelope'};
 }
 function edges(description){const out=[];for(let r=0;r<description.rings.length;r++){const ring=description.rings[r];let signed=0;for(let i=1;i<ring.length;i++)signed+=ring[i-1][0]*ring[i][1]-ring[i][0]*ring[i-1][1];const direction=(signed>0?1:-1)*(r===0?1:-1);for(let i=0;i<ring.length-1;i++){
  const a=ring[i],b=ring[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]);if(length<EPS)continue;const tangent=[(b[0]-a[0])/length,(b[1]-a[1])/length],normal=[tangent[1]*direction,-tangent[0]*direction];
  out.push({ringIndex:r,edgeIndex:i,a:a.slice(),b:b.slice(),length,tangent,normal});
 }}return out;}
 function edgeKey(e){return e.ringIndex+':'+e.edgeIndex;}
 function surfaceBounds(e,lo,hi){
  lo=Math.max(0,lo);hi=Math.min(e.length,hi);if(hi-lo<EPS)return[0,-1];if(!e.pieces)return[0,0];
  let a=0,b=e.pieces.length;while(a<b){const m=(a+b)>>1;if(e.pieces[m].end<=lo+EPS)a=m+1;else b=m;}const first=a;
  a=first;b=e.pieces.length;while(a<b){const m=(a+b)>>1;if(e.pieces[m].start<hi-EPS)a=m+1;else b=m;}return[first,a-1];
 }
 function surfaceCount(e,lo,hi){const[a,b]=surfaceBounds(e,lo,hi);return Math.max(0,b-a+1);}
 function surfacePoint(e,offset){
  offset=limit(offset,0,e.length);if(!e.pieces)return{point:[e.a[0]+e.tangent[0]*offset,e.a[1]+e.tangent[1]*offset],tangent:e.tangent,normal:e.normal,edgeIndex:e.edgeIndex,sourceOffset:offset};
  const[a]=surfaceBounds(e,Math.min(offset,e.length-EPS*2),Math.min(e.length,offset+EPS*4)),part=e.pieces[Math.min(e.pieces.length-1,a)],local=limit(offset-part.start,0,part.source.length);
  return{point:[part.a[0]+part.tangent[0]*local,part.a[1]+part.tangent[1]*local],tangent:part.tangent,normal:part.source.normal,edgeIndex:part.source.edgeIndex,sourceOffset:part.forward?local:part.source.length-local};
 }
 function surfaceDistance(e,p){
  let best={distance:Infinity,offset:0};for(const part of e.pieces||[{source:e,a:e.a,b:e.b,tangent:e.tangent,start:0,end:e.length}]){const local=limit((p[0]-part.a[0])*part.tangent[0]+(p[1]-part.a[1])*part.tangent[1],0,part.source.length),distance=Math.hypot(p[0]-part.a[0]-part.tangent[0]*local,p[1]-part.a[1]-part.tangent[1]*local);if(distance<best.distance)best={distance,offset:part.start+local};}return best;
 }
 function curveSurfaces(d,all=edges(d)){
  const result=[];
  for(let ringIndex=0;ringIndex<d.rings.length;ringIndex++){
   const ring=all.filter(e=>e.ringIndex===ringIndex);if(ring.length<3)continue;
   const join=(a,b)=>a.length<2.8&&b.length<2.8&&Math.hypot(a.b[0]-b.a[0],a.b[1]-b.a[1])<EPS&&a.tangent[0]*b.tangent[0]+a.tangent[1]*b.tangent[1]>=Math.cos(Math.PI/4);
   let cut=ring.findIndex((e,i)=>!join(ring[(i+ring.length-1)%ring.length],e));if(cut<0)cut=0;
   const ordered=ring.slice(cut).concat(ring.slice(0,cut)),chains=[];let chain=[];
   for(const e of ordered){if(chain.length&&!join(chain.at(-1),e)){chains.push(chain);chain=[];}chain.push(e);}if(chain.length)chains.push(chain);
   for(const source of chains){if(source.length<3||source.reduce((n,e)=>n+e.length,0)<1.45)continue;let oriented=source.map(e=>({source:e,a:e.a,b:e.b,tangent:e.tangent,forward:true}));const closed=Math.hypot(source[0].a[0]-source.at(-1).b[0],source[0].a[1]-source.at(-1).b[1])<EPS,less=(a,b)=>a[0]<b[0]||a[0]===b[0]&&a[1]<b[1];
    const reverse=parts=>parts.slice().reverse().map(part=>({...part,a:part.b,b:part.a,tangent:part.tangent.map(v=>-v),forward:!part.forward}));
    if(closed){let start=0;for(let i=1;i<oriented.length;i++)if(less(oriented[i].a,oriented[start].a))start=i;oriented=oriented.slice(start).concat(oriented.slice(0,start));if(less(oriented.at(-1).a,oriented[0].b)){oriented=reverse(oriented);}}
    else if(less(oriented.at(-1).b,oriented[0].a))oriented=reverse(oriented);
    let length=0;for(const part of oriented){part.start=length;length+=part.source.length;part.end=length;}
    const signature=JSON.stringify([ringIndex===0?'outer':'courtyard',...oriented.map(part=>part.a),oriented.at(-1).b]),surfaceId='curve:'+hash(signature).toString(16).padStart(8,'0')+hash('surface:'+signature).toString(16).padStart(8,'0');
    result.push({ringIndex,edgeIndex:oriented[0].source.edgeIndex,surfaceId,a:oriented[0].a,b:oriented.at(-1).b,tangent:oriented[0].tangent,normal:oriented[0].source.normal,length,pieces:oriented,closed});
   }
  }return result;
 }
 function spanSummary(e,offset,width){
  if(!e.surfaceId)return null;const[a,b]=surfaceBounds(e,offset,offset+width);return{surfaceId:e.surfaceId,offsetMeters:offset,widthMeters:width,firstSourceEdgeIndex:e.pieces[a]?.source.edgeIndex??null,lastSourceEdgeIndex:e.pieces[b]?.source.edgeIndex??null,segments:Math.max(0,b-a+1)};
 }
 function sourceSpans(e,offset,width){
  if(!e.pieces)return[{ringIndex:e.ringIndex,edgeIndex:e.edgeIndex,offset,width}];const[first,last]=surfaceBounds(e,offset,offset+width),spans=[];
  for(let i=first;i<=last;i++){const part=e.pieces[i],lo=Math.max(offset,part.start)-part.start,hi=Math.min(offset+width,part.end)-part.start;spans.push({ringIndex:e.ringIndex,edgeIndex:part.source.edgeIndex,offset:part.forward?lo:part.source.length-hi,width:hi-lo});}return spans;
 }
 function openingSurface(o,byEdge,bySurface){return o.surfaceId?bySurface.get(o.surfaceId):byEdge.get(o.ringIndex+':'+o.edgeIndex);}
 function openingConflict(o,e,occupied,complete=null){
  // Check source segments incrementally, without expanding every curved span
  // into a retained array for each window in a high-complexity building.
  const check=(source,offset,width)=>complete?.has(edgeKey(source))||(occupied.get(edgeKey(source))||[]).some(a=>a.offset<offset+width+.15&&a.offset+a.width+.15>offset&&a.bottom<o.bottom+o.height+.12&&a.bottom+a.height+.12>o.bottom);
  if(!e.pieces)return check(e,o.offset,o.width);const[first,last]=surfaceBounds(e,o.offset,o.offset+o.width);
  for(let i=first;i<=last;i++){const part=e.pieces[i],lo=Math.max(o.offset,part.start)-part.start,hi=Math.min(o.offset+o.width,part.end)-part.start;if(check(part.source,part.forward?lo:part.source.length-hi,hi-lo))return true;}return false;
 }
 function supportedOpening(o,e,d){return e&&o.offset+o.width<=e.length+EPS&&o.bottom+o.height<=d.height+EPS;}
 function entrances(draw,options={}){
  const d=draw?.rings&&draw.baseY!==undefined&&draw.height!==undefined&&draw.levelHeight?draw:describe(draw);if(!d||d.height<1.95)return[];
  const all=edges(d),curves=curveSurfaces(d,all),edgeMap=new Map(all.map(e=>[edgeKey(e),e])),documented=[];
  for(const o of d.facadeDocument?.openings||[]){if(o.type!=='door'||o.ringIndex!==0)continue;const e=edgeMap.get(o.ringIndex+':'+o.edgeIndex);if(supportedOpening(o,e,d)&&o.bottom<=.35)documented.push({o,e});}
  const complete=new Set((d.facadeDocument?.completeEdges||[]).map(e=>e.ringIndex+':'+e.edgeIndex)),near=Array.isArray(options.near)&&options.near.length===2&&options.near.every(finite)?options.near:null,preferred=options.preferredEdge,preferredId=text(options.preferredId);
  const preferredSurface=e=>preferred&&preferred.ringIndex===e.ringIndex&&(e.edgeIndex===preferred.edgeIndex||e.pieces?.some(part=>part.source.edgeIndex===preferred.edgeIndex));
  const documentedId=item=>item.o?d.id+':entrance:'+item.e.ringIndex+':'+item.e.edgeIndex+':'+Math.round((item.o.offset+item.o.width/2)/item.e.length*10000):null;
  const approach=item=>item.o?Math.hypot(...surfacePoint(item.e,item.o.offset+item.o.width/2).point.map((v,i)=>v-near[i])):surfaceDistance(item.e,near).distance;
  const compare=(a,b)=>{const exact=Number(documentedId(b)===preferredId)-Number(documentedId(a)===preferredId);if(exact)return exact;const preferredOrder=Number(!!preferredSurface(b.e))-Number(!!preferredSurface(a.e));if(preferredOrder)return preferredOrder;if(near){const distance=approach(a)-approach(b);if(Math.abs(distance)>EPS)return distance;}return b.e.length-a.e.length||Math.min(a.e.a[0],a.e.b[0])-Math.min(b.e.a[0],b.e.b[0])||Math.min(a.e.a[1],a.e.b[1])-Math.min(b.e.a[1],b.e.b[1])||Math.max(a.e.a[0],a.e.b[0])-Math.max(b.e.a[0],b.e.b[0])||Math.max(a.e.a[1],a.e.b[1])-Math.max(b.e.a[1],b.e.b[1]);};
  // Width is limited to 60% of its supporting facade: 1.30m is the
  // geometric minimum for a .78m door. Clearance checks still decide access.
  const candidates=(documented.length?documented:all.concat(curves).filter(e=>e.ringIndex===0&&e.length>=1.3-EPS&&(!complete.has(edgeKey(e))||e.surfaceId)).map(e=>({e,o:null}))).sort(compare),known=new Map();
  for(const o of d.facadeDocument?.openings||[]){const key=o.ringIndex+':'+o.edgeIndex;if(!known.has(key))known.set(key,[]);known.get(key).push(o);}
  const result=[];
  for(const {e,o}of candidates.slice(0,64)){
   const width=o?.width??Math.min(d.style==='industrial'?2.4:1.15,e.length*.6),height=o?.height??Math.min(2.35,d.levelHeight-.08,d.height-.08);if(height<1.85||width<.78-EPS)continue;
   const idAt=t=>d.id+':entrance:'+(e.surfaceId?e.surfaceId+':'+Math.floor(t*Math.max(1,Math.floor(e.length/3.2))):e.ringIndex+':'+e.edgeIndex+':'+Math.round(t*10000));
   let fractions=o?[(o.offset+o.width/2)/e.length]:[.5,.34,.66];
   if(e.surfaceId&&!o){const count=Math.max(1,Math.floor(e.length/3.2)),at=near?Math.floor(surfaceDistance(e,near).offset/e.length*count):Math.floor(count/2),prefix=d.id+':entrance:'+e.surfaceId+':',preferredSlot=preferredId.startsWith(prefix)?Number(preferredId.slice(prefix.length)):null,slots=[...(Number.isInteger(preferredSlot)&&preferredSlot>=0&&preferredSlot<count?[preferredSlot]:[]),at,at-1,at+1,Math.floor(count/2),0,count-1];fractions=[...new Set(slots.filter(n=>n>=0&&n<count))].slice(0,7).map(n=>(n+.5)/count);}
   else if(!o)fractions.sort((a,b)=>Number(idAt(b)===preferredId)-Number(idAt(a)===preferredId)||(near?Math.hypot(...surfacePoint(e,a*e.length).point.map((v,i)=>v-near[i]))-Math.hypot(...surfacePoint(e,b*e.length).point.map((v,i)=>v-near[i])):0));
   for(const t of fractions){const offset=t*e.length-width/2;if(offset<0||offset+width>e.length+EPS)continue;const opening={ringIndex:e.ringIndex,edgeIndex:e.edgeIndex,offset,bottom:0,width,height};if(!o&&openingConflict(opening,e,known,complete))continue;const at=surfacePoint(e,t*e.length),p=at.point;let candidate=null;
    for(const inset of[.95,.7,.5]){const ip=[p[0]-at.normal[0]*inset,p[1]-at.normal[1]*inset],op=[p[0]+at.normal[0]*1.15,p[1]+at.normal[1]*1.15];if(!inside(d.rings,...ip)||inside(d.rings,...op))continue;if([-1,1].some(s=>!inside(d.rings,ip[0]+at.tangent[0]*.4*s,ip[1]+at.tangent[1]*.4*s)))continue;
     candidate={id:idAt(t),buildingId:d.id,center:[p[0],d.baseY+(o?.bottom||0),p[1]],outside:[op[0],d.baseY+(o?.bottom||0),op[1]],inside:[ip[0],d.baseY+(o?.bottom||0),ip[1]],tangent:at.tangent.slice(),normal:at.normal.slice(),ringIndex:0,edgeIndex:at.edgeIndex,width,height,offset,provenance:o?'documented':'invented',source:o?d.facadeDocument.source:null,...(e.surfaceId?{surfaceId:e.surfaceId,arclength:t*e.length,span:spanSummary(e,offset,width)}:{})};break;
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
 function windowRegisters(d,levels){
  if(d.typology==='technical-tower')return[];
  if(d.levels===1&&d.typology==='nave'&&d.height>6){const registers=[{storey:0,bottom:Math.min(2,d.height*.12),height:Math.min(8,d.height*.40),kind:'nave'}];if(d.height>10)registers.push({storey:0,bottom:d.height*.72,height:Math.min(2.4,d.height*.14),kind:'clerestory'});return registers;}
  if(d.levels===1&&d.typology==='grandstand')return[{storey:0,bottom:Math.min(2,d.height*.10),height:Math.min(2.6,d.height*.30),kind:'concourse'}];
  if(d.levels===1&&d.typology==='open-hall'&&d.height>7)return[{storey:0,bottom:1.25,height:1.4,kind:'hall'},{storey:0,bottom:d.height*.70,height:Math.min(1.55,d.height*.16),kind:'clerestory'}];
  return levels.map((bottom,storey)=>{const height=(levels[storey+1]??d.height)-bottom,shop=storey===0&&d.style==='commercial',greenhouse=d.typology==='greenhouse';return{storey,bottom:bottom+(shop||greenhouse?Math.min(.15,height*.06):Math.min(d.style==='industrial'?1.25:.95,height*.29)),height:Math.min(greenhouse?height*.82:shop?2.75:d.style==='religious'?2.25:1.55,height*(shop||greenhouse?.82:.53)),kind:greenhouse?'greenhouse':shop?'shopfront':'standard'};});
 }
 function program(draw){
  const d=describe(draw);if(!d)return null;
  const all=edges(d),curves=curveSurfaces(d,all),byEdge=new Map(all.map(e=>[edgeKey(e),e])),bySurface=new Map(curves.map(e=>[e.surfaceId,e])),selection=draw.v050EntranceSelection;
  // Interior08 may select a short nearby edge outside the canonical 64 longest
  // candidates. Recover that same physical candidate instead of losing its door.
  const candidates=entrances(d,{near:selection?.center?[selection.center[0],selection.center[2]]:null,preferredEdge:selection,preferredId:selection?.id}),levelElevations=floorSchedule(d,selection),doors=(selection===null?[]:selection?candidates.filter(door=>door.id===selection.id).slice(0,1):candidates.slice(0,1)).map(door=>selectedEntrance(door,selection,d,levelElevations)).filter(Boolean),fixed=[],occupied=new Map();
  const occupy=o=>{const e=openingSurface(o,byEdge,bySurface);if(!e)return;for(const span of sourceSpans(e,o.offset,o.width)){const key=edgeKey(span);if(!occupied.has(key))occupied.set(key,[]);occupied.get(key).push({...o,...span});}};
  for(const door of doors)if(door.provenance==='invented'){const o={type:'door',ringIndex:0,edgeIndex:door.edgeIndex,offset:door.offset,bottom:door.elevationOffset,width:door.width,height:door.height,provenance:'invented',source:null,...(door.surfaceId?{surfaceId:door.surfaceId,arclength:door.arclength,span:{...door.span}}:{})};fixed.push(o);occupy(o);}
  const documented=(d.facadeDocument?.openings||[]).slice().sort((a,b)=>(a.type==='door'?-1:0)-(b.type==='door'?-1:0));let rejectedDocumented=0;
  for(const o of documented){const e=byEdge.get(edgeKey(o));if(!supportedOpening(o,e,d)){rejectedDocumented++;continue;}const item={...o,provenance:'documented',source:d.facadeDocument.source};fixed.push(item);occupy(item);}
  const seed=hash(d.id),bay=d.style==='industrial'?4.8:d.style==='religious'?4.2:2.8+(seed%50)/100,registers=windowRegisters(d,levelElevations),rows=[],complete=new Set((d.facadeDocument?.completeEdges||[]).map(edgeKey)),curvedEdges=new Set(curves.flatMap(e=>e.pieces.map(part=>edgeKey(part.source))));let potentialOpenings=0;
  // Every source segment remains intact. Short consecutive segments may share
  // an arclength chart, so a circular source contour can carry a real-width bay.
  // The grid has no arbitrary column cap; bounded pages materialise its slots.
  const canonical=e=>{const forward=!!e.surfaceId||e.a[0]<e.b[0]||e.a[0]===e.b[0]&&e.a[1]<e.b[1],a=forward?e.a:e.b,b=forward?e.b:e.a;return{edge:e,reverse:!forward,key:[e.ringIndex===0?0:1,...a,...b,e.surfaceId||'']};};
  const ordered=all.filter(e=>!curvedEdges.has(edgeKey(e))).concat(curves).map(canonical).sort((a,b)=>{for(let i=0;i<a.key.length;i++)if(a.key[i]!==b.key[i])return typeof a.key[i]==='string'?a.key[i].localeCompare(b.key[i]):a.key[i]-b.key[i];return 0;});
  for(const item of ordered){const e=item.edge;if(e.length<1.45||!e.surfaceId&&complete.has(edgeKey(e)))continue;const count=Math.max(1,Math.floor(e.length/bay));const slots=count*registers.length;if(!Number.isSafeInteger(slots)||!Number.isSafeInteger(potentialOpenings+slots))return null;rows.push({edge:e,count,reverse:item.reverse,start:potentialOpenings,end:potentialOpenings+slots});potentialOpenings+=slots;}
  return{...d,edges:all,curves,doors,levelElevations,seed,bay,registers,rows,fixed,occupied,complete,potentialOpenings,totalSlots:fixed.length+potentialOpenings,documentedCoverage:{declared:documented.length,accepted:documented.length-rejectedDocumented,rejected:rejectedDocumented}};
 }
 function candidateAt(p,index){
  if(!Number.isSafeInteger(index)||index<0||index>=p.potentialOpenings)return null;
  let lo=0,hi=p.rows.length-1,row=null;while(lo<=hi){const mid=(lo+hi)>>1,r=p.rows[mid];if(index<r.start)hi=mid-1;else if(index>=r.end)lo=mid+1;else{row=r;break;}}
  if(!row)return null;const e=row.edge,local=index-row.start,register=p.registers[Math.floor(local/row.count)],canonicalColumn=local%row.count,column=row.reverse?row.count-1-canonicalColumn:canonicalColumn,step=e.length/row.count,shop=register.kind==='shopfront',greenhouse=register.kind==='greenhouse',bottom=register.bottom,height=register.height,width=Math.min(greenhouse?3.8:shop?2.6:p.style==='industrial'?2.2:1.12,step*(greenhouse?.86:shop?.74:.53)),offset=step*(column+.5)-width/2;
  if(height<.5||bottom+height>p.height-.15||offset<.12||offset+width>e.length-.12)return null;
  const at=e.surfaceId?surfacePoint(e,offset+width/2):null,o={type:shop?'shopfront':'window',ringIndex:e.ringIndex,edgeIndex:at?.edgeIndex??e.edgeIndex,offset,bottom,width,height,provenance:'invented',source:null,...(e.surfaceId?{surfaceId:e.surfaceId,arclength:offset+width/2,span:spanSummary(e,offset,width)}:{})};
  return openingConflict(o,e,p.occupied,p.complete)?null:o;
 }
 function inventory(p){return{schemaVersion:1,method:'Complete metric facade/storey bay program; openings materialised in bounded pages',totalSlots:p.totalSlots,fixedOpenings:p.fixed.length,potentialOpenings:p.potentialOpenings,eligibleEdges:p.rows.length,sourceEdges:p.edges.length,curvedSurfaces:p.curves.length,storeys:p.levels,typology:p.typology,levelInferenceBasis:p.levelInferenceBasis,windowRegisters:p.registers.length,baySpacingMeters:p.bay,documentedCoverage:{...p.documentedCoverage},provenance:p.provenance};}
 function openingSpans(draw,opening){
  const d=describe(draw);if(!d||!opening||!finite(opening.offset)||!finite(opening.width)||opening.offset<0||opening.width<=0)return[];
  const all=edges(d),e=opening.surfaceId?curveSurfaces(d,all).find(e=>e.surfaceId===opening.surfaceId):all.find(e=>e.ringIndex===opening.ringIndex&&e.edgeIndex===opening.edgeIndex);return e&&opening.offset+opening.width<=e.length+EPS?sourceSpans(e,opening.offset,opening.width):[];
 }
 function facadePage(draw,options={}){
  const p=program(draw);if(!p)return null;const cursor=options.cursor??0,size=options.limit??128;
  if(!Number.isSafeInteger(cursor)||cursor<0||cursor>p.totalSlots||!Number.isInteger(size)||size<1||size>4096)throw new RangeError('Facade page requires a valid slot cursor and 1..4096 openings');
  // Even a fully occupied/documented edge cannot force an unbounded search.
  // A page may contain fewer than limit openings; nextCursor still advances
  // over every examined slot, so collecting pages never drops a later storey.
  const scanLimit=Math.min(16384,Math.max(size,size*8)),openings=[];let nextCursor=cursor,scanned=0;
  while(nextCursor<p.totalSlots&&openings.length<size&&scanned<scanLimit){const index=nextCursor++,o=index<p.fixed.length?p.fixed[index]:candidateAt(p,index-p.fixed.length);scanned++;if(o)openings.push({...o});}
  return{buildingId:p.id,cursor,nextCursor,scanned,done:nextCursor===p.totalSlots,openings,inventory:inventory(p)};
 }
 function facadePlan(draw,options={}){
  const p=program(draw);if(!p)return null;const maxOpenings=limit(Math.floor(options.maxOpenings??512),1,4096),openings=p.fixed.slice(0,maxOpenings).map(o=>({...o})),remaining=Math.max(0,maxOpenings-openings.length),sampleCount=Math.min(p.potentialOpenings,remaining),attempts=Math.min(p.potentialOpenings,remaining*4),visited=new Set();let attempted=0;
  // The render LOD samples the complete program; it never substitutes a sparse
  // sample for the model's authoritative, cursor-addressable opening inventory.
  for(let n=0;n<attempts&&openings.length<maxOpenings;n++){const slot=n%sampleCount,phase=Math.floor(n/sampleCount),index=Math.min(p.potentialOpenings-1,Math.floor(slot*p.potentialOpenings/sampleCount)+phase);if(visited.has(index))continue;visited.add(index);attempted++;const o=candidateAt(p,index);if(o)openings.push(o);}
  return{...p,openings,openingInventory:inventory(p),detailCoverage:{budgeted:attempted<p.potentialOpenings||p.fixed.length>maxOpenings,potentialOpenings:p.potentialOpenings,attempted,maxOpenings,retainedOpenings:openings.length,completeInventorySlots:p.totalSlots,documentedCoverage:{...p.documentedCoverage}}};
 }
 function geometry(draw,options={}){
  const maxQuads=limit(Math.floor(options.maxQuads??512),8,4096),detail=options.detail!=='low',plan=facadePlan(draw,{maxOpenings:Math.min(2048,Math.max(1,Math.floor(maxQuads*(detail?.60:.85))))});if(!plan)return{draws:[],quads:0,openings:0,bytes:0};
  const groups=new Map(),palette=PALETTES[plan.style],shade=((plan.seed%21)-10)/550;
  const material=name=>name==='wall'?palette.wall.map(v=>limit(v+shade,0,1)):palette[name]||palette.trim;
  let quads=0,openingCount=0;const renderedOpenings=[],deferredOpenings=[],byEdge=new Map(plan.edges.map(e=>[edgeKey(e),e])),bySurface=new Map(plan.curves.map(e=>[e.surfaceId,e]));
  function fragment(e,x0,y0,x1,y1,name,offset){if(quads>=maxQuads||x1<=x0||y1<=y0)return false;let g=groups.get(name);if(!g){g={vertices:[],faces:[]};groups.set(name,g);}const at=(x,y)=>[e.a[0]+e.tangent[0]*x+e.normal[0]*offset,plan.baseY+y,e.a[1]+e.tangent[1]*x+e.normal[1]*offset],k=g.vertices.length;g.vertices.push(at(x0,y0),at(x1,y0),at(x1,y1),at(x0,y1));g.faces.push([k,k+1,k+2],[k,k+2,k+3]);quads++;return true;}
  function quad(e,x0,y0,x1,y1,name,offset=.018){
   if(!e||x1<=x0||y1<=y0)return false;if(!e.pieces)return fragment(e,x0,y0,x1,y1,name,offset);
   const[first,last]=surfaceBounds(e,x0,x1);let painted=false;
   for(let i=first;i<=last&&quads<maxQuads;i++){const part=e.pieces[i],lo=Math.max(x0,part.start)-part.start,hi=Math.min(x1,part.end)-part.start;painted=fragment(part.source,part.forward?lo:part.source.length-hi,y0,part.forward?hi:part.source.length-lo,y1,name,offset)||painted;}return painted;
  }
  // A curved opening is a set of quads on the original source segments. Reserve
  // all of them before panels/ornament; an opening never stops halfway through.
  const retained=[];let openingQuads=0;
  for(const o of plan.openings){const e=openingSurface(o,byEdge,bySurface),cost=e?surfaceCount(e,o.offset,o.offset+o.width):0;if(!cost||openingQuads+cost>maxQuads){deferredOpenings.push({...o,requiredQuads:cost,reason:cost?'quad-budget':'unsupported-source-surface'});continue;}retained.push({o,e});openingQuads+=cost;}
  const panelBudget=maxQuads-openingQuads;let panelEdges=0;
  for(const e of plan.edges){if(quads>=panelBudget)break;if(quad(e,0,0,e.length,plan.height,'wall',.008))panelEdges++;}
  // Glazing/door faces on every retained facade and storey precede decoration.
  for(const {o,e}of retained)if(quad(e,o.offset,o.bottom,o.offset+o.width,o.bottom+o.height,o.type==='door'?'iron':'glass',.027)){openingCount++;renderedOpenings.push({...o});}
  const baseQuads=quads;
  if(detail){
   for(const e of plan.edges){if(quads>=maxQuads)break;if(plan.height>3)quad(e,0,Math.max(.1,plan.height-.20),e.length,plan.height-.05,'trim',.024);}
   for(const o of renderedOpenings){const e=openingSurface(o,byEdge,bySurface),x=o.offset,y=o.bottom,w=o.width,h=o.height,trim=Math.min(.09,w*.075,h*.06),lo=Math.max(0,x-trim),hi=Math.min(e.length,x+w+trim),bottom=Math.max(0,y-trim),top=Math.min(plan.height,y+h+trim);if(quads>=maxQuads)break;
    quad(e,lo,bottom,x,top,'trim',.042);quad(e,x+w,bottom,hi,top,'trim',.042);quad(e,x,y+h,x+w,top,'trim',.042);if(y>0)quad(e,x,bottom,x+w,y,'trim',.042);
    if(o.type==='window'&&plan.style==='residential'&&o.provenance!=='documented'){const sw=Math.min(.30,w*.28);if(x-sw>.08)quad(e,x-sw,y,x-.03,y+h,'shutter',.038);if(x+w+sw<e.length-.08)quad(e,x+w+.03,y,x+w+sw,y+h,'shutter',.038);}
    if(o.type==='window'&&y>.4)quad(e,lo,Math.max(0,y-.13),hi,y-.06,'trim',.075);
    if(o.type==='shopfront'&&o.provenance==='invented'){quad(e,x+w/2-.025,y,x+w/2+.025,y+h,'iron',.045);if(top+.18<plan.height)quad(e,lo,top+.04,hi,top+.18,'shutter',.033);}
   }
   // The same floor schedule as interior08 aligns a sloping street entrance.
   for(let floor=1;floor<plan.levelElevations.length&&quads<maxQuads;floor++){const y=plan.levelElevations[floor];for(const e of plan.edges){if(quads>=maxQuads)break;quad(e,0,Math.max(0,y-.075),e.length,Math.min(plan.height,y-.025),'trim',.022);}}
  }
  const tile=draw.v046Tile||draw.geoTile||'facade:'+plan.id,center=[(plan.bounds.minX+plan.bounds.maxX)/2,plan.baseY+plan.height/2,(plan.bounds.minZ+plan.bounds.maxZ)/2];
  const draws=[...groups].map(([name,g])=>({mesh:'geoSurface',vertices:g.vertices,faces:g.faces,pos:center.slice(),scale:[1,1,1],color:material(name),alpha:1,revision:0,v046Tile:tile,v046GeometryId:'facade:'+plan.id+':'+name,id:'facade:'+plan.id+':'+name,v050Facade:true,geoLayer:'facade',facadeBuildingId:plan.id,facadeProvenance:plan.provenance,sourceProvenance:plan.facadeDocument?{source:plan.facadeDocument.source,license:plan.facadeDocument.license,attribution:plan.facadeDocument.attribution,acquiredAt:plan.facadeDocument.acquiredAt}:null,renderOffsetMeters:.075}));
  const bytes=draws.reduce((n,g)=>n+g.vertices.length*96+g.faces.length*96,0),detailCoverage={...plan.detailCoverage,renderedOpenings:openingCount,unrenderedPlannedOpenings:plan.openings.length-openingCount,deferredOpenings:deferredOpenings.length,openingQuads,panelEdges,totalFacadeEdges:plan.edges.length,decorationQuads:quads-baseQuads};
  return{draws,quads,openings:openingCount,renderedOpenings,deferredOpenings,bytes:bytes+(renderedOpenings.length+deferredOpenings.length)*512,description:{id:plan.id,sourceId:plan.sourceId,stableSourceId:plan.stableSourceId,style:plan.style,styleBasis:plan.styleBasis,typology:plan.typology,levelInferenceBasis:plan.levelInferenceBasis,baseY:plan.baseY,height:plan.height,levels:plan.levels,levelHeight:plan.levelHeight,levelElevations:plan.levelElevations.slice(),provenance:plan.provenance,openingInventory:plan.openingInventory,detailCoverage}};
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
 return{hash,inside,normalized,geometryIdentity,style,typology,document,describe,edges,curveSurfaces,openingSpans,entrances,floorSchedule,facadePlan,facadePage,geometry,distance,Index,Cache};
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
  if(force){runtime.source=null;runtime.cache.clear();}
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
  v050FacadePage:(id,cursor=0,limit=128)=>{const item=runtime.selection.find(item=>item.description.id===id||item.description.sourceId===id||item.description.stableSourceId===id);return item?MistralFacades.facadePage(item.draw,{cursor,limit}):null;},
  v050FacadeOpeningSpans:(id,opening)=>{const item=runtime.selection.find(item=>item.description.id===id||item.description.sourceId===id||item.description.stableSourceId===id);return item?MistralFacades.openingSpans(item.draw,opening):[];},
  v050FacadeBuilding:(id)=>{const item=runtime.selection.find(item=>item.description.id===id||item.description.sourceId===id||item.description.stableSourceId===id);if(!item)return null;const d=item.description,result=runtime.live.get(d.id);return{id:d.id,sourceId:d.sourceId,stableSourceId:d.stableSourceId,baseY:d.baseY,height:d.height,levels:d.levels,levelHeight:d.levelHeight,levelsBasis:d.levelsBasis,levelInferenceBasis:d.levelInferenceBasis,style:d.style,styleBasis:d.styleBasis,typology:d.typology,provenance:d.provenance,rings:d.rings.slice(0,32).map(r=>r.slice(0,2048).map(p=>p.slice())),ringsTruncated:d.rings.length>32||d.rings.some(r=>r.length>2048),rendered:!!result,openings:result?.renderedOpenings.slice(0,128)||[],openingsTruncated:(result?.renderedOpenings.length||0)>128,openingInventory:result?.description.openingInventory||MistralFacades.facadePage(item.draw,{limit:1})?.inventory||null,deferredOpenings:result?.deferredOpenings.slice(0,128)||[],deferredOpeningsTruncated:(result?.deferredOpenings.length||0)>128,detailCoverage:result?.description.detailCoverage||null};}
 });
}
