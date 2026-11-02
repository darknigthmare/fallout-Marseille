"""Synthetic, isolated city publication/coverage/archive invariants."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import acquire_city_world as acquisition
import city_sources as city
import world_sources as world


BOX = [43.29, 5.36, 43.30, 5.37]
POLYGON = {'type': 'Polygon', 'coordinates': [[[5.36,43.29],[5.37,43.29],[5.37,43.30],[5.36,43.30],[5.36,43.29]]]}


def fixture(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    boundary = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'code_insee':'13055','nom_officiel':'Marseille'}, 'geometry': POLYGON}]}
    raw = world.canonical(boundary)
    digest = city.sha(raw)
    name = 'boundary-' + digest[:16] + '.json'
    (directory/name).write_bytes(raw)
    def fetch(_):
        raise AssertionError('fixture must use the injected complete collection function')
    def collection(layer, bounds, **kwargs):
        features = ([{'type':'Feature','id':'building.1','geometry': {'type':'Polygon','coordinates': [[[5.361,43.291],[5.363,43.291],[5.363,43.293],[5.361,43.293],[5.361,43.291]]]}, 'properties':{'hauteur':9}}]
                    if layer.endswith(':batiment') else [{'type':'Feature','id':'road.1','geometry':{'type':'LineString','coordinates':[[5.36,43.295],[5.37,43.295]]},'properties':{'largeur_de_chaussee':4}}])
        return acquisition.public.complete_collection(features, layer, bounds)
    tile = {'id':'m13055-r00-c00','queryBbox':BOX}
    with patch.object(acquisition.public,'fetch_features',side_effect=collection):
        descriptors = acquisition.acquire_tile(tile, fetch, list(acquisition.LAYERS.values()), directory, BOX, '2026-10-23')
    index = {'schemaVersion':1,'crs':'EPSG:4326','region':city.REGION,
             'municipality':{'code':'13055','name':'Marseille','bbox':BOX,
                             'boundary':{'path':city.PREFIX+name,'sha256':digest,'bytes':len(raw)},
                             'source':{'name':'Synthetic test boundary','resource':'ign-bdtopo','license':'Test fixture','attribution':'Test fixture','acquiredAt':'2026-10-23','url':acquisition.public.WFS}},
             'coverage':{'complete':True,'tileCount':1,'queryTileCount':1,'partitionStepDegrees':.025,
                         'uniqueBuildings':1,'uniqueRoads':1,'expandedBytes':sum(d['bytes'] for d in descriptors)},'tiles':descriptors}
    (directory/'index.json').write_bytes(world.canonical(index))
    return index


class CitySourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.directory = self.root/'source'
        self.index = fixture(self.directory)

    def tearDown(self):
        self.temporary.cleanup()

    def change_index(self, mutate):
        index = copy.deepcopy(self.index)
        mutate(index)
        (self.directory/'index.json').write_bytes(world.canonical(index))

    def test_complete_fixture_validates_and_audits_unique_ids(self):
        files, providers = city.validate_directory(self.directory)
        self.assertEqual(len(files),3)
        self.assertEqual(len(providers),3)
        result = city.audit_details(self.directory)
        self.assertEqual((result['totalBuildings'],result['totalRoads']),(1,1))
        self.assertTrue(result['coverage']['complete'])

    def test_runtime_city_atlas_restores_under_python_s_without_any_regional_manifest(self):
        # Copy only the offline validator modules. Acquisition CLIs and every
        # regional terrain manifest are deliberately absent from this project.
        tools = self.root/'minimal'/'tools'
        tools.mkdir(parents=True)
        for name in ('city_sources.py','world_sources.py'):
            shutil.copyfile(Path(city.__file__).parent/name,tools/name)
        script = ('import sys; sys.path.insert(0,sys.argv[1]); import city_sources; '
                  'files,_=city_sources.validate_directory(sys.argv[2]); '
                  'assert len(files)==3; '
                  'assert not any(name.startswith("acquire_") for name in sys.modules)')
        result=subprocess.run([sys.executable,'-S','-c',script,str(tools),str(self.directory)],
                              capture_output=True,text=True,timeout=10,cwd=tools.parent)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_offline_partition_helpers_match_acquisition_predicates(self):
        hole=[[5.364,43.294],[5.366,43.294],[5.366,43.296],[5.364,43.296],[5.364,43.294]]
        with_hole=copy.deepcopy(POLYGON)
        with_hole['coordinates'].append(hole)
        island={'type':'MultiPolygon','coordinates':[POLYGON['coordinates'],[[[5.375,43.295],[5.377,43.295],[5.377,43.297],[5.375,43.297],[5.375,43.295]]]]}
        for shape,bounds in [(POLYGON,BOX),(with_hole,BOX),(island,[43.29,5.36,43.30,5.38])]:
            for step in (.005,.025,.05):
                self.assertEqual(city._partition(bounds,shape,step),acquisition.partition(bounds,shape,step))
        root={'id':'m13055-r00-c00','queryBbox':BOX}
        self.assertEqual(city._split(root),acquisition.split(root))
        for child in city._split(root):
            self.assertEqual(city._split(child),acquisition.split(child))

    def test_missing_partition_is_not_a_complete_city(self):
        self.change_index(lambda d: d.update(tiles=[]))
        with self.assertRaisesRegex(world.SourceError,'complete bounded'):
            city.validate_directory(self.directory)

    def test_wrong_administrative_bbox_refused(self):
        self.change_index(lambda d: d['municipality'].update(bbox=[43.28,5.36,43.30,5.37]))
        with self.assertRaisesRegex(world.SourceError,'boundary extent'):
            city.validate_directory(self.directory)

    def test_missing_quadrant_refused(self):
        with self.assertRaisesRegex(world.SourceError,'every administrative'):
            city._complete_leaves('m13055-r00-c00', {'m13055-r00-c00-0':BOX,'m13055-r00-c00-1':BOX,'m13055-r00-c00-2':BOX})

    def test_overlapping_parent_child_refused(self):
        with self.assertRaisesRegex(world.SourceError,'overlapping'):
            city._complete_leaves('m13055-r00-c00', {'m13055-r00-c00':BOX,'m13055-r00-c00-0':BOX})

    def test_all_four_subdivisions_prove_coverage(self):
        city._complete_leaves('m13055-r00-c00', {'m13055-r00-c00-'+str(i):BOX for i in range(4)})

    def test_feature_byte_corruption_refused(self):
        path = self.directory/Path(self.index['tiles'][0]['path']).name
        path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(world.SourceError,'SHA-256 mismatch'):
            city.validate_directory(self.directory)

    def test_unsafe_descriptor_path_refused(self):
        self.change_index(lambda d: d['tiles'][0].update(path='data/map_pack/city/../secret.json'))
        with self.assertRaisesRegex(world.SourceError,'safe local'):
            city.validate_directory(self.directory)

    def test_false_aggregate_count_refused(self):
        self.change_index(lambda d: d['coverage'].update(uniqueBuildings=2))
        with self.assertRaisesRegex(world.SourceError,'aggregate source counts'):
            city.validate_directory(self.directory)

    def test_archive_roundtrip_and_existing_valid_import_preserved(self):
        archive_directory = self.root/'archives'
        receipt = city.package(self.directory,archive_directory)
        restored = self.root/'restored'
        result = city.install(archive_directory/'manifest.json',restored)
        self.assertEqual(result['status'],'installed')
        self.assertEqual(city.validate_directory(restored)[0], city.validate_directory(self.directory)[0])
        self.assertEqual(city.install(archive_directory/'manifest.json',restored)['status'],'preserved')
        self.assertEqual(receipt['members'][0]['name'],sorted(m['name'] for m in receipt['members'])[0])

    def test_archive_is_deterministic(self):
        first = city.package(self.directory,self.root/'a')
        second = city.package(self.directory,self.root/'b')
        self.assertEqual(first,second)

    def test_corrupted_existing_import_is_not_overwritten(self):
        city.package(self.directory,self.root/'a')
        destination = self.root/'corrupt'
        destination.mkdir()
        (destination/'index.json').write_text('{}')
        with self.assertRaises(world.SourceError):
            city.install(self.root/'a/manifest.json',destination)
        self.assertEqual((destination/'index.json').read_text(),'{}')

    def test_archive_outer_hash_mismatch_refused(self):
        receipt = city.package(self.directory,self.root/'a')
        archive = self.root/'a'/receipt['archive']
        archive.write_bytes(archive.read_bytes()+b'corrupt')
        with self.assertRaisesRegex(world.SourceError,'SHA-256 mismatch'):
            city.install(self.root/'a/manifest.json',self.root/'dest')
        self.assertFalse((self.root/'dest/index.json').exists())

    def test_archive_traversal_member_refused(self):
        receipt = city.package(self.directory,self.root/'a')
        receipt['members'][0]['name']='../escape.json'
        (self.root/'a/manifest.json').write_bytes(world.canonical(receipt))
        with self.assertRaisesRegex(world.SourceError,'unsafe'):
            city.read_package(self.root/'a/manifest.json')

    def test_rectangle_polygon_intersections_include_edges_and_skip_far_cells(self):
        self.assertTrue(acquisition.rectangle_touches_polygon(BOX,POLYGON))
        self.assertTrue(acquisition.rectangle_touches_polygon([43.294,5.35,43.296,5.365],POLYGON))
        self.assertFalse(acquisition.rectangle_touches_polygon([43.28,5.34,43.285,5.35],POLYGON))

    def test_polygon_hole_does_not_create_missing_land(self):
        shape=copy.deepcopy(POLYGON)
        shape['coordinates'].append([[5.364,43.294],[5.366,43.294],[5.366,43.296],[5.364,43.296],[5.364,43.294]])
        self.assertFalse(acquisition.rectangle_touches_polygon([43.2945,5.3645,43.2955,5.3655],shape))
        self.assertTrue(acquisition.rectangle_touches_polygon(BOX,shape))

    def test_exact_cache_receipt_is_reused_without_network(self):
        calls=[]
        fetch=acquisition.Cache(self.root/'http',lambda url:calls.append(url) or b'{"ok":true}')
        self.assertEqual(fetch('https://data.geopf.fr/test'),b'{"ok":true}')
        self.assertEqual(fetch('https://data.geopf.fr/test'),b'{"ok":true}')
        self.assertEqual(len(calls),1)
        next((self.root/'http').glob('*.raw')).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'cached official response'):
            fetch('https://data.geopf.fr/test')

    def test_retry_is_bounded_and_does_not_cache_error(self):
        calls=[]
        def network(url):
            calls.append(url)
            raise HTTPError(url,503,'busy',None,None)
        fetch=acquisition.Cache(self.root/'http',network)
        with patch.object(acquisition.time,'sleep'):
            with self.assertRaises(HTTPError):
                fetch('https://data.geopf.fr/test')
        self.assertEqual(len(calls),5)
        self.assertFalse((self.root/'http').exists())

    def test_source_failure_keeps_previous_index(self):
        old=(self.directory/'index.json').read_bytes()
        boundary={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'code_insee':'13055'},'geometry':POLYGON}]}
        with patch.object(acquisition,'municipality',return_value=(boundary,BOX,{})), patch.object(acquisition.public,'wfs_layers',return_value=list(acquisition.LAYERS.values())), patch.object(acquisition.public,'describe_feature_type',return_value={}), patch.object(acquisition.public,'validate_feature_schema',return_value={}), patch.object(acquisition,'acquire_tile',side_effect=ValueError('incomplete official page')):
            # The date receipt comes from the official municipality call in production.
            cache=acquisition.Cache
            class FixtureCache(cache):
                def __init__(self,*a,**k):
                    super().__init__(*a,**k)
                    self.receipts=[{'acquiredAt':'2026-10-23'}]
            with patch.object(acquisition,'Cache',FixtureCache):
                with self.assertRaisesRegex(ValueError,'incomplete official page'):
                    acquisition.acquire(self.root/'cache',self.directory,workers=1)
        self.assertEqual((self.directory/'index.json').read_bytes(),old)

    def unavailable_collection(self, method='Pas de Z', precision=9999):
        feature={'type':'Feature','id':'road.anomaly','geometry':{'type':'LineString','coordinates':[[5.361,43.291,-100],[5.362,43.292,24]]},
                 'properties':{'methode_d_acquisition_altimetrique':method,'precision_altimetrique':precision}}
        return acquisition.public.complete_collection([feature],acquisition.LAYERS['roads'],BOX)

    def test_explicit_no_z_anomaly_keeps_xy_and_original_hash(self):
        original=self.unavailable_collection()
        provider=world.provenance(name='IGN BD TOPO',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign-bdtopo',url=acquisition.public.WFS,vertical_datum='NGF-IGN69')
        result=acquisition.normalize_collection(original,provider,BOX)[0]
        self.assertEqual(original['features'][0]['geometry']['coordinates'][0],[5.361,43.291,-100])
        self.assertEqual(result['geometry']['coordinates'],[[5.361,43.291],[5.362,43.292,24]])
        proof=result['properties']['provenance']
        self.assertEqual(proof['inputSha256'],city.sha(world.canonical(original)))
        self.assertEqual(proof['sourceGeometryZUnavailable']['unavailableSourceValues'],[-100])
        self.assertEqual(proof['sourceGeometryZUnavailable']['removedCoordinates'],1)

    def test_negative_100_with_measured_method_is_not_changed(self):
        provider=world.provenance(name='IGN BD TOPO',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign-bdtopo',vertical_datum='NGF-IGN69')
        with self.assertRaisesRegex(world.SourceError,'outside the supported altitude'):
            acquisition.normalize_collection(self.unavailable_collection(method='Photogrammétrie'),provider,BOX)

    def test_negative_100_without_no_precision_is_not_changed(self):
        provider=world.provenance(name='IGN BD TOPO',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign-bdtopo',vertical_datum='NGF-IGN69')
        with self.assertRaisesRegex(world.SourceError,'outside the supported altitude'):
            acquisition.normalize_collection(self.unavailable_collection(precision=2.5),provider,BOX)

    def test_negative_100_from_other_provider_is_not_changed(self):
        provider=world.provenance(name='Local test',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='local-survey',vertical_datum='NGF-IGN69')
        collection=self.unavailable_collection()
        collection.pop('acquisitionCoverage')
        with self.assertRaisesRegex(world.SourceError,'outside the supported altitude'):
            acquisition.normalize_collection(collection,provider,BOX)

    def no_data_terrain(self, values):
        provider=world.provenance(name='IGN points test fixture',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign_rge_alti_wld',vertical_datum='NGF-IGN69')
        proof={'source':provider['name'],**{k:v for k,v in provider.items() if k!='name'},'inputSha256':'a'*64,'resampled':True}
        grid={'macro':'enrichment:'+city.REGION,'width':2,'height':2,'bbox':BOX,'rowOrder':'north-to-south','values':values,
              'validPoints':0,'missingPoints':4,'verticalDatum':'NGF-IGN69','sourceResource':'ign_rge_alti_wld','provenance':proof}
        raw=world.canonical(grid);digest=city.sha(raw);name='terrain-'+digest[:16]+'.json'
        (self.directory/name).write_bytes(raw)
        descriptor={'path':city.PREFIX+name,'sha256':digest,'bytes':len(raw),'bbox':BOX}
        index={'schemaVersion':1,'region':city.REGION,'bbox':BOX,'base':None,'tiles':[],'noDataTiles':[descriptor]}
        (self.directory/'terrain-index.json').write_bytes(world.canonical(index))

    def test_no_data_only_grid_is_preserved_as_measured_absence(self):
        self.no_data_terrain([None]*4)
        files,_=city.validate_directory(self.directory)
        self.assertIn('terrain-index.json',files)
        self.assertEqual(sum(name.startswith('terrain-') and name!='terrain-index.json' for name in files),1)

    def test_no_data_only_receipt_cannot_hide_a_supplied_height(self):
        self.no_data_terrain([None,None,20,None])
        with self.assertRaisesRegex(world.SourceError,'absent source samples'):
            city.validate_directory(self.directory)

    def test_render_bounds_cannot_use_arbitrary_distant_road_extent(self):
        self.change_index(lambda d: d['tiles'][0].update(renderBbox=[43.28,5.35,43.31,5.38]))
        with self.assertRaisesRegex(world.SourceError,'rendered extent'):
            city.validate_directory(self.directory)

    def test_immutable_city_geometry_is_never_silently_overwritten(self):
        path=self.root/'immutable.json'
        path.write_bytes(b'old')
        with self.assertRaisesRegex(world.SourceError,'preserved unchanged'):
            acquisition.immutable_write(path,b'new')
        self.assertEqual(path.read_bytes(),b'old')

    def test_geometry_cache_reuses_only_identical_verified_bytes(self):
        city._GEOMETRY_VALIDATED.clear()
        with patch.object(city,'geometry',wraps=world.geometry) as checked_geometry:
            city.validate_directory(self.directory)
            first=checked_geometry.call_count
            self.assertEqual(first,2)
            city.validate_directory(self.directory)
            self.assertEqual(checked_geometry.call_count,first)
            descriptor=self.index['tiles'][0]
            bundle=json.loads((self.directory/Path(descriptor['path']).name).read_bytes())
            bundle['features'][0]['geometry']['coordinates']=[[[5.361,43.291],[5.363,43.293],[5.361,43.293],[5.363,43.291],[5.361,43.291]]]
            raw=world.canonical(bundle);digest=city.sha(raw);name=descriptor['id']+'-'+digest[:16]+'.json'
            (self.directory/name).write_bytes(raw)
            self.change_index(lambda d:d['tiles'][0].update(path=city.PREFIX+name,sha256=digest,bytes=len(raw)))
            with self.assertRaises(world.SourceError):
                city.validate_directory(self.directory)
            self.assertGreater(checked_geometry.call_count,first)

    def test_geometry_cache_never_skips_sha_verification(self):
        city.validate_directory(self.directory)
        path=self.directory/Path(self.index['tiles'][0]['path']).name
        path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(world.SourceError,'SHA-256 mismatch'):
            city.validate_directory(self.directory)

    def test_geometry_cache_is_invalidated_when_geometry_limits_change(self):
        city.validate_directory(self.directory)
        with patch.object(world,'MAX_RING_VERTICES',4):
            with self.assertRaisesRegex(world.SourceError,'4..4 vertices'):
                city.validate_directory(self.directory)

    def test_conservative_wfs_border_object_keeps_original_xy(self):
        feature={'type':'Feature','id':'border.1','properties':{},'geometry':{'type':'Polygon','coordinates':[[[5.365,43.300001],[5.366,43.300001],[5.366,43.30001],[5.365,43.30001],[5.365,43.300001]]]}}
        collection=acquisition.public.complete_collection([feature],acquisition.LAYERS['buildings'],BOX)
        provider=world.provenance(name='IGN BD TOPO',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign-bdtopo',vertical_datum='NGF-IGN69')
        result=acquisition.normalize_collection(collection,provider,BOX)[0]
        self.assertEqual(result['geometry'],feature['geometry'])
        border=result['properties']['provenance']['sourceGeometryAdministrativeBorder']
        self.assertGreater(border['minimumSeparationMeters'],0)
        self.assertLessEqual(border['minimumSeparationMeters'],2)

    def test_wfs_object_far_from_municipality_is_still_rejected(self):
        feature={'type':'Feature','id':'far.1','properties':{},'geometry':{'type':'LineString','coordinates':[[5.365,43.31],[5.366,43.311]]}}
        collection=acquisition.public.complete_collection([feature],acquisition.LAYERS['roads'],BOX)
        provider=world.provenance(name='IGN BD TOPO',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign-bdtopo',vertical_datum='NGF-IGN69')
        with self.assertRaisesRegex(world.SourceError,'more than two metres'):
            acquisition.normalize_collection(collection,provider,BOX)

    def original_collections(self):
        bundle=json.loads((self.directory/Path(self.index['tiles'][0]['path']).name).read_bytes())
        collections={}
        for kind,layer in acquisition.LAYERS.items():
            rows=[]
            for feature in bundle['features']:
                if feature['properties']['kind']!=('building' if kind=='buildings' else 'road'):continue
                rows.append({'type':'Feature','id':feature['id'],'geometry':feature['geometry'],
                             'properties':{k:v for k,v in feature['properties'].items() if k not in ('kind','sourceId','provenance')}})
            collections[kind]=acquisition.public.complete_collection(rows,layer,BOX)
        return collections

    def test_accepted_leaf_checkpoint_reuses_exact_original_input_hashes(self):
        collections=self.original_collections()
        def fetch(layer,*args,**kwargs):
            return collections['buildings' if layer.endswith(':batiment') else 'roads']
        with patch.object(acquisition.public,'fetch_features',side_effect=fetch),patch.object(acquisition,'normalize_collection',side_effect=AssertionError('accepted exact input should reuse its validated leaf')):
            result=acquisition.acquire_tile({'id':'m13055-r00-c00','queryBbox':BOX},None,[],self.directory,BOX,'2026-10-23')
        self.assertEqual(result,self.index['tiles'])

    def test_accepted_leaf_checkpoint_never_replays_changed_source_values(self):
        collections=self.original_collections()
        collections['buildings']['features'][0]['properties']['hauteur']=13
        def fetch(layer,*args,**kwargs):
            return collections['buildings' if layer.endswith(':batiment') else 'roads']
        with patch.object(acquisition.public,'fetch_features',side_effect=fetch):
            result=acquisition.acquire_tile({'id':'m13055-r00-c00','queryBbox':BOX},None,[],self.directory,BOX,'2026-10-23')
        self.assertNotEqual(result[0]['sha256'],self.index['tiles'][0]['sha256'])
        bundle=json.loads((self.directory/Path(result[0]['path']).name).read_bytes())
        self.assertEqual(bundle['features'][0]['properties']['hauteur'],13)

    def tamper_leaf(self, change):
        original=self.directory/Path(self.index['tiles'][0]['path']).name
        bundle=json.loads(original.read_bytes());change(bundle)
        raw=world.canonical(bundle);digest=city.sha(raw)
        (self.directory/('m13055-r00-c00-'+digest[:16]+'.json')).write_bytes(raw)
        original.unlink()

    def test_checkpoint_rejects_shifted_output_even_with_correct_input_hash(self):
        collections=self.original_collections()
        def shift(bundle):
            for position in bundle['features'][0]['geometry']['coordinates'][0]:position[0]+=.0001
        self.tamper_leaf(shift)
        def fetch(layer,*args,**kwargs):return collections['buildings' if layer.endswith(':batiment') else 'roads']
        with patch.object(acquisition.public,'fetch_features',side_effect=fetch):
            result=acquisition.acquire_tile({'id':'m13055-r00-c00','queryBbox':BOX},None,[],self.directory,BOX,'2026-10-23')
        bundle=json.loads((self.directory/Path(result[0]['path']).name).read_bytes())
        self.assertEqual(bundle['features'][0]['geometry'],collections['buildings']['features'][0]['geometry'])
        self.assertEqual(result[0]['sha256'],self.index['tiles'][0]['sha256'])

    def test_checkpoint_rejects_synthesized_source_attribute_in_output(self):
        collections=self.original_collections()
        self.tamper_leaf(lambda bundle:bundle['features'][0]['properties'].update(hauteur=88))
        def fetch(layer,*args,**kwargs):return collections['buildings' if layer.endswith(':batiment') else 'roads']
        with patch.object(acquisition.public,'fetch_features',side_effect=fetch):
            result=acquisition.acquire_tile({'id':'m13055-r00-c00','queryBbox':BOX},None,[],self.directory,BOX,'2026-10-23')
        self.assertEqual(result[0]['sha256'],self.index['tiles'][0]['sha256'])

    def terrain_fixture(self, base_box=BOX, fine=None, requested=None, complete=True):
        fine=[] if fine is None else fine
        provider=world.provenance(name='Synthetic terrain fixture',license='Test fixture',attribution='Test fixture',acquired_at='2026-10-23',resource='ign_rge_alti_wld',vertical_datum='NGF-IGN69')
        def grid_file(box,value,base=False):
            grid=world.checked_terrain({'width':2,'height':2,'bbox':box,'rowOrder':'north-to-south','values':[value]*4},city.REGION,provider,'a'*64,BOX)
            grid['macro']=city.REGION if base else 'enrichment:'+city.REGION+':'+world.terrain_digest(grid)[:16]
            raw=world.canonical(grid);digest=city.sha(raw);name='terrain-'+digest[:16]+'.json'
            (self.directory/name).write_bytes(raw)
            return {'path':city.PREFIX+name,'sha256':digest,'bytes':len(raw),'bbox':box}
        base=grid_file(base_box,20,True)
        descriptors=[grid_file(box,value) for box,value in fine]
        index={'schemaVersion':1,'region':city.REGION,'bbox':BOX,'base':base,'tiles':descriptors,'noDataTiles':[],
               'coverage':{'complete':True,'fineComplete':complete,'requestedFinePartitions':len(fine) if requested is None else requested,'completedFinePartitions':len(fine)}}
        (self.directory/'terrain-index.json').write_bytes(world.canonical(index))
        return index

    def quadrants(self):
        return [child['queryBbox'] for child in acquisition.split({'id':'m13055-r00-c00','queryBbox':BOX})]

    def test_complete_terrain_base_cannot_be_a_small_subsector(self):
        self.terrain_fixture(base_box=self.quadrants()[0])
        with self.assertRaisesRegex(world.SourceError,'entire municipality'):
            city.validate_directory(self.directory)

    def test_false_fine_completion_count_is_rejected(self):
        self.terrain_fixture(requested=25,complete=True)
        path=self.directory/'terrain-index.json';index=json.loads(path.read_bytes());index['coverage']['completedFinePartitions']=25;path.write_bytes(world.canonical(index))
        with self.assertRaisesRegex(world.SourceError,'counts differ'):
            city.validate_directory(self.directory)

    def test_fine_completion_requires_the_actual_full_rectangle_union(self):
        self.terrain_fixture(fine=[(box,20) for box in self.quadrants()[:3]])
        with self.assertRaisesRegex(world.SourceError,'query gap'):
            city.validate_directory(self.directory)

    def test_fine_completion_refuses_overlapping_subsectors(self):
        self.terrain_fixture(fine=[(BOX,20),(self.quadrants()[0],21)])
        with self.assertRaisesRegex(world.SourceError,'overlapping interiors'):
            city.validate_directory(self.directory)

    def test_complete_fine_grids_with_matching_shared_edges_pass(self):
        self.terrain_fixture(fine=[(box,20) for box in self.quadrants()])
        files,_=city.validate_directory(self.directory)
        self.assertIn('terrain-index.json',files)

    def test_complete_fine_grids_cannot_hide_source_seam_disagreement(self):
        self.terrain_fixture(fine=[(box,20 if i else 21) for i,box in enumerate(self.quadrants())])
        with self.assertRaisesRegex(world.SourceError,'shared partition edge'):
            city.validate_directory(self.directory)

    def test_explicit_base_only_terrain_can_be_packaged_without_claiming_fine_coverage(self):
        self.terrain_fixture(complete=False,requested=0)
        receipt=city.package(self.directory,self.root/'base-only')
        self.assertIn('terrain-index.json',[row['name'] for row in receipt['members']])

    def test_runtime_full_terrain_validation_never_imports_geo_acquisition_dependencies(self):
        import builtins
        original_import=builtins.__import__
        self.terrain_fixture(fine=[(box,20) for box in self.quadrants()])
        def stdlib_only(name,*args,**kwargs):
            if name.split('.')[0] in ('acquire_city_world','acquire_public_world','acquire_city_terrain','convert_ign_dem','rasterio','numpy','affine'):
                raise AssertionError('Runtime restoration must not depend on geographic acquisition modules')
            return original_import(name,*args,**kwargs)
        with patch.object(builtins,'__import__',side_effect=stdlib_only):
            files,_=city.validate_directory(self.directory)
        self.assertIn('terrain-index.json',files)


if __name__ == '__main__':
    unittest.main()
