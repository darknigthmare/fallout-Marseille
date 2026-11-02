#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, math
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[1]
O=R/'verification'; O.mkdir(exist_ok=True)
H=(R/'JOUER_FALLOUT_MISTRAL_v0.41.html').read_text(encoding='utf-8')
shots=[]; errors=[]

def font(size,bold=False):
    p='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:return ImageFont.truetype(p,size)
    except:return None

# Actual production-manifest visualization (not a concept mockup).
manifest=json.loads((R/'data/map_pack/local_pack_v041_manifest.json').read_text(encoding='utf-8'))
W,HCH=1280,720; canvas=Image.new('RGB',(W,HCH),(10,16,12)); d=ImageDraw.Draw(canvas)
d.text((54,28),'PACK TERRITORIAL LOCAL v0.41 · 24 ARCHIVES AUTHENTIFIÉES',fill=(239,226,178),font=font(28,True))
d.text((54,67),'367 coordonnées générales · 5 517 cadastrales · 1 327 vides officielles',fill=(164,188,158),font=font(16))
chunks=manifest['chunks']; maxb=max(c['base64Bytes'] for c in chunks); left=64; top=126; rowh=22; barw=830
for i,c in enumerate(chunks):
    y=top+i*rowh; ratio=c['base64Bytes']/maxb; col=(159,190,124) if c['source']=='base' else (198,166,101)
    d.text((left,y),f"{i+1:02d}",fill=(135,154,132),font=font(12))
    d.rectangle((left+34,y+2,left+34+max(3,int(barw*ratio)),y+16),fill=col)
    d.text((left+barw+54,y),f"{c['name']:<29} {c['rows']:>3} coords · {c['base64Bytes']/1048576:5.2f} Mio",fill=(213,220,197),font=font(12))
d.text((54,666),f"Total transport Base64 : {manifest['totalBase64Bytes']/1048576:.2f} Mio · distribution binaire après décodage · bucket privé",fill=(216,205,161),font=font(15,True))
chart=O/'v041_00_manifest_chunks.png'; canvas.save(chart); shots.append((chart,'Manifeste de distribution réel','Les 5 884 coordonnées sont réparties dans 24 lots versionnés ; ce graphique est calculé depuis le manifeste final.'))

