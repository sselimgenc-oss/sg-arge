/* Replik ve veri sözleşmesi testi (yalnız Node, bağımlılık yok):  node ofis/test/replik.test.js
   Kural: süs replikleri veri gibi görünmez: rakam, adres, oran/yüzde, para ve yer tutucu içermez. */
'use strict';
const fs = require('fs'), path = require('path');
const dir = path.join(__dirname, '..');
const rd = f => fs.readFileSync(path.join(dir, f), 'utf8');
const R = JSON.parse(rd('replikler.json')), D = JSON.parse(rd('ornek_durum.json')), K = JSON.parse(rd('kadro.json')), OL = rd('OLAYLAR.md'), WORLD = rd('world.js');
let bad = 0;
const ok = (n, c, x) => { if (!c) bad++; console.log((c ? 'OK   ' : 'FAIL ') + n + (x ? ' → ' + x : '')); };

ok('replikler.json yapısı', Array.isArray(R.veri) && Array.isArray(R.suz) && R.veri.every(v => v.olay_turu && v.rol && typeof v.sablon === 'string') && R.suz.every(s => s.rol && typeof s.metin === 'string'));

const KOTU = [[/\d/, 'rakam'], [/0x/i, 'adres'], [/[%$€₺]/, 'oran/para işareti'], [/[{}]/, 'yer tutucu'], [/\b(adres|oran|yüzde|yuzde)/i, 'adres/oran sözcüğü'], [/[0-9a-f]{6,}/i, 'onaltılık dizi']];
const kotu = [];
R.suz.forEach(s => KOTU.forEach(([re, ad]) => { if (re.test(s.metin)) kotu.push('"' + s.metin + '" (' + ad + ')'); }));
ok('süs replikleri: rakam, adres, oran, para, yer tutucu yok (n=' + R.suz.length + ')', kotu.length === 0, kotu.join(' | '));
ok('süs replikleri tekil', new Set(R.suz.map(s => s.rol + '|' + s.metin)).size === R.suz.length);

const yer = new Set(R.yer_tutucular), bilinmeyen = [];
R.veri.forEach(v => (v.sablon.match(/\{(\w+)\}/g) || []).forEach(m => { if (!yer.has(m.slice(1, -1))) bilinmeyen.push(v.olay_turu + ':' + m); }));
ok('veri şablonlarında yalnız bilinen yer tutucular', bilinmeyen.length === 0, bilinmeyen.join(', '));

const turler = [...new Set(D.olaylar.map(e => e.tur))];
const eksik = turler.filter(t => t !== 'sistem' && !R.veri.some(v => v.olay_turu === t));
ok('her olay türü için en az bir veri repliği', eksik.length === 0, eksik.join(', '));

const md = [...OL.matchAll(/^\| `([a-z_]+)` \|/gm)].map(m => m[1]).filter(t => t !== 'sistem');
const sadeceMd = md.filter(t => !turler.includes(t)), sadeceVeri = turler.filter(t => t !== 'sistem' && !md.includes(t));
ok('OLAYLAR.md\'deki her olay türü örnek veride en az bir kez tetiklenir (n=' + md.length + ')', sadeceMd.length === 0, sadeceMd.join(', '));
ok('örnek verideki her olay türü OLAYLAR.md\'de açıklı', sadeceVeri.length === 0, sadeceVeri.join(', '));
const isaretli = [...OL.matchAll(/^\| `([a-z_]+)` \|[^\n]*\n/gm)].filter(m => !/zarf|not|ok/i.test(m[0]));
const mdIsaret = (OL.split('## İletişim işaretleri')[1] || '');
ok('OLAYLAR.md: iletişim işareti eşlemesi bölümü var ve her olay türü orada geçer', md.every(t => mdIsaret.indexOf('`' + t + '`') >= 0), md.filter(t => mdIsaret.indexOf('`' + t + '`') < 0).join(', '));

const ids = D.olaylar.map(e => e.id);
ok('olay_id: her olayda var ve tekil', ids.every(Boolean) && new Set(ids).size === ids.length);
ok('her olayda kural var', D.olaylar.every(e => typeof e.kural === 'string' && e.kural.length > 0));
ok('her trader\'da kat_olay (id, kural, zaman)', D.traderlar.filter(t => ['lab', 'aday', 'oda', 'kontrol'].includes(t.kat)).every(t => t.kat_olay && t.kat_olay.id && t.kat_olay.kural && !isNaN(Date.parse(t.kat_olay.zaman))));
ok('adresler uydurma ve "örnek" işaretli', D.traderlar.every(t => /^0xAAAA…\d{4}$/.test(t.adres) && t.ornek === true));

const roles = new Set(Object.keys(K.calisanlar).map(id => id.replace(/\d$/, '').replace(/^haberlesme$/, 'haber')));
const sRol = new Set(R.suz.map(s => s.rol)), vRol = new Set(R.veri.map(s => s.rol));
const rolEksik = [...roles, 'trader', 'obje'].filter(r => !sRol.has(r));
ok('her rol için süs repliği (çalışan rolleri + trader + obje)', rolEksik.length === 0, rolEksik.join(', '));
ok('veri replik rolleri geçerli', [...vRol].every(r => roles.has(r) || r === 'trader'), [...vRol].filter(r => !(roles.has(r) || r === 'trader')).join(', '));

const roomIds = [...WORLD.matchAll(/\{ id: '(\w+)'(?:, wall: \d+)?, ad: '/g)].map(m => m[1]).filter(r => r !== 'bahce');
ok('kadro.json: 14 odanın tamamı var (adı, yapar, yapmaz)', roomIds.length === 14 && roomIds.every(r => K.odalar[r] && K.odalar[r].ad && K.odalar[r].yapar && K.odalar[r].yapmaz), roomIds.join(','));
const nes = Object.keys(K.nesneler).reduce((m, k) => { const r = k.split('.')[0]; m[r] = (m[r] || 0) + 1; return m; }, {});
ok('kadro.json: oda başına en az 3 nesne tanımı', roomIds.every(r => (nes[r] || 0) >= 3), JSON.stringify(nes));
const objIds = [...new Set([...WORLD.matchAll(/'([a-z]+\.[a-z_]+\d?)'/g)].map(m => m[1]).filter(i => roomIds.includes(i.split('.')[0])))];
ok('dünyadaki her tıklanabilir nesnenin kadro.json tanımı var', objIds.every(i => K.nesneler[i]), objIds.filter(i => !K.nesneler[i]).join(', '));
ok('hiçbir oda 3\'ten az tıklanabilir nesne taşımıyor', roomIds.every(r => new Set(objIds.filter(i => i.startsWith(r + '.'))).size >= 3), roomIds.filter(r => new Set(objIds.filter(i => i.startsWith(r + '.'))).size < 3).join(', '));

console.log(bad ? '\n' + bad + ' test başarısız' : '\nhepsi geçti');
process.exit(bad ? 1 : 0);
