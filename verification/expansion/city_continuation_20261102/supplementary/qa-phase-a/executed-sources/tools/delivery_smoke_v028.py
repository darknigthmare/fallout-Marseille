#!/usr/bin/env python3
"""Fresh-browser checks on bytes read back from the distributed game ZIP.
Results appended outside the archives so their hashes remain final."""
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import zipfile,json,hashlib,traceback
R=Path(__file__).resolve().parents[1];P=R.parent;file=P/'FALLOUT_MISTRAL_v0.28_CONTROLES_LIVRAISON.json';report=json.loads(file.read_text());errors=[];rows=[]
def ck(ok,name,detail=None):rows.append(dict(ok=bool(ok),name=name,detail=detail));print(('OK 'if ok else 'FAIL ')+name,flush=True)
with zipfile.ZipFile(P/'FALLOUT_MISTRAL_v0.28_JEU_SEUL.zip')as z:H=z.read('JOUER_FALLOUT_MISTRAL_v0.28.html').decode()
ck(hashlib.sha256(H.encode()).hexdigest()==report['html_sha256'],'HTML relu du ZIP : empreinte identique aux quinze suites')
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960},accept_downloads=True);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV028').wait_for(timeout=30000);p.wait_for_timeout(2200)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  ck('v0.28' in p.title() and 'Tenir debout' in p.title(),'Titre et bouton du nouveau départ réellement chargés')
  c('v020Load','relay_cold');ck(c('save') is False,'Refus du stockage natif : pas de succès fictif')
  p.evaluate("window.__DELIVERY_STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__DELIVERY_STORE[k]??null,setItem:(k,v)=>__DELIVERY_STORE[k]=String(v),removeItem:k=>delete __DELIVERY_STORE[k]}})")
  c('v020SetPlayer',{'caps':317});c('save');keys=c('v018Keys');camp=p.evaluate('(k)=>localStorage.getItem(k)',keys['campaign']);p.evaluate('localStorage.setItem("fallout_mistral_sandbox_v027","ancienne-exploration-conservee")')
  p.once('dialog',lambda d:d.dismiss());ck(c('v028Start') is False,'Annuler le nouveau départ est sans effet')
  p.once('dialog',lambda d:d.accept());ck(c('v028Start') is True,'Confirmer démarre la véritable exploration séparée')
  ck(p.evaluate('(k)=>localStorage.getItem(k)',keys['campaign'])==camp,'Campagne antérieure inchangée après le nouveau départ')
  ck(p.evaluate('localStorage.getItem("fallout_mistral_sandbox_v027")')=='ancienne-exploration-conservee','Ancienne clé d’exploration v027 intacte')
  ck(s()['player']['zone']=='relay_cold' and c('getMode')=='PLAYING','Arrivée dans le bon intérieur, contrôle du personnage actif')
  ck(all(v==100 for v in s()['v028']['limbs'].values()),'Aucune blessure imposée au départ')
  ck(s()['inventory']['fieldSplint']==1 and s()['inventory']['traumaKit']==1,'Attelle et trousse de départ présentes une fois')
  ck(set(s()['equipment']['ownedWeapons'])=={'pistol10','pipeCarbine'},'Deux armes de départ, pas tout le catalogue')
  p.keyboard.press('l');ck(s()['v028']['lamp'],'L allume la lampe dans le HTML distribué')
  p.keyboard.press('Tab');ck(p.locator('.p28-limbs button').count()==6 and c('getMode')=='PIP','Tab ouvre les six régions de santé')
  p.locator('.p28-limbs [data-arg="leftArm"]').click();ck('Bras gauche' in p.locator('.p28-health-detail h2').inner_text(),'Sélection du bras par clic natif dans le ZIP')
  p.locator('[data-p27="p28:lamp"]').first.click();ck(not s()['v028']['lamp'],'Bouton du boîtier éteint la même lampe')
  p.keyboard.press('Tab');ck(c('getMode')=='PLAYING','Rangement du boîtier rend le contrôle du monde')
  c('v021MuteEnemies');near=c('v020Approach','v028:game');ck(bool(near),'Cassette physique accessible dans le jeu distribué');c('v020Interact','v028:game');c('v020ModalDismiss');c('v027Open','radio','games')
  ck(s()['v028']['game']['unlocked'] and p.locator('.p28-tile').count()==25,'Cassette acquise : grille intégrée disponible')
  before=c('v028GameState')['moves'];p.locator('[data-p27="p28:rotate"][data-arg="11"]').click();ck(c('v028GameState')['moves']==before+1,'Rotation effective d’une case, sans relancer le jeu')
  c('v027Open','data','system')
  with p.expect_download()as d:p.locator('[data-p27="export"]').click()
  dest=P/'MISTRAL_V028_VERIFY/delivery_export.json';d.value.save_as(dest);raw=json.loads(dest.read_text());ck(raw['v028']['game']['unlocked'] and raw['v028']['game']['levels']['0']['moves']==before+1,'Export JSON réellement téléchargé inclut le nouveau circuit')
  ck(all(v==100 for v in raw['v028']['limbs'].values()),'L’export conserve aussi l’état corporel')
  p.set_viewport_size({'width':390,'height':844});c('v027Open','radio','games');ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Fenêtre étroite : aucune largeur hors page')
  ck('SoftwareRenderer' in c('v020Renderer')['class'],'Rendu testé correctement identifié comme logiciel')
 except Exception:ck(False,'Exception lors du contrôle du ZIP',traceback.format_exc())
 ck(not errors,'Aucune exception JavaScript dans le navigateur de livraison',errors);b.close()
ck((R/'RAPPORT_VISUEL_V0.28.html').read_text().count('<article id="capture-')==23,'Rapport autonome contient vingt-trois captures documentées')
report['checks']=[x for x in report['checks']if not x.get('browser')]+[dict(x,browser=True)for x in rows];report['passed']=sum(x['ok']for x in report['checks']);report['failed']=sum(not x['ok']for x in report['checks']);report['browser_scope']='HTML exact relu du ZIP, set_content Chromium logiciel ; refus natif opaque puis stockage mémoire déclaré. Contrôles clavier et clics ; export JSON réellement téléchargé. Pas de GPU, iPhone ou carte géographique réelle.';file.write_text(json.dumps(report,ensure_ascii=False,indent=2));print('LIVRAISON',report['passed'],report['failed']);raise SystemExit(bool(report['failed']))
