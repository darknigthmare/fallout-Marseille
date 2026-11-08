"""Instrumented Cour du Lys test: actual authored scene, game reducers, UI and doors.
Two synthetic geographic ports; no route certification on IGN data or human playtest.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/lys/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__LYS_QA={
 close(){closePipboy();},
 focusPort(){debugDismissDialogue();mode="PLAYING";onGround=true;state.player.yaw=0;state.player.pitch=-.15;updateSelectedInteractable();return selectedInteractable?.id;},
 setup(){closePipboy();debugDismissDialogue();debugRenderPaused=true;updatePlayer=()=>{};state.player.hp=100;state.player.caps=100;state.character.special.I=5;for(const k of ['water','food','cloth','scrap','circuitry'])state.inventory[k]=10;state.v068Lys=MistralLys.fresh();return this.port(0);},
 port(index=0){
  debugDismissDialogue();const site=v042Site(MistralLys.PORTS[index]);world=createWorld(site.macro,'Port synthétique pour l’audience','PAS LES RUES IGN');world.v046=true;world.geoMacro=true;world.v046Anchor=[0,0,0];world.v046Records=new Map();world.geoTiles=new Map();world.v046ChunkDraws=[];world.v047TerrainDraws=[];world.bounds=[-30,30,-30,30];world.v047TerrainBank={read:()=>({height:0}),grids:new Map()};V046.terrain=world.v047TerrainBank;V046.readyAnchor=[0,0,0];V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;onGround=true;settings.geoFalloutLayer=true;v050TravelGround=()=>0;v049Own(world);
  state.player.zone=site.macro;state.player.pos=[0,1.65,2];state.player.yaw=0;state.player.pitch=-.15;state.v042.activeInterior=null;state.v042.discovered[site.id]=true;
  V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();V042_RUNTIME.worldId=world.id;V042_RUNTIME.nearest=null;
  const id='v042-npc:qa:lys';V042_RUNTIME.npcData.set(id,{siteId:site.id,name:'Passeur de test',role:'passeur',index:0});const n=addHumanNPC(world,id,'Passeur de test','Passeur',[0,0,0]);n.v042Site=site.id;addBox(world,[0,-.1,0],[40,.2,40],[.45,.43,.35]);mode='PLAYING';gameStarted=true;globalThis.__LYS_PORT=world;globalThis.__LYS_POS=state.player.pos.slice();updateSelectedInteractable();return {site:site.id,selected:selectedInteractable?.id};
 },
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v068LysInfo().points[id];state.player.pos=[p[0],p[1]+1.65,p[2]+2];state.player.yaw=0;state.player.pitch=-.18;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.7]),collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1])};},
 info(){return {ledger:state.v068Lys,caps:state.player.caps,inv:state.inventory,zone:state.player.zone,local:!!world.v068Lys,old:JSON.stringify([state.v060Council,state.v061Poste,state.v062Pharmacy,state.v063Radieuse,state.v064Mutuelle,state.v065Notaires,state.v066Voisins,state.v067Devoir]),npcs:world.npcs.length,gate:world.colliders.filter(c=>c.lysGate).map(c=>({id:c.lysGate,open:c.disabled})),crown:world.staticDraws.filter(d=>d.lysCrown&&!d.hidden).length,guide:world.staticDraws.filter(d=>d.lysGuide&&!d.hidden).length,body:world.staticDraws.find(d=>d.lysBody)?.emissive,gift:world.staticDraws.filter(d=>d.lysGift&&!d.hidden).length,giftCollision:world.colliders.filter(c=>c.lysGift&&!c.disabled).length,returnPoint:state.v042.returnPoint,error:__MISTRAL_DEBUG.v068LysInfo().error};},
 snapshot(){return JSON.stringify(state);},restore(s){debugDismissDialogue();state=migrateState(JSON.parse(s));state.v042.activeInterior=MistralLys.SITE_ID;loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';return this.info();},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 fail(type,id,answer){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v068LysAction(type,id,answer);}finally{saveGame=save;}return {result,same:JSON.stringify(state)===before};},
 failBoard(){const old=saveGame,originalWorld=world,originalPos=state.player.pos.slice(),ledger=JSON.stringify(state.v068Lys);saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Embarquer')).onChoose();}finally{saveGame=old;}return world===originalWorld&&state.v042.activeInterior===null&&JSON.stringify(state.player.pos)===JSON.stringify(originalPos)&&JSON.stringify(state.v068Lys)===ledger;},
 walk(points){mode='PLAYING';state.player.pos=points[0].slice();const visited=[];for(let i=1;i<points.length;i++){const t=points[i],ox=state.player.pos[0],oz=state.player.pos[2],steps=Math.ceil(Math.hypot(t[0]-ox,t[2]-oz)/.12);for(let j=0;j<steps;j++){tryPlayerMove((t[0]-ox)/steps,(t[2]-oz)/steps);state.player.pos[1]=groundHeightAt(state.player.pos[0],state.player.pos[2],state.player.pos[1]-1.65)+1.65;}visited.push(state.player.pos.slice());}return visited;},
 remember(){globalThis.__LYS_STALE=dialogueState.choices.find(c=>c.text.startsWith('Confirmer')).onChoose;},stale(){const before=JSON.stringify(state);__LYS_STALE();return JSON.stringify(state)===before;},
 atOrigin(){return world===__LYS_PORT&&JSON.stringify(state.player.pos)===JSON.stringify(__LYS_POS)&&state.v042.activeInterior===null;},
 render(which='court'){
  for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}
  document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';
  const c=({court:{pos:[5,3,25],target:[-5,3,-9]},king:{pos:[-3.2,5.9,-20.7],target:[-8,5.7,-26]},archive:{pos:[12,2.6,-13],target:[18,1.4,-24]},kitchen:{pos:[-11.7,2.5,3],target:[-18,1.1,-3]}})[which];sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:65},currentEnv());return renderer.constructor.name;
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralLys' in html
html=html.replace(marker,bridge+'\n'+marker);checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7500)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v068LysInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  port=page.evaluate('__LYS_QA.setup()');check('known safe port representative used',port['selected']=='npc:v042-npc:qa:lys')
  old=page.evaluate('__LYS_QA.info().old')
  def choose(text):
   print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected=None):
   d=page.evaluate('(id)=>__LYS_QA.near(id)',id);print('NEAR',id,d,flush=True);check('accessible E interaction '+id,d['selected']==(expected or 'lys68:'+id) and d['los'] and not d['collision']);page.keyboard.press('e')
  def embark():
   page.evaluate('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Passage maritime');choose('Embarquer');page.wait_for_timeout(150)
  page.keyboard.press('e');check('original representative dialogue preserved',page.locator('#dialogueChoices button').filter(has_text='Parler du secteur').count()==1);choose('Passage maritime');check('crossing advertised as narrative not navigable','sans navigation libre' in page.locator('#dialogueLine').inner_text());check('failed save cancels boarding at origin',page.evaluate('__LYS_QA.failBoard()'));choose('Embarquer')
  initial=page.evaluate('__LYS_QA.info()');check('native ferry arrival builds distinct court and four residents',initial['local'] and initial['npcs']==4)
  page.evaluate('__MISTRAL_DEBUG.v068LysOpen()');check('Pip-Boy contains new independent chapter','La Cour du Lys' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-carnet-desktop.png'));page.set_viewport_size({'width':390,'height':844});check('390 pixel page has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-carnet-mobile.png'));page.set_viewport_size({'width':1280,'height':800});page.evaluate('__LYS_QA.close()')
  page.evaluate('__LYS_QA.render()');page.screenshot(path=str(a.output/'03-cour-insulaire.png'))
  go('apolline','npc:lys68:apolline');choose('Ouvrir');choose('Revenir.');check('no requirement to finish the Cité chain',page.evaluate('__LYS_QA.info().ledger.opened') and page.evaluate('__LYS_QA.info().old')==old)
  # Return is available with an unfinished audience; no exile or one-way loading.
  go('sortie');page.wait_for_timeout(100);check('early return restores exact retained departure point',page.evaluate('__LYS_QA.atOrigin()'));embark();check('return visit preserves opened audience',page.evaluate('__LYS_QA.info().ledger.opened'))
  for who in ['sana','basile','jeanne']:
   go(who,'npc:lys68:'+who);choose('Écouter et conserver');choose('Revenir.')
  for doc in ['vivres','accueil']:
   go(doc);choose('Conserver cette preuve');choose('Revenir.')
  prepared=page.evaluate('__LYS_QA.snapshot()')
  # Security physically blocks front archive access before any route is unlocked.
  stopped=page.evaluate('(p)=>__LYS_QA.walk(p)',[[15.5,1.65,-6],[15.5,1.65,-14]])[-1];check('front archive gate physically blocks movement',stopped[2]>-10)
  go('guichet');before=page.evaluate('__LYS_QA.info()');choose('Un sujet héréditaire');check('wrong etiquette answer costs nothing',page.evaluate('__LYS_QA.info()')==before);choose('Un hôte secouru');choose('Revenir.')
  gates=page.evaluate('__LYS_QA.info().gate');check('front route opens only its own collision',gates==[{'id':'front','open':True},{'id':'service','open':False}])
  walk=page.evaluate('(p)=>__LYS_QA.walk(p)',[[15.5,1.65,-6],[15.5,1.65,-14],[16,1.65,-21]])[-1];check('opened archives traversable through native collision',abs(walk[2]+21)<.3)
  go('programme');choose('Conserver cette preuve');choose('Revenir.')
  stair=page.evaluate('(p)=>__LYS_QA.walk(p)',[[0,1.65,12],[0,1.65,-5],[-8,1.65,-5],[-8,1.65,-19],[-8,4.85,-23]])[-1];print('STAIR',stair,flush=True);check('royal gallery reachable without jumping',abs(stair[0]+8)<.3 and abs(stair[1]-4.85)<.2 and abs(stair[2]+23)<.3)
  page.evaluate('__LYS_QA.render("king")');page.screenshot(path=str(a.output/'04-louis-pedagogique.png'))
  ready=page.evaluate('__LYS_QA.snapshot()')
  go('louis');choose('Examiner : Le musée');check('confirmation limits scope to local rule','ancienne' in page.locator('#dialogueLine').inner_text() or 'anciens votes' in page.locator('#dialogueLine').inner_text());page.screenshot(path=str(a.output/'05-reglement-local.png'));page.evaluate('__LYS_QA.remember()')
  fail=page.evaluate('__LYS_QA.fail("decide","commune")');check('failed save does not remove crown or alter sources',not fail['result'] and fail['same']);choose('Confirmer');check('stale confirmation cannot reapply choice',page.evaluate('__LYS_QA.stale()'));choose('Revenir.')
  info=page.evaluate('__LYS_QA.info()');check('communal outcome visibly removes crown and displays guide',info['crown']==0 and info['guide']==1);check('previous regional and local records unchanged',info['old']==old)
  page.evaluate('__LYS_QA.render("king")');page.screenshot(path=str(a.output/'06-louis-guide.png'))
  for who in ['jeanne','basile','sana']:
   go(who,'npc:lys68:'+who);choose('Présenter le règlement');choose('Revenir.')
  go('apolline','npc:lys68:apolline');caps=page.evaluate('__LYS_QA.info().caps');choose('Clore l’audience');choose('Revenir.');check('completion grants exactly fifty-five caps',page.evaluate('__LYS_QA.info().caps')==caps+55)
  go('colis');inv=page.evaluate('__LYS_QA.info().inv');choose('Retirer le colis');choose('Revenir.');after=page.evaluate('__LYS_QA.info()');check('crate gives exact ordinary items once',after['inv']['food']==inv['food']+1 and after['inv']['water']==inv['water']+3);check('crate geometry and collision removed after pickup',after['gift']==0 and after['giftCollision']==0)
  save=page.evaluate('__LYS_QA.reload()');check('actual save reload keeps ending, receipts and exhausted stock',save['ledger']['finished'] and save['ledger']['claimed'] and save['ledger']['notified']==['sana','basile','jeanne']);go('colis');check('second claim unavailable after load',page.locator('#dialogueChoices button').filter(has_text='Retirer').count()==0);choose('Revenir.')
  # The two other policies are tested from the actually played checkpoint.
  for policy,label,crown,guide in [('serment','La Cour sous serment',3,0),('regence','La régence de secours',0,0)]:
   page.evaluate('(s)=>__LYS_QA.restore(s)',ready);go('louis');choose('Examiner : '+label);choose('Confirmer');choose('Revenir.');info=page.evaluate('__LYS_QA.info()');check('visible and persistent policy '+policy,info['ledger']['policy']==policy and info['crown']==crown and info['guide']==guide)
  # Free physical side route is independent of formal gate and Intelligence.
  page.evaluate('(s)=>__LYS_QA.restore(s)',prepared);go('levier');choose('Ouvrir la porte de service');choose('Revenir.');g=page.evaluate('__LYS_QA.info().gate');check('service alternative opens its own gate, not ceremonial gate',g==[{'id':'front','open':False},{'id':'service','open':True}]);walk=page.evaluate('(p)=>__LYS_QA.walk(p)',[[4,1.65,-21.5],[12,1.65,-21.5],[16,1.65,-21]])[-1];check('free side passage physically walkable',abs(walk[0]-16)<.3 and abs(walk[2]+21)<.3)
  page.evaluate('(s)=>__LYS_QA.restore(s)',prepared);go('guichet');c=page.evaluate('__LYS_QA.info().inv.circuitry');choose('Dérivation technique');choose('Revenir.');check('technical route consumes one circuit',page.evaluate('__LYS_QA.info().inv.circuitry')==c-1 and page.evaluate('__LYS_QA.info().ledger.route')=='technique')
  # New geographical narrative crossing from the second port retains its own origin.
  page.evaluate('__LYS_QA.port(1)');embark();check('Ratonneau also reaches the audience',page.evaluate('__LYS_QA.info().local'));go('sortie');page.wait_for_timeout(100);check('Ratonneau return restores its exact original scene and point',page.evaluate('__LYS_QA.atOrigin()'))
  check('no JavaScript or presentation exceptions',not errors and page.evaluate('__LYS_QA.info().error') is None)
  result={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Actual authored Cour du Lys, models, UI, E, native movement/collision, four actors, saves and visible alternatives. Two synthetic port scenes with real catalogue identities and native retained-world entry/exit. Scripted positions, isolated MemoryStorage, software renderer; no IGN sea traversal or human full campaign.'}
  (a.output/'LYS_BROWSER.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',page.evaluate('window.__LYS_QA?.info()'),flush=True);raise
 finally:browser.close()
