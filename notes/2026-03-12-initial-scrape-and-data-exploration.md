# 2026-03-12: Initial Scrape & Data Exploration

## Goal
Test the hypothesis that science fiction novel publishing has declined over time relative to fantasy, horror, and YA, using Locus Magazine's weekly new book release listings as a data source.

## Data Source
**Locus Magazine** — weekly new book release pages at locusmag.com, going back to August 2011.

- Category index: `https://locusmag.com/category/newtitlesbestsellers/`
- ~565 unique release pages discovered via category index crawler
- Pre-2011 data exists on the site but was excluded (see below)

## What We Built

### `get_urls.py`
Crawls the Locus category index pages and collects all "new book releases" URLs, saving them incrementally to `urls.txt`. Found two URL naming conventions:
- `new-book-releases-march-10-2026` (newer format)
- `new-books-7-june-2022` (older format)

### `scraper.py`
Scrapes each URL in `urls.txt` and outputs a timestamped CSV. Handles three distinct page formats that evolved over time:

| Era | Date format | Structure | Genre |
|-----|------------|-----------|-------|
| 2011–~2021 | `August 2011` | Title → Details → Description | Rarely labeled |
| ~2022–~2023 | `June 7, 2022` | Title → Details → Description | Labeled in description |
| ~2024–now | `MM/DD/YYYY` | Title → Description → Details | Labeled at start of description |

Fields extracted: `author`, `title`, `publisher`, `page_count` (int), `publication_date` (normalized to `YYYY-MM-DD`), `genre`, `source_url`, `date_scraped`

## Key Findings

### Dataset
- **11,191 total books** scraped from August 2011 through March 2026
- **470 missing publication dates**
- **5,941 missing genres (~53%)** — mostly pre-2022 entries where genre wasn't labeled by Locus editors

### Books per year (publication date)
| Year | Count |
|------|-------|
| 2011 | 215 (Aug–Dec only) |
| 2012 | 760 |
| 2013 | 823 |
| 2014 | 722 |
| 2015 | 682 |
| 2016 | 690 |
| 2017 | 660 |
| 2018 | 612 |
| 2019 | 667 |
| 2020 | 545 |
| 2021 | 450 |
| 2022 | 986 |
| 2023 | 484 |
| 2024 | 1,069 |
| 2025 | 1,123 |
| 2026 | 206 (Jan–Mar only) |

Small counts for 1899, 2007, 2009, 2010 are parsing noise (dates from book descriptions, not the listing itself).

### Top genres (where labeled, ~6,000 entries)
| Genre | Count |
|-------|-------|
| Fantasy novel | 512 |
| SF novel | 212 |
| Young-adult fantasy novel | 202 |
| Horror novel | 176 |
| Fantasy romance novel | 109 |
| Young-adult horror novel | 56 |
| Epic fantasy novel | 49 |
| Near-future SF novel | 39 |
| Fantasy novella | 39 |
| Urban fantasy novel | 39 |
| Science fiction novel | 22 |

Even with incomplete labeling, Fantasy (512) significantly outnumbers SF (212 + 22 = 234) in the labeled portion.

## Important Caveats
- **August 2011 was a deliberate editorial reset.** A note on the first page states that before this date, Locus explicitly omitted YA, horror, media tie-ins, and self-published books. Pre-2011 data would be systematically biased against those genres and is not comparable.
- **~53% of entries have no genre label.** Genre labeling appears to have been introduced gradually, with more consistent labeling from ~2022 onward. Trend analysis is most reliable for 2022+.
- **Genre text is raw and un-normalized.** "SF novel", "Science fiction novel", "Space opera SF novel" etc. are all separate values. Normalization/bucketing is needed before analysis.

## Next Steps
1. **Re-scrape** — a 2024-era parsing fix was made after the initial scrape; new CSV needed. Also add description text as a saved field to enable genre inference on pre-2022 entries.
2. **Genre normalization** — ✅ done (keyword bucketing in `normalize.py`; outputs `genre_bucket`, `genre_label`, `year`)
3. **Trend analysis** — year-over-year counts per genre bucket, focusing on 2022+ for most reliable genre data
4. **Pre-2022 genre coverage** — ~7,000 entries have no genre label (Locus didn't label consistently before ~2022). Options:
   - **Publisher heuristics** (quick win on existing data) — build a lookup table mapping known genre-specialized publishers (Tor, Baen, Orbit, Scholastic, etc.) to broad buckets
   - **Description keyword matching** — requires re-scrape with description capture first
   - **LLM classification** — highest accuracy, use after the above are exhausted
   - Start by sampling a few entries per year to understand the shape of the problem before committing to an approach

## GitHub
- Public repo created: `sf-list`
- `.gitignore` excludes: `*.csv`, `*.md` (except `CLAUDE.md` and `README.md`), `.venv/`, `__pycache__/`, `.settings.local.json`, `.claude/`
- `urls.txt` is committed (small, took effort to generate, doesn't change often)
