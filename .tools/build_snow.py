# -*- coding: utf-8 -*-
"""build_snow.py — 把斯诺各书的中文全文（.tools/sources/snow/<书>/ 下的文本/HTML）
转换为「导师文集」斯诺栏目页面：章节页 + 书选页 + 更新人物 index.html。
格式与 build_xixing.py（西行漫记）一致，复用 mew_convert.render_article。

用法：python build_snow.py [书key...]   （不带参数 = 构建 books.json 里全部书）
配置：.tools/sources/snow/books.json
"""
import os, re, sys, io, json, html as htmllib
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mew_convert import render_article

ROOT = r'C:\导师文集'
SNOW = os.path.join(ROOT, '其他著作', '埃德加·斯诺')
SRC = os.path.join(ROOT, '.tools', 'sources', 'snow')
CONFIG = os.path.join(SRC, 'books.json')

PIAN_NO = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二',
           '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']


def load_books():
    with open(CONFIG, encoding='utf-8') as f:
        return json.load(f)


def read_source_files(src_dir):
    """读取 src_dir 下所有章节源文件，按文件名自然排序。
    仅读取符合章节命名约定（NN-xxx.txt / NN-xxx.html）的文件，避免目录内
    检索记录/杂项 HTML 被误当章节。"""
    if not os.path.isdir(src_dir):
        return []
    names = []
    for fn in os.listdir(src_dir):
        if re.match(r'^\d{1,3}-.+\.(txt|html?)$', fn, re.I) and not fn.startswith('.'):
            names.append(fn)
    names.sort(key=lambda s: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)])
    files = []
    for fn in names:
        fp = os.path.join(src_dir, fn)
        with open(fp, encoding='utf-8', errors='replace') as f:
            raw = f.read()
        if fn.lower().endswith(('.html', '.htm')):
            blocks = parse_html_body(raw)
        else:
            blocks = parse_txt_blocks(raw)
        files.append({'file': fn, 'blocks': blocks})
    return files


def parse_html_body(raw):
    """从 HTML 提取正文块 [{kind, text}]。kind: h1-h4/p/quote。"""
    m = re.search(r'<body[^>]*>(.*?)</body>', raw, flags=re.S)
    inner = m.group(1) if m else raw
    out = []
    for mm in re.finditer(r'<(h1|h2|h3|h4|p|blockquote)([^>]*)>(.*?)</\1>', inner, flags=re.S):
        tag, content = mm.group(1), mm.group(3)
        content = re.sub(r'<[^>]+>', '', content)
        content = content.replace('\r', '').replace('\n', '').strip()
        content = re.sub(r'[ \t\u3000]+', '', content)
        if not content:
            continue
        kind = tag if tag.startswith('h') else ('quote' if tag == 'blockquote' else 'p')
        out.append({'kind': kind, 'text': content})
    return out


def parse_txt_blocks(raw):
    """纯文本 → 段落。以空行/行首缩进断段；无空行时按句末标点断段。"""
    END_RE = re.compile(r'[。！？…]["”\'）)」』】}\]]*$')
    lines = [ln.strip() for ln in raw.splitlines()]
    # 去掉页眉页脚噪声
    cleaned = []
    for ln in lines:
        if not ln:
            cleaned.append('')
            continue
        if re.fullmatch(r'\d{1,4}', ln):
            continue
        if re.fullmatch(r'[-\u2014·．.~～]{1,8}\s*\d{1,4}\s*[-\u2014·．.~～]{1,8}', ln):
            continue
        if re.fullmatch(r'第[一二三四五六七八九十百\d]+页', ln):
            continue
        cleaned.append(ln)
    out = []
    cur = []
    for ln in cleaned:
        if not ln:
            if cur:
                out.append({'kind': 'p', 'text': ''.join(cur)})
                cur = []
            continue
        cur.append(ln)
        if END_RE.search(ln):
            out.append({'kind': 'p', 'text': ''.join(cur)})
            cur = []
    if cur:
        out.append({'kind': 'p', 'text': ''.join(cur)})
    return out


def strip_dup_title(blocks, title):
    """去掉章节正文开头与标题重复的行。"""
    if not blocks:
        return blocks
    head = blocks[0]
    t = head['text']
    if t == title:
        return blocks[1:]
    if t.startswith(title):
        rest = t[len(title):]
        return [{'kind': head['kind'], 'text': rest}] + blocks[1:] if rest.strip() else blocks[1:]
    return blocks


