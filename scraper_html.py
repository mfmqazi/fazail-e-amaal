"""
Enhanced Web Scraper - Preserves HTML structure and inline image positions
"""
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BOOKS_CONFIG = [
    {"id": 1, "title": "Stories of Sahaabah", "arabic": "حکایاتِ صحابہ", "icon": "📿", "color": "#7c3aed", "index": "part1.htm", "type": "standard"},
    {"id": 2, "title": "Virtues of Holy Qur'aan", "arabic": "فضائلِ قرآن", "icon": "📖", "color": "#0891b2", "index": "part2.htm", "type": "standard"},
    {"id": 3, "title": "Virtues of Salaat", "arabic": "فضائلِ نماز", "icon": "🕌", "color": "#059669", "index": "part3.htm", "type": "standard"},
    {"id": 4, "title": "Virtues of Zikr", "arabic": "فضائلِ ذکر", "icon": "📿", "color": "#db2777", "index": "part4.htm", "type": "standard"},
    {"id": 5, "title": "Virtues of Tabligh", "arabic": "فضائلِ تبلیغ", "icon": "📢", "color": "#ea580c", "index": "part5.htm", "type": "standard"},
    {"id": 6, "title": "Virtues of Ramadhan", "arabic": "فضائلِ رمضان", "icon": "🌙", "color": "#1e40af", "index": "part6.htm", "type": "standard"},
    {"id": 7, "title": "Muslim Degeneration", "arabic": "مسلمانوں کی زوال", "icon": "📉", "color": "#4b5563", "index": "part7.html", "type": "book7"},
    {"id": 8, "title": "Six Fundamentals", "arabic": "چھ نمبر", "icon": "📜", "color": "#b45309", "index": "six_fundamentals1.html", "type": "book8"}
]

BOOK7_TOC = [
    {"title": "Author's Preface", "url": "muslim_degeneration1.html", "chapter": "Introduction"},
    {"title": "The Diagnosis", "url": "muslim_degeneration4.html", "chapter": "The Problem"},
    {"title": "The Root-Cause", "url": "muslim_degeneration8.html", "chapter": "The Problem"},
    {"title": "Solution", "url": "muslim_degeneration14.html", "chapter": "The Solution"},
    {"title": "Procedure to Work", "url": "muslim_degeneration17.html", "chapter": "The Solution"},
    {"title": "General Principles", "url": "muslim_degeneration18.html", "chapter": "The Solution"},
    {"title": "Summary and Conclusion", "url": "muslim_degeneration19.html", "chapter": "Conclusion"},
    {"title": "Final Appeal", "url": "muslim_degeneration21.html", "chapter": "Conclusion"},
]

# Book 8 - Six Fundamentals - Manual TOC with all 6 lessons
BOOK8_TOC = [
    {"title": "First Lesson: Kalimah Tayyibah", "url": "six_fundamentals1.html", "chapter": "Six Fundamentals"},
    {"title": "Second Lesson: Salaat", "url": "six_fundamentals3.html", "chapter": "Six Fundamentals"},
    {"title": "Third Lesson: Knowledge and Zikr", "url": "six_fundamentals5.html", "chapter": "Six Fundamentals"},
    {"title": "Fourth Lesson: Honour for a Muslim", "url": "six_fundamentals7.html", "chapter": "Six Fundamentals"},
    {"title": "Fifth Lesson: Sincerity of Intention", "url": "six_fundamentals9.html", "chapter": "Six Fundamentals"},
    {"title": "Sixth Lesson: Dawat and Tabligh", "url": "six_fundamentals10.html", "chapter": "Six Fundamentals"},
]

# Images that don't exist (404 on server) - now all available locally
BROKEN_IMAGES = []  # Cleared - we created local versions of all missing images

# Images to exclude (decorative, social, etc.)
EXCLUDE_PATTERNS = ['fb.gif', 'gplus.gif', 'pinterest.gif', 'corner', 'footer', 'design', 
                    'masjid', 'fazaileamaal_2', 'islamicgem.com', 'quran-770', 'left_footer', 
                    'right_footer', '_corner_']

BASE_URL = "http://fazaileamaal.com/"

# Local image path mapping
LOCAL_IMAGES = {}

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

def load_local_images():
    """Load mapping of local images"""
    import os
    if os.path.exists("images/arabic"):
        for f in os.listdir("images/arabic"):
            # Create mapping from original filename to local path
            LOCAL_IMAGES[f.lower()] = f"images/arabic/{f}"
    print(f"Loaded {len(LOCAL_IMAGES)} local images")

def get_local_image_path(url):
    """Convert remote URL to local path if available"""
    filename = url.split('/')[-1].lower()
    # Handle URL encoding
    from urllib.parse import unquote
    filename = unquote(filename)
    safe_filename = re.sub(r'[^\w\-.]', '_', filename).lower()
    
    if filename in LOCAL_IMAGES:
        return LOCAL_IMAGES[filename]
    if safe_filename in LOCAL_IMAGES:
        return LOCAL_IMAGES[safe_filename]
    return url  # Keep remote URL if no local version

