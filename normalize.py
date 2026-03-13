#!/usr/bin/env python3
"""Genre normalization for Locus Magazine book data.

Adds two columns to the most recent books CSV:
  genre_bucket  — broad category for trend analysis
  genre_label   — genre string with format suffix stripped (no "novel", "novella", etc.)

Bucket priority (first match wins):
  YA          — young-adult, young adult, middle-grade, standalone "ya"
  SF          — sf, science fiction, space opera, cyberpunk, solarpunk, biopunk
  Horror      — horror
  Romance     — romance
  Fantasy     — fantasy
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
    ]),
    ("Horror", [
        r"horror",
    ]),
    ("Romance", [
        r"romance",
    ]),
    ("Fantasy", [
        r"fantasy",
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
    # Collapse multiple spaces
    return re.sub(r"\s{2,}", " ", cleaned)


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

    print("=== Genre bucket distribution (all years) ===")
    counts = df["genre_bucket"].value_counts()
    pct = (counts / len(df) * 100).round(1)
    summary = pd.DataFrame({"count": counts, "%": pct})
    print(summary.to_string())

    print("\n=== Genre bucket by year — 2022+ (most reliable genre data) ===")
    recent = df[df["year"] >= 2022].copy()
    pivot = (
        recent.groupby(["year", "genre_bucket"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["SF", "Fantasy", "Horror", "YA", "Romance", "Non-fiction", "Other", "Unknown"], fill_value=0)
    )
    print(pivot.to_string())

    print("\n=== 'Other' bucket — top labels (candidates for new rules) ===")
    other_genres = df[df["genre_bucket"] == "Other"]["genre"].value_counts()
    print(other_genres.head(20).to_string())

    out_file = filename.replace(".csv", "_normalized.csv")
    df.to_csv(out_file, index=False)
    print(f"\nSaved to {out_file}")
