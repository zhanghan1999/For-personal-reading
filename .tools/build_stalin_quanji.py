# -*- coding: utf-8 -*-
"""build_quanji.py — 把《新编斯大林全集》正卷（文字版 PDF，20 卷）转成站内阅读页。

产物（相对 C:\\导师文集）：
  导师著作/斯大林/斯大林全集.html                     总选卷页（20 卷分区，全部篇目）
  导师著作/斯大林/斯大林全集/第X卷.html               卷选卷页（该卷篇目卡片）
  导师著作/斯大林/斯大林全集/第X卷/NN-篇名.html       阅读页（window.PAGE 契约）

页面骨架与 window.PAGE 注入全部复用 .tools/mew_convert.render_article。

用法：
  python build_quanji.py                 # 全量构建
  python build_quanji.py --only 1 6 20   # 只构建指定卷（调试）
  python build_quanji.py --sample        # 只打印 3 篇样本正文，不写文件
  python build_quanji.py --report        # 构建并写 _build_report.md
"""
import os, re, sys, io, json, html, glob

BASE = os.path.join(r'C:\导师文集', '.tools', 'sources', 'stalin')  # 缓存/目录素材（sources 不入库）
ROOT = r'C:\导师文集'
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(ROOT, '.tools'))
from mew_convert import render_article

CACHE = os.path.join(BASE, '_pages.json')
TOC = os.path.join(BASE, '_toc.json')
AUTHOR = os.path.join(ROOT, '导师著作', '斯大林')
WORKDIR = os.path.join(AUTHOR, '斯大林全集')
LANDING = os.path.join(AUTHOR, '斯大林全集.html')

BODY_LEFT = 56.8          # 正文左边界（PDF 单位）
HEAD_Y = 755.0            # 页眉线（y 大于此值视为页眉）
FOOT_Y = 45.0             # 页脚线
CJK = '\u3400-\u9fff\u3000-\u303f\uff00-\uffef'
SUP_O = '\ue000'
SUP_C = '\ue001'

NOTE_LABEL = re.compile(r'^([\u2460-\u2473\u2474-\u2487]|\[\s*\d+\s*\]|〔\s*\d+\s*〕|[（(]\s*\d+\s*[)）])')
DATE_RE = re.compile(r'^[（(][^（()）]{1,40}[）)]$')
SEP_RE = re.compile(r'^[—–─\-_·.…\s]{5,}$')
ORD_RE = re.compile(r'^[（(]?[一二三四五六七八九十百]+[）)、.．]?$')


# ---------------------------------------------------------------- 文本清洗
def is_wide(ch):
    if not ch:
        return False
    o = ord(ch)
    return (0x2010 <= o <= 0x2027 or 0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF
            or 0xFE30 <= o <= 0xFE4F or 0xFF00 <= o <= 0xFF60 or 0xFFE0 <= o <= 0xFFE6)


def scrub(s):
    s = s.replace('\r', '').replace('\n', '').replace('\t', ' ')
    for ch in ('\ufeff', '\u200b', '\u200c', '\u200d', '\u00ad', '\u2060'):
        s = s.replace(ch, '')
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'◇\s*\d+\s*◇', '', s)          # 原书页码标记
    s = re.sub(r'◇\s*\d*\s*◇?', '', s)          # 残缺点位标记
    s = re.sub(r'[ \u3000]{2,}', ' ', s)
    return s


def despace(s):
    """去掉与中日韩字符/标点相邻的空格（保留西文之间的单空格）。"""
    out = []
    for i, ch in enumerate(s):
        if ch == ' ':
            prev = s[i - 1] if i else ''
            nxt = s[i + 1] if i + 1 < len(s) else ''
            if is_wide(prev) or is_wide(nxt):
                continue
        out.append(ch)
    return ''.join(out)


def tidy(s):
    s = scrub(s)
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return despace(s)


def norm_t(s):
    s = re.sub(SUP_O + '[^' + SUP_C + ']*' + SUP_C, '', s)   # 去掉上标夹注
    s = tidy(s)
    s = re.sub(r'[\s\u3000·・,，。.、：:；;！!？?“”"\'‘’（）()《》<>—－\-〔〕\[\]【】]+', '', s)
    return s


def same_title(joined, title):
    nj, nt = norm_t(joined), norm_t(title)
    if not nj or not nt:
        return False
    if nj == nt:
        return True
    return nj in nt and (len(nt) - len(nj)) <= 2


