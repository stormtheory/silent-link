from PySide6 import QtWidgets
from typing import Optional
import ipaddress
from client.settings import Settings
from config import (APP_NAME, APP_ICON_PATH, CLIENT_IP, SSL_CA_PATH, CERTS_DIR,
                    DATA_DIR, ensure_data_dirs)
from config import SERVER_PORT as DEFAULT_SERVER_PORT


###############################################################################
# ─── UI helpers ─────────────────────────────────────────────────────────────
###############################################################################

class FirstRunDialog(QtWidgets.QDialog):
    """Ask for Display Name, Server IP, and Port on first launch."""
    def __init__(self, ptt_manager):
        MIC_STARTUP_OPTIONS = [
            "mute",
            "on"
        ]
        SPK_STARTUP_OPTIONS = [
            "on",
            "mute"
        ]
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} – Setup")
        form = QtWidgets.QFormLayout(self)
        self.ptt_manager = ptt_manager


        self.name_edit = QtWidgets.QLineEdit()
        self.ip_edit = QtWidgets.QLineEdit()
        self.port_edit = QtWidgets.QLineEdit(str(DEFAULT_SERVER_PORT))
        self.mic_startup_combo = QtWidgets.QComboBox()
        self.mic_startup_combo.addItems(MIC_STARTUP_OPTIONS)
        self.spk_startup_combo = QtWidgets.QComboBox()
        self.spk_startup_combo.addItems(SPK_STARTUP_OPTIONS)

        # PTT LISTENER
        self.ptt_listen_btn = QtWidgets.QPushButton("Set PTT Key/Button")
        self.ptt_label = QtWidgets.QLabel("(none)")
        self.ptt_label.setStyleSheet("font-style: italic; color: gray;")
        # Horizontal layout for button + current value
        ptt_layout = QtWidgets.QHBoxLayout()
        ptt_layout.addWidget(self.ptt_listen_btn)
        ptt_layout.addWidget(self.ptt_label)

        form.addRow("Display Name:", self.name_edit)
        form.addRow("Server IP:", self.ip_edit)
        form.addRow("Server Port:", self.port_edit)
        form.addRow("Mic at App Startup:", self.mic_startup_combo)
        form.addRow("Speaker at App Startup:", self.spk_startup_combo)
        form.addRow("Push-To-Talk Key:", ptt_layout)

        self.save_btn = QtWidgets.QPushButton("Save and Reload App")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setEnabled(False)
        form.addRow(self.save_btn)

        # Real-time validation
        self.name_edit.textChanged.connect(self.validate)
        self.ip_edit.textChanged.connect(self.validate)
        self.port_edit.textChanged.connect(self.validate)
        self.ptt_listen_btn.clicked.connect(self.listen_for_ptt_input)

        
        self.validate()

    def validate(self):
        name = self.name_edit.text().strip()
        ip = self.ip_edit.text().strip()
        port = self.port_edit.text().strip()
        
        # Name: 1–32 chars, letters, numbers, spaces only
        valid_name = 1 <= len(name) <= 32 and all(c.isalnum() or c.isspace() for c in name)

        # IP: use ipaddress for strict validation fallback
        try:
            ipaddress.ip_address(ip)
            valid_ip = True
        except ValueError:
            valid_ip = False

        # Port: integer 1–65535
        try:
            p = int(port)
            valid_port = 1 <= p <= 65535
        except ValueError:
            valid_port = False

        is_valid = valid_name and valid_ip and valid_port

        self.save_btn.setEnabled(is_valid)

    @property
    def display_name(self):
        return self.name_edit.text().strip()

    @property
    def server_ip(self):
        return self.ip_edit.text().strip()

    @property
    def server_port(self) -> Optional[int]:
        # Validate port: integer between 1 and 65535
        try:
            p = int(self.port_edit.text().strip())
            if 1 <= p <= 65535:
                return p
        except ValueError:
            pass
        return None
        
    @property
    def mic_startup(self) -> bool:
        return self.mic_startup_combo.currentText().lower() == "on" # True value

    @property
    def spk_startup(self) -> bool:
        return self.spk_startup_combo.currentText().lower() == "on" # True value
    
    @property
    def ptt_key(self) -> dict:
        return self.ptt_manager.ptt_key  # unified {'type': ..., 'key': ...}
    
    def listen_for_ptt_input(self):
        self.ptt_listen_btn.setEnabled(False)
        self.ptt_label.setText("Listening...")
        self.ptt_label.setStyleSheet("color: orange; font-style: italic;")

        def on_learned(trigger):
            input_type = trigger.get("type")
            if input_type == "keyboard":
                display = f"Keyboard: {trigger['key']}"
            elif input_type == "gamepad":
                display = f"Gamepad: Button {trigger['button']}"
            else:
                display = "(invalid input)"

            self.ptt_label.setText(display)
            self.ptt_label.setStyleSheet("color: green; font-style: normal;")
            self.ptt_listen_btn.setEnabled(True)

        # Connect your PTTManager's signal to update this dialog
        self.ptt_manager.pttInputLearned.connect(on_learned)

        # Start listening for input
        self.ptt_manager.listen_for_next_input()


