# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def match_brace(s, pos):
    depth = 0
    i = pos
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(s) - 1

tex = open(r'C:\导师文集\.tools\sources\stalin\lun-bianzhengweiwu.tex', encoding='utf-8').read()
start = tex.index(r'\subsection[二')
end = tex.index(r'\subsection[三')
body = tex[start:end]

# 第一个 quotation 块
i = body.find(r'\begin{quotation}')
j = body.find(r'\end{quotation}', i)
qc = body[i + len(r'\begin{quotation}'):j]
print('has footnote macro in first quote:', r'\footnote' in qc)

# 测试替换逻辑
notes = []
count = [0]
out = []
k = 0
while k < len(qc):
    if qc.startswith(r'\footnote{', k):
        open_brace = k + len(r'\footnote{') - 1
        print('footnote at', k, 'open_brace char=', repr(qc[open_brace]))
        close = match_brace(qc, open_brace)
        content = qc[open_brace + 1:close]
        count[0] += 1
        notes.append(content)
        out.append('<SUPREF>')
        k = close + 1
    else:
        out.append(qc[k])
        k += 1
print('converted refs:', count[0])
print('res tail:', ''.join(out)[-200:])
