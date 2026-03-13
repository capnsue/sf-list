#!/usr/bin/env python3

from scraper import scrape_page

urls = [
    'https://locusmag.com/2021/04/new-books-20-april-2021/',
]

for url in urls:
    books = scrape_page(url, debug=False)
    print(f"\n{url} -> {len(books)} books")
    for b in books:
        print(f"  {b['author']} | {b['title']} | {b['genre']}")
