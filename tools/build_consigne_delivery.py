"""Rebuild this incremental delivery from the byte-verified gestures ZIP.
The complete repository uses tools/build_single.py; this standalone assembler
only replaces the two exact source modules and inserts the two new ones.
All unrelated HTML/JavaScript and the original service worker are preserved.
"""
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json,re
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base',type=Path,required=True)
p.add_argument('--check',action='store_true')
a=p.parse_args();root=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
expected='8b90aea815826c0442c9742b6279c144043b1db99ef954d967621a054713e677'
with ZipFile(a.base) as z:
    oldhtml=z.read('index.html');oldgame=z.read('src/game.js').decode();sw=z.read('sw.js').decode()
    assert sha(oldhtml)==expected, 'Wrong baseline HTML: refusing an unverified overwrite'
    assert oldhtml==z.read('JOUER_FALLOUT_MISTRAL_v0.50.html')
    js=oldgame
    for name in ['src/v050/10u_gabians_runtime.js','src/v050/10x_consigne_gestes.js']:
        before=z.read(name).decode();after=(root/name).read_text()
        assert js.count(before)==1,(name,'source not unique in baseline')
        if '10x_' in name:
            after+='\n'+(root/'src/v050/10y_consigne_vie.js').read_text()+'\n'+(root/'src/v050/10z_consigne_vie_runtime.js').read_text()
        js=js.replace(before,after,1)
    html=oldhtml.decode()
    assert html.count(oldgame)==1, 'Baseline script not unique in HTML'
    html=html.replace(oldgame,js,1).encode()
    sw=re.sub(r"const CACHE='[^']+';","const CACHE='fallout-mistral-v050-"+sha(html)[:16]+"';",sw,count=1).encode()
    outputs={'src/game.js':js.encode(),'index.html':html,'JOUER_FALLOUT_MISTRAL_v0.50.html':html,'sw.js':sw}
    for name,content in outputs.items():
        if a.check:assert (root/name).read_bytes()==content,'Stale output: '+name
        else:(root/name).write_bytes(content)
    print(json.dumps({'baseline_html_sha256':expected,'method':'verified incremental source replacement, not a full-repository rebuild','outputs':{n:sha(v) for n,v in outputs.items()},'check':a.check},indent=2))
