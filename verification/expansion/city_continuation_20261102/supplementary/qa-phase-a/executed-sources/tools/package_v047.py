#!/usr/bin/env python3
"""Create and re-extract the complete v0.47 project and its playable distribution.
No external deployment. All delivered links refer to materialised local files.
"""
from pathlib import Path, PurePosixPath
import hashlib,json,zipfile,tempfile,subprocess,sys,threading,urllib.request,socket,time
R=Path(__file__).resolve().parents[1]; OUT=R.parent
HTML='JOUER_FALLOUT_MISTRAL_v0.47.html'
GAME=OUT/'FALLOUT_MISTRAL_v0.47_JEU_SEUL.zip';FULL=OUT/'FALLOUT_MISTRAL_v0.47_PROJET_COMPLET.zip'
CONTROL=OUT/'FALLOUT_MISTRAL_v0.47_CONTROLES_LIVRAISON.json';SUMS=OUT/'FALLOUT_MISTRAL_v0.47_CHECKSUMS.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def include(p):return p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.suffix.lower() not in {'.pyc','.ttf','.otf','.woff','.woff2'}
def safe(n):return not n.startswith(('/', '\\')) and '..' not in PurePosixPath(n).parts and '\\' not in n
checks=[]
def ck(name,ok,detail=None):
    checks.append({'name':name,'ok':bool(ok),'detail':detail});print(('OK ' if ok else 'FAIL ')+name,flush=True)
    if not ok:raise RuntimeError(name)
