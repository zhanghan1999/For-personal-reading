# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\snow\复始之旅'
fixes = {
    '02-到达中国.txt': ['历'],
    '64-青年.txt': ['青'],
}
for fn, bads in fixes.items():
    path = os.path.join(OUT, fn)
    lines = open(path, encoding='utf-8').read().split('\n')
    while lines:
        t = lines[0].strip()
        if not t or any(b == t for b in bads):
            lines.pop(0)
        else:
            break
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print(fn, '->', (lines[0][:30] if lines else '(empty)'))
print('DONE')
