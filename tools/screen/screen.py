#!/usr/bin/env python3
"""SixGates pre-analysis screen (K1 to K5, quantitative part) over SEC XBRL frames.

Input: frames.db (fetch_frames.py) and universe.json (S&P 500 plus Nasdaq-listed SEC filers).
Output: screen_all.csv (one row per company: ten-year metrics, filter states, flags) and
funnel.json. Thresholds are the "parametru propus" values of the framework (section 13):
  K1  fewer than 7 fiscal years, or more than 2 loss years in the last 10        -> respinge
  K3  median ROE (net income / beginning equity) below 12%                        -> respinge
  K4  net debt above 5 x (CFO - capex), or interest cover below 3                 -> respinge
  K5  diluted shares CAGR above 2%/yr over 5 years, or SBC above 10% of revenue   -> respinge
  K2  indicator only: R&D above 15% of revenue, revenue deviation above 20% in a year
  K7  applied later from SIC / GICS (banks, insurers, REITs, blank checks)
Nothing is estimated: a missing input leaves the metric None and the filter "neclar".
"""
from __future__ import annotations

import csv
import json
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
TODAY = date(2026, 11, 5)
WINDOW = 10

REV_TAGS = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax"]
NI_TAGS = ["NetIncomeLoss", "ProfitLoss"]
CFO_TAGS = ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]
CAPEX_TAGS = ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"]
DA_TAGS = ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet"]
SBC_TAGS = ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"]
RD_TAGS = ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]
INT_TAGS = ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt", "InterestPaidNet", "InterestPaid"]
EQ_TAGS = ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]
DIV_TAGS = ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"]


def d(s: str) -> date:
    return date.fromisoformat(s)


def near(a: str, b: str, days: int = 10) -> bool:
    return abs((d(a) - d(b)).days) <= days


def pick(facts_by_tag: dict, tags: list[str], end: str, kind: str):
    """First tag with a fact ending within 10 days of `end`; returns (value, tag, accn)."""
    for t in tags:
        for f in facts_by_tag.get(t, []):
            if near(f["end"], end) and (kind == "instant" or (f["start"] and 330 <= (d(f["end"]) - d(f["start"])).days <= 380)):
                return f["val"], t, f["accn"]
    return None, None, None


def cagr(a, b, years):
    if a is None or b is None or a <= 0 or b <= 0 or years <= 0:
        return None
    return (b / a) ** (1 / years) - 1


def load_company(con, cik: int) -> dict:
    facts = defaultdict(list)
    for tag, kind, start, end, val, accn in con.execute(
            "SELECT tag, kind, start, end, val, accn FROM facts WHERE cik=?", (cik,)):
        facts[tag].append({"kind": kind, "start": start, "end": end, "val": val, "accn": accn})
    return facts


def fiscal_years(facts) -> list[str]:
    """Fiscal year ends from annual net-income facts (one per year, latest filed wins)."""
    ends = {}
    for t in NI_TAGS:
        for f in facts.get(t, []):
            if f["start"] and 330 <= (d(f["end"]) - d(f["start"])).days <= 380 and d(f["end"]) <= TODAY:
                key = (d(f["end"]).year, d(f["end"]).month)
                ends.setdefault(key, f["end"])
    out = sorted(set(ends.values()))
    if out:
        from collections import Counter
        months = Counter(d(e).month for e in out)
        mode_m = months.most_common(1)[0][0]
        out = [e for e in out if min(abs(d(e).month - mode_m), 12 - abs(d(e).month - mode_m)) <= 1]
    # drop duplicates within 20 days (52/53-week year labels)
    dedup = []
    for e in out:
        if not dedup or (d(e) - d(dedup[-1])).days > 20:
            dedup.append(e)
    return dedup


