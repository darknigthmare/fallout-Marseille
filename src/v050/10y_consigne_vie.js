/* Une place dans la cour — finite, optional post-handoff routines.
 * Save only plain route distance and choices, never live NPC/renderer objects.
 * Original fan fiction: the three destinations are inside the authored consigne.
 */
const MistralConsigneLife = (() => {
  'use strict';
  const IDS = ['clef', 'bague', 'sifflet'];
  const ROUTES = {
    clef: {name:'Éloi', place:'la table des cartes', yaw:Math.PI/2,
      path:[[-11,0,18],[-17,0,18],[-17,0,12],[-20,0,12]]},
    bague: {name:'Mina', place:'le banc de fin de quart', yaw:0,
      path:[[-8,0,18],[-8,0,14],[-6,0,14],[-6,0,10]]},
    sifflet: {name:'Rachid', place:'le panneau des passages', yaw:-Math.PI/2,
      path:[[-5,0,18],[0,0,18],[5,0,18],[11,0,18]]}
  };
  const copy = x => JSON.parse(JSON.stringify(x));
  const uint = (n,max=999999) => Number.isSafeInteger(n) && n>=0 && n<=max;
  const idOK = id => {if(!IDS.includes(id))throw Error('Propriétaire inconnu.');};
  const lengths = id => ROUTES[id].path.slice(1).map((p,i)=>Math.round(Math.hypot(...p.map((v,j)=>v-ROUTES[id].path[i][j]))*1000));
  function total(id){idOK(id);return lengths(id).reduce((a,b)=>a+b,0);}
  function fresh(){return {schema:1,revision:0,people:Object.fromEntries(IDS.map(id=>[id,{started:false,progress:0,paused:false,heard:false}]))};}
  function migrate(raw,handoffs={}){
    if(raw==null)return fresh();
    if(typeof raw!=='object'||Array.isArray(raw)||raw.schema!==1||!uint(raw.revision))throw Error('Version ou révision de la cour inconnue.');
    const l=fresh();l.revision=raw.revision;
    for(const id of IDS){
      const a=raw.people?.[id];
      if(!a||['started','paused','heard'].some(k=>typeof a[k]!=='boolean')||!uint(a.progress,total(id)))throw Error('Trajet de '+ROUTES[id].name+' invalide.');
      if(a.started&&!['direct','consigne'].includes(handoffs[id])||!a.started&&(a.progress!==0||a.paused||a.heard)||a.heard&&a.progress!==total(id)||a.paused&&a.progress===total(id))throw Error('Trajet de '+ROUTES[id].name+' contradictoire.');
      l.people[id]={started:a.started,progress:a.progress,paused:a.paused,heard:a.heard};
    }
    return l;
  }
  function position(id,progress){
    idOK(id);if(!uint(progress,total(id)))throw Error('Distance invalide.');
    const path=ROUTES[id].path,ls=lengths(id);let left=progress;
    for(let i=0;i<ls.length;i++){
      if(left<=ls[i])return path[i].map((n,j)=>n+(path[i+1][j]-n)*left/ls[i]);
      left-=ls[i];
    }
    return path.at(-1).slice();
  }
  function heading(id,progress){
    const p=position(id,progress);
    if(progress===total(id))return ROUTES[id].yaw;
    const next=position(id,progress+1);
    return Math.atan2(p[0]-next[0],p[2]-next[2]);
  }
  function action(raw,handoffs,id,type,ctx={}){
    idOK(id);
    if(!ctx.local||!ctx.near||ctx.blocked)throw Error('Rejoignez cette personne dans la cour.');
    const l=migrate(raw,handoffs),a=l.people[id];
    if(ctx.revision!==l.revision||l.revision===999999)throw Error('Conversation périmée.');
    if(type==='go'){
      if(a.started||!['direct','consigne'].includes(handoffs[id]))throw Error('Rendez d’abord son objet à cette personne.');
      a.started=true;
    }else if(type==='wait'||type==='resume'){
      if(!a.started||a.progress===total(id)||a.paused===(type==='wait'))throw Error('Cette demande n’est plus nécessaire.');
      a.paused=type==='wait';
    }else if(type==='listen'){
      if(!a.started||a.progress!==total(id)||a.heard)throw Error('Cette conversation a déjà été notée ou n’est pas encore disponible.');
      a.heard=true;
    }else throw Error('Demande inconnue.');
    l.revision++;
    return l;
  }
  // A maximum 25cm step, sampled every 5cm, prevents corner-cutting and tunnelling.
  // The caller supplies the real world collision/crowding check, never a teleport.
  function advance(raw,handoffs,id,millimetres,canMove=()=>true){
    idOK(id);if(!uint(millimetres,250))throw Error('Pas de marche invalide.');
    const l=migrate(raw,handoffs),a=l.people[id],before=a.progress,end=total(id);
    if(!a.started||a.paused||a.progress===end||millimetres===0)return {ledger:l,moved:false,checkpoint:false,arrived:false,blocked:false};
    const next=Math.min(end,before+millimetres),ls=lengths(id);
    let last=position(id,before);
    for(let p=before;p<next;){
      const q=Math.min(next,p+50),target=position(id,q);
      if(!canMove(last,target,id))return {ledger:l,moved:false,checkpoint:false,arrived:false,blocked:true};
      last=target;p=q;
    }
    a.progress=next;
    const arrived=next===end;
    if(arrived){if(l.revision===999999)throw Error('Révision de la cour saturée.');l.revision++;}
    let sum=0;
    const checkpoint=arrived||Math.floor(before/2000)!==Math.floor(next/2000)||ls.some(n=>{sum+=n;return before<sum&&next>=sum;});
    return {ledger:l,moved:true,checkpoint,arrived,blocked:false};
  }
  function status(id,a){
    idOK(id);
    return !a.started?'au comptoir':a.progress===total(id)?(ROUTES[id].place.startsWith('le ')?'au '+ROUTES[id].place.slice(3):'à '+ROUTES[id].place):a.paused?'vous attend en chemin':'en route vers '+ROUTES[id].place;
  }
  for(const v of Object.values(ROUTES)){v.path.forEach(Object.freeze);Object.freeze(v.path);Object.freeze(v);}
  Object.freeze(ROUTES);
  return {IDS:IDS.slice(),ROUTES,fresh,migrate,total,position,heading,action,advance,status};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralConsigneLife;
