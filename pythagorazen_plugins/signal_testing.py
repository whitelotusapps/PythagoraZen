import inspect
import logging

from PyQt5.QtCore import QObject, pyqtSignal

from framework.api_paginator import ZendeskApiPaginator
from framework.instance_selection_dialog import InstanceSelectionDialog
from framework.logging_handler import PythagoraZenLogger
from framework.plugin_interface import PluginInterface
from framework.signal_test_file_1 import SignalTestFile1
from framework.signal_test_file_2 import SignalTestFile2


class Plugin(PluginInterface, QObject):
    """ """

    update_content_signal = pyqtSignal(dict, list, str, bool, bool, dict, str)

    def __init__(self, main_app, signal_manager):
        QObject.__init__(self)
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.main_app = main_app
        self.signal_manager = signal_manager
        self.plugin_name = "Signal Testing"
        self.selected_instance = None  # Initialize selected_instance
        self.instance_operations = None
        self.show_window = False
        self.skeleton_window = None

        self.signal_test_file_1 = SignalTestFile1(self.main_app, self.signal_manager)
        self.signal_test_file_2 = SignalTestFile2(self.main_app, self.signal_manager)

        # Connect the signals using SignalManager
        self.signal_manager.connect_instances(
            self.signal_test_file_1,
            "SignalTestFile1",
            "emit_method_1",
            self.signal_test_file_2,
            "SignalTestFile2",
            "slot_in_signal_test_file_2",
        )
        self.signal_manager.connect_instances(
            self.signal_test_file_2,
            "SignalTestFile2",
            "emit_method_2",
            self.signal_test_file_1,
            "SignalTestFile1",
            "slot_in_signal_test_file_1",
        )

        # Instantiate display_reports_window here
        # self.display_reports_window = CollectionSelectionJSONLoader(self.signal_manager)

        # Connect the signals after instantiation
        # self.show_reports_window_signal.connect(self.display_reports_window.show_display_reports_window)

    def use_databases(self, selected_instance: InstanceSelectionDialog):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        """

        :param selected_instance: InstanceSelectionDialog:

        """
        self.selected_instance = selected_instance

    def use_api_paginator(self, paginator: ZendeskApiPaginator):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        """

        :param paginator: ZendeskApiPaginator:

        """
        self.paginator_instance = paginator

    def supports_pagination(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        """ """
        return True

    def supports_mongodb(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        """ """
        return True

    def requires_plugin_window(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        """ """
        # Return True if a plugin window is required, False otherwise
        return True

    def interact(self, plugin_window):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        """

        :param plugin_window:

        """
        # Emit signals without calling them as functions
        self.signal_test_file_1.signal_test_file_1_emit_method_1()
        self.signal_test_file_2.signal_test_file_2_emit_method_2()
