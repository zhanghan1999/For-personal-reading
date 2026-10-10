# -*- coding: utf-8 -*-
"""find_intro.py — 搜索引言句以确定《论列宁主义基础》起点。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
targets = ['列宁主义是帝国主义和无产阶级革命时代的马克思主义',
           '什么是列宁主义',
           '列宁主义一般是无产阶级革命的理论和策略']
for p in range(1830, 1850):
    t = doc[p].get_text().replace('\n', '')
    for tg in targets:
        if tg in t:
            print('HIT page', p, 'for', tg)
            print(doc[p].get_text()[:400])
            print()
            break
doc.close()
