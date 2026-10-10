# -*- coding: utf-8 -*-
import os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = r'C:\导师文集\教员\毛选\5\07-为争取国家财政经济状况的基本好转而斗争.html'
html = open(p, encoding='utf-8').read()
m = re.search(r'<div class="notes">(.*?)<div class="chapnav"', html, flags=re.S)
if m:
    print('NOTES BLOCK:')
    print(m.group(1)[:1500])
else:
    print('no notes block found')
    # 找 note 相关
    for mm in re.finditer(r'note', html):
        print('note at', mm.start(), ':', html[max(0, mm.start()-40):mm.start()+80])
        break
