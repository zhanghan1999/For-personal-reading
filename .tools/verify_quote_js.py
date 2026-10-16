# -*- coding: utf-8 -*-
"""校验 quote.js 注入结果。"""
import os, re

ROOT = r'C:\导师文集'
count = 0
double = []
wrong_depth = []
missing_in_noncontent = []
reading_hit = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    if any(x in dirpath for x in ('\\.git', '\\批注', '\\.tools', '\\来源数据', '\\旧版合并页')):
        continue
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT)
        s = open(p, encoding='utf-8', errors='ignore').read()
        hits = re.findall(r'<script src="([^"]*assets/quote\.js)"></script>', s)
        is_reading = 'id="main"' in s and 'window.PAGE' in s
        if hits:
            count += 1
            if len(hits) > 1:
                double.append(rel)
            depth = rel.count(os.sep)
            expect = ('../' * depth) + 'assets/quote.js'
            for h in hits:
                if h != expect:
                    wrong_depth.append((rel, h, expect))
            if is_reading:
                reading_hit.append(rel)
        else:
            dirfiles = os.listdir(dirpath)
            has_chapter = any(re.match(r'^\d+-', f) for f in dirfiles if f.endswith('.html'))
            if not has_chapter and not is_reading:
                missing_in_noncontent.append(rel)

print('含 quote.js 的页面数:', count)
print('重复注入:', double or '无')
print('路径深度错误:', wrong_depth or '无')
print('误伤正文页:', reading_hit or '无')
print('缺少脚本的非正文页:', missing_in_noncontent or '无')
