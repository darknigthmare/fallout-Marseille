/* COCHONNET-3: deterministic, bounded exhibition boules, not federation rules.
 * Plain data owns every position/velocity. No random result or inventory stake.
 * Fixed 5 ms steps; simplified spheres, impacts, bounce and rolling friction. */
const MistralBoules=(()=>{
 'use strict';
 const copy=x=>JSON.parse(JSON.stringify(x)),teams=['player','house'];
 const SITE='v073-cour-cent-treves',RELAY='v042-marseille-caravan-01',STEP=.005;
 const radius=b=>b.id==='jack'?.085:.14,mass=b=>b.id==='jack'?.04:.7;
 const validInt=(n,max=999999)=>Number.isSafeInteger(n)&&n>=0&&n<=max;
 const body=(id,team,p)=>({id,team,p:p.slice(),v:[0,0,0],out:false});
 function fresh(){return {schema:1,revision:0,played:0,wins:0,round:null};}
 function distances(r){return r.balls.filter(b=>!b.out).map(b=>({id:b.id,team:b.team,metres:Math.hypot(b.p[0]-r.jack.p[0],b.p[2]-r.jack.p[2])})).sort((a,b)=>a.metres-b.metres||a.id.localeCompare(b.id));}
 function score(r){if(r.jack.out)return {winner:'draw',points:0,reason:'but-sorti'};const d=distances(r);if(!d.length)return {winner:'draw',points:0,reason:'aucune-boule'};const opponent=d.find(b=>b.team!==d[0].team);if(opponent&&Math.abs(opponent.metres-d[0].metres)<=.001)return {winner:'draw',points:0,reason:'egalite'};return {winner:d[0].team,points:d.filter(b=>b.team===d[0].team&&(!opponent||b.metres<opponent.metres-.001)).length,reason:'mesure'};}
 function next(r){if(r.used.player===3&&r.used.house===3)return null;if(r.used.player===3)return 'house';if(r.used.house===3)return 'player';const s=score(r);return s.winner==='draw'?(r.last==='player'?'house':'player'):s.winner==='player'?'house':'player';}
 function migrate(raw){
  if(raw==null)return fresh();if(typeof raw!=='object'||Array.isArray(raw)||raw.schema!==1)throw Error('Carnet COCHONNET inconnu.');
  for(const k of ['revision','played','wins'])if(!validInt(raw[k]))throw Error('Compteur COCHONNET invalide.');
  if(raw.wins>raw.played)throw Error('Victoires sans mènes.');
  const l={schema:1,revision:raw.revision,played:raw.played,wins:raw.wins,round:null};if(raw.round===null)return l;
  const r=raw.round;if(!r||typeof r!=='object'||!['aim','moving','result'].includes(r.phase)||!validInt(r.number)||r.number<1||r.number!==(r.phase==='result'?l.played:l.played+1))throw Error('Mène incohérente.');
  if(!teams.includes(r.last)||!validInt(r.used?.player,3)||!validInt(r.used?.house,3)||!Array.isArray(r.balls)||r.balls.length!==r.used.player+r.used.house||!validInt(r.ticks,4000)||!validInt(r.quiet,30)||!Number.isFinite(r.carry)||r.carry<0||r.carry>=STEP+1e-8||!['pointer','tirer'].includes(r.style)||!validInt(r.power,100))throw Error('État de lancer invalide.');
  const ids=new Set();for(const b of [r.jack,...r.balls]){if(!b||typeof b.out!=='boolean'||!Array.isArray(b.p)||!Array.isArray(b.v)||b.p.length!==3||b.v.length!==3||!b.p.every(n=>Number.isFinite(n)&&Math.abs(n)<=100)||!b.v.every(n=>Number.isFinite(n)&&Math.abs(n)<=40)||b.p[1]<radius(b)-.00001||ids.has(b.id))throw Error('Boule invalide.');ids.add(b.id);
   if(b===r.jack){if(b.id!=='jack'||b.team!==null)throw Error('But invalide.');}
   else if(!teams.includes(b.team)||!['1','2','3'].some(i=>b.id===b.team+i))throw Error('Identité de boule invalide.');
   if((b.out||r.phase!=='moving')&&b.v.some(n=>n!==0))throw Error('Mouvement hors phase.');
   if(!b.out&&(Math.abs(b.p[0])>2.5+radius(b)||b.p[2]<-12-radius(b)||b.p[2]>2+radius(b)))throw Error('Boule hors terrain non consignée.');
  }
  for(const t of teams)for(let i=1;i<=r.used[t];i++)if(!ids.has(t+i))throw Error('Boule manquante.');
  if(r.phase==='moving'&&(!r.balls.length||r.turn!==r.last||r.result!==null))throw Error('Lancer sans propriétaire.');
  if(r.phase==='aim'&&(r.turn!==next(r)||r.turn===null||r.result!==null||r.jack.out))throw Error('Tour incohérent.');
  if(r.phase==='result'&&(r.turn!==null||!r.jack.out&&r.balls.length!==6||JSON.stringify(r.result)!==JSON.stringify(score(r))))throw Error('Résultat sans mesure.');
  l.round=copy(r);return l;
 }
 function revision(l){if(l.revision>=999999)throw Error('Carnet plein.');l.revision++;return l;}
 function start(raw){const l=migrate(raw);if(l.round&&l.round.phase!=='result')throw Error('La mène en cours doit être terminée.');if(l.played>=999998)throw Error('Carnet plein.');const number=l.played+1;
  l.round={number,phase:'aim',turn:'player',last:'house',used:{player:0,house:0},jack:body('jack',null,[[-.28,.35,0][(number-1)%3],.085,-8-(number-1)%3*.45]),balls:[],ticks:0,quiet:0,carry:0,style:'pointer',power:34,result:null};return revision(l);}
 function configure(raw,style,power){const l=migrate(raw);if(!l.round||l.round.phase!=='aim'||l.round.turn!=='player'||!['pointer','tirer'].includes(style)||!validInt(power,100))throw Error('Réglage indisponible.');l.round.style=style;l.round.power=power;return revision(l);}
 function launch(raw,team,yaw,power,style){const l=migrate(raw),r=l.round;if(!r||r.phase!=='aim'||r.turn!==team||!teams.includes(team)||!Number.isFinite(yaw)||Math.abs(yaw)>.45||!validInt(power,100)||!['pointer','tirer'].includes(style))throw Error('Rejoignez le cercle et attendez votre tour.');
  const elevation=style==='pointer'?.64:.14,speed=style==='pointer'?4.5+power*.055:5+power*.065;
  const b=body(team+(r.used[team]+1),team,[0,.85,.5]);b.v=[Math.sin(yaw)*Math.cos(elevation)*speed,Math.sin(elevation)*speed,-Math.cos(yaw)*Math.cos(elevation)*speed];
  r.balls.push(b);r.used[team]++;r.last=team;r.phase='moving';r.ticks=0;r.quiet=0;r.carry=0;return revision(l);
 }
 function physics(r){
  const all=[r.jack,...r.balls];r.ticks++;
  for(const b of all){if(b.out)continue;const rad=radius(b);if(b.p[1]>rad+.00001||b.v[1]>0){b.v[1]-=9.81*STEP;}
   for(let i=0;i<3;i++)b.p[i]+=b.v[i]*STEP;
   if(b.p[1]<rad){b.p[1]=rad;if(b.v[1]<-.35){b.v[1]*=-.25;b.v[0]*=.72;b.v[2]*=.72;}else b.v[1]=0;}
   if(b.p[1]<=rad+.00001&&b.v[1]===0){const n=Math.hypot(b.v[0],b.v[2]),factor=n>0?Math.max(0,n-1.35*STEP)/n:0;b.v[0]*=factor;b.v[2]*=factor;}
   if(Math.abs(b.p[0])>2.5+rad||b.p[2]<-12-rad||b.p[2]>2+rad){b.out=true;b.v=[0,0,0];}
  }
  for(let i=0;i<all.length;i++)for(let j=i+1;j<all.length;j++){const a=all[i],b=all[j];if(a.out||b.out)continue;const delta=b.p.map((n,k)=>n-a.p[k]),d=Math.hypot(...delta),min=radius(a)+radius(b);if(d>=min)continue;
   const n=d>1e-9?delta.map(v=>v/d):[1,0,0],ia=1/mass(a),ib=1/mass(b),inv=ia+ib,overlap=min-d;
   for(let k=0;k<3;k++){a.p[k]-=n[k]*overlap*ia/inv;b.p[k]+=n[k]*overlap*ib/inv;}
   a.p[1]=Math.max(radius(a),a.p[1]);b.p[1]=Math.max(radius(b),b.p[1]);
   const closing=b.v.reduce((v,x,k)=>v+(x-a.v[k])*n[k],0);if(closing<0){const impulse=-(1+.42)*closing/inv;for(let k=0;k<3;k++){a.v[k]-=impulse*n[k]*ia;b.v[k]+=impulse*n[k]*ib;}}
  }
  // Contacts may push a resting sphere over a foul line in this same step.
  for(const b of all){if(!b.out&&(Math.abs(b.p[0])>2.5+radius(b)||b.p[2]<-12-radius(b)||b.p[2]>2+radius(b))){b.out=true;b.v=[0,0,0];}}
  const quiet=all.every(b=>b.out||b.p[1]<=radius(b)+.001&&Math.hypot(...b.v)<.025);r.quiet=quiet?r.quiet+1:0;
  if(r.ticks>3999)throw Error('Lancer non stabilisé : reprise nécessaire.');
  if(r.quiet>=30){for(const b of all)b.v=[0,0,0];r.carry=0;r.turn=r.jack.out?null:next(r);r.phase=r.turn===null?'result':'aim';r.result=r.phase==='result'?score(r):null;return true;}return false;
 }
 function advance(raw,dt){const l=migrate(raw),r=l.round;if(!Number.isFinite(dt)||dt<0||dt>.2)throw Error('Pas temporel invalide.');if(!r||r.phase!=='moving'||dt===0)return l;
  const total=r.carry+dt,steps=Math.floor((total+1e-10)/STEP);r.carry=Number((total-steps*STEP).toFixed(9));
  for(let i=0;i<steps;i++)if(physics(r)){if(r.phase==='result'){l.played++;if(r.result.winner==='player')l.wins++;}revision(l);break;}return l;
 }
 function settle(raw){let l=raw;for(let i=0;i<110&&l.round.phase==='moving';i++)l=advance(l,.2);if(l.round.phase==='moving')throw Error('Simulation non stabilisée.');return l;}
 // The machine uses the same launch/physics, with visible deterministic imprecision.
 // It reads the resting board, never the player's next input or hidden random rolls.
 function house(raw){const l=migrate(raw),r=l.round;if(!r||r.phase!=='aim'||r.turn!=='house')throw Error('Le lanceur attend.');
  const nearest=distances(r)[0],attack=nearest?.team==='player'&&nearest.metres<.48&&r.used.house>0;
  const target=attack?r.balls.find(b=>b.id===nearest.id).p:r.jack.p,style=attack?'tirer':'pointer';
  const error=[.28,-.38,.16][(r.number+r.used.house)%3],x=target[0]+error,z=target[2]+[.25,-.3,.15][r.used.house];
  const yaw=Math.max(-.44,Math.min(.44,Math.atan2(x,.5-z)));let low=0,high=100;
  for(let i=0;i<7;i++){const mid=Math.floor((low+high)/2),test=start(fresh());
   // Empty-lane calibration is not a match action and does not edit the caller.
   test.round.jack.p=[2,.085,-11];
   let shot=launch(test,'player',0,mid,style);shot=settle(shot);const end=shot.round.balls[0].p[2];if(end>z)low=mid+1;else high=mid;}
  return {team:'house',yaw,power:Math.min(100,low),style};
 }
 function briefing(raw){const l=migrate(raw),r=l.round;if(!r)return 'Nelly vous attend dans la cour des Cent Trêves. Trois boules chacun, aucune mise.';if(r.phase==='result')return r.result.reason==='but-sorti'?'Le but est sorti : mène annulée, aucune victoire.':r.result.winner==='draw'?'Égalité à la mesure. Personne ne prend de point.':`${r.result.winner==='player'?'Vous':'COCHONNET-3'} : ${r.result.points} point(s). Les positions font foi.`;if(r.phase==='moving')return `${r.last==='player'?'Votre boule':'La boule du lanceur'} est en mouvement. Attendez la mesure.`;return `${r.turn==='player'?'À vous de jouer depuis le cercle':'COCHONNET-3 prépare son lancer'}. Réserves : vous ${3-r.used.player}, machine ${3-r.used.house}.`;}
 return {SITE,RELAY,STEP,fresh,migrate,start,configure,launch,advance,settle,house,score,distances,briefing,radius};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralBoules;
