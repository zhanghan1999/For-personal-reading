// ia_debug.mjs — 调试 archive.org /login 表单结构
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';
const r = await fetch('https://archive.org/login', { headers: { 'User-Agent': UA }, redirect: 'manual', signal: AbortSignal.timeout(30000) });
console.log('status', r.status, 'len', (await r.clone().text()).length);
for (const c of r.headers.getSetCookie()) console.log('SETCOOKIE:', c.slice(0, 100));
const t = await r.text();
console.log('---- forms ----');
const forms = [...t.matchAll(/<form[^>]*>([\s\S]*?)<\/form>/g)];
console.log('forms:', forms.length);
for (const f of forms) {
  const action = (f[0].match(/action="([^"]+)"/) || [])[1];
  const method = (f[0].match(/method="([^"]+)"/i) || [])[1];
  console.log('FORM action=', action, 'method=', method);
  for (const inp of f[1].matchAll(/<(input|button|textarea)[^>]*>/g)) {
    console.log('   ', inp[0].slice(0, 150));
  }
}
console.log('---- csrf-ish ----');
console.log((t.match(/name="(csrf[a-z_]*|token|xsrf[a-z_]*)"[^>]*value="([^"]+)"/i) || ['no match']).slice(0, 4));
console.log('---- title ----');
console.log((t.match(/<title>([^<]*)<\/title>/) || [])[1]);
