"""Step 5: run the formula engine on the extracted annual facts.

Reads out/annual_us.csv and out/annual_eu.csv (plus the data issue logs and the
FRED hurdle input), computes the gate 3 and gate 5 metrics for each company and
writes out/metrics.csv and out/spike_report.md (Romanian).

Every metric row carries the formula id and version, the fact ids it used, a
status and flags. Nothing is estimated: a missing input propagates as a status.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict

import common
import formulas as F
from concept_map import REQUIRED_FOR_TEN_YEAR_RULE

ENTITIES = {
    "AAPL": {"name": "Apple Inc.", "source": "SEC EDGAR companyfacts", "unit": "USD", "scale": 1e6, "franchise": True},
    "KO": {"name": "The Coca-Cola Company", "source": "SEC EDGAR companyfacts", "unit": "USD", "scale": 1e6, "franchise": True},
    "MCO": {"name": "Moody's Corporation", "source": "SEC EDGAR companyfacts", "unit": "USD", "scale": 1e6, "franchise": True},
    "LVMH": {"name": "LVMH Moët Hennessy Louis Vuitton", "source": "ESEF via filings.xbrl.org", "unit": "EUR", "scale": 1e6, "franchise": True},
    "SNP": {"name": "OMV Petrom SA", "source": "ESEF via filings.xbrl.org", "unit": "RON", "scale": 1e6, "franchise": False},
}
WINDOW = 10
USABLE = {"ok", "partial_sum", "ambiguous", "derived_identity"}
METRIC_FIELDS = ["entity", "fiscal_year", "metric", "value", "unit", "status", "flags", "formula_id", "version", "inputs", "detail"]
A = F.Assumptions()


def load_annual() -> dict[str, dict[int, dict[str, dict]]]:
    """annual[entity][fy][concept] = row (value, status, fact_ids, source_concepts)."""
    annual: dict[str, dict[int, dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))
    for name in ("annual_us.csv", "annual_eu.csv"):
        for r in common.read_csv(common.OUT_DIR / name):
            annual[r["entity"]][int(r["fiscal_year"])][r["concept"]] = r
    return annual


def fact(row: dict | None, unit: str) -> F.Fact | None:
    """Turn an annual row into a Fact, or None when the value is not usable."""
    if not row or row["status"] not in USABLE or row["value"] == "":
        return None
    return F.Fact(float(row["value"]), row["fact_ids"], unit)


def compute_entity(entity: str, years: dict[int, dict[str, dict]], meta: dict) -> tuple[list[dict], dict]:
    """All metric rows for one entity plus a summary dict for the report."""
    unit = meta["unit"]
    fys = sorted(years)
    window = [fy for fy in fys if fy > fys[-1] - WINDOW]
    rows: list[dict] = []
    per_year: dict[int, dict[str, F.Result]] = defaultdict(dict)

    def emit(fy: int | None, metric: str, res: F.Result) -> F.Result:
        rows.append({"entity": entity, "fiscal_year": fy if fy is not None else "", "metric": metric, "value": "" if res.value is None else res.value,
                     "unit": res.unit, "status": res.status, "flags": ";".join(res.flags), "formula_id": res.formula_id,
                     "version": res.version, "inputs": ";".join(res.inputs), "detail": json.dumps(res.detail, ensure_ascii=False, default=str)})
        if fy is not None:
            per_year[fy][metric] = res
        return res

    g = lambda fy, c: fact(years.get(fy, {}).get(c), unit)
    # yearly building blocks (all fiscal years, so that deltas and beginning capital exist for the window)
    for fy in fys:
        ncwc = emit(fy, "ncwc", F.non_cash_working_capital(g(fy, "current_assets"), g(fy, "cash"), g(fy, "st_investments"),
                                                          g(fy, "current_liabilities"), g(fy, "st_borrowings"), g(fy, "ltd_current")))
        emit(fy, "tangible_capital", F.tangible_invested_capital(ncwc, g(fy, "ppe_net")))
        tr = emit(fy, "tax_rate", F.effective_tax_rate(g(fy, "income_tax"), g(fy, "pretax_income"), A))
        emit(fy, "nopat", F.nopat(g(fy, "operating_income"), tr))
    for fy in fys:
        mc = emit(fy, "maintenance_capex", F.maintenance_capex(g(fy, "capex"), g(fy, "d_and_a"), A.maintenance_capex_method))
        prev = per_year.get(fy - 1, {}).get("ncwc")
        cur = per_year[fy].get("ncwc")
        dwc = None
        if prev and prev.value is not None and cur and cur.value is not None:
            dwc = F.Fact(cur.value - prev.value, "derived:" + ";".join(cur.inputs + prev.inputs), unit)
        oe = emit(fy, "owner_earnings", F.owner_earnings(g(fy, "net_income"), g(fy, "d_and_a"), mc, dwc))
        emit(fy, "owner_earnings_ex_wc", F.owner_earnings(g(fy, "net_income"), g(fy, "d_and_a"), mc, None))
        nop = per_year[fy].get("nopat")
        tic_begin = per_year.get(fy - 1, {}).get("tangible_capital")
        nop_f = F.Fact(nop.value, "derived:" + ";".join(nop.inputs), unit) if nop and nop.value is not None else None
        tic_f = F.Fact(tic_begin.value, "derived:" + ";".join(tic_begin.inputs), unit) if tic_begin and tic_begin.value is not None else None
        emit(fy, "tangible_roic", F.return_on_tangible_capital(nop_f, tic_f))
        emit(fy, "capex_to_sales", F.ratio("capex_to_sales", g(fy, "capex"), g(fy, "revenue")))
        emit(fy, "cash_conversion", F.ratio("cash_conversion", g(fy, "cfo"), g(fy, "net_income")))
        debt_parts = [g(fy, c) for c in ("st_borrowings", "ltd_current", "debt_long")]
        present = [d for d in debt_parts if d is not None]
        if g(fy, "debt_long") is None:
            total_debt = F.Result("total_debt", "1.0.0", None, unit, "missing_input", ("missing:debt_long",), ())
        else:
            absent = [c for c, d in zip(("st_borrowings", "ltd_current", "debt_long"), debt_parts) if d is None]
            total_debt = F.Result("total_debt", "1.0.0", sum(d.value for d in present), unit, "ok",
                                  tuple(f"{c}:absent_treated_as_not_reported" for c in absent), tuple(d.fact_id for d in present))
        emit(fy, "total_debt", total_debt)
        cash, sti = g(fy, "cash"), g(fy, "st_investments")
        if total_debt.value is None or cash is None:
            net_debt = F.Result("net_debt", "1.0.0", None, unit, "missing_input", ("missing:total_debt_or_cash",), ())
        else:
            net_debt = F.Result("net_debt", "1.0.0", total_debt.value - cash.value - (sti.value if sti else 0.0), unit, "ok",
                                total_debt.flags + (() if sti else ("st_investments:absent_not_deducted",)),
                                total_debt.inputs + (cash.fact_id,) + ((sti.fact_id,) if sti else ()))
        emit(fy, "net_debt", net_debt)
        emit(fy, "net_debt_to_oe", F.ratio("net_debt_to_oe", net_debt, oe) if oe.value is not None and oe.value > 0
             else F.Result("net_debt_to_oe", "1.0.0", None, "ratio", "flagged" if oe.value is not None else "missing_input", ("non_positive_owner_earnings",), ()))
        emit(fy, "interest_coverage", F.ratio("interest_coverage", g(fy, "operating_income"), g(fy, "interest_expense")))
        for n in (5, 10):
            nop0 = per_year.get(fy - n, {}).get("nopat")
            tic0 = per_year.get(fy - n, {}).get("tangible_capital")
            tic1 = per_year[fy].get("tangible_capital")
            emit(fy, f"incremental_roic_{n}y", F.incremental_return(
                nop_f, F.Fact(nop0.value, "derived", unit) if nop0 and nop0.value is not None else None,
                F.Fact(tic1.value, "derived", unit) if tic1 and tic1.value is not None else None,
                F.Fact(tic0.value, "derived", unit) if tic0 and tic0.value is not None else None))
        # growth identity: reinvestment rate = (capex - D&A + delta NCWC) / NOPAT
        capex, da = g(fy, "capex"), g(fy, "d_and_a")
        if capex and da and dwc and nop_f and nop_f.value > 0:
            rr = F.Result("reinvestment_rate", "1.0.0", (capex.value - da.value + dwc.value) / nop_f.value, "ratio", "ok", (),
                          (capex.fact_id, da.fact_id, dwc.fact_id, nop_f.fact_id))
        else:
            rr = F.Result("reinvestment_rate", "1.0.0", None, "ratio", "missing_input", ("missing:capex_da_dwc_or_nopat",), ())
        emit(fy, "reinvestment_rate", rr)
        nop5 = per_year.get(fy - 5, {}).get("nopat")
        obs = F.cagr(F.Fact(nop5.value, "derived", unit) if nop5 and nop5.value is not None else None, nop_f, 5)
        emit(fy, "nopat_cagr_5y", obs)
        emit(fy, "growth_identity", F.growth_identity(rr, per_year[fy]["tangible_roic"], obs))
        emit(fy, "business_category", F.business_category(per_year[fy]["incremental_roic_5y"], per_year[fy]["capex_to_sales"], A))

    # window-level results
    complete = [fy for fy in fys if all(years[fy].get(c, {}).get("status") in USABLE for c in REQUIRED_FOR_TEN_YEAR_RULE)]
    rule = emit(None, "ten_year_rule", F.ten_year_rule(complete))
    oe_series = [F.Fact(per_year[fy]["owner_earnings"].value, per_year[fy]["owner_earnings"].inputs[0] if per_year[fy]["owner_earnings"].inputs else "", unit)
                 for fy in window if per_year[fy]["owner_earnings"].value is not None]
    emit(None, "predictability_oe", F.predictability(oe_series))
    last = fys[-1]
    oe_last = per_year[last]["owner_earnings"]
    first = window[0]
    oe_first = per_year.get(first, {}).get("owner_earnings")
    hist = F.cagr(F.Fact(oe_first.value, "derived", unit) if oe_first and oe_first.value is not None else None,
                  F.Fact(oe_last.value, "derived", unit) if oe_last.value is not None else None, last - first)
    emit(None, "oe_cagr_window", hist)
    if rule.status == "ok":
        iv = emit(None, "intrinsic_value_range", F.intrinsic_value_range(oe_last, hist, A))
        pay = emit(None, "price_i_would_pay_total", F.price_i_would_pay(iv, meta["franchise"], A))
        shares = g(last, "diluted_shares")
        if iv.value is not None and shares and shares.value > 0:
            emit(None, "price_i_would_pay_per_share", F.Result("price_i_would_pay_per_share", "1.0.0", pay.detail["low"] / shares.value, unit + "/share", "ok",
                                                               pay.flags, pay.inputs + (shares.fact_id,),
                                                               {"low": pay.detail["low"] / shares.value, "high": pay.detail["high"] / shares.value, "diluted_shares": shares.value}))
        else:
            emit(None, "price_i_would_pay_per_share", F.Result("price_i_would_pay_per_share", "1.0.0", None, unit + "/share", "missing_input", ("missing:diluted_shares",), ()))
    else:
        for m in ("intrinsic_value_range", "price_i_would_pay_total", "price_i_would_pay_per_share"):
            emit(None, m, F.Result(m, "1.0.0", None, unit, "flagged", ("insufficient_data",), (), {"complete_years": complete}))
    emit(None, "reverse_dcf", F.reverse_dcf(None, oe_last, A))
    emit(None, "margin_of_safety", F.margin_of_safety(None, per_year[last].get("owner_earnings")))
    retained = [(g(fy, "net_income"), g(fy, "dividends_paid")) for fy in fys[-5:]]
    if all(n and d for n, d in retained):
        ret = F.Fact(sum(n.value - d.value for n, d in retained), "derived", unit)
        emit(None, "one_dollar_test_5y", F.one_dollar_test(None, None, ret))
    else:
        emit(None, "one_dollar_test_5y", F.Result("one_dollar_test", "1.0.0", None, "ratio", "missing_input", ("missing:net_income_or_dividends",), ()))
    summary = {"fys": fys, "window": window, "complete": complete, "per_year": per_year, "rule": rule}
    return rows, summary


def fmt_m(v, scale=1e6) -> str:
    return "lipsă" if v is None else f"{v / scale:,.0f}"


def fmt_pct(res: F.Result | None) -> str:
    if res is None or res.value is None:
        if res is not None and "capital_did_not_grow" in res.flags:
            d = res.detail.get("delta_profit")
            return "n/a (capital nu a crescut, profit în creștere)" if d is not None and d > 0 else "n/a (capital nu a crescut)"
        if res is not None and "non_positive_tangible_capital" in res.flags:
            return "semnalat (capital tangibil ≤ 0)"
        return "lipsă"
    if res.value > 2.0:
        return f"> 200% (capital tangibil neglijabil, {res.value:.0f}x)"
    return f"{res.value * 100:.1f}%"


def fmt_x(res: F.Result | None) -> str:
    if res is None or res.value is None:
        if res is not None and "non_positive_owner_earnings" in res.flags:
            return "semnalat (OE ≤ 0)"
        return "lipsă"
    return f"{res.value:.2f}x"


def write_report(summaries: dict[str, dict], annual: dict, issues: list[dict], hurdle: dict) -> None:
    """Romanian spike report with per-company tables and the data issue log."""
    L: list[str] = []
    L.append("# Raportul spike-ului de date (faza 1)\n")
    L.append(f"Generat {common.now_iso()} de `spike/run_spike.py`. Toate cifrele provin din fapte descărcate (EDGAR companyfacts, filings.xbrl.org, FRED) sau din formule aplicate pe ele; nimic nu este estimat. Valorile sunt în milioane, în moneda de raportare a emitentului. Statusurile: `lipsă` = concept neraportat în sursă; `semnalat` = formula a refuzat calculul (de exemplu capital tangibil nepozitiv); `date insuficiente` = sub zece exerciții complete.\n")
    L.append(f"Intrare pentru prag: FRED DGS10 = {hurdle['latest_value_pct']}% la {hurdle['latest_date']} (sursa: {hurdle['source_url']}). Pragul total implicit al setului de ipoteze v1 rămâne 10% (randamentul obligațiunii lungi plus prima aleasă), deci DGS10 este referința, nu rata folosită.\n")
    L.append("Ipoteze fixe (assumption_set v1-default, versiunea 1): prag 10%; creștere explicită 10 ani; calea joasă = jumătate din CAGR-ul istoric al OE, plafon 5%, creștere terminală 2%; calea înaltă = CAGR istoric, plafon 10%, creștere terminală 3%; fără creștere când CAGR-ul este negativ; capex de întreținere = min(capex, amortizare); alte cheltuieli fără numerar neadăugate (compensația în acțiuni tratată drept cost real); tot numerarul tratat ca excedentar la calculul capitalului tangibil; marja cerută 30 la 50% pentru afacere, 15 la 25% pentru franciză. Pragurile categoriilor din scrisoarea 2007 (excelent > 30% ROIC incremental și capex/vânzări < 5%; bun ≥ costul capitalului + 5 puncte; groaznic < costul capitalului) sunt propuse și trebuie validate pe setul de aur.\n")
    L.append("## Sumar pe companii\n")
    L.append("| Companie | Sursă | Exerciții extrase | Regula de zece ani | VI calculată |")
    L.append("|---|---|---|---|---|")
    for ent, s in summaries.items():
        meta = ENTITIES[ent]
        rule = s["rule"]
        rule_txt = "trece" if rule.status == "ok" else f"date insuficiente ({int(rule.value)} consecutive complete)"
        iv = next((r for r in s["rows"] if r["metric"] == "intrinsic_value_range"), None)
        iv_txt = "da (interval)" if iv and iv["status"] == "ok" else ("nu: " + (iv["flags"] if iv else ""))
        L.append(f"| {meta['name']} ({ent}) | {meta['source']} | FY{s['fys'][0]} la FY{s['fys'][-1]} ({len(s['fys'])}), fereastră FY{s['window'][0]} la FY{s['window'][-1]} | {rule_txt} | {iv_txt} |")
    L.append("")
    for ent, s in summaries.items():
        meta = ENTITIES[ent]
        py = s["per_year"]
        unit = meta["unit"]
        L.append(f"## {meta['name']} ({ent}), {unit} milioane\n")
        L.append(f"Sursă: {meta['source']}. Exerciții disponibile: FY{s['fys'][0]} la FY{s['fys'][-1]}. Exerciții complete pentru regula de zece ani: {', '.join(str(y) for y in s['complete']) or 'niciunul'}.\n")
        L.append("### Tabel A: venituri, profit net, câștigurile proprietarului, ROIC tangibil\n")
        L.append("| An | Venituri | Profit net | OE | ROIC tangibil |")
        L.append("|---|---|---|---|---|")
        for fy in s["window"]:
            yr = annual[ent].get(fy, {})
            rev = yr.get("revenue", {}); ni = yr.get("net_income", {})
            L.append(f"| FY{fy} | {fmt_m(float(rev['value'])) if rev.get('value') else 'lipsă'} | {fmt_m(float(ni['value'])) if ni.get('value') else 'lipsă'} | {fmt_m(py[fy]['owner_earnings'].value)} | {fmt_pct(py[fy]['tangible_roic'])} |")
        L.append("")
        L.append("### Tabel B: ROIC incremental, categorie, datorie netă, conversie în numerar\n")
        L.append("| An | ROIC incr. 5 ani | Categorie 2007 (de validat) | Datorie netă / OE | CFO / profit net |")
        L.append("|---|---|---|---|---|")
        for fy in s["window"]:
            cat = py[fy]["business_category"]
            cat_txt = cat.detail.get("label", "lipsă") if cat.status in ("ok", "not_applicable") else "lipsă"
            L.append(f"| FY{fy} | {fmt_pct(py[fy]['incremental_roic_5y'])} | {cat_txt} | {fmt_x(py[fy]['net_debt_to_oe'])} | {fmt_x(py[fy]['cash_conversion'])} |")
        L.append("")
        last = s["fys"][-1]
        ir10 = py[last]["incremental_roic_10y"]
        roic_last = py[last]["tangible_roic"]
        gi = py[last]["growth_identity"]
        gi_txt = "n/a (capital tangibil neglijabil sau nepozitiv)" if roic_last.value is None or roic_last.value > 2.0 else fmt_pct(gi)
        L.append(f"ROIC incremental pe 10 ani la FY{last}: {fmt_pct(ir10)}. Acoperirea dobânzilor FY{last}: {fmt_x(py[last]['interest_coverage'])}. Capex/vânzări FY{last}: {fmt_pct(py[last]['capex_to_sales'])}. Identitatea creșterii FY{last}: g implicit = {gi_txt} față de CAGR NOPAT 5 ani observat {fmt_pct(py[last]['nopat_cagr_5y'])}.\n")
        L.append(f"OE FY{last} fără termenul de capital de lucru: {fmt_m(py[last]['owner_earnings_ex_wc'].value)} (față de {fmt_m(py[last]['owner_earnings'].value)} cu ΔWC). Termenul ΔWC an de an face seria OE volatilă; o regulă de normalizare (de exemplu media pe 3 ani a ΔWC) este o decizie de luat în faza 2, nu o ipoteză a spike-ului.\n")
        rows = {r["metric"]: r for r in s["rows"] if r["fiscal_year"] == ""}
        pred = rows["predictability_oe"]
        L.append("### Poarta 5: interval de valoare intrinsecă\n")
        if rows["intrinsic_value_range"]["status"] == "ok":
            d = json.loads(rows["intrinsic_value_range"]["detail"])
            pay = json.loads(rows["price_i_would_pay_total"]["detail"])
            L.append(f"- OE FY{last}: {fmt_m(py[last]['owner_earnings'].value)}; CAGR OE pe fereastră: {fmt_pct(F.Result('x','1',float(rows['oe_cagr_window']['value']) if rows['oe_cagr_window']['value'] != '' else None,'ratio','ok'))}; coeficient de variație OE: {float(pred['value']):.2f} ({json.loads(pred['detail']).get('loss_years', 0)} ani cu pierdere)." if rows['oe_cagr_window']['value'] != '' else f"- OE FY{last}: {fmt_m(py[last]['owner_earnings'].value)}; CAGR OE: lipsă.")
            L.append(f"- VI (interval): {fmt_m(d['low'])} la {fmt_m(d['high'])} {unit} milioane (g explicit {d['g_low']*100:.1f}% la {d['g_high']*100:.1f}%, r = {d['rate']*100:.0f}%, terminal {d['terminal_low']*100:.0f}% la {d['terminal_high']*100:.0f}%, {d['years']} ani).")
            L.append(f"- Prețul pe care l-aș plăti (pe VI joasă, marjă {'franciză' if meta['franchise'] else 'afacere'} {pay['margin_low']*100:.0f} la {pay['margin_high']*100:.0f}%): {fmt_m(pay['low'])} la {fmt_m(pay['high'])} {unit} milioane în total" +
                     (f", adică {json.loads(rows['price_i_would_pay_per_share']['detail'])['low']:.2f} la {json.loads(rows['price_i_would_pay_per_share']['detail'])['high']:.2f} {unit} pe acțiune diluată." if rows["price_i_would_pay_per_share"]["status"] == "ok" else "; pe acțiune: lipsă (acțiuni diluate neraportate)."))
            L.append("- Încadrarea în franciză sau afacere este o judecată a omului; aici este doar un parametru al spike-ului.")
        else:
            L.append(f"- Nu se calculează: {rows['intrinsic_value_range']['flags']} (exerciții complete: {', '.join(str(y) for y in s['complete']) or 'niciunul'}).")
            if py[last]["owner_earnings"].value is not None:
                L.append(f"- OE FY{last} există ({fmt_m(py[last]['owner_earnings'].value)}), dar poarta nu trece fără zece ani.")
        L.append(f"- DCF invers: {rows['reverse_dcf']['status']} ({rows['reverse_dcf']['flags']}). Marja de siguranță: {rows['margin_of_safety']['status']} ({rows['margin_of_safety']['flags']}). Testul dolarului pe 5 ani: {rows['one_dollar_test_5y']['status']} ({rows['one_dollar_test_5y']['flags']}). Niciun furnizor de prețuri nu a fost accesibil din container (EODHD și Polygon cer cheie, stooq blocat, Yahoo limitat), deci toate metricile cu preț rămân necalculate.\n")
    L.append("## Jurnalul problemelor de date\n")
    L.append("Grupat pe companie, severitate și tip, limitat la fereastra de analiză plus anul de bază; perioadele sunt comasate. Jurnalul complet, linie cu linie și pentru toți anii, este în `out/data_issues_us.csv`, `out/data_issues_eu.csv` și `out/data_issues_metrics.csv`.\n")
    grouped: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    window_start = {ent: s["window"][0] - 1 for ent, s in summaries.items()}
    for i in issues:
        if i["period"] and i["entity"] in window_start and int(i["period"][:4]) < window_start[i["entity"]]:
            continue  # pre-window years stay in the CSV logs only
        key = (i["entity"], i["severity"], i["concept"], _issue_kind(i["description"]))
        grouped[key].append(i["period"][:4] if i["period"] else "")
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    L.append("| Companie | Severitate | Concept | Perioade | Problemă |")
    L.append("|---|---|---|---|---|")
    for key in sorted(grouped, key=lambda k: (list(ENTITIES).index(k[0]) if k[0] in ENTITIES else 9, order.get(k[1], 9), k[2])):
        ent, sev, concept, kind = key
        periods = sorted({p for p in grouped[key] if p})
        per_txt = _compress(periods) if periods else "toate"
        L.append(f"| {ent} | {sev} | {concept} | {per_txt} | {kind} |")
    L.append("")
    (common.OUT_DIR / "spike_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def _issue_kind(desc: str) -> str:
    """Collapse a free-text issue into its type, in Romanian, for the grouped table."""
    d = desc
    if d.startswith("restated"):
        return "retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal"
    if d.startswith("rounding-only"):
        return "diferență doar de rotunjire între rapoarte"
    if d.startswith("synonym tags disagree"):
        return "etichete sinonime cu valori diferite; cea mai recent depusă păstrată, necesită verificare"
    if d.startswith("no standard-taxonomy fact"):
        return "concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă)"
    if d.startswith("partial sum"):
        return "sumă parțială: o componentă lipsește"
    if d.startswith("fallback tag"):
        return "etichetă de rezervă (mai largă sau mai îngustă) folosită, notată"
    if d.startswith("source tag changed"):
        return "schimbare de etichetă XBRL între exerciții"
    if d.startswith("per-entity override"):
        return "suprascriere per emitent spre eticheta corectă, justificată"
    if "52/53-week" in d:
        return "exercițiu de 52 sau 53 de săptămâni"
    if "share count ratio" in d:
        return "split de acțiuni retratat doar în rapoartele ulterioare; seria pe acțiune inutilizabilă fără factor de split"
    if d.startswith("ESEF history"):
        return "istoric ESEF scurt pe filings.xbrl.org; regula de zece ani nu poate fi îndeplinită din această sursă"
    if "filings for the same period" in d:
        return "depuneri duplicate pentru același exercițiu (versiuni lingvistice sau al doilea OAM)"
    if "ProfitLossBeforeTax not tagged" in d:
        return "profit înainte de impozit neetichetat; afișat ca identitate profit + impozit, marcat derivat"
    if "units ignored" in d:
        return "unități ignorate (pe acțiune, rapoarte)"
    if "companyfacts does not expose" in d:
        return "companyfacts nu expune decimals și nici etichetele proprii; ambele cer instanța XBRL a raportului"
    if d.startswith("negative equity") or "equity" in d and "negative" in d:
        return "capital propriu negativ"
    if d.startswith("currency"):
        return "monedă diferită de USD/EUR; fără conversie, fără amestec"
    if d.startswith("tangible capital"):
        return "capital tangibil nepozitiv: ROIC semnalat, nu calculat"
    if d.startswith("fy label"):
        return "eticheta exercițiului fiscal nu coincide cu anul datei de închidere"
    return d[:90]


def _compress(years: list[str]) -> str:
    """'2015, 2016, 2017, 2019' -> '2015 la 2017, 2019'."""
    ys = sorted(int(y) for y in years)
    out, start, prev = [], ys[0], ys[0]
    for y in ys[1:] + [None]:
        if y is not None and y == prev + 1:
            prev = y
            continue
        out.append(str(start) if start == prev else f"{start} la {prev}")
        if y is not None:
            start = prev = y
    return ", ".join(out)


def main() -> int:
    annual = load_annual()
    hurdle = json.loads((common.OUT_DIR / "hurdle_input.json").read_text(encoding="utf-8"))
    all_rows: list[dict] = []
    summaries: dict[str, dict] = {}
    metric_issues: list[dict] = []
    for ent, meta in ENTITIES.items():
        rows, s = compute_entity(ent, annual[ent], meta)
        s["rows"] = rows
        all_rows += rows
        summaries[ent] = s
        for fy in s["fys"]:
            eq = annual[ent][fy].get("equity", {})
            if eq.get("value") and float(eq["value"]) <= 0:
                metric_issues.append({"entity": ent, "severity": "medium", "concept": "equity", "period": f"{fy}",
                                      "description": f"negative equity in FY{fy} ({float(eq['value']) / 1e6:,.0f} m): return on equity not meaningful; tangible capital is the basis"})
            tic = s["per_year"][fy].get("tangible_capital")
            if tic and tic.status == "flagged":
                metric_issues.append({"entity": ent, "severity": "high", "concept": "tangible_capital", "period": f"{fy}",
                                      "description": f"tangible capital non-positive in FY{fy} ({tic.value / 1e6:,.0f} m): ROIC flagged, not computed"})
        if meta["unit"] not in ("USD", "EUR"):
            metric_issues.append({"entity": ent, "severity": "info", "concept": "all", "period": "",
                                  "description": f"currency {meta['unit']}: kept as reported, never converted or mixed"})
        print(f"{ent}: {len(rows)} metric rows; ten-year rule {s['rule'].status}; complete years {s['complete']}")
    for i in metric_issues:
        i["detected_at"] = common.now_iso()
    common.write_csv(common.OUT_DIR / "metrics.csv", all_rows, METRIC_FIELDS)
    common.write_csv(common.OUT_DIR / "data_issues_metrics.csv", metric_issues, ["entity", "severity", "concept", "period", "description", "detected_at"])
    issues = common.read_csv(common.OUT_DIR / "data_issues_us.csv") + common.read_csv(common.OUT_DIR / "data_issues_eu.csv") + metric_issues
    write_report(summaries, annual, issues, hurdle)
    print("wrote metrics.csv, data_issues_metrics.csv, spike_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
