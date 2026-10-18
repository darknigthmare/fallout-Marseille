#!/usr/bin/env python3
"""Build and verify BOTH runnable and complete-source v0.46 archives."""
from pathlib import Path,PurePosixPath
import zipfile,json,hashlib,sys,tempfile,subprocess
R=Path(__file__).resolve().parents[1];OUT=R.parent
HTML='JOUER_FALLOUT_MISTRAL_v0.46.html'
GAME=OUT/'FALLOUT_MISTRAL_v0.46_JEU_SEUL.zip';FULL=OUT/'FALLOUT_MISTRAL_v0.46_PROJET_COMPLET.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def include(p):return p.is_file() and '__pycache__' not in p.parts and p.suffix.lower() not in ('.pyc','.ttf','.otf','.woff','.woff2') and '.git' not in p.parts
# Source and data provenance stay unchanged; refreshed manifests cover this build.
full_files=[p for p in sorted(R.rglob('*')) if include(p) and p.name not in ['MANIFEST_SHA256.json','MANIFEST_JEU_SHA256.json']]
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'version':'0.46.0','files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in full_files]},ensure_ascii=False,indent=2)+'\n')
rootfiles=[HTML,'index.html','README_FR.md','START_HERE.txt','manifest.webmanifest','sw.js','RAPPORT_VISUEL_V0.46.html','RAPPORT_VISUEL_V0.46.png','LANCER_JEU.bat','LANCER_JEU.sh','LANCER_APP_WINDOWS.bat','LANCER_APP_LINUX.sh','LANCER_APP_MAC.command','INSTALLER_PACK_LOCAL_WINDOWS.bat','INSTALLER_PACK_LOCAL_LINUX_MAC.sh','VERIFIER_PACK_LOCAL_WINDOWS.bat','VERIFIER_PACK_LOCAL_LINUX_MAC.sh']
tools=['serve_game.py','validate_real_map_v046.py','install_local_pack_v041.py','install_terrain_v039.py','mvt_audit_v036.py','benchmark_map_v041.py','audit_real_map_v039.py','audit_real_map_v038.py','audit_terrain_v039.py','audit_corridors_v040.py']
rels=rootfiles+['tools/'+x for x in tools]
rels += [str(p.relative_to(R)) for folder in ['icons','data','verification/v046'] for p in (R/folder).rglob('*') if include(p)]
rels += ['docs/'+x for x in ['ARCHITECTURE_V0.46.md','LORE_RECONSTRUIT_V046.md','PROVENANCE_V046.md','KNOWN_LIMITATIONS_V0.46.md','INSTALLATION_V046.md','LICENCES_V046.md','STATUT_PRODUCTION.md','RAPPORT_QA.md','RELEASE_NOTES_V0.46.md','RAPPORT_VISUEL_V0.46.md']]
rels=sorted(set(rels));assert all((R/f).is_file() for f in rels)
(R/'MANIFEST_JEU_SHA256.json').write_text(json.dumps({'version':'0.46.0','files':[{'path':f,'bytes':(R/f).stat().st_size,'sha256':sha(R/f)} for f in rels]},ensure_ascii=False,indent=2)+'\n')
for target,files in [(GAME,[R/f for f in rels]+[R/'MANIFEST_JEU_SHA256.json']),(FULL,full_files+[R/'MANIFEST_SHA256.json'])]:
 target.unlink(missing_ok=True)
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:
   rel=p.relative_to(R).as_posix();z.write(p,rel if target==GAME else R.name+'/'+rel)
checks=[]
def ck(name,yes,detail=None):
 checks.append({'name':name,'ok':bool(yes),'detail':detail});print(('OK ' if yes else 'FAIL ')+name,flush=True)
 if not yes:raise RuntimeError(name)
