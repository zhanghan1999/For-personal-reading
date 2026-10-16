/* ============================================================
   导师文集 · 轮换引言 (assets/quote.js)
   纯原生 JS、无依赖；供 首页 + 人物页 + 书籍/选卷页 使用。
   特性：
   - 15 条引言；每 5 分钟全站同步换一条（同一时间槽所有页面显示同一条）；
   - 一轮内不重复，全部出现一遍后重新洗牌；
   - 增删引言（改 QUOTES 条数）自动重置本轮；
   - 找不到 .hero .sub.quote 时自动在 hero 的 .sub 与 .meta 之间插入；
   - localStorage 不可用时退化为「会话内不重复」（内存态），跨刷新不保证。
   使用：在非正文页 </body> 前挂 <script src="…/assets/quote.js"></script>。
   ============================================================ */
(function () {
  'use strict';

  var QUOTES = [
    { t: '我正式劝同志们读一点书，免得受知识分子的骗。', a: '—— 毛泽东' },
    { t: '学习的敌人是自己的满足，要认真学习一点东西，必须从不自满开始。', a: '—— 毛泽东《中国共产党在民族战争中的地位》' },
    { t: '读书是学习，使用也是学习，而且是更重要的学习。', a: '—— 毛泽东《中国革命战争的战略问题》' },
    { t: '一切狡猾的人，不照科学态度办事的人，自以为得计，自以为很聪明，其实都是最蠢的，都是没有好结果的。', a: '—— 毛泽东《整顿党的作风》' },
    { t: '没有革命的理论，就不会有革命的运动。', a: '—— 列宁《怎么办？》' },
    { t: '只有用人类创造的全部知识财富来丰富自己的头脑，才能成为共产主义者。', a: '—— 列宁《青年团的任务》' },
    { t: '我们不需要死记硬背，但是我们需要用基本事实的知识来发展和增进每个学习者的思考力。', a: '—— 列宁《青年团的任务》' },
    { t: '一个民族要想站在科学的最高峰，就一刻也不能没有理论思维。', a: '—— 恩格斯《自然辩证法》' },
    { t: '没有理论思维，就会连两件自然的事实也联系不起来，或者连二者之间所存在的联系都无法了解。', a: '—— 恩格斯《自然辩证法》' },
    { t: '真理是包含在认识过程本身中，包含在科学的长期的历史发展中。', a: '—— 恩格斯《路德维希·费尔巴哈和德国古典哲学的终结》' },
    { t: '离开革命实践的理论是空洞的理论，而不以革命理论为指南的实践是盲目的实践。', a: '—— 斯大林《论列宁主义基础》' },
    { t: '要建设，就必须有知识，必须掌握科学。而要有知识，就必须学习。顽强地、耐心地学习。', a: '—— 斯大林《在苏联列宁共产主义青年团第八次代表大会上的演说》' },
    { t: '掌握马克思列宁主义理论，决不是说要熟读它的一切公式和结论，而是要领会这个理论的实质。', a: '—— 斯大林《论列宁主义基础》' },
    { t: '在科学上没有平坦的大道，只有不畏劳苦沿着陡峭山路攀登的人，才有希望达到光辉的顶点。', a: '—— 马克思《资本论》第一卷法文版序言' },
    { t: '理论一经掌握群众，也会变成物质力量。', a: '—— 马克思《〈黑格尔法哲学批判〉导言》' }
  ];

  var N = QUOTES.length;
  var KEY = 'dsw-hero-quote-v1';
  var STEP = 5 * 60 * 1000;          // 5 分钟
  var mem = null;                    // localStorage 不可用时的会话内状态

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function stateFor(slot) {
    var st = null;
    try { st = JSON.parse(localStorage.getItem(KEY)); } catch (e) { st = null; }
    if (!st) st = mem;
    var needNew = !st || st.ver !== N || slot < st.start || slot >= st.start + N;
    if (needNew) {
      var deck = [];
      for (var i = 0; i < N; i++) deck.push(i);
      st = { ver: N, start: slot, deck: shuffle(deck) };
    }
    try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) { mem = st; }
    return st;
  }

  function currentQuote() {
    var slot = Math.floor(Date.now() / STEP);
    var st = stateFor(slot);
    var idx = st.deck[slot - st.start];
    return QUOTES[idx];
  }

  function render() {
    var hero = document.querySelector('.hero');
    if (!hero) return;
    var el = hero.querySelector('.sub.quote');
    if (!el) {
      el = document.createElement('div');
      el.className = 'sub quote';
      el.id = 'rotatingQuote';
      var meta = hero.querySelector('.meta');
      var sub = hero.querySelector('.sub');
      if (meta) hero.insertBefore(el, meta);
      else if (sub) sub.parentNode.insertBefore(el, sub.nextSibling);
      else hero.appendChild(el);
    }
    var q = currentQuote();
    el.innerHTML = '<span class="qtext"></span><br><span class="attr"></span>';
    var qt = el.querySelector('.qtext');
    var at = el.querySelector('.attr');
    if (qt) qt.textContent = '“' + q.t + '”';
    if (at) at.textContent = q.a;
  }

  render();
  // 对齐到整 5 分钟边界再开始轮换，全站切换误差 <1 秒
  var _now = Date.now();
  setTimeout(function () {
    render();
    setInterval(render, STEP);
  }, Math.ceil(_now / STEP) * STEP - _now);
  window.addEventListener('storage', function (e) {
    if (e.key === KEY) render();   // 多标签页同步
  });
})();
