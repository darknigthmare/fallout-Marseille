from pathlib import Path
import json,math,re,unicodedata,collections,time
root=Path('/workspace/fallout-Marseille');out=Path(__file__).parent
idx=json.loads((root/'data/map_pack/city/index.json').read_bytes());seen=set();counts=collections.Counter();examples=[];started=time.monotonic()
def project(lon,lat):
 e=.0818191910428158;n=.725607765053267;c=11754255.426096;phi=math.radians(lat);s=math.sin(phi);l=math.log(math.tan(math.pi/4+phi/2)*((1-e*s)/(1+e*s))**(e/2));r=c*math.exp(-n*l);g=n*(math.radians(lon)-math.radians(3));return[700000+r*math.sin(g),12655612.049876-r*math.cos(g)]
def num(v):
 try:n=float(v);return n if math.isfinite(n) else None
 except:return None
def inside(rings,x,z):
 def ring(r):
  yes=False
  for j in range(len(r)):
   a,b=r[j-1],r[j]
   if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:yes=not yes
  return yes
 return ring(rings[0]) and not any(ring(r) for r in rings[1:])
def clearance(rings,x,z):
 if not inside(rings,x,z):return -1
 d=math.inf
 for r in rings:
  for j in range(len(r)):
   a,b=r[j-1],r[j];dx,dz=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz or 1)));d=min(d,math.hypot(x-a[0]-t*dx,z-a[1]-t*dz))
 return d
for tile in idx['tiles']:
 for f in json.loads((root/tile['path']).read_bytes())['features']:
  p=f['properties'];id=p['sourceId']
  if p['kind']!='building' or id in seen:continue
  seen.add(id)
  for poly in f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else[f['geometry']['coordinates']]:
   outer=[project(c[0],c[1]) for c in poly[0]];lengths=[math.dist(outer[j-1],outer[j]) for j in range(1,len(outer))]
   if max(lengths,default=0)>=1.6:continue
   counts['noEdge16']+=1
   if max(lengths,default=0)<1.45:counts['noEdge145']+=1
   g,r,h,n=[num(p.get(k)) for k in ['altitude_minimale_sol','altitude_maximale_toit','hauteur','nombre_d_etages']]
   height=r-g if g is not None and r is not None and 0<r-g<=1000 else h if h is not None and .1<=h<=1000 else n*3 if n is not None and .1<=n<=200 else 6
   label=' '.join(str(p.get(k) or'') for k in ['nature','usage_1','usage_2','building','amenity','shop']).lower();label=''.join(c for c in unicodedata.normalize('NFD',label) if not unicodedata.combining(c));style='religious' if re.search('religieu|eglise|chapelle|cathedral|church|mosque|synagogue',label) else 'industrial' if re.search('industri|agricol|entrepot|warehouse|hangar|serre|greenhouse',label) else 'other'
   floors=int(n) if n is not None and n.is_integer() and 1<=n<=200 else max(1,math.floor(height/(4.2 if style=='industrial' else 3.05)+.5))
   xs=[c[0] for c in outer];zs=[c[1] for c in outer];w,d=max(xs)-min(xs),max(zs)-min(zs)
   enough=height/floors>=1.95-1e-7;wide=min(w,d)>=2
   if enough:counts['heightPerFloorAtLeast195cmWithEPS']+=1
   if enough and wide:
    counts['heightAndBBoxAtLeast2m']+=1
    if max(lengths)<1.45:counts['heightAndBBoxNoEdge145']+=1
    rings=[[project(c[0],c[1]) for c in ring] for ring in poly];center=[(max(xs)+min(xs))/2,(max(zs)+min(zs))/2];point=center if clearance(rings,*center)>=.43 else None
    if point is None:
     for j in range(64):
      if point:break
      for i in range(64):
       q=[min(xs)+w*(i+.5)/64,min(zs)+d*(j+.5)/64]
       if clearance(rings,*q)>=.43:point=q;break
    if point:counts['heightBBoxAndActorClearance043']+=1
    else:counts['heightBBoxButNoActorClearanceFound']+=1
    examples.append({'id':id,'path':tile['path'],'cleabs':p.get('cleabs'),'height':height,'levels':floors,'heightPerFloor':height/floors,'bboxMetres':[w,d],'maxEdgeLength':max(lengths),'noEdge145':max(lengths)<1.45,'actorPoint':point,'actorClearance':clearance(rings,*point) if point else None,'nature':p.get('nature'),'usage_1':p.get('usage_1')})
r={'scope':'Pinned source corpus; geometric actor compatibility only, not proof of actual habitable use or access. Source floor count or baseline estimated count, boundary EPS1e-7; exact point-in-polygon/segment clearance, center then bounded64x64search.','counts':dict(counts),'examples':examples,'seconds':round(time.monotonic()-started,3)}
(out/'CURVED_ELIGIBILITY.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'counts':dict(counts),'seconds':r['seconds'],'sample':next((x for x in examples if x['id']=='batiment.9375075'),None)},ensure_ascii=False))
