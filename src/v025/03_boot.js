function v025ResumeSandbox(){try{const keys=[V018_SANDBOX_KEY,'fallout_mistral_sandbox_v024','fallout_mistral_sandbox_v023','fallout_mistral_sandbox_v022','fallout_mistral_sandbox_v021','fallout_mistral_sandbox_v020','fallout_mistral_sandbox_v018'],key=keys.find(k=>localStorage.getItem(k));if(!key)return v020Notify('Aucune exploration sauvegardée.');const raw=JSON.parse(localStorage.getItem(key));v018ValidateSave(raw);state=migrateState(raw);v018SessionKind='sandbox';syncEquipment();gameStarted=true;hideAllScreens();loadZone(state.player.zone,{instance:!V015_GEO_MACROS[state.player.zone],force:true,silent:true,noTravel:true,spawn:state.player.pos,yaw:state.player.yaw});saveGame();return true;}catch(e){toast('Exploration non chargée : '+e.message,'bad');return false;}}
function v025Start(){if(!confirm('Ouvrir une exploration séparée au dépôt pour essayer le ciblage dans la scène ? La campagne et les anciennes sauvegardes sont conservées. Une précédente exploration v0.25 sera remplacée.'))return false;
 startNewGame(true);state.v018.travelMode='story';loadZone('transit_depot',{instance:true,force:true,silent:true,noTravel:true});const es=world.enemies.filter(e=>e.alive);
 let found=false;for(const e of es){for(const [dx,dz]of [[0,7],[5,5],[-5,5],[0,-7],[7,0],[-7,0]]){const p=[e.pos[0]+dx,groundHeightAt(e.pos[0]+dx,e.pos[2]+dz,e.pos[1])+1.65,e.pos[2]+dz];if(!collidesAt(p[0],p[2],.36,p[1])&&lineOfSight(p,[e.pos[0],e.pos[1]+1.2,e.pos[2]])){state.player.pos=p;state.player.yaw=Math.atan2(-dx,dz);state.player.pitch=0;found=true;break;}}if(found)break;}
 state.player.ap=state.player.maxAp;state.v021.returnPoints=[{zone:'aubagne'}];saveGame();if(found)toggleVATS();return true;
}
function v025AfterInit(){v025Layout();document.title='Fallout : Mistral · v0.25 · La cible dans le monde';$('v020Version').textContent='v0.25 · V.A.T.S. sur les ennemis de la scène · membres gauche / droit · caméra de visée et file de tirs. Carte réelle non intégrée.';
 const b=document.createElement('button');b.id='btnV025';b.textContent='Ciblage dans la scène · exploration séparée';b.onclick=v025Start;$('menuScreen').querySelector('nav').prepend(b);if($('btnV023Resume'))$('btnV023Resume').onclick=v025ResumeSandbox;
 const oldStatus=v018OpenStatus;v018OpenStatus=function(){oldStatus();const el=$('v018StatusScreen')?.querySelector('.eyebrow');if(el)el.textContent='ÉTAT RÉEL · v0.25 · CIBLAGE SUR LES MODÈLES — AUCUNE CARTE OFFICIELLE';};if($('v018MenuStatus'))$('v018MenuStatus').onclick=v018OpenStatus;
 addEventListener('resize',()=>{if(mode==='VATS'&&V025.active){const c=v025Current();if(c){v025Focus(c.enemy,true);v025Position();}}});
 const debug=window.__MISTRAL_DEBUG;
 Object.assign(debug,{
 v025Info:()=>({version:VERSION,active:V025.active,selected:V025.selected?{enemy:V025.selected.enemy.id,part:V025.selected.part}:null,rigFamilies:['raider','ghoul','robot','drone','crane','boar','dog','tarente','scorpion','crab'],officialTiles:0}),
 v025Snapshot:()=>({mode,player:deepClone(state.player),camera:getCamera(gameClock),screen:deepClone(V025.screen),targets:vatsState?.targets.map(e=>({id:e.id,name:e.name}))||[],parts:v025Current()?.parts.map(p=>({id:p.id,group:p.group,label:p.label,center:p.center,corners:p.corners,cost:p.cost,chance:v020TargetChance(v025Current().enemy,p)}))||[],queue:vatsState?.queue.map(q=>({id:q.part.id,enemy:q.enemy.id,cost:q.cost,rounds:q.rounds,critical:q.critical}))||[],lastShot:V025.lastShot?{emitted:V025.lastShot.emitted,hit:V025.lastShot.hit}:null}),
 v025Select:v025Select,v025Paint:()=>{if(V025.pan)V025.pan.duration=0;v025Paint();return V025.screen;},v025Navigate:(dx,dy)=>vatsNavigate(dx,dy),v025ResumeSandbox,v025Start,
 v025RigInfo:(i=0)=>{const e=world.enemies[i];if(!e)return null;const rig=v025Rig(e);return{type:e.type,family:rig.family,parts:rig.parts.map(p=>({id:p.id,label:p.label,center:p.center,cost:p.cost,group:p.group,size:p.bounds.max.map((v,j)=>v-p.bounds.min[j])})),draws:rig.draws.length};},
 v025Damage:(id,n=20,i=0)=>{damageEnemy(world.enemies[i],n,id,false,0);return world.enemies[i].health;},v025Loss:(i=0)=>Object.fromEntries(enemyHitParts(world.enemies[i]).map(p=>[p.id,v025LimbLoss(world.enemies[i],p.id)])),
 v025Wall:(x,y,z,sx,sy,sz)=>{addBox(world,[x,y,z],[sx,sy,sz],[.41,.45,.35]);addCollider(world,x,z,sx,sz,{minY:y-sy/2,maxY:y+sy/2});},
 v025MoveEnemy:(i,p,yaw=null)=>{const e=world.enemies[i];e.pos=[...p];if(yaw!==null)e.yaw=yaw;V025.rigs.delete(e);if(V025.active){v025Focus(e,true);renderVATS();}},
 v025Visibility:()=>world.enemies.map(e=>({id:e.id,parts:enemyHitParts(e).map(p=>({id:p.id,chance:v020TargetChance(e,p)}))})),
 v025EmitIndex:()=>V020.shots,v025Tinted:()=>collectDraws(gameClock).filter(d=>d.v025Enemy&&d.emissive>=.25&&d.color?.[1]>.55).map(d=>({enemy:d.v025Enemy,part:d.v025Part})),
 v025HitRay:(o,d)=>{const h=acquireShotTarget(o,d);return h?{enemy:h.enemy.id,part:h.part.id,t:h.t}:null;},
 });
 // Old QA callers use grouped names. Aliases address a real left member; the
 // rendered UI exposes only the actual new part IDs, never duplicate targets.
 debug.v023Select=(target,id)=>{if(!vatsState)return;vatsState.targetIndex=target;const parts=enemyHitParts(vatsState.targets[target]),alias=id==='arms'?'arm_l':id==='legs'?'leg_l':id;vatsState.partIndex=parts.findIndex(p=>p.id===id);if(vatsState.partIndex<0)vatsState.partIndex=Math.max(0,parts.findIndex(p=>p.id===alias));renderVATS();};
 debug.v020VatsCancel=()=>v020CancelVats();debug.toggleVATS=()=>toggleVATS();debug.v023ResumeSandbox=()=>v025ResumeSandbox();
}
