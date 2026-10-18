from pathlib import Path
import json, hashlib, traceback
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
H=(R/'JOUER_FALLOUT_MISTRAL_v0.39.html').read_text(encoding='utf-8')
checks=[];errors=[]
def ck(name,cond,detail=None):
 checks.append({'name':name,'ok':bool(cond),'detail':detail});print(('PASS ' if cond else 'FAIL ')+name, str(detail or '')[:220],flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept());p.set_content(H,wait_until='load');p.wait_for_timeout(3400)
 p.evaluate("window.__QA_STORE=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{get length(){return __QA_STORE.size},getItem:k=>__QA_STORE.get(String(k))??null,setItem:(k,v)=>__QA_STORE.set(String(k),String(v)),removeItem:k=>__QA_STORE.delete(String(k)),clear:()=>__QA_STORE.clear(),key:i=>[...__QA_STORE.keys()][i]??null}})")
 def c(name,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+name+'(...a)',list(args))
 try:
  menu=p.eval_on_selector_all('#menuScreen nav>*','els=>els.map(e=>e.id)')
  ck('Menu joueur structuré en neuf entrées',menu==['btnContinue','btnNew','btnV035Load','btnV035Career','btnV035Operations','btnChapter','btnOptions','btnCredits','btnV035Admin'],menu)
  ck('Outils versionnés absents du menu principal',not any(x.startswith('btnV0') and x not in {'btnV035Load','btnV035Career','btnV035Operations','btnV035Admin'} for x in menu),menu)
  info=c('v035Info');ck('Version et huit opérations',info['version']=='0.35.0' and info['operations']==8,info)
  p.click('#btnV035Career');ck('Écran carrière ouvrable',p.locator('#v035Screen:not(.hidden)').count()==1);ck('Six chapitres affichés',p.locator('.v35-chapter').count()==6);p.click('[data-v35="close"]')
  p.click('#btnV035Admin');ck('Outils internes regroupés dans Admin',p.locator('#v035AdminMount #btnV030').count()==1 and p.locator('#v035AdminMount #v018MenuStatus').count()==1);p.click('[data-v35="close"]')
  # Start a free game for full content access.
  c('v018NoNetwork',True);c('setRenderPaused',True);c('v018StartFree');p.wait_for_timeout(500)
  st=c('v020State');ck('Exploration libre démarrée',st['mode']=='free',st['mode']);ck('Hub A-03 disponible',c('v035Info')['hub'] is True)
  # Manual save slot and restore.
  caps=st['player']['caps'];ck('Emplacement 1 enregistré',bool(c('v035SaveSlot',1)));c('v020SetPlayer',{'caps':caps+999});ck('Mutation de contrôle appliquée',c('v020State')['player']['caps']==caps+999);ck('Emplacement 1 chargé',c('v035LoadSlot',1));p.wait_for_timeout(300);ck('Chargement restaure le portefeuille',c('v020State')['player']['caps']==caps,c('v020State')['player']['caps'])
  ck('Autosave créé',bool(c('v035Autosave','qa')) and c('v035Info')['autosave'])
  # A-03 return loop.
  c('v020Load','aubagne');stats=c('v020Stats');ids=[x['id'] for x in stats['interactables']];ck('Retour A-03 présent à Aubagne','v035-vault-return' in ids)
  ck('Retour A-03 approchable',c('v020Approach','v035-vault-return') is not None);ck('Retour A-03 activé',c('v020Interact','v035-vault-return'));p.wait_for_timeout(250);ck('Abri A-03 chargé',c('v020Stats')['id']=='vault',c('v020Stats')['id'])
  ids=[x['id'] for x in c('v020Stats')['interactables']];ck('Hub possède lit, tableau et terminal',all(x in ids for x in ['v035-hub-bed','v035-hub-board','v035-hub-save']),ids)
  c('v020SetPlayer',{'hp':25,'ap':3,'rad':17});before_time=c('v020State')['worldTime'];ck('Repos A-03 réussi',c('v035Rest'));after=c('v020State');ck('Repos restaure PV et PA',after['player']['hp']==after['player']['maxHp'] and after['player']['ap']==after['player']['maxAp']);ck('Repos conserve les radiations',after['player']['rad']==17);ck('Repos avance de huit heures',round((after['worldTime']-before_time)%24,2)==8.0,(before_time,after['worldTime']))
  # Operation through physical checkpoints.
  c('v020Load','aubagne');base_caps=c('v020State')['player']['caps'];ck('Opération Ateliers lancée',c('v035StartOperation','ateliers'));p.wait_for_timeout(250);ck('Opération charge Aubagne',c('v020Stats')['id']=='aubagne')
  for i in range(3):
   oid=f'v035-op-ateliers-{i}';ck(f'Poste {i+1} injecté',oid in [x['id'] for x in c('v020Stats')['interactables']]);ck(f'Poste {i+1} approché',c('v020Approach',oid) is not None);ck(f'Poste {i+1} validé',c('v020Interact',oid));p.wait_for_timeout(120)
  opstate=c('v035Operations');career=c('v035Career');ck('Opération clôturée',opstate['active'] is None and opstate['totalCompleted']==1,opstate);ck('Record de carrière inscrit',career['operations']==1,career);ck('Première prime versée',c('v020State')['player']['caps']>base_caps,(base_caps,c('v020State')['player']['caps']))
  # Session recap and save UI on mobile.
  recap=c('v035Recap');ck('Bilan de session calculé',recap is not None and 'chapter' in recap,recap)
  c('v035Open','saves');p.set_viewport_size({'width':390,'height':844});ck('Trois cartes de sauvegarde en portrait',p.locator('.v35-slot').count()==3);ck('Interface sans débordement majeur',p.evaluate('document.getElementById("v035Screen").scrollWidth<=innerWidth+2'));p.keyboard.press('Escape');ck('Échap ferme la couche produit',p.locator('#v035Screen.hidden').count()==1)
  ck('Aucune exception JavaScript',not errors,errors)
 except Exception:
  ck('Exception du pilote',False,traceback.format_exc())
 finally:b.close()
rep={'version':'0.39.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'Régression fonctionnalité v0.35 sur HTML exact v0.39, Chromium logiciel, stockage mémoire déclaré pour les écritures.'}
(O/'QA_REGRESSION_V035_ON_V039.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print('FINAL',rep['passed'],rep['failed'],flush=True)
raise SystemExit(bool(rep['failed'] or errors))
