import os

files = ['extracted_pentateuco.txt', 'extracted_codigodivino.txt']

for filename in files:
    path = f'd:/Anti Gravity/projects/verbum-dei-reader/{filename}'
    size = os.path.getsize(path)
    print(f"=== {filename} (Size: {size} bytes) ===")
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    # Find all "PAGE" or headers
    pages = [line.strip() for line in lines if line.startswith('=== PAGE')]
    print(f"Total pages: {len(pages)}")
    if pages:
        print(f"First page: {pages[0]}, Last page: {pages[-1]}")
    
    # Print first 20 non-empty lines
    print("First 20 non-empty lines:")
    non_empty = [line.strip() for line in lines if line.strip()]
    for line in non_empty[:20]:
        print(f"  {line[:120]}")
    print("\n")
