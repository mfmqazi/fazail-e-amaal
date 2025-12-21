import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def check_dims():
    doc = fitz.open(PDF_FILE)
    page = doc[10]
    rect = page.rect
    print(f"Page 10 Dimensions: {rect.width} x {rect.height}")
    if rect.width > rect.height:
        print("Orientation: Landscape (Likely Spread)")
    else:
        print("Orientation: Portrait")

if __name__ == "__main__":
    check_dims()
