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
