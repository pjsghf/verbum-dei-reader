# -*- coding: utf-8 -*-
import os
import re
import sys

# Configure UTF-8 output encoding for terminals
sys.stdout.reconfigure(encoding='utf-8')

# Import the BiblicalTranslator class
from test_translation import BiblicalTranslator

class BookProcessor:
    def __init__(self):
        print("Inicializando Tradutor Bíblico...")
        self.translator = BiblicalTranslator()
        
    def translate(self, text):
        if not text:
            return ""
        # Clean some known weird Spanish characters/artifacts from extraction
        text = text.replace("Bǔsquŝƪǔ", "Busca")
        text = text.replace("Búsqueda", "Busca")
        
        # Core translation
        translated = self.translator.translate_text(text)
        
        # Extra fine-tuning of translations for Portuguese readability
        portuguese_replacements = {
            "Génesis": "Gênesis",
            "Éxodo": "Êxodo",
            "Levítico": "Levítico",
            "Josué": "Josué",
            "Explicación:": "Reflexão:",
            "Explicación": "Reflexão",
            "Aplicación:": "Aplicação:",
            "Aplicación": "Aplicação",
            "Oración:": "Oração:",
            "Oración": "Oração",
            "Enseñanza:": "Reflexão:",
            "Enseñanza": "Reflexão",
            "Meditación:": "Reflexão:",
            "Meditación": "Reflexão",
            "jehová": "Senhor",
            "Jehová": "Senhor",
            "Moisés": "Moisés",
            "sacerdote": "sacerdote",
            "tabernáculo": "tabernáculo",
            "holocausto": "holocausto",
            "expiación": "expiação",
            "ofrenda": "oferta",
            "pecado": "pecado",
            "perdón": "perdão"
        }
        
        for key, val in portuguese_replacements.items():
            translated = re.sub(r'\b' + re.escape(key) + r'\b', val, translated)
            translated = re.sub(r'\b' + re.escape(key.capitalize()) + r'\b', val.capitalize(), translated)
            
        return translated

    def parse_page_structure(self, page_text, book_name):
        # Normalize whitespace
        page_text = page_text.strip()
        
        explanation_markers = [r'Explicaci[oó\ufffd]n:', r'Ense[nñ\ufffd]anza:', r'Meditaci[oó\ufffd]n:', r'Exposici[oó\ufffd]n:', r'Ense[nñ\ufffd]anza B[ií\ufffd]blica:?']
        application_markers = [r'Aplicaci[oó\ufffd]n:', r'Reflexi[oó\ufffd]n:']
        prayer_markers = [r'Oraci[oó\ufffd]n:']
        
        exp_pattern = '|'.join(explanation_markers)
        app_pattern = '|'.join(application_markers)
        pry_pattern = '|'.join(prayer_markers)
        
        has_exp = re.search(exp_pattern, page_text, re.IGNORECASE)
        has_app = re.search(app_pattern, page_text, re.IGNORECASE)
        has_pry = re.search(pry_pattern, page_text, re.IGNORECASE)
        
        # If absolutely no typical structure is found, it's a pure text page
        if not (has_exp or has_app or has_pry):
            return page_text, "", "", ""
            
        # Case A: Explicit Explanation header is present
        if has_exp:
            exp_split = re.split(exp_pattern, page_text, flags=re.IGNORECASE)
            part1 = exp_split[0].strip()
            
            explanation_text = ""
            application_text = ""
            prayer_text = ""
            
            if len(exp_split) > 1:
                rest = exp_split[1].strip()
                app_split = re.split(app_pattern, rest, flags=re.IGNORECASE)
                explanation_text = app_split[0].strip()
                
                if len(app_split) > 1:
                    rest2 = app_split[1].strip()
                    pry_split = re.split(pry_pattern, rest2, flags=re.IGNORECASE)
                    application_text = pry_split[0].strip()
                    if len(pry_split) > 1:
                        prayer_text = pry_split[1].strip()
                else:
                    pry_split = re.split(pry_pattern, rest, flags=re.IGNORECASE)
                    if len(pry_split) > 1:
                        explanation_text = pry_split[0].strip()
                        prayer_text = pry_split[1].strip()
                    else:
                        explanation_text = rest
                        
            return part1, explanation_text, application_text, prayer_text
            
        # Case B: No explanation header, but we have application or prayer (common in Êxodo)
        split_pattern = f"(?:{app_pattern}|{pry_pattern})"
        parts = re.split(split_pattern, page_text, 1, flags=re.IGNORECASE)
        part1 = parts[0].strip()
        
        # Try to isolate the commentary inside part1 from the scripture quote
        # Quotes are usually inside double quotes "..." or “...” or «...»
        explanation_text = ""
        quote_match = re.search(r'["“«]([^"”»]+)["”»]', part1)
        if quote_match:
            quote_end = quote_match.end()
            explanation_text = part1[quote_end:].strip()
            # Clean up explanation text (remove trailing colons or leading periods)
            explanation_text = re.sub(r'^[\s\.:\-,]+', '', explanation_text).strip()
            part1 = part1[:quote_end].strip()
            
        application_text = ""
        prayer_text = ""
        
        if has_app and has_pry:
            app_match = re.search(app_pattern, page_text, re.IGNORECASE)
            pry_match = re.search(pry_pattern, page_text, re.IGNORECASE)
            app_idx = app_match.start()
            pry_idx = pry_match.start()
            
            if app_idx < pry_idx:
                app_text_start = app_idx + len(app_match.group(0))
                application_text = page_text[app_text_start:pry_idx].strip()
                pry_text_start = pry_idx + len(pry_match.group(0))
                prayer_text = page_text[pry_text_start:].strip()
            else:
                pry_text_start = pry_idx + len(pry_match.group(0))
                prayer_text = page_text[pry_text_start:app_idx].strip()
                app_text_start = app_idx + len(app_match.group(0))
                application_text = page_text[app_text_start:].strip()
        elif has_app:
            app_match = re.search(app_pattern, page_text, re.IGNORECASE)
            app_text_start = app_match.start() + len(app_match.group(0))
            application_text = page_text[app_text_start:].strip()
        elif has_pry:
            pry_match = re.search(pry_pattern, page_text, re.IGNORECASE)
            pry_text_start = pry_match.start() + len(pry_match.group(0))
            prayer_text = page_text[pry_text_start:].strip()
            
        return part1, explanation_text, application_text, prayer_text

    def parse_header_and_verse(self, part1, book_name):
        # Build a resilient regex pattern for the book name that tolerates encoding/replacement artifacts
        book_patterns = {
            "Génesis": r"(?:G[eé\ufffd]?nesis|G\u00e9nesis|Gnesis)",
            "Éxodo": r"(?:[EÉeé\ufffd]?xodo|xodo|[X\ufffd]ODO)",
            "Levítico": r"(?:Lev[ií\ufffd]?tico|Lev\u00edtico|Levtico|LEVTICO)",
            "Josué": r"(?:Josu[eé\ufffd]?|Josu\u00e9|Josu|JOSU)"
        }
        pattern_str = book_patterns.get(book_name, re.escape(book_name))
        ref_pattern = rf'({pattern_str})\s+(\d+:\d+(?:-\d+)?)'
        ref_match = re.search(ref_pattern, part1, re.IGNORECASE)
        
        heading = ""
        verse_ref = ""
        quote = ""
        
        if ref_match:
            start_idx = ref_match.start()
            heading = part1[:start_idx].strip()
            rest = part1[start_idx:].strip()
            
            verse_ref = ref_match.group(0)
            quote_part = rest[len(verse_ref):].strip()
            
            # Clean double quotes
            quote = quote_part.strip('"').strip('“').strip('”').strip().strip(':').strip()
        else:
            heading = part1
            
        return heading, verse_ref, quote

    def build_page_html(self, heading, verse_ref, quote, explanation, application, prayer):
        # Translate components
        t_heading = self.translate(heading)
        t_ref = self.translate(verse_ref)
        t_quote = self.translate(quote)
        t_explanation = self.translate(explanation)
        t_application = self.translate(application)
        t_prayer = self.translate(prayer)
        
        # Build HTML
        html_parts = []
        
        # Heading
        if t_heading:
            html_parts.append(f"<h3>{t_heading}</h3>")
        elif t_ref:
            html_parts.append(f"<h3>{t_ref}</h3>")
            
        # Verse Blockquote
        if t_quote:
            ref_str = f" — {t_ref}" if t_ref else ""
            html_parts.append(f'<blockquote class="ancient-quote">\n  "{t_quote}"{ref_str}\n</blockquote>')
            
        # Explanation / Reflection
        if t_explanation:
            html_parts.append(f"<p><strong>Reflexão:</strong> {t_explanation}</p>")
            
        # Application
        if t_application:
            html_parts.append(f"<p><strong>Aplicação:</strong> {t_application}</p>")
            
        # Prayer Box
        if t_prayer:
            html_parts.append(f'<div class="prayer-box">\n  <strong>Oração Guiada:</strong><br>\n  {t_prayer}\n</div>')
            
        return "\n".join(html_parts)

    def process_versicle_book(self, filename, spanish_book_name, portuguese_book_name):
        print(f"Processando livro: {portuguese_book_name} ({filename})...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        pages = content.split('=== PAGE ')
        # The first page might be empty or title, let's look at all non-empty pages
        book_pages = []
        for p in pages:
            p = p.strip()
            if not p:
                continue
            # Remove the page header index (e.g. "0 ===" or "1 ===")
            lines = p.split('\n')
            first_line = lines[0].strip()
            if re.match(r'^\d+\s*===', first_line):
                p_text = "\n".join(lines[1:]).strip()
            else:
                p_text = p
                
            if p_text:
                book_pages.append(p_text)
                
        # Group into chapters dynamically
        chapters = []
        intro_chapter = {
            "id": "intro",
            "title": "Introdução e Contexto",
            "pages": []
        }
        
        current_chapter = None
        
        # Keep track of active bible chapter numbers to auto-group
        active_bible_chapter = None
        
        for idx, page_text in enumerate(book_pages):
            part1, explanation, application, prayer = self.parse_page_structure(page_text, spanish_book_name)
            
            # Check if it's an introduction page
            is_intro = not (explanation or application or prayer)
            
            if is_intro:
                # Compile intro page HTML
                intro_html = f"<h3>{self.translate(part1)}</h3>"
                # Add content of lines as paragraphs
                paragraphs = [p.strip() for p in part1.split('\n') if p.strip()]
                # If the first paragraph is the header, let's treat it nicely
                if len(paragraphs) > 1:
                    intro_html = f"<h3>{self.translate(paragraphs[0])}</h3>\n"
                    for para in paragraphs[1:]:
                        intro_html += f"<p>{self.translate(para)}</p>\n"
                else:
                    intro_html = f"<p>{self.translate(part1)}</p>"
                    
                intro_chapter["pages"].append(intro_html)
                continue
                
            heading, verse_ref, quote = self.parse_header_and_verse(part1, spanish_book_name)
            
            # Grouping Logic:
            # If there's an explicit "Capítulo X" in the heading or first lines:
            chap_match = re.search(r'Cap[íi\ufffd]tulo\s+(\d+)', heading + " " + page_text, re.IGNORECASE)
            
            # Or parse from reference: "Génesis 1:1" -> bible chapter 1
            ref_chap_match = None
            if verse_ref:
                # Find chapter number before colon
                ref_parts = re.search(r'(\d+):', verse_ref)
                if ref_parts:
                    ref_chap_match = int(ref_parts.group(1))
            
            if chap_match:
                chap_num = int(chap_match.group(1))
                # Create a new chapter
                title_clean = re.sub(r'Cap[íi\ufffd]tulo\s+\d+:\s*', '', heading, flags=re.IGNORECASE).strip()
                if not title_clean:
                    title_clean = f"Estudo do Capítulo {chap_num}"
                
                current_chapter = {
                    "id": f"chap-{chap_num}",
                    "title": f"Capítulo {chap_num}: {self.translate(title_clean)}",
                    "pages": []
                }
                chapters.append(current_chapter)
                active_bible_chapter = chap_num
            elif ref_chap_match and ref_chap_match != active_bible_chapter:
                # Chapter changed from the verse reference
                chap_num = ref_chap_match
                current_chapter = {
                    "id": f"chap-{chap_num}",
                    "title": f"Capítulo {chap_num}: {portuguese_book_name} Capítulo {chap_num}",
                    "pages": []
                }
                chapters.append(current_chapter)
                active_bible_chapter = chap_num
            elif current_chapter is None:
                # If no chapter created yet, create a default first chapter
                current_chapter = {
                    "id": "chap-1",
                    "title": f"Capítulo 1: Início dos Estudos",
                    "pages": []
                }
                chapters.append(current_chapter)
                active_bible_chapter = 1
                
            # Build and append page HTML
            page_html = self.build_page_html(heading, verse_ref, quote, explanation, application, prayer)
            current_chapter["pages"].append(page_html)
            
        # Add intro chapter if it has pages
        final_chapters = []
        if intro_chapter["pages"]:
            final_chapters.append(intro_chapter)
        final_chapters.extend(chapters)
        
        # Calculate total page count
        total_pages = sum(len(c["pages"]) for c in final_chapters)
        
        return final_chapters, total_pages

    def process_joshua_outlines(self, filename):
        print("Processando livro: 170 Esboços de Josué...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        pages = content.split('=== PAGE ')
        book_pages = []
        for p in pages:
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
                book_pages.append(p_text)
                
        # Grouping Joshua Outlines:
        # Pages index 0 to 4 are introductory (Presentation, Historical Context, Author, Theology)
        # Pages 5 to 220 are outlines
        # Page 221 is Reflection Final
        
        intro_pages_raw = book_pages[:5]
        outline_pages_raw = book_pages[5:-1]
        conclusion_pages_raw = [book_pages[-1]]
        
        chapters = []
        
        # 1. Introdução Chapter
        intro_chapter = {
            "id": "josue-intro",
            "title": "Introdução e Contexto Histórico",
            "pages": []
        }
        for idx, page in enumerate(intro_pages_raw):
            paragraphs = [p.strip() for p in page.split('\n') if p.strip()]
            html = f"<h3>{self.translate(paragraphs[0])}</h3>\n"
            for para in paragraphs[1:]:
                html += f"<p>{self.translate(para)}</p>\n"
            intro_chapter["pages"].append(html)
        chapters.append(intro_chapter)
        
        # 2. Outline Chapters (10 outlines each)
        outline_idx = 1
        current_chapter = None
        
        for idx, page in enumerate(outline_pages_raw):
            part1, explanation, application, prayer = self.parse_page_structure(page, "Josué")
            heading, verse_ref, quote = self.parse_header_and_verse(part1, "Josué")
            
            # Check if this starts a new chapter of 10
            # E.g., at outline 1, 11, 21, 31...
            if (outline_idx - 1) % 10 == 0:
                chap_start = outline_idx
                chap_end = chap_start + 9
                current_chapter = {
                    "id": f"josue-esbocos-{chap_start}-{chap_end}",
                    "title": f"Esboços {chap_start} a {chap_end}",
                    "pages": []
                }
                chapters.append(current_chapter)
                
            # Build and append page HTML
            page_html = self.build_page_html(heading, verse_ref, quote, explanation, application, prayer)
            current_chapter["pages"].append(page_html)
            
            outline_idx += 1
            
        # 3. Reflexão Final Chapter
        conclusion_chapter = {
            "id": "josue-conclusion",
            "title": "Reflexão Final e Legado",
            "pages": []
        }
        for idx, page in enumerate(conclusion_pages_raw):
            paragraphs = [p.strip() for p in page.split('\n') if p.strip()]
            html = f"<h3>{self.translate(paragraphs[0])}</h3>\n"
            for para in paragraphs[1:]:
                html += f"<p>{self.translate(para)}</p>\n"
            conclusion_chapter["pages"].append(html)
        chapters.append(conclusion_chapter)
        
        total_pages = sum(len(c["pages"]) for c in chapters)
        return chapters, total_pages

    def generate_all_books(self):
        # 1. Process Genesis
        genesis_chapters, genesis_pages = self.process_versicle_book(
            'extracted_genesis.txt', 'Génesis', 'Gênesis'
        )
        
        # 2. Process Exodus
        exodus_chapters, exodus_pages = self.process_versicle_book(
            'extracted_exodus.txt', 'Éxodo', 'Êxodo'
        )
        
        # 3. Process Leviticus
        leviticus_chapters, leviticus_pages = self.process_versicle_book(
            'extracted_leviticus.txt', 'Levítico', 'Levítico'
        )
        
        # 4. Process Joshua Outlines
        joshua_chapters, joshua_pages = self.process_joshua_outlines(
            'extracted_josue.txt'
        )
        
        # Construct the javascript definitions
        js_books = []
        
        # Genesis book
        js_books.append({
            "id": "genesis-explicado",
            "title": "Gênesis Explicado",
            "subtitle": "Versículo por Versículo",
            "author": "Verbum Dei",
            "cover": "assets/cover-genesis.webp",
            "description": "Uma jornada profunda pelas origens de todas as coisas. Descubra as chaves de sabedoria contidas nos primeiros capítulos do livro de Gênesis, explicadas versículo por versículo com reflexão e oração.",
            "category": "Estudo Bíblico",
            "readingTime": "60 min",
            "pagesCount": genesis_pages,
            "chapters": genesis_chapters
        })
        
        # Exodus book
        js_books.append({
            "id": "exodo-explicado",
            "title": "Êxodo Explicado",
            "subtitle": "Versículo por Versículo",
            "author": "Verbum Dei",
            "cover": "assets/cover-exodo.webp",
            "description": "A extraordinária história da libertação do povo de Israel do Egito, com explicações práticas e orações que iluminam nossa caminhada diária de fé.",
            "category": "Estudo Bíblico",
            "readingTime": "60 min",
            "pagesCount": exodus_pages,
            "chapters": exodus_chapters
        })
        
        # Leviticus book
        js_books.append({
            "id": "levitico-explicado",
            "title": "Levítico Explicado",
            "subtitle": "Versículo por Versículo",
            "author": "Verbum Dei",
            "cover": "assets/cover-levitico.webp",
            "description": "Uma exploração detalhada do livro da santidade, com reflexões e orações que trazem os antigos rituais para um significado espiritual e diário prático.",
            "category": "Estudo Bíblico",
            "readingTime": "60 min",
            "pagesCount": leviticus_pages,
            "chapters": leviticus_chapters
        })
        
        # Joshua book
        js_books.append({
            "id": "170-esbocos-de-josue",
            "title": "170 Esboços de Josué",
            "subtitle": "Estudos Bíblicos e Aplicações Práticas",
            "author": "Verbum Dei",
            "cover": "assets/cover-josue.webp",
            "description": "Um tesouro homilético indispensável com 170 esboços de sermões totalmente estruturados com ensinamentos, aplicações e orações baseados no livro de Josué.",
            "category": "Estudo Bíblico",
            "readingTime": "90 min",
            "pagesCount": joshua_pages,
            "chapters": joshua_chapters
        })
        
        return js_books

    def run(self):
        # Load the base data.js
        with open('data.js', 'r', encoding='utf-8') as f:
            raw_js = f.read()
            
        # Dynamically detect if a previous compilation is already in data.js to maintain idempotency
        generated_ids = ["genesis-explicado", "exodo-explicado", "levitico-explicado", "170-esbocos-de-josue"]
        earliest_idx = len(raw_js)
        for gid in generated_ids:
            idx = raw_js.find(f'id: "{gid}"')
            if idx != -1 and idx < earliest_idx:
                earliest_idx = idx
                
        if earliest_idx < len(raw_js):
            # We found a previous compilation! Slice right before its opening brace '{'
            brace_idx = raw_js.rfind('{', 0, earliest_idx)
            if brace_idx == -1:
                print("Erro: Não foi possível encontrar a abertura do primeiro objeto compilado!")
                sys.exit(1)
            base_js = raw_js[:brace_idx].strip()
        else:
            # First time running, slice right before the original "170-esbocos-de-josue" placeholder
            target_idx = raw_js.find('id: "170-esbocos-de-josue"')
            if target_idx == -1:
                print("Erro: Não foi possível encontrar a marca de corte do livro Josué placeholder no banco data.js!")
                sys.exit(1)
                
            brace_idx = raw_js.rfind('{', 0, target_idx)
            if brace_idx == -1:
                print("Erro: Não foi possível encontrar a abertura do objeto Josué placeholder!")
                sys.exit(1)
            base_js = raw_js[:brace_idx].strip()
            
        if base_js.endswith(','):
            pass
        else:
            base_js += ','
            
        # Generate new books
        new_books = self.generate_all_books()
        
        # Convert the new books into beautiful, clean JS object format (compatible with our data.js style)
        import json
        
        def format_js_value(val, indent_level=0):
            indent = "  " * indent_level
            if isinstance(val, dict):
                parts = ["{"]
                for k, v in val.items():
                    # For keys, format as plain JS property names if they are valid identifier names
                    prop_name = k
                    if not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', k):
                        prop_name = json.dumps(k)
                    parts.append(f"{indent}  {prop_name}: {format_js_value(v, indent_level + 1)},")
                parts.append(indent + "}")
                return "\n".join(parts)
            elif isinstance(val, list):
                parts = ["["]
                for item in val:
                    parts.append(f"{indent}  {format_js_value(item, indent_level + 1)},")
                parts.append(f"{indent}]")
                return "\n".join(parts)
            elif isinstance(val, str):
                # If the string contains HTML or newlines, format as modern template literals ``
                if '\n' in val or '<' in val or '"' in val:
                    # Clean up template literal escape characters
                    escaped = val.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
                    return f"`{escaped}`"
                else:
                    return json.dumps(val, ensure_ascii=False)
            else:
                return json.dumps(val)

        print("Formatando e compilando novos livros em Javascript...")
        js_books_chunks = []
        for idx, book in enumerate(new_books):
            formatted_book = format_js_value(book, indent_level=1)
            js_books_chunks.append(formatted_book)
            
        # Combine base_js and new compiled book objects
        new_data_js = base_js + "\n" + ",\n".join(js_books_chunks) + "\n];\n\nexport default BOOKS_DATABASE;\n"
        
        # Write to file
        with open('data.js', 'w', encoding='utf-8') as f:
            f.write(new_data_js)
            
        print("data.js gerado e sincronizado com sucesso!")

if __name__ == "__main__":
    processor = BookProcessor()
    processor.run()
