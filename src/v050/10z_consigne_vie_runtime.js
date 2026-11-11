/* Post-handoff life inside the existing consigne. Native E/dialogue, collision,
 * walking rig and transactional saves. No off-screen trips or extra currency. */
if(typeof baseState==='function'&&typeof MistralConsigneLife!=='undefined'){
  const M=MistralConsigneLife,copy=x=>JSON.parse(JSON.stringify(x));
  const rt={state:null,world:null,saveBlocked:null,error:null,blocked:[],busy:false};
  const local=()=>!!world?.v073Gabians&&state.v042?.activeInterior===MistralGabians.SITE;
  const person=id=>world?.npcs.find(n=>n.id==='g73:owner:'+id);
  const base=baseState;baseState=function(...a){const s=base(...a);s.v076Consigne=M.fresh();return s;};
  const migration=migrateState;migrateState=function(raw={}){const s=migration(...arguments);s.v076Consigne=M.migrate(raw?.v076Consigne,s.v073Gabians.handoffs);return s;};
  state=migrateState(state);if(world&&typeof v049Own==='function')v049Own(world);
  function own(){if(rt.state!==state||rt.world!==world){rt.state=state;rt.world=world;rt.saveBlocked=null;rt.error=null;rt.blocked=[];rt.busy=false;}}
  function unavailable(requireGround=true){return !local()||!gameStarted||!['PLAYING','DIALOGUE'].includes(mode)||state.player.hp<=0||(requireGround&&!onGround)||zoneTransitioning||V046.busy||V047.pending||V046.lab;}
  function near(id){const n=person(id),p=state.player.pos;return !!n&&n.alive!==false&&Math.hypot(p[0]-n.pos[0],p[2]-n.pos[2])<=3.2&&Math.abs(p[1]-n.pos[1]-1.65)<1.8&&lineOfSight(p,[n.pos[0],n.pos[1]+1.25,n.pos[2]]);}
  function notice(text){V027.message=text;toast(text,'bad');return false;}
  function restore(s,b){if(state!==s)return;for(const k of Object.keys(s))delete s[k];Object.assign(s,b);}
  function visuals(w){
    if(!w?.v073Gabians)return;
    for(const d of w.staticDraws)if(d.v076Drawing)d.hidden=state.v076Consigne.people.clef.progress!==M.total('clef');
    for(const id of M.IDS){const n=w.npcs.find(n=>n.id==='g73:owner:'+id),a=state.v076Consigne.people[id];if(!n)continue;
      n.pos=M.position(id,a.progress);n.home=n.pos.slice();n.v020Static=true;n.moving=false;n.activity=M.status(id,a);
      if(a.progress>0)n.yaw=M.heading(id,a.progress);
    }
  }
  function commit(next,caption){
    own();if(rt.busy)return false;
    const s=state,w=world,before=copy(s);rt.busy=true;
    try{s.v076Consigne=next;if(saveGame(false)===false||state!==s||world!==w)throw Error('La cour n’a pas pu être sauvegardée.');}
    catch(e){restore(s,before);return notice(e.message+' Aucun changement conservé.');}
    finally{rt.busy=false;if(state===s&&world===w)visuals(w);}
    rt.saveBlocked=null;rt.error=null;if(caption)toast(caption,'good');return true;
  }
  function act(id,type,revision){
    try{return commit(M.action(state.v076Consigne,state.v073Gabians.handoffs,id,type,{local:local(),near:near(id),blocked:unavailable(),revision}),type==='wait'?'La personne vous attend.':type==='resume'?'La personne reprend son chemin.':null);}
    catch(e){return notice(e.message);}
  }
  function guarded(id,fn){const s=state,w=world,rev=s.v076Consigne.revision;return ()=>{
    if(state!==s||world!==w||unavailable()||!near(id)||state.v076Consigne.revision!==rev)return notice('Conversation périmée.');
    return fn(rev);
  };}
  const LINES={
    clef:{go:'Vous vouliez me montrer le Demain ?',intro:'« Venez à la table. J’ai retrouvé un bout de carton assez propre pour dessiner la cabine. Ne vous attendez pas à un palais : le lit touchait presque le moteur. »',
      question:'C’est ici que se trouvait votre cabine ?',answer:'« Là. Deux pas depuis le moteur, un de plus jusqu’au lit. Le Demain prenait l’eau par quatre endroits, mais cette porte fermait. On se moquait de moi parce que je gardais la clé en dormant. Ils ne s’étaient jamais réveillés avec toutes leurs affaires sous la tête. »',
      final:'« Regardez : j’ai laissé la porte ouverte sur le dessin. Sur du carton, au moins, on choisit. »'},
    bague:{go:'Vous avez enfin fini votre quart ?',intro:'« Depuis une heure. Je m’étais seulement promis de ne pas rentrer sans cette bague. Je vais souffler près du banc ; pour une fois, les cordages attendront demain. »',
      question:'Pas de cordages ce soir ?',answer:'« Non. Quand je la remets, c’est fini. Les autres savent qu’il faut une vraie urgence pour venir me chercher. La dernière “urgence”, c’était une bâche qui claquait. Je leur ai dit de lui proposer un contrat de travail. Elle aussi faisait des heures. »',
      final:'« Ça fait drôle, une minute sans rien avoir à tenir. Vous pouvez rester. Tant que vous n’apportez pas une corde. »'},
    sifflet:{go:'Qu’allez-vous annoncer au panneau ?',intro:'« Rien qui fasse courir les gens. Je vais remettre l’ardoise à l’endroit. “Dernier passage” ne veut pas dire “embarquement immédiat”. Avec les rumeurs, ici, on remplit un bateau qui n’existe même pas. »',
      question:'Pourquoi garder une ardoise sans horaire ?',answer:'« Pour écrire qu’on n’en sait rien. Hier quelqu’un avait mis “départ à l’aube”. Il n’avait ni bateau ni rame, seulement un très beau crayon. J’ai effacé l’heure. Ceux qui attendent méritent mieux qu’une belle écriture. »',
      final:'« Le sifflet est revenu. Le bateau, non. Quand ça changera, on écrira quelque chose de vrai. »'}
  };
  const back=()=>({text:'Revenir.',onChoose:closeDialogue});
  function talk(id){
    if(unavailable()||!near(id))return false;own();
    const a=state.v076Consigne.people[id],d=LINES[id],arrived=a.progress===M.total(id),choices=[];
    let text=arrived?d.final:a.paused?'« Je vous attends ici. Dites-moi quand nous pouvons reprendre. »':d.intro;
    if(rt.saveBlocked===id)choices.push({text:'Retenter la sauvegarde du trajet.',onChoose:guarded(id,()=>{if(commit(copy(state.v076Consigne)))talk(id);})});
    if(!arrived)choices.push({text:a.paused?'Vous pouvez reprendre votre chemin.':'Attendez-moi ici un instant.',onChoose:guarded(id,rev=>{if(act(id,a.paused?'resume':'wait',rev))talk(id);})});
    if(arrived)choices.push({text:d.question,onChoose:guarded(id,rev=>{
      if(!a.heard&&!act(id,'listen',rev))return;
      openDialogue(speaker(M.ROUTES[id].name,'UNE PLACE DANS LA COUR',{clef:'ÉL',bague:'MI',sifflet:'RA'}[id]),d.answer,[{text:'Revenir à notre conversation.',onChoose:guarded(id,()=>talk(id))},back()]);
    })});
    choices.push(back());
    openDialogue(speaker(M.ROUTES[id].name,'UNE PLACE DANS LA COUR',{clef:'ÉL',bague:'MI',sifflet:'RA'}[id]),text,choices);return true;
  }
  // Add one optional invitation after the saved handoff; never auto-start a walk
  // while the player is reading the original recognition dialogue.
  const dialog=openDialogue;openDialogue=function(s,text,choices,...rest){
    if(local()){
      if(s?.name==='Nora Ferrand'&&M.IDS.some(k=>state.v076Consigne.people[k].started))text=text.replace('Éloi, Mina et Rachid attendent de ce côté du comptoir.', 'Éloi, Mina et Rachid sont toujours dans la cour.');
      const id=M.IDS.find(k=>M.ROUTES[k].name===s?.name),a=id&&state.v076Consigne.people[id];
      if(id&&state.v073Gabians.handoffs[id]!==null&&!a.started&&!choices?.some(c=>c.v076Invite)){
        choices=[...(choices||[]).slice(0,-1),{text:LINES[id].go,v076Invite:true,onChoose:guarded(id,rev=>{
          if(act(id,'go',rev))talk(id);
        })},...(choices||[]).slice(-1)];
      }
    }
    return dialog(s,text,choices,...rest);
  };
  const oldTalk=talkToNPC;talkToNPC=function(id){const key=M.IDS.find(k=>id==='g73:owner:'+k);return local()&&key&&state.v076Consigne.people[key].started?talk(key):oldTalk(...arguments);};
  function buildProps(w){
    const wood=[.42,.30,.19],metal=[.23,.30,.30],paper=[.71,.66,.48];
    function box(pos,size,color,solid=true){const d=addBox(w,pos,size,color);d.v076Prop=true;if(solid){const c=addCollider(w,pos[0],pos[2],size[0],size[2],{minY:pos[1]-size[1]/2,maxY:pos[1]+size[1]/2});c.v076Prop=true;}return d;}
    box([-22,1,12],[2,.14,3],wood);for(const x of [-22.7,-21.3])for(const z of [10.9,13.1])box([x,.47,z],[.14,.94,.14],metal);
    box([-22,1.08,12],[1.6,.025,2.3],paper,false);
    // A small hand-drawn cabin, not a real nautical chart or new destination.
    for(const [x,z,sx,sz]of [[-22,11.4,1.1,.025],[-22,12.6,1.1,.025],[-22.5,12,.025,1.2],[-21.5,11.7,.025,.6],[-22.15,12.25,.45,.025]])box([x,1.096,z],[sx,.012,sz],metal,false).v076Drawing=true;
    box([-6,.52,8.3],[4,.16,1.1],wood);box([-6,1.02,7.9],[4,.9,.12],wood);for(const x of [-7.5,-4.5])box([x,.25,8.3],[.18,.5,.9],metal);
    for(const z of [16.7,19.3])box([13.2,.65,z],[.16,1.3,.16],metal);
    box([13.2,1.35,18],[.15,2.3,3.3],wood);box([13.105,1.5,18],[.025,1.5,2.6],[.15,.22,.21],false);
    // Readable note available at the board; no ferry schedule or service implied.
    addInteract(w,'v076:board',[12.4,1.5,19.7],'Lire l’ardoise des passages',()=>{
      if(!local()||unavailable()||Math.hypot(state.player.pos[0]-12.4,state.player.pos[2]-19.7)>3.2||!lineOfSight(state.player.pos,[12.4,1.5,19.7]))return false;
      openDialogue(speaker('Ardoise des passages','CONSIGNE DU VIEUX-PORT','AP'),'PAS D’HORAIRE CONFIRMÉ.\n\n« Un appel n’est pas une promesse de traversée. Demandez avant d’attendre. — Rachid »',[back()]);return true;
    },{radius:3.2,priority:2,kind:'note'});
    // Signs have physical supports. The east-facing board's lettering rotates
    // with its face instead of floating across the path.
    for(const x of [-23.2,-20.8])box([x,.82,10.3],[.09,1.64,.09],metal);
    for(const x of [-7.1,-4.9])box([x,.94,7.78],[.08,1.88,.08],metal);
    if(typeof v021Sign==='function'){
      v021Sign(w,-22,1.6,10.3,'LE DEMAIN / SOUVENIR',.037);
      v021Sign(w,-6,1.8,7.78,'FIN DE QUART',.05);
      for(const [y,text]of [[1.9,'PAS D HORAIRE'],[1.4,'CONFIRME']]){
        const begin=w.staticDraws.length;v021Sign(w,0,0,0,text,.045);
        for(const d of w.staticDraws.slice(begin)){const [x,dy,z]=d.pos;d.pos=[13.07-z,y+dy,18+x];d.rotY=(d.rotY||0)-Math.PI/2;d.v076Prop=true;}
      }
    }
  }
  const builder=v042BuildInstance;v042BuildInstance=function(){const w=builder(...arguments);if(w?.v073Gabians){buildProps(w);visuals(w);}return w;};
  function clear(id,from,to){
    if(collidesAt(to[0],to[2],.38,to[1]+1.65)||!lineOfSight([from[0],from[1]+1.1,from[2]],[to[0],to[1]+1.1,to[2]]))return false;
    const p=state.player.pos;
    if(Math.abs(p[1]-1.65-to[1])<1.9&&Math.hypot(p[0]-to[0],p[2]-to[2])<.95)return false;
    return !world.npcs.some(n=>n.id!=='g73:owner:'+id&&n.alive!==false&&Math.abs(n.pos[1]-to[1])<1.8&&Math.hypot(n.pos[0]-to[0],n.pos[2]-to[2])<.8);
  }
  function tick(dt){
    own();if(!local())return;
    for(const id of M.IDS){const n=person(id);if(n)n.moving=false;}
    rt.blocked=[];
    if(unavailable(false)||mode!=='PLAYING'||inCombat||rt.busy||rt.saveBlocked||!Number.isFinite(dt)||dt<=0)return;
    const mm=Math.max(1,Math.round(Math.min(.2,dt)*1250)),s=state,w=world;
    for(const id of M.IDS){
      const n=person(id);if(!n||n.alive===false||globalThis.v075ConsigneGestureActive?.(id))continue;
      const old=n.pos.slice();let step;
      try{step=M.advance(s.v076Consigne,s.v073Gabians.handoffs,id,mm,(from,to)=>clear(id,from,to));}
      catch(e){rt.error=e.message;rt.saveBlocked=id;notice(e.message);return;}
      if(step.blocked){rt.blocked.push(id);continue;}if(!step.moved)continue;
      const before=step.checkpoint?copy(s):null;s.v076Consigne=step.ledger;
      if(step.checkpoint){
        try{if(saveGame(false)===false||s!==state||w!==world)throw Error('Le trajet n’a pas pu être sauvegardé.');}
        catch(e){restore(s,before);rt.saveBlocked=id;rt.error=e.message;visuals(w);notice(e.message+' Parlez à '+M.ROUTES[id].name+' pour réessayer.');return;}
      }
      if(s!==state||w!==world)return;
      n.pos=M.position(id,step.ledger.people[id].progress);n.home=n.pos.slice();n.yaw=step.arrived?M.ROUTES[id].yaw:Math.atan2(old[0]-n.pos[0],old[2]-n.pos[2]);
      n.moving=!step.arrived&&!settings.reduceMotion;n.activity=M.status(id,step.ledger.people[id]);
      if(step.arrived&&id==='clef')for(const d of w.staticDraws)if(d.v076Drawing)d.hidden=false;
    }
  }
  const schedules=updateNPCSchedules;updateNPCSchedules=function(dt){return local()?tick(dt):schedules(...arguments);};
  // A doorway must not discard the newest route distance on an unsuccessful save.
  const exit=v042ExitInstance;v042ExitInstance=function(){if(local()){
    const s=state,w=world,before=copy(s);
    try{if(saveGame(false)===false||s!==state||w!==world)throw Error();}catch{restore(s,before);return notice('Sortie annulée : le trajet n’a pas pu être sauvegardé.');}
  }return exit(...arguments);};
  const data=v027Data;v027Data=function(c){const result=data(...arguments);if(V027.sub==='gabians'){
    const l=state.v076Consigne,esc=v027Escape;
    const panel=document.createElement('section');panel.className='p27-long';panel.innerHTML='<h3>Une place dans la cour · facultatif</h3>'+M.IDS.map(id=>'<p><b>'+esc(M.ROUTES[id].name)+'</b> · '+esc(M.status(id,l.people[id]))+(l.people[id].heard?' · souvenir écouté':'')+'</p>').join('')+'<p>Ces rencontres ne changent ni la prime, ni le résultat de la consigne. Aucun départ de bateau n’est confirmé.</p>';c.appendChild(panel);
  }return result;};
  const after=globalThis.v053LoreAfterInit;globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{
    v076ConsigneInfo:()=>{own();return {local:local(),ledger:copy(state.v076Consigne),saveBlocked:rt.saveBlocked,error:rt.error,blocked:rt.blocked.slice(),people:(world?.npcs||[]).filter(n=>n.id.startsWith('g73:owner:')).map(n=>({id:n.id,pos:n.pos.slice(),yaw:n.yaw,moving:!!n.moving,activity:n.activity})),props:world?.staticDraws.filter(d=>d.v076Prop).length||0};}
  });};
}
