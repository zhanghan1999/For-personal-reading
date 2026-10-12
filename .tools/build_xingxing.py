# -*- coding: utf-8 -*-
"""build_xingxing.py — 把 OCR 出的《西行漫记》正文按目录切分成 57 节，生成站点页面。
先决：.tools/sources/xingxing/pages/P*.txt 已由 ocr_xingxing.py 生成。
产物：
  其他学习/埃德加·斯诺/红星照耀中国/          章节页（NN-节名.html）
  其他学习/埃德加·斯诺/红星照耀中国.html      书选页（12 篇卡片）
"""
import os, re, sys, io, html as htmllib, difflib
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
PAGES = r'C:\导师文集\.tools\sources\xingxing\pages'
SNOW = os.path.join(ROOT, '其他学习', '埃德加·斯诺')
BOOK_DIR = os.path.join(SNOW, '红星照耀中国')

# 目录（1979 三联董乐山译本，来自 PDF 目录页）
TOC = [
    ('第一篇', '探寻红色中国', ['一些未获解答的问题', '去西安的慢车', '汉代青铜', '通过红色大门']),
    ('第二篇', '去红都的道路', ['遭白匪追逐', '造反者', '贺龙二三事', '红军旅伴']),
    ('第三篇', '在保安', ['苏维埃掌权人物', '共产党的基本政策', '论抗日战争', '悬赏二百万元的首级', '红军剧社']),
    ('第四篇', '一个共产党员的由来', ['童年', '在长沙的日子', '革命的前奏', '国民革命时期', '苏维埃运动', '红军的成长']),
    ('第五篇', '长征', ['第五次围剿', '举国大迁移', '大渡河英雄', '过大草地']),
    ('第六篇', '红星在西北', ['陕西苏区：开创时期', '死亡和捐税', '苏维埃社会', '货币解剖', '人生五十始！']),
    ('第七篇', '去前线的路上', ['同红色农民谈话', '苏区工业', '“他们唱得太多了”']),
    ('第八篇', '同红军在一起', ['“真正的”红军', '彭德怀印象', '为什么当红军？', '游击战术', '红军战士的生活', '政治课']),
    ('第九篇', '同红军在一起（续）', ['红色窑工徐海东', '中国的阶级战争', '四大马', '穆斯林和马克思主义者']),
    ('第十篇', '战争与和平', ['再谈马', '“红小鬼”', '实践中的统一战线', '关于朱德']),
    ('第十一篇', '回到保安', ['路上的邂逅', '保安的生活', '俄国的影响', '中国共产主义运动和共产国际', '那个外国智囊', '别了，红色中国']),
    ('第十二篇', '又是白色世界', ['兵变前奏', '总司令被逮', '蒋，张和共产党', '“针锋相对”', '《友谊地久天长》？', '红色的天际']),
]
# 显示用的节标题替代表（PDF 目录 OCR 有误的纠正）
TITLE_FIX = {'汉代表铜': '汉代青铜', '人生五十始': '人生五十始！'}
# 已知 OCR 变体别名（别名 → 规范标题），用于匹配
TITLE_ALIAS = {'汉代表铜': '汉代青铜', '人生五十始': '人生五十始！',
               '第五次围巢': '第五次围剿', '总司令被速': '总司令被逮',
               '共产国际': '中国共产主义运动和共产国际'}

ALL_SECTIONS = []   # [(篇no, 篇名, 节名)]
for pi, (p, pname, secs) in enumerate(TOC, 1):
    for sec in secs:
        ALL_SECTIONS.append((pi, pname, sec))

def norm(s):
    s = s.replace('“', '').replace('”', '').replace('"', '').replace('‘', '').replace('’', '')
    s = re.sub(r'[《》？！。，、：；·—－\s　]+', '', s)
    return s.lower()

def load_ocr():
    pages = []
    for i in range(459):
        fp = os.path.join(PAGES, 'P%03d.txt' % i)
        if not os.path.exists(fp):
            continue
        with open(fp, encoding='utf-8') as f:
            pages.append((i, f.read()))
    return pages

