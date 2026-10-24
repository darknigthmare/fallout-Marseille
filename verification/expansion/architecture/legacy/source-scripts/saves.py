from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import json,hashlib,traceback
R=Path(__file__).resolve().parents[2];O=R/'verification/v049';H=(R/'JOUER_FALLOUT_MISTRAL_v0.49.html').read_text();tests=[];errors=[]
def ck(n,ok,d=None):tests.append({'name':n,'ok':bool(ok),'detail':d});print(('OK 'if ok else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.set_default_timeout(25000);p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{get length(){return __store.size},getItem:k=>__store.get(String(k))||null,setItem:(k,v)=>__store.set(String(k),String(v)),removeItem:k=>__store.delete(String(k)),key:i=>[...__store.keys()][i]||null}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  c('v046Lab');c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False});site=next(s for s in c('v042Catalog') if s['kind']=='shelter');c('v042Enter',site['id']);p.wait_for_timeout(150)
  a=c('v049Actors')[0];c('v049Damage',a['id'],14,'arm_l');c('v049ProbePose',a['id'],[-19,0,24],.45);snapshot=c('v023SnapshotState');hp=next(e for e in json.loads(snapshot)['v049']['actors'].values() if e['id']==a['id'])['health'];oldstore=p.evaluate('Array.from(__store.entries())')
  ck('Sauvegarde manuelle interdite dans le banc',c('v035SaveSlot',1) is False)
  ck('Aucun emplacement modifié par le banc',p.evaluate('Array.from(__store.entries())')==oldstore)
  ck('Sauvegarde automatique interdite dans le banc',c('v035Autosave','QA') is False)
  c('v046Campaign');c('v023Restore',snapshot);c('v020Load','v042_expedition');p.wait_for_timeout(250)
  acts=c('v049Actors');a2=next(e for e in acts if e['id']==a['id'])
  ck('Reprise JSON vers intérieur sans données réseau',a2['hp']==hp and a2['pos']==[-19,0,24],a2)
  # Move through the existing game's QA control, but do NOT manually checkpoint.
  idx=next(i for i,e in enumerate(c('v042World')['enemies']) if e['id']==a['id']);c('v025MoveEnemy',idx,[-20,0,25],.6)
  saved=c('v035SaveSlot',1);ck('Emplacement manuel créé en campagne',bool(saved))
  stored=p.evaluate("JSON.parse(__store.get('fallout_mistral_slot_v035_1'))")
  ck('Pose courante capturée avant enveloppe de sauvegarde',stored['snapshot']['v049']['actors'][a['id']]['pos']==[-20,0,25],stored['snapshot']['v049']['actors'][a['id']])
  c('v025MoveEnemy',idx,[-21,0,26],.7);ck('Rechargement de l’emplacement accepté',c('v035LoadSlot',1) is True);p.wait_for_timeout(250)
  a3=next(e for e in c('v049Actors') if e['id']==a['id']);ck('Emplacement restaure santé, position et orientation',a3['hp']==hp and a3['pos']==[-20,0,25] and a3['yaw']==.6,a3)
  ck('Membres blessés présents après chargement du slot',a3['limbs'].get('arm_l',0)>0,a3['limbs'])
  # Corrupted additions are filtered without losing a valid encounter.
  bad=json.loads(c('v023SnapshotState'));bad['v049']['actors']['__proto__']={'pos':[0,0,0],'home':[0,0,0],'health':999,'maxHealth':999};bad['v049']['actors']['bad-id']={**bad['v049']['actors'][a['id']]};bad['v049']['actors'][a['id']]['status']['arbitraryEffect']=999
  result=p.evaluate('(raw)=>{try{__MISTRAL_DEBUG.v023Restore(raw);return {rejected:false}}catch(e){return {rejected:true,message:e.message}}}',json.dumps(bad));ck('Import global refuse la clé de prototype',result['rejected'] and 'interdite' in result['message'],result)
  del bad['v049']['actors']['__proto__'];c('v023Restore',json.dumps(bad));state=json.loads(c('v023SnapshotState'));ck('Import refuse les identifiants injectés','__proto__' not in state['v049']['actors'] and 'bad-id' not in state['v049']['actors'])
  ck('Import retire les effets inconnus','arbitraryEffect' not in state['v049']['actors'][a['id']]['status'])
  ck('Import conserve la rencontre valide',state['v049']['actors'][a['id']]['health']==hp)
  ck('Aucune pollution de prototype',p.evaluate('Object.prototype.health===undefined'))
  ck('Aucune exception JavaScript',not errors,errors)
 except Exception:ck('Scénario sauvegardes v0.49',False,traceback.format_exc())
 b.close()
rep={'version':'0.49.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in tests),'failed':sum(not x['ok'] for x in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'HTML livré. Sauvegardes et imports du jeu testés avec stockage mémoire compatible, pas localStorage/IndexedDB natifs.'};(O/'QA_ENCOUNTER_SAVES.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(rep['failed'] or errors))
