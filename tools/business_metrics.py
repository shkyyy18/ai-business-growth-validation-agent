"""Offline arithmetic for explicitly aligned live-session exports.

These are our declared formulas, not claims about Douyin's dashboard definitions.
Missing data stays unknown; sales revenue is never treated as profit.
"""
from __future__ import annotations
import math
from datetime import datetime

FIELDS = {
    "impression_events", "entry_events", "view_sessions", "viewer_uv", "buyer_uv",
    "watch_seconds_sum", "gmv", "ad_attributed_gmv", "ad_spend",
    "realized_profit", "total_cost",
}
COUNT_FIELDS={"impression_events","entry_events","view_sessions","viewer_uv","buyer_uv"}
FORMULAS = {
    "entry_rate_event_basis": ("entry_events", "impression_events", 1),
    "buyer_conversion_uv_basis": ("buyer_uv", "viewer_uv", 1),
    "mean_watch_seconds_per_session": ("watch_seconds_sum", "view_sessions", 1),
    "gmv_per_1000_view_sessions": ("gmv", "view_sessions", 1000),
    "ad_gmv_roas": ("ad_attributed_gmv", "ad_spend", 1),
    "profit_roi": ("realized_profit", "total_cost", 1),
}

def calculate_live_metrics(record):
    """Require caller confirmation of one aligned window/currency/counting convention.

    Returns {metrics, missing, formulas, caveats}; does not aggregate sessions or
    estimate instantaneous inflow, causal impact, retention or platform benchmarks.
    """
    if not isinstance(record,dict):raise ValueError("Record must be an object")
    if record.get("definitions_confirmed") is not True:
        raise ValueError("Confirm window, attribution and event/UV definitions first")
    if not record.get("source_ref") or not record.get("currency"):
        raise ValueError("Source reference and currency are required")
    try:
        start=datetime.fromisoformat(record["window_start"])
        end=datetime.fromisoformat(record["window_end"])
    except (KeyError,TypeError,ValueError) as exc:
        raise ValueError("Explicit ISO observation window required") from exc
    if start.tzinfo is None or end.tzinfo is None or end<=start:
        raise ValueError("Observation window must have timezone and positive duration")
    values=record.get("values",{})
    if not isinstance(values,dict) or set(values)-FIELDS:
        raise ValueError("Unsupported field; do not silently guess dashboard mappings")
    for key,value in values.items():
        if value is None:continue
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError("Invalid numeric field: "+key)
        if value<0 and key!="realized_profit":raise ValueError("Negative field: "+key)
        if key in COUNT_FIELDS and value!=int(value):raise ValueError("Count must be integer: "+key)
    for small,big in [("entry_events","impression_events"),("buyer_uv","viewer_uv"),("viewer_uv","view_sessions"),("ad_attributed_gmv","gmv")]:
        if values.get(small) is not None and values.get(big) is not None and values[small]>values[big]:
            raise ValueError("Inconsistent same-window definitions: "+small+" > "+big)
    metrics={};missing={};formulas={}
    for name,(num,den,scale) in FORMULAS.items():
        n=values.get(num);d=values.get(den)
        formulas[name]=f"{num} / {den} * {scale}"
        if n is None or d is None:
            metrics[name]=None;missing[name]="missing numerator or denominator"
        elif d==0:
            metrics[name]=None;missing[name]="zero denominator; undefined, not zero"
        else:metrics[name]=n/d*scale
    minutes=(end-start).total_seconds()/60
    entries=values.get("entry_events")
    metrics["mean_entries_per_minute"]=None if entries is None else entries/minutes
    if entries is None:missing["mean_entries_per_minute"]="missing entry events"
    formulas["mean_entries_per_minute"]="entry_events / observation-window minutes"
    return {"metrics":metrics,"missing":missing,"formulas":formulas,"currency":record['currency'],"source_ref":record['source_ref'],"caveats":["Formula inputs are caller-mapped, not verified platform exports.","Average entry rate is not a real-time inflow curve.","GMV ROAS is not profit ROI; no sales or profits are inferred.","No comparisons, benchmarks, attribution conclusions or automatic sales decisions."]}


def cmd_live_metrics(args):
    import json
    from pathlib import Path
    try:
        record=json.loads(Path(args.source).read_text(encoding='utf-8-sig'))
        result=calculate_live_metrics(record)
        text=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
        if args.output:
            target=Path(args.output).resolve()
            if target.exists():raise ValueError('Refuse to overwrite existing output')
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x',encoding='utf-8') as handle:handle.write(text)
            print('Metrics saved; formulas do not establish business results.')
        else:print(text)
        return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print('Metric check failed: '+str(exc));return 2
