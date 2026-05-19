import re

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_josue.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)

for idx, page in enumerate(pages):
    match = re.search(r'Bosquejo\s+(\d+)\b', page)
    if match:
        num = int(match.group(1))
        # Print if page index and Bosquejo number differ or let's see how they map
        print(f"Page {idx}: contains Bosquejo {num} ('{page.strip().splitlines()[0][:60]}')")
