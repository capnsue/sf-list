# sf-list

Scraper for Locus Magazine weekly new book releases, built to analyze SF/fantasy genre trends over time.

## Quick orientation
- See `notes/` for session summaries with key findings and next steps — read the most recent one first
- Scripts: `get_urls.py` (discover URLs), `scraper.py` (scrape books), `explore.py` (pandas analysis), `normalize.py` (genre bucketing)
- Always run scripts with `uv run python <script>`

## Key conventions
- **Always add `time.sleep(1)` between requests** in any scraping loop — be polite to web servers
- Output CSVs are timestamped: `books_YYYYMMDD_HHMMSS.csv`
- `urls.txt` contains all ~565 release page URLs (deduplicated, no `#` anchors)

## Current status (2026-03-13)
- Latest scrape: `books_20260313_211555.csv` — 12,564 books, description field now captured (97% coverage)
- Latest normalized: `books_20260313_211555_normalized.csv` — includes `genre_bucket`, `genre_label`, `year`, `is_cozy`, `media_tie_in`, `description`
- Next: use `description` text to infer genre for ~7,259 pre-2022 Unknown entries, then trend analysis
