// download_collected.mjs — 批量下载马克思主义文库全集原始 HTML 到 .tools/sources/
// 用法: node download_collected.mjs [mew|mea|lenin|all]
import fs from 'node:fs';
import path from 'node:path';

const BASE = 'https://marx-zh-cn.github.io/docs';
const SRC = '.tools/sources';
const only = (process.argv[2] || 'all').toLowerCase();

const idx = JSON.parse(fs.readFileSync(path.join(SRC, '_collected_index.json'), 'utf8'));
const groups = [];
if (only === 'all' || only === 'mew') groups.push({ key: 'mew', remote: 'MEW-ZH', list: idx.mew, dir: 'mew' });
if (only === 'all' || only === 'mea') groups.push({ key: 'mea', remote: 'MEA', list: idx.mea, dir: 'mea' });
if (only === 'all' || only === 'lenin') groups.push({ key: 'lenin', remote: 'LENIN', list: idx.lenin, dir: 'lenin' });

const CONCURRENCY = Number(process.env.DL_CONCURRENCY || 12);
const RETRIES = 4;
const TIMEOUT = 45000;

const logPath = path.join(SRC, '_download_log.txt');
const log = (msg) => {
  const line = `[${new Date().toISOString()}] ${msg}`;
  fs.appendFileSync(logPath, line + '\n', 'utf8');
};

const stats = { ok: 0, skip: 0, fail: 0, bytes: 0, fails: [] };

async function fetchBuf(url, tries = RETRIES) {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT) });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return Buffer.from(await r.arrayBuffer());
    } catch (e) {
      lastErr = e;
      await new Promise(res => setTimeout(res, 300 * (i + 1) * (i + 1)));
    }
  }
  throw lastErr;
}

async function saveFile(dest, url) {
  if (fs.existsSync(dest)) {
    const st = fs.statSync(dest);
    if (st.size > 0) { stats.skip++; return; }
  }
  const buf = await fetchBuf(url);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, buf);
  stats.ok++;
  stats.bytes += buf.length;
}

// 任务清单
const tasks = [];
for (const g of groups) {
  for (const v of g.list) {
    if (v.status !== 200 || !v.pages || !v.pages.length) {
      log(`SKIP VOLUME ${g.key} ${v.vol} status=${v.status}`);
      continue;
    }
    const vdir = path.join(SRC, g.dir, String(v.vol));
    tasks.push({ dest: path.join(vdir, 'index.html'), url: `${BASE}/${g.remote}/${v.vol}/index.html` });
    for (const p of v.pages) {
      tasks.push({ dest: path.join(vdir, p.file), url: `${BASE}/${g.remote}/${v.vol}/${p.file}` });
    }
  }
}
log(`START tasks=${tasks.length} groups=${groups.map(g => g.key).join(',')}`);
console.log(`tasks=${tasks.length}`);

let cursor = 0;
let done = 0;
async function worker() {
  while (true) {
    const i = cursor++;
    if (i >= tasks.length) return;
    const t = tasks[i];
    try {
      await saveFile(t.dest, t.url);
    } catch (e) {
      stats.fail++;
      stats.fails.push({ url: t.url, err: String(e.message || e) });
      log(`FAIL ${t.url} ${e.message || e}`);
    }
    done++;
    if (done % 200 === 0) {
      const msg = `progress ${done}/${tasks.length} ok=${stats.ok} skip=${stats.skip} fail=${stats.fail} mb=${(stats.bytes / 1048576).toFixed(1)}`;
      console.log(msg);
      log(msg);
    }
  }
}

const t0 = Date.now();
await Promise.all(Array.from({ length: CONCURRENCY }, () => worker()));
const summary = { ...stats, total: tasks.length, seconds: Math.round((Date.now() - t0) / 1000) };
fs.writeFileSync(path.join(SRC, `_download_summary_${only}.json`), JSON.stringify(summary, null, 1), 'utf8');
log(`DONE ${JSON.stringify({ ...summary, fails: summary.fails.length })}`);
console.log('DONE', JSON.stringify({ ...summary, fails: summary.fails.length }));
