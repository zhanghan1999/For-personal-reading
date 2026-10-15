# -*- coding: utf-8 -*-
"""split_fszl.py — 把《复始之旅》OCR 页文本切成章节源文件。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PAGES = r'C:\导师文集\.tools\sources\snow\复始之旅\pages'
OUT = r'C:\导师文集\.tools\sources\snow\复始之旅'
os.makedirs(OUT, exist_ok=True)

TITLES = [
    "出版前言",
    "到达中国", "饿殍遍野", "来自肯塔基", "上海！", "编辑《密勒氏评论报》", "在密苏里的岁月",
    "游历记者", "华南", "文化传播者", "石头收藏家", "食生肉的国家", "龙云治下的生活",
    "旅途", "去缅甸路上", "锡袍的国度", "印度初观", "甘地和尼赫鲁", "孟买历险记",
    "与宋庆龄的友谊", "基督教徒和共产党人", "宋庆龄和历史", "记一次被遗忘的战役",
    "尼姆", "南洋", "勿吃邻居",
    "安家北京", "侥幸", "学习倒立", "活的中国", "“法西斯主义和共产主义之间”", "煽风点火",
    "行动", "“无为而无不为”", "跨越雷池", "冲破封锁", "周恩来", "与毛一起吃点心",
    "窑洞里的预言家", "只争朝夕", "出路", "从西安事变到抗战", "出北京记", "战争的实质",
    "卡尔森对未来的一瞥", "我们在开创一项事业", "我成了一名传教士", "在吕宋的插曲",
    "蒋家王朝的内争", "幻想的破灭", "“土地改革者”的神话", "战争中的战争", "大屠杀", "惜别",
    "老实人的归来", "会见军队", "武装部队总司令", "结束与开始", "在非洲上空迷失方向",
    "经过沙漠上空飞往新德里", "同尼赫鲁辩论", "“爆竹，开始响起来吧！”", "乌克兰交响乐团",
    "青年", "亲爱的总统先生", "李维诺夫的警告", "“和平革命”", "“非政治”关系", "失去的时间",
    "同罗斯福总统的最后一次谈话", "从摩西·泰勒夫人的城堡到延安", "最先进入维也纳",
    "广岛在莫斯科引起的反响",
    "终身签证", "伊本·沙特国王", "在德里的逗留", "新“帝国主义”", "更远的东方",
    "我们阻止一场革命", "甘地之死", "甘地的实质", "同贾瓦哈拉尔·尼赫鲁共进晚餐", "需要新表",
]
STARTS = [
    11,
    21, 26, 32, 36, 46, 52, 55, 61, 67, 73, 74, 79, 83, 90, 94, 101, 107, 110,
    116, 119, 125, 133, 141, 148, 152,
    161, 167, 171, 176, 180, 186, 192, 195, 200, 203, 208, 211, 216, 223, 230,
    239, 245, 251, 254, 258, 266, 273, 278, 288, 295, 302, 307, 311,
    317, 325, 329, 336, 339, 344, 351, 357, 362, 366, 374, 378, 387, 390, 399,
    405, 411, 417, 427,
    436, 441, 449, 455, 460, 464, 471, 479, 484, 492,
]
SKIP = {17, 18, 19, 20}  # 目录页

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
for n in range(0, 505):
    f = os.path.join(PAGES, 'P%03d.txt' % n)
    if os.path.exists(f):
        pages[n] = open(f, encoding='utf-8').read()

sections = []
for idx, start in enumerate(STARTS):
    end = STARTS[idx + 1] if idx + 1 < len(STARTS) else 505
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
