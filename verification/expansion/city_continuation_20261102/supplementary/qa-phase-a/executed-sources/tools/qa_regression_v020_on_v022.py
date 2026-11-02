#!/usr/bin/env python3
"""Targeted gameplay QA. Exact built HTML; simulated storage explicitly labelled.
No test in this suite validates geographic fidelity, real GPU performance or a
complete human campaign playthrough. QA fixture never enters distributed saves.
"""
from pathlib import Path
from qa_support import chromium_path
import json, math, traceback, hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
rows=[];errors=[];D='__MISTRAL_DEBUG';html=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text()
def check(ok,name,detail=None):
 rows.append({'ok':bool(ok),'name':name,'detail':detail});print(('OK  ' if ok else 'FAIL'),name, '' if detail is None else str(detail)[:160],flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 pg=b.new_page(viewport={'width':1440,'height':900});pg.set_default_timeout(8000);pg.on('pageerror',lambda e:errors.append(str(e)));pg.set_content(html,wait_until='load');ev=pg.evaluate
 pg.wait_for_timeout(3300);ev(D+'.v018NoNetwork(true);'+D+'.setRenderPaused(true)')
 def js(s,arg=None):return ev(s,arg)
 def call(name,arg=None):return js('(a)=>__MISTRAL_DEBUG.'+name+'(a)',arg)
 def load(id):call('v020Load',id);js(D+'.v018CaptureAt('+D+'.v020Stats().player,0,0)')
 def approach(id):return call('v020Approach',id)
 def dismiss():js(D+'.v020ModalDismiss()')
 def state():return js(D+'.getState()')
 def interact(id):return call('v020Interact',id)
 try:
  check(js(D+'.v020Version().version')=='0.20.0','Version et modules initialisés')
  check(js('document.title').endswith('Sous la cuirasse'),'Titre exact de la build')
  check(js(D+'.v020Version().actualMapTiles')==0,'Pas de prétendue acquisition cartographique')
  check(js(D+'.v020Version().recipes')==20,'20 recettes : 18 conservées et 2 soins supplémentaires')
  check(len(js(D+'.v020Version().operations'))==3,'3 interventions distinctes enregistrées')
  load('relay_vent');failedsave=js(D+'.save()');check(failedsave is False,'Refus réel du stockage opaque détecté, sans succès fictif',js(D+'.v018PersistentStatus()'))
  js('''window.__storageMap={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>Object.prototype.hasOwnProperty.call(__storageMap,k)?__storageMap[k]:null,setItem:(k,v)=>{__storageMap[k]=String(v)},removeItem:k=>delete __storageMap[k],clear:()=>{__storageMap={}}}})''')
  check(js(D+'.save()') is True,'Écriture vérifiée via adaptateur de stockage contrôlé')
  # Three concrete layouts; routes from spawn and resolutions exercised through real actions.
  for op in js(D+'.v020Version().operations'):
   js(D+'.v020Reset()');load(op);stats=js(D+'.v020Stats()')
   check(stats['id']==op,op+' : construction du bon intérieur')
   check(stats['draws']>=400 and stats['colliders']>=10,op+' : décor et collisions présents',{'draws':stats['draws'],'colliders':stats['colliders']})
   check(len(stats['rooms'])==5,op+' : cinq espaces de fonction différente')
   paths=[]
   for it in stats['interactables']:
    path=call('v020Route',it['pos']);paths.append({'id':it['id'],'nodes':len(path or [])})
   check(all(x['nodes'] for x in paths),op+' : tous les postes atteignables par le graphe local',paths)
   check(not call('v020Collides',stats['player']),op+' : apparition hors collision')
   check(not js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"finish","public")',op),op+' : récompense impossible à distance et avant étapes')
   approach(op+':contact');interact(op+':contact')
   if op=='relay_cold':pg.locator('#dialogueChoices button').filter(has_text='chambre froide').click()
   pg.locator('#dialogueChoices button').first.click();dismiss()
   check(state()['v020']['operations'][op]['accepted'],op+' : acceptation par dialogue réel')
   approach(op+':isolate');check(not js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"isolate")',op),op+' : consignation exige un diagnostic')
   approach(op+':terminal');check(js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"terminal")',op),op+' : diagnostic lu sur place');dismiss()
   approach(op+':part');check(js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"part")',op),op+' : composant récupéré sur place')
   s0=state();js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"part")',op);check(state()['inventory']==s0['inventory'],op+' : composant non duplicable')
   approach(op+':isolate');check(js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"isolate")',op),op+' : coupure du circuit')
   if op=='relay_brake':check(not js(D+'.v020Stats().enemy[0].alive'),'Palan : consignation neutralise le Protectron sans tir')
   approach(op+':finish');before=state();check(js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"finish","public")',op),op+' : issue publique et récompense');dismiss()
   after=state();check(after['v020']['operations'][op]['resolution']=='public',op+' : conséquence persistante enregistrée')
   check(after['player']['caps']-before['player']['caps']==75,op+' : montant de capsules exact')
   js('(id)=>__MISTRAL_DEBUG.v020OpAction(id,"finish","public")',op);check(state()['player']['caps']==after['player']['caps'],op+' : récompense non répétable')
   load(op);check(js(D+'.v020Stats().draws')>stats['draws'],op+' : changement de scène visible après restauration')
  # All nine decisions are individually callable, not just labels in a menu.
  for op in js(D+'.v020Version().operations'):
   for choice in ['atelier','recover']:
    js(D+'.v020Reset()');load(op);js('([id,c])=>__MISTRAL_DEBUG.v020SetOp(id,{accepted:true,diagnosed:true,component:true,isolated:true})',[op,choice]);approach(op+':finish')
    check(js('([id,c])=>__MISTRAL_DEBUG.v020OpAction(id,"finish",c)',[op,choice]),op+' : résolution alternative '+choice);dismiss()
  # Real parent portal, arrival, return position. No teleport button in player field panel.
  js(D+'.v020Reset()');load('aubagne');stats=js(D+'.v020Stats()');check(any(i['id']=='v020:portal:relay_vent' for i in stats['interactables']),'Aubagne : entrée de relève physique dans le quartier historique')
  approach('v020:portal:relay_vent');js(D+'.v020SetPlayer({yaw:.48,pitch:.13})');before=state()['player'];check(call('v020Enter','relay_vent'),'Entrée dans la relève via le portail proche')
  check(js(D+'.getWorld()')=='relay_vent','Entrée charge effectivement l’intérieur')
  js(D+'.save()');saved=js('JSON.parse(localStorage.getItem(__MISTRAL_DEBUG.v018SaveKey()))');check(saved['v020']['returnPoint']['zone']=='aubagne','Point de retour conservé dans la sauvegarde')
  approach('relay_vent:exit');check(js(D+'.v020Exit()'),'Sortie physique de l’intérieur');after=state()['player']
  check(math.dist(before['pos'],after['pos'])<.001 and abs(after['yaw']-before['yaw'])<.001 and abs(after['pitch']-before['pitch'])<.001,'Position et orientation parent restaurées',{'before':before['pos'],'after':after['pos']})
  # Door logic and map invalidation.
  load('relay_vent');approach('relay_vent:door');check(call('v020Door','relay_vent:door'),'Porte manipulable à proximité');check(state()['v020']['openedDoors']['relay_vent:door'],'Ouverture persistante')
  js(D+'.v020SetPlayer({pos:[-5,1.65,-6]})');check(call('v020Door','relay_vent:door') is False,'Porte refuse de se fermer sur le joueur')
  # Physical crafting and exact inventory accounting, all registered recipes.
  js(D+'.v020Reset()');load('relay_vent');recipes=js(D+'.v020Recipes()');seed={k:500 for r in recipes for k in r['cost']};seed.update({'caps':1000});call('v020Seed',seed)
  js(D+'.v020SetPlayer({pos:[0,1.65,-10]})');inv=state()['inventory'];check(call('v020Craft','bandage') is False and inv==state()['inventory'],'Atelier interdit à distance sans débiter les ressources')
  approach('relay_vent:station');xp=state()['player']['xp']
  for r in recipes:
   prev=state();ok=call('v020Craft',r['id']);cur=state();outkey='ammo' if r['item'] in cur['ammo'] else 'inventory'
   costs=all(cur['inventory'].get(k,0)==prev['inventory'].get(k,0)-n for k,n in r['cost'].items())
   produced=cur[outkey].get(r['item'],0)-prev[outkey].get(r['item'],0)==r['count']
   check(ok and costs and produced,'Recette réelle : '+r['name'],{'costs':costs,'produced':produced})
  check(state()['player']['xp']==xp,'Fabrication ne génère pas de boucle d’XP')
  call('v020Seed',{'cloth':0,'chemicals':0});prev=state()['inventory'];check(call('v020Craft','bandage') is False and state()['inventory']==prev,'Ressources insuffisantes : aucun débit partiel')
  check(call('v020Craft','inconnue') is False,'Recette inconnue rejetée')
  # Rest, stash, shortcuts and UI.
  call('v020Seed',{'cloth':10,'caps':500,'ration':2});prev=state()['inventory'].get('cloth',0);check(js(D+'.v020Stash("cloth",1)'),'Dépôt dans la réserve près de la halte');check(js(D+'.v020Stash("cloth",-1)') and state()['inventory']['cloth']==prev,'Reprise de réserve sans duplication')
  check(js(D+'.v020Stash("concordeSeal",1)') is False,'Objet de quête exclu de la réserve')
  js(D+'.v020SetPlayer({hp:35,rad:18,ap:20})');s=state();check(call('v020Rest',1),'Repos d’une heure à la halte');t=state();check(t['player']['hp']==53 and t['player']['rad']==18 and t['player']['caps']==s['player']['caps']-8,'Repos : coût, soin et radiations inchangées')
  js(D+'.v020SetPlayer({pos:[0,1.65,-10]})');check(call('v020Rest',4) is False,'Repos impossible à distance')
  dismiss();pg.keyboard.press('t');check(js(D+'.getMode()')=='FIELD','T ouvre le panneau de terrain');pg.get_by_role('button',name='Arsenal équipé',exact=True).click();check(pg.locator('#v020Body').inner_text().find('Pistolet 10 mm')>=0,'Inventaire équipé accessible par clic')
  pg.locator('#v020Search').fill('ZZZintrouvable');check(pg.locator('#v020Body .v20-card').count()==0,'Filtre d’équipement réellement appliqué')
  pg.keyboard.press('Escape');check(js(D+'.getMode()')=='PLAYING','Échap ferme le champ de recherche et le panneau')
  pg.keyboard.press('m');check(pg.locator('#v020Map').is_visible(),'M ouvre le plan local');pg.locator('#v020Map').click(position={'x':260,'y':180});check(pg.locator('#v020PathInfo').inner_text()!='','Plan : destination cliquée traitée')
  pin=js('''()=>{const cv=document.querySelector('#v020Map'),r=cv.getBoundingClientRect(),[x0,x1,z0,z1]=__MISTRAL_DEBUG.v020Stats().id==='relay_vent'?[-15,15,-15,15]:[-15,15,-15,15],scale=Math.min((860-70)/(x1-x0),(560-70)/(z1-z0)),ox=(860-(x1-x0)*scale)/2,oz=(560-(z1-z0)*scale)/2,x=-10,z=-7;cv.dispatchEvent(new MouseEvent('click',{clientX:r.left+(ox+(x-x0)*scale)/860*r.width,clientY:r.top+(oz+(z-z0)*scale)/560*r.height,bubbles:true}));return __MISTRAL_DEBUG.v020MapState();}''')
  check(abs(pin['pin'][0]+10)<.1 and abs(pin['pin'][2]+7)<.1,'Clic du plan correctement reprojeté aux coordonnées locales',pin['pin']);dismiss()
  pg.dispatch_event('body','keydown',{'key':'m','code':'Semicolon','bubbles':True});check(js(D+'.getMode()')=='FIELD' and pg.locator('#v020Map').is_visible(),'Clavier AZERTY : la lettre M ouvre aussi le plan');dismiss()
  # Cadence / reload / VATS in an explicitly synthetic isolated arena.
  js(D+'.v020Reset()');js(D+'.v020Fixture(false)');call('v020GrantWeapon','pistol10');call('v020Equip','pistol10');js(D+'.v020Tick(1)');start=state()['player']['ammoClip'];js(D+'.v020RandomFire(.5)');js(D+'.v020RandomFire(.5)');check(state()['player']['ammoClip']==start-1,'Cadence : deux appels immédiats ne consomment qu’un tir')
  js(D+'.v020Tick(.4)');js(D+'.v020RandomFire(.5)');check(state()['player']['ammoClip']==start-2,'Cadence : le tir suivant est autorisé après délai')
  call('v020Seed',{'ammo10':100});pg.keyboard.press('r');check(js(D+'.v020Combat().reload')>0,'R lance le rechargement')
  call('v020GrantWeapon','pipeCarbine');oldclip=state()['equipment']['loadedAmmo']['pistol10'];call('v020Equip','pipeCarbine');check(js(D+'.v020Combat().reload')==0,'Changer d’arme annule le rechargement en cours');js(D+'.v020Tick(3,true)');check(state()['equipment']['loadedAmmo']['pistol10']==oldclip,'Ancienne arme non rechargée par le minuteur annulé')
  js(D+'.v020Fixture(false)');call('v020Equip','pistol10');js(D+'.v020Tick(1)');call('v020Seed',{'ammo10':100});pg.keyboard.press('r');
  for _ in range(35):js(D+'.v020Tick(.05,true)')
  check(state()['player']['ammoClip']==10,'Rechargement fini : chargeur du pistolet correctement rempli')
  for weapon in ['pistol10','pipeCarbine']:
   js(D+'.v020Fixture(false)');call('v020GrantWeapon',weapon);call('v020Equip',weapon);js(D+'.v020Tick(1)');expected=js('(id)=>__MISTRAL_DEBUG.v020Damage(id)',weapon);beforehp=js(D+'.v020Stats().enemy[0].hp');before=state()['player'];js(D+'.v020Vats()');check(js(D+'.v020QueueBody()'),'VATS : torse mis en file avec '+weapon);js(D+'.v020VatsExecute()');js(D+'.v020RandomTick(.05,.5)');after=state()['player'];dealt=beforehp-js(D+'.v020Stats().enemy[0].hp')
   check(abs(dealt-expected)<.01,'VATS utilise les dégâts de '+weapon+' (pas une valeur fixe)',{'expected':expected,'actual':dealt})
   check(after['ap']==before['ap']-25 and after['ammoClip']==before['ammoClip']-1,'VATS débite une seule action réellement émise : '+weapon)
   js(D+'.v020VatsCancel()')
  js(D+'.v020Fixture(false)');call('v020Equip','pistol10');js(D+'.v020Tick(1)');js(D+'.v020Vats();'+D+'.v020QueueBody()');s=state()['player'];js(D+'.v020AddWall();'+D+'.v020VatsExecute();'+D+'.v020RandomTick(.05,.5)');t=state()['player'];check(s['ap']==t['ap'] and s['ammoClip']==t['ammoClip'],'Obstacle après mise en file : action annulée sans PA ni munition')
  load('relay_vent');check(js(D+'.v020Combat().execution') is None,'Changement de scène annule la file VATS')
  js(D+'.v020Fixture(true)');call('v020Equip','pistol10');js(D+'.v020Tick(1)');check(js(D+'.v020Vats()')=='PLAYING','VATS ne sélectionne pas une cible derrière un mur')
  auto=js(D+'.v020AutomaticIds()[0]');js(D+'.v020Fixture(false)');call('v020GrantWeapon',auto);call('v020Equip',auto);js(D+'.v020Tick(1)');start=state()['player']['ammoClip'];call('v020Hold',True)
  for _ in range(6):js(D+'.v020Tick(.15)')
  call('v020Hold',False);after=state()['player']['ammoClip'];check(after<start-1,'Arme automatique : maintien du tir et cadence effectifs',{'id':auto,'rounds':start-after});js(D+'.v020Tick(1)');check(state()['player']['ammoClip']==after,'Relâchement du tir : plus aucune émission')
  call('v020Hold',True);call('v020Open','interventions');check(js(D+'.getMode()')=='FIELD','L’ouverture d’une interface suspend le tir maintenu');dismiss()
  # Companion LOS and quiet, plus actual collision-aware movement.
  js(D+'.v020Fixture(true)');js(D+'.v020EnemyPatch({alerted:true})');hp=js(D+'.v020Stats().enemy[0].hp');js(D+'.v020Companion("mireille",[0,0,6],2)');check(js(D+'.v020Stats().enemy[0].hp')==hp,'Mireille ne tire pas à travers un mur')
  js(D+'.v020Fixture(false)');js(D+'.v020EnemyPatch({alerted:true})');js(D+'.v020Companion("mireille",[-2,0,6],0);'+D+'.v020Order("fire","quiet")');hp=js(D+'.v020Stats().enemy[0].hp');js(D+'.v020Companion("mireille",null,2)');check(js(D+'.v020Stats().enemy[0].hp')==hp,'Ordre de ne pas engager respecté')
  js(D+'.v020Order("fire","defend");'+D+'.v020Companion("mireille",null,2)');check(js(D+'.v020Stats().enemy[0].hp')<hp,'Riposte défensive sur une menace visible')
  js(D+'.v020Fixture(false,"raider",10)');js(D+'.v020EnemyPatch({alerted:true});'+D+'.v020Companion("roux",[0,0,7],0)');hp=js(D+'.v020Stats().enemy[0].hp');js(D+'.v020Companion("roux",null,.05)');check(js(D+'.v020Stats().enemy[0].hp')==hp,'Roux ne mord pas une cible distante')
  js(D+'.v020Companion("roux",[0,0,-1],0);'+D+'.v020Order("move","hold");'+D+'.v020Companion("roux",null,.05)');check(js(D+'.v020Stats().enemy[0].hp')<hp,'Roux mord une cible atteinte au contact')
  # Real keyboard traversal of the central corridor, not a teleported reachability claim.
  js(D+'.v020Reset()');load('relay_vent');s=state()['player']['pos'];pg.keyboard.down('w')
  for _ in range(30):js(D+'.v020Tick(.05,true)')
  pg.keyboard.up('w');t=state()['player']['pos'];check(3<s[2]-t[2]<3.6 and not call('v020Collides',t),'Le déplacement clavier s’arrête devant la console solide',{'from':s,'to':t})
  pg.keyboard.down('a')
  for _ in range(10):js(D+'.v020Tick(.05,true)')
  pg.keyboard.up('a');pg.keyboard.down('w')
  for _ in range(20):js(D+'.v020Tick(.05,true)')
  pg.keyboard.up('w');t=state()['player']['pos'];check(s[2]-t[2]>6 and not call('v020Collides',t),'Contournement réel au clavier autour de la console',t)
  for op in js(D+'.v020Version().operations'):
   js(D+'.v020Reset()');load(op);pos=next(x['pos'] for x in js(D+'.v020Stats().interactables') if x['id']==op+':part');walk=call('v020WalkQA',pos);check(walk['ok'],op+' : parcours complet automatisé par le contrôleur de mouvement jusqu’au magasin',walk)
  load('relay_vent')
  # Saves, old-field preservation, death guard, door/item persistence.
  approach('relay_vent:station');call('v020Seed',{'cloth':15,'chemicals':8});js(D+'.v020Craft("bandage")');check(js(D+'.save()'),'Sauvegarde contrôlée du nouvel état')
  snapshot=state();key=js(D+'.v018SaveKey()');raw=js('(k)=>localStorage.getItem(k)',key);valid=js('(s)=>__MISTRAL_DEBUG.v018InspectSave(JSON.parse(s))',raw);check(bool(valid),'Export contenant le nouvel intérieur accepté par le validateur')
  js(D+'.v020SetPlayer({hp:0})');check(js(D+'.save()') is False and js('(k)=>localStorage.getItem(k)',key)==raw,'La mort ne remplace pas la dernière sauvegarde vivante')
  js(D+'.v020SetPlayer({hp:100})');migrated=js('(s)=>__MISTRAL_DEBUG.v018Migrate(s)',{**snapshot,'version':'0.18.0','legacyMarker':{'keep':True}});check(migrated['legacyMarker']['keep'] and migrated['v020']['craftCount']==snapshot['v020']['craftCount'],'Migration conserve champs inconnus et nouveau suivi')
  check(js(D+'.v018Keys().campaign')!=js(D+'.v018Keys().sandbox'),'Campagne et bac à sable restent séparés')
  # Holotapes use original timed reader and new five-segment texts.
  load('relay_cold');approach('relay_cold:tape');interact('relay_cold:tape');check(js(D+'.getMode()')=='HOLOTAPE','Holodisque original chargé depuis le nouvel intérieur');check('Sofia' in pg.locator('#holotapeTitle').inner_text(),'Intervenante et bande correctes');js(D+'.v018TapeStep(1)');check(js(D+'.v018TapeState().index')==1,'Changement de segment sous-titré');js(D+'.v018TapeClose()')
  # Structural regression: every historical scene, separately, no claim of campaign completion.
  historical=js(D+'.allZones()');print('allZones shape',str(historical)[:80],flush=True)
  if isinstance(historical,dict):historical=list(historical)
  if historical and isinstance(historical[0],dict):historical=[x['id'] for x in historical]
  historical=[x for x in historical if not x.startswith('relay_') and not x.startswith('geo_') and x not in ['transit_depot','traverse_archives','mooring_station']]
  failed=[];metrics=[]
  for id in historical:
   try:
    load(id);st=js(D+'.v020Stats()');metrics.append({'id':id,'draws':st['draws'],'interactables':len(st['interactables'])})
    if st['id']!=id or st['draws']==0:failed.append(id)
   except Exception as e:failed.append({'id':id,'error':str(e)[:180]})
  check(not failed and len(historical)>=86,'Chargement structurel des 86 instances historiques',{'count':len(historical),'failures':failed})
  (O/'legacy_scene_checks.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
  # Responsive interface with genuine DOM checks, not physical-device claim.
  load('relay_vent');pg.set_viewport_size({'width':390,'height':844});
  for tab in ['interventions','atelier','inventaire','compagnons','halte','plan']:
   call('v020Open',tab);box=pg.locator('#v020Panel').bounding_box();check(box['x']>=0 and box['x']+box['width']<=391 and pg.locator('#v020Close').is_visible(),'Mobile 390×844 : panneau '+tab+' reste dans la fenêtre')
  check(js('document.documentElement.scrollWidth<=innerWidth'),'Aucun débordement horizontal de la page mobile')
  dismiss();pg.set_viewport_size({'width':1440,'height':900})
  check(not errors,'Aucune exception JavaScript dans la suite ciblée',errors)
 except Exception as e:
  check(False,'Exception de la suite',traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  result={'version':'0.22.0','html_sha256':hashlib.sha256(html.encode()).hexdigest(),'scope':{'browser':'Chromium Linux headless / SoftwareRenderer','load':'exact HTML via set_content; file navigation blocked by unchanged administrator policy','storage':'initial actual refusal tested, then explicit in-memory adapter; restart persistence not certified','graphics':'software renderer; no hardware GPU or physical mobile certification','campaign':'86 historical scene loads plus targeted new interventions, not a full campaign traversal','geography':'no official tiles or DEM acquired'},'total':len(rows),'passed':sum(x['ok'] for x in rows),'failed':sum(not x['ok'] for x in rows),'errors':errors,'results':rows}
  (O/'QA_REGRESSION_V020_ON_V022.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));b.close();print('RESULT',result['passed'],result['failed'],flush=True)
raise SystemExit(bool(result['failed']))
