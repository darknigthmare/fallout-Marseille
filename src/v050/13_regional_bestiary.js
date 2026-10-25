/* Three original regional assemblies. Encounter IDs, AI archetypes, wounds,
   rewards and finite corpse inventories retain their existing owners. */
const MistralRegionalBestiary=(()=>{
 const MAX_ASSIGNMENTS=256,MAX_BYTES=96*1024,copy=v=>JSON.parse(JSON.stringify(v)),finite=Number.isFinite;
 const SPECS={
  ratCable:{name:'Rat-câble',baseTypes:['molerat'],macros:['geo_huveaune','geo_marseille'],radius:.9,family:'regional-rat',attack:{melee:true,duration:.68,reach:1.85,radius:.92,label:'MORSURE DU RAT-CÂBLE'}},
  gabianBombardier:{name:'Gabian bombardier',baseTypes:['bloatfly'],macros:['geo_marseille','geo_calanques','geo_frioul','geo_laciotat'],radius:.96,family:'regional-bird',attack:{melee:false,duration:1.35,reach:14,radius:.85,label:'LÂCHER CORROSIF DU GABIAN'}},
  cerfa77:{name:'CERFA-77',baseTypes:['protectron','concordeDrone'],macros:['geo_marseille','geo_huveaune','geo_laciotat'],radius:.9,family:'regional-automaton',attack:{melee:false,duration:1.65,reach:22,radius:.72,label:'INJONCTION ARMÉE CERFA-77'}}
 };
 function species(site,baseType){return Object.keys(SPECS).find(id=>SPECS[id].baseTypes.includes(baseType)&&SPECS[id].macros.includes(site?.macro))||null;}
 function candidate(site,index,baseType){
  if(!site||!['nest','elite','boss'].includes(site.kind)||!Array.isArray(site.enemyTypes)||!Number.isInteger(index)||index<0||index>=site.enemySlots||!species(site,baseType))return null;
  // One regular slot per hostile site; elites and bosses retain their identity.
  for(let i=0;i<Math.min(16,site.enemySlots);i++){if(i===0&&['elite','boss'].includes(site.kind))continue;const type=site.enemyTypes[i%site.enemyTypes.length];if(species(site,type))return i===index&&type===baseType?species(site,type):null;}return null;
 }
 function fresh(){return{schema:1,assignments:{}};}
 function migrate(raw,resolve){const out=fresh();let bytes=0;for(const[id,value]of Object.entries(raw?.assignments||{}).slice(0,MAX_ASSIGNMENTS*4)){if(Object.keys(out.assignments).length>=MAX_ASSIGNMENTS)break;const expected=resolve(id);if(!expected||value?.species!==expected.species||value?.baseType!==expected.baseType)continue;const entry={species:expected.species,baseType:expected.baseType},size=JSON.stringify([id,entry]).length*2;if(bytes+size>MAX_BYTES)continue;bytes+=size;out.assignments[id]=entry;}return out;}
 function model(id,time=0,options={}){
  if(!SPECS[id])throw Error('Espèce régionale inconnue');if(!finite(time))time=0;const pose=options.reduceMotion?0:time,walk=options.moving===false?0:Math.sin(pose*8),wind=options.windup?Math.max(0,Math.min(1,options.windup)):0,out=[];
  const p=(mesh,pos,size,color,group='body',yaw=0,emissive=0)=>out.push({mesh,pos,size,color,group,yaw,emissive});
  if(id==='ratCable'){
   const fur=[.32,.29,.23],metal=[.21,.25,.24],flesh=[.53,.33,.26],light=[.72,.63,.37];
   p('sphere',[0,.33+wind*.05,.02],[.48,.39,.75],fur);p('sphere',[0,.32+wind*.14,-.42],[.34,.31,.37],fur,'head');p('cone',[0,.29+wind*.14,-.62],[.19,.15,.22],flesh,'head',Math.PI/2);
   for(const side of[-1,1]){p('sphere',[side*.13,.52+wind*.12,-.35],[.16,.2,.12],flesh,'head');p('sphere',[side*.13,.37+wind*.14,-.57],[.048,.05,.04],[.8,.47,.17],'head',0,.22);for(const z of[-.22,.27]){const lift=walk*side*(z<0?1:-1)*.06,group=(z<0?'fore_':'back_')+(side<0?'l':'r');p('cylinder',[side*.2,.15+Math.max(0,lift),z],[.09,.23,.13],fur,group);p('cube',[side*.21,.055+Math.max(0,lift),z-.04],[.12,.08,.19],flesh,group);}}
   // The cable curls inside the admitted body footprint instead of dragging a
   // metre-long rigid tail through neighbouring source walls.
   for(let i=0;i<7;i++){const a=i*.39,wiggle=options.reduceMotion?0:Math.sin(pose*3+i*.7)*.035;p('sphere',[Math.sin(a)*.27+wiggle,.23+i*.025,.44+Math.sin(a*.7)*.24],[.075,.075,.15],metal,'tail',a);}
   p('cube',[0,.5,.11],[.27,.12,.38],metal);for(const side of[-1,1])p('cube',[side*.12,.53,.11],[.035,.035,.3],light);
  }else if(id==='gabianBombardier'){
   const feather=[.67,.68,.59],dark=[.22,.27,.27],beak=[.69,.53,.2],sac=[.34,.47,.24],flap=options.reduceMotion?0:Math.sin(pose*5)*.18,bob=options.reduceMotion?0:Math.sin(pose*3)*.045;
   p('sphere',[0,.79+bob,0],[.35,.39,.56],feather);p('sphere',[0,.98+bob,-.27],[.25,.28,.27],feather,'head');p('cone',[0,.94+bob,-.46],[.14,.12,.26],beak,'head',Math.PI/2);p('sphere',[0,.61+bob-wind*.1,-.04],[.25,.2,.29],sac);
   for(const side of[-1,1]){const wing=side<0?'arm_l':'arm_r';p('sphere',[side*.27,.82+bob+flap,.025],[.38,.12,.37],feather,wing,side*.18);p('cube',[side*.5,.82+bob+flap*1.6,.08],[.28,.065,.44],dark,wing,side*.26);for(let k=0;k<3;k++)p('cube',[side*(.5+k*.045),.81+bob+flap*1.6,.2+k*.035],[.09,.05,.24],feather,wing,side*.3);p('sphere',[side*.075,1.01+bob,-.383],[.035,.037,.035],[.12,.14,.11],'head');p('cylinder',[side*.09,.37+bob,0],[.045,.34,.045],beak,side<0?'leg_l':'leg_r');p('cube',[side*.09,.2+bob,-.05],[.1,.035,.18],beak,side<0?'leg_l':'leg_r');}
   for(const side of[-1,0,1])p('cube',[side*.07,.77+bob,.38],[.12,.055,.28],dark,'tail',side*.15);
   if(wind>.25)p('sphere',[0,.47+bob-wind*.15,-.08],[.11,.12,.12],sac,'body',0,.15);
  }else{
   const shell=[.45,.48,.4],dark=[.18,.23,.23],paper=[.76,.73,.56],brass=[.55,.44,.23],stamp=wind*.23,scan=options.reduceMotion?0:Math.sin(pose*1.4)*.045;
   p('cube',[0,.86,0],[.58,.72,.43],shell);p('cube',[0,1.32,0],[.48,.29,.39],dark,'head');p('cube',[scan,1.34,-.217],[.31,.09,.035],wind?[.88,.29,.13]:[.29,.74,.56],'head',0,.5);p('cube',[0,.96,-.24],[.39,.25,.045],paper);for(let i=0;i<3;i++)p('cube',[0,.9+i*.055,-.267],[.26,.014,.012],dark);
   p('cube',[0,.72,-.35],[.4,.08,.31],dark);p('cube',[0,.77,-.37],[.27,.025,.27],paper);p('cube',[0,.5,0],[.64,.14,.48],brass);
   for(const side of[-1,1]){const arm=side<0?'arm_l':'arm_r',leg=side<0?'leg_l':'leg_r';p('sphere',[side*.36,1.05,0],[.19,.2,.2],shell,arm);p('cylinder',[side*.43,.85,-stamp],[.1,.35,.12],dark,arm);p('cube',[side*.43,.65,-stamp],[.18,.12,.2],brass,arm);p('cylinder',[side*.22,.28,0],[.24,.36,.42],dark,leg);p('cube',[side*.22,.105,-.02],[.28,.12,.44],shell,leg);}
   p('cube',[-.43,.59,-stamp],[.18,.05,.15],[.47,.17,.13],'arm_l');p('cube',[.43,.69,-.06-stamp],[.12,.12,.22],dark,'arm_r');p('cube',[0,1.55,.02],[.09,.19,.08],brass,'head');p('sphere',[0,1.67,.02],[.1,.1,.1],[.75,.39,.18],'head',0,.3);
  }
  return out;
 }
 function rotate(p,a){const c=Math.cos(a),s=Math.sin(a);return[c*p[0]+s*p[2],p[1],-s*p[0]+c*p[2]];}
 function rig(actor,id,time=0,options={}){
  if(!Array.isArray(actor?.pos)||actor.pos.length!==3||!actor.pos.every(finite))throw Error('Position d’acteur invalide');const yaw=finite(actor.yaw)?actor.yaw:0,local=model(id,time,options),groups=new Map(),draws=[];
  const world=p=>rotate(p,yaw).map((v,i)=>v+actor.pos[i]),groupOf=g=>/^(arm_[lr])$/.test(g)?'arms':/^(leg_[lr]|fore_[lr]|back_[lr])$/.test(g)?'legs':g==='tail'?'body':g;
  for(const part of local){const draw={mesh:part.mesh,pos:world(part.pos),scale:part.size.slice(),color:part.color.slice(),rotY:yaw+part.yaw,emissive:part.emissive,alpha:1,v025Part:part.group,v025Enemy:actor.id,v053RegionalPart:id};draws.push(draw);let group=groups.get(part.group);if(!group){group={id:part.group,min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity],draws:[]};groups.set(part.group,group);}group.draws.push(draw);for(const x of[-.5,.5])for(const y of[-.5,.5])for(const z of[-.5,.5]){const corner=rotate([part.size[0]*x,part.size[1]*y,part.size[2]*z],part.yaw).map((v,i)=>v+part.pos[i]);for(let i=0;i<3;i++){group.min[i]=Math.min(group.min[i],corner[i]);group.max[i]=Math.max(group.max[i],corner[i]);}}}
  const labels=id==='gabianBombardier'?{head:'TÊTE',body:'CORPS',arm_l:'AILE GAUCHE',arm_r:'AILE DROITE',leg_l:'PATTE GAUCHE',leg_r:'PATTE DROITE',tail:'QUEUE'}:id==='ratCable'?{head:'TÊTE',body:'CORPS CÂBLÉ',fore_l:'PATTE AV. GAUCHE',fore_r:'PATTE AV. DROITE',back_l:'PATTE AR. GAUCHE',back_r:'PATTE AR. DROITE',tail:'CÂBLE CAUDAL'}:{head:'LECTEUR OPTIQUE',body:'DOSSIER BLINDÉ',arm_l:'TAMPON',arm_r:'PINCE DE SAISIE',leg_l:'ROUE GAUCHE',leg_r:'ROUE DROITE'};
  const parts=[...groups.values()].map(b=>{const group=groupOf(b.id),center=b.min.map((v,i)=>(v+b.max[i])/2),size=b.min.map((v,i)=>b.max[i]-v),corners=[];for(const x of[0,1])for(const y of[0,1])for(const z of[0,1])corners.push(world([x?b.max[0]:b.min[0],y?b.max[1]:b.min[1],z?b.max[2]:b.min[2]]));return{id:b.id,group,label:labels[b.id]||b.id,center:world(center),radius:Math.max(.06,Math.min(.72,Math.max(...size)*.43)),mult:group==='head'?1.7:group==='arms'?.72:group==='legs'?.78:1,cost:group==='head'?35:group==='body'?25:22,bounds:b,corners};});
  const bounds={min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};for(const b of groups.values())for(let i=0;i<3;i++){bounds.min[i]=Math.min(bounds.min[i],b.min[i]);bounds.max[i]=Math.max(bounds.max[i],b.max[i]);}return{draws,parts,bounds,family:SPECS[id].family};
 }
 return{MAX_ASSIGNMENTS,MAX_BYTES,catalog:()=>copy(SPECS),species,candidate,fresh,migrate,model,rig};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralRegionalBestiary;

if(typeof v042SpawnEnemies==='function'&&typeof v049Identify==='function'){
 const specs=MistralRegionalBestiary.catalog(),stats={newVariants:0,restoredVariants:0,oldSlotsKept:0,unmeasuredSkipped:0,budgetSkipped:0,movementBlocked:0},rigCache=new WeakMap(),pendingWorlds=new WeakMap();let stageCache=null;
 function expected(id){const meta=v049Identify(id);if(meta?.kind!=='enemy'||meta.scope!=='outside')return null;const site=v042Site(meta.site),index=Number(id.split(':').at(-1)),baseType=site?.enemyTypes?.[index%site.enemyTypes.length],species=MistralRegionalBestiary.candidate(site,index,baseType);return species?{species,baseType}:null;}
 const base=baseState;baseState=function(){const s=base();s.v053Bestiary=MistralRegionalBestiary.fresh();return s;};
 const migration=migrateState;migrateState=function(input={}){const s=migration(input);s.v053Bestiary=MistralRegionalBestiary.migrate(input.v053Bestiary,expected);return s;};state=migrateState(state);if(world)v049Own(world);
 function stage(w){const bank=v047Bank(w);if(!stageCache||stageCache.world!==w||stageCache.bank!==bank||stageCache.records!==w.v046Records||stageCache.colliders!==w.colliders||stageCache.length!==w.colliders.length)stageCache={world:w,records:w.v046Records,bank,geoColliders:w.colliders.filter(c=>c.v046Tile),colliders:w.colliders,length:w.colliders.length};return stageCache;}
 function ground(w,x,z,radius){if(w!==world||!w?.v046||!w.geoMacro||!w.v046Records?.size||typeof v050TravelGround!=='function')return null;return v050TravelGround(stage(w),w,x,z,radius);}
 function valid(w,pos,radius,neighbours=false){const h=ground(w,pos[0],pos[2],radius);if(!Number.isFinite(h)||Math.abs(h-pos[1])>.35)return false;if(neighbours)for(const[dx,dz]of[[radius,0],[-radius,0],[0,radius],[0,-radius]]){const other=ground(w,pos[0]+dx,pos[2]+dz,radius*.25);if(!Number.isFinite(other)||Math.abs(other-h)>.5)return false;}return true;}
 function prior(id){return !!state.v049?.actors?.[id]||!!state.flags?.enemyDead?.[id]||Object.keys(state.v022?.encounters||{}).some(key=>key.endsWith('|'+id))||Object.values(state.v026?.containers||{}).some(c=>c.id==='remains:'+id);}
 function speciesOf(e){const entry=state.v053Bestiary?.assignments?.[e?.id];return e?.v053RegionalSpecies&&entry?.species===e.v053RegionalSpecies&&entry.baseType===e.type?entry.species:null;}
 // Prepare can build a temporary world or publish while busy. Remember only
 // actor-local eligibility here; no campaign entry exists until publication.
 function publish(w=world){const pending=w&&pendingWorlds.get(w);if(!pending)return;if(pending.owner!==state){pendingWorlds.delete(w);return;}if(w!==world||!gameStarted||V046.lab||V046.busy||V047.pending||zoneTransitioning||!v049Allowed(w))return;
  pendingWorlds.delete(w);for(const[e,proposal]of pending.actors){if(!w.enemies.includes(e)||e.alive===false||e.boss||proposal.baseType!==e.type)continue;const resolved=expected(e.id);if(!resolved||resolved.species!==proposal.species||resolved.baseType!==proposal.baseType)continue;let entry=state.v053Bestiary.assignments[e.id];if(!valid(w,e.pos,specs[proposal.species].radius,true)){stats.unmeasuredSkipped++;continue;}
   if(!entry){const ledger=state.v053Bestiary.assignments,bytes=JSON.stringify(ledger).length*2;if(Object.keys(ledger).length>=MistralRegionalBestiary.MAX_ASSIGNMENTS||bytes+JSON.stringify([e.id,proposal]).length*2>MistralRegionalBestiary.MAX_BYTES){stats.budgetSkipped++;continue;}entry=ledger[e.id]={...proposal};stats.newVariants++;}else stats.restoredVariants++;
   e.v053RegionalSpecies=entry.species;e.name=specs[entry.species].name;
  }
 }
 const spawn=v042SpawnEnemies;v042SpawnEnemies=function(w,p,site,inside=false){
  const before=new Set((w.enemies||[]).map(e=>e.id)),known=new Set();for(let i=0;i<Math.min(16,site.enemySlots||0);i++){const id=v042EnemyId(site,i,inside);if(prior(id))known.add(id);}
  const owner=state,result=spawn(...arguments);if(inside||owner!==state||!w?.v046||!w.geoMacro||V046.lab||!v049Allowed(w))return result;
  let pending=pendingWorlds.get(w);if(!pending||pending.owner!==state){pending={owner:state,actors:new Map()};pendingWorlds.set(w,pending);}
  for(const e of result||[]){if(before.has(e.id)||e.alive===false||e.boss)continue;const proposal=expected(e.id);if(!proposal||proposal.baseType!==e.type)continue;if(!state.v053Bestiary.assignments[e.id]&&known.has(e.id)){stats.oldSlotsKept++;continue;}pending.actors.set(e,proposal);}
  publish(w);return result;
 };
 const originalRig=v025Rig;v025Rig=function(e,t=gameClock){const id=speciesOf(e);if(!id)return originalRig(...arguments);const time=V025.active?V025.poseTime:t,key=JSON.stringify([id,time,e.pos,e.yaw,e.state,e.v021Windup?.elapsed,e.v021Windup?.duration,settings.reduceMotion]),cached=rigCache.get(e);if(cached?.key===key)return cached.rig;const rig=MistralRegionalBestiary.rig(e,id,time,{reduceMotion:settings.reduceMotion,moving:['chase','advance','retreat','search','patrol'].includes(e.state),windup:e.v021Windup?e.v021Windup.elapsed/e.v021Windup.duration:0});rig.key=key;rigCache.set(e,{key,rig});return rig;};
 const attack=v021AttackSpec;v021AttackSpec=function(e){const id=speciesOf(e);return id?{...specs[id].attack,reach:Math.min(specs[id].attack.reach,Math.max(specs[id].attack.melee?1.8:10,e.range||specs[id].attack.reach))}:attack(...arguments);};
 const move=tryEnemyMove;tryEnemyMove=function(e,dx,dz){const id=speciesOf(e);if(!id)return move(...arguments);const radius=specs[id].radius,h=ground(world,e.pos[0]+dx,e.pos[2],radius),h2=ground(world,e.pos[0]+dx,e.pos[2]+dz,radius);if(!Number.isFinite(h)||!Number.isFinite(h2)||Math.abs(h-e.pos[1])>.55||Math.abs(h2-h)>.55){stats.movementBlocked++;return;}return move(...arguments);};
 const update=updateEnemies;updateEnemies=function(dt){publish();const owner=world,poses=new Map((world?.enemies||[]).filter(e=>e.alive&&speciesOf(e)).map(e=>[e,e.pos.slice()])),out=update(...arguments);if(world===owner)for(const[e,p]of poses){const id=speciesOf(e);if(e.alive&&id&&!valid(owner,e.pos,specs[id].radius)){e.pos=p;stats.movementBlocked++;}}return out;};
 const remains=v026RemainsDraws;v026RemainsDraws=function(out,c){const id=typeof c?.id==='string'&&c.id.startsWith('remains:')?state.v053Bestiary?.assignments?.[c.id.slice(8)]?.species:null;if(!id||!specs[id])return remains(...arguments);const actor={id:c.id,pos:c.pos,yaw:c.actor?.yaw||0},rig=MistralRegionalBestiary.rig({id:c.id,pos:[0,0,0],yaw:0},id,0,{reduceMotion:true,moving:false}),yaw=actor.yaw,co=Math.cos(yaw),si=Math.sin(yaw),draws=rig.draws.map(d=>{const x=d.pos[0],z=d.pos[1]-.5;return{...d,pos:[actor.pos[0]+co*x+si*z,actor.pos[1]+.12+Math.abs(d.pos[2])*.16,actor.pos[2]-si*x+co*z],scale:[d.scale[0],Math.min(.16,d.scale[2]),d.scale[1]],rotY:yaw+d.rotY,color:d.color.map(v=>v*.72),v053RegionalCorpse:id,v026Corpse:c.id};});out.push(...draws);};
 function info(){const assignments=state.v053Bestiary.assignments,visible=(world?.enemies||[]).filter(e=>speciesOf(e)).map(e=>({id:e.id,species:speciesOf(e),name:e.name,baseType:e.type,site:e.v042Site,alive:e.alive,health:e.health,maxHealth:e.maxHealth,pos:e.pos.slice(),parts:v025Rig(e).parts.length,meshes:v025Rig(e).draws.length})),eligible=[];for(const site of V042_CATALOG)for(let i=0;i<Math.min(16,site.enemySlots);i++){const type=site.enemyTypes?.[i%site.enemyTypes.length],id=v042EnemyId(site,i,false),species=MistralRegionalBestiary.candidate(site,i,type);if(species&&!prior(id))eligible.push({id,site:site.id,species,baseType:type,lat:site.lat,lon:site.lon,macro:site.macro});}return{schema:1,...stats,assignments:Object.keys(assignments).length,maxAssignments:MistralRegionalBestiary.MAX_ASSIGNMENTS,maxBytes:MistralRegionalBestiary.MAX_BYTES,visible,eligibleSites:eligible.slice(0,32),eligibleSitesTruncated:eligible.length>32,scope:'Three original regional silhouettes on new validated encounters; existing AI types, identities, health and finite loot are retained. Ground-following inherited AI, no full aerial navigation.'};}
 globalThis.v053BestiaryAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v053BestiaryInfo:info,v053BestiaryCatalog:()=>MistralRegionalBestiary.catalog(),v053BestiaryActor:id=>{const e=world?.enemies?.find(e=>e.id===id);return e&&speciesOf(e)?{...info().visible.find(a=>a.id===id),rig:JSON.parse(JSON.stringify(v025Rig(e)))}:null;}});};
}
