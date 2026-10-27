import { eventId, isPerp, orderEvents } from "./events.js";

const INFO = "https://api.hyperliquid.xyz/info";
const STATUS = "https://raw.githubusercontent.com/sselimgenc-oss/sg-arge/copytrade-izleme/izleme/durum.json";
const CALLBACK = /^k\|([^|]+)\|([as])(?:\|([gbd]))?$/;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8" } });
}

function nowIso() { return new Date().toISOString(); }

async function retryFetch(url, init, fetcher = fetch) {
  let response = await fetcher(url, init);
  if (response.status === 429) {
    await new Promise(resolve => setTimeout(resolve, 1200));
    response = await fetcher(url, init);
  }
  return response;
}

async function telegram(env, method, body, fetcher = fetch) {
  const response = await fetcher(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`Telegram ${method} başarısız`);
  return response.json();
}

function number(value, digits = 2) {
  return new Intl.NumberFormat("tr-TR", { maximumFractionDigits: digits }).format(value);
}

// durum.json'daki traderlar[].tarz (v1.3): yalnız intraday ve swing etiketlenir
const STYLE_LABEL = { intraday: "[Intraday]", swing: "[Swing]" };

function nameWithStyle(trader) {
  const label = STYLE_LABEL[trader.tarz];
  return label ? `${trader.takma_ad} ${label}` : trader.takma_ad;
}

function formatEvent(event, trader) {
  if (event.tur === "isik") return `🔴 ${nameWithStyle(trader)} · sağlık ışığı kırmızı`;
  const icon = { acilis: "🟢", kapanis: "🔴", buyutme: "🔵" }[event.tur] || "⚪";
  const action = { acilis: "açtı", kapanis: "kapattı", buyutme: "büyüttü" }[event.tur];
  const pct = event.hesap_payi == null ? "" : ` · hesabın %${number(event.hesap_payi * 100, 1)}'i`;
  return `${icon} ${nameWithStyle(trader)} · ${event.coin} ${event.yon.toUpperCase()} ${action} · giriş ${number(event.fiyat)}${pct}`;
}

function callbackData(event, decision, reason) {
  const data = `k|${event.id}|${decision}${reason ? `|${reason}` : ""}`;
  return new TextEncoder().encode(data).byteLength <= 64 ? data : null;
}

function keyboard(event) {
  const open = callbackData(event, "a");
  const skip = callbackData(event, "s");
  return open && skip ? { inline_keyboard: [[{ text: "Açtım", callback_data: open }, { text: "Atladım", callback_data: skip }]] } : undefined;
}

function skipKeyboard(event) {
  const items = [["Geç gördüm", "g"], ["Beğenmedim", "b"], ["Diğer", "d"]]
    .map(([text, code]) => ({ text, callback_data: callbackData(event, "s", code) })).filter(item => item.callback_data);
  return { inline_keyboard: [items] };
}

function decision(data) {
  const found = CALLBACK.exec(data || "");
  if (!found) return null;
  const [, olay_id, raw, code] = found;
  if (raw === "a" && !code) return { olay_id, karar: "acti", neden: "diger" };
  if (raw === "s" && !code) return { olay_id, menu: true };
  const map = { g: "gec_gordum", b: "begenmedim", d: "diger" };
  return raw === "s" && map[code] ? { olay_id, karar: "atladi", neden: map[code] } : null;
}

async function currentStatus(fetcher = fetch) {
  const response = await fetcher(STATUS, { headers: { "cache-control": "no-cache" } });
  if (!response.ok) throw new Error("durum.json okunamadı");
  return response.json();
}

async function fills(address, start, fetcher = fetch) {
  const response = await retryFetch(INFO, { method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ type: "userFillsByTime", user: address, startTime: start, endTime: Date.now() }) }, fetcher);
  if (!response.ok) throw new Error(`Hyperliquid ${response.status}`);
  const body = await response.json();
  if (!Array.isArray(body)) throw new Error("Geçersiz Hyperliquid dolum yanıtı");
  return body.filter(isPerp);
}

async function sendOnce(env, event, trader, fetcher = fetch) {
  const previous = await env.DB.prepare("SELECT olay_id FROM bildirilen WHERE olay_id = ?").bind(event.id).first();
  if (previous) return false;
  await telegram(env, "sendMessage", { chat_id: env.TELEGRAM_CHAT_ID, text: formatEvent(event, trader),
    reply_markup: ["acilis", "buyutme"].includes(event.tur) ? keyboard(event) : undefined }, fetcher);
  await env.DB.prepare("INSERT OR IGNORE INTO bildirilen(olay_id, zaman) VALUES (?, ?)")
    .bind(event.id, nowIso()).run();
  return true;
}

function mergeFills(previous, incoming) {
  const all = new Map((previous || []).map(fill => [String(fill.tid), fill]));
  for (const fill of incoming) all.set(String(fill.tid), fill);
  return [...all.values()].sort((a, b) => Number(a.time) - Number(b.time) || String(a.tid).localeCompare(String(b.tid)));
}

async function accumulatedOrderEvents(env, trader, rows, account) {
  const grouped = new Map();
  for (const row of rows) grouped.set(String(row.oid), [...(grouped.get(String(row.oid)) || []), row]);
  const events = [];
  for (const [oid, incoming] of grouped) {
    const saved = await env.DB.prepare("SELECT dolumlar FROM emirler WHERE trader = ? AND oid = ?").bind(trader, oid).first();
    const merged = mergeFills(saved ? JSON.parse(saved.dolumlar) : [], incoming);
    await env.DB.prepare("INSERT INTO emirler(trader, oid, dolumlar) VALUES (?, ?, ?) ON CONFLICT(trader, oid) DO UPDATE SET dolumlar=excluded.dolumlar")
      .bind(trader, oid, JSON.stringify(merged)).run();
    events.push(...orderEvents(trader, merged, account));
  }
  return events;
}

