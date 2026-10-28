#!/usr/bin/env python3
"""Measured-source import, topology, coordinate and transaction contracts."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from world_sources import (SourceError, canonical, checked_terrain, decode_json,
                          lambert93_to_wgs84, provenance, publish_bundle,
                          read_ascii_grid, read_geojson, read_terrain,
                          _writer_lock, _publish_bundle_unlocked, terrain_digest)

BBOX = [43.245, 5.43, 43.335, 5.64]


def provider(name="Local measured survey", resource="survey-control"):
    return provenance(name=name, license="Licence Ouverte 2.0", attribution=name, acquired_at="2026-10-23", resource=resource,
                      url="https://example.org/measurement", vertical_datum="NGF-IGN69")


def building(identity="building-1"):
    return {"type": "Feature", "id": identity, "properties": {"hauteur": 11.7, "z_min_sol": 114.2, "z_max_toit": 125.9},
            "geometry": {"type": "Polygon", "coordinates": [
                [[5.50, 43.29], [5.501, 43.29], [5.501, 43.291], [5.50, 43.291], [5.50, 43.29]],
                [[5.5002, 43.2902], [5.5002, 43.2904], [5.5004, 43.2904], [5.5004, 43.2902], [5.5002, 43.2902]] ]}}


def road(identity="road-1"):
    return {"type": "Feature", "id": identity, "properties": {"largeur_de_chaussee": 6.25, "bridge": "yes"},
            "geometry": {"type": "LineString", "coordinates": [[5.5, 43.29], [5.501, 43.291], [5.502, 43.292]]}}


def features(*rows, source=None):
    return read_geojson(canonical({"type": "FeatureCollection", "features": list(rows)}), source or provider(), BBOX)


def grid():
    return {"width": 3, "height": 2, "bbox": [43.29, 5.5, 43.291, 5.502], "rowOrder": "north-to-south", "values": [100, 101, 102, 200, None, 202]}


def terrain(source=None):
    return read_terrain(canonical(grid()), "geo_huveaune", source or provider(), BBOX)


class ImportGeometryTests(unittest.TestCase):
    def test_preserves_source_courtyard_vertices_and_height_fields(self):
        original = building()
        result = features(original)[0]
        self.assertEqual(result["geometry"], original["geometry"])
        self.assertEqual(result["properties"]["hauteur"], 11.7)
        self.assertEqual(result["properties"]["z_max_toit"], 125.9)
        self.assertEqual(result["properties"]["kind"], "building")
        self.assertEqual(result["properties"]["sourceId"], "building-1")
        self.assertEqual(len(result["properties"]["provenance"]["inputSha256"]), 64)

    def test_road_keeps_width_and_every_source_vertex(self):
        result = features(road())[0]
        self.assertEqual(result["geometry"], road()["geometry"])
        self.assertEqual(result["properties"]["largeur_de_chaussee"], 6.25)
        self.assertEqual(result["properties"]["bridge"], "yes")
        self.assertEqual(result["properties"]["kind"], "road")

    def test_multipolygon_preserves_all_components_and_holes(self):
        feature = building()
        first = feature["geometry"]["coordinates"]
        second = [[[5.502, 43.29], [5.503, 43.29], [5.503, 43.291], [5.502, 43.291], [5.502, 43.29]]]
        feature["geometry"] = {"type": "MultiPolygon", "coordinates": [first, second]}
        self.assertEqual(features(feature)[0]["geometry"], feature["geometry"])

    def test_does_not_implicitly_close_an_open_ring(self):
        feature = building()
        feature["geometry"]["coordinates"][0].pop()
        with self.assertRaisesRegex(SourceError, "not closed"):
            features(feature)

    def test_rejects_self_intersecting_source(self):
        feature = building()
        feature["geometry"]["coordinates"] = [[[5.50,43.29],[5.502,43.292],[5.50,43.292],[5.502,43.29],[5.50,43.29]]]
        with self.assertRaises(SourceError):
            features(feature)

    def test_rejects_outside_or_touching_hole(self):
        feature = building()
        feature["geometry"]["coordinates"][1] = [[5.5,43.29],[5.5,43.2904],[5.5004,43.2904],[5.5004,43.29],[5.5,43.29]]
        with self.assertRaises(SourceError):
            features(feature)

    def test_rejects_nested_holes(self):
        feature = building()
        feature["geometry"]["coordinates"].append([[5.50025,43.29025],[5.50025,43.2903],[5.5003,43.2903],[5.5003,43.29025],[5.50025,43.29025]])
        with self.assertRaisesRegex(SourceError, "nested"):
            features(feature)

    def test_rejects_duplicate_source_identifiers(self):
        with self.assertRaisesRegex(SourceError, "duplicate source"):
            features(building("same"), road("same"))

    def test_geometry_identity_is_stable_when_no_source_id_exists(self):
        a = building()
        del a["id"]
        first = features(a)[0]["id"]
        a["properties"]["name"] = "Changed label"
        self.assertEqual(first, features(a)[0]["id"])
        self.assertTrue(first.startswith("geometry:"))

    def test_lambert93_control_point_uses_grs80(self):
        lon, lat = lambert93_to_wgs84(700000, 6600000)
        self.assertAlmostEqual(lon, 3.0, places=9)
        self.assertAlmostEqual(lat, 46.5, places=8)

    def test_projected_geojson_preserves_third_coordinate(self):
        feature = {"type":"Feature","id":"survey-road","properties":{},"geometry":{"type":"LineString","coordinates":[[700000,6600000,123.456],[700010,6600010,124.5]]}}
        output = read_geojson(canonical({"type":"FeatureCollection","features":[feature]}),provider(),[46.4,2.9,46.6,3.1],"EPSG:2154")
        first = output[0]["geometry"]["coordinates"][0]
        self.assertAlmostEqual(first[0],3.0,places=9)
        self.assertAlmostEqual(first[1],46.5,places=8)
        self.assertEqual(first[2],123.456)
        self.assertEqual(output[0]["properties"]["provenance"]["inputCrs"],"EPSG:2154")

    def test_rejects_mismatched_or_missing_vertical_reference(self):
        source = provider()
        del source["verticalDatum"]
        feature = road()
        feature["geometry"]["coordinates"][0].append(200)
        with self.assertRaisesRegex(SourceError,"vertical datum"):
            features(feature,source=source)

    def test_rejects_source_outside_region(self):
        feature = road()
        feature["geometry"]["coordinates"] = [[2.3,48.8],[2.31,48.81]]
        with self.assertRaisesRegex(SourceError,"selected region"):
            features(feature)

    def test_bdtopo_explicit_pas_de_z_sentinel_preserves_xy_and_proof(self):
        feature=road()
        feature['properties']['methode_d_acquisition_altimetrique']='Pas de Z'
        feature['properties']['precision_altimetrique']=9999
        feature['geometry']['coordinates']=[p+[-1000] for p in feature['geometry']['coordinates']]
        source=provider('IGN BD TOPO','ign-bdtopo')
        result=features(feature,source=source)[0]
        self.assertEqual(result['geometry']['coordinates'],road()['geometry']['coordinates'])
        proof=result['properties']['provenance']['sourceGeometryZNoData']
        self.assertEqual(proof['removedCoordinates'],3)
        self.assertEqual(proof['sentinel'],-1000)
        self.assertEqual(result['properties']['precision_altimetrique'],9999)

    def test_unknown_provider_or_unmarked_minus1000_is_never_silently_filtered(self):
        for source,method in [(provider(),'Pas de Z'),(provider('IGN BD TOPO','ign-bdtopo'),'Photogrammétrie')]:
            feature=road();feature['properties']['methode_d_acquisition_altimetrique']=method
            feature['geometry']['coordinates']=[p+[-1000] for p in feature['geometry']['coordinates']]
            with self.subTest(resource=source['resource'],method=method),self.assertRaisesRegex(SourceError,'altitude range'):
                features(feature,source=source)

    def test_completed_wfs_coverage_is_preserved_separately_from_feature_extent(self):
        collection={'type':'FeatureCollection','features':[road()],
                    'acquisitionCoverage':{'bbox':[43.28,5.49,43.30,5.51],'crs':'EPSG:4326','complete':True,'layer':'BDTOPO_V3:troncon_de_route','returned':1}}
        result=read_geojson(canonical(collection),provider('IGN BD TOPO','ign-bdtopo'),BBOX)
        self.assertEqual(result[0]['properties']['provenance']['coverage'],collection['acquisitionCoverage'])
        self.assertEqual(result[0]['geometry'],road()['geometry'])

    def test_false_incomplete_or_wrong_layer_coverage_cannot_replace_base_data(self):
        coverage={'bbox':[43.28,5.49,43.30,5.51],'crs':'EPSG:4326','complete':True,'layer':'BDTOPO_V3:troncon_de_route','returned':1}
        for change in [{'complete':False},{'returned':2},{'crs':'EPSG:2154'},{'layer':'BDTOPO_V3:batiment'},{'bbox':[43.0,5.0,44.0,6.0]}]:
            with self.subTest(change=change),self.assertRaises(SourceError):
                read_geojson(canonical({'type':'FeatureCollection','features':[road()],'acquisitionCoverage':{**coverage,**change}}),provider('IGN','ign-bdtopo'),BBOX)


class TerrainImportTests(unittest.TestCase):
    def conversion(self):
        return {"format":"GeoTIFF","inputSha256":"a"*64,"crs":"EPSG:2154","nativePixelSize":[1,1],"nativeTransform":[1,0,892000,0,-1,6250000],
                "sourceSize":[100,100],"resampling":"nearest","sampleConvention":"WGS84 regular nodes","requestedSpacingMeters":1,
                "actualSpacingMeters":[1,1],"resampled":True,"nodataPreserved":True,"verticalDatum":"NGF-IGN69"}

    def test_preserves_validated_geotiff_conversion_receipt(self):
        conversion=self.conversion()
        result=read_terrain(canonical({**grid(),"conversion":conversion}),"geo_huveaune",provider(),BBOX)
        self.assertEqual(result["provenance"]["conversion"],conversion)
        self.assertTrue(result["provenance"]["resampled"])
        self.assertNotEqual(result["provenance"]["inputSha256"],conversion["inputSha256"])

    def test_rejects_false_or_incomplete_conversion_metadata(self):
        for change in ({"verticalDatum":"ellipsoid"},{"inputSha256":"not-a-digest"},{"resampling":"invented"},{"nodataPreserved":False},{"actualSpacingMeters":[0,0]}):
            with self.subTest(change=change),self.assertRaises(SourceError):
                read_terrain(canonical({**grid(),"conversion":{**self.conversion(),**change}}),"geo_huveaune",provider(),BBOX)

    def test_terrain_preserves_every_value_and_nodata(self):
        result = terrain()
        self.assertEqual(result["values"],grid()["values"])
        self.assertEqual(result["macro"],"enrichment:geo_huveaune")
        self.assertEqual(result["sourceResource"],"survey-control")
        self.assertEqual(result["missingPoints"],1)
        self.assertFalse(result["provenance"]["resampled"])

    def test_ascii_corner_coordinates_become_sample_centres(self):
        raw=b"ncols 3\nnrows 2\nxllcorner 5.5\nyllcorner 43.29\ncellsize 0.001\nNODATA_value -9999\n100 101 102\n200 -9999 202\n"
        result=read_ascii_grid(raw,"geo_huveaune",provider(),BBOX)
        self.assertEqual(result["values"],grid()["values"])
        for got,expected in zip(result["bbox"],[43.2905,5.5005,43.2915,5.5025]):
            self.assertAlmostEqual(got,expected,places=10)
        self.assertEqual(result["provenance"]["originConvention"],"sample centres")

    def test_ascii_centre_coordinates_remain_unchanged(self):
        raw=b"ncols 2\nnrows 2\nxllcenter 5.5\nyllcenter 43.29\ncellsize 0.001\nNODATA_value -9999\n1 2\n3 4\n"
        self.assertEqual(read_ascii_grid(raw,"geo_huveaune",provider(),BBOX)["bbox"],[43.29,5.5,43.291,5.501])

    def test_rejects_projected_ascii_instead_of_misplacing_it(self):
        with self.assertRaisesRegex(SourceError,"reproject"):
            read_ascii_grid(b"anything","geo_huveaune",provider(),BBOX,"EPSG:2154")

    def test_rejects_wrong_row_order_missing_data_and_nonfinite_altitude(self):
        for change in ({"rowOrder":"south-to-north"},{"values":[1,2]},{"values":[1,2,3,4,5,float("inf")]},{"values":[None]*6}):
            obj={**grid(),**change}
            with self.subTest(change=change),self.assertRaises(SourceError):
                checked_terrain(obj,"geo_huveaune",provider(),"a"*64,BBOX)

    def test_rejects_undeclared_vertical_datum(self):
        source=provider();del source["verticalDatum"]
        with self.assertRaisesRegex(SourceError,"vertical datum"):
            read_terrain(canonical(grid()),"geo_huveaune",source,BBOX)

    def test_rejects_conflicting_declared_vertical_datum(self):
        with self.assertRaisesRegex(SourceError,"differs"):
            read_terrain(canonical({**grid(),"verticalDatum":"ellipsoid"}),"geo_huveaune",provider(),BBOX)


class ImportPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.output=Path(self.temp.name)
        self.source=provider()

    def tearDown(self):
        self.temp.cleanup()

    def publish(self,**kwargs):
        return publish_bundle(self.output,"geo_huveaune",self.source,**kwargs)

    def active(self):
        index=json.loads((self.output/"index.json").read_text())
        descriptor=index["regions"]["geo_huveaune"]
        path=self.output/Path(descriptor["path"]).name
        raw=path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),descriptor["sha256"])
        self.assertEqual(len(raw),descriptor["bytes"])
        return json.loads(raw),descriptor

    def test_same_import_is_idempotent(self):
        first=self.publish(features=features(building()))
        before=(self.output/"index.json").read_bytes()
        second=self.publish(features=features(building()))
        self.assertEqual(first["sha256"],second["sha256"])
        self.assertEqual(before,(self.output/"index.json").read_bytes())

    def test_different_import_requires_an_explicit_mutation(self):
        self.publish(features=features(building()))
        before=(self.output/"index.json").read_bytes()
        with self.assertRaisesRegex(SourceError,"--merge or --replace"):
            self.publish(features=features(road()))
        self.assertEqual(before,(self.output/"index.json").read_bytes())

    def test_terrain_building_road_sequence_accumulates_with_provenance(self):
        self.publish(terrain=terrain())
        self.publish(features=features(building()),merge=True)
        self.publish(features=features(road()),merge=True)
        bundle,descriptor=self.active()
        self.assertEqual(bundle["terrain"]["values"],grid()["values"])
        self.assertEqual({f["properties"]["kind"] for f in bundle["features"]},{"building","road"})
        self.assertEqual(descriptor["kinds"],["building","road","terrain"])
        self.assertEqual(len(bundle["sources"]),1)

    def test_merge_keeps_other_provider_attribution(self):
        self.publish(terrain=terrain())
        other=provider("Another measured provider","another-resource")
        publish_bundle(self.output,"geo_huveaune",other,features=features(road(),source=other),merge=True)
        bundle,descriptor=self.active()
        self.assertEqual(len(bundle["sources"]),2)
        self.assertEqual(bundle["source"]["resource"],"mixed-sources")
        self.assertEqual(bundle["features"][0]["properties"]["provenance"]["resource"],"another-resource")
        self.assertEqual(bundle["terrain"]["provenance"]["resource"],"survey-control")

    def test_merge_different_extents_preserves_older_fine_grid(self):
        fine=terrain()
        self.publish(terrain=fine)
        coarse=read_terrain(canonical({**grid(),'bbox':[43.28,5.49,43.30,5.51],'values':[90,91,92,93,94,95]}),'geo_huveaune',self.source,BBOX)
        result=self.publish(terrain=coarse,merge=True)
        bundle,_=self.active()
        self.assertNotIn('terrain',bundle)
        self.assertEqual(len(bundle['terrainTiles']),2)
        self.assertEqual(result['terrainSamples'],12)
        self.assertIn(fine['values'],[g['values'] for g in bundle['terrainTiles']])
        for entry in bundle['terrainTiles']:
            self.assertEqual(entry['macro'],'enrichment:geo_huveaune:'+terrain_digest(entry)[:16])

    def test_merge_same_extent_different_resolution_and_provider_coexists(self):
        self.publish(terrain=terrain())
        denser=read_terrain(canonical({**grid(),'width':4,'height':3,'values':list(range(12))}),'geo_huveaune',self.source,BBOX)
        self.publish(terrain=denser,merge=True)
        other=provider('Second provider','second-provider')
        publish_bundle(self.output,'geo_huveaune',other,terrain=terrain(other),merge=True)
        bundle,_=self.active()
        self.assertEqual(len(bundle['terrainTiles']),3)
        self.assertEqual({g['sourceResource'] for g in bundle['terrainTiles']},{'survey-control','second-provider'})

    def test_merge_same_provider_extent_dimensions_updates_only_that_grid(self):
        self.publish(terrain=terrain())
        broader=read_terrain(canonical({**grid(),'bbox':[43.28,5.49,43.30,5.51]}),'geo_huveaune',self.source,BBOX)
        self.publish(terrain=broader,merge=True)
        updated=read_terrain(canonical({**grid(),'values':[110,111,112,113,114,115]}),'geo_huveaune',self.source,BBOX)
        self.publish(terrain=updated,merge=True)
        bundle,_=self.active()
        self.assertEqual(len(bundle['terrainTiles']),2)
        by_bounds={tuple(g['bbox']):g for g in bundle['terrainTiles']}
        self.assertEqual(by_bounds[tuple(updated['bbox'])]['values'],updated['values'])
        self.assertEqual(by_bounds[tuple(broader['bbox'])]['values'],broader['values'])

    def test_feature_only_merge_does_not_drop_multiple_terrain_tiles(self):
        self.publish(terrain=terrain())
        broader=read_terrain(canonical({**grid(),'bbox':[43.28,5.49,43.30,5.51]}),'geo_huveaune',self.source,BBOX)
        self.publish(terrain=broader,merge=True)
        self.publish(features=features(building()),merge=True)
        bundle,_=self.active()
        self.assertEqual(len(bundle['terrainTiles']),2)
        self.assertEqual(len(bundle['features']),1)

    def test_corrupt_grid_identity_in_previous_multi_tile_bundle_is_refused(self):
        self.publish(terrain=terrain())
        broader=read_terrain(canonical({**grid(),'bbox':[43.28,5.49,43.30,5.51]}),'geo_huveaune',self.source,BBOX)
        result=self.publish(terrain=broader,merge=True)
        bundle,descriptor=self.active()
        bundle['terrainTiles'][0]['macro']='enrichment:geo_huveaune:not-the-grid-digest'
        raw=canonical(bundle);digest=hashlib.sha256(raw).hexdigest()
        filename='geo_huveaune-'+digest[:16]+'.json'
        (self.output/filename).write_bytes(raw)
        index=json.loads((self.output/'index.json').read_text())
        index['regions']['geo_huveaune'].update(path='data/map_pack/enrichment/'+filename,bytes=len(raw),sha256=digest)
        (self.output/'index.json').write_bytes(canonical(index))
        with self.assertRaisesRegex(SourceError,'terrain identity'):
            self.publish(features=features(building()),merge=True)

    def test_tile_count_and_total_cell_bounds_refuse_without_losing_fine_grid(self):
        self.publish(terrain=terrain())
        before=(self.output/'index.json').read_bytes()
        broader=read_terrain(canonical({**grid(),'bbox':[43.28,5.49,43.30,5.51]}),'geo_huveaune',self.source,BBOX)
        for setting,value in [('MAX_TERRAIN_TILES',1),('MAX_TERRAIN_CELLS',11)]:
            with self.subTest(setting=setting),patch('world_sources.'+setting,value),self.assertRaisesRegex(SourceError,'budget'):
                self.publish(terrain=broader,merge=True)
            self.assertEqual(before,(self.output/'index.json').read_bytes())

    def test_merge_replaces_same_source_feature_once(self):
        self.publish(features=features(building()))
        changed=building();changed["properties"]["hauteur"]=14.25
        self.publish(features=features(changed),merge=True)
        bundle,_=self.active()
        self.assertEqual(len(bundle["features"]),1)
        self.assertEqual(bundle["features"][0]["properties"]["hauteur"],14.25)

    def test_merge_rejects_provider_identifier_collision(self):
        self.publish(features=features(building()))
        other=provider("Other","other")
        with self.assertRaisesRegex(SourceError,"collision"):
            publish_bundle(self.output,"geo_huveaune",other,features=features(building(),source=other),merge=True)

    def test_merge_refuses_corrupt_existing_bundle_without_changing_index(self):
        result=self.publish(terrain=terrain())
        before=(self.output/"index.json").read_bytes()
        Path(result["bundle"]).write_bytes(b"{}")
        with self.assertRaisesRegex(SourceError,"SHA-256"):
            self.publish(features=features(building()),merge=True)
        self.assertEqual(before,(self.output/"index.json").read_bytes())

    def test_replace_also_refuses_corrupt_existing_data(self):
        result=self.publish(terrain=terrain())
        before=(self.output/"index.json").read_bytes()
        Path(result["bundle"]).write_bytes(b"{}")
        with self.assertRaisesRegex(SourceError,"SHA-256"):
            self.publish(features=features(building()),replace=True)
        self.assertEqual(before,(self.output/"index.json").read_bytes())

    def test_merge_refuses_local_path_escape(self):
        self.publish(terrain=terrain())
        index=json.loads((self.output/"index.json").read_text())
        index["regions"]["geo_huveaune"]["path"]="../outside.json"
        (self.output/"index.json").write_bytes(canonical(index))
        with self.assertRaisesRegex(SourceError,"content-addressed"):
            self.publish(features=features(building()),merge=True)

    def test_replace_keeps_old_bundle_but_switches_active_index(self):
        first=self.publish(features=features(building()))
        self.publish(features=features(road()),replace=True)
        bundle,_=self.active()
        self.assertTrue(Path(first["bundle"]).exists())
        self.assertEqual([f["properties"]["kind"] for f in bundle["features"]],["road"])

    def test_other_regions_are_preserved(self):
        self.publish(features=features(building()))
        before=json.loads((self.output/"index.json").read_text())["regions"]["geo_huveaune"]
        publish_bundle(self.output,"geo_garlaban",self.source,features=features(road()))
        after=json.loads((self.output/"index.json").read_text())["regions"]["geo_huveaune"]
        self.assertEqual(before,after)

    def test_descriptor_includes_complete_query_corners_without_objects(self):
        coverage={'bbox':[43.28,5.49,43.30,5.51],'crs':'EPSG:4326','complete':True,'layer':'BDTOPO_V3:troncon_de_route','returned':1}
        source=provider('IGN BD TOPO','ign-bdtopo')
        rows=read_geojson(canonical({'type':'FeatureCollection','features':[road()],'acquisitionCoverage':coverage}),source,BBOX)
        publish_bundle(self.output,'geo_huveaune',source,features=rows)
        bundle,descriptor=self.active()
        self.assertEqual(descriptor['bbox'],coverage['bbox'])

    def test_process_writers_serialize_index_updates_for_two_regions(self):
        script="""from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from world_sources import publish_bundle,decode_json
