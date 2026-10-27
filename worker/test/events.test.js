import assert from "node:assert/strict";
import test from "node:test";
import fixture from "../../tests/fixtures/olaylar.json" with { type: "json" };
import { callbackData, decision, handleTelegram, runCron, sendOnce } from "../src/index.js";
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
