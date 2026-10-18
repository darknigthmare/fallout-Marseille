#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
HTML=(R/'JOUER_FALLOUT_MISTRAL_v0.38.html').read_text(encoding='utf-8');MAN=json.loads((R/'data/map_pack/manifest_v038.json').read_text());shots=[];errors=[]
def vi(n:int)->bytes:
 out=bytearray()
 while True:
  b=n&127;n>>=7;out.append(b|(128 if n else 0))
  if not n:return bytes(out)
def zz(n:int)->int:return(n<<1)^(n>>63)
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
base_poly=[9,zz(2500),zz(2500),26,zz(500),0,0,zz(500),zz(-500),0,15]
BASE=layer('transportation',[feature(1,2,line)])+layer('building',[feature(10,3,base_poly)],'class','building')
cad_poly=[9,zz(1800),zz(1800),26,zz(2000),0,0,zz(2000),zz(-2000),0,15]
CAD=layer('batiments',[feature(20,3,cad_poly),feature(21,3,cad_poly)],'nature','dur')
EMPTY_SHA=hashlib.sha256(b'').hexdigest()
# Coverage plan image: only factual extents and counts; no invented roads.
W,H=1500,990;img=Image.new('RGB',(W,H),(14,20,16));d=ImageDraw.Draw(img)
try:F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34);F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);F3=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except:F=F2=F3=None
pad=90;left,bottom,right,top=5.235,43.105,5.775,43.44
xy=lambda lon,lat:(pad+(lon-left)/(right-left)*(W-2*pad),H-pad-(lat-bottom)/(top-bottom)*(H-2*pad))
d.text((pad,25),'FALLOUT : MISTRAL — CADASTRE COMPLET v0.38',font=F,fill=(231,221,171));d.text((pad,66),'Emprises WGS84 · 5 884 coordonnées du manifeste traitées · relief officiel non acquis',font=F2,fill=(168,190,162))
labels={'geo_marseille':'MARSEILLE','geo_huveaune':'HUVEAUNE / AUBAGNE','geo_garlaban':'GARLABAN','geo_calanques':'CALANQUES / CASSIS','geo_laciotat':'LA CIOTAT','geo_frioul':'FRIOUL','geo_etoile':'ÉTOILE','geo_saintebaume':'SAINTE-BAUME'}
for i,(mid,b) in enumerate(MAN['macros'].items()):
 s,w,n,e=b;x0,y1=xy(w,s);x1,y0=xy(e,n);outline=(105+((i*31)%105),145+((i*17)%80),95+((i*43)%120));d.rectangle((x0,y0,x1,y1),outline=outline,width=4);count=MAN['macroCounts'][mid];d.multiline_text((x0+8,y0+7),f"{labels[mid]}\n{count['base']} fond · {count['cadastre']} cad",font=F3,fill=(226,231,207),spacing=3)
