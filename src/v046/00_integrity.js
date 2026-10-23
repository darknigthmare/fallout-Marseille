/* Pure, independently testable continuity primitives. No global game mutation. */
const MistralIntegrity = (()=>{
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  function hash(value){let h=2166136261;const s=typeof value==='string'?value:JSON.stringify(value);for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619);return(h>>>0).toString(16).padStart(8,'0');}
  function ringKey(r){let a=r.map(p=>p.map(v=>Math.round(v*1000)/1000));if(a.length>1&&JSON.stringify(a[0])===JSON.stringify(a.at(-1)))a.pop();if(!a.length)return'';const candidates=[];for(const b of[a,a.slice().reverse()]){let m=0;for(let i=1;i<b.length;i++)if(JSON.stringify(b[i])<JSON.stringify(b[m]))m=i;candidates.push(JSON.stringify(b.slice(m).concat(b.slice(0,m))));}return candidates.sort()[0];}
  function footprintKey(source,rings,props={}){return source+':'+hash([rings.map(ringKey).sort(),['height','render_height','building:height','hauteur','z_min_sol','z_max_toit','altitude_minimale_sol','altitude_maximale_sol','altitude_minimale_toit','altitude_maximale_toit','ground_elevation','roof_elevation','levels','building:levels','nombre_d_etages','min_height','render_min_height','building:min_height','building:min_level','roof:height','roof:shape','roof:direction','width','largeur_de_chaussee','largeur_chaussee','lanes','nombre_de_voies','bridge','brunnel','position_par_rapport_au_sol','layer','ele','deck_height','sourceId'].map(k=>props[k]??null)]);}
  function inside(rings,x,z){function ring(r){let hit=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const a=r[i],b=r[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;}return !!rings.length&&ring(rings[0])&&!rings.slice(1).some(ring);}
  function intersects(a,b){return a[0]<b[2]&&a[2]>b[0]&&a[1]<b[3]&&a[3]>b[1];}
  function contains(b,lat,lon){return lat>=b[0]&&lat<=b[2]&&lon>=b[1]&&lon<=b[3];}
  /* Measurements are not parseFloat prefixes: an unknown unit must never turn
     into a plausible metre value. OSM feet/inches and decimal commas are explicit. */
  function metres(value){
    if(typeof value==='number')return Number.isFinite(value)?value:null;
    if(typeof value!=='string')return null;
    const s=value.trim(),feet=s.match(/^([+-]?\d+(?:[.,]\d+)?)\s*(?:ft|feet|'|′)(?:\s*(\d+(?:[.,]\d+)?)\s*(?:in|inches|"|″))?$/i);
    if(feet)return Number(feet[1].replace(',','.'))*.3048+(feet[2]?Number(feet[2].replace(',','.'))*.0254:0);
    const match=s.match(/^([+-]?\d+(?:[.,]\d+)?)\s*(m|metres?|mètres?|meters?|cm)?$/i);
    return match?Number(match[1].replace(',','.'))*(match[2]?.toLowerCase()==='cm'?.01:1):null;
  }
  function measurement(props,keys,min=0,max=1000){for(const key of keys){const n=metres(props[key]);if(n!==null&&n>=min&&n<=max)return{value:n,key};}return null;}
  function compatibleDatum(value){
    if(typeof value!=='string')return false;
    const text=value.trim().toUpperCase(),prefix=text.match(/^(?:NGF[\s_\/-]*IGN[\s_-]*(?:1969|69)|IGN[\s_-]*(?:1969|69)|EPSG\s*:\s*5720)/);
    if(!prefix)return false;const rest=text.slice(prefix[0].length).trim();return!rest||/^[—–,:;(\/-]/.test(rest);
  }
  function buildingProfile(props={}){
    const ground=measurement(props,['altitude_minimale_sol','z_min_sol','altitude_sol','ground_elevation'],-100,9000),groundMaximum=measurement(props,['altitude_maximale_sol','z_max_sol'],-100,9000),roofElevation=measurement(props,['altitude_maximale_toit','z_max_toit','altitude_toit','roof_elevation'],-100,10000),roofMinimum=measurement(props,['altitude_minimale_toit','z_min_toit'],-100,10000),supplied=measurement(props,['render_height','height','building:height','hauteur'],.1,1000),absoluteHeight=ground&&roofElevation&&roofElevation.value>ground.value&&roofElevation.value-ground.value<=1000?{value:roofElevation.value-ground.value,key:roofElevation.key+' − '+ground.key}:null,total=absoluteHeight||supplied,levels=measurement(props,['building:levels','levels','nombre_d_etages'],.1,200),roof=measurement(props,['roof:height'],0,200),lower=measurement(props,['render_min_height','min_height','building:min_height'],0,1000),minLevel=measurement(props,['building:min_level','min_level'],0,200);
    const top=total?.value??(levels?levels.value*3+(roof?.value||0):6),minimum=Math.min(lower?.value??(minLevel?minLevel.value*3:0),Math.max(0,top-.1));
    const roofHeight=Math.min(roof?.value||0,Math.max(0,top-minimum-.1)),shape=String(props['roof:shape']||'flat').toLowerCase(),direction=metres(props['roof:direction']);
    return{height:top-minimum,totalHeight:top,minHeight:minimum,groundElevation:ground?.value??null,groundMaximum:groundMaximum?.value??null,roofElevation:roofElevation?.value??null,roofMinimum:roofMinimum?.value??null,reportedHeight:supplied?.value??null,reportedHeightBasis:supplied?.key??null,eavesHeight:top-minimum-roofHeight,roofHeight,roofShape:shape,roofDirection:direction===null?null:((direction%360)+360)%360,estimated:!total,basis:total?.key||(levels?'niveaux × 3 m — estimation':'6 m par défaut — estimation'),minHeightBasis:lower?.key||(minLevel?'niveau inférieur × 3 m — estimation':'sol'),roofEstimated:!props['roof:shape']||roofHeight>0&&(!['flat','gabled','skillion'].includes(shape)||shape==='gabled'&&direction===null),roofRepresentation:props['roof:shape']?'Forme de toiture déclarée, construite avec ses dimensions disponibles':'Volume enveloppe ; la forme de la toiture n’est pas fournie',planimetricAccuracy:measurement(props,['precision_planimetrique'],0,100)?.value??null,altimetricAccuracy:measurement(props,['precision_altimetrique'],0,100)?.value??null};
  }
  function roadProfile(props={},water=false){
    const width=measurement(props,['width','largeur_de_chaussee','largeur_chaussee','largeur','est_width'],.05,300),lanes=measurement(props,['lanes','nombre_de_voies'],.1,30),cls=String(props.class||props.subclass||props.highway||'').toLowerCase(),trail=/path|track|footway/.test(cls),rail=/rail/.test(cls),arterial=/motorway|trunk|primary/.test(cls),absolute=measurement(props,['ele','deck_height','bridge:ele'],-100,9000),clearance=measurement(props,['bridge:height','min_height'],0,100),layer=Number(props.layer)||0,structure=String(props.brunnel||props.position_par_rapport_au_sol||'').toLowerCase(),bridge=/bridge|pont/.test(structure)||props.bridge==='yes'||props.bridge===true,tunnel=/tunnel|souterrain/.test(structure)||props.tunnel==='yes'||props.tunnel===true;
    const position=String(props.position_par_rapport_au_sol??'').trim(),ordinal=/^[+-]?\d+$/.test(position)&&Math.abs(Number(position))<100?Number(position):null,above=bridge||ordinal!==null&&ordinal>0,below=tunnel||ordinal!==null&&ordinal<0,isIGN=props.provenance?.resource==='ign-bdtopo',unavailableElevation=isIGN&&(above||below)&&!absolute&&!clearance;
    return{width:width?.value??(lanes?lanes.value*3.1:water?3:trail?1.6:rail?1.435:arterial?10:5.5),widthAssumed:!width,widthBasis:width?.key||(lanes?'voies × 3,1 m — estimation':'classe de voie — estimation'),absoluteHeight:absolute?.value??null,heightBasis:absolute?.key||clearance?.key||'terrain',offset:absolute?0:clearance?.value??(isIGN?0:above?Math.max(4,layer*4):below?-Math.max(4,Math.abs(layer)*4):0),elevationAssumed:!absolute&&!clearance,unavailableElevation,bridge:above,tunnel:below,sourcePosition:props.position_par_rapport_au_sol??null,ordinalPosition:ordinal,positionBasis:ordinal===null?null:'Ordre de superposition BD TOPO, sans unité métrique',planimetricAccuracy:measurement(props,['precision_planimetrique'],0,100)?.value??null,altimetricAccuracy:measurement(props,['precision_altimetrique'],0,100)?.value??null};
  }
  /* Stroke the unmodified source centreline. Mitred joins keep the specified
     width around normal bends; NoData removes faces instead of laying asphalt at zero. */
  function roadMesh(path,props,sample,water=false){
    const profile=roadProfile(props,water),points=[],validPath=(path||[]).filter(p=>Array.isArray(p)&&Number.isFinite(p[0])&&Number.isFinite(p[1]));
    for(let i=0;i<validPath.length-1;i++){const a=validPath[i],b=validPath[i+1],steps=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/12));for(let j=0;j<steps;j++){const t=j/steps,p=[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];if(Number.isFinite(a[2])&&Number.isFinite(b[2]))p[2]=a[2]+(b[2]-a[2])*t;points.push(p);}}
    if(validPath.length)points.push(validPath.at(-1).slice());
    const vertices=[],faces=[],valid=[],lift=water?.025:.085;
    for(let i=0;i<points.length;i++){
      const p=points[i],a=points[Math.max(0,i-1)],b=points[Math.min(points.length-1,i+1)],normal=(a,b)=>{const len=Math.hypot(b[0]-a[0],b[1]-a[1])||1;return[-(b[1]-a[1])/len,(b[0]-a[0])/len];},n0=normal(a,p),n1=normal(p,b);let nx=n0[0]+n1[0],nz=n0[1]+n1[1],len=Math.hypot(nx,nz);if(len<1e-8){[nx,nz]=normal(a,b);len=1;}nx/=len;nz/=len;const active=i===points.length-1?n0:n1,den=Math.abs(nx*active[0]+nz*active[1]),half=Math.min(profile.width*2,profile.width*.5/Math.max(.25,den));
      for(const side of[-1,1]){const x=p[0]+nx*half*side,z=p[1]+nz*half*side,ground=sample(x,z),height=Number.isFinite(p[2])?p[2]:profile.absoluteHeight!==null?profile.absoluteHeight:profile.unavailableElevation||ground===null?null:ground+profile.offset;vertices.push([x,height===null?0:height+lift,z]);valid.push(height!==null);}
      if(i){const k=i*2;if(valid[k-2]&&valid[k-1]&&valid[k])faces.push([k-2,k-1,k]);if(valid[k-1]&&valid[k+1]&&valid[k])faces.push([k-1,k+1,k]);}
    }
    if(validPath.length&&validPath.every(p=>Number.isFinite(p[2]))){profile.heightBasis='coordonnées Z source';profile.elevationAssumed=false;profile.unavailableElevation=false;}
    else if(validPath.some(p=>Number.isFinite(p[2]))){profile.heightBasis='coordonnées Z partielles et terrain';profile.elevationAssumed=true;}
    return{...profile,vertices,faces};
  }
  function roofMesh(rings,profile,ground,triangulate){
    if(!(profile.roofHeight>0)||!['gabled','skillion'].includes(profile.roofShape)||profile.roofDirection===null)return null;
    const axis=[Math.sin(profile.roofDirection*Math.PI/180),-Math.cos(profile.roofDirection*Math.PI/180)];let lo=Infinity,hi=-Infinity;
    for(const ring of rings)for(const p of ring){const projection=p[0]*axis[0]+p[1]*axis[1];lo=Math.min(lo,projection);hi=Math.max(hi,projection);}const middle=(lo+hi)/2;
    if(hi-lo<1e-6)return null;
    const signed=p=>p[0]*axis[0]+p[1]*axis[1]-middle,height=p=>ground+profile.minHeight+profile.eavesHeight+profile.roofHeight*(profile.roofShape==='gabled'?1-Math.abs(signed(p))/((hi-lo)/2):(hi-(p[0]*axis[0]+p[1]*axis[1]))/(hi-lo)),vertices=[],faces=[];
    const triangle=(a,b,c)=>{const k=vertices.length;vertices.push(a,b,c);faces.push([k,k+1,k+2]);};
    function clip(points,side){const out=[];for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length],da=signed(a)*side,db=signed(b)*side;if(da>=-1e-9)out.push(a);if((da>1e-9&&db< -1e-9)||(da< -1e-9&&db>1e-9)){const t=da/(da-db);out.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}}return out;}
    for(const t of triangulate(rings))for(const part of profile.roofShape==='gabled'?[clip(t,1),clip(t,-1)]:[t])for(let i=1;i<part.length-1;i++)triangle([part[0][0],height(part[0]),part[0][1]],[part[i+1][0],height(part[i+1]),part[i+1][1]],[part[i][0],height(part[i]),part[i][1]]);
    const eaves=ground+profile.minHeight+profile.eavesHeight;
    for(const ring of rings)for(let i=1;i<ring.length;i++){
      const a=ring[i-1],b=ring[i],points=[a];if(signed(a)*signed(b)<0){const t=signed(a)/(signed(a)-signed(b));points.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}points.push(b);
      for(let j=1;j<points.length;j++){const p=points[j-1],q=points[j];triangle([p[0],eaves,p[1]],[q[0],eaves,q[1]],[q[0],height(q),q[1]]);triangle([p[0],eaves,p[1]],[q[0],height(q),q[1]],[p[0],height(p),p[1]]);}
    }
    return{vertices,faces,sourceBasis:'forme, hauteur et direction de toiture déclarées'};
  }
  function terrain(raw,id,expected){
    const {width:w,height:h,bbox:b,values:v}=raw||{};
    if(raw?.macro!==id||!Number.isInteger(w)||!Number.isInteger(h)||w<2||h<2||w*h>1048576||!Array.isArray(v)||v.length!==w*h)throw new Error('Grille incomplète : '+id);
    if(!Array.isArray(b)||b.length!==4||!b.every(Number.isFinite)||b[0]>=b[2]||b[1]>=b[3]||expected&&b.some((x,i)=>Math.abs(x-expected[i])>1e-7))throw new Error('Emprise incompatible : '+id);
    const provenance=raw.provenance,declared=String(raw.sourceResource||raw.source_resource||raw.resource||'');
    const enrichment=id.startsWith('enrichment:')&&declared&&provenance&&['source','license','attribution','acquiredAt'].every(k=>typeof provenance[k]==='string'&&provenance[k].trim());
    if(declared!=='ign_rge_alti_wld'&&!enrichment&&!raw.qaFixture)throw new Error('Provenance altimétrique absente : '+id);
    if(enrichment&&!compatibleDatum(raw.verticalDatum||provenance?.verticalDatum))throw Error('Référentiel vertical incompatible : conversion explicite vers NGF-IGN69 requise pour '+id);
    if(raw.rowOrder&&raw.rowOrder!=='north-to-south')throw new Error('Ordre des lignes non pris en charge');
    const data=Float64Array.from(v,x=>x!==null&&typeof x==='number'&&Number.isFinite(x)&&x>-100&&x<9000?x:NaN);
    if(!data.some(Number.isFinite))throw new Error('Aucune altitude valide : '+id);
    const resolutionMeters=[(b[3]-b[1])*111320*Math.cos((b[0]+b[2])*Math.PI/360)/(w-1),(b[2]-b[0])*111320/(h-1)];
    return{id,width:w,height:h,bbox:b.slice(),data,qa:!!raw.qaFixture,enrichment:!!enrichment,sourceResource:declared,provenance:provenance?{...provenance}:null,verticalDatum:raw.verticalDatum||provenance?.verticalDatum||'NGF-IGN69 — RGE ALTI, France continentale',resolutionMeters};
  }
  function sample(t,lat,lon){if(!contains(t.bbox,lat,lon))return null;const b=t.bbox,x=clamp((lon-b[1])/(b[3]-b[1])*(t.width-1),0,t.width-1),y=clamp((b[2]-lat)/(b[2]-b[0])*(t.height-1),0,t.height-1),a=Math.floor(x),c=Math.floor(y),d=Math.min(t.width-1,a+1),e=Math.min(t.height-1,c+1),u=x-a,v=y-c;let sum=0,n=0;for(const[xx,yy,weight]of[[a,c,(1-u)*(1-v)],[d,c,u*(1-v)],[a,e,(1-u)*v],[d,e,u*v]]){if(weight<=1e-12)continue;const z=t.data[yy*t.width+xx];if(!Number.isFinite(z))return null;sum+=z*weight;n+=weight;}return n>0?sum/n:null;}
  class TerrainBank{
    constructor(bounds){this.bounds=Object.fromEntries(Object.entries(bounds).map(([k,b])=>[k,b.slice()]));this.grids=new Map();}
    add(raw,id){const t=terrain(raw,id,this.bounds[id]);if(!this.bounds[id])this.bounds[id]=t.bbox.slice();this.grids.set(id,t);return t;}
    required(b){return Object.keys(this.bounds).filter(id=>!id.startsWith('enrichment:')&&intersects(this.bounds[id],b)).sort();}
    read(lat,lon){const candidates=[],sources=[],noData=[];for(const id of Object.keys(this.bounds).sort()){const b=this.bounds[id];if(!contains(b,lat,lon))continue;if(!this.grids.has(id))return{height:null,missing:id,sources};const t=this.grids.get(id),height=sample(t,lat,lon);if(height===null){noData.push(id);continue;}candidates.push({id,t,height,resolution:t.resolutionMeters[0]*t.resolutionMeters[1]});}
      candidates.sort((a,b)=>a.resolution-b.resolution||Number(b.t.enrichment)-Number(a.t.enrichment)||a.id.localeCompare(b.id));const chosen=candidates[0];if(chosen)sources.push(chosen.id);return{height:chosen?.height??null,missing:null,sources,noData,resolutionMeters:chosen?.t.resolutionMeters.slice()||null,sourceResource:chosen?.t.sourceResource||null,interpolation:'bilinéaire, quatre échantillons valides requis',verticalDatum:chosen?.t.verticalDatum||null};}
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
  return{hash,ringKey,footprintKey,inside,intersects,contains,metres,compatibleDatum,buildingProfile,roadProfile,roadMesh,roofMesh,terrain,sample,TerrainBank,Gate};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralIntegrity;
