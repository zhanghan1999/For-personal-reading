# -*- coding: utf-8 -*-
"""
mew_convert.py — 把「马列著作网页版」(MARX-ZH-CN/marx-zh-cn.github.io) 的文章页 HTML
转换为「导师文集」网站的阅读页格式。

兼容两种源页面结构：
  A. 马恩全集（MEW-ZH）：
     <h1>作者。标题<sup>…</sup></h1>
     <table class="add rt">…版本信息…</table>
     <p>　　段落</p> / <h3>小节</h3> / <h4>小节</h4>
  B. 列宁全集（LENIN）：
     <h1>标题</h1>
     <p class="date">（副题）<br>（写作时间）</p>
     <div class="TCC">…站内目录…</div>
     <h3 id="1">章节</h3> / <h4>小节</h4>
     <table class="sign">…署名…</table>
     <table class="tnb">…统计表…</table>
  两者共同的：
     <p>　　段落</p>
     <sup><a href="#z1" id="zref1">…</a></sup> 脚注引用
     <aside class="footnote"><div class="style2">作者原注/脚注/注释</div><div><a id="az1" href="#azref1">(1)</a> 注文</div>…</aside>
"""
import re

TAG = re.compile(r'<[^>]+>')
STYLE = re.compile(r'\sstyle="[^"]*"')
BLOCK_RE = re.compile(
    r'<(h1|h2|h3|h4|p|blockquote|table|aside)([^>]*)>(.*?)</\1>',
    flags=re.S)


def _clean_inline(html):
    html = html.replace('\r', '').replace('\n', ' ')
    html = re.sub(r'[ \t　]+', ' ', html)
    return html


def _fmt_supref(html):
    """<sup><a href="#id" id="refid">label</a></sup> → fnref 格式。"""
    return re.sub(r'<sup>(<a href="#[^"]+"[^>]*>.*?</a>)</sup>',
                  r'<sup class="fnref">\1</sup>', html, flags=re.S)


def _strip_lead(html):
    return re.sub(r'^\s*[　 ]+', '', html)


def _table_to_lines(table_inner):
    m = re.search(r'<td[^>]*>(.*?)</td>', table_inner, flags=re.S)
    cell = m.group(1) if m else table_inner
    cell = TAG.sub('', cell)
    cell = cell.replace('\r', '')
    lines = [ln.strip() for ln in cell.split('\n') if ln.strip()]
    return '<br>\n'.join(lines)


def _parse_note_aside(inner):
    m = re.search(r'<div[^>]*class="style2"[^>]*>(.*?)</div>', inner, flags=re.S)
    if not m:
        return None
    header = TAG.sub('', m.group(1)).strip()
    rest = inner[m.end():]
    items = []
    for dm in re.finditer(r'<div[^>]*>(.*?)</div>', rest, flags=re.S):
        block = dm.group(1)
        am = re.match(r'<a[^>]*href="#[^"]+"[^>]*id="([^"]+)"[^>]*>(.*?)</a>(.*)',
                      block, flags=re.S)
        if am:
            nid = am.group(1)
            label = am.group(2)
            note_body = _clean_inline(am.group(3))
            note_body = _fmt_supref(note_body)
            items.append('<p class="note" id="%s">%s　%s</p>'
                         % (nid, label, note_body.strip()))
        else:
            block = _clean_inline(block)
            if block.strip():
                items.append('<p class="note">%s</p>' % _fmt_supref(block.strip()))
    if not items:
        return None
    return {'header': header, 'items': items}


