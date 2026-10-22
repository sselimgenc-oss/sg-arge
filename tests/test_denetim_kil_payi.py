import numpy as np

from backtests.denetim_kil_payi import benjamini_hochberg, student_t_cdf, welch_less


def test_student_t_cdf_matches_tables():
    assert abs(student_t_cdf(-2.228, 10) - 0.025) < 1e-4
    assert abs(student_t_cdf(-1.6448536, 1e6) - 0.05) < 1e-5
    assert student_t_cdf(0.0, 7) == 0.5
    assert abs(student_t_cdf(1.0, 5) + student_t_cdf(-1.0, 5) - 1.0) < 1e-12


def test_benjamini_hochberg_step_up_and_nan():
    p = np.array([0.001, 0.02, 0.03, 0.5, np.nan])
    assert benjamini_hochberg(p, 0.10).tolist() == [True, True, True, False, False]
    # 0.06 misses its rank-2 threshold (0.10*2/4 = 0.05), so only the first rank is a discovery
    assert benjamini_hochberg(np.array([0.01, 0.06, 0.9, 0.95]), 0.10).tolist() == [True, False, False, False]


def test_welch_less_detects_only_clearly_worse_samples():
    rng = np.random.default_rng(1)
    reference = rng.normal(0.2, 1.0, 500)
    assert welch_less(rng.normal(-0.5, 1.0, 200), reference) < 0.01
    assert welch_less(rng.normal(0.2, 1.0, 40), reference) > 0.05
