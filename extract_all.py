import pikepdf
import os
import sys

# Add directory of test_stream to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_stream import decode_text

pdf_files = {
    'josue': 'Conteúdo/170 BOSQUEJOS DE JOSUE.pdf',
    'genesis': 'Conteúdo/GENESIS-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'exodus': 'Conteúdo/EXODO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'leviticus': 'Conteúdo/LEVITICO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'pentateuco': 'Conteúdo/30 DIAS DE ORACIÓN - VERSICULO DEL PENTATEUCO.pdf',
    'codigodivino': 'Conteúdo/Codigo Divino.pdf'
}

for name, pdf_path in pdf_files.items():
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pdf_path)
    if not os.path.exists(full_path):
        print(f"Error: {full_path} does not exist!")
        continue
        
    print(f"Extracting {name} from {pdf_path}...")
    try:
        pdf = pikepdf.open(full_path)
        num_pages = len(pdf.pages)
        
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"extracted_{name}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            for page_idx in range(num_pages):
                try:
                    text = decode_text(full_path, page_idx)
                    f.write(f"=== PAGE {page_idx} ===\n")
                    f.write(text)
                    f.write("\n\n")
                except Exception as e:
                    f.write(f"=== PAGE {page_idx} ERROR: {e} ===\n\n")
        print(f"Finished {name}. Total pages: {num_pages}")
    except Exception as e:
        print(f"Failed to open {name}: {e}")
