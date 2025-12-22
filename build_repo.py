import fitz
import re
import json

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def build_repo():
    doc = fitz.open(PDF_FILE)
    repo = {} # (section, pnum) -> text
    
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
        
        for name, rect in quads:
            text = page.get_text("text", clip=rect)
            if not text.strip(): continue
            
            # Find page number and section
            # Check first 5 lines
            lines = text.split('\n')[:5] + text.split('\n')[-3:]
            pnum = None
            section = "GENERAL"
            
            for l in lines:
                l = l.strip()
                if re.match(r'^\d+$', l):
                    pnum = int(l)
                    break
                # Catch "15 Stories of..."
                m = re.match(r'^(\d+)\s+(.+)', l)
                if m:
                    pnum = int(m.group(1))
                    section = m.group(2)
                    break
            
            # If no number found, check if this is the start of a book (Index/Title)
            if not pnum:
                if "STORIES OF THE SAHAABAH" in text.upper(): section = "SAHAABAH"
                if "VIRTUES OF" in text.upper(): section = "VIRTUES"
                
            if pnum is not None:
                # Clean section
                section = re.sub(r'^[IVX\d\.\s]+', '', section).strip().upper()
                key = (section, pnum)
                # Store the most complete version
                if key not in repo or len(text) > len(repo[key]):
                    repo[key] = text
                    
    return repo

repo = build_repo()
print(f"Captured {len(repo)} logical pages.")
keys = sorted(repo.keys())
for k in keys[:20]:
    print(f"{k}: {len(repo[k])} chars")
