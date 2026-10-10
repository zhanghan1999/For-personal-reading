# -*- coding: utf-8 -*-
"""
毛选拆分脚本：从 parsed.json 生成每篇文章独立页面 + 各卷文章列表。

输出结构（与资本论一致）：
  教员/毛选/<卷号>/<序号>-<标题>.html   文章页
  教员/毛选.html                         选卷页（可放各卷卡片，由 index 进入）

文章页结构：
  - 引用 ../../assets/style.css + ../../assets/app.js
  - 内嵌 window.PAGE 数据（目录分组/当前高亮/翻页）
  - <article class="chapter"> 内容
"""
import json, os, re, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集\教员\毛选'
OUT = ROOT
ASSETS_REL = '../../../assets'  # 从 毛选/1/ 到根目录 assets/
# 文章页位于 教员/毛选/N/xx.html，首页在根目录 index.html，选卷页在 教员/毛选.html
HOME_REL = '../../../index.html'
VOLPAGE_REL = '../../毛选.html'

# 全角带圈数字 → 数字
CIRCLED = {
    '①':'1','②':'2','③':'3','④':'4','⑤':'5','⑥':'6','⑦':'7','⑧':'8','⑨':'9','⑩':'10',
    '⑪':'11','⑫':'12','⑬':'13','⑭':'14','⑮':'15','⑯':'16','⑰':'17','⑱':'18','⑲':'19','⑳':'20',
}
# 全角括号数字 ⑴-⒇ → 数字
PAREN = {
    '⑴':'1','⑵':'2','⑶':'3','⑷':'4','⑸':'5','⑹':'6','⑺':'7','⑻':'8','⑼':'9','⑽':'10',
    '⑾':'11','⑿':'12','⒀':'13','⒁':'14','⒂':'15','⒃':'16','⒄':'17','⒅':'18','⒆':'19','⒇':'20',
}

def html_escape(t):
    return t

def convert_refs(text, vol, art_idx):
    """把 ⑴ ⑵ ... 全角括号数字转为 fnref 上标，编号 = n<序号>。"""
    def rep(m):
        n = PAREN[m.group(0)]
        return '<sup class="fnref"><a href="#v%da%d-n%s">[%s]</a></sup>' % (vol, art_idx, n, n)
    return re.sub(r'[⑴-⒇]', rep, text)

def convert_refs_v5(text, vol, art_idx):
    """第五卷用 [1] 形式。"""
    def rep(m):
        n = m.group(1)
        return '<sup class="fnref"><a href="#v%da%d-n%s">[%s]</a></sup>' % (vol, art_idx, n, n)
    return re.sub(r'\[(\d+)\]', rep, text)

PAGE_SKELETON_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="{assets}/style.css">
<style>
  /* 本页专属微调 */
</style>
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

def build_article_page(vol, art_idx, title, date, headnote, body_html, notes_html,
                       toc_groups, active_file, prev, nxt, vol_meta):
    """toc_groups: [{label, items:[{num,title,href}]}]"""
    # 页面元数据（供公共 JS 用）
    page = {
        'brand': '毛泽东选集 · %s' % vol_meta['vol_cn'],
        'voltag': vol_meta['edition'],
        'homeHref': HOME_REL,
        'volHref': VOLPAGE_REL,
        'volLabel': '选卷',
        'tocGroups': toc_groups,
        'activeHref': active_file,
        'searchPlaceholder': '搜索篇名…',
    }
    # 正文
    parts = []
    parts.append('<article id="c%d" class="chapter">' % art_idx)
    parts.append('<div class="chapter-head">')
    if vol_meta.get('period'):
        parts.append('<div class="no">%s</div>' % vol_meta['period'])
    parts.append('<h2>%s</h2>' % title)
    if date:
        parts.append('<div class="date">%s</div>' % date)
    parts.append('</div>')
    if headnote:
        parts.append('<div class="headnote"><span class="tag">题解</span>%s</div>' % headnote)
    parts.append(body_html)
    if notes_html:
        parts.append('<div class="notes"><h4>注　释</h4>%s</div>' % notes_html)
    # 上/下一篇
    nav = '<div class="chapnav">'
    if prev:
        nav += '<a href="%s"><span class="lbl">&#8592; 上一篇</span><span class="ttl">%s</span></a>' % (prev['fname'], prev['title'])
    else:
        nav += '<a href="#top"><span class="lbl">&#8592; 封面</span></a>'
    if nxt:
        nav += '<a href="%s" style="text-align:right"><span class="lbl">下一篇 &#8594;</span><span class="ttl">%s</span></a>' % (nxt['fname'], nxt['title'])
    else:
        nav += '<a href="%s" style="text-align:right"><span class="lbl">回到选卷 &#8594;</span></a>' % VOLPAGE_REL
    nav += '</div>'
    parts.append(nav)
    parts.append('</article>')

    page_html = PAGE_SKELETON_HEAD.format(
        desc='《毛泽东选集》%s·%s' % (vol_meta['vol_cn'], title),
        title='%s · 《毛泽东选集》%s' % (title, vol_meta['vol_cn']),
        assets=ASSETS_REL,
        home=HOME_REL,
        volpage=VOLPAGE_REL,
        brand='毛泽东选集 · %s' % vol_meta['vol_cn'],
        voltag=vol_meta['edition'],
        volLabel='选卷',
        article='\n'.join(parts),
        footer='本文本整理自「毛泽东博览」（www.mzdbl.cn）《毛泽东选集》%s（%s），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。' % (vol_meta['vol_cn'], vol_meta['edition']),
        page_json=json.dumps(page, ensure_ascii=False),
    )
    return page_html


