# Open Questions

## Pending edits (both docs)

- **"Speculative fiction" terminology:** once confirmed with client, find-and-replace across both `writeup.md` and `methods-paper.md`

## Pending edits (writeup.md only)

- **"The friend pushed back"** → already fixed to Sue; double-check pronoun consistency throughout
- **GitHub repo URL** at the bottom is a placeholder — fill in real URL

## Pending edits (both docs)

- **Genre field description (multiple places):** The `genre` field is not a "raw Locus label" — it's extracted by our `extract_genre()` heuristic (truncate candidate text at first period or comma), which Sue devised by eyeballing a few pages. Should be described honestly as a naive heuristic we knew we'd iterate on, not as a structured data field Locus provides. Works reasonably for Era 2/3 pages; produces empty results for most Era 1 pages. This also affects the Pass 0 description in Section 4.1 — "Use the raw genre string from Locus directly" is wrong; Pass 0 is also our heuristic extraction, not something Locus labeled.

## Pending edits (methods-paper.md only — add to limitations section)

- **Cozy detection limited to labeled entries:** `is_cozy` only checks the Locus genre label field, so pre-2022 cozy books are invisible in our data. The cozy trend line may reflect the emergence of "cozy" as an explicit publishing label as much as the emergence of the genre itself. Both could be true simultaneously.

## Pending edits (methods-paper.md only)

- **"final scrape"** (Section 3.2) — don't imply the scrape is final; change to "before the scrape used for this analysis" or similar
- **Sleep timing / bottleneck claim** (Section 3.2) — remove the assertion that "network latency dominates." We halved sleep from 1s to 0.5s in the same run where we added description capture (more data per page). We observed no meaningful speedup but cannot attribute that to network latency specifically — the confound makes it impossible to say what the bottleneck was.
- **"final scraper" and "Final dataset"** (Sections 3.2 and 3.3) — two more instances of "final"; replace with neutral language
- **"Future scrapes should probably restore the 1.0s default as a courtesy"** (Section 3.2) — reads as admitting a mistake in a methods paper; either cut it or reframe neutrally
- **Author name** — "Sue [last name]" placeholder needs real name (or decide to omit)

## Code fixes needed (normalize.py)

- **vampire, zombie → Horror not Fantasy** (client feedback): these keywords are currently in the Fantasy bucket rules. Move them to Horror. Will require re-running normalization.

## Stuff to fix later (methods paper)

- **BookScan:** The industry-standard source for publishing trend data (BookScan) requires a paid membership costing thousands of dollars. Mention this explicitly — our Locus-based approach is a free, reproducible alternative. Also note that BookScan measures *sales* while we measure *new releases*, which are related but different questions.

## Future research ideas

- **Cozy detection in descriptions (client request):** Now that we have description text captured, run a keyword search for "cozy" on pre-2022 entries to see if any cozy books are hiding there unlabeled. Small effort, potentially interesting data point.

- **LLM disambiguation of SF/Fantasy combined bucket:** The ~1,500 entries assigned to the "SF/Fantasy" combined bucket (mostly 2011–2016, from generalist SFF publishers with no description text) could potentially be split by querying a local LLM with title, author, and publisher. Same approach as the planned world-knowledge pass for the 497 unresolvables — could be done in the same pass.

- **Media tie-in detection via character/franchise names:** Current `media_tie_in` flag only catches entries where Locus explicitly wrote "tie-in" in the genre label. Many tie-in books (especially pre-2022) are probably unlabeled. A lookup of unambiguous proper nouns in the description field — character names (Luke Skywalker, Captain Picard), franchise names (Star Wars, Star Trek, Warhammer) — would catch these without false positives. High precision, unknown recall.



- **Genre label adjective ordering:** In English, adjectives follow a conventional order (the "royal order of adjectives" — "little old lady" not "old little lady"). Do Locus genre labels follow a similar convention, e.g., is it always "young adult horror novel" and never "horror young adult novel"? If genre descriptors have a consistent ordering in publishing convention, that ordering could empirically inform the bucket priority order rather than us deriving it arbitrarily. Could be investigated by frequency-counting multi-word genre labels in the dataset.

## For us (methodology)

- **Priority order rationale (Section 4.2):** Where did the SF > Horror > Fantasy ordering actually come from? The methods paper gives a tidy justification but it may have been somewhat arbitrary. Can we actually defend it, or should we describe it more honestly as an initial ordering that we didn't rigorously derive?

## For the client (domain expert)

- **"Speculative fiction" terminology:** Is this how Locus describes their own coverage scope, or do they use "science fiction & fantasy" or something else? The term appears in the research question and should match how Locus frames it. Once answered, do a find-and-replace across both writeup docs — the term appears multiple times.

- **Publisher bucket assignments (Section 4.4 / Appendix):** Please review the publisher-to-bucket mappings for accuracy — particularly the SF/Fantasy combined assignments and any publishers where the genre skew may have shifted over time.

- **Locus coverage scope — is this accurate?** From the methods paper: *"Locus covers a subset of all speculative fiction published — primarily trade-published novels and novellas from genre-specialist and major general publishers. Self-published, small press, and non-English-language titles are underrepresented. The dataset reflects Locus's editorial coverage choices, not the full publishing market."* Sue does not have enough domain knowledge to verify this — please confirm or correct.
