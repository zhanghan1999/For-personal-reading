# 导师文集 · 项目说明

> **给后续 AI / 开发者的一句话**：本项目是一个**纯静态**的中文经典著作在线阅读网站（马克思、恩格斯、列宁、斯大林、毛泽东 + 埃德加·斯诺等），无任何构建框架，全部为提交到 git 的独立 `.html` / `.css` / `.js` 文件，可整体拷贝到任何电脑离线打开。读完本文件即可开展工作，无需重新通读全站结构。

---

## 1. 这是什么

- 形式：静态 HTML 站点，`index.html` 首页 → 人物页 → 作品选卷页 → 章节阅读页，四级导航。
- 技术栈：原生 HTML5 + CSS3 + 原生 JavaScript（`assets/app.js`、`assets/style.css`），**无框架、无打包器、无后端数据库**。
- 附带能力（依赖一个极小的本地服务器）：私人批注自动保存、读者补充注释写回文章页。
- 规模：约 **1.07 万个 HTML 页面 / 162 MB**；其中《马克思恩格斯全集》50 卷 6883 篇、《斯大林全集》20 卷 1146 篇、《鲁迅全集》13 个单行本 306 篇、毛泽东选集 230 篇、军事文集 1612 篇。全集目录已外置（每卷一个 `目录.js`），否则体积会翻倍。
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
│   ├── app.js                  # 全站公共脚本（目录/顶栏/脚注/批注/补充注释/阅读进度）
│   ├── read.js                 # 非正文页的阅读进度展示（卡片印章/进度条/继续阅读）
│   └── quote.js                # 非正文页的轮换引言
│
├── 导师著作\                   # 五位导师（马克思/恩格斯/列宁/斯大林/教员）
│   ├── 马克思\ 恩格斯\ 列宁\ 斯大林\ 教员\
│   ├── 马克思\马克思恩格斯全集.html              # 全集总选卷页（50 卷卡片）
│   ├── 马克思\马克思恩格斯全集\第X卷.html         # 卷选卷页
│   ├── 马克思\马克思恩格斯全集\第X卷\NN-篇名.html  # 阅读页（全集唯一正文）
│   ├── 马克思\马克思恩格斯全集\第X卷\目录.js      # 该卷侧栏目录（各页共用，勿内嵌）
│   ├── 马克思\资本论.html / 共产党宣言.html …      # 单行本「视图」页（卡片指向全集）
│   ├── 斯大林\斯大林全集.html                    # 斯大林全集总目（20 卷）
│   ├── 斯大林\斯大林全集\第X卷\NN-篇名.html       # 斯大林全集正文
│   └── （其余结构见下节）
│
├── 其他著作\                   # 非导师的其他人（现：埃德加·斯诺；规划：鲁迅）
│   ├── 埃德加·斯诺\
│   └── （鲁迅 等规划中，见第 8 节红线 10）
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
| ④′ 全集卷选卷页 | `导师著作/马克思/马克思恩格斯全集/第23卷.html` | `../../../assets/` | `../../../index.html` |
| ⑤ 全集阅读页 | `导师著作/马克思/马克思恩格斯全集/第23卷/01-…html` | `../../../../assets/` | `../../../../index.html` |

- 一个作品 = **1 个选卷页**（`导师著作/<人>/<作品>.html`，卡片列表）+ **1 个同名词目录**（`导师著作/<人>/<作品>/`，内存 `NN-<篇名>.html`）。
- 文件名规范：章节页统一 `两位序号-标题.html`（如 `01-第一章阶级社会和国家.html`）；选卷页用作品名。
- **全集结构（比普通作品多一层）**：`<全集名>.html`（卷卡片）→ `<全集名>/第X卷.html`（篇目卡片）→ `<全集名>/第X卷/NN-篇名.html`。阅读页因此是**五级深度**，assets/首页均为 `../../../../`。
- **单行本视图页**：`资本论.html`、`共产党宣言.html`、`反杜林论.html` 等不再存正文，卡片直接链到 `马克思恩格斯全集/第X卷/NN-…html`；跨导师时用 `../马克思/马克思恩格斯全集/…`。
- **教员（毛泽东）是特殊结构**：
  - `教员/毛选.html` → `教员/毛选/1..5/01-xxx.html`（每卷无独立选卷页，直接列文章）
  - `教员/军事文集.html` → `教员/军事文集/第X卷.html`（每卷有选卷页）→ `第X卷/01-xxx.html`
  - `教员/专题.html` → `教员/专题/实践论.html`（单页）/ `持久战.html` → `专题/持久战/01-…html` 等
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

