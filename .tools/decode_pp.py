# -*- coding: utf-8 -*-
"""decode_pp.py — 解码人民网 GBK 页面并打印链接，定位斯大林著作。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
raw = open(r'C:\导师文集\.tools\sources\pp-index.html', 'rb').read()
t = raw.decode('gb18030', errors='replace')
print('decoded len', len(t))
links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, flags=re.S)
for href, txt in links[:100]:
    txt2 = re.sub(r'<[^>]+>', '', txt).strip()
    if txt2:
        print(txt2[:44], '->', href[:100])
