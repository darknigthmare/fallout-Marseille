"""Authored COCHONNET court, native dialogs/actions and persistence. Fixture-only
positions/aim, synthetic port, MemoryStorage and software rendering, not human QA.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/cochonnet/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
def get_bridge(path):
 t=ast.parse(path.read_text());return next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='bridge' for k in n.targets))
base_bridge=get_bridge(root/'tests/expansion/lys_browser_smoke.py')
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__B73_QA={
 setup(){__LYS_QA.setup();state.v073Boules=MistralBoules.fresh();state.inventory.fragGrenade=3;state.inventory.fragMine=2;state.v046.lore.petanque={played:4,wins:2};return this.port();},
 port(){__LYS_QA.port();const site=v042Site(MistralBoules.RELAY);state.v042.discovered[site.id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();const n=world.npcs[0];n.v042Site=site.id;V042_RUNTIME.npcData.set(n.id,{siteId:site.id,name:'Représentant du Vieux-Port',role:'artisan',index:0});globalThis.__LYS_PORT=world;globalThis.__LYS_POS=state.player.pos.slice();return __LYS_QA.focusPort();},
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v073BoulesInfo().points[id];state.player.pos=[p[0],1.65,p[2]+(id==='sortie'?-1:id==='cercle'?.1:2)];state.player.yaw=id==='sortie'?Math.PI:0;state.player.pitch=id==='cercle'?-1.2:-.18;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,1.65)};},
 info(){const clone=x=>JSON.parse(JSON.stringify(x));return {...__MISTRAL_DEBUG.v073BoulesInfo(),legacy:clone(state.v046.lore.petanque),inventory:clone(state.inventory),caps:state.player.caps,xp:state.player.xp,old:JSON.stringify([state.v072Rats,state.v071Cigales,state.v070Secours,state.v069Parts,state.v068Lys,state.v067Devoir,state.v066Voisins,state.v065Notaires,state.v064Mutuelle,state.v063Radieuse,state.v062Pharmacy,state.v061Poste,state.v060Council,state.v046.lore.done]),weapons:JSON.stringify({clip:state.player.ammoClip,reserve:state.player.ammoReserve,weapon:state.player.weaponId,condition:equipmentCondition('weapon',state.player.weaponId)}),pos:state.player.pos.slice(),zone:world.id};},
 snapshot(){return JSON.stringify(state);},save(){return saveGame(false);},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';inCombat=false;return this.info();},
 ticks(n){for(let i=0;i<n;i++)updateEnemies(.2);return this.info();},
 aim(yaw){state.player.yaw=yaw;state.player.pitch=-.18;},
 nativeThrow(){return fireWeapon();},held(n){V020.heldFire=true;try{for(let i=0;i<n;i++){v020TickCombat(.2);updateEnemies(.2);}}finally{V020.heldFire=false;}return this.info();},
 mode(m){mode=m;},
 fail(type,value){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;try{const result=__MISTRAL_DEBUG.v073BoulesAction(type,value);return{result,same:JSON.stringify(state)===before};}finally{saveGame=save;}},
 failResolution(){const save=saveGame;saveGame=()=>false;try{for(let i=0;i<100&&!__MISTRAL_DEBUG.v073BoulesInfo().paused;i++)updateEnemies(.2);return this.info();}finally{saveGame=save;}},
 failEntry(){const owner=state,w=world,before=JSON.stringify(state),save=saveGame;saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre le boulodrome')).onChoose();}finally{saveGame=save;}return state===owner&&world===w&&JSON.stringify(state)===before;},
 staleRemember(){globalThis.__B73_STALE=dialogueState.choices.find(c=>c.text.startsWith('Ouvrir la mène')).onChoose;},staleApply(){const before=JSON.stringify(state);__B73_STALE();return before===JSON.stringify(state);},
 render(which='court'){debugDismissDialogue();for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen','v35pTitle']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';updateQuestUI();updateHUD();const c=which==='measure'?{pos:[2.4,2.8,-3.8],target:[0,.1,-8]}:{pos:[6,6,7],target:[0,.3,-5]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:60},currentEnv());}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1
html=html.replace(marker,base_bridge+'\n'+bridge+'\n'+marker)
checks=[];errors=[]
def check(label,ok):
 assert ok,label
 checks.append(label);print('PASS',label,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(7000)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 def ev(s,arg=None):return page.evaluate(s,arg)
 def choose(text):print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
 def go(id,expected=None):
  r=ev('(id)=>__B73_QA.near(id)',id);print('NEAR',id,r,flush=True);check('physical interaction '+id,r['selected']==(expected or 'r73:'+id) and not r['collision']);page.keyboard.press('e')
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v073BoulesInfo');ev('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  check('existing port representative selected',ev('__B73_QA.setup()')=='npc:v042-npc:qa:lys');old=ev('__B73_QA.info().old');page.keyboard.press('e');check('old port conversation retained',page.locator('#dialogueChoices button').filter(has_text='Parler du secteur').count()==1);choose('COCHONNET · La cour');check('failed entry restores whole origin',ev('__B73_QA.failEntry()'));choose('Rejoindre le boulodrome');check('authored court loaded without accepting a quest',ev('__B73_QA.info().local'))
  ev('__B73_QA.render()');page.screenshot(path=str(a.output/'01-cour-cent-treves.png'))
  go('sortie');check('ordinary return reaches exact retained origin',ev('__LYS_QA.atOrigin()'));ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('COCHONNET · La cour');choose('Rejoindre le boulodrome')
  go('nelly','npc:r73:nelly');ev('__B73_QA.staleRemember()');check('failed start restores all campaign state',ev('__B73_QA.fail("start")')['same']);choose('Ouvrir la mène');check('stale start confirmation refused',ev('__B73_QA.staleApply()'));check('start did not consume inventory or caps',ev('__B73_QA.info().caps')==100 and ev('__B73_QA.info().legacy')=={'played':4,'wins':2})
  check('remote throw refuses without consuming a ball',ev('__B73_QA.nativeThrow()') is False and ev('__B73_QA.info().ledger.round.used.player')==0)
  go('cercle');choose('Force +1');check('native strength control applied',ev('__B73_QA.info().ledger.round.power')==35);choose('Tirer ·');check('native gesture control applied',ev('__B73_QA.info().ledger.round.style')=='tirer');choose('Revenir.');page.keyboard.press('r');check('native reload command changes gesture not ammunition',ev('__B73_QA.info().ledger.round.style')=='pointer')
  ev('__B73_QA.aim(-.035)');before=ev('__B73_QA.info()');check('failed throw restores exact state',ev('__B73_QA.fail("throw")')['same']);ev('__B73_QA.nativeThrow()');check('native shoot action launches one ball',ev('__B73_QA.info().ledger.round.used.player')==1);ev('__B73_QA.ticks(1)');check('ball visibly airborne after a tick',ev('__B73_QA.info().ledger.round.balls[0].p[1]')>.85)
  ev('__B73_QA.mode("PIP")');frozen=ev('__B73_QA.info().ledger');ev('__B73_QA.ticks(10)');check('menu pauses flight exactly',ev('__B73_QA.info().ledger')==frozen);ev('__B73_QA.mode("PLAYING")');ev('__B73_QA.save()');mid=ev('__B73_QA.info().ledger');ev('__B73_QA.reload()');check('native save reload restores flight position and velocity',ev('__B73_QA.info().ledger')==mid)
  paused=ev('__B73_QA.failResolution()');check('failed measurement pauses without counting a result',paused['paused'] and paused['ledger']['round']['phase']=='moving' and paused['ledger']['played']==0)
  go('nelly','npc:r73:nelly');choose('Retenter la sauvegarde');choose('Revenir.');check('retry restores progression',not ev('__B73_QA.info().paused'));ev('__B73_QA.ticks(100)');check('machine made a real throw with its own ball',ev('__B73_QA.info().ledger.round.used.house')>=1)
  used=ev('__B73_QA.info().ledger.round.used.player');ev('__B73_QA.near("cercle")');ev('__B73_QA.held(150)');check('holding shoot cannot auto-play the next player turn',ev('__B73_QA.info().ledger.round.used.player')==used)
  inv=ev('__B73_QA.info().inventory');page.keyboard.press('n');page.keyboard.press('p');check('direct grenade action respects the truce',ev('__MISTRAL_DEBUG.v055OrdnanceThrow()') is False);check('direct mine action respects the truce',ev('__MISTRAL_DEBUG.v056MinesPlace()') is False);check('native grenade and mine inputs respect the truce',ev('__B73_QA.info().inventory')==inv and ev('__MISTRAL_DEBUG.getState().v055Ordnance.armed') is None and len(ev('__MISTRAL_DEBUG.getState().v056Mines.mines'))==0)
  for _ in range(6):
   info=ev('__B73_QA.info()');r=info['ledger']['round']
   if r['phase']=='result':break
   if r['phase']=='aim' and r['turn']=='player':
    ev('__B73_QA.near("cercle")');ev('__B73_QA.aim(-.035)');ev('__MISTRAL_DEBUG.v073BoulesAction("configure",{style:"pointer",power:34})');ev('__B73_QA.nativeThrow()')
   ev('__B73_QA.ticks(150)')
  done=ev('__B73_QA.info()');print('RESULT',done['ledger'],flush=True);check('full physical exhibition reaches a measured result',done['ledger']['round']['phase']=='result' and done['ledger']['played']==1)
  check('legacy counters increment once without clearing old quests',done['legacy']['played']==5 and done['legacy']['wins']==2+done['ledger']['wins'] and done['old']==old)
  check('no capsules, inventory, ammunition or weapon modification',done['xp']==before['xp'] and done['caps']==before['caps'] and done['inventory']==before['inventory'] and done['weapons']==before['weapons'])
  ev('__B73_QA.render("measure")');page.screenshot(path=str(a.output/'02-mesure-des-boules.png'))
  ev('__B73_QA.reload()');check('result and old counters survive reload without duplicate credit',ev('__B73_QA.info().ledger')==done['ledger'] and ev('__B73_QA.info().legacy')==done['legacy']);ev('__B73_QA.ticks(100)');check('finished simulation cannot give a second victory',ev('__B73_QA.info().legacy')==done['legacy'])
  ev('__MISTRAL_DEBUG.v073BoulesOpen()');check('Pip-Boy shows actual measured distances','Mesures entre centres' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'03-feuille-de-mene.png'));page.set_viewport_size({'width':390,'height':844});check('mobile 390px without horizontal overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'04-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
  go('nelly','npc:r73:nelly');choose('Commencer une autre');check('new round retains wins and resets only its own spheres',ev('__B73_QA.info().ledger.round.number')==2 and ev('__B73_QA.info().ledger.round.used')=={'player':0,'house':0} and ev('__B73_QA.info().legacy')==done['legacy'])
  ev('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(500);check('native new campaign inherits no boule board or wins',ev('__MISTRAL_DEBUG.v073BoulesInfo().ledger.round') is None and ev('__MISTRAL_DEBUG.v073BoulesInfo().ledger.played')==0)
  check('no JS exceptions or adapter failure',not errors and ev('__B73_QA.info().error') is None)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
  (a.output/'COCHONNET_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',ev('window.__B73_QA?.info()'),flush=True);raise
 finally:browser.close()