### 4.1 全集页面：目录外置（`目录.js` / `window.VOL_TOC`）

全集（马恩全集、斯大林全集、鲁迅全集）**不允许把目录内嵌进每页**——那会让同一卷 100 多页各存一份目录，马恩全集因此多出 165 MB。规则：

- 每卷（或每个共用同一份目录的目录）只放一个 `目录.js`：`window.VOL_TOC = [ {label, items:[{num,title,href}]} ];`
- 阅读页 `window.PAGE` **不含 `tocGroups`**，改为在自己的 `app.js` 之前引一行：
  `<script src="目录.js"></script>`（跨目录时用相对路径，如 `../目录.js`）
- `app.js` 的取值顺序：`PAGE.tocGroups` → `window.VOL_TOC` → `PAGE.toc`
- 必须用 `<script src>`（普通脚本），**不能用 `fetch` 读 `.json`**：`file://` 下 fetch 被 CORS 拦，双击打开会丢目录；`<script src>` 不受此限，双击照常有目录。
- 生成/重建后跑 `python .tools/slim_toc.py`（幂等；`build_mew_full.py`、`build_stalin_quanji.py` 已在末尾自动调用）。

## 5. `assets/app.js` 功能清单

单文件、IIFE、无依赖，`window.PAGE` 驱动，按 DOM 是否存在做特性探测：

- 目录渲染（`tocGroups`/`toc`）、顶栏填充、目录折叠（localStorage `dsw-toc-hidden`）。
- **目录自动定位**：渲染完成后把当前篇（`a.active`）滚到侧栏可视区中部，翻篇/点目录后不用再从第一篇往下翻；目录未溢出、或当前篇本来就靠前时不滚动（不白跳）。移动端抽屉打开后同样生效。
- 滚动进度条、返回顶部、打印；移动端目录抽屉；篇名搜索过滤。
- 脚注悬浮提示（正文 `sup.fnref` → 文末 `p.note`）。**注释条目本身缺失时**（有些页面的源文本没收录该条注）显示「本页未收录这条注释」，不再是点了没反应。
- **私人批注**（下划线 + 语句，右键菜单）：数据只存本机 `批注/annotations.js`（**gitignore**）。
  - 服务器模式（http）经 `POST /anno` 自动保存；`file://` 模式改为下载 annotations.js 手动覆盖。
  - 定位基于“主文本字符偏移”，包裹 `<u>` 不改变文本，刷新稳定。
- **读者补充注释**（`[dz.N]`，公共入库）：选中文字右键添加，标记 `sup.dzref` + 文末 `#dznotes` 区，自动重编号、可锁定只读。
  - **必须服务器模式**（`POST /page-write` 把 `<main>` 写回文章 HTML），`file://` 只读。
  - 序列化写回时会剥掉私人下划线（`u.anno`），保证隐私不外泄。
