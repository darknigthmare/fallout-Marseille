"""Compiled arsenal: production UI/equip/fire/reload/render; MemoryStorage on about:blank.
Existing diagnostics choose authored Aubagne, grant inspection weapons and step time.
No IGN traversal, acquisition certification, cold restart or human playtest claim.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, time
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/arsenal/browser');p.add_argument('--chromium',default=shutil.which('chromium'));a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
production=a.html.read_bytes();sha=hashlib.sha256(production).hexdigest();checks=[];errors=[];shots=[];started=time.monotonic()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
def check(name,ok):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(str(e)))
 def ev(s,arg=None):return page.evaluate(s,arg)
 def debug(name,*args):return ev('([name,args])=>__MISTRAL_DEBUG[name](...args)',[name,list(args)])
 def info():return debug('v056FirstPersonInfo')
 def state():return debug('v020State')
 def tick(n=1):return ev('(n)=>{for(let i=0;i<n;i++)__MISTRAL_DEBUG.v020Tick(.05,true);return __MISTRAL_DEBUG.v056FirstPersonRender();}',n)
 def invariant():
  s=state();return {k:s.get(k) for k in ['inventory','ammo','equipment','quest','rep','flags','v073Gabians','v074Pigeons','v076Consigne']}|{'caps':s['player']['caps']}
 def shot(name):
  path=a.output/(name+'.png');page.screenshot(path=str(path));shots.append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 try:
  page.set_content(shim+production.decode(),wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v056FirstPersonInfo');debug('startStory');page.wait_for_function('__MISTRAL_DEBUG.getState().v035.prologue.titleSeen && document.getElementById("v35pTitle").classList.contains("hidden")')
  debug('setRenderPaused',True);debug('v047Control',{'auto':False});debug('v018LoadInstance','aubagne');safe=[0,1.65,85];debug('v018CaptureAt',safe,0,0);tick(1)
  check('authored camera position collision-free',not debug('v020Collides',safe))
  matrix=[('saltArc','energy','energy'),('concordePistol','energy','energy-pistol'),('civicJudge','pistol','revolver'),('mistralNeedler','industrial','needle'),('ceramicSaw','blade','ceramic-disc'),('garlabanMortar','heavy','mortar40')]
  for wid,fam,prof in matrix:
   check('grant existing weapon for inspection '+wid,debug('v020GrantWeapon',wid));debug('v020Equip',wid);tick(1);i=info();check('correct native family and profile '+wid,i['family']==fam and i['profile']==prof and i['visible'])
   if wid=='ceramicSaw':check('native saw has guard and disc, not machete',i['parts'].get('ceramic-disc',0)>0 and i['parts'].get('saw-guard',0)>0 and i['parts'].get('blade',0)==0);shot('scie_ceramique')
  debug('v020Seed',{'syringes':40,'grenade40':8,'protonCell':14});page.mouse.click(700,400);page.wait_for_function('document.pointerLockElement===document.getElementById("gameCanvas")')
  for wid,held,old in [('mistralNeedler','held-needle-tray','held-cassette'),('garlabanMortar','held-40mm','held-rocket'),('saltArc','held-cell','held-magazine')]:
   debug('v020Equip',wid);debug('v018CaptureAt',safe,0,0);tick(10);before=state();b=debug('v020Combat');page.mouse.click(700,400);tick(2);after=debug('v020Combat');check('native trigger consumes ammunition '+wid,after['shots']>b['shots'] and after['ammo']<b['ammo']);page.keyboard.press('r');duration=debug('v020Combat')['reload'];check('native R begins reload '+wid,duration>0);tick(max(1,round(duration/.05*.5)));i=info();check('matching feed visible during native reload '+wid,i['pose']['loading'] and i['parts'].get(held,0)>0 and i['parts'].get(old,0)==0);shot('recharge_'+wid);tick(80);s=state();check('reload conserves actual ammunition '+wid,s['player']['ammoClip']+s['player']['ammoReserve']==before['player']['ammoClip']+before['player']['ammoReserve']-(b['ammo']-after['ammo']));check('no feed left floating after reload '+wid,info()['parts'].get(held,0)==0)
  baseline=invariant();page.keyboard.press('Tab');page.locator('#pipTabs button[data-arg="data"]').click();page.locator('[data-p27="sub"][data-arg="atelierArmes"]').click();check('guide available from native DATA subnavigation',page.locator('[data-arsenal-guide]').count()==1);check('search toolbar visible',page.locator('#p27Search').is_visible());check('55 catalogue records, not 55 granted weapons','55 fiches' in page.locator('[data-arsenal-guide]').inner_text());shot('carnet_ateliers')
  page.locator('#p27Search').fill('arc salin');check('search returns real local record',page.locator('[data-arsenal-detail="saltArc"]').count()==1);check('record uses actual proton ammunition','proton' in page.locator('[data-arsenal-ammo]').inner_text().lower());check('equipped flag matches actual weapon','ÉQUIPÉE' in page.locator('.p27-row').inner_text());check('guide reading preserves gameplay',invariant()==baseline)
  page.locator('#p27Search').fill('ceramique');check('accentless search selects ceramic entries',page.locator('.p27-row').count()>=2);page.locator('#p27Search').fill('<img src=x onerror=alert(1)>');check('injected search is plain text and no image added',page.locator('.p27-row').count()==0 and page.locator('#pipContent img').count()==0)
  page.locator('#p27Search').fill('');page.locator('[data-arsenal-filter]').click();check('owned-only filter has six actual owned regional weapons',page.locator('.p27-row').count()==6);page.locator('[data-arsenal-filter]').click();page.locator('[data-p27="page"][data-arg="1"]').click();check('pagination changes selection',page.locator('.p27-pages span').inner_text().startswith('2 /'))
  page.locator('#p27Search').fill('garlaban');page.locator('[data-p27="select"][data-arg="garlabanMortar"]').click();check('reference labels distinguish base damage and real ammo','Valeurs de base' in page.locator('[data-arsenal-detail]').inner_text() and '40 mm' in page.locator('[data-arsenal-ammo]').inner_text());page.locator('[data-arsenal-inventory]').click();check('inventory link opens the correct owned item',debug('v027UI')['sub']=='weapon' and debug('v027UI')['selected']=='garlabanMortar')
  page.locator('#pipTabs button[data-arg="data"]').click();page.locator('[data-p27="sub"][data-arg="atelierArmes"]').click();page.locator('#p27Search').fill('arc salin');page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(100);check('portrait guide remains reachable',page.locator('[data-arsenal-guide]').is_visible());check('no horizontal content overflow on portrait',ev('(()=>{const c=document.getElementById("pipContent");return c.scrollWidth<=c.clientWidth+2})()'));shot('carnet_portrait')
  page.locator('#p27Search').focus();page.keyboard.press('Control+A');page.keyboard.type('juge');page.keyboard.press('Tab');check('keyboard can leave search field',ev('document.activeElement.id')!='p27Search');check('reading/search/filter still preserve gameplay',invariant()==baseline);page.keyboard.press('Escape');check('guide exit returns to play',debug('v027UI')['mode'] in ['PLAYING','PAUSE']);check('no Javascript exception',not errors)
 finally:
  report={'html_sha256':sha,'scope':__doc__,'browser':browser.version,'passed':len(checks),'checks':checks,'errors':errors,'shots':shots,'complete':bool(checks and checks[-1]=='no Javascript exception'),'seconds':round(time.monotonic()-started,2)};(a.output/'ARSENAL_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close()
