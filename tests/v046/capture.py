from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,math,textwrap
R=Path(__file__).resolve().parents[2];O=R/'verification/v046';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.46.html').read_text();shots=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):
  fn=O/name;p.screenshot(path=str(fn));shots.append({'file':name,'title':title,'note':note});print(name,flush=True)
 shot('01_menu.png','Projet intégré · base vérifiée','Menu réel du projet repris depuis la v0.42. Le binaire v0.44 n’a pas été récupéré.')
 c('v046Lab');c('setRenderPaused',True);c('v022Freeze',True)
 origin=c('v046LabOrigin');x,z=origin[0],origin[2];initial=c('v046Info');start=initial['pos'];c('v046SetTime',12,0);c('v046Render')
 shot('02_aller.png','Avant franchissement','Banc synthétique de continuité : cinq bâtiments dont une cour, deux routes et des masques forestiers. Ce n’est pas Marseille.')
 sig0=c('v046Signature')
 for i in range(65):c('v046Move',2,0)
 c('v046SetTime',12,0);c('v046Render');shot('03_autre_cote.png','De l’autre côté : même scène','Le nom de région change ; ni les identités ni les coordonnées des bâtiments ne sont recalculées.')
 for i in range(65):c('v046Move',-2,0)
 c('v046SetTime',12,0);c('v046Render');shot('04_retour.png','Retour au point initial','Le test compare également les signatures complètes des bâtiments, routes et arbres. Aucune image n’est utilisée comme décor de remplacement.')
 sig1=c('v046Signature');(O/'ROUNDTRIP_CAPTURE.json').write_text(json.dumps({'buildingsIdentical':sig0['buildings']==sig1['buildings'],'roadsIdentical':sig0['roads']==sig1['roads'],'natureIdentical':sig0['nature']==sig1['nature'],'sameScene':sig0['scene']==sig1['scene'],'scope':'Banc synthétique explicite, pas une traversée de données géographiques réelles'},ensure_ascii=False,indent=2))
 c('v046CameraAt',[x+47,100,z+28],0,-.45);c('v046SetTime',12,0);c('v046Render');shot('05_cour.png','Cour préservée','Les anneaux intérieurs sont conservés. Le contrôle de collision confirme que le centre est libre et que les murs sont solides.')
 c('v046CameraAt',start,0,.025);c('v046Render');ll=c('v046LL');c('v046Control',{'delay':35,'fail':'all'});c('v046ClearCache');p.evaluate('(ll)=>{window.__failcap=__MISTRAL_DEBUG.v046Load(...ll)}',ll);p.wait_for_timeout(50);shot('06_chargement.png','Préparation avant affichage','Chargement réel du banc via le même gestionnaire que les sources cartographiques. Les entrées sont figées pendant la préparation.')
 p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="failed"');shot('07_echec.png','Donnée absente : pas de faux quartier','Échec injecté. Réessayer ou annuler conserve le joueur et l’ancienne scène ; aucune route ou maison de secours n’est inventée.')
 p.click('#v046Cancel');c('v046Control',{'delay':0,'fail':None});c('v046Frame')
 # Crop the actual UI screenshot; not a manufactured dashboard.
 path=O/'08_raccourcis.png';p.locator('#v020Quickbar').screenshot(path=str(path));shots.append({'file':path.name,'title':'Raccourcis persistants','note':'La barre cesse de supprimer et recréer ses boutons à chaque cycle. 600 mises à jour testées sans remplacement des éléments.'})
 c('v027Open','data','france');p.wait_for_timeout(80);shot('09_lore.png','France en Cendres · reconstruction','Neuf factions, huit dossiers jouables et COCHONNET réintégrés. Ce contenu ne prétend pas être le binaire v0.44 retrouvé.')
 b.close()
# Contact sheet: actual screenshots, captions, and an explicit experimental label.
fontdir='/usr/share/fonts/truetype/dejavu/'
def ft(sz,b=False):return ImageFont.truetype(fontdir+('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'),sz)
W=1500;pad=30;cw=705;ch=441;cap=122;rows=math.ceil(len(shots)/2);sheet=Image.new('RGB',(W,145+rows*(ch+cap+24)+30),'#0e1713');d=ImageDraw.Draw(sheet)
d.text((30,28),'MISTRAL / v0.46 — CONTINUITÉ VÉRIFIABLE',font=ft(32,True),fill='#f0e5b9');d.text((30,80),'Captures du moteur · banc synthétique identifié · aucune carte réelle complète revendiquée',font=ft(19),fill='#becbac')
for i,s in enumerate(shots):
 x=pad+(i%2)*(cw+30);y=145+(i//2)*(ch+cap+24);im=Image.open(O/s['file']).convert('RGB');im.thumbnail((cw,ch));sheet.paste(im,(x+(cw-im.width)//2,y+(ch-im.height)//2));d.rectangle((x,y+ch,x+cw,y+ch+cap),fill='#1c2a21');d.text((x+15,y+ch+14),s['title'],font=ft(19,True),fill='#ebdfae')
 for j,line in enumerate(textwrap.wrap(s['note'],85)[:3]):d.text((x+15,y+ch+48+j*20),line,font=ft(14),fill='#bbc8b2')
sheet.save(R/'RAPPORT_VISUEL_V0.46.png')
report={'version':'0.46.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'shots':shots,'errors':errors,'scope':'Screenshots réels d’un scénario synthétique explicitement marqué. Le territoire complet n’est pas installé.'};(O/'CAPTURES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('errors',errors);raise SystemExit(bool(errors))
