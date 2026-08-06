# Methodology

## What is archived

One JSON file per day, containing the Mt. Fuji visibility **forecast** values
for the north (Kawaguchiko) and south (Hakone) sides, as published by a
third-party Japanese meteorological forecast service. Values are stored
**unmodified** — this is an archive of forecasts as published, not a record of
ground-truth observations.

## Two scales

| Scale | Range | Meaning |
|---|---|---|
| `raw` | 0–100 | The score exactly as provided by the upstream source. |
| `index` | 0–10 | The display scale used on voybird.com/fujivis, derived from the raw score. |

The `index` is derived from `raw` with a fixed monotonic mapping. The raw
value was not persisted by the upstream archive before 2026-08-07, so earlier
daily files contain `index` only (`raw: null`).

## Timing

- The upstream service publishes updated forecasts on a daily schedule.
- Values are archived once per day at **17:00 JST**, after the upstream
  update has been observed.
- `fetched_at_jst` records the exact retrieval moment.

## Coverage gaps

- 2026-06-28: first day archived (index only).
- 2026-08-07: raw 0–100 values become available in the archive.
- Days with no upstream publication are simply absent; `scripts/validate.py`
  reports the expected vs actual day count.

## Non-goals

- No ground-truth observations (actual visibility measured after the fact).
- No derived analytics beyond the monthly aggregation in `scripts/aggregate.py`.
- No source-identifying information beyond "third-party Japanese
  meteorological forecast service".

## Verification

Any statistic on voybird.com/fujivis that references historical visibility is
derived from this archive. `scripts/validate.py` can be run at any time to
confirm the archive is complete and internally consistent.
