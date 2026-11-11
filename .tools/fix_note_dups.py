# -*- coding: utf-8 -*-
"""修复脚注 id 重复 / 上标 id 重复（只改 id 与断开的注释碎片，不改注释文字内容）。

处理的四类情况（判据都来自页面自身，不猜内容）：

① 续段碎片：相邻两条注释 id、编号相同，后一条其实是前一条被断开的后半截。
   - 后半截只有标点（源文本里的交叉引用被误当成新注，如「参看本卷第8页注[7]。」）
     → 把「[编号]标点」接回前一条，恢复原文；
   - 后半截是正文（如「页）。」）→ 直接接回，丢掉重复编号。
② 完全重复条目：同 id、同编号、文字一模一样（转换时复制了一次）→ 删后一条。
③ 分章重新编号（鲁迅常见：第一章 [1]-[10]，第二章又从 [1] 起）：
   按「上标编号 → 注释编号」把每个上标配到对应注释，再给重复 id 加 -2/-3 后缀。
④ 上标锚点 id 重复（同一条注被正文引用两次）：给重复的锚点 id 加 -2/-3，
   仅改 id 属性，href 与可见编号都不动。

页面若出现「某编号的上标数 > 注释数」（编号本身乱了，如 二心集/32-一电影与观众），
本脚本不动上标映射，只做 id 唯一化，并在报告中列为 needs-review。

用法：
    python .tools/fix_note_dups.py --check    # 只报告
    python .tools/fix_note_dups.py            # 写回（保留 CRLF）
"""
import os, re, sys, io, json, html, argparse
from collections import Counter, defaultdict, deque

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'.git', '.tools', 'node_modules', '批注', '.archive', '来源数据'}

RE_NOTE = re.compile(r'<p class="note"([^>]*)>(.*?)</p>', re.S)
RE_REF = re.compile(r'<sup class="fnref"><a ([^>]*)>(.*?)</a></sup>', re.S)
RE_HREF = re.compile(r'href="#([^"]+)"')
RE_ID = re.compile(r'\bid="([^"]+)"')
RE_TAG = re.compile(r'<[^>]+>')
RE_PUNCT = re.compile(r'^[\s。．.、，,；;：:！!？?—－\-…]*$')
RE_FRAG = re.compile(r'^[。．.、，,；;：:！!？?—－…]')
RE_SENT_END = '。！？；：”』）)」'

LABELS = [
    (re.compile(r'^\s*\[(\d{1,4})\]'), 'num'),
    (re.compile(r'^\s*[（(](\d{1,4})[）)]'), 'num'),
    (re.compile(r'^\s*(FN\d{1,3})'), 'fn'),
    (re.compile(r'^\s*(\d{1,4})(?![\d])'), 'num'),
]


def parse_label(text):
    for pat, kind in LABELS:
        m = pat.match(text)
        if m:
            v = m.group(1)
            return ('FN' + v[2:] if kind == 'fn' else str(int(v))), m.end()
    return None, 0


def collect(html_text):
    notes = []
    for m in RE_NOTE.finditer(html_text):
        attrs, body = m.group(1), m.group(2)
        mid = RE_ID.search(attrs)
        plain = RE_TAG.sub('', body)
        label, plen = parse_label(plain)
        notes.append({'m': m, 'full': m.group(0), 'id': mid.group(1) if mid else None,
                      'label': label, 'plain': plain, 'rest': plain[plen:]})
    refs = []
    for m in RE_REF.finditer(html_text):
        attrs, inner = m.group(1), m.group(2)
        hm = RE_HREF.search(attrs)
        idm = RE_ID.search(attrs)
        plain = RE_TAG.sub('', inner)
        label, _ = parse_label(plain)
        refs.append({'m': m, 'full': m.group(0), 'href': hm.group(1) if hm else None,
                     'anchor_id': idm.group(1) if idm else None,
                     'label': label, 'text': plain.strip()})
    return notes, refs


def unique_ids(notes):
    """按注释顺序给重复 id 加 -2/-3…；返回 {note_index: new_id}。"""
    used = set()
    out = {}
    seen = Counter()
    for i, n in enumerate(notes):
        if not n['id']:
            continue
        k = seen[n['id']]
        seen[n['id']] += 1
        cand = n['id'] if k == 0 else '%s-%d' % (n['id'], k + 1)
        while cand in used:
            cand += '-'
        used.add(cand)
        out[i] = cand
    return out


def plan_page(html_text, rel):
    notes, refs = collect(html_text)
    ids = [n['id'] for n in notes if n['id']]
    dup_note = [k for k, c in Counter(ids).items() if c > 1]
    anchor_ids = [r['anchor_id'] for r in refs if r['anchor_id']]
    dup_anchor = [k for k, c in Counter(anchor_ids).items() if c > 1]
    if not dup_note and not dup_anchor:
        return None

    notes_new = [dict(n) for n in notes]
    deleted = set()
    appends = defaultdict(str)
    merges = []
    dedup = []
    junk = []

    def prev_alive(i):
        j = i - 1
        while j >= 0 and j in deleted:
            j -= 1
        return j

    # ① 碎片：正文内交叉引用被误当成新注（如「参看本卷第92页注〔2〕。该报…」）。
