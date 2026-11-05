#!/usr/bin/env python3
"""Restrict the quantitative survivors to the user's circle (technology, cyber, fintech and related),
apply K7 exclusions, and rank by quality indicators. Adds a rough price indicator (Yahoo quote,
latest diluted shares) for the ranked list. Output: ranked.csv and ranked.json.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent

# Circle by SIC (Nasdaq names) and by GICS sub-industry (S&P 500 names).
SIC_IN = {
    # software, internet, IT services
    "7370", "7371", "7372", "7373", "7374", "7375", "7377", "7379",
    # hardware, semis, networking, instruments
    "3570", "3571", "3572", "3576", "3577", "3578", "3579", "3661", "3663", "3669", "3670", "3672", "3674",
    "3678", "3679", "3825",
    # distribution / channel, e-commerce
    "5045", "5961",
    # fintech, market infrastructure, data
    "6141", "6153", "6159", "6162", "6163", "6172", "6199", "6200", "6211", "6282", "6289", "7320",
    # business services NEC (payments, consulting), research and consulting
    "7389", "8700", "8742",
}
GICS_IN = {
    "Application Software", "Systems Software", "Interactive Media & Services", "Internet Services & Infrastructure",
    "IT Consulting & Other Services", "Data Processing & Outsourced Services", "Semiconductors",
    "Semiconductor Materials & Equipment", "Technology Hardware, Storage & Peripherals", "Communications Equipment",
    "Electronic Components", "Electronic Equipment & Instruments", "Electronic Manufacturing Services",
    "Technology Distributors", "Transaction & Payment Processing Services", "Financial Exchanges & Data",
    "Consumer Finance", "Investment Banking & Brokerage", "Research & Consulting Services", "Broadline Retail",
    "Internet Retail", "Interactive Home Entertainment",
}
# explicit platform names the user understands even when GICS/SIC puts them elsewhere
NAME_IN = {"BKNG", "ABNB", "UBER", "DASH", "EXPE", "SPOT", "NFLX"}
K7_SIC_PREFIX = ("602", "603", "609", "611", "631", "632", "633", "635", "636", "641", "679")  # banks, insurers, REITs, blank checks

CATEGORY = [
    ("fintech / infrastructură de piață", lambda sic, g: sic in {"6141", "6153", "6159", "6162", "6163", "6172", "6199", "6200", "6211", "6282", "6289", "7320"} or g in {"Transaction & Payment Processing Services", "Financial Exchanges & Data", "Consumer Finance", "Investment Banking & Brokerage"}),
    ("semiconductori / hardware / rețele", lambda sic, g: sic.startswith(("357", "366", "367", "3825")) or g in {"Semiconductors", "Semiconductor Materials & Equipment", "Technology Hardware, Storage & Peripherals", "Communications Equipment", "Electronic Components", "Electronic Equipment & Instruments", "Electronic Manufacturing Services"}),
    ("servicii IT / consultanță / distribuție", lambda sic, g: sic in {"7371", "7373", "8700", "8742", "5045"} or g in {"IT Consulting & Other Services", "Research & Consulting Services", "Technology Distributors"}),
    ("software / internet", lambda sic, g: sic.startswith("737") or g in {"Application Software", "Systems Software", "Interactive Media & Services", "Internet Services & Infrastructure", "Data Processing & Outsourced Services", "Interactive Home Entertainment"}),
    ("comerț online / platforme", lambda sic, g: sic == "5961" or g in {"Broadline Retail", "Internet Retail"}),
    ("servicii de afaceri (plăți, consultanță)", lambda sic, g: sic == "7389"),
]


def f(x):
    try:
        return float(x) if x not in ("", None) else None
    except ValueError:
        return None


def yahoo_quote(ticker: str):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1d"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        m = r.json()["chart"]["result"][0]["meta"]
        return m.get("regularMarketPrice"), time.strftime("%Y-%m-%d", time.gmtime(m.get("regularMarketTime", 0))), m.get("currency")
    except Exception:
        return None, None, None


def main() -> int:
    rows = list(csv.DictReader(open(HERE / "screen_all.csv", encoding="utf-8")))
    sic = json.load(open(HERE / "sic.json"))
    out = []
    for r in rows:
        if not (r.get("K1", "").startswith("trece") and r.get("K3", "").startswith("trece")
                and r.get("K4", "").startswith("trece") and r.get("K5", "").startswith("trece")):
            continue
        meta = sic.get(r["cik"], {})
        s = str(meta.get("sic") or "")
        g = r.get("gics_sub", "")
        tickers = r["tickers"].split("|")
        k7 = s.startswith(K7_SIC_PREFIX) or g in {"Diversified Banks", "Regional Banks", "Insurance Brokers", "Life & Health Insurance",
                                                  "Property & Casualty Insurance", "Multi-line Insurance", "Reinsurance",
                                                  "Asset Management & Custody Banks"} or "REIT" in g
        in_circle = (s in SIC_IN or g in GICS_IN or any(t in NAME_IN for t in tickers)) and not k7
        if not in_circle:
            continue
        cat = next((name for name, test in CATEGORY if test(s, g)), "altele")
        forms = meta.get("annual_forms") or []
        q = {
            "ticker": tickers[0], "name": r["name"], "cik": r["cik"], "sp500": r["sp500"], "exchanges": r["exchanges"],
            "sic": s, "sic_desc": meta.get("sicDescription"), "gics_sub": g, "category": cat,
            "forms": "|".join(forms), "fy_end": r["fy_last"], "years": r["years_available"],
            "loss_years": int(r["loss_years"] or 0), "roe_median": f(r["roe_median"]), "neg_equity_years": int(r["neg_equity_years"] or 0),
            "rev_last": f(r["rev_last"]), "rev_cagr": f(r["rev_cagr"]), "rev_max_dev": f(r["rev_max_dev"]),
            "op_margin_median": f(r["op_margin_median"]), "op_margin_min": f(r["op_margin_min"]),
            "fcf_margin_median": f(r["fcf_margin_median"]), "capex_to_cfo_median": f(r["capex_to_cfo_median"]),
            "oe_low_last": f(r["oe_low_last"]), "oe_low_cagr": f(r["oe_low_cagr"]), "fcf_last": f(r["fcf_last"]),
            "net_debt": f(r["net_debt"]), "nd_to_fcf": f(r["nd_to_fcf"]), "cover": f(r["cover"]),
            "shares_cagr5": f(r["shares_cagr5"]), "shares_cagr10": f(r["shares_cagr10"]), "sbc_to_rev": f(r["sbc_to_rev"]),
            "rd_to_rev": f(r["rd_to_rev"]), "buyback_last": f(r["buyback_last"]), "div_last": f(r["div_last"]),
            "K1": r["K1"], "K2_flags": r["K2_flags"], "K3": r["K3"], "K4": r["K4"], "K5": r["K5"],
            "share_flags": r.get("share_flags", ""), "debt_tag": r.get("debt_tag", ""), "cash_tag": r.get("cash_tag", ""),
        }
        # quality points (ranking aid only, never shown as a score to the user)
        pts = 0
        pts += 2 if q["loss_years"] == 0 else 0
        pts += 2 if (q["roe_median"] or 0) >= 0.25 else (1 if (q["roe_median"] or 0) >= 0.15 else 0)
        pts += 2 if (q["fcf_margin_median"] or 0) >= 0.20 else (1 if (q["fcf_margin_median"] or 0) >= 0.12 else 0)
        pts += 1 if (q["op_margin_min"] or 0) >= 0.15 else 0
        pts += 1 if q["rev_max_dev"] is not None and q["rev_max_dev"] <= 0.20 else 0
        pts += 1 if (q["rev_cagr"] or 0) >= 0.05 else 0
        pts += 1 if (q["oe_low_cagr"] or 0) >= 0.05 else 0
        pts += 1 if q["shares_cagr10"] is not None and q["shares_cagr10"] <= 0 else 0
        pts += 1 if (q["sbc_to_rev"] or 0) <= 0.05 else 0
        pts += 1 if (q["capex_to_cfo_median"] or 1) <= 0.25 else 0
        pts += 1 if (q["net_debt"] or 0) <= 0 else 0
        pts += 1 if int(q["years"] or 0) >= 10 else 0
        q["quality_pts"] = pts
        out.append(q)
    out.sort(key=lambda q: (-q["quality_pts"], -(q["fcf_margin_median"] or 0)))
    # rough price indicator for the top names
    for q in out[:40]:
        price, pdate, cur = yahoo_quote(q["ticker"])
        q["price"], q["price_date"], q["price_currency"] = price, pdate, cur
        time.sleep(0.3)
    with open(HERE / "ranked.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ["ticker"])
        w.writeheader()
        for q in out:
            w.writerow({k: ("" if v is None else v) for k, v in q.items()})
    json.dump(out, open(HERE / "ranked.json", "w"), indent=1, ensure_ascii=False)
    print(len(out), "in circle after K7")
    for q in out[:45]:
        print(f"{q['quality_pts']:2d} {q['ticker']:6} {q['name'][:28]:28} {q['category'][:22]:22} loss={q['loss_years']} roe={q['roe_median'] and round(q['roe_median'],2)} fcfm={q['fcf_margin_median'] and round(q['fcf_margin_median'],2)} opmin={q['op_margin_min'] and round(q['op_margin_min'],2)} revcagr={q['rev_cagr'] and round(q['rev_cagr'],3)} dev={q['rev_max_dev'] and round(q['rev_max_dev'],2)} sh10={q['shares_cagr10'] and round(q['shares_cagr10'],3)} sbc={q['sbc_to_rev'] and round(q['sbc_to_rev'],3)} rd={q['rd_to_rev'] and round(q['rd_to_rev'],2)} nd/fcf={q['nd_to_fcf'] and round(q['nd_to_fcf'],1)} px={q.get('price')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
