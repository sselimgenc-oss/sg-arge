/* Tema testleri (Playwright + Chromium): node ofis/test/tema.test.js
   Kapsam: varsayılan klasik tema, İzometrik seçimi ve kalıcılığı (localStorage, ?tema=), bölge→oda eşleşmesi
   (tıklanan bölge doğru odayı açar; oda içi görünüm ve panel iki temada ortaktır), binaya geri dönüş,
   rozet verisi (ornek_durum.json sabit fikstürüyle elle hesaplanmış altın değerler). */
'use strict';
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..', '..');
const ornek = require('../ornek_durum.json');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.webp': 'image/webp' };
let bad = 0;
const ok = (n, c, x) => { if (!c) bad++; console.log((c ? 'OK   ' : 'FAIL ') + n + (x !== undefined && x !== '' ? ' → ' + x : '')); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* altın değerler: ornek_durum.json'dan elle hesaplanır (Off.init() ilk durumu; hiçbir olay işlenmeden önce).
   ornek_durum.json'da trader.saglik hiç yok (yalnız gerçek veride gelir), bu yüzden rozet likidasyon-uzaklığına
   düşer; açık işlemi olmayan trader "veri yok" sayılır (yeşile düşürülmez — sahte "sağlıklı" uydurulmaz). */
const odaIds = ornek.traderlar.filter(t => t.kat === 'oda').map(t => t.id);
let YESIL = 0, SARI = 0, KIRMIZI = 0, VERIYOK = 0;
odaIds.forEach(id => {
  const ac = ornek.acik_islemler.filter(x => x.trader === id && x.lik_uzaklik != null);
  if (!ac.length) { VERIYOK++; return; }
  const worst = Math.min.apply(null, ac.map(x => x.lik_uzaklik));
  if (worst <= 10) KIRMIZI++; else if (worst <= 20) SARI++; else YESIL++;
});
const ODA_ROZET_BEKLENEN = ornek.katlar.oda.n + ' trader · 🟢' + YESIL + ' 🟡' + SARI + ' 🔴' + KIRMIZI + (VERIYOK ? ' · ' + VERIYOK + ' veri yok' : '');
let worstT = ornek.risk.tavanlar[0], worstR = 0;
ornek.risk.tavanlar.forEach(t => { const r = t.kullanim / t.tavan; if (r > worstR) { worstR = r; worstT = t; } });
const RISK_ISIK = worstR >= 0.999 ? '🔴' : worstR >= 0.75 ? '🟡' : '🟢';
const RISK_ROZET_BEKLENEN = RISK_ISIK + ' ' + worstT.ad + ' %' + Math.round(worstR * 100);
const getiri = (ornek.kasa.deger_usd / ornek.kasa.baslangic_usd - 1) * 100;
const FINANS_ROZET_BEKLENEN = '$' + ornek.kasa.deger_usd.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' · +' + getiri.toFixed(1) + '%';

const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  fs.readFile(path.join(root, p), (e, d) => { if (e) { r.writeHead(404); r.end('nf'); return; } r.writeHead(200, { 'content-type': (TYPES[path.extname(p)] || 'application/octet-stream') + '; charset=utf-8' }); r.end(d); });
}).listen(0, async () => {
  const base = 'http://localhost:' + srv.address().port + '/ofis/';
  const b = await chromium.launch();
  const errs = [];
  async function open(url, opt) {
    const ctx = await b.newContext(Object.assign({ viewport: { width: 1440, height: 900 } }, opt || {}));
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await pg.goto(base + (url || '?saat=15:40&durum=ornek')); await pg.waitForFunction('window.OFIS&&window.OFIS.ready');
    return { ctx, pg };
  }
  /* bölgenin ekran konumuna tıkla (clip-path yalnız o oda şeklinde isabetlidir; kutunun merkezi değil, çokgenin bbox merkezi kullanılır) */
  async function bolgeyeTikla(pg, id) {
    const geo = await pg.evaluate(id => {
      const b = OFIS.Tema.debug.bolgeler.find(x => x.oda === id);
      let x0 = 1, y0 = 1, x1 = 0, y1 = 0; b.poli.forEach(p => { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); });
      const r = document.querySelector('.izo-bolge[data-oda="' + id + '"]').getBoundingClientRect();
      return { fx: (x0 + x1) / 2, fy: (y0 + y1) / 2, r: { x: r.x, y: r.y, w: r.width, h: r.height } };
    }, id);
    await pg.mouse.click(geo.r.x + geo.fx * geo.r.w, geo.r.y + geo.fy * geo.r.h);
  }

  /* ---------- A. varsayılan tema ve seçim ---------- */
  let { ctx, pg } = await open();
  let t = await pg.evaluate(() => ({ tema: OFIS.Tema.get(), izo: document.getElementById('izoKap').hidden, kutu: document.body.classList.contains('tema-izo') }));
  ok('varsayılan tema klasik; izometrik kutu gizli', t.tema === 'klasik' && t.izo && !t.kutu, JSON.stringify(t));
  const webpYuklendi = await pg.evaluate(() => performance.getEntriesByType('resource').some(x => /ofis_izometrik_referans/.test(x.name)));
  ok('klasik temada referans görsel (webp) hiç indirilmez', !webpYuklendi);
  await ctx.close();

  ({ ctx, pg } = await open('?saat=15:40&durum=ornek&tema=izometrik'));
  t = await pg.evaluate(() => ({ tema: OFIS.Tema.get(), izo: document.getElementById('izoKap').hidden, sec: document.getElementById('temaSec').value }));
  ok('adres parametresiyle (?tema=izometrik) açılır, kutu görünür, ayarlardaki seçici eşleşir', t.tema === 'izometrik' && !t.izo && t.sec === 'izometrik', JSON.stringify(t));
  await sleep(300);
  const webpYuklendi2 = await pg.evaluate(() => performance.getEntriesByType('resource').some(x => /ofis_izometrik_referans/.test(x.name)));
  ok('izometrik temada referans görsel indirilir', webpYuklendi2);
  await ctx.close();

  /* ---------- B. tema seçimi kalıcılığı (localStorage; ayarlar penceresinden seçim) ---------- */
  ({ ctx, pg } = await open());
  await pg.click('#ayarBtn'); await sleep(150);
  await pg.selectOption('#temaSec', 'izometrik'); await sleep(150);
  t = await pg.evaluate(() => ({ tema: OFIS.Tema.get(), izo: document.getElementById('izoKap').hidden, ls: localStorage.getItem('sgofis.tema') }));
  ok('ayarlardan İzometrik seçilince hemen uygulanır ve localStorage\'a yazılır', t.tema === 'izometrik' && !t.izo && t.ls === 'izometrik', JSON.stringify(t));
  await pg.goto(pg.url().split('?')[0] + '?saat=15:40&durum=ornek'); await pg.waitForFunction('window.OFIS&&window.OFIS.ready');   // yeniden yükle, adres parametresi yok
  t = await pg.evaluate(() => ({ tema: OFIS.Tema.get(), izo: document.getElementById('izoKap').hidden }));
  ok('sayfa yeniden açılınca (adres parametresi yok) kayıtlı tema (izometrik) korunur', t.tema === 'izometrik' && !t.izo, JSON.stringify(t));
  await pg.click('#ayarBtn'); await sleep(150);
  await pg.selectOption('#temaSec', 'klasik'); await sleep(150);
  t = await pg.evaluate(() => ({ tema: OFIS.Tema.get(), izo: document.getElementById('izoKap').hidden, ls: localStorage.getItem('sgofis.tema') }));
  ok('Klasik\'e geri dönüş de kalıcı olur', t.tema === 'klasik' && t.izo && t.ls === 'klasik', JSON.stringify(t));
  await ctx.close();

  /* ---------- C. bölge → oda eşleşmesi: panel ortak veriden, ama görsel kendi temasında kalır (klasik piksel
     sahnesine geçilmez) — izometrik temada odaya girince #izoKap açık ve o odaya yakınlaşmış kalır, #tuval gizli. */
  ({ ctx, pg } = await open('?saat=15:40&durum=ornek&tema=izometrik'));
  const fitScale = await pg.evaluate(() => OFIS.Tema.debug.scale);
  for (const id of ['finans', 'risk', 'lab', 'arsiv', 'kapi', 'oda', 'makam']) {
    await bolgeyeTikla(pg, id); await sleep(700);
    const s = await pg.evaluate(() => ({ h: location.hash, active: OFIS.debug.mode.active, room: OFIS.debug.mode.room, izoHidden: document.getElementById('izoKap').hidden, tuvalVis: document.getElementById('tuval').style.visibility, scale: OFIS.Tema.debug.scale, kartGorunur: !document.getElementById('kartPanel').hidden || !document.getElementById('bilgi').hidden }));
    ok('bölge "' + id + '": doğru odayı açar, panel görünür, görsel KENDİ temasında kalır (izometrik açık+yakınlaşmış, piksel tuval gizli)', s.room === id && s.active && s.h === '#oda/' + id && !s.izoHidden && s.tuvalVis === 'hidden' && s.scale > fitScale && s.kartGorunur, JSON.stringify(s));
    await pg.click('#geriBtn'); await sleep(700);
    const back = await pg.evaluate(() => ({ active: OFIS.debug.mode.active, izoHidden: document.getElementById('izoKap').hidden, scale: OFIS.Tema.debug.scale }));
    ok('bölge "' + id + '" sonrası "← Bina" ile geri dönüş: izometrik görsel sığdırmaya döner (temalar karışmaz)', !back.active && !back.izoHidden && back.scale === 1, JSON.stringify(back));
  }
  await ctx.close();

  /* ---------- D. geri dönüş: Esc ve tarayıcı geri tuşu da izometrik görseli sığdırmaya döndürür (tuval hiç açılmaz) ---------- */
  ({ ctx, pg } = await open('?saat=15:40&durum=ornek&tema=izometrik'));
  await bolgeyeTikla(pg, 'lab'); await sleep(700);
  let tuvalHepGizliKaldi = (await pg.evaluate(() => document.getElementById('tuval').style.visibility)) === 'hidden';
  await pg.keyboard.press('Escape'); await sleep(200); await pg.keyboard.press('Escape'); await sleep(700);
  t = await pg.evaluate(() => ({ active: OFIS.debug.mode.active, izoHidden: document.getElementById('izoKap').hidden, tuvalVis: document.getElementById('tuval').style.visibility, scale: OFIS.Tema.debug.scale, h: location.hash }));
  ok('Esc ile binaya dönüş: izometrik görsel görünür kalır, sığdırmaya döner, tuval hiç açılmadı', !t.active && !t.izoHidden && t.tuvalVis === 'hidden' && t.scale === 1 && t.h === '' && tuvalHepGizliKaldi, JSON.stringify(t));
  await bolgeyeTikla(pg, 'oda'); await sleep(700);
  await pg.goBack(); await sleep(700);
  t = await pg.evaluate(() => ({ active: OFIS.debug.mode.active, izoHidden: document.getElementById('izoKap').hidden, scale: OFIS.Tema.debug.scale }));
  ok('tarayıcı geri tuşu da aynı şekilde izometrik görseli sığdırmaya döndürür', !t.active && !t.izoHidden && t.scale === 1, JSON.stringify(t));
  await ctx.close();

  /* ---------- E. rozet verisi (sentetik fikstür: ornek_durum.json; ilk durum, olay işlenmeden önce) ---------- */
  ({ ctx, pg } = await open('?saat=15:40&durum=ornek&tema=izometrik'));
  const r = await pg.evaluate(() => ({ finans: OFIS.Tema.debug.rozet('finans'), risk: OFIS.Tema.debug.rozet('risk'), oda: OFIS.Tema.debug.rozet('oda'), lab: OFIS.Tema.debug.rozet('lab'), arsiv: OFIS.Tema.debug.rozet('arsiv'), makam: OFIS.Tema.debug.rozet('makam') }));
  ok('Finans rozeti: kasa değeri ve getiri (ornek_durum.json altın değeri)', r.finans.t === FINANS_ROZET_BEKLENEN, JSON.stringify(r.finans) + ' beklenen=' + FINANS_ROZET_BEKLENEN);
  ok('Risk rozeti: en kötü tavan (Kaldıraç %80, ornek_durum.json altın değeri)', r.risk.t === RISK_ROZET_BEKLENEN, JSON.stringify(r.risk) + ' beklenen=' + RISK_ROZET_BEKLENEN);
  ok('Oda rozeti: 14 trader, likidasyon-uzaklığına göre 🟢/🟡/🔴 dağılımı (altın değeri)', r.oda.t === ODA_ROZET_BEKLENEN, JSON.stringify(r.oda) + ' beklenen=' + ODA_ROZET_BEKLENEN);
  ok('Lab rozeti: veri yaşı metni (bilinmiyor değil)', typeof r.lab.t === 'string' && r.lab.t.length > 0 && r.lab.c !== 'bil');
  ok('Arşiv rozeti: veri_kalitesi.deger metnini kullanır', r.arsiv.t === '48.210 satır', JSON.stringify(r.arsiv));
  ok('Makam rozeti: hafta/toplam', r.makam.t.indexOf('hafta 5/12') === 0, JSON.stringify(r.makam));
  /* gri oda (henüz verisi olmayan): gerçek veri senaryosunda rozet "gri" metnini gösterir, sayı uydurmaz */
  const griOrnek = { oda_durum: { finans: { gri: true, metin: 'sanal izleme başlamadı' } } };
  const griSonuc = await pg.evaluate(gdata => {
    const eski = OFIS.data.oda_durum; OFIS.data.oda_durum = gdata.oda_durum;
    const r = OFIS.Tema.debug.rozet('finans'); OFIS.data.oda_durum = eski; return r;
  }, griOrnek);
  ok('Finans gri (veri yok) durumunda rozet gri metni gösterir, sayı uydurmaz', griSonuc.t === 'sanal izleme başlamadı' && griSonuc.c === 'gri', JSON.stringify(griSonuc));
  /* Sekreterlik rozeti: onkayit_kasasi.surum alanından (SEMA.md §8; ornek_durum.json altın değeri) */
  const sekreterlik = await pg.evaluate(() => OFIS.Tema.debug.rozet('sekreterlik'));
  ok('Sekreterlik rozeti: onkayit_kasasi.surum metnini taşır', sekreterlik.t === 'ön kayıt ' + ornek.onkayit_kasasi.surum, JSON.stringify(sekreterlik));
  /* gerçek veride trader.saglik.isik geldiğinde (SEMA.md'de olmayan ama gercek.js'in izleme/durum.json'dan aynen
     taşıdığı alan) Oda rozeti likidasyon-uzaklığı yerine onu kullanır: gerçek sağlık sinyali varken uydurma yok */
  const saglikSonuc = await pg.evaluate(() => {
    const st = OFIS.Office.state(), odaIds = Object.keys(st.traders).filter(id => st.traders[id].kat === 'oda');
    const eski = odaIds.map(id => st.traders[id].saglik);
    odaIds.forEach((id, i) => { st.traders[id].saglik = { isik: i === 0 ? 'kirmizi' : i === 1 ? 'sari' : 'yesil' }; });
    const r = OFIS.Tema.debug.rozet('oda');
    odaIds.forEach((id, i) => { st.traders[id].saglik = eski[i]; });
    return r;
  });
  ok('Oda rozeti: gerçek sağlık verisi (saglik.isik) geldiğinde onu kullanır, likidasyona dönmez', /🔴1/.test(saglikSonuc.t) && /🟡1/.test(saglikSonuc.t), JSON.stringify(saglikSonuc));
  await ctx.close();

  /* ---------- F. canlılık: örnek akıştaki olaylar odaları yumuşakça parlatır ve odalar arası balon uçurur
     (aynı olay motoru office.js'den; figür yürütme yok — bu sürüm 1'in kapsamı dışında, ayrıca not düşülür).
     Balon kısa ömürlü olduğundan doğrudan "şu an var" yerine MutationObserver ile "en az bir kez görüldü" izlenir. */
  ({ ctx, pg } = await open('?saat=15:40&durum=ornek&tema=izometrik&hiz=8'));   // akışı hızlandır, olay çabuk gelsin
  await pg.evaluate(() => {
    window.__balon = 0;
    new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(n => { if (n.classList && n.classList.contains('izo-balon')) window.__balon++; }))).observe(document.getElementById('izoBalonlar'), { childList: true });
  });
  await sleep(4500);
  const balonSayisi = await pg.evaluate(() => window.__balon);
  ok('canlılık: örnek akıştaki olaylar (kapı geçişi, terfi, bildirim…) oda-arası balon olarak görünür', balonSayisi > 0, 'n=' + balonSayisi);
  await ctx.close();

  /* ---------- G. iki tema arasında geçiş sırasında JS hatası yok ---------- */
  ok('konsol/sayfa hatası yok', errs.length === 0, errs.join(' | '));

  await b.close(); srv.close();
  console.log(bad ? ('\n' + bad + ' test başarısız') : '\nTüm testler geçti.');
  process.exit(bad ? 1 : 0);
});
