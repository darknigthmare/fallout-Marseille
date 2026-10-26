from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse,hashlib,json,shutil,subprocess,sys,threading,time,socket,os,signal
ROOT=Path('/workspace/fallout-Marseille')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['continuation','chems','controller']);p.add_argument('--output',type=Path,required=True);p.add_argument('--expect-html-sha',required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
 assert sha(ROOT/'index.html')==a.expect_html_sha
 name={'continuation':'continuation_native.py','chems':'chems_native.py','controller':'controller_browser.py'}[a.kind];script=ROOT/'tests/expansion'/name;script_hash=sha(script)
 inputs={str(q.relative_to(ROOT)):sha(q) for q in [ROOT/'index.html',script,ROOT/'tools/serve_game.py']+list((ROOT/'src/v050').glob('*.js'))}
 server=thread=None
 try:
  command=[sys.executable,str(script)]
  if a.kind=='controller':
   sys.path.insert(0,str(ROOT/'tools'));from serve_game import GameHandler
   server=ThreadingHTTPServer(('127.0.0.1',0),GameHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_port)+'/index.html?skipboot=1'
   command+=['--url',url,'--output',str(out),'--expected-html-sha256',a.expect_html_sha]
   shutil.copyfile(script,out/'EXECUTED_CONTROLLER_BROWSER.py')
  else:
   command+=['--run','--output',str(out),'--expect-html-sha',a.expect_html_sha]
   if a.kind=='continuation':
    for flag,target in [('architecture','data/map_pack/architecture/index.json'),('lore','src/v050/10_lore_continuity.js'),('power','src/v050/11_power_armor.js'),('iconic','src/v050/12_iconic_ecosystem.js')]:command+=['--expect-'+flag+'-sha',sha(ROOT/target)]
   else:command+=['--expect-chems-sha',sha(ROOT/'src/v050/15_chemistry.js')]
  (out/'COMMAND.json').write_text(json.dumps({'command':command,'cwd':str(ROOT),'executedScriptSha256':script_hash,'htmlSha256':a.expect_html_sha},indent=2)+'\n')
  started=time.monotonic()
  with (out/'EXECUTION.log').open('w') as log:
   process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:code=process.wait(timeout=900)
   except subprocess.TimeoutExpired:
    os.killpg(process.pid,signal.SIGTERM)
    try:code=process.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);code=process.wait()
 finally:
  if server:port=server.server_port;server.shutdown();server.server_close();thread.join(timeout=5)
 report_name={'continuation':'CONTINUATION_NATIVE.json','chems':'CHEMS_NATIVE.json','controller':'CONTROLLER_BROWSER.json'}[a.kind];report=out/report_name
 unchanged=all(sha(ROOT/n)==h for n,h in inputs.items())
 status={'exitCode':code,'processFinished':True,'wrapperSha256':sha(Path(__file__)),'method':'Actual subprocess return code and exact log captured automatically by the coordinator wrapper.','htmlSha256':a.expect_html_sha,'elapsedSeconds':round(time.monotonic()-started,3),'unchangedInputs':unchanged,'linkedFiles':[{'file':q.name,'sha256':sha(q),'bytes':q.stat().st_size} for q in [report,out/'EXECUTION.log'] if q.exists()]}
 (out/'EXECUTION_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
 if a.kind=='controller' and report.exists():
  identity={'capturedAfterExecution':True,'exitCode':code,'scriptSha256':script_hash,'reportSha256':sha(report),'logSha256':sha(out/'EXECUTION.log'),'sourceHashes':inputs,'method':'Actual subprocess status and exact report/log identities captured after execution; Gamepad API explicitly simulated.'}
  (out/'EXECUTION_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n')
 print(json.dumps(status),flush=True);return code if code else int(not unchanged)
if __name__=='__main__':raise SystemExit(main())
