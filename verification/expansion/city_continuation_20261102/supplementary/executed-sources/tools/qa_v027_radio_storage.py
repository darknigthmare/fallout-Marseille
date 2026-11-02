#!/usr/bin/env python3
"""Embedded tapes, migration and file export. Controlled clocks and state;
opaque-origin memory storage only. Native-origin access attempted in separate report.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
import json,traceback,hashlib
R=Path(__file__).resolve().parents[1];O=R/'verification';H=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[]
def check(ok,title,d=None):rows.append(dict(ok=bool(ok),name=title,detail=d));print('OK' if ok else 'FAIL',title,str(d or '')[:200],flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':1000},has_touch=True);p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(8000);p.set_content(H,wait_until='load');p.locator('#btnV027').wait_for(timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def ui():return c('v027UI')
 def act(a,x=''):return c('v027Dispatch',a,x)
 def op(t,sub):return c('v027Open',t,sub)
 def dismiss():
  if c('getMode')=='PIP':c('closePip')
  c('v020ModalDismiss')
 def load(z):dismiss();c('v020Load',z);c('v021MuteEnemies');c('v022ResetRuntime')
 def clk(a,arg=None,scope='#pipboy'):
  p.locator(scope+' [data-p27="'+a+'"]'+('' if arg is None else '[data-arg="'+arg+'"]')).first.click()
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v027ManualTape',True);c('v020Reset');load('transit_depot');op('data','system')
  check(act('save') is False and 'refusée' in p.locator('#p27SaveState').inner_text(),'Refus natif en origine opaque signalé dans le Pip-Boy')
  p.evaluate("window.__STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__STORE[k]??null,setItem:(k,v)=>__STORE[k]=String(v),removeItem:k=>delete __STORE[k]}})")
  check(act('save') is True and 'écrite' in p.locator('#p27SaveState').inner_text(),'Écriture contrôlée annonce le succès uniquement après écriture')
  keys=c('v018Keys');check(keys['campaign']=='fallout_mistral_save_v030' and keys['sandbox']=='fallout_mistral_sandbox_v030','Clés campagne et exploration v027 distinctes')
  op('radio','tapes');check(ui()['rows']==[],'Aucune holobande non découverte dans le lecteur')
  check(not act('tape-start','v026_reserves'),'Lecture d’une bande non possédée refusée')
  op('radio','stations');before=s();clk('station','mistral');check('Les dossiers suspendus' in p.locator('#pipContent').inner_text(),'Station Mistral diffuse la transcription liée à l’état')
  check('PAS DE FLUX AUDIO' in p.locator('#pipContent').inner_text(),'Radio textuelle annoncée, pas de fausse promesse audio')
  check(not act('station','quais') and not act('station','reserves'),'Stations non débloquées ne révèlent pas leurs bulletins')
  check(s()['quest']==before['quest'] and s()['inventory']==before['inventory'],'Régler la radio ne modifie ni quête ni ressources')
  # Physical discovery through ordinary interaction, not a debug grant.
  dismiss();a=c('v020Approach','v026:notice');check(bool(a),'Bande du magasinier possède une interaction physique atteignable')
  c('v020Interact','v026:notice');check(s()['lore']['holotapes'].get('v026_reserves'),'Interaction dans la cour découvre effectivement la bande')
  c('v018TapeClose');dismiss();op('radio','tapes');check([r['id'] for r in ui()['rows']]==['v026_reserves'],'Bande trouvée répertoriée seule dans RADIO')
  count=s()['lore']['holotapePlays'].get('v026_reserves',0);clk('tape-start','v026_reserves','#p27ActionBar');check(ui()['tape']['playing'] and s()['lore']['holotapePlays']['v026_reserves']==count+1,'Lecture déclenchée explicitement une seule fois')
  duration=c('v018TapeDuration','Durée de test');c('v027TapeTick',1800);t=ui()['tape'];check(t['elapsed']>=1800,'Chronomètre fait avancer le segment lu')
  clk('tape-pause',scope='#p27ActionBar');old=ui()['tape'];c('v027TapeTick',5000);check(ui()['tape']==old,'Pause fige segment et temps écoulé')
  clk('tape-step','1','#p27ActionBar');check(ui()['tape']['index']==1 and ui()['tape']['elapsed']==0,'Suivant avance d’un segment et réinitialise sa progression')
  clk('tape-step','-1','#p27ActionBar');check(ui()['tape']['index']==0,'Précédent fonctionne depuis la barre du boîtier')
  c('v027TapeControl','speed','1.5');check(s()['v018']['tapeSpeed']==1.5,'Vitesse de lecture 1,5× enregistrée')
  check(not c('v027TapeControl','speed','999'),'Vitesse arbitraire refusée')
  p.locator('.p27-transcript summary').click();check(p.locator('.p27-transcript li').count()==5,'Transcription réelle des cinq segments affichée')
  c('v027TapeControl','restart');c('v027TapeTick',1900);before=ui()['tape'];c('closePip');check(ui()['tape']['playing'] is False,'Fermeture par défaut suspend la bande')
  check(s()['v018']['tapeBookmarks']['v026_reserves']['elapsed']==before['elapsed'],'Fermeture conserve un marque-page exact')
  op('radio','tapes');act('tape-start','v026_reserves');check(ui()['tape']['elapsed']==before['elapsed'],'Réouverture reprend au marque-page au lieu de repartir à zéro')
  op('data','system');clk('background');op('radio','tapes');c('closePip');c('v027TapeTick',500);check(not c('v027Subtitles')['hidden'] and '—' in c('v027Subtitles')['text'],'Sous-titres en jeu visibles lorsque l’option est activée')
  op('radio','tapes');check(c('v027Subtitles')['hidden'],'Ouvrir le boîtier masque immédiatement les sous-titres en exploration');c('closePip')
  before=ui()['tape'];c('v023TestDialog');c('v027TapeTick',6000);check(ui()['tape']['elapsed']==before['elapsed'] and c('v027Subtitles')['hidden'],'Dialogue suspend le chronomètre et masque la légende')
  dismiss();op('radio','tapes');c('v027TapeControl','restart');
  for i in range(15):c('v027TapeTick',20000)
  check(ui()['tape']['index']==4 and not ui()['tape']['playing'],'Fin de bande s’arrête sans déborder du dernier segment')
  clk('tape-pause',scope='#p27ActionBar');check(ui()['tape']['index']==0 and ui()['tape']['playing'],'Lecture après la fin redémarre proprement au premier segment')
  # Simulated browser hidden event clearly declared in test.
  p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
  check(not ui()['tape']['playing'],'Événement visibilitychange suspend la bande')
  p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
  c('v027TapeTick',500);check(not ui()['tape']['playing'],'Retour à la page n’impose pas une reprise automatique')
  c('v027TapeControl','restart');before=ui()['tape'];load('traverse_archives');check(ui()['tape'] is None and s()['v018']['tapeBookmarks'].get('v026_reserves') is not None,'Transition sauvegarde le repère puis invalide la lecture de la scène précédente')
  # A historical delayed mouse-lock request must not hijack a newly opened UI.
  load('aubagne');c('v026Trade','aubagne');c('v026CloseTrade');op('status','health');p.wait_for_timeout(250)
  check(p.evaluate('document.pointerLockElement===null'),'Fermeture du commerce puis Pip-Boy : aucun verrouillage différé de souris')
  p.locator('#pipTabs [data-tab="inventory"]').click();check(ui()['tab']=='inventory','Le curseur clique réellement sur INV après fermeture du commerce')
  dismiss();load('aubagne');c('v026Trade','aubagne');c('v026CloseTrade');load('transit_depot');c('v020Approach','v026:transit_depot|free');c('v026OpenContainer','transit_depot|free');p.wait_for_timeout(250)
  p.locator('[data-v26="select|radioTube"]').click();check(p.evaluate('document.pointerLockElement===null') and p.locator('[data-v26="select|radioTube"].active').count()==1,'La liste de fouille reste cliquable après un ancien retour différé du commerce',{'pointer':p.evaluate('document.pointerLockElement?.id'),'selected':p.locator('[data-v26="select|radioTube"].active').count()})
  dismiss()
  # Migration preserves older narrative progress and prevents poisoned prefs.
  before=s();raw=json.loads(json.dumps(before));raw.pop('v027',None);new=c('v018Migrate',raw)
  # Existing v026 migration fills missing false inspection flags; this is not quest progress.
  for z in ['transit_depot','traverse_archives','mooring_station']:raw['v026']['quest']['inspected'].setdefault(z,False)
  check(new['v026']==raw['v026'] and new['v023']==raw['v023'],'Migration v026 conserve réserves, aptitudes et conséquences', {'before':{k:raw[k] for k in ['v026','v023']},'after':{k:new[k] for k in ['v026','v023']}} if new['v026']!=raw['v026'] or new['v023']!=raw['v023'] else None)
  check(new['v027']['theme']=='green' and new['v027']['tagged']==[],'Migration ajoute préférences saines, pas de découverte inventée')
  raw['v027']={'theme':'poison','tagged':['circuitry','circuitry','caps','xxx'],'read':{'__proto__':True,'valid':True},'pin':{'zone':'x','pos':[None,0,0]},'documents':{'__proto__':{'text':'x'},'qa-old':{'title':'Texte réel','text':'Retenu'}}}
  new=c('v018Migrate',raw);check(new['v027']['theme']=='green' and new['v027']['tagged']==['circuitry'] and new['v027']['pin'] is None,'Import de préférences invalide nettoyé et dédupliqué')
  check('__proto__' not in new['v027']['documents'] and new['v027']['documents']['qa-old']['text']=='Retenu','Clés hostiles rejetées, texte valide conservé')
  # Successful file export, import real saved JSON through existing validator.
  op('data','system');clk('theme','white');act('tag','circuitry');c('v027ReadNote','qa-export','Mémo de transfert','Conserver ce texte après import.');dismiss();op('data','system')
  with p.expect_download() as dl:clk('export')
  download=dl.value;path=O/'QA_V027_EXPORT.json';download.save_as(path);exported=json.loads(path.read_text());check(exported['v027']['theme']=='white' and 'circuitry' in exported['v027']['tagged'],'Export JSON contient affichage et composants suivis')
  check(exported['v027']['documents']['qa-export']['text']=='Conserver ce texte après import.','Export inclut le texte des notes, pas seulement leurs titres')
  clk('theme','amber');c('v018ImportRaw',path.read_text());check(c('v027State')['theme']=='white','Import validé restaure les préférences archivées')
  raw=p.evaluate('JSON.stringify(__STORE)');try_err=None
  try:c('v018ImportRaw','{bad json}')
  except Exception as e:try_err=str(e)
  check(try_err is not None and p.evaluate('JSON.stringify(__STORE)')==raw,'Import JSON invalide ne remplace aucune sauvegarde')
  # New exploration confirmation decline and accept with protected campaign.
  dismiss();camp=p.evaluate('(k)=>localStorage.getItem(k)',keys['campaign']);p.once('dialog',lambda d:d.dismiss());check(c('v027Start') is False,'Refuser le nouveau départ ne crée pas une exploration')
  p.once('dialog',lambda d:d.accept());check(c('v027Start') is True,'Accepter démarre une vraie exploration distincte avec Pip-Boy')
  check(p.evaluate('(k)=>localStorage.getItem(k)',keys['campaign'])==camp,'Campagne existante inchangée après démarrage séparé')
  check(p.evaluate('(k)=>!!localStorage.getItem(k)',keys['sandbox']),'Exploration enregistrée dans sa propre clé')
  check(set(s()['equipment']['ownedWeapons'])=={'pistol10','pipeCarbine'},'Nouveau départ contient deux armes choisies, pas les 304 modèles')
  # Legacy resume from 026 is read, not overwritten.
  dismiss();raw=s();raw['v027']['theme']='amber';p.evaluate('([k,v])=>localStorage.setItem(k,v)',['fallout_mistral_sandbox_v026',json.dumps(raw)]);p.evaluate('(k)=>localStorage.removeItem(k)',keys['sandbox']);old=p.evaluate('localStorage.getItem("fallout_mistral_sandbox_v026")');check(c('v027ResumeSandbox'),'Ancienne exploration v026 reprise par le nouveau bouton')
  check(c('v027State')['theme']=='amber' and p.evaluate('localStorage.getItem("fallout_mistral_sandbox_v026")')==old,'Source v026 inchangée après migration en v027')
 except Exception:
  check(False,'Exception de la suite',traceback.format_exc());p.screenshot(path=str(O/'QA_V027_RADIO_FAILURE.png'))
 check(not errors,'Aucune exception JavaScript pendant la suite',errors);b.close()
report={'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'scope':'Chronométrage contrôlé et stockage mémoire déclaré ; export réel téléchargé via Chromium ; pas de voix enregistrée.','passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'checks':rows,'errors':errors};(O/'QA_V027_RADIO_STORAGE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('TOTAL',report['passed'],report['failed']);raise SystemExit(report['failed']>0)
