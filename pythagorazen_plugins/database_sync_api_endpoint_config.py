import json
import logging
import re

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QProgressBar, QProgressDialog

from framework.api_paginator import ZendeskApiPaginator
from framework.config_manager import ConfigManager
from framework.endpoint_selection_dialog_api_endpoint_config import (
    APIConfigEndpointSelectionDialog,
)
from framework.instance_database_operations_api_endpoint_config import (
    ZendeskInstanceDatabaseOperationsMongoDB,
)
from framework.instance_selection_dialog import InstanceSelectionDialog
from framework.logging_handler import PythagoraZenLogger
from framework.plugin_interface import PluginInterface


class Plugin(PluginInterface, QObject):
    update_content_signal = pyqtSignal(dict, list, str, bool, bool, dict, str)

    def __init__(self, main_app, signal_manager):
        QObject.__init__(self)
        self.main_app = main_app
        self.signal_manager = signal_manager
        self.config_manager = ConfigManager()
        self.plugin_name = "Dataabase Sync - API Endpoint Config"
        self.paginator_instance = None  # Store the paginator instance here
        self.selected_instance = None  # Initialize selected_instance
        self.instance_operations = None
        self.show_window = False
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        
    def requires_plugin_window(self):
        # Return True if a plugin window is required, False otherwise
        return True

    def use_databases(self, selected_instance: InstanceSelectionDialog):
        self.selected_instance = selected_instance

    def use_api_paginator(self, paginator: ZendeskApiPaginator):
        self.paginator_instance = paginator

    def supports_pagination(self):
        return True

    def supports_mongodb(self):
        return True

    """
    def extract_resource_name(self, endpoint):
        # Use a regular expression to find text within curly braces
        matches = re.findall(r'{(.*?)}', endpoint)

        if matches:
            # Take the first match, remove "_id" if it exists, and add "s" at the end if not already present
            resource_name = matches[0]
            if resource_name.endswith('_id'):
                resource_name = resource_name[:-3]  # Remove the trailing "_id"
            if not resource_name.endswith('s'):
                resource_name += 's'
            return resource_name
        else:
            # Return a default value or raise an exception based on your requirements
            return None
    """

    def interact(self, plugin_window):
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
            # Create ZendeskInstanceDatabaseOperations for the selected instance
            # self.filename()
            logging.info(
                f"INSTANCE: {self.selected_instance}"
            )  # THIE LINE WILL CONTAIN SENSITIVE INFORMATION
            logging.info(f"SUBDOMAIN: {zendesk_subdomain}")
            # self.instance_operations = ZendeskInstanceDatabaseOperationsMongoDB(zendesk_subdomain)

            endpoint_dialog = APIConfigEndpointSelectionDialog(zendesk_subdomain)
            # Retrieve the selected endpoints
            selected_active_endpoint_names = (
                endpoint_dialog.get_selected_active_endpoints_without_dependency_names_selection()
            )
            logging.info(f"Selected endpoints:\n{selected_active_endpoint_names}")

            if len(selected_active_endpoint_names) == 1:
                number_of_selected_endpoints = len(selected_active_endpoint_names)

            if len(selected_active_endpoint_names) > 1:
                number_of_selected_endpoints = len(selected_active_endpoint_names) + 1

            empty_endpoints = []
            endpoints_with_errors = []
            populated_endpoints = 0
            # Set up the progress dialog
            progress_dialog = QProgressDialog(
                "Populating Endpoints...",
                "Cancel",
                1,
                len(selected_active_endpoint_names),
                None,
            )
            progress_dialog.setWindowTitle("Populating Endpoints Without Dependencies")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Set up a progress bar inside the dialog
            progress_bar = QProgressBar(progress_dialog)
            progress_dialog.setBar(progress_bar)

            # Run the API requests in a loop
            for i, selected_active_endpoint_name in enumerate(
                selected_active_endpoint_names, start=1
            ):
                selected_active_endpoint_name_details = (
                    self.config_manager.get_endpoint_details_by_name(
                        selected_active_endpoint_name
                    )
                )
                if (
                    "end_point_dependencies"
                    not in selected_active_endpoint_name_details
                ):
                    if "mongodb_collection" in selected_active_endpoint_name_details:
                        end_point = selected_active_endpoint_name_details["end_point"]

                        # Update progress bar and status
                        # progress_dialog.setValue(i)
                        progress_percentage = int(
                            (i / number_of_selected_endpoints) * 100
                        )
                        progress_dialog.setValue(progress_percentage)
                        # progress_dialog.setLabelText(f"Working on endpoint {i} of {number_of_selected_endpoints}")
                        progress_dialog.setLabelText(
                            f"Working on endpoint {i} of {number_of_selected_endpoints}\nEndpoint: {selected_active_endpoint_name:<50}"
                        )

                        try:
                            paginator = ZendeskApiPaginator(
                                zendesk_subdomain,
                                zendesk_api_user_email_address,
                                zendesk_api_key,
                                end_point,
                            )
                            data = paginator.fetch_all_data()
                            if data:
                                self.instance_operations = (
                                    ZendeskInstanceDatabaseOperationsMongoDB(
                                        zendesk_subdomain,
                                        selected_active_endpoint_name_details[
                                            "mongodb_collection"
                                        ],
                                    )
                                )
                                try:
                                    self.instance_operations.insert_collection_data(
                                        data
                                    )
                                    populated_endpoints += 1
                                except Exception as e:
                                    error_message = str(e)
                                    logging.error(
                                        [
                                            f"error inserting collection data: {error_message}"
                                        ]
                                    )
                                finally:
                                    # Close the connection after all operations are done
                                    self.instance_operations.close_connection()
                            else:
                                empty_endpoints.append(selected_active_endpoint_name)
                        except Exception as e:
                            error_message = str(e)
                            error_dict = {
                                "name": selected_active_endpoint_name,
                                "error": error_message,
                            }
                            endpoints_with_errors.append(error_dict)
                            logging.error([f"error: {error_message}"])

                        # Check if the user pressed "Cancel"
                        if progress_dialog.wasCanceled():
                            break

            # Close the progress dialog when the loop is complete
            progress_dialog.close()

            ##################################################################################################
            # THE BELOW CODE IS FOR POPULATING DEPENDENCIES
            ##################################################################################################
            """            
            self.selected_instance = instance_selection_dialog.selected_instance
            zendesk_subdomain, zendesk_api_user_email_address, zendesk_api_key = instance_selection_dialog.selected_instance
            # Create ZendeskInstanceDatabaseOperations for the selected instance
            self.filename()
            print(f"INSTANCE: {self.selected_instance}") # THIE LINE WILL CONTAIN SENSITIVE INFORMATION
            print(f"SUBDOMAIN: {zendesk_subdomain}")
            #self.instance_operations = ZendeskInstanceDatabaseOperationsMongoDB(zendesk_subdomain)

            endpoint_dialog = APIConfigEndpointSelectionDialog(zendesk_subdomain)
            """

            # self.filename()
            # Retrieve the selected endpoints
            selected_active_endpoint_names = (
                endpoint_dialog.get_selected_active_endpoints_with_dependency_names_selection()
            )
            logging.info(
                f"Dependency Selected endpoints:\n{selected_active_endpoint_names}"
            )

            if len(selected_active_endpoint_names) == 1:
                number_of_selected_endpoints = len(selected_active_endpoint_names)

            if len(selected_active_endpoint_names) > 1:
                number_of_selected_endpoints = len(selected_active_endpoint_names) + 1

            empty_endpoints = []
            endpoints_with_errors = []
            populated_endpoints = 0
            # Set up the progress dialog
            progress_dialog = QProgressDialog(
                "Populating Dependency Endpoints...",
                "Cancel",
                1,
                len(selected_active_endpoint_names),
                None,
            )
            progress_dialog.setWindowTitle("Populating Endpoints With Dependencies")
            progress_dialog.setWindowModality(Qt.WindowModal)

            # Set up a progress bar inside the dialog
            progress_bar = QProgressBar(progress_dialog)
            progress_dialog.setBar(progress_bar)

            # Run the API requests in a loop
            for current_endpoint_count, selected_active_endpoint_name in enumerate(
                selected_active_endpoint_names, start=1
            ):
                # for selected_active_endpoint_name in selected_active_endpoint_names:
                selected_active_endpoint_name_details = (
                    self.config_manager.get_endpoint_details_by_name(
                        selected_active_endpoint_name
                    )
                )
                if "end_point_dependencies" in selected_active_endpoint_name_details:
                    if "mongodb_collection" in selected_active_endpoint_name_details:
                        end_point = selected_active_endpoint_name_details["end_point"]
                        # self.filename()
                        logging.info(f"DEPENDENCY ENDPOINT: {end_point}")
                        endpoint_dependency_lookup_collection = (
                            selected_active_endpoint_name_details[
                                "end_point_dependencies"
                            ]["mongodb_dependency_collection"]
                        )
                        endpoint_dependency_loopup_key = (
                            selected_active_endpoint_name_details[
                                "end_point_dependencies"
                            ]["mongodb_dependency_collection_key"]
                        )
                        logging.info(
                            f"ENDPOINT DEPENDENCY LOOKUP COLLECTION: {endpoint_dependency_lookup_collection}"
                        )

                        progress_dialog.setLabelText(
                            f"Working on endpoint {current_endpoint_count} of {number_of_selected_endpoints}\nEndpoint: {selected_active_endpoint_name:<50}"
                        )

                        try:
                            self.instance_operations = (
                                ZendeskInstanceDatabaseOperationsMongoDB(
                                    zendesk_subdomain,
                                    endpoint_dependency_lookup_collection,
                                )
                            )
                            # self.filename()
                            # print(f"\nDEPENDENCY ID COLLECTION: {self.instance_operations}\n")
                            # Execute the query to find all documents with the specified key
                            results = self.instance_operations.query_collection(
                                {}, {f"{endpoint_dependency_loopup_key}": 1, "_id": 0}
                            )
                            # print(f"RESULTS:\n{results}")
                            pattern = r"\{.*?\}"
                            if results:
                                endpoint_dependency_mongodb_collection = (
                                    selected_active_endpoint_name_details[
                                        "mongodb_collection"
                                    ]
                                )
                                logging.info("RESULTS OBTAINED!")
                                logging.info(
                                    f"DEPENDENCY MONGODB COLLECTION:  {endpoint_dependency_mongodb_collection}"
                                )
                                self.instance_operations = (
                                    ZendeskInstanceDatabaseOperationsMongoDB(
                                        zendesk_subdomain,
                                        endpoint_dependency_mongodb_collection,
                                    )
                                )
                                # print(f"\nDEPENDENCY COLLECTION: {self.instance_operations}\n")
                                # for result in results:
                                for i, result in enumerate(results, start=1):
                                    progress_percentage = int((i / len(results)) * 100)
                                    progress_dialog.setValue(progress_percentage)

                                    logging.info(f"RESULT:\n{result}")
                                    dependency_endpoint = re.sub(
                                        pattern,
                                        str(next(iter(result.values()), None)),
                                        end_point,
                                    )
                                    logging.info(
                                        f"UPDATED DEPENDENCY ENDPOINT: {dependency_endpoint}"
                                    )
                                    try:
                                        paginator = ZendeskApiPaginator(
                                            zendesk_subdomain,
                                            zendesk_api_user_email_address,
                                            zendesk_api_key,
                                            dependency_endpoint,
                                        )
                                        data = paginator.fetch_all_data()
                                        # logging.debug(f"\n{json.dumps(data, indent=4)}")

                                        try:
                                            self.instance_operations.insert_collection_data(
                                                data
                                            )
                                            populated_endpoints += 1
                                        except Exception as e:
                                            error_message = str(e)
                                            logging.error(
                                                [
                                                    f"error inserting collection data: {error_message}"
                                                ]
                                            )

                                        # Check if the user pressed "Cancel"
                                        if progress_dialog.wasCanceled():
                                            break

                                    except Exception as e:
                                        error_message = str(e)
                                        error_dict = {
                                            "name": selected_active_endpoint_name,
                                            "error": error_message,
                                        }
                                        endpoints_with_errors.append(error_dict)
                                        logging.error([f"error: {error_message}"])

                        except Exception as e:
                            error_message = str(e)
                            error_dict = {
                                "name": selected_active_endpoint_name,
                                "error": error_message,
                            }
                            endpoints_with_errors.append(error_dict)
                            logging.error([f"error: {error_message}"])

                        finally:
                            # Close the connection after all operations are done
                            self.instance_operations.close_connection()

            # Close the progress dialog when the loop is complete
            progress_dialog.close()

            logging.info(
                f"\nNUMBER OF ACTIVE ENDPOINTS: {self.config_manager.get_number_of_active_endpoints()}"
            )
            logging.info(
                f"NUMBER OF ACTIVE MONGODB COLLECTIONS: {self.config_manager.get_number_of_active_mongodb_collections()}"
            )
            logging.info(
                f"NUMBER OF SELECTED ENDPOINTS: {number_of_selected_endpoints}"
            )
            logging.info(
                f"NUMBER OF ENDPOINTS WITH DEPENDENCIES: {self.config_manager.get_number_of_active_endpoint_with_dependency_names()}"
            )
            logging.info(
                f"NUMBER OF ENDPOINTS WITH DEPENDENCIES AND MONGODB COLLECTIONS: {self.config_manager.get_number_of_active_endpoint_with_dependency_and_mongodb_collection_names()}"
            )
            logging.info(
                f"NUMBER OF POPULATED MONGODB COLLECTIONS: {populated_endpoints}"
            )

            if len(endpoints_with_errors) > 0:
                logging.error(
                    f"NUMBER OF ENDPOINTS WITH ERRORS: {len(endpoints_with_errors)}"
                )
                logging.error(
                    f"ENDPOINTS WITH ERRORS:\n{json.dumps(endpoints_with_errors, indent=4)}"
                )
            else:
                logging.info(
                    f"NUMBER OF ENDPOINTS WITH ERRORS: {len(endpoints_with_errors)}"
                )
                logging.info(
                    f"ENDPOINTS WITH ERRORS:\n{json.dumps(endpoints_with_errors, indent=4)}"
                )

            if len(empty_endpoints) > 0:
                logging.warning(f"EMPTY ENDPOINTS ({len(empty_endpoints)}):\n")
                logging.warning("\n".join(empty_endpoints))
            else:
                logging.info(f"EMPTY ENDPOINTS ({len(empty_endpoints)}):\n")
                logging.info("\n".join(empty_endpoints))
