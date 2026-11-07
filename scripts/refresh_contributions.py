"""Update public merged-PR evidence; authentication stays in the environment."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import urllib.parse
import urllib.request

root=Path(__file__).resolve().parents[1]
query='is:pr author:ninglinLiu is:merged -user:ninglinLiu'
headers={'Accept':'application/vnd.github+json','User-Agent':'ninglinLiu-profile','X-GitHub-Api-Version':'2022-11-28'}
if os.environ.get('GITHUB_TOKEN'):headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
rows=[]
for page in range(1,11):
    url='https://api.github.com/search/issues?'+urllib.parse.urlencode({'q':query,'per_page':100,'page':page,'sort':'created','order':'asc'})
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as response:payload=json.load(response)
    if payload.get('incomplete_results') or payload['total_count']>1000:
        raise RuntimeError('Search is incomplete. Keep the previous snapshot; partition the query before updating.')
    for item in payload['items']:
        merged=item.get('pull_request',{}).get('merged_at')
        if not merged:raise RuntimeError('Expected a merged PR.')
        rows.append({'repository':item['repository_url'].split('/repos/')[1],'number':item['number'],'title':item['title'],'url':item['html_url'],'merged_at':merged})
    if len(rows)>=payload['total_count']:break
if len({p['url'] for p in rows})!=payload['total_count']:raise RuntimeError('Incomplete or duplicate search results.')
rows.sort(key=lambda p:(p['merged_at'],p['url']),reverse=True)
snapshot={'updated_at':datetime.now(ZoneInfo('Asia/Taipei')).date().isoformat(),'query':query,'contributions':rows}
(root/'data/contributions.json').write_text(json.dumps(snapshot,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'Refreshed {len(rows)} merged upstream PRs.')
