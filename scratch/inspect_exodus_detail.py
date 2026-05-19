import re

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_exodus.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)
print(f"Total pages: {len(pages)}")

for idx, page in enumerate(pages[:20]):
    lines = [l.strip() for l in page.split('\n') if l.strip()]
    if lines:
        print(f"Page {idx}: '{lines[0][:100]}'")
    else:
        print(f"Page {idx}: Empty")
