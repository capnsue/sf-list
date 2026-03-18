# LLM-Assisted Genre Trend Analysis of Speculative Fiction Publishing, 2011–2026: Methods, Classification Pipeline, and Known Limitations

**Sue [last name]**
Draft, March 2026

---

## Abstract

This paper describes a web scraping and genre classification pipeline built to test the hypothesis that science fiction (SF) novel publishing has declined relative to fantasy, horror, and young-adult (YA) fiction over the past 15 years. Data were drawn from Locus Magazine's weekly new book release listings (August 2011–March 2026, ~565 pages, 12,564 books). All code was written collaboratively with Claude (Anthropic, claude-sonnet-4-6), a large language model, in an AI-assisted research workflow. The author has no prior domain expertise in SF/fantasy publishing; a domain expert (referred to here as the client) provided genre taxonomy guidance and served as a check on classification decisions. We describe the scraping methodology, multi-pass genre classification pipeline, known systematic biases, and unresolved gaps. Preliminary findings suggest SF's share of the speculative fiction market declined sharply after 2022 following an unexpected recovery period in the late 2010s, and that Horror has grown substantially in the same period.

---

## 1. Motivation and Research Question

The client, a longtime reader and observer of the SF/fantasy publishing industry, held the informal hypothesis that science fiction publishing had declined relative to fantasy, horror, and YA over the past decade or more — a decline he characterized as a subjective industry consensus. The goal of this project was to find a quantitative data source that could either support or complicate that hypothesis.

The research question: **Has the proportion of science fiction novels among new speculative fiction releases changed systematically between 2011 and 2026?**

---

## 2. Data Source

**Locus Magazine** (locusmag.com) publishes weekly lists of new speculative fiction releases. These pages include author, title, publisher, page count, publication date, a short genre label (inconsistently), and a description paragraph. The category index at `locusmag.com/category/newtitlesbestsellers/` lists all release pages back to August 2011.

**Why August 2011?** A note on the first Locus release page states that before August 2011, Locus explicitly omitted YA, horror, media tie-ins, and self-published books from their listings. Pre-2011 data is not comparable and was excluded.

**Coverage scope:** Locus covers a subset of all speculative fiction published — primarily trade-published novels and novellas from genre-specialist and major general publishers. Self-published, small press, and non-English-language titles are underrepresented. The dataset reflects *Locus's editorial coverage choices*, not the full publishing market.

Total pages scraped: 727 unique release pages (1,131 URLs were collected in total; 403 contained `#` anchors pointing to sections within a page and were deduplicated to their base URL, yielding 728 unique pages; 727 contained extractable book data). Books per page ranged from 2 to 53, with a median of 16 and mean of 17.3 (std 8.3) — pages vary considerably in length, likely reflecting both the length of the release week's list and changes in Locus's coverage scope over time. Total books: 12,564. Date range: August 2011 – March 2026 (partial year).

---

## 3. Scraping Pipeline

### 3.1 URL Discovery (`get_urls.py`)

A crawler traversed the Locus category index pages (paginated) and collected all URLs matching the release page naming pattern. Two URL conventions were encountered and handled:
- `new-book-releases-march-10-2026` (post-~2022 format)
- `new-books-7-june-2022` (pre-~2022 format)

Anchored URLs (`#section`) were deduplicated to base URLs. Result: 565 unique URLs saved to `urls.txt`.

### 3.2 Page Scraping (`scraper.py`)

Each URL was fetched with a 1-second delay between requests (rate limiting). Fields extracted per book entry: `author`, `title`, `publisher`, `page_count` (integer), `publication_date` (normalized to YYYY-MM-DD), `genre` (raw Locus label), `description` (full description paragraph), `source_url`, `date_scraped`.

**Three page format eras required distinct parsing strategies:**

| Era | Approx. dates | Structure | Genre field |
|-----|--------------|-----------|-------------|
| Era 1 | 2011–~2021 | Title → Details → Description | Absent or inconsistent |
| Era 2 | ~2022–2023 | Title → Details → Description | Present in description block |
| Era 3 | 2024–present | Title → Description → Details | Present at start of description |

