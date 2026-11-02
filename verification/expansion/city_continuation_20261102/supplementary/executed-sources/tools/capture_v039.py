#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);HTML=(R/'JOUER_FALLOUT_MISTRAL_v0.39.html').read_text();MAN=json.loads((R/'data/map_pack/terrain/manifest_v039.json').read_text());shots=[];errors=[]
REGIONS=json.loads((O/'TERRAIN_CLOUD_V039.json').read_text())['regions']
STATUS={'service':'fallout-mistral-terrain-v039','version':'0.39.0','source':{'resource':'ign_rge_alti_wld','title':MAN['source']['title'],'license':'Licence Ouverte 2.0','verticalDatum':MAN['source']['verticalDatum']},'grid':{'width':161,'height':161},'expected':[r['macro'] for r in REGIONS],'count':8,'complete':True,'totalBytes':1260176,'totalValid':174944,'totalMissing':32424,'regions':[{'macro':r['macro'],'valid_points':r['valid'],'missing_points':r['missing'],'min_elevation':r['min'],'max_elevation':r['max'],'mean_elevation':r['mean'],'bytes':r['bytes']} for r in REGIONS]}
VECTOR={'service':'fallout-mistral-map-v038','version':'0.38.0','plan':{'base':367,'cadastre':5517,'total':5884},'cache':{'base':{'coordinates':367,'pbf':367,'empty':0,'bytes':29456613,'hits':31},'cadastre':{'coordinates':5517,'pbf':4190,'empty':1327,'bytes':57517126,'hits':1},'total':5884,'totalBytes':86973739,'totalEmpty':1327,'complete':True,'newest':'2026-09-19T01:51:42Z'}}
# Controlled terrain render fixture: a broad ridge and an explicit NoData corner.
vals=[]
for y in range(33):
 for x in range(33):
  dx=(x-16)/16;dy=(y-16)/16;z=25+210*math.exp(-(dx*dx*2.6+dy*dy*1.8))+45*dx
  vals.append(None if x<5 and y>25 else round(z,2))
GRID={'version':'0.39.0','macro':'geo_marseille','bbox':[43.22,5.285,43.34,5.51],'width':33,'height':33,'rowOrder':'north-to-south','values':vals,'source':'RGE ALTI IGN','sourceResource':'ign_rge_alti_wld','sourceTitle':MAN['source']['title'],'license':'Licence Ouverte 2.0','verticalDatum':MAN['source']['verticalDatum']}
# Factual coverage/elevation plan.
W,H=1500,1050;img=Image.new('RGB',(W,H),(13,19,15));d=ImageDraw.Draw(img)
try:F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',33);F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19);F3=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except:F=F2=F3=None
pad=90;left,bottom,right,top=5.235,43.105,5.775,43.44;xy=lambda lon,lat:(pad+(lon-left)/(right-left)*(W-2*pad),H-pad-(lat-bottom)/(top-bottom)*(H-2*pad));labels={'geo_marseille':'MARSEILLE','geo_huveaune':'HUVEAUNE','geo_garlaban':'GARLABAN','geo_calanques':'CALANQUES','geo_laciotat':'LA CIOTAT','geo_frioul':'FRIOUL','geo_etoile':'ÉTOILE','geo_saintebaume':'SAINTE-BAUME'}
d.text((pad,22),'FALLOUT : MISTRAL — RELIEF RGE ALTI v0.39',font=F,fill=(232,222,174));d.text((pad,64),'8 grilles officielles échantillonnées · 161 × 161 · 174 944 mesures · 32 424 NoData',font=F2,fill=(168,191,162))
for lon in [5.3,5.4,5.5,5.6,5.7]:x,_=xy(lon,bottom);d.line((x,pad,x,H-pad),fill=(48,65,52));d.text((x-22,H-pad+12),f'{lon:.1f}°E',font=F3,fill=(132,153,132))
for lat in [43.15,43.2,43.25,43.3,43.35,43.4]:_,y=xy(left,lat);d.line((pad,y,W-pad,y),fill=(48,65,52));d.text((12,y-9),f'{lat:.2f}°N',font=F3,fill=(132,153,132))
for i,r in enumerate(REGIONS):
 s,w,n,e=r['bbox'];x0,y1=xy(w,s);x1,y0=xy(e,n);col=(95+(i*37)%120,138+(i*23)%90,88+(i*51)%125);d.rectangle((x0,y0,x1,y1),outline=col,width=4);pct=r['valid']/(r['valid']+r['missing'])*100;d.multiline_text((x0+7,y0+6),f"{labels[r['macro']]}\n{r['min']:.0f}–{r['max']:.0f} m · {pct:.1f}%",font=F3,fill=(230,233,209),spacing=3)
