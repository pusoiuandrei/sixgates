# SixGates data spike (phase 1)

Real-data spike behind `phase1/architecture.md`, section 8. It pulls primary
filings for five companies, normalises them into canonical concepts with full
provenance, runs the formula engine, and reconciles the latest fiscal year to
the primary documents. It is a spike, not the product: the code is small on
purpose and may seed the real repository.

Companies: Apple (CIK 320193), Coca-Cola (CIK 21344), Moody's (CIK 1059556)
from SEC EDGAR companyfacts; LVMH (LEI IOG4E947OATN0KJYSD45) and OMV Petrom
(LEI 549300UKYDM6L8HEPU79) from filings.xbrl.org (ESEF); FRED DGS10 for the
hurdle input.

## Layout

```
spike/
  common.py        rate-limited HTTP with a download manifest, CSV helpers
  concept_map.py   canonical concepts -> us-gaap / ifrs-full candidate tags
  sec_facts.py     step 1: companyfacts -> out/facts_us.csv, out/annual_us.csv
  esef_facts.py    step 2: xBRL-JSON   -> out/facts_eu.csv, out/annual_eu.csv
  fred.py          step 3: DGS10       -> out/hurdle_input.json
  formulas.py      step 4: pure, versioned formula engine
  tests/           pytest cases with expected values from the letters
  run_spike.py     step 5: out/metrics.csv, out/spike_report.md (Romanian)
  reconcile.py     step 6: out/reconciliation.md (Romanian)
  data/            downloads only (untrusted data, never executed)
  out/             results
```

## Run

Python 3.13 with `requests`, `pandas` (unused by the scripts, available),
`beautifulsoup4`, `lxml` and `pytest`. From this directory:

```
python3 sec_facts.py      # downloads companyfacts and submissions (SEC User-Agent header set)
python3 esef_facts.py     # downloads the filing index and xBRL-JSON files
python3 fred.py           # downloads the DGS10 CSV
python3 -m pytest tests/  # 22 known-result tests
python3 run_spike.py      # metrics and the Romanian report
python3 reconcile.py      # downloads the primary documents and reconciles
```

Downloads are cached under `data/`; delete a file to refetch it. Every download
is logged in `data/manifest.jsonl` with URL, sha256, size and time.

## Rules the code follows

* SEC requests carry `User-Agent: SixGates research spike contact@sixgates.local`
  and stay under 5 requests per second. Production must use the owner's real
  contact address (SEC fair-access policy).
* Nothing is estimated or interpolated. A concept that is not filed is
  `missing`; a sum with an absent component is `partial_sum`; synonym tags
  that disagree are `ambiguous`; an identity used instead of a tag is
  `derived_identity`. Every status is also written to the data issue logs.
* Among duplicates of the same (tag, period) the latest filed value wins and
  earlier ones are kept as `superseded_by`; a different earlier value is a
  restatement (logged with both values), a rounding-only difference is info.
* Per-entity overrides (`OVERRIDES` in `sec_facts.py` and `esef_facts.py`)
  point to a filed fact and carry the reason; they are logged as issues.
* Every formula returns a `Result` with value, fact ids, formula id, version,
  unit, status and flags; division by a non-positive tangible capital is
  refused and flagged.

## Outputs

* `out/facts_us.csv`, `out/facts_eu.csv`: every candidate fact with provenance
  (tag, accession or ESEF id, filed date, frame, unit, selected, superseded_by).
* `out/annual_us.csv`, `out/annual_eu.csv`: one row per entity, fiscal year and
  canonical concept with value, status, source tags and fact ids.
* `out/data_issues_*.csv`: the data issue log.
* `out/metrics.csv`: every derived value with formula id, version, inputs,
  status and flags.
* `out/spike_report.md`, `out/reconciliation.md`: the Romanian reports.
* `out/hurdle_input.json`: the DGS10 observation used as hurdle reference.
