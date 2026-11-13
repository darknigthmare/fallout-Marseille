#!/usr/bin/env python3
"""Check every published map byte and representative actual HTTP decoding."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from build_web import ROOT, OUTPUT, runtime_data_paths


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url', help='Optional local or public HTTP deployment')
    args = p.parse_args()
    manifest = json.loads((OUTPUT / 'release-manifest.json').read_text())
    rows = {row['path']: row for row in manifest['files']}
    expected = {str(path.relative_to(ROOT)) for path in runtime_data_paths()}
    assert {name for name in rows if name.startswith('data/')} == expected, 'No runtime geography file may be omitted or invented'
    for name, row in rows.items():
        wire = (OUTPUT / name).read_bytes()
        assert len(wire) == row['transportBytes'] and sha(wire) == row['transportSha256'], name
        raw = gzip.decompress(wire) if row['contentEncoding'] == 'gzip' else wire
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
        if name in expected:
            assert raw == (ROOT / name).read_bytes(), 'Decoded geography changed: ' + name
    audits = {name: json.loads((OUTPUT / '__mistral' / (name + '.json')).read_text())
              for name in ('local-data', 'world-sources', 'city-sources', 'precise-terrain')}
    assert audits['local-data']['complete'] is True
    assert audits['local-data']['vector']['missing'] == 0 and audits['local-data']['terrain']['missing'] == 0
    for name in ('world-sources', 'city-sources', 'precise-terrain'):
        assert audits[name]['ok'] is True and audits[name]['present'] is True
    assert 'limited central Marseille' in audits['precise-terrain']['scope'], 'Native LiDAR scope must not disappear'
    checked_http = []
    if args.base_url:
        origin = args.base_url.rstrip('/')
        # Cover every runtime map family, including a real nonempty PBF and a
        # large native terrain tile. Check decoded bytes against the manifest.
        families = ('france-vector/', 'cadastre/', 'terrain/', 'enrichment/', 'city/', 'precise/')
        selected = [max((name for name in expected if ('data/map_pack/' + family) in name
                         and rows[name]['bytes'] > 200 and not name.endswith('.empty.json')),
                        key=lambda name: rows[name]['bytes']) for family in families]
        for name in ['index.html', 'manifest.webmanifest', 'release-manifest.json'] + selected:
            with urlopen(Request(origin + '/' + name, headers={'Accept-Encoding': 'gzip'}), timeout=60) as response:
                wire = response.read()
                encoded = response.headers.get('Content-Encoding', '')
                raw = gzip.decompress(wire) if encoded == 'gzip' else wire
                assert response.status == 200
                if name in expected:
                    assert encoded == 'gzip', 'Map transport header absent: ' + name
                    if name.endswith('.json'):
                        assert 'json' in response.headers.get('Content-Type', '')
                if name in rows:
                    assert sha(raw) == rows[name]['sha256'], 'HTTP decoded SHA differs: ' + name
                checked_http.append({'path': name, 'contentEncoding': encoded or 'identity', 'decodedBytes': len(raw), 'sha256': sha(raw)})
        for name in audits:
            with urlopen(origin + '/__mistral/' + name, timeout=60) as response:
                report = json.loads(response.read())
                assert report['auditMode'] == 'immutable-build' and report['inspectedAt']
                assert report['sourceCommit'] == manifest['sourceCommit']
    print(json.dumps({'sourceCommit': manifest['sourceCommit'], 'runtimeFilesChecked': len(expected),
                      'decodedBytes': manifest['runtimeDataDecodedBytes'], 'wireBytes': manifest['runtimeDataTransportBytes'],
                      'httpChecks': checked_http}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
