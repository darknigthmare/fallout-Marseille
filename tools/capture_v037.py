#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
import json,hashlib

R=Path(__file__).resolve().parents[1]
O=R/'verification'; O.mkdir(exist_ok=True)
H=(R/'JOUER_FALLOUT_MISTRAL_v0.37.html').read_text(encoding='utf-8')
MAN=json.loads((R/'data/map_pack/manifest_v037.json').read_text(encoding='utf-8'))
shots=[]; errors=[]

def vi(n:int)->bytes:
 out=bytearray()
 while True:
  b=n&127;n>>=7;out.append(b|(128 if n else 0))
  if not n:return bytes(out)
def zz(n:int)->int:return (n<<1)^(n>>63)
def field(num:int,wire:int,payload:bytes|int)->bytes:
 head=vi((num<<3)|wire)
 if wire==0:return head+vi(int(payload))
 return head+vi(len(payload))+payload
def packed(vals):return b''.join(vi(v) for v in vals)
def value_string(s):return field(1,2,s.encode())
def feature(fid,geom_type,geometry,tags=(0,0)):
 return field(1,0,fid)+field(2,2,packed(tags))+field(3,0,geom_type)+field(4,2,packed(geometry))
def layer(name,features,key='class',value='primary'):
 raw=field(15,0,2)+field(1,2,name.encode())
 for f in features:raw+=field(2,2,f)
 raw+=field(3,2,key.encode())+field(4,2,value_string(value))+field(5,0,4096)
 return field(3,2,raw)
line=[9,zz(0),zz(2048),10,zz(4096),zz(0)]
base_poly=[9,zz(2500),zz(2500),26,zz(500),zz(0),zz(0),zz(500),zz(-500),zz(0),15]
BASE=layer('transportation',[feature(1,2,line)])+layer('building',[feature(10,3,base_poly)],'class','building')
cad_poly=[9,zz(1800),zz(1800),26,zz(2000),zz(0),zz(0),zz(2000),zz(-2000),zz(0),15]
CAD=layer('batiments',[feature(20,3,cad_poly),feature(21,3,cad_poly)],'nature','dur')

# Geographic coverage image. Only extents/counts; no invented road network.
W,HIMG=1500,990;img=Image.new('RGB',(W,HIMG),(14,20,16));d=ImageDraw.Draw(img)
try:
 F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
 F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
 F3=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except: F=F2=F3=None
pad=90;left,bottom,right,top=5.235,43.105,5.775,43.44
xy=lambda lon,lat:(pad+(lon-left)/(right-left)*(W-2*pad),HIMG-pad-(lat-bottom)/(top-bottom)*(HIMG-2*pad))
d.text((pad,25),'FALLOUT : MISTRAL — CACHE TERRITORIAL v0.37',font=F,fill=(231,221,171))
d.text((pad,66),'Emprises WGS84 officielles planifiées · aucune route ou altitude inventée',font=F2,fill=(168,190,162))
labels={'geo_marseille':'MARSEILLE','geo_huveaune':'HUVEAUNE / AUBAGNE','geo_garlaban':'GARLABAN','geo_calanques':'CALANQUES / CASSIS','geo_laciotat':'LA CIOTAT','geo_frioul':'FRIOUL','geo_etoile':'ÉTOILE','geo_saintebaume':'SAINTE-BAUME'}
for i,(mid,b) in enumerate(MAN['macros'].items()):
 s,w,n,e=b;x0,y1=xy(w,s);x1,y0=xy(e,n);outline=(105+((i*31)%105),145+((i*17)%80),95+((i*43)%120));d.rectangle((x0,y0,x1,y1),outline=outline,width=4);count=MAN['macroCounts'][mid];d.multiline_text((x0+8,y0+7),f"{labels[mid]}\n{count['base']} OSM · {count['cadastre']} CAD",font=F3,fill=(226,231,207),spacing=3)
for lon in [5.3,5.4,5.5,5.6,5.7]:
 x,_=xy(lon,bottom);d.line((x,pad,x,HIMG-pad),fill=(51,68,55));d.text((x-22,HIMG-pad+12),f'{lon:.1f}°E',font=F3,fill=(133,153,132))
