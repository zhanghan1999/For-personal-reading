/* ============================================================
   导师文集 · 阅读进度展示 (assets/read.js)
   供非正文页使用：首页 / 人物页 / 选卷页（由 .tools/inject_read_js.py 注入）。
   与阅读页 assets/app.js 共用同一份本机 localStorage（不进 git）：
     dsw-read-v1   { "站点相对路径(小写)": 已读时间戳 }
     dsw-read-last { page, title, brand, t }
   功能：
     - 章节卡片：已读的盖「✓ 已读」印章，入口文案变「重读本篇」；
     - 列章节卡片的选卷页：顶部「阅读进度 n / N 篇」进度条；
     - 卷 / 著作 / 人物卡片：聚合显示其目录下「已读 N 篇」；
     - 首页：「继续阅读」卡片，一键回到上次阅读页。
   localStorage 不可用时静默退化（不显示进度），不影响页面本身。
   ============================================================ */
(function () {
  'use strict';
  if (window.PAGE && document.getElementById('main')) return;   // 阅读页由 app.js 负责

  var KEY = 'dsw-read-v1';
  var LAST_KEY = 'dsw-read-last';

  /* ---- 站点根推导：必须在脚本执行期缓存 currentScript ---- */
  var ROOT_DIR = (function () {
    var cur = document.currentScript;
    if (!cur || !cur.src) return '';
    var p = cur.src.split('/'); p.pop(); p.pop();   // 去掉 read.js 与 assets
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
  function loadMap() {
    try {
      var m = JSON.parse(localStorage.getItem(KEY) || '{}');
      if (m && typeof m === 'object' && !Array.isArray(m)) return m;
    } catch (e) {}
    return {};
  }
  function loadLast() {
    try {
      var v = JSON.parse(localStorage.getItem(LAST_KEY) || 'null');
      if (v && typeof v.page === 'string' && v.page) return v;
    } catch (e) {}
    return null;
  }
  function isChapterKey(k) {
    var b = k.slice(k.lastIndexOf('/') + 1);
    return /^\d{1,4}-[^/]+\.html$/.test(b);   // 章节页文件名规范：两位序号-标题.html
  }
  function fmtDate(t) {
    var d = new Date(t || Date.now()), now = new Date();
    var s = (d.getMonth() + 1) + '月' + d.getDate() + '日';
    if (d.getFullYear() !== now.getFullYear()) s = d.getFullYear() + '年' + s;
    return s;
  }

  function paint() {
    var MAP = loadMap();
    var chapterTotal = 0, chapterRead = 0, cardsEl = null;

    document.querySelectorAll('a.card').forEach(function (card) {
      if (card.classList.contains('disabled')) return;
      var key = keyForHref(card.getAttribute('href'));
      if (!key) return;
      if (!cardsEl) cardsEl = card.parentNode;

      var direct = isChapterKey(key);           // 章节卡片（含单篇文章页：已被记录过也算）
      if (direct) {
        chapterTotal++;
        if (MAP[key]) chapterRead++;
      }
      if (direct || MAP[key]) {
        var read = !!MAP[key];
        card.classList.toggle('read', read);
        var go = card.querySelector('.go');
        if (go) go.textContent = read ? '重读本篇 →' : '打开阅读 →';
        return;
      }

      /* 聚合卡片：卷 / 著作 / 人物入口 → 统计其目录下已读篇数 */
      var base = key.slice(key.lastIndexOf('/') + 1);
      var prefix = '';
      if (base === 'index.html') prefix = key.slice(0, key.lastIndexOf('/') + 1);
      else if (/\.html$/.test(base)) prefix = key.slice(0, -5) + '/';   // 作品名.html → 作品名/
      if (!prefix) return;
      var n = 0;
      for (var k in MAP) { if (Object.prototype.hasOwnProperty.call(MAP, k) && k.indexOf(prefix) === 0) n++; }
      var el = card.querySelector('.readcount');
      if (n > 0) {
        if (!el) {
          el = document.createElement('div');
          el.className = 'readcount';
          var go2 = card.querySelector('.go');
          if (go2) card.insertBefore(el, go2); else card.appendChild(el);
        }
        el.textContent = '已读 ' + n + ' 篇';
      } else if (el) {
        el.parentNode.removeChild(el);
      }
    });

    /* 进度汇总：仅出现在直接列章节卡片的选卷页 */
    var sum = document.getElementById('readSummary');
    if (chapterTotal > 0 && cardsEl) {
      if (!sum) {
        sum = document.createElement('div');
        sum.id = 'readSummary';
        sum.className = 'read-summary';
        sum.innerHTML = '<span class="rs-label">阅读进度</span><span class="rs-bar"><i></i></span><span class="rs-num"></span>';
        cardsEl.parentNode.insertBefore(sum, cardsEl);
      }
      sum.querySelector('.rs-bar i').style.width = Math.round(chapterRead * 100 / chapterTotal) + '%';
      sum.querySelector('.rs-num').textContent = '已读 ' + chapterRead + ' / ' + chapterTotal + ' 篇'
          + (chapterRead === chapterTotal ? ' · 读毕' : '');
      sum.classList.toggle('done', chapterRead === chapterTotal);
    } else if (sum) {
      sum.parentNode.removeChild(sum);
    }

    paintResume();
  }

  /* 首页「继续阅读」：回到上次打开的阅读页 */
  function paintResume() {
    var old = document.getElementById('readResume');
    var last = loadLast();
    var hero = document.querySelector('.hero');
    var isHome = !!document.querySelector('.mentor-grid');
    if (!isHome || !hero || !last) {
      if (old) old.parentNode.removeChild(old);
      return;
    }
    if (!old) {
      old = document.createElement('a');
      old.id = 'readResume';
      old.className = 'resume';
      old.innerHTML = '<span class="rs-kicker">继续阅读</span>'
          + '<span class="rs-main"><b class="rs-brand"></b><span class="rs-title"></span></span>'
          + '<span class="rs-when"></span><span class="rs-go">继续 →</span>';
      hero.parentNode.insertBefore(old, hero.nextSibling);
    }
    old.href = ROOT_DIR + '/' + last.page;
    old.querySelector('.rs-brand').textContent = last.brand ? '《' + last.brand + '》' : '';
    old.querySelector('.rs-title').textContent = last.title || '';
    old.querySelector('.rs-when').textContent = '读于 ' + fmtDate(last.t);
  }

  paint();
  window.addEventListener('storage', function (ev) {
    if (ev.key === KEY || ev.key === LAST_KEY || ev.key === null) paint();
  });
})();
