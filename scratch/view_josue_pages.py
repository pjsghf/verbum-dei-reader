import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('d:/Anti Gravity/projects/verbum-dei-reader/extracted_josue.txt', 'r', encoding='utf-8') as f:
    content = f.read()

pages = re.split(r'=== PAGE \d+ ===', content)

print("=== Page 166 ===")
print(pages[166].strip()[:500])

print("=== Page 187 ===")
print(pages[187].strip()[:500])

print("=== Page 188 ===")
print(pages[188].strip()[:500])

print("=== Page 205 ===")
print(pages[205].strip()[:500])