The Era 3 format change — where the description block moved *before* the details block — caused silent parsing failures in early versions of the scraper, resulting in missed genre fields for 2024+ entries. This was identified and corrected before the final scrape.

**A note on sleep timing:** An initial attempt to reduce the inter-request delay from 1.0s to 0.5s was made during development. This did not meaningfully reduce total scrape time (network latency dominates over sleep time at this scale) and was retained at 0.5s in the final scraper. Future scrapes should probably restore the 1.0s default as a courtesy.

### 3.3 Re-scrape

A re-scrape was performed after adding the `description` field and correcting the Era 3 parsing bug. Final dataset: `books_20260313_211555.csv`, 12,564 books, 12,238 with non-empty description (97.4%).

---

## 4. Genre Classification Pipeline

### 4.1 Overview

Genre classification proceeded in three passes, each adding information for entries not resolved by the previous pass:

1. **Pass 0 (Locus label):** Use the raw genre string from Locus directly.
2. **Pass 1 (Description inference):** For unlabeled entries, infer from the description paragraph.
3. **Pass 2 (Publisher heuristics):** For entries with no usable description, infer from publisher name.

Two output columns track results:
- `genre_bucket` — the bucket assigned from the Locus label (Pass 0 only; never overwritten)
- `genre_inferred` — the bucket inferred from description or publisher (Passes 1–2)
- `genre_source` — `"label"`, `"description"`, or `"unknown"`

For analysis, the effective genre is: `genre_bucket` where not Unknown, else `genre_inferred`.

### 4.2 Genre Buckets

Genre strings were mapped to broad buckets using keyword matching (`re.search`), applied in priority order:

| Priority | Bucket | Keywords |
|----------|--------|---------|
| 1 | YA | young-adult, young adult, middle-grade, standalone "ya" |
| 2 | SF | sf, science fiction, space opera, cyberpunk, solarpunk, biopunk, sci-fi, alternate history, apocalyptic, dystopian, near-future, post-apocalyptic |
| 3 | Horror | horror, ghost, gothic, haunted, paranormal, supernatural |
| 4 | Fantasy | fantasy, romantasy, vampire, zombie, steampunk, fable, folkloric, magic realism, magical elements, weird western |
| 5 | Non-fiction | non-fiction, art book, graphic novel, reference |
| 6 | Other | labeled but no keyword matched |
| 7 | Unknown | no label at all |

**Priority order rationale:** YA takes precedence because "young-adult fantasy novel" should be classified as YA rather than Fantasy for the client's analysis (YA is a market category that cuts across genres). SF is prioritized over Horror and Fantasy because there is less keyword ambiguity in SF labels. Romance was removed as a standalone bucket at the client's request — romantasy and similar entries fall to Fantasy.

**Known misclassification:** "Alternate history fantasy novel" entries are classified as SF because "alternate history" fires before Fantasy in the keyword priority list. Alternate history fantasy is arguably a Fantasy subgenre, not SF. The number of affected entries is estimated to be small but has not been precisely quantified.

**Additional flags:**
- `is_cozy` (boolean): True if genre string contains "cozy"
- `media_tie_in`: "Media Tie-In" if genre string contains "tie-in", else empty

### 4.3 Pass 1: Description-Based Inference

**Motivation:** Pre-2022 Locus pages often lacked a structured genre field but included a description paragraph that frequently began with a genre label (e.g., "Fantasy novel, first in a series..."). This pattern was identified empirically by examining samples of unlabeled entries across years.

**Method:** Two sub-passes:
1. Extract the text before the first period or comma from the description ("genre hint"). Run through `genre_bucket()`. If not Unknown, accept as high-confidence inference.
2. If still Unknown, run `genre_bucket()` on the full description text. Lower confidence — catches keyword mentions in blurb prose.

Navigation-only descriptions ("Purchase this book from Amazon | Indiebound") were detected by pattern matching and skipped.

**Results:** 5,688 of 7,259 Unknowns resolved (78.4%) from description text.

