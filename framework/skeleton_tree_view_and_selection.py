import inspect
import json
import logging
import os

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import (
    QAction,
    QInputDialog,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from framework.logging_handler import PythagoraZenLogger


class SkeletonTreeViewAndSelection(QWidget):
    def __init__(
        self, json_data=None, selected_collection=None, zendesk_subdomain=None
    ):
        super(SkeletonTreeViewAndSelection, self).__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.selected_keys = []
        self.selected_collection = selected_collection
        self.zendesk_subdomain = zendesk_subdomain
        self.setWindowTitle(
            f"Collection: {self.selected_collection}, Instance: {self.zendesk_subdomain}"
        )
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.setColumnCount(2)

        # Set stylesheet with improved checkbox appearance
        self.tree_widget.setStyleSheet(
            """
            QTreeView::indicator:checked {
                image: url(none);
                background-color: palette(highlight);
                border: 1px solid palette(shadow);
            }
            QTreeView::item {
                color: black;  /* Set the color of the text */
            }
        """
        )

        # Populate the tree with provided or loaded JSON data
        if json_data:
            self.populate_tree(json_data, self.tree_widget)

        layout.addWidget(self.tree_widget)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all)

        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all)

        save_button = QPushButton("Save Selection")
        save_button.clicked.connect(self.save_selection)

        layout.addWidget(select_all_button)
        layout.addWidget(deselect_all_button)
        layout.addWidget(save_button)

        self.setLayout(layout)

        self.tree_widget.itemChanged.connect(self.handle_item_change)

    def load_and_display_json(self, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        data = self.load_json_file(file_path)
        if data:
            self.populate_tree(data, self.tree_widget)

    def load_json_file(self, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return data
        except Exception as e:
            logging.error(f"Error loading JSON file {file_path}: {e}")
            return None

    def populate_tree(self, data, parent_item=None, parent_key=""):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if isinstance(data, dict):
            for key, value in data.items():
                current_key = key if not parent_key else f"{parent_key}.{key}"
                display_key = key if not parent_key else key.split(".")[-1]

                if parent_item is None:
                    item = QTreeWidgetItem()
                    self.tree_widget.addTopLevelItem(item)
                else:
                    item = QTreeWidgetItem(parent_item)

                item.setText(0, display_key)
                item.setText(1, str(value))
                item.setCheckState(0, 0)  # Set checkbox for the key

                if isinstance(value, (dict, list)):
                    # Recursively populate the tree for nested structures
                    self.populate_tree(value, parent_key=current_key, parent_item=item)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_key = str(i) if not parent_key else f"{parent_key}.{i}"

                if parent_item is None:
                    child_item = QTreeWidgetItem()
                    self.tree_widget.addTopLevelItem(child_item)
                else:
                    child_item = QTreeWidgetItem(parent_item)

                child_item.setText(0, current_key)
                child_item.setText(1, str(item))
                child_item.setCheckState(0, 0)  # Set checkbox for the key

                if isinstance(item, (dict, list)):
                    # Recursively populate the tree for nested structures
                    self.populate_tree(
                        item, parent_key=current_key, parent_item=child_item
                    )

    # THIS CODE WORKS FOR STORING THE PARENT.KEY1.KEY2 IN A LIST OF SELECTED KEYS
    def get_selected_keys(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        selected_keys = []
        self.collect_selected_keys(self.tree_widget.invisibleRootItem(), selected_keys)
        return selected_keys

    def collect_selected_keys(
        self, item, selected_keys, parent_key="", recorded_keys=None
    ):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if recorded_keys is None:
            recorded_keys = set()

        if not parent_key:
            parent_key = None

        # Check if the item is checked
        if item.checkState(0) == Qt.Checked:
            # If the item has children, include its checked children
            if item.childCount() > 0:
                for i in range(item.childCount()):
                    child = item.child(i)
                    key = child.text(0)
                    current_key = key if not parent_key else f"{parent_key}.{key}"

                    # Recursively collect for nested structures
                    self.collect_selected_keys(
                        child,
                        selected_keys,
                        parent_key=current_key,
                        recorded_keys=recorded_keys,
                    )

            # If the item is a leaf, add it to selected_keys
            elif item.childCount() == 0:
                if parent_key not in recorded_keys:
                    selected_keys.append(parent_key)
                    recorded_keys.add(parent_key)

        # Recursively check each child, including unchecked ones
        for i in range(item.childCount()):
            child = item.child(i)
            key = child.text(0)
            current_key = key if not parent_key else f"{parent_key}.{key}"

            # Recursively collect for nested structures
            self.collect_selected_keys(
                child,
                selected_keys,
                parent_key=current_key,
                recorded_keys=recorded_keys,
            )

    def select_all(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.update_checkstate(self.tree_widget.invisibleRootItem(), True)

    def deselect_all(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.update_checkstate(self.tree_widget.invisibleRootItem(), False)

    def contextMenuEvent(self, event):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        menu = QMenu(self)
        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(
            lambda _, item=self.tree_widget.invisibleRootItem(): self.update_checkstate(
                item, True
            )
        )
        deselect_all_action = QAction("Deselect All", self)
        deselect_all_action.triggered.connect(
            lambda _, item=self.tree_widget.invisibleRootItem(): self.update_checkstate(
                item, False
            )
        )
        menu.addAction(select_all_action)
        menu.addAction(deselect_all_action)
        menu.exec_(event.globalPos())

    def update_checkstate(self, item, checked):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)

        # Recursively update the check state for children
        for i in range(item.childCount()):
            child = item.child(i)
            self.update_checkstate(child, checked)

        # Collect selected keys
        if checked:
            self.collect_selected_keys(item, self.selected_keys)

    def handle_item_change(self, item, column):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if column == 0:  # Check column
            self.update_checkstate(item, item.checkState(column) == 2)

    def save_selection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Show a dialog to get the multiline description
        description, ok = QInputDialog.getMultiLineText(
            self, "Enter Description", "Description:", ""
        )

        if ok:
            selected_keys = self.get_selected_keys()

            # Check if the user_data/collection_selection folder exists, if not, create it
            collection_folder_path = os.path.join(
                os.path.dirname(__file__), "../user_data/collection_selections"
            )
            os.makedirs(collection_folder_path, exist_ok=True)

            # Generate the file name based on the current date, time, and collection name
            current_datetime = QDateTime.currentDateTime().toString("yyyyMMdd_HHmmss")
            file_name = f"{current_datetime}_{self.selected_collection}.json"

            # Construct the full path to the file
            file_path = os.path.join(collection_folder_path, file_name)

            # Save the selected items to the JSON file along with the description
            with open(file_path, "w") as file:
                data = {
                    "timestamp": current_datetime,
                    "zendesk_instance": self.zendesk_subdomain,
                    "collection_name": self.selected_collection,
                    "selected_keys": selected_keys,
                    "report_description": description,
                }
                json.dump(data, file, indent=4)

            logging.info(f"Selection saved to: {file_path}")
