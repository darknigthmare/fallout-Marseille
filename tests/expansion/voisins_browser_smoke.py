"""Instrumented fete smoke on the actual bundled game and authored Radieuse.
Prerequisites run through their real reducers. Isolated MemoryStorage, scripted
positions and native collision calls; software renderer, not a human playthrough.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--html',type=Path,default=root/'index.html')
p.add_argument('--output',type=Path,default=root/'verification/voisins/browser')
p.add_argument('--chromium',default=shutil.which('chromium'))
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
html=a.html.read_text();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
shim="""<script>const qaStore=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaStore.get(k)??null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k),clear:()=>qaStore.clear()},configurable:true});</script>"""
bridge=r'''
globalThis.__V66_QA={
 close(){closePipboy();},
 setup(closed=true){
  closePipboy();debugDismissDialogue();debugRenderPaused=true;updatePlayer=()=>{};
  for(const id of ['water','food','cloth','scrap','circuitry','chemicals'])state.inventory[id]=60;
  state.player.caps=300;state.player.hp=100;state.character.special.I=6;state.character.special.C=6;
  state.v063Radieuse=MistralRadieuse.fresh();state.v064Mutuelle=MistralMutuelle.fresh();state.v065Notaires=MistralNotaires.fresh();state.v066Voisins=MistralVoisins.fresh();
  const ra=(type,id,choice)=>{state=MistralRadieuse.apply(state,{type,id,choice},{local:true,near:true,point:['accept','finish'].includes(type)?'josiane':['vote','clause'].includes(type)?'assemblee':id});};
  ra('accept');for(const id of Object.keys(MistralRadieuse.EVIDENCE))ra('inspect',id);for(const p of MistralRadieuse.PEOPLE)ra('hear',p.id);for(const [k,v]of Object.entries({charges:'solidarite',representation:'lots',controle:'audit'}))ra('clause',k,v);ra('vote');for(const id of MistralRadieuse.WORKS)ra('repair',id);ra('finish');
  const ua=(type,id)=>{state=MistralMutuelle.apply(state,{type,id},{local:true,near:true,point:type==='evidence'?MistralMutuelle.EVIDENCE[id].point:type==='report'?'josiane':'expert'});};
  ua('open');for(const id of MistralMutuelle.IDS)ua('evidence',id);ua('argue','copies');ua('settle','forfait');ua('report');
  const na=(type,id,value)=>{state=MistralNotaires.apply(state,{type,id,value},{local:true,near:true,point:type==='read'?MistralNotaires.READINGS[id].point:['witness','notify'].includes(type)?id:['dial','unseal','collect'].includes(type)?'vault':'notaire'});};
  na('open');for(const id of Object.keys(MistralNotaires.READINGS))na('read',id);na('witness','josiane');na('witness','salome');for(const [i,v]of ['76','48','86'].entries())na('dial',i,v);na('unseal','sequence');na('collect');na('decide','usage');na('notify','josiane');na('notify','salome');if(closed)na('close');
  state.v042.activeInterior=MistralRadieuse.SITE.id;state.v042.returnPoint=null;V046.busy=false;V047.pending=false;V046.lab=false;zoneTransitioning=false;
  loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true});onGround=true;mode='PLAYING';return this.info();
 },
 near(id){debugDismissDialogue();const p=__MISTRAL_DEBUG.v066VoisinsInfo().points[id];const staged=state.v066Voisins.started&&!state.v066Voisins.finished&&state.v066Voisins.layout==='commune';const dz=staged&&id==='salome'?-1.5:staged&&['karim','lucie'].includes(id)?1.2:2;state.player.pos=[p[0],p[1]+1.65,p[2]+dz];state.player.yaw=dz<0?Math.PI:0;state.player.pitch=-.2;onGround=true;mode='PLAYING';updateSelectedInteractable();return {selected:selectedInteractable?.id,collision:collidesAt(state.player.pos[0],state.player.pos[2],.38,state.player.pos[1]),los:lineOfSight(state.player.pos,[p[0],p[1]+1.25,p[2]+.85])};},
 info(){__MISTRAL_DEBUG.v066VoisinsInfo();return {ledger:state.v066Voisins,caps:state.player.caps,inv:state.inventory,old:JSON.stringify([state.v063Radieuse,state.v064Mutuelle,state.v065Notaires,state.v060Council,state.v061Poste,state.v062Pharmacy]),props:world.staticDraws.filter(d=>d.v066Voisins).length,food:world.staticDraws.filter(d=>d.v066Role?.startsWith('food:')&&!d.hidden).length,pennants:world.staticDraws.filter(d=>d.v066Role==='bunting'&&!d.hidden).length,staged:world.npcs.filter(n=>n.v066Staged).map(n=>n.id),npcs:world.npcs.filter(n=>n.id.startsWith('r63:')).map(n=>({id:n.id,pos:n.pos.slice()})),extras:world.interactables.filter(i=>i.v066Voisins).length,error:__MISTRAL_DEBUG.v066VoisinsInfo().error};},
 snapshot(){return JSON.stringify(state);},
 restore(raw){debugDismissDialogue();state=migrateState(JSON.parse(raw));loadZone(V042_INSTANCE_ZONE,{force:true,instance:true,noTravel:true,silent:true,spawn:state.player.pos.slice()});onGround=true;mode='PLAYING';return this.info();},
 reload(){return this.restore(localStorage.getItem(SAVE_KEY));},
 fail(type,id,value){const original=JSON.stringify(state),save=saveGame;saveGame=()=>false;let result;try{result=__MISTRAL_DEBUG.v066VoisinsAction(type,id,value);}finally{saveGame=save;}return {result,same:original===JSON.stringify(state)};},
 remember(){globalThis.__V66_STALE=dialogueState.choices.find(c=>c.text.includes('Confirmer')).onChoose;},
 stale(){const before=JSON.stringify(state);globalThis.__V66_STALE();return before===JSON.stringify(state);},
 walk(points){mode='PLAYING';let visited=[];state.player.pos=points[0].slice();for(let i=1;i<points.length;i++){const t=points[i],ox=state.player.pos[0],oz=state.player.pos[2],steps=Math.ceil(Math.hypot(t[0]-ox,t[2]-oz)/.12);for(let j=0;j<steps;j++){tryPlayerMove((t[0]-ox)/steps,(t[2]-oz)/steps);state.player.pos[1]=groundHeightAt(state.player.pos[0],state.player.pos[2],state.player.pos[1]-1.65)+1.65;}visited.push(state.player.pos.slice());}return visited;},
 portals(){
  debugDismissDialogue();mode='PLAYING';const site=MistralRadieuse.SITE;
  world=createWorld('geo_marseille','Extérieur synthétique de test','PAS LA CARTE IGN');world.geoMacro=true;world.v046=true;world.v046Anchor=[0,0,0];world.v046Records=new Map();world.geoTiles=new Map();world.v046ChunkDraws=[];world.v047TerrainDraws=[];world.bounds=[-30,30,-30,30];world.v047TerrainBank={read:()=>({height:0}),grids:new Map()};
  V046.terrain=world.v047TerrainBank;V046.readyAnchor=[0,0,0];V046.busy=false;V047.pending=false;zoneTransitioning=false;v049Own(world);state.player.zone=world.id;state.player.pos=[0,1.65,3];state.player.yaw=0;state.player.pitch=0;state.v042.activeInterior=null;
  V042_RUNTIME.active.clear();V042_RUNTIME.npcData.clear();V042_RUNTIME.worldId=world.id;V042_RUNTIME.nearest=null;v042Entrance(world,[0,0,0],site);
  const exterior=world,door=world.interactables.find(i=>i.id==='v042-enter-'+site.id),entered=door.onInteract();const first=this.info();state.player.pos=[0,1.65,26];onGround=true;const exited=world.interactables.find(i=>i.id==='r63:exit').onInteract(),retained=world===exterior;
  state.player.pos=[0,1.65,3];const returned=door.onInteract();return {entered,exited,retained,returned,first,second:this.info()};
 },
 repeat(){for(let i=0;i<20;i++)collectDraws(gameClock);return this.info();},
 render(which='table'){
  for(const id of ['dialogue','noteScreen','pipboy','menuScreen','bootScreen']){const e=document.getElementById(id);if(e){e.classList.remove('active');e.classList.add('hidden');}}
  document.getElementById('questFlash').style.display='none';document.getElementById('toastStack')?.replaceChildren();document.getElementById('interactPrompt').classList.add('hidden');mode='PLAYING';
  const c=which==='table'?{pos:[-11,9.6,-23],target:[-1,7.8,-26]}:which==='console'?{pos:[12,8.6,-22.8],target:[18,7.7,-27]}:{pos:[-15,2.4,3.5],target:[-21,1.2,-2]};
  sky?.draw(currentEnv(),performance.now());renderer.render(collectDraws(gameClock),{pos:c.pos,dir:vNorm(vSub(c.target,c.pos)),fov:62},currentEnv());return renderer.constructor.name;
 }
};
'''
marker='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
assert html.count(marker)==1 and 'const MistralVoisins' in html
html=html.replace(marker,bridge+'\n'+marker);checks=[];errors=[]
def check(name,ok):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=a.chromium,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(7000)
 page.on('pageerror',lambda e:(errors.append(e.stack),print('JS ERROR',e.stack,flush=True)))
 try:
  page.set_content(shim+html,wait_until='load');page.wait_for_function('!!window.__MISTRAL_DEBUG?.v066VoisinsInfo');page.evaluate('__MISTRAL_DEBUG.startStory()');page.wait_for_timeout(2200)
  locked=page.evaluate('__V66_QA.setup(false)');check('no festive props before notarial closure',locked['props']==0)
  start=page.evaluate('__V66_QA.setup(true)');old=start['old'];homes=start['npcs'];check('local props created once without extra people',start['props']>40 and len(start['npcs'])==5 and not start['staged'])
  page.evaluate('__MISTRAL_DEBUG.v066VoisinsOpen()');check('Pip-Boy fête chapter accessible','La fête des voisins' in page.locator('#pipboy').inner_text());page.screenshot(path=str(a.output/'01-carnet-desktop.png'))
  page.set_viewport_size({'width':390,'height':844});check('390px viewport no global horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));page.screenshot(path=str(a.output/'02-carnet-mobile.png'));page.set_viewport_size({'width':1280,'height':800});page.evaluate('__V66_QA.close()')
  def choose(text):
   print('CLICK',text,flush=True);page.locator('#dialogueChoices button').filter(has_text=text).click()
  def go(id,expected):
   data=page.evaluate('(id)=>__V66_QA.near(id)',id);print('NEAR',id,data,flush=True);check('E contact '+id,data['selected']==expected and not data['collision'] and data['los']);page.keyboard.press('e')
  def guest(id):
   go(id,'npc:r63:'+id)
   if page.locator('#dialogueChoices button').filter(has_text='Fête des voisins ·').count():choose('Fête des voisins ·')
  guest('josiane');choose('Préparer «');choose('Revenir.');check('opened by real dialogue',page.evaluate('__V66_QA.info().ledger.opened'))
  for who in ['karim','lucie','nadia','salome']:
   guest(who);choose('Écouter ses conditions');choose('Revenir.')
  invited=page.evaluate('__V66_QA.snapshot()')
  go('buffet','v66:buffet');choose('Utiliser le lot festif');choose('Revenir.')
  for id in ['rations','vaisselle']:
   go(id,'v66:'+id);choose('Prendre ce lot');choose('Revenir.')
  check('pantry route does not mint inventory or deplete older stocks',page.evaluate('__V66_QA.info().inv')==start['inv'] and page.evaluate('__V66_QA.info().old')==old)
  go('console','v66:console');choose('Lire la notice');choose('Revenir.')
  go('console','v66:console');before=page.evaluate('__V66_QA.info()');choose('Tester les trois réglages');check('unsafe audio test aborts without modifying registry or scene',page.evaluate('__V66_QA.info()')==before);choose('Revenir.')
  for id,text in [('source','Choisir : Micro'),('sortie','Choisir : Haut-parleurs'),('niveau','Choisir : Limiteur')]:
   go(id,'v66:'+id);choose(text);choose('Revenir.')
  go('console','v66:console');choose('Tester les trois réglages');choose('Revenir.');check('manual physical wiring secures only local limited audio',page.evaluate('__V66_QA.info().ledger.sound')=='limitee')
  page.evaluate('__V66_QA.render("console")');page.screenshot(path=str(a.output/'03-sonorisation.png'))
  prepared=page.evaluate('__V66_QA.snapshot()')
  # Collision route visits upper level without crossing the table footprint.
  path=[[0,1.65,25],[18,1.65,24],[18,1.65,9],[0,4.85,0],[-18,4.85,-8],[-18,4.85,-24],[10,8.05,-24],[10,8.05,-28]]
  walked=page.evaluate('(p)=>__V66_QA.walk(p)',path);print('WALK',walked,flush=True);check('stairs and terrace path remain physically traversable',abs(walked[-1][0]-10)<.3 and abs(walked[-1][1]-8.05)<.2 and abs(walked[-1][2]+28)<.3)
  guest('josiane');choose('Prévoir : Une table commune');check('setup confirmation does not conceal old roof exclusion','exclu du vote' in page.locator('#dialogueLine').inner_text());page.evaluate('__V66_QA.remember()')
  failed=page.evaluate('__V66_QA.fail("start","commune")');check('failed save does not move people or freeze service',not failed['result'] and failed['same'] and not page.evaluate('__V66_QA.info().staged'))
  choose('Confirmer la mise en place');check('same five actors staged on terrace, not duplicated',len(page.evaluate('__V66_QA.info().staged'))==5 and len(page.evaluate('__V66_QA.info().npcs'))==5)
  check('stale setup confirmation cannot replay action',page.evaluate('__V66_QA.stale()'))
  check('four portions and pennants visible on shared table',page.evaluate('__V66_QA.info().food')==4 and page.evaluate('__V66_QA.info().pennants')==11)
  page.evaluate('__V66_QA.render()');page.screenshot(path=str(a.output/'04-table-et-voisins.png'))
  guest('karim');choose('Servir sa portion');choose('Rendre l’origine');choose('Revenir.')
  check('one physical dish removed and answer preserved',page.evaluate('__V66_QA.info().food')==3 and page.evaluate('__V66_QA.info().ledger.answers.karim')=='comptes')
  restored=page.evaluate('__V66_QA.reload()');check('mid-service reload restores staging, portion and answer',len(restored['staged'])==5 and restored['food']==3 and restored['ledger']['answers']['karim']=='comptes')
  trip=page.evaluate('__V66_QA.portals()');check('native portal round-trip during service preserves portions and staging',trip['entered'] and trip['exited'] and trip['retained'] and trip['returned'] and len(trip['second']['staged'])==5 and trip['second']['ledger']['served']==['karim'] and trip['second']['old']==old)
  for who in ['lucie','nadia','salome']:
   guest(who);choose('Servir sa portion')
   if who=='salome':
    check('Salomé still recalls her old exclusion','exclu du vote' in page.locator('#dialogueLine').inner_text());choose('Dire publiquement');page.screenshot(path=str(a.output/'05-salome-et-reserves.png'))
   choose('Revenir.')
  guest('josiane');caps=page.evaluate('__V66_QA.info().caps');choose('Terminer la soirée')
  final=page.evaluate('__V66_QA.info()');check('shared-table outcome and exact one-time thirty capsules',final['ledger']['outcome']=='table_ouverte' and final['caps']==caps+30)
  check('actors restored to their original positions without old ledger edits',final['npcs']==homes and final['old']==old and not final['staged'])
  guest('josiane');choose('Revenir.')
  go('josiane','npc:r63:josiane');check('old Notaires and Mutuelle dialogue topics restored',page.locator('#dialogueChoices button').filter(has_text='Notaires ·').count()==1 and page.locator('#dialogueChoices button').filter(has_text='Mutuelle ·').count()==1);choose('Revenir.')
  done=page.evaluate('__V66_QA.reload()');check('reload keeps completed service and no food respawn',done['ledger']['finished'] and done['food']==0 and not done['staged'])
  page.evaluate('__V66_QA.near("josiane")');check('completion cannot be farmed',not page.evaluate('__MISTRAL_DEBUG.v066VoisinsAction("finish")'))
  count=page.evaluate('__V66_QA.repeat()');check('rendering does not duplicate tables controls or actors',count['props']==final['props'] and count['extras']==7 and len(count['npcs'])==5)
  # Alternate path: player pays provisions, no amplification, no scene reposition.
  page.evaluate('(s)=>__V66_QA.restore(s)',invited);go('buffet','v66:buffet');inv=page.evaluate('__V66_QA.info().inv');choose('Fournir 3 vivres');choose('Revenir.');check('player contribution deducts exact inventory amounts',page.evaluate('__V66_QA.info().inv.food')==inv['food']-3 and page.evaluate('__V66_QA.info().inv.water')==inv['water']-2)
  go('console','v66:console');choose('Débrancher');choose('Revenir.');check('unamplified path available without technical stat',page.evaluate('__V66_QA.info().ledger.sound')=='silence')
  guest('josiane');choose('Prévoir : Un service');choose('Confirmer');check('palier layout leaves everyone at their original stations',page.evaluate('__V66_QA.info().npcs')==homes and not page.evaluate('__V66_QA.info().staged'))
  for who in ['karim','lucie','nadia','salome']:
   guest(who);choose('Servir sa portion')
   if who=='karim':choose('Avancer 5 capsules')
   if who=='salome':choose('Présenter des excuses')
   choose('Revenir.')
  guest('josiane');choose('Terminer la soirée');check('palier outcome records material gesture and voluntary apology',page.evaluate('__V66_QA.info().ledger.outcome')=='paliers' and page.evaluate('__V66_QA.info().ledger.answers.karim')=='geste')
  # Alternate social ending from a legitimately prepared checkpoint.
  page.evaluate('(s)=>__V66_QA.restore(s)',prepared);guest('josiane');choose('Prévoir : Un service');choose('Confirmer')
  for who in ['karim','lucie','nadia','salome']:
   guest(who);choose('Servir sa portion')
   if who=='karim':choose('Reconnaître que le désaccord')
   if who=='salome':choose('Dire publiquement')
   choose('Revenir.')
  guest('josiane');choose('Terminer la soirée');check('unresolved objection produces truce not fabricated consensus',page.evaluate('__V66_QA.info().ledger.outcome')=='treve')
  page.evaluate('(s)=>__V66_QA.restore(s)',invited);go('console','v66:console');choose('Lire la notice');inv=page.evaluate('__V66_QA.info().inv.circuitry');choose('Régler avec Lucie');choose('Revenir.');check('technical shortcut spends one circuit and sets all physical switches',page.evaluate('__V66_QA.info().inv.circuitry')==inv-1 and page.evaluate('__V66_QA.info().ledger.sound')=='limitee')
  check('no JavaScript errors or swallowed presentation errors',not errors and not page.evaluate('__V66_QA.info().error'))
  report={'html_sha256':sha,'passed':len(checks),'checks':checks,'errors':errors,'browser':browser.version,'scope':'Actual authored Radieuse, existing NPCs staged/restored, E interaction, real buttons, inventory and isolated MemoryStorage. Prerequisites via original reducers; scripted positioning plus explicit native collision route. Native portal round-trip uses a synthetic retained exterior. Software renderer; not a full human campaign or IGN exterior traversal.'}
  (a.output/'VOISINS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception:
  page.screenshot(path=str(a.output/'failure.png'));print('STATE',page.evaluate('window.__V66_QA?.info()'),flush=True);raise
 finally:browser.close()
