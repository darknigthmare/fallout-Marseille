"""Bounded official acquisition: axis order, pagination and honest resolution."""
import contextlib
import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import acquire_public_world as source

CAPABILITIES = b'<WFS_Capabilities xmlns="http://www.opengis.net/wfs/2.0"><FeatureTypeList><FeatureType><Name>BDTOPO_V3:batiment</Name></FeatureType></FeatureTypeList></WFS_Capabilities>'
LAYER = 'BDTOPO_V3:batiment'
BOUNDS = [43.296, 5.57, 43.297, 5.571]

BUILDING_SCHEMA = b'''<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" targetNamespace="BDTOPO_V3"><xsd:complexType name="batimentType"><xsd:sequence>
<xsd:element name="hauteur" type="xsd:double" nillable="true"/><xsd:element name="altitude_minimale_sol" type="xsd:double" nillable="true"/>
<xsd:element name="altitude_minimale_toit" type="xsd:double" nillable="true"/><xsd:element name="altitude_maximale_toit" type="xsd:double" nillable="true"/>
<xsd:element name="geometrie" type="gml:MultiSurfacePropertyType" nillable="true"/></xsd:sequence></xsd:complexType></xsd:schema>'''
ROAD_SCHEMA = b'''<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" targetNamespace="BDTOPO_V3"><xsd:complexType name="troncon_de_routeType"><xsd:sequence>
<xsd:element name="largeur_de_chaussee" type="xsd:double" nillable="true"/><xsd:element name="nombre_de_voies" type="xsd:int" nillable="true"/>
<xsd:element name="position_par_rapport_au_sol" type="xsd:string" nillable="true"/><xsd:element name="geometrie" type="gml:CurvePropertyType" nillable="true"/>
</xsd:sequence></xsd:complexType></xsd:schema>'''


def feature(i):
    return {'type': 'Feature', 'id': f'building.{i}', 'properties': {'hauteur': 7.2},
            'geometry': {'type': 'Polygon', 'coordinates': [[[5.57, 43.296], [5.571, 43.296], [5.571, 43.297], [5.57, 43.296]]]}}


