"""
Extract Virtues of Holy Qur'an content from the PDF.
This script extracts the content for Book 2: Virtues of Holy Qur'an
and formats it for use in fazail_data.js
"""

import fitz
import json
import re

PDF_PATH = "fazail-e-amal-virtues-of-deeds.pdf"
OUTPUT_PATH = "quran_virtues_extracted.json"

# Page mapping discovery:
# - PDF Page 141: Foreword starts (book page 9)
# - PDF Page 145: Part I - Forty Ahadith starts (book page 16), Hadith 1 begins
# - PDF Page 146: Hadith 2 begins (book page 18)
# - So offset = PDF page - book page = 145 - 16 = 129

# Map of HADITH numbers to their PDF page numbers (discovered from scanning)
HADITH_PDF_PAGES = {
    1: 145,   # "The best amongst you is he who learns the Qur'an and teaches it"
    2: 146,   # Blessings of recitation
    3: 147,   # Rewards of two, three and four ayaat  
    4: 147,   
    5: 148,
    6: 148,
    7: 149,
    8: 150,
    9: 151,
    10: 153,
    11: 155,
    12: 156,
    13: 157,
    14: 157,
    15: 158,
    16: 158,
    17: 159,
    18: 159,
    19: 160,
    20: 160,
    21: 161,
    22: 162,
    23: 164,
    24: 165,
    25: 166,
    26: 168,
    27: 169,
    28: 170,
    29: 171,
    30: 172,
    31: 173,
    32: 175,
    33: 178,
    34: 180,
    35: 181,
    36: 181,
    37: 182,
    38: 182,
    39: 183,
    40: 184,
}

# Hadith titles from the TOC
HADITH_TITLES = {
    1: "The best among you is he who learns the Qur'an and teaches it",
    2: "Blessings of recitation and virtues of the Word of Allah",
    3: "Rewards of two, three and four ayaat",
    4: "Rewards for fluent recitation and for faltering recitation",
    5: "Two things for which jealousy is permissible",
    6: "Similitude of those who recite the Holy Qur'an and those who do not",
    7: "Rise and fall of nations by reason of the Holy Qur'an",
    8: "Three things shall be under Arsh of Allah on the Day of Judgement",
    9: "Elevated stage in Paradise by virtue of the Holy Qur'an",
    10: "A reward of ten virtues for every word of the Holy Qur'an",
    11: "Parents of one who recites the Holy Qur'an shall wear a crown more brilliant than the sun",
    12: "Fire does not burn the Holy Qur'an",
    13: "One who memorizes and acts upon the Holy Qur'an shall intercede for ten persons",
    14: "Similitude of one who learns and recites the Qur'an is like a bag full of musk",
    15: "A heart devoid of the Holy Qur'an is like a deserted house",
    16: "Recitation of the Holy Qur'an in Salaat is more virtuous",
    17: "The reward of reciting three ayaat in Salaat",
    18: "Rewards of visual recitation and recitation by memory",
    19: "Recitation of Qur'an cleans the rust of hearts",
    20: "The Holy Qur'an is the honour and distinction of Muslims",
    21: "Recitation of the Holy Qur'an is Nur in life and provision in the Hereafter",
    22: "Houses of recitation shine like the moon and stars for those in Heaven",
    23: "Descent of Sakinah and angels during Qur'an recitation",
    24: "Crowd of angels at the gathering for Qur'an recitation",
    25: "The Qur'an will intercede and its intercession will be accepted",
    26: "Reciter of the Qur'an is with the noble angels",
    27: "One who listens to the Qur'an gets abundant reward",
    28: "One hundred and twenty rewards for one ayat",
    29: "Reward for teaching one ayat",
    30: "Listening to the Qur'an absolves a hundred sins",
    31: "Surah Fatihah is a cure for all ailments",
    32: "Virtues of Ayatul Kursi",
    33: "Virtues of the last two ayaat of Surah Baqarah",
    34: "No interceder shall be better than the Holy Qur'an",
    35: "Protection afforded by the Qur'an in the grave",
    36: "One who reads the Holy Qur'an secures in his heart the knowledge of prophethood",
    37: "Punishment for one who reads the Holy Qur'an for worldly benefits alone",
    38: "Three persons shall be strolling on mounds of musk",
    39: "Learning of one ayat is more rewarding than hundred raka'at of Nafl Salaat",
    40: "The Book of Allah is protection against evil disorders",
}

def clean_text(text):
    """Clean up extracted text."""
    # Remove page headers
    text = re.sub(r'Virtues of the Holy Qur\'?an\s*\n', '', text)
    text = re.sub(r'Part I \(Hadith \d+\s*\)', '', text)
    text = re.sub(r'^\d+\s*\n', '', text, flags=re.MULTILINE)  # Page numbers at start of lines
    
    # Remove OCR artifacts
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    
    return text.strip()

