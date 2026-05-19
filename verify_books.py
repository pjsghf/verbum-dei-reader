# -*- coding: utf-8 -*-
import re
import sys
import os

# Configure UTF-8 output encoding for terminals
sys.stdout.reconfigure(encoding='utf-8')

def audit_database():
    print("==================================================")
    print("  VERBUM DEI - AUDITORIA DE INTEGRAÇÃO & TRADUÇÃO")
    print("==================================================")
    
    if not os.path.exists('data.js'):
        print("Erro: data.js não encontrado!")
        sys.exit(1)
        
    with open('data.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Structural Regex Parsing of data.js to count elements
    # Match the book declarations conjoining id and title
    books = re.findall(r'id:\s*["\']([^"\']+)["\'],\s*title:\s*["\']([^"\']+)["\']', content)
    
    # Clean unique IDs
    unique_books = []
    seen = set()
    for bid, title in books:
        if bid not in seen and bid in ["os-codigos-divinos", "30-dias-oracao-pentateuco", "genesis-explicado", "exodo-explicado", "levitico-explicado", "170-esbocos-de-josue"]:
            seen.add(bid)
            unique_books.append((bid, title))
            
    print(f"\n[+] Livros detectados na Base de Dados ({len(unique_books)}/6):")
    for idx, (bid, title) in enumerate(unique_books, 1):
        print(f"    {idx}. ID: {bid:<25} | Título: {title}")
        
    # Check if all 6 books are present
    all_6_ids = ["os-codigos-divinos", "30-dias-oracao-pentateuco", "genesis-explicado", "exodo-explicado", "levitico-explicado", "170-esbocos-de-josue"]
    missing = [bid for bid in all_6_ids if bid not in seen]
    if missing:
        print(f"\n[!] AVISO: Livros ausentes: {missing}")
    else:
        print("\n[✔] TODOS os 6 livros estão devidamente registrados na Base de Dados!")

    # 2. Page & Chapter Count Audit
    # Let's count occurrences of "chapters" in data.js to verify pages are parsed
    print("\n[+] Auditoria de Capítulos e Páginas por Livro:")
    
    # We will parse the chapters structure using basic regex/sub-string analysis
    for bid in all_6_ids:
        bid_idx = content.find(f'id: "{bid}"')
        if bid_idx == -1:
            print(f"    [!] {bid}: NÃO ENCONTRADO NO BANCO!")
            continue
            
        # Find pagesCount
        pages_match = re.search(r'pagesCount:\s*(\d+)', content[bid_idx:bid_idx+1000])
        pages_count = pages_match.group(1) if pages_match else "N/A"
        
        # Let's count chapters by finding occurrences of "id: "chap" or "id: "josue" inside this book's block
        # We find the next book or the end of the array
        next_bid_idx = len(content)
        for other_bid in all_6_ids:
            if other_bid == bid:
                continue
            idx = content.find(f'id: "{other_bid}"')
            if idx > bid_idx and idx < next_bid_idx:
                next_bid_idx = idx
                
        book_block = content[bid_idx:next_bid_idx]
        
        # Count chapters: search for {"id" or {id
        chapters_count = book_block.count('"pages": [') + book_block.count("'pages': [") + book_block.count('pages: [')
        
        print(f"    - {bid:<25} : {chapters_count:>3} Capítulos | {pages_count:>3} Páginas totais")

    # 3. Translation Quality Audit: Scan for leaked Spanish words
    print("\n[+] Auditoria de Qualidade de Tradução (Espanhol -> Português):")
    
    # Typical Spanish leak words to check (with word boundaries to avoid false positives)
    spanish_leaks = [
        (r'\bcon\b', "con (com)"),
        (r'\bpor\b', "por (por - acceptable in Portuguese, let's keep search context)"),
        (r'\ben\b', "en (em)"),
        (r'\ben la\b', "en la (na)"),
        (r'\ben el\b', "en el (no)"),
        (r'\bpara\b', "para (para - acceptable, skip)"),
        (r'\bdios\b', "dios (Deus)"),
        (r'\bDios\b', "Dios (Deus)"),
        (r'\bjehová\b', "jehová (Senhor)"),
        (r'\bJehová\b', "Jehová (Senhor)"),
        (r'\bGénesis\b', "Génesis (Gênesis)"),
        (r'\bÉxodo\b', "Éxodo (Êxodo)"),
        (r'\bLevítico\b', "Levítico (Levítico - check accent)"),
        (r'\bcapítulo\b', "capítulo (capítulo - check accent)"),
        (r'\bCapítulo\b', "Capítulo (Capítulo - check accent)"),
        (r'\bExplicación\b', "Explicación (Reflexão)"),
        (r'\bAplicación\b', "Aplicación (Aplicação)"),
        (r'\bOración\b', "Oración (Oração)"),
        (r'\bBǔsquŝƪǔ\b', "Bǔsquŝƪǔ (Busca)")
    ]
    
    total_leaks = 0
    for pattern, name in spanish_leaks:
        # Ignore check for common words that are identical like 'por' or 'para' if not specifically leaked
        if name in ["por (por - acceptable in Portuguese, let's keep search context)"]:
            continue
            
        matches = re.findall(pattern, content)
        count = len(matches)
        if count > 0:
            # Let's print context for critical leaks like 'en ', 'Dios', 'Jehová', 'Explicación'
            if "Acceptable" not in name:
                print(f"    [!] Alerta: {count} ocorrência(s) da palavra espanhola '{name}' detectada(s)!")
                total_leaks += count
                
    if total_leaks == 0:
        print("    [✔] Excelente! Nenhuma palavra ou marcador em espanhol vazou para as traduções.")
    else:
        print(f"    [!] Total de desvios gramaticais detectados: {total_leaks}")
        
    print("\n==================================================")
    print("             AUDITORIA CONCLUÍDA")
    print("==================================================")

if __name__ == "__main__":
    audit_database()
