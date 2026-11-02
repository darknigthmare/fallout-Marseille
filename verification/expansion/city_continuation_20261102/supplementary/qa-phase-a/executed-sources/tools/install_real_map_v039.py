#!/usr/bin/env python3
"""Install the v0.39 real-map pack: vector tiles and/or RGE ALTI terrain grids."""
from __future__ import annotations
import argparse,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(cmd):
 print('+',' '.join(map(str,cmd)),flush=True);return subprocess.run(cmd).returncode
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',choices=['all','vector','base','cadastre','terrain'],default='all');p.add_argument('--macro',default='all');p.add_argument('--endpoint',choices=['auto','cloud','direct'],default='cloud');p.add_argument('--workers',type=int,default=8);p.add_argument('--verify-only',action='store_true');p.add_argument('--dry-run',action='store_true');a=p.parse_args();started=time.time();steps=[]
 if a.source in ('all','vector','base','cadastre'):
  src='all' if a.source in ('all','vector') else a.source;cmd=[sys.executable,str(ROOT/'tools/install_real_map_v038.py'),'--source',src,'--macro',a.macro,'--endpoint',a.endpoint,'--workers',str(a.workers)]
  if a.verify_only:cmd.append('--verify-only')
  if a.dry_run:cmd.append('--dry-run')
  rc=run(cmd);steps.append({'name':'vector','returncode':rc})
 if a.source in ('all','terrain'):
  cmd=[sys.executable,str(ROOT/'tools/install_terrain_v039.py'),'--macro',a.macro,'--workers',str(min(a.workers,8))]
  if a.verify_only:cmd.append('--verify-only')
  if a.dry_run:cmd.append('--dry-run')
  rc=run(cmd);steps.append({'name':'terrain','returncode':rc})
 report={'version':'0.39.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'macro':a.macro,'endpoint':a.endpoint,'verifyOnly':a.verify_only,'dryRun':a.dry_run,'seconds':round(time.time()-started,2),'steps':steps,'ok':all(s['returncode']==0 for s in steps)}
 (ROOT/'data/map_pack/install_v039_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
