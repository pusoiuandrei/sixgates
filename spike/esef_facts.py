"""Step 2: ESEF filings from filings.xbrl.org to annual facts with provenance.

Outputs
-------
out/facts_eu.csv        every numeric, non-dimensional fact considered
out/annual_eu.csv       one row per (entity, fiscal year, canonical concept)
out/data_issues_eu.csv  issues detected here

Notes on the source: the xBRL-JSON (OIM) file of each filing holds the facts of
the inline XBRL report. Periods are ISO intervals whose end is the midnight that
*follows* the last day (``.../2025-01-01T00:00:00`` means 31 December 2024).
Only facts without extra dimensions are statement totals; everything else is a
breakdown and is ignored here. Issuer extensions (``LVM:``, ``omvpetrom:``)
are kept with their prefix; overrides match them by local name because the
prefix changes from year to year.
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from datetime import date, timedelta

import common
from concept_map import IFRS, REQUIRED_FOR_TEN_YEAR_RULE, ConceptSpec
from sec_facts import ANNUAL_FIELDS, ISSUE_FIELDS, RawFact, resolve_year, select_latest

ISSUERS: dict[str, dict] = {
    "IOG4E947OATN0KJYSD45": {"entity": "LVMH", "market": "Euronext Paris", "currency": "EUR"},
    "549300UKYDM6L8HEPU79": {"entity": "SNP", "market": "BVB", "currency": "RON"},
}
CORE_DIMS = {"concept", "entity", "period", "unit", "language"}

# Per-entity overrides for ESEF, matched by local name ("*:" prefix) because
# issuer extension prefixes are not stable across years.
OVERRIDES: dict[tuple[str, str], tuple[str, str]] = {
    ("LVMH", "operating_income"): (
        "*:ProfitLossFromOperatingActivitiesAfterShareOfProfitLossOfAssociatesAndJointVentures",
        "LVMH tags no ifrs-full operating profit; its 'operating profit' line (after other operating income and "
        "expenses) is an extension; the 'profit from recurring operations' subtotal is not used",
    ),
    ("LVMH", "capex"): (
        "*:OperatingInvestmentsClassifiedAsInvestingActivities",
        "cash-flow line 'operating investments' (purchases of property, plant, equipment and intangibles, net of "
        "disposals) is an extension",
    ),
    ("LVMH", "interest_expense"): (
        "*:CostOfNetDebt",
        "'cost of net financial debt' is an extension; ifrs-full:FinanceIncomeCost is a net figure with other items",
    ),
    ("SNP", "capex"): (
        "*:IntangibleAssetsAndPropertyPlantAndEquipment",
        "cash-flow line 'investments in intangible assets and property, plant and equipment' is an extension "
        "(prefix omvpetromsa in FY2021, omvpetrom in FY2022)",
    ),
}
FACT_FIELDS = [
    "fact_id", "entity", "lei", "canonical_concept", "source_concept", "unit", "period_start", "period_end",
    "is_instant", "fiscal_year", "value", "decimals", "accession", "form", "filed", "fy", "fp", "frame",
    "selected", "superseded_by", "is_restated", "used_for_canonical", "extracted_at", "source_url",
]


def _period(raw: str) -> tuple[str, str, bool]:
    """Convert an OIM period into (start, end, is_instant) with inclusive end dates."""
    if "/" in raw:
        s, e = raw.split("/")
        end = date.fromisoformat(e[:10]) - timedelta(days=1)
        return s[:10], end.isoformat(), False
    end = date.fromisoformat(raw[:10]) - timedelta(days=1)
    return "", end.isoformat(), True


def load_filings(lei: str) -> list[dict]:
    """Filing records for one LEI as listed by the filings.xbrl.org API."""
    url = f"https://filings.xbrl.org/api/entities/{lei}/filings?page%5Bsize%5D=50"
    data = common.load_json(common.fetch(url, common.DATA_DIR / "esef" / f"filings_{lei}.json"))
    out = []
    for f in data["data"]:
        a = f["attributes"]
        if a.get("json_url"):
            out.append({"id": f["id"], "fxo_id": a["fxo_id"], "period_end": a["period_end"], "country": a["country"],
                        "published": (a.get("published") or a.get("date_added") or "")[:10],
                        "json_url": "https://filings.xbrl.org" + a["json_url"],
                        "report_url": "https://filings.xbrl.org" + (a.get("report_url") or ""),
                        "package_sha256": a.get("sha256", ""), "errors": a.get("error_count")})
    return out


def collect_filing_facts(filing: dict, lei: str, entity: str, currency: str) -> tuple[list[RawFact], list[dict]]:
    """All numeric, non-dimensional facts of one filing as RawFact rows."""
    path = common.DATA_DIR / "esef" / lei / (filing["fxo_id"] + ".json")
    common.fetch(filing["json_url"], path)
    doc = common.load_json(path)
    facts: list[RawFact] = []
    issues: list[dict] = []
    other_units: set[str] = set()
    for fid, f in doc["facts"].items():
        dims = f["dimensions"]
        if "unit" not in dims or set(dims) - CORE_DIMS:
            continue
        unit = dims["unit"]
        if unit == f"iso4217:{currency}":
            canon_unit = currency
        elif unit in ("xbrli:shares", "shares"):
            canon_unit = "shares"
        else:
            other_units.add(unit)
            continue
        start, end, instant = _period(dims["period"])
        try:
            value = float(f["value"])
        except (TypeError, ValueError):
            continue
        facts.append(RawFact(
            fact_id=common.fact_id(lei, dims["concept"], unit, start, end, filing["fxo_id"]),
            entity=entity, cik=0, canonical_concept="", source_concept=dims["concept"], unit=canon_unit,
            period_start=start, period_end=end, is_instant=instant, fiscal_year=int(end[:4]), value=value,
            decimals="" if f.get("decimals") is None else str(f["decimals"]),
            accession=filing["fxo_id"], form="ESEF-AR", filed=filing["published"], fy=int(filing["period_end"][:4]),
            fp="FY", frame="", extracted_at=common.now_iso(), source_url=filing["json_url"],
        ))
    if other_units:
        issues.append({"severity": "info", "concept": "all", "period": filing["period_end"],
                       "description": f"{filing['fxo_id']}: units ignored {sorted(other_units)} (per-share and ratio facts)"})
    return facts, issues


def process_issuer(lei: str, meta: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Run selection and canonical mapping for one issuer."""
    entity, currency = meta["entity"], meta["currency"]
    filings = load_filings(lei)
    issues: list[dict] = []
    raw: list[RawFact] = []
    for filing in sorted(filings, key=lambda x: (x["period_end"], x["published"], x["fxo_id"])):
        facts, more = collect_filing_facts(filing, lei, entity, currency)
        raw += facts
        issues += more
    years = sorted({f["period_end"][:4] for f in filings})
    dup = {}
    for f in filings:
        dup.setdefault(f["period_end"], []).append(f["fxo_id"])
    for pe, ids in dup.items():
        if len(ids) > 1:
            issues.append({"severity": "info", "concept": "all", "period": pe,
                           "description": f"{len(ids)} filings for the same period (language versions or second OAM): {', '.join(ids)}"})
    issues.append({"severity": "high", "concept": "all", "period": "",
                   "description": f"ESEF history on filings.xbrl.org: filings for FY{years[0]} to FY{years[-1]} only; "
                                  f"the ten-year rule cannot be met from this source"})
    issues += select_latest(raw)
    lookup = {(f.source_concept, f.period_end): f for f in raw if f.selected}
    by_local = {(f.source_concept.split(":", 1)[1], f.period_end): f for f in raw if f.selected and not f.source_concept.startswith("ifrs-full:")}
    # focus years of the filings plus the comparative year of the oldest one;
    # older opening balances from the equity statement are not fiscal years
    fiscal_years = list(range(int(years[0]) - 1, int(years[-1]) + 1))
    annual: list[dict] = []
    facts_out: list[dict] = []
    for spec in IFRS:
        prev_source = None
        for fy in fiscal_years:
            end = f"{fy}-12-31"
            override = OVERRIDES.get((entity, spec.name))
            chosen: list[RawFact] = []
            status, note, more = "missing", "", []
            if override and override[0].startswith("*:"):
                f = by_local.get((override[0][2:], end))
                if f and (f.is_instant == (spec.kind == "instant")):
                    chosen, status, note = [f], "ok", f"override: {override[1]}"
                    more.append({"severity": "info", "concept": spec.name, "period": end,
                                 "description": f"per-entity override to extension {f.source_concept}: {override[1]}"})
            if not chosen:
                chosen, status, note, more = resolve_year(spec, lookup, end, fy, None, "")
            if not chosen and spec.name == "pretax_income":
                pl, tax = lookup.get(("ifrs-full:ProfitLoss", end)), lookup.get(("ifrs-full:IncomeTaxExpenseContinuingOperations", end))
                if pl and tax:
                    chosen, status, note = [pl, tax], "derived_identity", "ProfitLoss + IncomeTaxExpenseContinuingOperations (no ProfitLossBeforeTax tagged)"
                    more = [{"severity": "medium", "concept": spec.name, "period": end,
                             "description": f"FY{fy}: ProfitLossBeforeTax not tagged; shown as the identity ProfitLoss + income tax, marked derived"}]
            issues += more
            row = {"entity": entity, "cik": lei, "fiscal_year": fy, "period_end": end, "concept": spec.name, "value": "",
                   "unit": currency if spec.unit != "shares" else "shares", "status": status, "source_concepts": "",
                   "fact_ids": "", "note": note}
            if chosen:
                for f in chosen:
                    f.used_for_canonical = True
                    f.canonical_concept = spec.name
                row["value"] = f"{sum(f.value for f in chosen):.0f}"
                row["source_concepts"] = ";".join(f.source_concept for f in chosen)
                row["fact_ids"] = ";".join(f.fact_id for f in chosen)
                if prev_source and row["source_concepts"] != prev_source:
                    issues.append({"severity": "low", "concept": spec.name, "period": end,
                                   "description": f"source tag changed from {prev_source} to {row['source_concepts']}"})
                prev_source = row["source_concepts"]
            annual.append(row)
    for f in raw:
        if f.used_for_canonical or f.source_concept.startswith("ifrs-full:"):
            d = asdict(f)
            d["lei"] = lei
            facts_out.append(d)
    for i in issues:
        i.update(entity=entity, detected_at=common.now_iso())
    print(f"{entity}: {len(filings)} filings, fiscal years {fiscal_years[0]} to {fiscal_years[-1]} ({len(fiscal_years)}), "
          f"{len(raw)} numeric facts, {len(issues)} issues")
    return facts_out, annual, issues


def main() -> int:
    facts_all, annual_all, issues_all = [], [], []
    for lei, meta in ISSUERS.items():
        f, a, i = process_issuer(lei, meta)
        facts_all += f
        annual_all += a
        issues_all += i
    n1 = common.write_csv(common.OUT_DIR / "facts_eu.csv", facts_all, FACT_FIELDS)
    n2 = common.write_csv(common.OUT_DIR / "annual_eu.csv", annual_all, ANNUAL_FIELDS)
    n3 = common.write_csv(common.OUT_DIR / "data_issues_eu.csv", issues_all, ISSUE_FIELDS)
    print(f"wrote facts_eu.csv ({n1}), annual_eu.csv ({n2}), data_issues_eu.csv ({n3})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
