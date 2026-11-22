#!/usr/bin/env python3
"""Pull the authenticated user's starred repos and merge into data/stars.json.

Requires env STARS_TOKEN: a classic PAT with at least `public_repo` (read is enough).
GITHUB_TOKEN from Actions CANNOT read /user/starred, so a PAT is mandatory.
If STARS_TOKEN is missing the script exits 0 and leaves existing data alone.
"""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
STARS = os.path.join(DATA, 'stars.json')
PENDING = os.path.join(DATA, 'pending.tsv')
API = 'https://api.github.com'
TZ = timezone(timedelta(hours=8))


def fetch(path, token):
    r = urllib.request.Request(API + path)
    r.add_header('Accept', 'application/vnd.github.star+json')
    r.add_header('Authorization', 'Bearer ' + token)
    r.add_header('User-Agent', 'star-filter-refresh')
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def day_of(iso):
    return (iso or '')[:10]


def status_of(repo):
    if repo.get('archived'):
        return '已归档'
    pushed = repo.get('pushed_at') or ''
    if pushed:
        try:
            dt = datetime.fromisoformat(pushed.replace('Z', '+00:00'))
            if (datetime.now(timezone.utc) - dt).days > 730:
                return '2年未更新'
        except Exception:
            pass
    return '活跃'


def main():
    token = (os.environ.get('STARS_TOKEN') or '').strip()
    if not token:
        print('[skip] STARS_TOKEN not set - keeping existing data/stars.json')
        return

    old = {}
    if os.path.exists(STARS):
        for r in json.load(open(STARS, encoding='utf-8')):
            old[r['full_name']] = r
    print('[info] existing entries: %d' % len(old))

    items, page = [], 1
    while page <= 100:
        batch = fetch('/user/starred?per_page=100&page=%d' % page, token)
        if not batch:
            break
        items.extend(batch)
        print('[info] page %d -> %d' % (page, len(batch)))
        page += 1

    rows, new_count = [], 0
    for it in items:
        repo = it.get('repo') or it
        full = repo['full_name']
        prev = old.get(full, {})
        summary = (prev.get('summary') or '').strip()
        if not summary:
            new_count += 1
        rows.append({
            'full_name': full,
            'name': repo.get('name') or full.split('/')[-1],
            'owner': (repo.get('owner') or {}).get('login', full.split('/')[0]),
            'url': repo.get('html_url') or ('https://github.com/' + full),
            'summary': summary,
            'tags_str': prev.get('tags_str', ''),
            'aliases': prev.get('aliases', []),
            'description': repo.get('description') or '',
            'topics_str': ','.join(repo.get('topics') or []),
            'language': repo.get('language') or '',
            'stars': repo.get('stargazers_count') or 0,
            'forks': repo.get('forks_count') or 0,
            'star_day': day_of(it.get('starred_at')),
            'pushed_day': day_of(repo.get('pushed_at')),
            'created_day': day_of(repo.get('created_at')),
            'status': status_of(repo),
            'suggest_cat': prev.get('suggest_cat', ''),
            'pending': 0 if summary else 1,
        })

    os.makedirs(DATA, exist_ok=True)
    with open(STARS, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    todo = [r for r in rows if r['pending']]
    with open(PENDING, 'w', encoding='utf-8') as f:
        f.write('full_name\tdescription\ttopics\tlanguage\turl\n')
        for r in todo:
            f.write('%s\t%s\t%s\t%s\t%s\n' % (
                r['full_name'], (r['description'] or '').replace('\t', ' '),
                r['topics_str'], r['language'], r['url']))

    print('[done] total: %d | new/unsunnmarised: %d' % (len(rows), len(todo)))
    if todo:
        print('[next] run: python scripts/print_pending.py   (then paste into a free LLM)')


if __name__ == '__main__':
    main()
