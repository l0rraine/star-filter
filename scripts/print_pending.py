#!/usr/bin/env python3
"""Print the batch of unsummarised repos in the exact input format PROMPT.md expects.

Usage:
    python scripts/print_pending.py        # everything pending
    python scripts/print_pending.py 20     # first 20 only (good batch size for a chat window)
Copy the block between the two --- lines and paste it into any free LLM together with PROMPT.md.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
STARS = os.path.join(DATA, 'stars.json')
OUT = os.path.join(DATA, 'pending-input.txt')


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
    rows = json.load(open(STARS, encoding='utf-8'))
    todo = [r for r in rows if r.get('pending') or not (r.get('summary') or '').strip()]
    todo = todo[:limit]
    if not todo:
        print('[ok] nothing pending - all %d entries have a summary' % len(rows))
        return

    lines = []
    for i, r in enumerate(todo, 1):
        desc = (r.get('description') or '').strip().replace('\n', ' ')[:160]
        topics = (r.get('topics_str') or '').replace(',', ' ')[:80]
        if not desc and not topics:
            desc = '（无简介）'
        lines.append('%d. %s | %s | topics: %s | %s | ★%s'
                     % (i, r['full_name'], desc, topics or '-', r.get('language') or '-',
                        r.get('stars') or 0))

    block = '=== INPUT BEGIN ===\n' + '\n'.join(lines) + '\n=== INPUT END ==='
    print(block)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(block + '\n')
    print('\n[info] %d items, saved to data/pending-input.txt' % len(todo))


if __name__ == '__main__':
    main()
