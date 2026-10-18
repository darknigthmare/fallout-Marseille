/* A container is a finite persistent ledger. Rendering and UI only reflect it. */
function v026Key(zone,id){return zone+'|'+id;}
function v026NewContainer(w,id,title,pos,items,opts={}){const key=v026Key(w.id,id);let c=state.v026.containers[key];if(!c){const initial=v026CleanItems(items);c={zone:w.id,id,title,pos:[...pos],kind:opts.kind||'chest',items:{...initial},initial,gear:deepClone(opts.gear||{}),owned:!!opts.owned,permission:false,reported:false,lock:opts.lock||0,unlocked:!opts.lock,visited:false,pinWear:0,actor:opts.actor||null};state.v026.containers[key]=c;}return[key,c];}
function v026IsEmpty(c){return !Object.values(c.items).some(n=>n>0);}
function v026Physical(c,r=3.35){if(!world||world.id!==c.zone||state.player.hp<=0||zoneTransitioning)return false;const point=[c.pos[0],c.pos[1]+(c.kind==='remains'?.35:1.05),c.pos[2]];return dist2(state.player.pos,c.pos)<=r&&Math.abs(state.player.pos[1]-point[1])<1.9&&lineOfSight(state.player.pos,point);}
function v026Session(){const ctx=V026.context,c=ctx&&state.v026.containers[ctx.key];return V026.open&&mode==='SALVAGE'&&ctx?.scene===V020.scene&&c&&v026Physical(c)?c:null;}
function v026Attach(w,key,c){if(w.interactables.some(i=>i.id==='v026:'+key))return;const h=c.kind==='remains'?.35:1.05;v020Object(w,'v026:'+key,[c.pos[0],c.pos[1]+h,c.pos[2]],'Fouiller · '+c.title,()=>v026OpenContainer(key),'loot');}
function v026OpenContainer(key){if(!['PLAYING','SALVAGE'].includes(mode))return false;const c=state.v026.containers[key];if(!c||!v026Physical(c))return false;v026Open('bag');V026.tab='loot';V026.context={key,scene:V020.scene};V026.allowOwned=false;V026.selected=Object.keys(c.items).find(id=>c.items[id]>0)||null;V026.lockAngle=0;V026.lockHint='Cherchez un angle libre, sans forcer.';c.visited=true;saveGame();v026Render();return true;}
function v026Authorized(c){return c.unlocked&&(!c.owned||c.permission||V026.allowOwned);}
function v026Take(id,n=1){const c=v026Session();if(!c||!v026Authorized(c)||!Number.isInteger(n)||n<1||n>1000000||(c.items[id]||0)<n)return false;if((WEAPONS[id]||ARMORS[id])&&n!==1)return false;if((WEAPONS[id]||ARMORS[id])&&v026Owned(id))return v026Notice('Ce modèle est déjà dans le sac. Laissez-le ou récupérez ses pièces.');
 if(c.owned&&!c.permission&&!c.reported&&witnessNearby(c.pos)){c.reported=true;addCrime(1,V021_PLACES[c.zone]?.parent==='marseille'?'veilleurs':c.zone==='mooring_station'?'arsenal':'ligue','Prélèvement vu dans une réserve marquée');}
 if(!v026Grant(id,n,c.gear[id]))return false;c.items[id]-=n;v026Log('prendre',`${n} × ${v020Label(id)} — ${c.title}`);v026Commit(c);return true;}
function v026Commit(c){if(c.kind==='loose'&&v026IsEmpty(c)){state.flags.looted[c.id]=true;const l=world?.loot.find(l=>l.id===c.id);if(l)l.taken=true;}saveGame();v026Render();updateHUD();}
function v026TakeAll(){const c=v026Session();if(!c||!v026Authorized(c))return false;let done=false;for(const [id,n]of Object.entries({...c.items}))if(n>0&&!v026Owned(id))done=v026Take(id,n)||done;return done;}
function v026ReturnItem(id,n=1){const c=v026Session();if(!c||(c.id==='consignment'&&state.v026.quest.ending)||!c.unlocked||!Number.isInteger(n)||n<1||v026Category(id)==='quest')return false;
 // Only return items that originally belonged to the container. No generic remote stash or key duplication.
 const gap=Math.max(0,(c.initial[id]||0)-(c.items[id]||0));if(n>gap||WEAPONS[id]||ARMORS[id]||!v026Remove(id,n))return false;c.items[id]=(c.items[id]||0)+n;v026Log('rendre',`${n} × ${v020Label(id)} — ${c.title}`);v026Commit(c);return true;}
function v026RecoverDuplicate(id){const c=v026Session();if(!c||!v026Authorized(c)||!v026Owned(id)||(c.items[id]||0)<1)return false;
 if(c.owned&&!c.permission&&!c.reported&&witnessNearby(c.pos)){c.reported=true;addCrime(1,'ligue','Équipement prélevé dans une réserve marquée');}
 c.items[id]--;addItem('weaponParts',WEAPONS[id]?2:1);v026Log('démonter',`${v020Label(id)} — pièces récupérées sur le doublon`);v026Commit(c);return true;}
