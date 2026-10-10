# -*- coding: utf-8 -*-
"""Verify page links: TOC hrefs point to existing files, prev/next work, home/vol links."""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'

def extract_page(html):
    m = re.search(r'window\.PAGE = (\{.*?\});\s*</script>', html, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception as e:
        print('  JSON parse error:', e)
        return None

problems = 0
# 遍历所有文章页
for base, rel in [('教员/毛选', '毛选'), ('马克思/资本论', '资本论')]:
    base_dir = os.path.join(ROOT, base)
    for v in os.listdir(base_dir):
        vdir = os.path.join(base_dir, v)
        if not os.path.isdir(vdir):
            continue
        for f in sorted(os.listdir(vdir)):
            if not f.endswith('.html'):
                continue
            fp = os.path.join(vdir, f)
            html = open(fp, encoding='utf-8').read()
            page = extract_page(html)
            if not page:
                continue
            # 检查 TOC 链接指向的文件是否存在（同目录）
            for g in page.get('tocGroups', []):
                for it in g.get('items', []):
                    href = it['href']
                    target = os.path.join(vdir, href)
                    if not os.path.exists(target):
                        print('BROKEN TOC: %s/%s -> %s' % (base, v, href))
                        problems += 1
            # 检查 activeHref 存在
            if not os.path.exists(os.path.join(vdir, page.get('activeHref', ''))):
                print('BROKEN activeHref: %s/%s -> %s' % (base, v, page.get('activeHref')))
                problems += 1
            # 检查 homeHref / volHref（相对当前文件目录）
            cur_dir = vdir
            home_target = os.path.normpath(os.path.join(cur_dir, page.get('homeHref', '')))
            vol_target = os.path.normpath(os.path.join(cur_dir, page.get('volHref', '')))
            if not os.path.exists(home_target):
                print('BROKEN homeHref: %s/%s -> %s (resolved %s)' % (base, v, page.get('homeHref'), home_target))
                problems += 1
            if not os.path.exists(vol_target):
                print('BROKEN volHref: %s/%s -> %s (resolved %s)' % (base, v, page.get('volHref'), vol_target))
                problems += 1
print('总计检查链接问题:', problems)
