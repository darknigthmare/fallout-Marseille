"""Record an actual child exit and immutable executed script/log/report."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import time


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--report',required=True)
    p.add_argument('--freeze',type=Path)
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();command=a.command
    if command and command[0]=='--':command=command[1:]
    assert command
    a.output.mkdir(parents=True,exist_ok=True)
    script=Path(command[1]);script=script if script.is_absolute() else a.repo/script
    frozen=json.loads(a.freeze.read_text()) if a.freeze else {}
    assert all(sha(a.repo/n)==h for n,h in frozen.items()),'Runtime differs before execution'
    before=sha(script);shutil.copy2(script,a.output/('EXECUTED_'+script.name))
    started=time.time();log=a.output/'stdout.log'
    with log.open('w') as f:
        child=subprocess.Popen(command,cwd=a.repo,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        for line in child.stdout:
            f.write(line);f.flush();print(line,end='',flush=True)
        code=child.wait()
    changed=[n for n,h in frozen.items() if not (a.repo/n).is_file() or sha(a.repo/n)!=h]
    report=a.output/a.report
    receipt={'argv':command,'cwd':str(a.repo),'childPid':child.pid,'exitCode':code,'startedAtEpoch':started,'durationSeconds':time.time()-started,'scriptSha256':before,'scriptUnchanged':before==sha(script),'reportSha256':sha(report) if report.is_file() else None,'logSha256':sha(log),'html_sha256':sha(a.repo/'index.html'),'runtimeChanged':changed,'runtimeInputCount':len(frozen)}
    (a.output/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)
    return code or int(bool(changed) or not receipt['scriptUnchanged'])


if __name__=='__main__':raise SystemExit(main())