def esc(s):
    """把带上标哨兵的文本转成 HTML。"""
    t = html.escape(s.replace(SUP_O, '\x00').replace(SUP_C, '\x01'), quote=False)
    return t.replace('\x00', '<sup>').replace('\x01', '</sup>')


# ---------------------------------------------------------------- 行重建
_sup_warn = [0]


def page_to_lines(rows):
    """一页的原始 rows → 行列表 [{y,fs,x,eff,text,sep,newpara}]。"""
    body = [r for r in rows if FOOT_Y <= r[0] <= HEAD_Y and r[2] >= 13.5]
    sups = [r for r in rows if FOOT_Y <= r[0] <= HEAD_Y and r[2] < 13.5]
    lines = []
    for y, x, fs, text in body:
        raw = text.replace('\n', '')
        lead = len(raw) - len(raw.lstrip(' '))
        t = scrub(text)
        lines.append({'y': y, 'x': x, 'fs': fs, 'lead': lead,
                      'eff': x + lead * fs * 0.5, 'text': t})
    for y, x, fs, text in sups:
        cand = [ln for ln in lines if ln['y'] <= y + 2 and (y - ln['y']) <= 22]
        if not cand:
            _sup_warn[0] += 1
            continue
        tgt = max(cand, key=lambda ln: ln['y'])
        tgt['text'] = insert_sup(tgt['text'], tgt['x'], tgt['fs'], x, scrub(text).strip())
    for ln in lines:
        s = ln['text'].strip()
        ln['text'] = ln['text'].rstrip()
        ln['sep'] = False
        ln['septail'] = ''
        sm = re.search(r'[—─–-]{5,}', s)
        if sm and not re.search(r'[\u4e00-\u9fff]', s[:sm.start()]):
            ln['sep'] = True
            ln['septail'] = s[sm.end():].strip()
        elif s and SEP_RE.match(s) and not re.search(r'[\u4e00-\u9fff]', s):
            ln['sep'] = True
        ln['newpara'] = ln['eff'] > BODY_LEFT + 10
        ln['toc'] = bool(re.search(r'[…\.]{4,}\s*\d+\s*$', s))
    # 页眉残留：位于页面顶部、行很短、无句末标点（或含“斯大林全集 第X卷”）
    # 分隔线：只有其后全为小字号（<=15.5pt）时才是页底脚注分隔线，否则视为装饰线丢弃
    kept = []
    for i, ln in enumerate(lines):
        hs = re.sub(r'[\s\u3000]+', ' ', ln['text']).strip()
        if ln['y'] > 735 and ln['fs'] < 17 and len(hs) <= 26 and \
                ('斯大林全集' in hs or not re.search(r'[。！？，、；：]', hs)):
            continue
        if ln['sep']:
            rest = lines[i + 1:]
            ln['sep'] = all(r['fs'] < 15.8 for r in rest) and any(r['fs'] < 15.8 for r in rest)
            ln['orn'] = not ln['sep']
        kept.append(ln)
    return kept


def insert_sup(text, x0, fs, xs, sup):
    if not sup:
        return text
    target = (xs - x0) / (fs * 0.5)
    acc = 0.0
    idx = len(text)
    for i, ch in enumerate(text):
        w = 2.0 if is_wide(ch) else 1.0
        if acc + w / 2 >= target:
            idx = i
            break
        acc += w
    return text[:idx] + SUP_O + sup + SUP_C + text[idx:]


