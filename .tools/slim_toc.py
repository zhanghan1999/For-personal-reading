# -*- coding: utf-8 -*-
"""
slim_toc.py — 全集目录外置（瘦身）。

背景：全集每个阅读页都把「整卷/整部目录」内嵌在 window.PAGE.tocGroups 里，
同一卷 100 多页各存一份，马恩全集因此多出 164 MB。

做法：把目录抽成 <目录.js>（window.VOL_TOC = [...]），页面改为在其 app.js 之前
引一行 <script src="目录.js">；assets/app.js 在 tocGroups 为空时回退读 VOL_TOC。
普通 <script src> 在 file:// 下不受跨域限制，所以双击打开照旧有目录。

只处理「全集」目录（默认马恩全集 / 斯大林全集 / 鲁迅全集）：
  python .tools/slim_toc.py            # 瘦身
  python .tools/slim_toc.py --check    # 只统计，不写文件
  python .tools/slim_toc.py --root 导师著作/斯大林/斯大林全集
"""
import os, re, sys, io, json, hashlib, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r'C:\导师文集'

DEFAULT_ROOTS = [
    r'导师著作\马克思\马克思恩格斯全集',
    r'导师著作\斯大林\斯大林全集',
    r'其他著作\鲁迅\鲁迅全集',
]

PAGE_RE = re.compile(r'window\.PAGE = (\{.*?\});\s*</script>', re.S)
APP_RE = re.compile(r'<script src="([^"]*assets/app\.js)"></script>')
JS_NAME = '目录.js'


def toc_key(groups):
    return hashlib.md5(json.dumps(groups, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:10]


def scan(root):
    """返回 {toc_key: {'json': str, 'pages': [abspath, ...]}}"""
    found = {}
    for r, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.html'):
                continue
            p = os.path.join(r, f)
            try:
                s = open(p, encoding='utf-8').read()
            except Exception:
                continue
            m = PAGE_RE.search(s)
            if not m:
                continue
            try:
                P = json.loads(m.group(1))
            except Exception:
                continue
            g = P.get('tocGroups') or []
            if not g:
                continue
            k = toc_key(g)
            ent = found.setdefault(k, {'json': json.dumps(g, ensure_ascii=False), 'pages': []})
            ent['pages'].append(p)
    return found


def slim_root(root, check_only=False):
    """把 root 下所有内嵌目录抽成 目录.js；返回 (before, after, js_bytes, pages, groups)。"""
    groups = scan(root)
    if not groups:
        return None

    before = after = js_bytes = 0
    n_pages = 0
    used_paths = {}
    for k, g in groups.items():
        pages = g['pages']
        n_pages += len(pages)
        place = os.path.commonpath([os.path.dirname(p) for p in pages])
        name = JS_NAME if used_paths.get(place) in (None, k) else '目录-%s.js' % k
        js_path = os.path.join(place, name)
        if used_paths.get(place) not in (None, k):
            print('  !! 目录冲突，改用', os.path.relpath(js_path, ROOT))
        used_paths[place] = k

        payload = 'window.VOL_TOC = ' + g['json'] + ';\n'
        js_bytes += len(payload.encode('utf-8'))
        if not check_only:
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(payload)

        for p in pages:
            old_size = os.path.getsize(p)
            s = open(p, encoding='utf-8').read()
            m = PAGE_RE.search(s)
            if not m:
                continue
            P = json.loads(m.group(1))
            P.pop('tocGroups', None)
            # 只替换 JSON 本体（group 1），保留 ;</script>
            s2 = s[:m.start(1)] + json.dumps(P, ensure_ascii=False) + s[m.end(1):]

            rel = os.path.relpath(js_path, os.path.dirname(p)).replace('\\', '/')
            if not APP_RE.search(s2):
                print('  !! 找不到 app.js 引用，跳过:', os.path.relpath(p, ROOT))
                continue
            s2 = APP_RE.sub('<script src="%s"></script>\n<script src="\\1"></script>' % rel, s2, count=1)

            new_size = len(s2.encode('utf-8'))
            before += old_size
            after += new_size
            if not check_only:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(s2)
    return before, after, js_bytes, n_pages, len(groups)


def main():
    args = sys.argv[1:]
    check_only = '--check' in args
    roots = list(DEFAULT_ROOTS)
    if '--root' in args:
        i = args.index('--root')
        roots = [args[i + 1]]
    roots = [ROOT if os.path.isabs(r) else os.path.join(ROOT, r) for r in roots]

    tb = ta = 0
    for root in roots:
        if not os.path.isdir(root):
            print('跳过（不存在）:', os.path.relpath(root, ROOT))
            continue
        r = slim_root(root, check_only)
        if r is None:
            print('无内嵌目录，已是瘦身状态:', os.path.relpath(root, ROOT))
            continue
        before, after, js_bytes, pages, ngroups = r
        tb += before
        ta += after
        print('%s：%d 份目录 / %d 页 | %.1f MB → %.1f MB（目录 js %.2f MB，省 %.1f MB）' % (
            os.path.relpath(root, ROOT), ngroups, pages,
            before / 1048576, after / 1048576, js_bytes / 1048576, (before - after) / 1048576))

    if tb:
        print('合计：%.1f MB → %.1f MB，省 %.1f MB%s' % (
            tb / 1048576, ta / 1048576, (tb - ta) / 1048576,
            '（--check 未写入）' if check_only else ''))


if __name__ == '__main__':
    main()
