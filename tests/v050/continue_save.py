#!/usr/bin/env python3
"""Latest-save selection and real Continue-button checks in Chromium.

Private fixture helpers populate actual origin localStorage with dated saves.
The production validator, migration, button handler and scene loader execute;
no confirmation, storage implementation or map provider is mocked.
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,time,traceback,urllib.request
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
path=Path(os.environ.get('MISTRAL_HTML',ROOT/'JOUER_FALLOUT_MISTRAL_v0.50.html'))
original=path.read_text();html=original;injected='function v050ContinueTimestamp(' not in html
if injected:html=html.replace('/* The airlock commits', (ROOT/'src/v050/00_continue.js').read_text()+'\n/* The airlock commits',1)
adapter=r"""
window.__CONTINUE_TEST={
 fixture:(name,iso,version='0.50.0')=>{const s=baseState();s.character.name=name;s.version=version;s.lastSave=iso;
   s.player.zone='vault_prologue';s.player.discovered=['vault_prologue'];s.player.pos=[0,1.65,60];s.player.caps=73;s.quest.main=1;
   Object.assign(s.v035.prologue,{started:true,titleSeen:true,stage:8,complete:false});return s;},
 keys:()=>({current:SAVE_KEY,auto:V035_AUTOSAVE_KEY,slot1:v035SlotKey(1),slot2:v035SlotKey(2),slot3:v035SlotKey(3),legacy049:'fallout_mistral_save_v049',legacy048:'fallout_mistral_save_v048'}),
 set:rows=>{gameStarted=false;v046Cancel();V018.qaFreeze=true;debugRenderPaused=true;
   for(const k of [SAVE_KEY,...LEGACY_SAVE_KEYS,V035_AUTOSAVE_KEY,...[1,2,3].map(v035SlotKey)])localStorage.removeItem(k);
   for(const [key,value]of rows)localStorage.setItem(key,typeof value==='string'?value:JSON.stringify(value));
   v035RefreshContinue();return true;},
 read:key=>localStorage.getItem(key),
 state:()=>deepClone(state),
 menu:()=>showMenu(),
 candidateNames:()=>v050ContinueCandidates().map(c=>c.snapshot.character.name)
};
"""
html=html.replace('\ninit();\nv018AfterInit();','\n'+adapter+'\ninit();\nv018AfterInit();',1)
out=ROOT/'verification/v050';out.mkdir(parents=True,exist_ok=True)
checks=[];errors=[]
def check(name,ok,detail=None):checks.append({'name':name,'ok':bool(ok),'detail':detail});print(('OK ' if ok else 'FAIL ')+name,flush=True)
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
origin=f'http://127.0.0.1:{port}';log=(out/'continue_server.log').open('w')
server=subprocess.Popen([sys.executable,'tools/serve_game.py','--port',str(port),'--no-browser'],cwd=ROOT,stdout=log,stderr=log)
try:
    for _ in range(80):
        try:
            with urllib.request.urlopen(origin+'/index.html',timeout=1):break
        except Exception:time.sleep(.1)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(service_workers='block');page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.route(origin+'/index.html',lambda route:route.fulfill(status=200,content_type='text/html',body=html))
        page.goto(origin+'/index.html',wait_until='load');page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
        def api(name,*args):return page.evaluate('([n,a])=>__CONTINUE_TEST[n](...a)',[name,list(args)])
        def info():return page.evaluate('__MISTRAL_DEBUG.v050ContinueInfo()')
        keys=api('keys');a='2026-10-18T10:00:00.000Z';b='2026-10-18T11:00:00.000Z';c='2026-10-18T12:00:00.000Z'
        def fixture(name,date=a,version='0.50.0'):return api('fixture',name,date,version)
        def env(snapshot,date):return {'schema':1,'snapshot':snapshot,'savedAt':date}
        def seed(rows):return api('set',[[keys[k],v]for k,v in rows])
        def best():return api('candidateNames')[0] if info() else None
        current=fixture('courant récent',c);old=fixture('ancienne autosave',a)
        seed([('current',current),('auto',env(old,1792321200000))])
        # Dates are compared by parser, without relying on a guessed epoch.
        seed([('current',current),('auto',env(old,b)),('slot1',env(fixture('slot ancien'),a))])
        check('Courant récent prioritaire sur autosave et slot anciens',best()=='courant récent')
        before={k:api('read',keys[k])for k in ['current','auto','slot1']};info()
        check('Classement et rafraîchissement ne modifient aucune sauvegarde',before=={k:api('read',keys[k])for k in before})
        seed([('current',fixture('courant',a)),('auto',env(fixture('auto'),c)),('slot1',env(fixture('slot'),b))])
        check('Autosave réellement plus récente sélectionnée',best()=='auto')
        seed([('current',fixture('courant',a)),('auto',env(fixture('auto'),b)),('slot2',env(fixture('slot récent'),c))])
        check('Slot réellement plus récent sélectionné',best()=='slot récent' and info()[0]['slot']==2)
        seed([('current',fixture('courant',a)),('legacy049',fixture('legacy récente',c,'0.49.0'))])
        check('Sauvegarde v049 plus récente prise en compte',best()=='legacy récente' and info()[0]['kind']=='legacy')
        seed([('current',fixture('courant égal',b)),('auto',env(fixture('auto égale'),b)),('slot1',env(fixture('slot égal'),b)),('legacy049',fixture('legacy égale',b,'0.49.0'))])
        check('Égalité de date donne priorité au courant',best()=='courant égal')
        seed([('auto',env(fixture('auto égale'),b)),('slot2',env(fixture('slot deux'),b)),('slot1',env(fixture('slot un'),b))])
        check('Égalité sans courant reste déterministe',api('candidateNames')==['slot un','slot deux','auto égale'])
        seed([('legacy048',fixture('v048',b,'0.48.0')),('legacy049',fixture('v049',b,'0.49.0'))])
        check('Égalité entre legacy respecte la version la plus récente',best()=='v049')
        seed([('current',fixture('date invalide','not-a-date')),('auto',env(fixture('auto datée'),b))])
        check('Date invalide ne passe pas devant une sauvegarde datée',best()=='auto datée')
        seed([('auto',env(fixture('date snapshot',c),'not-a-date')),('current',fixture('courant',b))])
        check('Enveloppe sans date valide utilise lastSave de son snapshot',best()=='date snapshot')
        seed([('current','{corrompu'),('slot1',{'savedAt':c,'snapshot':{'player':{},'character':{},'quest':{}}}),('legacy049',fixture('secours v049',b,'0.49.0'))])
        check('JSON corrompu et snapshot invalide ignorés',best()=='secours v049' and len(info())==1)
        legacy_raw=api('read',keys['legacy049']);api('menu');page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().id==='vault_prologue'&&__MISTRAL_DEBUG.getState().character.name==='secours v049'")
        loaded=api('state')
        check('Vrai bouton Continuer charge le secours validé',loaded['character']['name']=='secours v049' and loaded['player']['caps']==73)
        check('Chargement du secours conserve sa clé source intacte',api('read',keys['legacy049'])==legacy_raw)
        check('Migration v049 conserve prologue et inventaire',loaded['v035']['prologue']['stage']==8 and loaded['quest']['main']==1 and loaded['v050Campaign']['returnPoint'] is None)
        check('Chargement sélectionné ne facture pas de trajet',loaded['worldTime']==fixture('compare')['worldTime'])
        seed([('current',fixture('dernier déplacement',c)),('auto',env(fixture('ancien atelier'),a))]);api('menu');page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.getState().character.name==='dernier déplacement'")
        check('Clic Continuer reprend le courant malgré une enveloppe existante',api('state')['character']['name']=='dernier déplacement')
        seed([('current','{'),('auto',{'snapshot':{}})]);api('menu')
        check('Bouton désactivé lorsque toutes les sauvegardes sont invalides',page.locator('#btnContinue').is_disabled())
        check('Aucune exception JavaScript',not errors,errors)
        context.close();browser.close()
except Exception:check('Scénario Continuer terminé',False,traceback.format_exc());print(traceback.format_exc(),flush=True)
finally:
    server.terminate();server.wait(timeout=10);log.close()
    report={'version':'0.50.0','html_sha256':hashlib.sha256(original.encode()).hexdigest(),'module_inserted_before_integration':injected,
      'scope':'Real Chromium and origin localStorage; private dated-save fixtures, production validator/migration/button/loader; no geography substitute',
      'passed':sum(c['ok']for c in checks),'failed':sum(not c['ok']for c in checks),'total':len(checks),'errors':errors,'checks':checks}
    (out/'QA_CONTINUE_SAVE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['passed','failed','total','errors']}),flush=True)
raise SystemExit(bool(report['failed'] or errors))
