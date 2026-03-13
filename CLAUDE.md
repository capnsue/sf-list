# sf-list

Scraper for Locus Magazine weekly new book releases, built to analyze SF/fantasy genre trends over time.

## Quick orientation
- See `notes/` for session summaries with key findings and next steps — read the most recent one first
- Scripts: `get_urls.py` (discover URLs), `scraper.py` (scrape books), `explore.py` (pandas analysis)
- Always run scripts with `uv run python <script>`

## Key conventions
- **Always add `time.sleep(1)` between requests** in any scraping loop — be polite to web servers
- Output CSVs are timestamped: `books_YYYYMMDD_HHMMSS.csv`
- `urls.txt` contains all ~565 release page URLs (deduplicated, no `#` anchors)

## Current status (2026-03-12)
- Initial scrape done: 11,191 books in `books_20260312_182528.csv`
- A 2024-era genre parsing fix was made after the scrape — **re-scrape needed**
- Next: re-scrape, then genre normalization (stopwords + rapidfuzz bucketing)
