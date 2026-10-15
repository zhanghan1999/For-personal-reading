# -*- coding: utf-8 -*-
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'C:\导师文集\.tools\sources\snow\大河彼岸'

PIAN = ['第一篇重访中国', '第二篇在浪涛冲击的地方', '第三篇社会主义建设', '第四篇民主专政',
        '第五篇西北：新中国的摇篮', '第六篇江南行']
ZHANG = ['出版前言', '序言', '抵达北京', '宁静的都市', '宏伟的城市', '从孔子到毛泽东', '包头回顾',
         '蒙古的钢', '白云铁矿', '蒙古公社来去', '中国为什么会变红', '坐上总理的特别火车', '古山成新岸',
         '周恩来和美国', '餐桌旁的谈话', '巨变', '保安掠影', '长征', '实力人物', '毛泽东的家', '钢的十年',
         '数字问题', '有关跃进的问题', '六〇一六二对中国的影响', '从姚伟谈到私人企业', '东北——工业的心脏',
         '两条腿比一条腿好', '上层社会', '科学与教育', '业余教育部', '访钢铁学院', '在北京看到的天鹅湖',
         '喜晤马海德医生', '普及医疗的成就', '我看到了人民解放军', '家庭：事实与幻想', '外国人眼中的中国医学史',
         '从约翰D谈到针灸', '八百名老革命战士', '党和人民', '公共安全', '苦工的真相', '学习与劳动改造',
         '有关少年罪犯的问题', '百花齐放的前奏', '团结批评团结', '香花和毒草', '百花齐放的尾声', '人口问题',
         '访黄冈公社', '成功的公社', '西安', '延安革命的博物馆', '延安师范学院', '穷苦人民的骄傲',
         '从柳林公社看中国的农村', '黄河之水今变蓝', '畅游三门峡', '洛阳与郑州', '重临上海', '建设建设',
         '上海市长一夕谈', '文艺与音乐', '犯罪和刑罚', '鼎足而立的三镇', '四川天府之国', '西藏实况',
         '少数民族', '云南之行']

def norm(s):
    return re.sub(r'[\s，。、．.·:：“”"''（）()\-—_·]', '', s)

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
