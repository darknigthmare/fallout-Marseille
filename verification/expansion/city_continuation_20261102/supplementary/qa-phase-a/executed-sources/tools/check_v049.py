#!/usr/bin/env python3
"""Run the reproducible v0.49 suites (or --collect existing results)."""
from pathlib import Path
import argparse,concurrent.futures,subprocess,sys,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'verification/v049';O.mkdir(exist_ok=True)
SPECS=[('kernel.test.cjs','QA_ENCOUNTER_KERNEL.json'),('runtime.py','QA_ENCOUNTERS.json'),('saves.py','QA_ENCOUNTER_SAVES.json'),('v048_kernel.test.cjs','QA_BUDGET_PASSAGES.json'),('v048_runtime.py','QA_PREPARATION_RETURNS.json'),('v048_inherited_kernel.test.cjs','QA_KERNEL_NEW.json'),('v048_inherited_legacy_kernel.test.cjs','QA_KERNEL_LEGACY.json'),('v048_inherited_legacy_distribution.cjs','QA_DISTRIBUTION.json'),('v048_inherited_runtime.py','QA_STREAMING_NEW.json'),('v048_inherited_server_io.py','QA_SERVER_IO.json'),('v048_inherited_lab_isolation.py','QA_LAB_ISOLATION.json'),('v048_inherited_legacy_runtime.py','QA_RUNTIME.json'),('v048_inherited_legacy_regression_campaign.py','QA_CAMPAIGN.json'),('v048_inherited_legacy_regression_prologue.py','QA_PROLOGUE.json'),('v048_inherited_legacy_regression_product.py','QA_PRODUCT.json')]
def run(spec):
 name,_=spec;cmd=['node' if name.endswith('.cjs') else sys.executable,'tests/v049/'+name]
 r=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=180)
 (O/(name+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
 print(('PASS ' if r.returncode==0 else 'FAIL ')+name,flush=True)
 return name,r.returncode
ap=argparse.ArgumentParser();ap.add_argument('--collect',action='store_true');ap.add_argument('--workers',type=int,default=1);a=ap.parse_args()
subprocess.run(['node','--check','src/game.js'],cwd=R,check=True)
if not a.collect:
 with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,3))) as ex:results=list(ex.map(run,SPECS))
 if any(rc for _,rc in results):raise SystemExit(1)
h=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.49.html').read_bytes()).hexdigest();rows=[];errors=[]
for name,f in SPECS:
 j=json.loads((O/f).read_text());rows.append({'test':name,'file':f,'passed':j['passed'],'failed':j['failed'],'total':j['total'],'sameHtml':not j.get('html_sha256') or j['html_sha256']==h});errors+=j.get('errors',[])
out={'version':'0.49.0','html_sha256':h,'passed':sum(r['passed'] for r in rows),'failed':sum(r['failed'] for r in rows),'total':sum(r['total'] for r in rows),'allHtmlMatch':all(r['sameHtml'] for r in rows),'javascriptErrors':errors,'suites':rows,'scope':'Programme complet exécuté en Chromium avec Playwright set_content et données synthétiques identifiées. Persistance, dépouilles, sauvegardes et régressions v0.48. Serveur loopback vérifié séparément. Pas de pack géographique intégral ni de navigation native/IndexedDB/PWA natifs certifiés.'}
(O/'QA_GLOBAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','failed','total','allHtmlMatch']},ensure_ascii=False));raise SystemExit(bool(out['failed'] or not out['allHtmlMatch'] or errors))
