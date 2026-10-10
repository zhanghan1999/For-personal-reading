# -*- coding: utf-8 -*-
"""dl_stalin_pdf2.py — 续传下载 39MB 斯大林全集 PDF（长超时），完成后再检索。"""
import subprocess, sys, io, os, urllib.parse, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

rel = '斯大林全集/新编《斯大林全集》全20卷正卷（诸夏怀斯社版）.pdf'
url = 'https://raw.githubusercontent.com/RedRevolution1949/marx-lenin-stalin-mao/main/' + urllib.parse.quote(rel)
dst = r'C:\导师文集\.tools\sources\stalin\sidalin-quanji.pdf'
print('url:', url, flush=True)

size = os.path.getsize(dst) if os.path.exists(dst) else 0
print('existing size:', size, flush=True)
# 续传下载（-C - 断点续传），超时放宽到 1800 秒
rc = subprocess.run(['curl.exe', '-s', '-L', '-C', '-', '--retry', '5', '--retry-all-errors',
                     '-o', dst, '--connect-timeout', '30', '--max-time', '1800', url]).returncode
print('curl rc:', rc, flush=True)
size2 = os.path.getsize(dst) if os.path.exists(dst) else -1
print('size after:', size2, flush=True)

if size2 > 30000000:
    try:
        import fitz
        doc = fitz.open(dst)
        print('pages:', doc.page_count, flush=True)
        p0 = doc[0].get_text()[:120]
        print('page0:', repr(p0), flush=True)
        hits = []
        for i in range(doc.page_count):
            t = doc[i].get_text()
            if '论列宁主义基础' in t:
                hits.append(i)
        print('hits:', hits[:30], 'total:', len(hits), flush=True)
        doc.close()
    except Exception as e:
        print('extract error:', e, flush=True)
else:
    print('DOWNLOAD INCOMPLETE, cannot extract', flush=True)
