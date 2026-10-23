/* Geographic field life. A bivouac is a player's temporary addition, never a
   surveyed building. Every service rechecks its physical context at payment. */
const V050_WASTELAND={binding:null,clock:0,drawCache:null};
const V050_CAMP_COST={scrap:3,cloth:1};
const V050_CAMP_RECIPES=['ration','purify','bandage'];
const V050_AID={
 water:{name:'Eau potable',cost:{water:2},caps:10,rep:1},
 food:{name:'Vivres',cost:{food:3},caps:10,rep:1},
 medicine:{name:'Trousse de soins',cost:{stimpak:1,cloth:1},caps:16,rep:2}
};
const V050_AID_FACTIONS={ligue:'ligue',ateliers:'artisans',collines:'collines',vigies:'secours',rade:'rade',insulaires:'francs',arsenal:'arsenal',concorde:'continuite'};
function v050WastelandFresh(){return{schema:1,kitOwned:false,camp:null,restHours:0,crafts:0,aid:{}};}
function v050AidSite(site){return!!site&&site.safe===true&&['settlement','outpost','caravan'].includes(site.kind);}
function v050WastelandMigrate(raw){
 const f=v050WastelandFresh(),old=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{};
 f.kitOwned=old.kitOwned===true;
 for(const k of ['restHours','crafts'])f[k]=typeof old[k]==='number'&&Number.isFinite(old[k])?Math.floor(clamp(old[k],0,100000)):0;
 const c=old.camp;
 if(f.kitOwned&&c&&typeof c==='object'&&typeof c.lat==='number'&&typeof c.lon==='number'&&Number.isFinite(c.lat)&&Number.isFinite(c.lon)){
  const macro=v046Region(c.lat,c.lon);
  if(macro)f.camp={lat:c.lat,lon:c.lon,macro,yaw:typeof c.yaw==='number'&&Number.isFinite(c.yaw)?c.yaw%TAU:0};
 }
 if(old.aid&&typeof old.aid==='object'&&!Array.isArray(old.aid))for(const site of V042_CATALOG){
  if(!v050AidSite(site)||!Object.hasOwn(old.aid,site.id))continue;
  const p=old.aid[site.id];if(!p||typeof p!=='object'||Array.isArray(p))continue;
  const record={};for(const type of Object.keys(V050_AID))if(Object.hasOwn(p,type)&&p[type]===true)record[type]=true;
  if(Object.keys(record).length)f.aid[site.id]=record;
 }
 return f;
}
const v050WastelandBase=baseState;
baseState=function(){const s=v050WastelandBase();s.v050Wasteland=v050WastelandFresh();return s;};
const v050WastelandMigration=migrateState;
migrateState=function(input={}){const s=v050WastelandMigration(input);s.v050Wasteland=v050WastelandMigrate(input.v050Wasteland);return s;};
state=migrateState(state);if(world)v049Own(world);

function v050WastelandBlocked(){
 if(!v027CanAct())return'Action disponible dans le Pip-Boy, pendant une partie active.';
 if(V046.lab)return'Le banc synthétique ne modifie pas votre matériel de campagne.';
 if(!world?.v046||!world.geoMacro)return'Rejoignez le territoire géographique extérieur.';
 if(V046.busy||V047.pending||zoneTransitioning)return'Attendez la fin du chargement du secteur.';
 const p=state.player.pos,ground=v050TravelGround(v050CampStage(),world,p[0],p[2],.38);
 if(!onGround||ground===null||!Number.isFinite(ground)||Math.abs(p[1]-ground-playerEyeHeight())>.75)return'Rejoignez un sol stable et dégagé avant cette opération.';
 if(v050TravelNearbyThreat(world,state.player.pos))return'Éloignez-vous du combat et des menaces avant cette opération.';
 if((world.enemies||[]).some(e=>e.alive&&dist2(e.pos,state.player.pos)<55))return'Une menace est encore trop proche pour installer une halte.';
 return null;
}
function v050WastelandNotify(reason){return v027Notify(reason);}
/* Roll back these synchronous transactions when browser persistence fails. No
   second wallet or world-state owner is created. Nothing waits on a callback. */
