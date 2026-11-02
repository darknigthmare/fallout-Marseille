#!/usr/bin/env python3
"""Package only after exact-build checks and verified screenshots."""
from pathlib import Path
import json,zipfile,hashlib,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1];OUT=R.parent
q=json.loads((R/'verification/QA_GLOBAL_V029.json').read_text());h=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes()).hexdigest();assert q['html_sha256']==h and q['same_html'] and not q['failed'] and not q['errors']
base=json.loads((R/'data/BASE_V028.json').read_text());assert all(hashlib.sha256((R/'history/v0.28_source'/n).read_bytes()).hexdigest()==v for n,v in base['reference_files'].items())
subprocess.run([sys.executable,str(R/'tools/make_report_v029.py')],check=True,cwd=R);subprocess.run([sys.executable,str(R/'tools/write_docs_v029.py')],check=True,cwd=R)
# Reports/probes of intermediate attempts are not release evidence.
for p in (R/'verification').iterdir():
 if p.name.startswith(('SMOKE','QA_PROBE','QA_CAPTURES'))or p.name in ['qa029world.log','qa029terminal.log','qa029perception.log','regression029.log']:p.unlink(missing_ok=True)
for p in (R/'tools').glob('*.py'):
 if p.name.startswith(('probe','smoke'))or (p.name.startswith(('capture_v','make_report_v','package_v','run_all_qa_v'))and 'v029'not in p.name):p.unlink()
for p in R.rglob('__pycache__'):
 if p.is_dir():shutil.rmtree(p)
# No font files are redistributed.
assert not any(p.suffix.lower()in['.ttf','.otf','.woff','.woff2']for p in R.rglob('*')if p.is_file())
def manifest(root):
 m={str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(root.rglob('*'))if p.is_file()and p.name!='MANIFEST_SHA256.json'}
 (root/'MANIFEST_SHA256.json').write_text(json.dumps({'version':'0.29.0','files':m},ensure_ascii=False,indent=2));return m
def pack(root,path,prefix=''):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,prefix+str(p.relative_to(root)))
 with zipfile.ZipFile(path)as z:assert z.testzip()is None
small=OUT/'_GAME_PACKAGE_V029';shutil.rmtree(small,ignore_errors=True);small.mkdir()
for n in ['JOUER_FALLOUT_MISTRAL_v0.29.html','LANCER_JEU.bat','LANCER_JEU.sh','README_FR.md','RAPPORT_VISUEL_V0.29.html','RAPPORT_VISUEL_V0.29.png','VOLET_AVANT_APRES_V0.29.png']:
 shutil.copy2(R/n,small/n)
for n in ['CONTENU_V0.29.md','RAPPORT_QA.md','STATUT_PRODUCTION.md','MIGRATION_V028_V029.md','CONTROLES.md','SOURCES_ET_CREDITS.md']:
 (small/'docs').mkdir(exist_ok=True);shutil.copy2(R/'docs'/n,small/'docs'/n)
manifest(small);manifest(R)
for root,path,prefix in [(small,OUT/'FALLOUT_MISTRAL_v0.29_JEU_SEUL.zip',''),(R,OUT/'FALLOUT_MISTRAL_v0.29_PROJET_COMPLET.zip',R.name+'/')]:pack(root,path,prefix);print(path,path.stat().st_size)
files=[R/'JOUER_FALLOUT_MISTRAL_v0.29.html',R/'RAPPORT_VISUEL_V0.29.png',OUT/'FALLOUT_MISTRAL_v0.29_JEU_SEUL.zip',OUT/'FALLOUT_MISTRAL_v0.29_PROJET_COMPLET.zip'];lines=[f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}'for p in files];(OUT/'FALLOUT_MISTRAL_v0.29_CHECKSUMS.txt').write_text('\n'.join(lines)+'\n');shutil.rmtree(small)
