#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path,PurePosixPath
import hashlib,json,zipfile,tempfile,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
GAME=OUT/'FALLOUT_MISTRAL_v0.37_JEU_SEUL.zip'
PROJECT=OUT/'FALLOUT_MISTRAL_v0.37_PROJET_COMPLET.zip'
CHECKS=OUT/'FALLOUT_MISTRAL_v0.37_CHECKSUMS.txt'
DELIVERY=OUT/'FALLOUT_MISTRAL_v0.37_CONTROLES_LIVRAISON.json'
HTML=ROOT/'JOUER_FALLOUT_MISTRAL_v0.37.html'

def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(name:str):
 p=PurePosixPath(name);return not p.is_absolute() and '..' not in p.parts and not any(part in ('','.') for part in p.parts)
# Exact QA aggregation after final rerun.
vr=ROOT/'verification';html_sha=sha(HTML)
reports=['QA_V037.json','QA_MAP_TOOLS_V037.json','QA_REGRESSION_V035_ON_V037.json','QA_REGRESSION_V035_PRODUCT_ON_V037.json','QA_REGRESSION_V035_PROLOGUE_ON_V037.json']
suites=[];passed=failed=total=0;errors=[]
for name in reports:
 d=json.loads((vr/name).read_text(encoding='utf-8'));p=int(d.get('passed',0));f=int(d.get('failed',0));t=int(d.get('total',p+f));h=d.get('html_sha256');suites.append({'file':name,'passed':p,'failed':f,'total':t,'sameHtml':not h or h==html_sha});passed+=p;failed+=f;total+=t;errors.extend(d.get('errors',[]))
