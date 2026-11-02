#!/usr/bin/env python3
"""Verify the actual ZIP bytes, rebuild source, then click the distributed game.
Native opaque storage refusal is checked before installing a declared memory store.
"""
from pathlib import Path
import hashlib,json,zipfile,subprocess,sys,tempfile
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];P=R.parent;Hname='JOUER_FALLOUT_MISTRAL_v0.28.html'
rows=[];errors=[];stats={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ck(ok,label,detail=None):
 rows.append({'ok':bool(ok),'name':label,'detail':detail});print('OK' if ok else 'FAIL',label,flush=True)
 if not ok:raise AssertionError(label)
with tempfile.TemporaryDirectory(prefix='mistral-v027-') as td:
 tmp=Path(td)
 for kind,suffix in [('game','JEU_SEUL'),('project','PROJET_COMPLET')]:
  zp=P/f'FALLOUT_MISTRAL_v0.27_{suffix}.zip'
  with zipfile.ZipFile(zp) as z:ck(z.testzip() is None,kind+' : intégrité ZIP');z.extractall(tmp/kind)
  root=(tmp/kind) if kind=='game' else tmp/kind/R.name
  man=json.loads((root/'MANIFEST_SHA256.json').read_text());bad=[rel for rel,d in man['files'].items() if not (root/rel).is_file() or (root/rel).stat().st_size!=d['bytes'] or sha(root/rel)!=d['sha256']]
  ck(not bad,kind+' : manifeste et tailles vérifiés',{'files':len(man['files']),'bad':bad});stats[kind+'_manifest_files']=len(man['files'])
  ck((root/Hname).read_bytes()==(R/Hname).read_bytes(),kind+' : HTML extrait identique au jeu testé')
 proj=tmp/'project'/R.name
 base=json.loads((proj/'data/BASE_V026.json').read_text());bad=[r['path'] for r in base['preserved'] if sha(proj/'history/v0.26_source'/r['path'])!=r['sha256']]
 ck(not bad,'Historique v0.26 conservé octet pour octet',{'files':len(base['preserved']),'bad':bad});stats['preserved_source_files']=len(base['preserved'])
 subprocess.run([sys.executable,'tools/build_single.py'],cwd=proj,check=True,capture_output=True);ck((proj/Hname).read_bytes()==(R/Hname).read_bytes(),'Reconstruction depuis le ZIP source identique au jeu distribué')
 sub=subprocess.run(['node','--check','src/game.js'],cwd=proj,capture_output=True,text=True);ck(sub.returncode==0,'Syntaxe JavaScript reconstruite valide',sub.stderr)
 binary=(tmp/'game'/Hname).read_text();ck(hashlib.sha256(binary.encode()).hexdigest()==json.loads((R/'verification/QA_GLOBAL_V027.json').read_text())['html_sha256'],'Le HTML lancé est celui des 963 contrôles')
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(12000);p.set_content(binary,wait_until='load');p.locator('#btnV027').wait_for(timeout=30000)
  def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v027ManualTape',True)
  ck('v0.27' in p.title(),'Titre réel du jeu distribué en v0.27')
  p.once('dialog',lambda d:d.dismiss());p.locator('#btnV027').click();ck(c('getMode')=='MENU','Refus au lancement conserve le menu')
  native=p.evaluate("(()=>{try{localStorage.setItem('test27','x');localStorage.removeItem('test27');return true;}catch{return false;}})()");ck(not native,'Stockage opaque natif refusé, aucun succès natif inventé')
  p.evaluate("window.__DELIVERY_STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__DELIVERY_STORE[k]??null,setItem:(k,v)=>__DELIVERY_STORE[k]=String(v),removeItem:k=>delete __DELIVERY_STORE[k]}})")
  p.evaluate("localStorage.setItem('fallout_mistral_save_v028','CAMPAGNE_TEMOIN')")
  p.once('dialog',lambda d:d.accept());p.locator('#btnV027').click();ck(c('getMode')=='PIP' and c('getState')['player']['zone']=='transit_depot','Lancement confirmé au dépôt et ouverture du boîtier')
  ck(p.evaluate("localStorage.getItem('fallout_mistral_save_v028')")=='CAMPAGNE_TEMOIN','Campagne témoin conservée pendant le départ séparé')
  ck(p.locator('#pipTabs button').count()==5,'Cinq boutons principaux dans la distribution')
  p.locator('#pipTabs [data-tab="inventory"]').click();ck(c('v027UI')['tab']=='inventory','Clic réel vers INV')
  p.locator('#p27Search').fill('carabine');ck(p.locator('#pipContent .p27-row').count()==1,'Recherche au clavier dans les possessions réelles')
  p.locator('#pipContent .p27-row').first.click();p.locator('#p27ActionBar [data-p27="equip"]').click();ck(c('getState')['player']['weaponId']=='pipeCarbine','Équipement de la carabine depuis le boîtier')
  p.locator('[data-p27="settings"]').click();p.locator('[data-p27="theme"][data-arg="amber"]').click();ck(c('v027State')['theme']=='amber','Palette modifiée par le bouton de réglage')
  p.locator('[data-p27="save"]').click();ck(p.evaluate("!!localStorage.getItem('fallout_mistral_sandbox_v028')"),'Écriture réussie vérifiée dans le stockage mémoire déclaré')
  p.keyboard.press('Tab');ck(c('getMode')=='PLAYING','TAB restitue le personnage')
  p.keyboard.press('i');ck(c('getMode')=='PIP' and c('v027UI')['tab']=='inventory','I ouvre directement le nouvel inventaire')
  p.locator('#pipTabs [data-tab="map"]').click();ck(p.locator('#pipContent canvas').count()==1,'Plan de la scène intégré et rendu')
  ck(not errors,'Aucune exception JavaScript du jeu réextrait',errors);b.close()
report={'version':'0.28.0','html_sha256':sha(R/Hname),'passed':sum(r['ok']for r in rows),'failed':sum(not r['ok']for r in rows),'checks':rows,'stats':stats,'scope':'ZIPs réextraits et manifestes relus ; source reconstruite ; clics réels dans le HTML extrait avec Chromium logiciel. Refus natif opaque testé puis adaptateur mémoire explicite. Aucun GPU ni iPhone matériel.','errors':errors}
(P/'FALLOUT_MISTRAL_v0.27_CONTROLES_LIVRAISON.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
files=[R/Hname,P/'FALLOUT_MISTRAL_v0.27_JEU_SEUL.zip',P/'FALLOUT_MISTRAL_v0.27_PROJET_COMPLET.zip',R/'RAPPORT_VISUEL_V0.27.png',R/'RAPPORT_VISUEL_V0.27.html',P/'FALLOUT_MISTRAL_v0.27_CONTROLES_LIVRAISON.json']
(P/'FALLOUT_MISTRAL_v0.27_CHECKSUMS.txt').write_text('\n'.join(f'{sha(f)}  {f.name}  ({f.stat().st_size} octets)' for f in files)+'\n')
print('DELIVERY',report['passed'],report['failed'])
