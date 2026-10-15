# -*- coding: utf-8 -*-
"""重新扫描：取目录之后第一次出现的章节标题位置。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def scan(path, contents_marker, chapters, body_start_extra=6000):
    t = open(path, encoding='utf-8').read()
    ci = t.upper().find(contents_marker)
    body_start = ci + body_start_extra  # 目录之后
    print('文件:', path.split('\\')[-1], '总长', len(t), 'contents at', ci, 'body_start', body_start)
    results = []
    for name, pat in chapters:
        occ = [m.start() for m in re.finditer(pat, t, re.I)]
        body_occ = [p for p in occ if p > body_start]
        pos = body_occ[0] if body_occ else -1
        results.append((name, pos))
        ctx = t[pos:pos+80].replace('\n', ' | ') if pos >= 0 else '(未找到)'
        print('%-30s pos=%8s  %s' % (name, pos, ctx[:70]))
    print()
    return results

# 斯大林需要和平
scan(r'C:\导师文集\.tools\sources\snow\斯大林需要和平\stalin_peace_djvu.txt', 'CONTENTS',
    [('Introduction', r'INTRODUCTION\s*by\s*MARTIN SOMMERS'),
     ('Ch1', r'WHY WE DON.{0,3}T UNDERSTAND THE RUSSIANS'),
     ('Ch2', r'AS IT LOOKS TO IVAN IVANOVITCH'),
     ('Ch3', r'WHY STALIN NEEDS PEACE'),
     ('Ch4', r'INVESTMENT IN PEACE')], 4000)

# 苏联力量的格局
scan(r'C:\导师文集\.tools\sources\snow\苏联力量的格局\soviet_power_djvu.txt', 'CONTENTS',
    [('Ch1', r'LONG BRIGHT DAYS'),
     ('Ch2', r'STALIN ENTERS THE BALKANS'),
     ('Ch3', r'POLISH INTERLUDE'),
     ('Ch4', r'RED STAR OVER EASTERN EUROPE'),
     ('Ch5', r'UKRAINE.{0,3}IN THE WAKE OF CONQUEST'),
     ('Ch6', r'VERDICT ON GERMANY'),
     ('Ch7', r'WHEN RUSSIA FIGHTS JAPAN'),
     ('Ch8', r'THE TWO CHINAS'),
     ('Ch9', r'STALIN AT WAR'),
     ('Ch10', r'MEN OF THE KREMLIN'),
     ('Ch11', r'RUSSIA REDISCOVERS HER PAST'),
     ('Ch12', r'THE PARTY AND THE PEOPLE')], 8000)
