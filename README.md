# Encryption & Decryption - Playfair & RSA

Chương trình mã hóa và giải mã sử dụng hai thuật toán: **Playfair** và **RSA**.

## Cấu trúc dự án

```
Encryption-Decryption/
├── main_ui.py      # File giao diện chính (kết hợp Playfair và RSA)
├── playfair.py     # File logic thuật toán Playfair
├── rsa.py          # File logic thuật toán RSA
├── requirements.txt # Các thư viện cần thiết
└── README.md       # File hướng dẫn
```

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Chạy chương trình

```bash
python main_ui.py
```

## Tính năng

### Playfair Cipher
- Mã hóa và giải mã văn bản
- Hỗ trợ ma trận 5x5 và 6x6
- Nhập từ file hoặc text trực tiếp
- Hiển thị ma trận và các bước xử lý

### RSA
- Tạo cặp khóa (public/private)
- Mã hóa và giải mã văn bản
- Hỗ trợ kích thước khóa: 1024, 2048, 4096 bits
- Import/Export khóa
- Nhập từ file hoặc text trực tiếp

## Lưu ý

- Các thuật toán được giữ nguyên logic gốc, không thay đổi
- File logic (`playfair.py`, `rsa.py`) chỉ chứa các hàm xử lý thuật toán
- File giao diện (`main_ui.py`) xử lý tất cả UI và tương tác người dùng

# Playfair-RSA
# Playfair-RSA
