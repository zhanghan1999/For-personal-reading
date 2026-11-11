# -*- coding: utf-8 -*-
"""fix_page_scripts.py — 修复 slim_toc 首次改写时吞掉 </script> 的问题，并把
目录-<hash>.js 规范成 目录.js（同目录只有一份时）。"""
import os, re, sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'
ROOTS = [r'导师著作\马克思\马克思恩格斯全集', r'导师著作\斯大林\斯大林全集',
         r'其他著作\鲁迅\鲁迅全集']
DEC = json.JSONDecoder()


def rename_js(root):
    """同目录只有一个 目录-<hash>.js 时改名为 目录.js，返回 {旧名: 新名}"""
    ren = {}
    for r, _, fs in os.walk(root):
        cand = [f for f in fs if re.fullmatch(r'目录-[0-9a-f]{10}\.js', f)]
        if len(cand) == 1 and '目录.js' not in fs:
            os.replace(os.path.join(r, cand[0]), os.path.join(r, '目录.js'))
            ren[cand[0]] = '目录.js'
    return ren


def fix(root, ren):
    n_fixed = n_ok = n_skip = 0
    for r, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.html'):
                continue
            p = os.path.join(r, f)
            s = open(p, encoding='utf-8').read()
            i = s.find('window.PAGE = ')
            if i < 0:
                continue
            try:
                _, end = DEC.raw_decode(s[i + len('window.PAGE = '):])
            except Exception:
                n_skip += 1
                continue
            abs_end = i + len('window.PAGE = ') + end
            changed = False
            if s[abs_end] == ';' and not s[abs_end + 1:].lstrip().startswith('</script>'):
                s = s[:abs_end + 1] + '</script>' + s[abs_end + 1:]
                changed = True
                n_fixed += 1
            else:
                n_ok += 1
            if ren:
                for old, new in ren.items():
                    if old in s:
                        s = s.replace(old, new)
                        changed = True
            if changed:
                with open(p, 'w', encoding='utf-8') as fh:
                    fh.write(s)
    print('%s: 修复 %d 页，正常 %d 页，跳过 %d' % (
        os.path.relpath(root, ROOT), n_fixed, n_ok, n_skip))


def main():
    for rel in ROOTS:
        root = os.path.join(ROOT, rel)
        if not os.path.isdir(root):
            continue
        ren = rename_js(root)
        if ren:
            print('%s: 目录 js 规范化 %d 个' % (os.path.relpath(root, ROOT), len(ren)))
        fix(root, ren)


if __name__ == '__main__':
    main()
