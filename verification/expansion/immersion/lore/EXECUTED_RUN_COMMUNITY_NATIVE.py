from pathlib import Path
import subprocess,time,hashlib,json,sys,argparse,datetime
parser=argparse.ArgumentParser();parser.add_argument('--output-name',default='native');args=parser.parse_args()
if not args.output_name.replace('-','').replace('_','').isalnum():parser.error('simple output name required')
root=Path('/workspace/fallout-Marseille');script=root/'tests/expansion/community_dossiers_native.py';out=Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion/lore')/args.output_name
out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
argv=[sys.executable,str(script),'--run','--output',str(out),'--expect-html-sha',sha(root/'index.html'),'--expect-architecture-sha',sha(root/'data/map_pack/architecture/index.json'),'--expect-lore-sha',sha(root/'src/v050/10_lore_continuity.js')]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();start=time.monotonic();log=out/'process.log';receipt={'argv':argv,'cwd':str(root),'startedAtUTC':started,'scriptSha256':sha(script),'runnerSha256':sha(Path(__file__))}
with log.open('w') as f:
 try:r=subprocess.run(argv,cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=1500);code=r.returncode
 except subprocess.TimeoutExpired:code=124
report=out/'COMMUNITY_DOSSIERS_NATIVE.json'
receipt.update(exitCode=code,elapsedSeconds=round(time.monotonic()-start,3),log='process.log',logSha256=sha(log),report=report.name,reportSha256=sha(report) if report.is_file() else None,scriptUnchanged=sha(script)==receipt['scriptSha256'])
(out/'EXECUTION_STATUS.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');(out/'EXECUTED_RUN_COMMUNITY_NATIVE.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(receipt,ensure_ascii=False));print(log.read_text()[-4500:]);raise SystemExit(code)