def safe_filename(title, idx):
    t = re.sub(r'[\\/:*?"<>|\n\r\t ]+', '', title)
    t = t.replace('?', '').replace('？', '')
    if len(t) > 40:
        t = t[:40]
    return '%02d-%s.html' % (idx, t or '无题')


def main():
    vols_meta = []
    # ---- 卷 1-4（articles 结构）----
    for vol in [1, 2, 3, 4]:
        data = json.load(open(os.path.join(SRC_DATA, '卷%d数据' % vol, 'parsed.json'), encoding='utf-8'))
        edition = data.get('edition', '')
        vol_cn = '第%s卷' % '一二三四五六七八九'[vol - 1]
        volpage = '../毛选.html'
        vol_meta = {'vol': vol, 'vol_cn': vol_cn, 'edition': edition, 'volpage': volpage}
        outdir = os.path.join(OUT, str(vol))
        os.makedirs(outdir, exist_ok=True)
        articles = data['articles']
        # 建立每篇文章条目（标题+文件名）
        entries = []
        for i, a in enumerate(articles, 1):
            title = a['title']
            fname = safe_filename(title, i)
            entries.append({'idx': i, 'title': title, 'fname': fname})
        # 目录分组：毛选按时期分组
        periods = data.get('periods', [])
        # 简化：单组（整卷），保持 num 序号
        toc_groups = [{'label': None, 'items': [
            {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries
        ]}]
        for i, a in enumerate(articles, 1):
            title = a['title']
            fname = entries[i - 1]['fname']
            # content → html
            date, headnote = None, None
            body_html = []
            for item in a['content']:
                if not isinstance(item, list) or len(item) < 2:
                    continue
                typ, txt = item[0], item[1]
                if typ == 'date':
                    date = txt.strip()
                elif typ == 'headnote':
                    headnote = re.sub(r'\s+', ' ', txt).strip()
                elif typ == 'p':
                    txt = convert_refs(txt, vol, i)
                    body_html.append('<p class="para">%s</p>' % txt.strip())
                elif typ == 'h':
                    body_html.append('<h3 class="subhead">%s</h3>' % txt.strip())
            # notes
            notes_html = []
            if a.get('notes'):
                for nt in a['notes']:
                    m = re.match(r'〔(\d+)〕(.*)', nt, flags=re.S)
                    if m:
                        n, body = m.group(1), m.group(2).strip()
                        notes_html.append('<p class="note" id="v%da%d-n%s">[%s]&ensp;%s</p>' % (vol, i, n, n, body))
                    else:
                        notes_html.append('<p class="note">%s</p>' % nt.strip())
            prev = entries[i - 2] if i > 1 else None
            nxt = entries[i] if i < len(entries) else None
            page = build_article_page(vol, i, title, date, headnote,
                                      '\n'.join(body_html), '\n'.join(notes_html),
                                      toc_groups, fname, prev, nxt, vol_meta)
            with open(os.path.join(outdir, fname), 'w', encoding='utf-8') as f:
                f.write(page)
            print('  vol%d wrote %s' % (vol, fname))
        vols_meta.append((vol, vol_cn, edition, len(articles)))

    # ---- 卷 5（列表结构）----
    data5 = json.load(open(os.path.join(ROOT, '5', '数据', 'parsed.json'), encoding='utf-8'))
    vol = 5
    vol_cn = '第五卷'
    edition = '1977年版'
    volpage = '../毛选.html'
    vol_meta = {'vol': vol, 'vol_cn': vol_cn, 'edition': edition, 'volpage': volpage}
    outdir = os.path.join(OUT, str(vol))
    os.makedirs(outdir, exist_ok=True)
    entries = []
    for i, a in enumerate(data5, 1):
        title = a['title']
        fname = safe_filename(title, i)
        entries.append({'idx': i, 'title': title, 'fname': fname})
    toc_groups = [{'label': None, 'items': [
        {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries
    ]}]
    for i, a in enumerate(data5, 1):
        title = a['title']
        fname = entries[i - 1]['fname']
        date = a.get('date')
        headnote = a.get('headnote')
        if headnote:
            headnote = re.sub(r'\s+', ' ', headnote).strip()
        body_html = []
        for item in a.get('body', []):
            if not isinstance(item, list) or len(item) < 2:
                continue
            typ, txt = item[0], item[1]
            if typ == 'p':
                txt = convert_refs_v5(txt, vol, i)
                body_html.append('<p class="para">%s</p>' % txt.strip())
            elif typ in ('h', 'subhead'):
                body_html.append('<h3 class="subhead">%s</h3>' % txt.strip())
        notes_html = []
        for nt in a.get('footnotes', []):
            # 兼容两种格式："[1]xxx..." 或 "注释[1]xxx..."
            m = re.match(r'(?:注释)?\[(\d+)\](.*)', nt, flags=re.S)
            if m:
                n, body = m.group(1), m.group(2).strip()
                notes_html.append('<p class="note" id="v%da%d-n%s">[%s]&ensp;%s</p>' % (vol, i, n, n, body))
            else:
                notes_html.append('<p class="note">%s</p>' % nt.strip())
        prev = entries[i - 2] if i > 1 else None
        nxt = entries[i] if i < len(entries) else None
        page = build_article_page(vol, i, title, date, headnote,
                                  '\n'.join(body_html), '\n'.join(notes_html),
                                  toc_groups, fname, prev, nxt, vol_meta)
        with open(os.path.join(outdir, fname), 'w', encoding='utf-8') as f:
            f.write(page)
        print('  vol5 wrote %s' % fname)
    vols_meta.append((vol, vol_cn, edition, len(data5)))

    print('毛选拆分完成, 共', sum(v[3] for v in vols_meta), '篇文章')


if __name__ == '__main__':
    main()
