#!/usr/bin/env python3
from pathlib import Path, PurePosixPath
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
import zipfile, tempfile, subprocess, hashlib, json, shutil

R=Path(__file__).resolve().parents[1]
OUT=R.parent
GAME=OUT/'FALLOUT_MISTRAL_v0.35_JEU_SEUL.zip'
PROJECT=OUT/'FALLOUT_MISTRAL_v0.35_PROJET_COMPLET.zip'
REPORT=OUT/'FALLOUT_MISTRAL_v0.35_CONTROLES_LIVRAISON.json'
HTML=R/'JOUER_FALLOUT_MISTRAL_v0.35.html'
release_hash=hashlib.sha256(HTML.read_bytes()).hexdigest()
rows=[]

def ck(name, cond, detail=None):
    rows.append({'test':name,'pass':bool(cond),'detail':detail})
    print(('OK ' if cond else 'FAIL ')+name, flush=True)
    if not cond: raise RuntimeError(f'{name}: {detail}')

def safe_names(names):
    bad=[]
    for name in names:
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name:bad.append(name)
    return bad

for label,zp,prefix in [('jeu',GAME,''),('projet',PROJECT,f'{R.name}/')]:
    with zipfile.ZipFile(zp) as z:
        ck(f'{label} : CRC',z.testzip() is None)
        bad=safe_names(z.namelist());ck(f'{label} : chemins sûrs',not bad,bad[:10])
        member=prefix+'JOUER_FALLOUT_MISTRAL_v0.35.html'
        ck(f'{label} : HTML présent',member in z.namelist(),member)
        ck(f'{label} : HTML identique',hashlib.sha256(z.read(member)).hexdigest()==release_hash)

# Player manifest validation.
with zipfile.ZipFile(GAME) as z:
    manifest=json.loads(z.read('MANIFEST_JEU_SHA256.json'))
    issues=[]
    for f in manifest['files']:
        if f['path'] not in z.namelist():issues.append(f"missing:{f['path']}")
        elif hashlib.sha256(z.read(f['path'])).hexdigest()!=f['sha256']:issues.append(f"hash:{f['path']}")
    ck('jeu : manifeste complet',not issues,issues[:10])

# Project manifest and byte-identical rebuild from the extracted source package.
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    with zipfile.ZipFile(PROJECT) as z:z.extractall(td)
    X=td/R.name
    manifest=json.loads((X/'MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    issues=[]
    for f in manifest['files']:
        p=X/f['path']
        if not p.exists():issues.append(f"missing:{f['path']}")
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:issues.append(f"hash:{f['path']}")
    ck('projet : manifeste complet',not issues,issues[:10])
    before=hashlib.sha256((X/'JOUER_FALLOUT_MISTRAL_v0.35.html').read_bytes()).hexdigest()
    run=subprocess.run(['python3','tools/build_single.py'],cwd=X,text=True,capture_output=True,timeout=120)
    ck('projet : reconstruction réussie',run.returncode==0,run.stderr[-1000:])
    after=hashlib.sha256((X/'JOUER_FALLOUT_MISTRAL_v0.35.html').read_bytes()).hexdigest()
    ck('projet : reconstruction byte-identique',before==after==release_hash,{'before':before,'after':after,'release':release_hash})
    node=subprocess.run(['node','--check','src/game.js'],cwd=X,text=True,capture_output=True,timeout=60)
    ck('projet : JavaScript valide',node.returncode==0,node.stderr[-1000:])

# Browser smoke on the exact HTML read back from the player ZIP. set_content is
# used because local-file and localhost navigation are restricted here.
with zipfile.ZipFile(GAME) as z:html=z.read('JOUER_FALLOUT_MISTRAL_v0.35.html').decode('utf-8')
errors=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html,wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=30000)
    ck('ZIP jeu : menu chargé',p.locator('#btnV035Career').count()==1 and p.locator('#btnV035Load').count()==1)
    p.click('#btnV035Career');p.locator('#v035Screen:not(.hidden)').wait_for(timeout=5000);ck('ZIP jeu : carrière ouvrable','Carrière' in p.locator('#v035Screen').inner_text())
    p.click('[data-v35="saves"]');ck('ZIP jeu : sauvegardes ouvrables','Trois emplacements manuels' in p.locator('#v035Screen').inner_text())
    ck('ZIP jeu : aucune exception JavaScript',not errors,errors)
    b.close()

summary={
 'version':'0.35.0','pass':all(r['pass'] for r in rows),'passed':sum(r['pass'] for r in rows),'total':len(rows),
 'html':{'bytes':HTML.stat().st_size,'sha256':release_hash},
 'game_zip':{'bytes':GAME.stat().st_size,'sha256':hashlib.sha256(GAME.read_bytes()).hexdigest()},
 'project_zip':{'bytes':PROJECT.stat().st_size,'sha256':hashlib.sha256(PROJECT.read_bytes()).hexdigest()},
 'checks':rows,
 'note':'Live localhost PWA registration was not executed because localhost navigation is blocked in this environment; its static distribution contract is covered by QA_V035_PWA.json.'
}
REPORT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checksum=OUT/'FALLOUT_MISTRAL_v0.35_CHECKSUMS.txt'
files=[HTML,GAME,PROJECT,R/'RAPPORT_VISUEL_V0.35.png',R/'RAPPORT_VISUEL_V0.35.html',REPORT]
checksum.write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}  {p.stat().st_size}' for p in files)+'\n',encoding='utf-8')
print('FINAL',summary['passed'],summary['total'],summary['pass'])