**Validation:** Spot-checks of classified entries looked accurate. No formal precision/recall measurement was performed — this is a known gap (see Section 6).

### 4.4 Pass 2: Publisher Heuristics

**Motivation:** 1,571 entries remained unresolved after description inference, primarily 2011–2013 books where the description field contained only navigation links. Publisher name was the only remaining signal.

**Method:** A lookup table of ~100 publishers was built mapping publisher name to genre bucket. Publishers were assigned by examining the unresolved entry list and applying domain knowledge (supplemented by client review of edge cases). Most SFF specialist publishers (Tor, Orbit, DAW, Roc, Ace) were mapped to an "SF/Fantasy" combined bucket, because these publishers release both SF and Fantasy and the data does not allow disambiguation at the publisher level alone.

Exceptions where stronger signal was available:
- **Baen** → SF (client confirmed strong military SF skew)
- YA imprints (Tor Teen, Scholastic, Margaret K. McElderry, etc.) → YA

**Results:** 1,074 additional entries resolved. Total unresolved after both passes: 497 (4.0% of full dataset).

**Limitation:** Publisher genre skews may have shifted over time. Tor in 2012 may have had a different SF/Fantasy balance than Tor in 2025. The lookup table applies a static mapping.

---

## 5. Findings

### 5.1 Year-by-Year Genre Counts

The table below combines labeled, description-inferred, and publisher-inferred genres. "SF/Fantasy" is a combined bucket from publisher heuristics where SF/Fantasy could not be disambiguated.

| Year | SF | Fantasy | SF/Fantasy | Horror | YA |
|------|-----|---------|------------|--------|-----|
| 2011 | 43 | 72 | 51 | 17 | 22 |
| 2012 | 176 | 304 | 130 | 61 | 88 |
| 2013 | 188 | 304 | 134 | 59 | 108 |
| 2014 | 185 | 274 | 129 | 42 | 94 |
| 2015 | 206 | 268 | 140 | 32 | 79 |
| 2016 | 194 | 249 | 148 | 39 | 65 |
| 2017 | 218 | 239 | 84 | 31 | 82 |
| 2018 | 211 | 216 | 2 | 32 | 65 |
| 2019 | 221 | 247 | 1 | 33 | 61 |
| 2020 | 180 | 216 | 24 | 37 | 45 |
| 2021 | 97 | 107 | 0 | 44 | 78 |
| 2022 | 225 | 290 | 0 | 149 | 178 |
| 2023 | 106 | 135 | 6 | 77 | 96 |
| 2024 | 213 | 371 | 15 | 179 | 196 |
| 2025 | 192 | 411 | 6 | 214 | 185 |

*(2011 covers August–December only. 2026 partial data excluded from this table.)*

### 5.2 SF as Proportion of SF + Fantasy

Excluding the SF/Fantasy combined bucket (which cannot be split), SF's share of the SF + Fantasy pool:

2011: 37.4% → 2012: 36.7% → 2013: 38.2% → 2014: 40.3% → 2015: 43.4% → 2016: 43.8% → 2017: 47.7% → **2018: 49.4%** → 2019: 47.2% → 2020: 45.5% → 2021: 47.6% → 2022: 43.7% → 2023: 44.1% → 2024: 36.5% → **2025: 31.8%**

SF's share rose through the 2010s, nearly reaching parity with Fantasy in 2018, then declined substantially after 2022.

### 5.3 Horror Growth

Horror counts: 17 (2011) → 61 (2012) → 44 (2021) → 149 (2022) → 179 (2024) → 214 (2025). The 2022+ growth is striking and does not appear to be a classification artifact — Locus genre labels became more consistent in this period.

### 5.4 Cozy as an Emerging Category

Cozy-flagged entries (books with "cozy" in the genre label): 1 (2022) → 2 (2023) → 7 (2024) → 20 (2025). Small absolute numbers, but a clear directional trend.

---

## 6. Known Limitations and Gaps

### 6.1 No Ground Truth Validation