function v050WastelandCommit(change,message){
 const owner=state,keys=['inventory','player','needs','rep','worldTime','v050Wasteland','v020','status','lastSave'];
 const snapshot=Object.fromEntries(keys.map(k=>[k,owner[k]===undefined?undefined:deepClone(owner[k])]));
 try{
  change();
  if(state!==owner||saveGame(false)===false)throw Error('La sauvegarde ne peut pas être conservée dans ce navigateur.');
 }catch(error){
  if(state===owner)for(const k of keys){if(snapshot[k]===undefined)delete owner[k];else owner[k]=snapshot[k];}
  return v050WastelandNotify(error.message||'Opération annulée sans paiement.');
 }
 V050_WASTELAND.binding=null;V050_WASTELAND.drawCache=null;v050CampBind();
 V027.message=message;toast(message,'good');renderPipboy();return true;
}
function v050CampStage(){return{records:world.v046Records,bank:world.v047TerrainBank||V046.terrain,geoColliders:(world.colliders||[]).filter(c=>c.v046Tile)};}
function v050CampGround(x,z,stage=v050CampStage()){
 const y=v050TravelGround(stage,world,x,z,.5);
 return y!==null&&Number.isFinite(y)&&!v046Blocked(world,x,z)?y:null;
}
function v050CampSpot(){
 if(!world?.v046)return null;
 const p=state.player.pos,stage=v050CampStage(),yaw=state.player.yaw||0;
 for(const r of[2.6,4.2])for(const angle of[0,-.8,.8,Math.PI]){
  const x=p[0]+Math.sin(yaw+angle)*r,z=p[2]-Math.cos(yaw+angle)*r,y=v050CampGround(x,z,stage);
  if(y===null)continue;
  const margin=[[1.3,0],[-1.3,0],[0,1.3],[0,-1.3],[1,1],[-1,-1],[1,-1],[-1,1]];
  if(margin.some(([dx,dz])=>{const h=v050CampGround(x+dx,z+dz,stage);return h===null||Math.abs(h-y)>.45;}))continue;
  const[lat,lon]=v015GeoUnproject(world.id,x,z),macro=v046Region(lat,lon);
  if(macro)return{lat,lon,macro,yaw};
 }
 return null;
}
function v050CampPosition(){
 const c=state.v050Wasteland?.camp;if(!c||!world?.v046)return null;
 const p=v015GeoProject(world.id,c.lat,c.lon);
 if(!p||!p.every(Number.isFinite)||Math.hypot(p[0]-state.player.pos[0],p[2]-state.player.pos[2])>720)return null;
 const h=v046HeightAt(p[0],p[2]);if(h.height===null||!Number.isFinite(h.height))return null;
 return[p[0],Math.max(0,h.height),p[2]];
}
function v050CampNear(){const p=v050CampPosition();return!!p&&dist2(p,state.player.pos)<=5&&Math.abs(p[1]+playerEyeHeight()-state.player.pos[1])<2.5;}
function v050CampUsable(){const p=v050CampPosition();return!!p&&v050CampNear()&&v050CampGround(p[0],p[2])!==null&&lineOfSight(state.player.pos,[p[0],p[1]+.6,p[2]]);}
function v050CampPlace(){
 const blocked=v050WastelandBlocked();if(blocked)return v050WastelandNotify(blocked);
 const s=state.v050Wasteland;if(s.camp)return v050WastelandNotify('Repliez votre bivouac existant avant de le déplacer.');
 if(!s.kitOwned&&!hasCost(V050_CAMP_COST))return v050WastelandNotify('Kit : il faut 3 ferrailles et 1 tissu. Aucun matériau dépensé.');
 const spot=v050CampSpot();if(!spot)return v050WastelandNotify('Pas de sol dégagé à proximité : évitez routes, murs, eau et pente, puis réessayez.');
 return v050WastelandCommit(()=>{if(!s.kitOwned&&!v020Spend(V050_CAMP_COST))throw Error('Matériaux devenus insuffisants.');s.kitOwned=true;s.camp=spot;},'Bivouac déployé. Votre halte est prête.');
}
function v050CampPack(){
 const blocked=v050WastelandBlocked();if(blocked)return v050WastelandNotify(blocked);
 if(!v050CampNear())return v050WastelandNotify('Approchez votre bivouac à moins de 5 m pour le replier.');
 return v050WastelandCommit(()=>{state.v050Wasteland.camp=null;},'Bivouac replié : le même kit pourra être redéployé.');
}
function v050CampRest(hours){
 const blocked=v050WastelandBlocked();if(blocked)return v050WastelandNotify(blocked);
 if(![1,4].includes(hours)||!v050CampUsable())return v050WastelandNotify('Le repos demande votre bivouac accessible à moins de 5 m, sur un sol toujours dégagé.');
 if(state.status?.infection>0||state.status?.bleeding>0||state.status?.burning>0)return v050WastelandNotify('Traitez l’infection, le saignement ou la brûlure avant de dormir en plein air.');
 const cost=hours===1?{water:1}:{water:1,ration:1};
 if(!hasCost(cost))return v050WastelandNotify('Réserves insuffisantes : aucun temps ni objet dépensé.');
 return v050WastelandCommit(()=>{
  if(!v020Spend(cost))throw Error('Réserves devenues insuffisantes.');
  state.worldTime=(state.worldTime+hours)%24;state.v050Wasteland.restHours+=hours;
  state.player.hp=Math.min(state.player.maxHp,state.player.hp+12*hours);state.player.ap=state.player.maxAp;
  if(state.needs){state.needs.fatigue=Math.max(0,state.needs.fatigue-25*hours);state.needs.thirst=Math.max(0,state.needs.thirst-20);if(hours===4)state.needs.hunger=Math.max(0,state.needs.hunger-25);}
  if(state.v020)state.v020.restHours+=hours;
 },`${hours} h de repos au bivouac. Les radiations et les blessures ne sont pas effacées.`);
}
function v050CampCraft(id){
 const blocked=v050WastelandBlocked();if(blocked)return v050WastelandNotify(blocked);
 const recipe=V050_CAMP_RECIPES.includes(id)&&V020_RECIPES.find(r=>r.id===id);
 if(!recipe||!v050CampUsable())return v050WastelandNotify('Cette préparation demande votre bivouac accessible à moins de 5 m.');
 if(!hasCost(recipe.cost))return v050WastelandNotify('Ingrédients insuffisants : aucun paiement partiel.');
 return v050WastelandCommit(()=>{if(!v020Spend(recipe.cost))throw Error('Ingrédients devenus insuffisants.');state.inventory[recipe.item]=(state.inventory[recipe.item]||0)+recipe.count;state.v050Wasteland.crafts++;},recipe.name+' · préparation au bivouac terminée.');
}
function v050AidContact(site){
 if(!v050AidSite(site)||!v042SiteDiscovered(site)||!world?.v046)return false;
 const p=state.player.pos;
 return(world.npcs||[]).some(n=>n.alive!==false&&n.v042Site===site.id&&dist2(n.pos,p)<=8&&Math.abs((n.pos[1]||0)+playerEyeHeight()-p[1])<3&&lineOfSight([p[0],p[1],p[2]],[n.pos[0],(n.pos[1]||0)+1.4,n.pos[2]]));
}
function v050AidDeliver(siteId,type){
 const blocked=v050WastelandBlocked();if(blocked)return v050WastelandNotify(blocked);
 const site=v042Site(siteId),aid=Object.hasOwn(V050_AID,type)&&V050_AID[type];
 if(!aid||!v050AidContact(site))return v050WastelandNotify('Approchez un habitant du relais découvert à moins de 8 m, avec un accès dégagé.');
 if(state.v050Wasteland.aid[siteId]?.[type])return v050WastelandNotify('Cette livraison a déjà été reçue : aucune seconde récompense.');
 if(!hasCost(aid.cost))return v050WastelandNotify('Il manque des fournitures : aucun paiement partiel.');
 return v050WastelandCommit(()=>{
  if(!v020Spend(aid.cost))throw Error('Fournitures devenues insuffisantes.');
  const ledger=state.v050Wasteland.aid;ledger[siteId]??={};ledger[siteId][type]=true;
  state.player.caps+=aid.caps;const faction=V050_AID_FACTIONS[site.faction];if(faction)state.rep[faction]=clamp((state.rep[faction]||0)+aid.rep,-100,100);
 },`${site.name} reçoit ${aid.name.toLocaleLowerCase('fr')} : ${aid.caps} capsules${V050_AID_FACTIONS[site.faction]?' et confiance accrue':''}.`);
}
function v050CampBind(){
 if(!world)return;const c=state.v050Wasteland?.camp,token=V050_WASTELAND.binding;
 if(token?.world===world&&token.state===state&&token.camp===c)return;
 world.interactables=(world.interactables||[]).filter(i=>i.id!=='v050-camp');
 const p=v050CampPosition();if(p)addInteract(world,'v050-camp',[p[0],p[1]+.6,p[2]],'Bivouac · repos et préparations',()=>v027Open('status','camp'),{radius:4.5,kind:'bench'});
 V050_WASTELAND.binding={world,state,camp:c};
}
const v050CampPublish=v046Publish;
v046Publish=function(...args){const result=v050CampPublish(...args);V050_WASTELAND.binding=null;if(args[0]===world)v050CampBind();return result;};
const v050CampUpdate=updatePlayer;
updatePlayer=function(dt){const result=v050CampUpdate(dt);if(mode==='PLAYING'&&gameStarted&&!zoneTransitioning){V050_WASTELAND.clock+=dt;if(V050_WASTELAND.clock>=1){V050_WASTELAND.clock=0;v050CampBind();}}return result;};
const v050CampDraws=collectDraws;
collectDraws=function(t){
 const draws=v050CampDraws(t),p=v050CampPosition(),c=state.v050Wasteland?.camp;if(!p||!c)return draws;
 let cache=V050_WASTELAND.drawCache;
 if(!cache||cache.world!==world||cache.camp!==c||cache.height!==p[1]){
  const temp={staticDraws:[]};addBox(temp,[p[0],p[1]+.09,p[2]],[1.05,.18,2.1],[.27,.35,.22],c.yaw);
  addBox(temp,[p[0]+1.1,p[1]+.28,p[2]+.6],[.6,.56,.65],COLORS.clothTan,c.yaw);
  addPart(temp,'cylinder',[p[0]-1,p[1]+.18,p[2]],[.28,.36,.28],COLORS.darkMetal);
  cache=V050_WASTELAND.drawCache={world,camp:c,height:p[1],draws:temp.staticDraws};
 }
 return draws.concat(cache.draws);
};
function v050CampPanel(c){
 const s=state.v050Wasteland,p=v050CampPosition(),near=v050CampNear(),usable=near&&v050CampUsable(),blocked=v050WastelandBlocked(),distance=p?Math.round(dist2(p,state.player.pos)):null;
 c.innerHTML=`<div class="p27-long v050-fieldlife"><p class="p27-kicker">EXPLORATION / HALTE PORTABLE</p><h2>Votre bivouac</h2><p>Installez une halte, reposez-vous et préparez vos réserves avant de reprendre la route.</p>
 <section><h3>${s.camp?'BIVOUAC DÉPLOYÉ':s.kitOwned?'KIT REPLIÉ':'CONSTRUIRE UN KIT'}</h3><p>${s.camp?`${escapeHtml(V015_GEO_MACROS[s.camp.macro]?.name||'Territoire')}${distance===null?' · hors du secteur chargé':` · ${distance} m`}. Repliez le bivouac sur place avant de le déplacer.`:s.kitOwned?'Votre kit existant sera réutilisé. Aucun remboursement de matériaux ni second kit gratuit.':'Première installation : 3 ferrailles et 1 tissu. Le kit se replie puis se redéploie sans nouvelle construction.'}</p>
 <div class="p27-actions">${v027Button(s.kitOwned?'Déployer près de moi':'Construire et déployer','w50:pitch','',!!blocked||!!s.camp||(!s.kitOwned&&!hasCost(V050_CAMP_COST)))}${v027Button('Replier le bivouac','w50:pack','',!!blocked||!near)}</div>
 ${blocked?`<p class="v050-field-warning">${escapeHtml(blocked)}</p>`:'<p>Choisissez un emplacement plat et dégagé, à l’écart des routes, de l’eau et des menaces.</p>'}</section>
 <section><h3>REPOS ET RÉSERVES</h3><p>À moins de 5 m du bivouac, sans ennemi proche. Une heure rend 12 PV et réduit la fatigue de 25. Les blessures et radiations exigent leurs soins habituels.</p><div class="p27-actions">${v027Button('Repos 1 h · 1 eau','w50:rest','1',!!blocked||!usable||!hasCost({water:1}))}${v027Button('Repos 4 h · 1 eau, 1 ration','w50:rest','4',!!blocked||!usable||!hasCost({water:1,ration:1}))}</div><p>${s.restHours} h au bivouac · ${s.crafts} préparations.</p></section>
 <section><h3>PRÉPARATIONS DE TERRAIN</h3><p>L’établi reste nécessaire aux armes, aux munitions et aux réparations. Le bivouac ne sert qu’à ces préparations.</p><div class="v050-field-recipes">${V020_RECIPES.filter(r=>V050_CAMP_RECIPES.includes(r.id)).map(r=>`<article><h4>${escapeHtml(r.name)}</h4><p>${v020HtmlCost(r.cost)} → ${r.count} ${escapeHtml(v020Label(r.item))}</p>${v027Button('Préparer','w50:craft',r.id,!!blocked||!usable||!hasCost(r.cost))}</article>`).join('')}</div></section></div>`;
}
function v050AidPanel(c){
 const sites=V042_CATALOG.filter(s=>v050AidSite(s)&&v042SiteDiscovered(s)),blocked=v050WastelandBlocked();
 sites.sort((a,b)=>Number(v050AidContact(b))-Number(v050AidContact(a))||a.name.localeCompare(b.name,'fr'));
 c.innerHTML=`<div class="p27-long v050-fieldlife"><p class="p27-kicker">RÉSEAU RÉGIONAL / FOURNITURES</p><h2>Entraide des relais</h2><p>Apportez des réserves à un habitant d’un relais découvert. Chaque relais accepte une seule livraison de chaque type, conservée dans votre sauvegarde. Les capsules couvrent une partie du transport ; la confiance progresse auprès de sa faction.</p>${blocked?`<p class="v050-field-warning">${escapeHtml(blocked)}</p>`:''}${sites.length?sites.map(site=>{const ledger=state.v050Wasteland.aid[site.id]||{},contact=v050AidContact(site);return`<section><h3>${escapeHtml(site.name)}</h3><p>${escapeHtml(site.factionLabel||site.faction)} · ${Object.keys(ledger).length}/3 livraisons${contact?' · HABITANT À PORTÉE':' · approchez un habitant à moins de 8 m'}</p><div class="v050-field-recipes">${Object.entries(V050_AID).map(([type,aid])=>`<article><h4>${aid.name}</h4><p>${v020HtmlCost(aid.cost)}</p><p>${aid.caps} capsules · ${aid.rep} confiance</p>${v027Button(ledger[type]?'Livraison reçue':'Remettre les fournitures','w50:aid',site.id+'|'+type,!!blocked||!contact||!!ledger[type]||!hasCost(aid.cost))}</article>`).join('')}</div></section>`;}).join(''):'<p>Aucun relais découvert. Explorez les implantations habitées du territoire pour les voir ici.</p>'}</div>`;
}
const v050CampStatus=v027Status;
v027Status=function(c){if(V027.sub==='camp')return v050CampPanel(c);return v050CampStatus(c);};
const v050AidData=v027Data;
v027Data=function(c){if(V027.sub==='aid')return v050AidPanel(c);return v050AidData(c);};
const v050WastelandDispatch=v027Dispatch;
v027Dispatch=function(action,arg=''){
 if(!action.startsWith('w50:'))return v050WastelandDispatch(action,arg);
 if(!v027CanAct())return false;
 if(action==='w50:pitch')return v050CampPlace();
 if(action==='w50:pack')return v050CampPack();
 if(action==='w50:rest')return v050CampRest(Number(arg));
 if(action==='w50:craft')return v050CampCraft(arg);
 if(action==='w50:aid'){const parts=arg.split('|');return parts.length===2?v050AidDeliver(...parts):false;}
 return false;
};
function v050WastelandAfterInit(){
 V027_SUBS.status.camp='BIVOUAC';V027_SUBS.data.aid='ENTRAIDE';
 Object.assign(window.__MISTRAL_DEBUG,{v050WastelandInfo:()=>({schema:1,state:deepClone(state.v050Wasteland),campPosition:v050CampPosition(),campNear:v050CampNear(),blocked:v050WastelandBlocked(),nearbyAid:V042_CATALOG.filter(v050AidContact).map(s=>s.id)}),v050WastelandAction:v027Dispatch});
}
