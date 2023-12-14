import inspect

# Update the Plugin class in your plugin file
import logging

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog

# from framework.instance_database_operations_mongodb import ZendeskInstanceDatabaseOperationsMongoDB
from framework.instance_database_operations_api_endpoint_config import (
    ZendeskInstanceDatabaseOperationsMongoDB,
)
from framework.instance_selection_dialog import InstanceSelectionDialog
from framework.key_selection_dialog import KeySelectionDialog
from framework.logging_handler import PythagoraZenLogger
from framework.mongodb_collection_selection_dialog import (
    MongoDBCollectionSelectionDialog,
)
from framework.plugin_interface import PluginInterface
from pipelines.user_updates import PipelineOperations


class Plugin(PluginInterface, QObject):
    update_content_signal = pyqtSignal(list, list, str, str, bool, bool, dict)

    def __init__(self, main_app, signal_manager):
        QObject.__init__(self)
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.main_app = main_app
        self.signal_manager = signal_manager
        self.plugin_name = "MongoDB - Select Collection - Pipeline"
        self.selected_instance = None  # Initialize selected_instance
        self.instance_operations = None
        self.show_window = True

    def requires_plugin_window(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Return True if a plugin window is required, False otherwise
        return True

    def use_databases(self, selected_instance: InstanceSelectionDialog):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.selected_instance = selected_instance

    def supports_mongodb(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return True

    def interact(self, plugin_window):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # self.filename()
        instance_selection_dialog = InstanceSelectionDialog(
            self.main_app.database_operations
        )
        # print(f"INSTANCE: {instance_selection_dialog}")
        result = instance_selection_dialog.exec_()

        if result == QDialog.Accepted:
            self.selected_instance = instance_selection_dialog.selected_instance
            (
                zendesk_subdomain,
                zendesk_api_user_email_address,
                zendesk_api_key,
            ) = instance_selection_dialog.selected_instance
            self.instance_operations = ZendeskInstanceDatabaseOperationsMongoDB(
                zendesk_subdomain, ""
            )
            # print(f"ZENDESK SUBDOMAIN: {zendesk_subdomain}")
            """
            pipeline_operations = PipelineOperations(
                self.instance_operations.users_collection,
                self.instance_operations.organizations_collection,
                zendesk_subdomain  # Pass the zendesk_subdomain here
            )
            """

            try:
                collection_selection_dialog = MongoDBCollectionSelectionDialog(
                    self.instance_operations, zendesk_subdomain
                )
                collection_selection_result = collection_selection_dialog.exec_()

                if collection_selection_result == QDialog.Accepted:
                    selected_collection = (
                        collection_selection_dialog.selected_collection
                    )
                    logging.info(f"Selected Collection: {selected_collection}")

                    self.instance_operations = ZendeskInstanceDatabaseOperationsMongoDB(
                        zendesk_subdomain, selected_collection
                    )
                    logging.info(f"DATABASE:\n{self.instance_operations.db}")
                    # data = self.instance_operations.query_collection()
                    data = self.instance_operations.query_collection({}, projection={})

                    all_keys = {
                        key for item in data for key in item.keys() if key != "_id"
                    }

                    # self.filename()
                    logging.info(f"ALL KEYS IS TYPE: {type(all_keys)}")
                    logging.info(f"ALL KEYS:\n{all_keys}")

                    key_selection_dialog = KeySelectionDialog(
                        all_keys, zendesk_subdomain, selected_collection
                    )
                    result = key_selection_dialog.exec_()

                    if result == QDialog.Accepted:
                        """
                        # Now plugin_instance is defined
                        plugin_instance = Plugin(self.main_app)
                        # Pass plugin_name when creating the PluginWindow instance
                        plugin_window = PluginWindow(self, plugin_instance.plugin_name)
                        plugin_window.show()
                        """
                        selected_keys = key_selection_dialog.selected_keys

                        # Filter the data based on selected keys
                        filtered_ticket_fields = []

                        for ticket_field in data:
                            # Create a new dictionary for each ticket field including only selected keys
                            filtered_ticket_fields.append(
                                {
                                    key: ticket_field[key]
                                    for key in selected_keys
                                    if key in ticket_field
                                }
                            )

                    # Check if the selected collection is "users"
                    if (
                        selected_collection == "users"
                        and "organization_id" in selected_keys
                    ):
                        # self.filename()
                        logging.info("USER PIPELINE CONDITION MET")
                        logging.info(f"ZENDESK SUBDOMAIN: {zendesk_subdomain}")
                        pipeline_operations = PipelineOperations(
                            self.instance_operations.users_collection,
                            self.instance_operations.organizations_collection,
                            self.instance_operations.groups_collection,
                            self.instance_operations.custom_roles_collection,
                            zendesk_subdomain,  # Pass the zendesk_subdomain here
                        )
                        # Use the modified user data from the pipeline
                        modified_users = pipeline_operations.update_user_data()
                        # Update the table view using the modified data
                        # self.filename()
                        # print(f"MODIFIED USERS:\n{json.dumps(modified_users, default=str, indent=4)}")

                        self.update_content_signal.emit(
                            modified_users,
                            list(data),
                            zendesk_subdomain,
                            selected_collection,
                            True,
                            True,
                            {},
                        )
                        if self.show_window:
                            plugin_window.show()
                    else:
                        # For other collections, update the table view with the original data
                        # self.filename()
                        # print(f"filtered_ticket_fields:\n{json.dumps(list(filtered_ticket_fields), default=str, indent=4)}")
                        self.update_content_signal.emit(
                            list(filtered_ticket_fields),
                            data,
                            zendesk_subdomain,
                            selected_collection,
                            True,
                            True,
                            {},
                        )
                        # self.update_content_signal.emit(list(data), data, "Ticket Field ID", True, True)

                        # print(f"DATA TYPE: {type(data)}")
                        # print(f"DATA:\n{json.dumps(data[0], default=str, indent=4)}")
                        # print(f"DATA:\n{data}")
                        # Extract all unique keys from the dictionaries
            except Exception as e:
                error_message = str(e)
                self.update_content_signal.emit(
                    [f"error: {error_message}"], [], "", False, False
                )
        else:
            # Handle the case when source_instance is None
            logging.warning("No source instance found.")
