from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,math
R=Path(__file__).resolve().parents[2];O=R/'verification/v048';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.48.html').read_text();shots=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.set_default_timeout(15000);p.on('pageerror',lambda e:errors.append(e.stack));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):
  path=O/(name+'.png');p.screenshot(path=str(path));shots.append({'file':path.name,'title':title,'note':note});print('CAP',name,flush=True)
 shot('01_menu','Version intégrée','Menu du HTML livré ; le banc de coutures reste séparé de la campagne.')
 c('v046Lab');c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False});c('v046SetTime',13,0);c('v046Render');sig=c('v046Signature');start=c('v047Info')['pos'];ll=c('v046LL')
 shot('02_avant','Extérieur conservé','Banc synthétique identifié : bâtiments, cour, route et masque forestier. Ce n’est pas Marseille.')
 c('v048Control',{'pausePhase':'relief','pauseMs':1800});c('v046ClearCache');p.evaluate('(ll)=>{window.__capJob=__MISTRAL_DEBUG.v046Load(...ll)}',ll);p.wait_for_function('__MISTRAL_DEBUG.v048Info().preparation?.phase==="relief"');
 shot('03_chargement','Préparation interruptible','Écran réel du chargement, avec pause QA injectée pour photographier l’étape terrain ; aucune performance inventée.');p.click('#v046Cancel');c('v048Control',{'pausePhase':None,'pauseMs':0});c('v046Load',*ll)
 # A real interior from the existing catalogue, loaded through its entry function.
 site=next(n for n in c('v042Catalog') if n['kind']=='shelter');c('v048RememberScene');c('v042Enter',site['id']);p.wait_for_timeout(200);c('v046CameraAt',[-18,1.75,39],0,0);c('v046Render')
 shot('04_passage','Cloisons et ouverture','Intérieur du jeu : le passage existe entre deux cloisons, y compris pour les segments définis en sens inverse.')
 c('v027Open','map','integrity');shot('05_diagnostic','La scène attend le retour','Diagnostic produit : un seul extérieur retenu, mémoire estimée et pauses coopératives réellement comptées.');c('closePip')
 c('v046Control',{'fail':'all'});c('v046ClearCache');c('v042Exit');c('v046SetTime',13,0);c('v046Render');back=c('v046Signature')
 shot('06_apres','Même extérieur, sans requête','Retour à la scène conservée alors que le fournisseur de test est volontairement en échec.')
 report={'sameGeometry':back==sig,'samePosition':c('v047Info')['pos']==start,'sameReferences':c('v048SceneSame'),'state':c('v048Info')}
 c('v046Control',{'fail':None});c('v048Control',{'returnBudget':0});c('v042Enter',site['id']);p.wait_for_timeout(180);c('v046Render');c('v046ClearCache');c('v046Control',{'fail':'all'});c('v042Exit');p.wait_for_function('__MISTRAL_DEBUG.v046Info().phase==="failed"')
 shot('07_echec','Une sortie peut échouer sans perdre le lieu','Échec réseau simulé sans scène retenue : réessai et annulation gardent les données de l’intérieur valides.')
 p.click('#v046Cancel');c('v046Render');shot('08_annulation','Retour dans l’intérieur','Après annulation du chargement de sortie, l’intérieur reste actif. Le joueur n’est pas envoyé dans un quartier vide.')
 b.close()
(O/'VISUAL_EVIDENCE.json').write_text(json.dumps({'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'shots':shots,'returnComparison':report,'errors':errors,'scope':'Captures du HTML réellement exécuté. Extérieurs synthétiques signalés ; caméras et une pause de préparation contrôlées pour photographier les vérifications.'},ensure_ascii=False,indent=2)+'\n')
# Contact sheet with full, readable captions. Screenshots are not regenerated art.
fontdir=Path('/usr/share/fonts/truetype/dejavu');font=lambda n,b=False:ImageFont.truetype(str(fontdir/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),n)
W=1488;pad=28;tw=702;th=439;rowh=540;head=156;canvas=Image.new('RGB',(W,head+4*rowh+28),'#0c1511');d=ImageDraw.Draw(canvas)
d.text((pad,25),'FALLOUT : MISTRAL',font=font(38,True),fill='#ebe6c5');d.text((pad,79),'v0.48 — Reprises sans rupture',font=font(24),fill='#bccfae');d.text((pad,121),'Captures réelles du programme • Banc extérieur synthétique clairement identifié',font=font(17),fill='#94ae95')
import textwrap
for i,s in enumerate(shots):
 x=pad+(i%2)*(tw+28);y=head+(i//2)*rowh;im=Image.open(O/s['file']).convert('RGB');im=ImageOps.contain(im,(tw,th));canvas.paste(im,(x,y));d.rectangle((x,y+th,x+tw,y+rowh-16),fill='#17251d');d.text((x+12,y+th+9),s['title'],font=font(18,True),fill='#eadba5')
 for k,line in enumerate(textwrap.wrap(s['note'],width=90)):
  d.text((x+12,y+th+36+k*18),line,font=font(13),fill='#bacab3')
canvas.save(R/'RAPPORT_VISUEL_V0.48.png');print('REPORT',R/'RAPPORT_VISUEL_V0.48.png','errors',errors);raise SystemExit(bool(errors or not report['sameGeometry']))
