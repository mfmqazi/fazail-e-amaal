import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

ANCHORS = {
    1: "JOURNEY TO TAIF",
    2: "WHO IS THE BEST PERSON",
    3: "REWARDS OF SALAAT",
    4: "VIRTUES OF ZIKR IN GENERAL",
    5: "LETTER TO HERACLIUS",
    6: "VIRTUES OF RAMADHAAN",
    7: "MUSLIM DEGENERATION",
    8: "SIX FUNDAMENTALS"
}

def get_linear_pages(doc):
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        left = page.get_text("text", clip=fitz.Rect(0, 0, w/2, h))
        right = page.get_text("text", clip=fitz.Rect(w/2, 0, w, h))
        pages.append(left)
        pages.append(right)
    return pages

def sync():
    doc = fitz.open(PDF_FILE)
    pages = get_linear_pages(doc)
    
    offsets = {}
    for book_id, anchor in ANCHORS.items():
        found = False
        for i, text in enumerate(pages):
            if anchor in text.upper() and ("CONTENTS" not in text.upper() and "INDEX" not in text.upper()):
                # Check for page number on that page
                m = re.search(r'\n\s*(\d+)\s*\n', text)
                if not m:
                    m = re.search(r'(\d+)\s*Stories of', text)
                if not m:
                     m = re.search(r'\n(\d+)\n', text)
                     
                if m:
                    logical_p = int(m.group(1))
                    offset = i - logical_p
                    offsets[book_id] = {"idx": i, "logical": logical_p, "offset": offset, "anchor": anchor}
                    print(f"Book {book_id}: Found {anchor} at linear index {i}, Logical Page {logical_p}. Offset: {offset}")
                    found = True
                    break
        if not found:
            print(f"Book {book_id}: Anchor {anchor} NOT FOUND")
            
    return offsets

if __name__ == "__main__":
    sync()
