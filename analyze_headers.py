import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def analyze_headers():
    doc = fitz.open(PDF_FILE)
    
    # Book 3 starts ~181 (from metadata). Headers likely around 190-200 based on ToC (195).
    # Let's scan 195-200.
    print("Scanning Pages 195-205 for Headers (Size > 12)...")
    
    for p_num in range(195, 205):
        page = doc[p_num]
        blocks = page.get_text("dict")["blocks"]
        
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if s['size'] > 12:
                            print(f"Page {p_num} | Size: {s['size']:.1f} | Text: {s['text'].strip()}")

if __name__ == "__main__":
    analyze_headers()
