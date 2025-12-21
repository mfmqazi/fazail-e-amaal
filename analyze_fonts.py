import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def analyze_fonts():
    try:
        doc = fitz.open(PDF_FILE)
        
        # Sample pages: 10 (Book 1), 200 (Book 3)
        pages_to_check = [10, 200]
        
        for p_num in pages_to_check:
            print(f"\n--- Analysis of Page {p_num} ---")
            page = doc[p_num]
            blocks = page.get_text("dict")["blocks"]
            
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            text = s["text"].strip()
                            if text:
                                print(f"Size: {s['size']:.2f} | Font: {s['font']} | Text: {text[:50]}...")
                                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_fonts()
