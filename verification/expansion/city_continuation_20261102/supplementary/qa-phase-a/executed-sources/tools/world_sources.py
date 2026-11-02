"""Bounded, offline import primitives for measured geographic enrichment.

Imports never fetch a URL, infer an elevation, simplify a footprint, or fill
NoData. WGS84 coordinates remain in their original order, including inner rings.
"""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
import hashlib
import json
import math
import os
import re
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_FEATURES = 20_000
MAX_VERTICES = 250_000
MAX_RING_VERTICES = 2048
MAX_GRID_CELLS = 1_048_576
MAX_TERRAIN_TILES = 16
MAX_TERRAIN_CELLS = 4_194_304
FORBIDDEN_KEYS = {"__proto__", "prototype", "constructor"}


class SourceError(ValueError):
    """An input cannot be imported without inventing or weakening its data."""


def finite(value, label="number"):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise SourceError(f"{label} must be a finite number")
    return float(value)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def bounded_bytes(path: Path):
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_INPUT_BYTES:
        raise SourceError(f"input must be a nonempty file of at most {MAX_INPUT_BYTES} bytes: {path}")
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise SourceError("input grew beyond the byte limit")
    return raw


def safe_tree(value, depth=0):
    if depth > 16:
        raise SourceError("JSON nesting exceeds the supported depth")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key in FORBIDDEN_KEYS or len(key) > 256:
                raise SourceError("unsafe or oversized JSON property name")
            safe_tree(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            safe_tree(item, depth + 1)
    elif isinstance(value, str):
        if len(value) > 4096:
            raise SourceError("JSON string exceeds the supported length")
    elif value is not None and type(value) not in (bool, int, float):
        raise SourceError("unsupported JSON value")
    elif type(value) in (int, float) and not math.isfinite(value):
        raise SourceError("non-finite JSON number")


def decode_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise SourceError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        obj = json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(SourceError("non-finite JSON number")))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise SourceError(f"invalid JSON: {error}") from error
    safe_tree(obj)
    return obj


def provenance(*, name, license, attribution, acquired_at, resource="local-survey", url=None, vertical_datum=None):
    result = {}
    for key, value in (("name", name), ("license", license), ("attribution", attribution), ("acquiredAt", acquired_at), ("resource", resource)):
        if not isinstance(value, str) or not value.strip() or len(value) > 1024:
            raise SourceError(f"source {key} must be explicitly supplied")
        result[key] = value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", result["acquiredAt"]):
        raise SourceError("acquired-at must be an ISO date YYYY-MM-DD")
    try:
        dt.date.fromisoformat(result["acquiredAt"])
    except ValueError as error:
        raise SourceError("acquired-at must be an ISO date YYYY-MM-DD") from error
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", result["resource"]):
        raise SourceError("source resource must be a stable provider identifier")
    if url:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise SourceError("source URL must be HTTPS and contain no credentials, query or fragment")
        result["url"] = url
    if vertical_datum:
        if not isinstance(vertical_datum, str) or not vertical_datum.strip() or len(vertical_datum) > 256:
            raise SourceError("invalid vertical datum")
        result["verticalDatum"] = vertical_datum.strip()
    return result


def checked_bbox(value):
    if not isinstance(value, list) or len(value) != 4:
        raise SourceError("bbox must be [south, west, north, east]")
    south, west, north, east = map(finite, value)
    if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise SourceError("invalid WGS84 extent")
    return [south, west, north, east]


def intersects(a, b):
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]


def lambert93_to_wgs84(x, y):
    """Inverse EPSG:2154, on the GRS80 ellipsoid; no spherical shortcut."""
    x, y = finite(x, "Lambert x"), finite(y, "Lambert y")
    if not (-500_000 <= x <= 2_000_000 and 5_000_000 <= y <= 8_000_000):
        raise SourceError("coordinates lie outside the supported Lambert-93 area")
    n, c, xs, ys, eccentricity = .7256077650532670, 11754255.426096, 700000., 12655612.049876, .0818191910428158
    radius = math.hypot(x - xs, y - ys)
    longitude = math.radians(3) + math.atan2(x - xs, ys - y) / n
    iso = -math.log(radius / c) / n
    latitude = 2 * math.atan(math.exp(iso)) - math.pi / 2
    for _ in range(12):
        sinphi = eccentricity * math.sin(latitude)
        updated = 2 * math.atan(math.exp(iso) * ((1 + sinphi) / (1 - sinphi)) ** (eccentricity / 2)) - math.pi / 2
        if abs(updated - latitude) < 1e-13:
            latitude = updated
            break
        latitude = updated
    return [math.degrees(longitude), math.degrees(latitude)]


