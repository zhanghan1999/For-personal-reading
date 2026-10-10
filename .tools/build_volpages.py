# -*- coding: utf-8 -*-
"""
生成选卷页 / 导师页 / 占位页。
- 选卷页：列出该导师所有著作/卷次卡片（如 教员/毛选.html）
- 导师页：某导师的入口页（如 教员/index.html）
- 占位页：暂无著作的导师
"""
import os, json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集'

def count_articles(vol_dir):
    """统计一个卷目录下有多少文章页（*.html，排除 index）。"""
    n = 0
    chars = 0
    if os.path.isdir(vol_dir):
        for f in os.listdir(vol_dir):
            if f.endswith('.html'):
                n += 1
    return n

VOL_CN = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']

def build_vol_page(mentor, title, subtitle, home_rel, vols, footnote):
    """vols: [{num, cn, edition, stat, range, first_page}]"""
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
<meta name="description" content="{title} 选卷首页">
<title>{title} · 选卷首页</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>{title}</h1>
    <div class="sub">{subtitle}</div>
    <div class="meta"><a href="{home}">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footnote}
  </footer>
</div>
</body>
</html>'''.format(title=title, subtitle=subtitle, home=home_rel,
               cards='\n'.join(cards), footnote=footnote)
    return html


def build_mentor_page(mentor, name, works_list, home_rel, footnote, avatar=''):
    """works_list: [{title, href, desc}]"""
    cards = []
    for w in works_list:
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
<meta name="description" content="{name} 著作">
<title>{name} · 著作</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>{name}</h1>
    <div class="sub">著作列表</div>
    <div class="meta"><a href="{home}">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footnote}
  </footer>
</div>
</body>
</html>'''.format(name=name, home=home_rel, cards='\n'.join(cards), footnote=footnote)
    return html


def build_placeholder(mentor, name, home_rel, avatar=''):
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{name} 著作整理中">
<title>{name} · 著作整理中</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="placeholder">
  <div class="avatar"><span>{ph}</span></div>
  <h1>{name}</h1>
  <p>该导师的著作正在整理中，敬请期待。</p>
  <a class="back" href="{home}">&#8678; 返回首页</a>
</div>
</body>
</html>'''.format(name=name, ph=mentor, home=home_rel)
    return html


def main():
    # ============ 毛选选卷页 ============
    maoxuan_vols = []
    for v in [1, 2, 3, 4, 5]:
        vol_dir = os.path.join(ROOT, '教员', '毛选', str(v))
        n = count_articles(vol_dir)
        edition = {1: '1952年版', 2: '1952年版', 3: '1952年版', 4: '1960年版', 5: '1977年版'}[v]
        period = {1: '1925—1937', 2: '1937—1941', 3: '1941—1945', 4: '1945—1949', 5: '1949—1957'}[v]
        # first article file
        files = sorted(f for f in os.listdir(vol_dir) if f.endswith('.html'))
        first = files[0] if files else '#'
        maoxuan_vols.append({
            'num': VOL_CN[v], 'cn': v, 'edition': edition,
            'stat': '%d 篇文章' % n, 'range': period,
            'first': '毛选/%d/%s' % (v, first),
        })
    maoxuan_page = build_vol_page(
        '教员', '毛泽东选集', '全 五 卷', '../index.html', maoxuan_vols,
        '文本整理自「毛泽东博览」（www.mzdbl.cn），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。')
    os.makedirs(os.path.join(ROOT, '教员'), exist_ok=True)
    with open(os.path.join(ROOT, '教员', '毛选.html'), 'w', encoding='utf-8') as f:
        f.write(maoxuan_page)
    print('wrote 教员/毛选.html')

    # ============ 教员导师页 ============
    mao_works = [{
        'title': '毛泽东选集',
        'href': '毛选.html',
        'desc': '全五卷 · 230 篇文章',
    }]
    mao_mentor = build_mentor_page('教员', '毛泽东', mao_works, '../index.html',
                                   '本页与各著作页面均为独立文件，可整体拷贝到其他电脑离线使用。')
    with open(os.path.join(ROOT, '教员', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(mao_mentor)
    print('wrote 教员/index.html')

    # ============ 占位页 ============
    for mentor, name in [('恩', '恩格斯'), ('列', '列宁'), ('斯', '斯大林')]:
        d = os.path.join(ROOT, mentor_map(mentor))
        os.makedirs(d, exist_ok=True)
        ph = build_placeholder(mentor, name, '../index.html')
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(ph)
        print('wrote %s/index.html' % mentor_map(mentor))


def mentor_map(ph):
    return {'恩': '恩格斯', '列': '列宁', '斯': '斯大林'}[ph]


if __name__ == '__main__':
    main()
