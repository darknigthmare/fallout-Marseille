#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile,tempfile,subprocess,sys,shutil,os
R=Path(__file__).resolve().parents[1]
OUT=R.parent
GAME=OUT/'FALLOUT_MISTRAL_v0.40_JEU_SEUL.zip'
PROJ=OUT/'FALLOUT_MISTRAL_v0.40_PROJET_COMPLET.zip'
CONTROLS=OUT/'FALLOUT_MISTRAL_v0.40_CONTROLES_LIVRAISON.json'
CHECKS=OUT/'FALLOUT_MISTRAL_v0.40_CHECKSUMS.txt'
HTML=R/'JOUER_FALLOUT_MISTRAL_v0.40.html'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe_member(name):
 p=Path(name);return not p.is_absolute() and '..' not in p.parts and '\\' not in name
# project manifest
entries=[]
for p in sorted(x for x in R.rglob('*') if x.is_file() and x.name!='MANIFEST_SHA256.json'):
 entries.append({'path':p.relative_to(R).as_posix(),'size':p.stat().st_size,'sha256':sha(p)})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'version':'0.40.0','files':entries},ensure_ascii=False,indent=2)+'\n')
# curated playable package
rels=[
 'JOUER_FALLOUT_MISTRAL_v0.40.html','index.html','LANCER_JEU.bat','LANCER_JEU.sh','LANCER_APP_WINDOWS.bat','LANCER_APP_LINUX.sh','LANCER_APP_MAC.command','START_HERE.txt','README_FR.md','manifest.webmanifest','sw.js','requirements-dev.txt','RAPPORT_VISUEL_V0.40.png','RAPPORT_VISUEL_V0.40.html','MANIFEST_SHA256.json',
 'AUDITER_CARTE_REELLE_LINUX_MAC.sh','AUDITER_CARTE_REELLE_WINDOWS.bat','INSTALLER_CARTE_REELLE_LINUX_MAC.sh','INSTALLER_CARTE_REELLE_RELAIS_WINDOWS.bat','INSTALLER_CARTE_REELLE_WINDOWS.bat',
 'icons/mistral-192.png','icons/mistral-512.png',
 'data/corridors/aubagne_marseille.json','data/corridors/aubagne_laciotat.json','data/map_pack/manifest_v038.json','data/map_pack/manifest_v038.compact.json','data/map_pack/manifest_v038_report.json','data/map_pack/install_v039_summary.json','data/map_pack/terrain/manifest_v039.json','data/map_pack/terrain/terrain_plan_v036.json',
 'tools/serve_game.py','tools/install_real_map_v039.py','tools/audit_real_map_v039.py','tools/install_terrain_v039.py','tools/audit_terrain_v039.py','tools/mvt_audit_v036.py','tools/audit_corridors_v040.py',
 'docs/CONTENU_V0.40.md','docs/ARCHITECTURE_V0.40.md','docs/KNOWN_LIMITATIONS_V0.40.md','docs/RELEASE_NOTES_V0.40.md','docs/INSTALLATION_CARTE_REELLE_V0.40.md','docs/LICENCES_CARTOGRAPHIQUES_V0.40.md','docs/RAPPORT_QA.md','docs/RAPPORT_VISUEL_V0.40.md','docs/STATUT_PRODUCTION.md','docs/MIGRATION_V039_V040.md',
 'verification/CORRIDORS_CLOUD_V040.json','verification/SECURITE_CORRIDORS_V040.json','verification/AUDIT_CORRIDORS_V040.json','verification/AUDIT_CORRIDORS_V040.html','verification/QA_GLOBAL_V040.json','verification/QA_V040.json','verification/QA_CLOUD_PROOF_V040.json','verification/CAPTURES_V040.json','verification/TERRAIN_CLOUD_V039.json','verification/SOURCES_OFFICIELLES_V039.json','verification/SECURITE_TERRAIN_V039.json'
]
rels += [p.relative_to(R).as_posix() for p in sorted((R/'verification').glob('v040_*.png'))]
missing=[r for r in rels if not (R/r).exists()]
if missing:raise SystemExit('missing game files: '+repr(missing))
game_manifest=[{'path':r,'size':(R/r).stat().st_size,'sha256':sha(R/r)} for r in rels]
for p in (GAME,PROJ,CHECKS,CONTROLS):
 if p.exists():p.unlink()
