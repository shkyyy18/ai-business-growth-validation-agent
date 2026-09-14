import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from research_corpus import compile_batches,search_notes
BATCHES=['research/m1-channel-discovery-2026-09-14','research/m1-professional-2026-09-14']

class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        for b in BATCHES:
            (self.root/b).mkdir(parents=True)
            for n in ['discovery-index.json','reading-notes.json']:shutil.copy2(ROOT/b/n,self.root/b/n)
    def mutate(self,name,fn,batch=0):
        p=self.root/BATCHES[batch]/name;x=json.loads(p.read_text(encoding='utf-8'));fn(x);p.write_text(json.dumps(x),encoding='utf-8')
    def test_real_two_batch_counts_and_boundaries(self):
        d=compile_batches(BATCHES,self.root)
        self.assertEqual(d['coverage']['observed_page_count'],11)
        self.assertEqual(d['coverage']['pages_with_attributed_works'],10)
        self.assertEqual(d['coverage']['observed_work_count'],172)
        self.assertEqual(d['coverage']['observed_account_count'],135)
        self.assertEqual(d['coverage']['platform_text_read'],60)
        self.assertEqual(d['coverage']['accounts_with_text_read'],40)
        self.assertFalse(d['coverage']['industry_sufficiency'])
        self.assertTrue(all(w['metrics']['views'] is None for w in d['works']))
    def test_supplemental_reading_changes_read_counts_not_discovery(self):
        batches=BATCHES+['research/m2-live-review-reading-2026-09-14']
        d=compile_batches(batches,ROOT)
        self.assertEqual(d['coverage']['observed_page_count'],11)
        self.assertEqual(d['coverage']['observed_work_count'],172)
        self.assertEqual(d['coverage']['observed_account_count'],135)
        self.assertEqual(d['coverage']['platform_asr_available'],81)
        self.assertEqual(d['coverage']['platform_text_read'],62)
        self.assertEqual(d['coverage']['accounts_with_text_read'],42)
        self.assertEqual(d['coverage']['original_videos_viewed'],0)
        self.assertEqual(sum(not w['material']['platform_text_read'] for w in d['works']),110)
        self.assertEqual(sum(w['material']['platform_asr_available'] and not w['material']['platform_text_read'] for w in d['works']),19)

    def test_published_corpus_replays_without_private_captures(self):
        batches=BATCHES+['research/m2-live-review-reading-2026-09-14']
        expected=json.loads((ROOT/'experiments/business-advisor-e2e-002/public-corpus.json').read_text(encoding='utf-8'))
        self.assertEqual(compile_batches(batches,ROOT),expected)

    def test_same_works_in_distinct_batches_not_summed(self):
        # Reuse identical records under another batch to exercise overlap;
        # this test does not create new real research observations.
        for name in ['discovery-index.json','reading-notes.json']:
            shutil.copy2(self.root/BATCHES[0]/name,self.root/BATCHES[1]/name)
        d=compile_batches(BATCHES,self.root)
        self.assertEqual(d['coverage']['observed_work_count'],98)
        self.assertEqual(d['coverage']['platform_text_read'],23)
        self.assertTrue(all(len(w['observations'])>=2 for w in d['works']))
    def test_merged_read_count_cannot_be_inflated(self):
        from consultant_case import validate_public_input
        for key in ['platform_text_read','platform_asr_available','accounts_with_text_read']:
            d=compile_batches(BATCHES,self.root);d['coverage'][key]+=1
            with self.subTest(key=key),self.assertRaises(ValueError):validate_public_input(d)

    def test_repeatable(self):
        self.assertEqual(compile_batches(BATCHES,self.root),compile_batches(BATCHES,self.root))
    def test_duplicate_batch_rejected(self):
        with self.assertRaises(ValueError):compile_batches([BATCHES[0]]*2,self.root)
    def test_stale_read_note_rejected(self):
        self.mutate('reading-notes.json',lambda d:d['notes'][0].update(platform_asr_sha256='changed'))
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_title_only_is_not_reading(self):
        self.mutate('reading-notes.json',lambda d:d['notes'][0].update(platform_asr_sha256=None))
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_identity_conflict_rejected(self):
        def conflict(d):
            o=copy.deepcopy(d['works'][0]['observations'][0]);o['author_sec_uid']='different';d['works'][0]['observations'].append(o)
        self.mutate('discovery-index.json',conflict)
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_unknown_author_rejected(self):
        self.mutate('discovery-index.json',lambda d:d['works'][0]['observations'][0].update(author_sec_uid=None))
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_false_read_flag_rejected(self):
        self.mutate('discovery-index.json',lambda d:d['works'][0].update(human_or_assistant_text_read=False))
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_count_mismatch_rejected(self):
        self.mutate('discovery-index.json',lambda d:d['counts'].update(text_read=999))
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_original_video_claim_needs_other_importer(self):
        self.mutate('discovery-index.json',lambda d:d['works'][0].update(original_video_viewed=True))
        with self.assertRaises(ValueError):compile_batches(BATCHES,self.root)
    def test_frozen_second_case_handoff(self):
        from consultant_case import run_case
        case_path=ROOT/'experiments/business-advisor-e2e-002/case.json'
        case=json.loads(case_path.read_text(encoding='utf-8'))
        for name in {e['path'] for e in case['evidence']}|{case['public_input']['path']}:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
        target=self.root/'case.json';target.write_text(json.dumps(case),encoding='utf-8')
        audit=run_case(target,self.root/'out',self.root)
        self.assertEqual(audit['counts']['platform_text_read'],62)
        self.assertFalse(audit['commercial_loop_validated'])
        self.assertFalse(audit['customer_delivery_validated'])
        self.assertIn('client_acceptance',next(n for n in audit['nodes'] if n['id']=='N8')['missing_evidence_kinds'])

    def test_query_only_retrieves_existing_material(self):
        rows=search_notes(compile_batches(BATCHES,self.root),'解压')
        self.assertTrue(any(x['work_id']=='7307878608217951538' for x in rows))
        self.assertTrue(all('notes' in x for x in rows))

if __name__=='__main__':unittest.main()
