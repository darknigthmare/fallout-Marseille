/* Keep the existing six-plate v0.30 simulation and its finite core ledger.
   This extension closes persistence gaps and brings maintenance to technicians
   already living in discovered geographic relays. It grants no equipment. */
const MistralPowerConservation=(()=>{
 const finite=n=>typeof n==='number'&&Number.isFinite(n);
 const words=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const technician=role=>/mecanicien|technicien|reparat/.test(words(role));
 const serviceSite=s=>!!s&&s.safe===true&&['settlement','outpost','caravan'].includes(s.kind);
 function contact(npc,record,site,position,eyeHeight,visible){
  if(!npc||npc.alive!==true||npc.hidden||!record||!site||typeof visible!=='function'||record.id!==npc.id||npc.v042Site!==site.id||record.siteId!==site.id||!serviceSite(site)||!technician(record.role))return false;
  if(!Array.isArray(position)||!Array.isArray(npc.pos)||position.length!==3||npc.pos.length!==3||![...position,...npc.pos,eyeHeight].every(finite))return false;
  if(Math.hypot(position[0]-npc.pos[0],position[2]-npc.pos[2])>4||Math.abs(position[1]-npc.pos[1]-eyeHeight)>1.25)return false;
  return visible(position,[npc.pos[0],npc.pos[1]+1.2,npc.pos[2]])===true;
 }
 return{technician,serviceSite,contact};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralPowerConservation;

if(typeof v030CanAct==='function'&&typeof window!=='undefined'){
 const runtime={depth:0,quote:null,lastError:null,commits:0,rollbacks:0};
 const clone=v=>JSON.parse(JSON.stringify(v));
 function available(modes=['PLAYING','PIP']){
  return !!(gameStarted&&world&&state?.player?.hp>0&&modes.includes(mode)&&!zoneTransitioning
   &&!V046.lab&&!V046.busy&&!V047.pending);
 }
 function contacts(){
  if(!available()||!world.v046||!world.geoMacro||v020Danger())return[];
  const result=[];
  for(const npc of world.npcs||[]){
   const record=V042_RUNTIME.npcData.get(npc.id),site=record&&v042Site(record.siteId);
   if(!site||!v042SiteDiscovered(site)||!MistralPowerConservation.contact(npc,record,site,state.player.pos,playerEyeHeight(),lineOfSight))continue;
   result.push({npc,record,site,distance:dist2(state.player.pos,npc.pos)});
  }
  return result.sort((a,b)=>a.distance-b.distance||a.npc.id.localeCompare(b.npc.id));
 }
 const originalCanAct=v030CanAct;
 v030CanAct=function(){return available()&&originalCanAct();};
 const originalService=v030NearService;
 v030NearService=function(){return available()&&(originalService()||contacts().length>0);};
 function serviceToken(){
  if(!available()||v020Danger())return null;
  if(originalService())return 'bench:'+world.id+':'+(world.v020Station?.id||'v030:station');
  const c=contacts()[0];return c?'technician:'+c.npc.id:null;
 }
 function refreshAfterRollback(){
  V030.quote=null;V030.restoreQuote=null;V030.endingQuote=null;runtime.quote=null;
  if(typeof v030ApplyWorld==='function')v030ApplyWorld();
  if(mode==='DIALOGUE'&&typeof closeDialogue==='function')closeDialogue();
  updateHUD();
  if(mode==='PIP')renderPipboy();
  if(mode==='TRADE'&&typeof renderTrade==='function')renderTrade();
 }
 function sceneSnapshot(w){
  const arrays={};for(const key of['staticDraws','colliders','interactables','npcs','enemies','loot','hazards','ambient'])if(Array.isArray(w?.[key]))arrays[key]=w[key].slice();
  const flags=[];for(const key of['staticDraws','colliders'])for(const item of arrays[key]||[])if(String(item.id||'').startsWith('v030:'))flags.push([item,Object.hasOwn(item,'hidden'),item.hidden,Object.hasOwn(item,'disabled'),item.disabled]);
  return{world:w,arrays,flags,nav:w?.v020NavEpoch,hadConsequence:Object.hasOwn(w||{},'v030Consequence'),consequence:w?.v030Consequence};
 }
 function restoreScene(snapshot){
  if(world!==snapshot.world)return;
  for(const[key,items]of Object.entries(snapshot.arrays))world[key]=items;
  for(const[item,hadHidden,hidden,hadDisabled,disabled]of snapshot.flags){if(hadHidden)item.hidden=hidden;else delete item.hidden;if(hadDisabled)item.disabled=disabled;else delete item.disabled;}
  world.v020NavEpoch=snapshot.nav;
  if(snapshot.hadConsequence)world.v030Consequence=snapshot.consequence;else delete world.v030Consequence;
 }
 function atomic(action,args,modes=['PLAYING','PIP']){
  if(!available(modes))return false;
  if(runtime.depth)return action(...args);
  const owner=state,before=clone(owner),scene=sceneSnapshot(world),save=saveGame;
  let requested=false,saveArgs=[false],result;
  runtime.depth++;
  // Original actions can save twice (trade then six-plate metadata). Defer
  // both calls so only the complete resulting ledger reaches storage.
  saveGame=function(...a){requested=true;saveArgs=a;return true;};
  try{
   result=action(...args);
   if(result?.then)throw Error('Une opération d’armure doit se terminer sans attente.');
   if(state!==owner||world!==scene.world)throw Error('La scène de l’opération a changé.');
   saveGame=save;
   if(result===false){for(const key of Object.keys(owner))delete owner[key];Object.assign(owner,before);return false;}
   if(requested&&save(...saveArgs)===false)throw Error('La sauvegarde locale est indisponible.');
   if(requested)runtime.commits++;
   runtime.lastError=null;
   return result;
  }catch(error){
   if(state===owner){for(const key of Object.keys(owner))delete owner[key];Object.assign(owner,before);restoreScene(scene);}
   runtime.rollbacks++;runtime.lastError=String(error?.message||error);refreshAfterRollback();
   return v027Notify('Opération annulée : '+runtime.lastError+' Charge, pièces et matériaux conservés.');
  }finally{saveGame=save;runtime.depth--;}
 }
 const switching=v030Switch;v030Switch=function(...a){return atomic(switching,a);};
 const inserting=v030Insert;v030Insert=function(...a){return atomic(inserting,a);};
 const ejecting=v030Eject;v030Eject=function(...a){return atomic(ejecting,a);};
 const equipping=equipArmor;
 equipArmor=function(id){return v030Powered(id)||v030Powered()?atomic(equipping,[id]):equipping(id);};
 const quoting=v030Quote;
 v030Quote=function(kind,value,confirm=false){
  if(!available())return false;
  if(!confirm){const result=quoting(kind,value,false);runtime.quote=result&&V030.quote?{owner:state,world,token:serviceToken()}:null;return result;}
  const quote=runtime.quote;runtime.quote=null;
  if(!quote||quote.owner!==state||quote.world!==world||!quote.token||quote.token!==serviceToken()){
   V030.quote=null;return v027Notify('Le point d’entretien a changé. Demandez un nouveau devis sur place.');
  }
  return atomic(quoting,[kind,value,true]);
 };
 // The same atomic boundary also covers the original finite acquisition and
 // its workshop gate; failed writes cannot leave a vanished core or open gate.
 const story=v030StoryAction;v030StoryAction=function(...a){return atomic(story,a,['PLAYING','PIP','DIALOGUE']);};
 const trial=v030Trial;v030Trial=function(...a){return atomic(trial,a,['PLAYING','PIP','DIALOGUE']);};
 const resolving=v030Resolve;v030Resolve=function(...a){return atomic(resolving,a,['PLAYING','PIP','DIALOGUE']);};
 const buying=buyTradeItem;
 buyTradeItem=function(id){return v030Powered(id)||id==='fusionCore'?atomic(buying,[id],['TRADE']):buying(id);};
 const selling=sellTradeItem;
 sellTradeItem=function(id){return v030Powered(id)||id==='fusionCore'?atomic(selling,[id],['TRADE']):selling(id);};
 function relays(){
  if(!world||!state?.v042)return[];
  return V042_CATALOG.filter(s=>MistralPowerConservation.serviceSite(s)&&s.npcRoles?.some(MistralPowerConservation.technician)&&v042SiteDiscovered(s)).map(site=>{
   const p=world.geoMacro?v015GeoProject(world.id,site.lat,site.lon):null;
   return{site,distance:p?dist2(p,state.player.pos):null};
  }).sort((a,b)=>(a.distance??Infinity)-(b.distance??Infinity)||a.site.name.localeCompare(b.site.name,'fr'));
 }
 function acquisition(){
  return Object.entries(MERCHANTS).map(([id,def])=>({id,name:def.name,stock:state.economy?.merchants?.[id]?.stock||def.stock})).map(row=>({...row,cores:Math.max(0,Number(row.stock.fusionCore)||0),suits:Object.entries(row.stock).filter(([id,count])=>count>0&&v030Powered(id)).map(([id,count])=>({id,count,name:ARMORS[id].name}))})).filter(row=>row.cores||row.suits.length).slice(0,8);
 }
 function sceneClear(w,x,z,radius=.38){
  const bounds=w.bounds;if(!bounds||x-radius<bounds[0]||x+radius>bounds[1]||z-radius<bounds[2]||z+radius>bounds[3])return false;
  return !(w.colliders||[]).some(c=>!c.disabled&&1.83>=(c.minY??0)&&0<=(c.maxY??Infinity)&&v017ColliderHit(c,x,z,radius));
 }
 function sceneSight(w,a,b){
  const delta=b.map((n,i)=>n-a[i]),length=Math.hypot(...delta),distance=Math.max(0,length-.25),direction=delta.map(n=>n/(length||1));
  return !(w.colliders||[]).some(c=>!c.disabled&&rayAABB(a,direction,c,distance)<distance);
 }
 function drydockAccess(w){
  if(w?.id!=='drydock'||w.v046||w.geoMacro||w.v053DrydockService)return w;
  const npc=w.npcs?.find(n=>n.id==='drydock-merchant'),it=w.interactables?.find(i=>i.id==='drydock-trade');
  if(!npc||!it||npc.alive!==true){w.v053DrydockService={status:'merchant-unavailable'};return w;}
  const original={merchant:npc.pos.slice(),interaction:it.pos.slice()};
  if(sceneClear(w,npc.pos[0],npc.pos[2])&&sceneClear(w,it.pos[0],it.pos[2]))return w;
  // The historical fictional shop is a closed solid. Put its existing person
  // and a small physical counter on the public south quay, never through it.
  for(const z of[80,84,88,92])for(const x of[-82,-86,-78,-90,-74,-94,-70,-66]){
   const merchant=[x,0,z-1.2],approach=[x,1.65,z+1.95],interaction=[x,1.2,z+.35];
   if(!sceneClear(w,x,z,1.13)||!sceneClear(w,merchant[0],merchant[2])||!sceneClear(w,approach[0],approach[2]))continue;
   if((w.npcs||[]).some(n=>n!==npc&&n.alive!==false&&(dist2(n.pos,merchant)<1.2||dist2(n.pos,approach)<1.2)))continue;
   if(!sceneSight(w,approach,interaction)||!sceneSight(w,approach,[merchant[0],1.2,merchant[2]]))continue;
   let pathClear=true;for(let step=0;step<=10;step++)if(!sceneClear(w,x,z+1.95+step*.15)){pathClear=false;break;}if(!pathClear)continue;
   npc.pos=merchant.slice();npc.home=merchant.slice();npc.yaw=Math.PI;
   it.pos=interaction.slice();
   addBox(w,[x,.44,z],[1.8,.88,.7],[.29,.33,.30],0,{id:'v053:drydock-counter'});
   addBox(w,[x,.90,z],[1.9,.08,.8],[.55,.48,.32],0,{id:'v053:drydock-counter-top'});
   addBox(w,[x-.50,1.01,z-.10],[.37,.14,.29],[.23,.26,.23],0,{id:'v053:drydock-counter-terminal'});
   addCollider(w,x,z,1.9,.8,{id:'v053:drydock-counter',minY:0,maxY:.94});
   addFloorZone(w,x,z,1.9,.8,.95,{id:'v053:drydock-counter',priority:3});
   w.v053DrydockService={status:'placed',original,merchant:merchant.slice(),approach,interaction:interaction.slice(),counter:[x,0,z],actorRadius:.38,provenance:'Authored access correction in the existing fictional drydock scene'};
   return w;
  }
  w.v053DrydockService={status:'no-clear-frontage',original};return w;
 }
 if(typeof buildWorld==='function'){
  const building=buildWorld;buildWorld=function(...args){return drydockAccess(building(...args));};
 }
 const powerHTML=v030PowerHTML;
 v030PowerHTML=function(c){
  const result=powerHTML(c),contact=contacts()[0],sites=relays(),stocks=acquisition(),blocked=!available();
  if(contact&&!originalService())c.innerHTML=c.innerHTML.replace('Établi local accessible · assistance arrêtée.',v027Escape(contact.record.name)+' · mécanicienne du relais accessible, assistance arrêtée.');
  c.innerHTML+='<section class="p30-geographic-service"><h3>ENTRETIEN SUR LE TERRITOIRE</h3><p>'+ (contact?v027Escape(contact.record.name)+' · '+v027Escape(contact.site.name)+' : entretien à moins de 4 m, avec vos matériaux.':'Approchez une mécanicienne d’un relais sûr et découvert à moins de 4 m, ou utilisez un établi. La ligne de vue et le danger sont vérifiés au moment des travaux.')+'</p>'+sites.slice(0,8).map(({site,distance})=>'<p>'+v027Escape(site.name)+(distance===null?'':' · '+Math.round(distance)+' m')+' '+v027Button('Suivre le relais','p53:trackTech',site.id,blocked)+'</p>').join('')+(sites.length?'':'<p>Explorez les relais habités pour trouver leurs mécaniciennes.</p>')+'<h3>CHÂSSIS ET CŒURS</h3><p>Alba Rousset remet le M-45 en état dans la baie des amarres : le dossier « Une force empruntée » permet d’obtenir le châssis et son cœur d’essai entamé.</p>'+v027Button('Suivre le dossier d’Alba','p53:trackRig','',blocked||!!state.v030.quest.ending)+stocks.map(row=>'<p>'+v027Escape(row.name)+' : '+row.cores+' lot(s) de cœur neuf'+(row.suits.length?' · '+row.suits.map(s=>v027Escape(s.name)+' × '+s.count).join(', '):'')+'. Achats au comptoir.</p>').join('')+'</section>';
  return result;
 };
 const dispatch=v027Dispatch;
 v027Dispatch=function(action,arg=''){
  if(!action.startsWith('p53:'))return dispatch(action,arg);
  if(!v027CanAct()||!available())return false;
  if(action==='p53:trackTech')return relays().some(r=>r.site.id===arg)?atomic(v042TrackSite,[arg]):false;
  if(action==='p53:trackRig')return atomic(v027Track,['rig030']);
  return false;
 };
 globalThis.v053PowerArmorAfterInit=function(){
  Object.assign(window.__MISTRAL_DEBUG,{v053PowerArmorInfo:()=>({existingSchema:state.v030.schema,online:v030Online(),charge:state.v030.core,spares:state.v030.spares.slice(),commits:runtime.commits,rollbacks:runtime.rollbacks,lastError:runtime.lastError,service:serviceToken(),technicians:contacts().map(c=>({id:c.npc.id,name:c.record.name,site:c.site.id,distance:c.distance})),discoveredRelays:relays().map(r=>({id:r.site.id,name:r.site.name,distance:r.distance})),acquisition:acquisition().map(({stock,...row})=>clone(row)),drydockService:world?.v053DrydockService?clone(world.v053DrydockService):null})});
 };
}
