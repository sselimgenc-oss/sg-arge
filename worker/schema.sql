CREATE TABLE IF NOT EXISTS imlec (
  trader TEXT PRIMARY KEY,
  son_dolum INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS bildirilen (
  olay_id TEXT PRIMARY KEY,
  zaman TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS kararlar (
  olay_id TEXT PRIMARY KEY,
  zaman TEXT NOT NULL,
  karar TEXT NOT NULL CHECK(karar IN ('acti', 'atladi')),
  neden TEXT NOT NULL CHECK(neden IN ('gec_gordum', 'begenmedim', 'bakiye_yok', 'diger')),
  not TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS isik (
  trader TEXT PRIMARY KEY,
  isik TEXT NOT NULL
);
