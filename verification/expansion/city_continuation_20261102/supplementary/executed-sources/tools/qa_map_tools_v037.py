#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, tempfile, subprocess, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from install_real_map_v037 import validate
checks=[]
def ck(name,cond,detail=None):
 checks.append({'name':name,'ok':bool(cond),'detail':detail});print(('OK ' if cond else 'FAIL ')+name,flush=True)
def vi(n:int)->bytes:
 out=bytearray()
 while True:
  b=n&127;n>>=7;out.append(b|(128 if n else 0))
  if not n:return bytes(out)
def zz(n:int)->int:return (n<<1)^(n>>63)
def field(num:int,wire:int,payload):
 h=vi((num<<3)|wire)
 if wire==0:return h+vi(int(payload))
 return h+vi(len(payload))+payload
def packed(vals):return b''.join(vi(v) for v in vals)
def value_string(s):return field(1,2,s.encode())
def feature(fid,typ,geom,tags=(0,0)):return field(1,0,fid)+field(2,2,packed(tags))+field(3,0,typ)+field(4,2,packed(geom))
def layer(name,features,key='class',value='primary'):
 raw=field(15,0,2)+field(1,2,name.encode())
 for f in features:raw+=field(2,2,f)
 raw+=field(3,2,key.encode())+field(4,2,value_string(value))+field(5,0,4096)
 return field(3,2,raw)
line=[9,zz(0),zz(2048),10,zz(4096),zz(0)]
BASE=layer('transportation',[feature(1,2,line)])
poly=[9,zz(200),zz(200),26,zz(1200),0,0,zz(1200),zz(-1200),0,15]
CAD=layer('batiments',[feature(2,3,poly),feature(3,3,poly)],'nature','dur')
with tempfile.TemporaryDirectory() as td:
 td=Path(td);pack=td/'pack';pack.mkdir();manifest=td/'manifest.json';out=td/'audit.json'
 rows=[]
 for source,z,x,y,data in [('base',14,8437,6001,BASE),('base',14,8438,6001,BASE),('cadastre',16,33750,24006,CAD)]:
  local=f'data/map_pack/{source}/{z}/{x}/{y}.pbf';p=pack/f'{source}/{z}/{x}/{y}.pbf';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);rows.append({'source':source,'z':z,'x':x,'y':y,'key':f'{z}/{x}/{y}','local':local,'macros':['geo_marseille']})
 manifest.write_text(json.dumps({'version':'0.37.0','tiles':rows}))
 cp=subprocess.run([sys.executable,str(ROOT/'tools/audit_real_map_v037.py'),'--manifest',str(manifest),'--pack',str(pack),'--output',str(out)],capture_output=True,text=True)
 audit=json.loads(out.read_text())
 ck('auditor accepts controlled pack',cp.returncode==0,{'rc':cp.returncode,'stderr':cp.stderr})
 ck('auditor validates three PBF',audit['valid']==3 and audit['invalid']==0,audit)
 ck('auditor matches cross-tile road',audit['transportTopology']['matchedSeams']>=1,audit['transportTopology'])
 ck('auditor does not invent a seam defect',audit['transportTopology']['unpairedWithNeighborLoaded']==0,audit['transportTopology'])
 ck('auditor detects exact cadastre duplicate',audit['buildings']['exactDuplicateFootprints']==1,audit['buildings'])
 ok,meta=validate(pack/'base/14/8437/6001.pbf');ck('installer validator accepts MVT',ok,meta)
 bad=td/'bad.pbf';bad.write_text('<html>not a tile</html>');ok2,meta2=validate(bad);ck('installer validator rejects HTML',not ok2,meta2)
 good_sha=hashlib.sha256(BASE).hexdigest();ok3,meta3=validate(pack/'base/14/8437/6001.pbf',good_sha);ck('installer validator checks SHA-256',ok3 and meta3['sha256']==good_sha,meta3)
report={'version':'0.37.0','passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'checks':checks,'scope':'Controlled local MVT fixtures. No geographic fidelity claim.'}
(ROOT/'verification/QA_MAP_TOOLS_V037.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'failed':report['failed'],'total':report['total']}))
raise SystemExit(bool(report['failed']))
