// proxy_fetch.mjs — 通过本机 Clash 代理(127.0.0.1:7890)抓取 URL。
// 用法:
//   node --use-env-proxy proxy_fetch.mjs <url>            # 打印正文(截断)
//   node --use-env-proxy proxy_fetch.mjs <url> <outfile>  # 保存响应体到文件(二进制安全)
//   node --use-env-proxy proxy_fetch.mjs <url> <outfile> -t  # 保存为文本
const [,, url, outfile, mode] = process.argv;
if (!url) { console.error('usage: node --use-env-proxy proxy_fetch.mjs <url> [outfile] [-t]'); process.exit(1); }
const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' };
const resp = await fetch(url, { headers, redirect: 'follow', signal: AbortSignal.timeout(60000) });
console.error('HTTP', resp.status, resp.headers.get('content-type'), 'url:', resp.url);
if (!resp.ok) { console.error('not ok; body head:'); const t = await resp.text(); console.error(t.slice(0, 800)); process.exit(2); }
if (outfile) {
  const buf = Buffer.from(await resp.arrayBuffer());
  const fs = await import('node:fs');
  fs.writeFileSync(outfile, buf);
  console.error('saved', outfile, buf.length, 'bytes');
} else {
  const t = await resp.text();
  console.log(t.length > 4000 ? t.slice(0, 4000) + '\n...[truncated]' : t);
}
