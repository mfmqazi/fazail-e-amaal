import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"

# TOC Ranges (Physical PDF Indices)
TOC_RANGES = {
    1: range(4, 15),
    2: range(137, 139),
    3: range(195, 198),
    4: range(248, 252),
    5: range(371, 373),
}

def extract_tocs():
    doc = fitz.open(PDF_FILE)
    all_entries = []
    
    for book_id, p_range in TOC_RANGES.items():
        print(f"Extracting TOC for Book {book_id}...")
        book_entries = []
        for p_num in p_range:
            page = doc[p_num]
            words = page.get_text("words")
            # Sort by Y then X
            words.sort(key=lambda w: (round(w[1], 1), w[0]))
            
            lines = []
            cur_line = []
            cur_y = words[0][1] if words else 0
            for w in words:
                if abs(w[1] - cur_y) > 3:
                    lines.append(" ".join(cur_line))
                    cur_line = [w[4]]
                    cur_y = w[1]
                else:
                    cur_line.append(w[4])
            lines.append(" ".join(cur_line))
            
            for line in lines:
                # Match title ... page_num
                m = re.search(r'^(.*?)\s+\.{3,}\s*(\d+)$', line)
                if not m:
                    # Alternative: Title at start, number at end
                    m = re.search(r'^([^\d]+)(\d+)$', line)
                    
                if m:
                    title = m.group(1).strip()
                    page_num = int(m.group(2))
                    if len(title) > 3:
                        all_entries.append({
                            "bookId": book_id,
                            "title": title,
                            "page": page_num,
                            "type": "story"
                        })
                elif "CHAPTER" in line.upper() or "PART" in line.upper():
                    all_entries.append({
                        "bookId": book_id,
                        "title": line.strip(),
                        "type": "header"
                    })
                    
    with open("toc_all_v6.json", "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=4)
    print(f"Extracted {len(all_entries)} TOC entries.")

if __name__ == "__main__":
    extract_tocs()
