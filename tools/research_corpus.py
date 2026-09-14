"""Merge reviewed public research batches offline. No crawler or automatic judgment.

Retains discovery vs reading counts and individually attributed observations.
Default output is private; publishing remains a separate reviewed action.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from consultant_case import ROOT, load, project_file, sha, validate_public_input


def compile_batches(batch_dirs, root=ROOT):
    root=Path(root).resolve()
    merged={}; reviewed={}; inputs=[]; conflicts=[]; pages=set(); contributing_pages=set()
    if not batch_dirs or len(set(batch_dirs))!=len(batch_dirs):
        raise ValueError('Nonempty, distinct batch paths required')
    for batch in batch_dirs:
        index_path=project_file(root,batch+'/discovery-index.json')
        notes_path=project_file(root,batch+'/reading-notes.json')
        index=load(index_path);notes=load(notes_path)['notes']
        pages.update(p['source_url'] for p in index['pages'])
        inputs.append({'batch':batch,'index_sha256':sha(index_path),'notes_sha256':sha(notes_path)})
        local={}
        for w in index['works']:
            wid=w['work_id']
            if wid in local or not re.fullmatch(r'\d+',wid):raise ValueError('Invalid/duplicate work ID')
            if w['canonical_url']!='https://www.douyin.com/video/'+wid:raise ValueError('Canonical URL mismatch')
            if w.get('original_video_viewed') or w.get('asr_audio_verified') or w.get('deep_analysis_complete'):
                raise ValueError('This importer only accepts metadata/platform-text batches')
            if not w.get('observations'):raise ValueError('Missing work observations')
            local[wid]=w
            target=merged.setdefault(wid,{'canonical_url':w['canonical_url'],'observations':[]})
            for o in w['observations']:
                for k in ['source_url','source_snapshot_sha256','source_json_path','author_sec_uid']:
                    if not o.get(k):raise ValueError('Missing observation field: '+k)
                if o.get('relationship') not in ['main','recommendation_or_list']:raise ValueError('Unverified attribution boundary')
                observed={**o,'batch':batch}
                if observed not in target['observations']:target['observations'].append(observed)
                contributing_pages.add(o['source_url'])
        seen=set()
        for n in notes:
            wid=n['work_id']
            if wid in seen or wid not in local:raise ValueError('Duplicate or missing reviewed work')
            seen.add(wid)
            if not n.get('platform_asr_sha256'):raise ValueError('Read note requires text fingerprint')
            if not any(o.get('platform_asr_available') is True and all(o.get(k)==n.get(k) for k in ['source_url','source_snapshot_sha256','source_json_path','platform_asr_sha256']) for o in local[wid]['observations']):
                raise ValueError('Read note source changed: '+wid)
            reviewed.setdefault(wid,[]).append({**n,'batch':batch})
        if index['counts']['unique_works']!=len(local) or index['counts']['text_read']!=len(seen):
            raise ValueError('Batch counts do not match records/notes')
        for wid,w in local.items():
            if w.get('human_or_assistant_text_read') is not (wid in seen):raise ValueError('Read flag without matching note')
        conflicts.extend({'batch':batch,**c} for c in index.get('conflicts',[]))
    accounts={};works=[]
    for wid,w in sorted(merged.items()):
        observations=w['observations'];ids={o['author_sec_uid'] for o in observations}
        if len(ids)!=1:raise ValueError('Conflicting author identities: '+wid)
        sec=next(iter(ids));key='douyin-sec:'+sec
        a=accounts.setdefault(key,{'uid':key,'sec_uid':sec,'identity_kind':'public_sec_uid_not_numeric_uid','observed_names':[],'work_ids':[],'reviewed_work_ids':[],'monetization_verified':False,'industry_tier':None})
        a['work_ids'].append(wid)
        if wid in reviewed:a['reviewed_work_ids'].append(wid)
        for o in observations:
            if o.get('author_name') and o['author_name'] not in a['observed_names']:a['observed_names'].append(o['author_name'])
        o=observations[0]
        works.append({'work_id':wid,'author_uid':key,'original_url':w['canonical_url'],
                      'source_url':o['source_url'],'source_sha256':o['source_snapshot_sha256'],'source_json_path':o['source_json_path'],
                      'title':o.get('title'),'metrics':{'likes':o.get('likes'),'views':None},
                      'metrics_observation_policy':'first retained snapshot for display only; all dated observations retained; not a common-window comparison',
                      'observations':observations,'reading_notes':reviewed.get(wid,[]),
                      'material':{'main_vs_recommendation_verified':True,'original_video_viewed':False,'verified_transcript':False,'platform_text_read':wid in reviewed,'platform_asr_available':any(x.get('platform_asr_available') for x in observations)},
                      'viral_classification':None,'commercial_outcome_verified':False})
    coverage={'observed_page_count':len(pages),'pages_with_attributed_works':len(contributing_pages),'observed_account_count':len(accounts),'observed_work_count':len(works),
              'platform_asr_available':sum(w['material']['platform_asr_available'] for w in works),
              'platform_text_read':len(reviewed),'accounts_with_text_read':sum(bool(a['reviewed_work_ids']) for a in accounts.values()),
              'original_videos_viewed':0,'verified_transcripts':0,'full_video_deep_analyses':0,'industry_sufficiency':False}
    result={'data_kind':'real_public_metadata','schema_version':'1.0','scope':'discovery_pool_including_adjacent_and_unread_not_qualified_competitor_census',
            'fingerprint_policy':'sha256-utf8-sig-lf-v1 for project files; raw sha256 for web snapshots',
            'input_batches':inputs,'source_conflicts':conflicts,'coverage':coverage,
            'accounts':[accounts[k] for k in sorted(accounts)],'works':works}
    validate_public_input(result)
    return result


def search_notes(data,query):
    """Literal metadata/note search, not a semantic quality or viral classifier."""
    rows=[]
    for w in data['works']:
        haystack=json.dumps({'title':w['title'],'notes':w['reading_notes']},ensure_ascii=False).casefold()
        if query.casefold() in haystack:
            rows.append({'work_id':w['work_id'],'original_url':w['original_url'],'platform_text_read':w['material']['platform_text_read'],
                         'notes':w['reading_notes'],'likes_snapshot':w['metrics']['likes']})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',action='append',required=True,help='Project-relative reviewed batch directory')
    p.add_argument('--output',default='private/workbench/research-corpus.json')
    p.add_argument('--query',help='Print matching titles/notes instead of writing a corpus')
    args=p.parse_args()
    try:
        data=compile_batches(args.batch)
        if args.query is not None:
            print(json.dumps(search_notes(data,args.query),ensure_ascii=False,indent=2));return 0
        output=(ROOT/args.output).resolve()
        if not output.is_relative_to(ROOT.resolve()):raise ValueError('Output must remain in project')
        if output.exists() or output.is_symlink():raise ValueError('Refuse to overwrite existing output')
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
        print(json.dumps(data['coverage'],ensure_ascii=False));return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('Research merge failed: '+str(exc));return 2

if __name__=='__main__':raise SystemExit(main())
