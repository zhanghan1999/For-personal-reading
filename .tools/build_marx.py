# -*- coding: utf-8 -*-
"""生成马克思的选卷页（资本论.html）与导师页（index.html）。"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集'
CAP = os.path.join(ROOT, '马克思', '资本论')

VOL_META = {
    1: {'mew': 23, 'year': '1972', 'sub': '资本的生产过程', 'range': '1867', 'vol_cn': '第一卷'},
    2: {'mew': 24, 'year': '1972', 'sub': '资本的流通过程', 'range': '1885', 'vol_cn': '第二卷'},
    3: {'mew': 25, 'year': '1974', 'sub': '资本主义生产的总过程', 'range': '1894', 'vol_cn': '第三卷'},
}

def count_articles(vol_dir):
    n = 0
    if os.path.isdir(vol_dir):
        for f in os.listdir(vol_dir):
            if f.endswith('.html') and not f.startswith('合并'):
                n += 1
    return n

def build_vol_page(vols, footnote):
    cards = []
    for v in vols:
        cards.append('''<a class="card" href="{first}">
  <div class="vol">第{cn}卷</div>
  <div class="ed">{edition}</div>
  <div class="stat">{stat}</div>
  <div class="range">{range}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(**v))
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《资本论》三卷选卷首页">
<title>《资本论》全三卷 · 选卷首页</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>资本论</h1>
    <div class="sub">全 三 卷</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footnote}
  </footer>
</div>
</body>
</html>'''.format(cards='\n'.join(cards), footnote=footnote)
    return html

def build_mentor_page(works, footnote):
    cards = []
    for w in works:
        cards.append('''<a class="card" href="{href}">
  <div class="vol">{title}</div>
  <div class="stat">{desc}</div>
  <div class="go">进入著作 &#8594;</div>
</a>'''.format(**w))
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="马克思 著作">
<title>马克思 · 著作</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>马克思</h1>
    <div class="sub">著作列表</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footnote}
  </footer>
</div>
</body>
</html>'''.format(cards='\n'.join(cards), footnote=footnote)
    return html

def main():
    vols = []
    for v in [1, 2, 3]:
        meta = VOL_META[v]
        n = count_articles(os.path.join(CAP, str(v)))
        files = sorted(f for f in os.listdir(os.path.join(CAP, str(v)))
                       if f.endswith('.html') and not f.startswith('合并'))
        first = files[0] if files else '#'
        vols.append({
            'cn': v, 'edition': '%s年版' % meta['year'],
            'stat': '%s · %d 篇' % (meta['sub'], n),
            'range': '%s 年出版 · 《马克思恩格斯全集》第%d卷' % (meta['range'], meta['mew']),
            'first': '资本论/%d/%s' % (v, first),
        })
    page = build_vol_page(vols,
        '文本整理自「中文马克思主义文库」镜像（marx-zh-cn.github.io）《马克思恩格斯全集》第一版第23—25卷（1972年版，中央编译局译，人民出版社出版），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。')
    with open(os.path.join(ROOT, '马克思', '资本论.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    print('wrote 马克思/资本论.html')

    works = [{
        'title': '资本论',
        'href': '资本论.html',
        'desc': '全三卷 · 109 篇文章',
    }]
    mentor = build_mentor_page(works,
        '本页与各著作页面均为独立文件，可整体拷贝到其他电脑离线使用。')
    with open(os.path.join(ROOT, '马克思', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(mentor)
    print('wrote 马克思/index.html')

if __name__ == '__main__':
    main()
