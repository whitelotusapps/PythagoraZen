import inspect
import logging

# edit_instance_dialog.py
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

from framework.logging_handler import PythagoraZenLogger


class EditInstanceDialog(QDialog):
    def __init__(
        self, subdomain, api_user_email, api_key, database_operations, parent=None
    ):
        super(EditInstanceDialog, self).__init__(parent)
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.subdomain = subdomain
        self.setWindowTitle(self.subdomain)
        self.api_user_email = api_user_email
        self.api_key = api_key
        self.database_operations = (
            database_operations  # Assign the instance variable here
        )

        self.init_ui()

    def init_ui(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.setWindowTitle(f"Edit {self.subdomain} Instance")
        self.setGeometry(400, 400, 800, 200)
        layout = QVBoxLayout(self)

        # Add QLineEdit for subdomain
        self.subdomain_input = QLineEdit(self)
        self.subdomain_input.setText(self.subdomain)
        layout.addWidget(QLabel("Subdomain:"))
        layout.addWidget(self.subdomain_input)

        # Add QLineEdit for API User Email
        self.email_input = QLineEdit(self)
        self.email_input.setText(self.api_user_email)
        layout.addWidget(QLabel("API User Email Address:"))
        layout.addWidget(self.email_input)

        # Add QLineEdit for API Key
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setText(self.api_key)
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key_input)

        # Add Save button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_data)
        layout.addWidget(save_button)

    def save_data(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Get the current text from the QLineEdit fields
        new_subdomain = self.subdomain_input.text()
        new_email = self.email_input.text()
        new_api_key = self.api_key_input.text()

        # Update the instance with the new data
        self.database_operations.update_instance(
            self.subdomain, new_subdomain, new_email, new_api_key
        )

        # Optionally, you can close the dialog or emit a signal for further actions
        self.accept()
