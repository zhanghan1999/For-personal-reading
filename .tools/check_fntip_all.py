# -*- coding: utf-8 -*-
"""全站脚注一致性扫描（只读）。

背景：阅读页正文的脚注上标是
    <sup class="fnref"><a href="#ID">[n]</a></sup>
文末注释条目必须带同名 id，点开才有内容：
    <p class="note" id="ID">[n]&ensp;…</p>
本脚本逐页比对，输出四类问题：

① 坏锚点：上标指向的 id 在本页根本不存在 —— 点击无反应（多为源文本里注释条目丢失）。
② 注释缺 id 但带编号 —— 条目在、只是缺 id，跑 fix_note_ids.py 可自动补。
③ 注释 id 重复 —— 两条注释共用一个 id，点开可能拿到错误的那条。
④ 正文上标 id 重复 —— 同一条注被正文引用两次（html 不合规但不影响点开，仅提示）。

用法：
    python .tools/check_fntip_all.py             # 摘要 + 按页面聚合
    python .tools/check_fntip_all.py --verbose   # 逐条列明细
"""
import os, re, sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', '.tools', 'node_modules', '批注', '.archive', '来源数据'}

RE_FNREF_HREF = re.compile(r'<sup class="fnref"><a href="#([^"]+)"')
RE_FNREF_ID = re.compile(r'<sup class="fnref"><a href="#[^"]+" id="([^"]+)"')
RE_NOTE = re.compile(r'<p class="note"([^>]*)>(.*?)</p>', re.S)
RE_ID_ATTR = re.compile(r'\bid="([^"]+)"')
# 注释编号：只认带闭合括号的写法，避免把以数字开头的正文当编号
RE_LABEL = re.compile(r'^\s*(?:注释)?\s*[\[［【(（〔]\s*(\d{1,3})\s*[\]］】)）〕]')


def _natural(s):
    """n2 < n10 的自然排序 key。"""
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]


def scan_file(html):
    """返回 (坏锚点列表, 带编号缺 id 数, 无编号缺 id 数, 重复注释 id 列表, 重复上标 id 列表)。"""
    refs = RE_FNREF_HREF.findall(html)
    all_ids = RE_ID_ATTR.findall(html)
    idset = set(all_ids)
    missing = [h for h in refs if h not in idset]

    numbered_no_id = 0
    plain_no_id = 0
    note_ids = []
    for m in RE_NOTE.finditer(html):
        attrs, body = m.group(1), m.group(2)
        mid = RE_ID_ATTR.search(attrs)
        if mid:
            note_ids.append(mid.group(1))
        elif RE_LABEL.match(body):
            numbered_no_id += 1
        else:
            plain_no_id += 1

    def dups(seq):
        seen, out = {}, []
        for x in seq:
            seen[x] = seen.get(x, 0) + 1
            if seen[x] == 2:
                out.append(x)
        return out

    return missing, numbered_no_id, plain_no_id, dups(note_ids), dups(RE_FNREF_ID.findall(html))


def main():
    verbose = '--verbose' in sys.argv
    files = pages = 0
    missing_all, noid_numbered, noid_plain, note_dups, ref_dups = [], [], [], [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            path = os.path.join(dirpath, fn)
            try:
                html = open(path, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            files += 1
            if 'class="fnref"' not in html:
                continue
            pages += 1
            rel = os.path.relpath(path, ROOT)
            missing, num_noid, plain_noid, ndup, rdup = scan_file(html)
            for h in missing:
                missing_all.append((rel, h))
            if num_noid:
                noid_numbered.append((rel, num_noid))
            if plain_noid:
                noid_plain.append((rel, plain_noid))
            for i in ndup:
                note_dups.append((rel, i))
            for i in rdup:
                ref_dups.append((rel, i))

    print('扫描 HTML 文件：%d 个；含脚注的页面：%d 个' % (files, pages))
    print('① 坏锚点（上标找不到注释，点了没反应）：%d 处（%d 个页面）'
          % (len(missing_all), len({f for f, _ in missing_all})))
    print('② 注释缺 id 但带编号（可自动补）：%d 条（%d 个页面）'
          % (sum(n for _, n in noid_numbered), len(noid_numbered)))
    print('③ 注释 id 重复：%d 个（%d 个页面）' % (len(note_dups), len({f for f, _ in note_dups})))
    print('④ 上标 id 重复（同注被引两次，仅提示）：%d 个（%d 个页面）'
          % (len(ref_dups), len({f for f, _ in ref_dups})))

    by_file = {}
    for rel, href in missing_all:
        by_file.setdefault(rel, set()).add(href)
    if by_file:
        print('\n== ① 坏锚点按页面聚合 ==')
        for rel, hrefs in sorted(by_file.items(), key=lambda kv: -len(kv[1])):
            print('  %-68s %3d  %s' % (rel, len(hrefs),
                                       ','.join(sorted(hrefs, key=_natural)[:8])))
    for rel, n in sorted(noid_numbered):
        print('  [② 缺 id 且带编号] %-56s %d 条' % (rel, n))
    for rel, i in sorted(note_dups):
        print('  [③ 注释 id 重复] %-56s %s' % (rel, i))
    if noid_plain:
        print('\n  （另有 %d 条无编号的注释条目没有 id：多为一条注释的续段，不算问题）'
              % sum(n for _, n in noid_plain))
    if verbose:
        print('\n== ① 明细 ==')
        for item in missing_all:
            print('  ', item)

    print('\nJSON:', json.dumps({
        'files': files,
        'pages_with_notes': pages,
        'missing_anchor': len(missing_all),
        'note_without_id_numbered': sum(n for _, n in noid_numbered),
        'note_id_duplicates': len(note_dups),
        'ref_id_duplicates': len(ref_dups),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()