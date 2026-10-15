# -*- coding: utf-8 -*-
"""清理《为亚洲而战》章节文件开头的篇/章标题行。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT = r'C:\导师文集\.tools\sources\snow\为亚洲而战'

PIAN = ['第一篇从北平到上海', '第二篇从上海到汉口', '第三篇南部前线', '第四篇一条吮自己创伤的蛟龙',
        '第五篇中国的"工合线"', '第六篇回到西北', '第七篇红色的战略', '第八篇在敌后',
        '第九篇帝国或民主', '第十篇中国抗战的前景']
ZHANG = ['出版前言', '亡命者', '一个绅士和一个流氓', '七·七', '华北前线', '中国的防御力', '上海战事目睹记',
         '没有领袖的上海', '战场凭吊', '艾黎这个人', '工业合作社的诞生', '政治一瞥', '蒋介石', '争讼的遗产',
         '"亡失"的红军', '人民的军队', '香港的插曲', '月光和炸弹', '自由中国的基础', '生产的贫乏', '中国的主力',
         '一个理想的史诗', '国民党和官僚政治', '成都和赴成都途中', '中国艰苦的建设者', '明日的希望',
         '中国的激流', '边区政府', '雨中之旅', '延安的重聚', '女英雄的大学', '红色预言家',
         '中国红军和苏维埃战略', '一个县长的教训', '民主政治的实验', '游击工业', '八路军', '游击队的作战效力',
         '团结还是毁灭', '自由中国的希望', '日本的命运', '上帝要毁灭谁', '可能发生的事情', '革命和反动',
         '旧中国的上海和一二八抗战', '一九三九年同毛泽东的谈话', '一九四三年从重庆看中国之命运']

def norm(s):
    return re.sub(r'[\s，。、．.·:：""''（）()\-—_·]', '', s)

known = set()
for t in PIAN + ZHANG:
    known.add(norm(t))
    known.add(norm(t)[:8])

for fn in sorted(os.listdir(OUT)):
    if not re.match(r'\d{2}-.+\.txt$', fn):
        continue
    path = os.path.join(OUT, fn)
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    # 去掉开头的标题行
    i = 0
    while i < len(lines):
        t = lines[i].strip()
        if not t:
            i += 1
            continue
        if len(norm(t)) <= 12 and norm(t) in known:
            i += 1
            continue
        break
    new = lines[i:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new))
    if i > 0:
        print('%s: 移除 %d 行标题，新开头: %s' % (fn, i, (new[0][:30] if new else '(空)')))
print('DONE')