payload=decode_json(Path(sys.argv[3]).read_bytes())
Path(sys.argv[4]).write_text('ready')
publish_bundle(Path(sys.argv[2]),'geo_garlaban',payload['source'],features=payload['features'])
"""
        payload=self.output/"worker.json"
        payload.write_bytes(canonical({"source":self.source,"features":features(road())}))
        ready=self.output/"worker.ready"
        with _writer_lock(self.output):
            worker=subprocess.Popen([sys.executable,"-c",script,str(ROOT/"tools"),str(self.output),str(payload),str(ready)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            deadline=time.monotonic()+5
            while not ready.exists() and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertTrue(ready.exists(),"worker did not reach publication")
            self.assertIsNone(worker.poll(),"worker must wait while another writer owns the lock")
            _publish_bundle_unlocked(self.output,"geo_huveaune",self.source,features=features(building()))
        stdout,stderr=worker.communicate(timeout=5)
        self.assertEqual(worker.returncode,0,stderr)
        index=decode_json((self.output/"index.json").read_bytes())
        self.assertEqual(set(index["regions"]),{"geo_huveaune","geo_garlaban"})

    def test_cli_import_is_usable_offline_and_reports_failure_exit(self):
        source=self.output/"input.geojson"
        source.write_bytes(canonical({"type":"FeatureCollection","features":[building()]}))
        command=[sys.executable,str(ROOT/"tools/import_world_sources.py"),"--region","geo_huveaune","--geojson",str(source),"--source","Survey","--license","Licence Ouverte 2.0","--attribution","Survey","--acquired-at","2026-10-23","--output",str(self.output/"installed")]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["features"],1)
        command[command.index("geo_huveaune")]="unknown"
        failed=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(failed.returncode,1)


class MetadataSafetyTests(unittest.TestCase):
    def test_requires_real_source_metadata_and_date(self):
        for change in ({"license":""},{"acquired_at":"20261023"},{"acquired_at":"2026-02-30"},{"url":"https://user:secret@example.org/a"},{"url":"https://example.org/?key=secret"}):
            options={"name":"Source","license":"Open","attribution":"Source","acquired_at":"2026-10-23",**change}
            with self.subTest(change=change),self.assertRaises(SourceError):
                provenance(**options)

    def test_json_rejects_duplicate_prototype_and_nonfinite_values(self):
        for raw in (b'{"a":1,"a":2}',b'{"__proto__":{"x":1}}',b'{"a":NaN}',b'{"a":Infinity}'):
            with self.subTest(raw=raw),self.assertRaises(SourceError):
                decode_json(raw)


if __name__=="__main__":
    unittest.main(verbosity=2)
