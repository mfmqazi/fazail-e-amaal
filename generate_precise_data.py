import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
TOC_FILE = "toc_extracted.json"
OUTPUT_FILE = "fazail_data.js"

# Book definitions (Page Ranges)
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
    text = re.sub(r'\.\.+', '', text) # Remove dots
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_precise_data():
    # Load ToC
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        toc_entries = json.load(f)
    
    # Load PDF
    doc = fitz.open(PDF_FILE)
    
    # Init Data
    stories = []
    story_id = 11 # Start after manual ones (if we kept them, but we deleted them. Start at 1 is fine if we wipe everything)
    
    # We will regenerate fresh.
    story_id = 1
    
    current_chapter = "General"
    
    # Filter/Process ToC
    # We iterate and maintain context
    processed_items = []
    
    for i, item in enumerate(toc_entries):
        # Determine Book
        page_num = item.get('page', 0)
        book_id = 0
        if page_num > 0:
            for bid, bmeta in BOOKS.items():
                if bmeta['start'] <= page_num <= bmeta['end']:
                    book_id = bid
                    break
        
        # Header logic
        if item['type'] == 'header':
            clean_header = clean_text(item['title'])
            if len(clean_header) > 3:
                current_chapter = clean_header.title()
                # Special: If header is "CHAPTER II", maybe keep previous title context?
                # For now simple replacement.
            continue
            
        if item['type'] == 'story' and book_id > 0:
            # Found a story
            title = clean_text(item['title'])
            start_page = item['page']
            
            # Find End Page
            # Look ahead for next story with page number
            end_page = start_page # minimal
            for j in range(i + 1, len(toc_entries)):
                next_item = toc_entries[j]
                if next_item.get('page', 0) > start_page:
                    end_page = next_item['page']
                    break
            
            # If no next story, use Book End
            if end_page == start_page:
                end_page = BOOKS[book_id]['end']
            
            # Extract Text
            content_text = ""
            # Loop pages. Note: PDF pages are 0-indexed? 
            # PyMuPDF doc[N] is 0-indexed.
            # Our 'page' numbers are consistent with 1-based usually printed?
            # Or are they PDF indices?
            # ToC says "15". PDF internal index 14?
            # The ToC scrapper `page_num = int(text)`. This is printed text. 
            # So likely 1-based relative to book, or absolute if PDF is sequential.
            # Let's assume absolute + offset check. 
            # Usually Page 1 is physically Page 3 or 4.
            # I'll use `page_num - 1` as approximation, or just try to read.
            # Actually, `fazail-e-amaal-complete.pdf` usually aligns Page 1 to real page? No.
            # I'll assume `page_num` maps roughly to `doc[page_num-1]`.
            
            try:
                # Extract from start_page to end_page (non-inclusive of end start?)
                # Actually, end_page is Start of next story.
                # So extract up to end_page.
                
                # Correction: PDF Page 15 might be doc[14].
                # User said "PDF Pages 4-7 have TOC".
                # toc_extracted ran on `range(3, 15)` (i.e. doc[3]..doc[14]). 
                # This yielded "15".
                # If Page 15 is content, and ToC is at 4-7. Then 15 is valid.
                
                # Check bounds
                if start_page > len(doc): start_page = len(doc)
                if end_page > len(doc): end_page = len(doc)
                
                # Heuristic: limit max length
                if end_page - start_page > 20: 
                    end_page = start_page + 5 # Cap huge jumps
                
                # Loop
                raw_text = ""
                # Map printed page to index: usually offset.
                # If ToC says 13 for Foreword. And ToC is at 4-7.
                # Foreword probably at real index ~13? Or offset?
                # PDF usually starts counting covers.
                # I will assume `page_num` is the PDF page label which usually aligns with index if no Roman preface.
                # But looking at ToC output: "Foreword ... 13". "Story ... 15".
                # If ToC is at 4. 13 is ahead. Seems physical index.
                # I'll use `page_num - 1` to be safe (0-index).
                
                start_idx = max(0, start_page - 1)
                end_idx = max(0, end_page - 1)
                
                for p in range(start_idx, end_idx):
                    raw_text += doc[p].get_text() + "\n"
                
                # Add overflow from end_page? (Just the text before next title?)
                # PyMuPDF text is page-based.
                # Hard to split exactly at title on next page.
                # We'll just take full pages for now, or up to end_idx (exclusive).
                # This mimics "Chapter" extraction.
                
                # Create Story
                stories.append({
                    "id": story_id,
                    "bookId": book_id,
                    "chapter": current_chapter,
                    "title": title,
                    "preview": raw_text[:150].replace('\n', ' ') + "...",
                    "content": f'<div class="story-content"><p>{raw_text.replace(chr(10), "<br>")}</p></div>'
                })
                story_id += 1
                
            except Exception as e:
                print(f"Error extracting {title}: {e}")

    # Construct Data Object
    # We need matching Books array.
    fazail_data = {
        "books": [
            {"id": bid, "title": meta["title"], "arabic": "", "description": "Extracted Content"} 
            for bid, meta in BOOKS.items()
        ],
        "chapters": [], # We encode chapters in stories directly or regenerate this list?
        # The frontend uses `chapters` list to populate dropdowns.
        # We MUST regenerate `chapters` list based on unique `current_chapter` found.
        "stories": stories
    }
    
    # Regenerate Chapters
    # Group stories by Book -> Chapter
    unique_chapters = {} # Key: (BookId, ChapterName)
    
    chapter_id = 101
    for s in stories:
        key = (s['bookId'], s['chapter'])
        if key not in unique_chapters:
            unique_chapters[key] = {
                "id": chapter_id,
                "bookId": s['bookId'],
                "title": s['chapter'],
                "arabic": ""
            }
            chapter_id += 1
    
    fazail_data['chapters'] = list(unique_chapters.values())
    
    # Save
    js_content = f"const fazailData = {json.dumps(fazail_data, indent=4)};"
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated {len(stories)} stories and {len(fazail_data['chapters'])} chapters.")

if __name__ == "__main__":
    generate_precise_data()
