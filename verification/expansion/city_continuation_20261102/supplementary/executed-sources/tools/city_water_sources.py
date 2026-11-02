"""Read-only validation of the optional, source-derived Marseille sea atlas."""
from pathlib import Path
import hashlib
import json
import math
import re
from urllib.parse import urlsplit, parse_qs

from world_sources import SourceError, bounded_bytes, checked_bbox, geometry, geometry_bbox, geometry_positions, provenance

PREFIX = 'data/map_pack/city/'
BOUNDS = [43.1696313, 5.22875102, 43.39105653, 5.53254336]
NAME = re.compile(r'water-[0-9a-f]{16}\.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_directory_files(directory):
    directory = Path(directory)
    path = directory / 'water-index.json'
    if not path.exists() and not path.is_symlink():
        return {}, []
    if path.is_symlink():
        raise SourceError('water index symlinks are refused')
    raw = bounded_bytes(path)
    if len(raw) > 1024 * 1024:
        raise SourceError('water index exceeds one MiB')
    index = json.loads(raw)
    atlas_bounds=checked_bbox(index.get('bbox'))
    if index.get('schemaVersion') != 1 or index.get('crs') != 'EPSG:4326' or index.get('municipalityBbox') != BOUNDS or any(abs(a-b)>.04 for a,b in zip(atlas_bounds,BOUNDS)):
        raise SourceError('water atlas CRS or bounds are incompatible')
    source = index.get('source', {})
    provider = provenance(name=source.get('source'), license=source.get('license'), attribution=source.get('attribution'),
                          acquired_at=source.get('acquiredAt'), resource=source.get('resource'), url=source.get('url'))
    if provider['resource'] != 'ign-city-water' or index.get('derivation', {}).get('noSimplification') is not True:
        raise SourceError('water atlas source/derivation is absent')
    grid=index.get('grid',{})
    if grid.get('zoom')!=14 or any(type(grid.get(k)) is not int or not 0<=grid[k]<16384 for k in ['minX','maxX','minY','maxY']) or grid['minX']>grid['maxX'] or grid['minY']>grid['maxY'] or (grid['maxX']-grid['minX']+1)*(grid['maxY']-grid['minY']+1)>1024:
        raise SourceError('water atlas grid is incompatible')
    def tile_bounds(x,y):
        lat=lambda row:math.degrees(math.atan(math.sinh(math.pi*(1-2*row/16384))))
        return[lat(y+1),x/16384*360-180,lat(y),(x+1)/16384*360-180]
    corner_a=tile_bounds(grid['minX'],grid['maxY']);corner_b=tile_bounds(grid['maxX'],grid['minY'])
    if any(abs(a-b)>1e-11 for a,b in zip(atlas_bounds,[corner_a[0],corner_a[1],corner_b[2],corner_b[3]])):
        raise SourceError('water atlas bounds differ from its XYZ grid')
    tiles, inputs = index.get('tiles'), index.get('inputs')
    if not isinstance(tiles, list) or not 1 <= len(tiles) <= 1024 or not isinstance(inputs, list) or len(inputs) != 2:
        raise SourceError('water atlas tile or input budget exceeded')
    files, used, input_layers = {'water-index.json': raw}, set(), set()
    def read(descriptor):
        name = str(descriptor.get('path', ''))
        if not name.startswith(PREFIX) or not NAME.fullmatch(name[len(PREFIX):]):
            raise SourceError('unsafe water atlas path')
        name = name[len(PREFIX):]
        digest = descriptor.get('sha256')
        if name in used or not re.fullmatch('[0-9a-f]{64}', str(digest)) or not name.endswith(digest[:16] + '.json'):
            raise SourceError('duplicate or non-addressed water descriptor')
        used.add(name)
        target = directory / name
        if target.is_symlink():
            raise SourceError('water atlas symlink refused')
        value = bounded_bytes(target)
        if type(descriptor.get('bytes')) is not int or len(value) != descriptor['bytes'] or len(value) > 8 * 1024 * 1024 or sha(value) != digest:
            raise SourceError('water atlas byte/SHA mismatch')
        files[name] = value
        return json.loads(value)
    for descriptor in inputs:
        value = read(descriptor)
        body = str(value.get('body', '')).encode('utf-8')
        url = urlsplit(str(value.get('url', '')))
        query = parse_qs(url.query)
        if value.get('role') != 'source-response' or url.scheme != 'https' or url.hostname != 'data.geopf.fr' or url.path != '/wfs/ows' or not body or len(body) != value.get('bytes') or sha(body) != value.get('sha256'):
            raise SourceError('water source input receipt invalid')
        payload = json.loads(body)
        rows = payload.get('features')
        if not isinstance(rows, list) or type(payload.get('numberMatched')) is not int or payload['numberMatched'] != len(rows) or payload.get('numberReturned') != len(rows):
            raise SourceError('water source query is incomplete')
        layer = query.get('TYPENAMES', [''])[0]
        input_layers.add(layer)
        if layer not in ('BDCARTO_V5:occupation_du_sol', 'BDTOPO_V3:limite_terre_mer'):
            raise SourceError('water source layer is unexpected')
        if query.get('SRSNAME')!=['EPSG:4326'] or payload.get('crs',{}).get('properties',{}).get('name')!='urn:ogc:def:crs:EPSG::4326':
            raise SourceError('water source input CRS is incompatible')
        seen_ids=set();input_vertices=0
        for feature in rows:
            props=feature.get('properties',{});geom=feature.get('geometry',{});identity=feature.get('id')
            if feature.get('type')!='Feature' or not isinstance(identity,str) or identity in seen_ids:
                raise SourceError('water source feature identity is invalid')
            seen_ids.add(identity)
            if layer.startswith('BDCARTO') and (props.get('nature')!='Eau libre' or geom.get('type') not in ('Polygon','MultiPolygon')) or layer.startswith('BDTOPO') and (props.get('niveau')!='Plus hautes eaux' or geom.get('type') not in ('LineString','MultiLineString')):
                raise SourceError('water source query returned an unexpected classification')
            points=list(geometry_positions(geom.get('coordinates')))
            input_vertices+=len(points)
            if not points or input_vertices>250000 or any(len(p)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in p) or not -180<=p[0]<=180 or not -90<=p[1]<=90 for p in points):
                raise SourceError('water source input has invalid coordinates')
    if input_layers != {'BDCARTO_V5:occupation_du_sol', 'BDTOPO_V3:limite_terre_mer'}:
        raise SourceError('water atlas lacks its coast and open-water inputs')
    keys = set()
    for descriptor in tiles:
        b = checked_bbox(descriptor.get('bbox'))
        if any((b[0] < atlas_bounds[0] - 1e-10, b[1] < atlas_bounds[1] - 1e-10, b[2] > atlas_bounds[2] + 1e-10, b[3] > atlas_bounds[3] + 1e-10)):
            raise SourceError('water tile lies outside the declared clipped atlas')
        tile = descriptor.get('tile', {})
        key = (tile.get('z'), tile.get('x'), tile.get('y'))
        if key in keys or key[0] != 14 or any(type(n) is not int for n in key):
            raise SourceError('water tile coordinate is invalid or repeated')
        if not grid['minX']<=key[1]<=grid['maxX'] or not grid['minY']<=key[2]<=grid['maxY'] or any(abs(a-c)>1e-11 for a,c in zip(b,tile_bounds(key[1],key[2]))):
            raise SourceError('water tile bounds differ from their XYZ coordinate')
        keys.add(key)
        value = read(descriptor)
        if value.get('schemaVersion') != 1 or value.get('role') != 'water-tile' or value.get('tile') != tile or value.get('bbox') != b or value.get('source') != source:
            raise SourceError('water tile metadata differs from its receipt')
        features = value.get('features')
        if not isinstance(features, list) or not features or len(features) > 512:
            raise SourceError('water tile has no bounded polygon set')
        counter = [0]
        for feature in features:
            if feature.get('type') != 'Feature' or feature.get('properties', {}).get('kind') != 'water' or feature['properties'].get('v051Water') is not True or feature['properties'].get('provenance') != source:
                raise SourceError('water polygon has no matching authoritative provenance')
            geom = geometry(feature.get('geometry'), 'EPSG:4326', counter)
            if geom['type'] not in ('Polygon', 'MultiPolygon'):
                raise SourceError('water feature is not polygonal')
            extent = geometry_bbox(geom)
            if any((extent[0] < b[0] - 1e-10, extent[1] < b[1] - 1e-10, extent[2] > b[2] + 1e-10, extent[3] > b[3] + 1e-10)):
                raise SourceError('water polygon exceeds its clipping boundary')
        if descriptor.get('features') != len(features) or descriptor.get('vertices') != counter[0]:
            raise SourceError('water tile source counts differ')
    return files, [provider]
