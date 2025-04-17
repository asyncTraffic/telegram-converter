import os, asyncio, sys, re
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QLabel, QFormLayout, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QIcon
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from opentele.td import TDesktop
from opentele.api import UseCurrentSession
from loguru import logger

logger.remove()
logger.add(
    "converter.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    filter=lambda record: "sensitive" not in record["extra"],
    backtrace=True,
    diagnose=True
)
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    filter=lambda record: "sensitive" not in record["extra"],
    backtrace=True,
    diagnose=True
)

async def session_to_tdata(session_path, api_id, api_hash, proxy_data=None, output_dir=None):
    if not os.path.exists(session_path):
        logger.error(f"Session file not found: {session_path}")
        raise FileNotFoundError("The selected .session file was not found. Please check the file path.")

    if output_dir is None:
        output_dir = os.path.dirname(session_path)
    
    session_name = os.path.splitext(os.path.basename(session_path))[0]
    tdata_dir = os.path.join(output_dir, f"{session_name}_tdata")

    proxy = None
    if proxy_data and proxy_data.get('ip') and proxy_data.get('port') and proxy_data.get('type'):
        proxy = (
            proxy_data['type'],
            proxy_data['ip'],
            int(proxy_data['port']),
            True,
            proxy_data.get('login'),
            proxy_data.get('password')
        )
        logger.info(f"Using proxy type: {proxy_data['type']}")
    else:
        logger.info("No proxy configured")

    try:
        client = TelegramClient(
            session_path,
            api_id=int(api_id),
            api_hash=api_hash,
            proxy=proxy if proxy else None
        )
    except Exception as e:
        logger.warning(f"Failed to initialize TelegramClient with session file: {str(e)}")
        try:
            with open(session_path, "r") as f:
                session_string = f.read().strip()
            logger.info("Session string loaded from session file")
            client = TelegramClient(
                StringSession(session_string),
                api_id=int(api_id),
                api_hash=api_hash,
                proxy=proxy if proxy else None
            )
        except Exception as e:
            logger.exception(f"Failed to read session file or initialize client")
            raise ValueError("Unable to initialize Telegram session. Please check the session file or API credentials.")

    try:
        tdesk = await client.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(os.path.join(tdata_dir, "tdata"))
        logger.info(f"tdata saved to: {tdata_dir}")
        return tdata_dir
    except Exception as e:
        logger.exception(f"Conversion to tdata failed")
        raise RuntimeError("Failed to convert session to tdata. Please try again or check the logs.")

class AsyncTrafficConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AsyncTraffic", "Converter")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🚀 AsyncTraffic Converter")
        self.setFixedSize(500, 500)
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
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                color: #333;
            }
            QComboBox:focus {
                border: 1px solid #007bff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #fff;
                color: #000;
                selection-background-color: #007bff;
                selection-color: #fff;
            }
            QComboBox::item:selected {
                background-color: #007bff;
                color: #fff;
            }
            QComboBox::item {
                color: #000;
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
        self.api_id_input.setText(self.settings.value("api_id", ""))
        self.api_id_input.textChanged.connect(self.save_api_id)
        form_layout.addRow("API ID:", self.api_id_input)

        self.api_hash_input = QLineEdit()
        self.api_hash_input.setPlaceholderText("Enter API Hash")
        self.api_hash_input.setText(self.settings.value("api_hash", ""))
        self.api_hash_input.textChanged.connect(self.save_api_hash)
        form_layout.addRow("API Hash:", self.api_hash_input)

        self.proxy_type_input = QComboBox()
        self.proxy_type_input.addItems(["None", "http", "https", "socks5", "socks4"])
        self.proxy_type_input.currentTextChanged.connect(self.toggle_proxy_input)
        form_layout.addRow("Proxy Type:", self.proxy_type_input)

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("Enter proxy (e.g., login:password@ip:port or ip:port)")
        self.proxy_input.setEnabled(False)
        form_layout.addRow("Proxy:", self.proxy_input)

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

    def save_api_id(self):
        self.settings.setValue("api_id", self.api_id_input.text())

    def save_api_hash(self):
        self.settings.setValue("api_hash", self.api_hash_input.text())

    def browse_session(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select .session File", "", "Session Files (*.session)"
        )
        if file_path:
            self.session_input.setText(file_path)

    def toggle_proxy_input(self):
        is_proxy_selected = self.proxy_type_input.currentText() != "None"
        self.proxy_input.setEnabled(is_proxy_selected)

    def toggle_inputs(self):
        has_session = bool(self.session_input.text())
        has_api_id = bool(self.api_id_input.text())
        has_api_hash = bool(self.api_hash_input.text())
        self.proxy_type_input.setEnabled(has_session)
        self.convert_button.setEnabled(has_session and has_api_id and has_api_hash)

    def parse_proxy_string(self, proxy_string):
        if not proxy_string:
            return None

        pattern = r"^(?:(?P<login>[^:]+):(?P<password>[^@]+)@)?(?P<ip>[^:]+):(?P<port>\d+)$"
        match = re.match(pattern, proxy_string)
        if not match:
            logger.error("Invalid proxy format provided")
            raise ValueError("Please enter proxy in format login:password@ip:port or ip:port")

        return {
            'type': self.proxy_type_input.currentText(),
            'ip': match.group('ip'),
            'port': match.group('port'),
            'login': match.group('login'),
            'password': match.group('password')
        }

    def start_conversion(self):
        self.convert_button.setEnabled(False)
        asyncio.run(self.convert_session())
        self.convert_button.setEnabled(True)

    async def convert_session(self):
        session_path = self.session_input.text()
        api_id = self.api_id_input.text()
        api_hash = self.api_hash_input.text()
        proxy_data = None

        if self.proxy_type_input.currentText() != "None":
            try:
                proxy_data = self.parse_proxy_string(self.proxy_input.text())
            except ValueError as e:
                logger.exception("Proxy parsing failed")
                QMessageBox.critical(
                    self, "❌ Error", str(e)
                )
                return

        try:
            tdata_dir = await session_to_tdata(
                session_path=session_path,
                api_id=api_id,
                api_hash=api_hash,
                proxy_data=proxy_data,
                output_dir=self.data_dir
            )
            QMessageBox.information(
                self, "✅ Success", f"Conversion completed!\ntdata saved to: {tdata_dir}"
            )
        except FileNotFoundError as e:
            logger.exception("Session file error")
            QMessageBox.critical(
                self, "❌ Error", str(e)
            )
        except ValueError as e:
            logger.exception("Session initialization error")
            QMessageBox.critical(
                self, "❌ Error", str(e)
            )
        except RuntimeError as e:
            logger.exception("Conversion error")
            QMessageBox.critical(
                self, "❌ Error", str(e)
            )
        except Exception as e:
            logger.exception("Unexpected error during conversion")
            QMessageBox.critical(
                self, "❌ Error", "An unexpected error occurred. Please check the logs for details.")
        finally:
            self.convert_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12))
    window = AsyncTrafficConverter()
    window.show()
    sys.exit(app.exec())
