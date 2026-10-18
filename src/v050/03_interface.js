/* v0.50 — installed geography and discovered-place travel.
   A shipping report is evidence about the delivery, never a live disk audit. */
const V050 = {version:'0.50.0',auditPromise:null,lastAudit:0};

function v050LocalSummary(data=V047.localData){
  if(location.protocol==='file:')return {title:'Ouvrez le lanceur de l’application',detail:'Les cartes locales se lisent avec LANCER_APP_WINDOWS.bat, LANCER_APP_LINUX.sh ou LANCER_APP_MAC.command.',ready:false};
  if(!data?.vector||!data?.terrain)return {title:'Cartes locales : vérification disponible',detail:'Consultez les fichiers installés et le territoire dans Cartes & territoire.',ready:false};
  const v=data.vector,t=data.terrain,count=(v.pbf||0)+(v.officialEmpty||0);
  const detail=`${count.toLocaleString('fr-FR')} / ${(v.expected||5884).toLocaleString('fr-FR')} coordonnées · ${t.valid||0} / ${t.expected||8} grilles de relief`;
  if(!data.live)return {title:'État de la livraison',detail:detail+' · rapport conservé ; votre disque reste à vérifier.',ready:false};
  return {title:data.complete?'Cartes locales prêtes':'Cartes locales à compléter',detail,ready:!!data.complete};
}

function v050RefreshMenu(){
  const el=$('v050MapSummary');if(!el)return;
  const s=v050LocalSummary();el.dataset.ready=String(s.ready);
  el.replaceChildren();const title=document.createElement('b');title.textContent=s.title;
  const detail=document.createElement('span');detail.textContent=s.detail;el.append(title,detail);
}

v047ReadLocal=async function(){
  if(V050.auditPromise)return V050.auditPromise;
  V050.auditPromise=(async()=>{
    let last;
    for(const url of ['__mistral/local-data','verification/v050/LOCAL_DATA_STATE.json']){
      const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),20000);
      try{
        const response=await fetch(url,{cache:'no-store',signal:ctrl.signal});
        if(!response.ok)throw Error('HTTP '+response.status);
        const data=await response.json();if(!data.vector||!data.terrain)throw Error('Rapport local incompatible');
        V047.localData={...data,live:url.startsWith('__mistral/')};V050.lastAudit=Date.now();return V047.localData;
      }catch(e){last=e;}finally{clearTimeout(timer);}
    }
    V047.localData={complete:false,error:String(last?.message||'Serveur local non disponible')};return null;
  })();
  try{return await V050.auditPromise;}finally{V050.auditPromise=null;v050RefreshMenu();}
};

const v050PreviousPanel=v047Panel;
v047Panel=function(container){
  v050PreviousPanel(container);
  const box=container.querySelector('.v047-integrity');if(!box)return;
  const summary=v050LocalSummary(),data=V047.localData,section=document.createElement('section');section.className='v050-geography';
  section.innerHTML=`<p class="p27-kicker">v0.50 / LES ROUTES RETROUVÉES</p><h2>${escapeHtml(summary.title)}</h2><p>${escapeHtml(summary.detail)}</p>
    <p>Les routes et emprises proviennent des tuiles OpenStreetMap et du cadastre ; les hauteurs du terrain proviennent de grilles IGN. Les bâtiments et décors sont une interprétation du jeu. Les hauteurs de toiture non documentées restent estimées.</p>
    <p>Dans MAP → LIEUX ET VOYAGES, sélectionnez un lieu découvert pour y voyager. Le départ exige un extérieur praticable, à distance du danger ; la destination est vérifiée avant le déplacement.</p>
    ${!data?.live||!data?.complete?'<p class="v050-install-note">Après extraction, lancez l’application avec son lanceur. Les archives géographiques fournies sont préparées sur votre ordinateur. Pour réparer un pack incomplet, utilisez INSTALLER_PACK_LOCAL_WINDOWS.bat ou INSTALLER_PACK_LOCAL_LINUX_MAC.sh.</p>':''}
    <small>Une grille est un échantillonnage du relief. Les points sans mesure restent absents et peuvent empêcher un chargement dans les zones concernées.</small>`;
  box.prepend(section);
};

const v050PreviousAdmin=v035AdminHTML;
v035AdminHTML=function(){const s=v050LocalSummary();return v050PreviousAdmin().replace('Carte réelle : non intégrée',escapeHtml(s.title+' — '+s.detail));};

const v050PreviousMenu=showMenu;
showMenu=function(){const result=v050PreviousMenu();v050RefreshMenu();if($('v050MapSummary')&&Date.now()-V050.lastAudit>30000)v047ReadLocal();return result;};

function v050AfterInit(){
  document.title='Fallout : Mistral · v0.50 · Les routes retrouvées';
  const menu=$('menuScreen'),label=menu?.querySelector('.menu-version');if(label)label.textContent='v0.50 · LES ROUTES RETROUVÉES';
  const nav=menu?.querySelector('.menu-actions');if(nav){
    const button=document.createElement('button');button.id='v050MapStatus';button.textContent='Cartes & territoire';button.onclick=()=>{v047OpenStatus();v047ReadLocal().then(()=>{const content=$('v047StatusContent');if(content&&mode==='STATUS')v047Panel(content);});};
    nav.insertBefore(button,$('btnV035Admin'));
    const summary=document.createElement('p');summary.id='v050MapSummary';summary.setAttribute('aria-live','polite');nav.after(summary);v050RefreshMenu();
  }
  const credits=document.querySelector('#creditsScreen .credits-card');if(credits){
    credits.innerHTML='<h2>FALLOUT : MISTRAL</h2><p>0.50.0 · Les routes retrouvées</p><p>Territoire géographique local, 248 lieux à découvrir, voyage rapide et rencontres persistantes. Campagne, prologue, intérieurs et lore des versions précédentes conservés.</p><p>Sources géographiques : © contributeurs OpenStreetMap — ODbL · Cadastre Etalab / DGFiP — Licence Ouverte 2.0 · IGN RGE ALTI — Licence Ouverte 2.0. La carte utilise les fichiers effectivement installés. Géométrie des bâtiments interprétée, hauteurs non documentées estimées.</p><p>Prototype de fan non officiel. Les anciens rapports inclus décrivent leurs versions respectives.</p><button id="btnCreditsClose" class="primary">Fermer</button>';
    $('btnCreditsClose').onclick=closeCredits;
  }
  if(typeof v050CampaignAfterInit==='function')v050CampaignAfterInit();
  if(typeof v050TravelAfterInit==='function')v050TravelAfterInit();
  Object.assign(window.__MISTRAL_DEBUG,{v050Info:()=>({version:V050.version,lab:V046.lab,localData:V047.localData,summary:v050LocalSummary(),saveKey:SAVE_KEY,settingsKey:SETTINGS_KEY}),v050ReadLocal:v047ReadLocal});
  if(location.protocol!=='file:')v047ReadLocal();
}
