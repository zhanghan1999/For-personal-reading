# -*- coding: utf-8 -*-
"""restructure.py — 站点重构：
1) 其他学习 -> 其他著作（文件夹与全部 HTML 内引用）
2) 五位导师目录移入 导师著作/
3) 重算全部相对链接（按旧位置解析 -> 导师前缀映射 -> 相对路径重算）
4) 页内文案 “其他学习” -> “其他著作”
"""
import os, re, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集'
OLD_MENTORS = ['马克思', '恩格斯', '列宁', '斯大林', '教员']
WRAP = '导师著作'
SKIP = {'.git', '.tools', 'node_modules'}

# ---------- 1) 其他学习 -> 其他著作 ----------
old_other = os.path.join(ROOT, '其他学习')
new_other = os.path.join(ROOT, '其他著作')
if os.path.isdir(old_other) and not os.path.isdir(new_other):
    os.rename(old_other, new_other)
    print('文件夹重命名: 其他学习 -> 其他著作')

def site_html_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            if fn.endswith('.html'):
                yield os.path.join(root, fn)

# ---------- 2) 文本替换 + 4) kicker ----------
n_text = 0
for fp in site_html_files():
    with open(fp, encoding='utf-8') as f:
        c = f.read()
    c2 = c.replace('其他学习', '其他著作').replace('其 他 学 习', '其 他 著 作')
    if c2 != c:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c2)
        n_text += 1
print('文本替换文件数:', n_text)

# ---------- 3) 移入 导师著作/ ----------
wrap = os.path.join(ROOT, WRAP)
os.makedirs(wrap, exist_ok=True)
for m in OLD_MENTORS:
    src = os.path.join(ROOT, m)
    dst = os.path.join(wrap, m)
    if os.path.isdir(src) and not os.path.isdir(dst):
        shutil.move(src, dst)
        print('已移入:', m)

# ---------- 链接重写 ----------
ATTR_RE = re.compile(
    r'(?P<key>href|src|homeHref|volHref|activeHref)(?P<sep>\s*=\s*|"\s*:\s*)"(?P<val>[^"]*)"')
SKIP_PREFIX = ('#', 'http:', 'https:', 'mailto:', 'tel:', 'javascript:', 'data:', 'blob:')

def map_target(abspath):
    rel = os.path.relpath(abspath, ROOT)
    parts = rel.split(os.sep)
    if parts and parts[0] in OLD_MENTORS:
        parts.insert(0, WRAP)
        return os.path.join(ROOT, *parts)
    return abspath

n_links = 0
for fp in site_html_files():
    newdir = os.path.dirname(fp)
    rel = os.path.relpath(newdir, ROOT)
    olddir = os.path.join(ROOT, *rel.split(os.sep)[1:]) if rel.split(os.sep)[0] == WRAP else newdir
    with open(fp, encoding='utf-8') as f:
        content = f.read()

    def repl(m):
        global n_links
        key, sep, val = m.group('key'), m.group('sep'), m.group('val')
        if val.startswith(SKIP_PREFIX) or not val:
            return m.group(0)
        target = os.path.normpath(os.path.join(olddir, val.replace('/', os.sep)))
        new_target = map_target(target)
        new_val = os.path.relpath(new_target, newdir).replace(os.sep, '/')
        if new_val != val:
            n_links += 1
        return '%s%s"%s"' % (key, sep, new_val)

    new_content = ATTR_RE.sub(repl, content)
    if new_content != content:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_content)
print('链接改写条数:', n_links)
print('DONE')
