"""La part des absents: real authored scene/UI/E/collision, isolated MemoryStorage.
Prior audience prepared through its real reducer; synthetic ports are shared with
lys_browser_smoke. This is not human playtesting or an IGN maritime traversal.
"""
from pathlib import Path
import argparse, ast, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/parts/browser')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
# Reuse the existing exact synthetic port fixture, not a new fake world contract.
tree=ast.parse((root/'tests/expansion/lys_browser_smoke.py').read_text())
base_bridge=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__PARTS_QA={
 setup(policy='serment',port=0){
  __LYS_QA.setup();let s=state;
  const step=(type,id,answer)=>s=MistralLys.apply(s,{type,id,answer},{local:true,near:true,point:MistralLys.point(type,id)});
  step('open');for(const id of MistralLys.VOICES)step('hear',id);step('read','vivres');step('read','accueil');step('gate','service');step('read','programme');step('decide',policy);for(const id of MistralLys.VOICES)step('notify',id);step('finish');state=s;state.v069Parts=MistralParts.fresh();v049Own(world);return __LYS_QA.port(port);
 },
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v069PartsInfo().points[id],d=id.startsWith('dest:')?3:2;state.player.pos=[p[0],p[1]+1.65,p[2]+d];state.player.yaw=0;state.player.pitch=-.18;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.9])};},
 info(){const l=state.v069Parts;return {ledger:l,caps:state.player.caps,inv:state.inventory,old:JSON.stringify([state.v068Lys,state.v060Council,state.v061Poste,state.v062Pharmacy,state.v063Radieuse,state.v064Mutuelle,state.v065Notaires,state.v066Voisins,state.v067Devoir]),local:!!world.v069Parts,npcs:world.npcs.length,gate:world.colliders.filter(c=>c.partsGate&&!c.disabled).length,racked:world.colliders.filter(c=>c.partsCrate&&!c.disabled).length,delivered:world.colliders.filter(c=>c.partsDelivered&&!c.disabled).length,carried:collectDraws(gameClock).filter(d=>d.partsHeld).length,error:__MISTRAL_DEBUG.v069PartsInfo().error};},
 snapshot(){return JSON.stringify(state);},
 restore(s){debugDismissDialogue();state=migrateState(JSON.parse(s));state.v042.activeInterior=MistralParts.SITE_ID;loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';return this.info();},
 reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 fail(type,id,throws=false){const before=JSON.stringify(state),w=world,save=saveGame;saveGame=()=>{if(throws)throw Error('QA storage error');return false;};let r;try{r=__MISTRAL_DEBUG.v069PartsAction(type,id);}finally{saveGame=save;}return {result:r,same:JSON.stringify(state)===before,world:world===w};},
 failBoard(){const save=saveGame,before=JSON.stringify(state),w=world;saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre le déchargement')).onChoose();}finally{saveGame=save;}return world===w&&JSON.stringify(state)===before;},
 remember(){globalThis.__PARTS_STALE=dialogueState.choices.find(c=>c.text.startsWith('Confirmer')).onChoose;},
 stale(){const before=JSON.stringify(state);__PARTS_STALE();return JSON.stringify(state)===before;},
 blocked(type,id,kind){const before=JSON.stringify(state),old={lab:V046.lab,busy:V046.busy,combat:inCombat,ground:onGround};if(kind==='lab')V046.lab=true;if(kind==='loading')V046.busy=true;if(kind==='combat')inCombat=true;if(kind==='air')onGround=false;let r;try{r=__MISTRAL_DEBUG.v069PartsAction(type,id);}finally{V046.lab=old.lab;V046.busy=old.busy;inCombat=old.combat;onGround=old.ground;}return r===false&&JSON.stringify(state)===before;},
 exitAny(){return v042ExitInstance();},returnSaved(){return JSON.stringify(state.v042.returnPoint.pos)===JSON.stringify(__LYS_POS)&&state.v042.returnPoint.macro===__LYS_PORT.id;},
 render(){for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';const c={pos:[19,8,27],target:[-2,1,-8]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:66},currentEnv());}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1
html=html.replace(marker,base_bridge+'\n'+bridge+'\n'+marker)
checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7500)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v069PartsInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  def ev(s,arg=None):return page.evaluate(s,arg)
  def choose(text):print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected=None):
   d=ev('(id)=>__PARTS_QA.near(id)',id);print('NEAR',id,d,flush=True);check('physical E contact '+id,d['selected']==(expected or 'parts69:'+id) and d['los'] and not d['collision']);page.keyboard.press('e')
  def embark():
   ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Ravitaillement du Lys');choose('Rejoindre le déchargement')
  ev('__LYS_QA.setup()');page.keyboard.press('e');check('new cargo topic absent before actual Lys closure',page.locator('#dialogueChoices button').filter(has_text='Ravitaillement du Lys').count()==0)
  ev('__PARTS_QA.setup("commune")');old=ev('__PARTS_QA.info().old');page.keyboard.press('e');check('old sector and Lys passage topics remain',page.locator('#dialogueChoices button').filter(has_text='Parler du secteur').count()==1 and page.locator('#dialogueChoices button').filter(has_text='Passage maritime').count()==1);choose('Ravitaillement du Lys');check('failed save cancels departure and preserves source',ev('__PARTS_QA.failBoard()'));choose('Rejoindre le déchargement')
  check('actual new authored yard has three actors and six racked crates',ev('__PARTS_QA.info().local&&__PARTS_QA.info().npcs===3&&__PARTS_QA.info().racked===6'))
  ev('__MISTRAL_DEBUG.v069PartsOpen()');check('Pip-Boy respects original communal outcome','déjà guide' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-pipboy-desktop.png'));page.set_viewport_size({'width':390,'height':844});check('390px no page-wide overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-pipboy-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()');ev('__PARTS_QA.render()');page.screenshot(path=str(a.output/'03-quai-ferme.png'))
  go('maelle','npc:parts69:maelle');choose('Aider au déchargement');choose('Revenir.');check('opened without changing previous history',ev('__PARTS_QA.info().old')==old)
  go('notice');choose('Examiner la consigne');choose('Revenir.')
  for actor in ['nora','eloi']:go(actor,'npc:parts69:'+actor);choose('Écouter sa position');choose('Revenir.')
  check('closed barrier stops native walk',ev('__LYS_QA.walk([[0,1.65,3],[0,1.65,-9]])')[0][2]>-3)
  go('babord');choose('Sécuriser cette amarre');choose('Revenir.')
  go('treuil');before=ev('__PARTS_QA.info()');choose('Abaisser la barrière');after=ev('__PARTS_QA.info()');check('one mooring cannot lower barrier or consume state',all(after[k]==before[k] for k in ['ledger','caps','inv','old','gate','racked','delivered']));choose('Revenir.')
  go('tribord');choose('Sécuriser cette amarre');choose('Revenir.')
  go('treuil');check('failed storage leaves gate physically closed',ev('__PARTS_QA.fail("gate","manuel").same') and ev('__PARTS_QA.info().gate')>0);choose('Abaisser la barrière');choose('Revenir.')
  check('native crossing now passes the exact former barrier',ev('__LYS_QA.walk([[0,1.65,3],[0,1.65,-9]])')[0][2]<-8.8)
  check('reverse crossing also passes',ev('__LYS_QA.walk([[0,1.65,-9],[0,1.65,3]])')[0][2]>2.8)
  ready=ev('__PARTS_QA.snapshot()')
  go('maelle','npc:parts69:maelle');choose('Examiner : La part des naufragés');check('confirmation explains actual quota and no political oath','Aucun bénéficiaire ne prête serment' in page.locator('#dialogueLine').inner_text());ev('__PARTS_QA.remember()');check('failed plan save changes nothing',ev('__PARTS_QA.fail("plan","secours").same'));choose('Confirmer cette répartition');check('stale plan confirmation refused',ev('__PARTS_QA.stale()'));choose('Revenir.')
  planned=ev('__PARTS_QA.snapshot()');inv=ev('__PARTS_QA.info().inv');caps=ev('__PARTS_QA.info().caps')
  go('crate:A');check('one crate really removed from rack and carried visually',ev('__PARTS_QA.info().racked===5&&__PARTS_QA.info().carried===1'))
  go('crate:B');check('second pickup cannot duplicate cargo',ev('__PARTS_QA.info().ledger.crates.A==="held"&&__PARTS_QA.info().ledger.crates.B==="rack"'))
  check('all native exits refuse carried cargo',ev('__PARTS_QA.exitAny()') is False)
  go('sortie');check('physical exit also keeps the carried crate inside',ev('__PARTS_QA.info().local'))
  go('crate:A');go('sortie');check('unfinished plan can leave with empty hands and return exactly',ev('__LYS_QA.atOrigin()'));embark();check('native revisit preserves the chosen plan',ev('__PARTS_QA.info().ledger.plan')=='secours');go('crate:A');ev('__PARTS_QA.reload()');check('real save load preserves carried crate and absent rack',ev('__PARTS_QA.info().ledger.crates.A==="held"&&__PARTS_QA.info().racked===5'))
  go('crate:A');check('same rack receives its own crate and removes held visual',ev('__PARTS_QA.info().racked===6&&__PARTS_QA.info().carried===0'))
  # Traverse to the cargo and back with the native movement/collision function.
  path=ev('__LYS_QA.walk([[0,1.65,25],[5,1.65,6],[0,1.65,1],[0,1.65,-8],[-10,1.65,-8],[-10,1.65,-11]])')
  check('actual route reaches first crate without a jump',abs(path[-1][0]+10)<.2 and abs(path[-1][2]+11)<.2)
  go('crate:A');go('dest:equipage');check('one delivered crate is visible and persistent',ev('__PARTS_QA.info().delivered===1&&__PARTS_QA.info().carried===0'))
  go('crate:B');go('dest:equipage');check('full destination refuses without losing held crate',ev('__PARTS_QA.info().ledger.crates.B==="held"&&__PARTS_QA.info().delivered===1'))
  ev('__PARTS_QA.near("dest:accueil")')
  for kind in ['combat','loading','lab','air']:check('delivery blocked during '+kind,ev('(k)=>__PARTS_QA.blocked("deliver","accueil",k)',kind))
  for throws in [False,True]:check('entire cargo rollback on storage '+str(throws),ev('(v)=>__PARTS_QA.fail("deliver","accueil",v).same',throws))
  go('dest:accueil');ev('__PARTS_QA.reload()');check('two deliveries survive reload without refill',ev('__PARTS_QA.info().delivered===2&&__PARTS_QA.info().racked===4'))
  check('reload preserves departure coordinates without reusing an old campaign owner',ev('__PARTS_QA.returnSaved()'))
  for crate,dest in [('F','accueil'),('C','cuisines'),('D','cuisines'),('E','cuisines')]:go('crate:'+crate);go('dest:'+dest)
  check('all six placed as 3/2/1 with no ordinary inventory reward',ev('__PARTS_QA.info().ledger.crates')=={'A':'equipage','B':'accueil','C':'cuisines','D':'cuisines','E':'cuisines','F':'accueil'} and ev('__PARTS_QA.info().inv')==inv)
  go('maelle','npc:parts69:maelle');check('completion rollback preserves six placements and reward',ev('__PARTS_QA.fail("finish").same'));choose('Faire constater');choose('Revenir.');check('reward exactly forty capsules once',ev('__PARTS_QA.info().caps')==caps+40)
  ev('__PARTS_QA.reload()');check('completed save retains cargo, historical source and no refill',ev('__PARTS_QA.info().ledger.finished&&__PARTS_QA.info().delivered===6&&__PARTS_QA.info().racked===0') and ev('__PARTS_QA.info().old')==old)
  go('maelle','npc:parts69:maelle');check('reward removed from dialogue after real reload',page.locator('#dialogueChoices button').filter(has_text='Faire constater').count()==0);choose('Revenir.')
  ev('__PARTS_QA.render()');page.screenshot(path=str(a.output/'04-six-caisses-reparties.png'))
  for plan,label,quota in [('rotation','La prochaine traversée',{'cuisines':3,'accueil':1,'equipage':2}),('quartiers','Les cuisines d’abord',{'cuisines':4,'accueil':1,'equipage':1})]:
   ev('(s)=>__PARTS_QA.restore(s)',ready);go('maelle','npc:parts69:maelle');choose('Examiner : '+label);choose('Confirmer cette répartition');choose('Revenir.');crates=iter(['F','E','D','C','B','A'])
   for dest,n in quota.items():
    for _ in range(n):go('crate:'+next(crates));go('dest:'+dest)
   go('maelle','npc:parts69:maelle');choose('Faire constater');choose('Revenir.');check('alternate full plan '+plan,ev('__PARTS_QA.info().ledger.plan')==plan and ev('__PARTS_QA.info().delivered')==6)
  # Same authored quest is reachable under the two other original settlements.
  for policy in ['serment','regence']:
   ev('(p)=>__PARTS_QA.setup(p,1)',policy);embark();go('maelle','npc:parts69:maelle');choose('Aider au déchargement');choose('Revenir.');check('distinct saved original settlement '+policy,ev('__PARTS_QA.info().ledger.basis.policy')==policy)
   go('notice');choose('Examiner la consigne');choose('Revenir.');go('treuil');n=ev('__PARTS_QA.info().inv.circuitry');choose('Commander les verrous');choose('Revenir.');check('technical gate consumes exactly one circuit '+policy,ev('__PARTS_QA.info().inv.circuitry')==n-1 and ev('__PARTS_QA.info().gate')==0)
   go('sortie');check('Ratonneau departure restored '+policy,ev('__LYS_QA.atOrigin()'))
  check('no JavaScript or adapter presentation errors',not errors and not ev('__PARTS_QA.info().error'))
 finally:
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
  (a.output/'PARTS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True);browser.close()
