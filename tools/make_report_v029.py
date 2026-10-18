#!/usr/bin/env python3
"""Contact sheet and self-contained report from actual browser screenshots."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import base64,io,json,html,textwrap,hashlib
R=Path(__file__).resolve().parents[1];meta=json.loads((R/'verification/CAPTURES_V029.json').read_text());current=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes()).hexdigest()
assert not meta['errors'] and meta['html_sha256']==current
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(n,b=False):
 try:return ImageFont.truetype(bold if b else font,n)
 except OSError:return ImageFont.load_default(size=n)
selected=['05_deduction.png','06_similitude.png','10_volet_ouvert.png','13_journal_archives.png','15_soupcon.png','18_pip_controleurs.png']
imgs={x['file']:x for x in meta['images']}
w=1800;pad=36;gap=24;tilew=(w-pad*2-gap)//2;himg=round(tilew*2/3);rowh=himg+95;header=190;canvas=Image.new('RGB',(w,header+3*(rowh+gap)+80),(13,24,22));d=ImageDraw.Draw(canvas)
d.text((pad,30),'FALLOUT : MISTRAL',font=f(44,True),fill=(224,231,211));d.text((pad,91),'v0.29  —  Les portes ont des oreilles',font=f(32),fill=(184,210,159));d.text((pad,140),'Captures réelles • scènes fictives • caméras et certains états préparés',font=f(21),fill=(161,180,166))
for i,key in enumerate(selected):
 x=pad+(i%2)*(tilew+gap);y=header+(i//2)*(rowh+gap);im=Image.open(R/'verification'/key).convert('RGB');im.thumbnail((tilew,himg),Image.Resampling.LANCZOS);canvas.paste(im,(x,y));d.rectangle((x,y+himg,x+tilew,y+rowh),fill=(23,39,33));
 for j,line in enumerate(textwrap.wrap(imgs[key]['title'],48)[:2]):d.text((x+15,y+himg+13+j*28),line,font=f(22,True),fill=(219,231,196))
d.text((pad,canvas.height-51),'Aucune carte cadastrale importée • rendu logiciel Chromium • fan project non officiel',font=f(20),fill=(160,185,167))
canvas.save(R/'RAPPORT_VISUEL_V0.29.png',optimize=True)
# Same-camera comparison uses screenshots only, no repaint of game objects.
bw=1800;ph=600;bp=Image.new('RGB',(bw,720),(13,24,22));dr=ImageDraw.Draw(bp)
for i,key in enumerate(['09_volet_ferme.png','10_volet_ouvert.png']):
 im=Image.open(R/'verification'/key).convert('RGB');im.thumbnail((880,ph),Image.Resampling.LANCZOS);bp.paste(im,(10+i*900,70));dr.text((25+i*900,20),'AVANT · volet fermé'if i==0 else'APRÈS · commande confirmée',font=f(26,True),fill=(203,226,178))
dr.text((24,672),'Même scène et même caméra ; le volet et sa collision changent réellement.',font=f(23),fill=(183,203,181));bp.save(R/'VOLET_AVANT_APRES_V0.29.png',optimize=True)
articles=[]
for i,e in enumerate(meta['images']):
 im=Image.open(R/'verification'/e['file']).convert('RGB');stream=io.BytesIO();im.save(stream,format='WEBP',quality=86,method=6);enc=base64.b64encode(stream.getvalue()).decode();articles.append(f'<article id="p{i+1}"><h2>{i+1:02d} / {html.escape(e["title"])}</h2><img class="{"portrait"if im.height>im.width else "landscape"}" src="data:image/webp;base64,{enc}" alt="{html.escape(e["title"])}"><p>{html.escape(e["note"])}</p><details><summary>Provenance de la capture</summary><pre>{html.escape(json.dumps(e["camera"],ensure_ascii=False,indent=2))}</pre><p>PNG original : verification/{html.escape(e["file"])}</p></details></article>')
nav=''.join(f'<a href="#p{i+1}">{i+1:02d} · {html.escape(e["title"])}</a>'for i,e in enumerate(meta['images']))
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mistral v0.29 — rapport visuel</title><style>body{margin:0;background:#101d18;color:#e3ead7;font:17px/1.7 system-ui,sans-serif}header,main{max-width:1250px;margin:auto;padding:32px}h1{font-size:clamp(32px,5vw,60px);line-height:1.12}header>p{max-width:950px;color:#bbcfbc}nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}a{color:#b8e8a2}nav a{padding:9px;border:1px solid #385242;text-decoration:none;font-size:14px}article{margin:0 0 55px;border-top:1px solid #52664e;padding-top:24px}h2{font-size:25px}img{display:block;max-width:100%;height:auto;border:1px solid #435f48}.portrait{max-width:min(390px,100%)}details{font-size:13px;color:#aec0af}pre{white-space:pre-wrap}footer{padding:35px;background:#0b1510;font-size:13px;word-break:break-word}@media(max-width:650px){header,main{padding:20px}body{font-size:15px}h2{font-size:21px}}</style><header><small>FAN PROJECT NON OFFICIEL · RAPPORT DE BUILD</small><h1>Les portes ont des oreilles</h1><p>v0.29 — Déduction, habilitations, trois contrôleurs physiques, trois locaux de service et infiltration. Les captures proviennent du HTML exact exécuté dans Chromium avec rendu logiciel. Les caméras, poses et quelques états sont préparés ; les prérequis et trajets sont testés séparément. Aucune image conceptuelle ni donnée géographique réelle n’est présentée comme une scène reconstruite.</p><nav>'''+nav+'</nav></header><main>'+''.join(articles)+'</main><footer>SHA-256 du HTML de jeu photographié : '+current+'<br>Images dérivées de PNG réels, encodées en WebP dans ce rapport autonome. Rendu non certifié sur GPU matériel ou iPhone réel.</footer></html>'
(R/'RAPPORT_VISUEL_V0.29.html').write_text(page)
print('REPORT',len(meta['images']),len(page))
