"""Instrumented rescue: real authored annexe, E/UI, native hazard and collision
functions and continuous escort update. Synthetic ports, scripted leader positions,
isolated MemoryStorage and software renderer; not a human IGN campaign."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/secours/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
source=ast.parse((root/'tests/expansion/lys_browser_smoke.py').read_text())
base_bridge=next(ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
const __S70_NATIVE_PLAYER=updatePlayer;
globalThis.__S70_QA={
 setup(index=0){__LYS_QA.setup();state.v070Secours=MistralSecours.fresh();return __LYS_QA.port(index);},
 info(){return {ledger:state.v070Secours,local:!!world.v070Secours,npcs:world.npcs.filter(n=>n.id.startsWith('s70:')).map(n=>({id:n.id,pos:n.pos.slice(),moving:n.moving})),hazards:world.hazards.filter(h=>h.id.startsWith('s70:')).map(h=>h.id),doors:world.colliders.filter(c=>c.s70Door&&!c.disabled).map(c=>c.s70Door),fires:world.staticDraws.filter(d=>d.s70Fire&&!d.hidden).length,safe:world.staticDraws.filter(d=>d.s70Safe&&!d.hidden).length,caps:state.player.caps,inv:state.inventory,old:JSON.stringify([state.v060Council,state.v061Poste,state.v062Pharmacy,state.v063Radieuse,state.v064Mutuelle,state.v065Notaires,state.v066Voisins,state.v067Devoir,state.v068Lys,state.v069Parts]),error:__MISTRAL_DEBUG.v070SecoursInfo().error,blocked:__MISTRAL_DEBUG.v070SecoursInfo().saveBlocked};},
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v070SecoursInfo().points[id];state.player.pos=[p[0],p[1]+1.65,p[2]+2];state.player.yaw=0;state.player.pitch=-.18;mode='PLAYING';onGround=true;updateSelectedInteractable();return{selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7])};},
 snapshot(){return JSON.stringify(state);},save(){return saveGame(false);},
 restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';return this.info();},
 reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 lead(id,dt=.2){const l=state.v070Secours.people[id],end=MistralSecours.length(id);let p=MistralSecours.position(id,Math.min(end,l.progress+2500));if(l.progress+2500>=end){p[0]+=id==='lila'?2.5:-2.5;}state.player.pos=[p[0],p[1]+1.65,p[2]];mode='PLAYING';onGround=true;updateNPCSchedules(dt);return state.v070Secours.people[id];},
 steps(id,n=1){for(let i=0;i<n;i++)this.lead(id);return this.info();},
 complete(id){let i=0;while(state.v070Secours.people[id].mode==='following'&&i++<900)this.lead(id);return {ticks:i,mode:state.v070Secours.people[id].mode,progress:state.v070Secours.people[id].progress};},
 blockedTick(id,reason){const before=state.v070Secours.people[id].progress,p=MistralSecours.position(id,before);state.player.pos=[p[0],1.65,p[2]+3];mode='PLAYING';let temp=null;
  if(reason==='distance')state.player.pos[0]+=10;if(reason==='behind')state.player.pos[2]=p[2]-2;if(reason==='menu')mode='PIP';
  if(reason==='sight'||reason==='collision'){temp=addCollider(world,p[0],p[2]+(reason==='sight'?1.5:.3),2,.15,{minY:0,maxY:reason==='sight'?3:.65});}
  updateNPCSchedules(.2);if(temp)world.colliders=world.colliders.filter(c=>c!==temp);mode='PLAYING';return before===state.v070Secours.people[id].progress;
 },
 failTick(id){const p=MistralSecours.position(id,state.v070Secours.people[id].progress+2500);state.player.pos=[p[0],1.65,p[2]];mode='PLAYING';const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;try{updateNPCSchedules(.2);}finally{saveGame=save;}return {same:before===JSON.stringify(state),blocked:__MISTRAL_DEBUG.v070SecoursInfo().saveBlocked};},
 fail(type,id){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v070SecoursAction(type,id);}finally{saveGame=save;}return {result,same:before===JSON.stringify(state)};},
 failBoard(){const before=JSON.stringify(state),scene=world,save=saveGame;saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre les')).onChoose();}finally{saveGame=save;}return world===scene&&before===JSON.stringify(state);},
 hazard(){const hp=state.player.hp;state.status.burning=0;state.status.smoke=0;state.player.pos=[2.3,1.65,0];mode='PLAYING';onGround=true;__S70_NATIVE_PLAYER(.1);const result={hpLost:hp-state.player.hp,burning:state.status.burning,smoke:state.status.smoke};state.player.hp=hp;state.status.burning=0;state.status.smoke=0;return result;},
 pauseExitFailure(){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=v042ExitInstance();}finally{saveGame=save;}return {same:before===JSON.stringify(state),result};},
 render(which='fire'){for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';const c=which==='fire'?{pos:[8,3.7,23],target:[0,1.8,-3]}:which==='escort'?{pos:[-8,2.7,10],target:[-14,1.4,-1]}:{pos:[0,3,29],target:[0,1.3,20]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:64},currentEnv());return renderer.constructor.name;}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralSecours' in html
html=html.replace(marker,base_bridge+'\n'+bridge+'\n'+marker);checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7500)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v070SecoursInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  def ev(s,arg=None):return page.evaluate(s,arg)
  def choose(text):print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected=None):
   d=ev('(id)=>__S70_QA.near(id)',id);print('NEAR',id,d,flush=True);check('reachable E contact '+id,d['selected']==(expected or 's70:'+id) and not d['collision'] and d['los']);page.keyboard.press('e')
  def embark():
   ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Secours de la Rade');choose('Rejoindre les Marins-Sapeurs')
  ev('__S70_QA.setup()');old=ev('__S70_QA.info().old');page.keyboard.press('e');check('independent rescue available before Lys and old port topics kept',page.locator('#dialogueChoices button').filter(has_text='Secours de la Rade').count()==1 and page.locator('#dialogueChoices button').filter(has_text='Passage maritime').count()==1)
  choose('Secours de la Rade');check('boarding rollback on refused save',ev('__S70_QA.failBoard()'));choose('Rejoindre les Marins-Sapeurs')
  check('new annexe with three actual actors and separate hazards',ev('__S70_QA.info().local') and len(ev('__S70_QA.info().npcs'))==3 and len(ev('__S70_QA.info().hazards'))==3)
  page.evaluate('__MISTRAL_DEBUG.v070SecoursOpen()');check('dedicated Pip-Boy chapter','Les vivants derrière la porte' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-pipboy-desktop.png'));page.set_viewport_size({'width':390,'height':844});check('390px no page-wide overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-pipboy-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
  ev('__S70_QA.render()');page.screenshot(path=str(a.output/'03-annexe-avant-extinction.png'))
  check('native fire hazard damages player and applies burning',ev('__S70_QA.hazard().hpLost')>0)
  go('farah','npc:s70:farah');choose('Prendre en charge');choose('Revenir.');go('console');choose('Lire les repères');choose('Revenir.');briefed=ev('__S70_QA.snapshot()')
  check('closed compartment stops native collision walk',ev('__LYS_QA.walk([[-14,1.65,-5],[-14,1.65,-19]])')[0][2]>-10)
  go('lance');before=ev('__S70_QA.info().ledger');choose('Actionner le dispositif manuel');check('unsafe discharge rejected without changing state',ev('__S70_QA.info().ledger')==before);choose('Revenir.')
  go('power');choose('Isoler le courant');choose('Revenir.');check('electric hazard removed separately',len(ev('__S70_QA.info().hazards'))==2)
  go('fuel');choose('Fermer l’alimentation');choose('Revenir.');go('lance');f=ev('__S70_QA.fail("extinguish","manuel")');check('refused storage preserves fire and resources',f['same'] and not f['result'] and ev('__S70_QA.info().fires')==5);choose('Actionner le dispositif manuel');choose('Revenir.')
  check('fire smoke and electric hazard actually removed',ev('__S70_QA.info().hazards')==[] and ev('__S70_QA.info().fires')==0)
  check('native hazard update no longer causes new fire damage',ev('__S70_QA.hazard().hpLost')==0)
  for id in ['lila','remi']:go('door:'+id);choose('Ouvrir cette issue');choose('Revenir.')
  for x in [-14,14]:
   check('opened corridor traversable both directions '+str(x),ev('(x)=>__LYS_QA.walk([[x,1.65,-5],[x,1.65,-24],[x,1.65,9]])',x)[-1][2]>8.8)
  released=ev('__S70_QA.snapshot()');go('remi','npc:s70:remi');check('conscious ghoul has a human rescue dialogue','goule' in page.locator('#dialogueLine').inner_text().lower() or 'teint' in page.locator('#dialogueLine').inner_text());choose('Revenir.')
  go('lila','npc:s70:lila');choose('Suivez-moi');
  for reason in ['distance','behind','menu','sight','collision']:check('escort waits for '+reason,ev('(r)=>__S70_QA.blockedTick("lila",r)',reason))
  ev('__S70_QA.steps("lila",10)');check('actual NPC moves gradually not directly to muster',ev('__S70_QA.info().ledger.people.lila.progress')==2400 and ev('__S70_QA.info().ledger.people.lila.mode')=='following')
  paused=ev('__S70_QA.pauseExitFailure()');check('failed pause save refuses exit without losing escort',paused['same'] and not paused['result'])
  go('sortie');check('leaving pauses the person and restores retained exterior',ev('__LYS_QA.atOrigin()') and ev('__S70_QA.info().ledger.people.lila.mode')=='waiting');embark();check('revisit preserves exact waiting position',ev('__S70_QA.info().ledger.people.lila.progress')==2400)
  go('lila','npc:s70:lila');choose('Suivez-moi');ev('__S70_QA.steps("lila",43)');check('escort reaches pre-corner without skipping checkpoint',ev('__S70_QA.info().ledger.people.lila.progress')==12720)
  ev('__S70_QA.steps("lila",1)');failed=ev('__S70_QA.failTick("lila")');check('checkpoint save refusal rolls movement back and pauses adapter',failed['same'] and failed['blocked']=='lila')
  go('lila','npc:s70:lila');choose('Attendre ici');choose('Revenir.');go('lila','npc:s70:lila');choose('Suivez-moi');ev('__S70_QA.steps("lila",5)');ev('__S70_QA.save()')
  before=ev('__S70_QA.info().ledger.people.lila.progress');ev('__S70_QA.reload()');check('real save reload resumes mid-corridor not at original room',ev('__S70_QA.info().ledger.people.lila.progress')==before)
  ev('__S70_QA.steps("lila",20)');ev('__S70_QA.render("escort")');page.screenshot(path=str(a.output/'04-accompagnement-en-cours.png'))
  res=ev('__S70_QA.complete("lila")');check('Lila arrives only after walking full route',res['mode']=='safe' and res['progress']==51000 and res['ticks']<900)
  go('farah','npc:s70:farah');check('one arrival insufficient for reward',page.locator('#dialogueChoices button').filter(has_text='Confirmer les deux').count()==0);choose('Revenir.')
  go('remi','npc:s70:remi');choose('Suivez-moi');res=ev('__S70_QA.complete("remi")');check('ghoul walks same safe-rescue conditions',res['mode']=='safe' and res['progress']==51000)
  check('two actual people remain at muster with visible reception markers',ev('__S70_QA.info().safe')==2 and ev('__S70_QA.info().ledger.order')==['lila','remi'])
  go('farah','npc:s70:farah');caps=ev('__S70_QA.info().caps');f=ev('__S70_QA.fail("finish")');check('reward rollback preserves completed evacuation',f['same'] and not f['result']);choose('Confirmer les deux');choose('Revenir.');check('exact one-time sixty-caps reward',ev('__S70_QA.info().caps')==caps+60)
  ev('__S70_QA.reload()');check('closure and hazards stay resolved on real reload',ev('__S70_QA.info().ledger.finished') and ev('__S70_QA.info().hazards')==[] and ev('__S70_QA.info().safe')==2)
  check('prior Lys cargo and institutional records unchanged',ev('__S70_QA.info().old')==old)
  ev('__S70_QA.render("muster")');page.screenshot(path=str(a.output/'05-deux-personnes-au-rassemblement.png'))
  go('farah','npc:s70:farah');check('completed reward absent after reload',page.locator('#dialogueChoices button').filter(has_text='Confirmer les deux').count()==0);choose('Revenir.')
  # Alternate technical route and reversed escort order on the same actual scene.
  ev('(s)=>__S70_QA.restore(s)',briefed);go('lance');n=ev('__S70_QA.info().inv.circuitry');choose('Commande technique');choose('Revenir.');check('technical discharge costs one circuit exactly',ev('__S70_QA.info().inv.circuitry')==n-1 and ev('__S70_QA.info().hazards')==[])
  for id in ['remi','lila']:go('door:'+id);choose('Ouvrir cette issue');choose('Revenir.');go(id,'npc:s70:'+id);choose('Suivez-moi');check('reverse order arrival '+id,ev('(id)=>__S70_QA.complete(id).mode',id)=='safe')
  go('farah','npc:s70:farah');choose('Confirmer les deux');choose('Revenir.');check('reverse order persists without moral penalty',ev('__S70_QA.info().ledger.order')==['remi','lila'])
  ev('__S70_QA.setup(1)');embark();go('sortie');check('Ratonneau return works with no prior campaign completion',ev('__LYS_QA.atOrigin()'))
  check('no JavaScript or adapter errors',not errors and not ev('__S70_QA.info().error'))
 finally:
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
  (a.output/'SECOURS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));browser.close()
