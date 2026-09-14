"""Evidence-first, offline case handoff. Not an autonomous advisor or a market validator.

Source checks prove file integrity, not the truth of human assertions. No network calls.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = [
    ("N0", "状态与上下文", {"context"}),
    ("N1", "资料与来源", {"public_input"}),
    ("N2", "能力盘点", {"founder_experience"}),
    ("N3", "客户与问题", {"client_problem"}),
    ("N4", "商业画布", {"hypothesis_canvas"}),
    ("N5", "假设与优先级", {"selected_task"}),
    ("N6", "访谈验证", {"client_interview"}),
    ("N7", "最小实验", {"experiment_agreement", "client_baseline"}),
    ("N8", "交付与采用", {"delivery", "client_acceptance"}),
    ("N9", "结果与成本", {"execution_result", "cost_record", "payment_outcome"}),
    ("N10", "结果复盘", {"result_review"}),
    ("N11", "复制与产品化判断", {"repeatability_review"}),
]
CLIENT_KINDS = {"client_problem", "client_interview", "experiment_agreement", "client_baseline", "client_acceptance", "execution_result", "payment_outcome"}
KINDS = {k for _, _, ks in NODES for k in ks} | {"candidate_problem", "research_probe", "access_review"}

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha(path):
    text=Path(path).read_bytes().decode("utf-8-sig").replace("\r\n","\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def project_file(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("Source must be a project-relative path")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Source missing or outside project: " + name)
    return path

def verify_case(case, root):
    if not isinstance(case,dict):raise ValueError("Case must be an object")
    if case.get("schema_version") != "1.0" or case.get("mode") != "real_partial_input":
        raise ValueError("Expected schema 1.0, mode real_partial_input")
    if case.get("fingerprint_policy") != "sha256-utf8-sig-lf-v1":raise ValueError("Explicit text fingerprint policy required")
    if not case.get("case_id") or not isinstance(case.get("evidence"), list):
        raise ValueError("Case ID and evidence list required")
    ids=set(); checked=[]
    for e in case["evidence"]:
        if not isinstance(e, dict) or not e.get("id") or e["id"] in ids:
            raise ValueError("Missing/duplicate evidence ID")
        ids.add(e["id"])
        if e.get("kind") not in KINDS or e.get("synthetic") is not False:
            raise ValueError("Unknown kind or synthetic/unspecified evidence")
        if e.get("kind") in CLIENT_KINDS and e.get("subject") != "client":
            raise ValueError("Public research subjects/founder history are not client evidence")
        if e.get("review_status") != "source_checked" or not e.get("assertion"):
            raise ValueError("Evidence requires a checked source and bounded assertion")
        source=project_file(root,e.get("path"))
        actual=sha(source)
        if actual != e.get("sha256"):
            raise ValueError("Source digest changed: " + e["path"])
        checked.append({"id":e["id"],"kind":e["kind"],"subject":e.get("subject"),"path":e["path"],"sha256":actual,"assertion":e["assertion"]})
    main=case.get("public_input",{})
    path=project_file(root,main.get("path"))
    if sha(path)!=main.get("sha256"):
        raise ValueError("Public input digest changed")
    data=load(path)
    validate_public_input(data)
    for key in ["canvas", "node_notes", "module_handoffs"]:
        if not isinstance(case.get(key),dict):raise ValueError("Missing mapping: "+key)
    for node,_,_ in NODES:
        if not isinstance(case["node_notes"].get(node),str) or not case["node_notes"][node]:
            raise ValueError("Missing grounded node note: "+node)
    return data,checked

def validate_public_input(data):
    if not isinstance(data,dict):raise ValueError("Public input must be an object")
    if data.get("data_kind")!="real_public_metadata":raise ValueError("Expected real public metadata")
    accounts=data.get("accounts"); works=data.get("works")
    if not isinstance(accounts,list) or not isinstance(works,list):raise ValueError("Accounts/works must be lists")
    by_id={}
    for a in accounts:
        if not isinstance(a,dict):raise ValueError("Account must be an object")
        uid=a.get("uid")
        if not isinstance(uid,str) or not uid or uid in by_id:raise ValueError("Missing/duplicate author UID")
        by_id[uid]=a
    seen=set()
    for w in works:
        if not isinstance(w,dict):raise ValueError("Work must be an object")
        wid=w.get("work_id")
        if not isinstance(wid,str) or not wid or wid in seen:raise ValueError("Missing/duplicate work ID")
        seen.add(wid)
        if w.get("author_uid") not in by_id:raise ValueError("Unknown author UID")
        if w.get("original_url") != "https://www.douyin.com/video/"+wid:
            raise ValueError("Original link/work ID mismatch")
        if not w.get("source_url") or not w.get("source_json_path") or not w.get("source_sha256"):
            raise ValueError("Missing source provenance")
        for field,value in w.get("metrics",{}).items():
            if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0):
                raise ValueError("Invalid metric: "+field)
        material=w.get("material",{})
        if material.get("main_vs_recommendation_verified") is not True:
            raise ValueError("Main/recommendation boundary unverified")
        if w.get("viral_classification") is not None:
            raise ValueError("This partial-input runner does not establish viral benchmarks")
    coverage=data.get("coverage",{})
    if coverage.get("observed_account_count")!=len(accounts) or coverage.get("observed_work_count")!=len(works):
        raise ValueError("Coverage count mismatch")
    for key,flag in [("original_videos_viewed","original_video_viewed"),("verified_transcripts","verified_transcript")]:
        actual=sum(w.get("material",{}).get(flag) is True for w in works)
        if coverage.get(key)!=actual:raise ValueError("Reading count mismatch: "+key)
    # Optional merged-corpus counts must remain consistent with material flags.
    for key,flag in [("platform_text_read","platform_text_read"),("platform_asr_available","platform_asr_available")]:
        if key in coverage and coverage[key] != sum(w.get("material",{}).get(flag) is True for w in works):
            raise ValueError("Reading count mismatch: " + key)
    if "accounts_with_text_read" in coverage:
        read_authors={w["author_uid"] for w in works if w.get("material",{}).get("platform_text_read") is True}
        if coverage["accounts_with_text_read"]!=len(read_authors):raise ValueError("Read-account count mismatch")
    if coverage.get("industry_sufficiency") is not False:
        raise ValueError("Partial-input source test cannot assert industry sufficiency")

def assess(case,data,checked):
    kinds={e["kind"] for e in checked}
    nodes=[]
    for node,name,required in NODES:
        missing=sorted(required-kinds)
        present=[e["id"] for e in checked if e["kind"] in required]
        nodes.append({"id":node,"name":name,"record_status":"evidence_present" if not missing else "needs_evidence","evidence_ids":present,"missing_evidence_kinds":missing,"note":case["node_notes"][node]})
    # Scope is a partial public-input test. Even a full set of labeled files is not market validation.
    return {"case_id":case["case_id"],"run_kind":"offline_source_integrity_and_handoff", "network_calls":0,"source_integrity":"passed", "industry_research_complete":False,"customer_delivery_validated":False,"commercial_loop_validated":False,"nodes":nodes,"counts":data["coverage"],"evidence":checked,"limitations":["A hash proves file identity, not source truth or client authorization.","Node evidence presence is not node/business completion.","No continuous feed, original-media review or transactions were established by this run."]}

def render_review(case,data,audit):
    lines=["# 商业顾问端到端检查："+case["case_id"],"","**本次运行：真实部分输入的来源核验与节点交接，不是客户业务闭环跑通。**","","## 实际材料",f"- {len(data['accounts'])}个公开研究账号、{len(data['works'])}条公开发现作品（主作品与推荐项分别核验）。不是我们的客户，也不是行业充分样本。","- 本命令离线运行，不采集、不调用模型、不生成原视频观察、成交或客户回答。","","## N0—N11交接","| 节点 | 文件证据 | 当前判断与下一动作 |","|---|---|---|"]
    for n in audit['nodes']:
        state="有对应来源（不等于业务验收）" if not n['missing_evidence_kinds'] else "待补："+", ".join(n['missing_evidence_kinds'])
        note=n['note'].replace('|','／').replace('\n',' ')
        lines.append(f"| {n['id']} {n['name']} | {state} | {note} |")
    lines += ["","## 当前画布：工作假设，不是客户已确认需求","| 要素 | 内容 |","|---|---|"]
    for k,v in case['canvas'].items():lines.append('| '+k+' | '+str(v).replace('|','／').replace('\n',' ')+' |')
    lines += ["","## M1—M5本次交接"]
    for k,v in case['module_handoffs'].items():lines += ['','### '+k,str(v)]
    lines += ["","## 继续/调整/停止判断",case['decision'],"","## 来源与边界"]
    for e in audit['evidence']:lines.append(f"- {e['id']} / {e['kind']}：`{e['path']}`。{e['assertion']}")
    lines += ['','不能因为命令成功、文件齐全或测试通过认定研究/交付/付费已验证。完整工时和模型费用未知，不能推导利润或效率提升比例。','']
    return '\n'.join(lines)

def run_case(case_path,output,root=ROOT,force=False):
    root=Path(root).resolve();case_path=Path(case_path).resolve();output=Path(output).resolve()
    if not case_path.is_relative_to(root) or not output.is_relative_to(root):
        raise ValueError("Case and output must stay inside the project")
    case=load(case_path);data,checked=verify_case(case,root);audit=assess(case,data,checked)
    artifacts={"input-audit.json":audit,"account-cards.json":data['accounts'],"content-library.json":data['works'],"handoff.json":{"case_id":case['case_id'],"decision":case['decision'],"module_handoffs":case['module_handoffs'],"missing":[{"node":n['id'],"kinds":n['missing_evidence_kinds']} for n in audit['nodes'] if n['missing_evidence_kinds']]}}
    names=list(artifacts)+['review.md']
    if output.exists() and not output.is_dir():raise ValueError("Output is not a directory")
    for name in names:
        target=output/name
        if target.is_symlink():raise ValueError("Refuse symlink output")
        if target.exists() and not force:raise ValueError("Output exists; use --force only after review")
        if target.exists() and not target.is_file():raise ValueError("Output target is not a file")
    # Validate everything before making output changes. No formal business files are modified.
    output.mkdir(parents=True,exist_ok=True)
    for name,obj in artifacts.items():(output/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (output/'review.md').write_text(render_review(case,data,audit),encoding='utf-8')
    return audit

def cmd_run_case(args):
    try:
        audit=run_case(args.case,args.output,force=args.force)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print('Case check failed: '+str(exc));return 2
    print('Source integrity: passed; N0-N11 handoff written.')
    print('Industry/customer/commercial validation: NOT COMPLETE.')
    print('Missing-evidence nodes: '+', '.join(n['id'] for n in audit['nodes'] if n['missing_evidence_kinds']))
    return 0

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('case');p.add_argument('--output',default=str(ROOT/'private/workbench/latest-case'));p.add_argument('--force',action='store_true')
    raise SystemExit(cmd_run_case(p.parse_args()))
