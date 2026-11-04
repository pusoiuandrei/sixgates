#!/usr/bin/env python3
"""Build SixGates v2.2 analysis JSON files from the phase 1 spike outputs.

Input: spike/out/annual_us.csv (canonical annual facts per entity), spike/out/facts_us.csv
(provenance per fact id), spike/out/data_issues_us.csv.
Output: data/analyses/<TICKER>/<date>_v1.json, one per entity, following the schema in
dashboard/schema.md. Formulas follow the framework v2.2 (framework/cadru_v2.md):
owner earnings as a range, tangible ROIC with the "negligible capital" state,
no year-by-year working capital change, thresholds labelled as proposed parameters.

Nothing is estimated: a missing input yields status "lipsa" and the metric is null.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPIKE = ROOT / "spike" / "out"
OUT = ROOT / "data" / "analyses"

FRAMEWORK_VERSION = "2.2"
TODAY = date.today().isoformat()

NAMES = {
    "AAPL": ("Apple Inc.", "NASDAQ (SUA)", "septembrie"),
    "KO": ("The Coca-Cola Company", "NYSE (SUA)", "decembrie"),
    "MCO": ("Moody's Corporation", "NYSE (SUA)", "decembrie"),
}

LABELS = {
    "revenue": "Venituri",
    "operating_income": "Profit operațional",
    "pretax_income": "Profit înainte de impozit",
    "income_tax": "Impozit pe profit",
    "net_income": "Profit net",
    "d_and_a": "Deprecieri și amortizări (D&A)",
    "capex": "Capex (plăți pentru imobilizări)",
    "cfo": "Flux de numerar din exploatare (CFO)",
    "cash": "Numerar",
    "st_investments": "Investiții pe termen scurt",
    "st_borrowings": "Împrumuturi pe termen scurt",
    "ltd_current": "Datorie pe termen lung, partea curentă",
    "debt_long": "Datorie pe termen lung",
    "interest_expense": "Cheltuieli cu dobânzile",
    "equity": "Capital propriu",
    "goodwill": "Fond comercial",
    "intangibles": "Alte imobilizări necorporale",
    "current_assets": "Active curente",
    "current_liabilities": "Datorii curente",
    "ppe_net": "Imobilizări corporale nete",
    "diluted_shares": "Acțiuni diluate (medie ponderată)",
    "dividends_paid": "Dividende plătite",
    "share_repurchases": "Răscumpărări de acțiuni",
}
FACT_ORDER = [
    "revenue", "operating_income", "pretax_income", "income_tax", "net_income", "d_and_a", "capex",
    "cfo", "cash", "st_investments", "st_borrowings", "ltd_current", "debt_long", "interest_expense",
    "equity", "goodwill", "intangibles", "current_assets", "current_liabilities", "ppe_net",
    "diluted_shares", "dividends_paid", "share_repurchases",
]

# Proposed parameters (framework section 13). Instruments of ours, not their rules.
P = {
    "window_years": 10,
    "short_history_min": 7,
    "excess_cash_pct_of_revenue": 0.02,
    "negligible_capital_pct_of_revenue": 0.05,
    "tax_rate_min": 0.0,
    "tax_rate_max": 0.5,
    "hurdle_floor_usd": 0.06,
    "k3_roe_median_min": 0.12,
    "k4_net_debt_to_fcf_max": 5.0,
    "k4_interest_cover_min": 3.0,
    "k5_share_cagr_max": 0.02,
    "surv_pass_net_debt_to_oe": 2.0,
    "surv_fail_net_debt_to_oe": 5.0,
    "surv_pass_cover": 8.0,
    "surv_fail_cover": 1.0,
    "stress_oe_drop": 0.5,
    "stress_cover_min": 3.0,
    "stress_years_to_repay_max": 6.0,
    "instab_loss_years": 2,
    "instab_cv_oe": 0.5,
    "instab_revenue_deviation": 0.20,
    "moat_roic_years_min": 8,
    "moat_gross_margin_drop_pts": 3.0,
    "category_terrific_after_tax": 0.25,
    "category_good_after_tax_low": 0.12,
    "category_good_after_tax_high": 0.20,
}


def fnum(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except ValueError:
        return None


def load():
    annual = list(csv.DictReader(open(SPIKE / "annual_us.csv", encoding="utf-8")))
    facts = {r["fact_id"]: r for r in csv.DictReader(open(SPIKE / "facts_us.csv", encoding="utf-8"))}
    issues = list(csv.DictReader(open(SPIKE / "data_issues_us.csv", encoding="utf-8")))
    return annual, facts, issues


def series(annual, entity):
    """Return {concept: {year: (value, status, source_concepts, fact_ids, note)}}."""
    out = defaultdict(dict)
    for r in annual:
        if r["entity"] != entity:
            continue
        y = int(r["fiscal_year"])
        out[r["concept"]][y] = (fnum(r["value"]), r["status"], r["source_concepts"], r["fact_ids"], r["note"])
    return out


def val(s, concept, year):
    t = s.get(concept, {}).get(year)
    if not t:
        return None
    v, status = t[0], t[1]
    if status == "missing" or v is None:
        return None
    return v  # "ambiguous" keeps the latest-filed value; the facts table flags it "necesita_verificare"


def safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def cagr(first, last, years):
    if first is None or last is None or first <= 0 or last <= 0 or years <= 0:
        return None
    return (last / first) ** (1.0 / years) - 1.0


def r2(x, nd=2):
    return None if x is None else round(x, nd)


def ro(x, nd=2, sign=False):
    """Format a number with a Romanian decimal comma (strings only; JSON numbers stay numbers)."""
    if x is None:
        return "lipsă"
    t = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return t.replace(".", ",")


def sig2(x):
    """Two significant digits (framework precision rule)."""
    if x is None or x == 0:
        return x
    mag = math.floor(math.log10(abs(x)))
    return round(x, -(mag - 1))


def build(entity, annual, facts, issues):
    s = series(annual, entity)
    years_all = sorted({y for c in s.values() for y in c})
    split_notes = []
    sh = s.get("diluted_shares", {})
    ys = sorted(y for y in sh if sh[y][0])
    for a_, b_ in zip(ys, ys[1:]):
        ratio = sh[b_][0] / sh[a_][0]
        for f in (2, 3, 4, 5, 7, 10):
            if abs(ratio - f) / f < 0.12:
                for y in ys:
                    if y <= a_:
                        v, st, src, fids, note = sh[y]
                        sh[y] = (v * f, st, src, fids, (note + "; " if note else "") + f"ajustat x{f} pentru split detectat între FY{a_} și FY{b_}")
                split_notes.append(f"numărul de acțiuni diluate pentru FY{ys[0]} la FY{a_} a fost înmulțit cu {f}: salt de {ro(ratio, 2)}x între FY{a_} și FY{b_}, consistent cu un split {f}:1; de verificat în 10-K")
                break
    window = years_all[-P["window_years"]:]
    name, market, fy_end = NAMES[entity]
    cik = next(r["cik"] for r in annual if r["entity"] == entity)

    # ---- facts table with provenance -------------------------------------------------
    fact_rows = []
    accessions = {}
    for concept in FACT_ORDER:
        values, statuses, srcs = {}, {}, set()
        for y in window:
            t = s.get(concept, {}).get(y)
            if t is None:
                values[str(y)] = None
                statuses[str(y)] = "lipsa"
                continue
            v, status, src, fids, note = t
            if status == "missing" or v is None:
                values[str(y)] = None
                statuses[str(y)] = "lipsa"
            elif status == "ambiguous":
                values[str(y)] = v
                statuses[str(y)] = "necesita_verificare"
            else:
                values[str(y)] = v
                statuses[str(y)] = "ok" if status == "ok" else "suma_partiala"
            if src:
                srcs.update(src.split(";"))
            for fid in (fids or "").split(";"):
                f = facts.get(fid)
                if f:
                    accessions[f["accession"]] = (f["form"], f["filed"], f["source_url"])
        fact_rows.append({
            "concept": concept,
            "label": LABELS[concept],
            "register": "F",
            "unit": "USD" if concept != "diluted_shares" else "acțiuni",
            "values": values,
            "status": statuses,
            "source_tags": sorted(srcs),
        })

    # ---- helpers per year ---------------------------------------------------------
    def g(concept, y):
        return val(s, concept, y)

    calc = defaultdict(dict)   # metric -> year -> value
    flags = defaultdict(dict)  # metric -> year -> flag text

    def put(metric, y, value, flag=None):
        calc[metric][str(y)] = value
        if flag:
            flags[metric][str(y)] = flag

    for i, y in enumerate(window):
        ni, da, capex, rev, opi = g("net_income", y), g("d_and_a", y), g("capex", y), g("revenue", y), g("operating_income", y)
        cfo = g("cfo", y)
        # Owner earnings range (1986, corrected): low = NI + D&A - total capex; high = NI + D&A - max(D&A, Greenwald maintenance capex)
        if None not in (ni, da, capex):
            oe_low = ni + da - capex
            # Greenwald maintenance capex: capex minus growth capex, growth capex = delta revenue * (PPE/revenue, avg prior 3 years)
            prev = [yy for yy in years_all if yy < y][-3:]
            ratios = [safe_div(g("ppe_net", yy), g("revenue", yy)) for yy in prev]
            ratios = [r for r in ratios if r is not None]
            rev_prev = g("revenue", y - 1) if (y - 1) in years_all else None
            if ratios and rev is not None and rev_prev is not None:
                growth_capex = max(0.0, (rev - rev_prev) * (sum(ratios) / len(ratios)))
                maint = max(0.0, capex - growth_capex)
                oe_high = ni + da - max(da, maint)
                put("greenwald_maintenance_capex", y, maint)
            else:
                oe_high = None
                put("greenwald_maintenance_capex", y, None, "lipsă: fără istoric pentru estimarea Greenwald")
            put("oe_low", y, oe_low)
            put("oe_high", y, oe_high)
            put("fcf_simple", y, (cfo - capex) if cfo is not None else None)
            put("oe_conversion", y, safe_div(oe_low, ni) if ni and ni > 0 else None)
            sh = g("diluted_shares", y)
            put("oe_low_per_share", y, safe_div(oe_low, sh))
        else:
            for m in ("oe_low", "oe_high", "fcf_simple", "oe_conversion", "oe_low_per_share"):
                put(m, y, None, "lipsă: profit net, D&A sau capex")
        # NOPAT and tangible capital
        tax, pretax = g("income_tax", y), g("pretax_income", y)
        rate = safe_div(tax, pretax)
        rate_flag = None
        if rate is None:
            rate_flag = "lipsă: impozit sau profit înainte de impozit"
        elif not (P["tax_rate_min"] <= rate <= P["tax_rate_max"]):
            rate_flag = f"rata efectivă {rate:.2f} în afara intervalului 0 la 0,5; plafonată la limită, necesită verificare"
            rate = min(max(rate, P["tax_rate_min"]), P["tax_rate_max"])
        put("effective_tax_rate", y, rate, rate_flag)
        nopat = opi * (1 - rate) if (opi is not None and rate is not None) else None
        put("nopat", y, nopat)
        ca, cl, cash, sti = g("current_assets", y), g("current_liabilities", y), g("cash", y), g("st_investments", y)
        stb, ltdc, ppe, gw, intang = g("st_borrowings", y), g("ltd_current", y), g("ppe_net", y), g("goodwill", y), g("intangibles", y)
        stb0 = stb if stb is not None else 0.0
        ltdc0 = ltdc if ltdc is not None else 0.0
        sti0 = sti if sti is not None else 0.0
        if None not in (ca, cl, cash, ppe, rev):
            excess_cash = max(0.0, cash + sti0 - P["excess_cash_pct_of_revenue"] * rev)
            nwc = (ca - excess_cash) - (cl - stb0 - ltdc0)
            tangible = nwc + ppe
            put("tangible_capital", y, tangible)
            put("capital_with_goodwill", y, tangible + (gw or 0.0) + (intang or 0.0))
            if tangible <= P["negligible_capital_pct_of_revenue"] * rev:
                put("roic_tangible", y, None, "capital necesar neglijabil (capital tangibil sub 5% din venituri sau negativ): semnal pozitiv, procentul nu se forțează")
                put("oe_over_capex_plus_nwc", y, safe_div(calc["oe_low"].get(str(y)), (capex or 0.0) + max(nwc, 0.0)))
            else:
                put("roic_tangible", y, safe_div(nopat, tangible))
            cwg = tangible + (gw or 0.0) + (intang or 0.0)
            if cwg <= P["negligible_capital_pct_of_revenue"] * rev:
                put("roic_with_goodwill", y, None, "capital (inclusiv fond comercial) neglijabil față de venituri")
            else:
                put("roic_with_goodwill", y, safe_div(nopat, cwg))
        else:
            put("tangible_capital", y, None, "lipsă: active curente, datorii curente, numerar sau imobilizări")
            put("roic_tangible", y, None, "lipsă")
        eq_begin = g("equity", y - 1) if (y - 1) in years_all else None
        if eq_begin is not None and eq_begin > 0 and ni is not None:
            put("roe_begin_equity", y, ni / eq_begin)
        else:
            put("roe_begin_equity", y, None, "capital propriu de început lipsă sau nepozitiv")
        put("capex_to_revenue", y, safe_div(capex, rev))
        put("da_to_capex", y, safe_div(da, capex))
        put("operating_margin", y, safe_div(opi, rev))
        # survival
        debt = (g("debt_long", y) or 0.0) + ltdc0 + stb0
        if g("debt_long", y) is None and stb is None and ltdc is None:
            put("net_debt", y, None, "lipsă: datorie")
        else:
            net_debt = debt - ((cash or 0.0) + sti0)
            put("net_debt", y, net_debt)
            put("net_debt_to_oe_low", y, safe_div(net_debt, calc["oe_low"].get(str(y))) if (calc["oe_low"].get(str(y)) or 0) > 0 else None)
        ie = g("interest_expense", y)
        put("interest_cover", y, safe_div(opi, ie) if ie else None, None if ie else "lipsă: cheltuieli cu dobânzile neraportate separat")

    # ---- aggregates ---------------------------------------------------------------
    y0, y1 = window[0], window[-1]
    n = len(window) - 1
    oe_series = [calc["oe_low"].get(str(y)) for y in window]
    oe_clean = [v for v in oe_series if v is not None]
    loss_years = sum(1 for y in window if (g("net_income", y) or 0) < 0)
    rev_series = [g("revenue", y) for y in window]
    # revenue deviation from linear trend
    dev = None
    if all(v is not None for v in rev_series):
        xs = list(range(len(rev_series)))
        xm, ym = sum(xs) / len(xs), sum(rev_series) / len(rev_series)
        b = sum((x - xm) * (v - ym) for x, v in zip(xs, rev_series)) / sum((x - xm) ** 2 for x in xs)
        a = ym - b * xm
        dev = max(abs(v - (a + b * x)) / v for x, v in zip(xs, rev_series))
    cv_oe = (statistics.pstdev(oe_clean) / statistics.mean(oe_clean)) if len(oe_clean) >= 3 and statistics.mean(oe_clean) > 0 else None
    margins = [calc["operating_margin"].get(str(y)) for y in window]
    margins = [m for m in margins if m is not None]
    indicators = {
        "revenue_cagr_10y": cagr(rev_series[0], rev_series[-1], n),
        "revenue_max_deviation_from_trend": dev,
        "operating_margin_min": min(margins) if margins else None,
        "operating_margin_max": max(margins) if margins else None,
        "oe_low_cv": cv_oe,
        "loss_years": loss_years,
        "instability_flag": bool((loss_years >= P["instab_loss_years"]) or (cv_oe is not None and cv_oe > P["instab_cv_oe"]) or (dev is not None and dev > P["instab_revenue_deviation"])),
    }
    oe_cagr = cagr(oe_series[0], oe_series[-1], n) if oe_series[0] and oe_series[-1] else None

    def incremental(span):
        yb = window[-1]
        candidates = [y for y in window if y <= yb - span and calc["nopat"].get(str(y)) is not None and calc["tangible_capital"].get(str(y)) is not None]
        if not candidates:
            return {"value": None, "state": "lipsă: nu există an de start cu NOPAT și capital tangibil", "years": None}
        ya = max(candidates)
        na, nb = calc["nopat"].get(str(ya)), calc["nopat"].get(str(yb))
        ca_, cb_ = calc["tangible_capital"].get(str(ya)), calc["tangible_capital"].get(str(yb))
        if None in (na, nb, ca_, cb_):
            return {"value": None, "state": "lipsă", "years": f"{ya} la {yb}"}
        dn, dc = nb - na, cb_ - ca_
        rev_b = g("revenue", yb) or 0.0
        base = {"delta_nopat": dn, "delta_capital": dc, "years": f"{ya} la {yb}"}
        if dc <= 0 and dn > 0:
            return {"value": None, "state": "profit în creștere fără capital suplimentar (cel mai bun caz)", **base}
        if dc <= 0:
            return {"value": None, "state": "capital în scădere, profit în scădere: necesită judecată", **base}
        if dc < P["negligible_capital_pct_of_revenue"] * rev_b and dn > 0:
            return {"value": None, "state": "capital aproape neschimbat (sub 5% din venituri), profit în creștere: randament incremental foarte mare, procentul nu se forțează", **base}
        return {"value": dn / dc, "state": "calculat", **base}

    sh0, sh1 = g("diluted_shares", y0), g("diluted_shares", y1)
    share_cagr = cagr(sh0, sh1, n)
    roic_vals = [calc["roic_tangible"].get(str(y)) for y in window]
    negligible_years = sum(1 for y in window if "neglijabil" in flags["roic_tangible"].get(str(y), ""))
    roic_clean = [v for v in roic_vals if v is not None]
    hurdle = P["hurdle_floor_usd"]
    roic_above_hurdle_years = sum(1 for v in roic_vals if v is not None and v > hurdle) + negligible_years

    # ---- survival aggregates ------------------------------------------------------
    last = str(y1)
    nd_last = calc["net_debt"].get(last)
    oe_last = calc["oe_low"].get(last)
    oe_min = min(oe_clean) if oe_clean else None
    cover_last = calc["interest_cover"].get(last)
    opi_last = g("operating_income", y1)
    ie_last = g("interest_expense", y1)
    stress = {
        "assumption": f"OE scade cu {int(P['stress_oe_drop']*100)}% doi ani la rând (parametru propus)",
        "interest_cover_after_shock": (opi_last * (1 - P["stress_oe_drop"]) / ie_last) if (opi_last and ie_last) else None,
        "years_to_repay_net_debt": (nd_last / (oe_last * (1 - P["stress_oe_drop"]))) if (nd_last is not None and oe_last and nd_last > 0) else (0.0 if nd_last is not None and nd_last <= 0 else None),
        "maturities_5y": None,
        "maturities_note": "lipsă: scadențele pe cinci ani nu sunt în companyfacts; se completează din notele 10-K cu pagina",
    }
    nd_to_oe = safe_div(nd_last, oe_last) if (oe_last or 0) > 0 else None
    nd_to_oe_min = safe_div(nd_last, oe_min) if (oe_min or 0) > 0 else None

    def surv_verdict():
        if len(oe_clean) < P["short_history_min"]:
            return "date_insuficiente", "sub 7 exerciții cu OE"
        if nd_last is None:
            return "date_insuficiente", "datoria lipsește"
        if nd_last <= 0:
            base_ok = True
            base_txt = "datorie netă negativă (numerar peste datorii)"
        else:
            if (cover_last is not None and cover_last < P["surv_fail_cover"]) or (nd_to_oe is not None and nd_to_oe > P["surv_fail_net_debt_to_oe"]):
                return "pica", f"acoperirea dobânzilor {ro(cover_last, 1)}x sau datorie netă pe OE_jos {ro(nd_to_oe, 2)}x peste pragul de picare"
            base_ok = (nd_to_oe is not None and nd_to_oe <= P["surv_pass_net_debt_to_oe"]) and (cover_last is not None and cover_last >= P["surv_pass_cover"])
            base_txt = f"datorie netă pe OE_jos {ro(nd_to_oe, 2)}x; acoperirea dobânzilor {'lipsă (cheltuiala cu dobânzile neraportată separat în companyfacts)' if cover_last is None else ro(cover_last, 1) + 'x'}"
        s_ok = ((stress["interest_cover_after_shock"] is None) or stress["interest_cover_after_shock"] >= P["stress_cover_min"]) and \
               ((stress["years_to_repay_net_debt"] is None) or stress["years_to_repay_net_debt"] <= P["stress_years_to_repay_max"])
        if base_ok and s_ok:
            return "trece", base_txt + "; stresul trece; scadențele lipsă, de completat"
        if base_ok and not s_ok:
            return "necesita_judecata", base_txt + "; stresul nu trece"
        return "necesita_judecata", base_txt + " (între pragurile de trecere și de picare)"

    surv_v, surv_reason = surv_verdict()

    # ---- pre-analysis filters -----------------------------------------------------
    roe_vals = [calc["roe_begin_equity"].get(str(y)) for y in window]
    roe_clean = [v for v in roe_vals if v is not None]
    roe_median = statistics.median(roe_clean) if roe_clean else None
    fcf_last = calc["fcf_simple"].get(last)
    k4_ratio = safe_div(nd_last, fcf_last) if (fcf_last or 0) > 0 else None
    public_years = len(years_all)
    filters = [
        {"id": "K1", "name": "Record scurt sau inconsistent",
         "state": "respinge" if (public_years < P["short_history_min"] or loss_years > 2) else "trece",
         "fact": f"{public_years} exerciții în companyfacts ({years_all[0]} la {years_all[-1]}); {loss_years} ani cu pierdere în fereastra {y0} la {y1}",
         "source": "SEC EDGAR companyfacts; criteriile de achiziție Berkshire: demonstrated consistent earning power"},
        {"id": "K2", "name": "Industrie în schimbare rapidă",
         "state": "neclar",
         "fact": "necesită citirea secțiunilor Business și Risk Factors din ultimul 10-K; indiciile (cicluri de produs, R&D pe vânzări, concentrarea clienților) nu sunt în companyfacts",
         "source": "1992, 1996, 2007; judecata utilizatorului"},
        {"id": "K3", "name": "Randamente slabe pe capital",
         "state": ("neclar" if roe_median is None else ("respinge" if roe_median < P["k3_roe_median_min"] else "trece")),
         "fact": ("ROE median pe capitalul de început de an: " + (f"{ro(roe_median*100, 1)}%" if roe_median is not None else "lipsă (capital propriu nepozitiv sau lipsă)")) + f"; ani cu ROIC tangibil peste prag sau capital neglijabil: {roic_above_hurdle_years} din {len(window)}",
         "source": "1977, 1979; banda descriptivă 12 la 20% (2010 până la 2016)"},
        {"id": "K4", "name": "Datorie",
         "state": ("neclar" if (nd_last is None) else ("trece" if nd_last <= 0 else ("respinge" if ((k4_ratio is not None and k4_ratio > P["k4_net_debt_to_fcf_max"]) or (cover_last is not None and cover_last < P["k4_interest_cover_min"])) else "trece"))),
         "fact": f"datorie netă {('lipsă' if nd_last is None else ro(nd_last/1e9, 1) + ' mld USD')}; datorie netă pe (CFO minus capex) {('lipsă' if k4_ratio is None else ro(k4_ratio, 1) + 'x')}; acoperirea dobânzilor {('lipsă' if cover_last is None else ro(cover_last, 1) + 'x')} (FY{y1})",
         "source": "criteriile de achiziție: little or no debt; praguri propuse"},
        {"id": "K5", "name": "Diluare",
         "state": ("neclar" if share_cagr is None else ("respinge" if share_cagr > P["k5_share_cagr_max"] else "trece")),
         "fact": f"CAGR acțiuni diluate {y0} la {y1}: {('lipsă' if share_cagr is None else ro(share_cagr*100, 1, sign=True) + '% pe an')}; compensația în acțiuni: lipsă în extracție",
         "source": "Owner's Manual 10; 2014; 1992, 1998"},
        {"id": "K6", "name": "Candoare",
         "state": "neclar",
         "fact": "necesită citirea ultimului comunicat de rezultate și a scrisorii către acționari (profit ajustat, restatări, promisiuni)",
         "source": "1983 principiul 12; 2002"},
        {"id": "K7", "name": "În afara cadrului",
         "state": "trece",
         "fact": "companie nefinanciară cu situații auditate în EDGAR; filtrul reputațional (2025) rămâne judecată",
         "source": "2002; 2025"},
    ]

    # ---- gate verdicts ------------------------------------------------------------
    enough = len(oe_clean) >= P["window_years"]
    short = P["short_history_min"] <= len(oe_clean) < P["window_years"]
    g3_reason = []
    if negligible_years:
        g3_reason.append(f"capital tangibil neglijabil în {negligible_years} din {len(window)} ani (semnal pozitiv)")
    if roic_clean:
        g3_reason.append(f"ROIC tangibil median {statistics.median(roic_clean)*100:.0f}% în anii cu capital măsurabil")
    inc5, inc10 = incremental(5), incremental(min(10, n))
    g3_reason.append(f"ROIC incremental 5 ani: {inc5['state'] if inc5['value'] is None else ('peste 200%' if inc5['value'] > 2 else f'{inc5['value']*100:.0f}%')}")
    g3_reason.append("categoria 2007 este judecată (de completat)")
    gates = [
        {"id": "G2", "name": "Poarta 2: înțelegi afacerea", "verdict": "necesita_judecata",
         "reason": "textele porții 2 nu sunt scrise (paragraful la zece ani, cele trei moduri de a muri, clasificarea)" + ("; indiciu de instabilitate prezent" if indicators["instability_flag"] else "; fără indiciu de instabilitate"),
         "pending_judgments": ["paragraful la zece ani", "cele trei moduri de a muri", "clasificarea în cerc / prea greu / în afară"]},
        {"id": "G3", "name": "Poarta 3: randamente pe capital",
         "verdict": ("date_insuficiente" if not (enough or short) else "necesita_judecata"),
         "reason": "; ".join(g3_reason) + ("" if enough else "; istoric scurt" if short else "; sub 7 exerciții"),
         "pending_judgments": ["categoria 2007 (excelentă, bună, groaznică)", "alegerea lui (c), capexul de menținere, dacă diferă de interval"]},
        {"id": "SURV", "name": "Supraviețuire", "verdict": surv_v, "reason": surv_reason,
         "pending_judgments": ["scadențele pe cinci ani din notele 10-K"]},
        {"id": "G4", "name": "Poarta 4: moat", "verdict": ("date_insuficiente" if not (enough or short) else "necesita_judecata"),
         "reason": f"dovezi: ROIC peste prag sau capital neglijabil în {roic_above_hurdle_years} din {len(window)} ani; marja operațională între {indicators['operating_margin_min']*100:.0f}% și {indicators['operating_margin_max']*100:.0f}%; formularul omului nu este completat" if margins else "formularul omului nu este completat",
         "pending_judgments": ["sursele șanțului cu dovezi", "testul francizei 1991", "testul capitalului 1998", "direcția și durabilitatea"]},
        {"id": "MGMT", "name": "Management", "verdict": "necesita_judecata",
         "reason": f"fapte disponibile: răscumpărări și dividende pe zece ani, CAGR acțiuni {('lipsă' if share_cagr is None else ro(share_cagr*100, 1, sign=True) + '%')}; candoarea, stimulentele și testul dolarului (forma Owner's Manual, cere valoarea contabilă pe acțiune și indexul) nu sunt evaluate",
         "pending_judgments": ["candoare", "stimulente din proxy", "judecata sincer și competent"]},
        {"id": "G5", "name": "Poarta 5: preț sub valoare", "verdict": "inchisa",
         "reason": "închisă până la textele porții 2; în plus lipsesc prețul și randamentul obligațiunii cu dată (fără vendor de prețuri în acest export)",
         "pending_judgments": ["prețul pe care l-aș plăti"]},
    ]

    # ---- data issues --------------------------------------------------------------
    issue_rows = []
    for r in issues:
        if r["entity"] != entity:
            continue
        per = r.get("period") or ""
        yr = per[:4]
        if yr.isdigit() and int(yr) < y0 - 1:
            continue
        sev = {"low": "info", "info": "info", "medium": "warning", "warning": "warning", "high": "blocking", "blocking": "blocking"}.get(r["severity"], "info")
        issue_rows.append({"type": sev, "concept": r["concept"], "period": per, "description": r["description"], "effect": ""})
    for note in split_notes:
        issue_rows.append({"type": "warning", "concept": "diluted_shares", "period": f"{y0} la {y1}", "description": note, "effect": "CAGR acțiuni și OE pe acțiune ajustate; de verificat"})
    issue_rows.append({"type": "info", "concept": "sbc", "period": f"{y0} la {y1}", "description": "compensația în acțiuni nu a fost extrasă în spike; OE nu o adaugă înapoi (nu afectează OE), dar filtrul K5 rămâne incomplet", "effect": "K5 parțial"})
    issue_rows.append({"type": "info", "concept": "price", "period": TODAY, "description": "fără sursă de preț și fără randamentul obligațiunii la data analizei; poarta 5 închisă", "effect": "G5 închisă"})
    issue_rows.append({"type": "info", "concept": "other_operating_assets", "period": f"{y0} la {y1}", "description": "capitalul investit tangibil folosește capital de lucru net plus imobilizări corporale; alte active operaționale nu sunt separate în companyfacts", "effect": "ROIC tangibil posibil ușor supraestimat"})

    # ---- sources ------------------------------------------------------------------
    sources = [{"title": "SEC EDGAR companyfacts (XBRL)", "url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json", "accessed": "2026-10-31"}]
    for acc, (form, filed, url) in sorted(accessions.items(), key=lambda kv: kv[1][1], reverse=True)[:12]:
        sources.append({"title": f"{form} depus {filed}, {acc}", "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/", "accessed": "2026-10-31"})

    def rows_from(metric, label, formula, unit, register="C"):
        return {"metric": metric, "label": label, "formula": formula, "unit": unit, "register": register,
                "values": {str(y): calc[metric].get(str(y)) for y in window},
                "flags": {str(y): flags[metric].get(str(y)) for y in window if flags[metric].get(str(y))}}

    gate3_rows = [
        rows_from("oe_low", "OE_jos", "profit net + D&A − capex total", "USD"),
        rows_from("oe_high", "OE_sus", "profit net + D&A − max(D&A, capex de menținere Greenwald)", "USD"),
        rows_from("greenwald_maintenance_capex", "Capex de menținere (Greenwald)", "capex − max(0, Δvenituri × media(imobilizări/venituri, 3 ani anteriori))", "USD"),
        rows_from("fcf_simple", "CFO − capex (verificare)", "flux din exploatare − capex", "USD"),
        rows_from("oe_conversion", "Conversie OE_jos / profit net", "OE_jos ÷ profit net", "x"),
        rows_from("oe_low_per_share", "OE_jos pe acțiune diluată", "OE_jos ÷ acțiuni diluate", "USD/acțiune"),
        rows_from("effective_tax_rate", "Rata efectivă de impozit", "impozit ÷ profit înainte de impozit, limitată la 0 la 50%", "%"),
        rows_from("nopat", "NOPAT", "profit operațional × (1 − rata efectivă)", "USD"),
        rows_from("tangible_capital", "Capital investit tangibil", "(active curente − numerar excedentar) − (datorii curente − datorie purtătoare de dobândă curentă) + imobilizări corporale nete; numerar excedentar = numerar + investiții pe termen scurt − 2% din venituri", "USD"),
        rows_from("roic_tangible", "ROIC tangibil", "NOPAT ÷ capital investit tangibil (sfârșit de an); „capital necesar neglijabil” când capitalul este sub 5% din venituri sau negativ", "%"),
        rows_from("roic_with_goodwill", "ROIC cu fond comercial (pe prețul plătit)", "NOPAT ÷ (capital tangibil + fond comercial + necorporale)", "%"),
        rows_from("oe_over_capex_plus_nwc", "OE_jos ÷ (capex + capital de lucru), când capitalul e neglijabil", "OE_jos ÷ (capex + max(capital de lucru net, 0))", "x"),
        rows_from("roe_begin_equity", "ROE pe capitalul de început de an", "profit net ÷ capital propriu la începutul anului", "%"),
        rows_from("capex_to_revenue", "Capex / venituri", "capex ÷ venituri", "%"),
        rows_from("da_to_capex", "D&A / capex", "D&A ÷ capex", "x"),
        rows_from("operating_margin", "Marja operațională", "profit operațional ÷ venituri", "%"),
    ]
    survival_rows = [
        rows_from("net_debt", "Datorie netă", "datorie pe termen lung + partea curentă + împrumuturi pe termen scurt − numerar − investiții pe termen scurt", "USD"),
        rows_from("net_debt_to_oe_low", "Datorie netă / OE_jos", "datorie netă ÷ OE_jos", "x"),
        rows_from("interest_cover", "Acoperirea dobânzilor", "profit operațional ÷ cheltuieli cu dobânzile", "x"),
    ]

    analysis = {
        "schema_version": "sixgates-analysis-1.0",
        "company": {"name": name, "ticker": entity, "market": market, "cik": cik, "lei": None, "currency": "USD",
                    "fiscal_year_end": fy_end, "standard": "US GAAP"},
        "analysis": {"date": TODAY, "version": 1, "framework_version": FRAMEWORK_VERSION, "author": "export din spike-ul fazei 1 (date reale, judecăți necompletate)",
                     "status": "draft", "notice": "Aritmetică cu surse și judecăți atribuite, nu sfat de investiții.",
                     "window": {"from": y0, "to": y1, "years_available": public_years, "years_in_window": len(window)}},
        "preanalysis": {"decision": "nedecis", "decided_at": None, "filters": filters},
        "gates": gates,
        "facts": {"unit": "USD", "display_scale": 1e6, "display_scale_label": "milioane", "years": window, "rows": fact_rows,
                  "note": "valorile din cea mai recentă depunere pentru fiecare perioadă; etichetele XBRL ca în depunere; sursa fiecărei linii în source_tags și în lista de surse"},
        "gate2": {"indicators": indicators, "parameters": {"instab_loss_years": P["instab_loss_years"], "instab_cv_oe": P["instab_cv_oe"], "instab_revenue_deviation": P["instab_revenue_deviation"]}},
        "gate3": {"years": window, "rows": gate3_rows,
                  "incremental": {"5y": inc5, "10y": inc10},
                  "oe_low_cagr": oe_cagr, "share_cagr": share_cagr,
                  "roic_above_hurdle_years": roic_above_hurdle_years, "negligible_capital_years": negligible_years,
                  "category": {"value": None, "register": "J", "author": None, "date": None, "reason": "de completat de om, cu cifrele de mai sus"}},
        "survival": {"rows": survival_rows, "latest": {"year": y1, "net_debt": nd_last, "net_debt_to_oe_low": nd_to_oe, "net_debt_to_min_oe_low": nd_to_oe_min, "interest_cover": cover_last},
                     "stress": stress, "thresholds": {k: P[k] for k in ("surv_pass_net_debt_to_oe", "surv_fail_net_debt_to_oe", "surv_pass_cover", "surv_fail_cover", "stress_cover_min", "stress_years_to_repay_max")}},
        "judgments": {
            "gate2": {"ten_year_paragraph": "", "three_ways_to_die": ["", "", ""], "classification": "", "author": "", "date": "", "register": "J"},
            "gate4": {"moat_sources": [], "franchise_test_1991": {"needed_or_desired": "", "no_close_substitute": "", "price_unregulated": ""}, "capital_test_1998": "", "star_manager_2007": "", "direction": "", "durability_years": "", "author": "", "date": "", "register": "J"},
            "management": {"candour": "", "incentives": "", "verdict": "", "author": "", "date": "", "register": "J"},
            "decision_paragraph": {"ten_years": "", "why_moat_holds": "", "price_vs_value": "", "what_would_prove_me_wrong": [], "closed_market_5y": "", "author": "", "date": "", "register": "J"},
        },
        "management_facts": {
            "buybacks": {str(y): g("share_repurchases", y) for y in window},
            "dividends": {str(y): g("dividends_paid", y) for y in window},
            "diluted_shares": {str(y): g("diluted_shares", y) for y in window},
            "share_cagr": share_cagr,
            "dollar_test_owner_manual": {"value": None, "note": "cere valoarea contabilă pe acțiune și S&P 500 cu dividende pe cinci ani: nu sunt în acest export"},
        },
        "gate5": {"locked": True, "lock_reason": "textele porții 2 lipsesc; fără preț și fără randament cu dată",
                  "inputs": {"oe_low_last": oe_last, "oe_high_last": calc["oe_high"].get(last), "oe_low_cagr_10y": oe_cagr, "bond_yield": None, "bond_yield_date": None, "price": None, "price_date": None, "shares_outstanding": None},
                  "grid": None, "perpetuity_check": None, "reverse_dcf": None, "oe_yield": None,
                  "margin": {"band": "afacere 30 la 50% (franciză 15 la 25% doar cu poarta 4 trecută)", "register": "parametru propus"},
                  "price_i_would_pay": {"value": None, "register": "J", "author": None, "date": None},
                  "verdict": "inchisa"},
        "data_issues": issue_rows,
        "parameters": [
            {"name": "Fereastra de istoric", "value": "10 exerciții; 7 la 9 istoric scurt; sub 7 date insuficiente", "inspired_by": "1983, Owner's Manual 9"},
            {"name": "Capex de menținere (c)", "value": "interval: D&A (podea) la capex total (plafon); Greenwald ca a treia estimare", "inspired_by": "1986, 2015"},
            {"name": "Numerar excedentar", "value": "numerar + investiții pe termen scurt peste 2% din venituri", "inspired_by": "instrument"},
            {"name": "Capital neglijabil", "value": "capital tangibil sub 5% din venituri sau negativ", "inspired_by": "instrument"},
            {"name": "Rata de actualizare (prag pentru persistența ROIC)", "value": "6% USD (podea), fără randamentul obligațiunii la data analizei", "inspired_by": "2000"},
            {"name": "Supraviețuire", "value": "trece: datorie netă ≤ 2 × OE_jos și acoperire ≥ 8; pică: > 5 × OE_jos sau acoperire < 1; stres OE −50% doi ani, acoperire după șoc ≥ 3, rambursare ≤ 6 ani", "inspired_by": "little or no debt"},
            {"name": "Instabilitate (poarta 2)", "value": "≥ 2 ani cu pierdere în 10; CV OE > 0,5; abatere venituri > 20%", "inspired_by": "instrument"},
            {"name": "Pre-analiza", "value": "K1 < 7 ani sau > 2 ani cu pierdere; K3 ROE median < 12%; K4 datorie netă > 5 × (CFO − capex) sau acoperire < 3; K5 acțiuni > +2% pe an", "inspired_by": "criteriile de achiziție; 2010 până la 2016; OM 10"},
        ],
        "sources": sources,
    }
    return analysis


def main():
    annual, facts, issues = load()
    entities = sorted({r["entity"] for r in annual})
    for e in entities:
        if e not in NAMES:
            continue
        a = build(e, annual, facts, issues)
        d = OUT / e
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{TODAY}_v1.json"
        p.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
        print(p.relative_to(ROOT), p.stat().st_size, "bytes; verdicts:", [(gt["id"], gt["verdict"]) for gt in a["gates"]])


if __name__ == "__main__":
    sys.exit(main())
