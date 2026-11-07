"""Instrumented smoke: real authored Radieuse interior, real UI/save/renderer.
Isolated storage and campaign setup. Does not certify the real IGN exterior.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/radieuse')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__R63_QA={
 enter(){closePipboy();debugDismissDialogue();debugRenderPaused=true;
  for(const id of ['water','food','cloth','scrap','circuitry','chemicals'])state.inventory[id]=30;
  state.player.caps=200;state.player.hp=100;state.v063Radieuse=MistralRadieuse.fresh();
  state.v042.activeInterior=MistralRadieuse.SITE.id;state.v042.returnPoint=null;
  V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});
  updatePlayer=()=>{};mode='PLAYING';onGround=true;
  return {id:world.id,custom:!!world.v063Radieuse,npcs:world.npcs.length,draws:world.staticDraws.length};
 },
 near(id){const p=__MISTRAL_DEBUG.v063RadieuseInfo().points[id];state.player.pos=[p[0],p[1]+1.65,p[2]+2];state.player.pitch=-.2;state.player.yaw=0;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.65]),collides:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1])};},
 talk(id){mode='PLAYING';return talkToNPC('r63:'+id);},
 scene(){return {pos:state.player.pos,doors:world.colliders.filter(c=>c.r63Gate).map(c=>c.disabled),leak:world.hazards.filter(h=>h.id==='r63-leak').length,lit:world.staticDraws.filter(d=>d.r63Light&&d.emissive>0).length,plants:world.staticDraws.filter(d=>d.r63Show==='toit'&&!d.hidden).length};},
 walk(points){mode='PLAYING';let visited=[];state.player.pos=[...points[0]];for(let i=1;i<points.length;i++){const t=points[i];const ox=state.player.pos[0],oz=state.player.pos[2],steps=Math.ceil(Math.hypot(t[0]-ox,t[2]-oz)/.12);for(let j=0;j<steps;j++){tryPlayerMove((t[0]-ox)/steps,(t[2]-oz)/steps);state.player.pos[1]=groundHeightAt(state.player.pos[0],state.player.pos[2],state.player.pos[1]-1.65)+1.65;}visited.push(state.player.pos.slice());}return visited;},
 render(which='hall'){
  for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const el=document.getElementById(id);if(el){el.classList.remove('active');el.classList.add('hidden');}}
  mode='PLAYING';document.getElementById('questFlash')?.classList.remove('show');document.getElementById('toastStack')?.replaceChildren();document.getElementById('questFlash').style.display='none';document.getElementById('interactPrompt').classList.add('hidden');selectedInteractable=null;const cams={hall:{pos:[3,2.4,27],target:[0,2,10]},rue:{pos:[-5,5.2,6],target:[9,4.5,-9]},toit:{pos:[15,8.3,-23],target:[-6,7,-31]},pompe:{pos:[-13,2,-3],target:[-19,1,-8]}};const c=cams[which];
  const camera={pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:65};sky?.draw(currentEnv(),performance.now());const draws=collectDraws(gameClock);renderer.render(draws,camera,currentEnv());return {engine:renderer.constructor.name,count:draws.length};
 },
 doorTrip(){
  debugDismissDialogue();mode='PLAYING';const s=MistralRadieuse.SITE;
  world=createWorld('geo_marseille','Extérieur synthétique pour les portes','PAS LA CARTE IGN');world.geoMacro=true;world.v046=true;world.v046Anchor=[0,0,0];world.v046Records=new Map();world.geoTiles=new Map();world.v046ChunkDraws=[];world.v047TerrainDraws=[];world.bounds=[-30,30,-30,30];world.v047TerrainBank={read:()=>({height:0}),grids:new Map()};
  V046.terrain=world.v047TerrainBank;V046.readyAnchor=[0,0,0];V046.busy=false;V047.pending=false;zoneTransitioning=false;v049Own(world);state.player.zone=world.id;state.player.pos=[0,1.65,3];state.player.yaw=0;state.player.pitch=0;state.v042.activeInterior=null;
  V042_RUNTIME.active.clear();V042_RUNTIME.npcData.clear();V042_RUNTIME.worldId=world.id;V042_RUNTIME.nearest=null;v042Entrance(world,[0,0,0],s);
  const exterior=world,door=world.interactables.find(i=>i.id==='v042-enter-'+s.id),entered=door.onInteract();const inside=!!world.v063Radieuse;state.player.pos=[0,1.65,26];onGround=true;
  const exit=world.interactables.find(i=>i.id==='r63:exit');const exited=exit.onInteract();return {entered,inside,exited,restored:world===exterior,active:state.v042.activeInterior,finished:state.v063Radieuse.finished,zone:state.player.zone};
 },
 reload(){const raw=JSON.parse(localStorage.getItem(SAVE_KEY));state=migrateState(raw);loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});return __MISTRAL_DEBUG.v063RadieuseInfo();},
 saveFailure(){const real=saveGame,old=JSON.stringify(state);saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v063RadieuseAction('repair','pompe');}finally{saveGame=real;}return {result,equal:old===JSON.stringify(state)};},
 state(){return {ledger:state.v063Radieuse,inv:state.inventory,caps:state.player.caps,previous:JSON.stringify([state.v060Council,state.v061Poste,state.v062Pharmacy])};}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralRadieuse=' in html
html=html.replace(marker,bridge+'\n'+marker)
checks=[];errors=[]
def check(name,value):
    assert value,name
    checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7000)
    page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
    try:
        page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v063RadieuseInfo')
        page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2500)
        page.evaluate('__MISTRAL_DEBUG.v063RadieuseOpen()')
        check('Pip-Boy includes the dedicated chapter','Assemblée générale extraordinaire' in page.locator('#pipboy').inner_text())
        page.screenshot(path=str(a.output/'01-carnet-desktop.png'))
        page.set_viewport_size({'width':390,'height':844});check('mobile no document-wide overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        page.screenshot(path=str(a.output/'02-carnet-mobile.png'));page.set_viewport_size({'width':1280,'height':800})
        built=page.evaluate('__R63_QA.enter()');print('BUILD',built,flush=True)
        check('dedicated authored instance and five human delegates',built['custom'] and built['npcs']==5)
        before=page.evaluate('__R63_QA.state().previous')
        # Physical collision routing, not teleportation between landing heights.
        path=[[0,1.65,25],[18,1.65,24],[18,1.65,9],[0,4.85,0],[-18,4.85,-8],[-18,4.85,-24],[10,8.05,-28]]
        walked=page.evaluate('(p)=>__R63_QA.walk(p)',path);print('WALK',walked,flush=True)
        check('two stairs reachable with native collision movement',abs(walked[-1][0]-10)<.3 and abs(walked[-1][1]-8.05)<.2 and abs(walked[-1][2]+28)<.3)
        back=page.evaluate('(p)=>__R63_QA.walk(p)',[[10,8.05,-28],[-18,8.05,-24],[-18,8.05,-8],[0,4.85,0],[18,4.85,9],[18,4.85,24],[0,1.65,25]])
        check('both stairs also descend without locking',abs(back[-1][1]-1.65)<.2 and abs(back[-1][0])<.3 and abs(back[-1][2]-25)<.3)
        workshop=page.evaluate('(p)=>__R63_QA.walk(p)',[[0,1.65,25],[-5,1.65,25],[-5,1.65,0],[-18,1.65,0],[-18,1.65,-6]])
        check('ground workshop doorway is walkable',abs(workshop[-1][0]+18)<.3 and abs(workshop[-1][2]+6)<.3 and abs(workshop[-1][1]-1.65)<.2)
        check('current year matches canonical 2297',page.locator('#locationCard small').inner_text().endswith('2297'))
        check('local quest replaces unrelated prologue HUD','PARTIES COMMUNES' in page.locator('#questTitle').inner_text())
        def choose(text):
            print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
        def npc(id):
            pos=page.evaluate('(id)=>__R63_QA.near(id)',id);check('reachable delegate '+id,pos['los'] and not pos['collides']);page.evaluate('(id)=>__R63_QA.talk(id)',id)
        npc('josiane');choose('Accepter');choose('Consigner');choose('Revenir.')
        check('accepted via actual dialogue',page.evaluate('__R63_QA.state().ledger.accepted'))
        for id in ['karim','lucie','nadia','salome']:
            npc(id);choose('Consigner');choose('Revenir.')
        for id in ['registre','pompe','reseau','toit']:
            pos=page.evaluate('(id)=>__R63_QA.near(id)',id);print('EVIDENCE',id,pos,flush=True)
            check('E selector finds '+id,pos['selected']=='r63:'+id and pos['los'] and not pos['collides'])
            page.keyboard.press('e');choose('Examiner et conserver');choose('Revenir.')
        check('all four findings saved',page.evaluate('__R63_QA.state().ledger.evidence.length')==4)
        page.evaluate('__R63_QA.near("assemblee")');page.keyboard.press('e')
        choose('Répartition par usage');choose('quatre délégations');choose('Mandat à SYNDIC');choose('Soumettre')
        check('rejected vote keeps negotiations open',page.evaluate('__R63_QA.state().ledger.vote===null&&__R63_QA.state().ledger.attempts===1'))
        choose('Contribution solidaire');choose('Tous les habitants');choose('Vérification par');choose('Soumettre')
        check('amended vote includes roof delegation',page.evaluate('__R63_QA.state().ledger.vote.yes')==4)
        page.screenshot(path=str(a.output/'03-vote-adopte.png'));choose('Revenir.')
        scene=page.evaluate('__R63_QA.scene()');check('vote alone does not repair equipment',scene['leak']==1 and scene['doors']==[False] and scene['lit']==0)
        page.evaluate('__R63_QA.render("pompe")');page.screenshot(path=str(a.output/'04-pompe-avant.png'))
        page.evaluate('__R63_QA.near("pompe")');failed=page.evaluate('__R63_QA.saveFailure()');check('failed save rolls back whole repair',not failed['result'] and failed['equal'])
        for id in ['pompe','reseau','toit']:
            page.evaluate('(id)=>__R63_QA.near(id)',id);page.keyboard.press('e');choose('Réaliser le travail');choose('Revenir.')
        scene=page.evaluate('__R63_QA.scene()');check('actual repairs remove leak and open shutter',scene['leak']==0 and scene['doors']==[True]);check('lamps and planters visibly change',scene['lit']==4 and scene['plants']==4)
        page.evaluate('__R63_QA.render("rue")');page.screenshot(path=str(a.output/'05-rue-reparee.png'))
        page.evaluate('__R63_QA.render("toit")');page.screenshot(path=str(a.output/'06-toit-repare.png'))
        npc('josiane');choose('réceptionner');choose('Revenir.');check('single completion reward',page.evaluate('__R63_QA.state().caps')==265)
        page.evaluate('__R63_QA.near("pompe")');page.keyboard.press('e');choose('Retirer 2 eaux');choose('Revenir.')
        check('finite common reserve consumed',page.evaluate('__R63_QA.state().ledger.water')==2)
        restored=page.evaluate('__R63_QA.reload()');check('save reload preserves vote repairs and water',restored['ledger']['finished'] and len(restored['ledger']['works'])==3 and restored['ledger']['water']==2)
        check('old systems unchanged',page.evaluate('__R63_QA.state().previous')==before)
        trip=page.evaluate('__R63_QA.doorTrip()');print('DOORS',trip,flush=True)
        check('native entrance opens the dedicated instance',trip['entered'] and trip['inside'])
        check('native exit restores retained exterior without losing works',trip['exited'] and trip['restored'] and trip['active'] is None and trip['finished'])
        check('no JavaScript exceptions',not errors)
        report={'html_sha256':sha,'checks':checks,'passed':len(checks),'errors':errors,'browser':browser.version,'scope':'Real authored interior, models, UI, native collision function, saves and software renderer. Injected setup and isolated MemoryStorage; synthetic exterior for portal round-trip, no real IGN exterior traversal.'}
        (a.output/'RADIEUSE_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2))
    except Exception:
        page.screenshot(path=str(a.output/'failure.png'))
        print('STATE',page.evaluate('window.__R63_QA?.state()'),flush=True)
        raise
    finally:
        browser.close()
