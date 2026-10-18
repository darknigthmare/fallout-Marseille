#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parents[1]
commands=[['node','--check','src/game.js'],['node','tests/v046/kernel.test.cjs'],['node','tests/v046/distribution.cjs'],[sys.executable,'tests/v046/runtime.py'],[sys.executable,'tests/v046/regression_campaign.py'],[sys.executable,'tests/v046/regression_prologue.py'],[sys.executable,'tests/v046/regression_product.py']]
for cmd in commands:
 print(' '.join(cmd),flush=True);r=subprocess.run(cmd,cwd=R)
 if r.returncode:raise SystemExit(r.returncode)
files=['QA_KERNEL.json','QA_DISTRIBUTION.json','QA_RUNTIME.json','QA_CAMPAIGN.json','QA_PROLOGUE.json','QA_PRODUCT.json'];rows=[]
sha=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.46.html').read_bytes()).hexdigest()
for name in files:
 d=json.loads((R/'verification/v046'/name).read_text());rows.append({'file':name,'passed':d['passed'],'failed':d['failed'],'total':d['total'],'sameHtml':not d.get('html_sha256') or d['html_sha256']==sha})
out={'version':'0.46.0','html_sha256':sha,'passed':sum(x['passed'] for x in rows),'failed':sum(x['failed'] for x in rows),'total':sum(x['total'] for x in rows),'allHtmlMatch':all(x['sameHtml'] for x in rows),'suites':rows,'scope':'Noyau Node et HTML réellement exécuté dans Chromium. Test géographique synthétique ; aucun audit exhaustif du terrain réel revendiqué.'}
(R/'verification/v046/QA_GLOBAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2));raise SystemExit(out['failed']!=0 or not out['allHtmlMatch'])
