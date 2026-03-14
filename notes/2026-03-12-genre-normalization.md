# 2026-03-12: Genre Normalization

## What We Built

### `normalize.py`
Reads the most recent `books_2*.csv` (or a filename passed as arg) and outputs `*_normalized.csv` with three new columns:

- **`genre_bucket`** — broad category: SF, Fantasy, Horror, YA, Romance, Non-fiction, Other, Unknown
- **`genre_label`** — raw genre with format words stripped ("novel", "novella", etc.)
- **`year`** — publication year as integer (derived from `publication_date`)

Bucketing is keyword-based (`re.search`), applied in priority order:
1. YA — "young-adult", "young adult", "middle-grade", standalone "ya"
2. SF — "sf", "science fiction", "space opera", "cyberpunk", "solarpunk", "biopunk"
3. Horror — "horror"
4. Romance — "romance"
5. Fantasy — "fantasy"
6. Non-fiction — "non-fiction", "art book", "graphic novel", "reference"
7. Other — labeled but no keyword matched
8. Unknown — no label at all

No fuzzy matching — the Locus genre strings are structured enough that keywords suffice.

**Multi-label decision:** first-match-wins for now. If friend wants YA broken down by subgenre, add a `genre_subbucket` column then.

## Key Numbers (from `books_20260312_200621_normalized.csv`)

| Bucket | Count | % |
|--------|-------|---|
| Unknown | 7,259 | 57.8% |
| Fantasy | 1,441 | 11.5% |
| Other | 1,078 | 8.6% |
| SF | 963 | 7.7% |
| YA | 870 | 6.9% |
| Horror | 586 | 4.7% |
| Romance | 293 | 2.3% |
| Non-fiction | 74 | 0.6% |

### 2022+ trend (most reliable — genre labeling consistent from here)

| Year | SF | Fantasy | Horror | YA | Romance |
|------|----|---------|--------|----|---------|
| 2022 | 202 | 280 | 113 | 178 | 37 |
| 2023 | 96 | 129 | 64 | 93 | 16 |
| 2024 | 197 | 321 | 136 | 192 | 76 |
| 2025 | 172 | 314 | 169 | 185 | 116 |
| 2026 | 36 | 64 | 26 | 33 | 27 |

Fantasy is consistently ~1.8× SF. Directionally supports the hypothesis.

## "Other" Bucket Notes
Top entries to potentially add rules for (future):
- `Supernatural mystery/thriller` → could → Horror
- `Paranormal mystery` → could → Horror
- `Star Trek/Star Wars/Gaming tie-in` → could → SF or a Tie-in bucket
- `, about a...` / `— where some have...` — scraping artifacts, will be fixed in re-scrape

## What Was Sent to Friend
`books_20260312_200621_normalized.csv` with a plain-English explanation of all columns and bucket definitions.

## Next Steps
1. **Re-scrape** — still needed (2024-era parsing fix made after initial scrape). Also add description text as a saved field.
2. **Pre-2022 genre coverage** — ~7,000 Unknown entries. Plan:
   - Sample a few entries per year first to understand the problem
   - Publisher heuristics as quick win (Tor/Baen/Orbit → SF/Fantasy, Scholastic → YA, etc.)
   - Description keyword matching after re-scrape
   - LLM classification as last resort
3. **Trend analysis** — once genre coverage is better, do year-over-year charts
4. **Await friend feedback** — he may have opinions on which buckets matter / subgenre breakdowns
