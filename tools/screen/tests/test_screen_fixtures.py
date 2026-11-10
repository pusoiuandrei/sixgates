"""Regression tests on frozen real data: facts extracted from the SEC frames API on 2026-11-10 for the companies
where the pipeline once went wrong. The expectations are the verified outputs after the fixes; a change here
means a rule drifted, not that the market moved (the fixtures do not update)."""
from __future__ import annotations

import gzip
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import screen  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


def load(ticker: str) -> dict:
    with gzip.open(FIX / f"facts_{ticker}.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)["facts"]


class RealCompanies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = {t: screen.analyse(load(t)) for t in
                 ("AMZN", "AAPL", "KLAC", "ORCL", "LDOS", "KO", "MCO", "ADBE", "CME", "NVDA", "CHKP")}

    def test_amazon_ttm_quarter_fact_does_not_become_a_fiscal_year(self):
        a = self.a["AMZN"]
        self.assertEqual(a["fy_last"], "2025-12-31")
        self.assertGreaterEqual(a["years_available"], 10)
        self.assertTrue(a["K1"].startswith("trece"))
        self.assertGreater(a["oe_high_last"], 5 * a["oe_low_last"])  # capex cycle opens the OE range

    def test_apple_split_adjusted_and_interest_missing_handled(self):
        a = self.a["AAPL"]
        self.assertIn("salt 4x", a["share_flags"])
        self.assertLess(a["shares_cagr10"], -0.02)
        self.assertEqual(a["K5"], "trece")
        self.assertTrue(a["K4"].startswith("trece"))
        self.assertIsNone(a["cover"])  # Apple stopped disclosing interest expense

    def test_kla_scale_error_adjusted(self):
        a = self.a["KLAC"]
        self.assertIn("salt 10x", a["share_flags"])
        self.assertLess(a["shares_cagr10"], 0.0)
        self.assertEqual(a["K5"], "trece")

    def test_oracle_notes_count_as_debt(self):
        a = self.a["ORCL"]
        self.assertGreater(a["debt_last"], 120e9)
        self.assertEqual(a["K4"], "respinge")
        self.assertLess(a["oe_low_last"], 0)
        self.assertGreater(a["capex_to_da_tangible"], 5)

    def test_leidos_merger_is_issuance_not_split(self):
        a = self.a["LDOS"]
        self.assertIn("emisiune", a["share_flags"])
        self.assertNotIn("split", a["share_flags"])
        self.assertGreater(a["shares_cagr10"], 0.02)
        self.assertEqual(a["K5"], "trece")  # five-year window is clean

    def test_coca_cola_fails_leverage_after_sbc(self):
        a = self.a["KO"]
        self.assertEqual(a["K4"], "respinge")
        self.assertGreater(a["nd_to_fcf"], 5)
        self.assertTrue(a["K3"].startswith("trece"))
        self.assertEqual(a["loss_years"], 0)

    def test_moodys_negative_equity_roe_undefined(self):
        a = self.a["MCO"]
        self.assertGreaterEqual(a["neg_equity_years"], 3)
        self.assertIn("ROE nedefinit", a["K3"])
        self.assertTrue(a["K3"].startswith("trece"))

    def test_adobe_negligible_capital_and_deceleration(self):
        a = self.a["ADBE"]
        self.assertEqual(a["negligible_capital_years"], 10)
        self.assertIsNone(a["roic_tangible_median"])
        self.assertIn("neglijabil", a["K3"])
        self.assertIn("venituri", a["trend_breaks"])
        self.assertTrue(a["K4"].startswith("trece (numerar net)"))
        self.assertLess(a["sbc_to_rev"], 0.10)

    def test_cme_passes_k3_only_through_negligible_capital(self):
        a = self.a["CME"]
        self.assertLess(a["roe_median"], 0.12)
        self.assertGreaterEqual(a["negligible_capital_years"], 5)
        self.assertTrue(a["K3"].startswith("trece"))

    def test_nvidia_two_splits_and_acceleration(self):
        a = self.a["NVDA"]
        self.assertIn("salt 4x", a["share_flags"])
        self.assertIn("salt 10x", a["share_flags"])
        self.assertEqual(a["K5"], "trece")
        self.assertIn("accelerare", a["trend_breaks"])
        self.assertIn("abatere venituri", a["K2_flags"])

    def test_check_point_no_debt_tags_and_margin_compression(self):
        a = self.a["CHKP"]
        self.assertTrue(a["debt_untagged"])
        self.assertIn("fără etichete de datorie", a["K4"])
        self.assertIn("marja operațională", a["trend_breaks"])
        self.assertEqual(a["loss_years"], 0)

    def test_verdict_vocabulary_is_closed(self):
        """K states use only the four framework words plus 'neclar' (the screen's own 'needs a look')."""
        for t, a in self.a.items():
            for k in ("K1", "K3", "K4", "K5"):
                self.assertTrue(a[k].startswith(("trece", "respinge", "neclar")), (t, k, a[k]))


if __name__ == "__main__":
    unittest.main()
