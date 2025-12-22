import fitz
import json
import re

PDF_FILE = "fazail-e-amal-virtues-of-deeds.pdf"
MAP_FILE = "master_logical_map.json"
OUTPUT_FILE = "fazail_data.js"

# Book Metadata
BOOKS = [
    {"id": 1, "title": "Stories of the Sahaabah", "arabic": "حکایاتِ صحابہ", "icon": "📿", "color": "#7c3aed", "desc": "Inspiring stories of the companions of the Prophet"},
    {"id": 2, "title": "Virtues of the Holy Qur'aan", "arabic": "فضائلِ قرآن", "icon": "📖", "color": "#0891b2", "desc": "The importance and rewards of reciting the Holy Quran"},
    {"id": 3, "title": "Virtues of Salaat", "arabic": "فضائلِ نماز", "icon": "🕌", "color": "#059669", "desc": "The significance and blessings of daily prayers"},
    {"id": 4, "title": "Virtues of Zikr", "arabic": "فضائلِ ذکر", "icon": "📿", "color": "#db2777", "desc": "The benefits of remembrance of Allah"},
    {"id": 5, "title": "Virtues of Tabligh", "arabic": "فضائلِ تبلیغ", "icon": "📢", "color": "#ea580c", "desc": "The duty of invitation to Islam"},
    {"id": 6, "title": "Virtues of Ramadhaan", "arabic": "فضائلِ رمضان", "icon": "🌙", "color": "#1e40af", "desc": "Blessings of the holy month of fasting"},
    {"id": 7, "title": "Muslim Degeneration", "arabic": "مسلمانوں کی پستی", "icon": "📉", "color": "#4b5563", "desc": "Causes of the decline of the Muslim Ummah"},
    {"id": 8, "title": "Six Fundamentals", "arabic": "چھ اصول", "icon": "📜", "color": "#b45309", "desc": "The core six principles of the Tabligh effort"}
]

def clean_text(text):
    # Remove obvious headers/footers based on known strings
    text = re.sub(r'^\s*\d+\s*\n', '', text)
    text = re.sub(r'^\s*Stories of the Sahaabah\s*\n', '', text, flags=re.I)
    text = re.sub(r'^\s*Virtues of .*?\n', '', text, flags=re.I)
    text = re.sub(r'^\s*Muslim Degeneration.*?\n', '', text, flags=re.I)
    return text.strip()

def generate_v10():
    with open(MAP_FILE, 'r') as f:
        page_map = json.load(f)
    
    doc = fitz.open(PDF_FILE)
    
    final_stories = []
    final_chapters = []
    chapter_set = set()
    story_id = 1
    
    # We use toc_all_v6.json as a base for story boundaries
    with open("toc_all_v6.json", "r", encoding="utf-8") as f:
        toc = json.load(f)
        
    # Re-assemble the linear text for each book using the map
    book_streams = {} # book_id -> list of logical pages
    for bid in range(1, 9):
        stream = []
        # Support up to 300 logical pages per book
        for pnum in range(1, 301):
            key = f"{bid}|{pnum}"
            if key in page_map:
                map_data = page_map[key]
                p_idx = map_data["p"]
                q_name = map_data["q"]
                page = doc[p_idx]
                w, h = page.rect.width, page.rect.height
                quads = {
                    "LT": fitz.Rect(0, 0, w/2, h/2),
                    "RT": fitz.Rect(w/2, 0, w, h/2),
                    "LB": fitz.Rect(0, h/2, w/2, h),
                    "RB": fitz.Rect(w/2, h/2, w, h)
                }
                text = page.get_text("text", clip=quads[q_name])
                stream.append({"num": pnum, "text": clean_text(text)})
        book_streams[bid] = stream

    # Process TOC using the linear streams
    current_chapter = "General"
    
    for i, entry in enumerate(toc):
        if entry["type"] == "header":
            current_chapter = re.sub(r'^[IVX\d\.\s]+', '', entry["title"]).strip()
            continue
            
        bid = entry["bookId"]
        start_p = entry["page"]
        title = entry["title"]
        # Find next story page
        end_p = start_p + 2
        next_title = None
        for j in range(i + 1, len(toc)):
            if toc[j]["type"] == "story" and toc[j]["bookId"] == bid:
                end_p = toc[j]["page"]
                next_title = toc[j]["title"]
                break
        
        # Extract text from stream
        if bid not in book_streams: continue
        stream = book_streams[bid]
        
        story_text = ""
        for p_data in stream:
            if start_p <= p_data["num"] < end_p:
                story_text += p_data["text"] + "\n\n"
        
        if not story_text.strip():
             # Fallback: if precisely one page
             for p_data in stream:
                 if p_data["num"] == start_p:
                     story_text = p_data["text"]
                     break
        
        if len(story_text) > 50:
            final_stories.append({
                "id": story_id,
                "bookId": bid,
                "chapter": current_chapter,
                "title": title,
                "preview": story_text[:150].replace('\n', ' ') + "...",
                "content": story_text.replace('\n', '<br>')
            })
            story_id += 1
            
            ckey = (bid, current_chapter)
            if ckey not in chapter_set:
                final_chapters.append({
                    "id": len(final_chapters) + 1,
                    "bookId": bid,
                    "title": current_chapter,
                    "arabic": "" # Hardcoding can be added
                })
                chapter_set.add(ckey)

    # Format the data
    output_data = {
        "books": [
            {"id": b["id"], "title": b["title"], "arabic": b["arabic"], "description": b["desc"], "icon": b["icon"], "color": b["color"]}
            for b in BOOKS
        ],
        "chapters": final_chapters,
        "stories": final_stories
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"const fazailData = {json.dumps(output_data, indent=4)};")
    
    print(f"Generated {len(final_stories)} stories.")

if __name__ == "__main__":
    generate_v10()
