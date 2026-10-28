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
  const properties=raw.properties||{},knownUse=v=>v&&!/^(?:indifferenciee?|inconnue?|unknown|yes|true|batiment|building|bati|non renseignee?)$/.test(normalText(v).trim()),sourceUse=[properties.usage_1,properties.usage_2,properties['building:use'],properties.building,properties.amenity,properties.shop].find(knownUse),nature=knownUse(properties.nature)?properties.nature:'',genericNature=/industri.*agric.*commercial/.test(normalText(nature)),use=String(sourceUse||(!genericNature&&nature)||properties.architectureUse||nature||'').slice(0,160),name=String(properties.name||properties.nom||properties.nom_du_batiment||'Bâtiment').slice(0,160);
  const kind=programTheme4(use),single=['industrial','annex','sports'].includes(kind)||/relig|eglise|culte|chapelle|cathedr|basilique|abbat|synagog|mosquee|temple/.test(normalText(use)),levels=Number.isInteger(raw.levels)&&raw.levels>0?raw.levels:single?1:Math.max(1,Math.round(raw.height/3));if(levels>MAX_LEVELS)throw Error('Nombre de niveaux non pris en charge');if(raw.height/levels<1.95-EPS)throw Error('Le volume et les niveaux renseignés ne laissent pas la hauteur d’un personnage');
  const declared=['building:levels','levels','nombre_d_etages'].find(k=>{const n=Number(properties[k]);return Number.isInteger(n)&&n>=1&&n<=200&&n===levels;}),levelsBasis=declared==='nombre_d_etages'?'nombre_d_etages IGN, rez-de-chaussée compris':declared||'estimation du volume et de l’usage';
  return{id:raw.id,sourceId:String(raw.sourceId||raw.id).slice(0,512),name,origin,rings,height:raw.height,levels,levelHeight:raw.height/levels,use,levelsBasis,outlineBasis:raw.provenance||'empreinte source',schema:1,layoutVersion:5,programmeUse:programmeUse(properties,use)};
 }
 function validateBuilding(raw){
  if(!raw||raw.schema!==1||typeof raw.id!=='string'||raw.id.length>512||!raw.id||!Array.isArray(raw.origin)||raw.origin.length!==3||!raw.origin.every(finite)||!finite(raw.height)||raw.height<=0||raw.height>2000||!Number.isInteger(raw.levels)||raw.levels<1||raw.levels>MAX_LEVELS)throw Error('Bâtiment sauvegardé invalide');
  const rings=cleanRings(raw.rings),b=bounds(rings);if(Math.max(b.maxX-b.minX,b.maxZ-b.minZ)>10000)throw Error('Emprise intérieure hors budget');if(raw.height/raw.levels<1.95-EPS)throw Error('Niveaux sauvegardés incompatibles avec leur volume');
  let levelElevations=null;if(raw.levelElevations!=null){if(!Array.isArray(raw.levelElevations)||raw.levelElevations.length!==raw.levels||raw.levelElevations.some(n=>!finite(n))||Math.abs(raw.levelElevations[0])>EPS)throw Error('Altitudes de planchers invalides');levelElevations=raw.levelElevations.slice();for(let i=0;i<raw.levels;i++)if((levelElevations[i+1]??raw.height)-levelElevations[i]<1.95-EPS)throw Error('Planchers inventés non praticables');}
  return{schema:1,id:raw.id,sourceId:String(raw.sourceId||raw.id).slice(0,512),name:String(raw.name||'Bâtiment').slice(0,160),origin:raw.origin.slice(),rings,height:raw.height,levels:raw.levels,levelHeight:raw.height/raw.levels,use:String(raw.use||'').slice(0,160),levelsBasis:String(raw.levelsBasis||'estimation').slice(0,160),outlineBasis:typeof raw.outlineBasis==='string'?raw.outlineBasis.slice(0,240):'empreinte source',layoutVersion:raw.layoutVersion===5?5:raw.layoutVersion===4?4:raw.layoutVersion===3?3:raw.layoutVersion===2?2:1,...([4,5].includes(raw.layoutVersion)?{programmeUse:validateProgrammeUse(raw.programmeUse,raw.use)}:{}),...(levelElevations?{levelElevations}:{} )};
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
   if(!Number.isInteger(l.level)||l.level<0||l.level>=b.levels||seen.has(l.level)||!finite(l.elevation)||!finite(l.height)||l.height<1.95-EPS||l.height>2000||l.elevation<-.02||l.elevation+l.height>b.height+.25||!Array.isArray(l.walls)||l.walls.length>2048||!Array.isArray(l.rooms)||l.rooms.length>512)throw Error('Niveau documentaire invalide');seen.add(l.level);
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
  archive:{size:[1.2,.55],height:1.75,label:'Étagères et registres',zone:'Archives'},
  checkout:{size:[1.6,.7],height:1.25,label:'Comptoir et caisse',zone:'Encaissement'},
  school_desk:{size:[1.2,1.2],height:.95,label:'Table scolaire et deux chaises',zone:'Enseignement'},
  teaching_board:{size:[1.8,.45],height:1.8,label:'Tableau sur pieds',zone:'Enseignement'},
  printer:{size:[.8,.65],height:1.1,label:'Photocopieur et rangement',zone:'Reprographie'},
  tool_cabinet:{size:[1.1,.6],height:1.75,label:'Armoire à outils',zone:'Outillage'},
  medical_screen:{size:[1.4,.45],height:1.65,label:'Paravent de soins',zone:'Confidentialité des soins'}
 };
 // New compact dwellings use a real single bed and a separate WC, not a
 // scaled actor or a smaller source volume. Saved version-two layouts keep
 // their original equipment and partitions exactly.
 const COMPACT_FURNITURE={bed:{...FURNITURE.bed,size:[.95,2.05],label:'Lit simple'},sanitary:{...FURNITURE.sanitary,size:[.6,.85],label:'WC séparé'}};
 function furnitureDefinition(f){return(f.variant==='compact'&&COMPACT_FURNITURE[f.kind])||FURNITURE[f.kind];}
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
  const d=furnitureDefinition(f);if(!d)throw Error('Mobilier inconnu');const out=[],box=(pos,size,material)=>out.push({pos,size,material}),kind=f.kind;
  if(kind==='bed'||kind==='medical_bed'){
   const[sx,sz]=d.size;box([0,.22,0],[sx,.28,sz],'metal');box([0,.5,0],[sx-.08,.25,sz-.1],kind==='medical_bed'?'medical':'fabric');box([0,.72,-sz*.31],[sx-.18,.18,.42],'paper');box([0,d.height/2,-sz/2+.04],[sx,d.height,.08],'wood');box([0,.64,sz*.16],[sx-.12,.06,sz*.55],kind==='medical_bed'?'medical':'blanket');
  }else if(kind==='sofa'){
   box([0,.25,0],[1.9,.35,.9],'wood');box([0,.7,-.34],[1.9,.5,.22],'fabric');box([-.84,.54,0],[.22,.38,.9],'fabric');box([.84,.54,0],[.22,.38,.9],'fabric');for(const x of[-.39,.39])box([x,.48,.08],[.72,.17,.66],'blanket');
  }else if(kind==='kitchen'){
   box([0,.43,0],[1.9,.86,.7],'wood');box([0,.91,0],[1.9,.1,.7],'porcelain');box([-.48,.973,0],[.62,.026,.48],'dark');box([-.48,.986,0],[.42,.025,.28],'water');box([.43,.973,0],[.58,.026,.5],'metal');for(const x of[.28,.58])box([x,1.002,0],[.18,.03,.28],'dark');box([-.48,1.07,-.27],[.055,.16,.055],'metal');box([-.48,1.13,-.2],[.055,.04,.18],'metal');
  }else if(kind==='sanitary'&&f.variant==='compact'){
   box([0,.35,.04],[.52,.7,.72],'porcelain');box([0,.83,-.3],[.52,.34,.18],'porcelain');box([0,.72,.05],[.47,.05,.58],'dark');
  }else if(kind==='sanitary'||kind==='washbasin'){
   if(kind==='sanitary'){box([-.35,.35,.14],[.52,.7,.72],'porcelain');box([-.35,.83,-.42],[.52,.34,.3],'porcelain');box([-.35,.72,.16],[.47,.05,.58],'dark');}
   const x=kind==='sanitary'?.4:0,sx=kind==='sanitary'?.5:.7,sz=kind==='sanitary'?.48:.55,z=kind==='sanitary'?-.1:0;box([x,.4,z],[sx,.8,sz],'wood');box([x,.83,z],[sx,.06,sz],'porcelain');box([x,.87,z],[sx*.65,.025,sz*.65],'dark');box([x,1.02,kind==='sanitary'?-.29:-.22],[.05,.26,.05],'metal');
  }else if(kind==='dining'){
   box([0,.77,0],[1.5,.1,.72],'wood');for(const x of[-.57,.57])box([x,.38,0],[.12,.76,.5],'wood');for(const z of[-.53,.53]){box([0,.42,z],[.54,.08,.29],'wood');box([0,.72,z+(z>0?.1:-.1)],[.54,.46,.09],'wood');}
  }else if(kind==='desk'){
   box([0,.78,-.2],[1.3,.12,.75],'wood');for(const x of[-.52,.52])box([x,.36,-.2],[.12,.72,.65],'metal');box([0,.96,-.35],[.54,.24,.24],'dark');box([0,1.21,-.4],[.56,.18,.12],'glass');box([0,.43,.42],[.5,.12,.3],'wood');box([0,.74,.53],[.5,.42,.09],'fabric');
  }else if(kind==='reception'){
   box([0,.5,0],[1.9,1,.7],'wood');box([0,1.07,0],[1.9,.1,.75],'porcelain');box([0,.66,.36],[1.5,.15,.025],'amber');box([.55,1.145,-.2],[.3,.05,.22],'dark');
  }else if(kind==='checkout'){
   box([0,.46,0],[1.6,.92,.65],'wood');box([0,.96,0],[1.6,.08,.7],'porcelain');box([.45,1.06,-.08],[.42,.12,.38],'dark');box([.45,1.205,-.18],[.3,.09,.12],'glass');
  }else if(kind==='school_desk'){
   box([0,.73,-.25],[1.2,.08,.6],'wood');for(const x of[-.49,.49])box([x,.35,-.25],[.09,.7,.5],'metal');for(const x of[-.31,.31]){box([x,.43,.39],[.48,.08,.32],'wood');box([x,.73,.55],[.48,.44,.1],'wood');}
  }else if(kind==='teaching_board'){
   box([0,1.25,0],[1.8,1.1,.12],'wood');box([0,1.25,.067],[1.66,.96,.012],'dark');for(const x of[-.65,.65]){box([x,.6,0],[.08,1.2,.08],'metal');box([x,.04,0],[.35,.08,.45],'metal');}
  }else if(kind==='printer'){
   box([0,.4,0],[.8,.8,.65],'metal');box([0,.95,-.03],[.74,.3,.56],'paper');box([0,.96,.255],[.56,.08,.08],'dark');box([.24,1.05,.25],[.2,.08,.12],'glass');
  }else if(kind==='medical_screen'){
   box([0,.95,0],[1.4,1.4,.1],'medical');for(const x of[-.54,.54]){box([x,.8,0],[.07,1.6,.07],'metal');box([x,.04,0],[.3,.08,.45],'metal');}
  }else if(['wardrobe','medical_cabinet','tool_cabinet'].includes(kind)){
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
 /* Version two uses real, enclosed invented rooms. The residual source area
    stays an explicitly described open/common space; no bounding-box floor is
    substituted for the measured outline. Saved version-one interiors retain
    their former layout, so a new partition cannot trap an existing save. */
 const PLAN_BUDGET={rooms:10,furniture:32,gridCells:4096,candidates:256,navigationChecks:180,accessProbesPerObject:25,cacheEntries:4,cacheBytes:1048576};
 const layoutCache=new Map();let layoutCacheBytes=0;
 function cacheLayout(key,result){const text=JSON.stringify(result),bytes=text.length*2;if(bytes>PLAN_BUDGET.cacheBytes)return result;while(layoutCache.size>=PLAN_BUDGET.cacheEntries||layoutCacheBytes+bytes>PLAN_BUDGET.cacheBytes){const id=layoutCache.keys().next().value;layoutCacheBytes-=layoutCache.get(id).length*2;layoutCache.delete(id);}layoutCache.set(key,text);layoutCacheBytes+=bytes;return result;}
 const normalText=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 function programTheme(use){const t=normalText(use);return /hopital|medical|sante|clinique/.test(t)?'medical':/sport|tribune|gymnas|stade|piscin/.test(t)?'sports':/annexe|garage|dependance|abri|remise/.test(t)?'annex':/bureau|office|administr/.test(t)?'office':/industri|entrepot|agric|hangar|silo|reservoir|serre|halle|usine|atelier|cuve|chateau.*eau/.test(t)?'industrial':/commercial|commerce|magasin|boutique|service/.test(t)?'commercial':/eglise|relig|culte|chapelle|cathedr|basilique|abbat|synagog|mosquee|temple|civic|mairie|ecole|musee/.test(t)?'civic':'residential';}
 function rotate(p,angle){const c=Math.cos(angle),s=Math.sin(angle);return[c*p[0]-s*p[1],s*p[0]+c*p[1]];}
 // Version four keeps the source category separate from the invented fit-out.
 // An institution name never supplies a school/health programme by itself.
 function programTheme4(use){const t=normalText(use);return /enseignement|ecole|scolaire|school|college|lycee|universit|kindergarten/.test(t)?'education':/hospital|doctor|dentist|clinic|health/.test(t)?'medical':/warehouse|industrial|workshop|farm|greenhouse/.test(t)?'industrial':/retail|supermarket|convenience|bakery|butcher|pharmacy|shop/.test(t)?'commercial':programTheme(use);}
 function programmeUse(properties,use){
  const field=['usage_1','usage_2','building:use','building','amenity','shop','nature','architectureUse'].find(k=>properties[k]&&String(properties[k]).slice(0,160)===use),basis=field==='architectureUse'?'architecture-annotation':field?'source-attribute':'invented-fallback';
  return{kind:field==='shop'?'commercial':programTheme4(use),basis,field:field||null,value:use};
 }
 function validateProgrammeUse(raw,use){
  if(!raw)return{kind:programTheme4(use),basis:'saved-use',field:null,value:String(use||'').slice(0,160)};
  if(!['residential','medical','sports','annex','office','industrial','commercial','civic','education'].includes(raw.kind)||!['source-attribute','architecture-annotation','invented-fallback','saved-use'].includes(raw.basis)||raw.field!==null&&!['usage_1','usage_2','building:use','building','amenity','shop','nature','architectureUse'].includes(raw.field)||typeof raw.value!=='string'||raw.value.length>160||(raw.field==='shop'?'commercial':programTheme4(raw.value))!==raw.kind||raw.value!==String(use||'').slice(0,160))throw Error('Usage du programme intérieur invalide');
  return{kind:raw.kind,basis:raw.basis,field:raw.field,value:raw.value};
 }
 function planAngle(rings){let longest=0,angle=0;for(let i=0;i<rings[0].length;i++){const a=rings[0][i],b=rings[0][(i+1)%rings[0].length],n=Math.hypot(b[0]-a[0],b[1]-a[1]);if(n>longest+EPS){longest=n;angle=Math.atan2(b[1]-a[1],b[0]-a[0]);}}return((angle+Math.PI/4)% (Math.PI/2)+Math.PI/2)%(Math.PI/2)-Math.PI/4;}
 const rectangle=(x,z,w,d)=>[[x,z],[x+w,z],[x+w,z+d],[x,z+d],[x,z]];
 function segmentsCross(a,b,c,d){const cross=(p,q,r)=>(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);return cross(a,b,c)*cross(a,b,d)<-EPS&&cross(c,d,a)*cross(c,d,b)<-EPS;}
 function segmentGap(a,b,c,d){return segmentsCross(a,b,c,d)?0:Math.min(segmentDistance(a,c,d),segmentDistance(b,c,d),segmentDistance(c,a,b),segmentDistance(d,a,b));}
 function containedRectangle(rings,ring,margin){
  if(!ring.every(p=>clearance(rings,...p)>=margin-EPS))return false;
  for(const source of rings)for(let i=0;i<source.length;i++){const a=source[i],b=source[(i+1)%source.length];
   // A hole or re-entrant corner wholly enclosed by the proposed rectangle
   // must be rejected even when no sampled furniture corner touches it.
   if(inside([ring],...a))return false;
   for(let j=0;j<4;j++){const c=ring[j],d=ring[j+1];if(segmentsCross(a,b,c,d))return false;const distance=Math.min(segmentDistance(a,c,d),segmentDistance(b,c,d),segmentDistance(c,a,b),segmentDistance(d,a,b));if(distance<margin-EPS)return false;}
  }return true;
 }
 function furnitureRing(f){if(f.ring)return f.ring;const size=f.localSize||f.size;return rectangle(-size[0]/2,-size[1]/2,...size).map(p=>{const q=rotate(p,f.rotation||0);return[q[0]+f.pos[0],q[1]+f.pos[1]];});}
 const furnitureGeometry=new WeakMap();
 function furnitureBlocked(f,x,z,radius=.38){let shape=furnitureGeometry.get(f);if(!shape){const ring=furnitureRing(f);shape={ring,bb:bounds([ring])};furnitureGeometry.set(f,shape);}const{ring,bb}=shape;if(x<bb.minX-radius||x>bb.maxX+radius||z<bb.minZ-radius||z>bb.maxZ+radius)return false;return inside([ring],x,z)||ring.some((a,i)=>segmentDistance([x,z],a,ring[(i+1)%ring.length])<radius-EPS);}
 function navigationGrid(rings){
  const bb=bounds(rings),width=bb.maxX-bb.minX,depth=bb.maxZ-bb.minZ,cellBudget=Math.max(96,Math.min(PLAN_BUDGET.gridCells,Math.floor(1000000/rings.reduce((n,r)=>n+r.length,0))));let step=Math.max(.25,Math.sqrt(width*depth/cellBudget)),nx=Math.max(1,Math.ceil(width/step)),nz=Math.max(1,Math.ceil(depth/step));while(nx*nz>cellBudget){step*=1.02;nx=Math.max(1,Math.ceil(width/step));nz=Math.max(1,Math.ceil(depth/step));}
  const dx=width/nx,dz=depth/nz,points=Array(nx*nz),clearances=new Float64Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){const p=[bb.minX+(i+.5)*dx,bb.minZ+(j+.5)*dz],gap=clearance(rings,...p);if(gap>=.5-EPS){points[j*nx+i]=p;clearances[j*nx+i]=gap-.1;}}
  return{nx,nz,dx,dz,minX:bb.minX,minZ:bb.minZ,step:Math.max(dx,dz),points,clearances};
 }
 function navigation(l,grid,furniture=[],required=null){
  const free=p=>walkable(l,...p,.4)&&!furniture.some(f=>furnitureBlocked(f,...p,.4)),directions=[[1,0],[-1,0],[0,1],[0,-1]],flags=new Uint8Array(grid.points.length),seen=new Uint8Array(grid.points.length),queue=[];let freeCount=0;
  let cache=l.navigationCache;if(!cache||cache.walls!==l.walls||cache.length!==l.walls.length){
   cache={walls:l.walls,length:l.walls.length,flags:new Uint8Array(grid.points.length),links:new Uint8Array(grid.points.length),clearances:new Float64Array(grid.points.length)};
   for(let i=0;i<grid.points.length;i++)if(grid.points[i]){const gap=Math.min(grid.clearances[i],...l.walls.map(w=>segmentDistance(grid.points[i],w.a,w.b)-w.thickness/2));cache.clearances[i]=gap;if(gap>=.4-EPS)cache.flags[i]=1;}
   const capsule=(a,b)=>!l.walls.some(w=>segmentGap(a,b,w.a,w.b)<.4+w.thickness/2-EPS)&&!l.rings.some(r=>r.some((p,i)=>segmentGap(a,b,p,r[(i+1)%r.length])<.5-EPS));
   for(let k=0;k<grid.points.length;k++)if(cache.flags[k]){const i=k%grid.nx,j=Math.floor(k/grid.nx);for(let d=0;d<directions.length;d++){const[di,dj]=directions[d],x=i+di,z=j+dj,n=z*grid.nx+x;if(x<0||x>=grid.nx||z<0||z>=grid.nz||!cache.flags[n])continue;const safe=Math.min(cache.clearances[k],cache.clearances[n])>=.4+Math.hypot(di*grid.dx,dj*grid.dz)/2-EPS;if(safe||capsule(grid.points[k],grid.points[n]))cache.links[k]|=1<<d;}}
   l.navigationCache=cache;
  }
  for(let i=0;i<grid.points.length;i++)if(cache.flags[i]&&!furniture.some(f=>furnitureBlocked(f,...grid.points[i],.4))){flags[i]=1;freeCount++;}
  const furnitureTravel=(a,b)=>{const n=Math.max(1,Math.ceil(Math.hypot(a[0]-b[0],a[1]-b[1])/.18));for(let i=0;i<=n;i++)if(furniture.some(f=>furnitureBlocked(f,a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n,.4)))return false;return true;};
  const travel=(a,b)=>canTravel(l,a,b,.4)&&furnitureTravel(a,b);
  const nearby=(p,visit)=>{const radius=grid.step*1.8+.05,cx=Math.floor((p[0]-grid.minX)/grid.dx),cz=Math.floor((p[1]-grid.minZ)/grid.dz),rx=Math.ceil(radius/grid.dx),rz=Math.ceil(radius/grid.dz);for(let z=Math.max(0,cz-rz);z<=Math.min(grid.nz-1,cz+rz);z++)for(let x=Math.max(0,cx-rx);x<=Math.min(grid.nx-1,cx+rx);x++){const i=z*grid.nx+x,q=grid.points[i];if(q&&Math.hypot(q[0]-p[0],q[1]-p[1])<=radius&&visit(i,q))return true;}return false;};
  const reach=p=>nearby(p,(i,q)=>{if(flags[i]&&!seen[i]&&travel(p,q)){seen[i]=1;queue.push(i);}return false;});
  reach(l.entry);
  // Door anchors retain a physical 1.2 m opening when the bounded grid is
  // coarser than the room plan. Their connecting segments use the same radius.
  const anchors=(l.roomDoors||[]).flatMap(d=>[d.inside,d.center,d.outside]),used=new Uint8Array(anchors.length);
  for(let head=0;head<queue.length;head++){
   const k=queue[head],p=grid.points[k];
   for(let d=0;d<directions.length;d++)if(cache.links[k]&(1<<d)){const[di,dj]=directions[d],n=k+dj*grid.nx+di;if(flags[n]&&!seen[n]&&furnitureTravel(p,grid.points[n])){seen[n]=1;queue.push(n);}}
   for(let a=0;a<anchors.length;a++)if(!used[a]&&Math.hypot(p[0]-anchors[a][0],p[1]-anchors[a][1])<=grid.step*1.8+.05&&free(anchors[a])&&travel(p,anchors[a])){used[a]=1;reach(anchors[a]);for(let b=0;b<anchors.length;b++)if(!used[b]&&Math.hypot(anchors[a][0]-anchors[b][0],anchors[a][1]-anchors[b][1])<1.6&&free(anchors[b])&&travel(anchors[a],anchors[b])){used[b]=1;reach(anchors[b]);}}
  }
  let disconnected=0;for(let i=0;i<flags.length;i++)if(flags[i]&&!seen[i]&&(!required||required[i]))disconnected++;
  const reaches=p=>free(p)&&nearby(p,(i,q)=>seen[i]&&travel(q,p));
  // The navigation grid is deliberately conservative. Boundary probes use
  // the physical actor radius for their short link to an already reached cell.
  const reachesAt=(p,radius=.38)=>walkable(l,...p,radius)&&!furniture.some(f=>furnitureBlocked(f,...p,radius))&&nearby(p,(i,q)=>seen[i]&&canTravel(l,q,p,radius)&&!furniture.some(f=>furnitureRing(f).some((a,j,r)=>segmentGap(q,p,a,r[(j+1)%r.length])<radius-EPS)));
  return{seen,freeCount,reached:queue.length,disconnected,reaches,reachesAt,step:grid.step,cells:grid.points.length};
 }
 const ROOM_TYPES={
  sanitary:{use:'Sanitaires',size:[2.4,2.4],required:['sanitary'],optional:['washbasin']},
  bedroom:{use:'Chambre',size:[3.5,3.4],required:['bed','wardrobe'],optional:['desk']},
  kitchen:{use:'Cuisine',size:[3.1,3.2],required:['kitchen'],optional:['dining']},
  living:{use:'Séjour',size:[4.1,3.7],required:['sofa','dining'],optional:['archive']},
  office:{use:'Bureau',size:[3.2,3.2],required:['desk','archive'],optional:['wardrobe']},
  stock:{use:'Réserve',size:[3.6,3.4],required:['shelf','crate'],optional:['wardrobe']},
  treatment:{use:'Salle de soins',size:[3.4,3.8],required:['medical_bed','medical_cabinet'],optional:['washbasin']},
  changing:{use:'Vestiaire',size:[3.1,3.1],required:['bench','wardrobe'],optional:['washbasin']},
  archive:{use:'Archives',size:[3.2,3.2],required:['archive'],optional:['desk']}
 };
 function floorProgram(kind,area){
  const roomTypes=kind==='residential'?['sanitary',...(area>=35?['bedroom']:[]),...(area>=70?['kitchen']:[]),...(area>=120?['living']:[]),...(area>=240?['bedroom']:[])]:kind==='medical'?['treatment','stock','sanitary']:kind==='industrial'?['office','sanitary']:kind==='commercial'?['stock','office','sanitary']:kind==='office'?['office','archive','sanitary']:kind==='sports'?['changing','sanitary']:kind==='annex'?[]:['archive','office','sanitary'];
  const openRequired=kind==='residential'?['bed','kitchen','sofa','dining','wardrobe']:kind==='medical'?['reception','bench','washbasin']:kind==='industrial'?['workbench','crate','pallet']:kind==='commercial'?['reception','shelf','bench']:kind==='office'?['desk','archive','bench']:kind==='sports'?['bench','wardrobe','washbasin']:kind==='annex'?['crate','shelf','workbench']:['bench','lectern','archive'];
  return{roomTypes,openRequired};
 }
 // These are invented programmes, not claims about a building's real rooms.
 // Keep a main working/teaching/public space before adding support rooms.
 const ROOM_TYPES4={
  ...ROOM_TYPES,
  classroom:{use:'Salle de classe',size:[6,5],required:['teaching_board','school_desk'],optional:['desk','shelf'],repeat:{school_desk:4}},
  consultation:{use:'Salle de soins',size:[3.8,4.3],required:['medical_bed','washbasin','medical_cabinet'],optional:['medical_screen']},
  medical_store:{use:'Réserve de soins',size:[3,3],required:['medical_cabinet'],optional:[]},
  staff_office:{use:'Bureau du personnel',size:[3.4,3.3],required:['desk'],optional:['archive','printer']},
  work_store:{use:'Réserve de l’atelier',size:[3.4,3.2],required:['tool_cabinet','crate'],optional:['pallet']}
 };
 function floorProgram4(kind,area){
  if(!['education','medical','industrial','commercial','office'].includes(kind))return floorProgram(kind,area);
  const roomTypes=kind==='education'?[...(area>=65?['classroom']:[]),...(area>=180?['staff_office']:[]),...(area>=35?['sanitary']:[])]:kind==='medical'?[...(area>=45?['consultation']:[]),...(area>=200?['medical_store']:[]),...(area>=35?['sanitary']:[])]:kind==='industrial'?[...(area>=220?['work_store']:[]),...(area>=180?['staff_office']:[]),...(area>=45?['sanitary']:[])]:kind==='commercial'?[...(area>=65?['stock']:[]),...(area>=180?['staff_office']:[]),...(area>=35?['sanitary']:[])]:[...(area>=65?['office']:[]),...(area>=180?['archive']:[]),...(area>=35?['sanitary']:[])];
  const openRequired=kind==='education'?['teaching_board','school_desk','desk','bench','archive']:kind==='medical'?['medical_bed','washbasin','medical_cabinet','reception','bench']:kind==='industrial'?['workbench','tool_cabinet','crate','pallet']:kind==='commercial'?['reception','checkout','shelf','bench']:['desk','printer','archive','bench'];
  const openOnly=kind==='commercial'?['reception','checkout','shelf','bench']:kind==='office'?['desk','printer','bench']:[];
  const openRepeat=kind==='education'?[]:kind==='medical'?['bench']:kind==='commercial'?['shelf']:kind==='office'?['desk','archive']:['workbench','crate','pallet'];
  return{roomTypes,openRequired,openOnly,openRepeat,priority:openRequired.concat('sanitary'),openReserveFraction:kind==='industrial'?.6:kind==='commercial'?.45:kind==='medical'?.4:.35};
 }
 function documentaryRoomProgram4(room,base,level){
  const use=normalText(room?.use);if(/classe|enseignement|scolaire|school|classroom/.test(use))return['teaching_board','school_desk','desk'];if(/soins|consultation|examen|treatment|medical/.test(use))return['medical_bed','washbasin','medical_cabinet'];if(/atelier|workshop/.test(use))return['workbench','tool_cabinet','crate'];if(/vente|commerce|boutique|shop/.test(use))return['checkout','shelf','reception'];return roomProgram(room,base,level);
 }
 function candidatePoints(bb,size){const[w,d]=size,xs=[bb.minX+.22,bb.maxX-w-.22],zs=[bb.minZ+.22,bb.maxZ-d-.22],step=Math.max(.8,Math.sqrt((bb.maxX-bb.minX)*(bb.maxZ-bb.minZ)/144));for(let x=bb.minX+.22;x+w<bb.maxX-.2;x+=step)xs.push(x);for(let z=bb.minZ+.22;z+d<bb.maxZ-.2;z+=step)zs.push(z);const points=[];for(const z of [...new Set(zs)])for(const x of [...new Set(xs)])points.push([x,z]);return points.slice(0,PLAN_BUDGET.candidates);}
 function rectFits(l,ring,rooms){
  const bb=bounds([ring]);if(bb.maxX-bb.minX<1.9||bb.maxZ-bb.minZ<1.9)return false;
  if(rooms.some(r=>{const b=r.bounds;return Math.hypot(Math.max(b.minX-bb.maxX,bb.minX-b.maxX,0),Math.max(b.minZ-bb.maxZ,bb.minZ-b.maxZ,0))<1.18;}))return false;
  if(Math.hypot(Math.max(bb.minX-l.entry[0],l.entry[0]-bb.maxX,0),Math.max(bb.minZ-l.entry[1],l.entry[1]-bb.maxZ,0))<1.2)return false;
  return containedRectangle(l.rings,ring,.19);
 }
 function roomWalls(ring,side,width=1.2){
  const walls=[];let door=null;for(let i=0;i<4;i++){const a=ring[i],b=ring[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]),t=[(b[0]-a[0])/length,(b[1]-a[1])/length];if(i!==side){walls.push({a:a.slice(),b:b.slice(),thickness:.16,provenance:'invented'});continue;}const center=[(a[0]+b[0])/2,(a[1]+b[1])/2],normal=[t[1],-t[0]],left=[center[0]-t[0]*width/2,center[1]-t[1]*width/2],right=[center[0]+t[0]*width/2,center[1]+t[1]*width/2];walls.push({a:a.slice(),b:left,thickness:.16,provenance:'invented'},{a:right,b:b.slice(),thickness:.16,provenance:'invented'});door={center,inside:[center[0]-normal[0]*.7,center[1]-normal[1]*.7],outside:[center[0]+normal[0]*.7,center[1]+normal[1]*.7],width,side,provenance:'invented'};}
  return{walls,door};
 }
 // No source coordinate is changed. At most256 points just inside source
 // edges catch small free pockets between a curved outline and new partitions.
 const BOUNDARY_PROBE_LIMIT=256;
 function boundaryProbes(rings){const edges=rings.flatMap(r=>r.map((a,i)=>[a,r[(i+1)%r.length]])),out=[],stride=Math.max(1,Math.ceil(edges.length/(BOUNDARY_PROBE_LIMIT/4)));for(let i=0;i<edges.length;i+=stride){const[a,b]=edges[i],dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz);if(length<EPS)continue;const p=[(a[0]+b[0])/2,(a[1]+b[1])/2];for(const gap of[.41,.58])for(const side of[-1,1]){const q=[p[0]+side*dz/length*gap,p[1]-side*dx/length*gap];if(clearance(rings,...q)>=.38-EPS)out.push(q);}}return out;}
 function generatedRooms(l,b,grid,baseline,program,checks){
  const rooms=[],omissions=[],bb=bounds(l.rings),unproven=baseline.freeCount>baseline.reached,limited=unproven||grid.step>.65||l.rings.reduce((n,r)=>n+r.length,0)>512;
  for(const type of program.roomTypes){
   if(limited||rooms.length>=PLAN_BUDGET.rooms){omissions.push({type,reason:unproven?'source-circulation-unproven':'room-proof-budget'});continue;}const original=(l.programVersion>=4?ROOM_TYPES4:ROOM_TYPES)[type],spec=l.compactResidential&&type==='sanitary'?{...original,size:[2,2.15]}:original;let found=null;
   if(program.openReserveFraction&&rooms.reduce((sum,r)=>sum+Math.abs(area(r.ring)),0)+spec.size[0]*spec.size[1]>(1-program.openReserveFraction)*l.sourceArea){omissions.push({type,reason:'programme-open-space-reserve'});continue;}
   for(const size of[spec.size,spec.size.slice().reverse()]){for(const p of candidatePoints(bb,size)){
    const ring=rectangle(...p,...size);if(!rectFits(l,ring,rooms))continue;
    for(const side of[0,1,2,3]){const shape=roomWalls(ring,side);shape.door.height=Math.min(2.12,l.height-.1);if(clearance(l.rings,...shape.door.outside)<.48||checks.count>=PLAN_BUDGET.navigationChecks)continue;checks.count++;const test={...l,walls:l.walls.concat(shape.walls),roomDoors:l.roomDoors.concat(shape.door)},nav=navigation(test,grid,[],baseline.seen);if(nav.disconnected||!nav.reaches(shape.door.inside)||!nav.reaches(shape.door.outside)||(l.boundaryAccessProbes||[]).some(p=>walkable(test,...p,.38)&&!nav.reachesAt(p,.38)))continue;
     found={id:'room:'+hash([b.id,l.level,type,rooms.length]),type,use:spec.use,ring,bounds:bounds([ring]),door:shape.door,required:spec.required.slice(),optional:spec.optional.slice(),...(spec.repeat?{repeat:{...spec.repeat}}:{}),provenance:'invented',coverage:'enclosed-room'};l.walls.push(...shape.walls);l.roomDoors.push({...shape.door,roomId:found.id});break;
    }if(found)break;
   }if(found)break;}
   if(found)rooms.push(found);else omissions.push({type,reason:checks.count>=PLAN_BUDGET.navigationChecks?'navigation-budget':'no-contained-connected-room'});
  }
  return{rooms,omissions,limited};
 }
 function furnitureFitsNew(l,p,size,furniture){
  const bb={minX:p[0]-size[0]/2,maxX:p[0]+size[0]/2,minZ:p[1]-size[1]/2,maxZ:p[1]+size[1]/2};
  if(Math.hypot(Math.max(bb.minX-l.entry[0],l.entry[0]-bb.maxX,0),Math.max(bb.minZ-l.entry[1],l.entry[1]-bb.maxZ,0))<.9)return false;
  if(furniture.some(f=>Math.hypot(Math.max(Math.abs(p[0]-f.pos[0])-(size[0]+f.size[0])/2,0),Math.max(Math.abs(p[1]-f.pos[1])-(size[1]+f.size[1])/2,0))<.16))return false;
  const ring=rectangle(bb.minX,bb.minZ,...size);if(!containedRectangle(l.rings,ring,.14))return false;
  for(const w of l.walls){if(inside([ring],...w.a)||inside([ring],...w.b))return false;const thick=w.thickness/2+.04;for(let j=0;j<4;j++){const a=ring[j],b=ring[j+1];if(segmentsCross(w.a,w.b,a,b)||Math.min(segmentDistance(w.a,a,b),segmentDistance(w.b,a,b),segmentDistance(a,w.a,w.b),segmentDistance(b,w.a,w.b))<thick-EPS)return false;}}
  return true;
 }
 function furnishNew(l,b,grid,baseline,program,checks,recorded){
  const furniture=[],zones=[],omissions=[],requirements=[],equipmentQuantities=[],rooms=l.rooms;
  for(const room of rooms){const kinds=room.required||(l.programVersion>=4?documentaryRoomProgram4(room,b.use,l.level):roomProgram(room,b.use,l.level));for(const kind of kinds)requirements.push({kind,room,required:true});}
  const inRooms=new Set(requirements.map(r=>r.kind));for(const kind of program.openRequired)if(!inRooms.has(kind)||program.openOnly?.includes(kind))requirements.push({kind,room:null,required:true});
  if(!rooms.some(r=>r.required?.includes('sanitary'))&&!requirements.some(r=>r.kind==='sanitary')&&!['annex','industrial','sports'].includes(l.theme))requirements.push({kind:'sanitary',room:null,required:true});
  if(l.programVersion>=4&&program.priority)requirements.sort((a,b)=>{const rank=k=>{const n=program.priority.indexOf(k);return n<0?program.priority.length:n;};return rank(a.kind)-rank(b.kind);});
  if(!recorded&&baseline.freeCount>baseline.reached)return{furniture,zones,omissions:requirements.map(r=>({kind:r.kind,roomId:r.room?.id||null,reason:'source-circulation-unproven'})),requirements:requirements.map(r=>({kind:r.kind,roomId:r.room?.id||null})),program:[...new Set(requirements.map(r=>r.kind))]};
  const positions=(region,size)=>{
   const bb=region?bounds([region.ring]):bounds(l.rings),hx=size[0]/2+.14,hz=size[1]/2+.14,xs=[bb.minX+hx,bb.maxX-hx],zs=[bb.minZ+hz,bb.maxZ-hz],step=Math.max(.6,Math.sqrt((bb.maxX-bb.minX)*(bb.maxZ-bb.minZ)/196));for(let x=bb.minX+hx;x<bb.maxX-hx;x+=step)xs.push(x);for(let z=bb.minZ+hz;z<bb.maxZ-hz;z+=step)zs.push(z);const points=[];for(const z of [...new Set(zs)])for(const x of [...new Set(xs)])points.push([x,z]);return points.slice(0,PLAN_BUDGET.candidates);
  };
  const approachValid=(f,p)=>{const room=f.roomId?rooms.find(r=>r.id===f.roomId):null;return(!room||clearance([room.ring],...p)>=.4-EPS)&&canTravel(l,f.pos,p,.04);};
  const approaches=f=>{const[p,q]=f.pos,[w,d]=f.size;return[[p,q+d/2+.64],[p,q-d/2-.64],[p+w/2+.64,q],[p-w/2-.64,q]].filter(a=>approachValid(f,a));};
  const probesClear=(nav,all,newFurniture)=>{if((l.boundaryAccessProbes||[]).some(p=>walkable(l,...p,.38)&&!all.some(f=>furnitureBlocked(f,...p,.38))&&!nav.reachesAt(p,.38)))return false;for(const f of all){if(Math.hypot(f.pos[0]-newFurniture.pos[0],f.pos[1]-newFurniture.pos[1])>5)continue;const room=rooms.find(r=>r.id===f.roomId),bb=room?bounds([room.ring]):bounds(l.rings),[x,z]=f.pos,[w,d]=f.size,xs=[x,(x-w/2+bb.minX)/2,(x+w/2+bb.maxX)/2,x-w/2-.42,x+w/2+.42],zs=[z,(z-d/2+bb.minZ)/2,(z+d/2+bb.maxZ)/2,z-d/2-.42,z+d/2+.42];for(const a of xs)for(const b of zs){const p=[a,b];if(walkable(l,...p,.38)&&!all.some(v=>furnitureBlocked(v,...p,.38))&&(l.strictAccessProbes?baseline.reachesAt(p,.38):baseline.reaches(p))&&!(l.strictAccessProbes?nav.reachesAt(p,.38):nav.reaches(p)))return false;}}return true;};
  const place=(kind,room)=>{
   const variant=l.compactResidential&&COMPACT_FURNITURE[kind]?'compact':null,def=variant?COMPACT_FURNITURE[kind]:FURNITURE[kind];if(!def||def.height>l.height-.1||furniture.length>=PLAN_BUDGET.furniture)return false;
   for(const turn of[0,Math.PI/2]){const size=turn?def.size.slice().reverse():def.size;
    for(const p of positions(room,size)){
     if(room&&!containedRectangle([room.ring],rectangle(p[0]-size[0]/2,p[1]-size[1]/2,...size),.12)||!room&&rooms.some(r=>inside([r.ring],...p))||!furnitureFitsNew(l,p,size,furniture))continue;
     const approachCandidates=[[p[0],p[1]+size[1]/2+.64],[p[0],p[1]-size[1]/2-.64],[p[0]+size[0]/2+.64,p[1]],[p[0]-size[0]/2-.64,p[1]]],f={id:'furnishing:'+hash([b.id,l.level,p,kind,turn,'rooms-v2']),pos:p.slice(),kind,size:size.slice(),localSize:def.size.slice(),rotation:turn,height:def.height,label:def.label,zone:def.zone,roomId:room?.id||null,...(variant?{variant}:{}),provenance:'invented',seed:parseInt(hash([b.id,l.level,p,kind]).slice(0,6),16)};
     const possible=approachCandidates.filter(q=>approachValid(f,q)&&walkable(l,...q,.4)&&!furniture.concat(f).some(a=>furnitureBlocked(a,...q,.4)));if(!possible.length||checks.count>=PLAN_BUDGET.navigationChecks)continue;checks.count++;const nav=navigation(l,grid,furniture.concat(f),baseline.seen);if(nav.disconnected||l.roomDoors.some(d=>!nav.reaches(d.center)||!nav.reaches(d.outside))||!probesClear(nav,furniture.concat(f),f))continue;const retained=furniture.map(a=>[a,[a.approach,...approaches(a)].find(q=>q&&nav.reaches(q))]);if(retained.some(a=>!a[1]))continue;const approach=possible.find(q=>nav.reaches(q));if(!approach)continue;
     for(const[a,q]of retained)a.approach=q.slice();f.approach=approach.slice();furniture.push(f);const[x,z]=p,[sx,sz]=size;zones.push({id:'invented-zone:'+f.id,use:def.zone,ring:rectangle(x-sx/2,z-sz/2,sx,sz),anchor:p.slice(),roomId:f.roomId,provenance:'invented',coverage:'furnished-function'});return true;
    }
   }return false;
  };
  for(const r of requirements)if(!place(r.kind,r.room))omissions.push({kind:r.kind,roomId:r.room?.id||null,reason:checks.count>=PLAN_BUDGET.navigationChecks?'navigation-budget':furniture.length>=PLAN_BUDGET.furniture?'furniture-budget':'metric-fit-or-access'});
  if(l.programVersion>=4)for(const room of rooms)for(const[kind,requested]of Object.entries(room.repeat||{})){let placed=furniture.filter(f=>f.roomId===room.id&&f.kind===kind).length;while(placed<requested&&furniture.length<PLAN_BUDGET.furniture&&checks.count<PLAN_BUDGET.navigationChecks){if(!place(kind,room))break;placed++;}equipmentQuantities.push({roomId:room.id,kind,requested,placed,complete:placed===requested,...(placed<requested?{reason:checks.count>=PLAN_BUDGET.navigationChecks?'navigation-budget':furniture.length>=PLAN_BUDGET.furniture?'furniture-budget':'metric-fit-or-access'}:{})});}
  for(const room of rooms)for(const kind of room.optional||[])if(furniture.length<PLAN_BUDGET.furniture&&checks.count<PLAN_BUDGET.navigationChecks)place(kind,room);
  // Large halls may repeat their useful equipment, while small dwellings keep
  // the complete distinct programme ahead of decoration and repeated storage.
  const target=omissions.length||(l.programVersion>=4?l.sourceArea:Math.abs(area(l.rings[0])))<180?furniture.length:Math.min(PLAN_BUDGET.furniture,Math.floor((l.programVersion>=4?l.sourceArea:Math.abs(area(l.rings[0])))/40));for(let repeat=0;furniture.length<target&&repeat<3;repeat++)for(const kind of program.openRepeat||program.openRequired){if(furniture.length>=target||checks.count>=PLAN_BUDGET.navigationChecks)break;place(kind,null);}
  return{furniture,zones,omissions,equipmentQuantities,requirements:requirements.map(r=>({kind:r.kind,roomId:r.room?.id||null})),program:[...new Set(requirements.map(r=>r.kind))]};
 }
 function layoutNew(b,level,start,gridLevels,recorded,doc){
  const angle=planAngle(b.rings),toLocal=p=>rotate(p,-angle),toWorld=p=>rotate(p,angle),sourceArea=Math.max(0,Math.abs(area(b.rings[0]))-b.rings.slice(1).reduce((s,r)=>s+Math.abs(area(r)),0)),kind=b.layoutVersion>=4?b.programmeUse.kind:programTheme(b.use),l={buildingId:b.id,level,rings:b.rings.map(r=>r.map(toLocal)),height:(gridLevels[level+1]??b.height)-gridLevels[level],elevation:gridLevels[level],entry:toLocal(start),walls:recorded?recorded.walls.map(w=>({...w,a:toLocal(w.a),b:toLocal(w.b)})):[],rooms:recorded?recorded.rooms.map(r=>({...r,ring:r.ring.map(toLocal)})):[],roomDoors:[],theme:kind,compactResidential:b.layoutVersion>=3&&!recorded&&kind==='residential'&&sourceArea<55,strictAccessProbes:b.layoutVersion>=4||b.layoutVersion===3&&!recorded&&kind==='residential'&&sourceArea<55,programVersion:b.layoutVersion,sourceArea};
  if(!walkable(l,...l.entry,.4)){const fallback=point(l.rings,null,.7);if(!fallback||!walkable(l,...fallback,.4))throw Error('Le plan documentaire bloque son entrée');l.entry=fallback;start=toWorld(fallback);}
  const grid=navigationGrid(l.rings),baseline=navigation({...l,walls:l.walls.slice()},grid),checks={count:0},program=b.layoutVersion>=4?floorProgram4(kind,sourceArea):floorProgram(kind,sourceArea);
  if(l.compactResidential||b.layoutVersion>=4)l.boundaryAccessProbes=boundaryProbes(l.rings).filter(p=>baseline.reachesAt(p,.38));
  const generated=recorded?{rooms:l.rooms,omissions:[],limited:false}:generatedRooms(l,b,grid,baseline,program,checks);l.rooms=generated.rooms;const contents=furnishNew(l,b,grid,baseline,program,checks,!!recorded),nav=navigation(l,grid,contents.furniture,baseline.seen);
  const walls=recorded?copy(recorded.walls):l.walls.map(w=>({...w,a:toWorld(w.a),b:toWorld(w.b)})),rooms=recorded?copy(recorded.rooms):l.rooms.map(r=>({...r,ring:r.ring.map(toWorld),bounds:bounds([r.ring.map(toWorld)]),door:{...r.door,center:toWorld(r.door.center),inside:toWorld(r.door.inside),outside:toWorld(r.door.outside)}})),furniture=contents.furniture.map(f=>{const ring=furnitureRing(f).map(toWorld),bb=bounds([ring]);return{...f,pos:toWorld(f.pos),approach:toWorld(f.approach),ring,localSize:f.localSize.slice(),size:[bb.maxX-bb.minX,bb.maxZ-bb.minZ],rotation:angle+f.rotation};}),roomArea=recorded?null:l.rooms.reduce((s,r)=>s+Math.abs(area(r.ring)),0);
  const result={buildingId:b.id,level,rings:copy(b.rings),height:l.height,elevation:l.elevation,walls,entry:start.slice(),stair:start.slice(),theme:kind,rooms,roomDoors:l.roomDoors.map(d=>({...d,center:toWorld(d.center),inside:toWorld(d.inside),outside:toWorld(d.outside)})),provenance:recorded?'documented':'invented',source:recorded?doc.source:null,levels:b.levels,furniture,functionalZones:contents.zones.map(z=>({...z,ring:z.ring.map(toWorld),anchor:toWorld(z.anchor)})),furnishingProgram:contents.program,roomsBasis:recorded?'documented':'invented-enclosed-rooms',roomCoverage:recorded?'documented-record':'rooms-and-open-source-space',layoutVersion:b.layoutVersion,
   openSpace:recorded?null:{id:'open:'+hash([b.id,level]),use:kind==='residential'?'Pièce de vie et circulation ouverte':kind==='industrial'?'Halle de travail et circulation':kind==='commercial'?'Espace de vente et circulation':'Espace commun et circulation',rings:copy(b.rings),excludedRooms:l.rooms.map(r=>r.id),provenance:'invented',area:Math.max(0,sourceArea-roomArea)},
   programCoverage:{provenance:'invented',frame:'building-local-metre',...(b.layoutVersion>=3?{programVersion:b.layoutVersion,...(b.layoutVersion>=4?{useBasis:copy(b.programmeUse),mainSpaceReserveFraction:program.openReserveFraction||0,equipmentQuantities:contents.equipmentQuantities||[],allRequestedEquipmentPlaced:!contents.omissions.length&&!contents.equipmentQuantities?.some(q=>!q.complete)}:{}),equipmentScale:l.compactResidential?'single-bed-and-separate-wc':'standard',boundaryAccessSamples:l.boundaryAccessProbes?.length||0}:{}),orientationRadians:angle,footprintArea:sourceArea,enclosedRoomArea:roomArea,openSourceArea:recorded?null:Math.max(0,sourceArea-roomArea),enclosedRooms:rooms.length,requestedRoomTypes:program.roomTypes,roomOmissions:generated.omissions,furnishingRequirements:contents.requirements,furnishingOmissions:contents.omissions,allRequestedFunctionsPlaced:!contents.omissions.length,allRequestedRoomsPlaced:!generated.omissions.length,completeInventedProgram:!recorded&&!contents.omissions.length&&!generated.omissions.length&&!(b.layoutVersion>=4&&contents.equipmentQuantities?.some(q=>!q.complete))&&baseline.freeCount===baseline.reached,roomsLimited:generated.limited,navigation:{sampledCells:nav.cells,stepMeters:nav.step,sourceUnreachableCells:baseline.freeCount-baseline.reached,newUnreachableCells:nav.disconnected,reachableCells:nav.reached,freeCells:nav.freeCount},budgets:{...PLAN_BUDGET,...(b.layoutVersion>=3?{boundaryAccessProbes:BOUNDARY_PROBE_LIMIT}:{})},navigationChecks:checks.count}};
  result.signature=hash([b.layoutVersion>=3?b.layoutVersion:2,b.id,b.rings,level,result.elevation,result.height,walls,rooms,furniture]);return result;
 }
 function walkable(layout,x,z,radius=.38){if(clearance(layout.rings,x,z)<radius)return false;return !layout.walls.some(w=>segmentDistance([x,z],w.a,w.b)<radius+w.thickness/2-EPS);}
 function canTravel(layout,from,to,radius=.38){const distance=Math.hypot(to[0]-from[0],to[1]-from[1]);if(distance>400)return false;const n=Math.max(1,Math.ceil(distance/.15));for(let i=0;i<=n;i++)if(!walkable(layout,from[0]+(to[0]-from[0])*i/n,from[1]+(to[1]-from[1])*i/n,radius))return false;return true;}
 function layout(b,level=0,entry=null,doc=null){
  b=validateBuilding(b);if(!Number.isInteger(level)||level<0||level>=b.levels)throw Error('Étage intérieur invalide');
  const checked=doc?document(doc,b):null,recorded=checked?.levels.find(l=>l.level===level),grid=floorLevels(b,checked),start=point(b.rings,recorded?.entry||entry,.43);
  if(!start)throw Error('L’emprise ne contient pas d’espace praticable pour un personnage');
  if(b.layoutVersion===2||b.layoutVersion===3||b.layoutVersion>=4){const key=hash([b,level,start,checked]),cached=layoutCache.get(key);if(cached){layoutCache.delete(key);layoutCache.set(key,cached);return JSON.parse(cached);}return cacheLayout(key,layoutNew(b,level,start,grid,recorded,checked));}
  const walls=recorded?recorded.walls:inventedWalls(b,start),result={buildingId:b.id,level,rings:copy(b.rings),height:(grid[level+1]??b.height)-grid[level],elevation:grid[level],walls,entry:start,theme:theme(b.use),rooms:recorded?.rooms||[],provenance:recorded?'documented':'invented',source:recorded?doc.source:null,levels:b.levels};
  if(!walkable(result,...start,.4)){const p=point(b.rings,null,.7);if(!p||!walkable(result,...p,.4))throw Error('Le plan documentaire bloque son entrée');result.entry=p;}
  result.stair=result.entry.slice();const contents=furnish(result,b,!!recorded);result.furniture=contents.furniture;result.functionalZones=contents.zones;result.furnishingProgram=contents.program;result.roomsBasis=recorded?'documented':'invented-functional-zones';result.roomCoverage=recorded?'documented-record':'partial';if(!recorded)result.rooms=copy(contents.zones);
  result.signature=hash([b.id,b.rings,level,result.elevation,result.height,walls,result.furniture]);return result;
 }
 // New version-five visits may close the invented room openings. Twin
 // pocket leaves retract into the existing partition, so opening a door
 // never adds a swept obstacle to a proved circulation route. A short wall
 // cannot receive an invented pocket: keep its original open passage.
 const ROOM_DOOR_LIMIT=2048;
 function migrateRoomDoorStates(raw){const out={};if(raw&&typeof raw==='object'&&!Array.isArray(raw))for(const[k,v]of Object.entries(raw).slice(0,ROOM_DOOR_LIMIT))if(/^[a-f0-9]{16}$/.test(k)&&v===true)out[k]=true;return out;}
 function roomDoorPlan(l){
  const doors=[],omissions=[];if(l.layoutVersion!==5||l.provenance==='documented')return{doors,omissions};
  for(const[index,d]of(l.roomDoors||[]).entries()){
   const room=l.rooms.find(r=>r.id===d.roomId),a=room?.ring?.[d.side],b=room?.ring?.[d.side+1],wallLength=a&&b?Math.hypot(b[0]-a[0],b[1]-a[1]):0;
   if(!room||!finite(d.width)||d.width<.9||!finite(d.height)||d.height<1.85||wallLength<d.width*2+.02){omissions.push({index,roomId:d.roomId||null,reason:'insufficient-pocket-wall'});continue;}
   const dx=d.outside[0]-d.inside[0],dz=d.outside[1]-d.inside[1],length=Math.hypot(dx,dz);if(length<EPS)continue;
   const normal=[dx/length,dz/length],tangent=[-normal[1],normal[0]],id=hash([l.buildingId,l.level,l.signature,index,'pocket-door-v5']);
   doors.push({id,index,roomId:d.roomId,use:room.use,center:d.center.slice(),normal,tangent,width:d.width,height:d.height,thickness:.04,elevation:l.elevation,provenance:'invented',mechanism:'twin-pocket',defaultClosed:false});
  }return{doors,omissions};
 }
 function roomDoorGeometry(d,closed){
  const half=d.width/2,parts=[];
  for(const sign of[-1,1]){const distance=sign*(closed?d.width/4:d.width*.75),center=[d.center[0]+d.tangent[0]*distance,d.center[1]+d.tangent[1]*distance];parts.push({kind:'leaf',pos:[center[0],d.elevation+d.height/2,center[1]],size:[half-.012,d.height-.04,d.thickness],rotation:-Math.atan2(d.tangent[1],d.tangent[0]),material:'wood'});}
  if(closed)for(const sign of[-1,1])for(const side of[-1,1]){const h=sign*.055;parts.push({kind:'handle',pos:[d.center[0]+d.tangent[0]*h+d.normal[0]*side*.035,d.elevation+1.04,d.center[1]+d.tangent[1]*h+d.normal[1]*side*.035],size:[.025,.16,.025],rotation:0,material:'metal'});}
  const w=d.width/2,t=d.thickness/2,ring=[[-w,-t],[w,-t],[w,t],[-w,t]].map(([x,z])=>[d.center[0]+d.tangent[0]*x+d.normal[0]*z,d.center[1]+d.tangent[1]*x+d.normal[1]*z]);ring.push(ring[0].slice());
  return{parts,ring,minY:d.elevation,maxY:d.elevation+d.height,closed:!!closed};
 }
 function roomDoorOccupied(d,pos,radius=.38){if(!Array.isArray(pos)||pos.length!==3||!pos.every(finite))return true;const feet=pos[1]-1.65,head=pos[1]+.18;if(head<d.elevation||feet>d.elevation+d.height)return false;const dx=pos[0]-d.center[0],dz=pos[2]-d.center[1],along=Math.abs(dx*d.tangent[0]+dz*d.tangent[1]),across=Math.abs(dx*d.normal[0]+dz*d.normal[1]);return along<d.width/2+radius+.025&&across<radius+d.thickness/2+.025;}
 // Services attach only to an already placed, reachable piece of furniture.
 // They add no partition, fixture, water connection or claimed real amenity.
 const SERVICE_LIMIT=2048,SERVICE_KINDS={bed:'rest',medical_bed:'rest',kitchen:'kitchen',workbench:'workshop'},SERVICE_RECIPES={kitchen:['ration','purify'],workshop:['bandage','ceramic','parts','circuit','plate','10mm','shells','cells','rivets','harpoons','fragGrenade']};
 function serviceEdge(ring,from,to){let first=Infinity;const d=[to[0]-from[0],to[1]-from[1]];for(let i=0;i<ring.length;i++){const a=ring[i],b=ring[(i+1)%ring.length],e=[b[0]-a[0],b[1]-a[1]],den=d[0]*e[1]-d[1]*e[0];if(Math.abs(den)<EPS)continue;const q=[a[0]-from[0],a[1]-from[1]],t=(q[0]*e[1]-q[1]*e[0])/den,u=(q[0]*d[1]-q[1]*d[0])/den;if(t>=-EPS&&t<=1+EPS&&u>=-EPS&&u<=1+EPS)first=Math.min(first,t);}return finite(first)?[from[0]+d[0]*first,from[1]+d[1]*first]:null;}
 function servicePlan(l){
  const services=[],omissions=[];for(const f of l.furniture||[]){const kind=SERVICE_KINDS[f.kind];if(!kind)continue;
   const p=f.approach;if(!Array.isArray(p)||p.length!==2||!p.every(finite)||!walkable(l,...p,.38)||(l.furniture||[]).some(o=>furnitureBlocked(o,...p,.38))){omissions.push({furnitureId:f.id,reason:'no-proved-furniture-approach'});continue;}
   const parts=furnitureModel(f),def=furnitureDefinition(f),part=parts.map((part,index)=>({...part,index})).filter(part=>part.size[0]*part.size[2]>=def.size[0]*def.size[1]*.5-EPS).sort((a,b)=>b.pos[1]-a.pos[1])[0],angle=f.rotation||0,place=q=>{const r=rotate(q,angle);return[r[0]+f.pos[0],r[1]+f.pos[1]];};
   if(!part){omissions.push({furnitureId:f.id,reason:'no-visible-service-component'});continue;}const center=place([part.pos[0],part.pos[2]]),dx=center[0]-p[0],dz=center[1]-p[1],distance=Math.hypot(dx,dz);if(distance<.1){omissions.push({furnitureId:f.id,reason:'invalid-furniture-approach'});continue;}
   const partRing=rectangle(part.pos[0]-part.size[0]/2,part.pos[2]-part.size[2]/2,part.size[0],part.size[2]).map(place),edge=serviceEdge(furnitureRing(f),p,center),mesh=serviceEdge(partRing,p,center);
   if(!edge||!mesh){omissions.push({furnitureId:f.id,reason:'no-visible-service-edge'});continue;}const target=[edge[0]-dx/distance*.035,l.elevation+part.pos[1],edge[1]-dz/distance*.035],meshAnchor=[mesh[0],target[1],mesh[1]],meshCenter=[center[0],target[1],center[1]],meshOffset=Math.hypot(target[0]-mesh[0],target[2]-mesh[1]);
   if(meshOffset>.16||!canTravel(l,p,[target[0],target[2]],.04)){omissions.push({furnitureId:f.id,reason:'obstructed-or-distant-service-edge'});continue;}
   services.push({id:hash([l.buildingId,l.level,l.signature,f.id,kind,'furniture-service-v1']),kind,furnitureId:f.id,furnitureKind:f.kind,label:f.label,approach:p.slice(),target,meshAnchor,meshCenter,meshPart:{index:part.index,material:part.material,offsetMeters:meshOffset},provenance:'invented'});
  }return{services,omissions};
 }
 // Interactions use the actual rendered boxes, in furniture-local space.
 // Looking at the former reserve point or empty space does not select a bed
 // or workbench merely because its service has a higher priority.
 function serviceAim(l,s,origin,direction){
  if(![origin,direction].every(v=>Array.isArray(v)&&v.length===3&&v.every(finite)))return null;const f=l.furniture?.find(f=>f.id===s.furnitureId),length=Math.hypot(...direction);if(!f||length<.5)return null;const p=rotate([origin[0]-f.pos[0],origin[2]-f.pos[1]],-(f.rotation||0)),d=rotate([direction[0]/length,direction[2]/length],-(f.rotation||0)),o=[p[0],origin[1]-l.elevation,p[1]],ray=[d[0],direction[1]/length,d[1]],parts=furnitureModel(f);let nearest=4.5,selected=null;
  for(const[index,part]of parts.entries()){let lo=0,hi=4.5,valid=true;for(let axis=0;axis<3;axis++){const a=part.pos[axis]-part.size[axis]/2,b=part.pos[axis]+part.size[axis]/2;if(Math.abs(ray[axis])<EPS){if(o[axis]<a||o[axis]>b){valid=false;break;}}else{let x=(a-o[axis])/ray[axis],z=(b-o[axis])/ray[axis];if(x>z)[x,z]=[z,x];lo=Math.max(lo,x);hi=Math.min(hi,z);if(lo>hi){valid=false;break;}}}if(valid&&lo<nearest){nearest=lo;selected={partIndex:index,material:part.material,distanceMeters:lo,point:origin.map((v,i)=>v+direction[i]/length*lo)};}}
  return selected;
 }
 function migrateServices(raw){const out={restHours:0,crafts:0,uses:{}};if(!raw||typeof raw!=='object'||Array.isArray(raw))return out;for(const k of['restHours','crafts'])if(Number.isInteger(raw[k])&&raw[k]>=0)out[k]=Math.min(1000000,raw[k]);if(raw.uses&&typeof raw.uses==='object'&&!Array.isArray(raw.uses))for(const[k,v]of Object.entries(raw.uses).slice(0,SERVICE_LIMIT))if(/^[a-f0-9]{16}$/.test(k)&&Number.isInteger(v)&&v>0)out.uses[k]=Math.min(1000000,v);return out;}
 return{EPS,MAX_POINTS,MAX_LEVELS,hash,area,bounds,inside,clearance,segmentDistance,cleanRings,building,validateBuilding,point,intervals,document,floorLevels,alignStreet,theme,program,roomProgram,programTheme,programTheme4,PLAN_BUDGET,FURNITURE,COMPACT_FURNITURE,furnitureDefinition,furnishingFits,furnitureModel,furnitureRing,furnitureBlocked,walkable,canTravel,layout,ROOM_DOOR_LIMIT,migrateRoomDoorStates,roomDoorPlan,roomDoorGeometry,roomDoorOccupied,SERVICE_LIMIT,SERVICE_KINDS,SERVICE_RECIPES,servicePlan,serviceAim,migrateServices};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralCityInteriors;

