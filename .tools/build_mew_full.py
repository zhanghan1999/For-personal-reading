# -*- coding: utf-8 -*-
"""
build_mew_full.py — 把 .tools/sources/mew/<卷>/ 的《马克思恩格斯全集》原始页
转成站内结构（全集唯一正文）：

  导师著作/马克思/马克思恩格斯全集.html              总选卷页（50 卷卡片）
  导师著作/马克思/马克思恩格斯全集/第X卷.html        卷选卷页（该卷篇目卡片）
  导师著作/马克思/马克思恩格斯全集/第X卷/NN-篇名.html 阅读页

同时输出 .tools/mew_full_map.json（卷 → 篇目 → 源文件/目标文件），供视图页生成使用。
"""
import os, re, sys, io, json, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import parse_article, render_article

ROOT = r'C:\导师文集'
SRC = os.path.join(ROOT, '.tools', 'sources')
OUTBASE = os.path.join(ROOT, '导师著作', '马克思')
SETDIR = os.path.join(OUTBASE, '马克思恩格斯全集')
MAP_PATH = os.path.join(ROOT, '.tools', 'mew_full_map.json')

AUTHOR_PREFIX = re.compile(
    r'^\s*(卡·马克思和弗·恩格斯合著|卡·马克思和弗·恩格斯|卡·马克思|弗·恩格斯)[。：:\s]*')


