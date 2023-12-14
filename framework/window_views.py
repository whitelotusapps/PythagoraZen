import inspect

# window_views.py
import json
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAbstractItemView, QLabel, QShortcut, QTableWidgetItem

from framework.logging_handler import PythagoraZenLogger

from framework.copy_handler import CopyHandler



class ViewManager:
    last_context_menu = None

    def __init__(self, module_window):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.module_window = module_window
        self.table = module_window.table
        self.json_browser = module_window.json_browser
        self.central_widget = module_window.central_widget
        self.api_response_button = module_window.api_response_button
        self.table_button = module_window.table_button
        self.current_view = self.table
        self.export_manager = module_window.export_manager
        self.export_manager.set_buttons(
            module_window.html_export_button,
            module_window.pdf_export_button,
            module_window.csv_export_button,
            module_window.xlsx_export_button,
        )

        self.table_button.clicked.connect(self.show_table_view)

        # Create a shortcut for copying selected data
        self.copy_shortcut = QShortcut(QKeySequence.Copy, self.table)
        self.copy_shortcut.activated.connect(self.copy_selected_data)

        # Set the initial visibility
        self.json_browser.hide()
        self.table.show()  # Show the table by default
        self.current_view = self.table

    def copy_selected_data(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Get the selected data and call the CopyHandler to copy it
        selected_ranges = self.table.selectedRanges()
        if selected_ranges:
            CopyHandler.copy_selection(self.table)

    def display_data_in_table(self, data_list):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.table.clear()

        if not data_list:
            return

        # Extract attribute names from the first item in the data_list
        attribute_names = list(data_list[0].keys())

        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.table.setColumnCount(len(attribute_names))

        for i, attribute in enumerate(attribute_names):
            item = QTableWidgetItem(attribute)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setHorizontalHeaderItem(i, item)

        self.table.setRowCount(len(data_list))

        for i, user_data in enumerate(data_list):
            for j, attribute in enumerate(attribute_names):
                value = str(user_data.get(attribute, ""))

                # Check if the value is a URL and make it clickable
                if "url" in attribute.lower() or "link" in attribute.lower():
                    label = QLabel('<a href="{0}">{0}</a>'.format(value))
                    label.setOpenExternalLinks(True)
                    label.setAlignment(Qt.AlignCenter)
                    self.table.setCellWidget(i, j, label)
                else:
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)

                # Check if the value is an email address and make it clickable
                if "email" in attribute.lower():
                    label = QLabel('<a href="mailto:{0}">{0}</a>'.format(value))
                    label.setOpenExternalLinks(True)
                    label.setAlignment(Qt.AlignCenter)
                    self.table.setCellWidget(i, j, label)
                else:
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)

        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # print(f"Displaying data in table:\n{data_list}")
        # print(f"Attribute names: {attribute_names}")

        self.switch_view(self.table)
        self.export_manager.show_save_buttons()

    def get_nested_value(self, data, attribute):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Recursively get nested value
        keys = attribute.split(".")
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    def display_api_response_as_json(self, api_response):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # print(f"API RESPONSE:\n\n{api_response}")
        # print(f"API RESPONSE DATA TYPE: {type(api_response)}")
        # print(f"DISPLAY API RESPONSE VIEW:\n{json.dumps(api_response, indent=4)}")
        self.json_browser.clear()
        self.json_browser.setPlainText(json.dumps(api_response, default=str, indent=4))
        self.switch_view(self.json_browser)
        self.api_response_button.show()  # Show the button after displaying API response

    @staticmethod
    def create_copy_menu(table, pos):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        menu = QMenu()

        copy_action = QAction("Copy", table)
        copy_action.triggered.connect(lambda: CopyHandler.copy_selection(table))
        menu.addAction(copy_action)

        # Set the last context menu
        ViewManager.last_context_menu = menu

        menu.exec_(table.viewport().mapToGlobal(pos))

    def show_api_response_view(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Hide the JSON view when switching to the table view
        self.json_browser.hide()
        self.switch_view(self.json_browser)
        self.export_manager.hide_save_buttons()

    def show_context_menu(self, pos):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Check if the last context menu is visible
        if self.last_context_menu and self.last_context_menu.isVisible():
            return

        # Use the CopyHandler to create and handle the context menu
        logging.info("create_copy_menu(table, pos) called")
        CopyHandler.create_copy_menu(self.table, pos)

    def clear_views(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.table.clear()
        self.json_browser.clear()

    def show_table_view(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Hide the JSON view when switching to the table view
        self.json_browser.hide()
        self.switch_view(self.table)
        self.export_manager.show_save_buttons()

    def switch_view(self, view):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.current_view.hide()
        self.current_view = view
        self.current_view.show()

        if self.current_view == self.table:
            self.central_widget.layout().addWidget(self.table)
            self.central_widget.layout().addWidget(self.json_browser)
        elif self.current_view == self.json_browser:
            self.central_widget.layout().addWidget(self.json_browser)
            self.central_widget.layout().addWidget(self.table)
