import assert from "node:assert/strict";
import test from "node:test";
import worker, { anahtarEslesir, bildirimKipi, checkStateAlerts, dailySummaryText, runCron, saglikHata, sendDailySummaryIfDue } from "../src/index.js";

function d1Mock(durumlar = {}) {
  const writes = [];
  return {
    writes,
    DB: {
      prepare(sql) {
        return {
          bind(...args) {
            return {
              first: async () => {
                if (/FROM imlec/.test(sql)) return { son_dolum: 0 };
                if (/FROM uyari_durum/.test(sql)) return args[0] in durumlar ? { deger: durumlar[args[0]] } : undefined;
                if (/FROM ozet_gonderildi/.test(sql)) return durumlar.gonderilenGunler?.has(args[0]) ? { gun: args[0] } : undefined;
                return undefined;
              },
              run: async () => { writes.push([sql, args]); if (/INSERT INTO uyari_durum/.test(sql)) durumlar[args[0]] = args[1]; if (/INSERT OR IGNORE INTO ozet_gonderildi/.test(sql)) durumlar.gonderilenGunler?.add(args[0]); return { meta: { changes: 1 } }; },
            };
          },
        };
      },
    },
  };
}

test("bildirimKipi: varsayılan 'ozet'; yalnız tam olarak 'islem' ise açık", () => {
  assert.equal(bildirimKipi({}), "ozet");
  assert.equal(bildirimKipi({ BILDIRIM_KIPI: "ozet" }), "ozet");
  assert.equal(bildirimKipi({ BILDIRIM_KIPI: "baska" }), "ozet");
  assert.equal(bildirimKipi({ BILDIRIM_KIPI: "islem" }), "islem");
});

test("varsayılan kipte (ozet) açılış/kapanış Telegram'a gitmez, ama kırmızı ışık uyarısı yine gider", async () => {
  const mock = d1Mock();
  const fill = { coin: "BTC", side: "B", sz: "1", px: "100", time: 5, oid: 7, tid: 1, startPosition: "0" };
  const sent = [];
  const fetcher = async (url, init) => {
    if (String(url).includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [{ id: "T1", kol: "oda", adres: "0x1", takma_ad: "Test", hesap_degeri: 1000, pozisyonlar: [], saglik: { isik: "kirmizi" } }] }));
    if (String(url).includes("api.hyperliquid.xyz")) return new Response(JSON.stringify([fill]));
    sent.push(JSON.parse(init.body).text); return new Response(JSON.stringify({ ok: true }));
  };
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock.DB };   // BILDIRIM_KIPI yok → varsayılan "ozet"
  await runCron(env, fetcher);   // ilk koşu: kırmızı ışık ilk kez görülüyor — taban, bildirim yok
  assert.equal(sent.length, 0);
  await runCron(env, fetcher);   // ikinci koşu: hâlâ kırmızı, yeni geçiş yok
  assert.equal(sent.filter(t => /açtı/.test(t)).length, 0, "açılış bildirimi kipi kapalıyken hiç gitmemeli");
});

test("dailySummaryText: yalnız motorun hazır kol_ozet alanını gösterir, hesap yapmaz (altın örnek)", () => {
  const now = Date.parse("2026-10-30T06:00:00Z");
  // Rakamlar kasten traderlar listesiyle UYUMSUZ: Worker traderlardan hesap yapsaydı farklı çıkardı. Ekran yalnız kol_ozet'i okur.
  const status = {
    uretildi: "2026-10-30T05:50:00Z",   // 10 dk önce
    traderlar: [{ id: "X", kol: "oda", kollar: ["oda"], gecerli: true, saglik: { isik: "kirmizi" }, sanal_kopya: { bakiye_usd: 1, getiri: 9 } }],
    kol_ozet: {
      kollar: { oda: { uye: 3, gecerli: 2, kapsama: 2 / 3, kasa_usd: 2000, getiri: 0, eksik_degerleme: 1,
                       isik: { yesil: 1, sari: 1, kirmizi: 1 }, sayac_24s: { acilis: 7, kapanis: 5, trader_sayisi: 4, kapanan: 5, kazanan: 2 } } },
      oda_kontrol_fark: 0,
    },
  };
  const text = dailySummaryText(status, now);
  assert.match(text, /Oda kasası \(sanal\): \$2\.000 \(\+0,0%\)/);
  assert.match(text, /Oda − Kontrol farkı.*\+0,0%/);
  assert.match(text, /Son 24 saat: 12 işlem \(7 açılış, 5 kapanış\) · 4 trader · kazanma 2\/5/);
  assert.match(text, /🟢 1 {3}🟡 1 {3}🔴 1/);
  assert.match(text, /Oda kapsama: 2\/3 geçerli \(%67\) · 1 geçersiz\/eski toplama girmez/);
  assert.match(text, /1 trader'ın açık lotu eksik değerlenmiş/);
  assert.match(text, /Veri 10 dk önce/);
});

test("dailySummaryText: kol_ozet yoksa uydurmaz, uyarır; 24 saat sayacı yoksa 'bilinmiyor'", () => {
  const now = Date.parse("2026-10-30T06:00:00Z");
  const eski = dailySummaryText({ uretildi: "2026-10-30T05:50:00Z", traderlar: [{ id: "O1", kol: "oda" }] }, now);
  assert.match(eski, /kol_ozet\) bu veride yok/);
  assert.doesNotMatch(eski, /Oda kasası/);
  const sayacsiz = dailySummaryText({ uretildi: "2026-10-30T05:50:00Z", kol_ozet: { kollar: { oda: { uye: 1, gecerli: 1, kapsama: 1, kasa_usd: 1000, getiri: null,
    eksik_degerleme: 0, isik: { yesil: 1, sari: 0, kirmizi: 0 }, sayac_24s: null } }, oda_kontrol_fark: null } }, now);
  assert.match(sayacsiz, /Son 24 saat: bilinmiyor/);
  assert.match(sayacsiz, /\(bilinmiyor\)/);
});

