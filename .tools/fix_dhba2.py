# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\snow\大河彼岸'
fixes = {
    '16-巨变.txt': 4,
    '49-人口问题.txt': 2,
    '53-延安——革命的博物馆.txt': 1,
}
for fn, n in fixes.items():
    path = os.path.join(OUT, fn)
    lines = open(path, encoding='utf-8').read().split('\n')
    removed = 0
    while removed < n and lines:
        if lines[0].strip():
            removed += 1
        lines.pop(0)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    first = next((l for l in lines if l.strip()), '(empty)')
    print(fn, '->', first.strip()[:40])
print('DONE')
