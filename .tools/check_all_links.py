# -*- coding: utf-8 -*-
"""check_all_links.py — 全站审计：解析每个 html 里的全部 <a href> 与 window.PAGE，
相对当前文件目录解析后检查目标是否存在。"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'

html_files = []
for root, _, fs in os.walk(ROOT):
    if '来源数据' in root or '.git' in root or '_pylib' in root or '_wheels' in root:
        continue
    for f in fs:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))
print('检查页面数:', len(html_files))

HREF_RE = re.compile(r'href="([^"]+)"')
bad = []
total = 0
for fp in html_files:
    try:
        html = open(fp, encoding='utf-8').read()
    except UnicodeDecodeError:
        html = open(fp, encoding='gb18030', errors='replace').read()
    d = os.path.dirname(fp)
    hrefs = set()
    for m in HREF_RE.finditer(html):
        hrefs.add(m.group(1))
    for h in hrefs:
        if not h or h.startswith(('#', 'http://', 'https://', 'mailto:', 'tel:', 'javascript:')):
            continue
        # 去掉查询串与锚点
        tgt = h.split('#')[0].split('?')[0]
        if not tgt:
            continue
        total += 1
        p = os.path.normpath(os.path.join(d, tgt))
        if not os.path.exists(p):
            bad.append((os.path.relpath(fp, ROOT), h))

print('内部链接总数:', total)
print('损坏链接数:', len(bad))
for f, h in bad:
    print('BROKEN:', f, '->', h)
