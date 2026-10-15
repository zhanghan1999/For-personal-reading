# -*- coding: utf-8 -*-
"""split_eng.py — 把两本英文原版 djvu.txt 切成章节源文件。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    {
        'key': '斯大林需要和平',
        'src': r'C:\导师文集\.tools\sources\snow\斯大林需要和平\stalin_peace_djvu.txt',
        'titles': ["Introduction", "Why We Don’t Understand the Russians",
                   "As It Looks to Ivan Ivanovitch", "Why Stalin Needs Peace",
                   "Investment in Peace"],
        'starts': [4100, 42597, 83663, 126134, 173207],
        'end': 212500,
    },
    {
        'key': '苏联力量的格局',
        'src': r'C:\导师文集\.tools\sources\snow\苏联力量的格局\soviet_power_djvu.txt',
        'titles': ["Long Bright Days", "Stalin Enters the Balkans", "Polish Interlude",
                   "Red Star over Eastern Europe", "Ukraine: In the Wake of Conquest",
                   "Verdict on Germany", "When Russia Fights Japan", "The Two Chinas",
                   "Stalin at War", "Men of the Kremlin", "Russia Rediscovers Her Past",
                   "The Party and the People"],
        'starts': [13929, 53465, 83527, 111688, 156330, 167497, 206392, 232002,
                   275481, 323430, 351553, 379714],
        'end': 394000,
    },
]

def clean_block(text):
    """清理英文 OCR 块：去页码、阅读器标记、多余空行。"""
    lines = []
    for ln in text.split('\n'):
        t = ln.strip()
        if not t:
            lines.append('')
            continue
        if re.fullmatch(r'\d{1,4}', t):  # 页码
            continue
        if re.fullmatch(r'[\s<>4i\-–—•·\u2192]+', t):  # 阅读器标记/装饰
            continue
        # 合并行内多余空格
        t = re.sub(r'\s+', ' ', t)
        lines.append(t)
    # 折叠连续空行
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
    # 去掉首尾空行
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return out

for book in BOOKS:
    t = open(book['src'], encoding='utf-8').read()
    outdir = os.path.join(r'C:\导师文集\.tools\sources\snow', book['key'])
    os.makedirs(outdir, exist_ok=True)
    starts = book['starts'] + [book['end']]
    for i, title in enumerate(book['titles']):
        seg = t[starts[i]:starts[i + 1]]
        lines = clean_block(seg)
        fn = os.path.join(outdir, '%02d-%s.txt' % (i + 1, title))
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print('%02d-%s.txt  段落=%d 字符=%d' % (i + 1, title, len(lines), sum(len(x) for x in lines)))
print('DONE')
