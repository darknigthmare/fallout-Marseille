/* Native adapter for La part des absents. No geography or previous ledger edits. */
if(typeof baseState==='function'&&typeof MistralParts!=='undefined'){
  const M=MistralParts,copy=o=>JSON.parse(JSON.stringify(o)),TITLE='LA PART DES ABSENTS';
  const PEOPLE={
    maelle:{name:'Maëlle Sarti',role:'Passeuse des Francs du Large',pos:[-8,0,23],text:'« J’ai ramené six caisses, pas une corne d’abondance. Les gens repêchés mangent avant de négocier leur passage. Mais mes deux matelots ne se nourrissent pas de grands principes non plus. Montrez-moi les caisses à leur place ; je paierai vos bras, pas votre signature. »'},
    eloi:{name:'Éloi Ferrand',role:'Délégué des Sections libres',pos:[12,0,23],text:'« Le pain n’a pas de blason. J’avais apporté une déclaration d’adhésion pour les bénéficiaires… Nora m’a demandé si un naufragé pouvait la lire en tenant encore sa fille. Elle a raison sur ce point. Je garde mon bonnet ; ils garderont le droit de ne pas le porter. »'},
    nora:{name:'Nora Haddad',role:'Habitante du refuge',pos:[-17,0,9],text:'« On est six dans notre cuisine. Depuis hier, deux autres dorment sous l’auvent et personne ne sait encore leur nom. Je ne veux pas qu’ils prennent notre place. Je veux qu’on leur en fasse une. Compter les présents, ça ne doit pas effacer ceux qui arrivent. »'}
  };
  const DEST={cuisines:{name:'Cuisines du refuge',pos:[-15,0,17]},accueil:{name:'Accueil des naufragés',pos:[0,0,16]},equipage:{name:'Provision de l’équipage',pos:[15,0,17]}};
  const P={...Object.fromEntries(Object.entries(PEOPLE).map(([id,n])=>[id,n.pos])),notice:[-16,0,2],babord:[-9,0,0],tribord:[9,0,0],treuil:[15,0,-.5],sortie:[0,0,27]};
  M.CRATES.forEach((id,i)=>P['crate:'+id]=[-10+(i%3)*10,0,-13-Math.floor(i/3)*9]);
  for(const[id,d]of Object.entries(DEST))P['dest:'+id]=d.pos;
  const rt={busy:false,error:null};
  const anchor=v042Site(MistralLys.ANCHOR);
  if(anchor&&!v042Site(M.SITE_ID)){
    const site={...copy(anchor),id:M.SITE_ID,name:'Cale du Lys · La part des absents',description:'Déchargement après l’audience. Quai fictionnel accessible par les passeurs ; aucune nouvelle géométrie relevée.',kind:'interior',interior:'parts',faction:'lys',factionLabel:'Cour du Lys d’If',tier:1,safe:true,unique:true,visitable:true,npcSlots:0,npcRoles:[],enemySlots:0,enemyTypes:[],enemyRadius:0,rewardCaps:0,rewardXP:0,respawnHours:0,provenance:{kind:'authored-fiction',anchorId:MistralLys.ANCHOR,scope:'Approximate existing anchor; fictional loading yard, not a surveyed quay.'}};
    V042_CATALOG.push(site);V042_SITE_BY_ID[site.id]=site;V042_SITES_BY_MACRO[site.macro].push(site);V042_LAYER_META.siteCount++;V042_LAYER_META.visitable++;V042_LAYER_META.counts.interior++;V042_LAYER_META.macroCounts[site.macro]++;
  }
  const oldBase=baseState;baseState=function(...a){const s=oldBase(...a);s.v069Parts=M.fresh();return s;};
  const oldMigrate=migrateState;migrateState=function(raw={}){const s=oldMigrate(raw);s.v069Parts=M.migrate(raw?.v069Parts);return s;};
  state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
  const local=()=>!!world?.v069Parts&&state.v042?.activeInterior===M.SITE_ID;
  function ready(){try{return !!M.basis(state);}catch{return false;}}
  const notice=t=>{V027.message=t;toast(t,'bad');return false;};
  function blocked(){return !gameStarted||!['PLAYING','PIP','DIALOGUE','NOTE'].includes(mode)||!(state.player?.hp>0)?'Reprenez une partie active.':V046.lab?'Banc de test sans progression.':zoneTransitioning||V046.busy||V047.pending?'Attendez la fin du chargement.':!onGround?'Rejoignez le sol.':inCombat?'Quittez le combat avant la manutention.':null;}
  function near(id){const p=P[id];if(!local()||!p)return false;if(PEOPLE[id]&&!world.npcs.some(n=>n.id==='parts69:'+id&&n.alive))return false;return Math.hypot(state.player.pos[0]-p[0],state.player.pos[2]-p[2])<=3.6&&Math.abs(state.player.pos[1]-p[1]-1.4)<1.9&&lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.9]);}
  function portNear(site){if(!MistralLys.PORTS.includes(site)||!world?.geoMacro||!world.v046||state.v042?.activeInterior||world.v050CityInterior||!settings.geoFalloutLayer||!v042SiteDiscovered(v042Site(site)))return false;const p=state.player.pos;if(typeof v050TravelNearbyThreat==='function'&&v050TravelNearbyThreat(world,p))return false;return world.npcs.some(n=>n.alive!==false&&V042_RUNTIME.npcData.get(n.id)?.siteId===site&&Math.hypot(n.pos[0]-p[0],n.pos[2]-p[2])<=8&&Math.abs(n.pos[1]+1.4-p[1])<2.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.4,n.pos[2]]));}
  function restore(owner,before){if(state!==owner)return;for(const k of Object.keys(owner))delete owner[k];Object.assign(owner,before);}
  function act(type,id,revision){
    if(rt.busy)return false;const owner=state,scene=world,before=copy(owner);let next;
    try{next=M.apply(owner,{type,id},{local:local(),near:near(M.point(type,id)),point:M.point(type,id),blocked:blocked(),revision});}catch(e){return notice(e.message);}
    rt.busy=true;
    try{owner.v069Parts=next.v069Parts;owner.inventory=next.inventory;owner.player.caps=next.player.caps;if(state!==owner||world!==scene||saveGame(false)===false)throw Error('Sauvegarde de cargaison refusée.');}
    catch(e){restore(owner,before);return notice(e.message+' Opération annulée.');}
    finally{rt.busy=false;}
    try{visuals(world);updateQuestUI(true);updateHUD();if(mode==='PIP')renderPipboy();toast(type==='finish'?'Déchargement soldé · 40 capsules.':type==='deliver'?'Caisse déposée et sauvegardée.':type==='take'?'Caisse portée · retour possible au râtelier.':'Cargaison sauvegardée.','good');}catch(e){rt.error=e.message;}
    return true;
  }
  function guard(fn){const owner=state,scene=world,rev=state.v069Parts.revision;return()=>state===owner&&world===scene&&rev===state.v069Parts.revision?fn(rev):notice('Cette conversation est périmée.');}
  const back=()=>({text:'Revenir.',onChoose:closeDialogue});
  function talk(id){
    if(blocked()||!near(id))return notice(blocked()||'Rejoignez cet interlocuteur.');const p=PEOPLE[id],l=state.v069Parts,ch=[];if(!p)return false;
    if(id==='maelle'){
      if(!l.opened)ch.push({text:'Aider au déchargement des six caisses.',onChoose:guard(rev=>{act('open',null,rev);talk(id);})});
      if(l.opened&&!l.plan&&l.gate&&l.heard.length===2)for(const[key,plan]of Object.entries(M.PLANS))ch.push({text:'Examiner : '+plan.name,onChoose:guard(()=>confirm(key))});
      if(l.plan&&!l.finished&&Object.values(M.tally(l)).reduce((a,b)=>a+b,0)===6)ch.push({text:'Faire constater le déchargement · 40 capsules.',onChoose:guard(rev=>{act('finish',null,rev);talk(id);})});
    }else if(l.opened&&!l.heard.includes(id)&&!l.plan)ch.push({text:'Écouter sa position sur les rations.',onChoose:guard(rev=>{act('hear',id,rev);talk(id);})});
    ch.push(back());const source=M.basis(state);
    openDialogue(speaker(p.name,p.role.toUpperCase(),'PA'),p.text+'\n\n'+(source?M.REACTIONS[source.policy]+'\n\n':'')+M.briefing(l)+(l.plan?'\n\n'+M.PLANS[l.plan].text:''),ch);return true;
  }
  function confirm(id){if(blocked()||!near('maelle')||!Object.hasOwn(M.PLANS,id))return false;const plan=M.PLANS[id];openDialogue(speaker('Maëlle Sarti','SIX CAISSES · RÉPARTITION EXCLUSIVE','MS'),plan.text+'\n\nChaque caisse doit être portée et déposée au bon emplacement. Aucun bénéficiaire ne prête serment à la Convention ou à la Cour. Le règlement précédent demeure intact. Vous recevrez 40 capsules après la remise des six caisses, pas à la signature.',[{text:'Confirmer cette répartition.',onChoose:guard(rev=>{act('plan',id,rev);talk('maelle');})},{text:'Revenir aux propositions.',onChoose:guard(()=>talk('maelle'))}]);return true;}
  function control(id){
    if(blocked()||!near(id))return false;const l=state.v069Parts,ch=[];let text='';
    if(id==='notice'){
      text='CONSIGNE DU PONTON — Les deux amarres doivent être verrouillées avant d’abaisser la barrière. Les repères bâbord et tribord deviennent verts quand leurs verrous tiennent. Le treuil est à droite. Six caisses scellées attendent derrière la barrière ; elles appartiennent au lot collectif, pas à votre sac.\n\nLa dérivation technique commande les deux verrous avec un circuit ; le chemin manuel reste gratuit.';
      if(l.opened&&!l.notice)ch.push({text:'Examiner la consigne et les repères.',onChoose:guard(rev=>{act('read',null,rev);control(id);})});
    }else if(['babord','tribord'].includes(id)){
      text='Le verrou '+(id==='babord'?'bâbord':'tribord')+' retient le ponton de déchargement. '+(l.moored.includes(id)?'Sa butée est engagée.':'Engagez sa butée avant la manœuvre.');
      if(l.opened&&!l.gate&&!l.moored.includes(id))ch.push({text:'Sécuriser cette amarre.',onChoose:guard(rev=>{act('moor',id,rev);control(id);})});
    }else if(id==='treuil'){
      text=l.gate?'La barrière est abaissée. Aucun autre circuit n’est nécessaire.':'Deux verrous, puis la manivelle. Un seul verrou engagé ne suffit pas ; une tentative prématurée ne consomme rien.';
      if(l.opened&&!l.gate){ch.push({text:'Abaisser la barrière à la manivelle.',onChoose:guard(rev=>{act('gate','manuel',rev);control(id);})});ch.push({text:'Commander les verrous · INT 5 + 1 circuit.',onChoose:guard(rev=>{act('gate','technique',rev);control(id);})});}
    }ch.push(back());openDialogue(speaker(id==='notice'?'Consigne du ponton':id==='treuil'?'Treuil du ponton':'Amarre '+id,'MANUTENTION · LOT COLLECTIF','PA'),text,ch);return true;
  }
  function cargo(id){const l=state.v069Parts;if(!M.CRATES.includes(id))return false;return act(l.crates[id]==='held'?'return':'take',id);}
  function visuals(w){if(!w?.v069Parts)return;const l=state.v069Parts;
    for(const d of w.staticDraws){
      if(d.partsGate)d.hidden=!!l.gate;if(d.partsLowered)d.hidden=!l.gate;
      if(d.partsMoor)d.color=l.moored.includes(d.partsMoor)?[.25,.65,.38]:[.70,.34,.18];
      if(d.partsCrate)d.hidden=l.crates[d.partsCrate]!=='rack';
      if(d.partsDelivered){const {dest,index}=d.partsDelivered;d.hidden=index>=M.tally(l)[dest];}
      if(d.partsFlag)d.color=l.plan==='secours'?[.35,.64,.57]:l.plan==='rotation'?[.29,.43,.66]:l.plan==='quartiers'?[.72,.52,.28]:[.46,.45,.39];
    }
    for(const c of w.colliders){if(c.partsGate)c.disabled=!!l.gate;if(c.partsCrate)c.disabled=l.crates[c.partsCrate]!=='rack';if(c.partsDelivered)c.disabled=c.partsDelivered.index>=M.tally(l)[c.partsDelivered.dest];}
  }
  function build(){
    const w=createWorld(V042_INSTANCE_ZONE,'Cale du Lys — La part des absents','QUAI FICTIONNEL · SIX CAISSES, PAS UNE FLOTTE',{skyTop:[55,89,125],skyBottom:[174,163,133],fog:[.48,.51,.53],wind:.6,daylight:.65,indoor:false});
    w.v069Parts=true;w.bounds=[-23,23,-29,30];w.spawn=[0,1.65,26];w.spawnYaw=0;V042_RUNTIME.instanceSite=M.SITE_ID;
    const stone=[.51,.50,.43],metal=[.22,.29,.31],wood=[.48,.35,.21];
    const box=(p,s,c=stone,solid=false,tag=null,value=true)=>{const d=addBox(w,p,s,c);if(tag)d[tag]=value;if(solid){const co=addCollider(w,p[0],p[2],s[0],s[2],{minY:p[1]-s[1]/2,maxY:p[1]+s[1]/2});if(tag)co[tag]=value;}return d;};
    const sign=(x,y,z,text)=>{if(typeof v021Sign==='function')v021Sign(w,x,y,z,text,.065);};
    box([0,-.2,0],[46,.4,60]);addFloorZone(w,0,0,46,60,0,{priority:1});
    for(const x of [-22.7,22.7])box([x,2,-1],[.6,4,58],stone,true);
    box([0,2,-28.7],[46,4,.6],stone,true);
    for(const x of [-14.5,14.5])box([x,2,29.7],[20,4,.6],stone,true);
    for(const x of [-14.5,14.5])box([x,2,-3],[17,4,.5],metal,true);
    box([0,1.8,-3],[12,3.6,.38],[.64,.47,.17],true,'partsGate');
    box([0,.1,-3],[12,.18,2.5],[.58,.44,.21],false,'partsLowered');
    for(let x=-5;x<=5;x+=2)box([x,1.8,-2.76],[.12,3.4,.1],metal,false,'partsGate');
    // Warehouse gantry, columns and an open central route: no jump required.
    for(const x of [-20,20]){box([x,3.4,-16],[.6,6.8,.6],metal,true);box([x,.3,-16],[1,.6,1],stone,true);}
    box([0,6.7,-16],[41,.6,.7],metal);box([0,5.6,-16],[.08,1.8,.08],metal);box([0,4.8,-16],[1.2,.12,.25],[.69,.52,.22]);
    for(const z of [-9,-18,-26])box([0,4.9,z],[42,.2,.2],metal);
    for(const x of [-20,-15,-10,-5,0,5,10,15,20])box([x,.012,-16],[.07,.025,22],[.72,.65,.44]);
    for(const id of ['babord','tribord']){const p=P[id];box([p[0],.45,p[2]],[.8,.9,.8],metal,true);box([p[0],1,p[2]+.2],[.65,.2,.3],[.70,.34,.18],false,'partsMoor',id);}
    box([15,.55,-.5],[1.2,1.1,1],metal,true);addPart(w,'cylinder',[15,1.3,-.5],[.6,.3,.6],[.61,.43,.22]);
    box([-16,1.2,2],[2,2.4,.2],wood,true);sign(-16,2.8,1.9,'DEUX AMARRES / PUIS LE TREUIL');
    for(const id of M.CRATES){const p=P['crate:'+id];box([p[0],.08,p[2]],[1.8,.16,1.5],wood);box([p[0],.8,p[2]],[1.4,1.3,1.1],wood,true,'partsCrate',id);box([p[0],.8,p[2]+.57],[.18,1.25,.03],[.75,.70,.52],false,'partsCrate',id);sign(p[0],2.1,p[2]-.4,'CAISSE '+id);}
    for(const[id,d]of Object.entries(DEST)){
      const p=d.pos;box([p[0],.04,p[2]],[5,.08,3.4],metal);sign(p[0],3,p[2]-1.4,id==='cuisines'?'CUISINES':id==='accueil'?'NAUFRAGES':'EQUIPAGE');
      for(let i=0;i<4;i++){const pos=[p[0]-1.15+(i%2)*2.3,.7,p[2]-.7+Math.floor(i/2)*1.4];box(pos,[1.35,1.3,1.1],wood,true,'partsDelivered',{dest:id,index:i});box([pos[0],pos[1],pos[2]+.57],[.18,1.2,.03],[.75,.7,.52],false,'partsDelivered',{dest:id,index:i});}
    }
    box([0,3,29.2],[3,1,.1],stone,false,'partsFlag');sign(0,4.4,-4,'LA PART DES ABSENTS');sign(0,2.4,28.9,'RETOUR AU PASSEUR');
    for(const[id,p]of Object.entries(PEOPLE))addHumanNPC(w,'parts69:'+id,p.name,p.role,p.pos,id==='eloi'?[.57,.21,.19]:id==='nora'?[.46,.41,.31]:[.26,.39,.48],{dialogue:'parts69:'+id,yaw:Math.PI});
    for(const id of ['notice','babord','tribord','treuil']){const p=P[id];addInteract(w,'parts69:'+id,[p[0],1.25,p[2]+.9],id==='notice'?'Lire la consigne du ponton':id==='treuil'?'Manœuvrer le treuil':'Vérifier l’amarre '+id,()=>control(id),{radius:3.6,kind:'quest',priority:5,condition:()=>near(id)&&!blocked()});}
    for(const id of M.CRATES){const key='crate:'+id,p=P[key];addInteract(w,'parts69:'+key,[p[0],1.25,p[2]+.9],'Caisse '+id+' · prendre / reposer',()=>cargo(id),{radius:3.6,kind:'quest',priority:5,condition:()=>near(key)&&!blocked()&&['rack','held'].includes(state.v069Parts.crates[id])});}
    for(const[id,d]of Object.entries(DEST)){const key='dest:'+id,p=d.pos;addInteract(w,'parts69:'+key,[p[0],1.25,p[2]+2.2],'Déposer · '+d.name,()=>act('deliver',id),{radius:3.6,kind:'quest',priority:6,condition:()=>near(key)&&!blocked()&&!!M.held(state.v069Parts)});}
    addInteract(w,'parts69:sortie',[0,1.25,27.9],'Retourner au point de départ',exit,{radius:3.6,kind:'door',priority:5});
    w.subzones=[{id:'parts-yard',name:'Répartition du quai',pos:[0,0,16]},{id:'parts-lock',name:'Ponton des deux amarres',pos:[0,0,0]},{id:'parts-cargo',name:'Les six caisses',pos:[0,0,-18]}];visuals(w);return w;
  }
  const oldBuild=v042BuildInstance;v042BuildInstance=function(){return state.v042?.activeInterior===M.SITE_ID?build():oldBuild(...arguments);};
  const oldTalk=talkToNPC;talkToNPC=function(id){return typeof id==='string'&&id.startsWith('parts69:')?talk(id.slice(8)):oldTalk(...arguments);};
  const oldClaim=v042ClaimInterior;v042ClaimInterior=function(id){return id===M.SITE_ID?false:oldClaim(...arguments);};
  const oldEnter=v042EnterSite;v042EnterSite=function(id){if(id===M.SITE_ID&&!ready())return notice('Terminez l’audience du Lys avant de rejoindre le déchargement.');return oldEnter(...arguments);};
  // A carried crate stays in this quest. The visible, always reachable original rack
  // is its safe drop point; leaving cannot teleport it into a different campaign.
  const previousExit=v042ExitInstance;v042ExitInstance=function(){if(local()&&M.held(state.v069Parts))return notice('Reposez la caisse '+M.held(state.v069Parts)+' à son râtelier avant de repartir.');return previousExit(...arguments);};
  function exit(){if(blocked()||!near('sortie'))return false;const h=M.held(state.v069Parts);if(h)return notice('Reposez la caisse '+h+' à son râtelier avant de repartir.');return v042ExitInstance();}
  function sail(site){
    if(blocked()||!ready()||!portNear(site))return notice(blocked()||'Rejoignez le passeur après l’audience du Lys.');
    const owner=state,scene=world,before=copy(owner),maps={active:new Map(V042_RUNTIME.active),npcs:new Map(V042_RUNTIME.npcData),nearest:V042_RUNTIME.nearest,instance:V042_RUNTIME.instanceSite,retained:V048.retained};
    const oldSave=saveGame;let wrote=false;
    saveGame=function(...a){const result=oldSave(...a);if(result===false)throw Error('Départ non sauvegardé.');wrote=true;return result;};
    try{if(!v042EnterSite(M.SITE_ID))throw Error('Passage interrompu.');return true;}
    catch(e){restore(owner,before);world=scene;V042_RUNTIME.active=maps.active;V042_RUNTIME.npcData=maps.npcs;V042_RUNTIME.nearest=maps.nearest;V042_RUNTIME.instanceSite=maps.instance;V048.retained=maps.retained;if(typeof v049Own==='function')v049Own(world);if(wrote){try{oldSave(false);}catch{}}return notice(e.message);}
    finally{saveGame=oldSave;}
  }
  function crossing(site){if(blocked()||!portNear(site)||!ready())return false;openDialogue(speaker('Maëlle Sarti','LE LOT DU LYS · PASSAGE NARRATIF','MS'),'« On a réglé la question de la couronne. Maintenant il y a six caisses sur mon ponton, trois destinations et pas assez de marge pour tout le monde. Vous venez donner un coup de main ? »\n\nTraversée narrative par chargement vers un quai fictionnel. Retour au même départ. Aucun navire pilotable, trajet IGN ou livraison automatique.',[{text:'Rejoindre le déchargement.',onChoose:guard(()=>sail(site))},back()]);return true;}
  const relayTalk=v042TalkNPC;v042TalkNPC=function(id){const site=V042_RUNTIME.npcData.get(id)?.siteId;if(!ready()||blocked()||!portNear(site))return relayTalk(...arguments);const prev=openDialogue;openDialogue=function(s,t,ch,...rest){return prev(s,t,[...(ch||[]).slice(0,-1),{text:'Ravitaillement du Lys · La part des absents',onChoose:guard(()=>crossing(site))},...(ch||[]).slice(-1)],...rest);};try{return relayTalk(...arguments);}finally{openDialogue=prev;}};
  const oldDraws=collectDraws;collectDraws=function(t){const draws=oldDraws(...arguments);if(local()&&M.held(state.v069Parts)){const p=state.player.pos,y=state.player.yaw,f=cameraDir(y,0),right=[Math.cos(y),0,-Math.sin(y)];part(draws,'cube',[p[0]+f[0]*.85+right[0]*.35,p[1]-.85,p[2]+f[2]*.85+right[2]*.35],[.60,.50,.55],[.48,.35,.21],y);draws[draws.length-1].partsHeld=M.held(state.v069Parts); }return draws;};
  function track(){if(blocked())return false;const owner=state,before=copy(owner);owner.v042.tracked=MistralLys.PORTS[0];try{if(saveGame(false)===false)throw Error();}catch{restore(owner,before);return notice('Suivi non sauvegardé.');}updateQuestUI(true);if(mode==='PIP')renderPipboy();return true;}
  V027_SUBS.data.parts='LA PART DES ABSENTS';
  const data=v027Data;v027Data=function(c){if(V027.sub!=='parts')return data(...arguments);const l=state.v069Parts,t=M.tally(l),esc=v027Escape,source=M.basis(state);c.innerHTML='<div class="p27-long"><p class="p27-kicker">LE LYS · APRÈS L’AUDIENCE</p><h2>La part des absents</h2><p>'+esc(source?M.REACTIONS[source.policy]:'L’audience du Lys doit être terminée. Aucune cargaison n’est attribuée par défaut.')+'</p><p>'+esc(M.briefing(l))+'</p>'+v027Button('Suivre le départ du Vieux-Port','parts69:track')+'<p>Autre départ : Ratonneau. Passage narratif vers le quai, sans navigation libre.</p><h3>Répartition</h3><p>'+esc(l.plan?M.PLANS[l.plan].text:'À décider auprès de Maëlle après inspection et discussions.')+'</p>'+M.DESTS.map(id=>'<p>'+esc(DEST[id].name)+' : '+t[id]+(l.plan?' / '+M.PLANS[l.plan].quota[id]:'')+'</p>').join('')+'<h3>Chaque caisse a une place</h3>'+M.CRATES.map(id=>'<p>Caisse '+id+' : '+esc(l.crates[id]==='rack'?'au râtelier':l.crates[id]==='held'?'portée':DEST[l.crates[id]].name)+'</p>').join('')+'<p>Six caisses collectives ; aucun aliment ajouté au sac. 40 capsules après remise complète, une fois.</p></div>';};
  const dispatch=v027Dispatch;v027Dispatch=function(a,arg){return a==='parts69:track'?v027CanAct()&&track():dispatch(...arguments);};
  const rows=v027QuestRows;v027QuestRows=function(){const l=state.v069Parts;return rows(...arguments).concat(l.opened?[{id:'parts69:quest',name:TITLE,stage:l.finished?'done':'active',active:local()&&!l.finished,text:M.briefing(l),zone:null,steps:[['Sécuriser le ponton',!!l.gate],['Convenir d’une répartition',!!l.plan],['Déposer les six caisses',Object.values(M.tally(l)).reduce((a,b)=>a+b,0)===6],['Constat de Maëlle',l.finished]],source:'Cale du Lys',badge:l.finished?'✓':'',hint:'Passeur du Vieux-Port ou de Ratonneau'}]:[]);};
  const oldTrack=v027Track;v027Track=function(id){return id==='parts69:quest'?track():oldTrack(...arguments);};
  function next(){const l=state.v069Parts,h=M.held(l);if(!l.opened)return'maelle';if(!l.notice)return'notice';if(!l.gate)return !l.moored.includes('babord')?'babord':!l.moored.includes('tribord')?'tribord':'treuil';const voice=M.VOICES.find(id=>!l.heard.includes(id));if(voice)return voice;if(!l.plan)return'maelle';if(h){const t=M.tally(l);return'dest:'+M.DESTS.find(id=>t[id]<M.PLANS[l.plan].quota[id]);}const crate=M.CRATES.find(id=>l.crates[id]==='rack');return crate?'crate:'+crate:!l.finished?'maelle':'sortie';}
  const marker=getObjectiveMarker;getObjectiveMarker=function(){if(!local())return marker(...arguments);const id=next(),p=P[id];return{zone:world.id,pos:[p[0],1.25,p[2]+.9],label:PEOPLE[id]?.name||DEST[id.slice(5)]?.name||'La part des absents · '+id};};
  const ui=updateQuestUI;updateQuestUI=function(flash=false){if(!local())return ui(...arguments);$('questTitle').textContent=TITLE;$('questObjective').textContent=M.briefing(state.v069Parts);if(flash){const f=$('questFlash');f.querySelector('strong').textContent=TITLE;f.querySelector('p').textContent=M.briefing(state.v069Parts);f.classList.add('show');setTimeout(()=>f.classList.remove('show'),3200);}};
  V027_STATIONS.parts={name:'Les caisses du Lys',freq:'98.7',hint:'Le pain n’a pas de blason',available:()=>state.v069Parts.opened,text:()=>M.briefing(state.v069Parts)+(state.v069Parts.plan?' '+M.PLANS[state.v069Parts.plan].text:'')};
  const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{v069PartsInfo:()=>({ledger:copy(state.v069Parts),points:copy(P),local:local(),ready:ready(),error:rt.error}),v069PartsOpen:()=>v027Open('data','parts'),v069PartsAction:act});};
}
