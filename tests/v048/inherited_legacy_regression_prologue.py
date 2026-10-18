from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
import json,hashlib,traceback
R=Path(__file__).resolve().parents[2];O=R/'verification/v048';H=(R/'JOUER_FALLOUT_MISTRAL_v0.48.html').read_text();checks=[];errors=[]
def ck(n,c,d=None):checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept());p.set_content(H,wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=30000)
 p.evaluate("window.__S=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__S.get(String(k))??null,setItem:(k,v)=>__S.set(String(k),String(v)),removeItem:k=>__S.delete(String(k))}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def dismiss():p.evaluate('__MISTRAL_DEBUG.v020ModalDismiss()')
 try:
  c('v018NoNetwork',True);c('setRenderPaused',True);c('v018StartStory');p.wait_for_timeout(700)
  ck('Nouvelle campagne dans le prologue',c('v020Stats')['id']=='vault_prologue',c('v020Stats')['id']);pr=c('v35pInfo');ck('Stage initial',pr['stage']==1,pr)
  ids=[x['id'] for x in c('v020Stats')['interactables']];ck('Interactions essentielles présentes',all(x in ids for x in ['v35p-locker','v35p-clinic','v35p-filter','v35p-ration','v35p-records','v35p-issue','v35p-exit']),ids)
  # Physical approach each route anchor.
  for oid in ['v35p-locker','v35p-clinic','v35p-filter','v35p-ration','v35p-records','v35p-issue','v35p-exit']:
   ck('Approche '+oid,c('v020Approach',oid) is not None)
  # Story functions and UI choices.
  c('v35pLocker');p.locator('#dialogueChoices button').first.click();ck('Casier -> stage 2',c('v35pInfo')['stage']==2)
  c('v35pClinic');p.locator('#dialogueChoices button').first.click();c('v35pFilter');p.locator('#dialogueChoices button').first.click();ck('Routine -> stage 3',c('v35pInfo')['stage']==3,c('v35pInfo'))
  c('v35pBreakfast');p.locator('#dialogueChoices button').first.click();ck('Petit-déjeuner -> stage 4',c('v35pInfo')['stage']==4)
  c('v35pRation');dismiss();ck('Décès administratif -> stage 5',c('v35pInfo')['stage']==5);ck('Quête principale lancée',c('v020State')['quest']['main']==1)
  c('v35pRecords');p.locator('#dialogueChoices button').first.click();ck('Archives -> stage 6',c('v35pInfo')['stage']==6)
  c('v35pBrief');p.locator('#dialogueChoices button').first.click();ck('Briefing -> stage 7',c('v35pInfo')['stage']==7)
  c('v35pIssue');p.locator('#dialogueChoices button').first.click();ck('Dotation -> stage 8',c('v35pInfo')['stage']==8);ck('Dotation unique',c('v35pInfo')['loadout']=='patrol')
  c('v35pExit');p.locator('#dialogueChoices button').first.click();p.wait_for_timeout(250);ck('Sortie vers Aubagne',c('v020Stats')['id']=='aubagne',c('v020Stats')['id']);ck('Prologue terminé',c('v35pInfo')['complete'] is True,c('v35pInfo'));ck('Campagne continue étape 2',c('v020State')['quest']['main']==2)
 except Exception:ck('Exception pilote',False,traceback.format_exc())
 b.close()
rep={'version':'0.46.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks};(O/'QA_PROLOGUE.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2));print('TOTAL',rep['passed'],rep['failed'],errors);raise SystemExit(bool(rep['failed'] or errors))
