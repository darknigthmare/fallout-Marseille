"""Actual consignment runtime, E/dialogues, native gun/collisions and save/load.
Scripted positions/aim and synthetic geographic relay; isolated MemoryStorage.
This is not a real IGN traversal, human playtest or disk-backed cold restart.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/gabians/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
def get_bridge(path):
 tree=ast.parse(path.read_text());return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='bridge' for k in n.targets))
base_bridge=get_bridge(root/'tests/expansion/lys_browser_smoke.py')
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__G73_QA={
 setup(){__LYS_QA.setup();state.v073Gabians=MistralGabians.fresh();return this.port();},
 port(){const site=v042Site(MistralGabians.RELAY);__LYS_QA.port();world.id=site.macro;state.player.zone=site.macro;state.v042.discovered[site.id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();const n=world.npcs[0];n.v042Site=site.id;V042_RUNTIME.npcData.set(n.id,{siteId:site.id,name:'Représentant du Vieux-Port',role:'artisan',index:0});globalThis.__LYS_PORT=world;globalThis.__LYS_POS=state.player.pos.slice();updateSelectedInteractable();return{selected:selectedInteractable?.id,site:site.id};},
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v073GabiansInfo().points[id];state.player.pos=[p[0],1.65,p[2]+2.2];state.player.yaw=0;state.player.pitch=-.24;onGround=true;mode='PLAYING';updateSelectedInteractable();return{selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,1.65),los:lineOfSight(state.player.pos,[p[0],1.25,p[2]+1.4])};},
 info(){return {...__MISTRAL_DEBUG.v073GabiansInfo(),caps:state.player.caps,inv:state.inventory,hp:state.player.hp,old:JSON.stringify([state.v072Rats,state.v071Cigales,state.v070Secours,state.v069Parts,state.v068Lys,state.v067Devoir,state.v066Voisins,state.v065Notaires,state.v064Mutuelle,state.v063Radieuse,state.v062Pharmacy,state.v061Poste,state.v060Council]),baskets:world.colliders.filter(c=>c.g73Basket).map(c=>({id:c.g73Basket,minY:c.minY,maxY:c.maxY})),objects:new Set(world.staticDraws.filter(d=>d.g73Object&&!d.hidden).map(d=>d.g73Object)).size,returned:new Set(world.staticDraws.filter(d=>d.g73Returned&&!d.hidden).map(d=>d.g73Returned)).size};},
 snapshot(){return JSON.stringify(state);},restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';inCombat=false;return this.info();},save(){return saveGame(false);},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 ticks(n=1,move=true){mode='PLAYING';if(move)state.player.pos=[25,1.65,23];for(let i=0;i<n;i++)updateEnemies(.2);return this.info();},
 fail(type,id,method){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v073GabiansAction(type,id,method);}finally{saveGame=save;}return{same:JSON.stringify(state)===before,result};},
 failEntry(){const save=saveGame,w=world,p=state.player.pos.slice();saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre la consigne')).onChoose();}finally{saveGame=save;}return world===w&&state.v042.activeInterior===null&&JSON.stringify(state.player.pos)===JSON.stringify(p);},
 threat(kind){debugDismissDialogue();const e=world.enemies.find(e=>e.g73Id==='filets');for(const a of Object.values(state.v073Gabians.birds)){a.cooldown=6000;a.wind=null;a.shot=null;}state.v073Gabians.birds.filets.cooldown=0;state.player.pos=[e.pos[0],1.65,e.pos[2]+3];state.player.hp=100;mode='PLAYING';updateEnemies(.1);const announced=!!state.v073Gabians.birds.filets.wind;let wall;if(kind==='dodge')state.player.pos[0]+=4;if(kind==='cover')wall=addCollider(world,e.pos[0],e.pos[2]+2,5,5,{minY:2,maxY:2.3});if(kind==='menu')mode='PIP';const before=state.player.hp;for(let i=0;i<14;i++)updateEnemies(.2);const after=state.player.hp;if(wall)world.colliders=world.colliders.filter(c=>c!==wall);return{announced,before,after,wind:state.v073Gabians.birds.filets.wind};},
 rig(){return v025Rig(world.enemies.find(e=>e.g73Id==='filets')).parts.map(p=>({id:p.id,label:p.label}));},
 shot(){debugDismissDialogue();const e=world.enemies.find(e=>e.g73Id==='filets');state.player.pos=[e.pos[0],1.65,e.pos[2]+5];const part=enemyHitParts(e).find(p=>p.id==='body'),d=vNorm(vSub(part.center,state.player.pos));state.player.yaw=Math.atan2(d[0],-d[2]);state.player.pitch=Math.asin(d[1]);mode='PLAYING';onGround=true;reloadTimer=0;V020.cooldown=0;V020.reload=null;state.player.weaponId='pistol10';setEquipmentCondition('weapon','pistol10',100);state.player.ammoClip=12;state.player.ammoReserve=20;state.player.clipSize=12;const before=e.health,ammo=state.player.ammoClip;fireWeapon();return{before,after:e.health,ammoBefore:ammo,ammoAfter:state.player.ammoClip};},
 kill(id){mode='PLAYING';damageEnemy(world.enemies.find(e=>e.g73Id===id),300,'body');return this.info();},
 effects(){const e=world.enemies.find(e=>e.g73Id==='filets');mode='PLAYING';damageEnemy(e,2,'arm_l');applyEnemyStatus(e,'burning',3);applyEnemyStatus(e,'slow',4);state.player.pos=[25,1.65,23];updateEnemies(.2);saveGame(false);return state.v073Gabians.birds.filets;},
 failHit(){const e=world.enemies.find(e=>e.g73Id==='filets'),before=JSON.stringify(state),hp=e.health,save=saveGame;saveGame=()=>false;try{damageEnemy(e,7,'body');}finally{saveGame=save;}return before===JSON.stringify(state)&&hp===e.health;},
 blockedFlight(){const e=world.enemies.find(e=>e.g73Id==='filets'),before=e.pos.slice(),c=addCollider(world,e.pos[0],e.pos[2],3,3,{minY:0,maxY:7});this.ticks(3);world.colliders=world.colliders.filter(k=>k!==c);return JSON.stringify(before)===JSON.stringify(e.pos);},
 underBasket(){state.player.pos=[-10,1.65,-13];this.ticks(50,false);const first=state.v073Gabians.platforms.filets.drop;this.ticks(10,false);return{first,second:state.v073Gabians.platforms.filets.drop,blocked:__MISTRAL_DEBUG.v073GabiansInfo().blockedBaskets,hp:state.player.hp};},
 setNearArrival(){const a=state.v073Gabians.birds.filets;a.phase='lure';a.waypoint=1;a.pos=[-22000,500,-19900];state.player.pos=[25,1.65,23];},
 failCheckpoint(){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;try{this.ticks(1);}finally{saveGame=save;}return{same:JSON.stringify(state)===before,paused:__MISTRAL_DEBUG.v073GabiansInfo().paused};},
 companions(){const before=JSON.stringify(state.v073Gabians),active=state.player.activeCompanion;state.player.activeCompanion='roux';state.flags.rouxAttackCooldown=0;state.flags.rouxPos=[-10,0,-7];updateCompanion(2);state.player.activeCompanion=active;return JSON.stringify(state.v073Gabians)===before;},
 run(type,id,method){const point=MistralGabians.actionPoint(type,id);this.near(point);if(!__MISTRAL_DEBUG.v073GabiansAction(type,id,method))throw Error('Native adapter refused '+type+': '+V027.message);},
 finishBranch(n){
  for(const id of MistralGabians.IDS.slice(0,n))this.kill(id);
  const falling=MistralGabians.IDS.slice(0,n).every(id=>state.v073Gabians.birds[id].phase==='falling');
  for(const id of MistralGabians.IDS.slice(n))this.run('lure',id);
  this.ticks(180);
  for(const id of MistralGabians.IDS)this.run('lower',id,'manuel');
  this.ticks(30);
  for(const id of Object.keys(MistralGabians.OBJECTS)){this.run('take',id);this.run('return',id);}
  const caps=state.player.caps;this.run('finish');const result={falling,capsBefore:caps,info:this.info()};this.save();return result;
 },
 fallingSave(){this.kill('filets');this.ticks(2);this.save();const before=JSON.stringify(state.v073Gabians);this.reload();return before===JSON.stringify(state.v073Gabians)&&state.v073Gabians.birds.filets.phase==='falling';},
 projectileSave(){this.threat('menu');mode='PLAYING';state.player.pos=[25,1.65,23];for(let i=0;i<6;i++)updateEnemies(.2);const active=!!state.v073Gabians.birds.filets.shot;this.save();const before=JSON.stringify(state.v073Gabians);this.reload();return active&&before===JSON.stringify(state.v073Gabians);},
 stale(){const callback=dialogueState.choices.find(c=>c.text.startsWith('Prendre')).onChoose;this.run('take','clef');const before=JSON.stringify(state);callback();return before===JSON.stringify(state);},
 render(which='court'){weaponKick=0;__MISTRAL_DEBUG.v056FirstPersonRender?.();debugDismissDialogue();for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';const e=world.enemies.find(e=>e.g73Id==='filets'),c=which==='bird'?{pos:[e.pos[0]+2.5,e.pos[1]+1.5,e.pos[2]+3.8],target:[e.pos[0],e.pos[1]+.8,e.pos[2]]}:which==='nora'?{pos:[-4,2.6,27],target:[-8,1.7,22]}:{pos:[24,7,21],target:[0,2,-8]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:62},currentEnv());return renderer.constructor.name;}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralGabians' in html
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
  r=ev('(id)=>__G73_QA.near(id)',id);print('NEAR',id,r,flush=True);check('native E interaction '+id,r['selected']==(expected or 'g73:'+id) and r['los'] and not r['collision']);page.keyboard.press('e')
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v073GabiansInfo');ev('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  port=ev('__G73_QA.setup()');check('existing Vieux-Port representative used',port['site']=='v042-marseille-caravan-01');old=ev('__G73_QA.info().old');page.keyboard.press('e');check('historical conversation preserved',page.locator('#dialogueChoices button').filter(has_text='Parler du secteur').count()==1);choose('Consigne ·');check('failed entry restores exact origin',ev('__G73_QA.failEntry()'));choose('Rejoindre la consigne')
  check('actual new court and two regional actors',ev('__G73_QA.info().local') and len(ev('__G73_QA.info().enemies'))==2)
  ev('__MISTRAL_DEBUG.v073GabiansOpen()');check('new field journal visible','Les objets trouvés' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-carnet.png'));page.set_viewport_size({'width':390,'height':844});check('390px journal no horizontal overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
  go('sortie');check('early return restores retained origin',ev('__LYS_QA.atOrigin()'));ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Consigne ·');choose('Rejoindre la consigne')
  ev('__G73_QA.render()');page.screenshot(path=str(a.output/'03-consigne.png'));ev('__G73_QA.render("bird")');page.screenshot(path=str(a.output/'04-gabian.png'))
  go('nora','npc:g73:nora');choose('Aider Nora');choose('Revenir.');go('registre');choose('Noter à qui');choose('Revenir.');initial=ev('__G73_QA.snapshot()')
  check('native gabian rig and wing target',any(p['label']=='AILE GAUCHE' for p in ev('__G73_QA.rig()')))
  for k in ['hit','dodge','cover','menu']:
   ev('(s)=>__G73_QA.restore(s)',initial);r=ev('(k)=>__G73_QA.threat(k)',k);print('THREAT',k,r,flush=True);check('locked corrosive drop '+k,r['announced'] and (r['after']<r['before'] if k=='hit' else r['after']==r['before']))
  ev('(s)=>__G73_QA.restore(s)',initial);check('refused impact rolls back health and ledger',ev('__G73_QA.failHit()'));r=ev('__G73_QA.shot()');print('SHOT',r,flush=True);check('native pistol consumes ammunition and hits bird',r['after']<r['before'] and r['ammoAfter']<r['ammoBefore'])
  ev('(s)=>__G73_QA.restore(s)',initial);effects=ev('__G73_QA.effects()');ev('__G73_QA.reload()');check('wings burning slow and position saved exactly',ev('__G73_QA.info().ledger.birds.filets')==effects and effects['wings']==25 and effects['burn']==2800)
  ev('(s)=>__G73_QA.restore(s)',initial);go('basket:filets');choose('Prendre : Clé');check('high basket cannot be looted',ev('__G73_QA.info().ledger.objects.clef')=='nest');choose('Revenir.');go('lower:filets');choose('Descendre à la manivelle');check('guarding bird prevents lowering',ev('__G73_QA.info().ledger.platforms.filets.method') is None);choose('Revenir.')
  walk=ev('__LYS_QA.walk([[0,1.65,25],[25.5,1.65,25],[25.5,1.65,-22]])');check('lateral route physically traversable',abs(walk[-1][0]-25.5)<.3 and abs(walk[-1][2]+22)<.3)
  go('lure:filets');r=ev('__G73_QA.fail("lure","filets")');check('failed lure save consumes nothing',r['same'] and not r['result']);choose('Déposer les restes');check('lure starts flight not instant arrival',ev('__G73_QA.info().ledger.birds.filets.phase')=='lure');check('flight respects solid obstacle',ev('__G73_QA.blockedFlight()'));check('companion ignores diverted bird',ev('__G73_QA.companions()'))
  ev('__G73_QA.ticks(8)');ev('__G73_QA.save()');mid=ev('__G73_QA.info().ledger');ev('__G73_QA.reload()');check('mid-flight exact save/load',ev('__G73_QA.info().ledger')==mid);checkpoint=ev('__G73_QA.snapshot()');ev('__G73_QA.setNearArrival()');r=ev('__G73_QA.failCheckpoint()');check('refused arrival retains bird and pauses safely',r['same'] and r['paused']);go('nora','npc:g73:nora');choose('Retenter la sauvegarde');choose('Revenir.');check('retry resumes the local simulation',not ev('__G73_QA.info().paused'));ev('(s)=>__G73_QA.restore(s)',checkpoint)
  go('lure:tole');choose('Déposer les restes');ev('__G73_QA.ticks(150)');print('FLIGHT',ev('__G73_QA.info().ledger.birds'),flush=True);check('two birds reach distinct feeding points',all(b['phase']=='fed' for b in ev('__G73_QA.info().ledger.birds').values()))
  go('lower:filets');choose('Descendre à la manivelle');check('basket does not teleport on action',ev('__G73_QA.info().ledger.platforms.filets.drop')==0);r=ev('__G73_QA.underBasket()');print('BASKET',r,flush=True);check('moving basket stops before occupied player volume',0<r['first']<3500 and r['first']==r['second'] and 'filets' in r['blocked']);ev('__G73_QA.save()');mid=ev('__G73_QA.info().ledger');ev('__G73_QA.reload()');check('mid-descent exact save/load',ev('__G73_QA.info().ledger')==mid);ev('__G73_QA.ticks(30)')
  go('lower:tole');scrap=ev('__G73_QA.info().inv.scrap');choose('Régler le réducteur');ev('__G73_QA.ticks(15)');check('technical reduction consumes one scrap',ev('__G73_QA.info().inv.scrap')==scrap-1);check('both basket collision volumes lowered',all(abs(c['minY']-.54)<.001 for c in ev('__G73_QA.info().baskets')))
  for point,label in [('basket:filets','Clé'),('basket:filets','Bague'),('basket:tole','Sifflet')]:go(point);choose('Prendre : '+label);choose('Revenir.')
  check('all three real objects removed from nests and carried',ev('__G73_QA.info().objects')==0 and all(v=='bag' for v in ev('__G73_QA.info().ledger.objects').values()));ev('__G73_QA.save()');ev('__G73_QA.reload()');check('carried objects persist without refill',all(v=='bag' for v in ev('__G73_QA.info().ledger.objects').values()))
  for label in ['Clé','Bague','Sifflet']:go('nora','npc:g73:nora');choose('Rendre : '+label);check('personal return line '+label,'Merci' in page.locator('#dialogueLine').inner_text());choose('Revenir.')
  check('three objects visible on the return counter',ev('__G73_QA.info().returned')==3);go('nora','npc:g73:nora');caps=ev('__G73_QA.info().caps');choose('Faire le point');choose('Revenir.');check('exactly 45 capsules with truthful survivor ending',ev('__G73_QA.info().caps')==caps+45 and ev('__G73_QA.info().ledger.outcome')=='vivants');ev('__G73_QA.reload()');go('nora','npc:g73:nora');check('no repeat reward after load',page.locator('#dialogueChoices button').filter(has_text='Faire le point').count()==0);choose('Revenir.');check('all thirteen previous ledgers unchanged',ev('__G73_QA.info().old')==old)
  ev('__G73_QA.render()');page.screenshot(path=str(a.output/'05-paniers-descendus.png'));ev('__G73_QA.render("nora")');page.screenshot(path=str(a.output/'06-nora.png'));check('no JavaScript or adapter exceptions',not errors and ev('__G73_QA.info().error') is None)
  ev('(s)=>__G73_QA.restore(s)',initial);check('corpse saved during descent without resurrection',ev('__G73_QA.fallingSave()'))
  ev('(s)=>__G73_QA.restore(s)',initial);check('released projectile survives save/load in flight',ev('__G73_QA.projectileSave()'))
  for n,outcome in [(1,'mixte'),(2,'abattus')]:
   ev('(s)=>__G73_QA.restore(s)',initial);r=ev('(n)=>__G73_QA.finishBranch(n)',n);check('native casualty branch '+str(n),r['falling'] and r['info']['ledger']['outcome']==outcome and r['info']['caps']==r['capsBefore']+45);ev('__G73_QA.reload()');check('casualty count remains after load '+str(n),sum(not e['alive'] for e in ev('__G73_QA.info().enemies'))==n and ev('__G73_QA.info().ledger.outcome')==outcome)
  check('no exception across all three endings',not errors and ev('__G73_QA.info().error') is None)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
  (a.output/'GABIANS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',ev('window.__G73_QA?.info()'),flush=True);raise
 finally:browser.close()
