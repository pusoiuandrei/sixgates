#!/usr/bin/env python3
"""Fetch SEC submissions metadata (SIC code, description, fiscal year end, forms) for a list of CIKs.

Usage: python3 sic_lookup.py ciks.txt  (one CIK per line) -> sic.json (cached, incremental).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

HERE = Path(os.environ.get("SIXGATES_SCREEN_DIR", Path(__file__).resolve().parent))
OUT = HERE / "sic.json"
UA = {"User-Agent": "SixGates research spike contact@sixgates.local", "Accept-Encoding": "gzip, deflate"}


def main() -> int:
    ciks = [int(x) for x in Path(sys.argv[1]).read_text().split()]
    cache = json.load(open(OUT)) if OUT.exists() else {}
    todo = [c for c in ciks if str(c) not in cache or "business_country" not in cache[str(c)]]
    print(f"{len(todo)} to fetch, {len(cache)} cached", flush=True)
    for i, cik in enumerate(todo, 1):
        url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
        for attempt in range(3):
            try:
                r = requests.get(url, headers=UA, timeout=60)
                if r.status_code == 200:
                    d = r.json()
                    rec = d.get("filings", {}).get("recent", {})
                    forms = rec.get("form", [])
                    dates = rec.get("filingDate", [])
                    last_annual = max((dt for f, dt in zip(forms, dates) if f in ("10-K", "20-F", "40-F")), default=None)
                    biz = (d.get("addresses") or {}).get("business") or {}
                    cache[str(cik)] = {
                        "business_country": biz.get("stateOrCountry"), "last_annual_filing": last_annual,
                        "name": d.get("name"), "sic": d.get("sic"), "sicDescription": d.get("sicDescription"),
                        "fiscalYearEnd": d.get("fiscalYearEnd"), "stateOfIncorporation": d.get("stateOfIncorporation"),
                        "exchanges": d.get("exchanges"), "tickers": d.get("tickers"),
                        "annual_forms": sorted({f for f in forms if f in ("10-K", "20-F", "40-F", "10-K/A", "20-F/A")}),
                        "category": d.get("category"),
                    }
                    break
                time.sleep(2)
            except requests.RequestException:
                time.sleep(2)
        else:
            cache[str(cik)] = {"error": "fetch failed"}
        time.sleep(0.2)
        if i % 50 == 0:
            json.dump(cache, open(OUT, "w"), indent=0)
            print(f"{i}/{len(todo)}", flush=True)
    json.dump(cache, open(OUT, "w"), indent=0)
    print("done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
