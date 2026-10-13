# -*- coding: utf-8 -*-
"""build_indexes.py — 依据生成好的作品目录，重建五位导师的 index.html 与首页 index.html。"""
import os, json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集'
WRAP = '导师著作'
M = json.load(open(os.path.join(ROOT, '.tools', 'manifest.json'), encoding='utf-8'))['works']


def count_pages(work):
    d = os.path.join(ROOT, WRAP, work['author'], work['dir'])
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith('.html') and not f.startswith('合并')])


MENTOR_TPL = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1{namecls}>{name}</h1>
    <div class="sub">著作列表</div>
    <div class="meta"><a href="../../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>
'''

CARD = '''<a class="card" href="{href}">
  <div class="vol">{title}</div>
  <div class="stat">{stat}</div>
  <div class="go">进入著作 &#8594;</div>
</a>'''


def mentor_page(name, cards, footer='本页与各著作页面均为独立文件，可整体拷贝到其他电脑离线使用。'):
    namecls = ' class="fullname"' if len(name) > 6 else ''
    return MENTOR_TPL.format(desc='%s 著作' % name, title='%s · 著作' % name, name=name,
                             namecls=namecls, cards='\n'.join(cards), footer=footer)


def build_author(full_name, author_key, extra):
    cards = []
    for w in M:
        if w['author'] != author_key:
            continue
        n = count_pages(w)
        cards.append(CARD.format(href=w['landing'], title=w['title'],
                                 stat='%d 篇' % n))
    cards += extra
    return mentor_page(full_name, cards)


def main():
    # 马克思：资本论 + 新增
    cards_marx = [CARD.format(href='资本论.html', title='资本论', stat='全三卷 · 109 篇文章')]
    page = build_author('卡尔·马克思', '马克思', cards_marx)
    open(os.path.join(ROOT, WRAP, '马克思', 'index.html'), 'w', encoding='utf-8').write(page)

    # 恩格斯
    page = build_author('弗里德里希·恩格斯', '恩格斯', [])
    open(os.path.join(ROOT, WRAP, '恩格斯', 'index.html'), 'w', encoding='utf-8').write(page)

    # 列宁
    page = build_author('弗拉基米尔·伊里奇·列宁', '列宁', [])
    open(os.path.join(ROOT, WRAP, '列宁', 'index.html'), 'w', encoding='utf-8').write(page)

    # 斯大林：两篇均已入库
    stalin_cards = [
        CARD.format(href='论列宁主义基础.html', title='论列宁主义基础',
                    stat='引言 + 九节 · 在斯维尔德洛夫大学的讲演（1924）'),
        CARD.format(href='论辩证唯物主义和历史唯物主义.html', title='论辩证唯物主义和历史唯物主义',
                    stat='全文 1 篇 · 《联共（布）党史简明教程》第四章第二节'),
    ]
    stalin_html = mentor_page('约瑟夫·维萨里奥诺维奇·斯大林', stalin_cards)
    open(os.path.join(ROOT, WRAP, '斯大林', 'index.html'), 'w', encoding='utf-8').write(stalin_html)

    # 教员：毛选 + 军事文集 + 专题
    mao_cards = [
        CARD.format(href='毛选.html', title='毛泽东选集', stat='全五卷 · 230 篇文章'),
        CARD.format(href='军事文集.html', title='毛泽东军事文集', stat='六卷 · 1612 篇 · 1927—1972 年军事著作'),
        CARD.format(href='专题.html', title='毛泽东思想经典篇目', stat='实践论 · 矛盾论 · 中国革命战争的战略问题 · 论持久战'),
    ]
    open(os.path.join(ROOT, WRAP, '教员', 'index.html'), 'w', encoding='utf-8').write(
        mentor_page('毛泽东', mao_cards))

    # 首页
    home = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="导师文集 · 经典著作在线阅读">
<title>导师文集 · 首页</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>导师文集</h1>
    <div class="sub quote">“我正式劝同志们读一点书，免得受知识分子的骗。”<br><span class="attr">—— 毛泽东</span></div>
    <div class="meta">头像图片待补充 · 点击人物进入其著作</div>
  </header>

  <div class="zone-title">导 师 著 作</div>
  <main class="mentor-grid">

<a class="mentor-card" href="导师著作/马克思/index.html">
  <div class="avatar"><span class="ph">马</span></div>
  <div class="name fullname">卡尔·马克思</div>
  <div class="works">《资本论》全三卷 · 共产党宣言 · 政治经济学批判</div>
  <div class="go">进入著作 &#8594;</div>
</a>

<a class="mentor-card" href="导师著作/恩格斯/index.html">
  <div class="avatar"><span class="ph">恩</span></div>
  <div class="name fullname">弗里德里希·恩格斯</div>
  <div class="works">反杜林论 · 自然辩证法 · 社会主义从空想到科学的发展 等</div>
  <div class="go">进入著作 &#8594;</div>
</a>

<a class="mentor-card" href="导师著作/列宁/index.html">
  <div class="avatar"><span class="ph">列</span></div>
  <div class="name fullname">弗拉基米尔·伊里奇·列宁</div>
  <div class="works">帝国主义是资本主义的最高阶段 · 国家与革命 · “左派”幼稚病 等</div>
  <div class="go">进入著作 &#8594;</div>
</a>

<a class="mentor-card" href="导师著作/斯大林/index.html">
  <div class="avatar"><span class="ph">斯</span></div>
  <div class="name fullname">约瑟夫·维萨里奥诺维奇·斯大林</div>
  <div class="works">论列宁主义基础 · 论辩证唯物主义和历史唯物主义</div>
  <div class="go">进入著作 &#8594;</div>
</a>

<a class="mentor-card" href="导师著作/教员/index.html">
  <div class="avatar"><span class="ph">毛</span></div>
  <div class="name">毛泽东</div>
  <div class="works">《毛泽东选集》全五卷 · 军事文集六卷 · 经典篇目专题</div>
  <div class="go">进入著作 &#8594;</div>
</a>

  </main>

  <div class="zone-title">其 他 著 作</div>
  <div class="mentor-grid">

<a class="mentor-card" href="其他著作/埃德加·斯诺/index.html">
  <div class="avatar"><span class="ph">斯</span></div>
  <div class="name fullname">埃德加·斯诺</div>
  <div class="works">《红星照耀中国（西行漫记）》· 1937 年报道中共苏区与红军的纪实经典</div>
  <div class="go">进入阅读 &#8594;</div>
</a>

  </div>

  <footer>
    头像图片待补充，替换 <code>assets/</code> 下对应头像即可更新首页。<br>
    本页与各著作页面均为独立文件，可整体拷贝到其他电脑离线使用。
  </footer>
</div>
</body>
</html>'''
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(home)
    print('indexes done')


if __name__ == '__main__':
    main()
