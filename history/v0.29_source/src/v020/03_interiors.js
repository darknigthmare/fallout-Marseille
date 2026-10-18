/* Hand-authored, fictional interiors: local game layouts, NOT cadastral data. */
const V020_OPERATIONS={
 relay_vent:{parent:'aubagne',place:'Aubagne · Atelier des souffles',title:'De l’air pour demain',name:'Lina Veyre',role:'Céramiste de maintenance',accent:[.64,.35,.19],
  intro:'La chambre des filtres aspire la poussière du four vers le dortoir. Ce n’est pas une pénurie de filtres : quelqu’un a inversé les consignes pour sauver une ancienne série de production. Je peux réparer, pas décider seule de qui respirera le premier.',
  past:'Ma mère signait chaque pièce ratée. Elle disait qu’un défaut sans nom finit toujours dans la maison de quelqu’un. J’ai conservé ses tessons ; pas pour accuser les morts, pour éviter de leur ressembler.',
  diagnosis:'Cycle 67 / recyclage inversé. Le filtre de réserve est intact dans le magasin ouest. Isoler le moteur avant de toucher au plénum. Le secteur du four conserve une ligne de retour manuelle.',
  component:'Cartouche céramique intacte',action:'Couper la recirculation',terminal:[0,1.1,8],part:[-10,1,-8],isolate:[9,1,-8],finish:[0,1,-10],note:[-10,1,0],enemy:[10,0,0],type:'radroach',
  choices:[['public','Priorité aux dortoirs','Le four ralentit. Les filtres propres vont aux familles ; Lina conserve une production réduite.',{water:4,stimpak:1}],['atelier','Rotation atelier / dortoirs','Lina affiche les horaires. Les équipes inspectent le registre au début de chaque relève.',{weaponParts:3,ceramicFilter:2}],['recover','Mettre l’installation en sommeil','Les habitants sont prévenus. Le moteur est démonté, sans prétendre que le service est rétabli.',{scrap:8,circuitry:3}]],
  tape:['Lina, relève du matin. Le filtre neuf est dans le casier ouest. Ne jetez pas la boîte vide : elle porte le numéro de cuisson.','Le registre affirme que le dortoir est inoccupé. Je viens pourtant d’y rapporter six couvertures.','Le ventilateur n’est pas cassé. Il obéit à une consigne écrite avant que les familles s’installent.','Je laisse le disjoncteur accessible. Même une bonne machine doit pouvoir être arrêtée par ceux qui vivent à côté.','Quand tu remettras le courant, écoute les tuyaux. Un souffle régulier vaut mieux qu’un voyant vert.']},
 relay_cold:{parent:'marseille',place:'Marseille · Annexe des Veilleurs',title:'La chaîne du froid',name:'Sofia Neri',role:'Infirmière des quais',accent:[.22,.48,.43],
  intro:'Les ampoules du dépôt ne sont pas toutes perdues. Le thermomètre a enregistré une coupure, puis une remise en route forcée. Il faut lire la courbe, récupérer le kit d’étanchéité et isoler l’armoire avant de choisir ce que nous conservons.',
  past:'Je ne veux pas d’un inventaire qui dit « vingt boîtes sauvées ». Certaines doses ont changé de couleur. Une réserve n’est utile que si les gens savent encore ce qu’ils reçoivent.',
  diagnosis:'Armoire C : rupture du circuit secondaire. Kit de joint en pharmacie. Consigner les lots exposés avant de remettre le groupe sous tension. Aucun réfrigérateur ne rend un lot avarié à nouveau sûr.',
  component:'Kit d’étanchéité stérile',action:'Isoler le circuit froid',terminal:[-8,1,7],part:[-11,1,-7],isolate:[11,1,-7],finish:[1,1,-8],note:[12,1,7],enemy:[11,0,-2],type:'feral',
  choices:[['public','Réserver les lots contrôlés aux urgences','Les lots douteux restent consignés. Les doses intactes alimentent le dispensaire.',{stimpak:3,antibiotics:2}],['atelier','Partager avec les équipes mobiles','Les réserves sont réparties en petites caisses tracées ; Sofia tient le registre des départs.',{stimpak:2,water:6}],['recover','Fermer la chambre et transférer les lots','Aucune remise en service n’est déclarée. Les lots sont déplacés et le groupe donne ses pièces.',{circuitry:5,chemicals:4}]],
  tape:['Ici Sofia. Ce relevé n’est pas une ordonnance : c’est l’histoire d’une panne.','À trois heures, l’armoire s’est arrêtée. Nous avons laissé les portes fermées et marqué l’heure sur le verre.','À cinq heures, un agent a réarmé le groupe pour effacer l’alarme. Le froid est revenu. Pas la confiance.','Les lots exposés ont une bande jaune. Personne ne doit les remettre avec les autres pour rendre le bilan plus joli.','Quand vous lirez ceci, demandez à voir le registre. Ne croyez pas une réserve uniquement parce qu’elle est froide.']},
 relay_brake:{parent:'laciotat',place:'La Ciotat · Poste du palan 12',title:'Le poids des vivants',name:'Nadir Colas',role:'Mécanicien de cale',accent:[.72,.49,.18],
  intro:'Le palan redémarre à chaque signal de fin de quart, même quand une équipe est encore sous la charge. Le frein de secours est au magasin, le sectionneur dans la travée est. Ensuite seulement nous pourrons décider de ses nouvelles consignes.',
  past:'J’ai passé vingt ans à écouter les pièces. Quand une dent grince, on dit qu’elle réclame de la graisse. Quand un collègue hésite, on dit qu’il manque de courage. J’aimerais qu’on apprenne à écouter les deux.',
  diagnosis:'Palan 12 / démarrage automatique interdit tant que le frein n’a pas été remplacé. Garniture de rechange : magasin ouest. Le sectionneur alimente aussi la sécurité mobile de la travée est.',
  component:'Garniture de frein certifiée',action:'Consigner le palan',terminal:[0,1,11],part:[-12,1,-10],isolate:[12,1,-10],finish:[0,1,-12],note:[-11,1,5],enemy:[12,0,0],type:'protectron',
  choices:[['public','Installer un double accord des équipes','Le moteur attend deux validations physiques. Le départ automatique ne décide plus de la fin d’une pause.',{steelPlate:3,weaponParts:4}],['atelier','Réserver le palan aux secours','Une clé de service est confiée aux équipes d’évacuation. Nadir organise les inspections.',{rescueBeacon:2,stimpak:2}],['recover','Déposer définitivement le moteur','La grue est signalée hors service ; ses pièces rejoignent les équipements réparables.',{scrap:12,circuitry:4}]],
  tape:['Nadir, poste douze. On n’a pas perdu la charge. On a perdu le droit de dire qu’on se trouvait dessous.','Le signal de fin de quart fait repartir le moteur. C’est un horaire, pas un regard.','La garniture est sur la tablette du magasin. J’ai marqué les côtes au crayon sur son emballage.','Coupez au sectionneur est. La machine de sécurité utilise le même départ ; elle s’arrêtera aussi.','Après la réparation, gardez les noms de ceux qui valident. Une case cochée sans personne derrière ne nous protégera pas.']}
};
const V020_STATIONS={aubagne:'Halte des céramistes',marseille:'Halte des Veilleurs',laciotat:'Halte du chantier',mugel:'Escale du Mugel',lagarde:'Refuge de la Garde'};
for(const [id,d] of Object.entries(V020_OPERATIONS)){
 if(!ALL_ZONE_IDS.includes(id))ALL_ZONE_IDS.push(id);
 V013_LORE_CATALOG[id]={zone:id,title:d.title,tapeTitle:`Relève enregistrée · ${d.name}`,speaker:d.name,lines:d.tape,terminalTitle:d.place,noteTitle:d.title,entries:[]};
}
const v020Unlocked=isZoneUnlocked;isZoneUnlocked=function(id){return V020_OPERATIONS[id]?v020Unlocked(V020_OPERATIONS[id].parent):v020Unlocked(id);};
function v020OpState(id){return state.v020.operations[id]||(state.v020.operations[id]={accepted:false,diagnosed:false,component:false,isolated:false,resolution:null});}
function v020Danger(){return (world?.enemies||[]).some(e=>e.alive&&e.alerted&&dist2(state.player.pos,e.pos)<22&&lineOfSight(state.player.pos,[e.pos[0],(e.pos[1]||0)+1,e.pos[2]]));}
function v020Object(w,id,pos,label,fn,kind='object'){addInteract(w,id,pos,label,fn,{radius:3.3,priority:5,kind});}
function v020Wall(w,x,z,sx,sz,col,h=3.8){addBox(w,[x,h/2,z],[sx,h,sz],col);addCollider(w,x,z,sx,sz,{maxY:h,id:`wall:${x}:${z}`});addBox(w,[x,.30,z],[sx+.015,.38,sz+.015],[.21,.23,.22]);addBox(w,[x,3.45,z],[sx+.015,.12,sz+.015],[.65,.57,.4]);}
function v020Bench(w,x,z,col,medical=false){addCollider(w,x,z,2.4,1,{maxY:.96});addBox(w,[x,.86,z],[2.4,.16,1],medical?[.71,.74,.66]:[.37,.29,.19]);for(const a of [-.9,.9])addBox(w,[x+a,.42,z],[.11,.8,.78],[.2,.23,.21]);for(let i=0;i<5;i++)addBox(w,[x-.85+i*.38,1.05,z+(i%2)*.14],[.23,.23,.30],i%2?col:[.63,.60,.47]);}
function v020Rack(w,x,z,col){for(const y of [.2,1,1.8,2.6])addBox(w,[x,y,z],[2.7,.1,.85],[.26,.30,.28]);for(const ox of[-1.3,1.3])addBox(w,[x+ox,1.4,z],[.09,2.8,.85],[.38,.4,.35]);for(let j=0;j<3;j++)for(let i=0;i<4;i++)addBox(w,[x-1+i*.67,.48+j*.8,z],[.46,.43,.58],(i+j)%3?col:[.65,.64,.5]);addCollider(w,x,z,2.7,.9,{maxY:2.8});}
function v020Console(w,id,pos,col){addCollider(w,pos[0],pos[2],1.25,.65,{maxY:.96});addBox(w,[pos[0],.55,pos[2]],[1.25,1.1,.65],[.23,.28,.25]);addBox(w,[pos[0],1.35,pos[2]],[1.1,.65,.24],[.13,.19,.15]);addBox(w,[pos[0],1.35,pos[2]+.14],[.84,.4,.035],col,0,{emissive:.6,id});for(let i=0;i<5;i++)addBox(w,[pos[0]-.4+i*.18,1.02,pos[2]+.23],[.09,.055,.07],[.78,.69,.43]);}
function v020Door(w,id,x,z,axis='x'){
 const opened=state.v020.openedDoors[id];const dims=axis==='x'?[2.3,3,.17]:[.17,3,2.3];
 const leaf=addBox(w,[x,1.5,z],dims,[.39,.47,.42],0,{id,hidden:!!opened});
 const c=addCollider(w,x,z,dims[0],dims[2],{maxY:3,id,disabled:!!opened});
 v020Object(w,id,[x+(axis==='z'?.9:0),1.1,z+(axis==='x'?.9:0)],'Ouvrir / fermer la porte',()=>{if(!v020Physical(id))return false;
 const next=!state.v020.openedDoors[id];if(!next&&[...w.npcs,...w.enemies,{pos:state.player.pos}].some(a=>a.alive!==false&&dist2(a.pos,[x,0,z])<1.35))return v020Notify('Passage occupé : la porte reste ouverte.',true);
 state.v020.openedDoors[id]=next;leaf.hidden=next;c.disabled=next;w.v020NavEpoch=(w.v020NavEpoch||0)+1;saveGame();return true;},'door');
}
function v020OpTalk(id){if(!v020Physical(id+':contact'))return false;const d=V020_OPERATIONS[id],s=v020OpState(id);openDialogue(speaker(d.name,d.role,'RE'),s.resolution?d.choices.find(c=>c[0]===s.resolution)[2]:d.intro,[
 {text:s.accepted?'Rappeler les opérations à effectuer.':'Je prends le relais.',onChoose:()=>{s.accepted=true;state.v020.tracked=id;saveGame();openDialogue(speaker(d.name,d.role,'RE'),'Lire le diagnostic, récupérer la pièce, isoler le circuit, puis revenir au pupitre de remise en service. Le passage secondaire permet de contourner la travée dangereuse.');}},
 {text:'Pourquoi tiens-tu à garder les anciens relevés ?',onChoose:()=>openDialogue(speaker(d.name,d.role,'RE'),d.past)},
 {text:'Repartir.',onChoose:closeDialogue}]);return true;}
