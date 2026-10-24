from pathlib import Path
import json,math,collections,heapq,time,re,unicodedata
root=Path('/workspace/fallout-Marseille');out=Path(__file__).parent
index=json.loads((root/'data/map_pack/city/index.json').read_bytes());seen=set();counts=collections.Counter();uses=collections.Counter();natures=collections.Counter();levels=collections.Counter();height_bins=collections.Counter();area_bins=collections.Counter();representatives={};largest=[];complexest=[];tallest=[];many_components=[];low_rooms=[];limit_examples=[]
def project(lon,lat):
 e=.0818191910428158;n=.725607765053267;c=11754255.426096;phi=math.radians(lat);s=math.sin(phi)
 l=math.log(math.tan(math.pi/4+phi/2)*((1-e*s)/(1+e*s))**(e/2));r=c*math.exp(-n*l);g=n*(math.radians(lon)-math.radians(3))
 return [700000+r*math.sin(g),12655612.049876-r*math.cos(g)]
def number(v):
 try:
  n=float(v)
  return n if math.isfinite(n) else None
 except (TypeError,ValueError):return None
def signed(r):
 x,z=r[0];return sum((r[i-1][0]-x)*(r[i][1]-z)-(r[i][0]-x)*(r[i-1][1]-z) for i in range(len(r)))/2
def ranked(heap, score, item, maxn=15):
 if len(heap)<maxn:heapq.heappush(heap,(score,item['id'],item))
 elif score>heap[0][0]:heapq.heapreplace(heap,(score,item['id'],item))
