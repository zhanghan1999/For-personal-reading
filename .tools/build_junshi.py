# -*- coding: utf-8 -*-
"""
build_junshi.py — 从 mzdbl.cn 的《毛泽东军事文集》六卷文本（GBK txt）
生成站点页面：
  教员/军事文集.html               主选卷页（6 张卷卡片 → 各卷选卷页）
  教员/军事文集/第X卷.html         卷选卷页（该卷全部文章卡片）
  教员/军事文集/第X卷/NN-标题.html 文章页（侧栏仅当前篇 ±30 邻篇，全链上下篇）
"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
SRC = r'C:\导师文集\.tools\sources\mzdbl'
MAO = os.path.join(ROOT, '教员')
OUT = os.path.join(MAO, '军事文集')
WIN = 30  # 侧栏邻篇窗口

VOLS = [
    {'no': 1, 'period': '土地革命战争时期（1927年8月—1937年7月）'},
    {'no': 2, 'period': '抗日战争时期（1937年7月—1945年8月）'},
    {'no': 3, 'period': '解放战争时期（1945年8月—1949年9月）'},
    {'no': 4, 'period': '建国初期与抗美援朝时期（1949年9月—1953年12月）'},
    {'no': 5, 'period': '社会主义革命和建设时期（1954年—1958年）'},
    {'no': 6, 'period': '社会主义革命和建设时期（1959年—1972年）'},
]

DATE_RE = re.compile(r'^（\s*一九[一二三四五六七八九十〇○●零]*\d*\s*年.*）\s*$')
NOTE_REF_RE = re.compile(r'〔\s*(\d+)\s*〕')


def gbk(path):
    raw = open(path, 'rb').read()
    return raw.decode('gb18030', errors='replace')


def parse_article(txt):
    lines = [ln.rstrip() for ln in txt.splitlines()]
    title_lines = []
    date = ''
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if DATE_RE.match(s):
            date = re.sub(r'[（)）]', '', s).strip()
            i += 1
            break
        title_lines.append(s)
        i += 1
    title = '　'.join(title_lines) if title_lines else '(无题)'
    title = re.sub(r'〔\s*\d+\s*〕', '', title).strip()

    body_lines = []
    in_notes = False
    notes_raw = []
    for ln in lines[i:]:
        s = ln.strip()
        if not s:
            continue
        if re.match(r'^注\s*[释釋]\s*$', s):
            in_notes = True
            continue
        if in_notes:
            notes_raw.append(s)
        else:
            body_lines.append(ln)
    notes = []
    for s in notes_raw:
        m = re.match(r'^〔?\s*(\d+)\s*〕?\s*(.*)$', s)
        if m:
            notes.append((int(m.group(1)), m.group(2).strip()))
        else:
            if notes:
                notes[-1] = (notes[-1][0], notes[-1][1] + s)
    paras = []
    cur = []
    for ln in body_lines:
        if re.match(r'^[\u3000　 ]{2,}', ln) or re.match(r'^ {4,}', ln):
            if cur:
                paras.append(''.join(cur))
            cur = [ln.strip()]
        else:
            cur.append(ln.strip())
    if cur:
        paras.append(''.join(cur))
    sig = ''
    kept = []
    for p in paras:
        if re.match(r'^根据(.{0,80}刊印。?)$', p) and len(p) < 90:
            sig = p
        else:
            kept.append(p)
    return {'title': title, 'date': date, 'paras': kept, 'notes': notes, 'sig': sig}


def safe_name(title, idx):
    t = re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', title)
    return '%02d-%s.html' % (idx, t[:40])


def build():
    vols = []
    for v in VOLS:
        vol_dir = os.path.join(SRC, '毛泽东军事文集%d' % v['no'])
        files = []
        for root, _, fs in os.walk(vol_dir):
            for f in fs:
                if f.lower().endswith('.txt'):
                    m = re.match(r'^(?:mjw)(\d{4})\.txt$', f.lower())
                    if m and int(m.group(1)) != v['no'] * 1000:
                        files.append((int(m.group(1)), os.path.join(root, f)))
        files.sort()
        articles = []
        for num, fp in files:
            art = parse_article(gbk(fp))
            art['_num'] = num
            articles.append(art)
        print('卷%d: %d 篇' % (v['no'], len(articles)))
        v['articles'] = articles
        vols.append(v)

    # —— 各卷：文章页 + 卷选卷页 ——
    for v in vols:
        vol_dir = os.path.join(OUT, '第%d卷' % v['no'])
        os.makedirs(vol_dir, exist_ok=True)
        arts = v['articles']
        entries = []
        for i, art in enumerate(arts, 1):
            entries.append({'idx': i, 'title': art['title'], 'fname': safe_name(art['title'], i)})

        for i, (art, e) in enumerate(zip(arts, entries), 1):
            # 侧栏目录窗口
            lo = max(0, i - 1 - WIN)
            hi = min(len(entries), i + WIN)
            win = entries[lo:hi]
            toc_groups = [{'label': None, 'items': [
                {'num': str(x['idx']), 'title': x['title'], 'href': x['fname']} for x in win
            ]}]
            prev = entries[i - 2] if i > 1 else None
            nxt = entries[i] if i < len(entries) else None
            body = []
            for p in art['paras']:
                def rep(m):
                    n = int(m.group(1))
                    return '<sup class="fnref"><a href="#jx%d">[%d]</a></sup>' % (n, n)
                body.append({'kind': 'p', 'html': NOTE_REF_RE.sub(rep, p)})
            if art['sig']:
                body.append({'kind': 'sig', 'html': art['sig']})
            notes_items = ['<p class="note" id="jx%d">[%d]&ensp;%s</p>' % (n, n, t) for n, t in art['notes']]
            result = {
                'title': e['title'],
                'secdate': art['date'].replace('●', '○') if art['date'] else '',
                'body': body,
                'notes': ([{'header': '注　释', 'items': notes_items}] if notes_items else []),
            }
            page_html = render_article(
                result, art_idx=1, brand='毛泽东军事文集 第%d卷' % v['no'], voltag=v['period'],
                toc_groups=toc_groups, active_href=e['fname'],
                prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
                nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
                vol_href='../第%d卷.html' % v['no'],
                footer='文本整理自「毛泽东博览」（www.mzdbl.cn）《毛泽东军事文集》第%d卷（军事科学出版社、中央文献出版社1993年版），仅作学习、研究参考之用；如与纸质版有出入，以纸质版为准。' % v['no'],
                home_href='../../../index.html', assets='../../../assets',
            )
            with open(os.path.join(vol_dir, e['fname']), 'w', encoding='utf-8') as f:
                f.write(page_html)

        # 卷选卷页
        cards = []
        for i, e in enumerate(entries, 1):
            art = arts[i - 1]
            cards.append('''<a class="card" href="{href}">
  <div class="vol">第{idx}篇</div>
  <div class="ed">{date}</div>
  <div class="stat">{title}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(idx=i, date=(art['date'].replace('●', '○') or '—'), title=e['title'], href='第%d卷/%s' % (v['no'], e['fname'])))
        vol_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="毛泽东军事文集 第{no}卷 目录">
<title>毛泽东军事文集 · 第{no}卷</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">毛 泽 东 军 事 文 集</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>第{no}卷</h1>
    <div class="sub">{period}</div>
    <div class="meta">{n} 篇 · <a href="../军事文集.html">&#8678; 返回六卷总目</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    文本整理自「毛泽东博览」（www.mzdbl.cn），军事科学出版社、中央文献出版社 1993 年版，仅作学习、研究参考之用；如与纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>'''.format(no=v['no'], period=v['period'], n=len(entries), cards='\n'.join(cards))
        with open(os.path.join(OUT, '第%d卷.html' % v['no']), 'w', encoding='utf-8') as f:
            f.write(vol_html)
        print('  卷%d 写入 %d 页 + 卷选卷页' % (v['no'], len(entries)))

    # —— 主选卷页 ——
    cards = []
    for v in vols:
        cards.append('''<a class="card" href="{href}">
  <div class="vol">第{no}卷</div>
  <div class="ed">1993年版</div>
  <div class="stat">{n} 篇 · {period}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(no=v['no'], n=len(v['articles']), period=v['period'], href='军事文集/第%d卷.html' % v['no']))
    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《毛泽东军事文集》六卷">
<title>毛泽东军事文集 · 六卷</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 毛 泽 东 思 想 经 典</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>毛泽东军事文集</h1>
    <div class="sub">六 卷 本（1927—1972）</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    文本整理自「毛泽东博览」（www.mzdbl.cn），军事科学出版社、中央文献出版社 1993 年版，仅作学习、研究参考之用；如与纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>'''.format(cards='\n'.join(cards))
    with open(os.path.join(MAO, '军事文集.html'), 'w', encoding='utf-8') as f:
        f.write(landing)
    print('wrote 教员/军事文集.html')


if __name__ == '__main__':
    build()
