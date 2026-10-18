#!/usr/bin/env python3
"""Campaign/map transaction checks in Chromium against installed real data.

The private test adapter restores an airlock-ready snapshot, freezes simulation,
approaches physical gateways, and injects preparation failures/session changes.
Only the document is instrumented; vector/terrain requests and browser storage
use the real local server. Native uninstrumented captures are a separate suite.
"""
from pathlib import Path
import hashlib, json, math, os, socket, subprocess, sys, time, traceback, urllib.request
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright

path=Path(os.environ.get('MISTRAL_HTML',ROOT/'JOUER_FALLOUT_MISTRAL_v0.50.html'))
original=path.read_text(encoding='utf-8');html=original
injected='const V050_CAMPAIGN_POINT=' not in html
if injected:
    html=html.replace('/* Territorial travel uses', (ROOT/'src/v050/01_campaign.js').read_text()+'\n/* Territorial travel uses',1)
if 'v050CampaignAfterInit();' not in html:
    html=html.replace('v050AfterInit();\n})();','v050AfterInit();\nv050CampaignAfterInit();\n})();',1)
adapter=r"""
window.__V050_CAMPAIGN_TEST={
 reset:snapshot=>{
   v046Cancel();state=migrateState(snapshot||baseState());
   if(!snapshot){state.mode='campaign';state.player.zone='vault_prologue';state.player.discovered=['vault_prologue'];state.quest.main=1;
     Object.assign(state.v035.prologue,{started:true,titleSeen:true,stage:8,locker:true,clinic:true,filter:true,breakfast:true,records:true,briefed:true,loadout:'patrol',complete:false});}
   V046.lab=false;V047.auto=false;V018.qaFreeze=true;debugRenderPaused=true;gameStarted=true;hideAllScreens();
   loadZone(state.player.zone,{instance:!V015_GEO_MACROS[state.player.zone],force:true,silent:true,noTravel:true,spawn:state.player.pos,yaw:state.player.yaw});
   mode='PLAYING';$('hud').classList.add('active');saveGame(false);return deepClone(state);
 },
 state:()=>deepClone(state),
 source:()=>({id:world?.id,scene:world?.v046SceneId||(world.v046SceneId=++V046.serial),mode,lab:V046.lab}),
 saved:()=>JSON.parse(storage.getItem(SAVE_KEY)),
 approach:id=>{
   const it=world?.interactables.find(i=>i.id===id);if(!it)return null;
   const stage=world.v046?{records:world.v046Records,bank:v047Bank(world),geoColliders:world.colliders.filter(c=>c.v046Tile)}:null;
   for(const r of [2.8,3.5,4])for(let n=0;n<24;n++){
     const a=n/24*TAU,x=it.pos[0]+Math.sin(a)*r,z=it.pos[2]+Math.cos(a)*r;
     const h=stage?v050TravelGround(stage,world,x,z,.5):groundHeightAt(x,z);
     if(h===null||collidesAt(x,z,.38,h+playerEyeHeight()))continue;
     state.player.pos=[x,h+playerEyeHeight(),z];state.player.yaw=Math.atan2(it.pos[0]-x,z-it.pos[2]);state.player.pitch=0;onGround=true;
     return {pos:state.player.pos.slice(),id:it.id};
   }return null;
 },
 mireille:()=>{const n=world.npcs.find(n=>n.id==='mireille');if(!n)return false;talkToNPC(n.id);return true;},
 continueStory:()=>{state.inventory.scrap=(state.inventory.scrap||0)+2;return deepClone(state);},
 objectives:()=>({title:$('questTitle').textContent,objective:$('questObjective').textContent,marker:getObjectiveMarker()}),
 migrate:s=>migrateState(s),
 replace:s=>{state=migrateState(s);loadZone(state.player.zone,{instance:true,force:true,silent:true,noTravel:true,spawn:state.player.pos,yaw:state.player.yaw});mode='PLAYING';return deepClone(state);}
};
"""
html=html.replace('\ninit();\nv018AfterInit();','\n'+adapter+'\ninit();\nv018AfterInit();',1)
out=ROOT/'verification/v050';out.mkdir(parents=True,exist_ok=True)
checks=[];errors=[];server=None;page=None
def check(name,ok,detail=None):
    checks.append({'name':name,'ok':bool(ok),'detail':detail});print(('OK ' if ok else 'FAIL ')+name,flush=True)
