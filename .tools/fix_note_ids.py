# -*- coding: utf-8 -*-
"""补齐脚注目标 id（幂等，可反复运行）。

背景
----
阅读页正文里的脚注上标是
    <sup class="fnref"><a href="#v5a29-n1">[1]</a></sup>
文末注释条目必须带同名 id 才能被 app.js 的悬浮脚注找到：
    <p class="note" id="v5a29-n1">[1]&ensp;…</p>
若注释条目漏了 id（毛选第五卷有 7 篇属于这种情况），点击上标就没有任何反应。

本脚本做的事
------------
1. 只处理同时满足以下条件的页面：页面里有 fnref 锚点；注释块里有 <p class="note"> 缺 id；
   这些缺 id 的条目前面带有编号（（1） / 〔1） / [1] / ［1］ 等 OCR 变体）。
2. 从该页 fnref 锚点反推 id 前缀（如 v5a29-n / jxz / zz），**不猜前缀**：
   只有当页面上所有锚点共用同一前缀时才动手，否则整页跳过并报告。
3. 按条目自带的编号补 id，并把编号统一成「[N]&ensp;正文」。
4. 已有 id 的条目一律不动；目标 id 若已存在（会撞车）则跳过并报告。

用法
----
    python .tools/fix_note_ids.py --check     # 只报告，不改文件
    python .tools/fix_note_ids.py             # 实际写入
    python .tools/fix_note_ids.py --path 导师著作\\教员\\毛选\\5   # 限定子树
"""
import os, re, sys, io, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', '.tools', 'node_modules', '批注', '.archive', '来源数据'}

RE_FNREF = re.compile(r'<sup class="fnref"><a href="#([^"]+)"')
RE_NOTE = re.compile(r'<p class="note"([^>]*)>(.*?)</p>', re.S)
# 编号变体：（1） 〔1） [1] ［1］ 【1】 (1) 1）
RE_LABEL = re.compile(r'^\s*[（(〔\[［【]?\s*(\d{1,3})\s*[）)〕\]］】]?\s*'
                      r'(?=[^\s\d）)〕\]］】])')
RE_TAIL_NUM = re.compile(r'^(.*?)(\d+)$')


def infer_prefix(refs):
    """从锚点反推 id 前缀；所有锚点必须共用一个前缀，否则返回 None。"""
    prefixes = set()
    for r in refs:
        m = RE_TAIL_NUM.match(r)
        if not m:
            return None
        prefixes.add(m.group(1))
    if len(prefixes) == 1:
        return prefixes.pop()
    return None


def has_id(attrs):
    return re.search(r'\bid\s*=', attrs) is not None


def fix_html(html, rel):
    refs = RE_FNREF.findall(html)
    if not refs:
        return None, '没有脚注上标'
    existing = set(re.findall(r'<p class="note"[^>]*\bid="([^"]+)"', html))
    # 找出缺 id 且带编号的条目
    targets = []
    for m in RE_NOTE.finditer(html):
        attrs, body = m.group(1), m.group(2)
        if has_id(attrs):
            continue
        lm = RE_LABEL.match(body)
        if not lm:
            continue
        targets.append((m, lm.group(1), body[lm.end():]))
    if not targets:
        return None, '没有「缺 id 但带编号」的注释条目'

    prefix = infer_prefix(refs)
    if prefix is None:
        return None, '锚点前缀不唯一（%s），跳过' % ','.join(sorted(set(refs))[:5])

    notes = []
    for m, num, rest in targets:
        nid = '%s%s' % (prefix, num)
        if nid in existing:
            notes.append('跳过（id 已存在：%s）' % nid)
            continue
        notes.append('补 id=%s' % nid)
    if not notes:
        return None, '无实际改动'

    def repl(m):
        attrs, body = m.group(1), m.group(2)
        if has_id(attrs):
            return m.group(0)
        lm = RE_LABEL.match(body)
        if not lm:
            return m.group(0)
        num = lm.group(1)
        rest = body[lm.end():].lstrip()
        nid = '%s%s' % (prefix, num)
        return '<p class="note" id="%s">[%s]&ensp;%s</p>' % (nid, num, rest)

    return RE_NOTE.sub(repl, html), '；'.join(notes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='只报告，不写文件')
    ap.add_argument('--path', default='', help='只处理该子目录')
    args = ap.parse_args()

    base = os.path.join(ROOT, args.path) if args.path else ROOT
    changed = skipped = 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            try:
                html = open(path, encoding='utf-8', newline='').read()   # newline='' 保留原 CRLF
            except (OSError, UnicodeDecodeError):
                skipped += 1
                continue
            new, info = fix_html(html, rel)
            if new is None:
                continue
            print('%-72s %s' % (rel, info))
            if args.check:
                changed += 1
                continue
            with open(path, 'w', encoding='utf-8', newline='') as f:   # 同样不做换行翻译
                f.write(new)
            changed += 1
    print('\n%s：%d 个页面（跳过 %d 个无法解码）'
          % ('待修复' if args.check else '已修复', changed, skipped))


if __name__ == '__main__':
    main()