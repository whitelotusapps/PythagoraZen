import inspect
import logging

from PyQt5.QtWidgets import QCheckBox, QDialog, QGridLayout, QPushButton, QVBoxLayout

from framework.logging_handler import PythagoraZenLogger


class KeySelectionDialog(QDialog):
    def __init__(self, keys, subdomain, selected_collection):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.setWindowTitle(f"{subdomain} - {selected_collection}")
        self.selected_keys = set()
        self.init_ui(keys)

    def init_ui(self, keys):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        layout = QVBoxLayout()
        self.setGeometry(100, 100, 400, 200)
        checkboxes = []

        for key in sorted(keys):
            checkbox = QCheckBox(key)
            checkboxes.append(checkbox)

        num_columns = 5
        num_rows = (len(checkboxes) + num_columns - 1) // num_columns
        grid_layout = QGridLayout()

        for i, checkbox in enumerate(checkboxes):
            grid_layout.addWidget(checkbox, i // num_columns, i % num_columns)

        layout.addLayout(grid_layout)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(lambda: self.toggle_all_checkboxes(True))
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(lambda: self.toggle_all_checkboxes(False))

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.accept_selection)

        layout.addWidget(select_all_button)
        layout.addWidget(deselect_all_button)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

    def toggle_all_checkboxes(self, state):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        checkboxes = self.findChildren(QCheckBox)
        for checkbox in checkboxes:
            checkbox.setChecked(state)

    def accept_selection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        checkboxes = self.findChildren(QCheckBox)
        self.selected_keys = {
            checkbox.text() for checkbox in checkboxes if checkbox.isChecked()
        }
        self.accept()
