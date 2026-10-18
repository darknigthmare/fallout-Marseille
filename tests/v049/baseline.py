from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import json,hashlib
import argparse
R=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser(description='Reproduce the fixed proximity-unload bug in the supplied v0.48 HTML.')
ap.add_argument('--baseline',type=Path,default=R/'history/v0.48_generated/JOUER_FALLOUT_MISTRAL_v0.48.html')
P=ap.parse_args().baseline;H=P.read_text()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();errs=[];p.on('pageerror',lambda e:errs.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__store.get(k)||null,setItem:(k,v)=>__store.set(k,String(v)),removeItem:k=>__store.delete(k)}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 c('v046Lab');c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False})
 site=next(s for s in c('v042Catalog') if s['kind']=='nest');st=json.loads(c('v023SnapshotState'));pos=c('v047Info')['pos'];st['v046']['placements'][site['id']]=[pos[0]+12,pos[1]-1.65,pos[2]];c('v023Restore',json.dumps(st));c('v042Spawn',site['id']);original=c('v042World')['enemies'][0];c('v025Damage','leg_l',18,0);hurt=c('v042World')['enemies'][0];c('v042Unload',site['id']);c('v042Spawn',site['id']);back=c('v042World')['enemies'][0]
 data={'version':'0.48.0 baseline','sourceSha256':hashlib.sha256(H.encode()).hexdigest(),'site':site['id'],'before':original,'damaged':hurt,'afterReturn':back,'reproducedHealing':hurt['hp']<original['hp'] and back['hp']==original['hp'],'errors':errs,'scope':'Exact v0.48 HTML, explicit placement in the identified synthetic exterior. Proximity actor unload/reload through production functions, not a full world reconstruction.'}
 (R/'verification/v049/BASELINE_V048.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps(data,ensure_ascii=False,indent=2));b.close()
