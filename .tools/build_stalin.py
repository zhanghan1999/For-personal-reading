# -*- coding: utf-8 -*-
"""
build_stalin.py — 从《联共(布)党史简明教程》第四章 TeX 中提取
《论辩证唯物主义和历史唯物主义》全文，生成「斯大林」作品页。
"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
SRC = os.path.join(ROOT, '.tools', 'sources', 'stalin', 'lun-bianzhengweiwu.tex')
AUTHOR = os.path.join(ROOT, '斯大林')
LANDING = '论辩证唯物主义和历史唯物主义.html'
WORKDIR = os.path.join(AUTHOR, '论辩证唯物主义和历史唯物主义')

NOTES = []
FN_COUNT = [0]


def match_brace(s, pos):
    depth = 0
    i = pos
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1


def clean_inline(s):
    """把剩余的 TeX 命令/花括号清掉，保留普通文本。"""
    s = s.replace('\\q', '')
    s = s.replace('\\dotemph{', '')
    s = s.replace('\\textbf{', '')
    s = s.replace('\\emph{', '')
    s = re.sub(r'\\[a-zA-Z]+\*?\s*', '', s)
    s = s.replace('\\', ' ')
    s = s.replace('{}', '')
    s = re.sub(r'[ \t　]+', ' ', s)
    return s.strip()


def take_notes(body):
    """把 \footnote{...} 换成上标引用，收集注释。"""
    out = []
    i = 0
    n = len(body)
    while i < n:
        if body.startswith(r'\footnote{', i):
            open_brace = i + len(r'\footnote{') - 1
            close = match_brace(body, open_brace)
            note_txt = body[open_brace + 1:close]
            FN_COUNT[0] += 1
            num = FN_COUNT[0]
            note_txt = clean_inline(note_txt)
            NOTES.append('<p class="note" id="lbz%d">[%d]&ensp;%s</p>' % (num, num, note_txt))
            out.append('<sup class="fnref"><a href="#lbz%d">[%d]</a></sup>' % (num, num))
            i = close + 1
        else:
            out.append(body[i])
            i += 1
    return ''.join(out)


def convert_inline(s):
    s = re.sub(r'\\\\', ' ', s)
    return clean_inline(s)


def extract_section(tex):
    start = tex.index(r'\subsection[二')
    end = tex.index(r'\subsection[三')
    sec = tex[start:end]
    m = re.search(r'\\subsection\[[^\]]*\]\{([^}]*)\}', sec)
    title = m.group(1) if m else '论辩证唯物主义和历史唯物主义'
    title = clean_inline(title.replace('\\', ' ')).replace('二', '').strip()
    body = sec[m.end():] if m else sec
    return title, body


def convert(tex_body):
    blocks = []
    pos = 0
    n = len(tex_body)
    while True:
        qs = tex_body.find(r'\begin{quotation}', pos)
        if qs == -1:
            blocks.append(('text', tex_body[pos:]))
            break
        if qs > pos:
            blocks.append(('text', tex_body[pos:qs]))
        qe = tex_body.find(r'\end{quotation}', qs)
        blocks.append(('quote', tex_body[qs + len(r'\begin{quotation}'):qe]))
        pos = qe + len(r'\end{quotation}')

    result = []
    for kind, content in blocks:
        content = take_notes(content)
        if kind == 'quote':
            html = convert_inline(content)
            result.append({'kind': 'quote', 'html': html})  # render_article 会包 <blockquote>
        else:
            content = content.replace('\\\\\n', '\n\n').replace('\\\n', '\n\n')
            paras = re.split(r'\n\s*\n', content)
            for p in paras:
                p = convert_inline(p)
                if not p:
                    continue
                if re.match(r'^[（(][一二三四五六七八九十]+[）)]', p) and len(p) < 40:
                    result.append({'kind': 'h3', 'html': p})
                else:
                    result.append({'kind': 'p', 'html': p})
    return result


def main():
    global NOTES, FN_COUNT
    NOTES = []
    FN_COUNT = [0]
    tex = open(SRC, encoding='utf-8').read()
    title, body = extract_section(tex)
    body_blocks = convert(body)
    print('title:', title, '| blocks:', len(body_blocks), '| notes:', len(NOTES))

    result = {
        'title': title,
        'secdate': '选自《联共（布）党史简明教程》第四章第二节<br>（1938年，斯大林著）',
        'body': body_blocks,
        'notes': ([{'header': '注　释', 'items': NOTES}] if NOTES else []),
    }
    fname = '01-%s.html' % re.sub(r'[\\/:*?"<>|\n\r\t ]+', '', title)[:40]
    toc_groups = [{'label': None, 'items': [{'num': '1', 'title': title, 'href': fname}]}]
    page_html = render_article(
        result, art_idx=1, brand=title, voltag='《斯大林选集》下卷',
        toc_groups=toc_groups, active_href=fname,
        prev=None, nxt=None, vol_href='../%s' % LANDING,
        footer='文本整理自 GitHub 公开仓库 VohsiLiu/History-of-the-Communist-Party-of-the-Soviet-Union-Bolshevik（《联共（布）党史简明教程》TeX 版）第四章第二节，系《斯大林选集》下卷所收《论辩证唯物主义和历史唯物主义》全文，仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。',
        home_href='../../index.html', assets='../../assets',
    )
    os.makedirs(WORKDIR, exist_ok=True)
    with open(os.path.join(WORKDIR, fname), 'w', encoding='utf-8') as f:
        f.write(page_html)
    print('wrote', os.path.join(WORKDIR, fname))

    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《论辩证唯物主义和历史唯物主义》选卷首页">
<title>论辩证唯物主义和历史唯物主义 · 选卷首页</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>论辩证唯物主义和历史唯物主义</h1>
    <div class="sub">《联共（布）党史简明教程》第四章第二节</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
<a class="card" href="论辩证唯物主义和历史唯物主义/{href}">
  <div class="vol">全文</div>
  <div class="ed">1938年版</div>
  <div class="stat">{title}</div>
  <div class="range">1938 年 · 《斯大林选集》下卷</div>
  <div class="go">打开阅读 &#8594;</div>
</a>
  </main>
  <footer>
    文本整理自 GitHub 公开仓库 VohsiLiu/History-of-the-Communist-Party-of-the-Soviet-Union-Bolshevik（《联共（布）党史简明教程》TeX 版）第四章第二节，仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。《论列宁主义基础》全文待补。
  </footer>
</div>
</body>
</html>'''.format(href=fname, title=title)
    with open(os.path.join(AUTHOR, LANDING), 'w', encoding='utf-8') as f:
        f.write(landing)
    print('wrote', os.path.join(AUTHOR, LANDING))


if __name__ == '__main__':
    main()
