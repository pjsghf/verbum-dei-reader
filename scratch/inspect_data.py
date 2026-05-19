import re

def main():
    with open('data.js', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # find occurrences of id: "..." and title: "..."
    # We can match id: and title: in the outer dictionary objects
    # Let's search for matches of id: and title: at the beginning of object declarations
    matches = re.findall(r'id:\s*["\']([^"\']+)["\'],\s*title:\s*["\']([^"\']+)["\']', text)
    print("Found books in database:")
    for book_id, title in matches:
        print(f"  ID: {book_id} -> Title: {title}")

if __name__ == '__main__':
    main()
