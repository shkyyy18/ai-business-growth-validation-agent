"""Offline fixture-only mapping experiment. No networking, downloading, or SDK imports.
Not a production adapter: only the pinned upstream fixture schema is supported.
"""
import copy
import json
from pathlib import Path

METRICS = {"digg_count": "likes", "comment_count": "comments",
           "collect_count": "saves", "share_count": "shares"}

def count(value):
    return value if type(value) is int and value >= 0 else None

def map_fixture(payload, *, source, expected_author=None, requested_cursor=0):
    result = {"evidence_type": "synthetic_fixture_only", "industry_sample": False,
              "source": source, "accounts": [], "works": [], "issues": [],
              "pagination": {}, "content_read_count": 0, "deep_analysis_count": 0}
    def issue(reason, work_id=None):
        result["issues"].append({"reason": reason, "work_id": work_id})
    if type(payload) is not dict or type(payload.get("status_code")) is not int or payload["status_code"] != 0:
        issue("upstream_error_or_unknown_status")
        return result
    if "aweme_list" in payload:
        entries = payload["aweme_list"]
        if not isinstance(entries, list):
            issue("malformed_list")
            return result
        more, cursor = payload.get("has_more"), payload.get("max_cursor")
        result["pagination"] = {"has_more_raw": more, "next_cursor_raw": cursor,
                                "total_raw": payload.get("total"),
                                "complete_account_verified": False}
        if more == 1 and (cursor is None or cursor == requested_cursor):
            issue("cursor_not_advancing")
        if more not in (0, 1):
            issue("unknown_has_more")
        if more == 1 and not entries:
            issue("empty_page_with_more")
    elif isinstance(payload.get("aweme_detail"), dict):
        entries = [payload["aweme_detail"]]
    else:
        issue("missing_supported_payload")
        return result
    seen, accounts = {}, {}
    for item in entries:
        if not isinstance(item, dict):
            issue("malformed_work")
            continue
        wid = item.get("aweme_id")
        author = item.get("author")
        if not isinstance(wid, str) or not wid:
            issue("missing_work_id")
            continue
        if not isinstance(author, dict) or not isinstance(author.get("sec_uid"), str) or not author["sec_uid"]:
            issue("missing_author_id", wid)
            continue
        aid = author["sec_uid"]
        if expected_author is not None and aid != expected_author:
            issue("author_mismatch", wid)
            continue
        status = item.get("status")
        if not isinstance(status, dict):
            issue("visibility_unknown", wid)
            continue
        if status.get("aweme_id") not in (None, wid):
            issue("status_id_mismatch", wid)
            continue
        if status.get("is_delete") is not False or status.get("is_prohibited") is not False or status.get("private_status") != 0:
            issue("restricted_deleted_or_unknown_visibility", wid)
            continue
        if status.get("in_reviewing") is True:
            issue("under_review", wid)
            continue
        stats = item.get("statistics")
        if stats is None:
            stats = {}
        if not isinstance(stats, dict):
            issue("malformed_statistics", wid)
            continue
        if stats.get("aweme_id") not in (None, wid):
            issue("statistics_id_mismatch", wid)
            continue
        if wid in seen:
            if seen[wid] == item:
                issue("duplicate_work", wid)
            else:
                issue("conflicting_duplicate_quarantined", wid)
                result["works"] = [w for w in result["works"] if w["work_id"] != wid]
            continue
        seen[wid] = copy.deepcopy(item)
        account = {"account_id": aid, "uid_raw": author.get("uid"),
                   "name": author.get("nickname"),
                   "followers_raw": count(author.get("follower_count")),
                   "account_total_likes_raw": count(author.get("total_favorited")),
                   "fixture_only": True, "baseline": None, "monetization": None}
        if aid in accounts and accounts[aid] != account:
            issue("account_snapshot_conflict", wid)
        else:
            accounts[aid] = account
        metrics = {}
        for raw_field, label in METRICS.items():
            raw = stats.get(raw_field)
            metrics[label] = {"raw_field": "statistics." + raw_field, "raw_value": raw,
                              "value": count(raw), "real_world_verified": False}
            if raw is not None and count(raw) is None:
                issue("invalid_metric:" + raw_field, wid)
        # Zero play_count may be a placeholder: retain it without using a denominator.
        metrics["plays"] = {"raw_field": "statistics.play_count",
                            "raw_value": stats.get("play_count"), "value": None,
                            "reason": "meaning_and_paid_traffic_scope_unverified"}
        result["works"].append({"work_id": wid, "account_id": aid,
            "source": source, "fixture_only": True,
            "original_url_raw": item.get("share_url"), "link_verified": False,
            "published_epoch_raw": item.get("create_time"),
            "platform_capture_time": None, "post_type_raw": item.get("aweme_type"),
            "description": item.get("desc"), "description_is_transcript": False,
            "metrics": metrics, "transcript": None, "video_viewed": False,
            "viral_label": None, "monetization": None})
    valid_aids = {w["account_id"] for w in result["works"]}
    result["accounts"] = [a for aid, a in accounts.items() if aid in valid_aids]
    return result

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    source = "fixtures/user_posts_page1.json"
    payload = json.loads((root / source).read_text(encoding="utf-8"))
    output = map_fixture(payload, source=source,
        expected_author="MS4wLjABAAAA_SYNTHETIC_DOUYIN_AUTHOR_0001")
    (root / "mapped-fixture.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fixture_accounts": len(output["accounts"]),
                      "fixture_works": len(output["works"]),
                      "industry_samples": 0, "content_read": 0}))
