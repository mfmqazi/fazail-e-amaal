import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def map_logical():
    doc = fitz.open(PDF_FILE)
    for i in range(50):
        page = doc[i]
        blocks = page.get_text("blocks")
        # Find all blocks that are just a number or start with a number
        found = []
        for b in blocks:
            # Look for page numbers (usually small, top or bottom)
            t = b[4].strip()
            m = re.match(r'^(\d+)\s*$', t)
            if m:
                num = int(m.group(1))
                if num < 1000:
                    found.append((num, b[0], b[1]))
        
        if found:
            # Sort by X
            found.sort(key=lambda x: x[1])
            print(f"Physical {i}: {found}")

map_logical()
