from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
import json,hashlib,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2];H=(R/'JOUER_FALLOUT_MISTRAL_v0.49.html').read_text();O=R/'verification/v049';checks=[];errors=[]
def ck(n,ok,d=None):checks.append({'name':n,'ok':bool(ok),'detail':d});print(('OK 'if ok else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__S=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__S.get(String(k))??null,setItem:(k,v)=>__S.set(String(k),String(v)),removeItem:k=>__S.delete(String(k)),clear:()=>__S.clear()}})")
 def c(n,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v020Reset');c('v020Load','transit_depot');p.wait_for_timeout(250)
  before=c('v046WorldObjects');state=c('v020State');ck('La campagne réelle de base est chargée',len(before['interactions'])>0,before)
  for i in range(2):
   ck('Entrée de banc isolé '+str(i+1),c('v046Lab'))
   ck('Le banc refuse une sauvegarde campagne '+str(i+1),c('v046Save') is False)
   ck('Retour de banc accepté '+str(i+1),c('v046Campaign') is True)
   p.wait_for_timeout(350)  # Include late startup/UI callbacks, not just the immediate return.
   ck('La vraie scène est restaurée '+str(i+1),c('v046WorldObjects')==before,c('v046WorldObjects'))
   after=c('v020State');ck('Position, zone et portefeuille restaurés '+str(i+1),after['player']['zone']==state['player']['zone'] and after['player']['pos']==state['player']['pos'] and after['player']['caps']==state['player']['caps'])
   ck('Aucune grille synthétique ne reste dans la campagne '+str(i+1),not c('v047Info')['lab'] and len(c('v047Info')['terrain'])==0)
  ck('Aucune exception JavaScript',not errors,errors)
 except Exception:ck('Scénario isolation du banc',False,traceback.format_exc())
 b.close()
r={'version':'0.47.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'checks':checks,'errors':errors};(O/'QA_LAB_ISOLATION.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['passed','failed','total','errors']}));raise SystemExit(bool(r['failed'] or errors))
