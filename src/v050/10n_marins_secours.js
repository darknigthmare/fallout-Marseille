/* Marins-Sapeurs — original Mistral fiction. A bounded, non-timed rescue.
 * The two evacuees are actors, never loot. Routes are authored metre-space paths.
 * Plain data is authoritative; no world object or observer is saved. */
const MistralSecours = (() => {
  'use strict';
  const copy = x => JSON.parse(JSON.stringify(x));
  const own = (o,k) => Object.prototype.hasOwnProperty.call(o || {},k);
  const integer = n => Number.isSafeInteger(n) && n >= 0 && n <= 999999;
  const SITE_ID = 'v070-annexe-secours';
  const PEOPLE = {
    lila: {name:'Lila Mensah',role:'Réparatrice des pompes',path:[[-14,0,-20],[-14,0,-7],[-14,0,9],[-8,0,9],[-8,0,21],[-4,0,21]],
      text:'« J’ai fermé le compartiment quand l’alarme a commencé. Rémi est de l’autre côté. Ne le laissez pas au registre des matières dangereuses : c’est lui qui a réparé notre soupape. »'},
    remi: {name:'Rémi Laugier',role:'Goule consciente · mécanicien',path:[[14,0,-20],[14,0,-7],[14,0,9],[8,0,9],[8,0,21],[4,0,21]],
      text:'« Le lecteur dit que je ne présente pas de signes vitaux conformes. Il n’a jamais apprécié mon teint. Mes jambes vont bien ; je suivrai quelqu’un qui regarde où il met les pieds. »'}
  };
  const IDS = Object.keys(PEOPLE);
  const cumulative = id => {
    const p=PEOPLE[id]?.path;if(!p)throw Error('Personne inconnue.');
    const a=[0];for(let i=1;i<p.length;i++)a.push(a[i-1]+Math.round(Math.hypot(p[i][0]-p[i-1][0],p[i][2]-p[i-1][2])*1000));return a;
  };
  function length(id){const a=cumulative(id);return a[a.length-1];}
  function position(id,progress=0){
    const p=PEOPLE[id]?.path,a=cumulative(id);if(!Number.isSafeInteger(progress)||progress<0||progress>length(id))throw Error('Position de secours invalide.');
    for(let i=1;i<a.length;i++)if(progress<=a[i]){const t=(progress-a[i-1])/(a[i]-a[i-1]);return p[i-1].map((v,j)=>v+(p[i][j]-v)*t);}return p[p.length-1].slice();
  }
  function fresh(){return {schema:1,revision:0,opened:false,briefed:false,power:false,fuel:false,extinguished:null,doors:{lila:false,remi:false},people:Object.fromEntries(IDS.map(id=>[id,{mode:'waiting',progress:0}])),order:[],finished:false};}
  function migrate(raw){
    if(raw==null)return fresh();
    if(typeof raw!=='object'||Array.isArray(raw))throw Error('Registre de secours illisible.');
    if(raw.schema>1)throw Error('Registre de secours plus récent que ce programme.');
    if(raw.schema!==1||!integer(raw.revision))throw Error('Version ou révision de secours invalide.');
    const l=fresh();l.revision=raw.revision;
    for(const k of ['opened','briefed','power','fuel','finished']){if(typeof raw[k]!=='boolean')throw Error('État de secours incomplet.');l[k]=raw[k];}
    if(raw.extinguished!==null&&!['manuel','technique'].includes(raw.extinguished))throw Error('Extinction inconnue.');l.extinguished=raw.extinguished;
    for(const id of IDS){const p=raw.people?.[id];if(typeof raw.doors?.[id]!=='boolean'||!p||!['waiting','following','safe'].includes(p.mode)||!Number.isSafeInteger(p.progress)||p.progress<0||p.progress>length(id))throw Error('Évacuation invalide.');
      l.doors[id]=raw.doors[id];l.people[id]={mode:p.mode,progress:p.progress};
      if((p.progress>0||p.mode!=='waiting')&&!l.doors[id])throw Error('Personne déplacée à travers une porte fermée.');
      if((p.mode==='safe')!==(p.progress===length(id)))throw Error('Arrivée de secours non attestée.');
    }
    if(IDS.filter(id=>l.people[id].mode==='following').length>1)throw Error('Un seul accompagnement à la fois.');
    if(!Array.isArray(raw.order)||new Set(raw.order).size!==raw.order.length||raw.order.some(id=>!IDS.includes(id)))throw Error('Ordre de secours invalide.');l.order=raw.order.slice();
    if(IDS.some(id=>(l.people[id].mode==='safe')!==l.order.includes(id)))throw Error('Réception de personne incohérente.');
    if(!l.opened&&(l.briefed||l.power||l.fuel||l.extinguished||IDS.some(id=>l.doors[id])||l.finished))throw Error('Intervention sans ouverture.');
    if((l.power||l.fuel||l.extinguished)&&!l.briefed)throw Error('Consigne de secours absente.');
    if(l.extinguished&&(!l.power||!l.fuel))throw Error('Énergie non isolée.');
    if(IDS.some(id=>l.doors[id])&&!l.extinguished)throw Error('Couloir non sécurisé.');
    if(l.finished&&l.order.length!==2)throw Error('Clôture sans les deux personnes.');
    return l;
  }
  const point=(type,id)=>['open','finish'].includes(type)?'farah':type==='brief'?'console':type==='isolate'?id:type==='extinguish'?'lance':type==='door'?'door:'+id:['follow','wait'].includes(type)?id:null;
  function briefing(raw){const l=migrate(raw);
    if(!l.opened)return 'Rencontrez Farah. Lila et Rémi attendent dans les compartiments protégés, alimentés par leur propre arrivée d’air.';
    if(l.finished)return 'Lila et Rémi sont au point de rassemblement. Le départ et leurs noms ne dépendent pas d’un dossier conforme.';
    if(!l.briefed)return 'Consultez le panneau de sécurité de l’annexe.';
    if(!l.extinguished)return 'Isolez le courant et l’alimentation, puis utilisez le dispositif d’extinction du poste. Le matériel de secours est déjà sur place.';
    const moving=IDS.find(id=>l.people[id].mode==='following');if(moving)return PEOPLE[moving].name+' vous accompagne. Restez proche et visible ; parlez-lui pour faire une pause.';
    if(l.order.length===2)return 'Les deux personnes sont arrivées par le couloir. Faites le compte-rendu à Farah.';
    return 'Ouvrez les portes et accompagnez Lila puis Rémi, ou l’inverse. Une personne vous suit à la fois ; l’autre attend dans son compartiment protégé.';
  }
  function apply(snapshot,a={},ctx={}){
    if(ctx.blocked)throw Error(String(ctx.blocked));const p=point(a.type,a.id);
    if(!p||!ctx.local||!ctx.near||ctx.point!==p)throw Error('Rejoignez le bon interlocuteur ou équipement.');
    if(!Number.isFinite(snapshot?.player?.hp)||snapshot.player.hp<=0||!integer(snapshot.player.caps))throw Error('Personnage indisponible.');
    const l=migrate(snapshot.v070Secours);if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Cette conversation est périmée.');
    if(l.revision===999999)throw Error('Registre de secours plein.');if(l.finished)throw Error('Intervention déjà clôturée.');let cost=0,reward=0;
    if(a.type==='open'){if(l.opened)throw Error('Intervention déjà ouverte.');l.opened=true;}
    else{
      if(!l.opened)throw Error('Parlez d’abord à Farah.');
      if(a.type==='brief'){if(l.briefed)throw Error('Consigne déjà lue.');l.briefed=true;}
      else if(a.type==='isolate'){if(!l.briefed||!['power','fuel'].includes(a.id)||l[a.id])throw Error('Consigne requise ou circuit déjà isolé.');l[a.id]=true;}
      else if(a.type==='extinguish'){
        if(!l.briefed||l.extinguished||!['manuel','technique'].includes(a.id))throw Error('Consigne requise ou extinction déjà effectuée.');
        if(a.id==='manuel'&&(!l.power||!l.fuel))throw Error('Isolez les deux alimentations avant la décharge.');
        if(a.id==='technique'){const n=snapshot.inventory?.circuitry;if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');if(!integer(n)||n<1)throw Error('Un circuit valide est nécessaire.');cost=1;l.power=true;l.fuel=true;}
        l.extinguished=a.id;
      }else if(a.type==='door'){if(!IDS.includes(a.id)||!l.extinguished||l.doors[a.id])throw Error('Sécurisez le couloir ; cette porte ne s’ouvre qu’une fois.');l.doors[a.id]=true;}
      else if(a.type==='follow'){if(!IDS.includes(a.id)||!l.doors[a.id]||l.people[a.id].mode==='safe'||IDS.some(id=>l.people[id].mode==='following'))throw Error('Ouvrez la porte et accompagnez une seule personne à la fois.');l.people[a.id].mode='following';}
      else if(a.type==='wait'){if(!IDS.includes(a.id)||l.people[a.id].mode!=='following')throw Error('Cette personne ne vous suit pas.');l.people[a.id].mode='waiting';}
      else if(a.type==='finish'){if(l.order.length!==2)throw Error('Les deux personnes doivent être présentes au rassemblement, pas simplement libérées.');reward=60;l.finished=true;}
      else throw Error('Action de secours inconnue.');
    }
    if(snapshot.player.caps+reward>999999)throw Error('Compte de capsules plein.');
    const out=copy(snapshot);if(cost)out.inventory.circuitry-=cost;out.player.caps+=reward;l.revision++;out.v070Secours=l;return out;
  }
  // Only the native adapter supplies distance, after time, distance, sight and collision checks.
  // Stop at each authored corner so checkpoints cannot be skipped by a large frame delta.
  function advance(raw,id,millimetres){
    const l=migrate(raw);if(!IDS.includes(id)||!Number.isSafeInteger(millimetres)||millimetres<1||millimetres>300)throw Error('Pas d’accompagnement invalide.');
    if(l.people[id].mode!=='following'||l.finished||l.revision===999999)throw Error('Accompagnement non actif.');
    const p=l.people[id],end=cumulative(id).find(v=>v>p.progress);p.progress=Math.min(end,p.progress+millimetres);
    const checkpoint=p.progress===end;if(checkpoint)l.revision++;
    if(p.progress===length(id)){p.mode='safe';l.order.push(id);}
    return {ledger:l,position:position(id,p.progress),checkpoint,arrived:p.mode==='safe'};
  }
  function pause(raw){const l=migrate(raw);const id=IDS.find(k=>l.people[k].mode==='following');if(!id)return l;if(l.revision===999999)throw Error('Registre plein.');l.people[id].mode='waiting';l.revision++;return l;}
  return {SITE_ID,PEOPLE:copy(PEOPLE),IDS:IDS.slice(),fresh,migrate,point,position,length,briefing,apply,advance,pause};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralSecours;
