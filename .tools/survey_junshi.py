# -*- coding: utf-8 -*-
"""survey_junshi.py — 普查六卷军事文集 txt 的解析结构，找出格式异常。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = r'C:\导师文集\.tools\sources\mzdbl'

def gbk(path):
    raw = open(path, 'rb').read()
    return raw.decode('gb18030', errors='replace')

DATE_RE = re.compile(r'^（\s*一九[一二三四五六七八九十〇零]*\d*\s*年.*）\s*$')
problems = []
for vol in range(1, 7):
    vol_dir = os.path.join(BASE, '毛泽东军事文集%d' % vol)
    # 找文章文件（排除 *000* 目录文件）
    files = []
    for root, _, fs in os.walk(vol_dir):
        for f in fs:
            if f.lower().endswith('.txt') and '000' not in f[:8]:
                files.append(os.path.join(root, f))
    files.sort()
    print('== 卷%d: %d 篇' % (vol, len(files)))
    no_date = 0
    empty = 0
    for fp in files:
        try:
            t = gbk(fp)
        except Exception as e:
            problems.append('%s: decode err %s' % (fp, e)); continue
        lines = [ln.strip() for ln in t.splitlines()]
        lines = [ln for ln in lines if ln]
        if not lines:
            empty += 1; problems.append('%s: EMPTY' % fp); continue
        has_date = any(DATE_RE.match(ln) for ln in lines[:6])
        if not has_date:
            no_date += 1
            problems.append('%s: NO-DATE | first: %s' % (os.path.basename(fp), lines[0][:30]))
    print('   无日期: %d, 空文件: %d' % (no_date, empty))
print('\n=== 异常样例（最多 25 条）===')
for p in problems[:25]:
    print(' ', p)
print('\n异常总数:', len(problems))
