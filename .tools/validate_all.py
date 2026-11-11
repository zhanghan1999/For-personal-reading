# -*- coding: utf-8 -*-
"""validate_all.py — 校验所有作品页面：链接、PAGE 数据、目录 href、关键结构。"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'
WRAP = '导师著作'
M = json.load(open(os.path.join(ROOT, '.tools', 'manifest.json'), encoding='utf-8'))['works']

problems = 0
NO_FNREF = [0]


def page_json(html):
    m = re.search(r'window\.PAGE = (\{.*?\});\s*</script>', html, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def check(pages, total):
    for rel in pages:
        fp = os.path.join(ROOT, rel)
        if not os.path.exists(fp):
            print('MISSING:', rel)
            return
        html = open(fp, encoding='utf-8').read()
        page = page_json(html)
        if not page:
            print('NO PAGE JSON:', rel)
            return
        d = os.path.dirname(fp)
        for g in page.get('tocGroups', []):
            for it in g.get('items', []):
                t = os.path.join(d, it['href'])
                if not os.path.exists(t):
                    print('BROKEN TOC:', rel, '->', it['href'])
                    return
        for key in ('activeHref', 'homeHref', 'volHref'):
            v = page.get(key)
            if not v:
                continue
            t = os.path.normpath(os.path.join(d, v))
            if not os.path.exists(t):
                print('BROKEN %s:' % key, rel, '->', v)
                return
        for pat, label in [(r'<article', 'article'), (r'id="toclist"', 'toclist'),
                           (r'id="tocCollapseBtn"', 'collapse'),
                           (r'assets/app\.js', 'appjs')]:
            if not re.search(pat, html):
                print('MISSING %s:' % label, rel)
                return
        if not re.search(r'class="fnref"', html):
            NO_FNREF[0] += 1
    print('  ok: %d pages' % total)


# 1) 各作品：选卷页 + 章节页（view=True 的为“全集视图页”，无独立正文目录）
view_works = []
for w in M:
    land = os.path.join(ROOT, WRAP, w['author'], w['landing'])
    if not os.path.exists(land):
        print('MISSING landing:', os.path.relpath(land, ROOT)); problems += 1
        continue
    d = os.path.join(ROOT, WRAP, w['author'], w['dir'])
    if w.get('view') or not os.path.isdir(d):
        if not w.get('view'):
            print('NO DIR (未标记 view):', os.path.relpath(d, ROOT)); problems += 1
            continue
        html = open(land, encoding='utf-8').read()
        if 'window.PAGE' in html:
            print('VIEW PAGE 仍有 window.PAGE:', os.path.relpath(land, ROOT)); problems += 1
        view_works.append(w['title'])
        continue
    files = sorted(f for f in os.listdir(d) if f.endswith('.html'))
    print('== %s / %s : %d 页' % (w['author'], w['title'], len(files)))
    check([os.path.join(WRAP, w['author'], w['dir'], f) for f in files], len(files))
print('== 全集视图页: %d 个 (%s)' % (len(view_works), '、'.join(view_works)))

# 1b) 马克思恩格斯全集（正文唯一存放地）
set_dir = os.path.join(ROOT, WRAP, '马克思', '马克思恩格斯全集')
if not os.path.isdir(set_dir):
    print('MISSING:', os.path.relpath(set_dir, ROOT)); problems += 1
else:
    vols = sorted(d for d in os.listdir(set_dir) if os.path.isdir(os.path.join(set_dir, d)))
    n_pages = 0
    for v in vols:
        fs = sorted(f for f in os.listdir(os.path.join(set_dir, v)) if f.endswith('.html'))
        n_pages += len(fs)
        check([os.path.join(WRAP, '马克思', '马克思恩格斯全集', v, f) for f in fs], len(fs))
    for f in [os.path.join(WRAP, '马克思', '马克思恩格斯全集.html')] + [
              os.path.join(WRAP, '马克思', '马克思恩格斯全集', v + '.html') for v in vols]:
        if not os.path.exists(os.path.join(ROOT, f)):
            print('MISSING:', f); problems += 1
    print('== 马克思恩格斯全集 : %d 卷 %d 页' % (len(vols), n_pages))

# 2) 斯大林：两部著作的阅读页与导航页
st_reading = []
st_landings = []
for root2, _, fs in os.walk(os.path.join(ROOT, WRAP, '斯大林')):
    for f in fs:
        if f.endswith('.html') and 'index.html' not in f:
            fp = os.path.join(root2, f)
            html = open(fp, encoding='utf-8').read()
            if 'window.PAGE' in html:
                st_reading.append(os.path.relpath(fp, ROOT))
            else:
                st_landings.append(os.path.relpath(fp, ROOT))
print('== 斯大林 : %d 阅读页 + %d 导航页' % (len(st_reading), len(st_landings)))
check(st_reading, len(st_reading))
for f in st_landings:
    if not os.path.exists(os.path.join(ROOT, f)):
        print('MISSING:', f); problems += 1

# 3) 教员专题：仅校验含 window.PAGE 的阅读页；选节/选卷页只查存在
reading = []
landings = []
for root2, _, fs in os.walk(os.path.join(ROOT, WRAP, '教员', '专题')):
    for f in fs:
        if f.endswith('.html'):
            fp = os.path.join(root2, f)
            html = open(fp, encoding='utf-8').read()
            if 'window.PAGE' in html:
                reading.append(os.path.relpath(fp, ROOT))
            else:
                landings.append(os.path.relpath(fp, ROOT))
print('== 教员 / 专题 : %d 阅读页 + %d 导航页' % (len(reading), len(landings)))
check(reading, len(reading))
for f in landings:
    if not os.path.exists(os.path.join(ROOT, f)):
        print('MISSING:', f); problems += 1
for f in [os.path.join(WRAP, '教员', '专题.html')]:
    if not os.path.exists(os.path.join(ROOT, f)):
        print('MISSING:', f); problems += 1

# 3) 导师页与首页
for f in ['index.html', os.path.join(WRAP, '马克思', 'index.html'),
          os.path.join(WRAP, '恩格斯', 'index.html'),
          os.path.join(WRAP, '列宁', 'index.html'),
          os.path.join(WRAP, '斯大林', 'index.html'),
          os.path.join(WRAP, '教员', 'index.html'),
          os.path.join(WRAP, '马克思', '资本论.html'),
          os.path.join(WRAP, '教员', '毛选.html'),
          os.path.join(WRAP, '马克思', '马克思恩格斯全集', '第4卷', '45-共产党宣言.html'),
          os.path.join(WRAP, '教员', '毛选', '1', '01-中国社会各阶级的分析.html')]:
    if not os.path.exists(os.path.join(ROOT, f)):
        print('MISSING:', f); problems += 1

print('无脚注页（正常）:', NO_FNREF[0])
print('总问题数:', problems)