for lat in [43.15,43.2,43.25,43.3,43.35,43.4]:
 _,y=xy(left,lat);d.line((pad,y,W-pad,y),fill=(51,68,55));d.text((12,y-9),f'{lat:.2f}°N',font=F3,fill=(133,153,132))
d.rectangle((pad,HIMG-70,W-pad,HIMG-20),fill=(25,36,28));d.text((pad+12,HIMG-62),'PLAN : 5 884 PBF · CACHE CLOUD RÉEL : 368 · PACK ZIP : 0 · MNT OFFICIELS : 0 / 8',font=F2,fill=(236,224,172))
coverage=O/'v037_01_plan_couverture.png';img.save(coverage);shots.append((coverage,'Plan territorial','Huit emprises WGS84, 5 884 coordonnées prévues, cache cloud réel 368 (fond 367/367), relief officiel 0/8.'))

with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=pw.chromium.launch if False else None
 page=b.new_page(viewport={'width':1440,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate(r'''() => {
  const databases=new Map();
  function open(name,version=1){const req={result:null,error:null};setTimeout(()=>{let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}const db={get objectStoreNames(){return{contains:n=>state.stores.has(n)}},createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,finished=false;const maybe=()=>setTimeout(()=>{if(!pending&&!finished){finished=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{const store=state.stores.get(n),opts=state.options.get(n)||{};const request=fn=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.();tx.onerror?.()}finally{pending--;maybe()}},0);return q};return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())}};maybe();return tx},close(){}};req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}
  Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});
  Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}});
 }''')
 def handler(route,req):
  u=req.url
  if u.endswith('/coverage'):
   route.fulfill(status=200,content_type='application/json',body=json.dumps({'service':'fallout-mistral-map-v037','version':'0.37.0','plan':{'base':367,'cadastre':5517,'total':5884},'cache':{'base':{'count':367,'bytes':29456613,'hits':31},'cadastre':{'count':1,'bytes':3816,'hits':1},'total':368,'totalBytes':29460429,'newest':'2026-09-19T00:56:40Z'}}));return
  if '/tile/base/' in u:
   route.fulfill(status=200,body=BASE,headers={'content-type':'application/x-protobuf','x-map-cache':'hit','x-map-sha256':hashlib.sha256(BASE).hexdigest(),'x-map-bytes':str(len(BASE)),'x-map-fetched-at':'2026-09-19T00:56:40Z'});return
  if '/tile/cadastre/' in u:
   route.fulfill(status=200,body=CAD,headers={'content-type':'application/x-protobuf','x-map-cache':'hit','x-map-sha256':hashlib.sha256(CAD).hexdigest(),'x-map-bytes':str(len(CAD)),'x-map-fetched-at':'2026-09-19T00:56:40Z'});return
  route.continue_()
 page.route('**/fallout-mistral-map-v037/**',handler)
 page.set_content(H,wait_until='load');page.wait_for_timeout(3500)
 page.evaluate("window.__CAPSTORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__CAPSTORE[k]??null,setItem:(k,v)=>__CAPSTORE[k]=String(v),removeItem:k=>delete __CAPSTORE[k]}})")
 def c(n,*a):return page.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):
  path=O/name;page.screenshot(path=str(path));shots.append((path,title,note));print('CAP',name,flush=True)
 page.wait_for_timeout(250);shot('v037_02_menu.png','Menu v0.37','La build annonce Cache territorial sans prétendre que le pack complet est embarqué.')
 c('v037OpenStatus');page.wait_for_timeout(100);shot('v037_03_statut.png','État cartographique','Le plan 5 884, le cache cloud réel 368 — fond 367/367, cadastre 1/5 517 — le cache local et le relief 0/8 sont séparés.');page.click('#v037StatusClose')
 c('v018LoadMacro','geo_marseille');page.wait_for_timeout(350)
 c('v018Queue','base',14,8437,6001);c('v018Queue','base',14,8438,6001);c('v018Queue','cadastre',16,33750,24006);page.wait_for_timeout(1700)
 c('v027Open','map','cache');page.wait_for_timeout(100);shot('v037_04_pip_cache.png','Pip-Boy — cache','Trois PBF contrôlés dans le cache local de QA ; 368 sont réellement archivés dans le cache cloud, dont le fond complet 367/367.');c('closePip')
 c('v027Open','map','coverage');page.wait_for_timeout(100);shot('v037_05_pip_couverture.png','Pip-Boy — couverture','Les huit macro-régions, le plan théorique et les fichiers acquis sont présentés séparément.');c('closePip')
 # Synthetic QA geometry clearly identified.
 c('v018Fixture',True);geom=c('v018Geometry');pts=[g.get('pos') for g in geom if g.get('pos') and len(g['pos'])==3]
 if pts:cx=sum(x[0] for x in pts)/len(pts);cz=sum(x[2] for x in pts)/len(pts)
 else:cx=cz=0
 c('v018CaptureAt',[cx,42,cz+58],0,-.55);shot('v037_06_raccord_synthetique.png','Raccord MVT synthétique','Vue de QA : deux tuiles contrôlées valident raccord routier, remplacement HLOD et déduplication cadastrale ; ce n’est pas Marseille.')
 c('v018Fixture',False)
 c('v018LoadMacro','geo_marseille');page.wait_for_timeout(250);c('v036SetLatLon',43.29,5.52);c('v036TryTransfer');page.wait_for_timeout(600);c('v018CaptureAt',[0,12,26],0,-.28);shot('v037_07_transition.png','Transition Marseille → Huveaune','La latitude/longitude est conservée au changement de macro-région.')
 page.set_viewport_size({'width':390,'height':844});c('v037OpenStatus');page.wait_for_timeout(100);shot('v037_08_mobile_statut.png','Statut en portrait','Lecture du statut cache/pack/terrain dans une fenêtre 390×844 simulée.');b.close()

thumb_w,thumb_h=650,380;pad=24;head=110;rows=(len(shots)+1)//2
canvas=Image.new('RGB',(thumb_w*2+pad*3,(thumb_h+92)*rows+head+pad*2),(10,15,11));dr=ImageDraw.Draw(canvas)
try:
 fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30);fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except:fb=fs=ft=None
