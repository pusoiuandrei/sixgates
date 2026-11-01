"""Step 3: FRED DGS10 (10-year Treasury constant maturity yield) as the hurdle input.

Writes out/hurdle_input.json with the latest observation, its date and provenance.
The CSV endpoint needs no API key; the production ingestion will use the FRED API
with the owner's key and store every observation in the ``price``-like series
table (see architecture.md, section 3).
"""

from __future__ import annotations

import csv
import json
import sys

import common

SERIES = "DGS10"
URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES}"


def latest_observation(path) -> dict:
    """Last non-missing observation of a fredgraph CSV (missing values are '.')."""
    last = None
    with path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            value = row.get(SERIES, "").strip()
            if value and value != ".":
                last = {"date": row["observation_date"], "value_pct": float(value)}
    if last is None:
        raise ValueError("no observation found")
    return last


def main() -> int:
    path = common.fetch(URL, common.DATA_DIR / "fred" / f"{SERIES}.csv", force=True)
    obs = latest_observation(path)
    out = {
        "series": SERIES,
        "source_url": URL,
        "sha256": common.sha256_of(path),
        "fetched_at": common.now_iso(),
        "latest_date": obs["date"],
        "latest_value_pct": obs["value_pct"],
        "as_rate": obs["value_pct"] / 100.0,
        "role": "long government bond yield, the floor and reference for the discount hurdle (default total hurdle 10%)",
    }
    (common.OUT_DIR / "hurdle_input.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"{SERIES} latest: {obs['value_pct']}% on {obs['date']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
