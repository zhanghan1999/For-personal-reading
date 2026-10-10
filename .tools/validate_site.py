# -*- coding: utf-8 -*-
"""Validate the rebuilt site structure."""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'

def check_file(path, checks):
    if not os.path.exists(path):
        print('  MISSING:', path)
        return
    html = open(path, encoding='utf-8').read()
    problems = []
    for label, pat in checks:
        if not re.search(pat, html, flags=re.S):
            problems.append(label)
    print('  %-40s size=%6dKB %s' % (os.path.relpath(path, ROOT), len(html) // 1024,
                                     ('OK' if not problems else 'MISSING: ' + ','.join(problems))))

# 公共资源
print('== 公共资源 ==')
for f in ['assets/style.css', 'assets/app.js', 'index.html']:
    check_file(os.path.join(ROOT, f), [
        ('has css vars', r'--paper'),
    ] if f.endswith('css') else [('has app.js', r'app.js')])

# 首页
print('== 首页 ==')
check_file(os.path.join(ROOT, 'index.html'), [
    ('五导师', r'马克思.*恩格斯.*列宁.*斯大林.*毛泽东'),
    ('头像占位', r'class="avatar"'),
])

# 毛选
print('== 毛选 ==')
check_file(os.path.join(ROOT, '教员', '毛选.html'), [('卡片', r'class="card"')])
check_file(os.path.join(ROOT, '教员', 'index.html'), [('卡片', r'class="card"')])
for v in [1, 5]:
    d = os.path.join(ROOT, '教员', '毛选', str(v))
    files = sorted(f for f in os.listdir(d) if f.endswith('.html'))
    print('  第%d卷 文章数: %d' % (v, len(files)))
    if files:
        fp = os.path.join(d, files[0])
        html = open(fp, encoding='utf-8').read()
        checks = [
            ('引style.css', r'assets/style\.css'),
            ('引app.js', r'assets/app\.js'),
            ('PAGE数据', r'window\.PAGE'),
            ('目录容器', r'id="toclist"'),
            ('折叠按钮', r'id="tocCollapseBtn"'),
            ('无旧menuBtn', r'^(?!.*id="menuBtn")'),
            ('article', r'<article'),
            ('notes', r'class="notes"'),
            ('fnref', r'class="fnref"'),
        ]
        print('  样例文章 %s:' % files[0])
        for label, pat in checks:
            ok = re.search(pat, html, flags=re.S) is not None
            print('    %-16s %s' % (label, 'OK' if ok else 'FAIL'))

# 资本论
print('== 资本论 ==')
check_file(os.path.join(ROOT, '马克思', '资本论.html'), [('卡片', r'class="card"')])
check_file(os.path.join(ROOT, '马克思', 'index.html'), [('卡片', r'class="card"')])
for v in [1, 3]:
    d = os.path.join(ROOT, '马克思', '资本论', str(v))
    files = sorted(f for f in os.listdir(d) if f.endswith('.html') and not f.startswith('合并'))
    print('  第%d卷 文章数: %d' % (v, len(files)))
    if files:
        fp = os.path.join(d, files[0])
        html = open(fp, encoding='utf-8').read()
        print('  样例 %s:' % files[0])
        for label, pat in [
            ('引style.css', r'assets/style\.css'),
            ('PAGE数据', r'window\.PAGE'),
            ('折叠按钮', r'id="tocCollapseBtn"'),
            ('article', r'<article'),
            ('notes', r'class="notes"'),
        ]:
            print('    %-16s %s' % (label, 'OK' if re.search(pat, html) else 'FAIL'))

# 占位页
print('== 占位页 ==')
for m in ['恩格斯', '列宁', '斯大林']:
    check_file(os.path.join(ROOT, m, 'index.html'), [('占位', r'class="placeholder"')])
