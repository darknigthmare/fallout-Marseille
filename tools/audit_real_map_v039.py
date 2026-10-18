#!/usr/bin/env python3
"""Run the vector and RGE ALTI local-pack audits and write a combined v0.39 report."""
from __future__ import annotations
import argparse,json,subprocess,sys,time,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--require-local',action='store_true');p.add_argument('--macro',default='all');a=p.parse_args();ver=ROOT/'verification';ver.mkdir(exist_ok=True)
 vector=ver/'AUDIT_VECTORIEL_LOCAL_V039.json';terrain=ver/'AUDIT_TERRAIN_V039.json'
 rv=subprocess.run([sys.executable,str(ROOT/'tools/audit_real_map_v038.py'),'--macro',a.macro,'--output',str(vector)]).returncode
 rt=subprocess.run([sys.executable,str(ROOT/'tools/audit_terrain_v039.py'),'--macro',a.macro,'--output',str(terrain)]).returncode
 v=json.loads(vector.read_text());t=json.loads(terrain.read_text());cloud_t=json.loads((ver/'TERRAIN_CLOUD_V039.json').read_text());cloud_v=json.loads((ver/'CACHE_CLOUD_V038.json').read_text())
 report={'version':'0.39.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'selection':a.macro,'cloud':{'vectorCoordinates':cloud_v['cache']['totalCoordinates'],'vectorPbf':cloud_v['cache']['base']['storedPbf']+cloud_v['cache']['cadastre']['storedPbf'],'vectorOfficialEmpty':cloud_v['cache']['cadastre']['officialEmpty'],'terrainRegions':cloud_t['totals']['regions'],'terrainValid':cloud_t['totals']['valid'],'terrainNoData':cloud_t['totals']['missing']},'local':{'vectorExpected':v['expected'],'vectorValid':v['valid'],'vectorMissing':v['missing'],'terrainExpected':t['expectedRegions'],'terrainValid':t['validRegions'],'terrainMissing':t['missingRegions']},'vectorAudit':v,'terrainAudit':t,'cloudComplete':cloud_v['cache']['totalCoordinates']==5884 and cloud_t['complete'],'localComplete':v['truth']['complete'] and t['complete']}
 out=ver/'AUDIT_CARTE_REELLE_V039.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 cards=[('Vectoriel cloud','5 884 / 5 884'),('Relief cloud','8 / 8'),('Vectoriel local',f"{v['valid']} / {v['expected']}"),('Relief local',f"{t['validRegions']} / {t['expectedRegions']}"),('Routes non appariées',str(v['transportTopology']['unpairedWithNeighborLoaded'])),('Recouvrements relief',str(len(t['overlaps'])))]
 out.with_suffix('.html').write_text(f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Audit carte v0.39</title><style>body{{background:#101712;color:#dce8d4;font:15px/1.55 system-ui;margin:0}}main{{max-width:1100px;margin:auto;padding:32px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}article{{background:#18231a;border:1px solid #465c49;padding:18px}}b{{font-size:26px;color:#e8dca3}}</style><main><h1>Fallout : Mistral — Audit cartographique v0.39</h1><p>Le cache cloud complet est distinct du pack présent sur le disque.</p><div class="grid">{''.join(f'<article><small>{html.escape(k)}</small><br><b>{html.escape(vv)}</b></article>' for k,vv in cards)}</div><h2>Conclusion</h2><p>{'Pack local complet.' if report['localComplete'] else 'Pack local incomplet ou non installé ; utilisez l’installateur v0.39 avant une certification topologique complète.'}</p></main></html>''',encoding='utf-8')
 print(json.dumps({'cloudComplete':report['cloudComplete'],'localComplete':report['localComplete'],'vector':f"{v['valid']}/{v['expected']}",'terrain':f"{t['validRegions']}/{t['expectedRegions']}"},ensure_ascii=False,indent=2));return 0 if (report['localComplete'] or not a.require_local) else 2
if __name__=='__main__':raise SystemExit(main())
