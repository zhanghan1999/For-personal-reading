# -*- coding: utf-8 -*-
"""probe_mzdbl.py — 探测 mzdbl.cn 站点结构，查找《毛泽东军事文集》栏目。"""
import subprocess, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT = r'C:\导师文集\.tools\sources\mzdbl'
os.makedirs(OUT, exist_ok=True)

def fetch(url, name):
    dst = os.path.join(OUT, name)
    subprocess.run(['curl.exe', '-s', '-L', '--connect-timeout', '20', '--max-time', '60', '-o', dst, url])
    raw = open(dst, 'rb').read()
    for enc in ('gb18030', 'utf-8'):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode('gb18030', errors='replace')

# 首页
home = fetch('http://www.mzdbl.cn/', 'index.html')
print('home size:', len(home))
# 找所有栏目链接
links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', home, flags=re.S)
for href, txt in links:
    t = re.sub(r'<[^>]+>', '', txt).strip()
    if t and re.search(r'军事|文集|毛选|选集', t):
        print('HIT:', t[:30], '->', href[:80])