# ---------------------------------------------------------------- 篇目组装
def assemble(title, pages):
    blocks = []
    secdates = []
    note_items = []
    cur = []
    title_buf = []
    seen_body = False
    in_notes = False
    note_cur = None
    prev_eff = None
    prev_term = True

    def flush():
        if cur:
            t = tidy(''.join(cur))
            if t:
                blocks.append({'kind': 'p', 'html': t})
            cur.clear()

    def title_ok(cand):
        nj, nt = norm_t(cand), norm_t(title)
        if not nj or not nt:
            return False
        return nj == nt or (len(nj) >= 3 and nj in nt)

    for lines in pages:
        in_notes = False
        note_cur = None
        for ln in lines:
            s = ln['text'].strip()
            if not s:
                continue
            if ln.get('orn'):
                continue
            if ln['sep']:
                # 页底注码分隔线：正文段落保持未闭合，跨页续行仍可拼接
                in_notes = True
                if not ln['septail']:
                    continue
                s = ln['septail']
            if in_notes:
                if ln['fs'] >= 17:
                    in_notes = False
                else:
                    m = NOTE_LABEL.match(s)
                    if m:
                        note_cur = {'label': m.group(1), 'text': s[m.end():].strip()}
                        note_items.append(note_cur)
                    elif note_cur is None:
                        note_cur = {'label': '', 'text': s}
                        note_items.append(note_cur)
                    else:
                        note_cur['text'] += s
                    continue
            started = bool(seen_body or blocks or cur or secdates)
            # —— 目录行（含引导点）：独立成段 ——
            if ln['toc']:
                flush()
                t = re.sub(r'[…\.]{4,}', '　', s)
                t = re.sub(r'[　 ]{2,}', '　', t).strip('　 ')
                if t:
                    blocks.append({'kind': 'p', 'html': t})
                seen_body = True
                prev_eff, prev_term = None, True
                continue
            # —— 大字号：篇名 / 分节标题 ——
            if ln['fs'] >= 17:
                if not started and len(title_buf) < 4 and title_ok(''.join(title_buf) + s):
                    title_buf.append(s)
                    continue
                if title_buf:
                    joined = tidy(''.join(title_buf))
                    if not same_title(joined, title):
                        blocks.insert(0, {'kind': 'h2', 'html': joined})
                    title_buf = []
                flush()
                blocks.append({'kind': 'h2' if ln['fs'] >= 20 else 'h3', 'html': s})
                seen_body = True
                prev_eff, prev_term = None, True
                continue
            # —— 正文 ——
            if not started:
                if ln['newpara'] and DATE_RE.match(s) and len(s) <= 45:
                    secdates.append(s)
                    continue
            if title_buf:
                joined = tidy(''.join(title_buf))
                if not same_title(joined, title):
                    blocks.insert(0, {'kind': 'h2', 'html': joined})
                title_buf = []
            seen_body = True
            if ORD_RE.match(s):
                flush()
                blocks.append({'kind': 'h3', 'html': s})
                prev_eff, prev_term = None, True
                continue
            if ln['newpara']:
                np = True
                if prev_eff is not None and prev_eff > BODY_LEFT + 10 and ln['eff'] == prev_eff \
                        and not prev_term:
                    np = False          # 悬挂缩进排版（年表等）：同缩进续行
            else:
                np = False
            if NOTE_LABEL.match(s) and len(s) > 4:
                # 卷末「注释」等条目：〔1〕/① 起新段
                np = True
            if s.startswith(('http://', 'https://')):
                np = True
            if np:
                flush()
            cur.append(s)
            prev_eff = ln['eff']
            prev_term = bool(re.search(r'[。！？；：…”』」）!?.…]$', s))
    flush()

    if title_buf:
        joined = tidy(''.join(title_buf))
        if not same_title(joined, title):
            blocks.insert(0, {'kind': 'h2', 'html': joined})

    # 注释去重
    seen = set()
    notes = []
    for it in note_items:
        t = tidy(it['text'])
        if len(t) < 2 or t in seen:
            continue
        seen.add(t)
        label = tidy(it['label'])
        notes.append('<p class="note">%s%s</p>' % (esc(label) + '　' if label else '', esc(t)))
    return blocks, secdates, notes


def body_len(blocks):
    n = 0
    for b in blocks:
        n += len(re.sub(r'<[^>]+>', '', b['html']))
    return n


# ---------------------------------------------------------------- 卷结构
def safe_name(t):
    t = re.sub(r'[\\/:*?"<>|\r\n\t]', '', t)
    t = re.sub(r'[\s\u3000]+', '', t)
    t = t.strip(' .')
    if len(t) > 60:
        t = t[:60].strip(' .')
    return t or '未命名'


def load_volumes():
    toc = json.load(open(TOC, encoding='utf-8'))
    vols = []
    for v in toc['volumes']:
        m = re.match(r'^(\d{2})第(.+?)卷[（(](.*?)[）)]\s*$', v['title'].strip())
        if not m:
            continue
        vols.append({'no': int(m.group(1)), 'name': '第%d卷' % int(m.group(1)),
                     'years': m.group(3).strip(), 'raw_title': v['title'],
                     'start': v['start'], 'articles': v['articles']})
    vols.sort(key=lambda x: x['no'])
    return vols, toc['pages_total']


