// googlesearch.mjs — 通过代理搜 Google 基础版(gbv=1)，打印结果
const [, , query] = process.argv;
if (!query) { console.error('usage: node --use-env-proxy googlesearch.mjs "<q>"'); process.exit(1); }
const url = 'https://www.google.com/search?q=' + encodeURIComponent(query) + '&gbv=1&hl=zh-CN&num=20';
const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' };
const resp = await fetch(url, { headers, signal: AbortSignal.timeout(40000) });
console.error('HTTP', resp.status, resp.url);
const t = await resp.text();
console.error('len', t.length);
// gbv=1 结果: <h3 class="r"><a href="URL">标题</a></h3> ... <div class="s">摘要
const re = /<h3[^>]*class="r"[^>]*><a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a><\/h3>/g;
let m, n = 0;
const out = [];
while ((m = re.exec(t)) !== null && n < 20) {
  const title = m[2].replace(/<[^>]+>/g, '').trim();
  out.push(`- ${title}\n  ${m[1].slice(0, 160)}`);
  n++;
}
if (!out.length) {
  console.log('NO matches; text head:');
  console.log(t.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 700));
} else {
  console.log(out.join('\n'));
}
