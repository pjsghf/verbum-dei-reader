import re
import sys

# Reconfigure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_josue.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)
print(f"Total pages in file: {len(pages)}")

# Print page index and the first non-empty line
for idx, page in enumerate(pages):
    lines = [l.strip() for l in page.split('\n') if l.strip()]
    if lines:
        print(f"Page {idx}: '{lines[0][:100]}'")
    else:
        print(f"Page {idx}: (empty)")
