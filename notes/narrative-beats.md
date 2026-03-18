# Narrative beats — for story doc

## The hypothesis
Friend believes SF publishing has declined relative to Fantasy, Horror, YA.
Data source: Locus Magazine weekly new book release pages, Aug 2011–Mar 2026, ~565 pages.

## What we built (and in what order)
1. `get_urls.py` — crawled Locus category index to discover all ~565 URLs, saved to urls.txt
2. `scraper.py` — scraped each page, extracted author/title/publisher/page_count/pub_date/genre
3. `explore.py` — first look at the data with pandas
4. `normalize.py` — genre bucketing, evolved significantly over two sessions

## The three page format eras (a key discovery)
Locus changed their page format multiple times:
- 2011–2021: Title → Details → Description (genre rarely labeled)
- 2022–2023: Title → Details → Description (genre labeled in description)
- 2024–now: Title → Description → Details (genre labeled at start of description)
Scraper handles all three. The 2024-era fix was a key debugging moment.

## First scrape results
- 11,191 books
- ~53% missing genre (pre-2022 Locus didn't label consistently)
- Top genres: Fantasy novel (512), SF novel (212), YA fantasy (202), Horror (176)
- Even with incomplete data, Fantasy >> SF

## Genre normalization journey
### Session 1: keyword bucketing
- Built BUCKET_RULES: priority order YA → SF → Horror → Romance → Fantasy → Non-fiction
- Keyword matching, no fuzzy — data was structured enough
- First pass: 5,305 labeled entries bucketed

### Friend's feedback (between sessions)
- Remove Romance — should fold into Fantasy/SF
- Add `is_cozy` boolean column (cozy is a trend he wants to track)
- Add `media_tie_in` secondary label
- Provided a table of ~20 keywords → buckets for Other entries
  (supernatural→Horror, paranormal→Horror, dystopian→SF, romantasy→Fantasy, etc.)

### Re-scrape #1
- Added description text capture to scraper (genre_candidate paragraph)
- Reduced sleep from 1s to 0.5s (didn't speed things up — network latency dominates)
- 12,564 books, 97% with description text

### Description-based inference (Pass 1)
- Key insight: pre-2022 descriptions often START with a genre label, same as post-2022 genre field
- Run extract_genre_hint() on description → genre_bucket() → high confidence
- Fall back to full description keyword match → lower confidence
- Result: 5,688 of 7,259 Unknowns resolved (78%)

### Publisher heuristics (Pass 2)
- Still 1,571 unresolved after description inference
- Examined publisher list in stuck entries — top publishers were almost all SFF specialists
- Tor (206), Baen (119), Ace (96), Orbit (84), DAW (73), Roc (64)...
- Built PUBLISHER_RULES table: ~100 publishers mapped to buckets
- Key limitation: most SFF publishers do both SF and Fantasy → "SF/Fantasy" combined bucket
- Exceptions: Baen → SF (Military SF skew), YA imprints (Tor Teen, Scholastic, etc.) → YA
- Result: 1,074 more resolved, total 93.2% of Unknowns resolved

## The 2021 dip investigation (a good science moment)
- Initial trend analysis showed a dip in 2021 SF/Fantasy counts
- First instinct: assume data quality issue, suggest limiting analysis to 2022+
- User pushed back — "that's not how a scientist thinks"
- Investigated properly:
  - Total book count genuinely dropped 2019→2020→2021 (668→568→451) — COVID publishing disruption real
  - 2021 Other bucket was anomalously large (109/451 = 24%)
  - Those "Other" entries had description sentences as genre labels — scraping artifact
  - But: description inference only rescued 14 of 109 (because description = same paragraph as genre)
  - Root cause: some 2021 entries had NO genre label at all, Locus just wrote a description sentence
  - "The Last Shadow" (Ender's Game finale) labeled as "Conclusion to both the original Ender series..."
  - These need world knowledge to classify → local LLM candidate list
- The 2022 jump (451→994) likely reflects Locus expanding coverage format, not real publishing surge

## The trend findings

Full year-by-year table (combined label + description + publisher inference):
year  SF   Fantasy  SF/Fantasy  Horror  YA
2011  43   72       51          17      22
2012  176  304      130         61      88
2013  188  304      134         59      108
2014  185  274      129         42      94
2015  206  268      140         32      79
2016  194  249      148         39      65
2017  218  239      84          31      82
2018  211  216      2           32      65
2019  221  247      1           33      61
2020  180  216      24          37      45
2021  97   107      0           44      78
2022  225  290      0           149     178
2023  106  135      6           77      96
2024  213  371      15          179     196
2025  192  411      6           214     185

SF as % of (SF + Fantasy + SF/Fantasy):
2011: 25.9%
2012: 28.9%
2013: 30.0%
2014: 31.5%
2015: 33.6%
2016: 32.8%
2017: 40.3%
2018: 49.2%
2019: 47.1%
2020: 42.9%
2021: 47.5%
2022: 43.7%
2023: 42.9%
2024: 35.6%
2025: 31.5%

Remaining unresolved (Other/Unknown) per year:
2011: 61, 2012: 206, 2013: 234, 2014: 192, 2015: 166, 2016: 162,
2017: 108, 2018: 83, 2019: 92, 2020: 64, 2021: 114, 2022: 133,
2023: 73, 2024: 123, 2025: 115

The real story: SF wasn't just declining — it staged a genuine recovery through the late 2010s,
nearly reaching parity with Fantasy by 2018-2019 (49.2%), before collapsing post-2022 to 31.5%.
Horror is exploding post-2022: 44 books (2021) → 149 (2022) → 214 (2025).
Cozy is a clear upward trend: 1 book (2022) → 2 (2023) → 7 (2024) → 20 (2025).
2021 dip in total books is real (COVID effect). 2022 surge likely Locus coverage expansion.
SF/Fantasy combined bucket concentrated in 2011-2016 (nav-only pages, no descriptions).
From 2017 onward SF/Fantasy nearly disappears — those years are most reliable.

## August 2011 editorial note
Locus explicitly reset their coverage in August 2011 — before that date they omitted YA,
horror, media tie-ins, and self-published books. Pre-2011 data exists but is not comparable.

## What's left
- 497 entries truly unresolvable (nav-only pages, no description, general trade publisher)
- Local LLM (ollama + llama3/mistral) for the "world knowledge" cases
- Notebook/visualisation for friend
- Trend analysis writeup
