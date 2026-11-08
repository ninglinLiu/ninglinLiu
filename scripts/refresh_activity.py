"""Fetch public profile activity and language bytes; keep tokens out of artifacts."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import Counter
import json
import os
import time
import urllib.error
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
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=45) as response:
                return response.read().decode('utf-8')
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** (attempt + 1))

def parse_calendar(weeks, start, today):
    levels = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2,
              'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
    days = []
    for week in weeks:
        for day in week['contributionDays']:
            if not str(start) <= day['date'] <= str(today):
                continue
            count = day['contributionCount']
            if not isinstance(count, int) or count < 0:
                raise RuntimeError('Invalid contribution count; preserve previous data.')
            days.append({'date': day['date'], 'level': levels[day['contributionLevel']], 'count': count})
    expected = {str(start + timedelta(days=i)) for i in range((today - start).days + 1)}
    if len(days) != len(expected) or {d['date'] for d in days} != expected:
        raise RuntimeError('Incomplete or duplicate public calendar; preserve previous data.')
    return sorted(days, key=lambda d: d['date'])

def main():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)
    # Official schema: https://docs.github.com/en/graphql/reference/users#contributionscollection
    # Actions uses a repository token without read:user scope: public contributions only.
    calendar_query = '''query($login:String!, $from:DateTime!, $to:DateTime!) {
      user(login:$login) { contributionsCollection(from:$from, to:$to) {
        contributionCalendar { weeks { contributionDays { date contributionCount contributionLevel } } }
      } }
    }'''
    calendar_payload = json.loads(request('https://api.github.com/graphql',
        {'query': calendar_query, 'variables': {'login': USER,
         'from': f'{start}T00:00:00Z', 'to': f'{today}T23:59:59Z'}}, authenticated=True))
    if calendar_payload.get('errors'):
        raise RuntimeError('GitHub GraphQL rejected the calendar query: ' + str(calendar_payload['errors']))
    weeks = calendar_payload['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    days = parse_calendar(weeks, start, today)
    urls = ['https://api.github.com/graphql', f'https://github.com/{USER}?tab=overview']

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
