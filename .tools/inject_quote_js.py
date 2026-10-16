# -*- coding: utf-8 -*-
"""把 assets/quote.js 挂到所有非正文页面（首页/人物页/书籍选卷页）。"""
import os, re

ROOT = r'C:\导师文集'
SKIP_DIR_PARTS = ('\\来源数据', '\\旧版合并页', '\\.tools', '\\批注', '\\.git')

def has_bom(data):
    return data[:3] == b'\xef\xbb\xbf'

def read_text(p):
    data = open(p, 'rb').read()
    bom = has_bom(data)
    s = data.decode('utf-8-sig')
    nl = '\r\n' if s.count('\r\n') > s.count('\n') // 2 else '\n'
    return s, bom, nl

def write_text(p, s, bom, nl):
    data = s.encode('utf-8')
    if bom:
        data = b'\xef\xbb\xbf' + data
    open(p, 'wb').write(data)

def is_reading_page(p):
    try:
        s, _, _ = read_text(p)
    except Exception:
        return False
    return 'id="main"' in s and 'window.PAGE' in s

pages = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if any(x in dirpath for x in SKIP_DIR_PARTS):
        continue
    html = [f for f in filenames if f.endswith('.html')]
    if not html:
        continue
    has_chapter = any(re.match(r'^\d+-', f) for f in html)
    if has_chapter:
        continue
    for fn in html:
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT)
        if is_reading_page(p):
            print('SKIP 正文页:', rel)
            continue
        pages.append((p, rel))

pages.sort(key=lambda x: x[1])
print('待挂载页面数:', len(pages))

done, skipped = 0, []
for p, rel in pages:
    depth = rel.count(os.sep)
    tag = '<script src="%s"></script>' % ('../' * depth + 'assets/quote.js')
    s, bom, nl = read_text(p)
    if 'assets/quote.js' in s:
        skipped.append(rel)
        continue
    if '</body>' in s:
        s = s.replace('</body>', tag + nl + '</body>', 1)
    else:
        s = s.rstrip() + nl + tag + nl
    try:
        write_text(p, s, bom, nl)
        done += 1
        print('INJECTED:', rel)
    except Exception as e:
        print('!! 跳过(写入失败):', rel, '->', e)

print('完成注入:', done, ' 跳过(已有):', len(skipped))
