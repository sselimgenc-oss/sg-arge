/* Ofis · tema seçimi (Klasik / İzometrik). Çizici arayüzü: ciz(data), odaSec(anahtar), temizle().
   Klasik tema mevcut piksel kodu (main.js/office.js/world.js) hiç değişmeden sarar; bu dosya yalnız
   dışarıdan onu seçer/bırakır. Panel, bilgi kutusu ve olay çekmecesi her iki temada da aynı veriden,
   aynı sol menü/PANEL_ESLE mantığıyla çalışır (ortak). Ama GÖRSEL ayrıdır: klasik temada bir odaya
   girmek kendi piksel kamerasını (#tuval) yakınlaştırır; izometrik temada aynı tıklama kendi
   referans görselini (#izoKap) o odaya yakınlaştırır — izometrik temadayken #tuval hiç görünmez,
   odaya girildiğinde "diğer temaya" geçilmez. Referans görsel yalnız İzometrik ilk gösterildiğinde
   yüklenir (klasik temada hiç istek gitmez). */
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

  /* mevcut oda (varsa) main.js'in dışarı verdiği debug.mode'dan okunur — main.js'e dokunulmadan. */
  function aktifOda() { const m = O.debug && O.debug.mode; return m && m.active ? m.room : null; }

  /* ---------- görünürlük: izometrik temadayken binanın tümünde de, oda içindeyken de #izoKap görünür;
     #tuval (klasik piksel sahnesi) izometrik temada hiç açılmaz — iki görsel birbirine karışmaz. ---------- */
  function uygula() {
    document.body.classList.toggle('tema-izo', mevcut === 'izometrik');
    const kap = $('#izoKap'); if (!kap) return;
    const goster = mevcut === 'izometrik';
    kap.hidden = !goster;
    const tuval = $('#tuval'); if (tuval) tuval.style.visibility = goster ? 'hidden' : 'visible';
    const sec = $('#temaSec'); if (sec && sec.value !== mevcut) sec.value = mevcut;
    if (goster) { gorselYukle(); oturt(); odaOdaklaSync(true); }
    rozetleriCiz();
  }
  /* oda girişi/çıkışı body.oda-ici sınıfıyla main.js'te değişir: burada izlenip kendi yakınlaşmamız uygulanır. */
  function odaOdaklaSync(animate) {
    if (mevcut !== 'izometrik') return;
    const id = aktifOda();
    if (id) odaOdakla(id, animate); else sigdir(animate);
  }
  new MutationObserver(() => { uygula(); }).observe(document.body, { attributes: true, attributeFilter: ['class'] });

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
  /* tavan birimi "x" (ör. kaldıraç) ise çarpan olarak yazılır (4x); "kasa payı"/diğerleri yüzde kalır. */
  const tavanDeger = t => t.birim === 'x' ? Math.round(t.kullanim * 10) / 10 + 'x' : '%' + Math.round((t.tavan ? t.kullanim / t.tavan : 0) * 100);
  function riskBadge(s) {
    const o = off(), g = o.gri('risk'); if (g) return { t: g, c: 'gri' };
    const tv = s.risk.tavanlar; if (!tv.length) return { t: 'bilinmiyor', c: 'bil' };
    let worst = tv[0], wr = 0;
    tv.forEach(t => { const r = t.tavan ? t.kullanim / t.tavan : 0; if (r > wr) { wr = r; worst = t; } });
    const c = wr >= 0.999 ? 'dn' : wr >= 0.75 ? 'wr' : 'ok', isik = c === 'dn' ? '🔴' : c === 'wr' ? '🟡' : '🟢';
    const kap = s.katlar.oda.kapasite, kalabalik = kap != null && s.katlar.oda.n != null && s.katlar.oda.n >= kap * 0.9 ? ' · kalabalık' : '';
    return { t: isik + ' ' + (s.alarm ? 'TAVAN DOLU' : esc(worst.ad) + ' ' + tavanDeger(worst)) + kalabalik, c: c };
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
    if (val == null && !inf) return { t: 'bilinmiyor', c: 'bil' };
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
    const bk = $('#izoBolgeler'), rk = $('#izoRozetler'), pk = $('#izoParlak'); if (!bk || !rk) return;
    bk.innerHTML = ''; rk.innerHTML = ''; if (pk) pk.innerHTML = '';
    BOLGELER.forEach(b => {
      const clip = 'polygon(' + b.poli.map(p => (p[0] * 100).toFixed(2) + '% ' + (p[1] * 100).toFixed(2) + '%').join(',') + ')';
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'izo-bolge'; btn.dataset.oda = b.oda;
      btn.style.clipPath = clip; btn.setAttribute('aria-label', (O.Names ? O.Names.room(b.oda, b.ad) : b.ad) + ': oda içine gir');
      btn.addEventListener('click', () => bolgeTik(b.oda));
      bk.appendChild(btn);
      if (pk) { const g = document.createElement('div'); g.className = 'izo-bolge-glow'; g.dataset.oda = b.oda; g.style.clipPath = clip; pk.appendChild(g); }
      if (ROZET[b.oda]) {
        const bx = bbox(b.poli);
        const cx = Math.max(0.07, Math.min(0.93, (bx.x0 + bx.x1) / 2)), cy = Math.max(0.06, Math.min(0.88, bx.y0 + (bx.y1 - bx.y0) * 0.14));
        const d = document.createElement('div');
        d.className = 'izo-rozet'; d.dataset.oda = b.oda; d.dataset.cx = cx; d.dataset.cy = cy;
        d.style.left = (cx * 100).toFixed(2) + '%'; d.style.top = (cy * 100).toFixed(2) + '%';
        rk.appendChild(d);
      }
    });
    rozetleriCiz();
  }
  /* Arşiv ve Sekreterlik'te veri yoksa (gerçek veride şimdilik hep öyle: gercek.js bu iki alanı doldurmuyor)
     "bilinmiyor" rozetiyle gürültü yapmak yerine rozet hiç gösterilmez — oda yine tıklanabilir kalır. */
  const ROZET_GIZLE_BILINMIYORSA = { arsiv: 1, sekreterlik: 1 };
  function rozetleriCiz() {
    const s = st(); if (!s) return;
    document.querySelectorAll('#izoRozetler .izo-rozet').forEach(d => {
      const f = ROZET[d.dataset.oda]; if (!f) return;
      const r = f(s) || { t: 'bilinmiyor', c: 'bil' };
      if (r.c === 'bil' && ROZET_GIZLE_BILINMIYORSA[d.dataset.oda]) { d.hidden = true; return; }
      d.hidden = false; d.innerHTML = r.t; d.className = 'izo-rozet' + (r.c ? ' ' + r.c : '');
    });
    rozetYerlestir();
  }
  const mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  /* ---------- canlılık: klasik temadaki "her hareket bir olaydan doğar" ilkesinin izometrik karşılığı.
     Figür yürütmek için fotoğrafik görselde oda içi koordinat yok (sürüm 2'nin işi); bunun yerine aynı olay
     motorundan (office.js) beslenen oda düzeyinde canlılık: olay olan oda yumuşakça parlar (Off.highlights()),
     birimler arası olaylarda (terfi, kapı geçişi, kasa güncellemesi…) küçük bir simge bir odadan diğerine uçar. ---------- */
  function rozetKonum(oda) {
    const b = BOLGELER.find(x => x.oda === oda); if (!b) return null;
    const bx = bbox(b.poli); return { x: ((bx.x0 + bx.x1) / 2) * 100, y: ((bx.y0 + bx.y1) / 2) * 100 };
  }
  const OLAY_IKON = {
    yeni_adres: { ikon: '🔍', oda: 'kapi' }, kapi_gecti: { ikon: '✅', oda: 'kapi' }, kapi_elendi: { ikon: '❌', oda: 'kapi' },
    terfi: { ikon: '⬆️' }, kat_dusur: { ikon: '⬇️' }, havuzdan_cikar: { ikon: '🚪', oda: 'lab' },
    islem_acildi: { ikon: '📈', oda: 'oda' }, islem_kapandi: { ikon: '💰', oda: 'oda' },
    risk_tavan: { ikon: '⚠️', oda: 'risk' }, risk_normal: { ikon: '✅', oda: 'risk' }, arsiv_yazildi: { ikon: '📦', oda: 'arsiv' },
    kasa_guncelle: { ikon: '💵', oda: 'finans' }, kirmizi_bayrak: { ikon: '🚩', oda: 'oda' }, bayrak_kalkti: { ikon: '✅', oda: 'oda' },
    kural_kitabi: { ikon: '📘', oda: 'sekreterlik' }, kullanici_karari: { ikon: '🗳️', oda: 'makam' }, veri_yenile: { ikon: '🔄', oda: 'finans' }
  };
  function olayBalonu(e) {
    if (mevcut !== 'izometrik' || mq.matches) return;
    const info = OLAY_IKON[e.tur]; if (!info) return;
    const kPos = rozetKonum(e.kimden || info.oda), hPos = rozetKonum(e.kime || info.oda), bas = kPos || hPos;
    if (!bas) return;
    const rk = $('#izoBalonlar'); if (!rk) return;
    const el = document.createElement('div');
    el.className = 'izo-balon'; el.textContent = info.ikon;
    el.style.left = bas.x + '%'; el.style.top = bas.y + '%';
    rk.appendChild(el);
    requestAnimationFrame(() => {
      if (hPos && kPos && hPos.x !== kPos.x) { el.style.left = hPos.x + '%'; el.style.top = hPos.y + '%'; }
      el.classList.add('izo-balon-git');
    });
    setTimeout(() => el.remove(), 1100);
  }
  /* odada olay oldukça yumuşak parlama (Off.highlights() zaten klasik temada da aynı veriyi besliyor) — yalnız
     bir şey parlarken kare ister, boşta durur (uygulamanın "boşta kare çizilmez" kuralına uyar). */
  let canliRaf = 0;
  function canliTick() {
    canliRaf = 0;
    const o = off(); if (mevcut !== 'izometrik' || !o || !o.highlights) return;
    const map = {}; o.highlights().forEach(h => { map[h.room] = h; });
    let aktif = false;
    document.querySelectorAll('#izoParlak .izo-bolge-glow').forEach(d => {
      const h = map[d.dataset.oda], op = h ? h.a * h.pulse * 0.4 : 0;
      d.style.opacity = op.toFixed(2); if (h) aktif = true;
    });
    if (aktif) canliRaf = requestAnimationFrame(canliTick);
  }
  function canliUyandir() { if (!canliRaf && mevcut === 'izometrik' && !mq.matches) canliRaf = requestAnimationFrame(canliTick); }
  /* bölgeye tıklama: sol menüdeki aynı odanın düğmesini tetikler (adres, panel/bilgi kutusu, "aynı menüye ikinci
     tıklama kapatır" gibi tüm kurallar main.js'te zaten var — burada yalnız tetiklenir). Kamera/yakınlaşma tarafı
     body.oda-ici değişince odaOdaklaSync() ile ayrıca, kendi görselimiz üstünde yapılır (main.js'e dokunmadan). */
  function bolgeTik(id) {
    if (Date.now() - sonSurukleBitti < 150) return;   // sürükleme bittikten hemen sonraki sahte tıklama yok sayılır
    const b = document.querySelector('.ray [data-oda="' + id + '"]'); if (b) b.click();
  }

  /* ---------- oturtma/yakınlaşma: taban (contain-fit) boyut + odak noktası (0..1) + ölçek — tamamı JS'de hesaplanır.
     Görsel her zaman mevcut konteyneri mümkün olduğunca doldurur (ekranı doldursun kuralı); odaya girince aynı
     mantıkla (klasik temadaki kamera yakınlaşmasıyla birebir aynı fikir) kendi görseli üstünde yakınlaşır. ---------- */
  const ORAN = 1536 / 1024;
  let baseW = 0, baseH = 0, scale = 1, focusX = 0.5, focusY = 0.5, sonSurukleBitti = 0;
  function animasyonlu(on) { const s = $('#izoSahne'); if (s) s.classList.toggle('izo-anim', on); }
  function oturt() {
    const kap = $('#izoKap'); if (!kap) return;
    const r = kap.getBoundingClientRect();
    let w = r.width, h = w / ORAN;
    if (h > r.height) { h = r.height; w = h * ORAN; }
    baseW = Math.max(1, w); baseH = Math.max(1, h);
    uygulaDonusum(false);
    rozetYerlestir();
  }
  /* Rozetler önce oranlı (dataset.cx/cy) hedef konuma yerleşir; burada ekran kenarından taşmayacak, birbiriyle ve
     yakınlaştırma düğmeleriyle çakışmayacak şekilde küçük kaydırmalarla düzeltilir (çatışma çözümü, px tabanlı).
     Yalnız bina görünümünde çalışır (oda yakınken tek rozet öne çıkar, karışıklık daha az önemlidir). */
  function rozetYerlestir() {
    if (scale > 1.02) return;
    const sahne = $('#izoSahne'); if (!sahne) return;
    const sr = sahne.getBoundingClientRect(); if (!sr.width || !sr.height) return;
    const zoomEl = document.querySelector('.izo-zoom'), zr = zoomEl ? zoomEl.getBoundingClientRect() : null;
    const pad = 4, placed = [];
    const rectOf = (bw, bh, x, y) => ({ x0: x - bw / 2, y0: y - bh / 2, x1: x + bw / 2, y1: y + bh / 2 });
    const kesisir = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
    document.querySelectorAll('#izoRozetler .izo-rozet').forEach(d => {
      if (d.hidden || d.dataset.cx == null) return;
      const bw = d.offsetWidth, bh = d.offsetHeight; if (!bw || !bh) return;
      let cx = parseFloat(d.dataset.cx) * sr.width, cy = parseFloat(d.dataset.cy) * sr.height;
      const sinirla = () => { cx = Math.max(bw / 2 + pad, Math.min(sr.width - bw / 2 - pad, cx)); cy = Math.max(bh / 2 + pad, Math.min(sr.height - bh / 2 - pad, cy)); };
      sinirla();
      if (zr) {
        const zRel = { x0: zr.left - sr.left - 6, y0: zr.top - sr.top - 6, x1: zr.right - sr.left + 6, y1: zr.bottom - sr.top + 6 };
        let tries = 0; while (kesisir(rectOf(bw, bh, cx, cy), zRel) && tries < 24) { cy -= 8; sinirla(); tries++; }
      }
      let tries2 = 0; while (placed.some(p => kesisir(rectOf(bw, bh, cx, cy), p)) && tries2 < 30) { cy += 8; sinirla(); tries2++; }
      d.style.left = cx + 'px'; d.style.top = cy + 'px';
      placed.push(rectOf(bw, bh, cx, cy));
    });
  }
  function uygulaDonusum(animate) {
    const kap = $('#izoKap'), sahne = $('#izoSahne'); if (!kap || !sahne || !baseW) return;
    animasyonlu(!!animate && !mq.matches);
    const rw = baseW * scale, rh = baseH * scale;
    sahne.style.width = rw + 'px'; sahne.style.height = rh + 'px';
    const left = kap.clientWidth / 2 - focusX * rw, top = kap.clientHeight / 2 - focusY * rh;
    sahne.style.transform = 'translate(' + left.toFixed(1) + 'px, ' + top.toFixed(1) + 'px)';
  }
  function siniraCek() {
    const kap = $('#izoKap'); if (!kap || !baseW) return;
    const rw = baseW * scale, rh = baseH * scale;
    const mx = Math.min(0.5, (kap.clientWidth / 2) / rw), my = Math.min(0.5, (kap.clientHeight / 2) / rh);
    focusX = Math.max(mx, Math.min(1 - mx, focusX)); focusY = Math.max(my, Math.min(1 - my, focusY));
  }
  function zoomBy(f) { scale = Math.max(1, Math.min(3, scale * f)); siniraCek(); uygulaDonusum(true); rozetYerlestir(); }
  function sigdir(animate) { scale = 1; focusX = 0.5; focusY = 0.5; uygulaDonusum(animate !== false); rozetYerlestir(); }
  /* bir odaya "kamerayı" (odak + ölçek) yakınlaştır — klasik temanın interiorCam() mantığının izometrik karşılığı */
  function odaOdakla(id, animate) {
    const b = BOLGELER.find(x => x.oda === id); if (!b) { sigdir(animate); return; }
    const bx = bbox(b.poli), w = Math.max(0.02, bx.x1 - bx.x0), h = Math.max(0.02, bx.y1 - bx.y0), PAD = 1.3;
    scale = Math.max(1, Math.min(3, Math.min(1 / (w * PAD), 1 / (h * PAD))));
    focusX = (bx.x0 + bx.x1) / 2; focusY = (bx.y0 + bx.y1) / 2;
    siniraCek(); uygulaDonusum(animate !== false);
  }
  if (window.ResizeObserver) { const ro = new ResizeObserver(() => oturt()); const kap0 = document.getElementById('izoKap'); if (kap0) ro.observe(kap0); }

  /* tek parmak/işaretçi sürükleme (yalnız yakınlaşmışken); çift işaretçi (parmakla) kabaca yakınlaştırır */
  let surukle = null; const isaretciler = new Map();
  function surukleBagla() {
    const kap = $('#izoKap'); if (!kap) return;
    /* yakalama (setPointerCapture) yalnız gerçek sürükleme başladığında alınır; basit dokunma/tıklama altındaki
       bölge düğmesine (clip-path) değmeden ulaşsın diye — erken yakalama tıklamayı üst öğeye kaydırabiliyor. */
    kap.addEventListener('pointerdown', e => { isaretciler.set(e.pointerId, { x: e.clientX, y: e.clientY }); surukle = { id: e.pointerId, x: e.clientX, y: e.clientY, fx: focusX, fy: focusY, moved: false, captured: false }; });
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
      if (surukle.moved && scale > 1 && baseW) { focusX = surukle.fx - dx / (baseW * scale); focusY = surukle.fy - dy / (baseH * scale); siniraCek(); uygulaDonusum(false); }
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
    if (fitb) fitb.addEventListener('click', () => odaOdaklaSync(true));
    surukleBagla(); oturt();
    veriYukle().then(uygula);
    if (O.Office && O.Office.on) O.Office.on(() => { rozetleriCiz(); canliUyandir(); });
    if (O.Office && O.Office.onEvent) O.Office.onEvent(olayBalonu);
    if (O.Names && O.Names.onChange) O.Names.onChange(izoCiz);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  T.debug = { get bolgeler() { return BOLGELER; }, rozet: id => { const s = st(); return s && ROZET[id] ? ROZET[id](s) : null; }, get scale() { return scale; }, get focus() { return { x: focusX, y: focusY }; } };
})();
