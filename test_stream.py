import pikepdf
import re

def parse_cmap(cmap_text):
    cmap = {}
    
    # Parse bfchar
    bfchar_blocks = re.findall(r'(\d+) beginbfchar\s+(.*?)\s+endbfchar', cmap_text, re.DOTALL)
    for count, block in bfchar_blocks:
        for line in block.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = re.findall(r'<([0-9a-fA-F]+)>', line)
            if len(parts) == 2:
                cid = int(parts[0], 16)
                val = "".join(chr(int(parts[1][i:i+4], 16)) for i in range(0, len(parts[1]), 4))
                cmap[cid] = val
                
    # Parse bfrange
    bfrange_blocks = re.findall(r'(\d+) beginbfrange\s+(.*?)\s+endbfrange', cmap_text, re.DOTALL)
    for count, block in bfrange_blocks:
        for line in block.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if range maps to a list
            if '[' in line:
                parts = re.findall(r'<([0-9a-fA-F]+)>', line)
                if len(parts) >= 2:
                    start_cid = int(parts[0], 16)
                    end_cid = int(parts[1], 16)
                    list_parts = re.findall(r'<([0-9a-fA-F]+)>', line[line.find('['):])
                    for idx, val_hex in enumerate(list_parts):
                        cid = start_cid + idx
                        val = "".join(chr(int(val_hex[i:i+4], 16)) for i in range(0, len(val_hex), 4))
                        cmap[cid] = val
            else:
                parts = re.findall(r'<([0-9a-fA-F]+)>', line)
                if len(parts) == 3:
                    start_cid = int(parts[0], 16)
                    end_cid = int(parts[1], 16)
                    start_val = int(parts[2], 16)
                    for cid in range(start_cid, end_cid + 1):
                        val_num = start_val + (cid - start_cid)
                        # val_num could be a multibyte unicode
                        val = chr(val_num)
                        cmap[cid] = val
                elif len(parts) == 2:
                    # e.g., <0001> <0001> <0041>
                    pass
    return cmap

