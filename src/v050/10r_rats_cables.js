/* Rats-câbles — authored depot encounter. Original Fallout: Mistral fiction.
 * Plain versioned data, finite maintenance kit, persistent wildlife and circuit state.
 * No real electrical procedure, surveyed station geometry or renewable animal loot. */
const MistralRats=(()=>{
 'use strict';
 const copy=x=>JSON.parse(JSON.stringify(x)),own=(o,k)=>Object.prototype.hasOwnProperty.call(o||{},k);
 const integer=(x,max=999999)=>Number.isSafeInteger(x)&&x>=0&&x<=max;
 const SITE='v072-depot-rats-cables',RELAY='v042-marseille-caravan-02',MAX_HP=5800,EXIT=-22000;
 const SPECIMENS={voie:{name:'Rat-câble des voies',x:-12},armoire:{name:'Rat-câble du tableau',x:0},retour:{name:'Rat-câble de la conduite',x:12}};
 const IDS=Object.keys(SPECIMENS),CIRCUITS=['eclairage','signal'];
 const NOTES={
  morsures:{name:'L’isolant, pas l’électricité',text:'Les dents ont arraché la gaine et les débris garnissent des abris secs. Ces rats ne se nourrissent pas de courant : leur nom vient des câbles rongés et des fils pris dans leur pelage. La chaleur et les passages abrités les attirent ici.'},
  plan:{name:'Un refuge derrière le dépôt',text:'La maintenance avait prévu une sortie vers un vide technique non électrifié. Ouvrez le volet, isolez le circuit et utilisez la ration d’appât réservée. Les survivants peuvent quitter les armoires sans être poussés vers les voies actives.'}
 };
 function fresh(){return {schema:1,revision:0,opened:false,notes:[],isolated:false,isolation:null,gate:false,bait:false,kit:false,repairs:[],restored:false,actors:Object.fromEntries(IDS.map(id=>[id,{hp:MAX_HP,arms:0,legs:0,z:-8000,dir:1,burn:0,slow:0}])),finished:false,outcome:null};}
 const retreating=l=>l.isolated&&l.gate&&l.bait;
 const settled=l=>IDS.every(id=>l.actors[id].hp===0||l.actors[id].z===EXIT);
 const outcome=l=>{const n=IDS.filter(id=>l.actors[id].hp===0).length;return n===0?'refuge':n===IDS.length?'abattus':'mixte';};
 function migrate(raw){
  if(raw==null)return fresh();if(typeof raw!=='object'||Array.isArray(raw)||raw.schema!==1)throw Error('Version du carnet des rats inconnue.');
  const l=fresh();if(!integer(raw.revision))throw Error('Révision invalide.');l.revision=raw.revision;
  for(const k of ['opened','isolated','gate','bait','kit','restored','finished']){if(typeof raw[k]!=='boolean')throw Error('Carnet incomplet.');l[k]=raw[k];}
  for(const [key,allowed]of [['notes',Object.keys(NOTES)],['repairs',CIRCUITS]]){if(!Array.isArray(raw[key])||new Set(raw[key]).size!==raw[key].length||raw[key].some(k=>!allowed.includes(k)))throw Error('Liste de progression invalide.');l[key]=raw[key].slice();}
  if(![null,'manuel','technique'].includes(raw.isolation)||l.isolated!==(raw.isolation!==null))throw Error('Isolation contradictoire.');l.isolation=raw.isolation;
  if(l.bait&&(!l.isolated||!l.gate)||l.repairs.length&&(!l.kit||!l.isolated))throw Error('Travaux sans préparation.');
  for(const id of IDS){const a=raw.actors?.[id];if(!a||!integer(a.hp,MAX_HP)||!integer(a.arms,65)||!integer(a.legs,65)||!Number.isSafeInteger(a.z)||a.z<EXIT||a.z>-6000||![-1,1].includes(a.dir)||!integer(a.burn,60000)||!integer(a.slow,60000))throw Error('Rat invalide.');
   if(a.z< -10000&&!retreating(l)||a.z===EXIT&&a.hp===0)throw Error('Départ contradictoire.');l.actors[id]=copy(a);}
  if(l.restored&&(!l.isolated||l.repairs.length!==2||!settled(l)))throw Error('Réseau remis sous tension sans sécurisation.');
  if(![null,'refuge','mixte','abattus'].includes(raw.outcome)||l.finished&&(!l.opened||l.notes.length!==2||!l.restored||raw.outcome!==outcome(l))||!l.finished&&raw.outcome!==null)throw Error('Conclusion invalide.');l.outcome=raw.outcome;return l;
 }
 function position(id,a){if(!IDS.includes(id))throw Error('Rat inconnu.');return[SPECIMENS[id].x,0,a.z/1000];}
 function briefing(raw){const l=migrate(raw);if(l.finished)return {refuge:'Les trois rats ont gagné le refuge. Les gaines et les deux circuits sont remis en service, sans prétendre décontaminer le dépôt.',mixte:'Le dépôt fonctionne à nouveau. Les survivants ont gagné le refuge ; les pertes restent consignées.',abattus:'Les trois rats sont morts. Les gaines sont protégées et le réseau est remis en service : les tirs seuls ne réparaient rien.'}[l.outcome];
  if(!l.opened)return 'Djamila attend au poste de maintenance de Saint-Charles.';
  if(!l.isolated)return 'Relevez les observations et isolez le tableau. Les passages latéraux évitent les territoires des rats.';
  if(!settled(l))return retreating(l)?'L’appât est posé. Laissez les survivants gagner le vide technique ; les blessures ralentissent leur départ.':'Le courant est isolé. Ouvrez le volet du refuge et posez l’appât réservé, ou sécurisez le dépôt autrement.';
  if(!l.kit)return 'Récupérez les deux gaines réservées dans la caisse de maintenance.';
  if(l.repairs.length!==2)return `Réparez les armoires sur place : ${l.repairs.length}/2 gaines posées.`;
  if(!l.restored)return 'Vérifiez puis réarmez le tableau principal. Les luminaires doivent retrouver un état stable.';
  return l.notes.length<2?'Le réseau fonctionne ; il manque encore des observations.':'Remettez le constat à Djamila.';
 }
 function act(s,a={},ctx={}){
  const point=['open','finish'].includes(a.type)?'djamila':a.type==='note'?a.id:['isolate','restore'].includes(a.type)?'tableau':a.type==='repair'?a.id:a.type;
  if(ctx.blocked)throw Error(String(ctx.blocked));if(!ctx.local||!ctx.near||ctx.point!==point)throw Error('Rejoignez le bon équipement.');
  if(!Number.isFinite(s?.player?.hp)||s.player.hp<=0||!integer(s.player.caps))throw Error('Personnage indisponible.');
  const l=migrate(s.v072Rats);if(ctx.revision!==undefined&&ctx.revision!==l.revision)throw Error('Conversation périmée.');if(l.finished||l.revision===999999)throw Error('Carnet clos ou plein.');let cost=0,reward=0;
  if(a.type==='open'){if(l.opened)throw Error('Mission déjà ouverte.');l.opened=true;}
  else if(a.type==='note'){if(!own(NOTES,a.id)||l.notes.includes(a.id))throw Error('Observation inconnue ou déjà consignée.');l.notes.push(a.id);}
  else if(a.type==='isolate'){if(l.isolated||!['manuel','technique'].includes(a.id))throw Error('Isolation déjà faite ou méthode inconnue.');if(a.id==='technique'){if(!Number.isFinite(s.character?.special?.I)||s.character.special.I<5)throw Error('Intelligence 5 nécessaire.');if(!integer(s.inventory?.circuitry)||s.inventory.circuitry<1)throw Error('Un circuit est nécessaire.');cost=1;}l.isolated=true;l.isolation=a.id;}
  else if(a.type==='gate'){if(l.gate)throw Error('Volet déjà ouvert.');l.gate=true;}
  else if(a.type==='bait'){if(l.bait||!l.isolated||!l.gate)throw Error('Isolez le courant et ouvrez le refuge avant de poser l’appât.');l.bait=true;}
  else if(a.type==='kit'){if(l.kit)throw Error('Deux gaines déjà prélevées.');l.kit=true;}
  else if(a.type==='repair'){if(!CIRCUITS.includes(a.id)||!l.isolated||!l.kit||l.repairs.includes(a.id)||!settled(l))throw Error('Isolez, récupérez les gaines et éloignez les rats avant ce travail.');l.repairs.push(a.id);}
  else if(a.type==='restore'){if(l.restored||!l.isolated||l.repairs.length!==2||!settled(l))throw Error('Deux circuits protégés et animaux éloignés nécessaires.');l.restored=true;}
  else if(a.type==='finish'){if(!l.opened||!l.restored||l.notes.length!==2)throw Error('Restaurez le réseau et rapportez les deux observations.');l.finished=true;l.outcome=outcome(l);reward=60;}
  else throw Error('Action inconnue.');if(s.player.caps+reward>999999)throw Error('Compte plein.');const out=copy(s);if(cost)out.inventory.circuitry-=cost;out.player.caps+=reward;l.revision++;out.v072Rats=l;return out;
 }
 function live(l,id){if(!IDS.includes(id)||l.actors[id].hp===0||l.actors[id].z===EXIT||l.finished||l.revision===999999)throw Error('Rat non ciblable.');return l.actors[id];}
 function hit(raw,id,amount,part='body',pierce=0){const l=migrate(raw),a=live(l,id);if(!Number.isFinite(amount)||amount<=0||amount>100000||typeof part!=='string'||!Number.isFinite(pierce))throw Error('Impact invalide.');a.hp=Math.max(0,a.hp-Math.max(100,Math.round(amount*(1-.05*(1-Math.max(0,Math.min(.9,pierce))))*100)));if(/^(arm|claw)/.test(part))a.arms=Math.min(65,a.arms+25);if(/^(leg|fore|back)/.test(part))a.legs=Math.min(65,a.legs+25);l.revision++;return l;}
 function move(raw,id,mm){const l=migrate(raw),a=live(l,id);if(!integer(mm,400)||mm===0)throw Error('Pas de déplacement invalide.');if(retreating(l)){a.z=Math.max(EXIT,a.z-mm);a.dir=-1;}else{a.z+=a.dir*mm;if(a.z>=-6000){a.z=-6000;a.dir=-1;}if(a.z<=-10000){a.z=-10000;a.dir=1;}}const arrived=a.z===EXIT;if(arrived)l.revision++;return{ledger:l,arrived,position:position(id,a)};}
 function effect(raw,id,type,seconds){const l=migrate(raw),a=live(l,id);if(!['burning','slow'].includes(type)||!Number.isFinite(seconds)||seconds<=0||seconds>60)throw Error('Effet invalide.');const key=type==='burning'?'burn':'slow';a[key]=Math.max(a[key],Math.round(seconds*1000));l.revision++;return l;}
 function effects(raw,id,ms){const l=migrate(raw),a=live(l,id);if(!integer(ms,200)||ms===0)throw Error('Pas temporel invalide.');const burn=a.burn,slow=a.slow;a.hp=Math.max(0,a.hp-Math.round(Math.min(burn,ms)*.15));a.burn=Math.max(0,burn-ms);a.slow=Math.max(0,slow-ms);const checkpoint=a.hp===0||burn>0&&a.burn===0||slow>0&&a.slow===0;if(checkpoint)l.revision++;return{ledger:l,checkpoint};}
 function bite(origin,aim,player,sight=true){if(!sight||![origin,aim,player].every(p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite)))return false;const dx=player[0]-origin[0],dz=player[2]-origin[2],ax=aim[0]-origin[0],az=aim[2]-origin[2],d=Math.hypot(dx,dz),n=Math.hypot(ax,az);return d>0&&d<=2.4&&Math.abs(player[1]-origin[1])<2.1&&n>0&&(dx*ax+dz*az)/(d*n)>=.5;}
 return{SITE,RELAY,MAX_HP,EXIT,IDS:IDS.slice(),SPECIMENS:copy(SPECIMENS),CIRCUITS:CIRCUITS.slice(),NOTES:copy(NOTES),fresh,migrate,retreating,settled,outcome,position,briefing,act,hit,move,effect,effects,bite};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralRats;
