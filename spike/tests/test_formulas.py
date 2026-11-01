"""Known-result tests for the formula engine.

Expected values come from the Berkshire letters as listed in recipe.md:
See's 1972 and 2007 (2007 letter), FlightSafety (2007 letter), the 1989 tax
deferral arithmetic, plus the rules of requirements_v0 section 5.
"""

import math

import pytest

import formulas as F

M = 1_000_000.0


def fact(value: float, fid: str = "f", unit: str = "USD") -> F.Fact:
    return F.Fact(value, fid, unit)


# ---------------------------------------------------------------- See's and FlightSafety (2007 letter)


def test_sees_1972_return_on_tangible_capital():
    # 1972: about 8m of net tangible assets, pre-tax earnings "less than 5m" (5m used, upper bound)
    r = F.return_on_tangible_capital(fact(5 * M, "sees_1972_pretax"), fact(8 * M, "sees_1972_capital"))
    assert r.status == "ok"
    assert r.value == pytest.approx(0.625, rel=1e-9)
    assert r.inputs == ("sees_1972_pretax", "sees_1972_capital")
    assert r.formula_id == "return_on_tangible_capital" and r.version == "1.0.0"


def test_sees_2007_return_on_tangible_capital():
    # 2007: 82m pre-tax on 40m of capital
    r = F.return_on_tangible_capital(fact(82 * M), fact(40 * M))
    assert r.value == pytest.approx(2.05, rel=1e-9)


def test_sees_incremental_return_1972_to_2007():
    # 77m extra pre-tax on 32m extra capital (only 32m reinvested in 35 years)
    r = F.incremental_return(fact(82 * M), fact(5 * M), fact(40 * M), fact(8 * M))
    assert r.status == "ok"
    assert r.value == pytest.approx(77 / 32, rel=1e-9)
    assert r.detail["delta_capital"] == pytest.approx(32 * M)


def test_flightsafety_incremental_return():
    # 509m extra capital for 159m extra pre-tax: "good" category
    r = F.incremental_return(fact(159 * M + 100 * M), fact(100 * M), fact(509 * M + 50 * M), fact(50 * M))
    assert r.value == pytest.approx(159 / 509, rel=1e-9)
    assert r.value == pytest.approx(0.3124, abs=5e-4)


# ---------------------------------------------------------------- 1989 tax arithmetic and switch inequality


def test_tax_deferral_1989_arithmetic():
    r = F.tax_deferral(1.0, 20, 0.34)
    end_taxed_exact = 1 + (2 ** 20 - 1) * 0.66          # 692,060.5
    annually_taxed_exact = 1.66 ** 20                      # about 25,251
    assert r.value == pytest.approx(end_taxed_exact, rel=1e-12)
    assert r.detail["annually_taxed"] == pytest.approx(annually_taxed_exact, rel=1e-12)
    # the letter's rounded figures: about 692,000 and about 25,000
    assert r.value == pytest.approx(692_000, rel=0.005)
    assert r.detail["annually_taxed"] == pytest.approx(25_000, rel=0.02)


def test_switch_with_tax_inequality_depends_on_horizon():
    # 34% tax on a 50% embedded gain, 10% held vs 12% alternative
    ten = F.switch_with_tax(0.34, 0.5, 0.10, 0.12, 10)
    twenty = F.switch_with_tax(0.34, 0.5, 0.10, 0.12, 20)
    assert ten.detail["after_switch"] == pytest.approx(0.83 * 1.12 ** 10)
    assert ten.detail["decision"] == "hold"                       # 2.578 < 2.594
    assert twenty.detail["decision"] == "switch_is_better_after_tax"  # 8.006 > 6.727


# ---------------------------------------------------------------- rules from requirements_v0 section 5


def test_ten_year_rule_nine_years_is_insufficient():
    r = F.ten_year_rule(list(range(2016, 2025)))  # 9 fiscal years
    assert r.status == "flagged" and "insufficient_data" in r.flags
    assert r.detail["longest_consecutive_run"] == 9


def test_ten_year_rule_ten_consecutive_years_pass_but_a_gap_does_not():
    assert F.ten_year_rule(list(range(2015, 2025))).status == "ok"
    with_gap = [2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]  # 2018 missing
    assert F.ten_year_rule(with_gap).status == "flagged"


