# --- CÁC HÀM XỬ LÝ LOGIC PLAYFAIR ---

def is_ascii_letter(char):
    """Kiểm tra ký tự A-Z không dấu"""
    return 'A' <= char.upper() <= 'Z'

def is_ascii_alnum(char):
    """Kiểm tra ký tự A-Z hoặc 0-9 không dấu"""
    c = char.upper()
    return ('A' <= c <= 'Z') or ('0' <= c <= '9')

def generate_matrix_5x5(key):
    key = ''.join([c.upper() for c in key if is_ascii_letter(c)])
    key = key.replace('J', 'I')
    key_unique = []
    for c in key:
        if c not in key_unique: key_unique.append(c)
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ' 
    for c in alphabet:
        if c not in key_unique: key_unique.append(c)
    matrix = [key_unique[i:i+5] for i in range(0, 25, 5)]
    return matrix

def generate_matrix_6x6(key):
    key = ''.join([c.upper() for c in key if is_ascii_alnum(c)])
    key_unique = []
    for c in key:
        if c not in key_unique: key_unique.append(c)
    alphanumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for c in alphanumeric:
        if c not in key_unique: key_unique.append(c)
    matrix = [key_unique[i:i+6] for i in range(0, 36, 6)]
    return matrix

def find_position(matrix, char):
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char: return i, j
    return None, None

# --- HÀM XỬ LÝ VĂN BẢN (DÙNG CHUNG CHO CẢ MÃ HÓA VÀ GIẢI MÃ) ---

def process_plaintext_5x5(text, sep1='X', sep2='Y'):
    """Xử lý văn bản 5x5: Tách cặp, chèn sep1/sep2 nếu trùng hoặc lẻ"""
    filtered_text = []
    for char in text:
        if is_ascii_letter(char):
            filtered_text.append(char.upper().replace('J', 'I'))
    text = ''.join(filtered_text)
    
    pairs = []
    inserted_indices = [] 
    i = 0
    char_count = 0 
    
    while i < len(text):
        a = text[i]
        if i + 1 < len(text):
            b = text[i + 1]
            if a == b:
                if a == sep1: pairs.append(a + sep2)
                else: pairs.append(a + sep1)
                inserted_indices.append(char_count + 1)
                i += 1
                char_count += 2
            else:
                pairs.append(a + b)
                i += 2
                char_count += 2
        else:
            if a == sep1: pairs.append(a + sep2) 
            else: pairs.append(a + sep1) 
            inserted_indices.append(char_count + 1)
            i += 1
            char_count += 2
    
    return pairs, inserted_indices

def process_plaintext_6x6(text, sep1='X', sep2='Y'):
    """Xử lý văn bản 6x6: Tách cặp, chèn sep1/sep2 nếu trùng hoặc lẻ"""
    text = ''.join([c.upper() for c in text if is_ascii_alnum(c)])
    
    pairs = []
    inserted_indices = [] 
    i = 0
    char_count = 0
    
    while i < len(text):
        a = text[i]
        if i + 1 < len(text):
            b = text[i + 1]
            if a == b:
                if a == sep1: pairs.append(a + sep2)
                else: pairs.append(a + sep1)
                inserted_indices.append(char_count + 1)
                i += 1
                char_count += 2
            else:
                pairs.append(a + b)
                i += 2
                char_count += 2
        else:
            if a == sep1: pairs.append(a + sep2) 
            else: pairs.append(a + sep1) 
            inserted_indices.append(char_count + 1)
            i += 1
            char_count += 2
    
    return pairs, inserted_indices

# --- CÁC HÀM TÍNH TOÁN ---

def encrypt_pair(matrix, a, b):
    row_a, col_a = find_position(matrix, a)
    row_b, col_b = find_position(matrix, b)
    if row_a is None or row_b is None: return a + b
    
    size = len(matrix)
    if row_a == row_b: 
        return matrix[row_a][(col_a + 1) % size] + matrix[row_b][(col_b + 1) % size]
    elif col_a == col_b: 
        return matrix[(row_a + 1) % size][col_a] + matrix[(row_b + 1) % size][col_b]
    else: 
        return matrix[row_a][col_b] + matrix[row_b][col_a]

def decrypt_pair(matrix, a, b):
    row_a, col_a = find_position(matrix, a)
    row_b, col_b = find_position(matrix, b)
    if row_a is None or row_b is None: return a + b
    
    size = len(matrix)
    if row_a == row_b: 
        return matrix[row_a][(col_a - 1) % size] + matrix[row_b][(col_b - 1) % size]
    elif col_a == col_b: 
        return matrix[(row_a - 1) % size][col_a] + matrix[(row_b - 1) % size][col_b]
    else: 
        return matrix[row_a][col_b] + matrix[row_b][col_a]

