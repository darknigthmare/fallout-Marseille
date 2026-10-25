from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
import json,hashlib,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2];O=R/'verification/v050/legacy';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.50.html').read_text();tests=[];errors=[]
def ck(n,ok,d=None):
 tests.append({'name':n,'ok':bool(ok),'detail':d});print(('OK ' if ok else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.set_default_timeout(15000);p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 def c(n,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
 try:
  ck('Version v0.47 exécutée',c('v047Info')['version']=='0.47.0')
  ck('Laboratoire synthétique chargé',c('v046Lab'))
  c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False,'cooldown':0})
  ll=c('v046LL');origin=c('v046LabOrigin');signature=c('v046Signature');bank=c('v047TerrainIdentity');height=c('v046Height',*ll);position=c('v047Info')['pos'];commits=c('v046Info')['commits']
  c('v047Control',{'terrainOffset':450,'failPrepare':True});c('v046ClearCache')
  ck('Échec après lecture du nouveau relief',c('v046Load',*ll) is False)
  ck('Échec : banque altimétrique publiée inchangée',c('v047TerrainIdentity')==bank)
  ck('Échec : altitude sous le joueur inchangée',c('v046Height',*ll)==height)
  ck('Échec : bâtiments et nature inchangés',c('v046Signature')==signature)
  ck('Échec : aucune publication partielle',c('v046Info')['commits']==commits)
  c('v046Cancel');c('v047Control',{'failPrepare':False,'delayPrepare':300});c('v046ClearCache')
  p.evaluate('(ll)=>{window.__cancelDuringPrepare=__MISTRAL_DEBUG.v046Load(...ll)}',ll);p.wait_for_function('__MISTRAL_DEBUG.v047Info().phase==="preparing"');c('v046Cancel');p.wait_for_timeout(420)
  ck('Annulation pendant construction : banque intacte',c('v047TerrainIdentity')==bank)
  ck('Annulation pendant construction : géométrie intacte',c('v046Signature')==signature)
  ck('Annulation pendant construction : position intacte',c('v047Info')['pos']==position)
  c('v047Control',{'terrainOffset':0,'delayPrepare':0,'auto':False});c('v046ClearCache');ck('Réessai après annulation',c('v046Load',*ll))
  c('v047ProbeRemember');c('v046Load',*ll);reuse=c('v047ProbeReuse');ck('Tuiles réutilisées par référence, pas réinstanciées',reuse['sameRecords']==c('v047Info')['tiles'],reuse)
  terrain=c('v047Info')['stats'];ck('Maillages terrain réutilisés',terrain['reusedTerrain']>0,terrain)
  # A warm load is requested before the 170m safety margin is exhausted.
  c('v047Control',{'auto':False,'cooldown':0});c('v046Control',{'delay':45,'fail':None});c('v046ClearCache');c('v046Move',72,0);base=c('v047Info');ck('Préchargement déclenché dans le secteur valide',p.evaluate('()=>{__MISTRAL_DEBUG.v047Control({auto:true});return __MISTRAL_DEBUG.v047Predict()}'))
  p.wait_for_timeout(35);s=c('v047Info');ck('Préchargement non bloquant',s['anticipating'] and not s['loading'] and not p.locator('#v046Loading').is_visible(),s)
  pos0=s['pos'];c('v046Move',4,0);pos1=c('v047Info')['pos'];ck('Le joueur peut marcher pendant la préparation',pos1[0]>pos0[0]+3.9)
  # Reaching unsafe territory promotes, rather than duplicates, the request.
  c('v046Move',110,0);hold=c('v047Info');ck('Au seuil de sécurité, attente visible',hold['loading'] and p.locator('#v046Loading').is_visible())
  ck('Le saut vers une zone non prête est refusé',hold['pos']==pos1)
  p.wait_for_function('__MISTRAL_DEBUG.v047Info().phase==="ready" && !__MISTRAL_DEBUG.v047Info().loading');s=c('v047Info')
  ck('La même anticipation est publiée une seule fois',s['stats']['warmStarted']==base['stats']['warmStarted']+1 and s['stats']['warmCommitted']==base['stats']['warmCommitted']+1,s['stats'])
  ck('Reprise sans téléportation',s['pos']==pos1)
  warm_count=s['stats']['warmStarted'];p.wait_for_timeout(350);ck('Joueur arrêté : aucun cycle anticipatif oscillant',c('v047Info')['stats']['warmStarted']==warm_count)
  ck('Scène conservée après publication',c('v046Signature')['scene']==signature['scene'])
  ck('Empreintes des bâtiments identiques',c('v046Signature')['buildings']==signature['buildings'])
  c('v046Move',110,0);ck('La marche reprend dans le secteur préparé',c('v047Info')['pos'][0]>pos1[0]+109)
  # A fast reversal before completion cannot publish the sector behind the player.
  c('v046Control',{'delay':30,'fail':None});c('v046ClearCache');c('v047Control',{'auto':False,'cooldown':0});c('v046Move',64,0);oldanchor=c('v047Info')['anchor'];oldbank=c('v047TerrainIdentity');ck('Seconde anticipation demandée',p.evaluate('()=>{__MISTRAL_DEBUG.v047Control({auto:true});return __MISTRAL_DEBUG.v047Predict()}'))
  c('v046Move',-190,0);p.wait_for_function('!__MISTRAL_DEBUG.v047Info().anticipating && !__MISTRAL_DEBUG.v047Info().loading');s=c('v047Info')
  ck('Demi-tour : ancien secteur validé conservé',s['anchor']==oldanchor and c('v047TerrainIdentity')==oldbank,s)
  ck('Demi-tour : préchargement périmé rejeté',s['stats']['stale']>=1,s['stats'])
  c('v046Cancel');c('v046Control',{'delay':0,'fail':None});c('v047Control',{'auto':False})
  # Bounded cache under repeated exploration. These remain synthetic inputs.
  for i in range(12):
   ok=c('v046Load',43.29,5.43+i*.014)
   ck('Chargement de stress '+str(i+1),ok)
  s=c('v047Info');ck('Cache brut borné après exploration',s['resources']['entries']<=128 and s['resources']['bytes']<=s['resources']['budgetBytes'],s['resources'])
  ck('Géométrie et terrain bornés',s['geometry']['entries']<=96 and s['terrainMeshes']['entries']<=64,{'geometry':s['geometry'],'terrainMeshes':s['terrainMeshes']})
  ck('Anciennes données non actives évincées',s['resources']['evictions']>0,s['resources'])
  ck('Retour au secteur initial',c('v046Load',*ll))
  ck('Bâtiments stables après éviction et retour',c('v046Signature')['buildings']==signature['buildings'])
  # Cancelling from the Pip-Boy must not resume combat or close the inventory.
  c('v027Open','data','france');c('v046Control',{'delay':0,'fail':'all'});c('v046ClearCache');c('v046Load',*ll)
  ck('Échec : bouton de réessai accessible au clavier',p.evaluate('document.activeElement.id')=='v046Retry')
  c('v046Cancel');ck('Annuler respecte le Pip-Boy ouvert',p.locator('#pipboy').is_visible())
  c('closePip');c('v046Control',{'delay':0,'fail':None})
  # Resource response guards use the production reader.
  ck('Lecture bornée valide',c('v047BodyTest',{'size':32,'max':100})=={'ok':True,'bytes':32})
  ck('Corps trop volumineux refusé',c('v047BodyTest',{'size':200,'max':100})['ok'] is False)
  ck('Signal déjà annulé respecté',c('v047BodyTest',{'size':32,'abort':True})['ok'] is False)
  c('v047OpenStatus');txt=p.locator('#v047StatusContent').inner_text();ck('Diagnostic réel du streaming affiché','LE TERRITOIRE EN AVANCE' in txt and 'réutilis' in txt,txt[:1200]);ck('Le banc ne prétend pas être Marseille','BANC SYNTHÉTIQUE ACTIF' in txt)
  ck('Aucune exception JavaScript',not errors,errors)
 except Exception:ck('Scénario complet v0.47',False,traceback.format_exc())
 b.close()
r={'version':'0.47.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(t['ok'] for t in tests),'failed':sum(not t['ok'] for t in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'HTML réel exécuté dans Chromium ; préchargement, échecs et stress utilisent le banc synthétique explicitement signalé, pas des quartiers réels.'};(O/'QA_STREAMING_NEW.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(r['failed'] or errors))
