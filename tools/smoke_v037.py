from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import json,hashlib
R=Path(__file__).resolve().parents[1];H=(R/'JOUER_FALLOUT_MISTRAL_v0.37.html').read_text();errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.wait_for_timeout(4000)
 print('title',p.title());print('errors',errors);print('debug',p.evaluate("Object.keys(__MISTRAL_DEBUG).filter(k=>k.startsWith('v037'))"));print('info',json.dumps(p.evaluate('__MISTRAL_DEBUG.v037Info()'),ensure_ascii=False)[:1800]);b.close()
raise SystemExit(bool(errors))
