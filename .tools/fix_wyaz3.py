# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\snow\为亚洲而战'
fixes = {
    '18-月光和炸弹.txt': 3,
    '22-一个理想的史诗.txt': 1,
    '40-自由中国的希望.txt': 1,
    '44-革命和反动.txt': 3,
}
for fn, n in fixes.items():
    path = os.path.join(OUT, fn)
    lines = open(path, encoding='utf-8').read().split('\n')
    # 移除前 n 个非空行
    removed = 0
    while removed < n and lines:
        t = lines[0].strip()
        if t:
            removed += 1
        lines.pop(0)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    first = next((l for l in lines if l.strip()), '(empty)')
    print(fn, '->', first.strip()[:40])
print('DONE')
