import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def view_page_15():
    doc = fitz.open(PDF_FILE)
    # Check Index 15 (Page 16?)
    # Check Index 14 (Page 15?)
    # Check Index 20 (Hypothetical offset)
    
    indices = [15, 20, 25]
    for idx in indices:
        print(f"\n--- PDF Index {idx} ---")
        try:
            print(doc[idx].get_text()[:300])
        except:
            pass

if __name__ == "__main__":
    view_page_15()
