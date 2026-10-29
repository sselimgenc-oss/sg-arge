"""
Hyperliquid Gölge Trader Kopyalama: Karar Kuralları Karşılaştırma Simülasyonu
Bağımsız, tohumlu Monte Carlo simülasyonu (>=500 tekrar).

Karşılaştırılan Kurallar:
(K1) Bayesçi Normal-Normal: Önsel fark ~ N(0, 0.30^2), 7 günlük blok bootstrap SE.
(K2) Her-An-Geçerli Test (Bahis Martingalesi): E <- E * (1 + lambda * clip(d_hafta, +-c)/c), c=5%, lambda in {0.1, 0.2, 0.3}, E >= 20.
(K3) Sabit Bakış (Group Sequential O'Brien-Fleming): 4, 8, 12. haftalarda iki taraflı O'Brien-Fleming eşiği.
"""

import argparse
import time
import numpy as np
import pandas as pd
from scipy.stats import norm


def simulate_daily_difference(n_days: int = 182, delta_annual: float = 0.0, rng: np.random.Generator = None) -> np.ndarray:
    """
    36 trader'lı veri üretimi:
    - 18 oda trader'ı, 18 kontrol trader'ı
    - Oynaklık sigma_i ~ Uniform(0.02, 0.08)
    - BTC betası beta_i ~ Uniform(0.0, 1.5)
    - Ortak faktör korelasyonu rho_i ~ Uniform(0.2, 0.5)
    - Şoklar: Student-t (df=4), varyans = 4/(4-2) = 2, standartlaştırılmış: t / sqrt(2)
    - BTC günlük oynaklık: %2.5 (sigma_btc = 0.025)
    - BTC beta düzeltmesi: R_i,t - beta_i * R_btc
    - Günlük fark: d_t = r_room,t - r_ctrl,t
    """
    if rng is None:
        rng = np.random.default_rng()

    n_room = 18
    n_ctrl = 18
    n_traders = n_room + n_ctrl  # 36

    sigma_i = rng.uniform(0.02, 0.08, size=n_traders)
    beta_i = rng.uniform(0.0, 1.5, size=n_traders)
    rho_i = rng.uniform(0.2, 0.5, size=n_traders)

    # Ortak faktör ve BTC
    f_common = rng.standard_t(df=4, size=n_days) / np.sqrt(2.0)
    sigma_btc = 0.025
    r_btc = rng.normal(0.0, sigma_btc, size=n_days)

    # Trader'a özgü şoklar
    eta = rng.standard_t(df=4, size=(n_traders, n_days)) / np.sqrt(2.0)

    # Ortak faktörle korele şok bileşimi
    shock = rho_i[:, None] * f_common[None, :] + np.sqrt(1.0 - rho_i[:, None] ** 2) * eta

    # Oda için yıllık alfa farkı / 365 (kripto 365 gün esası)
    delta_daily = delta_annual / 365.0
    alpha = np.zeros(n_traders)
    alpha[:n_room] = delta_daily

    # Beta düzeltmeli getiri: R_{i,t} - beta_i * R_btc = alpha_i + sigma_i * shock_{i,t}
    r_adj = alpha[:, None] + sigma_i[:, None] * shock

    # Eşit ağırlıklı portföyler
    r_room_adj = r_adj[:n_room].mean(axis=0)
    r_ctrl_adj = r_adj[n_room:].mean(axis=0)

    d_t = r_room_adj - r_ctrl_adj
    return d_t


