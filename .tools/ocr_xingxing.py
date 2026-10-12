# -*- coding: utf-8 -*-
"""ocr_xingxing.py — 对《西行漫记（红星照耀中国）》扫描版 PDF 逐页 OCR。
输出：每页一个文本文件到 .tools/sources/xingxing/pages/PNNN.txt（PNNN=物理页号）
用法：python ocr_xingxing.py [起始页] [结束页]
"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PDF = r'C:\导师文集\其他学习\埃德加·斯诺\西行漫记（红星照耀中国）.pdf'
OUT = r'C:\导师文集\.tools\sources\xingxing\pages'
os.makedirs(OUT, exist_ok=True)

from rapidocr_onnxruntime import RapidOCR
import pymupdf

ocr = RapidOCR()
doc = pymupdf.open(PDF)
TOTAL = doc.page_count

lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = int(sys.argv[2]) if len(sys.argv) > 2 else TOTAL - 3   # 跳过末尾 3 页元数据/目录

for i in range(lo, hi):
    dst = os.path.join(OUT, 'P%03d.txt' % i)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        continue
    pix = doc[i].get_pixmap(dpi=150)
    img_bytes = pix.tobytes('png')
    result, _ = ocr(img_bytes)
    lines = []
    if result:
        for box, txt, conf in result:
            t = (txt or '').strip()
            if t:
                lines.append(t)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    if (i - lo) % 10 == 0 or i == hi - 1:
        print('page %d/%d done, %d lines' % (i, TOTAL, len(lines)), flush=True)

doc.close()
print('OCR DONE %d..%d' % (lo, hi), flush=True)
