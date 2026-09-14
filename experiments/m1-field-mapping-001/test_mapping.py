"""Behavioral checks of our fixture mapper, not the upstream collector."""
import copy
import json
from pathlib import Path
import unittest
from map_fixture import map_fixture

ROOT = Path(__file__).resolve().parent
BASE = json.loads((ROOT / "fixtures/user_posts_page1.json").read_text(encoding="utf-8"))
AUTHOR = BASE["aweme_list"][0]["author"]["sec_uid"]

def run(data, **kwargs):
    return map_fixture(data, source="synthetic_unit_test", expected_author=AUTHOR, **kwargs)

class MappingChecks(unittest.TestCase):
    def test_valid_ids_and_metrics(self):
        out = run(BASE)
        self.assertEqual(len(out["accounts"]), 1)
        self.assertEqual(len(out["works"]), 2)
        self.assertTrue(all(w["account_id"] == AUTHOR for w in out["works"]))
        self.assertEqual(out["works"][0]["metrics"]["likes"]["value"], 98230)
        self.assertEqual(out["works"][0]["metrics"]["saves"]["value"], 5121)
    def test_zero_plays_not_a_denominator(self):
        metric = run(BASE)["works"][0]["metrics"]["plays"]
        self.assertEqual(metric["raw_value"], 0)
        self.assertIsNone(metric["value"])
    def test_unknown_metric_not_zero(self):
        data = copy.deepcopy(BASE)
        del data["aweme_list"][0]["statistics"]["collect_count"]
        self.assertIsNone(run(data)["works"][0]["metrics"]["saves"]["value"])
    def test_invalid_metric_not_coerced(self):
        for value in [-1, True, "1.2万"]:
            with self.subTest(value=value):
                data = copy.deepcopy(BASE)
                data["aweme_list"][0]["statistics"]["digg_count"] = value
                self.assertIsNone(run(data)["works"][0]["metrics"]["likes"]["value"])
    def test_description_is_not_reading(self):
        out = run(BASE)
        self.assertEqual(out["content_read_count"], 0)
        self.assertFalse(out["industry_sample"])
        for w in out["works"]:
            self.assertFalse(w["video_viewed"])
            self.assertIsNone(w["transcript"])
            self.assertIsNone(w["viral_label"])
            self.assertIsNone(w["monetization"])
    def test_recommendation_wrong_author_rejected(self):
        data = copy.deepcopy(BASE)
        data["aweme_list"][0]["author"]["sec_uid"] = "other_author"
        out = run(data)
        self.assertEqual(len(out["works"]), 1)
        self.assertIn("author_mismatch", [i["reason"] for i in out["issues"]])
    def test_statistics_wrong_id_rejected(self):
        data = copy.deepcopy(BASE)
        data["aweme_list"][0]["statistics"]["aweme_id"] = "other_work"
        self.assertEqual(len(run(data)["works"]), 1)
    def test_duplicate_not_double_counted(self):
        data = copy.deepcopy(BASE)
        data["aweme_list"].append(copy.deepcopy(data["aweme_list"][0]))
        self.assertEqual(len(run(data)["works"]), 2)
    def test_conflicting_duplicate_not_silently_overwritten(self):
        data = copy.deepcopy(BASE)
        item = copy.deepcopy(data["aweme_list"][0])
        item["statistics"]["digg_count"] = 999
        data["aweme_list"].append(item)
        out = run(data)
        self.assertEqual(len(out["works"]), 1)
        self.assertNotEqual(out["works"][0]["work_id"], item["aweme_id"])
    def test_cursor_stall_is_not_saturation(self):
        out = run(BASE, requested_cursor=BASE["max_cursor"])
        self.assertIn("cursor_not_advancing", [i["reason"] for i in out["issues"]])
        self.assertFalse(out["pagination"]["complete_account_verified"])
    def test_restricted_and_error_fixtures_excluded(self):
        for name in ["risk_control_captcha.json", "video_private.json", "video_deleted.json"]:
            with self.subTest(fixture=name):
                data = json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))
                out = run(data)
                self.assertEqual(out["works"], [])
                self.assertTrue(out["issues"])
    def test_unknown_shapes_rejected(self):
        for data in [None, {}, {"status_code": False}, {"status_code": 0, "aweme_list": {}}]:
            with self.subTest(data=data):
                self.assertEqual(run(data)["works"], [])
    def test_account_id_survives_name_change(self):
        data = copy.deepcopy(BASE)
        for item in data["aweme_list"]:
            item["author"]["nickname"] = "renamed"
        self.assertEqual(run(data)["accounts"][0]["account_id"], run(BASE)["accounts"][0]["account_id"])
    def test_missing_id_excluded(self):
        data = copy.deepcopy(BASE)
        del data["aweme_list"][0]["aweme_id"]
        self.assertEqual(len(run(data)["works"]), 1)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MappingChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT / "test-result.json").write_text(json.dumps({
        "test_cases_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "successful": result.wasSuccessful(),
        "scope": "our offline mapper only; not live API or industry validation"
    }, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() else 1)