def position(value, crs):
    if not isinstance(value, list) or len(value) not in (2, 3):
        raise SourceError("GeoJSON positions must have two or three coordinates")
    x, y = finite(value[0], "longitude/easting"), finite(value[1], "latitude/northing")
    result = lambert93_to_wgs84(x, y) if crs == "EPSG:2154" else [x, y]
    if not (-180 <= result[0] <= 180 and -90 <= result[1] <= 90):
        raise SourceError("position outside WGS84; supply the correct input CRS")
    if len(value) == 3:
        altitude = finite(value[2], "source elevation")
        if not -100 < altitude < 9000:
            raise SourceError("3D source elevation is outside the supported altitude range")
        result.append(altitude)
    return result


def _orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, p):
    return abs(_orientation(a, b, p)) <= 1e-14 and min(a[0], b[0]) - 1e-14 <= p[0] <= max(a[0], b[0]) + 1e-14 and min(a[1], b[1]) - 1e-14 <= p[1] <= max(a[1], b[1]) + 1e-14


def _segments_intersect(a, b, c, d):
    first, second, third, fourth = _orientation(a, b, c), _orientation(a, b, d), _orientation(c, d, a), _orientation(c, d, b)
    if first * second < 0 and third * fourth < 0:
        return True
    return any((abs(o) <= 1e-14 and _on_segment(u, v, p)) for o, u, v, p in ((first, a, b, c), (second, a, b, d), (third, c, d, a), (fourth, c, d, b)))


def _point_inside(ring, point):
    hit = False
    for a, b in zip(ring, ring[1:]):
        if _on_segment(a, b, point):
            return False
        if (a[1] > point[1]) != (b[1] > point[1]) and point[0] < (b[0] - a[0]) * (point[1] - a[1]) / (b[1] - a[1]) + a[0]:
            hit = not hit
    return hit


def _segment_candidates(first, second=None):
    """Conservative AABB sweep; the exact intersection predicate stays below.

    Expand both segment boxes by the existing on-segment tolerance. This is a
    deliberate superset (not a new geometric tolerance): every candidate still
    passes through the unchanged _segments_intersect predicate. Sorting and
    pruning only avoid testing segments whose expanded boxes cannot meet.
    Coordinates, vertex order, adjacent-edge rules and source bytes are intact.
    """
    rows = []
    for origin, ring in enumerate((first,) if second is None else (first, second)):
        for i, (a, b) in enumerate(zip(ring, ring[1:])):
            rows.append((min(a[0], b[0]) - 1e-14, max(a[0], b[0]) + 1e-14,
                         min(a[1], b[1]) - 1e-14, max(a[1], b[1]) + 1e-14, origin, i))
    rows.sort(key=lambda row: row[0])
    active = []
    count = len(first) - 1
    for current in rows:
        xmin, xmax, ymin, ymax, origin, i = current
        active = [previous for previous in active if previous[1] >= xmin]
        for previous in active:
            if previous[3] < ymin or previous[2] > ymax:
                continue
            other_origin, j = previous[4], previous[5]
            if second is None:
                if abs(i - j) == 1 or (i == 0 and j == count - 1) or (j == 0 and i == count - 1):
                    continue
                yield i, j
            elif origin != other_origin:
                yield (i, j) if origin == 0 else (j, i)
        active.append(current)


def _rings_intersect(first, second):
    return any(_segments_intersect(first[i], first[i + 1], second[j], second[j + 1])
               for i, j in _segment_candidates(first, second))


def _ring(raw, crs, counter):
    if not isinstance(raw, list) or not 4 <= len(raw) <= MAX_RING_VERTICES:
        raise SourceError(f"polygon rings require 4..{MAX_RING_VERTICES} vertices")
    ring = [position(p, crs) for p in raw]
    counter[0] += len(ring)
    if counter[0] > MAX_VERTICES:
        raise SourceError("source exceeds the vertex budget")
    if ring[0] != ring[-1]:
        raise SourceError("polygon ring is not closed; no implicit closing edge is added")
    if any(a[:2] == b[:2] for a, b in zip(ring, ring[1:])):
        raise SourceError("polygon ring contains a zero-length edge")
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:])) / 2
    if abs(area) < 1e-14:
        raise SourceError("polygon ring has zero area")
    for i, j in _segment_candidates(ring):
        if _segments_intersect(ring[i], ring[i + 1], ring[j], ring[j + 1]):
            raise SourceError("polygon ring self-intersects")
    return ring


