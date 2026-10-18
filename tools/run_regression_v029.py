#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json,hashlib,time
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
suites=[('qa_regression_v020_on_v022.py','QA_REGRESSION_V020_ON_V022.json'),('qa_regression_v021_on_v022.py','QA_REGRESSION_V021_ON_V022.json'),('qa_regression_v021_extra_on_v022.py','QA_REGRESSION_V021_EXTRA_ON_V022.json'),('qa_v022.py','QA_V022.json'),('qa_v022_extra.py','QA_V022_EXTRA.json'),('qa_v023.py','QA_V023.json'),('qa_v023_extra.py','QA_V023_EXTRA.json'),('qa_v025.py','QA_V025.json'),('qa_v025_pointer.py','QA_V025_POINTER.json'),('qa_v026.py','QA_V026.json'),('qa_v026_edges.py','QA_V026_EDGES.json'),('qa_v027.py','QA_V027.json'),('qa_v027_radio_storage.py','QA_V027_RADIO_STORAGE.json'),('qa_v028_body.py','QA_V028_BODY.json'),('qa_v028_light_story_game.py','QA_V028_LIGHT_STORY_GAME.json')]
h=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest();results=[]
for script,report in suites:
 t=time.monotonic();(O/report).unlink(missing_ok=True)
 with (O/(script+'.log')).open('w')as log:
  try:rc=subprocess.run([sys.executable,str(R/'tools'/script)],cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=500).returncode
  except subprocess.TimeoutExpired:rc=124
 j=json.loads((O/report).read_text()) if (O/report).exists() else {};x=dict(script=script,report=report,exit=rc,seconds=round(time.monotonic()-t,2),passed=j.get('passed',0),failed=j.get('failed',1),html_sha256=j.get('html_sha256')or j.get('sha256'),errors=j.get('errors',[]));results.append(x);print(script,rc,x['passed'],x['failed'],flush=True)
final=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest();summary=dict(version='0.29.0',html_sha256=h,passed=sum(x['passed']for x in results),failed=sum(x['failed']for x in results),same_html=h==final and all(x['html_sha256']==h for x in results),suites=results,scope='HTML exact dans Chromium logiciel. États/caméras d’essai préparés. Stockage mémoire déclaré après contrôle du refus natif opaque ; tentative localhost bloquée par administrateur. Pas de GPU, iPhone, ni parcours humain intégral.')
summary['total']=summary['passed']+summary['failed'];(O/'QA_GLOBAL_V029_REGRESSION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('GLOBAL',summary['passed'],summary['failed'],summary['same_html']);raise SystemExit(any(x['exit'] for x in results) or summary['failed']>0 or not summary['same_html'])
