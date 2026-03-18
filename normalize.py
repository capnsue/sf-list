#!/usr/bin/env python3
"""Genre normalization for Locus Magazine book data.

Adds columns to the most recent books CSV:
  genre_bucket  — broad category for trend analysis
  genre_label   — genre string with format suffix stripped (no "novel", "novella", etc.)
  is_cozy       — True if genre contains "cozy"
  media_tie_in  — "Media Tie-In" if genre contains "tie-in", else empty

Bucket priority (first match wins):
  YA          — young-adult, young adult, middle-grade, standalone "ya"
  SF          — sf, science fiction, space opera, cyberpunk, solarpunk, biopunk,
                sci-fi, alternate history, apocalyptic, dystopian, near-future,
                post-apocalyptic
  Horror      — horror, ghost, gothic, haunted, paranormal, supernatural
  Fantasy     — fantasy, romantasy, vampire, zombie, steampunk, fable, folkloric,
                magic realism, magical elements, weird western
  Non-fiction — non-fiction, nonfiction, art book, graphic novel, reference
  Other       — has a genre label but no keyword matched
  Unknown     — no genre label at all

Output: books_YYYYMMDD_HHMMSS_normalized.csv
"""

import pandas as pd
import glob
import re


BUCKET_RULES = [
    ("YA", [
        r"young[- ]adult",
        r"middle[- ]grade",
        r"\bya\b",
    ]),
    ("SF", [
        r"\bsf\b",
        r"science fiction",
        r"space opera",
        r"\bcyberpunk\b",
        r"\bsolarpunk\b",
        r"\bbiopunk\b",
        r"\bsci-?fi\b",
        r"alternate\s+history",
        r"\bapocalyptic\b",
        r"\bdystopian\b",
        r"near[- ]future",
        r"post[- ]apocalyptic",
    ]),
    ("Horror", [
        r"horror",
        r"\bghost\b",
        r"\bgothic\b",
        r"\bhaunted\b",
        r"\bparanormal\b",
        r"\bsupernatural\b",
    ]),
    ("Fantasy", [
        r"fantasy",
        r"\bromantasy\b",
        r"\bvampire\b",
        r"\bzombie\b",
        r"\bsteampunk\b",
        r"\bfable\b",
        r"\bfolkloric\b",
        r"magic(?:al)?\s+realism",
        r"magical\s+elements",
        r"weird\s+western",
    ]),
    ("Non-fiction", [
        r"non-?fiction",
        r"\bart book\b",
        r"\bgraphic novel\b",
        r"\breference\b",
    ]),
]

# Format words to strip when building genre_label
FORMAT_PATTERN = re.compile(
    r"\b(novel|novella|collection|anthology|short\s+fiction)\b",
    flags=re.IGNORECASE,
)


