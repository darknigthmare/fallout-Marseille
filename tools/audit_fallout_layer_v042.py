#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import collections, hashlib, html, json, math, sys

R = Path(__file__).resolve().parents[1]
CAT = R / 'data' / 'fallout_layer_v042.json'
OUT = R / 'verification'
OUT.mkdir(exist_ok=True)

def meters(a: dict, b: dict) -> float:
    lat = math.radians((a['lat'] + b['lat']) / 2)
    dx = (a['lon'] - b['lon']) * 111_320 * math.cos(lat)
    dy = (a['lat'] - b['lat']) * 111_320
    return math.hypot(dx, dy)

data = json.loads(CAT.read_text(encoding='utf-8'))
meta, macros, sites = data['meta'], data['macros'], data['sites']
errors: list[str] = []
warnings: list[str] = []
ids = [s['id'] for s in sites]
if len(ids) != len(set(ids)): errors.append('identifiants dupliqués')
if len(sites) != 248: errors.append(f'nombre de sites inattendu: {len(sites)}')
kind_counts = collections.Counter(s['kind'] for s in sites)
macro_counts = collections.Counter(s['macro'] for s in sites)
expected_kinds = {'shelter':16,'settlement':24,'outpost':24,'interior':48,'nest':64,'elite':24,'boss':8,'landmark':24,'caravan':16}
if dict(kind_counts) != expected_kinds: errors.append(f'comptage catégories: {dict(kind_counts)}')
for macro, profile in macros.items():
    bbox = profile['bbox']; arr = [s for s in sites if s['macro'] == macro]
    if len(arr) != 31: errors.append(f'{macro}: {len(arr)} sites au lieu de 31')
    for s in arr:
        if not (bbox[0] <= s['lat'] <= bbox[2] and bbox[1] <= s['lon'] <= bbox[3]): errors.append(f"{s['id']}: hors emprise")
        if s['visitable'] != (s['kind'] in ('shelter','interior')): errors.append(f"{s['id']}: visitable incohérent")
        if s['kind'] in ('nest','elite','boss') and not s['enemySlots']: errors.append(f"{s['id']}: site hostile sans ennemi")
        if s['safe'] and not s['npcSlots']: errors.append(f"{s['id']}: site sûr sans PNJ")
        if s['tier'] < 1 or s['tier'] > 5: errors.append(f"{s['id']}: tier {s['tier']}")
min_spacing: dict[str, dict] = {}
for macro in macros:
    arr = [s for s in sites if s['macro'] == macro]
    best = (float('inf'), '', '')
    for i, a in enumerate(arr):
        for b in arr[i+1:]:
            d = meters(a,b)
            if d < best[0]: best = (d,a['id'],b['id'])
    min_spacing[macro] = {'meters': round(best[0],1),'a':best[1],'b':best[2]}
    if best[0] < 100: warnings.append(f'{macro}: sites très proches ({best[0]:.1f} m)')
# Count all gameplay potential, not simultaneously instantiated.
npc_slots = sum(int(s.get('npcSlots',0)) for s in sites)
enemy_slots = sum(int(s.get('enemySlots',0)) for s in sites)
visitable = sum(bool(s.get('visitable')) for s in sites)
hostile = sum(s['kind'] in ('nest','elite','boss') for s in sites)
unique = sum(bool(s.get('unique')) for s in sites)
used_enemies = sorted({t for s in sites for t in ([*s.get('enemyTypes',[]),s.get('eliteType'),s.get('bossType')]) if t})
# Static schema checks.
required={'id','macro','lat','lon','kind','name','description','anchor','tier','faction','safe','visitable','theme','unique','discoverRadius','activationRadius','npcSlots','enemySlots'}
for s in sites:
    missing=required-set(s)
    if missing: errors.append(f"{s.get('id','?')}: champs manquants {sorted(missing)}")
    if s['discoverRadius'] >= s['activationRadius']: warnings.append(f"{s['id']}: découverte >= activation")
summary = {
    'version':'0.42.0','catalog_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),'ok':not errors,
    'errors':errors,'warnings':warnings,'siteCount':len(sites),'macroCount':len(macros),'kindCounts':dict(kind_counts),
    'macroCounts':dict(macro_counts),'minSpacing':min_spacing,'visitable':visitable,'hostileSites':hostile,
    'uniqueSites':unique,'npcSlots':npc_slots,'enemySlots':enemy_slots,'enemyFamilies':used_enemies,
    'streaming':{'defaultBudget':7,'minBudget':3,'maxBudget':12,'simultaneousSitesClaimedAtDefault':7},
    'disclosure':'Sites and Fallout fiction are original/fan-made placements. Coordinates are deterministic WGS84 overlays and do not modify OSM, Cadastre or RGE ALTI data.'
}
(OUT/'AUDIT_COUCHE_FALLOUT_V042.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=''.join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k,v in kind_counts.items())
macro_rows=''.join(f"<tr><td>{html.escape(k)}</td><td>{macro_counts[k]}</td><td>{min_spacing[k]['meters']} m</td></tr>" for k in macros)
err=''.join(f'<li>{html.escape(x)}</li>' for x in errors) or '<li>Aucune erreur structurelle.</li>'
warn=''.join(f'<li>{html.escape(x)}</li>' for x in warnings) or '<li>Aucun avertissement de densité.</li>'
page=f'''<!doctype html><meta charset="utf-8"><title>Audit couche Fallout v0.42</title><style>body{{background:#0e140f;color:#dce7d4;font:15px/1.55 system-ui;margin:0}}main{{max-width:1100px;margin:auto;padding:32px}}h1,h2{{color:#eadfac}}table{{width:100%;border-collapse:collapse;background:#152018;margin:12px 0 28px}}td,th{{border:1px solid #3b4d3d;padding:8px;text-align:left}}strong{{color:#d9edb7}}code{{color:#f2d38a}}</style><main><h1>Audit de la couche Fallout · v0.42</h1><p><strong>{len(sites)} sites</strong> déterministes sur {len(macros)} macro-régions. Statut : <strong>{'VALIDE' if not errors else 'ERREURS'}</strong>.</p><h2>Contenu potentiel</h2><p>{visitable} lieux visitables · {hostile} sites hostiles · {npc_slots} emplacements PNJ · {enemy_slots} emplacements ennemis · {len(used_enemies)} familles de créatures.</p><table><thead><tr><th>Catégorie</th><th>Nombre</th></tr></thead><tbody>{rows}</tbody></table><h2>Répartition et espacement</h2><table><thead><tr><th>Macro-région</th><th>Sites</th><th>Distance minimale</th></tr></thead><tbody>{macro_rows}</tbody></table><h2>Erreurs</h2><ul>{err}</ul><h2>Avertissements</h2><ul>{warn}</ul><p>Empreinte catalogue : <code>{summary['catalog_sha256']}</code></p><p>Les implantations sont fictives et superposées à la géographie réelle sans modifier les données cartographiques officielles.</p></main>'''
(OUT/'AUDIT_COUCHE_FALLOUT_V042.html').write_text(page,encoding='utf-8')
print(json.dumps({'ok':not errors,'sites':len(sites),'npcs':npc_slots,'enemies':enemy_slots,'warnings':len(warnings),'errors':len(errors)},ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
