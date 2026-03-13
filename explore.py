#!/usr/bin/env python3

import pandas as pd
import glob

# Load the most recent CSV
csv_files = sorted(glob.glob('books_2*.csv'))
filename = csv_files[-1]
print(f"Loading {filename}\n")

df = pd.read_csv(filename)

print(f"Total books: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nDate range: {df['publication_date'].min()} to {df['publication_date'].max()}")
print(f"Missing dates: {df['publication_date'].isna().sum()}")
print(f"Missing genres: {(df['genre'] == '').sum() + df['genre'].isna().sum()}")

print("\n--- Books per year ---")
df['year'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.year
print(df['year'].value_counts().sort_index().to_string())

def clean_genre(text):
    if not isinstance(text, str) or not text:
        return ""
    period_idx = text.find('.')
    comma_idx = text.find(',')
    indices = [i for i in [period_idx, comma_idx] if i > 0]
    return text[:min(indices)].strip() if indices else text.strip()

df['genre_clean'] = df['genre'].apply(clean_genre)

print("\n--- Top 30 genres ---")
print(df[df['genre_clean'] != '']['genre_clean'].value_counts().head(30).to_string())

print("\n--- Sample source URLs with missing genre (2011-2021) ---")
missing = df[
    (df['genre_clean'] == '') &
    (df['year'] >= 2011) &
    (df['year'] <= 2021)
]['source_url'].dropna().unique()
for url in missing[:5]:
    print(url)
