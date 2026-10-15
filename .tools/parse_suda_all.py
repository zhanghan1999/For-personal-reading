# -*- coding: utf-8 -*-
"""用 lxml 解析苏大主页全部书目（书名+作者+出版社+PDF链接）。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import html

t = open(r'C:\导师文集\.tools\sources\snow\为亚洲而战\suda_main.html', encoding='utf-8').read()
doc = html.fromstring(t)

items = []
for li in doc.xpath('//li[contains(@class,"news")]'):
    a = li.xpath('.//a[1]')
    if not a:
        continue
    href = a[0].get('href') or ''
    title_el = li.xpath('.//div[contains(@class,"s3")]')
    title = title_el[0].text_content().strip() if title_el else ''
    if not title or not href:
        continue
    # 作者/出版社
    spans = [s.text_content().strip() for s in li.xpath('.//span[contains(@class,"s5")]')]
    author = spans[0] if len(spans) > 0 else ''
    pub = spans[1] if len(spans) > 1 else ''
    items.append((title, author, pub, href))

print('条目数:', len(items))
seen = set()
for title, author, pub, href in items:
    key = title
    if key in seen:
        continue
    seen.add(key)
    print('-', title, '|', author, '|', pub, '|', href)

# 筛斯诺相关
print('\n=== 斯诺/尼姆/韦尔斯 相关 ===')
for title, author, pub, href in items:
    if any(k in title or k in author for k in ['斯诺', '西行漫记', '红星', '亚洲', '复始', '大河', '红区',
                                                '红色中国', '漫长的革命', '苏联力量', '斯大林需要', '委员长',
                                                '尼姆', '韦尔斯', '威尔', '全集', '文集']):
        print('★', title, '|', author, '|', pub, '|', href)
