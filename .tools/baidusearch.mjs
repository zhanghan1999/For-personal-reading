// baidusearch.mjs — 通过代理搜百度，打印结果标题+URL
const [, , query] = process.argv;
if (!query) { console.error('usage: node --use-env-proxy baidusearch.mjs "<q>"'); process.exit(1); }
const url = 'https://www.baidu.com/s?wd=' + encodeURIComponent(query) + '&rn=20';
const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' };
const resp = await fetch(url, { headers, signal: AbortSignal.timeout(40000) });
console.error('HTTP', resp.status, resp.url);
const t = await resp.text();
console.error('len', t.length);
// 百度结果: <h3 class="c-title ..."><a href="URL">标题</a>
const re = /<h3[^>]*class="[^"]*c-title[^"]*"[^>]*>[\s\S]*?<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
let m, n = 0;
const out = [];
while ((m = re.exec(t)) !== null && n < 20) {
  const title = m[2].replace(/<[^>]+>/g, '').trim();
  out.push(`- ${title}\n  ${m[1].slice(0, 140)}`);
  n++;
}
if (!out.length) {
  console.log('NO c-title matches; head:');
  console.log(t.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 600));
} else {
  console.log(out.join('\n'));
}
