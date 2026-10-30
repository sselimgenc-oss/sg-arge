import assert from "node:assert/strict";
import test from "node:test";
import { gecikmeDk, runCron } from "../src/index.js";

test("gecikmeDk: dolum zamanından şu ana kadar geçen dakika (altın örnek)", () => {
  const now = Date.parse("2026-01-01T10:05:00Z");
  assert.equal(gecikmeDk(Date.parse("2026-01-01T10:00:00Z"), now), 5);
  assert.equal(gecikmeDk(Date.parse("2026-01-01T09:00:00Z"), now), 65);
});

function d1Mock() {
  const imlec = new Map(), gecikme = new Map(), writes = [];
  return {
    gecikme, writes,
    DB: {
      prepare(sql) {
        return {
          bind(...args) {
            return {
              first: async () => {
                if (/FROM imlec/.test(sql)) return imlec.has(args[0]) ? { son_dolum: imlec.get(args[0]) } : undefined;
                if (/FROM isik/.test(sql)) return undefined;
                return undefined;
              },
              run: async () => {
                writes.push([sql, args]);
                if (/INSERT INTO imlec/.test(sql)) imlec.set(args[0], args[1]);
                if (/UPDATE imlec/.test(sql)) imlec.set(args[1], args[0]);
                if (/INTO son_gecikme/.test(sql)) gecikme.set(args[0], { gecikme_dk: args[1], zaman: args[2] });
                return { meta: { changes: 1 } };
              },
            };
          },
        };
      },
    },
  };
}

test("runCron: yeni dolum görünce gerçek gecikme D1'e yazılır (altın örnek)", async () => {
  const mock = d1Mock();
  mock.gecikme; // no-op reference to silence unused warnings in some linters
  const fillTime = Date.now() - 3 * 60000;   // 3 dk önce gerçekleşmiş dolum
  const fill = { coin: "BTC", side: "B", sz: "1", px: "100", time: fillTime, oid: 7, tid: 1, startPosition: "0" };
  const env = { DB: mock.DB };
  const fetcher = async (url) => {
    if (String(url).includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [{ id: "T1", kol: "oda", adres: "0x1", takma_ad: "Test", hesap_degeri: 1000, pozisyonlar: [] }] }));
    if (String(url).includes("api.hyperliquid.xyz")) return new Response(JSON.stringify([fill]));
    return new Response(JSON.stringify({ ok: true }));
  };
  // İlk koşu: imleci şimdiye koyar, henüz dolum görmez (taban).
  await runCron(env, fetcher);
  assert.equal(mock.gecikme.size, 0);
  // İmleci dolumdan önceye elle geri al ki ikinci koşuda "yeni dolum" sayılsın.
  mock.gecikme.clear();
  const writes2 = [];
  const env2 = { DB: { prepare(sql) { return { bind(...args) { return {
    first: async () => /FROM imlec/.test(sql) ? { son_dolum: fillTime - 1000 } : undefined,
    run: async () => { writes2.push([sql, args]); return { meta: { changes: 1 } }; },
  }; } }; } } };
  await runCron(env2, fetcher);
  const gecikmeYazisi = writes2.find(([sql]) => /INTO son_gecikme/.test(sql));
  assert.ok(gecikmeYazisi, "son_gecikme yazısı bekleniyordu");
  const [, args] = gecikmeYazisi;
  assert.equal(args[0], "T1");
  assert.ok(Math.abs(args[1] - 3) < 0.1, `gecikme ~3 dk olmalı, geldi: ${args[1]}`);
});

test("runCron: yeni dolum yoksa son_gecikme'ye yazılmaz", async () => {
  const writes = [];
  const env = { DB: { prepare(sql) { return { bind(...args) { return {
    first: async () => /FROM imlec/.test(sql) ? { son_dolum: Date.now() } : undefined,
    run: async () => { writes.push([sql, args]); return { meta: { changes: 1 } }; },
  }; } }; } } };
  const fetcher = async (url) => {
    if (String(url).includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [{ id: "T1", kol: "oda", adres: "0x1", takma_ad: "Test", hesap_degeri: 1000, pozisyonlar: [] }] }));
    if (String(url).includes("api.hyperliquid.xyz")) return new Response(JSON.stringify([]));
    return new Response(JSON.stringify({ ok: true }));
  };
  await runCron(env, fetcher);
  assert.equal(writes.filter(([sql]) => /INTO son_gecikme/.test(sql)).length, 0);
});

test("GET /gecikme: son_gecikme tablosunu trader'a göre sıralı döner", async () => {
  const worker = (await import("../src/index.js")).default;
  const rows = [{ trader: "T2", gecikme_dk: 4.2, zaman: "2026-01-01T00:00:00Z" }, { trader: "T1", gecikme_dk: 1.1, zaman: "2026-01-01T00:00:00Z" }];
  const env = { DB: { prepare(sql) { return { bind() { return { all: async () => ({ results: rows }) }; }, all: async () => ({ results: rows }) }; } } };
  const response = await worker.fetch(new Request("https://worker/gecikme"), env);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), rows);
});