for target,prefix,manifest in [(GAME,'','MANIFEST_JEU_SHA256.json'),(FULL,R.name+'/','MANIFEST_SHA256.json')]:
 with zipfile.ZipFile(target) as z:
  ck(target.stem+' : intégrité ZIP',z.testzip() is None)
  ck(target.stem+' : chemins sûrs',all(not n.startswith('/') and '..' not in PurePosixPath(n).parts and '\\' not in n for n in z.namelist()))
  ck(target.stem+' : HTML exact',hashlib.sha256(z.read(prefix+HTML)).hexdigest()==sha(R/HTML))
  m=json.loads(z.read(prefix+manifest));bad=[]
  for row in m['files']:
   raw=z.read(prefix+row['path'])
   if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:bad.append(row['path'])
  ck(target.stem+' : toutes les empreintes exactes',not bad,{'entries':len(m['files'])})
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(FULL) as z:z.extractall(td)
 E=Path(td)/R.name;r=subprocess.run([sys.executable,'tools/build_single.py'],cwd=E,capture_output=True,text=True,timeout=30)
 ck('Reconstruction du projet extrait',r.returncode==0,r.stderr[-400:]);ck('HTML reconstruit identique octet pour octet',sha(E/HTML)==sha(R/HTML))
 r=subprocess.run(['node','--check','src/game.js'],cwd=E,capture_output=True,text=True,timeout=30);ck('Syntaxe du JavaScript reconstruit',r.returncode==0,r.stderr[-400:])
 for t in ['kernel.test.cjs','distribution.cjs']:
  r=subprocess.run(['node','tests/v046/'+t],cwd=E,capture_output=True,text=True,timeout=30);ck('Tests du projet extrait : '+t,r.returncode==0,r.stdout[-120:])
from playwright.sync_api import sync_playwright
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(GAME) as z:z.extractall(td)
 E=Path(td)
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});err=[];p.on('pageerror',lambda e:err.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content((E/HTML).read_text(),wait_until='load');p.wait_for_timeout(3100)
  ck('Jeu extrait : version active',p.evaluate('__MISTRAL_DEBUG.v046Info().version')=='0.46.0')
  ck('Jeu extrait : banc complet ouvre',p.evaluate('__MISTRAL_DEBUG.v046Lab()') is True)
  sig=p.evaluate('__MISTRAL_DEBUG.v046Signature()');ck('Jeu extrait : cinq bâtiments de test, pas une image fixe',len(sig['buildings'])==5)
  ck('Jeu extrait : aucune exception JS',not err,err);b.close()
q=json.loads((R/'verification/v046/QA_GLOBAL.json').read_text());cap=json.loads((R/'verification/v046/CAPTURES.json').read_text())
ck('QA correspond exactement au HTML livré',q['failed']==0 and q['allHtmlMatch'] and q['html_sha256']==sha(R/HTML),{'tests':q['total']})
ck('Captures du même HTML',cap['html_sha256']==sha(R/HTML) and not cap['errors'])
prov=json.loads((R/'verification/v046/PROVENANCE.json').read_text());ck('Provenance ne revendique pas la v044 absente',prov['baseVersion']=='0.42.0' and prov['v044ArchiveRecovered'] is False)
local=json.loads((R/'verification/v046/LOCAL_DATA_STATE.json').read_text());ck('Pack géographique non installé annoncé comme incomplet',local['complete'] is False and local['vector']['missing']==5884 and local['terrain']['missing']==8)
report={'version':'0.46.0','passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'html_sha256':sha(R/HTML),'checks':checks,'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in [R/HTML,GAME,FULL,R/'RAPPORT_VISUEL_V0.46.png']}}
P=OUT/'FALLOUT_MISTRAL_v0.46_CONTROLES_LIVRAISON.json';P.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
C=OUT/'FALLOUT_MISTRAL_v0.46_CHECKSUMS.txt';C.write_text('\n'.join(sha(p)+'  '+p.name+'  '+str(p.stat().st_size) for p in [R/HTML,GAME,FULL,R/'RAPPORT_VISUEL_V0.46.png',P])+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','total','artifacts']},ensure_ascii=False,indent=2))
