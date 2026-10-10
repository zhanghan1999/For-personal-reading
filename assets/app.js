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
