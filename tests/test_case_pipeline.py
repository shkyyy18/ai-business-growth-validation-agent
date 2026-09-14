import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from consultant_case import run_case, verify_case, validate_public_input

class CasePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.case=json.loads((ROOT/'experiments/business-advisor-e2e-001/case.json').read_text(encoding='utf-8'))
        paths={e['path'] for e in self.case['evidence']}|{self.case['public_input']['path']}
        for name in paths:
            dst=self.root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dst)
        self.path=self.root/'case.json';self.save();self.output=self.root/'output'
    def save(self):
        self.path.write_text(json.dumps(self.case,ensure_ascii=False),encoding='utf-8')
    def run_it(self,force=False):
        return run_case(self.path,self.output,self.root,force=force)
    def data(self):
        return json.loads((self.root/self.case['public_input']['path']).read_text(encoding='utf-8'))
    def test_real_captured_metadata_end_to_end_handoff(self):
        result=self.run_it()
        self.assertEqual(result['source_integrity'],'passed')
        self.assertEqual(len(result['nodes']),12)
        self.assertEqual(result['counts']['observed_account_count'],1)
        self.assertEqual(result['counts']['observed_work_count'],2)
        self.assertFalse(result['commercial_loop_validated'])
        self.assertFalse(result['customer_delivery_validated'])
        self.assertFalse(result['industry_research_complete'])
        self.assertEqual(len(list(self.output.iterdir())),5)
        work=json.loads((self.output/'content-library.json').read_text(encoding='utf-8'))
        self.assertIsNone(work[0]['metrics']['views'])
        self.assertEqual(work[0]['raw_stats']['playCount'],0)
    def test_cross_platform_bom_and_newline_fingerprints(self):
        for item in self.case['evidence']:
            path=self.root/item['path']
            text=path.read_text(encoding='utf-8-sig')
            path.write_bytes(b'\xef\xbb\xbf'+text.replace('\n','\r\n').encode('utf-8'))
        self.assertEqual(self.run_it()['source_integrity'],'passed')
    def test_reproducible_output(self):
        self.run_it();old={p.name:p.read_bytes() for p in self.output.iterdir()}
        self.run_it(force=True)
        self.assertEqual(old,{p.name:p.read_bytes() for p in self.output.iterdir()})
    def test_no_overwrite_without_force(self):
        self.run_it()
        with self.assertRaises(ValueError):self.run_it()
    def test_source_change_stops_before_writing(self):
        (self.root/self.case['evidence'][0]['path']).write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError):self.run_it()
        self.assertFalse(self.output.exists())
    def test_missing_source_rejected(self):
        (self.root/self.case['evidence'][0]['path']).unlink()
        with self.assertRaises(ValueError):self.run_it()
    def test_path_escape_rejected(self):
        self.case['evidence'][0]['path']='../outside.md';self.save()
        with self.assertRaises(ValueError):self.run_it()
    def test_synthetic_is_not_real_evidence(self):
        self.case['evidence'][0]['synthetic']=True;self.save()
        with self.assertRaises(ValueError):self.run_it()
    def test_public_subject_is_not_client(self):
        self.case['evidence'][1]['kind']='client_acceptance';self.save()
        with self.assertRaises(ValueError):self.run_it()
    def test_missing_client_evidence_not_promoted_by_likes(self):
        result=self.run_it()
        n9=next(n for n in result['nodes'] if n['id']=='N9')
        self.assertIn('payment_outcome',n9['missing_evidence_kinds'])
        self.assertEqual(n9['record_status'],'needs_evidence')
    def test_duplicate_evidence_rejected(self):
        self.case['evidence'].append(copy.deepcopy(self.case['evidence'][0]));self.save()
        with self.assertRaises(ValueError):self.run_it()
    def test_unknown_author_rejected(self):
        d=self.data();d['works'][0]['author_uid']='other'
        with self.assertRaises(ValueError):validate_public_input(d)
    def test_duplicate_work_rejected(self):
        d=self.data();d['works'].append(copy.deepcopy(d['works'][0]))
        with self.assertRaises(ValueError):validate_public_input(d)
    def test_aggregation_id_is_not_original_id(self):
        d=self.data();d['works'][0]['original_url']=d['works'][0]['source_url']
        with self.assertRaises(ValueError):validate_public_input(d)
    def test_recommendation_boundary_required(self):
        d=self.data();d['works'][0]['material']['main_vs_recommendation_verified']=False
        with self.assertRaises(ValueError):validate_public_input(d)
    def test_invalid_metrics_rejected(self):
        for value in [True,-1,float('nan'),float('inf'),'1316']:
            d=self.data();d['works'][0]['metrics']['likes']=value
            with self.subTest(value=value),self.assertRaises(ValueError):validate_public_input(d)
    def test_counts_not_industry_sufficiency(self):
        d=self.data();d['coverage']['industry_sufficiency']=True
        with self.assertRaises(ValueError):validate_public_input(d)
    def test_reading_count_mismatch(self):
        d=self.data();d['coverage']['original_videos_viewed']=1
        with self.assertRaises(ValueError):validate_public_input(d)
    def test_malformed_top_level(self):
        with self.assertRaises(ValueError):validate_public_input([])
        with self.assertRaises(ValueError):verify_case([],self.root)
    def test_no_unfounded_viral_classification(self):
        d=self.data();d['works'][0]['viral_classification']='viral'
        with self.assertRaises(ValueError):validate_public_input(d)

if __name__=='__main__':unittest.main()
