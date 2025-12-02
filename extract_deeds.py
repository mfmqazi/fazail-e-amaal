import json
import re
import os
import fitz # PyMuPDF

def is_garbage(text):
    text = text.strip()
    if len(text) < 3:
        return False
        
    # Ignore numbers like (1), 1., 123
    if re.match(r'^[\(\[]?\d+[\)\]]?\.?$', text):
        return False
    
    # Check for specific garbage patterns or high non-alnum ratio
    # Added ~ and ` to the list, and check for them anywhere
    if re.search(r'[&@#$%\^&*/\\]{3,}', text) or re.search(r'[~`]', text):
        return True
        
    # Check for high density of punctuation/symbols
    if sum(1 for c in text if c in "&@#$%^*/\\") > 1:
        return True

    non_alnum = re.sub(r'[a-zA-Z0-9\s\.,;:\'\"-]', '', text)
    if len(text) > 0 and len(non_alnum) / len(text) > 0.4:
        return True
        
    return False

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return None

    output_dir = "arabic_clips"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    full_text = ""
    clip_count = 0
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        page_text = ""
        
        # Do not sort blocks manually; rely on fitz default order (usually better for reading order if not columnar-interleaved by y-coord)
        # blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))

        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    spans = line["spans"]
                    i = 0
                    while i < len(spans):
                        span = spans[i]
                        text = span["text"]
                        
                        if is_garbage(text):
                            # Look ahead for more garbage in this line to merge
                            garbage_spans = [span]
                            j = i + 1
                            while j < len(spans) and is_garbage(spans[j]["text"]):
                                garbage_spans.append(spans[j])
                                j += 1
                            
                            # Compute union bbox
                            x0 = min(s["bbox"][0] for s in garbage_spans)
                            y0 = min(s["bbox"][1] for s in garbage_spans)
                            x1 = max(s["bbox"][2] for s in garbage_spans)
                            y1 = max(s["bbox"][3] for s in garbage_spans)
                            
                            bbox = fitz.Rect(x0, y0, x1, y1)
                            
                            # Add generous padding to avoid clipping calligraphy
                            bbox.x0 -= 5
                            bbox.y0 -= 15  # Increased vertical padding
                            bbox.x1 += 5
                            bbox.y1 += 15  # Increased vertical padding
                            
                            pix = page.get_pixmap(clip=bbox, dpi=300)
                            filename = f"arabic_clip_{page_num+1}_{clip_count}.png"
                            pix.save(os.path.join(output_dir, filename))
                            
                            # Append image tag to text
                            page_text += f' <img src="{output_dir}/{filename}" class="arabic-text" alt="Arabic Text" /> '
                            clip_count += 1
                            
                            i = j # Skip processed spans
                        else:
                            # Debug print for suspicious but accepted text
                            if any(c in text for c in "~&+$<>^"):
                                print(f"DEBUG: Text kept (not garbage): {text!r}")
                            page_text += text + " "
                            i += 1
                    page_text += "\n"
            page_text += "\n"
        full_text += page_text
        
    return full_text

def load_deeds_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the array content
    match = re.search(r'const deeds = \[(.*?)\];', content, re.DOTALL)
    if not match:
        print("Could not find deeds array")
        return []
    
    array_content = match.group(1)
    deeds = []
    objects = array_content.split('},')
    
    for obj in objects:
        obj = obj.strip()
        if not obj:
            continue
            
        id_match = re.search(r'id:\s*(\d+)', obj)
        title_match = re.search(r'title:\s*"(.*?)"', obj)
        
        if id_match and title_match:
            deeds.append({
                "id": int(id_match.group(1)),
                "title": title_match.group(1).strip(),
                "content": "" # Placeholder
            })
    return deeds