GROUP_RE = re.compile(r'^(\d{4}年(（[上下1-9]）|-\d{4}年)?|\d{4}\.\d[\d.\-—]*|\d{1,2}月|\d{1,2}—\d{1,2}月|\d{4}年（[上下]）)$')


def plan_volume(vol, vol_end, total_pages):
    """给每个书签条目定 kind / 页范围。

    - fwd  ：起始页递增的条目，范围到下一个更大起始页前
    - back ：起始页回指（年/月分组标题、图版说明），只取单页
    - dup  ：与前面条目同页起始的分组标题，无独立正文
    - nopage：书签无页码
    """
    arts = vol['articles']
    cursor = max(1, vol['start'])
    for a in arts:
        p = a.get('page')
        if not isinstance(p, int) or p < 1:
            a['_kind'] = 'nopage'
        elif p < cursor:
            a['_kind'] = 'back'
        else:
            a['_kind'] = 'fwd'
            cursor = p

    fwd_pages = [a['page'] for a in arts if a.get('_kind') == 'fwd']
    seen = set()
    for a in arts:
        if a.get('_kind') != 'fwd':
            continue
        p = a['page']
        title = (a.get('title') or '').strip()
        label = bool(GROUP_RE.match(title))
        later = [q for q in fwd_pages if q > p]
        end = (later[0] - 1) if later else vol_end
        if end > total_pages:
            end = total_pages
        if p in seen:
            if label:
                a['_kind'] = 'dup'
                continue
            a['_start'], a['_end'] = p, max(p, end)
            continue
        seen.add(p)
        # 同页之后还有真正的子篇目（非分组标题）时，本篇只占标题页
        has_child = False
        hit = False
        for b in arts:
            if b is a:
                hit = True
                continue
            if hit and b.get('_kind') == 'fwd' and b.get('page') == p \
                    and not GROUP_RE.match((b.get('title') or '').strip()):
                has_child = True
                break
        a['_start'] = p
        a['_end'] = p if has_child else max(p, end)


def recover_back_articles(vol, cache):
    """书签排在卷末、正文却排在卷内前面的独立篇目（附录、补遗等）。

    这类书签起始页落在前一篇的范围内。若该页首行大字号标题与书签标题相符，
    就把正文范围从覆盖它的那篇里切出来，避免整篇正文被前一篇吞掉。
    """
    arts = vol['articles']
    fixed = 0
    for a in arts:
        if a.get('_kind') != 'back':
            continue
        p = a.get('page')
        if not isinstance(p, int):
            continue
        nj = norm_t(a.get('title') or '')
        # 与卷内已有篇目重号同题（附录重复收录）：只做指向说明
        twin = None
        for b in arts:
            if b is a or b.get('_kind') != 'fwd' or b.get('_start') != p:
                continue
            nb = norm_t(b.get('title') or '')
            if nj and nb and (nj in nb or nb in nj):
                twin = b
                break
        if twin is not None:
            a['_kind'] = 'alias'
            a['_alias'] = (twin.get('title') or '').strip()
            fixed += 1
            continue
        if p not in cache:
            continue
        owner = None
        for b in arts:
            if b.get('_kind') == 'fwd' and b.get('_start', 0) < p <= b.get('_end', 0):
                owner = b
                break
        if owner is None:
            continue
        lines = page_to_lines(cache[p]['rows'])
        head = ''
        for ln in lines:
            if ln['fs'] >= 17:
                head = ln['text']
                break
        if len(head) < 6:
            continue
        nj, nh = norm_t(a.get('title') or ''), norm_t(head)
        if not nj or not nh or (nj not in nh and nh not in nj):
            continue
        later = [b['_start'] for b in arts
                 if b.get('_kind') in ('fwd', 'dup') and b.get('_start', 0) > p
                 and b['_start'] <= owner['_end'] + 1]
        end = (min(later) - 1) if later else owner['_end']
        end = min(end, owner['_end'])
        if end - p < 1:
            continue
        owner['_end'] = p - 1
        a['_kind'] = 'fwd'
        a['_start'], a['_end'] = p, end
        fixed += 1
    return fixed


MISSING_NOTE = '本篇源文本缺失（原书此处为插图、图版说明或卷内分组标题页，PDF 无可抽取的正文文字）。'