def genre_bucket(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return "Unknown"
    text = raw.lower()
    for bucket, patterns in BUCKET_RULES:
        for pat in patterns:
            if re.search(pat, text):
                return bucket
    return "Other"


def genre_label(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return ""
    cleaned = FORMAT_PATTERN.sub("", raw).strip().strip(",").strip()
    return re.sub(r"\s{2,}", " ", cleaned)


def extract_genre_hint(text: str) -> str:
    """Extract the genre label from the start of a description (before first period or comma)."""
    if not isinstance(text, str) or not text.strip():
        return ""
    period_idx = text.find(".")
    comma_idx = text.find(",")
    indices = [i for i in [period_idx, comma_idx] if i > 0]
    return text[:min(indices)].strip() if indices else ""


# Descriptions that contain only navigation links — no useful content
_NAV_MARKERS = ("Purchase this book", "Directory Entry")


def infer_bucket_from_description(description: str) -> str:
    """Infer genre bucket from description text for Unknown entries.

    Step 1: Extract the genre hint from the start of the description (pre-2022
            entries often begin with a genre label, e.g. 'Fantasy novel, first in...')
            and run it through genre_bucket(). High confidence.
    Step 2: Fall back to running genre_bucket() on the full description text.
            Lower confidence but catches keyword-rich descriptions.
    Returns 'Unknown' if nothing useful is found.
    """
    if not isinstance(description, str) or not description.strip():
        return "Unknown"
    if any(marker in description for marker in _NAV_MARKERS):
        return "Unknown"

    # Step 1: genre hint from start of description
    hint = extract_genre_hint(description)
    if hint:
        bucket = genre_bucket(hint)
        if bucket not in ("Unknown", "Other"):
            return bucket

    # Step 2: full description keyword match
    return genre_bucket(description)


# Publisher heuristics — substring matched against lowercased publisher field.
# More specific entries must come before broader ones (e.g. "tor teen" before "tor").
# SF/Fantasy = specialist SFF house but can't distinguish SF from Fantasy.
PUBLISHER_RULES = [
    # YA imprints — high confidence
    ("tor teen",                    "YA"),
    ("tor/starscape",               "YA"),
    ("strange chemistry",           "YA"),
    ("harperteen",                  "YA"),
    ("harpercollins/tegen",         "YA"),
    ("harpercollins/greenwillow",   "YA"),
    ("harpercollins/balzer",        "YA"),
    ("harpercollins/heartdrum",     "YA"),
    ("scholastic",                  "YA"),
    ("delacorte",                   "YA"),
    ("disney/hyperion",             "YA"),
    ("katherine tegen",             "YA"),
    ("razorbill",                   "YA"),
    ("abrams/amulet",               "YA"),
    ("abrams amulet",               "YA"),
    ("feiwel",                      "YA"),
    ("sourcebooks fire",            "YA"),
    ("mcelderry",                   "YA"),
    ("nancy paulsen",               "YA"),
    ("orion children",              "YA"),
    ("greenwillow",                 "YA"),
    ("arthur a. levine",            "YA"),
    ("farshore",                    "YA"),
    ("electric monkey",             "YA"),
    # Horror specialty presses
    ("cemetery dance",              "Horror"),
    ("raw dog screaming",           "Horror"),
    ("dark regions",                "Horror"),
    ("word horde",                  "Horror"),
    ("comet press",                 "Horror"),
    ("necro publications",          "Horror"),
    ("hippocampus",                 "Horror"),
    ("burning effigy",              "Horror"),
    ("nightscape",                  "Horror"),
    ("dark renaissance",            "Horror"),
    ("dark renaissace",             "Horror"),
    ("journalstone",                "Horror"),
    ("journal-stone",               "Horror"),
    ("fedogan",                     "Horror"),
    ("haverhill house",             "Horror"),
    ("chizine",                     "Horror"),
    # Non-fiction / academic
    ("wesleyan university",         "Non-fiction"),
    ("oxford university",           "Non-fiction"),
    ("columbia university",         "Non-fiction"),
    ("university of illinois",      "Non-fiction"),
    ("university of arizona",       "Non-fiction"),
    ("university of minnesota",     "Non-fiction"),
    ("mit press",                   "Non-fiction"),
    ("the mit press",               "Non-fiction"),
    ("palgrave",                    "Non-fiction"),
    ("mcfarland",                   "Non-fiction"),
    ("wiley blackwell",             "Non-fiction"),
    ("flesk",                       "Non-fiction"),
    ("ballistic publishing",        "Non-fiction"),
    ("smart pop",                   "Non-fiction"),
    # SF — publishers that skew heavily SF
    ("baen",                        "SF"),
    # SF/Fantasy specialist presses
    ("tor.com",                     "SF/Fantasy"),
    ("tordotcom",                   "SF/Fantasy"),
    ("nightfire",                   "SF/Fantasy"),
    ("tor/forge",                   "SF/Fantasy"),
    ("tor/nightfire",               "SF/Fantasy"),
    ("tor",                         "SF/Fantasy"),
    ("orbit",                       "SF/Fantasy"),
    ("redhook",                     "SF/Fantasy"),
    ("daw",                         "SF/Fantasy"),
    ("prime books",                 "SF/Fantasy"),
    ("subterranean",                "SF/Fantasy"),
    ("solaris",                     "SF/Fantasy"),
    ("angry robot",                 "SF/Fantasy"),
    ("pyr",                         "SF/Fantasy"),
    ("harper voyager",              "SF/Fantasy"),
    ("del rey",                     "SF/Fantasy"),
    ("ballantine spectra",          "SF/Fantasy"),
    ("ballantine del rey",          "SF/Fantasy"),
    ("tachyon",                     "SF/Fantasy"),
    ("night shade",                 "SF/Fantasy"),
    ("lethe press",                 "SF/Fantasy"),
    ("lethe",                       "SF/Fantasy"),
    ("saga press",                  "SF/Fantasy"),
    ("/saga",                       "SF/Fantasy"),
    ("s&s/saga",                    "SF/Fantasy"),
    ("small beer press",            "SF/Fantasy"),
    ("fairwood",                    "SF/Fantasy"),
    ("aqueduct",                    "SF/Fantasy"),
    ("gollancz",                    "SF/Fantasy"),
    ("jo fletcher",                 "SF/Fantasy"),
    ("titan",                       "SF/Fantasy"),
    ("arc manor",                   "SF/Fantasy"),
    ("caezik sf",                   "SF/Fantasy"),
    ("edge science fiction",        "SF/Fantasy"),
    ("hades/edge",                  "SF/Fantasy"),
    ("hades/edge science",          "SF/Fantasy"),
    ("fantastic books",             "SF/Fantasy"),
    ("talos",                       "SF/Fantasy"),
    ("haikasoru",                   "SF/Fantasy"),
    ("galaxy press",                "SF/Fantasy"),
    ("world weaver",                "SF/Fantasy"),
    ("apex",                        "SF/Fantasy"),
    ("broken eye",                  "SF/Fantasy"),
    ("hydra house",                 "SF/Fantasy"),
    ("espec",                       "SF/Fantasy"),
    ("newcon press",                "SF/Fantasy"),
    ("mythic delirium",             "SF/Fantasy"),
    ("cheeky frawg",                "SF/Fantasy"),
    ("rosarium",                    "SF/Fantasy"),
    ("resurrection house",          "SF/Fantasy"),
    ("crossed genres",              "SF/Fantasy"),
    ("wire rim",                    "SF/Fantasy"),
    ("undertow",                    "SF/Fantasy"),
    ("parvus",                      "SF/Fantasy"),
    ("third flatiron",              "SF/Fantasy"),
    ("ifwg",                        "SF/Fantasy"),
    ("spectra",                     "SF/Fantasy"),
    ("isfic",                       "SF/Fantasy"),
    ("ace",                         "SF/Fantasy"),
    ("/roc",                        "SF/Fantasy"),
    ("penguin/roc",                 "SF/Fantasy"),
]


def infer_bucket_from_publisher(publisher: str) -> str:
    """Infer genre bucket from publisher name using specialist press heuristics.

    Returns a bucket string, or 'Unknown' if the publisher is a general trade
    house or not recognized. 'SF/Fantasy' is returned when we know it's a
    specialist SFF press but can't distinguish SF from Fantasy.
    """
    if not isinstance(publisher, str) or not publisher.strip():
        return "Unknown"
    pub = publisher.lower()
    for substring, bucket in PUBLISHER_RULES:
        if substring in pub:
            return bucket
    return "Unknown"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        csv_files = [f for f in glob.glob("books_2*.csv") if "_normalized" not in f]
        if not csv_files:
            print("No books CSV found.")
            raise SystemExit(1)
        filename = max(csv_files, key=lambda f: __import__("os").path.getmtime(f))

    print(f"Loading {filename}\n")

    df = pd.read_csv(filename)
    df["genre_bucket"] = df["genre"].apply(genre_bucket)
    df["genre_label"] = df["genre"].apply(genre_label)
    df["year"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.year.astype("Int64")
    df["is_cozy"] = df["genre"].str.contains(r"\bcozy\b", case=False, na=False)
    df["media_tie_in"] = df["genre"].str.contains(r"tie-?in", case=False, na=False).map({True: "Media Tie-In", False: ""})

    # Pass 1: description-based inference for Unknown entries
    unknown_mask = df["genre_bucket"] == "Unknown"
    df["genre_inferred"] = ""
    df.loc[unknown_mask, "genre_inferred"] = df.loc[unknown_mask, "description"].apply(infer_bucket_from_description)
    df["genre_source"] = "label"
    df.loc[unknown_mask & (df["genre_inferred"] != "Unknown"), "genre_source"] = "description"
    df.loc[unknown_mask & (df["genre_inferred"] == "Unknown"), "genre_source"] = "unknown"

    resolved_desc = (unknown_mask & (df["genre_inferred"] != "Unknown")).sum()
    print(f"=== Pass 1 — Description inference: {resolved_desc} of {unknown_mask.sum()} Unknowns resolved ===")
    print(df.loc[unknown_mask, "genre_inferred"].value_counts().to_string())

    # Pass 2: publisher heuristics for entries still unresolved after description inference
    still_unknown = (df["genre_bucket"] == "Unknown") & (df["genre_inferred"] == "Unknown")
    pub_inferred = df.loc[still_unknown, "publisher"].apply(infer_bucket_from_publisher)
    resolved_by_pub = pub_inferred[pub_inferred != "Unknown"]
    df.loc[resolved_by_pub.index, "genre_inferred"] = resolved_by_pub
    df.loc[resolved_by_pub.index, "genre_source"] = "publisher"

    resolved_pub = (still_unknown & (df["genre_inferred"] != "Unknown")).sum()
    print(f"\n=== Pass 2 — Publisher heuristics: {resolved_pub} more resolved ===")
    print(df.loc[still_unknown, "genre_inferred"].value_counts().to_string())

    total_resolved = resolved_desc + resolved_pub
    total_unknown = unknown_mask.sum()
    print(f"\n=== Total: {total_resolved} of {total_unknown} Unknowns resolved ({total_resolved/total_unknown*100:.1f}%) ===")

    print("\n=== Genre bucket distribution (all years, label only) ===")
    print("    (use genre_inferred for pre-2022 Unknown entries)")
    print()
    counts = df["genre_bucket"].value_counts()
    pct = (counts / len(df) * 100).round(1)
    print(pd.DataFrame({"count": counts, "%": pct}).to_string())

    print("\n=== Genre bucket by year — 2022+ (most reliable genre data) ===")
    recent = df[df["year"] >= 2022].copy()
    pivot = (
        recent.groupby(["year", "genre_bucket"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["SF", "Fantasy", "Horror", "YA", "Non-fiction", "Other", "Unknown"], fill_value=0)
    )
    print(pivot.to_string())

    print("\n=== Cozy books per year (2022+) ===")
    print(recent[recent["is_cozy"]].groupby("year").size().to_string())

    print("\n=== Media Tie-In books per year (2022+) ===")
    print(recent[recent["media_tie_in"] != ""].groupby("year").size().to_string())

    print("\n=== 'Other' bucket — top labels (candidates for new rules) ===")
    other_genres = df[df["genre_bucket"] == "Other"]["genre"].value_counts()
    print(other_genres.head(20).to_string())

    out_file = filename.replace(".csv", "_normalized.csv")
    df.to_csv(out_file, index=False)
    print(f"\nSaved to {out_file}")
