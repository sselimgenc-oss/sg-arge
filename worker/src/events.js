export function isPerp(fill) {
  return !String(fill.coin || "").startsWith("@") && !String(fill.coin || "").includes("/");
}

export function signed(fill) {
  return Number(fill.sz) * (["A", "Sell", "sell"].includes(String(fill.side)) ? -1 : 1);
}

export function eventId(trader, oid, kind) {
  return `${trader}-${String(oid)}-${kind}`;
}

export function orderEvents(trader, fills, account = 0) {
  const grouped = new Map();
  for (const fill of [...fills].filter(isPerp).sort((a, b) => Number(a.time) - Number(b.time) || String(a.tid).localeCompare(String(b.tid)))) {
    if (fill.oid === undefined || fill.oid === null || String(fill.oid) === "") throw new Error("Dolumda oid eksik");
    const key = String(fill.oid);
    grouped.set(key, [...(grouped.get(key) || []), fill]);
  }
  return [...grouped.entries()].sort(([, a], [, b]) => Number(a[0].time) - Number(b[0].time)).flatMap(([oid, rows]) => {
    const first = rows[0], last = rows.at(-1);
    const before = Number(first.startPosition || 0);
    const after = Number(last.startPosition || before) + signed(last);
    const price = rows.reduce((sum, fill) => sum + Number(fill.px) * Math.abs(Number(fill.sz)), 0) /
      rows.reduce((sum, fill) => sum + Math.abs(Number(fill.sz)), 0);
    const kinds = [];
    if (before && (!after || before * after < 0)) kinds.push(["kapanis", before]);
    if (after && (!before || before * after < 0)) kinds.push(["acilis", after]);
    else if (before * after > 0 && Math.abs(Math.abs(after) / Math.abs(before) - 1) > 0.25) {
      kinds.push([Math.abs(after) > Math.abs(before) ? "buyutme" : "azaltma", after]);
    }
    return kinds.map(([tur, size]) => ({
      id: eventId(trader, oid, tur), zaman: new Date(Number(last.time)).toISOString(), trader, tur,
      coin: last.coin, yon: size > 0 ? "long" : "short", fiyat: price,
      hesap_payi: account > 0 ? Math.abs(after * price) / account : 0,
    }));
  });
}
