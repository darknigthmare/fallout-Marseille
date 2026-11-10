/* Poste Restante: La bonne adresse. Original Mistral fiction.
 * Two local homing pigeons, sealed messages and physical acknowledgements.
 * A release is not a delivery; birds return to their own loft, never an arbitrary address.
 * The courier route remains available without items or high SPECIAL attributes. */
const MistralPigeons=(()=>{
 'use strict';
 const copy=x=>JSON.parse(JSON.stringify(x)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const uint=(n,max=999999)=>Number.isSafeInteger(n)&&n>=0&&n<=max;
 const SITE='v074-cour-colombiers',RELAY='v042-marseille-caravan-02';
 const MAIL={
  soins:{name:'Deux places au sec',recipient:'Aïcha Rouanet',bird:'azur',ring:'A-17',home:'Cour du dispensaire',pos:[-17,0,-16],
   body:'Deux sœurs attendent à la halte basse. Leur toit fuit. Deux places sèches suffiraient pour la nuit ; nous ne demandons pas leurs noms à la radio.',
   reply:'Aïcha prépare deux places dans son local, pas un hôpital neuf. Elle signe : « Je veux leur nom à leur arrivée, pour ne pas les appeler les deux places toute la nuit. »'},
  pompes:{name:'La poignée de rechange',recipient:'Marin Delmas',bird:'brique',ring:'B-04',home:'Terrasse des pompes',pos:[17,3.2,-16],
   body:'La poignée de rechange est arrivée au guichet. Ne démontez plus la vôtre pour rien. Le passeur la gardera jusqu’à votre retour ; son reçu porte le repère du quartier.',
   reply:'Marin signe : « J’en avais assez de réparer avec les pièces des voisins. Je passerai la chercher. Votre oiseau ne va tout de même pas la porter. »'}
 };
 const IDS=Object.keys(MAIL),BIRDS=['azur','brique'];
 const ROUTES={
  soins:[[-7000,1380,14000],[-7000,6000,10000],[-19000,6000,-8000],[-17000,1450,-16000]],
  pompes:[[7000,1380,14000],[7000,7000,10000],[19000,7000,-8000],[17000,4650,-16000]]
 };
 const POLICIES={
  scelles:{name:'Garder les réponses sous pli',text:'Mirette conserve les deux reçus au guichet. Les destinataires restent joignables, mais aucune adresse privée n’est recopiée sur le panneau.'},
  annonce:{name:'Afficher un bilan sans noms',text:'Le panneau indique seulement que les deux plis ont été reçus. Ni noms, ni besoins individuels, ni adresse d’hébergement ne sont diffusés. Les originaux restent sous pli.'}
 };
 function fresh(){return{schema:1,revision:0,opened:false,notes:[],hatches:{soins:false,pompes:false},mail:Object.fromEntries(IDS.map(id=>[id,{phase:'source',method:null,waypoint:0,pos:ROUTES[id][0].slice()}])),policy:null,finished:false};}
 function migrate(raw){
  if(raw==null)return fresh();
  if(typeof raw!=='object'||Array.isArray(raw)||raw.schema!==1||!uint(raw.revision))throw Error('Version ou révision du registre postal invalide.');
  const l=fresh();l.revision=raw.revision;
  for(const k of ['opened','finished']){if(typeof raw[k]!=='boolean')throw Error('Registre postal incomplet.');l[k]=raw[k];}
  if(!Array.isArray(raw.notes)||raw.notes.some(id=>!IDS.includes(id))||new Set(raw.notes).size!==raw.notes.length)throw Error('Bagues inconnues.');l.notes=raw.notes.slice();
  let carried=0;
  for(const id of IDS){
   if(typeof raw.hatches?.[id]!=='boolean')throw Error('Trappe invalide.');l.hatches[id]=raw.hatches[id];
   const a=raw.mail?.[id];
   if(!a||!['source','loaded','flying','arrived','carried','received'].includes(a.phase)||![null,'oiseau','pied'].includes(a.method)||!uint(a.waypoint,3)||!Array.isArray(a.pos)||a.pos.length!==3||!a.pos.every(Number.isSafeInteger))throw Error('Pli invalide.');
   if(!a.pos.every((n,i)=>i===1?n>=1000&&n<=7500:Math.abs(n)<=22000))throw Error('Position de pigeon invalide.');
   if(a.phase==='source'&&(a.method!==null||a.waypoint!==0)||a.phase==='loaded'&&(a.method!=='oiseau'||a.waypoint!==0)||a.phase==='carried'&&a.method!=='pied'||['flying','arrived'].includes(a.phase)&&a.method!=='oiseau'||a.phase==='received'&&a.method===null)throw Error('Mode d’acheminement contradictoire.');
   if(a.phase!=='source'&&!l.opened||(a.method==='oiseau')&&!l.notes.includes(id))throw Error('Acheminement sans préparation.');
   if(['flying','arrived'].includes(a.phase)||a.phase==='received'&&a.method==='oiseau'){
    if(!l.hatches[id])throw Error('Retour vers un colombier fermé.');
    if(a.phase==='flying'&&a.waypoint<1||a.phase!=='flying'&&a.waypoint!==3)throw Error('Étape de vol invalide.');
    if(a.phase!=='flying'&&a.pos.some((n,i)=>n!==ROUTES[id][3][i]))throw Error('Arrivée non physique.');
   }else if(a.pos.some((n,i)=>n!==ROUTES[id][0][i])||a.waypoint!==0)throw Error('Pigeon déplacé sans vol.');
   if(a.phase==='carried')carried++;l.mail[id]=copy(a);
  }
  if(carried>1)throw Error('La sacoche ne porte qu’un pli à la fois.');
  if(raw.policy!==null&&!own(POLICIES,raw.policy))throw Error('Politique inconnue.');l.policy=raw.policy;
  if((l.policy!==null)!==l.finished||l.finished&&(!l.opened||!IDS.every(id=>l.mail[id].phase==='received')))throw Error('Accusés de réception manquants.');
  return l;
 }
 function point(type,id){return ['open','finish'].includes(type)?'mirette':['read','load','take','unload','release'].includes(type)&&IDS.includes(id)?'source:'+id:type==='hatch'&&IDS.includes(id)?'loft:'+id:type==='receive'&&IDS.includes(id)?id:null;}
 function act(s,a={},ctx={}){
  const p=point(a.type,a.id);
  if(!p||ctx.blocked||!ctx.local||!ctx.near||ctx.point!==p)throw Error('Rejoignez le guichet ou le destinataire concerné.');
  if(!Number.isFinite(s?.player?.hp)||s.player.hp<=0||!uint(s.player.caps))throw Error('Personnage indisponible.');
  const l=migrate(s.v074Pigeons);if(l.finished||l.revision===999999||ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Registre clos, plein ou conversation périmée.');
  let reward=0;
  if(a.type==='open'){if(l.opened)throw Error('Tournée déjà acceptée.');l.opened=true;}
  else if(a.type==='read'){if(l.notes.includes(a.id))throw Error('Bague déjà relevée.');l.notes.push(a.id);}
  else if(a.type==='hatch'){if(l.hatches[a.id])throw Error('Trappe déjà ouverte.');l.hatches[a.id]=true;}
  else if(a.type==='finish'){
   if(!l.opened||!IDS.every(id=>l.mail[id].phase==='received')||!own(POLICIES,a.id))throw Error('Deux reçus sont nécessaires avant la clôture.');
   l.finished=true;l.policy=a.id;reward=50;
  }else{
   if(!l.opened)throw Error('Acceptez la tournée auprès de Mirette.');const m=l.mail[a.id];
   if(a.type==='load'){
    if(m.phase!=='source'||!l.notes.includes(a.id)||a.bird!==MAIL[a.id].bird)throw Error('Ce pigeon ne rentre pas au colombier du destinataire. Vérifiez sa bague.');m.phase='loaded';m.method='oiseau';
   }else if(a.type==='unload'){
    if(m.phase!=='loaded')throw Error('Seul un pli encore au départ peut être retiré du tube.');m.phase='source';m.method=null;
   }else if(a.type==='take'){
    if(m.phase!=='source'||IDS.some(id=>l.mail[id].phase==='carried'))throw Error('La sacoche est occupée ou ce pli a déjà quitté le guichet.');m.phase='carried';m.method='pied';
   }else if(a.type==='release'){
    if(m.phase!=='loaded'||!l.hatches[a.id])throw Error('Chargez le bon pigeon et ouvrez son colombier avant le départ.');m.phase='flying';m.waypoint=1;
   }else if(a.type==='receive'){
    if(!['arrived','carried'].includes(m.phase))throw Error('Le pli n’est pas arrivé. Un départ n’est pas un accusé de réception.');m.phase='received';
   }else throw Error('Action inconnue.');
  }
  if(s.player.caps+reward>999999)throw Error('Compte de capsules plein.');
  l.revision++;const out=copy(s);out.v074Pigeons=l;out.player.caps+=reward;return out;
 }
 function advance(raw,ms,ctx={}){
  if(!uint(ms,200)||ms===0)throw Error('Pas temporel invalide.');const l=migrate(raw),events=[];
  if(l.finished)return{ledger:l,events};if(l.revision===999999)throw Error('Registre plein.');
  for(const id of IDS){const a=l.mail[id];if(a.phase!=='flying')continue;const target=ROUTES[id][a.waypoint],delta=target.map((n,i)=>n-a.pos[i]),d=Math.hypot(...delta),step=Math.floor(ms*2.6);
   const pos=d<=step?target.slice():a.pos.map((n,i)=>n+Math.round(delta[i]*step/d));
   if(ctx.canMove&&!ctx.canMove(id,a.pos,pos))continue;a.pos=pos;
   if(pos.every((n,i)=>n===target[i])){if(a.waypoint===3){a.phase='arrived';events.push({type:'arrived',id});}else{a.waypoint++;events.push({type:'corner',id});}}
  }
  if(events.length)l.revision++;return{ledger:l,events};
 }
 function briefing(raw){const l=migrate(raw);if(l.finished)return POLICIES[l.policy].text;
  if(!l.opened)return 'Mirette cherche un porteur pour deux plis. Les oiseaux et la passerelle sont disponibles, sans paiement.';
  const n=IDS.filter(id=>l.mail[id].phase==='received').length;if(n===2)return 'Les deux destinataires ont signé. Retournez auprès de Mirette.';
  return n+'/2 reçus. '+IDS.filter(id=>l.mail[id].phase!=='received').map(id=>MAIL[id].name+' : '+({source:'au guichet',loaded:'chargé, pas envoyé',flying:'en vol vers son colombier',arrived:'arrivé, à faire signer',carried:'dans votre sacoche'}[l.mail[id].phase])).join(' ; ')+'.';
 }
 return{SITE,RELAY,MAIL:copy(MAIL),IDS:IDS.slice(),BIRDS:BIRDS.slice(),ROUTES:copy(ROUTES),POLICIES:copy(POLICIES),fresh,migrate,point,act,advance,briefing};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralPigeons;
