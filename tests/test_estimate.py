"""Regressions, the decomposition, the standard errors, and how close the reproduction came. No microdata needed."""
import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

import estimate
from data import OUTPUT


@pytest.fixture
def people():
    """Made-up records with a known gap and differences in characteristics."""
    rng = np.random.default_rng(1)
    n = 4000
    indigenous = rng.random(n) < 0.3
    education = rng.choice([1, 2, 9], n, p=[.3, .4, .3])
    education = np.where(indigenous & (rng.random(n) < .4), 1, education)
    d = pd.DataFrame({"indigenous": indigenous, "ancestry_only": False, "education": education,
                      "agegrp": rng.choice([9, 10, 11], n), "kol": rng.choice([1, 3], n), "marital": rng.choice(["never", "couple"], n),
                      "area": rng.choice([535, 999], n), "hhsize": rng.choice([1, 2, 3], n), "weight": rng.uniform(30, 40, n)})
    d["y"] = 10 + .4 * (education == 9) - .2 * (education == 1) - .3 * indigenous + rng.normal(0, .2, n)
    for i in range(8):
        d[f"wt{i + 1}"] = np.where(rng.integers(0, 8, n) == i, 8 * d.weight, 0)
    return d


def test_weighted_least_squares_matches_statsmodels():
    rng = np.random.default_rng(2)
    x = sm.add_constant(rng.normal(size=(300, 2)))
    y, w = x @ [1, 2, 3] + rng.normal(size=300), rng.uniform(1, 5, 300)
    assert estimate.wls(y, x, w) == pytest.approx(sm.WLS(y, x, weights=w).fit().params)


def test_robust_errors_match_statsmodels_hc1():
    rng = np.random.default_rng(3)
    x = sm.add_constant(rng.normal(size=(300, 2)))
    y = x @ [1, 2, 3] + rng.normal(size=300) * (1 + np.abs(x[:, 1]))
    beta, se, r2 = estimate.hc1(y, x)
    fit = sm.OLS(y, x).fit(cov_type="HC1")
    assert beta == pytest.approx(fit.params)
    assert se == pytest.approx(fit.bse)
    assert r2 == pytest.approx(fit.rsquared)


def test_decomposition_parts_add_up_to_the_raw_gap(people):
    e = estimate.gap_function(people)(people, people.weight.to_numpy())
    assert e.explained + e.unexplained == pytest.approx(e.raw)
    assert sum(e[family] for family in estimate.CONTROLS) == pytest.approx(e.explained)


def test_decomposition_finds_the_gap_it_was_given(people):
    e = estimate.gap_function(people)(people, people.weight.to_numpy())
    assert e.adjusted == pytest.approx(-.3, abs=.02)
    assert e.unexplained == pytest.approx(-.3, abs=.02)
    assert e.education < -.02  # the group was given less education
    assert abs(e.age) < .01  # and the same age


def test_explained_part_does_not_depend_on_the_left_out_category(people):
    base = estimate.gap_function(people)(people, people.weight.to_numpy())
    other = people.assign(education=people.education.map({1: 90, 2: 2, 9: 9}))  # sorts differently as text
    assert estimate.gap_function(other)(other, other.weight.to_numpy()).education == pytest.approx(base.education)


def test_replicate_standard_error_follows_the_user_guide_formula():
    d = pd.DataFrame({"weight": [1.0, 1, 1, 1, 1, 1, 1, 1], **{f"wt{i + 1}": np.eye(8)[i] for i in range(8)}})
    values = np.arange(8.0)

    def mean_of_group(_, w):
        return pd.Series({"m": (w * values).sum() / w.sum()})
    point, se = estimate.replicate_se(mean_of_group, d, 2006)
    assert point.m == pytest.approx(3.5)
    assert se.m == pytest.approx(np.sqrt(((values - 3.5) ** 2).sum() / 56))


def test_cohort_ages_five_years_at_each_census():
    for earlier, later in zip(estimate.COHORT.values(), list(estimate.COHORT.values())[1:]):
        assert [a + 1 for a in earlier] == list(later)


def test_identity_bound_uses_the_net_addition():
    cohorts = pd.DataFrame({"year": [2006, 2021, 2006, 2021], "group": ["Indigenous identity or registered"] * 2 + ["Comparison group"] * 2,
                            "count": [100.0, 180, 1000, 900]})
    same = pd.DataFrame({"year": [2006, 2021], "adjusted": [-.2, -.1]})
    t = estimate.identity_bound(cohorts, same).set_index("year")
    assert t.net_added_share[2006] == pytest.approx(0)
    assert t.net_added_share[2021] == pytest.approx(.5)  # 90 expected of 180
    assert t.gap_if_added_at_comparison_level[2021] == pytest.approx(-.2)


def test_changes_add_standard_errors_in_quadrature():
    rows = [{"year": y, "outcome": "wages", "sex": "men", **{m: v for m in ("raw", "adjusted", "unexplained")},
             **{f"{m}_se": .03 if y == 2006 else .04 for m in ("raw", "adjusted", "unexplained")}}
            for y, v in ((2006, -.5), (2016, -.4), (2021, -.3))]
    t = estimate.changes(pd.DataFrame(rows))
    row = t[(t.to == 2021) & (t.measure == "raw")].iloc[0]
    assert row.change == pytest.approx(.2)
    assert row.se == pytest.approx(.05)


@pytest.mark.skipif(not (OUTPUT / "reproduction_2006.csv").exists(), reason="run estimate.py first")
def test_reproduction_stays_close_to_the_coursework():
    t = pd.read_csv(OUTPUT / "reproduction_2006.csv")
    assert len(t) == 32
    assert t.difference_in_se.abs().max() < .5
    assert (t.n / t.published_n - 1).abs().max() < .015
    assert (np.sign(t.coefficient) == np.sign(t.published)).all()