function v026LockTolerance(c){return Math.max(4,17-c.lock*2+Math.floor(v023Skill('sneak')/12));}
function v026TurnLock(){const c=v026Session();if(!c||c.unlocked||(state.inventory.bobbyPin||0)<1)return false;const target=10+(detailHash(c.zone+':'+c.id)%161),delta=Math.abs(V026.lockAngle-target),tol=v026LockTolerance(c);
 if(delta<=tol){c.unlocked=true;c.pinWear=0;V026.lockHint='Le barillet est libre.';v026Log('ouvrir','Serrure ouverte — '+c.title);audio.ui(740,.07);saveGame();v026Render();return true;}
 c.pinWear=(c.pinWear||0)+1;V026.lockHint=(delta<35?'Le barillet commence à céder. ':'Le barillet résiste. ')+(V026.lockAngle<target?'Décalez vers la droite.':'Décalez vers la gauche.');if(c.pinWear>=3){state.inventory.bobbyPin--;c.pinWear=0;V026.lockHint+=' Épingle cassée.';}audio.ui(170,.06);saveGame();v026Render();return false;}
function v026DuplicateLoot(l){return {condition:65,mod:false};}
const v026OldTake=takeLoot;takeLoot=function(l){if(!l||l.taken||state.flags.looted[l.id])return false;
 // Unique story keys still use the old atomic acquisition, to preserve campaigns.
 if(!v026Known(l.item)||v026Category(l.item)==='quest')return v026OldTake(l);
 const [key,c]=v026NewContainer(world,l.id,l.label,[l.pos[0],l.pos[1]||0,l.pos[2]],{[l.item]:l.amount},{kind:'loose',owned:l.owned,gear:WEAPONS[l.item]||ARMORS[l.item]?{[l.item]:v026DuplicateLoot(l)}:{}});v026Attach(world,key,c);return v026OpenContainer(key);
};
const v026OldKill=killEnemy;killEnemy=function(e){if(!e?.alive)return;const w=world,loot={...(e.loot||{})};
 // Preserve narrative keys and boss unlocks, but stop ordinary rewards appearing remotely in the bag.
 e.loot={key:loot.key,shipKey:loot.shipKey};try{v026OldKill(e);}finally{e.loot=loot;}
 if(!w||!state.v026||state.v026.containers[v026Key(w.id,'remains:'+e.id)])return;
 const items={};if(loot.ammo&&ammoIdFor())items[ammoIdFor()]=Math.max(1,Math.round(loot.ammo*difficultyInfo().loot));
 for(const [id,n]of Object.entries(loot)){const key=id==='stim'?'stimpak':id;if(['key','shipKey','ammo'].includes(id)||!v026Known(key)||!Number.isFinite(n)||n<=0)continue;items[key]=(items[key]||0)+Math.max(1,Math.round(n*(key==='caps'||key==='stimpak'?1:difficultyInfo().loot)));}
 const family=v021EnemyFamily(e);if(['robot','drone','crane'].includes(family))items.lensHousing=(items.lensHousing||0)+1;else if(family==='raider')items.rationTin=1;
 const [key,c]=v026NewContainer(w,'remains:'+e.id,e.name,[...e.pos],items,{kind:'remains',actor:{type:e.type,yaw:e.yaw||0,boss:!!e.boss}});v026Attach(w,key,c);saveGame();
};
function v026RemainsDraws(out,c){const ds=[],e={id:c.id,type:c.actor.type,pos:[0,0,0],yaw:0,boss:c.actor.boss,alive:false,state:'idle',alerted:false,skin:[.53,.42,.30]};v025OriginalEnemyParts(ds,e,0);if(!ds.length)return;const f=v021EnemyFamily(e),lay=['robot','raider','ghoul','legacy'].includes(f),minY=lay?Math.min(...ds.map(d=>d.pos[2]-(d.scale?.[2]||1)/2)):0;const a=c.actor.yaw||0,co=Math.cos(a),si=Math.sin(a);
 for(const d of ds){let [x,y,z]=d.pos;let sc=[...d.scale];if(lay){[y,z]=[z-minY+.045,-y];sc=[sc[0],sc[2],sc[1]];}else{y=y*.28+.04;sc[1]*=.28;}out.push({...d,pos:[c.pos[0]+co*x+si*z,c.pos[1]+y,c.pos[2]-si*x+co*z],scale:sc,rotY:a,color:d.color.map(v=>v*.72),emissive:0,v026Corpse:c.id});}
}
const v026Draws=collectDraws;collectDraws=function(t){const ds=v026Draws(t);if(!world||!state.v026)return ds;for(const c of Object.values(state.v026.containers))if(c.zone===world.id&&c.kind==='remains'&&c.actor&&dist2(c.pos,state.player.pos)<65)v026RemainsDraws(ds,c);return ds;};
