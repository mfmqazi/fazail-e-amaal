import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
TOC_FILE = "toc_all_v6.json"
OUTPUT_FILE = "fazail_data.js"

# Physical PDF Index Ranges
BOOKS_META = {
    1: {"start": 21, "end": 135, "title": "Stories of Sahaabah", "arabic": "حکایاتِ صحابہ", "description": "Stories of the Companions", "icon": "📿", "color": "#7c3aed"},
    2: {"start": 136, "end": 193, "title": "Virtues of Holy Qur'aan", "arabic": "فضائلِ قرآن", "description": "Rewards of Recitation", "icon": "📖", "color": "#0891b2"},
    3: {"start": 194, "end": 246, "title": "Virtues of Salaat", "arabic": "فضائلِ نماز", "description": "Importance of Prayer", "icon": "🕌", "color": "#059669"},
    4: {"start": 247, "end": 369, "title": "Virtues of Zikr", "arabic": "فضائلِ ذکر", "description": "Remembrance of Allah", "icon": "📿", "color": "#db2777"},
    5: {"start": 370, "end": 394, "title": "Virtues of Tabligh", "arabic": "فضائلِ تبلیغ", "description": "Invitation to Islam", "icon": "📢", "color": "#ea580c"},
    6: {"start": 395, "end": 410, "title": "Virtues of Ramadhaan", "arabic": "فضائلِ رمضان", "description": "Blessings of Fasting", "icon": "🌙", "color": "#1e40af"},
    7: {"start": 411, "end": 430, "title": "Muslim Degeneration", "arabic": "مسلمانوں کی پستی", "description": "Causes of Decline", "icon": "📉", "color": "#4b5563"},
    8: {"start": 431, "end": 451, "title": "Six Fundamentals", "arabic": "چھ اصول", "description": "Core Principles", "icon": "📜", "color": "#b45309"}
}

# Mapping English to Arabic for Chapter Dropdown (Book 1)
BOOK1_CHAPTERS_ARABIC = {
    "STEADFASTNESS": "استقامت",
    "FEAR OF ALLAH": "خوفِ خدا",
    "ABSTINENCE": "زہد و قناعت",
    "PIETY": "تقویٰ",
    "DEVOTION": "نماز",
    "SYMPATHY": "ہمدردی و ایثار",
    "VALOUR": "بہادری",
    "ZEAL FOR KNOWLEDGE": "علم کا شوق",
    "COMPLIANCE": "اطاعت",
    "WOMEN": "خواتین کا جذبہ",
    "CHILDREN": "بچوں کا جذبہ",
    "LOVE": "حبِ رسول",
    "EPILOGUE": "خاتمہ"
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

def clean_title(title):
    return re.sub(r'[^a-zA-Z\s]', '', title).strip().upper()

def generate_final_v6():
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        toc_entries = json.load(f)
        
    doc = fitz.open(PDF_FILE)
    print("Linearizing PDF...")
    linear_pages = get_linear_text(doc)
    
    # Calculate Offsets for each book
    # Book 1: Journey to Taif (p15)
    # Book 2: Use Foreword (p17)
    # Book 3: Use Foreword (p12?)
    offsets = {1: 4, 2: 121, 3: 187, 4: 241, 5: 350, 6: 395, 7: 411, 8: 431} # Basic guestimates, will refine
    
    # Refining offsets dynamically
    anchors = {
        1: ("Journey to Taif", 15),
        2: ("Who is the best person", 17),
        3: ("THE REWARDS OF SALAAT", 12),
        4: ("VIRTUES OF ZIKR", 12)
    }
    
    for book_id, (text_anchor, logical_p) in anchors.items():
        start_search = BOOKS_META[book_id]['start'] * 2
        for i in range(start_search, start_search + 40):
            if i < len(linear_pages) and text_anchor.upper() in linear_pages[i].upper():
                offsets[book_id] = i - logical_p
                print(f"Book {book_id} offset: {offsets[book_id]} (Found at logical {i})")
                break

    stories = []
    chapters_map = {}
    story_id = 1
    
    # Process TOC entries
    for i, entry in enumerate(toc_entries):
        if entry['type'] == 'header': continue
        
        book_id = entry['bookId']
        offset = offsets.get(book_id, 0)
        start_page = entry['page']
        
        # Determine Current Chapter
        current_chapter = "General"
        # Search backwards for nearest header
        for j in range(i, -1, -1):
            if toc_entries[j]['type'] == 'header' and toc_entries[j]['bookId'] == book_id:
                current_chapter = toc_entries[j]['title']
                break
        
        # Clean chapter title
        chapter_clean = re.sub(r'^CHAPTER\s+[IVX\d]+[:\.\s]*', '', current_chapter, flags=re.I).strip()
        if not chapter_clean: chapter_clean = "General"
        
        # Chapter Arabic
        chapter_arabic = ""
        for key, arb in BOOK1_CHAPTERS_ARABIC.items():
            if key in chapter_clean.upper():
                chapter_arabic = arb
                break
        
        # End Page logic
        end_page = start_page
        next_title = None
        for j in range(i + 1, len(toc_entries)):
            if toc_entries[j]['type'] == 'story' and toc_entries[j]['bookId'] == book_id:
                end_page = toc_entries[j]['page']
                next_title = toc_entries[j]['title']
                break
        
        if end_page == start_page:
            end_page = start_page + 5 # Default limit
            
        start_idx = start_page + offset
        end_idx = end_page + offset
        
        # Bounds check
        if end_idx > len(linear_pages): end_idx = len(linear_pages)
        if end_idx <= start_idx: end_idx = start_idx + 1
        
        raw_text = ""
        # SURGICAL SPLIT
        for p in range(start_idx, end_idx):
            if p >= len(linear_pages): break
            content = linear_pages[p]
            
            # If start page, clip before title? (Maybe not needed if we want title)
            # If end page and next title exists, clip at next title
            if p == end_idx - 1 and next_title:
                # Search for next title on last page
                # Use a simplified search string for reliability
                search_term = next_title[:15].strip()
                if search_term.upper() in content.upper():
                    split_idx = content.upper().find(search_term.upper())
                    content = content[:split_idx]
            
            raw_text += content + "\n"
        
        # Cleanup page headers/noise
        raw_text = re.sub(r'\d+\s+Ch\.\s+[IVX]+:.*?\n', '', raw_text)
        raw_text = re.sub(r'\n\s*\d+\s*\n', '\n', raw_text)
        
        if len(raw_text.strip()) > 50:
            stories.append({
                "id": story_id,
                "bookId": book_id,
                "chapter": chapter_clean,
                "title": entry['title'],
                "preview": raw_text[:150].strip().replace('\n', ' ') + "...",
                "content": f'<div class="story-content"><p>{raw_text.strip().replace(chr(10), "<br>")}</p></div>'
            })
            
            # Map chapter
            ckey = (book_id, chapter_clean)
            if ckey not in chapters_map:
                chapters_map[ckey] = {
                    "id": 1000 + len(chapters_map),
                    "bookId": book_id,
                    "title": chapter_clean,
                    "arabic": chapter_arabic
                }
            story_id += 1

    # Format JSON
    js_data = {
        "books": [
            {"id": bid, "title": meta["title"], "arabic": meta["arabic"], "description": meta["description"], "icon": meta["icon"], "color": meta["color"]}
            for bid, meta in BOOKS_META.items()
        ],
        "chapters": list(chapters_map.values()),
        "stories": stories
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const fazailData = {json.dumps(js_data, indent=4)};")
    print(f"Generated {len(stories)} stories.")

if __name__ == "__main__":
    generate_final_v6()
