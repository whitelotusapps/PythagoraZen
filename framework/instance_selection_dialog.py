import inspect

# instance_selection_dialog.py
import logging

from PyQt5.QtWidgets import QComboBox, QDialog, QLabel, QPushButton, QVBoxLayout

from .credential_database_operations import (
    CredentialDatabaseOperations,
)  # Import DatabaseOperations
from framework.logging_handler import PythagoraZenLogger


class InstanceSelectionDialog(QDialog):
    def __init__(self, database_operations: CredentialDatabaseOperations):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.setWindowTitle("Select Instance")
        self.selected_instance = None
        self.database_operations = (
            database_operations  # Store an instance of DatabaseOperations
        )

        self.init_ui()

    def init_ui(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        layout = QVBoxLayout()

        # Fetch instances from the database
        try:
            instances = self.database_operations.fetch_instances()
        except Exception as e:
            error_message = str(e)
            logging.error(f"{error_message}")

        # Add only the subdomains to the combo box for display
        subdomains = [subdomain for subdomain, _, _ in instances]

        # Add a combo box for selecting instances
        self.instance_dropdown = QComboBox(self)
        self.instance_dropdown.addItems(subdomains)

        layout.addWidget(QLabel("Select Instance:"))
        layout.addWidget(self.instance_dropdown)

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.accept_selection)

        layout.addWidget(confirm_button)

        self.setLayout(layout)

    def accept_selection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Retrieve the selected index
        selected_index = self.instance_dropdown.currentIndex()

        # Fetch the corresponding tuple based on the index
        try:
            instances = self.database_operations.fetch_instances()
            selected_instance = instances[selected_index]
            self.selected_instance = selected_instance
            self.accept()
        except Exception as e:
            error_message = str(e)
            logging.error(f"ERROR: {error_message}")
