#!/usr/bin/env python3
"""Build index.html from data/stars.json + scripts/template.html (single file, no deps)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'stars.json')
TPL = os.path.join(ROOT, 'scripts', 'template.html')
OUT = os.path.join(ROOT, 'index.html')


def main():
    rows = json.load(open(DATA, encoding='utf-8'))
    arr = []
    for r in rows:
        summary = (r.get('summary') or '').strip()
        desc = (r.get('description') or '').strip()
        if not summary:
            summary = '待总结：' + (desc[:40] if desc else '（无简介）')
        arr.append([
            r.get('full_name', ''), r.get('name', ''), r.get('owner', ''),
            summary, r.get('tags_str', ''),
            ','.join(r.get('aliases') or []),
            desc[:150], r.get('topics_str', ''), r.get('language') or '',
            r.get('stars') or 0, r.get('pushed_day', ''), r.get('status', ''),
            r.get('url', ''), r.get('suggest_cat', ''),
            1 if (r.get('pending') or not (r.get('summary') or '').strip()) else 0,
        ])
    tpl = open(TPL, encoding='utf-8').read()
    html = tpl.replace('__DATA__', json.dumps(arr, ensure_ascii=False, separators=(',', ':')))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    pend = sum(1 for x in arr if x[14])
    print('[done] index.html %d KB | entries: %d | pending: %d'
          % (len(html.encode('utf-8')) // 1024, len(arr), pend))


if __name__ == '__main__':
    main()
