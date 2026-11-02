#!/usr/bin/env python3
"""Menu isolation, actual shot signal, serialization and scripted encounter state."""
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import hashlib,json,traceback
R=Path(__file__).resolve().parents[1];html=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[]
def ck(v,name,detail=None):
 rows.append(dict(ok=bool(v),name=name,detail=detail));print('OK' if v else 'FAIL',name,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html);p.locator('#btnV022').wait_for(state='visible',timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  p.evaluate("window.__EX={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__EX[k]??null,setItem:(k,v)=>__EX[k]=String(v),removeItem:k=>delete __EX[k]}})")
  keys=c('v018Keys');old=json.dumps(c('getState'));p.evaluate('(a)=>localStorage.setItem(a[0],a[1])',[keys['campaign'],old]);p.on('dialog',lambda d:d.accept());p.locator('#btnV022').click();p.wait_for_timeout(650)
  ck(c('getWorld')=='transit_depot' and c('getMode')=='PLAYING','Le bouton de découverte ouvre la cour et rend le contrôle')
  ck(c('getState')['player']['pos'][2]>24,'Le départ de découverte se situe réellement dans la nouvelle cour')
  ck(p.evaluate('(k)=>localStorage.getItem(k)',keys['campaign'])==old,'Campagne précédente inchangée après le clic de découverte')
  ck(c('v018SaveKey')==keys['sandbox'],'La découverte sauvegarde dans une clé séparée')
  s=c('getState');ck(s['v021']['ending']=='manual' and not s['v022']['task']['accepted'],'La découverte prépare le contexte sans accomplir la nouvelle quête')
  c('v021MuteEnemies');c('v022ResetRuntime');c('v022Time',10);c('v020GrantWeapon','pistol10');c('v020Equip','pistol10');c('v020Tick',1);c('v022Tick',.1,30);shots=c('v020Combat')['shots'];ammo=c('getState')['player']['ammoClip'];c('v020RandomFire',.5);c('v022Tick',.1,15)
  ck(c('v020Combat')['shots']==shots+1 and c('getState')['player']['ammoClip']==ammo-1,'Un vrai tir consomme une munition dans la cour',{'before':[shots,ammo],'after':c('v020Combat')})
  ck(any(e['detail']=='tir dans le relais' for e in c('v022Events')),'Le tir réel déclenche le signal d’alerte local')
  ck(all(n['activity']=='à l’abri' for n in c('v022Residents')),'Les neuf scripts partagés réagissent au tir : contrôle des trois résidents chargés')
  c('v022ResetRuntime');c('v022Task',{'accepted':True,'beds':True,'consent':'sealed','relay':True,'ending':'road','rewarded':True});c('save');raw=p.evaluate('(k)=>localStorage.getItem(k)',c('v018SaveKey'));c('v022Task',{'ending':None,'beds':False});c('v018ImportRaw',raw)
  ck(c('v022State')['task']['ending']=='road' and c('v022State')['task']['consent']=='sealed','Import réel du JSON rétablit les choix du retour (stockage mémoire)')
  c('v020Load','transit_depot');c('v021Scenario',{'accepted':True});c('v020Approach','transit_depot:power');c('v021Action','transit_depot','power');c('v020ModalDismiss');c('save');c('v020Load','traverse_archives');c('v020Load','transit_depot')
  ck(not any(e['alive'] and e['id']=='transit_depot:unit' for e in c('v021EnemyInfo')),'Une machine consignée ne redémarre pas avec la persistance des blessures',c('v021EnemyInfo'))
  c('v020Reset');c('v020Load','transit_depot');c('v021Hit',0,999);c('v020Load','traverse_archives');c('v020Load','transit_depot');en=c('v021EnemyInfo');ck(not any(e['alive'] and e['id']=='transit_depot:unit' for e in en),'Ennemi détruit non ressuscité au retour')
  bad=c('getState');bad['v022']['actors']={'bad':{'pos':['invalid',0,0]}};bad['v022']['encounters']={'bad':{'zone':'x','health':'broken'}};mig=c('v018Migrate',bad);ck('bad' not in mig['v022']['actors'] and 'bad' not in mig['v022']['encounters'],'Données de position et de santé invalides rejetées par la migration')
  ck(not errors,'Aucune exception JavaScript pendant les contrôles supplémentaires',errors)
 except Exception:ck(False,'Exception de la suite supplémentaire',traceback.format_exc())
 finally:
  result=dict(html_sha256=hashlib.sha256(html.encode()).hexdigest(),scope='HTML exact, rendu logiciel ; stockage mémoire explicite ; menu cliqué ; tir réel via fonction du jeu',total=len(rows),passed=sum(r['ok'] for r in rows),failed=sum(not r['ok'] for r in rows),errors=errors,results=rows);(R/'verification/QA_V022_EXTRA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('RESULT',result['passed'],result['failed'],flush=True);b.close()
raise SystemExit(bool(result['failed']))