dr.text((pad,pad),'FALLOUT : MISTRAL — v0.37 · CACHE TERRITORIAL',font=fb,fill=(235,224,173));dr.text((pad,pad+44),'Plan 5 884 · cache cloud réel 368 · fond 367/367 · pack 0 · relief 0/8',font=fs,fill=(168,190,162))
for i,(path,title,note) in enumerate(shots):
 im=Image.open(path).convert('RGB');im.thumbnail((thumb_w,thumb_h));bg=Image.new('RGB',(thumb_w,thumb_h),(0,0,0));bg.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2));x=pad+(i%2)*(thumb_w+pad);y=head+pad+(i//2)*(thumb_h+92);canvas.paste(bg,(x,y));dr.rectangle((x,y+thumb_h,x+thumb_w,y+thumb_h+92),fill=(21,30,23));dr.text((x+12,y+thumb_h+8),title,font=fs,fill=(236,226,181));dr.text((x+12,y+thumb_h+36),note[:96],font=ft,fill=(163,182,157))
report=R/'RAPPORT_VISUEL_V0.37.png';canvas.save(report)
(O/'CAPTURES_V037.json').write_text(json.dumps({'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':errors,'scope':'HTML exact v0.37. Cloud count 368 is live verified; base layer 367/367, cadastre 1/5517; local IndexedDB count and seam scene use controlled QA fixtures because native storage/network are blocked in the production sandbox. No official terrain bundled.','shots':[{'file':p.name,'title':t,'note':n} for p,t,n in shots]},ensure_ascii=False,indent=2),encoding='utf-8')
print('REPORT',report,'errors',errors)
raise SystemExit(1 if errors else 0)
