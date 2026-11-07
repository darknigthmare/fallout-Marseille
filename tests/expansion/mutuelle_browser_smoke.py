"""Instrumented Mutuelle smoke on production HTML. Real authored interior/UI/save.
The completed Radieuse prerequisite is constructed by its real pure model.
Isolated storage, scripted placement and software rendering; not an IGN playtest.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--html',type=Path,default=root/'index.html');p.add_argument('--output',type=Path,default=root/'verification/mutuelle/browser');p.add_argument('--chromium',default=shutil.which('chromium'));a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__M64_QA={
 enter(roof='lots'){
  closePipboy();debugDismissDialogue();debugRenderPaused=true;updatePlayer=()=>{};
  for(const id of['water','food','cloth','scrap','circuitry','chemicals'])state.inventory[id]=60;
  state.player.caps=200;state.player.hp=100;state.character.special.I=6;state.character.special.C=6;
  state.v063Radieuse=MistralRadieuse.fresh();state.v064Mutuelle=MistralMutuelle.fresh();
  const run=(type,id,choice)=>{const point=['accept','finish'].includes(type)?'josiane':['clause','vote'].includes(type)?'assemblee':id;state=MistralRadieuse.apply(state,{type,id,choice},{local:true,near:true,point});};
  run('accept');for(const id of Object.keys(MistralRadieuse.EVIDENCE))run('inspect',id);for(const p of MistralRadieuse.PEOPLE)run('hear',p.id);for(const[k,v]of Object.entries({charges:'solidarite',representation:roof,controle:'audit'}))run('clause',k,v);run('vote');for(const id of MistralRadieuse.WORKS)run('repair',id);run('finish');
  state.v042.activeInterior=MistralRadieuse.SITE.id;state.v042.returnPoint=null;V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';
  return {npcs:world.npcs.length,ready:__MISTRAL_DEBUG.v064MutuelleInfo().ready};
 },
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v064MutuelleInfo().points[id];state.player.pos=id==='syndic'?[p[0]-2,p[1]+1.65,p[2]+1]:[p[0],p[1]+1.65,p[2]+2];state.player.yaw=Math.atan2(p[0]-state.player.pos[0],state.player.pos[2]-(p[2]+.65));state.player.pitch=-.2;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.65])};},
 state(){return {ledger:state.v064Mutuelle,caps:state.player.caps,inv:state.inventory,old:JSON.stringify([state.v063Radieuse,state.v060Council,state.v061Poste,state.v062Pharmacy]),gift:world.staticDraws.filter(d=>d.v064Gift&&!d.hidden).length,colliders:world.colliders.filter(d=>d.v064Gift&&!d.disabled).length};},
 snapshot(){return JSON.stringify(state);},
 restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';return this.state();},
 reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 failSave(type,id){const old=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v064MutuelleAction(type,id);}finally{saveGame=save;}return {result,same:old===JSON.stringify(state)};},
 remember(){globalThis.__M64_STALE=dialogueState.choices.find(c=>c.text.includes('Confirmer')).onChoose;},
 stale(){const before=JSON.stringify(state);globalThis.__M64_STALE();return before===JSON.stringify(state);},
 render(kind='expert'){for(const id of['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');mode='PLAYING';const c=kind==='expert'?{pos:[7,2.5,27],target:[4.5,1,21]}:{pos:[9.5,5,-7],target:[9.5,3.6,-11]};const cam={pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:57};sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),cam,currentEnv());return renderer.constructor.name;},
 cycle(){for(let i=0;i<10;i++)collectDraws(gameClock);return {npcs:world.npcs.filter(n=>n.id==='m64:expert').length,it:world.interactables.filter(i=>i.id==='m64:colis').length};}
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralMutuelle' in html
html=html.replace(marker,bridge+'\n'+marker);checks=[];errors=[]
def check(name,ok):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(8000);page.on('pageerror',lambda e:(errors.append(e.stack),print(e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v064MutuelleInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2500)
  page.evaluate('__MISTRAL_DEBUG.v064MutuelleOpen()');check('locked before completion of Radieuse','réceptionner' in page.locator('#pipboy').inner_text())
  page.screenshot(path=str(a.output/'01-carnet-desktop.png'));page.set_viewport_size({'width':390,'height':844});check('mobile no page-wide overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-carnet-mobile.png'));page.set_viewport_size({'width':1280,'height':800})
  result=page.evaluate('__M64_QA.enter()');check('actual completed interior gets one new expert',result['npcs']==6 and result['ready']);old=page.evaluate('__M64_QA.state().old')
  def choose(text):
   print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected):
   info=page.evaluate('(id)=>__M64_QA.near(id)',id);print(id,info,flush=True);check('reachable interaction '+id,info['selected']==expected and not info['collision'] and info['los']);page.keyboard.press('e')
  go('expert','npc:m64:expert');choose('Ouvrir');check('claim accepted through the expert dialogue',page.evaluate('__M64_QA.state().ledger.opened'));choose('Revenir.')
  page.evaluate('__M64_QA.render()');page.screenshot(path=str(a.output/'03-experte-hall.png'))
  for point,name in [('registre','avenant'),('pompe','manchon'),('toit','annexe'),('syndic','refus automatique')]:
   go(point,'r63:'+point);choose('Mutuelle ·');choose('Verser cette pièce');choose('Revenir.')
  check('four source copies kept separately',page.evaluate('__M64_QA.state().ledger.evidence.length')==4)
  go('pompe','r63:pompe');check('original water withdrawal still available',page.locator('#dialogueChoices button').filter(has_text='Retirer 2 eaux').count()==1);choose('Revenir.')
  go('expert','npc:m64:expert');cloth=page.evaluate('__M64_QA.state().inv.cloth');choose('contre-expertise contradictoire');check('actual material cost applied once',page.evaluate('__M64_QA.state().inv.cloth')==cloth-2)
  checkpoint=page.evaluate('__M64_QA.snapshot()');choose('Examiner : Avenant de présence');check('irreversible decision requires a confirmation',page.locator('#dialogueChoices button').filter(has_text='Confirmer').count()==1)
  check('roof exclusion remains visible before inclusive settlement','exclu du vote' in page.locator('#dialogueLine').inner_text());page.screenshot(path=str(a.output/'04-accord-et-exclusion.png'))
  page.evaluate('__M64_QA.remember()');failed=page.evaluate('__M64_QA.failSave("settle","avenant")');check('save failure cancels costs outcome and caps',not failed['result'] and failed['same']);choose('Confirmer');check('accepted settlement stored',page.evaluate('__M64_QA.state().ledger.outcome')=='avenant');check('stale confirmation cannot duplicate payment',page.evaluate('__M64_QA.stale()'));choose('Revenir.')
  check('physical finite gift appears with collision',page.evaluate('__M64_QA.state().gift')==2 and page.evaluate('__M64_QA.state().colliders')==1)
  page.evaluate('__M64_QA.render("gift")');page.screenshot(path=str(a.output/'05-colis-disponible.png'))
  before=page.evaluate('__M64_QA.state().inv');go('colis','m64:colis');after=page.evaluate('__M64_QA.state()');check('E collects actual contents',after['inv']['cloth']==before['cloth']+2 and after['inv']['circuitry']==before['circuitry']+1)
  check('colis and blocking collider disappear after withdrawal',after['gift']==0 and after['colliders']==0);page.evaluate('__M64_QA.render("gift")');page.screenshot(path=str(a.output/'06-colis-retire.png'))
  go('josiane','npc:r63:josiane');choose('Mutuelle · remettre');check('receipt given once',page.evaluate('__M64_QA.state().ledger.reported'));choose('Revenir.')
  check('entire old vote works and other registers preserved',page.evaluate('__M64_QA.state().old')==old)
  loaded=page.evaluate('__M64_QA.reload()');check('save reload preserves settlement withdrawal and receipt',loaded['ledger']['reported'] and loaded['ledger']['claimed'] and loaded['ledger']['outcome']=='avenant')
  page.evaluate('__M64_QA.near("colis")');check('repeat claim refused after reload',not page.evaluate('__MISTRAL_DEBUG.v064MutuelleAction("claim")'))
  cycle=page.evaluate('__M64_QA.cycle()');check('render and reload never duplicate actors or interactions',cycle=={'npcs':1,'it':1})
  for outcome,label,gift in [('forfait','Quittance des lots inscrits',{'scrap':3}),('entraide','Entraide sans quittance',{'stimpak':1,'scrap':2})]:
   page.evaluate('(raw)=>__M64_QA.restore(raw)',checkpoint);go('expert','npc:m64:expert');choose('Examiner : '+label);choose('Confirmer');choose('Revenir.');before=page.evaluate('__M64_QA.state().inv');go('colis','m64:colis');after=page.evaluate('__M64_QA.state()');check(outcome+' complete alternate physical outcome',after['ledger']['outcome']==outcome and all(after['inv'].get(k,0)==before.get(k,0)+v for k,v in gift.items()));check(outcome+' leaves prior vote unchanged',after['old']==old)
  check('no JavaScript exception',not errors)
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Real authored Radieuse interior with completed prerequisite injected through its model; actual E interaction, NPC choices, source preservation, save writes and reload. Scripted positioning and isolated MemoryStorage; software renderer, no real IGN traversal.'}
  (a.output/'MUTUELLE_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('FAILURE STATE',page.evaluate('window.__M64_QA?.state()'),flush=True);raise
 finally:browser.close()
