#!/usr/bin/env python3
"""aggregate.py — Fold daily JSON archives into monthly CSV summaries.

Pure data processing: reads every file in data/daily/YYYY-MM-DD.json and
writes one data/monthly/YYYY-MM.csv per calendar month. Does not fetch,
scrape or compute anything beyond aggregation.

Output columns:
  date,north_am_index,north_pm_index,south_am_index,south_pm_index,
  north_am_raw,north_pm_raw,south_am_raw,south_pm_raw

Missing values are written as empty cells.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = REPO_ROOT / "data" / "daily"
MONTHLY_DIR = REPO_ROOT / "data" / "monthly"

COLUMNS = [
    "date",
    "north_am_index", "north_pm_index", "south_am_index", "south_pm_index",
    "north_am_raw", "north_pm_raw", "south_am_raw", "south_pm_raw",
]

SIDES = ("north", "south")
PERIODS = ("am", "pm")


def load_daily_files() -> list[dict]:
    if not DAILY_DIR.is_dir():
        print(f"error: daily directory not found: {DAILY_DIR}", file=sys.stderr)
        sys.exit(1)
    files = sorted(DAILY_DIR.glob("????-??-??.json"))
    records = []
    for path in files:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        records.append(data)
    return records


def to_row(data: dict) -> dict[str, str]:
    row = {"date": data.get("date", "")}
    scores = data.get("scores", {}) or {}
    for side in SIDES:
        for period in PERIODS:
            cell = (scores.get(side, {}) or {}).get(period, {}) or {}
            index_val = cell.get("index")
            raw_val = cell.get("raw")
            row[f"{side}_{period}_index"] = "" if index_val is None else str(index_val)
            row[f"{side}_{period}_raw"] = "" if raw_val is None else str(raw_val)
    return row


def main() -> None:
    records = load_daily_files()
    if not records:
        print("no daily files found; nothing to aggregate")
        return

    by_month: dict[str, list[dict[str, str]]] = defaultdict(list)
    for rec in records:
        month = str(rec.get("date", ""))[:7]
        if not month:
            continue
        by_month[month].append(to_row(rec))

    MONTHLY_DIR.mkdir(parents=True, exist_ok=True)
    for month, rows in sorted(by_month.items()):
        rows.sort(key=lambda r: r["date"])
        out_path = MONTHLY_DIR / f"{month}.csv"
        with out_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {out_path.name}: {len(rows)} days")


if __name__ == "__main__":
    main()
