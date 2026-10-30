CREATE TABLE IF NOT EXISTS imlec (
  trader TEXT PRIMARY KEY,
  son_dolum INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS bildirilen (
  olay_id TEXT PRIMARY KEY,
  zaman TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS emirler (
  trader TEXT NOT NULL,
  oid TEXT NOT NULL,
  dolumlar TEXT NOT NULL,
  PRIMARY KEY (trader, oid)
);
CREATE TABLE IF NOT EXISTS kararlar (
  olay_id TEXT PRIMARY KEY,
  zaman TEXT NOT NULL,
  karar TEXT NOT NULL CHECK(karar IN ('acti', 'atladi')),
  neden TEXT NOT NULL CHECK(neden IN ('gec_gordum', 'begenmedim', 'diger')),
  etiket TEXT NOT NULL DEFAULT ''  -- sözleşmedeki "not" alanı; NOT SQL'de ayrılmış kelime
);
CREATE TABLE IF NOT EXISTS isik (
  trader TEXT PRIMARY KEY,
  isik TEXT NOT NULL
);
-- Yalnız durum DEĞİŞİNCE uyarı göndermek için son bilinen durum (veri yaşı, kalabalık). Aynı uyarı tekrarlanmaz.
CREATE TABLE IF NOT EXISTS uyari_durum (
  anahtar TEXT PRIMARY KEY,
  deger TEXT NOT NULL
);
-- Günlük özetin en son hangi TR gününde gönderildiği (aynı gün iki kez gönderilmesin; Worker dakikada bir çalışıyor).
CREATE TABLE IF NOT EXISTS ozet_gonderildi (
  gun TEXT PRIMARY KEY
);
-- Worker sağlık kaydı (madde 19): kaynak başına ardışık hata sayısı ve son hata; 3. ardışık hatada Telegram alarmı.
CREATE TABLE IF NOT EXISTS saglik_kayit (
  kaynak TEXT PRIMARY KEY,
  ardisik INTEGER NOT NULL,
  son_hata TEXT,
  zaman TEXT
);
