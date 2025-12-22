import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
OUTPUT_FILE = "fazail_data.js"

# Manually verified physical start pages (0-indexed)
# Book 1: Stories of Sahaabah -> Starts around page 4 (ToC), 21 (Intro)
# Book 2: Virtues of Quran -> Starts around 136
# Book 3: Virtues of Salaat -> Starts around 198
# Book 4: Virtues of Zikr -> Starts around 247
# Book 5: Virtues of Tabligh -> Starts around 370
# Book 6: Virtues of Ramadhaan -> Starts around 395
# Book 7: Muslim Degeneration -> Starts around 411
# Book 8: Six Fundamentals -> Starts around 431

BOOKS_META = {
    1: {"name": "STORIES OF THE SAHAABAH", "start": 1, "offset": 4, "icon": "📿", "arabic": "حکایاتِ صحابہ", "color": "#7c3aed"},
    2: {"name": "VIRTUES OF THE HOLY QUR", "start": 136, "offset": 121, "icon": "📖", "arabic": "فضائلِ قرآن", "color": "#0891b2"},
    3: {"name": "VIRTUES OF SALAAT", "start": 194, "offset": 187, "icon": "🕌", "arabic": "فضائلِ نماز", "color": "#059669"},
    4: {"name": "VIRTUES OF ZIKR", "start": 247, "offset": 241, "icon": "📿", "arabic": "فضائلِ ذکر", "color": "#db2777"},
    5: {"name": "VIRTUES OF TABLIGH", "start": 370, "offset": 357, "icon": "📢", "arabic": "فضائلِ تبلیغ", "color": "#ea580c"},
    6: {"name": "VIRTUES OF RAMADHAAN", "start": 395, "offset": 394, "icon": "🌙", "arabic": "فضائلِ رمضان", "color": "#1e40af"},
    7: {"name": "MUSLIM DEGENERATION", "start": 411, "offset": 410, "icon": "📉", "arabic": "مسلمانوں کی پستی", "color": "#4b5563"},
    8: {"name": "SIX FUNDAMENTALS", "start": 431, "offset": 430, "icon": "📜", "arabic": "چھ اصول", "color": "#b45309"}
}

def get_linear_pages(doc):
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        rect = page.rect
        w, h = rect.width, rect.height
        # Split landscape pages (2-up spreads)
        left = page.get_text("text", clip=fitz.Rect(0, 0, w/2, h))
        right = page.get_text("text", clip=fitz.Rect(w/2, 0, w, h))
        pages.append(left)
        pages.append(right)
    return pages

def generate_data():
    doc = fitz.open(PDF_FILE)
    print("Linearizing PDF...")
    linear_pages = get_linear_pages(doc)
    
    with open("toc_all_v6.json", "r", encoding="utf-8") as f:
        toc = json.load(f)
        
    stories = []
    chapters = []
    found_chapters = set()
    
    story_id = 1
    current_chapter = "General"
    
    for i, entry in enumerate(toc):
        if entry["type"] == "header":
            current_chapter = entry["title"]
            continue
            
        book_id = entry["bookId"]
        meta = BOOKS_META[book_id]
        logical_p = entry["page"]
        
        # Calculate start index
        start_idx = logical_p + meta["offset"]
        
        # Find next story to determine end page
        end_idx = start_idx + 1
        next_title = None
        for j in range(i + 1, len(toc)):
            if toc[j]["type"] == "story" and toc[j]["bookId"] == book_id:
                end_idx = toc[j]["page"] + meta["offset"]
                next_title = toc[j]["title"]
                break
        
        if end_idx <= start_idx: end_idx = start_idx + 1
        
        content = ""
        for p in range(start_idx, end_idx):
            if p < len(linear_pages):
                text = linear_pages[p]
                # If it's the last page of the story and there's a next story title, clip it
                if p == end_idx - 1 and next_title:
                    m = re.search(re.escape(next_title[:20]), text, re.I)
                    if m:
                        text = text[:m.start()]
                content += text + "\n"
        
        # Clean content
        content = re.sub(r'\d+\s+Ch\.\s+[IVX]+:.*', '', content) # Remove headers
        content = content.strip()
        
        if content:
            stories.append({
                "id": story_id,
                "bookId": book_id,
                "chapter": current_chapter,
                "title": entry["title"],
                "preview": content[:200] + "...",
                "content": content.replace("\n", "<br>")
            })
            
            chapter_key = (book_id, current_chapter)
            if chapter_key not in found_chapters:
                chapters.append({
                    "id": len(chapters) + 1,
                    "bookId": book_id,
                    "title": current_chapter,
                    "arabic": "" # Hardcoded mapping would go here
                })
                found_chapters.add(chapter_key)
            
            story_id += 1

    # Prepare final JS
    final_books = []
    for bid, meta in BOOKS_META.items():
        final_books.append({
            "id": bid,
            "title": meta["name"].title(),
            "arabic": meta["arabic"],
            "description": f"Exploring the virtues of {meta['name'].title()}",
            "icon": meta["icon"],
            "color": meta["color"]
        })
        
    js_content = f"const fazailData = {json.dumps({'books': final_books, 'chapters': chapters, 'stories': stories}, indent=4)};"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"Generated {len(stories)} stories across {len(final_books)} books.")

if __name__ == "__main__":
    generate_data()