def should_include_image(src):
    """Check if image should be included"""
    src_lower = src.lower()
    
    # Must be a dua/arabic image
    is_dua = '/dua/' in src_lower or 'bismillah' in src_lower
    if not is_dua:
        return False
    
    # Check exclusions
    for pattern in EXCLUDE_PATTERNS + BROKEN_IMAGES:
        if pattern.lower() in src_lower:
            return False
    
    return True

def extract_toc_from_index(driver, book_id, index_url):
    print(f"Extracting TOC from {index_url}...")
    driver.get(index_url)
    time.sleep(2)
    
    js_code = """
    const results = [];
    let currentChapter = "";
    
    const allElements = document.querySelectorAll('body *');
    for (const el of allElements) {
        const text = el.innerText ? el.innerText.trim() : "";
        if (/^Chapter \\d+/i.test(text) && el.children.length === 0) {
            currentChapter = text;
        }
        if (el.tagName === 'A') {
            const href = el.getAttribute('href');
            if (href && /^\\d+.*\\.htm[l]?$/.test(href)) {
                results.push({
                    chapter: currentChapter,
                    title: text.replace(/\\s+/g, ' '),
                    url: href
                });
            }
        }
    }
    
    const uniqueResults = [];
    const urls = new Set();
    for (const r of results) {
        if (!urls.has(r.url)) {
            uniqueResults.push(r);
            urls.add(r.url);
        }
    }
    return JSON.stringify(uniqueResults);
    """
    
    toc_entries = []
    try:
        result = driver.execute_script(js_code)
        entries = json.loads(result)
        for entry in entries:
            entry['bookId'] = book_id
            entry['url'] = BASE_URL + entry['url'] if not entry['url'].startswith('http') else entry['url']
            toc_entries.append(entry)
    except Exception as e:
        print(f"Error extracting TOC: {e}")
    
    return toc_entries

def extract_story_html(driver, url):
    """Extract story content as HTML, preserving structure and image positions"""
    print(f"  Extracting content from {url}...")
    try:
        driver.get(url)
        time.sleep(1)
        
        # Extract the main content HTML - simpler approach
        html = driver.execute_script("""
            // Find the main content area - typically in a table cell
            const contentCells = document.querySelectorAll('td');
            let mainContent = null;
            let maxLength = 0;
            
            // Find the cell with most text content (likely the main content)
            for (const cell of contentCells) {
                const text = cell.innerText || '';
                if (text.length > maxLength && text.length > 500) {
                    maxLength = text.length;
                    mainContent = cell;
                }
            }
            
            if (!mainContent) {
                // Fallback to body
                mainContent = document.body;
            }
            
            return mainContent.innerHTML;
        """)
        
        # Get plain text for preview
        text = driver.execute_script("return document.body.innerText;")
        
        return html, text
    except Exception as e:
        print(f"  Error: {e}")
        return "", ""

