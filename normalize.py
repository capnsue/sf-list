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

    # Description-based inference for Unknown entries
    unknown_mask = df["genre_bucket"] == "Unknown"
    df["genre_inferred"] = ""
    df.loc[unknown_mask, "genre_inferred"] = df.loc[unknown_mask, "description"].apply(infer_bucket_from_description)
    df["genre_source"] = "label"
    df.loc[unknown_mask & (df["genre_inferred"] != "Unknown"), "genre_source"] = "description"
    df.loc[unknown_mask & (df["genre_inferred"] == "Unknown"), "genre_source"] = "unknown"

    resolved = (unknown_mask & (df["genre_inferred"] != "Unknown")).sum()
    print(f"=== Description inference: {resolved} of {unknown_mask.sum()} Unknowns resolved ===")
    print(df.loc[unknown_mask, "genre_inferred"].value_counts().to_string())

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
