// GitHub zamanlayıcısı bu repoda saatlik/15 dk'lık koşuları sık atlıyor (bkz. arsiv.yml'deki not, 2026-10-29).
// Bu modül yalnız KARAR verir: workflow_dispatch ile tetiklemek gerekir mi? Ağ çağrısı yapmaz (test edilebilir, saf fonksiyon).
// Kural: aynı iş akışının çalışan/sıradaki bir koşusu varsa asla tetikleme (çift koşu yok — GitHub zaten concurrency
// grubu kullanıyor ama Worker kendi tarafında da aynı anda birden çok dispatch göndermemeli). Yoksa, son BİTEN
// koşunun yaşı beklenen aralığı (+tolerans) aşıyorsa tetikle; GitHub'ın kendi zamanlayıcısı yedek olarak kalır.

const AKTIF_DURUMLAR = new Set(["in_progress", "queued", "waiting", "requested", "pending"]);

/**
 * @param {Array<{status:string, conclusion?:string|null, run_started_at?:string, created_at?:string}>} runs GitHub'ın
 *   "list workflow runs" yanıtındaki workflow_runs dizisi (en yeni önce varsayılır).
 * @param {number} esikDk Son biten koşudan bu yana geçen dakika bu değeri aşarsa tetiklenir.
 * @param {number} nowMs
 * @returns {{tetikle: boolean, neden: string, yasDk?: number}}
 */
export function tetiklemeKarari(runs, esikDk, nowMs = Date.now()) {
  if ((runs || []).some(r => AKTIF_DURUMLAR.has(r.status))) return { tetikle: false, neden: "calisan_var" };
  // Son BİTMİŞ koşu (sonucu ne olursa olsun): arsiv.yml boşluk eşiğinde bilerek kırmızı biter; "son başarılı" alınsaydı
  // Worker her dakika yeniden tetikler, kalıcı bir hatada da sonsuz yeniden deneme olurdu. Hata uyarısı arsiv_alarm'ın işidir.
  const son = (runs || []).find(r => r.status === "completed");
  if (!son) return { tetikle: true, neden: "kosu_yok" };
  const baslangic = Date.parse(son.run_started_at || son.created_at);
  if (!Number.isFinite(baslangic)) return { tetikle: true, neden: "kosu_yok" };
  const yasDk = (nowMs - baslangic) / 60000;
  return yasDk > esikDk ? { tetikle: true, neden: "eski", yasDk: Math.round(yasDk) } : { tetikle: false, neden: "taze", yasDk: Math.round(yasDk) };
}
