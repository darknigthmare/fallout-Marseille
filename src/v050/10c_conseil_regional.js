/* Fallout: Mistral v0.60 — États généraux du Mistral.
   Ce module transforme la projection v0.59 en conseil régional jouable.
   Les six fins de chapitre restent intactes : le conseil les agrège, fait voter
   quatre motions, ratifie une charte et produit des épilogues textuels honnêtes. */
const MistralCouncil=(()=>{
 'use strict';
 const SCHEMA=1;
 const NETWORKS=[
  {id:'identite',label:'Identité'},
  {id:'eau',label:'Eau'},
  {id:'sante',label:'Santé'},
  {id:'transport',label:'Transport'},
  {id:'energie',label:'Énergie'},
  {id:'communication',label:'Communication'},
  {id:'approvisionnement',label:'Approvisionnement'}
 ];
 const PATHS=[
  {id:'charte_vivants',label:'Charte des Vivants',title:'LES VIVANTS AVANT LES DOSSIERS',summary:'Aucune base unique ne peut retirer l’existence civile ni les droits vitaux.'},
  {id:'republique_services',label:'République des Services',title:'LA RÉPUBLIQUE RESTE OUVERTE',summary:'Les sept réseaux deviennent des institutions autonomes soumises à une charte commune.'},
  {id:'continuite',label:'Continuité administrative',title:'LA CONTINUITÉ RETROUVÉE',summary:'Une autorité régionale unifie les registres, les priorités et les recours.'},
  {id:'federation',label:'Fédération des Communes',title:'LES COMMUNES FONT RÉGION',summary:'Les territoires conservent leurs réseaux et délèguent seulement les compétences communes.'},
  {id:'travailleurs',label:'Gouvernement des travailleurs',title:'CEUX QUI TIENNENT LES RÉSEAUX',summary:'Les équipes qui entretiennent les services disposent du pouvoir de décision et de veto.'},
  {id:'levant',label:'Autorité du Levant',title:'LA CÔTE SOUS PAVILLON',summary:'Une autorité maritime et logistique coordonne secours, voies et approvisionnements.'},
  {id:'technocratie',label:'Technocratie atomique et contractuelle',title:'LA MESURE ET LE CONTRAT',summary:'Experts, seuils techniques et contrats deviennent la principale source de légitimité.'},
  {id:'fragmentation',label:'Fragmentation régionale',title:'AUCUNE CHARTE UNIQUE',summary:'Les territoires refusent une constitution commune et conservent leurs accords locaux.'}
 ];
 const MOTIONS={
  preuve:{label:'Motion I — Qui peut prouver une existence ?',choices:{
   pluralite:{label:'Pluralité obligatoire des preuves',text:'Aucune base unique ne peut déclarer une mort civile.',bonuses:{charte_vivants:4,republique_services:2,federation:2,continuite:-3,technocratie:-2}},
   registre:{label:'Registre régional unifié avec recours',text:'Une autorité unique conserve les versions et statue après recours.',bonuses:{continuite:4,technocratie:2,republique_services:1,charte_vivants:-1,fragmentation:-2}},
   local:{label:'Témoignages et registres territoriaux',text:'Les communes et relais attestent, puis se reconnaissent mutuellement.',bonuses:{federation:4,travailleurs:2,charte_vivants:1,fragmentation:1,continuite:-1}}
  }},
  minimum:{label:'Motion II — Quel minimum est inconditionnel ?',choices:{
   universel:{label:'Eau, soins et passage d’urgence universels',text:'Les besoins vitaux précèdent identité, cotisation et contrat.',bonuses:{charte_vivants:4,republique_services:4,federation:1,travailleurs:1,technocratie:-2,levant:-1}},
   contribution:{label:'Droits garantis par contribution ou service',text:'Chaque réseau publie la contribution qui ouvre des droits durables.',bonuses:{travailleurs:3,technocratie:3,republique_services:2,levant:1,charte_vivants:-2}},
   territorial:{label:'Quotas publics décidés par territoire',text:'Chaque territoire garantit un minimum et publie ses priorités.',bonuses:{federation:4,levant:2,continuite:1,fragmentation:1,republique_services:1}}
  }},
  controle:{label:'Motion III — Qui peut arrêter une décision ?',choices:{
   audit:{label:'Audit public et recours contradictoire',text:'Toute exclusion doit être motivée, conservée et contestable.',bonuses:{republique_services:4,charte_vivants:3,technocratie:1,continuite:1,levant:-1}},
   veto:{label:'Veto des équipes et usagers du réseau',text:'Les travailleurs et usagers peuvent suspendre un ordre dangereux.',bonuses:{travailleurs:4,federation:2,republique_services:2,continuite:-2,technocratie:-1}},
   commandement:{label:'Commandement régional en situation critique',text:'Une autorité peut imposer une priorité limitée et journalisée.',bonuses:{continuite:4,levant:4,technocratie:2,republique_services:-1,charte_vivants:-2}}
  }},
  force:{label:'Motion IV — Quelle force protège les réseaux ?',choices:{
   sans_armee:{label:'Services sans armée propre',text:'Chaque service dépend de secours civils et de garanties croisées.',bonuses:{charte_vivants:4,republique_services:4,federation:1,levant:-4,continuite:-2,technocratie:-1}},
   gardes_locales:{label:'Gardes locales coordonnées',text:'Les communes conservent leurs gardes sous règles d’assistance mutuelle.',bonuses:{federation:4,travailleurs:2,fragmentation:2,charte_vivants:1,continuite:-1}},
   unifiee:{label:'Force régionale unifiée',text:'Un commandement commun sécurise les axes, installations et secours.',bonuses:{continuite:4,levant:4,technocratie:2,republique_services:1,fragmentation:-3}}
  }}
 };
 const DELEGATIONS=[
  {id:'a03',label:'A‑03 et Odette Ferraud',network:'identite',aff:{charte_vivants:4,republique_services:2,federation:2,travailleurs:1,continuite:-1,levant:-2,technocratie:-2,fragmentation:0},likes:['preuve:pluralite','controle:audit','force:sans_armee'],dislikes:['preuve:registre','controle:commandement']},
  {id:'sansdossier',label:'Les Sans-Dossier',network:'identite',aff:{charte_vivants:5,republique_services:2,federation:2,travailleurs:1,continuite:-3,levant:-2,technocratie:-3,fragmentation:0},likes:['preuve:pluralite','minimum:universel','force:sans_armee'],dislikes:['preuve:registre','controle:commandement','force:unifiee']},
  {id:'concorde',label:'Direction de la Continuité — CONCORDE',network:'identite',aff:{continuite:5,technocratie:2,republique_services:1,levant:1,charte_vivants:-2,federation:-1,travailleurs:-2,fragmentation:-3},likes:['preuve:registre','controle:audit','force:unifiee'],dislikes:['preuve:local','force:gardes_locales']},
  {id:'convention',label:'Convention des Cendres',network:'communication',aff:{charte_vivants:2,federation:2,travailleurs:2,republique_services:1,continuite:-3,technocratie:-2,levant:-2,fragmentation:0},likes:['preuve:pluralite','minimum:universel','force:gardes_locales'],dislikes:['controle:commandement','preuve:registre']},
  {id:'communes',label:'Communes du Mistral',network:'eau',aff:{federation:5,charte_vivants:2,republique_services:2,travailleurs:1,fragmentation:1,continuite:-2,technocratie:-1,levant:-1},likes:['preuve:local','minimum:territorial','force:gardes_locales'],dislikes:['force:unifiee','controle:commandement']},
  {id:'gilets',label:'Gilets de Cendre',network:'transport',aff:{federation:3,charte_vivants:2,travailleurs:2,republique_services:1,fragmentation:1,continuite:-3,technocratie:-2,levant:-2},likes:['preuve:local','minimum:universel','force:gardes_locales'],dislikes:['controle:commandement','force:unifiee']},
  {id:'syndicat',label:'Syndicat Perpétuel',network:'approvisionnement',aff:{travailleurs:5,republique_services:2,federation:2,charte_vivants:1,technocratie:-1,continuite:-2,levant:-2,fragmentation:0},likes:['minimum:contribution','controle:veto','force:gardes_locales'],dislikes:['controle:commandement']},
  {id:'vigies',label:'Vigies des Crêtes',network:'communication',aff:{republique_services:3,federation:2,charte_vivants:1,continuite:1,technocratie:1,travailleurs:1,levant:0,fragmentation:-1},likes:['controle:audit','minimum:territorial','force:gardes_locales'],dislikes:[]},
  {id:'insulaires',label:'Insulaires du Lazaret',network:'approvisionnement',aff:{federation:3,charte_vivants:2,republique_services:2,fragmentation:1,travailleurs:0,continuite:-1,technocratie:-1,levant:-1},likes:['minimum:territorial','controle:audit','force:gardes_locales'],dislikes:['force:unifiee']},
  {id:'sociale',label:'La Sociale',network:'sante',aff:{republique_services:5,charte_vivants:4,federation:1,travailleurs:1,technocratie:0,continuite:0,levant:-1,fragmentation:-2},likes:['minimum:universel','controle:audit','force:sans_armee'],dislikes:['minimum:territorial','controle:commandement']},
  {id:'aiguilleurs',label:'Aiguilleurs du Réseau',network:'transport',aff:{republique_services:3,travailleurs:2,continuite:2,technocratie:1,federation:1,charte_vivants:0,levant:0,fragmentation:-2},likes:['minimum:contribution','controle:audit','force:unifiee'],dislikes:['fragmentation:yes']},
  {id:'commissariat',label:'Commissariat des Atomes',network:'energie',aff:{technocratie:5,continuite:2,levant:1,republique_services:1,travailleurs:0,federation:-1,charte_vivants:-1,fragmentation:-3},likes:['minimum:contribution','controle:commandement','force:unifiee'],dislikes:['force:sans_armee']},
  {id:'amiraute',label:'Amirauté du Levant',network:'approvisionnement',aff:{levant:5,continuite:2,technocratie:2,republique_services:0,travailleurs:-1,federation:-1,charte_vivants:-2,fragmentation:-3},likes:['minimum:territorial','controle:commandement','force:unifiee'],dislikes:['force:sans_armee']}
 ];
 const PATH_EFFECTS={
  charte_vivants:{access:8,legitimacy:10,coercion:-12,resilience:2},
  republique_services:{access:8,legitimacy:7,coercion:-5,resilience:10},
  continuite:{access:2,legitimacy:2,coercion:10,resilience:8},
  federation:{access:5,legitimacy:6,coercion:-4,resilience:6},
  travailleurs:{access:4,legitimacy:5,coercion:-2,resilience:7},
  levant:{access:2,legitimacy:1,coercion:8,resilience:8},
  technocratie:{access:3,legitimacy:3,coercion:7,resilience:10},
  fragmentation:{access:-4,legitimacy:-2,coercion:-5,resilience:-8}
 };
 const NETWORK_POLICY={
  charte_vivants:{
   identite:'Aucune mort civile ne peut être prononcée par une base unique ; la présence et le recours ouvrent immédiatement des droits provisoires.',
   eau:'Un minimum vital d’eau précède toute dette, identité ou appartenance territoriale.',
   sante:'L’urgence médicale est inconditionnelle ; les dettes de soin ne se transmettent pas.',
   transport:'Le passage d’urgence ne peut dépendre d’un billet, d’un dossier de naissance ou d’une dette.',
   energie:'Toute zone exposée dispose d’un droit de retrait, de mesure contradictoire et de réparation.',
   communication:'Les versions contradictoires restent publiques ; aucun signal unique ne vaut vérité définitive.',
   approvisionnement:'Les réserves vitales sont distribuées avant les contrats, avec quantités et refus publiés.'
  },
  republique_services:{
   identite:'Le service de l’identité constate et conserve les preuves, sans disposer d’une force propre.',
   eau:'Le service de l’eau garantit un seuil commun et rend ses stocks, pannes et priorités vérifiables.',
   sante:'La Sociale et les dispensaires coordonnent l’urgence sous une caisse et un recours communs.',
   transport:'Les voies partagent un billet civique, des priorités publiées et des arrêts de sécurité humains.',
   energie:'Les opérateurs publient doses, capacités et délestages ; les autres services disposent d’un recours.',
   communication:'Radio, poste et relais forment un service autonome tenu de publier sources et corrections.',
   approvisionnement:'Ports, marchés et ateliers partagent un manifeste régional sans devenir une armée.'
  },
  continuite:{
   identite:'Un registre régional unifié statue après recours et devient la preuve principale d’existence.',
   eau:'Les quotas et pompes suivent une priorité régionale unique, journalisée par CONCORDE.',
   sante:'Le triage régional répartit lits et médicaments selon une grille commune.',
   transport:'Horaires, billets et fermetures sont coordonnés par une autorité centrale.',
   energie:'Les délestages et zones d’exposition sont décidés au niveau régional.',
   communication:'Une chaîne officielle valide alertes, corrections et ordres de service.',
   approvisionnement:'Un manifeste central hiérarchise les cargaisons, réquisitions et réserves.'
  },
  federation:{
   identite:'Les registres territoriaux se reconnaissent mutuellement et conservent leurs contradictions.',
   eau:'Chaque bassin gère ses réserves tout en garantissant l’assistance entre communes.',
   sante:'Les dispensaires restent locaux, avec accueil réciproque et évacuations coordonnées.',
   transport:'Les voies sont cogérées ; aucun territoire ne peut imposer seul un péage régional.',
   energie:'Les producteurs négocient les échanges et gardent un droit de retrait territorial.',
   communication:'Chaque relais possède une voix et une copie des décisions fédérales.',
   approvisionnement:'Les communes mutualisent les pénuries sans abandonner leurs stocks à une autorité unique.'
  },
  travailleurs:{
   identite:'Les équipes d’accueil et d’archives disposent d’un veto sur les effacements automatiques.',
   eau:'Ceux qui entretiennent pompes et filtres décident des arrêts et des priorités de sécurité.',
   sante:'Les soignants et usagers gouvernent les caisses, stocks et protocoles.',
   transport:'Cheminots, dockers et conducteurs peuvent suspendre toute exclusion dangereuse.',
   energie:'Les équipes exposées disposent d’un veto sur les doses, cadences et redémarrages.',
   communication:'Les opérateurs conservent les sources et peuvent refuser un ordre de propagande.',
   approvisionnement:'Ateliers, marchés et équipages publient les stocks et décident collectivement des cadences.'
  },
  levant:{
   identite:'Un statut régional de résident et d’équipage conditionne la plupart des droits durables.',
   eau:'Dessalement, citernes et convois sont placés sous priorité logistique.',
   sante:'Les secours lourds suivent un commandement côtier et des couloirs d’évacuation.',
   transport:'Ports, routes stratégiques et voies maritimes passent sous protection unifiée.',
   energie:'Les installations critiques sont sécurisées comme objectifs de défense régionale.',
   communication:'Les alertes côtières et ordres de secours disposent d’une priorité de diffusion.',
   approvisionnement:'Manifestes, saisies et corridors sont coordonnés par l’Amirauté sous règles publiées.'
  },
  technocratie:{
   identite:'L’existence est validée par une chaîne de preuves normalisée et des seuils d’erreur mesurables.',
   eau:'Les allocations suivent rendement, pertes, qualité et contrats de maintenance.',
   sante:'Le triage combine urgence, capacité et contribution à la caisse régionale.',
   transport:'Les horaires, accès et fermetures sont optimisés selon capacité et risque calculés.',
   energie:'Les doses collectives, rendements et contrats déterminent les zones alimentées.',
   communication:'La confiance d’un signal dépend de sa traçabilité, de ses capteurs et de son audit.',
   approvisionnement:'Les contrats et prévisions répartissent stocks, pièces et cargaisons.'
  },
  fragmentation:{
   identite:'Chaque territoire conserve sa définition de l’existence et ses propres preuves.',
   eau:'Les bassins et citernes ne partagent plus de seuil régional garanti.',
   sante:'Les dispensaires négocient séparément accueil, dettes et évacuations.',
   transport:'Les passages, billets et péages dépendent de chaque autorité locale.',
   energie:'Les producteurs protègent leurs installations et limitent les échanges.',
   communication:'Les fréquences se contredisent sans instance commune de correction.',
   approvisionnement:'Marchés, ports et ateliers concluent des accords ponctuels sans manifeste commun.'
  }
 };
 const copy=value=>value==null?value:JSON.parse(JSON.stringify(value));
 const own=(value,key)=>Object.prototype.hasOwnProperty.call(value||{},key);
 const clamp=(value,min=0,max=100)=>Math.max(min,Math.min(max,Number.isFinite(Number(value))?Number(value):0));
 const pathById=id=>PATHS.find(path=>path.id===id);
 const motionComplete=clauses=>Object.keys(MOTIONS).every(id=>own(MOTIONS[id].choices,clauses?.[id]));
 const motionToken=(motion,choice)=>`${motion}:${choice}`;
 function fresh(){
  return{schema:SCHEMA,status:'locked',convenedAt:0,clauses:{preuve:null,minimum:null,controle:null,force:null},charter:null,tally:null,legitimacy:0,failedVotes:[],slides:[],projectionAtCouncil:null,journal:[]};
 }
 function sanitize(raw){
  const base=fresh(),input=raw&&typeof raw==='object'?raw:{};
  const statuses=new Set(['locked','available','convened','deliberating','ratified']);
  base.status=statuses.has(input.status)?input.status:'locked';
  base.convenedAt=Math.max(0,Number(input.convenedAt)||0);
  for(const id of Object.keys(MOTIONS)){const choice=input.clauses?.[id];base.clauses[id]=own(MOTIONS[id].choices,choice)?choice:null;}
  base.charter=pathById(input.charter)?input.charter:null;
  if(input.tally&&typeof input.tally==='object')base.tally={
   for:Math.max(0,Math.floor(Number(input.tally.for)||0)),
   against:Math.max(0,Math.floor(Number(input.tally.against)||0)),
   abstain:Math.max(0,Math.floor(Number(input.tally.abstain)||0)),
   details:Array.isArray(input.tally.details)?input.tally.details.filter(item=>item&&DELEGATIONS.some(d=>d.id===item.id)&&['for','against','abstain'].includes(item.vote)).slice(0,DELEGATIONS.length).map(copy):[]
  };
  base.legitimacy=Math.round(clamp(input.legitimacy));
  base.failedVotes=Array.isArray(input.failedVotes)?input.failedVotes.filter(item=>item&&pathById(item.path)).slice(-16).map(item=>({path:item.path,for:Math.max(0,Math.floor(Number(item.for)||0)),against:Math.max(0,Math.floor(Number(item.against)||0)),abstain:Math.max(0,Math.floor(Number(item.abstain)||0)),at:Math.max(0,Number(item.at)||0)})):[];
  base.slides=Array.isArray(input.slides)?input.slides.filter(item=>item&&typeof item.id==='string'&&typeof item.title==='string'&&typeof item.text==='string').slice(0,16).map(copy):[];
  base.projectionAtCouncil=input.projectionAtCouncil&&typeof input.projectionAtCouncil==='object'?copy(input.projectionAtCouncil):null;
  base.journal=Array.isArray(input.journal)?input.journal.filter(item=>item&&['convene','motion','vote_failed','ratified'].includes(item.type)).slice(-96).map(copy):[];
  if(base.charter&&base.status!=='ratified')base.status='ratified';
  return base;
 }
 function registryOf(campaign={},madame=null){
  const registry=madame||campaign.v059Madame||{};
  const networks=registry.networks&&typeof registry.networks==='object'?registry.networks:{};
  const scores=registry.scores&&typeof registry.scores==='object'?registry.scores:{};
  const projection=registry.projection&&typeof registry.projection==='object'?registry.projection:{winner:'fragmentation',alternate:null,confidence:0,margin:0,label:'Fragmentation régionale'};
  return{networks,scores,projection,identity:registry.identity||{}};
 }
 function unlocked(campaign={}){return !!(campaign.quest?.aubagneComplete||Number(campaign.quest?.main)>=59&&campaign.quest?.aubagneOutcome);}
 function synchronize(raw,campaign={},madame=null){
  const ledger=sanitize(raw),registry=registryOf(campaign,madame),isUnlocked=unlocked(campaign);
  if(!isUnlocked&&ledger.status!=='ratified')ledger.status='locked';
  else if(isUnlocked&&ledger.status==='locked')ledger.status='available';
  if(ledger.status==='convened'&&motionComplete(ledger.clauses))ledger.status='deliberating';
  if(ledger.status==='deliberating'&&!motionComplete(ledger.clauses))ledger.status='convened';
  if(ledger.status==='ratified'&&ledger.charter){
   if(!ledger.projectionAtCouncil)ledger.projectionAtCouncil=copy(registry.projection);
   if(!ledger.slides.length)ledger.slides=buildSlides(ledger.charter,ledger.clauses,registry,ledger.tally||forecastVotes(ledger.charter,ledger.clauses,registry));
  }
  return ledger;
 }
 function clauseBonus(path,clauses={}){
  let total=0;
  for(const [motion,choice] of Object.entries(clauses)){if(choice&&own(MOTIONS[motion]?.choices||{},choice))total+=Number(MOTIONS[motion].choices[choice].bonuses[path]||0);}
  return total;
 }
 function rankedPaths(registry,clauses={}){
  return PATHS.map((path,index)=>({...path,base:Number(registry.scores?.[path.id]||0),motion:clauseBonus(path.id,clauses),index}))
   .map(item=>({...item,adjusted:Math.round((item.base+item.motion)*100)/100}))
   .sort((a,b)=>b.adjusted-a.adjusted||b.base-a.base||a.index-b.index);
 }
 function networkSignal(path,delegate,registry){
  const network=registry.networks?.[delegate.network];if(!network)return 0;
  let signal=0;
  if(['charte_vivants','republique_services','federation','travailleurs'].includes(path)&&Number(network.legitimacy)>=55)signal++;
  if(['continuite','levant','technocratie'].includes(path)&&Number(network.resilience)>=55)signal++;
  if(path==='charte_vivants'&&Number(network.coercion)<=45)signal++;
  if(path==='republique_services'&&Number(network.access)>=55&&Number(network.resilience)>=50)signal++;
  if(path==='fragmentation'&&Number(network.resilience)<45)signal++;
  if(['continuite','levant','technocratie'].includes(path)&&Number(network.coercion)>=65)signal++;
  return signal;
 }
 function delegateVote(delegate,path,clauses,registry){
  const ranked=rankedPaths(registry,clauses),top=ranked[0],projection=registry.projection||{},selectedTokens=Object.entries(clauses||{}).filter(([,choice])=>choice).map(([motion,choice])=>motionToken(motion,choice));
  let score=Number(delegate.aff[path]||0);
  if(path===projection.winner)score+=2;else if(path===projection.alternate)score+=1;
  if(top&&path===top.id)score++;
  if(top&&top.adjusted-(ranked.find(item=>item.id===path)?.adjusted||0)>8)score--;
  for(const token of selectedTokens){if(delegate.likes.includes(token))score++;if(delegate.dislikes.includes(token))score--;}
  score+=networkSignal(path,delegate,registry);
  const vote=score>=2?'for':score<=-2?'against':'abstain';
  const reasons=[];
  if(Number(delegate.aff[path]||0)>=3)reasons.push('orientation proche de son mandat');
  if(path===projection.winner)reasons.push('projection régionale favorable');
  if(selectedTokens.some(token=>delegate.likes.includes(token)))reasons.push('motions compatibles');
  if(selectedTokens.some(token=>delegate.dislikes.includes(token)))reasons.push('garanties contestées');
  if(!reasons.length)reasons.push(vote==='abstain'?'mandat partagé':'équilibre des réseaux');
  return{id:delegate.id,label:delegate.label,vote,score,reasons};
 }
 function forecastVotes(path,clauses,registry){
  const details=DELEGATIONS.map(delegate=>delegateVote(delegate,path,clauses,registry)),count=vote=>details.filter(item=>item.vote===vote).length;
  const tally={for:count('for'),against:count('against'),abstain:count('abstain'),details};
  tally.passes=tally.for>=7&&tally.for>tally.against;
  return tally;
 }
 function candidates(raw,campaign={},madame=null){
  const ledger=synchronize(raw,campaign,madame),registry=registryOf(campaign,madame),complete=motionComplete(ledger.clauses),ranked=rankedPaths(registry,ledger.clauses),top=ranked[0]?.adjusted||0,projection=registry.projection||{};
  return ranked.map(item=>{
   const forecast=complete?forecastVotes(item.id,ledger.clauses,registry):{for:0,against:0,abstain:DELEGATIONS.length,details:[],passes:false};
   const eligible=complete&&(item.id===projection.winner||item.id===projection.alternate||item.id==='fragmentation'||item.adjusted>=top-5||item.motion>=4&&item.adjusted>=top-9);
   return{...item,eligible,forecast};
  });
 }
 function applyEffects(network,path,clauses){
  const effect={...(PATH_EFFECTS[path]||{})},next={...copy(network)};
  for(const key of ['access','legitimacy','coercion','resilience'])next[key]=Math.round(clamp(Number(next[key]||0)+Number(effect[key]||0)));
  if(clauses.preuve==='pluralite'&&next.id==='identite'){next.legitimacy=Math.round(clamp(next.legitimacy+8));next.coercion=Math.round(clamp(next.coercion-5));}
  if(clauses.preuve==='registre'&&next.id==='identite'){next.resilience=Math.round(clamp(next.resilience+5));next.coercion=Math.round(clamp(next.coercion+4));}
  if(clauses.preuve==='local'&&next.id==='identite'){next.legitimacy=Math.round(clamp(next.legitimacy+4));next.resilience=Math.round(clamp(next.resilience+3));}
  if(clauses.minimum==='universel')next.access=Math.round(clamp(next.access+5));
  if(clauses.minimum==='contribution'&&['sante','approvisionnement','transport'].includes(next.id)){next.resilience=Math.round(clamp(next.resilience+4));next.coercion=Math.round(clamp(next.coercion+2));}
  if(clauses.minimum==='territorial'&&['eau','transport','approvisionnement'].includes(next.id))next.access=Math.round(clamp(next.access+3));
  if(clauses.controle==='audit'){next.legitimacy=Math.round(clamp(next.legitimacy+4));next.coercion=Math.round(clamp(next.coercion-2));}
  if(clauses.controle==='veto'&&['energie','transport','approvisionnement','sante'].includes(next.id)){next.legitimacy=Math.round(clamp(next.legitimacy+3));next.resilience=Math.round(clamp(next.resilience+3));}
  if(clauses.controle==='commandement'){next.resilience=Math.round(clamp(next.resilience+3));next.coercion=Math.round(clamp(next.coercion+4));}
  if(clauses.force==='sans_armee'){next.coercion=Math.round(clamp(next.coercion-3));next.resilience=Math.round(clamp(next.resilience-1));}
  if(clauses.force==='gardes_locales'){next.resilience=Math.round(clamp(next.resilience+2));next.coercion=Math.round(clamp(next.coercion+1));}
  if(clauses.force==='unifiee'){next.resilience=Math.round(clamp(next.resilience+5));next.coercion=Math.round(clamp(next.coercion+5));}
  return next;
 }
 function buildSlides(path,clauses,registry,tally){
  const charter=pathById(path),slides=[
   {id:'charter',title:charter?.title||'ÉTATS GÉNÉRAUX DU MISTRAL',text:`${charter?.summary||''} Le vote est enregistré : ${tally.for} pour, ${tally.against} contre et ${tally.abstain} abstention(s).`},
   {id:'motions',title:'LES QUATRE GARANTIES',text:Object.entries(clauses).map(([motion,choice])=>`${MOTIONS[motion].label} : ${MOTIONS[motion].choices[choice]?.label||'non résolue'}.`).join(' ')}
  ];
  for(const definition of NETWORKS){
   const before=registry.networks?.[definition.id]||{id:definition.id,label:definition.label,access:20,legitimacy:20,coercion:50,resilience:25,controller:'Autorités fragmentées'};
   const after=applyEffects(before,path,clauses),policy=NETWORK_POLICY[path]?.[definition.id]||'La charte ne fixe pas de règle commune pour ce réseau.';
   slides.push({id:definition.id,title:definition.label.toUpperCase(),text:`${policy} Contrôleur au jour du vote : ${before.controller||'autorités fragmentées'}. Projection du registre — accès ${before.access}→${after.access}, légitimité ${before.legitimacy}→${after.legitimacy}, coercion ${before.coercion}→${after.coercion}, résilience ${before.resilience}→${after.resilience}.`});
  }
  return slides;
 }
 function legitimacy(tally,registry,clauses){
  const confidence=Number(registry.projection?.confidence||0),motionCount=Object.values(clauses).filter(Boolean).length;
  return Math.round(clamp(42+(tally.for-tally.against)*4+motionCount*2+confidence*.18-tally.abstain));
 }
 function reduce(raw,action={},campaign={},madame=null){
  const ledger=synchronize(raw,campaign,madame),registry=registryOf(campaign,madame),failure=reason=>({ok:false,reason,ledger}),at=Math.max(0,Number(action.at??campaign.playTime)||0);
  if(action.type==='convene'){
   if(ledger.status!=='available')return failure(ledger.status==='locked'?'Les six chapitres doivent être conclus avant les États généraux.':'Le conseil est déjà convoqué.');
   ledger.status='convened';ledger.convenedAt=at;ledger.projectionAtCouncil=copy(registry.projection);ledger.journal.push({type:'convene',at});
   return{ok:true,ledger,notice:'Les délégations des réseaux sont convoquées à Aubagne.'};
  }
  if(action.type==='motion'){
   if(!['convened','deliberating'].includes(ledger.status))return failure('Les motions ne peuvent être modifiées qu’avant la ratification.');
   if(!own(MOTIONS,action.motion)||!own(MOTIONS[action.motion].choices,action.choice))return failure('Motion ou choix inconnu.');
   ledger.clauses[action.motion]=action.choice;ledger.status=motionComplete(ledger.clauses)?'deliberating':'convened';ledger.journal.push({type:'motion',motion:action.motion,choice:action.choice,at});
   return{ok:true,ledger,notice:MOTIONS[action.motion].choices[action.choice].text};
  }
  if(action.type==='ratify'){
   if(ledger.status!=='deliberating'||!motionComplete(ledger.clauses))return failure('Les quatre motions doivent être adoptées avant le vote final.');
   if(!pathById(action.path))return failure('Projet de charte inconnu.');
   const candidate=candidates(ledger,campaign,madame).find(item=>item.id===action.path);
   if(!candidate?.eligible)return failure('Cette orientation ne réunit pas encore les conditions nécessaires pour être soumise au vote.');
   const tally=forecastVotes(action.path,ledger.clauses,registry);
   if(!tally.passes){
    ledger.failedVotes.push({path:action.path,for:tally.for,against:tally.against,abstain:tally.abstain,at});ledger.journal.push({type:'vote_failed',path:action.path,for:tally.for,against:tally.against,abstain:tally.abstain,at});
    return{ok:true,passed:false,ledger,notice:`La motion est rejetée : ${tally.for} pour, ${tally.against} contre, ${tally.abstain} abstention(s). Les garanties peuvent être amendées.`};
   }
   ledger.status='ratified';ledger.charter=action.path;ledger.tally=tally;ledger.legitimacy=legitimacy(tally,registry,ledger.clauses);ledger.projectionAtCouncil=copy(registry.projection);ledger.slides=buildSlides(action.path,ledger.clauses,registry,tally);ledger.journal.push({type:'ratified',path:action.path,for:tally.for,against:tally.against,abstain:tally.abstain,at});
   return{ok:true,passed:true,ledger,notice:`${pathById(action.path).label} ratifiée par ${tally.for} voix contre ${tally.against}.`};
  }
  if(action.type==='refresh')return{ok:true,ledger:synchronize(ledger,campaign,madame),notice:'Conseil régional recalculé.'};
  return failure('Action du conseil inconnue.');
 }
 function bulletin(raw,campaign={},madame=null){
  const ledger=synchronize(raw,campaign,madame),registry=registryOf(campaign,madame);
  if(ledger.status==='locked')return'États généraux — les six chartes régionales ne sont pas encore conclues.';
  if(ledger.status==='available')return`États généraux — convocation possible. Projection M.A.D.A.M.E. : ${registry.projection?.label||'indéterminée'}.`;
  if(ledger.status==='convened')return`États généraux — ${Object.values(ledger.clauses).filter(Boolean).length}/4 motions adoptées.`;
  if(ledger.status==='deliberating')return`États généraux — les quatre motions sont adoptées. La ratification finale reste ouverte.`;
  return`États généraux — ${pathById(ledger.charter)?.label||ledger.charter} ratifiée, légitimité ${ledger.legitimacy}/100, vote ${ledger.tally?.for||0}-${ledger.tally?.against||0}-${ledger.tally?.abstain||0}.`;
 }
 return{SCHEMA,NETWORKS:copy(NETWORKS),PATHS:copy(PATHS),MOTIONS:copy(MOTIONS),DELEGATIONS:copy(DELEGATIONS),fresh,sanitize,synchronize,candidates,forecastVotes,buildSlides,reduce,bulletin};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralCouncil;

if(typeof baseState==='function'&&typeof MistralMadame!=='undefined'){
 const clone=value=>JSON.parse(JSON.stringify(value));
 const oldBase=baseState;baseState=function(){const value=oldBase();value.v060Council=MistralCouncil.fresh();return value;};
 const oldMigrate=migrateState;migrateState=function(input={}){const value=oldMigrate(input);value.v059Madame=MistralMadame.synchronize(value.v059Madame,value);value.v060Council=MistralCouncil.synchronize(input.v060Council,value,value.v059Madame);return value;};
 state=migrateState(state);
 function restoreCouncil(owner,snapshot){if(state!==owner)return;for(const key of Object.keys(owner))if(!Object.prototype.hasOwnProperty.call(snapshot,key))delete owner[key];Object.assign(owner,snapshot);}
 function councilNotice(message){if(typeof V027!=='undefined')V027.message=message;if(typeof toast==='function')toast(message,'bad');return false;}
 function syncCouncil(){state.v059Madame=MistralMadame.synchronize(state.v059Madame,state);state.v060Council=MistralCouncil.synchronize(state.v060Council,state,state.v059Madame);return state.v060Council;}
 function transactCouncil(action){
  const owner=state,snapshot=clone(owner);owner.v059Madame=MistralMadame.synchronize(owner.v059Madame,owner);const plan=MistralCouncil.reduce(owner.v060Council,{...action,at:owner.playTime},owner,owner.v059Madame);
  if(!plan.ok)return councilNotice(plan.reason);
  try{owner.v060Council=plan.ledger;if(state!==owner||saveGame(false)===false)throw Error('Le conseil ne peut pas être sauvegardé.');}
  catch(error){restoreCouncil(owner,snapshot);return councilNotice((error?.message||'Écriture refusée.')+' Opération annulée.');}
  if(typeof updateQuestUI==='function')updateQuestUI(true);return plan;
 }
 const previousSave=saveGame;saveGame=function(){if(state?.v060Council){state.v059Madame=MistralMadame.synchronize(state.v059Madame,state);state.v060Council=MistralCouncil.synchronize(state.v060Council,state,state.v059Madame);}return previousSave(...arguments);};
 function councilBlocked(){if(!gameStarted||!(state.player?.hp>0))return'Reprenez une partie active avant cette opération.';if(!state.quest?.aubagneComplete)return'Concluez la charte d’Aubagne avant de convoquer la région.';return null;}
 function openCouncilData(){if(mode==='DIALOGUE')closeDialogue();v027Open('data','council');}
 function councilDialogue(){
  const deny=councilBlocked();syncCouncil();const council=state.v060Council,choices=[];
  if(deny)choices.push({text:'Revenir plus tard.',onChoose:closeDialogue});
  else if(council.status==='available')choices.push({text:'Convoquer les États généraux du Mistral.',onChoose:()=>{const plan=transactCouncil({type:'convene'});if(plan){closeDialogue();openCouncilData();}}});
  else if(['convened','deliberating'].includes(council.status))choices.push({text:'Reprendre les motions du conseil.',onChoose:openCouncilData});
  else if(council.status==='ratified'){choices.push({text:'Relire la ratification et les sept épilogues.',onChoose:()=>showEnding('regional')});choices.push({text:'Consulter le registre du conseil.',onChoose:openCouncilData});}
  choices.push({text:'Parler d’autre chose.',onChoose:()=>{closeDialogue();oldTalkMireille();}});
  const text=council.status==='ratified'?`La charte est votée. ${MistralCouncil.bulletin(council,state,state.v059Madame)}`:council.status==='available'?'Les six conseils locaux ont parlé. M.A.D.A.M.E. peut compter les équilibres, mais seule une assemblée peut transformer une projection en règle commune.':`Les délégations attendent les quatre motions. Projection actuelle : ${state.v059Madame.projection.label}.`;
  openDialogue(speaker('Mireille Barral','RAPPORTEUSE DES ÉTATS GÉNÉRAUX','MB'),text,choices);
 }
 const oldTalkMireille=talkMireille;talkMireille=function(){syncCouncil();if(state.quest?.aubagneComplete)return councilDialogue();return oldTalkMireille(...arguments);};
 const oldCompleteAubagne=completeAubagneChapter;completeAubagneChapter=function(){const result=oldCompleteAubagne(...arguments);syncCouncil();saveGame(false);return result;};
 const oldContinueExplore=continueExplore;continueExplore=function(){const prompt=!!state.quest?.aubagneComplete&&syncCouncil().status==='available';const result=oldContinueExplore(...arguments);if(prompt)setTimeout(()=>councilDialogue(),120);return result;};
 function showCouncilEnding(){
  syncCouncil();const council=state.v060Council;if(council.status!=='ratified')return councilNotice('Aucune charte régionale n’a encore été ratifiée.');
  document.exitPointerLock?.();mode='ENDING';$('hud').classList.remove('active');for(const id of ['pauseScreen','pipboy','tradeScreen','projectionScreen','dialogue'])$(id)?.classList.add('hidden');
  const charter=pathByCouncil(council.charter);$('endingEyebrow').textContent='ÉTATS GÉNÉRAUX DU MISTRAL';$('endingTitle').textContent=charter?.title||'CHARTE RÉGIONALE';$('btnContinueExplore').textContent='Continuer à explorer après la ratification';
  $('endingSummary').innerHTML=council.slides.map(slide=>`<div class="ending-card"><h3>${escapeCouncil(slide.title)}</h3><p>${escapeCouncil(slide.text)}</p></div>`).join('');$('endingScreen').classList.add('active');return true;
 }
 const oldShowEnding=showEnding;showEnding=function(chapter=null){if(chapter==='regional')return showCouncilEnding();return oldShowEnding(...arguments);};
 function pathByCouncil(id){return MistralCouncil.PATHS.find(path=>path.id===id);}
 function escapeCouncil(value){return typeof v027Escape==='function'?v027Escape(String(value??'')):String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
 function motionPanel(council,deny){
  return Object.entries(MistralCouncil.MOTIONS).map(([id,motion])=>'<section class="v046-notice"><h3>'+escapeCouncil(motion.label)+'</h3><p>'+escapeCouncil(motion.choices[council.clauses[id]]?.text||'Aucune clause adoptée.')+'</p>'+Object.entries(motion.choices).map(([choice,data])=>v027Button((council.clauses[id]===choice?'✓ ':'')+data.label,'c60:motion',id+'|'+choice,!!deny||council.status==='ratified')).join('')+'</section>').join('');
 }
 function candidatesPanel(council,deny){
  if(!Object.values(council.clauses).every(Boolean))return'<section class="v046-notice"><h3>Ratification</h3><p>Les quatre motions doivent être adoptées avant la présentation des chartes.</p></section>';
  return MistralCouncil.candidates(council,state,state.v059Madame).map(candidate=>'<section class="v046-notice"><h3>'+escapeCouncil(candidate.label)+'</h3><p>Score de campagne '+candidate.base+' · effet des motions '+(candidate.motion>=0?'+':'')+candidate.motion+' · score soumis '+candidate.adjusted+'.</p><p>Prévision : '+candidate.forecast.for+' pour · '+candidate.forecast.against+' contre · '+candidate.forecast.abstain+' abstention(s).</p>'+(candidate.eligible?v027Button('Soumettre au vote : '+candidate.label,'c60:ratify',candidate.id,!!deny):'<p>Orientation non recevable dans l’équilibre actuel. Modifiez les motions ou choisissez une orientation issue de la projection.</p>')+'</section>').join('');
 }
 function councilPanel(container){
  syncCouncil();const council=state.v060Council,deny=councilBlocked(),esc=escapeCouncil;
  if(council.status==='locked'){container.innerHTML='<div class="p27-long"><p class="p27-kicker">ÉTATS GÉNÉRAUX</p><h2>Conseil régional</h2><p>Les six chapitres doivent être conclus avant toute convocation.</p></div>';return;}
  if(council.status==='available'){container.innerHTML='<div class="p27-long"><p class="p27-kicker">ÉTATS GÉNÉRAUX</p><h2>Conseil régional</h2><p>La projection M.A.D.A.M.E. indique <strong>'+esc(state.v059Madame.projection.label)+'</strong>. Une projection n’est pas une constitution.</p>'+v027Button('Convoquer les délégations','c60:convene','',!!deny)+'</div>';return;}
  if(council.status==='ratified'){
   const charter=pathByCouncil(council.charter);container.innerHTML='<div class="p27-long"><p class="p27-kicker">CHARTE RATIFIÉE</p><h2>'+esc(charter?.label||council.charter)+'</h2><p>Vote '+council.tally.for+' pour · '+council.tally.against+' contre · '+council.tally.abstain+' abstention(s) · légitimité '+council.legitimacy+'/100.</p>'+council.slides.map(slide=>'<section class="v046-notice"><h3>'+esc(slide.title)+'</h3><p>'+esc(slide.text)+'</p></section>').join('')+v027Button('Afficher l’épilogue régional','c60:ending')+'</div>';return;
  }
  container.innerHTML='<div class="p27-long"><p class="p27-kicker">ÉTATS GÉNÉRAUX DU MISTRAL</p><h2>Quatre motions avant la charte</h2><p>Projection initiale : <strong>'+esc(council.projectionAtCouncil?.label||state.v059Madame.projection.label)+'</strong>. Les motions peuvent être amendées jusqu’à une ratification réussie.</p>'+(deny?'<p>'+esc(deny)+'</p>':'')+motionPanel(council,deny)+candidatesPanel(council,deny)+(council.failedVotes.length?'<h3>Votes rejetés</h3>'+council.failedVotes.map(vote=>'<p>'+esc(pathByCouncil(vote.path)?.label||vote.path)+' : '+vote.for+' pour, '+vote.against+' contre, '+vote.abstain+' abstention(s).</p>').join(''):'')+'</div>';
 }
 if(typeof V027_SUBS!=='undefined'&&V027_SUBS.data)V027_SUBS.data.council='CONSEIL RÉGIONAL';
 const oldData=v027Data;v027Data=function(container){if(V027.sub==='council')return councilPanel(container);const result=oldData(...arguments);if(['france','madame','services'].includes(V027.sub)&&state.quest?.aubagneComplete)container.insertAdjacentHTML('beforeend','<section class="v046-notice"><h2>États généraux du Mistral</h2><p>Les six chartes locales peuvent désormais être transformées en règle commune.</p>'+v027Button('Ouvrir le conseil régional','jump','data:council')+'</section>');return result;};
 const oldDispatch=v027Dispatch;v027Dispatch=function(action,arg=''){
  if(typeof action!=='string'||!action.startsWith('c60:'))return oldDispatch(...arguments);if(!v027CanAct())return false;
  if(action==='c60:convene'){const plan=transactCouncil({type:'convene'});if(plan&&mode==='PIP')renderPipboy();return !!plan;}
  if(action==='c60:motion'){const[motion,choice]=String(arg).split('|'),plan=transactCouncil({type:'motion',motion,choice});if(plan&&mode==='PIP')renderPipboy();return !!plan;}
  if(action==='c60:ratify'){const plan=transactCouncil({type:'ratify',path:String(arg)});if(!plan)return false;if(plan.passed)return showEnding('regional');if(mode==='PIP')renderPipboy();return true;}
  if(action==='c60:ending')return showEnding('regional');
  return false;
 };
 const oldRows=v027QuestRows;v027QuestRows=function(){syncCouncil();if(state.v060Council.status==='locked')return oldRows(...arguments);const council=state.v060Council,done=council.status==='ratified',motionCount=Object.values(council.clauses).filter(Boolean).length;return oldRows(...arguments).concat([{id:'c60:council',name:'ÉTATS GÉNÉRAUX DU MISTRAL',stage:done?'done':'active',active:!done,text:done?`${pathByCouncil(council.charter)?.label||council.charter} ratifiée par ${council.tally.for} voix.`:council.status==='available'?'Parlez à Mireille pour convoquer les délégations.':`${motionCount}/4 motions adoptées.`,zone:null,steps:[['Six chartes locales conclues',!!state.quest.aubagneComplete],['Conseil convoqué',council.status!=='available'],['Quatre motions adoptées',motionCount===4],['Charte régionale ratifiée',done]],source:'États généraux / M.A.D.A.M.E.',badge:done?'✓':'',hint:'Ratification et épilogues des sept réseaux'}]);};
 const oldTrack=v027Track;v027Track=function(id){if(id==='c60:council'){toast(state.v060Council.status==='available'?'Retrouvez Mireille à Aubagne pour convoquer le conseil.':'Ouvrez DATA → CONSEIL RÉGIONAL pour poursuivre les motions.');return true;}return oldTrack(...arguments);};
 if(typeof V027_STATIONS!=='undefined')V027_STATIONS.council={name:'États généraux du Mistral',freq:'60.7',hint:'Motions, vote et ratification',available:()=>syncCouncil().status!=='locked',text:()=>MistralCouncil.bulletin(state.v060Council,state,state.v059Madame)};
 const previousAfter=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){if(typeof previousAfter==='function')previousAfter();globalThis.__MISTRAL_DEBUG??={};Object.assign(globalThis.__MISTRAL_DEBUG,{v060CouncilInfo:()=>clone(syncCouncil()),v060CouncilOpen:()=>v027Open('data','council'),v060CouncilConvene:()=>transactCouncil({type:'convene'}),v060CouncilMotion:(motion,choice)=>transactCouncil({type:'motion',motion,choice}),v060CouncilRatify:path=>transactCouncil({type:'ratify',path}),v060CouncilEnding:()=>showEnding('regional')});};
}