test("checkStateAlerts: veri 3 saatten eskiyse uyarı gider, aynı durumda tekrarlanmaz", async () => {
  const mock = d1Mock();
  const sent = [];
  const fetcher = async (url, init) => { sent.push(JSON.parse(init.body).text); return new Response(JSON.stringify({ ok: true })); };
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock.DB };
  const eskiStatus = { uretildi: new Date(Date.now() - 200 * 60000).toISOString() };   // 200 dk > 180 dk eşik
  await checkStateAlerts(env, eskiStatus, fetcher);
  assert.equal(sent.length, 1);
  assert.match(sent[0], /3 saatten eski/);
  await checkStateAlerts(env, eskiStatus, fetcher);   // hâlâ eski, aynı uyarı tekrarlanmaz
  assert.equal(sent.length, 1);
  const tazeStatus = { uretildi: new Date().toISOString() };
  await checkStateAlerts(env, tazeStatus, fetcher);   // tazeye döndü, uyarı yok (yalnız kötüye gidişte uyarır)
  assert.equal(sent.length, 1);
  await checkStateAlerts(env, eskiStatus, fetcher);   // tekrar eskidi → tekrar uyarır
  assert.equal(sent.length, 2);
});

test("checkStateAlerts: kalabalık uyarısı başlayınca gider, aynı durumda tekrarlanmaz", async () => {
  const mock = d1Mock();
  const sent = [];
  const fetcher = async (url, init) => { sent.push(JSON.parse(init.body).text); return new Response(JSON.stringify({ ok: true })); };
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock.DB };
  const sakin = { uretildi: new Date().toISOString(), kalabalik: { uyari: false } };
  const kalabalik = { uretildi: new Date().toISOString(), kalabalik: { uyari: true, uyari_metni: "ETH net long %60" } };
  await checkStateAlerts(env, sakin, fetcher);
  assert.equal(sent.length, 0);
  await checkStateAlerts(env, kalabalik, fetcher);
  assert.equal(sent.length, 1);
  assert.match(sent[0], /Kalabalık uyarısı başladı: ETH net long %60/);
  await checkStateAlerts(env, kalabalik, fetcher);   // hâlâ kalabalık, tekrar uyarmaz
  assert.equal(sent.length, 1);
  await checkStateAlerts(env, sakin, fetcher);
  await checkStateAlerts(env, kalabalik, fetcher);   // yeniden başladı → yeniden uyarır
  assert.equal(sent.length, 2);
});

test("sendDailySummaryIfDue: yalnız 06:00 UTC'de (09:00 TR) ve günde bir kez gönderir", async () => {
  const mock = d1Mock({ gonderilenGunler: new Set() });
  const sent = [];
  const fetcher = async (url, init) => {
    if (String(url).includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [] }));
    sent.push(1); return new Response(JSON.stringify({ ok: true }));
  };
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock.DB };
  await sendDailySummaryIfDue(env, fetcher, Date.parse("2026-10-30T05:59:00Z"));
  assert.equal(sent.length, 0, "06:00 değilken gönderilmemeli");
  await sendDailySummaryIfDue(env, fetcher, Date.parse("2026-10-30T06:00:00Z"));
  assert.equal(sent.length, 1);
  await sendDailySummaryIfDue(env, fetcher, Date.parse("2026-10-30T06:00:30Z"));   // aynı dakika yine çağrılsa bile
  assert.equal(sent.length, 1, "aynı gün ikinci kez gönderilmemeli");
  await sendDailySummaryIfDue(env, fetcher, Date.parse("2026-10-31T06:00:00Z"));
  assert.equal(sent.length, 2, "ertesi gün yeniden gönderilmeli");
});

