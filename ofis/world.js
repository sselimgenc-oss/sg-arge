/* Ofis · dünya: bina yerleşimi, odalar, mobilya, zemin, yürüme ağı. */
(function () {
  'use strict';
  const O = window.OFIS, S = O.S, HW = O.HW, HH = O.HH, C = O.C, shade = O.shade;
  const BX = 4, BY = 5, BW = 26, BH = 16, WW = 36, WH = 30;
  const OX = WH * HW, OY = 96;
  const CW = (WW + WH) * HW, CH = OY + (WW + WH) * HH + 44;
  const sx = (x, y) => OX + (x - y) * HW, sy = (x, y) => OY + (x + y) * HH;

  const ROOMS = [
    { id: 'makam', ad: 'MAKAM', x: 0, y: 0, w: 4, h: 4, fl: ['wood', '#8f5d3b'], ac: '#6b3f2a', solid: true },
    { id: 'sekreterlik', ad: 'SEKRETERLİK', x: 4, y: 0, w: 4, h: 4, fl: ['carpet', '#cdb99a'], ac: '#7a6a50' },
    { id: 'finans', ad: 'FİNANS', x: 8, y: 0, w: 4, h: 4, fl: ['tile', '#d3e6d8', '#bdd6c6'], ac: '#2f7d5a' },
    { id: 'haberlesme', ad: 'HABERLEŞME', x: 12, y: 0, w: 4, h: 4, fl: ['carpet', '#4a6694'], ac: '#2f4f86' },
    { id: 'risk', ad: 'RİSK', x: 16, y: 0, w: 4, h: 4, fl: ['tile', '#ecdcc7', '#d9c2a2'], ac: '#b5472f' },
    { id: 'denetim', ad: 'DENETİM', x: 20, y: 0, w: 3, h: 4, fl: ['concrete', '#a3acb6'], ac: '#4a5568', solid: true },
    { id: 'arsiv', ad: 'ARŞİV', x: 23, y: 0, w: 3, h: 4, fl: ['wood', '#a67c4a'], ac: '#6b4a2a', solid: true },
    { id: 'tarama', ad: 'TARAMA', x: 0, y: 4, w: 5, h: 5, fl: ['carpet', '#8570a8'], ac: '#5b4a82' },
    { id: 'cay', ad: 'ÇAY OCAĞI', x: 5, y: 4, w: 3, h: 5, fl: ['tile', '#f0e3c6', '#dcc59d'], ac: '#b8803a' },
    { id: 'lab', ad: 'LAB · HAVUZ', x: 8, y: 4, w: 10, h: 5, fl: ['tile', '#e2ecf4', '#d0dfec'], ac: '#3b82b8' },
    { id: 'kontrol', ad: 'KONTROL GRUBU', x: 18, y: 4, w: 8, h: 5, fl: ['carpet', '#62809a'], ac: '#3f5f7a' },
    { id: 'hol', ad: 'HOL', x: 0, y: 9, w: 26, h: 2, fl: ['wood', '#cfae7c'], ac: '#8a6a3e' },
    { id: 'aday', ad: 'ADAY', x: 0, y: 11, w: 6, h: 5, fl: ['carpet', '#cf9556'], ac: '#a8682c' },
    { id: 'oda', ad: 'ODA · KOPYA', x: 6, y: 11, w: 16, h: 5, fl: ['carpet', '#43558c'], ac: '#2c3a6b' },
    { id: 'kapi', ad: 'KAPI', x: 22, y: 11, w: 4, h: 5, fl: ['stone', '#cfcac0'], ac: '#6a6a70' }
  ];
  const roomAt = {}; // "lx,ly" → oda
  ROOMS.forEach(r => { r.cx = r.x + r.w / 2; r.cy = r.y + r.h / 2; for (let i = 0; i < r.w; i++) for (let j = 0; j < r.h; j++) roomAt[(r.x + i) + ',' + (r.y + j)] = r; });
  const roomById = {}; ROOMS.forEach(r => (roomById[r.id] = r));

  const W = (O.World = { BX, BY, BW, BH, WW, WH, OX, OY, CW, CH, sx, sy, ROOMS, roomById, roomAt, statics: [], seats: { lab: [], aday: [], oda: [], kontrol: [] }, staff: [], tvs: {}, wins: [], leds: {}, screens: [], trees: [], lamps: [], boxSlots: [], doors: [] });

  /* ---------- yürüme ağı ---------- */
  const blocked = new Set(), wallH = new Set(), wallV = new Set();
  const inW = (x, y) => x >= 0 && y >= 0 && x < WW && y < WH;
  W.block = (x, y) => blocked.add(x + ',' + y);
  W.isBlocked = (x, y) => blocked.has(x + ',' + y);
  function canStep(x, y, nx, ny) {
    if (!inW(nx, ny)) return false;
    if (nx === x + 1 && wallV.has((x + 1) + ',' + y)) return false;
    if (nx === x - 1 && wallV.has(x + ',' + y)) return false;
    if (ny === y + 1 && wallH.has(x + ',' + (y + 1))) return false;
    if (ny === y - 1 && wallH.has(x + ',' + y)) return false;
    return true;
  }
  /* en kısa yol (BFS, 4 komşu). hedef ve başlangıç engelli olabilir (koltuk). */
  W.path = function (ax, ay, bx, by) {
    const key = (x, y) => y * WW + x, prev = new Map(), q = [[ax, ay]];
    prev.set(key(ax, ay), null);
    const D = [[1, 0], [0, 1], [-1, 0], [0, -1]];
    while (q.length) {
      const [x, y] = q.shift();
      if (x === bx && y === by) break;
      for (const d of D) {
        const nx = x + d[0], ny = y + d[1];
        if (prev.has(key(nx, ny)) || !canStep(x, y, nx, ny)) continue;
        if (blocked.has(nx + ',' + ny) && !(nx === bx && ny === by)) continue;
        prev.set(key(nx, ny), [x, y]); q.push([nx, ny]);
      }
    }
    if (!prev.has(key(bx, by))) return null;
    const out = []; let cur = [bx, by];
    while (cur) { out.push(cur); cur = prev.get(key(cur[0], cur[1])); }
    return out.reverse().slice(1);
  };

  /* ---------- statik varlıklar ---------- */
  function ent(k, px, py, s) { const e = { k: k, px: px, py: py, s: s }; W.statics.push(e); return e; }
  W.ent = ent;
  const putT = (s, tx, ty, ko) => ent(tx + ty + 1 + (ko || 0), sx(tx, ty), sy(tx, ty), s);
  const L = (s, lx, ly, o) => { o = o || {}; const e = putT(s, BX + lx, BY + ly, o.k); if (o.block !== false) W.block(BX + lx, BY + ly); return e; };
  W.putT = putT;

  /* ---------- zemin ---------- */
  const type = {}; // "x,y" → { k: tür, ... }
  function T(x, y, v) { type[x + ',' + y] = v; }
  function buildTypes() {
    for (let x = 0; x < WW; x++) for (let y = 0; y < WH; y++) T(x, y, { k: 'grass' });
    // yaya yolu: kapıdan doğuya, sonra güneye otoparka
    for (let x = BX + BW; x < BX + BW + 4; x++) for (let y = BY + 12; y <= BY + 13; y++) T(x, y, { k: 'stone', c: '#d2c6aa' });
    for (let y = BY + 12; y < BY + 19; y++) for (let x = BX + BW + 2; x <= BX + BW + 3; x++) T(x, y, { k: 'stone', c: '#d2c6aa' });
    // otopark
    for (let x = BX + 2; x <= BX + 23; x++) for (let y = BY + 18; y <= BY + 24; y++) T(x, y, { k: 'asph', c: '#4d525c' });
    // sürüş yolu otoparktan yola
    for (let x = BX + 24; x < WW; x++) for (let y = BY + 21; y <= BY + 22; y++) T(x, y, { k: 'asph', c: '#4d525c' });
    // ana yol (sağ kenar, dikey)
    for (let x = WW - 3; x < WW; x++) for (let y = 0; y < WH; y++) T(x, y, { k: 'asph', c: '#454a54', road: true });
    // bina plazası (ön ve sağ kenar boyunca taş şerit)
    for (let x = BX - 1; x < BX + BW + 1; x++) T(x, BY + BH, { k: 'stone', c: '#dcd3bf' });
    for (let y = BY; y < BY + BH + 1; y++) if (!(y >= BY + 12 && y <= BY + 13)) T(BX + BW, y, { k: 'stone', c: '#dcd3bf' });
    // oda zeminleri
    ROOMS.forEach(r => {
      for (let i = 0; i < r.w; i++) for (let j = 0; j < r.h; j++) T(BX + r.x + i, BY + r.y + j, { k: r.fl[0], c: r.fl[1], c2: r.fl[2], room: r.id });
    });
    // halı: Makam kırmızı, Hol şeridi, Kapı paspası, Oda orta kuşak
    for (let i = 1; i <= 2; i++) for (let j = 1; j <= 3; j++) T(BX + i, BY + j, { k: 'carpet', c: j === 1 || j === 3 || i === 1 && false ? '#a3322f' : '#a3322f', rug: true, room: 'makam' });
    for (let x = 2; x < 24; x++) T(BX + x, BY + 10, { k: 'carpet', c: '#6a4f7a', room: 'hol', rug: true });
    T(BX + 25, BY + 12, { k: 'carpet', c: '#5a5f68', room: 'kapi', rug: true }); T(BX + 25, BY + 13, { k: 'carpet', c: '#5a5f68', room: 'kapi', rug: true });
  }
  function buildGround() {
    const P = new O.Px(CW, CH);
    P.rect(0, 0, CW, CH, '#5e9c46');
    for (let s = 0; s < WW + WH; s++) for (let x = 0; x < WW; x++) {
      const y = s - x; if (y < 0 || y >= WH) continue;
      const t = type[x + ',' + y];
      const px = sx(x, y), py = sy(x, y);
      if (t.k === 'grass') S.floorTile && drawGrass(P, px, py, x, y);
      else S.floorTile(P, px, py, x, y, t.k, t.c, t.c2);
    }
    const I = new O.Iso(P, 0, 0);
    const wl = (a, b, c) => { const p = [sx(a[0], a[1]), sy(a[0], a[1])], q = [sx(b[0], b[1]), sy(b[0], b[1])]; P.line(p[0], p[1], q[0], q[1], c); };
    // zemin çizgileri: rug kenarı, otopark çizgileri, yol şeridi
    for (let x = BX + 2; x <= BX + 24; x++) {
      for (const [y0, y1] of [[BY + 18, BY + 20], [BY + 22, BY + 24]]) wl([x, y0], [x, y1 + 1 - 1], '#e8eaee');
    }
    wl([BX + 2, BY + 20], [BX + 24, BY + 20], '#e8eaee'); wl([BX + 2, BY + 22], [BX + 24, BY + 22], '#e8eaee');
    for (let y = 0; y < WH; y += 2) wl([WW - 2, y], [WW - 2, y + 1], '#e4c64a');
    // yaya geçidi çizgileri
    for (let y = BY + 20; y <= BY + 21; y++) for (let k = 0; k < 4; k++) wl([BX + 25, y + k * 0.25 + 0.1], [BX + 25, y + k * 0.25 + 0.2], '#e8eaee');
    // arka duvar dibinde yumuşak gölge
    const sh = (pts, a) => P.poly(pts.map(q => [sx(q[0], q[1]), sy(q[0], q[1])]), O.pk(20, 16, 30, a));
    [[0.12, 34], [0.28, 22], [0.48, 12]].forEach(b => {
      sh([[BX, BY], [BX + BW, BY], [BX + BW, BY + b[0]], [BX, BY + b[0]]], b[1] * 0.6);
      sh([[BX, BY], [BX + b[0], BY], [BX + b[0], BY + BH], [BX, BY + BH]], b[1] * 0.6);
    });
    // bina kaidesi (ön kenar kalınlığı)
    const slab = (a, b, c, d, col) => P.poly([[sx(a, b), sy(a, b)], [sx(c, d), sy(c, d)], [sx(c, d), sy(c, d) + 7], [sx(a, b), sy(a, b) + 7]], col);
    slab(BX, BY + BH, BX + BW, BY + BH, '#b7ad98');
    slab(BX + BW, BY + BH, BX + BW, BY, '#9a917e');
    P.line(sx(BX, BY + BH), sy(BX, BY + BH) + 7, sx(BX + BW, BY + BH), sy(BX + BW, BY + BH) + 7, '#6f6757');
    P.line(sx(BX + BW, BY + BH), sy(BX + BW, BY + BH) + 7, sx(BX + BW, BY), sy(BX + BW, BY) + 7, '#6f6757');
    W.ground = P.flush();
  }
  function drawGrass(P, px, py, x, y) { S.floorGrass(P, px, py, x, y); }

  /* ---------- duvar / bölme ---------- */
  function buildWalls() {
    const accAt = (lx, ly) => (roomAt[lx + ',' + ly] || { ac: '#6a5a40' }).ac;
    const decoH = { 0: 'pic', 1: 'win', 2: 'win', 3: 'pic', 4: 'win', 5: 'win', 11: 'pic', 15: 'win', 16: 'win', 19: 'pic' };
    const decoV = { 3: 'win', 4: 'win', 7: 'win', 8: 'pic', 9: 'win', 10: 'win', 11: 'win', 12: 'pic', 13: 'win', 14: 'pic', 15: 'win' };
    ent(BX + BY - 0.4, sx(BX, BY), sy(BX, BY), S.wallCorner('#6b3f2a'));
    for (let lx = 0; lx < BW; lx++) {
      const d = decoH[lx] || '';
      const e = ent(BX + lx + BY + 0.4, sx(BX + lx, BY), sy(BX + lx, BY), S.wallBH(accAt(lx, 0), d, lx));
      if (d === 'win') W.wins.push({ side: 'L', e: ent(BX + lx + BY + 0.41, sx(BX + lx, BY), sy(BX + lx, BY), null) });
    }
    for (let ly = 0; ly < BH; ly++) {
      const d = decoV[ly] || '';
      ent(BX + BY + ly + 0.4, sx(BX, BY + ly), sy(BX, BY + ly), S.wallBV(accAt(0, ly), d, ly + 3));
      if (d === 'win') W.wins.push({ side: 'R', e: ent(BX + BY + ly + 0.41, sx(BX, BY + ly), sy(BX, BY + ly), null) });
      wallV.add(BX + ',' + (BY + ly));
    }
    for (let lx = 0; lx < BW; lx++) wallH.add((BX + lx) + ',' + BY);
    // ön ve sağ alçak duvar (kesit); girişte boşluk
    for (let lx = 0; lx < BW; lx++) { ent(BX + lx + BY + BH + 0.57, sx(BX + lx, BY + BH - 1), sy(BX + lx, BY + BH - 1), S.curbH()); wallH.add((BX + lx) + ',' + (BY + BH)); }
    for (let ly = 0; ly < BH; ly++) {
      if (ly === 12 || ly === 13) continue;
      ent(BX + BW + BY + ly + 0.57, sx(BX + BW - 1, BY + ly), sy(BX + BW - 1, BY + ly), S.curbV());
      wallV.add((BX + BW) + ',' + (BY + ly));
    }
    // giriş kapı sütunları
    ent(BX + BW + BY + 12 - 0.06 + 0.57, sx(BX + BW - 1, BY + 12), sy(BX + BW - 1, BY + 12), S.doorPost());
    ent(BX + BW + BY + 14 - 0.06 + 0.57, sx(BX + BW - 1, BY + 14), sy(BX + BW - 1, BY + 14), S.doorPost());

    /* iç bölmeler. kapılar (boşluklar) hâlinde. */
    const kind = (a, b) => ((a && a.solid) || (b && b.solid)) ? 'solid' : 'glass';
    const ra = (lx, ly) => roomAt[lx + ',' + ly];
    const gapsH = { 4: [1, 5, 11, 14, 17, 21, 24], 9: [2, 6, 11, 14, 21, 24], 11: [1, 4, 9, 15, 23] };
    Object.keys(gapsH).forEach(yy => {
      const y = +yy;
      for (let lx = 0; lx < BW; lx++) {
        if (gapsH[y].indexOf(lx) >= 0) continue;
        const a = ra(lx, y - 1), b = ra(lx, y); if (a === b) continue;
        ent(BX + lx + BY + y + 0.5, sx(BX + lx, BY + y), sy(BX + lx, BY + y), S.partH(kind(a, b), (b && b.ac) || '#777'));
        wallH.add((BX + lx) + ',' + (BY + y));
      }
    });
    const gapsV = {};
    gapsV[6 + ',' + 13] = 1; gapsV[22 + ',' + 13] = 1; gapsV[8 + ',' + 6] = 1; gapsV[18 + ',' + 6] = 1;
    for (let lx = 1; lx < BW; lx++) for (let ly = 0; ly < BH; ly++) {
      const a = ra(lx - 1, ly), b = ra(lx, ly); if (!a || !b || a === b) continue;
      if (a.id === 'hol' || b.id === 'hol') continue;
      if (gapsV[lx + ',' + ly]) continue;
      ent(BX + lx + BY + ly + 0.5, sx(BX + lx, BY + ly), sy(BX + lx, BY + ly), S.partV(kind(a, b), b.ac));
      wallV.add((BX + lx) + ',' + (BY + ly));
    }
  }

  /* ---------- yerleşim ---------- */
  const SEATD = {}; // masa anahtarı → ekran girişi
  function pod(room, lx, deskY, seatY, wood, seedBase, opt) {
    opt = opt || {};
    const dsk = L(S.desk('y', wood || '#b98a55', seedBase + lx), lx, deskY);
    const scr = ent(BX + lx + BY + deskY + 1.02, sx(BX + lx, BY + deskY), sy(BX + lx, BY + deskY), null);
    const seat = { room: room, lx: lx, ly: seatY, tx: BX + lx, ty: BY + seatY, scr: scr, deskE: dsk, occ: null, kind: opt.kind };
    W.block(seat.tx, seat.ty);
    seat.chair = ent(seat.tx + seat.ty + 1.2, sx(seat.tx, seat.ty) , sy(seat.tx, seat.ty) + HH, null);
    seat.chair.s = null;
    seat.chairLook = O.look(seedBase * 7 + lx * 3 + seatY).chair;
    W.screens.push({ scr: scr, dir: 'y' });
    return seat;
  }
  W.seatPos = (seat) => ({ x: sx(seat.tx, seat.ty), y: sy(seat.tx, seat.ty) + HH });

  function buildFurniture() {
    const seats = W.seats;
    /* --- MAKAM --- */
    L(S.bigDesk('a'), 1, 1); L(S.bigDesk('b'), 2, 1);
    L(S.shelf('x', 'tall', 11), 0, 1); L(S.shelf('x', 'tall', 12), 0, 2);
    L(S.globe(), 3, 0); L(S.plant('tall'), 3, 3); L(S.plant('small'), 0, 3); L(S.floorLamp(), 3, 2);
    W.staff.push({ id: 'makam', room: 'makam', tx: BX + 1, ty: BY, pose: 'sitF', look: O.look(901, 'makam', { acc: 'tie', shirt: '#2c3342', pants: '#1f2430', hs: 'short', hair: '#d9d4c8', chair: '#7a2f2f', skin: '#e5b88e' }), blockSeat: true });
    W.block(BX + 1, BY); W.block(BX + 2, BY);
    W.emptyChairs = [{ tx: BX + 1, ty: BY + 2, c: '#7a2f2f' }, { tx: BX + 2, ty: BY + 2, c: '#7a2f2f' }];
    /* --- SEKRETERLİK --- */
    L(S.shelf('y', 'tall', 21), 6, 0); L(S.shelf('y', 'tall', 22), 7, 0); L(S.shelf('y', 'low', 23), 4, 0);
    const sk = pod('sekreterlik', 5, 1, 2, '#c9a36a', 30, { kind: 'staff' });
    sk.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'sekreter', room: 'sekreterlik', seat: sk, pose: 'sit', look: O.look(911, 'sek', { shirt: '#c05a8a', hs: 'bun', hair: '#4a3322', acc: '' }) });
    L(S.printer(), 7, 2); L(S.plant('tall'), 4, 3); L(S.cabinet('y'), 7, 3);
    /* --- FİNANS --- */
    L(S.safe(), 8, 0); L(S.coins(), 11, 1);
    const f1 = pod('finans', 10, 1, 2, '#d8d2c2', 40, { kind: 'staff' }); f1.scr.s = S.screen('y', 'staff');
    const f2 = pod('finans', 8, 2, 3, '#d8d2c2', 41, { kind: 'staff' }); f2.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'finans1', room: 'finans', seat: f1, pose: 'sit', look: O.look(921, 'fin', { acc: 'visor', shirt: '#e9e4d2' }) });
    W.staff.push({ id: 'finans2', room: 'finans', seat: f2, pose: 'sit', look: O.look(922, 'fin', { shirt: '#3b82c4', hs: 'long' }) });
    L(S.plant('tall'), 11, 3);
    /* --- HABERLEŞME --- */
    const h1 = pod('haberlesme', 13, 1, 2, '#9aa5b4', 50, { kind: 'staff' }); h1.scr.s = S.screen('y', 'staff');
    const h2 = pod('haberlesme', 15, 1, 2, '#9aa5b4', 51, { kind: 'staff' }); h2.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'haber1', room: 'haberlesme', seat: h1, pose: 'sit', look: O.look(931, 'hab', { acc: 'headset', shirt: '#3b6fb4' }) });
    W.staff.push({ id: 'haber2', room: 'haberlesme', seat: h2, pose: 'sit', look: O.look(932, 'hab', { acc: 'headset', shirt: '#2f9aa8', hs: 'long' }) });
    L(S.mailbox(), 12, 3); L(S.plant('small'), 15, 3); L(S.cooler(), 14, 3);
    W.mailboxLocal = [12, 3];
    /* --- RİSK --- */
    const r1 = pod('risk', 17, 1, 2, '#c9b9a0', 60, { kind: 'staff' }); r1.scr.s = S.screen('y', 'staff');
    const r2 = pod('risk', 19, 1, 2, '#c9b9a0', 61, { kind: 'staff' }); r2.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'risk1', room: 'risk', seat: r1, pose: 'sit', look: O.look(941, 'risk', { acc: 'vest', shirt: '#f28c28' }) });
    W.staff.push({ id: 'risk2', room: 'risk', seat: r2, pose: 'sit', look: O.look(942, 'risk', { shirt: '#b5472f', acc: 'glasses' }) });
    L(S.beacon(), 16, 0); W.beaconE = ent(BX + 16 + BY + 0 + 1.02, sx(BX + 16, BY), sy(BX + 16, BY), null);
    L(S.cabinet('y'), 16, 3); L(S.plant('small'), 19, 3);
    /* --- DENETİM --- */
    ['20', '21', '22'].forEach(x => { L(S.rack('y'), +x, 0); W.leds['rack' + x] = ent(BX + +x + BY + 1.02, sx(BX + +x, BY), sy(BX + +x, BY), null); });
    const d1 = pod('denetim', 21, 2, 3, '#aeb8c6', 70, { kind: 'staff' }); d1.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'denetim', room: 'denetim', seat: d1, pose: 'sit', look: O.look(951, 'den', { acc: 'glasses', shirt: '#6b7a8f' }) });
    L(S.cabinet('y'), 22, 2); L(S.plant('small'), 20, 3, { block: false });
    /* --- ARŞİV --- */
    ['23', '24', '25'].forEach((x, i) => L(S.shelf('y', 'tall', 31 + i), +x, 0));
    L(S.shelf('y', 'arsiv', 36), 24, 2);
    L(S.box(1), 25, 2); W.boxSlots = [[25, 3], [25, 3], [25, 3], [25, 3], [25, 3]];
    W.block(BX + 25, BY + 3);
    W.staff.push({ id: 'arsivci', room: 'arsiv', tx: BX + 24, ty: BY + 3, pose: 'stand', dir: 'u', look: O.look(961, 'ars', { shirt: '#9a6b3b', acc: 'glasses', hs: 'bald' }) });
    /* --- TARAMA --- */
    const t1 = pod('tarama', 2, 5, 6, '#b9a9d0', 80, { kind: 'staff' }); t1.scr.s = S.screen('y', 'staff');
    const t2 = pod('tarama', 4, 5, 6, '#b9a9d0', 81, { kind: 'staff' }); t2.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'tarama1', room: 'tarama', seat: t1, pose: 'sit', look: O.look(971, 'tar', { shirt: '#6a4fa0', hs: 'short' }) });
    W.staff.push({ id: 'tarama2', room: 'tarama', seat: t2, pose: 'sit', look: O.look(972, 'tar', { shirt: '#2f9aa8', hs: 'long' }) });
    L(S.printer(), 0, 7); L(S.printer(), 0, 8); L(S.plant('tall'), 4, 8); L(S.plant('small'), 0, 4);
    /* --- ÇAY OCAĞI --- */
    L(S.counter('u', 'tea'), 6, 4); L(S.counter('u', ''), 7, 4); L(S.fridge('y'), 7, 5);
    L(S.table('round'), 6, 7); L(S.stool(), 5, 7); L(S.plant('small'), 5, 8); L(S.vending(), 5, 5);
    W.staff.push({ id: 'cayci', room: 'cay', tx: BX + 6, ty: BY + 5, pose: 'stand', dir: 'u', look: O.look(981, 'cay', { acc: 'apron', shirt: '#d9d4c8', hs: 'bun', hair: '#2b2118' }), cayci: true });
    /* --- LAB --- (koltuk sütunları arasında boş koridor sütunları: her koltuğa ulaşılır) */
    [9, 10, 12, 13, 15, 16].forEach((x, i) => { seats.lab.push(pod('lab', x, 4, 5, '#ccd6e0', 100 + i)); seats.lab.push(pod('lab', x, 7, 8, '#ccd6e0', 120 + i)); });
    L(S.cooler(), 8, 4); L(S.plant('tall'), 11, 4); L(S.board(), 17, 5); L(S.plant('tall'), 17, 4); L(S.plant('small'), 14, 4);
    /* --- KONTROL --- */
    [19, 20, 22, 23, 25].forEach((x, i) => { seats.kontrol.push(pod('kontrol', x, 4, 5, '#b9c4d2', 140 + i)); seats.kontrol.push(pod('kontrol', x, 7, 8, '#b9c4d2', 160 + i)); });
    L(S.dice(), 18, 4); L(S.plant('tall'), 21, 4); L(S.plant('tall'), 24, 4);
    /* --- HOL --- */
    L(S.plant('tall'), 0, 9); L(S.bench('u'), 4, 9); L(S.bench('u'), 8, 9); L(S.plant('tall'), 12, 9); L(S.cooler(), 16, 9); L(S.bench('u'), 18, 9); L(S.plant('tall'), 25, 9); L(S.plant('small'), 25, 10);
    /* --- ADAY --- */
    [0, 2, 3, 5].forEach((x, i) => { seats.aday.push(pod('aday', x, 11, 12, '#d7b48a', 200 + i)); seats.aday.push(pod('aday', x, 14, 15, '#d7b48a', 220 + i)); });
    L(S.plant('tall'), 1, 11, { block: false }); W.block(BX + 1, BY + 11); L(S.plant('small'), 4, 11);
    /* --- ODA --- */
    [7, 8, 10, 11, 13, 14, 16, 17, 19, 20].forEach((x, i) => { seats.oda.push(pod('oda', x, 11, 12, '#a8b2cc', 300 + i)); seats.oda.push(pod('oda', x, 14, 15, '#a8b2cc', 330 + i)); });
    [6, 12, 18, 21].forEach(x => L(S.plant('tall'), x, 11));
    /* --- KAPI --- */
    L(S.turnstile(), 24, 12); L(S.turnstile(), 24, 14);
    const g = pod('kapi', 22, 14, 15, '#9aa5b4', 400, { kind: 'staff' }); g.scr.s = S.screen('y', 'staff');
    W.staff.push({ id: 'kapici', room: 'kapi', seat: g, pose: 'sit', look: O.look(991, 'kapi', { acc: 'cap', shirt: '#1f3a6e' }) });
    L(S.plant('tall'), 22, 11); L(S.plant('tall'), 25, 11); L(S.plant('small'), 25, 15); L(S.bench('u'), 23, 15);
  }
  W.sitDir = 'u';

  /* ---------- çevre ---------- */
  function buildOutside() {
    const taken = new Set();
    const ok = (x, y) => { const t = type[x + ',' + y]; return t && t.k === 'grass' && !taken.has(x + ',' + y); };
    // otopark arabaları (v yönünde duran, ters çevrilmiş sprite)
    const cols = ['#d4553b', '#3b82c4', '#e0a93a', '#3aa17a', '#8a63c9', '#e8e4da', '#2c3342', '#d86b8f', '#6b7a8f', '#c0683a'];
    const r = O.rng(77);
    for (let lx = 2; lx <= 23; lx++) {
      for (const row of [18, 22]) {
        if (r() < 0.34) continue;
        const c = cols[Math.floor(r() * cols.length)], x = BX + lx, y = BY + row;
        const s = O.flip(S.car(c, lx * 7 + row));
        ent(x + y + 1.5, sx(x, y), sy(x, y), s);
        W.block(x, y); W.block(x, y + 1);
      }
    }
    // giriş süsleri: çiçek tavaları, bank, tabela
    [[BX + BW, BY + 10, '#ff6b8a'], [BX + BW + 1, BY + 14, '#ffd24a'], [BX + BW, BY + 15, '#ffffff'], [BX + BW + 2, BY + 10, '#f5a3c0']].forEach((q, i) => {
      if (!ok(q[0], q[1])) return; ent(q[0] + q[1] + 1, sx(q[0], q[1]), sy(q[0], q[1]) + HH + 2, S.bush(40 + i, q[2])); W.block(q[0], q[1]); taken.add(q[0] + ',' + q[1]);
    });
    ent(BX + BW + 3 + BY + 15 + 1, sx(BX + BW + 3, BY + 15), sy(BX + BW + 3, BY + 15) + HH, S.signpost()); W.block(BX + BW + 3, BY + 15); taken.add((BX + BW + 3) + ',' + (BY + 15));
    // park lambaları
    [[BX + 2, BY + 20], [BX + 12, BY + 20], [BX + 22, BY + 20]].forEach(p => { const e = ent(p[0] + p[1] + 1.1, sx(p[0], p[1]) , sy(p[0], p[1]) + HH, S.lamp()); W.lamps.push(e); });
    // çalılar bina önünde
    for (let lx = 0; lx < 26; lx++) {
      if (lx >= 21 && lx <= 25) continue;
      const x = BX + lx, y = BY + BH + 1;
      if (r() < 0.75 && ok(x, y)) { ent(x + y + 1, sx(x, y), sy(x, y) + HH + 2, S.bush(lx, r() < 0.55 ? ['#ff6b8a', '#ffd24a', '#ffffff'][lx % 3] : null)); W.block(x, y); taken.add(x + ',' + y); }
    }
    // ağaçlar
    const kinds = ['g', 'g', 'o', 'pine', 'g', 'y', 'pine', 'o'];
    for (let x = 0; x < WW - 3; x++) for (let y = 0; y < WH - 1; y++) {
      const lx = x - BX, ly = y - BY;
      if (!ok(x, y)) continue;
      const inBldg = lx >= -1 && lx <= BW + 1 && ly >= -1 && ly <= BH + 1;
      if (inBldg) continue;
      const near = (lx > BW - 2 && ly > BH - 6 && ly < BH + 8 && lx < BW + 5 && ly >= 8) ; // giriş yolu çevresi
      if (near) continue;
      const d = O.h2(x, y, 55);
      const edge = (lx < -1 || ly < -1 || lx > BW + 1);
      if (d < (edge ? 0.26 : 0.1) && O.h2(x, y, 56) > 0.2) {
        if (taken.has((x - 1) + ',' + y) || taken.has(x + ',' + (y - 1)) || taken.has((x - 1) + ',' + (y - 1))) continue;
        const k = kinds[Math.floor(O.h2(x, y, 57) * kinds.length)];
        const e = ent(x + y + 1, sx(x, y), sy(x, y) + HH, S.tree(k, x * 31 + y));
        e.sway = O.h2(x, y, 58) * 6.28; e.tree = true; W.trees.push(e);
        W.block(x, y); taken.add(x + ',' + y);
      }
    }
  }

  function buildTVs() {
    const tv = (id, side, lx, ly, span) => {
      const x = BX + lx, y = BY + ly, k = side === 'L' ? (x + span - 1) + y + 0.43 : x + (y + span - 1) + 0.43;
      W.tvs[id] = { side: side, span: span, e: ent(k, sx(x, y), sy(x, y), null) };
    };
    tv('finans', 'L', 9, 0, 2); tv('haber', 'L', 12, 0, 3); tv('risk', 'L', 17, 0, 2); tv('tarama', 'R', 0, 5, 2);
  }
  W.resort = function () { W.statics.sort((a, b) => a.k - b.k); };
  W.build = function () {
    buildTypes(); buildGround(); buildWalls(); buildTVs(); buildFurniture(); buildOutside();
    W.resort();
  };
  W.localToWorld = (lx, ly) => [BX + lx, BY + ly];
  W.sign = function (r) { const yy = r.y + (r.y === 0 ? 0.9 : 0.5); return { x: sx(BX + r.cx, BY + yy), y: sy(BX + r.cx, BY + yy) - (r.y === 0 ? 40 : 26) }; };
  /* oda çokgeni (zemin) ekran noktaları */
  W.roomPoly = function (r) { const a = [BX + r.x, BY + r.y], b = [BX + r.x + r.w, BY + r.y + r.h]; return [[sx(a[0], a[1]), sy(a[0], a[1])], [sx(b[0], a[1]), sy(b[0], a[1])], [sx(b[0], b[1]), sy(b[0], b[1])], [sx(a[0], b[1]), sy(a[0], b[1])]]; };
})();
