/* Critical reserve is paid only for an emitted, valid shot; no geometry bypass. */
const v023Chance=v020TargetChance;v020TargetChance=function(e,p){const n=v023Chance(e,p);if(n<=0)return 0;if(V023.criticalShot)return 100;return Math.min(95,n+(v023Tagged('sneak')&&state.player.crouched?5:0));};vatsChance=v020TargetChance;
const v023Impact=v020Impact;v020Impact=function(e,n,part,crit,w){V023.hit=true;return v023Impact(e,n,part,crit||V023.criticalShot,w);};
const v023DamageWithSkills=v020Damage;v020Damage=function(w,e,part,crit){return v023DamageWithSkills(w,e,part,crit||V023.criticalShot);};
const v023Emit=v020Emit;v020Emit=function(forced=null){if(forced?.critical&&state.v023.critical<100)return false;V023.criticalShot=!!forced?.critical;V023.hit=false;let result=false;try{result=v023Emit(forced);if(result&&forced){if(forced.critical){state.v023.critical=0;v020Log('critique','Réserve engagée sur une action valide.');}else if(V023.hit)state.v023.critical=Math.min(100,state.v023.critical+16+(state.character.special.L||0));}}finally{V023.criticalShot=false;}updateHUD();return result;};

function v024EnemyFigureClass(e){
  const family=typeof v021EnemyFamily==='function'?v021EnemyFamily(e):(e?.type||'');
  if(['robot','automaton','drone'].includes(family))return 'robot';
  if(['ghoul','tarente','beast','dog'].includes(family))return 'feral';
  return 'humanoid';
}
function v024PartPlacement(partId){
  return({head:{x:50,y:18},body:{x:50,y:45},arms:{x:78,y:43},legs:{x:50,y:74}}[partId]||{x:50,y:50});
}
function v024EnsureVatsLayout(){
  const root=$('vats');if(!root)return null;let layout=$('v024VatsLayout');
  const parts=$('vatsParts'),queue=root.querySelector('.vatsQueue'),footer=root.querySelector('footer');
  if(!layout){
    layout=document.createElement('div');layout.id='v024VatsLayout';
    const figure=document.createElement('section');figure.id='v024VatsFigure';figure.setAttribute('aria-label','Schéma de ciblage V.A.T.S.');
    root.insertBefore(layout,queue);
    layout.append(parts,figure,queue);
  }
  let info=$('v023VatsInfo');if(!info){info=document.createElement('div');info.id='v023VatsInfo';root.insertBefore(info,footer)}
  return {layout,figure:$('v024VatsFigure'),info};
}
function v024FigureMarkup(e,parts,selectedIndex){
  const klass=v024EnemyFigureClass(e),selected=parts[selectedIndex]||parts[0],distance=Math.round(vLen(vSub(e.pos,state.player.pos))),queued=(vatsState?.queue||[]).filter(q=>q.enemy===e).length;
  const hotspots=parts.map((part,i)=>{const pos=v024PartPlacement(part.id),chance=v020TargetChance(e,part),active=i===selectedIndex,disabled=chance<=0;return `<button class="v24-part-hotspot ${active?'selected':''}" style="left:${pos.x}%;top:${pos.y}%" data-v24-part="${i}" ${disabled?'disabled':''} aria-label="${escapeHtml(part.label)}"><span>${chance}%</span><b>${escapeHtml(part.label)}</b><small>${part.cost} PA</small></button>`}).join('');
  return `<div class="v24-stage ${klass}"><div class="v24-stage-label"><small>CIBLE EN VUE</small><b>${escapeHtml(e.name)}</b><span>${distance} m · ${queued} action(s) réservée(s)</span></div><div class="v24-target-frame"><div class="v24-silhouette ${klass}"><div class="v24-shape head"></div><div class="v24-shape torso"></div><div class="v24-shape arm left"></div><div class="v24-shape arm right"></div><div class="v24-shape leg left"></div><div class="v24-shape leg right"></div>${hotspots}</div><div class="v24-corners"><i></i><i></i><i></i><i></i></div></div><div class="v24-stage-readout"><div><small>SÉLECTION</small><b>${escapeHtml(selected.label)}</b></div><div><small>PRÉCISION</small><b>${v020TargetChance(e,selected)} %</b></div><div><small>COÛT</small><b>${selected.cost} PA</b></div></div></div>`;
}

