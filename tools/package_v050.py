#!/usr/bin/env python3
"""Build, extract and verify v0.50 archives, including the installed real maps.

Requires Playwright/Chromium for the native navigation check of the extracted
playable archive. Artifacts are written outside the repository. The full source
ZIP also includes all verified map bundles, source modules and historical files.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile

R = Path(__file__).resolve().parents[1]
HTML = 'JOUER_FALLOUT_MISTRAL_v0.50.html'
GAME_NAME = 'FALLOUT_MISTRAL_v0.50_JEU_COMPLET.zip'
FULL_NAME = 'FALLOUT_MISTRAL_v0.50_PROJET_COMPLET.zip'
FULL_MANIFEST = 'MANIFEST_V050_SHA256.json'
GAME_MANIFEST = 'MANIFEST_JEU_V050_SHA256.json'
BLOCK = 1024 * 1024
PART_SIZE = 64 * 1024 * 1024
DRIVE_LIMIT = 100 * 1024 * 1024
CHECKS = []


def playable_tool_names():
    """Python modules needed by the extracted game and its source validators."""
    return ['serve_game.py', 'prepare_local_pack_v050.py', 'validate_real_map_v046.py',
            'install_local_pack_v041.py', 'install_real_map_v038.py', 'install_real_map_v039.py',
            'install_terrain_v039.py', 'mvt_audit_v036.py', 'benchmark_map_v041.py',
            'audit_real_map_v039.py', 'audit_real_map_v038.py', 'audit_terrain_v039.py',
            'audit_corridors_v040.py', 'world_source_bundle.py', 'world_sources.py',
            'city_sources.py', 'city_water_sources.py', 'precise_terrain_sources.py', 'acquire_city_world.py',
            'acquire_public_world.py']


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(BLOCK), b''):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ck(name, ok, detail=None):
    CHECKS.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print(('OK ' if ok else 'FAIL ') + name, flush=True)
    if not ok:
        raise RuntimeError(name)


def include(path):
    rel = path.relative_to(R)
    excluded = {'.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules', '.chunks_v041'}
    return (path.is_file() and not path.is_symlink()
            and not any(part in excluded for part in rel.parts)
            and not any(part.startswith('v050-legacy-') for part in rel.parts)
            and path.suffix not in {'.pyc', '.pyo'}
            and path.name not in {'.DS_Store', 'Thumbs.db', FULL_MANIFEST, GAME_MANIFEST}
            and not path.name.endswith('.reconstruction.tmp'))


def safe(name):
    return not name.startswith(('/', '\\')) and '\\' not in name and '..' not in PurePosixPath(name).parts


def entries(paths):
    return [{'path': p.relative_to(R).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in paths]


def zip_files(target, paths, prefix=''):
    temporary = target.with_name(target.name + '.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as bundle:
        for path in paths:
            info = zipfile.ZipInfo(prefix + path.relative_to(R).as_posix(), (2026, 10, 18, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if os.access(path, os.X_OK) else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with bundle.open(info, 'w', force_zip64=True) as out, path.open('rb') as source:
                shutil.copyfileobj(source, out, BLOCK)
    temporary.replace(target)


def validate_zip(target, prefix, manifest_name, html_hash):
    with zipfile.ZipFile(target) as bundle:
        names = bundle.namelist()
        ck(target.stem + ' : chemins sûrs et uniques', len(names) == len(set(names)) and all(safe(n) for n in names))
        ck(target.stem + ' : CRC ZIP', bundle.testzip() is None)
        manifest = json.loads(bundle.read(prefix + manifest_name))
        expected = {prefix + row['path'] for row in manifest['files']} | {prefix + manifest_name}
        ck(target.stem + ' : aucun composant manquant ou supplémentaire', set(names) == expected, {'files': len(names)})
        bad = []
        for row in manifest['files']:
            raw = bundle.read(prefix + row['path'])
            if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
                bad.append(row['path'])
        ck(target.stem + ' : toutes les empreintes SHA-256', not bad, {'files': len(manifest['files']), 'mismatches': bad})
        ck(target.stem + ' : HTML exact', hashlib.sha256(bundle.read(prefix + HTML)).hexdigest() == html_hash)


def check_extracted_server(folder, html_hash):
    from playwright.sync_api import sync_playwright
    from qa_support import chromium_path
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'http://127.0.0.1:{port}'
    with tempfile.TemporaryFile(mode='w+') as log:
        proc = subprocess.Popen([sys.executable, 'tools/serve_game.py', '--port', str(port), '--no-browser'], cwd=folder, stdout=log, stderr=log)
        try:
            status = None
            startup_deadline = time.monotonic() + 300
            while time.monotonic() < startup_deadline:
                if proc.poll() is not None:
                    log.seek(0)
                    raise RuntimeError('Serveur arrêté : ' + log.read()[-1200:])
                try:
                    with urllib.request.urlopen(url + '/__mistral/local-data', timeout=3) as response:
                        status = json.loads(response.read())
                        cache = response.headers.get('Cache-Control')
                    break
                except OSError:
                    time.sleep(.1)
            ck('Jeu extrait : serveur et audit HTTP natifs', status is not None and status.get('version') == '0.50.0' and cache == 'no-store')
            ck('Jeu extrait : 5 884 coordonnées et huit reliefs complets', status['complete'] and status['vector']['expected'] == 5884 and status['vector']['missing'] == 0 and status['terrain']['missing'] == 0, status)
            with urllib.request.urlopen(url + '/index.html', timeout=5) as response:
                ck('Jeu extrait : HTML HTTP identique', hashlib.sha256(response.read()).hexdigest() == html_hash)
            tile_manifest = read_json(folder / 'data/map_pack/manifest_v038.json')
            tile = next(row for row in tile_manifest['tiles'] if (folder / row['local']).stat().st_size > 0)
            with urllib.request.urlopen(url + '/' + tile['local'], timeout=5) as response:
                ck('Jeu extrait : vrai PBF servi sans substitution HTML', hashlib.sha256(response.read()).hexdigest() == sha(folder / tile['local']), tile['local'])
            terrain = folder / 'data/map_pack/terrain/geo_huveaune.json'
            with urllib.request.urlopen(url + '/data/map_pack/terrain/geo_huveaune.json', timeout=5) as response:
                ck('Jeu extrait : vraie grille de relief HTTP', hashlib.sha256(response.read()).hexdigest() == sha(terrain))
            city_index = folder / 'data/map_pack/city/index.json'
            if city_index.exists():
                with urllib.request.urlopen(url + '/__mistral/city-sources', timeout=300) as response:
                    city = json.load(response)
                expected_city = read_json(city_index)
                expected_terrain = read_json(folder / 'data/map_pack/city/terrain-index.json')
                ck('Jeu extrait : atlas communal et validateurs réellement distribués',
                   city.get('ok') is True and city.get('present') is True
                   and city['indexSha256'] == sha(city_index)
                   and city['coverage'] == expected_city['coverage']
                   and city['terrain']['coverage'] == expected_terrain['coverage']
                   and city['water']['present'] is True)
            with sync_playwright() as pw:
                browser = pw.chromium.launch(executable_path=chromium_path(), args=['--no-sandbox', '--disable-dev-shm-usage'])
                try:
                    page = browser.new_page(viewport={'width': 1280, 'height': 800})
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    response = page.goto(url + '/index.html', wait_until='domcontentloaded', timeout=30000)
                    page.locator('#menuScreen.active').wait_for(timeout=20000)
                    ck('Jeu extrait : vraie navigation Chromium et menu actif', response.status == 200 and page.evaluate('__MISTRAL_DEBUG.v050Info().version') == '0.50.0')
                    ck('Jeu extrait : stockage natif disponible', page.evaluate("window.isSecureContext && localStorage instanceof Storage && !!indexedDB"))
                    local = page.evaluate('async () => {await __MISTRAL_DEBUG.v050ReadLocal(); return __MISTRAL_DEBUG.v050Info().localData;}')
                    ck('Jeu extrait : menu lit réellement le pack complet', local and local.get('complete') is True)
                    ck('Jeu extrait : aucune exception JavaScript', not errors, errors)
                finally:
                    browser.close()
        finally:
            proc.terminate()
            proc.wait(timeout=10)


def split_and_verify(full, out):
    parts = []
    with full.open('rb') as source:
        index = 0
        while True:
            block = source.read(PART_SIZE)
            if not block:
                break
            index += 1
            target = out / (full.name + f'.{index:03d}')
            target.write_bytes(block)
            parts.append({'name': target.name, 'bytes': len(block), 'sha256': hashlib.sha256(block).hexdigest()})
    manifest = {'version': '0.50.0', 'archive': {'name': full.name, 'bytes': full.stat().st_size, 'sha256': sha(full)}, 'parts': parts}
    write_json(out / 'ARCHIVE_PARTS.json', manifest)
    shutil.copyfile(R / 'tools/reassemble_v050.py', out / 'RECONSTRUIRE_ARCHIVE.py')
    (out / 'RECONSTRUIRE_ARCHIVE_WINDOWS.bat').write_bytes(b'@echo off\r\ncd /d "%~dp0"\r\nwhere py >nul 2>nul\r\nif errorlevel 1 (python RECONSTRUIRE_ARCHIVE.py) else (py -3 RECONSTRUIRE_ARCHIVE.py)\r\npause\r\n')
    (out / 'RECONSTRUIRE_ARCHIVE_LINUX_MAC.sh').write_text('#!/usr/bin/env sh\nset -eu\ncd "$(dirname "$0")"\npython3 RECONSTRUIRE_ARCHIVE.py\n', encoding='utf-8')
    (out / 'LIRE_MOI.txt').write_text(
        'FALLOUT MARSEILLE — MISTRAL v0.50\n\n'
        'POUR JOUER : téléchargez FALLOUT_MISTRAL_v0.50_JEU_COMPLET.zip, extrayez-le\n'
        'puis lancez LANCER_APP_WINDOWS.bat, LANCER_APP_LINUX.sh ou LANCER_APP_MAC.command.\n'
        'Python 3 est requis. Les cartes et reliefs sont déjà extraits.\n\n'
        f'PROJET COMPLET : le ZIP de {full.stat().st_size:,} octets est livré en {len(parts)} parties.\n'
        'Téléchargez toutes les parties .zip.001, .zip.002, etc., ARCHIVE_PARTS.json,\n'
        'RECONSTRUIRE_ARCHIVE.py et le lanceur adapté dans un même dossier.\n'
        'Windows : RECONSTRUIRE_ARCHIVE_WINDOWS.bat ; Linux/macOS : python3 RECONSTRUIRE_ARCHIVE.py\n'
        'Le script contrôle chaque partie, puis le SHA-256 et le CRC du ZIP reconstitué.\n'
        'Il ne télécharge rien et ne remplace pas un ZIP différent déjà présent.\n'
        'Ne tentez pas d’extraire les parties séparément. Si Drive les enveloppe dans\n'
        'un autre ZIP, extrayez d’abord cette enveloppe.\n\n'
        'Le projet complet contient le jeu, les données extraites, les 24 archives\n'
        'géographiques d’origine, les sources, les tests et l’historique conservé.\n'
        'Consultez le rapport visuel v0.50 et docs/KNOWN_LIMITATIONS_V0.50.md.\n\n'
        'GitHub : https://github.com/darknigthmare/fallout-Marseille\n'
        'Drive : https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ\n', encoding='utf-8')
    ck('Parties de transfert sous la limite Drive', all(part['bytes'] <= DRIVE_LIMIT for part in parts), parts)
    with tempfile.TemporaryDirectory(prefix='mistral050-reassembly-') as td:
        folder = Path(td)
        for name in [part['name'] for part in parts] + ['ARCHIVE_PARTS.json', 'RECONSTRUIRE_ARCHIVE.py']:
            try:
                os.link(out / name, folder / name)
            except OSError:
                # The delivery directory and the system temp directory may
                # reside on different filesystems, including on Windows.
                shutil.copyfile(out / name, folder / name)
        process = subprocess.run([sys.executable, 'RECONSTRUIRE_ARCHIVE.py'], cwd=folder, capture_output=True, text=True, timeout=240)
        ck('Recomposition réelle depuis les parties', process.returncode == 0, process.stdout[-1200:] + process.stderr[-400:])
        ck('ZIP recomposé identique octet pour octet', sha(folder / full.name) == manifest['archive']['sha256'])
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=R.parent / 'delivery-v050')
    parser.add_argument('--quality-report', type=Path, default=R / 'verification/v050/QA_GLOBAL.json', help='Bilan complet réussi, lié au SHA du HTML à distribuer.')
    parser.add_argument('--native-report', type=Path, default=R / 'verification/v050/NATIVE_REAL_MAP.json', help='Parcours natif complet de campagne sur le même HTML.')
    args = parser.parse_args()
    out = args.output.resolve()
    if out == R or R in out.parents:
        parser.error('Le dossier de livraison doit être extérieur au dépôt.')
    out.mkdir(parents=True, exist_ok=True)
    html_hash = sha(R / HTML)
    quality = read_json(args.quality_report)
    native = read_json(args.native_report)
    ck('QA finale réussie sur le HTML distribué', quality['failed'] == 0 and quality['passed'] == quality['total'] and quality['html_sha256'] == html_hash, {'passed': quality['passed'], 'total': quality['total']})
    ck('Parcours natif complet sur le même HTML', native['failed'] == 0 and native['stage'] == 'complete' and native['html_sha256'] == html_hash and native['browser_document_sha256'] == html_hash and not native['page_errors'])
    ck('Index et programme distribués identiques', sha(R / 'index.html') == html_hash)
    rootfiles = [HTML, 'index.html', 'README.md', 'README_FR.md', 'START_HERE.txt', 'manifest.webmanifest', 'sw.js', 'RAPPORT_VISUEL_V0.50.html', 'RAPPORT_VISUEL_V0.50.png']
    rootfiles += [p.name for p in R.iterdir() if p.is_file() and p.suffix in {'.bat', '.sh', '.command'}]
    toolnames = playable_tool_names()
    paths = {R / name for name in rootfiles} | {R / 'tools' / name for name in toolnames}
    for folder in ['icons', 'data', 'docs', 'verification/v050', 'verification/expansion', 'implementation/real-sources', 'implementation/city-sources']:
        paths.update(p for p in (R / folder).rglob('*') if include(p)
                     and not any(part in {'archives', 'enrichment_archives', 'city_archives'} for part in p.relative_to(R).parts)
                     and not p.is_relative_to(R / 'data/map_pack/precise'))
    game_files = sorted(paths)
    ck('Tous les composants de la distribution jouable présents', all(p.is_file() for p in game_files))
    game_manifest = {'version': '0.50.0', 'scope': 'Jeu avec données géographiques de base extraites, lanceurs, documents et preuves. Le relief LiDAR natif reste dans ses archives vérifiées et se prépare hors ligne au lancement, sans doubler son contenu dans le ZIP. Les 24 ZIP de reconstruction de base figurent dans le projet complet.', 'files': entries(game_files)}
    write_json(R / GAME_MANIFEST, game_manifest)
    full_files = sorted([p for p in R.rglob('*') if include(p)] + [R / GAME_MANIFEST])
    full_manifest = {'version': '0.50.0', 'scope': 'Projet complet : sources, tests, historique, données géographiques extraites et 24 ZIP d’origine. Seuls VCS, caches et fichiers temporaires sont exclus.', 'files': entries(full_files)}
    write_json(R / FULL_MANIFEST, full_manifest)
    game, full = out / GAME_NAME, out / FULL_NAME
    zip_files(game, game_files + [R / GAME_MANIFEST])
    zip_files(full, full_files + [R / FULL_MANIFEST], R.name + '/')
    validate_zip(game, '', GAME_MANIFEST, html_hash)
    validate_zip(full, R.name + '/', FULL_MANIFEST, html_hash)
    ck('Jeu complet directement transférable sur Drive', game.stat().st_size <= DRIVE_LIMIT, game.stat().st_size)
    with tempfile.TemporaryDirectory(prefix='mistral050-full-') as td:
        with zipfile.ZipFile(full) as bundle:
            bundle.extractall(td)
        folder = Path(td) / R.name
        result = subprocess.run([sys.executable, 'tools/build_single.py'], cwd=folder, capture_output=True, text=True, timeout=60)
        ck('Reconstruction du projet extrait', result.returncode == 0, result.stderr[-500:])
        ck('HTML reconstruit identique octet pour octet', sha(folder / HTML) == html_hash and sha(folder / 'index.html') == html_hash)
        result = subprocess.run(['node', '--check', 'src/game.js'], cwd=folder, capture_output=True, text=True, timeout=30)
        ck('Syntaxe JavaScript du projet reconstruit', result.returncode == 0, result.stderr[-500:])
    with tempfile.TemporaryDirectory(prefix='mistral050-game-') as td:
        with zipfile.ZipFile(game) as bundle:
            bundle.extractall(td)
        check_extracted_server(Path(td), html_hash)
    parts = split_and_verify(full, out)
    for name in ['RAPPORT_VISUEL_V0.50.png', 'RAPPORT_VISUEL_V0.50.html']:
        shutil.copyfile(R / name, out / name)
    control = out / 'FALLOUT_MISTRAL_v0.50_CONTROLES_LIVRAISON.json'
    artifacts = [game, full, R / HTML, out / 'RAPPORT_VISUEL_V0.50.png', out / 'RAPPORT_VISUEL_V0.50.html']
    report = {'version': '0.50.0', 'html_sha256': html_hash, 'passed': sum(c['ok'] for c in CHECKS), 'failed': sum(not c['ok'] for c in CHECKS), 'total': len(CHECKS), 'checks': CHECKS, 'browserScope': 'Vraie navigation HTTP Chromium depuis le jeu extrait, stockage natif, aucun HTML injecté, aucune interception réseau. Contrôle de livraison limité au menu et aux données ; parcours complet documenté dans NATIVE_REAL_MAP.json.', 'artifacts': {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in artifacts}, 'full_archive_parts': parts}
    write_json(control, report)
    sums_files = sorted([p for p in out.iterdir() if p.is_file() and p.name != 'FALLOUT_MISTRAL_v0.50_CHECKSUMS.txt'])
    (out / 'FALLOUT_MISTRAL_v0.50_CHECKSUMS.txt').write_text(''.join(sha(p) + '  ' + p.name + '\n' for p in sums_files), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['passed', 'failed', 'total', 'artifacts']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