d.rectangle((pad,H-72,W-pad,H-20),fill=(24,35,27));d.text((pad+12,H-64),'VECTORIEL 5 884/5 884 · RELIEF 8/8 · 1,26 Mo JSON · SOURCE ign_rge_alti_wld · NODATA CONSERVÉ',font=F2,fill=(236,224,174));coverage=O/'v039_01_plan_relief.png';img.save(coverage);shots.append((coverage,'Huit grilles RGE ALTI','Emprises, extrema et couverture mesurée des huit macro-régions.'))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate(r'''() => {const databases=new Map();function open(name,version=1){const req={result:null,error:null};setTimeout(()=>{let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}const db={get objectStoreNames(){return{contains:n=>state.stores.has(n)}},createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,finished=false;const maybe=()=>setTimeout(()=>{if(!pending&&!finished){finished=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{const store=state.stores.get(n),opts=state.options.get(n)||{};const request=fn=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.()}finally{pending--;maybe()}},0);return q};return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())}};maybe();return tx},close(){}};req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}})}''')
 def relay(route,req):
  u=req.url
  if u.endswith('/fallout-mistral-terrain-v039/status'):route.fulfill(status=200,content_type='application/json',body=json.dumps(STATUS),headers={'access-control-allow-origin':'*'});return
  if '/fallout-mistral-terrain-v039/terrain/geo_marseille' in u:route.fulfill(status=200,content_type='application/json',body=json.dumps(GRID),headers={'access-control-allow-origin':'*','etag':'"sha256-fixture"'});return
  if u.endswith('/fallout-mistral-map-v038/coverage'):route.fulfill(status=200,content_type='application/json',body=json.dumps(VECTOR),headers={'access-control-allow-origin':'*'});return
  route.continue_()
 p.route('**/fallout-mistral-terrain-v039/**',relay);p.route('**/fallout-mistral-map-v038/**',relay);p.set_content(HTML,wait_until='load');p.wait_for_timeout(2800);p.evaluate("window.__CAPSTORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__CAPSTORE[k]??null,setItem:(k,v)=>__CAPSTORE[k]=String(v),removeItem:k=>delete __CAPSTORE[k]}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):path=O/name;p.screenshot(path=str(path));shots.append((path,title,note));print('CAP',name,flush=True)
 shot('v039_02_menu.png','Menu v0.39','Le dossier de production annonce le relief officiel 8/8 sans prétendre intégrer la résolution native complète.')
 c('v039OpenStatus');p.wait_for_timeout(100);shot('v039_03_statut.png','État cartographique','Vectoriel 5 884/5 884, relief 8/8, mesures et NoData comptés séparément.');p.click('#v039StatusClose')
 c('v018LoadMacro','geo_marseille');p.wait_for_timeout(250);c('v039TerrainApply',GRID);c('v021RenderAt',[0,58,95],0,-.48);shot('v039_04_maillage_fixture.png','Maillage terrain — fixture QA','Relief synthétique contrôlé servant uniquement à vérifier le maillage et les cellules NoData. Ce n’est pas Marseille.')
 c('v027Open','map','terrain');p.wait_for_timeout(100);shot('v039_05_pip_relief.png','Pip-Boy — Relief IGN','Huit régions, extrema, mesures, NoData et chaîne pack → IndexedDB → cache privé.');c('closePip')
 c('v027Open','map','coverage');p.wait_for_timeout(100);shot('v039_06_pip_couverture.png','Pip-Boy — Couverture','Le vectoriel complet et le relief 8/8 sont visibles sans masquer les audits restant à faire.');c('closePip')
 # NoData demonstration on the controlled fixture.
 c('v018LoadMacro','geo_marseille');p.wait_for_timeout(200);c('v039TerrainApply',GRID);pos=c('geoProject','geo_marseille',43.225,5.29);c('v018CaptureAt',[pos[0],18,pos[2]+35],0,-.35);shot('v039_07_nodata_fixture.png','NoData — fixture QA','Le coin sans donnée reste au plan de référence ; aucune altitude IGN n’y est inventée.')
 p.set_viewport_size({'width':390,'height':844});c('v027Open','map','terrain');p.wait_for_timeout(100);shot('v039_08_mobile_relief.png','Relief en portrait','Lecture des huit régions et des compteurs dans une fenêtre mobile simulée.');b.close()
thumb_w,thumb_h=650,380;pad=24;head=112;rows=(len(shots)+1)//2;canvas=Image.new('RGB',(thumb_w*2+pad*3,(thumb_h+92)*rows+head+pad*2),(10,15,11));dr=ImageDraw.Draw(canvas)
try:fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30);fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except:fb=fs=ft=None
dr.text((pad,pad),'FALLOUT : MISTRAL — v0.39 · RELIEF OFFICIEL',font=fb,fill=(235,224,173));dr.text((pad,pad+44),'8/8 grilles RGE ALTI · 174 944 mesures · 32 424 NoData · vectoriel 5 884/5 884',font=fs,fill=(168,190,162))
for i,(path,title,note) in enumerate(shots):
 im=Image.open(path).convert('RGB');im.thumbnail((thumb_w,thumb_h));bg=Image.new('RGB',(thumb_w,thumb_h),(0,0,0));bg.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2));x=pad+(i%2)*(thumb_w+pad);y=head+pad+(i//2)*(thumb_h+92);canvas.paste(bg,(x,y));dr.rectangle((x,y+thumb_h,x+thumb_w,y+thumb_h+92),fill=(21,30,23));dr.text((x+12,y+thumb_h+8),title,font=fs,fill=(236,226,181));dr.text((x+12,y+thumb_h+36),note[:104],font=ft,fill=(163,182,157))
report=R/'RAPPORT_VISUEL_V0.39.png';canvas.save(report);(O/'CAPTURES_V039.json').write_text(json.dumps({'html_sha256':hashlib.sha256(HTML.encode()).hexdigest(),'errors':errors,'scope':'Exact v0.39 HTML. Coverage plan uses verified cloud metadata. Browser terrain render is an explicitly labelled controlled fixture, not a geographic screenshot of Marseille.','shots':[{'file':x.name,'title':t,'note':n} for x,t,n in shots]},ensure_ascii=False,indent=2));print('REPORT',report,'errors',errors);raise SystemExit(1 if errors else 0)
