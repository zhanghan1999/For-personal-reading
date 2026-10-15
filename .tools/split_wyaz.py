# -*- coding: utf-8 -*-
"""split_wyaz.py — 把《为亚洲而战》OCR 页文本切成章节源文件。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PAGES = r'C:\导师文集\.tools\sources\snow\为亚洲而战\pages'
OUT = r'C:\导师文集\.tools\sources\snow\为亚洲而战'
os.makedirs(OUT, exist_ok=True)

TITLES = [
    "出版前言",
    "亡命者", "一个绅士和一个流氓", "七·七", "华北前线", "中国的防御力", "上海战事目睹记",
    "没有领袖的上海", "战场凭吊", "艾黎这个人", "工业合作社的诞生",
    "政治一瞥", "蒋介石", "争讼的遗产", "“亡失”的红军", "人民的军队", "香港的插曲",
    "月光和炸弹", "自由中国的基础", "生产的贫乏", "中国的主力",
    "一个理想的史诗", "国民党和官僚政治", "成都和赴成都途中", "中国艰苦的建设者", "明日的希望",
    "中国的激流", "边区政府", "雨中之旅", "延安的重聚", "女英雄的大学",
    "红色预言家", "中国红军和苏维埃战略", "一个县长的教训", "民主政治的实验",
    "游击工业", "八路军", "游击队的作战效力", "团结还是毁灭？",
    "自由中国的希望", "日本的命运", "上帝要毁灭谁？", "可能发生的事情",
    "革命和反动", "旧中国的上海和一二八抗战", "一九三九年同毛泽东的谈话", "一九四三年从重庆看中国之命运",
]
STARTS = [
    18, 27, 33, 39, 45, 53, 58, 69, 75, 84, 89, 96, 107, 112, 119, 127, 139,
    145, 154, 160, 167, 177, 185, 195, 203, 210, 221, 231, 239, 246, 253,
    259, 268, 275, 280, 287, 295, 302, 308, 316, 325, 337, 348, 360, 373, 410, 418,
]
SKIP = {24, 25, 26}  # 目录页

def clean_page(text):
    lines = []
    for ln in text.split('\n'):
        t = ln.strip()
        if not t:
            continue
        if re.fullmatch(r'\d{1,4}', t):
            continue
        t = re.sub(r'(中央社会主义学院|图书馆|图书铭?|藏书★|★藏书★|藏书)', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        if not t:
            continue
        lines.append(t)
    return lines

pages = {}
for n in range(6, 438):
    f = os.path.join(PAGES, 'P%03d.txt' % n)
    if os.path.exists(f):
        pages[n] = open(f, encoding='utf-8').read()

sections = []
for idx, start in enumerate(STARTS):
    end = STARTS[idx + 1] if idx + 1 < len(STARTS) else 438
    body = []
    for n in range(start, end):
        if n in SKIP:
            continue
        if n not in pages:
            continue
        body.extend(clean_page(pages[n]))
    sections.append((TITLES[idx], body))

def strip_heading(lines, title):
    if not lines:
        return lines
    key = re.sub(r'^[一二三四五六七八九十]+\s*[、．.·]?\s*', '', title)[:6]
    if re.search(re.escape(key), lines[0]):
        return lines[1:]
    return lines

for idx, (title, body) in enumerate(sections, 1):
    body = strip_heading(body, title)
    fn = os.path.join(OUT, '%02d-%s.txt' % (idx, title))
    with open(fn, 'w', encoding='utf-8') as f:
        f.write('\n'.join(body))
    print('%02d-%s.txt  段落数=%d' % (idx, title, len(body)))

print('DONE')
