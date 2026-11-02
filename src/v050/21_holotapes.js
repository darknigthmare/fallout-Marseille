/* Three original regional transcriptions extend the existing holodisc reader.
   The old lore flags remain the sole collection owner; these are authored props,
   not surveyed placements, recovered recordings or additional quest evidence. */
const MistralHolotapes=(()=>{
 const copy=value=>JSON.parse(JSON.stringify(value)),own=(value,key)=>!!value&&Object.hasOwn(value,key),finite=n=>typeof n==='number'&&Number.isFinite(n);
 const TAPES=[
  {id:'h58-atelier-releve',title:'La relève ne tient pas dans une colonne',speaker:'Mireille · copie des ateliers',scene:'aubagne',macro:'geo_huveaune',siteIndex:0,color:[.68,.42,.17],lines:[
   'Copie des ateliers. Mireille a laissé ces phrases avec les bordereaux de relève, pour que la personne suivante sache ce qui manque encore.',
   'Une liste peut compter les rations et oublier la personne qui vient les chercher. Avant de barrer un nom, demandez si quelqu’un l’attend à l’autre relais.',
   'Les Communes du Mistral discutent de l’eau à hauteur de table. Gardez les quantités, le nom de la personne qui remet et celui de la personne qui reçoit. Le mot partage ne remplit pas une citerne.',
   'CONCORDE appelle cela une exception de service. Nous appelons cela laisser une place au retour. Aucun de ces mots ne remplace le consentement de la famille.',
   'Si vous recopiez cette bande, conservez aussi les blancs du registre. Une réponse encore inconnue vaut mieux qu’une présence inventée.'
  ]},
  {id:'h58-deux-colonnes',title:'Le formulaire à deux colonnes',speaker:'Copie laissée au comptoir de Marseille',scene:'marseille',macro:'geo_marseille',siteIndex:1,color:[.23,.43,.52],lines:[
   'Transcription de comptoir. Deux copies du même formulaire CERFA-77 ont été déposées ici. Leur numéro concorde ; les colonnes, non.',
   'Sur la première, la case est vide parce que la personne n’a pas répondu. Sur la seconde, le vide est devenu un refus. Le robot ne voit pas la différence.',
   'La Convention des Cendres promet un droit d’exister sans justificatif. Cela ne nous dispense pas de demander à chacun quel nom peut circuler et auprès de qui.',
   'La personne qui tient le comptoir doit conserver les deux versions. N’effacez pas l’erreur pour rendre le registre plus propre ; notez comment vous l’avez constatée.',
   'Cette copie ne tranche aucun dossier. Elle rappelle pourquoi une preuve se recueille sur place et pourquoi personne ne doit conclure à votre place.'
  ]},
  {id:'h58-canal13-veille',title:'Canal 13 · la veille du passage',speaker:'Relais des Ronds-Points Libres',scene:'saintcharles',macro:'geo_marseille',siteIndex:2,color:[.62,.49,.12],lines:[
   'Canal 13, copie de veille. Les Gilets de Cendre demandent que ce message reste avec le registre du passage, même lorsque personne ne transmet.',
   'Un reflet jaune peut prévenir d’un obstacle. Il ne donne à personne le droit de réclamer un péage. Demandez qui a vu, où et à quel moment.',
   'Les Vigies des Crêtes distinguent une fumée observée d’un départ supposé. Reprenez leur prudence : les faits sur un feuillet, les questions sur un autre.',
   'Les Sans-Dossier ont besoin d’un lieu où attendre sans disparaître dans une file. N’annoncez pas un accueil avant que les personnes du relais aient donné leur accord.',
   'À la relève, comparez vos copies et nommez les secteurs encore sans réponse. Un ancien message qui tourne en boucle ne devient pas une autorisation de départ.'
  ]}
 ];
 const BY_ID=Object.fromEntries(TAPES.map(t=>[t.id,t])),WIDTH=.56,DEPTH=.42,TOP=.72,MAX_PLAYS=1000000;
 function known(id){return typeof id==='string'&&own(BY_ID,id);}
 function found(snapshot,id){return known(id)&&own(snapshot?.lore?.holotapes,id)&&snapshot.lore.holotapes[id]===true;}
 function normalize(snapshot){
  const s=copy(snapshot);s.lore??={};s.lore.holotapes??={};s.lore.holotapePlays??={};s.v018??={};s.v018.tapeBookmarks??={};
  for(const t of TAPES){
   if(!found(snapshot,t.id)){delete s.lore.holotapes[t.id];delete s.lore.holotapePlays[t.id];delete s.v018.tapeBookmarks[t.id];continue;}
   s.lore.holotapes[t.id]=true;const plays=snapshot.lore.holotapePlays?.[t.id];
   if(own(snapshot.lore.holotapePlays,t.id)&&Number.isInteger(plays)&&plays>=0)s.lore.holotapePlays[t.id]=Math.min(MAX_PLAYS,plays);else delete s.lore.holotapePlays[t.id];
   const b=snapshot.v018?.tapeBookmarks?.[t.id];
   if(own(snapshot.v018?.tapeBookmarks,t.id)&&b&&Number.isInteger(b.index)&&finite(b.elapsed)&&b.elapsed>=0)s.v018.tapeBookmarks[t.id]={index:Math.max(0,Math.min(t.lines.length-1,b.index)),elapsed:Math.min(24000,b.elapsed)};else delete s.v018.tapeBookmarks[t.id];
  }return s;
 }
 function award(snapshot,id){if(!known(id))throw Error('Bande inconnue.');if(found(snapshot,id))throw Error('Cet exemplaire est déjà conservé.');const out=normalize(snapshot);out.lore.holotapes[id]=true;return out;}
 function targets(catalog=[]){return TAPES.map(t=>{const sites=catalog.filter(s=>s?.safe===true&&s.macro===t.macro&&['settlement','outpost','caravan'].includes(s.kind)).sort((a,b)=>String(a.id).localeCompare(String(b.id)));return{...copy(t),siteId:sites.length?sites[t.siteIndex%sites.length].id:null};});}
 function candidates(at,id){if(!Array.isArray(at)||at.length!==3||!at.every(finite)||!known(id))return[];const offset=TAPES.findIndex(t=>t.id===id)*.43;return[3.2,4.8,6.8,9].flatMap(r=>Array.from({length:16},(_,n)=>[at[0]+Math.cos(offset+n*Math.PI/8)*r,at[2]+Math.sin(offset+n*Math.PI/8)*r]));}
 function overlapsPlayer(pos,player,eye=1.65,radius=.38){if(!Array.isArray(pos)||!Array.isArray(player)||pos.length!==3||player.length!==3||!pos.every(finite)||!player.every(finite)||!finite(eye)||eye<=0||!finite(radius)||radius<=0)return true;if(player[1]-eye>=pos[1]+TOP-1e-7||player[1]+.18<=pos[1]+1e-7)return false;const dx=Math.max(0,Math.abs(player[0]-pos[0])-WIDTH/2),dz=Math.max(0,Math.abs(player[2]-pos[2])-DEPTH/2);return dx*dx+dz*dz<=(radius+.02)**2;}
 function model(id){if(!known(id))throw Error('Modèle de bande inconnu.');const parts=[],box=(pos,size,color)=>parts.push({mesh:'cube',pos,size,color}),metal=[.22,.25,.22],edge=[.50,.48,.36],ink=[.08,.10,.08],t=BY_ID[id];
  box([0,.34,0],[.44,.68,.32],metal);box([0,.705,0],[WIDTH,.03,DEPTH],edge);box([0,.75,0],[.32,.06,.23],t.color);box([0,.785,-.045],[.23,.012,.075],[.79,.75,.57]);
  for(const x of[-.085,.085]){box([x,.787,.055],[.085,.013,.085],ink);box([x,.796,.055],[.027,.009,.027],edge);}
  box([0,.792,-.045],[.16,.005,.009],ink);box([0,.751,.121],[.18,.022,.012],ink);return parts;
 }
 function archiveCounts(snapshot,zones=[]){return{historical:zones.filter(id=>own(snapshot?.lore?.holotapes,id)&&snapshot.lore.holotapes[id]===true).length,historicalTotal:zones.length,regional:TAPES.filter(t=>found(snapshot,t.id)).length,regionalTotal:TAPES.length};}
 return{TAPES,BY_ID,WIDTH,DEPTH,TOP,MAX_PLAYS,copy,known,found,normalize,award,targets,candidates,overlapsPlayer,model,archiveCounts};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralHolotapes;

if(typeof window!=='undefined'&&typeof baseState==='function'){
 const M=MistralHolotapes,copy=M.copy,runtime={owner:null,entries:[],draws:[],clock:0,depth:0,error:null,targets:M.targets(typeof V042_CATALOG==='undefined'?[]:V042_CATALOG)};
 // Extend the existing catalogue and flags rather than creating a second player.
 for(const t of M.TAPES)if(!Object.hasOwn(V013_LORE_CATALOG,t.id))V013_LORE_CATALOG[t.id]={tapeTitle:t.title,speaker:t.speaker,lines:t.lines.slice(),v058Original:true};
 const migration=migrateState;migrateState=function(raw={}){return M.normalize(migration(raw));};state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
 const previousGround=groundHeightAt;
 function ground(x,z,ignoreOwn=false){if(world?.v046){if(typeof v050TravelGround!=='function')return null;return v050TravelGround({records:world.v046Records,bank:world.v047TerrainBank||V046.terrain,geoColliders:(world.colliders||[]).filter(c=>c.v046Tile),v050GameplayColliders:(world.colliders||[]).filter(c=>!c.v046Tile&&(!ignoreOwn||!c.v058Holotape))},world,x,z,.40);}const h=previousGround(x,z);return Number.isFinite(h)?h:null;}
 groundHeightAt=function(x,z,feet=0){let h=previousGround(x,z,feet);if(!Number.isFinite(h)||runtime.owner?.world!==world)return h;for(const e of runtime.entries){const top=e.pos[1]+M.TOP;if(top>=h&&top<=feet+.72+1e-7&&v017ColliderHit(e.collider,x,z,state.player.crouched?.32:.38))h=top;}return h;};
 function supported(pos,ignoreOwn=false){const[x,y,z]=pos,b=world?.bounds;if(!b||x<b[0]+.8||x>b[1]-.8||z<b[2]+.8||z>b[3]-.8)return false;for(const[dx,dz]of[[0,0],[-.32,-.26],[-.32,.26],[.32,-.26],[.32,.26]]){const h=ground(x+dx,z+dz,ignoreOwn);if(h===null||Math.abs(h-y)>.15)return false;}return !(world.colliders||[]).some(c=>!c.disabled&&(!ignoreOwn||!c.v058Holotape)&&y+.84>=(c.minY??-Infinity)&&y<=(c.maxY??Infinity)&&v017ColliderHit(c,x,z,.44));}
 function anchor(t){if(world?.v046){if(world.id!==t.macro&&!(world.id==='geo_marseille_commune'&&t.macro==='geo_marseille'))return null;const r=t.siteId&&V042_RUNTIME.active.get(t.siteId);return r?.site?.safe===true&&r.pos?.every(Number.isFinite)?r.pos.slice():null;}return world?.id===t.scene&&world.spawn?.every(Number.isFinite)?world.spawn.slice():null;}
 function available(){return !!(gameStarted&&world&&state.player.hp>0&&!zoneTransitioning&&!V046.lab&&!V046.busy&&!V047.pending);}
 function physical(e){if(!e||e.world!==world||!runtime.entries.includes(e)||!supported(e.pos,true)||typeof onGround==='boolean'&&!onGround)return false;const p=state.player.pos;if(Math.hypot(p[0]-e.pos[0],p[2]-e.pos[2])>2.5||Math.abs(p[1]-playerEyeHeight()-e.pos[1])>.32||collidesAt(p[0],p[2],state.player.crouched?.32:.38,p[1]))return false;return lineOfSight(p,e.interaction);}
 function danger(){return (world?.enemies||[]).some(e=>e.alive&&e.alerted&&Math.hypot(e.pos[0]-state.player.pos[0],e.pos[2]-state.player.pos[2])<16);}
 function bind(force=false){const geo=world?.v046===true,sites=geo?[...V042_RUNTIME.active.keys()].sort().join('|'):'',found=M.TAPES.map(t=>M.found(state,t.id)?'1':'0').join(''),o=runtime.owner;
  if(!force&&!runtime.invalid&&o?.world===world&&o.state===state&&o.records===world?.v046Records&&o.sites===sites&&o.layer===settings.geoFalloutLayer&&o.lab===V046.lab&&o.interior===world?.v050CityInterior&&o.found===found)return runtime.entries.length;
  if(o?.world){o.world.colliders=o.world.colliders.filter(c=>!c.v058Holotape);o.world.interactables=o.world.interactables.filter(c=>!c.v058Holotape);}if(world&&o?.world!==world){world.colliders=world.colliders.filter(c=>!c.v058Holotape);world.interactables=world.interactables.filter(c=>!c.v058Holotape);}runtime.entries=[];runtime.draws=[];runtime.invalid=false;runtime.owner={world,state,records:world?.v046Records,sites,layer:settings.geoFalloutLayer,lab:V046.lab,interior:world?.v050CityInterior,found};
  if(!world||V046.lab||world.v050CityInterior||geo&&!settings.geoFalloutLayer)return 0;
  for(const tape of runtime.targets){if(M.found(state,tape.id))continue;const at=anchor(tape);if(!at)continue;let pos=null;
   for(const[x,z]of M.candidates(at,tape.id)){const y=ground(x,z);if(y===null)continue;const p=[x,y,z];if(!supported(p)||M.overlapsPlayer(p,state.player.pos,playerEyeHeight(),state.player.crouched?.32:.38)||(world.interactables||[]).some(i=>!i.v058Holotape&&Math.hypot(i.pos[0]-x,i.pos[2]-z)<(i.priority>=7?(i.radius||3.2)+2:1.05))||(world.npcs||[]).some(n=>n.alive!==false&&Math.hypot(n.pos[0]-x,n.pos[2]-z)<1.25)||(world.hazards||[]).some(h=>Math.hypot((h.x??h.pos?.[0]??Infinity)-x,(h.z??h.pos?.[2]??Infinity)-z)<(h.radius||0)+.8)||!lineOfSight([at[0],at[1]+playerEyeHeight(),at[2]],[x,y+.80,z]))continue;pos=p;break;}if(!pos)continue;
   const collider=addCollider(world,pos[0],pos[2],M.WIDTH,M.DEPTH,{id:'holotape58:'+tape.id,minY:pos[1],maxY:pos[1]+M.TOP-.005});collider.v058Holotape=tape.id;
   const entry={tape,world,pos,collider,interaction:[pos[0],pos[1]+.80,pos[2]]};runtime.entries.push(entry);const temporary={staticDraws:[]};for(const[n,p]of M.model(tape.id).entries()){const d=addPart(temporary,p.mesh,p.pos.map((v,i)=>v+pos[i]),p.size,p.color,0,{id:'holotape58:'+tape.id+':'+n});d.v058Holotape=tape.id;}runtime.draws.push(...temporary.staticDraws);
   const it=addInteract(world,'holotape58:'+tape.id,entry.interaction,'Prendre l’holobande · '+tape.title,()=>pickup(tape.id),{radius:2.5,kind:'holotape',priority:5.15,condition:()=>available()&&mode==='PLAYING'&&physical(entry)&&!danger()});it.v058Holotape=tape.id;
  }return runtime.entries.length;
 }
 function pickup(id){const entry=runtime.entries.find(e=>e.tape.id===id);if(!available()||mode!=='PLAYING'||runtime.depth||!physical(entry)||danger()||M.found(state,id))return false;const owner=state,scene=world,before=copy(owner);let next;
  try{next=M.award(owner,id);}catch(error){runtime.error=String(error.message||error);return false;}runtime.depth++;
  try{owner.lore=next.lore;if(state!==owner||world!==scene||!physical(entry)||saveGame(false)===false)throw Error('La collecte ne peut pas être sauvegardée.');runtime.error=null;}
  catch(error){if(state===owner){for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}runtime.error=String(error.message||error);try{toast('Collecte annulée : '+runtime.error,'bad');}catch{}return false;}
  finally{runtime.depth--;}
  // Persistence owns the result. A later rendering/toast failure cannot undo it.
  try{bind(true);toast('Holobande conservée · RADIO → HOLODISQUES · '+entry.tape.title,'good');updateHUD();}catch(error){runtime.error='Présentation après sauvegarde : '+String(error.message||error);}return true;
 }
 const collectLegacy=collectHolotape;collectHolotape=function(id){return M.known(id)?pickup(id):collectLegacy(...arguments);};
 const openLegacy=openHolotape;openHolotape=function(id){if(!M.known(id))return openLegacy(...arguments);if(!available()||!M.found(state,id))return false;if(!v027Open('radio','tapes'))return false;V027.selected=id;return v027TapeStart(id);};
 const startLegacy=v027TapeStart;v027TapeStart=function(id){if(M.known(id)&&(!available()||!M.found(state,id)))return false;const result=startLegacy(...arguments);if(result!==false&&M.known(id))state.lore.holotapePlays[id]=Math.min(M.MAX_PLAYS,state.lore.holotapePlays[id]||0);return result;};
 const detailLegacy=v027TapeDetail;v027TapeDetail=function(row){const html=detailLegacy(...arguments);return M.known(row?.id)?html+'<p class="p27-muted">Récit original de Mistral, transcrit pour cette bande. Aucun enregistrement vocal ni preuve de quête supplémentaire.</p>':html;};
 // The older DATA archive enumerates historical zones, unlike the radio reader.
 // Keep that denominator accurate and route additional bands to the same reader.
 const archiveLegacy=renderPipData;renderPipData=function(c){const result=archiveLegacy(...arguments),button=c.querySelector?.('[data-v13data="holotapes"]');if(!button)return result;
  const counts=M.archiveCounts(state,ALL_ZONE_IDS);button.textContent='HOLODISQUES HISTORIQUES ('+counts.historical+'/'+counts.historicalTotal+')';const previous=button.onclick;
  button.onclick=function(...a){const r=previous?.apply(this,a),detail=c.querySelector('#dataDetail'),heading=detail?.querySelector('h3');if(heading)heading.textContent='HOLODISQUES HISTORIQUES · '+counts.historical+'/'+counts.historicalTotal;if(!detail)return r;const current=M.archiveCounts(state,ALL_ZONE_IDS),owner=state;
   detail.insertAdjacentHTML('beforeend','<section class="archive-card"><h3>Bandes des relais · '+current.regional+'/'+current.regionalTotal+'</h3><p>Les trois récits originaux des relais rejoignent le lecteur RADIO → HOLODISQUES, avec les bandes historiques et leurs marque-pages.</p><button type="button" data-h58-radio>OUVRIR LE LECTEUR DES BANDES</button></section>');const open=detail.querySelector('[data-h58-radio]');if(open)open.onclick=()=>state===owner&&available()?v027Open('radio','tapes'):false;return r;
  };return result;
 };
 const publish=v046Publish;v046Publish=function(...a){const r=publish(...a);if(a[0]===world)runtime.invalid=true;return r;};
 const draw=collectDraws;collectDraws=function(...a){const result=draw(...a);bind();return result.concat(runtime.draws);};
 const update=updatePlayer;updatePlayer=function(dt){const r=update(dt);runtime.clock+=Number.isFinite(dt)&&dt>0?dt:0;if(runtime.clock>=.75){runtime.clock=0;bind();}return r;};
 function info(){bind();return{found:M.TAPES.filter(t=>M.found(state,t.id)).map(t=>t.id),physical:runtime.entries.map(e=>({id:e.tape.id,name:e.tape.title,scene:e.tape.scene,siteId:e.tape.siteId,pos:e.pos.slice(),interaction:e.interaction.slice(),usable:available()&&mode==='PLAYING'&&physical(e)&&!danger()})),draws:runtime.draws.length,error:runtime.error,owner:'state.lore.holotapes',reader:'RADIO → HOLODISQUES',provenance:'Original authored props, placements and transcriptions; no recorded voice or surveyed architecture'};}
 globalThis.v058HolotapesAfterInit=function(){Object.assign(window.__MISTRAL_DEBUG,{v058HolotapesInfo:info,v058HolotapesPickup:pickup,v058HolotapesOpen:id=>openHolotape(id),v058HolotapesBind:()=>bind(true),v058HolotapesCatalog:()=>copy(runtime.targets)});bind(true);};
}
