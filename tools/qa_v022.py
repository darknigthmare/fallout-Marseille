#!/usr/bin/env python3
"""Exact HTML, software Chromium. Opaque-origin storage failure + explicit memory adapter.
Controller walking is real; individual actions use injected approaches for coverage.
No fake geographical fixture is presented as an imported real world.
"""
from pathlib import Path
from qa_support import chromium_path
import json,hashlib,math,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
html=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[];metrics=[]
def ck(ok,name,data=None):
 rows.append(dict(ok=bool(ok),name=name,detail=data));print(('OK' if ok else 'FAIL'),name,str(data)[:250] if data is not None else '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(6000);p.set_content(html,wait_until='load');p.wait_for_timeout(4000)
 ev=p.evaluate
 def call(n,*args):return ev('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
 def reset():call('v020Reset');call('v022ResetRuntime')
 def load(id):call('v020Load',id)
 def state():return call('getState')
 def dismiss():call('v020ModalDismiss')
 def near(id):return call('v020Approach',id)
 def action(k,value=None):near('v022:'+k);return call('v022Action',k,value)
 def prime():call('v021Scenario',{'ending':'manual','accepted':True});call('v022Task',{'accepted':True})
 try:
  call('setRenderPaused',True);call('v022Freeze',True);call('v018NoNetwork',True)
  ck(call('v022Info')['version']=='0.22.0','Version 0.22 chargée depuis le HTML final')
  p.locator('#btnV022').wait_for(state='visible',timeout=30000);ck(p.locator('#btnV022').is_visible(),'Scénario séparé accessible au menu')
  load('transit_depot');ck(call('save') is False,'Refus réel du stockage sur origine opaque signalé')
  ev("window.__store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k],clear:()=>{__store={}}}})")
  ck(call('save') is True,'Adaptateur de stockage mémoire explicitement employé pour les scénarios de réussite')
  ck(call('v022Info')['officialTiles']==0,'Aucune carte officielle simulée comme importée')
  for zone in ['transit_depot','traverse_archives','mooring_station']:
   reset();load(zone);call('v022Time',10);call('v022Tick',.05)
   s=call('v022Scene');c=call('v022Court');metrics.append(s)
   ck(len(s['rooms'])>=9 and c['end']>c['south']+24,zone+' : six espaces conservés + trois espaces de cour')
   ck(len(call('v022Residents'))==3,zone+' : trois résidents nommés')
   ck(s['draws']>1100 and s['colliders']>60,zone+' : géométrie et mobilier solide construits',s)
   paths=[]
   for i in call('v020Stats')['interactables']:
    route=call('v020Route',i['pos']);paths.append({'id':i['id'],'nodes':len(route or [])})
   ck(all(x['nodes'] for x in paths if not x['id'].startswith(('v029:exit:','v029:contact','v029:roomnote:'))),zone+' : objets historiques reliés ; alcôve verrouillée vérifiée en v029',paths)
   before=call('getWorld');walk=call('v021ActualWalk',[0,0,c['end']-7]);ck(walk['ok'] and call('getWorld')==before,zone+' : sortie dans la cour par le contrôleur réel sans chargement',walk)
   ret=call('v021ActualWalk',[0,0,18]);ck(ret['ok'],zone+' : retour physique depuis la cour vers l’intérieur',ret)
   call('v021MuteEnemies');call('v022ResetRuntime');call('v022Time',23);call('v022Tick',.1,800);ns=call('v022Residents')
   ck(all(math.dist(n['pos'],n['rest'])<1.0 for n in ns),zone+' : déplacement réel vers le repos nocturne',ns)
   ck(all(n['activity']=='repos' for n in ns),zone+' : animation de repos déclenchée après arrivée')
   ck(all(not call('v020Collides',[n['pos'][0],1.65,n['pos'][2]]) for n in ns),zone+' : aucun résident au repos dans un obstacle')
   ck(min(math.dist(a['pos'],b['pos']) for i,a in enumerate(ns) for b in ns[i+1:])>.75,zone+' : résidents non superposés')
   call('v022Time',10);call('v022Tick',.1,800);ns=call('v022Residents');ck(all(math.dist(n['pos'],n['work'])<1.0 for n in ns),zone+' : reprise du travail aux emplacements dédiés',ns)
   call('v022Time',13);call('v022Tick',.1,800);ns=call('v022Residents');ck(all(n['activity']=='pause' and math.dist(n['pos'],n['phase']['pos'])<.09 for n in ns),zone+' : pause de midi sur les sièges affectés',ns)
   call('v022Time',14);call('v022Tick',.1,800);ck(all(n['activity']=='travail' for n in call('v022Residents')),zone+' : retour de la pause de midi')
   call('v022Noise');call('v022Tick',.1,40);a=call('v022Residents');ck(all(n['activity']=='à l’abri' for n in a),zone+' : alerte fait quitter les postes')
   call('v022Open','habitants');frozen=call('v022Residents');tick=call('v022Tick',.1,80);ck(frozen==call('v022Residents'),zone+' : horaires et alerte suspendus dans le panneau');dismiss()
   call('v022Tick',.1,800);ck(all(n['activity']=='travail' for n in call('v022Residents')),zone+' : reprise après fin de l’alerte',call('v022Residents'))
   ck(call('v022DrawAudit')['finite'],zone+' : accessoires et poses sans coordonnée invalide')
   call('v021RenderAt',[0,1.65,c['end']-4],0,0,2);render=call('v021Renderer');ck(render['faces']>1500,zone+' : cour effectivement rendue',render)
  # Narrative preconditions and physically located actions.
  reset();load('transit_depot');call('v021MuteEnemies');near('v022:salome:talk');ck(call('v022Talk','v022:salome'),'Salomé se présente physiquement');p.locator('#dialogueChoices button').first.click();ck(not state()['v022']['task']['accepted'],'Suite bloquée tant que le canal six n’a pas de conclusion');dismiss()
  call('v021Scenario',{'ending':'manual','accepted':True});near('v022:salome:talk');call('v022Talk','v022:salome');p.locator('#dialogueChoices button').first.click();dismiss();ck(state()['v022']['task']['accepted'],'Acceptation par un vrai clic de dialogue')
  ck(not call('v022Action','beds'),'Réparation refusée loin des couchettes')
  call('v020Seed',{'cloth':0,'scrap':0});ck(not action('beds'),'Ressources insuffisantes refusées')
  ck(action('kit'),'Sangles collectées physiquement à l’étage');ck(not action('kit'),'Sangles non duplicables')
  ck(action('beds'),'Couchettes remises en état avec les sangles');dismiss();ck(state()['v022']['task']['beds'],'Réparation persistante validée')
  ck(not action('beds'),'Réparation non répétable')
  near('v022:tape');ck(call('v022Action','tape'),'Cassette présente dans le monde');ck(call('getMode')=='HOLOTAPE' and state()['lore']['holotapes']['v022_retour'],'Cassette inscrite dans les archives');call('v018TapeStep',1);ck(call('v018TapeState')['index']==1,'Sous-titres de la nouvelle cassette');call('v018TapeClose')
  load('traverse_archives');call('v021MuteEnemies');ck(action('consent'),'Choix de confidentialité proposé sur le pupitre');p.locator('#dialogueChoices button').first.click();dismiss();ck(state()['v022']['task']['consent']=='anonymous','Choix anonyme conservé après clic')
  ck(not action('consent','sealed'),'Choix de dossier non modifiable par appel répété')
  load('mooring_station');call('v021MuteEnemies');ck(action('relay'),'Diagnostic mécanique ouvert physiquement');ck(not action('relay',2),'Mauvais cran réinitialise l’essai');ck(not state()['v022']['task']['relay'],'Mauvais cran ne valide pas le poste')
  for k in [0,1,2]:ck(action('relay',k),'Séquence mécanique : cran '+str(k))
  dismiss();ck(state()['v022']['task']['relay'],'Radio remise en service après trois crans')
  near('v022:rayan:talk');ck(call('v022Decision'),'Deux destinations du retour proposées');caps=state()['player']['caps'];p.locator('#dialogueChoices button').first.click();ck(state()['v022']['task']['ending']=='home','Conclusion maison d’étape choisie par clic')
  ck(state()['player']['caps']-caps==120,'Récompense de 120 capsules, une seule fois')
  text=[]
  for k in range(3):text.append(p.locator('#dialogueLine').inner_text());p.locator('#dialogueChoices button').first.click()
  ck(len(set(text))==3 and all(len(t)>180 for t in text),'Trois scènes de conclusion, chacune distincte et rédigée')
  caps=state()['player']['caps'];near('v022:rayan:talk');call('v022Decision','road');dismiss();ck(state()['player']['caps']==caps and state()['v022']['task']['ending']=='home','Relecture sans changer la fin ni répéter le gain')
  # Alternate branch and ending reflect previous canal decision.
  reset();load('mooring_station');call('v021MuteEnemies');call('v021Scenario',{'ending':'silence'});call('v022Task',{'accepted':True,'beds':True,'consent':'sealed','relay':True});near('v022:rayan:talk');ck(call('v022Decision','road'),'Fin départs accompagnés active');call('v022Epilogue',2);ck('restent éteints' in p.locator('#dialogueLine').inner_text(),'Conclusion tient compte du canal six mis en silence');dismiss()
  # Resource path, cache once and no duplicate collection.
  reset();load('transit_depot');prime();call('v021MuteEnemies');call('v020Seed',{'cloth':0,'scrap':0});near('transit_depot:v22:cache');ck(call('v022Cache'),'Réserve locale donne les ressources de réparation');inv=state()['inventory'].copy();ck(not call('v022Cache') and state()['inventory']==inv,'Réserve non duplicable')
  ck(action('beds'),'Réparation sans trouver les sangles, avec ressources');dismiss();ck(state()['inventory']['cloth']==0 and state()['inventory']['scrap']==0,'Tissu et ferraille effectivement consommés')
  # Positions and injuries survive transitions and serialization.
  reset();load('transit_depot');call('v022Time',23);call('v022Tick',.1,800);pos={n['id']:n['pos'] for n in call('v022Residents')};ck(call('save'),'Écriture des horaires dans adaptateur mémoire')
  load('traverse_archives');load('transit_depot');ck(all(math.dist(pos[n['id']],n['pos'])<.1 for n in call('v022Residents')),'Positions des résidents conservées au retour dans la scène')
  e=call('v021EnemyInfo')[0];call('v021Hit',0,20);hp=call('v021EnemyInfo')[0]['health'];load('traverse_archives');load('transit_depot');ck(call('v021EnemyInfo')[0]['health']==hp and hp<e['health'],'Ennemi blessé ne retrouve pas tous ses PV au rechargement')
  snap=state();call('save');key=call('v018SaveKey');raw=ev('(k)=>localStorage.getItem(k)',key);ck(json.loads(raw)['v022']['encounters']==snap['v022']['encounters'],'Blessures présentes dans le JSON de sauvegarde')
  old=state();old.pop('v022');old['version']='0.21.0';old['custom_future']={'keep':True};mig=call('v018Migrate',old);ck(mig['custom_future']['keep'] and not mig['v022']['task']['accepted'],'Migration 0.21 conserve les champs inconnus et initialise le retour')
  # Mobile real UI interaction.
  dismiss();p.keyboard.press('k');ck(p.locator('#v020Title').inner_text()=='Une place au retour','K ouvre le suivi de retour');dismiss();p.keyboard.press('m');ck(p.locator('#v020Map').is_visible(),'Plan local accessible après extension')
  p.set_viewport_size({'width':390,'height':844})
  for panel in ['retour','habitants','plan']:
   call('v022Open',panel);box=p.locator('#v020Panel').bounding_box();ck(box['x']>=0 and box['x']+box['width']<=391 and ev('document.documentElement.scrollWidth<=innerWidth'),panel+' : panneau mobile sans débordement');ck(p.locator('#v020Close').is_visible(),panel+' : fermeture mobile visible');dismiss()
  ck(not errors,'Aucune exception JavaScript',errors)
 except Exception:
  ck(False,'Exception de la suite',traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  result={'version':'0.22.0','sha256':hashlib.sha256(html.encode()).hexdigest(),'scope':{'browser':'Chromium Linux, HTML exact via set_content ; HTTP local bloqué par politique navigateur','renderer':'SoftwareRenderer ; pas de GPU matériel certifié','storage':'refus natif origine opaque puis adaptateur mémoire explicitement installé','actions':'acceptation et fins par clic ; approches injectées ; marches par vrai contrôleur','geography':'cours fictives, zéro donnée cartographique officielle acquise'},'total':len(rows),'passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'errors':errors,'results':rows,'metrics':metrics};(O/'QA_V022.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('RESULT',result['passed'],result['failed'],flush=True);b.close()
raise SystemExit(bool(result['failed']))
