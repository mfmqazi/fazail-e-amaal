import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
TOC_FILE = "toc_extracted.json"
OUTPUT_FILE = "fazail_data.js"

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

BOOK1_CHAPTERS = [
    {"id": 101, "title": "Steadfastness in the face of hardships", "arabic": "استقامت", "keywords": ["Steadfastness", "Hardships", "Chapter I"]},
    {"id": 102, "title": "Fear of Allah", "arabic": "خوفِ خدا", "keywords": ["Fear of Allah", "Chapter II", "Chapter 2"]},
    {"id": 103, "title": "Abstinence and Contentment", "arabic": "زہد و قناعت", "keywords": ["Abstinence", "Contentment", "Chapter III", "Chapter 3"]},
    {"id": 104, "title": "Piety and Scrupulousness", "arabic": "تقویٰ", "keywords": ["Piety", "Scrupulousness", "Chapter IV", "Chapter 4"]},
    {"id": 105, "title": "Devotion to Salaat", "arabic": "نماز", "keywords": ["Devotion to Salaat", "Chapter V", "Chapter 5"]},
    {"id": 106, "title": "Sympathy and Self-sacrifice", "arabic": "ہمدردی و ایثار", "keywords": ["Sympathy", "Self-sacrifice", "Chapter VI", "Chapter 6"]},
    {"id": 107, "title": "Valour and Heroism", "arabic": "بہادری", "keywords": ["Valour", "Heroism", "Chapter VII", "Chapter 7"]},
    {"id": 108, "title": "Zeal for Knowledge", "arabic": "علم کا شوق", "keywords": ["Zeal for Knowledge", "Chapter VIII", "Chapter 8"]},
    {"id": 109, "title": "Compliance with the Prophet", "arabic": "اطاعت", "keywords": ["Compliance", "Chapter IX", "Chapter 9"]},
    {"id": 110, "title": "Women's Love of Faith", "arabic": "خواتین کا جذبہ", "keywords": ["Women", "Faith", "Chapter X", "Chapter 10"]},
    {"id": 111, "title": "Children's Devotion to Islam", "arabic": "بچوں کا جذبہ", "keywords": ["Children", "Devotion", "Chapter XI", "Chapter 11"]},
    {"id": 112, "title": "Love for the Prophet", "arabic": "حبِ رسول", "keywords": ["Love for the Prophet", "Chapter XII", "Chapter 12"]},
    {"id": 113, "title": "Epilogue: Sahabah's Virtues", "arabic": "خاتمہ", "keywords": ["Epilogue", "Privileges"]}
]

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

def clean_title_for_search(title):
    # Remove digits, extra spaces, special chars
    # "Prophet's Journey to Taif" -> "Journey to Taif" (Substrings are safer)
    # Pick longest word > 5 chars? Or just first 2 words?
    words = [w for w in title.split() if len(w) > 3]
    if len(words) >= 2:
        return " ".join(words[:3])
    return title

