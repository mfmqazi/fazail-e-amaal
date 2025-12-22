import fitz
import re
import json

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

BOOK_HEADERS = [
    (1, "STORIES OF THE SAHAABAH"),
    (2, "VIRTUES OF THE HOLY QUR"),
    (3, "VIRTUES OF SALAAT"),
    (4, "VIRTUES OF ZIKR"),
    (5, "VIRTUES OF TABLIGH"),
    (6, "VIRTUES OF RAMADHAAN"),
    (7, "MUSLIM DEGENERATION"),
    (8, "SIX FUNDAMENTALS")
]

def map_master():
    doc = fitz.open(PDF_FILE)
    # logical_map[(book_id, page_num)] = (phys_idx, rect)
    logical_map = {}
    
    for i in range(len(doc)):
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        
        # 4 Quadrants
        quads = [
            ("LT", fitz.Rect(0, 0, w/2, h/2)),
            ("RT", fitz.Rect(w/2, 0, w, h/2)),
            ("LB", fitz.Rect(0, h/2, w/2, h)),
            ("RB", fitz.Rect(w/2, h/2, w, h))
        ]
        
        # Determine Book of this physical page (for fallback)
        # Scan whole page for book headers
        page_text = page.get_text().upper()
        current_book_id = None
        for bid, head in BOOK_HEADERS:
            if head in page_text:
                current_book_id = bid
                break
        
        # Some pages have two books (e.g. end of one, start of next)
        # We check per quadrant
        for q_name, rect in quads:
            q_text = page.get_text("text", clip=rect)
            if not q_text.strip(): continue
            
            # Find closest Book Header to this quadrant
            q_book_id = current_book_id
            for bid, head in BOOK_HEADERS:
                if head in q_text.upper():
                    q_book_id = bid
                    break
            
            # Detect Page Number in this quadrant
            # Look at top/bottom 20%
            header_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + (rect.height * 0.2))
            footer_rect = fitz.Rect(rect.x0, rect.y1 - (rect.height * 0.2), rect.x1, rect.y1)
            
            h_text = page.get_text("text", clip=header_rect)
            f_text = page.get_text("text", clip=footer_rect)
            
            pnum = None
            # Search whole quadrant but prioritize top/bottom
            # Look for stands-alone digit in first/last lines
            lines = h_text.split('\n') + f_text.split('\n')
            for l in lines:
                l = l.strip()
                # Check for just digits or digits followed by book name noise
                m = re.match(r'^\s*(\d+)$', l)
                if not m: m = re.search(r'^\s*(\d+)\s+[A-Z]', l)
                if not m: m = re.search(r'^[A-Z].*\s+(\d+)\s*$', l)
                
                if m:
                    pnum = int(m.group(1))
                    if 0 < pnum < 500:
                        break
            
            if pnum and q_book_id:
                # Store
                key = (q_book_id, pnum)
                # If multiple quads claim same page, use the one with more text
                if key not in logical_map or len(q_text) > len(logical_map[key]['text']):
                    logical_map[key] = {
                        "p": i,
                        "q": q_name,
                        "text": q_text
                    }

    return logical_map

master_map = map_master()
print(f"Mapped {len(master_map)} logical pages.")

# Save map
serializable_map = {}
for (bid, pnum), data in master_map.items():
    serializable_map[f"{bid}|{pnum}"] = {"p": data["p"], "q": data["q"]}

with open("master_logical_map.json", "w") as f:
    json.dump(serializable_map, f)
