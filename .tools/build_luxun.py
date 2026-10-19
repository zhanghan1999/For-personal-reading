# -*- coding: utf-8 -*-
"""
build_luxun.py — 鲁迅「其他著作」栏目构建器（全集 + 单行本视图模式）。

数据源：.tools/sources/luxun/（github Ac-heron/luxun，md 文件）
结构：   全集/<单行本>/<篇目>.md
产出：   其他著作/鲁迅/
           ├── index.html          人物页（全集卡片 + 大单行本快捷卡片）
           ├── 鲁迅全集.html       全集选卷页（按单行本分组列出全部篇目）
           ├── 呐喊.html …         大单行本"视图"选卷页（指向全集同一批文件）
           └── 鲁迅全集/呐喊/01-狂人日记.html …  正文唯一存放（阅读页）

要点（对应 README 红线 11「全集通用规则」）：
- 正文唯一存放于 其他著作/鲁迅/鲁迅全集/<单行本>/；单行本选卷页只做视图，正文零重复。
- 阅读页 window.PAGE.tocGroups 按单行本分组；volHref 指向 鲁迅全集.html。
- 过滤源里的整理者附加文件：〈*〉目录.md / 简介.md / 2q 等。

用法：python .tools/build_luxun.py
"""
import os, re, sys, io, json, html as htmllib

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
LUXUN = os.path.join(ROOT, '其他著作', '鲁迅')
SRC = os.path.join(ROOT, '.tools', 'sources', 'luxun', '全集')

QUANJI = '鲁迅全集'
AUTHOR = '鲁迅'

# 需要过滤的非原文文件（整理者附加）：目录索引 / 简介等
FILTER_RX = re.compile(r'^(《.+》)?(目录|简介|前言|后记说明|出版说明)$|^2q$')

# 单行本卡片顺序（全集选卷页分组顺序）
VOL_ORDER = ['呐喊', '彷徨', '故事新编', '朝花夕拾', '野草',
             '坟', '热风', '华盖集', '华盖集续编', '华盖集续编的续编',
             '而已集', '三闲集', '二心集', '伪自由书']

# 大单行本：给独立"视图"选卷页 + 人物页快捷卡片
MAJOR_VOLS = ['呐喊', '彷徨', '故事新编', '朝花夕拾', '野草']

# 注标样式：四种并存
#   A. 全角方括号 〔N〕（主导，5338 处，N 可为全角数字）
#   B. 全角圆括号数字 ⑴⑵⑶…（U+2474–U+249B，89 处，常见于 呐喊/坟/而已集 等）
#   C. 半角方括号 ［N］（14 处，坟/写在《坟》后面、我们怎样做父亲）
#   D. 圆圈数字 ①②③…（87 处，阿Q正传/再论雷峰塔的倒掉/呐喊自序/离婚 等）
FULL_DIGITS = '０１２３４５６７８９'
HALF_DIGITS = '0123456789'
_TRANSLIT = str.maketrans(FULL_DIGITS, HALF_DIGITS)
PAREN_NUMS = ''.join(chr(0x2474 + i) for i in range(10))   # ⑴…⑽
CIRCLE_NUMS = ''.join(chr(0x2460 + i) for i in range(20))  # ①…⑳

# 匹配注标并捕获其数字（任意一种样式），group(1) 为半角数字字符串
NOTE_RE = re.compile(
    r'〔\s*([0-9%s]+)\s*〕'      # A: 〔N〕
    r'|［\s*([0-9%s]+)\s*］'     # C: ［N］
    r'|([%s])'                    # B: ⑴
    r'|([%s])'                    # D: ①
    % (FULL_DIGITS, FULL_DIGITS, PAREN_NUMS, CIRCLE_NUMS)
)

FULL_PRE = '　　'
SECTION_RE = re.compile(r'^[一二三四五六七八九十百千零〇\d]+\s*$')


def _is_fence_para(para_lines):
    """段落内容整体是 ``` 围栏残留。"""
    return all(not l.strip() or l.strip() == '```' for l in para_lines)


def _is_notes_header(para_lines):
    """注释区标题行：□注释 / 注释 / 注释：。"""
    s = merge_para(para_lines).strip()
    return s in ('□注释', '注释', '注', '注释：')


def _norm_digits(s):
    return s.translate(_TRANSLIT)


