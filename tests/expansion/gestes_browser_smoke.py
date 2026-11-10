"""Native consignment handoff choices and recognition gestures on the production bundle.
Scripted positions, synthetic Vieux-Port and MemoryStorage. Rendered native people,
actual callbacks/save rollback and software WebGL; not a human or IGN traversal test.
"""
from pathlib import Path
import argparse, ast, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/gestes/browser')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest()
def extract(name):
 tree=ast.parse((root/'tests/expansion'/name).read_text())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
bridge=r'''
globalThis.__G75_QA={
 clock:0,
 choiceCount(){return dialogueState.choices.filter(c=>c.v075Gesture).length;},
 startClock(){this.clock=gameClock;return __MISTRAL_DEBUG.v075GesturesInfo();},
 advance(ms){let left=ms;while(left>0){const d=Math.min(50,left);this.clock+=d/1000;collectDraws(this.clock);left-=d;}return this.info();},
 info(){const d=collectDraws(this.clock);return{...__MISTRAL_DEBUG.v075GesturesInfo(),objects:[...new Set(d.filter(x=>x.v075Object).map(x=>x.v075Object))],parts:d.filter(x=>x.v075Object).map(x=>({id:x.v075Object,pos:x.pos,mesh:x.mesh})),hands:d.filter(x=>x.v075Hand).length,arms:d.filter(x=>x.v075Arm).length,cord:d.filter(x=>x.v075Cord).length,marker:getObjectiveMarker(),title:$('questTitle').textContent,objective:$('questObjective').textContent};},
 failChoice(){const old=saveGame,before=JSON.stringify(state);saveGame=()=>false;try{dialogueState.choices.find(c=>c.v075Gesture).onChoose();}finally{saveGame=old;}return {same:JSON.stringify(state)===before,active:__MISTRAL_DEBUG.v075GesturesInfo().active};},
 remember(){globalThis.__G75_STALE=dialogueState.choices.find(c=>c.v075Gesture).onChoose;},
 stale(){const before=JSON.stringify(state);__G75_STALE();return JSON.stringify(state)===before;},
 mode(value){mode=value;},
 reduced(value){settings.reduceMotion=value;},
 draw(key){
  for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=$(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}
  $('questFlash').style.display='none';$('toastStack')?.replaceChildren();$('interactPrompt').classList.add('hidden');
  const n=world.npcs.find(n=>n.id==='g73:owner:'+key),pos=[n.pos[0]+1.15,1.9,n.pos[2]-2.35],target=[n.pos[0],1.08,n.pos[2]-.08];
  sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(this.clock),{pos,dir:vNorm(vSub(target,pos)),fov:54},currentEnv());
  return this.info();
 },
 snapshot(){return JSON.stringify(state);},
 save(){saveGame(false);return this.snapshot();}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
html=production.decode();assert html.count(marker)==1
html=html.replace(marker,'\n'.join(extract(n) for n in ['lys_browser_smoke.py','gabians_browser_smoke.py','retrouvailles_browser_smoke.py'])+'\n'+bridge+'\n'+marker)
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
checks=[];errors=[]
def check(name,ok):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(10000)
 page.on('pageerror',lambda e:errors.append(e.stack))
 def ev(s,arg=None):return page.evaluate(s,arg)
 def choose(text):page.locator('#dialogueChoices button').filter(has_text=text).click()
 def owner(key):
  selected=ev('(k)=>__OWNERS_QA.near(k)',key)
  check('native E targets '+key,selected['selected']=='npc:g73:owner:'+key and not selected['collision'])
  page.keyboard.press('e')
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v075GesturesInfo')
  ev('__MISTRAL_DEBUG.startStory()');page.wait_for_function('__MISTRAL_DEBUG.getState().v035.prologue.titleSeen && document.getElementById("v35pTitle").classList.contains("hidden")')
  ev('__G73_QA.setup()');page.keyboard.press('e');choose('Consigne ·');choose('Rejoindre la consigne')
  ev('__G73_QA.render()');initial=ev('__OWNERS_QA.prepare()');old=ev('__OWNERS_QA.info().old')
  owner('clef');check('native handoff choice decorated once',ev('__G75_QA.choiceCount()')==1)
  failed=ev('__G75_QA.failChoice()');check('failed native save does not move ledger or start gesture',failed['same'] and not failed['active'])
  ev('__G75_QA.remember()');choose('Remettre en main propre');info=ev('__G75_QA.startClock()')
  check('successful direct handoff starts key gesture',len(info['active'])==1 and info['active'][0]['id']=='clef')
  check('stale handoff changes no state',ev('__G75_QA.stale()'))
  snap=ev('__G75_QA.snapshot()');info=ev('__G75_QA.advance(800)')
  check('recognition pose replaces native right arm',info['hands']==1 and info['arms']==12 and info['active'][0]['phase']=='recognise')
  check('key silhouette is distinct',len([p for p in info['parts'] if p['id']=='clef'])==15)
  ev('__G75_QA.draw("clef")');page.screenshot(path=str(a.output/'01-eloi-clef-reconnue.png'))
  info2=ev('__G75_QA.info()');check('extra render does not advance animation',info2['active']==info['active'])
  ev('__G75_QA.mode("PIP")');paused=ev('__G75_QA.advance(500)');check('Pip-Boy pauses gesture',paused['active']==info['active'])
  ev('__G75_QA.mode("DIALOGUE")');ev('__G75_QA.advance(100)');check('dialogue keeps gesture visible',ev('__G75_QA.info().active[0].ms')>info['active'][0]['ms'])
  check('rendering and pause do not write gameplay state',ev('__G75_QA.snapshot()')==snap)
  ev('__G75_QA.save()');ev('__G73_QA.reload()');info=ev('__G75_QA.startClock()');check('mid-gesture reload does not replay a receipt',not info['active'])
  info=ev('__G75_QA.info()');check('received key retained visually after load','clef' in info['objects'] and info['hands']==0)
  ev('__G75_QA.draw("clef")');page.screenshot(path=str(a.output/'02-eloi-clef-conservee.png'))
  ev('__G73_QA.run("return","bague")');owner('bague');choose('Passer depuis le comptoir');ev('__G75_QA.startClock()');info=ev('__G75_QA.advance(1000)')
  check('counter handoff uses same native receipt with ring gesture',ev('__G73_QA.info().ledger.handoffs.bague')=='consigne' and any(x['id']=='bague' for x in info['active']))
  check('ring is a circular separate silhouette',len([p for p in info['parts'] if p['id']=='bague'])==12)
  ev('__G75_QA.draw("bague")');page.screenshot(path=str(a.output/'03-mina-gravure.png'))
  info=ev('__G75_QA.advance(2000)');check('ring settles on hand and animated limb returns to native rig',not info['active'] and info['hands']==0 and 'bague' in info['objects'])
  ev('__G75_QA.draw("bague")');page.screenshot(path=str(a.output/'04-mina-bague-remise.png'))
  owner('sifflet');choose('Remettre en main propre');ev('__G75_QA.startClock()');info=ev('__G75_QA.advance(800)')
  check('whistle recognised before neck cord appears',info['hands']==1 and info['cord']==0 and len([p for p in info['parts'] if p['id']=='sifflet'])==3)
  ev('__G75_QA.draw("sifflet")');page.screenshot(path=str(a.output/'05-rachid-sifflet.png'))
  info=ev('__G75_QA.advance(2200)');check('whistle remains on its neck cord',info['cord']==18 and not info['active'])
  ev('__G75_QA.draw("sifflet")');page.screenshot(path=str(a.output/'06-rachid-cordon.png'))
  check('three distinct received objects and no extra person',set(info['objects'])=={'clef','bague','sifflet'} and len(ev('__OWNERS_QA.info().people'))==4)
  snap=ev('__G75_QA.snapshot()');counts=ev('[__G75_QA.info().parts.length,__G75_QA.info().cord]')
  for _ in range(5):check('repeat render stable '+str(_),ev('[__G75_QA.info().parts.length,__G75_QA.info().cord]')==counts)
  check('no extra payment or inventory item',ev('__G73_QA.info().caps')==json.loads(initial)['player']['caps'] and ev('__G73_QA.info().inv')==json.loads(initial)['inventory'])
  ev('__G73_QA.run("finish")');info=ev('__G75_QA.info()')
  check('completed HUD and marker send player to actual exit','TERMINÉ' in info['title'] and 'Retour au Vieux-Port' in info['marker']['label'] and info['marker']['pos']==[0,1.25,28.4])
  check('only historical prime paid',ev('__G73_QA.info().caps')==json.loads(initial)['player']['caps']+45)
  ev('__G75_QA.save()');ev('__G73_QA.reload()');ev('__G75_QA.startClock()');info=ev('__G75_QA.info()')
  check('all accessories rebuilt from saved handoffs, no replay',len(info['objects'])==3 and not info['active'] and info['cord']==18)
  check('other thirteen quest ledgers untouched',ev('__OWNERS_QA.info().old')==old)
  # Reduced motion reuses the ordinary player setting; no developer menu is added.
  ev('(s)=>__G73_QA.restore(s)',initial);ev('__G75_QA.reduced(true)');owner('clef');choose('Remettre en main propre');ev('__G75_QA.startClock()');info=ev('__G75_QA.info()')
  check('reduced motion directly shows kept key, no animated arm',not info['active'] and 'clef' in info['objects'] and info['hands']==0)
  ev('__G75_QA.reduced(false)');owner('bague');choose('Remettre en main propre');ev('__G75_QA.startClock()');ev('__G75_QA.advance(500)');ev('__G75_QA.reduced(true)');info=ev('__G75_QA.info()')
  check('enabling reduced motion mid-gesture ends animation without losing object',not info['active'] and 'bague' in info['objects'])
  check('no JavaScript exceptions',not errors)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
  (a.output/'GESTES_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('ERRORS',errors,flush=True);print('STATE',ev('window.__MISTRAL_DEBUG?.v075GesturesInfo()'),flush=True);raise
 finally:browser.close()
