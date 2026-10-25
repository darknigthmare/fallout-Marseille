from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import json,hashlib,traceback
R=Path(__file__).resolve().parents[2];O=R/'verification/v049';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.49.html').read_text();tests=[];errors=[]
def ck(n,ok,d=None):
 tests.append({'name':n,'ok':bool(ok),'detail':d});print(('OK ' if ok else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.set_default_timeout(25000);p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__store.get(k)||null,setItem:(k,v)=>__store.set(k,String(v)),removeItem:k=>__store.delete(k)}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  ck('v0.48 exécutée',c('v048Info')['version']=='0.48.0')
  ck('Banc synthétique chargé',c('v046Lab') is True);c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False})
  ll=c('v046LL');signature=c('v046Signature');bank=c('v047TerrainIdentity');pos=c('v047Info')['pos'];commits=c('v046Info')['commits']
  eq=c('v048Equivalence');ck('Même géométrie que le constructeur v0.47',eq['same'],eq)
  info=c('v048Info');ck('La préparation a rendu la main',info['lastJob']['yields']>20,info['lastJob'])
  # Cancel during terrain and nature loops, through the production overlay button.
  for phase in ['batiments','collisions','relief','nature','publication']:
   c('v048Control',{'pausePhase':phase,'pauseMs':350});c('v046ClearCache')
   p.evaluate('(ll)=>{window.__task=__MISTRAL_DEBUG.v046Load(...ll)}',ll)
   p.wait_for_function('(phase)=>__MISTRAL_DEBUG.v048Info().preparation?.phase===phase',arg=phase)
   ck('Étape interruptible '+phase,p.locator('#v046Loading').is_visible())
   text=p.locator('#v048Phase').inner_text();ck('Étape réellement affichée '+phase,bool(text),text)
   p.click('#v046Cancel');p.wait_for_timeout(100)
   ck('Annulation conserve la scène '+phase,c('v046Signature')==signature and c('v047TerrainIdentity')==bank)
   ck('Annulation conserve position '+phase,c('v047Info')['pos']==pos)
  c('v048Control',{'pausePhase':None,'pauseMs':0});ck('Réessai après cinq annulations',c('v046Load',*ll))
  ck('Réessai conserve routes et cours',c('v046Signature')['buildings']==signature['buildings'] and c('v046Signature')['roads']==signature['roads'])
  # Keep exactly the exterior object while visiting an actual territorial interior.
  site=next(n for n in c('v042Catalog') if n['visitable']);c('v046SetView',.67,-.14)
  c('v048RememberScene');before=c('v047Info');start=c('v046Signature');wallet=json.loads(c('v023SnapshotState'))['player']['caps']
  ck('Entrée intérieure',c('v042Enter',site['id']) is True);p.wait_for_timeout(250)
  keep=c('v048Info')['retained'];ck('Une seule scène retenue',keep is not None and keep['site']==site['id'],keep)
  ck('Budget mémoire de retour respecté',keep['bytes']<=c('v048Info')['returnBudget'],keep)
  # Genuine inner walls/doors via live collider checks.
  for x,z,wallz in [(-12,24,18),(12,4,10),(-12,-16,-10),(12,-38,-30)]:
   ck(f'Porte x{x} z{z} traversable',c('v046Collide',x,z) is False)
   ck(f'Cloison voisine x{x} z{wallz} solide',c('v046Collide',x,wallz) is True)
  inner=json.loads(c('v023SnapshotState'));ck('Arrivée orientée vers intérieur',abs(inner['player']['yaw'])<.001,inner['player']['yaw'])
  # Earn a real one-shot quest reward in the instance; must survive return.
  q=c('v046Lore')['quests'][0];c('v046Accept',q['id']);c('v046TestQuestClear',q['id']);ck('Récompense de quête acquise',c('v046Claim',q['id']) is True)
  earned=json.loads(c('v023SnapshotState'))['player']['caps'];ck('Le portefeuille a progressé',earned>wallet,{ 'before':wallet,'after':earned})
  # All requests would now fail. Return must not touch the network/gate.
  c('v046Control',{'fail':'all'});c('v046ClearCache');jobs=len(c('v048Info')['jobs']);publications=c('v046Info')['commits']
  ck('Sortie fonctionne même sans réseau',c('v042Exit') is True);p.wait_for_timeout(300)
  ck('Même objet monde et banque de relief',c('v048SceneSame')=={'scene':True,'bank':True},c('v048SceneSame'))
  ck('Aucun chargement de retour',len(c('v048Info')['jobs'])==jobs and c('v046Info')['commits']==publications)
  ck('Même empreinte visible au retour',c('v046Signature')==start)
  st=json.loads(c('v023SnapshotState'));ck('Gains conservés au retour',st['player']['caps']==earned and st['v046']['lore']['done'][q['id']])
  ck('Position et regard de sortie conservés',c('v047Info')['pos']==before['pos'] and abs(st['player']['yaw']-.67)<.001 and abs(st['player']['pitch']+.14)<.001)
  ck('Retour validé annoncé prêt',c('v046Info')['phase']=='ready' and not c('v046Info')['busy'])
  ck('Mémoire de retour libérée',c('v048Info')['retained'] is None)
  ck('Récompense non répétable',c('v046Claim',q['id']) is False)
  # An unrelated load invalidates the retained world; no stale scene may return.
  c('v046Control',{'fail':None});c('v042Enter',site['id']);p.wait_for_timeout(200);c('v020Load','transit_depot');p.wait_for_timeout(250)
  ck('Autre destination invalide le retour',c('v048Info')['retained'] is None)
  ck('La scène étrangère est conservée',c('v042World')['id']=='transit_depot')
  # Reloaded/large interiors cannot rely on a retained scene: failed returns must
  # keep their active site metadata, and Retry must finalise the same exit.
  ck('Nouveau banc après déplacement étranger',c('v046Lab') is True);c('v047Control',{'auto':False})
  c('v048Control',{'returnBudget':0});c('v042Enter',site['id']);p.wait_for_timeout(180)
  ck('Budget zéro interdit la rétention',c('v048Info')['retained'] is None)
  insidepos=json.loads(c('v023SnapshotState'))['player']['pos']
  c('v046ClearCache');c('v046Control',{'fail':'all'});c('v042Exit')
  p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="failed"')
  ck('Sortie en échec conserve le lieu intérieur',json.loads(c('v023SnapshotState'))['v042']['activeInterior']==site['id'])
  ck('Sortie en échec conserve la position intérieure',json.loads(c('v023SnapshotState'))['player']['pos']==insidepos)
  ck('Réessai de sortie proposé',p.locator('#v046Retry').is_visible())
  p.click('#v046Cancel')
  ck('Annulation de sortie rend l’intérieur jouable',c('v042World')['id']=='v042_expedition' and not p.locator('#v046Loading').is_visible())
  ck('Retour incomplet ne perd pas la sauvegarde du lieu',json.loads(c('v023SnapshotState'))['v042']['activeInterior']==site['id'])
  c('v042Exit');p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="failed"')
  c('v046Control',{'fail':None});p.click('#v046Retry')
  p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="ready" && !__MISTRAL_DEBUG.v046Info().busy')
  ck('Réessai de sortie rejoint un extérieur valide',c('v042World')['geo'] is True)
  ck('Réessai termine les métadonnées intérieures',json.loads(c('v023SnapshotState'))['v042']['activeInterior'] is None)
  ck('Aucune transaction de porte restante',c('v048Info')['exitPending'] is None)
  c('v048Control',{'returnBudget':48*1024*1024})
  ck('Aucune exception JavaScript',not errors,errors)
 except Exception:ck('Scénario v0.48',False,traceback.format_exc())
 b.close()
rep={'version':'0.48.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in tests),'failed':sum(not x['ok'] for x in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'HTML final réellement exécuté; chargements du banc synthétique; collisions des véritables gabarits intérieurs et récompenses réelles du code de jeu. Aucun pack territorial intégral installé.'}
(O/'QA_PREPARATION_RETURNS.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(rep['failed'] or errors))
