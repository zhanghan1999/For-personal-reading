# -*- coding: utf-8 -*-
import os, sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 直接看第五卷 parsed.json 里 07 的 footnotes 原始格式
data = json.load(open(r'C:\导师文集\教员\毛选\来源数据\卷5数据\parsed.json', encoding='utf-8'))
for a in data:
    if a.get('title', '').startswith('为争取'):
        print('title:', a['title'])
        print('footnotes:', repr(a.get('footnotes')))
        # 测试正则
        for nt in a.get('footnotes', []):
            m = re.match(r'注释\[(\d+)\](.*)', nt, flags=re.S)
            print('  match:', m.groups() if m else 'NO MATCH', '| raw:', nt[:40])
        break
