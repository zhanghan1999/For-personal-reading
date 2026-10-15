// suda_check.mjs — 检查苏大数据库斯诺相关 PDF 大小
const base = 'https://marxism.suda.edu.cn';
const books = [
  ['尼姆韦尔斯(疑似续西行漫记)', '/_upload/article/files/37/1b/a553a3cc4b4fbd97f6df53ec4157/d12b4217-c5a2-4a56-a583-bdf81579ad49.pdf'],
  ['斯诺文集1复始之旅+2西行漫记', '/_upload/article/files/12/dd/23d2a8ee448382572553873c789d/a3aae1da-f1c1-460d-bc5a-8cb3057237ed.pdf'],
  ['斯诺文集第三部', '/_upload/article/files/18/c8/f2b4b23d44a191e2028d018aae71/fd4446cc-e271-4762-aa4e-5ecfd7e3911e.pdf'],
  ['斯诺文集第四部', '/_upload/article/files/11/7d/ecc8a7ef4a80916894d2b09d1dc6/21efbd6b-1302-4c49-b1c7-a9c96d6576cb.pdf'],
  ['斯诺文集3为亚洲而战+4大河彼岸', '/_upload/article/files/5c/2c/e7b08381462994ddc6962740d7f7/476dde22-b7fd-41a2-b7ea-f988cf79cdab.pdf'],
  ['红星照耀中国(人民文学)', '/_upload/article/files/ef/bc/eb7ff1c243c9b47ae067de751555/fafd02b8-1176-42d0-a6c8-8576d5cdff91.pdf'],
  ['斯诺在中国', '/_upload/article/files/5c/12/9b87cbd4473f846995c567e7b9e3/531325e7-a188-4c85-906a-cd750eedc328.pdf'],
];
for (const [name, path] of books) {
  try {
    const r = await fetch(base + path, { headers: { 'Range': 'bytes=0-1023' }, signal: AbortSignal.timeout(30000) });
    const b = await r.arrayBuffer();
    const cr = r.headers.get('content-range') || '';
    const size = cr.includes('/') ? cr.split('/')[1] : '?';
    const head = Buffer.from(b.slice(0, 5)).toString();
    console.log(name, '| status', r.status, '| size', size, '| head', head);
  } catch (e) {
    console.log(name, '| FAIL', e.cause?.code || e.message);
  }
}
