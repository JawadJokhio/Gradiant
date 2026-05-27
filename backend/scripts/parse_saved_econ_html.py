"""Parse saved papacambridge economics HTML pages into a structured JSON dataset.

Place downloaded HTML files into `data/economics/` (e.g., index.html and page_*.html).
This script will attempt to extract MCQ items and simple mark scheme text where possible.
Best-effort parser using BeautifulSoup if available; otherwise prints instructions.
"""
import os
import json
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "economics"
OUT_PATH = DATA_DIR / "economics_dataset_parsed.json"

def parse_file(path: Path):
    if not BeautifulSoup:
        raise RuntimeError("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
    with path.open('r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    items = []
    # Heuristic: look for paragraphs or list items that look like MCQs
    texts = soup.find_all(['p', 'li', 'div', 'span'])
    for t in texts:
        txt = t.get_text(separator=' ', strip=True)
        if not txt:
            continue
        # crude MCQ detection: presence of options A) or (A) or 'A.' and 'B.'
        if ('A)' in txt or '(A)' in txt or 'A.' in txt) and ('B)' in txt or '(B)' in txt or 'B.' in txt):
            items.append(txt)
    return items

def main():
    if not DATA_DIR.exists():
        print("No data/economics directory found. Save papacambridge HTML files there first.")
        return
    pages = sorted(DATA_DIR.glob('*.html'))
    if not pages:
        print("No HTML files found in data/economics/")
        return

    dataset = {"past_papers": {}, "exam_tips": []}
    for p in pages:
        try:
            found = parse_file(p)
        except Exception as e:
            print("Skipping", p.name, "—", e)
            continue
        if found:
            dataset['past_papers'].setdefault('imported', {})[p.name] = {"paper_1": {"mark_scheme": []}}
            for txt in found:
                dataset['past_papers']['imported'][p.name]['paper_1']['mark_scheme'].append({
                    "question": txt,
                    "marks": 1,
                    "options": [],
                    "correct": None,
                    "examiner_tips": []
                })

    with OUT_PATH.open('w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print("Wrote parsed dataset to", OUT_PATH)

if __name__ == '__main__':
    main()
