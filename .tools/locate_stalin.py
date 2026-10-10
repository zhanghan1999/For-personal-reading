# -*- coding: utf-8 -*-
"""locate_stalin.py — 定位《论列宁主义基础》在 PDF 中的起止页并抽样文本。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

doc = fitz.open(r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf')
probe = [1534, 1780, 1784, 1785, 1786, 1787, 1884, 1885, 1886, 1887, 1890, 1900]
for p in probe:
    t = doc[p].get_text().replace('\n', ' ')[:120]
    print('PAGE', p, ':', t)
doc.close()