- **阅读进度**（本机缓存，与批注一样不进 git）：`window.PAGE` 驱动，纯前端 `localStorage`，**不写任何文件**。
  - 存储键：`dsw-read-v1`（`{"站点相对路径(小写)": 已读时间戳}`）、`dsw-read-last`（上次阅读页，供首页「继续阅读」）。
  - **默认规则**：读阅读页时点「下一篇」，当前篇自动记为已读；顶栏 `#readBtn`（标记已读 / ✓ 已读）可手动补记或取消（末章、跳读都靠它）。
  - 阅读页：侧栏目录给已读篇打 ✓、顶部显示「已读 n / N 篇」进度条；多标签页通过 `storage` 事件同步。
  - 非正文页（`assets/read.js`）：选卷页顶部进度条 + 已读卡片盖「✓ 已读」印章、入口文案变「重读本篇 →」；卷/著作/人物卡片显示「已读 N 篇」；首页显示「继续阅读」卡片。
  - `file://` 双击与 http 服务器模式都可用（两模式键名一致）；`localStorage` 不可用时静默降级，不影响阅读。

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
| `manifest.json` + `build_works.py` | 马恩列作品构建清单与执行器（`--works 共产党宣言,反杜林论` 可指定）。标了 `"view": true` 的作品是全集视图页，构建时跳过。 |
| `build_marx.py` | 马克思 `资本论` 三卷选卷页/导师页。 |
| `build_mew_full.py` | 《马克思恩格斯全集》50 卷 6883 篇正文页 + 卷选卷页 + 总选卷页；补图、把源页内 `MEWxx-yyy.html` 链接改写为站内页、解包源站缺失的大图。 |
| `slim_toc.py` | **全集目录外置**：把各页内嵌的 `tocGroups` 抽成每卷一个 `目录.js`（`window.VOL_TOC`），幂等；`--check` 只统计。马恩全集可省 165 MB。 |
| `fix_page_scripts.py` | 修复 `slim_toc` 中断留下的坏页（补回 `</script>`、把 `目录-<hash>.js` 规范成 `目录.js`）。 |
| `build_view_works.py` | 全集视图页：把马克思/恩格斯的单行本改成指向全集的卡片页，并删除重复正文目录。 |
| `build_stalin_quanji.py` | 《斯大林全集》：文字版 PDF → 20 卷阅读页（pypdf 抽文本 + 书签切篇）；PDF/缓存/目录数据在 `sources/stalin/`。 |
| `build_stalin.py` / `build_stalin2.py` | 斯大林《论辩证唯物主义和历史唯物主义》（TeX）/《论列宁主义基础》（PDF 文本）。 |
| `split_mao.py` / `organize_mao.py` | 毛选：从 `parsed.json` 拆 230 篇到 `毛选/1..5/`；整理 `来源数据/`。 |
| `build_mao_topic.py` | 毛选经典篇目专题（实践论/矛盾论/战略问题/持久战）。 |
| `build_junshi.py` | 军事文集 1612 篇（源：mzdbl.cn GBK txt）。 |
| `build_xixing.py` / `build_snow.py` | 斯诺《红星照耀中国》（OCR）/ 其余各书（`sources/snow/books.json`）。 |
| `build_volpages.py` / `build_indexes.py` | 重建选卷页 / 人物页 / 首页索引。 |
| `inject_quote_js.py` / `inject_read_js.py` | 给所有非正文页挂 `assets/quote.js`（轮换引言）/ `assets/read.js`（阅读进度展示）。幂等；**重建导航后需重跑**。 |
| `check_links.py` `check_all_links.py` `validate_all.py` `validate_site.py` 等 | 全站链接与结构校验（改完必跑）。 |
| `check_fntip_all.py` | **脚注一致性体检**：逐页比对 `sup.fnref` 锚点与注释 id，报告坏锚点、注释条目缺 id、id 重复（按页面聚合；`--verbose` 列明细）。 |
| `fix_note_ids.py` | **补齐脚注目标 id**（幂等）：注释条目漏了 id 就会「点了没反应」，脚本从该页 fnref 锚点反推 id 前缀、按条目自带的编号补 id 并统一成 `[N]&ensp;正文`；前缀不唯一或会撞 id 时整页跳过并报告。`--check` 只报告。 |
| `fix_note_dups.py` | **修复重复 id / 断裂注释**（幂等）：把「正文交叉引用被当成新注」的碎片接回原注释（如 `…注〔7〕。` 被拆成两条）、合并被断开的续段（如 `…第４８９` + `页）。`）、删除完全重复条目；分章重新编号的页面（鲁迅）按「上标编号 → 注释编号」改写成唯一 id（`lxn-1-2` 之类）；上标锚点 id 重复的加 `-2/-3`。编号本身乱掉的页面只做 id 唯一化并列入 needs-review。`--check` 只报告。 |
| `fix_notes_in_body.py` | **把排成正文段落的注释收回注释区**（幂等）：个别军事文集篇目源文本缺「注　释」小标题，注释正文被当成普通段落排进正文（《论持久战》53 条），正文上标因此全指空。脚本只在「无注释块 + 段落编号 1..N 连续 + 彼此相邻且在尾章导航前」时动手。 |
| `restore_notes_from_source.py` | **从 `.tools/sources/mew` 原文补马恩全集注释**（幂等）：按段落命中率/标题定位源文件，只补源里确实定义了的编号（如第 47 卷 A–D 四页的 z113–z135、第 6 卷《辟谣》的 FN1），源里没有的不猜。 |
| `test_anno.js` / `test_dz.js` / `test_read.js` / `test_toc.js` / `test_note_map.js` | jsdom 端到端测试（私人批注 / 补充注释 / 阅读进度 / 脚注点开 + 目录定位 / 上标→注释映射）。 |

