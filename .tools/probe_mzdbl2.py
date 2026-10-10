# -*- coding: utf-8 -*-
"""probe_mzdbl2.py — 探测 mzdbl.cn 军事文集栏目。"""
import subprocess, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT = r'C:\导师文集\.tools\sources\mzdbl'
os.makedirs(OUT, exist_ok=True)

def fetch(url, name):
    dst = os.path.join(OUT, name)
    subprocess.run(['curl.exe', '-s', '-L', '--connect-timeout', '20', '--max-time', '60', '-o', dst, url])
    raw = open(dst, 'rb').read()
    try:
        return raw.decode('gb18030')
    except Exception:
        return raw.decode('gb18030', errors='replace')

# 1) 新增内容页：查"军事文集"
for name in ('xin9.html', 'xin8.html', 'xin7.html', 'xin6.html'):
    t = fetch('http://www.mzdbl.cn/' + name, name)
    if '军事' in t:
        print('==', name, '含有 军事 关键词 ==')
        for m in re.finditer(r'.{40}军事.{40}', t, re.S):
            print('  ', m.group(0).replace('\n', ' ')[:90])
    else:
        print(name, ': 无军事关键词, 链接数', len(re.findall(r'<a ', t)))

# 2) 常见栏目路径探测
for path in ('junshi/', 'junshiwenji/', 'wenji/', 'maoxuan/', 'jundui.html'):
    t = fetch('http://www.mzdbl.cn/' + path, 'probe-' + path.replace('/', '_') + '.html')
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    print('path', path, '-> size', len(t), 'title:', (title.group(1).strip() if title else 'N/A')[:30])
