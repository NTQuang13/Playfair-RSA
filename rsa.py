# --- CÁC HÀM XỬ LÝ LOGIC RSA ---

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64


def generate_key_pair(key_size=2048):
    """
    Tạo cặp khóa RSA (public và private)
    key_size: Kích thước khóa (1024, 2048, 4096)
    Returns: (private_key, public_key) objects
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key):
    """
    Chuyển public key thành định dạng PEM string
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')


def serialize_private_key(private_key):
    """
    Chuyển private key thành định dạng PEM string
    """
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')


def load_public_key(pem_string):
    """
    Load public key từ PEM string
    """
    return serialization.load_pem_public_key(
        pem_string.encode('utf-8'),
        backend=default_backend()
    )


def load_private_key(pem_string):
    """
    Load private key từ PEM string
    """
    return serialization.load_pem_private_key(
        pem_string.encode('utf-8'),
        password=None,
        backend=default_backend()
    )


def encrypt(plaintext, public_key):
    """
    Mã hóa văn bản bằng public key
    plaintext: string hoặc bytes
    public_key: RSA public key object
    Returns: base64 encoded string
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    
    ciphertext = public_key.encrypt(
        plaintext,
        padding.PKCS1v15()
    )
    
    return base64.b64encode(ciphertext).decode('utf-8')


def decrypt(ciphertext_base64, private_key):
    """
    Giải mã văn bản bằng private key
    ciphertext_base64: base64 encoded string
    private_key: RSA private key object
    Returns: plaintext string
    """
    ciphertext = base64.b64decode(ciphertext_base64)
    
    plaintext = private_key.decrypt(
        ciphertext,
        padding.PKCS1v15()
    )
    
    return plaintext.decode('utf-8')

