# Is Science Fiction Dying? We Scraped 15 Years of Locus Magazine to Find Out

A friend of mine has a theory: science fiction publishing has been declining for years, slowly losing ground to fantasy, horror, and YA. He's been watching the genre for decades, and the vibe feels real to him. But vibes aren't data. So we decided to find out.

## The Data Source

[Locus Magazine](https://locusmag.com) is the trade publication of record for science fiction and fantasy. Since August 2011, they've published a weekly list of new book releases — author, title, publisher, page count, publication date, and (usually) a genre label and short description. Nearly 15 years of weekly snapshots. Around 565 pages. We scraped all of it.

The resulting dataset: **12,564 books**, spanning August 2011 through early March 2026.

## What We Built

Three Python scripts, run in sequence:

**`get_urls.py`** crawls the Locus category index and collects all release page URLs, saving them to `urls.txt`. Locus has used two URL naming conventions over the years (`new-book-releases-march-10-2026` vs. `new-books-7-june-2022`), so the crawler handles both.

**`scraper.py`** fetches each page, extracts the book data, and outputs a timestamped CSV. This was harder than it sounds. Locus changed their page format at least three times:

| Era | Page structure | Genre labeling |
|-----|---------------|----------------|
| 2011–~2021 | Title → Details → Description | Rarely labeled |
| ~2022–2023 | Title → Details → Description | Genre in description field |
| 2024–now | Title → Description → Details | Genre at start of description |

Each era required a different parsing strategy. The 2024 format flip — where description moved *before* the details block — was a genuine debugging puzzle.

**`normalize.py`** takes the raw CSV and adds genre bucketing: SF, Fantasy, Horror, YA, and a few others. It also adds `is_cozy` (boolean), `media_tie_in` (flag), and year. Bucketing is keyword-based — "fantasy novel", "epic fantasy", "urban fantasy" all become Fantasy — and applied in priority order so a "young-adult fantasy novel" lands in YA, not Fantasy.

## The Big Complication: 57% Missing Genres

Here's the problem: Locus didn't consistently label genres before about 2022. Of 12,564 books, **7,259 had no genre field at all** — a 57% gap that would make any trend analysis over the full 2011–2026 period nearly meaningless.

We attacked this in layers.

**Layer 1: Description text.** We re-scraped everything to capture the full description paragraph. It turns out pre-2022 descriptions frequently *start* with a genre label — "Fantasy novel, first in a series..." — even when the structured genre field was empty. By extracting the text before the first period or comma and running it through the same bucketing logic, we resolved **5,688 of 7,259 Unknowns (78%)** from description text alone.

**Layer 2: Publisher heuristics.** The remaining 1,571 unresolved entries were mostly 2011–2013 books where the "description" was just navigation links ("Purchase this book from Amazon | Indiebound") — no text to mine. But publisher names are still there. We examined the top publishers among stuck entries: Tor (206 entries), Baen (119), Ace (96), Orbit (84), DAW (73), Roc (64). These are SFF specialists. We built a lookup table of ~100 publishers mapped to genre buckets. Most SFF publishers do both SF and Fantasy, so they get an "SF/Fantasy" combined bucket — but Baen skews heavily military SF, and YA imprints like Tor Teen and Scholastic get their own bucket.

Publisher heuristics resolved **1,074 more entries**, bringing us to **93.2% of Unknowns resolved** — leaving only 497 truly unresolvable (nav-only pages, no description, general trade publishers with no genre signal).

The dataset now has a `genre_source` column: `"label"` (from Locus directly), `"description"` (inferred), or `"unknown"`.

## A Good Science Moment

Early in the analysis, we noticed a dip in 2021 book counts and I instinctively suggested limiting the analysis to 2022 onward to avoid noise. My collaborator pushed back: that's not how a scientist thinks. You don't just discard the messy years.

She was right. We investigated properly.

The dip is real: total books dropped from 668 (2019) → 568 (2020) → 451 (2021). COVID disrupted publishing pipelines; that drop is documented industry-wide.

But 2021 also had an anomalously large "Other" bucket — 109 of 451 entries (24%) that couldn't be classified. When we dug in, we found why: some 2021 entries had no genre label at all, and the "description" was just the book's blurb rather than a genre sentence. "The Last Shadow" — the Ender's Game finale — was labeled with the first sentence of its plot description. No amount of keyword matching would catch that. These are the cases that genuinely require world knowledge to classify, and they're candidates for a local LLM pass later.

The 2022 surge (451 → 994 books) almost certainly reflects Locus expanding their coverage format, not a real publishing surge.

## What We Found

After combining labeled, description-inferred, and publisher-inferred genre data, here's the year-by-year picture:

| Year | SF | Fantasy | Horror | YA | SF as % of SF+Fantasy |
|------|-----|---------|--------|----|-----------------------|
| 2011 | 43 | 72 | 17 | 22 | 26% |
| 2012 | 176 | 304 | 61 | 88 | 29% |
| 2013 | 188 | 304 | 59 | 108 | 30% |
| 2014 | 185 | 274 | 42 | 94 | 32% |
| 2015 | 206 | 268 | 32 | 79 | 34% |
| 2016 | 194 | 249 | 39 | 65 | 33% |
| 2017 | 218 | 239 | 31 | 82 | 40% |
| 2018 | 211 | 216 | 32 | 65 | **49%** |
| 2019 | 221 | 247 | 33 | 61 | 47% |
| 2020 | 180 | 216 | 37 | 45 | 43% |
| 2021 | 97 | 107 | 44 | 78 | 48% |
| 2022 | 225 | 290 | 149 | 178 | 44% |
| 2023 | 106 | 135 | 77 | 96 | 43% |
| 2024 | 213 | 371 | 179 | 196 | 36% |
| 2025 | 192 | 411 | 214 | 185 | **32%** |

*(Note: 2011–2016 include "SF/Fantasy" combined entries for pre-description nav-only pages. 2017+ are the most reliable years — descriptions available, publisher heuristics minimal.)*

The story here is more interesting than a simple decline narrative.

**SF wasn't just shrinking — it staged a genuine recovery.** Through the mid-2010s, Fantasy held a consistent 2:1 lead over SF. Then SF climbed steadily, nearly reaching parity by 2018-2019 (49% of SF+Fantasy). That's a meaningful recovery that the vibe-based narrative misses entirely.

**The collapse is post-2022.** SF's share dropped from ~47% in 2019 to 32% in 2025. The fall is real. But it's recent — and Fantasy's growth isn't the only driver.

**Horror is exploding.** 44 books in 2021 → 149 in 2022 → 214 in 2025. That's a nearly 5× increase in four years. Horror is eating into the overall speculative fiction market in a way that isn't visible if you only look at SF vs. Fantasy.

**Cozy is a rising microtrend.** 1 cozy book in 2022 → 2 in 2023 → 7 in 2024 → 20 in 2025. Small numbers, but unmistakably directional.

## What's Left

About 497 entries remain truly unresolvable with the current approach — nav-only pages with no description text and general trade publishers. These are candidates for a local LLM pass (ollama + llama3 or similar) using title and author to infer genre from world knowledge.

The next deliverable for the friend is a proper visualization — year-over-year trend charts, probably in a Jupyter notebook or Excel-friendly CSV. The data is in good shape. The story is more nuanced than the original hypothesis, which is exactly what good data analysis is supposed to produce.

---

*Data: Locus Magazine new book release pages, August 2011 – March 2026. ~565 pages, 12,564 books. Code: Python, BeautifulSoup, pandas. Repo: [sf-list](https://github.com/suz/sf-list).*
