// 抓取全部卷目录，统计篇目数，输出卷清单 JSON
import fs from 'node:fs';

const BASE = 'https://marx-zh-cn.github.io/docs';
const dec = (buf) => {
  let t = buf.toString('utf8');
  if (t.includes('\uFFFD')) t = new TextDecoder('gb18030').decode(buf);
  return t;
};

async function getIndex(path) {
  const url = BASE + path;
  const r = await fetch(url);
  if (!r.ok) return { url, status: r.status };
  const buf = Buffer.from(await r.arrayBuffer());
  const text = dec(buf);
  const title = (text.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [, ''])[1].trim();
  const links = [...text.matchAll(/<a\s[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)]
    .map(m => ({ href: m[1], text: m[2].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim() }))
    .filter(l => l.text);
  // 只保留指向本卷正文 html（不带 # 锚点）
  const pages = [];
  const seen = new Set();
  for (const l of links) {
    if (l.href.includes('#') || /^(https?:|mailto:|\/)/i.test(l.href)) continue;
    if (!/\.html?$/i.test(l.href)) continue;
    if (/index\.html?$/i.test(l.href)) continue;
    if (seen.has(l.href)) continue;
    seen.add(l.href);
    pages.push({ file: l.href, title: l.text });
  }
  return { url, status: r.status, title, pages, bytes: buf.length };
}

const out = { mew: [], mea: [], lenin: [] };

for (let v = 1; v <= 50; v++) {
  const res = await getIndex(`/MEW-ZH/${v}/index.html`);
  out.mew.push({ vol: v, ...res });
  console.log(`MEW ${v}: ${res.status} pages=${res.pages ? res.pages.length : 0} ${res.title || ''}`);
}
for (const v of [1,2,3,4,5,6,7,8,10,26]) {
  const res = await getIndex(`/MEA/${v}/index.html`);
  out.mea.push({ vol: v, ...res });
  console.log(`MEA ${v}: ${res.status} pages=${res.pages ? res.pages.length : 0} ${res.title || ''}`);
}
for (let v = 1; v <= 60; v++) {
  const res = await getIndex(`/LENIN/${v}/index.html`);
  out.lenin.push({ vol: v, ...res });
  console.log(`LENIN ${v}: ${res.status} pages=${res.pages ? res.pages.length : 0} ${res.title || ''}`);
}

fs.writeFileSync('.tools/sources/_collected_index.json', JSON.stringify(out, null, 1), 'utf8');
const sums = {
  mew: out.mew.reduce((s, x) => s + (x.pages ? x.pages.length : 0), 0),
  mea: out.mea.reduce((s, x) => s + (x.pages ? x.pages.length : 0), 0),
  lenin: out.lenin.reduce((s, x) => s + (x.pages ? x.pages.length : 0), 0),
};
console.log('\nTOTAL', JSON.stringify(sums));
