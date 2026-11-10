"""Regression tests for the SixGates screen, synthetic cases: one company per rule.

Every case below encodes a mistake the pipeline made once, or a rule of the framework that must not drift.
Run: python3 -m unittest discover -s tools/screen/tests   (or pytest -q tools/screen/tests)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import screen  # noqa: E402


# ---------- synthetic company builder ----------
def company(years, rev, ni, opinc=None, cfo=None, capex=None, da=None, sbc=None, interest=None, shares=None,
            equity=None, cash=None, debt_nc=None, debt_cur=None, pretax=None, tax=None, assets_cur=None, liab_cur=None,
            ppe=None, goodwill=None, intang=None, amort=None, buyback=None, issuance=None, extra=None):
    """Build a frames-style facts dict. Durations end 12-31 of each year; instants at the same date.
    Scalars broadcast to every year; lists are per year; None leaves the tag out for that year."""
    n = len(years)

    def series(v):
        if v is None:
            return [None] * n
        return list(v) if isinstance(v, (list, tuple)) else [v] * n

    facts = {}

    def add(tag, kind, vals):
        for y, v in zip(years, series(vals)):
            if v is None:
                continue
            facts.setdefault(tag, []).append({"kind": kind, "start": f"{y}-01-01" if kind == "duration" else None,
                                              "end": f"{y}-12-31", "val": float(v), "accn": f"0000000000-{y}-000001"})

    add("Revenues", "duration", rev)
    add("NetIncomeLoss", "duration", ni)
    add("OperatingIncomeLoss", "duration", opinc if opinc is not None else [x * 1.25 if x is not None else None for x in series(ni)])
    add("NetCashProvidedByUsedInOperatingActivities", "duration", cfo if cfo is not None else [x * 1.2 if x is not None else None for x in series(ni)])
    add("PaymentsToAcquirePropertyPlantAndEquipment", "duration", capex if capex is not None else [x * 0.1 if x is not None else None for x in series(ni)])
    add("DepreciationDepletionAndAmortization", "duration", da if da is not None else [x * 0.1 if x is not None else None for x in series(ni)])
    add("ShareBasedCompensation", "duration", sbc)
    add("InterestExpense", "duration", interest)
    add("WeightedAverageNumberOfDilutedSharesOutstanding", "duration", shares if shares is not None else 100.0)
    add("StockholdersEquity", "instant", equity if equity is not None else [x * 5 if x is not None else None for x in series(ni)])
    add("CashAndCashEquivalentsAtCarryingValue", "instant", cash if cash is not None else 10.0)
    add("LongTermDebtNoncurrent", "instant", debt_nc)
    add("DebtCurrent", "instant", debt_cur)
    add("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "duration", pretax)
    add("IncomeTaxExpenseBenefit", "duration", tax)
    add("AssetsCurrent", "instant", assets_cur)
    add("LiabilitiesCurrent", "instant", liab_cur)
    add("PropertyPlantAndEquipmentNet", "instant", ppe)
    add("Goodwill", "instant", goodwill)
    add("IntangibleAssetsNetExcludingGoodwill", "instant", intang)
    add("AmortizationOfIntangibleAssets", "duration", amort)
    add("PaymentsForRepurchaseOfCommonStock", "duration", buyback)
    add("ProceedsFromIssuanceOfCommonStock", "duration", issuance)
    for tag, kind, vals in (extra or []):
        add(tag, kind, vals)
    return facts


YEARS10 = list(range(2016, 2026))
YEARS11 = list(range(2015, 2026))


class FiscalYears(unittest.TestCase):
    def test_ttm_fact_from_10q_is_not_a_fiscal_year(self):
        """Amazon's 10-Q carries trailing-twelve-month net income (2025-10-01 to 2026-09-30); it must not create a
        fiscal year ending in September next to the December ones."""
        facts = company(YEARS10, rev=100, ni=10)
        facts["NetIncomeLoss"].append({"kind": "duration", "start": "2025-10-01", "end": "2026-09-30", "val": 11.0, "accn": "x"})
        fys = screen.fiscal_years(facts)
        self.assertEqual(fys[-1], "2025-12-31")
        self.assertEqual(len(fys), 10)

    def test_52_53_week_year_labels_dedupe(self):
        facts = company(YEARS10, rev=100, ni=10)
        facts["NetIncomeLoss"].append({"kind": "duration", "start": "2025-01-01", "end": "2025-12-27", "val": 10.0, "accn": "y"})
        self.assertEqual(len(screen.fiscal_years(facts)), 10)

    def test_profit_loss_tag_counts_when_net_income_tag_is_missing(self):
        """Mastercard tagged ProfitLoss before NetIncomeLoss: years must come from the union of the two tags."""
        facts = company(YEARS10, rev=100, ni=10)
        early = [f for f in facts["NetIncomeLoss"] if f["end"] < "2021"]
        facts["NetIncomeLoss"] = [f for f in facts["NetIncomeLoss"] if f["end"] >= "2021"]
        facts["ProfitLoss"] = early
        a = screen.analyse(facts)
        self.assertEqual(a["years_available"], 10)
        self.assertTrue(a["K1"].startswith("trece"))


class K1Record(unittest.TestCase):
    def test_under_seven_years_rejects(self):
        a = screen.analyse(company(list(range(2020, 2026)), rev=100, ni=10))
        self.assertTrue(a["K1"].startswith("respinge"))

    def test_seven_to_nine_years_is_short_history(self):
        a = screen.analyse(company(list(range(2018, 2026)), rev=100, ni=10))
        self.assertEqual(a["K1"], "trece (istoric scurt)")

    def test_three_loss_years_reject_two_pass(self):
        ni3 = [10] * 7 + [-1, -1, -1]
        ni2 = [10] * 8 + [-1, -1]
        self.assertEqual(screen.analyse(company(YEARS10, rev=100, ni=ni3))["K1"], "respinge")
        self.assertEqual(screen.analyse(company(YEARS10, rev=100, ni=ni2))["K1"], "trece")


class K3Returns(unittest.TestCase):
    def test_roe_below_12_rejects_when_nothing_else_defined(self):
        a = screen.analyse(company(YEARS11, rev=100, ni=5, equity=100))  # ROE 5%
        self.assertEqual(a["K3"], "respinge")

    def test_negative_equity_makes_roe_undefined_and_roic_decides(self):
        """Moody's: equity below zero for years; ROE is undefined, tangible ROIC carries the filter."""
        a = screen.analyse(company(YEARS11, rev=100, ni=20, opinc=27, pretax=26, tax=5.2, equity=-50,
                                   assets_cur=30, liab_cur=20, ppe=10, cash=5))
        self.assertIn("ROE nedefinit", a["K3"])
        self.assertTrue(a["K3"].startswith("trece"), a["K3"])
        self.assertIsNone(a["roe_median"])
        self.assertGreater(a["roic_tangible_median"], 0.15)

    def test_negligible_tangible_capital_passes_with_positive_nopat(self):
        """Adobe, CME: working capital below zero or tiny; the state is 'capital neglijabil', not a percent."""
        a = screen.analyse(company(YEARS11, rev=100, ni=8, opinc=10, pretax=10, tax=2, equity=100,
                                   assets_cur=20, liab_cur=40, ppe=2, cash=5))  # capital tangibil negativ, ROE 8%
        self.assertIsNone(a["roic_tangible_median"])
        self.assertGreaterEqual(a["negligible_capital_years"], 5)
        self.assertIn("neglijabil", a["K3"])
        self.assertTrue(a["K3"].startswith("trece"))

    def test_tax_rate_outside_0_50_is_clamped(self):
        a = screen.analyse(company(YEARS11, rev=100, ni=10, opinc=12, pretax=12, tax=8, equity=100,
                                   assets_cur=60, liab_cur=20, ppe=40, cash=2))  # 67% tax: clamped to 50%
        self.assertTrue(a["tax_clamped_last"])
        self.assertAlmostEqual(a["nopat_last"], 6.0)


