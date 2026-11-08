"""Instrumented Notaires smoke on actual production HTML and Radieuse interior.
Prerequisites assembled through real quest models. Scripted positions, isolated
storage and software renderer: NOT a human full campaign or IGN exterior test.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/notaires/browser')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__N65_QA={
 close(){closePipboy();},
 setup(reported=true){
  closePipboy();debugDismissDialogue();debugRenderPaused=true;updatePlayer=()=>{};
  for(const id of ['water','food','cloth','scrap','circuitry','chemicals'])state.inventory[id]=60;
  state.player.caps=250;state.player.hp=100;state.character.special.I=6;state.character.special.C=6;
  state.v063Radieuse=MistralRadieuse.fresh();state.v064Mutuelle=MistralMutuelle.fresh();state.v065Notaires=MistralNotaires.fresh();
  const ra=(type,id,choice)=>{state=MistralRadieuse.apply(state,{type,id,choice},{local:true,near:true,point:['accept','finish'].includes(type)?'josiane':['vote','clause'].includes(type)?'assemblee':id});};
  ra('accept');for(const id of Object.keys(MistralRadieuse.EVIDENCE))ra('inspect',id);for(const p of MistralRadieuse.PEOPLE)ra('hear',p.id);for(const [k,v]of Object.entries({charges:'solidarite',representation:'lots',controle:'audit'}))ra('clause',k,v);ra('vote');for(const id of MistralRadieuse.WORKS)ra('repair',id);ra('finish');
  const ua=(type,id)=>{state=MistralMutuelle.apply(state,{type,id},{local:true,near:true,point:type==='evidence'?MistralMutuelle.EVIDENCE[id].point:type==='report'?'josiane':'expert'});};
  ua('open');for(const id of MistralMutuelle.IDS)ua('evidence',id);ua('argue','copies');ua('settle','forfait');if(reported)ua('report');
  state.v042.activeInterior=MistralRadieuse.SITE.id;state.v042.returnPoint=null;V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';return this.info();
 },
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v065NotairesInfo().points[id];state.player.pos=id==='desk'?[p[0]+2,p[1]+1.65,p[2]+1.4]:[p[0],p[1]+1.65,p[2]+2];state.player.yaw=Math.atan2(p[0]-state.player.pos[0],state.player.pos[2]-(p[2]+.7));state.player.pitch=-.2;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7])};},
 info(){__MISTRAL_DEBUG.v065NotairesInfo();return {ledger:state.v065Notaires,caps:state.player.caps,inv:state.inventory,old:JSON.stringify([state.v063Radieuse,state.v064Mutuelle,state.v060Council,state.v061Poste,state.v062Pharmacy]),notaries:world.npcs.filter(n=>n.id==='n65:notaire').length,door:world.colliders.filter(c=>c.v065Door&&!c.disabled).length,paper:world.staticDraws.filter(d=>d.v065Paper&&!d.hidden).length,receipts:world.staticDraws.filter(d=>d.v065ReceiptLabel&&!d.hidden).length};},
 snapshot(){return JSON.stringify(state);},
 restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';return this.info();},
 reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 fail(type,id){const original=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v065NotairesAction(type,id);}finally{saveGame=save;}return {result,same:original===JSON.stringify(state)};},
 remember(){globalThis.__N65_STALE=dialogueState.choices.find(c=>c.text.includes('Confirmer')).onChoose;},
 stale(){const before=JSON.stringify(state);globalThis.__N65_STALE();return before===JSON.stringify(state);},
 repeat(){for(let i=0;i<15;i++)collectDraws(gameClock);return {npc:world.npcs.filter(n=>n.id==='n65:notaire').length,desk:world.interactables.filter(i=>i.id==='n65:desk').length,vault:world.interactables.filter(i=>i.id==='n65:vault').length};},
 render(which='office'){
  for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}
  document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');mode='PLAYING';
  const c=which==='office'?{pos:[-1,2.4,23.4],target:[-4,1.1,16.5]}:{pos:[-1.4,5.4,-9.5],target:[-5,4.3,-14]};
  sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:59},currentEnv());return renderer.constructor.name;
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralNotaires' in html
html=html.replace(marker,bridge+'\n'+marker);checks=[];errors=[]
def check(name,ok):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7000)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v065NotairesInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2500)
  locked=page.evaluate('__N65_QA.setup(false)');check('no notary before Mutuelle receipt is delivered',locked['notaries']==0)
  start=page.evaluate('__N65_QA.setup(true)');check('one new notary after correct prerequisite',start['notaries']==1)
  old=start['old'];page.evaluate('__MISTRAL_DEBUG.v065NotairesOpen()');check('dedicated Pip-Boy chapter','Les clés ne font pas un titre' in page.locator('#pipboy').inner_text())
  page.screenshot(path=str(a.output/'01-notaires-desktop.png'));page.set_viewport_size({'width':390,'height':844});check('390px viewport has no page-wide overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-notaires-mobile.png'));page.set_viewport_size({'width':1280,'height':800});page.evaluate('__N65_QA.close()')
  def choose(text):
   print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected):
   data=page.evaluate('(id)=>__N65_QA.near(id)',id);print('NEAR',id,data,flush=True);check('reachable E interaction '+id,data['selected']==expected and not data['collision'] and data['los']);page.keyboard.press('e')
  go('notaire','npc:n65:notaire');choose('Ouvrir');check('accepted by real NPC button',page.evaluate('__N65_QA.info().ledger.opened'));choose('Revenir.')
  page.evaluate('__N65_QA.render()');page.screenshot(path=str(a.output/'03-notaire-hall.png'))
  go('desk','n65:desk');choose('Conserver une copie');choose('Revenir.')
  go('registre','r63:registre');check('original equipment and Mutuelle topics preserved',page.locator('#dialogueChoices button').filter(has_text='Mutuelle ·').count()==1);choose('Notaires ·');choose('Conserver une copie');choose('Revenir.')
  go('assurance','m64:dossier');choose('Notaires ·');choose('Conserver une copie');choose('Revenir.')
  for who in ['josiane','salome']:
   go(who,'npc:r63:'+who);choose('Notaires ·');choose('Consigner ce mandat');choose('Revenir.')
  check('three copies and both mandates persisted',page.evaluate('__N65_QA.info().ledger.readings.length===3&&__N65_QA.info().ledger.witnesses.length===2'))
  before_vault=page.evaluate('__N65_QA.snapshot()')
  go('vault','n65:vault');check('cabinet starts closed with solid door',page.evaluate('__N65_QA.info().door')==1)
  snapshot=page.evaluate('__N65_QA.info()');choose('Respecter l’ordre');check('wrong code preserves ledger inventory source and geometry',page.evaluate('__N65_QA.info()')==snapshot)
  for i,n in [(1,1),(2,2),(3,3)]:
   for _ in range(n):choose('Tourner le rouleau '+str(i))
  check('dials retain 76 48 86',page.evaluate('__N65_QA.info().ledger.dials')==['76','48','86'])
  fail=page.evaluate('__N65_QA.fail("unseal","sequence")');check('failed save leaves door closed and inventory unchanged',not fail['result'] and fail['same'] and page.evaluate('__N65_QA.info().door')==1)
  choose('Respecter l’ordre');check('cabinet door collision removed and original visible',page.evaluate('__N65_QA.info().door')==0 and page.evaluate('__N65_QA.info().paper')==1)
  choose('Revenir.');page.evaluate('__N65_QA.render("vault")');page.screenshot(path=str(a.output/'04-coffre-ouvert.png'))
  reopened=page.evaluate('__N65_QA.reload()');check('reload before pickup preserves open cabinet and paper',reopened['door']==0 and reopened['paper']==1 and not reopened['ledger']['original'])
  go('vault','n65:vault');choose('Prélever la minute');check('pickup removes physical original without creating saleable item',page.evaluate('__N65_QA.info().paper')==0 and page.evaluate('__N65_QA.info().ledger.original'));choose('Revenir.')
  before_decision=page.evaluate('__N65_QA.snapshot()')
  go('notaire','npc:n65:notaire');choose('Examiner : Convention');check('confirmation retains original roof exclusion','exclu du scrutin' in page.locator('#dialogueLine').inner_text());page.screenshot(path=str(a.output/'05-convention-et-exclusion.png'))
  page.evaluate('__N65_QA.remember()');failed=page.evaluate('__N65_QA.fail("decide","usage")');check('failed decision write changes no old source or new ledger',not failed['result'] and failed['same']);choose('Confirmer');check('stale confirmation rejected',page.evaluate('__N65_QA.stale()'));choose('Revenir.')
  check('insurance and prior vote untouched after new usage agreement',page.evaluate('__N65_QA.info().old')==old)
  for who in ['salome','josiane']:
   go(who,'npc:r63:'+who);choose('Notaires ·');choose('Remettre sa copie');choose('Revenir.')
  check('physical acknowledgment plaques visible at both recipients',page.evaluate('__N65_QA.info().receipts')==2)
  go('notaire','npc:n65:notaire');caps=page.evaluate('__N65_QA.info().caps');choose('Clore le registre');check('closure awards exactly 35 caps once',page.evaluate('__N65_QA.info().caps')==caps+35);choose('Revenir.')
  restored=page.evaluate('__N65_QA.reload()');check('reload preserves closed ledger and two recipients',restored['ledger']['closed'] and len(restored['ledger']['receipts'])==2 and restored['paper']==0)
  page.evaluate('__N65_QA.near("notaire")');check('repeat reward refused after reload',not page.evaluate('__MISTRAL_DEBUG.v065NotairesAction("close")'))
  check('no duplicated actor or interactions',page.evaluate('__N65_QA.repeat()')=={'npc':1,'desk':1,'vault':1})
  # All alternatives use the actual UI; fixtures only reset a previously played checkpoint.
  page.evaluate('(s)=>__N65_QA.restore(s)',before_decision);go('notaire','npc:n65:notaire');choose('Examiner : Répertoire');choose('Confirmer');choose('Revenir.');check('repertoire alternative persisted without rewriting sources',page.evaluate('__N65_QA.info().ledger.decision')=='repertoire' and page.evaluate('__N65_QA.info().old')==old)
  page.evaluate('(s)=>__N65_QA.restore(s)',before_vault);go('vault','n65:vault');scrap=page.evaluate('__N65_QA.info().inv.scrap');choose('Forcer la fermeture');choose('Prélever la minute');choose('Revenir.');check('forced opening costs two scrap and breaks verification',page.evaluate('__N65_QA.info().inv.scrap')==scrap-2 and not page.evaluate('__N65_QA.info().ledger.verified'))
  forced=page.evaluate('__N65_QA.snapshot()');go('notaire','npc:n65:notaire');choose('Examiner : Convention');choose('Confirmer');check('unverified original cannot generate usage act',page.evaluate('__N65_QA.info().ledger.decision') is None);choose('Examiner : Double garde');choose('Confirmer');choose('Revenir.');check('double custody remains available without more resources',page.evaluate('__N65_QA.info().ledger.decision')=='depot')
  page.evaluate('(s)=>__N65_QA.restore(s)',forced);go('notaire','npc:n65:notaire');cloth=page.evaluate('__N65_QA.info().inv.cloth');choose('Contre-vérifier');check('real cloth cost reestablishes documented verification',page.evaluate('__N65_QA.info().inv.cloth')==cloth-2 and page.evaluate('__N65_QA.info().ledger.verified'));choose('Examiner : Convention');choose('Confirmer');choose('Revenir.');check('verified forced route can reach usage agreement',page.evaluate('__N65_QA.info().ledger.decision')=='usage')
  page.evaluate('(s)=>__N65_QA.restore(s)',before_vault);go('vault','n65:vault');scrap=page.evaluate('__N65_QA.info().inv.scrap');choose('Déverrouiller le mécanisme');choose('Prélever la minute');choose('Revenir.');check('INT route costs one scrap and preserves seal verification',page.evaluate('__N65_QA.info().inv.scrap')==scrap-1 and page.evaluate('__N65_QA.info().ledger.verified'))
  check('no JavaScript exceptions on all tested routes',not errors)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Actual Radieuse interior, models, dialogue buttons, E inputs, save/load, visuals and collisions. Prerequisites through real quest reducers, scripted positions, isolated MemoryStorage. Software renderer; no human full-campaign or real IGN exterior validation.'}
  (a.output/'NOTAIRES_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',page.evaluate('window.__N65_QA?.info()'),flush=True);raise
 finally:browser.close()
