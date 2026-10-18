#!/usr/bin/env python3
"""Static distribution QA for the local PWA layer.

This intentionally does not claim a live service-worker registration: localhost
navigation is blocked by the current execution environment. It verifies the
shipping files and their internal contract against the exact release HTML.
"""
from pathlib import Path
from PIL import Image
import hashlib, json, re

R=Path(__file__).resolve().parents[1]
O=R/'verification'; O.mkdir(exist_ok=True)
rows=[]

def ck(name, cond, detail=None):
    rows.append({'name':name,'ok':bool(cond),'detail':detail})
    print(('OK ' if cond else 'FAIL ')+name, flush=True)

html=(R/'JOUER_FALLOUT_MISTRAL_v0.40.html').read_bytes()
index=(R/'index.html').read_bytes()
text=html.decode('utf-8')
manifest=json.loads((R/'manifest.webmanifest').read_text(encoding='utf-8'))
sw=(R/'sw.js').read_text(encoding='utf-8')

ck('Index installable identique au HTML autonome', hashlib.sha256(index).digest()==hashlib.sha256(html).digest())
ck('Manifest lié dans le HTML', bool(re.search(r'<link[^>]+rel=["\']manifest["\'][^>]+href=["\']manifest\.webmanifest["\']',text,re.I)) or ('manifest.webmanifest' in text))
ck('Manifest application cohérent', manifest.get('name','').startswith('Fallout : Mistral') and manifest.get('start_url')=='./index.html' and manifest.get('display')=='standalone', manifest)
icon_dims=[]
for size in (192,512):
    p=R/'icons'/f'mistral-{size}.png'
    if p.exists():
        with Image.open(p) as im: icon_dims.append(tuple(im.size))
ck('Icônes PWA aux dimensions déclarées', icon_dims==[(192,192),(512,512)], icon_dims)
core=['./index.html','./JOUER_FALLOUT_MISTRAL_v0.40.html','./manifest.webmanifest','./icons/mistral-192.png','./icons/mistral-512.png','./data/corridors/aubagne_marseille.json','./data/corridors/aubagne_laciotat.json']
ck('Service worker met en cache le noyau local', all(item in sw for item in core) and 'caches.open' in sw and 'fetch' in sw)
launchers=[R/'LANCER_APP_WINDOWS.bat',R/'LANCER_APP_LINUX.sh',R/'LANCER_APP_MAC.command']
launcher_text='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in launchers if p.exists())
ck('Trois lanceurs application ciblent le serveur local', len([p for p in launchers if p.exists()])==3 and 'serve_game.py' in launcher_text)

rep={
 'version':'0.40.0',
 'html_sha256':hashlib.sha256(html).hexdigest(),
 'passed':sum(x['ok'] for x in rows),
 'failed':sum(not x['ok'] for x in rows),
 'total':len(rows),
 'errors':[],
 'scope':'Static PWA/distribution contract. Live service-worker registration and offline reload were not executable because localhost navigation is blocked in this environment.',
 'checks':rows,
}
(O/'QA_PWA_V040.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('TOTAL',rep['passed'],rep['failed'],flush=True)
raise SystemExit(bool(rep['failed']))