def note_num(m):
    """从 NOTE_RE 的 match 提取半角数字。"""
    if m.group(1) is not None:     # 〔N〕
        return _norm_digits(m.group(1))
    if m.group(2) is not None:     # ［N］
        return _norm_digits(m.group(2))
    if m.group(3) is not None:     # ⑴
        return str(ord(m.group(3)) - 0x2474 + 1)
    return str(ord(m.group(4)) - 0x2460 + 1)   # ①


def strip_fence(raw):
    """去掉首尾的 ``` 代码围栏（容忍末尾多余空行）。"""
    lines = raw.split('\n')
    while lines and lines[0].strip() == '```':
        lines.pop(0)
    # 从尾部剥掉空行和围栏，两者可交错出现
    while lines:
        s = lines[-1].strip()
        if s == '```' or s == '':
            lines.pop()
        else:
            break
    return '\n'.join(lines)


def strip_toc_prefix(text):
    """
    去掉整理者附加的目录前缀：形如
        《野草》目录：
        题辞
        秋夜
        …
        （之后才是正文标题）
    检测条件收紧：目录标记必须是**独立一行**、形如 《xxx》目录[:：] 且行尾就在目录字样上
    （正文里顺带提到"目录"二字的不算，如"目录已经整齐"）；其后跟随的必须是连续的无缩进短行
    （篇名列表）。
    """
    lines = text.split('\n')
    TOC_LINE = re.compile(r'^[《〈][^《〉]{1,20}[》〉]\s*目\s*录\s*[:：]?\s*$')
    # 找目录标记行
    idx = None
    for i, l in enumerate(lines):
        if TOC_LINE.match(l.strip()):
            idx = i
            break
    if idx is None:
        return text
    # 收集标记行之后的"目录列表"范围：允许开头空行；列表行无全角缩进且短；
    # 遇到全角缩进行（正文）或 超过 60 行 或 遇到第二个空行后的正文段则停。
    j = idx + 1
    seen_blank = False
    while j < len(lines):
        s = lines[j].strip()
        if not s:
            if seen_blank:
                break
            seen_blank = True
            j += 1
            continue
        if s.startswith('\u3000'):
            break                      # 正文（全角缩进）
        if len(s) > 40:
            break                      # 过长，不是篇名
        if j - idx > 60:
            break
        seen_blank = False
        j += 1
    rest = '\n'.join(lines[j:])
    return rest


def split_paragraphs(text):
    """
    分段规则（兼容两种源风格）：
    - 空行 → 强制分段；
    - 无空行时：行首为全角缩进（　　）且上一行不是全角缩进开头 → 新段；
      （热风/狂人小序等"连续流"风格：段首全角缩进、续行顶格/半角）
    - 否则并入当前段（续行，折行合并）。
    返回 [ [line,...], ... ]（行保留原始缩进）。
    """
    paras = []
    cur = []
    for ln in text.split('\n'):
        if not ln.strip():
            if cur:
                paras.append(cur)
                cur = []
            continue
        if ln.strip() == '```':
            # 围栏残留行：当作段边界（若已在段中则断段）
            if cur:
                paras.append(cur)
                cur = []
            continue
        starts_fullwidth = ln.startswith('\u3000')
        if cur and starts_fullwidth and not cur[-1].startswith('\u3000'):
            # 上一行非全角缩进（顶格续行），本行全角缩进 → 新段
            paras.append(cur)
            cur = []
        cur.append(ln)
    if cur:
        paras.append(cur)
    return paras


def clean_line(ln):
    """去行首全角/半角缩进，去行尾空白。"""
    return ln.lstrip('\u3000 ').rstrip()


def merge_para(lines):
    """合并一个段内的折行：去掉行首缩进后直接拼接（鲁迅 md 折行无标点分隔）。"""
    return ''.join(clean_line(l) for l in lines)


def is_book_head(para_lines):
    """书头行：形如 鲁迅《热风》 / 鲁迅《故事新编》 的独立一行（单行本内多篇重复出现）。"""
    if len(para_lines) != 1:
        return False
    s = clean_line(para_lines[0])
    return bool(re.fullmatch(r'鲁迅[《〈].+[》〉]', s))


def looks_like_title(para_lines):
    """标题段：1-2 行、短、不含标点句号、非书头。"""
    txt = merge_para(para_lines)
    if not txt or len(txt) > 60:
        return False
    if '。' in txt or '，' in txt or '；' in txt or '：' in txt:
        return False
    return True


