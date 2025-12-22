import fitz
import re
import json

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def detect_strips():
    doc = fitz.open(PDF_FILE)
    results = []
    
    for i in range(len(doc)):
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        # Strips: [0-186, 186-373, 373-560, 560-747]
        strip_bounds = [
            (0, 186),
            (186, 373),
            (373, 560),
            (560, 747)
        ]
        
        page_strips = []
        for start_x, end_x in strip_bounds:
            rect = fitz.Rect(start_x, 0, end_x, h)
            text = page.get_text("text", clip=rect)
            
            # Detect number at top
            top_text = page.get_text("text", clip=fitz.Rect(start_x, 0, end_x, 100))
            # Number is usually on its own line or at start
            num_match = re.search(r'^\s*(\d+)', top_text)
            if not num_match:
                 # Check if it's the only digits on a line
                 lines = top_text.split('\n')
                 for l in lines:
                     if re.match(r'^\s*\d+\s*$', l):
                         num_match = re.search(r'(\d+)', l)
                         break
            
            num = int(num_match.group(1)) if num_match else None
            page_strips.append({"num": num, "text": text})
            
        print(f"P{i}: {[s['num'] for s in page_strips]}")
        results.append(page_strips)
        
    return results

detect_strips()
