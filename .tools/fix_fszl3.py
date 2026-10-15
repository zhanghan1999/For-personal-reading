# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
path = r'C:\导师文集\.tools\sources\snow\复始之旅\64-青年.txt'
lines = open(path, encoding='utf-8').read().split('\n')
while lines and lines[0].strip() in ('青', '年', ''):
    lines.pop(0)
open(path, 'w', encoding='utf-8').write('\n'.join(lines))
print('->', (lines[0][:40] if lines else '(empty)'))
