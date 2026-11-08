/* La part des absents — finite cargo, after the Cour du Lys.
 * Original Mistral fiction, not official Fallout canon or surveyed geometry.
 * Data is authoritative. A crate is in ONE place; ordinary inventory is never cargo.
 */
const MistralParts = (() => {
  'use strict';
  const Lys = typeof MistralLys !== 'undefined' ? MistralLys : require('./10k_cour_lys.js');
  const copy = o => JSON.parse(JSON.stringify(o));
  const own = (o,k) => Object.prototype.hasOwnProperty.call(o || {},k);
  const count = n => Number.isSafeInteger(n) && n >= 0 && n <= 999999;
  const SITE_ID = 'v069-cale-des-parts';
  const CRATES = ['A','B','C','D','E','F'];
  const DESTS = ['cuisines','accueil','equipage'];
  const VOICES = ['eloi','nora'];
  const PLANS = {
    secours: {name:'La part des naufragés',quota:{cuisines:3,accueil:2,equipage:1},text:'Trois caisses aux cuisines, deux aux nouveaux arrivants, une à l’équipage. Les naufragés reçoivent une marge ; les marins repartent sans réserve supplémentaire.'},
    rotation: {name:'La prochaine traversée',quota:{cuisines:3,accueil:1,equipage:2},text:'Trois caisses aux cuisines, une aux nouveaux arrivants, deux à l’équipage. Le secours immédiat est assuré au minimum ; la seconde caisse des marins est provisionnée, pas la promesse d’une flotte déjà en route.'},
    quartiers: {name:'Les cuisines d’abord',quota:{cuisines:4,accueil:1,equipage:1},text:'Quatre caisses aux cuisines, une aux nouveaux arrivants, une à l’équipage. Les habitants disposent d’une marge, sans priorité de titre ; les arrivants et les marins n’ont que leur minimum.'}
  };
  const REACTIONS = {
    serment:'Le serment de LOUIS a retiré les titres des rations. Éloi doit maintenant juger des actes, pas exiger une seconde abdication.',
    commune:'LOUIS est déjà guide, pas souverain. Le désaccord porte sur la part des absents, pas sur le rétablissement d’une monarchie.',
    regence:'La régence reste provisoire. Ce déchargement ne la rend ni permanente ni souveraine : ses réserves restent contestables.'
  };
  function fresh(){return {schema:1,revision:0,opened:false,basis:null,heard:[],notice:false,moored:[],gate:null,plan:null,crates:Object.fromEntries(CRATES.map(id=>[id,'rack'])),finished:false};}
  function basis(snapshot){const l=Lys.migrate(snapshot?.v068Lys);return l.finished?{policy:l.policy,route:l.route}:null;}
  function tally(l){const out={cuisines:0,accueil:0,equipage:0};for(const id of CRATES)if(DESTS.includes(l.crates[id]))out[l.crates[id]]++;return out;}
  function held(l){return CRATES.find(id=>l.crates[id]==='held')||null;}
  function migrate(raw){
    if(raw==null)return fresh();
    if(typeof raw!=='object'||Array.isArray(raw))throw Error('Registre de cargaison illisible.');
    if(raw.schema>1)throw Error('Registre de cargaison plus récent que ce programme.');
    const l=fresh();
    if(raw.schema!==1)throw Error('Version du registre de cargaison invalide.');
    if(!count(raw.revision))throw Error('Révision de cargaison invalide.');
    l.revision=raw.revision;
    for(const k of ['opened','notice','finished']){if(typeof raw[k]!=='boolean')throw Error('État de cargaison incomplet.');l[k]=raw[k];}
    for(const [key,allowed] of [['heard',VOICES],['moored',['babord','tribord']]]){
      if(!Array.isArray(raw[key])||new Set(raw[key]).size!==raw[key].length||raw[key].some(id=>!allowed.includes(id)))throw Error('Preuves de cargaison invalides.');
      l[key]=allowed.filter(id=>raw[key].includes(id));
    }
    if(raw.basis!==null){if(!raw.basis||!own(REACTIONS,raw.basis.policy)||!['etiquette','technique','service'].includes(raw.basis.route))throw Error('Origine de cargaison invalide.');l.basis={policy:raw.basis.policy,route:raw.basis.route};}
    for(const [key,allowed] of [['gate',['manuel','technique']],['plan',Object.keys(PLANS)]]){if(raw[key]!==null&&!allowed.includes(raw[key]))throw Error('Choix de cargaison invalide.');l[key]=raw[key];}
    if(!raw.crates||typeof raw.crates!=='object'||Array.isArray(raw.crates))throw Error('Inventaire de cargaison incomplet.');
    for(const id of CRATES){if(!own(raw.crates,id)||!['rack','held',...DESTS].includes(raw.crates[id]))throw Error('Position de caisse invalide.');l.crates[id]=raw.crates[id];}
    if(CRATES.filter(id=>l.crates[id]==='held').length>1)throw Error('Deux caisses ne peuvent pas être portées ensemble.');
    if(!l.opened&&(l.basis||l.heard.length||l.notice||l.moored.length||l.gate||l.plan||l.finished||CRATES.some(id=>l.crates[id]!=='rack')))throw Error('Cargaison sans ouverture documentée.');
    if(l.opened&&!l.basis)throw Error('Origine de cargaison absente.');
    if(l.moored.length&&!l.notice)throw Error('Inspection du ponton absente.');
    if(l.gate&&(!l.notice||l.moored.length!==2))throw Error('Accès sans amarres sécurisées.');
    if(l.plan&&(!l.gate||l.heard.length!==2))throw Error('Répartition sans accès ou interlocuteurs.');
    if(CRATES.some(id=>l.crates[id]!=='rack')&&!l.plan)throw Error('Caisse déplacée sans répartition.');
    const t=tally(l);
    if(l.plan&&DESTS.some(id=>t[id]>PLANS[l.plan].quota[id]))throw Error('Quota de cargaison dépassé.');
    if(l.finished&&(!l.plan||DESTS.some(id=>t[id]!==PLANS[l.plan].quota[id])))throw Error('Clôture sans six caisses déposées.');
    return l;
  }
  function point(type,id){return ['open','plan','finish'].includes(type)?'maelle':type==='hear'?id:type==='read'?'notice':type==='moor'?id:type==='gate'?'treuil':['take','return'].includes(type)?'crate:'+id:type==='deliver'?'dest:'+id:null;}
  function briefing(raw){const l=migrate(raw),t=tally(l),h=held(l);
    if(!l.opened)return 'Maëlle a ramené six caisses. Le règlement du Lys est acquis ; reste à le faire respecter sur le quai.';
    if(l.finished)return 'Six caisses remises, une seule manutention payée. Les titres n’ont pas retrouvé leur place dans les rations.';
    if(h)return 'Caisse '+h+' portée. Déposez-la à un emplacement encore libre du plan choisi, ou reposez-la à son râtelier.';
    if(!l.notice)return 'Lisez la consigne du ponton avant de toucher au treuil.';
    if(!l.gate)return 'Sécurisez les deux amarres puis abaissez la barrière du ponton. Une dérivation technique est facultative.';
    if(l.heard.length<2)return 'Écoutez Nora et Éloi : accueillir sans titre ne dit pas encore quelle part réserver aux absents.';
    if(!l.plan)return 'Convenez avec Maëlle d’une répartition des six caisses. Aucun serment politique ne conditionne le secours.';
    if(DESTS.every(id=>t[id]===PLANS[l.plan].quota[id]))return 'Les six caisses sont à destination. Faites constater le déchargement par Maëlle.';
    return DESTS.map(id=>id+' '+t[id]+'/'+PLANS[l.plan].quota[id]).join(' · ')+'. Portez une caisse à la fois depuis le ponton.';
  }
  function apply(snapshot,a={},ctx={}){
    if(ctx.blocked)throw Error(String(ctx.blocked));
    const p=point(a.type,a.id);
    if(!p||!ctx.local||!ctx.near||ctx.point!==p)throw Error('Rejoignez le bon interlocuteur, treuil ou emplacement.');
    if(!Number.isFinite(snapshot?.player?.hp)||snapshot.player.hp<=0||!count(snapshot.player.caps))throw Error('Personnage indisponible ou capsules invalides.');
    const source=basis(snapshot);if(!source)throw Error('Terminez d’abord l’audience du Lys.');
    const l=migrate(snapshot.v069Parts);
    if(l.opened&&JSON.stringify(source)!==JSON.stringify(l.basis))throw Error('Le règlement source a changé ; la cargaison ne sera pas réécrite.');
    if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Cette proposition est périmée.');
    if(l.revision===999999)throw Error('Registre de cargaison plein.');
    let cost=0,reward=0;
    if(a.type==='open'){if(l.opened)throw Error('Déchargement déjà ouvert.');l.opened=true;l.basis=source;}
    else{
      if(!l.opened)throw Error('Parlez d’abord à Maëlle.');
      if(l.finished)throw Error('Déchargement déjà soldé.');
      if(a.type==='hear'){if(!VOICES.includes(a.id)||l.heard.includes(a.id)||l.plan)throw Error('Position inconnue, déjà entendue ou plan fixé.');l.heard.push(a.id);}
      else if(a.type==='read'){if(l.notice)throw Error('Consigne déjà examinée.');l.notice=true;}
      else if(a.type==='moor'){if(!l.notice||l.gate||!['babord','tribord'].includes(a.id)||l.moored.includes(a.id))throw Error('Consigne requise ou amarre déjà sécurisée.');l.moored.push(a.id);}
      else if(a.type==='gate'){
        if(!l.notice||l.gate||!['manuel','technique'].includes(a.id))throw Error('Consigne requise ou ponton déjà ouvert.');
        if(a.id==='manuel'&&l.moored.length!==2)throw Error('Les deux amarres doivent être sécurisées.');
        if(a.id==='technique'){
          if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');
          const n=snapshot.inventory?.circuitry;if(!count(n)||n<1)throw Error('Un circuit valide est nécessaire.');cost=1;l.moored=['babord','tribord'];
        }l.gate=a.id;
      }
      else if(a.type==='plan'){if(l.plan||!l.gate||l.heard.length!==2||!own(PLANS,a.id))throw Error('Écoutez les deux positions et ouvrez le ponton ; le plan est exclusif.');l.plan=a.id;}
      else if(a.type==='take'){if(!l.plan||!CRATES.includes(a.id)||l.crates[a.id]!=='rack'||held(l))throw Error('Une seule caisse disponible peut être portée.');l.crates[a.id]='held';}
      else if(a.type==='return'){if(!CRATES.includes(a.id)||l.crates[a.id]!=='held')throw Error('Reposez la caisse à son propre râtelier.');l.crates[a.id]='rack';}
      else if(a.type==='deliver'){
        const h=held(l);if(!l.plan||!h||!DESTS.includes(a.id)||tally(l)[a.id]>=PLANS[l.plan].quota[a.id])throw Error('Caisse absente ou emplacement complet.');l.crates[h]=a.id;
      }
      else if(a.type==='finish'){const t=tally(l);if(!l.plan||held(l)||DESTS.some(id=>t[id]!==PLANS[l.plan].quota[id]))throw Error('Les six caisses doivent être déposées, pas simplement prises.');reward=40;l.finished=true;}
      else throw Error('Action de cargaison inconnue.');
    }
    if(snapshot.player.caps+reward>999999)throw Error('Compte de capsules plein.');
    const out=copy(snapshot);if(cost)out.inventory.circuitry-=cost;out.player.caps+=reward;l.revision++;
    out.v069Parts=migrate(l);return out;
  }
  return {SITE_ID,CRATES:CRATES.slice(),DESTS:DESTS.slice(),VOICES:VOICES.slice(),PLANS:copy(PLANS),REACTIONS:copy(REACTIONS),fresh,basis,tally,held,migrate,point,briefing,apply};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralParts;
