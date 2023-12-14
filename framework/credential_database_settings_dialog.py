import inspect
import logging

# database_settings_dialog.py
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from framework.add_instance_dialog import AddInstanceDialog
from framework.edit_instance_dialog import EditInstanceDialog
from framework.logging_handler import PythagoraZenLogger


class CredentialDatabaseSettingsDialog(QDialog):
    def __init__(self, parent, database_operations):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        super().__init__(parent)
        self.database_operations = database_operations
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Database Settings")
        self.resize(600, 400)  # Adjust the size as needed
        layout = QVBoxLayout(self)

        # Add a list widget for displaying instances
        self.instances_list = QListWidget(self)
        self.instances_list.setSelectionMode(QListWidget.SingleSelection)
        self.instances_list.itemClicked.connect(self.load_credentials)
        layout.addWidget(QLabel("Select Instance:"))
        layout.addWidget(self.instances_list)

        # Add buttons for adding, editing, and deleting
        add_button = QPushButton("Add", self)
        add_button.clicked.connect(self.add_instance)
        edit_button = QPushButton("Edit", self)
        edit_button.clicked.connect(self.edit_instance)
        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.delete_instance)

        layout.addWidget(add_button)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)

        # Populate the instances list
        self.populate_instances()

    def populate_instances(self):
        instances = self.database_operations.fetch_instances()

        self.instances_list.clear()

        for instance in instances:
            item = QListWidgetItem(instance[0])
            self.instances_list.addItem(item)

    def load_credentials(self, item):
        selected_subdomain = item.text()

        credentials = self.database_operations.fetch_credentials(selected_subdomain)

        # Do something with the credentials if needed

    def add_instance(self):
        add_dialog = AddInstanceDialog(self)
        result = add_dialog.exec_()

        if result == QDialog.Accepted:
            subdomain = add_dialog.subdomain_input.text()
            email_address = add_dialog.api_user_email_input.text()
            api_key = add_dialog.api_key_input.text()

            self.database_operations.add_instance(subdomain, email_address, api_key)

            # Update the instances list
            self.populate_instances()

    def edit_instance(self):
        current_item = self.instances_list.currentItem()

        if current_item is not None:
            subdomain = current_item.text()

            # Fetch the credentials for the selected subdomain
            credentials = self.database_operations.fetch_credentials(subdomain)

            # Pass the database_operations instance to EditInstanceDialog
            edit_dialog = EditInstanceDialog(
                subdomain,
                credentials.get("api_user_email", ""),
                credentials.get("api_key", ""),
                self.database_operations,
                self,
            )
            result = edit_dialog.exec_()

            if result == QDialog.Accepted:
                # Update the instances list
                self.populate_instances()

    def delete_instance(self):
        current_item = self.instances_list.currentItem()

        if current_item is not None:
            subdomain = current_item.text()

            # Delete the instance from the database
            self.database_operations.delete_instance(subdomain)

            # Remove the item from the list
            self.instances_list.takeItem(self.instances_list.row(current_item))
