/* v0.30 — powered armour is a simulation, not a free equipment grant.
   Existing complete suits keep their identity and their old aggregate wear. */
const V030={selected:'torso',quote:null,hitPart:null,handling:false,manual:false,checkpoint:0,epoch:0};
const V030_SLOTS={head:{name:'Casque',weight:.14},torso:{name:'Plastron',weight:.30},leftArm:{name:'Bras gauche',weight:.13},rightArm:{name:'Bras droit',weight:.13},leftLeg:{name:'Jambe gauche',weight:.15},rightLeg:{name:'Jambe droite',weight:.15}};
const V030_MODS={servos:{name:'Servos de portage',desc:'Capacité assistée +25 ; dépense de mouvement +25 %. Aucun effet hors tension.',cost:{scrap:6,circuitry:3,weaponParts:3}},seal:{name:'Joints de confinement',desc:'Résistance aux radiations +12 points, pondérée par l’intégrité du casque et du plastron. Fonctionne même hors tension.',cost:{cloth:5,chemicals:4,scrap:3}},ceramic:{name:'Écrans réfractaires',desc:'Résistance au feu +20 points ; masse +4. L’effet dépend de l’intégrité des plaques.',cost:{clay:6,scrap:4,steelPlate:2}}};
ARMORS.mistralRig={name:'Châssis assisté M-45 des amarres',dr:.53,rad:.28,fire:.24,powered:true,desc:'Châssis de manutention reconstruit à La Ciotat. Sa coque et ses raccords sont des créations de Mistral, pas un modèle militaire importé.'};ITEM_VALUES.mistralRig=1350;
function v030Powered(id=state.player.armorId){return !!(ARMORS[id]&&(ARMORS[id].powered||/armure assistée/i.test(ARMORS[id].name)||['t45Armor','t51Armor','t60Armor','x01Armor'].includes(id)));}
function v030Fresh(){return {schema:1,active:false,core:null,spares:[],rigs:{},vendorRigs:{},hitIndex:0,travelDistance:0,spent:0,quest:{accepted:false,servo:false,plan:false,isolated:false,restored:false,coreTaken:false,trial:null,ending:null,rewarded:false,tracked:false},history:[]};}
function v030Parts(condition=100){return Object.fromEntries(Object.keys(V030_SLOTS).map(k=>[k,condition]));}
const v030Base=baseState;baseState=function(){const s=v030Base();s.v030=v030Fresh();return s;};
const v030Migrate=migrateState;migrateState=function(raw={}){const s=v030Migrate(raw),p=raw.v030&&typeof raw.v030==='object'?raw.v030:{},f=v030Fresh();
 f.core=typeof p.core==='number'&&Number.isFinite(p.core)&&p.core>0?Math.min(100,p.core):null;
 f.spares=(Array.isArray(p.spares)?p.spares:[]).filter(n=>typeof n==='number'&&Number.isFinite(n)&&n>0).slice(0,40).map(n=>Math.min(100,n));
 for(const id of s.equipment.ownedArmors||[])if(v030Powered(id)){const a=p.rigs?.[id]||{},cond=v028Number(s.equipment.armorCondition[id],100);f.rigs[id]={parts:v030Parts(cond),mod:Object.hasOwn(V030_MODS,a.mod)?a.mod:null};for(const k of Object.keys(V030_SLOTS))f.rigs[id].parts[k]=v028Number(a.parts?.[k],cond);}
 f.active=p.active===true&&v030Powered(s.player.armorId)&&f.core>0&&(f.rigs[s.player.armorId]?.parts.torso??0)>0;
 f.hitIndex=Math.floor(v028Number(p.hitIndex,0,0,1e9));f.travelDistance=v028Number(p.travelDistance,0,0,1e9);f.spent=v028Number(p.spent,0,0,1e9);
 const q=p.quest||{};for(const k of ['accepted','servo','plan','isolated','restored','coreTaken','rewarded','tracked'])f.quest[k]=q[k]===true;f.quest.trial=['powered','manual'].includes(q.trial)?q.trial:null;f.quest.ending=['rescue','independent'].includes(q.ending)?q.ending:null;
 f.history=(Array.isArray(p.history)?p.history:[]).filter(x=>typeof x==='string').slice(-40).map(x=>x.slice(0,240));s.v030=f;return s;};state=migrateState(state);
function v030Rig(id=state.player.armorId){if(!v030Powered(id)||!state.equipment.ownedArmors.includes(id))return null;return state.v030.rigs[id]||(state.v030.rigs[id]={parts:v030Parts(state.equipment.armorCondition[id]??100),mod:null});}
function v030Average(id=state.player.armorId){const r=v030Rig(id);return r?Object.entries(V030_SLOTS).reduce((s,[k,d])=>s+d.weight*r.parts[k],0):100;}
function v030Online(){const r=v030Rig();return !!(state.v030?.active&&r&&r.parts.torso>0&&state.v030.core>0);}
function v030Log(text){state.v030.history.push(String(text).slice(0,240));state.v030.history=state.v030.history.slice(-40);}
function v030Save(){saveGame(false);updateHUD();if(mode==='PIP')renderPipboy();}
function v030CanAct(){return gameStarted&&world&&['PLAYING','PIP'].includes(mode)&&state.player.hp>0&&!zoneTransitioning;}
function v030RefreshCondition(id){if(state.v030.rigs[id])state.equipment.armorCondition[id]=v030Average(id);}