def clean_html_content(html):
    """Clean HTML content while preserving structure and images"""
    if not html:
        return ""
    
    # Remove all anchor tags that point to other pages
    html = re.sub(r'<a[^>]*href=["\'][^"\']*\.htm[l]?["\'][^>]*>.*?</a>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove navigation text patterns
    html = re.sub(r'(?:<<\s*)?Previous(?:\s*>>)?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'(?:<<\s*)?Next(?:\s*>>)?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'\bIndex\b', '', html, flags=re.IGNORECASE)
    html = re.sub(r'&nbsp;>>', '', html)
    html = re.sub(r'<<&nbsp;', '', html)
    
    # Remove footer content
    html = re.sub(r'Stories of Sahabah.*?Virtues of Ramadhan', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'Home\s*\|\s*Contact Us.*?Sitemap', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'KEEP IN TOUCH AT:.*$', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove navigation rows at the end
    html = re.sub(r'<p[^>]*class="centertext"[^>]*>.*?</p>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<td[^>]*class="back"[^>]*>.*?</td>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Process images - replace with local paths or remove if excluded
    def process_img(match):
        img_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
        if not src_match:
            return ''
        
        src = src_match.group(1)
        
        # Check if should include
        if not should_include_image(src):
            return ''
        
        # Get local path
        local_src = get_local_image_path(src)
        
        # Add styling class
        new_img = f'<img src="{local_src}" class="arabic-img" alt="Arabic Text" />'
        return f'<div class="arabic-image-container">{new_img}</div>'
    
    html = re.sub(r'<img[^>]+>', process_img, html, flags=re.IGNORECASE)
    
    # Clean up empty elements and excessive whitespace
    html = re.sub(r'<(?:font|span)[^>]*>\s*</(?:font|span)>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<br\s*/?>\s*<br\s*/?>\s*<br\s*/?>', '<br><br>', html, flags=re.IGNORECASE)
    html = re.sub(r'<p[^>]*>\s*</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<tr[^>]*>\s*</tr>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<td[^>]*>\s*</td>', '', html, flags=re.IGNORECASE)
    
    # Wrap in container
    html = f'<div class="story-content">{html}</div>'
    
    return html

def clean_text(text):
    """Clean text for preview"""
    if not text:
        return ""
    
    text = re.sub(r'<<\s*Previous.*?Next\s*>>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'Previous\s+Index\s+Next', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Stories of Sahabah.*?Virtues of Ramadhan', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'Home\s*\|\s*Contact Us.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def extract_book8_lessons(driver):
    lessons = []
    for page_url in BOOK8_PAGES:
        full_url = BASE_URL + page_url
        print(f"  Checking {full_url} for lessons...")
        try:
            driver.get(full_url)
            time.sleep(1)
            content = driver.execute_script("return document.body.innerText;")
            lesson_matches = re.findall(
                r'(First|Second|Third|Fourth|Fifth|Sixth)\s+Lesson\s*[:\-]?\s*([^\n]+)',
                content, re.IGNORECASE
            )
            for ordinal, title in lesson_matches:
                lessons.append({
                    "title": f"{ordinal} Lesson: {title.strip()}",
                    "url": full_url,
                    "chapter": "Six Fundamentals"
                })
        except Exception as e:
            print(f"  Error: {e}")
    
    if not lessons:
        lesson_names = [
            ("First Lesson", "Kalimah Tayyibah"),
            ("Second Lesson", "Salaat"),
            ("Third Lesson", "Ilm and Zikr"),
            ("Fourth Lesson", "Ikraam-e-Muslim"),
            ("Fifth Lesson", "Ikhlaas-e-Niyyat"),
            ("Sixth Lesson", "Dawat and Tabligh"),
        ]
        for i, (name, topic) in enumerate(lesson_names):
            page_idx = min(i, len(BOOK8_PAGES) - 1)
            lessons.append({
                "title": f"{name}: {topic}",
                "url": BASE_URL + BOOK8_PAGES[page_idx],
                "chapter": "Six Fundamentals"
            })
    return lessons

def main():
    print("Starting HTML-preserving web scraper for fazaileamaal.com...")
    
    # Load local images
    load_local_images()
    
    driver = setup_driver()
    
    all_books = []
    all_chapters = []
    all_stories = []
    chapter_set = set()
    
    story_id = 1
    chapter_id = 1
    
    try:
        for book in BOOKS_CONFIG:
            print(f"\n=== Processing Book {book['id']}: {book['title']} ===")
            
            all_books.append({
                "id": book['id'],
                "title": book['title'],
                "arabic": book['arabic'],
                "description": f"Virtues and stories from {book['title']}",
                "icon": book['icon'],
                "color": book['color']
            })
            
            if book['type'] == 'book7':
                toc = [{'bookId': book['id'], 'chapter': e['chapter'], 'title': e['title'], 'url': BASE_URL + e['url']} for e in BOOK7_TOC]
                print(f"  Using predefined TOC with {len(toc)} entries")
            elif book['type'] == 'book8':
                toc = [{'bookId': book['id'], 'chapter': e['chapter'], 'title': e['title'], 'url': BASE_URL + e['url']} for e in BOOK8_TOC]
                print(f"  Using predefined TOC with {len(toc)} lessons")
            else:
                index_url = BASE_URL + book['index']
                toc = extract_toc_from_index(driver, book['id'], index_url)
                print(f"  Found {len(toc)} entries in TOC")
            
            for entry in toc:
                html, text = extract_story_html(driver, entry['url'])
                html = clean_html_content(html)
                text = clean_text(text)
                
                if html and len(text) > 100:
                    chapter_name = entry.get('chapter', 'General') or 'General'
                    
                    all_stories.append({
                        "id": story_id,
                        "bookId": book['id'],
                        "chapter": chapter_name,
                        "title": entry['title'],
                        "preview": text[:150] + "...",
                        "content": html
                    })
                    story_id += 1
                    
                    ckey = (book['id'], chapter_name)
                    if ckey not in chapter_set:
                        all_chapters.append({
                            "id": chapter_id,
                            "bookId": book['id'],
                            "title": chapter_name,
                            "arabic": ""
                        })
                        chapter_id += 1
                        chapter_set.add(ckey)
                
                time.sleep(0.5)
            
            print(f"  Extracted {len([s for s in all_stories if s['bookId'] == book['id']])} stories")
    
    finally:
        driver.quit()
    
    output_data = {
        "books": all_books,
        "chapters": all_chapters,
        "stories": all_stories
    }
    
    with open("fazail_data.js", "w", encoding="utf-8") as f:
        f.write(f"const fazailData = {json.dumps(output_data, indent=4, ensure_ascii=False)};")
    
    print(f"\n=== DONE ===")
    print(f"Generated {len(all_books)} books, {len(all_chapters)} chapters, {len(all_stories)} stories")

if __name__ == "__main__":
    main()
