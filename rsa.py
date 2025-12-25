import random
import base64
import sys

# --- CÁC HÀM TOÁN HỌC BỔ TRỢ (HELPER FUNCTIONS) ---

def is_prime(n, k=5):
    """Kiểm tra số nguyên tố (Miller-Rabin test)"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    # Tìm r và d sao cho n - 1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(bits):
    """Tạo số nguyên tố lớn với số bit cho trước"""
    while True:
        n = random.getrandbits(bits)
        # Đảm bảo n là số lẻ và đủ độ dài bit
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    """Tìm nghịch đảo modular (Extended Euclidean Algorithm)"""
    d = 0
    x1, x2, x3 = 1, 0, phi
    y1, y2, y3 = 0, 1, e
    while y3 > 1:
        q = x3 // y3
        x3, y3 = y3, x3 % y3
        x1, y1 = y1, x1 - q * y1
        x2, y2 = y2, x2 - q * y2
    return y2 if y2 > 0 else y2 + phi

def int_to_bytes(i):
    """Chuyển số nguyên thành bytes"""
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder='big')

def bytes_to_int(b):
    """Chuyển bytes thành số nguyên"""
    return int.from_bytes(b, byteorder='big')

# --- CLASS GIẢ LẬP ĐỐI TƯỢNG KEY (ĐỂ TƯƠNG THÍCH GIAO DIỆN) ---

class MyRSAPublicKey:
    def __init__(self, n, e):
        self.n = n
        self.e = e

class MyRSAPrivateKey:
    def __init__(self, n, d, public_key):
        self.n = n
        self.d = d
        self._public_key = public_key

    def public_key(self):
        return self._public_key

# --- CÁC HÀM XỬ LÝ LOGIC RSA (THEO YÊU CẦU CỦA BẠN) ---

def generate_key_pair(key_size=1024):
    """
    Tạo cặp khóa RSA (public và private)
    Hỗ trợ: 512, 1024, 2048 bits
    Returns: (private_key, public_key) objects
    """
    # 1. Kiểm tra kích thước khóa hợp lệ
    if key_size not in [512, 1024, 2048]:
        # Nếu giao diện gửi số khác, ta mặc định về 1024 hoặc báo lỗi
        # Ở đây mình sẽ ép về giá trị gần nhất hoặc raise lỗi tùy bạn chọn.
        # Code này sẽ báo lỗi để bạn biết logic giao diện có sai không.
        raise ValueError("Chỉ hỗ trợ kích thước khóa: 512, 1024, 2048 bits")

    e = 65537
    
    # Chia đôi số bit cho p và q
    p_bits = key_size // 2
    q_bits = key_size - p_bits

    # 2. Vòng lặp tạo số nguyên tố
    while True:
        p = generate_large_prime(p_bits)
        q = generate_large_prime(q_bits)
        
        # Đảm bảo p và q khác nhau và tích n có độ dài bit ĐÚNG bằng key_size
        # (Đôi khi tích 2 số 512 bit có thể ra 1023 bit hoặc 1025 bit)
        if p != q:
            n = p * q
            if n.bit_length() == key_size:
                break
            
    phi = (p - 1) * (q - 1)
    
    # 3. Tính d (nghịch đảo modular)
    try:
        d = mod_inverse(e, phi)
    except:
        # Nếu e và phi không nguyên tố cùng nhau (rất hiếm), chạy lại
        return generate_key_pair(key_size)

    # 4. Đóng gói vào class giả lập
    public_key = MyRSAPublicKey(n, e)
    private_key = MyRSAPrivateKey(n, d, public_key)
    
    return private_key, public_key


def serialize_public_key(public_key):
    """
    Chuyển public key thành định dạng PEM string (Custom format)
    """
    # Format: n|e -> encode base64
    raw_data = f"{public_key.n}|{public_key.e}".encode('utf-8')
    b64_data = base64.b64encode(raw_data).decode('utf-8')
    return f"-----BEGIN PUBLIC KEY-----\n{b64_data}\n-----END PUBLIC KEY-----"


def serialize_private_key(private_key):
    """
    Chuyển private key thành định dạng PEM string (Custom format)
    """
    # Format: n|d -> encode base64
    raw_data = f"{private_key.n}|{private_key.d}".encode('utf-8')
    b64_data = base64.b64encode(raw_data).decode('utf-8')
    return f"-----BEGIN PRIVATE KEY-----\n{b64_data}\n-----END PRIVATE KEY-----"


def load_public_key(pem_string):
    """
    Load public key từ PEM string
    """
    try:
        lines = pem_string.strip().split('\n')
        # Lấy nội dung giữa header và footer
        b64_data = "".join([line for line in lines if "-----" not in line])
        raw_data = base64.b64decode(b64_data).decode('utf-8')
        n_str, e_str = raw_data.split('|')
        return MyRSAPublicKey(int(n_str), int(e_str))
    except Exception as e:
        raise ValueError("Invalid Public Key Format")


def load_private_key(pem_string):
    """
    Load private key từ PEM string
    """
    try:
        lines = pem_string.strip().split('\n')
        b64_data = "".join([line for line in lines if "-----" not in line])
        raw_data = base64.b64decode(b64_data).decode('utf-8')
        n_str, d_str = raw_data.split('|')
        n = int(n_str)
        d = int(d_str)
        # Tái tạo public key từ private key (e mặc định là 65537 nếu không lưu)
        # Lưu ý: Nếu muốn chính xác tuyệt đối, cần lưu cả e trong private key, 
        # nhưng ở đây ta giả định e=65537 để đơn giản hoặc tạo đối tượng dummy.
        pub_key = MyRSAPublicKey(n, 65537) 
        return MyRSAPrivateKey(n, d, pub_key)
    except Exception as e:
        raise ValueError("Invalid Private Key Format")


def encrypt(plaintext, public_key):
    """
    Mã hóa văn bản bằng public key (có Padding PKCS#1 v1.5)
    Returns: base64 encoded string
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    
    n = public_key.n
    e = public_key.e
    k = (n.bit_length() + 7) // 8 # Độ dài byte của key (ví dụ 256 bytes cho 2048 bit)

    # --- PKCS#1 v1.5 Padding ---
    # Cấu trúc: 00 02 [padding ngẫu nhiên khác 0] 00 [message]
    if len(plaintext) > k - 11:
        raise ValueError("Message too long for RSA Key size")
    
    pad_len = k - len(plaintext) - 3
    padding = bytearray()
    while len(padding) < pad_len:
        b = random.randint(1, 255) # Non-zero bytes
        padding.append(b)
        
    padded_msg = b'\x00\x02' + padding + b'\x00' + plaintext
    
    # --- Mã hóa RSA: c = m^e mod n ---
    m_int = bytes_to_int(padded_msg)
    c_int = pow(m_int, e, n)
    
    c_bytes = int_to_bytes(c_int)
    return base64.b64encode(c_bytes).decode('utf-8')


def decrypt(ciphertext_base64, private_key):
    """
    Giải mã văn bản bằng private key (Gỡ Padding PKCS#1 v1.5)
    Returns: plaintext string
    """
    try:
        ciphertext = base64.b64decode(ciphertext_base64)
        c_int = bytes_to_int(ciphertext)
        n = private_key.n
        d = private_key.d
        k = (n.bit_length() + 7) // 8

        # --- Giải mã RSA: m = c^d mod n ---
        m_int = pow(c_int, d, n)
        decrypted_bytes = int_to_bytes(m_int)

        # Đảm bảo độ dài byte đúng bằng k (nếu thiếu, thêm 0 ở đầu)
        if len(decrypted_bytes) < k:
            decrypted_bytes = b'\x00' * (k - len(decrypted_bytes)) + decrypted_bytes

        # --- Gỡ Padding PKCS#1 v1.5 ---
        # Kiểm tra byte đầu phải là 00 02
        if decrypted_bytes[0:2] != b'\x00\x02':
             # Xử lý trường hợp int_to_bytes có thể mất byte 00 đầu tiên
             # Nếu byte đầu là 02, ta chấp nhận
             if decrypted_bytes[0] == 2:
                 decrypted_bytes = b'\x00' + decrypted_bytes
             else:
                raise ValueError("Decryption failed (Invalid Padding)")

        # Tìm byte 00 tách biệt padding và message
        try:
            sep_index = decrypted_bytes.index(b'\x00', 2)
        except ValueError:
            raise ValueError("Decryption failed (No separator)")
            
        return decrypted_bytes[sep_index+1:].decode('utf-8')
        
    except Exception as e:
        return "Error: Decryption Failed or Key Mismatch"