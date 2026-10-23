#!/usr/bin/env python3
"""Package and restore validated local geographic sources, without network.

The checked-in receipt pins the complete ZIP and each accepted runtime file.
Existing, valid user imports are retained; invalid imports are never replaced
silently. Install the content-addressed files before atomically publishing their
index, just as the source importer does.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile
from contextlib import nullcontext

from world_sources import SourceError, _existing_bundle, _writer_lock, atomic_write, bounded_bytes, canonical, decode_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / 'data/map_pack/enrichment_archives/manifest.json'
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_MEMBERS = 32
NAME = re.compile(r'(?:index\.json|geo_[a-z0-9_]+-[0-9a-f]{16}\.json)')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_directory(directory):
    directory = Path(directory)
    if (directory / 'index.json').is_symlink():
        raise SourceError('source index symlink is not accepted')
    raw = bounded_bytes(directory / 'index.json')
    index = decode_json(raw)
    if not isinstance(index, dict) or index.get('schemaVersion') != 1 or index.get('crs') != 'EPSG:4326':
        raise SourceError('source index schema or CRS is invalid')
    regions = index.get('regions')
    if not isinstance(regions, dict) or not 1 <= len(regions) < MAX_MEMBERS:
        raise SourceError('source index must contain a bounded set of regions')
    files, sources = {'index.json': raw}, []
    for region, descriptor in sorted(regions.items()):
        if not isinstance(region, str) or not re.fullmatch(r'geo_[a-z0-9_]+', region):
            raise SourceError('invalid regional identifier')
        bundle, attribution = _existing_bundle(directory, region, descriptor)
        name = Path(descriptor['path']).name
        if not NAME.fullmatch(name):
            raise SourceError('source file must be a content-addressed regional bundle')
        files[name] = bounded_bytes(directory / name)
        for item in attribution:
            if item not in sources:
                sources.append(item)
    if sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise SourceError('source package exceeds the expanded byte budget')
    return files, sources


def package(directory, archive, receipt, replace=False):
    directory, archive, receipt = map(Path, (directory, archive, receipt))
    if archive.parent.resolve() != receipt.parent.resolve():
        raise SourceError('archive and receipt must share their local directory')
    if not replace and (archive.exists() or receipt.exists()):
        raise SourceError('archive or receipt exists; explicit --replace required')
    files, sources = validate_directory(directory)
    archive.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.world-sources-', suffix='.zip', dir=archive.parent)
    os.close(descriptor)
    temporary = Path(temporary)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for name, raw in sorted(files.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                output.writestr(info, raw)
        raw_archive = temporary.read_bytes()
        result = {'schemaVersion': 1, 'archive': archive.name, 'bytes': len(raw_archive), 'sha256': sha(raw_archive),
                  'members': [{'name': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(files.items())],
                  'sources': sources, 'scope': 'Verified runtime source extracts; source resolution and resampling are declared per grid'}
        # Content-addressed ZIP name makes publication safe even if a process
        # stops between archive and receipt writes. Old receipts keep working.
        expected_name = 'world-sources-' + result['sha256'][:16] + '.zip'
        actual_archive = archive.with_name(expected_name)
        if actual_archive.exists() and sha(actual_archive.read_bytes()) != result['sha256']:
            raise SourceError('existing archive conflicts with its content-addressed name')
        os.replace(temporary, actual_archive)
        result['archive'] = actual_archive.name
        atomic_write(receipt, canonical(result))
        return result
    finally:
        temporary.unlink(missing_ok=True)


def read_package(receipt):
    receipt = Path(receipt)
    obj = decode_json(bounded_bytes(receipt))
    if not isinstance(obj, dict) or obj.get('schemaVersion') != 1:
        raise SourceError('invalid source archive receipt')
    name = obj.get('archive')
    if not isinstance(name, str) or not re.fullmatch(r'world-sources-[0-9a-f]{16}\.zip', name):
        raise SourceError('archive must have a local content-addressed filename')
    archive = receipt.parent / name
    if archive.is_symlink() or not archive.is_file() or not 0 < archive.stat().st_size <= MAX_TOTAL_BYTES:
        raise SourceError('source archive is missing or exceeds its byte budget')
    raw = archive.read_bytes()
    if type(obj.get('bytes')) is not int or len(raw) != obj['bytes'] or sha(raw) != obj.get('sha256'):
        raise SourceError('source archive byte count or SHA-256 mismatch')
    rows = obj.get('members')
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_MEMBERS:
        raise SourceError('invalid source archive member list')
    expected = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('name'), str) or not NAME.fullmatch(row['name']) or row['name'] in expected:
            raise SourceError('unsafe or repeated source archive member')
        if type(row.get('bytes')) is not int or not 0 < row['bytes'] <= MAX_MEMBER_BYTES or not re.fullmatch(r'[0-9a-f]{64}', str(row.get('sha256', ''))):
            raise SourceError('source archive member bounds or digest invalid')
        expected[row['name']] = row
    if 'index.json' not in expected or sum(row['bytes'] for row in rows) > MAX_TOTAL_BYTES:
        raise SourceError('source archive index missing or expanded budget exceeded')
    files = {}
    with zipfile.ZipFile(archive) as source:
        infos = source.infolist()
        if len(infos) != len(expected) or {i.filename for i in infos} != set(expected):
            raise SourceError('source ZIP contains missing, duplicate or undeclared members')
        for info in infos:
            row = expected[info.filename]
            if info.file_size != row['bytes'] or stat.S_ISLNK(info.external_attr >> 16):
                raise SourceError('source ZIP size or member type differs from its receipt')
            with source.open(info) as stream:
                data = stream.read(row['bytes'] + 1)
            if len(data) != row['bytes'] or sha(data) != row['sha256']:
                raise SourceError('source ZIP member digest mismatch')
            files[info.filename] = data
    return obj, files


def install(receipt, directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise SourceError('source destination symlink is not accepted')
    # The POSIX importer uses the same lock. On Windows that importer refuses
    # publication; restoring the shipped immutable archive remains supported.
    with _writer_lock(directory) if os.name == 'posix' else nullcontext():
        return _install_locked(receipt, directory)


def _install_locked(receipt, directory):
    directory = Path(directory)
    obj, files = read_package(receipt)
    # Validate the full imported schema, geometry and provenance before touching
    # the destination, in addition to ZIP/byte/hash checks above.
    with tempfile.TemporaryDirectory(prefix='world-source-check-') as temporary:
        stage = Path(temporary)
        for name, raw in files.items():
            (stage / name).write_bytes(raw)
        validated, _ = validate_directory(stage)
        if set(validated) != set(files):
            raise SourceError('source archive has an unreferenced runtime file')
    if directory.is_symlink():
        raise SourceError('source destination symlink is not accepted')
    if (directory / 'index.json').exists() or (directory / 'index.json').is_symlink():
        validate_directory(directory)
        return {'status': 'preserved', 'reason': 'Existing validated user sources retained', 'archive': obj['archive']}
    directory.mkdir(parents=True, exist_ok=True)
    for name, raw in files.items():
        if name == 'index.json':
            continue
        destination = directory / name
        if destination.exists() or destination.is_symlink():
            if destination.is_symlink() or not destination.is_file() or destination.read_bytes() != raw:
                raise SourceError('existing source file conflicts with the verified archive')
        else:
            atomic_write(destination, raw)
    atomic_write(directory / 'index.json', files['index.json'])
    return {'status': 'installed', 'files': len(files), 'archive': obj['archive']}


def prepare_if_bundled(root):
    root = Path(root)
    receipt = root / 'data/map_pack/enrichment_archives/manifest.json'
    if not receipt.is_file():
        return None
    result = install(receipt, root / 'data/map_pack/enrichment')
    print('Sources géographiques fournies : ' + result['status'], flush=True)
    return result


def audit_details(directory):
    """A bounded read-only summary of verified files; no network or grid values."""
    directory = Path(directory)
    if not (directory / 'index.json').exists() and not (directory / 'index.json').is_symlink():
        return {'ok': True, 'present': False, 'regions': [], 'totalBuildings': 0, 'totalRoads': 0}
    files, sources = validate_directory(directory)
    index = decode_json(files['index.json'])
    regions = []
    for region, descriptor in sorted(index['regions'].items()):
        bundle = decode_json(files[Path(descriptor['path']).name])
        features = bundle.get('features', [])
        buildings = [f['properties'] for f in features if f['properties']['kind'] == 'building']
        roads = [f['properties'] for f in features if f['properties']['kind'] == 'road']
        coverage = []
        for feature in features:
            proof = feature['properties']['provenance']
            if proof.get('coverage'):
                row = {**proof['coverage'], 'source': proof['source'], 'acquiredAt': proof['acquiredAt']}
                if row not in coverage:
                    coverage.append(row)
        terrain = bundle.get('terrainTiles', [bundle['terrain']] if bundle.get('terrain') else [])
        grids = []
        for grid in terrain:
            south, west, north, east = grid['bbox']
            proof = grid['provenance']
            grids.append({'id': grid['macro'], 'width': grid['width'], 'height': grid['height'], 'bbox': grid['bbox'],
                          'validSamples': grid['validPoints'], 'noDataSamples': grid['missingPoints'],
                          'sourceResource': grid['sourceResource'], 'source': proof['source'],
                          'verticalDatum': grid['verticalDatum'], 'acquiredAt': proof['acquiredAt'],
                          'resolutionMeters': [(east - west) * 111320 * math.cos(math.radians((south + north) / 2)) / (grid['width'] - 1),
                                               (north - south) * 111320 / (grid['height'] - 1)],
                          'conversion': proof.get('conversion'), 'attribution': proof['attribution']})
        def positive_height(props):
            for key in ('height', 'hauteur', 'building:height'):
                value = props.get(key)
                if type(value) in (int, float) and math.isfinite(value) and value > 0:
                    return True
                if isinstance(value, str) and re.fullmatch(r'\s*\d+(?:[.,]\d+)?\s*(?:m|metres|meters)?\s*', value, re.IGNORECASE):
                    if float(re.sub(r'[^0-9.,]', '', value).replace(',', '.')) > 0:
                        return True
            return False
        regions.append({'id': region, 'sha256': descriptor['sha256'], 'source': bundle['source'],
                        'buildings': len(buildings), 'roads': len(roads), 'coverage': coverage, 'terrain': grids,
                        'estimatedBuildingHeights': sum(not positive_height(p) for p in buildings),
                        'unknownGeometryZ': sum(bool(f['properties']['provenance'].get('sourceGeometryZNoData')) for f in features)})
    return {'ok': True, 'present': True, 'regions': regions, 'sources': sources,
            'totalBuildings': sum(r['buildings'] for r in regions), 'totalRoads': sum(r['roads'] for r in regions)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    pack = sub.add_parser('pack')
    pack.add_argument('--directory', type=Path, default=ROOT / 'data/map_pack/enrichment')
    pack.add_argument('--archive', type=Path, required=True, help='Output directory and basename; final name is content-addressed')
    pack.add_argument('--receipt', type=Path, default=DEFAULT_RECEIPT)
    pack.add_argument('--replace', action='store_true')
    restore = sub.add_parser('install')
    restore.add_argument('--receipt', type=Path, default=DEFAULT_RECEIPT)
    restore.add_argument('--directory', type=Path, default=ROOT / 'data/map_pack/enrichment')
    args = parser.parse_args(argv)
    try:
        result = package(args.directory, args.archive, args.receipt, args.replace) if args.operation == 'pack' else install(args.receipt, args.directory)
    except (SourceError, OSError, ValueError, zipfile.BadZipFile) as error:
        print('Sources non installées : ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
