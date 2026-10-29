> **Lider denetim notu (2026-10-29):** Argon A22. Kod okundu, mantık tutarlı; kendi ortamımızda yeniden koşulmadı.
> Varsayılan veri üretimi (trader oynaklığı günlük %2–8, df=4) gerçek arşivle doğrulanmalı.
> **Sonuçlar:** (1) 12 haftada yıllık %50 fark bile ancak ~%20 güçle görülür; saptanabilir en küçük fark 12 haftada ~%150/yıl,
> 24 haftada ~%110/yıl. Yani resmî analiz büyük olasılıkla "kanıt yok" der; trader kararları istatistik kanıta değil gözleme
> dayanacak (ön kayıt 1.5 kararıyla uyumlu). (2) MBB %95 aralığı gerçekte ~%90 kapsıyor → aralık biraz dar, yanlış pozitif riski artar.
> (3) Durdurma 1, becerisiz odada ~%43 tetikleniyor; bu "yanlış alarm" değil beklenen davranış (beceri yoksa durmalı). Eksik olan:
> gerçek alfa varken kuralın yanlışlıkla durdurma oranı (hesaplanmadı). Eşik değişikliği kullanıcı kararıdır; Faz 3 sonucu ile birlikte değerlendirilir.

# Hyperliquid Trader Kopyalama Araştırması: Monte Carlo Güç ve Hipotez Simülasyon Raporu

**Tarih:** 29 Ekim 2026  
**Bağlam:** Hyperliquid gölge hesap (gerçek para yok) trader kopyalama araştırması. 18 kişilik seçilmiş "oda" ile 18 kişilik eşleştirilmiş rastgele "kontrol" grubu karşılaştırması.  
**Metodoloji:** Faktör modeli, OLS beta düzeltmesi, 7 günlük Örtüşen Blok Bootstrap (Moving Block Bootstrap - MBB).  

---

## 1. Çalıştırma Bilgileri ve Deney Kurulumu

* **Simülasyon Betiği:** `hyperliquid_copytrade_sim.py`
* **Çalıştırma Komutu:** `python3 hyperliquid_copytrade_sim.py 500 42`
* **Parametreler:** $N = 500$ bağımsız Monte Carlo tohumu (koşusu), tohum başına $B = 500$ MBB blok bootstrap tekrarı.
* **Toplam Çalışma Süresi:** 10.72 saniye.

### Temel Varsayımlar
1. **Piyasa Takvimi:** Kripto varlık piyasaları 7/24/365 işlem gördüğünden yıllıklandırma bazı $365$ gün kabul edilmiştir ($\alpha_{\text{günlük}} = \alpha_{\text{yıllık}} / 365$).
2. **Veri Üretim Süreci (DGP):** 36 trader'ın günlük getirileri kalın kuyruklu Student-$t$ ($df=4$) dağılımına sahiptir. BTC oynaklığı $\sigma_{\text{BTC}} = \%2.5$/gün (yıllık ~%47.8), trader oynaklıkları $\sigma_i \in [\%2.0, \%8.0]$, BTC betaları $\beta_i \in [0.0, 1.5]$ ve ikili korelasyonlar $\rho_{ij} \in [0.20, 0.50]$ aralığındadır.
3. **Portföy Ağırlıkları:** Her iki grupta 18 trader eşit ağırlıklıdır ($w_i = 1/18$). Fark serisi $d_t = R_{\text{oda}, t} - R_{\text{kontrol}, t}$.
4. **Piyasa Betası Düzeltmesi:** $d_t = \alpha + \beta \cdot \text{BTC}_t + \varepsilon_t$ (OLS). Karar istatistiği günlük $\hat{\alpha}$'dır.
5. **MBB Konfigürasyonu:** Haftalık mevsimselliği ve otokorelasyonu korumak için blok uzunluğu $b=7$ gün seçilmiştir. Persentil yöntemiyle %95 güven aralığı ($[2.5\%, 97.5\%]$) türetilmiştir.

---

## 2. Sıfır Beceri ($H_0$) Simülasyonu

Oda ve kontrol grupları arasında hiçbir beceri farkı olmadığı ($\alpha_{\text{gerçek}} = 0$) durumda elde edilen ampirik sonuçlar:

