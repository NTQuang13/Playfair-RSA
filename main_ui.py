import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton,
    QButtonGroup, QFileDialog, QFrame, QMessageBox, 
    QStackedWidget, QGraphicsDropShadowEffect, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt, QRegExp, QPointF
from PyQt5.QtGui import QFont, QColor, QCursor, QPainter, QPen, QBrush, QPolygonF, QRegExpValidator

# Import logic
import playfair
import rsa

# ==================== CUSTOM COMBOBOX ====================
class CustomComboBox(QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        arrow_x = self.width() - 20
        arrow_y = self.height() // 2
        
        painter.setPen(QPen(QColor("#6b7280"), 2))
        painter.setBrush(QBrush(QColor("#6b7280")))
        
        polygon = QPolygonF()
        polygon.append(QPointF(arrow_x, arrow_y - 4))
        polygon.append(QPointF(arrow_x + 6, arrow_y - 4))
        polygon.append(QPointF(arrow_x + 3, arrow_y + 3))
        
        painter.drawPolygon(polygon)

# ==================== MAIN WINDOW ====================
class CryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encryption & Decryption - Playfair & RSA")
        self.setGeometry(100, 50, 1400, 800)
        
        # State
        self.current_algorithm = 'playfair'  # 'playfair' or 'rsa'
        
        # Playfair state
        self.playfair_matrix = []
        self.playfair_matrix_size = '5'
        self.playfair_mode = 'encrypt'
        self.playfair_input_mode = 'file'
        self.playfair_file_content = ''
        self.playfair_file_path = ''
        
        # RSA state
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.rsa_private_key_pem = ""
        self.rsa_public_key_pem = ""
        self.rsa_input_mode = 'file'
        self.rsa_file_path = ''
        self.rsa_file_content = ''
        
        self.init_ui()
        self.setup_connections()
        self.show_playfair()

    def init_ui(self):
        self.setStyleSheet("background-color: #e5e7eb; font-family: 'Segoe UI', sans-serif;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # --- HEADER WITH ALGORITHM SELECTION ---
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 15px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("Encryption & Decryption")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1f2937;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Algorithm selection buttons
        self.btn_playfair = QPushButton("Playfair")
        self.btn_rsa = QPushButton("RSA")
        self.btn_playfair.setFixedSize(150, 45)
        self.btn_rsa.setFixedSize(150, 45)
        self.btn_playfair.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_rsa.setCursor(QCursor(Qt.PointingHandCursor))
        
        header_layout.addWidget(self.btn_playfair)
        header_layout.addWidget(self.btn_rsa)
        
        main_layout.addWidget(header_frame)
        
        # --- STACKED WIDGET FOR ALGORITHMS ---
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Create Playfair and RSA pages
        self.playfair_page = self.create_playfair_page()
        self.rsa_page = self.create_rsa_page()
        
        self.stack.addWidget(self.playfair_page)
        self.stack.addWidget(self.rsa_page)
        
        self.update_algorithm_buttons()

    # ==================== PLAYFAIR PAGE ====================
    def create_playfair_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main card
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 12px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Playfair Cipher - Encrypt & Decrypt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 10px;")
        card_layout.addWidget(title)
        
        # Content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Separators
        sep_container = QHBoxLayout()
        sep_container.setSpacing(15)
        
        sep_validator = QRegExpValidator(QRegExp("[A-Za-z]"))
        
        sep1_layout = QVBoxLayout()
        label_sep1 = QLabel("First Separator:")
        label_sep1.setStyleSheet("font-weight: 600; color: #374151;")
        self.playfair_sep1 = QLineEdit("X")
        self.playfair_sep1.setMaxLength(1)
        self.playfair_sep1.setValidator(sep_validator)
        self.style_input(self.playfair_sep1)
        self.playfair_sep1.textEdited.connect(lambda t: self.handle_separator(self.playfair_sep1, self.playfair_sep2, t))
        sep1_layout.addWidget(label_sep1)
        sep1_layout.addWidget(self.playfair_sep1)
        
        sep2_layout = QVBoxLayout()
        label_sep2 = QLabel("Second Separator:")
        label_sep2.setStyleSheet("font-weight: 600; color: #374151;")
        self.playfair_sep2 = QLineEdit("Y")
        self.playfair_sep2.setMaxLength(1)
        self.playfair_sep2.setValidator(sep_validator)
        self.style_input(self.playfair_sep2)
        self.playfair_sep2.textEdited.connect(lambda t: self.handle_separator(self.playfair_sep2, self.playfair_sep1, t))
        sep2_layout.addWidget(label_sep2)
        sep2_layout.addWidget(self.playfair_sep2)
        
        sep_container.addLayout(sep1_layout)
        sep_container.addLayout(sep2_layout)
        left_panel.addLayout(sep_container)
        
        # Key
        key_label = QLabel("Key:")
        key_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.playfair_key = QLineEdit()
        self.style_input(self.playfair_key)
        self.playfair_key.setPlaceholderText("Enter key...")
        self.playfair_key.textEdited.connect(self.on_playfair_key_edited)
        left_panel.addWidget(key_label)
        left_panel.addWidget(self.playfair_key)
        
        # Matrix
        matrix_area = QHBoxLayout()
        self.playfair_matrix_frame = QFrame()
        self.playfair_matrix_frame.setStyleSheet("border: 1px solid #d1d5db; border-radius: 6px; background-color: #f9fafb; padding: 10px;")
        self.playfair_matrix_layout = QVBoxLayout(self.playfair_matrix_frame)
        matrix_title = QLabel("Matrix:")
        matrix_title.setStyleSheet("font-size: 17px; font-weight: 600; color: #374151; margin-bottom: 5px;")
        self.playfair_matrix_layout.addWidget(matrix_title)
        self.playfair_grid = QGridLayout()
        self.playfair_grid.setSpacing(5)
        self.playfair_matrix_layout.addLayout(self.playfair_grid)
        
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.playfair_radio_5x5 = QRadioButton("5x5")
        self.playfair_radio_6x6 = QRadioButton("6x6")
        self.playfair_radio_5x5.setChecked(True)
        self.style_radio(self.playfair_radio_5x5)
        self.style_radio(self.playfair_radio_6x6)
        self.playfair_size_group = QButtonGroup()
        self.playfair_size_group.addButton(self.playfair_radio_5x5, 5)
        self.playfair_size_group.addButton(self.playfair_radio_6x6, 6)
        self.playfair_size_group.buttonClicked.connect(self.on_playfair_size_change)
        size_layout.addWidget(self.playfair_radio_5x5)
        size_layout.addWidget(self.playfair_radio_6x6)
        size_layout.addStretch()
        
        matrix_area.addWidget(self.playfair_matrix_frame, 1)
        matrix_area.addLayout(size_layout)
        left_panel.addLayout(matrix_area)
        
        # Mode
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: 600; color: #374151;")
        left_panel.addWidget(mode_label)
        mode_radios = QHBoxLayout()
        self.playfair_radio_encrypt = QRadioButton("Encrypt")
        self.playfair_radio_decrypt = QRadioButton("Decrypt")
        self.playfair_radio_encrypt.setChecked(True)
        self.style_radio(self.playfair_radio_encrypt)
        self.style_radio(self.playfair_radio_decrypt)
        self.playfair_mode_group = QButtonGroup()
        self.playfair_mode_group.addButton(self.playfair_radio_encrypt)
        self.playfair_mode_group.addButton(self.playfair_radio_decrypt)
        self.playfair_mode_group.buttonClicked.connect(self.update_playfair_labels)
        mode_radios.addWidget(self.playfair_radio_encrypt)
        mode_radios.addWidget(self.playfair_radio_decrypt)
        mode_radios.addStretch()
        left_panel.addLayout(mode_radios)
        
        left_panel.addStretch()
        
        # Buttons
        self.playfair_btn_run = self.create_button("▶ Execute", "#16a34a", "#15803d")
        self.playfair_btn_clear = self.create_button("🗑 Clear All", "#ef4444", "#dc2626")
        left_panel.addWidget(self.playfair_btn_run)
        left_panel.addWidget(self.playfair_btn_clear)
        
        content_layout.addLayout(left_panel, 3)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Input tabs
        input_tab_layout = QVBoxLayout()
        tab_header = QHBoxLayout()
        self.playfair_btn_tab_file = QPushButton("File Input")
        self.playfair_btn_tab_text = QPushButton("Text Input")
        self.playfair_btn_tab_file.setCursor(QCursor(Qt.PointingHandCursor))
        self.playfair_btn_tab_text.setCursor(QCursor(Qt.PointingHandCursor))
        self.playfair_btn_tab_file.setFixedHeight(38)
        self.playfair_btn_tab_text.setFixedHeight(38)
        tab_header.addWidget(self.playfair_btn_tab_file)
        tab_header.addWidget(self.playfair_btn_tab_text)
        tab_header.addStretch()
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e5e7eb;")
        input_tab_layout.addLayout(tab_header)
        input_tab_layout.addWidget(line)
        
        self.playfair_input_stack = QStackedWidget()
        
        # File input page
        page_file = QWidget()
        page_file_layout = QVBoxLayout(page_file)
        page_file_layout.setContentsMargins(0, 5, 0, 0)
        lbl_path = QLabel("Path:")
        lbl_path.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        page_file_layout.addWidget(lbl_path)
        file_row = QHBoxLayout()
        self.playfair_file_display = QLineEdit()
        self.playfair_file_display.setReadOnly(True)
        self.playfair_file_display.setPlaceholderText("Select input file...")
        self.style_input(self.playfair_file_display)
        self.playfair_btn_browse = self.create_button("Browse", "#a16207", "#854d0e")
        self.playfair_btn_browse.setFixedSize(100, 44)
        file_row.addWidget(self.playfair_file_display)
        file_row.addWidget(self.playfair_btn_browse)
        page_file_layout.addLayout(file_row)
        page_file_layout.addStretch()
        
        # Text input page
        page_text = QWidget()
        page_text_layout = QVBoxLayout(page_text)
        page_text_layout.setContentsMargins(0, 5, 0, 0)
        lbl_text = QLabel("Text:")
        lbl_text.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        page_text_layout.addWidget(lbl_text)
        self.playfair_text_area = QTextEdit()
        self.playfair_text_area.setPlaceholderText("Enter text here...")
        self.style_textarea(self.playfair_text_area, read_only=False)
        self.playfair_text_area.setFixedHeight(80)
        page_text_layout.addWidget(self.playfair_text_area)
        page_text_layout.addStretch()
        
        self.playfair_input_stack.addWidget(page_file)
        self.playfair_input_stack.addWidget(page_text)
        input_tab_layout.addWidget(self.playfair_input_stack)
        right_panel.addLayout(input_tab_layout)
        
        # Output
        self.playfair_lbl_pairs = QLabel("Plaintext Pairs:")
        self.playfair_lbl_pairs.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        self.playfair_out_pairs = QTextEdit()
        self.style_textarea(self.playfair_out_pairs, read_only=True)
        
        self.playfair_lbl_stream = QLabel("Ciphertext Stream:")
        self.playfair_lbl_stream.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        self.playfair_out_stream = QTextEdit()
        self.style_textarea(self.playfair_out_stream, read_only=True)
        
        self.playfair_lbl_result = QLabel("Encryption Result:")
        self.playfair_lbl_result.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        self.playfair_out_result = QTextEdit()
        self.style_textarea(self.playfair_out_result, read_only=True)
        self.playfair_out_result.setFixedHeight(130)
        
        right_panel.addWidget(self.playfair_lbl_pairs)
        right_panel.addWidget(self.playfair_out_pairs)
        right_panel.addWidget(self.playfair_lbl_stream)
        right_panel.addWidget(self.playfair_out_stream)
        right_panel.addWidget(self.playfair_lbl_result)
        right_panel.addWidget(self.playfair_out_result)
        
        # Buttons
        bottom_btns = QHBoxLayout()
        self.playfair_btn_save = self.create_button("💾 Save", "#2563eb", "#1d4ed8")
        self.playfair_btn_info = self.create_button("💡 Learn Algorithm", "#efb114", "#d97706")
        bottom_btns.addWidget(self.playfair_btn_save)
        bottom_btns.addWidget(self.playfair_btn_info)
        right_panel.addLayout(bottom_btns)
        
        content_layout.addLayout(right_panel, 7)
        card_layout.addLayout(content_layout)
        
        layout.addWidget(card)
        return page

    # ==================== RSA PAGE ====================
    def create_rsa_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main card
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 12px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("RSA - Encrypt & Decrypt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1f2937; margin-bottom: 10px;")
        card_layout.addWidget(title)
        
        # Content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Key size
        size_layout = QVBoxLayout()
        size_layout.setSpacing(5)
        label_size = QLabel("Key Size:")
        label_size.setStyleSheet("font-weight: 600; color: #374151; font-size: 20px;")
        size_layout.addWidget(label_size)
        self.rsa_key_size_combo = CustomComboBox()
        self.rsa_key_size_combo.addItems(["512 bits", "1024 bits", "2048 bits"])
        self.rsa_key_size_combo.setCurrentIndex(1)
        self.rsa_key_size_combo.setFixedHeight(45)
        self.rsa_key_size_combo.setStyleSheet("""
            QComboBox { border: 1px solid #d1d5db; border-radius: 6px; padding: 10px;
                background-color: white; color: #1f2937; font-size: 16px; }
            QComboBox::down-arrow { width: 0px; height: 0px; border: none; image: none; }
            QComboBox::drop-down { border: none; width: 25px; }
            QComboBox:focus { border: 2px solid #3b82f6; padding: 9px; }
        """)
        size_layout.addWidget(self.rsa_key_size_combo)
        left_panel.addLayout(size_layout)
        
        # Generate button
        self.rsa_btn_generate = self.create_button("Generate New Keys", "#10b981", "#059669", height=45)
        left_panel.addWidget(self.rsa_btn_generate)
        
        # Import buttons
        import_layout = QVBoxLayout()
        import_layout.setSpacing(5)
        label_import = QLabel("Key Import:")
        label_import.setStyleSheet("font-weight: 600; color: #374151; font-size: 20px;")
        import_layout.addWidget(label_import)
        import_buttons = QHBoxLayout()
        import_buttons.setSpacing(8)
        self.rsa_btn_import_public = self.create_button("Import Public", "#3b82f6", "#2563eb", height=38)
        self.rsa_btn_import_private = self.create_button("Import Private", "#3b82f6", "#2563eb", height=38)
        import_buttons.addWidget(self.rsa_btn_import_public)
        import_buttons.addWidget(self.rsa_btn_import_private)
        import_layout.addLayout(import_buttons)
        left_panel.addLayout(import_layout)
        
        # Key display
        key_display_layout = QVBoxLayout()
        key_display_layout.setSpacing(5)
        label_keys = QLabel("Keys:")
        label_keys.setStyleSheet("font-weight: 600; color: #374151; font-size: 20px;")
        key_display_layout.addWidget(label_keys)
        
        # Public key
        public_key_label = QLabel("Public Key:")
        public_key_label.setStyleSheet("font-size: 16px; color: #374151;")
        key_display_layout.addWidget(public_key_label)
        self.rsa_public_key_display = QTextEdit()
        self.rsa_public_key_display.setPlaceholderText("Public key will appear here...")
        self.rsa_public_key_display.setReadOnly(True)
        self.style_textarea(self.rsa_public_key_display, read_only=True)
        self.rsa_public_key_display.setFixedHeight(90)
        key_display_layout.addWidget(self.rsa_public_key_display)
        
        pub_btn_layout = QHBoxLayout()
        pub_btn_layout.setSpacing(6)
        self.rsa_btn_copy_public = self.create_button("Copy", "#6b7280", "#4b5563", height=32)
        self.rsa_btn_save_public = self.create_button("Save", "#6b7280", "#4b5563", height=32)
        pub_btn_layout.addWidget(self.rsa_btn_copy_public)
        pub_btn_layout.addWidget(self.rsa_btn_save_public)
        key_display_layout.addLayout(pub_btn_layout)
        
        key_display_layout.addWidget(QLabel(""))  # Spacer
        
        # Private key
        private_key_label = QLabel("Private Key:")
        private_key_label.setStyleSheet("font-size: 16px; color: #374151;")
        key_display_layout.addWidget(private_key_label)
        self.rsa_private_key_display = QTextEdit()
        self.rsa_private_key_display.setPlaceholderText("Private key will appear here...")
        self.rsa_private_key_display.setReadOnly(True)
        self.style_textarea(self.rsa_private_key_display, read_only=True)
        self.rsa_private_key_display.setFixedHeight(90)
        key_display_layout.addWidget(self.rsa_private_key_display)
        
        priv_btn_layout = QHBoxLayout()
        priv_btn_layout.setSpacing(6)
        self.rsa_btn_copy_private = self.create_button("Copy", "#6b7280", "#4b5563", height=32)
        self.rsa_btn_save_private = self.create_button("Save", "#6b7280", "#4b5563", height=32)
        priv_btn_layout.addWidget(self.rsa_btn_copy_private)
        priv_btn_layout.addWidget(self.rsa_btn_save_private)
        key_display_layout.addLayout(priv_btn_layout)
        
        left_panel.addLayout(key_display_layout, 1)
        
        # Mode
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(3)
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: 600; color: #374151; font-size: 20px;")
        mode_layout.addWidget(mode_label)
        mode_radios = QHBoxLayout()
        mode_radios.setSpacing(25)
        self.rsa_radio_encrypt = QRadioButton("Encrypt")
        self.rsa_radio_decrypt = QRadioButton("Decrypt")
        self.rsa_radio_encrypt.setChecked(True)
        radio_style = """
            QRadioButton { color: #374151; spacing: 10px; font-size: 18px; background-color: transparent; padding: 6px 0px; }
            QRadioButton::indicator { width: 20px; height: 20px; border-radius: 10px; border: 2px solid #d1d5db; background-color: white; }
            QRadioButton::indicator:checked { background-color: #3b82f6; border: 2px solid #3b82f6; }
            QRadioButton::indicator:checked:hover { background-color: #2563eb; border: 2px solid #2563eb; }
            QRadioButton::indicator:hover { border: 2px solid #94a3b8; }
        """
        self.rsa_radio_encrypt.setStyleSheet(radio_style)
        self.rsa_radio_decrypt.setStyleSheet(radio_style)
        self.rsa_mode_group = QButtonGroup()
        self.rsa_mode_group.addButton(self.rsa_radio_encrypt)
        self.rsa_mode_group.addButton(self.rsa_radio_decrypt)
        mode_radios.addWidget(self.rsa_radio_encrypt)
        mode_radios.addWidget(self.rsa_radio_decrypt)
        mode_radios.addStretch()
        mode_layout.addLayout(mode_radios)
        left_panel.addLayout(mode_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        self.rsa_btn_execute = self.create_button("▶ Execute", "#10b981", "#059669", height=45)
        self.rsa_btn_clear = self.create_button("🗑 Clear All", "#ef4444", "#dc2626", height=45)
        button_layout.addWidget(self.rsa_btn_execute)
        button_layout.addWidget(self.rsa_btn_clear)
        left_panel.addLayout(button_layout)
        left_panel.addStretch()
        
        content_layout.addLayout(left_panel, 3)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # Input tabs
        input_tab_layout = QVBoxLayout()
        input_tab_layout.setSpacing(5)
        tab_header = QHBoxLayout()
        self.rsa_btn_tab_file = QPushButton("File Input")
        self.rsa_btn_tab_text = QPushButton("Text Input")
        self.rsa_btn_tab_file.setCursor(QCursor(Qt.PointingHandCursor))
        self.rsa_btn_tab_text.setCursor(QCursor(Qt.PointingHandCursor))
        self.rsa_btn_tab_file.setFixedHeight(40)
        self.rsa_btn_tab_text.setFixedHeight(40)
        tab_header.addWidget(self.rsa_btn_tab_file)
        tab_header.addWidget(self.rsa_btn_tab_text)
        tab_header.addStretch()
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e5e7eb;")
        input_tab_layout.addLayout(tab_header)
        input_tab_layout.addWidget(line)
        
        self.rsa_input_stack = QStackedWidget()
        
        # File input page
        page_file = QWidget()
        page_file_layout = QVBoxLayout(page_file)
        page_file_layout.setContentsMargins(0, 5, 0, 0)
        lbl_path = QLabel("Path:")
        lbl_path.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        page_file_layout.addWidget(lbl_path)
        file_row = QHBoxLayout()
        self.rsa_file_display = QLineEdit()
        self.rsa_file_display.setReadOnly(True)
        self.rsa_file_display.setPlaceholderText("Select input file...")
        self.style_input(self.rsa_file_display)
        self.rsa_btn_browse = self.create_button("Browse", "#a16207", "#854d0e", height=40)
        self.rsa_btn_browse.setFixedWidth(90)
        file_row.addWidget(self.rsa_file_display)
        file_row.addWidget(self.rsa_btn_browse)
        page_file_layout.addLayout(file_row)
        page_file_layout.addStretch(1)
        
        # Text input page
        page_text = QWidget()
        page_text_layout = QVBoxLayout(page_text)
        page_text_layout.setContentsMargins(0, 5, 0, 0)
        lbl_text = QLabel("Text:")
        lbl_text.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        page_text_layout.addWidget(lbl_text)
        self.rsa_text_area = QTextEdit()
        self.rsa_text_area.setPlaceholderText("Enter text here...")
        self.style_textarea(self.rsa_text_area, read_only=False)
        self.rsa_text_area.setFixedHeight(120)
        page_text_layout.addWidget(self.rsa_text_area, 1)
        page_text_layout.addStretch()
        
        self.rsa_input_stack.addWidget(page_file)
        self.rsa_input_stack.addWidget(page_text)
        input_tab_layout.addWidget(self.rsa_input_stack, 1)
        right_panel.addLayout(input_tab_layout)
        
        # Result
        result_layout = QVBoxLayout()
        result_layout.setSpacing(5)
        label_result = QLabel("Result:")
        label_result.setStyleSheet("font-size: 20px; font-weight: 600; color: #374151;")
        result_layout.addWidget(label_result)
        self.rsa_output_text = QTextEdit()
        self.rsa_output_text.setPlaceholderText("Result will appear here...")
        self.rsa_output_text.setReadOnly(True)
        self.style_textarea(self.rsa_output_text, read_only=True)
        self.rsa_output_text.setFixedHeight(120)
        result_layout.addWidget(self.rsa_output_text, 1)
        right_panel.addLayout(result_layout, 1)
        
        # Buttons
        bottom_btns = QHBoxLayout()
        bottom_btns.setSpacing(8)
        self.rsa_btn_save_result = self.create_button("💾 Save Result", "#2563eb", "#1d4ed8", height=42)
        self.rsa_btn_info = self.create_button("💡 Learn Algorithm", "#efb013", "#d97706", height=42)
        bottom_btns.addWidget(self.rsa_btn_save_result)
        bottom_btns.addWidget(self.rsa_btn_info)
        right_panel.addLayout(bottom_btns)
        
        content_layout.addLayout(right_panel, 7)
        card_layout.addLayout(content_layout)
        
        layout.addWidget(card)
        return page

    # ==================== HELPER METHODS ====================
    def create_button(self, text, color, hover, height=40):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setFixedHeight(height)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; font-weight: 600; font-size: 15px;
                border-radius: 6px; border: none; padding: 0px 12px; }}
            QPushButton:hover {{ background-color: {hover}; }}
        """)
        return btn

    def style_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit { border: 1px solid #d1d5db; border-radius: 6px; padding: 6px 12px;
                color: #1f2937; background-color: white; }
            QLineEdit:focus { border: 2px solid #3b82f6; padding: 5px 11px; }
        """)

    def style_textarea(self, widget, read_only=False):
        bg_color = "#f9fafb" if read_only else "white"
        widget.setReadOnly(read_only)
        widget.setStyleSheet(f"""
            QTextEdit {{ border: 1px solid #d1d5db; border-radius: 6px; padding: 6px;
                color: #1f2937; background-color: {bg_color}; font-family: 'Consolas', monospace; }}
            QTextEdit:focus {{ border: 2px solid #3b82f6; }}
            QScrollBar:vertical {{ border: none; background-color: transparent; width: 8px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background-color: #cbd5e1; border-radius: 4px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background-color: #94a3b8; }}
        """)

    def style_radio(self, widget):
        widget.setStyleSheet("""
            QRadioButton { color: #374151; spacing: 8px; font-size: 17px; background-color: transparent; }
            QRadioButton::indicator { width: 16px; height: 16px; }
        """)

    def update_algorithm_buttons(self):
        if self.current_algorithm == 'playfair':
            self.btn_playfair.setStyleSheet("""
                QPushButton { background-color: #3b82f6; color: white; font-weight: bold;
                    border-radius: 6px; border: none; }
            """)
            self.btn_rsa.setStyleSheet("""
                QPushButton { background-color: #e5e7eb; color: #374151; font-weight: normal;
                    border-radius: 6px; border: none; }
                QPushButton:hover { background-color: #d1d5db; }
            """)
        else:
            self.btn_playfair.setStyleSheet("""
                QPushButton { background-color: #e5e7eb; color: #374151; font-weight: normal;
                    border-radius: 6px; border: none; }
                QPushButton:hover { background-color: #d1d5db; }
            """)
            self.btn_rsa.setStyleSheet("""
                QPushButton { background-color: #3b82f6; color: white; font-weight: bold;
                    border-radius: 6px; border: none; }
            """)

    def show_playfair(self):
        self.current_algorithm = 'playfair'
        self.stack.setCurrentIndex(0)
        self.update_algorithm_buttons()
        self.generate_and_show_playfair_matrix()

    def show_rsa(self):
        self.current_algorithm = 'rsa'
        self.stack.setCurrentIndex(1)
        self.update_algorithm_buttons()

    # ==================== PLAYFAIR METHODS ====================
    def handle_separator(self, current, other, text):
        if not text: return
        upper_text = text.upper()
        if text != upper_text:
            current.setText(upper_text)
        if upper_text == other.text():
            QMessageBox.warning(self, "Lỗi", "Hai ký tự Separator không được giống nhau!")
            current.setText("")

    def on_playfair_key_edited(self, text):
        upper_text = text.upper()
        if text != upper_text:
            self.playfair_key.setText(upper_text)
        self.generate_and_show_playfair_matrix()

    def on_playfair_size_change(self, btn):
        self.playfair_matrix_size = str(self.playfair_size_group.id(btn))
        self.update_playfair_key_validator()
        self.generate_and_show_playfair_matrix()

    def update_playfair_key_validator(self):
        key_text = self.playfair_key.text()
        if self.playfair_matrix_size == '5':
            regex = QRegExp("[A-Za-z]+")
            validator = QRegExpValidator(regex)
            self.playfair_key.setValidator(validator)
            cleaned = ''.join(c for c in key_text if playfair.is_ascii_letter(c))
            if cleaned != key_text:
                self.playfair_key.setText(cleaned)
        else:
            regex = QRegExp("[A-Za-z0-9]+")
            validator = QRegExpValidator(regex)
            self.playfair_key.setValidator(validator)
            cleaned = ''.join(c for c in key_text if playfair.is_ascii_alnum(c))
            if cleaned != key_text:
                self.playfair_key.setText(cleaned)

    def generate_and_show_playfair_matrix(self):
        key = self.playfair_key.text()
        if self.playfair_matrix_size == '5':
            self.playfair_matrix = playfair.generate_matrix_5x5(key)
        else:
            self.playfair_matrix = playfair.generate_matrix_6x6(key)
        self.render_playfair_matrix(self.playfair_matrix)

    def render_playfair_matrix(self, matrix_data):
        for i in reversed(range(self.playfair_grid.count())):
            self.playfair_grid.itemAt(i).widget().setParent(None)
        
        if not matrix_data:
            return

        for r, row in enumerate(matrix_data):
            for c, char in enumerate(row):
                cell = QLabel(char)
                cell.setFixedSize(40, 40)
                cell.setAlignment(Qt.AlignCenter)
                cell.setStyleSheet("""
                    QLabel { background-color: white; border: 1px solid #d1d5db;
                        color: #1f2937; font-family: 'Consolas', monospace; font-weight: bold;
                        border-radius: 4px; }
                """)
                self.playfair_grid.addWidget(cell, r, c)

    def update_playfair_labels(self):
        if self.playfair_radio_encrypt.isChecked():
            self.playfair_lbl_pairs.setText("Plaintext Pairs:")
            self.playfair_lbl_stream.setText("Ciphertext Stream:")
            self.playfair_lbl_result.setText("Encryption Result:")
        else:
            self.playfair_lbl_pairs.setText("Ciphertext Pairs:")
            self.playfair_lbl_stream.setText("Plaintext Stream:")
            self.playfair_lbl_result.setText("Decryption Result:")

    def update_playfair_input_tab_style(self):
        active_style = """
            QPushButton { color: #2563eb; font-weight: bold; border: none;
                border-bottom: 2px solid #2563eb; background-color: transparent;
                font-size: 20px; padding-bottom: 5px; }
        """
        inactive_style = """
            QPushButton { color: #4b5563; font-weight: normal; border: none;
                border-bottom: 2px solid transparent; background-color: transparent;
                font-size: 20px; padding-bottom: 5px; }
            QPushButton:hover { color: #1f2937; }
        """
        if self.playfair_input_mode == 'file':
            self.playfair_btn_tab_file.setStyleSheet(active_style)
            self.playfair_btn_tab_text.setStyleSheet(inactive_style)
            self.playfair_input_stack.setCurrentIndex(0)
        else:
            self.playfair_btn_tab_file.setStyleSheet(inactive_style)
            self.playfair_btn_tab_text.setStyleSheet(active_style)
            self.playfair_input_stack.setCurrentIndex(1)

    def playfair_switch_tab(self, mode):
        self.playfair_input_mode = mode
        self.update_playfair_input_tab_style()

    def playfair_browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "Text files (*.txt)")
        if fname:
            self.playfair_file_path = fname
            self.playfair_file_display.setText(fname)
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.playfair_file_content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    def playfair_run_cipher(self):
        if not self.playfair_matrix:
            QMessageBox.warning(self, "Warning", "Error creating matrix!")
            return
        
        sep1 = self.playfair_sep1.text()
        sep2 = self.playfair_sep2.text()

        if not sep1 or not sep2:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đủ ký tự cho cả 2 Separator!")
            return
        if sep1 == sep2:
            QMessageBox.warning(self, "Lỗi", "Hai Separator không được giống nhau!")
            return

        input_text = ""
        if self.playfair_input_mode == 'file':
            input_text = self.playfair_file_content
            if not input_text and not self.playfair_file_path:
                QMessageBox.warning(self, "Warning", "Please select a file!")
                return
        else:
            input_text = self.playfair_text_area.toPlainText()
            if not input_text:
                QMessageBox.warning(self, "Warning", "Please enter text!")
                return
        
        mode = 'encrypt' if self.playfair_radio_encrypt.isChecked() else 'decrypt'
        
        try:
            if self.playfair_matrix_size == '5':
                pairs, inserted_indices = playfair.process_plaintext_5x5(input_text, sep1=sep1, sep2=sep2)
            else:
                pairs, inserted_indices = playfair.process_plaintext_6x6(input_text, sep1=sep1, sep2=sep2)
            
            self.playfair_out_pairs.setText(' '.join(pairs))
            
            processed_pairs = []
            for pair in pairs:
                if len(pair) == 2:
                    if mode == 'encrypt':
                        processed_pairs.append(playfair.encrypt_pair(self.playfair_matrix, pair[0], pair[1]))
                    else:
                        processed_pairs.append(playfair.decrypt_pair(self.playfair_matrix, pair[0], pair[1]))
            
            output_stream = ''.join(processed_pairs)
            self.playfair_out_stream.setText(' '.join(processed_pairs))
            
            result = []
            idx = 0
            for char in input_text:
                is_valid = playfair.is_ascii_letter(char) if self.playfair_matrix_size == '5' else playfair.is_ascii_alnum(char)
                
                if is_valid:
                    if idx < len(output_stream):
                        c = output_stream[idx]
                        result.append(c.lower() if char.islower() else c)
                        idx += 1
                        while idx in inserted_indices and idx < len(output_stream):
                            result.append(output_stream[idx])
                            idx += 1
                else:
                    result.append(char)
            
            while idx < len(output_stream):
                result.append(output_stream[idx])
                idx += 1
                
            self.playfair_out_result.setText(''.join(result))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def playfair_clear_all(self):
        self.playfair_text_area.clear()
        self.playfair_file_display.clear()
        self.playfair_file_content = ''
        self.playfair_file_path = ''
        self.playfair_out_pairs.clear()
        self.playfair_out_stream.clear()
        self.playfair_out_result.clear()

    def playfair_save_file(self):
        content = self.playfair_out_result.toPlainText()
        if not content:
            QMessageBox.warning(self, "Warning", "No result to save!")
            return
        fname, _ = QFileDialog.getSaveFileName(self, 'Save file', 'result.txt', "Text files (*.txt)")
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def playfair_show_info(self):
        info_text = """Playfair Cipher là một phương pháp mã hóa cổ điển sử dụng ma trận 5x5 hoặc 6x6.

Cách hoạt động:
1. Tạo ma trận từ khóa
2. Chia văn bản thành các cặp ký tự
3. Mã hóa/giải mã từng cặp dựa trên vị trí trong ma trận

Đặc điểm:
• Ma trận 5x5: Chỉ chữ cái (J = I)
• Ma trận 6x6: Chữ cái và số"""
        QMessageBox.information(self, "Playfair Algorithm Info", info_text)

    # ==================== RSA METHODS ====================
    def update_rsa_input_tab_style(self):
        active_style = """
            QPushButton { color: #2563eb; font-weight: bold; border: none;
                border-bottom: 2px solid #2563eb; background-color: transparent;
                font-size: 20px; padding-bottom: 4px; }
        """
        inactive_style = """
            QPushButton { color: #4b5563; font-weight: normal; border: none;
                border-bottom: 2px solid transparent; background-color: transparent;
                font-size: 20px; padding-bottom: 4px; }
            QPushButton:hover { color: #1f2937; }
        """
        if self.rsa_input_mode == 'file':
            self.rsa_btn_tab_file.setStyleSheet(active_style)
            self.rsa_btn_tab_text.setStyleSheet(inactive_style)
            self.rsa_input_stack.setCurrentIndex(0)
        else:
            self.rsa_btn_tab_file.setStyleSheet(inactive_style)
            self.rsa_btn_tab_text.setStyleSheet(active_style)
            self.rsa_input_stack.setCurrentIndex(1)

    def rsa_switch_tab(self, mode):
        self.rsa_input_mode = mode
        self.update_rsa_input_tab_style()

    def rsa_browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "Text files (*.txt);;All files (*.*)")
        if fname:
            self.rsa_file_path = fname
            self.rsa_file_display.setText(fname)
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.rsa_file_content = f.read()
                    self.rsa_text_area.setText(self.rsa_file_content)
                    self.rsa_switch_tab('text')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    def rsa_get_input_text(self):
        if self.rsa_input_mode == 'file':
            return self.rsa_file_content
        else:
            return self.rsa_text_area.toPlainText()

    def rsa_generate_keys(self):
        try:
            key_size = int(self.rsa_key_size_combo.currentText().split()[0])
            self.rsa_private_key, self.rsa_public_key = rsa.generate_key_pair(key_size)
            self.rsa_public_key_pem = rsa.serialize_public_key(self.rsa_public_key)
            self.rsa_private_key_pem = rsa.serialize_private_key(self.rsa_private_key)
            self.rsa_public_key_display.setText(self.rsa_public_key_pem)
            self.rsa_private_key_display.setText(self.rsa_private_key_pem)
            QMessageBox.information(self, "Success", f"Successfully generated {key_size}-bit RSA key pair!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate keys: {str(e)}")

    def rsa_import_public_key(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, 'Open Public Key', '', "PEM files (*.pem);;All files (*.*)")
            if filename:
                with open(filename, 'rb') as f:
                    key_data = f.read()
                self.rsa_public_key = rsa.load_public_key(key_data.decode('utf-8'))
                self.rsa_public_key_pem = key_data.decode('utf-8')
                self.rsa_public_key_display.setText(self.rsa_public_key_pem)
                QMessageBox.information(self, "Success", "Public key imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import public key: {str(e)}")

    def rsa_import_private_key(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, 'Open Private Key', '', "PEM files (*.pem);;All files (*.*)")
            if filename:
                with open(filename, 'rb') as f:
                    key_data = f.read()
                self.rsa_private_key = rsa.load_private_key(key_data.decode('utf-8'))
                self.rsa_private_key_pem = key_data.decode('utf-8')
                self.rsa_private_key_display.setText(self.rsa_private_key_pem)
                self.rsa_public_key = self.rsa_private_key.public_key()
                self.rsa_public_key_pem = rsa.serialize_public_key(self.rsa_public_key)
                self.rsa_public_key_display.setText(self.rsa_public_key_pem)
                QMessageBox.information(self, "Success", "Private key imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import private key: {str(e)}")

    def rsa_execute_operation(self):
        mode = 'encrypt' if self.rsa_radio_encrypt.isChecked() else 'decrypt'
        if mode == 'encrypt':
            self.rsa_encrypt_text()
        else:
            self.rsa_decrypt_text()

    def rsa_encrypt_text(self):
        if not self.rsa_public_key:
            QMessageBox.warning(self, "Warning", "Please generate or import a public key first!")
            return
        try:
            plaintext = self.rsa_get_input_text().strip()
            if not plaintext:
                QMessageBox.warning(self, "Warning", "Please enter text to encrypt!")
                return
            encrypted_base64 = rsa.encrypt(plaintext, self.rsa_public_key)
            self.rsa_output_text.setText(encrypted_base64)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Encryption failed: {str(e)}")

    def rsa_decrypt_text(self):
        if not self.rsa_private_key:
            QMessageBox.warning(self, "Warning", "Please generate or import a private key first!")
            return
        try:
            ciphertext_base64 = self.rsa_get_input_text().strip()
            if not ciphertext_base64:
                QMessageBox.warning(self, "Warning", "Please enter base64 text to decrypt!")
                return
            plaintext = rsa.decrypt(ciphertext_base64, self.rsa_private_key)
            self.rsa_output_text.setText(plaintext)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Decryption failed: {str(e)}")

    def rsa_save_key_file(self, text_widget, default_name):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, 'Save Key File', default_name, "PEM files (*.pem);;All files (*.*)")
            if filename:
                with open(filename, 'w') as f:
                    f.write(text_widget.toPlainText())
                QMessageBox.information(self, "Success", "Key saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def rsa_save_result(self):
        try:
            content = self.rsa_output_text.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, "Warning", "No result to save!")
                return
            filename, _ = QFileDialog.getSaveFileName(self, 'Save Result', 'result.txt', "Text files (*.txt);;All files (*.*)")
            if filename:
                with open(filename, 'w') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", "Result saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def rsa_copy_to_clipboard(self, text_widget):
        text = text_widget.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Success", "Copied to clipboard!")
        else:
            QMessageBox.warning(self, "Warning", "No content to copy!")

    def rsa_clear_all(self):
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.rsa_public_key_pem = ""
        self.rsa_private_key_pem = ""
        self.rsa_public_key_display.clear()
        self.rsa_private_key_display.clear()
        self.rsa_text_area.clear()
        self.rsa_file_display.clear()
        self.rsa_file_content = ''
        self.rsa_file_path = ''
        self.rsa_output_text.clear()
        QMessageBox.information(self, "Cleared", "All inputs and outputs have been cleared!")

    def rsa_show_info(self):
        info_text = """RSA (Rivest-Shamir-Adleman) là hệ thống mật mã khóa công khai.

Các đặc điểm chính:
• Mã hóa bất đối xứng (dùng khóa công khai/khóa riêng)
• Truyền tải dữ liệu an toàn
• Hỗ trợ chữ ký số
• Giao thức trao đổi khóa

Cách hoạt động:
1. Tạo cặp khóa (Public Key / Private Key)
2. Mã hóa văn bản bằng khóa công khai (Public Key)
3. Giải mã văn bản bằng khóa riêng (Private Key)
4. Hai khóa có liên kết toán học chặt chẽ, nhưng không thể suy ra khóa riêng từ khóa công khai.

Độ an toàn: Dựa trên độ khó thực tế của bài toán phân tích thừa số các số nguyên tố lớn."""
        QMessageBox.information(self, "Thông tin thuật toán RSA", info_text)

    # ==================== CONNECTIONS ====================
    def setup_connections(self):
        # Algorithm selection
        self.btn_playfair.clicked.connect(self.show_playfair)
        self.btn_rsa.clicked.connect(self.show_rsa)
        
        # Playfair connections
        self.playfair_btn_tab_file.clicked.connect(lambda: self.playfair_switch_tab('file'))
        self.playfair_btn_tab_text.clicked.connect(lambda: self.playfair_switch_tab('text'))
        self.playfair_btn_browse.clicked.connect(self.playfair_browse_file)
        self.playfair_btn_run.clicked.connect(self.playfair_run_cipher)
        self.playfair_btn_clear.clicked.connect(self.playfair_clear_all)
        self.playfair_btn_save.clicked.connect(self.playfair_save_file)
        self.playfair_btn_info.clicked.connect(self.playfair_show_info)
        
        # RSA connections
        self.rsa_btn_generate.clicked.connect(self.rsa_generate_keys)
        self.rsa_btn_import_public.clicked.connect(self.rsa_import_public_key)
        self.rsa_btn_import_private.clicked.connect(self.rsa_import_private_key)
        self.rsa_btn_execute.clicked.connect(self.rsa_execute_operation)
        self.rsa_btn_clear.clicked.connect(self.rsa_clear_all)
        self.rsa_btn_copy_public.clicked.connect(lambda: self.rsa_copy_to_clipboard(self.rsa_public_key_display))
        self.rsa_btn_copy_private.clicked.connect(lambda: self.rsa_copy_to_clipboard(self.rsa_private_key_display))
        self.rsa_btn_save_public.clicked.connect(lambda: self.rsa_save_key_file(self.rsa_public_key_display, "public_key.pem"))
        self.rsa_btn_save_private.clicked.connect(lambda: self.rsa_save_key_file(self.rsa_private_key_display, "private_key.pem"))
        self.rsa_btn_save_result.clicked.connect(self.rsa_save_result)
        self.rsa_btn_info.clicked.connect(self.rsa_show_info)
        self.rsa_btn_tab_file.clicked.connect(lambda: self.rsa_switch_tab('file'))
        self.rsa_btn_tab_text.clicked.connect(lambda: self.rsa_switch_tab('text'))
        self.rsa_btn_browse.clicked.connect(self.rsa_browse_file)
        
        # Initialize
        self.playfair_switch_tab('file')
        self.rsa_switch_tab('file')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = CryptoApp()
    window.show()
    sys.exit(app.exec_())

