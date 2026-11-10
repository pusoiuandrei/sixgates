"""End-to-end regression of the screen pipeline on a small synthetic universe, plus the daily brief helpers.
No network: prices and FRED are stubbed; the frames database is built from the frozen fixtures and one synthetic bank.
"""
from __future__ import annotations

import csv
import gzip
import importlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

FIX = HERE / "fixtures"


def load(ticker: str) -> dict:
    with gzip.open(FIX / f"facts_{ticker}.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def build_workdir(tmp: Path) -> None:
    """frames.db with Adobe, Coca-Cola, Oracle, Moody's and a synthetic bank; universe.json; sic.json."""
    con = sqlite3.connect(tmp / "frames.db")
    con.execute("CREATE TABLE facts(tag TEXT, kind TEXT, cik INTEGER, start TEXT, end TEXT, val REAL, accn TEXT, frame TEXT, entity TEXT)")
    uni, sic = [], {}
    meta = {"ADBE": ("Application Software", "7372", "Services-Prepackaged Software", True),
            "KO": ("Soft Drinks & Non-alcoholic Beverages", "2080", "Beverages", True),
            "ORCL": ("Systems Software", "7372", "Services-Prepackaged Software", True),
            "MCO": ("Financial Exchanges & Data", "7320", "Services-Consumer Credit Reporting", True)}
    for t, (gics, s, sdesc, sp) in meta.items():
        d = load(t)
        for tag, facts in d["facts"].items():
            con.executemany("INSERT INTO facts VALUES (?,?,?,?,?,?,?,?,?)",
                            [(tag, f["kind"], d["cik"], f["start"], f["end"], f["val"], f["accn"], "", t) for f in facts])
        uni.append({"cik": d["cik"], "name": t, "tickers": [t], "exchanges": ["Nasdaq"], "sp500": sp, "gics_sector": "", "gics_sub": gics})
        sic[str(d["cik"])] = {"sic": s, "sicDescription": sdesc, "annual_forms": ["10-K"], "business_country": "CA",
                              "stateOfIncorporation": "DE", "last_annual_filing": "2026-02-01"}
    # synthetic bank passing every quantitative filter: must fall to K7
    cik = 999001
    for y in range(2015, 2026):
        rows = [("Revenues", "duration", f"{y}-01-01", f"{y}-12-31", 1000.0), ("NetIncomeLoss", "duration", f"{y}-01-01", f"{y}-12-31", 200.0),
                ("OperatingIncomeLoss", "duration", f"{y}-01-01", f"{y}-12-31", 260.0),
                ("NetCashProvidedByUsedInOperatingActivities", "duration", f"{y}-01-01", f"{y}-12-31", 250.0),
                ("PaymentsToAcquirePropertyPlantAndEquipment", "duration", f"{y}-01-01", f"{y}-12-31", 10.0),
                ("WeightedAverageNumberOfDilutedSharesOutstanding", "duration", f"{y}-01-01", f"{y}-12-31", 100.0),
                ("StockholdersEquity", "instant", None, f"{y}-12-31", 1000.0), ("CashAndCashEquivalentsAtCarryingValue", "instant", None, f"{y}-12-31", 500.0)]
        con.executemany("INSERT INTO facts VALUES (?,?,?,?,?,?,?,?,?)", [(a, b, cik, c, d_, v, "acc", "", "BANK") for a, b, c, d_, v in rows])
    uni.append({"cik": cik, "name": "Synthetic Bank", "tickers": ["BNKX"], "exchanges": ["Nasdaq"], "sp500": False, "gics_sector": "", "gics_sub": ""})
    sic[str(cik)] = {"sic": "6022", "sicDescription": "State Commercial Banks", "annual_forms": ["10-K"], "business_country": "NY",
                     "stateOfIncorporation": "DE", "last_annual_filing": "2026-02-01"}
    con.commit()
    con.close()
    json.dump(uni, (tmp / "universe.json").open("w"))
    json.dump(sic, (tmp / "sic.json").open("w"))


class Pipeline(unittest.TestCase):
    def test_screen_then_circle(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            build_workdir(tmp)
            os.environ["SIXGATES_SCREEN_DIR"] = str(tmp)
            import screen
            import rank_circle
            importlib.reload(screen)
            importlib.reload(rank_circle)
            self.assertEqual(screen.main(), 0)
            rows = {r["tickers"]: r for r in csv.DictReader((tmp / "screen_all.csv").open(encoding="utf-8"))}
            funnel = json.load((tmp / "funnel.json").open())
            self.assertEqual(funnel["universe"], 5)
            self.assertEqual(funnel["with_facts"], 5)
            self.assertEqual(rows["KO"]["K4"], "respinge")
            self.assertEqual(rows["ORCL"]["K4"], "respinge")
            self.assertTrue(rows["BNKX"]["K4"].startswith("trece"))  # numbers pass, K7 must catch it
            rank_circle.yahoo_quote = lambda t: (100.0, "2026-11-10", "USD")  # no network
            self.assertEqual(rank_circle.main(), 0)
            ranked = {q["ticker"]: q for q in json.load((tmp / "ranked.json").open(encoding="utf-8"))}
            self.assertIn("ADBE", ranked)
            self.assertIn("MCO", ranked)
            self.assertNotIn("KO", ranked)    # fails K4
            self.assertNotIn("ORCL", ranked)  # fails K4
            self.assertNotIn("BNKX", ranked)  # K7: bank
            self.assertGreaterEqual(ranked["ADBE"]["quality_pts"], 10)
            self.assertEqual(ranked["ADBE"]["category"], "software / internet")
            self.assertEqual(ranked["MCO"]["category"], "fintech / infrastructură de piață")


class DailyHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import daily
        cls.daily = daily

    def test_vi_matches_gordon_growth_when_g_equals_terminal(self):
        d = self.daily
        oe, r, g = 10.0, 0.06, 0.025
        self.assertAlmostEqual(d.vi_per_share(oe, g, r, gt=g), oe * (1 + g) / (r - g), places=6)

    def test_implied_growth_inverts_vi(self):
        d = self.daily
        for g in (-0.05, 0.0, 0.04, 0.12):
            price = d.vi_per_share(5.0, g, 0.08)
            self.assertAlmostEqual(d.implied_growth(5.0, price, 0.08), g, places=4)

    def test_price_band_language_has_no_verdict_words(self):
        d = self.daily
        vi = 100.0
        for price, expect in ((40.0, "peste marja maximă"), (60.0, "între marjele"), (80.0, "sub marja minimă"), (130.0, "peste VI_jos cu 30%")):
            band = d.band_text(price, vi)
            self.assertIn(expect, band)
            for word in ("ieftin", "scump", "cumpără", "vinde", "buy", "sell", "oportunitate"):
                self.assertNotIn(word, band.lower())
        self.assertEqual(d.band_text(50.0, 100.0), "sub VI_jos cu 50%: peste marja maximă propusă (50%)")

    def test_eligibility_reasons(self):
        d = self.daily
        today = date(2026, 11, 10)
        base = {"business_country": "DE", "quality_pts": 12, "fy_end": "2025-12-31", "oe_low_last": 1e9, "price": 10.0,
                "p_to_vi": 0.5, "mcap": 5e9, "rev_last": 1e9, "shares_cagr10": -0.01, "last_annual_filing": "2026-02-01"}
        self.assertEqual(d.eligible(dict(base), today), (True, ""))
        self.assertIn("China", d.eligible({**base, "business_country": "F4"}, today)[1])
        self.assertIn("puncte", d.eligible({**base, "quality_pts": 9}, today)[1])
        self.assertIn("15 luni", d.eligible({**base, "fy_end": "2024-12-31"}, today)[1])
        self.assertIn("OE_jos negativ", d.eligible({**base, "oe_low_last": -1.0}, today)[1])
        self.assertIn("preț", d.eligible({**base, "price": None}, today)[1])
        self.assertIn("capitalizare", d.eligible({**base, "mcap": 1e9}, today)[1])
        self.assertIn("venituri", d.eligible({**base, "rev_last": 1e8}, today)[1])
        self.assertIn("15%", d.eligible({**base, "shares_cagr10": 0.3}, today)[1])

    def test_rotation_excludes_recent_and_falls_back(self):
        d = self.daily
        today = date(2026, 11, 10)
        mk = lambda t, p: {"ticker": t, "business_country": "DE", "quality_pts": 12, "fy_end": "2025-12-31", "oe_low_last": 1.0,
                           "price": 10.0, "p_to_vi": p, "mcap": 5e9, "rev_last": 1e9, "shares_cagr10": 0.0, "last_annual_filing": "2026-02-01"}
        items = [mk("A", 0.3), mk("B", 0.4), mk("C", 0.5), mk("D", 0.6), mk("E", 0.7)]
        state = {"presented": {"A": ["2026-11-01"], "B": ["2026-10-01"]}}  # A recent, B older than 30 days
        picks, pool = d.choose(items, state, today)
        self.assertEqual([p["ticker"] for p in picks], ["B", "C", "D"])
        state2 = {"presented": {t: ["2026-11-09"] for t in "ABCDE"}}
        picks2, _ = d.choose(items, state2, today)
        self.assertEqual(len(picks2), 3)  # rotation exhausted: repeats allowed

    def test_sanity_line_flags_big_jumps(self):
        d = self.daily
        prev = {"counts": {"universe": 3800, "with_facts": 3200, "k_pass": 370, "in_circle": 110, "eligible": 44}}
        ok = d.sanity_line(prev, {"universe": 3805}, {"with_facts": 3210, "K1_K3_K4_K5_pass": 372}, 111, 45)
        bad = d.sanity_line(prev, {"universe": 3805}, {"with_facts": 3210, "K1_K3_K4_K5_pass": 372}, 60, 45)
        self.assertIn("în marja de 20%", ok)
        self.assertIn("ATENȚIE", bad)
        self.assertIn("în cerc 110 la 60", bad)

    def test_romanian_number_formatting(self):
        d = self.daily
        self.assertEqual(d.ro(1234.5, 1), "1 234,5")
        self.assertEqual(d.pct(0.1234), "12,3%")
        self.assertEqual(d.bn(2.5e9), "2,50 mld USD")
        self.assertEqual(d.bn(3.2e8), "320 mil USD")
        self.assertEqual(d.sig2(583.7), 580)

    def test_filing_link(self):
        self.assertEqual(self.daily.filing_link("796343", "0000796343-26-000003"),
                         "https://www.sec.gov/Archives/edgar/data/796343/000079634326000003/")


if __name__ == "__main__":
    unittest.main()
