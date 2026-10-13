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
      lastSel = {text: selText, offset: selectionOffsetInMain(), rect: null, range: null};
      try {
        lastSel.range = window.getSelection().getRangeAt(0);
        var rr = window.getSelection().getRangeAt(0).getBoundingClientRect();
        lastSel.rect = {left: rr.left, bottom: rr.bottom};
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
  window.addEventListener('resize', function () { hideMenu(); hideTip(); });
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
  function insertMarkerAtRangeEnd(range, marker) {
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
    dzState = {id: id, marker: marker, li: li, isNew: !!isNew};
    renderDzEditor();
    var r = marker.getBoundingClientRect();
    var w = dzEditor.offsetWidth, h = dzEditor.offsetHeight;
    dzEditor.style.left = Math.min(r.left, window.innerWidth - w - 10) + 'px';
    dzEditor.style.top = Math.min(r.bottom + 8, window.innerHeight - h - 10) + 'px';
    dzEditor.style.display = 'block';
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
          var m2 = dzState.marker, li2 = dzState.li;
          if (m2 && m2.parentNode) m2.parentNode.removeChild(m2);
          if (li2 && li2.parentNode) li2.parentNode.removeChild(li2);
          var sec = document.getElementById('dznotes');
          if (sec && !sec.querySelector('.dznote')) sec.parentNode.removeChild(sec);
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
        var li = dzState.li, marker = dzState.marker;
        if (!v.trim()) {
          if (marker && marker.parentNode) marker.parentNode.removeChild(marker);
          if (li && li.parentNode) li.parentNode.removeChild(li);
          var sec2 = document.getElementById('dznotes');
          if (sec2 && !sec2.querySelector('.dznote')) sec2.parentNode.removeChild(sec2);
        } else {
          li.querySelector('.dztext').textContent = v;
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
      if (dzState.isNew && dzState.marker) {           // 新建未保存：回滚空条目
        var m2 = dzState.marker, li2 = dzState.li;
        if (m2 && m2.parentNode) m2.parentNode.removeChild(m2);
        if (li2 && li2.parentNode) li2.parentNode.removeChild(li2);
        var sec3 = document.getElementById('dznotes');
        if (sec3 && !sec3.querySelector('.dznote')) sec3.parentNode.removeChild(sec3);
        renumberDz();
      }
      dzEditor.style.display = 'none';
      dzState = null;
    });
    btns.appendChild(cancel);
    dzEditor.appendChild(head);
    dzEditor.appendChild(ta);
    dzEditor.appendChild(btns);
  }
  function persistDz() {
    if (!SERVER_MODE) return;
    var path = decodeURIComponent(window.location.pathname).replace(/^\/+/, '');
    fetch('/page-write', {
      method: 'POST',
      headers: {'Content-Type': 'application/json;charset=utf-8'},
      body: JSON.stringify({path: path, mainHtml: serializeMain()})
    }).then(function (r) {
      toast(r.ok ? '补充注释已写入文章并保存' : '保存失败（HTTP ' + r.status + '）');
    }).catch(function () {
      toast('保存失败：无法连接本地服务器');
    });
  }
  /* 序列化 <main> 用于写回文章；剥掉私有下划线（u.anno），避免私人批注泄漏到公共 HTML */
  function serializeMain() {
    var clone = document.getElementById('main').cloneNode(true);
    clone.querySelectorAll('u.anno').forEach(function (u) {
      var t = document.createTextNode(u.textContent);
      u.parentNode.replaceChild(t, u);
    });
    return clone.innerHTML;
  }

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