for lon in [5.3,5.4,5.5,5.6,5.7]:x,_=xy(lon,bottom);d.line((x,pad,x,H-pad),fill=(51,68,55));d.text((x-22,H-pad+12),f'{lon:.1f}°E',font=F3,fill=(133,153,132))
for lat in [43.15,43.2,43.25,43.3,43.35,43.4]:_,y=xy(left,lat);d.line((pad,y,W-pad,y),fill=(51,68,55));d.text((12,y-9),f'{lat:.2f}°N',font=F3,fill=(133,153,132))
d.rectangle((pad,H-70,W-pad,H-20),fill=(25,36,28));d.text((pad+12,H-62),'CACHE : 5 884/5 884 · 4 557 PBF · 1 327 VIDES OFFICIELLES · 86,97 Mo · MNT : 0/8',font=F2,fill=(236,224,172))
coverage=O/'v038_01_plan_couverture.png';img.save(coverage);shots.append((coverage,'Couverture vectorielle complète','Les 5 884 coordonnées du manifeste sont traitées ; 4 557 contiennent un PBF et 1 327 sont officiellement vides. Relief 0/8.'))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':1440,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate(r'''() => {const databases=new Map();function open(name,version=1){const req={result:null,error:null};setTimeout(()=>{let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}const db={get objectStoreNames(){return{contains:n=>state.stores.has(n)}},createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,finished=false;const maybe=()=>setTimeout(()=>{if(!pending&&!finished){finished=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{const store=state.stores.get(n),opts=state.options.get(n)||{};const request=fn=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.()}finally{pending--;maybe()}},0);return q};return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())}};maybe();return tx},close(){}};req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}})}''')
 def relay(route,req):
  u=req.url;common={'access-control-allow-origin':'*','access-control-expose-headers':'X-Map-Cache, X-Map-Empty, X-Map-SHA256, X-Map-Bytes'}
  if u.endswith('/coverage'):
   route.fulfill(status=200,content_type='application/json',body=json.dumps({'service':'fallout-mistral-map-v038','version':'0.38.0','plan':{'base':367,'cadastre':5517,'total':5884},'cache':{'base':{'coordinates':367,'pbf':367,'empty':0,'bytes':29456613,'hits':31},'cadastre':{'coordinates':5517,'pbf':4190,'empty':1327,'bytes':57517126,'hits':1},'total':5884,'totalBytes':86973739,'totalEmpty':1327,'complete':True,'newest':'2026-09-19T01:51:42Z'}}));return
  if '/tile/base/' in u:route.fulfill(status=200,body=BASE,headers={**common,'content-type':'application/x-protobuf','x-map-cache':'hit','x-map-empty':'0','x-map-sha256':hashlib.sha256(BASE).hexdigest(),'x-map-bytes':str(len(BASE))});return
  if '/tile/cadastre/16/33730/23996' in u:route.fulfill(status=200,body=b'',headers={**common,'content-type':'application/x-protobuf','x-map-cache':'hit-empty','x-map-empty':'1','x-map-sha256':EMPTY_SHA,'x-map-bytes':'0'});return
  if '/tile/cadastre/' in u:route.fulfill(status=200,body=CAD,headers={**common,'content-type':'application/x-protobuf','x-map-cache':'hit','x-map-empty':'0','x-map-sha256':hashlib.sha256(CAD).hexdigest(),'x-map-bytes':str(len(CAD))});return
  route.continue_()
 page.route('**/fallout-mistral-map-v038/**',relay);page.set_content(HTML,wait_until='load');page.wait_for_timeout(3600)
 page.evaluate("window.__CAPSTORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__CAPSTORE[k]??null,setItem:(k,v)=>__CAPSTORE[k]=String(v),removeItem:k=>delete __CAPSTORE[k]}})")
 def c(n,*a):return page.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):path=O/name;page.screenshot(path=str(path));shots.append((path,title,note));print('CAP',name,flush=True)
 shot('v038_02_menu.png','Menu v0.38','Le menu annonce un cadastre complet sans prétendre que le relief officiel est installé.')
 c('v038OpenStatus');page.wait_for_timeout(120);shot('v038_03_statut.png','État cartographique','5 884/5 884 coordonnées : 4 557 PBF, 1 327 tuiles vides officielles et relief 0/8.');page.click('#v038StatusClose')
 c('v018LoadMacro','geo_marseille');page.wait_for_timeout(350);c('v018Queue','base',14,8437,6001);c('v018Queue','base',14,8438,6001);c('v018Queue','cadastre',16,33750,24006);c('v018Queue','cadastre',16,33730,23996);page.wait_for_timeout(1800)
 c('v027Open','map','cache');page.wait_for_timeout(100);shot('v038_04_pip_cache.png','Pip-Boy — cache complet','Le cache cloud, le navigateur, les PBF et les réponses officielles vides sont comptés séparément.');c('closePip')
 c('v027Open','map','coverage');page.wait_for_timeout(100);shot('v038_05_pip_couverture.png','Pip-Boy — couverture','Chaque macro-région est reliée au cache complet ; le relief officiel reste explicitement absent.');c('closePip')
 c('v018Fixture',True);geom=c('v018Geometry');pts=[g.get('pos') for g in geom if g.get('pos') and len(g['pos'])==3];cx=sum(x[0] for x in pts)/len(pts) if pts else 0;cz=sum(x[2] for x in pts)/len(pts) if pts else 0;c('v018CaptureAt',[cx,42,cz+58],0,-.55);shot('v038_06_raccord_synthetique.png','Raccord MVT synthétique','Fixture QA : raccord routier, remplacement du bâti générique et déduplication cadastrale. Ce n’est pas Marseille.');c('v018Fixture',False)
 c('v018LoadMacro','geo_marseille');page.wait_for_timeout(250);c('v036SetLatLon',43.29,5.52);c('v036TryTransfer');page.wait_for_timeout(600);c('v018CaptureAt',[0,12,26],0,-.28);shot('v038_07_transition.png','Transition Marseille → Huveaune','La transition conserve la latitude et la longitude avant reprojection dans la macro-région voisine.')
 page.set_viewport_size({'width':390,'height':844});c('v038OpenStatus');page.wait_for_timeout(100);shot('v038_08_mobile_statut.png','Statut en portrait','Lecture des compteurs PBF / vides / relief dans une fenêtre mobile simulée.');b.close()
thumb_w,thumb_h=650,380;pad=24;head=110;rows=(len(shots)+1)//2;canvas=Image.new('RGB',(thumb_w*2+pad*3,(thumb_h+92)*rows+head+pad*2),(10,15,11));dr=ImageDraw.Draw(canvas)
try:fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30);fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except:fb=fs=ft=None
dr.text((pad,pad),'FALLOUT : MISTRAL — v0.38 · CADASTRE COMPLET',font=fb,fill=(235,224,173));dr.text((pad,pad+44),'5 884/5 884 coordonnées · 4 557 PBF · 1 327 vides officielles · 86,97 Mo · relief 0/8',font=fs,fill=(168,190,162))
for i,(path,title,note) in enumerate(shots):
 im=Image.open(path).convert('RGB');im.thumbnail((thumb_w,thumb_h));bg=Image.new('RGB',(thumb_w,thumb_h),(0,0,0));bg.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2));x=pad+(i%2)*(thumb_w+pad);y=head+pad+(i//2)*(thumb_h+92);canvas.paste(bg,(x,y));dr.rectangle((x,y+thumb_h,x+thumb_w,y+thumb_h+92),fill=(21,30,23));dr.text((x+12,y+thumb_h+8),title,font=fs,fill=(236,226,181));dr.text((x+12,y+thumb_h+36),note[:100],font=ft,fill=(163,182,157))
report=R/'RAPPORT_VISUEL_V0.38.png';canvas.save(report);(O/'CAPTURES_V038.json').write_text(json.dumps({'html_sha256':hashlib.sha256(HTML.encode()).hexdigest(),'errors':errors,'scope':'Exact v0.38 HTML. The 5,884-coordinate cloud cache is live verified separately. Browser cache and seam render use controlled fixtures. No official terrain bundled.','shots':[{'file':p.name,'title':t,'note':n} for p,t,n in shots]},ensure_ascii=False,indent=2));print('REPORT',report,'errors',errors);raise SystemExit(1 if errors else 0)
