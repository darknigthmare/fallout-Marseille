/* Native adapter: bounded fire hazards and actual, checkpointed escort movement.
 * Fictional annexe at an existing approximate anchor; no surveyed geometry edits. */
if(typeof baseState==='function'&&typeof MistralSecours!=='undefined'){
  const M=MistralSecours,copy=o=>JSON.parse(JSON.stringify(o)),TITLE='LES VIVANTS DERRIÈRE LA PORTE';
  const P={farah:[-7,0,26],console:[-5,0,13],power:[-19,0,3],fuel:[19,0,3],lance:[0,0,6],'door:lila':[-18,0,-6],'door:remi':[18,0,-6],sortie:[0,0,28]};
  const rt={busy:false,error:null,saveBlocked:null};
  const anchor=v042Site(MistralLys.ANCHOR);
  if(anchor&&!v042Site(M.SITE_ID)){
    const s={...copy(anchor),id:M.SITE_ID,name:'Annexe des secours · Les vivants derrière la porte',description:'Poste insulaire des Marins-Sapeurs. Scène fictionnelle d’évacuation, pas une caserne réelle relevée.',kind:'interior',interior:'secours',faction:'secours',factionLabel:'Marins-Sapeurs de la Rade',tier:1,safe:true,visitable:true,unique:true,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],enemyRadius:0,rewardCaps:0,rewardXP:0,respawnHours:0,provenance:{kind:'authored-fiction',anchorId:MistralLys.ANCHOR,scope:'Approximate island anchor, no surveyed fire station or coastline changes.'}};
    V042_CATALOG.push(s);V042_SITE_BY_ID[s.id]=s;V042_SITES_BY_MACRO[s.macro].push(s);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[s.macro]++;
  }
  const base=baseState;baseState=function(...a){const s=base(...a);s.v070Secours=M.fresh();return s;};
  const migrate=migrateState;migrateState=function(raw={}){const s=migrate(...arguments);s.v070Secours=M.migrate(raw?.v070Secours);return s;};
  state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
  const local=()=>!!world?.v070Secours&&state.v042?.activeInterior===M.SITE_ID;
  const where=id=>M.IDS.includes(id)?world?.npcs.find(n=>n.id==='s70:'+id)?.pos:P[id];
  const notice=t=>{V027.message=t;toast(t,'bad');return false;};
  function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc de test sans progression.':zoneTransitioning||V046.busy||V047.pending?'Chargement en cours.':!onGround?'Rejoignez le sol.':inCombat?'Quittez le combat avant cet échange.':null;}
  function near(id){const p=where(id);if(!local()||!p)return false;if((id==='farah'||M.IDS.includes(id))&&!world.npcs.some(n=>n.id==='s70:'+id&&n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.2&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7]);}
  function restore(owner,before){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}
  function transact(type,id,revision){
    if(rt.busy)return false;const owner=state,scene=world,before=copy(owner);let next;
    try{next=M.apply(owner,{type,id},{local:local(),near:near(M.point(type,id)),point:M.point(type,id),blocked:blocked(),revision});}catch(e){return notice(e.message);}
    rt.busy=true;try{owner.v070Secours=next.v070Secours;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde du secours refusée.');}
    catch(e){restore(owner,before);return notice(e.message+' Opération annulée.');}finally{rt.busy=false;}
    if(type==='follow'||type==='wait')rt.saveBlocked=null;
    try{visuals(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='finish'?'Deux personnes revenues · 60 capsules, une fois.':'Secours sauvegardé.','good');}catch(e){rt.error=e.message;}return true;
  }
  function guard(fn){const owner=state,scene=world,rev=state.v070Secours.revision;return()=>state===owner&&world===scene&&rev===state.v070Secours.revision?fn(rev):notice('Cette conversation est périmée.');}
  const back=()=>({text:'Revenir.',onChoose:closeDialogue});
  function talk(id){
    if(blocked()||!near(id))return notice(blocked()||'Rejoignez cette personne.');const l=state.v070Secours,ch=[];let text,name,role;
    if(id==='farah'){
      name='Farah Serra';role='Marin-Sapeur · chef d’intervention';
      text='« Lila et Rémi sont dans les deux compartiments protégés. La fumée vient du groupe auxiliaire ; le poste a gardé ses portes fermées en attendant une identification conforme. Rémi est une goule consciente, pas un colis contaminé. Coupez les alimentations, déchargez le dispositif du poste, puis ouvrez. Je tiens le rassemblement. Ramenez les deux, pas leur numéro. »';
      if(!l.opened)ch.push({text:'Prendre en charge l’évacuation.',onChoose:guard(rev=>{transact('open',null,rev);talk(id);})});
      if(l.order.length===2&&!l.finished)ch.push({text:'Confirmer les deux arrivées · 60 capsules.',onChoose:guard(rev=>{transact('finish',null,rev);talk(id);})});
    }else{
      const p=M.PEOPLE[id];if(!p)return false;name=p.name;role=p.role;text=p.text;
      const phase=l.people[id].mode;
      if(phase==='safe')text+='\n\n« Je suis au rassemblement. Ma présence vaut davantage qu’une ligne dans leur machine. »';
      else if(l.doors[id]){
        if(phase==='following')ch.push({text:'Attendre ici, je reviens.',onChoose:guard(rev=>{transact('wait',id,rev);talk(id);})});
        else if(!M.IDS.some(k=>l.people[k].mode==='following'))ch.push({text:'Suivez-moi jusqu’au rassemblement.',onChoose:guard(rev=>{if(transact('follow',id,rev))closeDialogue();})});
      }
      text+='\n\n« Restez dans le couloir balisé. Si je vous perds de vue, je m’arrête. Dites-moi quand vous devez faire une pause. »';
    }
    ch.push(back());openDialogue(speaker(name,role.toUpperCase(),'MS'),text+'\n\n'+M.briefing(l),ch);return true;
  }
  function control(id){
    if(blocked()||!near(id))return false;const l=state.v070Secours,ch=[];let text='';
    if(id==='console'){
      text='POSTE DE SECOURS — Les deux compartiments restent protégés par une arrivée d’air distincte. Le couloir contient encore un foyer, de la fumée et un câble sous tension.\n\nCommandes du poste : sectionneur gauche, alimentation droite, puis lance centrale. Une procédure technique peut commander les deux isolations avec un circuit.';
      if(l.opened&&!l.briefed)ch.push({text:'Lire les repères du poste.',onChoose:guard(rev=>{transact('brief',null,rev);control(id);})});
    }else if(id==='power'||id==='fuel'){
      text=id==='power'?'Le sectionneur isole le câble détérioré et le moteur du groupe. Il ne coupe pas l’air indépendant des compartiments.':'Le robinet d’arrêt coupe l’alimentation du groupe auxiliaire. Le foyer résiduel doit encore être traité par le dispositif fixe.';
      if(!l[id])ch.push({text:id==='power'?'Isoler le courant.':'Fermer l’alimentation.',onChoose:guard(rev=>{transact('isolate',id,rev);control(id);})});
    }else if(id==='lance'){
      text=l.extinguished?'Le foyer est éteint et le couloir ventilé. Le dispositif reste en position de sécurité.':'La charge du poste est déjà réservée au secours. Les deux isolations sont nécessaires avant la décharge manuelle ; aucune ressource personnelle n’est obligatoire.';
      if(!l.extinguished)ch.push({text:'Actionner le dispositif manuel du poste.',onChoose:guard(rev=>{transact('extinguish','manuel',rev);control(id);})},{text:'Commande technique · INT 5 + 1 circuit.',onChoose:guard(rev=>{transact('extinguish','technique',rev);control(id);})});
    }else{
      const who=id.slice(5);text='Verrou mécanique du compartiment de '+M.PEOPLE[who].name+'. Il ouvre une issue dans le couloir sécurisé sans exiger une identité valide.';
      if(!l.doors[who])ch.push({text:'Ouvrir cette issue de secours.',onChoose:guard(rev=>{transact('door',who,rev);control(id);})});
    }
    ch.push(back());openDialogue(speaker(id==='console'?'Consigne du poste':id==='lance'?'Dispositif de secours':id==='power'?'Sectionneur':id==='fuel'?'Arrêt du groupe':'Issue du compartiment','MARINS-SAPEURS · ANNEXE','MS'),text,ch);return true;
  }
  function visuals(w){
    if(!w?.v070Secours)return;const l=state.v070Secours;
    for(const d of w.staticDraws){if(d.s70Fire)d.hidden=!!l.extinguished;if(d.s70Smoke)d.hidden=!!l.extinguished;if(d.s70Cable)d.hidden=l.power;if(d.s70Door)d.hidden=l.doors[d.s70Door];if(d.s70Control)d.color=l[d.s70Control]?[.24,.66,.41]:[.78,.25,.16];if(d.s70Safe)d.hidden=l.people[d.s70Safe].mode!=='safe';}
    for(const c of w.colliders)if(c.s70Door)c.disabled=l.doors[c.s70Door];
    w.hazards=w.hazards.filter(h=>!h.id.startsWith('s70:'));
    if(!l.extinguished){addHazard(w,'s70:fire',0,0,3,{damage:4,kind:'fire',label:'Foyer du groupe'});addHazard(w,'s70:smoke',0,-5,4,{kind:'smoke',label:'Fumée du couloir'});}
    if(!l.power)addHazard(w,'s70:cable',-19,-1,1.5,{damage:3,label:'Câble sous tension'});
    for(const id of M.IDS){const n=w.npcs.find(n=>n.id==='s70:'+id);if(n){n.pos=M.position(id,l.people[id].progress);n.home=n.pos.slice();n.moving=false;}}
  }
  function build(){
    const w=createWorld(V042_INSTANCE_ZONE,'Annexe des secours — Les vivants derrière la porte','MARINS-SAPEURS · SCÈNE FICTIONNELLE',{skyTop:[37,51,65],skyBottom:[124,110,88],fog:[.32,.34,.35],wind:.3,daylight:.48,indoor:false});
    w.v070Secours=true;w.bounds=[-23,23,-30,32];w.spawn=[0,1.65,28];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE_ID;rt.saveBlocked=null;
    const grey=[.38,.41,.42],red=[.55,.16,.12],metal=[.18,.23,.25],cream=[.70,.65,.51];
    const box=(p,s,c=grey,solid=false,key=null,val=true)=>{const d=addBox(w,p,s,c);if(key)d[key]=val;if(solid){const col=addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});if(key)col[key]=val;}return d;};
    const sign=(x,y,z,t)=>v021Sign(w,x,y,z,t,.065);
    box([0,-.2,1],[46,.4,62],grey);addFloorZone(w,0,1,46,62,0,{priority:1});
    for(const x of [-22.7,22.7])box([x,2.5,1],[.6,5,62],grey,true);
    box([0,2.5,-29.7],[46,5,.6],grey,true);for(const x of [-14,14])box([x,2.5,31.7],[18,5,.6],grey,true);
    // Two fire compartments. Protected occupants are never on the hazard patches.
    for(const [x,width]of [[-21,4],[0,20],[21,4]])box([x,2,-10],[width,4,.4],grey,true);
    box([0,2,-20],[.4,4,20],grey,true);
    for(const [id,x]of [['lila',-14],['remi',14]]){
      box([x,1.9,-10],[8,3.8,.35],red,true,'s70Door',id);sign(x,4.1,-9.72,id==='lila'?'COMPARTIMENT LILA':'COMPARTIMENT REMI');
      box([x,2.8,-29.3],[4,.6,.15],[.35,.53,.58]);box([x+4,.45,-24],[2,.9,3],cream,true);
    }
    // Corridors stay wide enough for one guide and an evacuee, no mandatory jump.
    for(const x of [-14,14])box([x,.012,6],[.12,.024,31],[.84,.75,.37]);
    for(const x of [-4,4]){box([x,.02,21],[3,.04,3],[.28,.47,.37]);box([x+(x<0?-2:2),.75,22],[.16,1.5,.16],[.37,.68,.45],false,'s70Safe',x<0?'lila':'remi');}
    // Damaged generator, finite local effects. No volumetric-fluid claim.
    box([0,.7,0],[3.2,1.4,3],metal,true);box([0,1.7,-.4],[2.5,.6,1.8],red);
    for(let i=0;i<5;i++){const d=addPart(w,'cone',[-1.1+i*.55,1.7+(i%2)*.3,.4],[.7,2.3,.7],i%2?[.90,.36,.09]:[.76,.18,.06]);d.s70Fire=true;d.emissive=.7;}
    for(let i=0;i<5;i++){const d=addPart(w,'sphere',[(i%2)*1.6-.8,3.1+i*.42,-.5-i*.8],[2.0+i*.22,.7,1.9],[.29,.29,.28]);d.s70Smoke=true;}
    for(let i=0;i<4;i++)box([-19+i*.2,.12,-1],[.10,.14,.7],[.88,.72,.30],false,'s70Cable');
    for(const id of ['power','fuel','lance','door:lila','door:remi']){const p=P[id];box([p[0],.65,p[2]],[1.0,1.3,.8],metal,true);box([p[0],1.35,p[2]+.1],[.55,.18,.35],id==='lance'?red:[.78,.25,.16],false,id==='power'||id==='fuel'?'s70Control':null,id);}
    box([-5,1.2,13],[2,2.4,.18],cream,true);sign(-5,2.7,13.12,'SECOURS / DEUX PRESENTS');
    // Hose from reserved station to the fixed generator nozzle, purely authored geometry.
    box([0,.10,4],[.18,.16,3],red);box([0,.10,2],[1.8,.16,.18],red);
    box([18,1.1,23],[5,2.2,6],red,true);box([18,2.25,23],[5.1,.12,6.1],cream);box([18,1.4,26.1],[3,.6,.08],metal);sign(18,3,26,'SECOURS');
    sign(0,3,31,'SORTIE / PASSEUR');sign(0,3,18,'RASSEMBLEMENT');
    addHumanNPC(w,'s70:farah','Farah Serra','Marin-Sapeur',P.farah,[.54,.14,.10],{yaw:Math.PI});
    for(const id of M.IDS){const p=M.PEOPLE[id];addHumanNPC(w,'s70:'+id,p.name,p.role,M.position(id,state.v070Secours.people[id].progress),id==='lila'?[.29,.42,.50]:[.41,.40,.30],{skin:id==='remi'?[.48,.46,.33]:undefined,yaw:Math.PI});}
    for(const id of ['console','power','fuel','lance','door:lila','door:remi']){const p=P[id];addInteract(w,'s70:'+id,[p[0],1.25,p[2]+.7],id==='console'?'Lire la consigne':id==='lance'?'Utiliser le dispositif de secours':id.startsWith('door:')?'Ouvrir l’issue':id==='power'?'Isoler le courant':'Couper l’alimentation',()=>control(id),{radius:3.2,priority:5,kind:'quest',condition:()=>!blocked()&&near(id)});}
    addInteract(w,'s70:sortie',[0,1.25,28.7],'Retourner au départ',()=>!blocked()&&near('sortie')&&v042ExitInstance(),{radius:3.2,priority:5,kind:'door'});
    w.levelRoutes=[{id:'secours-lila',points:M.PEOPLE.lila.path},{id:'secours-remi',points:M.PEOPLE.remi.path}];visuals(w);return w;
  }
  const buildBase=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE_ID?build():buildBase(...arguments);};
  const talkBase=talkToNPC;talkToNPC=function(id){return typeof id==='string'&&id.startsWith('s70:')?talk(id.slice(4)):talkBase(...arguments);};
  const claimBase=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE_ID?false:claimBase(...arguments);};
  function escortTick(dt){
    if(!local()||!gameStarted||mode!=='PLAYING'||zoneTransitioning||V046.busy||V047.pending||V046.lab||inCombat||!(state.player.hp>0)||rt.busy)return;
    const owner=state,scene=world,l=owner.v070Secours,id=M.IDS.find(k=>l.people[k].mode==='following');
    for(const n of scene.npcs)if(n.id.startsWith('s70:'))n.moving=false;
    if(!id||rt.saveBlocked||!Number.isFinite(dt)||dt<=0)return;
    const npc=scene.npcs.find(n=>n.id==='s70:'+id);if(!npc?.alive)return;
    const current=M.position(id,l.people[id].progress),player=owner.player.pos,d=Math.hypot(player[0]-current[0],player[2]-current[2]);
    if(d>7||d<.9||Math.abs(player[1]-current[1]-1.65)>2||!lineOfSight([current[0],current[1]+1.3,current[2]],player))return;
    let next;try{next=M.advance(l,id,Math.max(1,Math.round(Math.min(.2,dt)*1200)));}catch(e){rt.error=e.message;return;}
    const p=next.position;if(Math.hypot(player[0]-p[0],player[2]-p[2])>d+.005||collidesAt(p[0],p[2],.35,p[1]+1.65))return;
    const before=next.checkpoint?copy(owner):null;owner.v070Secours=next.ledger;
    if(next.checkpoint){
      try{if(owner!==state||scene!==world||saveGame(false)===false)throw Error('Point de secours non sauvegardé.');}
      catch(e){restore(owner,before);rt.saveBlocked=id;visuals(scene);notice(e.message+' Dites à la personne d’attendre, puis reprenez.');return;}
    }
    if(owner!==state||scene!==world)return;
    npc.pos=p;npc.home=p.slice();npc.yaw=Math.atan2(p[0]-current[0],current[2]-p[2]);npc.moving=!next.arrived;
    if(next.arrived){visuals(scene);updateQuestUI(true);toast(M.PEOPLE[id].name+' au rassemblement.','good');}
  }
  const npcBase=updateNPCSchedules;updateNPCSchedules=function(dt){if(!local())return npcBase(...arguments);escortTick(dt);};
  const exitBase=v042ExitInstance;v042ExitInstance=function(){
    if(local()&&M.IDS.some(id=>state.v070Secours.people[id].mode==='following')){
      const owner=state,before=copy(owner);try{owner.v070Secours=M.pause(owner.v070Secours);if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('La pause de l’accompagnement ne peut pas être sauvegardée.');}visuals(world);
    }return exitBase(...arguments);
  };
  function portNear(site){if(!MistralLys.PORTS.includes(site)||!world?.geoMacro||!world.v046||state.v042?.activeInterior||world.v050CityInterior||!settings.geoFalloutLayer||!v042SiteDiscovered(v042Site(site)))return false;const p=state.player.pos;if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,p))return false;return world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===site&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
  function sail(site){
    if(blocked()||!portNear(site))return false;const owner=state,scene=world,before=copy(owner),maps={active:new Map(V042_RUNTIME.active),npcs:new Map(V042_RUNTIME.npcData),nearest:V042_RUNTIME.nearest,instance:V042_RUNTIME.instanceSite,retained:V048.retained};const save=saveGame;let wrote=false;
    saveGame=function(...a){const r=save(...a);if(r===false)throw Error('Départ non sauvegardé.');wrote=true;return r;};
    try{if(!v042EnterSite(M.SITE_ID))throw Error('Départ interrompu.');return true;}
    catch(e){restore(owner,before);world=scene;V042_RUNTIME.active=maps.active;V042_RUNTIME.npcData=maps.npcs;V042_RUNTIME.nearest=maps.nearest;V042_RUNTIME.instanceSite=maps.instance;V048.retained=maps.retained;if(typeof v049Own==='function')v049Own(world);if(wrote){try{save(false);}catch{}}return notice(e.message);}finally{saveGame=save;}
  }
  function crossing(site){if(blocked()||!portNear(site))return false;openDialogue(speaker('Relais de secours','MARINS-SAPEURS DE LA RADE','MS'),'Une annexe insulaire signale deux personnes derrière ses portes de sécurité. Les compartiments tiennent ; le couloir doit être dégagé avant l’évacuation. Le passage est gratuit, sans justificatif de faction.\n\nTraversée narrative par chargement vers une scène fictionnelle. Retour au point de départ ; pas de bateau pilotable.',[{text:'Rejoindre les Marins-Sapeurs.',onChoose:guard(()=>sail(site))},back()]);return true;}
  const relayBase=v042TalkNPC;v042TalkNPC=function(id){const site=V042_RUNTIME.npcData.get(id)?.siteId;if(blocked()||!portNear(site))return relayBase(...arguments);const old=openDialogue;openDialogue=function(s,t,ch,...rest){return old(s,t,[...(ch||[]).slice(0,-1),{text:'Secours de la Rade · Les vivants derrière la porte',onChoose:guard(()=>crossing(site))},...(ch||[]).slice(-1)],...rest);};try{return relayBase(...arguments);}finally{openDialogue=old;}};
  function track(){if(blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=MistralLys.PORTS[0];try{if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Repère non sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
  V027_SUBS.data.secours='MARINS-SAPEURS';
  const data=v027Data;v027Data=function(c){if(V027.sub!=='secours')return data(...arguments);const l=state.v070Secours,esc=v027Escape;c.innerHTML='<div class="p27-long"><p class="p27-kicker">AUCUN VIVANT SANS SECOURS</p><h2>Les vivants derrière la porte</h2><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre le départ du Vieux-Port','s70:track')+'<p>Autre départ : Ratonneau. Les secours ne demandent aucune allégeance.</p><h3>Couloir</h3><p>'+esc(l.power?'Courant isolé.':'Câble encore sous tension.')+' '+esc(l.fuel?'Alimentation fermée.':'Groupe encore alimenté.')+' '+esc(l.extinguished?'Foyer éteint.':'Foyer et fumée présents.')+'</p><h3>Personnes, pas dossiers</h3>'+M.IDS.map(id=>'<p>'+esc(M.PEOPLE[id].name)+' : '+esc({waiting:'attend à sa position',following:'vous accompagne',safe:'au rassemblement'}[l.people[id].mode])+'</p>').join('')+'<p>Une personne à la fois, proche et visible, par le couloir balisé. Les compartiments disposent d’une arrivée d’air indépendante. Farah rémunère l’intervention après les deux arrivées.</p></div>';};
  const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='s70:track'?v027CanAct()&&track():dispatch(...arguments);};
  const rows=v027QuestRows;v027QuestRows=function(){const l=state.v070Secours;return rows(...arguments).concat(l.opened?[{id:'s70:quest',name:TITLE,stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:[['Foyer neutralisé',!!l.extinguished],['Lila accompagnée',l.people.lila.mode==='safe'],['Rémi accompagné',l.people.remi.mode==='safe'],['Rapport à Farah',l.finished]],source:'Marins-Sapeurs',badge:l.finished?'✓':'',hint:'Relais du Vieux-Port ou de Ratonneau'}]:[]);};
  const oldTrack=v027Track;v027Track=function(id){return id==='s70:quest'?track():oldTrack(...arguments);};
  function next(){const l=state.v070Secours;if(!l.opened)return'farah';if(!l.briefed)return'console';if(!l.extinguished)return!l.power?'power':!l.fuel?'fuel':'lance';const following=M.IDS.find(id=>l.people[id].mode==='following');if(following)return following;const id=M.IDS.find(id=>l.people[id].mode!=='safe');return id?l.doors[id]?id:'door:'+id:'farah';}
  const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return marker(...arguments);const id=next(),p=where(id);return{zone:world.id,pos:[p[0],p[1]+1.25,p[2]+.7],label:M.PEOPLE[id]?.name||'Marins-Sapeurs · '+id};};
  const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local())return ui(...arguments);$('questTitle').textContent=TITLE;$('questObjective').textContent=M.briefing(state.v070Secours);if(flash){const f=$('questFlash');f.querySelector('strong').textContent=TITLE;f.querySelector('p').textContent=M.briefing(state.v070Secours);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
  V027_STATIONS.secours={name:'Marins-Sapeurs — les présents du quai',freq:'18.7',hint:'Une peau irradiée ne retire pas le droit au secours',available:()=>state.v070Secours.opened,text:()=>M.briefing(state.v070Secours)};
  const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v070SecoursInfo:()=>({ledger:copy(state.v070Secours),points:copy({...P,...Object.fromEntries(M.IDS.map(id=>[id,where(id)||M.position(id,state.v070Secours.people[id].progress)]))}),local:local(),saveBlocked:rt.saveBlocked,error:rt.error}),v070SecoursOpen:()=>v027Open('data','secours'),v070SecoursAction:transact});};
}
