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

## Current status (2026-03-12)
- Re-scrape done: 12,564 books in `books_20260312_200621.csv`
- Genre normalization done: `normalize.py` outputs `*_normalized.csv` with `genre_bucket`, `genre_label`, `year` columns
- Normalized data sent to friend for review
- **Re-scrape still needed** — add description text capture, fix 2024-era parsing
- Next: pre-2022 genre coverage (publisher heuristics → description keywords → LLM), then trend analysis