def debt_at(facts, end):
    g = lambda tag: pick(facts, [tag], end, "instant")[0]
    ltd_nc, ltd_c, cur, stb, cp = (g("LongTermDebtNoncurrent"), g("LongTermDebtCurrent"), g("DebtCurrent"),
                                   g("ShortTermBorrowings"), g("CommercialPaper"))
    ltd_total, lease_total, lease_cur = g("LongTermDebt"), g("LongTermDebtAndCapitalLeaseObligations"), g(
        "LongTermDebtAndCapitalLeaseObligationsCurrent")
    tags = []
    if cur is not None:
        current = cur; tags.append("DebtCurrent")
    else:
        current = sum(x for x in (ltd_c, stb, cp) if x is not None)
        tags += [n for n, x in (("LongTermDebtCurrent", ltd_c), ("ShortTermBorrowings", stb), ("CommercialPaper", cp)) if x is not None]
    if ltd_nc is not None:
        noncurrent = ltd_nc; tags.append("LongTermDebtNoncurrent")
    elif ltd_total is not None:
        noncurrent = max(ltd_total - (ltd_c or 0), 0) if ltd_c is not None else ltd_total
        tags.append("LongTermDebt")
    elif lease_total is not None:
        noncurrent = lease_total; tags.append("LongTermDebtAndCapitalLeaseObligations")
        if lease_cur is not None and cur is None:
            current += lease_cur; tags.append("LongTermDebtAndCapitalLeaseObligationsCurrent")
    else:
        noncurrent = None
    if noncurrent is None and not tags:
        g2 = lambda tag: pick(facts, [tag], end, "instant")[0]
        for t in ("LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", "DebtLongtermAndShorttermCombinedAmount"):
            v = g2(t)
            if v is not None:
                return v, t
        parts = [(t, g2(t)) for t in ("LongTermNotesPayable", "NotesPayable", "ConvertibleNotesPayable", "ConvertibleDebtNoncurrent",
                                       "ConvertibleDebtCurrent", "SeniorNotes", "LongTermLineOfCredit", "LineOfCredit",
                                       "OtherLongTermDebtNoncurrent")]
        parts = [(t, v) for t, v in parts if v is not None]
        if parts:
            return sum(v for _, v in parts), "+".join(t for t, _ in parts)
        return None, "no debt tags"
    return (noncurrent or 0) + current, "+".join(tags)


def cash_at(facts, end):
    g = lambda tag: pick(facts, [tag], end, "instant")[0]
    both = g("CashCashEquivalentsAndShortTermInvestments")
    if both is not None:
        return both, "CashCashEquivalentsAndShortTermInvestments"
    cash = g("CashAndCashEquivalentsAtCarryingValue")
    tag = "CashAndCashEquivalentsAtCarryingValue"
    if cash is None:
        cash = g("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents")
        tag = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents (include numerar restricționat)"
    if cash is None:
        return None, "no cash tag"
    sti = g("ShortTermInvestments")
    if sti is None:
        sti = g("MarketableSecuritiesCurrent")
        if sti is not None:
            tag += "+MarketableSecuritiesCurrent"
    else:
        tag += "+ShortTermInvestments"
    if sti is None:
        sti = g("AvailableForSaleSecuritiesDebtSecuritiesCurrent")
        if sti is not None:
            tag += "+AvailableForSaleSecuritiesDebtSecuritiesCurrent"
    return cash + (sti or 0), tag


