import re

files = {
    'Genesis': 'extracted_genesis.txt',
    'Exodus': 'extracted_exodus.txt',
    'Leviticus': 'extracted_leviticus.txt',
    'Joshua': 'extracted_josue.txt'
}

for name, filename in files.items():
    print(f"\n==================== {name} ====================")
    path = f'd:/Anti Gravity/projects/verbum-dei-reader/{filename}'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Let's find any matches for "Capítulo" or "Bosquejo"
    matches = re.findall(r'(Cap[íi]tulo\s+\d+|Bosquejo\s+\d+)', content, re.IGNORECASE)
    print(f"Total matches of 'Capítulo/Bosquejo': {len(matches)}")
    if len(matches) > 0:
        print("First 10 matches:")
        for m in matches[:10]:
            print(f"  {m}")
        print("Last 5 matches:")
        for m in matches[-5:]:
            print(f"  {m}")
