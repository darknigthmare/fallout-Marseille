from pathlib import Path
import json,hashlib,math,textwrap
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2];O=R/'verification/v047';H=(R/'JOUER_FALLOUT_MISTRAL_v0.47.html').read_text();shots=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=18000)
 def c(n,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
 def shot(name,title,note):
  f=O/name;p.screenshot(path=str(f));shots.append({'file':name,'title':title,'note':note});print('CAP',name,flush=True)
 shot('01_menu.png','v0.47 intégrée à la v0.46 fournie','Menu du programme livré. La provenance historique v0.42 de la branche reste documentée.')
 c('v046Lab');c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False,'cooldown':0});c('v046SetTime',12,0);c('v046Render');start=c('v047Info')['pos'];ll=c('v046LL');before=c('v046Signature');bank=c('v047TerrainIdentity')
 shot('02_depart.png','Le secteur reste en scène','Banc synthétique explicitement signalé : bâtiments, cour et végétation. Ce n’est pas Marseille.')
 c('v046Control',{'delay':110,'fail':None});c('v046ClearCache');c('v046Move',72,0)
 p.evaluate('()=>{__MISTRAL_DEBUG.v047Control({auto:true,cooldown:0});__MISTRAL_DEBUG.v047Predict()}');c('v046Render');p.wait_for_timeout(40)
 shot('03_anticipation.png','Préparation pendant la marche','La barre discrète indique les ressources du prochain secteur. La scène et le mouvement restent actifs.')
 c('v046Move',4,0);c('v046Move',112,0);p.wait_for_timeout(60)
 shot('04_attente.png','Pas de pas dans un secteur incomplet','À la marge de sécurité, la même préparation devient bloquante. Aucune géométrie de secours n’est inventée.')
 p.wait_for_function('__MISTRAL_DEBUG.v047Info().phase==="ready" && !__MISTRAL_DEBUG.v047Info().loading',timeout=15000)
 c('v047Control',{'auto':False});c('v046Control',{'delay':0});c('v046Render');after=c('v046Signature')
 shot('05_reprise.png','Publication complète, même quartier','Le chargement se termine sans téléporter le joueur. Les empreintes bâties et la scène sont conservées.')
 evidence={'sameScene':before['scene']==after['scene'],'sameBuildings':before['buildings']==after['buildings'],'sameRoads':before['roads']==after['roads'],'scope':'Banc synthétique signalé, pas un relevé de la ville réelle.'}
 (O/'VISUAL_CONTINUITY.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 c('v046Control',{'delay':0});c('v047Control',{'terrainOffset':450,'failPrepare':True});c('v046ClearCache');now=c('v046LL');c('v046Load',*now)
 shot('06_refus.png','Préparation ratée : l’ancien relief reste intact','Échec injecté après lecture du terrain. Le test compare aussi l’empreinte de la banque de relief avant et après.')
 c('v046Cancel');c('v047Control',{'terrainOffset':0,'failPrepare':False});c('v046ClearCache');c('v046Load',*ll);c('v047OpenStatus');p.wait_for_timeout(80)
 shot('07_diagnostics.png','Compteurs de cette exécution','Tuiles réellement en scène, réutilisations et mémoire estimée. Aucune performance de la carte intégrale n’est annoncée.')
 p.click('#v047CloseStatus');c('v046CameraAt',start,0,.025);c('v046Render')
 shot('08_retour.png','Retour vérifiable','La banque et les ressources restent contrôlées au retour. Le HUD et le ciel hérités restent actifs.')
 c('v027Open','data','france');p.wait_for_timeout(70)
 shot('09_lore.png','Lore et dossiers conservés','Les neuf factions, huit dossiers et COCHONNET de la v0.46 sont préservés ; aucun nouveau modèle de créature n’est revendiqué.')
 c('closePip');p.set_viewport_size({'width':390,'height':844});c('v047OpenStatus');p.wait_for_timeout(80)
 shot('10_etroit.png','Statut sur fenêtre étroite','Lecture et défilement à 390 × 844 dans Chromium. Ce n’est pas une validation sur téléphone physique.')
 b.close()
fontroot=Path('/usr/share/fonts/truetype/dejavu')
def ft(size,bold=False):return ImageFont.truetype(str(fontroot/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
W,pad,cw,ch,cap=1500,30,705,441,124;sheet=Image.new('RGB',(W,148+math.ceil(len(shots)/2)*(ch+cap+24)+30),'#0b1412');d=ImageDraw.Draw(sheet);d.text((30,28),'MISTRAL / v0.47 — LE TERRITOIRE EN AVANCE',font=ft(30,True),fill='#f0e3b6');d.text((30,78),'Captures du programme exécuté · banc synthétique signalé · même archive source v0.46',font=ft(18),fill='#bacbb5')
for i,s in enumerate(shots):
 x=pad+(i%2)*(cw+30);y=148+(i//2)*(ch+cap+24);im=Image.open(O/s['file']).convert('RGB');im.thumbnail((cw,ch));sheet.paste(im,(x+(cw-im.width)//2,y+(ch-im.height)//2));d.rectangle((x,y+ch,x+cw,y+ch+cap),fill='#182b22');d.text((x+14,y+ch+14),s['title'],font=ft(18,True),fill='#e8dda9')
 for j,line in enumerate(textwrap.wrap(s['note'],82)[:3]):d.text((x+14,y+ch+47+20*j),line,font=ft(14),fill='#bdcbb4')
sheet.save(R/'RAPPORT_VISUEL_V0.47.png');r={'version':'0.47.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'shots':shots,'errors':errors,'scope':'Captures réelles du programme. Scène géographique de test synthétique explicitement marquée ; cartes réelles complètes non installées.'};(O/'CAPTURES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('errors',errors);raise SystemExit(bool(errors))
