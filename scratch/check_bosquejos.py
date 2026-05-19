import re

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_josue.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)
print(f"Total pages: {len(pages)}")

bosquejos = []
for idx, page in enumerate(pages):
    match = re.search(r'(Bosquejo\s+\d+):\s*(.*)', page)
    if match:
        bosquejos.append((idx, match.group(1), match.group(2)[:50]))

print(f"Total bosquejos found: {len(bosquejos)}")
print("First 5:")
for b in bosquejos[:5]:
    print(f"  Page {b[0]}: {b[1]} - {b[2]}")
print("Last 5:")
for b in bosquejos[-5:]:
    print(f"  Page {b[0]}: {b[1]} - {b[2]}")