class AcquisitionTests(unittest.TestCase):
    def test_actual_bdtopo_schema_names_are_read_before_promoting_measurements(self):
        calls=[]
        def fetch(url):
            calls.append(parse_qs(urlsplit(url).query))
            return BUILDING_SCHEMA
        schema=source.describe_feature_type(LAYER,fetch)
        self.assertEqual(calls[0]['REQUEST'],['DescribeFeatureType'])
        self.assertEqual(schema['schemaSha256'],hashlib.sha256(BUILDING_SCHEMA).hexdigest())
        self.assertIn('altitude_minimale_sol',{f['name'] for f in schema['fields']})
        self.assertNotIn('z_min_sol',{f['name'] for f in schema['fields']})
        self.assertEqual(source.validate_feature_schema('buildings',schema),schema)
        self.assertEqual(source.validate_feature_schema('roads',source.describe_feature_type('BDTOPO_V3:troncon_de_route',lambda _:ROAD_SCHEMA))['layer'],'BDTOPO_V3:troncon_de_route')

    def test_missing_or_mistyped_measured_schema_fields_are_refused(self):
        for raw in [BUILDING_SCHEMA.replace(b'altitude_minimale_sol',b'old_guessed_name'),BUILDING_SCHEMA.replace(b'type="xsd:double"',b'type="xsd:string"'),b'<ExceptionReport/>']:
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                source.validate_feature_schema('buildings',source.describe_feature_type(LAYER,lambda _:raw))

    def test_recording_fetch_preserves_exact_authoritative_response_and_query(self):
        with tempfile.TemporaryDirectory() as temporary:
            raw=b' exact response bytes\n'
            url=source.WFS+'?SERVICE=WFS&REQUEST=GetFeature'
            fetched=source.recording_fetch(Path(temporary),lambda _:raw)(url)
            self.assertEqual(fetched,raw)
            files=list(Path(temporary).glob('*.raw'))
            self.assertEqual(len(files),1)
            self.assertEqual(files[0].read_bytes(),raw)
            proof=json.loads(next(Path(temporary).glob('*.provenance.json')).read_text())
            self.assertEqual(proof['sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual(proof['bytes'],len(raw))
            self.assertEqual(proof['url'],url)

    def test_metre_grid_covers_both_bbox_edges_without_claiming_native_resolution(self):
        p = source.terrain_plan(BOUNDS, 2)
        self.assertEqual(p['bbox'], BOUNDS)
        self.assertGreaterEqual(p['width'], 41)
        self.assertGreaterEqual(p['height'], 57)
        self.assertIn('not a survey accuracy claim', p['sourceResolution'])
        self.assertLessEqual(p['points'], source.MAX_POINTS)

    def test_full_region_at_one_metre_is_rejected_instead_of_silently_downsampled(self):
        with self.assertRaisesRegex(ValueError, 'smaller bbox'):
            source.terrain_plan(source.REGIONS['geo_huveaune'], 1)

    def test_invalid_extent_and_spacing_refuse_before_network(self):
        for b in [[43, 5, 42, 6], [43, float('nan'), 44, 6], [90, 5, 91, 6]]:
            with self.assertRaises(ValueError):
                source.terrain_plan(b, 2)
        for spacing in [0, float('inf'), 201]:
            with self.assertRaises(ValueError):
                source.terrain_plan(BOUNDS, spacing)

    def test_wfs_uses_unambiguous_lon_lat_crs_and_declared_layer(self):
        calls = []
        def fetch(url):
            calls.append(parse_qs(urlsplit(url).query))
            if len(calls) == 1:
                return CAPABILITIES
            return json.dumps({'type': 'FeatureCollection', 'numberMatched': 1, 'features': [feature(1)]}).encode()
        result = source.fetch_features(LAYER, BOUNDS, fetch=fetch)
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['acquisitionCoverage'],{'bbox':BOUNDS,'crs':'EPSG:4326','complete':True,'layer':LAYER,'returned':1})
        self.assertEqual(calls[1]['BBOX'], ['5.57,43.296,5.571,43.297,urn:ogc:def:crs:OGC::CRS84'])
        self.assertEqual(calls[1]['SRSNAME'], ['urn:ogc:def:crs:OGC::CRS84'])

    def test_unknown_layer_does_not_issue_get_feature(self):
        calls = []
        def fetch(url):
            calls.append(url)
            return CAPABILITIES
        with self.assertRaisesRegex(ValueError, 'not advertised'):
            source.fetch_features('guessed:layer', BOUNDS, fetch=fetch)
        self.assertEqual(len(calls), 1)

    def test_complete_pagination_preserves_every_feature(self):
        starts = []
        def fetch(url):
            q = parse_qs(urlsplit(url).query)
            if q['REQUEST'] == ['GetCapabilities']:
                return CAPABILITIES
            start = int(q['STARTINDEX'][0]); starts.append(start)
            rows = [feature(i) for i in (range(1000) if start == 0 else [1000])]
            return json.dumps({'type': 'FeatureCollection', 'numberMatched': 1001, 'features': rows}).encode()
        data = source.fetch_features(LAYER, BOUNDS, fetch=fetch, pause=lambda _: None)
        self.assertEqual(starts, [0, 1000])
        self.assertEqual(len(data['features']), 1001)

    def test_repeated_page_fails_instead_of_reporting_complete(self):
        def fetch(url):
            if 'GetCapabilities' in url:
                return CAPABILITIES
            return json.dumps({'type': 'FeatureCollection', 'numberMatched': 'unknown', 'features': [feature(1), feature(2)]}).encode()
        with self.assertRaisesRegex(ValueError, 'repeated WFS page'):
            source.fetch_features(LAYER, BOUNDS, limit=2, fetch=fetch, pause=lambda _: None)

    def test_incomplete_advertised_count_fails(self):
        pages = iter([[feature(1)], []])
        def fetch(url):
            if 'GetCapabilities' in url:
                return CAPABILITIES
            return json.dumps({'type': 'FeatureCollection', 'numberMatched': 2, 'features': next(pages)}).encode()
        with self.assertRaisesRegex(ValueError, 'before its advertised'):
            source.fetch_features(LAYER, BOUNDS, fetch=fetch, pause=lambda _: None)

    def test_unknown_total_with_server_page_cap_does_not_truncate(self):
        pages = iter([[feature(1)], [feature(2)], []])
        def fetch(url):
            if 'GetCapabilities' in url:
                return CAPABILITIES
            return json.dumps({'type': 'FeatureCollection', 'numberMatched': 'unknown', 'features': next(pages)}).encode()
        rows = source.fetch_features(LAYER, BOUNDS, fetch=fetch, pause=lambda _: None)['features']
        self.assertEqual([r['id'] for r in rows], ['building.1', 'building.2'])

    def test_numeric_text_total_and_returned_count_are_checked(self):
        def fetch(url):
            if 'GetCapabilities' in url:
                return CAPABILITIES
            return b'{"type":"FeatureCollection","numberMatched":"10001","features":[]}'
        with self.assertRaisesRegex(ValueError, 'feature bound'):
            source.fetch_features(LAYER, BOUNDS, fetch=fetch)

    def test_service_exception_is_not_a_successful_empty_dataset(self):
        with self.assertRaisesRegex(ValueError, 'WFS capabilities'):
            source.wfs_layers(lambda _: b'<ExceptionReport/>')

    def test_zero_features_is_valid_only_when_advertised(self):
        def fetch(url):
            if 'GetCapabilities' in url:
                return CAPABILITIES
            return b'{"type":"FeatureCollection","numberMatched":0,"features":[]}'
        self.assertEqual(source.fetch_features(LAYER, BOUNDS, fetch=fetch)['features'], [])

    def test_dry_run_reports_plan_without_creating_downloads(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = source.main(['terrain', '--region', 'geo_huveaune', '--bbox', ','.join(map(str, BOUNDS)), '--spacing', '2', '--dry-run'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['endpoint'], source.terrain.OFFICIAL_API)

    def test_acquisition_and_real_importer_cli_accumulate_different_layers(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache, output = Path(temporary) / 'downloads', Path(temporary) / 'enrichment'
            arguments = ['--region', 'geo_huveaune', '--bbox', ','.join(map(str, BOUNDS)),
                         '--cache', str(cache), '--output', str(output)]
            building = feature(1)
            road = {'type': 'Feature', 'id': 'road.1', 'properties': {'largeur_de_chaussee': 6.5},
                    'geometry': {'type': 'LineString', 'coordinates': [[5.57, 43.296], [5.571, 43.297]]}}
            with contextlib.redirect_stdout(io.StringIO()):
                for kind, row in [('buildings', building), ('roads', road)]:
                    schema=source.describe_feature_type(LAYER,lambda _:BUILDING_SCHEMA if kind=='buildings' else ROAD_SCHEMA)
                    with patch.object(source,'wfs_layers',return_value=[LAYER,'BDTOPO_V3:troncon_de_route']),patch.object(source,'describe_feature_type',return_value=schema),patch.object(source, 'fetch_features', return_value={'type': 'FeatureCollection', 'features': [row]}):
                        self.assertEqual(source.main([kind] + arguments), 0)
            index = json.loads((output / 'index.json').read_text())
            descriptor = index['regions']['geo_huveaune']
            bundle = json.loads((output / Path(descriptor['path']).name).read_text())
            self.assertEqual({f['properties']['kind'] for f in bundle['features']}, {'building', 'road'})
            self.assertEqual(len(bundle['sources']), 2)
            self.assertTrue(all(f['properties']['provenance']['acquiredAt'].count('-') == 2 for f in bundle['features']))

    def test_official_full_vertical_datum_reaches_real_terrain_importer(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache,output=Path(temporary)/'downloads',Path(temporary)/'enrichment'
            full_datum='NGF-IGN69 — altitude normale, France continentale'
            def verified_download(region,manifest,path,*args):
                path.mkdir(parents=True,exist_ok=True)
                source.atomic_json(path/(region['macro']+'.json'),{'macro':region['macro'],'width':2,'height':2,'bbox':BOUNDS,'rowOrder':'north-to-south','values':[100,101,102,103],'verticalDatum':full_datum})
            with contextlib.redirect_stdout(io.StringIO()),patch.object(source.terrain,'fetch_official_region',side_effect=verified_download):
                code=source.main(['terrain','--region','geo_huveaune','--bbox',','.join(map(str,BOUNDS)),'--spacing','2','--cache',str(cache),'--output',str(output)])
            self.assertEqual(code,0)
            index=json.loads((output/'index.json').read_text())
            bundle=json.loads((output/Path(index['regions']['geo_huveaune']['path']).name).read_text())
            self.assertEqual(bundle['terrain']['verticalDatum'],full_datum)
            self.assertEqual(bundle['terrain']['provenance']['verticalDatum'],full_datum)


if __name__ == '__main__':
    unittest.main()
