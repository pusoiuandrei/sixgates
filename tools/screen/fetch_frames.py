#!/usr/bin/env python3
"""Fetch SEC XBRL frames (one concept, one period, all filers) into a compact SQLite table.

Why frames: one request returns the latest-filed value of a concept for every SEC filer in a
calendar period, so a ten-year screen of ~5,000 companies costs ~1,000 small requests instead
of 5,000 companyfacts downloads. Frames carry the accession number, so each value keeps its
provenance (accn + start/end). Fiscal years are aligned later by the fact's own end date, not
by the frame label (SEC maps a June-2025 fiscal year to CY2024).

Durations: CY2014 .. CY2025. Instants: CY2014Q1I .. CY2025Q4I.
Rate: ~5 requests/second in total (SEC allows 10). User-Agent: SixGates research contact.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parent
DB = OUT / "frames.db"
LOG = OUT / "fetch_frames.log"
UA = {"User-Agent": "SixGates research spike contact@sixgates.local", "Accept-Encoding": "gzip, deflate"}
BASE = "https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/{uom}/{frame}.json"
YEARS = list(range(2014, 2027))

DURATIONS = {
    # revenue
    "Revenues": "USD", "RevenueFromContractWithCustomerExcludingAssessedTax": "USD", "SalesRevenueNet": "USD",
    "RevenueFromContractWithCustomerIncludingAssessedTax": "USD",
    # profit
    "NetIncomeLoss": "USD", "ProfitLoss": "USD", "OperatingIncomeLoss": "USD",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "USD",
    "IncomeTaxExpenseBenefit": "USD",
    # cash flow
    "NetCashProvidedByUsedInOperatingActivities": "USD",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations": "USD",
    "PaymentsToAcquirePropertyPlantAndEquipment": "USD", "PaymentsToAcquireProductiveAssets": "USD",
    "DepreciationDepletionAndAmortization": "USD", "DepreciationAndAmortization": "USD",
    "DepreciationAmortizationAndAccretionNet": "USD",
    "ShareBasedCompensation": "USD", "AllocatedShareBasedCompensationExpense": "USD",
    "PaymentsForRepurchaseOfCommonStock": "USD", "PaymentsOfDividends": "USD", "PaymentsOfDividendsCommonStock": "USD",
    # interest, R&D, shares
    "InterestExpense": "USD", "InterestExpenseNonoperating": "USD", "InterestExpenseDebt": "USD",
    "InterestPaidNet": "USD", "InterestPaid": "USD",
    "ResearchAndDevelopmentExpense": "USD",
    "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost": "USD",
    "WeightedAverageNumberOfDilutedSharesOutstanding": "shares",
}
INSTANTS = {
    "StockholdersEquity": "USD", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest": "USD",
    "CashAndCashEquivalentsAtCarryingValue": "USD", "CashCashEquivalentsAndShortTermInvestments": "USD",
    "ShortTermInvestments": "USD", "MarketableSecuritiesCurrent": "USD",
    "AvailableForSaleSecuritiesDebtSecuritiesCurrent": "USD",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": "USD",
    "LongTermDebt": "USD", "LongTermDebtNoncurrent": "USD", "LongTermDebtCurrent": "USD", "DebtCurrent": "USD",
    "ShortTermBorrowings": "USD", "CommercialPaper": "USD",
    "LongTermDebtAndCapitalLeaseObligations": "USD", "LongTermDebtAndCapitalLeaseObligationsCurrent": "USD",
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities": "USD",
    "DebtLongtermAndShorttermCombinedAmount": "USD", "NotesPayable": "USD", "LongTermNotesPayable": "USD",
    "ConvertibleNotesPayable": "USD", "ConvertibleDebtNoncurrent": "USD", "ConvertibleDebtCurrent": "USD",
    "SeniorNotes": "USD", "LongTermLineOfCredit": "USD", "LineOfCredit": "USD", "OtherLongTermDebtNoncurrent": "USD",
}

_lock = threading.Lock()
_last = [0.0]
MIN_INTERVAL = 0.2  # global, ~5 req/s


def _throttle() -> None:
    with _lock:
        wait = MIN_INTERVAL - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()


def fetch_one(tag: str, uom: str, frame: str, kind: str) -> tuple[str, str, str, list[tuple]]:
    url = BASE.format(tag=tag, uom=uom, frame=frame)
    for attempt in range(4):
        _throttle()
        try:
            r = requests.get(url, headers=UA, timeout=120)
        except requests.RequestException as exc:
            if attempt == 3:
                return tag, frame, f"error {exc}", []
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code == 404:
            return tag, frame, "404", []
        if r.status_code != 200:
            if attempt == 3:
                return tag, frame, f"http {r.status_code}", []
            time.sleep(3 * (attempt + 1))
            continue
        d = r.json()
        rows = []
        for x in d.get("data", []):
            rows.append((tag, kind, int(x["cik"]), x.get("start"), x["end"], x["val"], x.get("accn"), frame,
                         x.get("entityName")))
        return tag, frame, "ok", rows
    return tag, frame, "gave up", []


def main() -> int:
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS facts(
        tag TEXT, kind TEXT, cik INTEGER, start TEXT, end TEXT, val REAL, accn TEXT, frame TEXT, entity TEXT)""")
    con.execute("CREATE TABLE IF NOT EXISTS done(tag TEXT, frame TEXT, status TEXT, n INTEGER, PRIMARY KEY(tag, frame))")
    done = {(t, f) for t, f in con.execute("SELECT tag, frame FROM done")}
    jobs = []
    for tag, uom in DURATIONS.items():
        for y in YEARS:
            f = f"CY{y}"
            if (tag, f) not in done:
                jobs.append((tag, uom, f, "duration"))
    for tag, uom in INSTANTS.items():
        for y in YEARS:
            for q in (1, 2, 3, 4):
                f = f"CY{y}Q{q}I"
                if (tag, f) not in done:
                    jobs.append((tag, uom, f, "instant"))
    print(f"{len(jobs)} frames to fetch ({len(done)} already done)", flush=True)
    t0 = time.time()
    n_ok = 0
    with ThreadPoolExecutor(max_workers=3) as ex, LOG.open("a", encoding="utf-8") as log:
        for i, (tag, frame, status, rows) in enumerate(ex.map(lambda j: fetch_one(*j), jobs), 1):
            if rows:
                con.executemany("INSERT INTO facts VALUES (?,?,?,?,?,?,?,?,?)", rows)
            con.execute("INSERT OR REPLACE INTO done VALUES (?,?,?,?)", (tag, frame, status, len(rows)))
            if status == "ok":
                n_ok += 1
            log.write(f"{tag}\t{frame}\t{status}\t{len(rows)}\n")
            if i % 50 == 0:
                con.commit()
                print(f"{i}/{len(jobs)} frames, {n_ok} ok, {time.time() - t0:.0f}s", flush=True)
    con.commit()
    con.execute("CREATE INDEX IF NOT EXISTS ix_cik ON facts(cik, tag, end)")
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    print(f"done: {n} facts in {DB.name}, {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