def _polygon(raw, crs, counter):
    if not isinstance(raw, list) or not raw:
        raise SourceError("polygon has no outer ring")
    rings = [_ring(r, crs, counter) for r in raw]
    for i, hole in enumerate(rings[1:], 1):
        if not _point_inside(rings[0], hole[0]):
            raise SourceError("polygon hole is not strictly inside its outer ring")
        for previous in rings[:i]:
            if _rings_intersect(hole, previous):
                raise SourceError("polygon rings intersect or touch")
        if any(_point_inside(previous, hole[0]) or _point_inside(hole, previous[0]) for previous in rings[1:i]):
            raise SourceError("polygon holes overlap or are nested")
    return rings


def _line(raw, crs, counter):
    if not isinstance(raw, list) or len(raw) < 2:
        raise SourceError("road lines require at least two vertices")
    counter[0] += len(raw)
    if counter[0] > MAX_VERTICES:
        raise SourceError("source exceeds the vertex budget")
    line = [position(p, crs) for p in raw]
    if any(a[:2] == b[:2] for a, b in zip(line, line[1:])):
        raise SourceError("road line contains a zero-length segment")
    return line


def geometry(raw, crs, counter):
    if not isinstance(raw, dict):
        raise SourceError("feature geometry must be an object")
    kind, coordinates = raw.get("type"), raw.get("coordinates")
    if kind == "Polygon":
        coordinates = _polygon(coordinates, crs, counter)
    elif kind == "MultiPolygon":
        if not isinstance(coordinates, list) or not coordinates:
            raise SourceError("empty MultiPolygon")
        coordinates = [_polygon(p, crs, counter) for p in coordinates]
    elif kind == "LineString":
        coordinates = _line(coordinates, crs, counter)
    elif kind == "MultiLineString":
        if not isinstance(coordinates, list) or not coordinates:
            raise SourceError("empty MultiLineString")
        coordinates = [_line(p, crs, counter) for p in coordinates]
    else:
        raise SourceError("only Polygon/MultiPolygon buildings and LineString/MultiLineString roads are supported")
    return {"type": kind, "coordinates": coordinates}


def geometry_positions(value):
    if isinstance(value, list) and value and type(value[0]) in (int, float):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from geometry_positions(item)


def geometry_bbox(geom):
    positions = list(geometry_positions(geom["coordinates"]))
    return [min(p[1] for p in positions), min(p[0] for p in positions), max(p[1] for p in positions), max(p[0] for p in positions)]


def _bdtopo_geometry_nodata(raw, props, source):
    """BD TOPO explicitly marks absent Z as -1000 with method 'Pas de Z'.

    Do not turn that sentinel into a measured altitude or reject its valid XY
    footprint. This is provider-specific and never a generic outlier filter.
    """
    if source.get("resource") != "ign-bdtopo" or props.get("methode_d_acquisition_altimetrique") != "Pas de Z" or not isinstance(raw, dict):
        return raw, 0
    removed = 0
    def coordinates(value):
        nonlocal removed
        if isinstance(value, list) and value and type(value[0]) in (int, float):
            if len(value) == 3 and value[2] == -1000:
                removed += 1
                return value[:2]
            return value
        return [coordinates(row) for row in value] if isinstance(value, list) else value
    return {**raw, "coordinates": coordinates(raw.get("coordinates"))}, removed


def coverage_metadata(raw, resource, returned=None, region_bbox=None):
    """A completed source query rectangle, never the union of its objects."""
    keys = {'bbox', 'crs', 'complete', 'layer', 'returned'}
    if not isinstance(raw, dict) or set(raw) != keys or resource != 'ign-bdtopo':
        raise SourceError('completed source coverage has missing/unsupported fields or provider')
    box = checked_bbox(raw['bbox'])
    if raw['complete'] is not True or raw['crs'] != 'EPSG:4326' or raw['layer'] not in ('BDTOPO_V3:batiment', 'BDTOPO_V3:troncon_de_route'):
        raise SourceError('source coverage must be a completed known BD TOPO WGS84 layer query')
    if type(raw['returned']) is not int or not 0 <= raw['returned'] <= MAX_FEATURES or returned is not None and raw['returned'] != returned:
        raise SourceError('source coverage count does not match its complete feature collection')
    if region_bbox is not None and not (region_bbox[0] <= box[0] < box[2] <= region_bbox[2] and region_bbox[1] <= box[1] < box[3] <= region_bbox[3]):
        raise SourceError('source coverage rectangle lies outside the selected region')
    return {**raw, 'bbox': box}


