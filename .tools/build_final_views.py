# -*- coding: utf-8 -*-
"""
build_final_views.py — 补齐最后三个「全集视图页」：
  · 斯大林《论列宁主义基础》         → 斯大林全集/第6卷/10-…
  · 斯大林《论辩证唯物主义和历史唯物主义》→ 斯大林全集/第14卷/53-…
  · 恩格斯《自然辩证法》            → 马克思恩格斯全集/第20卷/06-…（1971 第一版）
生成视图页、删除旧正文目录、把 manifest 里的自然辩证法标记为 view。
"""
import os, re, sys, io, json, shutil

ROOT = r'C:\导师文集'
sys.path.insert(0, os.path.join(ROOT, '.tools'))
from build_view_works import view_html  # noqa: E402  （其内部已设置 stdout 编码）

WRAP = os.path.join(ROOT, '导师著作')
MANIFEST = os.path.join(ROOT, '.tools', 'manifest.json')

VIEWS = [
    dict(author='斯大林', title='论列宁主义基础',
         prefix='斯大林全集',
         items=[(6, 10, '论列宁主义基础', '约·维·斯大林', '10-论列宁主义基础.html')]),
    dict(author='斯大林', title='论辩证唯物主义和历史唯物主义',
         prefix='斯大林全集',
         items=[(14, 53, '论辩证唯物主义和历史唯物主义', '约·维·斯大林', '53-论辩证唯物主义和历史唯物主义.html')]),
    dict(author='恩格斯', title='自然辩证法',
         prefix='../马克思/马克思恩格斯全集',
         items=[(20, 6, '自然辩证法', '弗·恩格斯', '06-自然辩证法.html')]),
]


def main():
    man = json.load(open(MANIFEST, encoding='utf-8'))
    for v in VIEWS:
        author, title = v['author'], v['title']
        out = os.path.join(WRAP, author, title + '.html')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(view_html(title, author, v['items'], v['prefix']))
        print('视图页 %s/%s.html（1 篇 → %s）' % (author, title, v['items'][0][4]))

        # 删除旧正文目录（严格限定在 导师著作/<author>/ 下）
        d = os.path.join(WRAP, author, title)
        if os.path.isdir(d):
            resolved = os.path.abspath(d)
            allowed = os.path.abspath(os.path.join(WRAP, author, ''))
            if resolved.startswith(allowed) and resolved != allowed.rstrip(os.sep):
                shutil.rmtree(resolved)
                print('  删除重复正文目录:', os.path.relpath(resolved, ROOT))
            else:
                print('  !! 跳过可疑路径', resolved)

        # manifest 标记
        for w in man['works']:
            if w['author'] == author and w['title'] == title and not w.get('view'):
                w['view'] = True
                w['view_of'] = v['prefix'].rsplit('/', 1)[-1] or v['prefix']
                w['note'] = '正文唯一存放于对应全集目录；本页仅为视图索引。'
                print('  manifest 标记 view:', title)

    json.dump(man, open(MANIFEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
