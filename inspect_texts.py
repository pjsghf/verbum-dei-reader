import re
from collections import Counter

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Remove markers and HTML
    text = re.sub(r'=== PAGE \d+ ===', '', text)
    words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b', text.lower())
    return words

all_words = []
for filename in ['extracted_genesis.txt', 'extracted_exodus.txt', 'extracted_leviticus.txt', 'extracted_josue.txt']:
    try:
        words = analyze_file(f'd:/Anti Gravity/projects/verbum-dei-reader/{filename}')
        all_words.extend(words)
        print(f'{filename}: {len(words)} words, {len(set(words))} unique')
    except Exception as e:
        print(f'Error reading {filename}: {e}')

counter = Counter(all_words)
print("Top 100 words:")
for word, count in counter.most_common(100):
    print(f"  {word}: {count}")