def protected(s):
    return {k:s.get(k) for k in ['player','worldTime','quest','inventory','equipment','flags','v050Campaign']}|{'prologue':s['v035']['prologue']}
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
origin=f'http://127.0.0.1:{port}'
log=(out/'campaign_server.log').open('w')
server=subprocess.Popen([sys.executable,'tools/serve_game.py','--port',str(port),'--no-browser'],cwd=ROOT,stdout=log,stderr=log)
try:
    for _ in range(80):
        try:
            with urllib.request.urlopen(origin+'/index.html',timeout=1):break
        except Exception:time.sleep(.15)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block')
        page=context.new_page();page.set_default_timeout(30000)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route(origin+'/index.html',lambda route:route.fulfill(status=200,content_type='text/html',body=html))
        page.goto(origin+'/index.html',wait_until='load');page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
        def call(name,*args):return page.evaluate('([n,a])=>__MISTRAL_DEBUG[n](...a)',[name,list(args)])
        def inspect(name,*args):return page.evaluate('([n,a])=>__V050_CAMPAIGN_TEST[n](...a)',[name,list(args)])
        def state():return inspect('state')
        def exit_choice(index=0):
            check('SAS accessible au stade de sortie',call('v35pExit') is True)
            choices=page.locator('#dialogueChoices button')
            if index==0:check('Choix carte réelle proposé avant la scène narrative',choices.nth(0).inner_text()=='Sortir vers Aubagne' and 'scène narrative' in choices.nth(1).inner_text())
            choices.nth(index).click()
        def finished(kind):
            page.wait_for_function('(kind)=>{const c=__MISTRAL_DEBUG.v050CampaignInfo();return !c.pending&&c.last?.status===\'complete\'&&c.last?.kind===kind;}',arg=kind,timeout=90000)
        initial=inspect('reset');source=inspect('source');before=state();saved=inspect('saved')
        call('v047Control',{'failPrepare':True})
        exit_choice();page.wait_for_function("__MISTRAL_DEBUG.v050CampaignInfo().pending?.status==='failed'",timeout=90000)
        check('Échec de carte conserve le sas actif',inspect('source')['scene']==source['scene'] and inspect('source')['id']=='vault_prologue')
        check('Échec conserve progression, objets, position et heure',protected(state())==protected(before))
        check('Échec ne publie pas de sauvegarde partielle',inspect('saved')==saved)
        call('v047Control',{'failPrepare':False});page.locator('#v046Retry').click();finished('exit')
        after=state();info=call('v050CampaignInfo');map_info=call('v047Info')
        check('Réessai sort sur les vraies données locales',not map_info['lab'] and map_info['tiles']>0 and set(map_info['origins'])=={'pack local'},map_info['origins'])
        check('Prologue terminé seulement après sortie validée',after['v035']['prologue']['complete'] and after['v035']['prologue']['stage']==9 and after['quest']['main']==2)
        check('Sortie ne fait pas avancer l’heure',after['worldTime']==before['worldTime'])
        check('Arrivée extérieure sans collision',call('v046Collide',after['player']['pos'][0],after['player']['pos'][2]) is False)
        check('Arrivée reste dans la marge du secteur chargé',math.dist([after['player']['pos'][0],after['player']['pos'][2]],[info['last']['loadedAnchor'][0],info['last']['loadedAnchor'][2]])<=145)
        check('Balise de campagne physique présente',info['gateway'] and info['gateway']['id']=='v050-campaign-workshops',info['gateway'])
        objective=inspect('objectives')
        check('Quête principale guide vers le passage réel',objective['marker'] and 'Ateliers' in objective['marker']['label'] and 'scène narrative' in objective['objective'],objective)
        check('Réessai terminé ne répète pas la sortie',call('v050CampaignRetry') is False)
        check('L’entrée narrative exige d’approcher la balise',call('v050CampaignOpenWorkshops') is False)
        approached=inspect('approach','v050-campaign-workshops');check('Balise accessible sur un sol dégagé',approached is not None,approached)
        return_point=state()['player']['pos'];check('Interaction physique ouvre la scène narrative',call('v050CampaignOpenWorkshops') is True)
        page.locator('#dialogueChoices button').first.click();finished('workshops')
        info=call('v050CampaignInfo')
        check('Ateliers nommés explicitement scène narrative',info['zone']=='aubagne' and 'scène narrative' in page.locator('#locationName').inner_text())
        check('Point géographique persistant capturé',info['saved']['returnPoint']['pos']==return_point)
        check('Mireille et son dialogue de campagne restent disponibles',inspect('mireille') is True)
        # Use her authored first choice, which opens the relay objective.
        page.locator('#dialogueChoices button').first.click()
        check('Dialogue de Mireille fait avancer la campagne',state()['quest']['main']==3)
        call('v020ModalDismiss');inspect('continueStory');story_state=state()
        check('Porte physique vers le territoire disponible',inspect('approach','v050-campaign-territory') is not None)
        story_state=state();call('v047Control',{'failPrepare':True})
        check('Retour proposé depuis les ateliers',call('v050CampaignOpenReturn') is True)
        page.locator('#dialogueChoices button').first.click();page.wait_for_function("__MISTRAL_DEBUG.v050CampaignInfo().pending?.status==='failed'",timeout=90000)
        check('Échec du retour conserve la scène narrative et ses acquis',call('v050CampaignInfo')['zone']=='aubagne' and protected(state())==protected(story_state))
        call('v047Control',{'failPrepare':False});page.locator('#v046Retry').click();finished('return');returned=state()
        check('Retour rejoint exactement le point conservé',all(abs(a-b)<.02 for a,b in zip(returned['player']['pos'],return_point)),{'expected':return_point,'actual':returned['player']['pos']})
        check('Quête et inventaire acquis dans les ateliers restent acquis',returned['quest']==story_state['quest'] and returned['inventory']==story_state['inventory'])
        check('Retour ne change pas l’heure',returned['worldTime']==story_state['worldTime'])
        # Reload a narrative snapshot through the normal migration and loader.
        reloaded=inspect('reset',story_state)
        check('Recharge d’une sauvegarde narrative conserve sa porte de retour',call('v050CampaignInfo')['gateway']['id']=='v050-campaign-territory' and state()['v050Campaign']['returnPoint']['pos']==return_point)
        inspect('approach','v050-campaign-territory');call('v050CampaignOpenReturn');page.locator('#dialogueChoices button').first.click();finished('return')
        check('Retour fonctionne après recharge de sauvegarde',all(abs(a-b)<.02 for a,b in zip(state()['player']['pos'],return_point)))
        # Abort after real downloads, during budgeted building preparation.
        inspect('reset',initial);before=state();source=inspect('source');call('v048Control',{'pausePhase':'batiments','pauseMs':1200})
        exit_choice();page.wait_for_function("__MISTRAL_DEBUG.v048Info().preparation?.phase==='batiments'",timeout=90000)
        page.locator('#v046Cancel').click();page.wait_for_timeout(1400)
        check('Annulation en préparation conserve sas, progression et heure',protected(state())==protected(before) and inspect('source')['scene']==source['scene'])
        check('Une sortie annulée ne peut plus être réessayée',call('v050CampaignRetry') is False)
        # Replacing a save while an old request awaits must not overwrite it.
        exit_choice();page.wait_for_function("__MISTRAL_DEBUG.v048Info().preparation?.phase==='batiments'",timeout=90000)
        replacement=json.loads(json.dumps(initial));replacement['player']['caps']+=37
        replacement=inspect('replace',replacement);page.wait_for_timeout(1400)
        check('Nouvelle sauvegarde protégée des réponses tardives',protected(state())==protected(replacement) and inspect('source')['mode']=='PLAYING')
        check('Ancien contexte de sortie invalidé',call('v050CampaignRetry') is False)
        call('v048Control',{'pausePhase':None,'pauseMs':0})
        inspect('reset',initial);before=state();exit_choice(1);finished('story-exit')
        check('Raccourci explicite conserve l’accès à la campagne historique',call('v050CampaignInfo')['zone']=='aubagne' and state()['quest']['main']==2 and state()['v050Campaign']['route']=='story')
        check('Raccourci n’ajoute aucun temps de trajet',state()['worldTime']==before['worldTime'])
        old=state();del old['v050Campaign'];migrated=inspect('migrate',old)
        check('Anciennes sauvegardes migrées sans perte de progression',migrated['quest']==old['quest'] and migrated['inventory']==old['inventory'] and migrated['v050Campaign']['returnPoint'] is None)
        check('Aucune exception JavaScript',not errors,errors)
        context.close();browser.close()
except Exception:
    check('Scénario campagne/carte terminé',False,traceback.format_exc())
    print(traceback.format_exc(),flush=True)
    if page:
        try:print(page.evaluate('({campaign:__MISTRAL_DEBUG.v050CampaignInfo(),stream:__MISTRAL_DEBUG.v047Info()})'))
        except Exception:pass
finally:
    if server:server.terminate();server.wait(timeout=10)
    log.close()
    report={'version':'0.50.0','tested_html':path.name,'html_sha256':hashlib.sha256(original.encode()).hexdigest(),
      'module_inserted_before_integration':injected,'private_test_adapter':True,'data':'Installed real vectors and measured terrain, fetched over the local HTTP server',
      'passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'errors':errors,'checks':checks}
    (out/'QA_CAMPAIGN_MAP.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['passed','failed','total','errors']}),flush=True)
raise SystemExit(bool(report['failed'] or errors))
