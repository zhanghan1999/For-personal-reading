import fs from 'node:fs';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
const base = 'https://ghfast.top/https://raw.githubusercontent.com/RedRevolution1949/marx-lenin-stalin-mao/main/';
const files = [
  ['斯大林全集/新编《斯大林全集》全20卷正卷（诸夏怀斯社版）.pdf', '.tools/sources/stalin/pdf/斯大林全集_正卷20卷.pdf'],
  ['斯大林全集/新编《斯大林全集》全10卷档案附卷（诸夏怀斯社版）.pdf', '.tools/sources/stalin/pdf/斯大林全集_档案附卷10卷.pdf'],
];
for (const [p, dest] of files) {
  const url = base + p.split('/').map(encodeURIComponent).join('/');
  try {
    const t0 = Date.now();
    const r = await fetch(url, { headers:{'User-Agent':'Mozilla/5.0'}, signal: AbortSignal.timeout(900000) });
    if (!r.ok) { console.log('FAIL', r.status, p); continue; }
    fs.mkdirSync(dest.replace(/[\\/][^\\/]+$/,''), { recursive: true });
    await pipeline(Readable.fromWeb(r.body), fs.createWriteStream(dest));
    const mb = fs.statSync(dest).size/1048576;
    console.log('OK', dest, mb.toFixed(1)+'MB', ((mb*1048576/((Date.now()-t0)/1000))/1048576).toFixed(2)+'MB/s');
  } catch(e) { console.log('ERR', p, e.message); }
}
