# sf-list

Scraper for Locus Magazine weekly new book releases, built to analyze SF/fantasy genre trends over time.

## Quick orientation
- See `notes/` for session summaries with key findings and next steps — read the most recent one first
- Scripts: `get_urls.py` (discover URLs), `scraper.py` (scrape books), `explore.py` (pandas analysis), `normalize.py` (genre bucketing)
- Always run scripts with `uv run python <script>`

## Key conventions
- **Always add `time.sleep(1)` between requests** in any scraping loop — be polite to web servers
- Output CSVs are timestamped: `books_YYYYMMDD_HHMMSS.csv`
- `urls.txt` contains 1,131 URLs total; 728 unique base pages after stripping `#` anchors

## Current status (2026-03-18)
- Latest scrape: `books_20260318_001543.csv` — 12,583 books (includes March 17 2026 releases)
- Latest normalized: `books_20260318_001543_normalized.csv`
- Description inference done: 5,688 of 7,259 Unknowns resolved (78%) via description text; 1,074 more via publisher heuristics (93.2% total)
- Columns: author, title, publisher, page_count, publication_date, genre, description, source_url, date_scraped, genre_bucket, genre_label, year, is_cozy, media_tie_in, genre_inferred, genre_source
- New buckets added: Tie-In, Short Fiction, Comic (per client feedback)
- **Next: update notebook to use new normalized CSV; do editing pass on methods-paper.md and writeup.md per open-questions.md**