class K4Leverage(unittest.TestCase):
    def test_sbc_counts_in_fcf(self):
        """Net debt 4.8x FCF before SBC, 5.2x after: K4 must use FCF after SBC and reject."""
        a = screen.analyse(company(YEARS10, rev=100, ni=10, cfo=20, capex=8, sbc=1.0, interest=1, opinc=12,
                                   cash=2, debt_nc=59.6))
        self.assertAlmostEqual(a["fcf_gross_last"], 12.0)
        self.assertAlmostEqual(a["fcf_last"], 11.0)
        self.assertAlmostEqual(a["nd_to_fcf"], 57.6 / 11.0, places=3)
        self.assertEqual(a["K4"], "respinge")

    def test_notes_tag_counts_as_debt(self):
        """Oracle: long-term debt sits under LongTermNotesPayable and a combined total; summing only DebtCurrent
        made it look like net cash."""
        facts = company(YEARS10, rev=100, ni=10, cfo=15, capex=30, cash=31, debt_cur=7.2,
                        extra=[("LongTermNotesPayable", "instant", 122.3), ("DebtLongtermAndShorttermCombinedAmount", "instant", 129.5)])
        a = screen.analyse(facts)
        self.assertAlmostEqual(a["debt_last"], 129.5)
        self.assertEqual(a["K4"], "respinge")  # FCF negative with net debt

    def test_notes_without_combined_total_are_summed(self):
        facts = company(YEARS10, rev=100, ni=10, cfo=15, capex=2, cash=1, debt_cur=2,
                        extra=[("LongTermNotesPayable", "instant", 20.0)])
        a = screen.analyse(facts)
        self.assertAlmostEqual(a["debt_last"], 22.0)

    def test_no_debt_tags_with_cash_and_equity_is_net_cash_flagged(self):
        a = screen.analyse(company(YEARS10, rev=100, ni=10, cash=30))
        self.assertTrue(a["debt_untagged"])
        self.assertIn("fără etichete de datorie", a["K4"])
        self.assertTrue(a["K4"].startswith("trece"))

    def test_missing_interest_small_net_debt_passes_large_is_unclear(self):
        small = screen.analyse(company(YEARS10, rev=100, ni=10, cfo=15, capex=3, cash=2, debt_nc=8))   # 0.5x
        large = screen.analyse(company(YEARS10, rev=100, ni=10, cfo=15, capex=3, cash=2, debt_nc=30))  # 2.3x
        self.assertTrue(small["K4"].startswith("trece (dobânzi nedisponibile"))
        self.assertTrue(large["K4"].startswith("neclar"))

    def test_low_interest_cover_rejects_even_with_low_net_debt(self):
        a = screen.analyse(company(YEARS10, rev=100, ni=10, opinc=12, cfo=15, capex=3, cash=2, debt_nc=8, interest=5))
        self.assertEqual(a["K4"], "respinge")