def build_placeholder(cfg):
    """无源文本时的『书目占位页』：只生成书选页（卡片 + 已核实版本信息），不生成章节页。"""
    key = cfg['key']
    brand = cfg.get('brand', key)
    footer = cfg.get('footer', '书目占位：暂未取得正文全文。')
    stat = cfg.get('stat', '')
    card_inner = '''<div class="card placeholder">
  <div class="vol">书目占位</div>
  <div class="ed">暂缺全文</div>
  <div class="stat">已核实版本信息：{stat}<br>尚未取得电子版正文，章节页待文本入库后补齐。</div>
</div>'''.format(stat=stat or '见页面脚注')
    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 其 他 学 习 · 埃 德 加 · 斯 诺</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">{name}</h1>
    <div class="sub">{subtitle}</div>
    <div class="meta">书目占位 · 暂缺全文 · <a href="index.html">&#8678; 返回埃德加·斯诺</a></div>
  </header>
  <main class="cards">
{card}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>'''.format(desc=cfg.get('desc', brand), title='%s · 埃德加·斯诺' % brand,
                name=brand, subtitle=cfg.get('subtitle', '埃德加·斯诺 著'),
                card=card_inner, footer=footer)
    with open(os.path.join(SNOW, '%s.html' % key), 'w', encoding='utf-8') as f:
        f.write(landing)
    print('  写入书目占位页: %s.html' % key)
    return {'key': key, 'brand': brand, 'n': 0, 'subtitle': cfg.get('subtitle', ''),
            'stat': '暂缺全文 · 书目占位'}


def build_book(cfg):
    key = cfg['key']
    print('==== 构建《%s》 ====' % key)
    src_dir = os.path.join(SRC, key)
    files = read_source_files(src_dir)
    if not files:
        return build_placeholder(cfg)

    # 章节清单：优先用配置的 chapters；否则按源文件个数
    chapters = cfg.get('chapters') or [os.path.splitext(f['file'])[0] for f in files]
    if len(chapters) != len(files):
        print('  警告: chapters(%d) != 源文件数(%d)' % (len(chapters), len(files)))

    book_dir = os.path.join(SNOW, key)
    os.makedirs(book_dir, exist_ok=True)

    entries = []
    for i, (f, chap) in enumerate(zip(files, chapters), 1):
        title = chap
        fname = '%02d-%s.html' % (i, re.sub(r'[\\/:*?"<>|\n\r\t 　]+', '', title)[:30])
        blocks = strip_dup_title(f['blocks'], title)
        body = []
        for b in blocks:
            if b['kind'] in ('h1', 'h2', 'h3'):
                body.append({'kind': 'h3', 'html': htmllib.escape(b['text'])})
            elif b['kind'] == 'h4':
                body.append({'kind': 'h4', 'html': htmllib.escape(b['text'])})
            elif b['kind'] == 'quote':
                body.append({'kind': 'quote', 'html': htmllib.escape(b['text'])})
            else:
                body.append({'kind': 'p', 'html': htmllib.escape(b['text'])})
        entries.append({'idx': i, 'title': title, 'fname': fname})

    # 目录分组（toc_groups）：按配置 grouping；否则平铺
    grouping = cfg.get('grouping')
    toc_groups = []
    if grouping:
        for g in grouping:
            items = [{'num': str(entries[i - 1]['idx']), 'title': entries[i - 1]['title'],
                      'href': entries[i - 1]['fname']} for i in g['items']]
            toc_groups.append({'label': g['label'], 'items': items})
    else:
        toc_groups = [{'label': None, 'items': [
            {'num': str(e['idx']), 'title': e['title'], 'href': e['fname']} for e in entries]}]

    voltag = cfg.get('voltag', '埃德加·斯诺 著')
    brand = cfg.get('brand', key)
    footer = cfg.get('footer', '文本整理自公开电子资料，仅供学习研究参考；如与纸质版有出入，以纸质版为准。')

    # —— 章节页 ——
    for k, e in enumerate(entries):
        prev = entries[k - 1] if k > 0 else None
        nxt = entries[k + 1] if k + 1 < len(entries) else None
        body_blocks = []
        for b in files[k]['blocks']:
            if b['kind'] in ('h1', 'h2', 'h3'):
                body_blocks.append({'kind': 'h3', 'html': htmllib.escape(b['text'])})
            elif b['kind'] == 'h4':
                body_blocks.append({'kind': 'h4', 'html': htmllib.escape(b['text'])})
            elif b['kind'] == 'quote':
                body_blocks.append({'kind': 'quote', 'html': htmllib.escape(b['text'])})
            else:
                body_blocks.append({'kind': 'p', 'html': htmllib.escape(b['text'])})
        result = {'title': e['title'], 'secdate': cfg.get('secdate', ''), 'body': body_blocks, 'notes': []}
        page_html = render_article(
            result, art_idx=1, brand=brand, voltag=voltag,
            toc_groups=toc_groups, active_href=e['fname'],
            prev={'href': prev['fname'], 'title': prev['title']} if prev else None,
            nxt={'href': nxt['fname'], 'title': nxt['title']} if nxt else None,
            vol_href='../%s.html' % key,
            footer=footer,
            home_href='../../../index.html', assets='../../../assets',
        )
        with open(os.path.join(book_dir, e['fname']), 'w', encoding='utf-8') as f:
            f.write(page_html)
    print('  写入章节页:', len(entries))

    # —— 书选页卡片 ——
    cards = []
    if grouping:
        for g in grouping:
            first = g['items'][0]
            cards.append('''<a class="card" href="{key}/{href}">
  <div class="vol">{label}</div>
  <div class="ed">{n} 节</div>
  <div class="stat">{name}</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(key=key, href=entries[first - 1]['fname'], label=g['label'],
               n=len(g['items']), name=g.get('name', '')))
    else:
        for e in entries:
            cards.append('''<a class="card" href="{key}/{href}">
  <div class="vol">{title}</div>
  <div class="ed">第 {idx} 章</div>
  <div class="go">打开阅读 &#8594;</div>
</a>'''.format(key=key, href=e['fname'], title=e['title'], idx=e['idx']))

    landing = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="hub">
  <header class="hero">
    <div class="kicker">导 师 文 集 · 其 他 学 习 · 埃 德 加 · 斯 诺</div>
    <div class="rule"><span class="star">&#9733;</span></div>
    <h1 class="fullname">{name}</h1>
    <div class="sub">{subtitle}</div>
    <div class="meta">{n} 节 · <a href="index.html">&#8678; 返回埃德加·斯诺</a></div>
  </header>
  <main class="cards">
{cards}
  </main>
  <footer>
    {footer}
  </footer>
