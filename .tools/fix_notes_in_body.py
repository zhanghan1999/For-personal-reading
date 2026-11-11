# -*- coding: utf-8 -*-
"""把「被排成正文段落的注释」收回注释区（幂等）。

背景：军事文集个别篇的源文本没有「注　释」小标题，build_junshi.py 因此没进入注释解析，
注释正文被当成普通段落排进正文，段首还带着自己的上标（`<p class="para"><sup ...>[n]</sup>　…`），
结果页面上没有注释区，正文里的上标全指不到目标（如《论持久战》53 条）。

判据（只动确凿的页面）：
- 页面没有 <div class="notes">；
- 以「<p class="para"><sup class="fnref">…[n]…</sup>　正文</p>」开头的段落，编号正好是 1..N 连续；
- 这些段落彼此相邻、位于 <div class="chapnav"> 之前（文章末尾）。
满足则把它们移入注释区，正文不再显示注释。

用法：python .tools/fix_notes_in_body.py [--check]
"""
import os, re, sys, io, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'.git', '.tools', 'node_modules', '批注', '.archive', '来源数据'}

RE_LEAD = re.compile(
    r'<p class="para"><sup class="fnref"><a href="#([^"]+)"[^>]*>\[(\d+)\]</a></sup>[\u3000\s]*(.*?)</p>',
    re.S)


def process(path, check):
    raw = open(path, encoding='utf-8', newline='').read()
    if '<div class="notes">' in raw:
        return None
    ms = list(RE_LEAD.finditer(raw))
    if not ms:
        return None
    nums = [int(m.group(2)) for m in ms]
    if nums != list(range(1, len(ms) + 1)):
        return ('编号不是 1..N 连续，跳过', 0)
    chap = raw.find('<div class="chapnav"')
    if chap == -1:
        return ('找不到 chapnav，跳过', 0)
    if ms[-1].end() > chap:
        return ('注释段落在 chapnav 之后，跳过', 0)
    # 段落之间只允许空白
    for a, b in zip(ms, ms[1:]):
        if raw[a.end():b.start()].strip():
            return ('注释段落不相邻，跳过', 0)

    notes = []
    for m in ms:
        nid, num, body = m.group(1), m.group(2), m.group(3)
        notes.append('<p class="note" id="%s">[%s]&ensp;%s</p>' % (nid, num, body.strip()))
    block = '<div class="notes"><h4>注　释</h4>' + '\n'.join(notes) + '</div>\n'

    # 删除段落后，把注释区插到 chapnav 前
    out = raw[:ms[0].start()] + raw[ms[-1].end():]
    chap2 = out.find('<div class="chapnav"')
    out = out[:chap2] + block + out[chap2:]
    # 清理多余空行
    out = re.sub(r'\n{3,}', '\n\n', out)
    if not check:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(out)
    return ('收回注释 %d 条' % len(notes), len(notes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    total = 0
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP]
        for fn in fns:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dp, fn)
            try:
                res = process(p, args.check)
            except (OSError, UnicodeDecodeError):
                continue
            if not res:
                continue
            info, n = res
            total += n
            print('%-74s %s' % (os.path.relpath(p, ROOT), info))
    print('\n%s：收回注释 %d 条' % ('待处理' if args.check else '已处理', total))


if __name__ == '__main__':
    main()