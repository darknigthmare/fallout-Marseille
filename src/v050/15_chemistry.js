/* Fictional chem effects, tolerance and withdrawal: bounded simulation rules.
   All quantities and durations below are game mechanics, not medical claims. */
const MistralChems=(()=>{
 const EPS=1e-7,DURATION=120,WASHOUT=180,WITHDRAWAL=300,MAX_LOAD=6,MAX_USES=1000000;
 const copy=v=>JSON.parse(JSON.stringify(v)),finite=n=>typeof n==='number'&&Number.isFinite(n),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const DEFINITIONS={
  jet:{name:'Jet',value:24,mass:.1,description:'Consommable de jeu : réserve maximale de PA +20 et recharge correspondante pendant 120 s actives. Tolérance et dépendance possibles.'},
  buffout:{name:'Buffout',value:28,mass:.1,description:'Consommable de jeu : PV maximaux +20, charge +15 kg et réserve de PV correspondante pendant 120 s actives. Tolérance et dépendance possibles.'},
  mentats:{name:'Mentats',value:26,mass:.1,description:'Consommable de jeu : Science, Réparation et Éloquence +15 pendant 120 s actives. Tolérance et dépendance possibles.'},
  psycho:{name:'Psycho',value:30,mass:.1,description:'Consommable de jeu : dégâts de vos armes et attaques V.A.T.S. +25 % pendant 120 s actives. Tolérance et dépendance possibles.'}
 };
 const IDS=Object.keys(DEFINITIONS),STOCKS={aubagne:{mentats:3,buffout:2},noailles:{jet:3,mentats:2},ciotatPort:{psycho:3,buffout:2}};
 const known=id=>typeof id==='string'&&Object.hasOwn(DEFINITIONS,id),integer=(n,max=MAX_USES)=>Number.isInteger(n)&&n>=0?Math.min(n,max):0;
 function row(){return{uses:0,load:0,washout:0,active:0,tier:0,dependent:false,withdrawal:0};}
 function fresh(){return{schema:1,elapsed:0,agents:Object.fromEntries(IDS.map(id=>[id,row()])),stocked:{},treatments:0,recoveries:0};}
 function migrate(raw){
  const out=fresh(),p=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{};out.elapsed=finite(p.elapsed)&&p.elapsed>=0?Math.min(p.elapsed,1e9):0;
  out.treatments=integer(p.treatments);out.recoveries=integer(p.recoveries);
  for(const id of Object.keys(STOCKS))if(Object.hasOwn(p.stocked||{},id)&&p.stocked[id]===true)out.stocked[id]=true;
  for(const id of IDS){const old=Object.hasOwn(p.agents||{},id)&&p.agents[id]&&typeof p.agents[id]==='object'?p.agents[id]:{},r=out.agents[id];r.uses=integer(old.uses);r.load=integer(old.load,MAX_LOAD);r.tier=integer(old.tier,3);r.active=finite(old.active)&&old.active>EPS?Math.min(old.active,DURATION):0;r.dependent=old.dependent===true||r.load>=3;
   r.washout=r.load?(finite(old.washout)&&old.washout>EPS?Math.min(old.washout,WASHOUT):WASHOUT):0;
   r.withdrawal=r.active?0:r.dependent?(finite(old.withdrawal)&&old.withdrawal>EPS?Math.min(old.withdrawal,WITHDRAWAL):WITHDRAWAL):0;
  }return out;
 }
 function tolerance(r){return Math.min(3,Math.floor(r.load/2));}
 function phase(r){return r.active>EPS?'active':r.dependent&&r.withdrawal>EPS?'withdrawal':r.load>0?'washout':'clear';}
 function modifiers(raw){
  const s=migrate(raw),m={hp:0,ap:0,carry:0,skills:{science:0,repair:0,speech:0},damage:1};
  for(const id of IDS){const r=s.agents[id],active=r.active>EPS,power=active?1-.2*r.tier:0,withdraw=!active&&r.dependent;
   if(id==='jet')m.ap=active?Math.round(20*power):withdraw?-15:0;
   if(id==='buffout'){m.hp=active?Math.round(20*power):withdraw?-10:0;m.carry=active?Math.round(15*power):withdraw?-10:0;}
   if(id==='mentats')for(const key of Object.keys(m.skills))m.skills[key]=active?Math.round(15*power):withdraw?-10:0;
   if(id==='psycho')m.damage=active?1+.25*power:withdraw?.85:1;
  }return m;
 }
 function dose(raw,id){if(!known(id))throw Error('Consommable chimique inconnu.');const s=migrate(raw),r=s.agents[id];r.uses=Math.min(MAX_USES,r.uses+1);r.load=Math.min(MAX_LOAD,r.load+1);r.washout=WASHOUT;r.tier=tolerance(r);r.active=DURATION;r.dependent=r.dependent||r.load>=3;r.withdrawal=0;return s;}
 function advance(raw,dt,active=true){
  const out=migrate(raw);if(!active||!finite(dt)||dt<=0)return out;out.elapsed=Math.min(1e9,out.elapsed+dt);
  for(const id of IDS){const r=out.agents[id];let remaining=dt,events=0;
   while(remaining>EPS&&events++<20){const wasActive=r.active>EPS,wasWithdrawal=!wasActive&&r.dependent&&r.withdrawal>EPS,hasLoad=r.load>0;
    const step=Math.min(remaining,wasActive?r.active:wasWithdrawal?r.withdrawal:Infinity,hasLoad?r.washout:Infinity);if(!Number.isFinite(step)||step<0)break;
    if(wasActive)r.active=Math.max(0,r.active-step);else if(wasWithdrawal)r.withdrawal=Math.max(0,r.withdrawal-step);if(hasLoad)r.washout=Math.max(0,r.washout-step);remaining-=step;
    if(wasActive&&r.active<=EPS){r.active=0;r.tier=0;if(r.dependent)r.withdrawal=WITHDRAWAL;}
    if(wasWithdrawal&&r.withdrawal<=EPS){r.withdrawal=0;r.dependent=false;r.load=0;r.washout=0;r.tier=0;out.recoveries=Math.min(MAX_USES,out.recoveries+1);}
    if(r.load>0&&r.washout<=EPS){r.load--;r.washout=r.load?WASHOUT:0;}
    if(step<=EPS&&!wasActive&&!wasWithdrawal&&!hasLoad)break;
   }
  }return out;
 }
 function summary(raw){const s=migrate(raw);return IDS.map(id=>{const r=s.agents[id];return{id,name:DEFINITIONS[id].name,...r,phase:phase(r),tolerance:tolerance(r),strength:r.active>0?Math.round((1-.2*r.tier)*100):0};});}
 function cost(raw){const count=summary(raw).filter(r=>r.load>0||r.dependent||r.active>0).length;return count?40+20*count:0;}
 function signature(raw){return JSON.stringify(migrate(raw));}
 function treat(raw){const s=migrate(raw);if(!cost(s))throw Error('Aucun effet ou état de dépendance à traiter.');for(const id of IDS){const uses=s.agents[id].uses;s.agents[id]=row();s.agents[id].uses=uses;}s.treatments=Math.min(MAX_USES,s.treatments+1);return s;}
 function loot(id,items,options={},existing=false){const out=copy(items||{});if(existing||!String(id).startsWith('city:')||options.owned===true||options.kind&&options.kind!=='chest')return out;let hash=2166136261;for(const c of 'chems:'+id)hash=Math.imul(hash^c.charCodeAt(0),16777619);const seed=hash>>>0;if(seed%13===0){const item=IDS[(seed>>>8)%IDS.length];out[item]=Math.min(MAX_USES,(out[item]||0)+1);}return out;}
 return{EPS,DURATION,WASHOUT,WITHDRAWAL,MAX_LOAD,MAX_USES,IDS,DEFINITIONS,STOCKS,known,row,fresh,migrate,tolerance,phase,modifiers,dose,advance,summary,cost,signature,treat,loot};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralChems;

if(typeof window!=='undefined'&&typeof baseState==='function'){
 const M=MistralChems,clone=v=>JSON.parse(JSON.stringify(v)),runtime={quote:null,error:null,depth:0,commits:0,rollbacks:0};
 V027_SUBS.status.chemistry='DÉPENDANCES';
 for(const[id,d]of Object.entries(M.DEFINITIONS)){ITEM_VALUES[id]=d.value;V027_AID_DESC[id]=d.description+' Trois prises rapprochées rendent dépendant ; le retrait devient actif après le bonus.';}
 const freshBase=baseState;baseState=function(...a){const s=freshBase(...a);s.v054Chems=M.fresh();return s;};
 const migration=migrateState;migrateState=function(input={}){const s=migration(input);s.v054Chems=M.migrate(input.v054Chems);return s;};state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const labels=itemLabel;itemLabel=function(id){return M.known(id)?M.DEFINITIONS[id].name:labels(id);};
 const category=v026Category;v026Category=function(id){return M.known(id)?'aid':category(id);};
 const mass=v026Mass;v026Mass=function(id){return M.known(id)?M.DEFINITIONS[id].mass:mass(id);};
 const description=v026Description;v026Description=function(id){return M.known(id)?V027_AID_DESC[id]:description(id);};
 const skill=v023Skill;v023Skill=function(key){const n=skill(key),bonus=M.modifiers(state.v054Chems).skills[key]||0;return Math.max(0,Math.min(100,n+bonus));};
 const capacity=v026Capacity;v026Capacity=function(){return Math.max(1,capacity()+M.modifiers(state.v054Chems).carry);};
 const damage=v020Damage;v020Damage=function(...a){return damage(...a)*M.modifiers(state.v054Chems).damage;};
 const derive=computeDerived;computeDerived=function(...a){const hp=state.player.hp,ap=state.player.ap,r=derive(...a),m=M.modifiers(state.v054Chems);state.player.maxHp=Math.max(1,state.player.maxHp+m.hp);state.player.maxAp=Math.max(1,state.player.maxAp+m.ap);state.player.hp=hp<=0?0:Math.max(0,Math.min(state.player.maxHp,hp));state.player.ap=Math.max(0,Math.min(state.player.maxAp,ap));return r;};
 const merchant=merchantState;merchantState=function(id){const ms=merchant(id),s=state.v054Chems,stock=Object.hasOwn(M.STOCKS,id)?M.STOCKS[id]:null;if(s&&stock&&!s.stocked[id]&&!V046.lab){for(const[item,count]of Object.entries(stock))if(!Object.hasOwn(ms.stock,item))ms.stock[item]=count;s.stocked[id]=true;}return ms;};
 const container=v026NewContainer;v026NewContainer=function(w,id,title,pos,items,options={}){const exists=!!state.v026?.containers?.[v026Key(w.id,id)];return container(w,id,title,pos,M.loot(id,items,options,exists),options);};
 function available(modes=['PLAYING','PIP','SALVAGE','FIELD']){return gameStarted&&world&&state.player.hp>0&&!zoneTransitioning&&!V046.lab&&!V046.busy&&!V047.pending&&modes.includes(mode);}
 function restore(owner,before){for(const key of Object.keys(owner))delete owner[key];Object.assign(owner,before);}
 function refresh(){if(mode==='TRADE'){try{renderTrade();}catch{}}else if(mode==='PIP')renderPipboy();else if(mode==='SALVAGE')v026Render();updateHUD();}
 function atomic(action,modes=['PLAYING','PIP','SALVAGE','FIELD']){
  if(!available(modes)||runtime.depth)return false;const owner=state,scene=world,before=clone(state),save=saveGame;let requested=false,args=[false];runtime.depth++;saveGame=function(...a){requested=true;args=a;return true;};
  try{const result=action();if(result?.then)throw Error('Cette opération doit se terminer sans attente.');if(state!==owner||world!==scene)throw Error('Le contexte a changé.');saveGame=save;if(result===false){restore(owner,before);return false;}if(!requested)throw Error('Aucune écriture complète demandée.');if(save(...args)===false)throw Error('Écriture de sauvegarde refusée.');runtime.commits++;runtime.error=null;return result;}
  catch(error){if(state===owner)restore(owner,before);runtime.rollbacks++;runtime.error=String(error.message||error);V027.message='Opération annulée : '+runtime.error+' Objets, soins et capsules conservés.';refresh();return false;}
  finally{saveGame=save;runtime.depth--;}
 }
 function use(id){if(!M.known(id)||!available()||v026Qty(id)<1)return false;const result=atomic(()=>{if(!v026Remove(id,1))return false;state.v054Chems=M.dose(state.v054Chems,id);runtime.quote=null;computeDerived();const m=M.modifiers(state.v054Chems);if(id==='jet')state.player.ap=Math.min(state.player.maxAp,state.player.ap+Math.max(0,m.ap));if(id==='buffout')state.player.hp=Math.min(state.player.maxHp,state.player.hp+Math.max(0,m.hp));saveGame(false);return true;});if(result){const row=M.summary(state.v054Chems).find(r=>r.id===id);V027.message=row.name+' · effet 120 s · puissance '+row.strength+' %'+(row.dependent?' · dépendance acquise':'');refresh();}return result;}
 const inventoryUse=useInventoryItem;useInventoryItem=function(id){return M.known(id)?use(id):inventoryUse(id);};
 const pipUse=v027ItemAction;v027ItemAction=function(kind,id){return kind==='use'&&M.known(id)?v027CanAct()&&use(id):pipUse(kind,id);};
 const bagUse=v026Use;v026Use=function(id){return M.known(id)?V026.open&&mode==='SALVAGE'&&use(id):bagUse(id);};
 const price=tradePrice;tradePrice=function(id,buy=true,vendor=tradeState?.id){const n=price(id,buy,vendor);return !M.known(id)||buy?n:Math.min(n,Math.max(1,price(id,true,vendor)-1));};
 const buying=buyTradeItem;buyTradeItem=function(id){return M.known(id)?atomic(()=>buying(id),['TRADE']):buying(id);};
 const selling=sellTradeItem;sellTradeItem=function(id){return M.known(id)?atomic(()=>selling(id),['TRADE']):selling(id);};
 const renderBarter=renderTrade;renderTrade=function(...a){const r=renderBarter(...a);if(!tradeState||typeof document==='undefined')return r;const list=$('tradeSellList');if(!list)return r;for(const[id,d]of Object.entries(M.DEFINITIONS)){if(v026Qty(id)<1||list.querySelector('[data-sell="'+id+'"]'))continue;const p=tradePrice(id,false),row=document.createElement('article');row.className='trade-row';row.innerHTML='<div><b>'+escapeHtml(d.name)+'</b><small>Disponible : '+v026Qty(id)+'</small></div><strong>'+p+' caps</strong><button data-sell="'+id+'"'+(merchantState(tradeState.id).caps<p?' disabled':'')+'>VENDRE</button>';row.querySelector('button').onclick=()=>sellTradeItem(id);list.appendChild(row);}return r;};
 const update=updateStatus;
 updateStatus=function(dt){const active=mode==='PLAYING'&&gameStarted&&!zoneTransitioning&&!V046.lab&&!V046.busy&&!V047.pending&&!V018.qaFreeze,before=M.modifiers(state.v054Chems),r=update(dt);if(active){state.v054Chems=M.advance(state.v054Chems,dt,true);const after=M.modifiers(state.v054Chems);if(before.hp!==after.hp||before.ap!==after.ap)computeDerived();}return r;};
 function nearDoctor(){if(!available(['PIP'])||!v027CanAct()||!v028NearMedic())return false;const npc=world.npcs.find(n=>n.id==='relay_cold:npc'&&n.alive!==false);return!!npc&&Math.hypot(npc.pos[0]-state.player.pos[0],npc.pos[2]-state.player.pos[2])<=4&&Math.abs(npc.pos[1]+playerEyeHeight()-state.player.pos[1])<=1&&!collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1])&&lineOfSight(state.player.pos,[npc.pos[0],npc.pos[1]+1.2,npc.pos[2]]);}
 function doctor(confirm=false){
  if(!nearDoctor()){runtime.quote=null;return v027Notify('Rejoignez Sofia, à l’Annexe des Veilleurs, hors danger et avec un accès libre.');}const cost=M.cost(state.v054Chems),signature=M.signature(state.v054Chems);if(!cost){runtime.quote=null;return v027Notify('Aucun état à traiter : consultation non facturée.');}
  if(!confirm){runtime.quote={owner:state,world,scene:V020.scene,signature,cost};renderPipboy();return true;}const q=runtime.quote;runtime.quote=null;if(!q||q.owner!==state||q.world!==world||q.scene!==V020.scene||q.signature!==signature||q.cost!==cost)return v027Notify('Le bilan a changé : demandez un nouveau devis.');if(state.player.caps<cost)return v027Notify('Capsules insuffisantes : aucun prélèvement partiel.');
  const result=atomic(()=>{if(!nearDoctor()||M.signature(state.v054Chems)!==signature||state.player.caps<cost)return false;state.player.caps-=cost;state.v054Chems=M.treat(state.v054Chems);computeDerived();v028Log('soin','Sofia : effets actifs, tolérance et dépendances traités · '+cost+' capsules. PV, radiations et blessures non soignés.');saveGame(false);return true;},['PIP']);if(result){V027.message='Dépendances et tolérance traitées. Les bonus chimiques actifs sont arrêtés ; les autres soins restent distincts.';refresh();}return result;
 }
 function panel(c){const rows=M.summary(state.v054Chems),m=M.modifiers(state.v054Chems),cost=M.cost(state.v054Chems),near=nearDoctor(),quote=runtime.quote&&runtime.quote.owner===state?runtime.quote:null;
  c.innerHTML='<div class="p27-long"><p class="p27-kicker">EFFETS ET DÉPENDANCES</p><h2>Chimie du Wasteland</h2><p>Quatre consommables de jeu : bonus 120 secondes actives. Les reprises rapprochées augmentent la tolérance et réduisent la puissance. La troisième prise rapprochée rend dépendant ; reprendre une dose masque le retrait sans guérir la dépendance.</p>'+rows.map(row=>'<section><h3>'+escapeHtml(row.name)+'</h3><p>'+({clear:'Aucun effet',active:'BONUS ACTIF',washout:'TOLÉRANCE EN RÉCUPÉRATION',withdrawal:'SEVRAGE ACTIF'})[row.phase]+' · '+row.uses+' prise(s) · tolérance '+row.tolerance+'/3'+(row.active?' · '+Math.ceil(row.active)+' s · puissance '+row.strength+' %':'')+(row.withdrawal?' · '+Math.ceil(row.withdrawal)+' s de retrait restantes':'')+(row.dependent?' · dépendance acquise':'')+'</p></section>').join('')+'<p>Modifications actuelles : PVmax '+m.hp+' · PAmax '+m.ap+' · charge '+m.carry+' kg · aptitudes cognitives '+m.skills.science+' · dégâts ×'+m.damage.toFixed(2)+'.</p><p>Sans reprise, le retrait dure 300 secondes actives, puis la famille récupère. Les menus, chargements et le temps hors partie ne font pas avancer ces compteurs.</p><div class="p27-actions">'+v027Button('Ouvrir les consommables','jump','inventory:aid')+'</div><h2>Poste de Sofia</h2><p>'+ (near?'Sofia est présente, proche et accessible.':'Rejoignez physiquement Sofia à l’Annexe des Veilleurs.')+'</p><p>Le traitement arrête tous les bonus chimiques et remet tolérance/dépendance à zéro. Il ne soigne ni PV, radiations, infection ou traumatismes.</p>'+v027Button(cost?'Demander un devis · '+cost+' capsules':'Aucun traitement nécessaire','c54:quote','',!near||!cost)+(quote?'<section><b>'+quote.cost+' capsules · bilan local</b><p>Les bonus actifs seront arrêtés. Paiement unique, uniquement tant que Sofia et le bilan restent accessibles.</p>'+v027Button('Confirmer le traitement','c54:confirm','',!near)+v027Button('Annuler','c54:cancel')+'</section>':'')+'</div>';
 }
 const status=v027Status;v027Status=function(c){if(V027.sub==='chemistry')return panel(c);const r=status(c);if(V027.sub==='health'){const rows=M.summary(state.v054Chems).filter(row=>row.phase!=='clear');c.innerHTML+='<section class="p27-long"><h3>Consommables et dépendances</h3>'+rows.map(row=>'<p>'+escapeHtml(row.name)+' · '+({active:'bonus actif',withdrawal:'sevrage actif',washout:'tolérance résiduelle'})[row.phase]+(row.dependent?' · dépendance':'')+'</p>').join('')+v027Button('Bilan des dépendances','jump','status:chemistry')+'</section>';}return r;};
 const dispatch=v027Dispatch;v027Dispatch=function(action,arg=''){if(!action.startsWith('c54:'))return dispatch(action,arg);if(!v027CanAct())return false;if(action==='c54:quote')return doctor(false);if(action==='c54:confirm')return doctor(true);if(action==='c54:cancel'){runtime.quote=null;renderPipboy();return true;}return false;};
 const sofia=v028Sofia;v028Sofia=function(...a){const result=sofia(...a),d=dialogueState;if(result&&d){openDialogue(d.speaker,d.line,[...d.choices,{id:'c54-sofia',text:'Parler des consommables, de la tolérance et du sevrage.',onChoose:()=>{debugDismissDialogue();v027Open('status','chemistry');}}]);}return result;};
 const close=closePipboy;closePipboy=function(...a){runtime.quote=null;return close(...a);};
 const load=loadZone;loadZone=function(...a){runtime.quote=null;return load(...a);};
 function info(){return{schema:1,state:clone(state.v054Chems),families:M.summary(state.v054Chems),modifiers:M.modifiers(state.v054Chems),skills:Object.fromEntries(['science','repair','speech'].map(k=>[k,v023Skill(k)])),capacity:v026Capacity(),doctor:{near:nearDoctor(),cost:M.cost(state.v054Chems),quote:runtime.quote?{cost:runtime.quote.cost,scene:runtime.quote.scene}:null,npc:'relay_cold:npc'},error:runtime.error,commits:runtime.commits,rollbacks:runtime.rollbacks,provenance:'Fictional deterministic game mechanics; no real medical simulation'};}
 globalThis.v054ChemsAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v054ChemsInfo:info,v054ChemsCatalog:()=>clone({definitions:M.DEFINITIONS,stocks:M.STOCKS,duration:M.DURATION,withdrawal:M.WITHDRAWAL}),v054ChemsUse:use,v054ChemsDoctor:doctor});};
}
