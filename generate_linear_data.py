import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
OUTPUT_FILE = "fazail_data.js"

# Book definitions (Page Ranges from metadata - useful for assigning ID)
# Update ranges to assume linearized approx if needed?
# Actually, we assign Book ID based on where the ToC entry falls or by title.
# We'll use the existing metadata ranges as a guide for mapping "Page Number" to Book.
BOOKS_META = {
    1: {"start": 3, "end": 130, "title": "Stories of Sahaabah"},
    2: {"start": 131, "end": 180, "title": "Virtues of Holy Qur'aan"},
    3: {"start": 181, "end": 260, "title": "Virtues of Salaat"},
    4: {"start": 261, "end": 320, "title": "Virtues of Zikr"},
    5: {"start": 321, "end": 370, "title": "Virtues of Tabligh"},
    6: {"start": 371, "end": 420, "title": "Virtues of Ramadhaan"},
    7: {"start": 421, "end": 440, "title": "Muslim Degeneration"},
    8: {"start": 441, "end": 452, "title": "Six Fundamentals"}
}

def get_linear_text(doc):
    print("Linearizing PDF (Splitting Spreads)...")
    linear_pages = []
    
    for p_num in range(len(doc)):
        page = doc[p_num]
        w, h = page.rect.width, page.rect.height
        
        # Left Half
        left_rect = fitz.Rect(0, 0, w/2, h)
        left_text = page.get_text(clip=left_rect)
        linear_pages.append(left_text)
        
        # Right Half
        right_rect = fitz.Rect(w/2, 0, w, h)
        right_text = page.get_text(clip=right_rect)
        linear_pages.append(right_text)
        
    return linear_pages

def parse_toc_linear(linear_pages):
    print("Scanning Linear ToC...")
    # ToC usually in first 20 logical pages
    entries = []
    
    # Heuristic: Scan pages 0-30
    toc_text = ""
    for i in range(min(30, len(linear_pages))):
        toc_text += linear_pages[i] + "\n"
        
    lines = toc_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Regex: Title ... Number
        # Or Title Number (if fuzzy)
        # Look for line ending in 1-3 digits
        match = re.search(r'^(.*?)[ .]+(\d{1,3})$', line)
        if match:
            title = match.group(1).strip(" .")
            page = int(match.group(2))
            
            # Filter noise
            if len(title) > 3 and page > 2:
                # Classify type
                etype = 'story'
                if "CHAPTER" in title.upper() or "PART" in title.upper():
                    etype = 'header'
                
                entries.append({"type": etype, "title": title, "page": page})
                
    return entries

def generate_linear_data():
    doc = fitz.open(PDF_FILE)
    
    # 1. Linearize
    linear_pages = get_linear_text(doc)
    print(f"Total Logical Pages: {len(linear_pages)}")
    
    # 2. Parse ToC
    extracted_entries = parse_toc_linear(linear_pages)
    print(f"Found {len(extracted_entries)} ToC entries.")
    
    # 3. Calculate Offset
    # Find "Prophet's Journey to Taif" (Page 15)
    target = "Journey to Taif"
    offset = 0
    found_idx = -1
    
    for i in range(min(50, len(linear_pages))):
        if target.upper() in linear_pages[i].upper():
            # Ensure not ToC page (check for dots or "CONTENTS")
            if ".........." not in linear_pages[i]:
                found_idx = i
                print(f"Found anchor '{target}' at Logical Page {i}")
                break
    
    if found_idx != -1:
        # Expected Page 15.
        # Logical Page i corresponds to Book Page 15.
        # Offset = i - 15.
        offset = found_idx - 15
        print(f"Calculated Offset: {offset}")
    else:
        print("Warning: Anchor not found. Using default Offset -4 (heuristic).")
        offset = -4
        
    # 4. Extract Stories
    stories = []
    story_id = 1
    current_chapter = "General"
    
    # Filter entries to unique sorted
    # Sometimes ToC has noise
    
    # Assign Book ID to entries
    # Use entries to modify global 'current_chapter'
    
    # Iterate entries
    for i, entry in enumerate(extracted_entries):
        page_num = entry['page']
        
        # Determine Book
        book_id = 1 # Default
        for bid, meta in BOOKS_META.items():
            if meta['start'] <= page_num <= meta['end']:
                book_id = bid
                break
                
        if entry['type'] == 'header':
            current_chapter = entry['title'].title()
            continue
            
        # It's a story
        title = entry['title']
        start_page = page_num
        
        # Find End Page
        end_page = start_page
        next_found = False
        for j in range(i + 1, len(extracted_entries)):
            next_entry = extracted_entries[j]
            if next_entry['page'] > start_page:
                end_page = next_entry['page']
                next_found = True
                break
        
        if not next_found:
             # Use Book End from meta
             end_page = BOOKS_META[book_id]['end']
             
        # Extract Content
        # Range: [start_page + offset, end_page + offset)
        start_idx = start_page + offset
        end_idx = end_page + offset
        
        # Clamp
        start_idx = max(0, start_idx)
        if end_idx > len(linear_pages): end_idx = len(linear_pages)
        if end_idx <= start_idx: end_idx = start_idx + 1 # At least one page
        
        # Retrieve text
        story_text = ""
        for p in range(start_idx, end_idx):
            story_text += linear_pages[p] + "\n"
            
        # Clean text
        story_text = re.sub(r'Page No:', '', story_text)
        story_text = re.sub(r'\d+$', '', story_text, flags=re.MULTILINE) # footer page nums
        story_text = story_text.replace('..........', '')
        
        if len(story_text) > 50:
             stories.append({
                 "id": story_id,
                 "bookId": book_id,
                 "chapter": current_chapter,
                 "title": title,
                 "preview": story_text[:150].replace('\n', ' ') + "...",
                 "content": f'<div class="story-content"><p>{story_text.replace(chr(10), "<br>")}</p></div>'
             })
             story_id += 1
             
    # 5. Fallback for Empty Books 5-8?
    # If ToC didn't cover them.
    # Check coverage
    covered_books = set(s['bookId'] for s in stories)
    print(f"Covered Books: {covered_books}")
    
    for bid, meta in BOOKS_META.items():
        if bid not in covered_books:
            print(f"Generating Fallback for Book {bid}")
            start_p = meta['start'] + offset
            end_p = meta['end'] + offset
            start_p = max(0, start_p)
            if end_p > len(linear_pages): end_p = len(linear_pages)
            
            raw_text = ""
            for p in range(start_p, end_p):
                raw_text += linear_pages[p] + "\n"
                
            # One generic story
            stories.append({
                 "id": story_id,
                 "bookId": bid,
                 "chapter": meta['title'],
                 "title": "Full Content",
                 "preview": raw_text[:150].replace('\n', ' ') + "...",
                 "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
            })
            story_id += 1

    # Regenerate Data
    # Collect unique chapters
    chapters_map = {}
    cid = 100
    for s in stories:
        k = (s['bookId'], s['chapter'])
        if k not in chapters_map:
            chapters_map[k] = {"id": cid, "bookId": s['bookId'], "title": s['chapter'], "arabic": ""}
            cid += 1
            
    js_data = {
        "books": [{"id": k, "title": v["title"], "arabic": "", "description": ""} for k,v in BOOKS_META.items()],
        "chapters": list(chapters_map.values()),
        "stories": stories
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const fazailData = {json.dumps(js_data, indent=4)};")
        
    print(f"Done. Generated {len(stories)} stories.")

if __name__ == "__main__":
    generate_linear_data()
