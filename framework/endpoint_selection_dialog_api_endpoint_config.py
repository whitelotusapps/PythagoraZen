import inspect

# instance_selection_dialog.py
import logging
import os

from PyQt5.QtWidgets import QDialog

from framework.config_manager import ConfigManager

# from framework.instance_database_operations_api_endpoint_config import \
#    ZendeskInstanceDatabaseOperationsMongoDB
from framework.key_selection_dialog import KeySelectionDialog

from framework.logging_handler import PythagoraZenLogger


class APIConfigEndpointSelectionDialog(QDialog):
    def __init__(self, zendesk_subdomain):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Get the absolute path of the current script
        script_path = os.path.abspath(__file__)
        self.selected_active_endpoints_without_dependency_names_selection = set()
        self.selected_active_endpoints_with_dependency_names_selection = set()
        self.config_manager = ConfigManager()
        self.zendesk_subdomain = zendesk_subdomain
        self.api_endpoint_config_json = os.path.join(
            os.path.dirname(os.path.dirname(script_path)),
            "api_endpoints",
            "api_endpoint_config.json",
        )
        logging.info(f"API ENDPOINT CONFIG FILE: {self.api_endpoint_config_json}")
        logging.info(f"SUBDOMAIN: {self.zendesk_subdomain}")
        # self.init_ui()

    def get_selected_active_endpoints_without_dependency_names_selection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoint_names = (
            self.config_manager.get_active_endpoints_without_dependency_names()
        )

        key_selection_dialog = KeySelectionDialog(
            active_endpoint_names,
            self.zendesk_subdomain,
            "API Endpoint Without Dependencies Selection",
        )
        logging.info("AFTER key_selection_dialog")
        result = key_selection_dialog.exec_()
        logging.info(f"RESULT: {result}")
        # Check the selected endpoints
        self.selected_active_endpoints_without_dependency_names_selection = (
            key_selection_dialog.selected_keys
        )
        logging.info(
            f"Selected Endpoints: {self.selected_active_endpoints_without_dependency_names_selection}"
        )
        logging.info(
            f"Number of selected keys: {len(self.selected_active_endpoints_without_dependency_names_selection)}"
        )

        return self.selected_active_endpoints_without_dependency_names_selection

    def get_selected_active_endpoints_with_dependency_names_selection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoint_names = (
            self.config_manager.get_active_endpoint_with_dependency_names()
        )

        key_selection_dialog = KeySelectionDialog(
            active_endpoint_names,
            self.zendesk_subdomain,
            "API Endpoint Dependencies Selection",
        )
        logging.info("AFTER key_selection_dialog")
        result = key_selection_dialog.exec_()
        logging.info(f"RESULT: {result}")
        # Check the selected endpoints
        self.selected_active_endpoints_with_dependency_names_selection = (
            key_selection_dialog.selected_keys
        )
        logging.info(
            f"Selected Endpoints: {self.selected_active_endpoints_with_dependency_names_selection}"
        )
        logging.info(
            f"Number of selected keys: {len(self.selected_active_endpoints_with_dependency_names_selection)}"
        )

        return self.selected_active_endpoints_with_dependency_names_selection
