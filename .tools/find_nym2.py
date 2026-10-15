# -*- coding: utf-8 -*-
"""快速定位：尼姆/韦尔斯/华侃/续西行 出现处 → 扫描附近 PDF href。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

pdfs = [(m.start(), m.group(0).strip()) for m in re.finditer(r'/_upload/article/files/[^"\']+\.pdf', t)]
print('pdf 总数:', len(pdfs))

for kw in ['尼姆', '韦尔斯', '华侃', '续西行']:
    for m in re.finditer(kw, t):
        pos = m.start()
        # 向前 6000 字符内最近的 pdf（标题在 pdf 链接之后 3000 内）
        best = None
        for p, h in pdfs:
            if 0 < p - pos < 6000 and (best is None or p - pos < best[0]):
                best = (p - pos, h)
        seg = re.sub(r'<[^>]+>', ' ', t[max(0, pos - 60):pos + 100])
        seg = re.sub(r'\s+', ' ', seg).strip()
        print('★', kw, '|', seg, '| PDF:', ('https://marxism.suda.edu.cn' + best[1]) if best else '(附近无 PDF)')
