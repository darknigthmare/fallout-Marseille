"""Close and restart Chromium with the same disk profile, then native Continue.
Fixture-only seed builds the court and plays runtime actions. Resume uses unchanged
production HTML with no fixture or save injection. Offline file URL; no IGN return.
"""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,tempfile
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/cochonnet/cold');p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest()
def bridge(path):
 t=ast.parse(path.read_text());return next(ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='bridge' for k in n.targets))
seed_bridge=bridge(root/'tests/expansion/lys_browser_smoke.py')+'\n'+bridge(root/'tests/expansion/cochonnet_browser_smoke.py')+r'''
globalThis.__B73_COLD={
 idle(){return gameStarted&&!zoneTransitioning&&!V046.busy&&!V047.pending;},
 prepare(scenario){
  __B73_QA.setup();state.v042.activeInterior=MistralBoules.SITE;state.v042.returnPoint=null;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';
  __B73_QA.near('nelly');if(!__MISTRAL_DEBUG.v073BoulesAction('start'))throw Error('Seed start refused');
  __B73_QA.near('cercle');__B73_QA.aim(-.035);fireWeapon();updateEnemies(.2);
  if(scenario==='completed')for(let n=0;n<7&&state.v073Boules.round.phase!=='result';n++){
   __B73_QA.ticks(150);const r=state.v073Boules.round;
   if(r.phase==='aim'&&r.turn==='player'){__B73_QA.near('cercle');__B73_QA.aim(-.035);fireWeapon();}
  }
  if(scenario==='completed'&&state.v073Boules.round.phase!=='result')throw Error('Seed did not finish');
  if(scenario==='flight'&&state.v073Boules.round.phase!=='moving')throw Error('Seed not airborne');
  if(saveGame(false)===false)throw Error('Seed save refused');
  const key=__MISTRAL_DEBUG.v050ContinueInfo()[0].key;
  return {key,raw:localStorage.getItem(key),ledger:state.v073Boules,legacy:state.v046.lore.petanque};
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert production.decode().count(marker)==1
seed=production.decode().replace(marker,seed_bridge+'\n'+marker).encode()
observer=r'''document.addEventListener('click',event=>{if(event.target.closest?.('#btnContinue'))queueMicrotask(()=>{const d=window.__MISTRAL_DEBUG;if(d?.getMode()==='PLAYING')d.pause();d?.setRenderPaused(true);});});'''
checks=[];errors=[]
def check(label,ok):
 assert ok,label
 checks.append(label);print('PASS',label,flush=True)
with tempfile.TemporaryDirectory(prefix='cochonnet-delivery-') as delivery:
 entry=Path(delivery)/'index.html';url=entry.as_uri()+'?skipboot=1'
 with sync_playwright() as pw:
  for scenario in ['flight','completed']:
   with tempfile.TemporaryDirectory(prefix='cochonnet-profile-') as profile:
    opts=dict(executable_path=a.chromium,headless=True,viewport={'width':1280,'height':800},args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    entry.write_bytes(seed);context=pw.chromium.launch_persistent_context(profile,**opts)
    try:
     page=context.pages[0];page.set_default_timeout(10000);page.on('pageerror',lambda e:errors.append(e.stack))
     page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v073BoulesInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_function('__B73_COLD.idle()')
     expected=page.evaluate('(s)=>__B73_COLD.prepare(s)',scenario);envelope=json.loads(expected['raw']);stored=envelope.get('snapshot',envelope)
     check(scenario+': native disk storage contains full ledger',page.evaluate('localStorage instanceof Storage') and stored['v073Boules']==expected['ledger'])
    except Exception:
     page.screenshot(path=str(a.output/(scenario+'-seed-failure.png')));raise
    finally:context.close()
    entry.write_bytes(production);context=pw.chromium.launch_persistent_context(profile,**opts)
    try:
     page=context.pages[0];page.set_default_timeout(10000);page.on('pageerror',lambda e:errors.append(e.stack));page.add_init_script(observer)
     response=page.goto(url,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v073BoulesInfo')
     check(scenario+': unchanged production bytes on resume',hashlib.sha256(response.body()).hexdigest()==sha)
     check(scenario+': no fixture bridge or memory storage on resume',page.evaluate('typeof __B73_QA==="undefined"&&typeof __B73_COLD==="undefined"&&localStorage instanceof Storage'))
     check(scenario+': native disk save survives complete process restart',page.evaluate('(k)=>localStorage.getItem(k)',expected['key'])==expected['raw'])
     page.wait_for_selector('#menuScreen.active');check(scenario+': native Continue enabled',page.locator('#btnContinue').is_enabled());page.locator('#btnContinue').click();page.wait_for_function('__MISTRAL_DEBUG.v073BoulesInfo().local')
     got=page.evaluate('__MISTRAL_DEBUG.v073BoulesInfo()');live=page.evaluate('__MISTRAL_DEBUG.getState()')
     check(scenario+': actual court restored by Continue',got['local'] and live['v042']['activeInterior']=='v073-cour-cent-treves')
     check(scenario+': exact positions velocities turn and score restored',got['ledger']==expected['ledger'])
     check(scenario+': old victory counters unchanged',live['v046']['lore']['petanque']==expected['legacy'])
     check(scenario+': inventory capsules ammunition unchanged',live['inventory']==stored['inventory'] and all(live['player'][k]==stored['player'][k] for k in ['caps','ammoClip','ammoReserve','xp']))
     check(scenario+': earlier campaign ledgers unchanged',all(live[k]==stored[k] for k in ['v072Rats','v071Cigales','v070Secours','v069Parts','v068Lys','v067Devoir','v066Voisins','v065Notaires','v064Mutuelle','v063Radieuse','v062Pharmacy','v061Poste','v060Council']))
     page.screenshot(path=str(a.output/(scenario+'-continue.png')))
    except Exception:
     page.screenshot(path=str(a.output/(scenario+'-resume-failure.png')));print('RESUME',page.evaluate('__MISTRAL_DEBUG.v073BoulesInfo()'),flush=True);raise
    finally:context.close()
check('no JavaScript errors during cold resumes',not errors)
report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'scope':__doc__}
(a.output/'COCHONNET_COLD_SAVE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
