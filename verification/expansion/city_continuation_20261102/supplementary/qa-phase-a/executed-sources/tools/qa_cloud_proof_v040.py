#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1];O=R/'verification';checks=[]
def ck(n,c,d=None):checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
proof=json.loads((O/'CORRIDORS_CLOUD_V040.json').read_text());sec=json.loads((O/'SECURITE_CORRIDORS_V040.json').read_text())
ck('deux corridors acquis',proof['complete'] and proof['count']==2,{'count':proof['count'],'complete':proof['complete']})
expected={'aubagne_marseille':(23701,72,78,50778,211820,285518,['geo_huveaune','geo_marseille']),'aubagne_laciotat':(22740,109,43,14365,84367,100476,['geo_huveaune','geo_laciotat'])}
RADIUS=6378137
def meters(a,b):
 lat=(a[0]+b[0])*.5*math.pi/180;return math.hypot((a[1]-b[1])*math.pi/180*RADIUS*math.cos(lat),(a[0]-b[0])*math.pi/180*RADIUS)
for id,(distance,points,tiles,features,nodes,edges,macros) in expected.items():
 p=proof['corridors'][id];path=p['path'];segs=[meters(a,b) for a,b in zip(path,path[1:])]
 ck(id+' certifié',p['status']=='certified' and p['distanceM']==distance,p)
 ck(id+' graphe documenté',p['pathPoints']==points and p['tileCount']==tiles and p['roadFeatures']==features and p['graphNodes']==nodes and p['graphEdges']==edges)
 ck(id+' extrémités proches',p['startSnapM']<50 and p['endSnapM']<50,{'start':p['startSnapM'],'end':p['endSnapM']})
 ck(id+' macro-séquence',p['macroSequence']==macros,p['macroSequence'])
 ck(id+' géométrie cohérente',len(path)==points and max(segs)<1300 and sum(segs)>distance*.65,{'points':len(path),'maxSegment':max(segs),'polyline':sum(segs),'graphDistance':distance})
 f=R/'data/corridors'/f'{id}.json';ck(id+' snapshot lisible',f.exists() and hashlib.sha256(f.read_bytes()).hexdigest()==p['localSha256'],p['localSha256'])
ck('bucket privé',sec['bucket']['public'] is False and sec['verifyJwt'] is True,sec['bucket'])
ck('table protégée',sec['table']['rls'] and not sec['table']['anonSelect'] and not sec['table']['authenticatedSelect'],sec['table'])
ck('construction figée',sec['buildRouteStatus']==410 and sec['temporaryExportStatus']==410)
rep={'version':'0.40.0','passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'checks':checks,'scope':'Consistency checks over locally captured Supabase corridor proofs, embedded snapshots and security state.'};(O/'QA_CLOUD_PROOF_V040.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total']}));raise SystemExit(bool(rep['failed']))
