"""Close/relaunch Chromium with its real disk-backed profile, then click Continue.
Production HTML is loaded unchanged from the same offline file path on resume. The
fixture seed uses existing rat/port helpers; no MemoryStorage or save import occurs
on resume. No real IGN return, human campaign or power-loss guarantee is asserted.
"""
from pathlib import Path
import argparse, ast, hashlib, json, shutil, tempfile
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/rats/cold')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest()
def bridge(path):
 tree=ast.parse(path.read_text())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bridge' for t in n.targets))
seed_bridge=bridge(root/'tests/expansion/lys_browser_smoke.py')+'\n'+bridge(root/'tests/expansion/rats_browser_smoke.py')
seed_bridge+=r'''
globalThis.__R72_COLD={
 prepare(scenario){
  const run=(type,id)=>{const p=['open','finish'].includes(type)?'djamila':type==='note'?id:['isolate','restore'].includes(type)?'tableau':type==='repair'?id:type;__R72_QA.near(p);if(!__MISTRAL_DEBUG.v072RatsAction(type,id))throw Error('fixture refused '+type);};
  run('open');run('note','morsures');run('note','plan');run('isolate','manuel');run('gate');run('bait');
  if(scenario==='retreat'){
   __R72_QA.wound('voie');__R72_QA.kill('retour');state.player.pos=[25,1.65,23];mode='PLAYING';
   for(let i=0;i<15;i++)updateEnemies(.2);
   applyEnemyStatus(world.enemies.find(e=>e.r72Id==='armoire'),'burning',4);
   applyEnemyStatus(world.enemies.find(e=>e.r72Id==='armoire'),'slow',5);updateEnemies(.2);
  }else{
   __R72_QA.ticks(100);run('kit');run('repair','eclairage');run('repair','signal');run('restore');run('finish');
  }
  state.player.pos=[25,1.65,23];inCombat=false;mode='PLAYING';
  if(saveGame(false)===false)throw Error('fixture save refused');
  const key=__MISTRAL_DEBUG.v050ContinueInfo()[0].key;
  return {key,raw:localStorage.getItem(key),live:__R72_QA.info(),points:__MISTRAL_DEBUG.v072RatsInfo().points};
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert production.decode().count(marker)==1
seed=production.decode().replace(marker,seed_bridge+'\n'+marker).encode()
checks=[];errors=[];runs=[]
def check(label,ok):
 assert ok,label
 checks.append(label);print('PASS',label,flush=True)
def choose(page,text):page.locator('#dialogueChoices button').filter(has_text=text).click()
# The observation listener cannot supply or migrate a save. It pauses after the
# native Continue handler to compare the exact checkpoint before another frame.
observer=r'''document.addEventListener('click',event=>{
 if(event.target.closest?.('#btnContinue'))queueMicrotask(()=>{
  const d=window.__MISTRAL_DEBUG;if(d?.getMode()==='PLAYING')d.pause();
  d?.setRenderPaused(true);
 });
});'''
with tempfile.TemporaryDirectory(prefix='mistral-offline-delivery-') as delivery:
 entry=Path(delivery)/'index.html';url=entry.as_uri()+'?skipboot=1'
 with sync_playwright() as pw:
  for scenario in ['retreat','completed']:
   with tempfile.TemporaryDirectory(prefix='mistral-disk-profile-') as profile:
    opts=dict(executable_path=a.chromium,headless=True,viewport={'width':1280,'height':800},args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    entry.write_bytes(seed)
    context=pw.chromium.launch_persistent_context(profile,**opts)
    try:
     page=context.pages[0];page.set_default_timeout(10000);page.on('pageerror',lambda e:errors.append(e.stack))
     page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v072RatsInfo')
     page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(800)
     page.evaluate('__R72_QA.setup()');page.keyboard.press('e');choose(page,'Aiguilleurs ·');choose(page,'Rejoindre le dépôt')
     seed_state=page.evaluate('(s)=>__R72_COLD.prepare(s)',scenario)
     expected=seed_state['live'];envelope=json.loads(seed_state['raw']);stored=envelope.get('snapshot',envelope);expected_ledger=expected['ledger']
     check(scenario+': real LocalStorage persisted native save',page.evaluate('localStorage instanceof Storage') and stored['v072Rats']==expected_ledger)
     if scenario=='retreat':
      check('checkpoint: wounded survivor partway to refuge',-22000<expected_ledger['actors']['voie']['z']<-8000 and expected_ledger['actors']['voie']['legs']>0)
      check('checkpoint: death and active effects recorded',expected_ledger['actors']['retour']['hp']==0 and expected_ledger['actors']['armoire']['burn']>0 and expected_ledger['actors']['armoire']['slow']>0)
    finally:context.close()
    # The same offline launch path now contains unchanged production bytes.
    entry.write_bytes(production)
    # A new Chromium process opens the same profile. No storage state is imported.
    context=pw.chromium.launch_persistent_context(profile,**opts)
    try:
     page=context.pages[0];page.set_default_timeout(10000);page.on('pageerror',lambda e:errors.append(e.stack));page.add_init_script(observer)
     response=page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v072RatsInfo')
     check(scenario+': resume page is byte-identical production HTML',hashlib.sha256(response.body()).hexdigest()==sha)
     check(scenario+': no seed bridge or memory storage on resume',page.evaluate('typeof __R72_COLD==="undefined" && typeof __R72_QA==="undefined" && localStorage instanceof Storage'))
     check(scenario+': disk save survives full Chromium restart',page.evaluate('(k)=>localStorage.getItem(k)',seed_state['key'])==seed_state['raw'])
     page.wait_for_selector('#menuScreen.active');check(scenario+': native Continue is enabled',page.locator('#btnContinue').is_enabled())
     page.locator('#btnContinue').click();page.wait_for_function('__MISTRAL_DEBUG.v072RatsInfo().local')
     got=page.evaluate('__MISTRAL_DEBUG.v072RatsInfo()');live=page.evaluate('__MISTRAL_DEBUG.getState()')
     check(scenario+': resumed in actual depot via Continue',got['local'] and live['v042']['activeInterior']=='v072-depot-rats-cables')
     check(scenario+': quest ledger exactly reconstructed',got['ledger']==expected_ledger)
     check(scenario+': health and positions reconstructed from saved actors',all(e['health']==expected_ledger['actors'][e['id']]['hp']/100 and e['pos'][2]==expected_ledger['actors'][e['id']]['z']/1000 for e in got['enemies']))
     check(scenario+': inventory and capsules unchanged',live['inventory']==expected['inv'] and live['player']['caps']==expected['caps'])
     old_keys=['v071Cigales','v070Secours','v069Parts','v068Lys','v067Devoir','v066Voisins','v065Notaires','v064Mutuelle','v063Radieuse','v062Pharmacy','v061Poste','v060Council']
     check(scenario+': earlier ledgers remain unchanged',all(live[k]==stored[k] for k in old_keys))
     page.screenshot(path=str(a.output/(scenario+'-continue.png')))
     if scenario=='completed':
      check('completed: zero living enemies or resurrected rats',all(not e['alive'] for e in got['enemies']))
      p=seed_state['points']['djamila'];page.evaluate('(p)=>{__MISTRAL_DEBUG.pause();__MISTRAL_DEBUG.teleport(p[0],p[2]+2);}',p)
      caps=live['player']['caps'];result=page.evaluate('__MISTRAL_DEBUG.v072RatsAction("finish")')
      check('completed: reward cannot be reclaimed after process restart',result is False and page.evaluate('__MISTRAL_DEBUG.getState().player.caps')==caps)
     else:
      check('retreat: dead rat stays dead, two survivors stay active',sum(e['alive'] for e in got['enemies'])==2)
     runs.append({'scenario':scenario,'storage_key':seed_state['key'],'same_disk_profile':True,'resume_html_sha256':sha,'native_continue':True})
    except Exception:
     page.screenshot(path=str(a.output/(scenario+'-failure.png')));print('RESUME INFO',page.evaluate('__MISTRAL_DEBUG.v072RatsInfo()'),flush=True);raise
    finally:context.close()
  check('no JavaScript exceptions during cold resumes',not errors)
result={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'runs':runs,'scope':'Native disk-backed Chromium LocalStorage at an offline file URL and full process restart followed by native Continue on unchanged production HTML. Seed checkpoint uses existing model/runtime helpers and a synthetic origin. Observer pauses immediately after Continue for exact comparison. No real IGN exterior return, power-loss or human campaign certification.'}
(a.output/'RATS_COLD_SAVE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
