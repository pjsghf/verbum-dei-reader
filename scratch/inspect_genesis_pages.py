def main():
    with open('extracted_genesis.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    pages = text.split('=== PAGE ')
    
    with open('scratch/genesis_pages.txt', 'w', encoding='utf-8') as out:
        for i, p in enumerate(pages):
            lines = [line.strip() for line in p.split('\n') if line.strip()]
            first_line = lines[1] if len(lines) > 1 else 'EMPTY'
            out.write(f"Page {i}: {first_line}\n")

if __name__ == '__main__':
    main()
