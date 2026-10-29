// GitHub zamanlayıcısı bu repoda saatlik/15 dk'lık koşuları sık atlıyor (bkz. arsiv.yml'deki not, 2026-10-29).
// Bu modül yalnız KARAR verir: workflow_dispatch ile tetiklemek gerekir mi? Ağ çağrısı yapmaz (test edilebilir, saf fonksiyon).
// Kural: aynı iş akışının çalışan/sıradaki bir koşusu varsa asla tetikleme (çift koşu yok — GitHub zaten concurrency
// grubu kullanıyor ama Worker kendi tarafında da aynı anda birden çok dispatch göndermemeli). Yoksa, son BAŞARILI
// koşunun yaşı beklenen aralığı (+tolerans) aşıyorsa tetikle; GitHub'ın kendi zamanlayıcısı yedek olarak kalır.

const AKTIF_DURUMLAR = new Set(["in_progress", "queued", "waiting", "requested", "pending"]);

/**
 * @param {Array<{status:string, conclusion?:string|null, run_started_at?:string, created_at?:string}>} runs GitHub'ın
 *   "list workflow runs" yanıtındaki workflow_runs dizisi (en yeni önce varsayılır).
 * @param {number} esikDk Son başarılı koşudan bu yana geçen dakika bu değeri aşarsa tetiklenir.
 * @param {number} nowMs
 * @returns {{tetikle: boolean, neden: string, yasDk?: number}}
 */
export function tetiklemeKarari(runs, esikDk, nowMs = Date.now()) {
  if ((runs || []).some(r => AKTIF_DURUMLAR.has(r.status))) return { tetikle: false, neden: "calisan_var" };
  const basarili = (runs || []).find(r => r.status === "completed" && r.conclusion === "success");
  if (!basarili) return { tetikle: true, neden: "basarili_kosu_yok" };
  const baslangic = Date.parse(basarili.run_started_at || basarili.created_at);
  if (!Number.isFinite(baslangic)) return { tetikle: true, neden: "basarili_kosu_yok" };
  const yasDk = (nowMs - baslangic) / 60000;
  return yasDk > esikDk ? { tetikle: true, neden: "eski", yasDk: Math.round(yasDk) } : { tetikle: false, neden: "taze", yasDk: Math.round(yasDk) };
}