def read_geojson(raw, source, region_bbox, crs="EPSG:4326"):
    if crs not in ("EPSG:4326", "EPSG:2154"):
        raise SourceError("GeoJSON CRS must be EPSG:4326 or EPSG:2154")
    obj = decode_json(raw)
    if not isinstance(obj, dict) or obj.get("type") != "FeatureCollection" or not isinstance(obj.get("features"), list):
        raise SourceError("GeoJSON input must be a FeatureCollection")
    if "crs" in obj:
        declared = obj["crs"]
        expected = f"urn:ogc:def:crs:EPSG::{crs.split(':')[1]}"
        name = declared.get("properties", {}).get("name") if isinstance(declared, dict) else None
        if name not in (crs, expected, "urn:ogc:def:crs:OGC:1.3:CRS84" if crs == "EPSG:4326" else crs):
            raise SourceError("declared GeoJSON CRS differs from --crs")
    if not 1 <= len(obj["features"]) <= MAX_FEATURES:
        raise SourceError(f"GeoJSON needs 1..{MAX_FEATURES} features")
    counter, seen, output = [0], set(), []
    input_sha = hashlib.sha256(raw).hexdigest()
    proof = {"source": source["name"], **{k: v for k, v in source.items() if k != "name"}, "inputSha256": input_sha, "inputCrs": crs}
    if 'acquisitionCoverage' in obj:
        if crs != 'EPSG:4326':
            raise SourceError('completed WFS coverage expects an unmodified WGS84 input collection')
        proof['coverage'] = coverage_metadata(obj['acquisitionCoverage'], source.get('resource'), len(obj['features']), region_bbox)
    for feature in obj["features"]:
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise SourceError("invalid GeoJSON feature")
        props = feature.get("properties") or {}
        if not isinstance(props, dict):
            raise SourceError("feature properties must be an object")
        input_geometry, missing_z = _bdtopo_geometry_nodata(feature.get("geometry"), props, source)
        geom = geometry(input_geometry, crs, counter)
        inferred = "building" if geom["type"] in ("Polygon", "MultiPolygon") else "road"
        if 'coverage' in proof and proof['coverage']['layer'] != ('BDTOPO_V3:batiment' if inferred == 'building' else 'BDTOPO_V3:troncon_de_route'):
            raise SourceError('source coverage layer does not match its geographic feature type')
        if props.get("kind", inferred) != inferred:
            raise SourceError("feature kind disagrees with its geometry")
        original_id = feature.get("id", props.get("sourceId"))
        if original_id is None:
            original_id = "geometry:" + hashlib.sha256(canonical(feature["geometry"])).hexdigest()[:24]
        if type(original_id) not in (str, int) or not str(original_id) or len(str(original_id)) > 256:
            raise SourceError("invalid source feature identifier")
        identity = str(original_id)
        if identity in seen:
            raise SourceError(f"duplicate source feature identifier: {identity}")
        seen.add(identity)
        if not intersects(geometry_bbox(geom), region_bbox):
            raise SourceError(f"source feature {identity} does not intersect the selected region")
        if any(len(p) == 3 for p in geometry_positions(geom["coordinates"])) and not source.get("verticalDatum"):
            raise SourceError("3D geometry requires an explicit vertical datum")
        feature_proof = dict(proof)
        if missing_z:
            feature_proof["sourceGeometryZNoData"] = {"sentinel": -1000, "removedCoordinates": missing_z, "condition": "BD TOPO methode_d_acquisition_altimetrique = Pas de Z", "action": "XY preserved; absent Z omitted, no altitude supplied"}
        output.append({"type": "Feature", "id": identity, "geometry": geom, "properties": {**props, "kind": inferred, "sourceId": identity, "provenance": feature_proof}})
    return output


