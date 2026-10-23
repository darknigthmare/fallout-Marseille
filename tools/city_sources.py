#!/usr/bin/env python3
"""Validate, package and restore the complete bounded Marseille source index.

This archive is separate from the older regional enrichment archive. It never
replaces a valid user-installed dataset, and it refuses corrupted installations.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile
import threading
import zipfile
import world_sources as geometry_schema

from world_sources import (SourceError, _checked_existing_provenance, _writer_lock, atomic_write,
                           bounded_bytes, canonical, checked_bbox, coverage_metadata, decode_json,
                           geometry, geometry_bbox, provenance)

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'data/map_pack/city/'
REGION = 'geo_marseille_commune'
MAX_MEMBERS = 4096
MAX_TOTAL = 1024 * 1024 * 1024
MAX_FILE = 64 * 1024 * 1024
NAME = re.compile(r'(?:index\.json|terrain-index\.json|water-index\.json|boundary-[0-9a-f]{16}\.json|terrain-[0-9a-f]{16}\.json|water-[0-9a-f]{16}\.json|m13055-r[0-9]{2}-c[0-9]{2}(?:-[0-3]){0,4}-[0-9a-f]{16}\.json)')
ID = re.compile(r'm13055-r[0-9]{2}-c[0-9]{2}(?:-[0-3]){0,4}')
_GEOMETRY_VALIDATED = {}
_GEOMETRY_LOCK = threading.Lock()
_GEOMETRY_VALIDATION_VERSION = 1


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def close_box(a, b):
    return len(a) == len(b) == 4 and all(abs(x - y) <= 1e-11 for x, y in zip(a, b))


def _read_descriptor(directory, descriptor, files):
    if not isinstance(descriptor, dict):
        raise SourceError('city descriptor is not an object')
    name = str(descriptor.get('path', ''))
    if not name.startswith(PREFIX) or not NAME.fullmatch(name[len(PREFIX):]):
        raise SourceError('city descriptor path is not a safe local content-addressed file')
    name = name[len(PREFIX):]
    digest = descriptor.get('sha256')
    if not re.fullmatch(r'[0-9a-f]{64}', str(digest)) or not name.endswith(digest[:16] + '.json'):
        raise SourceError('city descriptor does not match its content-addressed name')
    target = directory / name
    if target.is_symlink():
        raise SourceError('city file symlinks are refused')
    raw = bounded_bytes(target)
    if type(descriptor.get('bytes')) is not int or len(raw) != descriptor['bytes'] or sha(raw) != digest:
        raise SourceError('city byte count or SHA-256 mismatch: ' + name)
    files[name] = raw
    return decode_json(raw)


def _provider(provider):
    if not isinstance(provider, dict):
        raise SourceError('city source attribution is absent')
    return provenance(name=provider.get('name'), license=provider.get('license'), attribution=provider.get('attribution'),
                      acquired_at=provider.get('acquiredAt'), resource=provider.get('resource'),
                      url=provider.get('url'), vertical_datum=provider.get('verticalDatum'))


def _complete_leaves(base, leaves, suffix=''):
    key = base + suffix
    if key in leaves:
        if any(row.startswith(key + '-') for row in leaves):
            raise SourceError('city query has overlapping parent and child rectangles')
        return
    if len(suffix) >= 8 or not any(row.startswith(key + '-') for row in leaves):
        raise SourceError('city acquisition does not cover every administrative query rectangle')
    for digit in '0123':
        _complete_leaves(base, leaves, suffix + '-' + digit)


def _rectangle_touches_polygon(box, shape):
    """Pure counterpart of the acquisition plan; no acquisition CLI imports.

    Keep the exact conservative predicates used by acquire_city_world. Runtime
    restoration must work with this atlas alone, without regional manifests.
    """
    south, west, north, east = box
    corners = [[west, south], [east, south], [east, north], [west, north]]
    polygons = shape['coordinates'] if shape['type'] == 'MultiPolygon' else [shape['coordinates']]
    for polygon in polygons:
        outer = polygon[0]
        bounds = [min(p[1] for p in outer), min(p[0] for p in outer),
                  max(p[1] for p in outer), max(p[0] for p in outer)]
        if not geometry_schema.intersects(box, bounds):
            continue
        if any(west <= p[0] <= east and south <= p[1] <= north for p in outer):
            return True
        if any(geometry_schema._point_inside(outer, p)
               and not any(geometry_schema._point_inside(hole, p) for hole in polygon[1:])
               for p in corners):
            return True
        for ring in polygon:
            for a, b in zip(ring, ring[1:]):
                if max(a[0], b[0]) < west or min(a[0], b[0]) > east or max(a[1], b[1]) < south or min(a[1], b[1]) > north:
                    continue
                if any(geometry_schema._segments_intersect(a, b, c, d)
                       for c, d in zip(corners, corners[1:] + corners[:1])):
                    return True
    return False


def _partition(bounds, shape, step=.025):
    if not math.isfinite(step) or not .005 <= step <= .05:
        raise ValueError('partition step must be between .005 and .05 degrees')
    s, w, n, e = checked_bbox(bounds)
    rows, cols = math.ceil((n - s) / step), math.ceil((e - w) / step)
    result = []
    for row in range(rows):
        for col in range(cols):
            box = [s + (n - s) * row / rows, w + (e - w) * col / cols,
                   s + (n - s) * (row + 1) / rows, w + (e - w) * (col + 1) / cols]
            if _rectangle_touches_polygon(box, shape):
                result.append({'id': f'm13055-r{row:02d}-c{col:02d}', 'queryBbox': box})
    if not result or len(result) > 1024:
        raise ValueError('municipality plan is empty or exceeds the partition budget')
    return result


def _split(tile):
    s, w, n, e = tile['queryBbox']
    m, k = (s + n) / 2, (w + e) / 2
    return [{'id': tile['id'] + '-' + str(i), 'queryBbox': box}
            for i, box in enumerate(([s, w, m, k], [s, k, m, e], [m, w, n, k], [m, k, n, e]))]


def _check_terrain_seams(descriptors, edges):
    """Compare actual adjacent source nodes without importing acquisition CLIs."""
    same = lambda a, b: abs(a - b) <= 1e-11
    for offset, a in enumerate(descriptors):
        ab = a['bbox']
        for b in descriptors[offset + 1:]:
            bb, sides = b['bbox'], None
            if same(ab[0], bb[0]) and same(ab[2], bb[2]):
                if same(ab[3], bb[1]):
                    sides = ('east', 'west')
                elif same(ab[1], bb[3]):
                    sides = ('west', 'east')
            if same(ab[1], bb[1]) and same(ab[3], bb[3]):
                if same(ab[0], bb[2]):
                    sides = ('south', 'north')
                elif same(ab[2], bb[0]):
                    sides = ('north', 'south')
            if sides:
                left, right = edges[a['sha256']][sides[0]], edges[b['sha256']][sides[1]]
                if len(left) != len(right) or any(x != y for x, y in zip(left, right)):
                    raise SourceError('city fine terrain source samples disagree along a shared partition edge')


def validate_directory(directory):
    """Return exact referenced runtime files and their validated source records."""
    directory = Path(directory)
    if directory.is_symlink():
        raise SourceError('city source directory symlinks are refused')
    index_path = directory / 'index.json'
    if index_path.is_symlink():
        raise SourceError('city index symlink is refused')
    index_raw = bounded_bytes(index_path)
    if len(index_raw) > 1024 * 1024:
        raise SourceError('city index exceeds the one MiB runtime budget')
    index = decode_json(index_raw)
    if not isinstance(index, dict) or index.get('schemaVersion') != 1 or index.get('crs') != 'EPSG:4326' or index.get('region') != REGION:
        raise SourceError('city index schema or CRS is incompatible')
    city, coverage, tiles = index.get('municipality'), index.get('coverage'), index.get('tiles')
    if not isinstance(city, dict) or city.get('code') != '13055' or city.get('name') != 'Marseille':
        raise SourceError('city index must identify the official Marseille municipality')
    bounds = checked_bbox(city.get('bbox'))
    if not isinstance(coverage, dict) or coverage.get('complete') is not True or not isinstance(tiles, list) or not 1 <= len(tiles) <= 2048 or coverage.get('tileCount') != len(tiles):
        raise SourceError('city index does not certify a complete bounded tile set')
    files, providers = {'index.json': index_raw}, [_provider(city.get('source'))]
    boundary = _read_descriptor(directory, city.get('boundary'), files)
    rows = boundary.get('features') if isinstance(boundary, dict) else None
    if boundary.get('type') != 'FeatureCollection' or not isinstance(rows, list) or len(rows) != 1 or rows[0].get('properties', {}).get('code_insee') != '13055':
        raise SourceError('city boundary does not identify Marseille')
    boundary_geometry = rows[0].get('geometry')
    if not isinstance(boundary_geometry, dict) or boundary_geometry.get('type') not in ('Polygon', 'MultiPolygon') or not close_box(geometry_bbox(boundary_geometry), bounds):
        raise SourceError('city boundary extent differs from its index')
    polygons = boundary_geometry['coordinates'] if boundary_geometry['type'] == 'MultiPolygon' else [boundary_geometry['coordinates']]
    vertex_count = 0
    for polygon in polygons:
        if not isinstance(polygon, list) or not polygon:
            raise SourceError('city administrative polygon is empty')
        for ring in polygon:
            if not isinstance(ring, list) or len(ring) < 4 or ring[0] != ring[-1]:
                raise SourceError('city administrative polygon ring is unclosed')
            for point in ring:
                geometry_schema.position(point, 'EPSG:4326')
            vertex_count += len(ring)
    if vertex_count > 200_000:
        raise SourceError('city administrative boundary exceeds its bounded vertex budget')
    plan = _partition(bounds, boundary_geometry, coverage.get('partitionStepDegrees', .025))
    if coverage.get('queryTileCount') != len(plan):
        raise SourceError('administrative query plan count differs from its receipt')
    base_tiles = {row['id']: row for row in plan}
    leaves, unique, expanded = {}, {'building': {}, 'road': {}}, 0
    unavailable_z, administrative_border = set(), set()
    for descriptor in tiles:
        identity = descriptor.get('id')
        if not isinstance(identity, str) or not ID.fullmatch(identity) or identity in leaves or descriptor.get('region') != REGION:
            raise SourceError('city partition identity is invalid or duplicated')
        base = '-'.join(identity.split('-')[:3])
        if base not in base_tiles:
            raise SourceError('city partition lies outside the administrative query plan')
        expected = base_tiles[base]
        for digit in identity.split('-')[3:]:
            expected = _split(expected)[int(digit)]
        query = checked_bbox(descriptor.get('queryBbox'))
        if not close_box(expected['queryBbox'], query):
            raise SourceError('city partition extent differs from its subdivision identity')
        leaves[identity] = query
        bundle = _read_descriptor(directory, descriptor, files)
        if bundle.get('schemaVersion') != 1 or bundle.get('region') != REGION or not isinstance(bundle.get('features'), list) or len(bundle['features']) > 3000 or not close_box(bundle.get('queryBbox', []), query):
            raise SourceError('city partition bundle schema or feature budget is invalid')
        if len(files[Path(descriptor['path']).name]) > 8 * 1024 * 1024:
            raise SourceError('city partition exceeds its streaming byte budget')
        proofs = bundle.get('coverages')
        if not isinstance(proofs, list) or len(proofs) != 2 or proofs != descriptor.get('coverages'):
            raise SourceError('city partition has no matching complete two-layer query proofs')
        checked = [coverage_metadata(p, 'ign-bdtopo', region_bbox=bounds) for p in proofs]
        if {p['layer'] for p in checked} != {'BDTOPO_V3:batiment', 'BDTOPO_V3:troncon_de_route'} or any(not close_box(p['bbox'], query) for p in checked):
            raise SourceError('city partition layer proofs are incomplete')
        counts, seen, counter = {'buildings': 0, 'roads': 0}, set(), [0]
        # Hash verification above always precedes this cache. Only the costly
        # ring intersection checks are reused for identical previously accepted
        # bytes; new bytes and every index/provenance/coverage check still run.
        geometry_cache_key = (descriptor['sha256'], _GEOMETRY_VALIDATION_VERSION, 'EPSG:4326',
                              geometry_schema.MAX_FEATURES, geometry_schema.MAX_VERTICES, geometry_schema.MAX_RING_VERTICES)
        with _GEOMETRY_LOCK:
            geometry_previously_verified = geometry_cache_key in _GEOMETRY_VALIDATED
        chunk_bounds = checked_bbox(descriptor.get('bbox'))
        render_boxes = [query]
        for feature in bundle['features']:
            if not isinstance(feature, dict) or feature.get('type') != 'Feature' or not isinstance(feature.get('properties'), dict):
                raise SourceError('city partition has an invalid geographic feature')
            geom = feature['geometry'] if geometry_previously_verified else geometry(feature.get('geometry'), 'EPSG:4326', counter)
            props = feature['properties']
            kind = 'building' if geom['type'] in ('Polygon', 'MultiPolygon') else 'road'
            key = props.get('sourceId')
            if props.get('kind') != kind or not isinstance(key, str) or not key or (kind, key) in seen:
                raise SourceError('city source identity is invalid or duplicated inside a partition')
            seen.add((kind, key))
            proof = _checked_existing_provenance(props.get('provenance'))
            if proof.get('resource') != 'ign-bdtopo' or proof.get('coverage') not in checked:
                raise SourceError('city object does not retain its completed official query provenance')
            anomaly = proof.get('sourceGeometryZUnavailable')
            if anomaly is not None:
                unavailable_z.add((kind, key))
                if not isinstance(anomaly, dict) or props.get('methode_d_acquisition_altimetrique') != 'Pas de Z' or props.get('precision_altimetrique') != 9999 or type(anomaly.get('removedCoordinates')) is not int or anomaly['removedCoordinates'] <= 0 or not re.fullmatch(r'[0-9a-f]{64}', str(anomaly.get('originalFeatureSha256', ''))):
                    raise SourceError('city unavailable source Z has no matching explicit provider condition')
                values = anomaly.get('unavailableSourceValues')
                if not isinstance(values, list) or not values or any(type(value) not in (int, float) or value == -1000 or -100 < value < 9000 for value in values):
                    raise SourceError('city unavailable source Z receipt does not describe an out-of-range provider anomaly')
            if proof.get('sourceGeometryAdministrativeBorder'):
                administrative_border.add((kind, key))
            box = geometry_bbox(geom)
            if kind == 'building':
                render_boxes.append(box)
            if box[0] < chunk_bounds[0] - 1e-10 or box[1] < chunk_bounds[1] - 1e-10 or box[2] > chunk_bounds[2] + 1e-10 or box[3] > chunk_bounds[3] + 1e-10:
                raise SourceError('city descriptor fails to cover an entire source geometry')
            fingerprint = sha(canonical({'geometry': geom, 'properties': {k: v for k, v in props.items() if k != 'provenance'}}))
            if unique[kind].setdefault(key, fingerprint) != fingerprint:
                raise SourceError('city object changed between adjacent source queries')
            counts['buildings' if kind == 'building' else 'roads'] += 1
        if descriptor.get('counts') != counts or any(p['returned'] != counts['buildings' if p['layer'].endswith(':batiment') else 'roads'] for p in checked):
            raise SourceError('city partition source counts differ from their complete query proofs')
        render_bounds = [min(b[0] for b in render_boxes), min(b[1] for b in render_boxes), max(b[2] for b in render_boxes), max(b[3] for b in render_boxes)]
        if 'renderBbox' in descriptor and not close_box(checked_bbox(descriptor['renderBbox']), render_bounds):
            raise SourceError('city rendered extent differs from its whole buildings and clipped road queries')
        for provider in bundle.get('sources', []):
            checked_provider = _provider(provider)
            if checked_provider not in providers:
                providers.append(checked_provider)
        if not bundle.get('sources'):
            raise SourceError('city partition has no source attribution')
        with _GEOMETRY_LOCK:
            _GEOMETRY_VALIDATED[geometry_cache_key] = True
            while len(_GEOMETRY_VALIDATED) > 2048:
                _GEOMETRY_VALIDATED.pop(next(iter(_GEOMETRY_VALIDATED)))
        expanded += descriptor['bytes']
    for base in base_tiles:
        _complete_leaves(base, leaves)
    if coverage.get('uniqueBuildings') != len(unique['building']) or coverage.get('uniqueRoads') != len(unique['road']) or coverage.get('expandedBytes') != expanded:
        raise SourceError('city aggregate source counts or bytes differ from their receipt')
    if 'nonAcquiredZAnomalies' in coverage and coverage['nonAcquiredZAnomalies'] != len(unavailable_z) or 'administrativeEnvelopeBorderObjects' in coverage and coverage['administrativeEnvelopeBorderObjects'] != len(administrative_border):
        raise SourceError('city source anomaly counts differ from their preserved object provenance')
    terrain_path = directory / 'terrain-index.json'
    if terrain_path.exists() or terrain_path.is_symlink():
        if terrain_path.is_symlink():
            raise SourceError('city terrain index symlink is refused')
        terrain_raw = bounded_bytes(terrain_path)
        terrain_index = decode_json(terrain_raw)
        if terrain_index.get('schemaVersion') != 1 or terrain_index.get('region') != REGION or not close_box(terrain_index.get('bbox', []), bounds):
            raise SourceError('city terrain index does not cover the same administrative extent')
        files['terrain-index.json'] = terrain_raw
        no_data_descriptors = terrain_index.get('noDataTiles', [])
        if not isinstance(no_data_descriptors, list):
            raise SourceError('city NoData terrain receipt list is invalid')
        descriptors = ([terrain_index['base']] if terrain_index.get('base') else []) + terrain_index.get('tiles', []) + no_data_descriptors
        if not 1 <= len(descriptors) <= 2048:
            raise SourceError('city terrain index is empty or exceeds its tile budget')
        from world_sources import checked_terrain
        terrain_edges = {}
        for descriptor in descriptors:
            grid = _read_descriptor(directory, descriptor, files)
            proof = _checked_existing_provenance(grid.get('provenance'))
            provider = provenance(name=proof['source'], license=proof['license'], attribution=proof['attribution'], acquired_at=proof['acquiredAt'],
                                  resource=proof['resource'], url=proof.get('url'), vertical_datum=proof.get('verticalDatum'))
            if descriptor in no_data_descriptors:
                width, height, values = grid.get('width'), grid.get('height'), grid.get('values')
                if type(width) is not int or type(height) is not int or min(width, height) < 2 or width * height > 1_048_576 or not isinstance(values, list) or len(values) != width * height or any(value is not None for value in values):
                    raise SourceError('city NoData-only grid must preserve exactly its absent source samples')
                checked_bbox(grid.get('bbox'))
                if grid.get('rowOrder') != 'north-to-south' or grid.get('verticalDatum') != proof.get('verticalDatum') or grid.get('sourceResource') != proof.get('resource') or grid.get('validPoints') != 0 or grid.get('missingPoints') != width * height or type(proof.get('resampled')) is not bool:
                    raise SourceError('city NoData-only grid metadata differs from its official acquisition')
            else:
                checked_terrain(grid, REGION, provider, proof['inputSha256'], bounds)
            valid_samples = sum(value is not None for value in grid['values'])
            if grid.get('validPoints') != valid_samples or grid.get('missingPoints') != len(grid['values']) - valid_samples:
                raise SourceError('city terrain sample counts differ from its actual values')
            if any(key in grid for key in ('providerInvalidPoints', 'providerNoDataPoints')):
                invalid, absent = grid.get('providerInvalidPoints'), grid.get('providerNoDataPoints')
                if type(invalid) is not int or type(absent) is not int or min(invalid, absent) < 0 or invalid + absent + valid_samples != len(grid['values']):
                    raise SourceError('city terrain provider absence and invalid value counts differ from its samples')
                if any(descriptor.get(key) != grid[key] for key in ('providerInvalidPoints', 'providerNoDataPoints')):
                    raise SourceError('city terrain provider sample counts differ from its index descriptor')
            if not close_box(grid.get('bbox', []), checked_bbox(descriptor.get('bbox'))):
                raise SourceError('city terrain file extent differs from its descriptor')
            width = grid['width']
            terrain_edges[descriptor['sha256']] = {'north': grid['values'][:width], 'south': grid['values'][-width:],
                                                   'west': grid['values'][::width], 'east': grid['values'][width - 1::width]}
            if provider not in providers:
                providers.append(provider)
        terrain_coverage = terrain_index.get('coverage')
        if terrain_coverage is not None:
            if not isinstance(terrain_coverage, dict) or terrain_coverage.get('complete') is not True or not terrain_index.get('base') or not close_box(checked_bbox(terrain_index['base'].get('bbox')), bounds):
                raise SourceError('city complete terrain base must cover the entire municipality envelope')
            fine = terrain_index.get('tiles', []) + no_data_descriptors
            requested, completed = terrain_coverage.get('requestedFinePartitions'), terrain_coverage.get('completedFinePartitions')
            if type(requested) is not int or not 0 <= requested <= 2048 or type(completed) is not int or completed != len(fine) or not 0 <= completed <= requested or type(terrain_coverage.get('fineComplete')) is not bool:
                raise SourceError('city fine terrain counts differ from their actual referenced partitions')
            seen_terrain = set()
            area = 0
            for offset, descriptor in enumerate(fine):
                box = checked_bbox(descriptor.get('bbox'))
                if descriptor['sha256'] in seen_terrain or box[0] < bounds[0] - 1e-11 or box[1] < bounds[1] - 1e-11 or box[2] > bounds[2] + 1e-11 or box[3] > bounds[3] + 1e-11:
                    raise SourceError('city fine terrain partitions are duplicated or extend outside their complete envelope')
                seen_terrain.add(descriptor['sha256'])
                area += (box[2] - box[0]) * (box[3] - box[1])
                for previous in fine[:offset]:
                    other = previous['bbox']
                    if min(box[2], other[2]) - max(box[0], other[0]) > 1e-11 and min(box[3], other[3]) - max(box[1], other[1]) > 1e-11:
                        raise SourceError('city fine terrain partitions have overlapping interiors')
            if terrain_coverage['fineComplete']:
                if completed != requested or requested and not math.isclose(area, (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]), rel_tol=1e-9, abs_tol=1e-12):
                    raise SourceError('city completed fine terrain leaves an unmeasured query gap in its declared partition coverage')
                _check_terrain_seams(fine, terrain_edges)
    if (directory / 'water-index.json').exists() or (directory / 'water-index.json').is_symlink():
        from city_water_sources import validate_directory_files
        water_files, water_providers = validate_directory_files(directory)
        if set(water_files) & set(files) or any(not NAME.fullmatch(name) or len(raw) > MAX_FILE for name, raw in water_files.items()):
            raise SourceError('city water archive files collide or exceed the declared member schema')
        files.update(water_files)
        for provider in water_providers:
            provider = _provider(provider)
            if provider not in providers:
                providers.append(provider)
    if len(files) > MAX_MEMBERS or sum(map(len, files.values())) > MAX_TOTAL:
        raise SourceError('city dataset exceeds the member or expanded byte budget')
    return files, providers


def package(directory, archive_directory, replace=False):
    directory, archive_directory = map(Path, (directory, archive_directory))
    receipt_path = archive_directory / 'manifest.json'
    if receipt_path.exists() and not replace:
        raise SourceError('city receipt exists; explicit --replace is required')
    files, providers = validate_directory(directory)
    if 'terrain-index.json' in files:
        terrain_coverage = decode_json(files['terrain-index.json']).get('coverage', {})
        if terrain_coverage.get('fineComplete') is False and terrain_coverage.get('requestedFinePartitions', 0) > 0:
            raise SourceError('city fine terrain acquisition is still in progress; wait for its completed receipt before packaging')
    for name in ('index.json', 'terrain-index.json', 'water-index.json'):
        if name in files and (directory / name).read_bytes() != files[name]:
            raise SourceError('city index changed during archive validation; retry after publication finishes')
    archive_directory.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.city-sources-', suffix='.zip', dir=archive_directory)
    os.close(fd)
    temporary = Path(name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for name, raw in sorted(files.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                output.writestr(info, raw)
        archive_raw = temporary.read_bytes()
        digest = sha(archive_raw)
        archive = archive_directory / ('city-sources-' + digest[:16] + '.zip')
        if archive.exists() and archive.read_bytes() != archive_raw:
            raise SourceError('existing city archive conflicts with its content-addressed name')
        os.replace(temporary, archive)
        receipt = {'schemaVersion': 1, 'archive': archive.name, 'bytes': len(archive_raw), 'sha256': digest,
                   'members': [{'name': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(files.items())],
                   'sources': providers, 'scope': 'Complete authoritative Marseille WFS query partitions, whole returned objects, measured terrain and optional source-derived water atlas'}
        atomic_write(receipt_path, canonical(receipt))
        return receipt
    finally:
        temporary.unlink(missing_ok=True)


def read_package(receipt_path):
    receipt_path = Path(receipt_path)
    receipt = decode_json(bounded_bytes(receipt_path))
    name = receipt.get('archive')
    if receipt.get('schemaVersion') != 1 or not isinstance(name, str) or not re.fullmatch(r'city-sources-[0-9a-f]{16}\.zip', name):
        raise SourceError('city archive receipt is incompatible')
    target = receipt_path.parent / name
    if target.is_symlink() or not target.is_file() or not 0 < target.stat().st_size <= MAX_TOTAL:
        raise SourceError('city archive is missing, a symlink or over budget')
    raw = target.read_bytes()
    if type(receipt.get('bytes')) is not int or receipt['bytes'] != len(raw) or receipt.get('sha256') != sha(raw) or name != 'city-sources-' + sha(raw)[:16] + '.zip':
        raise SourceError('city archive byte count or SHA-256 mismatch')
    rows = receipt.get('members')
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_MEMBERS:
        raise SourceError('city archive member list is invalid')
    expected = {}
    for row in rows:
        member = row.get('name') if isinstance(row, dict) else None
        if not isinstance(member, str) or not NAME.fullmatch(member) or member in expected or type(row.get('bytes')) is not int or not 0 < row['bytes'] <= MAX_FILE or not re.fullmatch(r'[0-9a-f]{64}', str(row.get('sha256', ''))):
            raise SourceError('city archive has an unsafe, duplicate or oversized member')
        expected[member] = row
    if 'index.json' not in expected or sum(r['bytes'] for r in rows) > MAX_TOTAL:
        raise SourceError('city archive index missing or expanded byte budget exceeded')
    files = {}
    with zipfile.ZipFile(target) as archive:
        infos = archive.infolist()
        if len(infos) != len(expected) or {i.filename for i in infos} != set(expected):
            raise SourceError('city archive has undeclared, missing or duplicate members')
        for info in infos:
            row = expected[info.filename]
            if info.file_size != row['bytes'] or stat.S_ISLNK(info.external_attr >> 16):
                raise SourceError('city archive member size or type differs from its receipt')
            with archive.open(info) as stream:
                content = stream.read(row['bytes'] + 1)
            if len(content) != row['bytes'] or sha(content) != row['sha256']:
                raise SourceError('city archive member SHA-256 mismatch')
            files[info.filename] = content
    return receipt, files


def install(receipt_path, directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise SourceError('city installation destination symlink is refused')
    with _writer_lock(directory) if os.name == 'posix' else nullcontext():
        receipt, files = read_package(receipt_path)
        with tempfile.TemporaryDirectory(prefix='city-sources-check-') as temporary:
            stage = Path(temporary)
            for name, raw in files.items():
                (stage / name).write_bytes(raw)
            accepted, _ = validate_directory(stage)
            if set(accepted) != set(files):
                raise SourceError('city archive contains an unreferenced runtime file')
        if (directory / 'index.json').exists() or (directory / 'index.json').is_symlink():
            validate_directory(directory)
            return {'status': 'preserved', 'archive': receipt['archive']}
        for name, raw in files.items():
            if name in ('index.json', 'terrain-index.json', 'water-index.json'):
                continue
            destination = directory / name
            if destination.exists() or destination.is_symlink():
                if destination.is_symlink() or destination.read_bytes() != raw:
                    raise SourceError('city source file conflicts with the verified archive')
            else:
                atomic_write(destination, raw)
        if 'terrain-index.json' in files:
            atomic_write(directory / 'terrain-index.json', files['terrain-index.json'])
        if 'water-index.json' in files:
            atomic_write(directory / 'water-index.json', files['water-index.json'])
        atomic_write(directory / 'index.json', files['index.json'])
        return {'status': 'installed', 'files': len(files), 'archive': receipt['archive']}


def prepare_if_bundled(root):
    root = Path(root)
    receipt = root / 'data/map_pack/city_archives/manifest.json'
    if not receipt.exists():
        return None
    print('Vérification des sources de Marseille fournies…', flush=True)
    result = install(receipt, root / 'data/map_pack/city')
    print('Sources de Marseille fournies : ' + result['status'], flush=True)
    return result


def audit_details(directory):
    directory = Path(directory)
    if not (directory / 'index.json').exists() and not (directory / 'index.json').is_symlink():
        return {'ok': True, 'present': False, 'tileCount': 0, 'totalBuildings': 0, 'totalRoads': 0, 'terrain': {'present': False}}
    files, providers = validate_directory(directory)
    index = decode_json(files['index.json'])
    terrain = decode_json(files['terrain-index.json']) if 'terrain-index.json' in files else None
    water = decode_json(files['water-index.json']) if 'water-index.json' in files else None
    return {'ok': True, 'present': True, 'municipality': {k: index['municipality'][k] for k in ('code', 'name', 'bbox')},
            'coverage': index['coverage'], 'tileCount': len(index['tiles']),
            'totalBuildings': index['coverage']['uniqueBuildings'], 'totalRoads': index['coverage']['uniqueRoads'],
            'terrain': {'present': terrain is not None, 'base': terrain.get('base') if terrain else None,
                        'tileCount': len(terrain.get('tiles', [])) if terrain else 0,
                        'noDataTileCount': len(terrain.get('noDataTiles', [])) if terrain else 0,
                        'coverage': terrain.get('coverage') if terrain else None},
            'water': {'present': water is not None, 'tileCount': len(water.get('tiles', [])) if water else 0,
                      'source': water.get('source') if water else None, 'derivation': water.get('derivation') if water else None},
            'sources': providers, 'indexSha256': sha(files['index.json'])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['audit', 'pack', 'install'])
    parser.add_argument('--directory', type=Path, default=ROOT / 'data/map_pack/city')
    parser.add_argument('--archive-directory', type=Path, default=ROOT / 'data/map_pack/city_archives')
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = (package(args.directory, args.archive_directory, args.replace) if args.operation == 'pack' else
                  install(args.archive_directory / 'manifest.json', args.directory) if args.operation == 'install' else audit_details(args.directory))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (SourceError, OSError, ValueError, zipfile.BadZipFile) as error:
        print('Sources de Marseille refusées : ' + str(error))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
