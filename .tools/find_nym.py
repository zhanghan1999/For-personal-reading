# -*- coding: utf-8 -*-
"""精确定位苏大主页上尼姆·韦尔斯/续西行漫记条目的 PDF 链接。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

# 找含 尼姆/韦尔斯/华侃/续西行 的条目块：取 li.news 块
blocks = re.findall(r'<li class="news[^"]*">(.*?)</li>\s*</li>', t, re.S)
if not blocks:
    blocks = re.findall(r'<li class="news[^"]*">(.*?)</li>', t, re.S)
print('块数:', len(blocks))
for i, b in enumerate(blocks):
    if any(k in b for k in ['尼姆', '韦尔斯', '华侃', '续西行', 'Nym', 'Wales']):
        href = re.search(r'<a href="([^"]+\.pdf)', b)
        title = re.search(r'class="s3[^"]*">\s*([^<]+)<', b)
        print('块', i, '| 标题:', title.group(1).strip() if title else '?', '| PDF:', href.group(1).strip() if href else '?')
