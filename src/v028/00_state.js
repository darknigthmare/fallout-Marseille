/* v0.28 — local exploration systems. No new map data and no free migration rewards. */
const V028_LIMBS = {
 head:{name:'Tête',detail:'La gêne réduit la précision en tir libre et dans le V.A.T.S.'},
 torso:{name:'Torse',detail:'La récupération naturelle des points d’action ralentit.'},
 leftArm:{name:'Bras gauche',detail:'Le rechargement est plus lent et la mêlée moins efficace.'},
 rightArm:{name:'Bras droit',detail:'Le rechargement est plus lent et la mêlée moins efficace.'},
 leftLeg:{name:'Jambe gauche',detail:'La vitesse de déplacement diminue.'},
 rightLeg:{name:'Jambe droite',detail:'La vitesse de déplacement diminue. Deux jambes très atteintes empêchent le saut.'}
};
const V028={selected:'torso',quote:null,lightCache:new Map(),scene:0,lightCount:0,puzzle:0,gameMessage:'',lampHint:0,manual:false};
function v028Fresh(){return {schema:1,limbs:Object.fromEntries(Object.keys(V028_LIMBS).map(k=>[k,100])),hits:0,lamp:false,history:[],quest:{accepted:false,plan:false,isolated:false,rewarded:false,ending:null,tracked:false},game:{unlocked:false,levels:{}}};}
function v028Number(x,f=0,min=0,max=100){return typeof x==='number'&&Number.isFinite(x)?clamp(x,min,max):f;}
const v028Base=baseState;baseState=function(){const s=v028Base();s.v028=v028Fresh();return s;};
const v028Migrate=migrateState;migrateState=function(raw={}){const s=v028Migrate(raw),p=raw.v028&&typeof raw.v028==='object'?raw.v028:{},f=v028Fresh();
 for(const k of Object.keys(f.limbs))f.limbs[k]=v028Number(p.limbs?.[k],100);
 f.hits=Math.floor(v028Number(p.hits,0,0,1e9));f.lamp=p.lamp===true;
 f.history=(Array.isArray(p.history)?p.history:[]).slice(-32).filter(x=>x&&typeof x.text==='string').map(x=>({text:x.text.slice(0,240),kind:String(x.kind||'soin').slice(0,20)}));
 const q=p.quest||{};for(const k of ['accepted','plan','isolated','rewarded','tracked'])f.quest[k]=q[k]===true;
 f.quest.ending=['repair','manual'].includes(q.ending)?q.ending:null;
 f.game.unlocked=p.game?.unlocked===true;
 for(const [id,g]of Object.entries(p.game?.levels||{}).slice(0,6))if(/^[0-5]$/.test(id)&&g&&Array.isArray(g.turns))f.game.levels[id]={turns:g.turns.slice(0,25).map(n=>Math.floor(v028Number(n,0,0,3))),moves:Math.floor(v028Number(g.moves,0,0,1e6)),best:typeof g.best==='number'&&Number.isInteger(g.best)&&g.best>=0?Math.min(g.best,1e6):null,won:g.won===true,hints:Math.floor(v028Number(g.hints,0,0,1e6))};
 s.v028=f;return s;};state=migrateState(state);
function v028Log(kind,text){state.v028.history.push({kind,text});if(state.v028.history.length>32)state.v028.history.shift();}
function v028Save(){saveGame(false);if(mode==='PIP')renderPipboy();updateHUD();}
function v028Injury(k){return clamp((70-(state.v028?.limbs[k]??100))/70,0,1);}
function v028Effects(){const a=(v028Injury('leftArm')+v028Injury('rightArm'))/2,l=(v028Injury('leftLeg')+v028Injury('rightLeg'))/2;return {move:1-.42*l,reload:1+.65*a,melee:1-.28*a,accuracy:Math.round(14*v028Injury('head')),regen:1-.55*v028Injury('torso'),jump:(state.v028?.limbs.leftLeg??100)>25||(state.v028?.limbs.rightLeg??100)>25};}
const V028_ITEMS={fieldSplint:{name:'Attelle des ateliers',mass:.35,value:35,desc:'Dispositif de jeu : restaure un bras ou une jambe à 100, hors danger. Ne restaure pas les PV.'},traumaKit:{name:'Trousse de traumatologie',mass:.6,value:70,desc:'Dispositif de jeu : restaure une région corporelle à 100, hors danger. Ne traite pas les radiations ou les infections.'}};
for(const [id,d]of Object.entries(V028_ITEMS))ITEM_VALUES[id]=d.value;
const v028Label=itemLabel;itemLabel=function(id){return V028_ITEMS[id]?.name||v028Label(id);};
const v028Category=v026Category;v026Category=function(id){return V028_ITEMS[id]?'aid':v028Category(id);};
const v028Mass=v026Mass;v026Mass=function(id){return V028_ITEMS[id]?.mass??v028Mass(id);};
const v028Description=v026Description;v026Description=function(id){return V028_ITEMS[id]?.desc||v028Description(id);};
// Loaded rounds are weight too; reserve ammo and the active magazine are not counted twice.
const v028MassTotal=v026MassTotal;v026MassTotal=function(){const loaded=state.equipment?.loadedAmmo||{};let n=0;for(const id of state.equipment?.ownedWeapons||[]){const w=WEAPONS[id];if(!w||w.melee||!AMMO_INFO[w.ammoId])continue;const qty=id===state.player.weaponId?state.player.ammoClip:loaded[id];n+=v026Mass(w.ammoId)*v028Number(qty,0,0,w.clip||0);}return v028MassTotal()+n;};
V020_RECIPES.push({id:'fieldSplint',name:'Attelle des ateliers',category:'soins',cost:{cloth:3,scrap:2},item:'fieldSplint',count:1},{id:'traumaKit',name:'Trousse de traumatologie',category:'soins',cost:{cloth:4,chemicals:4,water:1},item:'traumaKit',count:1});
