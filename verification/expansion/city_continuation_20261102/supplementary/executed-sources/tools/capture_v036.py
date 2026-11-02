#!/usr/bin/env python3
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
H=(R/'JOUER_FALLOUT_MISTRAL_v0.36.html').read_text();BASE=(R/'data/fixtures/france-vector-z14-8437-6001.pbf').read_bytes();CAD=(R/'data/fixtures/cadastre-z16-33750-24006.pbf').read_bytes();M=json.loads((R/'data/map_pack/manifest_v036.compact.json').read_text())
shots=[];errors=[]
# Coverage plan (real geographic extents, no basemap and no invented roads).
W,HIMG=1500,980;img=Image.new('RGB',(W,HIMG),(15,21,17));d=ImageDraw.Draw(img)
try:
 F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34);F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);F3=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except:F=F2=F3=None
pad=90;left,bottom,right,top=5.235,43.105,5.775,43.44
xy=lambda lon,lat:(pad+(lon-left)/(right-left)*(W-2*pad),HIMG-pad-(lat-bottom)/(top-bottom)*(HIMG-2*pad))
d.text((pad,25),'FALLOUT : MISTRAL — PLAN DE COUVERTURE RÉELLE v0.36',font=F,fill=(231,221,171));d.text((pad,66),'Emprises WGS84 et nombre de tuiles planifiées · aucun tracé routier inventé',font=F2,fill=(168,190,162))
labels={'geo_marseille':'MARSEILLE','geo_huveaune':'HUVEAUNE / AUBAGNE','geo_garlaban':'GARLABAN','geo_calanques':'CALANQUES / CASSIS','geo_laciotat':'LA CIOTAT','geo_frioul':'FRIOUL','geo_etoile':'ÉTOILE','geo_saintebaume':'SAINTE-BAUME'}
for i,(mid,b) in enumerate(M['macros'].items()):
 s,w,n,e=b;x0,y1=xy(w,s);x1,y0=xy(e,n);outline=(105+((i*31)%105),145+((i*17)%80),95+((i*43)%120));d.rectangle((x0,y0,x1,y1),outline=outline,width=4);count=M['macroCounts'][mid];txt=f"{labels[mid]}\n{count['base']} OSM · {count['cadastre']} CAD";d.multiline_text((x0+8,y0+7),txt,font=F3,fill=(226,231,207),spacing=3)
# coordinate grid
for lon in [5.3,5.4,5.5,5.6,5.7]:
 x,_=xy(lon,bottom);d.line((x,pad,x,HIMG-pad),fill=(51,68,55),width=1);d.text((x-22,HIMG-pad+12),f'{lon:.1f}°E',font=F3,fill=(133,153,132))
for lat in [43.15,43.2,43.25,43.3,43.35,43.4]:
 _,y=xy(left,lat);d.line((pad,y,W-pad,y),fill=(51,68,55),width=1);d.text((12,y-9),f'{lat:.2f}°N',font=F3,fill=(133,153,132))
