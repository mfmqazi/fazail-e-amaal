"""
Properly integrate extracted Qur'an virtues content into fazail_data.js
"""

import json
import re

# Load extracted content
with open('quran_virtues_extracted.json', 'r', encoding='utf-8') as f:
    extracted = json.load(f)

# Load existing fazail_data.js
with open('fazail_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Get the stories we extracted - filter out very short ones
new_stories = [s for s in extracted['stories'] if len(s['content']) > 200]

print(f"Adding {len(new_stories)} stories for Virtues of Holy Qur'an")

# Find the highest existing story ID
existing_ids = re.findall(r'"id":\s*(\d+),\s*"bookId"', content)
max_id = max(int(id) for id in existing_ids) if existing_ids else 0
print(f"Highest existing story ID: {max_id}")

# Reassign IDs to new stories
for i, story in enumerate(new_stories):
    story['id'] = max_id + 1 + i

# Generate JavaScript for new stories
stories_js = ""
for story in new_stories:
    # Escape special characters in content for JavaScript
    story_content = story['content'].replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')
    story_preview = story['preview'].replace('\\', '\\\\').replace('\n', ' ').replace('"', '\\"')
    story_title = story['title'].replace('"', '\\"')
    story_chapter = story['chapter'].replace('"', '\\"')
    
    stories_js += f'''        {{
            "id": {story['id']},
            "bookId": {story['bookId']},
            "chapter": "{story_chapter}",
            "title": "{story_title}",
            "preview": "{story_preview[:200]}...",
            "content": "{story_content}"
        }},
'''

# Remove trailing comma from last story
stories_js = stories_js.rstrip(',\n') + '\n'

# Find the position to insert (before the closing ] of stories array)
# We need to find the last story entry and add after it
insert_marker = '        }\n    ]\n};'
new_content = content.replace(insert_marker, '        },\n' + stories_js + '    ]\n};')

# Write the updated file
with open('fazail_data.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully added {len(new_stories)} stories to fazail_data.js")
print(f"New story IDs: {new_stories[0]['id']} to {new_stories[-1]['id']}")
