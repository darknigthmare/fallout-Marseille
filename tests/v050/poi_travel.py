"""Player-path travel checks against the real game and its labelled data fixture.

Before integration, only the new source is inserted into a v0.49 HTML in memory.
After integration, MISTRAL_HTML (or v0.50 when present) is tested directly. The
test-only inspectors below never appear in the distributed game.
"""
from pathlib import Path
import hashlib, json, math, os, sys, traceback
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
candidate=ROOT/'JOUER_FALLOUT_MISTRAL_v0.50.html'
path=Path(os.environ.get('MISTRAL_HTML',candidate if candidate.exists() else ROOT/'JOUER_FALLOUT_MISTRAL_v0.49.html'))
html=path.read_text(encoding='utf-8')
injected='const V050_TRAVEL=' not in html
if injected:
    html=html.replace('\ninit();\nv018AfterInit();','\n'+(ROOT/'src/v050/02_poi_travel.js').read_text()+'\ninit();\nv018AfterInit();',1)
    html=html.replace('v049AfterInit();\n})();','v049AfterInit();\nv050TravelAfterInit();\n})();',1)

inspectors=r"""
window.__V050_TEST={
 state:()=>JSON.parse(JSON.stringify(state)),
 source:()=>({scene:world.v046SceneId||(world.v046SceneId=++V046.serial),mode,ground:onGround,ready:V027.ready}),
 threat:on=>{world.enemies=world.enemies.filter(e=>e.id!=='qa-threat');if(on)world.enemies.push({id:'qa-threat',alive:true,pos:[state.player.pos[0]+10,state.player.pos[1],state.player.pos[2]],alerted:true});},
 unknownHud:id=>{V042_RUNTIME.nearest={site:v042Site(id),d:300};settings.geoFalloutLayer=true;v042UpdateHud();return $('v042LayerHud').textContent;},
 validate:(id,kind)=>{const site=v042Site(id),plan=v046Plan(site.lat,site.lon),stage={bank:V046.terrain,records:new Map(world.v046Records),geoColliders:world.colliders.filter(c=>c.v046Tile)};
   const p=v050TravelPoint(site),ring=[[p[0]-500,p[2]-500],[p[0]+500,p[2]-500],[p[0]+500,p[2]+500],[p[0]-500,p[2]+500],[p[0]-500,p[2]-500]];
   if(kind==='missing')stage.bank={read:()=>({height:null})};
   if(kind==='tile')stage.records.clear();
   if(kind==='solid')stage.geoColliders.push({minX:p[0]-500,maxX:p[0]+500,minZ:p[2]-500,maxZ:p[2]+500,minY:-100,maxY:9000});
   if(kind==='water')stage.records.set('qa-water',{water:[{rings:[ring]}],land:[],roads:[]});
   try{return {ok:true,arrival:v050TravelArrival(stage,world,site,plan)};}catch(e){return {ok:false,error:e.message};}}
};
"""
html=html.replace('\ninit();\nv018AfterInit();','\n'+inspectors+'\ninit();\nv018AfterInit();',1)
out=ROOT/'verification/v050';out.mkdir(parents=True,exist_ok=True)
checks=[];errors=[]
def check(name,ok,detail=None):
    checks.append({'name':name,'ok':bool(ok),'detail':detail})
    print(('OK ' if ok else 'FAIL ')+name,flush=True)
