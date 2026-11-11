"""Negative tests ensure documentation checks cannot pass by ignoring missing links."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('registry', ROOT/'tools/verify_lore_registry.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = {'schema':1,'canon':'fan-lore-original-non-officiel','narrative_year':2297,'scope':'Only fixture narrative modules','entries':[{'id':'fixture','title':'Fixture','status':'implemented-local-scope','model':'MistralFixture','sources':['src/v050/10_fixture.js'],'chapters':['docs/LORE_FIXTURE.md'],'logic_test':'tests/expansion/lore_fixture.cjs','delivered':'One scene','open_limit':'No global simulation'}]}
        for name,text in {'docs/BIBLE_LORE_FALLOUT_MISTRAL.md':'2297 — création de fan non officielle\n[registre](REGISTRE_LORE.json)\n[chapitre](LORE_FIXTURE.md)', 'LORE.md':'[registre](docs/REGISTRE_LORE.json)\n[chapitre](docs/LORE_FIXTURE.md)', 'docs/LORE_FIXTURE.md':'# Fiction','src/v050/10_fixture.js':'const MistralFixture = {};','tests/expansion/lore_fixture.cjs':'// test','src/game.js':'const MistralFixture = {}; '}.items():
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        (self.root/'docs/REGISTRE_LORE.json').write_text(json.dumps(self.data))
    def result(self): return checker.inspect_registry(self.root, self.data, 'src/game.js')
    def fail_with(self,needle): self.assertTrue(any(needle in e for e in self.result()['errors']),self.result())
    def test_valid_fixture(self): self.assertTrue(self.result()['ok'])
    def test_current_repository(self): self.assertTrue(checker.inspect_registry(ROOT)['ok'],checker.inspect_registry(ROOT)['errors'])
    def test_duplicate_id(self): self.data['entries'].append(copy.deepcopy(self.data['entries'][0]));self.fail_with('duplicate id')
    def test_module_without_entry(self): (self.root/'src/v050/10_extra.js').write_text('const MistralExtra = {};');self.fail_with('undocumented narrative module')
    def test_missing_source(self): (self.root/'src/v050/10_fixture.js').unlink();self.fail_with('declared module absent')
    def test_missing_chapter(self): (self.root/'docs/LORE_FIXTURE.md').unlink();self.fail_with('unreadable docs/LORE_FIXTURE')
    def test_missing_bible_link(self): (self.root/checker.BIBLE).write_text('2297 — création de fan non officielle\n[registre](REGISTRE_LORE.json)');self.fail_with('not linked from central bible')
    def test_missing_index_link(self): (self.root/'LORE.md').write_text('[registre](docs/REGISTRE_LORE.json)');self.fail_with('not linked from LORE.md')
    def test_missing_model(self): (self.root/'src/v050/10_fixture.js').write_text('// stub');self.fail_with('model declaration not found')
    def test_bundle_model_missing(self): (self.root/'src/game.js').write_text('// old build');self.fail_with('model missing from compiled')
    def test_missing_test(self): (self.root/'tests/expansion/lore_fixture.cjs').unlink();self.fail_with('unreadable tests/')
    def test_missing_limit(self): self.data['entries'][0]['open_limit']='';self.fail_with('missing open_limit')
    def test_bad_schema(self): self.data['schema']=2;self.fail_with('unsupported')
    def test_future_year_or_official_claim(self): self.data['canon']='official';self.fail_with('canon qualifier')
    def test_path_escape(self): self.data['entries'][0]['sources']=['../outside.js'];self.fail_with('outside repository')
    def test_empty_entries(self): self.data['entries']=[];self.fail_with('empty entries')
    def test_empty_doc(self): (self.root/'docs/LORE_FIXTURE.md').write_text('');self.fail_with('empty file')
    def test_unknown_status(self): self.data['entries'][0]['status']='whole-game-finished';self.fail_with('undocumented status')
    def test_hashes_are_real(self):
        import hashlib
        p='docs/LORE_FIXTURE.md';self.assertEqual(self.result()['sha256'][p],hashlib.sha256((self.root/p).read_bytes()).hexdigest())

if __name__=='__main__': unittest.main()
