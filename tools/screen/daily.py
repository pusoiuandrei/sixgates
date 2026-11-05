#!/usr/bin/env python3
"""SixGates daily brief: three companies a day from the S&P 500 and Nasdaq universe.

Pipeline (all deterministic, nothing estimated):
  1. universe      S&P 500 constituents (GitHub datasets CSV, with GICS) + Nasdaq-listed SEC filers
  2. frames        ten years of XBRL facts for every filer (SEC frames API), ~6 minutes
  3. screen        pre-analysis filters K1, K3, K4, K5 and K2 indicators (framework section 1)
  4. sic           SIC code, country, forms for the quantitative survivors (cached in the repo)
  5. circle        K7 exclusions and the user's circle (technology, cyber, fintech, related), quality points
  6. price gate    Yahoo price, split-adjusted diluted shares, OE_jos yield vs DGS10, implied growth,
                   VI_jos grid (r = max(DGS10, 6%), +2, +4 points; g = 0, 4, 8% capped by OE history)
  7. rotation      three companies not shown in the last ROTATION_DAYS days, ordered by price gap
                   among names with at least MIN_QUALITY points; state kept in data/screens/daily/state.json
  8. brief         Romanian markdown, data/screens/daily/<date>/brief.md (+ picks.json, universe_today.csv)

Usage: python3 tools/screen/daily.py [--skip-fetch] [--workdir DIR] [--date AAAA-LL-ZZ]
Gate 2 (understanding the business) and gate 4 (moat) stay with the user; the brief only asks the question.
Language rule: no buy/sell/cheap/expensive verdicts; the price is placed against the value range.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from math import floor, log10
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
UA_SEC = {"User-Agent": "SixGates research spike contact@sixgates.local", "Accept-Encoding": "gzip, deflate"}
UA_WEB = {"User-Agent": "Mozilla/5.0"}
ROTATION_DAYS = 30
MIN_QUALITY = 10          # of 15 quality points in rank_circle.py (ranking aid, never shown as a score)
MAX_FILING_AGE_DAYS = 460 # latest fiscal year must end within ~15 months
EXCLUDE_COUNTRIES = {"F4", "K3"}  # business address in China or Hong Kong: outside the user's circle
MIN_MCAP_USD = 2e9        # parametru propus: capitalizare minimă pentru brief
MIN_REVENUE_USD = 5e8     # parametru propus: venituri minime în ultimul exercițiu
MAX_ABS_SHARE_CAGR = 0.15 # o serie de acțiuni care variază cu peste 15% pe an cere verificare manuală
R_FLOOR, G_CAP, G_TERMINAL = 0.06, 0.08, 0.025
MARGIN_BUSINESS = (0.30, 0.50)


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd: list[str], env: dict) -> None:
    log("run: " + " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


# ---------- formatting (Romanian) ----------
def ro(x, nd=1, suffix=""):
    if x is None:
        return "lipsă"
    s = f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")
    return s + suffix


def pct(x, nd=1):
    return "lipsă" if x is None else ro(x * 100, nd, "%")


def bn(x, cur="USD"):
    if x is None:
        return "lipsă"
    if abs(x) >= 1e9:
        return ro(x / 1e9, 2, f" mld {cur}")
    return ro(x / 1e6, 0, f" mil {cur}")


def sig2(x):
    if x is None or x == 0:
        return x
    return round(x, -int(floor(log10(abs(x)))) + 1)


# ---------- valuation helpers (framework section 9, instrument not rule) ----------
def vi_per_share(oe_ps: float, g: float, r: float, gt: float = G_TERMINAL, n: int = 10) -> float:
    return sum(oe_ps * (1 + g) ** t / (1 + r) ** t for t in range(1, n + 1)) + \
        oe_ps * (1 + g) ** n * (1 + gt) / (r - gt) / (1 + r) ** n


def implied_growth(oe_ps: float, price: float, r: float) -> float:
    lo, hi = -0.5, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if vi_per_share(oe_ps, mid, r) < price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------- step 1: universe ----------
def build_universe(work: Path) -> dict:
    raw = work / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    r = requests.get("https://www.sec.gov/files/company_tickers_exchange.json", headers=UA_SEC, timeout=120)
    r.raise_for_status()
    (raw / "company_tickers_exchange.json").write_bytes(r.content)
    r2 = requests.get("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv",
                      timeout=120)
    r2.raise_for_status()
    (raw / "sp500.csv").write_bytes(r2.content)
    d = json.loads(r.content)
    rows = [dict(zip(d["fields"], x)) for x in d["data"]]
    sp = list(csv.DictReader((raw / "sp500.csv").open(encoding="utf-8")))
    uni = {}
    for x in rows:
        if x["exchange"] not in ("Nasdaq", "NYSE", "CBOE", "TXSE") or not x["cik"]:
            continue
        cik = int(x["cik"])
        u = uni.setdefault(cik, {"cik": cik, "name": x["name"], "tickers": [], "exchanges": set(), "sp500": False,
                                 "gics_sector": "", "gics_sub": ""})
        u["tickers"].append(x["ticker"])
        u["exchanges"].add(x["exchange"])
    for x in sp:
        try:
            cik = int(x["CIK"])
        except (ValueError, KeyError):
            continue
        u = uni.setdefault(cik, {"cik": cik, "name": x["Security"], "tickers": [], "exchanges": set(), "sp500": False,
                                 "gics_sector": "", "gics_sub": ""})
        u["sp500"] = True
        u["gics_sector"], u["gics_sub"] = x["GICS Sector"], x["GICS Sub-Industry"]
        if x["Symbol"] not in u["tickers"]:
            u["tickers"].insert(0, x["Symbol"])
    scope = [{**u, "exchanges": sorted(u["exchanges"])} for u in uni.values() if u["sp500"] or "Nasdaq" in u["exchanges"]]
    scope.sort(key=lambda u: u["cik"])
    json.dump(scope, (work / "universe.json").open("w", encoding="utf-8"), ensure_ascii=False)
    return {"universe": len(scope), "sp500": sum(u["sp500"] for u in scope),
            "nasdaq": sum("Nasdaq" in u["exchanges"] for u in scope), "sp500_rows": len(sp)}


# ---------- step 6: price gate ----------
def yahoo(ticker: str):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=2y&interval=1d&events=splits"
    for attempt in range(3):
        try:
            res = requests.get(url, headers=UA_WEB, timeout=30).json()["chart"]["result"][0]
            meta = res["meta"]
            splits = [(time.strftime("%Y-%m-%d", time.gmtime(s["date"])), s["numerator"] / s["denominator"])
                      for s in (res.get("events", {}).get("splits", {}) or {}).values()]
            return meta.get("regularMarketPrice"), time.strftime("%Y-%m-%d", time.gmtime(meta.get("regularMarketTime", 0))), \
                meta.get("currency"), splits
        except Exception:
            time.sleep(1.5)
    return None, None, None, []


def dgs10(work: Path):
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10", timeout=60)
    r.raise_for_status()
    (work / "DGS10.csv").write_bytes(r.content)
    rows = [l.split(",") for l in r.text.strip().splitlines()[1:]]
    rows = [x for x in rows if len(x) == 2 and x[1] not in (".", "")]
    return rows[-1][0], float(rows[-1][1]) / 100


def price_gate(work: Path, ranked: list[dict], bond: float) -> list[dict]:
    con = sqlite3.connect(work / "frames.db")
    r0 = max(bond, R_FLOOR)
    out = []
    for q in ranked:
        cik, fy = int(q["cik"]), q["fy_end"]
        sh = con.execute("SELECT val FROM facts WHERE cik=? AND tag='WeightedAverageNumberOfDilutedSharesOutstanding' "
                         "AND end=? AND kind='duration'", (cik, fy)).fetchone()
        sh = sh[0] if sh else None
        price, pdate, cur, splits = yahoo(q["ticker"])
        adj = 1.0
        for sdate, ratio in splits:
            if sdate > fy:
                adj *= ratio
        oe = q.get("oe_low_last")
        g_hist = q.get("oe_low_cagr")
        g_used = None if g_hist is None else max(0.0, min(g_hist, G_CAP))
        item = dict(q)
        item.update(price=price, price_date=pdate, price_currency=cur, shares_basis=sh, split_adj=adj,
                    r_used=r0, g_used=g_used, oe_per_share=None, oe_yield=None, implied_g_r0=None, implied_g_r2=None,
                    vi_low=None, p_to_vi=None, discount_to_vi=None, grid=None, mcap=None, band=None)
        if oe and sh and price and cur == "USD" and oe > 0:
            sh_adj = sh * adj
            oe_ps = oe / sh_adj
            mcap = price * sh_adj
            vi_low = vi_per_share(oe_ps, g_used, r0) if g_used is not None else None
            grid = {f"r={r:.0%}": {f"g={g:.0%}": sig2(vi_per_share(oe_ps, g, r)) for g in (0.0, 0.04, 0.08)}
                    for r in (r0, r0 + 0.02, r0 + 0.04)}
            item.update(oe_per_share=oe_ps, oe_yield=oe_ps / price, mcap=mcap,
                        implied_g_r0=implied_growth(oe_ps, price, r0), implied_g_r2=implied_growth(oe_ps, price, r0 + 0.02),
                        vi_low=vi_low, p_to_vi=(price / vi_low) if vi_low else None,
                        discount_to_vi=(1 - price / vi_low) if vi_low else None, grid=grid)
            if vi_low:
                disc = 1 - price / vi_low
                if disc >= MARGIN_BUSINESS[1]:
                    item["band"] = f"sub VI_jos cu {pct(disc, 0)}: peste marja maximă propusă (50%)"
                elif disc >= MARGIN_BUSINESS[0]:
                    item["band"] = f"sub VI_jos cu {pct(disc, 0)}: între marjele propuse (30 la 50%)"
                elif disc > 0:
                    item["band"] = f"sub VI_jos cu {pct(disc, 0)}: sub marja minimă propusă (30%)"
                else:
                    item["band"] = f"peste VI_jos cu {pct(-disc, 0)}"
        elif oe is not None and oe <= 0:
            item["band"] = "OE_jos negativ (capex peste profit plus D&A): valoarea nu se calculează"
        out.append(item)
        time.sleep(0.25)
    return out


# ---------- step 7: rotation ----------
def eligible(item: dict, today: date) -> tuple[bool, str]:
    if item.get("business_country") in EXCLUDE_COUNTRIES:
        return False, "sediu în China sau Hong Kong (în afara cercului)"
    if item.get("quality_pts", 0) < MIN_QUALITY:
        return False, f"sub {MIN_QUALITY} puncte de calitate"
    try:
        if (today - date.fromisoformat(item["fy_end"])).days > MAX_FILING_AGE_DAYS:
            return False, "ultimul exercițiu mai vechi de 15 luni"
    except Exception:
        return False, "sfârșit de exercițiu necunoscut"
    if item.get("oe_low_last") is not None and item["oe_low_last"] <= 0:
        return False, "OE_jos negativ (capex peste profit plus D&A)"
    if item.get("price") is None:
        return False, "fără preț de la vendor"
    if item.get("p_to_vi") is None:
        return False, "fără acțiuni diluate în etichetele standard (acțiuni pe clase)"
    if (item.get("mcap") or 0) < MIN_MCAP_USD:
        return False, "capitalizare sub 2 mld USD"
    if (item.get("rev_last") or 0) < MIN_REVENUE_USD:
        return False, "venituri sub 500 mil USD"
    if item.get("shares_cagr10") is not None and abs(item["shares_cagr10"]) > MAX_ABS_SHARE_CAGR:
        return False, "seria de acțiuni variază cu peste 15% pe an (verificare manuală)"
    if not item.get("last_annual_filing"):
        return False, "data ultimului raport anual necunoscută"
    return True, ""


def choose(items: list[dict], state: dict, today: date) -> tuple[list[dict], list[dict]]:
    cutoff = (today - timedelta(days=ROTATION_DAYS)).isoformat()
    recent = {t for t, dates in state.get("presented", {}).items() if any(d >= cutoff for d in dates)}
    pool = []
    for it in items:
        ok, why = eligible(it, today)
        it["eligible"], it["ineligible_reason"] = ok, why
        if ok:
            pool.append(it)
    pool.sort(key=lambda it: (it["p_to_vi"], -it["quality_pts"]))
    fresh = [it for it in pool if it["ticker"] not in recent]
    picks = fresh[:3]
    if len(picks) < 3:  # rotation exhausted: allow repeats, oldest first
        last_seen = {t: max(d) for t, d in state.get("presented", {}).items()}
        rest = sorted([it for it in pool if it not in picks], key=lambda it: (last_seen.get(it["ticker"], ""), it["p_to_vi"]))
        picks += rest[:3 - len(picks)]
    return picks, pool


# ---------- step 8: brief ----------
def filing_link(cik: str, accn: str | None) -> str:
    if not accn:
        return ""
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"


def company_block(i: int, it: dict, bond: float, bond_date: str) -> str:
    idx = "S&P 500" if str(it.get("sp500")) == "True" else "Nasdaq (în afara S&P 500)"
    forms = it.get("forms") or ""
    fy = it["fy_end"]
    lines = [f"### {i}. {it['name']} ({it['ticker']})",
             f"{idx}; {it['category']}; SIC {it.get('sic') or 'lipsă'} ({it.get('sic_desc') or 'lipsă'}); exercițiul încheiat {fy}; "
             f"formular {forms or 'lipsă'}; ultimul raport anual depus {it.get('last_annual_filing') or 'lipsă'}; depunerea sursă a profitului net: {filing_link(it['cik'], it.get('accn_last')) or 'lipsă'}",
             "",
             "Zece ani de fapte [F] și calcule [C] (etichete XBRL standard, ultima depunere pentru fiecare an):",
             f"- Venituri {bn(it.get('rev_last'))} în ultimul exercițiu, CAGR {pct(it.get('rev_cagr'))} pe fereastră; marja operațională mediană {pct(it.get('op_margin_median'))}, minimă {pct(it.get('op_margin_min'))}",
             f"- Ani cu pierdere: {it.get('loss_years')} din {it.get('years')} disponibili; ROE median pe capitalul de început de an {pct(it.get('roe_median'))}"
             + (f" ({it.get('neg_equity_years')} ani cu capital propriu negativ)" if it.get('neg_equity_years') else ""),
             f"- OE_jos (profit net + D&A minus capex total) {bn(it.get('oe_low_last'))}, CAGR {pct(it.get('oe_low_cagr'))}; marja FCF mediană {pct(it.get('fcf_margin_median'))}; capex pe CFO median {pct(it.get('capex_to_cfo_median'))}",
             f"- Datorie netă {bn(it.get('net_debt'))} = {ro(it.get('nd_to_fcf'), 1, 'x')} FCF; acoperirea dobânzilor {ro(it.get('cover'), 0, 'x') if it.get('cover') is not None else 'nedisponibilă'}; etichete: {it.get('debt_tag') or 'fără datorie etichetată'}",
             f"- Acțiuni diluate CAGR 10 ani {pct(it.get('shares_cagr10'))}, 5 ani {pct(it.get('shares_cagr5'))}; compensație în acțiuni {pct(it.get('sbc_to_rev'))} din venituri; R&D {pct(it.get('rd_to_rev'))} din venituri; răscumpărări în ultimul exercițiu {bn(it.get('buyback_last'))}"
             + (f"; {it.get('share_flags')}" if it.get('share_flags') else ""),
             "",
             f"Filtre: K1 {it['K1']} | K3 {it['K3']} | K4 {it['K4']} | K5 {it['K5']} | K7 trece (nu e bancă, asigurător sau REIT; situații auditate în EDGAR)"
             + (f" | indicii K2: {it['K2_flags']}" if it.get('K2_flags') else " | indicii K2 din cifre: niciunul"),
             ""]
    if it.get("p_to_vi") is not None:
        g = it["grid"]
        gl = "; ".join(f"{rk}: " + ", ".join(f"{gk} {ro(v, 0)}" for gk, v in rv.items()) for rk, rv in g.items())
        lines += [f"Prețul, ultimul (poarta 5, instrument, nu regulă): {ro(it['price'], 2)} USD la {it['price_date']} (Yahoo Finance); capitalizare {bn(it['mcap'])} pe {ro(it['shares_basis'] * it['split_adj'] / 1e6, 1)} mil acțiuni diluate"
                  + (f" (ajustate {it['split_adj']:g}x pentru split după exercițiu)" if it['split_adj'] != 1 else ""),
                  f"- Randament OE_jos pe capitalizare {pct(it['oe_yield'])} față de DGS10 {pct(bond, 2)} ({bond_date}, FRED)",
                  f"- Creșterea OE pe zece ani presupusă de preț: {pct(it['implied_g_r0'])} pe an la r = {pct(it['r_used'], 0)}, {pct(it['implied_g_r2'])} la r = {pct(it['r_used'] + 0.02, 0)}; istoricul OE: {pct(it.get('oe_low_cagr'))}",
                  f"- VI_jos pe acțiune la g = {pct(it['g_used'], 0)} (istoric plafonat la 8%), r = {pct(it['r_used'], 0)}, creștere terminală 2,5%: {ro(sig2(it['vi_low']), 0)} USD; prețul este {it['band']}",
                  f"- Grila VI_jos pe acțiune: {gl}",
                  ""]
    else:
        lines += [f"Prețul: {it.get('band') or 'indicator de preț indisponibil'}", ""]
    lines += ["Ce decizi tu (porțile 2 și 4, nu se calculează): poți descrie această afacere peste zece ani și ce o poate omorî? "
              "Dacă nu, răspunsul este „prea greu”, oricât de bune ar fi cifrele.", ""]
    return "\n".join(lines)


def write_brief(out_dir: Path, today: date, counts: dict, funnel: dict, items: list[dict], pool: list[dict], picks: list[dict],
                state: dict, bond: float, bond_date: str) -> str:
    under = [it for it in pool if it.get("discount_to_vi") is not None and it["discount_to_vi"] > 0]
    prev = state.get("last_run", {})
    prev_pass = set(prev.get("in_circle_pass", []))
    now_pass = {it["ticker"] for it in items}
    entered, left = sorted(now_pass - prev_pass), sorted(prev_pass - now_pass)
    prev_under = set(prev.get("under_vi", []))
    now_under = {it["ticker"] for it in under}
    cutoff = (today - timedelta(days=ROTATION_DAYS)).isoformat()
    shown_recent = sorted(t for t, ds in state.get("presented", {}).items() if any(d >= cutoff for d in ds))
    L = [f"# SixGates zilnic, {today.isoformat()}", "",
         "Aritmetică cu surse și judecăți atribuite, nu sfat de investiții. Pragurile sunt parametri propuși (cadrul SixGates v2.3, secțiunea 13), nu reguli ale lui Buffett sau Munger. Poarta 2 (înțelegi afacerea) și poarta 4 (moat) rămân ale tale; prețul este ultimul și este pus față de intervalul de valoare, fără verdict.",
         "",
         "## Pâlnia de azi",
         f"- Univers: {counts['universe']} companii (S&P 500: {counts['sp500']} CIK-uri, inclusiv Dow 30; listate pe Nasdaq: {counts['nasdaq']}); cu fapte XBRL anuale: {funnel.get('with_facts')}",
         f"- K1 trece: {funnel.get('K1_pass')}; și K3: {funnel.get('K1_K3_pass')}; și K4: {funnel.get('K1_K3_K4_pass')}; și K5: {funnel.get('K1_K3_K4_K5_pass')}",
         f"- În cercul tău după K7: {len(items)}; eligibile pentru brief (cel puțin 10 puncte de calitate din 15, exercițiu recent, preț disponibil, capitalizare peste 2 mld USD, venituri peste 500 mil USD, sediu în afara Chinei și Hong Kong): {len(pool)}; cu preț sub VI_jos: {len(under)}",
         (f"- Schimbări față de rularea anterioară ({prev.get('date')}): intrate în lista cercului: {', '.join(entered) or 'niciuna'}; ieșite: {', '.join(left) or 'niciuna'}; "
          f"intrate sub VI_jos: {', '.join(sorted(now_under - prev_under)) or 'niciuna'}; ieșite de sub VI_jos: {', '.join(sorted(prev_under - now_under)) or 'niciuna'}"
          if prev.get("date") else "- Prima rulare: fără comparație cu o rulare anterioară"),
         f"- Rotație: companiile arătate în ultimele {ROTATION_DAYS} de zile nu se repetă ({len(shown_recent)} excluse azi)",
         "",
         "## Cele trei companii de azi: " + ", ".join(f"{p['ticker']} ({p['name']})" for p in picks), ""]
    for i, it in enumerate(picks, 1):
        L.append(company_block(i, it, bond, bond_date))
    L += ["## Restul listei cu preț sub VI_jos azi (ordonate după distanța față de VI_jos)"]
    others = [it for it in under if it not in picks]
    if others:
        for it in others[:25]:
            L.append(f"- {it['ticker']} ({it['name'][:40]}): preț {ro(it['price'], 2)}, VI_jos {ro(sig2(it['vi_low']), 0)} la g {pct(it['g_used'], 0)}, {it['band']}; randament OE {pct(it['oe_yield'])}"
                     + ("; recent arătată" if it['ticker'] in shown_recent else ""))
        if len(others) > 25:
            L.append(f"- și încă {len(others) - 25} în picks.json")
    else:
        L.append("- niciuna")
    L += ["", "## Calitate trece, preț peste VI_jos (primele 15 după calitate)"]
    above = sorted([it for it in pool if it.get("discount_to_vi") is not None and it["discount_to_vi"] <= 0],
                   key=lambda it: (-it["quality_pts"], it["p_to_vi"]))[:15]
    for it in above:
        L.append(f"- {it['ticker']}: preț {ro(it['price'], 2)}, {it['band']}; randament OE {pct(it['oe_yield'])}")
    excluded = [it for it in items if not it.get("eligible")]
    L += ["", f"## Excluse din brief azi ({len(excluded)}): " + "; ".join(f"{it['ticker']} ({it['ineligible_reason']})" for it in excluded[:40]) + (" ..." if len(excluded) > 40 else ""),
          "",
          "## Metodă și surse",
          "SEC XBRL frames API și companyfacts (data.sec.gov), formulare 10-K și 20-F în US GAAP; SEC company_tickers_exchange.json; constituenții S&P 500 din github.com/datasets/s-and-p-500-companies; FRED DGS10; prețuri Yahoo Finance (vendor, doar pentru poarta 5). "
          "Formule: OE_jos = profit net + D&A minus capex total; ROE pe capitalul de început de an; VI = suma OE × (1+g)^t / (1+r)^t pe zece ani plus valoarea terminală la 2,5%, actualizată; r = max(DGS10, 6%). "
          "Limite: OE_jos penalizează companiile în plin ciclu de investiții; acțiunile pe clase (Visa) nu au CAGR; emitenții IFRS nu apar. Codul: tools/screen/ în repo-ul SixGates; fișierele zilei: data/screens/daily/" + today.isoformat() + "/.",
          ""]
    text = "\n".join(L)
    (out_dir / "brief.md").write_text(text, encoding="utf-8")
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=str(REPO / "work" / "screen"))
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--skip-fetch", action="store_true", help="reuse frames.db already in workdir")
    ap.add_argument("--no-state", action="store_true", help="do not update state.json (dry run)")
    args = ap.parse_args()
    today = date.fromisoformat(args.date)
    work = Path(args.workdir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "SIXGATES_SCREEN_DIR": str(work), "DAILY": "1"}
    daily_dir = REPO / "data" / "screens" / "daily"
    out_dir = daily_dir / today.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path = daily_dir / "state.json"
    state = json.load(state_path.open()) if state_path.exists() else {"presented": {}, "last_run": {}}
    t0 = time.time()

    log("1/8 universe")
    counts = build_universe(work)
    log(f"universe: {counts}")

    if not args.skip_fetch or not (work / "frames.db").exists():
        log("2/8 frames (SEC), about 6 minutes")
        run([sys.executable, str(TOOLS / "fetch_frames.py")], env)
    else:
        log("2/8 frames: reusing " + str(work / "frames.db"))

    log("3/8 screen")
    run([sys.executable, str(TOOLS / "screen.py")], env)
    funnel = json.load((work / "funnel.json").open())

    log("4/8 SIC lookup (cached)")
    cache_repo = daily_dir / "sic_cache.json"
    if cache_repo.exists():
        shutil.copy(cache_repo, work / "sic.json")
    rows = list(csv.DictReader((work / "screen_all.csv").open(encoding="utf-8")))
    passing = [r for r in rows if all(r.get(k, "").startswith("trece") for k in ("K1", "K3", "K4", "K5"))]
    (work / "ciks_pass.txt").write_text("\n".join(r["cik"] for r in passing))
    run([sys.executable, str(TOOLS / "sic_lookup.py"), str(work / "ciks_pass.txt")], env)
    shutil.copy(work / "sic.json", cache_repo)

    log("5/8 circle and quality")
    run([sys.executable, str(TOOLS / "rank_circle.py")], env)
    ranked = json.load((work / "ranked.json").open(encoding="utf-8"))

    log("6/8 price gate")
    bond_date, bond = dgs10(work)
    items = price_gate(work, ranked, bond)

    log("7/8 rotation")
    picks, pool = choose(items, state, today)

    log("8/8 brief")
    text = write_brief(out_dir, today, counts, funnel, items, pool, picks, state, bond, bond_date)
    json.dump({"date": today.isoformat(), "bond": bond, "bond_date": bond_date, "counts": counts, "funnel": funnel,
               "picks": picks, "all_in_circle": items}, (out_dir / "picks.json").open("w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=str)
    shutil.copy(work / "screen_all.csv", out_dir / "universe_today.csv")
    if not args.no_state:
        for it in picks:
            state.setdefault("presented", {}).setdefault(it["ticker"], []).append(today.isoformat())
        state["last_run"] = {"date": today.isoformat(), "in_circle_pass": sorted(it["ticker"] for it in items),
                             "under_vi": sorted(it["ticker"] for it in pool if it.get("discount_to_vi") and it["discount_to_vi"] > 0),
                             "picks": [it["ticker"] for it in picks]}
        json.dump(state, state_path.open("w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"done in {time.time() - t0:.0f}s: {out_dir / 'brief.md'}; picks: {[p['ticker'] for p in picks]}")
    print("BRIEF_PATH=" + str(out_dir / "brief.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
