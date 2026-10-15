# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\snow\为亚洲而战'
fixes = {
    '12-政治一瞥.txt': ['政治一警'],
    '18-月光和炸弹.txt': ['第四篇'],
    '22-一个理想的史诗.txt': ['第五篇中国的“工合线'],
    '40-自由中国的希望.txt': ['第九篇帝国或民主？'],
    '44-革命和反动.txt': ['第十篇'],
    '47-一九四三年从重庆看中国之命运.txt': ['看中国之命运'],
}
for fn, bads in fixes.items():
    path = os.path.join(OUT, fn)
    lines = open(path, encoding='utf-8').read().split('\n')
    while lines:
        t = lines[0].strip()
        if not t or any(b in t for b in bads):
            lines.pop(0)
        else:
            break
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print(fn, '->', (lines[0][:30] if lines else '(empty)'))
print('DONE')
