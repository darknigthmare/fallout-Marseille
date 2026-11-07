"""Offline/instrumented postal smoke. Requires Playwright and Chromium.
This does NOT validate the real IGN map or a human campaign traversal.
The production bundle is unmodified on disk; a clearly isolated test bridge is
injected in memory. The model, conversations, saves and renderer are real.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse
import hashlib
import json
import shutil

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--html', type=Path, default=root / 'index.html')
parser.add_argument('--output', type=Path, default=root / 'verification/poste-restante')
parser.add_argument('--chromium', default=shutil.which('chromium'))
args = parser.parse_args()
out = args.output
out.mkdir(parents=True, exist_ok=True)
html = args.html.read_text(encoding='utf-8')
assert 'const MistralPoste=' in html, 'Rebuild the production HTML before testing.'
original_sha = hashlib.sha256(args.html.read_bytes()).hexdigest()
shim = """<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__POSTE_QA={
 setup(){
  updatePlayer=()=>{};debugRenderPaused=true;
  state.quest.aubagneComplete=true;state.v060Council={schema:1,status:'ratified',charter:'charte_vivants',clauses:{preuve:'pluralite',minimum:'universel',controle:'audit',force:'sans_armee'},tally:{for:8,against:3,abstain:2,details:[]},slides:[{id:'charter',title:'CHARTE DES VIVANTS',text:'Ratification synthétique pour le test postal.'}]};
  for(const id of ['water','food','cloth','scrap','circuitry','antibiotics'])state.inventory[id]=20;
  world=createWorld('geo_huveaune','Banc postal synthétique','AUCUN RELEVÉ IGN',{skyTop:[78,121,146],skyBottom:[191,181,139]});world.v046=true;world.geoMacro=true;world.v046Records=new Map();world.geoTiles=new Map();world.v047TerrainBank={read:()=>({height:0}),grids:new Map()};world.v046ChunkDraws=[];world.v047TerrainDraws=[];
  v049Own(world);V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;onGround=true;settings.geoFalloutLayer=true;v050TravelGround=()=>0;
  state.player.zone='geo_huveaune';state.player.pos=[0,1.65,1];state.player.yaw=0;state.player.pitch=0;state.v042.activeInterior=null;state.v061Poste=MistralPoste.fresh();
  const site=v042Site(MistralPoste.HOME);state.v042.discovered[site.id]=true;
  V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();V042_RUNTIME.npcData.set('qa-relay',{siteId:site.id,name:'Relais synthétique',role:'facteur',index:0});
  const npc=addHumanNPC(world,'qa-relay','Relais synthétique','Facteur',[0,0,0]);npc.v042Site=site.id;
  addBox(world,[0,-.1,0],[30,.2,30],[.43,.40,.31]);addBox(world,[-2,.4,-1],[1.5,.8,1],[.34,.23,.13]);
  mode='PLAYING';gameStarted=true;
  return window.__MISTRAL_DEBUG.v061PosteInfo();
 },
 gotoStand(){const e=window.__MISTRAL_DEBUG.v061PosteInfo().physical[0];state.player.pos=[e.pos[0],e.pos[1]+1.65,e.pos[2]+1.5];state.player.pitch=-.25;return{eye:state.player.pos,stand:e.pos,lineOfSight:lineOfSight(state.player.pos,[e.pos[0],e.pos[1]+1,e.pos[2]+.55]),condition:world.interactables.find(x=>x.id==='post61:identite').condition()};},
 talk(){mode='PLAYING';return v042TalkNPC('qa-relay');},
 select(){mode='PLAYING';updateSelectedInteractable();return selectedInteractable?.id;},
 render(){mode='PLAYING';for(const id of['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}
  const e=window.__MISTRAL_DEBUG.v061PosteInfo().physical[0],pos=e.pos;
  const parts=collectDraws(gameClock).filter(x=>x.v061Poste);const camera={pos:[pos[0]+1.9,pos[1]+1.8,pos[2]+3.4],dir:vNorm(vSub([pos[0],pos[1]+.7,pos[2]],[pos[0]+1.9,pos[1]+1.8,pos[2]+3.4])),fov:54};
  sky?.draw(currentEnv(),performance.now());renderer.render(world.staticDraws.concat(parts),camera,currentEnv());return {draws:parts.length,engine:renderer.constructor.name};
 },
 reload(){const data=JSON.parse(localStorage.getItem(SAVE_KEY));state=migrateState(data);v049Own(world);return window.__MISTRAL_DEBUG.v061PosteInfo();}
};
'''
marker = '/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker) == 1
html = html.replace(marker, bridge + '\n' + marker)
checks = []
errors = []

def check(name, condition):
    assert condition, name
    checks.append(name)

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=args.chromium, headless=True,
        args=['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.on('pageerror', lambda e: errors.append(e.stack))
    page.set_content(shim + html, wait_until='load')
    page.wait_for_function('!!window.__MISTRAL_DEBUG?.v061PosteInfo')
    page.evaluate('__MISTRAL_DEBUG.startStory()')
    page.wait_for_timeout(4000)
    page.evaluate('__MISTRAL_DEBUG.v061PosteOpen()')
    check('locked before ratification', 'La tournée s’ouvre' in page.locator('#pipboy').inner_text())
    page.evaluate("""()=>{const d=__MISTRAL_DEBUG,s=d.getState();s.quest.aubagneComplete=true;
      s.v060Council={schema:1,status:'ratified',charter:'charte_vivants',clauses:{preuve:'pluralite',minimum:'universel',controle:'audit',force:'sans_armee'},
        tally:{for:8,against:3,abstain:2,details:[]},slides:[{id:'charter',title:'CHARTE DES VIVANTS',text:'Ratification injectée pour le test.'}]};
      d.v023Restore(JSON.stringify(s));d.v061PosteOpen();}""")
    check('seven dossiers visible in Pip-Boy', page.locator('#pipboy .v046-notice').count() == 7)
    page.screenshot(path=str(out / '01-pipboy-desktop.png'))
    page.set_viewport_size({'width':390,'height':844})
    check('mobile viewport no page-wide overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
    page.screenshot(path=str(out / '02-pipboy-mobile.png'))
    page.set_viewport_size({'width':1280,'height':800})
    page.evaluate("__POSTE_QA.setup();document.getElementById('pipboy').classList.remove('active');document.getElementById('pipboy').classList.add('hidden')")
    info = page.evaluate('__MISTRAL_DEBUG.v061PosteInfo()')
    check('synthetic relay creates one stand', len(info['physical']) == 1 and info['draws'] == 4)
    page.evaluate('__POSTE_QA.talk()')
    topic = page.locator('#dialogueChoices button').filter(has_text='Poste Restante')
    check('postal topic added to existing dialogue', topic.count() == 1 and page.locator('#dialogueChoices button').count() > 1)
    topic.click()
    page.locator('#dialogueChoices button').filter(has_text='Accepter la tournée').click()
    check('accepted through real dialogue button', page.evaluate('__MISTRAL_DEBUG.v061PosteInfo().ledger.accepted'))
    page.locator('#dialogueChoices button').get_by_text('Revenir.', exact=True).click()
    approach = page.evaluate('__POSTE_QA.gotoStand()')
    check('stand does not occlude its own interaction', approach['lineOfSight'] and approach['condition'])
    check('actual interaction selector finds the stand', page.evaluate('__POSTE_QA.select()') == 'post61:identite')
    page.keyboard.press('e')
    check('E reads the evidence', page.evaluate('__MISTRAL_DEBUG.v061PosteInfo().ledger.letters.identite.read'))
    page.locator('#dialogueChoices button').filter(has_text='Fermer le document').click()
    before = page.evaluate('__MISTRAL_DEBUG.getState().inventory.cloth')
    page.evaluate('__POSTE_QA.talk()')
    page.locator('#dialogueChoices button').filter(has_text='Poste Restante').click()
    page.locator('#dialogueChoices button').filter(has_text='Faire reconnaître la présence').click()
    check('NPC choice deducts actual cloth', page.evaluate('__MISTRAL_DEBUG.getState().inventory.cloth') == before - 1)
    check('chosen outcome saved', page.evaluate('__MISTRAL_DEBUG.v061PosteInfo().ledger.letters.identite.choice') == 'a')
    page.locator('#dialogueChoices button').get_by_text('Revenir.', exact=True).click()
    check('finite gift has an actual rendered cache', page.evaluate('__POSTE_QA.render().draws') == 6)
    page.evaluate("""(()=>{const e=document.createElement('div');e.textContent='BANC SYNTHÉTIQUE • MOTEUR RÉEL • PAS LA CARTE IGN';
      e.style='position:fixed;z-index:999999;left:18px;top:18px;background:#161b21;color:#fff;padding:12px;font:14px monospace;pointer-events:none';document.body.appendChild(e)})()""")
    page.screenshot(path=str(out / '03-cache-present.png'))
    water = page.evaluate('__MISTRAL_DEBUG.getState().inventory.water')
    page.evaluate('__POSTE_QA.select()')
    page.keyboard.press('e')
    check('E claims exactly two waters', page.evaluate('__MISTRAL_DEBUG.getState().inventory.water') == water + 2)
    render = page.evaluate('__POSTE_QA.render()')
    check('gift cache disappears after claiming', render['draws'] == 4)
    page.screenshot(path=str(out / '04-cache-claimed.png'))
    restored = page.evaluate('__POSTE_QA.reload()')
    check('actual save migration preserves claim', restored['ledger']['letters']['identite']['claimed'])
    check('repeated claim refused after reload', not page.evaluate("__MISTRAL_DEBUG.v061PosteAction('claim','identite',null,'v042-huveaune-caravan-02')"))
    check('no JavaScript exceptions during tested path', not errors)
    report = {'html_sha256':original_sha,'checks':checks,'passed':len(checks),'errors':errors,
      'browser':browser.version,'renderer':render['engine'],
      'scope':'Offline about:blank, isolated MemoryStorage, injected ratification; flat synthetic relay and ground stub. Real game model/UI/save/renderer. Not a real-map or hardware performance certification.'}
    (out/'POSTE_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    browser.close()