def analyse(facts) -> dict | None:
    fys = fiscal_years(facts)
    if not fys:
        return None
    years_available = len(fys)
    win = fys[-WINDOW:]
    rows = []
    for e in win:
        r = {"end": e}
        r["rev"], r["rev_tag"], _ = pick(facts, REV_TAGS, e, "duration")
        r["ni"], _, r["ni_accn"] = pick(facts, NI_TAGS, e, "duration")
        r["opinc"], _, _ = pick(facts, ["OperatingIncomeLoss"], e, "duration")
        r["cfo"], _, _ = pick(facts, CFO_TAGS, e, "duration")
        r["capex"], _, _ = pick(facts, CAPEX_TAGS, e, "duration")
        r["da"], _, _ = pick(facts, DA_TAGS, e, "duration")
        r["sbc"], _, _ = pick(facts, SBC_TAGS, e, "duration")
        r["rd"], _, _ = pick(facts, RD_TAGS, e, "duration")
        r["interest"], _, _ = pick(facts, INT_TAGS, e, "duration")
        r["shares"], _, _ = pick(facts, ["WeightedAverageNumberOfDilutedSharesOutstanding"], e, "duration")
        r["buyback"], _, _ = pick(facts, ["PaymentsForRepurchaseOfCommonStock"], e, "duration")
        r["div"], _, _ = pick(facts, DIV_TAGS, e, "duration")
        r["equity"], _, _ = pick(facts, EQ_TAGS, e, "instant")
        r["cash"], r["cash_tag"] = cash_at(facts, e)
        r["debt"], r["debt_tag"] = debt_at(facts, e)
        rows.append(r)
    # beginning equity for the first window year
    prev_end = fys[-WINDOW - 1] if len(fys) > WINDOW else None
    prev_eq = pick(facts, EQ_TAGS, prev_end, "instant")[0] if prev_end else None

    ni = [r["ni"] for r in rows]
    loss_years = sum(1 for x in ni if x is not None and x <= 0)
    ni_missing = sum(1 for x in ni if x is None)
    # ROE on beginning equity
    roes, neg_eq = [], 0
    for i, r in enumerate(rows):
        beq = rows[i - 1]["equity"] if i > 0 else prev_eq
        if r["ni"] is None or beq is None:
            continue
        if beq <= 0:
            neg_eq += 1
            continue
        roes.append(r["ni"] / beq)
    roe_med = statistics.median(roes) if roes else None
    last = rows[-1]
    fcf_last = (last["cfo"] - last["capex"]) if last["cfo"] is not None and last["capex"] is not None else (
        last["cfo"] if last["cfo"] is not None and last["capex"] is None else None)
    capex_missing_last = last["cfo"] is not None and last["capex"] is None
    debt_untagged = last["debt"] is None and last["cash"] is not None and last["equity"] is not None
    net_debt = ((last["debt"] or 0) - last["cash"]) if (last["debt"] is not None or debt_untagged) and last["cash"] is not None else None
    nd_ratio = None
    if net_debt is not None and fcf_last is not None:
        nd_ratio = net_debt / fcf_last if fcf_last > 0 else (float("inf") if net_debt > 0 else 0.0)
    cover = None
    if last["opinc"] is not None and last["interest"] is not None and last["interest"] > 0:
        cover = last["opinc"] / last["interest"]
    sh = [r["shares"] for r in rows]
    split_flags = []
    for i in range(1, len(sh)):
        if sh[i] and sh[i - 1]:
            ratio = sh[i] / sh[i - 1]
            for m in (1.5, 2, 3, 4, 5, 7, 10, 20):
                if abs(ratio / m - 1) <= 0.12:
                    for j in range(i):
                        if sh[j]:
                            sh[j] *= m
                    split_flags.append(f"{rows[i]['end'][:4]}: salt {m}x în acțiuni (split sau scară; ajustat)")
                    break
                if abs(ratio * m - 1) <= 0.12:
                    for j in range(i):
                        if sh[j]:
                            sh[j] /= m
                    split_flags.append(f"{rows[i]['end'][:4]}: scădere {m}x în acțiuni (split invers sau scară; ajustat)")
                    break
    sh_cagr5 = cagr(sh[-6], sh[-1], 5) if len(sh) >= 6 else None
    sh_cagr10 = cagr(sh[0], sh[-1], len(sh) - 1) if len(sh) >= 2 else None
    sbc_rev = (last["sbc"] / last["rev"]) if last["sbc"] is not None and last["rev"] else None
    rd_rev = (last["rd"] / last["rev"]) if last["rd"] is not None and last["rev"] else None
    revs = [r["rev"] for r in rows]
    rev_cagr = cagr(revs[0], revs[-1], len(revs) - 1) if len(revs) >= 2 else None
    rev_dev = None
    if all(x is not None and x > 0 for x in revs) and len(revs) >= 3:
        rev_dev = max(abs(revs[i] / revs[i - 1] - 1) for i in range(1, len(revs)))
    fcfs = [(r["cfo"] - r["capex"]) for r in rows if r["cfo"] is not None and r["capex"] is not None]
    fcf_margins = [(r["cfo"] - r["capex"]) / r["rev"] for r in rows
                   if r["cfo"] is not None and r["capex"] is not None and r["rev"]]
    op_margins = [r["opinc"] / r["rev"] for r in rows if r["opinc"] is not None and r["rev"]]
    oe_low = [(r["ni"] + (r["da"] or 0) - r["capex"]) for r in rows
              if r["ni"] is not None and r["capex"] is not None]
    oe_cagr = cagr(oe_low[0], oe_low[-1], len(oe_low) - 1) if len(oe_low) >= 2 else None
    capex_cfo = statistics.median([r["capex"] / r["cfo"] for r in rows if r["capex"] is not None and r["cfo"]]) if any(
        r["capex"] is not None and r["cfo"] for r in rows) else None
    buyback_last = last["buyback"]

    # filter states
    if years_available < 7:
        k1 = "respinge (sub 7 exerciții)"
    elif ni_missing > 2:
        k1 = "neclar (profit net lipsă)"
    elif loss_years > 2:
        k1 = "respinge"
    else:
        k1 = "trece" if years_available >= WINDOW else "trece (istoric scurt)"
    if roe_med is None:
        k3 = "neclar (capital propriu negativ)" if neg_eq >= 3 and loss_years == 0 else "neclar"
    else:
        k3 = "respinge" if roe_med < 0.12 else "trece"
        if neg_eq >= 3:
            k3 += " (ani cu capital negativ)"
    if net_debt is None:
        k4 = "neclar (datorie sau numerar lipsă)"
    elif net_debt <= 0:
        k4 = "trece (numerar net)" + (" (fără etichete de datorie)" if debt_untagged else "")
    elif nd_ratio is not None and nd_ratio > 5:
        k4 = "respinge"
    elif cover is not None and cover < 3:
        k4 = "respinge"
    elif cover is None and nd_ratio is not None and nd_ratio <= 1:
        k4 = "trece (dobânzi nedisponibile, datorie netă sub 1x FCF)"
    elif cover is None:
        k4 = "neclar (dobânzi lipsă, datorie netă pozitivă)"
    else:
        k4 = "trece"
    if sh_cagr5 is None and sbc_rev is None:
        k5 = "neclar"
    elif (sh_cagr5 is not None and sh_cagr5 > 0.02) or (sbc_rev is not None and sbc_rev > 0.10):
        k5 = "respinge"
    else:
        k5 = "trece"
    k2_flags = []
    if rd_rev is not None and rd_rev > 0.15:
        k2_flags.append(f"R&D {rd_rev:.0%} din venituri")
    if rev_dev is not None and rev_dev > 0.20:
        k2_flags.append(f"abatere venituri {rev_dev:.0%} într-un an")
    return {
        "years_available": years_available, "fy_first": win[0], "fy_last": win[-1],
        "loss_years": loss_years, "ni_missing": ni_missing,
        "roe_median": roe_med, "roe_years": len(roes), "neg_equity_years": neg_eq,
        "rev_last": last["rev"], "rev_tag": last["rev_tag"], "rev_cagr": rev_cagr, "rev_max_dev": rev_dev,
        "ni_last": last["ni"], "opinc_last": last["opinc"], "cfo_last": last["cfo"], "capex_last": last["capex"],
        "fcf_last": fcf_last, "capex_missing_last": capex_missing_last,
        "cash_last": last["cash"], "cash_tag": last["cash_tag"], "debt_last": last["debt"], "debt_tag": last["debt_tag"],
        "net_debt": net_debt, "nd_to_fcf": nd_ratio, "interest_last": last["interest"], "cover": cover,
        "shares_cagr5": sh_cagr5, "shares_cagr10": sh_cagr10, "sbc_to_rev": sbc_rev, "rd_to_rev": rd_rev,
        "fcf_margin_median": statistics.median(fcf_margins) if fcf_margins else None,
        "op_margin_median": statistics.median(op_margins) if op_margins else None,
        "op_margin_min": min(op_margins) if op_margins else None,
        "oe_low_last": oe_low[-1] if oe_low else None, "oe_low_cagr": oe_cagr, "capex_to_cfo_median": capex_cfo,
        "buyback_last": buyback_last, "div_last": last["div"], "equity_last": last["equity"],
        "K1": k1, "K2_flags": "; ".join(k2_flags), "K3": k3, "K4": k4, "K5": k5,
        "share_flags": "; ".join(split_flags), "debt_untagged": debt_untagged,
        "ni_accn_last": last["ni_accn"],
    }