#    特征：去掉行首空白/&ensp; 后直接以标点开头，**且该编号在页面上还另有注释条目**
#    （引用号必然与某条注释同号）；真正以破折号开头的注释，其编号是唯一的，不会误判。
    label_cnt = Counter(n['label'] for n in notes_new if n['label'])
    for i in range(1, len(notes_new)):
        if i in deleted or not notes_new[i]['label']:
            continue
        if label_cnt[notes_new[i]['label']] < 2:
            continue
        lead = notes_new[i]['rest'].lstrip(' \t\r\n\u3000')
        if lead.startswith('&ensp;'):
            lead = lead[len('&ensp;'):]
        if not lead or not RE_FRAG.match(lead):
            continue
        p = prev_alive(i)
        if p < 0:
            continue
        appends[p] += '[%s]%s' % (notes_new[i]['label'], lead)
        deleted.add(i)
        junk.append((p, i, '[%s]%s' % (notes_new[i]['label'], lead[:20])))

    # ② 续段：紧跟其后、id 与编号都与上一条相同，且上一条没有句末标点、残片不以标点开头
    #    （如「…第４８９」+「页）。」）→ 直接接回，丢掉重复编号
    for i in range(1, len(notes_new)):
        if i in deleted or not notes_new[i]['id']:
            continue
        p = prev_alive(i)
        if p < 0:
            continue
        cur, prev = notes_new[i], notes_new[p]
        if cur['id'] != prev['id'] or cur['label'] != prev['label']:
            continue
        rest = cur['rest']
        if not rest.strip():
            deleted.add(i)
            dedup.append((p, i, '(空)'))
            continue
        lead = rest.lstrip(' \t\r\n\u3000')
        if lead.startswith('&ensp;'):
            lead = lead[len('&ensp;'):]
        if RE_FRAG.match(lead):
            continue
        if prev['plain'].rstrip()[-1:] in RE_SENT_END:
            continue
        appends[p] += lead
        deleted.add(i)
        merges.append((p, i, lead[:40]))

    # ③ 完全重复条目（同 id、同编号、文字一致）
    first_seen = {}
    for i, n in enumerate(notes_new):
        if i in deleted or not n['id'] or not n['label']:
            continue
        key = (n['id'], n['label'], n['plain'].strip())
        if key in first_seen:
            deleted.add(i)
            dedup.append((first_seen[key], i, n['plain'][:40]))
        else:
            first_seen[key] = i

    kept = [n for i, n in enumerate(notes_new) if i not in deleted]
    # ③ 分章重编号：判断编号是否可安全配对
    #    - 同一编号有多个注释（分章重编号）→ 按上标出现顺序排队配对；
    #    - 某编号上标数 > 注释数且注释数 > 1 → 编号本身乱了（无法判断属于哪一条），
    #      只做 id 唯一化、不动上标，列为 needs-review；
    #    - 注释数 == 1 时，多个上标重复引用同一条注是正常的（马恩全集常见），直接复用。
    rc = Counter(r['label'] for r in refs if r['label'])
    nc = Counter(n['label'] for n in kept if n['label'])
    overflow = {k: (rc[k], nc.get(k, 0)) for k in rc if rc[k] > nc.get(k, 0) and nc.get(k, 0) > 1}
    review = bool(overflow)

    new_id_by_index = {}
    for i, n in enumerate(notes_new):
        if i in deleted:
            continue
        new_id_by_index[i] = n['id']
    # 唯一化（对 kept 里重复的 id 加后缀）
    used = Counter()
    for i, n in enumerate(notes_new):
        if i in deleted or not n['id']:
            continue
        k = used[n['id']]
        used[n['id']] += 1
        if k > 0:
            cand = '%s-%d' % (n['id'], k + 1)
            while cand in set(v for v in new_id_by_index.values() if v):
                cand += '-'
            new_id_by_index[i] = cand

    # 上标配对（review 页面不动 href）
    ref_new_href = {}
    unmatched = 0
    if not review:
        queues = defaultdict(deque)
        for i, n in enumerate(notes_new):
            if i in deleted or not n['label']:
                continue
            queues[n['label']].append(i)
        last_used = {}
        for ri, r in enumerate(refs):
            if not r['label']:
                unmatched += 1
                continue
            q = queues.get(r['label'])
            if q:
                idx = q.popleft()
                last_used[r['label']] = idx
                ref_new_href[ri] = new_id_by_index[idx]
            elif r['label'] in last_used:
                # 同一条注被正文多次引用（注释只有一条）→ 复用
                ref_new_href[ri] = new_id_by_index[last_used[r['label']]]
            else:
                unmatched += 1

    # 上标锚点 id 唯一化
    anchor_new = {}
    used_a = Counter()
    for ri, r in enumerate(refs):
        if not r['anchor_id']:
            continue
        k = used_a[r['anchor_id']]
        used_a[r['anchor_id']] += 1
        if k > 0:
            cand = '%s-%d' % (r['anchor_id'], k + 1)
            existing = set(x for x in used_a if x)
            while cand in existing:
                cand += '-'
            anchor_new[ri] = cand

    edits = []
    for i, n in enumerate(notes_new):
        if i in deleted:
            edits.append((n['m'].start(), n['m'].end(), ''))
            continue
        full = n['full']
        if i in appends:
            assert full.endswith('</p>')
            # appends 里是页面原有文本（可能含 &ensp; 等实体），原样接回，不再二次转义
            full = full[:-4] + appends[i] + '</p>'
        new_id = new_id_by_index.get(i)
        if new_id and n['id'] and new_id != n['id']:
            full = full.replace('id="%s"' % n['id'], 'id="%s"' % new_id, 1)
        if full != n['full']:
            edits.append((n['m'].start(), n['m'].end(), full))
    for ri, r in enumerate(refs):
        full = r['full']
        if ri in ref_new_href and r['href'] and ref_new_href[ri] != r['href']:
            full = full.replace('href="#%s"' % r['href'], 'href="#%s"' % ref_new_href[ri], 1)
        if ri in anchor_new and r['anchor_id']:
            full = full.replace('id="%s"' % r['anchor_id'], 'id="%s"' % anchor_new[ri], 1)
        if full != r['full']:
            edits.append((r['m'].start(), r['m'].end(), full))

    if not edits:
        return None
    edits.sort(key=lambda e: e[0], reverse=True)
    out = html_text
    for s, e, rep in edits:
        out = out[:s] + rep + out[e:]

    return {
        'rel': rel, 'html': out,
        'notes': len(notes), 'deleted': len(deleted), 'merged': len(merges),
        'junk': len(junk), 'dedup': len(dedup), 'unmatched_refs': unmatched,
        'review': review, 'overflow': overflow,
        'dup_note_ids': dup_note, 'dup_anchor_ids': dup_anchor,
        'merges': merges[:5], 'junks': junk[:5], 'dedups': dedup[:5],
    }


