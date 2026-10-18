from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,html,io,base64,hashlib,textwrap
R=Path(__file__).resolve().parents[1];V=R/'verification';data=json.loads((V/'CAPTURES_V030.json').read_text())
sha=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest()
assert data['html_sha256']==sha and not data['errors'] and len(data['images'])==22
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(n,b=False):return ImageFont.truetype(bold if b else font,n)
W=1800;pad=36;gap=28;cw=(W-pad*2-gap)//2;ih=int(cw*960/1440);rh=ih+86;head=180;H=head+3*rh+2*gap+60
board=Image.new('RGB',(W,H),'#111d18');d=ImageDraw.Draw(board)
d.text((pad,30),'FALLOUT : MISTRAL  /  v0.30',font=f(39,True),fill='#efe2a9');d.text((pad,90),'SOUS LA CUIRASSE',font=f(27),fill='#b9d5b0');d.text((pad,135),'Captures du jeu exécuté · lieux fictifs · rendu logiciel · états préparés, tests séparés',font=f(18),fill='#a8b9a8')
picks=[('03_chassis_stationne.png','01  Un châssis physique dans la baie'),('08_pip_coeur.png','02  Six plaques et cœur conservé'),('12_devis_plaque.png','03  Une réparation, pas une guérison'),('15_ecrans_refractaires.png','04  Écrans réfractaires visibles'),('16_portillon_ferme.png','05  Avant l’épreuve : fermé'),('17_portillon_ouvert.png','06  Après l’épreuve : traversable')]
for i,(name,title)in enumerate(picks):
 x=pad+(i%2)*(cw+gap);y=head+(i//2)*(rh+gap);im=Image.open(V/name).convert('RGB').resize((cw,ih),Image.Resampling.LANCZOS);board.paste(im,(x,y));d.rectangle((x,y+ih,x+cw,y+rh),fill='#203229');d.text((x+16,y+ih+18),title,font=f(23,True),fill='#ecdfaa');d.text((x+16,y+ih+53),'Vue réelle du programme, pas une illustration conceptuelle.',font=f(15),fill='#b5c8b4')
d.text((pad,H-34),'Rapport intégral : 22 captures légendées dans le fichier HTML autonome.',font=f(18),fill='#a8b9a8');board.save(R/'RAPPORT_VISUEL_V0.30.png',optimize=True)
# Matched before/after gate, clearly labelled and unretouched beyond scaling.
pair=Image.new('RGB',(1800,720),'#111d18');pd=ImageDraw.Draw(pair);pd.text((30,22),'PORTILLON D’ESSAI  /  même scène, même caméra',font=f(30,True),fill='#e7dda8')
for i,name in enumerate(['16_portillon_ferme.png','17_portillon_ouvert.png']):
 im=Image.open(V/name).convert('RGB').resize((855,570),Image.Resampling.LANCZOS);x=30+i*885;pair.paste(im,(x,85));pd.text((x,675),['AVANT · collision active','APRÈS · passage effectivement ouvert'][i],font=f(24,True),fill='#c8deb9')
pair.save(R/'PORTILLON_AVANT_APRES_V0.30.png',optimize=True)
cards=[]
for a in data['images']:
 im=Image.open(V/a['file']).convert('RGB');im.thumbnail((1440,1000));buf=io.BytesIO();im.save(buf,format='JPEG',quality=84,optimize=True);enc=base64.b64encode(buf.getvalue()).decode()
 cards.append(f'<article><h2>{html.escape(a["title"])}</h2><img loading="lazy" src="data:image/jpeg;base64,{enc}" alt="{html.escape(a["title"])}"><p>{html.escape(a["note"])}</p><details><summary>Caméra et provenance</summary><pre>{html.escape(json.dumps(a["camera"],ensure_ascii=False,indent=2))}</pre><small>HTML SHA-256 : {sha}</small></details></article>')
out='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Rapport visuel · Mistral v0.30</title><style>body{margin:0;background:#111d18;color:#d4dfc5;font:16px/1.6 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:28px}header{padding:24px 0 35px;border-bottom:1px solid #6a7965}h1,h2{color:#ede0a8;line-height:1.2}h1{font-size:clamp(28px,4vw,50px)}article{background:#1b2b23;border:1px solid #465844;padding:20px;margin:28px 0}img{display:block;max-width:100%;height:auto;margin:auto}p{max-width:1050px}small{word-break:break-all}pre{overflow:auto;color:#b0cdb0}details{font-size:13px}a{color:#e2d69a}@media(max-width:600px){main{padding:12px}article{padding:12px}}</style><main><header><h1>FALLOUT : MISTRAL — v0.30</h1><h2>Sous la cuirasse</h2><p>22 captures du HTML exécuté. Les caméras et certains états de blessure, de charge ou de quête sont préparés pour présenter les systèmes. Les prérequis et parcours au contrôleur sont testés séparément. Les lieux et le châssis M-45 sont fictifs ; aucune cartographie réelle n’est revendiquée.</p><p>Chromium avec rendu logiciel. Pas de certification GPU ou iPhone. Les images proviennent du jeu, pas d’un générateur d’illustrations.</p></header>'''+''.join(cards)+'</main></html>'
(R/'RAPPORT_VISUEL_V0.30.html').write_text(out)
(R/'docs/RAPPORT_VISUEL_V0.30.md').write_text('# Rapport visuel v0.30\n\n22 captures du HTML exact ; caméras et états préparés, vérifications séparées. Voir le rapport HTML autonome et les PNG originaux sous verification/.\n\n'+'\n\n'.join('## '+a['title']+'\n\n'+a['note']+'\n\n![Capture](../verification/'+a['file']+')'for a in data['images']))
print('Visual report',len(cards),'captures', (R/'RAPPORT_VISUEL_V0.30.png').stat().st_size)
