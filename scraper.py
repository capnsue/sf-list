#!/usr/bin/env python3

import requests
import csv
import time
from bs4 import BeautifulSoup
from datetime import datetime
import re


def extract_page_count(text):
    """Extract page count from text like '400pp', returned as int"""
    match = re.search(r'(\d+)pp', text)
    return int(match.group(1)) if match else None


def extract_pub_date(text):
    """Extract and normalize publication date to YYYY-MM-DD.
    Handles:
    - 03/10/2026      → 2026-03-10
    - June 7, 2022    → 2022-06-07
    - August 2011     → 2011-08-01 (day unknown, use 01)
    """
    # MM/DD/YYYY
    match = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    if match:
        return f"{match.group(3)}-{match.group(1)}-{match.group(2)}"
    # Month Day, Year
    match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})', text)
    if match:
        dt = datetime.strptime(match.group(0), '%B %d, %Y')
        return dt.strftime('%Y-%m-%d')
    # Month Year (day unknown)
    match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', text)
    if match:
        dt = datetime.strptime(match.group(0), '%B %Y')
        return dt.strftime('%Y-%m-01')
    return ""


def extract_publisher(text):
    """Extract publisher from parenthesized section"""
    # Format: "(Publisher ISBN, $Price, ###pp, formats, MM/DD/YYYY)"
    # We want just the publisher name before the ISBN
    paren_match = re.search(r'\(([^)]+)\)', text)
    if paren_match:
        paren_content = paren_match.group(1)
        # Publisher is first part before ISBN (which starts with 9 usually)
        publisher_match = re.match(r'^([^0-9]+?)(?:\s+978|\s+\d{3}|$)', paren_content)
        if publisher_match:
            return publisher_match.group(1).strip()
    return ""


def extract_genre(text):
    """Extract genre - everything before the first period or comma"""
    if not text:
        return ""
    period_idx = text.find('.')
    comma_idx = text.find(',')
    # Take whichever delimiter comes first
    indices = [i for i in [period_idx, comma_idx] if i > 0]
    if indices:
        return text[:min(indices)].strip()
    return ""


def extract_author_and_title(para_text, bold_text):
    """Extract author from paragraph and title from bold text

    Format: "AuthorName: Title (details...)"
    Bold text contains only the title
    """
    # Find author by looking for text before the colon
    colon_idx = para_text.find(':')
    if colon_idx > 0:
        author_part = para_text[:colon_idx].strip()
        # Clean up - remove leading whitespace, HTML artifacts, and bullet markers (* + •)
        author = author_part.split('\n')[-1].strip().lstrip('*+•- ').strip()
        return author, bold_text

    return "", bold_text


def scrape_page(url, scrape_date=None, debug=False):
    if scrape_date is None:
        scrape_date = datetime.now().strftime('%Y-%m-%d')
    """Scrape a single Locus page and return list of books"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    books = []

    # Find all paragraphs in the main content
    paragraphs = soup.find_all('p')

    for i, para in enumerate(paragraphs):
        # Look for book entries: should have bold text (title/author) followed by details
        bold = para.find('strong') or para.find('b')

        if not bold:
            continue

        # Get the bold text (author/title)
        bold_text = bold.get_text(strip=True)

        # Skip if this looks like a section header or non-book content
        if any(skip in bold_text.lower() for skip in ['week of', 'support', 'locus', 'click']):
            continue

        # Get full paragraph text for extracting details
        para_text = para.get_text()

        # Skip if bold text doesn't appear near the start — it's emphasis within a description
        bold_pos = para_text.find(bold_text)
        if bold_pos > 80:
            continue

        # Extract author from paragraph, title from bold text
        author, title = extract_author_and_title(para_text, bold_text)

        # Find which paragraph contains publication details (page count or date)
        next1 = paragraphs[i + 1].get_text() if i + 1 < len(paragraphs) else ""
        next2 = paragraphs[i + 2].get_text() if i + 2 < len(paragraphs) else ""

        if extract_page_count(para_text) or extract_pub_date(para_text):
            # Details in same paragraph, genre in next (2026-era)
            details_text = para_text
            genre_candidate = next1
        elif extract_page_count(next1) or extract_pub_date(next1):
            # Details in next1, genre after paren or in next2 (2022-era)
            details_text = next1
            genre_candidate = next2
        else:
            # Details in next2, genre in next1 (2024-era)
            details_text = next2
            genre_candidate = next1

        publisher = extract_publisher(details_text)
        page_count = extract_page_count(details_text)
        pub_date = extract_pub_date(details_text)

        # Genre: text after closing paren in details paragraph, or the genre candidate paragraph
        paren_close = details_text.rfind(')')
        after_paren = details_text[paren_close + 1:].strip() if paren_close > 0 else ""
        genre = extract_genre(after_paren) if after_paren else extract_genre(genre_candidate)

        if debug and len(books) < 3:
            print(f"\nDEBUG Entry {i}: Bold text = '{bold_text}'")
            print(f"  Para: {para_text[:100]}")
            print(f"  Details: {details_text[:100]}")
            print(f"  Genre candidate: {genre_candidate[:100]}")
            print(f"  Genre: '{genre}'")

        # Only add if we found meaningful data
        if title and (page_count or pub_date):
            books.append({
                'author': author,
                'title': title,
                'publisher': publisher,
                'page_count': page_count,
                'publication_date': pub_date,
                'genre': genre,
                'source_url': url,
                'date_scraped': scrape_date,
            })

    return books



if __name__ == '__main__':
    with open('urls.txt') as f:
        urls = [line.strip() for line in f if line.strip() and '#' not in line]

    print(f"Loaded {len(urls)} URLs")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"books_{timestamp}.csv"
    fieldnames = ['author', 'title', 'publisher', 'page_count', 'publication_date', 'genre', 'source_url', 'date_scraped']
    scrape_date = datetime.now().strftime('%Y-%m-%d')

    total = 0
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Scraping {url}...")
            books = scrape_page(url, scrape_date=scrape_date)
            writer.writerows(books)
            f.flush()
            total += len(books)
            time.sleep(1)

    print(f"\nTotal books: {total} — saved to {filename}")
