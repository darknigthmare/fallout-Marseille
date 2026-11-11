"""Reproduce the local postal pigeon update from the exact validated local gabian delivery.
This is a hash-guarded incremental assembly, NOT a substitute for the repository's
full tools/build_single.py build. Only the four generated output files are written.
"""
from pathlib import Path
import argparse,hashlib,json,re,zipfile
EXPECTED = {'index.html': '7b714e126bcb2e420ecebe16492dd22ca4bbc8871d21e124fa3f505b92561d4c', 'JOUER_FALLOUT_MISTRAL_v0.50.html': '7b714e126bcb2e420ecebe16492dd22ca4bbc8871d21e124fa3f505b92561d4c', 'src/game.js': 'ab20c5630d631219441567ef09b24838aeea3f4895a3d70439b23d9273c31d59', 'sw.js': 'b7f1827b1daa99928801a45dfc2a903205e17055d8015a4a94ca6d212dc78828'}
ROOT=Path(__file__).resolve().parents[1]
MODULES=['src/v050/10v_pigeons_poste.js','src/v050/10w_pigeons_runtime.js']
MARKER='/* Keep the existing six-plate v0.30 simulation and its finite core ledger.'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--baseline',type=Path,required=True,help='Original FALLOUT_MISTRAL_GABIANS_MISE_A_JOUR.zip, not this new ZIP')
 p.add_argument('--output',type=Path,default=ROOT/'build/pigeons')
 p.add_argument('--check',action='store_true',help='Verify without changing existing outputs')
 a=p.parse_args();digest=lambda b:hashlib.sha256(b).hexdigest()
 with zipfile.ZipFile(a.baseline) as z:
  base={}
  for name,expected in EXPECTED.items():
   if z.getinfo(name).file_size>12_000_000:raise ValueError('Unexpected baseline file size: '+name)
   content=z.read(name)
   if digest(content)!=expected:raise ValueError('Baseline SHA-256 mismatch: '+name)
   base[name]=content.decode('utf-8')
 addition='\n'+'\n'.join((ROOT/name).read_text(encoding='utf-8') for name in MODULES)+'\n'
 outputs={}
 for name in ['index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js']:
  if base[name].count(MARKER)!=1:raise ValueError('Ambiguous module boundary: '+name)
  outputs[name]=base[name].replace(MARKER,addition+MARKER).encode('utf-8')
 html_sha=digest(outputs['index.html'])
 outputs['sw.js']=re.sub(r"const CACHE='[^']+'", "const CACHE='fallout-mistral-v050-"+html_sha[:16]+"'",base['sw.js'],count=1).encode('utf-8')
 for name,content in outputs.items():
  target=a.output/name
  if a.check:
   if not target.is_file() or target.read_bytes()!=content:raise ValueError('Generated output differs: '+name)
  else:
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
 print(json.dumps({'method':'verified incremental assembly','html_sha256':html_sha,'checked':a.check,'outputs':{n:digest(b) for n,b in outputs.items()}},indent=2))
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,KeyError,zipfile.BadZipFile) as err:raise SystemExit(str(err))
