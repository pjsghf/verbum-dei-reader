import re

files = ['extracted_genesis.txt', 'extracted_exodus.txt', 'extracted_leviticus.txt']

for filename in files:
    print(f"=== {filename} ===")
    with open(f'd:/Anti Gravity/projects/verbum-dei-reader/{filename}', 'r', encoding='latin-1') as f:
        content = f.read()
    
    matches = re.finditer(r'(cap[íi]tulo\s*\d+)', content, re.IGNORECASE)
    count = 0
    for m in matches:
        count += 1
        start = max(0, m.start() - 10)
        end = min(len(content), m.end() + 60)
        snippet = content[start:end].replace('\n', ' ')
        print(f"  Found: '{snippet}'")
    print(f"Total chapters in {filename}: {count}")