def protected(s):
    return {k:s.get(k) for k in ['player','worldTime','playTime','quest','inventory','equipment','v042','v046','v049','economy']}
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(30000)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('https://**/*',lambda r:r.abort())
    page.set_content(html,wait_until='load');page.wait_for_timeout(3000)
    page.evaluate("window.__store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{get length(){return __store.size},getItem:k=>__store.get(String(k))||null,setItem:(k,v)=>__store.set(String(k),String(v)),removeItem:k=>__store.delete(String(k)),key:i=>[...__store.keys()][i]||null}})")
    def call(name,*args):return page.evaluate('(a)=>__MISTRAL_DEBUG.'+name+'(...a)',list(args))
    def inspect(name,*args):return page.evaluate('(a)=>__V050_TEST.'+name+'(...a)',list(args))
    def state():return inspect('state')
    def open_map(site):
        call('v042Track',site['id']);call('v027Open','map','fallout')
    try:
        check('Banc de données identifié chargé',call('v046Lab'))
        call('setRenderPaused',True);call('v022Freeze',True);call('v047Control',{'auto':False})
        sites=call('v042Catalog');a=next(s for s in sites if s['kind']=='landmark' and s['macro']=='geo_huveaune');b=next(s for s in sites if s['kind']=='landmark' and s['macro']=='geo_marseille')
        call('v027Open','map','fallout');before=state()
        check('Lieu inconnu refusé',call('v050TravelRequest',a['id']) is False)
        check('Refus ne déplace et ne débite rien',protected(state())==protected(before))
        call('v042Discover',a['id']);open_map(a);before=state()
        check('Confirmation directe sans préparation refusée',call('v050TravelRequest',a['id'],True) is False)
        check('Fiche de voyage présente dans le Pip-Boy du jeu',page.locator('[data-p27="v050-travel"]').count()==1)
        inspect('threat',True)
        check('Ennemi proche bloque le voyage',call('v050TravelRequest',a['id']) is False)
        inspect('threat',False)
        before=state();source=inspect('source');quote=call('v050TravelQuote',a['id'])
        page.locator('[data-p27="v050-travel"]').click()
        check('Confirmation affiche la durée et la destination',a['name'] in page.locator('.v050-travel').inner_text() and 'Aucun coût en capsules' in page.locator('.v050-travel').inner_text())
        page.locator('[data-p27="v050-travel-confirm"]').click()
        page.wait_for_function("__MISTRAL_DEBUG.v050TravelInfo().last?.status==='complete'")
        after=state();info=call('v050TravelInfo')
        check('Voyage confirmé accompli',info['completed']==1,info)
        check('Même scène persistante après voyage',inspect('source')['scene']==source['scene'])
        check('Durée appliquée exactement une fois',math.isclose(after['worldTime'],(before['worldTime']+quote['minutes']/60)%24,abs_tol=1e-8))
        check('Capsules, XP et objets conservés',after['player']['caps']==before['player']['caps'] and after['player']['xp']==before['player']['xp'] and after.get('inventory')==before.get('inventory'))
        check('Arrivée réellement hors collision',call('v046Collide',after['player']['pos'][0],after['player']['pos'][2]) is False)
        check('Point d’arrivée dans la marge validée',math.dist([after['player']['pos'][0],after['player']['pos'][2]],[info['last']['loadedAnchor'][0],info['last']['loadedAnchor'][2]])<=145)
        call('v027Open','map','fallout')
        check('Voyage vers le lieu actuel refusé',call('v050TravelRequest',a['id']) is False)
        check('Réessai terminé sans second débit',call('v050TravelRetry') is False and state()['worldTime']==after['worldTime'])
        for kind in ['missing','tile','water','solid']:
            result=inspect('validate',a['id'],kind)
            check('Arrivée rejetée : '+kind,result['ok'] is False,result)
        call('v042Discover',b['id']);open_map(b)
        check('Repère suivi conservé au-delà du nom de macro',call('v050TravelMarker')['label']==b['name'])
        check('Liste proche considère aussi la macro voisine',b['id'] in [s['id'] for s in call('v050TravelNearby')])
        before=state();source=inspect('source');quote=call('v050TravelQuote',b['id'])
        call('v047Control',{'failPrepare':True});call('v050TravelRequest',b['id'])
        check('Échec de préparation propagé',call('v050TravelRequest',b['id'],True) is False)
        check('Échec conserve position, progression, inventaire et heure',protected(before)==protected(state()))
        check('Échec conserve la scène active',source['scene']==inspect('source')['scene'])
        call('v047Control',{'failPrepare':False})
        check('Réessai du même voyage réussit',call('v050TravelRetry') is True)
        check('Échec puis succès ne facturent qu’une durée',math.isclose(state()['worldTime'],(before['worldTime']+quote['minutes']/60)%24,abs_tol=1e-8) and call('v050TravelInfo')['completed']==2)
        open_map(a);call('v050TravelRequest',a['id']);before=state();source=inspect('source')
        call('v048Control',{'pausePhase':'batiments','pauseMs':1200})
        page.evaluate('(id)=>{window.__trip=__MISTRAL_DEBUG.v050TravelRequest(id,true);return true}',a['id'])
        page.wait_for_function("__MISTRAL_DEBUG.v048Info().preparation?.phase==='batiments'")
        call('v046Cancel');result=page.evaluate('window.__trip')
        check('Annulation interrompt une préparation réellement en cours',result is False)
        page.wait_for_timeout(1250)
        check('Réponse tardive ne change pas position, progression ni heure',protected(state())==protected(before))
        check('Annulation conserve la même scène',source['scene']==inspect('source')['scene'])
        check('Un voyage annulé ne peut pas être réessayé',call('v050TravelRetry') is False)
        open_map(a);call('v050TravelRequest',a['id'])
        before=state();source=inspect('source')
        page.evaluate('(id)=>{window.__trip=__MISTRAL_DEBUG.v050TravelRequest(id,true);return true}',a['id'])
        page.wait_for_function("__MISTRAL_DEBUG.v048Info().preparation?.phase==='batiments'")
        replacement=json.loads(json.dumps(before));replacement['player']['caps']+=17
        call('v049ReloadState',json.dumps(replacement))
        replacement=state();result=page.evaluate('window.__trip')
        check('Changement de sauvegarde rejette le voyage en attente',result is False)
        check('Réponse tardive préserve la sauvegarde nouvellement chargée',protected(state())==protected(replacement))
        check('Ancien contexte ne peut plus relancer le voyage',call('v050TravelRetry') is False)
        call('v046Cancel')
        call('v048Control',{'pausePhase':None,'pauseMs':0})
        unknown=next(s for s in sites if s['id'] not in state()['v042']['discovered'])
        text=inspect('unknownHud',unknown['id'])
        check('HUD ne révèle pas le nom d’un lieu inconnu','SIGNATURE INCONNUE' in text and unknown['name'] not in text)
        call('v042Clear',b['id']);call('v042Track',b['id'])
        check('Un lieu sécurisé reste suivable',b['name'] in page.locator('#questObjective').inner_text())
        check('Aucune exception JavaScript',not errors,errors)
    except Exception:
        check('Scénario de voyage',False,traceback.format_exc())
        print(json.dumps({'errors':errors,'last_check':checks[-1]},ensure_ascii=False),flush=True)
        try:print(json.dumps({'info':call('v050TravelInfo'),'source':inspect('source'),'integrity':call('v046Info')},ensure_ascii=False),flush=True)
        except Exception:pass
    browser.close()
report={'version':'0.50.0','tested_html':path.name,'in_memory_module_insertion':injected,'html_sha256':hashlib.sha256(html.encode()).hexdigest(),'passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'Programme exécuté dans Chromium, catalogue de production et fonctions joueur, données du banc synthétique signalé ; erreurs, eau, collision et NoData injectés uniquement dans ce test.'}
(out/'QA_POI_TRAVEL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(report['failed'] or errors))
