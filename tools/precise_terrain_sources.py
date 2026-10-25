#!/usr/bin/env python3
"""Verify/install the separate native LiDAR runtime atlas; never acquire data."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'data/map_pack/precision_archives/manifest.json'
MAX_MEMBER = 8 * 1024**2
MAX_TOTAL = 256 * 1024**2


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024**2), b''):
            h.update(part)
    return h.hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def safe_path(value):
    return (isinstance(value, str) and value.startswith('data/map_pack/precise/')
            and '\\' not in value and '..' not in PurePosixPath(value).parts
            and not PurePosixPath(value).is_absolute())


def manifest(root):
    path = Path(root) / MANIFEST
    if not path.is_file():
        return None
    value = json.loads(path.read_text())
    if value.get('schemaVersion') != 1 or not isinstance(value.get('archives'), list) or not 1 <= len(value['archives']) <= 64:
        raise ValueError('Invalid native terrain archive manifest')
    seen, total = set(), 0
    for archive in value['archives']:
        name = archive.get('path', '')
        if not name.startswith('data/map_pack/precision_archives/') or not name.endswith('.zip') or '..' in PurePosixPath(name).parts or '\\' in name:
            raise ValueError('Unsafe native terrain archive path')
        for row in archive.get('files', []):
            if not safe_path(row.get('path')) or row['path'] in seen or type(row.get('bytes')) is not int or not 0 < row['bytes'] <= MAX_MEMBER or len(row.get('sha256', '')) != 64:
                raise ValueError('Invalid or duplicated native terrain member')
            seen.add(row['path']); total += row['bytes']
    if total > MAX_TOTAL or not seen:
        raise ValueError('Native terrain expanded size exceeds budget')
    return value


def prepare_if_bundled(root=ROOT):
    root = Path(root)
    value = manifest(root)
    if value is None:
        return {'present': False, 'installed': 0}
    installed = 0
    for archive in value['archives']:
        path = root / archive['path']
        if not path.is_file() or path.stat().st_size != archive['bytes'] or digest(path) != archive['sha256']:
            raise ValueError('Native terrain archive differs from its receipt: ' + archive['path'])
        with zipfile.ZipFile(path) as bundle:
            rows = archive['files']
            if len(bundle.namelist()) != len(rows) or set(bundle.namelist()) != {r['path'] for r in rows}:
                raise ValueError('Native terrain archive inventory differs')
            for row in rows:
                target = root / row['path']
                if not target.resolve().is_relative_to(root.resolve()):
                    raise ValueError('Native terrain target escapes the selected installation root')
                if target.is_file():
                    if target.stat().st_size != row['bytes'] or digest(target) != row['sha256']:
                        raise ValueError('Existing native terrain file is altered: ' + row['path'])
                    continue
                info = bundle.getinfo(row['path'])
                if info.file_size != row['bytes'] or info.file_size > MAX_MEMBER:
                    raise ValueError('Native terrain ZIP size differs')
                raw = bundle.read(info)
                if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
                    raise ValueError('Native terrain ZIP checksum differs')
                target.parent.mkdir(parents=True, exist_ok=True)
                fd, temporary = tempfile.mkstemp(prefix='.precise-', dir=target.parent)
                try:
                    with os.fdopen(fd, 'wb') as stream:
                        stream.write(raw)
                    os.replace(temporary, target)
                finally:
                    Path(temporary).unlink(missing_ok=True)
                installed += 1
    return {'present': True, 'installed': installed}


def audit_details(root=ROOT):
    root = Path(root)
    value = manifest(root)
    if value is None:
        return {'ok': True, 'present': False, 'chunks': 0}
    rows = [r for a in value['archives'] for r in a['files']]
    for row in rows:
        p = root / row['path']
        if not p.is_file() or p.stat().st_size != row['bytes'] or digest(p) != row['sha256']:
            raise ValueError('Native terrain installation is incomplete or altered: ' + row['path'])
    index_path = root / 'data/map_pack/precise/index.json'
    index = json.loads(index_path.read_text())
    return {'ok': True, 'present': True, 'indexSha256': digest(index_path), 'chunks': len(index['tiles']),
            'nativeSpacingMeters': index['nativeSpacingMeters'], 'sourceTiles': index['sourceTiles'],
            'coverageSquareMeters': index['coverageSquareMeters'], 'validPoints': index['validPoints'],
            'noDataPoints': index['noDataPoints'], 'runtimeBytes': sum(t['bytes'] for t in index['tiles']),
            'scope': 'Native numeric LiDAR HD MNT cells, Lambert-93 / IGN69; limited central Marseille coverage.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare_if_bundled(args.root)
    print(json.dumps(audit_details(args.root), ensure_ascii=False))


if __name__ == '__main__':
    main()