def extract_hadith_content(doc, hadith_num, next_hadith_num=None):
    """Extract content for a single hadith from the PDF."""
    start_page = HADITH_PDF_PAGES[hadith_num] - 1  # 0-indexed
    
    if next_hadith_num and next_hadith_num in HADITH_PDF_PAGES:
        end_page = HADITH_PDF_PAGES[next_hadith_num]  # Include the page where next hadith starts
    else:
        end_page = start_page + 3  # Default to 3 pages for last entry
    
    content_parts = []
    for page_num in range(start_page, min(end_page, len(doc))):
        page_text = doc[page_num].get_text()
        content_parts.append(page_text)
    
    full_text = "\n".join(content_parts)
    
    # Try to extract just the relevant hadith content
    # Look for the start marker
    hadith_marker = f"HADITH-\\s*{hadith_num}\\b|HADITH\\s*-\\s*{hadith_num}\\b|HADITH\\s+{hadith_num}\\b|HADITH NO-\\s*{hadith_num}\\b"
    match = re.search(hadith_marker, full_text, re.IGNORECASE)
    
    if match:
        full_text = full_text[match.start():]
    
    # Look for the next hadith marker to trim the end (only if on different pages)
    if next_hadith_num and HADITH_PDF_PAGES.get(next_hadith_num, 0) > HADITH_PDF_PAGES[hadith_num]:
        next_marker = f"HADITH-\\s*{next_hadith_num}\\b|HADITH\\s*-\\s*{next_hadith_num}\\b|HADITH\\s+{next_hadith_num}\\b|HADITH NO-\\s*{next_hadith_num}\\b"
        next_match = re.search(next_marker, full_text, re.IGNORECASE)
        if next_match:
            full_text = full_text[:next_match.start()]
    elif next_hadith_num and HADITH_PDF_PAGES.get(next_hadith_num, 0) == HADITH_PDF_PAGES[hadith_num]:
        # Same page - find the next HADITH marker but include more content
        next_marker = f"HADITH-\\s*{next_hadith_num}\\b|HADITH\\s*-\\s*{next_hadith_num}\\b|HADITH\\s+{next_hadith_num}\\b|HADITH NO-\\s*{next_hadith_num}\\b"
        next_match = re.search(next_marker, full_text, re.IGNORECASE)
        if next_match:
            full_text = full_text[:next_match.start()]
    
    return clean_text(full_text)


def create_preview(content, max_length=150):
    """Create a preview from the content."""
    # Skip the HADITH-X header
    lines = content.split('\n')
    preview_text = ""
    
    for line in lines:
        line = line.strip()
        # Skip headers and short lines
        if line.startswith('HADITH') or len(line) < 30:
            continue
        # Skip lines that are mostly Arabic/special chars
        if len(re.sub(r'[a-zA-Z\s]', '', line)) > len(line) * 0.3:
            continue
        preview_text = line
        break
    
    if not preview_text:
        preview_text = content
    
    preview = preview_text[:max_length]
    if len(preview_text) > max_length:
        preview = preview.rsplit(' ', 1)[0] + '...'
    
    return preview

def format_as_html(content, title, hadith_num):
    """Format content as HTML for the story entry."""
    paragraphs = content.split('\n\n')
    html_parts = [
        f'<div class="story-content">',
        f'<h1>Virtues of the Holy Qur\'an</h1>',
        f'<h2>Hadith {hadith_num}: {title}</h2>'
    ]
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Skip the original hadith header
        if para.startswith('HADITH-') or para.startswith('HADITH -'):
            continue
        # Format quotes differently
        if para.startswith('"') or para.startswith("'"):
            html_parts.append(f'<blockquote>{para}</blockquote>')
        else:
            html_parts.append(f'<p>{para}</p>')
    
    html_parts.append('</div>')
    return ''.join(html_parts)

def main():
    print("Opening PDF...")
    doc = fitz.open(PDF_PATH)
    print(f"Total pages: {len(doc)}")
    
    stories = []
    story_id = 200  # Start with ID 200 for Qur'an virtues
    
    print("\nExtracting hadith content...")
    
    hadith_nums = sorted(HADITH_PDF_PAGES.keys())
    
    for i, hadith_num in enumerate(hadith_nums):
        next_hadith_num = hadith_nums[i + 1] if i + 1 < len(hadith_nums) else None
        title = HADITH_TITLES.get(hadith_num, f"Hadith {hadith_num}")
        
        print(f"  Extracting Hadith {hadith_num}: {title[:50]}...")
        
        content = extract_hadith_content(doc, hadith_num, next_hadith_num)
        preview = create_preview(content)
        html_content = format_as_html(content, title, hadith_num)
        
        story = {
            "id": story_id,
            "bookId": 2,
            "chapter": "Part 1: Forty Ahadith",
            "title": f"Hadith {hadith_num}: {title}",
            "preview": preview,
            "content": html_content
        }
        
        stories.append(story)
        story_id += 1
    
    # Also add the Foreword as a story
    print("  Extracting Foreword...")
    foreword_text = ""
    for page_num in range(140, 145):  # Pages 141-145 contain foreword
        foreword_text += doc[page_num].get_text() + "\n"
    
    foreword_text = clean_text(foreword_text)
    foreword_preview = create_preview(foreword_text)
    
    foreword_story = {
        "id": story_id,
        "bookId": 2,
        "chapter": "Introduction",
        "title": "Foreword - Virtues of the Holy Qur'an",
        "preview": foreword_preview,
        "content": format_as_html(foreword_text, "Foreword", "")
    }
    stories.insert(0, foreword_story)
    
    # Save extracted content
    print(f"\nSaving {len(stories)} stories to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({"stories": stories}, f, indent=2, ensure_ascii=False)
    
    print("Done!")
    
    # Print samples
    print("\n=== Sample Stories ===")
    for story in stories[:3]:
        print(f"\nTitle: {story['title']}")
        print(f"Preview: {story['preview'][:100]}...")
        print(f"Content length: {len(story['content'])} chars")

if __name__ == "__main__":
    main()
