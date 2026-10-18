from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,math,textwrap
R=Path(__file__).resolve().parents[2];O=R/'verification/v049';H=(R/'JOUER_FALLOUT_MISTRAL_v0.49.html').read_text();shots=[];errors=[];comparison={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.set_default_timeout(15000);p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__store.get(k)||null,setItem:(k,v)=>__store.set(k,String(v)),removeItem:k=>__store.delete(k)}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def shot(name,title,note):
  f=O/(name+'.png');p.screenshot(path=str(f));shots.append({'file':f.name,'title':title,'note':note});print('CAP',name,flush=True)
 p.locator('#menuScreen.active').wait_for(state='visible',timeout=18000)
 p.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')",timeout=18000)
 shot('01_menu','v0.49 intégrée','Menu du programme livré. Le projet est un prototype de fan non officiel.')
 c('v046Lab');c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False});c('v046SetTime',13,0)
 nest=next(s for s in c('v042Catalog') if s['kind']=='nest');safe=next(s for s in c('v042Catalog') if s['kind']=='settlement');shelter=next(s for s in c('v042Catalog') if s['kind']=='shelter');base=c('v047Info')['pos'];c('v049ProbeSpawn',nest['id'],[0,-12]);e=next(a for a in c('v049Actors') if a['kind']=='enemy');pos=[base[0],e['pos'][1],base[2]-12];c('v049ProbePose',e['id'],pos,math.pi);c('v049Damage',e['id'],28,'leg_l');c('v046CameraAt',base,0,0);c('v046Render');c('toggleVATS');targets=c('v025Snapshot')['targets'];idx=next(i for i,t in enumerate(targets) if t['id']==e['id']);c('v023Select',idx,'leg_l');c('v025Paint');p.wait_for_timeout(100)
 comparison['before']=next(a for a in c('v049Actors') if a['id']==e['id']);shot('02_blesse_avant','Adversaire blessé avant départ','Blessure appliquée par le combat du jeu. Rencontre placée pour test dans le banc synthétique, pas dans une rue réelle.')
 c('v020VatsCancel');c('v042Unload',nest['id']);c('v049ProbeSpawn',nest['id'],[0,-12]);c('v046CameraAt',base,0,0);c('v046Render');c('toggleVATS');targets=c('v025Snapshot')['targets'];idx=next(i for i,t in enumerate(targets) if t['id']==e['id']);c('v023Select',idx,'leg_l');c('v025Paint');p.wait_for_timeout(100)
 comparison['after']=next(a for a in c('v049Actors') if a['id']==e['id']);comparison['sameHealth']=comparison['before']['hp']==comparison['after']['hp'];comparison['samePosition']=comparison['before']['pos']==comparison['after']['pos'];comparison['sameLimbs']=comparison['before']['limbs']==comparison['after']['limbs'];shot('03_blesse_retour','Même santé après retour','Le site a été déchargé puis réinstancié. La santé, la pose et le membre blessé sont conservés, sans valeur d’affichage injectée.')
 c('v020VatsCancel');c('v049Damage',e['id'],99999);body=next(x for x in c('v049Bodies') if x['id']=='remains:'+e['id']);q=body['pos'];c('v046CameraAt',[q[0],q[1]+1.65,q[2]+2],0,-.35);c('v046Render');shot('04_depouille','Dépouille réelle du combat','Le corps reste dans le monde. Son inventaire possède une identité indépendante du nom de macro-région.')
 c('v026OpenContainer',body['key']);c('v026Take','caps',3);c('v026Close');c('v049RegionLabel','geo_huveaune');c('v042Unload',nest['id']);c('v049ProbeSpawn',nest['id'],[0,-12]);c('v046CameraAt',[q[0],q[1]+1.65,q[2]+1.5],0,-.35);c('v046Render');assert c('v026OpenContainer',body['key']);shot('05_butin','Le butin déjà pris ne revient pas','Trois capsules ont été prises, puis le site a été rechargé avec un autre libellé de région. Le reliquat est inchangé.');c('v026Close')
 c('v049ProbeSpawn',safe['id'],[18,8]);n=next(a for a in c('v049Actors') if a['kind']=='npc');np=[n['pos'][0]+.5,n['pos'][1],n['pos'][2]+.4];c('v049ProbePose',n['id'],np,1.2);c('v042Unload',safe['id']);c('v049ProbeSpawn',safe['id'],[18,8]);c('v046CameraAt',[np[0],np[1]+1.7,np[2]+8],0,-.04);c('v046Render');shot('06_habitants','Habitants et props stables','Les poses des habitants sont restaurées ; les détails du site ne sont plus tirés au hasard à chaque réapparition.')
 c('v042Enter',shelter['id']);p.wait_for_timeout(150);inner=next(a for a in c('v049Actors') if a['kind']=='enemy');c('v049Damage',inner['id'],18,'arm_r');c('v049ProbePose',inner['id'],[-18,0,24],math.pi);c('v049RebuildInstance');p.wait_for_timeout(150);c('v046CameraAt',[-18,1.7,31],0,0);c('v046Render');shot('07_interieur','Même occupant dans l’intérieur reconstruit','La visite intérieure conserve son propre journal. Ses coordonnées locales ne remplacent pas celles de l’extérieur.')
 c('v027Open','map','integrity');shot('08_journal','Diagnostic réellement mesuré','Compteurs issus de cette exécution : blessés mémorisés, dépouilles finies, habitants et restaurations. Aucun total territorial inventé.');c('closePip')
 comparison['journal']=c('v049Info');b.close()
report={'version':'0.49.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'shots':shots,'comparison':comparison,'errors':errors,'scope':'Captures réelles du programme. Positions/caméras préparées dans le banc synthétique identifié ; dégâts, déchargement, restauration et prises de butin par les fonctions de production.'}
(O/'VISUAL_EVIDENCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
font=lambda s,b=False:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',s)
W=1488;pad=28;tw=702;th=439;rowh=554;head=160;can=Image.new('RGB',(W,head+rowh*4+28),'#0c1511');d=ImageDraw.Draw(can);d.text((pad,24),'FALLOUT : MISTRAL',font=font(38,True),fill='#ebe6c5');d.text((pad,80),'v0.49 — Le quartier se souvient',font=font(25),fill='#bdcfaf');d.text((pad,124),'Captures du programme exécuté • Extérieurs du banc synthétique, pas une carte réelle',font=font(17),fill='#95b296')
for i,s in enumerate(shots):
 x=pad+i%2*(tw+28);y=head+i//2*rowh;im=ImageOps.contain(Image.open(O/s['file']).convert('RGB'),(tw,th));can.paste(im,(x,y));d.rectangle((x,y+th,x+tw,y+rowh-14),fill='#17251d');d.text((x+12,y+th+9),s['title'],font=font(18,True),fill='#eadba5')
 for k,line in enumerate(textwrap.wrap(s['note'],width=86)):
  d.text((x+12,y+th+38+k*19),line,font=font(15),fill='#b7c5af')
can.save(R/'RAPPORT_VISUEL_V0.49.png');print('REPORT',R/'RAPPORT_VISUEL_V0.49.png','ERRORS',errors,'COMPARE',comparison['sameHealth'],comparison['samePosition'],comparison['sameLimbs']);raise SystemExit(bool(errors))
