from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time,signal,os,shutil
ROOT=Path('/workspace/fallout-Marseille');BASE=Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--report-name',required=True);p.add_argument('script');p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args()
out=a.output;out.mkdir(parents=True,exist_ok=False);frozen=json.loads((BASE/'FROZEN_INPUTS.json').read_text());assert all(sha(ROOT/n)==h for n,h in frozen.items())
script=ROOT/a.script;before=sha(script);shutil.copy2(script,out/('EXECUTED_'+script.name));argv=[sys.executable,str(script)]+a.arguments
start=time.monotonic();log=out/'PROCESS.log'
with log.open('w') as f:
 process=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=process.wait(timeout=1000)
 except subprocess.TimeoutExpired:
  os.killpg(process.pid,signal.SIGTERM)
  try:code=process.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);code=process.wait()
report=out/a.report_name;changed=[n for n,h in frozen.items()if sha(ROOT/n)!=h]
receipt={'argv':argv,'cwd':str(ROOT),'exitCode':code,'elapsedSeconds':round(time.monotonic()-start,3),'scriptSha256':before,'scriptUnchanged':sha(script)==before,'reportSha256':sha(report)if report.exists()else None,'logSha256':sha(log),'changedProductionInputs':changed,'wrapperSha256':sha(Path(__file__))}
(out/'EXECUTION_STATUS.json').write_text(json.dumps(receipt,indent=2)+'\n');shutil.copy2(Path(__file__),out/'EXECUTED_RUN_CAPTURE.py');print(json.dumps(receipt),flush=True);raise SystemExit(code or int(bool(changed)or not receipt['scriptUnchanged']))
