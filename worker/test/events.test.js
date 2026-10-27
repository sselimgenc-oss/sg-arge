import assert from "node:assert/strict";
import test from "node:test";
import fixture from "../../tests/fixtures/olaylar.json" with { type: "json" };
import { callbackData, decision, formatEvent, handleTelegram, runCron, sendOnce } from "../src/index.js";
import { orderEvents } from "../src/events.js";

test("ortak oid fixture Python ile aynı olayları üretir", () => {
  const actual = orderEvents(fixture.trader, fixture.fills, fixture.account)
    .map(({ id, tur, coin, yon }) => ({ id, tur, coin, yon }));
  assert.deepEqual(actual, fixture.expected);
});

test("callback en çok 64 bayt ve yalnız geçerli kararlar", () => {
  const data = callbackData({ id: "T1-123-acilis" }, "s", "g");
  assert.ok(new TextEncoder().encode(data).byteLength <= 64);
  assert.deepEqual(decision(data), { olay_id: "T1-123-acilis", karar: "atladi", neden: "gec_gordum" });
  assert.equal(decision("bad"), null);
});

test("geçersiz webhook gizli başlığı D1 veya Telegram'a dokunmaz", async () => {
  const response = await handleTelegram(new Request("https://worker/telegram", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" }),
    { TELEGRAM_WEBHOOK_SECRET: "beklenen" }, () => { throw new Error("çağrılmamalı"); });
  assert.equal(response.status, 403);
});

test("ilk cron imleci şimdiye koyar, geçmiş bildirimi göndermez", async () => {
  const writes = [];
  const env = { DB: { prepare(sql) { return { bind(...args) { return {
    first: async () => undefined,
    run: async () => { writes.push([sql, args]); return { meta: { changes: 1 } }; },
  }; } }; } } };
  const fetcher = async () => new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [{ id: "T1", adres: "0x1", takma_ad: "Test", hesap_degeri: 1000, pozisyonlar: [], saglik: { isik: "yesil" } }] }));
  await runCron(env, fetcher);
  assert.equal(writes.length, 1);
  assert.match(writes[0][0], /INSERT INTO imlec/);
});

test("bildirilmiş olay yeniden Telegram'a gitmez", async () => {
  const env = { DB: { prepare() { return { bind() { return { run: async () => ({ meta: { changes: 0 } }) }; } }; } } };
  let calls = 0;
  assert.equal(await sendOnce(env, { id: "T1-1-acilis", tur: "acilis", coin: "BTC", yon: "long", fiyat: 1, hesap_payi: 0 }, { takma_ad: "Test" }, async () => { calls += 1; }), false);
  assert.equal(calls, 0);
});

test("mesaja tarz etiketi: [Intraday] / [Swing]; tarz yoksa etiket yok", () => {
  const event = { id: "T1-1-acilis", tur: "acilis", coin: "BTC", yon: "long", fiyat: 68400, hesap_payi: 0.08 };
  assert.match(formatEvent(event, { takma_ad: "Trader-1", tarz: "intraday" }), /^🟢 Trader-1 \[Intraday\] · BTC LONG açtı/);
  assert.match(formatEvent(event, { takma_ad: "Trader-2", tarz: "swing" }), /^🟢 Trader-2 \[Swing\] · BTC LONG açtı/);
  assert.doesNotMatch(formatEvent(event, { takma_ad: "Trader-3" }), /\[/);
  assert.doesNotMatch(formatEvent(event, { takma_ad: "Trader-4", tarz: "bilinmiyor" }), /\[/);
  assert.equal(formatEvent({ tur: "isik" }, { takma_ad: "Trader-1", tarz: "swing" }), "🔴 Trader-1 [Swing] · sağlık ışığı kırmızı");
});

test("tarz durum.json'dan okunur: cron mesajı etiketli gider", async () => {
  const sent = [];
  const env = { TELEGRAM_BOT_TOKEN: "x", TELEGRAM_CHAT_ID: "1", DB: { prepare(sql) { return { bind(...args) { return {
    first: async () => (/FROM imlec/.test(sql) ? { son_dolum: 0 } : undefined),
    run: async () => ({ meta: { changes: 1 } }),
  }; } }; } } };
  const fill = { coin: "BTC", side: "B", sz: "1", px: "100", time: 5, oid: 7, tid: 1, startPosition: "0" };
  const fetcher = async (url, init) => {
    if (String(url).includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [{ id: "T1", adres: "0x1", takma_ad: "Test", tarz: "swing", hesap_degeri: 1000, pozisyonlar: [], saglik: { isik: "yesil" } }] }));
    if (String(url).includes("api.hyperliquid.xyz")) return new Response(JSON.stringify([fill]));
    sent.push(JSON.parse(init.body).text);
    return new Response(JSON.stringify({ ok: true }));
  };
  await runCron(env, fetcher);
  assert.equal(sent.length, 1);
  assert.match(sent[0], /Test \[Swing\] · BTC LONG açtı/);
});
