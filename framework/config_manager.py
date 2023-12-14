import inspect
import json
import logging
import os

from framework.logging_handler import PythagoraZenLogger

# config_manager.py


class ConfigManager:
    def __init__(self):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.config_file_path = self.determine_config_path()
        self.config_data = self.load_config()

    def determine_config_path(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        script_path = os.path.abspath(__file__)
        return os.path.join(
            os.path.dirname(os.path.dirname(script_path)),
            "config_data/api_endpoints",
            "api_endpoint_config.json",
        )

    def load_config(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        try:
            with open(self.config_file_path, "r") as config_file:
                return json.load(config_file)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            return {}
        except Exception as e:
            logging.error(f"Error reading JSON file: {e}")
            return {}

    def get_active_endpoints(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoints = []
        for endpoint_group in self.config_data.values():
            for api_endpoint in endpoint_group:
                endpoint_details = list(api_endpoint.values())[0]
                if endpoint_details.get("pythagorazen_status", "") == "active":
                    active_endpoints.append(endpoint_details)
        return active_endpoints

    def get_endpoint_details_by_name(self, endpoint_name):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        for endpoint_group in self.config_data.values():
            for api_endpoint in endpoint_group:
                endpoint_details = list(api_endpoint.values())[0]
                if endpoint_details.get("name") == endpoint_name:
                    return endpoint_details
        return None

    def get_active_endpoint_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_names = []
        for endpoint_group in self.config_data.values():
            for api_endpoint in endpoint_group:
                endpoint_details = list(api_endpoint.values())[0]
                if "pythagorazen_status" in endpoint_details:
                    if endpoint_details["pythagorazen_status"] == "active":
                        active_names.append(endpoint_details["name"])
        return active_names

    def get_number_of_active_endpoints(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return len(self.get_active_endpoint_names())

    def get_active_endpoint_mongodb_collection_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoint_mongodb_names = []
        for endpoint_group in self.config_data.values():
            for api_endpoint in endpoint_group:
                endpoint_details = list(api_endpoint.values())[0]
                if (
                    "pythagorazen_status" in endpoint_details
                    and "mongodb_collection" in endpoint_details
                ):
                    if (
                        endpoint_details["pythagorazen_status"] == "active"
                        and endpoint_details["mongodb_collection"]
                    ):
                        active_endpoint_mongodb_names.append(
                            endpoint_details["mongodb_collection"]
                        )
        return active_endpoint_mongodb_names

    def get_number_of_active_mongodb_collections(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return len(self.get_active_endpoint_mongodb_collection_names())

    def get_active_endpoint_with_dependency_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoint_with_dependency_names = []
        for endpoint_group in self.config_data.values():
            for api_endpoint in endpoint_group:
                endpoint_details = list(api_endpoint.values())[0]
                if (
                    "pythagorazen_status" in endpoint_details
                    and "end_point_dependencies" in endpoint_details
                ):
                    if (
                        endpoint_details["pythagorazen_status"] == "active"
                        and endpoint_details["end_point_dependencies"]
                    ):
                        active_endpoint_with_dependency_names.append(
                            endpoint_details["name"]
                        )
        return active_endpoint_with_dependency_names

    def get_number_of_active_endpoint_with_dependency_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return len(self.get_active_endpoint_with_dependency_names())

    def get_active_endpoint_with_dependency_and_mongodb_collection_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoint_with_dependency_and_mongodb_collection_names = []
        for endpoint_group in self.config_data.values():
            for api_endpoint in endpoint_group:
                endpoint_details = list(api_endpoint.values())[0]
                if (
                    "pythagorazen_status" in endpoint_details
                    and "end_point_dependencies" in endpoint_details
                    and "mongodb_collection" in endpoint_details
                ):
                    if (
                        endpoint_details["pythagorazen_status"] == "active"
                        and endpoint_details["end_point_dependencies"]
                        and endpoint_details["mongodb_collection"]
                    ):
                        active_endpoint_with_dependency_and_mongodb_collection_names.append(
                            endpoint_details["mongodb_collection"]
                        )
        return active_endpoint_with_dependency_and_mongodb_collection_names

    def get_number_of_active_endpoint_with_dependency_and_mongodb_collection_names(
        self,
    ):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return len(
            self.get_active_endpoint_with_dependency_and_mongodb_collection_names()
        )

    def get_active_endpoints_without_dependency_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        active_endpoints_without_dependency_names = [
            item
            for item in self.get_active_endpoint_names()
            if item not in self.get_active_endpoint_with_dependency_names()
        ]
        return active_endpoints_without_dependency_names

    def get_number_of_active_endpoints_without_dependency_names(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return len(self.get_active_endpoints_without_dependency_names())
