import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def find_chapter_headers():
    doc = fitz.open(PDF_FILE)
    print("Searching for 'CHAPTER' or 'PART' in Book 3 (Pages 180-260)...")
    
    for p_num in range(180, 260):
        page = doc[p_num]
        blocks = page.get_text("dict")["blocks"]
        
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip().upper()
                        # fuzzy check
                        if "CHAPTER" in text or "PART" in text:
                            print(f"Page {p_num} | Size: {s['size']:.2f} | Text: {text}")

if __name__ == "__main__":
    find_chapter_headers()
