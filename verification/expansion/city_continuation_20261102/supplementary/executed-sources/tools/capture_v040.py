#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,math
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.40.html').read_text(encoding='utf-8');shots=[];errors=[]
def font(size,bold=False):
 p='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 try:return ImageFont.truetype(p,size)
 except:return None
# Actual proof map.
proofs=[json.loads(p.read_text()) for p in sorted((R/'data/corridors').glob('*.json'))]
macros={'MARSEILLE':[43.22,5.285,43.34,5.51],'HUVEAUNE':[43.245,5.43,43.335,5.64],'CALANQUES':[43.145,5.33,43.285,5.65],'LA CIOTAT':[43.125,5.54,43.255,5.735]}
W,HMAP=1280,720;pad=65;canvas=Image.new('RGB',(W,HMAP),(11,18,14));d=ImageDraw.Draw(canvas)
latmin,latmax=43.12,43.35;lonmin,lonmax=5.28,5.74
def xy(lat,lon):return(pad+(lon-lonmin)/(lonmax-lonmin)*(W-2*pad),HMAP-pad-(lat-latmin)/(latmax-latmin)*(HMAP-2*pad))
for name,b in macros.items():
 x1,y1=xy(b[0],b[1]);x2,y2=xy(b[2],b[3]);d.rectangle((min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)),outline=(75,101,76),width=2);d.text((min(x1,x2)+6,min(y1,y2)+5),name,fill=(139,165,132),font=font(15,True))
for p in proofs:
 pts=[xy(*q) for q in p['path']];d.line(pts,fill=(226,211,137),width=5);d.ellipse((pts[0][0]-7,pts[0][1]-7,pts[0][0]+7,pts[0][1]+7),fill=(180,220,160));d.ellipse((pts[-1][0]-7,pts[-1][1]-7,pts[-1][0]+7,pts[-1][1]+7),fill=(220,150,110));mid=pts[len(pts)//2];d.text((mid[0]+8,mid[1]-26),f"{p['label']} · {p['distanceM']/1000:.2f} km",fill=(240,229,180),font=font(17,True))
d.text((pad,20),'CORRIDORS CERTIFIÉS v0.40 · GRAPHE OSM MIS EN CACHE',fill=(240,229,180),font=font(26,True));d.text((pad,50),'Jaune : géométries embarquées · cadres : macro-régions · aucune route dessinée manuellement',fill=(166,188,159),font=font(15))
mapfile=O/'v040_00_corridors_preuve.png';canvas.save(mapfile);shots.append((mapfile,'Preuves des deux traversées','Géométries réelles issues du graphe OSM mis en cache.'))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate(r'''() => {const databases=new Map();function open(name,version=1){const req={};setTimeout(()=>{let s=databases.get(name);if(!s){s={version:0,stores:new Map(),opts:new Map()};databases.set(name,s)}const db={get objectStoreNames(){return{contains:n=>s.stores.has(n)}},createObjectStore(n,o={}){s.stores.set(n,new Map());s.opts.set(n,o);return{}},transaction(names){const tx={oncomplete:null,onerror:null};let pending=0,done=false;const fin=()=>setTimeout(()=>{if(!pending&&!done){done=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{if(!s.stores.has(n))s.stores.set(n,new Map());const st=s.stores.get(n),o=s.opts.get(n)||{};const rq=fn=>{const q={};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.()}finally{pending--;fin()}},0);return q};return{get:k=>rq(()=>st.get(k)),getAll:()=>rq(()=>[...st.values()]),put:(v,k)=>rq(()=>{const x=k??(o.keyPath?v[o.keyPath]:undefined);st.set(x,v);return x}),delete:k=>rq(()=>st.delete(k)),clear:()=>rq(()=>st.clear())}};fin();return tx},close(){}};req.result=db;if(version>s.version){req.oldVersion=s.version;s.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:536870912})}})}''')
 p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(800)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def snap(name,title,note):
  path=O/name;p.screenshot(path=str(path));shots.append((path,title,note));print('CAP',name,flush=True)
 snap('v040_01_menu.png','Menu v0.40','Le dossier cartographique affiche désormais Corridors continus.')
 c('v040OpenStatus');snap('v040_02_status.png','Statut de certification','Les deux distances, les raccords cadastraux et le relief sont séparés.');p.locator('#v040StatusClose').click()
 c('v018LoadMacro','geo_huveaune');p.wait_for_timeout(350);c('v027Open','map','corridors');snap('v040_03_pipboy.png','Roadbook dans le Pip-Boy','Deux trajets certifiés peuvent être activés ou préchargés.');c('closePip')
 proof=c('v040Proof','aubagne_marseille');c('v040Start','aubagne_marseille');c('v040SetPlayer',proof['path'][0][0],proof['path'][0][1]);c('v040Tick',.31)
 # Advance to one third for a visible HUD.
 for q in proof['path'][1:24]:c('v040SetPlayer',q[0],q[1]);c('v040Tick',.31)
 c('v021RenderAt',[0,3.1,12],0,-.04,2);snap('v040_04_roadbook.png','Traversée en cours','Le HUD suit la progression et compte les ruptures de continuité.')
 c('v040Stop')
 fixture=c('v040StitchFixture');draws=c('v040FixtureDraws');bd=draws[0]['bounds'];cx,cz=bd['cx'],bd['cz'];yaw=math.atan2(cx-(cx-12),cz-(cz+12));c('v021RenderAt',[cx-12,3.5,cz+12],yaw,-.08,2);snap('v040_05_stitch.png','Bâtiment cadastral recousu','Deux fragments de tuiles sont masqués et remplacés par une seule emprise sûre.')
 c('v027Open','map','corridors');snap('v040_06_certification.png','Compteurs de certification','Le Pip-Boy expose les bâtiments recousus et les preuves hors ligne.');c('closePip')
 c('v040OpenStatus');snap('v040_07_final_status.png','État après recollage','Le statut conserve une distinction claire entre preuve calculée et validation humaine restante.')
 b.close()
# Montage.
tw,th=620,348;gap=22;head=112;rows=math.ceil(len(shots)/2);report=Image.new('RGB',(tw*2+gap*3,head+rows*(th+88)+gap),(10,14,11));dr=ImageDraw.Draw(report);dr.text((gap,22),'FALLOUT : MISTRAL — v0.40 · CORRIDORS CONTINUS',fill=(238,225,174),font=font(29,True));dr.text((gap,62),'Captures directes du HTML final et tracés issus des preuves certifiées embarquées.',fill=(165,188,158),font=font(16))
for i,(path,title,note) in enumerate(shots):
 im=Image.open(path).convert('RGB');im.thumbnail((tw,th));bg=Image.new('RGB',(tw,th),(0,0,0));bg.paste(im,((tw-im.width)//2,(th-im.height)//2));x=gap+(i%2)*(tw+gap);y=head+(i//2)*(th+88);report.paste(bg,(x,y));dr.rectangle((x,y+th,x+tw,y+th+88),fill=(20,29,22));dr.text((x+12,y+th+8),title,fill=(232,219,169),font=font(17,True));dr.text((x+12,y+th+35),note[:92],fill=(166,181,157),font=font(13))
report_path=R/'RAPPORT_VISUEL_V0.40.png';report.save(report_path)
meta={'version':'0.40.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':errors,'shots':[{'file':x.name,'title':t,'note':n} for x,t,n in shots]};(O/'CAPTURES_V040.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('REPORT',report_path,'shots',len(shots),'errors',errors);raise SystemExit(bool(errors))
