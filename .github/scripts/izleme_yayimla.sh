#!/usr/bin/env bash
# Yalnız Actions'ın geçici checkout'unda çalışır; kullanıcı checkout'unda çalıştırmayın.
set -euo pipefail
[ "${GITHUB_ACTIONS:-}" = true ] || { echo 'Yalnız GitHub Actions için.' >&2; exit 1; }
archive=$(mktemp -d)
trap 'rm -rf "$archive"' EXIT
for path in durum.json motor.json binance_vadeli.txt; do
  if [ -f "izleme/$path" ]; then cp "izleme/$path" "$archive/"; fi
done
[ -s "$archive/durum.json" ] && [ -s "$archive/motor.json" ]
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
if git ls-remote --exit-code --heads origin copytrade-izleme >/dev/null; then
  git fetch origin copytrade-izleme
  git checkout -f -B copytrade-izleme FETCH_HEAD
else
  status=$?
  if [ "$status" -ne 2 ]; then exit "$status"; fi
  git checkout --orphan copytrade-izleme
  git rm -rfq --ignore-unmatch .
fi
mkdir -p izleme
cp -r "$archive"/. izleme/
# Worker'ın kararlar.jsonl dosyası ve diğer arşivleri korunur.
for path in durum.json motor.json binance_vadeli.txt; do
  if [ -f "$archive/$path" ]; then git add -f "izleme/$path"; fi
done
if git diff --cached --quiet; then exit 0; fi
git commit -m "izleme: saatlik durum $(date -u +%FT%TZ)"
for attempt in 1 2 3; do
  if git ls-remote --exit-code --heads origin copytrade-izleme >/dev/null; then
    git pull --rebase origin copytrade-izleme
  else
    status=$?
    if [ "$status" -ne 2 ]; then exit "$status"; fi
  fi
  if git push origin HEAD:copytrade-izleme; then exit 0; fi
  if [ "$attempt" -lt 3 ]; then sleep 5; fi
done
exit 1
