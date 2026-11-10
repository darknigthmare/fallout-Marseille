"""Actual postal courtyard, progressive flights, manual delivery, native dialogs,
E inputs, geometry, save/load and rewards. Scripted player positions, synthetic
Saint-Charles relay and isolated MemoryStorage; software renderer, not human QA.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/pigeons/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
def get_bridge(path):
 tree=ast.parse(path.read_text());return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='bridge' for k in n.targets))
base_bridge=get_bridge(root/'tests/expansion/lys_browser_smoke.py')
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__P74_QA={
 setup(){__LYS_QA.setup();state.v074Pigeons=MistralPigeons.fresh();return this.port();},
 port(){const site=v042Site(MistralPigeons.RELAY);__LYS_QA.port();world.id=site.macro;state.player.zone=site.macro;state.v042.discovered[site.id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();const n=world.npcs[0];n.v042Site=site.id;V042_RUNTIME.npcData.set(n.id,{siteId:site.id,name:'Représentant de Saint-Charles',role:'artisan',index:0});globalThis.__LYS_PORT=world;globalThis.__LYS_POS=state.player.pos.slice();updateSelectedInteractable();return{selected:selectedInteractable?.id,site:site.id};},
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v074PigeonsInfo().points[id];state.player.pos=[p[0],p[1]+1.65,p[2]+2];state.player.yaw=0;state.player.pitch=-.18;onGround=true;mode='PLAYING';updateSelectedInteractable();return{selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.8])};},
 info(){return{...__MISTRAL_DEBUG.v074PigeonsInfo(),caps:state.player.caps,inv:state.inventory,npcs:world.npcs.length,enemies:world.enemies.length,receipts:world.staticDraws.filter(d=>d.p74Receipt&&!d.hidden).length,envelopes:world.staticDraws.filter(d=>d.p74Envelope&&!d.hidden).length,panel:world.staticDraws.some(d=>d.p74Panel&&!d.hidden),lids:world.staticDraws.filter(d=>d.p74CageRoof).map(d=>({id:d.p74CageRoof,open:d.scale[1]>1})),doors:world.colliders.filter(c=>c.p74Hatch).map(c=>({id:c.p74Hatch,disabled:c.disabled})),old:JSON.stringify([state.v073Gabians,state.v072Rats,state.v071Cigales,state.v070Secours,state.v069Parts,state.v068Lys,state.v067Devoir,state.v066Voisins,state.v065Notaires,state.v064Mutuelle,state.v063Radieuse,state.v062Pharmacy,state.v061Poste,state.v060Council])};},
 snapshot(){return JSON.stringify(state);},restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';inCombat=false;return this.info();},save(){return saveGame(false);},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 ticks(n=1){mode='PLAYING';for(let i=0;i<n;i++)updateEnemies(.2);return this.info();},
 fail(type,id,bird){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v074PigeonsAction(type,id,bird);}finally{saveGame=save;}return{same:JSON.stringify(state)===before,result};},
 failEntry(){const save=saveGame,w=world,p=state.player.pos.slice();saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre la cour')).onChoose();}finally{saveGame=save;}return world===w&&state.v042.activeInterior===null&&JSON.stringify(state.player.pos)===JSON.stringify(p);},
 blockedFlight(){const a=state.v074Pigeons.mail.soins,before=a.pos.slice(),c=addCollider(world,a.pos[0]/1000,a.pos[2]/1000,3,3,{minY:0,maxY:10});this.ticks(3);world.colliders=world.colliders.filter(k=>k!==c);return JSON.stringify(before)===JSON.stringify(state.v074Pigeons.mail.soins.pos);},
 pausedFlight(){const before=JSON.stringify(state.v074Pigeons);for(const m of ['PIP','DIALOGUE','NOTE']){mode=m;for(let i=0;i<10;i++)updateEnemies(.2);}mode='PLAYING';return JSON.stringify(state.v074Pigeons)===before;},
 failArrival(){const a=state.v074Pigeons.mail.soins,target=MistralPigeons.ROUTES.soins[3];a.waypoint=3;a.pos=[target[0],target[1]+50,target[2]+50];const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;try{this.ticks(1);}finally{saveGame=save;}return{same:JSON.stringify(state)===before,paused:__MISTRAL_DEBUG.v074PigeonsInfo().paused};},
 remember(){globalThis.__P74_STALE=dialogueState.choices.find(c=>c.text.startsWith('Confirmer')).onChoose;},stale(){const before=JSON.stringify(state);globalThis.__P74_STALE();return JSON.stringify(state)===before;},
 render(which='court'){
 debugDismissDialogue();for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';
 const p=state.v074Pigeons.mail.soins.pos.map(n=>n/1000),c=which==='bird'?{pos:[p[0]+2,p[1]+1.3,p[2]+3],target:[p[0],p[1]+.3,p[2]]}:which==='stairs'?{pos:[3,4.5,12],target:[18,4.1,-12]}:{pos:[-22,7,24],target:[0,1,-5]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:60},currentEnv());return renderer.constructor.name;}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralPigeons' in html
html=html.replace(marker,base_bridge+'\n'+bridge+'\n'+marker)
checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(8000);page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 def ev(s,arg=None):return page.evaluate(s,arg)
 def choose(text):print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
 def go(id,expected=None):
  r=ev('(id)=>__P74_QA.near(id)',id);print('NEAR',id,r,flush=True);check('native E interaction '+id,r['selected']==(expected or 'p74:'+id) and r['los'] and not r['collision']);page.keyboard.press('e')
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v074PigeonsInfo');ev('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  r=ev('__P74_QA.setup()');check('existing Saint-Charles identity',r['site']=='v042-marseille-caravan-02');old=ev('__P74_QA.info().old');page.keyboard.press('e');check('old relay conversations remain',page.locator('#dialogueChoices button').filter(has_text='Parler du secteur').count()==1);choose('Poste Restante · La bonne');check('entry rollback when save refused',ev('__P74_QA.failEntry()'));choose('Rejoindre la cour')
  check('actual courtyard, three people and neutral birds',ev('__P74_QA.info().local') and ev('__P74_QA.info().npcs')==3 and ev('__P74_QA.info().enemies')==0 and len(ev('__P74_QA.info().birdDraws'))==2)
  ev('__MISTRAL_DEBUG.v074PigeonsOpen()');check('dedicated Pip-Boy with two messages','Deux places au sec' in page.locator('#pipboy').inner_text() and 'poignée' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-journal.png'));page.set_viewport_size({'width':390,'height':844});check('390px layout has no page overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
  go('sortie');check('early exit restores exact retained exterior',ev('__LYS_QA.atOrigin()'));ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Poste Restante · La bonne');choose('Rejoindre la cour')
  ev('__P74_QA.render()');page.screenshot(path=str(a.output/'03-cour.png'));ev('__P74_QA.render("bird")');page.screenshot(path=str(a.output/'04-pigeon.png'))
  go('mirette','npc:p74:mirette');choose('Accepter');choose('Revenir.');start=ev('__P74_QA.snapshot()')
  route=ev('__LYS_QA.walk([[0,1.65,25],[20,1.65,25],[20,1.65,13],[20,1.65,-6],[21,4.85,-9]])');print('STAIRS',route,flush=True);check('native stairs climb to inhabited upper terrace',abs(route[-1][0]-21)<.3 and abs(route[-1][1]-4.85)<.2 and abs(route[-1][2]+9)<.3)
  route=ev('__LYS_QA.walk([[21,4.85,-9],[20,4.85,-6],[20,4.85,13],[20,1.65,25]])');check('native stairs descend safely',abs(route[-1][1]-1.65)<.2 and abs(route[-1][2]-25)<.3)
  for id in ['soins','pompes']:
   go('source:'+id);choose('Relever la bague');before=ev('__P74_QA.info().ledger');choose('Fixer le pli au tube de '+('brique' if id=='soins' else 'azur'));check('wrong homing destination rejected '+id,ev('__P74_QA.info().ledger')==before);choose('Fixer le pli au tube de '+('azur' if id=='soins' else 'brique'));choose('Ouvrir la cage');check('closed destination refuses release '+id,ev('__P74_QA.info().ledger.mail.'+id+'.phase')=='loaded');choose('Revenir.')
   go('loft:'+id);choose('Ouvrir la trappe');choose('Revenir.');check('arrival hatch collision disabled '+id,next(d for d in ev('__P74_QA.info().doors') if d['id']==id)['disabled'])
   go('source:'+id);failure=ev('(id)=>__P74_QA.fail("release",id)',id);check('failed release leaves letter loaded '+id,failure['same'] and not failure['result']);choose('Ouvrir la cage');check('release not instantaneous arrival '+id,ev('__P74_QA.info().ledger.mail.'+id+'.phase')=='flying');check('source lid physically opens before takeoff '+id,next(d for d in ev('__P74_QA.info().lids') if d['id']==id)['open'])
  check('menu states pause pigeon flight',ev('__P74_QA.pausedFlight()'));check('solid obstacle prevents forward flight',ev('__P74_QA.blockedFlight()'));ev('__P74_QA.ticks(8)');ev('__P74_QA.save()');mid=ev('__P74_QA.info().ledger');ev('__P74_QA.reload()');check('mid-flight exact save reconstruction',ev('__P74_QA.info().ledger')==mid)
  checkpoint=ev('__P74_QA.snapshot()');r=ev('__P74_QA.failArrival()');check('arrival checkpoint refuses lost write',r['same'] and r['paused']);go('mirette','npc:p74:mirette');choose('Retenter la sauvegarde');choose('Revenir.');check('retry clears the deliberate pause',not ev('__P74_QA.info().paused'));ev('(s)=>__P74_QA.restore(s)',checkpoint)
  ev('__P74_QA.ticks(180)');print('FLIGHTS',ev('__P74_QA.info().ledger'),flush=True);check('two birds reach their exact different lofts',all(m['phase']=='arrived' for m in ev('__P74_QA.info().ledger.mail').values()));check('flight has not generated any acknowledgement',ev('__P74_QA.info().receipts')==0)
  for id in ['soins','pompes']:
   go(id,'npc:p74:'+id);choose('Remettre le pli');check('recipient has a personal response '+id,'sign' in page.locator('#dialogueLine').inner_text());choose('Conserver le reçu')
  check('two physical signed receipts appear',ev('__P74_QA.info().receipts')==2);check('no mail left on source trays',ev('__P74_QA.info().envelopes')==0)
  ready=ev('__P74_QA.snapshot()');go('mirette','npc:p74:mirette');choose('Afficher un bilan');check('confirmation forbids private addresses','Ni noms' in page.locator('#dialogueLine').inner_text());page.screenshot(path=str(a.output/'05-reponses.png'));ev('__P74_QA.remember()');caps=ev('__P74_QA.info().caps');failure=ev('__P74_QA.fail("finish","annonce")');check('failed final write retains capsules and decision',failure['same'] and not failure['result']);choose('Confirmer le traitement');check('exactly fifty capsules once',ev('__P74_QA.info().caps')==caps+50);check('stale confirmation refused',ev('__P74_QA.stale()'));choose('Revenir.');check('public board visible only for anonymised choice',ev('__P74_QA.info().panel'))
  ev('__P74_QA.reload()');go('mirette','npc:p74:mirette');check('no repeated reward after reload',page.locator('#dialogueChoices button').filter(has_text='Afficher un bilan').count()==0);choose('Revenir.');check('all earlier ledgers untouched',ev('__P74_QA.info().old')==old)
  ev('__P74_QA.render("stairs")');page.screenshot(path=str(a.output/'06-terrasse.png'))
  # Complete free on-foot alternative, using real dialogs and a single mailbag.
  ev('(s)=>__P74_QA.restore(s)',start)
  for id in ['pompes','soins']:
   go('source:'+id);choose('Prendre le pli dans la sacoche');choose('Revenir.')
   if id=='pompes':
    go('source:soins');choose('Prendre le pli dans la sacoche');check('only one carried sealed message',ev('__P74_QA.info().ledger.mail.soins.phase')=='source');choose('Revenir.')
   go(id,'npc:p74:'+id);choose('Remettre le pli');choose('Conserver le reçu')
  check('courier alternative leaves pigeons at start and lofts closed',all(m['method']=='pied' and m['waypoint']==0 for m in ev('__P74_QA.info().ledger.mail').values()) and not any(ev('__P74_QA.info().ledger.hatches').values()))
  go('mirette','npc:p74:mirette');choose('Garder les réponses');choose('Confirmer le traitement');choose('Revenir.');check('private policy has no public board',not ev('__P74_QA.info().panel') and ev('__P74_QA.info().ledger.finished'));check('no reagent or health change from delivery',ev('__P74_QA.info().inv')==json.loads(start)['inventory'])
  ev('__P74_QA.reload()');check('foot delivery and private policy persist',ev('__P74_QA.info().ledger.policy')=='scelles')
  # Campaign replacement correctly invalidates the session-only retained world.
  # Without geographic data the native loading gate must retain the interior.
  go('sortie');check('unavailable exterior after reload keeps completed interior safe',ev('__P74_QA.info().local') and ev('__MISTRAL_DEBUG.v048Info().exitPending!==null') and ev('__P74_QA.info().ledger.finished'))
  ev('__MISTRAL_DEBUG.v046Cancel()');check('cancelled return preserves active courtyard',ev('__P74_QA.info().local') and ev('__MISTRAL_DEBUG.v048Info().exitPending===null'))
  # Separate, same-session return with a prepared synthetic exterior on this state.
  ev('__P74_QA.port()');page.keyboard.press('e');choose('Poste Restante · La bonne');choose('Rejoindre la cour');go('sortie');check('same-session return preserves finished courier ledger',ev('__LYS_QA.atOrigin()') and ev('__P74_QA.info().ledger.finished'))
  check('no JavaScript or adapter error',not errors and ev('__P74_QA.info().error') is None)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
  (a.output/'PIGEONS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',ev('window.__P74_QA?.info()'),flush=True);raise
 finally:browser.close()
