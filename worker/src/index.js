import { eventId, isPerp, orderEvents } from "./events.js";
import { tetiklemeKarari } from "./tetikleyici.js";

const INFO = "https://api.hyperliquid.xyz/info";
const STATUS = "https://raw.githubusercontent.com/sselimgenc-oss/sg-arge/copytrade-izleme/izleme/durum.json";
const CALLBACK = /^k\|([^|]+)\|([as])(?:\|([gbd]))?$/;
const REPO = "sselimgenc-oss/sg-arge";
// izleme.yml saatlik (cron "23 * * * *"), arsiv.yml 15 dk'da bir (cron "*/15 * * * *") çalışmalı; GitHub zamanlayıcısı
// bu repoda sık atladığından (2026-10-29: 17:26'dan sonra izleme hiç başlamadı) burada yedek tetikleme var.
const TETIKLENECEK = [
  { dosya: "izleme.yml", esikDk: 75 },   // 60 dk + 15 dk tolerans
  { dosya: "arsiv.yml", esikDk: 20 },    // 15 dk + 5 dk tolerans
];

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

function isNotified(trader) { return trader.kol === "oda"; }

function githubHeaders(env) {
  return { authorization: `Bearer ${env.GITHUB_ACTIONS_TOKEN}`, accept: "application/vnd.github+json", "x-github-api-version": "2022-11-28", "user-agent": "sg-arge-worker" };
}

async function workflowRuns(env, dosya, fetcher = fetch) {
  const response = await fetcher(`https://api.github.com/repos/${REPO}/actions/workflows/${dosya}/runs?per_page=5`, { headers: githubHeaders(env) });
  if (!response.ok) throw new Error(`GitHub runs ${dosya} ${response.status}`);
  const body = await response.json();
  return body.workflow_runs || [];
}

async function dispatchWorkflow(env, dosya, fetcher = fetch) {
  const response = await fetcher(`https://api.github.com/repos/${REPO}/actions/workflows/${dosya}/dispatches`, {
    method: "POST", headers: { ...githubHeaders(env), "content-type": "application/json" }, body: JSON.stringify({ ref: "main" }),
  });
  if (!response.ok) throw new Error(`GitHub dispatch ${dosya} ${response.status}`);
}

// Token yoksa (secret ayarlanmamış) sessizce atlanır — GitHub'ın kendi zamanlayıcısı yedek olarak çalışmaya devam eder.
async function tetiklemeKontrol(env, fetcher = fetch) {
  if (!env.GITHUB_ACTIONS_TOKEN) return;
  for (const { dosya, esikDk } of TETIKLENECEK) {
    try {
      const runs = await workflowRuns(env, dosya, fetcher);
      if (tetiklemeKarari(runs, esikDk).tetikle) await dispatchWorkflow(env, dosya, fetcher);
    } catch { /* bir iş akışındaki hata diğerinin kontrolünü engellemesin */ }
  }
}

async function runCron(env, fetcher = fetch) {
  let status;
  try { status = await currentStatus(fetcher); } catch { return; }
  // Bildirim yalnız kol = oda için; kontrol/taban/elle kolları sessiz izlenir (Worker onlar için Hyperliquid'e de gitmez).
  for (const trader of (status.traderlar || []).filter(isNotified)) {
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
    // The first observed colour is a baseline, not an alert. Alert only on a known non-red → red transition.
    if (previous && trader.saglik?.isik === "kirmizi" && previous.isik !== "kirmizi") {
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
  const tetikleme = env.GITHUB_ACTIONS_TOKEN ? "" : "\n\n🔁 Otomatik tetikleme: kapalı (GITHUB_ACTIONS_TOKEN secret'ı yok)";
  await telegram(env, "sendMessage", { chat_id: env.TELEGRAM_CHAT_ID, text: formatStatus(status) + tetikleme, disable_web_page_preview: true }, fetcher);
  return new Response("ok");
}

const PANO = "https://sselimgenc-oss.github.io/sg-pano/";
const ESKI_DK = 90;
const LIGHT = { yesil: "🟢", sari: "🟡", kirmizi: "🔴" };

// Oda risk bayrakları (GOREV_ODA_RISK): yalnız uyarı varsa tek satır; bilgi amaçlı, otomasyon yok.
function riskLine(status, room) {
  const parts = [];
  if (status.kalabalik?.uyari && status.kalabalik.uyari_metni) parts.push(status.kalabalik.uyari_metni);
  const flagged = room.filter(t => t.yonsuz_bayrak?.bayrak).map(t => t.takma_ad);
  if (flagged.length) parts.push(`yönsüz bayrak: ${flagged.slice(0, 3).join(", ")}${flagged.length > 3 ? ` +${flagged.length - 3}` : ""}`);
  return parts.length ? `⚠️ ${parts.join(" · ")}` : "";
}

// /durum: yalnız oda (bildirimli kol) ayrıntılı; diğer kollar sayı.
function formatStatus(status, nowMs = Date.now()) {
  const all = status.traderlar || [];
  const hasArms = all.some(t => t.kol);
  const room = hasArms ? all.filter(isNotified) : all;
  const age = Math.max(0, Math.floor((nowMs - Date.parse(status.uretildi)) / 60000));
  const lines = [];
  const starts = room.map(t => Date.parse(t.t0)).filter(Number.isFinite);
  const week = starts.length ? Math.min(12, Math.floor((nowMs - Math.min(...starts)) / (7 * 86400000)) + 1) : null;
  lines.push(`📊 SG Arge · Pilot${week ? ` · hafta ${week}/12` : ""}`);
  lines.push(age > ESKI_DK ? `⚠️ Veri ${age} dk önce — güncellenmedi` : `🕐 Veri ${age} dk önce`);
  lines.push("");
  const count = c => room.filter(t => (t.saglik?.isik || "yesil") === c).length;
  const open = room.reduce((sum, t) => sum + (t.pozisyonlar || []).length, 0);
  lines.push(`${hasArms ? "Oda" : "İzlenen"} · ${room.length} trader`);
  lines.push(`🟢 ${count("yesil")}   🟡 ${count("sari")}   🔴 ${count("kirmizi")}`);
  lines.push(`📂 Açık pozisyon: ${open}`);
  for (const [colour, title] of [["kirmizi", "🔴 Dikkat"], ["sari", "🟡 İzle"]]) {
    const rows = room.filter(t => t.saglik?.isik === colour);
    if (!rows.length) continue;
    lines.push("", title);
    for (const t of rows.slice(0, 5)) lines.push(`• ${t.takma_ad} · ${(t.saglik.nedenler || []).join(", ") || LIGHT[colour]}`);
    if (rows.length > 5) lines.push(`• +${rows.length - 5} trader daha (panoda)`);
  }
  const risk = riskLine(status, room);
  if (risk) lines.push("", risk);
  lines.push("");
  if (hasArms) lines.push(`👀 Sessiz izleme: ${all.length - room.length} trader (kontrol, taban, elle)`);
  lines.push(`Pano: ${PANO}`);
  return lines.join("\n");
}

export default {
  scheduled(event, env, ctx) { ctx.waitUntil(runCron(env)); ctx.waitUntil(tetiklemeKontrol(env)); },
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

export { accumulatedOrderEvents, callbackData, decision, dispatchWorkflow, formatEvent, formatStatus, handleTelegram, isNotified, mergeFills, runCron, sendOnce, tetiklemeKontrol, workflowRuns };
