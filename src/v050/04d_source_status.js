/* The server's verified local source inventory is distinct from active scene
   geometry, horizontal sample spacing, survey accuracy and acquisition dates. */
const MistralSourceStatus=(()=>{
  const text=(value,limit=1000)=>typeof value==='string'?value.trim().slice(0,limit):'';
  function count(value,optional=false){if(optional&&value===undefined)return null;if(!Number.isSafeInteger(value)||value<0||value>100000000)throw Error('Comptage de sources incompatible');return value;}
  function bbox(value){if(!Array.isArray(value)||value.length!==4||!value.every(Number.isFinite)||value[0]<-90||value[2]>90||value[1]<-180||value[3]>180||value[0]>=value[2]||value[1]>=value[3])throw Error('Emprise de source incompatible');return value.slice();}
  function date(value){const s=text(value,100),day=s.slice(0,10);if(!/^\d{4}-\d{2}-\d{2}(?:T[\d:.+-]+Z?)?$/.test(s)||!Number.isFinite(Date.parse(s))||new Date(day+'T00:00:00Z').toISOString().slice(0,10)!==day)return null;return s;}
  function source(value){if(typeof value==='string')return{name:text(value),date:null,attribution:'',license:''};const s=value&&typeof value==='object'?value:{};return{name:text(s.name)||text(s.source)||text(s.resource)||'Source non renseignée',date:date(s.acquiredAt),attribution:text(s.attribution,2000),license:text(s.license)};}
  function spacing(value,box,width,height){if(typeof value==='number'&&Number.isFinite(value)&&value>0)return{meters:[value,value],derived:false};if(Array.isArray(value)&&value.length===2&&value.every(v=>Number.isFinite(v)&&v>0))return{meters:value.slice(),derived:false};const latitude=(box[0]+box[2])/2*Math.PI/180;return{meters:[(box[3]-box[1])*111320*Math.cos(latitude)/(width-1),(box[2]-box[0])*111320/(height-1)],derived:true};}
  function conversion(value){if(!value||typeof value!=='object')return null;const native=Array.isArray(value.nativePixelSize)&&value.nativePixelSize.length===2&&value.nativePixelSize.every(v=>Number.isFinite(v)&&v>0)?value.nativePixelSize.slice():null;return{resampled:value.resampled===true,resampling:text(value.resampling,100),format:text(value.format,100),crs:text(value.crs,100),nativePixelSize:native};}
  function terrain(value){if(!value||typeof value!=='object')throw Error('Grille de source incompatible');const width=count(value.width),height=count(value.height);if(width<2||height<2||width*height>4194304)throw Error('Dimensions de source incompatibles');const box=bbox(value.bbox),valid=count(value.validSamples),missing=count(value.noDataSamples);if(valid+missing!==width*height)throw Error('Échantillons de source incohérents');const proof=value.provenance||{},src=source(value.source||proof.source||value.sourceResource),d=date(value.acquiredAt)||date(proof.acquiredAt);return{id:text(value.id,160),width,height,bbox:box,validSamples:valid,noDataSamples:missing,source:src.name,sourceResource:text(value.sourceResource,120),verticalDatum:text(value.verticalDatum,300)||text(proof.verticalDatum,300)||'Référentiel vertical non renseigné',date:d,attribution:text(value.attribution,2000)||text(proof.attribution,2000),spacing:spacing(value.resolutionMeters,box,width,height),conversion:conversion(value.conversion||proof.conversion)};}
  function summary(value){
    if(!value||value.ok!==true||!Array.isArray(value.regions)||value.regions.length>64)throw Error('Rapport des sources incompatible');
    const seen=new Set(),regions=value.regions.map(region=>{
      if(!region||typeof region!=='object'||!text(region.id,160)||seen.has(region.id))throw Error('Région de source incompatible');seen.add(region.id);
      const buildings=count(region.buildings),roads=count(region.roads),withoutHeight=count(region.estimatedBuildingHeights,true),unknownZ=count(region.unknownGeometryZ,true);
      if(withoutHeight!==null&&withoutHeight>buildings||unknownZ!==null&&unknownZ>buildings+roads)throw Error('Qualité de source incohérente');
      const coverage=region.coverage||[],grids=region.terrain||[];if(!Array.isArray(coverage)||coverage.length>128||!Array.isArray(grids)||grids.length>32)throw Error('Inventaire de source hors budget');
      return{id:text(region.id,160),source:source(region.source),buildings,roads,withoutHeight,unknownZ,coverage:coverage.map(c=>({bbox:bbox(c.bbox),layer:text(c.layer,200)||'Couche non renseignée',source:text(c.source,1000),date:date(c.acquiredAt)})),terrain:grids.map(terrain)};
    });
    const totalBuildings=count(value.totalBuildings??0),totalRoads=count(value.totalRoads??0);
    if(totalBuildings!==regions.reduce((n,r)=>n+r.buildings,0)||totalRoads!==regions.reduce((n,r)=>n+r.roads,0))throw Error('Totaux des sources incohérents');
    if(value.present===false&&regions.length)throw Error('Présence des sources incohérente');
    return{present:value.present!==false&&regions.length>0,inspectedAt:date(value.inspectedAt),totalBuildings,totalRoads,regions};
  }
  return{summary,bbox,spacing,date};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralSourceStatus;

function v050SourceStatusAfterInit(){
  if(typeof window==='undefined'||window.__mistralSourceStatusInstalled)return;
  window.__mistralSourceStatusInstalled=true;
  const state={data:null,error:null,pending:null,attempted:false};
  const number=value=>value.toLocaleString('fr-FR',{maximumFractionDigits:2});
  const shownDate=value=>value?value.slice(0,10).split('-').reverse().join('/'):'non renseignée';
  const boxText=b=>'sud '+b[0].toFixed(5)+'° · ouest '+b[1].toFixed(5)+'° · nord '+b[2].toFixed(5)+'° · est '+b[3].toFixed(5)+'°';
  function node(tag,content,cls){const el=document.createElement(tag);if(content!==undefined)el.textContent=content;if(cls)el.className=cls;return el;}
  function paragraph(parent,content,cls){const p=node('p',content,cls);parent.appendChild(p);return p;}
  function show(section){
    section.replaceChildren();section.appendChild(node('p','SOURCES COMPLÉMENTAIRES · AUDIT DU DISQUE','p27-kicker'));
    section.appendChild(node('h2','Qualité et couverture des données'));
    paragraph(section,'Ces compteurs décrivent les fichiers complémentaires installés. Ils ne comptent pas les objets visibles à cet instant dans la scène.');
    const status=node('p',undefined,'v050-source-state');status.setAttribute('role','status');status.setAttribute('aria-live','polite');section.appendChild(status);
    const refresh=node('button','Rafraîchir');refresh.type='button';refresh.dataset.sourceRefresh='';refresh.setAttribute('aria-label','Rafraîchir l’audit des sources locales');refresh.disabled=!!state.pending||location.protocol==='file:';refresh.onclick=()=>load(true);section.appendChild(refresh);
    if(location.protocol==='file:'){status.textContent='Audit indisponible dans un fichier ouvert directement. Lancez le serveur local du jeu, puis ouvrez Cartes & territoire.';return;}
    if(state.pending){status.textContent='Lecture et vérification des sources locales… Le jeu reste accessible.';return;}
    if(state.error){status.textContent=state.error;paragraph(section,'Aucun état actualisé des sources complémentaires n’est confirmé. Le pack de base possède son audit distinct ; ce panneau ne modifie ni la partie ni les fichiers.');return;}
    if(!state.data){status.textContent='L’audit des sources complémentaires n’a pas encore été lancé.';return;}
    const data=state.data;
    if(!data.present){status.textContent='Aucune source complémentaire installée selon cet audit.';paragraph(section,'Le pack géographique de base est présenté séparément. L’absence d’ajout ne certifie pas une fidélité 1:1.');return;}
    status.textContent=number(data.totalBuildings)+' bâtiments · '+number(data.totalRoads)+' tronçons de route dans les ajouts vérifiés.';
    paragraph(section,'Couverture locale uniquement : un extrait ne couvre pas toute la ville ni l’ensemble du territoire du jeu. Le pas d’une grille mesure l’espacement des échantillons ; il ne garantit pas la précision du levé.','v050-source-limit');
    if(data.inspectedAt)paragraph(section,'Audit du disque : '+shownDate(data.inspectedAt)+'. Cette date d’inspection n’est pas une date de levé.');
    for(const region of data.regions){
      const article=node('article');article.className='v050-source-region';section.appendChild(article);
      const label=typeof V015_GEO_MACROS!=='undefined'&&V015_GEO_MACROS[region.id]?.name||region.id;
      article.appendChild(node('h3',label+' · '+number(region.buildings)+' bâtiments / '+number(region.roads)+' tronçons'));
      paragraph(article,'Source : '+region.source.name+'. Date déclarée : '+shownDate(region.source.date)+'.');
      if(region.source.attribution)paragraph(article,region.source.attribution,'v050-source-attribution');
      if(region.source.license)paragraph(article,'Licence : '+region.source.license+'.');
      paragraph(article,(region.withoutHeight===null?'Nombre de bâtiments sans hauteur déclarée non renseigné.':number(region.withoutHeight)+' bâtiment(s) sans hauteur déclarée.')+' '+(region.unknownZ===null?'Nombre d’objets avec Z signalé manquant non renseigné.':number(region.unknownZ)+' objet(s) avec Z signalé comme manquant.'));
      const list=node('ul');article.appendChild(list);
      for(const coverage of region.coverage){const line=node('li');list.appendChild(line);line.appendChild(node('b',coverage.layer));paragraph(line,boxText(coverage.bbox));if(coverage.source)paragraph(line,'Source : '+coverage.source+'. Date d’extraction déclarée : '+shownDate(coverage.date)+'.');}
      if(!region.coverage.length)paragraph(article,'Emprise des objets vectoriels non renseignée : aucune couverture exhaustive n’est déduite de leur présence.');
      for(const grid of region.terrain){
        const tile=node('section');tile.className='v050-source-terrain';article.appendChild(tile);
        tile.appendChild(node('h4',grid.source));
        paragraph(tile,number(grid.width)+' × '+number(grid.height)+' échantillons · '+number(grid.validSamples)+' altitudes présentes · '+number(grid.noDataSamples)+' valeurs NoData conservées.');
        paragraph(tile,'Pas horizontal '+(grid.spacing.derived?'estimé à partir de l’emprise':'déclaré')+' : environ '+grid.spacing.meters.map(v=>number(v)).join(' × ')+' m. Ce pas n’est pas une précision altimétrique.');
        paragraph(tile,'Emprise de cette grille : '+boxText(grid.bbox)+'.');
        paragraph(tile,'Référentiel vertical : '+grid.verticalDatum+'. Date déclarée pour la source : '+shownDate(grid.date)+'.');
        if(grid.conversion){const c=grid.conversion;paragraph(tile,c.resampled?'Grille rééchantillonnée'+(c.resampling?' par '+c.resampling:'')+' depuis la source'+(c.format?' '+c.format:'')+'.':'Conversion de la source documentée ; aucun rééchantillonnage déclaré.');if(c.nativePixelSize){const unit=c.crs==='EPSG:4326'?'°':c.crs==='EPSG:2154'?' m':' unités de la source';paragraph(tile,'Taille native des pixels déclarée : '+c.nativePixelSize.map(v=>number(v)).join(' × ')+unit+(c.crs?' ('+c.crs+')':'')+'. Elle est distincte de la précision du relevé.');}}
        if(grid.attribution)paragraph(tile,grid.attribution,'v050-source-attribution');
      }
      if(!region.terrain.length)paragraph(article,'Aucune grille complémentaire dans ce secteur. Le relief du pack de base reste distinct.');
    }
    paragraph(section,'Une date d’extraction ou de téléchargement ne prouve pas la date de levé de chaque bâtiment ou route. Les altitudes manquantes et les hauteurs estimées ne deviennent pas des mesures par interpolation.','v050-source-limit');
  }
  function refresh(){for(const section of document.querySelectorAll('[data-v050-source-status]'))show(section);}
  function load(force=false){
    if(state.pending)return state.pending;
    if(location.protocol==='file:'){state.attempted=true;refresh();return Promise.resolve(null);}
    if(!force&&state.attempted)return Promise.resolve(state.data);
    state.attempted=true;state.error=null;
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),12000);
    state.pending=Promise.resolve().then(async()=>{
      try{
        const response=await fetch('/__mistral/world-sources',{method:'GET',cache:'no-store',credentials:'same-origin',redirect:'error',signal:controller.signal});
        if(response.status===404)throw Error('Le serveur local ne fournit pas ce diagnostic. Relancez la version actuelle du serveur, puis rafraîchissez.');
        if(!response.ok){const json=response.headers.get('Content-Type')?.includes('json');throw Error(response.status===503?(json?'Le serveur n’a pas pu valider les sources locales. Vérifiez les fichiers puis rafraîchissez.':'Le serveur local est inaccessible ou ne fournit pas de sources vérifiées. Relancez le serveur puis rafraîchissez.'):'Audit des sources locales indisponible. Relancez le serveur puis rafraîchissez.');}
        const payload=await response.text();if(payload.length>2097152)throw Error('Rapport des sources trop volumineux. Aucun compteur actualisé confirmé.');
        state.data=MistralSourceStatus.summary(JSON.parse(payload));return state.data;
      }catch(error){state.error=error?.name==='AbortError'?'Le serveur local n’a pas répondu à temps. La partie reste accessible ; vous pouvez rafraîchir plus tard.':error instanceof TypeError?'Le serveur local est inaccessible. Lancez le serveur du jeu puis rafraîchissez.':error instanceof SyntaxError?'Le diagnostic local est illisible. Relancez la version actuelle du serveur puis rafraîchissez.':String(error?.message||'Audit des sources locales indisponible.');return null;}
      finally{clearTimeout(timer);state.pending=null;refresh();}
    });
    refresh();return state.pending;
  }
  const style=node('style');style.textContent='.v050-source-status{border:1px solid #84966e;background:#102017;padding:18px;margin:18px 0}.v050-source-status p,.v050-source-status li{line-height:1.6;overflow-wrap:anywhere}.v050-source-status button{padding:10px 16px;min-height:44px;margin:0 0 10px;color:#e5e8c9;background:#233826;border:1px solid #859966}.v050-source-status button:disabled{opacity:.65}.v050-source-state{font-weight:700}.v050-source-limit{border-left:3px solid #d6bf63;padding-left:12px}.v050-source-region{border-top:1px solid #526747;margin-top:18px;padding-top:12px}.v050-source-status ul{padding-left:22px}.v050-source-status li p{margin:4px 0 10px}.v050-source-terrain{padding:12px;background:#07150f;margin:12px 0}.v050-source-attribution{font-size:12px;color:#b8c8ac}';document.head.appendChild(style);
  const panelBase=v047Panel;
  v047Panel=function(container){panelBase(container);const box=container.querySelector('.v047-integrity');if(!box)return;const section=node('section');section.className='v050-source-status';section.dataset.v050SourceStatus='';section.setAttribute('aria-label','Qualité et couverture des sources locales complémentaires');box.prepend(section);show(section);if(!state.attempted)load();};
  if(window.__MISTRAL_DEBUG)Object.assign(window.__MISTRAL_DEBUG,{v050SourceStatus:()=>({pending:!!state.pending,error:state.error,data:state.data?JSON.parse(JSON.stringify(state.data)):null}),v050RefreshSourceStatus:()=>load(true)});
}