def main() -> int:
    con = sqlite3.connect(HERE / "frames.db")
    uni = json.load(open(HERE / "universe.json", encoding="utf-8"))
    out, funnel = [], defaultdict(int)
    for u in uni:
        facts = load_company(con, u["cik"])
        funnel["universe"] += 1
        a = analyse(facts) if facts else None
        row = {"cik": u["cik"], "name": u["name"], "tickers": "|".join(u["tickers"]), "exchanges": "|".join(u["exchanges"]),
               "sp500": u["sp500"], "gics_sector": u["gics_sector"], "gics_sub": u["gics_sub"]}
        if a is None:
            row.update({"K1": "fără fapte XBRL anuale (nu depune 10-K sau nu e emitent operațional)"})
            funnel["no_annual_facts"] += 1
        else:
            row.update(a)
            funnel["with_facts"] += 1
            if a["K1"].startswith("trece"):
                funnel["K1_pass"] += 1
                if a["K3"].startswith("trece"):
                    funnel["K1_K3_pass"] += 1
                    if a["K4"].startswith("trece"):
                        funnel["K1_K3_K4_pass"] += 1
                        if a["K5"].startswith("trece"):
                            funnel["K1_K3_K4_K5_pass"] += 1
        out.append(row)
    fields = list(out[0].keys())
    for r in out:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(HERE / "screen_all.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in out:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    json.dump(funnel, open(HERE / "funnel.json", "w"), indent=1)
    print(json.dumps(funnel, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
