/* Ofis · çizim döngüsü, kamera, gün ışığı, etiketler, etkileşim. */
(function () {
  'use strict';
  const O = window.OFIS, W = O.World, Off = O.Office, S = O.S, HW = O.HW, HH = O.HH;
  const $ = s => document.querySelector(s);
  const qs = new URLSearchParams(location.search);
  const mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  let reduced = mq.matches || qs.get('hareket') === '0';

  /* ---------- gün ışığı (gerçek saate göre) ---------- */
  const TINT = [[0, [88, 102, 170]], [5, [100, 112, 176]], [6.5, [255, 196, 150]], [8, [255, 250, 242]], [17, [255, 247, 232]], [18.5, [255, 184, 132]], [20, [150, 130, 190]], [21.5, [98, 110, 176]], [24, [88, 102, 170]]];
  const SKY = [[0, '#0b1030', '#26305e'], [5, '#10183c', '#2d3a6c'], [6.5, '#f2a36b', '#ffe0b0'], [8, '#7cc4f5', '#d4efff'], [17, '#7cc4f5', '#d4efff'], [18.5, '#f28a5a', '#ffd0a0'], [20, '#46407a', '#c07a9a'], [21.5, '#10183c', '#2d3a6c'], [24, '#0b1030', '#26305e']];
  function lerp(a, b, t) { return a + (b - a) * t; }
  function kf(tab, h, isSky) {
    for (let i = 0; i < tab.length - 1; i++) {
      const a = tab[i], b = tab[i + 1];
      if (h >= a[0] && h <= b[0]) {
        const t = (h - a[0]) / (b[0] - a[0]);
        if (!isSky) return a[1].map((v, j) => Math.round(lerp(v, b[1][j], t)));
        return { top: O.mix(a[1], b[1], t), bot: O.mix(a[2], b[2], t) };
      }
    }
    return isSky ? { top: O.C(tab[0][1]), bot: O.C(tab[0][2]) } : tab[0][1];
  }
  let light = { h: 12, tint: [255, 250, 242], night: 0, sky: null };
  function updateLight() {
    const c = Off.clock(), h = c.getHours() + c.getMinutes() / 60;
    const bucket = Math.round(h * 6);
    if (light.bucket === bucket) return false;
    const hh = bucket / 6, tint = kf(TINT, hh, false), sk = kf(SKY, hh, true);
    const lum = (tint[0] + tint[1] + tint[2]) / 765, night = Math.max(0, Math.min(1, (0.9 - lum) / 0.35));
    const day = hh >= 7.5 && hh <= 18;
    light = { bucket: bucket, h: hh, tint: tint, night: night, sky: { key: 'k' + bucket, top: sk.top, bot: sk.bot, orb: day ? '#fff2a8' : (night > 0.6 ? '#e8ecff' : '#ffd08a') } };
    W.wins.forEach(w => { w.e.s = S.windowGlass(w.side, light.sky); });
    const aksam = hh >= 19 || hh < 7;
    const el = $('#vardiya'); if (el) el.textContent = aksam ? 'Akşam vardiyası' : 'Gündüz vardiyası';
    return true;
  }

  /* ---------- tuval ve kamera ---------- */
  const cv = $('#tuval'), cx = cv.getContext('2d');
  const lo = document.createElement('canvas'), lc = lo.getContext('2d');
  const mid = document.createElement('canvas'), mc = mid.getContext('2d');
  const view = { w: 800, h: 500, dpr: 1 };
  const cam = { cx: 0, cy: 0, z: 1 };
  let target = null, fitZ = 1, dirty = true;

  function interest() {
    const x0 = W.OX + (W.BX - W.BY - W.BH) * HW, x1 = W.OX + (W.BX + W.BW - W.BY) * HW;
    const y0 = W.OY + (W.BX + W.BY) * HH - 56, y1 = W.OY + (W.BX + W.BW + W.BY + W.BH) * HH + 18;
    return { x0: x0, x1: x1, y0: y0, y1: y1 };
  }
  function fit() {
    const r = interest(), narrow = view.w < 700, mx = narrow ? 14 : 30, my = narrow ? 20 : 30;
    const z = Math.min(view.w / (r.x1 - r.x0 + mx * 2), view.h / (r.y1 - r.y0 + my * 2));
    return { cx: (r.x0 + r.x1) / 2, cy: (r.y0 + r.y1) / 2 + (narrow ? -6 : 24), z: z };
  }
  function setCam(c, animate) {
    if (!animate || reduced) { Object.assign(cam, c); target = null; } else target = { cx: c.cx, cy: c.cy, z: c.z, t0: performance.now(), from: { cx: cam.cx, cy: cam.cy, z: cam.z }, dur: 650 };
    dirty = true;
  }
  function resize() {
    const host = $('#ofisTuval'), r = host.getBoundingClientRect();
    view.w = Math.max(200, Math.round(r.width)); view.h = Math.max(160, Math.round(r.height)); view.dpr = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(view.w * view.dpr); cv.height = Math.round(view.h * view.dpr);
    const f = fit(), first = !cam.z || cam.first;
    const wasFit = Math.abs(cam.z - fitZ) < 1e-3 || !fitZ;
    fitZ = f.z;
    if (!cam.init) { Object.assign(cam, f); cam.init = true; } else if (wasFit) Object.assign(cam, f);
    dirty = true;
  }
  const toWorld = (px, py) => ({ x: (px - view.w / 2) / cam.z + cam.cx, y: (py - view.h / 2) / cam.z + cam.cy });
  const toView = (wx, wy) => ({ x: (wx - cam.cx) * cam.z + view.w / 2, y: (wy - cam.cy) * cam.z + view.h / 2 });
  function clampCam() {
    cam.z = Math.max(fitZ * 0.7, Math.min(4.2, cam.z));
    const mx = view.w / cam.z / 2, my = view.h / cam.z / 2;
    cam.cx = Math.max(Math.min(cam.cx, W.CW - mx * 0.3), mx * 0.3);
    cam.cy = Math.max(Math.min(cam.cy, W.CH - my * 0.3), my * 0.3);
  }

  /* ---------- sahne ---------- */
  lo.width = W.CW; lo.height = W.CH;
  function drawScene(now) {
    const ctx = lc;
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; ctx.imageSmoothingEnabled = false;
    ctx.drawImage(W.ground, 0, 0);
    const st = W.statics, dyn = Off.dyn();
    let j = 0;
    const sway = reduced ? 0 : 1;
    for (let i = 0; i < st.length; i++) {
      const e = st[i];
      while (j < dyn.length && dyn[j].k <= e.k) { dyn[j].draw(ctx); j++; }
      if (!e.s) continue;
      let ox = 0;
      if (e.tree && sway) ox = Math.round(Math.sin(now / 1100 + e.sway) * 0.6);
      ctx.drawImage(e.s.c, Math.round(e.px - e.s.ax) + ox, Math.round(e.py - e.s.ay));
    }
    while (j < dyn.length) { dyn[j].draw(ctx); j++; }
    // bayat odalar: renksiz
    const s = Off.state();
    Object.keys(s.stale).forEach(id => {
      if (!s.stale[id]) return;
      const r = W.roomById[id], p = W.roomPoly(r), up = 46;
      ctx.save(); ctx.beginPath();
      ctx.moveTo(p[0][0], p[0][1] - up); ctx.lineTo(p[1][0], p[1][1] - up); ctx.lineTo(p[1][0], p[1][1]); ctx.lineTo(p[2][0], p[2][1]); ctx.lineTo(p[3][0], p[3][1]); ctx.lineTo(p[3][0], p[3][1] - up); ctx.closePath();
      ctx.clip(); ctx.globalCompositeOperation = 'saturation'; ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, W.CW, W.CH);
      ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(150,155,170,1)'; ctx.fillRect(0, 0, W.CW, W.CH); ctx.restore();
    });
    // oda vurgusu
    Off.highlights().forEach(h => {
      const r = W.roomById[h.room]; if (!r) return;
      const p = W.roomPoly(r);
      ctx.save(); ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]); for (let i = 1; i < 4; i++) ctx.lineTo(p[i][0], p[i][1]); ctx.closePath();
      ctx.globalAlpha = h.a * (h.sel ? 0.9 : 1);
      ctx.fillStyle = 'rgba(255,224,120,' + (0.13 * h.pulse) + ')'; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = h.sel ? 'rgba(255,255,255,0.95)' : 'rgba(255,214,90,' + (0.6 + 0.4 * h.pulse) + ')'; ctx.stroke();
      ctx.restore();
    });
    // gün ışığı
    const t = light.tint;
    ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgb(' + t[0] + ',' + t[1] + ',' + t[2] + ')'; ctx.fillRect(0, 0, W.CW, W.CH);
    ctx.globalCompositeOperation = 'lighter';
    if (light.night > 0.05) {
      const n = light.night;
      ctx.globalAlpha = 0.16 * n; ctx.fillStyle = '#ffd29a';
      const bp = [[W.BX, W.BY], [W.BX + W.BW, W.BY], [W.BX + W.BW, W.BY + W.BH], [W.BX, W.BY + W.BH]].map(q => [W.sx(q[0], q[1]), W.sy(q[0], q[1])]);
      ctx.beginPath(); ctx.moveTo(bp[0][0], bp[0][1] - 30); ctx.lineTo(bp[1][0], bp[1][1] - 30); ctx.lineTo(bp[1][0], bp[1][1]); ctx.lineTo(bp[2][0], bp[2][1]); ctx.lineTo(bp[3][0], bp[3][1]); ctx.lineTo(bp[3][0], bp[3][1] - 30); ctx.closePath(); ctx.fill();
      ctx.globalAlpha = Math.min(1, n * 0.9);
      W.lamps.forEach(l => ctx.drawImage(Off.glow.warm, l.px - 26, l.py - 52 - 26));
      ctx.globalAlpha = Math.min(1, n * 0.5);
      W.wins.forEach(w => { const e = w.e; ctx.drawImage(Off.glow.blue, e.px - 22 + (w.side === 'L' ? 20 : -20), e.py - 22 - 20 + (w.side === 'L' ? 10 : 10)); });
    }
    if (s.alarm) {
      const k = reduced ? 1 : 0.5 + 0.5 * Math.sin(now / 180);
      ctx.globalAlpha = 0.85 * k; const b = W.beaconE; ctx.drawImage(Off.glow.red, b.px - 30, b.py - 30 - 24);
    }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  }

  /* ---------- ekrana aktarım (tam sayı büyütme + yumuşak küçültme) ---------- */
  function blit() {
    const dz = cam.z * view.dpr, k = dz > 1.6 ? Math.ceil(dz) : 1;
    const wl = view.w / cam.z, hl = view.h / cam.z;
    const left = cam.cx - wl / 2, top = cam.cy - hl / 2;
    const sx0 = Math.max(0, Math.floor(left)), sy0 = Math.max(0, Math.floor(top));
    const sx1 = Math.min(W.CW, Math.ceil(left + wl)), sy1 = Math.min(W.CH, Math.ceil(top + hl));
    cx.setTransform(1, 0, 0, 1, 0, 0);
    { const t = light.tint; cx.fillStyle = 'rgb(' + Math.round(94 * t[0] / 255) + ',' + Math.round(156 * t[1] / 255) + ',' + Math.round(70 * t[2] / 255) + ')'; cx.fillRect(0, 0, cv.width, cv.height); }
    const sw = sx1 - sx0, sh = sy1 - sy0;
    if (sw <= 0 || sh <= 0) return;
    if (k > 1) {
      if (mid.width !== sw * k || mid.height !== sh * k) { mid.width = sw * k; mid.height = sh * k; } mc.imageSmoothingEnabled = false; mc.drawImage(lo, sx0, sy0, sw, sh, 0, 0, sw * k, sh * k);
      cx.imageSmoothingEnabled = true; cx.imageSmoothingQuality = 'high';
      cx.drawImage(mid, 0, 0, sw * k, sh * k, (sx0 - left) * dz, (sy0 - top) * dz, sw * dz, sh * dz);
    } else {
      cx.imageSmoothingEnabled = true; cx.imageSmoothingQuality = 'high';
      cx.drawImage(lo, sx0, sy0, sw, sh, (sx0 - left) * dz, (sy0 - top) * dz, sw * dz, sh * dz);
    }
    cx.setTransform(view.dpr, 0, 0, view.dpr, 0, 0);
  }

  /* ---------- etiketler (tuval üstünde keskin metin) ---------- */
  const FONT = '"SF Mono", ui-monospace, Menlo, Consolas, "Liberation Mono", monospace';
  function pill(x, y, text, bg, fg, size, pad) {
    cx.font = '700 ' + size + 'px ' + FONT;
    const w = cx.measureText(text).width + pad * 2, h = size + pad + 2;
    cx.fillStyle = bg; rr(x - w / 2, y - h / 2, w, h, 3); cx.fill();
    cx.fillStyle = fg; cx.textBaseline = 'middle'; cx.textAlign = 'center'; cx.fillText(text, x, y + 0.5);
    return w;
  }
  function rr(x, y, w, h, r) { cx.beginPath(); cx.moveTo(x + r, y); cx.arcTo(x + w, y, x + w, y + h, r); cx.arcTo(x + w, y + h, x, y + h, r); cx.arcTo(x, y + h, x, y, r); cx.arcTo(x, y, x + w, y, r); cx.closePath(); }
  const KOLC = { kohort: '#f5cb5c', kontrol: '#6ea8ff', havuz: '#b8c2d4' };
  let hover = null, pinned = null, hoverRoom = null;
  function drawLabels() {
    const s = Off.state(), z = cam.z, showSigns = z >= 0.42;
    const fs = Math.max(6.5, Math.min(13, 5.8 + z * 3.4));
    drawTraderLabels();
    if (showSigns) {
      W.ROOMS.forEach(r => {
        if (r.id === 'hol') return;
        const p = W.sign(r), v = toView(p.x, p.y);
        if (v.x < -80 || v.y < -40 || v.x > view.w + 80 || v.y > view.h + 40) return;
        const stale = s.stale[r.id], sel = s.sel === r.id || hoverRoom === r.id;
        const txt = r.ad + (stale ? ' · BAYAT' : '');
        const bg = stale ? '#7a5a00' : '#fdf6e3', fg = stale ? '#fff4c8' : '#1b2236';
        cx.save(); if (sel) { cx.shadowColor = '#f5cb5c'; cx.shadowBlur = 8; }
        pill(v.x, v.y, txt, bg, fg, fs, fs < 9 ? 3 : 5);
        cx.restore();
        cx.strokeStyle = 'rgba(27,34,54,0.9)'; cx.lineWidth = 1; cx.beginPath(); cx.moveTo(v.x - 0.5, v.y + fs / 2 + 4); cx.lineTo(v.x - 0.5, v.y + fs / 2 + 8); cx.stroke();
      });
    }
  }
  function drawTraderLabels() {
    const z = cam.z;
    // trader etiketleri
    if (qs.get('etiket') === '0') return;
    const labs = Off.labels(), showAll = z >= 0.9, fs2 = Math.max(7, Math.min(11, 5.6 + z * 2.2));
    labs.forEach(l => {
      const hov = hover === l.a || pinned === l.a;
      if (!showAll && !hov) return;
      const v = toView(l.x, l.y);
      if (v.x < -40 || v.y < -20 || v.x > view.w + 40 || v.y > view.h + 20) return;
      const t = l.t || {}, short = hov || z >= 2.0 ? (t.adres || l.a.id) : '…' + String(t.adres || l.a.id).slice(-4);
      const w = pill(v.x + 4, v.y, short, 'rgba(14,20,38,' + (hov ? '0.95' : '0.7') + ')', hov ? '#ffe28a' : '#f1f5f9', fs2, 2);
      cx.fillStyle = KOLC[t.kol] || '#b8c2d4'; cx.fillRect(v.x + 4 - w / 2 - 3, v.y - 3, 3, 6);
      if (t.ornek) { /* "örnek" bilgisi ipucunda ve üst etiket çipinde */ }
    });
  }

  /* ---------- ipucu ---------- */
  const tip = $('#ipucu');
  function fmtUsd(v) { return (v < 0 ? '−' : v > 0 ? '+' : '') + '$' + Math.abs(v).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function fmtPct(v) { return (v < 0 ? '−' : v > 0 ? '+' : '') + '%' + Math.abs(v).toLocaleString('tr-TR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }); }
  const KATAD = { lab: 'Lab (havuz)', aday: 'Aday', oda: 'Oda (kopya)', kontrol: 'Kontrol grubu', disari: 'Kapıda' };
  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
  function tipFor(a) {
    const s = Off.state();
    if (a.kind === 'staff') {
      const names = { makam: 'Makam · karar kullanıcının', sekreter: 'Sekreter · kural kitabı', finans1: 'Finans · kasa ve işlem büyüklüğü', finans2: 'Finans · kasa ve işlem büyüklüğü', haber1: 'Haberleşme · Telegram', haber2: 'Haberleşme · Telegram', risk1: 'Risk · tavanlar', risk2: 'Risk · tavanlar', denetim: 'Denetim · veri kalitesi', arsivci: 'Arşiv · veri saklama', tarama1: 'Tarama · keşif', tarama2: 'Tarama · keşif', kapici: 'Kapı · ön eleme', cayci: 'Çaycı' };
      const id = a.staffId, note = id === 'cayci' ? '<div class="m">Yalnız ofis süsü; veri göstermez.</div>' : '<div class="m">Rol karakteri: modülün durumunu gösterir (karar kuraldadır).</div>';
      return '<b>' + esc(names[id] || 'Personel') + '</b>' + note;
    }
    const t = s.traders[a.id] || {}, tr = s.acik.filter(x => x.trader === a.id);
    let h = '<b>' + esc(t.adres || a.id) + '</b> <span class="ornek">örnek</span><div class="m">' + esc(KATAD[a.kat] || '—') + ' · kol: ' + esc(t.kol || 'bilinmiyor') + ' · tarz: ' + esc(t.tarz || 'bilinmiyor') + '</div>';
    h += '<div class="m">Etiket: ' + esc(t.etiket || 'bilinmiyor') + ' · gün n=' + (t.gun != null ? t.gun : 'bilinmiyor') + ' · işlem n=' + (t.islem_n != null ? t.islem_n : 'bilinmiyor') + '</div>';
    h += '<div class="m">Gölge puanı (bilgi): ' + (t.puan != null ? String(t.puan).replace('.', ',') : 'bilinmiyor') + '</div>';
    if (tr.length) tr.forEach(x => { h += '<div class="t ' + (x.kz_usd >= 0 ? 'up' : 'dn') + '">' + esc(x.coin) + ' ' + (x.yon === 'long' ? 'LONG' : 'SHORT') + ' ' + x.kaldirac + 'x · ' + fmtUsd(x.kz_usd) + ' (' + fmtPct(x.kz_yuzde) + ') · lik. %' + String(x.lik_uzaklik).replace('.', ',') + '</div>'; });
    else h += '<div class="m">Açık gölge işlemi yok.</div>';
    return h;
  }
  function showTip(html, px, py) {
    tip.innerHTML = html; tip.hidden = false;
    const r = $('#ofisTuval').getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = px + 14, y = py + 14;
    if (x + tw > view.w - 6) x = Math.max(6, px - tw - 14);
    if (y + th > view.h - 6) y = Math.max(6, py - th - 14);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { tip.hidden = true; }
  function inPoly(poly, wx, wy) {
    let c = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { if (((poly[i][1] > wy) !== (poly[j][1] > wy)) && (wx < (poly[j][0] - poly[i][0]) * (wy - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0])) c = !c; }
    return c;
  }
  function roomAtWorld(wx, wy) {
    // önce zemin (tam isabet); yoksa tavana kadar uzanan silüet (duvar bölgesi)
    let hit = null;
    W.ROOMS.forEach(r => { if (r.id !== 'hol' && inPoly(W.roomPoly(r), wx, wy)) hit = r; });
    if (hit) return hit;
    W.ROOMS.forEach(r => {
      if (r.id === 'hol') return;
      const p = W.roomPoly(r), up = 40;
      if (inPoly([[p[0][0], p[0][1] - up], [p[1][0], p[1][1] - up], [p[1][0], p[1][1]], [p[2][0], p[2][1]], [p[3][0], p[3][1]], [p[3][0], p[3][1] - up]], wx, wy)) hit = r;
    });
    return hit;
  }

  /* ---------- etkileşim ---------- */
  let drag = null;
  cv.addEventListener('pointerdown', e => {
    cv.setPointerCapture(e.pointerId);
    drag = { x: e.clientX, y: e.clientY, cx: cam.cx, cy: cam.cy, moved: false, id: e.pointerId, touch: e.pointerType === 'touch' };
  });
  cv.addEventListener('pointermove', e => {
    const r = cv.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top;
    if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
      if (drag.moved && (cam.z > fitZ * 1.04 || !drag.touch)) { cam.cx = drag.cx - dx / cam.z; cam.cy = drag.cy - dy / cam.z; target = null; clampCam(); dirty = true; hideTip(); return; }
    }
    if (e.pointerType === 'touch') return;
    const w = toWorld(px, py), a = Off.hit(w.x, w.y);
    hover = a; hoverRoom = a ? null : (roomAtWorld(w.x, w.y) || {}).id || null;
    if (a) showTip(tipFor(a), px, py);
    else if (hoverRoom) { const i = Off.roomInfo(hoverRoom); showTip('<b>' + esc(i.ad) + (i.stale ? ' · bayat' : '') + '</b>' + i.lines.map(l => '<div class="m">' + esc(l) + '</div>').join(''), px, py); }
    else if (!pinned) hideTip();
    cv.style.cursor = a || hoverRoom ? 'pointer' : (cam.z > fitZ * 1.04 ? 'grab' : 'default');
    dirty = true;
  });
  cv.addEventListener('pointerup', e => {
    const was = drag; drag = null;
    if (!was || was.moved) return;
    const r = cv.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top, w = toWorld(px, py), a = Off.hit(w.x, w.y);
    if (a) { pinned = a; showTip(tipFor(a), px, py); }
    else { pinned = null; const room = roomAtWorld(w.x, w.y); if (room) { selectRoom(room.id, true); const i = Off.roomInfo(room.id); showTip('<b>' + esc(i.ad) + '</b>' + i.lines.map(l => '<div class="m">' + esc(l) + '</div>').join(''), px, py); } else hideTip(); }
    dirty = true;
  });
  cv.addEventListener('pointerleave', () => { hover = null; hoverRoom = null; if (!pinned) hideTip(); dirty = true; });
  cv.addEventListener('wheel', e => {
    e.preventDefault();
    const r = cv.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top, before = toWorld(px, py);
    cam.z *= Math.exp(-e.deltaY * 0.0012); clampCam();
    const after = toWorld(px, py); cam.cx += before.x - after.x; cam.cy += before.y - after.y; clampCam(); target = null; dirty = true;
  }, { passive: false });
  cv.addEventListener('keydown', e => {
    const step = 40 / cam.z;
    if (e.key === 'ArrowLeft') cam.cx -= step; else if (e.key === 'ArrowRight') cam.cx += step; else if (e.key === 'ArrowUp') cam.cy -= step; else if (e.key === 'ArrowDown') cam.cy += step;
    else if (e.key === '+' || e.key === '=') zoomBy(1.25); else if (e.key === '-') zoomBy(0.8); else if (e.key === '0') setCam(fit(), true); else if (e.key === 'Escape') { pinned = null; hideTip(); }
    else return;
    e.preventDefault(); clampCam(); dirty = true;
  });
  function zoomBy(f) { setCam({ cx: cam.cx, cy: cam.cy, z: Math.max(fitZ * 0.7, Math.min(4.2, cam.z * f)) }, true); }
  $('#zIn').addEventListener('click', () => zoomBy(1.35));
  $('#zOut').addEventListener('click', () => zoomBy(1 / 1.35));
  $('#zFit').addEventListener('click', () => { selectRoom(null); setCam(fit(), true); setTab('genel', true); });

  function roomCenter(r) {
    const p = W.roomPoly(r), cxp = (p[0][0] + p[2][0]) / 2, cyp = (p[0][1] + p[2][1]) / 2;
    const ww = p[1][0] - p[3][0], hh = p[2][1] - p[0][1] + 52;
    return { cx: cxp, cy: cyp - 18, w: ww, h: hh };
  }
  function focusRoom(id) {
    const r = W.roomById[id]; if (!r) return;
    const c = roomCenter(r), z = Math.max(fitZ * 1.1, Math.min(3.4, Math.min(view.w / (c.w + 140), view.h / (c.h + 110))));
    setCam({ cx: c.cx, cy: c.cy, z: z }, true);
  }
  function selectRoom(id, focus) { Off.select(id); if (id && focus) focusRoom(id); dirty = true; }
  window.OFIS.focusRoom = id => selectRoom(id, true);

  /* ---------- sekmeler ---------- */
  const TABS = { genel: null, havuz: ['lab', '#cHuni'], aday: ['aday', '#cHuni'], oda: ['oda', '#cAcik'], kohort: ['kontrol', '#cKohort'], risk: ['risk', '#cRisk'], arsiv: ['arsiv', '#cVeri'], telegram: ['haberlesme', '#cTelegram'] };
  function setTab(name, silent) {
    document.querySelectorAll('[data-tab]').forEach(b => b.setAttribute('aria-pressed', b.dataset.tab === name ? 'true' : 'false'));
    if (silent) return;
    const t = TABS[name];
    if (!t) { selectRoom(null); setCam(fit(), true); const sol = $('#sol'); if (sol) sol.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); return; }
    selectRoom(t[0], true);
    const el = $(t[1]); if (el) { const sol = $('#sol'); if (window.matchMedia('(min-width: 900px)').matches && sol) sol.scrollTo({ top: el.offsetTop - 8, behavior: reduced ? 'auto' : 'smooth' }); else el.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'nearest' }); el.classList.add('vurgu'); setTimeout(() => el.classList.remove('vurgu'), 1800); }
  }
  document.querySelectorAll('[data-tab]').forEach(b => b.addEventListener('click', () => { const n = b.dataset.tab; if (n === 'tamekran') toggleFull(); else setTab(n); }));
  function toggleFull() {
    const on = !document.body.classList.contains('tam');
    document.body.classList.toggle('tam', on);
    const b = document.querySelector('[data-tab="tamekran"]'); if (b) b.setAttribute('aria-pressed', on ? 'true' : 'false');
    try { if (on && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {}); else if (!on && document.fullscreenElement) document.exitFullscreen(); } catch (e) { /* tam ekran izni yok: CSS düzeni yeterli */ }
    setTimeout(() => { resize(); const c = fit(); setCam(c, false); }, 60);
  }
  document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && document.body.classList.contains('tam')) toggleFull(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('tam')) toggleFull(); });
  document.querySelectorAll('[data-oda]').forEach(b => b.addEventListener('click', () => { selectRoom(b.dataset.oda, true); setTab('genel', true); const i = Off.roomInfo(b.dataset.oda); }));
  window.OFIS.setTab = setTab;

  /* ---------- ana döngü ---------- */
  let last = performance.now(), fpsN = 0, fpsT = 0;
  function frame(t) {
    const dt = Math.min(0.1, (t - last) / 1000); last = t;
    updateLight();
    Off.update(dt);
    if (target) {
      const p = Math.min(1, (t - target.t0) / target.dur), e = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
      cam.cx = target.from.cx + (target.cx - target.from.cx) * e; cam.cy = target.from.cy + (target.cy - target.from.cy) * e; cam.z = target.from.z * Math.pow(target.z / target.from.z, e);
      if (p >= 1) target = null;
    }
    clampCam();
    const p0 = performance.now(); drawScene(t); const p1 = performance.now(); blit(); const p2 = performance.now(); drawLabels(); const p3 = performance.now();
    const pf = window.OFIS.perf || (window.OFIS.perf = { scene: 0, blit: 0, lab: 0 }); pf.scene = pf.scene * 0.9 + (p1 - p0) * 0.1; pf.blit = pf.blit * 0.9 + (p2 - p1) * 0.1; pf.lab = pf.lab * 0.9 + (p3 - p2) * 0.1;
    dirty = false;
    if (qs.get('perf') === '1') { const el = $('#perf'); if (el) { el.hidden = false; el.textContent = (window.OFIS.fps || 0) + ' fps · sahne ' + pf.scene.toFixed(1) + ' ms · aktarım ' + pf.blit.toFixed(1) + ' ms'; } }
    fpsN++; fpsT += dt; if (fpsT >= 1) { window.OFIS.fps = Math.round(fpsN / fpsT); fpsN = 0; fpsT = 0; }
    if (!reduced) requestAnimationFrame(frame);
  }
  function startLoop() {
    last = performance.now();
    if (!reduced) requestAnimationFrame(frame);
  }
  let redTimer = null;
  function applyMotion() {
    Off.reduced = reduced; document.body.classList.toggle('az-hareket', reduced);
    if (redTimer) { clearInterval(redTimer); redTimer = null; }
    if (reduced) redTimer = setInterval(() => frame(performance.now() + 0), 700);
    else startLoop();
  }
  if (mq.addEventListener) mq.addEventListener('change', e => { reduced = e.matches; applyMotion(); });

  /* ---------- açılış ---------- */
  async function boot() {
    if (qs.get('saat')) { const m = /^(\d{1,2}):(\d{2})$/.exec(qs.get('saat')); if (m) { const d = new Date(); d.setHours(+m[1], +m[2], 0, 0); Off.timeOffsetMs = d.getTime() - Date.now(); } }
    const url = qs.get('durum') || 'ornek_durum.json';
    let data;
    try { const r = await fetch(url, { cache: 'no-store' }); if (!r.ok) throw new Error('HTTP ' + r.status); data = await r.json(); if (data.surum !== 1) throw new Error('desteklenmeyen şema sürümü: ' + data.surum); }
    catch (err) { $('#hata').hidden = false; $('#hata').textContent = 'Veri okunamadı (' + err.message + '). Sahte veri gösterilmiyor.'; return; }
    W.build();
    Off.init(data, { reduced: reduced, speed: parseFloat(qs.get('hiz')) || 1 });
    window.OFIS.data = data;
    updateLight(); resize();
    new ResizeObserver(() => { resize(); }).observe($('#ofisTuval'));
    if (O.Panel) O.Panel.init(Off, { focusRoom: id => selectRoom(id, true) });
    applyMotion();
    const f = qs.get('oda'); if (f) { setTimeout(() => selectRoom(f, true), 300); }
    window.OFIS.ready = true;
    if (reduced) frame(performance.now());
  }
  window.OFIS.debug = { cam: cam, view: view, toView: toView, toWorld: toWorld };
  window.OFIS.invalidate = () => { dirty = true; if (reduced) frame(performance.now()); };
  boot();
})();
