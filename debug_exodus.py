# -*- coding: utf-8 -*-
import re
from process_books import BookProcessor

processor = BookProcessor()
with open('extracted_exodus.txt', 'r', encoding='utf-8') as f:
    text = f.read()

raw_pages = text.split('=== PAGE ')
pages = []
for p in raw_pages:
    p = p.strip()
    if not p:
        continue
    lines = p.split('\n')
    first_line = lines[0].strip()
    if re.match(r'^\d+\s*===', first_line):
        p_text = "\n".join(lines[1:]).strip()
    else:
        p_text = p
    if p_text:
        pages.append(p_text)

page8 = pages[8]
part1, exp, app, pry = processor.parse_page_structure(page8, "Éxodo")
print("Page 8 part1:", repr(part1))

heading, verse_ref, quote = processor.parse_header_and_verse(part1, "Éxodo")
print("Heading:", repr(heading))
print("Verse Ref:", repr(verse_ref))
print("Quote:", repr(quote))

ref_chap_match = None
if verse_ref:
    ref_parts = re.search(r'(\d+):', verse_ref)
    if ref_parts:
        ref_chap_match = int(ref_parts.group(1))
print("Ref Chapter Match:", ref_chap_match)
