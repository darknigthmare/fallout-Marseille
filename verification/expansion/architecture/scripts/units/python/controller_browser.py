#!/usr/bin/env python3
"""Actual game + Chromium DOM/input integration with simulated Gamepad API.

No physical device compatibility is claimed. The game HTML, UI callbacks,
keyboard events and browser localStorage are real; navigator.getGamepads is the
explicit test seam. Run against tools/serve_game.py after building the game.
"""
from pathlib import Path
import argparse, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8765/index.html?skipboot=1')
    parser.add_argument('--output',type=Path,default=Path('/workspace/.cloud-setup/fallout-marseille/implementation/controller'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    checks=[];errors=[];html_sha256=None
    def check(name,ok,detail=None):
        checks.append({'name':name,'ok':bool(ok),'detail':detail})
        print(('OK ' if ok else 'FAIL ')+name,flush=True)
        if not ok:raise AssertionError(name+': '+str(detail))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(viewport={'width':1440,'height':900})
        context.add_init_script("""window.__controllerPads=[];
            Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>window.__controllerPads});
            window.__controllerSet=(buttons=[],axes=[0,0,0,0],index=3)=>{
              window.__controllerPads=[null,null,null,{index,id:'Simulated standard controller',connected:true,mapping:'standard',axes,
                buttons:Array.from({length:17},(_,i)=>({pressed:buttons.includes(i),value:buttons.includes(i)?1:0}))}];
              window.__MISTRAL_DEBUG?.v050ControllerStep(performance.now());
            };
        """)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
        try:
            response=page.goto(args.url,wait_until='load',timeout=60000)
            html_sha256=hashlib.sha256(response.body()).hexdigest()
            page.locator('#menuScreen.active').wait_for(timeout=45000)
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
            page.evaluate('__MISTRAL_DEBUG.setRenderPaused(true)')
            check('Production controller initialization is exposed',page.evaluate("typeof __MISTRAL_DEBUG.v050ControllerInfo==='function'"))
            page.evaluate('__controllerSet([0])')
            check('Held confirm on nonzero-slot connection does not enter a menu',page.evaluate("__MISTRAL_DEBUG.getMode()==='MENU'&&__MISTRAL_DEBUG.v050ControllerInfo().index===3"))
            def sample(buttons=None,axes=None):
                page.evaluate('([b,a])=>__controllerSet(b,a)',[buttons or [],axes or [0,0,0,0]])
            def press(button):
                sample();sample([button]);sample()
            press(13)
            check('Gamepad navigation focuses an actual visible menu button',page.evaluate("document.activeElement.tagName==='BUTTON'&&document.activeElement.getClientRects().length>0"))
            sample();sample([0]);sample()
            check('Focused menu confirmation runs a real UI action',page.evaluate("__MISTRAL_DEBUG.getMode()!=='MENU'"),page.evaluate('__MISTRAL_DEBUG.getMode()'))
            # Return through the actual menu path; enter an existing isolated
            # exploration via its normal UI action and use fresh context storage.
            page.evaluate("document.getElementById('btnCreatorBack')?.click();__MISTRAL_DEBUG.v027Start();__MISTRAL_DEBUG.closePip();")
            page.wait_for_function("__MISTRAL_DEBUG.getMode()==='PLAYING'")
            sample()
            page.keyboard.down('w')
            check('Physical keyboard state is present before gamepad input',page.evaluate("__MISTRAL_DEBUG.v050ControllerInfo().keyboardKeys.includes('KeyW')"))
            sample([], [.8,0,0,0]);sample()
            page.evaluate('window.__controllerPads=[];__MISTRAL_DEBUG.v050ControllerStep(performance.now())')
            check('Gamepad disconnect preserves a held physical keyboard key',page.evaluate("__MISTRAL_DEBUG.v050ControllerInfo().keyboardKeys.includes('KeyW')&&!__MISTRAL_DEBUG.v050ControllerInfo().connected"))
            page.keyboard.up('w');sample()
            before=page.evaluate('__MISTRAL_DEBUG.getState().player.yaw')
            sample([], [0,0,.9,.6]);page.wait_for_timeout(80);sample()
            after=page.evaluate('__MISTRAL_DEBUG.getState().player')
            check('Right stick changes the actual player view with finite pitch',after['yaw']!=before and abs(after['pitch'])<=1.3)
            ammo=page.evaluate('__MISTRAL_DEBUG.getState().player.ammoClip')
            sample([7]);page.wait_for_timeout(80);sample()
            fired=page.evaluate('__MISTRAL_DEBUG.getState().player.ammoClip')
            check('RT fires the actual equipped weapon once on its edge',fired==ammo-1,{'before':ammo,'after':fired})
            press(8)
            check('Select opens the real Pip-Boy',page.evaluate("__MISTRAL_DEBUG.getMode()==='PIP'"))
            old_tab=page.evaluate('__MISTRAL_DEBUG.v027UI().tab');press(5)
            check('Pip-Boy shoulder navigation changes its real tab',page.evaluate('__MISTRAL_DEBUG.v027UI().tab')!=old_tab)
            old_sub=page.evaluate('__MISTRAL_DEBUG.v027UI().sub');press(7)
            check('Pip-Boy trigger navigation changes its real subtab without firing',page.evaluate('__MISTRAL_DEBUG.v027UI().sub')!=old_sub and page.evaluate('__MISTRAL_DEBUG.getState().player.ammoClip')==fired)
            sample([7]);sample([1,7]);page.wait_for_timeout(50)
            check('Held trigger across closing a menu does not fire into the world',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'") and page.evaluate('__MISTRAL_DEBUG.getState().player.ammoClip')==fired)
            sample();press(9)
            check('Start opens actual pause and release does not resume it',page.evaluate("__MISTRAL_DEBUG.getMode()==='PAUSE'"))
            page.locator('#btnPauseOptions').click();sample()
            page.locator('#v050PadLook').focus()
            old_value=float(page.locator('#v050PadLook').input_value());press(15)
            new_value=float(page.locator('#v050PadLook').input_value())
            stored=page.evaluate("JSON.parse(localStorage.getItem('mistral_controller_v1'))")
            check('Gamepad adjusts real range control and persists preferences',new_value>old_value and stored['look']==new_value,stored)
            page.locator('#v050PadInvert').focus();press(0)
            check('Gamepad toggles a real checkbox and updates settings',page.locator('#v050PadInvert').is_checked() and page.evaluate('__MISTRAL_DEBUG.v050ControllerInfo().preferences.invertY'))
            press(1)
            check('B closes options through the real options callback',page.evaluate("__MISTRAL_DEBUG.getMode()==='PAUSE'"))
            press(1)
            check('B resumes through the real pause callback',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            # Existing isolated combat exploration performs its documented
            # placement assistance; all actions below use gamepad mappings.
            page.evaluate('__MISTRAL_DEBUG.v025Start()')
            page.wait_for_function("__MISTRAL_DEBUG.getMode()==='VATS'")
            sample();press(0)
            first=page.evaluate('__MISTRAL_DEBUG.v025Snapshot().queue')
            check('V.A.T.S. A reserves a real target/limb shot',len(first)==1,first)
            press(13);press(0)
            second=page.evaluate('__MISTRAL_DEBUG.v025Snapshot().queue')
            check('V.A.T.S. directional selection changes the queued limb',len(second)==2 and second[0]['id']!=second[1]['id'],second)
            press(2)
            check('V.A.T.S. X removes the final reserved shot',len(page.evaluate('__MISTRAL_DEBUG.v025Snapshot().queue'))==1)
            vats_ammo=page.evaluate('__MISTRAL_DEBUG.getState().player.ammoClip');press(7)
            page.wait_for_timeout(700)
            remaining=page.evaluate('__MISTRAL_DEBUG.getState().player.ammoClip')
            check('V.A.T.S. RT executes the actual reserved shot',remaining==vats_ammo-first[0]['rounds'],{'before':vats_ammo,'after':remaining,'reserved':first[0]['rounds']})
            page.wait_for_function("__MISTRAL_DEBUG.getMode()==='PLAYING'")
            page.evaluate("__MISTRAL_DEBUG.v020Open('interventions')");sample();press(13)
            check('Field services receive real controller focus',page.evaluate("document.getElementById('v020Panel').contains(document.activeElement)"))
            press(1)
            check('B closes field services with their own callback',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            page.evaluate("__MISTRAL_DEBUG.v035Open('career')");sample();press(13)
            check('Career panel receives real controller focus',page.evaluate("document.getElementById('v035Screen').contains(document.activeElement)"))
            press(1)
            check('B closes career to the recorded previous mode',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            page.evaluate("__MISTRAL_DEBUG.openLockpick('controller-test', {difficulty:2})");sample()
            page.locator('#lockpickAngle').focus();initial_angle=float(page.locator('#lockpickAngle').input_value());press(15)
            check('Controller adjusts actual lockpick angle input',float(page.locator('#lockpickAngle').input_value())>initial_angle)
            press(1)
            check('B exits the real lockpicking activity',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            page.evaluate('__MISTRAL_DEBUG.openPetanque()');sample()
            page.locator('#petanqueAngle').focus();initial_angle=float(page.locator('#petanqueAngle').input_value());press(15)
            check('Controller adjusts the actual pétanque angle',float(page.locator('#petanqueAngle').input_value())>initial_angle)
            press(1)
            check('B exits the real pétanque activity',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            page.evaluate("__MISTRAL_DEBUG.openTerminal('aubagne')");sample();press(13)
            check('Terminal controls receive real controller focus',page.evaluate("__MISTRAL_DEBUG.getMode()==='TERMINAL'&&document.getElementById('terminalLoreScreen').contains(document.activeElement)"))
            press(1)
            check('B exits the terminal with its own callback',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            page.evaluate("__MISTRAL_DEBUG.openHolotape('aubagne')");sample();press(1)
            check('B exits the actual holotape player',page.evaluate("__MISTRAL_DEBUG.getMode()==='PLAYING'"))
            check('No JavaScript exceptions during controller integration',not errors,errors)
        except Exception as error:
            checks.append({'name':'Browser controller scenario completes','ok':False,'detail':str(error)})
            print('FAIL '+str(error),flush=True)
            page.screenshot(path=str(args.output/'failure.png'))
        finally:
            report={'scope':'Actual game + Chromium DOM and keyboard/storage; navigator.getGamepads explicitly simulated, no physical device validation','html_sha256':html_sha256,'passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'errors':errors,'checks':checks}
            (args.output/'CONTROLLER_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps({k:report[k] for k in ['passed','failed','total','errors']}),flush=True)
            context.close();browser.close()
    return int(bool(report['failed'] or errors))

if __name__=='__main__':raise SystemExit(main())
