/* v0.26 — finite loot and transactions; original quests and real-map status are preserved. */
const V026={open:false,tab:'bag',context:null,selected:null,query:'',category:'all',sort:'name',page:0,epoch:0,lockAngle:0,lockHint:'Réglez l’épingle, puis essayez le barillet.',allowOwned:false,trade:null,message:'',hudAt:0};
const V026_JUNK={
 enamelCup:{name:'Quart émaillé',mass:.22,value:6,desc:'Le bord porte une réparation au fil de cuivre.',yield:{scrap:1}},
 radioTube:{name:'Tube radio fêlé',mass:.12,value:12,desc:'Un filament intact dans un verre étoilé.',yield:{circuitry:1,scrap:1}},
 burntMotor:{name:'Moteur bobiné brûlé',mass:2.4,value:28,desc:'Ses bobinages restent récupérables malgré le carter noirci.',yield:{scrap:4,circuitry:1}},
 ceramicShard:{name:'Tesson de filtre signé',mass:.3,value:8,desc:'Un numéro de cuisson gravé permet de suivre la série.',yield:{clay:2}},
 seaRope:{name:'Cordage dessalé',mass:1.1,value:10,desc:'Le cordage est usé, mais ses fibres tiennent encore.',yield:{cloth:3}},
 instrumentTray:{name:'Plateau inox rayé',mass:.65,value:14,desc:'Un coin a été redressé ; la liste des outils est gravée au revers.',yield:{scrap:2}},
 crackedGauge:{name:'Manomètre fendu',mass:.48,value:18,desc:'L’aiguille a arrêté sa course au-delà du dernier trait.',yield:{scrap:1,circuitry:1}},
 woolBlanket:{name:'Couverture élimée',mass:1.25,value:10,desc:'Elle a déjà été reprise avec trois tissus différents.',yield:{cloth:4}},
 brassValve:{name:'Vanne en laiton grippée',mass:1.6,value:24,desc:'Le volant ne tourne plus ; son corps peut être réusiné.',yield:{scrap:3,weaponParts:1}},
 emptyInjector:{name:'Injecteur vide',mass:.09,value:4,desc:'Aucune dose restante. Le matériau rejoint l’atelier, pas le dispensaire.',yield:{scrap:1}},
 lensHousing:{name:'Optique hors service',mass:.62,value:23,desc:'Les lentilles sont ternes ; le connecteur peut servir.',yield:{circuitry:2}},
 rationTin:{name:'Boîte de ration vide',mass:.08,value:3,desc:'Le couvercle a servi de pense-bête à un manutentionnaire.',yield:{scrap:1}}
};
for(const [id,d] of Object.entries(V026_JUNK))ITEM_VALUES[id]=d.value;
const v026LabelOld=itemLabel;itemLabel=function(id){return V026_JUNK[id]?.name||({bobbyPin:'Épingle de crochetage'})[id]||v026LabelOld(id);};
function v026Fresh(){return{schema:1,containers:{},vendorGear:{},marked:{},carry:false,transactions:[],quest:{accepted:false,inspected:{},informed:false,ending:null,rewarded:false,tracked:false}};}
const v026Base=baseState;baseState=function(){const s=v026Base();s.v026=v026Fresh();return s;};
function v026SafeKey(k){return typeof k==='string'&&/^[a-zA-Z0-9_:.| -]{1,190}$/.test(k)&&!['__proto__','prototype','constructor'].includes(k);}
function v026Count(n,max=1000000){return Number.isInteger(n)&&n>=0?Math.min(max,n):0;}
function v026Known(id){return id==='caps'||Object.hasOwn(ITEM_VALUES,id)||Object.hasOwn(AMMO_INFO,id)||Object.hasOwn(WEAPONS,id)||Object.hasOwn(ARMORS,id);}
function v026CleanItems(items){const out={};for(const [id,n] of Object.entries(items||{}).slice(0,400))if(v026SafeKey(id)&&v026Known(id)&&v026Count(n)>0)out[id]=v026Count(n);return out;}
function v026GearInfo(s,id){return {condition:equipmentCondition(WEAPONS[id]?'weapon':'armor',id),mod:!!s.equipment.weaponMods[id]};}
const v026Migrate=migrateState;migrateState=function(input={}){const s=v026Migrate(input),f=v026Fresh(),p=input.v026||{};s.v026=f;f.carry=p.carry===true;
 for(const [key,a]of Object.entries(p.containers||{}).slice(0,3000)){if(!v026SafeKey(key)||!a||!Array.isArray(a.pos)||a.pos.length!==3||!a.pos.every(n=>Number.isFinite(n)&&Math.abs(n)<1e7)||!v026SafeKey(a.zone))continue;
 const gear={};for(const [id,g]of Object.entries(a.gear||{}).slice(0,80))if((WEAPONS[id]||ARMORS[id])&&g)gear[id]={condition:clamp(Number(g.condition)||0,0,100),mod:!!g.mod};
 f.containers[key]={zone:a.zone,id:String(a.id||key).slice(0,180),kind:['chest','loose','remains'].includes(a.kind)?a.kind:'chest',title:String(a.title||'Conteneur').slice(0,160),pos:[...a.pos],items:v026CleanItems(a.items),initial:v026CleanItems(a.initial),gear,owned:!!a.owned,permission:!!a.permission,reported:!!a.reported,unlocked:!!a.unlocked,visited:!!a.visited,pinWear:v026Count(a.pinWear,2),lock:v026Count(a.lock,4),actor:a.actor?{type:String(a.actor.type||'').slice(0,90),yaw:Number(a.actor.yaw)||0,boss:!!a.actor.boss}:null};
 }
 for(const [vendor,items]of Object.entries(p.vendorGear||{}).slice(0,50)){if(!Object.hasOwn(MERCHANTS,vendor)||!items)continue;f.vendorGear[vendor]={};for(const[id,g]of Object.entries(items).slice(0,400))if((WEAPONS[id]||ARMORS[id])&&g)f.vendorGear[vendor][id]={condition:clamp(Number(g.condition)||0,0,100),mod:!!g.mod,queue:(Array.isArray(g.queue)?g.queue:[]).slice(0,120).filter(x=>x&&Number.isFinite(x.condition)).map(x=>({condition:clamp(x.condition,0,100),mod:!!x.mod}))};}
 for(const[k,v]of Object.entries(p.marked||{}).slice(0,400))if(v026SafeKey(k)&&v)f.marked[k]=true;
 const q=p.quest||{};f.quest={accepted:!!q.accepted,informed:!!q.informed,inspected:{},ending:['return','share','claim'].includes(q.ending)?q.ending:null,rewarded:!!q.rewarded,tracked:!!q.tracked};for(const z of ['transit_depot','traverse_archives','mooring_station'])f.quest.inspected[z]=!!q.inspected?.[z];
 for(const t of (Array.isArray(p.transactions)?p.transactions:[]).slice(-80))if(t&&typeof t.text==='string')f.transactions.push({text:t.text.slice(0,350),zone:String(t.zone||'').slice(0,100),kind:String(t.kind||'').slice(0,25)});return s;};state=migrateState(state);
