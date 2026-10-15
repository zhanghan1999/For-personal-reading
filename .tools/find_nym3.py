# -*- coding: utf-8 -*-
"""找尼姆·韦尔斯/续西行漫记 条目的 page.psp 详情页链接。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

psp = [(m.start(), m.group(0)) for m in re.finditer(r'href="(/wxk/[^"]+page\.psp[^"]*)"', t)]
print('page.psp 链接数:', len(psp))

for kw in ['尼姆', '韦尔斯', '华侃', '续西行', '中国为民主', '延安采访']:
    for m in re.finditer(kw, t):
        pos = m.start()
        best = None
        for p, h in psp:
            if 0 < p - pos < 8000 and (best is None or p - pos < best[0]):
                best = (p - pos, h)
        if best:
            seg = re.sub(r'<[^>]+>', ' ', t[max(0, pos - 60):pos + 120])
            seg = re.sub(r'\s+', ' ', seg).strip()
            print('★', kw, '|', seg, '| 详情页:', 'https://marxism.suda.edu.cn' + best[1])
