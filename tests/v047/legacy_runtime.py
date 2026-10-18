from pathlib import Path
from playwright.sync_api import sync_playwright
import json,time,hashlib,traceback
R=Path(__file__).resolve().parents[2];O=R/'verification/v047';O.mkdir(exist_ok=True)
HTML=(R/'JOUER_FALLOUT_MISTRAL_v0.47.html').read_text();tests=[];errors=[]
def ck(name,ok,detail=None):
 tests.append({'name':name,'ok':bool(ok),'detail':detail});print(('OK ' if ok else 'FAIL ')+name,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.set_default_timeout(10000);p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content(HTML,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__memoryStore=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__memoryStore.get(k)||null,setItem:(k,v)=>__memoryStore.set(k,String(v)),removeItem:k=>__memoryStore.delete(k)}})")
 def c(name,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+name+'(...a)',list(args))
 try:
  ck('Démarrage v0.46',c('v046Info')['version']=='0.46.0')
  ck('Banc se charge par la barrière réelle',c('v046Lab') is True)
  c('setRenderPaused',True);c('v022Freeze',True)
  info=c('v046Info');start=c('v046Signature');pos=info['pos'];ll=c('v046LL');origin=c('v046LabOrigin')
  ck('Cinq empreintes cadastrales de test chargées',len(start['buildings'])==5)
  ck('Des arbres sont créés dans le masque forestier',info['nature']>0,info['nature'])
  ck('Une seule projection pour les huit régions',len({json.dumps(c('v046Project',m,43.29,5.43)) for m in ['geo_marseille','geo_huveaune','geo_garlaban','geo_laciotat','geo_calanques','geo_etoile','geo_saintebaume','geo_frioul']})==1)
  ck('Cour du bâtiment reste traversable',c('v046Collide',origin[0]+50,origin[2]-68) is False)
  ck('Mur du même bâtiment garde sa collision',c('v046Collide',origin[0]+25,origin[2]-68) is True)
  # Three complete movements through the actual player movement function.
  for run in range(3):
   for i in range(65): c('v046Move',2,0)
   far=c('v046Signature');ck('Région traverse sans reconstruire — aller '+str(run+1),far['scene']==start['scene'] and far['region']=='geo_huveaune',{'scene':far['scene'],'region':far['region']})
   ck('Bâtiments identiques après franchissement '+str(run+1),far['buildings']==start['buildings'])
   for i in range(65):c('v046Move',-2,0)
   back=c('v046Signature');now=c('v046Info')
   ck('Retour conserve routes et forêt '+str(run+1),back['roads']==start['roads'] and back['nature']==start['nature'])
   ck('Position retour conservée '+str(run+1),max(abs(a-b) for a,b in zip(now['pos'],pos))<.03,{'before':pos,'after':now['pos']})
  # Actual overlay and failure contract, not a painted mock screen.
  saved=c('v046Signature');savedpos=c('v046Info')['pos'];commits=c('v046Info')['commits']
  c('v046Control',{'delay':18,'fail':'all'});c('v046ClearCache')
  p.evaluate('(ll)=>{window.__loadingTest=__MISTRAL_DEBUG.v046Load(...ll)}',ll);p.wait_for_timeout(35)
  ck('Écran de chargement réellement visible',p.locator('#v046Loading').is_visible())
  c('v046Move',5,0);ck('Déplacement bloqué pendant chargement',c('v046Info')['pos']==savedpos)
  p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="failed"')
  ck('Ressources manquantes interdisent la publication',c('v046Info')['commits']==commits and c('v046Signature')==saved)
  ck('Réessayer et annuler restent accessibles',p.locator('#v046Retry').is_visible() and p.locator('#v046Cancel').is_visible())
  p.screenshot(path=str(O/'loading_failed.png'))
  p.click('#v046Cancel');ck('Annulation reprend la scène intacte',not p.locator('#v046Loading').is_visible() and c('v046Signature')==saved and c('v046Info')['pos']==savedpos)
  c('v046Control',{'delay':0,'fail':None});ck('Réessai réussi',c('v046Load',*ll) is True)
  reread=c('v046Signature');ck('Rechargement ne déplace pas les bâtiments',reread['buildings']==saved['buildings'] and reread['roads']==saved['roads'])
  # Cancel while request in-flight: callbacks must never publish.
  commits=c('v046Info')['commits'];c('v046ClearCache');c('v046Control',{'delay':70,'fail':None})
  p.evaluate('(ll)=>{window.__late=__MISTRAL_DEBUG.v046Load(...ll)}',ll);p.wait_for_timeout(15);c('v046Cancel');p.wait_for_timeout(400)
  ck('Une réponse tardive après annulation ne change rien',c('v046Info')['commits']==commits and c('v046Info')['pos']==savedpos)
  c('v046Control',{'delay':0,'fail':None})
  # Quickbar identity: advance observed clock for repeated v020 updates without changing weapon.
  c('v046Frame');p.wait_for_timeout(240);c('v046Frame')
  hud=p.evaluate('''() => {const bar=document.getElementById('v020Quickbar'),hud=document.getElementById('weaponHud');const initial=[...bar.children];let changes=0;const sizes=[],hs=[];const real=performance.now.bind(performance);let n=0;Object.defineProperty(performance,'now',{configurable:true,value:()=>real()+n*240});for(n=0;n<600;n++){__MISTRAL_DEBUG.v046Frame();document.getElementById('ammoClip').textContent=String(n%3?1:999);document.getElementById('ammoReserve').textContent=String(n%2?99999:0);const rr=document.getElementById('v018ReloadProgress');if(rr){rr.hidden=n%2===0;rr.textContent='RECHARGEMENT · '+n+' %';}if(initial.some((x,i)=>bar.children[i]!==x))changes++;const a=bar.getBoundingClientRect(),b=hud.getBoundingClientRect();sizes.push([a.width,a.height]);hs.push([b.width,b.height]);}Object.defineProperty(performance,'now',{configurable:true,value:real});return {changes,children:initial.length,bar:sizes,hud:hs};}''')
  ck('Raccourcis non reconstruits sur 600 mises à jour',hud['changes']==0 and hud['children']>=6,{'rebuilds':hud['changes'],'children':hud['children']})
  ck('Dimensions des raccourcis constantes',len({tuple(x) for x in hud['bar']})==1,hud['bar'][0])
  ck('HUD arme constant sur 600 valeurs',len({tuple(x) for x in hud['hud']})==1 and hud['hud'][0][0]>0,hud['hud'][0])
  p.set_viewport_size({'width':390,'height':844});c('v046Frame');a=p.locator('#weaponHud').bounding_box();ck('HUD étroit défini sans pompage',abs(a['width']-210)<.5 and abs(a['height']-104)<.5,a);p.set_viewport_size({'width':1440,'height':900})
  c('v046SetTime',12);c('v046SetView',3.14159,0);c('v046Render');sun1=c('v046Sky');c('v046SetView',0,0);c('v046Render');sun2=c('v046Sky')
  ck('Ciel : azimut monde indépendant de la caméra',sun1['worldAzimuth']==sun2['worldAzimuth'])
  ck('Ciel : projection change avec le regard',sun1['screen']!=sun2['screen'],{'facing':sun1['screen'],'away':sun2['screen']})
  lore=c('v046Lore');ck('Neuf factions et huit dossiers réintégrés',len(lore['factions'])==9 and len(lore['quests'])==8)
  ck('Objectif non accompli ne donne pas de récompense',c('v046Accept','rondpoint') and c('v046Claim','rondpoint') is False)
  c('v046TestQuestClear','rondpoint');caps=c('v046Info')['lore'];ck('Récompense une seule fois',c('v046Claim','rondpoint') is True and c('v046Claim','rondpoint') is False)
  ck('Progression COCHONNET persistante',c('v046PlayBoule','pointer')['played']==1 and c('v046PlayBoule','tirer')['played']==2)
  ck('Le laboratoire ne sauvegarde jamais la campagne',c('v046Save') is False)
  c('v027Open','data','france');txt=p.locator('#pipContent').inner_text();ck('Dossiers de lore accessibles dans le vrai Pip-Boy','Bastille du Midi' in txt and 'COCHONNET' in txt)
  p.screenshot(path=str(O/'lore_pipboy.png'));c('closePip')
  # Legacy saves: translate once from the old region origin, including door returns.
  old=c('v020State');old.pop('v046',None);old['player']['zone']='geo_huveaune';old['player']['pos']=c('v046OldProject','geo_huveaune',43.29,5.56);old['player']['pos'][1]=51;old['player']['caps']=321;old['v042']['returnPoint']={'macro':'geo_huveaune','pos':old['player']['pos'][:],'yaw':.5};migrated=c('v046RestoreOld',old);expected=c('v046Project','geo_huveaune',43.29,5.56)
  ck('Ancienne sauvegarde convertie au repère commun',abs(migrated['player']['pos'][0]-expected[0])<.01 and abs(migrated['player']['pos'][2]-expected[2])<.01)
  ck('Portefeuille conservé pendant migration',migrated['player']['caps']==321)
  ck('Retour de porte converti avec la sauvegarde',migrated['v042']['returnPoint']['pos']==migrated['player']['pos'])
  again=c('v046RestoreOld',migrated);ck('Migration idempotente : pas de second déplacement',again['player']['pos']==migrated['player']['pos'])
  # Interior is explicitly instanced, unlike a macro-region boundary.
  site=next(q for q in c('v042Catalog') if q['kind']=='shelter')
  returnpos=c('v046Info')['pos'];beforedoor=c('v046Signature');ck('Abri existant toujours ouvrable',c('v042Enter',site['id']) is True)
  ck('Intérieur hérité conservé',c('v042World')['geo'] is False and len(c('v042World')['allSubzones'])>=6)
  ck('Sortie de l’abri acceptée',c('v042Exit') is True);p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="ready" && !__MISTRAL_DEBUG.v046Info().busy')
  ck('Retour au même point extérieur',max(abs(a-b) for a,b in zip(c('v046Info')['pos'],returnpos))<.04)
  ck('Bâtiments identiques après sortie d’instance',c('v046Signature')['buildings']==beforedoor['buildings'])
  ck('Aucune exception JS',not errors,errors)
 except Exception:ck('Exécution du scénario',False,traceback.format_exc())
 b.close()
report={'version':'0.46.0','html_sha256':hashlib.sha256(HTML.encode()).hexdigest(),'passed':sum(t['ok'] for t in tests),'failed':sum(not t['ok'] for t in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'Chromium, HTML réel via set_content. Données de coutures volontairement synthétiques. Aucun téléchargement géographique ni stockage IndexedDB natif revendiqué.'}
(O/'QA_RUNTIME.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['passed','failed','total','errors']}));sys_exit=report['failed']>0
raise SystemExit(sys_exit)
