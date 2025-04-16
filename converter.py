import os, asyncio, sys

from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QLabel, QFormLayout, QMessageBox
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from opentele.td import TDesktop
from opentele.api import UseCurrentSession

from loguru import logger



async def session_to_tdata(session_path, api_id, api_hash, proxy_data=None, output_dir=None):

    if not os.path.exists(session_path):
        raise FileNotFoundError(f"Session file {session_path} not found")

    if output_dir is None:
        output_dir = os.path.dirname(session_path)

    session_name = os.path.splitext(os.path.basename(session_path))[0]
    tdata_dir = os.path.join(output_dir, f"{session_name}_tdata")

    proxy = None
    if proxy_data and proxy_data.get('ip') and proxy_data.get('port'):
        proxy = (
            'socks5',
            proxy_data['ip'],
            int(proxy_data['port']),
            True,
            proxy_data.get('login'),
            proxy_data.get('password')
        )

    try:
        client = TelegramClient(
            session_path,
            api_id=int(api_id),
            api_hash=api_hash,
            proxy=proxy if proxy else None
        )
    except Exception as e:
        logger.warning(e)

        try:
            with open(session_path, "r") as f:
                session_string = f.read().strip()
            logger.info("Session string loaded from session.session")
        except Exception as e:
            logger.error(f"Failed to read session file: {e}")
            return

        client = TelegramClient(StringSession(session_string), api_id=int(api_id), api_hash=api_hash, proxy=proxy if proxy else None)
        

    tdesk = await client.ToTDesktop(flag=UseCurrentSession)
    tdesk.SaveTData(os.path.join(tdata_dir, "tdata"))
    
    return tdata_dir

class AsyncTrafficConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🚀 AsyncTraffic Converter 🚀")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                color: #333;
            }
            QLineEdit::placeholder {
                color: #888;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
                background-color: #f8f9fa;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QMessageBox {
                background-color: #fff;
                color: #333; 
            }
            QMessageBox QLabel {
                color: #333;
            }
            QMessageBox QPushButton {
                padding: 5px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("AsyncTraffic Converter 🌟")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setSpacing(10)

        self.session_input = QLineEdit()
        self.session_input.setPlaceholderText("Select .session file")
        self.session_input.setReadOnly(True)
        session_button = QPushButton("📂 Browse")
        session_button.clicked.connect(self.browse_session)
        session_layout = QHBoxLayout()
        session_layout.addWidget(self.session_input)
        session_layout.addWidget(session_button)
        form_layout.addRow("Session File:", session_layout)

        self.api_id_input = QLineEdit()
        self.api_id_input.setPlaceholderText("Enter API ID")
        form_layout.addRow("API ID:", self.api_id_input)

        self.api_hash_input = QLineEdit()
        self.api_hash_input.setPlaceholderText("Enter API Hash")
        form_layout.addRow("API Hash:", self.api_hash_input)

        self.proxy_ip_input = QLineEdit()
        self.proxy_ip_input.setPlaceholderText("Proxy IP (optional)")
        self.proxy_ip_input.setEnabled(False)
        form_layout.addRow("Proxy IP (socks5):", self.proxy_ip_input)

        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setPlaceholderText("Proxy Port (optional)")
        self.proxy_port_input.setEnabled(False)
        form_layout.addRow("Proxy Port (socks5):", self.proxy_port_input)

        self.proxy_login_input = QLineEdit()
        self.proxy_login_input.setPlaceholderText("Proxy Login (optional)")
        self.proxy_login_input.setEnabled(False)
        form_layout.addRow("Proxy Login (socks5):", self.proxy_login_input)

        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setPlaceholderText("Proxy Password (optional)")
        self.proxy_password_input.setEnabled(False)
        form_layout.addRow("Proxy Password (socks5):", self.proxy_password_input)

        layout.addLayout(form_layout)

        self.convert_button = QPushButton("Convert ▶️")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.session_input.textChanged.connect(self.toggle_inputs)
        self.api_id_input.textChanged.connect(self.toggle_inputs)
        self.api_hash_input.textChanged.connect(self.toggle_inputs)

    def browse_session(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select .session File", "", "Session Files (*.session)"
        )
        if file_path:
            self.session_input.setText(file_path)

    def toggle_inputs(self):
        has_session = bool(self.session_input.text())
        has_api_id = bool(self.api_id_input.text())
        has_api_hash = bool(self.api_hash_input.text())
        self.proxy_ip_input.setEnabled(has_session)
        self.proxy_port_input.setEnabled(has_session)
        self.proxy_login_input.setEnabled(has_session)
        self.proxy_password_input.setEnabled(has_session)
        self.convert_button.setEnabled(has_session and has_api_id and has_api_hash)

    def start_conversion(self):
        self.convert_button.setEnabled(False)
        asyncio.run(self.convert_session())
        self.convert_button.setEnabled(True)

    async def convert_session(self):
        session_path = self.session_input.text()
        api_id = self.api_id_input.text()
        api_hash = self.api_hash_input.text()

        proxy_data = {}
        if self.proxy_ip_input.text() and self.proxy_port_input.text():
            proxy_data = {
                'ip': self.proxy_ip_input.text(),
                'port': self.proxy_port_input.text(),
                'login': self.proxy_login_input.text() or None,
                'password': self.proxy_password_input.text() or None
            }

        try:
            tdata_dir = await session_to_tdata(
                session_path=session_path,
                api_id=int(api_id),
                api_hash=api_hash,
                proxy_data=proxy_data if proxy_data else None,
                output_dir=self.data_dir
            )
            QMessageBox.information(
                self, "✅ Success", f"Conversion completed!\ntdata saved to: {tdata_dir}"
            )
        except Exception as e:
            logger.exception(f"Conversion failed: {str(e)}")
            QMessageBox.critical(
                self, "❌ Error", f"Conversion failed:\n{str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12))
    window = AsyncTrafficConverter()
    window.show()
    sys.exit(app.exec())