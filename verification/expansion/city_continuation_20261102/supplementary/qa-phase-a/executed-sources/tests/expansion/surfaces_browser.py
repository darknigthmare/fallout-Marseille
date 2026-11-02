#!/usr/bin/env python3
"""Native JavaScript integration of measured decks and production player physics.

Uses controlled bridge geometry and baseline DEM; this is not a GIS source survey
or a full campaign browser proof. No game code or movement assertions are replaced.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright


def main():
    core = (ROOT / 'src/core-v017.js').read_text()
    script = """
      const noop=()=>{},V018={qaFreeze:false};
      const world={v046:true,id:'geo_huveaune',bounds:[-100,100,-100,100],hazards:[],v046Records:new Map()};
      let state,mode='PLAYING',gameStarted=true,zoneTransitioning=false,onGround=true,jumpVelocity=0,bobPhase=0,reloadTimer=0,weaponKick=0,autosaveTimer=0,inCombat=false,missing=false;
      const keys=new Set(),touchMove={x:0,y:0},audio={tone:noop};
      const isBoatZone=()=>false,pollGamepad=()=>({x:0,y:0,sprint:false}),clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
      const playerEyeHeight=()=>1.65,collidesAt=()=>false,v047Height=()=>({height:missing?null:0}),v047Bank=()=>({});
      const updateStatus=noop,updateNPCSchedules=noop,updateSelectedInteractable=noop,updateLootProximity=noop,updateCompanion=noop,updateEnemies=noop,updateRoux=noop,updateWeather=noop,saveGame=noop;
      function groundHeightAt(){return 0;}
    """
    script += (ROOT / 'src/v046/00_integrity.js').read_text()
    script += core[core.index('function tryPlayerMove('):core.index('function tryEnemyMove(')]
    script += core[core.index('function updatePlayer(dt)'):core.index('function toggleCrouch(')]
    script += (ROOT / 'src/v050/04b_surfaces.js').read_text()
    script += """
      function bridge(path=[[-10,0,4],[10,0,4]],props={}){
        const properties={bridge:'yes',width:6,...props},mesh=MistralIntegrity.roadMesh(path,properties,()=>0);
        const{vertices,faces,...profile}=mesh;
        return{mesh:'geoSurface',geoLayer:'transportation',sourceProfile:profile,roadWidth:mesh.width,roadProperties:properties,roadPath:path,vertices,faces,id:'native-fixture'};
      }
      function reset(draw=bridge(),feet=0,x=0){
        state={player:{pos:[x,feet+1.65,0],ap:100,maxAp:100,crouched:false,yaw:0},character:{trait:''},perks:{},weather:{type:'clear'},status:{},worldTime:12,playTime:0};
        world.v046Records=new Map([['tile',{roads:[draw]}]]);onGround=true;jumpVelocity=0;missing=false;
      }
      window.runSurfaceProof=()=>{
        const checks={},deck=4.085,foot=()=>state.player.pos[1]-1.65,near=(a,b)=>Math.abs(a-b)<1e-8;
        reset();updatePlayer(.1);checks.underpass_keeps_dem=near(foot(),0)&&onGround;
        reset(bridge([[0,0,0],[20,0,4]]),0,-.5);tryPlayerMove(.6,0);checks.ramp_entry=near(foot(),.105)&&onGround;
        tryPlayerMove(.5,0);checks.measured_slope=near(foot(),.205)&&onGround;
        reset(bridge(),6);onGround=false;jumpVelocity=-3;updatePlayer(.4);checks.falling_lands_on_deck=near(foot(),deck)&&onGround;
        reset(bridge(),1.8);onGround=false;jumpVelocity=5;updatePlayer(.2);checks.head_stays_below_plane=near(state.player.pos[1]+.18,deck-.001)&&jumpVelocity===0&&!onGround;
        reset(bridge(),deck,9.9);tryPlayerMove(.2,0);checks.edge_starts_fall=!onGround&&near(foot(),deck);
        reset(bridge([[-10,0],[10,0]],{layer:2}),0);updatePlayer(.1);checks.guessed_bridge_not_promoted=near(foot(),0)&&onGround;
        reset(bridge(),deck);missing=true;checks.nodata_preserved=near(groundHeightAt(0,0,deck),deck)&&v047Height().height===null;
        return checks;
      };
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<title>Measured bridge physics fixture</title>')
        page.add_script_tag(content=script)
        checks = page.evaluate('runSurfaceProof()')
        browser.close()
    report = {'suite': 'surfaces_browser', 'passed': sum(checks.values()),
              'failed': sum(not ok for ok in checks.values()), 'checks': checks, 'errors': errors}
    print(json.dumps(report, indent=2))
    return bool(report['failed'] or errors)


if __name__ == '__main__':
    raise SystemExit(main())