def split_title_and_notes(paras):
    """
    返回 (title, body_paras, note_paras)
    - 跳过开头书头段
    - 取第一个像标题的段为标题（剥掉〔N〕注标）
    - 正文段 = 标题之后、注释区之前的段
    - 注释区 = 以〔N〕开头的段（段首就是注标）
    """
    i = 0
    # 跳过书头
    if i < len(paras) and is_book_head(paras[i]):
        i += 1
    # 找标题（允许开头先出现 1-2 个短说明段，如 序言/题辞 的卷首说明）
    title = ''
    body_start = 0
    scan = i
    while scan < len(paras):
        p = paras[scan]
        if _is_fence_para(p):
            scan += 1
            continue
        # 注释区开始？
        first = clean_line(p[0]) if p else ''
        if NOTE_RE.match(first) or _is_notes_header(p):
            break
        if looks_like_title(p):
            title = NOTE_RE.sub('', merge_para(p)).strip()
            body_start = scan + 1
            break
        scan += 1
    if not title:
        # 兜底：第一篇目文件名（无 .md）
        return '', [], []
    # 分割正文与注释
    body_paras = []
    note_paras = []
    seen_notes_header = False
    j = body_start
    while j < len(paras):
        p = paras[j]
        if _is_fence_para(p):
            j += 1
            continue
        first = clean_line(p[0]) if p else ''
        if _is_notes_header(p):
            seen_notes_header = True
            j += 1
            continue
        if NOTE_RE.match(first) and (seen_notes_header or len(clean_line(p[0])) > 2):
            # 注释区条目：若段内含多个注标（如 〔１〕…〔２〕… 无空行黏连），按注标拆开
            merged = merge_para(p)
            note_paras.extend(_split_note_para(merged))
        else:
            body_paras.append(merge_para(p))
        j += 1
    return title, body_paras, note_paras


def _split_note_para(text):
    """把一段注释文本按注标拆成多条注释（源注释区无空行时多条黏连）。"""
    matches = list(NOTE_RE.finditer(text))
    if not matches:
        return [text]
    parts = []
    for k, m in enumerate(matches):
        start = m.start()
        end = matches[k + 1].start() if k + 1 < len(matches) else len(text)
        parts.append(text[start:end])
    return parts


def parse_note_item(text):
    """解析一条注释：〔N〕 或 ⑴ 开头的文本 → (num, body)。"""
    m = NOTE_RE.match(text)
    if not m:
        return None, text
    num = note_num(m)
    rest = text[m.end():].lstrip('\u3000 ')
    return num, rest


def convert_to_html(title, body_paras, note_paras):
    """
    把解析出的段落转成 render_article 的 body 块 + notes。
    - 注释区：〔N〕 → p.note（id=lxnN）
    - 正文段：p（段内〔N〕仅当注释区存在该编号 → sup.fnref 悬浮脚注；
      否则保留原文〔N〕——源注释区跳号时避免悬空链接）
    """
    # 先收集注释区存在的编号集合
    note_nums = set()
    for text in note_paras:
        num, _ = parse_note_item(text)
        if num is not None:
            note_nums.add(num)

    body = []
    for text in body_paras:
        # 小节编号行（一/二/三… 或纯数字）→ h3 小标题（毛选风格）
        if SECTION_RE.match(text):
            body.append({'kind': 'h3', 'html': htmllib.escape(text)})
            continue
        # 先转义全文，再替换注标为脚注标签（注标字符不受 escape 影响）
        t = htmllib.escape(text)
        def repl(m):
            n = note_num(m)
            if n in note_nums:
                return '<sup class="fnref"><a href="#lxn-%s">[%s]</a></sup>' % (n, n)
            return m.group(0)   # 源注释区无此编号，保留原文注标
        t = NOTE_RE.sub(repl, t)
        body.append({'kind': 'p', 'html': t})

    notes = []
    note_items_html = []
    for text in note_paras:
        num, rest = parse_note_item(text)
        # 注释体内部可能还引用其他注标（嵌套），剥掉内层注标防错
        rest = NOTE_RE.sub(lambda m: '', rest)
        if num is None:
            # 无注标但位于注释区的文本，作为普通注释段（可能是注释区导语）
            note_items_html.append('<p class="note">%s</p>' % htmllib.escape(rest))
            continue
        note_items_html.append('<p class="note" id="lxn-%s">[%s]　%s</p>'
                               % (num, num, htmllib.escape(rest)))
    if note_items_html:
        notes.append({'header': '注　释', 'items': note_items_html})
    return body, notes


def cn_num(n):
    """全角数字 → 半角（用于 [N] 显示）。"""
    return _norm_digits(n)


