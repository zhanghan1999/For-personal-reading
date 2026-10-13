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
    var groups = PAGE.tocGroups || [];
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
    var noteEl = document.getElementById(link.getAttribute('href').slice(1));
    if (!noteEl) return;
    fntip.textContent = noteEl.textContent.replace(/^[\[\]()a-zA-Z0-9]+\s*/, '');
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
        b.addEventListener('click', function () { hideMenu(); it[1](); });
        menu.appendChild(b);
      }
    });
    menu.style.display = 'block';
    var w = menu.offsetWidth, h = menu.offsetHeight;
    menu.style.left = Math.min(x, window.innerWidth - w - 8) + 'px';
    menu.style.top = Math.min(y, window.innerHeight - h - 8) + 'px';
  }

  /* ---- 批注编辑器弹窗 ---- */
  var editor = document.createElement('div');
  editor.className = 'anno-editor';
  editor.style.display = 'none';
  document.body.appendChild(editor);
  var editorState = null;
  function openEditor(x, y, state) {
    editorState = state;
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
    editor.style.display = 'block';
    var w = editor.offsetWidth, h = editor.offsetHeight;
    editor.style.left = Math.min(x, window.innerWidth - w - 10) + 'px';
    editor.style.top = Math.min(y, window.innerHeight - h - 10) + 'px';
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
    openEditor(x, y, {mode: 'add', anno: anno, text: text, offset: offset});
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
    openEditor(r.left, r.bottom + 8, {mode: 'edit', anno: anno, note: anno.note});
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
      pill.textContent = dirty ? '● 批注 ' + ALL.length + ' · 未保存' : '批注 ' + ALL.length;
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
      showMenu(ev.clientX, ev.clientY, [
        ['编辑批注', function () { editAnno(annoEl); }],
        ['删除下划线', function () { delAnno(annoEl); }],
        'sep',
        ['保存批注', saveAnno]
      ]);
      return;
    }
    var inMain = main && main.contains(t);
    var selText = inMain ? selTextInMain() : null;
    if (selText) {
      ev.preventDefault();
      lastSel = {text: selText, offset: selectionOffsetInMain(), rect: null};
      try {
        var rr = window.getSelection().getRangeAt(0).getBoundingClientRect();
        lastSel.rect = {left: rr.left, bottom: rr.bottom};
      } catch (e) {}
      showMenu(ev.clientX, ev.clientY, [
        ['添加下划线并批注', addAnno],
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
    if (!menu.contains(ev.target)) hideMenu();
    if (!editor.contains(ev.target)) editor.style.display = 'none';
  });
  window.addEventListener('scroll', function () { hideMenu(); hideTip(); }, {passive: true});
  window.addEventListener('resize', function () { hideMenu(); hideTip(); });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') { hideMenu(); editor.style.display = 'none'; hideTip(); }
  });

  /* ---- 载入批注数据（文件不存在则忽略） ---- */
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
