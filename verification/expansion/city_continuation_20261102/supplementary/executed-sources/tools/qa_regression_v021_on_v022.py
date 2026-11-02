#!/usr/bin/env python3
"""Targeted real-HTML QA: three authored fictional scenes, software renderer.
Movement tests use actual player controller, directed by the route follower.
The old locked-choice test deliberately dispatches a programmatic click (aria-disabled now blocks Playwright normal click).
Action tests approach via injected position; they are not a full human playthrough.
Storage failure is genuine; successful saves use an explicitly mocked adapter.
"""
from pathlib import Path
from qa_support import chromium_path
import json,hashlib,math,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
html=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[];metrics=[]
def ck(ok,name,data=None):
 rows.append(dict(ok=bool(ok),name=name,detail=data));print(('OK' if ok else 'FAIL'),name,str(data)[:250] if data is not None else '',flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);pg=b.new_page(viewport={'width':1280,'height':800});pg.on('pageerror',lambda e:errors.append(str(e)));pg.set_default_timeout(7000);pg.set_content(html,wait_until='load');pg.wait_for_timeout(4000)
 ev=pg.evaluate
 def js(s,arg=None):return ev(s,arg)
 def call(n,*args):return ev('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
 def dismiss():call('v020ModalDismiss')
 def reset():call('v020Reset')
 def load(id):call('v020Load',id)
 def st():return call('getState')
 def near(id):return call('v020Approach',id)
 def action(id,a,c=None):near(id+':'+a);return call('v021Action',id,a,c)
 def fixture(wall=False):
  call('v020Fixture',wall);call('v020EnemyPatch',dict(damage=12,range=15,detect=25,speed=0,alerted=True,state='combat',attackCooldown=0,attackType='laser'));call('v021ResetEvents')
 try:
  call('setRenderPaused',True);call('v018NoNetwork',True)
  ck(call('v021Info')['version']=='0.21.0','Version v0.21 initialisée')
  pg.locator('#btnV021').wait_for(state='visible',timeout=30000)
  ck(pg.locator('#btnV021').is_visible(),'Accès de découverte séparé visible au menu')
  ck(call('v021Info')['officialTiles']==0,'Aucune fausse acquisition géographique déclarée')
  load('transit_depot');ck(call('save') is False,'Refus réel du stockage signalé')
  ev("window.__storageMap={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>Object.prototype.hasOwnProperty.call(__storageMap,k)?__storageMap[k]:null,setItem:(k,v)=>{__storageMap[k]=String(v)},removeItem:k=>delete __storageMap[k],clear:()=>{__storageMap={}}}})")
  ck(call('save') is True,'Sauvegarde via adaptateur mémoire explicitement contrôlé')
  defs=call('v021Defs')
  for id,d in defs.items():
   reset();load(id);s=call('v020Stats');g=call('v021Graph');metrics.append(dict(id=id,draws=s['draws'],colliders=s['colliders'],graph=g))
   ck(s['id']==id and len(s['rooms'])>=6,id+' : six espaces historiques conservés')
   ck(s['draws']>600 and s['colliders']>40,id+' : décor solide et détaillé',metrics[-1])
   ck(g['ground']>1000 and g['upper']>400,id+' : graphe réellement multi-niveaux')
   paths=[{'id':i['id'],'nodes':len(call('v020Route',i['pos']) or [])} for i in s['interactables']]
   ck(all(i['nodes'] for i in paths if not i['id'].startswith(('v029:exit:','v029:contact','v029:roomnote:'))),id+' : points historiques et contrôleurs reliés (alcôve fermée testée séparément)',paths)
   ck(not call('v020Collides',s['player']),id+' : apparition libre')
   target=[d['cluePos'][0],3.2,d['cluePos'][2]+1]
   walk=call('v021ActualWalk',target);ck(walk['ok'] and walk['maxY']>4.7,id+' : montée par le contrôleur réel',walk)
   ck(abs(call('v021Ground',target[0],target[2],0))<.1,id+' : sol bas conservé sous la plateforme')
   ck(abs(call('v021Ground',target[0],target[2],3.2)-3.2)<.01,id+' : sol haut distinct')
   down=call('v021ActualWalk',[0,0,18]);ck(down['ok'] and down['pos'][1]<1.8,id+' : retour au rez-de-chaussée',down)
   # A terminal above the player may not be used through its supporting slab.
   call('v021Scenario',{'accepted':True});call('v020SetPlayer',{'pos':[target[0],1.65,target[2]]});call('v021Action',id,'clue');ck(not st()['v021']['clues'].get(d['clue']),id+' : preuve inaccessible à travers le plancher')
   near(id+':contact');ck(call('v021Talk',id),id+' : dialogue physique du responsable');dismiss()
   before=call('v021EnemyInfo');action(id,'power');dismiss();after=call('v021EnemyInfo')
   if id!='mooring_station':
    ck(not after[0]['alive'],id+' : consignation neutralise le robot')
    ck(after[1]['alive'],id+' : animal ou goule non neutralisé par une coupure électrique')
   else:
    ck(all(e['alive'] for e in after),id+' : une seule coupure ne suffit pas')
    action(id,'power2');dismiss();ck(all(not e['alive'] for e in call('v021EnemyInfo')),id+' : deux coupures arrêtent les automates')
   va=call('v021VisualAudit');ck(all(e['parts']>=10 and e['finite'] for e in va),id+' : représentations distinctes et coordonnées valides',va)
   near(id+':tape');call('v021Action',id,'tape');ck(call('getMode')=='HOLOTAPE',id+' : cassette ouverte physiquement');ck(d['person'] in pg.locator('#holotapeTitle').inner_text(),id+' : intervenant propre à la cassette');call('v018TapeStep',1);ck(call('v018TapeState')['index']==1,id+' : progression du sous-titre');call('v018TapeClose')
   call('v021RenderAt',s['player'],0,.02,1);render=call('v021Renderer');ck(render.get('backend')=='Canvas · profondeur complète' and render['faces']>1000,id+' : rendu réel avec profondeur',render)
  # Full narrative with real action dispatch and explicit preconditions.
  reset();load('transit_depot');call('v021Action','transit_depot','clue');ck(not st()['v021']['clues'],'Preuve refusée à distance')
  action('transit_depot','clue');ck(not st()['v021']['clues'],'Acceptation préalable nécessaire')
  near('transit_depot:contact');call('v021Talk','transit_depot');pg.locator('#dialogueChoices button').first.click();dismiss();ck(st()['v021']['accepted'],'Acceptation par un vrai clic dans le dialogue')
  for id,d in defs.items():
   load(id);ck(action(id,'clue') is True,id+' : collecte de la preuve sur place');dismiss();before=st();action(id,'clue');ck(st()['v021']['clues']==before['v021']['clues'] and st()['player']['caps']==before['player']['caps'],id+' : preuve non duplicable')
   action(id,'power');dismiss()
   if id=='mooring_station':
    near(id+':finish');call('v021Action',id,'finish','manual');ck(st()['v021']['ending'] is None,'Conclusion interdite avant la seconde coupure');action(id,'power2');dismiss()
  ck(len(st()['v021']['clues'])==3,'Les trois actes alimentent le même dossier')
  call('v021MuteEnemies');near('mooring_station:finish');before=st();call('v021Action','mooring_station','finish');locked=pg.locator('#dialogueChoices .locked').count();pg.locator('#dialogueChoices button').nth(1).evaluate('button=>button.click()');ck(st()['v021']['ending'] is None and locked==1,'Fin contrôlée verrouillée visuellement sans témoin');dismiss()
  load('traverse_archives');ck(action('traverse_archives','witness') is True and st()['v021']['witness'],'Témoin facultatif obtenu physiquement');dismiss()
  load('mooring_station');call('v021MuteEnemies');near('mooring_station:finish');before=st();ck(call('v021Action','mooring_station','finish','audited'),'Fin contrôlée obtenue après toutes les étapes')
  ck(st()['player']['caps']-before['player']['caps']==180,'Récompense exacte de 180 capsules')
  texts=[]
  for page in range(3):
   texts.append(pg.locator('#dialogueLine').inner_text());pg.locator('#dialogueChoices button').first.click()
  ck(len(set(texts))==3 and all(len(t)>140 for t in texts),'Trois scènes de conclusion distinctes, non phrases témoins')
  before=st();near('mooring_station:finish');call('v021Action','mooring_station','finish','manual');ck(st()['player']['caps']==before['player']['caps'] and st()['v021']['ending']=='audited','Conclusion et récompense non remplaçables')
  ck(len([n for n in call('v021Actors') if ':crew:' in n['id']])==3,'Équipe visible après la décision')
  for id in defs:
   load(id);ck(len([n for n in call('v021Actors') if ':crew:' in n['id']])==3,id+' : conséquence visible au rechargement')
  # Every ending, and reread never changes rewards.
  for choice in ['manual','silence']:
   reset();load('mooring_station');call('v021Scenario',dict(accepted=True,clues={'manifest':True,'waveform':True,'beacon':True},switches={'mooring_station:power':True,'mooring_station:power2':True}));call('v021MuteEnemies');near('mooring_station:finish');ck(call('v021Action','mooring_station','finish',choice),'Résolution alternative active : '+choice);dismiss();caps=st()['player']['caps'];call('v021Ending',0);dismiss();ck(st()['player']['caps']==caps,'Relecture sans récompense : '+choice)
  # Parent and return, with a real portal interaction.
  reset();load('aubagne');near('v021:portal:transit_depot');call('v020SetPlayer',dict(yaw=.37,pitch=.11));before=st()['player'];ck(call('v021Enter','transit_depot'),'Entrée physique depuis Aubagne');ck(call('getWorld')=='transit_depot','Entrée charge le dépôt')
  ck(call('save'),'Écriture de la pile de retour contrôlée');key=call('v018SaveKey');raw=ev('(k)=>localStorage.getItem(k)',key);saved=json.loads(raw);ck(saved['v021']['returnPoints'][-1]['zone']=='aubagne','Pile de retour dans le JSON')
  ck(bool(call('v018InspectSave',saved)),'Validateur accepte une sauvegarde dans le nouveau lieu')
  near('transit_depot:exit');ck(call('v021Exit'),'Sortie physique');after=st()['player'];ck(math.dist(before['pos'],after['pos'])<.001 and abs(before['yaw']-after['yaw'])<.001 and abs(before['pitch']-after['pitch'])<.001,'Retour à la position, direction et inclinaison exactes')
  old=st();old.pop('v021');old['version']='0.20.0';old['keep_this']={'ok':True};mig=call('v018Migrate',old);ck(mig['keep_this']['ok'] and not mig['v021']['accepted'],'Migration v0.20 ajoute l’enquête sans supprimer les champs inconnus')
  ck(call('v018Keys')['campaign']!=call('v018Keys')['sandbox'],'Campagne et découverte restent séparées')
  # Telegraphs in clearly synthetic fixture; no claim of geographical footage.
  reset();fixture();hp=st()['player']['hp'];t=call('v021AiTick',.02);ck(t['threats']==1 and t['hp']==hp,'Attaque annoncée avant dégâts')
  call('v021AiTick',.4);ck(st()['player']['hp']==hp,'Aucun dégât pendant la préparation')
  for _ in range(9):call('v021AiTick',.1)
  ck(st()['player']['hp']<hp and any(e['type']=='impact' for e in call('v021Events')),'Impact appliqué si le joueur reste dans la cible')
  fixture();hp=st()['player']['hp'];call('v021AiTick',.02);call('v020SetPlayer',{'pos':[3,1.65,8]});call('v021AiTick',1.2);ck(st()['player']['hp']==hp and any(e['type']=='évité' for e in call('v021Events')),'Déplacement hors cible évite le tir verrouillé')
  fixture();hp=st()['player']['hp'];call('v021AiTick',.02);call('v020AddWall');call('v021AiTick',1.2);ck(st()['player']['hp']==hp,'Un obstacle apparu pendant la préparation bloque l’impact')
  fixture();call('v021AiTick',.02);call('v021Hit',0,20);ck(not call('v021EnemyInfo')[0]['windup'] and any(e['type']=='interrompu' for e in call('v021Events')),'Un coup suffisant interrompt la préparation')
  fixture();call('v021AiTick',.02);call('v021Open');t=call('v021EnemyInfo')[0]['windup']['elapsed'];call('v021AiTick',2);ck(call('v021EnemyInfo')[0]['windup']['elapsed']==t,'Pause du combat dans le carnet');dismiss();load('transit_depot');ck(not any(e['windup'] for e in call('v021EnemyInfo')),'Aucune préparation ancienne après changement de scène')
  # New floor UI, real clicks, portrait layout and menu access.
  load('transit_depot');dismiss();pg.keyboard.press('j');ck(pg.locator('#v020Title').inner_text()=='Les absents de la relève','J ouvre le carnet lié aux trois lieux');dismiss();pg.keyboard.press('m');ck(pg.locator('.v21-floor-controls').is_visible(),'M affiche le choix d’étage');pg.get_by_role('button',name='Passerelles · +3,2 m',exact=True).click();ck(pg.get_by_role('button',name='Passerelles · +3,2 m',exact=True).get_attribute('class')=='active','Changement réel d’étage dans le plan')
  pg.locator('#v020Map').click(position={'x':380,'y':110});ck(bool(pg.locator('#v020PathInfo').inner_text()),'Plan traite une destination à l’étage');dismiss()
  pg.set_viewport_size({'width':390,'height':844})
  for floor in [0,3.2]:
   call('v021Floor',floor);box=pg.locator('#v020Panel').bounding_box();ck(box['x']>=0 and box['x']+box['width']<=391 and pg.locator('#v020Close').is_visible(),'Plan mobile fermé sans débordement · étage '+str(floor))
  call('v021Open');ck(pg.locator('#v020Close').is_visible() and ev('document.documentElement.scrollWidth<=innerWidth'),'Carnet mobile sans débordement')
  ck(not errors,'Aucune exception JavaScript dans les contrôles ciblés',errors)
 except Exception:
  ck(False,'Exception de la suite',traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  result={'version':'0.22.0','html_sha256':hashlib.sha256(html.encode()).hexdigest(),'scope':{'browser':'Chromium Linux headless, HTML exact via set_content','graphics':'SoftwareRenderer avec profondeur complète; aucun GPU matériel disponible','movement':'contrôleur joueur réel conduit par graphe, pas simple téléportation','narrative':'clic acceptation réel; approches injectées pour actions, pas parcours humain intégral','storage':'refus réel, puis adaptateur mémoire explicite; persistance intersession navigateur non certifiée','geography':'aucune acquisition cartographique officielle'},'total':len(rows),'passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'errors':errors,'results':rows,'scenes':metrics}
  (O/'QA_REGRESSION_V021_ON_V022.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('RESULT',result['passed'],result['failed'],flush=True);b.close()
raise SystemExit(bool(result['failed']))
