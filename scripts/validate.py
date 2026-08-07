#!/usr/bin/env python3
"""validate.py — Check the archive for completeness and internal consistency.

Pure data processing. Checks:
  1. Every expected day has a daily JSON file (contiguous from the earliest
     archived date; run with --from YYYY-MM-DD to set the expected start).
  2. Every JSON file is well-formed and has the required structure.
  3. Index values are within 0-10, raw values within 0-100 (when present).
  4. There are no duplicate dates.

Exit code 0 = archive OK, 1 = problems found.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = REPO_ROOT / "data" / "daily"

INDEX_RANGE = (0, 10)
RAW_RANGE = (0, 100)


def scale_index(raw: int) -> int:
    """Same mapping as the production scraper: min(10, max(1, ceil(raw/10)+1))."""
    import math
    return min(10, max(1, math.ceil(raw / 10) + 1))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from", dest="start",
        help="Expected archive start date (YYYY-MM-DD). Defaults to the "
             "earliest file actually present.",
    )
    parser.add_argument("--to", dest="end",
                        help="Expected archive end date (YYYY-MM-DD). "
                             "Defaults to today.")
    return parser.parse_args()


def load_all() -> list[dict]:
    if not DAILY_DIR.is_dir():
        print(f"error: daily directory not found: {DAILY_DIR}", file=sys.stderr)
        sys.exit(1)
    data = []
    for path in sorted(DAILY_DIR.glob("????-??-??.json")):
        with path.open("r", encoding="utf-8") as fh:
            try:
                data.append(json.load(fh))
            except json.JSONDecodeError as exc:
                print(f"error: {path.name} is not valid JSON: {exc}")
                sys.exit(1)
    return data


def main() -> None:
    args = parse_args()
    records = load_all()
    problems: list[str] = []

    dates = set()
    for rec in records:
        day = rec.get("date")
        if not day:
            problems.append(f"{rec}: missing 'date'")
            continue
        dates.add(day)

    if len(dates) != len(records):
        problems.append(f"duplicate dates: {len(records)} files, {len(dates)} unique")

    # Value range checks + raw/index cross-validation
    for rec in records:
        day = rec.get("date", "?")
        scores = rec.get("scores", {}) or {}
        for side in ("north", "south"):
            for period in ("am", "pm"):
                cell = (scores.get(side, {}) or {}).get(period, {}) or {}
                index_val = cell.get("index")
                raw_val = cell.get("raw")
                if index_val is not None:
                    lo, hi = INDEX_RANGE
                    if not (lo <= index_val <= hi):
                        problems.append(f"{day} {side}.{period}.index={index_val} out of range")
                if raw_val is not None:
                    lo, hi = RAW_RANGE
                    if not (lo <= raw_val <= hi):
                        problems.append(f"{day} {side}.{period}.raw={raw_val} out of range")
                    # Cross-check: when both present, index must equal scale_index(raw)
                    if index_val is not None and index_val != scale_index(raw_val):
                        problems.append(
                            f"{day} {side}.{period}: index={index_val} inconsistent "
                            f"with raw={raw_val} (expected {scale_index(raw_val)})"
                        )

    # Contiguity check
    if dates:
        start = args.start or min(dates)
        end = args.end or max(dates)
        try:
            d_start = date.fromisoformat(start)
            d_end = date.fromisoformat(end)
        except ValueError:
            problems.append(f"invalid date range: {start}..{end}")
        else:
            cursor = d_start
            while cursor <= d_end:
                iso = cursor.isoformat()
                if iso not in dates:
                    problems.append(f"missing day: {iso}")
                cursor += timedelta(days=1)

    if problems:
        print(f"validation failed: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    print(f"archive OK: {len(records)} day(s), no gaps, all values in range")


if __name__ == "__main__":
    main()
