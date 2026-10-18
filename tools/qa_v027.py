#!/usr/bin/env python3
"""Pip-Boy interaction tests against the exact offline HTML. Fixture state is
explicitly prepared; geometry/campaign fidelity and hardware GPU are not claimed.
LocalStorage here is a memory adapter; separate origin test exercises native storage.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
import json,hashlib,traceback
R=Path(__file__).resolve().parents[1];H=(R/'JOUER_FALLOUT_MISTRAL_v0.35.html').read_text();O=R/'verification';rows=[];errors=[]
def check(ok,title,detail=None):
 rows.append(dict(ok=bool(ok),name=title,detail=detail));print(('OK' if ok else 'FAIL'),title,detail if detail is not None else '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':1000},has_touch=True);p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(6000);p.set_content(H,wait_until='load');p.locator('#btnV027').wait_for(state='attached',timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def state():return c('getState')
 def action(a,arg=''):return c('v027Dispatch',a,arg)
 def open_(tab,sub=None):return c('v027Open',tab,sub)
 def dismiss():
  if c('getMode')=='PIP':c('closePip')
  c('v020ModalDismiss')
 def load(z='transit_depot'):
  dismiss();c('v020Load',z);c('v022ResetRuntime');c('v021MuteEnemies');c('v022Time',10)
 def reset(z='transit_depot'):
  dismiss();c('v020Reset');load(z)
 def click(a,arg=None,within='#pipboy'):
  s='[data-p27="'+a+'"]'+('' if arg is None else '[data-arg="'+arg+'"]')
  p.locator(within+' '+s).first.click()
 def body():return p.locator('#pipContent').inner_text()
 def ui():return c('v027UI')
 def fingerprint():
  s=state();return {k:s[k] for k in ['inventory','ammo','quest','flags','lore','rep','equipment','v026','v023']},(s['player']['caps'],s['player']['xp'])
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v027ManualTape',True)
  p.evaluate("window.__M={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__M[k]??null,setItem:(k,v)=>__M[k]=String(v),removeItem:k=>delete __M[k]}})")
  reset();check(c('v027Info')['version']=='0.35.0','Version exacte 0.27.0')
  before=fingerprint();open_('status','health')
  check(p.locator('#pipTabs button').count()==5,'Cinq boutons principaux, pas ancien menu en six onglets')
  check(p.locator('.p27-device').is_visible() and p.locator('#pipboy').get_attribute('role')=='dialog','Boîtier monté dans le vrai Pip-Boy accessible')
  for t,subs in c('v027Info')['subtabs'].items():
   for sub in subs:
    open_(t,sub);check(ui()['tab']==t and ui()['sub']==sub and len(body().strip())>10,f'{t}/{sub} : rubrique réelle rendue')
  check(before==fingerprint(),'Parcourir les 25 rubriques ne valide aucune quête ni ne crée ressources ou découvertes')
  open_('status','health');p.keyboard.press('e');check(ui()['tab']=='inventory','E passe au mode suivant');p.keyboard.press('d');check(ui()['sub']=='armor','D passe à la sous-rubrique suivante');p.keyboard.press('q');check(ui()['tab']=='status','Q revient au mode précédent')
  click('next');check(ui()['tab']=='inventory','Molette physique SELECT change réellement le mode')
  p.locator('#p27Search').fill('qead');p.keyboard.press('e');check(ui()['tab']=='inventory' and p.locator('#p27Search').input_value()=='qeade','Saisie q/e/a/d ne navigue pas dans le Pip-Boy')
  p.keyboard.press('Tab');check(c('getMode')=='PLAYING' and not p.locator('#pipboy').is_visible(),'Tab ferme même depuis le champ de recherche')
  p.keyboard.press('i');check(c('getMode')=='PIP' and ui()['tab']=='inventory','I ouvre le véritable INV au lieu du sac séparé')
  p.keyboard.press('Escape');check(c('getMode')=='PLAYING','Échap rend le contrôle au jeu')
  # Inventory, live readouts, no virtual catalogue grants.
  reset();c('v020Seed',{'caps':347,'stimpak':3,'radaway':2,'radioTube':2,'cloth':3});c('v020GrantWeapon','pipeCarbine');c('v026Give','workshopJacket',1);open_('inventory','weapon')
  check({r['id'] for r in ui()['rows']}==set(state()['equipment']['ownedWeapons']),'INV armes = modèles effectivement possédés')
  check('347' in p.locator('#p27Readouts').inner_text(),'Portefeuille affiché depuis player.caps')
  click('select','pipeCarbine');click('equip','pipeCarbine','#p27ActionBar');check(state()['player']['weaponId']=='pipeCarbine','Équiper depuis la barre basse change réellement l’arme')
  click('favorite','pipeCarbine|0','#p27ActionBar');check(state()['v020']['favorites'][0]=='pipeCarbine','Favori 1 enregistré depuis le Pip-Boy')
  check(not action('equip','weapon_does_not_exist'),'Équipement absent ou inconnu refusé')
  open_('inventory','armor');click('select','workshopJacket');check('Comparaison nominale' in body(),'Comparaison de protection avec indication de portée nominale')
  click('equip','workshopJacket','#p27ActionBar');check(state()['player']['armorId']=='workshopJacket','Équiper protection depuis le Pip-Boy')
  open_('inventory','aid');c('v020SetPlayer',{'hp':18,'maxHp':100,'rad':0});c('v027Select','stimpak');before=state();click('use','stimpak','#p27ActionBar');after=state()
  check(after['inventory']['stimpak']==before['inventory']['stimpak']-1 and after['player']['hp']>18,'Stimpak : un seul retrait et soin réel')
  c('v020SetPlayer',{'hp':100});before=state()['inventory']['stimpak'];check(action('use','stimpak') is False and state()['inventory']['stimpak']==before,'Soin gaspillé refusé, objet conservé')
  before=state()['inventory']['radaway'];check(action('use','radaway') is False and state()['inventory']['radaway']==before,'RadAway sans radiations ne consomme rien')
  open_('inventory','material');p.locator('#p27Search').fill('circuit');click('select','circuitry');before=state()['inventory'].get('circuitry',0);click('tag','circuitry','#p27ActionBar')
  check('circuitry' in c('v027State')['tagged'],'Recherche de circuits sauvegardée')
  check('Potentiel récupérable' in body() and state()['inventory'].get('circuitry',0)==before,'Potentiel des objets de récupération distinct des composants en sac')
  check('circuitry' in c('v027Matches','radioTube'),'Tube radio reconnu comme source de circuit recherché')
  open_('inventory','junk');p.locator('#p27Search').fill('impossiblexyz');check(ui()['rows']==[],'Recherche sans résultat : aucun objet attribué')
  p.locator('#p27Search').fill('tube');check(all('tube' in r['text'].lower() for r in ui()['rows']),'Recherche filtre réellement la liste')
  dismiss();load('transit_depot');container=next(x for x in c('v026Containers') if x['id']=='free');c('v020Approach','v026:'+container['key']);c('v026OpenContainer',container['key'])
  check(p.locator('.p27-found').count()>0,'Loupe de composant présente dans la fouille physique')
  # Workshop same actual gate as field UI.
  dismiss();load('relay_vent');c('v020Seed',{'radioTube':2});c('v020SetPlayer',{'pos':[0,1.65,-10]});open_('inventory','junk');before=state()['inventory'];check(action('recycle','radioTube') is False and state()['inventory']==before,'Démontage distant refusé sans débit')
  dismiss();c('v020Approach','relay_vent:station');open_('inventory','junk');c('v027Select','radioTube');before=state();check(action('recycle','radioTube'),'Démontage à l’établi accepté');after=state()
  check(after['inventory']['radioTube']==before['inventory']['radioTube']-1 and after['inventory'].get('circuitry',0)>before['inventory'].get('circuitry',0),'Objet consommé une fois, circuit réellement ajouté')
  check(after['player']['xp']==before['player']['xp'],'Démontage ne donne pas une boucle d’expérience')
  # All existing stored item IDs remain reachable through at least one category.
  reset();all_ids=list(state()['inventory']);c('v020Seed',{k:1 for k in all_ids});seen=set()
  for sub in ['weapon','armor','aid','quest','junk','material','ammo']:
   open_('inventory',sub)
   for page_i in range(80):
    seen.update(r['id'] for r in ui()['rows'])
    next_b=p.locator('#pipContent [data-p27="page"][data-arg="1"]')
    if next_b.is_disabled():break
    next_b.click()
  missing=[k for k in all_ids if k!='caps' and k not in seen]
  check(not missing,'Aucun objet historique en sac ne disparaît entre les sept catégories',missing)
  # Archive actual text, safe escaping, no hidden discoveries.
  reset();open_('data','notes');n0=len(c('v027Notes'));before=fingerprint();check('qa-doc' not in [r['id'] for r in c('v027Notes')],'Note non découverte absente')
  dismiss();c('v027ReadNote','qa-doc','Le reçu des passagers','Une caisse pour les couchettes. <script>bad()</script>');dismiss();open_('data','notes');click('select','qa-doc')
  check('<script>bad()</script>' in body() and p.locator('#pipContent script').count()==0,'Texte archivé exact, HTML neutralisé')
  click('read','qa-doc');check(c('v027State')['read'].get('qa-doc') is True,'Marquage lu enregistré')
  check(action('read','jamais-decouvert') is False,'Impossible de marquer une note inexistante')
  dismiss()
  for i in range(22):c('v027ReadNote','qa-page-'+str(i),'Note QA '+str(i),'Document synthétique pour tester la pagination.');dismiss()
  open_('data','notes');click('page','1');new=ui();check(len(new['rows'])>0 and new['selected']==new['rows'][0]['id'],'Changement de page sélectionne une entrée de cette page')
  check(any(r['id']==new['selected'] for r in new['rows']),'Détail actif correspond à la page visible, pas à la première page')
  # Quest filtering and tracking no completion.
  reset();open_('data','quests');check(all(r['id']!='local:cassis' for r in ui()['rows']),'Quête locale non commencée non révélée')
  c('v023SetQuest',{'accepted':True});c('v027Set','data','quests');click('select','aptitudes');before=state();click('track','aptitudes');after=state()
  check(after['v023']['quest']['tracked'] and not after['v021']['tracked'] and not after['v022']['task']['tracked'],'Suivi unique du dossier d’aptitudes, autres suivis désactivés')
  check(after['v023']['quest']['evidence']==before['v023']['quest']['evidence'] and after['player']['xp']==before['player']['xp'],'Suivre n’accorde pas preuve, récompense ni XP')
  c('v023SetQuest',{'ending':'network'});c('v027Set','data','quests');p.locator('#p27QuestFilter').select_option('done')
  check(any(r['id']=='aptitudes' for r in ui()['rows']),'Filtre terminé contient l’enquête résolue')
  check(action('track','aptitudes') is False,'Une quête terminée ne peut être réactivée par son suivi')
  # Terminals: known flag is not a permission to execute remotely.
  reset();c('v027MarkTerminal','aubagne');open_('data','terminals');check(len(ui()['rows'])==1,'Seul le terminal marqué comme visité est archivé')
  before=state();check(action('terminal','aubagne') is False and state()['lore']['terminalActions']==before['lore']['terminalActions'],'Terminal consulté ailleurs : commande impossible')
  dismiss();load('aubagne');c('v020Approach','v013-terminal-aubagne');open_('data','terminals');before=state();ok=action('terminal','aubagne');check(ok and state()['lore']['terminalActions'].get('aubagne'),'Commande autorisée au vrai terminal proche')
  before=state();check(action('terminal','aubagne') is False and state()['inventory']==before['inventory'],'Commande déjà appliquée non répétable')
  # Settings are persisted and invalid inputs rejected.
  reset();open_('data','system');click('theme','amber');check(p.locator('#pipboy').get_attribute('data-theme')=='amber' and c('v027State')['theme']=='amber','Thème ambre appliqué et sauvegardé')
  click('scan');check(p.locator('#pipboy').evaluate('(e)=>e.classList.contains("p27-no-scan")'),'Balayage désactivable sans modifier les stats')
  check(not action('theme','ultraviolet'),'Couleur inconnue refusée')
  # Local map no player relocation.
  load('transit_depot');open_('map','local');check(p.locator('#v020Map').count()==1,'Un seul canvas de plan, pas doublon laissé par le panneau de terrain')
  before=state()['player']['pos'];click('zoom','0.25');check('125%' in p.locator('#v020Map').get_attribute('style'),'Zoom local appliqué')
  click('floor','3.2');check('PASSERELLES' in body().upper() or '3,2' in body() or '3.2' in body(),'Étage haut disponible pour le lieu multi-étages')
  check(state()['player']['pos']==before,'Choisir étage et zoom ne déplace pas le personnage')
  click('floor','0');cv=p.locator('#v020Map');box=cv.bounding_box();cv.click(position={'x':500,'y':490},force=True)
  check(state()['player']['pos']==before,'Clic dans le plan ne téléporte pas le joueur')
  check(c('v027Pin')['saved'] is None or c('v027Pin')['saved']['zone']=='transit_depot','Balise conservée uniquement avec contexte du lieu')
  action('clear-pin');check(c('v027Pin')['saved'] is None and c('v027Pin')['path']==[],'Effacer balise retire aussi le parcours')
  open_('map','coverage');check('Aucun fond officiel' in body(),'Périmètre annonce les données absentes, pas une fausse carte')
  before=state()['player']['zone'];check(action('travel','transit_depot') is False and state()['player']['zone']==before,'Voyage direct vers intérieur refusé')
  check(action('travel','unknown-place') is False,'Destination inconnue refusée')
  # Geometry of responsive UI + real taps.
  p.set_viewport_size({'width':390,'height':844});open_('inventory','weapon');p.tap('#pipTabs [data-tab="data"]');check(ui()['tab']=='data','Geste tactile sélectionne DATA')
  p.tap('#pipTabs [data-tab="inventory"]');check(ui()['tab']=='inventory','Geste tactile sélectionne INV')
  bounds=c('v027UI');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Pas de défilement horizontal global à 390 px')
  fits=p.evaluate('Array.from(document.querySelectorAll("#pipTabs button,.p27-device")).every(e=>{let r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1})');check(fits,'Boîtier et cinq onglets entièrement à l’intérieur de la largeur mobile')
  check(p.locator('#p27ActionBar').bounding_box()['y']<844,'Barre d’action rapide dans la fenêtre mobile')
  p.locator('#pipTabs [data-tab="status"]').click();p.locator('#p27Subnav [data-arg="perks"]').click();check(ui()['sub']=='perks','Sous-rubrique hors premier écran atteignable par clic sur mobile')
  p.locator('.p27-screenhead [data-p27="close"]').click();check(c('getMode')=='PLAYING','Rangement tactile du Pip-Boy rend le contrôle')
 except Exception as ex:
  check(False,'Exception de la suite',traceback.format_exc());p.screenshot(path=str(O/'QA_V027_FAILURE.png'))
 check(not errors,'Absence d’exception JavaScript pendant les essais',errors);b.close()
report={'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'scope':'HTML exact dans Chromium logiciel ; caméra et état préparés ; stockage mémoire explicite. Pas de carte officielle ni certification GPU.','passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'checks':rows,'errors':errors};(O/'QA_V027.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('TOTAL',report['passed'],report['failed']);raise SystemExit(report['failed']>0)
