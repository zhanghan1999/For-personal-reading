# -*- coding: utf-8 -*-
"""
资本论拆分脚本：把三卷大页面按 <article class="chapter"> 拆成独立文章页。

输入：马克思/资本论/<n>/资本论-第<n>卷.html（旧版大页面）
输出：马克思/资本论/<n>/<序号>-<篇名>.html 独立页
同时生成：马克思/资本论.html 选卷页、马克思/index.html 导师页
"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集'
CAP = os.path.join(ROOT, '马克思', '资本论')
ASSETS_REL = '../../../assets'
HOME_REL = '../../../index.html'
VOLPAGE_REL = '../../资本论.html'

VOL_META = {
    1: {'mew': 23, 'year': '1972', 'sub': '资本的生产过程', 'range': '1867', 'vol_cn': '第一卷'},
    2: {'mew': 24, 'year': '1972', 'sub': '资本的流通过程', 'range': '1885', 'vol_cn': '第二卷'},
    3: {'mew': 25, 'year': '1974', 'sub': '资本主义生产的总过程', 'range': '1894', 'vol_cn': '第三卷'},
}

PAGE_SKELETON_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="{assets}/style.css">
</head>
<body>
<div id="progress"></div>

<aside id="toc">
  <h2>目　录</h2>
  <a class="backtop" href="{home}">&#9733; 首页</a>
  <a class="backtop" href="{volpage}" style="margin-left:10px">&#8678; 选卷</a>
  <input id="q" class="search" type="text" placeholder="搜索篇名…">
  <ul id="toclist"></ul>
</aside>
<div id="tocMask"></div>
<button id="tocCollapseBtn" title="收起目录">&#9664;</button>

<header id="topbar">
  <span class="brand">{brand}</span>
  <span class="voltag">{voltag}</span>
  <span class="spacer"></span>
  <a class="btn vol" href="{volpage}">{volLabel}</a>
  <button id="printBtn">打印</button>
</header>

<main id="main">
<span id="top"></span>
{article}
<footer>
  {footer}
</footer>
</main>

<button id="backtop" title="回到顶部">&#8593;</button>

<script>
window.PAGE = {page_json};
</script>
<script src="{assets}/app.js"></script>
</body>
</html>
'''


def safe_filename(title, idx):
    # title 可能是 "第一篇 商品和货币 第一章 商品" 形式，保留前 40 字符
    t = re.sub(r'[\\/:*?"<>|\n\r\t ]+', '', title)
    t = t.replace('?', '').replace('？', '').replace('．', '。')
    if len(t) > 44:
        t = t[:44]
    return '%02d-%s.html' % (idx, t or '无题')


def extract_articles(html):
    """把大页面按 article.chapter 拆开，返回 [(article_html, title)]。"""
    articles = []
    for m in re.finditer(r'<article id="c\d+" class="chapter">(.*?)</article>', html, flags=re.S):
        inner = m.group(1)
        # 提取标题（chapter-head h2）
        t = re.search(r'<h2>(.*?)</h2>', inner, flags=re.S)
        title = re.sub(r'<[^>]+>', '', t.group(1)).strip() if t else '无题'
        title = title.replace('\n', ' ').strip()
        articles.append((inner, title))
    return articles


def main():
    vol_stats = {}
    for vol in [1, 2, 3]:
        meta = VOL_META[vol]
        src = os.path.join(CAP, str(vol), '资本论-第%s卷.html' % vol)
        if not os.path.exists(src):
            print('SKIP missing', src)
            continue
        html = open(src, encoding='utf-8').read()
        articles = extract_articles(html)
        print('vol', vol, 'articles:', len(articles))
        outdir = os.path.join(CAP, str(vol))
        os.makedirs(outdir, exist_ok=True)
        # 先清掉旧的大页面（保留数据源？不删，重命名）
        # entries
        entries = []
        for i, (inner, title) in enumerate(articles, 1):
            fname = safe_filename(title, i)
            entries.append({'idx': i, 'title': title, 'fname': fname})
        toc_groups = [{'label': None, 'items': [
            {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries
        ]}]
        # 写每篇
        for i, (inner, title) in enumerate(articles, 1):
            fname = entries[i - 1]['fname']
            # 章节头改造：保留原 chapter-head，但保证 h2 为标题
            # 上/下一篇
            nav = '<div class="chapnav">'
            if i > 1:
                prev = entries[i - 2]
                nav += '<a href="%s"><span class="lbl">&#8592; 上一篇</span><span class="ttl">%s</span></a>' % (prev['fname'], prev['title'])
            else:
                nav += '<a href="#top"><span class="lbl">&#8592; 封面</span></a>'
            if i < len(entries):
                nxt = entries[i]
                nav += '<a href="%s" style="text-align:right"><span class="lbl">下一篇 &#8594;</span><span class="ttl">%s</span></a>' % (nxt['fname'], nxt['title'])
            else:
                nav += '<a href="%s" style="text-align:right"><span class="lbl">回到选卷 &#8594;</span></a>' % VOLPAGE_REL
            nav += '</div>'
            article_html = '<article id="c%d" class="chapter">\n%s\n%s\n</article>' % (i, inner, nav)
            page = {
                'brand': '资本论 · %s' % meta['vol_cn'],
                'voltag': '%s年版' % meta['year'],
                'homeHref': HOME_REL,
                'volHref': VOLPAGE_REL,
                'volLabel': '选卷',
                'tocGroups': toc_groups,
                'activeHref': fname,
                'searchPlaceholder': '搜索篇名…',
            }
            out = PAGE_SKELETON_HEAD.format(
                desc='《资本论》%s·%s' % (meta['vol_cn'], title),
                title='%s · 《资本论》%s' % (title, meta['vol_cn']),
                assets=ASSETS_REL,
                home=HOME_REL,
                volpage=VOLPAGE_REL,
                brand='资本论 · %s' % meta['vol_cn'],
                voltag='%s年版' % meta['year'],
                volLabel='选卷',
                article=article_html,
                footer='本文本整理自「中文马克思主义文库」镜像（marx-zh-cn.github.io）《马克思恩格斯全集》第一版第%d卷（%s年版，中央编译局译，人民出版社），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。' % (meta['mew'], meta['year']),
                page_json=json.dumps(page, ensure_ascii=False),
            )
            with open(os.path.join(outdir, fname), 'w', encoding='utf-8') as f:
                f.write(out)
        vol_stats[vol] = {'count': len(articles), 'meta': meta}
        # 旧大页面重命名保留
        old = os.path.join(CAP, str(vol), '资本论-第%s卷.html' % vol)
        new = os.path.join(CAP, str(vol), '合并版-第%s卷.html' % vol)
        if os.path.exists(old) and not os.path.exists(new):
            os.rename(old, new)
            print('  renamed old merged page ->', new)
    print('资本论拆分完成')


if __name__ == '__main__':
    main()
