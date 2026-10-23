/* Metre based interiors for streamed source footprints. A source outline is
   preserved, including courtyards. Unrecorded layouts are explicitly invented;
   a documentary plan must carry its own source and is checked before use. */
const MistralCityInteriors=(()=>{
 const EPS=1e-7,MAX_POINTS=8192,MAX_LEVELS=512;
 const finite=n=>typeof n==='number'&&Number.isFinite(n),copy=v=>JSON.parse(JSON.stringify(v));
 function hash(value){let a=2166136261,b=2246822519;for(const c of JSON.stringify(value)){a=Math.imul(a^c.charCodeAt(0),16777619);b=Math.imul(b^c.charCodeAt(0),3266489917);}return(a>>>0).toString(16).padStart(8,'0')+(b>>>0).toString(16).padStart(8,'0');}
 function area(ring){let n=0;for(let i=0,j=ring.length-1;i<ring.length;j=i++)n+=ring[j][0]*ring[i][1]-ring[i][0]*ring[j][1];return n/2;}
 function bounds(rings){let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;for(const ring of rings)for(const[x,z]of ring){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minZ=Math.min(minZ,z);maxZ=Math.max(maxZ,z);}return{minX,maxX,minZ,maxZ,cx:(minX+maxX)/2,cz:(minZ+maxZ)/2};}
 function ringContains(ring,x,z){let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
 function inside(rings,x,z){return ringContains(rings[0],x,z)&&!rings.slice(1).some(r=>ringContains(r,x,z));}
 function segmentDistance(p,a,b){const dx=b[0]-a[0],dz=b[1]-a[1],t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/(dx*dx+dz*dz||1)));return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz);}
 function clearance(rings,x,z){let d=Infinity;for(const ring of rings)for(let i=0;i<ring.length;i++)d=Math.min(d,segmentDistance([x,z],ring[i],ring[(i+1)%ring.length]));return inside(rings,x,z)?d:d<EPS?0:-1;}
 function cleanRings(raw){
  if(!Array.isArray(raw)||!raw.length||raw.length>128)throw Error('Empreinte intérieure absente ou trop complexe');let count=0;
  const rings=raw.map(r=>{if(!Array.isArray(r))throw Error('Anneau intérieur invalide');const out=[];for(const p of r){if(!Array.isArray(p)||p.length<2||!p.slice(0,2).every(finite)||p.slice(0,2).some(n=>Math.abs(n)>1000000))throw Error('Coordonnée intérieure invalide');if(!out.length||Math.hypot(p[0]-out.at(-1)[0],p[1]-out.at(-1)[1])>EPS)out.push(p.slice(0,2));}if(out.length>1&&Math.hypot(out[0][0]-out.at(-1)[0],out[0][1]-out.at(-1)[1])<EPS)out.pop();count+=out.length;if(out.length<3||Math.abs(area(out))<.02)throw Error('Anneau intérieur dégénéré');return out;});
  if(count>MAX_POINTS)throw Error('Budget de l’empreinte intérieure dépassé');return rings;
 }
 function building(raw){
  if(!raw||typeof raw.id!=='string'||!raw.id.trim()||raw.id.length>512||!finite(raw.baseY)||!finite(raw.height)||raw.height<=0||raw.height>2000)throw Error('Volume de bâtiment invalide');
  const source=cleanRings(raw.rings),b=bounds(source),origin=[b.cx,raw.baseY,b.cz],rings=source.map(r=>r.map(p=>[p[0]-b.cx,p[1]-b.cz]));
  const levels=Number.isInteger(raw.levels)&&raw.levels>0?raw.levels:Math.max(1,Math.round(raw.height/3));if(levels>MAX_LEVELS)throw Error('Nombre de niveaux non pris en charge');if(raw.height/levels<1.95)throw Error('Le volume et les niveaux renseignés ne laissent pas la hauteur d’un personnage');
  const properties=raw.properties||{},use=String(properties.usage_1||properties['building:use']||properties.building||properties.nature||'').slice(0,160),name=String(properties.name||properties.nom||properties.nom_du_batiment||'Bâtiment').slice(0,160);
  const levelsBasis=properties.nombre_d_etages!=null?'nombre_d_etages IGN, rez-de-chaussée compris':properties['building:levels']!=null?'building:levels':'estimation du volume';
  return{id:raw.id,sourceId:String(raw.sourceId||raw.id).slice(0,512),name,origin,rings,height:raw.height,levels,levelHeight:raw.height/levels,use,levelsBasis,outlineBasis:raw.provenance||'empreinte source',schema:1};
 }
 function validateBuilding(raw){
  if(!raw||raw.schema!==1||typeof raw.id!=='string'||raw.id.length>512||!raw.id||!Array.isArray(raw.origin)||raw.origin.length!==3||!raw.origin.every(finite)||!finite(raw.height)||raw.height<=0||raw.height>2000||!Number.isInteger(raw.levels)||raw.levels<1||raw.levels>MAX_LEVELS)throw Error('Bâtiment sauvegardé invalide');
  const rings=cleanRings(raw.rings),b=bounds(rings);if(Math.max(b.maxX-b.minX,b.maxZ-b.minZ)>10000)throw Error('Emprise intérieure hors budget');if(raw.height/raw.levels<1.95)throw Error('Niveaux sauvegardés incompatibles avec leur volume');
  let levelElevations=null;if(raw.levelElevations!=null){if(!Array.isArray(raw.levelElevations)||raw.levelElevations.length!==raw.levels||raw.levelElevations.some(n=>!finite(n))||Math.abs(raw.levelElevations[0])>EPS)throw Error('Altitudes de planchers invalides');levelElevations=raw.levelElevations.slice();for(let i=0;i<raw.levels;i++)if((levelElevations[i+1]??raw.height)-levelElevations[i]<1.95-EPS)throw Error('Planchers inventés non praticables');}
  return{schema:1,id:raw.id,sourceId:String(raw.sourceId||raw.id).slice(0,512),name:String(raw.name||'Bâtiment').slice(0,160),origin:raw.origin.slice(),rings,height:raw.height,levels:raw.levels,levelHeight:raw.height/raw.levels,use:String(raw.use||'').slice(0,160),levelsBasis:String(raw.levelsBasis||'estimation').slice(0,160),outlineBasis:typeof raw.outlineBasis==='string'?raw.outlineBasis.slice(0,240):'empreinte source',...(levelElevations?{levelElevations}:{} )};
 }
 function point(rings,preferred=null,radius=.43){
  if(preferred&&clearance(rings,...preferred)>=radius)return preferred.slice();
  const b=bounds(rings);if(clearance(rings,b.cx,b.cz)>=radius)return[b.cx,b.cz];const w=b.maxX-b.minX,d=b.maxZ-b.minZ,nx=Math.max(1,Math.min(4096,Math.round(Math.sqrt(4096*w/d)))),nz=Math.max(1,Math.floor(4096/nx));let best=null,max=-1;
  for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){const x=b.minX+w*(i+.5)/nx,z=b.minZ+d*(j+.5)/nz,c=clearance(rings,x,z);if(c>=radius&&c>max){max=c;best=[x,z];}}
  return best;
 }
 function intervals(rings,axis,at){
  const fixed=axis==='x'?0:1,vary=1-fixed,cuts=[];
  for(const ring of rings)for(let i=0;i<ring.length;i++){const a=ring[i],b=ring[(i+1)%ring.length];if((a[fixed]>at)!==(b[fixed]>at))cuts.push(a[vary]+(b[vary]-a[vary])*(at-a[fixed])/(b[fixed]-a[fixed]));}
  cuts.sort((a,b)=>a-b);const out=[];for(let i=1;i<cuts.length;i++){const lo=cuts[i-1],hi=cuts[i],p=axis==='x'?[at,(lo+hi)/2]:[(lo+hi)/2,at];if(hi-lo>EPS&&inside(rings,...p))out.push([lo,hi]);}return out;
 }
 function inventedWalls(b,entry){
  const box=bounds(b.rings),axis=box.maxX-box.minX>=box.maxZ-box.minZ?'x':'z',lo=axis==='x'?box.minX:box.minZ,hi=axis==='x'?box.maxX:box.maxZ,walls=[];
  const count=Math.min(48,Math.max(0,Math.floor((hi-lo)/6)-1));
  for(let i=1;i<=count;i++){const at=lo+(hi-lo)*i/(count+1);for(const[a,c]of intervals(b.rings,axis,at)){
    if(c-a<2.4)continue;const gap=Math.min(1.4,(c-a)*.4),toPoint=q=>axis==='x'?[at,q]:[q,at],samples=Math.min(2048,Math.max(16,Math.ceil((c-a)/.25))),runs=[];let start=null,last=null;
    // A courtyard can split the actor's clearance along an otherwise solid
    // source band. Give each such circulation band its own doorway.
    for(let j=1;j<samples;j++){const q=a+(c-a)*j/samples,good=clearance(b.rings,...toPoint(q))>=.65;if(good){if(start===null)start=q;last=q;}if((!good||j===samples-1)&&start!==null){runs.push([start,last]);start=null;}}
    const gaps=runs.map(([lo,hi])=>{const center=(lo+hi)/2;return[Math.max(a+.1,center-gap/2),Math.min(c-.1,center+gap/2)];});if(!gaps.length)continue;let cursor=a;
    for(const[lo,hi]of[...gaps,[c,c]]){if(lo>cursor+.25){const p=toPoint(cursor),q=toPoint(lo);if(segmentDistance(entry,p,q)>=1.1)walls.push({a:p,b:q,thickness:.16,provenance:'invented'});}cursor=Math.max(cursor,hi);}
  }}return walls;
 }
 function publicSource(s){
  if(!s||!['url','license','attribution','title','accessedAt'].every(k=>typeof s[k]==='string'&&s[k].trim()&&s[k].length<=2000))throw Error('Le plan documentaire doit indiquer sa provenance complète');
  let u;try{u=new URL(s.url);}catch{throw Error('URL de provenance invalide');}if(u.protocol!=='https:'||u.username||u.password)throw Error('La provenance doit être une URL HTTPS publique sans identifiants');
  if(!/^\d{4}-\d{2}-\d{2}(?:T|$)/.test(s.accessedAt))throw Error('Date de consultation documentaire invalide');return Object.fromEntries(['url','license','attribution','title','accessedAt'].map(k=>[k,s[k]]));
 }
 function segmentInside(rings,a,b,margin=0){const n=Math.max(1,Math.ceil(Math.hypot(a[0]-b[0],a[1]-b[1])/.2));if(n>50000)return false;for(let i=0;i<=n;i++){const t=i/n,x=a[0]+(b[0]-a[0])*t,z=a[1]+(b[1]-a[1])*t;if(clearance(rings,x,z)<margin-EPS)return false;}return true;}
 function document(raw,b){
  if(!raw||raw.schemaVersion!==1||raw.frame!=='building-local-metre'||raw.buildingId!==b.id||!Array.isArray(raw.levels)||!raw.levels.length||raw.levels.length>b.levels)throw Error('Plan documentaire incompatible avec le bâtiment');
  const source=publicSource(raw.source),seen=new Set(),levels=[];
  for(const l of raw.levels){
   if(!Number.isInteger(l.level)||l.level<0||l.level>=b.levels||seen.has(l.level)||!finite(l.elevation)||!finite(l.height)||l.height<1.95||l.height>12||l.elevation<-.02||l.elevation+l.height>b.height+.25||!Array.isArray(l.walls)||l.walls.length>2048||!Array.isArray(l.rooms)||l.rooms.length>512)throw Error('Niveau documentaire invalide');seen.add(l.level);
   const walls=l.walls.map(w=>{if(!w||!Array.isArray(w.a)||!Array.isArray(w.b)||w.a.length!==2||w.b.length!==2||![...w.a,...w.b].every(finite)||!segmentInside(b.rings,w.a,w.b)||Math.hypot(w.a[0]-w.b[0],w.a[1]-w.b[1])<.05)throw Error('Mur documentaire hors emprise');return{a:w.a.slice(),b:w.b.slice(),thickness:finite(w.thickness)?Math.max(.06,Math.min(.8,w.thickness)):.16,provenance:'documented'};});
   const rooms=l.rooms.map(r=>{const rings=cleanRings([r.ring]);if(rings[0].some(p=>clearance(b.rings,...p)<-.001)||rings[0].some((p,i)=>!segmentInside(b.rings,p,rings[0][(i+1)%rings[0].length])))throw Error('Pièce documentaire hors emprise');return{id:String(r.id||'pièce').slice(0,160),use:String(r.use||'').slice(0,160),ring:rings[0]};});
   if(l.entry&&(!Array.isArray(l.entry)||l.entry.length!==2||!l.entry.every(finite)||clearance(b.rings,...l.entry)<.43))throw Error('Entrée documentaire impraticable');
   levels.push({level:l.level,elevation:l.elevation,height:l.height,walls,rooms,entry:l.entry?.slice()||null});
  }
  levels.sort((a,c)=>a.level-c.level);for(let i=1;i<levels.length;i++)if(levels[i].elevation<levels[i-1].elevation+levels[i-1].height-.1)throw Error('Niveaux documentaires superposés');
  const out={schemaVersion:1,frame:raw.frame,buildingId:b.id,source,levels};floorLevels(b,out);return out;
 }
 function floorLevels(b,doc=null){
  if(!doc)return b.levelElevations?.slice()||Array.from({length:b.levels},(_,i)=>i*b.levelHeight);
  const fixed=new Map([[0,0],[b.levels,b.height]]),put=(i,y)=>{if(fixed.has(i)&&Math.abs(fixed.get(i)-y)>.05)throw Error('Le plan et le volume source ont des planchers incompatibles');fixed.set(i,y);};
  for(const l of doc.levels){put(l.level,l.elevation);put(l.level+1,l.elevation+l.height);}
  const ordered=[...fixed].sort((a,c)=>a[0]-c[0]),out=Array(b.levels);
  for(let k=1;k<ordered.length;k++){const[a,y]=ordered[k-1],[c,z]=ordered[k],h=(z-y)/(c-a);if(h<1.95-EPS)throw Error('Les niveaux documentés ne laissent pas de hauteur praticable');for(let i=a;i<c;i++)out[i]=y+(i-a)*h;}return out;
 }
 function alignStreet(raw,groundY,doc=null){
  const b=validateBuilding(raw);if(!finite(groundY))return null;const relative=groundY-b.origin[1],grid=floorLevels(b,doc),near=grid.map((elevation,level)=>({elevation,level,distance:Math.abs(elevation-relative)})).sort((a,c)=>a.distance-c.distance||a.level-c.level)[0];
  if(near.distance<=.65)return{building:b,level:near.level,elevation:near.elevation,thresholdMeters:groundY-b.origin[1]-near.elevation};
  if(doc||relative<1.95||relative>b.height-1.95)return null;
  const candidates=[];for(let i=1;i<b.levels;i++)if(relative/i>=1.95&&(b.height-relative)/(b.levels-i)>=1.95)candidates.push(i);
  candidates.sort((a,c)=>Math.abs(a-relative/b.height*b.levels)-Math.abs(c-relative/b.height*b.levels)||a-c);if(!candidates.length)return null;const level=candidates[0],elevations=Array.from({length:b.levels},(_,i)=>i<=level?relative*i/level:relative+(i-level)*(b.height-relative)/(b.levels-level));
  return{building:validateBuilding({...b,levelElevations:elevations}),level,elevation:relative,thresholdMeters:0};
 }
 function theme(use){const t=String(use).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();return /hopital|medical|sante|clinique/.test(t)?'medical':/industri|entrepot|agric|hangar/.test(t)?'industrial':/commercial|commerce|bureau|service/.test(t)?'commercial':/eglise|relig|culte/.test(t)?'civic':'residential';}
 const FURNITURE={
  bed:{size:[1.55,2.05],height:.95,label:'Lit et chevet',zone:'Coin nuit'},
  sofa:{size:[1.9,.9],height:.95,label:'Canapé',zone:'Salon'},
  kitchen:{size:[1.9,.7],height:1.15,label:'Cuisine, évier et plaques',zone:'Coin cuisine'},
  sanitary:{size:[1.3,1.15],height:1.15,label:'WC et lavabo',zone:'Coin sanitaire'},
  wardrobe:{size:[1.15,.6],height:1.8,label:'Armoire',zone:'Rangement'},
  dining:{size:[1.5,1.35],height:.95,label:'Table et chaises',zone:'Coin repas'},
  desk:{size:[1.3,1.15],height:1.3,label:'Bureau et terminal',zone:'Bureau'},
  reception:{size:[1.9,.75],height:1.17,label:'Comptoir d’accueil',zone:'Accueil'},
  shelf:{size:[1.2,.55],height:1.75,label:'Rayonnage de commerce',zone:'Rayonnage'},
  workbench:{size:[1.8,.8],height:1.1,label:'Établi et étau',zone:'Atelier'},
  crate:{size:[1.25,1.05],height:1.4,label:'Caisses empilées',zone:'Logistique'},
  pallet:{size:[2,.9],height:1.75,label:'Rack et palettes',zone:'Stockage industriel'},
  medical_bed:{size:[.95,2.1],height:1,label:'Lit médical',zone:'Soins'},
  medical_cabinet:{size:[.95,.55],height:1.75,label:'Armoire de soins',zone:'Réserve médicale'},
  washbasin:{size:[.7,.55],height:1.15,label:'Poste de lavage',zone:'Hygiène'},
  bench:{size:[1.75,.6],height:1,label:'Banc',zone:'Attente'},
  lectern:{size:[.7,.6],height:1.2,label:'Pupitre',zone:'Salle commune'},
  archive:{size:[1.2,.55],height:1.75,label:'Étagères et registres',zone:'Archives'}
 };
 function program(use,level=0){
  const kind=theme(use);return(kind==='residential'?(level>0?['bed','wardrobe','sanitary','desk','sofa','kitchen','dining']:['bed','kitchen','sofa','sanitary','wardrobe','dining','desk']):kind==='medical'?['medical_bed','medical_cabinet','washbasin','desk','bench','medical_bed']:kind==='industrial'?['workbench','crate','pallet','wardrobe','desk','crate']:kind==='commercial'?['reception','shelf','desk','crate','shelf','bench']:['bench','lectern','archive','desk','wardrobe']).slice();
 }
 function roomProgram(room,base,level){
  const use=String(room?.use||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  if(/chambre|nuit|bed|sleep/.test(use))return['bed','wardrobe','desk'];
  if(/cuisine|kitchen|repas|dining/.test(use))return['kitchen','dining','wardrobe'];
  if(/bain|sanitaire|toilet|lavabo|bath/.test(use))return['sanitary','washbasin','wardrobe'];
  if(/salon|sejour|living/.test(use))return['sofa','dining','archive'];
  if(/bureau|office/.test(use))return['desk','archive','wardrobe'];
  return program(base,level);
 }
 /* Bounding rectangles include an aisle around each prop. Test their interior
    too: four corners alone can miss a courtyard contained in the rectangle. */
 function furnishingFits(l,x,z,size,other=[]){
  if(Math.hypot(x-l.entry[0],z-l.entry[1])<2.4||!walkable(l,x,z,Math.hypot(size[0]/2,size[1]/2)+1))return false;
  const hx=size[0]/2+.85,hz=size[1]/2+.85,nx=Math.max(2,Math.ceil(hx*2/.4)),nz=Math.max(2,Math.ceil(hz*2/.4));
  for(let i=0;i<=nx;i++)for(let j=0;j<=nz;j++)if(!walkable(l,x-hx+hx*2*i/nx,z-hz+hz*2*j/nz,.08))return false;
  return!other.some(f=>Math.hypot(Math.max(Math.abs(x-f.pos[0])-(size[0]+f.size[0])/2,0),Math.max(Math.abs(z-f.pos[1])-(size[1]+f.size[1])/2,0))<.95);
 }
 function furnish(l,b,recorded=false){
  const bb=bounds(l.rings),step=Math.max(3,Math.sqrt((bb.maxX-bb.minX)*(bb.maxZ-bb.minZ)/64)),points=[],preferred=program(b.use,l.level);
  for(const phase of[.5,.25,.75])for(let z=bb.minZ+step*phase;z<bb.maxZ;z+=step)for(let x=bb.minX+step*phase;x<bb.maxX;x+=step)points.push([x,z]);
  // A different floor keeps its own stable arrangement, without changing the
  // measured outline, existing walls or documented room geometry.
  const seed=parseInt(hash([b.id,l.level,'furnishing']).slice(0,6),16);if(seed%2)points.reverse();
  const furniture=[],zones=[],used=new Set();
  const place=(kind,p)=>{
   if(used.has(p)||furniture.length>=32)return false;const room=recorded?l.rooms.find(r=>inside([r.ring],...p)):null,def=FURNITURE[kind];
   if(recorded&&l.rooms.length&&!room||!roomProgram(room,b.use,l.level).includes(kind)||def.height>l.height-.1||!furnishingFits(l,...p,def.size,furniture))return false;
   if(room){const hx=def.size[0]/2+.03,hz=def.size[1]/2+.03;if([[-hx,-hz],[hx,-hz],[hx,hz],[-hx,hz]].some(([dx,dz])=>clearance([room.ring],p[0]+dx,p[1]+dz)<0))return false;}
   const selected={id:'furnishing:'+hash([b.id,l.level,p,kind]),pos:p.slice(),kind,size:def.size.slice(),height:def.height,label:def.label,zone:def.zone,roomId:room?.id||null,provenance:'invented',seed:parseInt(hash([b.id,l.level,p,kind]).slice(0,6),16)};used.add(p);furniture.push(selected);const[x,z]=p,[sx,sz]=selected.size,hx=sx/2+.25,hz=sz/2+.25;
   zones.push({id:'invented-zone:'+selected.id,use:selected.zone,ring:[[x-hx,z-hz],[x+hx,z-hz],[x+hx,z+hz],[x-hx,z+hz],[x-hx,z-hz]],anchor:p.slice(),provenance:'invented',coverage:'partial'});
   return true;
  };
  // Reserve space for different essential uses before repeating racks or beds.
  const goals=[...new Set(recorded&&l.rooms.length?l.rooms.flatMap(r=>roomProgram(r,b.use,l.level)):preferred)];
  for(const kind of goals)for(const p of points)if(place(kind,p))break;
  for(const p of points){if(furniture.length>=32)break;const room=recorded?l.rooms.find(r=>inside([r.ring],...p)):null,choices=roomProgram(room,b.use,l.level),n=furniture.length;for(let i=0;i<choices.length;i++)if(place(choices[(n+i)%choices.length],p))break;}
  return{furniture,zones,program:preferred};
 }
 /* Small distinct models use at most ten boxes each. The declared footprint
    and top bound every visible part and the actor's conservative solid. */
 function furnitureModel(f){
  const d=FURNITURE[f.kind];if(!d)throw Error('Mobilier inconnu');const out=[],box=(pos,size,material)=>out.push({pos,size,material}),kind=f.kind;
  if(kind==='bed'||kind==='medical_bed'){
   const[sx,sz]=d.size;box([0,.22,0],[sx,.28,sz],'metal');box([0,.5,0],[sx-.08,.25,sz-.1],kind==='medical_bed'?'medical':'fabric');box([0,.72,-sz*.31],[sx-.18,.18,.42],'paper');box([0,d.height/2,-sz/2+.04],[sx,d.height,.08],'wood');box([0,.64,sz*.16],[sx-.12,.06,sz*.55],kind==='medical_bed'?'medical':'blanket');
  }else if(kind==='sofa'){
   box([0,.25,0],[1.9,.35,.9],'wood');box([0,.7,-.34],[1.9,.5,.22],'fabric');box([-.84,.54,0],[.22,.38,.9],'fabric');box([.84,.54,0],[.22,.38,.9],'fabric');for(const x of[-.39,.39])box([x,.48,.08],[.72,.17,.66],'blanket');
  }else if(kind==='kitchen'){
   box([0,.43,0],[1.9,.86,.7],'wood');box([0,.91,0],[1.9,.1,.7],'porcelain');box([-.48,.973,0],[.62,.026,.48],'dark');box([-.48,.986,0],[.42,.025,.28],'water');box([.43,.973,0],[.58,.026,.5],'metal');for(const x of[.28,.58])box([x,1.002,0],[.18,.03,.28],'dark');box([-.48,1.07,-.27],[.055,.16,.055],'metal');box([-.48,1.13,-.2],[.055,.04,.18],'metal');
  }else if(kind==='sanitary'||kind==='washbasin'){
   if(kind==='sanitary'){box([-.35,.35,.14],[.52,.7,.72],'porcelain');box([-.35,.83,-.42],[.52,.34,.3],'porcelain');box([-.35,.72,.16],[.47,.05,.58],'dark');}
   const x=kind==='sanitary'?.4:0,sx=kind==='sanitary'?.5:.7,sz=kind==='sanitary'?.48:.55,z=kind==='sanitary'?-.1:0;box([x,.4,z],[sx,.8,sz],'wood');box([x,.83,z],[sx,.06,sz],'porcelain');box([x,.87,z],[sx*.65,.025,sz*.65],'dark');box([x,1.02,kind==='sanitary'?-.29:-.22],[.05,.26,.05],'metal');
  }else if(kind==='dining'){
   box([0,.77,0],[1.5,.1,.72],'wood');for(const x of[-.57,.57])box([x,.38,0],[.12,.76,.5],'wood');for(const z of[-.53,.53]){box([0,.42,z],[.54,.08,.29],'wood');box([0,.72,z+(z>0?.1:-.1)],[.54,.46,.09],'wood');}
  }else if(kind==='desk'){
   box([0,.78,-.2],[1.3,.12,.75],'wood');for(const x of[-.52,.52])box([x,.36,-.2],[.12,.72,.65],'metal');box([0,.96,-.35],[.54,.24,.24],'dark');box([0,1.21,-.4],[.56,.18,.12],'glass');box([0,.43,.42],[.5,.12,.3],'wood');box([0,.74,.53],[.5,.42,.09],'fabric');
  }else if(kind==='reception'){
   box([0,.5,0],[1.9,1,.7],'wood');box([0,1.07,0],[1.9,.1,.75],'porcelain');box([0,.66,.36],[1.5,.15,.025],'amber');box([.55,1.145,-.2],[.3,.05,.22],'dark');
  }else if(['wardrobe','medical_cabinet'].includes(kind)){
   const[sx,sz]=d.size;box([0,d.height/2,0],[sx,d.height,sz],'metal');for(const x of[-sx*.245,sx*.245]){box([x,d.height*.52,sz/2-.035],[sx*.46,d.height*.92,.05],kind==='medical_cabinet'?'medical':'wood');box([x+(x<0?.12:-.12),d.height*.52,sz/2-.008],[.025,.2,.015],'dark');}if(kind==='medical_cabinet'){box([0,d.height*.69,sz/2-.004],[.34,.09,.008],'paper');box([0,d.height*.69,sz/2-.004],[.09,.34,.008],'paper');}
  }else if(['shelf','archive','pallet'].includes(kind)){
   const[sx,sz]=d.size;for(const x of[-sx/2+.04,sx/2-.04])box([x,d.height/2,0],[.08,d.height,sz],'metal');for(const y of[.12,.62,1.12,1.62])box([0,y,0],[sx,.08,sz],'wood');for(const y of[.36,.87,1.37])box([0,y,0],[sx*.7,.38,sz*.75],kind==='archive'?'paper':kind==='pallet'?'wood':'fabric');
  }else if(kind==='workbench'){
   box([0,.82,0],[1.8,.14,.8],'wood');for(const x of[-.72,.72])for(const z of[-.28,.28])box([x,.38,z],[.12,.76,.12],'metal');box([.5,1.0,-.1],[.34,.2,.3],'metal');box([-.45,.98,0],[.5,.18,.4],'amber');
  }else if(kind==='crate'){
   box([0,.38,0],[1.25,.76,1.05],'wood');box([0,1.08,0],[1.05,.64,.88],'wood');for(const x of[-.44,.44])box([x,.38,.515],[.07,.7,.02],'metal');for(const x of[-.35,.35])box([x,1.08,.43],[.06,.6,.02],'metal');
  }else if(kind==='bench'){
   box([0,.46,0],[1.75,.1,.6],'wood');box([0,.75,-.24],[1.75,.5,.12],'wood');for(const x of[-.63,.63])box([x,.22,0],[.12,.44,.48],'metal');
  }else if(kind==='lectern'){
   box([0,.08,0],[.7,.16,.6],'wood');box([0,.6,0],[.22,1.04,.24],'wood');box([0,1.15,0],[.7,.1,.6],'wood');box([0,1.19,0],[.36,.02,.35],'paper');
  }
  return out;
 }
 function walkable(layout,x,z,radius=.38){if(clearance(layout.rings,x,z)<radius)return false;return !layout.walls.some(w=>segmentDistance([x,z],w.a,w.b)<radius+w.thickness/2-EPS);}
 function canTravel(layout,from,to,radius=.38){const distance=Math.hypot(to[0]-from[0],to[1]-from[1]);if(distance>400)return false;const n=Math.max(1,Math.ceil(distance/.15));for(let i=0;i<=n;i++)if(!walkable(layout,from[0]+(to[0]-from[0])*i/n,from[1]+(to[1]-from[1])*i/n,radius))return false;return true;}
 function layout(b,level=0,entry=null,doc=null){
  b=validateBuilding(b);if(!Number.isInteger(level)||level<0||level>=b.levels)throw Error('Étage intérieur invalide');
  const checked=doc?document(doc,b):null,recorded=checked?.levels.find(l=>l.level===level),grid=floorLevels(b,checked),start=point(b.rings,recorded?.entry||entry,.43);
  if(!start)throw Error('L’emprise ne contient pas d’espace praticable pour un personnage');
  const walls=recorded?recorded.walls:inventedWalls(b,start),result={buildingId:b.id,level,rings:copy(b.rings),height:(grid[level+1]??b.height)-grid[level],elevation:grid[level],walls,entry:start,theme:theme(b.use),rooms:recorded?.rooms||[],provenance:recorded?'documented':'invented',source:recorded?doc.source:null,levels:b.levels};
  if(!walkable(result,...start,.4)){const p=point(b.rings,null,.7);if(!p||!walkable(result,...p,.4))throw Error('Le plan documentaire bloque son entrée');result.entry=p;}
  result.stair=result.entry.slice();const contents=furnish(result,b,!!recorded);result.furniture=contents.furniture;result.functionalZones=contents.zones;result.furnishingProgram=contents.program;result.roomsBasis=recorded?'documented':'invented-functional-zones';result.roomCoverage=recorded?'documented-record':'partial';if(!recorded)result.rooms=copy(contents.zones);
  result.signature=hash([b.id,b.rings,level,result.elevation,result.height,walls,result.furniture]);return result;
 }
 return{EPS,MAX_POINTS,MAX_LEVELS,hash,area,bounds,inside,clearance,segmentDistance,cleanRings,building,validateBuilding,point,intervals,document,floorLevels,alignStreet,theme,FURNITURE,program,roomProgram,furnishingFits,furnitureModel,walkable,canTravel,layout};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralCityInteriors;

/* Runtime is separate from the geometry module so source tests can exercise
   real polygon logic without fabricating the rest of a campaign. */
if(typeof baseState==='function'){
 const V050_CITY_ZONE='v050_city_interior';
 const V050_CITY={doors:new Map(),owner:null,tick:0,documents:new Map(),holding:false,exitPending:null,entered:0,returned:0,errors:[],last:null,rejections:{}};
 if(!ALL_ZONE_IDS.includes(V050_CITY_ZONE))ALL_ZONE_IDS.push(V050_CITY_ZONE);
 function fresh(){return{schema:1,active:null,returnPoint:null,visits:{}};}
 function migrate(raw){
  const f=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return f;
  const r=raw.returnPoint;if(r&&typeof r.macro==='string'&&V015_GEO_MACROS[r.macro]&&Array.isArray(r.pos)&&r.pos.length===3&&r.pos.every(Number.isFinite)){
   // Source identities and their declared bounds exist before asynchronous
   // city index loading. A cold interior save must not depend on whether the
   // measured exterior bank has finished registering those same bounds.
   const box=V015_GEO_MACROS[r.macro].bbox,ll=v015GeoUnproject(r.macro,r.pos[0],r.pos[2]);
   if(Array.isArray(box)&&box.length===4&&box.every(Number.isFinite)&&box[0]<box[2]&&box[1]<box[3]&&Array.isArray(ll)&&ll.length>=2&&ll.slice(0,2).every(Number.isFinite)&&ll[0]>=box[0]&&ll[0]<=box[2]&&ll[1]>=box[1]&&ll[1]<=box[3])f.returnPoint={macro:r.macro,pos:r.pos.slice(),yaw:Number.isFinite(r.yaw)?r.yaw:0,pitch:Number.isFinite(r.pitch)?r.pitch:0};
  }
  if(raw.active&&f.returnPoint){try{const b=MistralCityInteriors.validateBuilding(raw.active.building),floor=raw.active.floor,entry=raw.active.entry,streetFloor=raw.active.streetFloor??0;if(!Number.isInteger(floor)||floor<0||floor>=b.levels||!Number.isInteger(streetFloor)||streetFloor<0||streetFloor>=b.levels||!Array.isArray(entry)||entry.length!==2||!entry.every(Number.isFinite))throw Error('Étage sauvegardé invalide');const doc=raw.active.document?MistralCityInteriors.document(raw.active.document,b):null;MistralCityInteriors.layout(b,floor,entry,doc);const facing=Array.isArray(raw.active.facing)&&raw.active.facing.length===2&&raw.active.facing.every(Number.isFinite)?raw.active.facing.slice():[-entry[0],-entry[1]];f.active={building:b,floor,streetFloor,entry:entry.slice(),facing,document:doc};}catch{}}
  if(raw.visits&&typeof raw.visits==='object'&&!Array.isArray(raw.visits))for(const[k,v]of Object.entries(raw.visits).slice(0,20000))if(/^[a-f0-9]{16}$/.test(k)&&Number.isInteger(v)&&v>0)f.visits[k]=Math.min(v,1000000);
  return f;
 }
 const base=baseState;baseState=function(){const s=base();s.v050City=fresh();return s;};
 const migration=migrateState;migrateState=function(input={}){const s=migration(input);s.v050City=migrate(input.v050City);if(s.player.zone===V050_CITY_ZONE&&!s.v050City.active){const r=s.v050City.returnPoint;s.player.zone=r?.macro||'geo_marseille';if(r)s.player.pos=r.pos.slice();}return s;};
 state=migrateState(state);if(world)v049Own(world);
 const saveBase=saveGame;saveGame=function(...args){if(V050_CITY.holding||V050_CITY.exitPending?.owner===state)return false;return saveBase(...args);};
 function surface(w,rings,y,color,id){const triangles=v018Triangulate(rings);if(!triangles.length)throw Error('Sol intérieur sans triangulation');const vertices=[],faces=[];for(const t of triangles){const k=vertices.length;vertices.push(...t.map(p=>[p[0],y,p[1]]));faces.push([k,k+2,k+1]);}const d={mesh:'geoSurface',vertices,faces,pos:[MistralCityInteriors.bounds(rings).cx,y,MistralCityInteriors.bounds(rings).cz],scale:[1,1,1],color,id,revision:0};w.staticDraws.push(d);return d;}
 function wall(w,a,b,y,h,color,id,thickness=.18){
  const length=Math.hypot(b[0]-a[0],b[1]-a[1]);if(length<.02)return;const nx=-(b[1]-a[1])/length*thickness/2,nz=(b[0]-a[0])/length*thickness/2,r=[[a[0]+nx,a[1]+nz],[b[0]+nx,b[1]+nz],[b[0]-nx,b[1]-nz],[a[0]-nx,a[1]-nz]];
  r.push(r[0].slice());V017_PRISM_BASE(w,[r],y,h,color,{id});v017AddPolyCollider(w,r,y,y+h,{id,rings:[r]});
 }
 function build(){
  const a=state.v050City.active;if(!a)throw Error('Aucun intérieur de bâtiment sélectionné');const b=a.building,l=MistralCityInteriors.layout(b,a.floor,a.entry,a.document),palette={residential:{floor:[.34,.29,.22],wall:[.62,.56,.44]},medical:{floor:[.37,.43,.39],wall:[.58,.65,.59]},industrial:{floor:[.29,.29,.27],wall:[.42,.43,.40]},commercial:{floor:[.34,.33,.29],wall:[.58,.57,.49]},civic:{floor:[.42,.38,.31],wall:[.64,.60,.50]}}[l.theme];
  const w=createWorld(V050_CITY_ZONE,b.name,`MARSEILLE · ${a.floor?'NIVEAU '+a.floor:'REZ-DE-CHAUSSÉE'}`,{indoor:true,daylight:.32,fog:[.21,.24,.20],wind:0});w.v050CityInterior=l;w.v050CityBuilding=b;const bb=MistralCityInteriors.bounds(l.rings);w.bounds=[bb.minX-.1,bb.maxX+.1,bb.minZ-.1,bb.maxZ+.1];w.spawn=[l.entry[0],l.elevation+playerEyeHeight(),l.entry[1]];const facing=a.facing||[-l.entry[0],-l.entry[1]];w.spawnYaw=Math.atan2(facing[0],-facing[1]);
  surface(w,l.rings,l.elevation,palette.floor,'city-floor:'+l.signature);surface(w,l.rings,l.elevation+l.height-.08,cMix(palette.wall,COLORS.black,.25),'city-ceiling:'+l.signature);
  for(let r=0;r<l.rings.length;r++)for(let i=0;i<l.rings[r].length;i++)wall(w,l.rings[r][i],l.rings[r][(i+1)%l.rings[r].length],l.elevation,l.height,palette.wall,`city-boundary:${r}:${i}`,.2);
  for(let i=0;i<l.walls.length;i++){const p=l.walls[i];wall(w,p.a,p.b,l.elevation,Math.max(1.8,l.height-.08),cMix(palette.wall,COLORS.limestone,.08),'city-partition:'+i,p.thickness);}
  const materials={wood:[.39,.30,.21],fabric:[.32,.39,.32],blanket:[.43,.45,.28],metal:[.29,.32,.29],dark:[.15,.18,.16],porcelain:[.69,.70,.61],medical:[.48,.62,.54],paper:[.72,.68,.53],glass:[.17,.31,.28],water:[.25,.37,.35],amber:[.64,.48,.22]};
  for(let i=0;i<l.furniture.length;i++){const f=l.furniture[i],[x,z]=f.pos,y=l.elevation,parts=MistralCityInteriors.furnitureModel(f);for(let j=0;j<parts.length;j++){const part=parts[j],draw=addBox(w,[x+part.pos[0],y+part.pos[1],z+part.pos[2]],part.size,materials[part.material]||materials.wood,0,{id:`city-furniture:${i}:part:${j}`});draw.v050CityFurnishing={id:f.id,kind:f.kind,provenance:'invented'};}const collider=addCollider(w,x,z,f.size[0],f.size[1],{id:'city-furniture:'+i,minY:y,maxY:y+f.height});collider.v050CityFurnishing={id:f.id,kind:f.kind,provenance:'invented'};}
  const[x,z]=l.entry,y=l.elevation;
  addBox(w,[x,y+.06,z],[.65,.12,.65],[.57,.52,.28]);
  const inspect=()=>{
   const source=l.source,uses=[...new Set(l.functionalZones.map(z=>z.use))].join(', '),text=`${b.name}\nEmpreinte extérieure conservée à l’échelle métrique, cours exclues.\n${l.levels} niveau(x) : ${b.levelsBasis}.\nNiveau courant : ${l.provenance==='documented'?'plan documenté':'plan inventé, cohérent avec le volume et l’usage disponibles'}.\nLe mobilier et les réserves sont fictifs.\nProgramme inventé : ${uses||'pas de mobilier ajouté lorsque le passage manque'}. Ces zones fonctionnelles sont partielles et ne constituent pas un relevé des pièces.\n${source?source.title+'\n'+source.url+'\n'+source.license+' · '+source.attribution:'Aucun relevé public des pièces n’est attaché à ce bâtiment.'}`;
   openNote('city-plan:'+MistralCityInteriors.hash(b.id),b.name,text);
  };
  addInteract(w,'city-interior-landing',[x,y+1.1,z],'Palier · niveau '+a.floor+' · accès et provenance',()=>{
   const choices=[];
   if(a.floor+1<b.levels)choices.push({text:'Monter au niveau '+(a.floor+1),onChoose:()=>floor(1)});
   if(a.floor>0)choices.push({text:'Descendre au niveau '+(a.floor-1),onChoose:()=>floor(-1)});
   if(a.floor===(a.streetFloor??0))choices.push({text:'Sortir vers la rue',onChoose:exit});
   choices.push({text:'Consulter la provenance du plan',onChoose:()=>{closeDialogue();inspect();}},{text:'Continuer la visite',onChoose:closeDialogue});
   openDialogue(speaker(b.name,'PALIER · NIVEAU '+a.floor,'P'),l.provenance==='documented'?'Ce niveau utilise un plan documenté. Le mobilier et les réserves sont fictifs.':'Cet aménagement est inventé dans l’emprise extérieure source, à l’échelle métrique. Les niveaux sont reliés par ce palier ; le dessin de l’escalier n’est pas un relevé réel.',choices);
  },{kind:'door',radius:3,priority:8});
  // Every level is a separate physical storey, loaded at its metric elevation.
  // The landing changes floors explicitly; it is not a measured stair design.
  if(b.levels>1){const p=l.entry;for(let i=0;i<3;i++){const q=[p[0]+.65+i*.18,p[1]];if(MistralCityInteriors.clearance(l.rings,...q)>.35)addBox(w,[q[0],y+.06+i*.06,q[1]],[.16,.12+i*.12,.6],[.42,.43,.38]);}}
  const stash=l.furniture.find(f=>MistralCityInteriors.walkable(l,...f.pos,.8));
  if(stash&&typeof v026NewContainer==='function'){const id='city:'+MistralCityInteriors.hash(b.id)+':'+a.floor,p=[stash.pos[0],y,stash.pos[1]+stash.size[1]/2+.12],seed=parseInt(MistralCityInteriors.hash(id).slice(0,6),16),items=l.theme==='medical'?{cloth:1,water:1}:l.theme==='industrial'?{scrap:1+seed%3}:{cloth:1,scrap:1};const[key,c]=v026NewContainer(w,id,'Réserve fictive · '+b.name,p,items,{kind:'chest'});c.pos=p.slice();v026Attach(w,key,c);}
  w.subzones=[{id:'city-landing',name:'Palier · niveau '+a.floor,pos:[x,y,z]}];w.levelRoutes=[];return w;
 }
 const builder=buildWorld;buildWorld=function(id){return id===V050_CITY_ZONE?build():builder(id);};
 const unlock=isZoneUnlocked;isZoneUnlocked=function(id){return id===V050_CITY_ZONE?!!state.v050City?.active:unlock(id);};
 const region=worldRegionLabel;worldRegionLabel=function(id){return id===V050_CITY_ZONE?'MARSEILLE · INTÉRIEUR '+(state.v050City?.active?.floor||0):region(id);};
 const zoneName=v018ZoneName;v018ZoneName=function(id){return id===V050_CITY_ZONE?state.v050City?.active?.building?.name||'Intérieur de bâtiment':zoneName(id);};
 const ground=groundHeightAt;groundHeightAt=function(x,z,reference=0){const l=world?.v050CityInterior;return l?MistralCityInteriors.inside(l.rings,x,z)?l.elevation:0:ground(x,z,reference);};
 const collision=collidesAt;collidesAt=function(x,z,r=.38,y=null){const l=world?.v050CityInterior;if(l&&!MistralCityInteriors.walkable(l,x,z,r))return true;return collision(x,z,r,y);};
 const movement=tryPlayerMove;tryPlayerMove=function(dx,dz){const l=world?.v050CityInterior,p=state.player.pos;if(l&&!MistralCityInteriors.canTravel(l,[p[0],p[2]],[p[0]+dx,p[2]+dz],state.player.crouched?.32:.38))return false;return movement(dx,dz);};
 function snapshot(){return{owner:state,state:deepClone(state),world,mode,bank:V046.terrain,ready:V046.readyAnchor,loaded:new Map(V017_RUNTIME.loaded),active:new Map(V042_RUNTIME.active),npc:new Map(V042_RUNTIME.npcData),runtimeId:V042_RUNTIME.worldId};}
 function restore(s){if(state!==s.owner)return false;for(const k of Object.keys(state))delete state[k];Object.assign(state,deepClone(s.state));world=s.world;mode=s.mode;V046.terrain=s.bank;V046.readyAnchor=s.ready;V046.prepared=null;V046.busy=false;zoneTransitioning=false;V017_RUNTIME.loaded=new Map(s.loaded);V042_RUNTIME.active=new Map(s.active);V042_RUNTIME.npcData=new Map(s.npc);V042_RUNTIME.worldId=s.runtimeId;V050_CITY.holding=false;V050_CITY.exitPending=null;V050_CITY.owner=null;jumpVelocity=0;onGround=true;v049Own(world);updateLocation();updateHUD();return true;}
 function commit(s,change){V050_CITY.holding=true;try{change();V050_CITY.holding=false;if(state!==s.owner||saveBase(false)===false)throw Error('Sauvegarde impossible : le passage est annulé.');return true;}catch(e){restore(s);V050_CITY.errors.push(String(e.message||e));V050_CITY.errors=V050_CITY.errors.slice(-12);toast(String(e.message||e),'bad');return false;}finally{V050_CITY.holding=false;}}
 function near(it,r=3.5){return!!it&&Math.hypot(it.pos[0]-state.player.pos[0],it.pos[2]-state.player.pos[2])<=r&&Math.abs(it.pos[1]-state.player.pos[1])<3;}
 function enter(id){
  const rec=V050_CITY.doors.get(id);if(!rec||rec.world!==world||!world?.v046||V046.busy||V047.pending||zoneTransitioning||!['PLAYING','DIALOGUE'].includes(mode)||state.player.hp<=0||!near(rec.interaction,rec.interaction.radius+.1)||!lineOfSight(state.player.pos,rec.interaction.pos))return false;
  if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat()){toast('Éloignez-vous du danger avant d’entrer.','bad');return false;}
  closeDialogue();const s=snapshot(),descriptor=rec.building,entry=[rec.door.inside[0]-descriptor.origin[0],rec.door.inside[2]-descriptor.origin[2]],doc=V050_CITY.documents.get(descriptor.id)||null,streetFloor=rec.streetFloor??0;
  const ok=commit(s,()=>{MistralCityInteriors.layout(descriptor,streetFloor,entry,doc);state.v050City.returnPoint={macro:world.id,pos:state.player.pos.slice(),yaw:state.player.yaw,pitch:state.player.pitch};state.v050City.active={building:descriptor,floor:streetFloor,streetFloor,entry,facing:rec.door.normal.map(n=>-n),document:doc};const k=MistralCityInteriors.hash(descriptor.id);state.v050City.visits[k]=(state.v050City.visits[k]||0)+1;loadZone(V050_CITY_ZONE,{instance:true,force:true,silent:true,noTravel:true});if(world?.id!==V050_CITY_ZONE)throw Error('L’intérieur n’a pas été chargé');});
  if(ok){V050_CITY.doors.clear();V050_CITY.owner=null;V050_CITY.entered++;V050_CITY.last={event:'enter',building:descriptor.id,provenance:doc?'documented or mixed':'invented'};toast('Intérieur · '+(doc?'plan documentaire selon les niveaux disponibles':'aménagement inventé dans l’emprise source'),'good');}return ok;
 }
 function floor(delta){
  if(world?.id!==V050_CITY_ZONE||zoneTransitioning||V050_CITY.exitPending||![1,-1].includes(delta)||!['PLAYING','DIALOGUE'].includes(mode))return false;const a=state.v050City.active,l=world.v050CityInterior;
  if(!a||a.floor+delta<0||a.floor+delta>=a.building.levels||Math.hypot(state.player.pos[0]-l.stair[0],state.player.pos[2]-l.stair[1])>3)return false;
  closeDialogue();const s=snapshot();return commit(s,()=>{a.floor+=delta;loadZone(V050_CITY_ZONE,{instance:true,force:true,silent:true,noTravel:true});if(world?.v050CityInterior?.level!==a.floor)throw Error('Le palier n’a pas été chargé');});
 }
 function finishExit(ctx){
  if(V050_CITY.exitPending!==ctx||state!==ctx.owner||!world?.v046)return false;
  V050_CITY.exitPending=null;state.v050City.active=null;state.v050City.returnPoint=null;state.player.pitch=ctx.returnPoint.pitch;
  if(saveBase(false)===false){restore(ctx.snapshot);toast('La sortie n’a pas été sauvegardée. Votre intérieur est conservé.','bad');return false;}
  V050_CITY.returned++;V050_CITY.last={event:'return',building:ctx.building,position:state.player.pos.slice()};V050_CITY.owner=null;bind(true);return true;
 }
 function exit(){
  const s=state.v050City,a=s?.active,r=s?.returnPoint,it=world?.interactables.find(i=>i.id==='city-interior-landing');
  if(world?.id!==V050_CITY_ZONE||!a||a.floor!==(a.streetFloor??0)||!r||V050_CITY.exitPending||!near(it,3.2)||!['PLAYING','DIALOGUE'].includes(mode))return false;
  closeDialogue();const ctx={owner:state,snapshot:snapshot(),returnPoint:deepClone(r),building:a.building.id};V050_CITY.exitPending=ctx;
  try{const result=loadZone(r.macro,{geoDirect:true,force:true,noTravel:true,spawn:r.pos.slice(),yaw:r.yaw,v050CityReturn:true});if(world?.v046)finishExit(ctx);if(result&&typeof result.catch==='function')result.catch(e=>{if(V050_CITY.exitPending===ctx){V050_CITY.exitPending=null;toast('Retour interrompu : '+String(e.message||e),'bad');}});return true;}catch(e){V050_CITY.exitPending=null;restore(ctx.snapshot);toast('Retour interrompu : '+String(e.message||e),'bad');return false;}
 }
 const ensure=v046Ensure;v046Ensure=async function(...args){const ctx=V050_CITY.exitPending,ok=await ensure(...args);if(ok&&ctx&&V050_CITY.exitPending===ctx)finishExit(ctx);else if(!ok&&ctx&&V050_CITY.exitPending===ctx&&world!==ctx.snapshot.world)restore(ctx.snapshot);return ok;};
 const cancel=v046Cancel;v046Cancel=function(){const ctx=V050_CITY.exitPending;cancel();if(ctx&&ctx.owner===state){if(world!==ctx.snapshot.world)restore(ctx.snapshot);else{V050_CITY.exitPending=null;mode='PLAYING';zoneTransitioning=false;}}};
 const load=loadZone;loadZone=function(id,opts={}){const ctx=V050_CITY.exitPending;if(ctx&&!opts.v050CityReturn&&id!==ctx.returnPoint.macro)V050_CITY.exitPending=null;return load(id,opts);};
 const newGame=startNewGame;startNewGame=function(...args){V050_CITY.exitPending=null;V050_CITY.doors.clear();V050_CITY.owner=null;return newGame(...args);};
 function bind(force=false){
  if(!world?.v046||typeof MistralFacades==='undefined'){V050_CITY.doors.clear();V050_CITY.owner=null;return 0;}
  const pos=state.player.pos,stamp=world.v046Records;if(!force&&V050_CITY.owner?.world===world&&V050_CITY.owner.stamp===stamp&&Math.hypot(pos[0]-V050_CITY.owner.x,pos[2]-V050_CITY.owner.z)<12)return V050_CITY.doors.size;
  world.interactables=world.interactables.filter(i=>!i.v050CityDoor);V050_CITY.doors.clear();const candidates=[],seen=new Set(),rejections={nearbyBuildings:0,invalidVolume:0,unmeasuredApproach:0,unmatchedStreetLevel:0,blockedApproach:0,narrowDoor:0,noCandidate:0,eligible:0,interactions:0};
  for(const d of world.staticDraws){if(d.geoLayer!=='building'||!d.rings||d.hidden)continue;d.v050EntranceSelection=null;const bb=MistralCityInteriors.bounds(d.rings);if(pos[0]<bb.minX-100||pos[0]>bb.maxX+100||pos[2]<bb.minZ-100||pos[2]>bb.maxZ+100)continue;
   try{const description=MistralFacades.describe(d);if(!description||seen.has(description.id))continue;seen.add(description.id);rejections.nearbyBuildings++;const b=MistralCityInteriors.building(description);let accepted=false;
    for(const original of MistralFacades.entrances(d)){const p=original.outside;if(!p||!p.every(Number.isFinite))continue;const distance=Math.hypot(p[0]-pos[0],p[2]-pos[2]);if(distance>100)continue;const h=v047Height(v047Bank(world),p[0],p[2]).height;if(h===null){rejections.unmeasuredApproach++;continue;}if(collidesAt(p[0],p[2],.38,h+playerEyeHeight())){rejections.blockedApproach++;continue;}
     const local=[original.inside[0]-b.origin[0],original.inside[2]-b.origin[2]];if(MistralCityInteriors.clearance(b.rings,...local)<.43){rejections.narrowDoor++;continue;}const doc=V050_CITY.documents.get(b.id)||null,aligned=MistralCityInteriors.alignStreet(b,h,doc);if(!aligned||original.provenance==='documented'&&Math.abs(original.center[1]-(b.origin[1]+aligned.elevation))>.05){rejections.unmatchedStreetLevel++;continue;}
     const grid=MistralCityInteriors.floorLevels(aligned.building,doc),storeyHeight=(grid[aligned.level+1]??b.height)-grid[aligned.level],doorHeight=original.provenance==='documented'?original.height:Math.min(original.height,storeyHeight-.08);if(doorHeight<1.85||doorHeight>storeyHeight-.08+1e-7||aligned.elevation+doorHeight>b.height){rejections.unmatchedStreetLevel++;continue;}
     const door={...original,height:doorHeight,levelElevations:grid.slice(),elevationOffset:aligned.elevation,thresholdMeters:aligned.thresholdMeters,center:[original.center[0],b.origin[1]+aligned.elevation,original.center[2]],inside:[original.inside[0],b.origin[1]+aligned.elevation,original.inside[2]],outside:[original.outside[0],h,original.outside[2]]};candidates.push({distance,door,draw:d,building:aligned.building,streetFloor:aligned.level,pos:[p[0],h+1.1,p[2]]});accepted=true;break;}
    if(!accepted)rejections.noCandidate++;
   }catch(e){rejections.invalidVolume++;/* A tiny non-visitable shed remains a real exterior footprint. */}
  }
  candidates.sort((a,b)=>a.distance-b.distance||a.door.id.localeCompare(b.door.id));
  for(const c of candidates.slice(0,64)){c.draw.v050EntranceSelection=c.door;const id='city-door:'+MistralCityInteriors.hash([c.building.id,c.door.id]),it=addInteract(world,id,c.pos,'Entrer · '+c.building.name+' · intérieur '+(V050_CITY.documents.has(c.building.id)?'documenté selon niveaux':'inventé'),()=>enter(id),{kind:'door',radius:3.2,priority:2});it.v050CityDoor=true;V050_CITY.doors.set(id,{world,door:c.door,building:c.building,streetFloor:c.streetFloor,interaction:it});}
  rejections.eligible=candidates.length;rejections.interactions=V050_CITY.doors.size;V050_CITY.rejections=rejections;V050_CITY.owner={world,stamp,x:pos[0],z:pos[2]};return V050_CITY.doors.size;
 }
 const publish=v046Publish;v046Publish=function(...args){const result=publish(...args);V050_CITY.owner=null;if(args[0]===world)bind(true);return result;};
 const update=updatePlayer;updatePlayer=function(dt){const r=update(dt),l=world?.v050CityInterior;if(l&&state.player.pos[1]+.18>l.elevation+l.height-.08){state.player.pos[1]=Math.max(l.elevation+playerEyeHeight(),l.elevation+l.height-.261);if(jumpVelocity>0)jumpVelocity=0;onGround=false;}V050_CITY.tick+=Number.isFinite(dt)?dt:0;if(V050_CITY.tick>.5){V050_CITY.tick=0;if(!V046.busy&&!V047.pending&&!zoneTransitioning)bind();}return r;};
 function registerDocument(raw){const current=[...V050_CITY.doors.values()].find(x=>x.building.id===raw?.buildingId)?.building||state.v050City.active?.building;if(!current||current.id!==raw?.buildingId)throw Error('Le bâtiment du plan doit être chargé');const doc=MistralCityInteriors.document(raw,current);V050_CITY.documents.set(current.id,doc);V050_CITY.owner=null;bind(true);return{buildingId:current.id,documentedLevels:doc.levels.map(l=>l.level),source:doc.source};}
 function info(){const a=state.v050City.active,l=world?.v050CityInterior;return{version:1,zone:world?.id,active:a?{id:a.building.id,name:a.building.name,floor:a.floor,streetFloor:a.streetFloor??0,levels:a.building.levels,origin:a.building.origin.slice(),signature:l?.signature,layoutProvenance:l?.provenance,furnishing:l?{objects:l.furniture.length,byKind:Object.fromEntries([...new Set(l.furniture.map(f=>f.kind))].map(kind=>[kind,l.furniture.filter(f=>f.kind===kind).length])),functionalUses:[...new Set(l.functionalZones.map(z=>z.use))],roomsBasis:l.roomsBasis,roomCoverage:l.roomCoverage,provenance:'invented'}:null}:null,doors:[...V050_CITY.doors].map(([id,r])=>({id,building:r.building.id,pos:r.interaction.pos.slice(),levels:r.building.levels,streetFloor:r.streetFloor,provenance:V050_CITY.documents.has(r.building.id)?'documented or mixed':'invented'})),rejections:{...V050_CITY.rejections},interactionBudget:64,entered:V050_CITY.entered,returned:V050_CITY.returned,exitPending:!!V050_CITY.exitPending,last:V050_CITY.last,errors:V050_CITY.errors.slice()};}
 globalThis.v050CityInteriorAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v050CityInteriorInfo:info,v050CityInteriorEnter:enter,v050CityInteriorExit:exit,v050CityInteriorFloor:floor,v050CityInteriorBind:()=>bind(true),v050CityRegisterDocument:registerDocument});bind(true);};
}