def decode_text(pdf_path, page_num):
    pdf = pikepdf.open(pdf_path)
    page = pdf.pages[page_num]
    
    # Load fonts and their CMaps
    fonts = {}
    if hasattr(page.Resources, 'Font'):
        for name, font_obj in page.Resources.Font.items():
            if hasattr(font_obj, 'ToUnicode'):
                cmap_text = font_obj.ToUnicode.read_bytes().decode('utf-8', errors='ignore')
                fonts[name] = parse_cmap(cmap_text)
                
    # Read page content stream
    contents = page.obj.Contents
    if isinstance(contents, pikepdf.Array):
        stream_bytes = b"".join(s.read_bytes() for s in contents)
    else:
        stream_bytes = contents.read_bytes()
        
    # We want to parse the stream and extract text
    # A PDF content stream is parsed using a tokenized parser
    # Let's write a simple state machine to parse the stream bytes
    text = []
    current_font = None
    
    i = 0
    n = len(stream_bytes)
    
    while i < n:
        # Check for font changes
        # e.g. /R12 33.75 Tf
        if stream_bytes[i:i+1] == b'/':
            # Extract name
            start = i
            i += 1
            while i < n and stream_bytes[i:i+1] not in (b' ', b'\n', b'\r', b'/', b'[', b'(', b'<', b']', b')', b'>'):
                i += 1
            font_name = stream_bytes[start:i].decode('utf-8', errors='ignore')
            # Check if Tf follows shortly
            # Look ahead for Tf
            j = i
            while j < n and stream_bytes[j:j+1] in (b' ', b'\n', b'\r', b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'.'):
                j += 1
            if j + 2 <= n and stream_bytes[j:j+2] == b'Tf':
                current_font = font_name
                i = j + 2
                continue
                
        # Parse Tj operator: (string) Tj
        if stream_bytes[i:i+1] == b'(':
            # Read literal string, handling escapes
            start = i + 1
            i += 1
            paren_count = 1
            string_bytes = bytearray()
            while i < n and paren_count > 0:
                b = stream_bytes[i]
                if b == ord('(') and (i == 0 or stream_bytes[i-1] != ord('\\')):
                    paren_count += 1
                    string_bytes.append(b)
                elif b == ord(')') and (i == 0 or stream_bytes[i-1] != ord('\\')):
                    paren_count -= 1
                    if paren_count > 0:
                        string_bytes.append(b)
                elif b == ord('\\'):
                    # Handle escape
                    i += 1
                    if i < n:
                        escaped = stream_bytes[i]
                        if escaped == ord('n'):
                            string_bytes.append(ord('\n'))
                        elif escaped == ord('r'):
                            string_bytes.append(ord('\r'))
                        elif escaped == ord('t'):
                            string_bytes.append(ord('\t'))
                        elif escaped == ord('b'):
                            string_bytes.append(ord('\b'))
                        elif escaped == ord('f'):
                            string_bytes.append(ord('\f'))
                        elif escaped in (ord('('), ord(')'), ord('\\')):
                            string_bytes.append(escaped)
                        elif ord('0') <= escaped <= ord('7'):
                            # Octal escape
                            octal = bytearray([escaped])
                            if i + 1 < n and ord('0') <= stream_bytes[i+1] <= ord('7'):
                                i += 1
                                octal.append(stream_bytes[i])
                                if i + 1 < n and ord('0') <= stream_bytes[i+1] <= ord('7'):
                                    i += 1
                                    octal.append(stream_bytes[i])
                            string_bytes.append(int(octal.decode(), 8))
                else:
                    string_bytes.append(b)
                i += 1
                
            # Check if next operator is Tj or similar
            # Skip whitespace
            while i < n and stream_bytes[i:i+1] in (b' ', b'\n', b'\r'):
                i += 1
            if i + 2 <= n and stream_bytes[i:i+2] in (b'Tj', b"T*"):
                # Decode string_bytes
                decoded = decode_bytes_with_font(string_bytes, current_font, fonts)
                text.append(decoded)
                i += 2
            elif i + 1 <= n and stream_bytes[i:i+1] in (b"'", b'"'):
                decoded = decode_bytes_with_font(string_bytes, current_font, fonts)
                text.append(decoded + '\n')
                i += 1
            continue
            
        # Parse TJ operator: [ ... ] TJ
        if stream_bytes[i:i+1] == b'[':
            # Inside TJ, we have strings and numbers
            i += 1
            tj_text = []
            while i < n and stream_bytes[i:i+1] != b']':
                if stream_bytes[i:i+1] == b'(':
                    # Parse literal string
                    i += 1
                    paren_count = 1
                    string_bytes = bytearray()
                    while i < n and paren_count > 0:
                        b = stream_bytes[i]
                        if b == ord('(') and (i == 0 or stream_bytes[i-1] != ord('\\')):
                            paren_count += 1
                            string_bytes.append(b)
                        elif b == ord(')') and (i == 0 or stream_bytes[i-1] != ord('\\')):
                            paren_count -= 1
                            if paren_count > 0:
                                string_bytes.append(b)
                        elif b == ord('\\'):
                            i += 1
                            if i < n:
                                escaped = stream_bytes[i]
                                if escaped == ord('n'):
                                    string_bytes.append(ord('\n'))
                                elif escaped == ord('r'):
                                    string_bytes.append(ord('\r'))
                                elif escaped == ord('t'):
                                    string_bytes.append(ord('\t'))
                                elif escaped == ord('b'):
                                    string_bytes.append(ord('\b'))
                                elif escaped == ord('f'):
                                    string_bytes.append(ord('\f'))
                                elif escaped in (ord('('), ord(')'), ord('\\')):
                                    string_bytes.append(escaped)
                                elif ord('0') <= escaped <= ord('7'):
                                    octal = bytearray([escaped])
                                    if i + 1 < n and ord('0') <= stream_bytes[i+1] <= ord('7'):
                                        i += 1
                                        octal.append(stream_bytes[i])
                                        if i + 1 < n and ord('0') <= stream_bytes[i+1] <= ord('7'):
                                            i += 1
                                            octal.append(stream_bytes[i])
                                    string_bytes.append(int(octal.decode(), 8))
                        else:
                            string_bytes.append(b)
                        i += 1
                    decoded = decode_bytes_with_font(string_bytes, current_font, fonts)
                    tj_text.append(decoded)
                elif stream_bytes[i:i+1] == b'<':
                    # Parse hex string
                    i += 1
                    hex_bytes = bytearray()
                    while i < n and stream_bytes[i:i+1] != b'>':
                        if stream_bytes[i:i+1] not in (b' ', b'\n', b'\r'):
                            hex_bytes.append(stream_bytes[i])
                        i += 1
                    i += 1
                    try:
                        string_bytes = bytearray.fromhex(hex_bytes.decode())
                        decoded = decode_bytes_with_font(string_bytes, current_font, fonts)
                        tj_text.append(decoded)
                    except:
                        pass
                else:
                    i += 1
            i += 1 # Skip ]
            # Skip whitespace
            while i < n and stream_bytes[i:i+1] in (b' ', b'\n', b'\r'):
                i += 1
            if i + 2 <= n and stream_bytes[i:i+2] == b'TJ':
                text.append("".join(tj_text))
                i += 2
            continue
            
        i += 1
        
    return "".join(text)

def decode_bytes_with_font(string_bytes, font_name, fonts):
    if not font_name or font_name not in fonts:
        # Fallback to UTF-8
        return string_bytes.decode('utf-8', errors='ignore')
    
    cmap = fonts[font_name]
    decoded_chars = []
    
    # Check if 2 bytes per char
    # Usually true for Type 0 Fonts
    if len(string_bytes) % 2 == 0:
        for idx in range(0, len(string_bytes), 2):
            cid = (string_bytes[idx] << 8) | string_bytes[idx+1]
            char = cmap.get(cid, '?')
            decoded_chars.append(char)
    else:
        # Single byte or fallback
        for b in string_bytes:
            char = cmap.get(b, chr(b))
            decoded_chars.append(char)
            
    return "".join(decoded_chars)

if __name__ == '__main__':
    pdf_files = [
        'projects/verbum-dei-reader/Conteúdo/170 BOSQUEJOS DE JOSUE.pdf',
        'projects/verbum-dei-reader/Conteúdo/30 DIAS DE ORACIÓN - VERSICULO DEL PENTATEUCO.pdf',
        'projects/verbum-dei-reader/Conteúdo/Codigo Divino.pdf',
        'projects/verbum-dei-reader/Conteúdo/GENESIS-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
        'projects/verbum-dei-reader/Conteúdo/EXODO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf',
        'projects/verbum-dei-reader/Conteúdo/LEVITICO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf'
    ]
    for pdf in pdf_files:
        print(f"\n--- TESTING: {pdf} ---")
        try:
            # Let's decode page 1 (physical index 1, usually page 2) or page 0
            text = decode_text(pdf, 1)
            print("DECODED PAGE 1:")
            print(text[:300])
        except Exception as e:
            print(f"Error decoding {pdf}: {e}")



