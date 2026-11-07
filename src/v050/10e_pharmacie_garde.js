/* Pharmacies de Garde: original authored overlay, no surveyed pharmacy claimed.
   World time owns shifts; stocks never replenish on a shift or a reload. */
const MistralPharmacy=(()=>{
 'use strict';
 const copy=v=>JSON.parse(JSON.stringify(v)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const HOME='v042-marseille-settlement-02';
 const BRANCHES=[
  {id:'port',site:'v042-marseille-caravan-01',name:'Comptoir du Vieux-Port',hours:'06 h – 14 h',voice:'Lise Ravel',note:'La croix annonce une présence, pas une réserve sans fond.'},
  {id:'gare',site:'v042-marseille-caravan-02',name:'Comptoir de Saint-Charles',hours:'14 h – 22 h',voice:'Sofiane Tabet',note:'Le train est en retard. Le registre de garde aussi.'},
  {id:'aubagne',site:'v042-huveaune-caravan-02',name:'Comptoir d’Aubagne Haute',hours:'22 h – 06 h',voice:'Bérénice Fabre',note:'Une famille ne transmet pas ses dettes avec son ordonnance.'}
 ];
 const IDS=BRANCHES.map(b=>b.id),STAGES=['new','announced','redirected','carrying','done'];
 const GOODS={stimpak:{price:25,count:2},antibiotics:{price:18,count:1}};
 const METHODS={troc:{label:'Apporter des fournitures à l’équipe',cost:{water:2,cloth:2}},reparation:{label:'Réparer le coffret de conservation',cost:{scrap:2,circuitry:1}},controle:{label:'Contrôler les scellés · INT 5',cost:{chemicals:1},intelligence:5}};
 const ENDINGS={direct:{label:'Remise directe, reçu anonymisé',text:'Le dispensaire reçoit le lot. Le registre public conserve la quantité, pas le nom du patient. L’équipe remet un Stimpak et 35 capsules.',caps:35,items:{stimpak:1},care:0},mutuelle:{label:'Réserve mutualiste, sans dette héréditaire',text:'Le patient reçoit sa part en premier. Le reste rejoint une réserve contrôlée. L’équipe remet 20 capsules et trois prises en charge de 30 PV, sans effet sur les radiations ni les maladies.',caps:20,items:{},care:3}};
 function fresh(){return{schema:1,stage:'new',announced:null,supplier:null,method:null,outcome:null,care:0,stock:Object.fromEntries(IDS.map(id=>[id,Object.fromEntries(Object.entries(GOODS).map(([k,v])=>[k,v.count]))])),journal:[]};}
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Registre de pharmacie plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.announced=IDS.includes(raw.announced)?raw.announced:null;l.supplier=IDS.includes(raw.supplier)?raw.supplier:null;
  l.method=own(METHODS,raw.method)?raw.method:null;l.outcome=own(ENDINGS,raw.outcome)?raw.outcome:null;
  if(l.outcome){l.stage='done';l.care=l.outcome==='mutuelle'&&Number.isInteger(raw.care)?Math.max(0,Math.min(3,raw.care)):0;}
  else if(l.announced){l.stage=STAGES.includes(raw.stage)?raw.stage:'announced';if(l.stage==='new'||l.stage==='done')l.stage='announced';if(!l.supplier)l.stage='announced';else if(l.stage==='carrying'&&!l.method)l.stage='redirected';}
  // Absent/invalid stock in an existing register cannot mint new medicine.
  for(const id of IDS)for(const[k,g]of Object.entries(GOODS)){const n=raw.stock?.[id]?.[k];l.stock[id][k]=Number.isInteger(n)&&n>=0?Math.min(g.count,n):0;}
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&['accept','notice','collect','resolve','buy','care'].includes(e.type)).slice(-32).map(e=>({type:e.type,site:BRANCHES.some(b=>b.site===e.site)||e.site===HOME?e.site:null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];
  return l;
 }
 function duty(hour){if(!Number.isFinite(hour))return null;const h=((hour%24)+24)%24;return h>=6&&h<14?BRANCHES[0]:h>=14&&h<22?BRANCHES[1]:BRANCHES[2];}
 const branch=id=>BRANCHES.find(b=>b.id===id);
 function next(raw){const l=migrate(raw);return l.stage==='announced'?branch(l.announced)?.site:l.stage==='redirected'?branch(l.supplier)?.site:HOME;}
 function briefing(raw,hour){const l=migrate(raw),d=duty(hour),clock=d?`Garde actuelle : ${d.name}, ${d.hours}.`:'Horaire indisponible.';return clock+' '+(l.stage==='new'?'Longchamp attend un porteur pour un lot médical.':l.stage==='announced'?`Le reçu initial désigne ${branch(l.announced).name}. Vérifiez-y le planning.`:l.stage==='redirected'?`Un échange de garde n’a pas été transmis. Le lot est réservé à ${branch(l.supplier).name}, même après la relève.`:l.stage==='carrying'?'Lot scellé en votre garde. Rapportez-le à Longchamp.':ENDINGS[l.outcome].text);}
 function apply(snapshot,action={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));
  if(!ctx.contact)throw Error('Rencontrez le représentant de ce comptoir.');
  if(!snapshot?.player||!Number.isFinite(snapshot.player.hp)||snapshot.player.hp<=0)throw Error('Une partie active est nécessaire.');
  // Validate before JSON cloning: NaN must not become null and then zero.
  const validCount=n=>Number.isInteger(n)&&n>=0&&n<=999999;
  if(!validCount(snapshot.player.caps))throw Error('Compte de capsules invalide.');
  for(const[k,n]of Object.entries(snapshot.inventory||{}))if(!validCount(n))throw Error('Inventaire invalide : '+k);
  const s=copy(snapshot),l=migrate(s.v062Pharmacy),b=BRANCHES.find(b=>b.site===ctx.site);s.inventory??={};
  const needSite=site=>{if(ctx.site!==site)throw Error('Ce dossier appartient à un autre relais.');};
  const change=(items,sign)=>{for(const[k,n]of Object.entries(items)){const v=(s.inventory[k]??0)+sign*n;if(!validCount(v))throw Error('Fournitures insuffisantes ou capacité du registre dépassée.');}for(const[k,n]of Object.entries(items))s.inventory[k]=(s.inventory[k]??0)+sign*n;};
  if(action.type==='accept'){
   needSite(HOME);if(l.stage!=='new')throw Error('La demande est déjà ouverte.');const d=duty(s.worldTime);if(!d)throw Error('Horaire indisponible.');l.stage='announced';l.announced=d.id;
  }else if(action.type==='notice'){
   if(l.stage!=='announced')throw Error('Le planning a déjà été vérifié ou la demande n’est pas ouverte.');needSite(branch(l.announced).site);l.supplier=IDS[(IDS.indexOf(l.announced)+1)%IDS.length];l.stage='redirected';
  }else if(action.type==='collect'){
   if(l.stage!=='redirected')throw Error('Vérifiez le planning avant de retirer le lot, une seule fois.');needSite(branch(l.supplier).site);
   const m=METHODS[action.choice];if(!own(METHODS,action.choice))throw Error('Méthode inconnue.');
   const intelligence=Number(s.character?.special?.I);if(m.intelligence&&(!Number.isFinite(intelligence)||intelligence<m.intelligence))throw Error('Intelligence 5 requise pour le contrôle des scellés.');
   change(m.cost,-1);l.method=action.choice;l.stage='carrying';
  }else if(action.type==='resolve'){
   needSite(HOME);if(l.stage!=='carrying')throw Error('Rapportez le lot avant de conclure, une seule fois.');if(!own(ENDINGS,action.choice))throw Error('Répartition inconnue.');const e=ENDINGS[action.choice];
   if(!validCount(s.player.caps+e.caps))throw Error('Compte de capsules saturé.');change(e.items,1);s.player.caps+=e.caps;l.stage='done';l.outcome=action.choice;l.care=e.care;
  }else if(action.type==='buy'){
   if(l.stage==='new'||!b||duty(s.worldTime)?.id!==b.id)throw Error('Le comptoir de garde est fermé ou non connu.');
   if(!own(GOODS,action.item)||!l.stock[b.id][action.item])throw Error('Stock épuisé ou produit inconnu.');const price=GOODS[action.item].price;
   if(s.player.caps<price)throw Error('Capsules insuffisantes.');change({[action.item]:1},1);s.player.caps-=price;l.stock[b.id][action.item]--;
  }else if(action.type==='care'){
   if(!b||duty(s.worldTime)?.id!==b.id)throw Error('Rejoignez le comptoir actuellement de garde.');if(l.stage!=='done'||l.outcome!=='mutuelle'||l.care<=0)throw Error('Aucune prise en charge restante.');
   if(!Number.isFinite(s.player.maxHp)||s.player.hp>=s.player.maxHp)throw Error('Aucun PV à restaurer.');s.player.hp=Math.min(s.player.maxHp,s.player.hp+30);l.care--;
  }else throw Error('Action de pharmacie inconnue.');
  l.journal.push({type:action.type,site:ctx.site,at:Number.isFinite(s.playTime)?Math.max(0,s.playTime):0});l.journal=l.journal.slice(-32);s.v062Pharmacy=l;return s;
 }
 return{HOME,BRANCHES:copy(BRANCHES),METHODS:copy(METHODS),ENDINGS:copy(ENDINGS),GOODS:copy(GOODS),fresh,migrate,duty,next,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralPharmacy;

if(typeof baseState==='function'&&typeof V042_RUNTIME!=='undefined'){
 const M=MistralPharmacy,copy=v=>JSON.parse(JSON.stringify(v));
 const base=baseState;baseState=function(...a){const s=base(...a);s.v062Pharmacy=M.fresh();return s;};
 const migration=migrateState;migrateState=function(raw={}){const s=migration(raw);s.v062Pharmacy=M.migrate(raw?.v062Pharmacy);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const rt={world:null,state:null,signature:null,records:null,entries:[],draws:[],busy:false,error:null};
 const sites=[M.HOME,...M.BRANCHES.map(b=>b.site)],known=id=>sites.includes(id);
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE'].includes(mode)||!(state.player.hp>0)?'Reprenez une partie active.':V046.lab?'Le banc synthétique ne modifie pas la campagne.':zoneTransitioning||V046.busy||V047.pending?'Attendez la fin du chargement.':!world?.v046||state.v042?.activeInterior||world.v050CityInterior||!settings.geoFalloutLayer?'Rejoignez les relais extérieurs.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':v050TravelNearbyThreat(world,state.player.pos)?'Éloignez-vous du combat.':null;}
 function contact(id){const site=v042Site(id),p=state.player.pos;if(!site||!v042SiteDiscovered(site))return false;return (world?.npcs||[]).some(n=>n.alive!==false&&(n.v042Site===id||V042_RUNTIME.npcData.get(n.id)?.siteId===id)&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
 function notice(text){V027.message=text;toast(text,'bad');return false;}
 function restore(owner,snapshot){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,snapshot);}
 function act(type,site,choice,item){
  if(rt.busy)return false;const owner=state,scene=world,before=copy(owner);let next;
  try{next=M.apply(owner,{type,choice,item},{blocked:blocked(),contact:contact(site),site});}catch(e){return notice(e.message);}
  rt.busy=true;
  try{owner.v062Pharmacy=next.v062Pharmacy;owner.inventory=next.inventory;owner.player.caps=next.player.caps;owner.player.hp=next.player.hp;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde refusée.');}
  catch(e){restore(owner,before);return notice(e.message+' Échange annulé.');}finally{rt.busy=false;}
  rt.signature=null;try{bind();updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast('Registre de garde sauvegardé.','good');}catch(e){rt.error='Présentation après sauvegarde : '+e.message;}return true;
 }
 const costs=v=>Object.entries(v).map(([id,n])=>n+' '+itemLabel(id)).join(' + ');
 function talk(site){
  if(blocked()||!contact(site))return notice(blocked()||'Rejoignez le représentant.');const owner=state,scene=world,l=state.v062Pharmacy,b=M.BRANCHES.find(b=>b.site===site),choices=[],safe=fn=>()=>state===owner&&world===scene&&fn();
  const option=(text,type,choice,item)=>choices.push({text,onChoose:safe(()=>{act(type,site,choice,item);talk(site);})});
  if(site===M.HOME&&l.stage==='new')option('Accepter la recherche du lot scellé.','accept');
  if(l.stage==='announced'&&M.BRANCHES.find(b=>b.id===l.announced)?.site===site)option('Vérifier le planning affiché et son contre-reçu.','notice');
  if(l.stage==='redirected'&&M.BRANCHES.find(b=>b.id===l.supplier)?.site===site)for(const[id,m]of Object.entries(M.METHODS))option(m.label+' · '+costs(m.cost),'collect',id);
  if(l.stage==='carrying'&&site===M.HOME)for(const[id,e]of Object.entries(M.ENDINGS))option(e.label,'resolve',id);
  if(b&&l.stage!=='new'&&M.duty(state.worldTime)?.id===b.id){for(const[id,g]of Object.entries(M.GOODS))if(l.stock[b.id][id]>0)option('Acheter '+itemLabel(id)+' · '+g.price+' capsules · reste '+l.stock[b.id][id],'buy',null,id);if(l.care>0)option('Prise en charge · +30 PV maximum · reste '+l.care,'care');}
  choices.push({text:'Revenir.',onChoose:closeDialogue});
  const context=state.v060Council?.status==='ratified'?'La charte ratifiée reste consultable ; ce litige n’en réécrit pas le vote.':state.v054Services?.quests?.carte_verte?.outcome?'Votre décision de La carte verte est connue. Ce lot reste une livraison distincte.':'La Sociale et les officines partagent les soins, pas toujours leurs horaires.';
  openDialogue(speaker(b?.voice||'Dispensaire de Longchamp','PHARMACIES DE GARDE','PG'),'La pharmacie de garde — '+M.briefing(l,state.worldTime)+'\n\n'+(b?b.note:'Une personne reste sous la surveillance de l’équipe. Le lot réservé ne périme pas pendant votre trajet ; aucun compte à rebours ne provoque une mort hors écran.')+'\n\n'+context,choices);return true;
 }
 const oldTalk=v042TalkNPC;v042TalkNPC=function(id){const site=V042_RUNTIME.npcData.get(id)?.siteId;if(!known(site)||blocked()||!contact(site))return oldTalk(...arguments);const oldOpen=openDialogue,owner=state,scene=world;openDialogue=function(s,text,choices=[],...rest){const topic={text:'Pharmacies de Garde · planning et lot scellé',onChoose:()=>state===owner&&world===scene&&talk(site)};return oldOpen(s,text,[...choices.slice(0,-1),topic,...choices.slice(-1)],...rest);};try{return oldTalk(...arguments);}finally{openDialogue=oldOpen;}};
 function ground(x,z){return v050TravelGround({records:world.v046Records,bank:world.v047TerrainBank||V046.terrain,geoColliders:world.colliders.filter(c=>c.v046Tile),v050GameplayColliders:world.colliders.filter(c=>!c.v046Tile&&!c.v062Pharmacy)},world,x,z,.55);}
 function place(anchor,previous){const candidates=previous?[[previous[0],previous[2],true]]:[];for(const r of[5.5,7.5,9.5])for(let i=0;i<12;i++)candidates.push([anchor[0]+Math.cos(i*Math.PI/6)*r,anchor[2]+Math.sin(i*Math.PI/6)*r,false]);for(const[x,z,retained]of candidates){const y=ground(x,z);if(!Number.isFinite(y)||[[.55,.45],[-.55,.45],[.55,-.45],[-.55,-.45]].some(([dx,dz])=>{const h=ground(x+dx,z+dz);return !Number.isFinite(h)||Math.abs(h-y)>.12;}))continue;
   if(world.colliders.some(c=>!c.v062Pharmacy&&!c.disabled&&y+1.8>=(c.minY??-Infinity)&&y<=(c.maxY??Infinity)&&v017ColliderHit(c,x,z,.8))||world.npcs.some(n=>Math.hypot(n.pos[0]-x,n.pos[2]-z)<1.7)||world.interactables.some(i=>!i.v062Pharmacy&&Math.hypot(i.pos[0]-x,i.pos[2]-z)<2)||!retained&&Math.hypot(state.player.pos[0]-x,state.player.pos[2]-z)<1.4)continue;
   if(!lineOfSight([anchor[0],anchor[1]+1.6,anchor[2]],[x,y+1,z]))continue;return[x,y,z];}return null;}
 function bind(){
  const signature=[settings.geoFalloutLayer,V046.lab,world?.v050CityInterior,M.duty(state.worldTime)?.id,state.v062Pharmacy.stage,state.v062Pharmacy.supplier,...[...V042_RUNTIME.active.entries()].filter(([id])=>known(id)).map(([id,r])=>id+':'+r.pos?.join(','))].join('|');
  if(rt.world===world&&rt.state===state&&rt.records===world?.v046Records&&rt.signature===signature)return;
  const previous=rt.world===world&&rt.state===state?new Map(rt.entries.map(e=>[e.site,e.pos])):new Map();
  if(rt.world){rt.world.colliders=rt.world.colliders.filter(c=>!c.v062Pharmacy);rt.world.interactables=rt.world.interactables.filter(c=>!c.v062Pharmacy);}rt.world=world;rt.state=state;rt.records=world?.v046Records;rt.signature=signature;rt.entries=[];rt.draws=[];
  if(!world?.v046||V046.lab||!settings.geoFalloutLayer||world.v050CityInterior||state.v042?.activeInterior)return;
  for(const site of sites){const rec=V042_RUNTIME.active.get(site);if(!rec?.site.safe||!rec.pos?.every(Number.isFinite))continue;const pos=place(rec.pos,previous.get(site));if(!pos)continue;const b=M.BRANCHES.find(b=>b.site===site),active=b&&M.duty(state.worldTime)?.id===b.id,temp={staticDraws:[]},box=(offset,size,color)=>addBox(temp,pos.map((v,i)=>v+offset[i]),size,color),green=active?[.20,.8,.36]:[.24,.34,.27];
   box([0,.42,0],[.94,.84,.64],[.37,.40,.35]);box([0,.85,0],[1,.06,.7],[.65,.68,.56]);box([0,1.19,0],[.10,.65,.10],[.27,.30,.28]);box([0,1.58,0],[.76,.19,.14],green);box([0,1.58,0],[.20,.60,.14],green);
   const reserved=state.v062Pharmacy.stage==='redirected'&&b?.id===state.v062Pharmacy.supplier;if(reserved)box([0,1.02,.2],[.48,.27,.30],[.73,.70,.49]);
   for(const d of temp.staticDraws){d.v062Pharmacy=site;d.v042Site=site;}rt.draws.push(...temp.staticDraws);
   const c=addCollider(world,pos[0],pos[2],1,.7,{id:'pharmacy62:'+site,minY:pos[1],maxY:pos[1]+1.88});c.v062Pharmacy=site;c.v042Site=site;
   const e={site,pos,world,state},point=[pos[0],pos[1]+1.15,pos[2]+.65];const it=addInteract(world,'pharmacy62:'+site,point,'Lire le planning de garde',()=>{if(e.world!==world||e.state!==state||blocked())return false;openNote('pharmacy62:'+site,'PHARMACIES DE GARDE',M.BRANCHES.map(b=>b.name+' : '+b.hours).join('\n')+'\n\n'+M.briefing(state.v062Pharmacy,state.worldTime)+'\n\nLes échanges se font auprès du représentant. Stocks finis, non renouvelés à la relève.');return true;},{radius:3,priority:4.1,kind:'note',condition:()=>!blocked()&&e.world===world&&e.state===state&&Math.hypot(state.player.pos[0]-pos[0],state.player.pos[2]-pos[2])<3&&Math.abs(state.player.pos[1]-point[1])<2&&lineOfSight(state.player.pos,point)});it.v062Pharmacy=site;it.v042Site=site;rt.entries.push(e);
  }
 }
 const draw=collectDraws;collectDraws=function(...a){const result=draw(...a);bind();return result.concat(rt.draws);};
 function track(site=M.next(state.v062Pharmacy)){if(!known(site)||!v042Site(site)||blocked())return false;const owner=state,before=copy(owner),scene=world;owner.v042.tracked=site;try{if(state!==owner||world!==scene||saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Suivi non sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
 V027_SUBS.data.pharmacie='PHARMACIES DE GARDE';
 const data=v027Data;v027Data=function(c){if(V027.sub!=='pharmacie')return data(...arguments);const l=state.v062Pharmacy,esc=v027Escape,duty=M.duty(state.worldTime);c.innerHTML='<div class="p27-long"><p class="p27-kicker">LA SOCIALE ET LES OFFICINES</p><h2>La pharmacie de garde</h2><p>'+esc(M.briefing(l,state.worldTime))+'</p>'+v027Button('Suivre la prochaine étape','ph62:track',M.next(l))+'<h3>Planning quotidien · heure du jeu</h3>'+M.BRANCHES.map(b=>'<section class="v046-notice"><h3>'+esc(b.name)+'</h3><p>'+esc(b.hours)+' · '+(duty?.id===b.id?'DE GARDE':'FERMÉ')+'</p><p>'+esc(b.note)+'</p><p>'+Object.entries(M.GOODS).map(([id,g])=>esc(itemLabel(id))+' : '+l.stock[b.id][id]+' en réserve · '+g.price+' capsules').join(' / ')+'</p>'+v027Button('Suivre ce comptoir','ph62:track',b.site)+'</section>').join('')+'<p>Prises en charge restantes : '+l.care+'. Un achat, un retrait ou un soin exige la présence du représentant. Le lot de quête est distinct du stock à vendre.</p></div>';};
 const dispatch=v027Dispatch;v027Dispatch=function(action,arg){return action==='ph62:track'?v027CanAct()&&track(arg):dispatch(...arguments);};
 const rows=v027QuestRows;v027QuestRows=function(){const l=state.v062Pharmacy;return rows(...arguments).concat(l.stage==='new'?[]:[{id:'ph62:quest',name:'LA PHARMACIE DE GARDE',stage:l.stage==='done'?'done':'active',active:l.stage!=='done'&&state.v042.tracked===M.next(l),text:M.briefing(l,state.worldTime),zone:null,steps:[['Vérifier le planning initial',l.stage!=='announced'],['Récupérer le lot réservé',['carrying','done'].includes(l.stage)],['Remettre le lot à Longchamp',l.stage==='done']],source:'Pharmacies de Garde',hint:'Les réserves ne se renouvellent pas à la relève',badge:l.stage==='done'?'✓':''}]);};
 const oldTrack=v027Track;v027Track=function(id){return id==='ph62:quest'?track():oldTrack(...arguments);};
 V027_STATIONS.pharmacie={name:'La croix verte — garde et recours',freq:'94.2',hint:'Planning des officines et suivi du lot',available:()=>state.v062Pharmacy.stage!=='new',text:()=>M.briefing(state.v062Pharmacy,state.worldTime)};
 const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v062PharmacyInfo:()=>{bind();return{ledger:copy(state.v062Pharmacy),duty:M.duty(state.worldTime),physical:rt.entries.map(e=>({site:e.site,pos:e.pos.slice()})),draws:rt.draws.length,error:rt.error};},v062PharmacyOpen:()=>v027Open('data','pharmacie'),v062PharmacyAction:act,v062PharmacyTalk:talk});};
}