| İnceleme | Ampirik Sonuç (N=500) | Beklenen / Teorik Değer | Yorum ve Değerlendirme |
| :--- | :---: | :---: | :--- |
| **(a) 60 Günlük Tek Pencerede $\alpha > 0$ Oranı** | **%49.20** | ~%50.00 | $H_0$ simetrisi doğrulanmıştır; şans faktörü dengelidir. |
| **(b) Durdur Kuralı Yanlış Tetiklenme ($K = 6$)** | **%43.20** | %34.38 (Bağımsız) | 14 gün kaydırmalı 60 günlük pencereler 46 gün (%76.7) örtüşür. Otokorelasyon kümelenme yaratır. |
| **(b) Durdur Kuralı Yanlış Tetiklenme ($K = 8$)** | **%40.40** | %36.33 (Bağımsız) | Örtüşen pencerelerde varyans şişmesi nedeniyle yalancı alarm oranı yüksek kalır. |
| **(b) Durdur Kuralı Yanlış Tetiklenme ($K = 10$)** | **%43.00** | %37.70 (Bağımsız) | Pencerelerin bağımsız olmaması sebebiyle kural Tip I hata üretmeye devam eder. |
| **(b) Durdur Kuralı Yanlış Tetiklenme ($K = 12$)** | **%42.80** | %38.72 (Bağımsız) | Başarısız pencere oranı $>\%50$ kuralı, sıfır becerili odaların ~%43'ünü yanlışlıkla durdurur. |
| **(c) MBB %95 Kapsama Oranı ($n = 60$ gün)** | **%89.80** | %95.00 | Kalın kuyruk ($df=4$) ve küçük örneklem, persentil aralığını hafif daraltır (undercoverage). |
| **(c) MBB %95 Kapsama Oranı ($n = 84$ gün)** | **%90.00** | %95.00 | 12 haftada kapsama oranı hafif iyileşse de uç kuyruk riskleri nedeniyle nominal %95'in altındadır. |

---

## 3. Güç Analizi (Empirical Power)

Oda portföyüne net alfa enjekte edilerek ($d_t^{(\text{inj})} = d_t + \alpha_{\text{günlük}}$), MBB ile hesaplanan %95 güven aralığının alt sınırının sıfırdan büyük olma olasılığı ($P(\text{CI}_{\text{lower}} > 0)$) hesaplanmıştır:

| Yıllık Alfa | Günlük Alfa (Basit) | 84 Gün (12 Hafta) Güç | 168 Gün (24 Hafta) Güç |
| :---: | :---: | :---: | :---: |
| **+%10.0** | +2.74 bps/gün | **%6.60** | **%5.80** |
| **+%25.0** | +6.85 bps/gün | **%10.00** | **%11.20** |
| **+%50.0** | +13.70 bps/gün | **%20.00** | **%26.60** |

* **Ortalama Standart Hata:**  
  * $n = 84$ gün (12 hafta): $\text{SE}(\hat{\alpha}) = 14.61$ bps/gün (yıllık %53.33).  
  * $n = 168$ gün (24 hafta): $\text{SE}(\hat{\alpha}) = 10.55$ bps/gün (yıllık %38.50).  
* **Yorum:** Bireysel trader oynaklığının %2–%8 olduğu kripto piyasasında, yıllık %50 gibi yüksek bir getiri farkı dahi 12 haftada yalnızca %20 güçle istatistiksel anlamlılığa ulaşabilmektedir.

---

## 4. Saptanabilir En Küçük Fark (MDE — Minimum Detectable Effect)

%80 istatistiksel güç ($1 - \beta = 0.80$) ve %95 güven düzeyi ($\alpha_{\text{anlamlılık}} = 0.05$) altında tespit edilebilecek asgari farklar:

| Gözlem Penceresi | Günlük MDE | Yıllık MDE (%) | Analitik Yaklaşım ($2.80 \times \text{SE}$) |
| :--- | :---: | :---: | :---: |
| **12 Hafta ($n = 84$ gün)** | **41.71 bps/gün** | **+%152.24 / yıl** | $2.80 \times 14.61 \approx 40.91$ bps/gün |
| **24 Hafta ($n = 168$ gün)** | **29.87 bps/gün** | **+%109.01 / yıl** | $2.80 \times 10.55 \approx 29.54$ bps/gün |

---

## 5. Bağımsız Python 3 Simülasyon Kodu

