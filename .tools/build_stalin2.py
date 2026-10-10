# -*- coding: utf-8 -*-
"""
build_stalin2.py — 从《新编斯大林全集》正卷 PDF 提取的原始文本
（.tools/sources/stalin/lnjz-raw.txt，PDF 1840-1924 页 = 本卷 51-135 页）
生成《论列宁主义基础》的站点页面（引言 + 九节），并更新斯大林索引。
"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
SRC = os.path.join(ROOT, '.tools', 'sources', 'stalin', 'lnjz-raw.txt')
AUTHOR = os.path.join(ROOT, '斯大林')
LANDING = '论列宁主义基础.html'
WORKDIR = os.path.join(AUTHOR, '论列宁主义基础')

SECTIONS = ['一 列宁主义的历史根源', '二 方 法', '三 理 论', '四 无产阶级专政',
            '五 农民问题', '六 民族问题', '七 战略和策略', '八 党', '九 工作作风']


def is_header(line):
    t = line.strip()
    if not t:
        return False
    if '斯大林全集' in line and '第六卷' in line:
        return True
    if re.match(r'^论列宁主义基础\s*\d+\s*$', t):
        return True
    if re.match(r'^\d+\s*$', t):
        return True
    return False


def is_section(line):
    t = line.strip()
    return bool(re.match(r'^[一二三四五六七八九十]+\s+', t)) and len(t) < 20


def clean_text(s):
    s = re.sub(r'◇\d+◇', '', s)   # 页码标记
    s = re.sub(r'〔\d+〕', '', s)   # 全集注号（其注文在卷末，不收录）
    s = re.sub(r'\s+', '', s)      # 去掉所有空白（CJK 拼接）
    return s


def main():
    lines = open(SRC, encoding='utf-8').read().splitlines()
    # 按 PDFPAGE 分页，只取 PDF 1840-1924（论列宁主义基础部分）
    pages_raw = []
    cur = []
    for ln in lines:
        if ln.startswith('===== PDFPAGE 1925'):
            break
        if ln.startswith('===== PDFPAGE'):
            if cur:
                pages_raw.append(cur)
                cur = []
            continue
        if is_header(ln):
            continue
        cur.append(ln)
    if cur:
        pages_raw.append(cur)
    print('pdf pages:', len(pages_raw))

    # 首页的题名块（标题/副题/献词/署名）在正文首段之前，先剔除
    if pages_raw:
        page0 = pages_raw[0]
        first = 0
        for i, ln in enumerate(page0):
            if '列宁主义的基础是个很大的题目' in ln:
                first = i
                break
        pages_raw[0] = page0[first:]

    # —— 逐页解析：正文 + 页尾脚注块 ——
    # 正文块：('p', [lines]) / ('h3', text) / ('ref', marker)
    # 脚注块：('note', markers, [text_lines])
    body_blocks = []   # 最终: ('p', html) / ('h3', html)
    pending_refs = []  # 尚未配对的 ref 编号（FIFO）
    notes_map = {}     # ref编号 -> note html
    ref_cursor = 0

    def flush_para(cur_para, out):
        if cur_para:
            txt = clean_text(''.join(cur_para))
            # 行内 ① ② → 上标
            def repl(m):
                nonlocal ref_cursor
                ref_cursor += 1
                num = ref_cursor
                pending_refs.append(num)
                return '<sup class="fnref"><a href="#stln%d">[%d]</a></sup>' % (num, num)
            html = re.sub(r'[①②]', repl, txt)
            out.append(('p', html))
            return []
        return cur_para

    cur_para = []
    for page in pages_raw:
        in_fn = False
        cur_note = None
        page_had_fn = False
        for ln in page:
            if not ln.strip():
                continue
            if re.match(r'^—{4,}', ln.strip()):
                cur_para = flush_para(cur_para, body_blocks)
                in_fn = True
                page_had_fn = True
                continue
            if in_fn:
                m = re.match(r'^[\s\u3000]*([①②][、]?[①②]?)\s*(.*)$', ln)
                if m:
                    if cur_note is not None:
                        # 落地上一脚注
                        markers, ntext = cur_note
                        for _ in markers.replace('、', ''):
                            if pending_refs:
                                num = pending_refs.pop(0)
                                notes_map[num] = ntext
                    cur_note = (m.group(1), m.group(2))
                    continue
                else:
                    # 脚注续行
                    if cur_note is not None:
                        cur_note = (cur_note[0], cur_note[1] + '\n' + ln.strip())
                    continue
            # 正文行
            if is_section(ln):
                cur_para = flush_para(cur_para, body_blocks)
                body_blocks.append(('h3', clean_text(ln.strip())))
                continue
            if re.match(r'^ {4,}', ln) or re.match(r'^\u3000{2,}', ln):
                cur_para = flush_para(cur_para, body_blocks)
                cur_para = [ln]
            else:
                cur_para.append(ln)
        # 仅当该页有脚注块时才在页末收段（正文段落可跨页延续）
        if page_had_fn:
            cur_para = flush_para(cur_para, body_blocks)
        if cur_note is not None:
            markers, ntext = cur_note
            for _ in markers.replace('、', ''):
                if pending_refs:
                    num = pending_refs.pop(0)
                    notes_map[num] = ntext
    cur_para = flush_para(cur_para, body_blocks)

    # 未配对检查
    print('refs:', ref_cursor, '| paired notes:', len(notes_map), '| pending left:', len(pending_refs))
    for n, txt in notes_map.items():
        notes_map[n] = '<p class="note" id="stln%d">[%d]&ensp;%s</p>' % (n, n, clean_text(txt))

    # —— 按节切页 ——
    pages = []   # [{title, blocks, notes:set(n)}]
    cur_page = {'title': '引言', 'blocks': [], 'notes': []}
    sec_lookup = {}
    for s in SECTIONS:
        sec_lookup[clean_text(s)] = s
    for kind, data in body_blocks:
        if kind == 'h3' and data in sec_lookup:
            pages.append(cur_page)
            cur_page = {'title': sec_lookup[data], 'blocks': [], 'notes': []}
            continue
        cur_page['blocks'].append((kind, data))
        # 记录该块内的 ref 号
        for m in re.finditer(r'#stln(\d+)', data):
            num = int(m.group(1))
            if num not in cur_page['notes']:
                cur_page['notes'].append(num)
    pages.append(cur_page)

    # —— 渲染 ——
    entries = []
    for i, pg in enumerate(pages, 1):
        fname = '%02d-%s.html' % (i, re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', pg['title'])[:30])
        entries.append({'idx': i, 'title': pg['title'], 'fname': fname})
    toc_groups = [{'label': None, 'items': [{'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries]}]

    os.makedirs(WORKDIR, exist_ok=True)
    for i, pg in enumerate(pages, 1):
        e = entries[i - 1]
        prev = entries[i - 2] if i > 1 else None
        nxt = entries[i] if i < len(entries) else None
        body = []
        if i == 1:
            body.append({'kind': 'p', 'html': '献给为纪念列宁而吸收入党的同志们。'})
        for kind, html in pg['blocks']:
            body.append({'kind': kind, 'html': html})
        notes = []
        for n in pg['notes']:
            if n in notes_map:
                notes.append(notes_map[n])
        result = {
            'title': e['title'],
            'secdate': ('（在斯维尔德洛夫大学的讲演）<br>（一九二四年四月初至五月中旬）' if i == 1 else ''),
            'body': body,
            'notes': ([{'header': '注　释', 'items': notes}] if notes else []),
        }
        page_html = render_article(
            result, art_idx=1, brand='论列宁主义基础', voltag='《斯大林选集》上卷',
            toc_groups=toc_groups, active_href=e['fname'],
            prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
            nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
            vol_href='../%s' % LANDING,
            footer='文本整理自《新编斯大林全集》第六卷（1924年著作，《斯大林选集》上卷所收《论列宁主义基础》），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。',
            home_href='../../index.html', assets='../../assets',
        )
        with open(os.path.join(WORKDIR, e['fname']), 'w', encoding='utf-8') as f:
            f.write(page_html)
        print('wrote', os.path.join(WORKDIR, e['fname']))

    # —— 选卷页（位于 斯大林/<landing>.html，阅读页在 斯大林/论列宁主义基础/，链接需带目录前缀）——
    cards = []
    for i, e in enumerate(entries, 1):
        cards.append('''<a class="card" href="{href}">
  <div class="vol">{vol}</div>
  <div class="ed">1924年版</div>
  <div class="stat">{title}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(href='论列宁主义基础/' + e['fname'], vol='引言' if i == 1 else '第%d节' % (i - 1), title=e['title']))
    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《论列宁主义基础》选节首页">
<title>论列宁主义基础 · 选节首页</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 在 线 文 本 整 理</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>论列宁主义基础</h1>
    <div class="sub">在斯维尔德洛夫大学的讲演（一九二四年）</div>
    <div class="meta"><a href="../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    文本整理自《新编斯大林全集》第六卷（诸夏怀斯社版），仅作学习、研究参考之用；如与人民出版社纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>'''.format(cards='\n'.join(cards))
    with open(os.path.join(AUTHOR, LANDING), 'w', encoding='utf-8') as f:
        f.write(landing)
    print('wrote', os.path.join(AUTHOR, LANDING))

    json.dump({'pages': len(pages), 'landing': LANDING},
              open(os.path.join(ROOT, '.tools', 'stalin_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('pages:', len(pages))


if __name__ == '__main__':
    main()
