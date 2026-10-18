function v041AfterInit(){
 V027_SUBS.map.pack='PACK LOCAL';
 document.title='Fallout : Mistral · v0.41 · Territoire local';
 const mv=$('menuScreen .menu-version');if(mv)mv.textContent='PRÉ-BÊTA CARTOGRAPHIQUE v0.41.0 · « TERRITOIRE LOCAL »';
 const statusBtn=$('v018MenuStatus');if(statusBtn){statusBtn.textContent='Cartographie réelle · pack local et benchmark';statusBtn.onclick=v041OpenStatus}
 const credits=document.querySelector('#creditsScreen .credits-card');if(credits){credits.innerHTML=`<p class="eyebrow">DOSSIER DE PRODUCTION</p><h2>FALLOUT : MISTRAL</h2><p>La v0.41 distribue toute la couverture vectorielle en 24 archives JWT, ajoute une installation locale atomique et mesure le décodage réel du pack.</p><dl><dt>Version</dt><dd>0.41.0 · Territoire local</dd><dt>Vectoriel cloud</dt><dd>5 884 / 5 884 coordonnées</dd><dt>Distribution locale</dt><dd>24 archives · 367 générales · 5 517 cadastrales</dd><dt>Relief</dt><dd>8 / 8 grilles RGE ALTI disponibles</dd><dt>Attributions</dt><dd>© OpenStreetMap contributors — ODbL · Cadastre Etalab / DGFiP — Licence Ouverte 2.0 · RGE ALTI IGN</dd><dt>Statut</dt><dd>Pré-bêta cartographique ; installation machine cible et traversées humaines toujours requises</dd></dl><p class="credits-note">Prototype de fan non officiel. Le pack compact et le pack territorial lourd restent séparés.</p><button id="btnCreditsClose" class="primary">Fermer</button>`;$('btnCreditsClose').onclick=closeCredits}
 Promise.all([v041RemoteManifest(),v041LocalStatus(),v041BenchmarkStatus()]).then(()=>updateHUD());
 v018OpenStatus=v041OpenStatus;
 Object.assign(window.__MISTRAL_DEBUG,{v041Info:v041PackSummary,v041Remote:v041RemoteManifest,v041Local:v041LocalStatus,v041Benchmark:v041BenchmarkStatus,v041Refresh:v041RefreshPack,v041SetLocal:o=>Object.assign(V041.local,o),v041SetBenchmark:o=>Object.assign(V041.benchmark,o),v041OpenStatus});
}
