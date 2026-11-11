"""Source inventory is a bounded audit, not evidence of 98 implemented creatures."""
import copy, hashlib, importlib.util, json, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('regional_audit',ROOT/'tools/audit_regional_content.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class RegionalInventoryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=audit.build(ROOT)
 def test_exact_regional_coverage(self):
  ids=[x['id'] for x in self.data['regional_weapons']];self.assertEqual(len(ids),55);self.assertEqual(len(set(ids)),55)
 def test_current_bible_scope(self):self.assertEqual(len(self.data['bible_weapons']),49);self.assertEqual(len(self.data['creatures']),98)
 def test_nine_existing_rigs_not_ninety_eight(self):self.assertEqual(self.data['counts']['regional_rigs'],9)
 def test_general_biset_not_postal_pigeon(self):
  x=next(x for x in self.data['creatures'] if x['name']=='Général Biset');self.assertEqual(x['status'],'concept-ou-temoignage');self.assertFalse(x['rig_ids'])
 def test_crowned_rat_does_not_claim_aggregate(self):
  x=next(x for x in self.data['creatures'] if x['name']=='Rat-couronné');self.assertEqual(x['rig_ids'],['ratCrowned']);self.assertIn('pas l’agrégat',x['limit'])
 def test_revolutionary_pike_not_assimilated(self):
  x=next(x for x in self.data['bible_weapons'] if x['name']=='Pique de la République');self.assertFalse(x['catalogue_ids'])
 def test_regional_visuals_are_not_all_unique(self):
  self.assertTrue(all('unique_model' not in x for x in self.data['regional_weapons']));self.assertEqual(sum(x['additional_presentation'] for x in self.data['regional_weapons']),4)
 def test_actual_ammunition_names(self):
  d={x['id']:x for x in self.data['regional_weapons']};self.assertEqual(d['garlabanMortar']['ammo_id'],'grenade40');self.assertEqual(d['mistralNeedler']['ammo_id'],'syringes');self.assertEqual(d['saltArc']['ammo_id'],'protonCell')
 def test_melee_has_no_invented_ammo(self):
  d=next(x for x in self.data['regional_weapons'] if x['id']=='ceramicSaw');self.assertIsNone(d['ammo_id']);self.assertIsNone(d['clip']);self.assertIsNone(d['base_reload'])
 def test_source_hashes_match_examined_bytes(self):
  for name,h in self.data['source_sha256'].items():self.assertEqual(h,hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
 def test_documentation_current(self):
  self.assertEqual(json.loads((ROOT/audit.JSON_PATH).read_text()),self.data);self.assertEqual((ROOT/audit.MD_PATH).read_text(),audit.markdown(self.data))
 def test_deterministic_serialization(self):self.assertEqual(audit.markdown(self.data),audit.markdown(copy.deepcopy(self.data)))
 def test_no_missing_section_silent_success(self):
  with self.assertRaises(ValueError):audit.sections('## 38. Fake\n- x',38,42)
 def test_bullet_format_and_section_provenance(self):
  self.assertEqual(audit.bullets('## 38. Atelier\n- **Arme** : description ;\nprose\n- Autre ;'),[('Arme','38. Atelier'),('Autre','38. Atelier')])
 def test_normalization_not_fuzzy_aliasing(self):
  self.assertEqual(audit.fold('Écorcheur-calcaire'),audit.fold('ecorcheur calcaire'));self.assertNotEqual(audit.fold('Roi-Couronne'),audit.fold('Roi des Égouts'))
 def test_stale_document_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);(r/'docs').mkdir();(r/audit.JSON_PATH).write_text('{}');(r/audit.MD_PATH).write_text('old')
   with patch.object(audit,'ROOT',r),patch.object(audit,'build',return_value=self.data),patch('sys.argv',['audit','--check']):
    with self.assertRaises(SystemExit) as caught:audit.main()
   self.assertIn('périmé',str(caught.exception))
 def test_missing_id_is_not_silently_dropped(self):
  original=subprocess.check_output
  def intercept(args,**kwargs):
   out=original(args,**kwargs)
   if 'regional_catalog_snapshot' in args[-1]:
    d=json.loads(out);d['regional'].append('nonexistent');return json.dumps(d)
   return out
  with patch.object(audit.subprocess,'check_output',side_effect=intercept):
   with self.assertRaisesRegex(ValueError,'Unmapped regional ID'):audit.build(ROOT)
 def test_unknown_ammo_is_rejected(self):
  original=subprocess.check_output
  def intercept(args,**kwargs):
   out=original(args,**kwargs)
   if 'regional_catalog_snapshot' in args[-1]:
    d=json.loads(out);d['weapons']['mistralNeedler']['ammoId']='inventedAmmo';return json.dumps(d)
   return out
  with patch.object(audit.subprocess,'check_output',side_effect=intercept):
   with self.assertRaisesRegex(ValueError,'Unknown ammunition'):audit.build(ROOT)
 def test_no_network_or_side_effect_in_read_model(self):
  before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in self.data['source_sha256']};audit.build(ROOT)
  self.assertEqual(before,{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in before})
 def test_limits_survive_generated_table(self):
  s=audit.markdown(self.data);self.assertIn('pas un décompte d’espèces uniques',s);self.assertIn('COCHONNET',s);self.assertIn('concept à traiter',s)
if __name__=='__main__':unittest.main()
