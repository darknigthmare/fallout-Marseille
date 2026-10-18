#!/usr/bin/env python3
from pathlib import Path
import argparse,json,math,hashlib,html
R=Path(__file__).resolve().parents[1]
def tile(lat,lon,z):
 n=2**z;return int((lon+180)/360*n),int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
def meters(a,b):
 R0=6378137;lat=math.radians((a[0]+b[0])/2);return math.hypot(math.radians(a[1]-b[1])*R0*math.cos(lat),math.radians(a[0]-b[0])*R0)
def required(path,z,radius,step):
 out=set()
 for a,b in zip(path,path[1:]):
  n=max(1,math.ceil(meters(a,b)/step))
  for i in range(n+1):
   t=i/n;x,y=tile(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,z)
   for dx in range(-radius,radius+1):
    for dy in range(-radius,radius+1):out.add((z,x+dx,y+dy))
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pack',type=Path,default=R/'data/map_pack');ap.add_argument('--require-local',action='store_true');a=ap.parse_args()
 rows=[];all_ok=True
 for f in sorted((R/'data/corridors').glob('*.json')):
  p=json.loads(f.read_text());base=required(p['path'],14,1,650);cad=required(p['path'],16,0,240)
  bp=[a.pack/'base'/str(z)/str(x)/f'{y}.pbf' for z,x,y in base];cp=[a.pack/'cadastre'/str(z)/str(x)/f'{y}.pbf' for z,x,y in cad]
  local=sum(x.exists() for x in bp+cp);need=len(bp)+len(cp);geom=len(p['path'])==p['pathPoints'] and p['status']=='certified' and p['tileErrors']==0 and p['startSnapM']<50 and p['endSnapM']<50
  complete=local==need;ok=geom and (complete or not a.require_local);all_ok&=ok
  rows.append({'id':p['id'],'label':p['label'],'status':p['status'],'distanceM':p['distanceM'],'pathPoints':len(p['path']),'baseRequired':len(base),'cadastreRequired':len(cad),'localFiles':local,'requiredFiles':need,'localComplete':complete,'geometryValid':geom,'ok':ok,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 rep={'version':'0.40.0','pack':str(a.pack),'requireLocal':a.require_local,'ok':all_ok,'corridors':rows,'scope':'Certified proof geometry plus optional verification that every vector tile needed around each path is installed locally.'}
 O=R/'verification';O.mkdir(exist_ok=True);(O/'AUDIT_CORRIDORS_V040.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n')
 trs=''.join(f"<tr><td>{html.escape(r['label'])}</td><td>{r['distanceM']/1000:.2f} km</td><td>{r['pathPoints']}</td><td>{r['localFiles']}/{r['requiredFiles']}</td><td>{'OK' if r['ok'] else 'À compléter'}</td></tr>" for r in rows)
 (O/'AUDIT_CORRIDORS_V040.html').write_text(f"<!doctype html><meta charset=utf-8><title>Audit corridors v0.40</title><style>body{{background:#0b100c;color:#dfe6d3;font:16px system-ui;padding:30px}}table{{border-collapse:collapse}}td,th{{border:1px solid #53624e;padding:10px}}h1{{color:#e9dda9}}</style><h1>Audit corridors v0.40</h1><p>Pack : {html.escape(str(a.pack))} · exigence locale : {a.require_local}</p><table><tr><th>Corridor</th><th>Distance</th><th>Points</th><th>Fichiers locaux</th><th>État</th></tr>{trs}</table>",encoding='utf-8')
 print(json.dumps({'ok':all_ok,'corridors':[{k:r[k] for k in ['id','localFiles','requiredFiles','geometryValid','ok']} for r in rows]},ensure_ascii=False));raise SystemExit(0 if all_ok else 1)
if __name__=='__main__':main()
