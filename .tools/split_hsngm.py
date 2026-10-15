# -*- coding: utf-8 -*-
"""split_hsngm.py — 把《红色中国内幕》OCR 页文本切成章节源文件。
输出: .tools/sources/snow/红区内幕/NN-标题.txt (UTF-8)
"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PAGES = r'C:\导师文集\.tools\sources\snow\红区内幕\pages'
OUT = r'C:\导师文集\.tools\sources\snow\红区内幕'
os.makedirs(OUT, exist_ok=True)

# 章节标题（与 books.json chapters 顺序对应）
TITLES = [
    "前言",
    "再次“违法”",
    "逃往苏区",
    "和彭德怀一起在前线",
    "不可思议的年轻军队",
    "牺牲至上",
    "奔向延安",
    "在红色堡垒延安",
    "我自己的房间",
    "青年人的自我服务",
    "朱德的生平故事",
    "“飞行军”的统帅——罗炳辉",
    "黄埔军校的老战士——徐向前",
    "中国文字的拉丁化",
    "少数民族的觉醒者",
    "中国革命的半边天",
    "三位女领导人",
    "红色共和国的妇女",
    "红星的明灭",
    "中国革命的分析",
    "未来的展望",
    "征战之中的八路军",
    "九月的早晨",
    "“一旦醒来，它将震撼世界”",
    "译后记",
]
# 每节起始物理页（含该页标题行）
STARTS = [6, 11, 24, 34, 42, 52, 70, 78, 87, 101, 112, 124, 134, 142, 149,
          164, 177, 186, 196, 209, 246, 256, 262, 279, 301]
SKIP = {9, 10}  # 目次页

def clean_page(text):
    """清理单页文本：去藏书章、页码、空行。"""
    lines = []
    for ln in text.split('\n'):
        t = ln.strip()
        if not t:
            continue
        if re.fullmatch(r'\d{1,4}', t):  # 独立页码
            continue
        # 去掉嵌在行中的藏书章标记
        t = re.sub(r'(中央社会主义学院|图书馆|图书铭?|藏书★|★藏书★|藏书)', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        if not t:
            continue
        lines.append(t)
    return lines

# 读取页面
pages = {}
for n in range(6, 302):
    f = os.path.join(PAGES, 'P%03d.txt' % n)
    if os.path.exists(f):
        pages[n] = open(f, encoding='utf-8').read()

# 按边界切分
sections = []  # (title, [lines])
for idx, start in enumerate(STARTS):
    end = STARTS[idx + 1] if idx + 1 < len(STARTS) else 302
    title = TITLES[idx]
    body = []
    for n in range(start, end):
        if n in SKIP:
            continue
        if n not in pages:
            continue
        body.extend(clean_page(pages[n]))
    sections.append((title, body))

# 去掉每节第一行的标题行（"一、再次"违法"" 等）
def strip_heading(lines, title):
    if not lines:
        return lines
    # 标题行通常很短且含 一、/二、/三、/前言/译后记 等
    first = lines[0]
    key = re.sub(r'^[一二三四五六七八九十]+\s*[、．.·]?\s*', '', title)
    if re.search(re.escape(key[:6]), first):
        return lines[1:]
    return lines

for idx, (title, body) in enumerate(sections, 1):
    body = strip_heading(body, title)
    fn = os.path.join(OUT, '%02d-%s.txt' % (idx, title))
    with open(fn, 'w', encoding='utf-8') as f:
        f.write('\n'.join(body))
    print('%02d-%s.txt  段落数=%d' % (idx, title, len(body)))

print('DONE')
