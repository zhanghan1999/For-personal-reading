// sogousearch.mjs — 通过代理搜搜狗，打印结果标题+URL
const [, , query] = process.argv;
if (!query) { console.error('usage: node --use-env-proxy sogousearch.mjs "<q>"'); process.exit(1); }
const url = 'https://www.sogou.com/web?query=' + encodeURIComponent(query);
const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0', 'Accept-Language': 'zh-CN,zh;q=0.9' };
const resp = await fetch(url, { headers, signal: AbortSignal.timeout(40000) });
console.error('HTTP', resp.status, resp.url);
const t = await resp.text();
console.error('len', t.length);
const re = /<h3[^>]*>[\s\S]*?<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
let m, n = 0;
const out = [];
while ((m = re.exec(t)) !== null && n < 15) {
  const title = m[2].replace(/<[^>]+>/g, '').trim();
  if (title) out.push(`- ${title}\n  ${m[1].slice(0, 120)}`);
  n++;
}
if (!out.length) {
  console.log('NO matches; head:');
  console.log(t.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 500));
} else {
  console.log(out.join('\n'));
}