def eval_k1_bayes(d_t: np.ndarray, max_weeks: int = 26) -> tuple[str, int]:
    """
    (K1) Bayesçi Normal-Normal:
    Önsel yıllık fark ~ N(0, 0.30^2)
    SE: 7 günlük blok bootstrap (kayan blok / analytical MBB limit)
    Umut verici: P(fark > 0) > 0.95 ve P(fark > 20%/yıl) > 0.70
    Durdur: P(fark > 20%/yıl) < 0.10
    26. haftada karar yoksa 'kanıt yok'
    """
    mu_0 = 0.0
    sigma_0 = 0.30
    tau_0 = 1.0 / (sigma_0 ** 2)

    for w in range(1, max_weeks + 1):
        t_days = w * 7
        d_sub = d_t[:t_days]
        theta_hat = d_sub.mean() * 365.0

        if w == 1:
            # 1. haftada tek blok olduğu için günlük varyans ölçeklenir
            se_theta = (np.std(d_sub, ddof=1) / np.sqrt(t_days)) * 365.0
        else:
            # 7 günlük kayan blok bootstrap (MBB)
            blocks = np.lib.stride_tricks.sliding_window_view(d_sub, 7)
            b_means = blocks.mean(axis=1)
            var_mean = np.var(b_means, ddof=1) / w
            se_theta = np.sqrt(max(var_mean, 1e-12)) * 365.0

        tau_n = 1.0 / (se_theta ** 2)
        tau_post = tau_0 + tau_n
        sigma_post = 1.0 / np.sqrt(tau_post)
        mu_post = (theta_hat * tau_n) / tau_post

        p_gt_0 = norm.sf(0.0, loc=mu_post, scale=sigma_post)
        p_gt_20 = norm.sf(0.20, loc=mu_post, scale=sigma_post)

        if p_gt_0 > 0.95 and p_gt_20 > 0.70:
            return "umut_verici", w
        elif p_gt_20 < 0.10:
            return "durdur", w

    return "kanit_yok", max_weeks


def eval_k2_martingale(d_t: np.ndarray, lam: float = 0.2, c: float = 0.05, max_weeks: int = 26) -> tuple[str, int]:
    """
    (K2) Her-an-geçerli test:
    Bahis martingalesi: E <- E * (1 + lambda * clip(d_hafta, +-c) / c)
    Zarar tarafı için ayna testi: E_neg <- E_neg * (1 - lambda * clip(d_hafta, +-c) / c)
    E >= 20 -> 'fark var'
    """
    weekly_d = d_t.reshape(max_weeks, 7).sum(axis=1)
    e_pos = 1.0
    e_neg = 1.0

    for w, d_w in enumerate(weekly_d, 1):
        x = np.clip(d_w, -c, c) / c
        e_pos *= (1.0 + lam * x)
        e_neg *= (1.0 - lam * x)

        if e_pos >= 20.0:
            return "umut_verici", w
        elif e_neg >= 20.0:
            return "durdur", w

    return "kanit_yok", max_weeks


def eval_k3_obrien_fleming(d_t: np.ndarray) -> tuple[str, int]:
    """
    (K3) Sabit bakış:
    Yalnızca 4., 8., 12. haftalarda O'Brien-Fleming tipi eşik.
    K=3, alpha=0.05 (iki taraflı) için standart OF kritik değerleri:
    w=4 (t=1/3): 3.4711
    w=8 (t=2/3): 2.4544
    w=12 (t=1.0): 2.0040
    """
    b_thresholds = {4: 3.4711, 8: 2.4544, 12: 2.0040}

    for w in [4, 8, 12]:
        t_days = w * 7
        d_sub = d_t[:t_days]
        mean_d = d_sub.mean()
        se_d = np.std(d_sub, ddof=1) / np.sqrt(t_days)
        z = mean_d / max(se_d, 1e-12)

        crit = b_thresholds[w]
        if z >= crit:
            return "umut_verici", w
        elif z <= -crit:
            return "durdur", w

    return "kanit_yok", 12


