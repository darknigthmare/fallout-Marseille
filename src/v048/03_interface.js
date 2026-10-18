/* Production progress and truthful session-memory diagnostics. */
const V048_PHASES={validation:'Validation du relief',batiments:'Routes et bâtiments',collisions:'Passages et collisions',relief:'Maillages du terrain',nature:'Forêts et mobilier',publication:'Dernières vérifications'};
function v048WorkReport(){const j=V048.job;return j?{id:j.id,phase:j.work.phase,label:V048_PHASES[j.work.phase],done:j.done,total:j.total,...j.work.snapshot()}:null;}
function v048Info(){return {version:V048.version,preparation:v048WorkReport(),lastJob:V048.lastJob,jobs:V048.jobs.slice(),returns:{...V048.returns},exitPending:V048.exitPending?{site:V048.exitPending.site,target:V048.exitPending.target}:null,retained:V048.retained?{site:V048.retained.site,bytes:V048.retained.bytes,lab:V048.retained.lab,createdAt:V048.retained.createdAt}:null,returnBudget:V048.returnLimit};}
function v048RefreshWork(){
  const j=V048.job;if(!j)return;
  const text=`${V048_PHASES[j.work.phase]||j.work.phase} · ${j.done}/${j.total}`;
  const detail=$('v048Phase');if(detail&&detail.textContent!==text)detail.textContent=text;
  if(V047.pending?.blocking&&V046.gate.status.phase==='preparing'){
    const p=$('v046Progress');p.removeAttribute('value');p.setAttribute('aria-valuetext',text);
    $('v046ProgressText').textContent='Les données sont reçues. Préparation de la scène avant publication.';
  }
  const ribbon=$('v047StreamRibbon');if(ribbon&&V047.pending?.warm&&!V047.pending.blocking)ribbon.textContent='SECTEUR SUIVANT · '+text;
}
const v048LoadingBase=v046Loading;
v046Loading=function(s){v048LoadingBase(s);const detail=$('v048Phase');if(detail)detail.hidden=s.phase!=='preparing';
 if(s.phase==='preparing')v048RefreshWork();else $('v046Progress')?.removeAttribute('aria-valuetext');};
const v048PanelBase=v047Panel;
v047Panel=function(c){v048PanelBase(c);const info=v048Info(),last=info.lastJob,old=c.querySelector('.v047-integrity');if(!old)return;
 const section=document.createElement('section');section.className='v048-preparation';section.innerHTML=`<p class="p27-kicker">v0.48 / PRÉPARATION INTERRUPTIBLE</p><h2>REVENIR SANS RECONSTRUIRE</h2><p>Le travail de préparation rend régulièrement la main au navigateur. Une annulation est vérifiée entre les lots de géométrie, les rangées de terrain et les cellules de nature.</p><div class="v048-grid"><article><b>${info.returns.reused}</b><span>Retours sur la scène conservée</span></article><article><b>${last?.yields||0}</b><span>Pauses coopératives du dernier travail</span></article><article><b>${info.retained?v047MiB(info.retained.bytes):'—'}</b><span>Extérieur conservé en mémoire</span></article></div><p>${info.retained?'Un extérieur validé est conservé pendant la visite. Les quêtes, objets et récompenses acquis à l’intérieur ne sont pas restaurés à un état antérieur.':'Aucun extérieur conservé hors de la scène courante. Un seul secteur de retour peut être retenu.'}</p><p>${last?`Dernière préparation : ${last.status} · ${last.units} unités · ${last.yields} pauses · plus longue tranche observée ${last.maxSliceMs} ms.`:'Aucune préparation mesurée dans cette exécution.'}</p><small>Budget visé : 6 ms entre opérations. Une opération géométrique indivisible peut dépasser ce budget ; ce n’est pas une garantie de fréquence d’images. Retenir un extérieur conserve de la mémoire jusqu’au retour ou à un changement de destination.</small>`;
 old.prepend(section);
};
function v048AfterInit(){
 document.title='Fallout : Mistral · v0.48 · Reprises sans rupture';const version=$('menuScreen')?.querySelector('.menu-version');if(version)version.textContent='v0.48 · REPRISES SANS RUPTURE';
 const phase=document.createElement('p');phase.id='v048Phase';phase.hidden=true;phase.setAttribute('role','status');phase.setAttribute('aria-live','polite');$('v046ProgressText').after(phase);
 const credits=document.querySelector('#creditsScreen .credits-card');if(credits){credits.innerHTML='<h2>FALLOUT : MISTRAL</h2><p>0.48.0 · Reprises sans rupture</p><p>Reprise directe de l’archive complète v0.47 fournie. Préparation coopérative, retour conservé depuis les intérieurs et diagnostic des chargements.</p><p>248 implantations et lore de la branche conservés. Prototype de fan non officiel. Le pack géographique complet n’est pas embarqué. Les essais de coutures sont signalés comme synthétiques.</p><button id="btnCreditsClose" class="primary">Fermer</button>';$('btnCreditsClose').onclick=closeCredits;}
 Object.assign(window.__MISTRAL_DEBUG,{v048Info,v048Control:o=>{if('returnBudget'in o)V048.returnLimit=Math.max(0,Math.min(48*1024*1024,+o.returnBudget||0));if('pausePhase'in o)V048.test.pausePhase=o.pausePhase;if('pauseMs'in o)V048.test.pauseMs=Math.min(2000,Math.max(0,+o.pauseMs||0));return {...V048.test};},v046Lab:v046StartLab,v046Campaign:v048LeaveLab,v046Cancel,v042Exit:v042ExitInstance,
  v048ReturnCheck:()=>({retained:!!V048.retained,sameWorld:world===V048.retained?.world,sameState:state===V048.retained?.state,stats:{...V048.returns}}),
  v048RememberScene:()=>{V048.testScene=world;V048.testBank=V046.terrain;return !!world;},
  v048SceneSame:()=>({scene:world===V048.testScene,bank:V046.terrain===V048.testBank}),
  v048Equivalence:async()=>{if(!V046.lab||!world?.v046)throw Error('Banc requis');const ll=v015GeoUnproject(world.id,state.player.pos[0],state.player.pos[2]),plan=v046Plan(...ll),res=new Map();for(const k of[...plan.dem,...plan.keys])res.set(k,await v046LabProvider(k,new AbortController().signal));const signature=s=>MistralIntegrity.hash([s.geoDraws.map(d=>[d.v046GeometryId,d.rings,d.vertices,d.baseY,d.height]),s.geoColliders.map(c=>[c.rings,c.minY,c.maxY]),s.terrain.map(d=>[d.vertices,d.faces]),s.nature.draws.map(d=>[d.v046GeometryId,d.pos,d.scale])]);V047.records.clear();V047.meshes.clear();const a=await V048.legacyPrepare(plan,res,world,new AbortController().signal);V047.records.clear();V047.meshes.clear();const b=await v046Prepare(plan,res,world,new AbortController().signal);return {before:signature(a),after:signature(b),same:signature(a)===signature(b)};}});
}
