/* Ofis · tema seçimi (Klasik / İzometrik). Çizici arayüzü: ciz(data), odaSec(anahtar), temizle().
   Klasik tema mevcut piksel kodu (main.js/office.js/world.js) hiç değişmeden sarar; bu dosya yalnız
   dışarıdan onu seçer/bırakır. Oda içi görünüm, panel ve olay çekmecesi her iki temada da ortaktır:
   İzometrik tema yalnızca "binanın tümü" görünümünü değiştirir (referans görsel + tıklanabilir bölge
   + canlı rozet); bir odaya girilince mevcut piksel oda-içi sahnesi aynen açılır. Referans görsel
   yalnız İzometrik ilk kez gösterildiğinde yüklenir (klasik temada hiç istek gitmez). */
(function () {
  'use strict';
  const O = window.OFIS;
  const $ = s => document.querySelector(s);
  const T = (O.Tema = {});
  const KEY = 'sgofis.tema';
  const GECERLI = { klasik: 1, izometrik: 1 };

  function okuLS() { try { const v = localStorage.getItem(KEY); return GECERLI[v] ? v : null; } catch (e) { return null; } }
  function yazLS(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* okunamıyorsa sessizce yalnız bu oturumda kalır */ } }
  function okuURL() { try { const v = new URLSearchParams(location.search).get('tema'); return GECERLI[v] ? v : null; } catch (e) { return null; } }

  let mevcut = okuURL() || okuLS() || 'klasik';
  T.get = () => mevcut;
  T.set = function (v) {
    if (!GECERLI[v]) return;
    mevcut = v; yazLS(v); uygula();
  };

  /* ---------- görünürlük: oda içindeyken (body.oda-ici) her zaman ortak piksel sahnesi; binanın tümünde temaya göre ---------- */
  function odaIcindeMi() { return document.body.classList.contains('oda-ici'); }
  function uygula() {
    document.body.classList.toggle('tema-izo', mevcut === 'izometrik');
    const kap = $('#izoKap'); if (!kap) return;
    const goster = mevcut === 'izometrik' && !odaIcindeMi();
    kap.hidden = !goster;
    const tuval = $('#tuval'); if (tuval) tuval.style.visibility = goster ? 'hidden' : 'visible';
    const sec = $('#temaSec'); if (sec && sec.value !== mevcut) sec.value = mevcut;
    if (goster) { gorselYukle(); sigdir(false); oturt(); }
    rozetleriCiz();
  }
  new MutationObserver(uygula).observe(document.body, { attributes: true, attributeFilter: ['class'] });

  /* ---------- referans görsel: yalnız İzometrik ilk gösterildiğinde (data-src/data-srcset → src/srcset) ---------- */
  let gorselYuklendi = false;
  function gorselYukle() {
    if (gorselYuklendi) return; gorselYuklendi = true;
    const img = $('#izoImg'), kaynak = img && img.closest('picture').querySelector('source');
    if (kaynak && kaynak.dataset.srcset) { kaynak.srcset = kaynak.dataset.srcset; delete kaynak.dataset.srcset; }
    if (img && img.dataset.src) { img.src = img.dataset.src; delete img.dataset.src; }
  }

  /* ---------- bölge verisi ---------- */
  let BOLGELER = [];
  async function veriYukle() {
    try {
      const r = await fetch('tema/izometrik.json', { cache: 'no-store' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      BOLGELER = (j.bolgeler || []).slice();
    } catch (e) { BOLGELER = []; }
    izoCiz();
  }

  /* ---------- rozet hesabı (yalnız okuma; office.js state'inden) ---------- */
  function off() { return O.Office; }
  function st() { const o = off(); return o && o.state ? o.state() : null; }
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] || c));
  const usd = v => (v == null ? null : (v < 0 ? '−' : '') + '$' + Math.abs(v).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
  function finansBadge(s) {
    const o = off(), g = o.gri('finans'); if (g) return { t: g, c: 'gri' };
    const k = s.kasa; if (k.deger_usd == null) return { t: 'bilinmiyor', c: 'bil' };
    const getiri = k.baslangic_usd ? (k.deger_usd / k.baslangic_usd - 1) * 100 : null;
    const gt = getiri == null ? '' : ' · ' + (getiri < 0 ? '−' : '+') + Math.abs(getiri).toFixed(1) + '%';
    return { t: usd(k.deger_usd) + gt, c: getiri == null ? '' : (getiri < 0 ? 'dn' : getiri > 0 ? 'ok' : '') };
  }
  /* Risk: en kötü tavan kullanımı (ışık: 🟢/🟡/🔴). "Kalabalık" uyarısı yalnız kapasite bilinen kaynakta (ör. örnek veri)
     eklenir — gerçek veride oda.kapasite şimdilik hiç gelmiyor (gercek.js), sahte doluluk uydurulmaz. */
  function riskBadge(s) {
    const o = off(), g = o.gri('risk'); if (g) return { t: g, c: 'gri' };
    const tv = s.risk.tavanlar; if (!tv.length) return { t: 'bilinmiyor', c: 'bil' };
    let worst = tv[0], wr = 0;
    tv.forEach(t => { const r = t.tavan ? t.kullanim / t.tavan : 0; if (r > wr) { wr = r; worst = t; } });
    const c = wr >= 0.999 ? 'dn' : wr >= 0.75 ? 'wr' : 'ok', isik = c === 'dn' ? '🔴' : c === 'wr' ? '🟡' : '🟢';
    const kap = s.katlar.oda.kapasite, kalabalik = kap != null && s.katlar.oda.n != null && s.katlar.oda.n >= kap * 0.9 ? ' · kalabalık' : '';
    return { t: isik + ' ' + (s.alarm ? 'TAVAN DOLU' : esc(worst.ad) + ' %' + Math.round(wr * 100)) + kalabalik, c: c };
  }
  function labBadge(s) {
    const o = off(), g = o.gri('lab'); if (g) return { t: g, c: 'gri' };
    const inf = o.ageInfo('lab');
    return { t: O.Panel.ageTxt(inf), c: inf && inf.stale ? 'wr' : 'ok' };
  }
  const ISIK = { yesil: 'yesil', yeşil: 'yesil', sari: 'sari', sarı: 'sari', kirmizi: 'kirmizi', kırmızı: 'kirmizi' };
  /* Oda sağlığı: önce gerçek veride gelen trader.saglik.isik (bayrak varsa kırmızı sayılır); bu alan yoksa (ör. örnek
     veri) açık işlemlerin likidasyona uzaklığından (≤%10 kırmızı, ≤%20 sarı) türetilir. İkisi de yoksa "veri yok". */
  function odaBadge(s) {
    const o = off(), g = o.gri('oda'); if (g) return { t: g, c: 'gri' };
    const n = s.katlar.oda.n; if (n == null) return { t: 'bilinmiyor', c: 'bil' };
    const odaTraders = Object.keys(s.traders).map(id => s.traders[id]).filter(t => t.kat === 'oda');
    const saglikVar = odaTraders.some(t => t.saglik && t.saglik.isik);
    let yesil = 0, sari = 0, kirmizi = 0, bilinmeyen = 0;
    if (saglikVar) {
      odaTraders.forEach(t => {
        const isik = t.bayrak ? 'kirmizi' : ISIK[String((t.saglik || {}).isik || '').toLocaleLowerCase('tr')];
        if (isik === 'kirmizi') kirmizi++; else if (isik === 'sari') sari++; else if (isik === 'yesil') yesil++; else bilinmeyen++;
      });
    } else {
      odaTraders.forEach(t => {
        const ac = s.acik.filter(x => x.trader === t.id && x.lik_uzaklik != null);
        if (!ac.length) { bilinmeyen++; return; }
        const worst = Math.min.apply(null, ac.map(x => x.lik_uzaklik));
        if (worst <= 10) kirmizi++; else if (worst <= 20) sari++; else yesil++;
      });
    }
    const saglikN = yesil + sari + kirmizi;
    const kalan = bilinmeyen ? ' · ' + bilinmeyen + ' veri yok' : '';
    return { t: n + ' trader · ' + (saglikN ? '🟢' + yesil + ' 🟡' + sari + ' 🔴' + kirmizi + kalan : 'sağlık verisi yok'), c: kirmizi ? 'dn' : sari ? 'wr' : saglikN ? 'ok' : 'bil' };
  }
  function kapiBadge(s) {
    const o = off(), g = o.gri('kapi'); if (g) return { t: g, c: 'gri' };
    const inf = o.ageInfo('kapi');
    return { t: 'son tarama: ' + O.Panel.ageTxt(inf), c: inf && inf.stale ? 'wr' : 'ok' };
  }
  function arsivBadge(s) {
    const o = off(), g = o.gri('arsiv'); if (g) return { t: g, c: 'gri' };
    const row = s.vk.find(x => x.anahtar === 'arsiv'), inf = o.ageInfo('arsiv');
    const val = row && row.deger != null ? row.deger : null;
    return { t: val != null ? esc(val) : O.Panel.ageTxt(inf), c: inf && inf.stale ? 'wr' : 'ok' };
  }
  function makamBadge(s) {
    const k = s.kk; if (k.hafta == null) return { t: 'bilinmiyor', c: 'bil' };
    const kararN = (s.gecmis || []).concat(s.oturum || []).filter(e => e.tur === 'kullanici_karari').length;
    return { t: 'hafta ' + k.hafta + '/' + k.hafta_toplam + (kararN ? ' · karar ' + kararN : ''), c: '' };
  }
  function sekreterlikBadge(s) {
    const ok = s.onkayit; if (!ok || ok.surum == null) return { t: 'bilinmiyor', c: 'bil' };
    return { t: 'ön kayıt ' + esc(String(ok.surum)), c: '' };
  }
  const ROZET = { finans: finansBadge, risk: riskBadge, lab: labBadge, oda: odaBadge, kapi: kapiBadge, arsiv: arsivBadge, makam: makamBadge, sekreterlik: sekreterlikBadge };

  /* ---------- çizim: bölge tıklama hedefleri + rozetler ---------- */
  function bbox(poli) {
    let x0 = 1, y0 = 1, x1 = 0, y1 = 0;
    poli.forEach(p => { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); });
    return { x0, y0, x1, y1 };
  }
  function izoCiz() {
    const bk = $('#izoBolgeler'), rk = $('#izoRozetler'); if (!bk || !rk) return;
    bk.innerHTML = ''; rk.innerHTML = '';
    BOLGELER.forEach(b => {
      const clip = 'polygon(' + b.poli.map(p => (p[0] * 100).toFixed(2) + '% ' + (p[1] * 100).toFixed(2) + '%').join(',') + ')';
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'izo-bolge'; btn.dataset.oda = b.oda;
      btn.style.clipPath = clip; btn.setAttribute('aria-label', (O.Names ? O.Names.room(b.oda, b.ad) : b.ad) + ': oda içine gir');
      btn.addEventListener('click', () => bolgeTik(b.oda));
      bk.appendChild(btn);
      if (ROZET[b.oda]) {
        const bx = bbox(b.poli), cx = (bx.x0 + bx.x1) / 2, cy = bx.y0 + (bx.y1 - bx.y0) * 0.14;
        const d = document.createElement('div');
        d.className = 'izo-rozet'; d.dataset.oda = b.oda;
        d.style.left = (cx * 100).toFixed(2) + '%'; d.style.top = (cy * 100).toFixed(2) + '%';
        rk.appendChild(d);
      }
    });
    rozetleriCiz();
  }
  function rozetleriCiz() {
    const s = st(); if (!s) return;
    document.querySelectorAll('#izoRozetler .izo-rozet').forEach(d => {
      const f = ROZET[d.dataset.oda]; if (!f) return;
      const r = f(s) || { t: 'bilinmiyor', c: 'bil' };
      d.innerHTML = r.t; d.className = 'izo-rozet' + (r.c ? ' ' + r.c : '');
    });
  }
  const mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function bolgeTik(id) {
    if (Date.now() - sonSurukleBitti < 150) return;   // sürükleme bittikten hemen sonraki sahte tıklama yok sayılır
    if (!mq.matches) { animasyonlu(true); setTimeout(() => animasyonlu(false), 260); }
    const git = () => { const b = document.querySelector('.ray [data-oda="' + id + '"]'); if (b) b.click(); };
    mq.matches ? git() : setTimeout(git, 140);
  }

  /* ---------- oturtma (contain-fit, her yeniden boyutlandırmada JS'le hesaplanır: görsel ekranı mümkün olduğunca doldurur) ---------- */
  const ORAN = 1536 / 1024;
  let scale = 1, panX = 0, panY = 0;
  function animasyonlu(on) { const s = $('#izoSahne'); if (s) s.classList.toggle('izo-anim', on); }
  function oturt() {
    const kap = $('#izoKap'), sahne = $('#izoSahne'); if (!kap || !sahne) return;
    const r = kap.getBoundingClientRect();
    let w = r.width, h = w / ORAN;
    if (h > r.height) { h = r.height; w = h * ORAN; }
    sahne.style.width = Math.max(1, w) + 'px'; sahne.style.height = Math.max(1, h) + 'px';
    uygulaDonusum(false);
  }
  function uygulaDonusum(animate) {
    const sahne = $('#izoSahne'); if (!sahne) return;
    animasyonlu(!!animate && !mq.matches);
    sahne.style.transform = 'translate(-50%, -50%) translate(' + panX + 'px, ' + panY + 'px) scale(' + scale + ')';
  }
  function siniraCek() {
    const kap = $('#izoKap'); if (!kap) return;
    const maxX = kap.clientWidth * (scale - 1) / 2, maxY = kap.clientHeight * (scale - 1) / 2;
    panX = Math.max(-maxX, Math.min(maxX, panX)); panY = Math.max(-maxY, Math.min(maxY, panY));
  }
  function zoomBy(f) { scale = Math.max(1, Math.min(3, scale * f)); siniraCek(); uygulaDonusum(true); }
  function sigdir(animate) { scale = 1; panX = 0; panY = 0; uygulaDonusum(animate !== false); }
  if (window.ResizeObserver) { const ro = new ResizeObserver(() => oturt()); const kap0 = document.getElementById('izoKap'); if (kap0) ro.observe(kap0); }

  /* tek parmak/işaretçi sürükleme (yalnız yakınlaşmışken); çift işaretçi (parmakla) kabaca yakınlaştırır */
  let surukle = null, sonSurukleBitti = 0; const isaretciler = new Map();
  function surukleBagla() {
    const kap = $('#izoKap'); if (!kap) return;
    /* yakalama (setPointerCapture) yalnız gerçek sürükleme başladığında alınır; basit dokunma/tıklama altındaki
       bölge düğmesine (clip-path) değmeden ulaşsın diye — erken yakalama tıklamayı üst öğeye kaydırabiliyor. */
    kap.addEventListener('pointerdown', e => { isaretciler.set(e.pointerId, { x: e.clientX, y: e.clientY }); surukle = { id: e.pointerId, x: e.clientX, y: e.clientY, px: panX, py: panY, moved: false, captured: false }; });
    kap.addEventListener('pointermove', e => {
      if (!isaretciler.has(e.pointerId)) return;
      isaretciler.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (isaretciler.size === 2) {
        if (surukle && !surukle.captured) { try { kap.setPointerCapture(surukle.id); } catch (err) { /* yoksay */ } surukle.captured = true; }
        const p = [...isaretciler.values()], d = Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
        if (!surukle || !surukle.pinchD) surukle = Object.assign(surukle || {}, { pinchD: d, pinchS: scale });
        scale = Math.max(1, Math.min(3, surukle.pinchS * d / Math.max(1, surukle.pinchD))); siniraCek(); uygulaDonusum(false);
        return;
      }
      if (!surukle) return;
      const dx = e.clientX - surukle.x, dy = e.clientY - surukle.y;
      if (!surukle.moved && Math.abs(dx) + Math.abs(dy) > 6) { surukle.moved = true; if (scale > 1 && !surukle.captured) { try { kap.setPointerCapture(e.pointerId); } catch (err) { /* yoksay */ } surukle.captured = true; } }
      if (surukle.moved && scale > 1) { panX = surukle.px + dx; panY = surukle.py + dy; siniraCek(); uygulaDonusum(false); }
    });
    const biten = e => { isaretciler.delete(e.pointerId); if (surukle && surukle.moved) sonSurukleBitti = Date.now(); if (isaretciler.size < 2 && surukle) delete surukle.pinchD; if (!isaretciler.size) surukle = null; };
    kap.addEventListener('pointerup', biten); kap.addEventListener('pointercancel', biten); kap.addEventListener('pointerleave', biten);
    kap.addEventListener('wheel', e => { e.preventDefault(); zoomBy(Math.exp(-e.deltaY * 0.0012)); }, { passive: false });
  }

  /* ---------- kurulum ---------- */
  function init() {
    const sec = $('#temaSec');
    if (sec) { sec.value = mevcut; sec.addEventListener('change', () => T.set(sec.value)); }
    const inb = $('#izoIn'), outb = $('#izoOut'), fitb = $('#izoSigdir');
    if (inb) inb.addEventListener('click', () => zoomBy(1.35));
    if (outb) outb.addEventListener('click', () => zoomBy(1 / 1.35));
    if (fitb) fitb.addEventListener('click', () => sigdir(true));
    surukleBagla();
    veriYukle().then(uygula);
    if (O.Office && O.Office.on) O.Office.on(rozetleriCiz);
    if (O.Names && O.Names.onChange) O.Names.onChange(izoCiz);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  T.debug = { get bolgeler() { return BOLGELER; }, rozet: id => { const s = st(); return s && ROZET[id] ? ROZET[id](s) : null; }, get scale() { return scale; } };
})();
