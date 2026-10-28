/* Ofis · durum, aktörler, olay motoru, efektler, duvar ekranları.
   Kural: her hareket bir olaydan doğar. Boşta sahte hareket yok (çaycı yürüyüşü ve ağaç sallanması kaldırıldı). */
(function () {
  'use strict';
  const O = window.OFIS, W = O.World, S = O.S, HW = O.HW, HH = O.HH;
  const Off = (O.Office = {});
  const BX = W.BX, BY = W.BY;
  let st = null;
  const listeners = [];
  const now = () => performance.now();
  Off.on = f => listeners.push(f);
  const emit = () => listeners.forEach(f => f(st));
  Off.state = () => st;
  Off.reduced = false;
  Off.timeOffsetMs = 0;
  Off.clock = () => new Date(Date.now() + Off.timeOffsetMs);

  const clone = x => JSON.parse(JSON.stringify(x));

  /* ---------- başlangıç ---------- */
  Off.init = function (data, opt) {
    opt = opt || {};
    Off.reduced = !!opt.reduced;
    data.kasa = Object.assign({ deger_usd: null, baslangic_usd: null, gun_n: null, egri: [], zaman: null }, data.kasa || {});
    data.kasa.egri = data.kasa.egri || [];
    data.ozet = Object.assign({ islem_basi_usd: null, bugun_kz_usd: null, bugun_acilan_n: 0, bugun_kapanan_n: 0, zaman: null }, data.ozet || {});
    data.risk = Object.assign({ tavanlar: [], zaman: null }, data.risk || {});
    data.telegram = Object.assign({ bugun_n: null, son: [], zaman: null }, data.telegram || {});
    data.tarama = Object.assign({ puanlar: [], zaman: null }, data.tarama || {});
    data.kohort_kontrol = Object.assign({ hafta: 0, hafta_toplam: 12, performans_kilitli: true, kollar: [], onkayit: '', zaman: null }, data.kohort_kontrol || {});
    data.veri_kalitesi = data.veri_kalitesi || []; data.olaylar = data.olaylar || []; data.acik_islemler = data.acik_islemler || []; data.kapananlar = data.kapananlar || []; data.traderlar = data.traderlar || [];
    ['havuz', 'aday', 'oda', 'kontrol'].forEach(k => { data.katlar = data.katlar || {}; data.katlar[k] = Object.assign({ n: null, masa: 0, kapasite: null, zaman: null }, data.katlar[k] || {}); });
    st = {
      data: data, initial: clone(data), loadMs: Date.now(), simT: 0, evIdx: 0, speed: opt.speed || 1, turn: 0,
      traders: {}, actors: [], actorById: {}, katlar: clone(data.katlar), acik: clone(data.acik_islemler), kapanan: clone(data.kapananlar),
      kasa: clone(data.kasa), ozet: clone(data.ozet), risk: clone(data.risk), vk: clone(data.veri_kalitesi), tg: clone(data.telegram), kk: clone(data.kohort_kontrol),
      tarama: clone(data.tarama), stale: {}, hl: {}, sel: null, alarm: false, denetim: 'tamam', boxN: 3, log: [], fx: [], flash: {},
      scanUntil: 0, haberUntil: 0, kasaUntil: 0, last: { kz: null }
    };
    data.traderlar.forEach(t => (st.traders[t.id] = t));
    // Makam konuk sandalyeleri
    (W.emptyChairs || []).forEach(c => { const s = O.chairSpr(c.c, 'b'); W.ent(c.tx + c.ty + 1.2, W.sx(c.tx, c.ty), W.sy(c.tx, c.ty) + HH, s); });
    W.resort();
    buildActors();
    refreshVisuals();
    emit();
  };
  Off.reset = function () {
    // akış başa sarılırken sayılar ilk veriye döner (aktörler döngüde zaten başlangıç koltuklarına döner)
    const d = st.initial;
    st.katlar = clone(d.katlar); st.acik = clone(d.acik_islemler); st.kapanan = clone(d.kapananlar); st.kasa = clone(d.kasa); st.ozet = clone(d.ozet);
    st.risk = clone(d.risk); st.vk = clone(d.veri_kalitesi); st.tg = clone(d.telegram); st.stale = {}; st.alarm = false; st.denetim = 'tamam';
    st.evIdx = 0; st.simT = 0; st.turn++;
    log({ tur: 'sistem', oda: 'makam', metin: 'Örnek olay akışı baştan başladı (tur ' + (st.turn + 1) + ')' });
    emit();
  };

  /* ---------- aktörler ---------- */
  function mkActor(o) {
    const a = Object.assign({ path: [], queue: [], pose: 'stand', dir: 'u', seat: null, wait: 0, walkT: 0, alpha: 1, dead: false }, o);
    a.fx = a.tx + 0.5; a.fy = a.ty + 0.5;
    st.actors.push(a); st.actorById[a.id] = a; return a;
  }
  function sit(a, seat) {
    a.seat = seat; seat.occ = a; a.tx = seat.tx; a.ty = seat.ty; a.fx = a.tx + 0.5; a.fy = a.ty + 0.5; a.pose = 'sit'; a.dir = 'u'; seat.chair.s = null;
  }
  function standUp(a) {
    if (!a.seat) return;
    a.seat.occ = null; a.seat.chair.s = O.chairSpr(a.seat.chairLook, 'b'); a.seat = null;
  }
  function freeSeat(kat) { return (W.seats[kat] || []).find(s => !s.occ); }
  function buildActors() {
    // personel
    W.staff.forEach(sp => {
      const a = mkActor({ id: 's:' + sp.id, kind: 'staff', staffId: sp.id, room: sp.room, look: sp.look, tx: sp.seat ? sp.seat.tx : sp.tx, ty: sp.seat ? sp.seat.ty : sp.ty, cayci: !!sp.cayci });
      if (sp.seat) { sit(a, sp.seat); sp.seat.staff = true; }
      else { a.pose = sp.pose === 'sitF' ? 'sitF' : 'stand'; a.dir = sp.dir || 'u'; }
      a.home = [a.tx, a.ty];
    });
    // trader figürleri
    ['lab', 'aday', 'oda', 'kontrol'].forEach(kat => {
      const list = st.data.traderlar.filter(t => t.kat === kat);
      list.forEach(t => {
        const seat = freeSeat(kat); if (!seat) return;
        const a = mkActor({ id: t.id, kind: 'trader', kat: kat, tx: seat.tx, ty: seat.ty, look: O.look(parseInt(t.id.slice(1), 10) * 13 + 5, 'trader') });
        sit(a, seat);
      });
      // boş koltuklar boş sandalye olarak görünür
      W.seats[kat].forEach(seat => { if (!seat.occ) seat.chair.s = O.chairSpr(seat.chairLook, 'b'); });
    });
  }
  function nearestFree(tx, ty) { return [tx, ty]; }
  function go(a, tx, ty) {
    if (Off.reduced) { a.tx = tx; a.ty = ty; a.fx = tx + 0.5; a.fy = ty + 0.5; a.path = []; return; }
    const p = W.path(a.tx, a.ty, tx, ty);
    if (!p) { a.tx = tx; a.ty = ty; a.fx = tx + 0.5; a.fy = ty + 0.5; a.path = []; return; }
    a.path = p;
  }
  function stepActor(a, dt) {
    if (a.wait > 0) { a.wait -= dt; if (a.wait > 0) return; a.wait = 0; }
    if (a.path.length) {
      const n = a.path[0], tx = n[0] + 0.5, ty = n[1] + 0.5, dx = tx - a.fx, dy = ty - a.fy, d = Math.hypot(dx, dy), sp = 2.7 * dt;
      if (Math.abs(dx) > Math.abs(dy)) a.dir = dx > 0 ? 'r' : 'l'; else if (Math.abs(dy) > 1e-6) a.dir = dy > 0 ? 'd' : 'u';
      a.walkT += dt;
      a.pose = (Math.floor(a.walkT / 0.16) % 2) ? 'w1' : 'w0';
      if (d <= sp) { a.fx = tx; a.fy = ty; a.tx = n[0]; a.ty = n[1]; a.path.shift(); }
      else { a.fx += dx / d * sp; a.fy += dy / d * sp; }
      return;
    }
    if (a.queue.length) {
      const q = a.queue.shift();
      if (q.go) { go(a, q.go[0], q.go[1]); if (!a.path.length && !a.dead) { a.pose = 'stand'; } }
      else if (q.wait) { a.wait = Off.reduced ? 0 : q.wait; a.pose = 'stand'; }
      else if (q.sit) { sit(a, q.sit); }
      else if (q.fn) q.fn(a);
      else if (q.remove) a.dead = true;
      return;
    }
    if (!a.seat && a.pose !== 'sit' && a.pose !== 'sitF') a.pose = 'stand';
  }

  /* ---------- kayıt ve yardımcılar ---------- */
  const pad = n => (n < 10 ? '0' : '') + n;
  function log(e) {
    const c = Off.clock();
    st.log.unshift({ ts: pad(c.getHours()) + ':' + pad(c.getMinutes()) + ':' + pad(c.getSeconds()), oda: e.oda || '', tur: e.tur, metin: e.metin || e.tur, n: ++logN });
    if (st.log.length > 60) st.log.length = 60;
  }
  let logN = 0;
  function hl(room, ms) { if (!room) return; st.hl[room] = { until: now() + (ms || 3200), t0: now() }; }
  function bubble(room, name, color, dx, dy) {
    const r = W.roomById[room]; if (!r) return;
    const p = W.sign(r);
    st.fx.push({ type: 'bubble', name: name, color: color || '#1b2236', x: p.x + (dx || 0), y: p.y - 6 + (dy || 0), t0: now(), dur: 3600 });
  }
  function acikOf(tid) { return st.acik.filter(x => x.trader === tid); }
  function tradeKat(tid) { const a = st.actorById[tid]; return a ? a.kat : (st.traders[tid] || {}).kat; }
  const roomOf = tid => { const k = tradeKat(tid); return k === 'lab' || k === 'aday' || k === 'oda' || k === 'kontrol' ? k : 'oda'; };

  /* ---------- olaylar ---------- */
  const ENTRY = [BX + W.BW + 3, BY + 16], EXIT = [BX + W.BW + 3, BY + 17], GATE = [BX + 24, BY + 17];
  function move(tid, kimden, kime, e, ikon) {
    const a = st.actorById[tid]; if (!a) return;
    const seat = freeSeat(kime);
    standUp(a); a.kat = kime;
    if (seat) { seat.occ = a; a.seat = seat; a.queue = [{ go: [seat.tx, seat.ty] }, { sit: seat }]; a.pose = 'stand'; }
    if (st.traders[tid]) st.traders[tid].kat = kime;
    const k = { lab: 'havuz', aday: 'aday', oda: 'oda' };
    if (k[kimden] && st.katlar[k[kimden]]) st.katlar[k[kimden]].n--;
    if (k[kime] && st.katlar[k[kime]]) st.katlar[k[kime]].n++;
    hl(kimden, 2600); hl(kime, 4200);
    bubble(kime, ikon, ikon === 'asagi' ? '#c0392b' : '#1f8a5a');
  }
  const H = {
    yeni_adres(e) {
      const t = st.traders[e.trader] || (st.traders[e.trader] = { id: e.trader, adres: e.adres, kat: 'disari', kol: 'havuz', tarz: 'intraday', gun: 0, islem_n: 0, puan: null, etiket: '—', ornek: true });
      const old = st.actorById[e.trader]; if (old) { standUp(old); old.dead = true; delete st.actorById[e.trader]; }
      const a = mkActor({ id: e.trader, kind: 'trader', kat: 'disari', tx: ENTRY[0], ty: ENTRY[1], look: O.look(parseInt(e.trader.slice(1), 10) * 13 + 5, 'trader') });
      a.queue = [{ go: [GATE[0], GATE[1]] }, { wait: 0.4 }];
      st.tarama.yeni = true; st.scanUntil = now() + 3500;
      hl('tarama', 3600); hl('kapi', 2600); bubble('tarama', 'arama', '#5b4a82');
    },
    kapi_gecti(e) {
      const a = st.actorById[e.trader]; if (!a) return;
      const seat = freeSeat('lab'); a.kat = 'lab'; if (st.traders[e.trader]) st.traders[e.trader].kat = 'lab';
      if (seat) { seat.occ = a; a.seat = seat; a.queue = [{ go: [seat.tx, seat.ty] }, { sit: seat }]; }
      st.katlar.havuz.n++;
      hl('kapi', 3000); hl('lab', 4000); bubble('kapi', 'tik', '#1f8a5a');
    },
    kapi_elendi(e) {
      const a = st.actorById[e.trader]; if (!a) return;
      a.queue = [{ go: [EXIT[0], EXIT[1]] }, { remove: true }];
      hl('kapi', 3800); bubble('kapi', 'uyari', '#c0392b');
    },
    havuzdan_cikar(e) {
      const a = st.actorById[e.trader]; if (!a) return;
      standUp(a); a.queue = [{ go: [EXIT[0], EXIT[1]] }, { remove: true }];
      st.katlar.havuz.n--; hl('lab', 3600); hl('kapi', 3000); bubble('lab', 'asagi', '#c0392b');
    },
    terfi(e) { move(e.trader, e.kimden, e.kime, e, 'yukari'); },
    kat_dusur(e) { move(e.trader, e.kimden, e.kime, e, 'asagi'); },
    islem_acildi(e) {
      st.acik.push({ id: e.id, trader: e.trader, coin: e.coin, yon: e.yon, kaldirac: e.kaldirac, yas_dk: 0, t0: Date.now(), kz_usd: e.kz_usd, kz_yuzde: e.kz_yuzde, lik_uzaklik: e.lik_uzaklik, teminat_usd: e.teminat_usd });
      st.flash[e.trader] = now() + 4200; st.ozet.bugun_acilan_n++;
      hl(roomOf(e.trader), 3400); bubble(roomOf(e.trader), 'uyari', '#1b6fb8', 0, 0);
    },
    islem_kapandi(e) {
      const i = st.acik.findIndex(x => x.id === e.id); if (i < 0) return;
      const x = st.acik.splice(i, 1)[0];
      const sure = Math.round((x.yas_dk || 0) + (x.t0 ? (Date.now() - x.t0) / 60000 : (Date.now() - st.loadMs) / 60000));
      st.kapanan.unshift({ coin: x.coin, yon: x.yon, neden: e.neden, sure_dk: sure, kz_usd: e.kz_usd, kz_yuzde: e.kz_yuzde, trader: x.trader });
      if (st.kapanan.length > 6) st.kapanan.length = 6;
      st.kasa.deger_usd = Math.round((st.kasa.deger_usd + e.kz_usd) * 100) / 100; st.ozet.bugun_kz_usd = Math.round((st.ozet.bugun_kz_usd + e.kz_usd) * 100) / 100; st.ozet.bugun_kapanan_n++;
      st.kasaUntil = now() + 3000;
      st.flash[x.trader] = now() + 2000;
      hl('finans', 3400); hl(roomOf(x.trader), 2400);
      st.fx.push({ type: 'coin', t0: now(), dur: 2400, lx: 8.5, ly: 1.2, sign: e.kz_usd >= 0 });
    },
    bildirim(e) {
      st.tg.bugun_n++; st.tg.son.unshift(e.metin); if (st.tg.son.length > 4) st.tg.son.length = 4;
      st.haberUntil = now() + 3200; hl('haberlesme', 3400);
      const r = W.roomById.haberlesme, mx = W.sx(BX + W.mailboxLocal[0] + 0.5, BY + W.mailboxLocal[1] + 0.5), my = W.sy(BX + W.mailboxLocal[0] + 0.5, BY + W.mailboxLocal[1] + 0.5);
      st.fx.push({ type: 'env', t0: now(), dur: 4200, x0: mx, y0: my - 24 });
    },
    risk_tavan(e) {
      const it = st.risk.tavanlar.find(x => x.anahtar === e.kalem); if (it) it.kullanim = e.deger;
      st.alarm = true; hl('risk', 5200); bubble('risk', 'uyari', '#c0392b');
    },
    risk_normal(e) {
      const it = st.risk.tavanlar.find(x => x.anahtar === e.kalem); if (it) it.kullanim = e.deger;
      st.alarm = st.risk.tavanlar.some(x => x.kullanim >= x.tavan * 0.999 || x.kullanim >= 1);
      hl('risk', 2600); bubble('risk', 'tik', '#1f8a5a');
    },
    veri_bayat(e) {
      st.stale[e.oda] = true; const row = st.vk.find(x => x.anahtar === e.oda); if (row) { row._d = row.durum; row.durum = 'bayat'; row._v = row.deger; row.deger = e.yas_dk + ' dk önce'; }
      hl(e.oda, 3600); bubble(e.oda, 'saat', '#b8860b');
    },
    veri_taze(e) {
      st.stale[e.oda] = false; const row = st.vk.find(x => x.anahtar === e.oda); if (row) { row.durum = row._d || 'tamam'; row.deger = row._v || row.deger; }
      hl(e.oda, 2800); bubble(e.oda, 'tik', '#1f8a5a');
    },
    denetim(e) {
      st.denetim = e.sonuc; const row = st.vk.find(x => x.anahtar === 'denetim'); if (row) row.durum = e.sonuc === 'tamam' ? 'tamam' : 'uyari';
      hl('denetim', 3600); bubble('denetim', e.sonuc === 'tamam' ? 'tik' : 'goz', e.sonuc === 'tamam' ? '#1f8a5a' : '#b8860b');
    },
    arsiv_yazildi(e) {
      st.boxN = Math.min(5, st.boxN + 1); const row = st.vk.find(x => x.anahtar === 'arsiv'); if (row) row.deger = e.satir.toLocaleString('tr-TR') + ' satır';
      hl('arsiv', 3600); st.fx.push({ type: 'box', t0: now(), dur: 900 });
      if (st.boxN >= 5) st.boxN = 3;
    },
    kasa_guncelle(e) {
      st.kasa.deger_usd = e.deger_usd; st.kasaUntil = now() + 3000; hl('finans', 3200);
      st.fx.push({ type: 'coin', t0: now(), dur: 2400, lx: 8.5, ly: 1.2, sign: true });
    },
    kural_kitabi(e) { hl('sekreterlik', 3400); bubble('sekreterlik', 'belge', '#7a6a50'); },
    kullanici_karari(e) { hl('makam', 3600); bubble('makam', 'tik', '#6b3f2a'); },
    veri_yenile(e) {
      (e.guncellemeler || []).forEach(u => { const x = st.acik.find(y => y.id === u.id); if (x) { x.kz_usd = u.kz_usd; x.kz_yuzde = u.kz_yuzde; x.lik_uzaklik = u.lik_uzaklik; } });
      st.ozet.zaman = Off.clock().toISOString(); hl('finans', 2600); hl('oda', 2600);
    }
  };
  Off.applyEvent = function (e) { const f = H[e.tur]; if (f) f(e); log(e); emit(); };

  /* ---------- görsel durum (ekranlar, LED, ışık, duvar ekranları) ---------- */
  const tvCache = {};
  function tvSprite(id, sig, build) { const k = id + '|' + sig; return tvCache[k] || (tvCache[k] = build()); }
  function tvBase(id, draw) {
    const T = W.tvs[id], span = T.span, side = T.side;
    return O.tspr(54, I => {
      const pl = (a, b, z0, z1, c) => (side === 'L' ? I.fl(a, b, 0, z0, z1, c) : I.fr(0, a, b, z0, z1, c));
      const ln = (a0, z0, a1, z1, c) => (side === 'L' ? I.ln(a0, 0, z0, a1, 0, z1, c) : I.ln(0, a0, z0, 0, a1, z1, c));
      pl(0.05, span - 0.05, 15, 43, '#141927'); pl(0.05, span - 0.05, 42, 43, '#2c3550');
      draw(pl, ln, span);
    }, { w: 48 + span * 20, ax: side === 'L' ? 24 : 24 + span * 20 });
  }
  function drawFinans(flash) {
    const eg = st.kasa.egri, vals = eg.map(p => p[1]), n = vals.length;
    return tvBase('finans', (pl, ln, span) => {
      pl(0.12, span - 0.12, 17.5, 40.5, flash ? '#16463f' : '#0e2a2c');
      pl(0.2, span - 0.2, 19, 19.8, '#2f6a66');
      if (n >= 5) {
        const mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals), up = vals[n - 1] >= vals[0], col = up ? '#5ef2a8' : '#ff7b7b';
        const pts = vals.map((v, i) => [0.22 + (span - 0.44) * i / (n - 1), 22 + 15 * (v - mn) / ((mx - mn) || 1)]);
        for (let i = 0; i < pts.length - 1; i++) {
          for (let s = 0; s <= 4; s++) { const a = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * s / 4, z = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * s / 4; pl(a, a + 0.06, 19.8, z, up ? '#1e6a4e' : '#6a2a2a'); }
        }
        for (let i = 0; i < pts.length - 1; i++) ln(pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1, col);
        const l = pts[pts.length - 1]; pl(l[0] - 0.04, l[0] + 0.08, l[1] - 0.5, l[1] + 3, '#ffffff');
      } else {
        for (let i = 0; i < 6; i++) pl(0.3 + i * 0.28, 0.4 + i * 0.28, 26, 27, '#4a7a7a'); // "veri birikiyor"
      }
      if (flash) { pl(0.12, span - 0.12, 17.5, 18.5, '#f5cb5c'); pl(0.12, span - 0.12, 39.5, 40.5, '#f5cb5c'); }
    });
  }
  function drawHaber(flash, active) {
    return tvBase('haber', (pl, ln, span) => {
      pl(0.12, span - 0.12, 17.5, 40.5, flash ? '#1b4a8c' : '#0f1c33');
      pl(0.35, 1.25, 21, 35, '#fbf7ea'); pl(0.35, 1.25, 21, 22, '#e3dac2');
      ln(0.35, 35, 0.8, 28.5, '#c9bfa6'); ln(1.25, 35, 0.8, 28.5, '#c9bfa6'); pl(0.72, 0.88, 26, 29, '#d4553b');
      for (let i = 0; i < 4; i++) { const w = [0.9, 0.6, 1.0, 0.45][i]; pl(1.55, 1.55 + w, 33 - i * 4, 35 - i * 4, flash && i === 0 ? '#ffffff' : '#5a7fb8'); }
      pl(span - 0.38, span - 0.2, 37, 39, active ? '#3dd68c' : '#ff6b6b');
    });
  }
  function drawRisk(alarm, blink) {
    return tvBase('risk', (pl, ln, span) => {
      pl(0.12, span - 0.12, 17.5, 40.5, alarm && blink ? '#3a1216' : '#161a26');
      st.risk.tavanlar.forEach((t, i) => {
        const z = 35 - i * 5.5, r = Math.max(0, Math.min(1, t.kullanim / t.tavan)), col = r >= 0.95 ? '#ff5a5a' : r >= 0.75 ? '#ffc94a' : '#3dd68c';
        pl(0.22, span - 0.22, z, z + 3.4, '#252d42'); pl(0.22, 0.22 + (span - 0.44) * r, z, z + 3.4, col);
        pl(0.12, 0.2, z, z + 3.4, col);
      });
      if (alarm) { const c = blink ? '#ff4040' : '#8a2626'; pl(0.12, span - 0.12, 17.5, 18.5, c); pl(0.12, span - 0.12, 39.5, 40.5, c); }
    });
  }
  function drawTarama(scanStep) {
    const pu = (st.tarama.puanlar || []).slice(0, 6);
    return tvBase('tarama', (pl, ln, span) => {
      pl(0.12, span - 0.12, 17.5, 40.5, '#1c1630');
      pu.forEach((p, i) => { const z = 36 - i * 3.6; pl(0.22, 0.22 + (span - 0.44) * p, z, z + 2.4, i === 0 ? '#f5cb5c' : '#9b86d6'); });
      if (scanStep >= 0) { const z = 19 + scanStep * 2.1; pl(0.12, span - 0.12, z, z + 1.4, '#c9f4ff'); }
    });
  }
  const beacon = [0, 1].map(b => O.tspr(44, I => { const c = I.p(0.5, 0.5, 26); I.P.disc(c[0], c[1] - 4, 5, 5, b ? '#ff3b3b' : '#a82020'); I.P.disc(c[0] - 1, c[1] - 5, 2, 2, b ? '#ffe0e0' : '#e06060'); I.P.outline('#2a2230'); }));
  const glowSpr = (col, r) => { const c = document.createElement('canvas'); c.width = c.height = r * 2; const x = c.getContext('2d'), g = x.createRadialGradient(r, r, 0, r, r, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, r * 2, r * 2); return c; };
  Off.glow = { red: glowSpr('rgba(255,70,70,0.9)', 30), warm: glowSpr('rgba(255,214,140,0.9)', 26), blue: glowSpr('rgba(120,190,255,0.9)', 22), green: glowSpr('rgba(70,255,170,0.8)', 18), amber: glowSpr('rgba(255,200,70,0.8)', 18) };

  function refreshVisuals() {
    const t = now();
    // masa ekranları
    ['lab', 'aday', 'oda', 'kontrol'].forEach(kat => {
      W.seats[kat].forEach(seat => {
        const a = seat.occ; let state = 'idle';
        if (a && !st.stale[kat]) {
          const tr = acikOf(a.id);
          if (st.flash[a.id] > t) state = 'flash';
          else if (tr.length) state = tr.reduce((s, x) => s + x.kz_usd, 0) >= 0 ? 'up' : 'down';
        }
        seat.scr.s = S.screen('y', state);
      });
    });
    W.staff.forEach(sp => { if (sp.seat) sp.seat.scr.s = st.stale[sp.room] ? S.screen('y', 'idle') : S.screen('y', 'staff'); });
    // sunucu LED'leri
    const lc = st.denetim === 'tamam' ? '#3dd68c' : '#ffc94a';
    ['20', '21', '22'].forEach(x => { W.leds['rack' + x].s = S.rackLed('y', lc); });
    // alarm lambası
    const blink = Math.floor(t / 380) % 2;
    W.beaconE.s = st.alarm ? beacon[Off.reduced ? 1 : blink] : null;
    // duvar ekranları
    const fk = st.kasaUntil > t ? 1 : 0, hk = st.haberUntil > t ? 1 : 0;
    const eg = st.kasa.egri;
    W.tvs.finans.e.s = tvSprite('finans', fk + ':' + eg.length + ':' + (eg.length ? eg[eg.length - 1][1] : '') + ':' + st.kasa.deger_usd, () => drawFinans(!!fk));
    W.tvs.haber.e.s = tvSprite('haber', hk + ':' + (st.stale.haberlesme ? 1 : 0), () => drawHaber(!!hk, !st.stale.haberlesme));
    W.tvs.risk.e.s = tvSprite('risk', st.alarm + ':' + (Off.reduced ? 1 : blink) + ':' + st.risk.tavanlar.map(x => x.kullanim).join(','), () => drawRisk(st.alarm, Off.reduced || !!blink));
    const scanning = st.scanUntil > t, step = scanning ? Math.floor(((t % 1200) / 1200) * 10) : -1;
    W.tvs.tarama.e.s = tvSprite('tarama', step + ':' + (st.tarama.puanlar || []).join(','), () => drawTarama(Off.reduced ? -1 : step));
    // arşiv kutuları
    Off.boxes = st.boxN;
  }

  /* ---------- zaman çizelgesi ve güncelleme ---------- */
  Off.update = function (dt) {
    if (!st) return;
    const evs = st.data.olaylar, total = st.data.akis_suresi_sn || 120;
    st.simT += dt * st.speed;
    while (st.evIdx < evs.length && evs[st.evIdx].t <= st.simT) { Off.applyEvent(evs[st.evIdx]); st.evIdx++; }
    if (st.evIdx >= evs.length && st.simT >= total) Off.reset();
    st.actors.forEach(a => stepActor(a, dt));
    for (let i = st.actors.length - 1; i >= 0; i--) if (st.actors[i].dead) { const a = st.actors[i]; delete st.actorById[a.id]; st.actors.splice(i, 1); }
    // biten efektler
    const t = now();
    st.fx = st.fx.filter(f => t - f.t0 < f.dur);
    refreshVisuals();
  };

  /* ---------- çizim listesi ---------- */
  Off.dyn = function () {
    const out = [], t = now();
    st.actors.forEach(a => {
      const px = W.OX + (a.fx - a.fy) * HW, py = W.OY + (a.fx + a.fy) * HH;
      a.sx = px; a.sy = py;
      const sitting = a.pose === 'sit' || a.pose === 'sitF';
      const spr = O.person(a.look, a.pose, sitting ? 'u' : a.dir);
      out.push({ k: a.fx + a.fy + (sitting ? 0.25 : 0), a: a, draw: ctx => { if (a.alpha < 1) ctx.globalAlpha = a.alpha; ctx.drawImage(spr.c, Math.round(px - spr.ax), Math.round(py - spr.ay)); ctx.globalAlpha = 1; } });
    });
    // arşiv kutu yığını
    for (let i = 0; i < Off.boxes; i++) {
      const px = W.sx(BX + 25, BY + 3), py = W.sy(BX + 25, BY + 3) + HH - 12 * i, spr = O.icons.kutu();
      out.push({ k: BX + 25 + BY + 3 + 1.1 + i * 0.01, draw: ctx => ctx.drawImage(spr.c, Math.round(px - spr.ax), Math.round(py - spr.ay + 8)) });
    }
    st.fx.forEach(f => {
      const p = (t - f.t0) / f.dur, e = Off.reduced ? 1 : Math.min(1, p * 4);
      if (f.type === 'bubble') {
        const spr = O.bubble(f.name, f.color), up = Off.reduced ? 0 : Math.min(8, p * 24), al = p > 0.8 ? (1 - p) / 0.2 : 1, sc = 1;
        out.push({ k: 1e6, draw: ctx => { ctx.globalAlpha = al; ctx.drawImage(spr.c, Math.round(f.x - spr.ax), Math.round(f.y - spr.ay - up)); ctx.globalAlpha = 1; } });
      } else if (f.type === 'env') {
        const spr = O.icons.envelope(), pp = Off.reduced ? 0.5 : p, x = f.x0 + pp * 130, y = f.y0 - pp * 70 - Math.sin(pp * Math.PI) * 24, al = pp > 0.85 ? (1 - pp) / 0.15 : 1;
        out.push({ k: 1e6, draw: ctx => { ctx.globalAlpha = al; ctx.drawImage(spr.c, Math.round(x - spr.ax), Math.round(y - spr.ay)); ctx.globalAlpha = 1; } });
      } else if (f.type === 'coin') {
        const spr = O.icons.coin(), x = W.sx(BX + f.lx, BY + f.ly), y = W.sy(BX + f.lx, BY + f.ly) - 18 - (Off.reduced ? 10 : p * 20), al = p > 0.7 ? (1 - p) / 0.3 : 1;
        out.push({ k: 1e6, draw: ctx => { ctx.globalAlpha = al; ctx.drawImage(spr.c, Math.round(x - spr.ax), Math.round(y - spr.ay)); ctx.globalAlpha = 1; } });
      } else if (f.type === 'box') {
        // düşen kutu halkası: yığının üstüne parıltı
        const x = W.sx(BX + 25, BY + 3), y = W.sy(BX + 25, BY + 3) - 6 - 12 * Math.max(0, Off.boxes - 1);
        out.push({ k: 1e6, draw: ctx => { ctx.globalAlpha = 1 - p; ctx.fillStyle = '#fff6c0'; ctx.fillRect(Math.round(x - 8 + p * 4), Math.round(y - p * 14), 2, 2); ctx.fillRect(Math.round(x + 6 - p * 4), Math.round(y - 4 - p * 10), 2, 2); ctx.globalAlpha = 1; } });
      }
    });
    out.sort((a, b) => a.k - b.k);
    return out;
  };
  Off.hit = function (wx, wy) {
    if (!st) return null;
    let best = null;
    st.actors.forEach(a => {
      if (a.sx === undefined) return;
      const top = (a.pose === 'sit' || a.pose === 'sitF') ? 36 : 26;
      if (Math.abs(wx - a.sx) <= 8 && wy >= a.sy - top && wy <= a.sy + 4 && (!best || a.fx + a.fy > best.fx + best.fy)) best = a;
    });
    return best;
  };
  Off.labels = function () {
    if (!st) return [];
    return st.actors.filter(a => a.kind === 'trader' && a.alpha > 0.5 && a.sx !== undefined).map(a => ({ a: a, x: a.sx, y: a.sy - ((a.pose === 'sit') ? 31 : 28), t: st.traders[a.id] }));
  };
  Off.highlights = function () {
    const t = now(), out = [];
    Object.keys(st.hl).forEach(k => { const h = st.hl[k]; if (h.until > t) out.push({ room: k, a: Math.min(1, (h.until - t) / 800), pulse: Off.reduced ? 1 : 0.55 + 0.45 * Math.sin((t - h.t0) / 160) }); else delete st.hl[k]; });
    if (st.sel) out.push({ room: st.sel, a: 1, pulse: 1, sel: true });
    return out;
  };
  Off.select = function (room) { if (st) { st.sel = room; emit(); } };
  /* oda → anlık özet (tıklayınca) */
  Off.roomInfo = function (id) {
    const r = W.roomById[id]; if (!r || !st) return null;
    const k = st.katlar, lines = [];
    const stale = !!st.stale[id];
    switch (id) {
      case 'lab': lines.push('Havuz gölgede izleniyor: n=' + k.havuz.n + ' adres; ' + k.havuz.masa + ' masa görünür.'); break;
      case 'aday': lines.push('Aday katı: n=' + k.aday.n + ' (' + k.aday.masa + ' masa görünür).'); break;
      case 'oda': lines.push('Oda: ' + k.oda.n + '/' + k.oda.kapasite + ' trader; açık gölge işlemi ' + st.acik.length + '.'); break;
      case 'kontrol': lines.push('Kontrol: aynı havuzdan rastgele N=' + (st.kk.kollar[1] || {}).n + ' adres (sabit tohum).'); break;
      case 'risk': lines.push('Risk tavanları: ' + st.risk.tavanlar.map(x => x.ad + ' %' + Math.round(x.kullanim / x.tavan * 100)).join(' · ')); break;
      case 'finans': lines.push('Sanal kasa: $' + st.kasa.deger_usd.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' (n=' + st.kasa.gun_n + ' gün).'); break;
      case 'haberlesme': lines.push('Telegram bildirimi bugün: n=' + st.tg.bugun_n + '.'); break;
      case 'denetim': lines.push('Son denetim: ' + (st.denetim === 'tamam' ? 'tamam' : 'uyarı') + '.'); break;
      case 'arsiv': lines.push('Arşiv: ' + ((st.vk.find(x => x.anahtar === 'arsiv') || {}).deger || 'bilinmiyor') + '.'); break;
      case 'tarama': lines.push('Haftalık tarama: ' + ((st.vk.find(x => x.anahtar === 'tarama') || {}).deger || 'bilinmiyor') + '.'); break;
      case 'kapi': lines.push('Kapı: yeni adresler ön elemeden geçer; geçmiş yalnız ön eleme, karar değil.'); break;
      case 'sekreterlik': lines.push('Kural kitabı: kurallar.yaml, ön kayıt hash\'i, DURUM.md.'); break;
      case 'makam': lines.push('Karar kullanıcının; lider denetler.'); break;
      case 'cay': lines.push('Çay ocağı: yalnız ofis süsü, veri göstermez.'); break;
      default: lines.push('Ortak alan.');
    }
    return { ad: r.ad, lines: lines, stale: stale };
  };
})();
