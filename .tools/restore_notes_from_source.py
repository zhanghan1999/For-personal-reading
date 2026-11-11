# -*- coding: utf-8 -*-
"""从 .tools/sources/mew 原文补齐马恩全集阅读页缺失的注释条目（幂等）。

定位源文件的两条路子：
1) 正文段落命中：页面里较长的段落（去空白后前 40 字）在哪个源文件里出现得最多；
2) 标题命中：页面标题与源文件 <title> 完全一致（用于极短/拆分页）。

只在「源文件里确实定义了该注释 id」时补条目，找不到就如实报告，不猜内容。

用法：
    python .tools/restore_notes_from_source.py --check
    python .tools/restore_notes_from_source.py
"""
import os, re, sys, io, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '.tools', 'sources', 'mew')
MEGA = os.path.join(ROOT, '导师著作', '马克思', '马克思恩格斯全集')

RE_FNREF = re.compile(r'<sup class="fnref"><a href="#([^"]+)"')
RE_NOTE = re.compile(r'<p class="note"([^>]*)>(.*?)</p>', re.S)
RE_ID = re.compile(r'\bid="([^"]+)"')
RE_TAG = re.compile(r'<[^>]+>')
RE_ASIDE = re.compile(r'<aside[^>]*>(.*?)</aside>', re.S)
RE_SRC_NOTE = re.compile(
    r'<div><a href="#(?:z|bz|az)ref\d+" id="([^"]+)">(.*?)</a>(.*?)</div>', re.S)
RE_PAGE_TITLE = re.compile(r'<title>(.*?)</title>', re.S)
RE_SRC_TITLE = re.compile(r'<title>(.*?)</title>', re.S)
RE_LABEL_NUM = re.compile(r'^\s*(\d{1,4})')
RE_LABEL_FN = re.compile(r'^\s*(FN\d{1,3})')
RE_LABEL_PAREN = re.compile(r'^\s*\((\d+)\)')


def strip_tags(s):
    return RE_TAG.sub('', s)


def page_title(h):
    m = RE_PAGE_TITLE.search(h)
    if not m:
        return ''
    t = m.group(1).strip()
    return t.split('·')[0].strip()


def src_title(h):
    m = RE_SRC_TITLE.search(h)
    return m.group(1).strip() if m else ''


def parse_src_notes(src_html):
    out = {}
    for aside in RE_ASIDE.findall(src_html):
        for m in RE_SRC_NOTE.finditer(aside):
            nid, label_html, body_html = m.group(1), m.group(2), m.group(3)
            if nid in out:
                continue
            plain = strip_tags(label_html + body_html).strip()
            num = None
            kind = 'z'
            if nid.startswith('bz'):
                mm = RE_LABEL_FN.match(plain)
                kind = 'bz'
                if mm:
                    num = int(mm.group(1)[2:])
            elif nid.startswith('az'):
                mm = RE_LABEL_PAREN.match(plain)
                kind = 'az'
                if mm:
                    num = int(mm.group(1))
            else:
                mm = RE_LABEL_NUM.match(plain)
                if mm:
                    num = int(mm.group(1))
            if num is None:
                continue
            out[nid] = {'num': num, 'kind': kind, 'body': body_html.strip()}
    return out


def long_paras(page_html):
    paras = [re.sub(r'\s+', '', strip_tags(x))
             for x in re.findall(r'<p class="para">(.*?)</p>', page_html, re.S)]
    return [x for x in paras if len(x) > 60]


def find_candidates(vol, page_html):
    d = os.path.join(SRC, str(vol))
    if not os.path.isdir(d):
        return []
    paras = long_paras(page_html)
    title = page_title(page_html)
    out = []
    for fn in os.listdir(d):
        if not fn.endswith('.html'):
            continue
        s = open(os.path.join(d, fn), encoding='utf-8', errors='ignore').read()
        hits = 0
        if paras:
            flat = re.sub(r'\s+', '', s)
            hits = sum(1 for x in paras if x[:40] in flat)
        ratio = hits / len(paras) if paras else 0
        same_title = bool(title) and src_title(s) == title
        if ratio >= 0.5 or same_title:
            src_notes = parse_src_notes(s)
            out.append({'fn': fn, 'ratio': ratio, 'same_title': same_title,
                        'notes': src_notes, 'html': s})
    return out


