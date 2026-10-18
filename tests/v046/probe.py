from pathlib import Path
from playwright.sync_api import sync_playwright
import json,sys
R=Path(__file__).resolve().parents[2]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});errors=[];p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content((R/'index.html').read_text(),wait_until='load');p.wait_for_timeout(3100);print('title',p.title());print('errors',errors);print('v046',p.evaluate('typeof __MISTRAL_DEBUG.v046Info'))
 try:
  print('lab',p.evaluate('__MISTRAL_DEBUG.v046Lab()'));print('info',p.evaluate('__MISTRAL_DEBUG.v046Info()'));p.evaluate('__MISTRAL_DEBUG.v046Render()');p.screenshot(path=str(R/'verification/v046/probe.png'));print('errs',errors)
 except Exception as e:print('FAIL',e)
 b.close()
