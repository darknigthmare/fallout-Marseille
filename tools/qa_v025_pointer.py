#!/usr/bin/env python3
"""Native pointer clicks and touch taps on projected enemy mesh regions.
No dispatch_event substitution for the targeting checks in this suite.
"""
from pathlib import Path
import json,hashlib,math
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];H=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[]
def check(ok,name,detail=None):
 rows.append(dict(ok=bool(ok),name=name,detail=detail));print('OK' if ok else 'FAIL',name,detail or '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
 for mobile in [False,True]:
  p=b.new_page(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 960},has_touch=mobile);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV025').wait_for(timeout=30000)
  def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v020Reset');c('v020Fixture',False,'raider',7);c('v020EnemyPatch',{'yaw':math.pi});c('v020Tick',1);c('v020Vats');c('v025Paint')
  for part in ['head','arm_r','leg_l','body']:
   ss=c('v025Snapshot');v=next(x for x in ss['screen']if x['id']==part);point=v['center'];x,y=point['x'],point['y']
   # Ensure centre does not fall on a callout: this verifies selection on the body.
   hit=p.evaluate('p=>{const e=document.elementFromPoint(p.x,p.y);return {tag:e?.tagName,id:e?.dataset.part,parent:e?.parentNode?.id}}',{'x':x,'y':y})
   check(hit['tag']=='polygon',f"{'Tactile' if mobile else 'Souris'} : {part} est une zone de corps, pas une étiquette",hit)
   if mobile:p.touchscreen.tap(x,y)
   else:p.mouse.click(x,y)
   check(c('v025Info')['selected']['part']==part,f"{'Tactile' if mobile else 'Souris'} : sélection native de {part}")
   check(len(c('v025Snapshot')['queue'])==0,f"{'Tactile' if mobile else 'Souris'} : toucher {part} ne tire pas")
  p.locator('[data-v23="vats-add"]').click();check(c('v025Snapshot')['queue'][0]['id']=='body',f"{'Tactile' if mobile else 'Souris'} : ajout séparé du dernier membre visé")
  p.locator('[data-v23="vats-close"]').click();check(c('getMode')=='PLAYING',f"{'Tactile' if mobile else 'Souris'} : quitter retrouve le jeu")
  p.close()
 b.close()
check(not errors,'Aucune exception JavaScript',errors)
out=dict(version='0.25.0',html_sha256=hashlib.sha256(H.encode()).hexdigest(),total=len(rows),passed=sum(x['ok']for x in rows),failed=sum(not x['ok']for x in rows),errors=errors,scope='Exact HTML; synthetic arena; native mouse clicks and touchscreen taps on screen-projected polygon centres, no dispatch_event; no storage success claim',results=rows)
(R/'verification/QA_V025_POINTER.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('RESULT',out['total'],out['failed']);raise SystemExit(bool(out['failed']))
