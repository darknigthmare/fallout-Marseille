"""Three real disk-backed Chromium restarts: owner walking, explicitly waiting,
and all three arrived with memories heard. Seed-only scripted setup; resumed HTML
is byte-identical production without test bridge or MemoryStorage. No IGN return,
power-cut, human campaign or cross-browser certification.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,tempfile
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/consigne-vie/cold');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest()
def extract(name):
    tree=ast.parse((root/'tests/expansion'/name).read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
seed_bridge='\n'.join(extract(n) for n in ['lys_browser_smoke.py','gabians_browser_smoke.py','retrouvailles_browser_smoke.py','consigne_vie_browser_smoke.py'])
seed_bridge+=r'''
globalThis.__LIFE_COLD={
 idle(){return gameStarted&&!zoneTransitioning&&!V046.busy&&!V047.pending;},
 seed(scenario){
  __G73_QA.setup();state.v042.activeInterior=MistralGabians.SITE;state.v042.returnPoint=null;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';
  __OWNERS_QA.prepare();
  for(const id of MistralConsigneLife.IDS){__G73_QA.run('deliver',id);}
  __G73_QA.run('finish');
  const invite=id=>{if(!__LIFE_QA.near(id))throw Error('Owner not accessible');talkToNPC('g73:owner:'+id);dialogueState.choices.find(c=>c.v076Invite).onChoose();closeDialogue();};
  if(scenario==='arrived'){
   for(const id of MistralConsigneLife.IDS)invite(id);
   __LIFE_QA.away();__LIFE_QA.ticks(100);
   for(const id of MistralConsigneLife.IDS){__LIFE_QA.near(id);talkToNPC('g73:owner:'+id);dialogueState.choices[0].onChoose();closeDialogue();}
  }else{
   invite('clef');__LIFE_QA.away();__LIFE_QA.ticks(7);
   if(scenario==='waiting'){__LIFE_QA.near('clef');talkToNPC('g73:owner:clef');dialogueState.choices.find(c=>c.text.startsWith('Attendez')).onChoose();closeDialogue();}
  }
  __LIFE_QA.away();if(saveGame(false)===false)throw Error('Disk save refused');
  const key=__MISTRAL_DEBUG.v050ContinueInfo()[0].key;
  return {key,raw:localStorage.getItem(key),expected:__MISTRAL_DEBUG.getState(),info:__MISTRAL_DEBUG.v076ConsigneInfo()};
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert production.decode().count(marker)==1
seed=production.decode().replace(marker,seed_bridge+'\n'+marker).encode()
observer=r'''document.addEventListener('click',event=>{if(event.target.closest?.('#btnContinue'))queueMicrotask(()=>{const d=window.__MISTRAL_DEBUG;if(d?.getMode()==='PLAYING')d.pause();d?.setRenderPaused(true);});});'''
checks=[];errors=[];runs=[];version=None;failure=None

def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS',name,flush=True)
try:
    with tempfile.TemporaryDirectory(prefix='mistral-life-delivery-') as delivery,sync_playwright() as pw:
        entry=Path(delivery)/'index.html';url=entry.as_uri()+'?skipboot=1'
        for scenario in ['walking','waiting','arrived']:
            print('SCENARIO',scenario,flush=True)
            with tempfile.TemporaryDirectory(prefix='mistral-life-profile-') as profile:
                opts=dict(executable_path=a.chromium,headless=True,viewport={'width':1280,'height':800},args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
                entry.write_bytes(seed);ctx=pw.chromium.launch_persistent_context(profile,**opts)
                try:
                    page=ctx.pages[0];page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(e.stack))
                    page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v076ConsigneInfo')
                    page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_function('__LIFE_COLD.idle()')
                    saved=page.evaluate('(s)=>__LIFE_COLD.seed(s)',scenario);expected=saved['expected'];ledger=expected['v076Consigne']
                    envelope=json.loads(saved['raw']);stored=envelope.get('snapshot',envelope)
                    check(scenario+': native Storage contains exact routine snapshot',page.evaluate('localStorage instanceof Storage') and stored['v076Consigne']==ledger)
                    if scenario=='arrived':check('checkpoint: all memories heard and all destinations reached',all(p['heard'] for p in ledger['people'].values()))
                    else:check(scenario+': intermediate progress and pause flag exact',ledger['people']['clef']['progress']==1750 and ledger['people']['clef']['paused']==(scenario=='waiting'))
                finally:ctx.close()
                entry.write_bytes(production);ctx=pw.chromium.launch_persistent_context(profile,**opts)
                try:
                    page=ctx.pages[0];page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(e.stack));page.add_init_script(observer)
                    response=page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v076ConsigneInfo')
                    check(scenario+': unchanged production bytes on resume',hashlib.sha256(response.body()).hexdigest()==sha)
                    check(scenario+': no bridge or fake Storage in new process',page.evaluate('typeof __LIFE_QA==="undefined"&&typeof __LIFE_COLD==="undefined"&&typeof __G73_QA==="undefined"&&localStorage instanceof Storage'))
                    check(scenario+': exact persisted save survived browser closure',page.evaluate('(k)=>localStorage.getItem(k)',saved['key'])==saved['raw'])
                    page.wait_for_selector('#menuScreen.active');check(scenario+': native Continue enabled',page.locator('#btnContinue').is_enabled());page.locator('#btnContinue').click()
                    page.wait_for_function('__MISTRAL_DEBUG.v076ConsigneInfo().local')
                    info=page.evaluate('__MISTRAL_DEBUG.v076ConsigneInfo()');live=page.evaluate('__MISTRAL_DEBUG.getState()')
                    check(scenario+': actual interior and all owner distances reconstructed',info['local'] and info['ledger']==ledger)
                    check(scenario+': physical owner positions equal saved route positions',[x['pos'] for x in info['people']]==[x['pos'] for x in saved['info']['people']])
                    check(scenario+': original handoffs, prime and inventory preserved',live['v073Gabians']==expected['v073Gabians'] and live['player']['caps']==expected['player']['caps'] and live['inventory']==expected['inventory'])
                    old=[k for k in expected if k.startswith(('v06','v07')) and k!='v076Consigne']
                    check(scenario+': all earlier quest registers untouched',all(live[k]==expected[k] for k in old))
                    check(scenario+': no visual recognition replay on load',not page.evaluate('__MISTRAL_DEBUG.v075GesturesInfo().active'))
                    check(scenario+': paused native menu does not advance routines',not any(x['moving'] for x in info['people']))
                    check(scenario+': no duplicate or missing owners',len(info['people'])==3 and len({x['id'] for x in info['people']})==3)
                    page.screenshot(path=str(a.output/(scenario+'-continue.png')))
                    runs.append({'scenario':scenario,'native_continue':True,'same_disk_profile':True,'resume_html_sha256':sha,'ledger':ledger})
                finally:ctx.close()
        check('no JavaScript exceptions across three restarts',not errors)
except Exception as exc:
    failure={'type':type(exc).__name__,'message':str(exc),'classification':'BLOCKED_ENVIRONMENT' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc) else 'FAILED'}
    raise
finally:
    report={'html_sha256':sha,'passed':len(checks),'complete':len(runs)==3 and not errors,'checks':checks,'errors':errors,'runs':runs,'failure':failure,'scope':__doc__}
    (a.output/'CONSIGNE_VIE_COLD_SAVE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