/* Runtime is separate from the geometry module so source tests can exercise
   real polygon logic without fabricating the rest of a campaign. */
if(typeof baseState==='function'){
 const V050_CITY_ZONE='v050_city_interior';
 // User registrations live in the save, bounded in UTF-16 storage bytes.
 // Installed atlas plans remain source data; only the active visit snapshots one.
 const V050_DOCUMENT_LIMITS={buildings:32,bytes:512*1024};
 const V050_CITY={doors:new Map(),owner:null,tick:0,documentOwner:null,documentRejections:new Map(),holding:false,exitPending:null,entered:0,returned:0,errors:[],last:null,rejections:{}};
 if(!ALL_ZONE_IDS.includes(V050_CITY_ZONE))ALL_ZONE_IDS.push(V050_CITY_ZONE);
 function fresh(){return{schema:2,active:null,returnPoint:null,visits:{},documents:[],documentOmissions:0,documentWarnings:[],roomDoorStates:{},services:MistralCityInteriors.migrateServices(null)};}
 function documentBytes(records){return JSON.stringify(records).length*2;}
 // Guessed floor schedules and labels are not measurements. A documentary
 // schedule replaces those guesses, but never a changed footprint or volume.
 function documentMetricKey(b){const rings=MistralFacades.normalized(b.rings);if(!rings)throw Error('Empreinte documentaire invalide');return MistralCityInteriors.hash([b.id,b.origin,b.height,b.levels,MistralFacades.geometryIdentity(rings)]);}
 function documentRecord(building,raw){const b=MistralCityInteriors.validateBuilding(building);return{building:b,document:MistralCityInteriors.document(raw,b)};}
 function documentPut(records,record){const next=records.filter(r=>r.building.id!==record.building.id).concat([record]);if(next.length>V050_DOCUMENT_LIMITS.buildings)throw Error('Registre des plans limité à '+V050_DOCUMENT_LIMITS.buildings+' bâtiments ; utilisez un atlas installé pour les collections plus grandes.');if(documentBytes(next)>V050_DOCUMENT_LIMITS.bytes)throw Error('Registre des plans limité à 512 Kio dans la sauvegarde ; utilisez un atlas installé pour les plans volumineux.');return next;}
 function documentWarning(target,message,count=1){target.documentOmissions+=count;if(target.documentWarnings.length<12)target.documentWarnings.push(String(message).slice(0,240));}
 function documentRejected(id,message){if(V050_CITY.documentOwner!==state){V050_CITY.documentOwner=state;V050_CITY.documentRejections.clear();}const key=id+':'+message;if(!V050_CITY.documentRejections.has(key)){if(V050_CITY.documentRejections.size>=64)V050_CITY.documentRejections.delete(V050_CITY.documentRejections.keys().next().value);V050_CITY.documentRejections.set(key,{building:id,reason:String(message).slice(0,240)});}}
 function resolvedDocument(b,attached=null){
  if(V050_CITY.documentOwner!==state){V050_CITY.documentOwner=state;V050_CITY.documentRejections.clear();}
  const records=state.v050City?.documents;if(Array.isArray(records)){const record=records.find(r=>r?.building?.id===b.id);if(record)try{if(documentMetricKey(record.building)!==documentMetricKey(b))throw Error('Le volume source a changé ; le plan sauvegardé ne lui est pas appliqué.');return{document:MistralCityInteriors.document(record.document,b),origin:'registered'};}catch(e){documentRejected(b.id,e.message||e);}}
  if(attached!=null)try{return{document:MistralCityInteriors.document(attached,b),origin:'installed'};}catch(e){documentRejected(b.id,'Plan installé refusé : '+String(e.message||e));}
  return null;
 }
 function migrate(raw){
  const f=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return f;
  f.roomDoorStates=MistralCityInteriors.migrateRoomDoorStates(raw.roomDoorStates);
  f.services=MistralCityInteriors.migrateServices(raw.services);
  if(raw.documents!=null){if(!Array.isArray(raw.documents))documentWarning(f,'Registre documentaire sauvegardé invalide.');else{
   if(raw.documents.length>V050_DOCUMENT_LIMITS.buildings)documentWarning(f,'Plans supplémentaires hors budget du registre sauvegardé.',raw.documents.length-V050_DOCUMENT_LIMITS.buildings);
   const seen=new Set();for(const entry of raw.documents.slice(0,V050_DOCUMENT_LIMITS.buildings))try{if(documentBytes([entry])>V050_DOCUMENT_LIMITS.bytes)throw Error('Plan sauvegardé hors budget.');const record=documentRecord(entry?.building,entry?.document);if(seen.has(record.building.id))throw Error('Identifiant de plan sauvegardé dupliqué.');seen.add(record.building.id);f.documents=documentPut(f.documents,record);}catch(e){documentWarning(f,e.message||e);}
  }}
  const r=raw.returnPoint;if(r&&typeof r.macro==='string'&&V015_GEO_MACROS[r.macro]&&Array.isArray(r.pos)&&r.pos.length===3&&r.pos.every(Number.isFinite)){
   // Source identities and their declared bounds exist before asynchronous
   // city index loading. A cold interior save must not depend on whether the
   // measured exterior bank has finished registering those same bounds.
   const box=V015_GEO_MACROS[r.macro].bbox,ll=v015GeoUnproject(r.macro,r.pos[0],r.pos[2]);
   if(Array.isArray(box)&&box.length===4&&box.every(Number.isFinite)&&box[0]<box[2]&&box[1]<box[3]&&Array.isArray(ll)&&ll.length>=2&&ll.slice(0,2).every(Number.isFinite)&&ll[0]>=box[0]&&ll[0]<=box[2]&&ll[1]>=box[1]&&ll[1]<=box[3])f.returnPoint={macro:r.macro,pos:r.pos.slice(),yaw:Number.isFinite(r.yaw)?r.yaw:0,pitch:Number.isFinite(r.pitch)?r.pitch:0};
  }
  if(raw.active&&f.returnPoint){try{const b=MistralCityInteriors.validateBuilding(raw.active.building),floor=raw.active.floor,entry=raw.active.entry,streetFloor=raw.active.streetFloor??0;if(!Number.isInteger(floor)||floor<0||floor>=b.levels||!Number.isInteger(streetFloor)||streetFloor<0||streetFloor>=b.levels||!Array.isArray(entry)||entry.length!==2||!entry.every(Number.isFinite))throw Error('Étage sauvegardé invalide');const doc=raw.active.document?MistralCityInteriors.document(raw.active.document,b):null;MistralCityInteriors.layout(b,floor,entry,doc);const facing=Array.isArray(raw.active.facing)&&raw.active.facing.length===2&&raw.active.facing.every(Number.isFinite)?raw.active.facing.slice():[-entry[0],-entry[1]],documentOrigin=doc?(['registered','installed','legacy'].includes(raw.active.documentOrigin)?raw.active.documentOrigin:'legacy'):null;f.active={building:b,floor,streetFloor,entry:entry.slice(),facing,document:doc,documentOrigin};}catch{}}
  // Older saves held only the current documentary snapshot. Recover it before
  // leaving that interior; a later explicit registry revision remains separate
  // from the immutable geometry of the currently visited floor.
  if(f.active?.document&&f.active.documentOrigin!=='installed')try{const a=f.active,record=f.documents.find(r=>r.building.id===a.building.id);if(!record)f.documents=documentPut(f.documents,documentRecord(a.building,a.document));else if(documentMetricKey(record.building)!==documentMetricKey(a.building))documentWarning(f,'Le plan actif et le registre désignent deux volumes différents ; leurs instantanés restent séparés.');}catch(e){documentWarning(f,e.message||e);}
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
 function applyRoomDoor(rec,closed){
  const shape=MistralCityInteriors.roomDoorGeometry(rec.door,closed);rec.closed=!!closed;rec.collider.disabled=!closed;
  for(let i=0;i<rec.draws.length;i++){const draw=rec.draws[i],part=shape.parts[i];draw.hidden=!part;if(part){draw.pos=part.pos.slice();draw.scale=part.size.slice();draw.rotY=part.rotation;draw.revision=(draw.revision||0)+1;}}
  rec.interaction.label=(closed?'Ouvrir':'Fermer')+' · '+rec.door.use+' · porte coulissante';
 }
 function toggleRoomDoor(id,expectedWorld=world,expectedState=state){
  const rec=world?.v055RoomDoors?.get(id),active=state.v050City?.active;
  if(!rec||world!==expectedWorld||state!==expectedState||rec.owner!==state||!active||active.building.layoutVersion!==5||!['PLAYING'].includes(mode)||state.player.hp<=0||V046.busy||V047.pending||zoneTransitioning||V050_CITY.holding||V050_CITY.exitPending)return false;
  const d=rec.door,p=state.player.pos,distance=Math.hypot(p[0]-d.center[0],p[2]-d.center[1]),side=(p[0]-d.center[0])*d.normal[0]+(p[2]-d.center[1])*d.normal[1]>=0?1:-1,target=[d.center[0]+d.normal[0]*side*.14,d.elevation+1.04,d.center[1]+d.normal[1]*side*.14];
  if(distance>2.4||Math.abs(p[1]-(d.elevation+playerEyeHeight()))>.7||!MistralCityInteriors.canTravel(world.v050CityInterior,[p[0],p[2]],[target[0],target[2]],.04)||!lineOfSight(p,target))return false;
  const closed=!rec.closed;if(closed&&MistralCityInteriors.roomDoorOccupied(d,p,state.player.crouched?.32:.38)){toast('Écartez-vous du passage avant de fermer la porte.','bad');return false;}
  const states=state.v050City.roomDoorStates;if(closed&&!states[id]&&Object.keys(states).length>=MistralCityInteriors.ROOM_DOOR_LIMIT){toast('Le registre des portes est plein ; ce passage reste ouvert.','bad');return false;}
  const s=snapshot(),previous=rec.closed,ok=commit(s,()=>{if(closed)states[id]=true;else delete states[id];applyRoomDoor(rec,closed);});
  if(!ok)applyRoomDoor(rec,previous);return ok;
 }
 function installRoomDoors(w,l,materials){
  const plan=MistralCityInteriors.roomDoorPlan(l);w.v055RoomDoors=new Map();w.v055RoomDoorOmissions=plan.omissions;
  for(const door of plan.doors){const shape=MistralCityInteriors.roomDoorGeometry(door,true),draws=shape.parts.map((p,i)=>{const draw=addBox(w,p.pos,p.size,materials[p.material],p.rotation,{id:'city-room-door:'+door.id+':'+i});draw.v055RoomDoor={id:door.id,kind:p.kind,provenance:'invented'};return draw;}),collider=v017AddPolyCollider(w,shape.ring,shape.minY,shape.maxY,{id:'city-room-door:'+door.id});collider.v055RoomDoor={id:door.id,provenance:'invented'};
   const owner=state,interaction=addInteract(w,'city-room-door:'+door.id,[door.center[0],door.elevation+1.04,door.center[1]],'Porte coulissante',()=>toggleRoomDoor(door.id,w,owner),{kind:'door',radius:2.4,priority:9}),rec={owner,door,draws,collider,interaction,closed:false};interaction.v055RoomDoor=door.id;w.v055RoomDoors.set(door.id,rec);applyRoomDoor(rec,!!state.v050City.roomDoorStates[door.id]);
  }
 }
 function serviceReady(id,expectedWorld=world,expectedState=state){
  const rec=world?.v056InteriorServices?.get(id),l=world?.v050CityInterior,p=state.player.pos;
  if(!rec||rec.owner!==state||state!==expectedState||world!==expectedWorld||!l||!state.v050City?.active||!['PLAYING','DIALOGUE'].includes(mode)||state.player.hp<=0||V046.busy||V047.pending||zoneTransitioning||V050_CITY.holding||V050_CITY.exitPending||!onGround)return false;
  if(state.v055Ordnance?.armed?.zone===world.id)return false;
  if(Math.hypot(p[0]-rec.service.approach[0],p[2]-rec.service.approach[1])>2.2||Math.abs(p[1]-l.elevation-playerEyeHeight())>.7||!MistralCityInteriors.canTravel(l,[p[0],p[2]],[rec.service.target[0],rec.service.target[2]],.04)||!lineOfSight(p,rec.service.target))return false;
  if((world.enemies||[]).some(e=>e.alive&&Math.hypot(e.pos[0]-p[0],e.pos[2]-p[2])<25&&lineOfSight(p,[e.pos[0],e.pos[1]+1,e.pos[2]])))return false;
  return rec;
 }
 function serviceRecipe(rec,id){return(MistralCityInteriors.SERVICE_RECIPES[rec.service.kind]||[]).includes(id)&&typeof V020_RECIPES!=='undefined'?V020_RECIPES.find(r=>r.id===id):null;}
 function useService(id,action,expectedWorld=world,expectedState=state){
  const rec=serviceReady(id,expectedWorld,expectedState);if(!rec)return false;const rest=rec.service.kind==='rest',hours=action==='rest:1'?1:action==='rest:4'?4:0,recipe=rest?null:serviceRecipe(rec,action),cost=rest?hours===1?{water:1}:{water:1,ration:1}:recipe?.cost;
  if(rest&&(!hours||['infection','bleeding','burning'].some(k=>state.status?.[k]>0))||!rest&&!recipe||!cost||typeof hasCost!=='function'||!hasCost(cost))return false;
  const s=snapshot(),ok=commit(s,()=>{
   if(typeof v020Spend!=='function'||!v020Spend(cost))throw Error('Réserves devenues insuffisantes ; le service est annulé.');
   const ledger=state.v050City.services;if(rest){
    state.worldTime=((state.worldTime||0)+hours)%24;ledger.restHours=Math.min(1000000,ledger.restHours+hours);state.player.hp=Math.min(state.player.maxHp,state.player.hp+12*hours);state.player.ap=state.player.maxAp;
    if(state.needs){state.needs.fatigue=Math.max(0,(state.needs.fatigue||0)-25*hours);state.needs.thirst=Math.max(0,(state.needs.thirst||0)-20);if(hours===4)state.needs.hunger=Math.max(0,(state.needs.hunger||0)-25);}if(state.v020)state.v020.restHours=(state.v020.restHours||0)+hours;
   }else{
    if(typeof AMMO_INFO!=='undefined'&&AMMO_INFO[recipe.item])addAmmo(recipe.item,recipe.count);else addItem(recipe.item,recipe.count);ledger.crafts=Math.min(1000000,ledger.crafts+1);if(state.v020?.craftCount)state.v020.craftCount[recipe.id]=(state.v020.craftCount[recipe.id]||0)+1;
   }
   if(ledger.uses[id]||Object.keys(ledger.uses).length<MistralCityInteriors.SERVICE_LIMIT)ledger.uses[id]=Math.min(1000000,(ledger.uses[id]||0)+1);
  });
  if(ok){closeDialogue();toast(rest?hours+' h de repos · blessures et radiations conservées.':recipe.name+' · préparation terminée.','good');updateHUD();}return ok;
 }
 function openService(id,expectedWorld=world,expectedState=state,page=0){
  const rec=serviceReady(id,expectedWorld,expectedState);if(!rec)return false;const s=rec.service,choices=[];
  if(s.kind==='rest')for(const hours of[1,4])choices.push({text:hours===1?'Se reposer 1 h · 1 eau':'Dormir 4 h · 1 eau et 1 ration',condition:()=>!!serviceReady(id,expectedWorld,expectedState)&&hasCost(hours===1?{water:1}:{water:1,ration:1})&&!['infection','bleeding','burning'].some(k=>state.status?.[k]>0),lockText:'Réserves insuffisantes ou blessure active : soignez infection, saignement et brûlure avant le repos.',onChoose:()=>useService(id,'rest:'+hours,expectedWorld,expectedState)});
  else{const recipes=MistralCityInteriors.SERVICE_RECIPES[s.kind].map(id=>serviceRecipe(rec,id)).filter(Boolean),pages=Math.max(1,Math.ceil(recipes.length/5)),at=Math.max(0,Math.min(pages-1,Number.isInteger(page)?page:0));for(const r of recipes.slice(at*5,at*5+5))choices.push({text:r.name+' · '+costText(r.cost),condition:()=>!!serviceReady(id,expectedWorld,expectedState)&&hasCost(r.cost),lockText:'Ingrédients insuffisants ou mobilier devenu inaccessible ; aucun paiement effectué.',onChoose:()=>useService(id,r.id,expectedWorld,expectedState)});if(pages>1)choices.push({text:'Autres préparations · '+(at+1)+'/'+pages,onChoose:()=>openService(id,expectedWorld,expectedState,(at+1)%pages)});}
  choices.push({text:'Continuer la visite',onChoose:closeDialogue});
  openDialogue(speaker(s.label,s.kind==='rest'?'REPOS À COUVERT':s.kind==='kitchen'?'PRÉPARATION DES RÉSERVES':'ÉTABLI DE RÉCUPÉRATION','⚙'),s.kind==='rest'?'Ce couchage permet une halte à couvert. Une heure rend 12 PV, quatre heures 48 PV et restaurent les PA ; eau et ration viennent de votre sac. Soignez infection, saignement et brûlure avant le repos. Les radiations et blessures ne sont pas effacées.':'Installez vos outils et préparez vos réserves. Les ingrédients viennent de votre sac ; vérifiez vos fournitures avant de commencer.',choices);return true;
 }
 function installServices(w,l){
  const plan=MistralCityInteriors.servicePlan(l);w.v056InteriorServices=new Map();w.v056InteriorServiceOmissions=plan.omissions;
  for(const service of plan.services){const owner=state,label=service.kind==='rest'?'Se reposer · '+service.label:service.kind==='kitchen'?'Préparer des réserves · cuisine':'Fabriquer · établi de récupération',interaction=addInteract(w,'city-service:'+service.id,service.target.slice(),label,()=>openService(service.id,w,owner),{kind:service.kind==='rest'?'rest':'bench',radius:2.4,priority:10,condition:()=>!!serviceReady(service.id,w,owner)&&!!MistralCityInteriors.serviceAim(l,service,state.player.pos,cameraDir(state.player.yaw,state.player.pitch))});interaction.v056InteriorService=service.id;w.v056InteriorServices.set(service.id,{owner,service,interaction});}
 }
 function build(){
  const a=state.v050City.active;if(!a)throw Error('Aucun intérieur de bâtiment sélectionné');const b=a.building,l=MistralCityInteriors.layout(b,a.floor,a.entry,a.document),palette={residential:{floor:[.34,.29,.22],wall:[.62,.56,.44]},medical:{floor:[.37,.43,.39],wall:[.58,.65,.59]},industrial:{floor:[.29,.29,.27],wall:[.42,.43,.40]},annex:{floor:[.29,.29,.27],wall:[.42,.43,.40]},sports:{floor:[.35,.37,.30],wall:[.61,.61,.49]},office:{floor:[.35,.34,.28],wall:[.60,.59,.50]},education:{floor:[.38,.34,.25],wall:[.66,.64,.51]},commercial:{floor:[.34,.33,.29],wall:[.58,.57,.49]},civic:{floor:[.42,.38,.31],wall:[.64,.60,.50]}}[l.theme];
  const w=createWorld(V050_CITY_ZONE,b.name,`MARSEILLE · ${a.floor?'NIVEAU '+a.floor:'REZ-DE-CHAUSSÉE'}`,{indoor:true,daylight:.32,fog:[.21,.24,.20],wind:0});w.v050CityInterior=l;w.v050CityBuilding=b;const bb=MistralCityInteriors.bounds(l.rings);w.bounds=[bb.minX-.1,bb.maxX+.1,bb.minZ-.1,bb.maxZ+.1];w.spawn=[l.entry[0],l.elevation+playerEyeHeight(),l.entry[1]];const facing=a.facing||[-l.entry[0],-l.entry[1]];w.spawnYaw=Math.atan2(facing[0],-facing[1]);
  surface(w,l.rings,l.elevation,palette.floor,'city-floor:'+l.signature);surface(w,l.rings,l.elevation+l.height-.08,cMix(palette.wall,COLORS.black,.25),'city-ceiling:'+l.signature);
  for(let r=0;r<l.rings.length;r++)for(let i=0;i<l.rings[r].length;i++)wall(w,l.rings[r][i],l.rings[r][(i+1)%l.rings[r].length],l.elevation,l.height,palette.wall,`city-boundary:${r}:${i}`,.2);
  for(let i=0;i<l.walls.length;i++){const p=l.walls[i];wall(w,p.a,p.b,l.elevation,Math.max(1.8,l.height-.08),cMix(palette.wall,COLORS.limestone,.08),'city-partition:'+i,p.thickness);}
  for(let i=0;i<(l.roomDoors||[]).length;i++){const d=l.roomDoors[i],dx=d.outside[0]-d.inside[0],dz=d.outside[1]-d.inside[1],length=Math.hypot(dx,dz),tx=-dz/length*d.width/2,tz=dx/length*d.width/2;if(d.height<l.height-.08)wall(w,[d.center[0]-tx,d.center[1]-tz],[d.center[0]+tx,d.center[1]+tz],l.elevation+d.height,l.height-.08-d.height,palette.wall,'city-room-lintel:'+i,.16);}
  const materials={wood:[.39,.30,.21],fabric:[.32,.39,.32],blanket:[.43,.45,.28],metal:[.29,.32,.29],dark:[.15,.18,.16],porcelain:[.69,.70,.61],medical:[.48,.62,.54],paper:[.72,.68,.53],glass:[.17,.31,.28],water:[.25,.37,.35],amber:[.64,.48,.22]};
  for(let i=0;i<l.furniture.length;i++){const f=l.furniture[i],[x,z]=f.pos,y=l.elevation,parts=MistralCityInteriors.furnitureModel(f),angle=f.rotation||0,c=Math.cos(angle),s=Math.sin(angle);for(let j=0;j<parts.length;j++){const part=parts[j],draw=addBox(w,[x+c*part.pos[0]-s*part.pos[2],y+part.pos[1],z+s*part.pos[0]+c*part.pos[2]],part.size,materials[part.material]||materials.wood,-angle,{id:`city-furniture:${i}:part:${j}`});draw.v050CityFurnishing={id:f.id,kind:f.kind,provenance:'invented'};}const collider=f.ring?v017AddPolyCollider(w,f.ring,y,y+f.height,{id:'city-furniture:'+i}):addCollider(w,x,z,f.size[0],f.size[1],{id:'city-furniture:'+i,minY:y,maxY:y+f.height});collider.v050CityFurnishing={id:f.id,kind:f.kind,provenance:'invented'};}
  installRoomDoors(w,l,materials);
  installServices(w,l);
  const[x,z]=l.entry,y=l.elevation;
  addBox(w,[x,y+.06,z],[.65,.12,.65],[.57,.52,.28]);
  const inspect=()=>{
   const use=b.programmeUse,useLabel=b.layoutVersion>=4?(use.basis==='source-attribute'?`Usage source (${use.field}) : ${use.value}.`:use.basis==='architecture-annotation'?`Usage d’annotation d’architecture : ${use.value}.`:'Usage du programme choisi ou repris sans catégorie source précise.'):'',source=l.source,uses=[...new Set(l.functionalZones.map(z=>z.use))].join(', '),coverage=l.programCoverage,description=coverage?`${l.rooms.length} pièce(s) close(s), portes de 1,20 m et espace restant conservé comme volume ouvert et circulation. ${coverage.roomOmissions.length} pièce(s) et ${coverage.furnishingOmissions.length} fonction(s) du programme non placées faute de place, de passage ou de budget.`:'Zones fonctionnelles partielles ; aucun relevé des pièces.',text=`${b.name}\nEmpreinte extérieure conservée à l’échelle métrique, cours exclues.\n${l.levels} niveau(x) : ${b.levelsBasis}.\nNiveau courant : ${l.provenance==='documented'?'plan documenté':'plan inventé, cohérent avec le volume et l’usage disponibles'}.\nLe mobilier et les réserves sont fictifs.${useLabel?'\n'+useLabel:''}\nProgramme inventé : ${uses||'pas de mobilier ajouté lorsque le passage manque'}. ${l.provenance==='documented'?'Les contours et murs documentés sont conservés ; leurs équipements sont inventés.':description}\n${source?source.title+'\n'+source.url+'\n'+source.license+' · '+source.attribution:'Aucun relevé public des pièces n’est attaché à ce bâtiment.'}`;
   openNote('city-plan:'+MistralCityInteriors.hash(b.id),b.name,text+(l.layoutVersion===5&&l.provenance!=='documented'?'\nLes portes coulissantes et leurs poches sont inventées ; elles restent ouvertes par défaut. Chaque fermeture est conservée dans cette sauvegarde.':''));
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
  const stash=l.furniture.find(f=>f.approach||MistralCityInteriors.walkable(l,...f.pos,.8));
  if(stash&&typeof v026NewContainer==='function'){const id='city:'+MistralCityInteriors.hash(b.id)+':'+a.floor,p=stash.approach?[stash.approach[0],y,stash.approach[1]]:[stash.pos[0],y,stash.pos[1]+stash.size[1]/2+.12],seed=parseInt(MistralCityInteriors.hash(id).slice(0,6),16),items=l.theme==='medical'?{cloth:1,water:1}:l.theme==='industrial'?{scrap:1+seed%3}:{cloth:1,scrap:1};const[key,c]=v026NewContainer(w,id,'Réserve fictive · '+b.name,p,items,{kind:'chest'});c.pos=p.slice();v026Attach(w,key,c);}
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
  if(world?.v046&&V050_CITY.owner?.state!==state)bind(true);
  const rec=V050_CITY.doors.get(id);if(!rec||rec.world!==world||!world?.v046||V046.busy||V047.pending||zoneTransitioning||!['PLAYING','DIALOGUE'].includes(mode)||state.player.hp<=0||!near(rec.interaction,rec.interaction.radius+.1)||!lineOfSight(state.player.pos,rec.interaction.pos))return false;
  if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat()){toast('Éloignez-vous du danger avant d’entrer.','bad');return false;}
  closeDialogue();const s=snapshot(),descriptor=rec.building,entry=[rec.door.inside[0]-descriptor.origin[0],rec.door.inside[2]-descriptor.origin[2]],resolved=rec.document?{document:rec.document,origin:rec.documentOrigin}:resolvedDocument(descriptor),doc=resolved?.document||null,documentOrigin=resolved?.origin||null,streetFloor=rec.streetFloor??0;
  const ok=commit(s,()=>{MistralCityInteriors.layout(descriptor,streetFloor,entry,doc);state.v050City.returnPoint={macro:world.id,pos:state.player.pos.slice(),yaw:state.player.yaw,pitch:state.player.pitch};state.v050City.active={building:descriptor,floor:streetFloor,streetFloor,entry,facing:rec.door.normal.map(n=>-n),document:doc,documentOrigin};const k=MistralCityInteriors.hash(descriptor.id);state.v050City.visits[k]=(state.v050City.visits[k]||0)+1;loadZone(V050_CITY_ZONE,{instance:true,force:true,silent:true,noTravel:true});if(world?.id!==V050_CITY_ZONE)throw Error('L’intérieur n’a pas été chargé');});
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
 const newGame=startNewGame;startNewGame=function(...args){V050_CITY.exitPending=null;V050_CITY.doors.clear();V050_CITY.owner=null;V050_CITY.documentOwner=null;V050_CITY.documentRejections.clear();return newGame(...args);};
 function bind(force=false){
  if(!world?.v046||typeof MistralFacades==='undefined'){V050_CITY.doors.clear();V050_CITY.owner=null;return 0;}
  const pos=state.player.pos,stamp=world.v046Records;if(!force&&V050_CITY.owner?.state===state&&V050_CITY.owner.world===world&&V050_CITY.owner.stamp===stamp&&Math.hypot(pos[0]-V050_CITY.owner.x,pos[2]-V050_CITY.owner.z)<12)return V050_CITY.doors.size;
  world.interactables=world.interactables.filter(i=>!i.v050CityDoor);V050_CITY.doors.clear();const candidates=[],seen=new Set(),rejections={nearbyBuildings:0,invalidVolume:0,unmeasuredApproach:0,unmatchedStreetLevel:0,blockedApproach:0,narrowDoor:0,noCandidate:0,eligible:0,interactions:0};
  for(const d of world.staticDraws){if(d.geoLayer!=='building'||!d.rings||d.hidden)continue;d.v050EntranceSelection=null;const bb=MistralCityInteriors.bounds(d.rings);if(pos[0]<bb.minX-100||pos[0]>bb.maxX+100||pos[2]<bb.minZ-100||pos[2]>bb.maxZ+100)continue;
   try{const description=MistralFacades.describe(d);if(!description||seen.has(description.id))continue;seen.add(description.id);rejections.nearbyBuildings++;const b=MistralCityInteriors.building(description),resolved=resolvedDocument(b,description.properties?.interiorDocument),doc=resolved?.document||null,documentOrigin=resolved?.origin||null;let accepted=false;
    for(const original of MistralFacades.entrances(d,{near:[pos[0],pos[2]]})){const p=original.outside;if(!p||!p.every(Number.isFinite))continue;const distance=Math.hypot(p[0]-pos[0],p[2]-pos[2]);if(distance>100)continue;const h=v047Height(v047Bank(world),p[0],p[2]).height;if(h===null){rejections.unmeasuredApproach++;continue;}if(collidesAt(p[0],p[2],.38,h+playerEyeHeight())){rejections.blockedApproach++;continue;}
     const local=[original.inside[0]-b.origin[0],original.inside[2]-b.origin[2]];if(MistralCityInteriors.clearance(b.rings,...local)<.43){rejections.narrowDoor++;continue;}const aligned=MistralCityInteriors.alignStreet(b,h,doc);if(!aligned||original.provenance==='documented'&&Math.abs(original.center[1]-(b.origin[1]+aligned.elevation))>.05){rejections.unmatchedStreetLevel++;continue;}
     const grid=MistralCityInteriors.floorLevels(aligned.building,doc),storeyHeight=(grid[aligned.level+1]??b.height)-grid[aligned.level],doorHeight=original.provenance==='documented'?original.height:Math.min(original.height,storeyHeight-.08);if(doorHeight<1.85||doorHeight>storeyHeight-.08+1e-7||aligned.elevation+doorHeight>b.height){rejections.unmatchedStreetLevel++;continue;}
     const door={...original,height:doorHeight,levelElevations:grid.slice(),elevationOffset:aligned.elevation,thresholdMeters:aligned.thresholdMeters,center:[original.center[0],b.origin[1]+aligned.elevation,original.center[2]],inside:[original.inside[0],b.origin[1]+aligned.elevation,original.inside[2]],outside:[original.outside[0],h,original.outside[2]]};candidates.push({distance,door,draw:d,building:aligned.building,document:doc,documentOrigin,streetFloor:aligned.level,pos:[p[0],h+1.1,p[2]]});accepted=true;break;}
    if(!accepted)rejections.noCandidate++;
   }catch(e){rejections.invalidVolume++;/* A tiny non-visitable shed remains a real exterior footprint. */}
  }
  candidates.sort((a,b)=>a.distance-b.distance||a.door.id.localeCompare(b.door.id));
  for(const c of candidates.slice(0,64)){c.draw.v050EntranceSelection=c.door;const id='city-door:'+MistralCityInteriors.hash([c.building.id,c.door.id]),it=addInteract(world,id,c.pos,'Entrer · '+c.building.name+' · intérieur '+(c.document?'documenté selon niveaux':'inventé'),()=>enter(id),{kind:'door',radius:3.2,priority:2});it.v050CityDoor=true;V050_CITY.doors.set(id,{world,door:c.door,building:c.building,document:c.document,documentOrigin:c.documentOrigin,streetFloor:c.streetFloor,interaction:it});}
  rejections.eligible=candidates.length;rejections.interactions=V050_CITY.doors.size;V050_CITY.owner={state,world,stamp,x:pos[0],z:pos[2]};return V050_CITY.doors.size;
 }
 const publish=v046Publish;v046Publish=function(...args){const result=publish(...args);V050_CITY.owner=null;if(args[0]===world)bind(true);return result;};
 const update=updatePlayer;updatePlayer=function(dt){const r=update(dt),l=world?.v050CityInterior;if(l&&state.player.pos[1]+.18>l.elevation+l.height-.08){state.player.pos[1]=Math.max(l.elevation+playerEyeHeight(),l.elevation+l.height-.261);if(jumpVelocity>0)jumpVelocity=0;onGround=false;}V050_CITY.tick+=Number.isFinite(dt)?dt:0;if(V050_CITY.tick>.5){V050_CITY.tick=0;if(!V046.busy&&!V047.pending&&!zoneTransitioning)bind();}return r;};
 function registerDocument(raw){
  if(V046.busy||V047.pending||zoneTransitioning||V050_CITY.holding||V050_CITY.exitPending)throw Error('Attendez la fin du passage avant d’enregistrer un plan.');
  if(world?.v046&&V050_CITY.owner?.state!==state)bind(true);
  const current=[...V050_CITY.doors.values()].find(x=>x.building.id===raw?.buildingId)?.building||state.v050City.active?.building;if(!current||current.id!==raw?.buildingId)throw Error('Le bâtiment du plan doit être chargé');
  let record,next;try{if(documentBytes([{building:current,document:raw}])>V050_DOCUMENT_LIMITS.bytes)throw Error('Plan fourni hors budget du registre de 512 Kio.');record=documentRecord(current,raw);next=documentPut(state.v050City.documents||[],record);}catch(e){documentRejected(current.id,e.message||e);throw e;}
  const s=snapshot(),activeSnapshotPreserved=state.v050City.active?.building.id===current.id;
  V050_CITY.holding=true;try{state.v050City.documents=next;V050_CITY.owner=null;bind(true);V050_CITY.holding=false;if(state!==s.owner||saveBase(false)===false)throw Error('Le plan n’a pas été sauvegardé ; l’enregistrement est annulé.');}catch(e){restore(s);bind(true);documentRejected(current.id,e.message||e);throw e;}finally{V050_CITY.holding=false;}
  return{buildingId:current.id,documentedLevels:record.document.levels.map(l=>l.level),source:{...record.document.source},persisted:true,activeSnapshotPreserved,appliesOnNextEntry:activeSnapshotPreserved};
 }
 function info(){
  if(world?.v046&&V050_CITY.owner?.state!==state)bind(true);
  if(V050_CITY.documentOwner!==state){V050_CITY.documentOwner=state;V050_CITY.documentRejections.clear();}
  const a=state.v050City.active,l=world?.v050CityInterior,records=state.v050City.documents||[];
  return{version:2,zone:world?.id,active:a?{id:a.building.id,name:a.building.name,layoutVersion:a.building.layoutVersion,floor:a.floor,streetFloor:a.streetFloor??0,levels:a.building.levels,origin:a.building.origin.slice(),signature:l?.signature,layoutProvenance:l?.provenance,documentOrigin:a.documentOrigin||null,documentedLevels:a.document?.levels.map(r=>r.level)||[],documentSource:a.document?{...a.document.source}:null,currentLevelSource:l?.source?{...l.source}:null,furnishing:l?{objects:l.furniture.length,renderFurniture:world.staticDraws.filter(d=>d.v050CityFurnishing).length,colliderFurniture:world.colliders.filter(c=>c.v050CityFurnishing).length,byKind:Object.fromEntries([...new Set(l.furniture.map(f=>f.kind))].map(kind=>[kind,l.furniture.filter(f=>f.kind===kind).length])),functionalUses:[...new Set(l.functionalZones.map(z=>z.use))],roomsBasis:l.roomsBasis,roomCoverage:l.roomCoverage,programCoverage:l.programCoverage||null,provenance:'invented'}:null}:null,
   doors:[...V050_CITY.doors].map(([id,r])=>({id,building:r.building.id,pos:r.interaction.pos.slice(),levels:r.building.levels,streetFloor:r.streetFloor,provenance:r.document?'documented or mixed':'invented',documentOrigin:r.documentOrigin||null,documentedLevels:r.document?.levels.map(l=>l.level)||[],documentSource:r.document?{...r.document.source}:null})),
   services:{stations:[...(world?.v056InteriorServices?.values()||[])].map(r=>({...deepClone(r.service),interactionId:r.interaction.id,label:r.interaction.label})),omissions:deepClone(world?.v056InteriorServiceOmissions||[]),ledger:deepClone(state.v050City.services),limit:MistralCityInteriors.SERVICE_LIMIT},roomDoors:{doors:[...(world?.v055RoomDoors?.values()||[])].map(r=>({...deepClone(r.door),closed:r.closed,colliderEnabled:!r.collider.disabled,renderedParts:r.draws.filter(d=>!d.hidden).length,interactionId:r.interaction.id,label:r.interaction.label})),omissions:world?.v055RoomDoorOmissions||[],savedClosed:Object.keys(state.v050City.roomDoorStates||{}).length,limit:MistralCityInteriors.ROOM_DOOR_LIMIT},documentRegistry:{entries:records.length,bytes:documentBytes(records),maxBuildings:V050_DOCUMENT_LIMITS.buildings,maxBytes:V050_DOCUMENT_LIMITS.bytes,omissions:state.v050City.documentOmissions||0,warnings:(state.v050City.documentWarnings||[]).slice(),rejections:[...V050_CITY.documentRejections.values()].map(r=>({...r}))},rejections:{...V050_CITY.rejections},interactionBudget:64,entered:V050_CITY.entered,returned:V050_CITY.returned,exitPending:!!V050_CITY.exitPending,last:V050_CITY.last,errors:V050_CITY.errors.slice()};
 }
 globalThis.v050CityInteriorAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v050CityInteriorInfo:info,v050CityInteriorEnter:enter,v050CityInteriorExit:exit,v050CityInteriorFloor:floor,v050CityInteriorBind:()=>bind(true),v050CityRegisterDocument:registerDocument,v055CityRoomDoor:toggleRoomDoor,v056CityInteriorService:useService,v056CityInteriorServiceOpen:openService,v056CityInteriorAimInfo:()=>{const l=world?.v050CityInterior,p=state.player.pos,dir=cameraDir(state.player.yaw,state.player.pitch);return{selected:typeof selectedInteractable==='undefined'?null:selectedInteractable?.id||null,hits:l?[...(world?.v056InteriorServices?.values()||[])].map(r=>({id:r.service.id,hit:MistralCityInteriors.serviceAim(l,r.service,p,dir)})).filter(r=>r.hit):[]};},v052CityInteriorLayout:()=>world?.v050CityInterior?deepClone(world.v050CityInterior):null});bind(true);};
}
