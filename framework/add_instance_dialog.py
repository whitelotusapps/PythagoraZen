import inspect
import logging

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

from framework.logging_handler import PythagoraZenLogger

class AddInstanceDialog(QDialog):
    def __init__(self, parent=None):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.setWindowTitle("Add Instance")
        self.setGeometry(400, 400, 800, 200)
        layout = QVBoxLayout(self)

        self.subdomain_input = QLineEdit(self)
        self.api_user_email_input = QLineEdit(self)
        self.api_key_input = QLineEdit(self)

        layout.addWidget(QLabel("Subdomain:"))
        layout.addWidget(self.subdomain_input)
        layout.addWidget(QLabel("API User Email Address:"))
        layout.addWidget(self.api_user_email_input)
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key_input)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.accept)

        layout.addWidget(save_button)