```python
#!/usr/bin/env python3
"""
Hyperliquid Trader Kopyalama Araştırması: Monte Carlo Güç ve Hipotez Simülasyonu
================================================================================
Gereksinimler: Python 3, numpy, pandas (Ağ bağlantısı gerektirmez).
Çalıştırma: python3 hyperliquid_copytrade_sim.py 500 42
"""

import sys
import time
import numpy as np
import pandas as pd


def run_simulation(n_sims=500, seed=42, B_boot=500):
    start_time = time.time()

    # 1. PARAMETRELER VE MODEL TANIMI
    n_traders = 36
    df = 4
    sigma_btc = 0.025  # BTC günlük oynaklığı: %2.5 (yıllık ~%47.8)
    block_size = 7     # MBB blok uzunluğu: 7 gün (1 hafta)
    T_max = 214        # K=12 pencere için gereken gün sayısı: (12-1)*14 + 60
    
    annual_alphas = [0.10, 0.25, 0.50]
    daily_alphas = {r: r / 365.0 for r in annual_alphas}

    alpha_single_60 = []
    stop_triggered_k6 = []
    stop_triggered_k8 = []
    stop_triggered_k10 = []
    stop_triggered_k12 = []
    
    coverage_60 = []
    coverage_84 = []
    
    ci_lower_84_all = []
    ci_lower_168_all = []
    se_alpha_84_all = []
    se_alpha_168_all = []

    # 2. MONTE CARLO DÖNGÜSÜ
    for sim_idx in range(n_sims):
        sim_seed = seed + sim_idx
        sim_rng = np.random.default_rng(sim_seed)
        
        # Trader Parametreleri
        betas = sim_rng.uniform(0.0, 1.5, size=n_traders)
        min_vol = np.maximum(0.02, betas * sigma_btc + 0.005)
        sigmas = sim_rng.uniform(min_vol, 0.08)
        
        # Faktör Modeli: Ortak kripto faktörü ile korelasyon ~0.2 - 0.5
        rem_var = sigmas**2 - (betas * sigma_btc)**2
        frac_common = 0.35
        gamma = np.sqrt(frac_common * rem_var)
        s = np.sqrt((1.0 - frac_common) * rem_var)
        
        # Student-t (df=4) Şokları
        t_scale = np.sqrt((df - 2.0) / df)
        z_btc = sim_rng.standard_t(df, size=T_max) * t_scale
        btc = sigma_btc * z_btc
        
        z_m = sim_rng.standard_t(df, size=T_max) * t_scale
        z_eps = sim_rng.standard_t(df, size=(n_traders, T_max)) * t_scale
        
        returns = (betas[:, None] * btc[None, :] +
                   gamma[:, None] * z_m[None, :] +
                   s[:, None] * z_eps)
        
        # Rastgele 18 / 18 Bölme
        perm = sim_rng.permutation(n_traders)
        oda_idx = perm[:18]
        ctrl_idx = perm[18:]
        
        r_oda = np.mean(returns[oda_idx, :], axis=0)
        r_ctrl = np.mean(returns[ctrl_idx, :], axis=0)
        d = r_oda - r_ctrl

        # 1(a) 60 Günlük Tek Pencerede alpha > 0
        d_60 = d[:60]
        btc_60 = btc[:60]
        cov_60 = np.cov(btc_60, d_60)
        b_60 = cov_60[0, 1] / cov_60[0, 0]
        a_60 = np.mean(d_60) - b_60 * np.mean(btc_60)
        alpha_single_60.append(a_60 > 0)

        # 1(b) 14 Gün Kaydırmalı 6-12 Pencerede Durdur Kuralı
        alphas_windows = []
        for k in range(12):
            s_idx = k * 14
            e_idx = s_idx + 60
            d_w = d[s_idx:e_idx]
            btc_w = btc[s_idx:e_idx]
            cov_w = np.cov(btc_w, d_w)
            b_w = cov_w[0, 1] / cov_w[0, 0]
            a_w = np.mean(d_w) - b_w * np.mean(btc_w)
            alphas_windows.append(a_w)
        alphas_windows = np.array(alphas_windows)

        stop_triggered_k6.append(np.mean(alphas_windows[:6] <= 0) > 0.50)
        stop_triggered_k8.append(np.mean(alphas_windows[:8] <= 0) > 0.50)
        stop_triggered_k10.append(np.mean(alphas_windows[:10] <= 0) > 0.50)
        stop_triggered_k12.append(np.mean(alphas_windows[:12] <= 0) > 0.50)

        # Vektörize MBB Fonksiyonu
        def mbb_alpha_distribution(d_sub, btc_sub):
            T = len(d_sub)
            num_blocks = T - block_size + 1
            idx_blocks = np.arange(num_blocks)[:, None] + np.arange(block_size)[None, :]
            
            d_bl = d_sub[idx_blocks]
            btc_bl = btc_sub[idx_blocks]
            
            k_blocks = int(np.ceil(T / block_size))
            rand_idx = sim_rng.integers(0, num_blocks, size=(B_boot, k_blocks))
            
            d_boot = d_bl[rand_idx].reshape(B_boot, k_blocks * block_size)[:, :T]
            btc_boot = btc_bl[rand_idx].reshape(B_boot, k_blocks * block_size)[:, :T]
            
            btc_m = np.mean(btc_boot, axis=1)
            d_m = np.mean(d_boot, axis=1)
            btc_dev = btc_boot - btc_m[:, None]
            d_dev = d_boot - d_m[:, None]
            
            var_b = np.sum(btc_dev**2, axis=1)
            cov_bd = np.sum(btc_dev * d_dev, axis=1)
            b_boot = cov_bd / var_b
            a_boot = d_m - b_boot * btc_m
            return a_boot

        # 1(c) MBB %95 Kapsama
        a_boot_60 = mbb_alpha_distribution(d[:60], btc[:60])
        ci_l60, ci_u60 = np.percentile(a_boot_60, [2.5, 97.5])
        coverage_60.append(ci_l60 <= 0.0 <= ci_u60)

        a_boot_84 = mbb_alpha_distribution(d[:84], btc[:84])
        ci_l84, ci_u84 = np.percentile(a_boot_84, [2.5, 97.5])
        coverage_84.append(ci_l84 <= 0.0 <= ci_u84)
        ci_lower_84_all.append(ci_l84)
        se_alpha_84_all.append(np.std(a_boot_84))

        a_boot_168 = mbb_alpha_distribution(d[:168], btc[:168])
        ci_l168, ci_u168 = np.percentile(a_boot_168, [2.5, 97.5])
        ci_lower_168_all.append(ci_l168)
        se_alpha_168_all.append(np.std(a_boot_168))

    elapsed_time = time.time() - start_time

    # 3. İSTATİSTİKSEL ÖZETLER
    ci_lower_84_all = np.array(ci_lower_84_all)
    ci_lower_168_all = np.array(ci_lower_168_all)
    se_alpha_84_all = np.array(se_alpha_84_all)
    se_alpha_168_all = np.array(se_alpha_168_all)

    rate_alpha_gt_0 = np.mean(alpha_single_60)
    stop_rate_k6 = np.mean(stop_triggered_k6)
    stop_rate_k8 = np.mean(stop_triggered_k8)
    stop_rate_k10 = np.mean(stop_triggered_k10)
    stop_rate_k12 = np.mean(stop_triggered_k12)

    cov_rate_60 = np.mean(coverage_60)
    cov_rate_84 = np.mean(coverage_84)

    power_results = []
    for r in annual_alphas:
        d_alpha = daily_alphas[r]
        p_84 = np.mean((ci_lower_84_all + d_alpha) > 0)
        p_168 = np.mean((ci_lower_168_all + d_alpha) > 0)
        power_results.append({
            'Yıllık Alfa': f"%{r*100:.0f}",
            'Günlük Alfa (bps)': f"{d_alpha * 10000:.2f} bps",
            '84 Gün (12 Hafta) Güç': f"%{p_84 * 100:.2f}",
            '168 Gün (24 Hafta) Güç': f"%{p_168 * 100:.2f}"
        })
    df_power = pd.DataFrame(power_results)

    mde_daily_84 = -np.percentile(ci_lower_84_all, 20)
    mde_annual_84 = mde_daily_84 * 365.0

    mde_daily_168 = -np.percentile(ci_lower_168_all, 20)
    mde_annual_168 = mde_daily_168 * 365.0

    mean_se_84 = np.mean(se_alpha_84_all)
    mean_se_168 = np.mean(se_alpha_168_all)

    print("=" * 80)
    print(f"HYPERLIQUID COPY-TRADE SIMULATION REPORT (Monte Carlo N={n_sims}, Seed={seed})")
    print(f"Toplam Çalışma Süresi: {elapsed_time:.2f} saniye")
    print("=" * 80)
    print(f"1(a) 60 günlük tek pencerede alpha > 0 oranı: %{rate_alpha_gt_0 * 100:.2f}")
    print(f"1(b) 'DURDUR' Kuralının Yanlış Tetiklenme Oranı:")
    print(f"     - K = 6  Pencere: %{stop_rate_k6 * 100:.2f}")
    print(f"     - K = 8  Pencere: %{stop_rate_k8 * 100:.2f}")
    print(f"     - K = 10 Pencere: %{stop_rate_k10 * 100:.2f}")
    print(f"     - K = 12 Pencere: %{stop_rate_k12 * 100:.2f}")
    print(f"1(c) MBB %95 Kapsama Oranı:")
    print(f"     - n = 60 gün : %{cov_rate_60 * 100:.2f}")
    print(f"     - n = 84 gün : %{cov_rate_84 * 100:.2f}")
    print("\nGüç Analizi:")
    print(df_power.to_string(index=False))
    print("\nMDE (%80 Güç):")
    print(f"  - 12 Hafta: Günlük {mde_daily_84 * 10000:.2f} bps (Yıllık %{mde_annual_84 * 100:.2f})")
    print(f"  - 24 Hafta: Günlük {mde_daily_168 * 10000:.2f} bps (Yıllık %{mde_annual_168 * 100:.2f})")
    print("=" * 80)


if __name__ == "__main__":
    n_sims = 500
    seed = 42
    if len(sys.argv) > 1:
        n_sims = int(sys.argv[1])
    if len(sys.argv) > 2:
        seed = int(sys.argv[2])
    run_simulation(n_sims=n_sims, seed=seed)
```
