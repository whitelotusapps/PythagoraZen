import inspect
import json
import logging

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog

from framework.api_paginator import ZendeskApiPaginator
from framework.instance_database_operations_api_endpoint_config import (
    ZendeskInstanceDatabaseOperationsMongoDB,
)
from framework.instance_selection_dialog import InstanceSelectionDialog
from framework.logging_handler import PythagoraZenLogger
from framework.mongodb_collection_selection_dialog import (
    MongoDBCollectionSelectionDialog,
)
from framework.plugin_interface import PluginInterface
from framework.skeleton_tree_view_and_selection import SkeletonTreeViewAndSelection


class Plugin(PluginInterface, QObject):
    update_content_signal = pyqtSignal(dict, list, str, str, bool, bool, dict)

    def __init__(self, main_app, signal_manager):
        QObject.__init__(self)
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.main_app = main_app
        self.signal_manager = signal_manager
        self.plugin_name = "Skeleton Tree View and Selection"
        self.selected_instance = None  # Initialize selected_instance
        self.instance_operations = None
        self.show_window = False
        self.skeleton_window = None
        self.skeleton_instance = SkeletonTreeViewAndSelection

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

    def get_populated_value(self, field_name):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug(f"FIELD NAME: {field_name}")
        logging.debug(
            f"COLLECTION: {self.selected_collection.db.name}.{self.selected_collection.collection.name}"
        )

        if not isinstance(field_name, str):
            logging.error("field_name must be a string")
            logging.error(f"PASSED FIELD: {field_name}")

        if not hasattr(self.selected_collection, "find_one") or not callable(
            getattr(self.selected_collection, "find_one")
        ):
            logging.error("collection must be a valid MongoDB collection")
            logging.error(f"PASSED COLLECTION: {self.selected_collection}")

        query = {field_name: {"$exists": True, "$ne": []}}
        result = self.selected_collection.find_one(query, {field_name: 1, "_id": 0})

        if result:
            return result.get(field_name)

        logging.warning(f"No documents found with the field '{field_name}'")
        return None

    def create_skeleton(self, data):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.info("create_skeleton method called")
        logging.debug(f"collection: {self.selected_collection}")
        skeleton = {}

        # Iterate through documents
        for document in self.selected_collection.find():
            self.process_document(document, skeleton)

        # Sort root keys
        sorted_keys = sorted(skeleton.keys())

        # Create a new dictionary with sorted keys
        sorted_dict = {key: skeleton[key] for key in sorted_keys}

        # return skeleton
        return sorted_dict

    def extract_first_items(self, d):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        new_dict = {}
        for key, value in d.items():
            if isinstance(value, list) and value:
                new_dict[key] = [value[0]]
            elif isinstance(value, dict):
                new_dict[key] = self.extract_first_items(value)
            else:
                new_dict[key] = value
        return new_dict

    def process_document(self, document, skeleton, depth=0):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        for key, value in document.items():

            if (
                not isinstance(value, dict)
                and not isinstance(value, list)
                and depth == 0
                and key not in skeleton
            ):
                logging.debug(f"1 KEY: {key}\tDEPTH: {depth}")
                if not value:
                    logging.debug(
                        f"1 KEY: {key}\tVALUE: {value}\t\tFINDING POPULATED VALUE..."
                    )
                    populated_value = self.get_populated_value(key)
                    # print(f"\nD: {depth} K: {key} V: {json.dumps(populated_value, default=str, indent=4)}\n")
                    skeleton[key] = populated_value
                else:
                    skeleton[key] = value

                self.process_document(document, skeleton, depth + 1)
                # skeleton[key] = value
                # print(f"\nD: {depth} K: {key} V: {value}\n")
                # process_document(document, skeleton, collection, depth + 1)

            if isinstance(value, dict) and key not in skeleton and depth == 0:
                logging.debug(f"2 KEY: {key}\tDEPTH: {depth}")
                if not value:
                    logging.debug(
                        f"2 KEY: {key}\tVALUE: {value}\t\tFINDING POPULATED VALUE..."
                    )
                    populated_value = self.get_populated_value(key)
                    # print(f"\nD: {depth} K: {key} V: {json.dumps(populated_value, default=str, indent=4)}\n")
                    skeleton[key] = populated_value
                else:
                    logging.debug(f"\nD: {depth} K: {key} V: {value}\n")
                    skeleton[key] = value

                self.process_document(document, skeleton, depth + 1)
                # skeleton[key] = value
                # print(f"\nD: {depth} K: {key} V: {value}\n")
                # process_document(document, skeleton, collection, depth + 1)

            # if isinstance(value, list) and depth == 0 and key not in skeleton:
            if isinstance(value, list) and key not in skeleton:
                if not value:
                    logging.debug(f"3 KEY: {key}\tDEPTH: {depth}")
                    populated_value = self.get_populated_value(key)
                    # print(f"\nD: {depth} K: {key} V: {json.dumps(populated_value, default=str, indent=4)}\n")
                    skeleton[key] = populated_value
                    self.process_document(document, skeleton, depth + 1)
                else:
                    logging.debug(f"4 KEY: {key}\tDEPTH: {depth}")
                    if isinstance(value, list) and list:
                        # print(f"5 KEY {key}")
                        # print(f"{key} VALUE[0]:\n{json.dumps(value[0], default=str, indent=4)}")
                        if isinstance(value[0], dict):
                            logging.debug(f"6 KEY {key}")
                            skeleton[key] = self.extract_first_items(value[0])
                        else:
                            logging.debug(f"7 KEY {key}")
                            skeleton[key] = value
                    if isinstance(value, list) and not list:
                        logging.debug(f"8 KEY {key}")
                        populated_value = self.get_populated_value(key)
                        skeleton[key] = populated_value

                    self.process_document(document, skeleton, depth + 1)

    def interact(self, plugin_window):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        instance_selection_dialog = InstanceSelectionDialog(
            self.main_app.database_operations
        )
        result = instance_selection_dialog.exec_()

        if result == QDialog.Accepted:
            self.selected_instance = instance_selection_dialog.selected_instance
            (
                zendesk_subdomain,
                zendesk_api_user_email_address,
                zendesk_api_key,
            ) = instance_selection_dialog.selected_instance

            logging.debug(f"self.selected_instance: {self.selected_instance}")
            zendesk_subdomain, _, _ = self.selected_instance
            self.instance_operations = ZendeskInstanceDatabaseOperationsMongoDB(
                zendesk_subdomain, ""
            )

            try:
                collection_selection_dialog = MongoDBCollectionSelectionDialog(
                    self.instance_operations, zendesk_subdomain
                )
                collection_selection_result = collection_selection_dialog.exec_()

                if collection_selection_result == QDialog.Accepted:
                    selected_collection_name = (
                        collection_selection_dialog.selected_collection
                    )
                    logging.info(
                        f"Selected Collection Name: {selected_collection_name}"
                    )
                    self.selected_collection = self.instance_operations.db[
                        selected_collection_name
                    ]
                    logging.info(f"DATABASE:\n{self.instance_operations.db}")
                    logging.info(f"Selected Collection: {self.selected_collection}")

                    # Call the appropriate method to fetch the data from MongoDB
                    # Modify this according to how your data is fetched in your actual code
                    data = self.selected_collection.find()

                    # Create and show the SkeletonTreeViewAndSelection window
                    result_skeleton = self.create_skeleton(data)
                    logging.debug(
                        f"RESULT SKELETON:\n{json.dumps(result_skeleton, default=str, indent=4)}"
                    )
                    logging.debug(
                        f"self.selected_collection: {self.selected_collection}"
                    )
                    self.skeleton_window = SkeletonTreeViewAndSelection(
                        result_skeleton, selected_collection_name, zendesk_subdomain
                    )
                    logging.debug("After skeleton_window")

                    # Initialize result_skeleton before the try block
                    # result_skeleton = None # Setting this to None throws an error

                    # Show the SkeletonTreeViewAndSelection window
                    try:
                        # content, api_response, zendesk_subdomain, selected_collection, show_table_button, show_api_button, skeleton_data, skeleton_window_title
                        self.update_content_signal.emit(
                            {},
                            [],
                            zendesk_subdomain,
                            selected_collection_name,
                            True,
                            True,
                            result_skeleton,
                        )
                    except Exception as e:
                        # Handle the exception (you can customize this part based on your needs)
                        logging.error(f"An error occurred: {e}")

                    self.skeleton_window.show()
                    logging.debug("After skeleton_window.show()")

            except Exception as generic_exception:
                # Handle any other exceptions
                logging.error(f"An unexpected error occurred: {generic_exception}")
            finally:
                # Code that will be executed no matter what, for cleanup or finalization
                # Close resources, clean up, etc.
                logging.info(
                    "Finally block: Cleaning up resources or finalizing actions"
                )
