/* ============================================================
   导师文集 · 公共脚本 (assets/app.js)
   依赖：页面中定义 window.PAGE 数据对象
   PAGE = {
     brand: '毛泽东选集 · 第一卷',        // 顶栏品牌
     voltag: '1952年版',                   // 顶栏版本标签
     homeHref: '../index.html',            // 首页（导师列表）
     volHref: '../毛选.html',              // 选卷页
     volLabel: '选卷',
     tocTitle: '目　录',
     tocGroups: [                          // 目录分组（可选，无则用 toc 扁平）
       { label: '第一次国内革命战争时期', items: [ {num:'1', title:'...', href:'...'} ] }
     ],
     toc: [ {num:'1', title:'...', href:'...'} ],   // 无分组时用
     activeHref: '01.html',                // 当前文章文件名（用于高亮）
     searchPlaceholder: '搜索篇名…'
   }
   页面骨架由各页 HTML 提供：#toc ul#toclist + #topbar + #main
   ============================================================ */
(function () {
  var PAGE = window.PAGE || {};

  // ---------- 目录生成 ----------
  var tocList = document.getElementById('toclist');
  if (tocList) {
    // 全集类页面：目录由同目录的 目录.js 提供（window.VOL_TOC），页面内不再内嵌，避免每页重复
    var groups = PAGE.tocGroups || [];
    if (!groups.length && window.VOL_TOC && window.VOL_TOC.length) {
      groups = window.VOL_TOC;
    }
    if (!groups.length && PAGE.toc && PAGE.toc.length) {
      groups = [{ label: null, items: PAGE.toc }];
    }
    var html = '';
    groups.forEach(function (g) {
      if (g.label) html += '<li class="toc-group">' + g.label + '</li>';
      g.items.forEach(function (it) {
        var active = it.href === PAGE.activeHref ? ' class="active"' : '';
        html += '<li><a' + active + ' href="' + it.href + '" data-title="' + it.title + '">' +
                '<span class="num">' + (it.num || '') + '</span> ' + it.title + '</a></li>';
      });
    });
    tocList.innerHTML = html;
  }

  // ---------- 顶栏 ----------
  var topbar = document.getElementById('topbar');
  if (topbar && PAGE.brand) {
    var brandEl = topbar.querySelector('.brand');
    if (brandEl) brandEl.textContent = PAGE.brand;
    var voltagEl = topbar.querySelector('.voltag');
    if (voltagEl && PAGE.voltag) voltagEl.textContent = PAGE.voltag;
    var homeLink = topbar.querySelector('a.home');
    if (homeLink && PAGE.homeHref) homeLink.href = PAGE.homeHref;
    var volLink = topbar.querySelector('a.vol');
    if (volLink && PAGE.volHref) {
      volLink.href = PAGE.volHref;
      if (PAGE.volLabel) volLink.textContent = PAGE.volLabel;
    }
  }

  // ---------- 目录折叠（◀ 收起 / ▶ 展开） ----------
  var toc = document.getElementById('toc');
  var body = document.body;
  var collapseBtn = document.getElementById('tocCollapseBtn');

  function setTocHidden(hidden) {
    if (hidden) {
      body.classList.add('toc-hidden');
      collapseBtn.innerHTML = '&#9654;';
      collapseBtn.title = '展开目录';
    } else {
      body.classList.remove('toc-hidden');
      collapseBtn.innerHTML = '&#9664;';
      collapseBtn.title = '收起目录';
    }
    try { localStorage.setItem('dsw-toc-hidden', hidden ? '1' : '0'); } catch (e) {}
  }
  if (collapseBtn) {
    collapseBtn.addEventListener('click', function () {
      setTocHidden(!body.classList.contains('toc-hidden'));
    });
    // 记住上次状态（默认展开）
    var saved = null;
    try { saved = localStorage.getItem('dsw-toc-hidden'); } catch (e) {}
    if (saved === '1' && window.innerWidth > 900) setTocHidden(true);
  }

  // ---------- 目录定位：把「当前篇」放到侧栏中间 ----------
  // 每次翻篇/点目录都是整页刷新（纯静态站点），目录滚动位置不会自己保留；
  // 这里在渲染完成后把高亮项滚到可视区中部，避免每次都从第一篇开始翻找。
  // 目录未超出可视高度、或当前篇已在前几篇时（目标位置为负）保持不动，不会白跳一下。
  function centerActiveToc() {
    if (!toc || !tocList) return;
    var active = tocList.querySelector('a.active');
    if (!active) return;
    var max = toc.scrollHeight - toc.clientHeight;
    if (max <= 0) return;
    var r = active.getBoundingClientRect();
    var b = toc.getBoundingClientRect();
    var target = toc.scrollTop + (r.top - b.top) - (toc.clientHeight / 2 - r.height / 2);
    toc.scrollTop = Math.max(0, Math.min(max, target));
  }
  function centerActiveTocSoon() {
    if (window.requestAnimationFrame) window.requestAnimationFrame(centerActiveToc);
    else setTimeout(centerActiveToc, 0);
  }
  centerActiveTocSoon();   // 等目录下方的「阅读进度」条插入后再定位，避免相差一条高度
  // 从 bfcache 返回（后退/前进）时浏览器会恢复页面状态，再校正一次
  window.addEventListener('pageshow', function (ev) {
    if (ev.persisted) centerActiveTocSoon();
  });

  // ---------- 进度条 / 返回顶部 / 打印 ----------
  var progress = document.getElementById('progress');
  var backtop = document.getElementById('backtop');
  function onScroll() {
    var h = document.documentElement;
    var max = (h.scrollHeight - h.clientHeight) || 1;
    var p = Math.min(100, (h.scrollTop / max) * 100);
    if (progress) progress.style.width = p + '%';
    if (backtop) backtop.style.display = h.scrollTop > 600 ? 'block' : 'none';
  }
  window.addEventListener('scroll', onScroll, {passive: true});
  onScroll();
  if (backtop) backtop.addEventListener('click', function () {
    window.scrollTo({top: 0, behavior: 'smooth'});
  });
  var printBtn = document.getElementById('printBtn');
  if (printBtn) printBtn.addEventListener('click', function () { window.print(); });

  // ---------- 移动端目录开关 ----------
  var mask = document.getElementById('tocMask');
  var menuBtn = document.getElementById('menuBtn');
  function closeToc() {
    if (toc) toc.classList.remove('open');
    if (mask) mask.classList.remove('open');
  }
  if (menuBtn) menuBtn.addEventListener('click', function () {
    if (toc) toc.classList.add('open');
    if (mask) mask.classList.add('open');
  });
  if (mask) mask.addEventListener('click', closeToc);
  if (toc) toc.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', closeToc);
  });

  // ---------- 搜索过滤 ----------
  var box = document.getElementById('q');
  if (box && tocList) {
    box.addEventListener('input', function () {
      var q = box.value.trim();
      tocList.querySelectorAll('li').forEach(function (li) {
        var a = li.querySelector('a');
        if (!a) { li.style.display = q ? 'none' : ''; return; }
        var hit = !q || a.getAttribute('data-title').indexOf(q) !== -1;
        li.style.display = hit ? '' : 'none';
      });
    });
  }

  // ---------- 脚注弹窗 ----------
  var fntip = document.createElement('div');
  fntip.className = 'fntip';
  document.body.appendChild(fntip);
  function showFntip(link) {
    var href = link.getAttribute('href') || '';
    var noteEl = href.charAt(0) === '#' ? document.getElementById(href.slice(1)) : null;
    // 少数页面源文件里注释条目本身就缺（扫描件未收录），给一句明确提示，避免“点了没反应”
    fntip.textContent = noteEl
        ? noteEl.textContent.replace(/^[\[\]()a-zA-Z0-9]+\s*/, '')
        : '本页未收录这条注释（原始文本此处缺注）。';
    fntip.style.display = 'block';
    var rect = link.getBoundingClientRect();
    var w = Math.min(340, window.innerWidth - 24);
    fntip.style.width = w + 'px';
    var left = Math.min(rect.left, window.innerWidth - w - 12);
    left = Math.max(12, left);
    fntip.style.left = left + 'px';
    var top = rect.bottom + 8;
    fntip.style.top = top + 'px';
    var h = fntip.offsetHeight;
    if (top + h > window.innerHeight - 12) {
      top = Math.max(12, rect.top - h - 8);
      fntip.style.top = top + 'px';
    }
    fntip._ref = link;
  }
  function hideFntip() {
    fntip.style.display = 'none';
    fntip._ref = null;
  }
  document.addEventListener('click', function (ev) {
    var sup = ev.target.closest ? ev.target.closest('sup.fnref') : null;
    if (sup) {
      var link = sup.querySelector('a');
      if (link) {
        ev.preventDefault();
        if (fntip._ref === link) { hideFntip(); return; }
        showFntip(link);
        return;
      }
    }
    if (fntip._ref && !fntip.contains(ev.target)) hideFntip();
  });
  window.addEventListener('scroll', function () { if (fntip._ref) hideFntip(); }, { passive: true });
  window.addEventListener('resize', function () { if (fntip._ref) hideFntip(); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') hideFntip(); });
})();

