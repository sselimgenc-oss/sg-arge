/* Arayüz testleri (Playwright + Chromium):  node ofis/test/ui.test.js
   Kapsam: oda içi görünüm ve adres yönlendirmesi, bilgi kutusu, tıklanabilir kişiler/nesneler, ad değiştirme (saklama, dışa/içe aktarma),
   olay yokken çizim döngüsünün durması, hızlı olay kuyruğunda durum tutarlılığı, iletişim işaretleri, performans körlüğü, yasal ibare, telefon. */
'use strict';
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..', '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.md': 'text/plain' };
let bad = 0;
const ok = (n, c, x) => { if (!c) bad++; console.log((c ? 'OK   ' : 'FAIL ') + n + (x !== undefined && x !== '' ? ' → ' + x : '')); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  fs.readFile(path.join(root, p), (e, d) => { if (e) { r.writeHead(404); r.end('nf'); return; } r.writeHead(200, { 'content-type': (TYPES[path.extname(p)] || 'application/octet-stream') + '; charset=utf-8' }); r.end(d); });
}).listen(0, async () => {
  const base = 'http://localhost:' + srv.address().port + '/ofis/';
  const b = await chromium.launch();
  const errs = [];
  async function open(url, opt) {
    const ctx = await b.newContext(Object.assign({ viewport: { width: 1440, height: 900 }, acceptDownloads: true }, opt || {}));
    const pg = await ctx.newPage();
    pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await pg.goto(base + (url || '?saat=15:40')); await pg.waitForFunction('window.OFIS&&window.OFIS.ready');
    return { ctx, pg };
  }
  const click = async (pg, id) => {            // oyun dünyasındaki bir aktörün ekran konumuna tıkla
    const p = await pg.evaluate(id => { const a = OFIS.Office.state().actorById[id]; const v = OFIS.debug.toView(a.sx, a.sy - 14); const r = document.getElementById('tuval').getBoundingClientRect(); return { x: v.x + r.left, y: v.y + r.top }; }, id);
    await pg.mouse.click(p.x, p.y);
  };

  /* ---------- A. oda içi görünüm ve adres ---------- */
  let { ctx, pg } = await open();
  await pg.click('.ray [data-oda=lab]'); await sleep(900);
  let st = await pg.evaluate(() => ({ h: location.hash, a: OFIS.debug.mode.active, r: OFIS.debug.mode.room, t: OFIS.debug.roomT(), ust: !document.getElementById('odaUst').hidden, pr: document.querySelector('.ray [data-oda=lab]').getAttribute('aria-pressed') }));
  ok('Lab: adres #oda/lab, oda içi açık, geçiş tamam, geri düğmesi görünür', st.h === '#oda/lab' && st.a && st.r === 'lab' && st.t === 1 && st.ust && st.pr === 'true', JSON.stringify(st));
  const z1 = await pg.evaluate(() => OFIS.debug.cam.z), zf = await pg.evaluate(() => { const c = OFIS.debug.cam; return c.z; });
  await pg.keyboard.press('Escape'); await sleep(900);
  st = await pg.evaluate(() => ({ h: location.hash, a: OFIS.debug.mode.active, t: OFIS.debug.roomT(), ust: document.getElementById('odaUst').hidden, z: OFIS.debug.cam.z }));
  ok('Esc binaya döndürür (adres temizlenir, yakınlaşma geri alınır)', st.h === '' && !st.a && st.t === 0 && st.ust && st.z < z1 * 0.7, JSON.stringify(st) + ' zLab=' + z1.toFixed(2));
  await pg.click('.ray [data-oda=lab]'); await sleep(500); await pg.goBack(); await sleep(900);
  ok('tarayıcı geri tuşu binaya döndürür', await pg.evaluate(() => !OFIS.debug.mode.active && location.hash === ''));
  await pg.goForward(); await sleep(900);
  ok('ileri tuşu odaya geri götürür', await pg.evaluate(() => OFIS.debug.mode.active && OFIS.debug.mode.room === 'lab'));
  await pg.click('#geriBtn'); await sleep(900);
  ok('Geri düğmesi binaya döndürür', await pg.evaluate(() => !OFIS.debug.mode.active && location.hash === ''));
  await pg.click('.ray [data-oda=kapi]'); await sleep(300); await pg.click('.ray [data-oda=arsiv]'); await sleep(400);
  ok('Kapı ve Arşiv aynı kalıpla açılır', await pg.evaluate(() => OFIS.debug.mode.room === 'arsiv' && location.hash === '#oda/arsiv'));
  await pg.click('#geriBtn'); await sleep(900);
  ok('iki oda gezdikten sonra Geri tek adımda binaya döner', await pg.evaluate(() => !OFIS.debug.mode.active && location.hash === ''));
  const walls = await pg.evaluate(() => ({ lab: OFIS.World.statics.filter(e => e.wall && e.wall.includes('lab')).length, arsiv: OFIS.World.statics.filter(e => e.wall && e.wall.includes('arsiv')).length, kapi: OFIS.World.statics.filter(e => e.wall && e.wall.includes('kapi')).length }));
  ok('seçili odanın duvar parçaları işaretli (Arşiv duvarı kalkar)', walls.arsiv > 0, JSON.stringify(walls));
  await ctx.close();
  ({ ctx, pg } = await open('?saat=15:40#oda/lab'));
  ok('doğrudan #oda/lab adresi odayı anında açar', await pg.evaluate(() => OFIS.debug.mode.active && OFIS.debug.mode.room === 'lab' && OFIS.debug.roomT() === 1));
  await ctx.close();

  /* ---------- B. bilgi kutusu, tıklanabilir kişi ve nesneler ---------- */
  ({ ctx, pg } = await open());
  const gaps = await pg.evaluate(() => {
    const W = OFIS.World, bad = [];
    Object.keys(W.gapsH).forEach(y => W.gapsH[y].forEach(lx => [[W.BX + lx, W.BY + +y], [W.BX + lx, W.BY + +y - 1]].forEach(t => { if (W.isBlocked(t[0], t[1])) bad.push('h' + y + ':' + lx + '→' + t.join(',')); })));
    Object.keys(W.gapsV).forEach(k => { const [lx, ly] = k.split(',').map(Number); [[W.BX + lx, W.BY + ly], [W.BX + lx - 1, W.BY + ly]].forEach(t => { if (W.isBlocked(t[0], t[1])) bad.push('v' + k + '→' + t.join(',')); }); });
    return bad;
  });
  ok('iç kapı boşlukları mobilyayla kapanmaz (Denetim koltuğu hariç)', gaps.filter(x => x !== 'h4:21→25,8').length === 0, gaps.join(', '));
  ok('denetçi trader masasına, postacı posta kutusuna yürüyebilir (yol var)', await pg.evaluate(() => { const W = OFIS.World, st = OFIS.Office.state(), d = st.actorById['s:denetim'], t = st.actorById.T046, h = st.actorById['s:haber1']; return !!W.path(d.tx, d.ty, t.tx, t.ty - 1) && !!W.path(h.tx, h.ty, W.BX + W.mailboxLocal[0] + 1, W.BY + W.mailboxLocal[1]); }));
  await pg.click('.ray [data-oda=lab]'); await sleep(900);
  await click(pg, 'T006'); await sleep(400);
  let tx = await pg.evaluate(() => document.getElementById('bilgi').textContent);
  ok('kişiye tıklayınca bilgi kutusu: Kimlik · Gerçek veri · Replik · Neden burada? (olay_id, kural, tarih)', ['Kimlik', 'Gerçek veri', 'Replik', 'Neden burada?', 'olay_id', 'kural', 'tarih', '0xAAAA…0006'].every(k => new RegExp(k, 'i').test(tx)), tx.slice(0, 80).replace(/\n/g, ' '));
  ok('ofis esprisi ayrı ve etiketli', await pg.evaluate(() => !!document.querySelector('#bilgi .r-suz .etiket') && /ofis esprisi/i.test(document.querySelector('#bilgi .r-suz .etiket').textContent)));
  ok('"X dk önce"/zaman ve n gösterilir', /n=\d+/.test(tx) && /(dk önce|şimdi|sa )/.test(tx), '');
  ok('tıklanan kişi tepki animasyonu yapar', await pg.evaluate(() => { const a = OFIS.Office.state().actorById.T006; return !!a.react; }));
  await sleep(1100);
  ok('tepki biter (döngü uykuya döner)', await pg.evaluate(() => { const a = OFIS.Office.state().actorById.T006; return !a.react; }));
  await pg.keyboard.press('Escape'); await sleep(300);
  ok('Esc önce bilgi kutusunu kapatır, odada kalır', await pg.evaluate(() => document.getElementById('bilgi').hidden && OFIS.debug.mode.active));
  await pg.keyboard.press('Escape'); await sleep(900);
  ok('ikinci Esc binaya döndürür', await pg.evaluate(() => !OFIS.debug.mode.active));

  // her kişi tıklanabilir
  const result = await pg.evaluate(async () => {
    const W = OFIS.World, Off = OFIS.Office, st = Off.state(), miss = [];
    const wait = ms => new Promise(r => setTimeout(r, ms));
    const rooms = {};
    st.actors.forEach(a => { if (a.dead) return; const room = a.kind === 'staff' ? a.room : a.kat; if (W.roomById[room] && !W.roomById[room].out) (rooms[room] = rooms[room] || []).push(a); });
    for (const room of Object.keys(rooms)) {
      OFIS.debug.goRoom(room); await wait(260);
      rooms[room].forEach(a => {
        let hit = false;
        for (let dy = 6; dy <= 30 && !hit; dy += 3) for (let dx = -3; dx <= 3 && !hit; dx += 3) { const p = OFIS.debug.pick(a.sx + dx, a.sy - dy, false); if (p && p.type === 'person' && p.a === a) hit = true; }
        if (!hit) miss.push(a.id);
      });
    }
    return { total: st.actors.filter(a => !a.dead).length, miss };
  });
  ok('tüm kişiler tıklanabilir (n=' + result.total + ')', result.miss.length === 0, result.miss.join(','));
  // her odada en az 3 tıklanabilir nesne
  const objres = await pg.evaluate(async () => {
    const W = OFIS.World, wait = ms => new Promise(r => setTimeout(r, ms)), found = {}, bad = [];
    for (const room of Object.keys(W.roomById)) {
      if (W.roomById[room].out) continue;
      OFIS.debug.goRoom(room); await wait(260);
      for (const o of W.objects.filter(x => x.room === room)) {
        const s = o.e.s; if (!s) { bad.push(o.id + ':sprite yok'); continue; }
        const x0 = o.e.px - s.ax, y0 = o.e.py - s.ay; let hit = false;
        for (let y = 3; y < s.c.height && !hit; y += 5) for (let x = 3; x < s.c.width && !hit; x += 5) { const p = OFIS.debug.pick(x0 + x, y0 + y, false); if (p && p.type === 'obje' && p.o.id === o.id) hit = true; }
        if (hit) (found[room] = found[room] || new Set()).add(o.id); else bad.push(o.id);
      }
    }
    return { sayi: Object.fromEntries(Object.keys(found).map(k => [k, found[k].size])), bad };
  });
  const az = Object.keys(objres.sayi).filter(k => objres.sayi[k] < 3);
  ok('her odada en az 3 tıklanabilir nesne (' + Object.keys(objres.sayi).length + ' oda)', Object.keys(objres.sayi).length === 14 && az.length === 0, JSON.stringify(objres.sayi) + (objres.bad.length ? ' ulaşılamayan: ' + objres.bad.join(',') : ''));
  // Lab nesnesi → bilgi kutusu
  await pg.evaluate(() => OFIS.debug.goRoom('lab')); await sleep(900);
  const lp = await pg.evaluate(() => {
    const o = OFIS.World.objects.find(x => x.id === 'lab.pano'), s = o.e.s, x0 = o.e.px - s.ax, y0 = o.e.py - s.ay;
    const hits = []; for (let y = 2; y < s.c.height; y += 2) for (let x = 2; x < s.c.width; x += 2) { const p = OFIS.debug.pick(x0 + x, y0 + y, false); if (p && p.type === 'obje' && p.o.id === 'lab.pano') hits.push([x0 + x, y0 + y]); }
    if (!hits.length) return null; const mx = hits.reduce((a, h) => a + h[0], 0) / hits.length, my = hits.reduce((a, h) => a + h[1], 0) / hits.length; hits.sort((a, b) => Math.hypot(a[0] - mx, a[1] - my) - Math.hypot(b[0] - mx, b[1] - my));
    const v = OFIS.debug.toView(hits[0][0], hits[0][1]), r = document.getElementById('tuval').getBoundingClientRect(); return { x: v.x + r.left, y: v.y + r.top };
  });
  await pg.mouse.click(lp.x, lp.y); await sleep(400);
  tx = await pg.evaluate(() => document.getElementById('bilgi').textContent);
  ok('Lab panosuna tıklayınca havuz verisi (n=, zaman) ve Replik bölümü', /Havuz panosu/.test(tx) && /n=\d+ adres/.test(tx) && /Replik/.test(tx), tx.slice(0, 90));
  await pg.click('#bKapat'); await sleep(200);
  ok('× düğmesi bilgi kutusunu kapatır', await pg.evaluate(() => document.getElementById('bilgi').hidden));
  await ctx.close();

  /* ---------- C. adlar: değiştirme, saklama, dışa/içe aktarma ---------- */
  ({ ctx, pg } = await open());
  await pg.click('#ayarBtn'); await sleep(200);
  ok('ayarlar penceresi açılır (yasal ibare dâhil)', await pg.evaluate(() => document.getElementById('ayarlar').open && /yatırım tavsiyesi değil/.test(document.getElementById('ayarlar').textContent)));
  await pg.fill('input[data-kind=oda][data-id=lab]', 'Havuz Odası'); await pg.keyboard.press('Tab'); await sleep(150);
  await pg.fill('input[data-kind=calisan][data-id=denetim]', 'Müfettiş'); await pg.keyboard.press('Tab'); await sleep(150);
  await pg.click('#ayarKapat'); await sleep(200);
  ok('oda adı menüde ve etiketlerde değişir', await pg.evaluate(() => /Havuz Odası/.test(document.querySelector('.ray [data-oda=lab] span').textContent) && OFIS.Names.room('lab') === 'Havuz Odası'));
  await pg.reload(); await pg.waitForFunction('window.OFIS&&window.OFIS.ready'); await sleep(300);
  ok('adlar sayfa yenilenince korunur', await pg.evaluate(() => OFIS.Names.room('lab') === 'Havuz Odası' && OFIS.Names.staff('denetim') === 'Müfettiş' && /Havuz Odası/.test(document.querySelector('.ray [data-oda=lab] span').textContent)));
  await pg.click('.ray [data-oda=denetim]'); await sleep(900);
  await click(pg, 's:denetim'); await sleep(400);
  tx = await pg.evaluate(() => document.getElementById('bilgi').textContent);
  ok('çalışan bilgi kutusunda yeni ad görünür', /Müfettiş/.test(tx), tx.slice(0, 30));
  await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); await sleep(900);
  await pg.click('.ray [data-oda=oda]'); await sleep(900);
  await click(pg, 'T033'); await sleep(300);
  await pg.click('#bAdBtn'); await pg.fill('#bAdInput', 'Kısa Ad'); await pg.click('#bAdForm button[type=submit]'); await sleep(300);
  tx = await pg.evaluate(() => document.getElementById('bilgi').textContent);
  ok('trader takma adı: başlık değişir, gerçek adres (kısaltılmış) sabit kalır', /Kısa Ad/.test(tx) && /0xAAAA…0033/.test(tx), tx.slice(0, 60));
  await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); await sleep(900);
  await pg.click('#ayarBtn'); await sleep(200);
  const [dl] = await Promise.all([pg.waitForEvent('download'), pg.click('#ayarDisa')]);
  const exported = JSON.parse(fs.readFileSync(await dl.path(), 'utf8'));
  ok('JSON dışa aktarma (surum 1; oda, çalışan, trader adları)', exported.surum === 1 && exported.odalar.lab === 'Havuz Odası' && exported.calisanlar.denetim === 'Müfettiş' && exported.traderlar.T033 === 'Kısa Ad', JSON.stringify(exported));
  await pg.click('#ayarSifirla'); await sleep(150);
  ok('varsayılana dön: adlar kadro.json varsayılanına döner', await pg.evaluate(() => OFIS.Names.room('lab') === 'LAB · HAVUZ' && OFIS.Names.staff('denetim') === 'Denetçi' && OFIS.Names.trader('T033') === ''));
  await pg.setInputFiles('#ayarIce', { name: 'adlar.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify({ surum: 1, odalar: { lab: 'İçe Lab', yok: 'x' }, calisanlar: { cayci: 'Çaycı Usta' }, traderlar: { T033: 'Kısa Ad', zzz: 'x' } })) }); await sleep(300);
  const imp = await pg.evaluate(() => ({ lab: OFIS.Names.room('lab'), cay: OFIS.Names.staff('cayci'), t: OFIS.Names.trader('T033'), msg: document.getElementById('ayarMesaj').textContent }));
  ok('JSON içe aktarma: bilinen kimlikler uygulanır, bilinmeyenler atlanır', imp.lab === 'İçe Lab' && imp.cay === 'Çaycı Usta' && imp.t === 'Kısa Ad' && /2 kayıt atlandı/.test(imp.msg), JSON.stringify(imp));
  await pg.setInputFiles('#ayarIce', { name: 'bozuk.json', mimeType: 'application/json', buffer: Buffer.from('{bozuk') }); await sleep(300);
  ok('geçersiz JSON reddedilir, adlar bozulmaz', await pg.evaluate(() => /[iİ]çe aktarılamadı/.test(document.getElementById('ayarMesaj').textContent) && OFIS.Names.room('lab') === 'İçe Lab'));
  await pg.setInputFiles('#ayarIce', { name: 'surum.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify({ surum: 9, odalar: { lab: 'X' } })) }); await sleep(300);
  ok('desteklenmeyen sürüm reddedilir', await pg.evaluate(() => /desteklenmeyen/.test(document.getElementById('ayarMesaj').textContent) && OFIS.Names.room('lab') === 'İçe Lab'));
  await ctx.close();

  /* ---------- D. olay yokken döngü durur ---------- */
  ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); pg = await ctx.newPage();
  pg.on('pageerror', e => errs.push(e.message));
  const orn = JSON.parse(fs.readFileSync(path.join(root, 'ofis', 'ornek_durum.json'), 'utf8')); orn.olaylar = [];
  await pg.route('**/bos.json', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify(orn) }));
  await pg.goto(base + 'index.html?saat=15:40&durum=bos.json'); await pg.waitForFunction('window.OFIS&&window.OFIS.ready'); await sleep(2500);
  const k0 = await pg.evaluate(() => OFIS.perf.kare); await sleep(2500); const k1 = await pg.evaluate(() => OFIS.perf.kare);
  ok('olay yokken kare çizilmez (2,5 sn boyunca ' + (k1 - k0) + ' kare)', k1 - k0 === 0 && await pg.evaluate(() => !OFIS.debug.loop().raf));
  await pg.mouse.move(900, 400); await sleep(300); const k2 = await pg.evaluate(() => OFIS.perf.kare);
  ok('etkileşim döngüyü uyandırır', k2 > k1); await sleep(1500);
  const k3 = await pg.evaluate(() => OFIS.perf.kare); await sleep(1500);
  ok('etkileşimden sonra döngü yeniden uyur', (await pg.evaluate(() => OFIS.perf.kare)) === k3);
  await ctx.close();

  /* ---------- E. hızlı olay kuyruğu: durum her zaman doğru ---------- */
  ({ ctx, pg } = await open('?saat=15:40&hiz=30'));
  await sleep(9000);
  await pg.evaluate(() => { OFIS.Office.state().speed = 0; }); await sleep(9000);
  const cons = await pg.evaluate(() => {
    const W = OFIS.World, st = OFIS.Office.state(), probs = [];
    st.actors.forEach(a => {
      if (a.dead) return;
      if (a.path.length || a.queue.length || a.wait > 0) probs.push(a.id + ':yürüyor/kuyrukta');
      if (a.carry) probs.push(a.id + ':taşıyor');
      if (a.kind === 'trader' && ['lab', 'aday', 'oda', 'kontrol'].includes(a.kat)) { if (!a.seat || a.seat.occ !== a || a.tx !== a.seat.tx || a.ty !== a.seat.ty) probs.push(a.id + ':koltuk tutarsız'); }
      if (a.kind === 'staff' && a.home && (a.tx !== a.home[0] || a.ty !== a.home[1])) probs.push(a.id + ':yerinde değil');
    });
    let occ = 0; ['lab', 'aday', 'oda', 'kontrol'].forEach(k => W.seats[k].forEach(s => { if (s.occ) occ++; }));
    const seated = st.actors.filter(a => a.kind === 'trader' && !a.dead && ['lab', 'aday', 'oda', 'kontrol'].includes(a.kat)).length;
    if (occ !== seated) probs.push('dolu koltuk ' + occ + ' ≠ oturan ' + seated);
    return { probs, turn: st.turn, simT: Math.round(st.simT), marks: OFIS.Office.marks().length, neg: Object.values(st.katlar).some(k => k.n < 0) };
  });
  ok('hız ×30 sonrası (tur ' + cons.turn + '): koltuk, kat ve figürler tutarlı, takılan animasyon yok', cons.probs.length === 0 && !cons.neg && cons.marks === 0, cons.probs.join(', '));
  await ctx.close();

  /* ---------- F. her olay türü bir iletişim işareti üretir ---------- */
  ({ ctx, pg } = await open());
  await pg.evaluate(() => { OFIS.Office.state().speed = 0; window.__m = {}; setInterval(() => OFIS.Office.marks().forEach(m => { if (m.e && m.e.tur) (window.__m[m.e.tur] = window.__m[m.e.tur] || new Set()).add(m.kind); }), 60); });
  const evs = await pg.evaluate(() => OFIS.data.olaylar.map(e => e.tur));
  for (let i = 0; i < evs.length; i++) { await pg.evaluate(i => OFIS.Office.applyEvent(OFIS.data.olaylar[i]), i); await sleep(evs[i] === 'kirmizi_bayrak' || evs[i] === 'bayrak_kalkti' ? 5600 : evs[i] === 'bildirim' ? 2800 : 1200); if (evs[i] === 'kirmizi_bayrak') { ok('kırmızı bayrak notu trader masasında durur', await pg.evaluate(() => { const n = OFIS.Office.notes().T046; return !!(n && n.shown); })); } }
  await sleep(1500);
  const mm = await pg.evaluate(() => Object.fromEntries(Object.entries(window.__m).map(([k, v]) => [k, [...v]])));
  const turler = [...new Set(evs)].filter(t => t !== 'sistem'), yok = turler.filter(t => !mm[t]);
  ok('her olay türü (n=' + turler.length + ') en az bir zarf/not/ok üretir', yok.length === 0, yok.join(', '));
  ok('bayrak kalkınca not masadan kalkar', await pg.evaluate(() => !OFIS.Office.notes().T046));
  ok('olay işaretine tıklayınca olay_id ve zaman', await pg.evaluate(async () => {
    OFIS.Office.applyEvent({ id: 'ev-test', tur: 'kapi_gecti', trader: 'T062', oda: 'kapi', kural: 'ön eleme kuralı', metin: 'test' });
    await new Promise(r => setTimeout(r, 900));
    const m = OFIS.Office.marks()[0]; if (!m) return false;
    const mx = (m.a.x + m.b.x) / 2, my = (m.a.y + m.b.y) / 2, p = OFIS.debug.pick(mx, my, false);
    return !!p && p.type === 'isaret';
  }));
  await ctx.close();

  /* ---------- G. performans körlüğü ve yasal ibare ---------- */
  ({ ctx, pg } = await open());
  await sleep(400);
  tx = await pg.evaluate(() => document.body.textContent);
  ok('toplanmış performans (kasa değeri, % değişim, günlük toplam K/Z) hiçbir yerde yok', !/1\.01\d,\d\d/.test(tx) && !/%1,24/.test(tx) && !/Bugün\s*[−+-]\$/.test(tx) && /Kasa değeri kilitli/.test(tx), '');
  ok('yasal ibare her ekranda ("araştırma / sanal, yatırım tavsiyesi değil")', await pg.evaluate(() => { const y = document.getElementById('yasal'); const r = y.getBoundingClientRect(); return /yatırım tavsiyesi değil/.test(y.textContent) && r.height > 0; }));
  await pg.click('.ray [data-oda=finans]'); await sleep(900);
  await pg.evaluate(() => { const o = OFIS.World.objects.find(x => x.id === 'finans.kasa'); const s = o.e.s, x0 = o.e.px - s.ax, y0 = o.e.py - s.ay; const hits = []; for (let y = 2; y < s.c.height; y += 2) for (let x = 2; x < s.c.width; x += 2) { const p = OFIS.debug.pick(x0 + x, y0 + y, false); if (p && p.type === 'obje') hits.push([x0 + x, y0 + y]); } const mx = hits.reduce((a, h) => a + h[0], 0) / hits.length, my = hits.reduce((a, h) => a + h[1], 0) / hits.length; hits.sort((a, b) => Math.hypot(a[0] - mx, a[1] - my) - Math.hypot(b[0] - mx, b[1] - my)); const v = OFIS.debug.toView(hits[0][0], hits[0][1]), r = document.getElementById('tuval').getBoundingClientRect(); window.__pt = { x: v.x + r.left, y: v.y + r.top }; });
  const pt = await pg.evaluate(() => window.__pt); await pg.mouse.click(pt.x, pt.y); await sleep(300);
  tx = await pg.evaluate(() => document.getElementById('bilgi').textContent);
  ok('Finans kasası bilgi kutusunda değer yok, "kilitli" yazar; yasal ibare var', /kilitli/.test(tx) && !/\$1\.0\d\d/.test(tx) && /yatırım tavsiyesi/.test(tx), tx.slice(0, 90));
  await ctx.close();

  /* ---------- H. hareket azaltma ---------- */
  ({ ctx, pg } = await open('?saat=15:40&hiz=4', { reducedMotion: 'reduce' }));
  await sleep(6000);
  const rm = await pg.evaluate(() => ({ red: OFIS.Office.reduced, walk: OFIS.Office.state().actors.filter(a => a.path.length).length, log: OFIS.Office.state().log.length, raf: OFIS.debug.loop().raf }));
  ok('azaltılmış hareket: yürüyen yok, olaylar işleniyor, döngü uyuyor', rm.red && rm.walk === 0 && rm.log > 0 && !rm.raf, JSON.stringify(rm));
  await ctx.close();

  /* ---------- I. telefon: çekmece, dokunma hedefi, taşma ---------- */
  ({ ctx, pg } = await open('?saat=15:40', { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true }));
  const ov = await pg.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
  ok('telefonda yatay kaydırma yok', ov.sw <= ov.iw + 1, JSON.stringify(ov));
  await pg.tap('.ray [data-oda=lab]'); await sleep(900);
  const pp = await pg.evaluate(() => { const a = OFIS.Office.state().actorById.T006; const v = OFIS.debug.toView(a.sx + 3, a.sy - 6), r = document.getElementById('tuval').getBoundingClientRect(); return { x: v.x + r.left, y: v.y + r.top }; });
  await pg.touchscreen.tap(pp.x, pp.y); await sleep(500);
  const dr = await pg.evaluate(() => { const b = document.getElementById('bilgi'), r = b.getBoundingClientRect(), k = document.getElementById('bKapat').getBoundingClientRect(); return { hidden: b.hidden, pos: getComputedStyle(b).position, bottom: Math.round(r.bottom), vh: innerHeight, w: Math.round(r.width), kw: Math.round(k.width), kh: Math.round(k.height), txt: b.innerText.length }; });
  ok('telefonda bilgi alttan çekmece olarak açılır (dokunmayla, hover gerekmez)', !dr.hidden && dr.pos === 'fixed' && Math.abs(dr.bottom - dr.vh) <= 1 && dr.w === 390, JSON.stringify(dr));
  ok('kapat düğmesi ≥ 44 px', dr.kw >= 44 && dr.kh >= 44);
  const small = await pg.evaluate(() => [...document.querySelectorAll('button, .btn-dosya')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && (r.height < 43.5 || r.width < 43.5) && !e.closest('table') && !e.closest('.gozcu'); }).map(e => (e.id || e.className || e.textContent.trim().slice(0, 12)) + ':' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)));
  ok('telefonda tüm düğmeler ≥ 44 px (tablo ve günlük satırları hariç)', small.length === 0, small.join(', '));
  await pg.tap('#bKapat'); await sleep(200);
  ok('çekmece kapanır', await pg.evaluate(() => document.getElementById('bilgi').hidden));
  await ctx.close();

  ok('sayfa/konsol hatası yok', errs.length === 0, errs.slice(0, 3).join(' | '));
  console.log(bad ? '\n' + bad + ' test başarısız' : '\nhepsi geçti');
  await b.close(); srv.close(); process.exit(bad ? 1 : 0);
});
