"""Native consignment owner dialogues and optional handoffs, actual geometry and saves.
Setup uses a synthetic Vieux-Port relay and scripted positions, with MemoryStorage.
Not a human playthrough, IGN route or cold process restart (separate suite).
"""
from pathlib import Path
import argparse, ast, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--html', type=Path, default=root/'index.html')
p.add_argument('--output', type=Path, default=root/'verification/retrouvailles/browser')
p.add_argument('--chromium', default=shutil.which('chromium'))
a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
production = a.html.read_bytes(); sha = hashlib.sha256(production).hexdigest()
def extract(name):
    tree=ast.parse((root/'tests/expansion'/name).read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
bridge = r'''
globalThis.__OWNERS_QA={
 near(key){debugDismissDialogue();const p=__MISTRAL_DEBUG.v073GabiansInfo().points['owner:'+key];state.player.pos=[p[0],1.65,p[2]-2.2];state.player.yaw=Math.PI;state.player.pitch=-.2;onGround=true;mode='PLAYING';updateSelectedInteractable();return{selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,1.65)};},
 info(){return{...__G73_QA.info(),people:world.npcs.map(n=>({id:n.id,name:n.name,pos:n.pos})),receipts:world.staticDraws.filter(d=>d.g73Receipt&&!d.hidden).length,rows:v027QuestRows().filter(q=>q.id?.startsWith('g73:'))};},
 prepare(){__G73_QA.run('open');for(const id of MistralGabians.IDS)__G73_QA.run('lure',id);__G73_QA.ticks(150);for(const id of MistralGabians.IDS)__G73_QA.run('lower',id,'manuel');__G73_QA.ticks(30);for(const id of Object.keys(MistralGabians.OBJECTS))__G73_QA.run('take',id);return __G73_QA.snapshot();},
 legacy(){const raw=JSON.parse(__G73_QA.snapshot());raw.v073Gabians.schema=1;delete raw.v073Gabians.handoffs;return __G73_QA.restore(JSON.stringify(raw));},
 remember(){globalThis.__OWNER_STALE=dialogueState.choices.find(c=>c.text.startsWith('Remettre en main')).onChoose;},
 stale(){const before=JSON.stringify(state);__OWNER_STALE();return JSON.stringify(state)===before;},
 drawOwner(){const pos=state.player.pos.slice();sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos,dir:vNorm([0,-.1,1]),fov:65},currentEnv());},
 render(){__G73_QA.render();const pos=[-3,3.1,12.5],target=[-8,1.5,20.5];sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos,dir:vNorm(vSub(target,pos)),fov:65},currentEnv());}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
html=production.decode(); assert html.count(marker)==1
html=html.replace(marker,extract('lys_browser_smoke.py')+'\n'+extract('gabians_browser_smoke.py')+'\n'+bridge+'\n'+marker)
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
checks=[]; errors=[]
def check(name, ok):
    assert ok,name
    checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(8000)
    page.on('pageerror',lambda e: errors.append(e.stack))
    def ev(s,arg=None):return page.evaluate(s,arg)
    def choose(text):page.locator('#dialogueChoices button').filter(has_text=text).click()
    def owner(key):
        info=ev('(k)=>__OWNERS_QA.near(k)',key)
        check('accessible native owner '+key,info['selected']=='npc:g73:owner:'+key and not info['collision'])
        ev('__OWNERS_QA.drawOwner()');page.keyboard.press('e')
    try:
        page.set_content(shim+html,wait_until='load')
        page.wait_for_function('!!window.__MISTRAL_DEBUG?.v073GabiansInfo')
        ev('__MISTRAL_DEBUG.startStory()');page.wait_for_function('__MISTRAL_DEBUG.getState().v035.prologue.titleSeen && document.getElementById("v35pTitle").classList.contains("hidden")')
        ev('__G73_QA.setup()');page.keyboard.press('e');choose('Consigne ·');choose('Rejoindre la consigne')
        info=ev('__OWNERS_QA.info()')
        check('Nora and three identified owners are actually present',len(info['people'])==4 and {p['name'] for p in info['people']}=={'Nora Ferrand','Éloi','Mina','Rachid'})
        old=info['old'];inv=info['inv']
        # Retire seed-only intro overlays before capturing the authored court.
        ev('__G73_QA.render()')
        for key,question in [('clef','Votre premier bateau'),('bague','La marque à l’intérieur'),('sifflet','Pourquoi ne pas prendre')]:
            owner(key)
            check('no false handoff before recovery '+key,page.locator('#dialogueChoices button').filter(has_text='Remettre en main').count()==0)
            initials={'clef':'ÉL','bague':'MI','sifflet':'RA'}[key];before=page.locator('#speakerInitials').inner_text()
            choose(question);check('personal memory '+key,len(page.locator('#dialogueLine').inner_text())>90)
            check('correct owner identity in dialogue and memory '+key,before==initials and page.locator('#speakerInitials').inner_text()==initials);choose('Revenir.')
        route=ev('__LYS_QA.walk([[0,1.65,25],[-16,1.65,25],[-16,1.65,15.8],[-11,1.65,15.8],[-8,1.65,15.8],[-5,1.65,15.8]])')
        check('counter accessible around its left edge through actual collisions',all(abs(p[2]-15.8)<.3 for p in route[-3:]))
        initial=ev('__OWNERS_QA.prepare()')
        owner('clef');ev('__OWNERS_QA.remember()')
        fail=ev('__G73_QA.fail("deliver","clef")')
        check('failed owner save restores bag and entire state',fail['same'] and fail['result'] is False)
        check('failed handoff creates no physical receipt',ev('__OWNERS_QA.info().receipts')==0)
        choose('Remettre en main propre')
        check('Éloi recognises his bent key','dent tordue' in page.locator('#dialogueLine').inner_text())
        check('stale handoff callback is harmless',ev('__OWNERS_QA.stale()'))
        page.screenshot(path=str(a.output/'01-eloi-clef.png'));choose('Revenir.')
        ev('__G73_QA.run("return","bague")');owner('bague');choose('Passer depuis le comptoir')
        check('Mina recognises her private engraving','marque à l’intérieur' in page.locator('#dialogueLine').inner_text());choose('Revenir.')
        owner('sifflet');choose('Remettre en main propre')
        check('Rachid distinguishes his signal from an alarm','pas une alarme' in page.locator('#dialogueLine').inner_text());choose('Revenir.')
        info=ev('__OWNERS_QA.info()')
        check('mixed direct/counter provenance persisted',info['ledger']['handoffs']=={'clef':'direct','bague':'consigne','sifflet':'direct'})
        check('three receipts replace objects without duplicating them',info['receipts']==3 and info['returned']==0 and info['objects']==0)
        check('handoffs do not mint currency or ordinary loot',info['caps']==json.loads(initial)['player']['caps'] and info['inv']==inv)
        ev('__G73_QA.run("finish")');ev('__G73_QA.save()');snapshot=ev('__OWNERS_QA.info()');ev('__G73_QA.reload()')
        check('personal receipts and closed quest survive normal save/load',ev('__OWNERS_QA.info().ledger')==snapshot['ledger'] and ev('__OWNERS_QA.info().receipts')==3)
        check('only original 45 caps paid',ev('__OWNERS_QA.info().caps')==json.loads(initial)['player']['caps']+45)
        check('original quest and optional epilogue both completed',all(q['stage']=='done' for q in ev('__OWNERS_QA.info().rows')))
        for key in ['clef','bague','sifflet']:
            owner(key);check('no repeat handoff '+key,page.locator('#dialogueChoices button').filter(has_text='en main propre').count()==0);choose('Revenir.')
        ev('__MISTRAL_DEBUG.v073GabiansOpen()')
        check('Pip-Boy names the actual recipients',all('remis à '+n in page.locator('#pipboy').inner_text() for n in ['Éloi','Mina','Rachid']))
        page.screenshot(path=str(a.output/'02-carnet-restitutions.png'));page.set_viewport_size({'width':390,'height':844})
        check('390px journal without horizontal overflow',ev('document.documentElement.scrollWidth<=innerWidth'))
        page.screenshot(path=str(a.output/'03-carnet-mobile.png'));page.set_viewport_size({'width':1280,'height':800});ev('__LYS_QA.close()')
        ev('__OWNERS_QA.render()');page.screenshot(path=str(a.output/'04-proprietaires-comptoir.png'))
        # Upgrade a previously completed save, then play the optional epilogue.
        ev('(s)=>__G73_QA.restore(s)',initial)
        for key in ['clef','bague','sifflet']:ev('(k)=>__G73_QA.run("return",k)',key)
        ev('__G73_QA.run("finish")');caps=ev('__OWNERS_QA.info().caps');legacy=ev('__OWNERS_QA.legacy()')
        check('legacy completed save keeps its outcome and currency',legacy['ledger']['finished'] and legacy['caps']==caps and legacy['ledger']['outcome']=='vivants')
        check('migration does not invent personal receipts',all(v is None for v in legacy['ledger']['handoffs'].values()))
        check('optional epilogue does not reopen original quest',ev('__OWNERS_QA.info().rows[0].stage')=='done' and ev('__OWNERS_QA.info().rows[1].stage')=='active')
        for key in ['sifflet','clef','bague']:owner(key);choose('Passer depuis le comptoir');choose('Revenir.')
        check('post-completion counter handoffs pay no second reward',ev('__OWNERS_QA.info().caps')==caps)
        check('all old records unchanged by optional epilogue',ev('__OWNERS_QA.info().old')==old)
        check('no JavaScript exceptions',not errors)
        report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':__doc__}
        (a.output/'RETROUVAILLES_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2))
    except Exception:
        page.screenshot(path=str(a.output/'failure.png'));print('STATE',ev('window.__OWNERS_QA?.info()'),flush=True);raise
    finally:browser.close()