q=json.loads((R/'verification/v047/QA_GLOBAL.json').read_text());cap=json.loads((R/'verification/v047/CAPTURES.json').read_text());h=sha(R/HTML)
ck('QA actuelle et toutes les empreintes concordent',q['failed']==0 and q['passed']==q['total'] and q['allHtmlMatch'] and q['html_sha256']==h,{'passed':q['passed'],'total':q['total']})
ck('Captures du même HTML, sans exception',cap['html_sha256']==h and not cap['errors'])
rootfiles=[HTML,'index.html','README_FR.md','START_HERE.txt','manifest.webmanifest','sw.js','RAPPORT_VISUEL_V0.47.html','RAPPORT_VISUEL_V0.47.png','LANCER_JEU.bat','LANCER_JEU.sh','LANCER_APP_WINDOWS.bat','LANCER_APP_LINUX.sh','LANCER_APP_MAC.command','INSTALLER_PACK_LOCAL_WINDOWS.bat','INSTALLER_PACK_LOCAL_LINUX_MAC.sh','VERIFIER_PACK_LOCAL_WINDOWS.bat','VERIFIER_PACK_LOCAL_LINUX_MAC.sh','BENCHMARK_PACK_LOCAL_WINDOWS.bat','BENCHMARK_PACK_LOCAL_LINUX_MAC.sh']
tools=['serve_game.py','validate_real_map_v046.py','install_local_pack_v041.py','install_terrain_v039.py','mvt_audit_v036.py','benchmark_map_v041.py','audit_real_map_v039.py','audit_real_map_v038.py','audit_terrain_v039.py','audit_corridors_v040.py']
docs=['CONTENU_V0.47.md','ARCHITECTURE_V0.47.md','KNOWN_LIMITATIONS_V0.47.md','MIGRATION_V046_V047.md','PROVENANCE_V047.md','INSTALLATION_V047.md','STATUT_PRODUCTION.md','RELEASE_NOTES_V0.47.md','RAPPORT_QA.md','RAPPORT_VISUEL_V0.47.md','LORE_RECONSTRUIT_V046.md','LICENCES_V046.md']
rels=rootfiles+['tools/'+n for n in tools]+['docs/'+n for n in docs]
rels += [p.relative_to(R).as_posix() for folder in ['icons','data'] for p in (R/folder).rglob('*') if include(p)]
rels += [p.relative_to(R).as_posix() for p in (R/'verification/v047').iterdir() if include(p) and p.suffix in {'.json','.png'}]
rels=sorted(set(rels));ck('Tous les composants du jeu compact sont présents',all((R/x).is_file() for x in rels))
# Full source archive excludes only generated manifests, bytecode, VCS, fonts.
full_files=[p for p in sorted(R.rglob('*')) if include(p) and p.name not in {'MANIFEST_SHA256.json','MANIFEST_JEU_SHA256.json'}]
full_manifest={'version':'0.47.0','scope':'Projet complet : sources, données présentes, tests et historique. Pas le pack territorial absent.','files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in full_files]}
game_manifest={'version':'0.47.0','scope':'Distribution jouable sans sources de reconstruction.','files':[{'path':f,'bytes':(R/f).stat().st_size,'sha256':sha(R/f)} for f in rels]}
(R/'MANIFEST_SHA256.json').write_text(json.dumps(full_manifest,ensure_ascii=False,indent=2)+'\n');(R/'MANIFEST_JEU_SHA256.json').write_text(json.dumps(game_manifest,ensure_ascii=False,indent=2)+'\n')
for target,files in [(GAME,[R/f for f in rels]+[R/'MANIFEST_JEU_SHA256.json']),(FULL,full_files+[R/'MANIFEST_SHA256.json'])]:
    target.unlink(missing_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:
            rel=p.relative_to(R).as_posix();z.write(p,rel if target==GAME else R.name+'/'+rel)
for target,prefix,manifest in [(GAME,'','MANIFEST_JEU_SHA256.json'),(FULL,R.name+'/','MANIFEST_SHA256.json')]:
    with zipfile.ZipFile(target) as z:
        ck(target.stem+' : CRC ZIP',z.testzip() is None)
        ck(target.stem+' : chemins sûrs',all(safe(n) for n in z.namelist()))
        ck(target.stem+' : HTML exact',hashlib.sha256(z.read(prefix+HTML)).hexdigest()==h)
        m=json.loads(z.read(prefix+manifest));bad=[]
        for e in m['files']:
            raw=z.read(prefix+e['path'])
            if len(raw)!=e['bytes'] or hashlib.sha256(raw).hexdigest()!=e['sha256']:bad.append(e['path'])
        ck(target.stem+' : toutes les empreintes exactes',not bad,{'files':len(m['files'])})
        ck(target.stem+' : aucune fonte distribuée',all(PurePosixPath(n).suffix.lower() not in {'.ttf','.otf','.woff','.woff2'} for n in z.namelist()))
with tempfile.TemporaryDirectory(prefix='mistral047-full-') as td:
    with zipfile.ZipFile(FULL) as z:z.extractall(td)
    E=Path(td)/R.name
    r=subprocess.run([sys.executable,'tools/build_single.py'],cwd=E,capture_output=True,text=True,timeout=45)
    ck('Reconstruction du projet extrait',r.returncode==0,r.stderr[-600:]);ck('HTML reconstruit identique octet pour octet',sha(E/HTML)==h)
    r=subprocess.run(['node','--check','src/game.js'],cwd=E,capture_output=True,text=True,timeout=30);ck('Syntaxe du programme reconstruit',r.returncode==0,r.stderr[-400:])
    for name in ['kernel.test.cjs','legacy_kernel.test.cjs','legacy_distribution.cjs']:
        r=subprocess.run(['node','tests/v047/'+name],cwd=E,capture_output=True,text=True,timeout=30);ck('Tests du projet extrait : '+name,r.returncode==0,r.stdout[-160:])
# Playable ZIP: inspect read-only loopback route and execute the exact HTML offline.
from playwright.sync_api import sync_playwright
with tempfile.TemporaryDirectory(prefix='mistral047-game-') as td:
    with zipfile.ZipFile(GAME) as z:z.extractall(td)
    E=Path(td)
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    log=(E/'server-check.log').open('w');proc=subprocess.Popen([sys.executable,'tools/serve_game.py','--port',str(port),'--no-browser'],cwd=E,stdout=log,stderr=log)
    try:
        status=None
        for _ in range(50):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/__mistral/local-data',timeout=1) as response:status=json.loads(response.read());break
            except OSError:time.sleep(.08)
        ck('Serveur du jeu extrait et audit HTTP fonctionnels',status is not None and status.get('version')=='0.47.0')
        ck('Audit du jeu extrait : manques déclarés',status['vector']['missing']==5884 and status['terrain']['missing']==8 and not status['complete'],status)
    finally:
        proc.terminate();proc.wait(timeout=6);log.close()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=browser.new_page(viewport={'width':1280,'height':800});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content((E/HTML).read_text(),wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=18000)
        ck('Jeu extrait : version active',p.evaluate('__MISTRAL_DEBUG.v047Info().version')=='0.47.0')
        ck('Jeu extrait : banc de chargement ouvre réellement',p.evaluate('__MISTRAL_DEBUG.v046Lab()') is True)
        sig=p.evaluate('__MISTRAL_DEBUG.v046Signature()');ck('Jeu extrait : scène de cinq bâtiments, pas une image',len(sig['buildings'])==5)
        ck('Jeu extrait : retour hors banc',p.evaluate('__MISTRAL_DEBUG.v046Campaign()') is True and not p.evaluate('__MISTRAL_DEBUG.v047Info().lab'))
        ck('Jeu extrait : aucune exception JavaScript',not errors,errors);browser.close()
prov=json.loads((R/'verification/v047/PROVENANCE.json').read_text())
ck('Provenance directe v0.46 explicitement conservée',prov['baseVersion']=='0.46.0' and prov['baseRecoveredInThisTurn'] and not prov['v044ArchiveRecovered'],prov['baseSha256'])
ck('Catalogue de 248 sites et modules v0.46 inchangés',prov['catalogue248Unchanged'] and prov['v046ModulesUnchanged'],prov['catalogueSha256'])
local=json.loads((R/'verification/v047/LOCAL_DATA_STATE.json').read_text());ck('Absence du pack territorial annoncée sans ambiguïté',not local['complete'] and local['vector']['missing']==5884 and local['terrain']['missing']==8)
report={'version':'0.47.0','passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'html_sha256':h,'checks':checks,'browserScope':'HTML extrait exécuté via set_content, réseau externe bloqué. Pas de navigation native/IndexedDB natif certifiés. Serveur contrôlé par requêtes HTTP Python séparées.','artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [R/HTML,GAME,FULL,R/'RAPPORT_VISUEL_V0.47.png',R/'RAPPORT_VISUEL_V0.47.html']}}
CONTROL.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
files=[R/HTML,GAME,FULL,R/'RAPPORT_VISUEL_V0.47.png',R/'RAPPORT_VISUEL_V0.47.html',CONTROL,R/'verification/v047/QA_GLOBAL.json']
SUMS.write_text('\n'.join(sha(p)+'  '+p.name+'  '+str(p.stat().st_size) for p in files)+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','total','artifacts']},ensure_ascii=False,indent=2))
