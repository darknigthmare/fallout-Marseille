#!/usr/bin/env python3
"""Re-extract, verify manifests, rebuild and interact with the distributed HTML.
Uses actual clicks/taps and an explicitly declared storage adapter after failure."""
from pathlib import Path
import zipfile,hashlib,json,subprocess,shutil,sys
import qa029_support as qs
R=Path(__file__).resolve().parents[1];OUT=R.parent;TEMP=OUT/'_VERIFY_V029';shutil.rmtree(TEMP,ignore_errors=True);TEMP.mkdir()
checks=[]
def ck(ok,name,detail=None):checks.append({'ok':bool(ok),'name':name,'detail':detail});print(('OK 'if ok else 'FAIL ')+name,flush=True)
for kind in ['JEU_SEUL','PROJET_COMPLET']:
 path=OUT/('FALLOUT_MISTRAL_v0.29_'+kind+'.zip')
 with zipfile.ZipFile(path)as z:
  ck(z.testzip()is None,'CRC ZIP '+kind);z.extractall(TEMP/kind)
  if kind=='JEU_SEUL':qs.H=z.read('JOUER_FALLOUT_MISTRAL_v0.29.html').decode()
 folder=TEMP/kind/(R.name if kind=='PROJET_COMPLET'else'');man=json.loads((folder/'MANIFEST_SHA256.json').read_text())['files'];bad=[n for n,d in man.items()if not (folder/n).is_file()or hashlib.sha256((folder/n).read_bytes()).hexdigest()!=d['sha256']]
 ck(not bad,'Empreintes du manifeste '+kind,{'files':len(man),'bad':bad});ck((folder/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes()==(R/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes(),'HTML exact dans '+kind)
project=TEMP/'PROJET_COMPLET'/R.name;before=(project/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes();subprocess.run([sys.executable,str(project/'tools/build_single.py')],cwd=project,check=True);ck((project/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes()==before,'Reconstruction des sources réextraites identique au HTML testé');ck(subprocess.run(['node','--check',str(project/'src/game.js')],capture_output=True).returncode==0,'Syntaxe JavaScript reconstruite')
G=qs.Game('RELEASE_NOT_ANOTHER_SUITE');c=G.c;p=G.p
try:
 ck(p.locator('#btnV029').is_visible(),'Nouvel accès visible dans le fichier distribué');ck(c('v029Info')['version']=='0.29.0','Version du runtime correspond au ZIP')
 native=p.evaluate("(()=>{try{localStorage.setItem('__probe029','x');localStorage.removeItem('__probe029');return false}catch(e){return e.name==='SecurityError'}})()")
 ck(native,'Stockage natif opaque refuse réellement l’écriture');G.memory();old=json.dumps(G.s());p.evaluate('(s)=>localStorage.setItem("fallout_mistral_save_v028",s)',old)
 p.once('dialog',lambda d:d.dismiss());p.locator('#btnV029').click();ck(p.evaluate('localStorage.getItem("fallout_mistral_save_v028")')==old,'Refus de confirmation conserve la campagne')
 p.once('dialog',lambda d:d.accept());p.locator('#btnV029').click();ck(G.s()['player']['zone']=='transit_depot'and c('v018SaveKey')=='fallout_mistral_sandbox_v029','Départ réel dans une exploration distincte')
 ck(p.evaluate('localStorage.getItem("fallout_mistral_save_v028")')==old,'Campagne v028 intacte après création de l’exploration')
 ck(G.s()['equipment']['ownedWeapons']==['pistol10','pipeCarbine'],'Arsenal de départ limité, pas 304 armes gratuites')
 G.near('v029:terminal:depot');c('v020Tick',.02,True);p.locator('#gameCanvas').focus();p.keyboard.press('e');ck(p.locator('#terminal29').evaluate('(e)=>e.open'),'Touche E ouvre le contrôleur réellement placé')
 p.locator('[data-t29="hack"]').click();d=c('v029Deck','depot');wrong=next(i for i in range(12)if i!=d['answer']);p.locator('[data-t29="word"][data-arg="'+str(wrong)+'"]').click();ck(G.st()['terminals']['depot']['attempts']==3,'Candidat cliqué dans le jeu distribué consomme un essai')
 p.keyboard.press('Escape');c('v020Tick',.02,True);p.locator('#gameCanvas').focus();p.keyboard.press('e');ck(G.st()['terminals']['depot']['attempts']==3,'Refermer au clavier ne rend pas les essais');p.locator('[data-t29="hack"]').click();p.locator('[data-t29="word"][data-arg="'+str(d['answer'])+'"]').click();ck(G.st()['terminals']['depot']['unlocked'],'Authentification fonctionnelle dans l’archive finale')
 p.locator('[data-t29="command"][data-arg="door"]').click();ck(not G.st()['terminals']['depot']['door'],'Commande préparée mais pas encore appliquée');p.locator('[data-t29="confirm"]').click();ck(G.st()['terminals']['depot']['door'],'Confirmation appliquée dans le fichier distribué');p.keyboard.press('Escape');walk=c('v021ActualWalk',[-15,0,44.35]);ck(walk['ok'],'Traversée avec contrôleur réel après ouverture',walk)
 c('v027Open','data','system')
 with p.expect_download()as download:p.locator('[data-p27="export"]').click()
 target=OUT/'V029_EXPORT_QA.json';download.value.save_as(target);export=json.loads(target.read_text());ck(export['v029']['terminals']['depot']['door']and export['v029']['terminals']['depot']['unlocked'],'Export JSON réellement téléchargé contient portes et authentification')
 ck(export['v029']['terminals']['depot']['attempts']==3,'Export conserve les essais consommés')
 ck(not G.errors,'Aucune exception navigateur pendant les interactions de livraison',G.errors)
except Exception:
 import traceback;ck(False,'Exception dans la vérification de distribution',traceback.format_exc())
G.b.close();G.pw.stop()
T=qs.Game('RELEASE_TOUCH',{'width':390,'height':844},True)
try:
 T.memory();T.reset();T.open('depot');T.p.locator('[data-t29="hack"]').tap();d=T.c('v029Deck','depot');T.p.locator('[data-t29="word"][data-arg="'+str(d['answer'])+'"]').tap();ck(T.st()['terminals']['depot']['unlocked'],'Authentification au tap tactile sur le HTML relu dans le ZIP')
 ck(T.p.locator('#terminal29').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),'Largeur de terminal sans débordement à 390 px');T.p.locator('[data-t29="close"]').tap();ck(T.c('getMode')=='PLAYING','Fermeture tactile rend le jeu au personnage');ck(not T.errors,'Aucune exception dans le contrôle tactile de livraison',T.errors)
except Exception:
 import traceback;ck(False,'Exception tactile de distribution',traceback.format_exc())
T.b.close();T.pw.stop()
files=[R/'JOUER_FALLOUT_MISTRAL_v0.29.html',R/'RAPPORT_VISUEL_V0.29.png',OUT/'FALLOUT_MISTRAL_v0.29_JEU_SEUL.zip',OUT/'FALLOUT_MISTRAL_v0.29_PROJET_COMPLET.zip']
res={'version':'0.29.0','passed':sum(x['ok']for x in checks),'failed':sum(not x['ok']for x in checks),'checks':checks,'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files},'scope':'Archives réextraites, manifests, reconstruction, HTML relu dans le ZIP, vrais clics/clavier/taps. Chromium logiciel via set_content ; stockage mémoire déclaré après refus natif opaque.'};(OUT/'FALLOUT_MISTRAL_v0.29_CONTROLES_LIVRAISON.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print('DELIVERY',res['passed'],res['failed']);raise SystemExit(bool(res['failed']))
