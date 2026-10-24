/* Installed municipal coverage and architectural interpretation are reported
   separately. Displayed totals are audited files, never the active draw count. */
function v051CityPanelAfterInit(){
 if(typeof window==='undefined'||window.__mistralCityPanelInstalled)return;
 window.__mistralCityPanelInstalled=true;
 const status={data:null,error:null,pending:null,attempted:false};
 const number=n=>n.toLocaleString('fr-FR');
 const count=n=>Number.isSafeInteger(n)&&n>=0&&n<=10000000;
 function parse(raw){
  if(!raw||raw.ok!==true||typeof raw.present!=='boolean')throw Error('Inventaire municipal incompatible.');
  if(!raw.present)return{present:false};
  const m=raw.municipality,b=m?.bbox;
  if(m?.code!=='13055'||!Array.isArray(b)||b.length!==4||!b.every(Number.isFinite)||b[0]>=b[2]||b[1]>=b[3]||b[0]<-90||b[2]>90||b[1]<-180||b[3]>180)throw Error('Limite municipale incompatible.');
  if(!count(raw.totalBuildings)||!count(raw.totalRoads)||!count(raw.tileCount))throw Error('Comptage municipal incompatible.');
  return{present:true,municipality:{name:'Marseille',code:'13055',bbox:b.slice()},totalBuildings:raw.totalBuildings,totalRoads:raw.totalRoads,tileCount:raw.tileCount,coverageComplete:raw.coverage?.complete===true,terrainPresent:raw.terrain?.present===true};
 }
 function node(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;}
 function paragraph(parent,text){parent.appendChild(node('p',text));}
 function show(section){
  section.replaceChildren();section.appendChild(node('h2','Marseille : territoire et architecture'));
  const stateLine=node('p');stateLine.setAttribute('role','status');stateLine.setAttribute('aria-live','polite');section.appendChild(stateLine);
  const refresh=node('button','Vérifier les données de Marseille');refresh.type='button';refresh.dataset.cityRefresh='';refresh.disabled=!!status.pending||location.protocol==='file:';refresh.onclick=()=>load(true);section.appendChild(refresh);
  if(location.protocol==='file:'){stateLine.textContent='Lancez le serveur local du jeu pour lire les cartes municipales.';return;}
  if(status.pending){stateLine.textContent='Vérification des fichiers de Marseille… La partie reste accessible.';return;}
  if(status.error){stateLine.textContent=status.error;paragraph(section,'Aucun inventaire municipal actualisé n’est confirmé. Les sources du pack de base et les ajouts d’Aubagne ont leurs audits séparés.');return;}
  const d=status.data;
  if(!d){stateLine.textContent='Les fichiers municipaux n’ont pas encore été vérifiés.';return;}
  if(!d.present){stateLine.textContent='Aucun complément municipal de Marseille installé selon cet audit.';return;}
  stateLine.textContent=number(d.totalBuildings)+' objets bâtiment · '+number(d.totalRoads)+' tronçons routiers dans '+number(d.tileCount)+' secteurs vérifiés.';
  paragraph(section,d.coverageComplete?'Les requêtes vectorielles couvrent la limite administrative officielle de Marseille (13055). Les objets renvoyés sont conservés entiers, y compris les objets de bordure que l’index spatial du fournisseur peut renvoyer hors de cette limite.':'La présence de ces fichiers ne confirme pas encore une acquisition vectorielle de toute la commune.');
  paragraph(section,d.terrainPresent?'Un relief municipal supplémentaire est installé. Sa résolution et les absences de mesure restent celles de ses sources.':'Aucun relief municipal supplémentaire n’est confirmé dans cet inventaire.');
  paragraph(section,'Les coordonnées, contours, cours et hauteurs disponibles viennent des relevés. Leurs précisions et dates peuvent varier ; une échelle d’un mètre dans le jeu ne certifie pas chaque détail architectural.');
  paragraph(section,'Les façades et intérieurs sont complétés de façon cohérente et déterministe. Seules les parties accompagnées d’un document attribué sont présentées comme documentées. Les autres fenêtres, portes, pièces et aménagements sont inventés.');
  const architecture=window.__MISTRAL_DEBUG?.v052ArchitectureInfo?.();
  if(architecture?.error)paragraph(section,'Les annotations architecturales locales sont invalides et ne sont pas appliquées. Vérifiez leur installation.');
  else if(architecture?.loaded)paragraph(section,number(architecture.siteLabels)+' associations de bâtiments à un site identifié · '+number(architecture.facadeDocuments)+' plans de façade · '+number(architecture.interiorDocuments)+' plans d’intérieur attribués installés. L’appartenance à un site ne décrit pas ses fenêtres ou ses pièces.');
  if(architecture?.rejected?.length)paragraph(section,number(architecture.rejected.length)+' annotation(s) ne correspondent plus à la géométrie chargée et sont écartées.');
  paragraph(section,'Approchez-vous d’une porte accessible et utilisez Interagir pour entrer. Les étages et le retour extérieur appartiennent au même bâtiment ; les intérieurs historiques de la campagne gardent leurs accès.');
 }
 function refresh(){for(const section of document.querySelectorAll('[data-city-source-status]'))show(section);}
 window.addEventListener('mistral-architecture-ready',refresh);
 function load(force=false){
  if(status.pending)return status.pending;
  if(!force&&status.attempted)return Promise.resolve(status.data);
  status.attempted=true;status.error=null;
  const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),180000);
  status.pending=Promise.resolve().then(async()=>{
   try{
    const response=await fetch('/__mistral/city-sources',{cache:'no-store',credentials:'same-origin',redirect:'error',signal:ctrl.signal});
    if(!response.ok)throw Error(response.status===404?'Le serveur ne fournit pas encore l’audit municipal. Relancez le serveur actuel.':'Les fichiers municipaux n’ont pas pu être vérifiés. Consultez leur installation puis réessayez.');
    const body=await response.text();if(body.length>2097152)throw Error('Inventaire municipal trop volumineux.');
    status.data=parse(JSON.parse(body));return status.data;
   }catch(error){status.error=error?.name==='AbortError'?'La vérification municipale a dépassé le délai. Vous pouvez réessayer.':error instanceof SyntaxError?'Le diagnostic municipal est illisible. Relancez le serveur actuel.':String(error?.message||'Audit municipal indisponible.').slice(0,600);return null;}
   finally{clearTimeout(timer);status.pending=null;refresh();}
  });refresh();return status.pending;
 }
 const previous=v047Panel;
 v047Panel=function(container){previous(container);const box=container.querySelector('.v047-integrity');if(!box)return;const section=node('section');section.className='v051-city-status';section.dataset.citySourceStatus='';section.setAttribute('aria-label','Couverture municipale et architecture de Marseille');box.prepend(section);show(section);if(!status.attempted)load();};
 Object.assign(window.__MISTRAL_DEBUG,{v051ReadCityStatus:()=>load(true),v051CityPanel:()=>({pending:!!status.pending,error:status.error,data:status.data?JSON.parse(JSON.stringify(status.data)):null})});
}
