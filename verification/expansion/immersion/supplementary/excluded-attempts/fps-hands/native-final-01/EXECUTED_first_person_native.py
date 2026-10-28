#!/usr/bin/env python3
"""Native foreground presentation pilot on unchanged production HTML.

Diagnostic navigation selects authored Aubagne (not a surveyed Marseille view),
places the camera at an existing collision-free road point, grants nine ordinary
weapons for a presentation matrix and ammunition for the reload check. Active
simulation is stepped with the inherited diagnostic v020Tick; UI inputs, Canvas,
WebGL scene, collisions, firing, reload and browser storage remain production.
No network, renderer, input handler or localStorage is replaced.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import sys
import threading
import time
import traceback
ROOT=Path(__file__).resolve().parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--expect-html-sha',required=True);p.add_argument('--expect-fps-sha',required=True);a=p.parse_args()
 if not a.run:print('Prepared only; pass --run with frozen production hashes.');return 0
 a.output.mkdir(parents=True,exist_ok=True);started=time.monotonic();r={'scope':__doc__,'checks':[],'shots':[],'page_errors':[],'console_errors':[],'request_failures':[],'local_http_errors':[],'native_navigation':False,'html_injected':False,'network_mocked':False,'storage_mocked':False,'input_hardware_claim':'Native Chromium mouse and keyboard; portrait pointer events are simulated by Playwright, not physical touch hardware.','assistance':['Existing authored Aubagne selected through v020Load.','Camera diagnostic at [0,1.65,85], actual production collision/LOS checked.','v020GrantWeapon equips nine ordinary weapons for presentation inspection; not acquisition or balancing evidence.','v020Seed ammo10=60 supplies reload inputs.','v020Tick(.05,true) steps active production simulation while frame progression is frozen for reproducible screenshots.','v028Settings controls existing reduceMotion/reducedFlashes settings for their visible checks.']};pinned={};server=browser=context=pw=None;code=1
 def save():
  r.update(passed=sum(c['ok']for c in r['checks']),failed=sum(not c['ok']for c in r['checks']),elapsed_seconds=round(time.monotonic()-started,3),pinned_inputs=pinned);(a.output/'FIRST_PERSON_NATIVE.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 def check(name,ok,detail=None):
  r['checks'].append({'name':name,'ok':bool(ok),'detail':detail});print(('OK 'if ok else'FAIL ')+name,flush=True);save()
  if not ok:raise AssertionError(name)
 def pin(relative,expected=None):
  got=sha(ROOT/relative)
  if expected is not None and got!=expected:raise AssertionError('Frozen input mismatch '+relative)
  if relative in pinned and got!=pinned[relative]:raise AssertionError('Input changed '+relative)
  pinned[relative]=got
 def debug(name,*values):return page.evaluate('([name,args])=>__MISTRAL_DEBUG[name](...args)',[name,list(values)])
 def info():return debug('v056FirstPersonInfo')
 def state():return debug('v020State')
 def tick(n=1):page.evaluate('(n)=>{for(let i=0;i<n;i++)__MISTRAL_DEBUG.v020Tick(.05,true)}',n)
 def shot(name):
  path=a.output/(name+'.png');page.screenshot(path=str(path));r['shots'].append({'file':path.name,'sha256':sha(path)});save()
 def pixels():return page.evaluate('''()=>{const c=document.getElementById('v056FirstPersonCanvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height),p=d.data;let solid=0,centre=0;for(let y=0;y<c.height;y+=3)for(let x=0;x<c.width;x+=3)if(p[(y*c.width+x)*4+3]>0){solid++;if(Math.abs(x-c.width/2)<c.width*.025&&Math.abs(y-c.height/2)<c.height*.025)centre++;}return{width:c.width,height:c.height,solid,centre,connected:c.isConnected,visible:getComputedStyle(c.parentElement).display!=='none'}}''')
 try:
  pin('index.html',a.expect_html_sha);pin('JOUER_FALLOUT_MISTRAL_v0.50.html',a.expect_html_sha);pin('src/v050/17_first_person.js',a.expect_fps_sha);pin('src/v050/19_fps_hud.js');pin('tests/expansion/first_person_native.py')
  sys.path.insert(0,str(ROOT/'tools'));from serve_game import GameHandler;from qa_support import chromium_path;from playwright.sync_api import sync_playwright
  class Handler(GameHandler):
   def log_message(self,*_):pass
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server_thread=threading.Thread(target=server.serve_forever,daemon=True);server_thread.start();origin=f'http://127.0.0.1:{server.server_address[1]}';r['url']=origin+'/index.html?skipboot'
  pw=sync_playwright().start();browser=pw.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);r['browser_version']=browser.version;context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block');page=context.new_page();page.set_default_timeout(30000)
  page.on('pageerror',lambda e:r['page_errors'].append(str(e)));page.on('console',lambda e:r['console_errors'].append(e.text)if e.type=='error'else None);page.on('requestfailed',lambda q:r['request_failures'].append({'url':q.url,'failure':q.failure}));page.on('response',lambda q:r['local_http_errors'].append({'url':q.url,'status':q.status})if q.url.startswith(origin+'/')and q.status>=400 else None);page.on('dialog',lambda d:d.accept())
  response=page.goto(r['url'],wait_until='load',timeout=60000);r['native_navigation']=True;check('HTTP loads the exact frozen production HTML',response.status==200 and hashlib.sha256(response.body()).hexdigest()==a.expect_html_sha);page.wait_for_function("typeof __MISTRAL_DEBUG?.v056FirstPersonInfo==='function'&&!document.getElementById('bootScreen').classList.contains('active')",timeout=120000)
  check('Menu hides the foreground and refuses held aim',not info()['visible']and not page.evaluate('v056FirstPersonAim(true)'))
  debug('setRenderPaused',True);debug('v047Control',{'auto':False});debug('v018LoadInstance','aubagne');safe=[0,1.65,85];check('Chosen authored road point is free under actual production collision',not debug('v020Collides',safe));debug('v018CaptureAt',safe,0,0);check('Native WebGL scene and projected foreground are both active',debug('v020Renderer')['webgl']and info()['visible']and info()['stats']['visibleFaces']>50)
  check('Foreground really paints nontransparent pixels and leaves the central hip aperture clear',pixels()['solid']>1000 and pixels()['centre']==0,pixels());shot('01_native_pistol_hip')
  matrix=[('pistol10','pistol'),('pipeCarbine','rifle'),('dockShotgun','shotgun'),('laserPistol','energy'),('missileLauncher','heavy'),('rivetGun','industrial'),('combatKnife','blade'),('sledgehammer','melee'),('powerFist','fist')];r['weapon_matrix']=[]
  for weapon,kind in matrix:
   check('Ordinary diagnostic grant succeeds for presentation: '+weapon,debug('v020GrantWeapon',weapon));check('Normal equip selects presentation weapon: '+weapon,debug('v020Equip',weapon));debug('v056FirstPersonRender');item=info();r['weapon_matrix'].append({'weapon':weapon,'info':item,'pixels':pixels()});check('Native attached canvas shows family '+kind,item['family']==kind and item['visible']and item['stats']['visibleFaces']>50 and pixels()['connected']and pixels()['solid']>1000)
   if kind in['rifle','energy','blade']:shot('02_matrix_'+kind)
  wall=page.evaluate('''()=>{const D=__MISTRAL_DEBUG;for(const c of D.v018World().colliders){if(![c.minX,c.maxX,c.minZ,c.maxZ].every(Number.isFinite)||c.disabled||Number.isFinite(c.maxY)&&c.maxY<2||Number.isFinite(c.minY)&&c.minY>1)continue;const x=(c.minX+c.maxX)/2,z=(c.minZ+c.maxZ)/2;for(const[p,t]of[[[c.minX-.5,1.65,z],[c.minX+.1,1.65,z]],[[c.maxX+.5,1.65,z],[c.maxX-.1,1.65,z]],[[x,1.65,c.minZ-.5],[x,1.65,c.minZ+.1]],[[x,1.65,c.maxZ+.5],[x,1.65,c.maxZ-.1]]])if(!D.v020Collides(p)&&!D.v020LOS(p,t))return{position:p,yaw:Math.atan2(t[0]-p[0],-(t[2]-p[2])),collider:c.id||null};}return null}''');check('An existing authored wall has a collision-free close approach',wall is not None,wall);debug('v018CaptureAt',wall['position'],wall['yaw'],0);check('Actual wall occlusion lowers the viewmodel and refuses aim',info()['proximity']==1 and not page.evaluate('v056FirstPersonAim(true)'));r['wall_approach']=wall;shot('02b_native_wall_lowering');debug('v018CaptureAt',safe,0,0)
  page.keyboard.down('w');tick(4);walking=info();page.keyboard.up('w');check('Actual forward movement drives bounded foreground gait',walking['visible'] and state()['player']['pos'][2]<safe[2]);page.keyboard.down('w');page.keyboard.down('Shift');tick(4);sprinting=info();page.keyboard.up('Shift');page.keyboard.up('w');check('Actual sprint movement lowers the foreground stance',sprinting['pose']['sprint']>0,sprinting['pose']);debug('v018CaptureAt',safe,0,0);tick(1)
  debug('v020Equip','pipeCarbine');debug('v018CaptureAt',safe,0,0);camera_before=debug('v025Snapshot')['camera'];resources_before=state();page.keyboard.down('x');tick(7);aimed=info();camera_after=debug('v025Snapshot')['camera'];check('Native held X aligns the sight presentation',aimed['aim']>.99 and aimed['aimHeld']);check('Aiming leaves the actual world direction and FOV unchanged',camera_before['dir']==camera_after['dir']and camera_before['fov']==camera_after['fov']);check('Aiming consumes no ammunition, inventory or capsules',resources_before['player']['ammoClip']==state()['player']['ammoClip']and resources_before['inventory']==state()['inventory']and resources_before['player']['caps']==state()['player']['caps']);shot('03_native_rifle_aim');page.keyboard.up('x');tick(7);check('Native X release returns the grip to the hip',not info()['aimHeld']and info()['aim']<.01)
  page.keyboard.down('x');tick(7);page.keyboard.press('Tab');check('Opening actual Pip-Boy clears held aim and hides hands',debug('v020Stats')['mode']=='PIP'and not info()['visible']and not info()['aimHeld']);page.keyboard.up('x');page.keyboard.press('Tab');check('Closing actual Pip-Boy restores the foreground without stuck aim',info()['visible']and not info()['aimHeld'])
  page.keyboard.press('c');check('Actual C hides the foreground in third person',state()['player']['cameraMode']=='third'and not info()['visible']);page.keyboard.press('c');check('Actual C restores first person presentation',state()['player']['cameraMode']=='first'and info()['visible'])
  debug('v020Equip','pistol10');debug('v020Seed',{'ammo10':60});debug('v018CaptureAt',safe,0,0);tick(6)
  page.mouse.click(700,420);page.wait_for_function("document.pointerLockElement===document.getElementById('gameCanvas')");before_fire=debug('v020Combat');page.mouse.click(700,420);after_fire=debug('v020Combat');check('Real pointer-locked left click emits exactly one ordinary pistol shot',after_fire['shots']==before_fire['shots']+1 and after_fire['ammo']==before_fire['ammo']-1,{'before':before_fire,'after':after_fire});check('Actual emitted shot drives foreground recoil',info()['pose']['origin'][2]<.67);shot('04_native_shot_recoil');tick(8)
  page.keyboard.press('r');check('Actual R starts the ordinary reload and releases aim',debug('v020Combat')['reload']>0 and not info()['aimHeld']);tick(6);check('Active simulation exposes the reload hand pose',info()['pose']['loading']and info()['pose']['reloadLift']>0);shot('05_native_reload_hands');tick(30);check('Ordinary reload finishes with the original clip capacity',debug('v020Combat')['reload']==0 and state()['player']['ammoClip']==10)
  page.evaluate('document.exitPointerLock()');page.set_viewport_size({'width':390,'height':844});debug('v018CaptureAt',safe,0,0);portrait=pixels();check('Portrait reuses one connected canvas at the actual viewport dimensions',portrait['width']==390 and portrait['height']==844 and portrait['connected']and portrait['solid']>1000,portrait);shot('06_native_portrait_hands')
  aim_button=page.locator('[data-fps56-aim]');check('Visible production hold-to-aim HUD action exists',aim_button.count()==1 and aim_button.is_visible());aim_button.hover();page.mouse.down();tick(7);check('HUD pointerdown holds actual presentation aim',info()['aimHeld']and info()['aim']>.99);page.mouse.up();tick(7);check('HUD pointerup releases aim without a stuck weapon',not info()['aimHeld']and info()['aim']<.01)
  debug('v028Settings',{'reduceMotion':True,'reducedFlashes':True});debug('v056FirstPersonRender');page.keyboard.down('x');debug('v056FirstPersonRender');check('Existing reduced motion setting applies the aim pose immediately',info()['aim']==1);page.keyboard.up('x');debug('v056FirstPersonRender');check('Reduced motion release immediately restores the static hip pose',info()['aim']==0);shot('07_native_portrait_reduced_motion');debug('v028Settings',{'reduceMotion':False,'reducedFlashes':False})
  check('Native pilot records no JavaScript exception',not r['page_errors'],r['page_errors']);check('Native local production resources have no HTTP failure',not r['local_http_errors'],r['local_http_errors']);
  for relative,expected in list(pinned.items()):pin(relative,expected)
  check('All production and pilot inputs retain their frozen hashes',True);code=0
 except Exception as e:
  r['exception']=repr(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
  if 'page'in locals():
   try:shot('failure')
   except Exception:pass
 finally:
  closed={}
  for name,obj in [('context',context),('browser',browser)]:
   try:
    if obj:obj.close()
    closed[name]=True
   except Exception as e:closed[name]=repr(e)
  try:
   if pw:pw.stop()
   closed['playwright']=True
  except Exception as e:closed['playwright']=repr(e)
  try:
   if server:server.shutdown();server.server_close();server_thread.join(timeout=5)
   closed['server']=True
  except Exception as e:closed['server']=repr(e)
  r.update(cleanup=closed,process_exit_code=code,stage='complete'if code==0 else'failed');save()
 return code
if __name__=='__main__':raise SystemExit(main())
