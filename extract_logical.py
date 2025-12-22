import fitz
import re
import json

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def get_logical_pages():
    doc = fitz.open(PDF_FILE)
    pages_db = {} # (section_name, page_num) -> content
    
    for i in range(len(doc)):
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        blocks = page.get_text("blocks")
        
        # 1. Identify all page numbers on this physical sheet
        # A block is a page number if it's a small integer and at the top or bottom
        # And usually near a book title
        
        headers = [b for b in blocks if b[1] < 100] # Top 100 units
        
        # Map X-coordinates of page numbers to their values
        num_cols = {} # x_center -> num
        for b in headers:
            text = b[4].strip()
            if re.match(r'^\d+$', text):
                num = int(text)
                if num < 1000: # Ignore years/etc
                    x_mid = (b[0] + b[2]) / 2
                    num_cols[x_mid] = num
        
        if not num_cols:
            continue
            
        # 2. For each number found, identify the book section
        # The section title is usually near the number
        for x_mid, p_num in num_cols.items():
            # Find closest text that looks like a section title
            section = "Unknown"
            min_dist = 999
            for b in headers:
                t = b[4].strip()
                if len(t) > 5 and not t.isdigit():
                    dist = abs(((b[0] + b[2]) / 2) - x_mid)
                    if dist < min_dist:
                        min_dist = dist
                        section = t
            
            # Clean section name
            section = re.sub(r'^[IVX\d\.\s]+', '', section).strip()
            section = re.sub(r'\s*Page No:.*', '', section, flags=re.I).strip()
            
            # 3. Extract all text in this column (approx +/- 180 units around x_mid)
            col_rect = fitz.Rect(x_mid - 170, 0, x_mid + 170, h)
            col_text = page.get_text("text", clip=col_rect)
            
            key = (section.upper(), p_num)
            if key not in pages_db or len(col_text) > len(pages_db[key]):
                pages_db[key] = col_text
                
    return pages_db

# Test it
db = get_logical_pages()
print(f"Detected {len(db)} unique logical pages.")
# Sorted keys
keys = sorted(db.keys())
for k in keys[:20]:
    print(f"{k[0]} - Page {k[1]}: {len(db[k])} chars")
