#!/usr/bin/env python3
"""Focused VATS tests: same rendered rigs and camera as gameplay.
HTML exact via set_content, real DOM clicks/keys; synthetic arenas explicitly
used for repeatable occlusion/combat checks, not as geographic evidence.
"""
from pathlib import Path
import hashlib,json,math,traceback,os
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
URL=os.environ.get('MISTRAL_TEST_URL','http://127.0.0.1:8765/JOUER_FALLOUT_MISTRAL_v0.30.html');rows=[];errors=[]
def ck(ok,name,detail=None):
 rows.append(dict(ok=bool(ok),name=name,detail=detail));print('OK' if ok else 'FAIL',name,str(detail)[:220] if detail is not None else '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.set_default_timeout(6000);p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text(),wait_until='load');p.locator('#btnV025').wait_for(timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def snap():return c('v025Snapshot')
 def reset(kind='raider',distance=7):
  c('v020VatsCancel');c('v020Reset');c('v020Fixture',False,kind,distance);c('v020EnemyPatch',{'yaw':math.pi});c('v020Tick',1);c('v022Freeze',True)
 def openv():
  c('v020Vats');c('v025Paint');return snap()
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  ck(c('v025Info')['version']=='0.30.0','Version effective 0.25')
  ck(p.evaluate("(()=>{try{localStorage.setItem('v025_native_probe','ok');return false}catch(e){return true}})()"),'Refus natif du stockage sur origine opaque constaté')
  p.evaluate("window.__v25Store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__v25Store[k]??null,setItem:(k,v)=>__v25Store[k]=String(v),removeItem:k=>delete __v25Store[k]}})")
  ck(p.evaluate("localStorage.setItem('v025_adapter_probe','ok');localStorage.getItem('v025_adapter_probe')")=='ok','Adaptateur mémoire explicite pour les scénarios de réussite')
  ck(p.locator('#btnV025').is_visible(),'Menu de prise en main disponible')
  # Cancel startup must leave saves intact.
  p.evaluate("localStorage.setItem('fallout_mistral_save_v026','campaign-sentinel');localStorage.setItem('fallout_mistral_sandbox_v024','old-sentinel')")
  p.once('dialog',lambda d:d.dismiss());p.locator('#btnV025').click();ck(c('getMode')=='MENU','Annuler la confirmation ne démarre pas le scénario')
  p.once('dialog',lambda d:d.accept());p.locator('#btnV025').click();c('v025Paint');ck(c('getMode')=='VATS' and s()['player']['zone']=='transit_depot','Menu démarre le V.A.T.S. contre un ennemi du dépôt')
  ck(p.evaluate("localStorage.getItem('fallout_mistral_save_v026')")=='campaign-sentinel','Campagne préservée par la prise en main')
  ck(p.evaluate("localStorage.getItem('fallout_mistral_sandbox_v024')")=='old-sentinel','Ancienne exploration v0.24 intacte')
  p.evaluate("localStorage.removeItem('fallout_mistral_save_v026');localStorage.removeItem('fallout_mistral_sandbox_v024')")
  reset();before=s()['player'];a=openv();ck(a['camera']['pos']==before['pos'],'Caméra de ciblage conserve exactement l’origine des yeux')
  ck(s()['player']['pos']==before['pos'] and s()['player']['yaw']==before['yaw'] and s()['player']['pitch']==before['pitch'],'Cadrage sans déplacement ni rotation du personnage enregistré')
  ck(p.locator('.v24-silhouette').count()==0 and p.locator('#v024VatsFigure').count()==0,'Ancien dessin anatomique supprimé')
  ck(p.evaluate("getComputedStyle(document.getElementById('vats')).backdropFilter")=='none','Pas de flou opaque cachant la scène')
  expected={'head','body','arm_l','arm_r','leg_l','leg_r'}
  ck({x['id'] for x in a['parts']}==expected,'Six zones distinctes sur un humanoïde')
  ck(all(x['chance']>0 for x in a['parts']),'Toutes les zones découvertes visibles dans une arène ouverte')
  ck(all(x['visible'] and x['center'] and x['label'] for x in a['screen']),'Six ancrages projetés dans le cadre de la caméra')
  # Independently calculate projection from camera and centre; compare <.1px.
  cam=a['camera'];f=cam['dir'];ln=math.sqrt(sum(t*t for t in f));f=[t/ln for t in f];right=[-f[2],0,f[0]];ln=math.sqrt(sum(t*t for t in right));right=[t/ln for t in right];up=[right[1]*f[2]-right[2]*f[1],right[2]*f[0]-right[0]*f[2],right[0]*f[1]-right[1]*f[0]];focal=960/(2*math.tan(math.radians(cam['fov'])/2));drifts=[]
  for part in a['parts']:
   rel=[part['center'][i]-cam['pos'][i] for i in range(3)];z=sum(rel[i]*f[i] for i in range(3));x=720+sum(rel[i]*right[i] for i in range(3))*focal/z;y=480-sum(rel[i]*up[i] for i in range(3))*focal/z;point=next(e for e in a['screen'] if e['id']==part['id'])['center'];drifts.append(math.hypot(x-point['x'],y-point['y']))
  ck(max(drifts)<.1,'Projection indépendante : écart inférieur à 0,1 pixel',max(drifts))
  # Click labels and actual polygon volumes; click alone cannot consume anything.
  ap,ammo=s()['player']['ap'],s()['player']['ammoClip'];p.locator('#vatsParts [data-part="arm_l"]').click();ck(c('v025Info')['selected']['part']=='arm_l','Clic sur OUTIL/BRAS gauche sélectionne le membre réel')
  ck(not snap()['queue'] and s()['player']['ap']==ap and s()['player']['ammoClip']==ammo,'Sélection sans ajout ou débit implicite')
  p.locator('#v025Overlay [data-part="head"]').dispatch_event('click');ck(c('v025Info')['selected']['part']=='head','La zone projetée elle-même est interactive')
  tint=c('v025Tinted');ck(tint and all(x['part']=='head' for x in tint),'Surbrillance appliquée aux primitives de la tête, pas à une silhouette séparée',tint[:3])
  p.locator('#vatsParts [data-part="arm_r"]').click();p.locator('[data-v23="vats-add"]').click();ck(snap()['queue'][0]['id']=='arm_r','File conserve le bras droit réellement sélectionné')
  c('v023Crit',100);c('v025Select','head');p.locator('[data-v23="vats-critical"]').click();ck(snap()['queue'][-1]['critical'] and snap()['queue'][-1]['id']=='head','Critique explicitement réservé sur la tête')
  p.locator('[data-v23="queue-up|1"]').click();ck(snap()['queue'][0]['critical'],'Réorganisation visuelle préserve le critique')
  p.locator('[data-v23="queue-remove|1"]').click();ck(len(snap()['queue'])==1 and s()['player']['ap']==ap,'Retrait individuel sans coût')
  p.locator('[data-v23="vats-close"]').click();ck(c('getMode')=='PLAYING' and s()['v023']['critical']==100,'Annulation garde le critique')
  ck(not c('v025Info')['active'] and s()['player']['pos']==before['pos'],'Sortie retire le cadrage, position exacte conservée')
  ck(p.evaluate("!document.body.classList.contains('v025-targeting')"),'HUD normal rétabli après fermeture')
  # Rotated and elevated actor target volumes are derived from its visible rig.
  reset();openv();base=snap()['parts'];c('v025MoveEnemy',0,[1,3.2,1],math.pi/2);rot=snap()['parts'];ck(all(x['center'][1]>3.2 for x in rot),'Volumes suivent l’altitude du modèle')
  armL=next(x for x in rot if x['id']=='arm_l');armR=next(x for x in rot if x['id']=='arm_r');ck(abs(armL['center'][2]-armR['center'][2])>.45,'Bras gauche/droit suivent la rotation, pas l’axe X fixe')
  ck(all(math.isfinite(v) for x in rot for v in x['center']),'Coordonnées d’anatomie finies après rotation/translation')
  # Actual emitted shot side, native per-limb persistence in an authored scene.
  c('v020VatsCancel');c('v020Reset');c('v020Load','transit_depot');c('v021Pose','transit_depot:unit',math.pi);c('v020EnemyPatch',{'health':500,'maxHealth':500});c('v025Damage','arm_l',30);loss=c('v025Loss');ck(loss['arm_l']>0 and loss['arm_r']==0,'Une blessure à gauche ne remplit pas la jauge de droite',loss)
  c('v025Damage','leg_r',20);loss=c('v025Loss');ck(loss['leg_r']>0 and loss['leg_l']==0,'Blessures des jambes distinguées')
  ck(c('save') is True,'Sauvegarde réussie via adaptateur mémoire déclaré')
  key=c('v018SaveKey');raw=p.evaluate('(k)=>localStorage.getItem(k)',key);ck(json.loads(raw)['v025']['limbs']['transit_depot']['transit_depot:unit']['arm_l']>0,'Dégâts de membre sérialisés dans le JSON de sauvegarde')
  c('v020Load','traverse_archives');c('v020Load','transit_depot');ck(c('v025Loss')['arm_l']>0 and c('v025Loss')['arm_r']==0,'Dégâts de côté conservés au rechargement de scène')
  imported=c('v018Migrate',json.loads(raw));ck(imported['v025']['limbs']==json.loads(raw)['v025']['limbs'],'Migration conserve les atteintes anatomiques')
  bad=json.loads(raw);bad['v025']['limbs']['bad']={'unit':{'head':-20,'body':500,'unknown':.6}};m=c('v018Migrate',bad);ck(m['v025']['limbs']['bad']['unit']=={'head':0,'body':1},'Import borne les valeurs et filtre les membres inconnus')
  # Cover blocks selected parts only, not an imaginary drawing of the whole body.
  reset();c('v025Wall',0,.6,4,5,1.2,.35);a=openv();vis={x['id']:x['chance'] for x in a['parts']};ck(vis['head']>0 and vis['leg_l']==0 and vis['leg_r']==0,'Couverture basse : tête exposée, deux jambes masquées',vis)
  ck(p.locator('#vatsParts [data-part="leg_l"]').is_disabled(),'Étiquette masquée désactivée')
  c('v025Select','leg_l');ck(not c('v023Queue'),'Impossible de réserver un membre derrière le couvert')
  c('v025Select','head');ck(c('v023Queue'),'Tête exposée encore réservable')
  c('v020VatsCancel');reset();openv();c('v025Select','body');c('v023Crit',100);c('v023Queue',True);ap=s()['player']['ap'];ammo=s()['player']['ammoClip'];c('v020AddWall');c('v020VatsExecute');c('v020RandomTick',.1,.5)
  ck(s()['player']['ap']==ap and s()['player']['ammoClip']==ammo and s()['v023']['critical']==100,'Mur après réservation : action annulée sans coût ni critique')
  ck(c('v025Snapshot')['lastShot']['emitted'] is False,'Retour d’exécution explicite pour action annulée')
  reset();openv();c('v025Select','arm_r');c('v023Crit',100);c('v023Queue',True);ap=s()['player']['ap'];ammo=s()['player']['ammoClip'];c('v020VatsExecute');c('v020RandomTick',.1,.999)
  ck(s()['player']['ap']==ap-22 and s()['player']['ammoClip']==ammo-1 and s()['v023']['critical']==0,'Critique côté droit : coût exact de l’action émise')
  ck(c('v025Loss')['arm_r']>0 and c('v025Loss')['arm_l']==0,'Tir critique atteint le membre choisi, pas le côté opposé')
  ck(p.locator('#v025Exec').is_visible(),'Bilan d’exécution présent pendant la rafale')
  c('v020VatsCancel');ck(p.locator('#v025Exec').is_hidden(),'Bilan retiré à l’arrêt')
  # Family-specific anatomy from real original rigs (not all a humanoid).
  families=[('robot',6),('feralGhoul',6),('tarente',3),('radscorpion',5),('crab',5),('sanglier',6),('ledgerhound',6),('eyebot',4),('walkingcrane',4),('deathclaw',3)]
  for typ,count in families:
   reset(typ);rig=c('v025RigInfo');a=openv();ck(len(rig['parts'])>=count,typ+' : zones construites à partir du modèle',[(x['id'],x['label']) for x in rig['parts']]);ck(all(math.isfinite(v) and v>=0 for x in rig['parts'] for v in x['size']),typ+' : volumes finis et positifs')
  # Multi-target and queue compatibility, including side IDs.
  reset();c('v023EnemyAdd');c('v020SetPlayer',{'ap':200,'maxAp':200});a=openv();first=a['targets'][0]['id'];c('v025Select','arm_l');c('v023Queue');p.locator('[data-v23="vats-target|1"]').click();c('v025Paint');ck(c('v025Info')['selected']['enemy']!=first,'Changer de cible cadre le second acteur du monde')
  c('v025Select','head');c('v023Queue');ck(len(snap()['queue'])==2 and snap()['queue'][0]['enemy']!=snap()['queue'][1]['enemy'],'File multi-cibles conserve les bons acteurs')
  c('v020VatsCancel');reset();c('v020SetPlayer',{'ap':200,'maxAp':200});openv();c('v025Select','body')
  for _ in range(6):c('v023Queue')
  ck(len(snap()['queue'])==6 and not c('v023Queue'),'Limite à six actions conservée')
  c('v020Load','mooring_station');ck(not c('v025Info')['active'] and c('v020Combat')['execution'] is None,'Transition supprime ancrages/caméra/file obsolètes')
  # Far and close targets: projection remains finite, no translation cheat.
  for distance in [1.2,4,18,60]:
   reset(distance=distance);c('v020GrantWeapon','huntingRifle');c('v020Equip','huntingRifle');c('v020Tick',1);a=openv();ck(a['mode']=='VATS' and 10<=a['camera']['fov']<=85 and a['camera']['pos']==a['player']['pos'],f'Cadrage à {distance} m, zoom borné et origine fixe');ck(all(math.isfinite(q) for r in a['screen'] if r['center'] for q in r['center'].values()),f'Projection finie à {distance} m')
  reset(distance=90);ck(c('v020Vats')=='PLAYING','Hors portée : le zoom ne crée pas une cible autorisée')
  # Keyboard and touch: selectors reach actual rendered areas.
  reset();openv();p.locator('#vatsParts [data-part="head"]').click();p.keyboard.press('s');ck(c('v025Info')['selected']['part']=='body','S sélectionne le membre suivant');p.keyboard.press('z');ck(c('v025Info')['selected']['part']=='head','Z AZERTY sélectionne le membre précédent');p.keyboard.press('e');ck(len(snap()['queue'])==1,'E ajoute une action');p.keyboard.press('Backspace');ck(not snap()['queue'],'Retour arrière retire une action')
  for width,height in [(390,844),(844,390),(1280,720)]:
   p.set_viewport_size({'width':width,'height':height});p.wait_for_timeout(60);c('v025Paint');a=snap();ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'{width}×{height} sans débordement horizontal');labels=[r['label'] for r in a['screen'] if r['visible']];ck(all(r['x']>=0 and r['x']+r['width']<=width+1 for r in labels),f'{width}×{height} étiquettes dans la largeur');
   p.locator('#vatsParts [data-part="body"]').click();p.locator('[data-v23="vats-add"]').click();ck(snap()['queue'][-1]['id']=='body',f'{width}×{height} ciblage et ajout au clic');p.locator('[data-v25="undo"]').click()
  p.set_viewport_size({'width':390,'height':844});c('v025Paint');c('v023Crit',100);c('v025Select','head');p.locator('[data-v23="vats-critical"]').click();p.locator('#v025QueueToggle').click();ck(p.locator('#vatsQueue').is_visible(),'File dépliable sur mobile');p.locator('[data-v23="queue-remove|0"]').click();ck(not snap()['queue'],'Retrait tactile dans la file dépliée');p.locator('[data-v23="vats-close"]').click();ck(c('getMode')=='PLAYING','Fermeture tactile')
  # Native resume from v024: choose newest old source and preserve old bytes.
  p.set_viewport_size({'width':1280,'height':900});c('v020Reset');c('v020Load','transit_depot');old=s();old.pop('v025',None);old['version']='0.24.0';txt=json.dumps(old)
  p.evaluate('(t)=>{localStorage.removeItem("fallout_mistral_sandbox_v026");localStorage.setItem("fallout_mistral_sandbox_v024",t)}',txt);ck(c('v025ResumeSandbox'),'Reprise v0.24 via adaptateur mémoire déclaré');ck(c('v018SaveKey')=='fallout_mistral_sandbox_v030','Nouvelle clé v0.25, pas d’écrasement v0.24');ck(p.evaluate('localStorage.getItem("fallout_mistral_sandbox_v024")')==txt,'Ancienne sauvegarde préservée octet pour octet')
  ck(not errors,'Aucune exception JavaScript pendant la suite',errors)
 except Exception:ck(False,'Exception de la suite',traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  result=dict(version='0.25.0',html_sha256=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_bytes()).hexdigest(),total=len(rows),passed=sum(x['ok'] for x in rows),failed=sum(not x['ok'] for x in rows),errors=errors,source=URL,scope='Localhost navigation refused by managed browser (ERR_BLOCKED_BY_ADMINISTRATOR), exact HTML via set_content. Native opaque-origin refusal checked, then explicit memory storage adapter for successful save scenarios; software Chromium. Original authored scene for menu/persistence; explicitly synthetic arenas for combat/occlusion/anatomy projection. DOM clicks, keyboard and viewport emulation. No official geography imported.',results=rows);(O/'QA_V025.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));b.close();print('RESULT',result['passed'],result['failed'],flush=True)
raise SystemExit(result['failed']>0)