function v020OpAction(id,step,choice){const d=V020_OPERATIONS[id],s=v020OpState(id);if(!d||!v020Physical(id+':'+step)||(v020Danger()&&!['part','isolate'].includes(step)))return v020Notify('Rejoignez le poste et mettez-vous hors du combat.',true);
 if(step==='terminal'){s.diagnosed=true;saveGame();openDialogue(speaker('Maintenance locale',d.place,'PC'),d.diagnosis);return true;}
 if(!s.accepted)return v020Notify('Parlez d’abord au responsable de la relève.',true);
 if(step==='part'){if(s.component)return v020Notify('La pièce est déjà dans votre dossier.');s.component=true;state.v020.looted[id+':part']=true;world.staticDraws.filter(p=>p.id===id+':component').forEach(p=>p.hidden=true);toast(d.component+' récupérée.','good');saveGame();return true;}
 if(step==='isolate'){if(!s.diagnosed)return v020Notify('Consultez d’abord la consigne du terminal.',true);if(s.isolated)return false;s.isolated=true;world.hazards=[];if(id==='relay_brake')for(const e of world.enemies)if(robotType(e.type)){e.alive=false;e.health=0;state.flags.enemyDead[e.id]=true;}world.staticDraws.filter(p=>p.id===id+':signal').forEach(p=>p.color=[.3,.65,.42]);toast('Énergie consignée. La zone technique est sûre.','good');saveGame();return true;}
 if(step==='finish'){
  if(s.resolution)return v020Notify('Cette intervention a déjà été soldée.');
  if(!s.diagnosed||!s.component||!s.isolated)return v020Notify('Diagnostic, pièce et consignation requis.',true);
  if(!choice){openDialogue(speaker(d.name,'Choix de remise en service','RE'),'La panne est comprise et la pièce est prête. Choisissez ce que devient le service.',d.choices.map(c=>({text:c[1],onChoose:()=>{debugDismissDialogue();v020OpAction(id,'finish',c[0]);}})));return true;}
  const c=d.choices.find(c=>c[0]===choice);if(!c)return false;
  s.resolution=c[0];s.completedAt=state.playTime||0;for(const [k,n] of Object.entries(c[3]))addItem(k,n);state.player.caps+=75;gainXP(110);v020ApplyResult(world,id);saveGame();openDialogue(speaker(d.name,d.role,'RE'),c[2]+'\n\nIntervention clôturée · 75 capsules · 110 XP.');return true;
 }return false;
}
function v020ApplyResult(w,id){const d=V020_OPERATIONS[id],s=v020OpState(id);if(!s.resolution)return;
 const col=s.resolution==='recover'?[.57,.39,.22]:[.33,.69,.44];w.staticDraws.filter(p=>p.id===id+':operating').forEach(p=>{p.color=col;p.emissive=.4;});
 if(s.resolution!=='recover'&&!w.v020Restored){w.v020Restored=true;const n=addHumanNPC(w,id+':assistant','Équipe de relève','Service rétabli',[-3,0,7],[.5,.58,.4],{route:[[-3,0,7],[2,0,7],[2,0,4],[-3,0,4]]});n.v020Static=false;v020Bench(w,4,9,col,id==='relay_cold');}
}
function v020BuildInterior(id){const d=V020_OPERATIONS[id],s=v020OpState(id),w=createWorld(id,d.place,d.parent,{skyTop:[19,28,26],skyBottom:[52,61,51],fog:[.22,.26,.22],daylight:.82,wind:0,indoor:true});
 w.bounds=id==='relay_brake'?[-18,18,-17,17]:id==='relay_cold'?[-17,17,-13,13]:[-15,15,-15,15];w.spawn=[0,1.65,w.bounds[3]-3];w.spawnYaw=0;w.v020Interior=true;w.v020NavEpoch=1;const [l,r,t,b]=w.bounds;
 addFloorZone(w,0,0,r-l,b-t,0);addBox(w,[0,-.2,0],[r-l,.4,b-t],[.3,.33,.29]);
 for(let x=l+1;x<r;x+=2)for(let z=t+1;z<b;z+=2)addBox(w,[x,.005,z],[1.96,.015,1.96],((x+z)%4)?[.36,.38,.33]:[.39,.41,.36]);
 for(const [x,z,sx,sz] of [[l,0,.4,b-t],[r,0,.4,b-t],[0,t,r-l,.4],[0,b,r-l,.4]])v020Wall(w,x,z,sx,sz,[.54,.55,.45]);
 // Roof strips retain an actual roof; skylights provide a readable industrial interior.
 for(let x=l+2;x<r;x+=4){addBox(w,[x,4.12,0],[3.2,.20,b-t],[.24,.29,.27]);addBox(w,[x+1.78,4.02,0],[.22,.15,b-t],[.17,.21,.2]);}
 for(let z=t+3;z<b;z+=6)for(const x of [-4,4]){addBox(w,[x,3.82,z],[2,.12,.28],[.82,.82,.55],0,{emissive:.75});addBox(w,[x,3.6,z],[.08,.25,.08],[.25,.28,.24]);}
 for(const x of[l+.7,r-.7])for(const y of[2.7,3.1])addBox(w,[x,y,0],[.16,.16,b-t-.5],d.accent);
 const walls=id==='relay_vent'?[[-5,-11,.26,8],[-5,0,.26,8],[-5,11,.26,8],[5,-9,.26,12],[5,10,.26,10],[-13,4,4,.24],[-7,4,4,.24],[10,4,10,.24]]:
 id==='relay_cold'?[[0,-8,.25,10],[-13,2,8,.25],[0,2,12,.25],[13,2,8,.25],[8,-8,.25,10]]:
 [[-7,-3,.32,13],[7,-3,.32,13],[-12,7,10,.3],[12,7,10,.3],[0,-4,8,.3]];
 for(const a of walls)v020Wall(w,...a,[.40,.47,.40],3.4);
 if(id==='relay_vent')v020Door(w,id+':door',-5,-6,'z');
 if(id==='relay_cold')v020Door(w,id+':door',-8,2);
 if(id==='relay_brake')v020Door(w,id+':door',7,5,'z');
 // Props are placed against walls, away from the two independent circulation loops.
 for(const x of[l+2.1,r-2.1])for(const z of[t+2.2,b-2.2])v020Rack(w,x,z,d.accent);
 for(const z of[-2,4])v020Bench(w,l+3.2,z,d.accent,id==='relay_cold');
 for(const x of[-3,2])v020Bench(w,x,t+1.5,d.accent);
 if(id==='relay_cold'){for(const z of[-9,-4]){addBox(w,[-12,.65,z],[3.4,.16,1.3],[.78,.78,.65]);addBox(w,[-13.25,.81,z],[.7,.16,1.1],[.87,.85,.72]);addBox(w,[-12,.3,z],[2.9,.6,.8],[.31,.37,.35]);}for(let j=0;j<3;j++){addBox(w,[13,1.1,-9+j*3],[1.5,2.2,1.2],[.65,.69,.59]);addBox(w,[13,1.1,-8.37+j*3],[1.35,1.9,.03],[.3,.44,.38]);}}
 else if(id==='relay_vent'){for(const z of[-10,-4]){addPart(w,'cylinder',[12,1.3,z],[2.3,2.6,2.3],d.accent);addBox(w,[12,2.8,z],[2.6,.25,2.6],[.25,.27,.24]);addCollider(w,12,z,2.3,2.3,{maxY:2.6});}for(let i=0;i<7;i++)addBox(w,[0,2.8,-4+i*.3],[3.1,.08,.15],[.24,.30,.25]);}
 else{for(const x of[-4,4]){addBox(w,[x,2.2,-2],[.4,4.4,.45],d.accent);addBox(w,[x,2.2,4],[.4,4.4,.45],d.accent);}addBox(w,[0,4,1],[8.6,.6,.7],d.accent);addBox(w,[0,2.4,1],[2.7,1.7,2.4],[.27,.34,.3]);addCollider(w,0,1,2.7,2.4,{maxY:3.3});addBox(w,[0,1.45,1],[3,.18,2.6],[.35,.28,.18]);for(const x of[-.9,.9]){addPart(w,'cylinder',[x,3.5,1],[.07,.9,.07],[.64,.65,.54]);addBox(w,[x,2.4,2.23],[.12,1.7,.06],[.57,.56,.42]);}for(const x of[-4,4])for(const z of[-2,4]){addBox(w,[x,.09,z],[1.1,.18,1.1],[.28,.31,.27]);for(const ox of[-.35,.35])addPart(w,'cylinder',[x+ox,.22,z],[.11,.12,.11],[.67,.67,.55]);}for(const z of[-1,3])addBox(w,[0,.03,z],[5,.03,.11],[.8,.63,.21]);}
 const contact=addHumanNPC(w,id+':npc',d.name,d.role,[-3,0,b-4],d.accent,{yaw:.6});contact.v020Static=true;
 v020Object(w,id+':contact',[-3,1,b-4],'Parler à '+d.name,()=>v020OpTalk(id),'npc');
 v020Console(w,id+':operating',d.terminal,[.33,.67,.42]);v020Object(w,id+':terminal',d.terminal,'Terminal · diagnostic',()=>v020OpAction(id,'terminal'),'terminal');
 addBox(w,[d.part[0],.9,d.part[2]],[.78,.62,.64],[.78,.64,.4],0,{id:id+':component',hidden:s.component});v020Object(w,id+':part',d.part,d.component,()=>v020OpAction(id,'part'),'loot');
 v020Console(w,id+':signal',d.isolate,s.isolated?[.3,.65,.42]:[.85,.28,.17]);v020Object(w,id+':isolate',d.isolate,d.action,()=>v020OpAction(id,'isolate'),'terminal');
 v020Console(w,id+':operating',d.finish,[.65,.51,.25]);v020Object(w,id+':finish',d.finish,'Pupitre · remise en service',()=>v020OpAction(id,'finish'),'terminal');
 addBox(w,[d.note[0],.99,d.note[2]],[.45,.12,.32],[.72,.69,.45]);v020Object(w,id+':tape',d.note,'Holodisque · '+d.name,()=>{if(v020Physical(id+':tape'))openHolotape(id);},'loot');
 const e=addEnemy(w,id+':security',d.type,id==='relay_brake'?'Protectron de quart':id==='relay_cold'?'Goule de la réserve':'Radcafard du four',d.enemy,{health:id==='relay_brake'?100:65,range:id==='relay_brake'?13:2,detect:11,loot:{caps:12},speed:1.5});if(e){e.alerted=false;if(s.isolated&&id==='relay_brake'){e.alive=false;e.health=0;}}
 if(!s.isolated)addHazard(w,id+':heat',d.isolate[0]+2,d.isolate[2]+1,1.25,{damage:2,label:'Circuit non consigné',kind:'burning'});
 v020Object(w,id+':station',[3,1,b-3],'Établi et halte de relève',()=>v020OpenField('atelier'),'bench');v020Bench(w,3,b-2,d.accent);w.v020Station={id:id+':station',name:d.place};
 v020Object(w,id+':exit',[0,1,b-1],'Revenir au quartier',v020ExitInterior,'door');addBox(w,[0,1.5,b-.22],[2.8,3,.16],[.24,.37,.3]);
 w.v020Rooms=id==='relay_vent'?[['Accueil',0,9],['Magasin',-10,-8],['Dortoir',-10,0],['Circuit des fours',10,-6],['Pupitre',0,-10]]:id==='relay_cold'?[['Accueil',-8,7],['Pharmacie',-11,-7],['Soins',-11,-2],['Chambre froide',11,-7],['Régulation',1,-8]]:[['Relève',0,11],['Magasin',-12,-10],['Palan',0,1],['Travée est',12,-8],['Consignes',0,-12]];
 v020ApplyResult(w,id);return w;
}
function v020EnterInterior(id){const d=V020_OPERATIONS[id];if(!d||!v020Physical('v020:portal:'+id,4))return false;state.v020.returnPoint={zone:world.id,pos:[...state.player.pos],yaw:state.player.yaw,pitch:state.player.pitch,geoContext:deepClone(state.geo||null)};state.v020.visits[id]=true;debugDismissDialogue();loadZone(id,{instance:true,force:true,silent:true,noTravel:true});saveGame();return true;}
function v020ExitInterior(){if(!world?.v020Interior||!v020Physical(world.id+':exit',3.6))return false;const d=V020_OPERATIONS[world.id],r=state.v020.returnPoint||{zone:d.parent,pos:null,yaw:0,pitch:0};state.v020.returnPoint=null;debugDismissDialogue();loadZone(r.zone,{instance:true,force:true,silent:true,noTravel:true,...(r.pos?{spawn:r.pos}:{}),yaw:r.yaw});state.player.pitch=r.pitch||0;saveGame();return true;}
function v020ClearPoint(w,origin){for(let radius=3;radius<20;radius+=2)for(let j=0;j<16;j++){const a=j/16*TAU,p=[origin[0]+Math.sin(a)*radius,1,origin[2]+Math.cos(a)*radius];if(p[0]<w.bounds[0]+3||p[0]>w.bounds[1]-3||p[2]<w.bounds[2]+3||p[2]>w.bounds[3]-3)continue;if(w.colliders.some(c=>!c.disabled&&p[0]>c.minX-2&&p[0]<c.maxX+2&&p[2]>c.minZ-2&&p[2]<c.maxZ+2))continue;return p;}return [origin[0],1,origin[2]];}
const v020BuildBase=buildWorld;
buildWorld=function(id){if(V020_OPERATIONS[id])return v020BuildInterior(id);const w=v020BuildBase(id);if(!V020_STATIONS[id])return w;
 const p=v020ClearPoint(w,w.spawn),portal=Object.keys(V020_OPERATIONS).find(k=>V020_OPERATIONS[k].parent===id);
 v020Bench(w,p[0],p[2],[.42,.5,.36]);v020Object(w,'v020:station',p,'Halte · atelier, réserve, repos',()=>v020OpenField('atelier'),'bench');w.v020Station={id:'v020:station',name:V020_STATIONS[id]};
 if(portal){const q=v020ClearPoint(w,[p[0]+6,1,p[2]]);addBox(w,[q[0],1.5,q[2]-1],[3,3,.3],[.26,.35,.30]);addBox(w,[q[0],3.15,q[2]-1],[3.4,.3,.55],[.66,.53,.25]);v020Object(w,'v020:portal:'+portal,q,'Entrer · '+V020_OPERATIONS[portal].place,()=>v020EnterInterior(portal),'door');}
 return w;};
const v020OldObjective=getObjectiveMarker;getObjectiveMarker=function(){
 const id=state.v020.tracked,d=V020_OPERATIONS[id];if(d){const s=v020OpState(id);if(!s.resolution){const target=!s.accepted?'contact':!s.diagnosed?'terminal':!s.component?'part':!s.isolated?'isolate':'finish';const it=world?.interactables.find(i=>i.id===(world.id===id?id+':'+target:'v020:portal:'+id));if(it)return {zone:world.id,pos:it.pos,label:it.label};}}
 return v020OldObjective();};
