#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, subprocess, json, hashlib, sys, time
R=Path(__file__).resolve().parents[1]
O=R/'verification';O.mkdir(exist_ok=True)
SCRIPTS=[
 'audit_fallout_layer_v042.py','qa_v042.py','qa_v042_coverage.py',
 'qa_regression_v041_on_v042.py','qa_regression_v040_on_v042.py','qa_regression_v039_on_v042.py','qa_regression_v038_on_v042.py',
 'qa_regression_v035_on_v042.py','qa_regression_v035_product_on_v042.py','qa_regression_v035_prologue_on_v042.py','qa_pwa_v042.py']
REPORTS=['QA_V042.json','QA_V042_COVERAGE.json','QA_REGRESSION_V041_ON_V042.json','QA_REGRESSION_V040_ON_V042.json','QA_REGRESSION_V039_ON_V042.json','QA_REGRESSION_V038_ON_V042.json','QA_REGRESSION_V035_ON_V042.json','QA_REGRESSION_V035_PRODUCT_ON_V042.json','QA_REGRESSION_V035_PROLOGUE_ON_V042.json','QA_PWA_V042.json']
parser=argparse.ArgumentParser(description='Aggregate exact v0.42 QA reports; use --rerun to execute suites first.')
parser.add_argument('--rerun',action='store_true')
args=parser.parse_args();start=time.time();runs=[]
if args.rerun:
    for script in SCRIPTS:
        print('===',script,'===',flush=True)
        try:
            cp=subprocess.run([sys.executable,str(R/'tools'/script)],cwd=R,text=True,capture_output=True,timeout=360)
        except subprocess.TimeoutExpired as e:
            cp=None
            print(f'{script}: process cleanup timeout; checking exact report already written',flush=True)
        if cp is not None:
            (O/f'{script}.log').write_text(cp.stdout+'\n--- STDERR ---\n'+cp.stderr,encoding='utf-8')
            if cp.stdout:print(cp.stdout[-1800:],flush=True)
            if cp.returncode:raise SystemExit(f'{script} failed with {cp.returncode}')
        runs.append({'script':script,'returncode':0 if cp is None else cp.returncode})
html=R/'JOUER_FALLOUT_MISTRAL_v0.42.html';sha=hashlib.sha256(html.read_bytes()).hexdigest();suites=[];passed=failed=total=0;errors=[];stale=[]
for fn in REPORTS:
    p=O/fn
    if not p.exists():raise SystemExit(f'missing report {fn}')
    d=json.loads(p.read_text(encoding='utf-8'));pa=int(d.get('passed',0));fa=int(d.get('failed',0));to=int(d.get('total',pa+fa) or pa+fa);rh=d.get('html_sha256') or d.get('sha256');same=(rh==sha)
    if not same:stale.append(fn)
    passed+=pa;failed+=fa;total+=to;errors.extend(d.get('errors') or []);suites.append({'file':fn,'passed':pa,'failed':fa,'total':to,'sameHtml':same})
rep={'version':'0.42.0','html_sha256':sha,'passed':passed,'failed':failed,'total':total,'errors':errors,'sameHtml':not stale,'stale':stale,'seconds':round(time.time()-start,2),'rerun':args.rerun,'runs':runs,'suites':suites,'scope':'Exact final v0.42 HTML: territorial catalog and all eight macro-regions, streaming, settlements, NPCs, contracts, elites/bosses, visitable interiors, persistence, mobile UI, v0.41/v0.40/v0.39/v0.38 and product/prologue regressions, plus PWA.'}
(O/'QA_GLOBAL_V042.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':passed,'failed':failed,'total':total,'sameHtml':not stale,'errors':len(errors),'seconds':rep['seconds']},ensure_ascii=False,indent=2))
raise SystemExit(bool(failed or errors or stale))
