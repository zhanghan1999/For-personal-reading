# -*- coding: utf-8 -*-
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\snow\复始之旅'

PIAN = ['第一篇游历', '第二篇煽火', '第三篇大河彼岸', '第四篇冷战']
ZHANG = ['出版前言', '到达中国', '饿殍遍野', '来自肯塔基', '上海', '编辑密勒氏评论报', '在密苏里的岁月',
         '游历记者', '华南', '文化传播者', '石头收藏家', '食生肉的国家', '龙云治下的生活', '旅途',
         '去缅甸路上', '锡袍的国度', '印度初观', '甘地和尼赫鲁', '孟买历险记', '与宋庆龄的友谊',
         '基督教徒和共产党人', '宋庆龄和历史', '记一次被遗忘的战役', '尼姆', '南洋', '勿吃邻居',
         '安家北京', '侥幸', '学习倒立', '活的中国', '法西斯主义和共产主义之间', '煽风点火', '行动',
         '无为而无不为', '跨越雷池', '冲破封锁', '周恩来', '与毛一起吃点心', '窑洞里的预言家', '只争朝夕',
         '出路', '从西安事变到抗战', '出北京记', '战争的实质', '卡尔森对未来的一瞥', '我们在开创一项事业',
         '我成了一名传教士', '在吕宋的插曲', '蒋家王朝的内争', '幻想的破灭', '土地改革者的神话',
         '战争中的战争', '大屠杀', '惜别', '老实人的归来', '会见军队', '武装部队总司令', '结束与开始',
         '在非洲上空迷失方向', '经过沙漠上空飞往新德里', '同尼赫鲁辩论', '爆竹，开始响起来吧', '乌克兰交响乐团',
         '青年', '亲爱的总统先生', '李维诺夫的警告', '和平革命', '非政治关系', '失去的时间',
         '同罗斯福总统的最后一次谈话', '从摩西泰勒夫人的城堡到延安', '最先进入维也纳', '广岛在莫斯科引起的反响',
         '终身签证', '伊本沙特国王', '在德里的逗留', '新帝国主义', '更远的东方', '我们阻止一场革命',
         '甘地之死', '甘地的实质', '同贾瓦哈拉尔尼赫鲁共进晚餐', '需要新表']

def norm(s):
    return re.sub(r'[\s，。、．.·:：“”"''（）()\-—_·\d!！?？]', '', s)

known = set()
for t in PIAN + ZHANG:
    known.add(norm(t))
    known.add(norm(t)[:8])

for fn in sorted(os.listdir(OUT)):
    if not re.match(r'\d{2}-.+\.txt$', fn):
        continue
    path = os.path.join(OUT, fn)
    lines = open(path, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        t = lines[i].strip()
        if not t:
            i += 1
            continue
        nt = norm(t)
        if len(nt) <= 12 and (nt in known or any(nt.startswith(k[:4]) for k in known if len(k) >= 4)):
            i += 1
            continue
        break
    new = lines[i:]
    open(path, 'w', encoding='utf-8').write('\n'.join(new))
    if i > 0:
        print('%s: 移除 %d 行，新开头: %s' % (fn, i, (new[0][:26] if new else '(空)')))
print('DONE')
