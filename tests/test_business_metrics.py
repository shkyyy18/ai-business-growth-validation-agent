import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from business_metrics import calculate_live_metrics

# SYNTHETIC arithmetic fixtures only. No actual live-stream/customer result.
BASE={"definitions_confirmed":True,"source_ref":"synthetic-unit-test","currency":"CNY","window_start":"2026-09-14T20:00:00+08:00","window_end":"2026-09-14T21:00:00+08:00","values":{"impression_events":1000,"entry_events":200,"view_sessions":200,"viewer_uv":150,"buyer_uv":3,"watch_seconds_sum":6000,"gmv":900,"ad_attributed_gmv":600,"ad_spend":200,"realized_profit":-50,"total_cost":950}}
class BusinessMetricsTests(unittest.TestCase):
    def test_explicit_formulas(self):
        r=calculate_live_metrics(BASE)['metrics']
        self.assertAlmostEqual(r['entry_rate_event_basis'],0.2)
        self.assertAlmostEqual(r['buyer_conversion_uv_basis'],0.02)
        self.assertAlmostEqual(r['mean_watch_seconds_per_session'],30)
        self.assertAlmostEqual(r['gmv_per_1000_view_sessions'],4500)
        self.assertAlmostEqual(r['ad_gmv_roas'],3)
        self.assertAlmostEqual(r['profit_roi'],-50/950)
        self.assertAlmostEqual(r['mean_entries_per_minute'],200/60)
    def test_missing_is_not_zero(self):
        d=copy.deepcopy(BASE);d['values']={}
        r=calculate_live_metrics(d)
        self.assertTrue(all(v is None for v in r['metrics'].values()))
    def test_zero_numerator_is_zero(self):
        d=copy.deepcopy(BASE);d['values']['buyer_uv']=0
        self.assertEqual(calculate_live_metrics(d)['metrics']['buyer_conversion_uv_basis'],0)
    def test_zero_denominator_is_unknown(self):
        d=copy.deepcopy(BASE);d['values']={'ad_spend':0,'ad_attributed_gmv':0}
        self.assertIsNone(calculate_live_metrics(d)['metrics']['ad_gmv_roas'])
    def test_revenue_does_not_imply_profit(self):
        d=copy.deepcopy(BASE);del d['values']['realized_profit']
        self.assertIsNone(calculate_live_metrics(d)['metrics']['profit_roi'])
    def test_no_unconfirmed_mapping(self):
        d=copy.deepcopy(BASE);d['definitions_confirmed']=False
        with self.assertRaises(ValueError):calculate_live_metrics(d)
    def test_bad_numeric_values(self):
        for x in [True,-1,float('nan'),float('inf'),'200',1.5]:
            d=copy.deepcopy(BASE);d['values']['entry_events']=x
            with self.subTest(value=x),self.assertRaises(ValueError):calculate_live_metrics(d)
    def test_inconsistent_denominators(self):
        d=copy.deepcopy(BASE);d['values']['buyer_uv']=151
        with self.assertRaises(ValueError):calculate_live_metrics(d)
    def test_invalid_window(self):
        d=copy.deepcopy(BASE);d['window_end']=d['window_start']
        with self.assertRaises(ValueError):calculate_live_metrics(d)
    def test_naive_window(self):
        d=copy.deepcopy(BASE);d['window_start']='2026-09-14T20:00:00'
        with self.assertRaises(ValueError):calculate_live_metrics(d)
    def test_unknown_fields_not_silently_mapped(self):
        d=copy.deepcopy(BASE);d['values']['ROI']=3
        with self.assertRaises(ValueError):calculate_live_metrics(d)

if __name__=='__main__':unittest.main()
