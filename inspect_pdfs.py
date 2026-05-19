import pikepdf
from test_stream import decode_text

pdf_files = {
    'Genesis': 'projects/verbum-dei-reader/Conteúdo/GENESIS-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'Exodus': 'projects/verbum-dei-reader/Conteúdo/EXODO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
    'Leviticus': 'projects/verbum-dei-reader/Conteúdo/LEVITICO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf'
}

for name, pdf_path in pdf_files.items():
    print(f"\n==================== {name} ====================")
    pdf = pikepdf.open(pdf_path)
    num_pages = len(pdf.pages)
    print(f"Total pages: {num_pages}")
    
    # Print page 1, 2, 3, 4, 5
    for page_idx in range(min(5, num_pages)):
        try:
            text = decode_text(pdf_path, page_idx)
            print(f"\n--- Page {page_idx} (First 200 chars) ---")
            print(text[:200].replace('\n', ' '))
        except Exception as e:
            print(f"Error page {page_idx}: {e}")
