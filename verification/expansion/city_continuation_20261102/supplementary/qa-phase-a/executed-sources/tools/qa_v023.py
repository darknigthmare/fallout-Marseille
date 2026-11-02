"""Exact HTML through set_content (file: blocked by managed browser).
Native opaque-origin write failure is checked before an explicit in-memory adapter.
Combat fixtures are synthetic tests, not geographical imports. Story tests use real UI
choices; reachability is additionally tested with the player controller.
"""
from pathlib import Path
from qa_support import chromium_path
import json,hashlib,traceback,math
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';html=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[]
def ck(ok,title,detail=None):
 rows.append({'ok':bool(ok),'name':title,'detail':detail});print('OK' if ok else 'FAIL',title,str(detail)[:300] if detail is not None else '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(7000);p.set_content(html,wait_until='load');p.locator('#btnV023').wait_for(state='visible',timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def d():c('v020ModalDismiss')
 def reset():d();c('v020Reset');c('v022ResetRuntime')
 def load(z):d();c('v020Load',z);c('v021MuteEnemies');c('v022ResetRuntime')
 def near(i):return c('v020Approach',i)
 def click(text):p.locator('#dialogueChoices button').filter(has_text=text).first.click()
 def prime():load('transit_depot');near('v023:lise');c('v023Topic','lise');click('suivre la transformation');d()
 def evidence(k):
  z=c('v023Defs')[k]['zone'];load(z);near('v023:proof:'+k);r=c('v023Collect',k);d();return r
 def witness(k):
  load('traverse_archives' if k=='diane' else 'mooring_station');near('v022:'+k+':talk');c('v023Topic',k);click('extrait consenti' if k=='diane' else 'protocole décrit');d()
 def prep_all():
  prime()
  for k in ['manifest','register','protocol']:evidence(k)
  witness('diane');witness('rayan')
  near('v023:diagnostic');c('v023Diagnose');d();load('transit_depot');near('v023:lise')
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  ck(c('v025Info')['version']=='0.30.0','Version et nouveau bouton du HTML final')
  load('transit_depot');ck(c('save') is False,'Refus natif du stockage sur origine opaque explicitement détecté')
  p.evaluate("window.__store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}})")
  ck(c('save') is True,'Sauvegarde fonctionnelle avec adaptateur mémoire déclaré')
  ck(c('v018Keys')['campaign']=='fallout_mistral_save_v030' and c('v018Keys')['sandbox']=='fallout_mistral_sandbox_v030','Clés campagne / exploration séparées v023')
  reset();load('vault');ck(near('v023:goat') is not None,'Borne G.O.A.T. physiquement accessible dans A-03');ck(c('v023OpenGoat'),'Examen ouvert depuis A-03');base=s()['character']['special'].copy();xp=s()['player'].get('xp');
  for i in range(3):p.locator('[data-v23="answer|0"]').click()
  ck(len(s()['v023']['goat']['answers'])==3,'Trois réponses enregistrées par vrais clics');d();ck(c('v023OpenGoat') and c('v023DialogMeta')['goatPage']==3,'Reprise à la quatrième question après fermeture')
  p.locator('[data-v23="back"]').click();p.locator('[data-v23="answer|1"]').click();ck(s()['v023']['goat']['answers'][2]==1 and len(s()['v023']['goat']['answers'])==3,'Retour modifie la réponse, sans accumuler de points')
  for i in range(3,10):p.locator('[data-v23="answer|'+str(i%4)+'"]').click()
  ck(sum(c('v023GoatScores').values())==40,'Scores recalculés : dix réponses, quarante points au total')
  ck(c('v023DialogMeta')['goatPage']==10,'Écran de proposition après dix questions');d();c('v023OpenGoat');ck(c('v023DialogMeta')['goatPage']==10,'Reprise du résultat inachevé, sans repasser les dix questions')
  for k in c('v023Recommended'):p.locator('[data-v23="tag|'+k+'"]').click()
  ck(p.locator('[data-v23="confirm-goat"]').is_disabled(),'Confirmation bloquée tant que trois spécialités ne sont pas retenues')
  for k in ['repair','medicine','speech']:p.locator('[data-v23="tag|'+k+'"]').click()
  p.locator('[data-v23="confirm-goat"]').click();ck(s()['v023']['goat']['completed'] and s()['v023']['goat']['tags']==['repair','medicine','speech'],'Trois spécialités personnalisées, pas seulement la proposition')
  ck(s()['character']['special']==base and s()['player'].get('xp')==xp,'Aucun changement S.P.E.C.I.A.L. ni XP à la validation')
  ck(c('v023Skills')['repair']==40 and c('v023Skills')['guns']==25,'Bonus +15 limité aux trois compétences choisies')
  ck(not c('v023ConfirmGoat'),'Répéter une validation ne cumule aucun bonus')
  c('v020SetPlayer',{'hp':20,'maxHp':200});c('v020Seed',{'stimpak':3});d();c('v023Heal');ck(s()['player']['hp']==83 and s()['inventory']['stimpak']==2,'Spécialité Médecine : soin direct 55 + 8, un seul Stimpak')
  c('v020SetPlayer',{'hp':20});c('v023UseItem','stimpak');ck(s()['player']['hp']==83 and s()['inventory']['stimpak']==1,'Même bonus via inventaire et consommation unique')
  snap=s();old=json.loads(json.dumps(snap));old.pop('v023');old['version']='0.22.0';old['future_marker']={'keep':True};mig=c('v018Migrate',old);ck(mig['future_marker']['keep'] and mig['v022']==old['v022'] and not mig['v023']['goat']['completed'],'Migration v022 préserve l’ancien retour et les champs inconnus')
  invalid={**snap,'v023':{'critical':-400,'goat':{'tags':['repair','repair','ghost'],'completed':True},'quest':{'ending':'invalid'}}};m=c('v018Migrate',invalid);ck(m['v023']['critical']==0 and not m['v023']['goat']['completed'] and m['v023']['quest']['ending'] is None,'Normalisation des doublons, tags inconnus, critique et conclusion invalide')
  reset();load('transit_depot');near('v023:goat');c('v023OpenGoat',True);c('v023Draft',['guns','science','melee']);ck(c('v023ConfirmGoat') and s()['v023']['goat']['method']=='manual','Choix direct équivalent, sans questionnaire obligatoire')
  damage_tag=c('v020Damage','pistol10');c('v023Set',{'goat':{'completed':False,'tags':[],'answers':[],'method':None}});damage_base=c('v020Damage','pistol10');ck(abs(damage_tag/damage_base-1.06)<.0001,'Spécialité Balistique : +6 % dans le calcul de combat commun')
  # Real reachability to the three upper-level evidence positions, not teleport-only claims.
  for k,definition in c('v023Defs').items():
   reset();load(definition['zone']);stats=c('v020Stats');it=next(i for i in stats['interactables'] if i['id']=='v023:proof:'+k);target=[it['pos'][0],3.2,it['pos'][2]+1.4];walk=c('v021ActualWalk',target);ck(walk['ok'] and walk['maxY']>4.7,k+' : montée par le contrôleur jusqu’à la preuve',walk)
   ck(near('v023:proof:'+k) is not None,k+' : point d’interaction visible et accessible')
  reset();prime();ck(s()['v023']['quest']['accepted'],'Nouvelle enquête acceptée par le dialogue de Lise')
  ck(not c('v023Resolve','appeal'),'Résolution prématurée refusée');ck(not c('v023Collect','protocol'),'Collecte distante dans un autre lieu refusée')
  near('v023:lise');c('v023Topic','lise');click('sans poser de questions');ck(s()['v023']['quest']['trust']==-1,'Affirmation non étayée affecte la confiance, sans bloquer l’enquête');d();near('v023:lise');c('v023Topic','lise');click('sans poser de questions');ck(s()['v023']['quest']['trust']==-1,'Même provocation ne cumule pas les pénalités');d()
  evidence('manifest');near('v023:lise');c('v023Topic','lise');click('Voici les deux versions');ck(s()['v023']['quest']['trust']==1,'La preuve ouvre un rattrapage après le bluff');d()
  load('mooring_station');near('v023:diagnostic');ck(not c('v023Diagnose') and s()['v023']['checks']['diagnosticFailed'],'Diagnostic sans compétence ni protocole échoue sans bloquer la suite');d();evidence('protocol');near('v023:diagnostic');ck(c('v023Diagnose'),'Même diagnostic réussi après lecture du protocole');d()
  # Three fully separate resolutions, each exact-once and with prior choices preserved.
  for ending in ['appeal','network','contract']:
   reset();c('v021Scenario',{'ending':'silence'});c('v022Task',{'ending':'road','consent':'sealed'});prep_all();q=s();caps=q['player']['caps'];stock=q['inventory'].copy();c('v023Hearing');ck(p.locator('#dialogueChoices button.locked').count()==0,ending+' : dossier complet ouvre les trois résolutions')
   c('v023Preview',ending);ck(not s()['v023']['quest']['ending'],ending+' : aperçu sans engagement');click('Revenir aux autres');ck(not s()['v023']['quest']['ending'],ending+' : retour à la discussion sans modifier les réserves')
   c('v023Preview',ending);click('Confirmer');ck(s()['v023']['quest']['ending']==ending and s()['player']['caps']==caps+90,ending+' : confirmation persistante et 90 capsules une seule fois')
   texts=[]
   for i in range(3):texts.append(p.locator('#dialogueLine').inner_text());p.locator('#dialogueChoices button').first.click()
   ck(len(set(texts))==3 and all(len(x)>170 for x in texts),ending+' : trois scènes de conclusion distinctes')
   ck('restent éteints' in texts[2] and s()['v022']['task']['consent']=='sealed' and s()['v021']['ending']=='silence',ending+' : décisions du canal et confidentialité conservées')
   near('v023:lise');ck(not c('v023Resolve',ending) and s()['player']['caps']==caps+90,ending+' : résolution répétée refusée')
   for z in ['transit_depot','traverse_archives','mooring_station']:
    load(z);props=c('v023Scene')['props'];ck(any(x['id'].startswith('v023:after') and not x['hidden'] for x in props),ending+' / '+z+' : tableau et lumière de formation réellement visibles')
    near('v023:delivery');ck(c('v023Delivery'),ending+' / '+z+' : livraison physique obtenue');bag=s()['inventory'];ck(not c('v023Delivery') and s()['inventory']==bag,ending+' / '+z+' : aucun doublon de livraison')
    ck(all(x['hidden'] for x in c('v023Scene')['props'] if x['id'].startswith('v023:supply')),ending+' / '+z+' : caisse retirée visuellement après collecte')
   ck(all(s()['v023']['quest']['deliveries'].values()),ending+' : les trois livraisons sont mémorisées')
  # Alternate low-skill solution does not require finishing the GOAT or all evidence.
  reset();prime();evidence('manifest');evidence('protocol');witness('rayan');load('transit_depot');near('v023:lise');ck(c('v023Resolve','network') and not s()['v023']['goat']['completed'],'Voie sans aucun G.O.A.T., avec seulement deux preuves et Rayan');d()
  discounted=c('v023Price','food',True,'noailles');sell=c('v023Price','food',False,'noailles');outside=c('v023Price','food',True,'belsunce');c('v023SetQuest',{'ending':None});normal=c('v023Price','food',True,'noailles');ck(discounted==max(1,math.floor(normal*.95)) and sell==c('v023Price','food',False,'noailles') and outside==c('v023Price','food',True,'belsunce'),'Conséquence commerciale ciblée : achat essentiels seulement, pas revente ni autre marchand')
  # Shared dialogue validation and literal text rendering.
  load('transit_depot');c('v023SetQuest',{'accepted':True});c('v023TestDialog');c('v023SetQuest',{'accepted':False});p.locator('#dialogueChoices button').first.click();ck(not s()['v023']['checks'].get('testExecuted'),'Condition revalidée au clic après changement d’état')
  c('v023SetQuest',{'accepted':True});c('v023TestDialog');p.evaluate("window.__oldChoice=document.querySelector('#dialogueChoices button')");d();near('v023:lise');c('v023Topic','lise');p.evaluate('__oldChoice.click()');ck(not s()['v023']['checks'].get('testExecuted'),'Bouton détaché d’un ancien dialogue ne peut plus agir')
  count=len(s()['v023']['history']);p.keyboard.press('h');ck(p.locator('#v023History').is_visible(),'H ouvre l’historique sans fermer le dialogue');p.keyboard.press('Escape');ck(not p.locator('#v023History').is_visible() and c('getMode')=='DIALOGUE','Échap revient à la conversation exacte');ck(len(s()['v023']['history'])==count,'Consultation de l’historique ne duplique pas les répliques');d()
  # V.A.T.S. transaction and guaranteed critical restricted by geometry.
  reset();c('v020Fixture',False);c('v020Tick',1);c('v020Vats');c('v023Select',0,'body');before=s()['player'];ck(not c('v023Queue',True),'Critique refusé avec jauge vide');c('v023Crit',100);ck(c('v023Queue',True),'Critique réservé avec jauge pleine');ck(not c('v023Queue',True),'Deux réservations d’un même critique interdites');ck(s()['v023']['critical']==100 and s()['player']['ap']==before['ap'] and s()['player']['ammoClip']==before['ammoClip'],'Préparation sans débit PA, munitions ni jauge');c('v020VatsCancel');ck(s()['v023']['critical']==100,'Annulation conserve la réserve critique')
  c('v020Vats');c('v023Select',0,'body');c('v023Queue',True);c('v020VatsExecute');hp=c('v020Stats')['enemy'][0]['hp'];c('v020RandomTick',.1,.999);after=s()['player'];ck(c('v020Stats')['enemy'][0]['hp']<hp and s()['v023']['critical']==0,'Critique valide touche même avec jet 0,999 puis vide la réserve');ck(after['ap']==before['ap']-25 and after['ammoClip']==before['ammoClip']-1,'Critique débite exactement une action émise');c('v020VatsCancel')
  reset();c('v020Fixture',False);c('v023Crit',100);c('v020Vats');c('v023Select',0,'body');c('v023Queue',True);res=s()['player'];c('v020AddWall');c('v020VatsExecute');c('v020RandomTick',.1,.5);ck(s()['player']['ammoClip']==res['ammoClip'] and s()['player']['ap']==res['ap'] and s()['v023']['critical']==100,'Mur ajouté après sélection : aucun tir, aucun coût, critique conservé');c('v020VatsCancel')
  reset();c('v020Fixture',False);c('v023EnemyAdd');c('v020SetPlayer',{'ap':200,'maxAp':200});c('v023Crit',100);c('v020Vats');c('v023Select',0,'body');c('v023Queue');c('v023Select',1,'head');c('v023Queue',True);ck(len(c('v023QueueInfo'))==2 and c('v023EditQueue',1,-1),'Deux cibles et réorganisation de la file');ck(c('v023QueueInfo')[0]['critical'],'Action critique effectivement remontée');ck(c('v023EditQueue',1,0) and len(c('v023QueueInfo'))==1,'Retrait individuel actualise la file');c('v020VatsCancel')
  reset();c('v020Fixture',False);c('v020SetPlayer',{'ap':200,'maxAp':200});c('v020Vats');c('v023Select',0,'body');
  for _ in range(6):c('v023Queue')
  ck(len(c('v023QueueInfo'))==6 and not c('v023Queue'),'Six actions maximum, sans inflation silencieuse');c('v020VatsExecute')
  for _ in range(32):c('v020RandomTick',.1,.5)
  ck(s()['v023']['critical']==100,'Six impacts V.A.T.S. normaux remplissent la réserve, plafonnée à 100')
  # Serialization and separate migration from the previous sandbox key.
  d();load('transit_depot');c('v023SetQuest',{'accepted':True,'trust':1});snap=s();raw=c('v023SnapshotState');c('v020Reset');c('v023Restore',raw);ck(s()['v023']==json.loads(raw)['v023'],'Sérialisation du dossier, de la jauge, des échanges et aptitudes')
  old=json.loads(raw);old.pop('v023');old['version']='0.22.0';p.evaluate('(s)=>localStorage.setItem("fallout_mistral_sandbox_v022",s)',json.dumps(old));p.evaluate('localStorage.removeItem("fallout_mistral_sandbox_v026")');ck(c('v023ResumeSandbox') and c('v018SaveKey')=='fallout_mistral_sandbox_v030','Reprise d’une exploration v022 vers sa clé v023 distincte');ck(p.evaluate('localStorage.getItem("fallout_mistral_sandbox_v022")')==json.dumps(old),'Ancienne exploration v022 conservée intacte')
  # Narrow viewports: real buttons and no horizontal spill.
  p.set_viewport_size({'width':390,'height':844});reset();load('transit_depot');near('v023:goat');c('v023OpenGoat')
  for panel in ['goat','aptitudes','dossier','dialogues','consequences']:
   c('v023Open',panel);ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth') and p.locator('#v020Close').is_visible(),panel+' : panneau 390×844 sans débordement et fermeture accessible')
  d();c('v020Fixture',False);c('v023Crit',100);c('v020Vats');ck(p.locator('[data-v23="vats-critical"]').is_enabled(),'Commande critique tactile présente');p.locator('[data-v23="vats-critical"]').click();ck(len(c('v023QueueInfo'))==1,'Ajout critique au clic dans une fenêtre mobile');ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'V.A.T.S. mobile sans débordement horizontal');p.locator('[data-v23="vats-close"]').click();ck(c('getMode')=='PLAYING','Annulation V.A.T.S. par bouton tactile')
  ck(not errors,'Aucune exception JavaScript dans la suite',errors)
 except Exception:
  ck(False,'Exception de la suite',traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  result={'version':'0.23.0','html_sha256':hashlib.sha256(html.encode()).hexdigest(),'total':len(rows),'passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'errors':errors,'scope':'Exact HTML via set_content; managed file navigation denied; software Chromium; native opaque-origin write failure then explicit memory store; no geographic data; choices clicked; controller walk tests separate from injected approaches.','results':rows};(O/'QA_V023.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('RESULT',result['passed'],result['failed'],flush=True);b.close()
raise SystemExit(bool(result['failed']))
