#!/usr/bin/env python3
"""Apply summarisation results from data/summaries.tsv into data/stars.json.

Queue format (tab separated, 4 columns, no header required):
    full_name    summary    tags(comma)    aliases(comma)

Rows whose full_name exists get merged (pending -> 0) and are removed from the queue,
so the file only ever holds what is still waiting to be applied.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
STARS = os.path.join(DATA, 'stars.json')
QUEUE = os.path.join(DATA, 'summaries.tsv')


def main():
    if not os.path.exists(QUEUE):
        print('[skip] no data/summaries.tsv')
        return
    lines = [l.rstrip('\n') for l in open(QUEUE, encoding='utf-8') if l.strip()]
    rows = json.load(open(STARS, encoding='utf-8'))
    by_name = {r['full_name']: r for r in rows}

    applied, left = 0, []
    for ln in lines:
        p = ln.split('\t')
        if p[0].strip().lower() == 'full_name':
            continue
        if len(p) < 2 or not p[1].strip():
            left.append(ln)
            continue
        full = p[0].strip()
        r = by_name.get(full)
        if not r:
            print('[warn] not in stars.json: %s' % full)
            left.append(ln)
            continue
        r['summary'] = p[1].strip()
        if len(p) > 2 and p[2].strip():
            r['tags_str'] = p[2].strip()
        if len(p) > 3 and p[3].strip():
            r['aliases'] = [a.strip() for a in p[3].split(',') if a.strip()]
        r['pending'] = 0
        applied += 1

    with open(STARS, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(QUEUE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(left) + ('\n' if left else ''))
    print('[done] applied: %d | still queued: %d | pending in data: %d'
          % (applied, len(left), sum(1 for r in rows if r.get('pending'))))


if __name__ == '__main__':
    main()
