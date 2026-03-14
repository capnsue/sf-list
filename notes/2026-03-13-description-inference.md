# 2026-03-13: Description-Based Genre Inference

## What We Did

Added description-based genre inference to `normalize.py` to recover genre
classifications for the ~7,259 pre-2022 Unknown entries.

### How it works
For every row where `genre_bucket == "Unknown"`, we try two steps:

1. **Genre hint extraction** — pull the text before the first period or comma
   from the description. Pre-2022 descriptions often start with a genre label
   (e.g. "Fantasy novel, first in a series..."). Run that hint through
   `genre_bucket()`. High confidence.
2. **Full description keyword match** — fall back to running `genre_bucket()`
   on the full description text. Lower confidence but catches more.

Navigation-only descriptions ("Purchase this book from Amazon | Indiebound")
are skipped and left as Unknown.

### New columns
- **`genre_inferred`** — the inferred bucket for Unknown rows (empty for labeled rows)
- **`genre_source`** — `"label"` (from Locus genre field), `"description"` (inferred),
  or `"unknown"` (couldn't resolve)

`genre_bucket` is never overwritten — it always reflects the Locus label.
For analysis, combine: use `genre_bucket` where it's not Unknown, use
`genre_inferred` to fill the gaps.

## Results

**5,688 of 7,259 Unknowns resolved (78%) from description text alone.**

| Inferred bucket | Count |
|----------------|-------|
| Fantasy | 2,287 |
| SF | 1,659 |
| Unknown (unresolved) | 1,571 |
| Other | 671 |
| YA | 618 |
| Horror | 336 |
| Non-fiction | 117 |

Spot-checks looked accurate. One known edge case: "Alternate history fantasy
novel" descriptions get bucketed as SF (alternate history → SF fires before
fantasy). Small number, acceptable for now.

The 1,571 remaining Unknowns are mostly 2011–2013 entries where the description
was just navigation links ("Purchase this book from Amazon"). No description
text available — would need external lookup or LLM to resolve.

## Next Steps
1. **Trend analysis** — this is the actual end goal. Now that we have good genre
   coverage across all years, build year-over-year charts combining `genre_bucket`
   (labeled) and `genre_inferred` (inferred). Focus question: has SF declined
   relative to Fantasy over 2011–2026?
2. **"The Dark Archive" edge case** — "alternate history fantasy" entries getting
   bucketed as SF. Low priority, small number.
3. **Remaining 1,571 Unknowns** — publisher heuristics or local LLM (ollama +
   llama3/mistral) as last resort. Put on hold until trend analysis is done.
4. **Commit** — scraper.py (description field, 0.5s sleep), normalize.py
   (inference, new columns), this notes file.
