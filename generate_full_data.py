import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
TOC_FILE = "toc_extracted.json"
OUTPUT_FILE = "fazail_data.js"

BOOKS = {
    1: {"title": "Stories of Sahaabah", "start": 3, "end": 130},
    2: {"title": "Virtues of Holy Qur'aan", "start": 131, "end": 180},
    3: {"title": "Virtues of Salaat", "start": 181, "end": 260},
    4: {"title": "Virtues of Zikr", "start": 261, "end": 320},
    5: {"title": "Virtues of Tabligh", "start": 321, "end": 370},
    6: {"title": "Virtues of Ramadhaan", "start": 371, "end": 420},
    7: {"title": "Muslim Degeneration", "start": 421, "end": 440},
    8: {"title": "Six Fundamentals", "start": 441, "end": 452},
}

def clean_text(text):
    text = re.sub(r'Page No:', '', text)
    text = re.sub(r'\.\.+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_full_data():
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        toc_entries = json.load(f)
    
    doc = fitz.open(PDF_FILE)
    stories = []
    current_chapter = "General"
    story_id = 1
    
    # 1. Process ToC (High Precision)
    for i, item in enumerate(toc_entries):
        page_num = item.get('page', 0)
        book_id = 0
        if page_num > 0:
            for bid, bmeta in BOOKS.items():
                if bmeta['start'] <= page_num <= bmeta['end']:
                    book_id = bid
                    break
        
        if item['type'] == 'header':
            clean = clean_text(item['title'])
            if len(clean) > 3: current_chapter = clean.title()
            continue
            
        if item['type'] == 'story' and book_id > 0:
            title = clean_text(item['title'])
            start_page = item['page']
            end_page = start_page
            for j in range(i + 1, len(toc_entries)):
                if toc_entries[j].get('page', 0) > start_page:
                    end_page = toc_entries[j]['page']
                    break
            if end_page == start_page: end_page = BOOKS[book_id]['end']
            
            # Extract
            raw_text = ""
            try:
                start_idx = max(0, start_page - 1)
                end_idx = max(0, end_page - 1)
                if end_idx > len(doc): end_idx = len(doc)
                
                if end_idx - start_idx > 20: end_idx = start_idx + 5
                
                for p in range(start_idx, end_idx):
                    raw_text += doc[p].get_text() + "\n"
                
                if len(raw_text) > 50:
                    stories.append({
                        "id": story_id,
                        "bookId": book_id,
                        "chapter": current_chapter,
                        "title": title,
                        "preview": raw_text[:150].replace('\n', ' ') + "...",
                        "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
                    })
                    story_id += 1
            except Exception as e: print(e)

    # 2. Fallback for Empty Books
    extracted_books = set(s['bookId'] for s in stories)
    print(f"ToC covered books: {extracted_books}")
    
    for bid, meta in BOOKS.items():
        if bid not in extracted_books:
            print(f"Generating Fallback content for Book {bid}: {meta['title']}")
            # Extract whole book range
            raw_text = ""
            start = meta['start'] - 1
            end = meta['end'] - 1
            if end > len(doc): end = len(doc)
            
            for p in range(start, end):
                raw_text += doc[p].get_text() + "\n"
            
            # Simple chunking
            # Split by "HADITH" or "PART" or generic Paragraphs?
            # To be safe, just one large story for now, OR split by double-newline if paragraphs are clean.
            # Splitting by "HADITH" is best for these books.
            
            splits = re.split(r'(HADITH|Hadith|No\.|Story)\s*[-.]?\s*\d+', raw_text)
            
            if len(splits) > 2:
                # Distribute
                chunk_id = 1
                for k in range(1, len(splits), 2):
                    header = splits[k] + " " + splits[k+1][:5].strip()
                    content = splits[k+1]
                    if len(content) > 100:
                        stories.append({
                            "id": story_id,
                            "bookId": bid,
                            "chapter": meta['title'], # Use Book Title as Chapter
                            "title": f"Selection {chunk_id}",
                            "preview": content[:150].replace('\n', ' ') + "...",
                            "content": f'<div class="story-content"><p>{content.replace(chr(10), "<br>")}</p></div>'
                        })
                        story_id += 1
                        chunk_id += 1
            else:
                # One big story
                stories.append({
                    "id": story_id,
                    "bookId": bid,
                    "chapter": meta['title'],
                    "title": "Full Content",
                    "preview": raw_text[:150].replace('\n', ' ') + "...",
                    "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
                })
                story_id += 1

    # Regenerate Struct
    final_chapters = {}
    cid = 100
    for s in stories:
        k = (s['bookId'], s['chapter'])
        if k not in final_chapters:
            final_chapters[k] = {"id": cid, "bookId": s['bookId'], "title": s['chapter'], "arabic": ""}
            cid += 1
            
    js_data = {
        "books": [{"id": k, "title": v["title"], "arabic": v.get("arabic",""), "description": ""} for k,v in BOOKS.items()],
        "chapters": list(final_chapters.values()),
        "stories": stories
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const fazailData = {json.dumps(js_data, indent=4)};")
    print(f"Total Stories: {len(stories)}")

if __name__ == "__main__":
    generate_full_data()
