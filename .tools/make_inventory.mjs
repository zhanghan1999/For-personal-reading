// make_inventory.mjs — 根据下载索引与本地文件生成全集群书库存档案
import fs from 'node:fs';
import path from 'node:path';

const SRC = '.tools/sources';
const idx = JSON.parse(fs.readFileSync(path.join(SRC, '_collected_index.json'), 'utf8'));

function dirSize(dir) {
  let total = 0, files = 0;
  const walk = (d) => {
    if (!fs.existsSync(d)) return;
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else { total += fs.statSync(p).size; files++; }
    }
  };
  walk(dir);
  return { total, files };
}

const groups = [
  { key: 'mew', label: '马克思恩格斯全集（中文第一版，第1卷为第二版）', remote: 'MEW-ZH', dir: 'mew', list: idx.mew, edition: '《马克思恩格斯全集》中文第一版（人民出版社）' },
  { key: 'mea', label: '马克思恩格斯文集 / 全集第二版零卷', remote: 'MEA', dir: 'mea', list: idx.mea, edition: '《马克思恩格斯文集》（10卷本，2009）＋全集第二版第26、44卷' },
  { key: 'lenin', label: '列宁全集（中文第二版）', remote: 'LENIN', dir: 'lenin', list: idx.lenin, edition: '《列宁全集》中文第二版（人民出版社）' },
];

const lines = [];
lines.push('# 全集群书库存档案（自动生成）');
lines.push('');
lines.push(`生成时间：${new Date().toISOString()}  `);
lines.push(`数据源：中文马克思主义文库镜像 https://marx-zh-cn.github.io/docs/  `);
lines.push(`本地位置：\`.tools/sources/{mew,mea,lenin}/<卷号>/\`（raw HTML，未加工）`);
lines.push('');

const summary = [];
for (const g of groups) {
  const base = path.join(SRC, g.dir);
  const { total, files } = dirSize(base);
  const vols = g.list.filter(v => v.status === 200 && v.pages && v.pages.length);
  const pages = vols.reduce((s, v) => s + v.pages.length, 0);
  summary.push({ key: g.key, label: g.label, vols: vols.length, volRange: `${Math.min(...vols.map(v=>v.vol))}-${Math.max(...vols.map(v=>v.vol))}`, pages, files, mb: +(total / 1048576).toFixed(1) });

  lines.push(`## ${g.label}`);
  lines.push('');
  lines.push(`- 版本：${g.edition}`);
  lines.push(`- 卷数：**${vols.length}** 卷；篇目（正文页）：**${pages}** 篇；本地文件 ${files} 个，${(total / 1048576).toFixed(1)} MB`);
  const missing = g.list.filter(v => v.status !== 200 || !v.pages || !v.pages.length).map(v => v.vol);
  if (missing.length) lines.push(`- 源站缺失卷：${missing.join('、')}`);
  lines.push('');
  lines.push('| 卷 | 标题（年代） | 篇数 | 本地 |');
  lines.push('|---|---|---|---|');
  for (const v of g.list) {
    if (v.status !== 200 || !v.pages || !v.pages.length) {
      lines.push(`| ${v.vol} | （源站 404） | 0 | — |`);
      continue;
    }
    const t = (v.title || '').replace(/\|/g, '/');
    lines.push(`| ${v.vol} | ${t} | ${v.pages.length} | \`.tools/sources/${g.dir}/${v.vol}/\` |`);
  }
  lines.push('');
}

lines.push('## 斯大林全集');
lines.push('');
const stalinDir = path.join(SRC, 'stalin/pdf');
const st = dirSize(stalinDir);
lines.push(`- 本地文件 ${st.files} 个，${(st.total / 1048576).toFixed(1)} MB（**文字版 PDF**，可直接抽文本，非扫描件）`);
if (fs.existsSync(stalinDir)) {
  for (const f of fs.readdirSync(stalinDir)) lines.push(`  - \`${f}\`（${(fs.statSync(path.join(stalinDir, f)).size / 1048576).toFixed(1)} MB）`);
}
const tocPath = path.join(SRC, 'stalin/_toc.json');
if (fs.existsSync(tocPath)) {
  const toc = JSON.parse(fs.readFileSync(tocPath, 'utf8'));
  const vols = toc.volumes.filter(v => /第.+卷/.test(v.title) && !/总目录|告读者/.test(v.title));
  const arts = vols.reduce((s, v) => s + v.articles.length, 0);
  lines.push(`- 书签结构：**${vols.length}** 卷 / **${arts}** 篇 / PDF 共 ${toc.pages_total} 页；目录已抽为 \`stalin/_toc.json\``);
  lines.push('');
  lines.push('| 卷 | 标题（年代） | 书签篇数 | 起始页 |');
  lines.push('|---|---|---|---|');
  for (const v of vols) lines.push(`| ${v.title.slice(0, 2).replace(/^0/, '')} | ${v.title.replace(/\|/g, '/')} | ${v.articles.length} | ${v.start} |`);
}
lines.push('');
lines.push('> 说明：斯大林全集中文 HTML 全文源（marxists.org）本机不可达；已取得诸夏怀斯社《新编斯大林全集》正卷20卷与档案附卷10卷。前 13 卷为人民出版社 1953 年起中文版原卷，14—20 卷为该社续编。');
lines.push('');

fs.writeFileSync(path.join(SRC, 'COLLECTED.md'), lines.join('\n'), 'utf8');
fs.writeFileSync(path.join(SRC, '_collected_summary.json'), JSON.stringify(summary, null, 1), 'utf8');
console.log(JSON.stringify(summary, null, 1));