def clean_title(html, fallback=''):
    t = re.sub(r'<sup.*?</sup>', '', html, flags=re.S)
    t = re.sub(r'<br\s*/?>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    m = AUTHOR_PREFIX.match(t)
    author = ''
    if m:
        author = m.group(1)
        t = t[m.end():].strip()
    t = re.sub(r'\s*(FN\d*)$', '', t).strip()
    t = t or re.sub(r'\s+', ' ', fallback).strip() or '无题'
    return t, author


def safe_filename(title, idx):
    t = re.sub(r'[\\/:*?"<>|\n\r\t ]+', '', title)
    t = t.replace('？', '').replace('?', '').replace('！', '').replace('，', '')
    if len(t) > 40:
        t = t[:40]
    return '%02d-%s.html' % (idx, t or '无题')


def era_of(vol_title):
    """从卷标题里抠年代范围：'…第27卷-（书信。1842年—1851年12月）' → '书信 · 1842年—1851年12月'"""
    m = re.search(r'[（(](.*?)[）)]\s*$', vol_title)
    return m.group(1).strip() if m else ''


SRC_PAGE_RE = re.compile(r'href="(MEW\d+-\d+\.html)(#[^"]*)?"')
IMG_LINK_RE = re.compile(r'<a\s+[^>]*href="([^"#][^"]*)"[^>]*>(.*?)</a>', re.S | re.I)


def unwrap_missing_anchors(html, out_dir):
    """把指向本站不存在文件的 <a> 解包成纯内容（源站缺失的大图、外部条目等），保证零坏链。"""
    def rep(m):
        href, inner = m.group(1), m.group(2)
        if href.startswith(('http://', 'https://', 'mailto:', 'javascript:', 'tel:', '/')):
            return m.group(0)
        tgt = os.path.join(out_dir, href.split('#')[0].split('?')[0])
        return m.group(0) if os.path.exists(tgt) else inner
    return IMG_LINK_RE.sub(rep, html)


def main():
    idx = json.load(open(os.path.join(SRC, '_collected_index.json'), encoding='utf-8'))
    vols = [v for v in idx['mew'] if v.get('status') == 200 and v.get('pages')]
    if len(sys.argv) > 1:  # 调试：只处理指定卷，如 python build_mew_full.py 4
        only = set(int(x) for x in sys.argv[1:])
        vols = [v for v in vols if v['vol'] in only]
    mapping = {'volumes': []}
    total = 0
    os.makedirs(SETDIR, exist_ok=True)

    # —— 第一遍：先算出全卷的「源文件名 → 卷/成品文件名」映射（跨卷互链要用）——
    global_map = {}
    plans = {}
    for v in vols:
        no = v['vol']
        src_dir = os.path.join(SRC, 'mew', str(no))
        entries = []
        for i, p in enumerate(v['pages'], 1):
            raw = open(os.path.join(src_dir, p['file']), encoding='utf-8', errors='replace').read()
            parsed = parse_article(raw)
            title, author = clean_title(parsed['title'], p['title'])
            parsed['title'] = title
            fname = safe_filename(title, i)
            entries.append({'idx': i, 'title': title, 'author': author,
                            'fname': fname, 'src': p['file'], 'parsed': parsed})
            global_map[p['file']] = (no, fname)
        plans[no] = entries

    for v in vols:
        no = v['vol']
        era = era_of(v['title'])
        vdir = os.path.join(SETDIR, '第%d卷' % no)
        os.makedirs(vdir, exist_ok=True)
        src_dir = os.path.join(SRC, 'mew', str(no))
        entries = plans[no]

        toc_groups = [{'label': None, 'items': [
            {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries]}]

        footer = ('文本整理自「中文马克思主义文库」镜像（marx-zh-cn.github.io）《马克思恩格斯全集》'
                  '第%d卷（中文第一版，人民出版社；第1卷为中文第二版），仅作学习、研究参考之用；'
                  '如与人民出版社纸质版有出入，以纸质版为准。' % no)

        for i, e in enumerate(entries):
            prev = entries[i - 1] if i > 0 else None
            nxt = entries[i + 1] if i + 1 < len(entries) else None
            page_html = render_article(
                e['parsed'],
                art_idx=1,
                brand='马克思恩格斯全集 · 第%d卷' % no,
                voltag=era or ('第%d卷' % no),
                toc_groups=toc_groups,
                active_href=e['fname'],
                prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
                nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
                vol_href='../第%d卷.html' % no,
                footer=footer,
                home_href='../../../../index.html',
                assets='../../../../assets',
            )
            out = os.path.join(vdir, e['fname'])

            # 补齐正文引用的本地图片（先补图，再判断锚点目标是否存在）
            for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', page_html, re.I):
                rel = m.group(1)
                if re.match(r'^(https?:|data:|//|/)', rel):
                    continue
                s = os.path.join(src_dir, rel)
                d = os.path.join(vdir, rel)
                if os.path.exists(s) and not os.path.exists(d):
                    os.makedirs(os.path.dirname(d), exist_ok=True)
                    shutil.copyfile(s, d)

            # 源页内「分篇目录」链接（MEW17-036.html 之类）改为站内成品页
            def rep_href(m):
                src_name, anchor = m.group(1), m.group(2) or ''
                tgt = global_map.get(src_name)
                if not tgt:
                    return m.group(0)
                tvol, tfname = tgt
                href = tfname if tvol == no else '../../第%d卷/%s' % (tvol, tfname)
                return 'href="%s%s"' % (href, anchor)
            page_html = SRC_PAGE_RE.sub(rep_href, page_html)

            # 源站缺失的大图 / 外部条目解包，保持零坏链
            page_html = unwrap_missing_anchors(page_html, vdir)

            with open(out, 'w', encoding='utf-8') as f:
                f.write(page_html)

        # 卷选卷页
        cards = []
        for e in entries:
            cards.append('''<a class="card" href="第{no}卷/{href}">
  <div class="vol">第 {idx} 篇</div>
  <div class="ed">{author}</div>
  <div class="stat">{title}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(no=no, idx=e['idx'], href=e['fname'], title=e['title'],
                author=e['author'] or '&nbsp;'))
        vol_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="马克思恩格斯全集 第{no}卷 目录">
<title>马克思恩格斯全集 · 第{no}卷</title>
<link rel="stylesheet" href="../../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">马 克 思 恩 格 斯 全 集</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>第{no}卷</h1>
    <div class="sub">{era}</div>
    <div class="meta">{n} 篇 · <a href="../马克思恩格斯全集.html">&#8678; 返回五十卷总目</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>'''.format(no=no, era=era or '', n=len(entries), cards='\n'.join(cards), footer=footer)
        with open(os.path.join(SETDIR, '第%d卷.html' % no), 'w', encoding='utf-8') as f:
            f.write(vol_html)

        mapping['volumes'].append({
            'vol': no,
            'title': v['title'],
            'era': era,
            'articles': [{'idx': e['idx'], 'title': e['title'], 'author': e['author'],
                          'fname': e['fname'], 'src': e['src']} for e in entries],
        })
        total += len(entries)
        print('第%d卷: %d 篇' % (no, len(entries)))

    # 总选卷页
    cards = []
    for v in mapping['volumes']:
        cards.append('''<a class="card" href="马克思恩格斯全集/第{no}卷.html">
  <div class="vol">第{no}卷</div>
  <div class="ed">{era}</div>
  <div class="stat">{n} 篇</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(no=v['vol'], era=v['era'] or '&nbsp;', n=len(v['articles'])))
    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《马克思恩格斯全集》中文版 五十卷">
<title>马克思恩格斯全集 · 五十卷</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 马 克 思 恩 格 斯</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">马克思恩格斯全集</h1>
    <div class="sub">五 十 卷（1833—1895）· 共 {total} 篇</div>
    <div class="meta"><a href="../../index.html">&#8678; 返回马克思</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    文本整理自「中文马克思主义文库」镜像（marx-zh-cn.github.io）《马克思恩格斯全集》中文版；第一版第2—50卷（人民出版社），第1卷为中文第二版。仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>'''.format(total=total, cards='\n'.join(cards))
    with open(os.path.join(OUTBASE, '马克思恩格斯全集.html'), 'w', encoding='utf-8') as f:
        f.write(landing)

    json.dump(mapping, open(MAP_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('完成：%d 卷 %d 篇；映射表 %s' % (len(mapping['volumes']), total, MAP_PATH))

    # 目录外置：每卷一个 目录.js，避免 6883 页各带一份整卷目录（可省 165 MB）
    try:
        from slim_toc import slim_root
        for v in mapping['volumes']:
            r = slim_root(os.path.join(SETDIR, '第%d卷' % v['vol']))
            if r:
                print('  瘦身 第%d卷：%.1f → %.1f MB' % (v['vol'], r[0] / 1048576, r[1] / 1048576))
    except Exception as e:
        print('  !! 目录外置失败（请手动跑 python .tools/slim_toc.py）：', e)


if __name__ == '__main__':
    main()
