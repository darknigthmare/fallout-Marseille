#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'verification/v047';O.mkdir(exist_ok=True)
commands=[['node','--check','src/game.js'],['node','tests/v047/kernel.test.cjs'],['node','tests/v047/legacy_kernel.test.cjs'],['node','tests/v047/legacy_distribution.cjs'],[sys.executable,'tests/v047/runtime.py'],[sys.executable,'tests/v047/server_io.py'],[sys.executable,'tests/v047/lab_isolation.py'],[sys.executable,'tests/v047/legacy_runtime.py'],[sys.executable,'tests/v047/legacy_regression_campaign.py'],[sys.executable,'tests/v047/legacy_regression_prologue.py'],[sys.executable,'tests/v047/legacy_regression_product.py']]
for cmd in ([] if '--collect' in sys.argv else commands):
 print(' '.join(cmd),flush=True)
 r=subprocess.run(cmd,cwd=R)
 if r.returncode:raise SystemExit(r.returncode)
files=['QA_KERNEL_NEW.json','QA_KERNEL_LEGACY.json','QA_DISTRIBUTION.json','QA_STREAMING_NEW.json','QA_SERVER_IO.json','QA_LAB_ISOLATION.json','QA_RUNTIME.json','QA_CAMPAIGN.json','QA_PROLOGUE.json','QA_PRODUCT.json'];sha=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.47.html').read_bytes()).hexdigest();rows=[]
for f in files:
 j=json.loads((O/f).read_text());rows.append({'file':f,'passed':j['passed'],'failed':j['failed'],'total':j['total'],'sameHtml':not j.get('html_sha256') or j['html_sha256']==sha})
out={'version':'0.47.0','html_sha256':sha,'passed':sum(r['passed'] for r in rows),'failed':sum(r['failed'] for r in rows),'total':sum(r['total'] for r in rows),'allHtmlMatch':all(r['sameHtml'] for r in rows),'suites':rows,'limitations':['Géographie du banc synthétique ; pas de traversée du pack territorial intégral.','Navigation native Chromium bloquée par la politique de cet environnement. Tests navigateur via set_content ; serveur HTTP vérifié séparément. Pas de validation IndexedDB natif ni installation PWA native.']}
(O/'QA_GLOBAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2));raise SystemExit(bool(out['failed'] or not out['allHtmlMatch']))