def clean_page(raw):
    out = []
    for ln in raw.splitlines():
        t = ln.strip()
        if not t:
            continue
        if '欢迎关注' in t or '学习理论' in t:
            continue
        if re.fullmatch(r'\d{1,4}', t):            # 页号
            continue
        if re.fullmatch(r'[-\u2014·．.~～]{1,6}\s*\d{1,4}\s*[-\u2014·．.~～]{1,6}', t):
            continue
        if re.fullmatch(r'第[一二三四五六七八九十百\d]+页', t):
            continue
        out.append(t)
    return out

def find_sections(pages):
    """pages: [(page_no, [line,...])]。返回 [{pi, pname, sec, text_lines}]。
    自动排除“目录页”（页内匹配到 ≥4 个已知标题）避免误判。"""
    n_sec = len(ALL_SECTIONS)
    known = [norm(t) for _, _, t in ALL_SECTIONS]
    lookup = {known[i]: i for i in range(n_sec)}
    for alias, canon in TITLE_ALIAS.items():
        if norm(canon) in lookup:
            lookup[norm(alias)] = lookup[norm(canon)]

    def match_index(line):
        t = line.strip()
        if not t:
            return None
        cands = [t]
        # 节号前缀（如“四 红军旅伴”）只作为剥离候选；先试整行（避免误剥“四大马”的“四”）
        m = re.match(r'^([一二三四五六七八九十]+)\s*[、.．]?\s*(.+)$', t)
        if m:
            cands.append(m.group(2))
        for c in cands:
            nc = norm(c)
            if nc in lookup:
                return lookup[nc]
        for c in cands:
            nc = norm(c)
            if len(nc) >= 4:
                scores = [difflib.SequenceMatcher(None, nc, known[j]).ratio() for j in range(n_sec)]
                best = max(range(n_sec), key=lambda j: scores[j])
                if scores[best] >= 0.75:
                    return best
        return None

    # 目录页（≥4 个标题命中）
    toc_pages = set()
    for pno, plines in pages:
        if sum(1 for ln in plines if match_index(ln) is not None) >= 4:
            toc_pages.add(pno)
    print('目录页(已排除):', sorted(toc_pages))

    # 顺序行 + 边界（非目录页）
    ordered = []                     # (line, page_no, sec_idx_or_None)
    for pno, plines in pages:
        for ln in plines:
            ordered.append((ln, pno, None if pno in toc_pages else match_index(ln)))

    # 单调顺序选取每节首个边界
    next_expected = 0
    bpos = []                        # (行号, 节索引, 页号)
    for idx, (ln, pno, si) in enumerate(ordered):
        if si is None:
            continue
        if si >= next_expected:
            bpos.append((idx, si, pno))
            next_expected = si + 1
        # si < next_expected：乱序/重复，跳过

    result = []
    for k, (idx, si, pno) in enumerate(bpos):
        end = bpos[k + 1][0] if k + 1 < len(bpos) else len(ordered)
        pi, pname, sec = ALL_SECTIONS[si]
        sec = TITLE_FIX.get(sec, sec)
        result.append({'pi': pi, 'pname': pname, 'sec': sec, 'page': pno,
                       'text': [ln for ln, _, _ in ordered[idx:end]]})
    return result

