from pathlib import Path
import json,collections,math,heapq
def project(lon,lat):
 e=.0818191910428158;n=.725607765053267;c=11754255.426096;phi=math.radians(lat);s=math.sin(phi)
 l=math.log(math.tan(math.pi/4+phi/2)*((1-e*s)/(1+e*s))**(e/2));r=c*math.exp(-n*l);g=n*(math.radians(lon)-math.radians(3))
 return [700000+r*math.sin(g),12655612.049876-r*math.cos(g)]
root=Path('/workspace/fallout-Marseille');out=Path(__file__).parent;i=json.loads((root/'data/map_pack/city/index.json').read_bytes());seen=set();tab=collections.Counter();examples={};near=[];edgeCounts=collections.Counter();edgeLargest=[];noDoors=[]
for d in i['tiles']:
 for f in json.loads((root/d['path']).read_bytes())['features']:
  p=f['properties'];id=p['sourceId']
  if p['kind']!='building' or id in seen:continue
  seen.add(id)
  if p.get('nature')=='Industriel, agricole ou commercial':
   use=str(p.get('usage_1'));tab[use]+=1
   if use not in examples:examples[use]={'id':id,'path':d['path'],'properties':p}
  polys=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else[f['geometry']['coordinates']]
  for poly in polys:
   outer=[project(c[0],c[1]) for c in poly[0]]
   long=sum(math.hypot(outer[j][0]-outer[j-1][0],outer[j][1]-outer[j-1][1])>=1.6 for j in range(1,len(outer)))
   edgeCounts['components']+=1
   if long>64:edgeCounts['outerEdgesAtLeast1_6mOver64']+=1
   if long==0:
    edgeCounts['noOuterEdgeAtLeast1_6m']+=1
    xs=[a[0] for a in outer];ys=[a[1] for a in outer]
    if min(max(xs)-min(xs),max(ys)-min(ys))>=2 and len(noDoors)<12:noDoors.append({'id':id,'path':d['path'],'properties':p,'bboxMetres':[max(xs)-min(xs),max(ys)-min(ys)],'outerEdges':len(outer)-1})
   item={'id':id,'path':d['path'],'cleabs':p.get('cleabs'),'longOuterEdges':long,'outerNodes':len(outer)-1,'usage_1':p.get('usage_1'),'nature':p.get('nature')}
   if len(edgeLargest)<15:heapq.heappush(edgeLargest,(long,id,item))
   elif long>edgeLargest[0][0]:heapq.heapreplace(edgeLargest,(long,id,item))
  n=p.get('nombre_d_etages');g=p.get('altitude_minimale_sol');r=p.get('altitude_maximale_toit')
  if isinstance(n,(int,float)) and 1<=n<=200 and isinstance(g,(int,float)) and isinstance(r,(int,float)) and 0<r-g<=1000 and 1.95-1e-7<=(r-g)/n<1.95:
   near.append({'id':id,'path':d['path'],'ground':g,'roof':r,'height':r-g,'levels':n,'perLevel':(r-g)/n,'nature':p.get('nature'),'usage_1':p.get('usage_1')})
r={'scope':'Exact attribute cross-tabs, deduplicated actual source IDs','ambiguousNaturePrimaryUses':dict(tab),'examples':examples,'falseStrict195BoundaryCases':near,'outerEdgeCounts':dict(edgeCounts),'mostLongOuterEdges':[a[2] for a in sorted(edgeLargest,reverse=True)],'noDoorDespiteBBoxAtLeast2mExamples':noDoors}
(out/'ATTRIBUTE_CROSS_TABS.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'crossTab':dict(tab),'floatCases':len(near),'nearExamples':near[:4],'outerEdgeCounts':dict(edgeCounts),'maxEdge':max(edgeLargest)[2]},ensure_ascii=False))
