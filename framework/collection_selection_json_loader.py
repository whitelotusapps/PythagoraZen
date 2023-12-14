import inspect
import json
import logging
import os
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from framework.logging_handler import PythagoraZenLogger
from framework.skeleton_tree_view_and_selection import SkeletonTreeViewAndSelection


class ClickableGroupBox(QGroupBox):
    clicked = pyqtSignal(object, str)  # Signal now emits both data and file path

    def __init__(self, data, file_path, edit_callback=None):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")

        self.data = data
        self.file_path = file_path  # Add file_path attribute
        self.edit_callback = edit_callback

        # Create an "Edit" button
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.handle_edit_click)

        # Create an inner widget and layout for details
        self.inner_widget = QWidget(self)
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.setup_inner_layout()

        # Create an outer layout for "Edit" button and inner layout
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.addWidget(self.inner_widget)
        self.outer_layout.addWidget(self.edit_button)
        self.setLayout(self.outer_layout)

    def setup_inner_layout(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        for title, key in [
            ("Zendesk Instance:", "zendesk_instance"),
            ("Collection Name:", "collection_name"),
            ("Report Description:", "report_description"),
        ]:
            title_label = QLabel(title)
            title_label.setStyleSheet(
                "background-color: white;"
            )  # White background for titles

            data_label = QLabel(self.data[key])
            data_label.setStyleSheet(
                "background-color: yellow;"
            )  # Yellow background for data

            # Enable word wrapping for the data label
            data_label.setWordWrap(True)

            self.inner_layout.addWidget(title_label)
            self.inner_layout.addWidget(data_label)

    def handle_edit_click(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if self.edit_callback:
            self.edit_callback(self.data)

    """
    def mousePressEvent(self, event):
        self.clicked.emit(self.data, self.file_path)  # Pass both data and file path
        super().mousePressEvent(event)
    """

    def mousePressEvent(self, event):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug(f"Clicked on group box. File path: {self.file_path}")
        logging.debug("Data:")
        logging.debug(f"\n{json.dumps(self.data, indent=4)}")
        super().mousePressEvent(event)


class CollectionSelectionJSONLoader(QWidget):
    def __init__(self):
        super().__init__()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Create an instance of SkeletonTreeViewAndSelection
        self.skeleton_tree_view = SkeletonTreeViewAndSelection()
        self.json_folder_path = os.path.join(
            os.path.dirname(__file__), "../user_data/collection_selections"
        )
        self.file_widgets = []

        self.setWindowTitle("JSON Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a child widget for QScrollArea
        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)

        # Wrap the main layout in a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.scroll_content_widget)

        # Create main layout
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        self.load_json_files()

    def load_json_files(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        json_files = [
            f for f in os.listdir(self.json_folder_path) if f.endswith(".json")
        ]

        for json_file in json_files:
            file_path = os.path.join(self.json_folder_path, json_file)
            data = self.load_json_file(file_path)

            if data:
                self.create_file_widget(data)

    def load_json_file(self, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {e}")
            return None

    def create_file_widget(self, data):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.file_path = os.path.join(
            self.json_folder_path, f"{data['timestamp']}.json"
        )
        group_box = ClickableGroupBox(
            data, self.file_path, edit_callback=self.handle_edit_button_click
        )
        group_box.setTitle(f"{self.format_timestamp(data['timestamp'])}")
        group_box.setStyleSheet(
            """
            QGroupBox {
                background-color: white;
            }
        """
        )

        # Add the group box to the layout
        self.scroll_layout.addWidget(group_box)

    def format_timestamp(self, timestamp):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Convert timestamp to datetime object
        dt_object = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")

        # Format datetime object in long form
        formatted_timestamp = dt_object.strftime("%A, %B %d, %Y %I:%M%p")

        return formatted_timestamp

    def handle_group_box_click(self, data, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Handle the click on the group box here, e.g., show more details
        print(
            f"File path: {file_path}\nClicked on group box:\n{json.dumps(data, indent=4)}"
        )

    def handle_edit_button_click(self, data):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Handle the click on the "Edit" button here
        print(f"Clicked on Edit button for: {data}")

    def show_display_reports_window(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.show()
