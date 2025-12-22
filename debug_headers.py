import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def debug_headers():
    doc = fitz.open(PDF_FILE)
    for i in range(10, 20):
        page = doc[i]
        h = page.rect.height
        top_blocks = [b for b in page.get_text("blocks") if b[1] < h * 0.15]
        print(f"P{i}:")
        for b in top_blocks:
             print(f"  {b[4].strip()} at x={b[0]}")

debug_headers()
