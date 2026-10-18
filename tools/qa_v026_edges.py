#!/usr/bin/env python3
"""Edge-case transactions and native touchscreen checks on the shipped HTML.
Prepared scenario states are explicit. Tests use a memory storage adapter."""
from pathlib import Path
import json,hashlib,traceback
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];H=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[]
def ck(ok,n,d=None):rows.append(dict(ok=bool(ok),name=n,detail=d));print('OK'if ok else'FAIL',n,d or '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV026').wait_for(timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def d():c('v020ModalDismiss')
 def load(z):d();c('v020Load',z);c('v022ResetRuntime');c('v022Time',10);c('v021MuteEnemies')
 def chest(z,i):load(z);c('v020Approach','v026:'+z+'|'+i);c('v026OpenContainer',z+'|'+i)
 c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
 p.evaluate("window.__TEST26={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__TEST26[k]??null,setItem:(k,v)=>__TEST26[k]=String(v),removeItem:k=>delete __TEST26[k]}})")
 try:
  c('v020Reset');load('transit_depot');c('v020Approach','v022:salome:talk');c('v020Interact','v022:salome:talk');ck(p.locator('#dialogueChoices button').filter(has_text='réserves dites abandonnées').count()==1,'La quête est reliée au dialogue normal de Salomé');p.locator('#dialogueChoices button').filter(has_text='réserves dites abandonnées').click();ck(p.locator('#dialogueLine').inner_text().find('lot')>=0,'Le vrai lien ouvre le dialogue des réserves');d()
  chest('traverse_archives','consignment');p.locator('[data-v26="owned"]').click();c('v026Take','water',1);ck(s()['crime']['marseille']>0 and s()['crime']['collines']==0,'Crime des archives attribué à Marseille, pas aux collines',s()['crime']);d()
  c('v020Reset');chest('transit_depot','workcase');c('v026Give','bobbyPin',2);c('v026LockSet',c('v026LockTarget','transit_depot|workcase'));c('v026TurnLock');c('v020GrantWeapon','pipeCarbine');p0=s()['inventory']['weaponParts'];ck(not c('v026Take','pipeCarbine',1),'Pas de double exemplaire créé silencieusement');ck(c('v026RecoverDuplicate','pipeCarbine'),'Démontage du doublon explicitement demandé');ck(s()['inventory']['weaponParts']==p0+2 and not c('v026RecoverDuplicate','pipeCarbine'),'Pièces du doublon récupérées une fois');d()
  # Actual free-fire death via the existing emitter, not direct killEnemy.
  c('v020Reset');c('v020Fixture',False,'raider',5);c('v020EnemyPatch',{'health':1,'loot':{'key':True,'caps':7,'ammo':3}});c('v020Tick',1);c('v020Vats');c('v023Select',0,'body');c('v023Crit',100);c('v023Queue',True);c('v020VatsExecute');c('v020RandomTick',.2,.01);ck(not c('v020Stats')['enemy'][0]['alive'],'Une véritable exécution VATS crée la mort');ck(len(c('v026Containers'))==1,'Le décès par VATS passe par le conteneur persistant');ck(s()['inventory']['shipKey']>0 and s()['flags']['bossDefeated'],'La clé et les verrous narratifs historiques restent immédiats');ck(s()['player']['caps']==18,'Les capsules restent sur le corps après le tir');c('v020VatsCancel')
  # Used mods: stock must remember both metadata and empty magazine.
  c('v020Reset');load('aubagne');c('v020Seed',{'scrap':100,'circuitry':100,'weaponParts':100,'sealant':10,'caps':50000});c('v020GrantWeapon','pipeCarbine');c('installWeaponMod','pipeCarbine');ck(s()['equipment']['weaponMods']['pipeCarbine'],'Modification initiale installée pour essai');c('v026Condition','pipeCarbine',36);c('v026Trade','aubagne');c('v026Sell','pipeCarbine');ck(c('v026State')['vendorGear']['aubagne']['pipeCarbine']['mod'],'Modification enregistrée chez le marchand');c('v026Buy','pipeCarbine');ck(s()['equipment']['weaponMods']['pipeCarbine'] and s()['equipment']['weaponCondition']['pipeCarbine']==36,'Rachat conserve modification et usure');before=s()['player']['caps'];c('v020SetPlayer',{'pos':[80,1.65,80]});ck(not c('v026Sell','pipeCarbine') and s()['player']['caps']==before,'Échange périmé après déplacement refusé');c('v026CloseTrade')
  # Multiple used copies held by a vendor retain their distinct states, while
  # the player still owns only one of each model at a time.
  load('aubagne');c('v026Trade','aubagne');c('v026Condition','pipeCarbine',30);c('v026Sell','pipeCarbine');c('v020GrantWeapon','pipeCarbine');c('v026Condition','pipeCarbine',58);c('v026Sell','pipeCarbine');ck(len(c('v026State')['vendorGear']['aubagne']['pipeCarbine']['queue'])==1,'Deux exemplaires usés gardent leurs métadonnées au comptoir');c('v026Buy','pipeCarbine');ck(s()['equipment']['weaponCondition']['pipeCarbine']==58,'Premier rachat : état de la dernière arme vendue');ck(c('v026State')['vendorGear']['aubagne']['pipeCarbine']['condition']==30,'Le stock restant conserve le second état, sans remise à neuf');c('v026CloseTrade')
  # Stale DOM callbacks cannot move items from a different scene.
  c('v020Reset');chest('transit_depot','free');p.locator('[data-v26="select|radioTube"]').click();p.evaluate("window.__oldTake=document.querySelector('[data-v26=\"take|radioTube|1\"]').onclick");load('mooring_station');pre=s()['inventory'].get('radioTube',0);p.evaluate('window.__oldTake()');ck(s()['inventory'].get('radioTube',0)==pre,'Ancien callback de bouton ne prélève pas après transition')
  # All 12 new salvage families are obtainable, including robot optics.
  ids=set()
  for z in ['transit_depot','traverse_archives','mooring_station','relay_vent','relay_cold','relay_brake']:
   load(z)
   for a in c('v026Containers'):ids.update(a['initial'])
  load('transit_depot');# optical loot tested in main suite
  expected={'enamelCup','radioTube','rationTin','ceramicShard','woolBlanket','emptyInjector','instrumentTray','burntMotor','seaRope','brassValve','crackedGauge'}
  ck(expected<=ids,'Onze objets de récupération sont réellement placés, optique sur robots',sorted(expected-ids))
  # One stale replay must not cancel an agreement nor refill distributed lots.
  q={'accepted':True,'informed':True,'inspected':dict.fromkeys(['transit_depot','traverse_archives','mooring_station'],True),'ending':None,'rewarded':False,'tracked':False};c('v026Set',{'quest':q});c('v020Approach','v022:salome:talk');c('v026Preview','share');p.locator('#dialogueChoices button').filter(has_text='Confirmer').click();d();chest('transit_depot','consignment');ck(not c('v026ReturnItem','cloth',1),'Pas de restitution dans un lot déjà remis aux destinataires');ck(c('v026Missing')=={},'Le bilan ne réclame pas à nouveau les fournitures distribuées');p.locator('[data-v26="all"]').click();d();chest('transit_depot','consignment');ck(sum(c('v026State')['containers']['transit_depot|consignment']['items'].values())==0,'Le partage n’est pas renouvelé au rechargement')
  # Genuine touchscreen taps, rather than dispatch_event.
  p2=b.new_page(viewport={'width':390,'height':844},has_touch=True);p2.on('pageerror',lambda e:errors.append(str(e)));p2.set_content(H,wait_until='load');p2.locator('#btnV026').wait_for(timeout=30000)
  def m(n,*a):return p2.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
  m('setRenderPaused',True);m('v022Freeze',True);m('v018NoNetwork',True);p2.evaluate("window.__M={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__M[k]??null,setItem:(k,v)=>__M[k]=String(v),removeItem:k=>delete __M[k]}})");m('v020Reset');m('v020Load','transit_depot');m('v022ResetRuntime');m('v021MuteEnemies');m('v020Approach','v026:transit_depot|free');m('v020Interact','v026:transit_depot|free')
  def tap(sel):
   loc=p2.locator(sel).first;loc.scroll_into_view_if_needed();box=loc.bounding_box();p2.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
  tap('[data-v26="select|enamelCup"]');pre=m('getState')['inventory'].get('enamelCup',0);tap('[data-v26="take|enamelCup|1"]');ck(m('getState')['inventory']['enamelCup']==pre+1,'Tap natif sur écran étroit transfère un objet');tap('[data-v26="close"]');ck(m('getMode')=='PLAYING','Fermeture tactile rend la main au jeu');m('v026Open');ck(p2.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Pas de débordement horizontal du sac après transfert tactile');p2.close()
 except Exception as e:ck(False,'Exception extra',str(e));traceback.print_exc()
 ck(not errors,'Aucune exception JavaScript',errors);b.close()
out=dict(version='0.30.0',html_sha256=hashlib.sha256(H.encode()).hexdigest(),total=len(rows),passed=sum(r['ok']for r in rows),failed=sum(not r['ok']for r in rows),errors=errors,scope='Authored maps, explicit synthetic VATS kill, native clicks and touchscreen taps, memory storage adapter',results=rows);(R/'verification/QA_V026_EDGES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('RESULT',out['total'],out['failed']);raise SystemExit(bool(out['failed']))
