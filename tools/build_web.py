#!/usr/bin/env python3
"""Publish the real Mistral distribution and every bundled runtime map.

All geography is restored and audited with the existing offline tools. HTTP
gzip changes transport only: browser-decoded bytes retain their original SHA.
The immutable deployment exposes build-time audits, never a fake live disk scan.
"""
from __future__ import annotations

from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from prepare_local_pack_v050 import prepare_if_bundled as prepare_base
from validate_real_map_v046 import audit as audit_base
from world_source_bundle import prepare_if_bundled as prepare_world, audit_details as audit_world
from city_sources import prepare_if_bundled as prepare_city, audit_details as audit_city
from precise_terrain_sources import prepare_if_bundled as prepare_precise, audit_details as audit_precise

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.vercel-static'
REPORT_NAMES = ('local-data', 'world-sources', 'city-sources', 'precise-terrain')
EXCLUDED_DATA_DIRECTORIES = {'archives', 'enrichment_archives', 'city_archives', 'precision_archives', '.chunks_v041'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def runtime_data_paths(root=ROOT):
    """Everything in data is shipped except offline installers and archives."""
    for path in sorted((root / 'data').rglob('*')):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DATA_DIRECTORIES or part.startswith('.') for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('Runtime symlink refused: ' + str(relative))
        if path.is_file():
            yield path


def web_html(raw):
    text = raw.decode('utf-8')
    # The same game reads these fields. Distinguish immutable build evidence
    # from its original local server's repeated filesystem inspection.
    substitutions = {
        "...j,live:url.startsWith('__mistral/')": "...j,live:url.startsWith('__mistral/')&&j.auditMode!=='immutable-build'",
        "...data,live:url.startsWith('__mistral/')": "...data,live:url.startsWith('__mistral/')&&data.auditMode!=='immutable-build'",
        'Audit du disque : ': 'Audit des fichiers de cette livraison : ',
        "if(!data.live)return {title:'État de la livraison'": "if(data.auditMode==='immutable-build')return {title:data.complete?'Territoire livré en ligne':'Livraison géographique à compléter',detail:detail+' · fichiers du déploiement vérifiés à sa construction.',ready:!!data.complete};if(!data.live)return {title:'État de la livraison'",
        "${!data?.live||!data?.complete?": "${(!data?.live&&data?.auditMode!=='immutable-build')||!data?.complete?",
    }
    if (text.count("...j,live:url.startsWith('__mistral/')") != 1 or
            text.count("...data,live:url.startsWith('__mistral/')") != 1 or text.count('Audit du disque : ') != 1):
        raise ValueError('Audit presentation changed upstream; review export rather than patching unknown code')
    for before, after in substitutions.items():
        if text.count(before) != 1:
            raise ValueError('Expected one known audit presentation site: ' + before)
        text = text.replace(before, after)
    return text.encode('utf-8')


def main():
    if not prepare_base(ROOT):
        raise ValueError('Bundled base geography is incomplete')
    prepare_world(ROOT)
    prepare_city(ROOT)
    prepare_precise(ROOT)
    pack = ROOT / 'data/map_pack'
    reports = {
        'local-data': audit_base(pack),
        'world-sources': audit_world(pack / 'enrichment'),
        'city-sources': audit_city(pack / 'city'),
        'precise-terrain': audit_precise(ROOT),
    }
    if not reports['local-data'].get('complete'):
        raise ValueError('Base vector/terrain audit must be complete before publication')
    for name in REPORT_NAMES[1:]:
        if reports[name].get('ok') is not True or reports[name].get('present') is not True:
            raise ValueError('Bundled geography family absent or invalid: ' + name)
    inspected_at = datetime.now(timezone.utc).isoformat()
    source_commit = os.environ.get('VERCEL_GIT_COMMIT_SHA') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    inventory = []

    def publish(relative, raw, encoding=None):
        target = OUTPUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        wire = gzip.compress(raw, compresslevel=6, mtime=0) if encoding == 'gzip' else raw
        target.write_bytes(wire)
        inventory.append({'path': str(relative), 'bytes': len(raw), 'sha256': digest(raw),
                          'transportBytes': len(wire), 'transportSha256': digest(wire),
                          'contentEncoding': encoding or 'identity'})

    source_html = (ROOT / 'index.html').read_bytes()
    html = web_html(source_html)
    publish(Path('index.html'), html)
    publish(Path('JOUER_FALLOUT_MISTRAL_v0.50.html'), html)
    publish(Path('manifest.webmanifest'), (ROOT / 'manifest.webmanifest').read_bytes())
    worker = (ROOT / 'sw.js').read_text()
    worker = worker.replace("const CACHE='fallout-mistral-v050-", "const CACHE='fallout-mistral-web-")
    worker = worker.replace(digest(source_html)[:16], digest(html)[:16])
    publish(Path('sw.js'), worker.encode())
    for path in sorted((ROOT / 'icons').iterdir()):
        if path.is_file():
            publish(path.relative_to(ROOT), path.read_bytes())
    for path in runtime_data_paths():
        publish(path.relative_to(ROOT), path.read_bytes(), 'gzip')
    for name, report in reports.items():
        inspection_scope = 'Fichiers de ce déploiement vérifiés à sa construction, avant compression HTTP sans perte. Aucun audit du disque du joueur ; aucune acquisition réseau.'
        report.update(auditMode='immutable-build', inspectedAt=inspected_at,
                      sourceCommit=source_commit, distributionManifest='/release-manifest.json',
                      inspectionScope=inspection_scope)
        # Retain the native LiDAR coverage limitation and every original
        # provenance field; deployment inspection is a separate concern.
        report.setdefault('scope', inspection_scope)
        if name == 'local-data':
            report['version'] = '0.50.0'
        publish(Path('__mistral') / (name + '.json'), canonical(report))
    # Existing fallback paths also carry this actual inspection, not an old
    # checked-in counter. The main four routes remain the normal game path.
    for legacy in ('v047', 'v050'):
        publish(Path('verification') / legacy / 'LOCAL_DATA_STATE.json', canonical(reports['local-data']))
    data_rows = [r for r in inventory if r['path'].startswith('data/')]
    manifest = {
        'schemaVersion': 1, 'game': 'fallout-mistral', 'version': '0.50.0',
        'sourceRepository': 'https://github.com/darknigthmare/fallout-Marseille',
        'sourceCommit': source_commit, 'builtAt': inspected_at,
        'sourceHtmlSha256': digest(source_html), 'deployedHtmlSha256': digest(html),
        'htmlChanges': 'Audit presentation only: immutable build inspection is not presented as a scan of the player disk. Game mechanics and geographic decoded bytes are unchanged.',
        'transport': 'HTTP gzip for every data/* file; Content-Encoding is required. Browser-decoded bytes match the listed SHA-256.',
        'runtimeDataFiles': len(data_rows), 'runtimeDataDecodedBytes': sum(r['bytes'] for r in data_rows),
        'runtimeDataTransportBytes': sum(r['transportBytes'] for r in data_rows),
        'audits': {name: '/__mistral/' + name for name in REPORT_NAMES},
        'files': inventory,
        'limitations': ['Source coverage, NoData and unknown architectural details retain the game\'s original provenance and limitations.',
                        'Audit responses describe the immutable deployed files inspected at build time, not mutable player files or a new geographic acquisition.'],
    }
    (OUTPUT / 'release-manifest.json').write_bytes(canonical(manifest))
    print(json.dumps({k: manifest[k] for k in ('sourceCommit', 'runtimeDataFiles', 'runtimeDataDecodedBytes', 'runtimeDataTransportBytes', 'deployedHtmlSha256')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
