# -*- coding: utf-8 -*-
"""
整理毛选目录：把抓取素材/工具/备份收拢到 来源数据 文件夹，保留数据层面干净。
目标：
  教员/毛选/
  ├── 1~5/           只保留文章页
  └── 来源数据/
      ├── 卷1数据~卷5数据    （各卷原 数据 目录）
      ├── 工具               （解析/下载脚本）
      ├── 预览.png
      ├── 旧版合并页          （旧整卷大页面）
      ├── acl-recovery       （权限修复备份）
      └── backup_fix_20261009（早期修复备份）
"""
import os, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r'C:\导师文集'
MAO = os.path.join(ROOT, '教员', '毛选')
SRC = os.path.join(MAO, '来源数据')
os.makedirs(SRC, exist_ok=True)

def move(src, dst):
    if not os.path.exists(src):
        print('  skip(缺失)', src)
        return
    if os.path.exists(dst):
        shutil.rmtree(dst) if os.path.isdir(dst) else os.remove(dst)
    shutil.move(src, dst)
    print('  moved', os.path.relpath(src, MAO), '->', os.path.relpath(dst, MAO))

# 1. 各卷 数据 目录
for v in ['1', '2', '3', '4', '5']:
    d = os.path.join(MAO, v, '数据')
    if os.path.isdir(d):
        move(d, os.path.join(SRC, '卷%s数据' % v))
    # 第5卷还有 data 目录（shots）
    d2 = os.path.join(MAO, v, 'data')
    if os.path.isdir(d2):
        move(d2, os.path.join(SRC, '卷%sdata' % v))

# 2. 工具
move(os.path.join(MAO, '工具'), os.path.join(SRC, '工具'))

# 3. 预览.png
move(os.path.join(MAO, '预览.png'), os.path.join(SRC, '预览.png'))

# 4. 旧版合并页
move(os.path.join(MAO, '旧版合并页'), os.path.join(SRC, '旧版合并页'))

# 5. 毛选内 acl-recovery（如存在）
move(os.path.join(MAO, 'acl-recovery'), os.path.join(SRC, 'acl-recovery-毛选'))

# 6. 根目录 acl-recovery
move(os.path.join(ROOT, 'acl-recovery'), os.path.join(SRC, 'acl-recovery-根目录'))

# 7. 根目录 backup_fix_20261009
move(os.path.join(ROOT, 'backup_fix_20261009'), os.path.join(SRC, 'backup_fix_20261009'))

print('整理完成')
