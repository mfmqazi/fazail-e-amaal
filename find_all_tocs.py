import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

BOOKS = [
    {"id": 1, "title": "STORIES OF THE SAHAABAH", "search": "STORIES OF THE SAHAABAH"},
    {"id": 2, "title": "VIRTUES OF THE HOLY QUR", "search": "VIRTUES OF THE HOLY QUR"},
    {"id": 3, "title": "VIRTUES OF SALAAT", "search": "VIRTUES OF SALAAT"},
    {"id": 4, "title": "VIRTUES OF ZIKR", "search": "VIRTUES OF ZIKR"},
    {"id": 5, "title": "VIRTUES OF TABLIGH", "search": "VIRTUES OF TABLIGH"},
    {"id": 6, "title": "VIRTUES OF RAMADHAAN", "search": "VIRTUES OF RAMADHAAN"},
    {"id": 7, "title": "MUSLIM DEGENERATION", "search": "MUSLIM DEGENERATION"},
    {"id": 8, "title": "SIX FUNDAMENTALS", "search": "SIX FUNDAMENTALS"}
]

def find_tocs():
    doc = fitz.open(PDF_FILE)
    results = {}
    
    # Range of pages to check around expected book starts
    for book in BOOKS:
        found_start = -1
        found_toc = -1
        
        # Scan pages to find the start of the book section
        for i in range(len(doc)):
            text = doc[i].get_text().upper()
            if book["search"] in text:
                if "PART I" in text or "CHAPTER I" in text or "CONTENTS" in text:
                    if found_start == -1: 
                        found_start = i
                if "CONTENTS" in text:
                    if found_toc == -1:
                        found_toc = i
        
        results[book["id"]] = {"start": found_start, "toc": found_toc}
        print(f"Book {book['id']} ({book['title']}): Start Index={found_start}, TOC Index={found_toc}")

find_tocs()
