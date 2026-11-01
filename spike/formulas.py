"""SixGates formula engine (spike): pure, versioned functions, no I/O.

Every function takes typed inputs (``Fact`` values carrying their fact ids)
and returns a ``Result`` with: value, the fact ids it used, formula id and
version, unit, status and flags. Nothing is estimated: a missing input gives
``status="missing_input"``; a division that the method forbids (non-positive
tangible capital, non-positive owner earnings) gives ``status="flagged"`` with
the reason, never a number.

Sources: Berkshire letters 1983 (one-dollar test), 1986 (owner earnings), 1989
(tax deferral arithmetic), 1992 and 2000 (intrinsic value, Aesop), 2007
(See's, FlightSafety, great/good/gruesome); requirements_v0 section 5.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Iterable, NamedTuple

ENGINE_VERSION = "0.1.0"


class Fact(NamedTuple):
    """A number with its provenance handle (fact id or derived value id)."""

    value: float
    fact_id: str
    unit: str = "USD"


@dataclass(frozen=True)
class Result:
    """Value object returned by every formula."""

    formula_id: str
    version: str
    value: float | None
    unit: str
    status: str  # ok | missing_input | not_applicable | flagged | not_computed
    flags: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        """Plain dict for CSV or JSON export."""
        return {"value": self.value, "inputs": list(self.inputs), "formula_id": self.formula_id,
                "version": self.version, "unit": self.unit, "status": self.status,
                "flags": list(self.flags), "detail": dict(self.detail)}


@dataclass(frozen=True)
class Assumptions:
    """Fixed, visible assumptions (assumption_set v1). Any change creates a scenario."""

    name: str = "v1-default"
    version: str = "1"
    hurdle_rate: float = 0.10            # total discount hurdle (long bond yield plus premium, floor 10%)
    terminal_growth_low: float = 0.02
    terminal_growth_high: float = 0.03
    explicit_years: int = 10
    growth_cap_high: float = 0.10        # explicit-period growth never above this
    growth_cap_low: float = 0.05
    growth_low_fraction: float = 0.5     # low path uses half the historical CAGR
    margin_business: tuple[float, float] = (0.30, 0.50)
    margin_franchise: tuple[float, float] = (0.15, 0.25)
    cost_of_capital: float = 0.10        # for the 2007 categories (thresholds to validate)
    excellent_incremental_roic: float = 0.30
    good_spread_over_cost: float = 0.05
    low_capex_to_sales: float = 0.05
    tax_rate_clamp: tuple[float, float] = (0.0, 0.50)
    maintenance_capex_method: str = "min_capex_da"  # alternative: greenwald
    other_noncash_added_back: bool = False           # SBC treated as a real cost in v1

    def snapshot(self) -> dict:
        return dict(self.__dict__)


def _missing(formula_id: str, version: str, unit: str, names: Iterable[str]) -> Result:
    names = tuple(names)
    return Result(formula_id, version, None, unit, "missing_input", tuple(f"missing:{n}" for n in names), ())


def _ids(*facts: Fact | None) -> tuple[str, ...]:
    return tuple(f.fact_id for f in facts if f is not None)


def _same_unit(*facts: Fact) -> bool:
    return len({f.unit for f in facts}) == 1


# --------------------------------------------------------------------------- gate 3


def maintenance_capex(capex: Fact | None, d_and_a: Fact | None, method: str = "min_capex_da",
                      ppe_to_sales_avg: Fact | None = None, delta_revenue: Fact | None = None) -> Result:
    """Maintenance capex, default min(capex, D&A); alternative Greenwald.

    Greenwald: maintenance capex = capex minus growth capex, where growth capex
    is the average PP&E-to-sales ratio times the revenue increase (zero when
    revenue fell). Both variants are shown in the product; the choice is marked.
    """
    fid, ver = "maintenance_capex", "1.0.0"
    if capex is None or d_and_a is None:
        return _missing(fid, ver, "USD", [n for n, f in (("capex", capex), ("d_and_a", d_and_a)) if f is None])
    if method == "min_capex_da":
        value = min(capex.value, d_and_a.value)
        return Result(fid, ver, value, capex.unit, "ok", ("method:min_capex_da",), _ids(capex, d_and_a),
                      {"capex": capex.value, "d_and_a": d_and_a.value})
    if method == "greenwald":
        if ppe_to_sales_avg is None or delta_revenue is None:
            return _missing(fid, ver, capex.unit, ["ppe_to_sales_avg", "delta_revenue"])
        growth_capex = ppe_to_sales_avg.value * max(delta_revenue.value, 0.0)
        value = max(capex.value - growth_capex, 0.0)
        return Result(fid, ver, value, capex.unit, "ok", ("method:greenwald",),
                      _ids(capex, d_and_a, ppe_to_sales_avg, delta_revenue),
                      {"capex": capex.value, "growth_capex": growth_capex, "ppe_to_sales_avg": ppe_to_sales_avg.value,
                       "delta_revenue": delta_revenue.value})
    raise ValueError(f"unknown maintenance capex method {method}")


def owner_earnings(net_income: Fact | None, d_and_a: Fact | None, maint_capex: Result,
                   delta_working_capital: Fact | None = None, other_noncash: Fact | None = None) -> Result:
    """Owner earnings (1986): net income + D&A + other non-cash charges
    minus maintenance capex minus the increase in non-cash working capital."""
    fid, ver = "owner_earnings", "1.0.0"
    missing = [n for n, f in (("net_income", net_income), ("d_and_a", d_and_a)) if f is None]
    if missing or maint_capex.value is None:
        return _missing(fid, ver, "USD", missing + ([] if maint_capex.value is not None else ["maintenance_capex"]))
    flags = [f"maint_capex:{maint_capex.flags[0].split(':')[1]}" if maint_capex.flags else "maint_capex"]
    value = net_income.value + d_and_a.value - maint_capex.value
    detail = {"net_income": net_income.value, "d_and_a": d_and_a.value, "maintenance_capex": maint_capex.value}
    if other_noncash is not None:
        value += other_noncash.value
        detail["other_noncash"] = other_noncash.value
    else:
        flags.append("other_noncash:not_added_back")
    if delta_working_capital is not None:
        value -= delta_working_capital.value
        detail["delta_working_capital"] = delta_working_capital.value
    else:
        flags.append("delta_working_capital:missing_not_subtracted")
    return Result(fid, ver, value, net_income.unit, "ok", tuple(flags),
                  _ids(net_income, d_and_a, other_noncash, delta_working_capital) + maint_capex.inputs, detail)


def non_cash_working_capital(current_assets: Fact | None, cash: Fact | None, st_investments: Fact | None,
                             current_liabilities: Fact | None, st_borrowings: Fact | None,
                             ltd_current: Fact | None) -> Result:
    """(current assets minus cash and short-term investments) minus
    (current liabilities minus short-term borrowings and current maturities)."""
    fid, ver = "non_cash_working_capital", "1.0.0"
    missing = [n for n, f in (("current_assets", current_assets), ("cash", cash),
                              ("current_liabilities", current_liabilities)) if f is None]
    if missing:
        return _missing(fid, ver, "USD", missing)
    flags = []
    sti = st_investments.value if st_investments else 0.0
    stb = st_borrowings.value if st_borrowings else 0.0
    ltc = ltd_current.value if ltd_current else 0.0
    for name, f in (("st_investments", st_investments), ("st_borrowings", st_borrowings), ("ltd_current", ltd_current)):
        if f is None:
            flags.append(f"{name}:absent_treated_as_not_reported")
    value = (current_assets.value - cash.value - sti) - (current_liabilities.value - stb - ltc)
    return Result(fid, ver, value, current_assets.unit, "ok", tuple(flags),
                  _ids(current_assets, cash, st_investments, current_liabilities, st_borrowings, ltd_current),
                  {"current_assets": current_assets.value, "cash": cash.value, "st_investments": sti,
                   "current_liabilities": current_liabilities.value, "st_borrowings": stb, "ltd_current": ltc})


def tangible_invested_capital(ncwc: Result, ppe_net: Fact | None, other_operating_assets: Fact | None = None) -> Result:
    """Net working capital + net PP&E + other operating assets, excess cash excluded
    (all cash is treated as excess in v1, an explicit assumption). Goodwill and
    acquired intangibles are excluded; see ``capital_on_price_paid`` for the variant."""
    fid, ver = "tangible_invested_capital", "1.0.0"
    if ncwc.value is None or ppe_net is None:
        return _missing(fid, ver, "USD", (["ncwc"] if ncwc.value is None else []) + (["ppe_net"] if ppe_net is None else []))
    value = ncwc.value + ppe_net.value + (other_operating_assets.value if other_operating_assets else 0.0)
    flags = list(ncwc.flags) + ([] if other_operating_assets else ["other_operating_assets:not_included"])
    status = "ok"
    if value <= 0:
        flags.append("non_positive_tangible_capital")
        status = "flagged"
    return Result(fid, ver, value, ppe_net.unit, status, tuple(flags), ncwc.inputs + _ids(ppe_net, other_operating_assets),
                  {"ncwc": ncwc.value, "ppe_net": ppe_net.value})


def capital_on_price_paid(tangible_capital: Result, goodwill: Fact | None, intangibles: Fact | None) -> Result:
    """Invested capital including goodwill and acquired intangibles (the 'on the price paid' view)."""
    fid, ver = "capital_on_price_paid", "1.0.0"
    if tangible_capital.value is None or goodwill is None or intangibles is None:
        return _missing(fid, ver, "USD", [n for n, v in (("tangible_capital", tangible_capital.value),
                                                           ("goodwill", goodwill), ("intangibles", intangibles)) if v is None])
    value = tangible_capital.value + goodwill.value + intangibles.value
    return Result(fid, ver, value, goodwill.unit, "ok", (), tangible_capital.inputs + _ids(goodwill, intangibles),
                  {"tangible_capital": tangible_capital.value, "goodwill": goodwill.value, "intangibles": intangibles.value})


def effective_tax_rate(income_tax: Fact | None, pretax_income: Fact | None, a: Assumptions = Assumptions()) -> Result:
    """income tax / pre-tax income, clamped to the assumption range with a flag."""
    fid, ver = "effective_tax_rate", "1.0.0"
    if income_tax is None or pretax_income is None:
        return _missing(fid, ver, "ratio", [n for n, f in (("income_tax", income_tax), ("pretax_income", pretax_income)) if f is None])
    if pretax_income.value <= 0:
        return Result(fid, ver, None, "ratio", "flagged", ("non_positive_pretax_income",), _ids(income_tax, pretax_income))
    raw = income_tax.value / pretax_income.value
    lo, hi = a.tax_rate_clamp
    flags = []
    value = raw
    if raw < lo or raw > hi:
        value = min(max(raw, lo), hi)
        flags.append(f"tax_rate_clamped:{raw:.3f}->{value:.3f}")
    return Result(fid, ver, value, "ratio", "ok", tuple(flags), _ids(income_tax, pretax_income), {"raw_rate": raw})


def nopat(operating_income: Fact | None, tax_rate: Result) -> Result:
    """Operating income times (1 minus the effective tax rate)."""
    fid, ver = "nopat", "1.0.0"
    if operating_income is None or tax_rate.value is None:
        return _missing(fid, ver, "USD", (["operating_income"] if operating_income is None else []) + (["tax_rate"] if tax_rate.value is None else []))
    value = operating_income.value * (1.0 - tax_rate.value)
    return Result(fid, ver, value, operating_income.unit, "ok", tax_rate.flags, _ids(operating_income) + tax_rate.inputs,
                  {"operating_income": operating_income.value, "tax_rate": tax_rate.value})


def return_on_tangible_capital(profit: Fact | None, capital: Fact | None) -> Result:
    """profit / tangible capital; never divides by a non-positive capital (flag instead).

    Used for See's 1972 (pre-tax 5 on 8) and 2007 (82 on 40) and for the yearly
    tangible ROIC with NOPAT over beginning-of-year tangible capital.
    """
    fid, ver = "return_on_tangible_capital", "1.0.0"
    if profit is None or capital is None:
        return _missing(fid, ver, "ratio", [n for n, f in (("profit", profit), ("capital", capital)) if f is None])
    if not _same_unit(profit, capital):
        return Result(fid, ver, None, "ratio", "flagged", ("unit_mismatch",), _ids(profit, capital))
    if capital.value <= 0:
        return Result(fid, ver, None, "ratio", "flagged", ("non_positive_tangible_capital",), _ids(profit, capital),
                      {"profit": profit.value, "capital": capital.value})
    return Result(fid, ver, profit.value / capital.value, "ratio", "ok", (), _ids(profit, capital),
                  {"profit": profit.value, "capital": capital.value})


def incremental_return(profit_end: Fact | None, profit_start: Fact | None, capital_end: Fact | None,
                       capital_start: Fact | None) -> Result:
    """(profit_end minus profit_start) / (capital_end minus capital_start), 2007 letter.

    FlightSafety: 159 extra pre-tax on 509 extra capital. When capital did not
    grow the ratio has no meaning: the result is flagged and both deltas shown.
    """
    fid, ver = "incremental_return", "1.0.0"
    missing = [n for n, f in (("profit_end", profit_end), ("profit_start", profit_start),
                              ("capital_end", capital_end), ("capital_start", capital_start)) if f is None]
    if missing:
        return _missing(fid, ver, "ratio", missing)
    d_profit = profit_end.value - profit_start.value
    d_capital = capital_end.value - capital_start.value
    ids = _ids(profit_end, profit_start, capital_end, capital_start)
    detail = {"delta_profit": d_profit, "delta_capital": d_capital}
    if d_capital <= 0:
        return Result(fid, ver, None, "ratio", "flagged", ("capital_did_not_grow",), ids, detail)
    return Result(fid, ver, d_profit / d_capital, "ratio", "ok", (), ids, detail)


def growth_identity(reinvestment_rate: Result, roic: Result, observed_cagr: Result) -> Result:
    """implied growth = reinvestment rate x ROIC, shown next to the observed CAGR (1992, 2000)."""
    fid, ver = "growth_identity", "1.0.0"
    if reinvestment_rate.value is None or roic.value is None:
        return _missing(fid, ver, "ratio", ["reinvestment_rate"] if reinvestment_rate.value is None else ["roic"])
    implied = reinvestment_rate.value * roic.value
    detail = {"reinvestment_rate": reinvestment_rate.value, "roic": roic.value, "observed_cagr": observed_cagr.value}
    flags = () if observed_cagr.value is not None else ("observed_cagr:missing",)
    return Result(fid, ver, implied, "ratio", "ok", flags, reinvestment_rate.inputs + roic.inputs + observed_cagr.inputs, detail)


def ratio(formula_id: str, numerator: Fact | Result | None, denominator: Fact | Result | None,
          deny_non_positive_denominator: bool = True) -> Result:
    """Generic guarded ratio used for capex/sales, cash conversion, net debt/OE, EBIT/interest."""
    ver = "1.0.0"
    if numerator is None or denominator is None or getattr(numerator, "value", None) is None or getattr(denominator, "value", None) is None:
        return _missing(formula_id, ver, "ratio", ["numerator"] if numerator is None or numerator.value is None else ["denominator"])
    num, den = numerator.value, denominator.value
    ids = tuple(numerator.inputs if isinstance(numerator, Result) else (numerator.fact_id,)) + \
        tuple(denominator.inputs if isinstance(denominator, Result) else (denominator.fact_id,))
    if deny_non_positive_denominator and den <= 0:
        return Result(formula_id, ver, None, "ratio", "flagged", ("non_positive_denominator",), ids, {"numerator": num, "denominator": den})
    return Result(formula_id, ver, num / den, "ratio", "ok", (), ids, {"numerator": num, "denominator": den})


def cagr(start: Fact | None, end: Fact | None, years: int) -> Result:
    """Compound annual growth rate between two positive values."""
    fid, ver = "cagr", "1.0.0"
    if start is None or end is None:
        return _missing(fid, ver, "ratio", ["start"] if start is None else ["end"])
    if start.value <= 0 or end.value <= 0:
        return Result(fid, ver, None, "ratio", "flagged", ("non_positive_endpoint",), _ids(start, end))
    return Result(fid, ver, (end.value / start.value) ** (1.0 / years) - 1.0, "ratio", "ok", (), _ids(start, end), {"years": years})


def predictability(series: list[Fact]) -> Result:
    """Coefficient of variation of owner earnings and number of loss years over the window."""
    fid, ver = "predictability", "1.0.0"
    if len(series) < 2:
        return _missing(fid, ver, "ratio", ["series"])
    values = [f.value for f in series]
    mean = statistics.fmean(values)
    loss_years = sum(1 for v in values if v <= 0)
    if mean <= 0:
        return Result(fid, ver, None, "ratio", "flagged", ("non_positive_mean",), tuple(f.fact_id for f in series), {"loss_years": loss_years})
    cv = statistics.pstdev(values) / mean
    return Result(fid, ver, cv, "ratio", "ok", (), tuple(f.fact_id for f in series), {"loss_years": loss_years, "n": len(values)})


def ten_year_rule(fiscal_years_complete: list[int], required: int = 10) -> Result:
    """'date insuficiente' unless at least ``required`` consecutive fiscal years have every needed concept."""
    fid, ver = "ten_year_rule", "1.0.0"
    years = sorted(set(fiscal_years_complete))
    best = run = 0
    for i, y in enumerate(years):
        run = run + 1 if i and years[i - 1] == y - 1 else 1
        best = max(best, run)
    detail = {"complete_years": years, "longest_consecutive_run": best, "required": required}
    if best >= required:
        return Result(fid, ver, float(best), "years", "ok", (), (), detail)
    return Result(fid, ver, float(best), "years", "flagged", ("insufficient_data",), (), detail)


def business_category(incremental_roic: Result, capex_to_sales: Result, a: Assumptions = Assumptions()) -> Result:
    """2007 letter categories with explicit thresholds (to validate on the golden set):
    excellent: incremental ROIC above 30% and low capex/sales; good: between cost of
    capital + 5 points and 30%; gruesome: below the cost of capital with growing capital."""
    fid, ver = "business_category_2007", "1.0.0"
    if incremental_roic.value is None:
        if "capital_did_not_grow" in incremental_roic.flags:
            # See's pattern: profit grew while the capital employed did not (2007 letter);
            # profit that fell while capital was released is simply not classifiable here
            d_profit = incremental_roic.detail.get("delta_profit", 0.0)
            if d_profit > 0:
                return Result(fid, ver, None, "category", "ok", ("capital_did_not_grow", "thresholds_to_validate"), incremental_roic.inputs,
                              {"label": "excelent (profit în creștere fără capital suplimentar)", **incremental_roic.detail})
            return Result(fid, ver, None, "category", "not_applicable", ("capital_did_not_grow",), incremental_roic.inputs,
                          {"label": "n/a (profit în scădere, capital eliberat)", **incremental_roic.detail})
        return _missing(fid, ver, "category", ["incremental_roic"])
    r = incremental_roic.value
    cts = capex_to_sales.value
    flags = ["thresholds_to_validate"]
    if r > a.excellent_incremental_roic and cts is not None and cts < a.low_capex_to_sales:
        label = "excelent"
    elif r >= a.cost_of_capital + a.good_spread_over_cost:
        # FlightSafety (2007): 31% on incremental capital but capital-hungry, "good" not "great"
        label = "bun"
        if cts is None:
            flags.append("capex_to_sales:missing")
    elif r < a.cost_of_capital:
        label = "groaznic"
    else:
        label = "între bun și groaznic (sub costul capitalului + 5 puncte)"
    return Result(fid, ver, r, "category", "ok", tuple(flags), incremental_roic.inputs + capex_to_sales.inputs,
                  {"label": label, "incremental_roic": r, "capex_to_sales": cts})


# --------------------------------------------------------------------------- gate 5


def dcf_value(oe0: float, growth: float, rate: float, terminal_growth: float, years: int) -> float:
    """Present value of owner earnings growing at ``growth`` for ``years`` then at
    ``terminal_growth`` forever; the terminal value is discounted to today."""
    if rate <= terminal_growth:
        raise ValueError("discount rate must exceed terminal growth")
    pv = 0.0
    oe = oe0
    for t in range(1, years + 1):
        oe = oe * (1.0 + growth)
        pv += oe / (1.0 + rate) ** t
    terminal = oe * (1.0 + terminal_growth) / (rate - terminal_growth)
    return pv + terminal / (1.0 + rate) ** years


def intrinsic_value_range(oe: Result, historical_cagr: Result, a: Assumptions = Assumptions()) -> Result:
    """Intrinsic value as a range (1992, 2000): low path (half the historical
    owner-earnings CAGR, capped, terminal 2%) and high path (historical CAGR,
    capped, terminal 3%); discount rate = the fixed hurdle. No growth is assumed
    when the historical CAGR is negative or unknown."""
    fid, ver = "intrinsic_value_range", "1.0.0"
    if oe.value is None:
        return _missing(fid, ver, "USD", ["owner_earnings"])
    if oe.value <= 0:
        return Result(fid, ver, None, oe.unit, "flagged", ("non_positive_owner_earnings",), oe.inputs)
    flags = []
    if historical_cagr.value is None or historical_cagr.value < 0:
        g_low = g_high = 0.0
        flags.append("growth:none_assumed")
    else:
        g_high = min(historical_cagr.value, a.growth_cap_high)
        g_low = min(historical_cagr.value * a.growth_low_fraction, a.growth_cap_low)
    low = dcf_value(oe.value, g_low, a.hurdle_rate, a.terminal_growth_low, a.explicit_years)
    high = dcf_value(oe.value, g_high, a.hurdle_rate, a.terminal_growth_high, a.explicit_years)
    detail = {"low": low, "high": high, "g_low": g_low, "g_high": g_high, "rate": a.hurdle_rate,
              "terminal_low": a.terminal_growth_low, "terminal_high": a.terminal_growth_high,
              "years": a.explicit_years, "assumption_set": f"{a.name}/{a.version}"}
    return Result(fid, ver, low, oe.unit, "ok", tuple(flags), oe.inputs + historical_cagr.inputs, detail)


def reverse_dcf(market_value: Fact | None, oe: Result, a: Assumptions = Assumptions()) -> Result:
    """Growth rate over the explicit period that makes the DCF equal the market value (2000)."""
    fid, ver = "reverse_dcf", "1.0.0"
    if market_value is None:
        return Result(fid, ver, None, "ratio", "not_computed", ("no_price_source",), oe.inputs)
    if oe.value is None or oe.value <= 0:
        return Result(fid, ver, None, "ratio", "flagged" if oe.value is not None else "missing_input", ("non_positive_owner_earnings",), oe.inputs)
    g_term = (a.terminal_growth_low + a.terminal_growth_high) / 2.0
    lo, hi = -0.5, 0.5
    f = lambda g: dcf_value(oe.value, g, a.hurdle_rate, g_term, a.explicit_years) - market_value.value
    if f(lo) > 0 or f(hi) < 0:
        return Result(fid, ver, None, "ratio", "flagged", ("implied_growth_out_of_range",), oe.inputs + _ids(market_value))
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return Result(fid, ver, (lo + hi) / 2.0, "ratio", "ok", (), oe.inputs + _ids(market_value),
                  {"market_value": market_value.value, "terminal_growth": g_term, "rate": a.hurdle_rate})


def margin_of_safety(price: Fact | None, intrinsic_value: Result) -> Result:
    """1 minus price / intrinsic value (low end of the range)."""
    fid, ver = "margin_of_safety", "1.0.0"
    if price is None:
        return Result(fid, ver, None, "ratio", "not_computed", ("no_price_source",), intrinsic_value.inputs)
    if intrinsic_value.value is None or intrinsic_value.value <= 0:
        return _missing(fid, ver, "ratio", ["intrinsic_value"])
    return Result(fid, ver, 1.0 - price.value / intrinsic_value.value, "ratio", "ok", (), intrinsic_value.inputs + _ids(price),
                  {"price": price.value, "intrinsic_value": intrinsic_value.value})


def price_i_would_pay(intrinsic_value: Result, franchise: bool, a: Assumptions = Assumptions()) -> Result:
    """intrinsic value x (1 minus required margin); margin 30 to 50% for a business,
    15 to 25% for a franchise; returned as a range on the low intrinsic value."""
    fid, ver = "price_i_would_pay", "1.0.0"
    if intrinsic_value.value is None:
        return _missing(fid, ver, "USD", ["intrinsic_value"])
    lo_m, hi_m = a.margin_franchise if franchise else a.margin_business
    low, high = intrinsic_value.value * (1 - hi_m), intrinsic_value.value * (1 - lo_m)
    return Result(fid, ver, low, intrinsic_value.unit, "ok", ("franchise" if franchise else "business",), intrinsic_value.inputs,
                  {"low": low, "high": high, "margin_low": lo_m, "margin_high": hi_m})


def one_dollar_test(market_cap_end: Fact | None, market_cap_start: Fact | None, retained_earnings: Fact | None) -> Result:
    """Change in market value over the window divided by earnings retained (1983); passes at 1 or above."""
    fid, ver = "one_dollar_test", "1.0.0"
    if market_cap_end is None or market_cap_start is None:
        return Result(fid, ver, None, "ratio", "not_computed", ("no_price_source",), _ids(retained_earnings))
    if retained_earnings is None:
        return _missing(fid, ver, "ratio", ["retained_earnings"])
    if retained_earnings.value <= 0:
        return Result(fid, ver, None, "ratio", "flagged", ("nothing_retained",), _ids(market_cap_end, market_cap_start, retained_earnings))
    return Result(fid, ver, (market_cap_end.value - market_cap_start.value) / retained_earnings.value, "ratio", "ok", (),
                  _ids(market_cap_end, market_cap_start, retained_earnings))


# --------------------------------------------------------------------------- gate 6 and letters arithmetic


def tax_deferral(principal: float, doublings: int, tax_rate: float) -> Result:
    """1989 letter: one dollar doubling ``doublings`` times taxed once at the end
    versus taxed at every doubling (34% then: about 692,000 vs about 25,000)."""
    fid, ver = "tax_deferral_1989", "1.0.0"
    gross = principal * 2 ** doublings
    end_taxed = principal + (gross - principal) * (1 - tax_rate)
    annually_taxed = principal * (1 + (2 - 1) * (1 - tax_rate)) ** doublings
    return Result(fid, ver, end_taxed, "USD", "ok", (), (), {"annually_taxed": annually_taxed, "gross": gross, "tax_rate": tax_rate})


def switch_with_tax(tax_rate: float, gain_fraction: float, r_current: float, r_alternative: float, years: int) -> Result:
    """Hold if (1 minus t x g)(1 + r2)^n < (1 + r1)^n, where g is the unrealised gain
    as a fraction of current value (requirements_v0, after the 1989 arithmetic)."""
    fid, ver = "switch_with_tax", "1.0.0"
    after_switch = (1 - tax_rate * gain_fraction) * (1 + r_alternative) ** years
    hold = (1 + r_current) ** years
    detail = {"after_switch": after_switch, "hold": hold, "decision": "hold" if after_switch < hold else "switch_is_better_after_tax"}
    return Result(fid, ver, after_switch / hold, "ratio", "ok", (), (), detail)


def kelly_fraction(p: float, b: float, fraction: float = 0.25, cap: float = 0.40) -> Result:
    """f = (p minus (1 minus p)/b) x fraction, capped (1966 partnership, Munger 1994)."""
    fid, ver = "kelly_fraction", "1.0.0"
    raw = p - (1 - p) / b
    value = max(0.0, min(raw * fraction, cap))
    return Result(fid, ver, value, "ratio", "ok", (), (), {"raw_kelly": raw, "fraction": fraction, "cap": cap})