def find_deed_content(full_text, deeds):
    # We will search for headers based on ID.
    # Patterns observed: "(1) TITLE", "2. TITLE", "(53) TITLE"
    # We'll look for these patterns at the start of lines.
    
    # Sort deeds by ID just in case
    deeds.sort(key=lambda x: x['id'])
    
    deed_indices = []
    
    # Overrides for IDs that are labeled differently in PDF
    ID_OVERRIDES = {
        37: 31, # Labeled as (31) in PDF body
        47: 41, # Labeled as (41) in PDF body
        79: 19, # data.js 79 (Morsel) -> PDF 19 (typo for 79)
    }
    
    # Overrides for Regex patterns for specific IDs (original ID)
    REGEX_OVERRIDES = {
        1: r'(?:^|\n)\s*\(1\)\s+GOOD', # Deed 1 override
        2: r'(?:^|\n)\s*2\.\s+PRAYING', # Deed 2 uses "2. PRAYING"
        21: r'(?:^|\n)\s*(?:Tenderness\s+towards\s+others|\(21\))', # Missing header
        51: r'(?:\(511|511\.)', # Typo in PDF, appears mid-line
        68: r'(?:^|\n).*?\(68\)', # Loose match for 68 (has noise before it), non-greedy
        71: r'(?:^|\n).*?(?:Six\s+Good\s+Deeds|SIX\s+GOOD\s+DEEDS|\(71\))', # Weird label, loose match
        79: r'(?:^|\n)\s*(?:\(19\)|19\.)\s+CLEANING' # Second (19)
    }
    
    current_pos = 0
    
    for deed in deeds:
        deed_id = deed['id']
        
        # Determine search ID
        search_id = ID_OVERRIDES.get(deed_id, deed_id)
        
        # Determine pattern
        if deed_id in REGEX_OVERRIDES:
            pattern = REGEX_OVERRIDES[deed_id]
        else:
            # Default pattern: (ID) followed by whitespace AND an uppercase letter (start of title)
            # We REMOVED 'ID.' because it matches list items (e.g. 1., 3., 4.) inside other deeds.
            # We use (?=[A-Z]) to ensure it's a title (most titles start with uppercase).
            pattern = r'(?:^|\n)\s*\(' + str(search_id) + r'\)\s+(?=[A-Z])'
            
        match = re.search(pattern, full_text[current_pos:])
        
        if match:
            start_index = current_pos + match.start()
            # For overrides that might match loose text, we want the start of the match
            # For standard IDs, match.start() includes the newline/start
            
            # Adjust start index to skip the newline if it matched
            if full_text[start_index] == '\n':
                start_index += 1
                
            deed_indices.append((deed_id, start_index))
            print(f"Found start of deed {deed_id} (Search ID: {search_id}) at index {start_index}. Match: {match.group().strip()}")
            current_pos = start_index + 1 # Advance slightly to avoid re-matching same spot
        else:
            # If mapped ID failed, maybe try original ID?
            if search_id != deed_id:
                 id_pattern_orig = r'(?:^|\n)\s*(?:(' + str(deed_id) + r')|' + str(deed_id) + r'\.)\s+(?=[A-Z])'
                 match_orig = re.search(id_pattern_orig, full_text[current_pos:])
                 if match_orig:
                     start_index = current_pos + match_orig.start()
                     if full_text[start_index] == '\n':
                        start_index += 1
                     deed_indices.append((deed_id, start_index))
                     print(f"Found start of deed {deed_id} (Original ID) at index {start_index}. Match: {match_orig.group().strip()}")
                     current_pos = start_index + 1
                     continue

            print(f"Warning: Could not find start of deed {deed_id} (Search ID: {search_id})")
            print(f"Context at current_pos ({current_pos}): {full_text[current_pos:current_pos+100]!r}")
            
    # Now extract content
    final_deeds = []
    for i in range(len(deed_indices)):
        deed_id, start_index = deed_indices[i]
        
        if i < len(deed_indices) - 1:
            end_index = deed_indices[i+1][1]
        else:
            end_index = len(full_text)
            
        content = full_text[start_index:end_index].strip()
        
        # Clean up the content
        lines = content.split('\n')
        
        # Remove lines that are just the ID and Title (existing logic)
        search_id = ID_OVERRIDES.get(deed_id, deed_id)
        if lines:
            first_line = lines[0]
            if str(search_id) in first_line or str(deed_id) in first_line or (deed_id == 21 and "Tenderness" in first_line):
                if deed_id != 21:
                    lines.pop(0)
        
        # Filter out page numbers (lines that are just digits)
        cleaned_lines = []
        for line in lines:
            # Check if line is just a number (page number)
            if re.match(r'^\s*\d+\s*$', line):
                continue
            
            cleaned_lines.append(line)
            
        content = '\n'.join(cleaned_lines).strip()
        content = re.sub(r'\s+', ' ', content)
        
        deed_obj = next(d for d in deeds if d['id'] == deed_id)
        deed_obj['content'] = content
        final_deeds.append(deed_obj)
    
    return final_deeds

def main():
    pdf_path = "easy-good-deeds.pdf"
    print(f"Extracting text from {pdf_path}...")
    
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        return

    # Save full text for debugging
    with open("full_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    print("Saved full_text.txt")

    print("Loading metadata...")
    deeds_meta = load_deeds_metadata('data.js')
    
    print(f"Loaded {len(deeds_meta)} deeds from metadata.")
    
    print("Parsing deeds...")
    deeds = find_deed_content(full_text, deeds_meta)
    
    print(f"Extracted content for {len(deeds)} deeds.")
    
    # Save to JSON
    with open("deeds_content.json", "w", encoding="utf-8") as f:
        json.dump(deeds, f, indent=4)
    print("Saved to deeds_content.json")

if __name__ == "__main__":
    main()
