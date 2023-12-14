import inspect
import logging

# mongodb_collection_selection_dialog.py
from PyQt5.QtWidgets import QComboBox, QDialog, QLabel, QPushButton, QVBoxLayout

from framework.logging_handler import PythagoraZenLogger

from .instance_database_operations_api_endpoint_config import (
    ZendeskInstanceDatabaseOperationsMongoDB,
)


class MongoDBCollectionSelectionDialog(QDialog):
    def __init__(
        self, database_operations: ZendeskInstanceDatabaseOperationsMongoDB, subdomain
    ):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.setWindowTitle(f"{subdomain}")
        self.selected_collection = None
        self.database_operations = (
            database_operations  # Store an instance of DatabaseOperations
        )
        self.init_ui()

    def init_ui(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        layout = QVBoxLayout()
        self.setGeometry(100, 100, 400, 200)
        # Fetch collections from the database_operations
        try:
            collections = self.database_operations.list_available_collections()
            sorted_collections = sorted(collections)
        except Exception as e:
            error_message = str(e)
            print(f"ERROR: {error_message}")

        # Add a combo box for selecting collections
        self.collection_dropdown = QComboBox(self)
        self.collection_dropdown.addItems(sorted_collections)

        layout.addWidget(QLabel("Select Collection:"))
        layout.addWidget(self.collection_dropdown)

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.accept_selection)

        layout.addWidget(confirm_button)

        self.setLayout(layout)

    def accept_selection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Retrieve the selected index
        selected_index = self.collection_dropdown.currentIndex()

        # Fetch the corresponding collection based on the index
        try:
            collections = self.database_operations.list_available_collections()
            sorted_collections = sorted(collections)
            selected_collection = sorted_collections[selected_index]
            self.selected_collection = selected_collection
            self.accept()
        except Exception as e:
            error_message = str(e)
            print(f"ERROR: {error_message}")