def insert_notes(page_html, new_notes):
    m = re.search(r'<div class="notes">(.*?)</div>', page_html, re.S)
    if not m:
        # 没有注释块：新建一个，放在 chapnav 前
        block = '<div class="notes"><h4>注　释</h4>' + '\n'.join(new_notes) + '</div>\n'
        i = page_html.find('<div class="chapnav"')
        if i == -1:
            return page_html, 0
        return page_html[:i] + block + page_html[i:], len(new_notes)
    block = m.group(1)
    items = list(RE_NOTE.finditer(block))
    # 按 kind 找到插入锚点：numeric 注释按编号排序
    inserts = []
    for note_html in new_notes:
        nid = RE_ID.search(note_html).group(1)
        num_m = re.match(r'<p class="note" id="[^"]+">(?:FN|\(|)(\d+)', note_html)
        num = int(num_m.group(1)) if num_m else None
        kind = 'bz' if nid.startswith('bz') else ('az' if nid.startswith('az') else 'z')
        pos = None
        if num is not None:
            for it in items:
                mid = RE_ID.search(it.group(1))
                iid = mid.group(1) if mid else ''
                ikind = 'bz' if iid.startswith('bz') else ('az' if iid.startswith('az') else 'z')
                if ikind != kind:
                    continue
                plain = strip_tags(it.group(2)).strip()
                mm = RE_LABEL_NUM.match(plain)
                if mm and int(mm.group(1)) > num:
                    pos = it.start()
                    break
        if pos is None:
            same = [it for it in items
                    if (RE_ID.search(it.group(1)).group(1) if RE_ID.search(it.group(1)) else '').startswith(
                        'bz' if kind == 'bz' else 'z')]
            pos = same[-1].end() if same else len(block)
        inserts.append((pos, note_html))
    for pos, note_html in sorted(inserts, key=lambda x: x[0], reverse=True):
        block = block[:pos] + note_html + block[pos:]
    return page_html[:m.start(1)] + block + page_html[m.end(1):], len(new_notes)


def process_page(path, vol, check):
    raw = open(path, encoding='utf-8', newline='').read()
    refs = list(dict.fromkeys(RE_FNREF.findall(raw)))
    ids = set(RE_ID.findall(raw))
    missing = [r for r in refs if r not in ids]
    if not missing:
        return None
    cands = find_candidates(vol, raw)
    if not cands:
        return ('未找到源文件', 0, missing)
    best = None
    for c in cands:
        got = [x for x in missing if x in c['notes']]
        key = (len(got), c['ratio'], c['same_title'])
        if best is None or key > best[0]:
            best = (key, c, got)
    _, src, got = best
    if not got:
        return ('源文件里没有这些编号', 0, missing)
    notes = []
    for nid in got:
        n = src['notes'][nid]
        label = ('FN%d' % n['num']) if n['kind'] == 'bz' else (
            '(%d)' % n['num'] if n['kind'] == 'az' else str(n['num']))
        notes.append('<p class="note" id="%s">%s&ensp;%s</p>' % (nid, label, n['body']))
    out, added = insert_notes(raw, notes)
    if not check:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(out)
    return ('源 %s（段落命中 %.0f%%）' % (src['fn'], src['ratio'] * 100),
            added, [x for x in missing if x not in got])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    pages = added = 0
    still = []
    for vol in range(1, 51):
        vdir = os.path.join(MEGA, '第%d卷' % vol)
        if not os.path.isdir(vdir):
            continue
        for fn in sorted(os.listdir(vdir)):
            if not fn.endswith('.html'):
                continue
            p = os.path.join(vdir, fn)
            res = process_page(p, vol, args.check)
            if not res:
                continue
            info, n, rest = res
            pages += 1
            added += n
            still.extend((os.path.relpath(p, ROOT), x) for x in rest)
            print('%-72s %s 补 %d 条%s' % (os.path.relpath(p, ROOT), info, n,
                                          ('  仍缺：' + ','.join(rest[:8])) if rest else ''))
    print('\n%s：%d 页，补 %d 条；仍缺 %d 处' % ('待补' if args.check else '已补', pages, added, len(still)))
    for rel, x in still[:12]:
        print('   仍缺 %-10s %s' % (x, rel))


if __name__ == '__main__':
    main()