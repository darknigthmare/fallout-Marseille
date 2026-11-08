"""Instrumented Compagnons smoke on the actual bundled game and authored Radieuse.
Prerequisites run through their real reducers. Isolated MemoryStorage, scripted
positions and native collision calls; software renderer, not a human playthrough.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/compagnons/browser')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__D67_QA={
 close(){closePipboy();},
 setup(done=true){
  closePipboy();debugDismissDialogue();debugRenderPaused=true;updatePlayer=()=>{};
  for(const id of ['water','food','cloth','scrap','circuitry','chemicals'])state.inventory[id]=60;
  state.player.caps=300;state.player.hp=100;state.character.special.I=6;state.character.special.C=6;
  state.v063Radieuse=MistralRadieuse.fresh();state.v064Mutuelle=MistralMutuelle.fresh();state.v065Notaires=MistralNotaires.fresh();state.v066Voisins=MistralVoisins.fresh();
  const ra=(type,id,choice)=>{state=MistralRadieuse.apply(state,{type,id,choice},{local:true,near:true,point:['accept','finish'].includes(type)?'josiane':['vote','clause'].includes(type)?'assemblee':id});};
  ra('accept');for(const id of Object.keys(MistralRadieuse.EVIDENCE))ra('inspect',id);for(const p of MistralRadieuse.PEOPLE)ra('hear',p.id);for(const [k,v]of Object.entries({charges:'solidarite',representation:'lots',controle:'audit'}))ra('clause',k,v);ra('vote');for(const id of MistralRadieuse.WORKS)ra('repair',id);ra('finish');
  const ua=(type,id)=>{state=MistralMutuelle.apply(state,{type,id},{local:true,near:true,point:type==='evidence'?MistralMutuelle.EVIDENCE[id].point:type==='report'?'josiane':'expert'});};
  ua('open');for(const id of MistralMutuelle.IDS)ua('evidence',id);ua('argue','copies');ua('settle','forfait');ua('report');
  const na=(type,id,value)=>{state=MistralNotaires.apply(state,{type,id,value},{local:true,near:true,point:type==='read'?MistralNotaires.READINGS[id].point:['witness','notify'].includes(type)?id:['dial','unseal','collect'].includes(type)?'vault':'notaire'});};
  na('open');for(const id of Object.keys(MistralNotaires.READINGS))na('read',id);na('witness','josiane');na('witness','salome');for(const [i,v]of ['76','48','86'].entries())na('dial',i,v);na('unseal','sequence');na('collect');na('decide','usage');na('notify','josiane');na('notify','salome');na('close');
  const va=(type,id,value)=>{state=MistralVoisins.apply(state,{type,id,value},{local:true,near:true,point:['open','start','finish'].includes(type)?'josiane':type==='meal'?'buffet':['notice','sound'].includes(type)?'console':id});};
  va('open');for(const id of MistralVoisins.GUESTS)va('listen',id);va('meal','placard');for(const id of MistralVoisins.PANTRY)va('collect',id);va('sound','silence');va('start','paliers');for(const id of MistralVoisins.GUESTS)va('serve',id);va('answer','karim','comptes');va('answer','salome','reserves');if(done)va('finish');
  state.v067Devoir=MistralDevoir.fresh();state.inventory.chemicals=20;state.inventory.clay=20;
  state.v042.activeInterior=MistralRadieuse.SITE.id;state.v042.returnPoint=null;V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';return this.info();
 }, near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v067DevoirInfo().points[id];state.player.pos=[p[0],p[1]+1.65,p[2]+2];const target=[p[0],p[1]+(id==='cadran'?1.75:1.1),p[2]+(id==='montage'?1.05:.7)];state.player.yaw=0;state.player.pitch=Math.atan2(target[1]-state.player.pos[1],state.player.pos[2]-target[2]);onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,target)};},
 relay(id){debugDismissDialogue();const site=v042Site(MistralDevoir.SITES[id]);world=createWorld(site.macro,'Relais synthétique · Compagnons','BANC DE TEST, PAS LA CARTE IGN',{skyTop:[78,121,146],skyBottom:[191,181,139]});world.v046=true;world.geoMacro=true;world.v046Records=new Map();world.geoTiles=new Map();world.v047TerrainBank={read:()=>({height:0}),grids:new Map()};world.v046ChunkDraws=[];world.v047TerrainDraws=[];v049Own(world);V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;onGround=true;settings.geoFalloutLayer=true;v050TravelGround=()=>0;state.player.zone=site.macro;state.player.pos=[0,1.65,2];state.player.yaw=0;state.player.pitch=-.15;state.v042.activeInterior=null;state.v042.discovered[site.id]=true;V042_RUNTIME.active.clear();V042_RUNTIME.active.set(site.id,{site,pos:[0,0,0]});V042_RUNTIME.npcData.clear();const nid='v042-npc:qa:devoir';V042_RUNTIME.npcData.set(nid,{siteId:site.id,name:'Correspondant de test',role:'artisan',index:0});const n=addHumanNPC(world,nid,'Correspondant de test','Artisan',[0,0,0]);n.v042Site=site.id;addBox(world,[0,-.1,0],[32,.2,32],[.43,.40,.31]);mode='PLAYING';gameStarted=true;updateSelectedInteractable();return {id:selectedInteractable?.id,site:site.id,contacts:__MISTRAL_DEBUG.v067DevoirInfo().contacts};},
 inside(){debugDismissDialogue();state.v042.activeInterior=MistralRadieuse.SITE.id;loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';return this.info();},
 info(){__MISTRAL_DEBUG.v067DevoirInfo();return {ledger:state.v067Devoir,inv:state.inventory,caps:state.player.caps,old:JSON.stringify([state.v063Radieuse,state.v064Mutuelle,state.v065Notaires,state.v066Voisins,state.v060Council,state.v061Poste,state.v062Pharmacy]),parts:world.staticDraws.filter(d=>['bati','cartouche','clapet'].includes(d.v067Role)&&!d.hidden).map(d=>d.v067Role),props:world.staticDraws.filter(d=>d.v067Devoir).length,interactions:world.interactables.filter(i=>i.v067Devoir).length,plans:world.staticDraws.filter(d=>d.v067Role?.startsWith('plan:')&&!d.hidden).length,needle:world.staticDraws.find(d=>d.v067Role==='needle')?.pos[0],error:__MISTRAL_DEBUG.v067DevoirInfo().error};},
 snapshot(){return JSON.stringify(state);},restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));return this.inside();},reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 fail(type,id,value,answer){const before=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v067DevoirAction(type,id,value,answer);}finally{saveGame=save;}return {result,same:JSON.stringify(state)===before};},
 remember(){globalThis.__D67_STALE=dialogueState.choices.find(c=>c.text.includes('Confirmer')).onChoose;},stale(){const before=JSON.stringify(state);globalThis.__D67_STALE();return before===JSON.stringify(state);},repeat(){for(let i=0;i<15;i++)collectDraws(gameClock);return this.info();},
 walk(points){mode='PLAYING';state.player.pos=points[0].slice();const visited=[];for(let i=1;i<points.length;i++){const t=points[i],ox=state.player.pos[0],oz=state.player.pos[2],steps=Math.ceil(Math.hypot(t[0]-ox,t[2]-oz)/.12);for(let j=0;j<steps;j++){tryPlayerMove((t[0]-ox)/steps,(t[2]-oz)/steps);state.player.pos[1]=groundHeightAt(state.player.pos[0],state.player.pos[2],state.player.pos[1]-1.65)+1.65;}visited.push(state.player.pos.slice());}return visited;},
 render(){for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');mode='PLAYING';const pos=[-13.7,3.1,5.8],target=[-18,1.4,3.5];sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos,dir:vNorm(vSub(target,pos)),fov:58},currentEnv());return renderer.constructor.name;}
};

'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralDevoir' in html
html=html.replace(marker,bridge+'\n'+marker);checks=[];errors=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(8000)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v067DevoirInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2300)
  locked=page.evaluate('__D67_QA.setup(false)');check('no workshop before completion of the party',locked['props']==0)
  start=page.evaluate('__D67_QA.setup(true)');old=start['old'];check('authored bench created once without new residents',start['props']>0 and start['interactions']==4)
  page.evaluate('__MISTRAL_DEBUG.v067DevoirOpen()');check('dedicated Pip-Boy and both relay names visible','Aubagne' in page.locator('#pipboy').inner_text() and 'Ciotat' in page.locator('#pipboy').inner_text())
  page.screenshot(path=str(a.output/'01-carnet-desktop.png'));page.set_viewport_size({'width':390,'height':844});check('390px viewport has no global horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-carnet-mobile.png'));page.set_viewport_size({'width':1280,'height':800});page.evaluate('__D67_QA.close()')
  def choose(text):
   print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected):
   pos=page.evaluate('(id)=>__D67_QA.near(id)',id);print('NEAR',id,pos,flush=True);check('physical E contact '+id,pos['selected']==expected and not pos['collision'] and pos['los']);page.keyboard.press('e')
  def lucie():
   go('lucie','npc:r63:lucie');choose('Compagnons du Devoir ·')
  def relay(id):
   result=page.evaluate('(id)=>__D67_QA.relay(id)',id);check('correct occupied relay '+id,result['contacts'][id] and result['id']=='npc:v042-npc:qa:devoir');page.keyboard.press('e');check('ordinary relay conversation remains reachable',page.locator('#dialogueChoices button').filter(has_text='Parler du secteur').count()==1);choose('Compagnons du Devoir ·')
  lucie();choose('Commencer');check('quest accepted through real dialogue',page.evaluate('__D67_QA.info().ledger.opened'));choose('Revenir.');opened=page.evaluate('__D67_QA.snapshot()')
  page.evaluate('__D67_QA.render()');page.screenshot(path=str(a.output/'03-banc-avant-montage.png'))
  for id,wrong,right in [('ciotat','Clapet A','Clapet C'),('aubagne','Cartouche rouge','Cartouche bleue')]:
   relay(id);choose('Écouter la leçon');before=page.evaluate('__D67_QA.info()');choose('Essai : '+wrong);check('wrong apprenticeship sample consumes nothing '+id,page.evaluate('__D67_QA.info()')==before);choose('Essai : '+right);check('part obtained once without saleable duplicate '+id,page.evaluate(f'__D67_QA.info().ledger.lessons.{id}.method')=='apprentissage');choose('Revenir.')
  check('history unchanged by two external relay visits',page.evaluate('__D67_QA.info().old')==old)
  page.evaluate('__D67_QA.inside()');p=page.evaluate('(p)=>__D67_QA.walk(p)',[[0,1.65,25],[-10,1.65,25],[-10,1.65,12],[-5,1.65,10],[-5,1.65,0],[-14,1.65,0],[-14,1.65,5.5],[-18,1.65,5.5]]);print('PATH',p,flush=True);check('workshop remains accessible with native collision',abs(p[-1][0]+18)<.3 and abs(p[-1][2]-5.5)<.3)
  go('montage','d67:montage');choose('Monter : bâti');choose('Monter : cartouche');choose('Monter : clapet');choose('Revenir.');check('all three components actually visible',len(page.evaluate('__D67_QA.info().parts'))==3)
  go('cadran','d67:cadran');choose('Lire la notice');before=page.evaluate('__D67_QA.info()');choose('Éprouver à charge');check('unsafe order blocked without supply or state change',page.evaluate('__D67_QA.info()')==before);choose('Revenir.');built=page.evaluate('__D67_QA.snapshot()')
  go('entree','d67:entree');choose('entree : ouverte');choose('Revenir.');go('cadran','d67:cadran');choose('Amorcer');check('priming moves the physical indicator',page.evaluate('__D67_QA.info().needle')==-18);choose('Revenir.');go('retour','d67:retour');choose('retour : ferme');choose('Revenir.')
  go('cadran','d67:cadran');choose('Éprouver à charge');check('limited test distinct from validation',page.evaluate('__D67_QA.info().ledger.pressure')==2 and not page.evaluate('__D67_QA.info().ledger.tested'));choose('Revenir.');reloaded=page.evaluate('__D67_QA.reload()');check('load preserves in-progress pressure and acquired parts',reloaded['ledger']['pressure']==2 and len(reloaded['parts'])==3)
  go('cadran','d67:cadran');choose('Relever la graduation');choose('Revenir.');go('retour','d67:retour');failure=page.evaluate('__D67_QA.fail("switch","retour","ouvert")');check('save failure does not commit test or move gauge',not failure['result'] and failure['same'] and page.evaluate('__D67_QA.info().ledger.pressure')==2);choose('retour : ouvert');choose('Revenir.');check('release validates assay and closes supply',page.evaluate('__D67_QA.info().ledger.tested') and page.evaluate('__D67_QA.info().ledger.controls.entree')=='fermee')
  page.evaluate('__D67_QA.render()');page.screenshot(path=str(a.output/'04-ouvrage-eprouve.png'));tested=page.evaluate('__D67_QA.snapshot()')
  lucie();choose('Examiner : Plans partagés');check('confirmation states shared finite stock and limits','trois doses' in page.locator('#dialogueLine').inner_text() and 'radiation' in page.locator('#dialogueLine').inner_text());page.screenshot(path=str(a.output/'05-transmission-confirmee.png'));page.evaluate('__D67_QA.remember()');caps=page.evaluate('__D67_QA.info().caps');choose('Confirmer la transmission');check('one-time forty-five caps and shared plan',page.evaluate('__D67_QA.info().caps')==caps+45 and page.evaluate('__D67_QA.info().ledger.plan')=='partage');check('stale confirmation cannot repeat the reward',page.evaluate('__D67_QA.stale()'));choose('Revenir.');check('two physical plan copies appear',page.evaluate('__D67_QA.info().plans')==2)
  for id in ['aubagne','ciotat']:
   relay(id);before=page.evaluate('__D67_QA.info()');choose('Préparer un mastic');after=page.evaluate('__D67_QA.info()');check('real finite recipe at '+id,after['inv']['chemicals']==before['inv']['chemicals']-1 and after['inv']['cloth']==before['inv']['cloth']-1 and after['inv']['sealant']==before['inv'].get('sealant',0)+1 and after['ledger']['remaining']==before['ledger']['remaining']-1);choose('Revenir.')
  page.evaluate('__D67_QA.inside()');lucie();choose('Préparer un mastic');choose('Revenir.');check('all three sites consume a single three-dose reserve',page.evaluate('__D67_QA.info().ledger.remaining')==0);saved=page.evaluate('__D67_QA.reload()');check('exhaustion survives save reload',saved['ledger']['remaining']==0 and saved['ledger']['produced']==3);lucie();check('exhausted recipe removed from dialogue',page.locator('#dialogueChoices button').filter(has_text='Préparer un mastic').count()==0);choose('Revenir.')
  check('all prior records still unchanged after crafting',page.evaluate('__D67_QA.info().old')==old);r=page.evaluate('__D67_QA.repeat()');check('no duplication on repeated rendering',r['interactions']==4 and r['props']==start['props'])
  page.evaluate('(s)=>__D67_QA.restore(s)',tested);lucie();choose('Examiner : Réserve d’atelier');choose('Confirmer la transmission');choose('Revenir.');relay('aubagne');check('workshop policy does not expose external crafting',page.locator('#dialogueChoices button').filter(has_text='Préparer un mastic').count()==0);choose('Revenir.');page.evaluate('__D67_QA.inside()');lucie()
  for _ in range(5):choose('Préparer un mastic')
  check('supervised plan has exactly five doses at Lucie',page.evaluate('__D67_QA.info().ledger.remaining')==0 and page.evaluate('__D67_QA.info().ledger.produced')==5);choose('Revenir.')
  page.evaluate('(s)=>__D67_QA.restore(s)',opened);relay('aubagne');choose('Écouter la leçon');prior=page.evaluate('__D67_QA.info().inv');choose('Échanger les fournitures');now=page.evaluate('__D67_QA.info().inv');check('exchange consumes two clay and one cloth',now['clay']==prior['clay']-2 and now['cloth']==prior['cloth']-1);choose('Revenir.');relay('ciotat');choose('Écouter la leçon');prior=page.evaluate('__D67_QA.info().inv.scrap');choose('Expertise technique');check('technical part spends one scrap',page.evaluate('__D67_QA.info().inv.scrap')==prior-1);choose('Revenir.')
  page.evaluate('(s)=>__D67_QA.restore(s)',built);go('cadran','d67:cadran');prior=page.evaluate('__D67_QA.info().inv.circuitry');choose('Contrôle technique');check('technical assay spends one circuit and returns safe controls',page.evaluate('__D67_QA.info().inv.circuitry')==prior-1 and page.evaluate('__D67_QA.info().ledger.testMethod')=='technique');choose('Revenir.')
  check('no runtime JavaScript or presentation errors',not errors and page.evaluate('__D67_QA.info().error') is None)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Real authored Radieuse, native UI/E/dialogues, models, finite inventory, save/load and collision. Earlier quests prepared through original reducers; scripted positions; external relay fixtures use existing catalogue identities and flat synthetic ground, not IGN traversal. Isolated MemoryStorage, software renderer, not a full human campaign.'}
  (a.output/'COMPAGNONS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',page.evaluate('window.__D67_QA?.info()'),flush=True);raise
 finally:browser.close()