def parse_article(raw):
    m = re.search(r'<body[^>]*>(.*?)</body>', raw, flags=re.S)
    inner = m.group(1) if m else raw

    title = ''
    secdate_lines = []
    body = []
    note_groups = []

    for mm in BLOCK_RE.finditer(inner):
        tag = mm.group(1)
        attrs = mm.group(2) or ''
        content = mm.group(3)

        if tag == 'h1':
            title = _clean_inline(content)
            title = _fmt_supref(title)
            continue
        if tag == 'aside':
            g = _parse_note_aside(content)
            if g:
                note_groups.append(g)
            continue

        # —— 表格分类 ——
        if tag == 'table':
            if re.search(r'class="[^"]*rt[^"]*"', attrs):
                secdate_lines.append(_table_to_lines(content))
            elif re.search(r'class="[^"]*sign[^"]*"', attrs):
                lines = _table_to_lines(content)
                body.append({'kind': 'sig', 'html': lines})
            else:
                # 数据表（tnb 等）：去掉内联 style，保留结构
                tbl = '<table%s>%s</table>' % (STYLE.sub('', attrs).strip(), content)
                tbl = STYLE.sub('', tbl)
                body.append({'kind': 'table', 'html': tbl})
            continue

        # —— 日期段 / 段内目录 / 正文块 ——
        if tag == 'p' and re.search(r'class="[^"]*date[^"]*"', attrs):
            secdate_lines.append(_fmt_supref(_clean_inline(content)))
            continue
        if tag == 'div' and re.search(r'class="[^"]*TCC[^"]*"', attrs):
            continue  # 站内目录，丢弃

        if tag == 'h2':
            body.append({'kind': 'h2', 'html': _strip_lead(_clean_inline(content)).strip()})
            continue
        if tag == 'h3':
            body.append({'kind': 'h3', 'html': _strip_lead(_clean_inline(content)).strip()})
            continue
        if tag == 'h4':
            body.append({'kind': 'h4', 'html': _strip_lead(_clean_inline(content)).strip()})
            continue
        if tag == 'blockquote':
            body.append({'kind': 'quote',
                         'html': _fmt_supref(_clean_inline(content)).strip()})
            continue
        if tag == 'p':
            content = _fmt_supref(_clean_inline(content))
            content = _strip_lead(content).strip()
            content = re.sub(r'\s+', ' ', content)
            if content:
                body.append({'kind': 'p', 'html': content})
            continue

    # 若无 h1 标题，取正文开头的第一个 h2 作为标题（允许开头先有 1-2 个 h4/h3 页码标记）
    if not title:
        for k, blk in enumerate(body[:3]):
            if blk['kind'] == 'h2':
                title = blk['html']
                del body[k]
                break

    return {
        'title': title,
        'secdate': '<br>\n'.join(secdate_lines),
        'body': body,
        'notes': note_groups,
    }


def render_article(result, art_idx=1, brand='', voltag='', toc_groups=None,
                   active_href='', prev=None, nxt=None, vol_href='../index.html',
                   footer='', home_href='../../index.html', assets='../../assets'):
    parts = []
    parts.append('<article id="c%d" class="chapter">' % art_idx)
    parts.append('<div class="chapter-head">')
    if voltag:
        parts.append('<div class="no">%s</div>' % voltag)
    parts.append('<h2>%s</h2>' % result['title'])
    if result.get('secdate'):
        parts.append('<p class="secdate">%s</p>' % result['secdate'])
    parts.append('</div>')
    if result.get('headnote'):
        parts.append('<div class="headnote"><span class="tag">题解</span>%s</div>'
                     % result['headnote'])
    for blk in result['body']:
        kind = blk['kind']
        html = blk['html']
        if kind == 'p':
            parts.append('<p class="para">%s</p>' % html)
        elif kind == 'sig':
            parts.append('<p class="para sig">%s</p>' % html)
        elif kind == 'h2' or kind == 'h3':
            parts.append('<h3 class="subhead">%s</h3>' % html)
        elif kind == 'h4':
            parts.append('<h4 class="subhead2">%s</h4>' % html)
        elif kind == 'quote':
            parts.append('<blockquote>%s</blockquote>' % html)
        elif kind == 'table':
            parts.append(html)
    for g in result['notes']:
        parts.append('<div class="notes"><h4>%s</h4>%s</div>'
                     % (g['header'], '\n'.join(g['items'])))
    nav = '<div class="chapnav">'
    if prev:
        nav += '<a href="%s"><span class="lbl">&#8592; 上一篇</span><span class="ttl">%s</span></a>' % (prev['href'], prev['title'])
    else:
        nav += '<a href="#top"><span class="lbl">&#8592; 封面</span></a>'
    if nxt:
        nav += '<a href="%s" style="text-align:right"><span class="lbl">下一篇 &#8594;</span><span class="ttl">%s</span></a>' % (nxt['href'], nxt['title'])
    else:
        nav += '<a href="%s" style="text-align:right"><span class="lbl">回到选卷 &#8594;</span></a>' % vol_href
    nav += '</div>'
    parts.append(nav)
    parts.append('</article>')

    page = {
        'brand': brand,
        'voltag': voltag or '',
        'homeHref': home_href,
        'volHref': vol_href,
        'volLabel': '选卷',
        'tocGroups': toc_groups or [],
        'activeHref': active_href,
        'searchPlaceholder': '搜索篇名…',
    }
    import json
    skeleton = '''<!DOCTYPE html>
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
    plain_title = TAG.sub('', result['title']).strip()
    return skeleton.format(
        desc='%s·%s' % (brand, plain_title),
        title='%s · %s' % (plain_title, brand),
        assets=assets,
        home=home_href,
        volpage=vol_href,
        brand=brand,
        voltag=voltag or '',
        volLabel='选卷',
        article='\n'.join(parts),
        footer=footer,
        page_json=json.dumps(page, ensure_ascii=False),
    )
