#!/usr/bin/env python3
"""Run every retained regression then the local-control/perception suites on one build."""
from pathlib import Path
import subprocess,json,hashlib,sys
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
steps=['run_regression_v029.py','qa_v029_terminal.py','qa_v029_world_story.py','qa_v029_perception_mobile.py'];runs=[]
for script in steps:
 with (O/(script+'.log')).open('w')as f:r=subprocess.run([sys.executable,str(R/'tools'/script)],cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
 runs.append({'script':script,'exit':r.returncode});print(script,r.returncode,flush=True)
base=json.loads((O/'QA_GLOBAL_V029_REGRESSION.json').read_text());files=['QA_V029_TERMINAL.json','QA_V029_WORLD_STORY.json','QA_V029_PERCEPTION_MOBILE.json','QA_V029_TOUCH.json'];extras=[json.loads((O/n).read_text())for n in files];sha=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest();total=base['total']+sum(x['total']for x in extras);failed=base['failed']+sum(x['failed']for x in extras)
report={'version':'0.29.0','html_sha256':sha,'total':total,'passed':total-failed,'failed':failed,'retained':base['total'],'new':sum(x['total']for x in extras),'suites':len(base['runs'])+len(extras) if 'runs'in base else 19,'errors':[e for x in extras for e in x['errors']],'same_html':base['same_html'] and all(x['html_sha256']==sha for x in extras),'runs':runs,'regression':'QA_GLOBAL_V029_REGRESSION.json','new_reports':files,'scope':'Software Chromium. Opaque-origin native failure; success paths use explicit memory adapter. Synthetic AI arena marked as such. Real fictional scene routes tested separately. No GPU/iPhone certification. No full manual campaign playthrough.'}
(O/'QA_GLOBAL_V029.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('FINAL',report['passed'],report['failed'],report['same_html'],flush=True);raise SystemExit(bool(failed or report['errors'] or not report['same_html'] or any(r['exit']for r in runs)))