toggleVATS=function(){if(mode==='VATS'){closeVATS();return false;}if(mode!=='PLAYING'||V020.reload||reloadTimer>0||state.player.hp<=0||zoneTransitioning)return false;if(equipmentCondition('weapon',state.player.weaponId)<=0)return v020Notify('Réparez cette arme avant le V.A.T.S.',true);const targets=vatsTargets();if(!targets.length)return v020Notify('Aucune cible visible et à portée.',true);const min=Math.min(...targets.flatMap(e=>enemyHitParts(e).filter(p=>v020TargetChance(e,p)>0).map(p=>p.cost)));if(state.player.ap<min)return v020Notify('Points d’action insuffisants.',true);v020Mode('VATS');vatsState={targets,targetIndex:0,partIndex:0,queue:[]};$('vats').classList.remove('hidden');renderVATS();return true;};
function v023Queue(critical=false){if(mode!=='VATS'||!vatsState)return false;if(vatsState.queue.length>=6)return v020Notify('Six actions au maximum.',true);const e=vatsState.targets[vatsState.targetIndex],part=enemyHitParts(e)[vatsState.partIndex];if(!part||v020TargetChance(e,part)<=0)return v020Notify('Cible masquée ou hors portée.',true);const queue=vatsState.queue,cost=queue.reduce((n,q)=>n+q.cost,0),ammo=queue.reduce((n,q)=>n+q.rounds,0),w=currentWeapon(),profile=v020Profile(w),rounds=w.melee?0:Math.min(profile.rounds,state.player.ammoClip-ammo);if(cost+part.cost>state.player.ap)return v020Notify('Points d’action déjà réservés.',true);if(!w.melee&&rounds<=0)return v020Notify('Chargeur déjà réservé.',true);if(critical&&(state.v023.critical<100||queue.some(q=>q.critical)))return v020Notify('Une réserve pleine et non engagée est nécessaire.',true);queue.push({enemy:e,part:{...part},cost:part.cost,rounds,weapon:state.player.weaponId,critical});renderVATS();return true;}
vatsAddCurrent=function(){return v023Queue(false);};
function v023EditQueue(i,move=0){if(mode!=='VATS'||!vatsState||!Number.isInteger(i)||i<0||i>=vatsState.queue.length)return false;const q=vatsState.queue;if(!move)q.splice(i,1);else{const next=i+move;if(next<0||next>=q.length)return false;[q[i],q[next]]=[q[next],q[i]];}renderVATS();return true;}
renderVATS=function(){
  if(!vatsState)return;vatsState.targets=vatsState.targets.filter(e=>e.alive);if(!vatsState.targets.length){closeVATS();return}
  vatsState.targetIndex=(vatsState.targetIndex+vatsState.targets.length)%vatsState.targets.length;
  const e=vatsState.targets[vatsState.targetIndex],parts=enemyHitParts(e);if(!parts.length){closeVATS();return}
  vatsState.partIndex=(vatsState.partIndex+parts.length)%parts.length;
  const p=parts[vatsState.partIndex],w=currentWeapon(),used=vatsState.queue.reduce((n,q)=>n+q.rounds,0),ap=vatsState.queue.reduce((n,q)=>n+q.cost,0);
  $('vatsTargetName').textContent=`${e.name.toUpperCase()} · ${Math.ceil(e.health)}/${e.maxHealth} PV`;
  $('vatsAp').textContent=Math.max(0,Math.floor(state.player.ap-ap));
  const nodes=v024EnsureVatsLayout(),box=$('vatsParts'),qbox=$('vatsQueue'),figure=nodes.figure,panel=nodes.info;
  box.innerHTML=parts.map((part,i)=>{const active=i===vatsState.partIndex,chance=v020TargetChance(e,part),queued=vatsState.queue.filter(q=>q.enemy===e&&q.part.id===part.id).length;return `<button class="${active?'selected':''} v24-part-card" data-v24-part="${i}" ${chance<=0?'disabled':''}><span>${chance}%</span><b>${escapeHtml(part.label)}</b><small>${part.cost} PA · ×${part.mult.toFixed(2)}${queued?` · ${queued} en file`:''}</small></button>`}).join('');
  box.querySelectorAll('[data-v24-part]').forEach(btn=>btn.onclick=()=>{vatsState.partIndex=+btn.dataset.v24Part;renderVATS()});
  figure.innerHTML=v024FigureMarkup(e,parts,vatsState.partIndex);
  figure.querySelectorAll('[data-v24-part]').forEach(btn=>btn.onclick=()=>{vatsState.partIndex=+btn.dataset.v24Part;renderVATS()});
  const d=Math.round(v020Damage(w,e,p,false)),mit=clamp((e.armor||0)-(w.armorPierce||0),0,.95);
  panel.innerHTML=`<div class="v23-vats-summary"><div><small>ARME / CHARGEUR</small><b>${escapeHtml(w.name)}</b><span>${w.melee?'Contact · sans munitions':`${used} réservé(s) / ${state.player.ammoClip} · ${Math.max(0,state.player.ammoClip-used)} libre(s)`}</span></div><div><small>MEMBRE VISÉ</small><b>${escapeHtml(p.label)}</b><span>Précision ${v020TargetChance(e,p)} % · coût ${p.cost} PA · dégâts ×${p.mult.toFixed(2)}</span></div><div><small>RÉSERVE CRITIQUE</small><b>${Math.floor(state.v023.critical)} / 100</b><progress value="${state.v023.critical}" max="100"></progress></div></div><p class="v23-muted">Armure ennemie estimée : ${(e.armor||0)*100|0} % · pénétration de l’arme : ${(w.armorPierce||0)*100|0} % · mitigation résiduelle ≈ ${Math.round(mit*100)} %. Dégâts estimés : ${d}. Bras affaiblis ${Math.round((e.armDamage||0)*100)} % · jambes ralenties ${Math.round((e.legDamage||0)*100)} %.</p><div class="v23-actions"><button data-v23="vats-target|-1">◀ Cible</button><button data-v23="vats-target|1">Cible ▶</button><button data-v23="vats-add">Ajouter [E]</button><button data-v23="vats-critical" ${state.v023.critical>=100&&!vatsState.queue.some(q=>q.critical)?'':'disabled'}>Ajouter critique [C]</button><button data-v23="vats-execute" ${vatsState.queue.length?'':'disabled'}>Exécuter [Espace]</button><button data-v23="vats-close">Annuler [V]</button></div>`;
  qbox.innerHTML=vatsState.queue.map((q,i)=>`<div class="v23-queue-row"><b>${i+1}</b><span>${escapeHtml(q.enemy.name)} · ${escapeHtml(q.part.label)}<small>${q.cost} PA · ${q.rounds} munition(s)${q.critical?' · CRITIQUE RÉSERVÉ':''}</small></span><button data-v23="queue-up|${i}" aria-label="Monter action ${i+1}" ${i?'':'disabled'}>↑</button><button data-v23="queue-down|${i}" aria-label="Descendre action ${i+1}" ${i<vatsState.queue.length-1?'':'disabled'}>↓</button><button data-v23="queue-remove|${i}" aria-label="Retirer action ${i+1}">×</button></div>`).join('')||'<p class="v23-muted">Sélectionnez une cible, visez un membre puis ajoutez une action. Aucun PA ni aucune munition ne sont dépensés tant que la file n’est pas exécutée.</p>';
};
