"""Isolated source-water fixtures. No test response is installed as geography."""
from pathlib import Path
import hashlib
import json
import math
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlencode, parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import city_water_sources as water
import acquire_city_water as acquire
from world_sources import SourceError, canonical


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fixture(directory):
    s,w,n,e=water.BOUNDS
    tx=lambda x:math.floor((x+180)/360*16384)
    ty=lambda y:math.floor((1-math.asinh(math.tan(math.radians(y)))/math.pi)/2*16384)
    lat=lambda y:math.degrees(math.atan(math.sinh(math.pi*(1-2*y/16384))))
    lon=lambda x:x/16384*360-180
    grid={'zoom':14,'minX':tx(w),'maxX':tx(e),'minY':ty(n),'maxY':ty(s)}
    bounds=[lat(grid['maxY']+1),lon(grid['minX']),lat(grid['minY']),lon(grid['maxX']+1)]
    tile={'z':14,'x':grid['minX'],'y':grid['minY']}
    box=[lat(tile['y']+1),lon(tile['x']),lat(tile['y']),lon(tile['x']+1)]
    a,b,c,d=box[1],box[0],box[3],box[2]
    ring=[[a,b],[c,b],[c,d],[a,d],[a,b]]
    provider={'source':'Explicitly synthetic coastline fixture','license':'CC0 fixture','attribution':'Test only','acquiredAt':'2026-10-23','resource':'ign-city-water','url':'https://data.geopf.fr/wfs/ows'}
    def store(obj):
        raw=canonical(obj);sha=digest(raw);name='water-'+sha[:16]+'.json';(directory/name).write_bytes(raw)
        return{'path':water.PREFIX+name,'bytes':len(raw),'sha256':sha}
    inputs=[]
    for layer,geom,properties in [('BDCARTO_V5:occupation_du_sol',{'type':'Polygon','coordinates':[ring]},{'nature':'Eau libre'}),('BDTOPO_V3:limite_terre_mer',{'type':'LineString','coordinates':ring[:2]},{'niveau':'Plus hautes eaux'})]:
        body=canonical({'type':'FeatureCollection','crs':{'properties':{'name':'urn:ogc:def:crs:EPSG::4326'}},'numberMatched':1,'numberReturned':1,'features':[{'type':'Feature','id':layer+':fixture','properties':properties,'geometry':geom}]})
        url='https://data.geopf.fr/wfs/ows?'+urlencode({'TYPENAMES':layer,'SRSNAME':'EPSG:4326'})
        inputs.append(store({'schemaVersion':1,'role':'source-response','url':url,'bytes':len(body),'sha256':digest(body),'body':body.decode()}))
    raw_tile={'schemaVersion':1,'role':'water-tile','tile':tile,'bbox':box,'source':provider,'features':[{'type':'Feature','id':'synthetic-water','properties':{'kind':'water','v051Water':True,'provenance':provider},'geometry':{'type':'Polygon','coordinates':[ring]}}]}
    descriptor=store(raw_tile);descriptor.update(tile=tile,bbox=box,features=1,vertices=5)
    index={'schemaVersion':1,'crs':'EPSG:4326','bbox':bounds,'municipalityBbox':water.BOUNDS,'grid':grid,'source':provider,'inputs':inputs,'tiles':[descriptor],'derivation':{'noSimplification':True}}
    (directory/'water-index.json').write_bytes(canonical(index))
    return index,raw_tile


class SourceWaterTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.directory=Path(self.temporary.name)
        self.index,self.tile=fixture(self.directory)

    def tearDown(self):
        self.temporary.cleanup()

    def rewrite_index(self):
        (self.directory/'water-index.json').write_bytes(canonical(self.index))

    def rewrite(self,descriptor,obj):
        raw=canonical(obj);sha=digest(raw);name='water-'+sha[:16]+'.json';(self.directory/name).write_bytes(raw)
        descriptor.update(path=water.PREFIX+name,bytes=len(raw),sha256=sha);self.rewrite_index()

    def mutate_input(self,change):
        d=self.index['inputs'][0];receipt=json.loads((self.directory/Path(d['path']).name).read_bytes());body=json.loads(receipt['body']);change(body);raw=canonical(body);receipt.update(body=raw.decode(),bytes=len(raw),sha256=digest(raw));self.rewrite(d,receipt)

    def test_full_fixture_validates_exact_bytes_without_shapely(self):
        import builtins
        original=builtins.__import__
        def restricted(name,*args,**kwargs):
            if name.startswith('shapely'):raise ImportError('Runtime intentionally has no Shapely')
            return original(name,*args,**kwargs)
        with patch('builtins.__import__',side_effect=restricted):files,providers=water.validate_directory_files(self.directory)
        self.assertEqual(len(files),4);self.assertEqual(providers[0]['resource'],'ign-city-water')

    def test_missing_optional_atlas_is_empty(self):
        (self.directory/'water-index.json').unlink();self.assertEqual(water.validate_directory_files(self.directory),({},[]))

    def test_corrupt_file_is_not_reused(self):
        p=self.directory/Path(self.index['tiles'][0]['path']).name;p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaisesRegex(SourceError,'SHA'):water.validate_directory_files(self.directory)

    def test_traversal_descriptor_rejected(self):
        self.index['tiles'][0]['path']='data/map_pack/city/../water-deadbeefdeadbeef.json';self.rewrite_index()
        with self.assertRaisesRegex(SourceError,'unsafe'):water.validate_directory_files(self.directory)

    def test_unattributed_water_is_rejected(self):
        self.index['source']['attribution']='';self.rewrite_index()
        with self.assertRaises(SourceError):water.validate_directory_files(self.directory)

    def test_a_partial_source_query_cannot_be_called_complete(self):
        self.mutate_input(lambda b:b.update(numberMatched=2))
        with self.assertRaisesRegex(SourceError,'incomplete'):water.validate_directory_files(self.directory)

    def test_nonfinite_source_coordinates_are_rejected(self):
        self.mutate_input(lambda b:b['features'][0]['geometry']['coordinates'][0].__setitem__(1,[181,43]))
        with self.assertRaisesRegex(SourceError,'coordinates'):water.validate_directory_files(self.directory)

    def test_wrong_source_classification_is_rejected(self):
        self.mutate_input(lambda b:b['features'][0]['properties'].update(nature='Forêt'))
        with self.assertRaisesRegex(SourceError,'classification'):water.validate_directory_files(self.directory)

    def test_wrong_source_crs_is_rejected(self):
        self.mutate_input(lambda b:b.update(crs={'properties':{'name':'EPSG:2154'}}))
        with self.assertRaisesRegex(SourceError,'CRS'):water.validate_directory_files(self.directory)

    def test_counts_cannot_be_fabricated(self):
        self.index['tiles'][0]['vertices']=6;self.rewrite_index()
        with self.assertRaisesRegex(SourceError,'counts'):water.validate_directory_files(self.directory)

    def test_coordinate_does_not_select_another_xyz_tile(self):
        self.index['tiles'][0]['tile']['x']+=1;self.rewrite_index()
        with self.assertRaisesRegex(SourceError,'XYZ'):water.validate_directory_files(self.directory)

    def test_hole_outside_source_water_rejected(self):
        self.tile['features'][0]['geometry']['coordinates'].append([[6,43],[6.001,43],[6.001,43.001],[6,43.001],[6,43]])
        self.rewrite(self.index['tiles'][0],self.tile)
        with self.assertRaisesRegex(SourceError,'hole'):water.validate_directory_files(self.directory)

    def test_vertex_beyond_tile_boundary_rejected(self):
        self.tile['features'][0]['geometry']['coordinates'][0][1][0]+=.1;self.rewrite(self.index['tiles'][0],self.tile)
        with self.assertRaises(SourceError):water.validate_directory_files(self.directory)

    def test_repeated_water_tile_rejected(self):
        self.index['tiles'].append(self.index['tiles'][0]);self.rewrite_index()
        with self.assertRaisesRegex(SourceError,'repeated'):water.validate_directory_files(self.directory)

    def test_symlink_index_rejected(self):
        p=self.directory/'water-index.json';raw=p.read_bytes();p.unlink();(self.directory/'other').write_bytes(raw);p.symlink_to(self.directory/'other')
        with self.assertRaisesRegex(SourceError,'symlink'):water.validate_directory_files(self.directory)

    def test_acquisition_is_exact_and_reproducible_from_fixed_source_bodies(self):
        try:from shapely.geometry import shape,Point
        except ImportError:self.skipTest('Shapely optional acquisition dependency not installed')
        s,w,n,e=water.BOUNDS;middle=(w+e)/2
        rectangle=[[w-.03,s-.03],[middle,s-.03],[middle,n+.03],[w-.03,n+.03],[w-.03,s-.03]]
        def payload(layer):
            geom={'type':'Polygon','coordinates':[rectangle]} if layer.startswith('BDCARTO') else {'type':'LineString','coordinates':[[middle,s-.03],[middle,n+.03]]}
            props={'nature':'Eau libre'} if layer.startswith('BDCARTO') else {'niveau':'Plus hautes eaux'}
            return canonical({'type':'FeatureCollection','numberMatched':1,'numberReturned':1,'crs':{'properties':{'name':'urn:ogc:def:crs:EPSG::4326'}},'features':[{'type':'Feature','id':layer+':fixture','properties':props,'geometry':geom}]})
        class FakeCache:
            def __init__(self,*args):pass
            def __call__(self,url):return payload(parse_qs(urlsplit(url).query)['TYPENAMES'][0])
        with tempfile.TemporaryDirectory() as temp,patch.object(acquire,'Cache',FakeCache):
            path=Path(temp);first=acquire.acquire(path/'cache',path/'atlas');before=(path/'atlas/water-index.json').read_bytes();second=acquire.acquire(path/'cache',path/'atlas')
            self.assertEqual(before,(path/'atlas/water-index.json').read_bytes());self.assertEqual(first,second)
            features=[]
            for d in first['tiles']:features.extend(json.loads((path/'atlas'/Path(d['path']).name).read_bytes())['features'])
            self.assertTrue(any(shape(f['geometry']).contains(Point(w+.01,(s+n)/2)) for f in features))
            self.assertFalse(any(shape(f['geometry']).contains(Point(e-.01,(s+n)/2)) for f in features))
            self.assertEqual(first['derivation']['unsupportedTinyFragments'],[])


if __name__=='__main__':unittest.main()