def test_non_positive_tangible_capital_is_flagged_not_divided():
    r = F.return_on_tangible_capital(fact(1_000 * M), fact(-900 * M))
    assert r.status == "flagged" and r.value is None
    assert "non_positive_tangible_capital" in r.flags
    ncwc = F.non_cash_working_capital(fact(1_000 * M), fact(2_000 * M), fact(0.0), fact(2_500 * M), None, None)
    tic = F.tangible_invested_capital(ncwc, fact(300 * M))
    assert tic.value == pytest.approx(-3_200 * M) and tic.status == "flagged"


def test_incremental_return_flagged_when_capital_shrinks():
    r = F.incremental_return(fact(200 * M), fact(100 * M), fact(80 * M), fact(100 * M))
    assert r.status == "flagged" and r.value is None and "capital_did_not_grow" in r.flags


def test_unit_mismatch_is_refused():
    r = F.return_on_tangible_capital(fact(5 * M, unit="USD"), fact(8 * M, unit="EUR"))
    assert r.status == "flagged" and "unit_mismatch" in r.flags


def test_maintenance_capex_default_and_greenwald():
    default = F.maintenance_capex(fact(12_715 * M, "capex"), fact(11_698 * M, "da"))
    assert default.value == pytest.approx(11_698 * M) and "method:min_capex_da" in default.flags
    gw = F.maintenance_capex(fact(1_000 * M), fact(800 * M), "greenwald", fact(0.20, "ratio", "ratio"), fact(2_000 * M))
    assert gw.value == pytest.approx(600 * M)  # 1,000 minus 0.20 x 2,000 of growth capex
    gw_decline = F.maintenance_capex(fact(1_000 * M), fact(800 * M), "greenwald", fact(0.20, "ratio", "ratio"), fact(-500 * M))
    assert gw_decline.value == pytest.approx(1_000 * M)  # no growth capex when revenue fell


def test_owner_earnings_arithmetic_and_flags():
    mc = F.maintenance_capex(fact(100 * M), fact(80 * M))
    oe = F.owner_earnings(fact(500 * M, "ni"), fact(80 * M, "da"), mc, delta_working_capital=fact(20 * M, "dwc"))
    assert oe.value == pytest.approx((500 + 80 - 80 - 20) * M)
    assert "other_noncash:not_added_back" in oe.flags
    assert set(oe.inputs) >= {"ni", "da", "dwc"}
    missing = F.owner_earnings(None, fact(80 * M), mc)
    assert missing.status == "missing_input" and missing.value is None


def test_effective_tax_rate_clamp_and_nopat():
    tr = F.effective_tax_rate(fact(300 * M), fact(1_000 * M))
    assert tr.value == pytest.approx(0.30)
    clamped = F.effective_tax_rate(fact(900 * M), fact(1_000 * M))
    assert clamped.value == pytest.approx(0.50) and clamped.flags
    n = F.nopat(fact(1_000 * M), tr)
    assert n.value == pytest.approx(700 * M)
    assert F.effective_tax_rate(fact(10 * M), fact(-5 * M)).status == "flagged"


def test_dcf_is_monotonic_in_the_discount_rate_and_growth():
    v8 = F.dcf_value(100.0, 0.05, 0.08, 0.02, 10)
    v10 = F.dcf_value(100.0, 0.05, 0.10, 0.02, 10)
    v12 = F.dcf_value(100.0, 0.05, 0.12, 0.02, 10)
    assert v8 > v10 > v12
    assert F.dcf_value(100.0, 0.08, 0.10, 0.02, 10) > v10
    with pytest.raises(ValueError):
        F.dcf_value(100.0, 0.05, 0.02, 0.03, 10)


def test_dcf_closed_form_check():
    # zero growth, zero terminal growth: annuity of 10 payments plus perpetuity discounted
    r = 0.10
    annuity = 100.0 * (1 - (1 + r) ** -10) / r
    perpetuity_pv = (100.0 / r) / (1 + r) ** 10
    assert F.dcf_value(100.0, 0.0, r, 0.0, 10) == pytest.approx(annuity + perpetuity_pv, rel=1e-12)