The classification pipeline has not been evaluated against a labeled ground truth. Precision and recall for the description-inference and publisher-heuristic passes are unknown. Spot-checks were performed and results looked reasonable, but this is not a substitute for systematic validation. A sample of ~200 entries randomly drawn across years, manually labeled, and compared to pipeline output would establish a baseline accuracy estimate.

### 6.2 The SF/Fantasy Combined Bucket

Publisher heuristics could not distinguish SF from Fantasy for entries from generalist SFF publishers. These entries (concentrated in 2011–2016, where description text was unavailable) are excluded from the SF% calculation in Section 5.2. If the true SF/Fantasy split for these entries differs systematically from the labeled years, the trend line for early years is biased.

### 6.3 The 2022 Coverage Expansion

Total book counts per year: 2021: 451 → 2022: 994. This near-doubling almost certainly reflects a change in Locus's coverage scope rather than an actual doubling of new releases. Genre proportions in 2022 may not be directly comparable to 2021. The nature and timing of this editorial change has not been confirmed with Locus.

### 6.4 The 2021 Anomaly

2021 had an unusually large "Other" bucket (109 of 451 entries, 24%). Investigation revealed that some 2021 entries had no genre label and descriptions that were plot blurbs rather than genre sentences — making both description inference and publisher heuristics unreliable for these entries. Some require world knowledge to classify (e.g., a book described only as "the conclusion to the original Ender series" requires knowing that Ender's Game is SF). These 109 entries remain unclassified and inflate the "Other/Unknown" count for 2021. The COVID-era publishing disruption is also reflected in lower total counts for 2020–2021.

### 6.5 Alternate History Fantasy Misclassification

The keyword "alternate history" maps to the SF bucket (by client convention) before "fantasy" is tested. "Alternate history fantasy" as a subgenre (e.g., secondary-world alternate history with fantasy elements) would be misclassified as SF. The prevalence of this edge case has not been measured.

### 6.6 Locus Coverage Bias

Locus covers a curated subset of speculative fiction. Their selection criteria, editorial focus, and relationships with publishers have likely evolved over 15 years. Changes in what Locus *chooses to cover* are indistinguishable from changes in what publishers *produce* in this dataset.

### 6.7 LLM-Assisted Methodology Transparency

All code was written by Claude (Anthropic, claude-sonnet-4-6) in response to prompts from the author. Methodological decisions — bucket definitions, priority ordering, inference strategy, publisher mappings — were made collaboratively: Claude proposed approaches, the author approved, redirected, or pushed back, and the client provided domain-expert review of taxonomy decisions. This division of labor is not standard in academic research and its implications for reproducibility and bias are not fully understood. The prompts used to elicit code are not currently logged in a reproducible form.

---

## 7. Remaining Work

- **Ground truth validation:** Hand-label a stratified random sample; measure pipeline precision/recall.
- **LLM classification for world-knowledge cases:** ~497 entries remain unresolved. A local LLM (e.g., ollama + llama3) queried with title, author, and publisher could resolve many of these.
- **Visualization:** Year-over-year trend charts for the client.
- **Locus coverage change investigation:** Attempt to confirm the nature and timing of the 2022 expansion.
- **Prompt logging:** Capture the full prompt/response history for methodological transparency.

---

## Appendix: Publisher Bucket Mappings (selected)

| Publisher | Assigned bucket | Rationale |
|-----------|----------------|-----------|
| Tor | SF/Fantasy | Major SFF publisher, both genres |
| Baen | SF | Client: strong military SF skew |
| Orbit | SF/Fantasy | Major SFF publisher, both genres |
| DAW | SF/Fantasy | Major SFF publisher, both genres |
| Ace | SF/Fantasy | Penguin imprint, both genres |
| Roc | SF/Fantasy | Penguin imprint, both genres |
| Tor Teen | YA | YA imprint of Tor |
| Scholastic | YA | YA/children's publisher |
| Margaret K. McElderry | YA | YA imprint (Simon & Schuster) |
| Cemetery Dance | Horror | Horror specialist |
| Flame Tree Press | Horror | Horror specialist |

*(Full table of ~100 publishers available in `normalize.py`.)*