def generate_final_v5():
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        toc_entries = json.load(f)
    doc = fitz.open(PDF_FILE)
    print("Linearizing PDF...")
    linear_pages = get_linear_text(doc)
    
    target = "Journey to Taif"
    offset = 4
    for i in range(min(50, len(linear_pages))):
        text = linear_pages[i].replace('\n', ' ')
        if target.upper() in text.upper() and ".........." not in linear_pages[i]:
             offset = i - 15
             break

    stories = []
    story_id = 1
    current_chapter_obj = BOOK1_CHAPTERS[0] 
    
    valid_entries = [e for e in toc_entries if e.get('page', 0) > 0]
    valid_entries.sort(key=lambda x: x['page'])
    
    used_books = set()
    
    for i, entry in enumerate(valid_entries):
        page_num = entry['page']
        book_id = 1
        for bid, meta in BOOKS_META.items():
            if meta['start'] <= page_num <= meta['end']:
                book_id = bid
                break
        
        if book_id == 1:
            title_text = entry['title']
            for ch in BOOK1_CHAPTERS:
                for kw in ch['keywords']:
                    if kw.upper() in title_text.upper():
                        current_chapter_obj = ch
                        break
        else:
             current_chapter_obj = {"title": BOOKS_META[book_id]['title'], "arabic": BOOKS_META[book_id]['arabic']}

        start_page = page_num
        end_page = start_page
        next_title_search = None
        
        if i + 1 < len(valid_entries):
            next_entry = valid_entries[i+1]
            if next_entry['page'] > start_page:
                end_page = next_entry['page']
                next_title_search = clean_title_for_search(next_entry['title'])
            elif next_entry['page'] == start_page: 
                 # Next story starts ON SAME PAGE
                 end_page = start_page
                 next_title_search = clean_title_for_search(next_entry['title'])
        else:
             end_page = BOOKS_META[book_id]['end']

        start_idx = max(0, start_page + offset)
        end_idx = max(0, end_page + offset)
        
        start_search_title = clean_title_for_search(entry['title'])

        # Logic:
        # 1. Extract Full Range first? Then slice?
        # Simpler: Iterate pages.
        # If Page == start_idx: Search START TITLE.
        # If Page == end_idx: Search NEXT TITLE.
        
        raw_text = ""
        try:
            # Bounds
            if end_idx > len(linear_pages): end_idx = len(linear_pages)
            if end_idx <= start_idx: end_idx = start_idx + 1
            if end_idx - start_idx > 10: end_idx = start_idx + 5

            for p in range(start_idx, end_idx):
                if p >= len(linear_pages): break
                page_content = linear_pages[p]
                
                # SLICING LOGIC
                # Start Slice
                if p == start_idx:
                    # Find Title
                    # PyMuPDF text is messy. Regex fuzzy match?
                    # "Prophet's Journey"
                    patterns = [re.escape(start_search_title), start_search_title[:10]] 
                    match_idx = -1
                    for pat in patterns:
                        m = re.search(pat, page_content, re.IGNORECASE)
                        if m:
                            match_idx = m.end() # Start text AFTER title
                            break
                    if match_idx != -1:
                        page_content = page_content[match_idx:] # Clip top
                
                # End Slice
                if p == end_idx - 1 and next_title_search:
                    # Find Next Title
                    patterns = [re.escape(next_title_search), next_title_search[:10]]
                    match_idx = -1
                    for pat in patterns:
                         m = re.search(pat, page_content, re.IGNORECASE)
                         if m:
                             match_idx = m.start() # End text BEFORE next title
                             break
                    if match_idx != -1:
                        page_content = page_content[:match_idx] # Clip bottom
                
                raw_text += page_content + "\n"
        except Exception as e:
            print(e)
            pass
        
        raw_text = re.sub(r'Page No:', '', raw_text)
        
        if len(raw_text) > 50:
            stories.append({
                "id": story_id,
                "bookId": book_id,
                "chapter": current_chapter_obj['title'],
                "chapter_arabic": current_chapter_obj.get('arabic', ''),
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
                "chapter_arabic": meta['arabic'],
                "title": "Full Content",
                "preview": raw_text[:150].replace('\n', ' ') + "...",
                "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
            })
            story_id += 1
            
    final_chapters = {}
    cid = 100
    for ch in BOOK1_CHAPTERS:
         final_chapters[(1, ch['title'])] = {"id": ch['id'], "bookId": 1, "title": ch['title'], "arabic": ch['arabic']}

    for s in stories:
        k = (s['bookId'], s['chapter'])
        if k not in final_chapters:
            new_id = len(final_chapters) + 101
            final_chapters[k] = {"id": new_id, "bookId": s['bookId'], "title": s['chapter'], "arabic": s.get("chapter_arabic", "")}

    js_data = {
        "books": [{"id": k, "title": v["title"], "arabic": v["arabic"], "description": v["description"]} for k,v in BOOKS_META.items()],
        "chapters": list(final_chapters.values()),
        "stories": stories
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const fazailData = {json.dumps(js_data, indent=4)};")
    print(f"Generated {len(stories)} stories.")

if __name__ == "__main__":
    generate_final_v5()
