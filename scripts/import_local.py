#!/usr/bin/env python3
"""One-off: import an existing stars.json (rich version) into data/stars.json (slim).

Usage:
    python scripts/import_local.py "C:\\path\\to\\stars.json"
Already-summarised entries keep summary/tags/aliases; the rest are marked pending.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
STARS = os.path.join(DATA, 'stars.json')


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: import_local.py <source stars.json>')
    src = json.load(open(sys.argv[1], encoding='utf-8'))
    rows = []
    for r in src:
        summary = (r.get('summary') or '').strip()
        rows.append({
            'full_name': r.get('full_name', ''),
            'name': r.get('name') or r.get('full_name', '').split('/')[-1],
            'owner': r.get('owner') or r.get('full_name', '').split('/')[0],
            'url': r.get('url') or ('https://github.com/' + r.get('full_name', '')),
            'summary': summary,
            'tags_str': r.get('tags_str', '') or '',
            'aliases': r.get('aliases') or [],
            'description': r.get('description') or '',
            'topics_str': r.get('topics_str', '') or '',
            'language': r.get('language') or '',
            'stars': r.get('stars') or 0,
            'forks': r.get('forks') or 0,
            'star_day': r.get('star_day', ''),
            'pushed_day': r.get('pushed_day', ''),
            'created_day': r.get('created_day', ''),
            'status': r.get('status', ''),
            'suggest_cat': r.get('suggest_cat', ''),
            'pending': 0 if summary else 1,
        })
    rows.sort(key=lambda x: (x['star_day'] or '', x['full_name']), reverse=True)
    os.makedirs(DATA, exist_ok=True)
    with open(STARS, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    pend = sum(1 for x in rows if x['pending'])
    print('[done] imported %d | pending %d | %.1f KB'
          % (len(rows), pend, os.path.getsize(STARS) / 1024))


if __name__ == '__main__':
    main()
