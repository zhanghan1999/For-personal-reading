// fetch_images.mjs — 扫描已下载的全集 HTML，补齐其引用的本地图片
import fs from 'node:fs';
import path from 'node:path';

const SRC = '.tools/sources';
const groups = [
  { dir: 'mew', remote: 'MEW-ZH' },
  { dir: 'mea', remote: 'MEA' },
  { dir: 'lenin', remote: 'LENIN' },
];

let missing = 0, copied = 0, failed = 0, bytes = 0;
const jobs = [];

for (const g of groups) {
  const root = path.join(SRC, g.dir);
  if (!fs.existsSync(root)) continue;
  for (const vol of fs.readdirSync(root)) {
    const vdir = path.join(root, vol);
    if (!fs.statSync(vdir).isDirectory()) continue;
    for (const f of fs.readdirSync(vdir)) {
      if (!/\.html?$/i.test(f)) continue;
      const raw = fs.readFileSync(path.join(vdir, f), 'utf8');
      for (const m of raw.matchAll(/<img[^>]+src=["']([^"']+)["']/gi)) {
        const src = m[1];
        if (/^(https?:|data:|\/\/)/i.test(src)) continue;
        const rel = src.split('?')[0];
        const dest = path.join(vdir, rel);
        if (fs.existsSync(dest)) continue;
        jobs.push({ dest, url: `https://marx-zh-cn.github.io/docs/${g.remote}/${vol}/${rel.split('/').map(encodeURIComponent).join('/')}` });
      }
    }
  }
}

const uniq = new Map();
for (const j of jobs) uniq.set(j.dest, j);
const list = [...uniq.values()];
console.log('image refs to fetch:', list.length);

let cursor = 0;
async function worker() {
  while (true) {
    const i = cursor++;
    if (i >= list.length) return;
    const { dest, url } = list[i];
    let ok = false;
    for (let a = 0; a < 4 && !ok; a++) {
      try {
        const r = await fetch(url, { signal: AbortSignal.timeout(40000) });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const buf = Buffer.from(await r.arrayBuffer());
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.writeFileSync(dest, buf);
        bytes += buf.length; copied++; ok = true;
      } catch (e) {
        if (a === 3) { failed++; console.log('FAIL', url, e.message); }
        else await new Promise(res => setTimeout(res, 400 * (a + 1)));
      }
    }
  }
}
await Promise.all(Array.from({ length: 8 }, () => worker()));
console.log(JSON.stringify({ refs: list.length, copied, failed, mb: +(bytes / 1048576).toFixed(1) }));