with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':1440,'height':960}); p.on('pageerror',lambda e:errors.append(str(e)))
    p.evaluate(r'''() => {const databases=new Map();function open(name,version=1){const req={};setTimeout(()=>{let s=databases.get(name);if(!s){s={version:0,stores:new Map(),opts:new Map()};databases.set(name,s)}const db={get objectStoreNames(){return{contains:n=>s.stores.has(n)}},createObjectStore(n,o={}){s.stores.set(n,new Map());s.opts.set(n,o);return{}},transaction(names){const tx={oncomplete:null,onerror:null};let pending=0,done=false;const fin=()=>setTimeout(()=>{if(!pending&&!done){done=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{if(!s.stores.has(n))s.stores.set(n,new Map());const st=s.stores.get(n),o=s.opts.get(n)||{};const rq=fn=>{const q={};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.()}finally{pending--;fin()}},0);return q};return{get:k=>rq(()=>st.get(k)),getAll:()=>rq(()=>[...st.values()]),put:(v,k)=>rq(()=>{const x=k??(o.keyPath?v[o.keyPath]:undefined);st.set(x,v);return x}),delete:k=>rq(()=>st.delete(k)),clear:()=>rq(()=>st.clear())}};fin();return tx},close(){}};req.result=db;if(version>s.version){req.oldVersion=s.version;s.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:536870912})}})}''')
    p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort())
    p.set_content(H,wait_until='load'); p.wait_for_timeout(850)
    def c(n,*a): return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
    def snap(name,title,note):
        path=O/name; p.screenshot(path=str(path)); shots.append((path,title,note)); print('CAP',name,flush=True)

    snap('v041_01_menu.png','Menu v0.41','Le dossier de production affiche « Territoire local » ; les outils internes restent dans Admin.')
    c('v041OpenStatus'); snap('v041_02_status_pending.png','Statut avant installation','État réel du ZIP compact : distribution disponible, mais pack lourd non installé dans cette exécution.'); p.locator('#v041StatusClose').click()
    c('v020Reset'); c('v020Load','transit_depot'); p.wait_for_timeout(180); c('v027Open','map','pack')
    snap('v041_03_pip_pending.png','Pip-Boy · pack non détecté','L’interface explique les 24 archives et ne confond pas le cache cloud avec une installation locale.'); c('closePip')

    # Presentation-only UI state: the caption explicitly says it is simulated for layout verification.
    c('v041SetLocal',{'state':'ready','complete':True,'coordinates':5884,'objects':4557,'officialEmpty':1327,'missing':0,'invalid':0,'bytes':86973739,'terrain':8})
    c('v041SetBenchmark',{'state':'ready','sampledPbf':4557,'decodedBytes':86973739,'seconds':4.2,'throughputMiBps':19.75,'tilesPerSecond':1085.0,'p95':2.1,'peakRssKiB':150000,'terrain':8,'completePack':True})
    c('v027Open','map','pack'); snap('v041_04_pip_complete_demo.png','Présentation de l’état complet','État injecté uniquement pour vérifier la mise en page finale ; le runner n’a pas installé le pack lourd à cause de sa résolution DNS.'); c('closePip')
    c('v041OpenStatus'); snap('v041_05_status_benchmark_demo.png','Présentation du benchmark','Valeurs de présentation injectées pour tester les métriques ; les performances réelles seront écrites par benchmark_map_v041.py sur la machine cible.'); p.locator('#v041StatusClose').click()

    c('v020Reset'); c('v020Load','transit_depot'); p.wait_for_timeout(160); c('v027Open','map','corridors')
    snap('v041_06_roadbook.png','Roadbook conservé','Les deux corridors certifiés de la v0.40 restent disponibles après l’ajout du pack local.'); c('closePip')

    p.set_viewport_size({'width':390,'height':844}); c('v027Open','map','pack'); p.wait_for_timeout(100)
    snap('v041_07_mobile_pack.png','Pack local sur écran étroit','La rubrique reste défilable et lisible à 390 × 844 ; il s’agit d’une fenêtre simulée, pas d’une certification matérielle.')
    b.close()

# Montage.
tw,th=620,348; gap=22; head=118; rows=math.ceil(len(shots)/2)
report=Image.new('RGB',(tw*2+gap*3,head+rows*(th+96)+gap),(9,14,10)); dr=ImageDraw.Draw(report)
dr.text((gap,22),'FALLOUT : MISTRAL — v0.41 · TERRITOIRE LOCAL',fill=(239,225,176),font=font(29,True))
dr.text((gap,61),'Captures directes du HTML final et graphique calculé depuis le manifeste de production.',fill=(163,187,157),font=font(16))
for i,(path,title,note) in enumerate(shots):
    im=Image.open(path).convert('RGB'); im.thumbnail((tw,th)); bg=Image.new('RGB',(tw,th),(0,0,0)); bg.paste(im,((tw-im.width)//2,(th-im.height)//2))
    x=gap+(i%2)*(tw+gap); y=head+(i//2)*(th+96); report.paste(bg,(x,y)); dr.rectangle((x,y+th,x+tw,y+th+96),fill=(19,28,21))
    dr.text((x+12,y+th+8),title,fill=(232,220,171),font=font(17,True)); dr.text((x+12,y+th+36),note[:105],fill=(164,181,156),font=font(13))
report_path=R/'RAPPORT_VISUEL_V0.41.png'; report.save(report_path)
meta={'version':'0.41.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':errors,'disclosure':'The two complete-pack screenshots use injected presentation data solely to validate layout. No claim is made that the heavy pack was installed in this runner.','shots':[{'file':p.name,'title':t,'note':n} for p,t,n in shots]}
(O/'CAPTURES_V041.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('REPORT',report_path,'shots',len(shots),'errors',errors)
raise SystemExit(bool(errors))
