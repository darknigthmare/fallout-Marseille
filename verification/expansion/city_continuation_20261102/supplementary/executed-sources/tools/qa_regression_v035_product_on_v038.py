from pathlib import Path
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
import json,hashlib,traceback
R=Path(__file__).resolve().parents[1];O=R/'verification';H=(R/'JOUER_FALLOUT_MISTRAL_v0.38.html').read_text();rows=[];errs=[]
def ck(n,c,d=None):rows.append({'name':n,'ok':bool(c),'detail':d});print(('OK 'if c else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errs.append(str(e)));p.on('dialog',lambda d:d.accept());p.set_content(H,wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=30000)
 p.evaluate("window.__S=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__S.get(String(k))??null,setItem:(k,v)=>__S.set(String(k),String(v)),removeItem:k=>__S.delete(String(k)),clear:()=>__S.clear()}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  c('v018NoNetwork',True);c('setRenderPaused',True);c('v018StartFree');p.wait_for_timeout(700);saved=c('v035SaveSlot',1);ck('Sauvegarde manuelle produite',bool(saved));latest=c('v035Latest');ck('Emplacement manuel détecté',any(x['slot']==1 for x in latest),[(x['kind'],x['slot']) for x in latest]);caps=c('v020State')['player']['caps'];c('v020SetPlayer',{'caps':caps+999});c('v035Menu');p.wait_for_timeout(100);ck('Continuer réactivé',not p.locator('#btnContinue').is_disabled());p.click('#btnContinue');p.wait_for_timeout(220);ck('Reprise restaure un point cohérent',c('v020State')['player']['caps']==caps,c('v020State')['player']['caps'])
  ck('Mode sûr activable',c('v035SafeMode'));diag=c('v035Diagnostic');ck('Diagnostic contient build, carrière et slots',diag['version']=='0.38.0' and 'career'in diag and len(diag['slots'])>=1,diag)
  ck('PWA manifeste présent',(R/'manifest.webmanifest').exists());ck('Service worker présent',(R/'sw.js').exists());ck('Index installable identique',hashlib.sha256((R/'index.html').read_bytes()).hexdigest()==hashlib.sha256(H.encode()).hexdigest())
  ck('Crédits v0.35 à jour','0.38.0 · Cadastre complet' in p.locator('#creditsScreen').inner_text())
 except Exception:ck('Exception pilote',False,traceback.format_exc())
 b.close()
rep={'version':'0.38.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok']for x in rows),'failed':sum(not x['ok']for x in rows),'total':len(rows),'errors':errs,'checks':rows};(O/'QA_REGRESSION_V035_PRODUCT_ON_V038.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2));print('TOTAL',rep['passed'],rep['failed'],errs);raise SystemExit(bool(rep['failed']or errs))
