def main():
    for name in ['extracted_genesis.txt', 'extracted_exodus.txt', 'extracted_leviticus.txt']:
        with open(name, 'r', encoding='utf-8') as f:
            text = f.read()
        pages = text.split('=== PAGE ')
        print(f"File: {name} (Total pages: {len(pages)})")
        chapter_pages = []
        for i, p in enumerate(pages):
            lines = [l.strip() for l in p.split('\n') if l.strip()]
            if not lines:
                continue
            first_lines = " | ".join(lines[1:3])
            # search for "Capítulo" or "Capitulo" (case insensitive)
            if 'cap' in first_lines.lower() or 'capí' in first_lines.lower():
                chapter_pages.append((i, first_lines[:100]))
        print(f"  Found chapter-like keywords in pages:")
        for idx, text_preview in chapter_pages:
            print(f"    Page {idx}: {text_preview}")

if __name__ == '__main__':
    main()