started=time.monotonic()
for di,d in enumerate(index['tiles']):
 rows=json.loads((root/d['path']).read_bytes())['features']
 for f in rows:
  p=f['properties']
  if p['kind']!='building':continue
  id=p['sourceId']
  if id in seen:continue
  seen.add(id);counts['uniqueBuildings']+=1
  geometry=f['geometry'];polys=geometry['coordinates'] if geometry['type']=='MultiPolygon' else[geometry['coordinates']]
  counts['multipartBuildings' if len(polys)>1 else 'singlepartBuildings']+=1
  counts['buildingComponents']+=len(polys);uses[str(p.get('usage_1'))]+=1;natures[str(p.get('nature'))]+=1
  ground,roof,h,n=(number(p.get(k)) for k in ['altitude_minimale_sol','altitude_maximale_toit','hauteur','nombre_d_etages'])
  if ground is None:counts['missingAbsoluteGround']+=1
  if h is None or not .1<=h<=1000:counts['missingPositiveDeclaredHeight']+=1
  if ground is not None and roof is not None and 0<roof-ground<=1000:height=roof-ground;basis='absolute-roof-ground'
  elif h is not None and .1<=h<=1000:height=h;basis='hauteur'
  elif n is not None and .1<=n<=200:height=n*3;basis='levels-estimate'
  else:height=6;basis='default-estimate'
  counts['heightBasis:'+basis]+=1
  declared=n is not None and n.is_integer() and 1<=n<=200
  if p.get('nombre_d_etages') is not None:
   counts['nonNullSourceLevels']+=1
   if not declared:
    counts['nonNullInvalidSourceLevels']+=1
    counts['invalidSourceLevelsValue:'+repr(p.get('nombre_d_etages'))]+=1
    if len(limit_examples)<12:limit_examples.append({'id':id,'cleabs':p.get('cleabs'),'path':d['path'],'value':p.get('nombre_d_etages'),'heightM':height})
  if n is not None:levels[str(n)]+=1
  label=' '.join(str(p.get(k) or '') for k in ['nature','usage_1','usage_2','building','amenity','shop']).lower()
  label=''.join(c for c in unicodedata.normalize('NFD',label) if not unicodedata.combining(c))
  style='religious' if re.search('religieu|eglise|chapelle|cathedral|church|mosque|synagogue',label) else 'industrial' if re.search('industri|agricol|entrepot|warehouse|hangar|serre|greenhouse',label) else 'commercial' if re.search('commercial|commerce|magasin|shop|retail|restaurant',label) else 'civic' if re.search('public|mairie|administr|ecole|school|hopital|hospital|musee|museum|gare|station',label) else 'residential'
  floors=int(n) if declared else max(1,math.floor(height/(4.2 if style=='industrial' else 3.05)+.5))
  if height<1.95:counts['heightBelowActorMinimumBuildings']+=1
  elif height/floors<1.95:
   counts['declaredOrDerivedFloorsTooLowBuildings']+=1
   if height/floors>=1.95-1e-7:counts['rejectedOnlyByFloatThresholdAt195cm']+=1
  if declared and height/floors>8:counts['declaredFloorsOver8m']+=1
  total_area=0;max_nodes=0;ring_total=0;node_total=0;has_holes=False;component_metrics=[]
  for poly in polys:
   rings=[]
   for ring in poly:
    rings.append([project(c[0],c[1]) for c in ring])
   area=max(0,abs(signed(rings[0]))-sum(abs(signed(r)) for r in rings[1:]));total_area+=area
   pts=[v for ring in rings for v in ring];xs=[v[0] for v in pts];ys=[v[1] for v in pts];width=max(xs)-min(xs);depth=max(ys)-min(ys)
   nodes=sum(max(0,len(r)-1) for r in rings);max_nodes=max(max_nodes,max(len(r)-1 for r in rings));ring_total+=len(rings);node_total+=nodes;has_holes|=len(rings)>1
   if min(width,depth)<.86:counts['componentsBBoxNarrowerThanActorDiameter']+=1
   if len(rings)>128:counts['componentsOverInteriorRingLimit']+=1
   if nodes>8192:counts['componentsOverInteriorNodeLimit']+=1
   if max(len(r)-1 for r in rings)>2048:counts['componentsOverSourceProjectionRingLimit2048']+=1
   if nodes>16384 or len(rings)>256:counts['componentsOverFacadeLimits']+=1
   if area<.02:counts['componentsBelowInteriorAreaMinimum']+=1
   if max(width,depth)>10000:counts['componentsOverSavedInteriorExtentLimit']+=1
   bay_lo,bay_hi=(4.8,4.8) if style=='industrial' else (4.2,4.2) if style=='religious' else (2.8,3.29)
   def potential(bay):return sum(min(160,math.floor(math.hypot(r[i][0]-r[i-1][0],r[i][1]-r[i-1][1])/bay))*floors for r in rings for i in range(1,len(r)) if math.hypot(r[i][0]-r[i-1][0],r[i][1]-r[i-1][1])>=1.45)
   lower,upper=potential(bay_hi),potential(bay_lo)
   if lower>4096:counts['componentsGuaranteedOverMaxFacadeOpeningPlan4096']+=1
   if upper>4096:counts['componentsPossiblyOverMaxFacadeOpeningPlan4096']+=1
   if lower>85:counts['componentsGuaranteedOverHighQualityOpeningBudgetApprox85']+=1
   if upper>85:counts['componentsPossiblyOverHighQualityOpeningBudgetApprox85']+=1
   component_metrics.append({'areaM2':round(area,3),'bboxMetres':[round(width,3),round(depth,3)],'rings':len(rings),'nodes':nodes,'potentialOpeningCandidateBounds':[lower,upper]})
  counts['buildingsWithCourtyards']+=int(has_holes)
  if total_area>1000:counts['buildingsOver1000m2']+=1
  if total_area>10000:counts['buildingsOver10000m2']+=1
  if total_area>50000:counts['buildingsOver50000m2']+=1
  item={'id':id,'cleabs':p.get('cleabs'),'path':d['path'],'nature':p.get('nature'),'usage_1':p.get('usage_1'),'heightM':round(height,4),'heightBasis':basis,'levels':floors,'levelsDeclared':declared,'sourceLevels':p.get('nombre_d_etages'),'levelHeightM':round(height/floors,4),'areaM2':round(total_area,3),'components':component_metrics,'ringCount':ring_total,'nodeCount':node_total,'rawMaxRingNodes':max_nodes}
  ranked(largest,total_area,item);ranked(complexest,node_total,item);ranked(tallest,height,item);ranked(many_components,len(polys),item)
  if height>=1.95 and height/floors<1.95 and len(low_rooms)<20:low_rooms.append(item)
  for key in [style,'nature:'+str(p.get('nature')),'usage:'+str(p.get('usage_1'))]:
   if key not in representatives or representatives[key]['areaM2']<total_area:representatives[key]=item
 if di%40==0:print(di,len(seen),flush=True)
r={'scope':'Read-only statistical audit of actual pinned IGN city vectors; area and dimensions projected by the exact current engine Lambert-93 formula (copied without modification), translation-stable area arithmetic; source IDs deduplicated, returned border objects included','indexSha256':__import__('hashlib').sha256((root/'data/map_pack/city/index.json').read_bytes()).hexdigest(),'counts':dict(counts),'primaryUses':dict(uses),'natures':dict(natures),'sourceLevelsDistribution':dict(levels),'largest': [x[2] for x in sorted(largest,reverse=True)],'complexest':[x[2] for x in sorted(complexest,reverse=True)],'tallest':[x[2] for x in sorted(tallest,reverse=True)],'mostComponents':[x[2] for x in sorted(many_components,reverse=True)],'floorHeightRejectedExamples':low_rooms,'nonNullInvalidLevelExamples':limit_examples,'largestByUseOrNature':representatives,'seconds':round(time.monotonic()-started,3)}
(out/'SOURCE_SHAPES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'counts':dict(counts),'uses':dict(uses),'natures':dict(natures),'seconds':r['seconds']},ensure_ascii=False))
