# -*- coding: utf-8 -*-
"""在苏大主页直接找斯诺相关书名，并提取其附近 PDF 链接。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

# 所有 pdf href 位置
pdfs = [(m.start(), m.group(1).strip()) for m in re.finditer(r'<a href="(/_upload/article/files/[^"]+\.pdf)', t)]
pdfs.sort()

keys = ['斯诺', '西行漫记', '红星照耀中国', '为亚洲而战', '复始之旅', '大河彼岸', '漫长的革命', '红区内幕',
        '苏联力量的格局', '斯大林需要和平', '委员长生活漫记', '红色中国', '尼姆', '海伦', '威尔']
hits = []
for k in keys:
    for m in re.finditer(re.escape(k), t):
        pos = m.start()
        # 找最近的 pdf
        best = None
        for p, h in pdfs:
            if abs(p - pos) < 4000 and (best is None or abs(p - pos) < abs(best[0] - pos)):
                best = (p, h)
        if best:
            hits.append((k, pos, best[1]))
seen = set()
for k, pos, href in hits:
    key = (k, href)
    if key in seen:
        continue
    seen.add(key)
    # 取书名上下文
    seg = t[max(0, pos - 50):pos + 80]
    seg = re.sub(r'<[^>]+>', ' ', seg)
    seg = re.sub(r'\s+', ' ', seg).strip()
    print('★', k, '| 上下文:', seg, '|', 'https://marxism.suda.edu.cn' + href)
