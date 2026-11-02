#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile, hashlib
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'verification';O.mkdir(exist_ok=True);checks=[]
def ck(n,c,d=None):checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
def run(cmd):return subprocess.run(cmd,capture_output=True,text=True)
def grid(macro,bbox,offset=0,bad=False):
 vals=[]
 for y in range(5):
  for x in range(5):vals.append(round(offset+10+x*2+y*3,2))
 if bad:vals[12]=-99999
 return {'version':'0.39.0','macro':macro,'bbox':bbox,'width':5,'height':5,'rowOrder':'north-to-south','values':vals,'source':'RGE ALTI IGN','sourceResource':'ign_rge_alti_wld','sourceTitle':'Fixture RGE ALTI QA','license':'Licence Ouverte 2.0','verticalDatum':'NGF-IGN69'}
with tempfile.TemporaryDirectory() as td:
 root=Path(td);pack=root/'terrain';pack.mkdir();manifest={'version':'0.39.0','source':{'name':'RGE ALTI IGN','resource':'ign_rge_alti_wld','title':'Fixture RGE ALTI QA','license':'Licence Ouverte 2.0','verticalDatum':'NGF-IGN69'},'relay':'https://invalid.example','publicKey':'fixture','grid':{'width':5,'height':5,'rowOrder':'north-to-south','samplesPerRegion':25},'noData':{'minimumExclusive':-100,'maximumExclusive':9000},'regions':[{'macro':'macro_a','bbox':[0,0,1,1]},{'macro':'macro_b','bbox':[0,.5,1,1.5]}]}
 mp=root/'manifest.json';mp.write_text(json.dumps(manifest));(pack/'macro_a.json').write_text(json.dumps(grid('macro_a',[0,0,1,1],0,True)));(pack/'macro_b.json').write_text(json.dumps(grid('macro_b',[0,.5,1,1.5],1,False)))
 installer=ROOT/'tools/install_terrain_v039.py';audit=ROOT/'tools/audit_terrain_v039.py';report=root/'audit.json'
 r=run([sys.executable,str(installer),'--manifest',str(mp),'--output',str(pack),'--verify-only']);ck('verify-only accepts valid fixtures',r.returncode==0,{'stdout':r.stdout,'stderr':r.stderr})
 ir=json.loads((pack/'install_terrain_v039_report.json').read_text());ck('installer sanitises bad sentinel',ir['validPoints']==49 and ir['missingPoints']==1,ir)
 clean=json.loads((pack/'macro_a.json').read_text());ck('sentinel persisted as null',clean['values'][12] is None,clean['values'][10:15])
 r=run([sys.executable,str(audit),'--manifest',str(mp),'--pack',str(pack),'--output',str(report),'--overlap-steps','7']);ck('audit accepts complete pack',r.returncode==0,{'stdout':r.stdout,'stderr':r.stderr})
 ar=json.loads(report.read_text());ck('audit reports two regions',ar['complete'] and ar['validRegions']==2 and ar['missingRegions']==0 and ar['invalidRegions']==0,ar);ck('overlap diagnostic produced',len(ar['overlaps'])==1 and ar['overlaps'][0]['samples']>0,ar['overlaps'])
 # Missing file is not silently accepted.
 (pack/'macro_b.json').unlink();r=run([sys.executable,str(audit),'--manifest',str(mp),'--pack',str(pack),'--output',str(report)]);ar2=json.loads(report.read_text());ck('missing terrain is reported',r.returncode==2 and ar2['missingRegions']==1 and not ar2['complete'],ar2)
 # Malformed payload is invalid, never interpreted as flat official terrain.
 (pack/'macro_b.json').write_text('<html>error</html>');r=run([sys.executable,str(audit),'--manifest',str(mp),'--pack',str(pack),'--output',str(report)]);ar3=json.loads(report.read_text());ck('HTML disguised as terrain is rejected',r.returncode==2 and ar3['invalidRegions']==1,ar3['invalid'])
rep={'version':'0.39.0','passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'checks':checks,'scope':'Local controlled terrain fixtures. No network used. Tests installer sanitisation, verify-only, overlap audit, missing files and malformed JSON rejection.'};(O/'QA_TERRAIN_TOOLS_V039.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total']}));raise SystemExit(bool(rep['failed']))
