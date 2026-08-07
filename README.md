# Mt. Fuji Visibility Archive

Daily archive of Mt. Fuji visibility forecast scores, published as an open dataset.

**What this is:** A machine-readable record of visibility forecasts for the
north (Kawaguchiko) and south (Hakone) sides of Mt. Fuji, archived once per day
since June 2026.
**What this is NOT:** Ground-truth observations. These are *forecasts as they
were published*, kept unmodified. They describe how often Fuji was *expected*
to be visible — not how often it actually was. That distinction matters when
reading any statistic derived from this data.

## Why this exists

[voybird.com/fujivis](https://voybird.com/fujivis) publishes visibility
forecasts for travellers. Any historical statistic shown there is derived from
this archive. Publishing the raw record lets anyone verify those numbers
independently rather than taking them on trust.

## Data source

Visibility scores come from a third-party Japanese meteorological forecast
service. This archive stores the values as retrieved, without modification.
Derived statistics and the display scale used on voybird.com are our own.

## Format

Each day is a single JSON file under `data/daily/`:

| Field | Meaning |
|---|---|
| `date` | Forecast target date (Asia/Tokyo) |
| `fetched_at_jst` | When the value was retrieved (JST) |
| `scores.north/south.am/pm.index` | Visibility index, 0–10 (voybird.com display scale) |
| `scores.north/south.am/pm.raw` | Raw score, 0–100 as provided by the source (archived since 2026-08-07; `null` for earlier dates) |
| `note` | Always flags these as forecasts, not observations |

New scores are archived once daily at 17:00 JST, after the upstream service's
scheduled update. Historical days recovered from the sibling fuji-visibility
service (2026-06-16 → 2026-06-27) carry their original retrieval timestamps.

## Coverage

- Start date: 2026-06-16
- Days archived: 53
- Completeness: 53/53 (see `scripts/validate.py`)
- Index-only period: 2026-06-16 → 2026-08-06 (raw values not retained by the upstream archive before 2026-08-07)
- Dual-scale period: 2026-08-07 onward (index + raw)

## Scripts

- `scripts/aggregate.py` — folds daily JSON files into monthly CSV summaries (pure data processing)
- `scripts/validate.py` — checks the archive for missing days, malformed files and out-of-range values

## Licence

- Data: [CC BY 4.0](LICENSE) — attribution to voybird.com appreciated
- Scripts: [MIT](LICENSE-CODE)

## Maintainer

Citron Chan — Founder, Voybird
[voybird.com](https://voybird.com) · [LinkedIn](https://www.linkedin.com/in/citron-jiyuu/)
