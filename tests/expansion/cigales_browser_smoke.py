"""Real encounter/UI/targeting smoke, scripted positions and synthetic relay.
No geographic IGN traversal or human playtest claimed. Isolated MemoryStorage.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/cigales/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
source=ast.parse((root/'tests/expansion/lys_browser_smoke.py').read_text())
base_bridge=next(ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__C71_QA={
 setup(){__LYS_QA.setup();state.v071Cigales=MistralCigales.fresh();return this.port();},
 port(){const site=v042Site(MistralCigales.RELAY);__LYS_QA.port();world.id=site.macro;state.player.zone=site.macro;state.v042.discovered[site.id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();const n=world.npcs[0];n.v042Site=site.id;V042_RUNTIME.npcData.set(n.id,{siteId:site.id,name:'Relais de terrain',role:'éclaireuse',index:0});globalThis.__LYS_PORT=world;globalThis.__LYS_POS=state.player.pos.slice();updateSelectedInteractable();return {selected:selectedInteractable?.id,site:site.id};},
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v071CigalesInfo().points[id];state.player.pos=[p[0],1.65,p[2]+2];state.player.yaw=0;state.player.pitch=-.18;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,1.65),los:lineOfSight(state.player.pos,[p[0],1.25,p[2]+.7])};},
 info(){return {ledger:state.v071Cigales,caps:state.player.caps,inv:state.inventory,hp:state.player.hp,ap:state.player.ap,local:!!world.v071Cigales,enemies:__MISTRAL_DEBUG.v071CigalesInfo().enemies,old:JSON.stringify([state.v070Secours,state.v069Parts,state.v068Lys,state.v067Devoir,state.v066Voisins,state.v065Notaires,state.v064Mutuelle,state.v063Radieuse,state.v062Pharmacy,state.v061Poste,state.v060Council]),error:__MISTRAL_DEBUG.v071CigalesInfo().error};},
 snapshot(){return JSON.stringify(state);},restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';inCombat=false;return this.info();},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 fail(type,id){const s=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v071CigalesAction(type,id);}finally{saveGame=save;}return {same:JSON.stringify(state)===s,result};},
 ticks(n=1){mode='PLAYING';for(let i=0;i<n;i++)updateEnemies(.2);return this.info();},
 save(){return saveGame(false);},
 failEntry(){const old=saveGame,w=world,p=state.player.pos.slice(),l=JSON.stringify(state.v071Cigales);saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre le relais')).onChoose();}finally{saveGame=old;}return world===w&&state.v042.activeInterior===null&&JSON.stringify(state.player.pos)===JSON.stringify(p)&&JSON.stringify(state.v071Cigales)===l;},
 threaten(){const e=world.enemies.find(e=>e.c71Id==='centre');state.player.pos=[0,1.65,-3];mode='PLAYING';for(const a of world.enemies){a.c71Wind=null;a.c71Cooldown=999;}e.c71Cooldown=0;updateEnemies(.1);return !!e.c71Wind;},
 failArrival(){for(const e of world.enemies)if(e.c71Id!=='ouest')e.alive=false;const a=state.v071Cigales.actors.ouest;a.travel=9800;const e=world.enemies.find(e=>e.c71Id==='ouest');e.pos=MistralCigales.position('ouest',a);const old=saveGame;saveGame=()=>false;try{mode='PLAYING';updateEnemies(.2);}finally{saveGame=old;}return {travel:state.v071Cigales.actors.ouest.travel,alive:e.alive,blocked:__MISTRAL_DEBUG.v071CigalesInfo().blocked};},
 threat(kind){debugDismissDialogue();const e=world.enemies.find(e=>e.c71Id==='centre');for(const a of world.enemies){a.c71Wind=null;a.c71Cooldown=999;}e.c71Cooldown=0;state.player.pos=[0,1.65,-3];state.player.hp=100;state.player.ap=80;mode='PLAYING';updateEnemies(.1);const announced=!!e.c71Wind;
  if(kind==='dodge')state.player.pos=[6,1.65,-3];if(kind==='wall')state.player.pos=[0,1.65,4];if(kind==='menu')mode='PIP';if(kind==='distance')state.player.pos=[0,1.65,15];
  const before={hp:state.player.hp,ap:state.player.ap};for(let i=0;i<9;i++)updateEnemies(.2);const after={hp:state.player.hp,ap:state.player.ap};return {announced,before,after,wind:!!e.c71Wind};
 },
 rig(){const e=world.enemies.find(e=>e.c71Id==='centre');return v025Rig(e).parts.map(p=>({id:p.id,label:p.label,center:p.center}));},
 shot(){debugDismissDialogue();const e=world.enemies.find(e=>e.c71Id==='centre');state.player.pos=[e.pos[0],1.65,e.pos[2]+4];const part=enemyHitParts(e).find(p=>p.id==='body'),d=vNorm(vSub(part.center,state.player.pos));state.player.yaw=Math.atan2(d[0],-d[2]);state.player.pitch=Math.asin(d[1]);mode='PLAYING';onGround=true;reloadTimer=0;V020.cooldown=0;V020.reload=null;state.player.weaponId='pistol10';setEquipmentCondition('weapon','pistol10',100);state.player.ammoClip=12;state.player.ammoReserve=20;state.player.clipSize=12;const before=e.health,ammo=state.player.ammoClip;fireWeapon();return {before,after:e.health,ammoBefore:ammo,ammoAfter:state.player.ammoClip,target:acquireShotTarget(state.player.pos,d)?.enemy?.id};},
 wound(id,part='leg_l'){mode='PLAYING';damageEnemy(world.enemies.find(e=>e.c71Id===id),5,part);return this.info();},
 kill(id){mode='PLAYING';damageEnemy(world.enemies.find(e=>e.c71Id===id),200,'body');return this.info();},
 nativeEffects(){const e=world.enemies.find(e=>e.c71Id==='centre');mode='PLAYING';state.player.pos=[25,1.65,24];applyEnemyStatus(e,'burning',3);applyEnemyStatus(e,'slow',3);updateEnemies(.2);saveGame(false);return this.info().ledger.actors.centre;},
 companions(){const before=JSON.stringify(state.v071Cigales),active=state.player.activeCompanion;state.player.activeCompanion='roux';state.flags.rouxAttackCooldown=0;state.flags.rouxPos=[0,0,-7];updateCompanion(2);state.player.activeCompanion=active;return JSON.stringify(state.v071Cigales)===before;},
 failHit(){const e=world.enemies.find(e=>e.c71Id==='ouest'),old=JSON.stringify(state.v071Cigales),save=saveGame;saveGame=()=>false;try{damageEnemy(e,10,'body');}finally{saveGame=save;}return old===JSON.stringify(state.v071Cigales)&&e.health===72;},
 blockedRetreat(){const old=state.v071Cigales.actors.ouest.travel,p=MistralCigales.position('ouest',state.v071Cigales.actors.ouest);const c=addCollider(world,p[0],p[2]-.4,3,1,{minY:0,maxY:3});updateEnemies(.2);world.colliders=world.colliders.filter(x=>x!==c);return state.v071Cigales.actors.ouest.travel===old;},
 render(which='wide'){debugDismissDialogue();for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';const c=which==='wide'?{pos:[22,5,17],target:[0,1,-10]}:which==='insect'?{pos:[3,2.4,-2],target:[0,1,-8]}:{pos:[20,4,-1],target:[0,1,-17]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:62},currentEnv());return renderer.constructor.name;}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralCigales' in html
html=html.replace(marker,base_bridge+'\n'+bridge+'\n'+marker);checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7000)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v071CigalesInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  def ev(s,arg=None):return page.evaluate(s,arg)
  def choose(text):print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected=None):
   d=ev('(id)=>__C71_QA.near(id)',id);print('NEAR',id,d,flush=True);check('reachable E interaction '+id,d['selected']==(expected or 'c71:'+id) and not d['collision'] and d['los']);page.keyboard.press('e')
  port=ev('__C71_QA.setup()');check('actual Font de Mai identity retained',port['site']=='v042-garlaban-caravan-01');old=ev('__C71_QA.info().old');page.keyboard.press('e');choose('Vigies · Le faux midi');check('failed entry save preserves departure',ev('__C71_QA.failEntry()'));choose('Rejoindre le relais')
  check('dedicated scene with three native targetable creatures',ev('__C71_QA.info().local') and len(ev('__C71_QA.info().enemies'))==3)
  ev('__MISTRAL_DEBUG.v071CigalesOpen()');check('field journal accessible','Le faux midi' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-carnet.png'));page.set_viewport_size({'width':390,'height':844});check('390px no page-wide overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
  go('sortie');check('early exit restores exact retained Font de Mai',ev('__LYS_QA.atOrigin()'));ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Vigies · Le faux midi');choose('Rejoindre le relais')
  ev('__C71_QA.render()');page.screenshot(path=str(a.output/'03-relais.png'));ev('__C71_QA.render("insect")');page.screenshot(path=str(a.output/'04-cymbalier.png'))
  go('aline','npc:c71:aline');choose('Chercher la cause');choose('Revenir.')
  for id in ['mue','signal']:go(id);choose('Consigner cette observation');choose('Revenir.')
  check('two observations retained',len(ev('__C71_QA.info().ledger.notes'))==2);start=ev('__C71_QA.snapshot()')
  rig=ev('__C71_QA.rig()');check('real regional target groups, not humanoid placeholder',any(p['label']=='TYMBAL' for p in rig) and any(p['label']=='AILE GAUCHE' for p in rig) and len(rig)>=8)
  pulse=ev('__C71_QA.threat("hit")');check('telegraphed crissement actually damages HP and AP',pulse['announced'] and pulse['after']['hp']<pulse['before']['hp'] and pulse['after']['ap']<pulse['before']['ap'])
  check('new pulse has visible warning before discharge',ev('__C71_QA.threaten()'));ev('__C71_QA.render("insect")');page.screenshot(path=str(a.output/'05-crissement.png'))
  for kind in ['dodge','wall','distance']:
   r=ev('(kind)=>__C71_QA.threat(kind)',kind);check('crissement avoidable by '+kind,r['announced'] and r['after']==r['before'])
  r=ev('__C71_QA.threat("menu")');check('menus stop windup and damage',r['after']==r['before'] and r['wind']);ev('(s)=>__C71_QA.restore(s)',start)
  check('save refusal cancels creature damage',ev('__C71_QA.failHit()'))
  shot=ev('__C71_QA.shot()');print('SHOT',shot,flush=True);check('native gun uses actual aim hitboxes and costs ammunition',shot['after']<shot['before'] and shot['ammoAfter']<shot['ammoBefore']);ev('(s)=>__C71_QA.restore(s)',start)
  status=ev('__C71_QA.nativeEffects()');ev('__C71_QA.reload()');check('native burning and slowing persist and tick on the encounter',ev('__C71_QA.info().ledger.actors.centre')==status and status['hp']<7200 and status['burn']==2800 and status['slow']==2800);ev('(s)=>__C71_QA.restore(s)',start)
  # No casualties path, via the side lane, not teleportation through a cover wall.
  path=ev('__LYS_QA.walk([[0,1.65,24],[26,1.65,24],[26,1.65,-25],[0,1.65,-25]])');print('WALK',path,flush=True);check('native side lane reaches back of relay',abs(path[-1][0])<.3 and abs(path[-1][2]+25)<.3)
  go('sectionneur');failure=ev('__C71_QA.fail("cut","manuel")');check('save failure leaves amplifier active',failure['same'] and not failure['result']);choose('Couper le relais manuellement');check('cut does not instantly remove insects',sum(e['alive'] for e in ev('__C71_QA.info().enemies'))==3)
  check('companions stop automatically attacking retreating wildlife',ev('__C71_QA.companions()'))
  check('retreat checks physical obstacle',ev('__C71_QA.blockedRetreat()'));ev('__C71_QA.ticks(5)');check('survivors move gradually',0<ev('__C71_QA.info().ledger.actors.ouest.travel')<10000)
  # Reload an actual save written by the embedded game, not a regenerated fixture.
  ev('__C71_QA.save()');mid=ev('__C71_QA.info().ledger');ev('__C71_QA.reload()');check('intermediate retreat persisted',ev('__C71_QA.info().ledger')==mid)
  ev('__C71_QA.ticks(40)');check('all survivors genuinely reached exits',all(a['travel']==10000 for a in ev('__C71_QA.info().ledger.actors').values()))
  go('aline','npc:c71:aline');caps=ev('__C71_QA.info().caps');choose('Remettre le constat');choose('Revenir.');check('nonlethal outcome and single 65 caps',ev('__C71_QA.info().ledger.outcome')=='retrait' and ev('__C71_QA.info().caps')==caps+65)
  ev('__C71_QA.reload()');go('aline','npc:c71:aline');check('no repeated reward on reload',page.locator('#dialogueChoices button').filter(has_text='Remettre le constat').count()==0);choose('Revenir.');check('old political and rescue ledgers unchanged',ev('__C71_QA.info().old')==old)
  # Injuries persist without being misreported as deaths. Check saved arrival failure separately.
  ev('(s)=>__C71_QA.restore(s)',start);ev('__C71_QA.wound("ouest")');wound=ev('__C71_QA.info().ledger.actors.ouest');ev('__C71_QA.reload()');check('native part damage persists across actual save load',ev('__C71_QA.info().ledger.actors.ouest')==wound and wound['legs']>0)
  go('sectionneur');choose('Couper le relais manuellement');ev('__C71_QA.ticks(5)');check('damaged legs slow authored retreat',ev('__C71_QA.info().ledger.actors.ouest.travel')<ev('__C71_QA.info().ledger.actors.centre.travel'));ev('__C71_QA.save()');checkpoint=ev('__C71_QA.snapshot()');failure=ev('__C71_QA.failArrival()');check('failed arrival checkpoint does not record a departure',failure['travel']==9800 and failure['alive'] and failure['blocked']);go('aline','npc:c71:aline');choose('Retenter la sauvegarde');choose('Revenir.');check('checkpoint retry resumes the blocked encounter',not ev('__MISTRAL_DEBUG.v071CigalesInfo().blocked'));ev('(s)=>__C71_QA.restore(s)',checkpoint);ev('__C71_QA.ticks(50)');go('aline','npc:c71:aline');choose('Remettre le constat');choose('Revenir.');check('wounded survivors remain a no-death conclusion',ev('__C71_QA.info().ledger.outcome')=='retrait')
  # Mixed and all-combat outcomes use real target damage adapter, not rewritten death flags.
  for n in [1,3]:
   ev('(s)=>__C71_QA.restore(s)',start)
   for id in ['ouest','centre','est'][:n]:ev('(id)=>__C71_QA.kill(id)',id)
   go('sectionneur');qty=ev('__C71_QA.info().inv.circuitry');choose('Isoler et relever');check('technical alternative costs one circuit '+str(n),ev('__C71_QA.info().inv.circuitry')==qty-1);ev('__C71_QA.ticks(40)');go('aline','npc:c71:aline');choose('Remettre le constat');choose('Revenir.');check('casualty count reflected in conclusion '+str(n),ev('__C71_QA.info().ledger.outcome')==('mixte' if n==1 else 'abattues'))
  check('no JavaScript or adapter errors',not errors and ev('__C71_QA.info().error') is None)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Real authored scene, existing cicada rig, native E/dialogue/shooting/hitboxes/collisions, custom encounter FSM and original save routines. Scripted guide/aim positions; synthetic Font de Mai relay; isolated MemoryStorage, software renderer. No real IGN traversal or human campaign.'}
  (a.output/'CIGALES_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',ev('window.__C71_QA?.info()'),flush=True);raise
 finally:browser.close()