/* ============================================================
   阅读进度（本地缓存）—— 数据只存本机浏览器 localStorage，不进 git
   存储：dsw-read-v1   { "站点相对路径(小写)": 已读时间戳 }
         dsw-read-last { page, title, brand, t } 供首页「继续阅读」
   规则：① 点「下一篇」自动把当前章节记为已读（默认规则）
         ② 顶栏「标记已读」按钮可手动标记 / 取消（末章等场景）
         ③ 侧栏目录给已读章节打 ✓，并显示整卷进度
   file:// 双击与 http 服务器模式均可用，两种模式键名一致。
   首页 / 选卷页的展示由 assets/read.js 完成，共用同一份存储。
   ============================================================ */
(function () {
  if (!window.PAGE || !document.getElementById('main')) return;   // 仅阅读页生效

  var KEY = 'dsw-read-v1';
  var LAST_KEY = 'dsw-read-last';

  /* ---- 站点根与页面标识：与批注相同的推导方式，file:// 亦可用 ----
   * 注意：必须在脚本执行期立即缓存 currentScript（事件回调里它是 null） */
  var ROOT_DIR = (function () {
    var cur = document.currentScript;
    if (!cur || !cur.src) return '';
    var p = cur.src.split('/'); p.pop(); p.pop();   // 去掉 app.js 与 assets
    return p.join('/');
  })();
  var ROOT_PATH = ROOT_DIR.replace(/^[a-z][a-z0-9+.-]*:\/\//i, '');
  function rootRel(pathname) {
    var path = decodeURIComponent(pathname || '').replace(/\\/g, '/');
    if (ROOT_PATH) {
      if (path.indexOf('/' + ROOT_PATH + '/') === 0) return path.slice(ROOT_PATH.length + 2);
      if (path.indexOf(ROOT_PATH + '/') === 0) return path.slice(ROOT_PATH.length + 1);
    }
    return path.replace(/^\/+/, '');
  }
  function keyForHref(href) {
    if (!href || /^(?:[a-z][a-z0-9+.-]*:)?\/\//i.test(href) || href.charAt(0) === '#') return '';
    try {
      var u = new URL(href, window.location.href);
      if (u.protocol !== window.location.protocol) return '';
      if (/^https?:$/.test(u.protocol) && u.host !== window.location.host) return '';
      return rootRel(u.pathname).toLowerCase();
    } catch (e) { return ''; }
  }

  var THIS_PAGE = rootRel(window.location.pathname);
  var THIS_KEY = THIS_PAGE.toLowerCase();

  /* ---- 读写（localStorage 不可用时退化为会话内内存态） ---- */
  function loadMap() {
    try {
      var m = JSON.parse(localStorage.getItem(KEY) || '{}');
      if (m && typeof m === 'object' && !Array.isArray(m)) return m;
    } catch (e) {}
    return {};
  }
  var MAP = loadMap();
  function saveMap() {
    try { localStorage.setItem(KEY, JSON.stringify(MAP)); } catch (e) {}
  }
  function currentTitle() {
    var groups = PAGE.tocGroups || window.VOL_TOC || (PAGE.toc ? [{ items: PAGE.toc }] : []);
    for (var i = 0; i < groups.length; i++) {
      var items = groups[i].items || [];
      for (var j = 0; j < items.length; j++) {
        if (items[j].href === PAGE.activeHref) return items[j].title;
      }
    }
    return (document.title || '').split(' · ')[0] || THIS_PAGE;
  }
  function saveLast() {
    try {
      localStorage.setItem(LAST_KEY, JSON.stringify({
        page: THIS_PAGE, title: currentTitle(), brand: PAGE.brand || '', t: Date.now()
      }));
    } catch (e) {}
  }
  function isRead() { return !!MAP[THIS_KEY]; }
  function markRead() {
    MAP[THIS_KEY] = Date.now();
    saveMap(); saveLast(); paint();
  }
  function unmarkRead() {
    delete MAP[THIS_KEY];
    saveMap(); paint();
  }

  /* ---- 顶栏「标记已读」按钮 ---- */
  var topbar = document.getElementById('topbar');
  var btn = null;
  if (topbar) {
    btn = document.createElement('button');
    btn.id = 'readBtn';
    btn.type = 'button';
    var printBtn = document.getElementById('printBtn');
    if (printBtn) topbar.insertBefore(btn, printBtn);
    else topbar.appendChild(btn);
    btn.addEventListener('click', function () {
      if (isRead()) { unmarkRead(); toast('已取消本篇的已读标记。'); }
      else { markRead(); toast('已记下阅读进度：本篇标记为已读（只存本机浏览器）。'); }
    });
  }

  /* ---- 侧栏目录：✓ 标记 + 整卷进度 ---- */
  var tocList = document.getElementById('toclist');
  var sumText = null, sumBar = null;
  if (tocList && tocList.parentNode) {
    var summary = document.createElement('div');
    summary.className = 'read-progress';
    summary.innerHTML = '<div class="rp-text"><span>阅读进度</span><b></b></div>'
                      + '<div class="rp-bar"><i></i></div>';
    sumText = summary.querySelector('.rp-text b');
    sumBar = summary.querySelector('.rp-bar i');
    tocList.parentNode.insertBefore(summary, tocList);
  }
  function paint() {
    if (btn) {
      var read = isRead();
      btn.textContent = read ? '✓ 已读' : '标记已读';
      btn.classList.toggle('on', read);
      btn.title = read
          ? '本篇已记为已读（记录只存本机浏览器，不上传）。\n点击可取消标记。'
          : '把本篇记为已读（记录只存本机浏览器，不上传）。\n默认规则：点「下一篇」时自动把本篇记为已读。';
    }
    if (!tocList) return;
    var total = 0, done = 0;
    tocList.querySelectorAll('a').forEach(function (a) {
      total++;
      var read = !!MAP[keyForHref(a.getAttribute('href'))];
      if (read) done++;
      a.classList.toggle('read', read);
      var mark = a.querySelector('.readmark');
      if (read && !mark) {
        mark = document.createElement('span');
        mark.className = 'readmark';
        mark.textContent = '✓';
        a.appendChild(mark);
      } else if (!read && mark) {
        mark.parentNode.removeChild(mark);
      }
    });
    if (sumText) {
      sumText.textContent = '已读 ' + done + ' / ' + total + ' 篇' + (total > 0 && done === total ? ' · 读毕' : '');
      sumBar.style.width = (total ? Math.round(done * 100 / total) : 0) + '%';
    }
  }

  /* ---- 默认规则：点「下一篇」= 当前章节已读 ---- */
  var nextLink = null;
  document.querySelectorAll('.chapnav a').forEach(function (a) {
    var lbl = a.querySelector('.lbl');
    if (lbl && lbl.textContent.indexOf('下一篇') !== -1) nextLink = a;
  });
  if (nextLink) {
    nextLink.addEventListener('click', function () {
      // localStorage 同步写入，先于跳转完成；Ctrl+点击开新标签时也照常记录并刷新本页
      markRead();
    });
  }

  /* ---- 多标签页同步 ---- */
  window.addEventListener('storage', function (ev) {
    if (ev.key === KEY || ev.key === LAST_KEY || ev.key === null) { MAP = loadMap(); paint(); }
  });

  /* ---- 轻提示 ---- */
  var toastEl = null;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'read-toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.style.display = 'block';
    clearTimeout(toastEl._t);
    toastEl._t = setTimeout(function () { toastEl.style.display = 'none'; }, 3500);
  }

  saveLast();   // 记录「上次读到哪」供首页继续阅读（打开即记，不算已读）
  paint();
})();

/* ============================================================
   本地批注（下划线 + 语句）—— 数据只存本机，不进 git
   存储：<站点根>/批注/annotations.js
        （script 标签动态加载，file:// 下也无跨域限制）
   用法：选中文字 → 右键 → “添加下划线并批注”
         右键点已有下划线 → 编辑 / 删除
         右下角浮动按钮 → 生成批注文件（保存到 批注/annotations.js）
   ============================================================ */
(function () {
  if (!window.PAGE || !document.getElementById('main')) return;   // 仅阅读页生效

  var ALL = [];            // 全站批注
  var dirty = false;

  /* ---- 站点根与页面标识：由 app.js 自身 URL 推导，file:// 亦可用 ---- */
  function siteRootDir() {
    var cur = document.currentScript;
    if (!cur || !cur.src) return '';
    var p = cur.src.split('/'); p.pop(); p.pop();   // 去掉 app.js 与 assets
    return p.join('/');
  }
  function siteRootPath() {
    return siteRootDir().replace(/^[a-z][a-z0-9+.-]*:\/\//i, '');
  }
  function pageSiteRel() {
    var path = (window.location.pathname || '').replace(/\\/g, '/');
    var rp = siteRootPath();
    if (rp && path.indexOf(rp) === 0) {
      return path.slice(rp.length).replace(/^\/+/, '');
    }
    return path.replace(/^\/+/, '');
  }
  var THIS_PAGE = pageSiteRel().toLowerCase();
  var ANNO_SRC = siteRootDir() + '/批注/annotations.js';
  var SERVER_MODE = /^https?:$/.test(window.location.protocol);   // 走本地服务器（http）时自动保存

  function buildAnnoJs() {
    return '/* 本地批注数据 —— 此文件不上传 git\n'
         + ' * 保存位置：' + ANNO_SRC + '\n'
         + ' * 若文件不存在，新建一个文本文件命名为 annotations.js 即可。 */\n'
         + 'window.__ANNOTATIONS__ = ' + JSON.stringify(ALL, null, 2) + ';\n';
  }

  /* ---- 文本定位工具（基于字符偏移，包裹不改变文本，偏移跨刷新稳定） ---- */
  function textNodes() {
    var root = document.getElementById('main');
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var arr = [], n;
    while ((n = w.nextNode())) arr.push(n);
    return arr;
  }
  function wrapSegment(node, s, e, anno) {
    var txt = node.nodeValue;
    var pre = document.createTextNode(txt.slice(0, s));
    var mid = document.createTextNode(txt.slice(s, e));
    var post = document.createTextNode(txt.slice(e));
    var u = document.createElement('u');
    u.className = 'anno';
    u.setAttribute('data-id', anno.id);
    u.setAttribute('data-note', anno.note || '');
    u.appendChild(mid);
    var parent = node.parentNode;
    parent.insertBefore(pre, node);
    parent.insertBefore(u, node);
    parent.insertBefore(post, node);
    parent.removeChild(node);
  }
  function locateAndWrap(offset, len, anno) {
    var nodes = textNodes(), acc = 0, end = offset + len;
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i], L = node.nodeValue.length;
      if (offset >= acc && offset <= acc + L && end <= acc + L) {
        wrapSegment(node, offset - acc, end - acc, anno);
        return true;
      }
      acc += L;
    }
    return false;
  }
  function wrapRange(offset, len, anno) {
    var end = offset + len;
    var nodes = textNodes(), acc = 0, segs = [];
    for (var i = 0; i < nodes.length; i++) {
      var L = nodes[i].nodeValue.length;
      var s = Math.max(offset, acc), e = Math.min(end, acc + L);
      if (s < e) segs.push([s, e]);
      acc += L;
    }
    segs.reverse();           // 从后往前包，避免节点树变化导致索引失效
    for (var j = 0; j < segs.length; j++) {
      locateAndWrap(segs[j][0], segs[j][1] - segs[j][0], anno);
    }
  }
  function selectionOffsetInMain() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed) return -1;
    var c = sel.getRangeAt(0).startContainer;
    if (c && c.nodeType === 3) {
      var nodes = textNodes(), acc = 0;
      for (var i = 0; i < nodes.length; i++) {
        if (nodes[i] === c) return acc + sel.getRangeAt(0).startOffset;
        acc += nodes[i].nodeValue.length;
      }
    }
    return -1;
  }
  function selTextInMain() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed) return null;
    var main = document.getElementById('main');
    var node = sel.anchorNode;
    if (!main || !node || !main.contains(node)) return null;
    return sel.toString();
  }

  /* ---- 渲染本页批注 ---- */
  function mine() {
    return ALL.filter(function (a) { return (a.page || '').toLowerCase() === THIS_PAGE; });
  }
  function renderAll() {
    mine().forEach(function (a) {
      try { wrapRange(a.offset || 0, (a.text || '').length, a); } catch (e) {}
    });
  }

  /* ---- 右键菜单 ---- */
  var menu = document.createElement('div');
  menu.className = 'anno-menu';
  menu.style.display = 'none';
  document.body.appendChild(menu);
  function hideMenu() { menu.style.display = 'none'; menu.innerHTML = ''; }
  function showMenu(x, y, items) {
    menu.innerHTML = '';
    items.forEach(function (it) {
      if (it === 'sep') {
        var d = document.createElement('div'); d.className = 'sep'; menu.appendChild(d);
      } else {
        var b = document.createElement('button');
        b.textContent = it[0];
        b.addEventListener('click', function (ev) {
          if (ev && ev.stopPropagation) ev.stopPropagation();   // 防止冒泡到全局 click 把刚弹出的编辑器关掉
          hideMenu();
          it[1]();
        });
        menu.appendChild(b);
      }
    });
    menu.style.display = 'block';
    var w = menu.offsetWidth, h = menu.offsetHeight;
    menu.style.left = Math.min(x, window.innerWidth - w - 8) + 'px';
    menu.style.top = Math.min(y, window.innerHeight - h - 8) + 'px';
  }

  /* ---- 浮层定位：先量真实尺寸再摆位，保证整个浮层留在视口内 ----
   * 关键：必须在 display:block（但 visibility:hidden）下量 offsetWidth/offsetHeight，
   * 否则 display:none 时量到 0，钳制失效 —— 浮层会伸出右/下边界，锁定、保存、取消都点不到。
   * 下方放不下时优先翻到锚点上方；翻上去仍放不下则贴底并内部滚动。
   * anchorTop：锚点（标记/选中行）的顶部，用于判断往上翻的位置。 */
  var POPUP_PAD = 8;
  function placePopup(el, x, y, anchorTop) {
    el.style.maxWidth = '';
    el.style.maxHeight = '';
    el.style.overflowY = '';
    el.style.visibility = 'hidden';
    el.style.display = 'block';
    el.style.left = '0px';
    el.style.top = '0px';
    var vw = window.innerWidth, vh = window.innerHeight;
    var w = el.offsetWidth, h = el.offsetHeight;
    if (w > vw - POPUP_PAD * 2) {          // 窗口很窄/浏览器放大：先限宽再重量
      el.style.maxWidth = Math.max(160, vw - POPUP_PAD * 2) + 'px';
      w = el.offsetWidth;
    }
    var maxH = Math.max(120, vh - POPUP_PAD * 2);
    if (h > maxH) {                        // 窗口很矮：限高 + 内部滚动，别让按钮掉出视口
      el.style.maxHeight = maxH + 'px';
      el.style.overflowY = 'auto';
      h = Math.min(el.offsetHeight, maxH);
    }
    var left = Math.max(POPUP_PAD, Math.min(x, vw - w - POPUP_PAD));
    var top = y;
    if (top + h > vh - POPUP_PAD) {
      var up = (typeof anchorTop === 'number' ? anchorTop : y) - h - POPUP_PAD;
      top = (up >= POPUP_PAD) ? up : vh - h - POPUP_PAD;
    }
    top = Math.max(POPUP_PAD, Math.min(top, vh - h - POPUP_PAD));
    el.style.left = Math.round(left) + 'px';
    el.style.top = Math.round(top) + 'px';
    el.style.visibility = '';
  }

  /* ---- 批注编辑器弹窗 ---- */
  var editor = document.createElement('div');
  editor.className = 'anno-editor';
  editor.style.display = 'none';
  document.body.appendChild(editor);
  var editorState = null;
  var editorAnchor = null;        // 编辑框锚点，窗口缩放/改尺寸时据此重新摆位
  function openEditor(x, y, state, anchorTop) {
    editorState = state;
    editorAnchor = {x: x, y: y, top: anchorTop};
    editor.innerHTML = '';
    var ta = document.createElement('textarea');
    ta.placeholder = '写下你的批注语句…（可留空，仅下划线）';
    ta.value = state.note || '';
    var btns = document.createElement('div'); btns.className = 'btns';
    var ok = document.createElement('button'); ok.className = 'ok'; ok.textContent = '保存';
    var cancel = document.createElement('button'); cancel.textContent = '取消';
    ok.addEventListener('click', function () { commitEditor(ta.value); });
    cancel.addEventListener('click', function () { editor.style.display = 'none'; editorState = null; });
    btns.appendChild(cancel); btns.appendChild(ok);
    editor.appendChild(ta); editor.appendChild(btns);
    placePopup(editor, x, y, anchorTop);
    ta.focus();
  }
  function commitEditor(note) {
    var st = editorState;
    editor.style.display = 'none';
    editorState = null;
    if (!st) return;
    if (st.mode === 'add') {
      st.anno.note = note.trim();
      st.anno.updated = new Date().toISOString();
      ALL.push(st.anno);
      wrapRange(st.offset, st.text.length, st.anno);
    } else if (st.mode === 'edit') {
      st.anno.note = note.trim();
      st.anno.updated = new Date().toISOString();
      var id = st.anno.id;
      document.querySelectorAll('u.anno[data-id="' + id + '"]').forEach(function (el) {
        el.setAttribute('data-note', st.anno.note || '');
      });
    }
    dirty = true;
    hideTip();
    updatePill();
    autoSave();
  }

  /* ---- 添加批注（用右键时捕获的选中内容；避免点击菜单项后选中被清空） ---- */
  var lastSel = null;
  function addAnno() {
    var sel = lastSel;
    var text = (sel && sel.text) ? sel.text : selTextInMain();
    if (!text) { toast('请先在正文中选中一段文字，再右键标注。'); return; }
    var offset = (sel && typeof sel.offset === 'number' && sel.offset >= 0)
        ? sel.offset : selectionOffsetInMain();
    if (offset < 0) {
      var full = textNodes().map(function (n) { return n.nodeValue; }).join('');
      offset = full.indexOf(text);
      if (offset < 0) { alert('无法定位选中文字，批注未添加。'); return; }
    }
    var anno = {
      id: 'a' + Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36),
      page: THIS_PAGE,
      text: text,
      offset: offset,
      note: '',
      created: new Date().toISOString(),
      updated: new Date().toISOString()
    };
    var x = (sel && sel.rect) ? sel.rect.left + 8 : 120;
    var y = (sel && sel.rect) ? sel.rect.bottom + 8 : 120;
    openEditor(x, y, {mode: 'add', anno: anno, text: text, offset: offset},
               (sel && sel.rect) ? sel.rect.top : undefined);
  }

  /* ---- 编辑 / 删除 ---- */
  function findAnnoByEl(u) {
    var id = u.getAttribute('data-id');
    for (var i = 0; i < ALL.length; i++) if (ALL[i].id === id) return ALL[i];
    return null;
  }
  function editAnno(u) {
    var anno = findAnnoByEl(u);
    if (!anno) return;
    var r = u.getBoundingClientRect();
    openEditor(r.left, r.bottom + 8, {mode: 'edit', anno: anno, note: anno.note}, r.top);
  }
  function delAnno(u) {
    var id = u.getAttribute('data-id');
    ALL = ALL.filter(function (a) { return a.id !== id; });
    document.querySelectorAll('u.anno[data-id="' + id + '"]').forEach(function (el) {
      var parent = el.parentNode;
      while (el.firstChild) parent.insertBefore(el.firstChild, el);
      parent.removeChild(el);
    });
    dirty = true;
    updatePill();
    autoSave();
  }

  /* ---- 保存：服务器模式 POST 直写本地文件；file:// 模式下载后覆盖 ---- */
  function saveAnno() {
    var js = buildAnnoJs();
    if (SERVER_MODE) {
      saveViaServer(js);
      return;
    }
    var blob = new Blob([js], {type: 'application/javascript;charset=utf-8'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'annotations.js';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 300);
    dirty = false;
    updatePill();
    toast('已生成批注文件（共 ' + ALL.length + ' 条）。\n'
        + '① 浏览器会下载 annotations.js\n'
        + '② 把它覆盖保存到：' + ANNO_SRC + '\n'
        + '（网页无法直接写本地文件，所以保存=下载后存放；之后刷新页面批注自动恢复）');
  }

  /* 服务器模式：POST /anno 由本地服务器写入 批注/annotations.js */
  function saveViaServer(js) {
    fetch('/anno', {
      method: 'POST',
      headers: {'Content-Type': 'application/javascript;charset=utf-8'},
      body: js
    }).then(function (r) {
      if (r.ok) {
        dirty = false;
        updatePill();
      } else {
        toast('自动保存失败（HTTP ' + r.status + '），可改用下载保存。');
      }
    }).catch(function () {
      toast('自动保存失败：无法连接本地服务器，可改用下载保存。');
    });
  }
  function autoSave() {
    if (SERVER_MODE) saveViaServer(buildAnnoJs());
  }

  /* ---- 右下角状态按钮 ---- */
  var pill = document.createElement('button');
  pill.className = 'anno-pill';
  pill.title = SERVER_MODE
      ? '批注已自动保存到本机 批注/annotations.js（不上传 git）。\n点击可立即保存一次。'
      : '批注数据只存本机 批注/annotations.js（不上传 git）。\n点击此按钮生成批注文件：浏览器下载 annotations.js 后，覆盖保存到：\n' + ANNO_SRC;
  pill.addEventListener('click', saveAnno);
  document.body.appendChild(pill);
  function updatePill() {
    if (SERVER_MODE) {
      pill.textContent = '批注 ' + ALL.length + (dirty ? ' · 保存中' : ' · 已自动保存');
      pill.classList.toggle('dirty', dirty);
    } else {
      pill.textContent = dirty
          ? '● 批注 ' + ALL.length + ' · 未保存·点此下载'
          : '批注 ' + ALL.length + ' · 已保存(文件模式)';
      pill.classList.toggle('dirty', dirty);
    }
  }

  /* ---- 悬停提示 ---- */
  var tip = document.createElement('div');
  tip.className = 'anno-tip';
  tip.style.display = 'none';
  document.body.appendChild(tip);
  function hideTip() { tip.style.display = 'none'; }
  document.addEventListener('mouseover', function (ev) {
    var u = ev.target.closest ? ev.target.closest('u.anno') : null;
    if (u) {
      var note = u.getAttribute('data-note') || '';
      if (!note) { hideTip(); return; }
      tip.textContent = note;
      tip.style.display = 'block';
      var r = u.getBoundingClientRect();
      var tw = tip.offsetWidth, th = tip.offsetHeight;
      var left = Math.min(r.left, window.innerWidth - tw - 8); left = Math.max(8, left);
      var top = r.bottom + 6;
      if (top + th > window.innerHeight - 8) top = Math.max(8, r.top - th - 6);
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
    } else if (tip.style.display === 'block') {
      hideTip();
    }
  });

  /* ---- 轻提示 ---- */
  var toastEl = null;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'anno-toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.style.display = 'block';
    clearTimeout(toastEl._t);
    toastEl._t = setTimeout(function () { toastEl.style.display = 'none'; }, 6000);
  }

  /* ---- 右键事件 ---- */
  document.addEventListener('contextmenu', function (ev) {
    var t = ev.target;
    var annoEl = t.closest ? t.closest('u.anno') : null;
    var main = document.getElementById('main');
    if (annoEl) {
      ev.preventDefault();
      // 在已有下划线上右键且有文字选中时，也提供「添加补充注释」（两种注释可叠加同位置）
      var selTxt2 = main && main.contains(t) ? selTextInMain() : null;
      var items2 = [
        ['编辑批注', function () { editAnno(annoEl); }],
        ['删除下划线', function () { delAnno(annoEl); }]
      ];
      if (selTxt2) {
        lastSel = {text: selTxt2, offset: selectionOffsetInMain(), rect: null, range: null};
        try {
          lastSel.range = window.getSelection().getRangeAt(0);
          var rr2 = window.getSelection().getRangeAt(0).getBoundingClientRect();
          lastSel.rect = {left: rr2.left, top: rr2.top, bottom: rr2.bottom};
        } catch (e) {}
        items2.push(['添加补充注释', addDzAnno]);
      }
      items2.push('sep', ['保存批注', saveAnno]);
      showMenu(ev.clientX, ev.clientY, items2);
      return;
    }
    var inMain = main && main.contains(t);
    var selText = inMain ? selTextInMain() : null;
    if (selText) {
      ev.preventDefault();
      lastSel = {text: selText, offset: selectionOffsetInMain(), rect: null, range: null};
      try {
        lastSel.range = window.getSelection().getRangeAt(0);
        var rr = window.getSelection().getRangeAt(0).getBoundingClientRect();
        lastSel.rect = {left: rr.left, top: rr.top, bottom: rr.bottom};
      } catch (e) {}
      showMenu(ev.clientX, ev.clientY, [
        ['添加下划线并批注', addAnno],
        ['添加补充注释', addDzAnno],
        'sep',
        ['复制', function () { try { document.execCommand('copy'); } catch (e) {} }],
        ['全选', function () {
          if (main) {
            var r = document.createRange(); r.selectNodeContents(main);
            var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
          }
        }],
        ['保存批注', saveAnno]
      ]);
      return;
    }
    hideMenu();
    // 在正文里右键但没选中文字：给个提示，避免“没反应”
    if (inMain) {
      toast('请先在正文中选中一段文字，再右键标注（或用鼠标直接拖选后右键）。');
    }
  });
  document.addEventListener('click', function (ev) {
    var dzm = ev.target.closest ? ev.target.closest('sup.dzref') : null;
    if (dzm) { ev.preventDefault(); openDzEditor(dzm); return; }
    if (!menu.contains(ev.target)) hideMenu();
    if (!editor.contains(ev.target)) editor.style.display = 'none';
    if (!dzEditor.contains(ev.target)) { dzEditor.style.display = 'none'; dzState = null; }
  });
  window.addEventListener('scroll', function () { hideMenu(); hideTip(); }, {passive: true});
  window.addEventListener('resize', function () {
    hideMenu();
    hideTip();
    // 窗口尺寸/浏览器缩放变化后按原锚点重新摆位，别让浮层被挤出视口
    if (dzState && dzState.anchor && dzEditor.style.display === 'block') {
      placePopup(dzEditor, dzState.anchor.left, dzState.anchor.bottom + 8, dzState.anchor.top);
    }
    if (editorAnchor && editor.style.display === 'block') {
      placePopup(editor, editorAnchor.x, editorAnchor.y, editorAnchor.top);
    }
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') {
      hideMenu();
      editor.style.display = 'none';
      dzEditor.style.display = 'none';
      dzState = null;
      hideTip();
    }
  });

  /* ================= 补充注释（读者注释 · 公共入库） =================
   * 与私人下划线批注不同：补充注释直接写进文章 HTML（上标 + 文末「读者补充注释」区），
   * 提交 git 公开；编号 [dz.1][dz.2]… 按页重置；锁定条目只读但照常参与重编号。
   * 增/删/改必须服务器模式（http），file:// 只能看。 */
  var dzEditor = document.createElement('div');
  dzEditor.className = 'anno-editor dz-editor';
  dzEditor.style.display = 'none';
  document.body.appendChild(dzEditor);
  var dzState = null;

  function ensureDzSection() {
    var main = document.getElementById('main');
    var sec = document.getElementById('dznotes');
    if (!sec) {
      sec = document.createElement('section');
      sec.id = 'dznotes';
      sec.className = 'dznotes';
      var h = document.createElement('h3');
      h.className = 'dznotes-title';
      h.textContent = '读者补充注释';
      var ol = document.createElement('ol');
      ol.className = 'dzlist';
      sec.appendChild(h);
      sec.appendChild(ol);
      main.appendChild(sec);
    }
    return sec;
  }
  function genDzId() {
    return 'dz' + Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36);
  }
  /* 标记该插在谁后面：整块上标（脚注 [1] / 已有补充注释）> 链接 > 私人下划线。
   * 一定要插到这些元素的“后面”，不能插进它们内部：
   * <sup class="fnref"> 的 UA font-size:smaller(≈0.83) 与 <a> 的 0.72em 会逐层相乘，
   * 嵌进去的标记字号会被缩小一到两级，看起来比原版注释小；
   * 下划线则会在写回时被剥掉。 */
  function markerHost(node) {
    var sup = null, other = null;
    var n = node ? (node.nodeType === 1 ? node : node.parentNode) : null;
    for (; n && n.nodeType === 1 && n.id !== 'main'; n = n.parentNode) {
      var tag = n.tagName;
      if (tag === 'SUP') { sup = n; break; }
      if (!other && (tag === 'A' || (tag === 'U' && n.classList && n.classList.contains('anno')))) other = n;
    }
    return sup || other;
  }
  function insertMarkerAtRangeEnd(range, marker) {
    var host = markerHost(range.endContainer);
    if (host && host.parentNode) {
      host.parentNode.insertBefore(marker, host.nextSibling);
      return;
    }
    var node = range.endContainer, off = range.endOffset;
    if (node.nodeType === 3) {
      if (off < node.nodeValue.length) {
        var after = node.splitText(off);
        node.parentNode.insertBefore(marker, after);
      } else {
        node.parentNode.insertBefore(marker, node.nextSibling);
      }
    } else {
      node.insertBefore(marker, node.childNodes[off] || null);
    }
  }
  /* 老页面里已经被插进 <sup class="fnref"><a>…</a></sup> 内部的标记：
   * 打开页面时把它挪到整个上标后面，字号才和原版注释同级（字号逐层相乘的问题见 markerHost） */
  function normalizeDzMarkers() {
    var list = Array.prototype.slice.call(document.querySelectorAll('sup.dzref'));
    list.forEach(function (m) {
      var host = markerHost(m.parentNode);
      if (host && host.parentNode && host.contains(m)) {
        host.parentNode.insertBefore(m, host.nextSibling);
      }
    });
  }
  /* 按标记在正文中的顺序统一重编号 + 重排底部列表，保证一一对应 */
  function renumberDz() {
    var markers = Array.prototype.slice.call(document.querySelectorAll('sup.dzref'));
    var sec = document.getElementById('dznotes');
    var ol = sec ? sec.querySelector('ol.dzlist') : null;
    markers.forEach(function (m, i) {
      m.textContent = '[dz.' + (i + 1) + ']';
      if (ol) {
        var li = ol.querySelector('.dznote[data-id="' + m.getAttribute('data-id') + '"]');
        if (li) {
          var lbl = li.querySelector('.dzlabel');
          if (lbl) lbl.textContent = '[dz.' + (i + 1) + ']';
          if (li.parentNode !== ol) ol.appendChild(li);
        }
      }
    });
  }
  function dzNoteText(li) {
    var t = li.querySelector('.dztext');
    return t ? t.textContent : '';
  }
  /* 删掉一条补充注释：正文上标 + 文末条目；条目删空时连「读者补充注释」区一起收掉 */
  function removeDzNote(marker, li) {
    if (marker && marker.parentNode) marker.parentNode.removeChild(marker);
    if (li && li.parentNode) li.parentNode.removeChild(li);
    var sec = document.getElementById('dznotes');
    if (sec && !sec.querySelector('.dznote')) sec.parentNode.removeChild(sec);
  }
  function addDzAnno() {
    if (!SERVER_MODE) {
      toast('补充注释需在服务器模式下添加：双击「启动导师文集.bat」，用 http://127.0.0.1:8790/ 打开本站。');
      return;
    }
    var range = lastSel && lastSel.range;
    if (!range || range.collapsed) { toast('请先选中正文中的一段文字，再右键添加补充注释。'); return; }
    var id = genDzId();
    var sec = ensureDzSection();
    var ol = sec.querySelector('ol.dzlist');
    var li = document.createElement('li');
    li.className = 'dznote';
    li.setAttribute('data-id', id);
    li.setAttribute('data-locked', '0');
    var lbl = document.createElement('span'); lbl.className = 'dzlabel';
    var txt = document.createElement('span'); txt.className = 'dztext';
    li.appendChild(lbl); li.appendChild(txt);
    ol.appendChild(li);
    var marker = document.createElement('sup');
    marker.className = 'dzref';
    marker.setAttribute('data-id', id);
    marker.title = '读者补充注释';
    insertMarkerAtRangeEnd(range, marker);
    renumberDz();
    openDzEditor(marker, true);
  }
  function openDzEditor(marker, isNew) {
    if (!SERVER_MODE) {
      toast('补充注释需在服务器模式下编辑：双击「启动导师文集.bat」打开本站。');
      return;
    }
    var id = marker.getAttribute('data-id');
    var sec = document.getElementById('dznotes');
    if (!sec) return;
    var li = sec.querySelector('.dznote[data-id="' + id + '"]');
    if (!li) return;
    var r = marker.getBoundingClientRect();   // 先记下锚点，锁定/解锁重绘后仍按它定位
    dzState = {
      id: id, marker: marker, li: li, isNew: !!isNew,
      anchor: {left: r.left, top: r.top, bottom: r.bottom}
    };
    renderDzEditor();                          // 内部负责量尺寸 + 摆位
    if (li.getAttribute('data-locked') !== '1') dzEditor.querySelector('textarea').focus();
  }
  function renderDzEditor() {
    var locked = dzState.li.getAttribute('data-locked') === '1';
    dzEditor.innerHTML = '';
    var head = document.createElement('div');
    head.className = 'dz-head';
    var t = document.createElement('span');
    t.className = 'dz-title';
    t.textContent = '读者补充注释' + (locked ? '（已锁定）' : '');
    var lockBtn = document.createElement('button');
    lockBtn.className = 'lockbtn';
    lockBtn.textContent = locked ? '🔓 解锁' : '🔒 锁定';
    lockBtn.title = locked ? '解锁后才可以编辑或删除' : '锁定后只读，防止误操作（仍会参与自动重编号）';
    lockBtn.addEventListener('click', function (ev) {
      if (ev && ev.stopPropagation) ev.stopPropagation();   // 重绘会替换按钮，阻止冒泡以免误判“点在弹窗外”
      if (locked) {
        // 当前已锁定 -> 仅解锁（只读期间内容不会变）
        dzState.li.setAttribute('data-locked', '0');
        renderDzEditor();
        persistDz();
      } else {
        // 当前未锁定 -> 先保存当前输入，再锁定（空内容等同删除）
        var v = ta.value;
        if (!v.trim()) {
          removeDzNote(dzState.marker, dzState.li);
          renumberDz();
          dzEditor.style.display = 'none';
          dzState = null;
          persistDz();
        } else {
          dzState.li.querySelector('.dztext').textContent = v;
          dzState.li.setAttribute('data-locked', '1');
          renderDzEditor();
          persistDz();
        }
      }
    });
    head.appendChild(t);
    head.appendChild(lockBtn);
    var ta = document.createElement('textarea');
    ta.placeholder = '写补充注释…（留空后点保存 = 删除该条，编号自动重排）';
    ta.value = dzNoteText(dzState.li);
    ta.disabled = locked;
    var btns = document.createElement('div');
    btns.className = 'btns';
    if (!locked) {
      var ok = document.createElement('button');
      ok.className = 'ok';
      ok.textContent = '保存';
      ok.addEventListener('click', function () {
        var v = ta.value;
        if (!v.trim()) {
          removeDzNote(dzState.marker, dzState.li);
        } else {
          dzState.li.querySelector('.dztext').textContent = v;
        }
        renumberDz();
        dzEditor.style.display = 'none';
        dzState = null;
        persistDz();
      });
      btns.appendChild(ok);
    }
    var cancel = document.createElement('button');
    cancel.textContent = '取消';
    cancel.addEventListener('click', function () {
      var wasNew = dzState.isNew;
      var empty = !ta.value.trim();
      if (empty) {
        // 取消时内容为空：和「保存空内容」一样按删除处理（新条目、被清空的旧条目都删掉）
        removeDzNote(dzState.marker, dzState.li);
        renumberDz();
      } else if (wasNew) {
        // 新建未保存：丢弃输入，回滚这条空条目
        removeDzNote(dzState.marker, dzState.li);
        renumberDz();
      }
      dzEditor.style.display = 'none';
      dzState = null;
      if (empty && !wasNew) persistDz();   // 旧条目被清空删除，要写回文章
    });
    btns.appendChild(cancel);
    dzEditor.appendChild(head);
    dzEditor.appendChild(ta);
    dzEditor.appendChild(btns);
    // 每次重绘（含锁定/解锁后按钮数量变化）都按锚点重新摆位，避免高度变化后越界
    if (dzState && dzState.anchor) {
      placePopup(dzEditor, dzState.anchor.left, dzState.anchor.bottom + 8, dzState.anchor.top);
    }
  }
  function persistDz() {
    if (!SERVER_MODE) return;
    var path = decodeURIComponent(window.location.pathname).replace(/^\/+/, '');
    fetch('/page-write', {
      method: 'POST',
      headers: {'Content-Type': 'application/json;charset=utf-8'},
      body: JSON.stringify({path: path, mainHtml: serializeMain()}),
      keepAlive: true            // 点保存后立刻刷新/跳转也不中断写入
    }).then(function (r) {
      toast(r.ok ? '补充注释已写入文章并保存' : '保存失败（HTTP ' + r.status + '）');
    }).catch(function () {
      toast('保存失败：无法连接本地服务器');
    });
  }
  /* 序列化 <main> 用于写回文章；剥掉私有下划线（u.anno）时保留内部子节点
   * （万一补充注释标记在下划线内，也随内容移出，不丢失） */
  function serializeMain() {
    var clone = document.getElementById('main').cloneNode(true);
    clone.querySelectorAll('u.anno').forEach(function (u) {
      while (u.firstChild) u.parentNode.insertBefore(u.firstChild, u);
      u.parentNode.removeChild(u);
    });
    return clone.innerHTML;
  }

  /* ---- 载入批注数据（文件不存在则忽略） ---- */
  normalizeDzMarkers();   // 老页面里嵌在脚注上标内部的补充注释标记先挪出来（字号才同级）
  updatePill();
  var s = document.createElement('script');
  s.src = SERVER_MODE ? ANNO_SRC + '?t=' + Date.now() : ANNO_SRC;   // http 下加时间戳防缓存
  s.onload = function () {
    if (Array.isArray(window.__ANNOTATIONS__)) ALL = window.__ANNOTATIONS__;
    renderAll();
    updatePill();
  };
  s.onerror = function () { updatePill(); };
  document.head.appendChild(s);
})();
