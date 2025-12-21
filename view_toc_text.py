import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def view_toc():
    doc = fitz.open(PDF_FILE)
    page = doc[3] # Page 4
    print(page.get_text())

if __name__ == "__main__":
    view_toc()
