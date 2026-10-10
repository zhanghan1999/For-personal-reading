# -*- coding: utf-8 -*-
"""crawl_pp.py — 爬取人民网 64162/64165/70293 分栏的 30 页索引，GBK 解码后找斯大林相关条目。"""
import subprocess, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\pp'
os.makedirs(OUT, exist_ok=True)

base = 'http://cpc.people.com.cn/GB/64162/64165/70293/{0}/index.html'
hits = []
for i in range(70294, 70324):
    url = base.format(i)
    dst = os.path.join(OUT, '%d.html' % i)
    if not os.path.exists(dst) or os.path.getsize(dst) < 200:
        subprocess.run(['curl.exe', '-s', '--connect-timeout', '15', '-o', dst, url])
    try:
        t = open(dst, 'rb').read().decode('gb18030', errors='replace')
    except Exception:
        continue
    links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t, flags=re.S)
    for href, txt in links:
        txt2 = re.sub(r'<[^>]+>', '', txt).strip()
        if re.search(r'斯大林|列宁主义基础|辩证唯物主义|历史唯物主义|联共|斯大林选集', txt2):
            hits.append((i, txt2[:60], href[:120]))
    print('page', i, 'links:', len(links), 'size:', os.path.getsize(dst))

print('==== HITS ====')
for h in hits:
    print(h)
print('total hits:', len(hits))
