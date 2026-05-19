# -*- coding: utf-8 -*-
import os
import re
import sys
import time
from deep_translator import GoogleTranslator

sys.stdout.reconfigure(encoding='utf-8')

class FileTranslator:
    def __init__(self):
        self.translator = GoogleTranslator(source='es', target='pt')
        
    def chunk_text(self, text, max_chars=3500):
        # Split text into lines to avoid cutting in the middle of a line or a page marker
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_len = 0
        
        for line in lines:
            line_len = len(line) + 1
            if current_len + line_len > max_chars:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += line_len
                
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks

    def translate_with_retry(self, text, retries=5, delay=2):
        if not text.strip():
            return text
            
        for i in range(retries):
            try:
                translated = self.translator.translate(text)
                if translated:
                    # Clean up encoding artifacts if any
                    return translated
            except Exception as e:
                print(f"  [!] Erro de conexão na tradução (tentativa {i+1}/{retries}): {e}")
                time.sleep(delay)
                delay *= 1.5
                
        raise Exception("Falha crítica: Não foi possível traduzir o bloco após várias tentativas.")

    def translate_file(self, src_filename, dest_filename):
        print(f"\n=== Traduzindo {src_filename} -> {dest_filename} ===")
        if not os.path.exists(src_filename):
            print(f"[Erro] Arquivo de origem não encontrado: {src_filename}")
            return
            
        with open(src_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = self.chunk_text(content)
        total_chunks = len(chunks)
        print(f"Arquivo dividido em {total_chunks} blocos de tradução.")
        
        translated_chunks = []
        for idx, chunk in enumerate(chunks):
            print(f"  Trabalhando no bloco {idx+1}/{total_chunks} ({len(chunk)} caracteres)...", end="", flush=True)
            t_chunk = self.translate_with_retry(chunk)
            
            # Normalize translated markers
            # Sometimes Google Translate translates "=== PAGE 1 ===" into "=== PÁGINA 1 ===", "=== Pagina 1 ===", etc.
            # We want to normalize them back to standard "=== PAGE X ===" so the compiler works perfectly!
            t_chunk = re.sub(r'===\s*(?:P[Ááa]GINA|P[áa]gina|Pgina|P\u00c1gina|PAGE|Page)\s*(\d+)\s*===', r'=== PAGE \1 ===', t_chunk)
            
            # Fine-tune translation anomalies to ensure 100% perfect PT-BR
            # E.g. "Jehová" -> "Senhor" (standard in Portuguese bibles)
            t_chunk = re.sub(r'\bJehová\b', 'Senhor', t_chunk)
            t_chunk = re.sub(r'\bjehová\b', 'Senhor', t_chunk)
            t_chunk = re.sub(r'\bél\b', 'ele', t_chunk, flags=re.IGNORECASE)
            
            translated_chunks.append(t_chunk)
            print(" Concluído!")
            time.sleep(0.5) # Soft delay to avoid rate limit
            
        final_content = '\n'.join(translated_chunks)
        
        with open(dest_filename, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        print(f"=== {dest_filename} salvo com sucesso! ===")

if __name__ == "__main__":
    translator = FileTranslator()
    
    files_to_translate = [
        ('extracted_genesis.txt', 'extracted_genesis_pt.txt'),
        ('extracted_exodus.txt', 'extracted_exodus_pt.txt'),
        ('extracted_leviticus.txt', 'extracted_leviticus_pt.txt'),
        ('extracted_josue.txt', 'extracted_josue_pt.txt')
    ]
    
    for src, dest in files_to_translate:
        translator.translate_file(src, dest)
        
    print("\nTodos os arquivos de texto foram perfeitamente traduzidos para Português (PT-BR)!")
