import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def view_linear_sample():
    doc = fitz.open(PDF_FILE)
    page = doc[7] # Index 7 = Physical Page 8? Or Logical Page 14/15?
    w, h = page.rect.width, page.rect.height
    
    # Left
    left = page.get_text(clip=fitz.Rect(0, 0, w/2, h))
    print("--- LEFT HALF (Logical Page 14?) ---")
    print(left[:300])
    
    # Right
    right = page.get_text(clip=fitz.Rect(w/2, 0, w, h))
    print("\n--- RIGHT HALF (Logical Page 15?) ---")
    print(right[:300])

if __name__ == "__main__":
    view_linear_sample()