def validate(new_html):
    notes, refs = collect(new_html)
    ids = [n['id'] for n in notes if n['id']]
    dup = [k for k, c in Counter(ids).items() if c > 1]
    idset = set(ids)
    dangling = [r['href'] for r in refs if r['href'] and r['href'] not in idset]
    by_id = {n['id']: n for n in notes if n['id']}
    label_bad = []
    for r in refs:
        n = by_id.get(r['href'])
        if n and r['label'] and n['label'] and r['label'] != n['label']:
            label_bad.append((r['text'], r['label'], n['label']))
    return set(dup), set(dangling), set(label_bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    stats = Counter()
    review_pages, problems = [], []
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP]
        for fn in fns:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, ROOT)
            try:
                raw = open(p, encoding='utf-8', newline='').read()
            except (OSError, UnicodeDecodeError):
                continue
            if 'class="fnref"' not in raw:
                continue
            plan = plan_page(raw, rel)
            if not plan:
                continue
            dup0, dangling0, bad0 = validate(raw)
            dup, dangling, label_bad = validate(plan['html'])
            if dup or (dangling - dangling0) or (label_bad - bad0):
                problems.append((rel, sorted(dup)[:3], sorted(dangling - dangling0)[:3],
                                 sorted(label_bad - bad0)[:3]))
                continue
            stats['pages'] += 1
            stats['deleted'] += plan['deleted']
            stats['merged'] += plan['merged']
            stats['junk'] += plan['junk']
            stats['dedup'] += plan['dedup']
            stats['unmatched'] += plan['unmatched_refs']
            if plan['review']:
                review_pages.append((rel, plan['overflow']))
            print('%-64s 注释%3d 删%2d 接回%2d 合并%2d 去重%2d 未配上标%2d%s'
                  % (rel, plan['notes'], plan['deleted'], plan['junk'], plan['merged'],
                     plan['dedup'], plan['unmatched_refs'],
                     '  [needs-review]' if plan['review'] else ''))
            if not args.check:
                with open(p, 'w', encoding='utf-8', newline='') as f:
                    f.write(plan['html'])
    print('\n合计：%d 页；删碎条 %d、合并续段 %d、去重 %d、未配对上的上标 %d'
          % (stats['pages'], stats['deleted'], stats['merged'],
             stats['dedup'], stats['unmatched']))
    if review_pages:
        print('\n需人工复核（编号本身乱了，只做了 id 唯一化）：%d 页' % len(review_pages))
        for rel, ov in review_pages:
            print('  %-64s %s' % (rel, ov))
    if problems:
        print('\n校验失败（已跳过，未写回）：%d 页' % len(problems))
        for row in problems:
            print('  ', row)
    print('\n%s' % ('（--check 模式，未写回）' if args.check else '已写回'))


if __name__ == '__main__':
    main()