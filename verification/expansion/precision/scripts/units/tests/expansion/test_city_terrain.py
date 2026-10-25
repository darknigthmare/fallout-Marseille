"""Physical coordinate and NoData contracts for commune-wide terrain grids."""
import json
from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
import acquire_city_terrain as city


class CityTerrainTests(unittest.TestCase):
    def test_pixel_centres_are_requested_nodes(self):
        url,extent=city.node_request([43.2,5.3,43.3,5.4],5,6)
        q=parse_qs(urlsplit(url).query)
        self.assertEqual(q['LAYERS'],[city.LAYER])
        self.assertEqual(q['STYLES'],['normal'])
        self.assertEqual(q['CRS'],['IGNF:WGS84G'])
        dx=(extent[2]-extent[0])/5;dy=(extent[3]-extent[1])/6
        self.assertAlmostEqual(extent[0]+dx/2,5.3)
        self.assertAlmostEqual(extent[2]-dx/2,5.4)
        self.assertAlmostEqual(extent[3]-dy/2,43.3)
        self.assertAlmostEqual(extent[1]+dy/2,43.2)

    def test_request_bounds_are_finite_and_dimensions_bounded(self):
        for b,w,h in [([43,5,44,6],1,2),([43,5,44,6],1025,1024),([43,5,44,6],2.0,2),([44,5,43,6],2,2)]:
            with self.subTest((b,w,h)),self.assertRaises(ValueError): city.node_request(b,w,h)

    def test_partitions_cover_global_grid_and_share_exact_boundary_nodes(self):
        bounds=[43.1696313,5.22875102,43.39105653,5.53254336]
        plans=city.partitions(bounds,10)
        self.assertEqual(len(plans),25)
        self.assertTrue(all(p['width']*p['height']<=251001 for p in plans))
        self.assertEqual(min(p['bbox'][0] for p in plans),bounds[0])
        self.assertEqual(max(p['bbox'][2] for p in plans),bounds[2])
        self.assertEqual(min(p['bbox'][1] for p in plans),bounds[1])
        self.assertEqual(max(p['bbox'][3] for p in plans),bounds[3])
        for a in plans:
            for b in plans:
                aw,bw=a['globalWindow'],b['globalWindow']
                if aw[1]==bw[1] and aw[2]==bw[0]: self.assertEqual(a['bbox'][3],b['bbox'][1])
                if aw[0]==bw[0] and aw[3]==bw[1]: self.assertEqual(a['bbox'][0],b['bbox'][2])

    def test_plan_rejects_huge_implicit_native_grid(self):
        with self.assertRaises(ValueError): city.partitions([43,5,44,6],1)

    def test_point_requests_reuse_exact_same_shared_edge_coordinates(self):
        tiles=city.partitions([43.2,5.3,43.205,5.307],10,20)
        # Compare independently calculated API requests, including decimal
        # quantization, rather than merely comparing the descriptor bboxes.
        for a in tiles:
            for b in tiles:
                aw,bw=a['globalWindow'],b['globalWindow']
                if aw[1]==bw[1] and aw[2]==bw[0]:
                    an,bn=city.grid_nodes(a),city.grid_nodes(b)
                    self.assertEqual(an[a['width']-1::a['width']],bn[::b['width']])
                if aw[0]==bw[0] and aw[3]==bw[1]:
                    an,bn=city.grid_nodes(a),city.grid_nodes(b)
                    self.assertEqual(an[-a['width']:],bn[:b['width']])

    def raster(self,values,*,count=1,dtype='float32',crs='EPSG:4326',bounds=None,nodata=-99999):
        import numpy as np
        from rasterio.io import MemoryFile
        from rasterio.transform import from_bounds
        bounds=bounds or city.node_request([43.2,5.3,43.3,5.4],2,2)[1]
        with MemoryFile() as file:
            with file.open(driver='GTiff',width=2,height=2,count=count,dtype=dtype,crs=crs,
                           transform=from_bounds(*bounds,2,2),nodata=nodata) as raster:
                for i in range(1,count+1):raster.write(np.array(values,dtype=dtype).reshape(2,2),i)
            return file.read()

    def test_actual_nodata_and_negative_elevations_preserved(self):
        values,header=city.decode_raster(self.raster([-2.5,-99999,20,45]),[43.2,5.3,43.3,5.4],2,2)
        self.assertEqual(values,[-2.5,None,20,45])
        self.assertEqual(header['nodata'],-99999)
        self.assertTrue(header['nodeCentresVerified'])

    def test_unmasked_contaminated_lidar_sample_rejected_without_clamping(self):
        with self.assertRaisesRegex(ValueError,'not clamped'):
            city.decode_raster(self.raster([-8233,5,20,45],nodata=-9999),[43.2,5.3,43.3,5.4],2,2)

    def test_rgb_picture_is_not_an_elevation_grid(self):
        with self.assertRaisesRegex(ValueError,'single floating'):
            city.decode_raster(self.raster([0,1,2,3],count=3,dtype='uint8',nodata=255),[43.2,5.3,43.3,5.4],2,2)

    def test_georeference_displacement_rejected(self):
        with self.assertRaisesRegex(ValueError,'georeferencing'):
            city.decode_raster(self.raster([0,1,2,3],bounds=[5.2,43.15,5.5,43.35]),[43.2,5.3,43.3,5.4],2,2)

    def test_projected_raster_cannot_be_mislabelled_wgs84(self):
        with self.assertRaisesRegex(ValueError,'geographic'):
            city.decode_raster(self.raster([0,1,2,3],crs='EPSG:2154'),[43.2,5.3,43.3,5.4],2,2)

    def test_geographic_nad27_cannot_be_mislabelled_wgs84(self):
        with self.assertRaisesRegex(ValueError,'recognized WGS84'):
            city.decode_raster(self.raster([0,1,2,3],crs='EPSG:4267'),[43.2,5.3,43.3,5.4],2,2)

    def test_geographic_nad83_cannot_be_mislabelled_wgs84(self):
        with self.assertRaisesRegex(ValueError,'recognized WGS84'):
            city.decode_raster(self.raster([0,1,2,3],crs='EPSG:4269'),[43.2,5.3,43.3,5.4],2,2)

    def test_fully_nodata_raster_is_not_filled_with_sea_level(self):
        values,header=city.decode_raster(self.raster([-99999]*4),[43.2,5.3,43.3,5.4],2,2)
        self.assertEqual(values,[None]*4)

    def points_response(self,zs,coordinates=None):
        coords=coordinates or [(43.3,5.35)]*len(zs)
        return json.dumps({'elevations':[{'lat':lat,'lon':lon,'z':z} for z,(lat,lon) in zip(zs,coords)]}).encode()

    def test_point_api_exact_sentinel_and_negative_measurement(self):
        zs=[-99999,None,-2.55,0,24.28]
        self.assertEqual(city.decode_points(self.points_response(zs),[(43.3,5.35)]*5),[None,None,-2.55,0,24.28])

    def test_point_api_near_sentinel_cannot_be_silently_masked(self):
        with self.assertRaisesRegex(ValueError,'no value clamped'):
            city.decode_points(self.points_response([-99998.9]),[(43.3,5.35)])

    def test_point_api_changed_coordinate_rejected(self):
        with self.assertRaisesRegex(ValueError,'changed requested'):
            city.decode_points(self.points_response([20],[(43.31,5.35)]),[(43.3,5.35)])

    def test_point_api_partial_response_rejected(self):
        with self.assertRaisesRegex(ValueError,'omits requested'):
            city.decode_points(self.points_response([20]),[(43.3,5.35)]*2)

    def test_point_api_invalid_altitude_type_rejected(self):
        with self.assertRaisesRegex(ValueError,'no value clamped'):
            city.decode_points(self.points_response(['42 metres']),[(43.3,5.35)])

    def test_invalid_provider_observation_is_distinct_from_exact_nodata(self):
        values,invalid=city.decode_points(self.points_response([-99999,-99998.99,12.32]),[(43.3,5.35)]*3,allow_invalid=True)
        self.assertEqual(values,[None,None,12.32])
        self.assertEqual(len(invalid),1)
        self.assertEqual(invalid[0]['index'],1)
        self.assertEqual(invalid[0]['reportedZ'],-99998.99)
        self.assertEqual(invalid[0]['lat'],43.3)
        self.assertEqual(invalid[0]['lon'],5.35)

    def test_progress_index_cannot_claim_unacquired_fine_coverage(self):
        bounds=[43.2,5.3,43.3,5.4];base={'validPoints':10}
        result=[({'validPoints':4},{})]
        index=city.terrain_index(bounds,base,result,25)
        self.assertTrue(index['coverage']['complete'])
        self.assertFalse(index['coverage']['fineComplete'])
        self.assertEqual(index['coverage']['completedFinePartitions'],1)
        self.assertEqual(index['coverage']['requestedFinePartitions'],25)
        with self.assertRaisesRegex(ValueError,'missing partitions'):
            city.terrain_index(bounds,base,result,25,True)

    def test_published_grid_separates_invalid_observation_from_provider_nodata(self):
        import hashlib
        values=[None,None,-1.2,0,2.5,4.5]
        receipt={'sha256':'a'*64,'acquiredAt':'2026-10-23T12:00:00Z','url':city.POINT_API}
        header={'providerInvalidPoints':1,'providerInvalidSamplesSha256':'b'*64,'format':'IGN point-elevation JSON'}
        plan={'id':'fixture','bbox':[43.2,5.3,43.3,5.4],'width':3,'height':2,'spacingMeters':[100,100]}
        with TemporaryDirectory() as temporary,patch.object(city,'point_grid',return_value=(values,receipt,header)):
            descriptor,proof=city.acquire_grid(plan,Path(temporary),Path(temporary),base=True)
            raw=(Path(temporary)/Path(descriptor['path']).name).read_bytes();grid=json.loads(raw)
            self.assertEqual(descriptor['sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual(grid['providerInvalidPoints'],1)
            self.assertEqual(grid['providerNoDataPoints'],1)
            self.assertEqual(grid['missingPoints'],2)
            self.assertEqual(grid['values'],values)
            self.assertEqual(grid['macro'],'geo_marseille_commune')
            self.assertEqual(grid['provenance']['serviceSampling']['resampling'],'provider-unspecified')
            self.assertEqual(grid['verticalDatum'],grid['provenance']['verticalDatum'])
            self.assertRegex(grid['provenance']['acquiredAt'],r'^\d{4}-\d{2}-\d{2}$')
            self.assertEqual(grid['provenance']['downloadedAt'],'2026-10-23T12:00:00Z')
            # Validate the emitted metadata against the existing importer's
            # independent contract, which rejects full ISO dates and mismatched
            # vertical-datum strings in this source schema.
            import world_sources
            proof=world_sources._checked_existing_provenance(grid['provenance'])
            source=world_sources.provenance(name=proof['source'],license=proof['license'],attribution=proof['attribution'],
                                           acquired_at=proof['acquiredAt'],resource=proof['resource'],vertical_datum=proof['verticalDatum'])
            checked=world_sources.checked_terrain(grid,city.REGION,source,proof['inputSha256'],plan['bbox'])
            self.assertEqual(checked['validPoints'],4)

    def test_cached_wms_source_hash_mismatch_prevents_publication(self):
        import hashlib
        url='https://data.geopf.fr/wms-r/wms?fixture=1'
        key=hashlib.sha256(url.encode()).hexdigest()
        with TemporaryDirectory() as temporary:
            folder=Path(temporary);(folder/(key+'.tif')).write_bytes(b'corrupted')
            (folder/(key+'.json')).write_text(json.dumps({'url':url,'bytes':9,'sha256':'0'*64}))
            with patch.object(city,'fetch',side_effect=AssertionError('corruption must not trigger a silent re-download')):
                with self.assertRaisesRegex(ValueError,'differs from its acquisition receipt'):
                    city.read_cached(folder,url,10)

    def test_actual_edge_audit_detects_height_and_nodata_disagreement(self):
        import hashlib
        with TemporaryDirectory() as temporary:
            folder=Path(temporary);descriptors=[]
            for i,bounds,values in [(0,[43.2,5.3,43.3,5.4],[1,2,3,None]),
                                    (1,[43.2,5.4,43.3,5.5],[2,4,None,8])]:
                raw=city.canonical({'width':2,'height':2,'values':values});sha=hashlib.sha256(raw).hexdigest()
                p=folder/f'{i}.json';p.write_bytes(raw)
                descriptors.append({'path':str(p),'sha256':sha,'bytes':len(raw),'bbox':bounds})
            index={'tiles':descriptors,'coverage':{'fineComplete':True}}
            audit=city.audit_shared_edges(index,folder)
            self.assertEqual(audit['comparedNodes'],2)
            self.assertEqual(audit['mismatches'],0)
            # Change one measured height, then turn the matching missing node
            # into a measurement; both changes must be detected independently.
            raw=city.canonical({'width':2,'height':2,'values':[2.5,4,6,8]})
            (folder/'1.json').write_bytes(raw);descriptors[1].update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            audit=city.audit_shared_edges(index,folder)
            self.assertEqual(audit['mismatches'],2)
            self.assertEqual(audit['maximumHeightDifferenceMeters'],.5)


if __name__=='__main__':unittest.main()
