import fitz
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def parse_master_toc():
    doc = fitz.open(PDF_FILE)
    print("Parsing Master ToC (Pages 3-7)...")
    
    # PDF Page 4 is index 3
    toc_text = ""
    for p_num in range(3, 8):
        page = doc[p_num]
        text = page.get_text()
        toc_text += text + "\n"
    
    # Process lines
    lines = toc_text.split('\n')
    entries = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Pattern: "Title .... 123" or "Title 123"
        # Often gaps are spaces or dots
        # Regex: Text followed by optional dots/spaces and a number at end
        match = re.search(r'^(.*?)(?:\.{2,}|\s{2,})(\d+)$', line)
        if match:
            title = match.group(1).strip(" .")
            page_num = int(match.group(2))
            
            # Filter noise
            if len(title) > 3 and page_num > 0:
                entries.append({"title": title, "page": page_num})
                print(f"Found: {title} -> {page_num}")
        else:
            # Maybe spacing is weird. Try searching for number at end
             pass

    # Save to file for inspection
    with open("toc_entries.txt", "w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"{e['title']} | {e['page']}\n")

if __name__ == "__main__":
    parse_master_toc()
