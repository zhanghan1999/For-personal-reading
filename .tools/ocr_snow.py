# -*- coding: utf-8 -*-
"""ocr_snow.py — 对斯诺系列扫描版 PDF 逐页 OCR。
用法: python ocr_snow.py <pdf路径> <输出目录> [起始页] [结束页]
输出: 输出目录/P{NNN}.txt（物理页号）
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PDF = sys.argv[1]
OUT = sys.argv[2]
lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
hi = int(sys.argv[4]) if len(sys.argv) > 4 else None
os.makedirs(OUT, exist_ok=True)

from rapidocr_onnxruntime import RapidOCR
import pymupdf

ocr = RapidOCR()
doc = pymupdf.open(PDF)
TOTAL = doc.page_count
if hi is None:
    hi = TOTAL - 3  # 跳过末尾元数据页

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
