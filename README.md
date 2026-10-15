# 导师文集 · 项目说明

> **给后续 AI / 开发者的一句话**：本项目是一个**纯静态**的中文经典著作在线阅读网站（马克思、恩格斯、列宁、斯大林、毛泽东 + 埃德加·斯诺等），无任何构建框架，全部为提交到 git 的独立 `.html` / `.css` / `.js` 文件，可整体拷贝到任何电脑离线打开。读完本文件即可开展工作，无需重新通读全站结构。

---

## 1. 这是什么

- 形式：静态 HTML 站点，`index.html` 首页 → 人物页 → 作品选卷页 → 章节阅读页，四级导航。
- 技术栈：原生 HTML5 + CSS3 + 原生 JavaScript（`assets/app.js`、`assets/style.css`），**无框架、无打包器、无后端数据库**。
- 附带能力（依赖一个极小的本地服务器）：私人批注自动保存、读者补充注释写回文章页。
- 规模：约 **2451 个 HTML 页面**；毛泽东选集 230 篇、军事文集 1612 篇、资本论 109 篇等。
- 数据来源：各著作来源不一（中文马克思主义文库镜像、mzdbl.cn、OCR 扫描件等），页面 footer 均保留来源与版权说明，勿删。

## 2. 目录结构总览

```
C:\导师文集\
├── index.html                  # 全站首页（人物卡片总入口）
├── 启动导师文集.bat            # 双击启动本地服务器并打开首页（GBK+CRLF 编码）
├── README.md                   # 本文档
├── AGENTS.md                   # AI 会话自动加载的速览（指向本文档）
├── .gitignore                  # 关键：批注/ sources/ node_modules 等不入库
│
├── assets\
│   ├── style.css               # 全站公共样式（首页/选卷页/阅读页共用）
│   └── app.js                  # 全站公共脚本（目录/顶栏/脚注/批注/补充注释）
│
├── 导师著作\                   # 五位导师（马克思/恩格斯/列宁/斯大林/教员）
│   ├── 马克思\ 恩格斯\ 列宁\ 斯大林\ 教员\
│   └── （结构见下节）
│
├── 其他著作\                   # 非导师的其他人（现仅 埃德加·斯诺）
│   └── 埃德加·斯诺\
│
├── 批注\
│   └── annotations.js          # 私人批注数据（window.__ANNOTATIONS__），已被 gitignore
│
└── .tools\                     # 本地服务器 + 构建/校验脚本 + 源素材（工具层，不入库）
    ├── server.ps1              # 本地服务器（主力，纯 PowerShell，免装 Python）
    ├── server.py               # 本地服务器（Python 等价实现，备用）
    ├── manifest.json           # 马恩列（及斯大林部分）作品构建清单
    ├── mew_convert.py          # 核心转换器：源 HTML → 阅读页 + window.PAGE
    ├── build_*.py              # 各栏目构建脚本（见第 6 节）
    ├── check_*.py / validate_*.py  # 链接/结构校验脚本
    ├── test_anno.js / test_dz.js   # jsdom 端到端测试（批注/补充注释）
    ├── sources\                # 源素材（gitignore，不入库）
    └── node_modules\           # jsdom 等测试依赖（gitignore）
```

## 3. 页面层级与链接规则

共 4 级页面，**一律使用相对路径**，注意相对深度：

| 级别 | 位置示例 | 引用 assets | 链接首页 |
|---|---|---|---|
| ① 首页 | `index.html` | `assets/` | — |
| ② 人物页 | `导师著作/列宁/index.html` | `../../assets/` | `../../index.html` |
| ③ 选卷页 | `导师著作/列宁/国家与革命.html` | `../../assets/` | `../../index.html` |
| ④ 阅读页 | `导师著作/列宁/国家与革命/01-…html` | `../../../assets/` | `../../../index.html` |

- 一个作品 = **1 个选卷页**（`导师著作/<人>/<作品>.html`，卡片列表）+ **1 个同名词目录**（`导师著作/<人>/<作品>/`，内存 `NN-<篇名>.html`）。
- 文件名规范：章节页统一 `两位序号-标题.html`（如 `01-第一章阶级社会和国家.html`）；选卷页用作品名。
- **教员（毛泽东）是特殊结构**：
  - `教员/毛选.html` → `教员/毛选/1..5/01-xxx.html`（每卷无独立选卷页，直接列文章）
  - `教员/军事文集.html` → `教员/军事文集/第X卷.html`（每卷有选卷页）→ `第X卷/01-xxx.html`
  - `教员/专题.html` → `教员/专题/实践论.html`（单页）/ `持久战.html` → `专题/持久战/01-…html` 等
