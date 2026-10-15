# -*- coding: utf-8 -*-
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def clean_block(text):
    lines = []
    for ln in text.split('\n'):
        t = ln.strip()
        if not t:
            lines.append('')
            continue
        if re.fullmatch(r'\d{1,4}', t):
            continue
        if re.fullmatch(r'[\s<>4i\-–—•·\u2192]+', t):
            continue
        t = re.sub(r'\s+', ' ', t)
        lines.append(t)
    out = []
    prev_blank = False
    for ln in lines:
        if not ln:
            if not prev_blank:
                out.append('')
            prev_blank = True
        else:
            out.append(ln)
            prev_blank = False
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return out

# 修复乌克兰章
d = r'C:\导师文集\.tools\sources\snow\苏联力量的格局'
broken = os.path.join(d, '05-Ukraine')
if os.path.exists(broken):
    os.remove(broken)
    print('已删除损坏文件 05-Ukraine')
t = open(os.path.join(d, 'soviet_power_djvu.txt'), encoding='utf-8').read()
seg = t[156330:167497]
lines = clean_block(seg)
fn = os.path.join(d, '05-Ukraine in the Wake of Conquest.txt')
open(fn, 'w', encoding='utf-8').write('\n'.join(lines))
print('已重建', os.path.basename(fn), '段落', len(lines))

# 清理 01-Introduction（斯大林）开头的目录残留
d2 = r'C:\导师文集\.tools\sources\snow\斯大林需要和平'
p1 = os.path.join(d2, '01-Introduction.txt')
ls = open(p1, encoding='utf-8').read().split('\n')
while ls and ('INVESTMENT IN PEACE 151' in ls[0] or not ls[0].strip()):
    ls.pop(0)
open(p1, 'w', encoding='utf-8').write('\n'.join(ls))
print('01-Introduction 清理后开头:', ls[0][:40])

# 清理 04-Why Stalin Needs Peace 的第二章结尾残留
p4 = os.path.join(d2, '04-Why Stalin Needs Peace.txt')
ls = open(p4, encoding='utf-8').read().split('\n')
# 去掉开头到 "(3 J" 标记之间的非标题行，并去掉 "(3 J"
i = 0
while i < len(ls):
    t0 = ls[i].strip()
    if not t0:
        i += 1
        continue
    if t0 == '(3 J':
        i += 1
        break
    i += 1
ls = ls[i:]
# 去掉可能残留的空行
while ls and not ls[0].strip():
    ls.pop(0)
open(p4, 'w', encoding='utf-8').write('\n'.join(ls))
print('04 清理后开头:', ls[0][:50])
print('DONE')
