"""Run prior browser suites against this delivery, not historical QA reports."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import argparse,subprocess,json,hashlib,time
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
folder=root/'verification/consigne-vie/regressions';folder.mkdir(parents=True,exist_ok=True)
suites='gestes retrouvailles pigeons gabians rats cigales secours parts lys compagnons voisins notaires mutuelle radieuse poste pharmacie'.split()
jobs=[(s,root/f'tests/expansion/{s}_browser_smoke.py') for s in suites]+[(s,root/f'tests/expansion/{s}_cold_save_smoke.py') for s in ['birds','rats']]
# Distinguish the historical rat browser and cold-restart reports.
jobs=[(name+('-cold' if 'cold_save' in str(path) else ''),path) for name,path in jobs]
sha=hashlib.sha256((root/'index.html').read_bytes()).hexdigest()
def run(job):
    name,path=job;out=folder/name;t=time.monotonic()
    with (folder/(name+'.log')).open('w') as log:
        result=subprocess.run(['python',str(path),'--html',str(root/'index.html'),'--output',str(out)],cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=360)
    reports=[]
    for p in out.glob('*.json'):
        v=json.loads(p.read_text())
        if 'html_sha256' in v and 'passed' in v:reports.append((p,v))
    valid=result.returncode==0 and len(reports)==1 and reports[0][1]['html_sha256']==sha and not reports[0][1].get('errors') and reports[0][1].get('complete',True)
    record={'suite':name,'ok':valid,'exit_code':result.returncode,'seconds':round(time.monotonic()-t,1),'passed':reports[0][1]['passed'] if len(reports)==1 else None,'report':str(reports[0][0].relative_to(root)) if len(reports)==1 else None}
    print(json.dumps(record),flush=True);return record
results=[]
with ThreadPoolExecutor(max_workers=max(1,min(a.workers,3))) as pool:
    for f in as_completed([pool.submit(run,j) for j in jobs]):
        results.append(f.result());(folder/'SUMMARY.json').write_text(json.dumps({'html_sha256':sha,'complete':len(results)==len(jobs),'results':results},indent=2))
assert all(v['ok'] for v in results), 'One or more regressions failed; inspect logs'
