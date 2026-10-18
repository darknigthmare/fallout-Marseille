"""Re-extract distributed archives, verify all hashes, rebuild, execute the HTML
read from the small ZIP, and exercise real UI controls. Storage adapter declared."""
from pathlib import Path
import json,zipfile,hashlib,shutil,subprocess,sys
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];P=R.parent;T=P/'MISTRAL_V030_LIVRAISON_TESTS';rows=[];errors=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(v,name,detail=None):rows.append({'ok':bool(v),'name':name,'detail':detail});print(('OK 'if v else 'FAIL ')+name,flush=True)
if T.exists():shutil.rmtree(T)
T.mkdir()
htmlbytes=None
for typ,zname in [('game','FALLOUT_MISTRAL_v0.30_JEU_SEUL.zip'),('source','FALLOUT_MISTRAL_v0.30_PROJET_COMPLET.zip')]:
 with zipfile.ZipFile(P/zname)as z:
  ck(z.testzip()is None,typ+' : intégrité ZIP');z.extractall(T/typ)
 d=T/typ if typ=='game'else T/typ/'FALLOUT_MISTRAL_v0.30';manifest=json.loads((d/'MANIFEST_SHA256.json').read_text());bad=[r['path']for r in manifest['files']if not (d/r['path']).is_file()or sha((d/r['path']).read_bytes())!=r['sha256']]
 ck(not bad,typ+' : chaque fichier du manifeste présent et identique',{'files':len(manifest['files']),'bad':bad})
 b=(d/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes();ck(b==(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes(),typ+' : HTML identique au programme testé')
 if typ=='game':htmlbytes=b
 else:
  ret=subprocess.run([sys.executable,'tools/build_single.py'],cwd=d,capture_output=True,text=True)
  ck(ret.returncode==0,'Reconstruction depuis les seules sources extraites',ret.stdout[-200:]);ck((d/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()==b,'HTML reconstruit identique octet pour octet')
base=json.loads((R/'data/BASE_V029.json').read_text());bad=[e['path']for e in base['preserved']if not (R/e['path']).is_file()or sha((R/e['path']).read_bytes())!=e['sha256']];ck(not bad,'Références v0.29 intactes',{'files':len(base['preserved']),'bad':bad})
qa=json.loads((R/'verification/QA_GLOBAL_V030.json').read_text());ck(qa['failed']==0 and qa['same_html']and qa['html_sha256']==sha(htmlbytes),'Le paquet correspond aux 23 suites finales exécutées')
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960},has_touch=True);p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(7000);p.set_content(htmlbytes.decode(),wait_until='load');p.locator('#btnV030').wait_for(timeout=30000);p.wait_for_timeout(2300)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
 ck(p.title().endswith('Sous la cuirasse')and p.locator('#btnV030').is_visible(),'Titre et bouton de la build relue depuis le ZIP')
 blocked=p.evaluate("(()=>{try{localStorage.setItem('__test','1');return false}catch(e){return e.name==='SecurityError'}})()");ck(blocked,'Refus natif de l’origine opaque explicitement vérifié')
 p.evaluate("window.__STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__STORE[k]??null,setItem:(k,v)=>__STORE[k]=String(v),removeItem:k=>delete __STORE[k]}})")
 p.evaluate("localStorage.setItem('fallout_mistral_save_v030','campagne-conservee');localStorage.setItem('fallout_mistral_sandbox_v029','ancienne-exploration')")
 p.once('dialog',lambda d:d.dismiss());p.locator('#btnV030').click();ck(c('getMode')=='MENU','Annuler le nouveau départ conserve le menu et la partie')
 p.once('dialog',lambda d:d.accept());p.locator('#btnV030').click();c('v021MuteEnemies');ck(c('getState')['player']['zone']=='mooring_station','Départ effectif à la baie d’assistance');ck('mistralRig'not in c('getState')['equipment']['ownedArmors'],'Pas d’armure attribuée gratuitement au départ')
 ck(p.evaluate("localStorage.getItem('fallout_mistral_save_v030')")=='campagne-conservee','Campagne non écrasée par le départ séparé');ck(p.evaluate("localStorage.getItem('fallout_mistral_sandbox_v029')")=='ancienne-exploration','Ancienne exploration v029 inchangée')
 c('v020Approach','v030:alba');ck(c('v020Interact','v030:alba')is True,'Alba abordable sur place depuis le programme distribué');p.locator('#dialogueChoices button').filter(has_text='rapport').first.click();ck(c('v030State')['quest']['accepted'],'Acceptation par véritable clic de dialogue')
 c('v020ModalDismiss');p.keyboard.press('u');ck(c('getMode')=='PIP'and 'Aucun châssis porté'in p.locator('#pipboy').inner_text(),'U ouvre un diagnostic vide honnête, sans inventaire offert')
 # Controlled suit supplied only to exercise UI transaction on the distributed HTML.
 c('v030Set',{'rig':'mistralRig','core':None,'active':False});c('v020Seed',{'fusionCore':1});c('v030Show');p.locator('[data-p27="p30:insert"][data-arg="new"]').click();ck(c('v030State')['core']==100 and c('getState')['ammo']['fusionCore']==0,'Bouton d’insertion retire réellement un cœur neuf')
 p.locator('[data-p27="p30:power"]').click();ck(c('v030Online'),'Assistance activée au clic');p.locator('[data-p27="p30:power"]').click();p.locator('[data-p27="p30:eject"]').click();ck(c('v030State')['core']is None and c('v030State')['spares']==[100],'Éjection dans une réserve séparée, sans cellule neuve recréée')
 p.set_viewport_size({'width':390,'height':844});p.locator('.p30-slots button[data-arg="leftArm"]').tap();ck(p.locator('.p30-slots button[data-arg="leftArm"]').get_attribute('aria-pressed')=='true','Véritable geste tactile sélectionne le bras gauche')
 ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Interface étroite sans débordement horizontal global');c('v027Open','data','system')
 with p.expect_download()as download:p.locator('[data-p27="export"]').tap()
 obj=json.loads(Path(download.value.path()).read_text());ck(obj['v030']['spares']==[100]and obj['v030']['core']is None,'Export JSON effectivement téléchargé avec état énergétique conservé')
 ck(not errors,'Aucune exception JavaScript dans le programme du ZIP',errors);b.close()
report={'version':'0.30.0','html_sha256':sha(htmlbytes),'passed':sum(r['ok']for r in rows),'failed':sum(not r['ok']for r in rows),'total':len(rows),'checks':rows,'errors':errors,'scope':'Re-extracted exact HTML via set_content, software Chromium; native opaque storage rejection checked then explicit memory adapter. Seeded suit only for UI controls, not normal progression. No GPU/iPhone certification.'}
(P/'FALLOUT_MISTRAL_v0.30_CONTROLES_LIVRAISON.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DELIVERY',report['passed'],report['failed']);raise SystemExit(bool(report['failed']))
