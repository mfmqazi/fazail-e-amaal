import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
TOC_FILE = "toc_extracted.json"
OUTPUT_FILE = "fazail_data.js"

# Restored Metadata with Arabic
BOOKS_META = {
    1: {"start": 3, "end": 130, "title": "Stories of Sahaabah", "arabic": "حکایاتِ صحابہ", "description": "Stories of the Companions"},
    2: {"start": 131, "end": 180, "title": "Virtues of Holy Qur'aan", "arabic": "فضائلِ قرآن", "description": "Rewards of Recitation"},
    3: {"start": 181, "end": 260, "title": "Virtues of Salaat", "arabic": "فضائلِ نماز", "description": "Importance of Prayer"},
    4: {"start": 261, "end": 320, "title": "Virtues of Zikr", "arabic": "فضائلِ ذکر", "description": "Remembrance of Allah"},
    5: {"start": 321, "end": 370, "title": "Virtues of Tabligh", "arabic": "فضائلِ تبلیغ", "description": "Invitation to Islam"},
    6: {"start": 371, "end": 420, "title": "Virtues of Ramadhaan", "arabic": "فضائلِ رمضان", "description": "Blessings of Fasting"},
    7: {"start": 421, "end": 440, "title": "Muslim Degeneration", "arabic": "مسلمانوں کی پستی", "description": "Causes of Decline"},
    8: {"start": 441, "end": 452, "title": "Six Fundamentals", "arabic": "چھ اصول", "description": "Core Principles"}
}

def get_linear_text(doc):
    linear_pages = []
    for p_num in range(len(doc)):
        page = doc[p_num]
        w, h = page.rect.width, page.rect.height
        left = page.get_text(clip=fitz.Rect(0, 0, w/2, h))
        right = page.get_text(clip=fitz.Rect(w/2, 0, w, h))
        linear_pages.append(left)
        linear_pages.append(right)
    return linear_pages

def generate_final_v3():
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        toc_entries = json.load(f)
        
    doc = fitz.open(PDF_FILE)
    print("Linearizing PDF...")
    linear_pages = get_linear_text(doc)
    
    # Calculate Offset (Same logic)
    target = "Journey to Taif"
    offset = 4
    for i in range(min(50, len(linear_pages))):
        text = linear_pages[i].replace('\n', ' ')
        if target.upper() in text.upper():
            if ".........." not in linear_pages[i] and not re.search(r'\.\s+\d+$', text):
                print(f"Found Anchors '{target}' at Logical Page {i}")
                offset = i - 15
                break

    stories = []
    story_id = 1
    current_chapter = "General"
    used_books = set()
    
    for i, entry in enumerate(toc_entries):
        page_num = entry.get('page', 0)
        
        # Book ID
        book_id = 1
        for bid, meta in BOOKS_META.items():
            if meta['start'] <= page_num <= meta['end']:
                book_id = bid
                break
        
        # Handle Headers Correctly
        # Only treat as Chapter Header if it contains specific keywords
        # Otherwise ignore (it's likely a title fragment)
        if entry.get('type') == 'header':
            clean = entry['title'].strip().upper()
            if "CHAPTER" in clean or "PART" in clean or "BOOK" in clean:
                current_chapter = entry['title'].strip().title()
                # Remove "Chapter Ii" -> "Chapter II" fix? cosmetic.
            # Else ignore
            continue
            
        start_page = page_num
        end_page = start_page
        
        # Lookahead
        for j in range(i + 1, len(toc_entries)):
            p = toc_entries[j].get('page', 0)
            if p > start_page:
                end_page = p
                break
                
        if end_page == start_page:
            end_page = BOOKS_META[book_id]['end']
            
        start_idx = max(0, start_page + offset)
        end_idx = max(0, end_page + offset)
        
        # Bounds logic
        if end_idx > len(linear_pages): end_idx = len(linear_pages)
        if end_idx <= start_idx: end_idx = start_idx + 1
        if end_idx - start_idx > 10: end_idx = start_idx + 5
        
        raw_text = ""
        try:
            for p in range(start_idx, end_idx):
                if p < len(linear_pages):
                    raw_text += linear_pages[p] + "\n"
        except: pass
        
        # Clean
        raw_text = re.sub(r'Page No:', '', raw_text)
        
        if len(raw_text) > 50:
            stories.append({
                "id": story_id,
                "bookId": book_id,
                "chapter": current_chapter,
                "title": entry['title'],
                "preview": raw_text[:150].replace('\n', ' ') + "...",
                "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
            })
            story_id += 1
            used_books.add(book_id)

    # Fallback
    for bid, meta in BOOKS_META.items():
        if bid not in used_books:
            print(f"Generating Fallback for Book {bid}")
            start_p = max(0, meta['start'] + offset)
            end_p = min(len(linear_pages), meta['end'] + offset)
            
            raw_text = ""
            try:
                for p in range(start_p, end_p):
                     if p < len(linear_pages):
                        raw_text += linear_pages[p] + "\n"
            except: pass
            
            stories.append({
                "id": story_id,
                "bookId": bid,
                "chapter": meta['title'],
                "title": "Full Content",
                "preview": raw_text[:150].replace('\n', ' ') + "...",
                "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
            })
            story_id += 1
            
    # Save
    chapters_map = {}
    cid = 100
    for s in stories:
        k = (s['bookId'], s['chapter'])
        if k not in chapters_map:
            chapters_map[k] = {"id": cid, "bookId": s['bookId'], "title": s['chapter'], "arabic": ""}
            cid += 1
            
    js_data = {
        "books": [{"id": k, "title": v["title"], "arabic": v["arabic"], "description": v["description"]} for k,v in BOOKS_META.items()],
        "chapters": list(chapters_map.values()),
        "stories": stories
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const fazailData = {json.dumps(js_data, indent=4)};")
    print(f"Generated {len(stories)} stories.")

if __name__ == "__main__":
    generate_final_v3()
