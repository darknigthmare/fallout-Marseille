from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('/workspace/fallout-Marseille')
base=Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((base/'FROZEN_INPUTS.json').read_text())
assert all(sha(root/p)==h for p,h in expected.items())
rebuilt=base/'rebuild-final'
rebuilt.mkdir(exist_ok=False)
shutil.copytree(root/'src',rebuilt/'src',ignore=shutil.ignore_patterns('__pycache__'))
(rebuilt/'tools').mkdir()
shutil.copy2(root/'tools/build_single.py',rebuilt/'tools/build_single.py')
p=subprocess.run([sys.executable,'tools/build_single.py'],cwd=rebuilt,capture_output=True,text=True)
rows=[{'path':name,'same':(root/name).read_bytes()==(rebuilt/name).read_bytes(),'sourceSha256':sha(root/name),'rebuiltSha256':sha(rebuilt/name)} for name in ['index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js']]
(base/'REPRODUCIBLE_BUILD.json').write_text(json.dumps({'scope':'Fresh source-only reconstruction, three exact byte comparisons.','exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'html_sha256':expected['index.html'],'files':rows},indent=2)+'\n')
assert p.returncode==0 and all(r['same'] for r in rows)
game=base/'legacy-game'
for name in ['src','tools','tests','icons','docs']:
 shutil.copytree(root/name,game/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','v050-legacy-*'))
for name in ['index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','sw.js']:
 shutil.copy2(root/name,game/name)
for name in ['enrichment','enrichment_archives','landmark_surfaces']:
 shutil.copytree(root/'data/map_pack'/name,game/'data/map_pack'/name,dirs_exist_ok=True)
shutil.rmtree(game/'verification/v050/legacy',ignore_errors=True)
(game/'verification/v050/legacy').mkdir(parents=True)
q=game/'verification/v050/QA_LEGACY.json'
if q.exists():q.unlink()
out=base/'legacy-final';out.mkdir(exist_ok=True)
original=Path('/workspace/.cloud-setup/fallout-marseille/next-expansion/legacy-final/run_legacy_audit.py').read_text()
original=original.replace("BASE = Path('/workspace/.cloud-setup/fallout-marseille/next-expansion')", "BASE = Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion')")
original=original.replace("EXPECTED = 'ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670'",'EXPECTED = '+repr(expected['index.html']))
(out/'run_legacy_audit.py').write_text(original)
shutil.copy2('/workspace/.cloud-setup/fallout-marseille/next-expansion/check_runtime_closure.py',base/'check_runtime_closure.py')
print(json.dumps({'rebuild':all(r['same'] for r in rows),'html':expected['index.html'],'legacyCopyPrepared':True,'rootInputsUnchanged':all(sha(root/p)==h for p,h in expected.items())}))
