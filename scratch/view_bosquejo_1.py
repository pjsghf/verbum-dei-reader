import re

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_josue.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)
print(pages[6])
