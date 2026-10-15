// ia_login3.mjs — 完整登录：PHPSESSID → CSRF → /services/account/login/ → 借阅 → 下载
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
const hdr = (extra = {}) => ({ 'User-Agent': UA, Origin: 'https://archive.org', Referer: 'https://archive.org/account/login', ...(Object.keys(cookies).length ? { Cookie: ck() } : {}), ...extra });

// 带重试的 fetch（代理不稳）
async function fetchR(url, init = {}, tries = 5) {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const ctl = new AbortController();
      const to = setTimeout(() => ctl.abort(), (init.signal_timeout || 30000));
      const r = await fetch(url, { ...init, signal: ctl.signal });
      clearTimeout(to);
      return r;
    } catch (e) {
      lastErr = e;
      console.error('retry', i + 1, url.slice(0, 60), e.cause?.code || e.code || e.message);
      await new Promise(r => setTimeout(r, 1500 * (i + 1)));
    }
  }
  throw lastErr;
}

// 1) /account/login -> 302 + PHPSESSID，然后跟随
const g = await fetchR('https://archive.org/account/login', { headers: hdr(), redirect: 'manual' });
absorb(g);
console.log('[1] /account/login', g.status, 'loc:', g.headers.get('location'), 'cookies:', Object.keys(cookies).join(','));
if (g.status === 302) {
  const loc = g.headers.get('location');
  const u2 = loc.startsWith('http') ? loc : 'https://archive.org' + loc;
  const g2 = await fetchR(u2, { headers: hdr(), redirect: 'manual' });
  absorb(g2);
  console.log('[1b] follow ->', u2.slice(0, 60), g2.status, 'cookies:', Object.keys(cookies).join(','));
}

// 2) CSRF
const cr = await fetchR('https://archive.org/services/csrf-token', { headers: hdr() });
const cj = await cr.json();
const csrf = (cj && cj.value && cj.value.token) || '';
console.log('[2] csrf status', cr.status, 'token len', csrf.length);
absorb(cr);

// 3) 登录（试两种 body 形式）
const attempts = [
  JSON.stringify({ username: creds.email, password: creds.password, remember: true, t: csrf }),
  'username=' + encodeURIComponent(creds.email) + '&password=' + encodeURIComponent(creds.password) + '&remember=true&t=' + encodeURIComponent(csrf),
];
for (let i = 0; i < attempts.length; i++) {
  const ct = i === 0 ? 'application/json' : 'application/x-www-form-urlencoded';
  const lp = await fetchR('https://archive.org/services/account/login/', {
    method: 'POST',
    headers: hdr({ 'Content-Type': ct, 'Accept': 'application/json', 'X-CSRFToken': csrf }),
    body: attempts[i],
  });
  const lj = await lp.text();
  console.log('[3] login attempt', i, 'status', lp.status, 'body:', lj.slice(0, 400).replace(/\s+/g, ' '));
  absorb(lp);
  if (lp.ok || /success.?[:=]\s*true|logged-in-user/i.test(lj)) break;
}

// 4) 验证
const ac = await fetchR('https://archive.org/account', { headers: hdr() });
const act = await ac.text();
const logged = /logout|Account Settings/i.test(act);
console.log('[4] account', ac.status, 'logged-in:', logged, 'cookies:', Object.keys(cookies).join(','));

if (logged) {
  // 5) 借阅
  const br = await fetchR('https://archive.org/services/loans/loan/?action=borrow&identifier=' + ID, {
    method: 'POST', headers: hdr(),
  });
  const bt = await br.text();
  console.log('[5] borrow', br.status, bt.slice(0, 400).replace(/\s+/g, ' '));
  absorb(br);
  try { const bj = JSON.parse(bt); if (bj && bj.token) cookies['loan-' + ID] = bj.token; } catch (e) {}
  // 6) 下载
  const dl = await fetchR('https://archive.org/download/' + ID + '/' + ID + '_djvu.txt', { headers: hdr() }, 6);
  console.log('[6] download', dl.status);
  if (dl.ok) {
    const buf = Buffer.from(await dl.arrayBuffer());
    fs.writeFileSync(OUT, buf);
    console.log('saved', OUT, buf.length, 'bytes');
  } else {
    console.log('download err:', (await dl.text()).slice(0, 300));
  }
} else {
  console.log('登录未成功。');
}
