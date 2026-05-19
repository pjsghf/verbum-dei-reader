import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_josue.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)

for idx, page in enumerate(pages):
    # Find any words with non-standard characters
    corrupted_words = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]*[ǔŝƪƷƖǂőŞǇĢƘŃ]*[ǔŝƪƷƖǂőŞǇĢƘŃ]+[a-zA-ZáéíóúüñÁÉÍÓÚÜÑǔŝƪƷƖǂőŞǇĢƘŃ]*\b', page)
    if corrupted_words:
        print(f"Page {idx} has corrupted words: {set(corrupted_words)}")
