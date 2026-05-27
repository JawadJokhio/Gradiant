"""Simple scraper to download Economics past paper index pages.

This script attempts to fetch the papacambridge index and save HTML pages under data/economics/.
The site may block automated requests; run locally and provide appropriate headers or use a browser-exported HTML.
"""
import os
import requests
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

BASE = "https://pastpapers.papacambridge.com/papers/caie/o-level-economics-2281"
OUT_DIR = os.path.join(os.getcwd(), "data", "economics")

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def fetch_index():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    resp = requests.get(BASE, headers=headers, timeout=20)
    resp.raise_for_status()
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(resp.text)
    return resp.text

def extract_links(html: str):
    if not BeautifulSoup:
        print("bs4 not installed; skipping link extraction. Install with 'pip install beautifulsoup4' to enable full scraping.")
        return []
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.select("a")
    links = []
    for a in anchors:
        href = a.get('href')
        if href and 'papers' in href:
            links.append(href)
    return list(set(links))

def download_links(links):
    headers = {"User-Agent": "Mozilla/5.0"}
    for i, link in enumerate(links[:50]):
        full = link if link.startswith('http') else ('https://pastpapers.papacambridge.com' + link)
        try:
            r = requests.get(full, headers=headers, timeout=20)
            r.raise_for_status()
            fname = os.path.join(OUT_DIR, f"page_{i}.html")
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(r.text)
        except Exception as e:
            print("Failed to download", full, e)

def main():
    ensure_dir()
    try:
        html = fetch_index()
    except Exception as e:
        print("Could not fetch index page:", e)
        return
    links = extract_links(html)
    download_links(links)
    print("Saved index and linked pages to", OUT_DIR)

if __name__ == '__main__':
    main()