qa={'version':'0.37.0','htmlSha256':html_sha,'passed':passed,'failed':failed,'total':total,'errors':errors,'sameHtml':all(s['sameHtml'] for s in suites),'suites':suites,'cloudCacheVerifiedTiles':368,'cloudBaseTiles':367,'cloudCadastreTiles':1,'localPackValidTiles':0,'officialTerrainMacros':0,'scope':'Exact final HTML for browser suites; controlled local MVT fixtures for installer/auditor QA; live official source/cache evidence stored separately.'}
(vr/'QA_GLOBAL_V037.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Final project manifest.
manifest=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name!='MANIFEST_SHA256.json':manifest.append({'path':p.relative_to(ROOT).as_posix(),'size':p.stat().st_size,'sha256':sha(p)})
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps({'version':'0.37.0','files':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Curated runnable package, including map install/audit tools.
game_rel=[
 'START_HERE.txt','JOUER_FALLOUT_MISTRAL_v0.37.html','index.html','manifest.webmanifest','sw.js','README_FR.md','package.json','requirements-dev.txt','MANIFEST_SHA256.json',
 'LANCER_JEU.bat','LANCER_JEU.sh','LANCER_APP_WINDOWS.bat','LANCER_APP_LINUX.sh','LANCER_APP_MAC.command',
 'INSTALLER_CARTE_REELLE_WINDOWS.bat','INSTALLER_CARTE_REELLE_RELAIS_WINDOWS.bat','INSTALLER_CARTE_REELLE_LINUX_MAC.sh','AUDITER_CARTE_REELLE_WINDOWS.bat','AUDITER_CARTE_REELLE_LINUX_MAC.sh',
 'RAPPORT_VISUEL_V0.37.png','RAPPORT_VISUEL_V0.37.html',
 'icons/mistral-192.png','icons/mistral-512.png',
 'tools/serve_game.py','tools/install_real_map_v037.py','tools/audit_real_map_v037.py','tools/mvt_audit_v036.py','tools/terrain_real_v036.py',
 'data/map_pack/manifest_v037.json','data/map_pack/manifest_v037.compact.json','data/map_pack/manifest_v037_report.json',
 'verification/AUDIT_CARTE_REELLE_V037.json','verification/AUDIT_CARTE_REELLE_V037.html','verification/INSTALLATION_DRY_RUN_V037.txt','verification/CACHE_CLOUD_V037.json','verification/SOURCES_OFFICIELLES_V037.json','verification/SECURITE_CACHE_V037.json','verification/QA_GLOBAL_V037.json','verification/CAPTURES_V037.json'
]
for p in sorted((ROOT/'docs').glob('*V0.37*')):game_rel.append(p.relative_to(ROOT).as_posix())
for name in ['RAPPORT_QA.md','STATUT_PRODUCTION.md']:game_rel.append('docs/'+name)
for p in sorted((ROOT/'verification').glob('v037_*.png')):game_rel.append(p.relative_to(ROOT).as_posix())
missing=[rel for rel in game_rel if not (ROOT/rel).exists()]
if missing:raise SystemExit(f'Missing game package files: {missing}')
for z in [GAME,PROJECT]:z.unlink(missing_ok=True)
with zipfile.ZipFile(GAME,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for rel in sorted(set(game_rel)):z.write(ROOT/rel,rel)
with zipfile.ZipFile(PROJECT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,(Path(ROOT.name)/p.relative_to(ROOT)).as_posix())
checks=[]
def ck(name,condition,detail=None):
 checks.append({'name':name,'ok':bool(condition),'detail':detail});
 if not condition:raise RuntimeError(f'{name}: {detail}')
for label,zp,prefix in [('game',GAME,''),('project',PROJECT,ROOT.name+'/')]:
 with zipfile.ZipFile(zp) as z:
  ck(f'{label} CRC',z.testzip() is None,z.testzip())
  ck(f'{label} safe paths',all(safe(n) for n in z.namelist()))
  target=prefix+'JOUER_FALLOUT_MISTRAL_v0.37.html';ck(f'{label} HTML present',target in z.namelist());ck(f'{label} HTML identical',hashlib.sha256(z.read(target)).hexdigest()==html_sha)
# Extract and rebuild full project.
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(PROJECT) as z:z.extractall(td)
 extracted=Path(td)/ROOT.name
 proc=subprocess.run([sys.executable,str(extracted/'tools/build_single.py')],cwd=extracted,capture_output=True,text=True)
 ck('project rebuild exit',proc.returncode==0,proc.stderr[-1500:])
 ck('project rebuild byte-identical',sha(extracted/'JOUER_FALLOUT_MISTRAL_v0.37.html')==html_sha,sha(extracted/'JOUER_FALLOUT_MISTRAL_v0.37.html'))
 node=subprocess.run(['node','--check',str(extracted/'src/game.js')],capture_output=True,text=True);ck('project JavaScript syntax',node.returncode==0,node.stderr)
 # project manifest integrity after extraction (before rebuild only source-generated outputs are deterministic; rebuild is identical)
 man=json.loads((extracted/'MANIFEST_SHA256.json').read_text());bad=[]
 for item in man['files']:
  p=extracted/item['path']
  if not p.exists() or sha(p)!=item['sha256']:bad.append(item['path'])
 ck('project manifest integrity',not bad,bad[:20])
# Game manifest subset and static PWA contracts.
ck('index identical',sha(ROOT/'index.html')==html_sha)
sw=(ROOT/'sw.js').read_text();ck('service worker v037',"fallout-mistral-v037-1" in sw and 'JOUER_FALLOUT_MISTRAL_v0.37.html' in sw)
wm=json.loads((ROOT/'manifest.webmanifest').read_text());ck('PWA manifest cache territory','Cache territorial' in wm['name'])
ck('QA 102/102',passed==102 and failed==0 and not errors,qa)
ck('local audit truthful',json.loads((vr/'AUDIT_CARTE_REELLE_V037.json').read_text())['valid']==0)
ck('cloud cache truthful',json.loads((vr/'CACHE_CLOUD_V037.json').read_text())['cache']['totalTiles']==368)
ck('terrain truthful',json.loads((vr/'SOURCES_OFFICIELLES_V037.json').read_text())['sources']['terrain']['numericFilesBundled']==0)
report={'version':'0.37.0','htmlSha256':html_sha,'passed':sum(c['ok'] for c in checks),'total':len(checks),'checks':checks,'artifacts':{p.name:{'size':p.stat().st_size,'sha256':sha(p)} for p in [HTML,GAME,PROJECT,ROOT/'RAPPORT_VISUEL_V0.37.png',ROOT/'RAPPORT_VISUEL_V0.37.html']}}
DELIVERY.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=[]
for p in [HTML,GAME,PROJECT,ROOT/'RAPPORT_VISUEL_V0.37.png',ROOT/'RAPPORT_VISUEL_V0.37.html',DELIVERY,vr/'QA_GLOBAL_V037.json']:
 lines.append(f'{sha(p)}  {p.name}  {p.stat().st_size}')
CHECKS.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'qa':f'{passed}/{total}','delivery':f"{report['passed']}/{report['total']}",'game':report['artifacts'][GAME.name],'project':report['artifacts'][PROJECT.name]},ensure_ascii=False,indent=2))
