#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'verification/v048';O.mkdir(exist_ok=True)
commands=[['node','--check','src/game.js'],['node','tests/v048/kernel.test.cjs'],['node','tests/v048/inherited_kernel.test.cjs'],['node','tests/v048/inherited_legacy_kernel.test.cjs'],['node','tests/v048/inherited_legacy_distribution.cjs'],[sys.executable,'tests/v048/runtime.py']]
commands += [[sys.executable,'tests/v048/'+n] for n in ['inherited_runtime.py','inherited_server_io.py','inherited_lab_isolation.py','inherited_legacy_runtime.py','inherited_legacy_regression_campaign.py','inherited_legacy_regression_prologue.py','inherited_legacy_regression_product.py']]
for cmd in ([] if '--collect' in sys.argv else commands):
 print(' '.join(cmd),flush=True)
 r=subprocess.run(cmd,cwd=R)
 if r.returncode:raise SystemExit(r.returncode)
files=['QA_BUDGET_PASSAGES.json','QA_PREPARATION_RETURNS.json','QA_KERNEL_NEW.json','QA_KERNEL_LEGACY.json','QA_DISTRIBUTION.json','QA_STREAMING_NEW.json','QA_SERVER_IO.json','QA_LAB_ISOLATION.json','QA_RUNTIME.json','QA_CAMPAIGN.json','QA_PROLOGUE.json','QA_PRODUCT.json']
h=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.48.html').read_bytes()).hexdigest();rows=[]
for f in files:
 j=json.loads((O/f).read_text());rows.append({'file':f,'passed':j['passed'],'failed':j['failed'],'total':j['total'],'sameHtml':not j.get('html_sha256') or j['html_sha256']==h})
out={'version':'0.48.0','html_sha256':h,'passed':sum(r['passed'] for r in rows),'failed':sum(r['failed'] for r in rows),'total':sum(r['total'] for r in rows),'allHtmlMatch':all(r['sameHtml'] for r in rows),'suites':rows,'scope':'HTML réel, préparation et retours via banc synthétique identifié, collisions des gabarits du jeu, tests purs Node et serveur HTTP loopback. Pas de pack territorial intégral ni navigation native certifiés.'}
(O/'QA_GLOBAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2));raise SystemExit(bool(out['failed'] or not out['allHtmlMatch']))
