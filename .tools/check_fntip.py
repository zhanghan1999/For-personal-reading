# -*- coding: utf-8 -*-
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
d = r'C:\导师文集\教员\毛选\5'
for f in sorted(os.listdir(d)):
    if f.startswith('07-'):
        p = os.path.join(d, f)
        html = open(p, encoding='utf-8').read()
        print('FILE:', f)
        print('has fntip in html:', 'fntip' in html)
        print('fnref count:', html.count('class="fnref"'))
        print('note count:', html.count('class="note"'))
        fnref_hrefs = re.findall(r'class="fnref"><a href="#([^"]+)"', html)
        note_ids = re.findall(r'class="note" id="([^"]+)"', html)
        print('fnref hrefs:', fnref_hrefs)
        print('note ids:', note_ids)
        missing = [h for h in fnref_hrefs if h not in note_ids]
        print('missing (href 无对应 id):', missing)
        break
