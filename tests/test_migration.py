import copy,json,tempfile,unittest
from decimal import Decimal
from pathlib import Path
from migration.compiler import compile_mapping,write_artifacts,Rejected
from migration.powercenter import read_export
from migration.reconcile import compare
BASE=Path(__file__).resolve().parents[1]
class MigrationTests(unittest.TestCase):
    def setUp(self): self.ir=read_export(BASE/'examples/orders.xml')
    def test_golden_sql(self): self.assertEqual(compile_mapping(self.ir),(BASE/'artifacts/demo/mapping.sql').read_text())
    def test_hash_reproducible(self):
        with tempfile.TemporaryDirectory() as d:
            a=write_artifacts(self.ir,d);b=write_artifacts(self.ir,d);self.assertEqual(a,b)
    def test_unsupported_expr(self):
        self.ir['select'][0]['expr']={'raw':'DROP TABLE orders'}
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_unknown_field(self):
        self.ir['where']['left']={'field':'ghost'}
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_identifier_injection(self):
        self.ir['source']='orders; DELETE'
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_wrong_types(self):
        self.ir['where']['right']={'literal':100,'type':'BIGINT'}
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_decimal_precision_rejected(self):
        self.ir['where']['right']['literal']='100.001'
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_streaming_rejected(self):
        self.ir['semantics']['mode']='unbounded'
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_extra_ir_rejected(self):
        self.ir['credentials']='secret'
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_duplicate_field_rejected(self):
        self.ir['fields'].append(self.ir['fields'][0])
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_alias_collision(self):
        self.ir['select'][1]['as']='id'
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_bigint_overflow(self):
        self.ir['where']['right']={'literal':2**63,'type':'BIGINT'}
        with self.assertRaises(Rejected):compile_mapping(self.ir)
    def test_safe_upper(self):
        self.ir['select'][2]['expr']={'upper':{'field':'region'}}
        self.assertIn('UPPER(`region`)',compile_mapping(self.ir))
    def test_no_artifacts_on_failure(self):
        self.ir['version']=2
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(Rejected):write_artifacts(self.ir,d)
            self.assertEqual(list(Path(d).iterdir()),[])
    def xml_variant(self,old,new):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.xml';p.write_text((BASE/'examples/orders.xml').read_text().replace(old,new));return read_export(p)
    def test_unsupported_transform(self):
        with self.assertRaises(Rejected):self.xml_variant('TYPE="Filter"','TYPE="Lookup"')
    def test_missing_edge(self):
        with self.assertRaises(Rejected):self.xml_variant('FROMFIELD="id"','FROMFIELD="missing"')
    def test_extra_metadata(self):
        with self.assertRaises(Rejected):self.xml_variant('<MAPPING NAME=', '<MAPPING EXTRA="x" NAME=')
    def test_xml_entity_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.xml';p.write_text('<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><POWERMART>&a;</POWERMART>')
            with self.assertRaises(Rejected):read_export(p)
    def test_duplicate_bag(self): self.assertFalse(compare([(1,),(1,)],[(1,)])['passed'])
    def test_order_irrelevant(self): self.assertTrue(compare([(1,),(2,)],[(2,),(1,)])['passed'])
    def test_null_not_string(self):self.assertFalse(compare([(None,)],[('None',)])['passed'])
    def test_decimal_normalization(self):self.assertTrue(compare([(Decimal('100.00'),)],[(Decimal('100'),)])['passed'])
    def test_type_sensitive(self):self.assertFalse(compare([(1,)],[('1',)])['passed'])
    def test_threshold_mutation_changes_hash(self):
        with tempfile.TemporaryDirectory() as d:
            a=write_artifacts(self.ir,d);self.ir['where']['op']='gt';b=write_artifacts(self.ir,d)
            self.assertNotEqual(a['sql_sha256'],b['sql_sha256'])
if __name__=='__main__':unittest.main()
