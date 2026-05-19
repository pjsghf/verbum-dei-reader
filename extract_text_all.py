import pikepdf
from test_stream import decode_text

pdf_files = {
    'josue': 'projects/verbum-dei-reader/Conteúdo/170 BOSQUEJOS DE JOSUE.pdf',
    'genesis': 'projects/verbum-dei-reader/Conteúdo/GENESIS-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'exodus': 'projects/verbum-dei-reader/Conteúdo/EXODO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'leviticus': 'projects/verbum-dei-reader/Conteúdo/LEVITICO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf'
}

for name, pdf_path in pdf_files.items():
    print(f"Extracting {name}...")
    pdf = pikepdf.open(pdf_path)
    num_pages = len(pdf.pages)
    
    with open(f"projects/verbum-dei-reader/extracted_{name}.txt", "w", encoding="utf-8") as f:
        for page_idx in range(num_pages):
            try:
                text = decode_text(pdf_path, page_idx)
                f.write(f"=== PAGE {page_idx} ===\n")
                f.write(text)
                f.write("\n\n")
            except Exception as e:
                f.write(f"=== PAGE {page_idx} ERROR: {e} ===\n\n")
    print(f"Finished {name}. Total pages: {num_pages}")