d.rectangle((pad,HIMG-58,W-pad,HIMG-20),fill=(25,36,28));d.text((pad+12,HIMG-53),'TOTAL : 367 tuiles OSM z14 + 5 517 tuiles cadastrales z16 = 5 884 · terrain numérique officiel : 0 / 8',font=F2,fill=(236,224,172))
coverage=O/'v036_01_plan_couverture.png';img.save(coverage);shots.append((coverage,'Plan de couverture','Huit emprises géographiques et 5 884 tuiles planifiées. Le dessin ne fabrique aucune route.'))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 def handler(route,req):
  if req.url.endswith('/meta'):route.fulfill(status=200,content_type='application/json',body=json.dumps({'sources':{'base':{'count':367},'cadastre':{'count':5517}},'total':5884}))
  elif '/tile/base/' in req.url:route.fulfill(status=200,content_type='application/x-protobuf',body=BASE)
  elif '/tile/cadastre/' in req.url:route.fulfill(status=200,content_type='application/x-protobuf',body=CAD)
  else:route.continue_()
 p.route('**/fallout-mistral-map-v036/**',handler);p.set_content(H,wait_until='load');p.wait_for_timeout(3500)
 p.evaluate("window.__CAPSTORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__CAPSTORE[k]??null,setItem:(k,v)=>__CAPSTORE[k]=String(v),removeItem:k=>delete __CAPSTORE[k]}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):
  path=O/name;p.screenshot(path=str(path));shots.append((path,title,note));print('CAP',name,flush=True)
 c('v036Health');p.wait_for_timeout(120)
 shot('v036_02_menu.png','Menu v0.36','La build annonce explicitement son statut cartographique.')
 c('v018OpenStatus');p.wait_for_timeout(100);shot('v036_03_statut.png','État des données','Distinction explicite entre couverture vectorielle adressable, pack hors ligne et relief numérique absent.');c('v018CloseStatus')
 c('v018LoadMacro','geo_marseille');p.wait_for_timeout(500);c('v018Queue','base',14,8437,6001);c('v018Queue','cadastre',16,33750,24006);p.wait_for_timeout(1100);c('v018Fixture',True)
 geom=c('v018Geometry');poses=[g.get('pos') for g in geom if g.get('pos') and len(g['pos'])==3]
 if poses:
  cx=sum(x[0] for x in poses)/len(poses);cz=sum(x[2] for x in poses)/len(poses)
 else:cx=cz=0
 c('v018CaptureAt',[cx,46,cz+58],0,-.57);shot('v036_04_pipeline_mvt.png','Pipeline MVT validé','Géométrie synthétique explicitement marquée : cette vue teste le décodeur/rendu, pas la fidélité de Marseille.')
 c('v018Fixture',False);c('v027Open','map','coverage');p.wait_for_timeout(100);shot('v036_05_pip_couverture.png','Pip-Boy — couverture','Les huit territoires et les limites 0/8 du relief officiel restent consultables en jeu.');c('closePip')
 # Transfer presentation: preserve real geographic coordinate between worlds.
 c('v018LoadMacro','geo_marseille');p.wait_for_timeout(350);c('v036SetLatLon',43.29,5.52);c('v036TryTransfer');p.wait_for_timeout(650);c('v018CaptureAt',[0,12,26],0,-.28);shot('v036_06_transition_huveaune.png','Transition continue','La position WGS84 passe de Marseille à l’Huveaune sans voyage scénaristique ni changement de coordonnées.')
 c('v027Open','map','local');p.wait_for_timeout(100);shot('v036_07_position_locale.png','Position locale','Le terminal affiche la macro-région, la position et le nombre de tuiles actives.');c('closePip')
 p.set_viewport_size({'width':390,'height':844});c('v018OpenStatus');p.wait_for_timeout(100);shot('v036_08_mobile_statut.png','Statut en portrait','Lecture du statut cartographique sur une fenêtre 390 × 844 simulée.');b.close()
# collage
thumb_w,thumb_h=650,380;pad=24;head=110;rows=(len(shots)+1)//2
canvas=Image.new('RGB',(thumb_w*2+pad*3,(thumb_h+88)*rows+head+pad*2),(10,15,11));dr=ImageDraw.Draw(canvas)
try:fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30);fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except:fb=fs=ft=None
dr.text((pad,pad),'FALLOUT : MISTRAL — v0.36 · TERRITOIRE RÉEL',font=fb,fill=(235,224,173));dr.text((pad,pad+44),'Couverture vectorielle officielle en streaming · terrain numérique officiel encore absent',font=fs,fill=(168,190,162))
for i,(path,title,note) in enumerate(shots):
 im=Image.open(path).convert('RGB');im.thumbnail((thumb_w,thumb_h));bg=Image.new('RGB',(thumb_w,thumb_h),(0,0,0));bg.paste(im,((thumb_w-im.width)//2,(thumb_h-im.height)//2));x=pad+(i%2)*(thumb_w+pad);y=head+pad+(i//2)*(thumb_h+88);canvas.paste(bg,(x,y));dr.rectangle((x,y+thumb_h,x+thumb_w,y+thumb_h+88),fill=(21,30,23));dr.text((x+12,y+thumb_h+8),title,font=fs,fill=(236,226,181));dr.text((x+12,y+thumb_h+35),note[:92],font=ft,fill=(163,182,157))
report=R/'RAPPORT_VISUEL_V0.36.png';canvas.save(report)
(O/'CAPTURES_V036.json').write_text(json.dumps({'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':errors,'shots':[{'file':p.name,'title':t,'note':n} for p,t,n in shots]},ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',report,'errors',errors);raise SystemExit(1 if errors else 0)
