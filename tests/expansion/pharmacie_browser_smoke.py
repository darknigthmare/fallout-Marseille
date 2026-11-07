"""Instrumented browser smoke on the real production bundle.
Synthetic flat relays and isolated storage, not an IGN traversal or human playtest.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/pharmacie-garde')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__PH_QA={
 setup(){closePipboy();debugDismissDialogue();updatePlayer=()=>{};debugRenderPaused=true;state.v062Pharmacy=MistralPharmacy.fresh();state.player.caps=200;state.player.hp=60;state.player.maxHp=115;state.character.special.I=5;for(const id of ['water','food','cloth','scrap','circuitry','chemicals','antibiotics'])state.inventory[id]=20;return this.relay(MistralPharmacy.HOME,8);},
 relay(id,h=state.worldTime){
  world=createWorld('geo_marseille','Relais synthétique de pharmacie','AUCUN RELEVÉ IGN',{skyTop:[78,121,146],skyBottom:[191,181,139]});world.v046=true;world.geoMacro=true;world.v046Records=new Map();world.geoTiles=new Map();world.v047TerrainBank={read:()=>({height:0}),grids:new Map()};world.v046ChunkDraws=[];world.v047TerrainDraws=[];
  v049Own(world);V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;onGround=true;settings.geoFalloutLayer=true;v050TravelGround=()=>0;
  state.player.zone='geo_marseille';state.player.pos=[0,1.65,1];state.player.yaw=0;state.player.pitch=0;state.v042.activeInterior=null;state.worldTime=h;
  const site=v042Site(id);state.v042.discovered[id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();V042_RUNTIME.npcData.set('qa-relay',{siteId:id,name:'Relais synthétique',role:'soignant',index:0});const n=addHumanNPC(world,'qa-relay','Relais synthétique','Soignant',[0,0,0]);n.v042Site=id;
  addBox(world,[0,-.1,0],[32,.2,32],[.43,.40,.31]);mode='PLAYING';gameStarted=true;return __MISTRAL_DEBUG.v062PharmacyInfo();
 },
 talk(){mode='PLAYING';return v042TalkNPC('qa-relay');},
 nearStand(){const e=__MISTRAL_DEBUG.v062PharmacyInfo().physical[0];state.player.pos=[e.pos[0],e.pos[1]+1.65,e.pos[2]+1.6];state.player.pitch=-.23;state.player.yaw=0;mode='PLAYING';updateSelectedInteractable();return {id:selectedInteractable?.id,visible:lineOfSight(state.player.pos,[e.pos[0],e.pos[1]+1.15,e.pos[2]+.65])};},
 render(){mode='PLAYING';for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}const entry=__MISTRAL_DEBUG.v062PharmacyInfo().physical[0],p=entry.pos,parts=collectDraws(gameClock).filter(d=>d.v062Pharmacy);const cam={pos:[p[0]+1.9,p[1]+1.8,p[2]+3.4],dir:vNorm(vSub([p[0],p[1]+.9,p[2]],[p[0]+1.9,p[1]+1.8,p[2]+3.4])),fov:54};sky?.draw(currentEnv(),performance.now());renderer.render(world.staticDraws.concat(parts),cam,currentEnv());return {draws:parts.length,engine:renderer.constructor.name};},
 reload(){const raw=JSON.parse(localStorage.getItem(SAVE_KEY));state=migrateState(raw);v049Own(world);return __MISTRAL_DEBUG.v062PharmacyInfo();},
 hurt(){state.player.hp=50;state.player.rad=19;state.status.infection=7;},
 closed(){mode='PLAYING';return __MISTRAL_DEBUG.v062PharmacyAction('buy','v042-marseille-caravan-02',null,'stimpak');}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1
html=html.replace(marker,bridge+'\n'+marker)
checks=[];errors=[]
def check(name,value):
    assert value,name
    checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':900})
    page.set_default_timeout(7000)
    page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
    page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v062PharmacyInfo')
    page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(3500)
    page.evaluate('__MISTRAL_DEBUG.v062PharmacyOpen()')
    check('three pharmacy cards visible',page.locator('#pipboy .v046-notice').count()==3)
    page.screenshot(path=str(a.output/'01-planning-desktop.png'))
    page.set_viewport_size({'width':390,'height':844})
    check('no document-wide mobile overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
    page.screenshot(path=str(a.output/'02-planning-mobile.png'));page.set_viewport_size({'width':1280,'height':800})
    page.evaluate('__PH_QA.setup()')
    before=page.evaluate('JSON.stringify(__MISTRAL_DEBUG.getState().v060Council)')
    def topic():
        page.evaluate('__PH_QA.talk()')
        page.locator('#dialogueChoices button').filter(has_text='Pharmacies de Garde').click()
    def choose(text):
        print('CLICK',text,flush=True)
        page.locator('#dialogueChoices button').filter(has_text=text).click()
    topic();choose('Accepter la recherche');check('accepted via real dialogue button',page.evaluate('__MISTRAL_DEBUG.v062PharmacyInfo().ledger.stage')=='announced')
    choose('Revenir.');near=page.evaluate('__PH_QA.nearStand()')
    check('cabinet does not occlude interaction',near['visible'] and near['id'].startswith('pharmacy62:'))
    page.keyboard.press('e');check('E opens actual timetable note','PHARMACIES DE GARDE' in page.locator('#dialogue').inner_text())
    choose('Fermer le document')
    page.evaluate("__PH_QA.relay('v042-marseille-caravan-01',8)")
    topic();choose('Vérifier le planning');check('mismatched shift gives persistent supplier',page.evaluate('__MISTRAL_DEBUG.v062PharmacyInfo().ledger.supplier')=='gare')
    choose('Revenir.');page.evaluate("__PH_QA.relay('v042-marseille-caravan-02',3)")
    check('closed pharmacy refuses ordinary purchase',not page.evaluate('__PH_QA.closed()'))
    check('reserved parcel visible at closed office',page.evaluate('__MISTRAL_DEBUG.v062PharmacyInfo().draws')==6)
    page.evaluate("""(()=>{let e=document.createElement('div');e.textContent='BANC SYNTHÉTIQUE • MOTEUR RÉEL • HORS CARTE IGN';e.style='position:fixed;z-index:999999;left:18px;top:18px;background:#161b21;color:white;padding:12px;font:14px monospace;pointer-events:none';document.body.appendChild(e)})()""")
    page.evaluate('__PH_QA.render()');page.screenshot(path=str(a.output/'03-lot-reserve.png'))
    prior=page.evaluate('__MISTRAL_DEBUG.getState().inventory.scrap')
    topic();choose('Réparer le coffret');check('reserved pickup works outside duty hours',page.evaluate('__MISTRAL_DEBUG.v062PharmacyInfo().ledger.stage')=='carrying')
    check('actual repair cost deducted',page.evaluate('__MISTRAL_DEBUG.getState().inventory.scrap')==prior-2)
    choose('Revenir.');check('parcel disappears after pickup',page.evaluate('__PH_QA.render().draws')==5)
    page.screenshot(path=str(a.output/'04-lot-retire.png'))
    page.evaluate("__PH_QA.relay('v042-marseille-settlement-02',8)");topic();choose('Réserve mutualiste')
    check('mutual outcome grants exactly three care credits',page.evaluate('__MISTRAL_DEBUG.v062PharmacyInfo().ledger.care')==3)
    check('historical ratification untouched',page.evaluate('JSON.stringify(__MISTRAL_DEBUG.getState().v060Council)')==before)
    choose('Revenir.');page.evaluate("__PH_QA.relay('v042-marseille-caravan-01',8)");topic()
    money=page.evaluate('__MISTRAL_DEBUG.getState().player.caps')
    choose('Acheter Stimpak');choose('Acheter Stimpak')
    check('two purchases deplete real finite stock',page.evaluate('__MISTRAL_DEBUG.v062PharmacyInfo().ledger.stock.port.stimpak')==0)
    check('real purchase cost paid twice',page.evaluate('__MISTRAL_DEBUG.getState().player.caps')==money-50)
    check('exhausted purchase button removed',page.locator('#dialogueChoices button').filter(has_text='Acheter Stimpak').count()==0)
    page.evaluate('__PH_QA.hurt()');choose('Prise en charge')
    s=page.evaluate('__MISTRAL_DEBUG.getState()');check('care restores 30 HP only',s['player']['hp']==80 and s['player']['rad']==19 and s['status']['infection']==7)
    restored=page.evaluate('__PH_QA.reload()')
    check('save reload preserves spent stock and care',restored['ledger']['stock']['port']['stimpak']==0 and restored['ledger']['care']==2)
    check('no runtime JavaScript exceptions',not errors)
    render=page.evaluate('__PH_QA.render()');page.screenshot(path=str(a.output/'05-comptoir-de-garde.png'))
    report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'renderer':render['engine'],'scope':'Instrumented production bundle; isolated memory storage; flat synthetic relays; terrain stub; real UI, E interaction, NPC choices, inventory, save migration and renderer. No IGN-world traversal or human playtest.'}
    (a.output/'PHARMACIE_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));browser.close()
