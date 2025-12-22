import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

BOOKS = [
    "STORIES OF THE SAHAABAH",
    "VIRTUES OF THE HOLY QUR",
    "VIRTUES OF SALAAT",
    "VIRTUES OF ZIKR",
    "VIRTUES OF TABLIGH",
    "VIRTUES OF RAMADHAAN",
    "MUSLIM DEGENERATION",
    "SIX FUNDAMENTALS"
]

def map_books():
    doc = fitz.open(PDF_FILE)
    found = {}
    for i in range(20, len(doc)): # Skip ToC pages
        text = doc[i].get_text().upper()
        # Clean text: remove multiple spaces
        clean = " ".join(text.split())
        for b in BOOKS:
            # Check if title is on the page and it's NOT a ToC entry (no dots)
            if b in clean and b not in found:
                # ToC check: if the line has many dots or a page number at end
                # Usually titles are alone on a line.
                lines = [l for l in text.split('\n') if b in l.upper()]
                is_toc = any("...." in l or re.search(r'\d+$', l.strip()) for l in lines)
                if not is_toc or len(clean) < 200: # Short pages are often title pages
                    found[b] = i
                    print(f"Book '{b}' starts at Index {i}")
    
    print("\nSUMMARY:")
    for b in BOOKS:
        print(f"{b} -> {found.get(b, 'NOT FOUND')}")

map_books()
