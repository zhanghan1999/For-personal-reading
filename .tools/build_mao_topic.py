# -*- coding: utf-8 -*-
"""
build_mao_topic.py — 从《毛选》parsed.json 提取四篇名著，生成独立「专题」阅读区。
不动毛选目录。

专题结构：
  教员/专题.html                       专题首页（4 篇卡片）
  教员/专题/实践论.html                全文单页
  教员/专题/矛盾论.html                选节页 + 矛盾论/01..07
  教员/专题/中国革命战争的战略问题.html 选章页 + 中国革命战争的战略问题/01..05
  教员/专题/持久战.html                选节页 + 持久战/01..21
"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
MAO = os.path.join(ROOT, '教员')
TOPIC = os.path.join(MAO, '专题')

CIRCLED = {
    '①':'1','②':'2','③':'3','④':'4','⑤':'5','⑥':'6','⑦':'7','⑧':'8','⑨':'9','⑩':'10',
    '⑪':'11','⑫':'12','⑬':'13','⑭':'14','⑮':'15','⑯':'16','⑰':'17','⑱':'18','⑲':'19','⑳':'20',
}
PAREN = {
    '⑴':'1','⑵':'2','⑶':'3','⑷':'4','⑸':'5','⑹':'6','⑺':'7','⑻':'8','⑼':'9','⑽':'10',
    '⑾':'11','⑿':'12','⒀':'13','⒁':'14','⒂':'15','⒃':'16','⒄':'17','⒅':'18','⒆':'19','⒇':'20',
}


def safe_filename(title, idx):
    t = re.sub(r'[\\/:*?"<>|\n\r\t ]+', '', title)
    t = t.replace('?', '').replace('？', '')
    if len(t) > 40:
        t = t[:40]
    return '%02d-%s.html' % (idx, t or '无题')


def convert_refs(text, prefix):
    """⑴-⒇ → sup.fnref，目标 id 形如 {prefix}n<序号>。"""
    def rep(m):
        n = PAREN[m.group(0)]
        return '<sup class="fnref"><a href="#%sn%s">[%s]</a></sup>' % (prefix, n, n)
    return re.sub(r'[⑴-⒇]', rep, text)


def parse_notes(notes, prefix):
    items = []
    for nt in notes:
        m = re.match(r'〔(\d+)〕(.*)', nt, flags=re.S)
        if m:
            n, body = m.group(1), m.group(2).strip()
            items.append({'num': n, 'html': '<p class="note" id="%sn%s">[%s]&ensp;%s</p>' % (prefix, n, n, body)})
        else:
            items.append({'num': None, 'html': '<p class="note">%s</p>' % nt.strip()})
    return items


def load_article(vol, title):
    data = json.load(open(os.path.join(MAO, '毛选', '来源数据', '卷%s数据' % vol, 'parsed.json'), encoding='utf-8'))
    for a in data['articles']:
        if a['title'] == title:
            return data, a
    raise KeyError(title)


def build_topic_pages(work):
    """生成一个专题作品的页面，返回 (landing_cards, ) 元信息。"""
    data, article = load_article(work['vol'], work['mao_title'])
    date, headnote = None, None
    blocks = []  # [(kind, text)]  kind in p/h
    for item in article['content']:
        if not isinstance(item, list) or len(item) < 2:
            continue
        typ, txt = item[0], item[1]
        if typ == 'date':
            date = txt.strip()
        elif typ == 'headnote':
            headnote = re.sub(r'\s+', ' ', txt).strip()
        elif typ == 'p':
            blocks.append(('p', txt.strip()))
        elif typ == 'h':
            blocks.append(('h', txt.strip()))

    prefix = work['prefix']
    notes = parse_notes(article.get('notes', []), prefix)

    # —— 分页 ——
    # 若整篇只有开头一个 h 且其不是“第X章/一/二/（一）”这类节题 → 视为副标题，单页
    h_idx = [i for i, b in enumerate(blocks) if b[0] == 'h']
    subtitle = None
    if len(h_idx) == 1 and h_idx[0] == 0:
        first_h = blocks[0][1]
        if not re.match(r'^(第[一二三四五六七八九十百]+章|[一二三四五六七八九十]+、|（[一二三四五六七八九十]+）)', first_h):
            subtitle = first_h
            blocks = blocks[1:]

    pages = []  # [{title, body: [(kind,html)], refs:set}]
    cur = None
    for kind, txt in blocks:
        if kind == 'h':
            if re.match(r'^第[一二三四五六七八九十百]+节', txt):
                # “第X节”作为当前章内的小节标题，不另起一页
                if cur is None:
                    cur = {'title': '引言', 'body': []}
                cur['body'].append(('h3', txt))
                continue
            if cur is not None:
                pages.append(cur)
            cur = {'title': txt, 'body': []}
        else:
            if cur is None:
                cur = {'title': '引言', 'body': []}
            html = convert_refs(txt, prefix)
            cur['body'].append(('p', html))
    if cur is not None:
        pages.append(cur)

    # 单页作品（副标题情形）：页面标题用作品名
    if subtitle and len(pages) == 1:
        pages[0]['title'] = work['title']

    # 引用统计 → 分配注释到页
    for i, pg in enumerate(pages):
        refs = set()
        for kind, html in pg['body']:
            for m in re.finditer(r'href="#%sn(\d+)"' % prefix, html):
                refs.add(m.group(1))
        pg['refs'] = refs
    last_idx = len(pages) - 1
    for nt in notes:
        if nt['num'] is None:
            continue
        target = None
        for i, pg in enumerate(pages):
            if nt['num'] in pg['refs']:
                target = i
                break
        if target is None:
            target = last_idx
        pages[target].setdefault('notes', []).append(nt['html'])

    # —— 渲染页面 ——
    work_dir = os.path.join(TOPIC, work['topic_dir']) if len(pages) > 1 else TOPIC
    vol_href = '../%s' % work['landing'] if len(pages) > 1 else '../专题.html'  # landing 已含 .html
    brand = work['title']
    voltag = work['voltag']
    footer = work['footer']
    # 多页作品页位于 教员/专题/<作品>/NN.html（4 级），单页作品位于 教员/专题/<作品>.html（3 级）
    assets = '../../../assets' if len(pages) > 1 else '../../assets'
    home = '../../../index.html' if len(pages) > 1 else '../../index.html'

    entries = []
    for i, pg in enumerate(pages, 1):
        title = pg['title']
        if len(pages) == 1:
            # 单篇作品直接以标题命名（与选卷页 landing 同名）
            fname = re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', title) + '.html'
        else:
            fname = safe_filename(title, i)
        entries.append({'idx': i, 'title': title, 'fname': fname})

    toc_groups = [{'label': None, 'items': [
        {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries
    ]}]

    os.makedirs(work_dir, exist_ok=True)
    for i, pg in enumerate(pages, 1):
        e = entries[i - 1]
        prev = entries[i - 2] if i > 1 else None
        nxt = entries[i] if i < len(entries) else None
        result = {
            'title': pg['title'],
            'secdate': '',
            'body': [{'kind': kind, 'html': html} for kind, html in pg['body']],
            'notes': ([{'header': '注　释', 'items': pg.get('notes', [])}] if pg.get('notes') else []),
        }
        if i == 1:
            sec = []
            if subtitle:
                sec.append(subtitle)
            if date:
                sec.append(date)
            result['secdate'] = '<br>\n'.join(sec)
            if headnote:
                result['headnote'] = headnote
        page_html = render_article(
            result, art_idx=1, brand=brand, voltag=voltag,
            toc_groups=toc_groups, active_href=e['fname'],
            prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
            nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
            vol_href=vol_href, footer=footer, home_href=home, assets=assets,
        )
        out = os.path.join(work_dir, e['fname'])
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page_html)
        print('  wrote', os.path.relpath(out, ROOT))

    # —— 选节/选章页（位于 教员/专题/<landing>.html，阅读页在 教员/专题/<topic_dir>/，链接需带目录前缀）——
    if len(pages) > 1:
        cards = []
        for i, e in enumerate(entries, 1):
            cards.append('''<a class="card" href="{href}">
  <div class="vol">{vol}</div>
  <div class="ed">{ed}</div>
  <div class="stat">{stat}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(
                href='%s/%s' % (work['topic_dir'], e['fname']),
                vol='第%d节' % i if work.get('unit') == '节' else '第%d章' % i,
                ed=work.get('edition', ''),
                stat=e['title'],
            ))
        landing = build_work_landing(work['title'], work.get('sub', ''), cards, work['footer'])
        with open(os.path.join(TOPIC, work['landing']), 'w', encoding='utf-8') as f:
            f.write(landing)
        print('  wrote', os.path.relpath(os.path.join(TOPIC, work['landing']), ROOT))
        return {'href': work['landing'], 'title': work['title'],
                'ed': work.get('edition', ''), 'range': work.get('range', ''),
                'stat': '%d 篇' % len(pages)}
    else:
        return {'href': work['landing'], 'title': work['title'],
                'ed': work.get('edition', ''), 'range': work.get('range', ''),
                'stat': '全文 1 篇'}


def build_work_landing(title, sub, cards, footer):
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{title} 选节首页">
<title>{title} · 选节首页</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 毛 泽 东 思 想 经 典 篇 目</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>{title}</h1>
    <div class="sub">{sub}</div>
    <div class="meta"><a href="../专题.html">&#8678; 返回专题</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>'''.format(title=title, sub=sub, cards='\n'.join(cards), footer=footer)


def build_topic_index(works):
    cards = []
    for w in works:
        cards.append('''<a class="card" href="专题/{href}">
  <div class="vol">{title}</div>
  <div class="ed">{ed}</div>
  <div class="stat">{stat}</div>
  <div class="range">{range}</div>
  <div class="go">进入阅读 &#8594;</div>
</a>'''.format(**w))
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="毛泽东思想经典篇目专题">
<title>毛泽东思想经典篇目 · 专题</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>毛泽东思想经典篇目</h1>
    <div class="sub">单 篇 名 著 专 题</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    本专题各篇选自《毛泽东选集》第一、二卷，文本整理自「毛泽东博览」（www.mzdbl.cn），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。《毛泽东选集》全五卷仍保留于「毛选」栏目，可随时对照阅读。
  </footer>
</div>
</body>
</html>'''.format(cards='\n'.join(cards))
    with open(os.path.join(TOPIC, '..', '专题.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('  wrote 教员/专题.html')


def main():
    works = [
        {
            'vol': 1, 'mao_title': '实践论', 'prefix': 'sj',
            'title': '实践论', 'topic_dir': '实践论', 'landing': '实践论.html',
            'voltag': '选自《毛泽东选集》第一卷', 'edition': '1952年版',
            'range': '1937 年 7 月', 'sub': '论认识和实践的关系——知和行的关系',
            'footer': '本篇选自《毛泽东选集》第一卷（1952年版），文本整理自「毛泽东博览」（www.mzdbl.cn），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。',
        },
        {
            'vol': 1, 'mao_title': '矛盾论', 'prefix': 'md',
            'title': '矛盾论', 'topic_dir': '矛盾论', 'landing': '矛盾论.html',
            'voltag': '选自《毛泽东选集》第一卷', 'edition': '1952年版',
            'range': '1937 年 8 月', 'sub': '七 节', 'unit': '节',
            'footer': '本篇选自《毛泽东选集》第一卷（1952年版），文本整理自「毛泽东博览」（www.mzdbl.cn），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。',
        },
        {
            'vol': 1, 'mao_title': '中国革命战争的战略问题', 'prefix': 'zz',
            'title': '中国革命战争的战略问题', 'topic_dir': '中国革命战争的战略问题',
            'landing': '中国革命战争的战略问题.html',
            'voltag': '选自《毛泽东选集》第一卷', 'edition': '1952年版',
            'range': '1936 年 12 月', 'sub': '五 章', 'unit': '章',
            'footer': '本篇选自《毛泽东选集》第一卷（1952年版），文本整理自「毛泽东博览」（www.mzdbl.cn），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。',
        },
        {
            'vol': 2, 'mao_title': '论持久战', 'prefix': 'cj',
            'title': '论持久战', 'topic_dir': '持久战', 'landing': '持久战.html',
            'voltag': '选自《毛泽东选集》第二卷', 'edition': '1952年版',
            'range': '1938 年 5 月', 'sub': '二十一 节', 'unit': '节',
            'footer': '本篇选自《毛泽东选集》第二卷（1952年版），文本整理自「毛泽东博览」（www.mzdbl.cn），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。',
        },
    ]
    results = []
    for w in works:
        print('== 教员 / %s' % w['title'])
        results.append(build_topic_pages(w))
    build_topic_index(results)
    print('专题完成')


if __name__ == '__main__':
    main()
