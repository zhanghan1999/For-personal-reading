# -*- coding: utf-8 -*-
"""从苏大数据库主页提取所有书目条目（链接 + 标题 + 作者/出版社）。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

# 找书条目链接
hrefs = re.findall(r'href="([^"]*c\d+[^"]*page\.psp[^"]*)"[^>]*>\s*([^<]{1,60})<', t)
seen = set()
for h, title in hrefs:
    title = title.strip()
    if title and (h, title) not in seen:
        seen.add((h, title))
        print(h, '|', title)
print('--- 总数:', len(seen))

# 也找含 斯诺 的片段，看作者信息
print('=== 斯诺 作者信息上下文 ===')
for m in re.finditer(r'斯诺', t):
    s = max(0, m.start() - 40)
    seg = t[s:m.start() + 60]
    seg = re.sub(r'<[^>]+>', ' ', seg)
    seg = re.sub(r'\s+', ' ', seg).strip()
    if '作者' in seg or '出版社' in seg or '出版时间' in seg:
        print('-', seg)
