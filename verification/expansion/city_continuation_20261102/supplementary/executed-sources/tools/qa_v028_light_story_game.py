#!/usr/bin/env python3
"""Light, authored quest and six games. Authentic rendered frames and clicks;
state setup, camera positions and synthetic occlusion arena explicitly marked."""
from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops,ImageStat
import hashlib,json,traceback,math
R=Path(__file__).resolve().parents[1];O=R/'verification';H=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();checks=[];errors=[]
def check(ok,name,detail=None):checks.append(dict(ok=bool(ok),name=name,detail=detail));print(('OK 'if ok else 'FAIL ')+name,flush=True)
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.set_default_timeout(8000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV028').wait_for(timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def st():return c('v028State')
 def q():return c('v028Quest')
 def dismiss():
  if p.locator('#pipboy').is_visible():c('closePip')
  c('v020ModalDismiss')
 def op(tab='radio',sub='games'):return c('v027Open',tab,sub)
 def near(id):return c('v020Approach',id)
 def click(a,arg=None):
  sel='[data-p27="p28:'+a+'"]'+(''if arg is None else '[data-arg="'+str(arg)+'"]');p.locator(sel).filter(visible=True).first.click()
 def choice(text):p.locator('#dialogueChoices button').filter(has_text=text).first.click()
 def load(z='relay_cold',mute=True):
  dismiss();c('v020Load',z);c('v022ResetRuntime');c('v022Time',10)
  if mute:c('v021MuteEnemies')
 def reset():
  dismiss();c('v020Reset');load();c('v028Settings',{'survivalNeeds':False});c('v026Carry',False)
 def unlock():
  load();near('v028:game');c('v020Interact','v028:game');dismiss();op()
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v020Load','relay_cold');check(c('save') is False,'Stockage natif opaque refuse l’écriture avant adaptateur')
  p.evaluate("window.__STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__STORE[k]??null,setItem:(k,v)=>__STORE[k]=String(v),removeItem:k=>delete __STORE[k]}})")
  reset();check(not st()['lamp'],'La lampe est éteinte au départ')
  p.keyboard.press('l');check(st()['lamp'],'L allume réellement la lampe')
  p.keyboard.press('l');check(not st()['lamp'],'L éteint réellement la lampe')
  op('status','health');click('lamp');check(st()['lamp'],'Bouton Pip-Boy et raccourci partagent le même état')
  c('v027Set','inventory','weapon');p.locator('#p27Search').fill('l');p.keyboard.press('l');check(st()['lamp'],'Écrire L dans la recherche ne modifie pas l’éclairage')
  dismiss();near('v028:medic');c('v028Sofia');p.keyboard.press('l');check(st()['lamp'],'Dialogue ne prend pas le raccourci de lampe');dismiss()
  # Actual software renderer before/after with identical eye point.
  c('v028Set',{'lamp':False});camera=[-10,1.65,1];c('v028Render',camera,0,-.01);p.evaluate("document.getElementById('toastStack').innerHTML=''");p.screenshot(path=str(O/'QA_V028_LAMP_OFF.png'))
  baseDraws=c('v020Stats')['draws'];c('v028LampToggle');render=c('v028Render',camera,0,-.01);p.screenshot(path=str(O/'QA_V028_LAMP_ON.png'))
  check(render['renderer']=='software' and render['faces']>30,'Lampe : surfaces de la scène réellement éclairées par le moteur logiciel',render)
  check(c('v020Stats')['draws']==baseDraws,'Échantillonnage de lumière ne modifie pas les décors persistants')
  a=Image.open(O/'QA_V028_LAMP_OFF.png').convert('RGB');z=Image.open(O/'QA_V028_LAMP_ON.png').convert('RGB');area=(120,220,1320,720);dif=ImageChops.difference(a.crop(area),z.crop(area));change=sum(ImageStat.Stat(dif).mean)/3
  check(change>2,'Comparaison des pixels de la scène, hors HUD : éclairage visible',{'mean_abs_change':change})
  stats=c('v028LightStats');check(stats['samples']<=6000,'Cache d’occultation borné pendant le rendu')
  for _ in range(3):c('v028Render',camera,0,-.01)
  check(c('v020Stats')['draws']==baseDraws,'Plusieurs images ne dupliquent pas les maillages de sol')
  # Pure physical samples tested in the same lighting code, not a fake image.
  c('v020Fixture',False);c('v028Set',{'lamp':True});nearLight=c('v028LightPoint',[0,0,5],[0,1,0]);far=c('v028LightPoint',[0,0,-9],[0,1,0]);behind=c('v028LightPoint',[0,0,1],[0,1,0])
  check(nearLight>0 and far==0 and behind>0,'Éclairement local limité au rayon de onze mètres')
  c('v020AddWall');check(c('v028LightPoint',[0,0,1],[0,1,0])==0,'Un mur bloque l’échantillon de lumière placé derrière lui')
  c('v028Set',{'lamp':False});check(c('v028LightPoint',[0,0,5],[0,1,0])==0,'Lampe éteinte ne laisse pas un éclairement résiduel')
  c('v020Fixture',False);c('v020EnemyPatch',{'damage':5,'detect':0,'alerted':False});c('v028Set',{'lamp':False});c('v028AI',.01);check(not c('v020Stats')['enemy'][0]['alerted'],'Sans lampe, la menace du contrôle à portée de détection nulle ne repère pas le joueur')
  c('v028Set',{'lamp':True});c('v028AI',.01);check(c('v020Stats')['enemy'][0]['alerted'],'Lampe visible à courte distance : adversaire alerté')
  c('v020Fixture',True);c('v020EnemyPatch',{'damage':5,'detect':0,'alerted':False});c('v028Set',{'lamp':True});c('v028AI',.01);check(not c('v020Stats')['enemy'][0]['alerted'],'Lampe derrière un mur ne déclenche pas la détection supplémentaire')
  c('v020Fixture',False,'raider',18);c('v020EnemyPatch',{'damage':5,'detect':0,'alerted':False});c('v028AI',.01);check(not c('v020Stats')['enemy'][0]['alerted'],'Lampe ne signale pas automatiquement les ennemis au-delà de douze mètres')
  # Original optional quest, physical evidence and original cold-chain preserved.
  reset();original=s()['v020']['operations']['relay_cold'];check(not c('v028Resolve','repair'),'Impossible de résoudre la veille avant son diagnostic')
  near('v028:switch');check(not c('v028Isolate'),'Interrupteur non identifié : aucune consignation aveugle')
  near('v028:medic');c('v020Interact','v028:medic');choice('Pourquoi la pharmacie');choice('Je vais examiner');dismiss();check(q()['accepted'] and q()['tracked'],'Acceptation par les répliques réelles de Sofia')
  op('data','quests');check(any(x['id']=='nightcare' for x in c('v027QuestRows')),'Quête locale enregistrée dans DATA')
  dismiss();load('traverse_archives');c('v020SetPlayer',{'pos':[-17,1.65,-18]});check(not c('v028ReadPlan'),'Preuve à l’étage non lisible à travers le plancher')
  load('traverse_archives');walk=c('v021ActualWalk',[-17,3.2,-16.5]);check(walk['ok'] and walk['maxY']>4.7,'Montée réelle au contrôleur vers le plan dans la galerie',walk)
  check(c('v028ReadPlan') and q()['plan'],'Plan pris à portée après le parcours, pas depuis l’interface')
  check('v028-plan' in s()['v027']['documents'],'Le document intégral rejoint les archives du Pip-Boy')
  load();near('v028:switch');check(c('v028Isolate') and q()['isolated'],'Consignation physique de L-4 après identification')
  before=s()['inventory'];check(not c('v028Isolate') and s()['inventory']==before,'Consignation non répétable et sans prélèvement caché')
  check(s()['v020']['operations']['relay_cold']==original,'Ancienne chaîne du froid non résolue ou modifiée par L-4')
  near('v028:medic');c('v028Options');check(p.locator('#dialogueChoices button').count()==3,'Deux solutions et option de report affichées')
  c('v020Seed',{'scrap':0,'circuitry':0});before=s();choice('Remettre la veille');choice('Confirmer');check(q()['ending'] is None and s()['inventory']==before['inventory'],'Refus du manque de matériaux sans débit partiel')
  c('v020Seed',{'scrap':10,'circuitry':10});before=s();c('v028Preview','repair');choice('Confirmer');after=s()
  check(q()['ending']=='repair' and q()['rewarded'],'Accord fixe réellement validé')
  check(after['inventory']['scrap']==before['inventory']['scrap']-3 and after['inventory']['circuitry']==before['inventory']['circuitry']-2,'Débit exact de trois ferrailles et deux circuits')
  check(after['player']['caps']==before['player']['caps']+50 and after['player']['xp']==before['player']['xp']+60,'Récompense unique : cinquante capsules, soixante XP')
  check(after['inventory'].get('traumaKit',0)==before['inventory'].get('traumaKit',0)+1,'Solution fixe : une trousse réellement remise')
  check(c('v028AmbientAt',[-10,0,-5])==1,'Solution fixe restaure réellement l’éclairage de la pharmacie')
  first=p.locator('#dialogueLine').inner_text();p.locator('#dialogueChoices button').first.click();second=p.locator('#dialogueLine').inner_text();check(first!=second and len(first)>100 and len(second)>100,'Deux scènes distinctes de l’épilogue fixe');dismiss();before=s();c('v028Epilogue',0);check(s()['player']==before['player'] and s()['inventory']==before['inventory'],'Relecture sans ressources recréées');dismiss();check(not c('v028Resolve','manual'),'Une seconde conclusion ne remplace pas l’accord fixé')
  raw=s();c('v018ImportRaw',json.dumps(raw));check(q()['ending']=='repair' and c('v028AmbientAt',[-10,0,-5])==1,'Accord et éclairage conservés après import complet')
  # Second outcome by a fresh accepted quest and physical documents, not state grant.
  reset();near('v028:medic');c('v028QuestTalk');choice('Je vais examiner');dismiss();load('traverse_archives');near('v028:plan');c('v028ReadPlan');dismiss();load();near('v028:switch');c('v028Isolate');near('v028:medic');c('v028Options');before=s();choice('Garder un éclairage');choice('Confirmer');after=s()
  check(q()['ending']=='manual' and after['inventory'].get('fieldSplint',0)==before['inventory'].get('fieldSplint',0)+2,'Solution mobile : deux attelles effectivement remises')
  check(after['inventory']['scrap']==before['inventory']['scrap'] and after['inventory']['circuitry']==before['inventory']['circuitry'],'Solution mobile ne consomme pas de composants')
  check(c('v028AmbientAt',[-10,0,-5])<.3,'Solution mobile ne prétend pas réparer le poste fixe')
  first=p.locator('#dialogueLine').inner_text();p.locator('#dialogueChoices button').first.click();second=p.locator('#dialogueLine').inner_text();check(first!=second and len(first)>100,'Deux scènes propres à la solution mobile');dismiss()
  # Games: acquired physically, solved with native pointer clicks, no economy reward.
  reset();op();check('Trouvez la cassette' in p.locator('#pipContent').inner_text(),'Jeu inconnu non distribué à la migration')
  check(not c('v028GameAction','rotate','11'),'Pas de rotation tant que la cassette n’est pas trouvée')
  dismiss();check(not c('v028PickupGame'),'Bande non récupérable à distance')
  near('v028:game');c('v020Interact','v028:game');check(st()['game']['unlocked'] and s()['lore']['holotapes'].get('v028_night'),'Cassette physique débloque le jeu et la bande sous-titrée')
  dismiss();op();check(p.locator('.p28-tile').count()==25,'Grille réelle de vingt-cinq cellules')
  before=s();flow=c('v028Circuit');check(not flow['success'],'Le premier circuit ne démarre pas gagné')
  for level in range(6):
   if level:click('level',str(level))
   board=c('v028Board',level);g=c('v028GameState',level);before_moves=g['moves'];start=board['start'];end=board['end'];check(not c('v028GameAction','rotate',str(start)) and not c('v028GameAction','rotate',str(end)),'Circuit '+str(level+1)+' : deux bornes fixes non tournables')
   blank=next(i for i,x in enumerate(board['masks'])if not x);check(not c('v028GameAction','rotate',str(blank)),'Circuit '+str(level+1)+' : isolant non cliquable')
   turns=g['turns'];checks_before=len(checks)
   # The solved orientation is zero modulo four, with 180-degree equivalence for straight pipes.
   for cell in board['path'][1:-1]:
    for j in range((4-turns[cell])%4):click('rotate',str(cell))
   flow=c('v028Circuit',level);g=c('v028GameState',level)
   check(flow['success'] and not flow['leaks'],'Circuit '+str(level+1)+' : sortie réellement alimentée après rotations au clic')
   check(g['won'] and g['best'] is not None and g['moves']>=before_moves,'Circuit '+str(level+1)+' : meilleur score persistant')
   check('SORTIE ALIMENTÉE' in p.locator('.p28-verdict').inner_text(),'Circuit '+str(level+1)+' : réussite reflétée dans la grille')
  after=s();check(after['player']['caps']==before['player']['caps'] and after['player']['xp']==before['player']['xp'] and after['inventory']==before['inventory'],'Six circuits terminés : zéro capsule, XP ou butin ajouté')
  old=c('v028GameState');p.once('dialog',lambda d:d.dismiss());click('reset');check(c('v028GameState')==old,'Refus de réinitialisation conserve la disposition')
  p.once('dialog',lambda d:d.accept());click('reset');g=c('v028GameState');check(g['best']==old['best'] and g['moves']==0 and not c('v028Circuit')['success'],'Recommencer conserve le record mais rétablit la panne')
  before=g['turns'];click('hint');check(c('v028GameState')['turns']==before and 'Vérifiez la case' in p.locator('#pipContent').inner_text(),'Indice indique une case sans la tourner ni offrir de solution')
  raw=s();moves=c('v028GameState')['moves'];cell=c('v028Board')['path'][3];click('rotate',str(cell));check(c('v028GameState')['moves']==moves+1,'Une rotation reste une seule action')
  c('v018ImportRaw',json.dumps(raw));op();click('level','0');click('level','5');check(c('v028GameState')['turns']==before,'Import retrouve les orientations du circuit en cours')
  check(not c('v028GameAction','level','88') and not c('v028GameAction','rotate','-1'),'Niveau et cellule invalides refusés')
  c('v027Set','inventory','aid');check(not c('v028GameAction','rotate',str(cell)),'Ancienne commande de jeu refusée dans une autre rubrique')
  # True touch context, same HTML and declared storage, no iPhone certification.
  mobile=b.new_context(viewport={'width':390,'height':844},has_touch=True);m=mobile.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(H);m.locator('#btnV028').wait_for(timeout=30000)
  def mc(n,*a):return m.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
  mc('setRenderPaused',True);mc('v022Freeze',True);mc('v018NoNetwork',True);m.evaluate("window.__S={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__S[k]??null,setItem:(k,v)=>__S[k]=String(v),removeItem:k=>delete __S[k]}})")
  mc('v020Reset');mc('v020Load','relay_cold');mc('v021MuteEnemies');mc('v020Approach','v028:game');mc('v028PickupGame');mc('v020ModalDismiss');mc('v027Open','radio','games');board=mc('v028Board');cell=board['path'][1];n=mc('v028GameState')['moves'];tile=m.locator('[data-p27="p28:rotate"][data-arg="'+str(cell)+'"]');tile.scroll_into_view_if_needed();box=tile.bounding_box();m.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
  check(mc('v028GameState')['moves']==n+1,'Tactile simulé 390×844 : rotation sur la vraie grille')
  check(m.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Jeu intégré sans débordement horizontal mobile')
  mc('closePip');mc('v028Render',[-10,1.65,1],0,-.01);lamp=m.locator('#p28LampHud');box=lamp.bounding_box();m.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2);check(mc('v028State')['lamp'],'Bouton HUD de lampe actionnable au toucher')
  mobile.close()
 except Exception:check(False,'Exception de la suite',traceback.format_exc());p.screenshot(path=str(O/'QA_V028_LIGHT_STORY_GAME_FAILURE.png'))
 check(not errors,'Aucune exception JavaScript de la suite',errors);b.close()
r=dict(html_sha256=hashlib.sha256(H.encode()).hexdigest(),passed=sum(x['ok']for x in checks),failed=sum(not x['ok']for x in checks),checks=checks,errors=errors,scope='Exact HTML Chromium logiciel. Caméras/états et occlusion synthétiques déclarés ; pixels réels de lumière, parcours contrôleur vers preuve, 6 puzzles par clic. Stockage mémoire après refus natif opaque, mobile tactile simulé.');(O/'QA_V028_LIGHT_STORY_GAME.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('TOTAL',r['passed'],r['failed']);raise SystemExit(bool(r['failed']))