def conversion_metadata(raw, datum):
    """Keep an explicit converter receipt separate from the imported JSON hash."""
    keys = {"format", "inputSha256", "crs", "nativePixelSize", "nativeTransform", "sourceSize", "resampling", "sampleConvention", "requestedSpacingMeters", "actualSpacingMeters", "resampled", "nodataPreserved", "verticalDatum"}
    if not isinstance(raw, dict) or set(raw) != keys:
        raise SourceError("terrain conversion receipt has missing or unsupported fields")
    if raw["format"] != "GeoTIFF" or not isinstance(raw["inputSha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", raw["inputSha256"]):
        raise SourceError("terrain conversion receipt needs the original GeoTIFF SHA-256")
    if not isinstance(raw["crs"], str) or not re.fullmatch(r"EPSG:[0-9]{3,6}", raw["crs"]):
        raise SourceError("terrain conversion receipt needs an explicit EPSG CRS")
    for key, size in (("nativePixelSize", 2), ("nativeTransform", 6), ("actualSpacingMeters", 2)):
        row = raw[key]
        if not isinstance(row, list) or len(row) != size:
            raise SourceError(f"conversion {key} has the wrong dimension")
        values = [finite(x, key) for x in row]
        if key != "nativeTransform" and any(x <= 0 for x in values):
            raise SourceError(f"conversion {key} must be positive")
    size = raw["sourceSize"]
    if not isinstance(size, list) or len(size) != 2 or any(type(x) is not int or x <= 0 for x in size):
        raise SourceError("conversion sourceSize must contain positive integer dimensions")
    if finite(raw["requestedSpacingMeters"], "requested spacing") <= 0:
        raise SourceError("conversion requested spacing must be positive")
    if raw["resampling"] != "nearest" or raw["sampleConvention"] != "WGS84 regular nodes" or type(raw["resampled"]) is not bool or raw["nodataPreserved"] is not True:
        raise SourceError("unsupported terrain conversion sampling or NoData policy")
    if raw["verticalDatum"] != datum:
        raise SourceError("conversion vertical datum differs from the declared source")
    return dict(raw)


def checked_terrain(obj, region, source, input_sha, region_bbox):
    if not isinstance(obj, dict):
        raise SourceError("terrain must be a JSON object")
    width, height, values = obj.get("width"), obj.get("height"), obj.get("values")
    if type(width) is not int or type(height) is not int or min(width, height) < 2 or width * height > MAX_GRID_CELLS:
        raise SourceError("terrain dimensions exceed the supported grid budget")
    if not isinstance(values, list) or len(values) != width * height:
        raise SourceError("terrain value count does not match its grid")
    bbox = checked_bbox(obj.get("bbox"))
    if not intersects(bbox, region_bbox):
        raise SourceError("terrain does not intersect the selected region")
    if obj.get("rowOrder") != "north-to-south":
        raise SourceError("terrain rowOrder must be north-to-south")
    datum = source.get("verticalDatum")
    if not datum:
        raise SourceError("terrain requires an explicit vertical datum")
    supplied_datum = obj.get("verticalDatum")
    if supplied_datum is not None and supplied_datum != datum:
        raise SourceError("terrain vertical datum differs from declared source")
    clean = []
    for value in values:
        if value is None:
            clean.append(None)
            continue
        altitude = finite(value, "terrain altitude")
        if not -100 < altitude < 9000:
            raise SourceError("out-of-range altitude; use null for NoData")
        clean.append(altitude)
    valid = sum(v is not None for v in clean)
    if not valid:
        raise SourceError("terrain has no measured samples")
    result = {"macro": "enrichment:" + region, "width": width, "height": height, "bbox": bbox, "rowOrder": "north-to-south", "values": clean,
            "sourceResource": source["resource"], "verticalDatum": datum, "validPoints": valid, "missingPoints": len(clean) - valid,
            "sampleSpacingDegrees": [(bbox[3] - bbox[1]) / (width - 1), (bbox[2] - bbox[0]) / (height - 1)],
            "provenance": {"source": source["name"], **{k: v for k, v in source.items() if k != "name"}, "inputSha256": input_sha, "inputCrs": "EPSG:4326", "resampled": False}}
    if "conversion" in obj:
        receipt = conversion_metadata(obj["conversion"], datum)
        result["provenance"].update(conversion=receipt, resampled=receipt["resampled"])
    return result


def read_ascii_grid(raw, region, source, region_bbox, crs="EPSG:4326"):
    if crs != "EPSG:4326":
        raise SourceError("ASCII grids currently require EPSG:4326; reproject projected rasters explicitly with GDAL before import")
    try:
        lines = raw.decode("utf-8-sig").splitlines()
    except UnicodeError as error:
        raise SourceError("ASCII grid is not UTF-8") from error
    header, row_start = {}, 0
    known = {"ncols", "nrows", "xllcorner", "yllcorner", "xllcenter", "yllcenter", "cellsize", "nodata_value"}
    for i, line in enumerate(lines):
        fields = line.split()
        if not fields:
            continue
        key = fields[0].lower()
        if key not in known:
            row_start = i
            break
        if len(fields) != 2 or key in header:
            raise SourceError("invalid or duplicate ASCII grid header")
        try:
            header[key] = float(fields[1])
        except ValueError as error:
            raise SourceError("invalid ASCII header number") from error
    else:
        raise SourceError("ASCII grid has no samples")
    if not {"ncols", "nrows", "cellsize", "nodata_value"}.issubset(header):
        raise SourceError("ASCII grid header is incomplete")
    width, height, cell = header["ncols"], header["nrows"], header["cellsize"]
    if not all(math.isfinite(x) for x in header.values()) or not width.is_integer() or not height.is_integer() or min(width, height) < 2 or width * height > MAX_GRID_CELLS or cell <= 0:
        raise SourceError("invalid ASCII dimensions or cell size")
    width, height = int(width), int(height)
    for axis in ("x", "y"):
        if sum(axis + "ll" + suffix in header for suffix in ("corner", "center")) != 1:
            raise SourceError("ASCII origin needs exactly one corner or centre per axis")
    west = header.get("xllcenter", header.get("xllcorner", 0) + cell / 2)
    south = header.get("yllcenter", header.get("yllcorner", 0) + cell / 2)
    rows = [line.split() for line in lines[row_start:] if line.strip()]
    if len(rows) != height or any(len(row) != width for row in rows):
        raise SourceError("ASCII sample rows do not match declared dimensions")
    try:
        samples = [float(token) for row in rows for token in row]
    except ValueError as error:
        raise SourceError("invalid ASCII altitude") from error
    values = [None if value == header["nodata_value"] else value for value in samples]
    result = checked_terrain({"width": width, "height": height, "bbox": [south, west, south + cell * (height - 1), west + cell * (width - 1)], "rowOrder": "north-to-south", "values": values}, region, source, hashlib.sha256(raw).hexdigest(), region_bbox)
    result["provenance"].update(inputFormat="ESRI ASCII", originConvention="sample centres", originalCellSize=cell)
    return result


def read_terrain(raw, region, source, region_bbox, format="json", crs="EPSG:4326"):
    if format == "ascii":
        return read_ascii_grid(raw, region, source, region_bbox, crs)
    if crs != "EPSG:4326":
        raise SourceError("JSON grids require WGS84 regular sample coordinates")
    return checked_terrain(decode_json(raw), region, source, hashlib.sha256(raw).hexdigest(), region_bbox)


def atomic_write(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def _existing_bundle(output, region, descriptor):
    if not isinstance(descriptor, dict):
        raise SourceError("existing region descriptor is invalid")
    digest = descriptor.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise SourceError("existing bundle SHA-256 is missing or invalid")
    filename = f"{region}-{digest[:16]}.json"
    if descriptor.get("path") != "data/map_pack/enrichment/" + filename:
        raise SourceError("existing bundle path is not a local content-addressed region file")
    target = output / filename
    if target.is_symlink():
        raise SourceError("existing bundle symlink is not accepted")
    raw = bounded_bytes(target)
    if type(descriptor.get("bytes")) is not int or len(raw) != descriptor["bytes"] or hashlib.sha256(raw).hexdigest() != digest:
        raise SourceError("existing bundle byte count or SHA-256 does not match its index")
    bundle = decode_json(raw)
    if not isinstance(bundle, dict) or bundle.get("schemaVersion") != SCHEMA_VERSION or bundle.get("region") != region or not isinstance(bundle.get("features"), list):
        raise SourceError("existing bundle schema does not match this region")
    if len(bundle["features"]) > MAX_FEATURES:
        raise SourceError("existing bundle exceeds the feature budget")
    counter, seen = [0], set()
    for feature in bundle["features"]:
        if not isinstance(feature, dict) or feature.get("type") != "Feature" or not isinstance(feature.get("properties"), dict):
            raise SourceError("existing bundle contains an invalid feature")
        geom = geometry(feature.get("geometry"), "EPSG:4326", counter)
        props = feature["properties"]
        kind = "building" if geom["type"] in ("Polygon", "MultiPolygon") else "road"
        key = (props.get("kind"), props.get("sourceId"))
        if key[0] != kind or not isinstance(key[1], str) or not key[1] or key in seen:
            raise SourceError("existing bundle feature identity is invalid or duplicated")
        seen.add(key)
        _checked_existing_provenance(props.get("provenance"))
    _bundle_terrain_tiles(bundle, region)
    sources = bundle.get("sources", [bundle.get("source")])
    if not isinstance(sources, list) or not sources:
        raise SourceError("existing source attribution is missing")
    for provider in sources:
        if not isinstance(provider, dict):
            raise SourceError("existing source attribution is invalid")
        provenance(name=provider.get("name"), license=provider.get("license"), attribution=provider.get("attribution"), acquired_at=provider.get("acquiredAt"),
                   resource=provider.get("resource"), url=provider.get("url"), vertical_datum=provider.get("verticalDatum"))
    return bundle, sources


def _checked_existing_provenance(proof):
    if not isinstance(proof, dict):
        raise SourceError("existing measured data has no source provenance")
    provenance(name=proof.get("source"), license=proof.get("license"), attribution=proof.get("attribution"), acquired_at=proof.get("acquiredAt"),
               resource=proof.get("resource"), url=proof.get("url"), vertical_datum=proof.get("verticalDatum"))
    if not isinstance(proof.get("inputSha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", proof["inputSha256"]):
        raise SourceError("existing measured data has no valid original input SHA-256")
    if "conversion" in proof:
        receipt = conversion_metadata(proof["conversion"], proof.get("verticalDatum"))
        if proof.get("resampled") is not receipt["resampled"]:
            raise SourceError("existing terrain resampling claim differs from its conversion receipt")
    if 'coverage' in proof:
        coverage_metadata(proof['coverage'], proof['resource'])
    return proof


def _source_summary(sources):
    if len(sources) == 1:
        return sources[0]
    return {"name": "Sources multiples documentées", "resource": "mixed-sources", "license": "Voir les licences de chaque source et objet",
            "attribution": " · ".join(sorted({s["attribution"] for s in sources})), "acquiredAt": max(s["acquiredAt"] for s in sources)}


def terrain_digest(grid):
    """A grid's identity covers source, georeferencing and every sample."""
    keys = ('sourceResource', 'verticalDatum', 'width', 'height', 'bbox', 'rowOrder', 'values')
    try:
        return hashlib.sha256(canonical({key: grid[key] for key in keys})).hexdigest()
    except (KeyError, TypeError, ValueError) as error:
        raise SourceError('terrain digest cannot be computed from an incomplete grid') from error


def terrain_slot(grid):
    """Only the same provider/georeference/resolution/datum can update a slot."""
    try:
        return canonical({key: grid[key] for key in ('sourceResource', 'verticalDatum', 'width', 'height', 'bbox', 'rowOrder')})
    except (KeyError, TypeError, ValueError) as error:
        raise SourceError('terrain slot cannot be computed from an incomplete grid') from error


def _bundle_terrain_tiles(bundle, region, validate=True):
    entries = []
    if 'terrain' in bundle:
        entries.append((bundle['terrain'], False))
    if 'terrainTiles' in bundle:
        if not isinstance(bundle['terrainTiles'], list) or not bundle['terrainTiles']:
            raise SourceError('existing terrainTiles must be a nonempty array')
        entries.extend((grid, True) for grid in bundle['terrainTiles'])
    if len(entries) > MAX_TERRAIN_TILES:
        raise SourceError('regional terrain exceeds the tile count budget')
    unique, count = {}, 0
    for grid, multi in entries:
        if not isinstance(grid, dict):
            raise SourceError('existing terrain grid is invalid')
        if validate:
            expected = 'enrichment:' + region + (':' + terrain_digest(grid)[:16] if multi else '')
            if grid.get('macro') != expected:
                raise SourceError('existing terrain identity is invalid')
            proof = _checked_existing_provenance(grid.get('provenance'))
            provider = provenance(name=proof['source'], license=proof['license'], attribution=proof['attribution'], acquired_at=proof['acquiredAt'],
                                  resource=proof['resource'], url=proof.get('url'), vertical_datum=proof.get('verticalDatum'))
            checked_terrain(grid, region, provider, proof['inputSha256'], checked_bbox(grid.get('bbox')))
            if grid.get('sourceResource') != proof['resource']:
                raise SourceError('existing terrain resource differs from its source provenance')
        slot = terrain_slot(grid)
        if slot in unique:
            raise SourceError('existing terrain grids have duplicate source/resolution slots')
        unique[slot] = grid
        count += len(grid['values'])
    if count > MAX_TERRAIN_CELLS:
        raise SourceError('regional terrain exceeds the aggregate sample budget')
    return list(unique.values())


@contextmanager
def _writer_lock(output):
    """Kernel-owned advisory lock; crashed writers never leave an active lock."""
    try:
        import fcntl
    except ImportError as error:
        raise SourceError("source publication currently requires POSIX file locking") from error
    output.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output / ".import.lock", os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    locked = False
    try:
        deadline = time.monotonic() + 30
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise SourceError("another source import is still writing; retry after it finishes")
                time.sleep(.025)
        yield
    finally:
        if locked:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def publish_bundle(output, region, source, *, features=None, terrain=None, replace=False, merge=False):
    """Serialize read/merge/publish across processes; never unlink another lock."""
    output = Path(output)
    with _writer_lock(output):
        return _publish_bundle_unlocked(output, region, source, features=features, terrain=terrain, replace=replace, merge=merge)


def _publish_bundle_unlocked(output, region, source, *, features=None, terrain=None, replace=False, merge=False):
    """Validate first, write content-addressed data, then atomically switch index."""
    output = Path(output)
    if not re.fullmatch(r"geo_[a-z0-9_]+", region):
        raise SourceError("invalid region identifier")
    if replace and merge:
        raise SourceError("--merge and --replace are mutually exclusive")
    if not features and terrain is None:
        raise SourceError("no geographic data to publish")
    index_path = output / "index.json"
    index = {"schemaVersion": SCHEMA_VERSION, "crs": "EPSG:4326", "regions": {}}
    sources, merged_features = [source], features or []
    grids = [terrain] if terrain is not None else []
    if index_path.is_symlink():
        raise SourceError("existing index symlink is not accepted")
    if index_path.exists():
        index = decode_json(bounded_bytes(index_path))
        if not isinstance(index, dict) or index.get("schemaVersion") != SCHEMA_VERSION or index.get("crs") != "EPSG:4326" or not isinstance(index.get("regions"), dict):
            raise SourceError("existing enrichment index is invalid; preserved unchanged")
        existing = index["regions"].get(region)
        prior = prior_sources = None
        if (merge or replace) and existing is not None:
            prior, prior_sources = _existing_bundle(output, region, existing)
        if merge and prior is not None:
            by_id = {(f["properties"]["kind"], f["properties"]["sourceId"]): f for f in prior["features"]}
            for feature in merged_features:
                props = feature["properties"]
                key = (props["kind"], props["sourceId"])
                old = by_id.get(key)
                if old is not None and old["properties"]["provenance"]["resource"] != props["provenance"]["resource"]:
                    raise SourceError("feature ID collision between different providers; review sources and use an intentional replacement")
                by_id[key] = feature
            merged_features = [by_id[key] for key in sorted(by_id)]
            if len(merged_features) > MAX_FEATURES:
                raise SourceError("merged features exceed the runtime budget")
            by_slot = {terrain_slot(grid): grid for grid in _bundle_terrain_tiles(prior, region, validate=False)}
            for grid in grids:
                by_slot[terrain_slot(grid)] = grid
            grids = [by_slot[key] for key in sorted(by_slot)]
            unique = {canonical(s): s for s in prior_sources + sources}
            sources = [unique[key] for key in sorted(unique)]
    source = _source_summary(sources)
    bundle = {"schemaVersion": SCHEMA_VERSION, "region": region, "source": source, "sources": sources, "features": merged_features}
    if sum(1 for feature in merged_features for _ in geometry_positions(feature['geometry']['coordinates'])) > MAX_VERTICES:
        raise SourceError('merged geographic source exceeds the vertex budget')
    boxes = [geometry_bbox(f["geometry"]) for f in bundle["features"]]
    boxes.extend(f['properties']['provenance']['coverage']['bbox'] for f in bundle['features'] if 'coverage' in f['properties']['provenance'])
    if len(grids) > MAX_TERRAIN_TILES or sum(len(grid['values']) for grid in grids) > MAX_TERRAIN_CELLS:
        raise SourceError('regional terrain exceeds the tile or aggregate sample budget')
    if len(grids) == 1:
        bundle['terrain'] = {**grids[0], 'macro': 'enrichment:' + region}
    elif grids:
        bundle['terrainTiles'] = [{**grid, 'macro': 'enrichment:' + region + ':' + terrain_digest(grid)[:16]} for grid in grids]
    boxes.extend(grid['bbox'] for grid in grids)
    bbox = [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]
    raw = canonical(bundle)
    if len(raw) > MAX_INPUT_BYTES:
        raise SourceError("output bundle exceeds the runtime byte budget")
    digest = hashlib.sha256(raw).hexdigest()
    filename = f"{region}-{digest[:16]}.json"
    descriptor = {"path": "data/map_pack/enrichment/" + filename, "sha256": digest, "bytes": len(raw), "bbox": bbox,
                  "kinds": sorted({f["properties"]["kind"] for f in bundle["features"]} | ({"terrain"} if grids else set())), "source": source}
    existing = index["regions"].get(region)
    if existing is not None and existing != descriptor and not (replace or merge):
        raise SourceError("region already has another import; use --merge or --replace after reviewing source provenance")
    target = output / filename
    if target.is_symlink():
        raise SourceError("content-addressed output symlink is not accepted")
    if target.exists() and target.read_bytes() != raw:
        raise SourceError("existing content-addressed file differs; preserved unchanged")
    if not target.exists():
        atomic_write(target, raw)
    index["regions"][region] = descriptor
    atomic_write(index_path, canonical(index))
    return {"index": str(index_path), "bundle": str(target), "sha256": digest, "features": len(bundle["features"]),
            "terrainSamples": sum(len(grid['values']) for grid in grids), "terrainTileCount": len(grids), "source": source, "region": region}
