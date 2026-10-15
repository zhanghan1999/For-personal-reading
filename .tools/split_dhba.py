# -*- coding: utf-8 -*-
"""split_dhba.py — 把《大河彼岸》OCR 页文本切成章节源文件。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PAGES = r'C:\导师文集\.tools\sources\snow\大河彼岸\pages'
OUT = r'C:\导师文集\.tools\sources\snow\大河彼岸'
os.makedirs(OUT, exist_ok=True)

TITLES = [
    "出版前言", "序言",
    "抵达北京", "宁静的都市", "宏伟的城市", "从孔子到毛泽东", "包头回顾", "蒙古的钢", "白云铁矿",
    "蒙古公社来去", "中国为什么会变红", "坐上总理的特别火车", "古山成新岸", "周恩来和美国", "餐桌旁的谈话",
    "巨变", "保安掠影", "长征", "实力人物", "毛泽东的家",
    "钢的十年", "数字问题", "有关跃进的问题", "“六〇—六二”对中国的影响", "从姚伟谈到私人企业",
    "东北——工业的心脏", "两条腿比一条腿好！", "上层社会", "科学与教育", "业余教育“部”", "访钢铁学院",
    "在北京看到的天鹅湖", "喜晤马海德医生", "普及医疗的成就", "我看到了人民解放军", "家庭：事实与幻想",
    "外国人眼中的中国医学史", "从约翰·D·谈到针灸",
    "八百名老革命战士", "党和人民", "公共安全", "“苦工”的真相", "学习与劳动改造", "有关少年罪犯的问题",
    "“百花齐放”的前奏", "团结—批评团结", "香花和毒草", "“百花齐放”的尾声",
    "人口问题", "访黄冈公社", "成功的公社", "西安", "延安——革命的博物馆", "延安师范学院",
    "穷苦人民的骄傲", "从柳林公社看中国的农村", "黄河之水今变蓝", "畅游三门峡", "洛阳与郑州",
    "重临上海", "“建设，建设”", "上海市长一夕谈", "文艺与音乐", "犯罪和刑罚", "鼎足而立的三镇",
    "四川：天府之国", "西藏实况", "少数民族", "云南之行",
]
STARTS = [
    7, 13,
    22, 30, 34, 38, 50, 58, 65, 70, 77, 83, 88, 96, 102,
    106, 108, 118, 127, 134, 142, 148, 150, 157, 161, 168, 175, 179, 183, 196,
    204, 219, 223, 235, 245, 257, 267, 272,
    283, 288, 292, 300, 305, 314, 319, 321, 328, 330,
    333, 340, 346, 359, 369, 376, 380, 390, 401, 406, 417,
    426, 434, 442, 450, 459, 463, 468, 479, 487, 491,
]
SKIP = {18, 19, 20, 21}  # 目录页

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
for n in range(0, 500):
    f = os.path.join(PAGES, 'P%03d.txt' % n)
    if os.path.exists(f):
        pages[n] = open(f, encoding='utf-8').read()

sections = []
for idx, start in enumerate(STARTS):
    end = STARTS[idx + 1] if idx + 1 < len(STARTS) else 500
    body = []
    for n in range(start, end):
        if n in SKIP:
            continue
        if n not in pages:
            continue
        body.extend(clean_page(pages[n]))
    sections.append((TITLES[idx], body))

for idx, (title, body) in enumerate(sections, 1):
    fn = os.path.join(OUT, '%02d-%s.txt' % (idx, title))
    with open(fn, 'w', encoding='utf-8') as f:
        f.write('\n'.join(body))
    print('%02d-%s.txt  段落数=%d' % (idx, title, len(body)))
print('DONE')
