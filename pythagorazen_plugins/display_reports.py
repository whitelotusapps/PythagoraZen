import inspect
import logging

from PyQt5.QtCore import QObject, pyqtSignal

from framework.api_paginator import ZendeskApiPaginator
from framework.collection_selection_json_loader import CollectionSelectionJSONLoader
from framework.instance_selection_dialog import InstanceSelectionDialog
from framework.logging_handler import PythagoraZenLogger
from framework.plugin_interface import PluginInterface


class Plugin(PluginInterface, QObject):
    update_content_signal = pyqtSignal(dict, list, str, str, bool, bool, dict)
    show_reports_window_signal = pyqtSignal()

    def __init__(self, main_app, signal_manager):
        QObject.__init__(self)
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.main_app = main_app
        self.signal_manager = signal_manager
        self.plugin_name = "Display Reports"
        self.selected_instance = None  # Initialize selected_instance
        self.instance_operations = None
        self.show_window = False
        self.skeleton_window = None

        # Instantiate display_reports_window here
        self.display_reports_window = CollectionSelectionJSONLoader()

        # Connect the signals after instantiation
        # self.show_reports_window_signal.connect(self.display_reports_window.show_display_reports_window)

    def use_databases(self, selected_instance: InstanceSelectionDialog):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.selected_instance = selected_instance

    def use_api_paginator(self, paginator: ZendeskApiPaginator):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.paginator_instance = paginator

    def supports_pagination(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return True

    def supports_mongodb(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return True

    def requires_plugin_window(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Return True if a plugin window is required, False otherwise
        return True

    def interact(self, plugin_window):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Connect the signals after instantiation
        self.show_reports_window_signal.connect(
            plugin_window.show_display_reports_window
        )

        # Emit the signal to show the reports window
        self.show_reports_window_signal.emit()
