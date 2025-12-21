import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def calculate_offset():
    doc = fitz.open(PDF_FILE)
    
    target_text = "Journey to Taif"
    print(f"Searching for '{target_text}' in first 50 pages to determine offset...")
    
    found_page = -1
    for p_num in range(50):
        page = doc[p_num]
        text = page.get_text()
        if target_text.upper() in text.upper():
             print(f"Found '{target_text}' on PDF Page Index {p_num}")
             # Print tiny context
             print(text[:100].replace('\n', ' '))
    
    if found_page != -1:
        # ToC says Page 15.
        # If found at PDF Index 20.
        # Offset = 20 - 15 = 5.
        # Check printed page number on that page
        # Usually at bottom
        pass

if __name__ == "__main__":
    calculate_offset()