def build():
    pages = load_ocr()
    print('OCR 页数:', len(pages))
    pg_list = [(pg, clean_page(raw)) for pg, raw in pages]
    secs = find_sections(pg_list)
    print('识别到节数:', len(secs), '/', len(ALL_SECTIONS))
    for s in secs:
        print('  节[%d] 页P%03d: %s' % (s['pi'], s['page'], s['sec']))
    # 汇总缺失
    found = {(s['pi'], s['sec']) for s in secs}
    missing = [(pi, pn, sn) for pi, pn, sn in ALL_SECTIONS if (pi, sn) not in found]
    if missing:
        print('未识别节:', missing)

    # —— 生成章节页 ——
    os.makedirs(BOOK_DIR, exist_ok=True)
    entries = []   # {idx, title, fname}
    toc_groups = []
    cur_pi = None
    group = None
    for k, s in enumerate(secs, 1):
        title = s['sec']
        fname = '%02d-%s.html' % (k, re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', title)[:30])
        entries.append({'idx': k, 'title': title, 'fname': fname, 'pi': s['pi'], 'pname': s['pname']})
        if s['pi'] != cur_pi:
            cur_pi = s['pi']
            group = {'label': '%s %s' % (['','第一篇','第二篇','第三篇','第四篇','第五篇','第六篇','第七篇','第八篇','第九篇','第十篇','第十一篇','第十二篇'][s['pi']], s['pname']), 'items': []}
            toc_groups.append(group)
        group['items'].append({'num': str(k), 'title': title, 'href': fname})
    if len(entries) != len(ALL_SECTIONS):
        print('警告：章节数 %d != 目录数 %d，缺失节将不生成页面' % (len(entries), len(ALL_SECTIONS)))

    for k, (s, e) in enumerate(zip(secs, entries), 1):
        paras = []
        for ln in s['text']:
            paras.append({'kind': 'p', 'html': htmllib.escape(ln)})
        prev = entries[k - 2] if k > 1 else None
        nxt = entries[k] if k < len(entries) else None
        result = {
            'title': e['title'],
            'secdate': '%s · %s' % (['','第一篇','第二篇','第三篇','第四篇','第五篇','第六篇','第七篇','第八篇','第九篇','第十篇','第十一篇','第十二篇'][s['pi']], s['pname']),
            'body': paras,
            'notes': [],
        }
        page_html = render_article(
            result, art_idx=1, brand='红星照耀中国（西行漫记）', voltag='埃德加·斯诺 著 · 董乐山 译',
            toc_groups=toc_groups, active_href=e['fname'],
            prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
            nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
            vol_href='../红星照耀中国.html',
            footer='文本经扫描 OCR 整理（埃德加·斯诺《红星照耀中国（西行漫记）》，董乐山译，三联书店 1979 年版），仅供学习研究参考；OCR 或有错漏，如与纸质版有出入，以纸质版为准。',
            home_href='../../../index.html', assets='../../../assets',
        )
        with open(os.path.join(BOOK_DIR, e['fname']), 'w', encoding='utf-8') as f:
            f.write(page_html)
    print('写入章节页:', len(entries))

    # —— 书选页（12 篇卡片） ——
    cards = []
    first_of_pian = {}
    for e in entries:
        first_of_pian.setdefault(e['pi'], e['fname'])
    pian_names = ['', '探寻红色中国', '去红都的道路', '在保安', '一个共产党员的由来', '长征', '红星在西北',
                  '去前线的路上', '同红军在一起', '同红军在一起（续）', '战争与和平', '回到保安', '又是白色世界']
    pian_no = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
    for pi in range(1, 13):
        href = first_of_pian.get(pi)
        if not href:
            continue
        n = sum(1 for e in entries if e['pi'] == pi)
        cards.append('''<a class="card" href="红星照耀中国/{href}">
  <div class="vol">第{pian}篇</div>
  <div class="ed">{n} 节</div>
  <div class="stat">{name}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(href=href, pian=pian_no[pi], n=n, name=pian_names[pi]))
    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="《红星照耀中国》（西行漫记）· 埃德加·斯诺 著">
<title>红星照耀中国（西行漫记）· 埃德加·斯诺</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 其 他 学 习 · 埃 德 加 · 斯 诺</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">红星照耀中国</h1>
    <div class="sub">西行漫记（Red Star Over China）· 董乐山 译</div>
    <div class="meta">{n} 节 · <a href="index.html">&#8678; 返回埃德加·斯诺</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    埃德加·斯诺（Edgar Snow，1905—1972）1936 年进入陕北苏区采访后所著，是第一部向世界系统报道中国共产党与红军的纪实著作。
    文本经扫描 OCR 整理（董乐山译，三联书店 1979 年版），仅供学习研究参考；OCR 或有错漏，如与纸质版有出入，以纸质版为准。
  </footer>
</div>
</body>
</html>'''.format(n=len(entries), cards='\n'.join(cards))
    with open(os.path.join(SNOW, '红星照耀中国.html'), 'w', encoding='utf-8') as f:
        f.write(landing)
    print('写入书选页')

if __name__ == '__main__':
    build()
