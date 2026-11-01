from pathlib import Path
import hashlib,json,socket,subprocess,time
root=Path('/workspace/fallout-Marseille');out=Path('/workspace/.cloud-setup/fallout-marseille/continuation-next/districts/native-final-98a7-02');out.mkdir(parents=True,exist_ok=False)
script=root/'tests/expansion/north_terrain_native.py';python='/workspace/.cloud-setup/fallout-marseille/venv/bin/python'
expected_html='98a78a1cd1ca8748d12f206ec5f5fe3562706b00057b84628343f22d36560241';expected_index='d368402cd6c249f45b6ad4e7d9156088bf634e2f6c07fd10fdd7826d1a47c2e2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(root/'index.html')==expected_html;assert sha(root/'data/map_pack/enrichment/index.json')==expected_index
command=[python,str(script),'--run','--output',str(out),'--expect-html-sha',expected_html,'--expect-index-sha',expected_index]
receipt={'argv':command,'cwd':str(root),'scriptSha256Before':sha(script),'expectedHtmlSha256':expected_html,'expectedIndexSha256':expected_index,'startedAtUnix':time.time(),'stdout':'stdout.log'}
with (out/'stdout.log').open('w') as log:
 process=subprocess.Popen(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
 receipt['pid']=process.pid;receipt['exitCode']=process.wait()
receipt.update(elapsedSeconds=round(time.time()-receipt['startedAtUnix'],3),scriptSha256After=sha(script),htmlSha256After=sha(root/'index.html'),indexSha256After=sha(root/'data/map_pack/enrichment/index.json'),stdoutSha256=sha(out/'stdout.log'))
report_path=out/'NORTH_TERRAIN_NATIVE.json'
if report_path.exists():
 receipt['reportSha256']=sha(report_path);report=json.loads(report_path.read_text());receipt['total']=report['total'];receipt['passed']=report['passed'];receipt['stage']=report['stage']
 if report.get('origin'):
  port=int(report['origin'].rsplit(':',1)[1]);s=socket.socket();s.settimeout(2)
  try:s.connect(('127.0.0.1',port));closed=False
  except (ConnectionRefusedError,TimeoutError):closed=True
  finally:s.close()
  (out/'POST_EXIT_PORT_CHECK.json').write_text(json.dumps({'port':port,'connectionRefusedAfterExit':closed,'scope':'Independent TCP observation after the exact native process completed.'},indent=2)+'\n')
(out/'EXECUTION_STATUS.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
raise SystemExit(receipt['exitCode'])
