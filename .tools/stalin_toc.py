# -*- coding: utf-8 -*-
"""抽取斯大林全集正卷 PDF 的书签目录 → JSON（卷 → 篇目 → 起始页）"""
import sys, json, os
sys.path.insert(0, '.tools/sources/stalin/_pylib')
import pypdf

r = pypdf.PdfReader('.tools/sources/stalin/pdf/斯大林全集_正卷20卷.pdf')
vols = []
cur_vol = None

def page_index(dest):
    try:
        return r.get_destination_page_number(dest) + 1
    except Exception:
        return None

def walk(items, depth=0):
    global cur_vol
    for it in items:
        if isinstance(it, list):
            walk(it, depth + 1)
            continue
        title = str(getattr(it, 'title', '')).strip()
        pg = page_index(it)
        if depth == 0 and (title[:2].isdigit() or '第' in title and '卷' in title):
            cur_vol = {'title': title, 'start': pg, 'articles': []}
            vols.append(cur_vol)
        elif cur_vol is not None and title:
            cur_vol['articles'].append({'title': title, 'page': pg})

walk(r.outline)
out = {'source': '新编《斯大林全集》正卷20卷（诸夏怀斯社版）', 'pages_total': len(r.pages), 'volumes': vols}
os.makedirs('.tools/sources/stalin', exist_ok=True)
json.dump(out, open('.tools/sources/stalin/_toc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('volumes:', len(vols))
for v in vols:
    print(f"  {v['title'][:40]:<42} start={v['start']:<5} articles={len(v['articles'])}")
