import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def audit():
    doc = fitz.open(PDF_FILE)
    mapping = []
    
    for i in range(len(doc)):
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        
        # Clip top area for numbers
        top_rect = fitz.Rect(0, 0, w, 100)
        left_top = page.get_text("text", clip=fitz.Rect(0, 0, w/2, 100))
        right_top = page.get_text("text", clip=fitz.Rect(w/2, 0, w, 100))
        
        l_num = re.search(r'^\s*(\d+)', left_top)
        r_num = re.search(r'^\s*(\d+)', right_top)
        
        ln = int(l_num.group(1)) if l_num else None
        rn = int(r_num.group(1)) if r_num else None
        
        # Sometimes numbers are at the end/bottom? Or different parts.
        if not ln:
            l_num = re.search(r'(\d+)\s*$', left_top)
            ln = int(l_num.group(1)) if l_num else None
        if not rn:
            r_num = re.search(r'(\d+)\s*$', right_top)
            rn = int(r_num.group(1)) if r_num else None
            
        print(f"Physical {i}: Left={ln}, Right={rn}")

audit()