def build_all():
    vols = {}
    for v in os.listdir(SRC):
        d = os.path.join(SRC, v)
        if not os.path.isdir(d):
            continue
        if v not in VOL_ORDER:
            continue
        items = []
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.md'):
                continue
            stem = fn[:-3]
            if FILTER_RX.match(stem):
                print('  [过滤] %s/%s' % (v, fn))
                continue
            raw = open(os.path.join(d, fn), encoding='utf-8', errors='replace').read()
            text = strip_fence(raw)
            text = strip_toc_prefix(text)
            paras = split_paragraphs(text)
            title, body_paras, note_paras = split_title_and_notes(paras)
            if not title:
                print('  [警告] %s/%s 无标题，用文件名' % (v, fn))
                title = stem
            items.append({'stem': stem, 'title': title, 'body': body_paras,
                          'notes': note_paras})
        if items:
            vols[v] = items
    return vols


def main():
    print('==== 解析鲁迅源数据 ====')
    # 清理旧产物（防止注标/标题变更后残留旧文件）
    if os.path.isdir(LUXUN):
        for fn in os.listdir(LUXUN):
            p = os.path.join(LUXUN, fn)
            if fn == 'index.html':
                continue
            if os.path.isdir(p):
                import shutil
                shutil.rmtree(p)
            else:
                os.remove(p)
        print('  已清理旧产物:', LUXUN)

    vols = build_all()
    total = sum(len(items) for items in vols.values())
    print('单行本数:', len(vols), ' 篇目总数:', total)

    os.makedirs(os.path.join(LUXUN, QUANJI), exist_ok=True)

    # ============ 1. 阅读页（正文唯一存放） ============
    entries = {}   # vol -> [entry]
    for vi, vol in enumerate(VOL_ORDER):
        items = vols.get(vol)
        if not items:
            continue
        vol_dir = os.path.join(LUXUN, QUANJI, vol)
        os.makedirs(vol_dir, exist_ok=True)
        vol_entries = []
        for i, it in enumerate(items, 1):
            fname = '%02d-%s.html' % (i, re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', it['title'])[:40])
            vol_entries.append({'num': str(i), 'title': it['title'], 'href': fname})
            body, notes = convert_to_html(it['title'], it['body'], it['notes'])
            result = {'title': it['title'], 'secdate': '', 'body': body, 'notes': notes}
            # 上一篇/下一篇：单行本内接续（跨单行本不连，同毛选卷内接续）
            prev = vol_entries[i - 2] if i >= 2 else None
            nxt = None
            page_html = render_article(
                result, art_idx=1,
                brand='鲁迅全集 · %s' % vol,
                voltag='鲁迅 著',
                toc_groups=None,          # 阅读页目录由全集分组（见下）
                active_href=fname,
                prev={'href': prev['href'], 'title': prev['title']} if prev else None,
                nxt=nxt,
                vol_href='../../鲁迅全集.html',
                footer='文本整理自公开电子资料（github Ac-heron/luxun），仅供学习研究参考；'
                       '如与人民文学出版社《鲁迅全集》纸质版有出入，以纸质版为准。',
                home_href='../../../../index.html', assets='../../../../assets',
            )
            with open(os.path.join(vol_dir, fname), 'w', encoding='utf-8') as f:
                f.write(page_html)
        entries[vol] = vol_entries
        print('  阅读页: %s %d 篇' % (vol, len(vol_entries)))

    # ============ 2. 阅读页 tocGroups 回填（跨单行本目录分组） ============
    # 阅读页目录需要"按单行本分组"显示全集结构，且 href 指向同卷内文件（相对自身深度）
    # 阅读页位于 鲁迅全集/<vol>/，目录里本卷条目用本卷文件名，其他卷用 ../<vol2>/<file>
    for vol, vol_entries in entries.items():
        groups = []
        for v2 in VOL_ORDER:
            e2 = entries.get(v2)
            if not e2:
                continue
            prefix = '' if v2 == vol else '../%s/' % v2
            items = [{'num': e['num'], 'title': e['title'],
                      'href': prefix + e['href']} for e in e2]
            groups.append({'label': v2, 'items': items})
        vol_dir = os.path.join(LUXUN, QUANJI, vol)
        for e in vol_entries:
            fp = os.path.join(vol_dir, e['href'])
            with open(fp, encoding='utf-8') as f:
                html = f.read()
            # 替换 window.PAGE 里的 tocGroups
            html = re.sub(r'"tocGroups":\s*[^,]*', '"tocGroups": %s' % json.dumps(groups, ensure_ascii=False), html, count=1)
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(html)
    print('  已回填阅读页 tocGroups（按单行本分组）')

    # ============ 3. 全集选卷页（按单行本分组卡片） ============
    group_blocks = []
    for v in VOL_ORDER:
        e = entries.get(v)
        if not e:
            continue
        cards = '\n'.join('''<a class="card" href="%s/%s/%s">
  <div class="vol">%s</div>
  <div class="ed">%s 篇</div>
  <div class="go">打开阅读 &#8594;</div>
</a>''' % (QUANJI, v, ent['href'], ent['title'], ent['num']) for ent in e)
        group_blocks.append('<div class="zone-title">%s</div>\n<div class="cards">\n%s\n</div>' % (v, cards))
    quanji_page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="鲁迅全集 · 全部著作">
<title>鲁迅全集 · 全部著作</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">其 他 著 作 · 鲁 迅</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">鲁迅全集</h1>
    <div class="sub">按单行本分组 · 全部篇目</div>
    <div class="meta"><a href="index.html">&#8678; 返回鲁迅</a></div>
  </header>
  <main>
{groups}
  </main>
  <footer>
    文本整理自公开电子资料（github Ac-heron/luxun），仅供学习研究参考；如与人民文学出版社《鲁迅全集》纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>'''.format(groups='\n'.join(group_blocks))
    with open(os.path.join(LUXUN, QUANJI + '.html'), 'w', encoding='utf-8') as f:
        f.write(quanji_page)
    print('  全集选卷页: %s.html' % QUANJI)

    # ============ 4. 大单行本"视图"选卷页 ============
    for v in MAJOR_VOLS:
        e = entries.get(v)
        if not e:
            continue
        cards = '\n'.join('''<a class="card" href="%s/%s/%s">
  <div class="vol">%s</div>
  <div class="ed">第 %s 篇</div>
  <div class="go">打开阅读 &#8594;</div>
</a>''' % (QUANJI, v, ent['href'], ent['title'], ent['num']) for ent in e)
        page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《%s》 · 鲁迅">
<title>%s · 鲁迅</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">其 他 著 作 · 鲁 迅</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>%s</h1>
    <div class="sub">鲁迅 著 · 全%d篇</div>
    <div class="meta"><a href="index.html">&#8678; 返回鲁迅</a> · <a href="%s.html">&#8678; 全集</a></div>
  </header>
  <main class="cards">
%s
  </main>
  <footer>
    文本整理自公开电子资料（github Ac-heron/luxun），仅供学习研究参考；如与人民文学出版社《鲁迅全集》纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>''' % (v, v, v, len(e), QUANJI, cards)
        with open(os.path.join(LUXUN, '%s.html' % v), 'w', encoding='utf-8') as f:
            f.write(page)
        print('  单行本视图选卷页: %s.html' % v)

    # ============ 5. 人物页 index.html ============
    major_cards = '\n'.join('''<a class="card" href="%s.html">
  <div class="vol">%s</div>
  <div class="stat">%d 篇</div>
  <div class="go">进入阅读 &#8594;</div>
</a>''' % (v, v, len(entries[v])) for v in MAJOR_VOLS if v in entries)
    index_page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="鲁迅 · 其他著作">
<title>鲁迅 · 其他著作</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">其 他 著 作 · 鲁 迅</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">鲁迅</h1>
    <div class="sub">周树人（1881—1936） · 文学家、思想家、革命家</div>
    <div class="meta"><a href="../../index.html">&#8678; 返回首页</a></div>
  </header>
  <main class="cards">
<a class="card" href="鲁迅全集.html">
  <div class="vol">鲁迅全集</div>
  <div class="stat">%d 篇 · 按单行本分组</div>
  <div class="go">进入全集 &#8594;</div>
</a>
%s
  </main>
  <footer>
    鲁迅（周树人），中国现代文学奠基人。本文集整理自公开电子资料（github Ac-heron/luxun），
    以《呐喊》《彷徨》《故事新编》《朝花夕拾》《野草》五部文学单行本为全集入口，
    其余杂文集见全集分组。文本仅供学习研究参考；如与纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>''' % (total, major_cards)
    os.makedirs(LUXUN, exist_ok=True)
    with open(os.path.join(LUXUN, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_page)
    print('  人物页: index.html')

    print('==== 构建完成 ====')


if __name__ == '__main__':
    main()
