/* Les objets trouvés — original Fallout: Mistral fiction. Plain saved data;
 * two existing gabian models, three finite objects and two moving baskets.
 * No theft from ordinary inventory, no surveyed geometry or regional reset. */
const MistralGabians=(()=>{
 'use strict';
 const copy=x=>JSON.parse(JSON.stringify(x)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const uint=(n,max=999999)=>Number.isSafeInteger(n)&&n>=0&&n<=max;
 const SITE='v073-consigne-gabians',RELAY='v042-marseille-caravan-01',HP=4200,DROP=3500,IDS=['filets','tole'];
 const BIRDS={filets:{name:'Gabian des filets',side:-1},tole:{name:'Gabian de la tôle',side:1}};
 const OBJECTS={
  clef:{name:'Clé de cabine',nest:'filets',owner:'Éloi',text:'Éloi a changé trois fois de bateau. Il garde la clé de la première cabine où il a pu dormir porte fermée.'},
  bague:{name:'Bague de quart',nest:'filets',owner:'Mina',text:'Mina ne porte plus sa bague au travail : les cordages accrochent. Elle l’avait attachée au ticket de consigne.'},
  sifflet:{name:'Sifflet du passeur',nest:'tole',owner:'Rachid',text:'Rachid annonçait le dernier passage avec ce sifflet. Depuis, il crie. Cela porte moins loin, et il se fatigue.'}
 };
 const OIDS=Object.keys(OBJECTS),start=id=>[BIRDS[id].side*10000,4400,-7000],feed=id=>[BIRDS[id].side*22000,400,-20000];
 const patrol=id=>{const x=BIRDS[id].side;return[[x*10000,4400,-7000],[x*14000,5000,-9000],[x*14000,4400,-5000],[x*10000,4400,-7000]];};
 function fresh(){return {schema:2,revision:0,opened:false,manifest:false,lures:Object.fromEntries(IDS.map(id=>[id,false])),platforms:Object.fromEntries(IDS.map(id=>[id,{method:null,drop:0}])),objects:Object.fromEntries(OIDS.map(id=>[id,'nest'])),handoffs:Object.fromEntries(OIDS.map(id=>[id,null])),birds:Object.fromEntries(IDS.map(id=>[id,{hp:HP,wings:0,legs:0,pos:start(id),phase:'guard',waypoint:0,burn:0,slow:0,cooldown:1800,wind:null,shot:null}])),finished:false,outcome:null};}
 const vector=p=>Array.isArray(p)&&p.length===3&&p.every(Number.isSafeInteger)&&Math.abs(p[0])<=28000&&p[1]>=0&&p[1]<=6500&&p[2]>=-26000&&p[2]<=30000;
 const safeBird=a=>['fed','dead'].includes(a.phase)&&!a.burn&&!a.shot&&!a.wind;
 const settled=l=>IDS.every(id=>safeBird(l.birds[id]));
 const result=l=>{const n=IDS.filter(id=>l.birds[id].hp===0).length;return n===0?'vivants':n===2?'abattus':'mixte';};
 function migrate(raw){
  if(raw==null)return fresh();if(typeof raw!=='object'||Array.isArray(raw)||![1,2].includes(raw.schema))throw Error('Version de consigne inconnue.');
  if(!uint(raw.revision))throw Error('Révision invalide.');const l=fresh();l.revision=raw.revision;
  for(const k of ['opened','manifest','finished']){if(typeof raw[k]!=='boolean')throw Error('Carnet incomplet.');l[k]=raw[k];}
  for(const id of IDS){
   if(typeof raw.lures?.[id]!=='boolean')throw Error('Appât invalide.');l.lures[id]=raw.lures[id];
   const p=raw.platforms?.[id],a=raw.birds?.[id];
   if(!p||![null,'manuel','technique'].includes(p.method)||!uint(p.drop,DROP)||p.method===null&&p.drop!==0)throw Error('Panier incohérent.');l.platforms[id]={method:p.method,drop:p.drop};
   if(!a||!uint(a.hp,HP)||!uint(a.wings,65)||!uint(a.legs,65)||!vector(a.pos)||!['guard','lure','fed','falling','dead'].includes(a.phase)||!uint(a.waypoint,3)||!uint(a.burn,60000)||!uint(a.slow,60000)||!uint(a.cooldown,6000))throw Error('Gabian invalide.');
   if((a.hp===0)!==['falling','dead'].includes(a.phase)||a.phase==='guard'&&l.lures[id]||['lure','fed'].includes(a.phase)&&!l.lures[id]||a.phase==='lure'&&a.waypoint>1||a.phase==='fed'&&a.pos.some((n,i)=>n!==feed(id)[i])||a.phase==='dead'&&a.pos[1]!==0||a.hp===0&&(a.burn||a.slow))throw Error('État du gabian contradictoire.');
   if(a.wind!==null&&(!a.wind||!vector(a.wind.target)||!uint(a.wind.elapsed,1099)||a.phase!=='guard'))throw Error('Annonce invalide.');
   if(a.shot!==null&&(!a.shot||!vector(a.shot.origin)||!vector(a.shot.target)||!uint(a.shot.duration,2000)||a.shot.duration<100||!uint(a.shot.elapsed,a.shot.duration-1)||!uint(a.shot.power,1000)))throw Error('Projectile invalide.');
   l.birds[id]={hp:a.hp,wings:a.wings,legs:a.legs,pos:a.pos.slice(),phase:a.phase,waypoint:a.waypoint,burn:a.burn,slow:a.slow,cooldown:a.cooldown,wind:a.wind===null?null:copy(a.wind),shot:a.shot===null?null:copy(a.shot)};
   if(p.method&&!['fed','falling','dead'].includes(a.phase))throw Error('Panier déplacé sous un oiseau en garde.');
  }
  for(const id of OIDS){const v=raw.objects?.[id];if(!['nest','bag','returned'].includes(v)||v!=='nest'&&l.platforms[OBJECTS[id].nest].drop!==DROP||v==='returned'&&!l.opened)throw Error('Objet rendu sans collecte.');l.objects[id]=v;}
  // Schema 1 tracked return to Nora, never a personal handoff. Do not invent it.
  if(raw.schema===2){
   if(!raw.handoffs||typeof raw.handoffs!=='object'||Array.isArray(raw.handoffs))throw Error('Reçus personnels manquants.');
   for(const id of OIDS){const v=raw.handoffs[id];if(![null,'direct','consigne'].includes(v)||v!==null&&l.objects[id]!=='returned')throw Error('Remise personnelle contradictoire.');l.handoffs[id]=v;}
  }
  if(![null,'vivants','mixte','abattus'].includes(raw.outcome)||l.finished&&(!l.opened||!settled(l)||OIDS.some(id=>l.objects[id]!=='returned')||raw.outcome!==result(l))||!l.finished&&raw.outcome!==null)throw Error('Réception incohérente.');l.outcome=raw.outcome;return l;
 }
 function actionPoint(type,id){if(type==='deliver'&&own(OBJECTS,id))return 'owner:'+id;if(['open','return','finish'].includes(type))return 'nora';if(type==='manifest')return 'registre';if(['lure','lower'].includes(type)&&IDS.includes(id))return type+':'+id;if(type==='take'&&own(OBJECTS,id))return 'basket:'+OBJECTS[id].nest;return null;}
 function act(s,a={},ctx={}){
  const point=actionPoint(a.type,a.id);if(!point||ctx.blocked||!ctx.local||!ctx.near||ctx.point!==point)throw Error('Rejoignez la personne ou le panier concerné.');
  if(!Number.isFinite(s?.player?.hp)||s.player.hp<=0||!uint(s.player.caps))throw Error('Personnage indisponible.');
  const l=migrate(s.v073Gabians);if(l.finished&&a.type!=='deliver'||l.revision===999999||ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Carnet clos, plein ou conversation périmée.');let cost=0,reward=0;
  if(a.type==='open'){if(l.opened)throw Error('Mission déjà ouverte.');l.opened=true;}
  else if(a.type==='manifest'){if(l.manifest)throw Error('Registre déjà lu.');l.manifest=true;}
  else if(a.type==='lure'){const b=l.birds[a.id];if(l.lures[a.id]||b.hp===0)throw Error('Appât inutile.');l.lures[a.id]=true;b.phase='lure';b.waypoint=0;b.wind=null;}
  else if(a.type==='lower'){const p=l.platforms[a.id],b=l.birds[a.id];if(p.method!==null||!safeBird(b)||!['manuel','technique'].includes(a.method))throw Error('Attendez que le gabian soit à l’écart et le danger passé.');if(a.method==='technique'){if(!Number.isFinite(s.character?.special?.I)||s.character.special.I<5)throw Error('Intelligence 5 nécessaire.');if(!uint(s.inventory?.scrap)||s.inventory.scrap<1)throw Error('Une ferraille est nécessaire.');cost=1;}p.method=a.method;}
  else if(a.type==='take'){if(l.objects[a.id]!=='nest'||l.platforms[OBJECTS[a.id].nest].drop!==DROP)throw Error('Descendez entièrement le panier.');l.objects[a.id]='bag';}
  else if(a.type==='return'){if(!l.opened||!own(OBJECTS,a.id)||l.objects[a.id]!=='bag')throw Error('Vous ne portez pas cet objet pour Nora.');l.objects[a.id]='returned';}
  else if(a.type==='deliver'){if(!l.opened||!own(OBJECTS,a.id)||l.handoffs[a.id]!==null||!['bag','returned'].includes(l.objects[a.id]))throw Error('Retrouvez cet objet avant de le remettre à son propriétaire.');l.handoffs[a.id]=l.objects[a.id]==='bag'?'direct':'consigne';l.objects[a.id]='returned';}
  else if(a.type==='finish'){if(!l.opened||OIDS.some(id=>l.objects[id]!=='returned')||!settled(l))throw Error('Rapportez les trois objets et attendez la fin des dangers.');l.finished=true;l.outcome=result(l);reward=45;}
  else throw Error('Action inconnue.');if(s.player.caps+reward>999999)throw Error('Compte plein.');const out=copy(s);if(cost)out.inventory.scrap-=cost;out.player.caps+=reward;l.revision++;out.v073Gabians=l;return out;
 }
 function living(l,id){if(!IDS.includes(id)||l.finished||l.revision===999999||l.birds[id].hp===0)throw Error('Gabian non ciblable.');return l.birds[id];}
 function dead(a){a.hp=0;a.phase='falling';a.wind=null;a.burn=0;a.slow=0;}
 function hit(raw,id,amount,part='body',pierce=0){const l=migrate(raw),a=living(l,id);if(!Number.isFinite(amount)||amount<=0||amount>100000||typeof part!=='string'||!Number.isFinite(pierce))throw Error('Impact invalide.');a.hp=Math.max(0,a.hp-Math.max(100,Math.round(amount*(1-.05*(1-Math.max(0,Math.min(.9,pierce))))*100)));if(/^arm_/.test(part))a.wings=Math.min(65,a.wings+25);if(/^leg_/.test(part))a.legs=Math.min(65,a.legs+25);a.wind=null;a.cooldown=900;if(a.hp===0)dead(a);l.revision++;return l;}
 function effect(raw,id,type,seconds){const l=migrate(raw),a=living(l,id);if(!['burning','slow'].includes(type)||!Number.isFinite(seconds)||seconds<=0||seconds>60)throw Error('Effet invalide.');const key=type==='burning'?'burn':'slow';a[key]=Math.max(a[key],Math.round(seconds*1000));l.revision++;return l;}
 function stepToward(pos,target,mm){const d=Math.hypot(...target.map((n,i)=>n-pos[i]));return d<=mm?target.slice():pos.map((n,i)=>n+Math.round((target[i]-n)*mm/d));}
 function projectilePosition(s){const u=Math.min(1,s.elapsed/s.duration);return[s.origin[0]+(s.target[0]-s.origin[0])*u,s.origin[1]+(s.target[1]-s.origin[1])*u*u,s.origin[2]+(s.target[2]-s.origin[2])*u].map(n=>n/1000);}
 function advance(raw,ms,ctx={}){
  if(!uint(ms,200)||ms===0)throw Error('Pas de simulation invalide.');const l=migrate(raw),events=[];if(l.finished)return{ledger:l,events};if(l.revision===999999)throw Error('Carnet plein.');
  for(const id of IDS){const a=l.birds[id];a.cooldown=Math.max(0,a.cooldown-ms);
   if(a.shot){const before=projectilePosition(a.shot);a.shot.elapsed+=ms;if(ctx.projectileClear&&!ctx.projectileClear(before,projectilePosition(a.shot))){a.shot=null;events.push({type:'blocked-shot',id});}else if(a.shot.elapsed>=a.shot.duration){events.push({type:'impact',id,target:a.shot.target.map(n=>n/1000),damage:a.shot.power/100});a.shot=null;}}
   if(a.hp>0){const burn=a.burn,slow=a.slow;a.hp=Math.max(0,a.hp-Math.round(Math.min(ms,burn)*.15));a.burn=Math.max(0,burn-ms);a.slow=Math.max(0,slow-ms);if(a.hp===0){dead(a);events.push({type:'death',id});}else if(burn>0&&!a.burn||slow>0&&!a.slow)events.push({type:'effect-ended',id});}
   if(a.phase==='falling'){a.pos[1]=Math.max(0,a.pos[1]-ms*3);if(a.pos[1]===0){a.phase='dead';events.push({type:'landed',id});}continue;}
   if(a.phase==='dead'||a.phase==='fed')continue;
   if(a.phase==='guard'){
    if(a.wind){a.wind.elapsed+=ms;if(a.wind.elapsed>=1100){const origin=[a.pos[0],a.pos[1]+500,a.pos[2]],target=a.wind.target;a.shot={origin,target,elapsed:0,duration:Math.max(100,Math.min(2000,Math.round(Math.sqrt(2*Math.max(100,origin[1]-target[1])/9800)*1000))),power:Math.round(800*(1-a.wings/100))};a.wind=null;a.cooldown=3500;events.push({type:'released',id});}continue;}
    const t=ctx.targets?.[id];if(!a.shot&&a.cooldown===0&&vector(t)&&Math.hypot(t[0]-a.pos[0],t[2]-a.pos[2])<=10000){a.wind={target:t.slice(),elapsed:0};events.push({type:'warning',id});continue;}
   }
   const target=a.phase==='lure'?(a.waypoint===0?[BIRDS[id].side*22000,4400,-7000]:feed(id)):patrol(id)[a.waypoint];
   const speed=(a.phase==='lure'?3000:900)*(1-a.wings/100*.65)*(1-a.legs/100*.15)*(a.slow>0?.55:1),candidate=stepToward(a.pos,target,Math.max(1,Math.floor(speed*ms/1000)));
   if(ctx.canMove&&!ctx.canMove(id,a.pos,candidate))continue;a.pos=candidate;
   if(a.pos.every((n,i)=>n===target[i])){if(a.phase==='lure'&&a.waypoint===1){a.phase='fed';events.push({type:'fed',id});}else a.waypoint=a.phase==='lure'?1:(a.waypoint+1)%4;}
  }
  for(const id of IDS){const p=l.platforms[id];if(!p.method||p.drop===DROP)continue;const next=Math.min(DROP,p.drop+Math.round(ms*(p.method==='technique'?1.4:.7)));if(ctx.platformClear&&!ctx.platformClear(id,p.drop,next))continue;p.drop=next;if(next===DROP)events.push({type:'basket-down',id});}
  if(events.length)l.revision++;return{ledger:l,events};
 }
 function briefing(raw){const l=migrate(raw),bag=OIDS.filter(id=>l.objects[id]==='bag').length,n=OIDS.filter(id=>l.objects[id]==='returned').length;
  if(l.finished){const n=OIDS.filter(id=>l.handoffs[id]!==null).length;return {vivants:'Les deux gabians sont vivants, à l’écart des paniers.',mixte:'Un gabian a été tué ; le carnet ne l’efface pas.',abattus:'Les deux gabians sont morts. Nora paie la récupération, pas les oiseaux.'}[l.outcome]+' '+(n===3?'Éloi, Mina et Rachid ont retrouvé leurs affaires.':n+'/3 objet(s) remis en personne. Les autres restent à la consigne ; leurs propriétaires attendent au comptoir.');}
  if(!l.opened)return 'Nora garde une consigne près du Vieux-Port. Trois objets manquent à leurs propriétaires.';
  if(n===3)return settled(l)?'Les trois objets sont rendus. Parlez à Nora.':'Les objets sont rendus. Attendez la fin des dangers.';
  if(bag)return `${bag} objet(s) dans votre sac de mission ; ${n}/3 rendu(s). Remise possible à Nora ou aux propriétaires au comptoir.`;
  const id=IDS.find(id=>OIDS.some(o=>OBJECTS[o].nest===id&&l.objects[o]==='nest'));
  if(id&&!safeBird(l.birds[id]))return l.lures[id]?'Laissez le gabian rejoindre les restes de poisson. Un oiseau blessé vole moins vite.':'Déposez les restes à l’écart, ou affrontez les gabians. Le registre donne le nom des propriétaires.';
  if(id&&l.platforms[id].drop!==DROP)return l.platforms[id].method?'Le panier descend. Ne restez pas dessous.':'Actionnez le palan pour descendre le panier sans détruire le nid.';
  return 'Prenez chaque objet dans les paniers abaissés, puis rendez-le à Nora ou à son propriétaire au comptoir.';
 }
 return{SITE,RELAY,HP,DROP,IDS:IDS.slice(),BIRDS:copy(BIRDS),OBJECTS:copy(OBJECTS),fresh,migrate,act,hit,effect,advance,projectilePosition,briefing,actionPoint,settled,result};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralGabians;
