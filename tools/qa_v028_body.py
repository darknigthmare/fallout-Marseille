#!/usr/bin/env python3
"""Player-body, treatment and needs checks. Exact HTML; deliberately controlled
state/arena. Storage failure first, then declared in-memory adapter. No GPU claim."""
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import hashlib,json,traceback,math
R=Path(__file__).resolve().parents[1];O=R/'verification';H=(R/'JOUER_FALLOUT_MISTRAL_v0.35.html').read_text();checks=[];errors=[]
def check(ok,name,detail=None):
 checks.append(dict(ok=bool(ok),name=name,detail=detail));print(('OK 'if ok else 'FAIL ')+name,flush=True)
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.set_default_timeout(7000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV028').wait_for(state='attached',timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def st():return c('v028State')
 def op(sub='health'):c('v027Open','status',sub)
 def dismiss():
  if p.locator('#pipboy').is_visible():c('closePip')
  c('v020ModalDismiss')
 def act(a,arg=''):return c('v027Dispatch','p28:'+a,arg)
 def click(a,arg=None):
  sel='[data-p27="p28:'+a+'"]'+(''if arg is None else '[data-arg="'+str(arg)+'"]');p.locator(sel).filter(visible=True).first.click()
 def load(z='relay_cold'):
  dismiss();c('v020Load',z);c('v022ResetRuntime');c('v021MuteEnemies');c('v022Time',10)
 def reset():
  dismiss();c('v020Reset');load();c('v028Settings',{'survivalNeeds':False});c('v026Carry',False)
 def near(id):return c('v020Approach',id)
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  check(c('v028Info')=={'version':'0.35.0','limbs':6,'boards':6,'recipes':20,'officialTiles':0},'Six régions, six circuits, vingt recettes, aucune carte officielle')
  check(p.title().endswith('Relève complète'),'Titre de la nouvelle build')
  c('v020Load','relay_cold');check(c('save') is False,'Refus du stockage natif opaque vérifié avant adaptateur')
  p.evaluate("window.__STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__STORE[k]??null,setItem:(k,v)=>__STORE[k]=String(v),removeItem:k=>delete __STORE[k]}})")
  check(c('save') is True,'Écriture par adaptateur mémoire déclarée')
  oldsettings={'survivalNeeds':True,'reduceMotion':True,'volume':0.17};p.evaluate('(v)=>localStorage.setItem("fallout_mistral_settings_v027",JSON.stringify(v))',oldsettings);loaded=c('v028LoadSettings');check(loaded['survivalNeeds'] and loaded['reduceMotion'] and loaded['volume']==0.17,'Options v027 récupérées avant les valeurs anciennes v017')
  p.evaluate('localStorage.setItem("fallout_mistral_settings_v028",JSON.stringify({volume:0.3}))');check(c('v028LoadSettings')['volume']==0.3,'Préférence v028 prend priorité sans écraser la v027');p.evaluate('localStorage.removeItem("fallout_mistral_settings_v028")');check(p.evaluate('JSON.parse(localStorage.getItem("fallout_mistral_settings_v027")).volume')==0.17,'Lecture des options ne modifie pas la source précédente')
  reset();raw=s();raw.pop('v028',None);raw['legacy_unknown']={'preserve':1};mig=c('v018Migrate',raw)
  check(all(h==100 for h in mig['v028']['limbs'].values()),'Migration ancienne partie : aucune blessure imposée')
  check(not mig['v028']['lamp'] and not mig['v028']['game']['unlocked'],'Migration : aucune bande ou lampe active inventée')
  baseline=c('v018Migrate',raw);check(mig['inventory']==raw['inventory'] and mig['v023']==raw['v023'] and mig['v026']['quest'].get('ending')==raw['v026']['quest'].get('ending') and not mig['inventory'].get('fieldSplint',0) and not mig['inventory'].get('traumaKit',0),'Migration ne donne pas de soins et conserve les issues existantes')
  check(mig['legacy_unknown']=={'preserve':1},'Champs anciens inconnus conservés')
  raw['v028']={'limbs':{'head':-4,'torso':400,'leftArm':None,'rightArm':'bad','inconnu':0},'lamp':'yes','hits':-8,'history':[{'text':'x'*400}]*70,'quest':{'ending':'inconnu'},'game':{'unlocked':True,'levels':{'0':{'turns':[9,-1,None]*20,'moves':-8},'99':{'turns':[0]*25}}}}
  mig=c('v018Migrate',raw)
  check(mig['v028']['limbs']['head']==0 and mig['v028']['limbs']['torso']==100 and mig['v028']['limbs']['leftArm']==100,'Valeurs extrêmes bornées ; null ne crée pas une blessure')
  check(set(mig['v028']['limbs'])==set(st()['limbs']) and len(mig['v028']['history'])==32,'Six clés seulement et historique borné')
  check(len(mig['v028']['history'][0]['text'])==240 and mig['v028']['quest']['ending'] is None,'Texte et issue inconnue nettoyés')
  check(len(mig['v028']['game']['levels']['0']['turns'])==25 and '99'not in mig['v028']['game']['levels'],'Grille importée bornée, niveau inexistant rejeté')
  # Actual damage goes through existing armour, then trauma on one body region.
  c('v020Fixture',False);before=s();c('v028Hurt',20,'leftLeg');after=s();loss=before['player']['hp']-after['player']['hp']
  check(loss>0 and abs(after['v028']['limbs']['leftLeg']-(100-loss*1.12))<1e-8,'Lésion calculée après les dégâts réels de protection',{'loss':loss,'limb':after['v028']['limbs']['leftLeg']})
  check(all(v==100 for k,v in after['v028']['limbs'].items() if k!='leftLeg'),'Impact sur jambe gauche : cinq autres régions intactes')
  before=st()['limbs'];c('v028NativeDamage',6,'Radiation de test');check(st()['limbs']==before,'Radiation : pas de traumatisme répétitif')
  before=st()['limbs'];c('v028NativeDamage',.5,'Petite brûlure');check(st()['limbs']==before,'Petit effet continu : aucune nouvelle région cassée')
  op();hp=s()['player']['hp'];before=st()['limbs'];c('v028Hurt',20,'head');check(s()['player']['hp']==hp and st()['limbs']==before,'Interface ouverte : dégâts et traumatismes suspendus')
  check(c('v028Trauma',-8,'head') is False and c('v028Trauma',20,'unknown') is False,'Lésion négative et membre inconnu refusés')
  # Real movement / reload / damage / chance, not just display values.
  reset();c('v020Fixture',False);base=c('v028MoveTest',1,0);c('v020SetPlayer',{'pos':[0,1.65,8]});c('v028Set',{'limbs':{'leftLeg':0,'rightLeg':0}});slow=c('v028MoveTest',1,0)
  check(abs(base-1)<1e-6 and abs(slow-.58)<1e-6,'Deux jambes atteintes réduisent le déplacement réel à 58 %')
  check(c('v028Jump')['jumpVelocity']==0,'Deux jambes sévères empêchent effectivement le saut')
  c('v028Set',{'limbs':{'leftLeg':100}});check(c('v028Jump')['jumpVelocity']>0,'Une jambe soignée autorise de nouveau le saut')
  reset();c('v020Fixture',False);c('v020GrantWeapon','pistol10');c('v020Equip','pistol10');c('v020Tick',1);c('v020Seed',{'ammo10':50});c('v020SetPlayer',{'ammoClip':0});normal=c('v028Reload');c('v020Load','relay_cold');c('v021MuteEnemies');c('v028Set',{'limbs':{'leftArm':0,'rightArm':0}});c('v020SetPlayer',{'ammoClip':0});injured=c('v028Reload')
  check(normal['started'] and injured['started'] and abs(injured['time']/normal['time']-1.65)<1e-6,'Bras atteints : minuteur de rechargement réellement multiplié par 1,65',{'base':normal,'injured':injured})
  reset();c('v020Fixture',False);damage=c('v020Damage','machete');ball=c('v020Damage','pistol10');c('v028Set',{'limbs':{'leftArm':0,'rightArm':0}})
  check(abs(c('v020Damage','machete')-damage*.72)<1e-6,'Bras atteints : dégâts de mêlée réduits à 72 %')
  check(c('v020Damage','pistol10')==ball,'Lésion des bras ne réduit pas arbitrairement les dégâts de balle')
  chance=c('v028CombatStats')['chance'];c('v028Set',{'limbs':{'head':0}});check(c('v028CombatStats')['chance']==max(5,chance-14),'Tête atteinte : précision V.A.T.S. réduite de quatorze points')
  c('v020AddWall');check(c('v028CombatStats')['chance']==0,'Pénalité de tête ne transforme pas un obstacle en chance positive')
  reset();c('v020Fixture',False);c('v020SetPlayer',{'ap':10});c('v020Tick',.5,True);normal=s()['player']['ap']-10;c('v020SetPlayer',{'ap':10});c('v028Set',{'limbs':{'torso':0}});c('v020Tick',.5,True);low=s()['player']['ap']-10
  check(normal>0 and abs(low/normal-.45)<1e-6,'Torse atteint : récupération naturelle des PA à 45 %',{'normal':normal,'hurt':low})
  # Targeted consumption and regional, not total-health effects.
  reset();near('v028:medic');c('v020Seed',{'stimpak':4,'fieldSplint':2,'traumaKit':2,'caps':500});c('v020SetPlayer',{'hp':45,'rad':24});c('v028Set',{'limbs':{'head':10,'leftArm':30,'leftLeg':0,'torso':40}});op()
  check(p.locator('.p28-limbs button').count()==6,'Six régions sélectionnables par boutons natifs')
  p.locator('[data-p27="p28:limb"][data-arg="leftLeg"]').last.click();check('Jambe gauche' in p.locator('.p28-health-detail h2').inner_text(),'Sélection réelle de jambe dans le Pip-Boy')
  before=s();click('treat','leftLeg|stimpak');after=s()
  check(after['v028']['limbs']['leftLeg']==35 and after['inventory']['stimpak']==before['inventory']['stimpak']-1,'Stimpak ciblé : +35 sur une région, un seul objet')
  check(after['player']['hp']==45 and after['player']['rad']==24 and after['status']==before['status'],'Soin ciblé ne restaure ni PV ni radiations ni états')
  click('treat','leftLeg|fieldSplint');check(st()['limbs']['leftLeg']==100,'Attelle restaure la jambe à 100')
  before=s()['inventory'];check(c('v028Treat','leftLeg','fieldSplint') is False and s()['inventory']==before,'Attelle non gaspillée sur une jambe intacte')
  check(c('v028Treat','head','fieldSplint') is False and s()['inventory']==before,'Attelle pour la tête refusée sans débit')
  check(c('v028Treat','head','traumaKit') is True and st()['limbs']['head']==100,'Trousse restaure la tête sans toucher les autres régions')
  check(st()['limbs']['torso']==40 and st()['limbs']['leftArm']==30,'Traitement régional ne guérit pas le corps entier')
  c('v020Seed',{'traumaKit':0});before=s()['inventory'];check(c('v028Treat','torso','traumaKit') is False and s()['inventory']==before,'Trousse manquante : aucun prélèvement partiel')
  # Danger guard: a deliberately controlled alive/alerted enemy.
  dismiss();c('v020Fixture',False);c('v020EnemyPatch',{'damage':10,'alerted':True});c('v028Set',{'limbs':{'leftArm':10}});c('v020Seed',{'fieldSplint':1,'traumaKit':1,'stimpak':2});op()
  check(not c('v028Treat','leftArm','fieldSplint') and not c('v028Treat','leftArm','traumaKit'),'En menace visible, attelle et trousse sont refusées')
  check(c('v028Treat','leftArm','stimpak') and st()['limbs']['leftArm']==45,'Stimpak ciblé reste utilisable pendant une menace')
  # Doctor quote: physical proximity, no implicit treatment and no stale debit.
  reset();c('v020Seed',{'caps':1000});c('v028Set',{'limbs':{'head':20,'torso':40}});c('v020SetPlayer',{'pos':[10,1.65,-10]});op();before=s()['player']['caps'];check(c('v028Doctor') is False,'Médecin indisponible à distance malgré interface')
  near('v028:medic');cost=c('v028MedicalCost');check(c('v028Doctor') and s()['player']['caps']==before,'Devis local ne prélève pas les capsules')
  c('v028Set',{'limbs':{'leftArm':25}});check(c('v028Doctor',True) is False and s()['player']['caps']==before,'Nouveau dommage invalide l’ancien devis')
  c('v028Doctor');p.keyboard.press('Tab');op();check(c('v028Doctor',True) is False,'Ranger puis rouvrir le Pip-Boy invalide le devis')
  c('v028Doctor');price=c('v028MedicalCost');c('v020SetPlayer',{'hp':43,'rad':31});before=s();click('doctor-confirm');after=s()
  check(all(n==100 for n in st()['limbs'].values()) and after['player']['caps']==before['player']['caps']-price,'Validation du devis : six régions et montant exact')
  check(after['player']['hp']==43 and after['player']['rad']==31,'Médecin traumatismes ne traite ni PV ni radiations')
  before=s()['player']['caps'];check(not c('v028Doctor') and s()['player']['caps']==before,'Personnage intact : consultation gratuite, pas de facture')
  c('v028Set',{'limbs':{'head':0}});c('v020Seed',{'caps':1});c('v028Doctor');before=s();check(c('v028Doctor',True) is False and s()['player']['caps']==1 and st()['limbs']['head']==0,'Devis non payable : aucun paiement partiel ni soin')
  c('v020Seed',{'caps':500});c('v028Doctor');load('relay_vent');op();check(c('v028Doctor',True) is False,'Transition annule le devis et interdit un soin à distance')
  # Craft original two new items using the real workbench.
  reset();load('relay_vent');near('relay_vent:station');c('v020Seed',{'cloth':20,'scrap':10,'chemicals':10,'water':5});xp=s()['player']['xp']
  for id in ['fieldSplint','traumaKit']:
   before=s();check(c('v020Craft',id),'Fabrication physique : '+id);check(s()['inventory'].get(id,0)==before['inventory'].get(id,0)+1,'Un objet produit : '+id)
  check(s()['player']['xp']==xp,'Fabrication des soins ne génère pas d’XP')
  c('v020Seed',{'chemicals':0});before=s()['inventory'];check(not c('v020Craft','traumaKit') and before==s()['inventory'],'Recette insuffisante ne prélève aucune ressource')
  # Loaded cartridges mass and optional survival.
  reset();c('v020SetPlayer',{'ammoClip':0});a=c('v028NeedState')['mass'];c('v020SetPlayer',{'ammoClip':10});z=c('v028NeedState')['mass'];check(z>a,'Cartouches du chargeur actif comptées dans la charge')
  c('v020SetPlayer',{'ammoClip':9});check(abs(c('v028NeedState')['mass']-(a+(z-a)*.9))<1e-7,'Retrait d’une cartouche chargée enlève exactement sa masse')
  check(not c('v028NeedState')['enabled'] and not s()['v026']['carry'],'Besoins et surcharge non imposés au départ')
  c('v020Seed',{'ration':3,'food':3,'water':3});c('v028Needs',{'hunger':80,'thirst':80,'fatigue':80});c('v020SetPlayer',{'hp':s()['player']['maxHp']});op('survival');before=s()['inventory']['ration'];check(not act('need-use','ration') and s()['inventory']['ration']==before,'Besoins désactivés : ration sans effet utile non consommée')
  click('needs');check(c('v028NeedState')['enabled'],'Activation réelle des besoins dans le Pip-Boy')
  before=s()['inventory'];click('need-use','ration');check(s()['needs']['hunger']==40 and s()['inventory']['ration']==before['ration']-1,'Ration à PV pleins retire quarante points de faim')
  click('need-use','food');check(s()['needs']['hunger']==15,'Aliment retire vingt-cinq points de faim')
  click('need-use','water');check(s()['needs']['thirst']==45,'Eau retire trente-cinq points de soif')
  keys=c('v018Keys');stored=p.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',c('v018SaveKey'));check(stored['needs']==s()['needs'],'Besoins après consommation réellement sauvegardés')
  old=s()['needs'];c('v020Tick',2,True);check(s()['needs']==old,'Menus suspendent la progression des besoins')
  dismiss();c('v020Tick',2,True);check(s()['needs']['thirst']>old['thirst'],'Besoins progressent pendant le jeu actif')
  c('v028Settings',{'survivalNeeds':False});old=s()['needs'];c('v020Tick',2,True);check(s()['needs']==old,'Désactivation suspend sans effacer les besoins')
  load('relay_vent');near('relay_vent:station');c('v020Seed',{'caps':100,'ration':3});c('v028Needs',{'fatigue':80});c('v028Set',{'limbs':{'leftLeg':20}});before=s();check(c('v020Rest',1),'Repos réel disponible à la halte');check(s()['needs']['fatigue']==50 and st()['limbs']['leftLeg']==20,'Repos payé retire trente fatigue sans guérir les jambes')
  op('survival');p.locator('[data-p27="field"][data-arg="halte"]').click();check(c('getMode')=='FIELD' and 'Repos' in p.locator('#v020Body').inner_text(),'Passerelle Survie → Halte ouvre le vrai service')
  # JSON persistence with old keys protected.
  dismiss();load();c('v028Set',{'limbs':{'rightArm':28},'lamp':True});c('save');raw=s();p.evaluate('localStorage.setItem("fallout_mistral_save_v027","ancienne-source")');c('v028Set',{'limbs':{'rightArm':100},'lamp':False});c('v018ImportRaw',json.dumps(raw));check(st()['limbs']['rightArm']==28 and st()['lamp'],'Import validé conserve traumatismes et lampe')
  check(p.evaluate('localStorage.getItem("fallout_mistral_save_v027")')=='ancienne-source','Import ne supprime pas l’ancienne clé v027')
  # Actual mobile buttons and bounded layout.
  p.set_viewport_size({'width':390,'height':844});near('v028:medic');op();p.locator('.p28-limbs button[data-arg="rightArm"]').click();check('Bras droit' in p.locator('.p28-health-detail h2').inner_text(),'Fenêtre mobile : sélection corporelle effective')
  check(p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Interface mobile sans débordement horizontal de page')
  p.mouse.move(0,0);style=p.locator('.p28-limbs button.active').evaluate('(el)=>({bg:getComputedStyle(el).backgroundColor,color:getComputedStyle(el).color})');check(style['bg']!=style['color'] and style['bg']=='rgb(159, 236, 170)','Sélection corporelle contrastée même hors survol et sur tactile',style)
  c('v027Dispatch','theme','amber');style=p.locator('.p28-limbs button.active').evaluate('(el)=>getComputedStyle(el).backgroundColor');check(style=='rgb(245, 202, 117)','La sélection active respecte le phosphore ambre');c('v027Dispatch','theme','green')
  c('v020Seed',{'traumaKit':2});c('v027Set','status','health');click('treat','rightArm|traumaKit');check(st()['limbs']['rightArm']==100,'Bouton de soin réellement accessible sur fenêtre mobile')
 except Exception:check(False,'Exception dans la suite',traceback.format_exc());p.screenshot(path=str(O/'QA_V028_BODY_FAILURE.png'))
 check(not errors,'Aucune exception JavaScript de la suite',errors);b.close()
report=dict(html_sha256=hashlib.sha256(H.encode()).hexdigest(),passed=sum(x['ok']for x in checks),failed=sum(not x['ok']for x in checks),checks=checks,errors=errors,scope='Exact HTML, Chromium logiciel, états et arène synthétiques déclarés, clics réels. Stockage mémoire après refus natif opaque, pas de GPU/iPhone réel.');(O/'QA_V028_BODY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('TOTAL',report['passed'],report['failed']);raise SystemExit(bool(report['failed']))
