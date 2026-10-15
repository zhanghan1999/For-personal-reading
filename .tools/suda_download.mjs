// suda_download.mjs — 批量下载苏大斯诺相关 PDF
import fs from 'node:fs';
const base = 'https://marxism.suda.edu.cn';
const dir = 'C:/导师文集/.tools/sources/snow/_pdfs/';
fs.mkdirSync(dir, { recursive: true });
const books = [
  ['nym_wales.pdf', '/_upload/article/files/37/1b/a553a3cc4b4fbd97f6df53ec4157/d12b4217-c5a2-4a56-a583-bdf81579ad49.pdf'],
  ['snow_vol1_2.pdf', '/_upload/article/files/12/dd/23d2a8ee448382572553873c789d/a3aae1da-f1c1-460d-bc5a-8cb3057237ed.pdf'],
  ['snow_vol3.pdf', '/_upload/article/files/18/c8/f2b4b23d44a191e2028d018aae71/fd4446cc-e271-4762-aa4e-5ecfd7e3911e.pdf'],
  ['snow_vol4.pdf', '/_upload/article/files/11/7d/ecc8a7ef4a80916894d2b09d1dc6/21efbd6b-1302-4c49-b1c7-a9c96d6576cb.pdf'],
  ['snow_vol3_4.pdf', '/_upload/article/files/5c/2c/e7b08381462994ddc6962740d7f7/476dde22-b7fd-41a2-b7ea-f988cf79cdab.pdf'],
  ['red_star_renmin.pdf', '/_upload/article/files/ef/bc/eb7ff1c243c9b47ae067de751555/fafd02b8-1176-42d0-a6c8-8576d5cdff91.pdf'],
  ['snow_in_china.pdf', '/_upload/article/files/5c/12/9b87cbd4473f846995c567e7b9e3/531325e7-a188-4c85-906a-cd750eedc328.pdf'],
];
async function dl(name, path) {
  const dest = dir + name;
  if (fs.existsSync(dest) && fs.statSync(dest).size > 100000) { console.log('skip (exists)', name); return; }
  try {
    const r = await fetch(base + path, { signal: AbortSignal.timeout(600000) });
    if (!r.ok) { console.log('FAIL', name, r.status); return; }
    const buf = Buffer.from(await r.arrayBuffer());
    fs.writeFileSync(dest, buf);
    console.log('DONE', name, buf.length);
  } catch (e) { console.log('FAIL', name, e.cause?.code || e.message); }
}
for (const [name, path] of books) await dl(name, path);
console.log('ALL DONE');