- **马克思特殊**：`马克思/资本论.html` → `资本论/1|2|3/01-…html`（卷目录用数字 `1/2/3`）。
- 新增人物/作品时，把选卷页链接写对相对深度即可，无需任何路由配置。

## 4. 阅读页结构与 `window.PAGE` 数据契约（关键）

所有阅读页是同一套骨架（由 `mew_convert.render_article` 生成）：

```html
<div id="progress"></div>
<aside id="toc">… <ul id="toclist"></ul> </aside>   <!-- 侧栏目录，列表由 app.js 渲染 -->
<div id="tocMask"></div>
<button id="tocCollapseBtn">…</button>
<header id="topbar"> … </header>
<main id="main">
  <article class="chapter"> …正文… <div class="chapnav">上一篇/下一篇</div> </article>
  <footer>…来源说明…</footer>
</main>
<button id="backtop">…</button>
<script>window.PAGE = { … };</script>
<script src="…/assets/app.js"></script>
```

**`window.PAGE` 是页面向 `app.js` 传数据的唯一契约**，字段：

```js
{
  brand: '国家与革命',          // 顶栏品牌名
  voltag: '《列宁全集》第31卷',  // 顶栏版本标签
  homeHref: '../../../index.html',
  volHref: '../国家与革命.html', // “选卷”链接
  volLabel: '选卷',
  tocGroups: [                  // 目录（分组或扁平二选一）
    { label: '第一次国内革命战争时期', items: [{ num:'1', title:'…', href:'01-….html' }] }
  ],
  // 无分组时用 toc: [ {num, title, href} ]
  activeHref: '01-….html',      // 当前文章文件名（目录高亮用）
  searchPlaceholder: '搜索篇名…'
}
```

> **改页面必改 PAGE**：目录、顶栏、高亮、上一篇/下一篇全部由 `app.js` 依据 `window.PAGE` 生成，正文里不要手写目录列表。

## 5. `assets/app.js` 功能清单

单文件、IIFE、无依赖，`window.PAGE` 驱动，按 DOM 是否存在做特性探测：

- 目录渲染（`tocGroups`/`toc`）、顶栏填充、目录折叠（localStorage `dsw-toc-hidden`）。
- 滚动进度条、返回顶部、打印；移动端目录抽屉；篇名搜索过滤。
- 脚注悬浮提示（正文 `sup.fnref` → 文末 `p.note`）。
- **私人批注**（下划线 + 语句，右键菜单）：数据只存本机 `批注/annotations.js`（**gitignore**）。
  - 服务器模式（http）经 `POST /anno` 自动保存；`file://` 模式改为下载 annotations.js 手动覆盖。
  - 定位基于“主文本字符偏移”，包裹 `<u>` 不改变文本，刷新稳定。
- **读者补充注释**（`[dz.N]`，公共入库）：选中文字右键添加，标记 `sup.dzref` + 文末 `#dznotes` 区，自动重编号、可锁定只读。
  - **必须服务器模式**（`POST /page-write` 把 `<main>` 写回文章 HTML），`file://` 只读。
  - 序列化写回时会剥掉私人下划线（`u.anno`），保证隐私不外泄。

## 6. 本地服务器（`启动导师文集.bat`）

- 端口 **8790**，`http://127.0.0.1:8790/`。
- `.tools/server.ps1`（**主力**，HttpListener 纯 PowerShell，任何 Windows 免装 Python）；
  `.tools/server.py`（Python 等价实现，备用/参照）。
- 接口：
  - `GET *` — 静态托管，`Cache-Control: no-cache`（保证补充注释改动立即可见）。
  - `POST /anno` — 写入 `批注/annotations.js`。
  - `POST /page-write` — 写回阅读页 `<main>`，**含路径安全校验**（仅站点内 `.html`、禁 `..` 穿越）。
- 打开方式：双击 `启动导师文集.bat`；直接双击 `index.html`（file://）可阅读 + 私人批注（手动保存），但补充注释需服务器模式。

