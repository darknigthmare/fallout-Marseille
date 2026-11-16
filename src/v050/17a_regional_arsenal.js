/* Regional presentation contract. Stable IDs only; numeric weapon data, ammo,
   ownership, rewards, damage and save schemas are not changed. */
const MistralRegionalArsenal=(()=>{
 'use strict';
 const RECORDS={
  "mistralCarbine":{"family":"rifle","profile":"rifle","name":"Carabine du Mistral","note":"Les ateliers privilégient un boîtier réparable plutôt qu’un nom gravé. La Carabine n’annule pas le vent : la précision reste celle de son mécanisme."},
  "ceramicLauncher":{"family":"industrial","profile":"industrial","name":"Lance-brique céramique","note":"Prototype des Céramistes projetant des masses réfractaires."},
  "concordePistol":{"family":"energy","profile":"energy-pistol","name":"Pistolet CONCORDE","note":"Le numéro de service survit au service lui-même. Les contacts de la cellule comptent davantage que le cachet figurant sur la crosse."},
  "calanquesGlaive":{"family":"blade","profile":"blade","name":"Glaive des Calanques","note":"Lame anticorrosion conçue par les sauveteurs côtiers."},
  "releveTorch":{"family":"industrial","profile":"industrial","name":"Chalumeau de la Relève","note":"Chalumeau industriel réglé pour découper blindages et automates."},
  "cisternNeedler":{"family":"industrial","profile":"industrial","name":"Aiguilleur de la Citerne","note":"Arme pneumatique silencieuse issue des équipes hydrauliques."},
  "saltScatter":{"family":"shotgun","profile":"shotgun","name":"Éparpilleur de sel","note":"Fusil côtier chargé pour repousser les créatures marines."},
  "gardianArc":{"family":"energy","profile":"energy","name":"Arc des Veilleurs","note":"Le nom des Veilleurs ne constitue pas une promesse de neutralisation non létale. Le projecteur conserve les dégâts de sa fiche."},
  "provenceRevolver":{"family":"pistol","profile":"revolver","name":"Revolver des Communes","note":"Arme marquée des sceaux de plusieurs communes du réseau."},
  "transferCarbine":{"family":"rifle","profile":"rifle","name":"Carabine des Correspondances","note":"Arme de M-04 dont chaque pièce porte un numéro de transit différent."},
  "hearthHammer":{"family":"melee","profile":"melee","name":"Marteau du Foyer témoin","note":"Marteau cérémoniel d’A-19, renforcé par des briques réfractaires."},
  "floodGun":{"family":"industrial","profile":"industrial","name":"Canon de la Crue","note":"Lanceur hydraulique de H-12 adapté aux projectiles métalliques."},
  "rootSpear":{"family":"blade","profile":"blade","name":"Lance des Racines","note":"Arme organo-céramique conçue dans G-22."},
  "seasonRifle":{"family":"rifle","profile":"rifle","name":"Fusil des Saisons","note":"Fusil de C-14 réglé pour les cycles thermiques extrêmes."},
  "keelCannon":{"family":"heavy","profile":"heavy","name":"Canon de Quille","note":"Arme navale compacte forgée dans LC-03."},
  "echoPistol":{"family":"energy","profile":"energy-pistol","name":"Pistolet de l’Écho","note":"Arme d’IV-07 synchronisée avec les balises radio."},
  "mercyLaser":{"family":"energy","profile":"energy","name":"Laser du Répit","note":"Instrument médical de P-08 converti en laser de précision."},
  "civicJudge":{"family":"pistol","profile":"revolver","name":"Juge civique","note":"Le barillet compte six chambres, pas six présomptions de culpabilité. Les articles gravés sur le métal ne rendent pas celui qui le porte impartial."},
  "stageGun":{"family":"pistol","profile":"pistol","name":"Arme de scène T-05","note":"Accessoire de théâtre devenu une arme réelle après deux siècles."},
  "radeRepeater":{"family":"rifle","profile":"rifle","name":"Répétiteur de la Rade","note":"Carabine à levier construite pour les patrouilles des quais."},
  "mistralNeedler":{"family":"industrial","profile":"needle","name":"Aiguille du Mistral","note":"Les équipes de secours ont conservé les aiguilles et le système pneumatique. Cette version blesse et ralentit : ce n’est ni une anesthésie garantie, ni une guérison."},
  "ceramicSaw":{"family":"blade","profile":"ceramic-disc","name":"Scie céramique d’Aubagne","note":"Le disque réfractaire vient du travail de la Manufacture. Remettre une arme en état n’efface pas ce qu’elle a servi à couper."},
  "garlabanMortar":{"family":"heavy","profile":"mortar40","name":"Mortier du Garlaban","note":"Les Vigies ne confondent pas une crête dégagée avec une zone vide. Le tube emploie les charges de 40 mm prévues par son catalogue, pas des missiles."},
  "municipalLaser":{"family":"energy","profile":"energy","name":"Laser municipal","note":"Carabine énergétique standardisée par les services publics restaurés."},
  "saltArc":{"family":"energy","profile":"energy","name":"Arc salin de La Ciotat","note":"Les contacts souffrent autant du sel que les tôles des chantiers. La cellule à protons reste son alimentation ; l’eau de mer n’est pas une munition gratuite."},
  "m13_archivistPistol":{"family":"energy","profile":"energy-pistol","name":"Pistolet de l’Archiviste","note":"Projette des impulsions codées qui perturbent les automates."},
  "m13_notaryCarbine":{"family":"rifle","profile":"rifle","name":"Carabine notariale","note":"Carabine de sûreté portant chaque impact dans un registre mécanique."},
  "m13_mistralDerringer":{"family":"pistol","profile":"pistol","name":"Derringer du Mistral","note":"Arme de poche à deux coups conçue pour les négociations difficiles."},
  "m13_seilleGauss":{"family":"energy","profile":"energy","name":"Gauss de la Seille","note":"Fusil Gauss stabilisé par une céramique d’Aubagne."},
  "m13_longchampLaser":{"family":"energy","profile":"energy","name":"Laser de Longchamp","note":"Fusil alimenté par les cellules d’archives hydrauliques."},
  "m13_huveauneRebarGun":{"family":"industrial","profile":"industrial","name":"Lance-fer de l’Huveaune","note":"Projette des tiges réfractaires issues des galeries."},
  "m13_garlabanFlareRifle":{"family":"rifle","profile":"rifle","name":"Fusil de vigie du Garlaban","note":"Fusil de signalisation transformé en arme de précision incendiaire."},
  "m13_calanqueSpeargun":{"family":"industrial","profile":"industrial","name":"Arbalète des Calanques","note":"Lance des traits anticorrosion avec très peu de bruit."},
  "m13_ciotatPlasmaCutter":{"family":"energy","profile":"energy","name":"Découpeur plasma de La Ciotat","note":"Outil naval converti pour découper armures et robots."},
  "m13_aubagneKilnHammer":{"family":"melee","profile":"melee","name":"Marteau des fours d’Aubagne","note":"Masse en céramique réfractaire conservant une chaleur extrême."},
  "m13_bastideRifle":{"family":"rifle","profile":"rifle","name":"Fusil des Bastides","note":"Fusil long protégé par du bois d’olivier et des joints de cuir."},
  "m13_radeScattergun":{"family":"shotgun","profile":"shotgun","name":"Éparpilleur de la Rade","note":"Fusil de défense portuaire chargé pour les espaces étroits."},
  "m13_transitPulseGun":{"family":"energy","profile":"energy-pistol","name":"Pistolet à impulsions du Transit","note":"Arme ferroviaire perturbant les capteurs et serrures."},
  "m13_concordeStampGun":{"family":"industrial","profile":"industrial","name":"Poinçon CONCORDE","note":"Projette des poinçons métalliques numérotés."},
  "m13_mistralReelGun":{"family":"energy","profile":"energy","name":"Canon-bobine du Mistral","note":"Accélérateur lourd construit avec des bobines de relais."},
  "m13_oliveBlade":{"family":"blade","profile":"blade","name":"Lame d’olivier","note":"Lame courte montée sur une poignée en olivier durci."},
  "m13_brineCaster":{"family":"energy","profile":"energy","name":"Projeteur de saumure","note":"Les charges de saumure se comptent au dépôt. Aucun prélèvement dans la mer ne les remplace automatiquement."},
  "m13_quarryAutocannon":{"family":"heavy","profile":"heavy","name":"Autocanon des Carrières","note":"Arme lourde conçue à partir d’un perforateur de roche."},
  "m13_sirenCarbine":{"family":"energy","profile":"energy","name":"Carabine-Sirène","note":"Combine tir énergétique et impulsion d’alarme."},
  "m13_refugeNeedler":{"family":"industrial","profile":"needle","name":"Aiguille des Veilleurs","note":"Arme médicale silencieuse tirant des dards stabilisés."},
  "m13_ceramicGauntlet":{"family":"fist","profile":"fist","name":"Gantelet céramique","note":"Poing assisté isolé par des plaques d’argile technique."},
  "m13_vineyardRepeater":{"family":"rifle","profile":"rifle","name":"Répétiteur des Vignes","note":"Carabine à levier des cultures en terrasses."},
  "m13_mugelDeckGun":{"family":"heavy","profile":"heavy","name":"Canon de pont du Mugel","note":"Pièce de pont miniaturisée pour les défenses côtières."},
  "m13_islandSignalPistol":{"family":"energy","profile":"energy-pistol","name":"Pistolet de l’Île Verte","note":"Pistolet lumineux utilisé par les équipes de sauvetage."},
  "m13_canailleRailRifle":{"family":"rifle","profile":"rifle","name":"Fusil-rail de Canaille","note":"Arme de falaise projetant des pointes à très haute vitesse."},
  "m13_noaillesCompact":{"family":"pistol","profile":"pistol","name":"Compact de Noailles","note":"Pistolet-mitrailleur court fabriqué pour les marchés étroits."},
  "m13_saintCharlesSMG":{"family":"rifle","profile":"rifle","name":"P.-M. Saint-Charles","note":"Arme de sûreté ferroviaire à forte cadence."},
  "m13_vieuxPortRevolver":{"family":"pistol","profile":"revolver","name":"Revolver du Vieux-Port","note":"Revolver inoxydable porté par les capitaines de quai."},
  "m13_firewatchLance":{"family":"blade","profile":"blade","name":"Lance des Vigies","note":"Longue lance munie d’un crochet de secours."},
  "m13_memoryRecorderGun":{"family":"energy","profile":"energy","name":"Enregistreur de mémoire","note":"Un appareil nommé Enregistreur ne rend pas une mémoire au blessé. Son alimentation et ses dégâts restent ceux d’une arme."}
 };
 for(const value of Object.values(RECORDS))Object.freeze(value);Object.freeze(RECORDS);
 const own=(o,k)=>!!o&&Object.hasOwn(o,k);
 function entry(id){return typeof id==='string'&&own(RECORDS,id)?RECORDS[id]:null;}
 function identify(w){return entry(w?.mistralViewId);}
 function catalogue(weapons={},ammo={},snapshot={}){
  const owned=new Set(Array.isArray(snapshot.equipment?.ownedWeapons)?snapshot.equipment.ownedWeapons:[]);
  return Object.entries(RECORDS).filter(([id])=>own(weapons,id)).map(([id,view])=>{
   const w=weapons[id],ammunition=w.melee?null:(w.ammoId||'ammo10');
   return {id,name:w.name||view.name,note:view.note,description:w.desc||'',family:view.family,profile:view.profile,
    owned:owned.has(id),equipped:snapshot.player?.weaponId===id,ammoId:ammunition,
    ammoName:ammunition?(ammo[ammunition]?.name||ammunition):'Aucune munition',
    damage:w.damage,clip:w.melee?null:w.clip,range:w.range,reload:w.melee?null:w.reload,
    pellets:w.pellets||1,burst:w.burst||1,status:w.status||null,melee:!!w.melee};
  });
 }
 const fold=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr-FR');
 function filter(rows,query='',ownedOnly=false){const q=fold(query).slice(0,120).trim();return rows.filter(r=>(!ownedOnly||r.owned)&&(!q||fold([r.name,r.description,r.note,r.ammoName].join(' ')).includes(q))).sort((a,b)=>a.name.localeCompare(b.name,'fr'));}
 function install(presentation,weapons){
  if(!presentation||!weapons||presentation.mistralRegionalArsenal)return false;
  // Enumerable visual metadata survives currentWeapon()'s modifier copy.
  // It is NOT stored in the player save and never replaces a weapon object.
  for(const id of Object.keys(RECORDS))if(own(weapons,id))weapons[id].mistralViewId=id;
  const family=presentation.family,profile=presentation.profile,geometry=presentation.geometry;
  presentation.family=function(w={}){return identify(w)?.family||family(w);};
  presentation.profile=function(w={}){return identify(w)?.profile||profile(w);};
  presentation.geometry=function(kind,p={}){return decorate(geometry,kind,p);};
  Object.defineProperty(presentation,'mistralRegionalArsenal',{value:true});return true;
 }
 function decorate(build,kind,p={}){
  const special=['needle','mortar40','ceramic-disc'].includes(p.profile)?p.profile:null;
  if(!special)return build(kind,p);
  const baseProfile=special==='needle'?'industrial':special==='mortar40'?'launcher':'blade';
  const mesh=build(kind,{...p,profile:baseProfile}),q=mesh.pose;
  mesh.profile=special;
  let serial=mesh.faces.reduce((m,f)=>Math.max(m,f.id),0)+1;
  const steel=[.34,.39,.38],edge=[.68,.67,.54],dark=[.10,.14,.14],clay=[.62,.40,.22],glass=[.43,.63,.57],brass=[.66,.52,.25];
  const add=(a,b)=>a.map((v,i)=>v+b[i]),mul=(a,n)=>a.map(v=>v*n),sub=(a,b)=>a.map((v,i)=>v-b[i]);
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm=a=>mul(a,1/(Math.hypot(...a)||1));
  function rotate(v){const cz=Math.cos(q.roll),sz=Math.sin(q.roll),x=v[0]*cz-v[1]*sz,y=v[0]*sz+v[1]*cz,cp=Math.cos(q.pitch),sp=Math.sin(q.pitch),yy=y*cp-v[2]*sp,z=y*sp+v[2]*cp,cy=Math.cos(q.yaw),sy=Math.sin(q.yaw);return[x*cy+z*sy,yy,-x*sy+z*cy];}
  const transform=(v,anchor=null)=>add(anchor||q.origin,rotate(v));
  function poly(points,color,tag,anchor=null){mesh.faces.push({points:points.map(v=>transform(v,anchor)),color:color.slice(),tag,id:serial++});}
  function box(c,size,color,tag,anchor=null){const v=Array.from({length:8},(_,k)=>c.map((n,i)=>n+(k&(1<<i)?1:-1)*size[i]/2));for(const f of [[0,4,6,2],[1,3,7,5],[0,1,5,4],[2,6,7,3],[0,2,3,1],[4,5,7,6]])poly(f.map(i=>v[i]),color,tag,anchor);}
  function tube(a,b,r,color,tag,anchor=null,sides=10){const axis=norm(sub(b,a)),x=norm(cross(axis,Math.abs(axis[1])>.9?[1,0,0]:[0,1,0])),y=norm(cross(axis,x)),rings=[a,b].map(c=>Array.from({length:sides},(_,i)=>add(c,add(mul(x,Math.cos(i/sides*Math.PI*2)*r),mul(y,Math.sin(i/sides*Math.PI*2)*r)))));poly(rings[0].slice().reverse(),color,tag,anchor);poly(rings[1],color,tag,anchor);for(let i=0;i<sides;i++)poly([rings[0][i],rings[0][(i+1)%sides],rings[1][(i+1)%sides],rings[1][i]],color,tag,anchor);}
  const detached=q.loading&&q.reloadProgress>=.18&&q.reloadProgress<=.86;
  if(special==='needle'){
   mesh.faces=mesh.faces.filter(f=>!['rivet-cassette','held-cassette','cassette-rivet'].includes(f.tag));
   const anchor=detached?mesh.anchors.reloadPart:null,c=detached?[0,0,0]:[0,-.105,.12];
   box(c,[.075,.09,.10],steel,detached?'held-needle-tray':'needle-tray',anchor);
   for(let i=0;i<3;i++){const x=c[0]+(i-1)*.021; tube([x,c[1]+.05,c[2]-.026],[x,c[1]+.05,c[2]+.022],.007,glass,'needle-window',anchor,6);tube([x,c[1]+.05,c[2]+.022],[x,c[1]+.05,c[2]+.044],.002,edge,'needle-tip',anchor,6);}
   box([-.044,.015,.12],[.012,.052,.105],glass,'pressure-window');
  }else if(special==='mortar40'){
   mesh.faces=mesh.faces.filter(f=>!['held-rocket','rocket-tip'].includes(f.tag));
   box([.074,.02,.22],[.025,.048,.12],clay,'mortar-sleeve');
   if(detached){const a=mesh.anchors.reloadPart;tube([0,0,-.045],[0,0,.025],.022,steel,'held-40mm',a);tube([0,0,-.049],[0,0,-.041],.025,brass,'40mm-rim',a);tube([0,0,.025],[0,0,.045],.019,clay,'40mm-cap',a);}
  }else{
   mesh.faces=mesh.faces.filter(f=>!['blade','blade-spine','handle','handle-wrap','guard'].includes(f.tag));
   box([0,-.065,0],[.045,.14,.055],dark,'saw-grip');box([0,.055,.09],[.095,.12,.18],clay,'saw-motor');
   tube([-.017,.14,.22],[.017,.14,.22],.112,edge,'ceramic-disc',null,18);
   const phase=!p.reduceMotion&&Number.isFinite(p.kick)&&p.kick>0?(Number.isFinite(p.phase)?p.phase:0)+p.kick*4:0;
   for(let i=0;i<12;i++){const a=i*Math.PI/6+phase;for(const side of [-1,1])box([side*.020,.14+Math.sin(a)*.090,.22+Math.cos(a)*.090],[.008,.010,.014],dark,'disc-slot');}
   tube([-.025,.14,.22],[.025,.14,.22],.025,brass,'disc-hub');
   box([0,.256,.20],[.085,.025,.17],steel,'saw-guard');tube([0,.10,.045],[0,.22,.045],.014,dark,'saw-handle');
   mesh.anchors.disc=transform([0,.14,.22]);
  }
  return mesh;
 }
 return {RECORDS,entry,identify,catalogue,filter,install,decorate};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralRegionalArsenal;
if(typeof document!=='undefined'&&typeof MistralFirstPerson!=='undefined')MistralRegionalArsenal.install(MistralFirstPerson,WEAPONS);
