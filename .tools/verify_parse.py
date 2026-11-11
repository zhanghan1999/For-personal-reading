# -*- coding: utf-8 -*-
import sys, os, glob, json, collections
sys.path.insert(0, '.tools')
import mew_convert as mc

files = []
for pat in ('.tools/sources/mew/*/*.html', '.tools/sources/lenin/*/*.html', '.tools/sources/mea/*/*.html'):
    files.extend(glob.glob(pat))
files = [f for f in files if not f.endswith('index.html')]
print('article files:', len(files))

no_title = []
empty_body = []
notes_total = 0
for f in files:
    raw = open(f, encoding='utf-8', errors='replace').read()
    a = mc.parse_article(raw)
    if not a['title']:
        no_title.append(f)
    if not a['body']:
        empty_body.append(f)
    notes_total += len(a['notes'])

print('no title:', len(no_title), no_title[:5])
print('empty body:', len(empty_body), empty_body[:5])
print('note groups:', notes_total)
