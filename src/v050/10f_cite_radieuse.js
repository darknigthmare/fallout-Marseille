/* Cité Radieuse — original, compact fictional interior; not a surveyed floor plan.
 * Geographic reference: UNESCO property 1321rev-009, N43 15 40.93 E5 23 46.24.
 * No changes to IGN geometry, regional ratification, pharmacy or postal records.
 */
const MistralRadieuse=(()=>{
 'use strict';
 const copy=v=>JSON.parse(JSON.stringify(v)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const SITE={id:'v063-cite-radieuse',macro:'geo_marseille',lat:43+15/60+40.93/3600,lon:5+23/60+46.24/3600,kind:'interior',name:'Cité Radieuse · Les parties communes',description:'Une copropriété habitée, ses galeries et sa terrasse. Les travaux attendent un vote que SYNDIC-PRIME ne sait plus compter.',anchor:'Boulevard Michelet',tier:1,faction:'ligue',factionLabel:'Copropriété Radieuse',safe:true,visitable:true,interior:'radieuse',theme:'urban',unique:true,discoverRadius:190,activationRadius:700,enemyRadius:0,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],eliteType:'robot',bossType:'robot',rewardCaps:0,rewardXP:0,respawnHours:0,icon:'home',provenance:{kind:'authored-fiction',pointSource:'https://whc.unesco.org/fr/list/1321/cartes/',reference:'1321rev-009',interior:'Original compressed fiction; no surveyed geometry'}};
 const PEOPLE=[
  {id:'josiane',name:'Josiane Roux',role:'Présidente de séance',pos:[-7,0,22],text:'Le toit est commun. Les fuites aussi. Le registre fait voter des propriétaires morts, puis reproche aux vivants de ne pas atteindre le quorum.'},
  {id:'karim',name:'Karim Bellon',role:'Habitants du rez-de-chaussée',pos:[10,0,20],text:'Je ne monte jamais dans la galerie. Mais la colonne d’eau qui l’alimente traverse ma cuisine. Qu’on m’explique les charges avant de me les réclamer.'},
  {id:'lucie',name:'Lucie Armand',role:'Atelier des communs',pos:[-15,0,0],text:'La pompe n’est pas une métaphore politique. Il faut une pièce, des mains et quelqu’un pour vérifier le travail. Le vote ne tournera pas les boulons.'},
  {id:'nadia',name:'Nadia Ferrat',role:'Rue intérieure',pos:[9,3.2,-3],text:'Les étages hauts paient l’eau qui ne monte plus. Je défendrai une contribution partagée, pas un compteur posé sur chaque porte.'},
  {id:'salome',name:'Salomé Veyre',role:'Habitants du toit',pos:[10,6.4,-28],text:'Nous entretenons les cuves depuis trois générations. Dans les plans, nous sommes une toiture. Une toiture n’a pas de voix, mais elle reçoit les factures.'}
 ];
 const EVIDENCE={registre:{name:'Le registre des absents',pos:[-16,0,22],text:'Le registre inclut des lots sans occupants et ignore les abris du toit. Une note de maintenance atteste pourtant leur présence. Ne détruisez aucune des deux listes.'},pompe:{name:'La colonne de retour',pos:[-18,0,-8],text:'La dérivation est déboîtée. L’eau fuit dans le local au lieu de rejoindre la colonne commune. Une réparation locale suffit ; le réacteur n’est pas en fusion.'},reseau:{name:'Le tableau des parties communes',pos:[18,3.2,-7],text:'Le circuit des lampes partage un contacteur avec le volet de la réserve. SYNDIC-PRIME a suspendu le courant jusqu’à paiement des charges.'},toit:{name:'Le toit habité',pos:[-8,6.4,-28],text:'Les bâches sont devenues poreuses. Les jardinières et la réserve restent réparables. Un plan annexe compte cinq familles qu’aucun bulletin de vote ne reconnaît.'}};
 const OPTIONS={charges:{solidarite:'Contribution solidaire',usage:'Répartition par usage',avance:'Avance personnelle · 45 capsules'},representation:{occupants:'Tous les habitants, y compris le toit',lots:'Les quatre délégations des lots inscrits'},controle:{audit:'Vérification par les habitants',syndic:'Mandat à SYNDIC-PRIME'}};
 const COSTS={solidarite:{pompe:{scrap:2},reseau:{circuitry:1},toit:{cloth:2}},usage:{pompe:{scrap:3,cloth:1},reseau:{circuitry:1,scrap:1},toit:{cloth:3}},avance:{pompe:{scrap:1},reseau:{circuitry:1},toit:{cloth:1}}};
 const WORKS=['pompe','reseau','toit'];
 function fresh(){return{schema:1,accepted:false,evidence:[],heard:[],clauses:{charges:null,representation:null,controle:null},vote:null,attempts:0,works:[],finished:false,water:0,journal:[]};}
 function tally(l){
  const c=l.clauses||{};const details=PEOPLE.map(p=>{const present=l.heard.includes(p.id),eligible=p.id!=='salome'||c.representation==='occupants';let yes=false;
   if(p.id==='josiane'||p.id==='lucie')yes=c.controle==='audit'||c.charges==='avance';
   if(p.id==='karim')yes=c.charges==='usage'||c.charges==='avance';
   if(p.id==='nadia')yes=c.charges==='solidarite'||c.charges==='avance';
   if(p.id==='salome')yes=c.representation==='occupants'&&c.charges!=='usage';
   return{id:p.id,name:p.name,present,eligible,vote:!eligible?'excluded':!present?'absent':yes?'for':'against'};});
  const present=details.filter(d=>d.present&&d.eligible).length,yes=details.filter(d=>d.vote==='for').length;
  return{quorum:4,present,yes,no:details.filter(d=>d.vote==='against').length,passed:present>=4&&yes>=3,details};
 }
 function migrate(raw){
  if(raw&&Number.isInteger(raw.schema)&&raw.schema>1)throw Error('Registre de copropriété plus récent que ce programme.');
  const l=fresh();if(!raw||typeof raw!=='object'||Array.isArray(raw))return l;
  l.accepted=raw.accepted===true;
  const ids=PEOPLE.map(p=>p.id),keys=Object.keys(EVIDENCE);
  l.evidence=Array.isArray(raw.evidence)?keys.filter(k=>raw.evidence.includes(k)):[];
  l.heard=Array.isArray(raw.heard)?ids.filter(k=>raw.heard.includes(k)):[];
  for(const k of Object.keys(OPTIONS))l.clauses[k]=own(OPTIONS[k],raw.clauses?.[k])?raw.clauses[k]:null;
  l.attempts=Number.isInteger(raw.attempts)?Math.max(0,Math.min(1000,raw.attempts)):0;
  // A partial/corrupt register cannot invent a vote, a repair or renewable water.
  const complete=l.accepted&&keys.every(k=>l.evidence.includes(k))&&Object.values(l.clauses).every(Boolean);
  if(raw.vote?.passed===true&&complete){const t=tally(l);if(t.passed)l.vote=t;}
  if(l.vote){l.works=Array.isArray(raw.works)?WORKS.filter(k=>raw.works.includes(k)):[];l.finished=raw.finished===true&&WORKS.every(k=>l.works.includes(k));}
  l.water=l.finished&&Number.isInteger(raw.water)?Math.max(0,Math.min(3,raw.water)):0;
  l.journal=Array.isArray(raw.journal)?raw.journal.filter(e=>e&&['accept','inspect','hear','clause','vote','repair','finish','water'].includes(e.type)).slice(-48).map(e=>({type:e.type,id:typeof e.id==='string'?e.id.slice(0,32):null,at:Number.isFinite(e.at)&&e.at>=0?e.at:0})):[];
  return l;
 }
 function stage(raw){const l=migrate(raw);return l.finished?'done':l.vote?(l.works.length===3?'report':'works'):l.accepted?'inquiry':'new';}
 function briefing(raw){const l=migrate(raw);return l.finished?'Travaux réceptionnés. La pompe, l’éclairage et la réserve commune fonctionnent dans cette instance.':l.vote?`Motion adoptée : ${l.works.length}/3 travaux effectués. Le vote ne remplace pas la réparation sur place.`:l.accepted?`${l.evidence.length}/4 constats et ${l.heard.length}/5 témoignages. Préparez une motion, puis revenez au pupitre de l’assemblée.`:'Josiane attend une personne capable de lire les comptes et de regarder les tuyaux.';}
 function apply(snapshot,a={},ctx={}){
  if(ctx.blocked)throw Error(String(ctx.blocked));if(!ctx.local)throw Error('Rejoignez la Cité Radieuse.');
  if(!snapshot?.player||!Number.isFinite(snapshot.player.hp)||snapshot.player.hp<=0)throw Error('Une partie active est nécessaire.');
  const count=n=>Number.isInteger(n)&&n>=0&&n<=999999;
  if(!count(snapshot.player.caps))throw Error('Compte de capsules invalide.');
  for(const n of Object.values(snapshot.inventory||{}))if(!count(n))throw Error('Inventaire invalide.');
  const out=copy(snapshot),l=migrate(out.v063Radieuse);out.inventory??={};
  const at=id=>{if(ctx.point!==id||!ctx.near)throw Error('Approchez-vous du bon interlocuteur ou équipement.');};
  const spend=cost=>{for(const[id,n]of Object.entries(cost))if((out.inventory[id]||0)<n)throw Error('Fournitures insuffisantes.');for(const[id,n]of Object.entries(cost))out.inventory[id]-=n;};
  if(a.type==='accept'){at('josiane');if(l.accepted)throw Error('La demande est déjà acceptée.');l.accepted=true;}
  else if(a.type==='inspect'){at(a.id);if(!own(EVIDENCE,a.id))throw Error('Constat inconnu.');if(l.evidence.includes(a.id))throw Error('Constat déjà conservé.');l.evidence.push(a.id);}
  else if(a.type==='hear'){at(a.id);if(l.vote)throw Error('Le scrutin est clos ; son procès-verbal reste inchangé.');if(!PEOPLE.some(p=>p.id===a.id))throw Error('Habitant inconnu.');if(l.heard.includes(a.id))throw Error('Témoignage déjà conservé.');l.heard.push(a.id);}
  else if(a.type==='clause'){
   at('assemblee');if(!l.accepted||l.vote)throw Error('Motion non ouverte ou déjà adoptée.');if(!own(OPTIONS,a.id)||!own(OPTIONS[a.id],a.choice))throw Error('Clause inconnue.');l.clauses[a.id]=a.choice;
  }else if(a.type==='vote'){
   at('assemblee');if(!l.accepted||l.vote)throw Error('Vote non ouvert ou déjà adopté.');
   if(!Object.keys(EVIDENCE).every(k=>l.evidence.includes(k))||!Object.values(l.clauses).every(Boolean))throw Error('Les quatre constats et les trois clauses sont nécessaires.');
   const result=tally(l);l.attempts=Math.min(1000,l.attempts+1);
   if(result.passed){if(l.clauses.charges==='avance'){if(out.player.caps<45)throw Error('45 capsules requises pour cette avance.');out.player.caps-=45;}l.vote=result;}
  }else if(a.type==='repair'){
   at(a.id);if(!l.vote||!WORKS.includes(a.id)||l.works.includes(a.id))throw Error('Travail non voté, inconnu ou déjà effectué.');spend(COSTS[l.clauses.charges][a.id]);l.works.push(a.id);
  }else if(a.type==='finish'){
   at('josiane');if(l.finished||!WORKS.every(k=>l.works.includes(k)))throw Error('Travaux incomplets ou déjà réceptionnés.');
   if(out.player.caps>999934)throw Error('Compte de capsules plein.');out.player.caps+=65;l.finished=true;l.water=3;
  }else if(a.type==='water'){
   at('pompe');if(!l.finished||l.water<1)throw Error('Réserve commune vide ou non réceptionnée.');const n=out.inventory.water||0;if(n>999997)throw Error('Inventaire plein.');out.inventory.water=n+2;l.water--;
  }else throw Error('Action de copropriété inconnue.');
  l.journal.push({type:a.type,id:a.id||null,at:Number.isFinite(out.playTime)?Math.max(0,out.playTime):0});l.journal=l.journal.slice(-48);out.v063Radieuse=l;return out;
 }
 return{SITE:copy(SITE),PEOPLE:copy(PEOPLE),EVIDENCE:copy(EVIDENCE),OPTIONS:copy(OPTIONS),COSTS:copy(COSTS),WORKS:WORKS.slice(),fresh,migrate,tally,stage,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralRadieuse;

if(typeof baseState==='function'&&typeof V042_CATALOG!=='undefined'){
 const M=MistralRadieuse,copy=v=>JSON.parse(JSON.stringify(v)),POINTS={...Object.fromEntries(M.PEOPLE.map(p=>[p.id,p.pos])),...Object.fromEntries(Object.entries(M.EVIDENCE).map(([id,e])=>[id,e.pos])),assemblee:[0,0,14],syndic:[17,0,8],exit:[0,0,28]};
 if(!V042_SITE_BY_ID[M.SITE.id]){const site=copy(M.SITE);V042_CATALOG.push(site);V042_SITE_BY_ID[site.id]=site;V042_SITES_BY_MACRO[site.macro].push(site);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[site.macro]++;}
 const oldBase=baseState;baseState=function(...args){const s=oldBase(...args);s.v063Radieuse=M.fresh();return s;};
 const oldMigration=migrateState;migrateState=function(raw={}){const s=oldMigration(raw);s.v063Radieuse=M.migrate(raw?.v063Radieuse);return s;};
 state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const runtime={busy:false,error:null};
 const local=()=>!!world?.v063Radieuse&&state.v042?.activeInterior===M.SITE.id;
 function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Le banc géographique ne modifie pas la campagne.':zoneTransitioning||V046.busy||V047.pending?'Attendez la fin du chargement.':typeof onGround==='boolean'&&!onGround?'Rejoignez un sol stable.':inCombat?'Terminez le combat.':null;}
 function near(id){const p=POINTS[id];if(!local()||!p)return false;const n=world.npcs.find(n=>n.id==='r63:'+id);if(M.PEOPLE.some(p=>p.id===id)&&(!n||!n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.6&&Math.abs(state.player.pos[1]-p[1]-1.4)<2&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.65]);}
 function notice(s){V027.message=s;toast(s,'bad');return false;}
 function restore(owner,snapshot){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,snapshot);}
 function action(type,id,choice){
  if(runtime.busy)return false;const owner=state,scene=world,before=copy(owner);let next;
  const point=['vote','clause'].includes(type)?'assemblee':['accept','finish'].includes(type)?'josiane':type==='water'?'pompe':id;
  try{next=M.apply(owner,{type,id,choice},{blocked:blocked(),local:local(),near:near(point),point});}catch(e){return notice(e.message);}
  runtime.busy=true;
  try{owner.v063Radieuse=next.v063Radieuse;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde de copropriété refusée.');}
  catch(e){restore(owner,before);return notice(e.message+' Échange annulé.');}finally{runtime.busy=false;}
  try{visuals(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='vote'?(owner.v063Radieuse.vote?'Motion adoptée. Les travaux restent à faire.':'Motion rejetée. Vous pouvez modifier les clauses.'):type==='finish'?'Travaux réceptionnés · 65 capsules.':'Registre de copropriété sauvegardé.','good');}catch(e){runtime.error=e.message;}
  return true;
 }
 const costs=items=>Object.entries(items).map(([id,n])=>n+' '+itemLabel(id)).join(' + ');
 function conversation(id){
  if(blocked()||!near(id))return notice(blocked()||'Rejoignez cet interlocuteur.');const p=M.PEOPLE.find(p=>p.id===id),owner=state,scene=world,l=state.v063Radieuse,choices=[],guard=fn=>()=>state===owner&&world===scene&&fn();
  if(p){
   if(!l.vote&&!l.heard.includes(id))choices.push({text:'Consigner son témoignage.',onChoose:guard(()=>{action('hear',id);conversation(id);})});
   if(id==='josiane'&&!l.accepted)choices.push({text:'Accepter « Assemblée générale extraordinaire ».',onChoose:guard(()=>{action('accept',id);conversation(id);})});
   if(id==='josiane'&&!l.finished&&l.works.length===3)choices.push({text:'Faire réceptionner les trois travaux · 65 capsules.',onChoose:guard(()=>{action('finish',id);conversation(id);})});
  }
  choices.push({text:'Revenir.',onChoose:closeDialogue});
  openDialogue(speaker(p?.name||'SYNDIC-PRIME',p?.role||'GESTION DES PARTIES COMMUNES',p?'CR':'SP'),(p?p.text:'« Les absents n’ont pas payé leurs charges. Les présents n’ont pas de lots. Le règlement ne prévoit pas que ces deux faits puissent se produire simultanément. »')+'\n\n'+M.briefing(l),choices);return true;
 }
 function equipment(id){
  if(blocked()||!near(id))return notice(blocked()||'Approchez-vous de cet équipement.');const owner=state,scene=world,l=state.v063Radieuse,e=M.EVIDENCE[id],choices=[],guard=fn=>()=>state===owner&&world===scene&&fn();
  if(e&&!l.evidence.includes(id))choices.push({text:'Examiner et conserver le constat.',onChoose:guard(()=>{action('inspect',id);equipment(id);})});
  if(l.vote&&M.WORKS.includes(id)&&!l.works.includes(id))choices.push({text:'Réaliser le travail voté · '+costs(M.COSTS[l.clauses.charges][id]),onChoose:guard(()=>{action('repair',id);equipment(id);})});
  if(id==='pompe'&&l.finished&&l.water>0)choices.push({text:'Retirer 2 eaux de la réserve commune · '+l.water+' retraits restants.',onChoose:guard(()=>{action('water',id);equipment(id);})});
  choices.push({text:'Revenir.',onChoose:closeDialogue});
  openDialogue(speaker(e?.name||'Équipement','CITÉ RADIEUSE','CR'),e.text+'\n\n'+(l.works.includes(id)?'Réparation effectuée et sauvegardée.':l.vote?'L’assemblée autorise les travaux ; apportez les fournitures indiquées.':'Les constats sont accessibles avant le vote. Les travaux attendent un accord.'),choices);return true;
 }
 function assembly(){
  if(blocked()||!near('assemblee'))return notice(blocked()||'Rejoignez le pupitre de l’assemblée.');const owner=state,scene=world,l=state.v063Radieuse,choices=[],guard=fn=>()=>state===owner&&world===scene&&fn();
  if(l.accepted&&!l.vote){for(const[k,opts]of Object.entries(M.OPTIONS))for(const[id,label]of Object.entries(opts))choices.push({text:(l.clauses[k]===id?'✓ ':'')+label,onChoose:guard(()=>{action('clause',k,id);assembly();})});choices.push({text:'Soumettre la motion au vote.',onChoose:guard(()=>{action('vote');assembly();})});}
  choices.push({text:'Revenir.',onChoose:closeDialogue});const vote=l.vote||M.tally(l);
  openDialogue(speaker('Assemblée générale extraordinaire','CINQ DÉLÉGATIONS · QUORUM QUATRE','AG'),(l.vote?'Motion adoptée et exclusive.':'Les constats précèdent le vote. Un rejet ne ferme pas les négociations.')+'\n\n'+vote.details.map(d=>d.name+' : '+({for:'pour',against:'contre',absent:'témoignage manquant',excluded:'exclue du scrutin'}[d.vote])).join('\n')+`\n\nPrésents : ${vote.present}/4 nécessaires · Pour : ${vote.yes}/3 nécessaires.`+(l.clauses.charges?'\nFournitures à apporter après le vote : '+M.WORKS.map(k=>M.EVIDENCE[k].name+' — '+costs(M.COSTS[l.clauses.charges][k])).join(' ; '):'')+'\nLes règles de cette assemblée sont fictives, propres à la copropriété post-atomique.',choices);return true;
 }
 function visuals(w){if(!w?.v063Radieuse)return;const l=state.v063Radieuse;for(const d of w.staticDraws){if(d.r63Show)d.hidden=!l.works.includes(d.r63Show);if(d.r63Hide)d.hidden=l.works.includes(d.r63Hide);if(d.r63Light){d.color=l.works.includes('reseau')?[.92,.79,.42]:[.22,.24,.22];d.emissive=l.works.includes('reseau')?.65:0;}}for(const c of w.colliders)if(c.r63Gate)c.disabled=l.works.includes('reseau');w.hazards=w.hazards.filter(h=>h.id!=='r63-leak');if(!l.works.includes('pompe'))addHazard(w,'r63-leak',-20,-10,1.6,{damage:1,label:'Fuite du local commun',kind:'hazard'});}
 function build(){
  const w=createWorld(V042_INSTANCE_ZONE,'Cité Radieuse — les parties communes','INSTANCE SCÉNARISÉE · TROIS NIVEAUX',{skyTop:[68,97,119],skyBottom:[167,153,116],fog:[.44,.48,.42],wind:.15,daylight:.65,indoor:false});
  w.v063Radieuse=true;w.bounds=[-26,26,-35,31];w.spawn=[0,1.65,25];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE.id;
  const concrete=[.49,.48,.42],dark=[.19,.24,.24],cream=[.70,.65,.53];
  const box=(p,s,c=concrete,solid=false)=>{const d=addBox(w,p,s,c);if(solid)addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});return d;};
  const slab=(x,z,sx,sz,h)=>{box([x,h-.18,z],[sx,.36,sz],concrete);addFloorZone(w,x,z,sx,sz,h,{priority:1});if(h>0)addCollider(w,x,z,sx,sz,{minY:h-.36,maxY:h-.10});};
  const sign=(x,y,z,text,size=.075)=>{if(typeof v021Sign==='function')v021Sign(w,x,y,z,text,size);};
  slab(0,-2,52,66,0);
  // Upper street and terrace: distinct slabs; safe, open stairs always available.
  slab(0,-5,48,30,3.2);slab(0,-28,48,12,6.4);
  v021Stairs(w,18,16,12,3.8,3.2); // z=22 -> 10, feet 0 -> 3.2.
  // Second stair has its own base height; only lower supporting slab under it.
  const temp=createWorld('r63-stairs','Escalier haut','');v021Stairs(temp,-18,-16,12,3.8,3.2);
  for(const d of temp.staticDraws){d.pos[1]+=3.2;w.staticDraws.push(d);}for(const c of temp.colliders){c.minY+=3.2;c.maxY+=3.2;w.colliders.push(c);}for(const f of temp.floorZones){f.startHeight+=3.2;f.endHeight+=3.2;w.floorZones.push(f);}
  // Envelope, pilotis, colour-coded door bays and transparent sightlines.
  box([-25,4,-2],[.6,8,66],concrete,true);box([25,4,-2],[.6,8,66],concrete,true);box([0,4,-34],[50,8,.6],concrete,true);
  box([-14,1.7,30],[22,3.4,.45],dark,true);box([14,1.7,30],[22,3.4,.45],dark,true);
  for(const x of[-21,-9,9,21])for(const z of[-16,8])box([x,1.5,z],[.75,3,.75],cream,true);
  // Ground workshop remains reachable under the gallery; avoid floor-level rays.
  box([-12,1.3,-7],[.3,2.6,8],concrete,true);box([-12,1.3,5],[.3,2.6,4],concrete,true);box([-18,1.3,7],[12,2.6,.3],concrete,true);
  for(const x of[-8,0,8,16]){const col=[[.62,.29,.20],[.25,.43,.53],[.73,.57,.23],[.35,.46,.30]][(x+8)/8];box([x,4.5,-19.7],[5.5,2.6,.28],col,true);sign(x,5.5,-19.48,'RUE '+(x+17),.055);}
  for(const [x,z]of[[-23,-10],[23,-10],[-10,8],[8,8]]){const d=box([x,2.8,z],[1.4,.12,.35],[.22,.24,.22]);d.r63Light=true;}
  // Low railings leave the two stair openings open, no invisible fall-blockers.
  for(const [x,z,sx,sz,y]of[[0,10,30,.22,4.0],[23.5,-5,.22,28,4],[-23.5,-5,.22,28,4],[4,-22,36,.22,7.2],[-23.5,-28,.22,12,7.2],[23.5,-28,.22,12,7.2]])box([x,y,z],[sx,1.3,sz],dark,true);
  // Common reserve, opened by the actual contactor repair.
  box([5,4.45,-12],[.3,2.5,6],cream,true);box([13,4.45,-12],[.3,2.5,6],cream,true);box([9,4.45,-15],[8,2.5,.3],cream,true);
  const shutter=box([9,4.45,-9],[8,2.5,.28],dark);shutter.r63Hide='reseau';const gate=addCollider(w,9,-9,8,.28,{minY:3.2,maxY:5.7});gate.r63Gate=true;
  box([8,3.65,-13],[1,.9,1],[.48,.34,.18],true);box([11,3.65,-13],[1,.9,1],[.48,.34,.18],true);
  // Equipment and evidence interaction points sit in front of their colliders.
  for(const[id,e]of Object.entries(M.EVIDENCE)){const[x,y,z]=e.pos;box([x,y+.52,z],[1.1,1.04,.75],dark,true);box([x,y+1.15,z],[1.16,.18,.82],cream);sign(x,y+1.55,z+.06,id.toUpperCase(),.05);addInteract(w,'r63:'+id,[x,y+1.25,z+.65],'Examiner · '+e.name,()=>equipment(id),{radius:3.5,kind:'quest',priority:5,condition:()=>local()&&near(id)});}
  const leak=box([-20,.04,-10],[3,.06,3],[.24,.44,.37]);leak.r63Hide='pompe';const flow=box([-19,.7,-9],[.15,.15,1.4],[.29,.65,.57]);flow.r63Show='pompe';
  for(const x of[-12,-6,0,6]){box([x,6.7,-32],[3,.6,1.8],[.34,.28,.20],true);const plant=box([x,7.2,-32],[2.5,.7,1.3],[.32,.48,.23]);plant.r63Show='toit';const tarp=box([x,7.1,-32],[3.1,.1,2],[.39,.34,.23]);tarp.r63Hide='toit';}
  // Council desk and the terminal are physical, not global remote actions.
  box([0,.45,14],[3.8,.9,1.1],dark,true);sign(0,1.5,14,'ASSEMBLEE',.06);addInteract(w,'r63:assemblee',[0,1.25,14.65],'Ouvrir la séance de copropriété',assembly,{radius:3.5,kind:'terminal',priority:5,condition:()=>local()&&near('assemblee')});
  box([17,1,8],[1.6,2,.8],dark,true);box([17,1.5,8.45],[1.2,.7,.05],[.45,.68,.34]);addInteract(w,'r63:syndic',[17,1.3,8.65],'Interroger SYNDIC-PRIME',()=>conversation('syndic'),{radius:3.5,kind:'terminal',priority:4});
  for(const p of M.PEOPLE)addHumanNPC(w,'r63:'+p.id,p.name,p.role,p.pos,p.id==='salome'?[.40,.52,.31]:[.34,.42,.50],{dialogue:'r63:'+p.id,yaw:Math.PI});
  sign(0,2.5,29,'SORTIE / MICHELET',.07);sign(-6,2.6,8,'ATELIER / POMPE',.08);sign(18,3.2,10,'RUE INTERIEURE',.06);sign(-18,6.8,-22,'TERRASSE',.06);
  addInteract(w,'r63:exit',[0,1.25,28],'Retourner au territoire',()=>{if(blocked()||!near('exit'))return false;return v042ExitInstance();},{radius:3.5,kind:'door',priority:4});
  w.subzones=[{id:'r63-hall',name:'Hall et assemblée',pos:[0,0,20]},{id:'r63-atelier',name:'Atelier commun',pos:[-18,0,0]},{id:'r63-rue',name:'Rue intérieure',pos:[0,3.2,-4]},{id:'r63-toit',name:'Toit habité',pos:[0,6.4,-28]}];
  w.levelRoutes=[{id:'r63-main',points:[[0,0,25],[18,0,22],[18,3.2,10],[0,3.2,0],[-18,3.2,-10],[-18,6.4,-22],[10,6.4,-28]]}];visuals(w);return w;
 }
 const oldBuild=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE.id?build():oldBuild(...arguments);};
 const oldGround=groundHeightAt;groundHeightAt=function(x,z,feet=0){if(!world?.v063Radieuse)return oldGround(...arguments);const h=world.floorZones.filter(f=>x>=f.minX&&x<=f.maxX&&z>=f.minZ&&z<=f.maxZ).map(f=>floorZoneHeight(f,x,z)).filter(h=>h<=feet+.60);return h.length?Math.max(...h):0;};
 // Present-tense date only; Radio Mistral's 2291 founding remains historical lore.
 const oldSpeaker=speaker;speaker=function(name,role,initials){return oldSpeaker(name,role==='LONGCHAMP · 2291'?'LONGCHAMP · 2297':role,initials);};
 const oldTalk=talkToNPC;talkToNPC=function(id){return typeof id==='string'&&id.startsWith('r63:')?conversation(id.slice(4)):oldTalk(...arguments);};
 // Only this authored site uses the dedicated objectives; never auto-award generic clear loot.
 const oldClaim=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE.id?false:oldClaim(...arguments);};
 const oldLayer=v042LayerPanel;v042LayerPanel=function(c){const result=oldLayer(...arguments);const p=c.querySelector('.v42-layer>p');if(p)p.textContent=p.textContent.replace('248 implantations',V042_LAYER_META.siteCount+' implantations');return result;};
 V027_SUBS.data.radieuse='CITÉ RADIEUSE';
 const oldData=v027Data;v027Data=function(c){if(V027.sub!=='radieuse')return oldData(...arguments);const esc=v027Escape,l=state.v063Radieuse,t=l.vote||M.tally(l);c.innerHTML='<div class="p27-long"><p class="p27-kicker">LES PARTIES COMMUNES</p><h2>Assemblée générale extraordinaire</h2><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre la Cité Radieuse','r63:track')+'<h3>Constats</h3>'+Object.entries(M.EVIDENCE).map(([id,e])=>'<p>'+ (l.evidence.includes(id)?'✓ ':'— ')+esc(e.name)+'</p>').join('')+'<h3>Délégations</h3>'+t.details.map(d=>'<p>'+esc(d.name)+' · '+esc(d.vote==='excluded'?'Exclue du scrutin':!d.present?'À rencontrer':l.vote?(d.vote==='for'?'Pour':'Contre'):'Témoignage recueilli')+'</p>').join('')+'<h3>Travaux sur place</h3>'+M.WORKS.map(k=>'<p>'+(l.works.includes(k)?'✓ ':'— ')+esc(M.EVIDENCE[k].name)+'</p>').join('')+'<p>Retraits de deux eaux restants : '+l.water+'. Les votes et les réparations se font sur place.</p><p>Intérieur scénarisé compact à trois niveaux, pas une restitution des appartements réels. La ratification régionale reste inchangée.</p></div>';};
 function track(){if(blocked())return notice(blocked());const owner=state,scene=world,before=copy(owner);owner.v042.tracked=M.SITE.id;try{if(state!==owner||world!==scene||saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Repère non sauvegardé.');}updateQuestUI(true);return true;}
 const oldDispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='r63:track'?v027CanAct()&&track():oldDispatch(...arguments);};
 function nextPoint(){const l=state.v063Radieuse;if(!l.accepted)return'josiane';const e=Object.keys(M.EVIDENCE).find(k=>!l.evidence.includes(k));if(!l.vote&&e)return e;const p=M.PEOPLE.find(p=>!l.heard.includes(p.id));if(!l.vote&&p)return p.id;if(!l.vote)return'assemblee';return M.WORKS.find(k=>!l.works.includes(k))||(l.finished?'pompe':'josiane');}
 const oldMarker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return oldMarker(...arguments);const id=nextPoint(),p=POINTS[id];return{zone:world.id,pos:[p[0],p[1]+1.25,p[2]],label:M.EVIDENCE[id]?.name||M.PEOPLE.find(p=>p.id===id)?.name||'Assemblée de copropriété'};};
 const oldQuestUI=updateQuestUI;updateQuestUI=function(flash=false){if(!local())return oldQuestUI(...arguments);const title='LES PARTIES COMMUNES',text=M.briefing(state.v063Radieuse);$('questTitle').textContent=title;$('questObjective').textContent=text;if(flash){const f=$('questFlash');f.querySelector('strong').textContent=title;f.querySelector('p').textContent=text;f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
 const oldRows=v027QuestRows;v027QuestRows=function(){const l=state.v063Radieuse;return oldRows(...arguments).concat(l.accepted?[{id:'r63:quest',name:'ASSEMBLÉE GÉNÉRALE EXTRAORDINAIRE',stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:[['Quatre constats',l.evidence.length===4],['Motion adoptée',!!l.vote],['Trois travaux réalisés',l.works.length===3],['Travaux réceptionnés',l.finished]],source:'Copropriété Radieuse',badge:l.finished?'✓':'',hint:'Josiane Roux · boulevard Michelet'}]:[]);};
 const oldTrack=v027Track;v027Track=function(id){return id==='r63:quest'?track():oldTrack(...arguments);};
 V027_STATIONS.radieuse={name:'Les parties communes — procès-verbal',freq:'93.6',hint:'Les travaux ne se votent pas tout seuls',available:()=>state.v063Radieuse.accepted,text:()=>M.briefing(state.v063Radieuse)};
 const oldAfter=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){oldAfter?.();for(const selector of ['#menuScreen .eyebrow','#locationCard small','#v35pTitle small'])for(const el of document.querySelectorAll(selector))if(el.textContent.includes('2291'))el.textContent=el.textContent.replace('2291','2297');Object.assign(window.__MISTRAL_DEBUG,{v063RadieuseInfo:()=>({ledger:copy(state.v063Radieuse),local:local(),tally:M.tally(state.v063Radieuse),error:runtime.error,points:copy(POINTS),site:copy(M.SITE)}),v063RadieuseOpen:()=>v027Open('data','radieuse'),v063RadieuseAction:action});};
}
