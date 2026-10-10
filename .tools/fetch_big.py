# -*- coding: utf-8 -*-
"""fetch_big.py — 用系统 curl 直连下载大源文件（需要非受限执行）。"""
import subprocess, sys, io, time, os, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RAW = r'C:\导师文集\.tools\sources\raw'
TASKS = [
    ('MEW20-003', 'https://raw.githubusercontent.com/MARX-ZH-CN/MARX-ZH-CN.github.io/main/docs/MEW-ZH/20/MEW20-003.html'),
    ('MEA26-017', 'https://raw.githubusercontent.com/MARX-ZH-CN/MARX-ZH-CN.github.io/main/docs/MEA/26/MEA26-017.html'),
]

def complete(path):
    try:
        with open(path, encoding='utf-8') as f:
            c = f.read()
        return c.rstrip().endswith('</html>') and 'Content truncated' not in c and os.path.getsize(path) > 5000
    except Exception:
        return False

def run_curl(args):
    return subprocess.run(args, capture_output=True).returncode

for name, url in TASKS:
    dst = os.path.join(RAW, name + '.html')
    ok = False
    # 直连重试
    for i in range(1, 4):
        if ok: break
        if i > 1: time.sleep(2 * i)
        rc = run_curl(['curl.exe', '-s', '--retry', '2', '--retry-all-errors',
                       '-o', dst, '--connect-timeout', '30', url])
        ok = complete(dst)
        print('%s direct try%d rc=%d size=%d ok=%s' % (name, i, rc,
              os.path.getsize(dst) if os.path.exists(dst) else -1, ok))
    # 代理
    if not ok:
        for label, base in [('allorigins', 'http://api.allorigins.win/raw?url='),
                            ('codetabs', 'http://api.codetabs.com/v1/proxy?quest=')]:
            if ok: break
            try:
                run_curl(['curl.exe', '-s', '-o', dst, '--connect-timeout', '30',
                          base + urllib.parse.quote(url, safe='')])
            except Exception as e:
                print(name, label, 'err', e)
            ok = complete(dst)
            print('%s %s size=%d ok=%s' % (name, label,
                  os.path.getsize(dst) if os.path.exists(dst) else -1, ok))
    print('FINAL %s size=%d ok=%s' % (name, os.path.getsize(dst) if os.path.exists(dst) else -1, ok))
