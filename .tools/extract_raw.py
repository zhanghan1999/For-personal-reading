# -*- coding: utf-8 -*-
"""extract_raw.py — 提取《论列宁主义基础》原始文本到本地供清洗。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
parts = []
for p in range(1840, 1983):
    t = doc[p].get_text()
    parts.append('===== PDFPAGE %d =====\n%s' % (p, t))
open(r'C:\导师文集\.tools\sources\stalin\lnjz-raw.txt', 'w', encoding='utf-8').write('\n'.join(parts))
print('wrote raw, chars:', sum(len(x) for x in parts))
doc.close()
