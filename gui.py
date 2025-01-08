from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFrame, QFileDialog,
    QHBoxLayout, QTextEdit
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor


class LogHandler(QObject):
    log_signal = pyqtSignal(str)

    def write(self, text):
        if text.strip():  # Only emit non-empty strings
            self.log_signal.emit(text)

    def flush(self):
        pass


class ModernConfigGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth_token = None
        self.ip_address = None
        self.install_path = None
        self.path_entry_clicked = False
        self.log_handler = LogHandler()
        self.log_handler.log_signal.connect(self.update_log)
        self.installation_complete = False
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Procesure Agent Configuration')
        self.setMinimumSize(600, 600)  # Set minimum size instead of fixed
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 2px;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
                margin-bottom: 15px;
                min-height: 20px;
                color: #2c3e50;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 14px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
            }
            QPushButton#browse_btn {
                min-width: 80px;
                padding: 12px;
                margin-left: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 12px;
                color: #2c3e50;
                background-color: white;
                min-height: 150px;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 20, 50, 40)
        layout.setSpacing(5)

        # Title
        title = QLabel('Procesure Agent Configuration')
        title.setStyleSheet("""
            font-size: 20px;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 30px;
            padding: 10px 0;
            border-bottom: 2px solid #e0e0e0;
            min-height: 30px;
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop)

        # Input Fields Container
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)

        # Auth Token
        input_layout.addWidget(QLabel('Auth Token:'))
        self.auth_entry = QLineEdit()
        self.auth_entry.setFixedHeight(45)
        self.auth_entry.setPlaceholderText('Enter your authentication token')
        input_layout.addWidget(self.auth_entry)

        # IP Address
        input_layout.addWidget(QLabel('IP Address:'))
        self.ip_entry = QLineEdit()
        self.ip_entry.setFixedHeight(45)
        self.ip_entry.setPlaceholderText('Enter IP address')
        input_layout.addWidget(self.ip_entry)

        # Install Path with Browse Button
        input_layout.addWidget(QLabel('Installation Path:'))
        path_layout = QHBoxLayout()
        path_layout.setSpacing(0)
        
        self.path_entry = QLineEdit()
        self.path_entry.setFixedHeight(45)
        self.path_entry.setPlaceholderText('C:\Program Files\Procesure')
        self.path_entry.mousePressEvent = self.on_path_entry_click
        path_layout.addWidget(self.path_entry)
        
        browse_btn = QPushButton('Browse')
        browse_btn.setObjectName('browse_btn')
        browse_btn.setFixedHeight(45)
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        
        input_layout.addLayout(path_layout)
        layout.addWidget(input_container)

        # Add Installation Log
        layout.addWidget(QLabel('Installation Progress:'))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text, 1)  # Give it a stretch factor of 1

        # Button container at the bottom
        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # Continue Button
        self.continue_btn = QPushButton('Continue')
        self.continue_btn.setFixedHeight(45)
        self.continue_btn.clicked.connect(self.on_continue)
        button_layout.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Close Button (hidden initially)
        self.close_btn = QPushButton('Close')
        self.close_btn.setFixedHeight(45)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.hide()
        button_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.button_container)

        # Center the window on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_log(self, text):
        self.log_text.append(text.strip())
        # Scroll to the bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Check if installation is complete
        if "Setup complete" in text:
            self.installation_complete = True
            self.continue_btn.hide()
            self.close_btn.show()
            # Enable all input fields
            self.auth_entry.setEnabled(True)
            self.ip_entry.setEnabled(True)
            self.path_entry.setEnabled(True)
        elif "Setup failed" in text:
            self.installation_complete = False
            self.continue_btn.setEnabled(True)
            self.continue_btn.setText("Continue")
            # Enable all input fields
            self.auth_entry.setEnabled(True)
            self.ip_entry.setEnabled(True)
            self.path_entry.setEnabled(True)

    def get_log_handler(self):
        return self.log_handler

    def on_path_entry_click(self, event):
        if not self.path_entry_clicked:
            self.path_entry.clear()
            self.path_entry_clicked = True
        QLineEdit.mousePressEvent(self.path_entry, event)

    def on_continue(self):
        self.auth_token = self.auth_entry.text()
        self.ip_address = self.ip_entry.text()
        if not self.path_entry.text():
            self.install_path = r"C:\Program Files\Procesure"
        else:
            self.install_path = self.path_entry.text()
        
        # Disable input fields during installation
        self.auth_entry.setEnabled(False)
        self.ip_entry.setEnabled(False)
        self.path_entry.setEnabled(False)
        
        self.continue_btn.setEnabled(False)
        self.continue_btn.setText("Installing...")
        self.installation_started = True

    def get_config(self):
        self.show()
        QApplication.instance().exec()
        return self.auth_token, self.ip_address, self.install_path

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            self.path_entry.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.path_entry.setText(folder)
            self.path_entry_clicked = True 