async function runCron(env, fetcher = fetch) {
  let status;
  try { status = await currentStatus(fetcher); } catch { return; }
  for (const trader of status.traderlar || []) {
    const stored = await env.DB.prepare("SELECT son_dolum FROM imlec WHERE trader = ?").bind(trader.id).first();
    if (!stored) {
      await env.DB.prepare("INSERT INTO imlec(trader, son_dolum) VALUES (?, ?)").bind(trader.id, Date.now()).run();
      continue;
    }
    try {
      const rows = await fills(trader.adres, Number(stored.son_dolum), fetcher);
      for (const event of await accumulatedOrderEvents(env, trader.id, rows, Number(trader.hesap_degeri))) {
        if (["acilis", "kapanis", "buyutme"].includes(event.tur)) await sendOnce(env, event, trader, fetcher);
      }
      const newest = Math.max(Number(stored.son_dolum), ...rows.map(row => Number(row.time)));
      // Her dakika çalıştığı için yalnız değişince yazılır (D1 ücretsiz yazma kotası).
      if (newest !== Number(stored.son_dolum)) {
        await env.DB.prepare("UPDATE imlec SET son_dolum = ? WHERE trader = ?").bind(newest, trader.id).run();
      }
    } catch { /* the cursor intentionally remains unchanged */ }
    const previous = await env.DB.prepare("SELECT isik FROM isik WHERE trader = ?").bind(trader.id).first();
    if (trader.saglik?.isik === "kirmizi" && previous?.isik !== "kirmizi") {
      await sendOnce(env, { id: `${trader.id}-${status.uretildi}-isik`, tur: "isik", coin: "", yon: "", fiyat: null, hesap_payi: null }, trader, fetcher);
    }
    const current = trader.saglik?.isik || "yesil";
    if (previous?.isik !== current) {
      await env.DB.prepare("INSERT INTO isik(trader, isik) VALUES (?, ?) ON CONFLICT(trader) DO UPDATE SET isik=excluded.isik")
        .bind(trader.id, current).run();
    }
  }
}

async function handleTelegram(request, env, fetcher = fetch) {
  if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.TELEGRAM_WEBHOOK_SECRET) return new Response("forbidden", { status: 403 });
  const update = await request.json();
  const callback = update.callback_query;
  if (callback) {
    if (String(callback.from?.id) !== String(env.TELEGRAM_CHAT_ID) || String(callback.message?.chat?.id) !== String(env.TELEGRAM_CHAT_ID)) return new Response("ok");
    await telegram(env, "answerCallbackQuery", { callback_query_id: callback.id }, fetcher);
    const value = decision(callback.data);
    if (!value) return new Response("ok");
    if (value.menu) {
      await telegram(env, "editMessageReplyMarkup", { chat_id: callback.message.chat.id, message_id: callback.message.message_id,
        reply_markup: skipKeyboard({ id: value.olay_id }) }, fetcher);
      return new Response("ok");
    }
    await env.DB.prepare("INSERT INTO kararlar(olay_id, zaman, karar, neden, etiket) VALUES (?, ?, ?, ?, '') ON CONFLICT(olay_id) DO UPDATE SET zaman=excluded.zaman, karar=excluded.karar, neden=excluded.neden, etiket=''")
      .bind(value.olay_id, nowIso(), value.karar, value.neden).run();
    const label = value.karar === "acti" ? "✅ Açtım" : `⏭ Atladım — ${value.neden.replaceAll("_", " ")}`;
    await telegram(env, "editMessageReplyMarkup", { chat_id: callback.message.chat.id, message_id: callback.message.message_id,
      reply_markup: { inline_keyboard: [] } }, fetcher);
    await telegram(env, "editMessageText", { chat_id: callback.message.chat.id, message_id: callback.message.message_id,
      text: `${callback.message.text}\n${label}` }, fetcher);
    return new Response("ok");
  }
  const message = update.message;
  if (String(message?.chat?.id) !== String(env.TELEGRAM_CHAT_ID) || message?.text !== "/durum") return new Response("ok");
  let status;
  try { status = await currentStatus(fetcher); } catch { return new Response("ok"); }
  const age = Math.max(0, Math.floor((Date.now() - Date.parse(status.uretildi)) / 60000));
  const text = (status.traderlar || []).map(trader => `${trader.takma_ad}: ${trader.saglik.isik} · ${trader.pozisyonlar.length} açık pozisyon`).join("\n");
  await telegram(env, "sendMessage", { chat_id: env.TELEGRAM_CHAT_ID, text: `${text}\nVeri yaşı: ${age} dk` }, fetcher);
  return new Response("ok");
}

export default {
  scheduled(event, env, ctx) { ctx.waitUntil(runCron(env)); },
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/kararlar") {
      const rows = await env.DB.prepare("SELECT olay_id, substr(zaman, 1, 10) AS zaman, karar, CASE WHEN neden = 'bakiye_yok' THEN 'diger' ELSE neden END AS neden, etiket AS \"not\" FROM kararlar ORDER BY zaman").all();
      return json(rows.results || []);
    }
    if (request.method === "POST" && url.pathname === "/telegram") return handleTelegram(request, env);
    return new Response("not found", { status: 404 });
  },
};

export { accumulatedOrderEvents, callbackData, decision, formatEvent, handleTelegram, mergeFills, runCron, sendOnce };
