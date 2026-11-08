/* Le faux midi — authored encounter, not a new geographic survey.
 * Existing cicada mesh, isolated combat state, non-lethal retreat and no respawn loot.
 * HP in hundredths and retreat in millimetres keep saves plain and deterministic. */
const MistralCigales=(()=>{
 'use strict';
 const copy=x=>JSON.parse(JSON.stringify(x)),integer=(x,max=999999)=>Number.isSafeInteger(x)&&x>=0&&x<=max;
 const SITE='v071-relais-faux-midi',RELAY='v042-garlaban-caravan-01';
 const SPECIMENS={ouest:{name:'Crisseuse des restanques',x:-15},centre:{name:'Cymbalier du relais',x:0},est:{name:'Porteuse de chaux',x:15}};
 const IDS=Object.keys(SPECIMENS),NOTES={mue:{name:'Des mues, pas un nid de reine',text:'Les enveloppes abandonnées sont accrochées près des racines. Aline a noté trois émergences, pas une colonie gouvernée par une reine. Les noms Crisseuse, Cymbalier et Porteuse décrivent ces trois individus, pas trois espèces certifiées.'},signal:{name:'Une sirène qui imite midi',text:'Le programme agricole d’avant-guerre rejoue sa cadence à chaque remise sous tension. Les vibrations du relais entretiennent la réaction des adultes. Couper ce signal peut les laisser rejoindre les fissures ; cela ne décontamine ni le sol ni les insectes.'}};
 const MAX_HP=7200,LENGTH=10000;
 function fresh(){return{schema:1,revision:0,opened:false,notes:[],cut:false,method:null,actors:Object.fromEntries(IDS.map(id=>[id,{hp:MAX_HP,arms:0,legs:0,travel:0,burn:0,slow:0}])),finished:false,outcome:null};}
 function migrate(raw){
  if(raw==null)return fresh();if(typeof raw!=='object'||Array.isArray(raw)||raw.schema!==1)throw Error('Version du carnet des cigales inconnue.');
  const l=fresh();if(!integer(raw.revision))throw Error('Révision du carnet invalide.');l.revision=raw.revision;
  for(const k of ['opened','cut','finished']){if(typeof raw[k]!=='boolean')throw Error('Carnet incomplet.');l[k]=raw[k];}
  if(!Array.isArray(raw.notes)||new Set(raw.notes).size!==raw.notes.length||raw.notes.some(k=>!Object.hasOwn(NOTES,k)))throw Error('Observations invalides.');l.notes=raw.notes.slice();
  if(![null,'manuel','technique'].includes(raw.method)||l.cut!==(raw.method!==null))throw Error('Coupure contradictoire.');l.method=raw.method;
  for(const id of IDS){const a=raw.actors?.[id];if(!a||!integer(a.hp,MAX_HP)||!integer(a.arms,65)||!integer(a.legs,65)||!integer(a.travel,LENGTH)||a.travel>0&&!l.cut||a.travel===LENGTH&&a.hp===0)throw Error('État de spécimen invalide.');if(!integer(a.burn??0,60000)||!integer(a.slow??0,60000))throw Error('Effet temporaire invalide.');l.actors[id]={hp:a.hp,arms:a.arms,legs:a.legs,travel:a.travel,burn:a.burn??0,slow:a.slow??0};}
  if(![null,'retrait','mixte','abattues'].includes(raw.outcome))throw Error('Conclusion inconnue.');l.outcome=raw.outcome;
  if(l.finished&&(!l.opened||l.notes.length!==2||!settled(l)||l.outcome!==outcome(l))||!l.finished&&l.outcome!==null)throw Error('Conclusion sans observations ou résolution.');return l;
 }
 function settled(l){return l.cut&&IDS.every(id=>l.actors[id].hp===0||l.actors[id].travel===LENGTH);}
 function outcome(l){const n=IDS.filter(id=>l.actors[id].hp===0).length;return n===0?'retrait':n===3?'abattues':'mixte';}
 function position(id,a){if(!IDS.includes(id))throw Error('Spécimen inconnu.');return[SPECIMENS[id].x,0,-8-a.travel/1000];}
 function briefing(raw){const l=migrate(raw);return l.finished?({retrait:'Les trois adultes ont rejoint les fissures. Le relais reste coupé ; leurs habitats ne sont pas guéris.',mixte:'Les survivantes ont rejoint les fissures. Les pertes restent au carnet ; la coupure ne les efface pas.',abattues:'Les trois adultes ont été abattus. Le relais est coupé pour ne pas attirer une nouvelle émergence.'}[l.outcome]):!l.opened?'Aline attend au poste protégé. Le chant vient aussi du vieux relais.':!l.cut?'Observe les mues et le câblage. Les murets coupent la ligne de vue des crissements. Le sectionneur est derrière les trois perchoirs.':!settled(l)?'Signal coupé. Laissez les survivantes rejoindre leurs fissures ; les blessures peuvent ralentir leur retraite.':l.notes.length<2?'Le site est calme, mais il manque des observations au carnet.':'Revenez donner le constat à Aline.';}
 function act(snapshot,a={},ctx={}){
  const point=a.type==='open'||a.type==='finish'?'aline':a.type==='note'?a.id:'sectionneur';
  if(ctx.blocked)throw Error(String(ctx.blocked));if(!ctx.local||!ctx.near||ctx.point!==point)throw Error('Rejoignez le bon point du relais.');
  if(!Number.isFinite(snapshot?.player?.hp)||snapshot.player.hp<=0||!integer(snapshot.player.caps))throw Error('Personnage indisponible.');
  const l=migrate(snapshot.v071Cigales);if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Conversation périmée.');if(l.finished||l.revision===999999)throw Error('Carnet clos ou plein.');let cost=0,reward=0;
  if(a.type==='open'){if(l.opened)throw Error('Mission déjà ouverte.');l.opened=true;}
  else if(a.type==='note'){if(!Object.hasOwn(NOTES,a.id)||l.notes.includes(a.id))throw Error('Observation inconnue ou déjà consignée.');l.notes.push(a.id);}
  else if(a.type==='cut'){if(l.cut||!['manuel','technique'].includes(a.id))throw Error('Relais déjà coupé ou méthode inconnue.');if(a.id==='technique'){if(!Number.isFinite(snapshot.character?.special?.I)||snapshot.character.special.I<5)throw Error('Intelligence 5 nécessaire.');if(!integer(snapshot.inventory?.circuitry)||snapshot.inventory.circuitry<1)throw Error('Un circuit est nécessaire.');cost=1;}l.cut=true;l.method=a.id;}
  else if(a.type==='finish'){if(!l.opened||l.notes.length!==2||!settled(l))throw Error('Coupez le relais, résolvez la rencontre et conservez les deux observations.');l.finished=true;l.outcome=outcome(l);reward=65;}
  else throw Error('Action inconnue.');if(snapshot.player.caps+reward>999999)throw Error('Compte plein.');
  const out=copy(snapshot);if(cost)out.inventory.circuitry-=cost;out.player.caps+=reward;l.revision++;out.v071Cigales=l;return out;
 }
 function hit(raw,id,amount,part='body',pierce=0){
  const l=migrate(raw),a=l.actors[id];if(!IDS.includes(id)||!a||a.hp===0||a.travel===LENGTH||l.finished||l.revision===999999)throw Error('Spécimen non ciblable.');
  if(!Number.isFinite(amount)||amount<=0||amount>100000||!Number.isFinite(pierce)||typeof part!=='string')throw Error('Dégâts invalides.');
  const dealt=Math.max(100,Math.round(amount*(1-.08*(1-Math.max(0,Math.min(.9,pierce))))*100));a.hp=Math.max(0,a.hp-dealt);
  if(/^(arm|claw)/.test(part))a.arms=Math.min(65,a.arms+25);if(/^(leg|fore|back)/.test(part))a.legs=Math.min(65,a.legs+25);l.revision++;return l;
 }
 function retreat(raw,id,mm){const l=migrate(raw),a=l.actors[id];if(!IDS.includes(id)||!a||!l.cut||a.hp===0||a.travel===LENGTH||l.finished||!integer(mm,400)||mm===0||l.revision===999999)throw Error('Retraite invalide.');a.travel=Math.min(LENGTH,a.travel+mm);const arrived=a.travel===LENGTH;if(arrived)l.revision++;return{ledger:l,arrived,position:position(id,a)};}
 function effect(raw,id,type,seconds){const l=migrate(raw),a=l.actors[id];if(!IDS.includes(id)||!a||!['burning','slow'].includes(type)||!Number.isFinite(seconds)||seconds<=0||seconds>60||l.finished||a.hp===0||a.travel===LENGTH||l.revision===999999)throw Error('Effet indisponible.');const key=type==='burning'?'burn':'slow';a[key]=Math.max(a[key],Math.round(seconds*1000));l.revision++;return l;}
 function effects(raw,id,ms){const l=migrate(raw),a=l.actors[id];if(!IDS.includes(id)||!a||!integer(ms,200)||ms===0||a.hp===0||a.travel===LENGTH||l.finished||l.revision===999999)throw Error('Pas temporel invalide.');const burn=a.burn,slow=a.slow;a.hp=Math.max(0,a.hp-Math.round(Math.min(burn,ms)*.15));a.burn=Math.max(0,burn-ms);a.slow=Math.max(0,slow-ms);const checkpoint=a.hp===0||burn>0&&a.burn===0||slow>0&&a.slow===0;if(checkpoint)l.revision++;return{ledger:l,checkpoint};}
 function cone(origin,target,player,sight=true){if(!sight||![origin,target,player].every(p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite)))return false;const dx=player[0]-origin[0],dz=player[2]-origin[2],ax=target[0]-origin[0],az=target[2]-origin[2],d=Math.hypot(dx,dz),n=Math.hypot(ax,az);return d<=14&&Math.abs(player[1]-origin[1])<3&&d>0&&n>0&&(dx*ax+dz*az)/(d*n)>=Math.cos(Math.PI/12);}
 return{SITE,RELAY,IDS:IDS.slice(),SPECIMENS:copy(SPECIMENS),NOTES:copy(NOTES),MAX_HP,LENGTH,fresh,migrate,settled,outcome,position,briefing,act,hit,retreat,effect,effects,cone};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralCigales;
