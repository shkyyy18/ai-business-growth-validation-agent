"""Bounded public HTML inspection; inert JSON only, no login/JS/media requests."""
import datetime, hashlib, html, json, re, urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parent
URLS=['https://www.douyin.com/shipin/7314025932749146164','https://www.douyin.com/shipin/7644393111137011758']
def walk(x,p='$'):
    if isinstance(x,dict):
        yield p,x
        for k,v in x.items():yield from walk(v,p+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,p+'['+str(i)+']')
def inspect(url):
    record={'source_url':url,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authentication_sent':False,'original_video_viewed':False}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:
            raw=response.read(2500001);record.update(http_status=response.status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),truncated=len(raw)>2500000)
        if record['truncated']:return record
        s=raw.decode('utf-8','replace'); decoder=json.JSONDecoder(); fragments=[]
        for match in re.finditer(r'self\.__pace_f\.push\(',s):
            try:
                v,end=decoder.raw_decode(s[match.end():])
                if isinstance(v,list) and len(v)>1 and isinstance(v[1],str):fragments.append(v[1])
            except ValueError:pass
        candidates=[]
        # Inspect frame starts in captured fragments; this is a bounded diagnostic, not a full RSC protocol decoder.
        payload='\n'.join(fragments)
        for match in re.finditer(r'(?:^|\n)([0-9a-f]+):',payload):
            try:frame,end=decoder.raw_decode(payload[match.end():])
            except ValueError:continue
            for path,obj in walk(frame,'frame:'+match.group(1)):
                if 'authorInfo' in obj and 'desc' in obj:
                    author=obj.get('authorInfo') or {}
                    selected={k:obj[k] for k in ['awemeId','awemeType','desc','itemTitle','createTime','duration','statistics','stats','statsInfo','video'] if k in obj}
                    selected['author']={k:author[k] for k in ['uid','secUid','nickname','followerCount','totalFavorited','signature'] if k in author}
                    selected.pop('video',None)
                    selected['source_json_path']=path
                    # Never persist authentication tokens, media URLs or unrelated app state.
                    selected['text_fields']={k:v for k,v in obj.items() if any(t in k.lower() for t in ['transcript','subtitle']) and isinstance(v,(str,int,float))}

                    if path.endswith('.awemeInfo'):candidates.append(selected)
                if path.endswith('.mainVideo') and 'videoUrl' in obj and 'nickname' in obj:
                    candidates.append({'source_json_path':path,'link_card':{k:obj[k] for k in ['text','nickname','videoUrl','duration','updateTS','diggCount'] if k in obj}})
        record['candidates']=candidates
        # Text only from visible HTML, not arbitrary escaped scripts.
        text=html.unescape(re.sub('<[^>]+>',' ',re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',s,flags=re.S)))
        text=re.sub(r'\s+',' ',text)
        # Bounded preview for boundary verification, not a corpus transcript.
        record['visible_text_length']=len(text)  # no third-party transcript export
        record['frame_count']=len(fragments)
    except Exception as exc:record['error']=type(exc).__name__+': '+str(exc)
    return record
if __name__=='__main__':
    records=[inspect(url) for url in URLS]
    (OUT/'structured-public-probes.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in records:
        print(r['source_url'],r.get('http_status'),r.get('error',''))
        for c in r.get('candidates',[]):print(json.dumps(c,ensure_ascii=False)[:8500])
