import assert from "node:assert/strict";
import test from "node:test";
import { tetiklemeKarari } from "../src/tetikleyici.js";
import { dispatchWorkflow, handleTelegram, tetiklemeKontrol, workflowRuns } from "../src/index.js";

const NOW = Date.parse("2026-10-29T18:00:00Z");

test("çalışan ya da sırada bekleyen koşu varsa asla tetiklenmez", () => {
  assert.deepEqual(tetiklemeKarari([{ status: "in_progress" }], 60, NOW), { tetikle: false, neden: "calisan_var" });
  assert.deepEqual(tetiklemeKarari([{ status: "queued" }], 60, NOW), { tetikle: false, neden: "calisan_var" });
  assert.deepEqual(tetiklemeKarari([{ status: "waiting" }], 60, NOW), { tetikle: false, neden: "calisan_var" });
});

test("hiç koşu yoksa tetiklenir; kırmızı biten koşu da sayılır (arşiv boşluk eşiğinde bilerek kırmızı biter → dakikada bir yeniden tetikleme yok)", () => {
  assert.deepEqual(tetiklemeKarari([], 60, NOW), { tetikle: true, neden: "kosu_yok" });
  assert.deepEqual(tetiklemeKarari([{ status: "completed", conclusion: "failure", run_started_at: "2026-10-29T17:30:00Z" }], 60, NOW),
    { tetikle: false, neden: "taze", yasDk: 30 });
  assert.deepEqual(tetiklemeKarari([{ status: "completed", conclusion: "failure", run_started_at: "2026-10-29T16:30:00Z" }], 60, NOW),
    { tetikle: true, neden: "eski", yasDk: 90 });
});

test("son başarılı koşu eşikten eskiyse tetiklenir (altın örnek: 75 dk eşik, 80 dk önce)", () => {
  const runs = [{ status: "completed", conclusion: "success", run_started_at: "2026-10-29T16:40:00Z" }];   // NOW - 80 dk
  assert.deepEqual(tetiklemeKarari(runs, 75, NOW), { tetikle: true, neden: "eski", yasDk: 80 });
});

test("son başarılı koşu eşikten tazeyse tetiklenmez (altın örnek: 75 dk eşik, 23 dk önce)", () => {
  const runs = [{ status: "completed", conclusion: "success", run_started_at: "2026-10-29T17:37:00Z" }];   // NOW - 23 dk
  assert.deepEqual(tetiklemeKarari(runs, 75, NOW), { tetikle: false, neden: "taze", yasDk: 23 });
});

test("en yeni başarılı koşu esas alınır (liste karışık sırada olsa bile ilk eşleşen kullanılır)", () => {
  const runs = [
    { status: "completed", conclusion: "success", run_started_at: "2026-10-29T17:00:00Z" },   // 60 dk önce → sınırda
    { status: "completed", conclusion: "failure", run_started_at: "2026-10-29T17:50:00Z" },
  ];
  assert.deepEqual(tetiklemeKarari(runs, 75, NOW), { tetikle: false, neden: "taze", yasDk: 60 });
});

test("GITHUB_ACTIONS_TOKEN yoksa tetikleme kontrolü hiçbir ağ çağrısı yapmaz (sessizce atlar)", async () => {
  let called = false;
  await tetiklemeKontrol({}, async () => { called = true; return new Response("{}"); });
  assert.equal(called, false);
});

test("token varsa eski koşular için dispatch tetiklenir, taze olanlar için tetiklenmez", async () => {
  // izleme.yml eşiği 75 dk: 120 dk önceki koşu eski. arsiv.yml eşiği 20 dk: 10 dk önceki koşu taze.
  const dispatched = [];
  const fetcher = async (url, init) => {
    if (url.includes("/runs")) {
      const dkOnce = url.includes("izleme.yml") ? 120 : 10;
      const runStarted = new Date(Date.now() - dkOnce * 60000).toISOString();
      return new Response(JSON.stringify({ workflow_runs: [{ status: "completed", conclusion: "success", run_started_at: runStarted }] }));
    }
    if (url.includes("/dispatches")) { dispatched.push({ url, body: JSON.parse(init.body) }); return new Response(null, { status: 204 }); }
    throw new Error("beklenmeyen istek: " + url);
  };
  await tetiklemeKontrol({ GITHUB_ACTIONS_TOKEN: "t" }, fetcher);
  assert.equal(dispatched.length, 1);
  assert.match(dispatched[0].url, /izleme\.yml\/dispatches$/);
  assert.deepEqual(dispatched[0].body, { ref: "main" });
});