test("sendDailySummaryIfDue: 06:00'da kaçarsa sonraki dakikalarda telafi eder ('gecikmeli'), 06:00 öncesi göndermez, günde bir kez", async () => {
  const mock = d1Mock({ gonderilenGunler: new Set() });
  const sent = [];
  const fetcher = async (url, init) => {
    if (String(url).includes("durum.json")) return new Response(JSON.stringify({ uretildi: "2026-10-30T08:00:00Z", traderlar: [] }));
    sent.push(JSON.parse(init.body).text); return new Response(JSON.stringify({ ok: true }));
  };
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock.DB };
  await sendDailySummaryIfDue(env, fetcher, Date.parse("2026-10-30T05:59:00Z"));
  assert.equal(sent.length, 0);
  await sendDailySummaryIfDue(env, fetcher, Date.parse("2026-10-30T06:03:00Z"));      // 06:03: hâlâ zamanında (< 06:05), etiket yok
  assert.equal(sent.length, 1);
  assert.doesNotMatch(sent[0], /gecikmeli/);
  const mock2 = d1Mock({ gonderilenGunler: new Set() });
  const env2 = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock2.DB };
  await sendDailySummaryIfDue(env2, fetcher, Date.parse("2026-10-30T09:30:00Z"));      // kaçmıştı: 09:30'da telafi
  assert.equal(sent.length, 2);
  assert.match(sent[1], /Günlük özet \(gecikmeli\)/);
  await sendDailySummaryIfDue(env2, fetcher, Date.parse("2026-10-30T09:31:00Z"));
  assert.equal(sent.length, 2, "telafiden sonra aynı gün tekrar gitmez");
});

test("saglikHata: ardışık hata D1'e yazılır, 3. hatada tek Telegram alarmı gider", async () => {
  const kayit = {};
  const sent = [];
  const DB = { prepare(sql) { return { bind(...a) { return {
    first: async () => (/FROM saglik_kayit/.test(sql) && kayit[a[0]] ? { ardisik: kayit[a[0]] } : undefined),
    run: async () => { if (/INSERT INTO saglik_kayit/.test(sql)) kayit[a[0]] = a[1]; return {}; },
  }; } }; } };
  const fetcher = async (url, init) => { sent.push(JSON.parse(init.body).text); return new Response(JSON.stringify({ ok: true })); };
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB };
  await saglikHata(env, "durum_okuma", new Error("HTTP 500"), fetcher);
  await saglikHata(env, "durum_okuma", new Error("HTTP 500"), fetcher);
  assert.equal(sent.length, 0);
  await saglikHata(env, "durum_okuma", new Error("HTTP 500"), fetcher);
  assert.equal(kayit.durum_okuma, 3);
  assert.equal(sent.length, 1);
  assert.match(sent[0], /durum_okuma 3 dakikadır başarısız \(HTTP 500\)/);
  await saglikHata(env, "durum_okuma", new Error("HTTP 500"), fetcher);
  assert.equal(sent.length, 1, "alarm yalnız 3. hatada bir kez");
});

test("GET /kararlar: KARAR_ANAHTARI tanımlıysa anahtarsız 401, doğru anahtarla 200; tanımsızsa eski açık davranış", async () => {
  const DB = { prepare() { return { all: async () => ({ results: [{ olay_id: "a" }] }) }; } };
  const gor = (env, headers = {}) => worker.fetch(new Request("https://w.test/kararlar", { headers }), { DB, ...env });
  assert.equal((await gor({ KARAR_ANAHTARI: "gizli" })).status, 401);
  assert.equal((await gor({ KARAR_ANAHTARI: "gizli" }, { authorization: "Bearer yanlis" })).status, 401);
  assert.equal((await gor({ KARAR_ANAHTARI: "gizli" }, { authorization: "Bearer gizli" })).status, 200);
  assert.equal((await gor({})).status, 200);
  assert.equal(anahtarEslesir("Bearer a", "Bearer ab"), false);
});

test("sendDailySummaryIfDue: durum.json okunamazsa sessizce atlar", async () => {
  const mock = d1Mock({ gonderilenGunler: new Set() });
  let sent = false;
  const fetcher = async url => { if (String(url).includes("durum.json")) return new Response("", { status: 500 }); sent = true; return new Response(JSON.stringify({ ok: true })); };
  await sendDailySummaryIfDue({ TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: mock.DB }, fetcher, Date.parse("2026-10-30T06:00:00Z"));
  assert.equal(sent, false);
});
