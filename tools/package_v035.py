#!/usr/bin/env python3
from pathlib import Path
import zipfile, hashlib, json

R=Path(__file__).resolve().parents[1]
OUT=R.parent
GAME=OUT/'FALLOUT_MISTRAL_v0.35_JEU_SEUL.zip'
PROJECT=OUT/'FALLOUT_MISTRAL_v0.35_PROJET_COMPLET.zip'

# Project manifest is generated from the exact tree before packaging.
entries=[]
for p in sorted(R.rglob('*')):
    if not p.is_file() or p.name in {'MANIFEST_SHA256.json'}:
        continue
    entries.append({'path':p.relative_to(R).as_posix(),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'version':'0.35.0','files':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Player package: runnable application, documentation, visual evidence and QA summary.
game_files=[
 'JOUER_FALLOUT_MISTRAL_v0.35.html','index.html','manifest.webmanifest','sw.js',
 'icons/mistral-192.png','icons/mistral-512.png',
 'LANCER_JEU.bat','LANCER_JEU.sh','LANCER_APP_WINDOWS.bat','LANCER_APP_LINUX.sh','LANCER_APP_MAC.command',
 'tools/serve_game.py','README_FR.md','START_HERE.txt','RAPPORT_VISUEL_V0.35.png','RAPPORT_VISUEL_V0.35.html',
 'docs/CONTENU_V0.35.md','docs/RAPPORT_QA.md','docs/STATUT_PRODUCTION.md','docs/MIGRATION_V030_V035.md',
 'docs/ARCHITECTURE_V0.35.md','docs/ROADMAP_COMMERCIAL.md','docs/RAPPORT_VISUEL_V0.35.md',
 'docs/RELEASE_NOTES_V0.35.md','docs/KNOWN_LIMITATIONS_V0.35.md',
 'verification/QA_GLOBAL_V035.json','verification/CAPTURES_V035.json',
]
game_files += [p.relative_to(R).as_posix() for p in sorted((R/'verification').glob('v035_*.png'))]
missing=[rel for rel in game_files if not (R/rel).exists()]
if missing: raise SystemExit(f'Missing game files: {missing}')
game_manifest=[]
for rel in game_files:
    p=R/rel;game_manifest.append({'path':rel,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest_bytes=(json.dumps({'version':'0.35.0','files':game_manifest},ensure_ascii=False,indent=2)+'\n').encode()

for target in (GAME,PROJECT):
    target.unlink(missing_ok=True)
with zipfile.ZipFile(GAME,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for rel in game_files:z.write(R/rel,arcname=rel)
    z.writestr('MANIFEST_JEU_SHA256.json',manifest_bytes)
with zipfile.ZipFile(PROJECT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(R.rglob('*')):
        if p.is_file():z.write(p,arcname=f'{R.name}/{p.relative_to(R).as_posix()}')
print(GAME, GAME.stat().st_size, hashlib.sha256(GAME.read_bytes()).hexdigest())
print(PROJECT, PROJECT.stat().st_size, hashlib.sha256(PROJECT.read_bytes()).hexdigest())