test("bir iş akışının GitHub çağrısı başarısız olursa diğeri yine de kontrol edilir", async () => {
  const dispatched = [];
  const fetcher = async (url) => {
    if (url.includes("izleme.yml/runs")) return new Response(null, { status: 500 });
    if (url.includes("arsiv.yml/runs")) return new Response(JSON.stringify({ workflow_runs: [] }));
    if (url.includes("/dispatches")) { dispatched.push(url); return new Response(null, { status: 204 }); }
    throw new Error("beklenmeyen istek: " + url);
  };
  await tetiklemeKontrol({ GITHUB_ACTIONS_TOKEN: "t" }, fetcher);
  assert.equal(dispatched.length, 1);
  assert.match(dispatched[0], /arsiv\.yml/);
});

test("workflowRuns başarısız HTTP yanıtında hata fırlatır", async () => {
  await assert.rejects(() => workflowRuns({ GITHUB_ACTIONS_TOKEN: "t" }, "izleme.yml", async () => new Response(null, { status: 403 })));
});

const durumIstegi = () => new Request("https://worker/telegram", {
  method: "POST", headers: { "content-type": "application/json", "X-Telegram-Bot-Api-Secret-Token": "secret" },
  body: JSON.stringify({ message: { chat: { id: "1" }, text: "/durum" } }),
});

test("/durum: GITHUB_ACTIONS_TOKEN yoksa 'otomatik tetikleme kapalı' notu eklenir", async () => {
  const env = { TELEGRAM_CHAT_ID: "1", TELEGRAM_BOT_TOKEN: "x", TELEGRAM_WEBHOOK_SECRET: "secret" };
  let sent;
  const fetcher = async (url, init) => {
    if (url.includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [] }));
    if (url.includes("api.telegram.org")) { sent = JSON.parse(init.body); return new Response(JSON.stringify({ ok: true })); }
    throw new Error("beklenmeyen istek: " + url);
  };
  await handleTelegram(durumIstegi(), env, fetcher);
  assert.match(sent.text, /Otomatik tetikleme: kapalı/);
});

test("/durum: GITHUB_ACTIONS_TOKEN varsa 'otomatik tetikleme kapalı' notu eklenmez", async () => {
  const env = { TELEGRAM_CHAT_ID: "1", TELEGRAM_BOT_TOKEN: "x", TELEGRAM_WEBHOOK_SECRET: "secret", GITHUB_ACTIONS_TOKEN: "t" };
  let sent;
  const fetcher = async (url, init) => {
    if (url.includes("durum.json")) return new Response(JSON.stringify({ uretildi: new Date().toISOString(), traderlar: [] }));
    if (url.includes("api.telegram.org")) { sent = JSON.parse(init.body); return new Response(JSON.stringify({ ok: true })); }
    throw new Error("beklenmeyen istek: " + url);
  };
  await handleTelegram(durumIstegi(), env, fetcher);
  assert.doesNotMatch(sent.text, /Otomatik tetikleme/);
});

test("dispatchWorkflow doğru uç noktaya ve gövdeye POST atar", async () => {
  let seen;
  await dispatchWorkflow({ GITHUB_ACTIONS_TOKEN: "t" }, "arsiv.yml", async (url, init) => { seen = { url, init }; return new Response(null, { status: 204 }); });
  assert.equal(seen.url, "https://api.github.com/repos/sselimgenc-oss/sg-arge/actions/workflows/arsiv.yml/dispatches");
  assert.equal(seen.init.method, "POST");
  assert.deepEqual(JSON.parse(seen.init.body), { ref: "main" });
  assert.equal(seen.init.headers.authorization, "Bearer t");
});