class K5Dilution(unittest.TestCase):
    def test_exact_split_ratio_is_adjusted(self):
        """Apple 2020, Nvidia 2021 and 2024: a round multiple is a split even when revenue jumped (Nvidia +114%)."""
        shares = [100] * 5 + [1000] * 5  # 10:1 in the sixth year
        a = screen.analyse(company(YEARS10, rev=[100] * 5 + [230] * 5, ni=10, shares=shares))
        self.assertIn("split", a["share_flags"])
        self.assertAlmostEqual(a["shares_cagr10"], 0.0, places=6)
        self.assertEqual(a["K5"], "trece")

    def test_scale_error_without_equity_jump_is_adjusted(self):
        """KLA FY2024: diluted shares tagged ten times too large, equity flat."""
        shares = [140] * 8 + [1361] * 2
        a = screen.analyse(company(YEARS10, rev=100, ni=10, shares=shares, equity=50))
        self.assertIn("ajustat", a["share_flags"])
        self.assertEqual(a["K5"], "trece")

    def test_merger_issuance_is_not_a_split(self):
        """Leidos 2017: shares x1.48 with revenue +44%: issuance, kept in the dilution CAGR."""
        shares = [73] * 2 + [108] * 8
        rev = [5000] * 2 + [7200] * 8
        a = screen.analyse(company(YEARS10, rev=rev, ni=200, shares=shares, equity=[1200] * 2 + [3300] * 8))
        self.assertIn("emisiune", a["share_flags"])
        self.assertGreater(a["shares_cagr10"], 0.03)

    def test_sbc_above_10_percent_rejects(self):
        a = screen.analyse(company(YEARS10, rev=100, ni=10, sbc=11))
        self.assertEqual(a["K5"], "respinge")

    def test_dilution_above_2_percent_rejects(self):
        shares = [100 * 1.03 ** i for i in range(10)]
        a = screen.analyse(company(YEARS10, rev=100, ni=10, shares=shares))
        self.assertEqual(a["K5"], "respinge")


