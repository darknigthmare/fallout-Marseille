#!/usr/bin/env python3
"""Run the inherited contracts on the current HTML without changing old reports.

The historical suites still use their original synthetic/controlled harnesses.
Native HTTP and real-map coverage are recorded separately by tests/v050.
"""
from pathlib import Path
import argparse
import ast
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/v050'
LEGACY = OUT / 'legacy'
HTML = ROOT / 'JOUER_FALLOUT_MISTRAL_v0.50.html'


def specifications():
    tree = ast.parse((ROOT / 'tools/check_v049.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SPECS' for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError('Liste des contrats historiques introuvable')


def adapt(name, text):
    text = text.replace('JOUER_FALLOUT_MISTRAL_v0.49.html', HTML.name)
    text = text.replace('verification/v049', 'verification/v050/legacy')
    # Versions of the retained gameplay modules are intentionally unchanged.
    text = text.replace("diag['version']=='0.49.0'", "diag['version']=='0.50.0'")
    text = text.replace("local['version']=='0.49.0'", "local['version']=='0.50.0'")
    text = text.replace('0.49.0 · Le quartier se souvient', '0.50.0 · Les routes retrouvées')
    if name.endswith('distribution.cjs'):
        text = text.replace('fallout-mistral-v049-1', 'fallout-mistral-v050-10').replace('/v0.49.html/', '/v0.50.html/')
    if name == 'v048_runtime.py':
        # The controlled pause must outlast Playwright's two stable animation
        # frames even when another software-rendered browser uses the CPU.
        # Keep the real Cancel button and every stage/rollback assertion.
        text = text.replace("'pausePhase':phase,'pauseMs':350", "'pausePhase':phase,'pauseMs':1500")
    if name.endswith('regression_campaign.py'):
        text = text.replace('Menu joueur structuré en neuf entrées', 'Menu joueur et accès aux cartes : dix entrées')
        text = text.replace("'btnOptions','btnCredits','btnV035Admin']", "'btnOptions','btnCredits','v050MapStatus','btnV035Admin']")
    if name.endswith('regression_prologue.py'):
        # Preserve the legacy narrative route contract. The first, geographic
        # option is exercised against actual files by the native v0.50 suite.
        text = text.replace("c('v35pExit');p.locator('#dialogueChoices button').first.click();",
                            "c('v35pExit');p.get_by_role('button',name='Rejoindre directement les ateliers — scène narrative',exact=True).click();")
    if name.endswith('regression_product.py'):
        # v0.50 Continue compares raw current saves with envelopes. This fixture
        # changes the caps after its manual slot, then the menu saves that newer
        # state. Its recap can retain the same lastSave millisecond: current wins
        # that documented tie. Prove the ordering and the untouched manual slot;
        # expecting the old caps here would reinstate the lost-progress bug.
        old = "p.click('#btnContinue');p.wait_for_timeout(220);ck('Reprise restaure un point cohérent',c('v020State')['player']['caps']==caps,c('v020State')['player']['caps'])"
        new = """continue_candidates=c('v050ContinueInfo');chosen=continue_candidates[0];chosen_raw=p.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',chosen['key']);chosen_snapshot=chosen_raw['snapshot'] if chosen['kind'] in ['slot','auto'] else chosen_raw
  manual_key=next(x['key'] for x in continue_candidates if x['kind']=='slot' and x['slot']==1)
  p.click('#btnContinue');p.wait_for_timeout(220);resumed=c('v020State');manual_after=p.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',manual_key)
  ck('Continuer reprend le plus récent ou le courant à date égale, slot intact',chosen['kind'] in ['current','auto'] and (chosen['savedAt']>saved['savedAt'] or (chosen['savedAt']==saved['savedAt'] and chosen['kind']=='current')) and chosen_snapshot['player']['caps']==caps+999 and resumed['player']['caps']==caps+999 and resumed['player']['zone']==chosen_snapshot['player']['zone'] and resumed['quest']==chosen_snapshot['quest'] and manual_after==saved,{'selected':chosen,'manualSavedAt':saved['savedAt'],'manualCaps':saved['snapshot']['player']['caps'],'expectedCaps':caps+999,'selectedCaps':chosen_snapshot['player']['caps'],'resumedCaps':resumed['player']['caps'],'resumedZone':resumed['player']['zone'],'manualSlotUnchanged':manual_after==saved})"""
        if text.count(old) != 1:
            raise RuntimeError('Contrat de reprise historique introuvable ou ambigu')
        text = text.replace(old, new, 1)
    if name.endswith('server_io.py'):
        text = text.replace("'Absence de pack signalée et non masquée',local['vector']['missing']==5884 and local['terrain']['missing']==8 and not local['complete']",
                            "'Pack complet confirmé par le disque',local['vector']['missing']==0 and local['vector']['invalid']==0 and local['vector']['pbf']+local['vector']['officialEmpty']==5884 and local['terrain']['valid']==8 and local['terrain']['invalid']==0 and local['complete']")
        # Startup now validates the communal atlas before opening HTTP. Match
        # the current delivery check's bounded readiness window while retaining
        # every historical assertion and leaving the historical source intact.
        waits = [
            (' for _ in range(80):',
             ' readiness_deadline=time.monotonic()+300\n while time.monotonic()<readiness_deadline:'),
            ("urllib.request.urlopen(base+'/index.html',timeout=2)",
             "urllib.request.urlopen(base+'/index.html',timeout=3)"),
            ("urllib.request.urlopen(base+'/__mistral/local-data')",
             "urllib.request.urlopen(base+'/__mistral/local-data',timeout=300)"),
        ]
        for old, new in waits:
            if text.count(old) != 1:
                raise RuntimeError('Délai serveur historique introuvable ou ambigu : ' + old)
            text = text.replace(old, new, 1)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--only', help='Nom exact d’un script historique à exécuter')
    args = parser.parse_args()
    LEGACY.mkdir(parents=True, exist_ok=True)
    specs = specifications()
    if args.only:
        specs = [s for s in specs if s[0] == args.only]
        if not specs:
            parser.error('Suite inconnue')
    subprocess.run(['node', '--check', 'src/game.js'], cwd=ROOT, check=True)
    results = []
    adaptations = []
    if not args.collect:
        # Same depth as tests/v049: the original __file__/__dirname roots work.
        with tempfile.TemporaryDirectory(prefix='v050-legacy-', dir=ROOT / 'tests') as temporary:
            staging = Path(temporary)
            for name, _ in specs:
                source = (ROOT / 'tests/v049' / name).read_text(encoding='utf-8')
                current = adapt(name, source)
                (staging / name).write_text(current, encoding='utf-8')
                adaptations.append({'test': name, 'sourceSha256': hashlib.sha256(source.encode()).hexdigest(),
                                    'executedSha256': hashlib.sha256(current.encode()).hexdigest()})

            def run(spec):
                name, _ = spec
                cmd = ['node' if name.endswith('.cjs') else sys.executable, str(staging / name)]
                # Only the server suite waits for full communal-atlas startup.
                timeout_seconds = 420 if name.endswith('server_io.py') else 240
                try:
                    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout_seconds)
                    log, code = result.stdout + '\n' + result.stderr, result.returncode
                except subprocess.TimeoutExpired as error:
                    log, code = f'Timeout de {timeout_seconds} secondes : {error}', 124
                (LEGACY / (name + '.log')).write_text(log, encoding='utf-8')
                print(('PASS ' if code == 0 else 'FAIL ') + name, flush=True)
                return {'test': name, 'exitCode': code}

            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 3))) as executor:
                results = list(executor.map(run, specs))

    digest = hashlib.sha256(HTML.read_bytes()).hexdigest()
    rows, errors = [], []
    for name, filename in specs:
        path = LEGACY / filename
        if not path.is_file():
            rows.append({'test': name, 'file': filename, 'passed': 0, 'failed': 1, 'total': 1, 'sameHtml': False})
            errors.append(f'{name} : rapport absent')
            continue
        report = json.loads(path.read_text(encoding='utf-8'))
        rows.append({'test': name, 'file': filename, 'passed': report['passed'], 'failed': report['failed'],
                     'total': report['total'], 'sameHtml': not report.get('html_sha256') or report['html_sha256'] == digest})
        errors.extend(report.get('errors', []))
    report = {'version': '0.50.0', 'html_sha256': digest,
              'scope': 'Contrats hérités exécutés sur le programme actuel. Bancs synthétiques et réseau contrôlé ; voir NATIVE_REAL_MAP.json pour les parcours HTTP réels.',
              'passed': sum(r['passed'] for r in rows), 'failed': sum(r['failed'] for r in rows),
              'total': sum(r['total'] for r in rows), 'allHtmlMatch': all(r['sameHtml'] for r in rows),
              'javascriptErrors': errors, 'suites': rows, 'processes': results, 'adaptations': adaptations}
    target = OUT / ('QA_LEGACY_' + args.only.replace('.', '_') + '.json' if args.only else 'QA_LEGACY.json')
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['passed', 'failed', 'total', 'allHtmlMatch', 'javascriptErrors']}, ensure_ascii=False))
    return int(bool(report['failed'] or errors or not report['allHtmlMatch'] or any(r['exitCode'] for r in results)))


if __name__ == '__main__':
    raise SystemExit(main())
