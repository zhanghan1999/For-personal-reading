// bingsearch.mjs — 通过 Clash 代理搜索 Bing 国际版，打印结果标题+URL。
// 用法: node --use-env-proxy bingsearch.mjs "<查询词>"
const [, , query] = process.argv;
if (!query) { console.error('usage: node --use-env-proxy bingsearch.mjs "<query>"'); process.exit(1); }
const url = 'https://www.bing.com/search?q=' + encodeURIComponent(query) + '&count=20&setlang=en';
const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' };
const resp = await fetch(url, { headers, signal: AbortSignal.timeout(40000) });
console.error('HTTP', resp.status, resp.url);
const t = await resp.text();
// bing 结果: <li class="b_algo">...<h2><a href="URL">TITLE</a></h2>...<p>SNIPPET</p>
const re = /<li class="b_algo">[\s\S]*?<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a><\/h2>[\s\S]*?<p[^>]*>([\s\S]*?)<\/p>/g;
let m, n = 0;
const out = [];
while ((m = re.exec(t)) !== null && n < 20) {
  const href = m[1];
  const title = m[2].replace(/<[^>]+>/g, '').trim();
  const snip = m[3].replace(/<[^>]+>/g, '').trim();
  out.push(`- ${title}\n  ${href}\n  ${snip.slice(0, 200)}`);
  n++;
}
if (!out.length) {
  console.log('NO b_algo matches; page len=', t.length);
  const i = t.search(/No results|<div id="b_results">/);
  console.log('marker at', i);
  console.log(t.slice(0, 600).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' '));
} else {
  console.log(out.join('\n'));
}
