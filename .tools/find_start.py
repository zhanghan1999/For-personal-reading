# -*- coding: utf-8 -*-
"""find_start.py — 定位《论列宁主义基础》起始页（标题页/序言开头）。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
for p in range(1850, 1865):
    t = doc[p].get_text().replace('\n', ' | ').strip()[:150]
    print(p, '::', t)
print('---- 1858-1862 full first 600 ----')
for p in [1858, 1859, 1860, 1861]:
    print('== page', p, '==')
    print(doc[p].get_text()[:600])
doc.close()
