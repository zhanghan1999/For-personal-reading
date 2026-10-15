# -*- coding: utf-8 -*-
"""split_changmang.py — 把用户提供的《漫长的革命》(上海人民出版社1975年版·伍协力译, GB18030 txt)
按目录拆分为 33 个章节 txt（UTF-8），供 build_snow.py 生成站点页面。"""
import re, os

SRC = r'C:\Users\zh\Downloads\《漫长的革命》[美]埃德加·斯诺.txt'
OUT = r'C:\导师文集\.tools\sources\snow\漫长的革命'

raw = open(SRC, 'rb').read().decode('gb18030')
lines = [ln.rstrip('\r\n') for ln in raw.splitlines()]

SEC_RE = re.compile(r'^[\(（][一二三四五六七八九十Ｏ○〇0-9]{1,4}[\)）]\s*\S')
BU_HEADERS = {'一、一个不同的国家？', '二、医疗和人口控制', '三、无产阶级文化大革命',
              '四、军队、党和人民', '五、人民公社', '六、与总理一夕之谈',
              '七、同主席共进早餐', '八、尼克松要去紫禁城'}
PAGE_HEADER = '[美]埃德加·斯诺《漫长的革命》'
APP_TITLES = ['一、山南海北', '二、1964年同周恩来的谈话',
              '三、中国共产党中央委员会关于无产阶级文化大革命的决定',
              '四、中国共产党章程', '五、1970年12月18日斯诺同毛泽东谈话纪要',
              '六、1936年9月底至10月初斯诺采访毛泽东纪要', '七、在斯诺最后的日子里']


def strip_artifacts(block, in_appendix_six=False, drop_first_line=True):
    """去掉页眉/页码等噪声，返回行列表。"""
    out = []
    for k, ln in enumerate(block):
        if k == 0 and drop_first_line and ln.strip():
            continue  # 节标题行
        s = ln.strip()
        if not s:
            if out and out[-1] != '':
                out.append('')
            continue
        if s == PAGE_HEADER:
            continue
        if s == '附录':
            continue
        if re.fullmatch(r'\d{1,4}', s):
            continue
        if in_appendix_six and (s == '六、1936年9月底至10月初斯诺采访毛泽东纪要'
                                or s == '（同《毛泽东自述：一个共产党员的经历》1936年与斯诺的谈话）'):
            continue
        if s in BU_HEADERS:
            continue
        out.append(s)
    while out and out[-1] == '':
        out.pop()
    return out


def write_chapter(idx, title, block):
    fn = '%02d-%s.txt' % (idx, re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', title)[:40])
    with open(os.path.join(OUT, fn), 'w', encoding='utf-8') as f:
        f.write('\n'.join(block))
    print('  %s <- %s (%d 行)' % (fn, title, len(block)))


# —— 1. 译者的话 ——
tl = [i for i, l in enumerate(lines) if l.strip() == '译者的话']
assert len(tl) >= 2, tl
body_start = next(i for i in range(tl[1], len(lines)) if lines[i].strip() == '一、一个不同的国家？')
yi_block = lines[tl[1] + 1:body_start]
write_chapter(1, '译者的话', strip_artifacts(yi_block))

# —— 2. 正文 25 节 ——
app_start = next(i for i in range(body_start, len(lines)) if lines[i].strip() == '附录')
bounds = [i for i in range(body_start, app_start) if SEC_RE.match(lines[i].strip())]
print('正文节边界数:', len(bounds))
assert len(bounds) == 25, len(bounds)

SEC_TITLES = ['天安门上的会见', '周总理的一个暗示', '文化革命的实质', '普通公民王某',
              '针刺流产', '什么是针刺？', '性和人口控制', '一些特殊情况', '“把重点放到农村去”',
              '崇拜的降温', '文化', '通过宣传搞阴谋', '公开的战争', '一种军队专政?',
              '“为人民服务”', '作为建设者的军队', '艾丽斯在南泥湾', '军队和人民',
              '开端', '令人激动的旅行', '富人和穷人', '后顾前瞻',
              '周恩来与敞开的门', '同毛泽东的一次交谈', '实力地位']
assert len(SEC_TITLES) == 25

for i in range(25):
    start = bounds[i]
    end = bounds[i + 1] if i + 1 < 25 else app_start
    block = strip_artifacts(lines[start:end])
    write_chapter(2 + i, SEC_TITLES[i], block)

# —— 3. 附录 7 篇 ——
app_bounds = []
last = None
for i in range(app_start, len(lines)):
    s = lines[i].strip()
    for t in APP_TITLES:
        if s.startswith(t):
            if t != last:          # 去重：附录六内的重复页眉不计为新边界
                app_bounds.append(i)
                last = t
            break
print('附录边界数:', len(app_bounds))
assert len(app_bounds) == 7, app_bounds

APP_TITLES_SHORT = ['附录一 山南海北（1965年1月9日同毛泽东的谈话）',
                    '附录二 1964年同周恩来的谈话',
                    '附录三 中国共产党中央委员会关于无产阶级文化大革命的决定',
                    '附录四 中国共产党章程',
                    '附录五 1970年12月18日斯诺同毛泽东谈话纪要',
                    '附录六 1936年采访毛泽东纪要',
                    '附录七 在斯诺最后的日子里']
for k in range(7):
    start = app_bounds[k]
    end = app_bounds[k + 1] if k + 1 < 7 else len(lines)
    in6 = (k == 5)
    block = strip_artifacts(lines[start:end], in_appendix_six=in6)
    write_chapter(27 + k, APP_TITLES_SHORT[k], block)

print('完成。共 33 个章节文件。')
