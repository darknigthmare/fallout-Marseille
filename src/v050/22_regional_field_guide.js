/* A readable workshop catalogue, not an equipment dispenser or discovery grant.
   Real catalogue values and existing ownership remain authoritative. */
if(typeof document!=='undefined')(()=>{
 'use strict';
 let ownedOnly=false;
 const esc=v=>v027Escape(v),number=v=>Number.isFinite(v)?v027Num(v,2):'—';
 const labels={pistol:'Arme de poing',revolver:'Revolver',rifle:'Arme longue',shotgun:'Fusil à grenaille','break-action':'Fusil basculant',energy:'Projecteur énergétique','energy-pistol':'Arme énergétique courte',heavy:'Arme lourde',launcher:'Lanceur',industrial:'Outil détourné',blade:'Lame',melee:'Outil de frappe',fist:'Gantelet',needle:'Aiguille pneumatique','mortar40':'Mortier de 40 mm','ceramic-disc':'Scie à disque réfractaire'};
 const effects={slow:'Ralentissement',burning:'Brûlure',bleeding:'Saignement'};
 function rows(){return MistralRegionalArsenal.catalogue(WEAPONS,AMMO_INFO,state);}
 function render(c){
  const all=rows(),entries=MistralRegionalArsenal.filter(all,V027.query,ownedOnly).map(r=>({...r,badge:r.equipped?'ÉQUIPÉE':r.owned?'EN VOTRE POSSESSION':'FICHE D’ATELIER',hint:r.ammoName}));
  c.innerHTML=`<section class="p27-long" data-arsenal-guide><p class="p27-kicker">CARNET DES ATELIERS</p><p>Le nom sur la crosse ne dit pas quelle cartouche y mettre. Une fiche ne fournit pas l’arme.</p><div class="p27-actions"><button type="button" data-arsenal-filter aria-pressed="${ownedOnly}">${ownedOnly?'Afficher toutes les fiches':'Afficher mes armes seulement'}</button><span role="status">${all.filter(r=>r.owned).length} en votre possession · ${all.length} fiches</span></div></section>`+v027List(entries,r=>`<div data-arsenal-detail="${esc(r.id)}"><p class="p27-kicker">${esc(labels[r.profile]||r.family)}</p><h2>${esc(r.name)}</h2><p>${esc(r.description)}</p>${r.note!==r.description?`<h3>Note d’atelier</h3><p>${esc(r.note)}</p>`:''}<h3>Fiche de référence</h3><p>Valeurs de base, avant état, modifications, protection de la cible et difficulté.</p><dl><dt>Alimentation</dt><dd data-arsenal-ammo>${esc(r.ammoName)}</dd><dt>Dégâts de base par projectile ou impact</dt><dd>${number(r.damage)}</dd><dt>Portée de référence</dt><dd>${number(r.range)} m</dd>${r.melee?'':`<dt>Capacité</dt><dd>${number(r.clip)}</dd><dt>Rechargement</dt><dd>${number(r.reload)} s</dd>`}<dt>Projectiles par salve</dt><dd>${number(r.pellets)}</dd><dt>Impulsions par rafale</dt><dd>${number(r.burst)}</dd>${r.status?`<dt>Effet</dt><dd>${esc(effects[r.status]||r.status)}</dd>`:''}</dl><p>${r.owned?'Cette arme figure dans votre équipement.':'Cette fiche ne signifie pas que l’arme est à vendre ici.'}</p>${r.owned?`<button type="button" data-arsenal-inventory="${esc(r.id)}">Voir dans mon équipement</button>`:''}</div>`,{label:'CARNET DES ATELIERS'});
  c.querySelector('[data-arsenal-filter]').onclick=()=>{if(!v027CanAct())return;ownedOnly=!ownedOnly;V027.page=0;V027.selected=null;renderPipboy();c.querySelector('[data-arsenal-filter]')?.focus({preventScroll:true});};
  c.querySelector('[data-arsenal-inventory]')?.addEventListener('click',e=>{if(!v027CanAct())return;const id=e.currentTarget.dataset.arsenalInventory;if(!state.equipment.ownedWeapons.includes(id))return;v027Set('inventory','weapon');V027.query=WEAPONS[id].name;V027.selected=id;renderPipboy();});
 }
 V027_SUBS.data.atelierArmes='ATELIERS · ARMES';
 const data=v027Data;v027Data=function(c){return V027.sub==='atelierArmes'?render(c):data(...arguments);};
 const oldRender=renderPipboy;renderPipboy=function(){const out=oldRender(...arguments);if(mode==='PIP'&&V027.ready&&V027.tab==='data'&&V027.sub==='atelierArmes'){const toolbar=$('p27Toolbar');if(toolbar)toolbar.hidden=false;if($('p27Sort'))$('p27Sort').hidden=true;if($('p27QuestFilter'))$('p27QuestFilter').hidden=true;}return out;};
})();
