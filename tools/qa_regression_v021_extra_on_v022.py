from pathlib import Path
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import hashlib,json,math,traceback
R=Path(__file__).resolve().parents[1];html=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();rows=[];errors=[]
def ck(ok,name,detail=None):rows.append(dict(ok=bool(ok),name=name,detail=detail));print('OK' if ok else 'FAIL',name,str(detail)[:170],flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);pg=b.new_page(viewport={'width':1280,'height':800});pg.on('pageerror',lambda e:errors.append(str(e)));pg.set_content(html,wait_until='load');pg.locator('#btnV021').wait_for(state='visible',timeout=30000)
 def call(n,*a):return pg.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  call('v018NoNetwork',True);call('setRenderPaused',True)
  pg.evaluate("window.__QA_STORAGE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__QA_STORAGE[k]||null,setItem:(k,v)=>__QA_STORAGE[k]=String(v),removeItem:k=>delete __QA_STORAGE[k]}})")
  pg.on('dialog',lambda d:d.accept());pg.locator('#btnV021').click();pg.wait_for_timeout(900)
  ck(call('getWorld')=='transit_depot','Clic du menu lance réellement le dépôt sans transition périmée')
  ck(call('getMode')=='PLAYING','Contrôle joueur actif après le menu')
  key=call('v018SaveKey');ck(key==call('v018Keys')['sandbox'],'Découverte écrite uniquement dans la clé exploration')
  saved=json.loads(pg.evaluate('(k)=>localStorage.getItem(k)',key));ck(saved['player']['zone']=='transit_depot' and saved['v021']['visited']['transit_depot'],'Point de départ sauvegardé dans le nouveau lieu')
  call('v020Reset');call('v020Load','transit_depot');before=call('v021Actors');
  for _ in range(30):call('v020NpcStep',.2)
  after=call('v021Actors');a=next(n for n in before if n['id'].endswith('porter'));z=next(n for n in after if n['id'].endswith('porter'));ck(math.dist(a['pos'],z['pos'])>.05,'Le porteur du dépôt se déplace réellement',{'from':a['pos'],'to':z['pos']})
  call('v020SetPlayer',{'pos':[-5,4.85,-17]});call('v020Companion','mireille',[-4,0,17],0);call('v020Order','fire','quiet');call('v020Order','move','follow');call('v021MuteEnemies')
  for _ in range(400):last=call('v020Companion','mireille',None,.1)
  ck(last['pos'][1]>3 and math.dist(last['pos'],[-5,3.2,-17])<4,'Le compagnon rejoint le joueur par les escaliers',last)
  # Same final scene state can be exported and imported through the real validator.
  call('v021Scenario',{'accepted':True,'clues':{'manifest':True},'switches':{'transit_depot:power':True},'returnPoints':[{'zone':'aubagne','pos':[12,1.65,7],'yaw':.37,'pitch':.08}]});call('save');raw=pg.evaluate('(k)=>localStorage.getItem(k)',call('v018SaveKey'));call('v021Scenario',{'accepted':False,'clues':{}});call('v018ImportRaw',raw);s=call('v021State');ck(s['accepted'] and s['clues'].get('manifest') and s['returnPoints'][0]['zone']=='aubagne','Import JSON réel restaure preuves, coupures et retour (stockage simulé)')
  types=[('raider','raider'),('feral','ghoul'),('robot','robot'),('archiveDrone','drone'),('tarente','tarente'),('radscorpion','scorpion'),('crab','crab'),('sanglier','boar'),('mutantHound','dog'),('craneWalker','crane')]
  for type,family in types:
   call('v020Fixture',False,type,8);d=call('v021VisualAudit')[0];ck(d['family']==family and d['parts']>=10 and d['finite'],'Silhouette : '+family,d)
  ck(not errors,'Aucune exception JS du menu, des acteurs et de l’import',errors)
 except Exception:ck(False,'Exception suite supplémentaire',traceback.format_exc())
 finally:
  out=dict(html_sha256=hashlib.sha256(html.encode()).hexdigest(),scope='HTML exact, rendu logiciel ; fixture visuelle synthétique explicitement nommée ; stockage mémoire',total=len(rows),passed=sum(r['ok'] for r in rows),failed=sum(not r['ok'] for r in rows),results=rows,errors=errors);(R/'verification/QA_REGRESSION_V021_EXTRA_ON_V022.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));b.close();print('RESULT',out['passed'],out['failed'])
raise SystemExit(bool(out['failed']))
