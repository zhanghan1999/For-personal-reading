# -*- coding: utf-8 -*-
"""find_work_start.py — 查找《论列宁主义基础》标题页与开头句子。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
for p in range(1848, 1858):
    t = doc[p].get_text()
    first = ' '.join(t.split())[:100]
    print('== PDF', p, '==')
    print(first)
    print()
doc.close()
