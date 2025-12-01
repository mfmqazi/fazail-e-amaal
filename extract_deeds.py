import json
import re
import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return None

    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
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

def clean_text(text):
    return text

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
        72: 78, # data.js 72 (Right) -> PDF 78
        73: 19, # data.js 73 (Morsel) -> PDF 19 (typo for 79)
        74: 80, # data.js 74 (Sneezing) -> PDF 80
        75: 81, # data.js 75 (Fear) -> PDF 81
        76: 82, # data.js 76 (Optimism) -> PDF 82
        # 77: 71, # REMOVED: We will handle 77 by copying 71's content manually
        78: 9999, # Block data.js 78 (Consultation) from PDF 78
        79: 9999, # Block data.js 79 (Shura)
        80: 9999, # Block data.js 80 (Graveyards) from PDF 80
        81: 9999, # Block data.js 81 (Wudu) from PDF 81
        82: 9999  # Block data.js 82 (Debt) from PDF 82
    }
    
    # Overrides for Regex patterns for specific IDs (original ID)
    REGEX_OVERRIDES = {
        1: r'(?:^|\n)\s*\(1\)\s+GOOD', # Deed 1 override
        2: r'(?:^|\n)\s*2\.\s+PRAYING', # Deed 2 uses "2. PRAYING"
        21: r'(?:^|\n)\s*(?:Tenderness\s+towards\s+others|\(21\))', # Missing header
        51: r'(?:\(511|511\.)', # Typo in PDF, appears mid-line
        68: r'(?:^|\n).*?\(68\)', # Loose match for 68 (has noise before it), non-greedy
        71: r'(?:^|\n)\s*(?:\(71\)|71\.|Six\s+Good\s+Deeds|\(71\)-\(17\))', # Weird label
        73: r'(?:^|\n)\s*(?:\(19\)|19\.)\s+CLEANING' # Second (19)
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
    
    # Post-processing: Copy content for missing deeds if needed
    # Specifically for 77 (Modesty) which is part of 71 (Six Good Deeds)
    deed_71 = next((d for d in final_deeds if d['id'] == 71), None)
    if deed_71:
        deed_77_orig = next((d for d in deeds if d['id'] == 77), None)
        if deed_77_orig:
            # Check if 77 is already in final_deeds (it shouldn't be if it wasn't found)
            if not any(d['id'] == 77 for d in final_deeds):
                print("Copying content from Deed 71 to Deed 77")
                deed_77_orig['content'] = deed_71['content']
                final_deeds.append(deed_77_orig)
        
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
