"""Offline inspection of five bounded public-page captures; no JS execution or network."""
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PRIVATE=ROOT/'private/research/m1-public-followup-20260914'
OUT=Path(__file__).resolve().parent

def frames(text):
    decoder=json.JSONDecoder(); parts=[]
    for match in re.finditer(r'self\.__pace_f\.push\(',text):
        try: value,_=decoder.raw_decode(text[match.end():])
        except ValueError: continue
        if isinstance(value,list) and len(value)>1 and isinstance(value[1],str): parts.append(value[1])
    payload='\n'.join(parts)
    for match in re.finditer(r'(?:^|\n)([0-9a-f]+):',payload):
        try: value,_=decoder.raw_decode(payload[match.end():])
        except ValueError: continue
        yield 'frame:'+match.group(1),value

def walk(value,path):
    if isinstance(value,dict):
        yield path,value
        for key,child in value.items():yield from walk(child,path+'.'+key)
    elif isinstance(value,list):
        for i,child in enumerate(value):yield from walk(child,path+f'[{i}]')

def clean(value):
    return None if value in ('','$undefined','$null','0',0,None) else value

def main():
    records={}; texts={}; pages=[]; conflicts=[]; appearances=0
    for source in json.loads((PRIVATE/'manifest.json').read_text(encoding='utf-8')):
        raw=(ROOT/source['snapshot_path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==source['sha256']
        page=dict(source); page['cards_seen']=0
        for frame,value in frames(raw.decode('utf-8','replace')):
            for path,shipin in walk(value,frame):
                if not path.endswith('.shipin') or not isinstance(shipin.get('mainVideo'),dict):continue
                main=shipin['mainVideo']; info=shipin.get('awemeInfo') or {}
                main_id=str(info.get('awemeId',''))
                assert str(main.get('awemeId',''))==main_id, 'main/details ID mismatch'
                for section in ['mainVideo','relatedRecommend','favorVideoList','latestVideoList','hotRecommendList','favorVideos','latestVideos','hotVideos']:
                    cards=shipin.get(section,[])
                    if isinstance(cards,dict):cards=[cards]
                    if not isinstance(cards,list):continue
                    for i,card in enumerate(cards):
                        if not isinstance(card,dict):continue
                        work_id=str(card.get('awemeId',''))
                        if not re.fullmatch(r'\d+',work_id):continue
                        link=card.get('videoUrl','')
                        if link != 'https://www.douyin.com/video/'+work_id:
                            conflicts.append({'source':source['name'],'work_id':work_id,'reason':'noncanonical card link'});continue
                        is_main=section=='mainVideo';author=(info.get('authorInfo') or {}) if is_main else {}
                        sec=clean(author.get('secUid')) or clean(card.get('secUID'))
                        if not sec:
                            match=re.fullmatch(r'https://www\.douyin\.com/user/([^/?]+)',card.get('userHomgepageUrl',''))
                            if match:sec=match.group(1)
                        asr=card.get('asrText'); asr=asr if isinstance(asr,str) and asr and not asr.startswith('$') else None
                        observation={
                            'source_url':source['source_url'],'source_snapshot_sha256':source['sha256'],
                            'observed_at_utc':source['file_modified_at_utc'],'source_json_path':path+'.'+section+(f'[{i}]' if not is_main else ''),
                            'relationship':'main' if is_main else 'recommendation_or_list',
                            'author_name':author.get('nickname') or card.get('nickname'),
                            'author_sec_uid':sec,'author_uid':clean(author.get('uid')) or clean(card.get('uid')),
                            'identity_basis':'awemeInfo.authorInfo' if is_main else ('card profile link/ID' if sec else 'name_only_unresolved'),
                            'title':card.get('text'), 'published_at_unix':card.get('updateTS'),
                            'duration_ms':card.get('duration'),'likes':card.get('diggCount'),
                            'main_named_stats':info.get('stats') if is_main else None,
                            'views':None,'monetization_verified':False,
                            'platform_asr_reference_unresolved':isinstance(card.get('asrText'),str) and card.get('asrText','').startswith('$') and card.get('asrText')!='$undefined','platform_asr_available':bool(asr),'platform_asr_characters':len(asr) if asr else 0,
                            'platform_asr_sha256':hashlib.sha256(asr.encode('utf-8')).hexdigest() if asr else None,
                        }
                        record=records.setdefault(work_id,{'work_id':work_id,'canonical_url':link,'observations':[],'original_video_viewed':False,'asr_audio_verified':False,'human_or_assistant_text_read':False,'deep_analysis_complete':False})
                        record['observations'].append(observation); appearances+=1;page['cards_seen']+=1
                        if asr:texts.setdefault(work_id,[]).append({'source':source['name'],'source_json_path':observation['source_json_path'],'text':asr,'sha256':observation['platform_asr_sha256']})
        pages.append(page)
    accounts={};unresolved=[]
    for work_id,record in records.items():
        secs={o['author_sec_uid'] for o in record['observations'] if o['author_sec_uid']}
        if len(secs)>1:conflicts.append({'work_id':work_id,'reason':'author identity conflict'});continue
        if not secs:unresolved.append(work_id);continue
        sec=next(iter(secs)); account=accounts.setdefault(sec,{'sec_uid':sec,'observed_names':[],'work_ids':[]})
        account['work_ids'].append(work_id)
        for o in record['observations']:
            if o['author_name'] not in account['observed_names']:account['observed_names'].append(o['author_name'])
    data={'scope':'public_discovery_not_industry_census','pages':pages,'counts':{'pages':len(pages),'card_appearances':appearances,'unique_works':len(records),'stable_identity_accounts':len(accounts),'works_without_stable_author':len(unresolved),'works_with_platform_asr':len(texts),'original_videos_viewed':0,'audio_verified_transcripts':0,'text_read':0,'deep_analyses':0},'conflicts':conflicts,'accounts':list(accounts.values()),'unresolved_author_work_ids':unresolved,'works':list(records.values())}
    note_path=OUT/'reading-notes.json'
    if note_path.exists():
        notes=json.loads(note_path.read_text(encoding='utf-8'))['notes']
        seen=set()
        for note in notes:
            wid=note['work_id']
            assert wid not in seen and wid in records, 'duplicate/missing reviewed work'
            seen.add(wid)
            assert any(o['source_snapshot_sha256']==note['source_snapshot_sha256'] and o['source_json_path']==note['source_json_path'] and o['platform_asr_sha256']==note['platform_asr_sha256'] for o in records[wid]['observations']), 'review source changed'
            records[wid]['human_or_assistant_text_read']=True
        data['counts']['text_read']=len(seen)
    (OUT/'discovery-index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (PRIVATE/'asr-by-work.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data['counts'],ensure_ascii=False));print('conflicts',conflicts)
    for work_id,r in records.items():
        o=r['observations'][0];print(work_id,o['author_name'],'likes='+str(o['likes']),'asr='+str(o['platform_asr_characters']),o['title'][:95])
if __name__=='__main__':main()
