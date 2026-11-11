# -*- coding: utf-8 -*-
"""
build_view_works.py — 通用「全集视图页」构建器。

对 manifest 中指定的作品：正文不再单独存放，选卷页的卡片直接指向
《马克思恩格斯全集》对应卷的同一批文件（全集唯一正文）。

用法：
  python .tools/build_view_works.py            # 马克思(4) + 恩格斯(5)
"""
import os, re, sys, io, json, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'
WRAP = os.path.join(ROOT, '导师著作')
MAP_PATH = os.path.join(ROOT, '.tools', 'mew_full_map.json')
MANIFEST = os.path.join(ROOT, '.tools', 'manifest.json')

KICKER = {'马克思': '导 师 文 集 · 卡 尔 · 马 克 思',
          '恩格斯': '导 师 文 集 · 弗 里 德 里 希 · 恩 格 斯',
          '斯大林': '导 师 文 集 · 约 瑟 夫 · 斯 大 林'}

FOOTER = ('本篇正文收录于《马克思恩格斯全集》中文版（人民出版社）；此处仅为视图索引，'
          '正文唯一存放于全集正文目录。仅作学习、研究参考之用。')

# 需要转成视图页的恩格斯作品（自然辩证法源出《马恩全集》第二版第26卷，暂不并入）
ENGELS_VIEWS = ['社会主义从空想到科学的发展', '家庭、私有制和国家的起源',
                '路德维希·费尔巴哈和德国古典哲学的终结', '反杜林论', '英国工人阶级状况']


def load_map():
    m = json.load(open(MAP_PATH, encoding='utf-8'))
    idx = {}
    for v in m['volumes']:
        for a in v['articles']:
            idx[a['src']] = {'vol': v['vol'], 'fname': a['fname'], 'title': a['title'],
                             'author': a['author'], 'idx': a['idx']}
    return idx


def view_html(title, author, items, set_prefix, back='index.html'):
    """items: [(vol, idx, title, author, fname)]，set_prefix 形如 '马克思恩格斯全集' 或 '../马克思/马克思恩格斯全集'"""
    cards = []
    for vol, n, t, au, fname in items:
        cards.append('''<a class="card" href="{href}">
  <div class="vol">第 {n} 篇 · 第{vol}卷</div>
  <div class="ed">{author}</div>
  <div class="stat">{title}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(href='%s/第%d卷/%s' % (set_prefix, vol, fname), n=n, vol=vol,
                author=au or '&nbsp;', title=t))
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title} · 视图索引</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">{kicker}</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>{title}</h1>
    <div class="sub">共 {n} 篇 · 正文见《马克思恩格斯全集》第{vols}卷</div>
    <div class="meta"><a href="{back}">&#8678; 返回{author}</a> · <a href="{setpage}">&#8678; 全集</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>'''.format(desc='%s 视图索引（正文见《马克思恩格斯全集》）' % title,
                 title=title, kicker=KICKER.get(author, ''),
                 n=len(items),
                 vols='—'.join(sorted(set(str(i[0]) for i in items), key=int)),
                 back=back, author=author,
                 setpage=set_prefix + '.html',
                 cards='\n'.join(cards), footer=FOOTER)


def main():
    idx = load_map()
    man = json.load(open(MANIFEST, encoding='utf-8'))['works']
    by_title = {(w['author'], w['title']): w for w in man}

    todo = []
    for t in ('共产党宣言', '关于费尔巴哈的提纲', '政治经济学批判'):
        todo.append(('马克思', t, '马克思恩格斯全集'))
    for t in ENGELS_VIEWS:
        todo.append(('恩格斯', t, '../马克思/马克思恩格斯全集'))

    touched = {'马克思': [], '恩格斯': []}
    for author, title, prefix in todo:
        w = by_title.get((author, title))
        if not w:
            print('!! manifest 里没有：', author, title)
            continue
        items, missing = [], []
        for sf in w['source_files']:
            a = idx.get(os.path.basename(sf['path']))
            if not a:
                missing.append(os.path.basename(sf['path']))
                continue
            items.append((a['vol'], a['idx'], a['title'], a['author'], a['fname']))
        if missing:
            print('!! %s 有未映射源文件，跳过：%s' % (title, missing))
            continue
        if not items:
            continue
        out = os.path.join(WRAP, author, title + '.html')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(view_html(title, author, items, prefix))
        print('视图页 %s/%s.html（%d 篇，第%s卷）' % (
            author, title, len(items), '、'.join(sorted(set(str(i[0]) for i in items), key=int))))
        touched[author].append((title, len(items)))

        d = os.path.join(WRAP, author, w['dir'])
        if os.path.isdir(d):
            resolved = os.path.abspath(d)
            allowed = os.path.abspath(os.path.join(WRAP, author, ''))
            if resolved.startswith(allowed) and resolved != allowed.rstrip(os.sep):
                shutil.rmtree(resolved)
                print('  删除重复正文目录:', os.path.relpath(resolved, ROOT))
            else:
                print('  !! 跳过可疑路径', resolved)

    # 更新人物页卡片说明
    for author, items in touched.items():
        p = os.path.join(WRAP, author, 'index.html')
        if not os.path.exists(p):
            continue
        html = open(p, encoding='utf-8').read()
        for title, n in items:
            html = re.sub(
                r'(<a class="card" href="%s\.html">\s*<div class="vol">%s</div>\s*<div class="stat">)[^<]*(</div>)' % (
                    re.escape(title), re.escape(title)),
                r'\g<1>%d 篇（全集视图）\g<2>' % n, html)
        if author == '马克思' and '马克思恩格斯全集.html' not in html:
            html = html.replace('  <main class="cards">\n', '''  <main class="cards">
<a class="card" href="马克思恩格斯全集.html">
  <div class="vol">马克思恩格斯全集</div>
  <div class="stat">全 50 卷 · 6883 篇 · 1833—1895</div>
  <div class="go">进入全集 &#8594;</div>
</a>
''', 1)
        if author == '恩格斯' and '马克思恩格斯全集.html' not in html:
            html = html.replace('  <main class="cards">\n', '''  <main class="cards">
<a class="card" href="../马克思/马克思恩格斯全集.html">
  <div class="vol">马克思恩格斯全集</div>
  <div class="stat">全 50 卷 · 6883 篇 · 1833—1895</div>
  <div class="go">进入全集 &#8594;</div>
</a>
''', 1)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(html)
        print('已更新', os.path.relpath(p, ROOT))


if __name__ == '__main__':
    main()
