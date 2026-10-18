#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path,PurePosixPath
import hashlib,json,zipfile,tempfile,subprocess,sys,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent
GAME=OUT/'FALLOUT_MISTRAL_v0.38_JEU_SEUL.zip';PROJECT=OUT/'FALLOUT_MISTRAL_v0.38_PROJET_COMPLET.zip';CHECKS=OUT/'FALLOUT_MISTRAL_v0.38_CHECKSUMS.txt';DELIVERY=OUT/'FALLOUT_MISTRAL_v0.38_CONTROLES_LIVRAISON.json';HTML=ROOT/'JOUER_FALLOUT_MISTRAL_v0.38.html'
def sha(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(name:str):
 p=PurePosixPath(name);return not p.is_absolute() and '..' not in p.parts and not any(x in ('','.') for x in p.parts)
# Rebuild once and check syntax.
proc=subprocess.run([sys.executable,str(ROOT/'tools/build_single.py')],cwd=ROOT,capture_output=True,text=True)
if proc.returncode:raise SystemExit(proc.stderr)
node=subprocess.run(['node','--check',str(ROOT/'src/game.js')],capture_output=True,text=True)
if node.returncode:raise SystemExit(node.stderr)
html_sha=sha(HTML);vr=ROOT/'verification'
reports=['QA_V038.json','QA_MAP_TOOLS_V038.json','QA_CLOUD_PROOF_V038.json','QA_REGRESSION_V035_ON_V038.json','QA_REGRESSION_V035_PRODUCT_ON_V038.json','QA_REGRESSION_V035_PROLOGUE_ON_V038.json']
suites=[];passed=failed=total=0;errors=[]
for name in reports:
 d=json.loads((vr/name).read_text());p=int(d.get('passed',0));f=int(d.get('failed',0));t=int(d.get('total',p+f));h=d.get('html_sha256');suites.append({'file':name,'passed':p,'failed':f,'total':t,'sameHtml':not h or h==html_sha});passed+=p;failed+=f;total+=t;errors.extend(d.get('errors',[]))
qa={'version':'0.38.0','htmlSha256':html_sha,'passed':passed,'failed':failed,'total':total,'errors':errors,'sameHtml':all(s['sameHtml'] for s in suites),'suites':suites,'cloudCoordinates':5884,'storedPbf':4557,'officialEmpty':1327,'cloudBytes':86973739,'localPackValid':0,'officialTerrainMacros':0}
(vr/'QA_GLOBAL_V038.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
# Manifest after all reports exist.
manifest=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name!='MANIFEST_SHA256.json':manifest.append({'path':p.relative_to(ROOT).as_posix(),'size':p.stat().st_size,'sha256':sha(p)})
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps({'version':'0.38.0','files':manifest},ensure_ascii=False,indent=2)+'\n')
# Curated runnable package.
game_rel=[
 'START_HERE.txt','JOUER_FALLOUT_MISTRAL_v0.38.html','index.html','manifest.webmanifest','sw.js','README_FR.md','package.json','requirements-dev.txt','MANIFEST_SHA256.json',
 'LANCER_JEU.bat','LANCER_JEU.sh','LANCER_APP_WINDOWS.bat','LANCER_APP_LINUX.sh','LANCER_APP_MAC.command',
 'INSTALLER_CARTE_REELLE_WINDOWS.bat','INSTALLER_CARTE_REELLE_RELAIS_WINDOWS.bat','INSTALLER_CARTE_REELLE_LINUX_MAC.sh','AUDITER_CARTE_REELLE_WINDOWS.bat','AUDITER_CARTE_REELLE_LINUX_MAC.sh',
 'RAPPORT_VISUEL_V0.38.png','RAPPORT_VISUEL_V0.38.html','icons/mistral-192.png','icons/mistral-512.png',
 'tools/serve_game.py','tools/install_real_map_v038.py','tools/audit_real_map_v038.py','tools/mvt_audit_v036.py','tools/terrain_real_v036.py',
 'data/map_pack/manifest_v038.json','data/map_pack/manifest_v038.compact.json','data/map_pack/manifest_v038_report.json',
 'verification/AUDIT_CARTE_REELLE_V038.json','verification/AUDIT_CARTE_REELLE_V038.html','verification/CACHE_CLOUD_V038.json','verification/SOURCES_OFFICIELLES_V038.json','verification/SECURITE_CACHE_V038.json','verification/QA_GLOBAL_V038.json','verification/CAPTURES_V038.json'
]
for p in sorted((ROOT/'docs').glob('*V0.38*')):game_rel.append(p.relative_to(ROOT).as_posix())
for name in ['RAPPORT_QA.md','STATUT_PRODUCTION.md']:game_rel.append('docs/'+name)
for p in sorted(vr.glob('v038_*.png')):game_rel.append(p.relative_to(ROOT).as_posix())
missing=[x for x in game_rel if not (ROOT/x).exists()]
if missing:raise SystemExit('Missing game package files: '+repr(missing))
for z in [GAME,PROJECT]:z.unlink(missing_ok=True)
with zipfile.ZipFile(GAME,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for rel in sorted(set(game_rel)):z.write(ROOT/rel,rel)
with zipfile.ZipFile(PROJECT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,(Path(ROOT.name)/p.relative_to(ROOT)).as_posix())
checks=[]
def ck(name,condition,detail=None):checks.append({'name':name,'ok':bool(condition),'detail':detail});
for label,zp,prefix in [('game',GAME,''),('project',PROJECT,ROOT.name+'/')]:
 with zipfile.ZipFile(zp) as z:
  bad=z.testzip();ck(f'{label} CRC',bad is None,bad);ck(f'{label} safe paths',all(safe(n) for n in z.namelist()))
  target=prefix+'JOUER_FALLOUT_MISTRAL_v0.38.html';ck(f'{label} HTML present',target in z.namelist());ck(f'{label} HTML identical',hashlib.sha256(z.read(target)).hexdigest()==html_sha)
# Extract full project, rebuild and validate manifest.
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(PROJECT) as z:z.extractall(td)
 extracted=Path(td)/ROOT.name;pr=subprocess.run([sys.executable,str(extracted/'tools/build_single.py')],cwd=extracted,capture_output=True,text=True);ck('project rebuild exit',pr.returncode==0,pr.stderr[-1000:]);ck('project rebuild byte-identical',sha(extracted/'JOUER_FALLOUT_MISTRAL_v0.38.html')==html_sha);nd=subprocess.run(['node','--check',str(extracted/'src/game.js')],capture_output=True,text=True);ck('project JavaScript syntax',nd.returncode==0,nd.stderr)
 man=json.loads((extracted/'MANIFEST_SHA256.json').read_text());bad=[]
 for item in man['files']:
  p=extracted/item['path']
  if not p.exists() or sha(p)!=item['sha256']:bad.append(item['path'])
 ck('project manifest integrity',not bad,bad[:20])
# Browser smoke from extracted game ZIP.
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(GAME) as z:z.extractall(td)
 html=(Path(td)/'JOUER_FALLOUT_MISTRAL_v0.38.html').read_text();errs=[]
 with sync_playwright() as pw:
  exe='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None
  b=pw.chromium.launch(executable_path=exe,args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errs.append(str(e)));p.set_content(html,wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=30000);text=p.locator('body').inner_text();ck('game ZIP browser loads','CADASTRE COMPLET' in text or 'Cartographie réelle' in text or 'cadastre complet' in p.title().lower(),text[:500]);ck('game ZIP no JavaScript exception',not errs,errs);b.close()
# Static contracts.
ck('index identical',sha(ROOT/'index.html')==html_sha);sw=(ROOT/'sw.js').read_text();ck('service worker v038',"fallout-mistral-v038-1" in sw and 'JOUER_FALLOUT_MISTRAL_v0.38.html' in sw);wm=json.loads((ROOT/'manifest.webmanifest').read_text());ck('PWA manifest cadastre','Cadastre complet' in wm['name'])
ck('QA 113/113',passed==113 and failed==0 and not errors,qa)
audit=json.loads((vr/'AUDIT_CARTE_REELLE_V038.json').read_text());ck('local ZIP audit truthful',audit['valid']==0 and audit['missing']==5884,audit)
cloud=json.loads((vr/'CACHE_CLOUD_V038.json').read_text());ck('cloud cache complete',cloud['complete'] and cloud['cache']['totalCoordinates']==5884 and cloud['cache']['totalStoredPbf']==4557 and cloud['cache']['totalOfficialEmpty']==1327,cloud['cache'])
src=json.loads((vr/'SOURCES_OFFICIELLES_V038.json').read_text());ck('terrain truthful',src['sources']['terrain']['numericFilesBundled']==0,src['sources']['terrain'])
report={'version':'0.38.0','htmlSha256':html_sha,'passed':sum(c['ok'] for c in checks),'total':len(checks),'checks':checks,'artifacts':{p.name:{'size':p.stat().st_size,'sha256':sha(p)} for p in [HTML,GAME,PROJECT,ROOT/'RAPPORT_VISUEL_V0.38.png',ROOT/'RAPPORT_VISUEL_V0.38.html']}}
if report['passed']!=report['total']:
 for c in checks:
  if not c['ok']:print('FAIL',c)
 raise SystemExit('delivery validation failed')
DELIVERY.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=[f'{sha(p)}  {p.name}  {p.stat().st_size}' for p in [HTML,GAME,PROJECT,ROOT/'RAPPORT_VISUEL_V0.38.png',ROOT/'RAPPORT_VISUEL_V0.38.html',DELIVERY,vr/'QA_GLOBAL_V038.json']];CHECKS.write_text('\n'.join(lines)+'\n')
print(json.dumps({'qa':f'{passed}/{total}','delivery':str(report['passed'])+'/'+str(report['total']),'game':report['artifacts'][GAME.name],'project':report['artifacts'][PROJECT.name]},ensure_ascii=False,indent=2))