function v026Log(kind,text){state.v026.transactions.push({kind,text,zone:world?.id||''});if(state.v026.transactions.length>80)state.v026.transactions.shift();}
function v026Qty(id){if(id==='caps')return state.player.caps||0;if(WEAPONS[id])return state.equipment.ownedWeapons.includes(id)?1:0;if(ARMORS[id])return state.equipment.ownedArmors.includes(id)?1:0;return isAmmo(id)?ammoAmount(id):state.inventory[id]||0;}
function v026Category(id){return WEAPONS[id]?'weapon':ARMORS[id]?'armor':AMMO_INFO[id]?'ammo':V026_JUNK[id]?'junk':['stimpak','radaway','water','food','ration','antibiotics','fireGel'].includes(id)?'aid':id==='caps'?'caps':(ITEM_VALUES[id]>0||['bobbyPin','ceramicFilter'].includes(id))?'material':'quest';}
function v026Mass(id){if(id==='caps')return 0;if(V026_JUNK[id])return V026_JUNK[id].mass;if(WEAPONS[id]){const w=WEAPONS[id];return w.heavy?9:w.melee?2.2:w.clip>20?4.3:2.0;}if(ARMORS[id])return /power|cargo/i.test(id)?16:4.5;if(AMMO_INFO[id])return /harpoon|missile|miniNuke|grenade/i.test(id)?.3:.012;return({stimpak:.1,radaway:.1,water:.5,ration:.35,food:.4,bobbyPin:.002,cloth:.1,scrap:.25,steelPlate:1.4,clay:.35})[id]??(v026Category(id)==='quest'?0:.15);}
function v026MassTotal(){const ids=new Set([...Object.keys(state.inventory),...Object.keys(state.ammo),...state.equipment.ownedWeapons,...state.equipment.ownedArmors]);return [...ids].reduce((n,id)=>n+v026Mass(id)*v026Qty(id),0);}
function v026Capacity(){return 35+5*(state.character.special.S||1);}
function v026Owned(id){return WEAPONS[id]?state.equipment.ownedWeapons.includes(id):ARMORS[id]?state.equipment.ownedArmors.includes(id):false;}
function v026Grant(id,n,gear=null){if(!v026Known(id)||!v026Count(n))return false;if(WEAPONS[id]||ARMORS[id]){if(v026Owned(id))return false;addOwnedEquipment(id);if(gear){setEquipmentCondition(WEAPONS[id]?'weapon':'armor',id,gear.condition);if(WEAPONS[id])state.equipment.weaponMods[id]=!!gear.mod;}return true;}if(id==='caps')state.player.caps+=n;else if(isAmmo(id))addAmmo(id,n);else addItem(id,n);return true;}
function v026Remove(id,n){if(!Number.isInteger(n)||n<=0||v026Qty(id)<n||WEAPONS[id]||ARMORS[id]||v026Category(id)==='quest')return false;if(id==='caps')state.player.caps-=n;else if(isAmmo(id)){state.ammo[id]-=n;if(ammoIdFor()===id)state.player.ammoReserve=state.ammo[id];}else state.inventory[id]-=n;return true;}
// Optional carry friction, default off. The catalogue sandbox is never trapped by its hundreds of weapons.
const v026Move=tryPlayerMove;tryPlayerMove=function(dx,dz){const k=state.v026?.carry&&v026MassTotal()>v026Capacity()?.65:1;return v026Move(dx*k,dz*k);};
