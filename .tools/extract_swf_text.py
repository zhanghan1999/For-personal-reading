# -*- coding: utf-8 -*-
"""
《毛泽东文集》人民网 SWF(CWS) 文字提取器
用法：python extract_swf_text.py <xxx.swf> [输出.txt]
- 自动解压 CWS(FWS/ZWS)；
- 优先解析 DefineEditText/DefineText 标签（Flash 规范字符串为 UTF-8）；
- 同时做全文扫描：GBK / UTF-16LE / UTF-16BE / UTF-8 四种编码里的可读中文段；
- 顺带查找引言出处句（免得受知识分子的骗 / 读一点书）。
"""
import sys, re, zlib, lzma, struct

def load_swf(path):
    data = open(path, 'rb').read()
    sig = data[:3]
    if sig == b'FWS':
        return data
    if sig == b'CWS':
        return data[:8] + zlib.decompress(data[8:])
    if sig == b'ZWS':
        return data[:8] + lzma.decompress(data[8:])
    raise ValueError('不是 SWF: %r' % sig)

def read_rect(b, off):
    # RECT：5 字节位串
    n = b[off]
    nb = n >> 3
    bits = 5 + nb * 4
    return off + (bits + 7) // 8

def iter_tags(b):
    off = 8
    off = read_rect(b, off)
    off += 4  # frame rate(2)+frame count(2)
    while off + 2 <= len(b):
        h = struct.unpack_from('<H', b, off)[0]
        code = h >> 6
        ln = h & 0x3F
        off += 2
        if ln == 0x3F:
            ln = struct.unpack_from('<I', b, off)[0]
            off += 4
        if off + ln > len(b):
            break
        yield code, b[off:off + ln]
        off += ln

def parse_edittext(body):
    """DefineEditText (37)：提取字符串（Flash 规范为 UTF-8）"""
    outs = []
    try:
        # 前若干字段后是 1 字节字符串长度（0 表示空字符串结束）
        off = 0
        # 跳过: 字符ID(2) 边界(4*?) ... 见下
        # 简化：粗扫 UTF-8 字符串
        pass
    except Exception:
        pass
    return outs

def utf8_runs(data):
    return re.findall(rb'[\x20-\x7e\xc2-\xf4][\x80-\xbf]*(?:[\x20-\x7e\xc2-\xf4][\x80-\xbf]*){3,}', data)

def decode_run(run):
    try:
        s = run.decode('utf-8')
        if re.search(r'[\u4e00-\u9fff]', s):
            return s
    except Exception:
        pass
    return None

def gbk_runs(data):
    out = []
    cur = bytearray()
    for b in data:
        if 0x81 <= b <= 0xFE:
            cur.append(b)
        elif 0x40 <= b <= 0xFE and len(cur) % 2 == 1:
            cur.append(b)
        elif b == 0x20:
            cur.append(b)
        else:
            if len(cur) >= 4:
                s = bytes(cur).decode('gbk', 'ignore')
                if re.search(r'[\u4e00-\u9fff]', s):
                    out.append(s)
            cur = bytearray()
    return out

def main():
    path = sys.argv[1]
    swf = load_swf(path)
    print('SWF 解压后字节数:', len(swf))
    # 1) 标签级提取（UTF-8 字符串）
    found = []
    for code, body in iter_tags(swf):
        if code in (11, 33, 37):  # DefineText / DefineText2 / DefineEditText
            for run in utf8_runs(body):
                s = decode_run(run)
                if s:
                    found.append(s)
    print('标签级 UTF-8 文本段:', len(found))
    # 2) 全文件编码扫描
    gbk = gbk_runs(swf)
    utf16 = []
    for enc in ('utf-16-le', 'utf-16-be'):
        try:
            s = swf.decode(enc, 'ignore')
            for m in re.finditer(r'[\u4e00-\u9fff][\u4e00-\u9fff\u3000-\u303f\uff00-\uffef，。；：、！？（）“”《》、A-Za-z0-9 ]{4,}', s):
                utf16.append(m.group(0))
        except Exception:
            pass
    print('GBK 段:', len(gbk), ' UTF-16 段:', len(utf16))
    # 3) 引言出处
    for key in ('免得受知识分子的骗', '读一点书'):
        for name, coll in (('utf8', found), ('gbk', gbk), ('utf16', utf16)):
            for s in coll:
                if key in s:
                    i = s.find(key)
                    print('★ 命中', name, key, '=>', s[max(0, i - 40): i + 60])
    # 4) 写盘
    if len(sys.argv) > 2:
        out = []
        out += ['[UTF8-TAGS]'] + found
        out += ['[GBK]'] + gbk
        out += ['[UTF16]'] + utf16
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write('\n'.join(out))
        print('已写出:', sys.argv[2])

if __name__ == '__main__':
    main()
