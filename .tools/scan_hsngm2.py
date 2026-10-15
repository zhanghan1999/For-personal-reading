# -*- coding: utf-8 -*-
"""按短行标题精确扫描《红色中国内幕》章节边界。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PAGES = r'C:\导师文集\.tools\sources\snow\红区内幕\pages'
page_files = sorted([f for f in os.listdir(PAGES) if re.match(r'P\d{3}\.txt', f)])
pages = {}
for f in page_files:
    num = int(f[1:4])
    pages[num] = open(os.path.join(PAGES, f), encoding='utf-8').read().split('\n')

targets = [
    ('前言', r'前言'),
    ('一再次违法', r'再次'),
    ('二逃往苏区', r'逃往苏区'),
    ('三和彭德怀在前线', r'和彭德怀一起在前线'),
    ('四不可思议的年轻军队', r'不可思议的年轻军队'),
    ('五牺牲至上', r'牺牲至上'),
    ('六奔向延安', r'奔向延安'),
    ('一在红色堡垒延安', r'在红色堡垒延安'),
    ('二我自己的房间', r'我自己的房间'),
    ('三青年人的自我服务', r'青年人的自我服务'),
    ('四朱德的生平故事', r'朱德的生平故事'),
    ('五飞行军统帅罗炳辉', r'罗炳辉'),
    ('六黄埔老战士徐向前', r'徐向前'),
    ('七中国文字的拉丁化', r'文字的拉丁化'),
    ('八少数民族的觉醒者', r'少数民族的觉醒者'),
    ('一中国革命的半边天', r'半边天'),
    ('二三位女领导人', r'三位女领导人'),
    ('1蔡畅', r'蔡畅'),
    ('2刘群先', r'刘群先'),
    ('3康克清', r'康克清'),
    ('三红色共和国的妇女', r'红色共和国的妇女'),
    ('一红星的明灭', r'红星的明灭'),
    ('二中国革命的分析', r'中国革命的分析'),
    ('1毛泽东', r'毛泽东：中国革命'),
    ('2洛甫', r'洛甫：中国革命'),
    ('3朱德', r'朱德：红军的故事'),
    ('三未来的展望', r'未来的展望'),
    ('一征战之中的八路军', r'征战之中的八路军'),
    ('二九月的早晨', r'九月的早晨'),
    ('三一旦醒来', r'一旦醒来，它将震撼世界'),
    ('译后记', r'译后记'),
]

for name, pat in targets:
    rx = re.compile(pat)
    for num in sorted(pages):
        if num < 11:
            continue
        for ln in pages[num]:
            t = ln.strip()
            # 短行标题：去标点后长度适中
            core = re.sub(r'[、．.。·—\-—\s""''“”（）()\d①②③④⑤⑥⑦⑧]', '', t)
            if 2 <= len(core) <= 14 and rx.search(t):
                print('%-22s => P%03d  行: %s' % (name, num, t[:40]))
                break
