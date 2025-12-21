import fitz

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

def extract_toc_structured():
    doc = fitz.open(PDF_FILE)
    print("Extracting Structured ToC (Pages 3-7)...")
    
    entries = []
    
    # Iterate ToC pages
    for p_num in range(3, 15):
        page = doc[p_num]
        items = page.get_text("dict")["blocks"]
        
        # Collect text spans with coordinates
        spans = []
        for b in items:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text and text != "." and not text.replace('.', '').strip() == "":
                             spans.append({
                                 "text": text,
                                 "x": s["bbox"][0],
                                 "y": s["bbox"][1],
                                 "size": s["size"]
                             })
        
        # Sort by Y (vertical), then X (horizontal)
        spans.sort(key=lambda s: (round(s["y"], 1), s["x"]))
        
        # Group by Line (Y-coordinate proximity)
        lines = []
        current_line = []
        last_y = -100
        
        for s in spans:
            if abs(s["y"] - last_y) < 5: # Same line tolerance
                current_line.append(s)
            else:
                if current_line: lines.append(current_line)
                current_line = [s]
                last_y = s["y"]
        if current_line: lines.append(current_line)
        
        # Process lines to find Title + Page Number
        for line in lines:
            line_text = " ".join([s["text"] for s in line])
            
            # Check for Page Number at end (Rightmost element)
            last_item = line[-1]
            # Is it a number?
            page_num = -1
            if last_item["text"].isdigit():
                page_num = int(last_item["text"])
            
            # Identify Headers (Center, Bold, Keywords)
            # Chapter Headers typically don't have page numbers on same line in this PDF?
            # Image shows: "CHAPTER II" (No number). "FEAR OF ALLAH" (No number).
            # Image shows: "Prophet's Journey... ... 15"
            
            if page_num > 0:
                # This is a story entry
                title_parts = [s["text"] for s in line[:-1]]
                title = " ".join(title_parts).strip(" .")
                if title:
                    entries.append({"type": "story", "title": title, "page": page_num})
            else:
                 # Header or multi-line title continuation
                 # Check keywords
                 raw_text = line_text.upper()
                 if "CHAPTER" in raw_text or "STORY" in raw_text or "VIRTUES" in raw_text or "PART" in raw_text:
                     entries.append({"type": "header", "title": line_text})  
                 
    import json
    with open("toc_extracted.json", "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4)
    print(f"Saved {len(entries)} entries to toc_extracted.json")

if __name__ == "__main__":
    extract_toc_structured()
