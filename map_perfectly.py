import fitz
import re
import json

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

# Verified Book Ranges (Physical Index)
BOOKS = [
    {"id": 1, "name": "Sahaabah", "start": 0, "end": 135},
    {"id": 2, "name": "Quran", "start": 136, "end": 193},
    {"id": 3, "name": "Salaat", "start": 194, "end": 246},
    {"id": 4, "name": "Zikr", "start": 247, "end": 369},
    {"id": 5, "name": "Tabligh", "start": 370, "end": 394},
    {"id": 6, "name": "Ramadhaan", "start": 395, "end": 410},
    {"id": 7, "name": "Muslim Degeneration", "start": 411, "end": 430},
    {"id": 8, "name": "Six Fundamentals", "start": 431, "end": 451}
]

def map_perfectly():
    doc = fitz.open(PDF_FILE)
    page_map = {} # (book_id, p_num) -> (phys_idx, quad_name)
    
    for book in BOOKS:
        print(f"Mapping {book['name']} (Physical {book['start']}-{book['end']})...")
        for i in range(book['start'], book['end'] + 1):
            if i >= len(doc): break
            page = doc[i]
            w, h = page.rect.width, page.rect.height
            
            # Quads: [LT, RT, LB, RB]
            quads = [
                ("LT", fitz.Rect(0, 0, w/2, h/2)),
                ("RT", fitz.Rect(w/2, 0, w, h/2)),
                ("LB", fitz.Rect(0, h/2, w/2, h)),
                ("RB", fitz.Rect(w/2, h/2, w, h))
            ]
            
            for q_name, rect in quads:
                # Use "dict" to get precise locations
                blocks = page.get_text("dict", clip=rect)["blocks"]
                found_nums = []
                for b in blocks:
                    if "lines" not in b: continue
                    for l in b["lines"]:
                        for s in l["spans"]:
                            txt = s["text"].strip()
                            # Check if span is just a number
                            if re.match(r'^\d+$', txt):
                                num = int(txt)
                                if num < 500:
                                    # Record Y coordinate to distinguish Top/Bottom
                                    found_nums.append((num, s["origin"][1]))
                
                if found_nums:
                    # Usually the page number is at the top of the logical page
                    # Or bottom? 
                    # For a quadrant, we pick the one that is most "header-like" or "footer-like"
                    for num, y in found_nums:
                        page_map[(book['id'], num)] = (i, q_name)
                        
    return page_map

pm = map_perfectly()
print(f"Mapped {len(pm)} logical pages.")

# Save map
with open("page_map_v9.json", "w") as f:
    # Convert keys to strings for JSON
    json.dump({f"{k[0]}|{k[1]}": v for k, v in pm.items()}, f)
