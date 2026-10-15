// ia_login2.mjs — 完整登录流程：取 PHPSESSID → 取 CSRF → POST /services/account/login/ → 借阅 → 下载
import fs from 'node:fs';
const creds = JSON.parse(fs.readFileSync('C:/导师文集/.tools/sources/snow/红区内幕/_ia_creds.json', 'utf8'));
const ID = 'bwb_S0-CDJ-933';
const OUT = 'C:/导师文集/.tools/sources/snow/红区内幕/Inside_Red_China_1939_djvu.txt';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';

let cookies = {};
const ck = () => Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ');
function absorb(resp) {
  let setc = [];
  try { setc = resp.headers.getSetCookie(); } catch (e) { setc = (resp.headers.get('set-cookie') || '').split(/,(?=\s*[A-Za-z_][^=]*=)/); }
  for (const c of setc) { const m = c.match(/^([^=]+)=([^;]*)/); if (m) cookies[m[1].trim()] = m[2].trim(); }
}
const baseHdr = () => ({ 'User-Agent': UA, Origin: 'https://archive.org', Referer: 'https://archive.org/login', ...(Object.keys(cookies).length ? { Cookie: ck() } : {}) });

// 1) PHPSESSID
const g = await fetch('https://archive.org/login', { headers: baseHdr(), redirect: 'manual', signal: AbortSignal.timeout(30000) });
absorb(g);
console.log('[1] /login', g.status, 'cookies:', Object.keys(cookies).join(','));

// 2) 取 CSRF —— 正确端点 /services/csrf-token
let csrf = '';
for (const u of ['https://archive.org/services/csrf-token']) {
  try {
    const r = await fetch(u, { headers: baseHdr(), signal: AbortSignal.timeout(20000) });
    absorb(r);
    const t = await r.text();
    console.log('[2] csrf probe', u, '->', r.status, t.slice(0, 250).replace(/\s+/g, ' '));
    const m = t.match(/"token"\s*:\s*"([^"]+)"/);
    if (m) csrf = m[1];
    if (csrf) break;
  } catch (e) { console.log('[2] csrf probe fail', u, e.message); }
}
console.log('[2] csrf token:', csrf ? csrf.slice(0, 40) : '(none)');

// 3) 登录
const body = JSON.stringify({ username: creds.email, password: creds.password, remember: 'true', t: csrf });
const lp = await fetch('https://archive.org/services/account/login/', {
  method: 'POST', headers: { ...baseHdr(), 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
  body, signal: AbortSignal.timeout(30000),
});
const lj = await lp.text();
console.log('[3] login status', lp.status, 'body:', lj.slice(0, 500).replace(/\s+/g, ' '));
absorb(lp);

// 4) 验证
const ac = await fetch('https://archive.org/account', { headers: baseHdr(), signal: AbortSignal.timeout(30000) });
const act = await ac.text();
console.log('[4] account status', ac.status, 'logged-in:', /logout|Account Settings/i.test(act), 'cookies now:', Object.keys(cookies).join(','));

if (/logout|Account Settings/i.test(act)) {
  // 5) 借阅
  const br = await fetch('https://archive.org/services/loans/loan/?action=borrow&identifier=' + ID, {
    method: 'POST', headers: baseHdr(), signal: AbortSignal.timeout(30000),
  });
  const bt = await br.text();
  console.log('[5] borrow', br.status, bt.slice(0, 400).replace(/\s+/g, ' '));
  absorb(br);
  try { const bj = JSON.parse(bt); if (bj && bj.token) cookies['loan-' + ID] = bj.token; } catch (e) {}
  // 6) 下载
  const dl = await fetch('https://archive.org/download/' + ID + '/' + ID + '_djvu.txt', { headers: baseHdr(), signal: AbortSignal.timeout(120000) });
  console.log('[6] download status', dl.status);
  if (dl.ok) {
    const buf = Buffer.from(await dl.arrayBuffer());
    fs.writeFileSync(OUT, buf);
    console.log('saved', OUT, buf.length, 'bytes');
  } else {
    const err = await dl.text();
    console.log('download err body:', err.slice(0, 300));
  }
} else {
  console.log('登录未成功，停止。');
}
