/* Fallout: Mistral v0.59 — A-03, M.A.D.A.M.E. et registre civique.
   Ce module enrichit le prologue historique sans le dupliquer. Il transforme
   les preuves déjà produites par la campagne en état civique durable, calcule
   l'état des sept réseaux et projette les équilibres politiques possibles. */
const MistralMadame=(()=>{
 'use strict';
 const SCHEMA=1;
 const NETWORKS=[
  {id:'identite',label:'Identité',question:'Qui peut attester qu’une personne existe ?'},
  {id:'eau',label:'Eau',question:'Qui reçoit la ressource avant que la réserve soit vide ?'},
  {id:'sante',label:'Santé',question:'Le soin est-il un droit, une dette ou une cotisation ?'},
  {id:'transport',label:'Transport',question:'Qui peut circuler, et sous quelle preuve ?'},
  {id:'energie',label:'Énergie',question:'Qui accepte le risque nécessaire aux autres ?'},
  {id:'communication',label:'Communication',question:'Qui transforme un signal en vérité publique ?'},
  {id:'approvisionnement',label:'Approvisionnement',question:'Qui décide ce qui circule, attend ou reste au quai ?'}
 ];
 const ENDINGS=[
  {id:'charte_vivants',label:'Charte des Vivants'},
  {id:'republique_services',label:'République des Services'},
  {id:'continuite',label:'Continuité administrative'},
  {id:'federation',label:'Fédération des Communes'},
  {id:'travailleurs',label:'Gouvernement des travailleurs'},
  {id:'levant',label:'Autorité du Levant'},
  {id:'technocratie',label:'Technocratie atomique et contractuelle'},
  {id:'fragmentation',label:'Fragmentation régionale'}
 ];
 const EVIDENCE={
  body:'Présence corporelle constatée à A-03',
  deathNotice:'Avis de décès automatique 04-771-C',
  terminalTrace:'Trace du relais d’Aubagne à 05 h 57',
  a03Journal:'Journal des listes falsifiées d’A-03',
  odetteTestimony:'Témoignage d’Odette Ferraud',
  relayRecognition:'Présence provisoire reconnue par AUB-04',
  regionalSignatures:'Chaîne régionale des signatures CONCORDE',
  publicWitnesses:'Témoignages et registres communaux',
  hydraulicRegisters:'Registres reliant identité et droit à l’eau',
  visualArchives:'Images postérieures au décès administratif'
 };
 const PETITIONS={
  presence:{label:'Présence physique provisoire',text:'M.A.D.A.M.E. constate un corps vivant, mais refuse de remplacer seule le dossier régional.'},
  trace:{label:'Audit de la trace 05 h 57',text:'La décision extérieure est conservée avec son origine. Le décès ne peut plus être présenté comme une décision purement locale.'},
  plurality:{label:'Conservation des versions contradictoires',text:'L’avis de décès, le corps présent et les archives d’A-03 restent simultanément consultables. Aucune version ne peut effacer les autres sans audit.'}
 };
 const ODETTE={
  attestation:{label:'Attestation nominative',text:'Odette signe une attestation qui engage son nom et confirme votre présence devant le sas.'},
  protect:{label:'Témoignage protégé',text:'Odette confirme votre présence sans livrer les familles sauvées par les anciennes falsifications.'},
  contradiction:{label:'Copie contradictoire',text:'Le journal d’A-03 est joint au dossier. La falsification et les vies qu’elle a protégées restent visibles ensemble.'},
  silence:{label:'Départ sans attestation',text:'Vous quittez A-03 sans demander à Odette de devenir une nouvelle pièce du dossier.'}
 };
 const MILESTONES=new Set(['identity','routes','water','industry','marseille','aubagne']);
 const clamp=(value,min=0,max=100)=>Math.max(min,Math.min(max,Number.isFinite(Number(value))?Number(value):0));
 const copy=value=>value==null?value:JSON.parse(JSON.stringify(value));
 const own=(value,key)=>Object.prototype.hasOwnProperty.call(value||{},key);
 const blankEvidence=()=>Object.fromEntries(Object.keys(EVIDENCE).map(key=>[key,false]));
 const blankNetwork=definition=>({id:definition.id,label:definition.label,question:definition.question,access:20,legitimacy:20,coercion:50,resilience:25,controller:'Autorités fragmentées',reasons:[]});
 const blankScores=()=>Object.fromEntries(ENDINGS.map(ending=>[ending.id,0]));
 function fresh(){
  return{
   schema:SCHEMA,
   identity:{status:'registered',stage:'before_notice',terminalPetition:null,odetteChoice:null,relayMethod:null,chapterOutcome:null,contradiction:0,madamePressure:20,evidence:blankEvidence()},
   networks:Object.fromEntries(NETWORKS.map(definition=>[definition.id,blankNetwork(definition)])),
   scores:blankScores(),
   projection:{winner:'fragmentation',label:'Fragmentation régionale',alternate:null,alternateLabel:null,confidence:12,margin:0,state:'précoce',reasons:['Aucune décision régionale suffisante n’est encore enregistrée.']},
   journal:[]
  };
 }
 function sanitize(raw){
  const base=fresh(),input=raw&&typeof raw==='object'?raw:{};
  const identity=input.identity&&typeof input.identity==='object'?input.identity:{};
  const evidence=blankEvidence();
  for(const key of Object.keys(evidence))evidence[key]=identity.evidence?.[key]===true;
  base.identity={
   ...base.identity,
   status:['registered','declared_dead','contested','provisional','recognized','plural'].includes(identity.status)?identity.status:base.identity.status,
   stage:typeof identity.stage==='string'?identity.stage:base.identity.stage,
   terminalPetition:own(PETITIONS,identity.terminalPetition)?identity.terminalPetition:null,
   odetteChoice:own(ODETTE,identity.odetteChoice)?identity.odetteChoice:null,
   relayMethod:['repair','negotiate','falsify','force'].includes(identity.relayMethod)?identity.relayMethod:null,
   chapterOutcome:['continuity','federation','workers','fragment'].includes(identity.chapterOutcome)?identity.chapterOutcome:null,
   contradiction:clamp(identity.contradiction,0,10),
   madamePressure:clamp(identity.madamePressure),
   evidence
  };
  if(Array.isArray(input.journal))base.journal=input.journal.filter(entry=>entry&&typeof entry==='object'&&typeof entry.type==='string').slice(-96).map(entry=>({type:String(entry.type).slice(0,48),choice:entry.choice==null?null:String(entry.choice).slice(0,64),area:entry.area==null?null:String(entry.area).slice(0,32),at:Math.max(0,Number(entry.at)||0)}));
  return base;
 }
 function campaignParts(campaign={}){
  return{
   quest:campaign.quest||{},
   flags:campaign.flags||{},
   notes:(campaign.flags||{}).notes||{},
   services:campaign.v054Services?.quests||{},
   continuity:campaign.v053Lore?.quests||{},
   rep:campaign.rep||{},
   playTime:Number(campaign.playTime)||0
  };
 }
 function adjust(networks,id,delta={},controller=null,reason=null){
  const network=networks[id];if(!network)return;
  for(const metric of['access','legitimacy','coercion','resilience'])if(own(delta,metric))network[metric]=clamp(network[metric]+Number(delta[metric]||0));
  if(controller)network.controller=controller;
  if(reason&&!network.reasons.includes(reason))network.reasons.push(reason);
 }
 function addScore(scores,reasonMap,id,amount,reason){
  if(!own(scores,id)||!Number.isFinite(Number(amount)))return;
  scores[id]+=Number(amount);
  if(reason){reasonMap[id]??=[];reasonMap[id].push({weight:Number(amount),text:reason});}
 }
 function markEvidence(identity,parts){
  const {quest,flags,notes}=parts,evidence=identity.evidence;
  if(flags.rationDenied){evidence.body=true;evidence.deathNotice=true;identity.status='declared_dead';identity.stage='declared_dead';}
  if(flags.archiveMemo)evidence.terminalTrace=true;
  if(notes['journal-a03'])evidence.a03Journal=true;
  if(identity.odetteChoice&&identity.odetteChoice!=='silence')evidence.odetteTestimony=true;
  if(flags.relayPowered||quest.relayOutcome){evidence.relayRecognition=true;identity.relayMethod=quest.relayOutcome||identity.relayMethod;identity.status='provisional';identity.stage='relay_recognized';}
  if(notes['marseille-proof']||flags.marseilleArchiveRead)evidence.regionalSignatures=true;
  if(quest.treilleOutcome||quest.cadastreOutcome||notes['yanis-testimony']||notes['list-anonymized'])evidence.publicWitnesses=true;
  if(quest.waterOutcome||flags.longchampArchiveRead)evidence.hydraulicRegisters=true;
  if(quest.cinemaOutcome||flags.cinemaResolved)evidence.visualArchives=true;
  if(quest.main>=5&&!quest.mainComplete)identity.stage='regional_inquiry';
  if(quest.mainComplete||quest.finalOutcome){identity.chapterOutcome=quest.finalOutcome||identity.chapterOutcome;identity.status=identity.chapterOutcome==='fragment'?'plural':'recognized';identity.stage='regional_verdict';}
  let contradiction=0;
  if(evidence.body&&evidence.deathNotice)contradiction+=2;
  for(const key of['terminalTrace','a03Journal','odetteTestimony','relayRecognition','regionalSignatures','publicWitnesses','hydraulicRegisters','visualArchives'])if(evidence[key])contradiction+=1;
  identity.contradiction=clamp(contradiction,0,10);
 }
 function applyIdentity(result,parts,reasonMap){
  const {identity,networks,scores}=result,e=identity.evidence;
  if(e.deathNotice){adjust(networks,'identite',{access:-10,legitimacy:-5,coercion:20},'CONCORDE — dossier de décès','Le dossier 04-771-C suspend ration, soin et passage.');addScore(scores,reasonMap,'continuite',2,'Le décès initial résulte d’une décision centralisée.');}
  if(e.body)adjust(networks,'identite',{legitimacy:6,resilience:2},null,'Le corps présent contredit le statut enregistré.');
  if(e.terminalTrace)adjust(networks,'identite',{legitimacy:8,coercion:-4,resilience:5},null,'La trace extérieure de 05 h 57 est conservée.');
  if(e.a03Journal)adjust(networks,'identite',{legitimacy:8,resilience:7},null,'Le journal d’A-03 documente les falsifications protectrices.');
  if(e.odetteTestimony)adjust(networks,'identite',{access:5,legitimacy:8,coercion:-3},null,'Odette devient témoin de la contradiction.');
  if(e.relayRecognition)adjust(networks,'identite',{access:20,legitimacy:10,resilience:10},'Relais AUB-04 et preuves locales','AUB-04 reconnaît une présence provisoire.');
  if(e.regionalSignatures)adjust(networks,'identite',{legitimacy:10,coercion:-5,resilience:8},null,'La chaîne de signatures régionales est visible.');
  if(e.publicWitnesses)adjust(networks,'identite',{access:12,legitimacy:12,coercion:-8,resilience:10},'Registres et témoins pluriels','Les preuves communales complètent le registre central.');
  if(e.hydraulicRegisters)adjust(networks,'identite',{access:5,legitimacy:5},null,'Les droits hydrauliques révèlent les effets matériels d’un effacement.');
  if(e.visualArchives)adjust(networks,'identite',{legitimacy:10,resilience:8},null,'Les images datées prouvent une vie postérieure au décès officiel.');
  if(identity.terminalPetition==='presence'){adjust(networks,'identite',{access:7,legitimacy:4},null,'M.A.D.A.M.E. conserve une preuve corporelle provisoire.');addScore(scores,reasonMap,'charte_vivants',2,'La présence physique devient une preuve opposable.');}
  if(identity.terminalPetition==='trace'){adjust(networks,'identite',{legitimacy:8,coercion:-4,resilience:6},null,'L’origine de la décision est rendue vérifiable.');addScore(scores,reasonMap,'charte_vivants',3,'La décision conserve sa provenance et peut être contestée.');addScore(scores,reasonMap,'federation',1,'Le relais local peut contredire le centre.');}
  if(identity.terminalPetition==='plurality'){adjust(networks,'identite',{legitimacy:10,coercion:-10,resilience:8},'Registre contradictoire','Plusieurs versions doivent rester consultables.');addScore(scores,reasonMap,'charte_vivants',5,'Aucune base unique ne peut effacer les autres preuves.');addScore(scores,reasonMap,'fragmentation',1,'La pluralité reste difficile à arbitrer.');}
  if(identity.odetteChoice==='attestation'){addScore(scores,reasonMap,'charte_vivants',3,'Odette engage publiquement son nom pour une personne effacée.');}
  if(identity.odetteChoice==='protect'){adjust(networks,'identite',{coercion:-5},null,'Le témoignage protège les familles déjà sauvées par les falsifications.');addScore(scores,reasonMap,'federation',3,'Les communautés gardent une part de leurs preuves hors du centre.');addScore(scores,reasonMap,'charte_vivants',1,'Le droit d’exister n’exige pas de livrer tous les noms.');}
  if(identity.odetteChoice==='contradiction'){adjust(networks,'identite',{legitimacy:8,resilience:8},null,'La copie contradictoire empêche l’effacement de l’histoire d’A-03.');addScore(scores,reasonMap,'charte_vivants',4,'La falsification et les vies protégées restent visibles ensemble.');addScore(scores,reasonMap,'federation',2,'Les archives locales conservent leur autonomie.');}
  const relay=identity.relayMethod;
  if(relay==='repair'){adjust(networks,'identite',{legitimacy:6,resilience:12},'CONCORDE réparé sous contrôle local','La validation est rétablie sans réécrire les noms.');addScore(scores,reasonMap,'republique_services',2,'La maintenance rend un service vérifiable sans supprimer les archives.');}
  if(relay==='negotiate'){adjust(networks,'identite',{access:12,legitimacy:12,coercion:-5},'Procédure 17-B et témoins locaux','La présence physique devient une exception reconnue.');addScore(scores,reasonMap,'charte_vivants',3,'La procédure 17-B reconnaît la présence avant le registre définitif.');addScore(scores,reasonMap,'continuite',2,'La contestation utilise encore le droit de CONCORDE.');}
  if(relay==='falsify'){adjust(networks,'identite',{access:10,legitimacy:-4,coercion:-8,resilience:-2},'Sceaux concurrents','Une signature valide remplace provisoirement le décès.');addScore(scores,reasonMap,'fragmentation',3,'Les sceaux concurrents affaiblissent toute source unique de vérité.');addScore(scores,reasonMap,'federation',1,'Une autorité locale peut résister au centre.');}
  if(relay==='force'){adjust(networks,'identite',{access:7,legitimacy:-10,coercion:5,resilience:-8},'Relais forcé','Le service revient sans règle de recours stable.');addScore(scores,reasonMap,'fragmentation',4,'La force rétablit le service mais ne résout pas la légitimité.');}
  const final=identity.chapterOutcome;
  if(final==='continuity'){adjust(networks,'identite',{access:20,legitimacy:10,coercion:25,resilience:22},'Direction de la Continuité et M.A.D.A.M.E.','Le réseau central devient l’arbitre régional.');addScore(scores,reasonMap,'continuite',14,'Le premier conseil confie l’identité à la Continuité.');}
  if(final==='federation'){adjust(networks,'identite',{access:30,legitimacy:30,coercion:-15,resilience:24},'Fédération des communes','Les preuves locales et régionales se reconnaissent mutuellement.');addScore(scores,reasonMap,'federation',13,'Le premier conseil fédère les communes et leurs registres.');addScore(scores,reasonMap,'charte_vivants',3,'La reconnaissance repose sur plusieurs autorités contestables.');}
  if(final==='workers'){adjust(networks,'identite',{access:22,legitimacy:22,coercion:-2,resilience:30},'Travailleurs des réseaux','Ceux qui entretiennent les services valident les dossiers.');addScore(scores,reasonMap,'travailleurs',14,'Le premier conseil remet le réseau à ceux qui le font fonctionner.');}
  if(final==='fragment'){adjust(networks,'identite',{access:12,legitimacy:12,coercion:-25,resilience:-12},'Registres indépendants','Aucune autorité ne peut effacer toute la région.');addScore(scores,reasonMap,'fragmentation',13,'Le premier conseil refuse une autorité régionale unique.');addScore(scores,reasonMap,'charte_vivants',2,'La pluralité protège contre l’effacement central, sans garantir les services.');}
 }
 function applyNetworkChoices(result,parts,reasonMap){
  const {quest,flags,services,continuity}=parts,{networks,scores}=result;
  const route=quest.routesOutcome;
  if(route==='public'){adjust(networks,'transport',{access:38,legitimacy:25,coercion:-5,resilience:22},'Service public régional','Les voies sont un service commun.');addScore(scores,reasonMap,'republique_services',8,'Les routes deviennent un service public régional.');}
  if(route==='cooperative'){adjust(networks,'transport',{access:28,legitimacy:32,coercion:-12,resilience:28},'Coopératives d’entretien','Les équipes contrôlent les tronçons qu’elles entretiennent.');addScore(scores,reasonMap,'travailleurs',6,'Les équipes gouvernent les routes entretenues.');addScore(scores,reasonMap,'federation',5,'Les coopératives coordonnent plusieurs territoires.');}
  if(route==='concessions'){adjust(networks,'transport',{access:22,legitimacy:-4,coercion:15,resilience:15},'Concessions et péages','L’expansion dépend de contrats payants.');addScore(scores,reasonMap,'technocratie',4,'Les concessions transforment le passage en contrat mesuré.');}
  if(route==='local'){adjust(networks,'transport',{access:14,legitimacy:18,coercion:-12,resilience:-4},'Communautés locales','Chaque territoire contrôle son passage.');addScore(scores,reasonMap,'federation',5,'Les communautés gardent la souveraineté de leurs voies.');addScore(scores,reasonMap,'fragmentation',3,'Les règles de passage restent discontinues.');}
  const water=quest.waterOutcome;
  if(water==='right'){adjust(networks,'eau',{access:45,legitimacy:36,coercion:-22,resilience:20},'Droit régional opposable','L’accès vital prime sur le dossier.');addScore(scores,reasonMap,'charte_vivants',9,'L’eau devient un droit opposable à toute administration.');addScore(scores,reasonMap,'republique_services',6,'Le réseau de l’eau reçoit une obligation universelle.');}
  if(water==='federated'){adjust(networks,'eau',{access:34,legitimacy:32,coercion:-12,resilience:28},'Fédération des bassins','Communes et travailleurs contrôlent les bassins.');addScore(scores,reasonMap,'federation',8,'Les bassins sont fédérés par les communes et les équipes.');addScore(scores,reasonMap,'travailleurs',3,'Les mainteneurs siègent dans la gestion de l’eau.');}
  if(water==='priority'){adjust(networks,'eau',{access:24,legitimacy:14,coercion:14,resilience:22},'Service des eaux à quotas publics','Les besoins sont classés par priorité.');addScore(scores,reasonMap,'republique_services',4,'Le service des eaux publie ses priorités.');addScore(scores,reasonMap,'continuite',3,'Les quotas exigent un arbitre régional fort.');}
  if(water==='concessions'){adjust(networks,'eau',{access:20,legitimacy:-5,coercion:16,resilience:18},'Concessions hydrauliques','Les extensions dépendent d’opérateurs contractuels.');addScore(scores,reasonMap,'technocratie',5,'Le réseau de l’eau est piloté par contrats et capacité.');}
  const industry=quest.industryOutcome;
  if(industry==='public'){adjust(networks,'approvisionnement',{access:32,legitimacy:23,coercion:-3,resilience:25},'Service public du littoral','Chantiers, quais et secours publient leurs obligations.');adjust(networks,'energie',{access:18,legitimacy:14,coercion:-3,resilience:18},'Service public du littoral');addScore(scores,reasonMap,'republique_services',7,'Le littoral devient un service public régional.');}
  if(industry==='federation'){adjust(networks,'approvisionnement',{access:28,legitimacy:34,coercion:-12,resilience:30},'Fédération ouvrière et maritime','Travailleurs, ports et communes partagent les décisions.');adjust(networks,'energie',{access:12,legitimacy:18,coercion:-7,resilience:20},'Fédération ouvrière et maritime');addScore(scores,reasonMap,'travailleurs',8,'La production est gouvernée avec les équipes.');addScore(scores,reasonMap,'federation',6,'Ports et communes maritimes partagent l’autorité.');}
  if(industry==='arsenal'){adjust(networks,'approvisionnement',{access:18,legitimacy:6,coercion:20,resilience:30},'Arsenal de La Ciotat','L’Arsenal concentre la production et les quais.');adjust(networks,'energie',{access:12,legitimacy:5,coercion:18,resilience:24},'Arsenal de La Ciotat');addScore(scores,reasonMap,'technocratie',6,'L’Arsenal concentre les outils et la capacité industrielle.');addScore(scores,reasonMap,'travailleurs',2,'Les sièges ouvriers limitent partiellement l’Arsenal.');}
  if(industry==='francs'){adjust(networks,'approvisionnement',{access:25,legitimacy:17,coercion:0,resilience:24},'Francs du Large sous charte','Les secours et tarifs dépendent des équipages.');adjust(networks,'transport',{access:14,legitimacy:10,coercion:-2,resilience:16},'Francs du Large sous charte');addScore(scores,reasonMap,'federation',3,'Les équipages conservent une autonomie maritime.');addScore(scores,reasonMap,'fragmentation',2,'La route bleue dépend encore d’acteurs autonomes.');}
  const city=quest.marseilleOutcome;
  if(city==='commune'){for(const id of['sante','transport','communication'])adjust(networks,id,{access:24,legitimacy:30,coercion:-13,resilience:18},'Commune de la Rade','Les quartiers gouvernent les services urbains.');addScore(scores,reasonMap,'federation',9,'Marseille choisit les assemblées de quartier.');}
  if(city==='public'){for(const id of['sante','transport','communication'])adjust(networks,id,{access:32,legitimacy:23,coercion:-2,resilience:23},'Service public municipal','Images, billets, soins et alertes ont des obligations universelles.');addScore(scores,reasonMap,'republique_services',9,'Marseille unifie ses services sous obligations universelles.');}
  if(city==='federation'){for(const id of['sante','transport','communication'])adjust(networks,id,{access:28,legitimacy:35,coercion:-12,resilience:26},'Fédération des quartiers et travailleurs','Les services sont reliés sans autorité unique.');addScore(scores,reasonMap,'federation',10,'Marseille fédère quartiers, travailleurs et Veilleurs.');addScore(scores,reasonMap,'charte_vivants',3,'Les droits urbains reposent sur plusieurs recours.');}
  if(city==='concessions'){for(const id of['sante','transport','communication'])adjust(networks,id,{access:18,legitimacy:0,coercion:14,resilience:18},'Concessions urbaines auditées','Les contrats financent les services urbains.');addScore(scores,reasonMap,'technocratie',6,'Marseille confie ses services à des concessions auditées.');}
  const aubagne=quest.aubagneOutcome;
  if(aubagne==='federation'){for(const id of['identite','transport','communication','approvisionnement'])adjust(networks,id,{access:18,legitimacy:28,coercion:-10,resilience:22},'Fédération du pays d’Aubagne','Communes, artisans et Vigies partagent les règles.');addScore(scores,reasonMap,'federation',10,'Le pays d’Aubagne adopte une fédération de communes.');}
  if(aubagne==='public'){for(const id of['identite','transport','communication','approvisionnement'])adjust(networks,id,{access:25,legitimacy:20,coercion:0,resilience:25},'Service public territorial','Le territoire coordonne noms, évacuations, filtres et secours.');addScore(scores,reasonMap,'republique_services',10,'Aubagne coordonne ses réseaux comme services publics.');}
  if(aubagne==='cooperative'){for(const id of['identite','transport','communication','approvisionnement'])adjust(networks,id,{access:20,legitimacy:28,coercion:-10,resilience:28},'Coopératives d’ateliers et de quartiers','Les coopératives gouvernent les réseaux du territoire.');addScore(scores,reasonMap,'travailleurs',10,'Aubagne choisit les coopératives d’ateliers et de quartiers.');}
  if(aubagne==='concessions'){for(const id of['identite','transport','communication','approvisionnement'])adjust(networks,id,{access:16,legitimacy:0,coercion:14,resilience:18},'Concessions territoriales auditées','Les secours dépendent de contrats financés.');addScore(scores,reasonMap,'technocratie',6,'Aubagne finance ses réseaux par concessions auditées.');}
  const health=services.carte_verte?.outcome;
  if(health==='urgence_universelle'){adjust(networks,'sante',{access:26,legitimacy:22,coercion:-15,resilience:12},'La Sociale et relais d’urgence','Le soin précède la vérification d’identité.');addScore(scores,reasonMap,'charte_vivants',5,'La Sociale reconnaît un soin avant tout dossier.');addScore(scores,reasonMap,'republique_services',3,'Une obligation d’urgence est confiée au réseau de santé.');}
  if(health==='cotisation_locale'){adjust(networks,'sante',{access:20,legitimacy:18,coercion:-4,resilience:20},'Caisse locale auditée','La caisse publie ses entrées et sorties.');addScore(scores,reasonMap,'republique_services',4,'La santé devient un service financé et auditable.');addScore(scores,reasonMap,'federation',2,'La caisse reste sous contrôle local.');}
  const rail=services.terminus_humain?.outcome;
  if(rail==='quai_humain'){adjust(networks,'transport',{access:22,legitimacy:22,coercion:-15,resilience:10},'Aiguilleurs et quai humain','Les absents de l’Horloge disposent d’un accueil.');addScore(scores,reasonMap,'charte_vivants',4,'Le quai reconnaît les voyageurs que l’Horloge efface.');}
  if(rail==='horaire_manuel'){adjust(networks,'transport',{access:15,legitimacy:20,coercion:-8,resilience:24},'Registre manuel des Aiguilleurs','Un arrêt local peut contredire l’Horloge.');addScore(scores,reasonMap,'republique_services',4,'Le rail conserve un arrêt manuel et une preuve contradictoire.');addScore(scores,reasonMap,'federation',2,'Les relais locaux peuvent contredire le centre.');}
  const atom=services.dose_collective?.outcome;
  if(atom==='dosimetres_partages'){adjust(networks,'energie',{access:14,legitimacy:27,coercion:-17,resilience:18},'Commissariat sous mesure contradictoire','Les habitants vérifient les doses officielles.');addScore(scores,reasonMap,'charte_vivants',3,'Les mesures atomiques deviennent contestables.');addScore(scores,reasonMap,'technocratie',1,'Le Commissariat conserve son expertise, mais pas le monopole de la mesure.');}
  if(atom==='cordon_civil'){adjust(networks,'energie',{access:8,legitimacy:12,coercion:-7,resilience:12},'Cordon civil témoin','Les seuils de retrait sont consignés publiquement.');adjust(networks,'sante',{access:14,legitimacy:12,coercion:-5,resilience:8},'Réserve civile d’exposition');addScore(scores,reasonMap,'republique_services',4,'Santé et énergie partagent un protocole civil.');}
  const sea=services.pavillon_secours?.outcome;
  if(sea==='corridor_civil'){adjust(networks,'transport',{access:18,legitimacy:15,coercion:-10,resilience:10},'Corridor civil de secours','Le sauvetage précède l’immatriculation.');adjust(networks,'approvisionnement',{access:18,legitimacy:15,coercion:-8,resilience:10},'Corridor civil de secours');addScore(scores,reasonMap,'charte_vivants',4,'Les naufragés sont reconnus avant leur pavillon.');addScore(scores,reasonMap,'federation',2,'La halte conserve le contrôle du protocole maritime.');}
  if(sea==='convoi_enregistre'){adjust(networks,'transport',{access:12,legitimacy:18,coercion:2,resilience:18},'Manifeste maritime partagé','Le manifeste appartient aussi aux équipages et au relais.');adjust(networks,'approvisionnement',{access:14,legitimacy:20,coercion:3,resilience:18},'Manifeste maritime partagé');addScore(scores,reasonMap,'levant',5,'L’Amirauté obtient un cadre d’enregistrement des secours.');addScore(scores,reasonMap,'republique_services',2,'Le manifeste reste contradictoire et partagé.');}
  const identityQuests=['cendres','formulaire','attente'];
  if(identityQuests.some(id=>continuity[id]?.outcome)){adjust(networks,'identite',{access:7,legitimacy:9,coercion:-4,resilience:6},null,'Les dossiers des relais ajoutent des preuves et des recours.');addScore(scores,reasonMap,'charte_vivants',2,'Les relais reconnaissent attestations et contradictions.');}
  if(continuity.signaux?.outcome){adjust(networks,'communication',{access:12,legitimacy:14,coercion:-8,resilience:12},'Canal 13 et Vigies','Les limites des observations sont diffusées.');addScore(scores,reasonMap,'republique_services',2,'Les alertes conservent leurs incertitudes.');}
  if(continuity.partage?.outcome){adjust(networks,'eau',{access:14,legitimacy:12,coercion:-8,resilience:8},'Tables d’accueil des Communes','Une réserve d’eau ne dépend pas d’une carte de naissance.');addScore(scores,reasonMap,'charte_vivants',3,'Les Communes séparent l’eau de l’identité administrative.');}
  if(continuity.passage_libre?.outcome){adjust(networks,'transport',{access:14,legitimacy:12,coercion:-10,resilience:8},'Relais sans péage','Les signes de passage ne deviennent pas une taxe.');addScore(scores,reasonMap,'federation',2,'Les relais locaux garantissent le passage sans péage.');}
  if(quest.signalOutcome==='public'){adjust(networks,'communication',{access:20,legitimacy:18,coercion:-12,resilience:12},'Relais public de la Garde','Toutes les alertes vitales conservent leur source.');addScore(scores,reasonMap,'republique_services',4,'Les alertes vitales deviennent un service universel.');}
  if(quest.signalOutcome==='distributed'){adjust(networks,'communication',{access:17,legitimacy:24,coercion:-15,resilience:22},'Clés distribuées aux quartiers','Plusieurs équipes peuvent émettre.');addScore(scores,reasonMap,'federation',4,'Les quartiers partagent les clés de diffusion.');}
  if(quest.signalOutcome==='controlled'){adjust(networks,'communication',{access:10,legitimacy:12,coercion:18,resilience:20},'Contrôle central audité','Une autorité classe les priorités.');addScore(scores,reasonMap,'continuite',4,'Le relais d’alerte reste centralisé et audité.');}
  if(quest.signalOutcome==='subscription'){adjust(networks,'communication',{access:8,legitimacy:-5,coercion:15,resilience:12},'Abonnements prioritaires','Les alertes commerciales passent avant certaines urgences.');addScore(scores,reasonMap,'technocratie',4,'Le réseau d’alerte dépend de contrats prioritaires.');}
  if(flags.firewatchActive&&quest.firewatchOutcome==='command'){adjust(networks,'communication',{access:8,legitimacy:5,coercion:14,resilience:18},'Commandement de crise','La vigie centralise temporairement les ordres.');addScore(scores,reasonMap,'continuite',3,'Aubagne accepte un commandement central pendant la crise.');}
 }
 function finalize(result,parts,reasonMap){
  const {networks,scores,identity}=result;
  const values=Object.values(networks);
  const average=metric=>values.reduce((sum,network)=>sum+network[metric],0)/Math.max(1,values.length);
  const avgAccess=average('access'),avgLegitimacy=average('legitimacy'),avgCoercion=average('coercion'),avgResilience=average('resilience');
  if(avgAccess>=58&&avgLegitimacy>=55&&avgCoercion<=45){addScore(scores,reasonMap,'charte_vivants',5,'Plusieurs réseaux combinent accès, recours et faible coercition.');addScore(scores,reasonMap,'republique_services',4,'Les services disposent d’obligations communes et vérifiables.');}
  if(avgResilience>=58)addScore(scores,reasonMap,'republique_services',4,'Les sept réseaux résistent aux ruptures locales.');
  if(avgCoercion>=65){addScore(scores,reasonMap,'continuite',5,'La plupart des réseaux reposent sur une autorité coercitive.');addScore(scores,reasonMap,'technocratie',3,'Les seuils et contrats dominent les recours humains.');}
  const controllers=values.map(network=>network.controller.toLowerCase());
  const federated=controllers.filter(text=>/fédér|commune|quartier|coopérative|relais/.test(text)).length;
  const workers=controllers.filter(text=>/travail|ouvrier|atelier|arsenal/.test(text)).length;
  const publicServices=controllers.filter(text=>/service public|territorial|municipal/.test(text)).length;
  if(federated>=3)addScore(scores,reasonMap,'federation',4,'Plusieurs réseaux sont gouvernés par des autorités locales coordonnées.');
  if(workers>=2)addScore(scores,reasonMap,'travailleurs',4,'Plusieurs réseaux dépendent directement de leurs équipes.');
  if(publicServices>=2)addScore(scores,reasonMap,'republique_services',4,'Plusieurs réseaux sont déjà organisés comme services publics.');
  const completedChapters=['mainComplete','routesComplete','waterComplete','industryComplete','marseilleComplete','aubagneComplete'].filter(key=>parts.quest[key]).length;
  const completedServices=Object.values(parts.services).filter(quest=>quest?.outcome).length;
  const evidenceCount=Object.values(identity.evidence).filter(Boolean).length;
  if(completedChapters<=1&&completedServices===0)addScore(scores,reasonMap,'fragmentation',2,'La plupart des réseaux n’ont pas encore de règle commune.');
  for(const id of Object.keys(scores))scores[id]=Math.round(scores[id]*100)/100;
  const ranked=ENDINGS.map((ending,index)=>({...ending,score:scores[ending.id],index})).sort((a,b)=>b.score-a.score||a.index-b.index);
  const top=ranked[0],second=ranked[1],confidence=Math.round(clamp(12+completedChapters*11+completedServices*5+evidenceCount*2));
  const margin=Math.round((top.score-second.score)*100)/100;
  const reasonEntries=(reasonMap[top.id]||[]).sort((a,b)=>Math.abs(b.weight)-Math.abs(a.weight));
  const reasons=[];for(const entry of reasonEntries){if(entry.weight<=0||reasons.includes(entry.text))continue;reasons.push(entry.text);if(reasons.length>=5)break;}
  if(!reasons.length)reasons.push('Les décisions disponibles ne dessinent pas encore une majorité institutionnelle stable.');
  result.projection={winner:top.id,label:top.label,alternate:second.id,alternateLabel:second.label,confidence,margin,state:confidence<35?'précoce':margin<3?'contestée':'dominante',reasons};
  identity.madamePressure=clamp(20+(identity.status==='declared_dead'?25:0)+(identity.chapterOutcome==='continuity'?25:0)+(identity.relayMethod==='force'?10:0)-(identity.terminalPetition==='plurality'?12:0)-(identity.chapterOutcome==='fragment'?15:0)+avgCoercion*.25);
  for(const network of values){network.access=Math.round(clamp(network.access));network.legitimacy=Math.round(clamp(network.legitimacy));network.coercion=Math.round(clamp(network.coercion));network.resilience=Math.round(clamp(network.resilience));network.reasons=network.reasons.slice(-4);}
  return result;
 }
 function synchronize(raw,campaign={}){
  const ledger=sanitize(raw),parts=campaignParts(campaign),networks=Object.fromEntries(NETWORKS.map(definition=>[definition.id,blankNetwork(definition)])),scores=blankScores(),reasonMap={};
  ledger.networks=networks;ledger.scores=scores;
  markEvidence(ledger.identity,parts);
  applyIdentity(ledger,parts,reasonMap);
  applyNetworkChoices(ledger,parts,reasonMap);
  return finalize(ledger,parts,reasonMap);
 }
 function reduce(raw,action={},campaign={}){
  const ledger=sanitize(raw),failure=reason=>({ok:false,reason,ledger:synchronize(ledger,campaign)}),at=Math.max(0,Number(action.at??campaign.playTime)||0);
  if(action.type==='notice'){
   ledger.identity.evidence.body=true;ledger.identity.evidence.deathNotice=true;ledger.identity.status='declared_dead';ledger.identity.stage='declared_dead';
   if(!ledger.journal.some(entry=>entry.type==='notice'))ledger.journal.push({type:'notice',choice:null,area:'identity',at});
   return{ok:true,ledger:synchronize(ledger,campaign),notice:'Le décès administratif et la présence corporelle sont conservés comme deux faits contradictoires.'};
  }
  if(action.type==='petition'){
   if(!own(PETITIONS,action.choice))return failure('Requête inconnue.');
   if(ledger.identity.terminalPetition)return failure('Une requête contradictoire est déjà attachée au dossier A-03.');
   ledger.identity.terminalPetition=action.choice;
   if(action.choice==='presence')ledger.identity.evidence.body=true;
   if(action.choice==='trace')ledger.identity.evidence.terminalTrace=true;
   if(action.choice==='plurality'){ledger.identity.evidence.deathNotice=true;ledger.identity.evidence.a03Journal=true;}
   ledger.journal.push({type:'petition',choice:action.choice,area:'identity',at});
   return{ok:true,ledger:synchronize(ledger,campaign),notice:PETITIONS[action.choice].text};
  }
  if(action.type==='odette'){
   if(!own(ODETTE,action.choice))return failure('Décision d’Odette inconnue.');
   if(ledger.identity.odetteChoice)return failure('Le témoignage d’Odette a déjà une forme définitive.');
   ledger.identity.odetteChoice=action.choice;if(action.choice!=='silence')ledger.identity.evidence.odetteTestimony=true;
   ledger.journal.push({type:'odette',choice:action.choice,area:'identity',at});
   return{ok:true,ledger:synchronize(ledger,campaign),notice:ODETTE[action.choice].text};
  }
  if(action.type==='relay'){
   if(!['repair','negotiate','falsify','force'].includes(action.choice))return failure('Méthode de relais inconnue.');
   ledger.identity.relayMethod=action.choice;ledger.identity.evidence.relayRecognition=true;ledger.identity.status='provisional';ledger.identity.stage='relay_recognized';
   if(!ledger.journal.some(entry=>entry.type==='relay'&&entry.choice===action.choice))ledger.journal.push({type:'relay',choice:action.choice,area:'identity',at});
   return{ok:true,ledger:synchronize(ledger,campaign),notice:'La méthode de reconnaissance du relais AUB-04 est conservée.'};
  }
  if(action.type==='chapter'){
   if(!['continuity','federation','workers','fragment'].includes(action.choice))return failure('Conclusion identitaire inconnue.');
   ledger.identity.chapterOutcome=action.choice;ledger.identity.status=action.choice==='fragment'?'plural':'recognized';ledger.identity.stage='regional_verdict';
   if(!ledger.journal.some(entry=>entry.type==='chapter'&&entry.area==='identity'))ledger.journal.push({type:'chapter',choice:action.choice,area:'identity',at});
   return{ok:true,ledger:synchronize(ledger,campaign),notice:'La conclusion du premier conseil est intégrée au registre civique.'};
  }
  if(action.type==='milestone'){
   if(!MILESTONES.has(action.area))return failure('Réseau de campagne inconnu.');
   const key=String(action.choice||'').slice(0,64);
   if(!ledger.journal.some(entry=>entry.type==='milestone'&&entry.area===action.area&&entry.choice===key))ledger.journal.push({type:'milestone',choice:key,area:action.area,at});
   return{ok:true,ledger:synchronize(ledger,campaign),notice:'La décision régionale est intégrée à la projection.'};
  }
  if(action.type==='refresh')return{ok:true,ledger:synchronize(ledger,campaign),notice:'Registre civique recalculé.'};
  return failure('Action civique inconnue.');
 }
 function evidenceList(raw,campaign={}){const ledger=synchronize(raw,campaign);return Object.entries(ledger.identity.evidence).map(([id,active])=>({id,label:EVIDENCE[id],active}));}
 function bulletin(raw,campaign={}){
  const ledger=synchronize(raw,campaign),identity=ledger.identity,projection=ledger.projection;
  if(identity.status==='registered'&&!identity.evidence.deathNotice)return'M.A.D.A.M.E. — aucun conflit d’identité actif dans le registre local.';
  if(identity.status==='declared_dead')return`M.A.D.A.M.E. — dossier 04-771-C déclaré mort. Contradictions conservées : ${identity.contradiction}/10. Une présence physique ne constitue pas encore une autorité régionale.`;
  if(identity.status==='provisional')return`M.A.D.A.M.E. — présence provisoire reconnue par AUB-04. Méthode : ${identity.relayMethod||'non précisée'}. Projection institutionnelle : ${projection.label}, confiance ${projection.confidence} %.`;
  return`M.A.D.A.M.E. — statut ${identity.status}. Projection institutionnelle : ${projection.label}, confiance ${projection.confidence} %, marge ${projection.margin}.`;
 }
 return{SCHEMA,NETWORKS:copy(NETWORKS),ENDINGS:copy(ENDINGS),EVIDENCE:copy(EVIDENCE),PETITIONS:copy(PETITIONS),ODETTE:copy(ODETTE),fresh,sanitize,synchronize,reduce,evidenceList,bulletin};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralMadame;

if(typeof baseState==='function'){
 const clone=value=>JSON.parse(JSON.stringify(value));
 const oldBase=baseState;baseState=function(){const value=oldBase();value.v059Madame=MistralMadame.fresh();return value;};
 const oldMigrate=migrateState;migrateState=function(input={}){const value=oldMigrate(input);value.v059Madame=MistralMadame.synchronize(input.v059Madame,value);return value;};
 state=migrateState(state);
 function restoreOwner(owner,snapshot){if(state!==owner)return;for(const key of Object.keys(owner))if(!Object.prototype.hasOwnProperty.call(snapshot,key))delete owner[key];Object.assign(owner,snapshot);}
 function notifyCivic(message){if(typeof V027!=='undefined')V027.message=message;if(typeof toast==='function')toast(message,'bad');return false;}
 function transactCivic(action,mutate=null){
  const owner=state,snapshot=clone(owner),plan=MistralMadame.reduce(owner.v059Madame,{...action,at:owner.playTime},owner);
  if(!plan.ok)return notifyCivic(plan.reason);
  try{if(typeof mutate==='function')mutate(owner);owner.v059Madame=MistralMadame.synchronize(plan.ledger,owner);if(state!==owner||saveGame(false)===false)throw Error('Le registre civique ne peut pas être sauvegardé.');}
  catch(error){restoreOwner(owner,snapshot);return notifyCivic((error?.message||'Écriture refusée.')+' Opération annulée.');}
  if(typeof updateQuestUI==='function')updateQuestUI(true);return plan;
 }
 function recordCivic(action){
  const plan=MistralMadame.reduce(state.v059Madame,{...action,at:state.playTime},state);if(!plan.ok)return false;state.v059Madame=plan.ledger;saveGame(false);return true;
 }
 const previousSave=saveGame;saveGame=function(){if(state?.v059Madame)state.v059Madame=MistralMadame.synchronize(state.v059Madame,state);return previousSave(...arguments);};
 function terminalResponse(choice){return MistralMadame.PETITIONS[choice]?.text||'La requête est conservée.';}
 function openMadameTerminal(){
  state.v059Madame=MistralMadame.synchronize(state.v059Madame,state);const identity=state.v059Madame.identity,choices=[];
  if(!identity.terminalPetition){
   choices.push({text:'Faire constater la présence physique comme preuve provisoire.',onChoose:()=>choosePetition('presence')});
   choices.push({text:'Exporter et auditer la trace extérieure de 05 h 57.',tag:conditionTag('P',4),condition:()=>state.flags.archiveMemo||state.character.special.P>=4,lockText:'Perception 4 ou trace déjà découverte requise.',onChoose:()=>choosePetition('trace')});
   choices.push({text:'Conserver l’avis de décès, le corps présent et le journal comme versions contradictoires.',tag:conditionTag('I',4),condition:()=>!!state.flags.notes['journal-a03']||state.character.special.I>=4,lockText:'Intelligence 4 ou journal A-03 requis.',onChoose:()=>choosePetition('plurality')});
  }else choices.push({text:'Relire la réponse de M.A.D.A.M.E.',onChoose:()=>openDialogue(speaker('M.A.D.A.M.E.','ARBITRAGE RÉGIONAL — A-03','MD'),terminalResponse(identity.terminalPetition),[{text:'Fermer la réponse.',onChoose:closeDialogue}])});
  choices.push({text:'Relire l’avis de décès automatique.',onChoose:()=>openNote('ration-notice','AVIS AUTOMATIQUE','Votre décès administratif est daté de ce matin à 06 h 00. La signature provient du relais CONCORDE d’Aubagne à 05 h 57.')});
  choices.push({text:'Quitter la borne.',onChoose:closeDialogue});
  openDialogue(speaker('M.A.D.A.M.E.','MODULE ADMINISTRATIF DE DÉCISION, D’ARBITRAGE, DE MÉMOIRE ET D’EXÉCUTION','MD'),`CONTRADICTION ACTIVE. Le dossier 04-771-C est clos, mais un corps répond à son nom. Niveau de contradiction : ${identity.contradiction}/10. Toute correction supprimant une preuve doit être justifiée.`,choices);
 }
 function choosePetition(choice){
  const plan=transactCivic({type:'petition',choice},owner=>{if(choice==='trace')owner.flags.archiveMemo=true;if(choice==='plurality')owner.flags.notes['a03-contradiction']=true;});
  if(!plan)return;openDialogue(speaker('M.A.D.A.M.E.','ARBITRAGE RÉGIONAL — A-03','MD'),plan.notice,[{text:'Conserver la réponse dans le Pip-Boy.',onChoose:closeDialogue}]);
 }
 const oldRationTerminal=interactRationTerminal;interactRationTerminal=function(){
  if(state.flags.rationDenied)return openMadameTerminal();
  const before=state.flags.rationDenied,result=oldRationTerminal(...arguments);if(!before&&state.flags.rationDenied)recordCivic({type:'notice'});return result;
 };
 function odetteGift(){if(state.flags.looted['odette-gift'])return notifyCivic('Odette vous a déjà donné tout ce qu’elle pouvait.');state.flags.looted['odette-gift']=true;addAmmo('ammo10',8);addItem('water',1);saveGame(false);closeDialogue();return true;}
 function leaveA03(){closeDialogue();setMainStage(2);loadZone('aubagne');}
 function odetteChoiceResponse(choice,canLeave){
  const options=[];if(canLeave)options.push({text:'Quitter A-03 et rejoindre Aubagne.',onChoose:leaveA03});options.push({text:'Continuer à parler avec Odette.',onChoose:()=>odetteDialogue(canLeave)});
  openDialogue(speaker('Odette Ferraud','SURVEILLANTE A-03','OF'),MistralMadame.ODETTE[choice]?.text||'Le choix est conservé.',options);
 }
 function chooseOdette(choice,canLeave){
  const plan=transactCivic({type:'odette',choice},owner=>{if(choice==='attestation')owner.flags.notes['odette-attestation']=true;if(choice==='protect')owner.flags.notes['odette-protected']=true;if(choice==='contradiction')owner.flags.notes['a03-copy']=true;});
  if(plan)odetteChoiceResponse(choice,canLeave);
 }
 function odetteDialogue(canLeave=false){
  state.v059Madame=MistralMadame.synchronize(state.v059Madame,state);const identity=state.v059Madame.identity,choices=[];
  if(!identity.odetteChoice){
   choices.push({text:'Demander à Odette une attestation nominative.',onChoose:()=>chooseOdette('attestation',canLeave)});
   choices.push({text:'Protéger les familles : attester votre présence sans livrer leurs noms.',onChoose:()=>chooseOdette('protect',canLeave)});
   choices.push({text:'Joindre une copie contradictoire du journal A-03.',condition:()=>!!state.flags.notes['journal-a03'],lockText:'Le journal A-03 doit d’abord être lu.',onChoose:()=>chooseOdette('contradiction',canLeave)});
   choices.push({text:'Partir sans demander d’attestation.',onChoose:()=>chooseOdette('silence',canLeave)});
  }else choices.push({text:'Relire la forme choisie pour le témoignage.',onChoose:()=>odetteChoiceResponse(identity.odetteChoice,canLeave)});
  choices.push({text:'Demander des fournitures.',onChoose:odetteGift});
  if(canLeave)choices.push({text:'Quitter A-03 maintenant.',onChoose:leaveA03});else choices.push({text:'Prendre congé.',onChoose:closeDialogue});
  const text=identity.odetteChoice?'Le dossier garde déjà notre décision. Ce qui est écrit pourra me protéger, protéger les familles ou nous condamner tous les deux.':'La borne n’a pas seulement commis une erreur. Elle a choisi une version du monde où tu n’existes plus. Je peux témoigner, mais chaque forme de preuve expose quelqu’un.';
  openDialogue(speaker('Odette Ferraud','SURVEILLANTE A-03','OF'),text,choices);
 }
 const oldVaultExit=interactVaultExit;interactVaultExit=function(){if(!state.flags.rationDenied)return oldVaultExit(...arguments);return odetteDialogue(true);};
 const oldTalkOdette=talkOdette;talkOdette=function(){if(world?.id==='vault'&&state.flags.rationDenied)return odetteDialogue(false);return oldTalkOdette(...arguments);};
 const oldResolveRelay=resolveRelay;resolveRelay=function(outcome){const before=!!state.flags.relayPowered,result=oldResolveRelay(...arguments);if(!before&&state.flags.relayPowered)recordCivic({type:'relay',choice:outcome});return result;};
 function wrapMilestone(original,area){return function(outcome){const result=original(...arguments);recordCivic({type:area==='identity'?'chapter':'milestone',area,choice:outcome});return result;};}
 completeChapter=wrapMilestone(completeChapter,'identity');
 completeRoutesChapter=wrapMilestone(completeRoutesChapter,'routes');
 completeWaterChapter=wrapMilestone(completeWaterChapter,'water');
 completeIndustryChapter=wrapMilestone(completeIndustryChapter,'industry');
 completeMarseilleChapter=wrapMilestone(completeMarseilleChapter,'marseille');
 completeAubagneChapter=wrapMilestone(completeAubagneChapter,'aubagne');
 if(typeof V027_SUBS!=='undefined'&&V027_SUBS.data)V027_SUBS.data.madame='M.A.D.A.M.E. ET SEPT RÉSEAUX';
 function evidencePanel(ledger){const esc=v027Escape;return MistralMadame.evidenceList(ledger,state).map(item=>'<li>'+(item.active?'✓':'○')+' '+esc(item.label)+'</li>').join('');}
 function networkPanel(ledger){const esc=v027Escape;return MistralMadame.NETWORKS.map(def=>{const network=ledger.networks[def.id];return'<section class="v046-notice"><h3>'+esc(network.label)+'</h3><p>'+esc(network.controller)+'</p><p>Accès '+network.access+' · Légitimité '+network.legitimacy+' · Coercition '+network.coercion+' · Résilience '+network.resilience+'</p><p>'+esc(network.reasons.join(' ')||network.question)+'</p></section>';}).join('');}
 function projectionPanel(ledger){const esc=v027Escape,ranked=MistralMadame.ENDINGS.map(ending=>({...ending,score:ledger.scores[ending.id]})).sort((a,b)=>b.score-a.score);return'<section class="v046-notice"><h3>Projection institutionnelle</h3><p><strong>'+esc(ledger.projection.label)+'</strong> · '+esc(ledger.projection.state)+' · confiance '+ledger.projection.confidence+' % · marge '+ledger.projection.margin+'</p><p>Alternative : '+esc(ledger.projection.alternateLabel||'aucune')+'</p><ul>'+ledger.projection.reasons.map(reason=>'<li>'+esc(reason)+'</li>').join('')+'</ul><p>'+ranked.map(item=>esc(item.label)+' '+item.score).join(' · ')+'</p><p>Cette projection n’est pas une fin déclenchée : elle décrit l’équilibre produit par les décisions réellement sauvegardées.</p></section>';}
 function madamePanel(container){
  state.v059Madame=MistralMadame.synchronize(state.v059Madame,state);const esc=v027Escape,ledger=state.v059Madame,identity=ledger.identity;
  container.innerHTML='<div class="p27-long"><p class="p27-kicker">DOSSIER 04-771-C</p><h2>A-03, M.A.D.A.M.E. et les sept réseaux</h2><p>Statut : <strong>'+esc(identity.status)+'</strong> · étape '+esc(identity.stage)+' · contradiction '+identity.contradiction+'/10 · pression M.A.D.A.M.E. '+Math.round(identity.madamePressure)+'/100.</p><p>Requête A-03 : '+esc(MistralMadame.PETITIONS[identity.terminalPetition]?.label||'aucune')+' · témoignage d’Odette : '+esc(MistralMadame.ODETTE[identity.odetteChoice]?.label||'non fixé')+' · relais : '+esc(identity.relayMethod||'non résolu')+'.</p><h3>Chaîne de preuves</h3><ul>'+evidencePanel(ledger)+'</ul><h3>Réseaux</h3>'+networkPanel(ledger)+projectionPanel(ledger)+'</div>';
 }
 const oldData=v027Data;v027Data=function(container){if(V027.sub==='madame')return madamePanel(container);const result=oldData(...arguments);if(['france','continuity','services'].includes(V027.sub))container.insertAdjacentHTML('beforeend','<section class="v046-notice"><h2>Dossier A-03 et sept réseaux</h2><p>M.A.D.A.M.E. confronte le décès administratif aux preuves de terrain et calcule l’équilibre institutionnel produit par vos décisions.</p>'+v027Button('Consulter le registre civique','jump','data:madame')+'</section>');return result;};
 const oldRows=v027QuestRows;v027QuestRows=function(){
  const ledger=MistralMadame.synchronize(state.v059Madame,state),identity=ledger.identity,done=!!state.quest.mainComplete;
  return oldRows(...arguments).concat([{id:'a03:identity',name:'DOSSIER 04-771-C — PREUVES CONTRADICTOIRES',stage:done?'done':'active',active:!done&&state.player.zone==='vault',text:done?'Le premier conseil a fixé une règle régionale. Le registre civique continue d’en mesurer les effets.':identity.status==='declared_dead'?'Réunissez des preuves, choisissez la forme du témoignage d’Odette puis gagnez le relais AUB-04.':'Le dossier suit la progression de « Un vivant de trop ».',zone:null,steps:[['Avis de décès et présence corporelle conservés',identity.evidence.deathNotice&&identity.evidence.body],['Requête contradictoire déposée auprès de M.A.D.A.M.E.',!!identity.terminalPetition],['Forme du témoignage d’Odette fixée',!!identity.odetteChoice],['Présence reconnue par le relais AUB-04',identity.evidence.relayRecognition],['Règle régionale de l’identité adoptée',done]],source:'A-03 / M.A.D.A.M.E.',badge:done?'✓':'',hint:'Chaîne de preuves et souveraineté de l’identité'}]);
 };
 const oldTrack=v027Track;v027Track=function(id){if(id==='a03:identity'){toast(state.player.zone==='vault'?'La borne, Odette et le sas portent les preuves du dossier.':'Suivez l’objectif principal « Un vivant de trop » jusqu’au relais AUB-04.');return true;}return oldTrack(...arguments);};
 if(typeof V027_STATIONS!=='undefined')V027_STATIONS.madame={name:'M.A.D.A.M.E. — Cohérence civique',freq:'A-03',hint:'Statut, contradictions et projection',available:()=>!!state.flags.rationDenied,text:()=>MistralMadame.bulletin(state.v059Madame,state)};
 const previousAfter=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){if(typeof previousAfter==='function')previousAfter();globalThis.__MISTRAL_DEBUG??={};Object.assign(globalThis.__MISTRAL_DEBUG,{v059MadameInfo:()=>clone(MistralMadame.synchronize(state.v059Madame,state)),v059MadameOpen:()=>v027Open('data','madame'),v059MadameRefresh:()=>recordCivic({type:'refresh'}),v059MadamePetition:choice=>transactCivic({type:'petition',choice}),v059MadameOdette:choice=>transactCivic({type:'odette',choice})});};
}
