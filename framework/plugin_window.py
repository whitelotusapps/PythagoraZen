import logging
import inspect

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from framework.logging_handler import PythagoraZenLogger

from framework.collection_selection_json_loader import CollectionSelectionJSONLoader
from framework.export_manager import ExportManager
from framework.json_highlighter import JsonSyntaxHighlighter
from framework.skeleton_tree_view_and_selection import SkeletonTreeViewAndSelection
from framework.window_views import ViewManager


class PluginWindow(QMainWindow):
    update_content_signal = pyqtSignal(list, dict, str, str, bool, bool, dict)
    show_reports_window_signal = pyqtSignal()

    def __init__(self, plugin_instance, plugin_name):
        super().__init__(
            None,
            Qt.Window
            | Qt.CustomizeWindowHint
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint,
        )
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.plugin_instance = plugin_instance
        self.plugin_name = plugin_name
        self.skeleton_window = None
        self.display_reports_window = None
        # logger = logging.getLogger(__name__)
        self.setWindowTitle(plugin_name)
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

        self.api_response_button.clicked.connect(
            self.view_manager.show_api_response_view
        )

        # self.show()

    def show_window(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Call init_ui when you explicitly want to show the window
        self.init_ui()

    def init_ui(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(layout)

        self.label = QLabel(self.plugin_name)
        layout.addWidget(self.label)

        splitter = QSplitter(self)
        layout.addWidget(splitter)

        self.table = QTableWidget(self)
        splitter.addWidget(self.table)

        self.json_browser = QTextBrowser(self)
        splitter.addWidget(self.json_browser)

        self.table_button = QPushButton("Table View")
        self.api_response_button = QPushButton("API Response View")

        # Set the initial visibility of save buttons to be hidden
        self.table_button.hide()

        self.api_response_button.hide()  # Initially hide the button

        self.json_highlighter = JsonSyntaxHighlighter(self.json_browser.document())
        self.update_content_signal.connect(self.update_content)

        self.current_view = self.table

        self.html_export_button = QPushButton("Export to HTML")
        self.pdf_export_button = QPushButton("Export to PDF")
        self.csv_export_button = QPushButton("Export to CSV")
        self.xlsx_export_button = QPushButton("Export to XLSX")

        # Set the initial visibility of save buttons to be hidden
        self.html_export_button.hide()
        self.pdf_export_button.hide()
        self.csv_export_button.hide()
        self.xlsx_export_button.hide()

        layout.addWidget(self.table_button)
        layout.addWidget(self.api_response_button)
        layout.addWidget(self.html_export_button)
        layout.addWidget(self.pdf_export_button)
        layout.addWidget(self.csv_export_button)
        layout.addWidget(self.xlsx_export_button)

        # Initialize ExportManager after buttons are created
        self.export_manager = ExportManager(self.table)
        self.export_manager.set_buttons(
            self.html_export_button,
            self.pdf_export_button,
            self.csv_export_button,
            self.xlsx_export_button,
        )
        self.html_export_button.clicked.connect(self.export_manager.export_to_html)
        self.pdf_export_button.clicked.connect(self.export_manager.export_to_pdf)
        self.csv_export_button.clicked.connect(self.export_manager.export_to_csv)
        self.xlsx_export_button.clicked.connect(self.export_manager.export_to_xlsx)

        self.view_manager = ViewManager(self)

    def update_content(
        self,
        content,
        api_response,
        zendesk_subdomain,
        selected_collection,
        show_table_button,
        show_api_button,
        skeleton_data,
    ):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug(f"content: {content}")
        logging.debug(f"api_response: {api_response}")
        logging.debug(f"zendesk_subdomain: {zendesk_subdomain}")
        logging.debug(f"selected_collection: {selected_collection}")
        logging.debug(f"show_table_button: {show_table_button}")
        logging.debug(f"show_api_button: {show_api_button}")
        logging.debug(f"skeleton_data: {skeleton_data}")

        if "error" in content:
            self.label.setText(f"Error: {content['error']}")
        else:
            # self.label.setText("Data View")
            self.label.setText(
                f"Zendesk Instance (database): {zendesk_subdomain}\nCollection: {selected_collection}"
            )
            self.label.setWordWrap(True)  # Enable word wrapping for the QLabel
            self.label.setTextInteractionFlags(
                Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
            )

        # Adjust visibility based on the parameters
        self.api_response_button.setVisible(show_api_button)
        self.table_button.setVisible(show_table_button)

        self.view_manager.display_api_response_as_json(api_response)
        self.view_manager.display_data_in_table(content)

        self.skeleton_data = skeleton_data
        self.skeleton_window_title = selected_collection

    def show_skeleton_view(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug(f"self.skeleton_data:\n{self.skeleton_data}")
        logging.debug(f"self.skeleton_window_title: {self.skeleton_window_title}")
        # Delegate the responsibility to the plugin instance
        if hasattr(self.plugin_instance, "show_skeleton_view"):
            # Check if the SkeletonTreeViewAndSelection window is already created
            if self.skeleton_window is None:
                # Create and show the SkeletonTreeViewAndSelection window
                self.skeleton_window = SkeletonTreeViewAndSelection(
                    self.skeleton_data, self.skeleton_window_title
                )
                self.skeleton_window.show()
            else:
                # If the window is already created, update its content with new data
                # data = self.selected_collection.find()  # Fetch the new data
                result_skeleton = self.plugin_instance.create_skeleton(
                    self.skeleton_data
                )
                self.skeleton_window.update_content(
                    result_skeleton, self.skeleton_window_title
                )

    def show_display_reports_window(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Check if the window is already created and visible
        if (
            self.display_reports_window is None
            or not self.display_reports_window.isVisible()
        ):
            # If not, create a new instance
            self.display_reports_window = CollectionSelectionJSONLoader()
            # Connect the signals for the new instance
            self.show_reports_window_signal.connect(
                self.display_reports_window.show_display_reports_window
            )
            # Show the window
            self.display_reports_window.show()
        else:
            # If the window is already visible, bring it to the front
            self.display_reports_window.raise_()
            self.display_reports_window.activateWindow()
