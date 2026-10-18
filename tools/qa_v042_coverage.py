#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,traceback
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=R/'JOUER_FALLOUT_MISTRAL_v0.42.html';checks=[];errors=[]
def ck(n,c,d=None):checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort());p.set_content(H.read_text(),wait_until='load');p.wait_for_timeout(400)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  for macro in c('v036Macros'):
   sites=c('v042Macro',macro);c('v017LoadMacro',macro)
   inside=[]
   for site in sites:
    q=c('v042Project',site['id']);inside.append(bool(q and q['inside']))
   ck(f'{macro} · 31 projections valides',len(sites)==31 and all(inside),{'sites':len(sites),'inside':sum(inside)})
   sample=next((s for s in sites if s['kind']=='settlement'),sites[0]);c('v017SetPlayerLatLon',sample['lat'],sample['lon']);c('v042Update',.8);r=c('v042Runtime');ck(f'{macro} · streaming actif',sample['id'] in r['active'] and len(r['active'])<=7,r)
   boss=next(s for s in sites if s['kind']=='boss');c('v017SetPlayerLatLon',boss['lat'],boss['lon']);c('v042Update',.8);w=c('v042World');enemy=[e for e in w['enemies'] if e['site']==boss['id']];ck(f'{macro} · boss régional présent',len(enemy)==boss['enemySlots'] and any(e['rank']=='boss' for e in enemy),{'boss':boss['id'],'enemies':len(enemy)})
  ck('aucune exception JavaScript',not errors,errors)
 except Exception:ck('scénario couverture v0.42',False,traceback.format_exc())
 b.close()
rep={'version':'0.42.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'All 8 real-map macro-regions are loaded with network blocked. All 248 site projections and one settlement + regional boss stream per macro are verified.'};(O/'QA_V042_COVERAGE.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errors))