with zipfile.ZipFile(GAME,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for r in sorted(set(rels)):z.write(R/r,arcname=r)
 z.writestr('MANIFEST_JEU_SHA256.json',json.dumps({'version':'0.40.0','files':game_manifest},ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(PROJ,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(x for x in R.rglob('*') if x.is_file()):z.write(p,arcname=f'{R.name}/{p.relative_to(R).as_posix()}')
controls={'version':'0.40.0','checks':[]}
def ck(name,cond,detail=None):controls['checks'].append({'name':name,'ok':bool(cond),'detail':detail});print(('OK ' if cond else 'FAIL ')+name);return bool(cond)
html_sha=sha(HTML)
for label,zp,prefix in [('jeu',GAME,''),('projet',PROJ,f'{R.name}/')]:
 with zipfile.ZipFile(zp) as z:
  ck(f'CRC {label}',z.testzip() is None,z.testzip())
  ck(f'chemins sûrs {label}',all(safe_member(n) for n in z.namelist()))
  member=prefix+HTML.name;ck(f'HTML présent {label}',member in z.namelist());ck(f'HTML identique {label}',hashlib.sha256(z.read(member)).hexdigest()==html_sha)
# verify project manifest
manifest=json.loads((R/'MANIFEST_SHA256.json').read_text());bad=[]
for e in manifest['files']:
 p=R/e['path']
 if not p.exists() or p.stat().st_size!=e['size'] or sha(p)!=e['sha256']:bad.append(e['path'])
ck('manifeste projet exact',not bad,bad[:10])
# exact rebuild from extracted project
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(PROJ) as z:z.extractall(td)
 E=Path(td)/R.name
 before=sha(E/HTML.name)
 r=subprocess.run([sys.executable,'tools/build_single.py'],cwd=E,capture_output=True,text=True,timeout=180)
 ck('reconstruction projet',r.returncode==0,(r.stdout+r.stderr)[-1000:])
 ck('reconstruction byte-identique',sha(E/HTML.name)==before==html_sha,{'before':before,'after':sha(E/HTML.name)})
 node=subprocess.run(['node','--check','src/game.js'],cwd=E,capture_output=True,text=True,timeout=60)
 ck('syntaxe JavaScript extraite',node.returncode==0,node.stderr[-500:])
# game manifest and PWA contract
with tempfile.TemporaryDirectory() as td:
 with zipfile.ZipFile(GAME) as z:z.extractall(td)
 E=Path(td);gm=json.loads((E/'MANIFEST_JEU_SHA256.json').read_text());bad=[]
 for e in gm['files']:
  p=E/e['path']
  if not p.exists() or p.stat().st_size!=e['size'] or sha(p)!=e['sha256']:bad.append(e['path'])
 ck('manifeste jeu exact',not bad,bad[:10])
 sw=(E/'sw.js').read_text();ck('PWA v0.40',"fallout-mistral-v040-1" in sw and 'JOUER_FALLOUT_MISTRAL_v0.40.html' in sw and 'aubagne_marseille.json' in sw)
 audit=subprocess.run([sys.executable,'tools/audit_corridors_v040.py'],cwd=E,capture_output=True,text=True,timeout=60)
 ck('audit corridors du ZIP compact',audit.returncode==0,audit.stdout[-500:])
# browser smoke on extracted game
try:
 from playwright.sync_api import sync_playwright
 sys.path.insert(0,str(R/'tools'));from qa_support import chromium_path
 with tempfile.TemporaryDirectory() as td:
  with zipfile.ZipFile(GAME) as z:z.extractall(td)
  h=(Path(td)/HTML.name).read_text()
  with sync_playwright() as pw:
   b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});errs=[];p.on('pageerror',lambda e:errs.append(str(e)));p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort());p.set_content(h,wait_until='load');p.wait_for_timeout(650);ck('jeu extrait charge',p.title().startswith('Fallout : Mistral · v0.40'));ck('surface v0.40 disponible',p.evaluate("typeof __MISTRAL_DEBUG.v040Info")=='function');info=p.evaluate('__MISTRAL_DEBUG.v040Info()');ck('deux preuves embarquées',len(info['corridors']['rows'])==2 and all(x['status']=='certified' for x in info['corridors']['rows']),info['corridors']['rows']);ck('aucune exception au smoke',not errs,errs);b.close()
except Exception as e:ck('browser smoke exécuté',False,repr(e))
controls['passed']=sum(x['ok'] for x in controls['checks']);controls['failed']=sum(not x['ok'] for x in controls['checks']);controls['total']=len(controls['checks']);controls['html_sha256']=html_sha;controls['artifacts']={p.name:{'size':p.stat().st_size,'sha256':sha(p)} for p in [HTML,R/'RAPPORT_VISUEL_V0.40.png',GAME,PROJ]}
CONTROLS.write_text(json.dumps(controls,ensure_ascii=False,indent=2)+'\n')
items=[HTML,R/'RAPPORT_VISUEL_V0.40.png',R/'RAPPORT_VISUEL_V0.40.html',GAME,PROJ,CONTROLS,R/'verification/QA_GLOBAL_V040.json']
CHECKS.write_text('\n'.join(f'{sha(p)}  {p.name}  {p.stat().st_size}' for p in items)+'\n')
print(json.dumps({'passed':controls['passed'],'failed':controls['failed'],'total':controls['total'],'game':GAME.stat().st_size,'project':PROJ.stat().st_size},ensure_ascii=False))
raise SystemExit(bool(controls['failed']))
