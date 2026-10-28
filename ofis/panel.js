/* Ofis · sol panel ve gözcü kaydı. Her sayının yanında zaman damgası ya da n; veri yoksa "bilinmiyor" (sıfır değil). */
(function () {
  'use strict';
  const O = window.OFIS;
  const $ = s => document.querySelector(s);
  const P = (O.Panel = {});
  let Off, api, st, raf = 0;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const UNK = '<span class="bil">bilinmiyor</span>';
  const num = (v, d) => v == null || isNaN(v) ? null : Number(v).toLocaleString('tr-TR', { minimumFractionDigits: d == null ? 0 : d, maximumFractionDigits: d == null ? 0 : d });
  const usd = (v, sign) => { if (v == null) return UNK; const s = v < 0 ? '−' : (sign && v > 0 ? '+' : ''); return s + '$' + Math.abs(v).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  const pct = (v, sign, d) => { if (v == null) return UNK; const s = v < 0 ? '−' : (sign && v > 0 ? '+' : ''); return s + '%' + Math.abs(v).toLocaleString('tr-TR', { minimumFractionDigits: d == null ? 1 : d, maximumFractionDigits: d == null ? 1 : d }); };
  const cls = v => (v > 0 ? 'up' : v < 0 ? 'dn' : 'fl');
  const pad = n => (n < 10 ? '0' : '') + n;
  function hm(iso) { if (!iso) return 'bilinmiyor'; const d = new Date(iso); if (isNaN(d)) return 'bilinmiyor'; return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function dur(sec) { sec = Math.max(0, Math.round(sec)); const m = Math.floor(sec / 60); if (m < 1) return sec + ' sn'; if (m < 60) return m + ' dk'; const h = Math.floor(m / 60); if (h < 24) return h + ' sa ' + pad(m % 60) + ' dk'; return Math.floor(h / 24) + ' g ' + (h % 24) + ' sa'; }
  const NEDEN = { trader_kapatti: 'trader kapattı', zarar_kesme: 'zarar kesme', sure: 'süre doldu' };
  const KATAD = { lab: 'Lab', aday: 'Aday', oda: 'Oda', kontrol: 'Kontrol' };
  const ODA_AD = id => { const r = O.World.roomById[id]; return r ? O.Names.room(id, r.ad) : id; };
  const ORN = '<span class="ornek">örnek</span>';

  function kasa() {
    // ön kayıt: toplanmış performans (kasa değeri, eğri, % değişim) ofiste gösterilmez
    const k = st.kasa, el = $('#kasaIcerik'), tem = st.acik.reduce((sum, x) => sum + (x.teminat_usd || 0), 0), kk = st.kk;
    el.innerHTML = '<div class="kilit" role="note"><svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M4 7V5a4 4 0 0 1 8 0v2h1v8H3V7zm2 0h4V5a2 2 0 0 0-4 0z" fill="currentColor"/></svg><div><b>Kasa değeri kilitli</b><div class="ks">Toplanmış performans ön kayıt gereği gösterilmez (hafta ' + kk.hafta + '/' + kk.hafta_toplam + ').</div></div></div>' +
      '<div class="kasa-satir ks2"><div><span class="kl">başlangıç</span><div class="kv">' + usd(k.baslangic_usd) + '</div></div><div><span class="kl">açık işlem teminatı</span><div class="kv">' + usd(tem) + '</div></div></div>' +
      '<p class="meta">n=' + (k.gun_n == null ? 'bilinmiyor' : k.gun_n + ' gün') + ' · veri ' + hm(k.zaman) + ' · ' + ORN + '</p>';
  }
  function ozet() {
    const a = st.acik, tem = a.reduce((s, x) => s + (x.teminat_usd || 0), 0), o = st.ozet, k = st.katlar;
    const box = (l, v, sub) => '<div class="kutu"><div class="kl">' + l + '</div><div class="kv">' + v + '</div><div class="ks">' + sub + '</div></div>';
    $('#ozetIcerik').innerHTML =
      box('Açık işlem', a.length, 'teminat ' + usd(tem)) +
      box('Bugün', 'n=' + (o.bugun_acilan_n + o.bugun_kapanan_n), o.bugun_acilan_n + ' açıldı · ' + o.bugun_kapanan_n + ' kapandı') +
      box('Oda', k.oda.n + '<small>/' + k.oda.kapasite + '</small>', 'doluluk ' + pct(k.oda.n / k.oda.kapasite * 100, false, 0)) +
      box('Aday', k.aday.n, 'n=' + k.aday.n + ' · ' + hm(k.aday.zaman)) +
      box('Havuz', k.havuz.n, 'n=' + k.havuz.n + ' · ' + hm(k.havuz.zaman)) +
      box('İşlem başı', usd(o.islem_basi_usd), 'kural: kurallar.yaml');
    $('#ozetMeta').innerHTML = 'veri ' + hm(o.zaman) + ' · ' + ORN;
  }
  function liveSec(x) { return (x.yas_dk || 0) * 60 + (x.t0 ? (Date.now() - x.t0) / 1000 : (Date.now() - st.loadMs) / 1000); }
  function acik() {
    const rows = st.acik.slice().sort((a, b) => liveSec(a) - liveSec(b));
    $('#acikN').textContent = rows.length;
    if (!rows.length) { $('#acikIcerik').innerHTML = '<p class="bos">Açık gölge işlemi yok.</p>'; return; }
    const lc = v => (v == null ? '' : v <= 10 ? 'dn' : v <= 20 ? 'wr' : 'fl');
    $('#acikIcerik').innerHTML = '<table class="tab"><caption class="sr">Açık gölge işlemleri</caption><thead><tr><th scope="col">İşlem</th><th scope="col">Trader</th><th scope="col" class="r">Süre</th><th scope="col" class="r">K/Z</th><th scope="col" class="r" title="Likidasyona uzaklık">Lik.</th></tr></thead><tbody>' +
      rows.map(x => {
        const t = st.traders[x.trader] || {};
        return '<tr data-id="' + esc(x.id) + '"><td><button class="sb" data-trader="' + esc(x.trader) + '"><i class="kt ' + (x.yon === 'long' ? 'lg' : 'sh') + '"></i><b>' + esc(x.coin) + '</b> <span class="yon ' + (x.yon === 'long' ? 'lg' : 'sh') + '">' + (x.yon === 'long' ? 'LONG' : 'SHORT') + ' ' + x.kaldirac + 'x</span></button></td>' +
          '<td class="mono">' + esc((t.adres || x.trader).replace('0xAAAA', '0xAAAA')) + '</td><td class="r s" data-sure="' + esc(x.id) + '">' + dur(liveSec(x)) + '</td>' +
          '<td class="r ' + cls(x.kz_usd) + '">' + usd(x.kz_usd, true) + '<small>' + pct(x.kz_yuzde, true) + '</small></td><td class="r ' + lc(x.lik_uzaklik) + '">' + (x.lik_uzaklik == null ? UNK : pct(x.lik_uzaklik, false)) + '</td></tr>';
      }).join('') + '</tbody></table>';
    $('#acikMeta').innerHTML = 'n=' + rows.length + ' · veri ' + hm(st.ozet.zaman) + ' · trader adresleri ' + ORN;
  }
  function kapanan() {
    const el = $('#kapIcerik');
    if (!st.kapanan.length) { el.innerHTML = '<p class="bos">Henüz kapanan işlem yok.</p>'; return; }
    el.innerHTML = st.kapanan.slice(0, 5).map(x => {
      const t = st.traders[x.trader] || {};
      return '<div class="kap"><i class="kt ' + (x.kz_usd >= 0 ? 'lg' : 'sh') + '"></i><div class="kk"><b>' + esc(x.coin) + '</b> <span class="yon ' + (x.yon === 'long' ? 'lg' : 'sh') + '">' + (x.yon === 'long' ? 'LONG' : 'SHORT') + '</span><div class="ks">' + esc(NEDEN[x.neden] || x.neden) + ' · ' + dur((x.sure_dk || 0) * 60) + ' · ' + esc(t.adres || x.trader) + '</div></div><div class="kr ' + cls(x.kz_usd) + '">' + pct(x.kz_yuzde, true) + '<small>' + usd(x.kz_usd, true) + '</small></div></div>';
    }).join('');
    $('#kapMeta').innerHTML = 'n=' + Math.min(5, st.kapanan.length) + ' (son kapananlar) · ' + ORN;
  }
  function huni() {
    const k = st.katlar, tot = Math.max(1, k.havuz.n);
    const row = (ad, n, sub, w, c, extra) => '<div class="hr"><div class="hh"><b>' + ad + '</b><span>' + n + extra + '</span></div><div class="hb"><i style="width:' + Math.max(4, w) + '%;background:' + c + '"></i></div><div class="ks">' + sub + '</div></div>';
    $('#huniIcerik').innerHTML =
      row('Havuz · Lab', num(k.havuz.n), 'gölgede izlenir · ' + hm(k.havuz.zaman), 100, '#8aa4c8', '') +
      row('Aday', num(k.aday.n), 'havuzun ' + pct(k.aday.n / tot * 100, false) + ' · ' + hm(k.aday.zaman), k.aday.n / tot * 100, '#e0a14a', '') +
      row('Oda · kopya', k.oda.n + '/' + k.oda.kapasite, 'havuzun ' + pct(k.oda.n / tot * 100, false) + ' · ' + hm(k.oda.zaman), k.oda.n / tot * 100, '#6a86d8', '');
    $('#huniMeta').innerHTML = 'ofiste ' + k.havuz.masa + '/' + k.aday.masa + '/' + k.oda.masa + ' masa görünür · ' + ORN;
  }
  function kohort() {
    const k = st.kk, pr = Math.max(0, Math.min(1, k.hafta / k.hafta_toplam));
    $('#kohIcerik').innerHTML = '<div class="hafta"><span>hafta <b>' + k.hafta + '/' + k.hafta_toplam + '</b></span><div class="hb"><i style="width:' + (pr * 100).toFixed(0) + '%;background:#46d3c2"></i></div></div>' +
      '<ul class="kollar">' + k.kollar.map(c => '<li><span>' + esc(c.ad) + '</span><b>N=' + c.n + '</b></li>').join('') + '</ul>' +
      (k.performans_kilitli ? '<div class="kilit" role="note"><svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M4 7V5a4 4 0 0 1 8 0v2h1v8H3V7zm2 0h4V5a2 2 0 0 0-4 0z" fill="currentColor"/></svg><div><b>Performans kilitli</b><div class="ks">' + esc(k.onkayit) + '. Kâr görüldükçe trader, eşik ya da süre değiştirilmez.</div></div></div>' : '<p class="bos">Performans: bilinmiyor.</p>');
    $('#kohMeta').innerHTML = 'veri ' + hm(k.zaman) + ' · ' + ORN;
  }
  function veri() {
    $('#veriIcerik').innerHTML = st.vk.map(r => {
      const d = r.durum === 'tamam' ? 'ok' : r.durum === 'bilinmiyor' ? 'bl' : 'wr';
      return '<div class="vr"><i class="nk ' + d + '" aria-hidden="true"></i><div class="vk"><b>' + esc(r.ad) + '</b><div class="ks">' + (r.deger == null ? UNK : esc(r.deger)) + ' · ' + (r.zaman ? hm(r.zaman) : 'zaman bilinmiyor') + '</div></div><span class="rz ' + d + '">' + (r.durum === 'tamam' ? 'tamam' : r.durum === 'bayat' ? 'bayat' : r.durum === 'bilinmiyor' ? 'bilinmiyor' : 'uyarı') + '</span></div>';
    }).join('');
    $('#veriMeta').innerHTML = 'n=' + st.vk.length + ' kontrol · ' + ORN;
  }
  function risk() {
    $('#riskIcerik').innerHTML = st.risk.tavanlar.map(t => {
      const r = t.kullanim / t.tavan, c = r >= 0.999 ? 'dn' : r >= 0.75 ? 'wr' : 'ok', f = x => t.birim === 'kasa payı' ? pct(x * 100, false, 0) : '%' + Math.round(x * 100);
      return '<div class="rr"><div class="rh"><b>' + esc(t.ad) + '</b><span class="' + c + '">' + (r >= 0.999 ? 'TAVAN DOLU' : '%' + Math.round(r * 100)) + '</span></div><div class="hb"><i class="' + c + '" style="width:' + Math.min(100, r * 100).toFixed(0) + '%"></i></div><div class="ks">' + esc(t.birim) + ': ' + f(t.kullanim) + ' / ' + f(t.tavan) + '</div></div>';
    }).join('');
    $('#riskMeta').innerHTML = 'veri ' + hm(st.risk.zaman) + ' · eşikler yalnız kurallar.yaml\'da · ' + ORN;
  }
  function tg() {
    $('#tgIcerik').innerHTML = '<div class="tgs"><b>' + (st.tg.bugun_n == null ? UNK : st.tg.bugun_n) + '</b><span>bildirim bugün</span></div><ul class="tgl">' + st.tg.son.slice(0, 3).map(s => '<li>' + esc(s) + '</li>').join('') + '</ul>';
    $('#tgMeta').innerHTML = 'son ' + hm(st.tg.zaman) + ' · ' + ORN;
  }
  function gozcu() {
    $('#gozcuListe').innerHTML = st.log.slice(0, 7).map(l => '<li><button data-oda="' + esc(l.oda) + '"><time>' + l.ts + '</time><i class="oc" data-o="' + esc(l.oda) + '">' + esc(ODA_AD(l.oda)) + '</i><span>' + esc(l.metin) + '</span></button></li>').join('') || '<li class="bos">Henüz olay yok (örnek akış başlıyor).</li>';
  }
  function aciklama() {
    const k = st.katlar, ac = Object.keys(st.stale).filter(x => st.stale[x]).map(ODA_AD);
    $('#ofisAciklama').textContent = 'Örnek veriyle çalışan izometrik ofis: 14 oda; Lab, Aday, Oda ve Kontrol masalarında trader figürleri oturur. Havuz ' + k.havuz.n + ', aday ' + k.aday.n + ', oda ' + k.oda.n + '/' + k.oda.kapasite + '. Açık gölge işlemi ' + st.acik.length + '. Risk alarmı ' + (st.alarm ? 'açık' : 'yok') + '. Bayat oda: ' + (ac.length ? ac.join(', ') : 'yok') + '.';
  }
  function top() {
    const ornek = String(O.data.kaynak || '').indexOf('ornek') === 0;
    $('#ornekFlt').hidden = !ornek;
    const c = O.data.cipler || {}, low = v => String(v).toLocaleLowerCase('tr');
    $('#kayitDeger').textContent = c.golge ? low(c.golge) : 'bilinmiyor';
    $('#hatDeger').textContent = c.telegram ? low(c.telegram) : 'bilinmiyor';
    $('#plHat .lamba').className = 'lamba ' + (low(c.telegram || '') === 'açık' ? 'ok' : 'wr');
  }
  function render() {
    raf = 0; st = Off.state(); if (!st) return;
    kasa(); ozet(); acik(); kapanan(); huni(); kohort(); veri(); risk(); tg(); gozcu(); aciklama(); top();
  }
  function schedule() { if (!raf) raf = requestAnimationFrame(render); }
  P.init = function (off, a) {
    Off = off; api = a;
    Off.on(schedule); O.Names.onChange(schedule);
    document.addEventListener('click', e => {
      const b = e.target.closest('[data-oda]'); if (b && b.closest('#gozcuListe') && b.dataset.oda) api.focusRoom(b.dataset.oda);
      const s = e.target.closest('.sb'); if (s) { const act = Off.state().actorById[s.dataset.trader]; const k = act && act.kat; if (k) api.focusRoom(k); }
    });
    // süre hücreleri canlı akar (hareket azaltılmışsa dakikada bir)
    setInterval(() => {
      if (!st) return;
      const sl = Off.state(); sl.acik.forEach(x => { const c = document.querySelector('[data-sure="' + x.id + '"]'); if (c) c.textContent = dur(liveSec(x)); });
      const sc = $('#saat'); if (sc) { const d = Off.clock(); sc.textContent = pad(d.getHours()) + ':' + pad(d.getMinutes()); }
    }, Off.reduced ? 15000 : 1000);
    render();
    const sc = $('#saat'); if (sc) { const d = Off.clock(); sc.textContent = pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  };
})();