## 7. 构建 / 维护脚本（`.tools/`）

这些脚本用于**重建或新增内容**。`sources/` 为原始素材（gitignore）。

| 脚本 | 职责 |
|---|---|
| `mew_convert.py` | 核心：解析“马列著作网页版”风格源 HTML（`h1`/`p`/`table`/`aside` 注释块）→ `parse_article`/`render_article` 生成阅读页骨架 + `window.PAGE`。多数 build 脚本复用它。 |
| `manifest.json` + `build_works.py` | 马恩列作品构建清单与执行器（`--works 共产党宣言,反杜林论` 可指定）。 |
| `build_marx.py` | 马克思 `资本论` 三卷选卷页/导师页。 |
| `build_stalin.py` / `build_stalin2.py` | 斯大林《论辩证唯物主义和历史唯物主义》（TeX）/《论列宁主义基础》（PDF 文本）。 |
| `split_mao.py` / `organize_mao.py` | 毛选：从 `parsed.json` 拆 230 篇到 `毛选/1..5/`；整理 `来源数据/`。 |
| `build_mao_topic.py` | 毛选经典篇目专题（实践论/矛盾论/战略问题/持久战）。 |
| `build_junshi.py` | 军事文集 1612 篇（源：mzdbl.cn GBK txt）。 |
| `build_xixing.py` / `build_snow.py` | 斯诺《红星照耀中国》（OCR）/ 其余各书（`sources/snow/books.json`）。 |
| `build_volpages.py` / `build_indexes.py` | 重建选卷页 / 人物页 / 首页索引。 |
| `check_links.py` `check_all_links.py` `validate_all.py` `validate_site.py` 等 | 全站链接与结构校验（改完必跑）。 |
| `test_anno.js` / `test_dz.js` | jsdom 端到端测试（私人批注 / 补充注释）。 |

## 8. 约定与红线（务必遵守）

1. **纯静态**：不要引入框架/打包器/数据库；所有页面是独立 HTML，相对链接。
2. **链接深度**：人物/选卷页 `../../`，阅读页 `../../../`（见第 3 节表）。
3. **改阅读页先改 `window.PAGE`**，目录等由 `app.js` 生成，勿手写重复。
4. **隐私边界**：`批注/annotations.js` 是用户私人数据，**永不入库**；补充注释写回 HTML 前会剥掉私人下划线。
5. **不要提交**：`批注/`、`.tools/sources/`、`.tools/node_modules/`、各处 `来源数据/`、`.tools/package*.json`、测试临时脚本（见 `.gitignore`）。
6. **来源版权**：各页 footer 的来源/版本说明保留原样，不删除。
7. **编码**：站点 HTML/JS 为 UTF-8；`启动导师文集.bat` 必须 GBK + CRLF（否则中文 cmd 解析出错闪退）。
8. **历史已重写**：仓库历史经 filter-repo 瘦身，勿尝试还原旧大文件。
9. **二进制大文件不入库**：压缩包（`*.zip`/`*.7z`/`*.rar` 等）、PDF 源素材、可执行/镜像文件一律不提交 git（见 `.gitignore` 纪律段）。如未来做按人物打包分发，产物统一放 `.archive/`（已忽略），由脚本生成、作为分发产物，不入库；源 HTML 与构建脚本才是入库的真相。

## 9. 常见任务速查（AI 可直接照做）

- **读某一篇文章**：`导师著作/<人>/<作品>/NN-<篇名>.html`（阅读页，含 `window.PAGE` 与全文）。
- **查某个作品有哪些篇目**：看 `<作者>/<作品>.html` 选卷页，或 `<作品>/` 目录下 `NN-*.html`。
- **新增一篇/一本书**：准备源素材到 `.tools/sources/` → 复用 `render_article` 写构建脚本（或改 `manifest.json`）→ 生成选卷页与章节页 → 跑 `build_volpages.py`/`build_indexes.py` 重建导航 → `check_all_links.py` 校验零坏链 → 手动抽查 1-2 个阅读页。
- **只改样式/脚本**：改 `assets/style.css` / `assets/app.js`，全站即时生效（无缓存构建）。
- **验证全站**：`python .tools/check_all_links.py`、`python .tools/validate_all.py`。
- **启动站点**：双击 `启动导师文集.bat`（或 `powershell -File .tools\server.ps1`）。
