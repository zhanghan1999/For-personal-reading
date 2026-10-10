# -*- coding: utf-8 -*-
"""slim_repo.py — 重写 git 历史，删除仓库中的中间产物（来源数据/旧版合并页/截图/源文本）。
用法：在 C:\\导师文集 下运行 python .tools\\slim_repo.py
"""
import sys, os
sys.argv = [
    'git-filter-repo', '--force', '--invert-paths',
    '--path', '.tools/sources',
    '--path', '教员/毛选/来源数据',
    '--path', '马克思/资本论/旧版合并页',
    '--path', '马克思/.tools',
]
from git_filter_repo import main
main()
