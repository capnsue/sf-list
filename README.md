# sf-list

Scrapes [Locus Magazine](https://locusmag.com)'s weekly new book release listings to analyze genre trends in speculative fiction publishing over time.

## The hypothesis
Science fiction novel publishing has declined over the years, while fantasy, horror, and YA have grown.

## Data
~11,000 books scraped from Locus Magazine's weekly new release pages, covering August 2011 through present. Fields: author, title, publisher, page count, publication date, genre, source URL, date scraped.

## Scripts

| Script | What it does |
|--------|-------------|
| `get_urls.py` | Crawls the Locus category index and saves all release page URLs to `urls.txt` |
| `scraper.py` | Scrapes each URL in `urls.txt` and outputs a timestamped CSV |
| `explore.py` | Loads the latest CSV into pandas for exploration and analysis |

## Usage

```bash
uv sync
uv run python scraper.py
```

## Notes
- Data starts at August 2011 — this was a deliberate editorial reset by Locus. Pre-2011 listings excluded YA and horror by policy, making them not comparable.
- Genre labeling is sparse before ~2022. Trend analysis is most reliable from 2022 onward.
