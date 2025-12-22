import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
OUTPUT_FILE = "fazail_data.js"

# Exact offsets calculated/verified
BOOKS_META = {
    1: {"name": "Stories of the Sahaabah", "offset": 4, "icon": "📿", "arabic": "حکایاتِ صحابہ", "color": "#7c3aed"},
    2: {"name": "Virtues of the Holy Qur'aan", "offset": 272, "icon": "📖", "arabic": "فضائلِ قرآن", "color": "#0891b2"},
    3: {"name": "Virtues of Salaat", "offset": 387, "icon": "🕌", "arabic": "فضائلِ نماز", "color": "#059669"},
    4: {"name": "Virtues of Zikr", "offset": 474, "icon": "📿", "arabic": "فضائلِ ذکر", "color": "#db2777"},
    5: {"name": "Virtues of Tabligh", "offset": 740, "icon": "📢", "arabic": "فضائلِ تبلیغ", "color": "#ea580c"},
    6: {"name": "Virtues of Ramadhaan", "offset": 791, "icon": "🌙", "arabic": "فضائلِ رمضان", "color": "#1e40af"},
    7: {"name": "Muslim Degeneration", "offset": 822, "icon": "📉", "arabic": "مسلمانوں کی پستی", "color": "#4b5563"},
    8: {"name": "Six Fundamentals", "offset": 864, "icon": "📜", "arabic": "چھ اصول", "color": "#b45309"}
}

def clean_title(title):
    # Remove leading/trailing dots and spaces
    t = title.strip(".")
    t = t.strip()
    # Remove common OCR artifacts like "IB 120" or "NO."
    t = re.sub(r'^(?:[IVX\d]+\s+|CHAPTER\s+[IVX\d]+\s+|PART\s+[IVX\d]+\s+)', '', t, flags=re.I)
    # Fix common typos
    t = re.sub(r'([a-z])gives', r'\1 gives', t, flags=re.I)
    t = re.sub(r'([a-z])and', r'\1 and', t, flags=re.I)
    t = t.strip()
    return t

CHAPTER_ARABIC = {
    "Steadfastness": "استقامت",
    "Fear of Allah": "خوفِ خدا",
    "Abstinence": "زہد و قناعت",
    "Piety": "تقویٰ",
    "Salaat": "نماز",
    "JAMAAT": "جماعت",
    "ZIKR": "ذکر",
    "TABLIGH": "تبلیغ",
}

def get_chapter_arabic(title):
    for key, arb in CHAPTER_ARABIC.items():
        if key.upper() in title.upper():
            return arb
    return ""

def get_linear_pages(doc):
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        rect = page.rect
        w, h = rect.width, rect.height
        left = page.get_text("text", clip=fitz.Rect(0, 0, w/2, h))
        right = page.get_text("text", clip=fitz.Rect(w/2, 0, w, h))
        pages.append(left)
        pages.append(right)
    return pages

def generate_v8():
    doc = fitz.open(PDF_FILE)
    print("Linearizing PDF...")
    linear_pages = get_linear_pages(doc)
    
    with open("toc_all_v6.json", "r", encoding="utf-8") as f:
        toc_data = json.load(f)
        
    stories = []
    chapters = []
    found_chapters = set()
    
    story_id = 1
    current_chapter = "General"
    
    # Filter TOC data: Remove entries that are just the book title or TOC itself
    filtered_toc = []
    for entry in toc_data:
        t = entry["title"].upper()
        # Skip entries that look like book titles (often found on TOC page 1)
        is_book_title = any(meta["name"].upper() in t for meta in BOOKS_META.values())
        if is_book_title and entry.get("page", 0) < 10:
            continue
        if "CONTENTS" in t or "INDEX" in t:
            continue
        filtered_toc.append(entry)

    for i, entry in enumerate(filtered_toc):
        if entry["type"] == "header":
            current_chapter = clean_title(entry["title"])
            if not current_chapter: current_chapter = "General"
            continue
            
        book_id = entry["bookId"]
        meta = BOOKS_META[book_id]
        logical_p = entry["page"]
        
        # Calculate start index
        start_idx = logical_p + meta["offset"]
        
        # End logic
        end_idx = start_idx + 1
        next_title = None
        for j in range(i + 1, len(filtered_toc)):
            if filtered_toc[j]["type"] == "story" and filtered_toc[j]["bookId"] == book_id:
                end_idx = filtered_toc[j]["page"] + meta["offset"]
                next_title = filtered_toc[j]["title"]
                break
        
        # Clamp range
        if end_idx <= start_idx: end_idx = start_idx + 2 # Allow at least 2 pages
        if end_idx - start_idx > 20: end_idx = start_idx + 10 # Safety break
        
        content = ""
        for p in range(start_idx, end_idx):
            if p < len(linear_pages):
                text = linear_pages[p]
                
                # Surgical split at next title
                if p == end_idx - 1 and next_title:
                    # Clean next title for search
                    nt_search = next_title[:15].strip(".")
                    m = re.search(re.escape(nt_search), text, re.I)
                    if m:
                        text = text[:m.start()]
                
                content += text + "\n"
        
        # Post-process content: Remove page headers and generic footers
        content = re.sub(r'\n\s*\d+\s*\n', '\n', content) # Remove standalone page numbers
        content = re.sub(r'.*?Stories of the Sahaabah.*?\n', '', content, flags=re.I)
        content = re.sub(r'.*?Virtues of .*?Qur.*?\n', '', content, flags=re.I)
        content = re.sub(r'.*?Virtues of Salaat.*?\n', '', content, flags=re.I)
        
        content = content.replace("\n", "<br>").strip()
        
        if len(content) > 50:
            title = clean_title(entry["title"])
            stories.append({
                "id": story_id,
                "bookId": book_id,
                "chapter": current_chapter,
                "title": title,
                "preview": re.sub(r'<br>', ' ', content)[:150] + "...",
                "content": content
            })
            
            chapter_key = (book_id, current_chapter)
            if chapter_key not in found_chapters:
                chapters.append({
                    "id": len(chapters) + 1,
                    "bookId": book_id,
                    "title": current_chapter,
                    "arabic": get_chapter_arabic(current_chapter)
                })
                found_chapters.add(chapter_key)
            
            story_id += 1

    # Book 7 & 8 Fallback (since TOC v6 missed them)
    for bid in [7, 8]:
        meta = BOOKS_META[bid]
        print(f"Generating fallback for {meta['name']}...")
        start = meta["offset"] + 1
        end = start + 40
        raw_text = ""
        for p in range(start, min(end, len(linear_pages))):
            raw_text += linear_pages[p] + "\n"
        
        content = raw_text.replace("\n", "<br>").strip()
        stories.append({
            "id": story_id,
            "bookId": bid,
            "chapter": "General",
            "title": "Full Section",
            "preview": meta["name"] + " content...",
            "content": content
        })
        story_id += 1

    # Final Output
    final_books = []
    for bid, meta in BOOKS_META.items():
        final_books.append({
            "id": bid,
            "title": meta["name"],
            "arabic": meta["arabic"],
            "description": f"Exploring the virtues of {meta['name']}",
            "icon": meta["icon"],
            "color": meta["color"]
        })
        
    js_content = f"const fazailData = {json.dumps({'books': final_books, 'chapters': chapters, 'stories': stories}, indent=4)};"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"Generated {len(stories)} stories.")

if __name__ == "__main__":
    generate_v8()