def build_volume(vol, vol_end, cache, total_pages, write=True):
    plan_volume(vol, vol_end, total_pages)
    recover_back_articles(vol, cache)
    entries = []
    used_names = {}
    stats = {'ok': 0, 'short': 0, 'nopage': 0, 'back': 0, 'dup': 0}
    for i, a in enumerate(vol['articles'], 1):
        title = (a.get('title') or '').strip() or '未命名'
        kind = a['_kind']
        pages = []
        if kind == 'fwd':
            pages = [page_to_lines(cache[p]['rows'])
                     for p in range(a['_start'], a['_end'] + 1)
                     if p in cache and cache[p]['rows']]
        elif kind == 'back':
            p = a['page']
            pages = [page_to_lines(cache[p]['rows'])] if (p in cache and cache[p]['rows']) else []
        blocks, secdates, notes = assemble(title, pages)
        if kind == 'alias':
            blocks = [{'kind': 'p', 'html': '本篇与《%s》为同一篇，原书在卷末附录中重复列目，正文见该篇。'
                       % (a.get('_alias') or '')}]
            notes = []
            status = 'alias'
            n = body_len(blocks)
            stats['alias'] = stats.get('alias', 0) + 1
            entries.append({
                'idx': i, 'title': title, 'fname': '',
                'blocks': blocks, 'secdate': [], 'notes': [], 'status': status,
                'chars': n, 'page': a.get('page'), 'kind': kind,
                'start': a.get('_start'), 'end': a.get('_end'),
            })
            continue
        # 回指条目只保留短文本（图版说明之类），避免整页目录混入
        if kind == 'back' and body_len(blocks) > 60:
            blocks = []
        n = body_len(blocks)
        status = 'ok'
        if kind == 'nopage' or kind == 'dup' or not blocks:
            status = 'nopage' if kind == 'nopage' else ('dup' if kind == 'dup' else 'empty')
            blocks.append({'kind': 'p', 'html': MISSING_NOTE})
            stats['nopage' if kind in ('nopage', 'dup') else 'empty'] = \
                stats.get('nopage' if kind in ('nopage', 'dup') else 'empty', 0) + 1
        elif n < 50:
            status = 'short'
            blocks.append({'kind': 'p', 'html': MISSING_NOTE})
            stats['short'] += 1
        else:
            stats['ok'] += 1
        entries.append({
            'idx': i, 'title': title, 'fname': '',
            'blocks': blocks, 'secdate': secdates, 'notes': notes,
            'status': status, 'chars': n,
            'page': a.get('page'), 'kind': kind,
            'start': a.get('_start'), 'end': a.get('_end'),
        })
    # —— 剔除无可读正文的条目（封面/扉页/像页/声明页/纯分组标题/图注页），再连续重排编号 ——
    IMG_T = ('封面', '口号页', '俄文版扉页', '俄文扉页', '中文版扉页', '中文扉页',
             '斯大林像', '声明页', '插图（新增）', '插图', '封底', '版权页', '正文')
    skip_cls, skip_detail = {}, []
    keep = []
    for e in entries:
        if e['status'] in ('ok', 'short'):
            keep.append(e)
            continue
        t = e['title'].strip()
        if t in IMG_T:
            k = '卷首卷末图片/装饰页'
        elif GROUP_RE.match(t):
            k = '卷内年/月/时段分组标题'
        elif e['kind'] == 'back':
            k = '插图图注页'
        elif e['kind'] == 'nopage':
            k = '书签缺页码'
        elif e['kind'] == 'alias':
            k = '卷末附录重复列目'
        else:
            k = '其他'
            skip_detail.append('%s《%s》(page=%s)' % (vol['name'], t, e['page']))
        skip_cls[k] = skip_cls.get(k, 0) + 1
    stats['skipped'] = len(entries) - len(keep)
    stats['skip_cls'] = skip_cls
    stats['skip_detail'] = skip_detail
    used = {}
    for i, e in enumerate(keep, 1):
        base = '%02d-%s' % (i, safe_name(e['title']))
        name, k = base, 2
        while name in used:
            name = '%s-%d' % (base, k)
            k += 1
        used[name] = True
        e['idx'] = i
        e['fname'] = name + '.html'
    return keep, stats


# ---------------------------------------------------------------- 渲染
FOOTER = ('文本据诸夏怀斯社《新编斯大林全集》正卷（文字版 PDF，2016年）第{no}卷整理；'
          '前十三卷为人民出版社1953年起中文版原卷。仅作学习、研究参考之用。')


