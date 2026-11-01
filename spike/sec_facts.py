"""Step 1: SEC EDGAR companyfacts to annual facts with full provenance.

Outputs
-------
out/facts_us.csv    every candidate fact considered (selected and superseded)
out/annual_us.csv   one row per (entity, fiscal year, canonical concept)
out/data_issues.csv appended with the issues detected here

Selection rules (see architecture.md, section 3):
* only 10-K and 10-K/A forms; duration facts of 340 to 380 days (52/53-week
  years), instant facts at the fiscal year end;
* fiscal year label = ``fy`` of the 10-K in which that period end is the focus
  period (the ``fy``/``fp`` fields describe the filing, not the fact);
* for the same (tag, unit, period) the latest filed value wins, earlier ones
  are kept and marked superseded; a different earlier value is a restatement;
* canonical concepts follow concept_map priorities; nothing is estimated.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date

import common
from concept_map import REQUIRED_FOR_TEN_YEAR_RULE, US_GAAP, ConceptSpec

COMPANIES: dict[int, str] = {320193: "AAPL", 21344: "KO", 1059556: "MCO"}
ANNUAL_FORMS = {"10-K", "10-K/A"}
MIN_DAYS, MAX_DAYS = 340, 380

FACT_FIELDS = [
    "fact_id", "entity", "cik", "canonical_concept", "source_concept", "unit",
    "period_start", "period_end", "is_instant", "fiscal_year", "value", "decimals",
    "accession", "form", "filed", "fy", "fp", "frame", "selected", "superseded_by",
    "is_restated", "used_for_canonical", "extracted_at", "source_url",
]
ANNUAL_FIELDS = [
    "entity", "cik", "fiscal_year", "period_end", "concept", "value", "unit",
    "status", "source_concepts", "fact_ids", "note",
]
ISSUE_FIELDS = ["entity", "severity", "concept", "period", "description", "detected_at"]


@dataclass
class RawFact:
    """One companyfacts entry with its provenance, before selection."""

    fact_id: str
    entity: str
    cik: int
    canonical_concept: str
    source_concept: str
    unit: str
    period_start: str
    period_end: str
    is_instant: bool
    fiscal_year: int | None
    value: float
    decimals: str
    accession: str
    form: str
    filed: str
    fy: int | None
    fp: str
    frame: str
    selected: bool = False
    superseded_by: str = ""
    is_restated: bool = False
    used_for_canonical: bool = False
    extracted_at: str = ""
    source_url: str = ""


# Per-entity overrides: (entity, canonical concept, fiscal year) -> (tag, reason).
# This is the spike version of the ``concept_override`` table. Every entry must
# point to a filed fact and carry the evidence that justifies it.
OVERRIDES: dict[tuple[str, str, int], tuple[str, str]] = {
    ("AAPL", "d_and_a", 2015): (
        "DepreciationAmortizationAndAccretionNet",
        "In the FY2017 10-K Apple reused DepreciationDepletionAndAmortization for the PP&E-only depreciation "
        "in the notes (9,200) while the cash-flow line (11,257) carried DepreciationAmortizationAndAccretionNet; "
        "the cash-flow statement value is the one the method needs.",
    ),
}


def _days(start: str, end: str) -> int:
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def _precision(value: float) -> float:
    """Power of ten implied by trailing zeros (1 for a non-round value)."""
    iv = abs(int(round(value)))
    if iv == 0:
        return 1.0
    p = 1
    while iv % (p * 10) == 0 and p < 10 ** 12:
        p *= 10
    return float(p)


def differs_beyond_rounding(a: float, b: float) -> bool:
    """True when two reported values differ even at the coarser of their precisions."""
    p = max(_precision(a), _precision(b))
    return round(a / p) != round(b / p)


def fiscal_year_map(facts: dict) -> tuple[dict[str, int], list[dict]]:
    """Map each fiscal-year-end date to its fiscal year label.

    For every 10-K accession, the focus period is the 12-month duration with the
    latest end date; its end is labelled with the filing's ``fy``. Returns the
    map plus a list of data issues (label conflicts, fy/end-year mismatches).
    """
    focus: dict[str, tuple[str, int]] = {}  # accn -> (max_end, fy)
    for body in facts.get("us-gaap", {}).values():
        for entries in body["units"].values():
            for e in entries:
                if e.get("form") not in ANNUAL_FORMS or e.get("fp") != "FY" or "start" not in e:
                    continue
                if not (MIN_DAYS <= _days(e["start"], e["end"]) <= MAX_DAYS):
                    continue
                cur = focus.get(e["accn"])
                if cur is None or e["end"] > cur[0]:
                    focus[e["accn"]] = (e["end"], int(e["fy"]))
    end_to_fy: dict[str, int] = {}
    issues: list[dict] = []
    for accn, (end, fy) in sorted(focus.items()):
        if end in end_to_fy and end_to_fy[end] != fy:
            issues.append({"severity": "medium", "concept": "fiscal_year", "period": end,
                           "description": f"fy label conflict for period end {end}: {end_to_fy[end]} vs {fy} ({accn}); kept {fy}"})
        end_to_fy[end] = fy
        if fy != int(end[:4]) and int(end[5:7]) > 3:
            issues.append({"severity": "low", "concept": "fiscal_year", "period": end,
                           "description": f"fy label {fy} differs from period end year {end[:4]} ({accn}); label kept, check convention"})
    return end_to_fy, issues


def collect_raw_facts(facts: dict, spec: ConceptSpec, entity: str, cik: int,
                      end_to_fy: dict[str, int], source_url: str) -> list[RawFact]:
    """Gather all 10-K facts for every tag the spec may use."""
    tags = list(spec.candidates) + list(spec.fallbacks) + [t for comp in spec.components for t in comp]
    out: list[RawFact] = []
    for tag in tags:
        body = facts.get("us-gaap", {}).get(tag)
        if not body:
            continue
        for unit, entries in body["units"].items():
            if unit != spec.unit:
                continue
            for e in entries:
                if e.get("form") not in ANNUAL_FORMS:
                    continue
                is_instant = "start" not in e
                if is_instant != (spec.kind == "instant"):
                    continue
                if not is_instant and not (MIN_DAYS <= _days(e["start"], e["end"]) <= MAX_DAYS):
                    continue
                start = "" if is_instant else e["start"]
                out.append(RawFact(
                    fact_id=common.fact_id(cik, tag, unit, start, e["end"], e["accn"]),
                    entity=entity, cik=cik, canonical_concept=spec.name, source_concept=f"us-gaap:{tag}",
                    unit=unit, period_start=start, period_end=e["end"], is_instant=is_instant,
                    fiscal_year=end_to_fy.get(e["end"]), value=float(e["val"]),
                    decimals="",  # not exposed by companyfacts; comes from the filing instance
                    accession=e["accn"], form=e["form"], filed=e["filed"], fy=e.get("fy"), fp=e.get("fp", ""),
                    frame=e.get("frame", ""), extracted_at=common.now_iso(), source_url=source_url,
                ))
    return out


def select_latest(raw: list[RawFact]) -> list[dict]:
    """Mark the latest-filed fact per (tag, unit, period) as selected; flag restatements."""
    groups: dict[tuple, list[RawFact]] = defaultdict(list)
    for f in raw:
        groups[(f.source_concept, f.unit, f.period_start, f.period_end)].append(f)
    issues: list[dict] = []
    for key, items in groups.items():
        items.sort(key=lambda f: (f.filed, f.accession))
        winner = items[-1]
        winner.selected = True
        for older in items[:-1]:
            older.superseded_by = winner.fact_id
            if older.value == winner.value:
                continue
            concept = winner.canonical_concept or winner.source_concept.split(":", 1)[-1]
            if differs_beyond_rounding(older.value, winner.value):
                winner.is_restated = True
                issues.append({"severity": "medium", "concept": concept, "period": winner.period_end,
                               "description": f"restated {winner.source_concept}: {older.value:,.0f} ({older.accession}, filed {older.filed}) "
                                              f"to {winner.value:,.0f} ({winner.accession}, filed {winner.filed}); latest kept"})
            else:
                issues.append({"severity": "info", "concept": concept, "period": winner.period_end,
                               "description": f"rounding-only difference on {winner.source_concept}: {older.value:,.0f} vs {winner.value:,.0f}; latest kept"})
    return issues


def resolve_year(spec: ConceptSpec, lookup, end: str, fy: int, override: tuple[str, str] | None,
                 prefix: str) -> tuple[list, str, str, list[dict]]:
    """Pick the facts behind one canonical value for one fiscal year.

    Order: per-entity override, synonyms (latest filed wins, disagreement flagged),
    fallbacks (noted), components (summed, absences flagged). ``lookup`` maps
    (source_concept, period_end) to a selected fact. Returns (facts, status,
    note, issues). Shared by the SEC and ESEF pipelines.
    """
    issues: list[dict] = []
    if override:
        f = lookup.get((f"{prefix}{override[0]}", end))
        if f:
            issues.append({"severity": "info", "concept": spec.name, "period": end,
                           "description": f"per-entity override to {override[0]}: {override[1]}"})
            return [f], "ok", f"override: {override[1]}", issues
    present = [lookup[(f"{prefix}{t}", end)] for t in spec.candidates if (f"{prefix}{t}", end) in lookup]
    if present:
        latest = max(present, key=lambda f: f.filed)  # ties keep priority order (max returns the first)
        others = [p for p in present if p is not latest and differs_beyond_rounding(p.value, latest.value)]
        if others:
            desc = "; ".join(f"{p.source_concept}={p.value:,.0f} ({p.accession})" for p in [latest] + others)
            issues.append({"severity": "high", "concept": spec.name, "period": end,
                           "description": f"synonym tags disagree for FY{fy}: {desc}; latest filed kept, needs an override or a reconciliation"})
            return [latest], "ambiguous", "synonym tags disagree: " + desc, issues
        return [latest], "ok", "", issues
    for t in spec.fallbacks:
        f = lookup.get((f"{prefix}{t}", end))
        if f:
            issues.append({"severity": "low", "concept": spec.name, "period": end,
                           "description": f"fallback tag {t} used for FY{fy} (no synonym tag filed)"})
            return [f], "ok", f"fallback tag {t}", issues
    chosen, absent = [], []
    for comp in spec.components:
        hit = next((lookup.get((f"{prefix}{t}", end)) for t in comp if (f"{prefix}{t}", end) in lookup), None)
        if hit:
            chosen.append(hit)
        else:
            absent.append("|".join(comp))
    if chosen:
        if absent:
            issues.append({"severity": "low" if spec.absent_ok else "medium", "concept": spec.name, "period": end,
                           "description": f"partial sum for FY{fy}, components absent: {', '.join(absent)}"})
            return chosen, "partial_sum", f"components absent: {', '.join(absent)}", issues
        return chosen, "ok", "sum of components", issues
    sev = "high" if spec.name in REQUIRED_FOR_TEN_YEAR_RULE else ("low" if spec.absent_ok else "medium")
    issues.append({"severity": sev, "concept": spec.name, "period": end,
                   "description": f"no standard-taxonomy fact for FY{fy} (candidates: {', '.join(spec.candidates + spec.fallbacks)}); marked missing"})
    return [], "missing", "", issues


def annual_rows(spec: ConceptSpec, raw: list[RawFact], entity: str, cik: int,
                fiscal_years: dict[int, str]) -> tuple[list[dict], list[dict]]:
    """Build the canonical annual value per fiscal year from selected facts."""
    lookup: dict[tuple[str, str], RawFact] = {(f.source_concept, f.period_end): f for f in raw if f.selected}
    rows: list[dict] = []
    issues: list[dict] = []
    prev_source = None
    for fy in sorted(fiscal_years):
        end = fiscal_years[fy]
        chosen, status, note, more = resolve_year(spec, lookup, end, fy, OVERRIDES.get((entity, spec.name, fy)), "us-gaap:")
        issues += more
        row = {"entity": entity, "cik": cik, "fiscal_year": fy, "period_end": end, "concept": spec.name,
               "value": "", "unit": spec.unit, "status": status, "source_concepts": "", "fact_ids": "", "note": note}
        if chosen:
            for f in chosen:
                f.used_for_canonical = True
            row["value"] = f"{sum(f.value for f in chosen):.0f}"
            row["source_concepts"] = ";".join(f.source_concept for f in chosen)
            row["fact_ids"] = ";".join(f.fact_id for f in chosen)
            src = row["source_concepts"]
            if prev_source and src != prev_source:
                issues.append({"severity": "low", "concept": spec.name, "period": end,
                               "description": f"source tag changed from {prev_source} to {src}"})
            prev_source = src
        rows.append(row)
    return rows, issues


def split_check(annual: list[dict]) -> list[dict]:
    """Flag share-count jumps that betray an unadjusted stock split across filings.

    "Latest filed wins" mixes pre-split and post-split comparatives when a split
    happens between filings (Apple FY2017 vs FY2018). Per-share series need a
    split-factor table before use; here we only make the problem visible.
    """
    issues: list[dict] = []
    shares = sorted((r for r in annual if r["concept"] == "diluted_shares" and r["value"]), key=lambda r: r["fiscal_year"])
    for prev, cur in zip(shares, shares[1:]):
        ratio = float(cur["value"]) / float(prev["value"])
        if ratio > 1.5 or ratio < 1 / 1.5:
            issues.append({"severity": "high", "concept": "diluted_shares", "period": cur["period_end"],
                           "description": f"share count ratio {ratio:.2f} vs FY{prev['fiscal_year']}: comparatives restated for a split "
                                          f"in a later filing; per-share series unusable without a split-factor table"})
    return issues


def process_company(cik: int, entity: str) -> tuple[list[dict], list[dict], list[dict]]:
    """Run the full selection for one company."""
    path = common.DATA_DIR / "sec" / f"companyfacts_CIK{cik:010d}.json"
    source_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    common.fetch(source_url, path, headers=common.SEC_HEADERS)
    facts = common.load_json(path)["facts"]
    end_to_fy, issues = fiscal_year_map(facts)
    fiscal_years = {fy: end for end, fy in end_to_fy.items()}
    issues.append({"severity": "info", "concept": "all", "period": "",
                   "description": "companyfacts does not expose decimals or company extension tags; both need the filing instance"})
    for fy, end in sorted(fiscal_years.items()):
        prev_end = fiscal_years.get(fy - 1)
        if prev_end:
            days = _days(prev_end, end)
            if days not in (365, 366):
                issues.append({"severity": "info", "concept": "fiscal_year", "period": end,
                               "description": f"FY{fy} spans {days} days (52/53-week calendar); ratios use the reported period as is"})
    all_facts: list[dict] = []
    annual: list[dict] = []
    for spec in US_GAAP:
        raw = collect_raw_facts(facts, spec, entity, cik, end_to_fy, source_url)
        issues += select_latest(raw)
        rows, more = annual_rows(spec, raw, entity, cik, fiscal_years)
        annual += rows
        issues += more
        all_facts += [asdict(f) for f in raw]
    issues += split_check(annual)
    for i in issues:
        i.update(entity=entity, detected_at=common.now_iso())
    return all_facts, annual, issues


def main() -> int:
    facts_all: list[dict] = []
    annual_all: list[dict] = []
    issues_all: list[dict] = []
    for cik, entity in COMPANIES.items():
        f, a, i = process_company(cik, entity)
        facts_all += f
        annual_all += a
        issues_all += i
        years = sorted({r["fiscal_year"] for r in a})
        print(f"{entity}: {len(f)} raw facts, fiscal years {years[0]} to {years[-1]} ({len(years)}), {len(i)} issues")
    n1 = common.write_csv(common.OUT_DIR / "facts_us.csv", facts_all, FACT_FIELDS)
    n2 = common.write_csv(common.OUT_DIR / "annual_us.csv", annual_all, ANNUAL_FIELDS)
    n3 = common.write_csv(common.OUT_DIR / "data_issues_us.csv", issues_all, ISSUE_FIELDS)
    print(f"wrote facts_us.csv ({n1}), annual_us.csv ({n2}), data_issues_us.csv ({n3})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
