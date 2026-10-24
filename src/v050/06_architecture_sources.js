/* Attributed architecture is an optional overlay. Official source geometry and
   cached WFS properties remain untouched. A site label is never a room plan. */
const MistralArchitectureSources=(()=>{
 const MAX_BYTES=1024*1024,MAX_RECORDS=128,EPS=1e-7;
 const finite=n=>typeof n==='number'&&Number.isFinite(n),clone=v=>JSON.parse(JSON.stringify(v));
 function fail(message){throw Error('Sources architecturales : '+message);}
 function text(value,name,max=2000){if(typeof value!=='string'||!value.trim()||value.length>max)fail(name+' absent ou trop long');return value.trim();}
 function source(raw){
  if(!raw||typeof raw!=='object')fail('attribution absente');
  const out=Object.fromEntries(['url','title','license','attribution','accessedAt'].map(k=>[k,text(raw[k],k)]));let u;
  try{u=new URL(out.url);}catch{fail('URL de provenance invalide');}
  if(u.protocol!=='https:'||u.username||u.password||!/^\d{4}-\d{2}-\d{2}(?:T|$)/.test(out.accessedAt))fail('provenance HTTPS ou date invalide');
  if(raw.responseSha256!==undefined){if(!/^[a-f0-9]{64}$/.test(raw.responseSha256))fail('empreinte de réponse invalide');out.responseSha256=raw.responseSha256;}
  return out;
 }
 function geometry(raw){
  if(!raw||!['Polygon','MultiPolygon'].includes(raw.type))fail('empreinte source requise');let count=0;
  const polygons=raw.type==='Polygon'?[raw.coordinates]:raw.coordinates;
  if(!Array.isArray(polygons)||!polygons.length||polygons.length>128)fail('polygones source hors budget');
  for(const polygon of polygons){if(!Array.isArray(polygon)||!polygon.length||polygon.length>128)fail('anneaux source invalides');
   for(const ring of polygon){if(!Array.isArray(ring)||ring.length<4)fail('anneau source ouvert');
    for(const p of ring){if(!Array.isArray(p)||![2,3].includes(p.length)||!p.every(finite)||Math.abs(p[0])>180||Math.abs(p[1])>90||++count>16384)fail('coordonnées source invalides');}
    if(ring[0][0]!==ring.at(-1)[0]||ring[0][1]!==ring.at(-1)[1])fail('anneau source ouvert');
   }
  }return JSON.stringify([raw.type,raw.coordinates]);
 }
 function component(raw){
  if(!raw||typeof raw.id!=='string'||!raw.id||raw.id.length>512||!finite(raw.baseY)||!finite(raw.height)||raw.height<=0||raw.height>1000||!Number.isInteger(raw.levels)||raw.levels<1||raw.levels>200||!Array.isArray(raw.rings)||!raw.rings.length)fail('liaison métrique du composant invalide');
  let count=0;for(const ring of raw.rings){if(!Array.isArray(ring)||ring.length<4)fail('anneau métrique invalide');for(const p of ring)if(!Array.isArray(p)||p.length!==2||!p.every(finite)||++count>16384)fail('anneau métrique hors budget');if(ring[0][0]!==ring.at(-1)[0]||ring[0][1]!==ring.at(-1)[1])fail('anneau métrique ouvert');}
  return clone(raw);
 }
 function sameRings(a,b){return a.length===b.length&&a.every((r,i)=>r.length===b[i].length&&r.every((p,j)=>p.every((n,k)=>Math.abs(n-b[i][j][k])<=EPS)));}
 function knownUse(properties){const normalized=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toLowerCase(),specific=v=>{const n=normalized(v);return !!n&&!/^(indifferenciee?|autre|inconnu|unknown|00|yes|true|batiment|building|bati|non renseigne|no|none)$/.test(n);};return ['usage_1','usage_2','building:use','building','amenity','shop'].some(k=>specific(properties[k]))||specific(properties.nature)&&!/industri.*agricol.*commercial/.test(normalized(properties.nature));}
 function matches(c,d){return c.id===d.id&&c.levels===d.levels&&Math.abs(c.baseY-d.baseY)<=EPS&&Math.abs(c.height-d.height)<=EPS&&sameRings(c.rings,d.rings);}
 function validate(raw,adapters){
  if(!raw||raw.schemaVersion!==1||raw.frame!=='engine-lambert93-metre'||!Array.isArray(raw.records)||raw.records.length>MAX_RECORDS||JSON.stringify(raw).length*2>MAX_BYTES)fail('atlas incompatible ou hors budget');
  const records=[],ids=new Set(),targets=new Set();
  for(const value of raw.records){
   const id=text(value?.id,'identifiant',160),target=value?.target;if(ids.has(id))fail('identifiant dupliqué');ids.add(id);
   if(!target||typeof target.cleabs!=='string'||!target.cleabs.trim()||target.cleabs.length>512)fail('identité IGN absente');
   const rawGeometry=geometry(target.rawGeometry),bound=target.component?component(target.component):null,key=target.cleabs+':'+(bound?.id||'*');if(targets.has(key))fail('cible architecturale dupliquée');targets.add(key);
   const entry={id,target:{cleabs:target.cleabs,rawGeometry:clone(target.rawGeometry),component:bound},geometryKey:rawGeometry,source:source(value.source)};
   if(value.label){const l=value.label;if(l.kind!=='site-context'||l.geometryFictive!==false||!finite(l.precisionMeters)||l.precisionMeters<0||l.precisionMeters>3||!finite(l.buildingOverlapRatio)||l.buildingOverlapRatio<.99-EPS||l.buildingOverlapRatio>1+EPS||l.centroidInside!==true)fail('association de site insuffisamment établie');entry.label={kind:l.kind,text:text(l.text,'libellé',240),siteName:text(l.siteName,'site',240),use:typeof l.use==='string'?l.use.slice(0,160):'',precisionMeters:l.precisionMeters,geometryFictive:false,buildingOverlapRatio:l.buildingOverlapRatio,centroidInside:true};}
   if(value.facadeDocument||value.interiorDocument){if(!bound||!adapters?.facades||!adapters?.interiors)fail('plans sans liaison métrique ni validateurs');
    const d={...bound,sourceId:target.cleabs,stableSourceId:target.cleabs,levelHeight:bound.height/bound.levels,properties:{},provenance:'source'};
    if(value.facadeDocument){const doc=adapters.facades.document(value.facadeDocument);if(!doc)fail('plan de façade invalide');source({url:doc.source,title:entry.source.title,license:doc.license,attribution:doc.attribution,accessedAt:doc.acquiredAt});const edges=new Map(adapters.facades.edges(d).map(e=>[e.ringIndex+':'+e.edgeIndex,e]));
     for(const o of doc.openings){const edge=edges.get(o.ringIndex+':'+o.edgeIndex);if(!edge||o.offset+o.width>edge.length+EPS||o.bottom+o.height>bound.height+EPS)fail('ouverture documentaire hors de la façade');}
     for(const e of doc.completeEdges)if(!edges.has(e.ringIndex+':'+e.edgeIndex))fail('face documentaire inconnue');entry.facadeDocument=clone(value.facadeDocument);
    }
    if(value.interiorDocument){const b=adapters.interiors.building(d);adapters.interiors.document(value.interiorDocument,b);entry.interiorDocument=clone(value.interiorDocument);}
   }
   if(!entry.label&&!entry.facadeDocument&&!entry.interiorDocument)fail('annotation vide');records.push(entry);
  }
  return{schemaVersion:1,frame:raw.frame,records};
 }
 class Registry{
  constructor(raw,adapters){const atlas=validate(raw,adapters);this.adapters=adapters;this.bySource=new Map();this.records=atlas.records;this.applied=new Set();this.rejected=new Map();for(const entry of this.records){const id=entry.target.cleabs;if(!this.bySource.has(id))this.bySource.set(id,[]);this.bySource.get(id).push(entry);}}
  apply(draw){
   const props=draw?.geoProperties,entries=this.bySource.get(props?.cleabs);if(!entries||!draw.sourceGeometry)return false;let key;try{key=geometry(draw.sourceGeometry);}catch{for(const entry of entries)this.rejected.set(entry.id,'source-geometry-invalid');return false;}let changed=false;
   for(const entry of entries){if(key!==entry.geometryKey){this.rejected.set(entry.id,'source-geometry-changed');continue;}
    const next={...draw.geoProperties};
    if(entry.label){if(!String(next.name||next.nom||next.nom_du_batiment||'').trim())next.name=entry.label.text;
     if(!knownUse(next)&&entry.label.use)next.architectureUse=entry.label.use;next.architectureSite={...entry.label,source:clone(entry.source)};
    }
    // Context can change an inferred floor count. Bind the final descriptor
    // before applying any part, so a plan cannot invalidate its own volume.
    if(entry.target.component){const d=this.adapters.facades.describe({...draw,geoProperties:next});if(!d||!matches(entry.target.component,d)){this.rejected.set(entry.id,'component-or-edge-order-changed');continue;}}
    for(const field of ['facadeDocument','interiorDocument'])if(entry[field]&&!next[field])next[field]=clone(entry[field]);
    draw.geoProperties=next;draw.v052ArchitectureSource={recordId:entry.id,source:clone(entry.source),scope:entry.label?'site-context-and-attributed-parts':'attributed-parts'};this.applied.add(entry.id);changed=true;
   }return changed;
  }
  info(){return{records:this.records.length,siteLabels:this.records.filter(r=>r.label).length,facadeDocuments:this.records.filter(r=>r.facadeDocument).length,interiorDocuments:this.records.filter(r=>r.interiorDocument).length,appliedRecords:this.applied.size,rejected:[...this.rejected].map(([id,reason])=>({id,reason}))};}
 }
 return{MAX_BYTES,MAX_RECORDS,EPS,source,geometry,component,sameRings,matches,validate,Registry};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralArchitectureSources;

if(typeof v046Import==='function'&&typeof window!=='undefined'){
 const clone=v=>JSON.parse(JSON.stringify(v));
 const runtime={promise:null,registry:null,loaded:false,missing:false,error:null,serial:0};
 function info(){return{loaded:runtime.loaded,missing:runtime.missing,error:runtime.error,...(runtime.registry?.info()||{records:0,siteLabels:0,facadeDocuments:0,interiorDocuments:0,appliedRecords:0,rejected:[]})};}
 async function ready(){
  if(!runtime.promise)runtime.promise=(async()=>{try{const raw=await v050LocalSourceJSON('data/map_pack/architecture/index.json',null,true);runtime.missing=raw===null;runtime.registry=new MistralArchitectureSources.Registry(raw||{schemaVersion:1,frame:'engine-lambert93-metre',records:[]},{facades:MistralFacades,interiors:MistralCityInteriors});runtime.loaded=true;if(!V046.lab&&world?.v046){let changed=false;for(const draw of world.staticDraws||[])if(draw.geoLayer==='building')changed=runtime.registry.apply(draw)||changed;if(changed){window.__MISTRAL_DEBUG?.v050FacadeRefresh?.();window.__MISTRAL_DEBUG?.v050CityInteriorBind?.();}}return info();}catch(error){runtime.error=String(error.message||error);throw error;}finally{window.dispatchEvent?.(new Event('mistral-architecture-ready'));}})();return runtime.promise;
 }
 const importing=v046Import;v046Import=function(...args){const result=importing(...args);if(!V046.lab&&runtime.registry)for(const draw of result.buildings||[])runtime.registry.apply(draw);return result;};
 const ensure=v046Ensure;v046Ensure=async function(...args){const serial=++runtime.serial;if(!V046.lab)try{await ready();}catch{if(typeof toast==='function')toast('Les sources architecturales locales ne sont pas valides. Leurs annotations ne sont pas appliquées.','bad');}if(serial!==runtime.serial)return false;return ensure(...args);};
 const cancel=v046Cancel;v046Cancel=function(...args){runtime.serial++;return cancel(...args);};
 globalThis.v052ArchitectureAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v052ArchitectureInfo:info,v052ArchitectureReady:ready,v052ArchitectureTarget:id=>{const draw=world?.staticDraws.find(d=>d.geoLayer==='building'&&[d.geoProperties?.cleabs,d.geoProperties?.sourceId,d.geoFeatureId,MistralFacades.describe(d)?.id].includes(id));if(!draw||!draw.sourceGeometry)return null;const d=MistralFacades.describe(draw);if(!d)return null;return{cleabs:draw.geoProperties.cleabs,rawGeometry:clone(draw.sourceGeometry),component:{id:d.id,baseY:d.baseY,height:d.height,levels:d.levels,rings:clone(d.rings)},annotation:clone({name:draw.geoProperties.name||draw.geoProperties.nom||null,architectureSite:draw.geoProperties.architectureSite||null,appliedSource:draw.v052ArchitectureSource||null})};}});ready().catch(()=>{});};
}
