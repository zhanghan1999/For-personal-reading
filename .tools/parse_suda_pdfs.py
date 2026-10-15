# -*- coding: utf-8 -*-
"""提取苏大主页所有 PDF 链接 + 书名。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

# 找所有 a href pdf
pdfs = list(re.finditer(r'<a href="(/_upload/article/files/[^"]+\.pdf)', t))
print('PDF 链接数:', len(pdfs))
out = []
for m in pdfs:
    start = m.start()
    # 向后找最近的 s3 标题（标题在 a 标签内部）
    seg = t[start:start + 3000]
    tm = re.search(r'class="s3[^"]*">\s*([^<]+)<', seg)
    title = tm.group(1).strip() if tm else '(无标题)'
    href = m.group(1).strip()
    out.append((title, href))
    print('-', title, '|', href)

# 过滤斯诺相关
print('=== 斯诺相关 ===')
for title, href in out:
    if any(k in title for k in ['斯诺', '西行漫记', '红星', '亚洲', '复始', '大河', '红色中国', '漫长的革命', '红区', '苏联力量', '斯大林需要', '委员长']):
        print('★', title, '|', href)
