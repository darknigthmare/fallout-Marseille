"""All retained and new suites on the same final HTML. No carried-over pass count."""
from pathlib import Path
import json,subprocess,sys,hashlib,time
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
steps=['run_all_qa_v029.py','qa_v030_power.py','qa_v030_story.py','qa_v030_edges.py','qa_v030_touch.py'];runs=[]
sha=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest()
for script in steps:
 start=time.monotonic()
 with (O/(script+'.log')).open('w')as log:
  try:rc=subprocess.run([sys.executable,str(R/'tools'/script)],cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=1400).returncode
  except subprocess.TimeoutExpired:rc=124
 runs.append({'script':script,'exit':rc,'seconds':round(time.monotonic()-start,2)});print(script,rc,flush=True)
base=json.loads((O/'QA_GLOBAL_V029.json').read_text());names=['QA_V030_POWER.json','QA_V030_STORY.json','QA_V030_EDGES.json','QA_V030_TOUCH.json'];extras=[json.loads((O/n).read_text())for n in names]
retained=json.loads((O/'QA_GLOBAL_V029_REGRESSION.json').read_text())
errors=base['errors']+[e for x in retained['suites'] for e in x['errors']]+[e for x in extras for e in x['errors']]
report={'version':'0.30.0','html_sha256':sha,'total':base['total']+sum(x['total']for x in extras),'failed':base['failed']+sum(x['failed']for x in extras),'retained':base['total'],'new':sum(x['total']for x in extras),'suites':19+len(extras),'errors':errors,'same_html':base['same_html']and base['html_sha256']==sha and all(x['html_sha256']==sha for x in extras) and hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest()==sha,'runs':runs,'reports':['QA_GLOBAL_V029.json']+names,'scope':'Exact build; Chromium software. Native opaque-origin storage rejection then declared memory adapter. Real authored scene routes and actual mouse/touch controls; synthetic fixture explicitly used for isolated combat/physics checks. No GPU/iPhone/official geographic validation.'}
report['passed']=report['total']-report['failed'];(O/'QA_GLOBAL_V030.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('FINAL',report['passed'],report['failed'],report['same_html'],flush=True)
raise SystemExit(bool(report['failed'] or errors or not report['same_html'] or any(r['exit']for r in runs)))
