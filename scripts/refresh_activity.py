"""Fetch public profile activity and language bytes; keep tokens out of artifacts."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from collections import Counter
import json
import os
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'ninglinLiu'
HEADERS = {'User-Agent': USER + '-profile', 'Accept': 'application/vnd.github+json'}

def request(url, payload=None, authenticated=False):
    headers = dict(HEADERS)
    if authenticated and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    body = json.dumps(payload).encode() if payload else None
    if body: headers['Content-Type'] = 'application/json'
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=60) as response:
        return response.read().decode('utf-8')

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tips = {}
        self.current = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and a.get('data-date'):
            self.cells[a['id']] = {'date': a['data-date'], 'level': int(a.get('data-level', 0))}
        if tag == 'tool-tip':
            self.current = a.get('for')
            self.tips[self.current] = ''
    def handle_data(self, data):
        if self.current: self.tips[self.current] += data
    def handle_endtag(self, tag):
        if tag == 'tool-tip': self.current = None

def main():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)
    urls = []
    days = []
    for year in range(start.year, today.year + 1):
        url = f'https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31'
        urls.append(url)
        calendar = Calendar()
        calendar.feed(request(url))
        for identity, day in calendar.cells.items():
            if not str(start) <= day['date'] <= str(today): continue
            tip = calendar.tips.get(identity, '')
            count = re.search(r'([\d,]+) contributions?\b', tip)
            if count: value = int(count.group(1).replace(',', ''))
            elif re.search(r'No contributions?\b', tip, re.I): value = 0
            else: raise RuntimeError('Calendar count could not be parsed; preserve previous data.')
            days.append({**day, 'count': value})
    days = list({d['date']:d for d in days}.values())
    days.sort(key=lambda d: d['date'])
    if len(days) < 364: raise RuntimeError(f'Incomplete public calendar: {len(days)} days')

    query = '''query($login:String!, $cursor:String) { user(login:$login) {
      repositories(first:100, after:$cursor, privacy:PUBLIC, isFork:false, ownerAffiliations:OWNER,
        orderBy:{field:NAME,direction:ASC}) {
        pageInfo { hasNextPage endCursor }
        nodes { nameWithOwner isArchived languages(first:100,orderBy:{field:SIZE,direction:DESC}) {
          totalCount edges { size node { name color } }
        } }
      }
    } }'''
    repos = []; cursor = None
    while True:
        payload = json.loads(request('https://api.github.com/graphql',
            {'query': query, 'variables': {'login': USER, 'cursor': cursor}}, authenticated=True))
        if payload.get('errors'): raise RuntimeError('GitHub GraphQL rejected the language query: ' + str(payload['errors']))
        page = payload['data']['user']['repositories']
        for repo in page['nodes']:
            languages = repo['languages']
            if languages['totalCount'] > len(languages['edges']): raise RuntimeError('Incomplete repository language list')
            repos.append({'name': repo['nameWithOwner'], 'archived': repo['isArchived'],
                'languages': [{'name': e['node']['name'], 'color': e['node']['color'], 'bytes': e['size']} for e in languages['edges']]})
        if not page['pageInfo']['hasNextPage']: break
        cursor = page['pageInfo']['endCursor']
    totals = Counter(); colors = {}
    for repo in repos:
        for language in repo['languages']:
            totals[language['name']] += language['bytes']
            colors[language['name']] = language['color'] or '#adbec1'
    snapshot = {'updated_at': str(today), 'calendar_source': urls, 'calendar': days,
        'language_scope': 'GitHub language bytes in owned, public, non-fork repositories, including archived repositories.',
        'repositories': repos,
        'languages': [{'name': name, 'bytes': size, 'color': colors[name]} for name, size in totals.most_common()]}
    (ROOT/'data/activity.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Public activity: {len(days)} days, {sum(d["count"] for d in days)} contributions; {len(repos)} repositories, {len(totals)} languages.')

if __name__ == '__main__': main()