def test_intrinsic_value_range_low_below_high_and_no_growth_when_cagr_negative():
    oe = F.Result("owner_earnings", "1.0.0", 1_000 * M, "USD", "ok", (), ("oe",))
    cagr = F.Result("cagr", "1.0.0", 0.08, "ratio", "ok", (), ("c",))
    iv = F.intrinsic_value_range(oe, cagr)
    assert iv.status == "ok" and iv.detail["low"] < iv.detail["high"]
    assert iv.detail["g_high"] == pytest.approx(0.08) and iv.detail["g_low"] == pytest.approx(0.04)
    neg = F.intrinsic_value_range(oe, F.Result("cagr", "1.0.0", -0.03, "ratio", "ok", (), ("c",)))
    assert neg.detail["g_low"] == 0.0 == neg.detail["g_high"] and "growth:none_assumed" in neg.flags
    loss = F.intrinsic_value_range(F.Result("owner_earnings", "1.0.0", -5 * M, "USD", "ok", (), ("oe",)), cagr)
    assert loss.status == "flagged"


def test_reverse_dcf_recovers_the_growth_rate():
    a = F.Assumptions()
    oe = F.Result("owner_earnings", "1.0.0", 1_000 * M, "USD", "ok", (), ("oe",))
    g_term = (a.terminal_growth_low + a.terminal_growth_high) / 2
    market_value = F.dcf_value(1_000 * M, 0.05, a.hurdle_rate, g_term, a.explicit_years)
    r = F.reverse_dcf(fact(market_value, "mcap"), oe, a)
    assert r.value == pytest.approx(0.05, abs=1e-6)
    assert F.reverse_dcf(None, oe, a).status == "not_computed"


def test_margin_of_safety_and_price_i_would_pay():
    iv = F.Result("intrinsic_value_range", "1.0.0", 100.0, "USD", "ok", (), ("iv",))
    assert F.margin_of_safety(fact(70.0, "p"), iv).value == pytest.approx(0.30)
    biz = F.price_i_would_pay(iv, franchise=False)
    assert (biz.detail["low"], biz.detail["high"]) == pytest.approx((50.0, 70.0))
    fr = F.price_i_would_pay(iv, franchise=True)
    assert (fr.detail["low"], fr.detail["high"]) == pytest.approx((75.0, 85.0))
    assert F.margin_of_safety(None, iv).status == "not_computed"


def test_one_dollar_test_and_kelly():
    assert F.one_dollar_test(fact(300 * M), fact(100 * M), fact(150 * M)).value == pytest.approx(200 / 150)
    assert F.one_dollar_test(None, None, fact(150 * M)).status == "not_computed"
    k = F.kelly_fraction(0.6, 2.0, fraction=0.5, cap=0.40)
    assert k.detail["raw_kelly"] == pytest.approx(0.4) and k.value == pytest.approx(0.2)
    assert F.kelly_fraction(0.9, 10.0, fraction=0.5).value == 0.40  # cap at 40%


def test_business_category_thresholds():
    good = F.business_category(F.Result("incremental_return", "1.0.0", 159 / 509, "ratio", "ok", (), ()),
                               F.Result("capex_to_sales", "1.0.0", 0.08, "ratio", "ok", (), ()))
    assert good.detail["label"] == "bun"
    excellent = F.business_category(F.Result("incremental_return", "1.0.0", 77 / 32, "ratio", "ok", (), ()),
                                    F.Result("capex_to_sales", "1.0.0", 0.01, "ratio", "ok", (), ()))
    assert excellent.detail["label"] == "excelent"
    gruesome = F.business_category(F.Result("incremental_return", "1.0.0", 0.04, "ratio", "ok", (), ()),
                                   F.Result("capex_to_sales", "1.0.0", 0.15, "ratio", "ok", (), ()))
    assert gruesome.detail["label"] == "groaznic"
    # See's pattern: pre-tax profit up, capital employed flat or down (2007 letter)
    sees_like = F.incremental_return(fact(82 * M), fact(5 * M), fact(8 * M), fact(8 * M))
    cat = F.business_category(sees_like, F.Result("capex_to_sales", "1.0.0", 0.01, "ratio", "ok", (), ()))
    assert cat.status == "ok" and cat.detail["label"].startswith("excelent")
    worse = F.business_category(F.incremental_return(fact(50 * M), fact(80 * M), fact(8 * M), fact(10 * M)),
                                F.Result("capex_to_sales", "1.0.0", 0.01, "ratio", "ok", (), ()))
    assert worse.status == "not_applicable"


def test_result_exposes_version_and_round_trips_to_dict():
    r = F.ratio("capex_to_sales", fact(10.0, "a"), fact(100.0, "b"))
    d = r.as_dict()
    assert d["formula_id"] == "capex_to_sales" and d["version"] == "1.0.0"
    assert d["inputs"] == ["a", "b"] and d["value"] == pytest.approx(0.1)
    assert F.ENGINE_VERSION
