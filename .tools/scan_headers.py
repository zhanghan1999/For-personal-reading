# -*- coding: utf-8 -*-
"""scan_headers.py — 扫描 1860-2050 页的运行页眉，定位《论列宁主义基础》起止。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
# 页眉通常在第一行文本里
for p in range(1860, 2070, 2):
    t = doc[p].get_text().strip().replace('\n', ' | ')[:90]
    print(p, '::', t)
doc.close()
