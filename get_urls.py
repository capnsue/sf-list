#!/usr/bin/env python3

import requests
import time
from bs4 import BeautifulSoup

CATEGORY_URL = "https://locusmag.com/category/newtitlesbestsellers/page/{}/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def get_release_urls():
    urls = []
    page = 1

    with open('urls.txt', 'w') as f:
        while True:
            url = CATEGORY_URL.format(page)
            print(f"Fetching page {page}...", end=" ", flush=True)

            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 404:
                print("done.")
                break
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)

            found = 0
            for link in links:
                href = link['href']
                if ('new-book-releases-' in href or 'new-books-' in href) and href not in urls:
                    urls.append(href)
                    f.write(href + '\n')
                    f.flush()
                    found += 1

            print(f"found {found} release URLs")
            time.sleep(1)
            page += 1

    return urls


if __name__ == '__main__':
    urls = get_release_urls()
    print(f"\nTotal: {len(urls)} release pages saved to urls.txt")
