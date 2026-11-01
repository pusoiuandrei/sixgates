"""Shared helpers for the SixGates data spike: paths, rate-limited HTTP, manifest.

Downloads are treated as untrusted data. They live under ``data/`` and are never
executed or imported; scripts only parse them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import time
from datetime import datetime, timezone
from typing import Any, Iterable

import requests

SPIKE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = SPIKE_DIR / "data"
OUT_DIR = SPIKE_DIR / "out"
MANIFEST = DATA_DIR / "manifest.jsonl"

# SEC fair-access policy: identify yourself. Production must use the owner's
# real contact address here (see architecture.md, section 3).
SEC_USER_AGENT = "SixGates research spike contact@sixgates.local"
SEC_HEADERS = {"User-Agent": SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"}

# Self-imposed ceiling: 5 requests per second (SEC allows 10).
_MIN_INTERVAL_S = 0.21
_last_request_at = 0.0


def now_iso() -> str:
    """Current UTC time as an ISO 8601 string with seconds precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_of(path: pathlib.Path) -> str:
    """SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _throttle() -> None:
    global _last_request_at
    wait = _MIN_INTERVAL_S - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def fetch(url: str, dest: pathlib.Path, headers: dict[str, str] | None = None,
          force: bool = False, timeout: int = 120) -> pathlib.Path:
    """Download ``url`` into ``dest`` (cached) and append a manifest line.

    The manifest records url, destination, sha256, size and fetch time so every
    downstream number can be traced back to a concrete downloaded artefact.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        return dest
    _throttle()
    resp = requests.get(url, headers=headers or {}, timeout=timeout)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    with MANIFEST.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "url": url,
            "dest": str(dest.relative_to(SPIKE_DIR)),
            "sha256": sha256_of(dest),
            "bytes": dest.stat().st_size,
            "fetched_at": now_iso(),
            "status": resp.status_code,
        }) + "\n")
    return dest


def load_json(path: pathlib.Path) -> Any:
    """Parse a downloaded JSON file (data only, never code)."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> int:
    """Write dict rows to CSV with a fixed column order; returns the row count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            n += 1
    return n


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    """Read a CSV written by :func:`write_csv` back into dict rows."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def fact_id(*parts: Any) -> str:
    """Deterministic 16-hex-char identifier for a fact, from its provenance tuple."""
    raw = "|".join(str(p) for p in parts).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]