class OwnerEarningsRange(unittest.TestCase):
    def test_hyperscaler_capex_opens_the_range(self):
        """Capex three times tangible D&A: OE_jos carries all of it, OE_sus only the D&A."""
        a = screen.analyse(company(YEARS10, rev=100, ni=20, da=10, capex=30, amort=2))
        self.assertAlmostEqual(a["oe_low_last"], 0.0)         # 20 + 10 - 30
        self.assertAlmostEqual(a["oe_high_last"], 22.0)       # 20 + 10 - min(8, 30)
        self.assertAlmostEqual(a["capex_to_da_tangible"], 30 / 8)
        self.assertFalse(a["amort_missing"])

    def test_asset_light_capex_below_da_keeps_range_closed(self):
        a = screen.analyse(company(YEARS10, rev=100, ni=20, da=10, capex=3, amort=0))
        self.assertAlmostEqual(a["oe_low_last"], 27.0)
        self.assertAlmostEqual(a["oe_high_last"], 27.0)  # maintenance capped at total capex

    def test_missing_amortization_tag_is_flagged(self):
        a = screen.analyse(company(YEARS10, rev=100, ni=20, da=10, capex=12))
        self.assertTrue(a["amort_missing"])


class Buybacks(unittest.TestCase):
    def test_net_buybacks_and_price_per_share_retired(self):
        shares = [100 - i for i in range(10)]  # one share retired a year
        a = screen.analyse(company(YEARS10, rev=100, ni=10, shares=shares, buyback=5.0, issuance=2.0))
        self.assertAlmostEqual(a["net_buyback_last"], 3.0)
        self.assertAlmostEqual(a["price_per_share_retired"], 3.0)

    def test_no_share_reduction_gives_no_price_per_share(self):
        a = screen.analyse(company(YEARS10, rev=100, ni=10, shares=100, buyback=5.0))
        self.assertIsNone(a["price_per_share_retired"])


class Direction(unittest.TestCase):
    def test_revenue_deceleration_is_flagged(self):
        rev = [100 * 1.2 ** i for i in range(7)] + [100 * 1.2 ** 6 * 1.05 ** i for i in range(1, 4)]
        a = screen.analyse(company(YEARS10, rev=rev, ni=[x * 0.2 for x in rev]))
        self.assertIn("venituri", a["trend_breaks"])
        self.assertNotIn("accelerare", a["trend_breaks"])
        self.assertAlmostEqual(a["rev_cagr_long"], 0.20, places=3)
        self.assertAlmostEqual(a["rev_cagr_short"], 0.05, places=3)

    def test_steady_growth_has_no_break(self):
        rev = [100 * 1.1 ** i for i in range(10)]
        a = screen.analyse(company(YEARS10, rev=rev, ni=[x * 0.2 for x in rev]))
        self.assertEqual(a["trend_breaks"], "")

    def test_margin_compression_is_flagged(self):
        rev = [100] * 10
        ni = [20] * 7 + [12] * 3
        a = screen.analyse(company(YEARS10, rev=rev, ni=ni, opinc=[25] * 7 + [15] * 3))
        self.assertIn("marja operațională", a["trend_breaks"])

    def test_slower_buybacks_are_not_called_dilution(self):
        shares = [100 * 0.95 ** i for i in range(7)] + [100 * 0.95 ** 6 * 0.99 ** i for i in range(1, 4)]
        a = screen.analyse(company(YEARS10, rev=100, ni=10, shares=shares))
        self.assertIn("răscumpărări încetinite", a["trend_breaks"])
        self.assertNotIn("diluare în creștere", a["trend_breaks"])


class K2Indicators(unittest.TestCase):
    def test_rd_and_revenue_swing_flags(self):
        rev = [100] * 8 + [140, 150]
        facts = company(YEARS10, rev=rev, ni=10, extra=[("ResearchAndDevelopmentExpense", "duration", 30)])  # 20% of 150
        a = screen.analyse(facts)
        self.assertIn("R&D", a["K2_flags"])
        self.assertIn("abatere venituri", a["K2_flags"])


if __name__ == "__main__":
    unittest.main()
