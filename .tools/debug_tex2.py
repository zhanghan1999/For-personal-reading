# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r'C:\导师文集\.tools')
import build_stalin as bs

tex = open(r'C:\导师文集\.tools\sources\stalin\lun-bianzhengweiwu.tex', encoding='utf-8').read()
title, body = bs.extract_section(tex)
# 只测 take_notes 对一个 quote 的处理
i = body.find(r'\begin{quotation}')
j = body.find(r'\end{quotation}', i)
qc = body[i + len(r'\begin{quotation}'):j]
res = bs.take_notes(qc)
print('take_notes has ref:', '<sup class="fnref"' in res)
# 再测 convert_inline
res2 = bs.convert_inline(res)
print('after convert_inline has ref:', '<sup class="fnref"' in res2)
print('tail:', res2[-160:])
# 统计 convert() 整体
blocks, notes = bs.convert(body)
kinds = {}
for b in blocks:
    kinds[b['kind']] = kinds.get(b['kind'], 0) + 1
print('kinds:', kinds, 'notes:', len(notes))
# 检查第一个 quote block 是否含 fnref
for b in blocks:
    if b['kind'] == 'quote':
        print('quote block has fnref:', 'class="fnref"' in b['html'], '| head:', b['html'][:80])
        break
