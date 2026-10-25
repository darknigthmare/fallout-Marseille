/* Collectible objects and printed skill magazines are authored game content.
   Their placements never claim an IGN survey or a recovered studio asset. */
const MistralIconicEcosystem=(()=>{
 const STATS=['S','P','E','C','I','A','L'],SKILLS=['repair','medicine','science','guns'];
 const copy=value=>JSON.parse(JSON.stringify(value)),finite=value=>typeof value==='number'&&Number.isFinite(value),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const DRINKS={nukaCola:{name:'Nuka-Cola',hp:12,ap:20,rad:2,value:20,mass:.4,color:[.49,.08,.05],description:'Boisson récupérée : +12 PV, +20 PA, +2 radiations et une capsule conservée.'},nukaQuantum:{name:'Nuka-Cola Quantum',hp:20,ap:60,rad:5,value:45,mass:.4,color:[.08,.43,.74],description:'Boisson luminescente : +20 PV, +60 PA, +5 radiations et une capsule conservée.'}};
 const BOOKS={magazineRepair:{name:'Le Mécano du désert',skill:'repair',value:18,mass:.15,color:[.62,.35,.13]},magazineMedicine:{name:'Médecine de terrain',skill:'medicine',value:18,mass:.15,color:[.33,.57,.39]},magazineScience:{name:'Science ! · édition Mistral',skill:'science',value:18,mass:.15,color:[.18,.43,.61]},magazineGuns:{name:'Armes et munitions · fiche de tir',skill:'guns',value:18,mass:.15,color:[.62,.22,.16]}};
 const OBJECTS=[
  ...STATS.map((stat,i)=>({id:'figurine-'+stat.toLowerCase(),kind:'figurine',stat,name:'Figurine S.P.E.C.I.A.L. · '+({S:'Force',P:'Perception',E:'Endurance',C:'Charisme',I:'Intelligence',A:'Agilité',L:'Chance'})[stat],scene:['aubagne','marseille','fontdemai','saintcharles','ceramiques','panier','ciotatport'][i],macro:['geo_huveaune','geo_marseille','geo_garlaban','geo_marseille','geo_huveaune','geo_marseille','geo_laciotat'][i],siteIndex:[0,0,0,1,1,2,0][i]})),
  ...Object.keys(BOOKS).map((item,i)=>({id:'edition-'+BOOKS[item].skill,kind:'magazine',item,name:BOOKS[item].name,scene:['relay_vent','relay_cold','traverse_archives','mooring_station'][i],macro:['geo_huveaune','geo_marseille','geo_marseille','geo_laciotat'][i],siteIndex:0})),
  {id:'bouteille-classique',kind:'bottle',item:'nukaCola',name:'Nuka-Cola',scene:'aubagne',macro:'geo_huveaune',siteIndex:0},
  {id:'bouteille-quantum',kind:'bottle',item:'nukaQuantum',name:'Nuka-Cola Quantum',scene:'mooring_station',macro:'geo_laciotat',siteIndex:0}
 ];
 const BY_ID=Object.assign(Object.create(null),Object.fromEntries(OBJECTS.map(o=>[o.id,o]))),AID=Object.assign(Object.create(null),DRINKS,BOOKS),DURATION=120,SKILL_BONUS=10;
 function hash(value){let h=2166136261;for(const char of String(value))h=Math.imul(h^char.charCodeAt(0),16777619);return h>>>0;}
 function fresh(){return{schema:1,found:{},read:{},effects:{},drinks:0};}
 function migrate(raw){
  const out=fresh(),p=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{};
  for(const id of Object.keys(BY_ID))if(Object.hasOwn(p.found||{},id)&&p.found[id]===true)out.found[id]=true;
  for(const id of Object.keys(BOOKS))if(Object.hasOwn(p.read||{},id)&&Number.isInteger(p.read[id])&&p.read[id]>=0)out.read[id]=Math.min(100000,p.read[id]);
  for(const key of SKILLS)if(Object.hasOwn(p.effects||{},key)&&finite(p.effects[key])&&p.effects[key]>0)out.effects[key]=clamp(p.effects[key],0,DURATION);
  if(Number.isInteger(p.drinks)&&p.drinks>=0)out.drinks=Math.min(100000,p.drinks);return out;
 }
 function targets(catalog=[]){return OBJECTS.map(object=>{const sites=catalog.filter(site=>site?.safe===true&&site.macro===object.macro&&['settlement','outpost','caravan'].includes(site.kind)).sort((a,b)=>String(a.id).localeCompare(String(b.id)));return{...object,siteId:sites.length?sites[object.siteIndex%sites.length].id:null};});}
 function award(snapshot,id){
  const object=BY_ID[id];if(!object)throw Error('Objet de collection inconnu.');const out=copy(snapshot),ledger=migrate(out.v053Iconic);
  if(ledger.found[id])throw Error('Cet exemplaire a déjà été récupéré.');out.inventory??={};out.character??={special:{}};out.character.special??={};let gain=0;
  if(object.stat){const before=out.character.special[object.stat];if(!Number.isInteger(before)||before<1||before>10)throw Error('Fiche S.P.E.C.I.A.L. invalide.');const after=Math.min(10,before+1);gain=after-before;out.character.special[object.stat]=after;}
  else{const count=out.inventory[object.item]??0;if(!Number.isInteger(count)||count<0||count>=1000000)throw Error('Inventaire hors limite.');out.inventory[object.item]=count+1;}
  ledger.found[id]=true;out.v053Iconic=ledger;return{snapshot:out,statGain:gain,object:copy(object)};
 }
 function consume(snapshot,id){
  const definition=AID[id];if(!definition)throw Error('Objet sans usage ici.');const out=copy(snapshot),quantity=out.inventory?.[id],p=out.player;
  if(!Number.isInteger(quantity)||quantity<1||!p||!['hp','maxHp','ap','maxAp','rad','caps'].every(k=>finite(p[k]))||p.hp<=0||p.maxHp<=0||p.maxAp<0||p.caps<0)throw Error('Objet ou fiche indisponible.');
  const ledger=migrate(out.v053Iconic);
  if(Object.hasOwn(BOOKS,id)){const skill=definition.skill;if(ledger.effects[skill]>0)throw Error('Cette aptitude bénéficie déjà de sa lecture. L’exemplaire est conservé.');ledger.effects[skill]=DURATION;ledger.read[id]=Math.min(100000,(ledger.read[id]||0)+1);}
  else{p.hp=Math.min(p.maxHp,p.hp+definition.hp);p.ap=Math.min(p.maxAp,p.ap+definition.ap);p.rad=clamp(p.rad+definition.rad,0,100);p.caps=Math.min(1000000000,p.caps+1);ledger.drinks=Math.min(100000,ledger.drinks+1);}
  out.inventory[id]=quantity-1;out.v053Iconic=ledger;return out;
 }
 function tick(raw,dt,active=true){const out=migrate(raw);if(!active||!finite(dt)||dt<=0)return out;for(const skill of Object.keys(out.effects)){const left=Math.max(0,out.effects[skill]-dt);if(left>0)out.effects[skill]=left;else delete out.effects[skill];}return out;}
 function skill(base,key,raw){return clamp(base+(SKILLS.includes(key)&&migrate(raw).effects[key]>0?SKILL_BONUS:0),0,100);}
 function loot(id,items,options={},existing=false){
  const out=copy(items||{});if(existing||!String(id).startsWith('city:')||options.owned===true||options.kind&&options.kind!=='chest')return out;
  const seed=hash('printed-and-bottled:'+id);if(seed%5===0)out.nukaCola=Math.min(1000000,(out.nukaCola||0)+1);if(seed%19===0)out.nukaQuantum=Math.min(1000000,(out.nukaQuantum||0)+1);if(seed%31===0){const item=Object.keys(BOOKS)[(seed>>>8)%SKILLS.length];out[item]=Math.min(1000000,(out[item]||0)+1);}return out;
 }
 function candidates(anchor,id){if(!Array.isArray(anchor)||anchor.length!==3||!anchor.every(finite))return[];const out=[],offset=hash(id)%16*Math.PI/8;for(const radius of[2.2,3.6,5.2,7.2])for(let n=0;n<12;n++){const a=offset+n*Math.PI/6;out.push([anchor[0]+Math.cos(a)*radius,anchor[2]+Math.sin(a)*radius]);}return out;}
 function model(object){
  if(!object||!BY_ID[object.id])throw Error('Modèle de collection inconnu.');object=BY_ID[object.id];
  const parts=[],box=(pos,size,color,emissive=0)=>parts.push({mesh:'cube',pos,size,color,emissive}),brown=[.30,.23,.15],blue=[.12,.28,.52],gold=[.82,.67,.25];
  box([0,.34,0],[.68,.68,.60],brown);box([0,.695,0],[.72,.04,.64],[.43,.36,.23]);
  if(object.kind==='figurine'){box([0,.75,0],[.28,.07,.28],blue);box([-.055,.86,0],[.075,.19,.09],blue);box([.055,.86,0],[.075,.19,.09],blue);box([0,1.005,0],[.19,.20,.12],blue);box([0,1.17,0],[.22,.22,.20],gold);box([-.14,1.04,0],[.09,.20,.09],blue);box([.14,1.07,0],[.09,.18,.09],gold);box([0,1.29,-.01],[.23,.04,.20],[.70,.57,.18]);}
  else if(object.kind==='magazine'){const color=BOOKS[object.item].color;box([0,.74,0],[.40,.045,.29],color);box([0,.767,0],[.28,.007,.18],[.83,.78,.58]);box([0,.773,.06],[.25,.008,.035],color);}
  else{const d=DRINKS[object.item],glow=object.item==='nukaQuantum'?.28:0;box([0,.89,0],[.16,.34,.16],d.color,glow);box([0,1.10,0],[.075,.10,.075],d.color,glow);box([0,1.16,0],[.09,.035,.09],[.72,.70,.61]);box([0,.88,-.083],[.145,.12,.008],object.item==='nukaQuantum'?[.32,.68,.81]:[.78,.13,.09],glow);}
  return parts;
 }
 return{STATS,SKILLS,DRINKS,BOOKS,AID,OBJECTS,BY_ID,DURATION,SKILL_BONUS,hash,fresh,migrate,targets,award,consume,tick,skill,loot,candidates,model};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralIconicEcosystem;

if(typeof window!=='undefined'&&typeof baseState==='function'){
 const M=MistralIconicEcosystem,clone=value=>JSON.parse(JSON.stringify(value)),runtime={owner:null,previousWorld:null,entries:[],draws:[],stands:[],boundWorld:null,clock:0,sites:[],tradeDepth:0,targets:M.targets(typeof V042_CATALOG==='undefined'?[]:V042_CATALOG),error:null};
 const itemNames=Object.assign(Object.create(null),Object.fromEntries(Object.entries(M.AID).map(([id,d])=>[id,d.name])));
 V027_SUBS.data.iconic='COLLECTION';
 for(const[id,d]of Object.entries(M.AID)){ITEM_VALUES[id]=d.value;V027_AID_DESC[id]=d.description||'Lecture : +10 '+(typeof V023_SKILLS!=='undefined'?V023_SKILLS[d.skill]?.name:d.skill)+' pendant 120 secondes de jeu actif. Ne se cumule pas avec la même aptitude.';}
 const freshBase=baseState;baseState=function(...args){const s=freshBase(...args);s.v053Iconic=M.fresh();return s;};
 const migrateBase=migrateState;migrateState=function(input={}){const s=migrateBase(input);s.v053Iconic=M.migrate(input.v053Iconic);return s;};state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const labelBase=itemLabel;itemLabel=function(id){return itemNames[id]||labelBase(id);};
 const categoryBase=v026Category;v026Category=function(id){return M.AID[id]?'aid':categoryBase(id);};
 const massBase=v026Mass;v026Mass=function(id){return M.AID[id]?.mass??massBase(id);};
 const descBase=v026Description;v026Description=function(id){return M.AID[id]?V027_AID_DESC[id]:descBase(id);};
 const skillBase=v023Skill;v023Skill=function(key){return M.skill(skillBase(key),key,state.v053Iconic);};
 const newContainerBase=v026NewContainer;v026NewContainer=function(w,id,title,pos,items,options={}){const exists=!!state.v026?.containers?.[v026Key(w.id,id)];return newContainerBase(w,id,title,pos,M.loot(id,items,options,exists),options);};
 function available(){return gameStarted&&world&&state.player.hp>0&&!zoneTransitioning&&!V046.lab&&!V046.busy&&!V047.pending&&['PLAYING','PIP','SALVAGE','FIELD'].includes(mode);}
 function snapshot(){return Object.fromEntries(['inventory','player','character','v053Iconic','lastSave','ammo','equipment','version'].map(k=>[k,state[k]===undefined?undefined:clone(state[k])]));}
 function commit(change){const owner=state,before=snapshot();try{change();computeDerived();if(state!==owner||saveGame(false)===false)throw Error('Écriture de la sauvegarde refusée.');}catch(error){if(state===owner)for(const k of Object.keys(before)){if(before[k]===undefined)delete owner[k];else owner[k]=before[k];}runtime.error=String(error.message||error);toast('Opération annulée : '+runtime.error,'bad');return false;}runtime.error=null;runtime.owner=null;return true;}
 function use(id){if(!available()||!M.AID[id])return false;let next;try{next=M.consume(snapshot(),id);}catch(error){toast(error.message,'bad');return false;}if(!commit(()=>{for(const k of['inventory','player','character','v053Iconic'])if(next[k]!==undefined)state[k]=next[k];}))return false;toast(M.BOOKS[id]?'Lecture retenue · '+M.BOOKS[id].name+' · 120 s actives':M.DRINKS[id].name+' · une capsule conservée','good');if(mode==='SALVAGE')v026Render();else if(mode==='PIP')renderPipboy();updateHUD();return true;}
 const useBase=useInventoryItem;useInventoryItem=function(id){return M.AID[id]?use(id):useBase(id);};
 const salvageUseBase=v026Use;v026Use=function(id){if(!M.AID[id])return salvageUseBase(id);return V026.open&&mode==='SALVAGE'?use(id):false;};
 const pipUseBase=v027ItemAction;v027ItemAction=function(kind,id){return kind==='use'&&M.AID[id]?(v027CanAct()?use(id):false):pipUseBase(kind,id);};
 const priceBase=tradePrice;tradePrice=function(id,buy=true,vendor=tradeState?.id){const quoted=priceBase(id,buy,vendor);return !M.AID[id]||buy?quoted:Math.min(quoted,Math.max(1,priceBase(id,true,vendor)-1));};
 function restoreOwner(owner,before){for(const key of Object.keys(owner))delete owner[key];Object.assign(owner,before);}
 function refreshTrade(){try{renderTrade();}catch{}updateHUD();}
 function trade(action,id){
  if(!gameStarted||!world||state.player.hp<=0||zoneTransitioning||V046.lab||V046.busy||V047.pending||mode!=='TRADE'||runtime.tradeDepth)return false;
  const owner=state,before=clone(state),scene=world,vendor=tradeState?.id,save=saveGame;let requested=false,args=[false];runtime.tradeDepth++;
  // The inherited barter applies stock/wallet/logs before calling saveGame.
  // Defer that call so a rejected final write restores every participating ledger.
  saveGame=function(...values){requested=true;args=values;return true;};
  try{const result=action(id);if(result?.then)throw Error('Le troc doit se terminer sans attente.');if(state!==owner||world!==scene||mode!=='TRADE'||tradeState?.id!==vendor)throw Error('Le contexte du comptoir a changé.');saveGame=save;
   if(result===false||!requested){restoreOwner(owner,before);return false;}
   if(save(...args)===false)throw Error('Écriture de la sauvegarde refusée.');runtime.error=null;return result;
  }catch(error){if(state===owner)restoreOwner(owner,before);runtime.owner=null;runtime.error=String(error.message||error);refreshTrade();toast('Troc annulé : '+runtime.error,'bad');return false;}
  finally{saveGame=save;runtime.tradeDepth--;}
 }
 const buyBase=buyTradeItem;buyTradeItem=function(id){return M.AID[id]?trade(buyBase,id):buyBase(id);};
 const sellBase=sellTradeItem;sellTradeItem=function(id){return M.AID[id]?trade(sellBase,id):sellBase(id);};
 const tradeRenderBase=renderTrade;renderTrade=function(...args){const result=tradeRenderBase(...args);if(!tradeState||typeof document==='undefined')return result;const list=$('tradeSellList');if(!list)return result;
  for(const[id,d]of Object.entries(M.AID)){if(v026Qty(id)<1||list.querySelector('[data-sell="'+id+'"]'))continue;const price=tradePrice(id,false),row=document.createElement('article');row.className='trade-row';row.innerHTML='<div><b>'+escapeHtml(d.name)+'</b><small>Disponible : '+v026Qty(id)+' · consommable conservé dans le sac</small></div><strong>'+price+' caps</strong><button data-sell="'+id+'"'+(merchantState(tradeState.id).caps<price?' disabled':'')+'>VENDRE</button>';row.querySelector('button').onclick=()=>sellTradeItem(id);list.appendChild(row);}return result;
 };
 const statusBase=updateStatus;updateStatus=function(dt){const out=statusBase(dt);if(mode==='PLAYING'&&!zoneTransitioning&&!V046.busy&&!V047.pending)state.v053Iconic=M.tick(state.v053Iconic,dt,true);return out;};
 const groundBase=groundHeightAt;
 groundHeightAt=function(x,z,referenceFeet=0){let height=groundBase(x,z,referenceFeet);if(!world||runtime.boundWorld!==world||!Number.isFinite(height))return height;const radius=state.player.crouched?.32:.38,feet=Number.isFinite(referenceFeet)?referenceFeet:0;for(const c of runtime.stands)if(c.v053Iconic&&!c.disabled&&Number.isFinite(c.v053IconicTop)&&c.v053IconicTop>=height&&c.v053IconicTop<=feet+.72+1e-7&&v017ColliderHit(c,x,z,radius))height=Math.max(height,c.v053IconicTop);return height;};
 function ground(x,z,ignoreId=null){
  if(world?.v046){if(typeof v050TravelGround!=='function')return null;return v050TravelGround({records:world.v046Records,bank:world.v047TerrainBank||V046.terrain,geoColliders:(world.colliders||[]).filter(c=>c.v046Tile),...(ignoreId?{v050GameplayColliders:(world.colliders||[]).filter(c=>!c.v046Tile&&c.v053Iconic!==ignoreId)}:{})},world,x,z,.43);}
  const value=groundBase(x,z);return Number.isFinite(value)?value:null;
 }
 function free(x,z){const y=ground(x,z);if(y===null||!Number.isFinite(y))return null;const b=world.bounds;if(!b||x<b[0]+.8||x>b[1]-.8||z<b[2]+.8||z>b[3]-.8||collidesAt(x,z,.8,y+playerEyeHeight()))return null;
  if(world.interactables.some(i=>!i.v053Iconic&&i.priority>=7&&Math.hypot(i.pos[0]-x,i.pos[2]-z)<(i.radius||3.2)+2))return null;
  if((world.npcs||[]).some(n=>n.alive!==false&&Math.hypot(n.pos[0]-x,n.pos[2]-z)<1.15)|| (world.hazards||[]).some(h=>Math.hypot((h.x??h.pos?.[0]??Infinity)-x,(h.z??h.pos?.[2]??Infinity)-z)<(h.radius||0)+.8))return null;
  for(const[dx,dz]of[[.45,0],[-.45,0],[0,.45],[0,-.45]]){const h=ground(x+dx,z+dz);if(h===null||Math.abs(h-y)>.22)return null;}return[x,y,z];
 }
 function anchor(object){
  if(world?.v046){const record=object.siteId&&V042_RUNTIME.active.get(object.siteId);if(!record||record.site?.safe!==true||!record.pos?.every(Number.isFinite))return null;return record.pos.slice();}
  return world?.id===object.scene&&world.spawn?.every(Number.isFinite)?world.spawn.slice():null;
 }
 function revalidate(record){const [x,y,z]=record.pos,read=ground(x,z,record.object.id);if(read===null||Math.abs(read-y)>.1||collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]))return false;return world.v046||!world.colliders.some(c=>c.v053Iconic!==record.object.id&&!c.disabled&&y+1.83>=(c.minY??-Infinity)&&y<=(c.maxY??Infinity)&&v017ColliderHit(c,x,z,.4));}
 function pickup(id){const rec=runtime.entries.find(e=>e.object.id===id);if(!available()||mode!=='PLAYING'||!rec||rec.world!==world||state.v053Iconic.found[id]||Math.hypot(state.player.pos[0]-rec.pos[0],state.player.pos[2]-rec.pos[2])>2.6||Math.abs(state.player.pos[1]-(rec.pos[1]+playerEyeHeight()))>1||!lineOfSight(state.player.pos,rec.interaction)||!revalidate(rec))return false;
  let award;try{award=M.award(snapshot(),id);}catch(error){toast(error.message,'bad');return false;}if(!commit(()=>{for(const k of['inventory','player','character','v053Iconic'])state[k]=award.snapshot[k];}))return false;
  toast(rec.object.kind==='figurine'?rec.object.name+(award.statGain?' · +1 permanent':' · maximum déjà atteint'):rec.object.name+' ajouté au sac.','good');bind(true);updateHUD();return true;
 }
 function bind(force=false){
  const geo=world?.v046===true,siteKey=geo?[...V042_RUNTIME.active.keys()].sort().join('|'):'';
  if(!force&&runtime.owner?.world===world&&runtime.owner.state===state&&runtime.owner.records===world?.v046Records&&runtime.owner.sites===siteKey&&runtime.owner.layer===settings.geoFalloutLayer)return runtime.entries.length;
  const previous=runtime.owner?.world||runtime.previousWorld;runtime.previousWorld=null;if(previous&&previous!==world){previous.interactables=previous.interactables.filter(i=>!i.v053Iconic);previous.colliders=previous.colliders.filter(c=>!c.v053Iconic);}if(world){world.interactables=world.interactables.filter(i=>!i.v053Iconic);world.colliders=world.colliders.filter(c=>!c.v053Iconic);}runtime.entries=[];runtime.draws=[];runtime.stands=[];runtime.boundWorld=world;
  runtime.owner={world,state,records:world?.v046Records,sites:siteKey,layer:settings.geoFalloutLayer};if(!world||V046.lab||geo&&!settings.geoFalloutLayer||world.v050CityInterior)return 0;
  const used=[];for(const object of runtime.targets){if(state.v053Iconic.found[object.id])continue;const at=anchor(object);if(!at)continue;let pos=null;
   for(const[x,z]of M.candidates(at,object.id)){if(used.some(p=>Math.hypot(p[0]-x,p[2]-z)<1.25))continue;const p=free(x,z);if(!p)continue;if(!lineOfSight([at[0],at[1]+playerEyeHeight(),at[2]],[x,p[1]+1.0,z]))continue;pos=p;break;}if(!pos)continue;used.push(pos);
   const interaction=[pos[0],pos[1]+(object.kind==='figurine'?1.1:object.kind==='magazine'?.82:.95),pos[2]],record={object,world,pos,interaction};runtime.entries.push(record);
   const collider=addCollider(world,pos[0],pos[2],.68,.60,{id:'iconic-stand:'+object.id,minY:pos[1],maxY:pos[1]+.715});collider.v053Iconic=object.id;collider.v053IconicTop=pos[1]+.72;runtime.stands.push(collider);
   const temporary={staticDraws:[]};for(const[p,part]of M.model(object).entries()){const center=[pos[0]+part.pos[0],pos[1]+part.pos[1],pos[2]+part.pos[2]],draw=addPart(temporary,part.mesh,center,part.size,part.color,0,{id:'iconic:'+object.id+':'+p,emissive:part.emissive});draw.v053Iconic={id:object.id,kind:object.kind,provenance:'authored-game-content'};}runtime.draws.push(...temporary.staticDraws);
   const item=addInteract(world,'iconic:'+object.id,interaction,(object.kind==='figurine'?'Récupérer · ':'Prendre · ')+object.name,()=>pickup(object.id),{radius:2.6,kind:'loot',priority:5.2});item.v053Iconic=object.id;
  }return runtime.entries.length;
 }
 const publishBase=v046Publish;v046Publish=function(...args){const result=publishBase(...args);if(args[0]===world)runtime.owner=null;return result;};
 const loadBase=loadZone;loadZone=function(...args){runtime.previousWorld=runtime.owner?.world||world;runtime.owner=null;return loadBase(...args);};
 const updateBase=updatePlayer;updatePlayer=function(dt){const result=updateBase(dt);runtime.clock+=Number.isFinite(dt)?dt:0;if(runtime.clock>=.75){runtime.clock=0;bind();}return result;};
 const collectBase=collectDraws;collectDraws=function(t){const draws=collectBase(t);bind();return draws.concat(runtime.draws);};
 function panel(c){const ledger=state.v053Iconic,stats=M.OBJECTS.filter(o=>o.kind==='figurine'),esc=escapeHtml;
  c.innerHTML=`<div class="p27-long"><p class="p27-kicker">COLLECTION ET LECTURES</p><h2>Trésors du Wasteland</h2><p>Sept figurines améliorent chacune un attribut S.P.E.C.I.A.L. de 1, une seule fois, dans la limite de 10. Les exemplaires physiques se trouvent dans les scènes habitées et leurs relais géographiques ; ces deux accès partagent la même collection.</p><p>${stats.filter(o=>ledger.found[o.id]).length}/7 figurines récupérées. Les présentoirs et leurs emplacements sont des créations du jeu, sans relevé architectural.</p>${stats.map(o=>`<section><h3>${esc(o.name)}</h3><p>${ledger.found[o.id]?'RÉCUPÉRÉE · aucun bonus à reprendre':'À DÉCOUVRIR · relais habités et scènes régionales'}</p></section>`).join('')}<h2>Magazines d’aptitudes</h2><p>La lecture consomme un exemplaire et ajoute 10 points pendant 120 secondes de jeu actif. Un même bonus ne se cumule pas ; les menus et chargements ne consomment pas la durée. La lecture n’accomplit aucune quête à votre place.</p>${Object.entries(M.BOOKS).map(([id,d])=>`<p><b>${esc(d.name)}</b> · ${ledger.read[id]||0} lecture(s)${ledger.effects[d.skill]>0?' · '+Math.ceil(ledger.effects[d.skill])+' s restantes':''}</p>`).join('')}<h2>Nuka-Cola et Quantum</h2><p>Les bouteilles rejoignent AIDE dans l’inventaire. Leurs PV et PA respectent vos maxima ; la dose de radiation et la capsule conservée sont appliquées au même paiement. ${ledger.drinks} bouteille(s) consommée(s).</p><p>Les réserves inventées de certains bâtiments peuvent aussi contenir une bouteille ou un magazine. Leur contenu est fini et ne se renouvelle pas à la réentrée.</p></div>`;
 }
 const dataBase=v027Data;v027Data=function(c){return V027.sub==='iconic'?panel(c):dataBase(c);};
 globalThis.v053IconicAfterInit=function(){V027_SUBS.data.iconic='COLLECTION';Object.assign(window.__MISTRAL_DEBUG,{v053IconicInfo:()=>({schema:1,found:clone(state.v053Iconic.found),effects:clone(state.v053Iconic.effects),read:clone(state.v053Iconic.read),drinks:state.v053Iconic.drinks,physical:runtime.entries.map(e=>({id:e.object.id,kind:e.object.kind,name:e.object.name,siteId:e.object.siteId,scene:e.object.scene,pos:e.pos.slice(),interaction:e.interaction.slice()})),draws:runtime.draws.length,error:runtime.error,provenance:'Authored game objects and procedural models; not surveyed architecture or recovered studio assets'}),v053IconicBind:()=>bind(true),v053IconicPickup:pickup,v053IconicUse:use,v053IconicCatalog:()=>clone(runtime.targets)});bind(true);};
}
