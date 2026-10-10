# -*- coding: utf-8 -*-
"""
build_works.py — 依据 manifest（作品清单）把 .tools/sources 里的源文章页
转换为「导师文集」站点的作品页与章节页。

用法：
  python .tools/build_works.py <manifest.json>   # 生成所有作品
  python .tools/build_works.py <manifest.json> --works 共产党宣言,反杜林论
"""
import os, re, sys, io, json, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import parse_article, render_article

ROOT = r'C:\导师文集'
SOURCES = os.path.join(ROOT, '.tools', 'sources')


def safe_filename(title, idx):
    t = re.sub(r'[\\/:*?"<>|\n\r\t ]+', '', title)
    t = t.replace('?', '').replace('？', '')
    if len(t) > 40:
        t = t[:40]
    return '%02d-%s.html' % (idx, t or '无题')


AUTHOR_PREFIX = re.compile(
    r'^\s*(卡·马克思和弗·恩格斯合著|卡·马克思和弗·恩格斯|弗·恩格斯。|弗·恩格斯\s|卡·马克思。|卡·马克思\s)')


def clean_title(html):
    """清洗标题：去掉脚注上标、HTML 标签、作者前缀、结尾脚注编号。"""
    t = re.sub(r'<sup.*?</sup>', '', html, flags=re.S)
    t = re.sub(r'<br\s*/?>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = AUTHOR_PREFIX.sub('', t).strip()
    t = re.sub(r'\s*(FN\d*|\d+)$', '', t).strip()
    return t


def load_source_file(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def build_landing_page(work, entries, first_href):
    cards = []
    for i, e in enumerate(entries, 1):
        vol = e['vol']
        cards.append('''<a class="card" href="{href}">
  <div class="vol">{vol}</div>
  <div class="ed">{ed}</div>
  <div class="stat">{stat}</div>
  <div class="range">{range}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(
            href=e['href'],
            vol=vol,
            ed=work.get('edition', ''),
            stat=e.get('stat', ''),
            range=work.get('range', ''),
        ))
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title} · 选卷首页</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>{title}</h1>
    <div class="sub">{sub}</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>'''.format(
        desc='%s 选卷首页' % work['title'],
        title=work['title'],
        sub=work.get('sub', ''),
        cards='\n'.join(cards),
        footer=work.get('footer', ''),
    )
    return html


def build_work(work):
    """处理一个作品。work 结构见 manifest。"""
    author_dir = os.path.join(ROOT, work['author'])
    work_dir = os.path.join(author_dir, work['dir'])
    os.makedirs(work_dir, exist_ok=True)

    src_files = work['source_files']  # [{path, title}] 相对于 SOURCES
    entries = []
    for i, sf in enumerate(src_files, 1):
        raw = load_source_file(os.path.join(SOURCES, sf['path']))
        parsed = parse_article(raw)
        title = clean_title(sf.get('title') or parsed['title'])
        parsed['title'] = title  # 渲染用清洗后的标题
        fname = safe_filename(title, i)
        entries.append({'idx': i, 'title': title, 'fname': fname,
                        'parsed': parsed})

    toc_groups = [{'label': None, 'items': [
        {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']}
        for e in entries
    ]}]

    vol_href = '../%s' % work['landing']  # landing 已含 .html
    assets = '../../assets'
    home = '../../index.html'
    brand = work['brand']
    voltag = work.get('voltag', '')
    footer = work.get('footer', '')

    for i, e in enumerate(entries):
        prev = entries[i - 1] if i > 1 else None
        nxt = entries[i] if i < len(entries) else None
        page_html = render_article(
            e['parsed'],
            art_idx=1,
            brand=brand,
            voltag=voltag,
            toc_groups=toc_groups,
            active_href=e['fname'],
            prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
            nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
            vol_href=vol_href,
            footer=footer,
            home_href=home,
            assets=assets,
        )
        out = os.path.join(work_dir, e['fname'])
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page_html)
        print('  wrote', os.path.relpath(out, ROOT))

    # 选卷页
    landing_entries = [{'vol': '第%d篇' % e['idx'] if len(entries) > 1 else '全文',
                        'href': e['fname'],
                        'ed': work.get('edition', ''),
                        'stat': e['title']} for e in entries]
    landing = build_landing_page(work, landing_entries, entries[0]['fname'])
    landing_path = os.path.join(author_dir, work['landing'])
    with open(landing_path, 'w', encoding='utf-8') as f:
        f.write(landing)
    print('  wrote', os.path.relpath(landing_path, ROOT))
    return len(entries)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('--works', default='')
    args = ap.parse_args()
    with open(args.manifest, encoding='utf-8') as f:
        manifest = json.load(f)
    want = set(w.strip() for w in args.works.split(',') if w.strip())
    total = 0
    for work in manifest['works']:
        if want and work['id'] not in want:
            continue
        print('== %s / %s' % (work['author'], work['title']))
        n = build_work(work)
        total += n
    print('完成，共生成 %d 个章节页' % total)


if __name__ == '__main__':
    main()
