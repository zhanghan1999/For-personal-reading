# -*- coding: utf-8 -*-
"""从苏大数据库主页提取所有书目条目：PDF链接 + 书名 + 作者 + 出版社 + 时间。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()

blocks = re.findall(r'<li class="news[^"]*">(.*?)</li>', t, re.S)
print('条目块数:', len(blocks))
for b in blocks:
    href = re.search(r'<a href="([^"]+\.pdf)', b)
    title = re.search(r'class="s3[^"]*">([^<]+)<', b)
    author = re.search(r'作者：</span>\s*<span class="s5[^"]*">([^<]+)<', b)
    pub = re.search(r'出版社：</span>\s*<span class="s5[^"]*">([^<]+)<', b)
    year = re.search(r'出版时间：</span>\s*<span class="s5[^"]*">([^<]+)<', b)
    if href and title:
        print('-', title.group(1).strip(), '|', (author.group(1).strip() if author else '?'), '|',
              (pub.group(1).strip() if pub else '?'), '|', (year.group(1).strip() if year else '?'))
        print('   PDF:', 'https://marxism.suda.edu.cn' + href.group(1).strip())
