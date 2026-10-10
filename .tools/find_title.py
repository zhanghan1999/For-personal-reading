# -*- coding: utf-8 -*-
"""find_title.py — 找到《论列宁主义基础》标题页与正文起点。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
for p in range(1788, 1812):
    t = doc[p].get_text().replace('\n', ' | ').strip()[:130]
    print(p, '::', t)
print('==== detail 1792-1796 ====')
for p in [1790, 1791, 1792]:
    print('==', p, '==')
    print(doc[p].get_text()[:500])
doc.close()
