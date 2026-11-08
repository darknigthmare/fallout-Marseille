"""Production rat depot and native UI/combat/save smoke. Scripted actor positions,
synthetic Saint-Charles relay, isolated MemoryStorage and software renderer.
Not a human full campaign or an IGN route certification.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/rats/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
def get_bridge(file):
 t=ast.parse(file.read_text());return next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='bridge' for k in n.targets))
base_bridge=get_bridge(root/'tests/expansion/lys_browser_smoke.py')
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__R72_QA={
 setup(){__LYS_QA.setup();state.v072Rats=MistralRats.fresh();return this.port();},
 port(){const site=v042Site(MistralRats.RELAY);__LYS_QA.port();world.id=site.macro;state.player.zone=site.macro;state.v042.discovered[site.id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();const n=world.npcs[0];n.v042Site=site.id;V042_RUNTIME.npcData.set(n.id,{siteId:site.id,name:'Représentant de Saint-Charles',role:'artisan',index:0});globalThis.__LYS_PORT=world;globalThis.__LYS_POS=state.player.pos.slice();updateSelectedInteractable();return {selected:selectedInteractable?.id,site:site.id};},
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v072RatsInfo().points[id];state.player.pos=[p[0],1.65,p[2]+2];state.player.yaw=0;state.player.pitch=-.18;onGround=true;mode='PLAYING';updateSelectedInteractable();return{selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,1.65),los:lineOfSight(state.player.pos,[p[0],1.25,p[2]+.7])};},
 info(){return {ledger:state.v072Rats,caps:state.player.caps,inv:state.inventory,hp:state.player.hp,local:!!world.v072Rats,old:JSON.stringify([state.v071Cigales,state.v070Secours,state.v069Parts,state.v068Lys,state.v067Devoir,state.v066Voisins,state.v065Notaires,state.v064Mutuelle,state.v063Radieuse,state.v062Pharmacy,state.v061Poste,state.v060Council]),hazards:world.hazards.filter(h=>h.id.startsWith('r72:')).length,gate:world.colliders.filter(c=>c.r72Gate).map(c=>!!c.disabled),lamps:world.staticDraws.filter(d=>d.r72Light&&d.emissive>.5).length,spares:world.staticDraws.filter(d=>d.r72Spare&&!d.hidden).length,repairs:world.staticDraws.filter(d=>d.r72Repair&&d.color[1]>.6).length,enemies:__MISTRAL_DEBUG.v072RatsInfo().enemies,error:__MISTRAL_DEBUG.v072RatsInfo().error};},
 snapshot(){return JSON.stringify(state);},restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';inCombat=false;return this.info();},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},save(){return saveGame(false);},
 gateBlocked(){return collidesAt(0,-18,.38,1.65);},
 fail(type,id){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v072RatsAction(type,id);}finally{saveGame=save;}return{same:JSON.stringify(state)===before,result};},
 failEntry(){const save=saveGame,w=world,p=state.player.pos.slice(),l=JSON.stringify(state.v072Rats);saveGame=()=>false;try{dialogueState.choices.find(c=>c.text.startsWith('Rejoindre le dépôt')).onChoose();}finally{saveGame=save;}return world===w&&state.v042.activeInterior===null&&JSON.stringify(state.player.pos)===JSON.stringify(p)&&JSON.stringify(state.v072Rats)===l;},
 ticks(n=1){mode='PLAYING';state.player.pos=[25,1.65,23];for(let i=0;i<n;i++)updateEnemies(.2);return this.info();},
 threat(kind){debugDismissDialogue();const e=world.enemies.find(e=>e.r72Id==='armoire');for(const r of world.enemies){r.r72Wind=null;r.r72Cooldown=999;}e.r72Cooldown=0;state.player.pos=[e.pos[0],1.65,e.pos[2]+1.6];state.player.hp=100;mode='PLAYING';updateEnemies(.1);const announced=!!e.r72Wind;let wall;
 if(kind==='dodge')state.player.pos[0]+=3;if(kind==='distance')state.player.pos[2]+=4;if(kind==='wall')wall=addCollider(world,e.pos[0],e.pos[2]+.8,2,.15,{minY:0,maxY:3});if(kind==='menu')mode='PIP';
 const before=state.player.hp;for(let i=0;i<4;i++)updateEnemies(.2);const after=state.player.hp;if(wall)world.colliders=world.colliders.filter(c=>c!==wall);return{announced,before,after,wind:!!e.r72Wind};},
 rig(){return v025Rig(world.enemies.find(e=>e.r72Id==='armoire')).parts.map(p=>({id:p.id,label:p.label}));},
 shot(){debugDismissDialogue();const e=world.enemies.find(e=>e.r72Id==='armoire');state.player.pos=[e.pos[0],1.65,e.pos[2]+3];const part=enemyHitParts(e).find(p=>p.id==='body'),d=vNorm(vSub(part.center,state.player.pos));state.player.yaw=Math.atan2(d[0],-d[2]);state.player.pitch=Math.asin(d[1]);mode='PLAYING';onGround=true;reloadTimer=0;V020.cooldown=0;V020.reload=null;state.player.weaponId='pistol10';setEquipmentCondition('weapon','pistol10',100);state.player.ammoClip=12;state.player.ammoReserve=20;state.player.clipSize=12;const before=e.health,ammo=state.player.ammoClip;fireWeapon();return{before,after:e.health,ammoBefore:ammo,ammoAfter:state.player.ammoClip};},
 kill(id){mode='PLAYING';damageEnemy(world.enemies.find(e=>e.r72Id===id),300,'body');return this.info();},
 wound(id){mode='PLAYING';damageEnemy(world.enemies.find(e=>e.r72Id===id),3,'fore_l');return this.info();},
 effects(){const e=world.enemies.find(e=>e.r72Id==='armoire');mode='PLAYING';state.player.pos=[25,1.65,23];applyEnemyStatus(e,'burning',3);applyEnemyStatus(e,'slow',3);updateEnemies(.2);saveGame(false);return this.info().ledger.actors.armoire;},
 blockedMove(){const a=state.v072Rats.actors.voie,e=world.enemies.find(e=>e.r72Id==='voie'),old=a.z,c=addCollider(world,e.pos[0],e.pos[2]-.3,3,.8,{minY:0,maxY:3});updateEnemies(.2);world.colliders=world.colliders.filter(o=>o!==c);return state.v072Rats.actors.voie.z===old;},
 failArrival(){for(const e of world.enemies)if(e.r72Id!=='voie')e.alive=false;const a=state.v072Rats.actors.voie;a.z=-21900;const e=world.enemies.find(e=>e.r72Id==='voie');e.pos=MistralRats.position('voie',a);const save=saveGame;saveGame=()=>false;try{mode='PLAYING';updateEnemies(.2);}finally{saveGame=save;}return{z:state.v072Rats.actors.voie.z,alive:e.alive,paused:__MISTRAL_DEBUG.v072RatsInfo().paused};},
 companions(){const before=JSON.stringify(state.v072Rats),active=state.player.activeCompanion;state.player.activeCompanion='roux';state.flags.rouxAttackCooldown=0;state.flags.rouxPos=[0,0,-7];updateCompanion(2);state.player.activeCompanion=active;return JSON.stringify(state.v072Rats)===before;},
 failHit(){const e=world.enemies.find(e=>e.r72Id==='voie'),before=JSON.stringify(state.v072Rats),hp=e.health,save=saveGame;saveGame=()=>false;try{damageEnemy(e,7,'body');}finally{saveGame=save;}return before===JSON.stringify(state.v072Rats)&&e.health===hp;},
 render(which='depot'){debugDismissDialogue();for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;mode='PLAYING';const c=which==='rat'?{pos:[2,1.5,-4],target:[0,.4,-8]}:which==='refuge'?{pos:[19,4,-14],target:[0,.7,-22]}:{pos:[23,5,17],target:[0,1,-10]};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:62},currentEnv());return renderer.constructor.name;}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralRats=' in html
html=html.replace(marker,base_bridge+'\n'+bridge+'\n'+marker)
checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7000)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v072RatsInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  def ev(s,arg=None):return page.evaluate(s,arg)
  def choose(text):print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected=None):
   r=ev('(id)=>__R72_QA.near(id)',id);print('NEAR',id,r,flush=True);check('physical interaction '+id,r['selected']==(expected or 'r72:'+id) and r['los'] and not r['collision']);page.keyboard.press('e')
  port=ev('__R72_QA.setup()');check('existing Saint-Charles relay identity',port['site']=='v042-marseille-caravan-02');old=ev('__R72_QA.info().old');page.keyboard.press('e');choose('Aiguilleurs ·');check('failed entry restores exact origin',ev('__R72_QA.failEntry()'));choose('Rejoindre le dépôt')
  check('new depot and three native rat actors',ev('__R72_QA.info().local') and len(ev('__R72_QA.info().enemies'))==3)
  ev('__MISTRAL_DEBUG.v072RatsOpen()');check('field journal visible','Les dents du réseau' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-carnet.png'));page.set_viewport_size({'width':390,'height':844});check('390px layout no horizontal overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
  go('sortie');check('early exit returns to exact retained scene',ev('__LYS_QA.atOrigin()'));ev('__LYS_QA.focusPort()');page.keyboard.press('e');choose('Aiguilleurs ·');choose('Rejoindre le dépôt')
  ev('__R72_QA.render()');page.screenshot(path=str(a.output/'03-depot-avant.png'));ev('__R72_QA.render("rat")');page.screenshot(path=str(a.output/'04-rat-cable.png'))
  go('djamila','npc:r72:djamila');choose('Examiner « Les dents');choose('Revenir.')
  for id in ['morsures','plan']:go(id);choose('Consigner cette observation');choose('Revenir.')
  start=ev('__R72_QA.snapshot()');check('two observations persisted',len(ev('__R72_QA.info().ledger.notes'))==2)
  check('regional rat body and quadruped hitboxes',any(p['label']=='CORPS CÂBLÉ' for p in ev('__R72_QA.rig()')) and any(p['id']=='fore_l' for p in ev('__R72_QA.rig()')))
  ev('__R72_QA.ticks(3)');check('patrol positions actually change',ev('__R72_QA.info().ledger.actors.voie.z')!=-8000);ev('__R72_QA.save()');patrol=ev('__R72_QA.info().ledger');ev('__R72_QA.reload()');check('patrol exact after reload',ev('__R72_QA.info().ledger')==patrol);ev('(s)=>__R72_QA.restore(s)',start)
  for k in ['hit','dodge','distance','wall','menu']:
   ev('(s)=>__R72_QA.restore(s)',start);r=ev('(k)=>__R72_QA.threat(k)',k);check('telegraphed bite '+k,r['announced'] and (r['after']<r['before'] if k=='hit' else r['after']==r['before']))
  ev('(s)=>__R72_QA.restore(s)',start);check('hit rollback when storage refuses',ev('__R72_QA.failHit()'));shot=ev('__R72_QA.shot()');print('SHOT',shot,flush=True);check('native gun and ammunition hit real rat',shot['after']<shot['before'] and shot['ammoAfter']<shot['ammoBefore']);ev('(s)=>__R72_QA.restore(s)',start)
  effects=ev('__R72_QA.effects()');ev('__R72_QA.reload()');check('burn and slow persist without cure',ev('__R72_QA.info().ledger.actors.armoire')==effects and effects['hp']<5800 and effects['burn']==2800);ev('(s)=>__R72_QA.restore(s)',start)
  check('three cable hazards before isolation',ev('__R72_QA.info().hazards')==3)
  go('kit');choose('Prélever les deux gaines');choose('Revenir.');check('finite spare sleeves disappear from crate',ev('__R72_QA.info().spares')==0)
  go('eclairage');choose('Remplacer la gaine');check('unsafe repair refused',ev('__R72_QA.info().ledger.repairs')==[]);choose('Revenir.')
  go('tableau');failure=ev('__R72_QA.fail("isolate","manuel")');check('failed isolation keeps cable danger',failure['same'] and not failure['result'] and ev('__R72_QA.info().hazards')==3);choose('Isoler le tableau manuellement');choose('Revenir.');check('actual electrical hazards removed',ev('__R72_QA.info().hazards')==0)
  route=ev('__LYS_QA.walk([[0,1.65,24],[25.5,1.65,24],[25.5,1.65,-15]])');check('side lane traversable with native collisions',abs(route[-1][0]-25.5)<.3 and abs(route[-1][2]+15)<.3)
  check('refuge barrier blocks player before opening',ev('__R72_QA.gateBlocked()'))
  go('gate');choose('Ouvrir le volet');choose('Revenir.');check('physical barrier disappears with collision',ev('__R72_QA.info().gate')==[True] and not ev('__R72_QA.gateBlocked()'))
  route=ev('__LYS_QA.walk([[25.5,1.65,-15],[25.5,1.65,-25],[0,1.65,-25]])');check('opened back passage traversable',abs(route[-1][0])<.3 and abs(route[-1][2]+25)<.3)
  go('bait');choose('Poser l’appât');check('bait starts movement without instant disappearance',sum(e['alive'] for e in ev('__R72_QA.info().enemies'))==3);check('companions do not attack diverting rats',ev('__R72_QA.companions()'))
  check('refuge movement respects obstacle',ev('__R72_QA.blockedMove()'));ev('__R72_QA.ticks(10)');check('retreat progress is gradual',-22000<ev('__R72_QA.info().ledger.actors.voie.z')< -10000);ev('__R72_QA.save()');mid=ev('__R72_QA.info().ledger');ev('__R72_QA.reload()');check('mid-retreat save position retained',ev('__R72_QA.info().ledger')==mid)
  checkpoint=ev('__R72_QA.snapshot()');r=ev('__R72_QA.failArrival()');check('failed arrival does not erase active rat',r['z']==-21900 and r['alive'] and r['paused']);go('djamila','npc:r72:djamila');choose('Retenter la sauvegarde');choose('Revenir.');check('retry releases stalled simulation',not ev('__MISTRAL_DEBUG.v072RatsInfo().paused'));ev('(s)=>__R72_QA.restore(s)',checkpoint);ev('__R72_QA.ticks(70)');check('three survivors genuinely reach refuge',all(r['z']==-22000 for r in ev('__R72_QA.info().ledger.actors').values()))
  def repair_finish():
   for id in ['eclairage','signal']:go(id);choose('Remplacer la gaine');choose('Revenir.')
   check('two cabinets actually change appearance',ev('__R72_QA.info().repairs')==2)
   go('tableau');choose('Réarmer les deux');choose('Revenir.');check('six lamps stabilized after restoration',ev('__R72_QA.info().lamps')==6)
   go('djamila','npc:r72:djamila');caps=ev('__R72_QA.info().caps');choose('Faire réceptionner');choose('Revenir.');check('exactly sixty caps at reception',ev('__R72_QA.info().caps')==caps+60)
  repair_finish();check('nonlethal conclusion reflects actual departures',ev('__R72_QA.info().ledger.outcome')=='refuge');ev('__R72_QA.render()');page.screenshot(path=str(a.output/'05-depot-restaure.png'))
  ev('__R72_QA.reload()');go('djamila','npc:r72:djamila');check('reward unavailable after reload',page.locator('#dialogueChoices button').filter(has_text='Faire réceptionner').count()==0);choose('Revenir.');check('old political and wildlife ledgers preserved',ev('__R72_QA.info().old')==old)
  for n in [1,3]:
   ev('(s)=>__R72_QA.restore(s)',start)
   for id in ['voie','armoire','retour'][:n]:ev('(id)=>__R72_QA.kill(id)',id)
   go('tableau');qty=ev('__R72_QA.info().inv.circuitry');choose('Contrôler et isoler');choose('Réarmer les deux');check('kill alone never repairs network '+str(n),not ev('__R72_QA.info().ledger.restored') and ev('__R72_QA.info().inv.circuitry')==qty-1);choose('Revenir.')
   if n==1:
    go('gate');choose('Ouvrir le volet');choose('Revenir.');go('bait');choose('Poser l’appât');ev('__R72_QA.ticks(90)')
   go('kit');choose('Prélever les deux');choose('Revenir.');repair_finish();check('casualty outcome '+str(n),ev('__R72_QA.info().ledger.outcome')==('mixte' if n==1 else 'abattus'))
  check('no JavaScript or adapter errors',not errors and ev('__R72_QA.info().error') is None)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Actual authored depot, native E/dialogues/shooting/hitboxes/collision, rat runtime and game save/load. Scripted positions and aim, synthetic Saint-Charles relay, isolated MemoryStorage and software renderer. No real IGN traversal or human campaign.'}
  (a.output/'RATS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',ev('window.__R72_QA?.info()'),flush=True);raise
 finally:browser.close()