def run_simulation(n_reps: int = 500, seed: int = 2026) -> pd.DataFrame:
    deltas = [0.0, 0.10, 0.25, 0.50, -0.25]
    rules = [
        "K1 (Bayes)",
        "K2 (λ=0.1)",
        "K2 (λ=0.2)",
        "K2 (λ=0.3)",
        "K3 (O'Brien-Fleming)",
    ]

    rng = np.random.default_rng(seed)
    raw_records = {r: {d: [] for d in deltas} for r in rules}

    t0 = time.time()
    for delta in deltas:
        for _ in range(n_reps):
            d_t = simulate_daily_difference(182, delta, rng)
            raw_records["K1 (Bayes)"][delta].append(eval_k1_bayes(d_t))
            raw_records["K2 (λ=0.1)"][delta].append(eval_k2_martingale(d_t, lam=0.1))
            raw_records["K2 (λ=0.2)"][delta].append(eval_k2_martingale(d_t, lam=0.2))
            raw_records["K2 (λ=0.3)"][delta].append(eval_k2_martingale(d_t, lam=0.3))
            raw_records["K3 (O'Brien-Fleming)"][delta].append(eval_k3_obrien_fleming(d_t))
    elapsed = time.time() - t0

    table_rows = []
    for r in rules:
        for delta in deltas:
            outcomes = raw_records[r][delta]
            decs = [o[0] for o in outcomes]
            weeks = [o[1] for o in outcomes]

            p_umut = np.mean([d == "umut_verici" for d in decs])
            p_durdur = np.mean([d == "durdur" for d in decs])
            p_kanit_yok = np.mean([d == "kanit_yok" for d in decs])
            mean_w = np.mean(weeks)

            # 1. Yanlış "Umut Verici" Oranı (fark=0'da)
            if delta == 0.0:
                fp_umut_str = f"{p_umut * 100:.1f}%"
            elif delta < 0.0:
                fp_umut_str = f"{p_umut * 100:.1f}%"  # Ters yönlü yanlış pozitif
            else:
                fp_umut_str = "—"  # Fark pozitifken umut verici yanlış alarm değil, doğru tespittir

            # 2. Doğru Tespit Oranı
            if delta > 0.0:
                tp_str = f"{p_umut * 100:.1f}%"
            elif delta < 0.0:
                tp_str = f"{p_durdur * 100:.1f}%"
            else:
                tp_str = f"{p_kanit_yok * 100:.1f}% (H0)"

            # 3. Yanlış "Durdur" Oranı (fark>0'da)
            if delta > 0.0:
                fn_stop_str = f"{p_durdur * 100:.1f}%"
            elif delta == 0.0:
                fn_stop_str = f"{p_durdur * 100:.1f}%"
            else:
                fn_stop_str = "—"  # Fark negatifken durdurmak doğru karardır

            table_rows.append({
                "Kural": r,
                "Gerçek Yıllık Fark": f"{delta * 100:+.0f}%",
                "Yanlış 'Umut Verici'": fp_umut_str,
                "Doğru Tespit Oranı": tp_str,
                "Yanlış 'Durdur' Oranı": fn_stop_str,
                "Ort. Karar Haftası": f"{mean_w:.1f}",
                "Umut Verici (%)": f"{p_umut * 100:.1f}%",
                "Durdur (%)": f"{p_durdur * 100:.1f}%",
                "Kanıt Yok (%)": f"{p_kanit_yok * 100:.1f}%",
            })

    df_summary = pd.DataFrame(table_rows)
    return df_summary, elapsed


def main():
    parser = argparse.ArgumentParser(description="Hyperliquid Karar Kuralları Simülasyonu")
    parser.add_argument("--reps", type=int, default=500, help="Tekrar sayısı (varsayılan: 500)")
    parser.add_argument("--seed", type=int, default=2026, help="Rastgelelik tohumu (varsayılan: 2026)")
    args = parser.parse_args()

    print(f"Simülasyon Başlatılıyor: {args.reps} tekrar/senaryo, Tohum={args.seed}...")
    df_res, elapsed = run_simulation(n_reps=args.reps, seed=args.seed)

    print("\n" + "=" * 90)
    print("HYPERLIQUID GÖLGE TRADER KARAR KURALLARI PERFORMANS TABLOSU")
    print(f"Çalıştırma Süresi: {elapsed:.2f} saniye (Toplam {args.reps * 5} patika)")
    print("=" * 90)
    print(df_res.to_string(index=False))
    print("=" * 90)


if __name__ == "__main__":
    main()