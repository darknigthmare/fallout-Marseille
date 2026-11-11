"""Six disk-backed Chromium restarts for postal pigeons and consignment gabians.
Seed-only fixtures prepare native saves. Resume loads byte-identical production HTML
at the same file URL, clicks Continue, and has no seed bridge or fake storage.
Scripted positions and authored interiors only; no power-cut or real IGN certification.
"""
from pathlib import Path
import argparse, ast, hashlib, json, shutil, tempfile
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/retrouvailles/cold')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest()
def extract(name):
    tree=ast.parse((root/'tests/expansion'/name).read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
seed_bridge='\n'.join(extract(n) for n in ['lys_browser_smoke.py','gabians_browser_smoke.py','pigeons_browser_smoke.py'])
seed_bridge+=r'''
globalThis.__BIRDS_COLD={
 idle(){return gameStarted&&!zoneTransitioning&&!V046.busy&&!V047.pending;},
 seed(scenario){
  const postal=scenario.startsWith('pigeons'),qa=postal?__P74_QA:__G73_QA;
  qa.setup();state.v042.activeInterior=postal?MistralPigeons.SITE:MistralGabians.SITE;
  state.v042.returnPoint=null;loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});
  onGround=true;mode='PLAYING';
  const run=(type,id,bird)=>{
   const point=postal?MistralPigeons.point(type,id):MistralGabians.actionPoint(type,id);
   if(point.startsWith('owner:')){const p=__MISTRAL_DEBUG.v073GabiansInfo().points[point];state.player.pos=[p[0],1.65,p[2]-2.2];onGround=true;mode='PLAYING';}
   else qa.near(point);
   const action=postal?__MISTRAL_DEBUG.v074PigeonsAction:__MISTRAL_DEBUG.v073GabiansAction;
   if(!action(type,id,bird))throw Error('Native seed action refused '+type+': '+V027.message);
  };
  run('open');
  if(postal){
   if(scenario==='pigeons-flight'){
    run('read','soins');run('load','soins','azur');run('hatch','soins');run('release','soins');qa.ticks(7);run('take','pompes');
   }else{
    for(const id of ['soins','pompes']){
     if(scenario==='pigeons-public'){
      run('read',id);run('load',id,id==='soins'?'azur':'brique');run('hatch',id);run('release',id);qa.ticks(150);
     }else run('take',id);
     run('receive',id);
    }
    run('finish',scenario==='pigeons-public'?'annonce':'scelles');
   }
  }else if(scenario==='gabians-threat'){
   qa.threat('menu');mode='PLAYING';state.player.pos=[25,1.65,23];for(let i=0;i<6;i++)updateEnemies(.2);
   qa.kill('tole');const e=world.enemies.find(e=>e.g73Id==='filets');damageEnemy(e,2,'arm_l');applyEnemyStatus(e,'burning',3);applyEnemyStatus(e,'slow',4);
  }else{
   for(const id of MistralGabians.IDS)run('lure',id);qa.ticks(150);run('lower','filets','manuel');
   if(scenario==='gabians-basket')qa.underBasket();
   else{
    run('lower','tole','manuel');qa.ticks(30);
    for(const id of Object.keys(MistralGabians.OBJECTS)){run('take',id);run(id==='clef'?'deliver':'return',id);}
    run('finish');run('deliver','bague');
   }
  }
  if(scenario!=='gabians-basket')state.player.pos=[25,1.65,23];
  inCombat=false;mode='PLAYING';if(saveGame(false)===false)throw Error('Native disk save refused');
  const key=__MISTRAL_DEBUG.v050ContinueInfo()[0].key;
  return{key,raw:localStorage.getItem(key),expected:__MISTRAL_DEBUG.getState(),info:postal?__MISTRAL_DEBUG.v074PigeonsInfo():__MISTRAL_DEBUG.v073GabiansInfo()};
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert production.decode().count(marker)==1
seed=production.decode().replace(marker,seed_bridge+'\n'+marker).encode()
# Observation only, after the game's native Continue handler. No save injection.
observer=r'''document.addEventListener('click',event=>{if(event.target.closest?.('#btnContinue'))queueMicrotask(()=>{const d=window.__MISTRAL_DEBUG;if(d?.getMode()==='PLAYING')d.pause();d?.setRenderPaused(true);});});'''
checks=[];errors=[];runs=[]
def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS',name,flush=True)
scenarios=['pigeons-flight','pigeons-public','pigeons-private','gabians-threat','gabians-basket','gabians-owners']
try:
    with tempfile.TemporaryDirectory(prefix='mistral-birds-delivery-') as delivery, sync_playwright() as pw:
        entry=Path(delivery)/'index.html';url=entry.as_uri()+'?skipboot=1'
        for scenario in scenarios:
            print('SCENARIO',scenario,flush=True)
            postal=scenario.startswith('pigeons');keyname='v074Pigeons' if postal else 'v073Gabians'
            infofn='v074PigeonsInfo' if postal else 'v073GabiansInfo'
            with tempfile.TemporaryDirectory(prefix='mistral-birds-profile-') as profile:
                opts=dict(executable_path=a.chromium,headless=True,viewport={'width':1280,'height':800},args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
                entry.write_bytes(seed)
                context=pw.chromium.launch_persistent_context(profile,**opts)
                try:
                    page=context.pages[0];page.set_default_timeout(12000);page.on('pageerror',lambda e:errors.append(e.stack))
                    page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.'+infofn)
                    page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_function('__BIRDS_COLD.idle()')
                    saved=page.evaluate('(s)=>__BIRDS_COLD.seed(s)',scenario)
                    expected=saved['expected'];ledger=expected[keyname]
                    envelope=json.loads(saved['raw']);stored=envelope.get('snapshot',envelope)
                    check(scenario+': real Storage holds native snapshot',page.evaluate('localStorage instanceof Storage') and stored[keyname]==ledger)
                    if scenario=='pigeons-flight':
                        check('checkpoint: pigeon in flight and other letter carried',ledger['mail']['soins']['phase']=='flying' and ledger['mail']['pompes']['phase']=='carried')
                    if scenario=='gabians-threat':
                        b=ledger['birds'];check('checkpoint: active shot, wounded wings, effects and falling corpse',b['filets']['shot'] is not None and b['filets']['wings']>0 and b['filets']['burn']>0 and b['filets']['slow']>0 and b['tole']['phase']=='falling')
                    if scenario=='gabians-basket':check('checkpoint: occupied basket suspended halfway',0<ledger['platforms']['filets']['drop']<3500)
                    if scenario=='gabians-owners':check('checkpoint: mixed handoffs with one object still at Nora',ledger['handoffs']=={'clef':'direct','bague':'consigne','sifflet':None})
                finally:context.close()
                # Same path, same disk profile, a completely new browser process.
                entry.write_bytes(production)
                context=pw.chromium.launch_persistent_context(profile,**opts)
                try:
                    page=context.pages[0];page.set_default_timeout(12000);page.on('pageerror',lambda e:errors.append(e.stack));page.add_init_script(observer)
                    response=page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.'+infofn)
                    check(scenario+': byte-identical production HTML on resume',hashlib.sha256(response.body()).hexdigest()==sha)
                    check(scenario+': no fixture or fake Storage on resume',page.evaluate('typeof __BIRDS_COLD==="undefined"&&typeof __G73_QA==="undefined"&&typeof __P74_QA==="undefined"&&typeof qaStore==="undefined"&&localStorage instanceof Storage'))
                    check(scenario+': exact save survived process termination',page.evaluate('(k)=>localStorage.getItem(k)',saved['key'])==saved['raw'])
                    page.wait_for_selector('#menuScreen.active');check(scenario+': native Continue enabled',page.locator('#btnContinue').is_enabled())
                    page.locator('#btnContinue').click();page.wait_for_function('__MISTRAL_DEBUG.'+infofn+'().local')
                    info=page.evaluate('__MISTRAL_DEBUG.'+infofn+'()');live=page.evaluate('__MISTRAL_DEBUG.getState()')
                    check(scenario+': Continue reconstructed correct authored interior',info['local'] and live['v042']['activeInterior']==expected['v042']['activeInterior'])
                    check(scenario+': quest and all intermediate fields exact',info['ledger']==ledger)
                    check(scenario+': health inventory and currency exact',all(live['player'][k]==expected['player'][k] for k in ['caps','hp']) and live['inventory']==expected['inventory'])
                    previous=[k for k in expected if k.startswith(('v06','v07')) and k!=keyname]
                    check(scenario+': other quest registries unchanged',all(live[k]==expected[k] for k in previous))
                    if not postal:
                        check(scenario+': actual gabian health and positions reconstructed',all(e['health']==ledger['birds'][e['id']]['hp']/100 and e['pos']==[n/1000 for n in ledger['birds'][e['id']]['pos']] and e['alive']==(ledger['birds'][e['id']]['hp']>0) for e in info['enemies']))
                    if ledger['finished']:
                        # Check rejection while genuinely PLAYING, grounded and at the clerk.
                        point=info['points']['mirette' if postal else 'nora'];caps=live['player']['caps']
                        result=page.evaluate('''(a)=>{const d=__MISTRAL_DEBUG;if(d.getMode()!=='PLAYING')d.pause();d.teleport(a.p[0],a.p[2]+2);const mode=d.getMode(),r=a.postal?d.v074PigeonsAction('finish','annonce'):d.v073GabiansAction('finish');d.pause();return{mode,result:r,caps:d.getState().player.caps};}''',{'p':point,'postal':postal})
                        check(scenario+': duplicate reward rejected in valid gameplay context',result['mode']=='PLAYING' and result['result'] is False and result['caps']==caps)
                    page.screenshot(path=str(a.output/(scenario+'-continue.png')))
                    runs.append({'scenario':scenario,'storage_key':saved['key'],'same_disk_profile':True,'native_continue':True,'resume_html_sha256':sha})
                finally:context.close()
        check('no JavaScript exceptions in any cold restart',not errors)
finally:
    report={'html_sha256':sha,'passed':len(checks),'complete':len(runs)==len(scenarios) and not errors,'checks':checks,'errors':errors,'runs':runs,'scope':__doc__}
    (a.output/'BIRDS_COLD_SAVE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