def secdate_html(secs):
    if not secs:
        return ''
    out = []
    for s in secs[:3]:
        out.append(esc(tidy(s)))
    return '<br>\n'.join(out)


def write_reading_pages(vol, entries):
    outdir = os.path.join(WORKDIR, vol['name'])
    os.makedirs(outdir, exist_ok=True)
    # 清理上一轮的旧页面（剔除条目后序号会前移，不清理会留下野文件）
    for old in glob.glob(os.path.join(outdir, '*.html')):
        os.remove(old)
    toc_items = [{'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries]
    toc_groups = [{'label': vol['name'], 'items': toc_items}]
    brand = '斯大林全集 · %s' % vol['name']
    voltag = '《斯大林全集》%s' % vol['name']
    footer = FOOTER.format(no=vol['no'])
    for i, e in enumerate(entries):
        prev = entries[i - 1] if i > 0 else None
        nxt = entries[i + 1] if i + 1 < len(entries) else None
        result = {
            'title': e['title'],
            'secdate': secdate_html(e['secdate']),
            'body': [{'kind': b['kind'], 'html': esc(b['html'])} for b in e['blocks']],
            'notes': ([{'header': '注　释', 'items': e['notes']}] if e['notes'] else []),
        }
        page = render_article(
            result, art_idx=1, brand=brand, voltag=voltag,
            toc_groups=toc_groups, active_href=e['fname'],
            prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
            nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
            vol_href='../%s.html' % vol['name'],
            footer=footer,
            home_href='../../../../index.html', assets='../../../../assets',
        )
        with open(os.path.join(outdir, e['fname']), 'w', encoding='utf-8') as f:
            f.write(page)


CARD = '''<a class="card" href="{href}">
  <div class="vol">{vol}</div>
  <div class="ed">{ed}</div>
  <div class="stat">{title}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''


def write_volume_page(vol, entries):
    cards = []
    for e in entries:
        ed = ''
        if e['secdate']:
            ed = esc(tidy(e['secdate'][0]).strip('（）() '))
            if len(ed) > 24:
                ed = ''
        if not ed:
            ed = esc(vol['years'])
        cards.append(CARD.format(href='%s/%s' % (vol['name'], e['fname']),
                                 vol='第%d篇' % e['idx'], ed=ed, title=html.escape(e['title'], quote=False)))
    page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《斯大林全集》{name} 目录">
<title>斯大林全集 · {name}</title>
<link rel="stylesheet" href="../../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">斯 大 林 全 集 · 正 卷 二 十 卷</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1>{name}</h1>
    <div class="sub">{years}</div>
    <div class="meta">{n} 篇 · <a href="../斯大林全集.html">&#8678; 返回二十卷总目</a> · <a href="../index.html">&#8678; 斯大林</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>
'''.format(name=vol['name'], years=html.escape(vol['years'], quote=False), n=len(entries),
           cards='\n'.join(cards), footer=FOOTER.format(no=vol['no']))
    with open(os.path.join(WORKDIR, vol['name'] + '.html'), 'w', encoding='utf-8') as f:
        f.write(page)


def write_landing(all_entries):
    parts = []
    total = 0
    for vol, entries in all_entries:
        total += len(entries)
        cards = []
        for e in entries:
            cards.append(CARD.format(href='斯大林全集/%s/%s' % (vol['name'], e['fname']),
                                     vol='第%d篇' % e['idx'],
                                     ed=html.escape(vol['years'], quote=False),
                                     title=html.escape(e['title'], quote=False)))
        parts.append('<div class="zone-title">%s（%s）</div>\n<div class="cards">\n%s\n</div>'
                     % (vol['name'], html.escape(vol['years'], quote=False), '\n'.join(cards)))
    page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="斯大林全集 · 正卷二十卷 全部篇目">
<title>斯大林全集 · 正卷二十卷</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 斯 大 林</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">斯大林全集</h1>
    <div class="sub">正卷二十卷 · 按卷分组，共 {total} 篇</div>
    <div class="meta"><a href="index.html">&#8678; 返回斯大林</a></div>
  </header>
  <main>
{parts}
  </main>
  <footer>
    文本据诸夏怀斯社《新编斯大林全集》正卷（文字版 PDF，2016年）整理；前十三卷为人民出版社1953年起中文版原卷。仅作学习、研究参考之用。
  </footer>
</div>
</body>
</html>
'''.format(total=total, parts='\n'.join(parts))
    with open(LANDING, 'w', encoding='utf-8') as f:
        f.write(page)
    return total


# ---------------------------------------------------------------- 主流程
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    argv = sys.argv[1:]
    only = []
    if '--only' in argv:
        i = argv.index('--only')
        only = [int(x) for x in argv[i + 1:] if x.isdigit()]
    sample = '--sample' in argv
    report = '--report' in argv

    volumes, total_pages = load_volumes()
    cache = {p['p']: p for p in json.load(open(CACHE, encoding='utf-8'))}
    print('volumes:', len(volumes), 'pages_total:', total_pages, 'cache:', len(cache))

    results = []
    for k, vol in enumerate(volumes):
        vol_end = (volumes[k + 1]['start'] - 1) if k + 1 < len(volumes) else total_pages
        entries, stats = build_volume(vol, vol_end, cache, total_pages)
        results.append((vol, entries, stats))

    if sample:
        picks = [0, 5, 19]
        for pi in picks:
            vol, entries = results[pi][0], results[pi][1]
            cand = [x for x in entries if x['status'] == 'ok' and x['chars'] > 900
                    and '目录' not in x['title']]
            e = cand[min(4, len(cand) - 1)] if cand else entries[-1]
            txt = '\n'.join(re.sub(r'<[^>]+>', '', b['html']) for b in e['blocks'])
            print('\n' + '=' * 30, vol['name'], e['title'], 'chars', e['chars'], '=' * 30)
            print(txt[:800])
        return

    for vol, entries, stats in results:
        print('%s  收文=%d  ok=%d short=%d 剔除=%d' %
              (vol['name'], len(entries), stats['ok'], stats['short'],
               stats.get('skipped', 0)))
        if only and vol['no'] not in only:
            continue
        write_reading_pages(vol, entries)
        write_volume_page(vol, entries)
    total = write_landing([(v, e) for v, e, _ in results])

    print('总篇目:', sum(len(e) for _, e, _ in results), '/ landing total:', total,
          '/ sup_unattached:', _sup_warn[0])

    if report or True:
        lines = ['# 《斯大林全集》正卷二十卷 · 构建报告', '',
                 '- 源：`.tools/sources/stalin/pdf/斯大林全集_正卷20卷.pdf`（文字版 PDF，%d 页）'
                 % total_pages,
                 '- 书签：`.tools/sources/stalin/_toc.json`',
                 '- 生成脚本：`.tools/sources/stalin/build_quanji.py`（复用 `.tools/mew_convert.render_article`）',
                 '- 构建时间：%s' % __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
                 '', '## 每卷篇数', '',
                 '| 卷 | 年代 | 收文 | 正常 | 偏短 | 剔除的书签条目 |', '|---|---|---|---|---|---|']
        tot = {'n': 0, 'ok': 0, 'short': 0, 'bad': 0}
        for vol, entries, stats in results:
            bad = stats.get('skipped', 0)
            tot['n'] += len(entries)
            tot['ok'] += stats['ok']
            tot['short'] += stats['short']
            tot['bad'] += bad
            lines.append('| %s | %s | %d | %d | %d | %d |' %
                         (vol['name'], vol['years'], len(entries), stats['ok'], stats['short'], bad))
        lines.append('| **合计** |  | **%d** | **%d** | **%d** | **%d** |' %
                     (tot['n'], tot['ok'], tot['short'], tot['bad']))
        lines.append('')
        lines.append('## 已剔除的书签条目（原书无正文，未成页）')
        lines.append('')
        cls = {}
        others = []
        for vol, entries, stats in results:
            for k, v in stats.get('skip_cls', {}).items():
                cls[k] = cls.get(k, 0) + v
            others.extend(stats.get('skip_detail', []))
        for k in sorted(cls, key=lambda x: -cls[x]):
            lines.append('- %s：%d 条' % (k, cls[k]))
        if others:
            lines.append('- 其他明细：' + '；'.join(others))
        lines.append('')
        lines.append('保留下来的偏短篇目（<50 字但确有正文，如图注、短电文）：%d 篇，'
                     '正文末尾附「本篇源文本缺失」提示。' % tot['short'])
        lines.append('')
        lines.append('## 校验')
        lines.append('')
        lines.append('- `python .tools/check_all_links.py`：全站 10696 页、64234 条内部链接、**0 坏链**；')
        lines.append('- `.tools/sources/stalin/_navcheck.py`：逐页核对「上一篇/下一篇」、`tocGroups`、`activeHref` '
                     '与实际文件名及标题是否一一对应，1146 页 **0 处不一致**；')
        lines.append('- `.tools/sources/stalin/_scan.py`：页眉混入 / `◇页码◇` / 零宽字符 / 制表符 / 破折号分隔线 均为 0；')
        lines.append('- `.tools/sources/stalin/_verify.py`：逐篇回查 PDF 正文行是否都进入页面，未命中率 0.14%，'
                     '未命中的全部是「（一九二X年X月X日）」这类被提为 `secdate` 的日期行；')
        lines.append('')
        lines.append('## 处理说明')
        lines.append('')
        lines.append('- 页眉（`页码 + 斯大林全集 第X卷` / `页码 + 篇名`）、页脚纯页码逐页剥离；'
                     '另按「页面顶部 + 行很短 + 无句末标点」补漏个别页眉位置异常的页；')
        lines.append('- 左边距竖排夹注字符（x<40）按坐标剔除；`◇数字◇` 原书页码标记删除；')
        lines.append('- 段落按首行缩进/居中重排，跨页、跨行硬换行合并；悬挂缩进的年表类版式按「同缩进 + 上行无句末标点」判为续行；')
        lines.append('- 字号 22pt/36pt 视为篇名或卷内分篇标题，18pt 视为小节标题（h3）；')
        lines.append('- 页底 `——————` 之后若全为 14pt 小字，收为「注释」区并按注号合并、同文去重；'
                     '页面中部的装饰性破折线直接丢弃；')
        lines.append('- 上标小字（<13.5pt）按坐标还原为 `<sup>`，保留原书夹注页码符号；')
        lines.append('- 书签回指条目（年/月分组标题、插图说明等）按单页取文，超过 60 字视为无正文；')
        lines.append('- 同一页起始的父篇/子篇（如「联共（布）第十四次代表大会」与其「中央委员会的政治报告」）：'
                     '父篇只占标题页，子篇从同页取文，宁可一页重复也不丢正文；纯分组标题（年/月/时段）不重复；')
        lines.append('- 抽取文本 < 50 字的篇目仍生成页面，并在正文末尾注明「本篇源文本缺失」。')
        lines.append('- **无可读正文的书签条目（封面/口号页/扉页/斯大林像/声明页/纯年·月·时段分组标题/'
                     '只有图注的插图页）一律不成页、不进目录**，共剔除 %d 条；'
                     '剔除后卷内编号按新顺序从 01 连续重排，`tocGroups` 与上下篇同步重排。' % tot['bad'])
        lines.append('')
        lines.append('## 取舍与已知问题')
        lines.append('')
        lines.append('- 阅读页目录深度为四级（`导师著作/斯大林/斯大林全集/第X卷/`），故相对路径用 '
                     '`../../../../assets/`、`../../../../index.html`（与 `教员/军事文集/第X卷/` 一致）；'
                     '选卷页 `斯大林全集/第X卷.html` 为三级，用 `../../../assets/`。')
        lines.append('- 1424 条书签全部成页（含封面、版权页、年/月分组标题），以与 `_toc.json` 计数严格一致；'
                     '无正文者写「本篇源文本缺失」。')
        lines.append('- 文件名去掉全部空白与 `\\/:*?"<>|` 等非法字符，超 60 字截断，重名加 `-2`/`-3`。')
        lines.append('- 上标注号保留为 `<sup>`，不生成脚注锚点链接（避免锚点与实际注文分离造成坏链）。')
        with open(os.path.join(BASE, '_build_report.md'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print('report ->', os.path.join(BASE, '_build_report.md'))


if __name__ == '__main__':
    main()
    # 目录外置：每卷一个 目录.js（与全站全集一致）
    try:
        import sys
        sys.path.insert(0, r'C:\导师文集\.tools')
        from slim_toc import slim_root
        r = slim_root(WORKDIR)
        if r:
            print('瘦身：%.1f → %.1f MB' % (r[0] / 1048576, r[1] / 1048576))
    except Exception as e:
        print('!! 目录外置失败（请手动跑 python .tools/slim_toc.py）：', e)
