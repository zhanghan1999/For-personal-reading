// ia_getbook.mjs — 登录 archive.org → 借阅《Inside Red China》(bwb_S0-CDJ-933) → 下载全文 djvu.txt。
// 走本机 Clash 代理(127.0.0.1:7890)，凭据从 _ia_creds.json 读取（gitignore 已忽略）。
import fs from 'node:fs';

const creds = JSON.parse(fs.readFileSync('C:/导师文集/.tools/sources/snow/红区内幕/_ia_creds.json', 'utf8'));
const ID = 'bwb_S0-CDJ-933';
const OUT = 'C:/导师文集/.tools/sources/snow/红区内幕/Inside_Red_China_1939_djvu.txt';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';

let cookies = {};
function ck() { return Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; '); }
function absorb(resp) {
  let setc = [];
  try { setc = resp.headers.getSetCookie(); } catch (e) { setc = (resp.headers.get('set-cookie') || '').split(/,(?=\s*[A-Za-z_][^=]*=)/); }
  for (const c of setc) { const m = c.match(/^([^=]+)=([^;]*)/); if (m) cookies[m[1].trim()] = m[2].trim(); }
}
const opt = (extra = {}) => ({ headers: { 'User-Agent': UA, ...(Object.keys(cookies).length ? { Cookie: ck() } : {}) }, signal: AbortSignal.timeout(40000), ...extra });

// 1) 先 GET 登录页拿 csrftoken cookie
const g = await fetch('https://archive.org/account/login', opt());
absorb(g);
console.log('[1] login page status', g.status, 'cookies:', Object.keys(cookies).join(','));

// 2) POST 登录
const lp = await fetch('https://archive.org/account/login', {
  ...opt({ method: 'POST', redirect: 'manual' }),
  headers: { 'User-Agent': UA, 'Content-Type': 'application/x-www-form-urlencoded', ...(Object.keys(cookies).length ? { Cookie: ck() } : {}) },
  body: `username=${encodeURIComponent(creds.email)}&password=${encodeURIComponent(creds.password)}`,
});
absorb(lp);
console.log('[2] login POST status', lp.status, 'loc:', lp.headers.get('location'));
if (lp.status === 302) { // 跟随一次跳转完成登录
  const loc = lp.headers.get('location');
  const locUrl = loc.startsWith('http') ? loc : 'https://archive.org' + loc;
  const l2 = await fetch(locUrl, opt());
  absorb(l2);
  console.log('[2b] follow ->', l2.status, 'cookies:', Object.keys(cookies).join(','));
}

// 3) 验证登录状态
const ac = await fetch('https://archive.org/account', opt());
const act = await ac.text();
console.log('[3] account page status', ac.status, 'logged-in:', /logout|Account Settings/i.test(act));

// 4) 借阅
const br = await fetch('https://archive.org/services/loans/loan/?action=borrow&identifier=' + ID, {
  ...opt({ method: 'POST' }),
  headers: { 'User-Agent': UA, ...(Object.keys(cookies).length ? { Cookie: ck() } : {}) },
});
const btxt = await br.text();
console.log('[4] borrow status', br.status, 'body:', btxt.slice(0, 400));
try { const bj = JSON.parse(btxt); if (bj.token) { const m = btxt.match(/token":"([^"]+)/); if (m) cookies['loan-' + ID] = m[1]; } } catch (e) {}
absorb(br);

// 5) 下载 djvu.txt
const dl = await fetch('https://archive.org/download/' + ID + '/' + ID + '_djvu.txt', opt({ redirect: 'follow' }));
console.log('[5] download status', dl.status, 'len:', dl.headers.get('content-length'));
const buf = Buffer.from(await dl.arrayBuffer());
fs.writeFileSync(OUT, buf);
console.log('saved', OUT, buf.length, 'bytes');