</div>
</body>
</html>'''.format(desc=cfg.get('desc', brand), title='%s · 埃德加·斯诺' % brand,
                name=brand, subtitle=cfg.get('subtitle', '埃德加·斯诺 著'),
                n=len(entries), cards='\n'.join(cards), footer=footer)
    with open(os.path.join(SNOW, '%s.html' % key), 'w', encoding='utf-8') as f:
        f.write(landing)
    print('  写入书选页: %s.html' % key)
    return {'key': key, 'brand': brand, 'n': len(entries), 'subtitle': cfg.get('subtitle', ''),
            'stat': cfg.get('stat', '')}


def update_index(books_done):
    """把新书卡片写进 埃德加·斯诺/index.html 的人物页。"""
    fp = os.path.join(SNOW, 'index.html')
    with open(fp, encoding='utf-8') as f:
        html = f.read()
    # 找到 <main class="cards"> ... </main> 段
    m = re.search(r'(<main class="cards">)(.*?)(</main>)', html, flags=re.S)
    if not m:
        print('  index.html 结构异常，跳过更新')
        return
    inner = m.group(2)
    # 保留未被本次重建覆盖的既有卡片（如《红星照耀中国》）
    rebuilt_keys = {b['key'] for b in books_done}
    kept = []
    for cm in re.finditer(r'<a class="card" href="([^"]+\.html)"[\s\S]*?</a>', inner):
        href = cm.group(1)
        base = href[:-5]
        if base not in rebuilt_keys:
            kept.append(cm.group(0))
    new_cards = '\n'.join(kept) + ('\n' if kept else '')
    for b in books_done:
        key = b['key']
        stat = b.get('stat') or ('%d 节' % b['n'])
        new_cards += '''<a class="card" href="{key}.html">
  <div class="vol">{brand}</div>
  <div class="stat">{stat}</div>
  <div class="go">进入阅读 &#8594;</div>
</a>
'''.format(key=key, brand=b['brand'], stat=stat)
    html = html[:m.start(2)] + new_cards + html[m.end(2):]
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(html)
    print('  已更新人物 index.html，新增卡片:', [b['key'] for b in books_done])


def main():
    only = sys.argv[1:]
    books = load_books()
    done = []
    for cfg in books:
        if only and cfg['key'] not in only:
            continue
        r = build_book(cfg)
        if r:
            done.append(r)
    if done:
        update_index(done)


if __name__ == '__main__':
    main()