## 8. 约定与红线（务必遵守）

1. **纯静态**：不要引入框架/打包器/数据库；所有页面是独立 HTML，相对链接。
2. **链接深度**：人物/选卷页 `../../`，阅读页 `../../../`（见第 3 节表）。
3. **改阅读页先改 `window.PAGE`**，目录等由 `app.js` 生成，勿手写重复。
4. **隐私边界**：`批注/annotations.js` 是用户私人数据，**永不入库**；补充注释写回 HTML 前会剥掉私人下划线。
   - 阅读进度同理：只存浏览器 `localStorage`，**不写站点文件、不入库**，清缓存即清空；换浏览器/换电脑不迁移。
5. **不要提交**：`批注/`、`.tools/sources/`、`.tools/node_modules/`、各处 `来源数据/`、`.tools/package*.json`、测试临时脚本（见 `.gitignore`）。
6. **来源版权**：各页 footer 的来源/版本说明保留原样，不删除。
7. **编码**：站点 HTML/JS 为 UTF-8；`启动导师文集.bat` 必须 GBK + CRLF（否则中文 cmd 解析出错闪退）。
8. **历史已重写**：仓库历史经 filter-repo 瘦身，勿尝试还原旧大文件。
9. **二进制大文件不入库**：压缩包（`*.zip`/`*.7z`/`*.rar` 等）、PDF 源素材、可执行/镜像文件一律不提交 git（见 `.gitignore` 纪律段）。如未来做按人物打包分发，产物统一放 `.archive/`（已忽略），由脚本生成、作为分发产物，不入库；源 HTML 与构建脚本才是入库的真相。
10. **导师著作仅限五位**：`导师著作/` 只允许 马克思、恩格斯、列宁、斯大林、教员（毛泽东） 五位；其他作者（埃德加·斯诺、规划中的鲁迅等）一律归入 `其他著作/`，**不得新增导师目录**。
11. **全集通用规则（适用于任何作者）**：若某作者以"全集"形态收录，正文**唯一存放**于全集正文目录；`<全集名>.html` 选卷页按卷（或单行本）分组列出全部篇目；各单行本（如《呐喊》《资本论》）只生成指向同一批文件的"视图"选卷页，**正文零重复**。`volHref` 指向全集选卷页。
    - **非导师作者**（如鲁迅）：`其他著作/<作者>/<全集名>/<单行本>/NN-<篇名>.html`。
    - **五位导师**（如马克思、恩格斯）：`导师著作/<人>/<全集名>/第X卷/NN-<篇名>.html`，卷选卷页 `导师著作/<人>/<全集名>/第X卷.html`。全集若为两位导师共有（《马克思恩格斯全集》），正文只在**一位导师目录下存一份**（现放 `导师著作/马克思/马克思恩格斯全集/`），另一位导师的选卷页用 `../马克思/…` 相对链接指向同一批文件。
    - 先例：鲁迅 2026；马克思恩格斯全集 2026（50 卷 6883 篇，`build_mew_full.py` 建正文 + `build_view_works.py` 建视图页）；斯大林全集 2026（20 卷，`build_stalin_quanji.py`）。
