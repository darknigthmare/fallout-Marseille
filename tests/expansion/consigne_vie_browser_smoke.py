"""Native optional owner routines: dialogs/E, real collision, saved route distances,
blocking, rollback, rendering and local doors. Scripted positions, synthetic exterior,
MemoryStorage and software rendering; not a human playthrough or IGN certification.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/consigne-vie/browser');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest()
def extract(name):
    tree=ast.parse((root/'tests/expansion'/name).read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
bridge=r'''
globalThis.__LIFE_QA={
 info(){return __MISTRAL_DEBUG.v076ConsigneInfo();},
 near(id){debugDismissDialogue();const n=world.npcs.find(n=>n.id==='g73:owner:'+id);for(const [x,z]of [[0,-2.2],[2.2,0],[-2.2,0],[0,2.2]]){
 const p=[n.pos[0]+x,1.65,n.pos[2]+z];if(collidesAt(p[0],p[2],.38,1.65)||!lineOfSight(p,[n.pos[0],1.25,n.pos[2]]))continue;
 state.player.pos=p;const d=vNorm(vSub([n.pos[0],1.25,n.pos[2]],p));state.player.yaw=Math.atan2(d[0],-d[2]);state.player.pitch=Math.asin(d[1]);onGround=true;mode='PLAYING';updateSelectedInteractable();if(selectedInteractable?.id==='npc:'+n.id)return true;
 }return false;},
 away(){state.player.pos=[24,1.65,23];onGround=true;mode='PLAYING';inCombat=false;},
 ticks(n=1){for(let i=0;i<n;i++)updateNPCSchedules(.2);return this.info();},
 failChoice(text){const fn=dialogueState.choices.find(c=>c.text.includes(text)).onChoose,old=saveGame,before=JSON.stringify(state);saveGame=()=>false;try{fn();}finally{saveGame=old;}return before===JSON.stringify(state);},
 remember(text){globalThis.__LIFE_STALE=dialogueState.choices.find(c=>c.text.includes(text)).onChoose;},
 stale(){const before=JSON.stringify(state);__LIFE_STALE();return before===JSON.stringify(state);},
 gate(kind){if(kind==='loading')zoneTransitioning=true;else if(kind==='combat')inCombat=true;else if(kind==='dead')state.player.hp=0;else mode=kind;},
 ungate(){zoneTransitioning=false;inCombat=false;state.player.hp=100;mode='PLAYING';},
 reduced(value){settings.reduceMotion=value;collectDraws(gameClock);},
 obstacle(id){const n=world.npcs.find(n=>n.id==='g73:owner:'+id);globalThis.__LIFE_OBSTACLE=addCollider(world,n.pos[0],n.pos[2],1.6,1.6,{minY:0,maxY:2});},
 clearObstacle(){world.colliders=world.colliders.filter(c=>c!==__LIFE_OBSTACLE);},
 crowd(id){const p=MistralConsigneLife.position(id,state.v076Consigne.people[id].progress+250);state.player.pos=[p[0],1.65,p[2]];},
 failTick(){const old=saveGame,before=JSON.stringify(state);saveGame=()=>false;try{updateNPCSchedules(.2);}finally{saveGame=old;}return {same:before===JSON.stringify(state),info:this.info()};},
 render(id){for(const k of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=$(k);e?.classList.remove('active');e?.classList.add('hidden');}document.getElementById('questFlash').style.display='none';$('toastStack')?.replaceChildren();$('interactPrompt').classList.add('hidden');
 const c=({clef:{pos:[-16.5,2.6,17.5],target:[-21.3,1.05,12]},bague:{pos:[-1.8,2.1,14.2],target:[-6,1.15,9.5]},sifflet:{pos:[6.6,2.4,23.0],target:[12,1.2,18]},court:{pos:[21,7,28],target:[-8,1.1,13]}})[id];
 sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:60},currentEnv());return this.info();},
 routeGeometry(){return MistralConsigneLife.IDS.map(id=>{for(let p=0;p<=MistralConsigneLife.total(id);p+=50){const q=MistralConsigneLife.position(id,p);if(collidesAt(q[0],q[2],.38,q[1]+1.65))return{id,clear:false,p};}return{id,clear:true};});},
 airborne(){onGround=false;},
 ground(){onGround=true;},
 ringFollows(){const n=world.npcs.find(n=>n.id==='g73:owner:bague'),moving=n.moving,yaw=n.yaw;
 try{n.moving=true;n.yaw=.7;const draws=[];humanParts(draws,n,1.35);const ring=draws.filter(d=>d.v075Object==='bague'),center=[0,1,2].map(i=>ring.reduce((sum,d)=>sum+d.pos[i],0)/ring.length);
 const hand=draws.find(d=>!d.v075Object&&d.mesh==='sphere'&&d.scale?.every((v,i)=>Math.abs(v-[.16,.18,.15][i])<1e-6)&&MistralConsigneGestures.unpoint(n.pos,n.yaw,d.pos)[0]>.2);
 const local=MistralConsigneGestures.unpoint(n.pos,n.yaw,hand.pos);local[2]-=.065;const expected=MistralConsigneGestures.point(n.pos,n.yaw,local);return ring.length===12&&center.every((v,i)=>Math.abs(v-expected[i])<1e-8);
 }finally{n.moving=moving;n.yaw=yaw;}},
 save(){return saveGame(false);},
 exitFail(){const old=saveGame,before=JSON.stringify(state),w=world;saveGame=()=>false;let r;try{r=v042ExitInstance();}finally{saveGame=old;}return r===false&&w===world&&before===JSON.stringify(state);},
 drawState(){const before=JSON.stringify(state);for(let i=0;i<10;i++)collectDraws(gameClock+i/20);return before===JSON.stringify(state);},
 corruptRestore(){const raw=JSON.parse(JSON.stringify(state));raw.v076Consigne.schema=99;try{migrateState(raw);return false;}catch{return true;}},
 oldRestore(){const raw=JSON.parse(JSON.stringify(state));delete raw.v076Consigne;return __G73_QA.restore(JSON.stringify(raw));}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
html=production.decode();assert html.count(marker)==1
html=html.replace(marker,'\n'.join(extract(n) for n in ['lys_browser_smoke.py','gabians_browser_smoke.py','retrouvailles_browser_smoke.py','gestes_browser_smoke.py'])+'\n'+bridge+'\n'+marker)
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
checks=[];errors=[];complete=False

def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(12000)
    page.on('pageerror',lambda e:errors.append(e.stack))
    def ev(s,arg=None):return page.evaluate(s,arg)
    def choose(text):page.locator('#dialogueChoices button').filter(has_text=text).click()
    def owner(id):
        check('native E follows current '+id,ev('(id)=>__LIFE_QA.near(id)',id));page.keyboard.press('e')
    try:
        page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v076ConsigneInfo')
        ev('__MISTRAL_DEBUG.startStory()');page.wait_for_function('__MISTRAL_DEBUG.getState().v035.prologue.titleSeen && document.getElementById("v35pTitle").classList.contains("hidden")')
        ev('__G73_QA.setup()');page.keyboard.press('e');choose('Consigne ·');choose('Rejoindre la consigne')
        check('four original people, no extra copy',len(ev('__OWNERS_QA.info().people'))==4)
        check('three physical destinations and all routes clear',ev('__LIFE_QA.info().props')>=15 and all(v['clear'] for v in ev('__LIFE_QA.routeGeometry()')))
        owner('clef');check('no invitation before restitution',page.locator('#dialogueChoices button').filter(has_text='montrer le Demain').count()==0);choose('Revenir.')
        ev('__OWNERS_QA.prepare()');old=ev('__OWNERS_QA.info().old');caps=ev('__MISTRAL_DEBUG.getState().player.caps');inv=ev('JSON.stringify(__MISTRAL_DEBUG.getState().inventory)')
        owner('clef');choose('Remettre en main propre');ev('__G75_QA.startClock()');
        check('invitation appears after saved handoff',page.locator('#dialogueChoices button').filter(has_text='montrer le Demain').count()==1)
        check('failed invitation save restores entire state',ev('__LIFE_QA.failChoice("montrer le Demain")'))
        ev('__LIFE_QA.remember("montrer le Demain")');choose('montrer le Demain');check('invitation recorded without forcing dialogue shut',ev('__LIFE_QA.info().ledger.people.clef.started') and ev('__MISTRAL_DEBUG.getMode()')=='DIALOGUE')
        check('stale invitation cannot change world',ev('__LIFE_QA.stale()'))
        choose('Revenir.');ev('__LIFE_QA.away()');ev('__LIFE_QA.ticks(4)');check('recognition gesture finishes before walking',ev('__LIFE_QA.info().ledger.people.clef.progress')==0)
        ev('__G75_QA.advance(3100)');info=ev('__LIFE_QA.ticks(3)');check('native schedule moves Eloi continuously',info['ledger']['people']['clef']['progress']==750 and info['people'][0]['moving'])
        check('rendering does not advance gameplay or write saves',ev('__LIFE_QA.drawState()'))
        before=ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')
        for mode in ['PIP','DIALOGUE','PAUSE','loading','combat','dead']:
            ev('(k)=>__LIFE_QA.gate(k)',mode);ev('__LIFE_QA.ticks(3)');check('routine pauses for '+mode,ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==before);ev('__LIFE_QA.ungate()')
        ev('__LIFE_QA.airborne()');ev('__LIFE_QA.ticks()');check('player jumping does not freeze a safe owner',ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.progress')==1000);ev('__LIFE_QA.ground()')
        ev('__LIFE_QA.obstacle("clef")');before=ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.progress');info=ev('__LIFE_QA.ticks(8)');check('real solid collider blocks rather than teleports',info['ledger']['people']['clef']['progress']==before and 'clef' in info['blocked']);ev('__LIFE_QA.clearObstacle()')
        ev('__LIFE_QA.crowd("clef")');info=ev('__LIFE_QA.ticks(4)');check('owner yields to player in corridor',info['ledger']['people']['clef']['progress']==before and 'clef' in info['blocked']);ev('__LIFE_QA.away()')
        owner('clef');choose('Attendez-moi ici');check('explicit wait saved',ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.paused'));choose('Revenir.');ev('__LIFE_QA.away()');ev('__LIFE_QA.ticks(5)');check('explicit wait is stationary',ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.progress')==before)
        ev('__LIFE_QA.save()');snapshot=ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)');ev('__G73_QA.reload()');check('paused precise position reconstructed by native load',ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==snapshot and ev('__LIFE_QA.info().people[0].pos')==[-12,0,18] and abs(ev('__LIFE_QA.info().people[0].yaw')-1.5707963267948966)<1e-8)
        owner('clef');choose('reprendre votre chemin');choose('Revenir.');ev('__LIFE_QA.away()');ev('__LIFE_QA.ticks(3)');fail=ev('__LIFE_QA.failTick()');check('checkpoint failure rolls back exact state and stops walking',fail['same'] and fail['info']['saveBlocked']=='clef')
        before=ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.progress');ev('__LIFE_QA.ticks(4)');check('no progress after refused checkpoint',ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.progress')==before)
        owner('clef');choose('Retenter la sauvegarde');choose('Revenir.');ev('__LIFE_QA.away()');ev('__LIFE_QA.ticks(120)');check('successful retry reaches the real map table',ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.progress')==15000 and ev('__LIFE_QA.info().people[0].pos')==[-20,0,12])
        owner('clef');choose('C’est ici');check('Eloi has new contextual memory and no false destination','toutes leurs affaires' in page.locator('#dialogueLine').inner_text() and ev('__MISTRAL_DEBUG.getState().v076Consigne.people.clef.heard'));page.screenshot(path=str(a.output/'01-eloi-souvenir.png'));choose('Revenir.');ev('__LIFE_QA.render("clef")');page.screenshot(path=str(a.output/'02-eloi-table.png'))
        ev('__G73_QA.run("return","bague")');owner('bague');choose('Passer depuis le comptoir');ev('__LIFE_QA.reduced(true)');choose('fini votre quart');choose('Revenir.');ev('__LIFE_QA.away()');info=ev('__LIFE_QA.ticks(4)');check('reduced motion keeps real walking distance without limb cycling',info['ledger']['people']['bague']['progress']==1000 and not info['people'][1]['moving'])
        ev('__LIFE_QA.ticks(80)');owner('bague');choose('Pas de cordages');check('Mina rests without working with her ring','heures' in page.locator('#dialogueLine').inner_text() and ev('__MISTRAL_DEBUG.getState().v076Consigne.people.bague.heard'));choose('Revenir.');ev('__LIFE_QA.render("bague")');page.screenshot(path=str(a.output/'03-mina-banc.png'))
        owner('sifflet');choose('Remettre en main propre');choose('annoncer au panneau');choose('Revenir.');ev('__LIFE_QA.away()');ev('__LIFE_QA.ticks(90)');owner('sifflet');choose('Pourquoi garder une ardoise');check('Rachid does not invent a functioning ferry','ni bateau ni rame' in page.locator('#dialogueLine').inner_text() and ev('__MISTRAL_DEBUG.getState().v076Consigne.people.sifflet.heard'));choose('Revenir.');ev('__LIFE_QA.render("sifflet")');page.screenshot(path=str(a.output/'04-rachid-panneau.png'))
        check('all objects remain attached to existing recipients',set(ev('__G75_QA.info().objects'))=={'clef','bague','sifflet'})
        check('ring follows the native hand while walking and turning',ev('__LIFE_QA.ringFollows()'))
        check('no extra caps inventory or changes to previous quests',ev('__MISTRAL_DEBUG.getState().player.caps')==caps and ev('JSON.stringify(__MISTRAL_DEBUG.getState().inventory)')==inv and ev('__OWNERS_QA.info().old')==old)
        ev('__G73_QA.run("finish")');check('historical prime still exactly 45',ev('__MISTRAL_DEBUG.getState().player.caps')==caps+45)
        ev('__MISTRAL_DEBUG.v073GabiansOpen()');text=page.locator('#pipboy').inner_text();check('journal lists real places and three heard memories',all(t in text for t in ['table des cartes','banc de fin de quart','panneau des passages']) and text.count('souvenir écouté')==3)
        page.screenshot(path=str(a.output/'05-journal.png'));page.set_viewport_size({'width':390,'height':844});check('390px journal has no horizontal overflow',ev('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'06-journal-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
        ev('__LIFE_QA.save()');snapshot=ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)');ev('__G73_QA.reload()');check('all arrivals and memories survive reload',ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==snapshot)
        check('unknown routine schema is rejected',ev('__LIFE_QA.corruptRestore()'))
        check('failed exit keeps current world and full state',ev('__LIFE_QA.exitFail()'))
        ev('__LIFE_QA.render("court")');page.screenshot(path=str(a.output/'07-cour-vivante.png'))
        ev('__G73_QA.near("sortie")');page.keyboard.press('e')
        page.get_by_text('Le secteur n’est pas prêt',exact=True).wait_for()
        check('missing exterior data preserves interior and exact routine ledger',ev('__LIFE_QA.info().local') and ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==snapshot)
        page.get_by_role('button',name='Revenir sans déplacer le joueur').click()
        check('native cancellation retains valid interior',ev('__LIFE_QA.info().local') and ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==snapshot)
        # Recreate the documented synthetic port, then verify a retained-world
        # roundtrip separately. This does not assert an IGN return after restart.
        ev('__G73_QA.port()');page.keyboard.press('e');choose('Consigne ·');choose('Rejoindre la consigne')
        ev('__G73_QA.near("sortie")');page.keyboard.press('e');check('native retained synthetic exterior return preserves routes',ev('__MISTRAL_DEBUG.getState().v042.activeInterior') is None and ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==snapshot)
        ev('__G73_QA.port()');page.keyboard.press('e');choose('Consigne ·');choose('Rejoindre la consigne');check('return rebuilds destinations without duplicate people or props',ev('JSON.stringify(__MISTRAL_DEBUG.getState().v076Consigne)')==snapshot and len(ev('__OWNERS_QA.info().people'))==4)
        ev('__LIFE_QA.oldRestore()');check('old completed save stays complete without invented routines',ev('__MISTRAL_DEBUG.getState().v073Gabians.finished') and all(not x['started'] for x in ev('__MISTRAL_DEBUG.getState().v076Consigne.people').values()) and ev('__MISTRAL_DEBUG.getState().player.caps')==caps+45)
        check('no JavaScript exceptions',not errors);complete=True
    except Exception:
        page.screenshot(path=str(a.output/'failure.png'));print('ERRORS',errors,flush=True);print('STATE',ev('window.__LIFE_QA?.info()'),flush=True);raise
    finally:
        report={'html_sha256':sha,'passed':len(checks),'complete':complete,'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
        (a.output/'CONSIGNE_VIE_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));browser.close()
