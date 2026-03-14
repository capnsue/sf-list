# 2026-03-13: Description Capture & Re-scrape

## What We Did

### Updated `normalize.py` with friend's feedback
- Removed Romance bucket — entries now fall to Fantasy or SF naturally
- Added `is_cozy` column — boolean flag, True if genre contains "cozy"
- Added `media_tie_in` column — "Media Tie-In" if genre contains "tie-in", else empty
- Added friend's keyword table to Other-bucket refinements:
  - Fantasy: romantasy, vampire, zombie, steampunk, fable, folkloric, magic realism, magical elements, weird western
  - Horror: ghost, gothic, haunted, paranormal, supernatural
  - SF: sci-fi, alternate history, apocalyptic, dystopian, near-future, post-apocalyptic

### Updated `scraper.py`
- Added `description` field — saves the full description paragraph for each book
- Reduced sleep from 1s to 0.5s (didn't meaningfully speed up scrape — network latency dominates)

### Re-scraped
- New CSV: `books_20260313_211555.csv`
- 12,564 books, 12,238 with description text (97% coverage)
- Numbers identical to previous scrape — data is stable and consistent

## Current Normalized Output (`books_20260313_211555_normalized.csv`)

| Bucket | Count | % |
|--------|-------|---|
| Unknown | 7,259 | 57.8% |
| Fantasy | 1,639 | 13.0% |
| SF | 1,062 | 8.5% |
| Other | 895 | 7.1% |
| YA | 870 | 6.9% |
| Horror | 766 | 6.1% |
| Non-fiction | 73 | 0.6% |

### 2022+ trend

| Year | SF | Fantasy | Horror | YA |
|------|----|---------|--------|----|
| 2022 | 225 | 290 | 149 | 178 |
| 2023 | 106 | 135 | 77 | 93 |
| 2024 | 210 | 371 | 178 | 192 |
| 2025 | 192 | 411 | 214 | 185 |
| 2026 | 44 | 83 | 34 | 33 |

### Cozy trend (2022+)
1 → 2 → 7 → 20 → 3 (2026 partial). Clear upward trend.

## Columns in current normalized CSV
`author, title, publisher, page_count, publication_date, genre, description, source_url, date_scraped, genre_bucket, genre_label, year, is_cozy, media_tie_in`

## Next Steps
1. **Pre-2022 genre coverage** — ~7,259 Unknown entries. Now that we have description text, approach:
   - Keyword match on `description` field using existing BUCKET_RULES patterns
   - Only apply to rows where `genre_bucket == "Unknown"`
   - Sample a few per year first to validate quality before bulk-applying
2. **Publisher heuristics** — fallback for entries with no description either
3. **Trend analysis** — year-over-year charts, the actual end goal for friend
4. **Await further friend feedback** on buckets/subgenres