12. **全集目录外置（强制）**：全集阅读页**禁止内嵌 `tocGroups`**——每卷只留一个 `目录.js`（`window.VOL_TOC`），页面在 `app.js` 前引 `<script src="目录.js">`。原因：6883 页各带一份整卷目录等于白占 165 MB。改完/重建后必须跑 `python .tools/slim_toc.py`（幂等；两大全集构建脚本已自动调用）。**不得改用 `fetch` + `.json`**：`file://` 下会被 CORS 拦死，双击打开就没目录了。详见第 4.1 节。
13. **校验脚本默认只看站点**：`check_all_links.py` 默认跳过 `.tools/`（原始素材页面的链接本就指向站外），加 `--with-tools` 才连素材一起查；它同时校验 `<script src>`，目录 js 漏拷会被它抓出来。

## 9. 常见任务速查（AI 可直接照做）

- **读某一篇文章**：`导师著作/<人>/<作品>/NN-<篇名>.html`（阅读页，含 `window.PAGE` 与全文）。
- **查某个作品有哪些篇目**：看 `<作者>/<作品>.html` 选卷页，或 `<作品>/` 目录下 `NN-*.html`。
- **新增一篇/一本书**：准备源素材到 `.tools/sources/` → 复用 `render_article` 写构建脚本（或改 `manifest.json`）→ 生成选卷页与章节页 → 跑 `build_volpages.py`/`build_indexes.py` 重建导航 → `check_all_links.py` 校验零坏链 → 手动抽查 1-2 个阅读页。
- **全集增补/重跑**：马恩全集 → `python .tools/build_mew_full.py`（可选卷号调试，末尾自动瘦身）→ `python .tools/build_view_works.py`；斯大林全集 → 改 `.tools/sources/stalin/_toc.json` 后跑 `python .tools/build_stalin_quanji.py`（同样自动瘦身）。
- **瘦身/体检**：`python .tools/slim_toc.py --check` 看还有多少内嵌目录；`python .tools/slim_toc.py` 执行外置。若 `slim_toc` 中途失败留下坏页，跑 `python .tools/fix_page_scripts.py` 修 `</script>` 并规范 `目录.js` 命名。
- **重命名/删除某篇后**：`tocGroups`/`VOL_TOC`（即 `目录.js`）与“上一篇/下一篇”都不会自动改，必须整卷重建（全集群书一律重建，不要手改单页）。
- **脚注点不开**：跑 `python .tools/check_fntip_all.py` 定位（坏锚点 / 注释条目缺 id / 注释 id 重复），再按类型修：缺 id → `python .tools/fix_note_ids.py`；id 重复、上下标编号错位、断裂注释 → `python .tools/fix_note_dups.py`；注释被排成正文 → `python .tools/fix_notes_in_body.py`；马恩全集缺条目 → `python .tools/restore_notes_from_source.py`（都幂等，先用 `--check` 看会改哪些）。剩下的坏锚点基本都是**源文本里就没有这条注**（毛选旧卷 15 页、马恩第 1/48 卷个别页等），本地素材补不出来，页面会显示「本页未收录这条注释」；要补内容只能换外部底本重做，别手写猜测。
- **只改样式/脚本**：改 `assets/style.css` / `assets/app.js` / `assets/read.js`，全站即时生效（无缓存构建）。
- **新增/重建导航页后**：跑 `python .tools/inject_read_js.py`（阅读进度展示）与 `python .tools/inject_quote_js.py`（轮换引言），两者幂等。
- **验证全站**：`python .tools/check_all_links.py`、`python .tools/validate_all.py`。
- **启动站点**：双击 `启动导师文集.bat`（或 `powershell -File .tools\server.ps1`）。
