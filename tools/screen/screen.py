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
import os
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(os.environ.get("SIXGATES_SCREEN_DIR", Path(__file__).resolve().parent))
TODAY = date.today()
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
ISSUE_TAGS = ["ProceedsFromIssuanceOfCommonStock", "ProceedsFromStockOptionsExercised",
              "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlans"]
EXCESS_CASH_PCT = 0.02      # numerar peste 2% din venituri = excedentar (parametru propus)
NEGLIGIBLE_CAPITAL_PCT = 0.05  # capital tangibil sub 5% din venituri sau negativ = neglijabil (parametru propus)
ROIC_PASS = 0.15            # K3 pe ROIC tangibil median (parametru propus)
SHORT, LONG = 3, 7          # fereastra scurtă față de cea lungă


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
    g2 = lambda tag: pick(facts, [tag], end, "instant")[0]
    if noncurrent is None:
        # the noncurrent part may sit under notes or senior-notes tags (Oracle: LongTermNotesPayable)
        parts = [(t, g2(t)) for t in ("LongTermNotesPayable", "NotesPayable", "ConvertibleNotesPayable", "ConvertibleDebtNoncurrent",
                                       "SeniorNotes", "LongTermLineOfCredit", "LineOfCredit", "OtherLongTermDebtNoncurrent")]
        parts = [(t, v) for t, v in parts if v is not None]
        if parts:
            noncurrent = sum(v for _, v in parts)
            tags += [t for t, _ in parts]
        if cur is None:
            v = g2("ConvertibleDebtCurrent")
            if v is not None:
                current += v
                tags.append("ConvertibleDebtCurrent")
    # a combined total, when tagged, is the most complete figure: take it if it exceeds the parts
    combined = None
    for t in ("DebtLongtermAndShorttermCombinedAmount", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"):
        v = g2(t)
        if v is not None:
            combined = v if combined is None else max(combined, v)
    parts_total = (noncurrent or 0) + current if (noncurrent is not None or tags) else None
    if combined is not None and (parts_total is None or combined > parts_total):
        return combined, "DebtLongtermAndShorttermCombinedAmount" if g2("DebtLongtermAndShorttermCombinedAmount") == combined else "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"
    if parts_total is None:
        return None, "no debt tags"
    return parts_total, "+".join(tags)


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
        r["pretax"], _, _ = pick(facts, ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"], e, "duration")
        r["tax"], _, _ = pick(facts, ["IncomeTaxExpenseBenefit"], e, "duration")
        r["depr"], _, _ = pick(facts, ["Depreciation"], e, "duration")
        r["amort_intang"], _, _ = pick(facts, ["AmortizationOfIntangibleAssets"], e, "duration")
        r["issuance"] = sum(v for v in (pick(facts, [t], e, "duration")[0] for t in ISSUE_TAGS) if v is not None) \
            if any(pick(facts, [t], e, "duration")[0] is not None for t in ISSUE_TAGS) else None
        r["assets_cur"], _, _ = pick(facts, ["AssetsCurrent"], e, "instant")
        r["liab_cur"], _, _ = pick(facts, ["LiabilitiesCurrent"], e, "instant")
        r["ppe"], _, _ = pick(facts, ["PropertyPlantAndEquipmentNet"], e, "instant")
        r["goodwill"], _, _ = pick(facts, ["Goodwill"], e, "instant")
        r["intang"], _, _ = pick(facts, ["IntangibleAssetsNetExcludingGoodwill"], e, "instant")
        r["debt_cur"] = pick(facts, ["DebtCurrent"], e, "instant")[0]
        if r["debt_cur"] is None:
            parts = [pick(facts, [t], e, "instant")[0] for t in ("LongTermDebtCurrent", "ShortTermBorrowings", "CommercialPaper")]
            r["debt_cur"] = sum(v for v in parts if v is not None) if any(v is not None for v in parts) else 0.0
        # capital investit tangibil la sfârșitul anului: capital de lucru net fără numerar excedentar și fără datoria
        # curentă purtătoare de dobândă, plus imobilizări corporale nete (alte active operaționale: nedisponibile în frames)
        if r["assets_cur"] is not None and r["liab_cur"] is not None and r["ppe"] is not None and r["cash"] is not None:
            excess = max(r["cash"] - EXCESS_CASH_PCT * (r["rev"] or 0), 0.0) if r["rev"] else r["cash"]
            r["cap_tang"] = (r["assets_cur"] - excess) - (r["liab_cur"] - (r["debt_cur"] or 0)) + r["ppe"]
            r["cap_with_gw"] = r["cap_tang"] + (r["goodwill"] or 0) + (r["intang"] or 0)
        else:
            r["cap_tang"] = r["cap_with_gw"] = None
        # NOPAT = profit operațional × (1 minus rata efectivă, limitată la 0 la 50%)
        if r["opinc"] is not None and r["pretax"] and r["tax"] is not None:
            t = r["tax"] / r["pretax"] if r["pretax"] > 0 else None
            r["tax_rate"] = min(max(t, 0.0), 0.5) if t is not None else None
            r["tax_clamped"] = t is not None and (t < 0 or t > 0.5)
        else:
            r["tax_rate"], r["tax_clamped"] = None, False
        r["nopat"] = r["opinc"] * (1 - r["tax_rate"]) if r["opinc"] is not None and r["tax_rate"] is not None else None
        rows.append(r)
    # beginning equity for the first window year
    prev_end = fys[-WINDOW - 1] if len(fys) > WINDOW else None
    prev_eq = pick(facts, EQ_TAGS, prev_end, "instant")[0] if prev_end else None
    prev_cap = prev_cap_gw = None
    if prev_end:
        pa, pl, pp = (pick(facts, [t], prev_end, "instant")[0] for t in ("AssetsCurrent", "LiabilitiesCurrent", "PropertyPlantAndEquipmentNet"))
        pc, _ = cash_at(facts, prev_end)
        pdc = pick(facts, ["DebtCurrent"], prev_end, "instant")[0] or 0.0
        prev_rev = pick(facts, REV_TAGS, prev_end, "duration")[0]
        if None not in (pa, pl, pp, pc):
            excess = max(pc - EXCESS_CASH_PCT * (prev_rev or 0), 0.0) if prev_rev else pc
            prev_cap = (pa - excess) - (pl - pdc) + pp
            prev_cap_gw = prev_cap + (pick(facts, ["Goodwill"], prev_end, "instant")[0] or 0) + (pick(facts, ["IntangibleAssetsNetExcludingGoodwill"], prev_end, "instant")[0] or 0)

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
    roics, roics_gw, negligible_years, roic_states = [], [], 0, []
    for i, r in enumerate(rows):
        bcap = rows[i - 1]["cap_tang"] if i > 0 else prev_cap
        bcap_gw = rows[i - 1]["cap_with_gw"] if i > 0 else prev_cap_gw
        if r["nopat"] is None or bcap is None:
            roic_states.append(None)
            continue
        if bcap <= 0 or (r["rev"] and bcap < NEGLIGIBLE_CAPITAL_PCT * r["rev"]):
            if r["nopat"] > 0:
                negligible_years += 1
                roic_states.append("neglijabil")
            else:
                roic_states.append("neglijabil, NOPAT negativ")
            continue
        roics.append(r["nopat"] / bcap)
        roic_states.append(r["nopat"] / bcap)
        if bcap_gw and bcap_gw > 0:
            roics_gw.append(r["nopat"] / bcap_gw)
    roic_med = statistics.median(roics) if roics else None
    roic_gw_med = statistics.median(roics_gw) if roics_gw else None
    last = rows[-1]
    def fcf_adj(r):
        """CFO minus SBC (added back in CFO, but a real cost) minus capex; None when CFO or capex is missing."""
        if r["cfo"] is None or r["capex"] is None:
            return None
        return r["cfo"] - (r["sbc"] or 0) - r["capex"]
    fcf_last = fcf_adj(last)
    fcf_gross_last = (last["cfo"] - last["capex"]) if last["cfo"] is not None and last["capex"] is not None else None
    sbc_missing_last = last["cfo"] is not None and last["sbc"] is None
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
    def grew(a, b, pct=0.30):
        return a is not None and b is not None and a > 0 and b / a - 1 > pct
    for i in range(1, len(sh)):
        if not (sh[i] and sh[i - 1]):
            continue
        ratio = sh[i] / sh[i - 1]
        if 0.74 < ratio < 1.35:
            continue
        yr = rows[i]["end"][:4]
        issuance_like = grew(rows[i - 1]["equity"], rows[i]["equity"]) or grew(rows[i - 1]["rev"], rows[i]["rev"])
        handled = False
        for m in (2, 3, 4, 5, 7, 10, 20, 1.5):
            exact_up, loose_up = abs(ratio / m - 1) <= 0.03 and m != 1.5, abs(ratio / m - 1) <= 0.12
            exact_dn, loose_dn = abs(ratio * m - 1) <= 0.03 and m != 1.5, abs(ratio * m - 1) <= 0.12
            if exact_up or (loose_up and not issuance_like):
                for j in range(i):
                    if sh[j]:
                        sh[j] *= m
                split_flags.append(f"{yr}: salt {m:g}x în acțiuni, raport rotund{' fără salt de capital sau venituri' if not exact_up else ''}: split sau scară; ajustat")
                handled = True
                break
            if exact_dn or (loose_dn and not grew(rows[i]["equity"], rows[i - 1]["equity"])):
                for j in range(i):
                    if sh[j]:
                        sh[j] /= m
                split_flags.append(f"{yr}: scădere {m:g}x în acțiuni: split invers sau scară; ajustat")
                handled = True
                break
        if not handled:
            if ratio > 1 and issuance_like:
                split_flags.append(f"{yr}: emisiune de acțiuni {ratio:.2f}x (capital propriu sau venituri cu peste 30% mai mari): fuziune sau majorare; neajustat, intră în diluare")
            elif ratio > 1:
                split_flags.append(f"{yr}: salt {ratio:.2f}x în acțiuni neexplicat; neajustat, intră în diluare; verificare")
            else:
                split_flags.append(f"{yr}: scădere {1 / ratio:.2f}x în acțiuni (răscumpărare masivă sau scindare); neajustat")
    sh_cagr5 = cagr(sh[-6], sh[-1], 5) if len(sh) >= 6 else None
    sh_cagr10 = cagr(sh[0], sh[-1], len(sh) - 1) if len(sh) >= 2 else None
    sbc_rev = (last["sbc"] / last["rev"]) if last["sbc"] is not None and last["rev"] else None
    rd_rev = (last["rd"] / last["rev"]) if last["rd"] is not None and last["rev"] else None
    revs = [r["rev"] for r in rows]
    rev_cagr = cagr(revs[0], revs[-1], len(revs) - 1) if len(revs) >= 2 else None
    rev_dev = None
    if all(x is not None and x > 0 for x in revs) and len(revs) >= 3:
        rev_dev = max(abs(revs[i] / revs[i - 1] - 1) for i in range(1, len(revs)))
    fcf_margins = [fcf_adj(r) / r["rev"] for r in rows if fcf_adj(r) is not None and r["rev"]]
    op_margins = [r["opinc"] / r["rev"] for r in rows if r["opinc"] is not None and r["rev"]]
    # OE_jos: tot capexul este menținere. OE_sus: menținerea este D&A tangibil (D&A minus amortizarea
    # necorporalelor dobândite), deci OE_sus = profit net + amortizarea necorporalelor; dacă capexul total este sub
    # D&A tangibil, menținerea nu poate depăși capexul, iar OE_sus = OE_jos.
    def oe_pair(r):
        if r["ni"] is None or r["capex"] is None:
            return None, None, None
        da = r["da"] or 0
        amort = r["amort_intang"] or 0
        da_tang = r["depr"] if r["depr"] is not None else max(da - amort, 0)
        maint = min(da_tang, r["capex"])
        return r["ni"] + da - r["capex"], r["ni"] + da - maint, da_tang
    oe_pairs = [oe_pair(r) for r in rows]
    oe_low = [p[0] for p in oe_pairs if p[0] is not None]
    oe_high = [p[1] for p in oe_pairs if p[1] is not None]
    oe_cagr = cagr(oe_low[0], oe_low[-1], len(oe_low) - 1) if len(oe_low) >= 2 else None
    oe_high_cagr = cagr(oe_high[0], oe_high[-1], len(oe_high) - 1) if len(oe_high) >= 2 else None
    da_tang_last = oe_pairs[-1][2] if oe_pairs and oe_pairs[-1][2] is not None else None
    capex_to_da = (last["capex"] / da_tang_last) if last["capex"] is not None and da_tang_last else None
    amort_missing = last["amort_intang"] is None and last["depr"] is None
    capex_cfo = statistics.median([r["capex"] / r["cfo"] for r in rows if r["capex"] is not None and r["cfo"]]) if any(
        r["capex"] is not None and r["cfo"] for r in rows) else None
    buyback_last = last["buyback"]
    net_buyback_last = (last["buyback"] - (last["issuance"] or 0)) if last["buyback"] is not None else None
    issuance_missing = last["buyback"] is not None and last["issuance"] is None
    price_per_retired = None
    if net_buyback_last and len(sh) >= 2 and sh[-2] and sh[-1] and sh[-2] > sh[-1]:
        price_per_retired = net_buyback_last / (sh[-2] - sh[-1])

    # direcția: ultimii SHORT ani față de precedenții LONG ani (indiciu, nu filtru)
    def seg_cagr(vals, i0, i1):
        if i1 - i0 < 1 or vals[i0] is None or vals[i1] is None:
            return None
        return cagr(vals[i0], vals[i1], i1 - i0)
    def seg_median(vals, i0, i1):
        v = [x for x in vals[i0:i1 + 1] if x is not None]
        return statistics.median(v) if v else None
    n = len(rows)
    direction = {}
    if n >= SHORT + 3:
        cut = n - 1 - SHORT  # index of the year that starts the short window
        opm = [r["opinc"] / r["rev"] if r["opinc"] is not None and r["rev"] else None for r in rows]
        roe_series = []
        for i, r in enumerate(rows):
            beq = rows[i - 1]["equity"] if i > 0 else prev_eq
            roe_series.append(r["ni"] / beq if r["ni"] is not None and beq and beq > 0 else None)
        roic_series = [x if isinstance(x, float) else None for x in roic_states]
        oe_series = [p[0] for p in oe_pairs]
        direction = {
            "rev_cagr_short": seg_cagr(revs, cut, n - 1), "rev_cagr_long": seg_cagr(revs, 0, cut),
            "op_margin_short": seg_median(opm, cut + 1, n - 1), "op_margin_long": seg_median(opm, 0, cut),
            "roe_short": seg_median(roe_series, cut + 1, n - 1), "roe_long": seg_median(roe_series, 0, cut),
            "roic_short": seg_median(roic_series, cut + 1, n - 1), "roic_long": seg_median(roic_series, 0, cut),
            "oe_cagr_short": seg_cagr(oe_series, cut, n - 1), "oe_cagr_long": seg_cagr(oe_series, 0, cut),
            "shares_cagr_short": seg_cagr(sh, cut, n - 1), "shares_cagr_long": seg_cagr(sh, 0, cut),
        }
    breaks = []
    def diff(a, b):
        return None if a is None or b is None else a - b
    def rp(x):  # Romanian percent, one decimal, explicit sign
        return ("+" if x > 0 else "") + f"{x * 100:.1f}".replace(".", ",") + "%"
    if direction:
        dv = diff(direction["rev_cagr_short"], direction["rev_cagr_long"])
        if dv is not None and dv <= -0.05:
            breaks.append(f"venituri {rp(direction['rev_cagr_short'])} pe an în ultimii {SHORT} ani față de {rp(direction['rev_cagr_long'])} în cei {LONG} dinainte")
        elif dv is not None and dv >= 0.05:
            breaks.append(f"venituri în accelerare: {rp(direction['rev_cagr_short'])} pe an față de {rp(direction['rev_cagr_long'])}")
        dm = diff(direction["op_margin_short"], direction["op_margin_long"])
        if dm is not None and dm <= -0.03:
            breaks.append(f"marja operațională mediană {rp(direction['op_margin_short']).lstrip('+')} față de {rp(direction['op_margin_long']).lstrip('+')}")
        dr = diff(direction["roic_short"], direction["roic_long"])
        if dr is None:
            dr = diff(direction["roe_short"], direction["roe_long"])
            label, dr_from, dr_to = "ROE", direction["roe_long"], direction["roe_short"]
        else:
            label, dr_from, dr_to = "ROIC tangibil", direction["roic_long"], direction["roic_short"]
        if dr is not None and dr <= -0.05:
            breaks.append(f"{label} în scădere cu {abs(dr) * 100:.0f} puncte (de la {rp(dr_from).lstrip('+')} la {rp(dr_to).lstrip('+')})")
        do = diff(direction["oe_cagr_short"], direction["oe_cagr_long"])
        if do is not None and do <= -0.05:
            breaks.append(f"OE_jos {rp(direction['oe_cagr_short'])} pe an față de {rp(direction['oe_cagr_long'])}")
        ds = diff(direction["shares_cagr_short"], direction["shares_cagr_long"])
        if ds is not None and ds >= 0.02:
            if direction["shares_cagr_short"] is not None and direction["shares_cagr_short"] > 0:
                breaks.append(f"diluare în creștere: acțiuni {rp(direction['shares_cagr_short'])} pe an față de {rp(direction['shares_cagr_long'])}")
            else:
                breaks.append(f"răscumpărări încetinite: acțiuni {rp(direction['shares_cagr_short'])} pe an față de {rp(direction['shares_cagr_long'])}")

    # filter states
    if years_available < 7:
        k1 = "respinge (sub 7 exerciții)"
    elif ni_missing > 2:
        k1 = "neclar (profit net lipsă)"
    elif loss_years > 2:
        k1 = "respinge"
    else:
        k1 = "trece" if years_available >= WINDOW else "trece (istoric scurt)"
    roe_defined = roe_med is not None and len(roes) >= 5
    roic_defined = roic_med is not None and len(roics) >= 5
    negligible_ok = negligible_years >= 5 and loss_years <= 2
    passes = []
    if roe_defined and roe_med >= 0.12:
        passes.append(f"ROE median {roe_med:.0%}")
    if roic_defined and roic_med >= ROIC_PASS:
        passes.append(f"ROIC tangibil median {roic_med:.0%}")
    if negligible_ok:
        passes.append(f"capital tangibil neglijabil în {negligible_years} ani cu NOPAT pozitiv")
    if passes:
        k3 = "trece (" + "; ".join(passes) + ")"
    elif roe_defined or roic_defined:
        k3 = "respinge"
    else:
        k3 = "neclar (ROE nedefinit: capital propriu negativ)" if neg_eq >= 3 else "neclar (ROE și ROIC nedefinite)"
    if neg_eq >= 3 and not k3.startswith("neclar"):
        k3 += f"; ROE nedefinit în {neg_eq} ani (capital propriu sub zero)"
    if net_debt is None:
        k4 = "neclar (datorie sau numerar lipsă)"
    elif net_debt <= 0:
        k4 = "trece (numerar net)" + (" (fără etichete de datorie)" if debt_untagged else "")
    elif nd_ratio is not None and nd_ratio > 5:
        k4 = "respinge"
    elif cover is not None and cover < 3:
        k4 = "respinge"
    elif cover is None and nd_ratio is not None and nd_ratio <= 1:
        k4 = "trece (dobânzi nedisponibile, datorie netă sub 1x FCF după SBC)"
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
        "roic_tangible_median": roic_med, "roic_years": len(roics), "negligible_capital_years": negligible_years,
        "roic_with_goodwill_median": roic_gw_med, "cap_tangible_last": last["cap_tang"], "nopat_last": last["nopat"],
        "tax_clamped_last": last["tax_clamped"],
        "rev_last": last["rev"], "rev_tag": last["rev_tag"], "rev_cagr": rev_cagr, "rev_max_dev": rev_dev,
        "ni_last": last["ni"], "opinc_last": last["opinc"], "cfo_last": last["cfo"], "capex_last": last["capex"],
        "fcf_last": fcf_last, "fcf_gross_last": fcf_gross_last, "sbc_missing_last": sbc_missing_last,
        "capex_missing_last": capex_missing_last,
        "cash_last": last["cash"], "cash_tag": last["cash_tag"], "debt_last": last["debt"], "debt_tag": last["debt_tag"],
        "net_debt": net_debt, "nd_to_fcf": nd_ratio, "interest_last": last["interest"], "cover": cover,
        "shares_cagr5": sh_cagr5, "shares_cagr10": sh_cagr10, "sbc_to_rev": sbc_rev, "rd_to_rev": rd_rev,
        "fcf_margin_median": statistics.median(fcf_margins) if fcf_margins else None,
        "op_margin_median": statistics.median(op_margins) if op_margins else None,
        "op_margin_min": min(op_margins) if op_margins else None,
        "oe_low_last": oe_low[-1] if oe_low else None, "oe_low_cagr": oe_cagr, "capex_to_cfo_median": capex_cfo,
        "oe_high_last": oe_high[-1] if oe_high else None, "oe_high_cagr": oe_high_cagr,
        "da_last": last["da"], "da_tangible_last": da_tang_last, "amort_intangibles_last": last["amort_intang"],
        "capex_to_da_tangible": capex_to_da, "amort_missing": amort_missing,
        "buyback_last": buyback_last, "issuance_last": last["issuance"], "net_buyback_last": net_buyback_last,
        "issuance_missing": issuance_missing, "price_per_share_retired": price_per_retired,
        "div_last": last["div"], "equity_last": last["equity"],
        **{k: v for k, v in direction.items()}, "trend_breaks": "; ".join(breaks),
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
