# -*- coding: utf-8 -*-
"""扫描英文原版两本书的正文章节标题位置（djvu.txt 连续文本）。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def find_body_chapters(path, patterns, skip_after_contents=True):
    t = open(path, encoding='utf-8').read()
    print('总长:', len(t))
    if skip_after_contents:
        # 找 CONTENTS 之后的正文起点：跳过目录
        ci = t.upper().find('CONTENTS')
        print('CONTENTS at', ci)
    results = []
    for name, pat in patterns:
        occ = [m.start() for m in re.finditer(pat, t, re.I)]
        # 正文位置 = 最后一个出现（目录在前，正文标题在后）
        pos = occ[-1] if occ else -1
        results.append((name, pos, len(occ)))
    for name, pos, cnt in results:
        ctx = t[pos:pos+90].replace('\n', ' | ') if pos >= 0 else '(未找到)'
        print('%-28s 出现%d次  pos=%s  %s' % (name, cnt, pos, ctx[:80]))
    return results

print('===== 斯大林需要和平 =====')
find_body_chapters(r'C:\导师文集\.tools\sources\snow\斯大林需要和平\stalin_peace_djvu.txt',
    [('Introduction', r'INTRODUCTION\s*by\s*MARTIN SOMMERS'),
     ('Ch1 WHY WE DONT UNDERSTAND', r'WHY WE DON.?\s*T UNDERSTAND THE RUSSIANS'),
     ('Ch2 AS IT LOOKS TO IVAN', r'AS IT LOOKS TO IVAN IVANOVITCH'),
     ('Ch3 WHY STALIN NEEDS PEACE', r'WHY STALIN NEEDS PEACE'),
     ('Ch4 INVESTMENT IN PEACE', r'INVESTMENT IN PEACE')])

print()
print('===== 苏联力量的格局 =====')
find_body_chapters(r'C:\导师文集\.tools\sources\snow\苏联力量的格局\soviet_power_djvu.txt',
    [('Ch1 LONG BRIGHT DAYS', r'LONG BRIGHT DAYS'),
     ('Ch2 STALIN ENTERS THE BALKANS', r'STALIN ENTERS THE BALKANS'),
     ('Ch3 POLISH INTERLUDE', r'POLISH INTERLUDE'),
     ('Ch4 RED STAR OVER EASTERN EUROPE', r'RED STAR OVER EASTERN EUROPE'),
     ('Ch5 UKRAINE WAKE OF CONQUEST', r'UKRAINE.{0,3}IN THE WAKE OF CONQUEST'),
     ('Ch6 VERDICT ON GERMANY', r'VERDICT ON GERMANY'),
     ('Ch7 WHEN RUSSIA FIGHTS JAPAN', r'WHEN RUSSIA FIGHTS JAPAN'),
     ('Ch8 THE TWO CHINAS', r'THE TWO CHINAS'),
     ('Ch9 STALIN AT WAR', r'STALIN AT WAR'),
     ('Ch10 MEN OF THE KREMLIN', r'MEN OF THE KREMLIN'),
     ('Ch11 RUSSIA REDISCOVERS HER PAST', r'RUSSIA REDISCOVERS HER PAST'),
     ('Ch12 PARTY AND THE PEOPLE', r'THE PARTY AND THE PEOPLE')])
